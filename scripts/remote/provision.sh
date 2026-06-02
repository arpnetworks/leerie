#!/usr/bin/env bash
# scripts/remote/provision.sh — provision a Fly.io Machine for one leerie run.
#
# This is the remote equivalent of `nerdctl run --rm`: start a Fly Machine
# from the leerie image, block until the machine is reachable (SSH/started),
# then destroy it on exit — whether the caller exits cleanly, is interrupted
# by Ctrl-C, or crashes.
#
# Usage (invoked from the leerie launcher's REMOTE=true branch):
#
#   source scripts/remote/provision.sh
#   provision_machine             # blocks until machine is started
#   # ... do work (run leerie inside the machine) ...
#   export LEERIE_REMOTE_EXIT_RC=$orch_rc   # launcher sets this on exit
#   # decide_teardown is registered as an EXIT trap; classifies the rc
#   # and routes to stop_machine (pause-on-failure) or destroy_machine.
#
# Environment variables (set by the launcher before sourcing):
#
#   LEERIE_FLY_APP    — Fly.io app name (default: "leerie")
#   FLY_IMAGE_TAG   — full image tag to launch (e.g. registry.fly.io/leerie:0.2.1)
#   FLY_REGION      — Fly.io region (default: from fly.toml or "iad")
#   FLY_VM_CPUS     — vCPUs for the machine (default: 4)
#   FLY_VM_MEMORY   — memory in MB for the machine (default: 8192)
#   LEERIE_RUN_ID     — orchestrator-minted run id (optional; when set,
#                     provision writes fly_machine_id to the run sidecar
#                     and decide_teardown writes paused_at on pause)
#   USER_REPO       — host-side path to the user's repo (for sidecar I/O)
#   LEERIE_REMOTE_EXIT_RC — set by the launcher just before exit; read by
#                     the EXIT trap to classify the orchestrator's exit
#                     code. Pause-worthy: any non-zero other than
#                     EXIT_NEEDS_ANSWERS=10, EX_TEMPFAIL=75, SIGINT=130,
#                     SIGTERM=143. (DESIGN §6 Remote pause-on-failure.)
#
# Exports:
#   LEERIE_MACHINE_ID — the created machine's ID (available after provision_machine)
#
# The teardown trap is registered when provision_machine succeeds. It fires
# on EXIT (clean exit), INT (Ctrl-C), and TERM (SIGTERM). A machine that
# fails to start is destroyed immediately before provision_machine returns 1.

set -euo pipefail

# --- shared lib (update_run_json / iso_now) ------------------------------
_PROVISION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "$_PROVISION_DIR/lib.sh"

# --- configuration with defaults -----------------------------------------
FLY_APP="${LEERIE_FLY_APP:-leerie}"
FLY_REGION="${FLY_REGION:-iad}"
FLY_VM_CPUS="${FLY_VM_CPUS:-4}"
FLY_VM_MEMORY="${FLY_VM_MEMORY:-8192}"

# Max seconds to wait for the machine to reach state "started".
MACHINE_START_TIMEOUT="${LEERIE_MACHINE_START_TIMEOUT:-120}"

# Exported machine ID — empty until provision_machine succeeds.
LEERIE_MACHINE_ID=""

# require_flyctl now lives in lib.sh (sourced above) with auto-install
# support. Inline detection here has been removed to avoid drift.

# --- stop machine --------------------------------------------------------
# Pause-on-failure path: preserves the machine's filesystem on its Fly
# volume so resume-machine.sh can wake it later. Idempotent and tolerant
# of an already-stopped machine.
stop_machine() {
  local mid="$LEERIE_MACHINE_ID"
  if [ -z "$mid" ]; then
    return 0
  fi
  echo "[leerie] remote: stopping machine $mid (paused)..." >&2
  flyctl machine stop "$mid" --app "$FLY_APP" 2>/dev/null || true
  # Don't clear LEERIE_MACHINE_ID — the launcher's notification block
  # needs it to print the attach/resume commands.
}

