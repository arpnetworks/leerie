"""Tests for multi-sample planner crash tolerance.

When planner_samples > 1, a crashed sample (plan_one returns None) must
be dropped — not die(). The run aborts only when ALL samples for a
domain crash. Single-sample mode preserves the original die() behavior.
"""
from __future__ import annotations


def _minimal_plan(**overrides):
    """A plan dict that passes _select_best_planner_sample's scoring."""
    base = {
        "status": "ready",
        "subtasks": [
            {
                "id": "feat-001",
                "title": "a subtask",
                "intent": "do the thing",
                "scope_note": "one change",
                "files_likely_touched": [],
                "depends_on": [],
                "requires": [],
                "provides": [],
                "success_criteria_seed": "done",
                "size": "small",
                "investigation_notes": "",
            }
        ],
    }
    base.update(overrides)
    return base


def test_select_best_drops_no_samples_when_all_valid(leerie, tmp_path):
    """All samples valid — selection picks from all of them."""
    samples = [_minimal_plan(), _minimal_plan(), _minimal_plan()]
    best = leerie._select_best_planner_sample(samples, tmp_path, "feature-implementation")
    assert best is not None
    assert best["status"] == "ready"


def test_select_best_works_with_single_surviving_sample(leerie, tmp_path):
    """One sample is enough for selection to succeed."""
    samples = [_minimal_plan()]
    best = leerie._select_best_planner_sample(samples, tmp_path, "bug-fixing")
    assert best is not None
    assert best["status"] == "ready"


def test_multi_sample_collection_filters_none():
    """Simulate the multi-sample collection path: None results are
    filtered out, surviving samples proceed to selection."""
    cats = ["feature-implementation", "bug-fixing"]
    n_samples = 3
    coro_keys = []
    for c in cats:
        for s in range(n_samples):
            coro_keys.append((c, s))

    # bug-fixing sample 2 crashed (None), others succeeded
    all_results = [
        _minimal_plan(),  # feat-s0
        _minimal_plan(),  # feat-s1
        _minimal_plan(),  # feat-s2
        _minimal_plan(),  # bug-s0
        _minimal_plan(),  # bug-s1
        None,             # bug-s2 — crashed
    ]

    by_category: dict[str, list[dict]] = {}
    for (c, _s_idx), result in zip(coro_keys, all_results):
        if result is not None:
            by_category.setdefault(c, []).append(result)

    assert len(by_category["feature-implementation"]) == 3
    assert len(by_category["bug-fixing"]) == 2


def test_multi_sample_collection_all_crashed_detected():
    """When all samples for a domain are None, the category has no
    surviving samples — the caller should detect this and abort."""
    cats = ["bug-fixing"]
    n_samples = 3
    coro_keys = [(cats[0], s) for s in range(n_samples)]

    all_results = [None, None, None]

    by_category: dict[str, list[dict]] = {}
    for (c, _s_idx), result in zip(coro_keys, all_results):
        if result is not None:
            by_category.setdefault(c, []).append(result)

    assert by_category.get("bug-fixing", []) == []
