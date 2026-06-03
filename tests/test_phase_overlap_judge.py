"""Tests for `phase_overlap_judge` and its helpers — the phase 2¾
plan-overlap judge (DESIGN §5 *Cross-domain surface overlap*).

Covers the SCHEMAS["plan_overlap_judge"] contract, the
_validate_overlap_judge_output merge-feasibility backstop, and the two
pure apply functions `_apply_overlap_merge` and `_apply_overlap_drop`.
The async phase_overlap_judge wrapper itself is exercised indirectly
through its short-circuit conditions; the load-bearing logic lives in
the helpers and is easier to test directly.

Mirrors the test style of test_reconciler_schema.py +
test_apply_reconciler_output_*.py: extract the schema / call the pure
helper / reason over the result.
"""
from __future__ import annotations

import copy

import pytest


# --------------------------------------------------------------------- #
# Schema tests
# --------------------------------------------------------------------- #

def _valid_collision_merge() -> dict:
    return {
        "a_sid": "feat-001",
        "b_sid": "refactor-001",
        "artifact": "EmptyState primitive (src/components/features/empty-state.tsx)",
        "resolution": "merge",
        "reason": "Both create EmptyState in the same file with shared "
                  "provides tag empty-state-primitive.",
        "merge_feasibility": "Both intents can be satisfied by a single "
                             "EmptyState with optional icon/title/description/"
                             "CTA props.",
    }


def _valid_collision_drop_a() -> dict:
    return {
        "a_sid": "feat-008",
        "b_sid": "refactor-001",
        "artifact": "AuthShell component",
        "resolution": "drop_a",
        "reason": "feat-008 is superseded by the refactor-001 + refactor-002 "
                  "extract+adopt pair, which split the same scope cleanly.",
    }


def _valid_collision_unresolvable() -> dict:
    return {
        "a_sid": "feat-008",
        "b_sid": "refactor-001",
        "artifact": "AuthShell component",
        "resolution": "unresolvable",
        "reason": "feat-008's required {children}-only contract and "
                  "refactor-001's required `description` prop are "
                  "structurally incompatible.",
    }


def test_schema_exists(leerie):
    assert "plan_overlap_judge" in leerie.SCHEMAS


def test_schema_empty_collisions_valid(leerie):
    """The no-collision case is the common one — the judge must be able
    to return {collisions: []}."""
    import jsonschema
    jsonschema.validate({"collisions": []},
                        leerie.SCHEMAS["plan_overlap_judge"])


def test_schema_full_payload_valid(leerie):
    import jsonschema
    jsonschema.validate(
        {"collisions": [
            _valid_collision_merge(),
            _valid_collision_drop_a(),
            _valid_collision_unresolvable(),
        ]},
        leerie.SCHEMAS["plan_overlap_judge"])


def test_schema_rejects_unknown_resolution(leerie):
    import jsonschema
    bad = _valid_collision_drop_a()
    bad["resolution"] = "merge_or_split"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"collisions": [bad]},
                            leerie.SCHEMAS["plan_overlap_judge"])


def test_schema_rejects_extra_top_level_keys(leerie):
    import jsonschema
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            {"collisions": [], "extra": "nope"},
            leerie.SCHEMAS["plan_overlap_judge"])


def test_schema_requires_core_fields(leerie):
    import jsonschema
    incomplete = {"a_sid": "feat-001", "b_sid": "refactor-001",
                  "resolution": "merge"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"collisions": [incomplete]},
                            leerie.SCHEMAS["plan_overlap_judge"])


# --------------------------------------------------------------------- #
# _validate_overlap_judge_output (the merge-feasibility backstop)
# --------------------------------------------------------------------- #

def _by_id(subtasks):
    return {s["id"]: s for s in subtasks}


def test_validator_passes_on_drop_without_merge_feasibility(leerie):
    """drop_a/drop_b/unresolvable don't need merge_feasibility — only
    `merge` requires the discipline."""
    by_id = _by_id([
        {"id": "feat-008"}, {"id": "refactor-001"},
    ])
    leerie._validate_overlap_judge_output(
        {"collisions": [_valid_collision_drop_a()]}, by_id)


