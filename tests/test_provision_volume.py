"""Tests for the FLY_VM_DISK_GB opt-in volume in provision.sh.

The volume is the operational lever the user pulls when a run hits
ENOSPC on Fly's default ephemeral disk. These tests assert two
things via flyctl-stub interception:

  (a) UNSET: `flyctl machine run` is called WITHOUT --volume, and
      `flyctl volumes create` is NEVER called. The invocation must be
      byte-for-byte identical to today's behavior.

  (b) SET: `flyctl volumes create ... --size N` runs first, the volume
      ID is captured, and `flyctl machine run --volume <id>:/home/leerie`
      runs after. volume_id ends up in the persisted run.json.

The stub flyctl records every invocation into a log file so the test
can replay-assert the exact argv sequence.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROVISION_SH = REPO_ROOT / "scripts" / "remote" / "provision.sh"


def _run_bash(script: str, env: dict | None = None,
              cwd: Path | None = None) -> subprocess.CompletedProcess:
    base_env = {k: v for k, v in os.environ.items()}
    if env:
        base_env.update(env)
    return subprocess.run(
        ["bash", "-c", script],
        env=base_env,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )


def _make_recording_flyctl(tmp_path: Path) -> tuple[Path, Path]:
    """Stub flyctl that records every invocation and emits realistic
    output so provision.sh can parse machine/volume IDs.

    Returns: (stub_path, invocation_log_path). The log is one line per
    call, with arguments joined by '|' for unambiguous parsing.
    """
    log_path = tmp_path / "flyctl-calls.log"
    log_path.write_text("")
    stub = tmp_path / "flyctl"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f'LOG="{log_path}"\n'
        '# Record the argv with | as separator (no | in any of our args).\n'
        'argv=""\n'
        'for a in "$@"; do\n'
        '  if [ -z "$argv" ]; then argv="$a"; else argv="$argv|$a"; fi\n'
        'done\n'
        'echo "$argv" >> "$LOG"\n'
        # Dispatch by subcommand.
        'case "$1" in\n'
        '  auth)\n'
        '    case "${2:-}" in\n'
        '      status) exit 0 ;;\n'
        '      *)      exit 0 ;;\n'
        '    esac\n'
        '    ;;\n'
        '  volumes|volume)\n'
        '    case "${2:-}" in\n'
        '      create)\n'
        '        # Emit a realistic create output the provision.sh\n'
        '        # parser can read.\n'
        '        cat <<EOF\n'
        '                  ID: vol_abcdef0123456789\n'
        '                Name: test_volume_name\n'
        '                 App: leerie\n'
        '              Region: iad\n'
        '                Size: 30 GB\n'
        'EOF\n'
        '        exit 0\n'
        '        ;;\n'
        '      destroy) exit 0 ;;\n'
        '    esac\n'
        '    ;;\n'
        '  machine)\n'
        '    case "${2:-}" in\n'
        '      run)\n'
        '        # Output a realistic Machine ID line.\n'
        '        echo "  Machine ID: machine-deadbeef1234"\n'
        '        echo "  State: started"\n'
        '        exit 0\n'
        '        ;;\n'
        '      status)\n'
        '        echo "started"\n'
        '        exit 0\n'
        '        ;;\n'
        '      stop|destroy) exit 0 ;;\n'
        '    esac\n'
        '    ;;\n'
        'esac\n'
        'exit 0\n'
    )
    stub.chmod(0o755)
    return stub, log_path


def _read_calls(log_path: Path) -> list[list[str]]:
    """Read the recorded calls and return them as a list of argv lists."""
    if not log_path.exists():
        return []
    return [
        line.split("|")
        for line in log_path.read_text().splitlines()
        if line.strip()
    ]


def _make_run_dir(tmp_path: Path, run_id: str) -> Path:
    """Create a minimal host-side run dir with run.json that
    provision.sh's `update_run_json` can write into."""
    run_dir = tmp_path / "user-repo" / ".leerie" / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text("{}")
    return run_dir


