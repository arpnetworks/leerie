#!/usr/bin/env python3
"""Root-privileged cgroup broker for leerie worker containment.

Why this exists (DESIGN §6 *Memory containment*, and the reproduced
cgroup-v2 delegation constraint): the orchestrator runs as the non-root
`leerie` user, but cgroup enforcement cannot be done from non-root code.

Two kernel facts make non-root self-enforcement impossible, both
reproduced live (see docs/DESIGN.md §6):
  1. Migrating a task into a cgroup requires write on `cgroup.procs` of
     the destination, the source, AND their common ancestor. Workers are
     born in the root-owned container scope (`/system.slice/nerdctl-*.scope`
     locally, the machine scope on Fly); moving them into `leerie.slice`
     crosses the root cgroup, which `leerie` does not own → EACCES/EIO.
  2. Even inside a properly *delegated* subtree the kernel keeps the
     controller limit files (`pids.max`, `memory.max`) root-owned — a
     delegatee may organize processes but not set controller limits.

So the operations that matter (create a worker cgroup, set its limits,
enroll the worker PID, tear it down) must run as root. This broker is
launched by `scripts/container-entry.sh` at PID 1 (root) *before* the
privilege drop to `leerie`, and the non-root orchestrator drives it over
a Unix socket. It is the single root-privileged surface in the worker
path, so it is deliberately tiny and validates every input.

Protocol (newline-terminated, one request per connection):
  ping                          -> OK
  probe                         -> OK <hierarchy>   (round-trips create+enroll+destroy of a throwaway cgroup)
  create <sid> <mem_bytes> <pids_max>  -> OK | ERR <msg>
  enroll <sid> <pid>            -> OK | ERR <msg>
  destroy <sid>                 -> OK | ERR <msg>

`<sid>` is validated against `^[A-Za-z0-9._-]+$` and only ever composed
into `leerie-w-<sid>` under the fixed slice — no path traversal. `<pid>`,
`<mem_bytes>`, `<pids_max>` must be non-negative integers.

cgroup v1 vs v2 (both reproduced): on v2 (Colima) we write the unified
`leerie.slice/leerie-w-<sid>/{pids,memory}.max`. On v1/hybrid (Fly
Firecracker VMs) the unified mount has no controllers, so we write the
split hierarchies (`/sys/fs/cgroup/pids/leerie.slice/...`,
`/sys/fs/cgroup/memory/leerie.slice/...`). The hierarchy is detected once
at startup and reported by `probe` so the orchestrator's telemetry records
which path was taken.
"""

import contextlib
import os
import re
import signal
import socket
import sys

SOCK_PATH = "/run/leerie-cgroup.sock"
SLICE = "leerie.slice"
V2_ROOT = "/sys/fs/cgroup"
_SID_RE = re.compile(r"^[A-Za-z0-9._-]+$")

# Hierarchy is one of: "v2", "v1", "none". Decided at startup by _detect().
_HIER = "none"


def _log(msg: str) -> None:
    # PID 1's stdout is the container log; prefix so these lines are greppable.
    print(f"[cgroup-broker] {msg}", file=sys.stderr, flush=True)


def _detect() -> str:
    """Decide which cgroup hierarchy is usable. v2 if the unified mount
    exposes controllers we can enable; v1 if the split controller mounts
    exist; else none."""
    try:
        if os.path.isfile(f"{V2_ROOT}/cgroup.controllers"):
            # Unified. Ensure pids+memory are delegatable into children.
            _write(f"{V2_ROOT}/{SLICE}/cgroup.subtree_control",
                   "+pids +memory", swallow=True, mkparent=True)
            ctrls = _read(f"{V2_ROOT}/{SLICE}/cgroup.controllers")
            if "pids" in ctrls and "memory" in ctrls:
                return "v2"
        # v1/hybrid: split controllers each at their own mount.
        if os.path.isdir(f"{V2_ROOT}/pids") and os.path.isdir(f"{V2_ROOT}/memory"):
            return "v1"
    except OSError as e:
        _log(f"detect error: {e}")
    return "none"


def _read(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return ""


def _write(path: str, val: str, swallow: bool = False,
           mkparent: bool = False) -> None:
    if mkparent:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "w") as f:
            f.write(val)
    except OSError:
        if not swallow:
            raise


# --- v2 paths --------------------------------------------------------------

def _v2_dir(sid: str) -> str:
    return f"{V2_ROOT}/{SLICE}/leerie-w-{sid}"


def _v2_create(sid: str, mem: int, pids: int) -> None:
    d = _v2_dir(sid)
    os.makedirs(d, exist_ok=True)
    if pids > 0:
        _write(f"{d}/pids.max", str(pids))
    if mem > 0:
        _write(f"{d}/memory.max", str(mem))
        # Match _cgroup_create's prior behavior: no swap padding to delay OOM.
        _write(f"{d}/memory.swap.max", "0", swallow=True)


def _v2_enroll(sid: str, pid: int) -> None:
    _write(f"{_v2_dir(sid)}/cgroup.procs", str(pid))


def _v2_destroy(sid: str) -> None:
    d = _v2_dir(sid)
    _write(f"{d}/cgroup.kill", "1", swallow=True)
    try:
        os.rmdir(d)
    except OSError:
        pass


# --- v1 paths (split controllers) -----------------------------------------

def _v1_dirs(sid: str) -> tuple[str, str]:
    return (f"{V2_ROOT}/pids/{SLICE}/leerie-w-{sid}",
            f"{V2_ROOT}/memory/{SLICE}/leerie-w-{sid}")


