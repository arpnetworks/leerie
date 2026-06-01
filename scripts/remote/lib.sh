#!/usr/bin/env bash
# scripts/remote/lib.sh — shared helpers for the remote (Fly.io) lifecycle.
#
# Sourced by provision.sh, resume-machine.sh, and (Phase 4) re-seed.sh.
# Pure functions — no global state, no traps. Callers own their own
# lifecycle decisions; this file only provides reusable building blocks.

# --- update_run_json -----------------------------------------------------
# Atomically merge key/value pairs into a run.json sidecar on the host.
#
# Usage:
#   update_run_json "$USER_REPO/.pila/runs/<run-id>/run.json" \
#                   key1 value1 [key2 value2 ...]
#
# Values are treated as strings and JSON-encoded. The merge is read →
# patch → temp-file write → rename, mirroring the orchestrator's
# State.save() + _write_run_json() atomicity contract (DESIGN §6).
#
# Returns 0 on success. Returns 1 (and writes to stderr) if the sidecar
# directory does not exist or the rewrite fails.
update_run_json() {
  local sidecar="$1"
  shift
  local dir
  dir="$(dirname "$sidecar")"
  if [ ! -d "$dir" ]; then
    echo "update_run_json: $dir does not exist" >&2
    return 1
  fi
  local tmp
  tmp="$(mktemp "$sidecar.XXXXXX")"
  # Python handles the read+merge+write so we don't reimplement JSON
  # escaping in bash. The trailing args are key/value pairs; odd-count
  # is a programming error.
  if ! python3 - "$sidecar" "$tmp" "$@" <<'PY'
import json, os, sys
sidecar, tmp, *rest = sys.argv[1:]
if len(rest) % 2 != 0:
    print(f"update_run_json: expected even number of key/value args, got {len(rest)}", file=sys.stderr)
    sys.exit(1)
data = {}
if os.path.exists(sidecar):
    try:
        with open(sidecar) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
    except (OSError, ValueError):
        data = {}
for i in range(0, len(rest), 2):
    k, v = rest[i], rest[i+1]
    # Empty string clears the key (sets to null).
    data[k] = None if v == "" else v
with open(tmp, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
  then
    rm -f "$tmp"
    echo "update_run_json: python merge failed for $sidecar" >&2
    return 1
  fi
  mv "$tmp" "$sidecar"
}

# --- iso_now -------------------------------------------------------------
# Emit an ISO-8601 UTC timestamp (sub-second precision). Used as
# paused_at / similar event markers.
iso_now() {
  python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))'
}

# --- render_tail_wrapper -------------------------------------------------
# Emit a POSIX-sh script (to stdout) that:
#   1. If $1 looks like a bootstrap id (`_bootstrap-<hex>`), waits for the
#      orchestrator to rename the run dir, then reads the handover file
#      (`/work/.pila/launcher-<bootstrap>.runid`) for the final id.
#      Otherwise treats $1 as the final id directly.
#   2. Tails the orchestrator log at the final path.
#   3. Watches the orchestrator pid (from orchestrator.pid). When the pid
#      disappears the orchestrator has exited cleanly. The wrapper kills
#      the tail and prints the finalize banner.
#   4. If AUTO_FINALIZE_TOKEN is set in the wrapper's environment, prints
#      that token on the *last* line of stderr instead of (after) the
#      banner; callers can grep for the token to trigger
#      `pila --finalize` automatically. Decoupled from the wrapper itself
#      because exec'ing `pila` back inside the Fly machine is wrong; the
#      auto-finalize step has to run on the host.
#
# Usage (caller):
#   _wrapper="$(render_tail_wrapper)"
#   flyctl machine exec "$MID" --app "$APP" -- \
#     sh -c "$_wrapper" -- "$RUN_ID"
#
# The wrapper is purely shell (POSIX sh, runs in the Fly image's /bin/sh)
# so it stays portable across remote sh implementations (busybox / dash /
# bash). It uses `tail -F` which all of those support.
render_tail_wrapper() {
  cat <<'TAIL_SH'
# Run-id input: prefer the PILA_TAIL_RUN_ID env var (works under
# `flyctl ssh console --command` which discards positional args), fall
# back to $1 (works under `flyctl machine exec ... -- sh -c "..." -- id`).
ID="${PILA_TAIL_RUN_ID:-$1}"
if [ -z "$ID" ]; then
  echo "[pila] remote: render_tail_wrapper got empty run-id (PILA_TAIL_RUN_ID unset and \$1 empty)" >&2
  exit 2
fi
HANDOVER="/work/.pila/launcher-${ID}.runid"

# Wait briefly for the orchestrator to write its log file. Without this,
# `tail -F` against a not-yet-existent file just spins.
LOG="/work/.pila/runs/${ID}/orchestrator.log"
for _ in 1 2 3 4 5 6 7 8 9 10; do
  [ -f "$LOG" ] && break
  sleep 1
done

# If we were given a bootstrap id, the orchestrator will rename the run
# dir at end-of-classify. Tail the bootstrap log; when the bootstrap dir
# disappears, read the handover file for the final id and re-target.
case "$ID" in
  _bootstrap-*)
    ( tail -F "$LOG" 2>/dev/null ) &
    TAIL_PID=$!
    while [ -d "/work/.pila/runs/${ID}" ]; do
      sleep 1
    done
    kill "$TAIL_PID" 2>/dev/null || true
    wait "$TAIL_PID" 2>/dev/null || true
    if [ ! -f "$HANDOVER" ]; then
      echo "[pila] remote: bootstrap dir gone but no handover at $HANDOVER" >&2
      exit 2
    fi
    FINAL="$(head -1 "$HANDOVER" 2>/dev/null)"
    if [ -z "$FINAL" ]; then
      echo "[pila] remote: handover file empty at $HANDOVER" >&2
      exit 2
    fi
    echo "[pila] remote: run-id promoted to ${FINAL}" >&2
    ID="$FINAL"
    LOG="/work/.pila/runs/${ID}/orchestrator.log"
    ;;
