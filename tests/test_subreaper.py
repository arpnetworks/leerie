"""Tests for the orchestrator zombie-reaper (DESIGN §6 *Zombie reaping*).

The leerie container's PID 1 is `runuser`/the entrypoint (or an idle
`sleep infinity` on Fly), NOT a real init — it never `wait()`s arbitrary
orphans. Worker tool subtrees routinely orphan short-lived subprocesses
(git, ssh-agent, their children); without a subreaper those reparent to
PID 1 and rot as `<defunct>` zombies, each counting against the worker
cgroup's `pids.max` until it fills and every `fork()` EAGAINs. This was
captured live in production (453 defunct `git`, all ppid==1).

The fix: the orchestrator calls `_become_subreaper()` early in `main()`
(so orphaned descendants reparent to it) and runs `_zombie_reaper()` to
`waitpid` them. These tests verify both halves.
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import sys

import pytest

linux_only = pytest.mark.skipif(
    not sys.platform.startswith("linux"),
    reason="prctl(PR_SET_CHILD_SUBREAPER) and PID-reparenting are Linux-only.",
)


def test_become_subreaper_noop_off_linux_does_not_raise(leerie):
    """On any platform, `_become_subreaper()` must return a bool and never
    raise — on non-Linux it is a documented no-op (returns False)."""
    result = leerie._become_subreaper()
    assert isinstance(result, bool)
    if not sys.platform.startswith("linux"):
        assert result is False


@linux_only
def test_become_subreaper_sets_the_flag(leerie):
    """On Linux, `_become_subreaper()` installs the child-subreaper flag,
    verifiable by reading it back via prctl(PR_GET_CHILD_SUBREAPER)."""
    import ctypes

    assert leerie._become_subreaper() is True
    libc = ctypes.CDLL(None, use_errno=True)
    out = ctypes.c_int(0)
    rc = libc.prctl(leerie._PR_GET_CHILD_SUBREAPER, ctypes.byref(out), 0, 0, 0)
    assert rc == 0
    assert out.value == 1, "PR_GET_CHILD_SUBREAPER should read back 1 (set)"


@linux_only
def test_zombie_reaper_reaps_an_orphaned_child(leerie):
    """A child that exits without being wait()ed becomes a <defunct> zombie.
    One tick of `_zombie_reaper` must reap it so it no longer occupies a task
    slot. This is the exact mechanism that was filling the cgroup pids.max.

    We fork a direct child (so this test process is its parent and thus the
    one obligated to wait) that exits immediately, confirm it is a zombie,
    then run the reaper and confirm it is gone.
    """
    pid = os.fork()
    if pid == 0:  # child
        os._exit(0)

    # Give the child a moment to exit and become a zombie.
    def _is_zombie(p: int) -> bool:
        try:
            with open(f"/proc/{p}/stat") as f:
                # field 3 (0-indexed 2) is state; 'Z' = zombie
                return f.read().split(")")[-1].split()[0] == "Z"
        except OSError:
            return False

    for _ in range(50):
        if _is_zombie(pid):
            break
        import time
        time.sleep(0.02)
    assert _is_zombie(pid), "child should be a zombie before reaping"

    async def _one_tick():
        task = asyncio.create_task(leerie._zombie_reaper(interval_sec=0.05))
        await asyncio.sleep(0.2)  # enough for at least one waitpid drain
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(_one_tick())

    # After reaping, the pid must no longer exist at all (zombie cleared).
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)


def test_reaper_is_wired_into_orchestrate(leerie):
    """The reaper only helps if `orchestrate()` actually spawns AND cancels it
    (mirroring `_memory_sampler`'s lifecycle). Source-pin the wiring so a
    refactor can't silently drop it — the fix is inert without this."""
    import inspect

    src = inspect.getsource(leerie.orchestrate)
    assert "_zombie_reaper()" in src, (
        "orchestrate() must spawn _zombie_reaper() as a background task")
    assert "reaper_task = asyncio.create_task" in src, (
        "reaper task must be created like sampler_task")
    assert "reaper_task.cancel()" in src, (
        "reaper task must be cancelled in orchestrate()'s finally")


def test_main_installs_subreaper(leerie):
    """`main()` must call `_become_subreaper()` before spawning workers, or
    orphans never reparent to us and the reaper has nothing to reap."""
    import inspect

    src = inspect.getsource(leerie.main)
    assert "_become_subreaper()" in src, (
        "main() must call _become_subreaper() early, before orchestrate()")


@linux_only
def test_zombie_reaper_does_not_steal_asyncio_worker_status(leerie):
    """The reaper must NOT `waitpid` a live asyncio-managed subprocess — doing
    so steals the exit status out from under asyncio's child watcher, which
    then reports returncode 255 instead of the true code. This is the exact
    race the targeted-reap fix (never `waitpid(-1)`) prevents.

    Spawn a real `create_subprocess_exec` child that exits 7, run the reaper
    concurrently across the child's exit, and assert `proc.wait()` returns the
    TRUE code (7), not 255. Without the fix (blanket `waitpid(-1)`) this would
    flake to 255 whenever the reaper won the race."""
    async def _run() -> int:
        proc = await asyncio.create_subprocess_exec(
            "sh", "-c", "sleep 0.3; exit 7",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        # The reaper registers no exclusion here (this isn't _invoke), so this
        # test relies on the state==Z + ppid==getpid scan alone: a LIVE child
        # is not state Z, and once it exits asyncio reaps it before it lingers.
        # Run the reaper hot (20ms) across the whole lifetime to maximize the
        # race window the old waitpid(-1) would have lost.
        reaper = asyncio.create_task(leerie._zombie_reaper(interval_sec=0.02))
        rc = await proc.wait()
        reaper.cancel()
        try:
            await reaper
        except asyncio.CancelledError:
            pass
        return rc

    rc = asyncio.run(_run())
    assert rc == 7, (
        f"worker exit code was stolen by the reaper (got {rc}, expected 7) — "
        "the reaper must never waitpid an asyncio-managed child")


@linux_only
def test_zombie_reaper_excludes_registered_worker_pids(leerie, monkeypatch):
    """Belt-and-suspenders: even if a registered worker PID were briefly a
    zombie, `_orphan_zombie_children` must exclude anything in
    `_ASYNCIO_MANAGED_PIDS`. Fork a zombie, register its pid, and assert the
    scan omits it; then unregister and assert it appears."""
    pid = os.fork()
    if pid == 0:
        os._exit(0)
    try:
        import time
        for _ in range(50):
            try:
                with open(f"/proc/{pid}/stat") as f:
                    if f.read().split(")")[-1].split()[0] == "Z":
                        break
            except OSError:
                pass
            time.sleep(0.02)
        leerie._ASYNCIO_MANAGED_PIDS.add(pid)
        assert pid not in leerie._orphan_zombie_children(), (
            "registered worker pid must be excluded from the reap set")
        leerie._ASYNCIO_MANAGED_PIDS.discard(pid)
        assert pid in leerie._orphan_zombie_children(), (
            "unregistered zombie child should be reapable")
    finally:
        leerie._ASYNCIO_MANAGED_PIDS.discard(pid)
        try:
            os.waitpid(pid, 0)
        except (ChildProcessError, OSError):
            pass


def test_reparented_orphans_accepts_orchestrator_ppid(leerie, monkeypatch):
    """After `_become_subreaper`, orphans reparent to the orchestrator, not
    PID 1. `_reparented_orphans` must accept `ppid == os.getpid()` in addition
    to `ppid == 1`, or the mid-run reaper misses every reparented orphan."""
    import os as _os
    min_age = leerie._PID_REAP_MIN_AGE_SEC
    me = _os.getpid()
    fake_ps = (
        "  PID  PPID ELAPSED\n"
        f"  300 {me} {min_age + 10}\n"   # reparented to orchestrator — accept
        f"  301     1 {min_age + 10}\n"  # reparented to init — accept
        f"  302     2 {min_age + 10}\n"  # attached elsewhere — reject
    )

    def fake_run(cmd, **kwargs):
        class R:
            stdout = fake_ps
        return R()

    monkeypatch.setattr(leerie.subprocess, "run", fake_run)
    result = leerie._reparented_orphans({300, 301, 302})
    assert set(result) == {300, 301}, f"got {result}"


@linux_only
def test_zombie_reaper_survives_no_children(leerie):
    """With no children to wait on, the reaper must not crash — it swallows
    ChildProcessError and keeps looping."""
    async def _run():
        task = asyncio.create_task(leerie._zombie_reaper(interval_sec=0.05))
        await asyncio.sleep(0.15)
        assert not task.done(), "reaper must keep running when there are no children"
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(_run())