def test_no_volume_when_disk_gb_unset(tmp_path):
    """The byte-for-byte-today guarantee: with FLY_VM_DISK_GB unset,
    no `flyctl volumes create` happens and no `--volume` arg is passed
    to `flyctl machine run`."""
    stub, log = _make_recording_flyctl(tmp_path)
    run_id = "feat-test-001"
    run_dir = _make_run_dir(tmp_path, run_id)
    user_repo = tmp_path / "user-repo"
    env = {
        "LEERIE_REPO": str(REPO_ROOT),
        "PATH": f"{stub.parent}:{os.environ['PATH']}",
        "FLY_IMAGE_TAG": "registry.fly.io/leerie:test",
        "FLY_APP": "leerie",
        "USER_REPO": str(user_repo),
        "LEERIE_RUN_ID": run_id,
        # Skip the wait-for-started polling loop.
        "LEERIE_MACHINE_START_TIMEOUT": "1",
    }
    # Stub wait_for_started to a no-op so the test doesn't actually
    # poll. We do this by overriding the function after sourcing.
    result = _run_bash(
        f"source {PROVISION_SH}\n"
        "wait_for_started() { return 0; }\n"
        "provision_machine\n",
        env=env,
    )
    calls = _read_calls(log)
    # Filter out auth status (called by require_flyctl).
    non_auth = [c for c in calls if c[0] != "auth"]
    # Sanity check: we should see at least one machine-run call.
    machine_runs = [c for c in non_auth if c[:2] == ["machine", "run"]]
    assert machine_runs, f"expected machine run call; calls={calls}"
    # No volume create should have happened.
    volume_creates = [c for c in non_auth if c[:2] == ["volumes", "create"]]
    assert not volume_creates, (
        f"FLY_VM_DISK_GB unset must NOT trigger volume create.\n"
        f"calls={calls}"
    )
    # No --volume arg on the machine-run call.
    for mr in machine_runs:
        assert "--volume" not in mr, (
            f"FLY_VM_DISK_GB unset must NOT pass --volume to machine run.\n"
            f"argv={mr}"
        )
    # And the persisted run.json should not have volume_id.
    sidecar = json.loads((run_dir / "run.json").read_text())
    assert "volume_id" not in sidecar, sidecar


def test_volume_created_when_disk_gb_set(tmp_path):
    """With FLY_VM_DISK_GB=30, volume-create runs first with --size 30,
    machine-run gets --volume "<id>:/home/leerie", and run.json
    captures the volume_id."""
    stub, log = _make_recording_flyctl(tmp_path)
    run_id = "feat-test-002"
    run_dir = _make_run_dir(tmp_path, run_id)
    user_repo = tmp_path / "user-repo"
    env = {
        "LEERIE_REPO": str(REPO_ROOT),
        "PATH": f"{stub.parent}:{os.environ['PATH']}",
        "FLY_IMAGE_TAG": "registry.fly.io/leerie:test",
        "FLY_APP": "leerie",
        "USER_REPO": str(user_repo),
        "LEERIE_RUN_ID": run_id,
        "FLY_VM_DISK_GB": "30",
        "LEERIE_MACHINE_START_TIMEOUT": "1",
    }
    result = _run_bash(
        f"source {PROVISION_SH}\n"
        "wait_for_started() { return 0; }\n"
        "provision_machine\n",
        env=env,
    )
    assert result.returncode == 0, (
        f"provision_machine should succeed; stderr={result.stderr}"
    )
    calls = _read_calls(log)
    # Ignore auth.
    non_auth = [c for c in calls if c[0] != "auth"]
    # First non-auth call: volumes create with --size 30.
    volume_creates = [c for c in non_auth if c[:2] == ["volumes", "create"]]
    assert len(volume_creates) == 1, (
        f"expected one volumes create; calls={calls}"
    )
    vc = volume_creates[0]
    assert "--size" in vc and vc[vc.index("--size") + 1] == "30", vc
    assert "--app" in vc and vc[vc.index("--app") + 1] == "leerie", vc
    # The volume name should be the leerie_data_<6hex> shape.
    # The volume name is the first positional after `volumes create`.
    vol_name = vc[2]
    assert vol_name.startswith("leerie_data_"), vol_name
    # The machine-run call should include --volume with the parsed ID.
    machine_runs = [c for c in non_auth if c[:2] == ["machine", "run"]]
    assert len(machine_runs) == 1, calls
    mr = machine_runs[0]
    assert "--volume" in mr, mr
    vol_arg = mr[mr.index("--volume") + 1]
    assert vol_arg == "vol_abcdef0123456789:/home/leerie", vol_arg
    # Ordering: volumes-create must precede machine-run.
    vc_idx = non_auth.index(vc)
    mr_idx = non_auth.index(mr)
    assert vc_idx < mr_idx, (
        f"volumes create must come before machine run; "
        f"vc_idx={vc_idx} mr_idx={mr_idx}"
    )
    # And the persisted run.json should carry volume_id.
    sidecar = json.loads((run_dir / "run.json").read_text())
    assert sidecar.get("volume_id") == "vol_abcdef0123456789", sidecar
    assert sidecar.get("fly_machine_id") == "machine-deadbeef1234", sidecar


