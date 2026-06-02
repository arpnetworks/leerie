"""E1: launcher's bootstrap-id → final-id resolution at resume time.

When the user runs `leerie --resume --run-id _bootstrap-XXX --runtime fly`
after pausing with `leerie --stop _bootstrap-XXX`, the orchestrator on the
machine has already renamed its run dir to a final id via
`State.rename_to`. The launcher must read the final id from the machine
(via `flyctl machine exec cat /work/.leerie/launcher-<bootstrap>.runid`)
and rewrite both `LEERIE_RUN_ID` and the `--run-id` element of
`REWRITTEN_ARGS` before exec'ing the orchestrator. The host-side run
dir gets migrated from `_bootstrap-XXX/` to `<final>/` so `leerie --list`
and subsequent verbs find the run.

Because the E1 logic lives mid-script in the launcher's `RUNTIME=fly`
branch, we test it via a mirror harness rather than sourcing `leerie`
directly. A coupling test below pins the launcher's source so a
refactor that breaks the mirror fails THIS test.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEERIE = REPO_ROOT / "leerie"


# Test harness: a self-contained bash script that mirrors the E1 block.
# Inputs:
#   LEERIE_RUN_ID, LEERIE_MACHINE_ID, FLY_APP, USER_REPO, REWRITTEN_ARGS array,
#   _resumed flag.
# Stubs flyctl: when called with `machine exec MID --app APP -- cat <path>`,
# returns the contents of $tmp_path/handover (if exists) else nothing.
# After running, prints LEERIE_RUN_ID and each REWRITTEN_ARGS element on
# separate lines so the test can assert on them.
_HARNESS = """
set -euo pipefail
LEERIE_RUN_ID="$1"
LEERIE_MACHINE_ID="$2"
FLY_APP="$3"
USER_REPO="$4"
_resumed="$5"
shift 5
REWRITTEN_ARGS=("$@")

if [ "$_resumed" = "true" ] && \\
   [ -n "$LEERIE_RUN_ID" ] && \\
   [[ "$LEERIE_RUN_ID" == _bootstrap-* ]]; then
  _bootstrap_pid="$LEERIE_RUN_ID"
  _final_id="$(flyctl ssh console --app "$FLY_APP" \\
                 --machine "$LEERIE_MACHINE_ID" --pty=false \\
                 -C "cat /work/.leerie/launcher-${_bootstrap_pid}.runid" \\
                 2>/dev/null | head -1 | tr -d '[:space:]' || true)"
  if [ -n "$_final_id" ] && [ "$_final_id" != "$_bootstrap_pid" ]; then
    echo "[leerie] remote: bootstrap id ${_bootstrap_pid} promoted to ${_final_id} on machine — rewriting LEERIE_RUN_ID" >&2
    _host_boot_dir="$USER_REPO/.leerie/runs/${_bootstrap_pid}"
    _host_final_dir="$USER_REPO/.leerie/runs/${_final_id}"
    if [ -d "$_host_boot_dir" ] && [ ! -d "$_host_final_dir" ]; then
      mv "$_host_boot_dir" "$_host_final_dir" 2>/dev/null || true
    fi
    LEERIE_RUN_ID="$_final_id"
    _rewritten_count="${#REWRITTEN_ARGS[@]}"
    _i=0
    while [ "$_i" -lt "$_rewritten_count" ]; do
      if [ "${REWRITTEN_ARGS[$_i]}" = "--run-id" ] && \\
         [ "$((_i + 1))" -lt "$_rewritten_count" ] && \\
         [ "${REWRITTEN_ARGS[$((_i + 1))]}" = "$_bootstrap_pid" ]; then
        REWRITTEN_ARGS[$((_i + 1))]="$_final_id"
        break
      fi
      _i=$((_i + 1))
    done
  fi
fi

echo "LEERIE_RUN_ID=$LEERIE_RUN_ID"
for arg in ${REWRITTEN_ARGS[@]+"${REWRITTEN_ARGS[@]}"}; do
  echo "ARG=$arg"
