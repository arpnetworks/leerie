"""Behavioral test for scripts/new-worktree.sh idempotency.

Verifies that new-worktree.sh correctly reuses an existing worktree
when called a second time with the same subtask-id and run-id.
Without the WT-canonicalization fix, the reuse check fails when
LEERIE_STATE_DIR is unset (WT is relative, git worktree list
outputs absolute paths), causing the second call to crash with
'fatal: ... already exists'.
"""
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "new-worktree.sh"


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(cwd),
        capture_output=True, text=True, check=False,
    )


def _run_new_worktree(cwd: Path, sid: str, run_id: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.pop("LEERIE_STATE_DIR", None)
    return subprocess.run(
        ["bash", str(SCRIPT), sid, run_id],
        cwd=str(cwd), capture_output=True, text=True, check=False, env=env,
    )


def test_reuse_worktree_when_state_dir_unset(tmp_path: Path) -> None:
    """Second call reuses existing worktree instead of crashing."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git("init", "-q", "-b", "main", cwd=repo)
    _git("config", "user.email", "test@leerie.local", cwd=repo)
    _git("config", "user.name", "leerie-test", cwd=repo)
    _git("config", "commit.gpgsign", "false", cwd=repo)
    (repo / "file.txt").write_text("initial\n")
    _git("add", "file.txt", cwd=repo)
    _git("commit", "-q", "-m", "initial", cwd=repo)
    _git("branch", "leerie/runs/run-42", "main", cwd=repo)

    r1 = _run_new_worktree(repo, "sub-001", "run-42")
    assert r1.returncode == 0, f"first call failed: {r1.stderr}"
    wt1 = r1.stdout.strip().splitlines()[-1]
    assert Path(wt1).is_absolute()
    assert Path(wt1).is_dir()

    r2 = _run_new_worktree(repo, "sub-001", "run-42")
    assert r2.returncode == 0, f"second call failed (reuse path broken): {r2.stderr}"
    wt2 = r2.stdout.strip().splitlines()[-1]
    assert wt2 == wt1


def test_reuse_worktree_when_state_dir_set(tmp_path: Path) -> None:
    """Reuse also works when LEERIE_STATE_DIR is an absolute path."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git("init", "-q", "-b", "main", cwd=repo)
    _git("config", "user.email", "test@leerie.local", cwd=repo)
    _git("config", "user.name", "leerie-test", cwd=repo)
    _git("config", "commit.gpgsign", "false", cwd=repo)
    (repo / "file.txt").write_text("initial\n")
    _git("add", "file.txt", cwd=repo)
    _git("commit", "-q", "-m", "initial", cwd=repo)
    _git("branch", "leerie/runs/run-42", "main", cwd=repo)

    state_dir = tmp_path / "state"
    env = dict(os.environ)
    env["LEERIE_STATE_DIR"] = str(state_dir)

    def _run(sid: str, run_id: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(SCRIPT), sid, run_id],
            cwd=str(repo), capture_output=True, text=True, check=False, env=env,
        )

    r1 = _run("sub-001", "run-42")
    assert r1.returncode == 0, f"first call failed: {r1.stderr}"
    wt1 = r1.stdout.strip().splitlines()[-1]
    assert Path(wt1).is_absolute()

    r2 = _run("sub-001", "run-42")
    assert r2.returncode == 0, f"second call failed (reuse path broken): {r2.stderr}"
    wt2 = r2.stdout.strip().splitlines()[-1]
    assert wt2 == wt1
