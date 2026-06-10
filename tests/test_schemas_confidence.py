"""Structural tests for the confidence/status fields on all worker schemas
(DESIGN §8).

The point of pinning these structural contracts is mechanical enforcement
of DESIGN §12 / §8: a worker that skipped self-gating fails its own JSON
schema before the orchestrator sees the payload. The schema's
required-ness of the discipline fields is the structural part of the
gate; the quality of each field's content is model-judged. If a future
change removes one of these fields without an accompanying DESIGN update,
this test catches it.
"""
from __future__ import annotations

import pytest


def test_planner_schema_top_level_required(leerie):
    """Planner must emit domain, subtasks, status, and confidence."""
    planner = leerie.SCHEMAS["planner"]
    required = set(planner["required"])
    assert {"domain", "subtasks", "status", "confidence"}.issubset(required)


def test_planner_schema_status_enum(leerie):
    """status is the ready/blocked enum."""
    status = leerie.SCHEMAS["planner"]["properties"]["status"]
    assert status["type"] == "string"
    assert set(status["enum"]) == {"ready", "blocked"}


def test_planner_schema_confidence_required_fields(leerie):
    """The four discipline fields are required-when-confidence-is-present.
    Combined with confidence being top-level required, a planner that
    skipped any of them fails its own schema."""
    conf = leerie.SCHEMAS["planner"]["properties"]["confidence"]
    assert conf["type"] == "object"
    required = set(conf["required"])
    expected = {"task_understanding", "decomposition_quality", "basis",
                "falsifiers_tested", "contradictions_reconciled",
                "gap_to_close"}
    assert expected.issubset(required)


def test_planner_confidence_axes_are_numbers(leerie):
    props = leerie.SCHEMAS["planner"]["properties"]["confidence"]["properties"]
    assert props["task_understanding"]["type"] == "number"
    assert props["decomposition_quality"]["type"] == "number"


def test_implementer_schema_top_level_required(leerie):
    """Implementer must emit subtask_id, status, and confidence."""
    impl = leerie.SCHEMAS["implementer"]
    required = set(impl["required"])
    assert {"subtask_id", "status", "confidence"}.issubset(required)


def test_implementer_schema_confidence_required_fields(leerie):
    """The implementer's confidence object must require the same
    discipline fields as the planner's (DESIGN §8 — same disciplines,
    different axes)."""
    conf = leerie.SCHEMAS["implementer"]["properties"]["confidence"]
    assert conf["type"] == "object"
    required = set(conf["required"])
    expected = {"root_cause", "solution", "basis",
                "falsifiers_tested", "contradictions_reconciled",
                "gap_to_close"}
    assert expected.issubset(required)


def test_implementer_confidence_axes_are_numbers(leerie):
    props = leerie.SCHEMAS["implementer"]["properties"]["confidence"]["properties"]
    assert props["root_cause"]["type"] == "number"
    assert props["solution"]["type"] == "number"


def test_conformer_schema_top_level_required(leerie):
    """Conformer must emit confidence (the §8 self-gate). Same
    structural enforcement as planner/implementer — the orchestrator
    does not read it, but the schema rejects payloads that skip it."""
    conf = leerie.SCHEMAS["conformer"]
    required = set(conf["required"])
    assert "confidence" in required


def test_conformer_schema_confidence_required_fields(leerie):
    """The conformer's confidence object must require the same
    discipline fields as planner/implementer (DESIGN §8 — same
    disciplines, different axes)."""
    conf = leerie.SCHEMAS["conformer"]["properties"]["confidence"]
    assert conf["type"] == "object"
    required = set(conf["required"])
    expected = {"conformance", "basis", "falsifiers_tested",
                "contradictions_reconciled", "gap_to_close"}
    assert expected.issubset(required)


def test_gap_to_close_keys_match_score_axes(leerie):
    """The gap_to_close sub-object's keys mirror the score axes so a
    below-threshold score has a clear field to fill. Catches future
    drift where someone renames an axis without updating the gap
    field."""
    planner_gap = leerie.SCHEMAS["planner"]["properties"]["confidence"]["properties"]["gap_to_close"]
    assert set(planner_gap["properties"].keys()) == {
        "task_understanding", "decomposition_quality"}
    impl_gap = leerie.SCHEMAS["implementer"]["properties"]["confidence"]["properties"]["gap_to_close"]
    assert set(impl_gap["properties"].keys()) == {"root_cause", "solution"}
    conformer_gap = leerie.SCHEMAS["conformer"]["properties"]["confidence"]["properties"]["gap_to_close"]
    assert set(conformer_gap["properties"].keys()) == {"conformance"}


# --- New schemas: classifier, reconciler, provision, overlap judge, integrator ---

_DISCIPLINE_FIELDS = {"basis", "falsifiers_tested",
                      "contradictions_reconciled", "gap_to_close"}


def _assert_confidence_schema(leerie, schema_key: str, axes: list[str]):
    """Shared structural assertions for any confidence schema."""
    schema = leerie.SCHEMAS[schema_key]
    assert "confidence" in set(schema["required"]), (
        f"{schema_key} must require confidence at the top level")
    conf = schema["properties"]["confidence"]
    assert conf["type"] == "object"
    required = set(conf["required"])
    assert _DISCIPLINE_FIELDS.issubset(required), (
        f"{schema_key} confidence missing discipline fields: "
        f"{_DISCIPLINE_FIELDS - required}")
    for ax in axes:
        assert ax in required, f"{schema_key} confidence missing axis {ax!r}"
        assert conf["properties"][ax]["type"] == "number", (
            f"{schema_key} confidence.{ax} must be a number")
    gap = conf["properties"]["gap_to_close"]
    assert set(gap["properties"].keys()) == set(axes), (
        f"{schema_key} gap_to_close keys must mirror axes")


@pytest.mark.parametrize("schema_key, axes", [
    ("classifier", ["classification"]),
    ("reconciler", ["reconciliation"]),
    ("provision", ["recipe_correctness"]),
    ("plan_overlap_judge", ["judgment"]),
    ("integrator", ["resolution"]),
])
def test_new_schema_confidence_structure(leerie, schema_key, axes):
    """Every worker schema has a required confidence object with the §8
    discipline fields and worker-specific numeric score axes."""
    _assert_confidence_schema(leerie, schema_key, axes)


def test_confidence_schema_helper_produces_correct_structure(leerie):
    """The _confidence_schema helper builds the same shape regardless
    of the number of axes."""
    single = leerie._confidence_schema(["x"])
    assert set(single["required"]) == {"x", "basis", "falsifiers_tested",
                                        "contradictions_reconciled",
                                        "gap_to_close"}
    assert single["properties"]["x"]["type"] == "number"
    assert set(single["properties"]["gap_to_close"]["properties"].keys()) == {"x"}

    multi = leerie._confidence_schema(["a", "b", "c"])
    assert {"a", "b", "c"}.issubset(set(multi["required"]))
    for ax in ("a", "b", "c"):
        assert multi["properties"][ax]["type"] == "number"
    assert set(multi["properties"]["gap_to_close"]["properties"].keys()) == {
        "a", "b", "c"}
