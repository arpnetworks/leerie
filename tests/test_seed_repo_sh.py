"""Tests for scripts/remote/seed-repo.sh.

seed-repo.sh is sourced by the pila launcher after provision_machine()
succeeds.  These tests exercise the script's bash logic in isolation via
subprocess, with flyctl and git stubbed out so no real Fly.io calls or
network traffic occur.

The seed mechanism uses `git bundle` over `flyctl ssh console -C "sh
-c 'cat > ...'"` for the transport. The stub flyctl below recognizes
these classes of invocation (substring matchers, so the `sh -c '...'`
wrapper is handled transparently):

  1. `--machine probe-nonexistent`: require_fly_ssh's cert-validity
     probe — emit "no started VMs" on stderr so the helper short-circuits.
  2. `-C "true"`: wait_for_fly_ssh_ready's readiness probe — exit 0.
  3. `-C "sh -c '...find /work...'"`: the /work content-wipe step.
     Just exit 0 (we'll let the machine-side clone create the dir).
  4. `-C "sh -c 'cat > /tmp/pila-seed.bundle'"`: capture stdin to
     <dest_dir>/seed.bundle (the parent bundle pipe).
  5. `-C "sh -c 'cat > /tmp/pila-subs/<name>.bundle'"`: capture stdin
     to <dest_dir>/subs/<name>.bundle (a submodule bundle pipe).
  6. `-C "sh -c '<clone-script>'"`: the machine-side clone command.
     Rewrite the absolute paths in the script (`/tmp/pila-seed.bundle`,
     `/tmp/pila-subs`, `/work`) to point at the test's <dest_dir>, then
     exec the script. The resulting clone tree is what tests inspect.
     The script contains `git -c protocol.file.allow=always submodule
     update --recursive`, which the stub passes through unchanged so
     the local git invocation accepts the file://-style bundle URLs.
  7. Anything else: log and exit 0.
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


def _make_stub_flyctl(stub_path: Path, exec_log: Path, dest_dir: Path) -> None:
    """Stub flyctl that handles the bundle-pipe seed pattern AND actually
    executes the machine-side clone+submodule-update on the test host.

    The clone command's body is rewritten so all `/tmp/pila-*` and `/work`
    paths point inside `dest_dir`, then it's exec'd locally. After the
    test the dest_dir/work directory contains a real git clone of the
    fixture repo, suitable for assertions about working-tree content.
    """
    # Resolve dest_dir to absolute, then escape for safe substitution in
    # a sed-like sequence inside the stub.
    dest = str(dest_dir.resolve())
    stub_path.write_text(
        f"""#!/usr/bin/env bash
echo "flyctl $*" >> {exec_log}

DEST={dest!r}

# Parse args: pull -C "<cmd>" and --machine <id> out of argv.
remote_cmd=""
machine=""
while [ $# -gt 0 ]; do
  case "$1" in
    -C) remote_cmd="$2"; shift 2 ;;
    --machine) machine="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# require_fly_ssh probe.
if [ "$machine" = "probe-nonexistent" ]; then
  echo "Error: no started VMs" >&2
  exit 1
fi

# wait_for_fly_ssh_ready probe.
if [ "$remote_cmd" = "true" ]; then
  exit 0
fi

# Drain stdin to a target file (used by bundle-pipe and as fallback).
_drain_to() {{
  mkdir -p "$(dirname "$1")"
  cat > "$1"
}}

