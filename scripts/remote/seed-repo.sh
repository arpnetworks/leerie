#!/usr/bin/env bash
# scripts/remote/seed-repo.sh — seed the developer's working tree into a
# Fly.io Machine for one pila remote run.
#
# Single-channel seeding: tar the host's working tree (including .git
# and any uncommitted/untracked files) and pipe it to /work on the
# remote via `flyctl ssh console -C "tar -xC /work"`. The same
# transport is used for the Claude config seed (~640 MB) so the
# scale is well-validated.
#
# This replaces an older two-channel design that ran `git clone
# --filter=blob:none` from origin inside the machine and then
# rsync'd the dirty delta separately. The clone path required SSH
# keys / known_hosts on the Fly machine for the git remote — which
# pila intentionally does not deploy (DESIGN §6 *Finalization*:
# workers commit on the machine, the host pushes via
# `pila --finalize`; no long-lived push tokens on Fly). Tar-piping
# from the host removes that requirement entirely: the laptop
# already has the full repo, including `.git`, including
# uncommitted files.
#
# After seeding, /work on the machine mirrors the developer's working
# tree: same tracked files, same uncommitted edits, same untracked
# files, full git history.
#
# Usage (called by the pila launcher after provision_machine succeeds):
#
#   source scripts/remote/seed-repo.sh
#   seed_repo         # blocks until seeding is complete
#
# Environment variables consumed:
#
#   PILA_MACHINE_ID   — ID of the started Fly Machine (set by provision.sh)
#   PILA_FLY_APP      — Fly.io app name (default: "pila")
#   USER_REPO         — absolute path to the local git repo (set by launcher)
#   PILA_GIT_REMOTE   — kept for backward compat (unused by the tar-pipe path)
#
# Requires: flyctl on PATH and authenticated; tar.

set -euo pipefail

FLY_APP="${PILA_FLY_APP:-pila}"
GIT_REMOTE="${PILA_GIT_REMOTE:-origin}"

# ---------------------------------------------------------------------------
# machine_exec <cmd>...
#
# Run a command on the Fly Machine via `flyctl machine exec`.
# Streams stdout/stderr to the caller's stderr for visibility.
# ---------------------------------------------------------------------------
machine_exec() {
  # Current flyctl `machine exec` accepts only a single command-string
  # arg (post-`--` argv was removed). Shell-quote the argv and pipe
  # through ssh console -C, which forwards both stdin and exit code.
  local cmd
  cmd="$(python3 -c '
import shlex, sys
print(" ".join(shlex.quote(a) for a in sys.argv[1:]))
' "$@")"
  flyctl ssh console --app "$FLY_APP" --machine "$PILA_MACHINE_ID" \
    --pty=false -C "$cmd"
}

# ---------------------------------------------------------------------------
# _seed_repo_preflight
#
# Common validation for both seed_repo_clone and seed_repo_dirty. Returns 0
# when all required env vars and binaries are present; 1 with an actionable
# stderr message otherwise.
# ---------------------------------------------------------------------------
_seed_repo_preflight() {
  if [ -z "${PILA_MACHINE_ID:-}" ]; then
    echo "pila: seed_repo: PILA_MACHINE_ID is not set" >&2
    return 1
  fi
  if [ -z "${USER_REPO:-}" ]; then
    echo "pila: seed_repo: USER_REPO is not set" >&2
    return 1
  fi
  # flyctl presence + auth via the shared helper from lib.sh. The launcher's
  # RUNTIME=fly preflight already calls require_flyctl; this is belt-and-
  # braces for callers that source seed-repo.sh standalone.
  if ! command -v require_flyctl >/dev/null 2>&1; then
    if ! command -v flyctl >/dev/null 2>&1; then
      echo "pila: seed_repo: flyctl not found on PATH" >&2
      return 1
    fi
  else
    require_flyctl || return 1
  fi
}