# --- destroy machine -----------------------------------------------------
# Full reap. Idempotent: destroy is no-op if the machine is already gone.
destroy_machine() {
  local mid="$LEERIE_MACHINE_ID"
  if [ -z "$mid" ]; then
    return 0
  fi
  echo "[leerie] remote: destroying machine $mid ..." >&2
  if flyctl machine destroy "$mid" \
       --app "$FLY_APP" \
       --force \
       2>/dev/null; then
    echo "[leerie] remote: machine $mid destroyed" >&2
  else
    # destroy can fail if the machine was already stopped/destroyed by Fly.
    # Attempt stop first as a fallback, then a second destroy.
    flyctl machine stop "$mid" --app "$FLY_APP" 2>/dev/null || true
    flyctl machine destroy "$mid" --app "$FLY_APP" --force 2>/dev/null || true
    echo "[leerie] remote: machine $mid stop+destroy attempted (may already be gone)" >&2
  fi
  # Drop the PID-keyed attach pointer (Phase 3) — the machine no longer
  # exists, so attach should report "no active remote machine" next time.
  if [ -n "${USER_REPO:-}" ]; then
    rm -f "$USER_REPO/.leerie/remote/$$.json"
  fi
  LEERIE_MACHINE_ID=""
}

# --- _try_fetch_branch_for_teardown --------------------------------------
# Source fetch-branch.sh (idempotent — safe to re-source) and run
# fetch_branch against the live machine. Returns 0 on success (state
# + run branch are on the host), 1 on any failure (network, missing
# run dir on machine, etc).
#
# Called from decide_teardown's clean-exit branch BEFORE destroy_machine,
# so a failure here means we keep the machine running rather than
# destroying work-in-progress.
#
# Requires: LEERIE_MACHINE_ID, USER_REPO, FLY_APP in scope (already set
# by the time decide_teardown runs, since provision_machine populates
# them).
_try_fetch_branch_for_teardown() {
  # LEERIE_REPO (set by the launcher) or LEERIE_HOME (set by some callers
  # for compat) points at the leerie install dir. Fall back to deriving
  # it from this file's location if neither is set (e.g. provision.sh
  # sourced standalone in a test).
  local _leerie_dir="${LEERIE_REPO:-${LEERIE_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}}"
  if [ ! -f "$_leerie_dir/scripts/remote/fetch-branch.sh" ]; then
    echo "leerie: _try_fetch_branch_for_teardown: fetch-branch.sh missing at $_leerie_dir" >&2
    return 1
  fi
  # shellcheck disable=SC1091
  . "$_leerie_dir/scripts/remote/fetch-branch.sh"
  if ! fetch_branch; then
    return 1
  fi
  return 0
}