def test_validator_passes_on_unresolvable_without_merge_feasibility(leerie):
    by_id = _by_id([
        {"id": "feat-008"}, {"id": "refactor-001"},
    ])
    leerie._validate_overlap_judge_output(
        {"collisions": [_valid_collision_unresolvable()]}, by_id)


def test_validator_passes_on_merge_with_feasibility(leerie):
    by_id = _by_id([
        {"id": "feat-001"}, {"id": "refactor-001"},
    ])
    leerie._validate_overlap_judge_output(
        {"collisions": [_valid_collision_merge()]}, by_id)


def test_validator_dies_on_merge_without_feasibility(leerie, capsys):
    """The load-bearing case: a `merge` without a concrete
    merge_feasibility statement must die — auto-merging without the
    unified-intent would produce a frankenstein implementer spec."""
    bad = _valid_collision_merge()
    del bad["merge_feasibility"]
    by_id = _by_id([
        {"id": "feat-001"}, {"id": "refactor-001"},
    ])
    with pytest.raises(SystemExit):
        leerie._validate_overlap_judge_output(
            {"collisions": [bad]}, by_id)
    err = capsys.readouterr().err
    assert "merge_feasibility" in err
    assert "feat-001" in err
    assert "refactor-001" in err


def test_validator_dies_on_merge_with_blank_feasibility(leerie, capsys):
    """Empty / whitespace-only merge_feasibility is also rejected —
    the model could satisfy the schema by emitting ' ' but the
    discipline requires a concrete statement."""
    bad = _valid_collision_merge()
    bad["merge_feasibility"] = "   "
    by_id = _by_id([
        {"id": "feat-001"}, {"id": "refactor-001"},
    ])
    with pytest.raises(SystemExit):
        leerie._validate_overlap_judge_output(
            {"collisions": [bad]}, by_id)


def test_validator_dies_on_unknown_sid(leerie, capsys):
    bad = _valid_collision_drop_a()
    bad["a_sid"] = "ghost-001"
    by_id = _by_id([
        {"id": "feat-008"}, {"id": "refactor-001"},
    ])
    with pytest.raises(SystemExit):
        leerie._validate_overlap_judge_output(
            {"collisions": [bad]}, by_id)
    err = capsys.readouterr().err
    assert "ghost-001" in err


def test_validator_dies_on_self_collision(leerie, capsys):
    bad = _valid_collision_drop_a()
    bad["b_sid"] = bad["a_sid"]
    by_id = _by_id([
        {"id": bad["a_sid"]},
    ])
    with pytest.raises(SystemExit):
        leerie._validate_overlap_judge_output(
            {"collisions": [bad]}, by_id)


def test_validator_dies_on_duplicate_pair(leerie, capsys):
    """Two collisions on the same pair (even with different field
    order) would be incoherent — the model must pick one resolution
    per pair."""
    c1 = _valid_collision_drop_a()
    c2 = dict(c1)
    c2["a_sid"], c2["b_sid"] = c1["b_sid"], c1["a_sid"]  # swapped
    by_id = _by_id([
        {"id": c1["a_sid"]}, {"id": c1["b_sid"]},
    ])
    with pytest.raises(SystemExit):
        leerie._validate_overlap_judge_output(
            {"collisions": [c1, c2]}, by_id)


# --------------------------------------------------------------------- #
# _apply_overlap_drop
# --------------------------------------------------------------------- #

def _two_plans_basic():
    """Two plans, three subtasks: feat-008 + refactor-001 are the
    colliding pair; downstream-001 depends on feat-008."""
    return [
        {
            "domain": "feature-implementation",
            "subtasks": [
                {"id": "feat-008", "title": "Add AuthShell",
                 "intent": "...", "provides": ["auth-shell-adopted"],
                 "requires": [], "depends_on": [],
                 "files_likely_touched": ["src/auth-shell.tsx"],
                 "success_criteria_seed": "feat-008 criteria"},
                {"id": "downstream-001", "title": "Use AuthShell",
                 "intent": "...", "provides": [],
                 "requires": [{"tag": "auth-shell-adopted",
                               "extent": "in_plan"}],
                 "depends_on": ["feat-008"],
                 "files_likely_touched": [],
                 "success_criteria_seed": "downstream criteria"},
            ],
        },
        {
            "domain": "refactoring",
            "subtasks": [
                {"id": "refactor-001", "title": "Extract AuthShell",
                 "intent": "...", "provides": ["auth-shell-component"],
                 "requires": [], "depends_on": [],
                 "files_likely_touched": ["src/auth-shell.tsx"],
                 "success_criteria_seed": "refactor-001 criteria"},
            ],
        },
    ]


