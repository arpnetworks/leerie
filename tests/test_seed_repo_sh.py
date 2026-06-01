"""Tests for scripts/remote/seed-repo.sh.

seed-repo.sh is sourced by the pila launcher after provision_machine()
succeeds.  These tests exercise the script's bash logic in isolation via
subprocess, with flyctl and git stubbed out so no real Fly.io calls or
network traffic occur.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_SH = REPO_ROOT / "scripts" / "remote" / "seed-repo.sh"


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


def test_seed_repo_sh_exists():
    assert SEED_SH.exists(), "scripts/remote/seed-repo.sh is missing"


def test_seed_repo_sh_is_executable():
    assert os.access(SEED_SH, os.X_OK), (
        "scripts/remote/seed-repo.sh is not executable"
    )


def test_seed_repo_fails_without_machine_id():
    """seed_repo returns 1 when PILA_MACHINE_ID is unset."""
    result = _run_bash(
        f"source {SEED_SH}; seed_repo",
        env={"PILA_MACHINE_ID": "", "USER_REPO": "/tmp"},
    )
    assert result.returncode != 0
    assert "PILA_MACHINE_ID" in result.stderr


def test_seed_repo_fails_without_user_repo():
    """seed_repo returns 1 when USER_REPO is unset."""
    result = _run_bash(
        f"source {SEED_SH}; seed_repo",
        env={"PILA_MACHINE_ID": "test-machine-001", "USER_REPO": ""},
    )
    assert result.returncode != 0
    assert "USER_REPO" in result.stderr


def test_seed_repo_fails_when_flyctl_missing():
    """seed_repo returns 1 with an actionable error when flyctl is absent."""
    result = _run_bash(
        f"source {SEED_SH}; seed_repo",
        env={
            "PILA_MACHINE_ID": "test-machine-001",
            "USER_REPO": "/tmp",
            "PATH": "/usr/bin:/bin",  # no flyctl here
        },
    )
    assert result.returncode != 0
    assert "flyctl" in result.stderr.lower()


def test_seed_repo_succeeds_without_origin_remote(tmp_path):
    """seed_repo no longer requires a git remote — the tar-pipe path
    delivers the whole tree (including .git) from the host, so a
    no-remote repo seeds normally."""
    repo = tmp_path / "myrepo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@test.com"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Test"],
        check=True, capture_output=True,
    )

    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    fake_flyctl.write_text(
        "#!/usr/bin/env bash\n"
        f"echo \"flyctl $*\" >> {exec_log}\n"
        "cat > /dev/null\n"  # drain stdin so the tar producer doesn't SIGPIPE
        "exit 0\n"
    )
    fake_flyctl.chmod(0o755)

    result = _run_bash(
        f"source {SEED_SH}; seed_repo",
        env={
            "PILA_MACHINE_ID": "test-machine-001",
            "PILA_FLY_APP": "pila",
            "USER_REPO": str(repo),
            "PATH": f"{tmp_path}:/usr/bin:/bin",
        },
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"


def test_seed_repo_git_aware_excludes_and_includes(tmp_path):
    """seed_repo's tar payload obeys .gitignore (skipping build artifacts),
    hard-skips .pila/, hard-includes .claude/, and always includes .git/.
    Verifies the full git-ls-files + force-include pipeline."""
    repo = tmp_path / "myrepo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@test.com"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Test"],
        check=True, capture_output=True,
    )
    # .gitignore excludes build artifacts AND .claude/ (the latter is
    # the common case — we want to force-include it despite this).
    (repo / ".gitignore").write_text("build/\n*.log\n.claude/\n")
    # Tracked source file.
    (repo / "src.py").write_text("print('hi')")
    # Untracked-not-ignored file (rides along).
    (repo / "untracked.txt").write_text("untracked")
    # Gitignored build artifact (must NOT ride along).
    (repo / "build").mkdir()
    (repo / "build" / "out.bin").write_text("artifact")
    # Gitignored log file (must NOT ride along).
    (repo / "debug.log").write_text("noise")
    # Host run state (must NOT ride along, even though not in .gitignore).
    (repo / ".pila" / "runs" / "old").mkdir(parents=True)
    (repo / ".pila" / "runs" / "old" / "state.json").write_text("{}")
    # Repo-local Claude settings (gitignored, but force-include).
    (repo / ".claude" / "hooks").mkdir(parents=True)
    (repo / ".claude" / "settings.local.json").write_text('{"x": 1}')
    (repo / ".claude" / "hooks" / "pre-tool-use.sh").write_text("#!/bin/sh\n")
    subprocess.run(
        ["git", "-C", str(repo), "add", ".gitignore", "src.py"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "init"],
        check=True, capture_output=True,
    )

    # Stub flyctl: capture stdin into a tar file we can inspect.
    captured_tar = tmp_path / "captured.tar"
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    fake_flyctl.write_text(
        "#!/usr/bin/env bash\n"
        f"echo \"flyctl $*\" >> {exec_log}\n"
        # If the -C arg contains "tar -xC /work", we're the tar receiver:
        # capture stdin into the tarfile for later inspection.
        # Any other invocation: drain stdin and exit 0.
        'for arg in "$@"; do\n'
        f'  if [ "$arg" = "tar -xC /work" ]; then cat > "{captured_tar}"; exit 0; fi\n'
        'done\n'
        "cat > /dev/null\n"
        "exit 0\n"
    )
    fake_flyctl.chmod(0o755)

    result = _run_bash(
        f"source {SEED_SH}; seed_repo",
        env={
            "PILA_MACHINE_ID": "test-machine-gitaware",
            "PILA_FLY_APP": "pila",
            "USER_REPO": str(repo),
            "PATH": f"{tmp_path}:/usr/bin:/bin",
        },
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert captured_tar.exists(), "tar payload was never captured"

    # Extract and check.
    extract_dir = tmp_path / "extracted"
    extract_dir.mkdir()
    subprocess.run(
        ["tar", "-xf", str(captured_tar), "-C", str(extract_dir)],
        check=True, capture_output=True,
    )
    landed = {
        str(p.relative_to(extract_dir))
        for p in extract_dir.rglob("*")
        if p.is_file()
    }

    # Tracked + untracked-not-ignored ride along.
    assert "src.py" in landed
    assert "untracked.txt" in landed
    assert ".gitignore" in landed
    # Gitignored artifacts do NOT ride along.
    assert "build/out.bin" not in landed, (
        f"gitignored build artifact leaked into seed: {landed}"
    )
    assert "debug.log" not in landed, (
        f"gitignored log file leaked into seed: {landed}"
    )
    # .pila/ never rides along regardless of .gitignore.
    assert not any(p.startswith(".pila/") for p in landed), (
        f"host .pila/ leaked into seed: {landed}"
    )
    # .claude/ rides along EVEN THOUGH .gitignore lists it.
    assert ".claude/settings.local.json" in landed, (
        f".claude/ should be force-included; got: {landed}"
    )
    assert ".claude/hooks/pre-tool-use.sh" in landed
    # .git/ rides along (worker needs full history for worktrees).
    assert any(p.startswith(".git/") for p in landed), (
        f".git/ must be force-included; got: {landed}"
    )


def test_seed_repo_tar_pipes_full_tree(tmp_path):
    """seed_repo wipes /work and tar-pipes the host tree (including .git)
    via flyctl ssh console -C "tar -xC /work"."""
    repo = tmp_path / "myrepo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "test@test.com"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "Test"],
        check=True, capture_output=True,
    )
    (repo / "README.md").write_text("hello")
    subprocess.run(
        ["git", "-C", str(repo), "add", "README.md"], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "init"],
        check=True, capture_output=True,
    )
    # An untracked file — must still ride along in the tar pipe.
    (repo / "local_notes.txt").write_text("my notes")

    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    fake_flyctl.write_text(
        "#!/usr/bin/env bash\n"
        f"echo \"flyctl $*\" >> {exec_log}\n"
        # Drain stdin so the tar producer doesn't get SIGPIPE.
        "cat > /dev/null\n"
        "exit 0\n"
    )
    fake_flyctl.chmod(0o755)

    result = _run_bash(
        f"source {SEED_SH}; seed_repo",
        env={
            "PILA_MACHINE_ID": "test-machine-abc",
            "PILA_FLY_APP": "pila",
            "USER_REPO": str(repo),
            "PATH": f"{tmp_path}:/usr/bin:/bin",
        },
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert exec_log.exists(), "flyctl was never called"
    log_text = exec_log.read_text()
    # The /work wipe step.
    assert "rm -rf /work" in log_text, (
        f"Expected /work wipe via ssh console -C; got:\n{log_text}"
    )
    # The tar pipe target.
    assert "tar -xC /work" in log_text, (
        f"Expected tar-pipe target on remote; got:\n{log_text}"
    )
    # We must NOT see git clone — that's the removed channel.
    assert "git clone" not in log_text, (
        f"git clone should be gone (was the SSH-keys-on-Fly bug); got:\n{log_text}"
    )
