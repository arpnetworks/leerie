#!/usr/bin/env bash
# Tiny shared helper for timestamped, repo-tagged stderr logs.
# Sourced by lib.sh (for all host-side remote scripts) and directly by
# seed-auth.sh and fetch-branch.sh (whose standalone-test sourcing path
# doesn't go through lib.sh, and which want this helper without the rest
# of lib.sh's surface in scope).
#
# Format: <ISO-8601 seconds + ±HH:MM offset> [leerie] [<repo>] <msg>
# e.g.    2026-06-03T05:07:10-05:00 [leerie] [stackpulse] hello
# Repo derives from $USER_REPO (basename); falls back to "?" if unset.
# The `sed` fixes up BSD `date` output (`-0500`) to ISO-8601's `-05:00`
# — GNU `%:z` is not portable to the macOS launcher host.
remote_log() {
  local _repo _ts
  _repo="$(basename "${USER_REPO:-?}")"
  _ts="$(date +%FT%T%z | sed 's/\(..\)$/:\1/')"
  printf '%s [leerie] [%s] %s\n' "$_ts" "$_repo" "$*" >&2
}