def test_apply_drop_removes_dropped_sid(leerie):
    plans = _two_plans_basic()
    leerie._apply_overlap_drop(plans, dropped_sid="feat-008",
                               surviving_sid="refactor-001")
    surviving = {s["id"] for plan in plans for s in plan["subtasks"]}
    assert "feat-008" not in surviving
    assert {"downstream-001", "refactor-001"} == surviving


def test_apply_drop_rewrites_downstream_depends_on(leerie):
    plans = _two_plans_basic()
    leerie._apply_overlap_drop(plans, dropped_sid="feat-008",
                               surviving_sid="refactor-001")
    downstream = next(s for plan in plans for s in plan["subtasks"]
                      if s["id"] == "downstream-001")
    assert "feat-008" not in downstream["depends_on"]
    assert "refactor-001" in downstream["depends_on"]


def test_apply_drop_silent_on_missing_sid(leerie):
    """Mirrors the conditional_drops apply step — dropping an unknown
    sid is a silent no-op, not a die. The validator catches truly
    unknown sids upstream."""
    plans = _two_plans_basic()
    before = copy.deepcopy(plans)
    leerie._apply_overlap_drop(plans, dropped_sid="ghost-999",
                               surviving_sid="refactor-001")
    assert plans == before


def test_apply_drop_unions_provides_to_survivor(leerie):
    """The dropped subtask's `provides` tags must be unioned into the
    survivor — otherwise downstream `requires` entries that matched
    the dropped subtask's tags become orphans that surface as a
    confusing `validate_plan` error instead of a clean plan-time
    resolution. This is the load-bearing fix from the self-review."""
    plans = _two_plans_basic()
    leerie._apply_overlap_drop(plans, dropped_sid="feat-008",
                               surviving_sid="refactor-001")
    survivor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "refactor-001")
    # feat-008 provided "auth-shell-adopted"; refactor-001 originally
    # provided "auth-shell-component"; post-drop the survivor must
    # provide both.
    assert "auth-shell-adopted" in survivor["provides"]
    assert "auth-shell-component" in survivor["provides"]


def test_apply_drop_resolves_orphan_downstream_requires(leerie):
    """End-to-end pin on the `0c4bab`-style failure mode: a downstream
    subtask requires a tag that only the dropped subtask provides;
    after the drop, that requirement must resolve against the
    surviving subtask's now-unioned provides — not orphan into a
    `validate_plan` error."""
    plans = [
        {"domain": "feature-implementation", "subtasks": [
            {"id": "feat-008", "title": "x", "intent": "x",
             "provides": ["auth-shell-adopted"], "requires": [],
             "depends_on": [], "files_likely_touched": [],
             "success_criteria_seed": "x"},
            {"id": "feat-011", "title": "consumer", "intent": "x",
             "provides": [], "requires": [
                 {"tag": "auth-shell-adopted", "extent": "in_plan"}],
             "depends_on": [], "files_likely_touched": [],
             "success_criteria_seed": "x"},
        ]},
        {"domain": "refactoring", "subtasks": [
            {"id": "refactor-001", "title": "x", "intent": "x",
             "provides": ["auth-shell-component"], "requires": [],
             "depends_on": [], "files_likely_touched": [],
             "success_criteria_seed": "x"},
        ]},
    ]
    leerie._apply_overlap_drop(plans, dropped_sid="feat-008",
                               surviving_sid="refactor-001")
    # Build the merged subtasks dict the way schedule()/validate_plan do.
    merged = {s["id"]: s for plan in plans for s in plan["subtasks"]}
    all_provides = {tag for s in merged.values()
                    for tag in s.get("provides", [])}
    consumer = merged["feat-011"]
    for entry in consumer["requires"]:
        if entry.get("extent") == "in_plan":
            assert entry["tag"] in all_provides, (
                f"orphan requires: {entry['tag']} not provided by any "
                "surviving subtask — _apply_overlap_drop failed to "
                "union dropped.provides into the survivor")