# --- decide_teardown (registered as EXIT/INT/TERM trap) ------------------
# Classifies $LEERIE_REMOTE_EXIT_RC (set by the launcher just before exit)
# and dispatches to stop_machine (pause-on-failure) or destroy_machine.
# Classification table is documented in DESIGN §6 Remote pause-on-failure.
#
# Clean-exit branch (rc=0/10/75): syncs run state to the host via
# _try_fetch_branch_for_teardown BEFORE destroying the machine. If
# sync fails, leaves machine running so the user can recover.
#
# Pause branch (other non-zero): writes paused_at + pause_reason to
# the run sidecar so the resume path can find the machine later.
#
# Idempotent: the trap fires on every exit, including success; the
# stop/destroy primitives no-op on an empty LEERIE_MACHINE_ID.
decide_teardown() {
  local rc="${LEERIE_REMOTE_EXIT_RC:-0}"
  local mid="$LEERIE_MACHINE_ID"
  if [ -z "$mid" ]; then
    return 0
  fi
  case "$rc" in
    0|10|75)
      # Genuine terminal exits of the *run*:
      #   0   — orchestrator finished cleanly (the tail wrapper detected
      #         orchestrator-pid exit and printed the finalize hint).
      #   10  — EXIT_NEEDS_ANSWERS (plugin re-run).
      #   75  — EX_TEMPFAIL (rate-limit, parse-fail).
      #
      # SAFETY-CRITICAL: pull the run branch + state dir to the host
      # BEFORE destroying the machine. If we destroy first and then
      # try to fetch, the user has paid for LLM work that is now
      # unrecoverable. This is a one-way ratchet: machine destruction
      # is gated on confirmed host-side state.
      #
      # On sync failure we leave the machine RUNNING (not stopped) so
      # the user can investigate without first having to start a
      # paused machine. They explicitly destroy via `leerie --kill`
      # when they've recovered the work.
      if _try_fetch_branch_for_teardown; then
        echo "[leerie] remote: run branch + state synced to host" >&2
        if [ -n "${LEERIE_REMOTE_RUN_ID:-}" ]; then
          echo "[leerie] remote: run 'leerie --finalize $LEERIE_REMOTE_RUN_ID' to push and open a PR" >&2
        fi
        destroy_machine
      else
        local sync_reason="sync-failed-on-clean-exit"
        local sidecar=""
        if [ -n "${USER_REPO:-}" ] && [ -n "${LEERIE_RUN_ID:-}" ]; then
          sidecar="$USER_REPO/.leerie/runs/$LEERIE_RUN_ID/run.json"
        fi
        if [ -n "$sidecar" ] && [ -f "$sidecar" ]; then
          update_run_json "$sidecar" \
            sync_failed_at "$(iso_now)" \
            sync_fail_reason "$sync_reason" \
            fly_machine_id "$mid" || true
        fi
        echo "" >&2
        echo "================================================================" >&2
        echo "leerie: WARNING — sync from machine to host FAILED." >&2
        echo "  The orchestrator finished cleanly but the run branch + state" >&2
        echo "  could not be pulled back. The machine is being LEFT RUNNING" >&2
        echo "  so your work is not lost. Recover manually:" >&2
        echo "" >&2
        echo "    1. Investigate / retry sync:" >&2
        echo "         leerie --finalize ${LEERIE_RUN_ID:-<run-id>}" >&2
        echo "       (this calls fetch_branch + host push; safe to retry)" >&2
        echo "" >&2
        echo "    2. Or attach + inspect manually:" >&2
        echo "         leerie --attach ${LEERIE_RUN_ID:-<run-id>}" >&2
        echo "" >&2
        echo "    3. When your work is safely on the host, destroy the" >&2
        echo "       machine:" >&2
        echo "         leerie --kill ${LEERIE_RUN_ID:-<run-id>}" >&2
        echo "" >&2
        echo "  Machine: $mid (still running on Fly)" >&2
        echo "================================================================" >&2
        # Intentionally NO stop_machine, NO destroy_machine. The user
        # owns this machine until they explicitly --kill it.
      fi
      ;;
    130|143)
      # Host-side SIGINT (130) / SIGTERM (143). With the detached
      # orchestrator (DESIGN §6 *Detached orchestrator (remote mode)*),
      # these signals reach the *tail wrapper* on the host, not the
      # orchestrator. The orchestrator is still running on the machine.
      # Leave the machine alone and print reattach hints.
      echo "" >&2
      echo "[leerie] detached from run ${LEERIE_RUN_ID:-<unknown>} (machine $mid still running)" >&2
      if [ -n "${LEERIE_RUN_ID:-}" ]; then
        echo "       reattach:  leerie --attach $LEERIE_RUN_ID --tail" >&2
        echo "       pause:     leerie --stop $LEERIE_RUN_ID" >&2
        echo "       destroy:   leerie --kill $LEERIE_RUN_ID" >&2
      else
        echo "       reattach:  leerie --attach <run-id> --tail" >&2
        echo "       (run-id was not exported; check leerie --list for the active machine)" >&2
      fi
      # Intentionally no stop/destroy — the orchestrator must keep running.
      ;;
    *)
      # Unknown non-zero: pause. Stop the machine (preserves filesystem on
      # the Fly volume) and surface the failure to the user via the run
      # sidecar.
      local reason="${LEERIE_PAUSE_REASON:-worker-error}"
      local sidecar=""
      if [ -n "${USER_REPO:-}" ] && [ -n "${LEERIE_RUN_ID:-}" ]; then
        sidecar="$USER_REPO/.leerie/runs/$LEERIE_RUN_ID/run.json"
      fi
      if [ -n "$sidecar" ] && [ -f "$sidecar" ]; then
        update_run_json "$sidecar" \
          paused_at "$(iso_now)" \
          pause_reason "$reason" \
          fly_machine_id "$mid" || true
      fi
      stop_machine
      echo "" >&2
      echo "[leerie] PAUSED: machine $mid (rc=$rc, reason=$reason)" >&2
      if [ -n "${LEERIE_RUN_ID:-}" ]; then
        echo "  run-id:  $LEERIE_RUN_ID" >&2
        echo "  resume:  leerie --resume --run-id $LEERIE_RUN_ID --runtime fly" >&2
      fi
      echo "  attach:  leerie --attach ${LEERIE_RUN_ID:-<run-id>} --tail" >&2
      echo "  kill:    leerie --kill ${LEERIE_RUN_ID:-<run-id>}" >&2
      if [ -n "${LEERIE_PAUSE_NOTIFY_CMD:-}" ]; then
        eval "$LEERIE_PAUSE_NOTIFY_CMD" || true
      fi
      # Don't clear LEERIE_MACHINE_ID — leave the pointer for the user.
      ;;
  esac
}

