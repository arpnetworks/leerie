"""Tests for dead-subtask elimination (_prune_dead_subtasks).

DESIGN §5: when at least one domain has 0 subtasks and the reconciler
marks requires tags as unresolvable, subtasks whose EVERY in_plan
requires is unresolvable are "fully speculative" and pruned mechanically.
"""
from __future__ import annotations


def _plan(domain: str, subtasks: list[dict]) -> dict:
    return {"domain": domain, "status": "ready", "subtasks": subtasks}


def _subtask(sid: str, requires: list[dict] | None = None,
             provides: list[str] | None = None,
             depends_on: list[str] | None = None) -> dict:
    return {
        "id": sid,
        "title": f"subtask {sid}",
        "intent": "do something",
        "scope_note": "",
        "files_likely_touched": [],
        "depends_on": depends_on or [],
        "requires": requires or [],
        "provides": provides or [],
        "success_criteria_seed": "done",
        "size": "small",
        "investigation_notes": "",
    }


def _in_plan(tag: str) -> dict:
    return {"tag": tag, "extent": "in_plan"}


def _unresolvable(sid: str, tag: str) -> dict:
    return {"sid": sid, "tag": tag, "reason": "no provider"}


def test_prune_all_requires_unresolvable(leerie):
    """Subtask with 2 in_plan requires, both unresolvable → pruned."""
    plans = [
        _plan("refactoring", []),
        _plan("testing", [
            _subtask("test-001", provides=["baseline-green"]),
            _subtask("test-002",
                     requires=[_in_plan("extracted"), _in_plan("migrated")]),
        ]),
    ]
    unresolvable = [
        _unresolvable("test-002", "extracted"),
        _unresolvable("test-002", "migrated"),
    ]
    pruned = leerie._prune_dead_subtasks(plans, unresolvable)
    assert pruned == ["test-002"]
    assert len(plans[1]["subtasks"]) == 1
    assert plans[1]["subtasks"][0]["id"] == "test-001"


def test_prune_partial_requires_not_pruned(leerie):
    """Subtask with 2 in_plan requires, only 1 unresolvable → NOT pruned."""
    plans = [
        _plan("refactoring", []),
        _plan("testing", [
            _subtask("test-001",
                     requires=[_in_plan("tag-a"), _in_plan("tag-b")],
                     provides=["result"]),
        ]),
    ]
    unresolvable = [_unresolvable("test-001", "tag-a")]
    pruned = leerie._prune_dead_subtasks(plans, unresolvable)
    assert pruned == []
    assert len(plans[1]["subtasks"]) == 1


def test_prune_no_empty_domain_skips(leerie):
    """No domain has 0 subtasks → no pruning even if unresolvable."""
    plans = [
        _plan("refactoring", [
            _subtask("refactor-001", provides=["something"]),
        ]),
        _plan("testing", [
            _subtask("test-001",
                     requires=[_in_plan("missing-tag")]),
        ]),
    ]
    unresolvable = [_unresolvable("test-001", "missing-tag")]
    pruned = leerie._prune_dead_subtasks(plans, unresolvable)
    assert pruned == []
    assert len(plans[1]["subtasks"]) == 1


def test_prune_no_in_plan_requires_skips(leerie):
    """Subtask with no in_plan requires → not pruned even if sid is
    in the unresolvable set (edge case: sid appears for a non-in_plan
    reason)."""
    plans = [
        _plan("refactoring", []),
        _plan("testing", [
            _subtask("test-001", provides=["baseline"]),
        ]),
    ]
    unresolvable = [_unresolvable("test-001", "phantom")]
    pruned = leerie._prune_dead_subtasks(plans, unresolvable)
    assert pruned == []
    assert len(plans[1]["subtasks"]) == 1


def test_prune_depends_on_cleanup(leerie):
    """Pruning a subtask removes it from surviving subtasks' depends_on."""
    plans = [
        _plan("refactoring", []),
        _plan("testing", [
            _subtask("test-001", provides=["baseline"]),
            _subtask("test-002",
                     requires=[_in_plan("extracted")]),
            _subtask("test-003",
                     depends_on=["test-001", "test-002"],
                     provides=["final"]),
        ]),
    ]
    unresolvable = [_unresolvable("test-002", "extracted")]
    pruned = leerie._prune_dead_subtasks(plans, unresolvable)
    assert pruned == ["test-002"]
    surviving = {s["id"]: s for s in plans[1]["subtasks"]}
    assert "test-002" not in surviving
    assert surviving["test-003"]["depends_on"] == ["test-001"]


def test_prune_mixed_domains(leerie):
    """Only fully-speculative subtasks pruned; others untouched."""
    plans = [
        _plan("refactoring", []),
        _plan("testing", [
            _subtask("test-001", provides=["baseline"]),
            _subtask("test-002",
                     requires=[_in_plan("extracted")]),
            _subtask("test-003",
                     requires=[_in_plan("baseline")],
                     provides=["guarded"]),
        ]),
    ]
    unresolvable = [_unresolvable("test-002", "extracted")]
    pruned = leerie._prune_dead_subtasks(plans, unresolvable)
    assert pruned == ["test-002"]
    surviving_ids = [s["id"] for s in plans[1]["subtasks"]]
    assert surviving_ids == ["test-001", "test-003"]


def test_prune_returns_sorted_sids(leerie):
    """Return value is sorted list of pruned sids."""
    plans = [
        _plan("refactoring", []),
        _plan("testing", [
            _subtask("test-003", requires=[_in_plan("c")]),
            _subtask("test-001", requires=[_in_plan("a")]),
            _subtask("test-002", requires=[_in_plan("b")]),
        ]),
    ]
    unresolvable = [
        _unresolvable("test-003", "c"),
        _unresolvable("test-001", "a"),
        _unresolvable("test-002", "b"),
    ]
    pruned = leerie._prune_dead_subtasks(plans, unresolvable)
    assert pruned == ["test-001", "test-002", "test-003"]


def test_source_text_pins(leerie):
    """Source-text pins: function and audit key exist in leerie.py."""
    import inspect
    source = inspect.getsource(leerie)
    assert "_prune_dead_subtasks" in source
    assert "speculative_collapse_drops" in source
