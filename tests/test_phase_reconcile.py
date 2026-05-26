"""Tests for `phase_reconcile()` — the orchestrator-level wrapper that
spawns the reconciler worker when planners produced mismatched
capability tags.

The live LLM call (`claude_p`) is exercised end-to-end at PR-review
time, not in unit tests (the codebase's testing convention; see
CLAUDE.md "The worker invocation path is not unit-tested"). Here we
cover:

- The **short-circuit path** — when every `requires` is already
  resolved, `phase_reconcile` returns the plan unchanged without
  spawning a worker (the most common case in practice).
- **Source-text pins** on the worker invocation shape, the die() paths,
  and the second-pass check.
- The **mutation logic** is tested in test_phase_reconcile_helpers.py
  against `_apply_reconciler_output`; here we just confirm
  `phase_reconcile` plumbs everything correctly.
"""
from __future__ import annotations

import asyncio
import inspect
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CENTELLA_PY = REPO_ROOT / "orchestrator" / "centella.py"


def _plan(domain: str, *subtasks: dict) -> dict:
    return {"domain": domain, "status": "ready", "subtasks": list(subtasks)}


def _minimal_state(centella, tmp_path):
    """A State with just enough plumbing for phase_reconcile to read
    st.bump_workers and not crash. No actual workers will run — the
    short-circuit path never invokes claude_p."""
    centella_root = tmp_path / ".centella"
    run_id = "test-reconcile-aaa111"
    (centella_root / "runs" / run_id).mkdir(parents=True)
    st = centella.State(centella_root, run_id)
    st.data = {"task": "test", "worker_count": 0}
    st.save()
    return st


# --- short-circuit -------------------------------------------------------

def test_short_circuit_no_unresolved_returns_plans_unchanged(centella, tmp_path):
    """The common case: planners agreed on capability vocabulary, every
    `requires` has a matching `provides`. phase_reconcile must return
    the plans list without spawning a worker."""
    plans = [
        _plan("feature-implementation",
              {"id": "feat-001", "title": "x", "provides": ["a"]}),
        _plan("testing",
              {"id": "test-001", "title": "y", "requires": ["a"]}),
    ]
    st = _minimal_state(centella, tmp_path)
    caps = {"max_total_workers": 40, "max_parallel": 4,
            "confidence_rounds": 8}
    # `models` doesn't need a "reconciler" key for the short-circuit
    # path — the worker is never invoked.
    models: dict[str, str] = {}

    result = asyncio.run(centella.phase_reconcile(plans, "test task", st,
                                                  caps, models))
    # Same list, unchanged.
    assert result is plans
    assert plans[1]["subtasks"][0]["requires"] == ["a"]
    # No worker spawned → worker_count unchanged.
    assert st.data.get("worker_count", 0) == 0


def test_short_circuit_empty_plans(centella, tmp_path):
    """Defensive: empty plans list short-circuits without error."""
    plans: list = []
    st = _minimal_state(centella, tmp_path)
    caps = {"max_total_workers": 40, "max_parallel": 4,
            "confidence_rounds": 8}
    result = asyncio.run(centella.phase_reconcile(plans, "x", st, caps, {}))
    assert result is plans
    assert result == []


def test_short_circuit_plan_with_no_requires(centella, tmp_path):
    """Plan with subtasks that have `provides` but no `requires` →
    nothing to reconcile."""
    plans = [_plan("feature-implementation",
                   {"id": "feat-001", "title": "x", "provides": ["a"]})]
    st = _minimal_state(centella, tmp_path)
    caps = {"max_total_workers": 40, "max_parallel": 4,
            "confidence_rounds": 8}
    result = asyncio.run(centella.phase_reconcile(plans, "x", st, caps, {}))
    assert result is plans
    assert st.data.get("worker_count", 0) == 0


# --- source-text pins on phase_reconcile's contract ----------------------

def test_phase_reconcile_uses_reconciler_schema(centella):
    """Worker is gated on SCHEMAS["reconciler"] — pin so the schema-key
    arg doesn't drift."""
    src = inspect.getsource(centella.phase_reconcile)
    assert 'schema_key="reconciler"' in src


def test_phase_reconcile_uses_read_tools(centella):
    """Reconciler is read-only — same tool bucket as classifier/planner.
    Pin so a refactor doesn't accidentally upgrade it to ACT_TOOLS
    (write/edit) which would let the worker modify files."""
    src = inspect.getsource(centella.phase_reconcile)
    assert "allowed_tools=READ_TOOLS" in src


def test_phase_reconcile_uses_reconciler_model(centella):
    """The worker uses models['reconciler'] — pin so commit 4's wiring
    pre-condition (commit 3 adds 'reconciler' to WORKER_TYPES) doesn't
    silently regress."""
    src = inspect.getsource(centella.phase_reconcile)
    assert 'models["reconciler"]' in src


def test_phase_reconcile_uses_reconciler_prompt(centella):
    """The system prompt comes from prompts/reconciler.md."""
    src = inspect.getsource(centella.phase_reconcile)
    assert '"reconciler.md"' in src


def test_phase_reconcile_dies_on_unresolvable(centella):
    """When the reconciler returns a non-empty `unresolvable` array, the
    orchestrator dies with the worker's reasoning. Pin the call to
    die() and the structural shape."""
    src = inspect.getsource(centella.phase_reconcile)
    # die() must be called inside an unresolvable check.
    assert "unresolvable" in src
    assert "die(" in src
    # Specifically: dies BEFORE mutating anything, so phantom edits
    # aren't left on disk. Pin by looking for the unresolvable check
    # appearing before the _apply_reconciler_output call.
    unresolvable_pos = src.find('unresolvable = output.get("unresolvable"')
    apply_pos = src.find("_apply_reconciler_output(plans, output)")
    assert unresolvable_pos != -1 and apply_pos != -1
    assert unresolvable_pos < apply_pos, (
        "unresolvable check must run BEFORE _apply_reconciler_output "
        "so a fail-closed run leaves no phantom mutations"
    )


def test_phase_reconcile_second_pass_check_present(centella):
    """After applying the reconciler's output, phase_reconcile re-runs
    `_compute_unresolved_requires` to catch the case where an
    `added_subtask` itself has unresolved `requires`. Pin so a future
    refactor can't silently regress to the single-pass behavior."""
    src = inspect.getsource(centella.phase_reconcile)
    # The function should call _compute_unresolved_requires twice:
    # once at the start (to short-circuit) and once after applying.
    count = src.count("_compute_unresolved_requires(plans)")
    assert count >= 2, (
        f"phase_reconcile should call _compute_unresolved_requires twice "
        f"(initial check + second-pass after applying reconciler output), "
        f"found {count}"
    )


def test_phase_reconcile_bumps_workers(centella):
    """Worker invocation must go through st.bump_workers to count
    against max_total_workers. Pin so the reconciler counts toward the
    cap (and budget).

    Note: short-circuit path doesn't bump (no worker spawned)."""
    src = inspect.getsource(centella.phase_reconcile)
    assert "st.bump_workers(caps)" in src


def test_phase_reconcile_uses_sid_reconciler(centella):
    """The worker's sid (used for logs and .centella/logs/<sid>.log) is
    'reconciler'. Pin so the log file lookup is stable."""
    src = inspect.getsource(centella.phase_reconcile)
    assert 'sid="reconciler"' in src