def test_apply_drop_drops_self_referencing_requires(leerie):
    """After unioning the dropped subtask's `provides` into the
    survivor, any `extent: in_plan` requires entry on the survivor
    whose tag is now in its own provides is a graph self-loop and
    must be removed. Mirrors the same cleanup in _apply_overlap_merge."""
    plans = _two_plans_basic()
    # Make refactor-001 require what feat-008 provides — after the
    # drop, the survivor (refactor-001) would self-loop if the cleanup
    # didn't fire.
    refactor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "refactor-001")
    refactor["requires"] = [
        {"tag": "auth-shell-adopted", "extent": "in_plan"}]
    leerie._apply_overlap_drop(plans, dropped_sid="feat-008",
                               surviving_sid="refactor-001")
    survivor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "refactor-001")
    assert "auth-shell-adopted" in survivor["provides"]
    # The self-loop requires entry must be gone.
    assert all(e.get("tag") != "auth-shell-adopted"
               for e in survivor["requires"]
               if isinstance(e, dict))


def test_apply_drop_preserves_external_requires_on_survivor(leerie):
    """External requires (out-of-graph) stay regardless of the
    provides union — they are deploy-time preconditions, not graph
    edges, so they can't be self-loops."""
    plans = _two_plans_basic()
    refactor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "refactor-001")
    refactor["requires"] = [
        {"tag": "auth-shell-adopted", "extent": "external",
         "reason": "out of graph"}]
    leerie._apply_overlap_drop(plans, dropped_sid="feat-008",
                               surviving_sid="refactor-001")
    survivor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "refactor-001")
    # External entry survives even though the tag is now in provides.
    assert any(e.get("tag") == "auth-shell-adopted"
               and e.get("extent") == "external"
               for e in survivor["requires"]
               if isinstance(e, dict))


def test_apply_drop_idempotent_provides_dedup(leerie):
    """If the survivor already provides one of the dropped tags, the
    union must not duplicate it."""
    plans = _two_plans_basic()
    # Pre-stamp refactor-001 with the same tag feat-008 provides.
    refactor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "refactor-001")
    refactor["provides"].append("auth-shell-adopted")
    leerie._apply_overlap_drop(plans, dropped_sid="feat-008",
                               surviving_sid="refactor-001")
    survivor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "refactor-001")
    # Exactly one occurrence, not two.
    assert survivor["provides"].count("auth-shell-adopted") == 1


# --------------------------------------------------------------------- #
# _apply_overlap_merge
# --------------------------------------------------------------------- #

def test_apply_merge_collapses_to_lex_smaller_sid(leerie):
    """Stable surviving-sid rule: lexicographically smaller wins.
    Calling with (a, b) and (b, a) must produce the same surviving sid."""
    plans1 = _two_plans_basic()
    surviving1 = leerie._apply_overlap_merge(
        plans1, "feat-008", "refactor-001",
        artifact="AuthShell component",
        merge_feasibility="Unified API: optional description prop.")
    plans2 = _two_plans_basic()
    surviving2 = leerie._apply_overlap_merge(
        plans2, "refactor-001", "feat-008",
        artifact="AuthShell component",
        merge_feasibility="Unified API: optional description prop.")
    assert surviving1 == surviving2 == "feat-008"  # lex-smaller


def test_apply_merge_unions_files_provides_requires(leerie):
    plans = _two_plans_basic()
    # Add a distinct file + require + depends to refactor-001 so we
    # can confirm union semantics.
    refactor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "refactor-001")
    refactor["files_likely_touched"].append("src/auth-shell.test.tsx")
    refactor["provides"].append("extra-tag")
    refactor["requires"] = [
        {"tag": "brand-tokens", "extent": "external",
         "reason": "globals.css"}]
    leerie._apply_overlap_merge(
        plans, "feat-008", "refactor-001",
        artifact="AuthShell",
        merge_feasibility="Unified.")
    survivor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "feat-008")
    assert set(survivor["files_likely_touched"]) == {
        "src/auth-shell.tsx", "src/auth-shell.test.tsx"}
    assert set(survivor["provides"]) == {
        "auth-shell-adopted", "auth-shell-component", "extra-tag"}
    # external requires survive (out-of-graph; not a self-loop)
    assert any(e.get("tag") == "brand-tokens"
               for e in survivor["requires"])