# --- wait for machine to reach state "started" ---------------------------
# flyctl machine status does NOT accept --json (same caveat as
# `flyctl machine run` — see comment block in provision_machine). Parse
# the text output instead. The output begins with lines like:
#   Machine ID: <id>
#   Instance ID: <iid>
#   State: <state>
# We extract "State: " case-insensitively from the prefix-aligned format
# (note: lower in the output there's also a table with "State │ <state>"
# in box-drawing characters — we match the first standalone "State:" line).
wait_for_started() {
  local mid="$1"
  local deadline=$(( $(date +%s) + MACHINE_START_TIMEOUT ))
  local state=""
  echo "[leerie] remote: waiting for machine $mid to start (timeout: ${MACHINE_START_TIMEOUT}s)..." >&2
  while true; do
    state="$(flyctl machine status "$mid" \
               --app "$FLY_APP" 2>/dev/null \
             | sed 's/\x1b\[[0-9;]*m//g' \
             | awk -F': *' '/^State: / { print $2; exit }' \
             | tr -d '[:space:]' || true)"
    case "$state" in
      started)
        echo "[leerie] remote: machine $mid is started" >&2
        return 0
        ;;
      failed|stopped|destroyed|replacing)
        echo "leerie: machine $mid entered state '$state' — cannot proceed" >&2
        return 1
        ;;
    esac
    if [ "$(date +%s)" -ge "$deadline" ]; then
      echo "leerie: timed out waiting for machine $mid to start (${MACHINE_START_TIMEOUT}s)" >&2
      return 1
    fi
    sleep 2
  done
}

