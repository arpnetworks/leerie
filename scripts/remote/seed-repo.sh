#!/usr/bin/env bash
# scripts/remote/seed-repo.sh — seed the developer's working tree into a
# Fly.io Machine for one leerie remote run.
#
# Two-phase seeding:
#
#   1. `seed_repo_clone` — laptop creates `git bundle` for the parent
#      repo and each submodule (recursive); pipes each bundle to the
#      machine via `flyctl ssh console -C "sh -c 'cat > /tmp/...'"`.
#      Machine then `git clone`s from the parent bundle file on local
#      disk, wires each submodule URL to point at its bundle, and runs
#      `git -c protocol.file.allow=always submodule update --recursive`
#      (the protocol-flag is required by git 2.38+ for file://-style
#      URLs, per CVE-2022-39253). Delivers committed state only.
#
#   2. `seed_repo_dirty` — laptop rsync's the dirty/untracked delta
#      (uncommitted edits, untracked-not-ignored files, forced-in
#      `.claude/`) into /work via the existing `fly_rsync_wrapper`
#      from lib.sh. Same helper used by `re-seed.sh` for the Phase 4
#      mid-run re-seed flow. Delivers uncommitted state.
#
# Why bundles instead of a tar pipe or pure rsync:
#   macOS BSD `tar -c` normalizes filenames NFC → NFD when archiving
#   (libarchive behavior; documented). The Linux receiver writes NFD
#   bytes to disk; git's index still holds the NFC bytes (because the
#   index was built on macOS where APFS normalizes at the syscall
#   layer). Result: filenames with `ó`, `ñ`, emoji, etc. show as
#   untracked + missing on the machine even when clean on the host,
#   and any submodule containing such a file flags the parent ` M`.
#   This broke `~/src/enric/api`'s preflight in the live test on
#   2026-06-01.
#
#   Bundles sidestep the problem entirely because the bundle file
#   stores pack-format binary objects (tree entries by raw bytes);
#   the receiving Linux git creates filenames natively on disk from
#   those objects. No filename ever serializes through the transport
#   layer where normalization could intervene. rsync (used for the
#   dirty delta) also preserves filename bytes verbatim.
#
# Why bundle each submodule separately:
#   `git bundle create --all` packs only the host repo's own refs.
#   Submodule objects live in `.git/modules/<sm>/` and are NOT
#   included in the parent's bundle. We bundle each submodule
#   separately, transfer each, and on the machine point each
#   submodule's URL at its bundle file (via `git config
#   submodule.<name>.url`) before submodule update.
#
# Transport is the SAME `flyctl ssh console -C "sh -c 'cat > ...'"`
# pipe leerie uses for the Claude home stage (~234 MB, proven) and the
# reverse direction in `fetch-branch.sh` (which moves bundles
# machine → host). The `sh -c` wrapper is load-bearing: bare
# `-C "cat > /tmp/..."` is parsed by flyctl as if `>` were a `cat`
# argument and fails with `cat: invalid option -- 'c'`.
#
# Fly machines deliberately receive no GitHub credentials (DESIGN §6
# *Finalization*: workers commit on the machine, the host pushes via
# `leerie --finalize`; no long-lived push tokens on Fly). Bundling from
# the host satisfies the no-credentials constraint without an
# in-machine `git clone` against origin.
#
# After seeding, /work on the machine mirrors the developer's working
# tree: same committed state, same uncommitted edits, same untracked
# files, full git history, submodule working trees populated.
#
# Usage (called by the leerie launcher after provision_machine succeeds):
#
#   source scripts/remote/seed-repo.sh
#   seed_repo         # blocks until seeding is complete
#
# Environment variables consumed:
#
#   LEERIE_MACHINE_ID   — ID of the started Fly Machine (set by provision.sh)
#   LEERIE_FLY_APP      — Fly.io app name (default: "leerie")
#   USER_REPO         — absolute path to the local git repo (set by launcher)
#
# Requires (host): flyctl on PATH and authenticated; git; python3;
#                  rsync (for the dirty-delta phase).
# Requires (machine, baked into the image): git; rsync.

set -euo pipefail

# --- shared lib (fly_rsync_wrapper / iso_now / require_flyctl / etc.) -----
_SEED_REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "$_SEED_REPO_DIR/lib.sh"

FLY_APP="${LEERIE_FLY_APP:-leerie}"