def test_apply_merge_drops_self_referencing_requires(leerie):
    """If the merged unit's `provides` now covers a requires tag from
    either half, that requires entry becomes a self-loop and must be
    dropped."""
    plans = _two_plans_basic()
    # Make feat-008 require what refactor-001 provides → after merge,
    # the merged unit provides both, so the requires entry becomes a
    # self-loop.
    feat = next(s for plan in plans for s in plan["subtasks"]
                if s["id"] == "feat-008")
    feat["requires"] = [
        {"tag": "auth-shell-component", "extent": "in_plan"}]
    leerie._apply_overlap_merge(
        plans, "feat-008", "refactor-001",
        artifact="AuthShell",
        merge_feasibility="Unified.")
    survivor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "feat-008")
    assert all(e.get("tag") != "auth-shell-component"
               for e in survivor["requires"]
               if isinstance(e, dict))


def test_apply_merge_writes_feasibility_into_intent(leerie):
    plans = _two_plans_basic()
    feasibility = ("Both can be satisfied by a brand-styled AuthShell "
                   "with optional description prop.")
    leerie._apply_overlap_merge(
        plans, "feat-008", "refactor-001",
        artifact="AuthShell component",
        merge_feasibility=feasibility)
    survivor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "feat-008")
    assert feasibility in survivor["intent"]
    assert "Merged with refactor-001 by plan-overlap-judge" in survivor["intent"]
    assert "AuthShell component" in survivor["intent"]


def test_apply_merge_concatenates_success_criteria(leerie):
    plans = _two_plans_basic()
    leerie._apply_overlap_merge(
        plans, "feat-008", "refactor-001",
        artifact="AuthShell", merge_feasibility="Unified.")
    survivor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "feat-008")
    assert "feat-008 criteria" in survivor["success_criteria_seed"]
    assert "refactor-001 criteria" in survivor["success_criteria_seed"]
    assert " AND " in survivor["success_criteria_seed"]


def test_apply_merge_rewrites_downstream_depends_on(leerie):
    plans = _two_plans_basic()
    leerie._apply_overlap_merge(
        plans, "feat-008", "refactor-001",
        artifact="AuthShell", merge_feasibility="Unified.")
    downstream = next(s for plan in plans for s in plan["subtasks"]
                      if s["id"] == "downstream-001")
    # feat-008 is the survivor (lex-smaller), so downstream-001's
    # depends_on stays pointing at feat-008.
    assert downstream["depends_on"] == ["feat-008"]


def test_apply_merge_stamps_merged_from(leerie):
    plans = _two_plans_basic()
    leerie._apply_overlap_merge(
        plans, "feat-008", "refactor-001",
        artifact="AuthShell", merge_feasibility="Unified.")
    survivor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "feat-008")
    assert survivor.get("_merged_from") == ["refactor-001"]


def test_apply_merge_die_on_missing_sid(leerie, capsys):
    plans = _two_plans_basic()
    with pytest.raises(SystemExit):
        leerie._apply_overlap_merge(
            plans, "feat-008", "ghost-999",
            artifact="X", merge_feasibility="Unified.")


# --------------------------------------------------------------------- #
# Idempotence — applying the same merge twice is a noop on the second
# pass (the absorbed sid is already gone; the survivor's `_merged_from`
# already lists it). Pin the invariant.
# --------------------------------------------------------------------- #

def test_apply_merge_then_drop_idempotence(leerie):
    """A run that re-applies a previously-applied merge (e.g. resume)
    must not silently double-stamp _merged_from."""
    plans = _two_plans_basic()
    leerie._apply_overlap_merge(
        plans, "feat-008", "refactor-001",
        artifact="X", merge_feasibility="Unified.")
    survivor = next(s for plan in plans for s in plan["subtasks"]
                    if s["id"] == "feat-008")
    assert survivor.get("_merged_from") == ["refactor-001"]
    # Re-applying with the dropped sid no longer present — the
    # validator would catch this upstream, but the helper's missing-sid
    # die() makes it explicit.
    with pytest.raises(SystemExit):
        leerie._apply_overlap_merge(
            plans, "feat-008", "refactor-001",
            artifact="X", merge_feasibility="Unified.")
