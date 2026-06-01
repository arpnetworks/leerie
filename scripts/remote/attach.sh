#!/usr/bin/env bash
# scripts/remote/attach.sh — open a PTY into a running or paused Fly Machine.
#
# Phase 3: realizes the PTY-over-SSH attach channel from
# remote-task-system.md lines 22–33. Uses `flyctl ssh console` which routes
# through Fly's hallpass + WireGuard mesh — no sshd in the image, no key
# management, no public exposure. Auth inherits from `flyctl auth status`,
# which the launcher already requires for the RUNTIME=fly path.
#
# Usage (invoked via `pila --attach [<run-id>] [--tail] [--app <app>]`):
#
#   pila --attach my-run-abc           # land in bash at /work
#   pila --attach my-run-abc --tail    # tail the orchestrator log instead
#   pila --attach                      # resolve from .pila/remote/ (single active record)
#
# Resolution rules:
#   1. If <run-id> is given, look up .pila/runs/<run-id>/fly-machine.json
#      (written by the launcher post-fetch_branch when a remote run
#      completes) or .pila/runs/<run-id>/run.json (Phase 2 sidecar, which
#      carries `fly_machine_id`).
#   2. If <run-id> is absent and exactly one active record exists under
#      .pila/remote/*.json, use it.
#   3. Multiple active records → print the list and exit 1.
#   4. No records → exit 1 with "no active remote machine".
#
# Security: Fly Machines are reachable only via the Fly org's WireGuard
# mesh. No public ports are opened. The user attaching must have the same
# `flyctl auth` that launched the run.

set -euo pipefail

_ATTACH_USAGE='Usage: pila --attach [<run-id>] [--tail] [--auto-finalize] [--all-logs] [--app <app>]'

# --- arg parsing ---------------------------------------------------------
ATTACH_RUN_ID=""
ATTACH_TAIL=false
ATTACH_AUTO_FINALIZE=false
ATTACH_ALL_LOGS=false
ATTACH_APP="${PILA_FLY_APP:-pila}"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --tail)            ATTACH_TAIL=true; shift ;;
    --auto-finalize)   ATTACH_AUTO_FINALIZE=true; shift ;;
    --all-logs)        ATTACH_ALL_LOGS=true; shift ;;
    --app)             ATTACH_APP="$2"; shift 2 ;;
    --app=*)           ATTACH_APP="${1#--app=}"; shift ;;
    --help|-h)         echo "$_ATTACH_USAGE" >&2; exit 0 ;;
    --*)
      echo "attach: unknown flag: $1" >&2
      echo "$_ATTACH_USAGE" >&2
      exit 1
      ;;
    *)
      if [ -z "$ATTACH_RUN_ID" ]; then
        ATTACH_RUN_ID="$1"; shift
      else
        echo "attach: unexpected argument: $1" >&2
        exit 1
      fi
      ;;
  esac
done

# --- resolve repo root ---------------------------------------------------
# USER_REPO is set by the launcher; fall back to PWD if invoked standalone.
USER_REPO="${USER_REPO:-$PWD}"
PILA_DIR="$USER_REPO/.pila"

# --- preflight: flyctl required -----------------------------------------
# Use the shared helper from lib.sh — handles auto-install + auth prompt.
_ATTACH_DIR="$(CDPATH= cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "$_ATTACH_DIR/lib.sh"
require_flyctl || exit 1

# --- resolve machine id -------------------------------------------------
ATTACH_MACHINE_ID=""

# Strategy A: an explicit run-id was given — look in .pila/runs/<id>/.
if [ -n "$ATTACH_RUN_ID" ]; then
  for candidate in \
    "$PILA_DIR/runs/$ATTACH_RUN_ID/fly-machine.json" \
    "$PILA_DIR/runs/$ATTACH_RUN_ID/run.json"; do
    if [ -f "$candidate" ]; then
      ATTACH_MACHINE_ID="$(python3 -c "
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    print(d.get('fly_machine_id') or '')
except Exception:
    pass
" "$candidate" 2>/dev/null || true)"
      [ -n "$ATTACH_MACHINE_ID" ] && break
    fi
  done
fi

