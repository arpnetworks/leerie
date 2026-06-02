#!/usr/bin/env bash
# scripts/host-finalize.sh — host-side finalize block (push + PR creation).
#
# Sourced by the `leerie` launcher's normal post-run path and by the
# `leerie --finalize <run-id>` fast-path. Both code paths share the same
# push/PR mechanics — the discovery of *which* run to finalize differs.
#
# Exports: host_finalize <run-dir>
#
# Inputs (env or args):
#   $1                — absolute path to .leerie/runs/<run-id>/
#   USER_REPO         — git repo root (set by launcher)
#   NO_VERIFY_PUSH    — "true" to pass --no-verify to git push (optional)
#
# Side effects:
#   - git push -u origin <run-branch>
#   - gh pr create
#   - update_run_json on the sidecar to record pushed_at / pr_url / errors
#
# Exit code semantics:
#   0 — success (push OK; PR may have failed non-fatally)
#   1 — push failed (no PR attempted)
#
# DESIGN §6 *Finalization*. The host owns this step because gh auth,
# ssh-agent, and Keychain are host-side; the Fly Machine cannot push.

# update_run_json (local jq-based helper). Kept here rather than in
# scripts/remote/lib.sh because that one uses python3, and the launcher
# already imports jq via the preflight; using jq keeps this file
# python-free and matches the in-place semantics of the original block.
_host_finalize_update_run_json() {
  local sidecar="$1"
  shift
  local tmp="$sidecar.tmp"
  local jq_filter='.'
  for kv in "$@"; do
    local key="${kv%%=*}"
    local val="${kv#*=}"
    if [ -z "$val" ]; then
      jq_filter="${jq_filter} | .${key} = null"
    else
      jq_filter="${jq_filter} | .${key} = \$${key}"
    fi
  done
  local args=()
  for kv in "$@"; do
    local key="${kv%%=*}"
    local val="${kv#*=}"
    [ -z "$val" ] || args+=(--arg "$key" "$val")
  done
  jq "${args[@]+"${args[@]}"}" "$jq_filter" "$sidecar" > "$tmp"
  mv "$tmp" "$sidecar"
}

