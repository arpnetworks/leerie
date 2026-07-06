"""Behavioral tests for scripts/host-finalize.sh.

Companion to tests/test_finalize_sh_behavior.py (which covers
scripts/finalize.sh, the in-container verifier). This file covers
scripts/host-finalize.sh, the host-side push+PR block extracted from
the leerie launcher to make `leerie --finalize <run-id>` actually finalize
(Audit Drift 7).

The tests source host-finalize.sh in a bash subprocess with stubbed
`git` and `gh` (writes-to-log instead of touching real remotes) and
assert on:
  - early-exit invariants (no_push, already-pushed, missing branch)
  - run.json sidecar updates (pushed_at, push_error, pr_url, pr_error)

Push/PR end-to-end with a real local git repo is covered separately by
test_finalize_sh_behavior.py's harness pattern; this file focuses on the
extracted function's contract.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOST_FINALIZE_SH = REPO_ROOT / "scripts" / "host-finalize.sh"


def _make_stub_bin(tmp_path: Path, name: str, body: str) -> None:
    """Write a stub `name` binary that logs to ${name}.log and runs `body`."""
    p = tmp_path / name
    p.write_text(f"#!/usr/bin/env bash\necho \"$@\" >> {tmp_path}/{name}.log\n{body}\n")
    p.chmod(0o755)


def _make_run(tmp_path: Path, run_id: str, run_json: dict,
              state_json: dict | None = None) -> Path:
    user_repo = tmp_path / "user-repo"
    run_dir = user_repo / ".leerie" / "runs" / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "run.json").write_text(json.dumps(run_json))
    if state_json is not None:
        (run_dir / "state.json").write_text(json.dumps(state_json))
    return run_dir


def _run_host_finalize(tmp_path: Path, run_dir: Path,
                       git_body: str = "exit 0",
                       gh_body: str = "echo https://github.com/o/r/pull/1") -> subprocess.CompletedProcess:
    """Source host-finalize.sh in bash with stubbed git/gh and call
    host_finalize <run_dir>. Returns the CompletedProcess."""
    _make_stub_bin(tmp_path, "git", git_body)
    _make_stub_bin(tmp_path, "gh", gh_body)
    # No-op `sleep` so the gh-pr-create retry loop's backoff
    # (0/5/10/20/30s) is exercised WITHOUT real wall-clock delay — a
    # PR-failure test would otherwise spend ~68s sleeping. The retry
    # logic is still verified (the loop iterates and re-invokes `gh`,
    # visible in gh.log); only the delay is removed.
    _make_stub_bin(tmp_path, "sleep", "exit 0")
    user_repo = run_dir.parent.parent.parent  # .leerie/runs/<id>/.. → .leerie → repo
    # Run under `set -euo pipefail` to match production faithfully:
    # host-finalize.sh is always sourced INTO the launcher, which sets
    # `set -euo pipefail` (leerie:17). Without this, a failing command
    # substitution inside host_finalize (e.g. `ls-remote` on an absent
    # origin → pipefail rc 128) would be silently swallowed by the test
    # but abort finalize in production. Matching shell options here is
    # what makes those `|| true` guards actually verified.
    script = f"set -euo pipefail; . {HOST_FINALIZE_SH}; host_finalize {run_dir}"
    return subprocess.run(
        ["bash", "-c", script],
        env={
            "PATH": f"{tmp_path}:/usr/bin:/bin",
            "USER_REPO": str(user_repo),
            "HOME": str(tmp_path),
        },
        capture_output=True, text=True, check=False,
    )


# --- early-exit invariants ------------------------------------------------

def test_skips_when_no_push_true(tmp_path):
    """run.json has no_push=true → skip with the "no_push=true" message,
    return 0 without touching git or gh."""
    run_dir = _make_run(tmp_path, "feat-x-aaaaaa", run_json={
        "branch": "leerie/runs/feat-x-aaaaaa",
        "working_branch": "main",
        "no_push": True,
        "finished_at": "2026-05-29T16:00:00+00:00",
    })
    r = _run_host_finalize(tmp_path, run_dir)
    assert r.returncode == 0, r.stderr
    assert "no_push=true" in r.stderr
    # No git or gh invocations.
    assert not (tmp_path / "git.log").exists() or (tmp_path / "git.log").read_text() == ""


def test_skips_when_already_pushed_and_origin_up_to_date(tmp_path):
    """run.json has pushed_at set AND origin already matches the local
    run-branch tip → idempotent re-invocation; return 0 without a second
    push. The idempotency gate is tip-aware (DESIGN §6 *Finalization*):
    pushed_at alone is not enough — origin must match."""
    run_dir = _make_run(tmp_path, "feat-y-aaaaaa", run_json={
        "branch": "leerie/runs/feat-y-aaaaaa",
        "working_branch": "main",
        "pushed_at": "2026-05-29T16:00:00+00:00",
        "finished_at": "2026-05-29T15:00:00+00:00",
    })
    # git stub: rev-parse (local tip) and ls-remote (origin tip) both
    # return the SAME sha → tips equal → no-op.
    git_body = '''
if [ "$1" = "-C" ] && [ "$3" = "rev-parse" ] && [ "$4" = "--verify" ]; then
  exit 0
fi
if [ "$1" = "-C" ] && [ "$3" = "rev-parse" ]; then
  echo "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"; exit 0
fi
if [ "$1" = "-C" ] && [ "$3" = "ls-remote" ]; then
  printf 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\trefs/heads/x\n'; exit 0
fi
exit 0
'''
    r = _run_host_finalize(tmp_path, run_dir, git_body=git_body)
    assert r.returncode == 0, r.stderr
    assert "already pushed" in r.stderr
    assert "origin up to date" in r.stderr
    # No `git push` was invoked (only rev-parse / ls-remote). Match the
    # push subcommand token, not the substring — the tmp path contains
    # "pushed".
    git_log = (tmp_path / "git.log").read_text()
    push_invoked = any(
        "push" in line.split() for line in git_log.splitlines()
    )
    assert not push_invoked, git_log


def test_repushes_when_local_ahead_of_origin(tmp_path):
    """run.json has pushed_at set but the local run-branch tip is AHEAD of
    origin (a prior finalize pushed a PARTIAL branch — the PR-#22 wedge).
    The run is complete (completed_waves == len(waves)), so host_finalize
    falls through to a fast-forward re-push + PR instead of no-op'ing."""
    run_dir = _make_run(
        tmp_path, "feat-ahead-aaaa",
        run_json={
            "branch": "leerie/runs/feat-ahead-aaaa",
            "working_branch": "main",
            "pushed_at": "2026-05-29T16:00:00+00:00",
            "finished_at": "2026-05-29T17:00:00+00:00",
        },
        state_json={"task": "x", "started_at": "2026-05-29T15:00:00+00:00",
                    "categories": ["feature"], "waves": [[]],
                    "completed_waves": 1},
    )
    # git stub: local tip 'bbbb…' != origin tip 'aaaa…' → local ahead →
    # re-push. Track that `push` is invoked.
    git_body = '''
if [ "$1" = "-C" ] && [ "$3" = "rev-parse" ] && [ "$4" = "--verify" ]; then
  exit 0
fi
if [ "$1" = "-C" ] && [ "$3" = "rev-parse" ]; then
  echo "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"; exit 0
fi
if [ "$1" = "-C" ] && [ "$3" = "ls-remote" ]; then
  printf 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\trefs/heads/x\n'; exit 0
fi
exit 0
'''
    r = _run_host_finalize(tmp_path, run_dir, git_body=git_body)
    assert r.returncode == 0, r.stderr
    assert "re-pushing" in r.stderr
    # A `git push` DID happen (match the subcommand token, not the tmp
    # path substring), and a PR was opened.
    git_log = (tmp_path / "git.log").read_text()
    push_invoked = any(
        "push" in line.split() for line in git_log.splitlines()
    )
    assert push_invoked, git_log
    after = json.loads((run_dir / "run.json").read_text())
    assert after.get("pr_url") is not None
    assert after.get("pr_error") is None


def test_already_pushed_up_to_date_noops_even_with_incomplete_waves(tmp_path):
    """Regression guard: an already-pushed run whose origin matches the
    local tip must no-op (return 0) EVEN IF state.json shows
    completed_waves < len(waves) — a resume artifact, or a run pushed under
    old semantics then re-finalized. The tip-aware idempotency short-circuit
    runs BEFORE the completion gate, so a genuinely-pushed run is never
    refused with 'refusing to finalize' (DESIGN §6 *Finalization*: only the
    re-push is gated on completeness, not the equal-tips no-op)."""
    run_dir = _make_run(
        tmp_path, "feat-done-aaaa",
        run_json={
            "branch": "leerie/runs/feat-done-aaaa",
            "working_branch": "main",
            "pushed_at": "2026-05-29T16:00:00+00:00",
            "finished_at": "2026-05-29T15:00:00+00:00",
        },
        # Incomplete waves — would trip the completion gate if it ran first.
        state_json={"task": "x", "started_at": "2026-05-29T15:00:00+00:00",
                    "categories": ["feature"],
                    "waves": [[1], [2], [3]], "completed_waves": 1},
    )
    # git stub: local tip == origin tip → already pushed, up to date.
    git_body = '''
if [ "$1" = "-C" ] && [ "$3" = "rev-parse" ] && [ "$4" = "--verify" ]; then
  exit 0
fi
if [ "$1" = "-C" ] && [ "$3" = "rev-parse" ]; then
  echo "cccccccccccccccccccccccccccccccccccccccc"; exit 0
fi
if [ "$1" = "-C" ] && [ "$3" = "ls-remote" ]; then
  printf 'cccccccccccccccccccccccccccccccccccccccc\trefs/heads/x\n'; exit 0
fi
exit 0
'''
    r = _run_host_finalize(tmp_path, run_dir, git_body=git_body)
    assert r.returncode == 0, r.stderr
    assert "origin up to date" in r.stderr
    assert "refusing to finalize" not in r.stderr
    # No push happened.
    git_log = (tmp_path / "git.log").read_text()
    push_invoked = any(
        "push" in line.split() for line in git_log.splitlines()
    )
    assert not push_invoked, git_log


def test_fails_when_branch_missing(tmp_path):
    """run.json missing the `branch` field → error and return 1."""
    run_dir = _make_run(tmp_path, "feat-z-aaaaaa", run_json={
        "working_branch": "main",
        "finished_at": "2026-05-29T16:00:00+00:00",
    })
    r = _run_host_finalize(tmp_path, run_dir)
    assert r.returncode == 1, r.stderr
    assert "missing branch info" in r.stderr


def test_records_push_error_on_git_push_failure(tmp_path):
    """git push fails → push_error set on sidecar, pushed_at stays null,
    function returns 1."""
    run_dir = _make_run(tmp_path, "feat-q-aaaaaa", run_json={
        "branch": "leerie/runs/feat-q-aaaaaa",
        "working_branch": "main",
        "finished_at": "2026-05-29T16:00:00+00:00",
    })
    # git stub: emit a fake error to stderr and exit 1 on `push`.
    git_body = '''
if [ "$1" = "-C" ] && [ "$3" = "push" ] || [ "$1" = "push" ]; then
  echo "fatal: simulated push failure" >&2
  exit 1
fi
exit 0
'''
    r = _run_host_finalize(tmp_path, run_dir, git_body=git_body)
    assert r.returncode == 1, r.stderr
    assert "git push failed" in r.stderr
    after = json.loads((run_dir / "run.json").read_text())
    assert after.get("push_error") is not None
    assert "simulated push failure" in after["push_error"]
    assert after.get("pushed_at") is None


def test_records_pushed_at_on_success(tmp_path):
    """Successful push writes pushed_at and clears push_error."""
    run_dir = _make_run(
        tmp_path, "feat-s-aaaaaa",
        run_json={
            "branch": "leerie/runs/feat-s-aaaaaa",
            "working_branch": "main",
            "finished_at": "2026-05-29T16:00:00+00:00",
            "pr_title": "feat: do thing",
            "pr_body": "## Summary\n\nthis is the body",
        },
        state_json={
            "task": "do thing",
            "started_at": "2026-05-29T15:00:00+00:00",
            "categories": ["feature"],
        },
    )
    r = _run_host_finalize(tmp_path, run_dir)
    assert r.returncode == 0, r.stderr
    after = json.loads((run_dir / "run.json").read_text())
    assert after.get("pushed_at") is not None
    assert after.get("push_error") is None
    assert after.get("pr_url") is not None
    assert after.get("pr_error") is None


def test_skips_when_run_branch_absent_locally(tmp_path):
    """Defense-in-depth: when run.json names a branch that does NOT
    exist locally (the cleared-but-empty terminal-state case from
    DESIGN §8 — no setup-run.sh ran), host_finalize logs "absent
    locally" and returns 0 without attempting git push.

    Without this guard, the launcher would try to push a non-existent
    branch and fail with `src refspec ... does not match any`. The
    guard backstops fetch-branch.sh's conditional stripper and the
    --finalize stripper in `leerie`."""
    run_dir = _make_run(tmp_path, "noop-run-aaaaaa", run_json={
        "branch": "leerie/runs/noop-run-aaaaaa",
        "working_branch": "main",
        "finished_at": "2026-05-29T16:00:00+00:00",
    })
    # git stub: `rev-parse --verify` returns 1 (branch absent); any
    # other invocation passes. This is the shape `git -C <repo>
    # rev-parse --verify refs/heads/<branch>` sees on a local repo
    # that never had the branch checked out.
    git_body = '''
if [ "$1" = "-C" ] && [ "$3" = "rev-parse" ]; then
  exit 1
fi
exit 0
'''
    r = _run_host_finalize(tmp_path, run_dir, git_body=git_body)
    assert r.returncode == 0, r.stderr
    assert "absent locally" in r.stderr
    assert "treating as no-op" in r.stderr
    # Sidecar untouched: no push_error, no pushed_at, no pr_*.
    after = json.loads((run_dir / "run.json").read_text())
    assert after.get("pushed_at") is None
    assert after.get("push_error") is None
    assert after.get("pr_url") is None
    assert after.get("pr_error") is None


def test_pr_failure_is_non_fatal(tmp_path):
    """gh pr create fails → pr_error set, return 0 (push already succeeded)."""
    run_dir = _make_run(
        tmp_path, "feat-p-aaaaaa",
        run_json={
            "branch": "leerie/runs/feat-p-aaaaaa",
            "working_branch": "main",
            "finished_at": "2026-05-29T16:00:00+00:00",
        },
        state_json={"task": "x", "started_at": "2026-05-29T15:00:00+00:00",
                    "categories": ["feature"], "waves": [[]],
                    # A genuinely finalized run has completed_waves ==
                    # len(waves); required so the completion gate treats
                    # this as complete (not a mid-wave crash).
                    "completed_waves": 1},
    )
    r = _run_host_finalize(tmp_path, run_dir,
                           gh_body='echo "fatal: simulated gh failure" >&2; exit 1')
    # PR failure is non-fatal — push succeeded.
    assert r.returncode == 0, r.stderr
    after = json.loads((run_dir / "run.json").read_text())
    assert after.get("pushed_at") is not None
    assert after.get("pr_url") is None
    assert after.get("pr_error") is not None
    assert "simulated gh failure" in after["pr_error"]


# --- completion gate (DESIGN §6, the PR-#22 fix) --------------------------

def test_gate_blocks_mid_wave_crashed_run(tmp_path):
    """A run with finished_at (die-path discovery stamp) but
    completed_waves < len(waves) is refused: no push, no PR, return 1 with
    an actionable resume hint. This is the single chokepoint that prevents
    the launcher / --finalize verb / Fly teardown from pushing a partial
    run branch and opening a premature PR (the PR-#22 incident)."""
    run_dir = _make_run(
        tmp_path, "crash-run-aaaaaa",
        run_json={
            "branch": "leerie/runs/crash-run-aaaaaa",
            "working_branch": "main",
            "finished_at": "2026-07-05T23:25:46+00:00",
        },
        state_json={"completed_waves": 1, "waves": [[1], [2], [3], [4], [5]]},
    )
    r = _run_host_finalize(tmp_path, run_dir)
    assert r.returncode == 1, r.stderr
    assert "refusing to finalize" in r.stderr
    assert "1 of 5 waves" in r.stderr
    # No push, no PR, and no pushed_at written.
    assert not (tmp_path / "git.log").exists() or \
        "push" not in (tmp_path / "git.log").read_text()
    after = json.loads((run_dir / "run.json").read_text())
    assert after.get("pushed_at") is None


def test_gate_allows_fully_integrated_run(tmp_path):
    """completed_waves == len(waves) → the gate lets the run through to
    the normal push path."""
    run_dir = _make_run(
        tmp_path, "done-run-aaaaaa",
        run_json={
            "branch": "leerie/runs/done-run-aaaaaa",
            "working_branch": "main",
            "finished_at": "2026-07-05T23:25:46+00:00",
        },
        state_json={"task": "x", "started_at": "2026-07-05T21:00:00+00:00",
                    "categories": ["feature"],
                    "completed_waves": 3, "waves": [[1], [2], [3]]},
    )
    r = _run_host_finalize(tmp_path, run_dir)
    assert r.returncode == 0, r.stderr
    assert "refusing to finalize" not in r.stderr
    after = json.loads((run_dir / "run.json").read_text())
    assert after.get("pushed_at") is not None


def test_gate_allows_no_work_run(tmp_path):
    """The cleared-but-empty terminal state (no_work_required, waves==[])
    is not blocked. (It normally short-circuits on no_push=true earlier;
    this pins the gate's own no-work exemption directly.)"""
    run_dir = _make_run(
        tmp_path, "nowork-run-aaaaaa",
        run_json={
            "branch": "leerie/runs/nowork-run-aaaaaa",
            "working_branch": "main",
            "finished_at": "2026-07-05T23:25:46+00:00",
        },
        state_json={"no_work_required": True, "completed_waves": 0, "waves": []},
    )
    r = _run_host_finalize(tmp_path, run_dir)
    assert r.returncode == 0, r.stderr
    assert "refusing to finalize" not in r.stderr


def test_gate_fails_open_without_state_json(tmp_path):
    """No state.json (state_json=None) → fail-open: the gate does not fire,
    so a legitimately complete run is never blocked over a missing file."""
    run_dir = _make_run(
        tmp_path, "nostate-run-aaaaaa",
        run_json={
            "branch": "leerie/runs/nostate-run-aaaaaa",
            "working_branch": "main",
            "finished_at": "2026-07-05T23:25:46+00:00",
        },
        # no state_json
    )
    r = _run_host_finalize(tmp_path, run_dir)
    assert r.returncode == 0, r.stderr
    assert "refusing to finalize" not in r.stderr
    after = json.loads((run_dir / "run.json").read_text())
    assert after.get("pushed_at") is not None
