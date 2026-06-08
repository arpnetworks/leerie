"""Tests for scripts/remote/collect-subtrees.sh.

collect-subtrees.sh is sourced by the leerie launcher's --finalize path.
It SSHes a bash payload to the Fly Machine that runs setup-run.sh +
integrate.sh for un-merged subtask branches. These tests exercise the
payload logic in isolation via subprocess, with flyctl stubbed and a
fixture git repo standing in for /work + /opt/leerie-image/scripts/.

The bash payload discovers un-integrated subtask branches, runs
setup-run.sh to ensure the staging worktree exists, then merges each
via integrate.sh. Conflicts are skipped. Sentinels communicate the
result to the host-side wrapper.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COLLECT_SH = REPO_ROOT / "scripts" / "remote" / "collect-subtrees.sh"
SCRIPTS_DIR = REPO_ROOT / "scripts"


def _run_bash(script: str, env: dict | None = None) -> subprocess.CompletedProcess:
    base_env = {k: v for k, v in os.environ.items()}
    if env:
        base_env.update(env)
    return subprocess.run(
        ["bash", "-c", script],
        env=base_env,
        capture_output=True,
        text=True,
    )


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo)] + list(args),
        capture_output=True,
        text=True,
        check=check,
    )


def _make_fixture_repo(tmp_path: Path) -> Path:
    """Create a minimal git repo with an initial commit."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "user.email", "test@test.com")
    (repo / "README.md").write_text("hello\n")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "initial")
    return repo


def _make_subtask_branch(
    repo: Path, run_id: str, sid: str, parent_branch: str, files: dict[str, str]
) -> None:
    """Create a subtask branch with commits off parent_branch."""
    branch = f"leerie/subtasks/{run_id}/{sid}"
    _git(repo, "branch", branch, parent_branch)
    _git(repo, "checkout", branch)
    for name, content in files.items():
        (repo / name).write_text(content)
        _git(repo, "add", name)
    _git(repo, "commit", "-m", f"subtask {sid}")
    _git(repo, "checkout", "main")


def _make_run_branch(repo: Path, run_id: str) -> None:
    """Create the run branch at HEAD (simulates setup-run.sh having run)."""
    branch = f"leerie/runs/{run_id}"
    _git(repo, "branch", branch, "HEAD")


def _make_fake_flyctl(tmp_path: Path, repo: Path, state_dir: Path) -> Path:
    """Stub flyctl that routes `bash -s` payloads to a local bash invocation
    with paths rewritten to point at the fixture repo."""
    stub = tmp_path / "bin" / "flyctl"
    stub.parent.mkdir(parents=True, exist_ok=True)
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f'REPO="{repo}"\n'
        f'STATE_DIR="{state_dir}"\n'
        f'SCRIPTS="{SCRIPTS_DIR}"\n'
        'CMD=""\n'
        'while [ $# -gt 0 ]; do\n'
        '  case "$1" in\n'
        '    -C) CMD="$2"; shift 2 ;;\n'
        '    auth) shift; case "${1:-}" in status) exit 0 ;; esac ;;\n'
        '    *) shift ;;\n'
        '  esac\n'
        'done\n'
        '[ -z "$CMD" ] && exit 0\n'
        'case "$CMD" in\n'
        '  bash*-s*)\n'
        '    SCRIPT="$(cat)"\n'
        # Rewrite in-machine paths to fixture paths.
        '    REWRITTEN="${SCRIPT//\\/opt\\/leerie-image\\/scripts/$SCRIPTS}"\n'
        '    REWRITTEN="${REWRITTEN//\\/work\\/.leerie\\/runs/$STATE_DIR/runs}"\n'
        '    REWRITTEN="${REWRITTEN//cd \\/work/cd $REPO}"\n'
        # Override LEERIE_STATE_DIR for the payload.
        f'    export LEERIE_STATE_DIR="{state_dir}"\n'
        '    printf "%s" "$REWRITTEN" | bash -s\n'
        '    exit $?\n'
        '    ;;\n'
        '  *) exit 0 ;;\n'
        'esac\n'
    )
    stub.chmod(0o755)
    return stub


def _make_state_json(
    state_dir: Path,
    run_id: str,
    waves: list[list[str]] | None = None,
    completed_waves: int = 0,
) -> None:
    """Write a minimal state.json for wave ordering."""
    run_dir = state_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    data = {"run_id": run_id, "task": "test"}
    if waves is not None:
        data["waves"] = waves
        data["completed_waves"] = completed_waves
    (run_dir / "state.json").write_text(json.dumps(data, indent=2))
    # Also create working-branch file (needed by setup-run.sh)
    (run_dir / "working-branch").write_text("main\n")


def test_collect_subtrees_sh_exists():
    assert COLLECT_SH.exists()


def test_refuses_when_no_machine_id():
    result = _run_bash(
        f"source {COLLECT_SH}; collect_subtrees_remote leerie ''",
        env={"LEERIE_REPO": str(REPO_ROOT)},
    )
    assert result.returncode != 0
    assert "LEERIE_MACHINE_ID" in result.stderr


