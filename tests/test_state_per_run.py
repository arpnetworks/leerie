"""Tests for the per-run State refactor — `State.__init__` taking
(leerie_root, run_id).

Covers:
- State paths are correctly anchored under runs/<run-id>/.
- Two State instances with different run_ids have disjoint storage.
- save() writes to the right path; load() reads from the right path.
- Run-directory flock prevents dual-orchestrator races.
"""
from __future__ import annotations

import pytest


def test_state_path_is_per_run(leerie, tmp_path):
    """state.json lives at leerie_root/runs/<run-id>/state.json."""
    st = leerie.State(tmp_path, "feat-foo-abc123")
    assert st.path == tmp_path / "runs" / "feat-foo-abc123" / "state.json"
    assert st.run_dir == tmp_path / "runs" / "feat-foo-abc123"
    assert st.run_id == "feat-foo-abc123"
    assert st.leerie_root == tmp_path


def test_state_save_writes_to_per_run_dir(leerie, tmp_path):
    """save() writes the JSON under runs/<run-id>/."""
    (tmp_path / "runs" / "feat-foo-abc123").mkdir(parents=True)
    st = leerie.State(tmp_path, "feat-foo-abc123")
    st.data = {"task": "x"}
    st.save()
    saved = tmp_path / "runs" / "feat-foo-abc123" / "state.json"
    assert saved.exists()


def test_state_load_reads_from_per_run_dir(leerie, tmp_path):
    import json
    rd = tmp_path / "runs" / "feat-foo-abc123"
    rd.mkdir(parents=True)
    (rd / "state.json").write_text(json.dumps({"task": "loaded"}))
    st = leerie.State(tmp_path, "feat-foo-abc123")
    assert st.load() is True
    assert st.data["task"] == "loaded"


def test_state_load_returns_false_when_absent(leerie, tmp_path):
    """Per-run dir without a state.json (fresh bootstrap) loads to False
    rather than raising."""
    (tmp_path / "runs" / "feat-foo-abc123").mkdir(parents=True)
    st = leerie.State(tmp_path, "feat-foo-abc123")
    assert st.load() is False


def test_two_states_disjoint_paths(leerie, tmp_path):
    """Two State instances with different run_ids have completely
    disjoint storage — the central property the per-run refactor must
    guarantee."""
    sa = leerie.State(tmp_path, "feat-a-aaaaaa")
    sb = leerie.State(tmp_path, "fix-b-bbbbbb")
    assert sa.path != sb.path
    assert sa.run_dir != sb.run_dir
    # The directories must not share any path component below
    # leerie_root — they're siblings.
    assert sa.run_dir.parent == sb.run_dir.parent == tmp_path / "runs"


def test_two_states_save_independently(leerie, tmp_path):
    """Save one State; the other's path stays empty."""
    (tmp_path / "runs" / "feat-a-aaaaaa").mkdir(parents=True)
    (tmp_path / "runs" / "fix-b-bbbbbb").mkdir(parents=True)
    sa = leerie.State(tmp_path, "feat-a-aaaaaa")
    sb = leerie.State(tmp_path, "fix-b-bbbbbb")
    sa.data = {"task": "a"}
    sa.save()
    assert sa.path.exists()
    assert not sb.path.exists()


# --- repo_root ---------------------------------------------------------------

def test_state_repo_root_defaults_to_leerie_root_parent(leerie, tmp_path):
    """When no repo_root is passed, st.repo_root == st.leerie_root.parent."""
    st = leerie.State(tmp_path / ".leerie", "feat-foo-abc123")
    assert st.repo_root == tmp_path


def test_state_repo_root_explicit_override(leerie, tmp_path):
    """An explicit repo_root is stored independently of leerie_root."""
    leerie_root = tmp_path / "dot-leerie"
    repo_root = tmp_path / "my-repo"
    st = leerie.State(leerie_root, "feat-foo-abc123", repo_root=repo_root)
    assert st.repo_root == repo_root
    assert st.leerie_root == leerie_root
    assert st.repo_root != st.leerie_root.parent


def test_state_repo_root_explicit_does_not_affect_run_dir(leerie, tmp_path):
    """run_dir derivation is always under leerie_root, not repo_root."""
    leerie_root = tmp_path / "dot-leerie"
    repo_root = tmp_path / "my-repo"
    st = leerie.State(leerie_root, "feat-foo-abc123", repo_root=repo_root)
    assert st.run_dir == leerie_root / "runs" / "feat-foo-abc123"


