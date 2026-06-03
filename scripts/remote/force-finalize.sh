#!/usr/bin/env bash
# scripts/remote/force-finalize.sh — patch finished_at into a stuck run's
# run.json on the Fly Machine, after verifying the orchestrator process is
# dead.
#
# When does this run?  `leerie --finalize <run-id> --force`.  Today's
# fetch-branch.sh discovery loop scans .leerie/runs/*/run.json on the machine
# for entries with `finished_at` set and `pushed_at` unset (DESIGN §6
# *Finalization*).  When the orchestrator dies before phase_finalize (ENOSPC
# mid-merge, worker crash, kill -9, etc.), `finished_at` is never written and
# the discovery loop returns zero — the user cannot recover the work via
# `leerie --finalize` because the run isn't "finalized" from the host's view.
#
# The recovery procedure is mechanical: SSH in, check the orchestrator is
# really dead, patch run.json with `finished_at` + audit fields, exit, then
# re-run --finalize.  Doing this by hand requires knowing internals;
# automating it via --force keeps the recovery on the user's well-trodden
# path.
#
# Safety belt: this script REFUSES to patch a run where the orchestrator
# process is still alive.  Predicate (verified against `leerie` launcher
# lines 1806, 1812–1814 and `scripts/remote/lib.sh` line 221 on 2026-06-02):
#
#   * The launcher's _launch_script writes orchestrator.pid immediately
#     after subprocess.Popen returns, BEFORE the orchestrator's first phase
#     runs — so the file is in place from the moment the orchestrator
#     exists.
#   * Nothing in orchestrator/leerie.py ever deletes the pid file — it is
#     the expected stale artifact after a clean exit.
#
#   Therefore on the machine:
#     pid file MISSING                         → REFUSE (early-failure or
#                                                 tampering — bail to manual)
#     pid file present + kill -0 succeeds +    → REFUSE (orchestrator is
#       /proc/<pid>/cmdline contains "python"   alive; force would race the
#                                                running orchestrator)
#     pid file present + kill -0 fails ESRCH   → SAFE (stale pid file from
#                                                 a dead orchestrator; this
#                                                 is what we expect)
#
# The /proc/<pid>/cmdline guard catches pid reuse — short-lived per-run
# Fly machines make this very unlikely but it's a cheap check.
#
# Why cmdline and not comm: the kernel sets /proc/<pid>/comm from argv[0]
# of the parent's execve call (basename of the *invoked* binary), NOT
# from the shebang interpreter the kernel actually loaded. For a
# pip-installed Python script like `pytest`, that means comm = "pytest"
# even though the running ELF is /usr/bin/python3 — "python" not in
# "pytest", so a comm-based check would let an alive orchestrator slip
# through on any non-trivial launcher. /proc/<pid>/cmdline holds the
# full execve argv (NUL-separated) after shebang resolution, which
# always names the interpreter explicitly. Verified inside
# python:3.10-slim on 2026-06-02 that comm='pytest' but cmdline starts
# with '/usr/local/bin/python3.10\0/usr/local/bin/pytest\0…'.
#
# Platform note: the Python payload runs ON THE MACHINE (Linux), which
# always has /proc. The pid-reuse guard works as designed there. If the
# payload is ever exercised on a system without /proc (e.g. a macOS
# host test fixture), pathlib.Path("/proc/<pid>/cmdline").read_bytes()
# raises and the exception handler sets the identity marker to "?" —
# the "python" check then evaluates False and the script falls through
# to the patch branch. That is intentional for the production code path
# (Linux machine only) and documented here for any future Darwin reuse;
# tests/test_force_finalize_sh.py::test_refuses_when_pid_alive gates on
# sys.platform == "linux" for the same reason.
#
# Usage (sourced by the leerie launcher's --finalize --force fast-path):
#
#   source scripts/remote/force-finalize.sh
#   force_finalize_remote "$FLY_APP" "$LEERIE_MACHINE_ID"
#
# Environment consumed:
#   FLY_APP             — Fly.io app name (e.g. "leerie")
#   LEERIE_MACHINE_ID   — ID of the Fly Machine to SSH into
#
# Exit semantics:
#   0  — patch succeeded (or run was already finalized; idempotent)
#   1  — refused (orchestrator alive, pid file missing, ambiguous run dirs,
#        SSH failure, JSON parse error on the remote side)
#
# After this returns 0, the caller (`leerie --finalize`) falls through to
# the normal fetch_branch path.