def test_destroy_machine_destroys_volume_when_set(tmp_path):
    """destroy_machine should destroy the volume after the machine when
    LEERIE_VOLUME_ID is set."""
    stub, log = _make_recording_flyctl(tmp_path)
    env = {
        "LEERIE_REPO": str(REPO_ROOT),
        "PATH": f"{stub.parent}:{os.environ['PATH']}",
        "FLY_APP": "leerie",
    }
    result = _run_bash(
        f"source {PROVISION_SH}\n"
        'LEERIE_MACHINE_ID="machine-foo"\n'
        'LEERIE_VOLUME_ID="vol_bar"\n'
        "destroy_machine\n",
        env=env,
    )
    calls = _read_calls(log)
    # Expect: machine destroy, volumes destroy.
    machine_destroys = [c for c in calls if c[:2] == ["machine", "destroy"]]
    volume_destroys = [c for c in calls if c[:2] == ["volumes", "destroy"]]
    assert machine_destroys, calls
    assert volume_destroys, calls
    # Ordering: machine destroy must precede volume destroy. (Fly
    # refuses to destroy a volume still attached to a live machine.)
    md_idx = calls.index(machine_destroys[0])
    vd_idx = calls.index(volume_destroys[0])
    assert md_idx < vd_idx, (
        f"machine destroy must precede volume destroy; "
        f"md_idx={md_idx} vd_idx={vd_idx}"
    )
    # Volume destroy must reference the right ID.
    vd = volume_destroys[0]
    assert "vol_bar" in vd, vd


def test_destroy_machine_does_not_call_volumes_when_unset(tmp_path):
    """destroy_machine should NOT call volumes destroy when
    LEERIE_VOLUME_ID is empty (the today's-behavior case)."""
    stub, log = _make_recording_flyctl(tmp_path)
    env = {
        "LEERIE_REPO": str(REPO_ROOT),
        "PATH": f"{stub.parent}:{os.environ['PATH']}",
        "FLY_APP": "leerie",
    }
    result = _run_bash(
        f"source {PROVISION_SH}\n"
        'LEERIE_MACHINE_ID="machine-foo"\n'
        'LEERIE_VOLUME_ID=""\n'
        "destroy_machine\n",
        env=env,
    )
    calls = _read_calls(log)
    machine_destroys = [c for c in calls if c[:2] == ["machine", "destroy"]]
    volume_destroys = [c for c in calls if c[:2] == ["volumes", "destroy"]]
    assert machine_destroys, calls
    assert not volume_destroys, (
        f"volumes destroy must NOT fire when LEERIE_VOLUME_ID is empty.\n"
        f"calls={calls}"
    )


def _make_recording_flyctl_failing_machine_run(tmp_path: Path) -> tuple[Path, Path]:
    """Variant of _make_recording_flyctl where `machine run` exits non-zero
    (and prints nothing parseable to stdout). Used to exercise the
    orphan-volume cleanup path at provision.sh:533-545 — when machine-
    create fails AFTER volumes-create succeeded, the volume must be
    reaped explicitly because the EXIT trap is not yet registered.
    """
    log_path = tmp_path / "flyctl-calls.log"
    log_path.write_text("")
    stub = tmp_path / "flyctl"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f'LOG="{log_path}"\n'
        'argv=""\n'
        'for a in "$@"; do\n'
        '  if [ -z "$argv" ]; then argv="$a"; else argv="$argv|$a"; fi\n'
        'done\n'
        'echo "$argv" >> "$LOG"\n'
        'case "$1" in\n'
        '  auth)\n'
        '    case "${2:-}" in status) exit 0 ;; *) exit 0 ;; esac\n'
        '    ;;\n'
        '  volumes|volume)\n'
        '    case "${2:-}" in\n'
        '      create)\n'
        # Realistic create output so the parser captures the ID.
        '        cat <<EOF\n'
        '                  ID: vol_abcdef0123456789\n'
        '                Name: test_volume_name\n'
        '                 App: leerie\n'
        'EOF\n'
        '        exit 0\n'
        '        ;;\n'
        # The orphan-cleanup path calls `volumes destroy` — must succeed
        # so we can assert the reaping ran.
        '      destroy) exit 0 ;;\n'
        '    esac\n'
        '    ;;\n'
        '  machine)\n'
        '    case "${2:-}" in\n'
        # The failure under test: machine run exits non-zero with no
        # parseable "Machine ID:" line. The provision parser ends up
        # with machine_id="" and falls into the orphan-cleanup branch.
        '      run)\n'
        '        echo "ERROR: capacity exhausted in region iad" >&2\n'
        '        exit 1\n'
        '        ;;\n'
        '      stop|destroy) exit 0 ;;\n'
        '    esac\n'
        '    ;;\n'
        'esac\n'
        'exit 0\n'
    )
    stub.chmod(0o755)
    return stub, log_path