done
"""


def _stub_flyctl_returns_handover(tmp_path: Path, final_id: str) -> Path:
    """Write a stub `flyctl` that, when called with `machine exec ... cat`,
    prints `final_id`. Records argv to flyctl.log."""
    handover = tmp_path / "handover"
    handover.write_text(f"{final_id}\n")
    stub = tmp_path / "flyctl"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f"echo \"$@\" >> {tmp_path}/flyctl.log\n"
        "# When the launcher does `flyctl ssh console ... -C 'cat /work/...runid'`,\n"
        "# our stub prints the test's handover file. Match by `cat` in the -C arg.\n"
        'for a in "$@"; do\n'
        '  case "$a" in\n'
        '    *cat*launcher-*.runid*)\n'
        f"      cat {handover}\n"
        "      exit 0\n"
        '      ;;\n'
        '  esac\n'
        "done\n"
        "exit 0\n"
    )
    stub.chmod(0o755)
    return stub


def _run_harness(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "-c", _HARNESS, "_", *args],
        env={"PATH": f"{tmp_path}:/usr/bin:/bin"},
        capture_output=True, text=True, check=False,
    )


# --- the happy path -------------------------------------------------------

def test_bootstrap_id_resume_rewrites_run_id_via_handover(tmp_path: Path):
    """When LEERIE_RUN_ID is a bootstrap id and the machine's handover
    file names a final id, the harness rewrites LEERIE_RUN_ID to the
    final id and updates the --run-id element of REWRITTEN_ARGS."""
    _stub_flyctl_returns_handover(tmp_path, "feat-foo-abc123")
    user_repo = tmp_path / "user-repo"
    (user_repo / ".leerie" / "runs" / "_bootstrap-aaaaaa").mkdir(parents=True)
    (user_repo / ".leerie" / "runs" / "_bootstrap-aaaaaa" / "run.json").write_text(
        '{"paused_at": "x", "fly_machine_id": "mach"}'
    )
    r = _run_harness(
        tmp_path,
        "_bootstrap-aaaaaa",  # LEERIE_RUN_ID
        "mach-test",           # LEERIE_MACHINE_ID
        "leerie",                # FLY_APP
        str(user_repo),        # USER_REPO
        "true",                # _resumed
        # REWRITTEN_ARGS — mirrors what `leerie --resume --run-id _bootstrap-aaaaaa --runtime fly` builds
        "--runtime", "fly", "--resume", "--run-id", "_bootstrap-aaaaaa",
    )
    assert r.returncode == 0, r.stderr
    assert "LEERIE_RUN_ID=feat-foo-abc123" in r.stdout
    assert "ARG=feat-foo-abc123" in r.stdout
    assert "ARG=_bootstrap-aaaaaa" not in r.stdout
    # Host dir migrated.
    assert (user_repo / ".leerie" / "runs" / "feat-foo-abc123").is_dir()
    assert not (user_repo / ".leerie" / "runs" / "_bootstrap-aaaaaa").exists()
    # Notification printed to stderr.
    assert "promoted to feat-foo-abc123" in r.stderr


# --- no-op when not a bootstrap id ----------------------------------------

def test_non_bootstrap_id_is_left_alone(tmp_path: Path):
    """When LEERIE_RUN_ID is already a final id, the harness short-circuits
    and does NOT call flyctl or rewrite anything."""
    _stub_flyctl_returns_handover(tmp_path, "should-never-see-this")
    user_repo = tmp_path / "user-repo"
    user_repo.mkdir()
    r = _run_harness(
        tmp_path,
        "feat-already-abc123",
        "mach-x", "leerie", str(user_repo), "true",
        "--runtime", "fly", "--resume", "--run-id", "feat-already-abc123",
    )
    assert r.returncode == 0, r.stderr
    assert "LEERIE_RUN_ID=feat-already-abc123" in r.stdout
    # No flyctl invocation.
    assert not (tmp_path / "flyctl.log").exists()


def test_not_resumed_skips_rewrite(tmp_path: Path):
    """The E1 block fires only when _resumed=true. A fresh provision
    must not consult the handover."""
    _stub_flyctl_returns_handover(tmp_path, "should-never-see-this")
    user_repo = tmp_path / "user-repo"
    user_repo.mkdir()
    r = _run_harness(
        tmp_path,
        "_bootstrap-aaaaaa",
        "mach-x", "leerie", str(user_repo), "false",  # not resumed
        "--runtime", "fly",
    )
    assert r.returncode == 0, r.stderr
    assert "LEERIE_RUN_ID=_bootstrap-aaaaaa" in r.stdout
    assert not (tmp_path / "flyctl.log").exists()


# --- no handover file: the bootstrap id stays ----------------------------

def test_no_handover_leaves_bootstrap_id_unchanged(tmp_path: Path):
    """If the machine doesn't have a handover file (orchestrator hadn't
    yet renamed before pause), the launcher leaves LEERIE_RUN_ID alone
    and proceeds with the bootstrap id. The downstream orchestrator
    then needs the F1 carve-out in resolve_run_id to accept the
    explicit `_bootstrap-*` --run-id (the default discover_runs filter
    would otherwise skip the bootstrap dir and die). This test only
    covers the launcher-side rewrite (or lack thereof); the
    orchestrator-side carve-out is tested in
    test_resolve_run_id.py::test_resolve_explicit_bootstrap_id_accepted_when_state_json_exists."""
    # Stub flyctl that returns nothing (no handover).
    stub = tmp_path / "flyctl"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f"echo \"$@\" >> {tmp_path}/flyctl.log\n"
        "exit 0\n"  # nothing on stdout
    )
    stub.chmod(0o755)
    user_repo = tmp_path / "user-repo"
    user_repo.mkdir()
    r = _run_harness(
        tmp_path,
        "_bootstrap-aaaaaa",
        "mach-x", "leerie", str(user_repo), "true",
        "--runtime", "fly", "--resume", "--run-id", "_bootstrap-aaaaaa",
    )
    assert r.returncode == 0, r.stderr
    assert "LEERIE_RUN_ID=_bootstrap-aaaaaa" in r.stdout
    assert "ARG=_bootstrap-aaaaaa" in r.stdout


# --- coupling test: the launcher source must match the harness ----------

def test_launcher_e1_block_pinned():
    """Coupling test: the E1 block in the launcher must match what the
    harness above tests. Pin a few distinctive substrings so a refactor
    that diverges from the harness fails THIS test instead of silently
    skipping coverage."""
    launcher = LEERIE.read_text()
    # The bootstrap-id branch guard.
    assert '[[ "$LEERIE_RUN_ID" == _bootstrap-* ]]' in launcher
    # The handover-cat flyctl ssh console invocation.
    assert 'cat /work/.leerie/launcher-${_bootstrap_pid}.runid' in launcher
    # The notification banner.
    assert 'promoted to' in launcher
    # The REWRITTEN_ARGS array element rewrite.
    assert 'REWRITTEN_ARGS[$((_i + 1))]="$_final_id"' in launcher
    # The host-side migration step.
    assert 'mv "$_host_boot_dir" "$_host_final_dir"' in launcher