# ---------------------------------------------------------------------------
# _seed_repo_preflight
#
# Common validation for both seed_repo_clone and seed_repo_dirty. Returns 0
# when all required env vars and binaries are present; 1 with an actionable
# stderr message otherwise.
# ---------------------------------------------------------------------------
_seed_repo_preflight() {
  if [ -z "${LEERIE_MACHINE_ID:-}" ]; then
    echo "leerie: seed_repo: LEERIE_MACHINE_ID is not set" >&2
    return 1
  fi
  if [ -z "${USER_REPO:-}" ]; then
    echo "leerie: seed_repo: USER_REPO is not set" >&2
    return 1
  fi
  # flyctl presence + auth via the shared helper from lib.sh. The launcher's
  # RUNTIME=fly preflight already calls require_flyctl; this is belt-and-
  # braces for callers that source seed-repo.sh standalone.
  if ! command -v require_flyctl >/dev/null 2>&1; then
    if ! command -v flyctl >/dev/null 2>&1; then
      echo "leerie: seed_repo: flyctl not found on PATH" >&2
      return 1
    fi
  else
    require_flyctl || return 1
  fi
}

# ---------------------------------------------------------------------------
# seed_repo_clone
#
# Bundle the host's committed state (parent + every submodule), pipe
# each bundle to the machine via ssh-console, and have the machine
# clone from those bundle files on its local disk. Always wipes /work
# first — call this only on a fresh provision, never on resume.
#
# Why bundles instead of tar or rsync: the bundle file is pack-format
# binary; tree entries are stored as raw bytes; the receiving Linux
# git materializes filenames natively from those objects. macOS BSD
# tar's NFC→NFD filename normalization (the bug that triggered this
# whole rewrite) doesn't apply because filenames don't transit the
# wire as strings — only commit-hash refs and packed objects do.
# ---------------------------------------------------------------------------
seed_repo_clone() {
  _seed_repo_preflight || return 1

  # Ensure SSH cert is valid and hallpass is ready before the pipe.
  # Both helpers are no-ops when called against an already-warm
  # machine, so the cost is one fast probe.
  if command -v require_fly_ssh >/dev/null 2>&1; then
    if ! require_fly_ssh "$FLY_APP"; then
      echo "leerie: seed_repo: Fly SSH setup failed; cannot seed repo" >&2
      return 1
    fi
  fi
  if command -v wait_for_fly_ssh_ready >/dev/null 2>&1; then
    wait_for_fly_ssh_ready "$FLY_APP" "$LEERIE_MACHINE_ID" || true
  fi

  echo "[leerie] remote: seeding — bundling $USER_REPO (parent + submodules) to /work ..." >&2

  # Empty /work's CONTENTS but preserve the directory inode. A bare
  # `rm -rf /work && mkdir -p /work` replaces the inode, which leaves
  # any process whose cwd was /work (e.g. the ssh-console shell, the
  # detached orchestrator we'll launch later) holding a stale fd and
  # causes getcwd() to fail downstream. Common symptom: `shell-init:
  # error retrieving current directory` from sub-shells, and claude
  # --version timing out (its node runtime tries to stat ".").
  #
  # Also reset the bundle staging dirs in case a prior paused run
  # left them behind.
  if ! flyctl ssh console --app "$FLY_APP" --machine "$LEERIE_MACHINE_ID" \
         --pty=false -C "sh -c 'find /work -mindepth 1 -maxdepth 1 -exec rm -rf {} + && chown leerie: /work && rm -rf /tmp/leerie-seed.bundle /tmp/leerie-subs && mkdir -p /tmp/leerie-subs'" >/dev/null 2>&1; then
    echo "leerie: seed_repo: failed to reset /work on machine $LEERIE_MACHINE_ID" >&2
    return 1
  fi

  # 1. Bundle the parent repo and pipe it to /tmp/leerie-seed.bundle on
  #    the machine. `git bundle create - --all` packs every ref into a
  #    single pack-format binary stream on stdout.
  #
  #    The receiver MUST be wrapped in `sh -c '...'`; without it, the
  #    remote treats `>` as an argument to `cat` rather than a shell
  #    redirect and fails with `cat: invalid option -- 'c'`.
  if ! git -C "$USER_REPO" bundle create - --all 2>/dev/null \
        | flyctl ssh console --quiet --app "$FLY_APP" \
            --machine "$LEERIE_MACHINE_ID" --pty=false \
            -C "sh -c 'cat > /tmp/leerie-seed.bundle'" >/dev/null 2>&1; then
    echo "leerie: seed_repo: failed to pipe parent bundle to machine" >&2
    return 1
  fi

  # 2. Bundle each submodule recursively, pipe each into
  #    /tmp/leerie-subs/<flattened-displaypath>.bundle. The display-path
  #    flattening (`/` → `_`) is applied identically here and in the
  #    machine-side clone script (step 3) so both sides agree on the
  #    filename for nested submodules like `vendor/foo` → `vendor_foo`.
  #
  #    `git submodule foreach --recursive` walks every nested submodule.
  #    Inside the foreach, $displaypath is git's superproject-relative
  #    path. We export host-side env vars the foreach body needs.
  if [ -f "$USER_REPO/.gitmodules" ]; then
    if ! (
      cd "$USER_REPO" && \
      LEERIE_FLY_APP="$FLY_APP" LEERIE_MACHINE_ID="$LEERIE_MACHINE_ID" \
      git submodule --quiet foreach --recursive '
        bn="$(printf %s "$displaypath" | tr / _).bundle"
        # The `-C` arg must be `sh -c "..."` not bare `cat > ...`;
        # without the shell wrapper the remote treats `>` as an arg to
        # `cat`. Single-quote the inner script for the foreach context.
        git bundle create - --all 2>/dev/null \
          | flyctl ssh console --quiet --app "$LEERIE_FLY_APP" \
              --machine "$LEERIE_MACHINE_ID" --pty=false \
              -C "sh -c '\''cat > /tmp/leerie-subs/$bn'\''" >/dev/null 2>&1 \
          || { echo "leerie: seed_repo: failed to pipe submodule $displaypath bundle" >&2; exit 1; }
      '
    ); then
      echo "leerie: seed_repo: submodule bundling failed" >&2
      return 1
    fi
  fi

  # 3. Machine-side: clone from /tmp/leerie-seed.bundle into /work, wire
  #    each submodule's URL to its bundle file (in `.git/config`, NOT
  #    `.gitmodules` — we never modify the committed file), then
  #    submodule update. Finally chown -R leerie: /work so the
  #    orchestrator (which runs as leerie) owns its working tree.
  #
  #    `git clone` against a bundle file path Just Works — git
  #    recognizes the bundle header and treats the file like a remote.
  if ! flyctl ssh console --app "$FLY_APP" --machine "$LEERIE_MACHINE_ID" \
         --pty=false -C 'sh -c '"'"'
set -e
# `protocol.file.allow=always` is required for submodule update to
# accept file://-style local paths (bundle files on disk). Git 2.38+
# blocks `file` by default per CVE-2022-39253. We trust local paths
# because we just put them there.
git clone /tmp/leerie-seed.bundle /work
cd /work
if [ -f .gitmodules ]; then
  git submodule init
  git submodule status | awk "{print \$2}" | while read sm; do
    bn=$(printf %s "$sm" | tr / _).bundle
    if [ -f "/tmp/leerie-subs/$bn" ]; then
      git config "submodule.$sm.url" "/tmp/leerie-subs/$bn"
    fi
  done
  git -c protocol.file.allow=always submodule update --recursive
fi
chown -R leerie: /work
# Clean up the bundle tmpfiles — they served their purpose.
rm -rf /tmp/leerie-seed.bundle /tmp/leerie-subs
'"'" >/dev/null 2>&1; then
    echo "leerie: seed_repo: machine-side clone from bundle failed" >&2
    return 1
  fi

  echo "[leerie] remote: repo seeded to /work" >&2
}

