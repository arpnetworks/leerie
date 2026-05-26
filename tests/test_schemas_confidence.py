"""Structural tests for the confidence/status fields added to the planner
and implementer schemas (DESIGN §8).

The point of pinning these structural contracts is mechanical enforcement
of DESIGN §12 / §8: a worker that skipped self-gating fails its own JSON
schema before the orchestrator sees the payload. The schema's
required-ness of the discipline fields is the structural part of the
gate; the quality of each field's content is model-judged. If a future
change removes one of these fields without an accompanying DESIGN update,
this test catches it.
"""
from __future__ import annotations


def test_planner_schema_top_level_required(centella):
    """Planner must emit domain, subtasks, status, and confidence."""
    planner = centella.SCHEMAS["planner"]
    required = set(planner["required"])
    assert {"domain", "subtasks", "status", "confidence"}.issubset(required)


def test_planner_schema_status_enum(centella):
    """status is the ready/blocked enum."""
    status = centella.SCHEMAS["planner"]["properties"]["status"]
    assert status["type"] == "string"
    assert set(status["enum"]) == {"ready", "blocked"}


def test_planner_schema_confidence_required_fields(centella):
    """The four discipline fields are required-when-confidence-is-present.
    Combined with confidence being top-level required, a planner that
    skipped any of them fails its own schema."""
    conf = centella.SCHEMAS["planner"]["properties"]["confidence"]
    assert conf["type"] == "object"
    required = set(conf["required"])
    expected = {"task_understanding", "decomposition_quality", "basis",
                "falsifiers_tested", "contradictions_reconciled",
                "gap_to_close"}
    assert expected.issubset(required)


def test_planner_confidence_axes_are_numbers(centella):
    props = centella.SCHEMAS["planner"]["properties"]["confidence"]["properties"]
    assert props["task_understanding"]["type"] == "number"
    assert props["decomposition_quality"]["type"] == "number"


def test_implementer_schema_top_level_required(centella):
    """Implementer must emit subtask_id, status, and confidence."""
    impl = centella.SCHEMAS["implementer"]
    required = set(impl["required"])
    assert {"subtask_id", "status", "confidence"}.issubset(required)


def test_implementer_schema_confidence_required_fields(centella):
    """The implementer's confidence object must require the same
    discipline fields as the planner's (DESIGN §8 — same disciplines,
    different axes)."""
    conf = centella.SCHEMAS["implementer"]["properties"]["confidence"]
    assert conf["type"] == "object"
    required = set(conf["required"])
    expected = {"root_cause", "solution", "basis",
                "falsifiers_tested", "contradictions_reconciled",
                "gap_to_close"}
    assert expected.issubset(required)


def test_implementer_confidence_axes_are_numbers(centella):
    props = centella.SCHEMAS["implementer"]["properties"]["confidence"]["properties"]
    assert props["root_cause"]["type"] == "number"
    assert props["solution"]["type"] == "number"


def test_gap_to_close_keys_match_score_axes(centella):
    """The gap_to_close sub-object's keys mirror the score axes so a
    below-threshold score has a clear field to fill. Catches future
    drift where someone renames an axis without updating the gap
    field."""
    planner_gap = centella.SCHEMAS["planner"]["properties"]["confidence"]["properties"]["gap_to_close"]
    assert set(planner_gap["properties"].keys()) == {
        "task_understanding", "decomposition_quality"}
    impl_gap = centella.SCHEMAS["implementer"]["properties"]["confidence"]["properties"]["gap_to_close"]
    assert set(impl_gap["properties"].keys()) == {"root_cause", "solution"}
