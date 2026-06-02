"""Tests for seed_inspect_dirs in scripts/remote/seed-repo.sh.

seed_inspect_dirs ships each --inspect-dir host path to /inspect/<basename>
on the Fly machine via rsync over `flyctl ssh console`. It's called by the
leerie launcher after seed_repo on fresh provision and after re_seed on
resume. See docs/IMPLEMENTATION.md §0.5 "Remote runtime (Fly.io) transport".

These tests stub flyctl and exercise the bash function in isolation via
subprocess. The stub recognizes:

  1. `-C "true"`: wait_for_fly_ssh_ready probe → exit 0.
  2. `-C "sh -c 'mkdir -p /inspect && chown leerie: /inspect'"`: the
     one-shot inspect parent setup. Rewrite `/inspect` → DEST/inspect and
     eval locally.
  3. `rsync*` with a `<machine>:/inspect/<base>/` target: rewrite the
     trailing `/inspect/` → `DEST/inspect/` and eval the rewritten
     rsync locally so the protocol completes.
  4. `chown -R leerie: /inspect/<base>`: exit 0 (no `leerie` user on
     the test host).
  5. Anything else: drain stdin and exit 0 (defensive — keeps unrelated
     producers from SIGPIPE'ing).
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


def _make_stub_flyctl(stub_path: Path, exec_log: Path, dest_dir: Path,
                      fail_rsync: bool = False) -> None:
    """Stub flyctl that handles the seed_inspect_dirs pattern and actually
    executes rsync locally against `dest_dir/inspect/...`.

    fail_rsync=True makes every rsync invocation exit 1; used to assert
    that seed_inspect_dirs aborts on the first failure and does not
    attempt subsequent records.
    """
    dest = str(dest_dir.resolve())
    log_path = str(exec_log.resolve())
    rsync_fail_clause = "exit 1" if fail_rsync else """
    # The driver rsync -e wrapper invokes flyctl with the receiver-side
    # rsync command, e.g. `rsync --server ... /inspect/<base>/`. Rewrite
    # the path so the receiver runs against DEST/inspect/<base>/ on the
    # test host. Same pattern test_seed_repo_sh.py uses for /work.
    local_cmd="${remote_cmd// \\/inspect/ $DEST/inspect}"
    eval "$local_cmd"
    exit $?
"""
    stub_path.write_text(
        f"""#!/usr/bin/env bash
echo "flyctl $*" >> {log_path!r}

DEST={dest!r}

# Parse args: pull -C "<cmd>" out of argv.
remote_cmd=""
while [ $# -gt 0 ]; do
  case "$1" in
    -C) remote_cmd="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# wait_for_fly_ssh_ready probe.
if [ "$remote_cmd" = "true" ]; then
  exit 0
fi

case "$remote_cmd" in
  *"mkdir -p /inspect"*)
    # One-shot inspect parent setup. Rewrite /inspect → DEST/inspect.
    local_cmd="${{remote_cmd//chown leerie: \\/inspect/true}}"
    local_cmd="${{local_cmd//\\/inspect/$DEST/inspect}}"
    eval "$local_cmd"
    exit $?
    ;;
  rsync*)
    {rsync_fail_clause}
    ;;
  *"chown -R leerie: /inspect"*)
    # Per-dir chown after rsync. No `leerie` user on the test host; swallow.
    exit 0
    ;;
  *)
    cat > /dev/null
    exit 0
    ;;
esac
"""
    )
    stub_path.chmod(0o755)


def _make_stub_timeout(stub_dir: Path) -> None:
    """Same `timeout` stub as test_seed_repo_sh.py — macOS doesn't ship
    GNU `timeout` in /usr/bin, and the tests pin PATH for determinism."""
    stub = stub_dir / "timeout"
    stub.write_text(
        """#!/usr/bin/env bash