def test_collected_none_when_all_integrated(tmp_path):
    """When every subtask branch is already an ancestor of the run branch,
    sentinel is COLLECTED-NONE."""
    repo = _make_fixture_repo(tmp_path)
    run_id = "test-all-integrated-abc"
    state_dir = tmp_path / "state"

    _make_run_branch(repo, run_id)
    _make_state_json(state_dir, run_id, waves=[["s1"]], completed_waves=1)

    # Create a subtask branch at the same commit as run branch (already integrated).
    _git(repo, "branch", f"leerie/subtasks/{run_id}/s1",
         f"leerie/runs/{run_id}")

    stub = _make_fake_flyctl(tmp_path, repo, state_dir)
    env = {
        "LEERIE_REPO": str(REPO_ROOT),
        "PATH": f"{stub.parent}:{os.environ['PATH']}",
    }
    result = _run_bash(
        f"source {COLLECT_SH}; collect_subtrees_remote leerie machine-xxx",
        env=env,
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    assert "already integrated" in result.stderr.lower() or "COLLECTED-NONE" in result.stderr


def test_collected_all_clean_merges(tmp_path):
    """Two un-integrated subtasks that touch different files merge cleanly."""
    repo = _make_fixture_repo(tmp_path)
    run_id = "test-clean-merge-abc"
    state_dir = tmp_path / "state"

    _make_run_branch(repo, run_id)
    _make_state_json(state_dir, run_id, waves=[["s1", "s2"]], completed_waves=0)

    _make_subtask_branch(repo, run_id, "s1", f"leerie/runs/{run_id}",
                         {"file_a.txt": "content a\n"})
    _make_subtask_branch(repo, run_id, "s2", f"leerie/runs/{run_id}",
                         {"file_b.txt": "content b\n"})

    stub = _make_fake_flyctl(tmp_path, repo, state_dir)
    env = {
        "LEERIE_REPO": str(REPO_ROOT),
        "PATH": f"{stub.parent}:{os.environ['PATH']}",
    }
    result = _run_bash(
        f"source {COLLECT_SH}; collect_subtrees_remote leerie machine-xxx",
        env=env,
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    assert "integrated 2" in result.stderr.lower()

    # Verify the run branch now has both files.
    show_a = _git(repo, "show", f"leerie/runs/{run_id}:file_a.txt", check=False)
    show_b = _git(repo, "show", f"leerie/runs/{run_id}:file_b.txt", check=False)
    assert show_a.returncode == 0, "file_a.txt missing from run branch"
    assert show_b.returncode == 0, "file_b.txt missing from run branch"


def test_collected_with_conflict_skipped(tmp_path):
    """When two subtasks modify the same file region, one merges and the
    other is skipped (conflict). Sentinel reports the skip."""
    repo = _make_fixture_repo(tmp_path)
    run_id = "test-conflict-abc"
    state_dir = tmp_path / "state"

    _make_run_branch(repo, run_id)
    _make_state_json(state_dir, run_id, waves=[["s1", "s2"]], completed_waves=0)

    # Both subtasks modify the same file with conflicting content.
    _make_subtask_branch(repo, run_id, "s1", f"leerie/runs/{run_id}",
                         {"conflict.txt": "version A\n"})
    _make_subtask_branch(repo, run_id, "s2", f"leerie/runs/{run_id}",
                         {"conflict.txt": "version B\n"})

    stub = _make_fake_flyctl(tmp_path, repo, state_dir)
    env = {
        "LEERIE_REPO": str(REPO_ROOT),
        "PATH": f"{stub.parent}:{os.environ['PATH']}",
    }
    result = _run_bash(
        f"source {COLLECT_SH}; collect_subtrees_remote leerie machine-xxx",
        env=env,
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    # One integrated, one skipped.
    assert "integrated 1" in result.stderr.lower()
    assert "skipped 1" in result.stderr.lower()


def test_collected_none_when_no_subtask_branches(tmp_path):
    """When no subtask branches exist at all, sentinel is COLLECTED-NONE."""
    repo = _make_fixture_repo(tmp_path)
    run_id = "test-no-branches-abc"
    state_dir = tmp_path / "state"

    _make_run_branch(repo, run_id)
    _make_state_json(state_dir, run_id, waves=[[]], completed_waves=0)

    stub = _make_fake_flyctl(tmp_path, repo, state_dir)
    env = {
        "LEERIE_REPO": str(REPO_ROOT),
        "PATH": f"{stub.parent}:{os.environ['PATH']}",
    }
    result = _run_bash(
        f"source {COLLECT_SH}; collect_subtrees_remote leerie machine-xxx",
        env=env,
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    assert "already integrated" in result.stderr.lower() or "COLLECTED-NONE" in result.stderr


def test_setup_run_creates_missing_worktree(tmp_path):
    """When the run branch doesn't exist yet, setup-run.sh creates it
    and the collection can still proceed."""
    repo = _make_fixture_repo(tmp_path)
    run_id = "test-no-run-branch-abc"
    state_dir = tmp_path / "state"

    # Don't create run branch — setup-run.sh inside the payload should do it.
    _make_state_json(state_dir, run_id, waves=[["s1"]], completed_waves=0)

    _make_subtask_branch(repo, run_id, "s1", "main",
                         {"new_file.txt": "new content\n"})

    stub = _make_fake_flyctl(tmp_path, repo, state_dir)
    env = {
        "LEERIE_REPO": str(REPO_ROOT),
        "PATH": f"{stub.parent}:{os.environ['PATH']}",
    }
    result = _run_bash(
        f"source {COLLECT_SH}; collect_subtrees_remote leerie machine-xxx",
        env=env,
    )
    assert result.returncode == 0, f"stderr={result.stderr}"
    assert "integrated 1" in result.stderr.lower()

    # Verify the run branch was created and has the file.
    show = _git(repo, "show", f"leerie/runs/{run_id}:new_file.txt", check=False)
    assert show.returncode == 0, "new_file.txt missing from run branch"