esac

PID_FILE="/work/.pila/runs/${ID}/orchestrator.pid"
ORCH_PID="$(head -1 "$PID_FILE" 2>/dev/null)"

( tail -F "$LOG" 2>/dev/null ) &
TAIL_PID=$!

# Watch the orchestrator pid. When it disappears the orchestrator exited.
# If no pid is recorded yet, treat the wrapper as "watch until killed".
if [ -n "$ORCH_PID" ]; then
  while kill -0 "$ORCH_PID" 2>/dev/null; do
    sleep 2
  done
else
  # No pid file. Block on the tail (it will only return if the log is
  # truncated or removed). This is the degenerate case for very-early
  # reattach.
  wait "$TAIL_PID" 2>/dev/null || true
fi

kill "$TAIL_PID" 2>/dev/null || true
wait "$TAIL_PID" 2>/dev/null || true

echo "" >&2
echo "[pila] remote: orchestrator exited — syncing run branch + state to host..." >&2

# Auto-finalize hook: when the calling host sets AUTO_FINALIZE_TOKEN,
# print it as the wrapper's last stderr line. The host-side caller
# greps for the token, captures the final run-id, and exec's
# `pila --finalize <id>` on the host (the machine cannot do it; auth
# lives on the host).
if [ -n "$AUTO_FINALIZE_TOKEN" ]; then
  echo "${AUTO_FINALIZE_TOKEN}${ID}" >&2
fi
TAIL_SH
}