def _v1_create(sid: str, mem: int, pids: int) -> None:
    pdir, mdir = _v1_dirs(sid)
    os.makedirs(pdir, exist_ok=True)
    os.makedirs(mdir, exist_ok=True)
    if pids > 0:
        _write(f"{pdir}/pids.max", str(pids))
    if mem > 0:
        _write(f"{mdir}/memory.limit_in_bytes", str(mem))


def _v1_enroll(sid: str, pid: int) -> None:
    pdir, mdir = _v1_dirs(sid)
    # v1: enroll into every controller hierarchy via its tasks/cgroup.procs.
    _write(f"{pdir}/cgroup.procs", str(pid))
    _write(f"{mdir}/cgroup.procs", str(pid))


def _v1_destroy(sid: str) -> None:
    pdir, mdir = _v1_dirs(sid)
    # v1 has no cgroup.kill; move survivors to the parent then rmdir.
    for d in (pdir, mdir):
        for pid in _read(f"{d}/cgroup.procs").split():
            _write(f"{os.path.dirname(d)}/cgroup.procs", pid, swallow=True)
        try:
            os.rmdir(d)
        except OSError:
            pass


# --- dispatch --------------------------------------------------------------

def _valid_sid(sid: str) -> bool:
    return bool(_SID_RE.match(sid)) and ".." not in sid


def _do(verb: str, args: list[str]) -> str:
    if _HIER == "none":
        return "ERR no usable cgroup hierarchy"
    create = _v2_create if _HIER == "v2" else _v1_create
    enroll = _v2_enroll if _HIER == "v2" else _v1_enroll
    destroy = _v2_destroy if _HIER == "v2" else _v1_destroy

    if verb == "create":
        sid, mem, pids = args[0], int(args[1]), int(args[2])
        if not _valid_sid(sid):
            return "ERR bad sid"
        if mem < 0 or pids < 0:
            return "ERR bad limit"
        create(sid, mem, pids)
        return "OK"
    if verb == "enroll":
        sid, pid = args[0], int(args[1])
        if not _valid_sid(sid) or pid <= 0:
            return "ERR bad sid/pid"
        enroll(sid, pid)
        return "OK"
    if verb == "destroy":
        sid = args[0]
        if not _valid_sid(sid):
            return "ERR bad sid"
        destroy(sid)
        return "OK"
    return f"ERR unknown verb {verb}"


def _handle(line: str) -> str:
    parts = line.strip().split()
    if not parts:
        return "ERR empty"
    verb, args = parts[0], parts[1:]
    if verb == "ping":
        return "OK"
    if verb == "probe":
        # End-to-end round-trip on a throwaway sid: the true test of the
        # path workers use (create + enroll a real pid + destroy).
        sid = "PROBE"
        try:
            child = os.fork()
            if child == 0:  # noqa: SIM115 — child just idles until killed
                signal.pause()
                os._exit(0)
            _do("create", [sid, "0", "64"])
            r = _do("enroll", [sid, str(child)])
            # Reap the child BEFORE destroy: on v2 `_do("destroy")` writes
            # cgroup.kill, which SIGKILLs the enrolled child — if PID 1 then
            # reaps the zombie before our os.kill/waitpid, those would raise
            # ProcessLookupError/ChildProcessError and falsely fail an
            # otherwise-healthy probe. Kill+reap here, tolerate already-gone.
            with contextlib.suppress(ProcessLookupError):
                os.kill(child, signal.SIGKILL)
            with contextlib.suppress(ChildProcessError):
                os.waitpid(child, 0)
            _do("destroy", [sid])
            return f"OK {_HIER}" if r == "OK" else f"ERR probe enroll: {r}"
        except OSError as e:
            return f"ERR probe: {e}"
    try:
        return _do(verb, args)
    except (OSError, ValueError, IndexError) as e:
        return f"ERR {type(e).__name__}: {e}"


def main() -> int:
    global _HIER
    _HIER = _detect()
    _log(f"hierarchy={_HIER}")

    if os.path.exists(SOCK_PATH):
        os.unlink(SOCK_PATH)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(SOCK_PATH)
    # World-connectable so the post-privilege-drop leerie orchestrator can
    # reach it on every runtime — including the rootless path where the
    # orchestrator runs in a nested user namespace (`unshare --user`), so
    # its uid as seen here is not leerie's image uid and a chown+0o660
    # lockdown could lock the real client out. Every request is validated
    # (fixed verb set; `_valid_sid` regex; integer pid/limits), so a
    # crafted request cannot escape `leerie-w-<sid>` under the slice.
    # Residual: `enroll` trusts the caller-supplied pid without verifying
    # it belongs to leerie, so a hostile in-container process could enroll
    # an arbitrary pid into a capped cgroup (a local DoS). Accepted: the
    # container runs only leerie's own workers — there is no adversarial
    # process model inside it — and a peer-uid check (SO_PEERCRED) is
    # unreliable across the rootless userns boundary.
    os.chmod(SOCK_PATH, 0o666)
    srv.listen(16)
    _log(f"listening on {SOCK_PATH}")

    # Reap nothing else; ignore SIGCHLD from the probe fork via waitpid above.
    while True:
        try:
            conn, _ = srv.accept()
        except OSError:
            continue
        try:
            # Bound the per-connection recv so a client that connects but
            # never sends can't wedge this single-threaded accept loop and
            # starve every other worker's cgroup op. The orchestrator's
            # `_cgroup_request` always sends immediately, so a well-behaved
            # run never hits this; it guards against a buggy in-container
            # process holding a connection open.
            conn.settimeout(5.0)
            data = conn.recv(4096).decode(errors="replace")
            resp = _handle(data)
            conn.sendall((resp + "\n").encode())
        except OSError as e:
            _log(f"conn error: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    sys.exit(main())