# ---------------------------------------------------------------------------
# seed_repo_clone
#
# Tar-pipe the host's working tree (including .git, including any
# uncommitted/untracked files) to /work on the remote. Always wipes
# /work first — call this only on a fresh provision, never on resume.
#
# This replaces the old `git clone --filter=blob:none` from origin
# inside the machine, which required SSH keys + known_hosts for the
# git remote that pila deliberately does not deploy to Fly (DESIGN §6
# *Finalization*: no long-lived push tokens on the machine).
#
# The host has the entire repo on disk; piping it up via the same
# ssh-console transport already proven for the 640 MB Claude config
# seed is faster than a re-clone over the public internet for any
# repo small enough to fit on a developer laptop. .git includes the
# full object database, so worktrees on the machine work normally.
# ---------------------------------------------------------------------------
seed_repo_clone() {
  _seed_repo_preflight || return 1

  # Ensure SSH cert is valid and hallpass is ready before the tar
  # pipe. Both helpers are no-ops when called against an already-
  # warm machine, so the cost is one fast probe.
  if command -v require_fly_ssh >/dev/null 2>&1; then
    if ! require_fly_ssh "$FLY_APP"; then
      echo "pila: seed_repo: Fly SSH setup failed; cannot seed repo" >&2
      return 1
    fi
  fi
  if command -v wait_for_fly_ssh_ready >/dev/null 2>&1; then
    wait_for_fly_ssh_ready "$FLY_APP" "$PILA_MACHINE_ID" || true
  fi

  echo "[pila] remote: seeding — tar-piping $USER_REPO (full tree + .git) to /work ..." >&2

  # Empty /work's CONTENTS but preserve the directory inode. A bare
  # `rm -rf /work && mkdir -p /work` replaces the inode, which leaves
  # any process whose cwd was /work (e.g. the ssh-console shell, the
  # detached orchestrator we'll launch later) holding a stale fd and
  # causes getcwd() to fail downstream. Common symptom: `shell-init:
  # error retrieving current directory` from sub-shells, and claude
  # --version timing out (its node runtime tries to stat ".").
  #
  # find -delete on /work/* preserves the /work inode itself.
  if ! flyctl ssh console --app "$FLY_APP" --machine "$PILA_MACHINE_ID" \
         --pty=false -C "sh -c 'find /work -mindepth 1 -maxdepth 1 -exec rm -rf {} + && chown pila: /work'" >/dev/null 2>&1; then
    echo "pila: seed_repo: failed to reset /work on machine $PILA_MACHINE_ID" >&2
    return 1
  fi

  # Build the seed file list:
  #   1. Tracked + untracked-not-ignored (git ls-files), filtered to
  #      drop any .pila/ entries even if the user's .gitignore lacks
  #      them. .pila/ is host-side run state; the machine must not
  #      see prior runs.
  #   2. .claude/ verbatim (force-include even if .gitignore'd —
  #      most repo-level .gitignore files list .claude/, but workers
  #      need the repo's hooks/settings/plugins to run).
  #   3. .git/ verbatim (workers need full history for worktrees).
  #
  # The pipeline was verified end-to-end against a fixture repo with
  # tracked + untracked + gitignored + .pila/ + .claude/ + .git/.
  # Output extracted contained exactly the expected paths and
  # `git log` worked on the extracted copy.
  #
  # COPYFILE_DISABLE=1 silences GNU tar's "Ignoring unknown extended
  # header keyword 'LIBARCHIVE.xattr.com.apple.provenance'" warnings
  # on the remote when the host is macOS. No-op on Linux.
  #
  # Wrap the pipeline in a single attempt + one retry after `flyctl
  # agent restart` if the failure matches the transient "tunnel
  # unavailable" pattern. Observed on cold-start probes: a fresh
  # flyctl agent occasionally returns "tunnel unavailable" within
  # ~7s; restarting the agent reliably clears it.
  local tar_rc=0 attempt err_log
  for attempt in 1 2; do
    err_log="$(mktemp)"
    {
      ( cd "$USER_REPO" && \
        git ls-files -z --cached --others --exclude-standard \
          | python3 -c '
import sys
for f in sys.stdin.buffer.read().split(b"\x00"):
    if not f or f.startswith(b".pila/") or f == b".pila":
        continue
    sys.stdout.buffer.write(f + b"\x00")
' )
      if [ -d "$USER_REPO/.claude" ]; then
        ( cd "$USER_REPO" && find .claude -print0 )
      fi
      if [ -d "$USER_REPO/.git" ]; then
        ( cd "$USER_REPO" && find .git -print0 )
      fi
    } \
      | COPYFILE_DISABLE=1 tar -C "$USER_REPO" --null -T - -cf - 2>/dev/null \
      | flyctl ssh console --app "$FLY_APP" --machine "$PILA_MACHINE_ID" \
          --pty=false -C "sh -c 'tar -xC /work && chown -R pila: /work'" >/dev/null 2>"$err_log"
    tar_rc=${PIPESTATUS[2]}
    if [ "$tar_rc" -eq 0 ]; then
      rm -f "$err_log"
      break
    fi
    if [ "$attempt" -eq 1 ] \
       && grep -qE "tunnel unavailable|context deadline exceeded|i/o timeout" "$err_log"; then
      cat "$err_log" >&2
      echo "[pila] remote: tunnel unavailable; restarting flyctl agent and retrying once..." >&2
      flyctl agent restart >/dev/null 2>&1 || true
      sleep 2
      rm -f "$err_log"
      continue
    fi
    cat "$err_log" >&2
    rm -f "$err_log"
    break
  done

  if [ "$tar_rc" -ne 0 ]; then
    echo "pila: seed_repo: tar transfer to /work failed (exit $tar_rc)" >&2
    return 1
  fi

  echo "[pila] remote: repo seeded to /work" >&2
}

# ---------------------------------------------------------------------------
# seed_repo_dirty
#
# Re-seed helper used by `scripts/remote/re-seed.sh` (Phase 4) when the
# user pauses a run, edits files locally, and resumes. Tars the host's
# `git status --porcelain` dirty set and streams it into /work on the
# remote. NOT called by `seed_repo()` on a fresh provision anymore —
# `seed_repo_clone` already includes uncommitted files via
# `git ls-files --others --exclude-standard`.
#
# Defensive excludes (.pila/runs/*/worktrees/* and .git/*) protect against
# a future change that lets the dirty set name worktree paths — currently
# the host can't produce those paths because worktrees live only on the
# machine, but the safety belt prevents silent clobbering.
# ---------------------------------------------------------------------------
seed_repo_dirty() {
  _seed_repo_preflight || return 1

  # Compute the dirty set: modified tracked files + untracked files,
  # excluding git-ignored entries.
  local dirty_files
  dirty_files="$(git -C "$USER_REPO" status --porcelain 2>/dev/null \
                  | awk '
                      # Untracked files (including untracked dirs — trailing /)
                      /^\?\? / {
                        f = substr($0, 4)
                        gsub(/\/$/, "", f)
                        print f
                        next
                      }
                      # Modified/deleted/renamed/copied in worktree (column 2)
                      length($0) >= 2 && substr($0,2,1) != " " {
                        f = substr($0, 4)
                        if (index(f, " -> ")) {
                          f = substr(f, index(f, " -> ") + 4)
                        }
                        gsub(/\/$/, "", f)
                        print f
                      }
                  ')"

  if [ -z "$dirty_files" ]; then
    echo "[pila] remote: seeding — working tree is clean; no delta to sync" >&2
    return 0
  fi

  local file_count
  file_count="$(printf '%s\n' "$dirty_files" | wc -l | tr -d ' ')"
  echo "[pila] remote: seeding — syncing $file_count dirty file(s)/dir(s)..." >&2

  # Defensive --exclude flags: structural protection in case a future
  # change lets host-side dirty paths cross the boundary.
  #
  # Current flyctl removed `--stdin` from `machine exec`. Use
  # `flyctl ssh console -C` instead — it forwards host stdin to the
  # remote command and handles arbitrarily large payloads.
  # Defensive: see comment in seed-auth.sh for require_fly_ssh.
  if command -v require_fly_ssh >/dev/null 2>&1; then
    if ! require_fly_ssh "$FLY_APP"; then
      echo "pila: seed_repo: Fly SSH setup failed; cannot transfer delta" >&2
      return 1
    fi
  fi
  if command -v wait_for_fly_ssh_ready >/dev/null 2>&1; then
    wait_for_fly_ssh_ready "$FLY_APP" "$PILA_MACHINE_ID" || true
  fi
  local tar_rc=0
  {
    printf '%s\n' "$dirty_files" \
      | while IFS= read -r f; do printf '%s\0' "$f"; done \
      | COPYFILE_DISABLE=1 tar -C "$USER_REPO" \
            --exclude='.pila/runs/*/worktrees/*' \
            --exclude='.git/*' \
            --null -T - \
            -czf - 2>/dev/null
  } | flyctl ssh console \
        --app "$FLY_APP" \
        --machine "$PILA_MACHINE_ID" \
        --pty=false \
        -C "tar -C /work -xzf -" >/dev/null 2>&1 || tar_rc=$?

  if [ "$tar_rc" -ne 0 ]; then
    echo "pila: seed_repo: tar delta transfer failed (exit $tar_rc)" >&2
    return 1
  fi

  echo "[pila] remote: seeding complete" >&2
}

# ---------------------------------------------------------------------------
# seed_repo
#
# Used on fresh provisions. seed_repo_clone now tar-pipes the entire
# working tree (including uncommitted files) so the dirty-rsync that
# used to follow is redundant here. re-seed.sh still calls
# seed_repo_dirty directly when the user pauses + edits + resumes.
# ---------------------------------------------------------------------------
seed_repo() {
  seed_repo_clone
}