case "$remote_cmd" in
  *"cat > /tmp/pila-seed.bundle"*)
    _drain_to "$DEST/seed.bundle"
    exit 0
    ;;
  *"cat > /tmp/pila-subs/"*)
    # Extract the per-submodule basename from "cat > /tmp/pila-subs/<bn>".
    bn="${{remote_cmd##*cat > /tmp/pila-subs/}}"
    _drain_to "$DEST/subs/$bn"
    exit 0
    ;;
  *"find /work -mindepth"*)
    # /work reset step. Make sure the parent of DEST/work exists and is empty.
    rm -rf "$DEST/work" "$DEST/subs"
    mkdir -p "$DEST" "$DEST/subs"
    exit 0
    ;;
  *"git clone /tmp/pila-seed.bundle /work"*)
    # The machine-side clone script. Rewrite absolute paths to point
    # inside the test's DEST dir, then strip the chown (no pila user
    # on the test host), then exec.
    #
    # Step 1: strip the `chown -R pila: /work` line BEFORE path
    # substitution, since the path substitution would rewrite /work
    # everywhere and make the chown harder to recognize.
    local_cmd="${{remote_cmd//chown -R pila: \\/work/true}}"
    # Step 2: strip the post-clone `rm -rf /tmp/pila-...` cleanup so
    # tests can still inspect the bundle files we captured.
    local_cmd="${{local_cmd//rm -rf \\/tmp\\/pila-seed.bundle \\/tmp\\/pila-subs/true}}"
    # Step 3: rewrite the absolute paths.
    local_cmd="${{local_cmd//\\/tmp\\/pila-seed.bundle/$DEST/seed.bundle}}"
    local_cmd="${{local_cmd//\\/tmp\\/pila-subs/$DEST/subs}}"
    local_cmd="${{local_cmd//\\/work/$DEST/work}}"
    eval "$local_cmd"
    exit $?
    ;;
  chown*)
    # Standalone chown calls (none expected post-bundle-rewrite, but
    # safe to swallow).
    exit 0
    ;;
  *)
    # Unknown remote command. Drain stdin so producers don't SIGPIPE
    # and exit 0.
    cat > /dev/null
    exit 0
    ;;
esac
"""
    )
    stub_path.chmod(0o755)


def _make_stub_timeout(stub_dir: Path) -> None:
    """Stub `timeout` for hosts where coreutils isn't on /usr/bin.

    lib.sh's require_fly_ssh and wait_for_fly_ssh_ready both wrap flyctl
    in `timeout <secs>` so a stuck WireGuard handshake doesn't hang the
    seed forever. macOS doesn't ship `timeout` in /usr/bin (it's in
    coreutils via Homebrew). Tests pin PATH to a controlled set so they
    don't depend on the host's Homebrew layout; this stub provides
    `timeout` semantics (run the child, propagate rc, ignore the time
    cap) good enough for unit tests."""
    stub = stub_dir / "timeout"
    stub.write_text(
        """#!/usr/bin/env bash