# --- run-directory flock ------------------------------------------------------
# DESIGN §6 *Single owner per run dir*. State.__init__ acquires an
# exclusive advisory flock on run_dir; a second instance against the
# same dir raises StateLockedError. This is the load-bearing defense
# against the dual-orchestrator race documented in that DESIGN
# subsection.


def test_state_lock_blocks_second_instance(leerie, tmp_path):
    """Two State instances on the same run dir: second raises
    StateLockedError. First still holds the lock and can keep
    working (no half-released state)."""
    sa = leerie.State(tmp_path, "feat-foo-abc123")
    with pytest.raises(leerie.StateLockedError) as excinfo:
        leerie.State(tmp_path, "feat-foo-abc123")
    assert excinfo.value.run_dir == sa.run_dir
    # sa must still be functional — the failed acquisition should not
    # have stolen or corrupted its lock.
    sa.data = {"task": "still works"}
    sa.save()
    assert (tmp_path / "runs" / "feat-foo-abc123" / "state.json").exists()


def test_state_lock_released_on_explicit_release(leerie, tmp_path):
    """release_lock() lets a fresh State acquire the same dir."""
    sa = leerie.State(tmp_path, "feat-foo-abc123")
    sa.release_lock()
    # Now a second construction must succeed.
    sb = leerie.State(tmp_path, "feat-foo-abc123")
    assert sb.run_dir == sa.run_dir
    sb.data = {"task": "second owner"}
    sb.save()


def test_state_lock_released_on_subprocess_exit(leerie, tmp_path):
    """When the owning process dies, the kernel releases the flock.
    A second invocation can then acquire — no manual cleanup needed.
    Uses a subprocess to simulate process death (in-process release
    is covered by test_state_lock_released_on_explicit_release)."""
    import subprocess
    import sys
    from pathlib import Path
    leerie_py = Path(leerie.__file__)
    # Subprocess A: acquires the lock and exits cleanly (no explicit
    # release — kernel handles it on process exit). The orchestrator
    # is a single-file script, not a package, so we load it via
    # importlib (matching tests/conftest.py).
    prog = (
        "import importlib.util\n"
        "from pathlib import Path\n"
        f"spec = importlib.util.spec_from_file_location('leerie', {str(leerie_py)!r})\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(mod)\n"
        f"mod.State(Path({str(tmp_path)!r}), 'feat-foo-abc123')\n"
    )
    holder = subprocess.run(
        [sys.executable, "-c", prog],
        capture_output=True, text=True,
    )
    assert holder.returncode == 0, (
        f"holder failed: stdout={holder.stdout!r} stderr={holder.stderr!r}")
    # Now the in-process State must be able to acquire.
    sa = leerie.State(tmp_path, "feat-foo-abc123")
    assert sa._lock_fd is not None


def test_state_lock_survives_save(leerie, tmp_path):
    """save()'s atomic tmp.replace(state.json) must not orphan the lock.
    The lock is on run_dir (a stable inode), not on state.json (which
    is replaced on every save). After many saves the second-instance
    block must still hold."""
    import json
    sa = leerie.State(tmp_path, "feat-foo-abc123")
    for i in range(5):
        sa.data = {"iter": i}
        sa.save()
    # Confirm the saves actually wrote, not just returned cleanly —
    # without this, a silently-swallowed save() exception would let
    # the test pass on a broken implementation.
    saved = json.loads(
        (tmp_path / "runs" / "feat-foo-abc123" / "state.json").read_text())
    assert saved == {"iter": 4}
    # After 5 saves, a second construction must still be refused.
    with pytest.raises(leerie.StateLockedError):
        leerie.State(tmp_path, "feat-foo-abc123")


def test_state_lock_disjoint_run_ids_do_not_block(leerie, tmp_path):
    """The lock is per-run-dir, not global. Two State instances on
    different run_ids must both succeed — that's the whole point of
    per-run isolation."""
    sa = leerie.State(tmp_path, "feat-a-aaaaaa")
    sb = leerie.State(tmp_path, "fix-b-bbbbbb")
    assert sa._lock_fd is not None
    assert sb._lock_fd is not None
    assert sa.run_dir != sb.run_dir
