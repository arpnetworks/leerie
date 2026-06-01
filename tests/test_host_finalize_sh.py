"""Behavioral tests for scripts/host-finalize.sh.

Companion to tests/test_finalize_sh_behavior.py (which covers
scripts/finalize.sh, the in-container verifier). This file covers
scripts/host-finalize.sh, the host-side push+PR block extracted from
the pila launcher to make `pila --finalize <run-id>` actually finalize
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
    run_dir = user_repo / ".pila" / "runs" / run_id
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
    user_repo = run_dir.parent.parent.parent  # .pila/runs/<id>/.. → .pila → repo
    script = f". {HOST_FINALIZE_SH}; host_finalize {run_dir}"
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
        "branch": "pila/runs/feat-x-aaaaaa",
        "working_branch": "main",
        "no_push": True,
        "finished_at": "2026-05-29T16:00:00+00:00",
    })
    r = _run_host_finalize(tmp_path, run_dir)
    assert r.returncode == 0, r.stderr
    assert "no_push=true" in r.stderr
    # No git or gh invocations.
    assert not (tmp_path / "git.log").exists() or (tmp_path / "git.log").read_text() == ""


def test_skips_when_already_pushed(tmp_path):
    """run.json has pushed_at set → idempotent re-invocation; return 0."""
    run_dir = _make_run(tmp_path, "feat-y-aaaaaa", run_json={
        "branch": "pila/runs/feat-y-aaaaaa",
        "working_branch": "main",
        "pushed_at": "2026-05-29T16:00:00+00:00",
        "finished_at": "2026-05-29T15:00:00+00:00",
    })
    r = _run_host_finalize(tmp_path, run_dir)
    assert r.returncode == 0, r.stderr
    assert "already pushed" in r.stderr


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
        "branch": "pila/runs/feat-q-aaaaaa",
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
            "branch": "pila/runs/feat-s-aaaaaa",
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


def test_pr_failure_is_non_fatal(tmp_path):
    """gh pr create fails → pr_error set, return 0 (push already succeeded)."""
    run_dir = _make_run(
        tmp_path, "feat-p-aaaaaa",
        run_json={
            "branch": "pila/runs/feat-p-aaaaaa",
            "working_branch": "main",
            "finished_at": "2026-05-29T16:00:00+00:00",
        },
        state_json={"task": "x", "started_at": "2026-05-29T15:00:00+00:00",
                    "categories": ["feature"], "waves": [[]]},
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