set -eu -o pipefail

# Source _log.sh so remote_log is available even when sourced standalone.
# shellcheck disable=SC1091
. "${LEERIE_REPO:-$(cd -- "$(dirname "$(dirname "$(dirname "${BASH_SOURCE[0]}")")")" && pwd -P)}/scripts/remote/_log.sh"

force_finalize_remote() {
  local app="${1:-${FLY_APP:-leerie}}"
  local machine="${2:-${LEERIE_MACHINE_ID:-}}"

  if [ -z "$machine" ]; then
    remote_log "force-finalize: LEERIE_MACHINE_ID not set"
    return 1
  fi

  # The discovery + pid-check + patch payload, run on the machine as a
  # single python3 invocation via `bash -lc`.  Single python so all
  # decisions happen atomically; no risk of a half-patched run.json.
  #
  # The payload prints one of three sentinel lines to stdout that the
  # host-side caller parses to drive logging:
  #   OK:<final_run_id>          — patched (or already finalized); fall through
  #   REFUSE-ALIVE:<pid>:<comm>  — orchestrator alive; do not proceed
  #   REFUSE-NOPID:<run_id>      — pid file missing
  #   REFUSE-MULTI:<count>       — more than one non-bootstrap run dir
  #   REFUSE-NONE                — no non-bootstrap run dir
  #   ERROR:<message>            — anything else
  local payload
  payload=$(cat <<'PYEOF'
import json
import os
import pathlib
import sys
import time

runs_dir = pathlib.Path("/work/.leerie/runs")
if not runs_dir.is_dir():
    print("ERROR:no /work/.leerie/runs on machine")
    sys.exit(1)

# Discover the single non-bootstrap run dir.
candidates = [
    p for p in runs_dir.iterdir()
    if p.is_dir() and not p.name.startswith("_bootstrap-")
]
if len(candidates) == 0:
    print("REFUSE-NONE")
    sys.exit(0)
if len(candidates) > 1:
    print(f"REFUSE-MULTI:{len(candidates)}")
    sys.exit(0)
run_dir = candidates[0]
run_id = run_dir.name

run_json_path = run_dir / "run.json"
if not run_json_path.is_file():
    print(f"ERROR:run.json missing under {run_dir}")
    sys.exit(1)

try:
    data = json.loads(run_json_path.read_text())
except Exception as exc:  # noqa: BLE001
    print(f"ERROR:run.json parse failed: {exc}")
    sys.exit(1)

# Idempotent — if finished_at is already set, no patch needed.
if data.get("finished_at"):
    print(f"OK:{run_id}")
    sys.exit(0)

# Verify orchestrator process is dead.
pid_path = run_dir / "orchestrator.pid"
if not pid_path.is_file():
    print(f"REFUSE-NOPID:{run_id}")
    sys.exit(0)
try:
    pid = int(pid_path.read_text().strip())
except Exception:
    print(f"ERROR:orchestrator.pid not an integer in {run_dir}")
    sys.exit(1)

# kill -0: does the process exist?
alive = False
try:
    os.kill(pid, 0)
    alive = True
except ProcessLookupError:
    alive = False
except PermissionError:
    # EPERM means it exists but is not signalable; treat as alive.
    alive = True

ident = ""
if alive:
    # Read /proc/<pid>/cmdline (NUL-separated execve argv) rather than
    # /proc/<pid>/comm. See the header comment "Why cmdline and not
    # comm" — comm is the basename of the invoked binary (e.g.
    # "pytest"), but cmdline always names the interpreter explicitly.
    try:
        cmdline_raw = pathlib.Path(f"/proc/{pid}/cmdline").read_bytes()
        is_python = b"python" in cmdline_raw
        first = cmdline_raw.split(b"\x00", 1)[0].decode(errors="replace")
        ident = first.rsplit("/", 1)[-1] if first else "?"
    except Exception:
        is_python = False
        ident = "?"
    # Guard against pid reuse: only refuse if the live process looks like
    # the orchestrator (a python process).  On short-lived Fly machines
    # collision is unlikely but the check is cheap.
    if is_python:
        print(f"REFUSE-ALIVE:{pid}:{ident}")
        sys.exit(0)
    # If it's NOT python, treat the pid file as a stale collision and
    # proceed.  Log this in audit fields below.

# Safe to patch.
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
data["finished_at"] = now
data["recovered_at"] = now
data["recovered_via"] = "force-finalize"
# Mechanism flag: the orchestrator died before it could set its own
# no_push intent; treat as user-intent-push (the host-side finalize gate
# remains the source of truth for actual push decisions).
if data.get("no_push") is True:
    data["no_push"] = False

tmp_path = run_json_path.with_suffix(".json.tmp")
tmp_path.write_text(json.dumps(data, indent=2) + "\n")
os.replace(tmp_path, run_json_path)
print(f"OK:{run_id}")
sys.exit(0)
PYEOF
)

  # Pipe the Python source via stdin to `python3 -` on the machine. This
  # sidesteps the `flyctl ssh console --command` argv-not-shell semantics
  # (the bug Part 1.5 fixed in attach.sh) and Python's own quoting
  # (single vs triple, escapes) entirely — the script body never has to
  # round-trip through a shell quoter.
  local result
  if ! result="$(printf '%s' "$payload" \
        | flyctl ssh console --app "$app" --machine "$machine" \
            --pty=false -C "python3 -" 2>&1)"; then
    remote_log "force-finalize: SSH to machine $machine failed"
    remote_log "  output: $result"
    return 1
  fi

  # Result lines: the python prints exactly one sentinel; flyctl's own
  # "Connecting to …" stderr lands on stderr (which we merged with 2>&1)
  # so filter for the sentinel.  Strip CR (flyctl ssh console can produce
  # CRLF line endings when fronted by a TTY-emulating layer).
  local sentinel
  sentinel="$(printf '%s\n' "$result" | tr -d '\r' \
              | grep -E '^(OK|REFUSE-ALIVE|REFUSE-NOPID|REFUSE-MULTI|REFUSE-NONE|ERROR):?' \
              | tail -1 || true)"
  if [ -z "$sentinel" ]; then
    remote_log "force-finalize: no sentinel in remote output:"
    remote_log "  $result"
    return 1
  fi

  case "$sentinel" in
    OK:*)
      local rid="${sentinel#OK:}"
      remote_log "force-finalize: machine=$machine run=$rid patched (finished_at + recovered_at + recovered_via=force-finalize)"
      return 0
      ;;
    REFUSE-ALIVE:*)
      local rest="${sentinel#REFUSE-ALIVE:}"
      local pid="${rest%%:*}"
      local comm="${rest#*:}"
      remote_log "force-finalize: REFUSED — orchestrator pid $pid ($comm) is still alive on machine $machine."
      remote_log "  Use \`leerie --kill <run-id>\` if you really want to abandon the run, or"
      remote_log "  \`leerie --attach <run-id>\` to inspect what it's doing first."
      return 1
      ;;
    REFUSE-NOPID:*)
      local rid="${sentinel#REFUSE-NOPID:}"
      remote_log "force-finalize: REFUSED — run $rid has no orchestrator.pid on machine $machine."
      remote_log "  This usually means the orchestrator failed very early (before phase_classify)."
      remote_log "  Attach manually with \`leerie --attach\` to inspect, then \`--kill\` when done."
      return 1
      ;;
    REFUSE-MULTI:*)
      local count="${sentinel#REFUSE-MULTI:}"
      remote_log "force-finalize: REFUSED — $count non-bootstrap run dirs on machine $machine; can't pick one."
      remote_log "  Attach manually to disambiguate."
      return 1
      ;;
    REFUSE-NONE)
      remote_log "force-finalize: REFUSED — no non-bootstrap run dir on machine $machine."
      remote_log "  The orchestrator likely never reached phase_classify."
      return 1
      ;;
    ERROR:*)
      remote_log "force-finalize: ${sentinel}"
      return 1
      ;;
    *)
      remote_log "force-finalize: unexpected sentinel: $sentinel"
      return 1
      ;;
  esac
}