# --- provision_machine ---------------------------------------------------
# Creates a Fly Machine from $FLY_IMAGE_TAG, registers the destroy trap,
# and blocks until the machine reaches state "started".
# Requires: $FLY_IMAGE_TAG set by the caller.
# Exports:  $LEERIE_MACHINE_ID
# Returns:  0 on success; 1 on failure (machine is destroyed before returning).
provision_machine() {
  if [ -z "${FLY_IMAGE_TAG:-}" ]; then
    echo "leerie: FLY_IMAGE_TAG is not set — cannot start a Fly Machine" >&2
    echo "  Build and push the leerie image first:" >&2
    echo "    ./scripts/remote/build-push.sh --app $FLY_APP --push" >&2
    return 1
  fi

  require_flyctl || return 1

  echo "[leerie] remote: creating machine (app=$FLY_APP region=$FLY_REGION image=$FLY_IMAGE_TAG)..." >&2

  # flyctl machine run --detach starts the machine without streaming its
  # output. Note: flyctl machine run does NOT accept --json (only some
  # other subcommands do — `flyctl machine status --json` for example).
  # The text output contains a line like "Machine ID: <id>" which we
  # parse via awk. Defensively initialize machine_id="" so any future
  # parser failure doesn't trigger set -u at the empty-check below.
  local create_output=""
  local machine_id=""
  if create_output="$(flyctl machine run "$FLY_IMAGE_TAG" \
       --app "$FLY_APP" \
       --region "$FLY_REGION" \
       --vm-cpus "$FLY_VM_CPUS" \
       --vm-memory "$FLY_VM_MEMORY" \
       --detach \
       2>&1)"; then
    # Extract the first whitespace-delimited token after "Machine ID:".
    # Tolerant of ANSI color codes by stripping ESC[<...>m sequences first.
    machine_id="$(printf '%s' "$create_output" \
                  | sed 's/\x1b\[[0-9;]*m//g' \
                  | awk '/Machine ID:/ { for (i=1; i<=NF; i++) if ($i == "ID:") { print $(i+1); exit } }')"
  fi

  if [ -z "$machine_id" ]; then
    echo "leerie: failed to create Fly Machine — flyctl output:" >&2
    printf '  %s\n' "$create_output" >&2
    return 1
  fi

  echo "[leerie] remote: created machine $machine_id" >&2
  LEERIE_MACHINE_ID="$machine_id"
  export LEERIE_MACHINE_ID

  # Register teardown trap immediately after a successful creation so Ctrl-C
  # or any error after this point cannot leak the machine. decide_teardown
  # classifies $LEERIE_REMOTE_EXIT_RC and dispatches to stop or destroy.
  # shellcheck disable=SC2064
  trap 'decide_teardown' EXIT INT TERM

  # Persist fly_machine_id to the run sidecar immediately so a launcher
  # crash before classification still leaves a recoverable pointer.
  # DESIGN §6 Remote pause-on-failure: the sidecar is the source of truth
  # for what's recoverable; the env-var-only path of older revisions
  # leaks machines on launcher crash.
  if [ -n "${USER_REPO:-}" ] && [ -n "${LEERIE_RUN_ID:-}" ]; then
    local sidecar="$USER_REPO/.leerie/runs/$LEERIE_RUN_ID/run.json"
    if [ -f "$sidecar" ]; then
      update_run_json "$sidecar" fly_machine_id "$machine_id" || true
    fi
  fi

  # PID-keyed pointer for `leerie --attach` (no run-id available yet on
  # fresh runs because the orchestrator hasn't minted one). The file is
  # under $USER_REPO/.leerie/remote/<launcher-pid>.json and is removed by
  # destroy_machine on teardown. The launcher renames it to
  # .leerie/runs/<run-id>/fly-machine.json after fetch-branch.sh runs.
  # (Phase 3: PTY-over-SSH attach.)
  if [ -n "${USER_REPO:-}" ]; then
    local remote_dir="$USER_REPO/.leerie/remote"
    mkdir -p "$remote_dir"
    local pid_record="$remote_dir/$$.json"
    # Record the USER's launch-time --no-push intent here so the host's
    # `leerie --finalize` step can distinguish "user opted out of pushing"
    # from "the in-Fly orchestrator was told not to push because it
    # can't reach github" (the latter is a mechanism flag the launcher
    # forces, NOT a user-intent flag).
    python3 - "$pid_record" "$machine_id" "$FLY_APP" "${LEERIE_RUN_ID:-}" "$$" "${NO_PUSH:-false}" <<'PY'
import json, sys, datetime
path, mid, app, run_id, pid, no_push = sys.argv[1:]
data = {
    "fly_app": app,
    "fly_machine_id": mid,
    "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "run_id": run_id or None,
    "launcher_pid": int(pid),
    "host_no_push": no_push in ("true", "1", "yes"),
}
with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
  fi

  # Wait until the machine is reachable.
  if ! wait_for_started "$machine_id"; then
    # decide_teardown will fire via the EXIT trap as this function returns 1.
    # The non-zero rc the caller sets will route to destroy (not pause)
    # because a machine that never started has no useful state to inspect.
    return 1
  fi

  return 0
}