# Stub timeout: skip the time arg(s), exec the rest. Handles both
#   timeout 8 cmd ...
#   timeout --kill-after=2 10 cmd ...
while [[ "$1" == --* ]]; do shift; done
shift  # discard the seconds arg
exec "$@"
"""
    )
    stub.chmod(0o755)


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


def test_seed_repo_succeeds_on_minimal_repo(tmp_path):
    """seed_repo completes end-to-end against a minimal one-commit repo
    with no submodules."""
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

    dest = tmp_path / "machine"
    dest.mkdir()
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    _make_stub_flyctl(fake_flyctl, exec_log, dest)
    _make_stub_timeout(tmp_path)

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
    # The clone landed at dest/work.
    assert (dest / "work" / "README.md").exists(), (
        f"clone target /work didn't materialize at {dest/'work'}; "
        f"stderr={result.stderr}"
    )
    # It's a proper git clone.
    assert (dest / "work" / ".git").is_dir()


def test_seed_repo_pipes_bundle_via_ssh_console(tmp_path):
    """seed_repo invokes git bundle + flyctl ssh console -C 'cat > ...'.
    Asserts the three structural calls land in the exec log."""
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

    dest = tmp_path / "machine"
    dest.mkdir()
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    _make_stub_flyctl(fake_flyctl, exec_log, dest)
    _make_stub_timeout(tmp_path)

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
    log_text = exec_log.read_text()

    # /work content-wipe step (must run before bundle pipe so /tmp is fresh).
    assert "find /work -mindepth 1 -maxdepth 1" in log_text, (
        f"expected /work content-wipe step; got:\n{log_text}"
    )
    # Parent bundle pipe.
    assert "cat > /tmp/pila-seed.bundle" in log_text, (
        f"expected parent bundle pipe; got:\n{log_text}"
    )
    # Machine-side clone command.
    assert "git clone /tmp/pila-seed.bundle /work" in log_text, (
        f"expected machine-side clone from bundle; got:\n{log_text}"
    )
    # No rsync (the old path).
    assert "rsync" not in log_text, (
        f"rsync should not appear in the new bundle-only path; got:\n{log_text}"
    )
    # No tar -xC (the older tar-pipe path).
    assert "tar -xC /work" not in log_text, (
        f"tar -xC /work should be gone; got:\n{log_text}"
    )
    # The bundle file actually landed.
    assert (dest / "seed.bundle").exists(), (
        f"parent bundle was not captured at {dest/'seed.bundle'}"
    )


def test_seed_repo_preserves_nfc_unicode_filenames_in_submodule(tmp_path):
    """Regression test for the live failure on ~/src/enric/api on
    2026-06-01: a submodule contained a PDF with an NFC `ó` and 📄
    emoji in its name. The old tar-pipe path flipped the filename to
    NFD during host-side `tar -c`, which made git's working-tree
    match fail on the Linux receiver.

    With the bundle pipe + machine-side `git clone`, the filename
    never transits as a string — it's stored as raw bytes in pack
    objects. Linux git materializes it natively. This test builds the
    NFC fixture, runs the seed pipeline through the stub, and verifies
    the resulting working tree has the NFC bytes intact in the
    submodule's content."""
    # NFC ó = b"\xc3\xb3". 📄 emoji = b"\xf0\x9f\x93\x84".
    # Don't use a Python literal for the filename — the source file's
    # encoding could normalize it. Build from raw bytes.
    nfc_name = b"\xf0\x9f\x93\x84Plan de implementaci\xc3\xb3n.pdf"
    nfc_str = nfc_name.decode("utf-8")

    # Build the submodule source.
    sub = tmp_path / "submodule-source"
    sub.mkdir()
    subprocess.run(["git", "-C", str(sub), "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(sub), "config", "user.email", "t@t.com"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(sub), "config", "user.name", "T"],
        check=True, capture_output=True,
    )
    (sub / nfc_str).write_text("fake pdf content")
    subprocess.run(
        ["git", "-C", str(sub), "add", nfc_str], check=True, capture_output=True
    )
    subprocess.run(
        ["git", "-C", str(sub), "commit", "-m", "add pdf"],
        check=True, capture_output=True,
    )

    # Build the parent repo with the submodule added at "data".
    parent = tmp_path / "myrepo"
    parent.mkdir()
    subprocess.run(["git", "-C", str(parent), "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(parent), "config", "user.email", "t@t.com"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(parent), "config", "user.name", "T"],
        check=True, capture_output=True,
    )
    (parent / "README.md").write_text("parent")
    subprocess.run(
        ["git", "-C", str(parent), "add", "README.md"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(parent), "commit", "-m", "init"],
        check=True, capture_output=True,
    )
    subprocess.run(
        [
            "git", "-C", str(parent), "-c", "protocol.file.allow=always",
            "submodule", "add", str(sub), "data",
        ],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(parent), "commit", "-m", "add submodule"],
        check=True, capture_output=True,
    )

    dest = tmp_path / "machine"
    dest.mkdir()
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    _make_stub_flyctl(fake_flyctl, exec_log, dest)
    _make_stub_timeout(tmp_path)

    result = _run_bash(
        f"source {SEED_SH}; seed_repo",
        env={
            "PILA_MACHINE_ID": "test-machine-submodule",
            "PILA_FLY_APP": "pila",
            "USER_REPO": str(parent),
            "PATH": f"{tmp_path}:/usr/bin:/bin",
            # No GIT_ALLOW_PROTOCOL needed — the production code embeds
            # `git -c protocol.file.allow=always submodule update` in the
            # machine-side clone script, and the stub passes that flag
            # through unchanged when it eval's the rewritten script.
        },
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"

    # The PDF must land inside data/ in the cloned /work, with its
    # NFC bytes intact.
    pdf_path = dest / "work" / "data" / nfc_str
    landed = sorted(
        os.fsencode(p.name)
        for p in (dest / "work" / "data").rglob("*")
        if p.is_file() and not p.name.startswith(".")
    )
    assert pdf_path.exists(), (
        f"submodule's NFC-named PDF did not land at {pdf_path}\n"
        f"actually landed in data/: {landed}"
    )
    # And the filename bytes on disk equal the NFC bytes the host has.
    assert nfc_name in landed, (
        f"NFC filename bytes were not preserved.\n"
        f"expected to find: {nfc_name!r}\n"
        f"actually landed: {landed}"
    )

    # The parent's `git status --porcelain` on the seeded tree should
    # show NO ` M data` (the bug we're fixing). Untracked entries are
    # fine — that's what preflight tolerates.
    porcelain = subprocess.run(
        ["git", "-C", str(dest / "work"), "status", "--porcelain"],
        capture_output=True, text=True, check=True,
    ).stdout
    assert " M data" not in porcelain and "M  data" not in porcelain, (
        f"parent repo flags the submodule dirty after seed — the bug "
        f"we're fixing.\nporcelain:\n{porcelain}"
    )