# ---------------------------------------------------------------------------
# seed_repo_dirty
#
# Rsync the dirty/untracked delta from host to /work on the machine.
# Called by both the fresh-provision path (after `seed_repo_clone`
# delivers committed state, this fills in uncommitted edits) AND by
# `scripts/remote/re-seed.sh` (Phase 4) when the user pauses a run,
# edits files locally, and resumes.
#
# The file list, host-side, combines two sources:
#
#   (a) `git status --porcelain` output (modified-but-uncommitted
#       tracked files + untracked-not-ignored files), filtered to drop
#       defensive `.leerie/runs/*/worktrees/*` and `.git/*` entries (the
#       upstream behavior shouldn't surface these today, but the
#       exclude prevents silent clobbering if it ever does).
#
#   (b) Every file under the repo-local `.claude/` directory, force-
#       included even when `.gitignore` excludes it. Most repos list
#       `.claude/` in their gitignore but workers need its hooks,
#       agents, skills, commands, and settings to function. Bundles
#       can't carry gitignored content (only committed state), so this
#       step is where `.claude/` lands on the machine.
#
# Transport: rsync over `flyctl ssh console -C "rsync --server ..."`
# via the `fly_rsync_wrapper` helper in lib.sh. rsync preserves
# filename bytes verbatim (NFC stays NFC on the Linux receiver).
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

  # The dirty set is git status output. But we ALSO need to ship the
  # repo-local `.claude/` directory verbatim, even when it's gitignored
  # (the common case — most repos list `.claude/` in their gitignore).
  # Workers need its hooks/agents/skills/commands to function. The
  # bundle-based seed_repo_clone can't carry it (gitignored content
  # isn't in the bundle); this rsync step is where it lands.
  local claude_files=""
  if [ -d "$USER_REPO/.claude" ]; then
    claude_files="$(cd "$USER_REPO" && find .claude -type f 2>/dev/null)"
  fi

  if [ -z "$dirty_files" ] && [ -z "$claude_files" ]; then
    echo "[leerie] remote: seeding — working tree is clean; no delta to sync" >&2
    return 0
  fi

  # Combined count for the user-facing message (dirty entries +
  # .claude/ files). Count nonempty input lines from both sources.
  local file_count
  file_count="$(printf '%s\n%s\n' "$dirty_files" "$claude_files" \
                 | grep -c -v '^$' || true)"
  echo "[leerie] remote: seeding — syncing $file_count dirty / forced-include file(s)..." >&2

  # rsync the dirty delta. rsync preserves filename bytes verbatim
  # (NFC stays NFC on the Linux receiver), important for the same
  # reason seed_repo_clone uses bundles instead of tar.
  #
  # Defensive: the dirty set comes from `git status --porcelain` which
  # operates on the parent repo. Excluding .leerie/runs/*/worktrees/*
  # and .git/* structurally protects against any future change that
  # lets those paths surface in the porcelain output.
  if command -v require_fly_ssh >/dev/null 2>&1; then
    if ! require_fly_ssh "$FLY_APP"; then
      echo "leerie: seed_repo: Fly SSH setup failed; cannot transfer delta" >&2
      return 1
    fi
  fi
  if command -v wait_for_fly_ssh_ready >/dev/null 2>&1; then
    wait_for_fly_ssh_ready "$FLY_APP" "$LEERIE_MACHINE_ID" || true
  fi

  local rsync_rc=0
  local file_list wrapper
  file_list="$(mktemp -t leerie-reseed-list.XXXXXX)"
  wrapper="$(fly_rsync_wrapper "$FLY_APP")"

  # Build NUL-delimited file list. Two sources concatenated:
  #   (a) git porcelain dirty set, filtered (drop .git/, .leerie/runs/
  #       worktrees, blanks)
  #   (b) repo-local .claude/ files (force-included even if gitignored)
  # The python filter applies to both; .claude/* entries from (b)
  # pass the filter trivially (no .git/ or worktree prefix).
  printf '%s\n%s\n' "$dirty_files" "$claude_files" \
    | python3 -c '