# --- require_flyctl ------------------------------------------------------
# Ensure flyctl is on PATH and authenticated, auto-installing if missing.
#
# Behavior:
#   1. command -v flyctl. If found, skip to step 3.
#   2. If --no-runtime-install / PILA_NO_RUNTIME_INSTALL=1, print install
#      hint and return 1 (preserves the pre-auto-install contract).
#      Otherwise prompt to install via:
#        - macOS: brew install flyctl
#        - Linux: curl -L https://fly.io/install.sh | sh
#                 (also adds ~/.fly/bin to PATH for this shell)
#      If install fails or user declines, return 1.
#   3. flyctl auth status. If unauthenticated, print "flyctl auth login"
#      instructions and (if stdin is a TTY) prompt to run it now.
#      The prompt opens a browser via `flyctl auth login`; on success,
#      auth check is re-run.
#
# Honors:
#   PILA_NO_RUNTIME_INSTALL=1   skip auto-install, fall back to hint+exit
#   PILA_NONINTERACTIVE=1        never prompt; install/auth must already be set up
#
# Idempotent: safe to call multiple times. Returns 0 if flyctl is ready.
require_flyctl() {
  if ! command -v flyctl >/dev/null 2>&1; then
    if [ "${PILA_NO_RUNTIME_INSTALL:-0}" = "1" ] || [ "${PILA_NONINTERACTIVE:-0}" = "1" ]; then
      echo "pila: flyctl not found on PATH." >&2
      echo "  Install from https://fly.io/docs/flyctl/install/" >&2
      echo "  or: brew install flyctl (macOS)" >&2
      return 1
    fi
    if ! _require_flyctl_install; then
      return 1
    fi
    # After install, re-resolve PATH (installers commonly add to ~/.fly/bin).
    if ! command -v flyctl >/dev/null 2>&1; then
      if [ -x "$HOME/.fly/bin/flyctl" ]; then
        export PATH="$HOME/.fly/bin:$PATH"
      fi
    fi
    if ! command -v flyctl >/dev/null 2>&1; then
      echo "pila: flyctl install reported success but binary still not on PATH." >&2
      echo "  Check $HOME/.fly/bin or restart your shell." >&2
      return 1
    fi
  fi
  if ! flyctl auth status >/dev/null 2>&1; then
    if [ "${PILA_NONINTERACTIVE:-0}" = "1" ]; then
      echo "pila: flyctl is not authenticated." >&2
      echo "  Run: flyctl auth login" >&2
      return 1
    fi
    if ! _require_flyctl_login; then
      return 1
    fi
  fi
  return 0
}

# --- require_fly_ssh ------------------------------------------------------
# Ensure the host's SSH agent has a Fly-issued certificate for SSH-based
# file transfer via `flyctl ssh console -C "..." < tar`. Certs expire after
# 24 hours; if missing/expired the SSH attempts hang or error. Pila uses
# SSH for seeding repo+auth into the machine because flyctl removed
# `--stdin` from `machine exec` and the alternative argv-based payload
# transfer hits ARG_MAX on macOS for typical Claude config (~640 MB).
#
# Idempotent: a successful `flyctl ssh console --pty=false -C true
# --machine <non-existent>` against the target app proves the cert is
# valid (returns "no started VMs" with rc=1 but doesn't hang).
#
# This is best-effort: if `flyctl ssh issue` fails (e.g. user is on a
# restricted org), seed-auth will surface the original SSH error.
require_fly_ssh() {
  local fly_app="${1:-$PILA_FLY_APP}"
  local fly_org="${PILA_FLY_ORG:-personal}"
  # Probe: a quick ssh attempt against a non-existent machine. Fly's
  # error is "no started VMs" which means auth succeeded; any other
  # error (hangs, "could not connect to WireGuard", etc.) means we
  # need to issue a fresh cert.
  if echo | timeout 8 flyctl ssh console --app "$fly_app" \
       --machine "probe-nonexistent" --pty=false -C "true" 2>&1 \
     | grep -qE "no started VMs|app.*not.*found"; then
    return 0
  fi
  # If the agent ALREADY has an SSH cert, the probe might have failed
  # for an unrelated reason (transient WireGuard hiccup, Fly API 500
  # during the cert-issuance outage we observed 2026-06-01). Skip
  # the `flyctl ssh issue` step — the existing cert is almost
  # certainly Fly's (regular SSH key authentication doesn't put
  # certs in the agent; only Fly does for this user).
  if ssh-add -l 2>/dev/null | grep -qE "CERT\)"; then
    echo "[pila] remote: ssh-agent has cert(s); skipping issue step" >&2
    return 0
  fi
  echo "[pila] remote: issuing Fly SSH certificate (24h) for org=$fly_org" >&2
  if ! flyctl ssh issue --agent --hours 24 "$fly_org" >/dev/null 2>&1; then
    # Best-effort: if we have ANY ssh-add cert, hope it's a Fly one
    # and let the subsequent ssh console attempt either succeed or
    # surface the real error.
    if ssh-add -l >/dev/null 2>&1; then
      echo "pila: warning: flyctl ssh issue failed (possible Fly API outage); proceeding with existing agent state" >&2
      return 0
    fi
    echo "pila: warning: flyctl ssh issue failed and no ssh-agent cert available; seed-auth may fail" >&2
    return 1
  fi
  return 0
}