def test_orphan_volume_cleaned_on_machine_create_failure(tmp_path):
    """When `flyctl machine run` fails AFTER `flyctl volumes create`
    succeeded, the orphan-volume cleanup path at provision.sh:533-545
    must run — otherwise the volume keeps incurring per-GB-month
    charges with no machine to attach it to. The EXIT trap isn't
    registered yet at this point (it fires only after a machine-id is
    captured), so the cleanup has to be explicit.
    """
    stub, log = _make_recording_flyctl_failing_machine_run(tmp_path)
    run_id = "feat-test-orphan"
    _make_run_dir(tmp_path, run_id)
    user_repo = tmp_path / "user-repo"
    env = {
        "LEERIE_REPO": str(REPO_ROOT),
        "PATH": f"{stub.parent}:{os.environ['PATH']}",
        "FLY_IMAGE_TAG": "registry.fly.io/leerie:test",
        "FLY_APP": "leerie",
        "USER_REPO": str(user_repo),
        "LEERIE_RUN_ID": run_id,
        "FLY_VM_DISK_GB": "30",
        "LEERIE_MACHINE_START_TIMEOUT": "1",
    }
    result = _run_bash(
        f"source {PROVISION_SH}\n"
        "wait_for_started() { return 0; }\n"
        "provision_machine\n",
        env=env,
    )
    # provision_machine should fail.
    assert result.returncode != 0, (
        f"expected provision_machine to fail; stderr={result.stderr}"
    )
    calls = _read_calls(log)
    non_auth = [c for c in calls if c[0] != "auth"]
    # The sequence must be: volumes create (success) → machine run
    # (fail) → volumes destroy (cleanup).
    volume_creates = [c for c in non_auth if c[:2] == ["volumes", "create"]]
    machine_runs = [c for c in non_auth if c[:2] == ["machine", "run"]]
    volume_destroys = [c for c in non_auth if c[:2] == ["volumes", "destroy"]]
    assert len(volume_creates) == 1, (
        f"expected exactly one volumes create; calls={non_auth}"
    )
    assert len(machine_runs) == 1, (
        f"expected exactly one machine run (the failing one); calls={non_auth}"
    )
    assert len(volume_destroys) == 1, (
        f"expected exactly one volumes destroy (the orphan cleanup); "
        f"calls={non_auth}"
    )
    # The orphan destroy must target the SAME volume that was created
    # (not some other volume we never knew about).
    vc_id = volume_creates[0][2]  # positional arg after `volumes create`
    vd = volume_destroys[0]
    # `volumes destroy` argv: ["volumes", "destroy", "<id>", "--app", ..., "--yes"]
    assert vd[2] == "vol_abcdef0123456789", (
        f"orphan destroy must target the volume we created (vol_abcdef…); "
        f"got argv={vd}"
    )
    # Ordering: create → run → destroy. Anything else is a sequencing bug.
    vc_idx = non_auth.index(volume_creates[0])
    mr_idx = non_auth.index(machine_runs[0])
    vd_idx = non_auth.index(volume_destroys[0])
    assert vc_idx < mr_idx < vd_idx, (
        f"expected volumes create < machine run < volumes destroy; "
        f"vc_idx={vc_idx} mr_idx={mr_idx} vd_idx={vd_idx}"
    )
