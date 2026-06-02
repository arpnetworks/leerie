"""Tests for `render_tail_wrapper` in scripts/remote/lib.sh.

The helper emits a POSIX-sh wrapper script that runs inside a Fly
Machine. Both leerie's initial-launch tail and scripts/remote/attach.sh
--tail use it. These tests exercise the wrapper in a tmp_path "fake
machine" filesystem (no actual Fly Machine; the script's only
dependencies are local files and `tail -F`).

Coverage:
  - Bootstrap-id input → waits for rename → reads handover → re-tails final
  - Final-id input → tails directly
  - Pid disappearance → wrapper exits with finalize hint
  - AUTO_FINALIZE_TOKEN env var → token line emitted with final id
"""
from __future__ import annotations

import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LIB_SH = REPO_ROOT / "scripts" / "remote" / "lib.sh"


def _render(tmp_path: Path) -> str:
    """Run `render_tail_wrapper` and return its stdout (the wrapper script)."""
    r = subprocess.run(
        ["bash", "-c", f". {LIB_SH}; render_tail_wrapper"],
        capture_output=True, text=True, check=True,
    )
    return r.stdout


def _setup_fake_work(tmp_path: Path, run_id: str, *, pid: int | None = None,
                     log_lines: list[str] | None = None) -> Path:
    """Create /work-like directory structure under tmp_path/work/. Returns
    the run dir."""
    work = tmp_path / "work"
    run_dir = work / ".leerie" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    log = run_dir / "orchestrator.log"
    log.write_text("\n".join(log_lines or []) + "\n")
    if pid is not None:
        (run_dir / "orchestrator.pid").write_text(f"{pid}\n")
    return run_dir


def _run_wrapper(tmp_path: Path, script: str, run_id: str,
                 env_extra: dict | None = None,
                 timeout: float = 5.0) -> subprocess.CompletedProcess:
    """Run the wrapper with run_id as $1. The wrapper hard-codes
    /work/... so we use a `sed` rewrite to point at $tmp_path/work for
    the test."""
    rewritten = script.replace("/work/", f"{tmp_path}/work/")
    env = {"PATH": "/usr/bin:/bin"}
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", "-c", rewritten + "\n", "_", run_id],
        env=env,
        capture_output=True, text=True, timeout=timeout, check=False,
    )


# --- emission contract ----------------------------------------------------

def test_render_emits_non_empty_script(tmp_path):
    out = _render(tmp_path)
    assert "tail -F" in out
    assert "orchestrator.log" in out
    assert "orchestrator.pid" in out
    assert "_bootstrap-" in out  # bootstrap-id branch present
    assert "AUTO_FINALIZE_TOKEN" in out


# --- final-id direct tail -------------------------------------------------

def test_final_id_tails_directly_until_pid_dies(tmp_path):
    """Given a final-style run-id and a pid that doesn't exist, the
    wrapper exits promptly with the finalize hint."""
    _setup_fake_work(tmp_path, "feat-x-aaaaaa", pid=999999,
                     log_lines=["[leerie] hello"])
    script = _render(tmp_path)
    r = _run_wrapper(tmp_path, script, "feat-x-aaaaaa")
    assert r.returncode == 0, r.stderr
    assert "orchestrator exited" in r.stderr


# --- bootstrap id branch (without rename — wrapper should fail with the
# documented handover-missing error) ---------------------------------------

def test_bootstrap_id_without_handover_errors(tmp_path):
    """Bootstrap id input with no handover file when the dir disappears
    → exit 2 with the documented error."""
    _setup_fake_work(tmp_path, "_bootstrap-abc123", pid=None,
                     log_lines=["[leerie] bootstrap"])
    script = _render(tmp_path)

    # Spawn the wrapper and immediately rm the bootstrap dir to simulate
    # the rename without writing a handover file.
    rewritten = script.replace("/work/", f"{tmp_path}/work/")
    proc = subprocess.Popen(
        ["bash", "-c", rewritten + "\n", "_", "_bootstrap-abc123"],
        env={"PATH": "/usr/bin:/bin"},
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True,
    )
    # Let the wrapper enter its tail loop briefly, then yank the dir.
    time.sleep(0.5)
    bootstrap_dir = tmp_path / "work" / ".leerie" / "runs" / "_bootstrap-abc123"
    log_path = bootstrap_dir / "orchestrator.log"
    log_path.unlink()
    bootstrap_dir.rmdir()
    try:
        stdout, stderr = proc.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        raise AssertionError(f"wrapper hung; stderr so far: {stderr!r}")
    assert proc.returncode == 2, stderr
    assert "no handover at" in stderr or "bootstrap dir gone but no handover" in stderr


# --- bootstrap → handover → final ----------------------------------------

def test_bootstrap_id_resolves_via_handover(tmp_path):
    """Bootstrap id → wrapper waits for dir to disappear → reads
    handover file → re-tails final log → exits when pid disappears."""
    _setup_fake_work(tmp_path, "_bootstrap-def456", pid=None,
                     log_lines=["[leerie] bootstrap"])
    final_dir = _setup_fake_work(tmp_path, "feat-y-bbbbbb", pid=999999,
                                 log_lines=["[leerie] promoted"])
    # Pre-write the handover file (this is what the orchestrator would
    # write at end of phase_classify).
    handover = tmp_path / "work" / ".leerie" / "launcher-_bootstrap-def456.runid"
    handover.parent.mkdir(parents=True, exist_ok=True)
    handover.write_text("feat-y-bbbbbb\n")

    script = _render(tmp_path)
    rewritten = script.replace("/work/", f"{tmp_path}/work/")
    proc = subprocess.Popen(
        ["bash", "-c", rewritten + "\n", "_", "_bootstrap-def456"],
        env={"PATH": "/usr/bin:/bin"},
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True,
    )
    time.sleep(0.5)
    # Yank the bootstrap dir to trigger the rename branch.
    bootstrap_dir = tmp_path / "work" / ".leerie" / "runs" / "_bootstrap-def456"
    (bootstrap_dir / "orchestrator.log").unlink()
    bootstrap_dir.rmdir()
    try:
        stdout, stderr = proc.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        raise AssertionError(f"wrapper hung; stderr so far: {stderr!r}")
    assert proc.returncode == 0, stderr
    assert "promoted to feat-y-bbbbbb" in stderr
    assert "orchestrator exited" in stderr


# --- auto-finalize token --------------------------------------------------

def test_auto_finalize_token_emitted_when_set(tmp_path):
    """AUTO_FINALIZE_TOKEN env var → wrapper prints "${TOKEN}${final_id}"
    on its last stderr line for the host caller to grep."""
    _setup_fake_work(tmp_path, "feat-z-cccccc", pid=999999,
                     log_lines=["[leerie] go"])
    script = _render(tmp_path)
    r = _run_wrapper(tmp_path, script, "feat-z-cccccc",
                     env_extra={"AUTO_FINALIZE_TOKEN": "<<TOK>>"})
    assert r.returncode == 0, r.stderr
    assert "<<TOK>>feat-z-cccccc" in r.stderr


def test_auto_finalize_token_absent_when_unset(tmp_path):
    """No token env var → no token line in stderr."""
    _setup_fake_work(tmp_path, "feat-q-dddddd", pid=999999,
                     log_lines=["[leerie] go"])
    script = _render(tmp_path)
    r = _run_wrapper(tmp_path, script, "feat-q-dddddd")
    assert r.returncode == 0, r.stderr
    assert "<<" not in r.stderr.split("\n")[-2]  # no token sentinel
