"""phase_finalize must gate pr_writer and run.json.no_push on **intent**,
not on the orchestrator's --no-push mechanism flag.

Regression pin for the Fly-runtime PR-description bug:

On Fly, the launcher always passes --no-push to the in-Machine
orchestrator because the Machine has no GitHub auth and cannot push.
The orchestrator-side --no-push is therefore a mechanism flag, not the
user's intent. The user's launch-time intent flows separately via
--host-no-push true|false (recorded in fly-machine.json.host_no_push
host-side, propagated into the Machine on argv).

`push_will_happen(no_push, host_no_push)` is the helper that resolves
intent vs mechanism into a single boolean. phase_finalize must:

  1. Gate the pr_writer invocation on `push_will_happen(...)`.
  2. Gate the run.json.no_push write on `not push_will_happen(...)`
     (the host's host_finalize reads run.json.no_push as the
     authoritative intent flag).
  3. Gate the "skipped push and PR" log line on the same intent.

Without (1), pr_writer is silently skipped on every Fly run and the
host's gh pr create falls back to the deterministic template. Without
(2), host_finalize would refuse to push on every Fly happy path
because the synced run.json carries no_push=true.
"""
from __future__ import annotations

import inspect


def test_phase_finalize_gates_pr_writer_on_intent(leerie):
    """pr_writer must run when push_will_happen() is True — not when
    the mechanism flag `not no_push` is True."""
    src = inspect.getsource(leerie.phase_finalize)
    # Look for the gate using push_will_happen, not the legacy
    # `if not no_push and ...` form.
    assert "push_will_happen(no_push, host_no_push)" in src, (
        "phase_finalize must call push_will_happen(no_push, host_no_push) "
        "to decide whether pr_writer runs. The bare `not no_push` gate is "
        "wrong on Fly: the launcher injects --no-push as a mechanism "
        "flag (the Machine can't push), so the bare gate silences "
        "pr_writer on every Fly run."
    )


def test_phase_finalize_writes_intent_not_mechanism_to_run_json(leerie):
    """run.json.no_push must be written as **intent** so host_finalize
    reads the user's preference, not the launcher-forced mechanism flag."""
    src = inspect.getsource(leerie.phase_finalize)
    # The line `no_push=no_push,` is the regression marker — that
    # writes the mechanism flag verbatim, which on Fly conflates
    # mechanism with intent.
    assert "no_push=not will_push" in src or "no_push=not push_will_happen" in src, (
        "phase_finalize must write intent (not the mechanism flag) to "
        "run.json.no_push. Look for `no_push=not will_push` (where "
        "`will_push = push_will_happen(no_push, host_no_push)`). "
        "Writing `no_push=no_push` directly is the bug — it propagates "
        "the launcher-forced mechanism flag and makes host_finalize "
        "skip push on every Fly run."
    )


def test_phase_finalize_signature_accepts_host_no_push(leerie):
    """phase_finalize must accept host_no_push as a keyword argument so
    the orchestrator's main entry point can pass args.host_no_push
    through without the no-work path (which only writes via
    _write_run_json) needing the new parameter."""
    sig = inspect.signature(leerie.phase_finalize)
    assert "host_no_push" in sig.parameters, (
        "phase_finalize must accept host_no_push: bool | None = None. "
        "None default keeps local-runtime callers and tests working "
        "(push_will_happen falls back to `not no_push` for None)."
    )
    param = sig.parameters["host_no_push"]
    assert param.default is None, (
        "host_no_push must default to None so callers can omit it on "
        "the local-runtime path without changing behavior."
    )


def test_phase_finalize_skip_log_line_gates_on_intent(leerie):
    """The 'skipped push and PR (--no-push)' log line must fire on
    intent, not on the mechanism flag. Otherwise on Fly the log says
    'skipped push' on every run while the host is about to push."""
    src = inspect.getsource(leerie.phase_finalize)
    # The legacy `if no_push:` branch around the skip log is the
    # regression marker.
    assert "if not will_push:" in src or "if not push_will_happen" in src, (
        "The 'skipped push and PR' log line must branch on intent "
        "(`not will_push` / `not push_will_happen(...)`), not on the "
        "raw no_push flag. On Fly the bare `if no_push:` fires for "
        "every happy-path run because no_push is True as a mechanism "
        "flag, and the log misleadingly says 'skipped' while the host "
        "is auto-finalizing."
    )


def test_orchestrate_call_site_passes_host_no_push(leerie):
    """The phase_finalize call site in _run_phases must pass
    host_no_push=args.host_no_push so the Fly path's intent reaches
    the function. Without this thread, host_no_push stays None and
    the Fly happy path silently regresses to using the mechanism
    flag."""
    src = inspect.getsource(leerie._run_phases)
    assert "host_no_push=getattr(args, \"host_no_push\", None)" in src, (
        "_run_phases's phase_finalize call must pass "
        "host_no_push=getattr(args, \"host_no_push\", None). Without "
        "this, args.host_no_push (set from --host-no-push by the Fly "
        "launcher) never reaches phase_finalize and the Fly happy "
        "path silently regresses to the mechanism-flag gate."
    )
