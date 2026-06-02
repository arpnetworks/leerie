#!/usr/bin/env bash
# Tiny shared helper for timestamped, repo-tagged stderr logs.
# Sourced by lib.sh (for all host-side remote scripts) and directly by
# seed-auth.sh and fetch-branch.sh (whose standalone-test sourcing path
# doesn't go through lib.sh, and which want this helper without the rest
# of lib.sh's surface in scope).
#
# Format: [leerie HH:MM:SS] [<repo>] <msg>
# Repo derives from $USER_REPO (basename); falls back to "?" if unset.
remote_log() {
  local _repo
  _repo="$(basename "${USER_REPO:-?}")"
  printf '[leerie %s] [%s] %s\n' "$(date +%H:%M:%S)" "$_repo" "$*" >&2
}