# Strategy B: no explicit run-id — scan .pila/remote/ for active records.
# Each record's filename is a launcher PID; treat the record as stale if
# the PID no longer exists.
if [ -z "$ATTACH_MACHINE_ID" ] && [ -z "$ATTACH_RUN_ID" ]; then
  ACTIVE=()
  if [ -d "$PILA_DIR/remote" ]; then
    for f in "$PILA_DIR/remote"/*.json; do
      [ -e "$f" ] || continue
      pid="$(basename "$f" .json)"
      # If the recorded PID is gone, treat as stale and skip.
      if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        ACTIVE+=("$f")
      fi
    done
  fi
  case "${#ACTIVE[@]}" in
    0)
      echo "pila: no active remote machine" >&2
      echo "  No records under $PILA_DIR/remote/ and no <run-id> given." >&2
      echo "  $_ATTACH_USAGE" >&2
      exit 1
      ;;
    1)
      ATTACH_MACHINE_ID="$(python3 -c "
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    print(d.get('fly_machine_id') or '')
except Exception:
    pass
" "${ACTIVE[0]}" 2>/dev/null || true)"
      ;;
    *)
      echo "pila: multiple active remote machines — pass --attach <run-id> to disambiguate:" >&2
      for f in "${ACTIVE[@]}"; do
        python3 -c "
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    print(f\"  pid={d.get('launcher_pid','?')} machine={d.get('fly_machine_id','?')} run={d.get('run_id','?')}\")
except Exception:
    pass
" "$f" >&2 || true
      done
      exit 1
      ;;
  esac
fi

if [ -z "$ATTACH_MACHINE_ID" ]; then
  if [ -n "$ATTACH_RUN_ID" ]; then
    echo "pila: no fly_machine_id recorded for run $ATTACH_RUN_ID" >&2
    echo "  Looked in: $PILA_DIR/runs/$ATTACH_RUN_ID/fly-machine.json" >&2
    echo "             $PILA_DIR/runs/$ATTACH_RUN_ID/run.json" >&2
  else
    echo "pila: could not resolve fly_machine_id" >&2
  fi
  exit 1
fi

# --- build the ssh command ----------------------------------------------
echo "[pila] attach: flyctl ssh console -a $ATTACH_APP --machine $ATTACH_MACHINE_ID" >&2

if [ "$ATTACH_TAIL" = "true" ]; then
  if [ "$ATTACH_ALL_LOGS" = "true" ]; then
    # Per-worker logs (the pre-detach behavior). Useful for inspecting
    # individual implementer/conformer output across the run.
    if [ -z "$ATTACH_RUN_ID" ]; then
      REMOTE_CMD='tail -F /work/.pila/runs/*/logs/*.log 2>/dev/null'
    else
      REMOTE_CMD="tail -F /work/.pila/runs/$ATTACH_RUN_ID/logs/*.log 2>/dev/null"
    fi
    exec flyctl ssh console \
      --app "$ATTACH_APP" \
      --machine "$ATTACH_MACHINE_ID" \
      --command "$REMOTE_CMD"
  fi

  # Default --tail: canonical reattach to orchestrator.log via the shared
  # render_tail_wrapper helper (DESIGN §6 *Detached orchestrator (remote
  # mode)*). Handles the `_bootstrap-<6hex>` → final-id rename
  # transparently via the handover file the orchestrator writes after
  # phase_classify. Also watches orchestrator.pid; when it disappears,
  # prints the finalize hint and exits.
  if [ -z "$ATTACH_RUN_ID" ]; then
    echo "attach: --tail requires a <run-id> (the orchestrator log path is per-run)" >&2
    echo "  Tip: 'pila --list' lists known runs. The detach banner that printed" >&2
    echo "  when you Ctrl-C'd the original launch shows the bootstrap id." >&2
    exit 1
  fi

  TAIL_SCRIPT="$(render_tail_wrapper)"
  AUTO_FINALIZE_ENV=""
  if [ "$ATTACH_AUTO_FINALIZE" = "true" ]; then
    # The wrapper prints "${TOKEN}${final_id}" on its last stderr line
    # when AUTO_FINALIZE_TOKEN is set. We grep for the token in the
    # remote command's stderr to capture the final id, then exec
    # `pila --finalize <id>` on the host (the machine cannot finalize;
    # push + gh auth live host-side). Token is a launcher-pid sentinel
    # so it never collides with run-id text.
    AUTO_FINALIZE_TOKEN="<<PILA_AUTOFIN_$$>>"
    AUTO_FINALIZE_ENV="AUTO_FINALIZE_TOKEN='$AUTO_FINALIZE_TOKEN'; export AUTO_FINALIZE_TOKEN
"
  fi

  # Prefix the wrapper script with PILA_TAIL_RUN_ID=... so the wrapper
  # receives the run-id even though `flyctl ssh console --command` does
  # not pass positional args after `--`. The wrapper consults
  # ${PILA_TAIL_RUN_ID:-$1} so the env var wins.
  RUN_ID_ENV="PILA_TAIL_RUN_ID='$ATTACH_RUN_ID'; export PILA_TAIL_RUN_ID
"

  if [ "$ATTACH_AUTO_FINALIZE" = "true" ]; then
    # Capture stderr through a tee so the user still sees the stream,
    # but we can also grep for the token to drive auto-finalize.
    _stderr_capture="$(mktemp -t pila-attach.XXXXXX)"
    trap 'rm -f "$_stderr_capture"' EXIT
    set +e
    flyctl ssh console \
      --app "$ATTACH_APP" \
      --machine "$ATTACH_MACHINE_ID" \
      --command "${RUN_ID_ENV}${AUTO_FINALIZE_ENV}$TAIL_SCRIPT" \
      2> >(tee "$_stderr_capture" >&2)
    rc=$?
    set -e
    if [ "$rc" -eq 0 ]; then
      final_id="$(grep -oE "${AUTO_FINALIZE_TOKEN}[^ ]+" "$_stderr_capture" 2>/dev/null | tail -1 | sed "s|^${AUTO_FINALIZE_TOKEN}||")"
      if [ -n "$final_id" ]; then
        echo "[pila] auto-finalize: running 'pila --finalize $final_id'" >&2
        # exec back into pila itself. The PILA env vars the original
        # invocation set are still in scope. Use portable cd+pwd to
        # resolve $0's directory (macOS pre-Monterey has no realpath).
        exec "${PILA_REPO:-$(cd -- "$(dirname "$(dirname "$0")")" && pwd -P)}/pila" --finalize "$final_id"
      fi
    fi
    exit "$rc"
  fi

  exec flyctl ssh console \
    --app "$ATTACH_APP" \
    --machine "$ATTACH_MACHINE_ID" \
    --command "${RUN_ID_ENV}$TAIL_SCRIPT"
fi

# Default: bare shell at /work with $PS1 identifying the run-id.
if [ -n "$ATTACH_RUN_ID" ]; then
  REMOTE_CMD="cd /work && PS1='pila@$ATTACH_RUN_ID:\\w\\$ ' exec bash --noprofile --norc -i"
else
  REMOTE_CMD="cd /work && PS1='pila@remote:\\w\\$ ' exec bash --noprofile --norc -i"
fi

exec flyctl ssh console \
  --app "$ATTACH_APP" \
  --machine "$ATTACH_MACHINE_ID" \
  --command "$REMOTE_CMD"