import sys
for line in sys.stdin.read().splitlines():
    if not line:
        continue
    # .git/ and .leerie/ are coordination state, never transported here.
    # .git/ → bundle path creates it natively on the machine.
    # .leerie/ → host-side run state; the machine writes its own.
    if line.startswith(".git/") or line == ".git":
        continue
    if line.startswith(".leerie/") or line == ".leerie":
        continue
    # Defensive: drop worktree paths if they ever surface.
    if "/.leerie/runs/" in line and "/worktrees/" in line:
        continue
    sys.stdout.buffer.write(line.encode() + b"\x00")
' > "$file_list"

  LEERIE_FLY_APP="$FLY_APP" rsync -a -H \
    --from0 --files-from="$file_list" \
    -e "$wrapper" \
    "$USER_REPO/" "$LEERIE_MACHINE_ID:/work/" \
    >/dev/null 2>&1
  rsync_rc=$?

  if [ "$rsync_rc" -ne 0 ]; then
    rm -f "$file_list" "$wrapper"
    echo "leerie: seed_repo: rsync delta transfer failed (exit $rsync_rc)" >&2
    return 1
  fi

  # Chown the freshly-rsync'd paths. Keep it broad — rsync may have
  # touched directories above the dirty files too.
  if ! flyctl ssh console --app "$FLY_APP" --machine "$LEERIE_MACHINE_ID" \
         --pty=false -C "chown -R leerie: /work" >/dev/null 2>&1; then
    rm -f "$file_list" "$wrapper"
    echo "leerie: seed_repo: chown -R leerie: /work after delta failed" >&2
    return 1
  fi

  rm -f "$file_list" "$wrapper"
  echo "[leerie] remote: seeding complete" >&2
}

# ---------------------------------------------------------------------------
# seed_repo
#
# Used on fresh provisions. Two phases:
#   1. seed_repo_clone — bundles parent + submodules, machine clones from
#      bundles. Delivers committed state only.
#   2. seed_repo_dirty — rsync's the dirty/untracked delta plus
#      forced-in .claude/, completing the working tree state on the
#      machine.
#
# re-seed.sh still calls seed_repo_dirty directly when the user
# pauses + edits + resumes.
# ---------------------------------------------------------------------------
seed_repo() {
  seed_repo_clone || return 1
  seed_repo_dirty
}