host_finalize() {
  local run_dir="$1"
  if [ -z "$run_dir" ] || [ ! -d "$run_dir" ]; then
    echo "host_finalize: missing or invalid <run-dir>: $run_dir" >&2
    return 1
  fi

  local run_json="$run_dir/run.json"
  local state_json="$run_dir/state.json"
  if [ ! -f "$run_json" ]; then
    echo "host_finalize: no run.json at $run_json" >&2
    return 1
  fi

  # Honor run.json.no_push (--no-push or no-work short-circuit).
  if [ "$(jq -r '.no_push // false' "$run_json")" = "true" ]; then
    echo "[leerie] finalize: run.json has no_push=true; skipping push + PR" >&2
    return 0
  fi

  # Honor already-pushed (idempotent re-invocation of --finalize).
  if [ -n "$(jq -r '.pushed_at // ""' "$run_json")" ]; then
    echo "[leerie] finalize: run already pushed; nothing to do" >&2
    return 0
  fi

  local run_id run_branch working_branch
  run_id="$(basename "$run_dir")"
  run_branch="$(jq -r '.branch // ""' "$run_json")"
  working_branch="$(jq -r '.working_branch // ""' "$run_json")"
  if [ -z "$run_branch" ] || [ -z "$working_branch" ]; then
    echo "leerie: error — run.json at $run_json is missing branch info." >&2
    echo "  Skipping push + PR. Push the run branch manually if it exists." >&2
    return 1
  fi

  # --- step 1: push -----------------------------------------------------
  local push_args=(git -C "$USER_REPO" push -u origin "$run_branch")
  [ "${NO_VERIFY_PUSH:-false}" = "true" ] && push_args+=(--no-verify)

  echo "[leerie] finalize: pushing $run_branch to origin$([ "${NO_VERIFY_PUSH:-false}" = "true" ] && echo " (--no-verify)")" >&2
  local push_stderr
  if ! push_stderr="$("${push_args[@]}" 2>&1 >/dev/null)"; then
    _host_finalize_update_run_json "$run_json" \
      "pushed_at=" "push_error=${push_stderr:-git push failed}" \
      "pr_url=" "pr_error="
    echo "leerie: error: git push failed for branch \`$run_branch\`." >&2
    echo "  Local state is intact:" >&2
    echo "    - run branch:     $run_branch (holds all wave merges)" >&2
    echo "    - working branch: $working_branch (unchanged from run start; the intended PR base)" >&2
    echo "  Resolve and retry manually:" >&2
    echo "    git push -u origin $run_branch$([ "${NO_VERIFY_PUSH:-false}" = "true" ] && echo " --no-verify")" >&2
    echo "  Push stderr was:" >&2
    printf '    %s\n' "$push_stderr" >&2
    return 1
  fi
  local pushed_at
  pushed_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  _host_finalize_update_run_json "$run_json" "pushed_at=$pushed_at" "push_error="
  echo "[leerie] finalize: pushed $run_branch" >&2

  # --- step 2: PR creation ---------------------------------------------
  # Primary path: the pr_writer worker (DESIGN §6 *Finalization*) wrote
  # pr_title + pr_body to run.json. Use them when present.
  # Fallback: compose a deterministic body from state.json.
  local pr_title pr_body pr_title_llm pr_body_llm
  pr_title_llm="$(jq -r '.pr_title // ""' "$run_json")"
  pr_body_llm="$(jq -r '.pr_body // ""' "$run_json")"

  if [ -n "$pr_title_llm" ] && [ -n "$pr_body_llm" ]; then
    pr_title="leerie: $pr_title_llm"
    pr_body="$pr_body_llm"
  else
    # Deterministic fallback.
    local or_na_helper task first_cat source_of_truth started_at finished_at
    local wave_count subtask_count worker_count working_branch_display
    or_na_helper() { [ -n "$1" ] && [ "$1" != "null" ] && printf '%s' "$1" || printf 'n/a'; }
    task="$(jq -r '.task // ""' "$state_json")"
    first_cat="$(or_na_helper "$(jq -r '.categories[0] // ""' "$state_json")")"
    source_of_truth="$(or_na_helper "$(jq -r '.answers.source_of_truth // ""' "$state_json")")"
    started_at="$(or_na_helper "$(jq -r '.started_at // ""' "$state_json")")"
    finished_at="$(or_na_helper "$(jq -r '.finished_at // ""' "$state_json")")"
    wave_count="$(jq -r '.waves | length' "$state_json")"
    subtask_count="$(jq -r '[.waves[] | length] | add // 0' "$state_json")"
    worker_count="$(or_na_helper "$(jq -r '.worker_count // ""' "$state_json")")"
    working_branch_display="$(or_na_helper "$working_branch")"

    pr_title="leerie: $run_id"
    pr_body="$(cat <<EOF
## Task

$task

## Classification

- Category: $first_cat
- Source of truth: $source_of_truth

## Run summary

- Run ID: $run_id
- Started: $started_at
- Finished: $finished_at
- Waves: $wave_count, subtasks: $subtask_count
- Workers: $worker_count
- Generated by leerie on \`$working_branch_display\`.

See \`.leerie/runs/$run_id/state.json\` for full run state.
EOF
)"
  fi

  echo "[leerie] finalize: opening PR against $working_branch" >&2
  local pr_output
  if ! pr_output="$(echo "$pr_body" | gh pr create \
                    --base "$working_branch" \
                    --head "$run_branch" \
                    --title "$pr_title" \
                    --body-file - 2>&1)"; then
    # PR-creation failure is NON-fatal — push succeeded.
    _host_finalize_update_run_json "$run_json" \
      "pr_url=" "pr_error=${pr_output:-gh pr create failed}"
    echo "⚠  \`gh pr create\` failed; branch was pushed successfully." >&2
    echo "  Pushed branch: $run_branch (on origin)" >&2
    echo "  Open the PR manually:" >&2
    echo "    gh pr create --base $working_branch --head $run_branch" >&2
    echo "  Or via the GitHub web UI for the repo." >&2
    echo "  gh stderr was:" >&2
    printf '    %s\n' "$pr_output" >&2
    return 0
  fi
  local pr_url
  pr_url="$(printf '%s' "$pr_output" | tail -n 1)"
  _host_finalize_update_run_json "$run_json" "pr_url=$pr_url" "pr_error="
  echo "[leerie] finalize: opened PR $pr_url" >&2
  return 0
}