while [[ "$1" == --* ]]; do shift; done
shift  # discard the seconds arg
exec "$@"
"""
    )
    stub.chmod(0o755)


def _make_host_inspect_dir(root: Path, name: str, files: dict[str, str]) -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    for relpath, content in files.items():
        f = d / relpath
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
    return d


def test_seed_inspect_dirs_no_op_when_empty(tmp_path):
    """Empty LEERIE_INSPECT_HOST_TARGETS → returns 0 and never calls flyctl."""
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    _make_stub_flyctl(fake_flyctl, exec_log, tmp_path)
    _make_stub_timeout(tmp_path)

    result = _run_bash(
        f"source {SEED_SH}; seed_inspect_dirs",
        env={
            "LEERIE_MACHINE_ID": "test-machine-001",
            "LEERIE_FLY_APP": "leerie",
            "USER_REPO": str(tmp_path),
            "LEERIE_INSPECT_HOST_TARGETS": "",
            "PATH": f"{tmp_path}:/usr/bin:/bin",
        },
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    # _seed_repo_preflight runs `flyctl auth status` even on the empty
    # path; what must NOT happen is any ssh-console / rsync / mkdir
    # invocation against the machine.
    log_text = exec_log.read_text() if exec_log.exists() else ""
    assert "ssh console" not in log_text, (
        f"empty inspect set should never call ssh console; got:\n{log_text}"
    )
    assert "rsync" not in log_text, (
        f"empty inspect set should never invoke rsync; got:\n{log_text}"
    )


def test_seed_inspect_dirs_fails_without_machine_id(tmp_path):
    """seed_inspect_dirs returns 1 when LEERIE_MACHINE_ID is unset."""
    result = _run_bash(
        f"source {SEED_SH}; seed_inspect_dirs",
        env={
            "LEERIE_MACHINE_ID": "",
            "USER_REPO": str(tmp_path),
            "LEERIE_INSPECT_HOST_TARGETS": f"{tmp_path}/x\t/inspect/x",
        },
    )
    assert result.returncode != 0
    assert "LEERIE_MACHINE_ID" in result.stderr


def test_seed_inspect_dirs_single_dir_lands(tmp_path):
    """One inspect-dir record → file lands at DEST/inspect/<basename>/<file>."""
    src = _make_host_inspect_dir(tmp_path / "hostroot", "beacon",
                                 {"README.md": "hi beacon"})
    dest = tmp_path / "machine"
    dest.mkdir()
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    _make_stub_flyctl(fake_flyctl, exec_log, dest)
    _make_stub_timeout(tmp_path)

    record = f"{src}\t/inspect/beacon"
    result = _run_bash(
        f"source {SEED_SH}; seed_inspect_dirs",
        env={
            "LEERIE_MACHINE_ID": "test-machine-001",
            "LEERIE_FLY_APP": "leerie",
            "USER_REPO": str(tmp_path),
            "LEERIE_INSPECT_HOST_TARGETS": record,
            "PATH": f"{tmp_path}:/usr/bin:/bin",
        },
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    landed = dest / "inspect" / "beacon" / "README.md"
    assert landed.exists(), f"file did not land at {landed}; stderr={result.stderr}"
    assert landed.read_text() == "hi beacon"


def test_seed_inspect_dirs_multiple_dirs_each_lands_separately(tmp_path):
    """Two inspect-dir records → both contents land at their distinct targets."""
    src_a = _make_host_inspect_dir(tmp_path / "hostroot", "stackpulse",
                                   {"src/api.ts": "export const x = 1"})
    src_b = _make_host_inspect_dir(tmp_path / "hostroot", "navegando",
                                   {"docs/intro.md": "navegando docs"})
    dest = tmp_path / "machine"
    dest.mkdir()
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    _make_stub_flyctl(fake_flyctl, exec_log, dest)
    _make_stub_timeout(tmp_path)

    record = f"{src_a}\t/inspect/stackpulse\n{src_b}\t/inspect/navegando"
    result = _run_bash(
        f"source {SEED_SH}; seed_inspect_dirs",
        env={
            "LEERIE_MACHINE_ID": "test-machine-001",
            "LEERIE_FLY_APP": "leerie",
            "USER_REPO": str(tmp_path),
            "LEERIE_INSPECT_HOST_TARGETS": record,
            "PATH": f"{tmp_path}:/usr/bin:/bin",
        },
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert (dest / "inspect" / "stackpulse" / "src" / "api.ts").read_text() == \
        "export const x = 1"
    assert (dest / "inspect" / "navegando" / "docs" / "intro.md").read_text() == \
        "navegando docs"


def test_seed_inspect_dirs_chowns_each_target(tmp_path):
    """After each rsync, `chown -R leerie: /inspect/<base>` appears in the
    exec log — same ownership-handover pattern seed_repo_dirty uses."""
    src_a = _make_host_inspect_dir(tmp_path / "hostroot", "alpha",
                                   {"a.txt": "a"})
    src_b = _make_host_inspect_dir(tmp_path / "hostroot", "bravo",
                                   {"b.txt": "b"})
    dest = tmp_path / "machine"
    dest.mkdir()
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    _make_stub_flyctl(fake_flyctl, exec_log, dest)
    _make_stub_timeout(tmp_path)

    record = f"{src_a}\t/inspect/alpha\n{src_b}\t/inspect/bravo"
    result = _run_bash(
        f"source {SEED_SH}; seed_inspect_dirs",
        env={
            "LEERIE_MACHINE_ID": "test-machine-001",
            "LEERIE_FLY_APP": "leerie",
            "USER_REPO": str(tmp_path),
            "LEERIE_INSPECT_HOST_TARGETS": record,
            "PATH": f"{tmp_path}:/usr/bin:/bin",
        },
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    log = exec_log.read_text()
    assert "chown -R leerie: /inspect/alpha" in log, (
        f"missing alpha chown; log:\n{log}"
    )
    assert "chown -R leerie: /inspect/bravo" in log, (
        f"missing bravo chown; log:\n{log}"
    )


def test_seed_inspect_dirs_preserves_nfc_unicode_filenames(tmp_path):
    """Inspect dirs commonly contain non-ASCII filenames (PDFs, docs).
    rsync preserves filename bytes verbatim on the Linux receiver — no
    NFC→NFD flip from a tar pipe. Regression-protects the rationale that
    drove the seed_repo_dirty design (seed-repo.sh:22-38)."""
    nfc_name = "Planón.pdf"  # 'ó' as single codepoint U+00F3 (NFC)
    src = _make_host_inspect_dir(tmp_path / "hostroot", "docs",
                                 {nfc_name: "binary-ish content"})
    dest = tmp_path / "machine"
    dest.mkdir()
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    _make_stub_flyctl(fake_flyctl, exec_log, dest)
    _make_stub_timeout(tmp_path)

    record = f"{src}\t/inspect/docs"
    result = _run_bash(
        f"source {SEED_SH}; seed_inspect_dirs",
        env={
            "LEERIE_MACHINE_ID": "test-machine-001",
            "LEERIE_FLY_APP": "leerie",
            "USER_REPO": str(tmp_path),
            "LEERIE_INSPECT_HOST_TARGETS": record,
            "PATH": f"{tmp_path}:/usr/bin:/bin",
        },
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    landed_files = [p.name for p in (dest / "inspect" / "docs").iterdir()]
    assert nfc_name in landed_files, (
        f"NFC filename {nfc_name!r} not preserved; landed files: "
        f"{[name.encode('utf-8') for name in landed_files]}"
    )


def test_seed_inspect_dirs_skips_non_inspect_targets(tmp_path):
    """Records whose remote target is NOT under /inspect/ are skipped
    structurally — belt-and-braces against an in-repo path slipping
    through the launcher's redundant-mount-skip branch."""
    src = _make_host_inspect_dir(tmp_path / "hostroot", "weird",
                                 {"x.txt": "x"})
    dest = tmp_path / "machine"
    dest.mkdir()
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    _make_stub_flyctl(fake_flyctl, exec_log, dest)
    _make_stub_timeout(tmp_path)

    # Remote target points at /work/sub — must NOT be rsync'd.
    record = f"{src}\t/work/sub"
    result = _run_bash(
        f"source {SEED_SH}; seed_inspect_dirs",
        env={
            "LEERIE_MACHINE_ID": "test-machine-001",
            "LEERIE_FLY_APP": "leerie",
            "USER_REPO": str(tmp_path),
            "LEERIE_INSPECT_HOST_TARGETS": record,
            "PATH": f"{tmp_path}:/usr/bin:/bin",
        },
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    # mkdir /inspect should have happened, but no rsync for /work/sub
    # should appear in the log.
    log = exec_log.read_text()
    assert "rsync" not in log, (
        f"non-/inspect target should be skipped; rsync log line found:\n{log}"
    )
    assert "skipping non-/inspect target" in result.stderr


def test_seed_inspect_dirs_creates_inspect_parent_first(tmp_path):
    """The mkdir /inspect step appears in the log BEFORE any rsync — so
    per-dir rsync lands under a leerie-owned parent."""
    src = _make_host_inspect_dir(tmp_path / "hostroot", "first",
                                 {"a.txt": "a"})
    dest = tmp_path / "machine"
    dest.mkdir()
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    _make_stub_flyctl(fake_flyctl, exec_log, dest)
    _make_stub_timeout(tmp_path)

    record = f"{src}\t/inspect/first"
    result = _run_bash(
        f"source {SEED_SH}; seed_inspect_dirs",
        env={
            "LEERIE_MACHINE_ID": "test-machine-001",
            "LEERIE_FLY_APP": "leerie",
            "USER_REPO": str(tmp_path),
            "LEERIE_INSPECT_HOST_TARGETS": record,
            "PATH": f"{tmp_path}:/usr/bin:/bin",
        },
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    log = exec_log.read_text()
    mkdir_pos = log.find("mkdir -p /inspect")
    rsync_pos = log.find("rsync")
    assert mkdir_pos != -1, f"missing mkdir /inspect step; log:\n{log}"
    assert rsync_pos != -1, f"missing rsync step; log:\n{log}"
    assert mkdir_pos < rsync_pos, (
        f"mkdir /inspect must precede rsync; got positions "
        f"mkdir={mkdir_pos}, rsync={rsync_pos}; log:\n{log}"
    )


def test_seed_inspect_dirs_aborts_on_rsync_failure(tmp_path):
    """A failed rsync makes seed_inspect_dirs return 1 and stop — the
    second record is NOT attempted. Mirrors seed_repo_dirty's fatal-on-
    rsync-failure behavior."""
    src_a = _make_host_inspect_dir(tmp_path / "hostroot", "alpha",
                                   {"a.txt": "a"})
    src_b = _make_host_inspect_dir(tmp_path / "hostroot", "bravo",
                                   {"b.txt": "b"})
    dest = tmp_path / "machine"
    dest.mkdir()
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    _make_stub_flyctl(fake_flyctl, exec_log, dest, fail_rsync=True)
    _make_stub_timeout(tmp_path)

    record = f"{src_a}\t/inspect/alpha\n{src_b}\t/inspect/bravo"
    result = _run_bash(
        f"source {SEED_SH}; seed_inspect_dirs",
        env={
            "LEERIE_MACHINE_ID": "test-machine-001",
            "LEERIE_FLY_APP": "leerie",
            "USER_REPO": str(tmp_path),
            "LEERIE_INSPECT_HOST_TARGETS": record,
            "PATH": f"{tmp_path}:/usr/bin:/bin",
        },
    )
    assert result.returncode != 0, (
        f"expected nonzero exit on rsync failure; got 0\n"
        f"stderr={result.stderr}\nlog={exec_log.read_text()}"
    )
    log = exec_log.read_text()
    # bravo's chown must NOT appear — we should have bailed after alpha
    # failed.
    assert "chown -R leerie: /inspect/bravo" not in log, (
        f"bravo should not have been attempted after alpha rsync failed; "
        f"log:\n{log}"
    )


def test_seed_inspect_dirs_skips_malformed_record(tmp_path):
    """A record without a tab separator is logged and skipped (not
    rsync'd to an empty/bogus target). Belt-and-braces defense."""
    dest = tmp_path / "machine"
    dest.mkdir()
    exec_log = tmp_path / "exec_log.txt"
    fake_flyctl = tmp_path / "flyctl"
    _make_stub_flyctl(fake_flyctl, exec_log, dest)
    _make_stub_timeout(tmp_path)

    record = "/some/path-without-tab-separator"  # no \t
    result = _run_bash(
        f"source {SEED_SH}; seed_inspect_dirs",
        env={
            "LEERIE_MACHINE_ID": "test-machine-001",
            "LEERIE_FLY_APP": "leerie",
            "USER_REPO": str(tmp_path),
            "LEERIE_INSPECT_HOST_TARGETS": record,
            "PATH": f"{tmp_path}:/usr/bin:/bin",
        },
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    log = exec_log.read_text()
    assert "rsync" not in log, (
        f"malformed record should be skipped; rsync log line found:\n{log}"
    )
    assert "malformed record" in result.stderr