# --- wait_for_fly_ssh_ready ----------------------------------------------
# Block until hallpass (Fly's in-machine SSH daemon) is ready to accept
# connections. require_fly_ssh proves the cert is valid; this proves the
# *target machine* will actually answer. A freshly-started machine takes
# 5-30 s for hallpass to come up after `flyctl machine start` reports
# "started", so naively running `ssh console -C "tar -x"` against it
# yields "ssh: handshake failed: EOF".
#
# Strategy: probe with `ssh console --pty=false -C true` against the
# actual machine ID; success exits 0, EOF/connection errors retry.
# Bounded by 60 s total (12 attempts × 5 s sleep).
#
# Usage:
#   wait_for_fly_ssh_ready "$FLY_APP" "$machine_id"
wait_for_fly_ssh_ready() {
  local fly_app="$1"
  local machine_id="$2"
  local attempts=0
  local max_attempts=12
  while [ "$attempts" -lt "$max_attempts" ]; do
    # `</dev/null` is load-bearing: if stdin is a TTY (the normal
    # case when pila is run interactively), flyctl ssh console hangs
    # after the SSH session is established — empirically observed,
    # 11+ minutes without returning. Detaching stdin lets flyctl
    # complete the -C "true" command and exit cleanly in <5 s.
    # `--kill-after=2` ensures `timeout` escalates SIGTERM to
    # SIGKILL after a 2 s grace period; some flyctl code paths
    # ignore SIGTERM while waiting on the WireGuard tunnel.
    if timeout --kill-after=2 10 flyctl ssh console --app "$fly_app" \
         --machine "$machine_id" --pty=false -C "true" \
         </dev/null >/dev/null 2>&1; then
      return 0
    fi
    attempts=$((attempts + 1))
    if [ "$attempts" -lt "$max_attempts" ]; then
      sleep 5
    fi
  done
  echo "pila: warning: machine $machine_id did not accept SSH within 60s" >&2
  return 1
}


# Internal: install flyctl via the OS-appropriate path with user prompt.
_require_flyctl_install() {
  local os
  os="$(uname -s)"
  echo "" >&2
  case "$os" in
    Darwin)
      echo "[pila] flyctl is not installed. Install via:" >&2
      echo "         brew install flyctl" >&2
      printf "       Run it now? [Y/n] " >&2
      local ans
      read -r ans
      case "${ans:-Y}" in
        [Yy]*|"") ;;
        *)
          echo "pila: aborted by user; install flyctl manually and re-run." >&2
          return 1
          ;;
      esac
      if ! command -v brew >/dev/null 2>&1; then
        echo "pila: brew not found. Install Homebrew first: https://brew.sh" >&2
        return 1
      fi
      if ! brew install flyctl; then
        echo "pila: brew install flyctl failed" >&2
        return 1
      fi
      ;;
    Linux)
      echo "[pila] flyctl is not installed. Install via:" >&2
      echo "         curl -L https://fly.io/install.sh | sh" >&2
      printf "       Run it now? [Y/n] " >&2
      local ans
      read -r ans
      case "${ans:-Y}" in
        [Yy]*|"") ;;
        *)
          echo "pila: aborted by user; install flyctl manually and re-run." >&2
          return 1
          ;;
      esac
      if ! curl -L https://fly.io/install.sh | sh; then
        echo "pila: flyctl install script failed" >&2
        return 1
      fi
      ;;
    *)
      echo "pila: don't know how to install flyctl on $os." >&2
      echo "  Install manually from https://fly.io/docs/flyctl/install/" >&2
      return 1
      ;;
  esac
  return 0
}

# Internal: prompt + run flyctl auth login. Opens a browser.
_require_flyctl_login() {
  echo "" >&2
  echo "[pila] flyctl is installed but not authenticated." >&2
  printf "       Run 'flyctl auth login' now (opens browser)? [Y/n] " >&2
  local ans
  read -r ans
  case "${ans:-Y}" in
    [Yy]*|"") ;;
    *)
      echo "pila: aborted by user; run 'flyctl auth login' manually and re-run." >&2
      return 1
      ;;
  esac
  if ! flyctl auth login; then
    echo "pila: flyctl auth login failed" >&2
    return 1
  fi
  if ! flyctl auth status >/dev/null 2>&1; then
    echo "pila: flyctl auth login reported success but auth status still fails." >&2
    return 1
  fi
  return 0
}
