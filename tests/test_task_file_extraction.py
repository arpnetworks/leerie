"""Tests for task-referenced file extraction and coverage checking.

Covers ``glob_task_references``, ``extract_task_file_structure``,
``check_task_file_coverage``, and ``_format_task_file_structure``.
"""
from __future__ import annotations

from pathlib import Path


# --- glob_task_references ------------------------------------------------ #

class TestExpandBraces:
    def test_no_braces(self, leerie):
        assert leerie._expand_braces("foo.md") == ["foo.md"]

    def test_simple_braces(self, leerie):
        result = leerie._expand_braces("spec.{md,yaml}")
        assert sorted(result) == ["spec.md", "spec.yaml"]

    def test_braces_with_glob(self, leerie):
        result = leerie._expand_braces("spec-*.{md,yaml}")
        assert sorted(result) == ["spec-*.md", "spec-*.yaml"]

    def test_three_alternatives(self, leerie):
        result = leerie._expand_braces("f.{a,b,c}")
        assert sorted(result) == ["f.a", "f.b", "f.c"]


class TestGlobTaskReferences:
    def test_no_file_refs(self, leerie, tmp_path):
        assert leerie.glob_task_references(
            "fix the login bug", tmp_path) == []

    def test_explicit_md_file(self, leerie, tmp_path):
        (tmp_path / "spec.md").write_text("# Spec\n")
        result = leerie.glob_task_references(
            "implement everything in spec.md", tmp_path)
        assert len(result) == 1
        assert result[0].name == "spec.md"

    def test_glob_pattern(self, leerie, tmp_path):
        (tmp_path / "plan-a.md").write_text("# A\n")
        (tmp_path / "plan-b.md").write_text("# B\n")
        (tmp_path / "plan-c.txt").write_text("C\n")
        result = leerie.glob_task_references(
            "check plan-*.md files", tmp_path)
        assert len(result) == 2

    def test_yaml_file(self, leerie, tmp_path):
        (tmp_path / "tasks.yaml").write_text("- id: t1\n")
        result = leerie.glob_task_references(
            "complete tasks.yaml", tmp_path)
        assert len(result) == 1

    def test_nonexistent_file(self, leerie, tmp_path):
        result = leerie.glob_task_references(
            "fix missing.py", tmp_path)
        assert result == []

    def test_brace_expansion(self, leerie, tmp_path):
        (tmp_path / "plan.md").write_text("# Plan\n")
        (tmp_path / "plan.yaml").write_text("- id: t1\n")
        (tmp_path / "plan.txt").write_text("ignored\n")
        result = leerie.glob_task_references(
            "check plan.{md,yaml}", tmp_path)
        assert len(result) == 2
        names = {p.name for p in result}
        assert names == {"plan.md", "plan.yaml"}

    def test_brace_expansion_with_glob(self, leerie, tmp_path):
        (tmp_path / "spec-a.md").write_text("# A\n")
        (tmp_path / "spec-b.yaml").write_text("- id: b\n")
        result = leerie.glob_task_references(
            "check spec-*.{md,yaml}", tmp_path)
        assert len(result) == 2

    def test_deduplication(self, leerie, tmp_path):
        (tmp_path / "spec.md").write_text("# Spec\n")
        result = leerie.glob_task_references(
            "check spec.md and also spec.md again", tmp_path)
        assert len(result) == 1


# --- extract_task_file_structure ---------------------------------------- #

class TestExtractTaskFileStructure:
    def test_no_files_returns_none(self, leerie, tmp_path):
        assert leerie.extract_task_file_structure(
            "fix the bug", tmp_path) is None

    def test_markdown_headings_h3_plus(self, leerie, tmp_path):
        (tmp_path / "spec.md").write_text(
            "# Overview\n## Details\n### Deep\n#### Deeper\nSome text\n")
        items = leerie.extract_task_file_structure(
            "check spec.md", tmp_path)
        assert items is not None
        assert not any("Overview" in i for i in items)
        assert not any("Details" in i for i in items)
        assert any("Deep" in i for i in items)
        assert any("Deeper" in i for i in items)

    def test_numbered_items(self, leerie, tmp_path):
        (tmp_path / "plan.md").write_text(
            "1. First step\n2. Second step\nNot numbered\n")
        items = leerie.extract_task_file_structure(
            "implement plan.md", tmp_path)
        assert items is not None
        assert any("First step" in i for i in items)
        assert any("Second step" in i for i in items)

    def test_toc_links_excluded(self, leerie, tmp_path):
        (tmp_path / "spec.md").write_text(
            "1. [Overview](#overview)\n2. Real item\n"
            "3. [Details](#details)\n")
        items = leerie.extract_task_file_structure(
            "review spec.md", tmp_path)
        assert items is not None
        assert not any("Overview" in i for i in items)
        assert not any("Details" in i for i in items)
        assert any("Real item" in i for i in items)

    def test_yaml_list_ids(self, leerie, tmp_path):
        (tmp_path / "jobs.yaml").write_text(
            "- id: wave-0\n  name: first\n- id: wave-1\n  name: second\n")
        items = leerie.extract_task_file_structure(
            "complete jobs.yaml", tmp_path)
        assert items is not None
        assert any("wave-0" in i for i in items)
        assert any("wave-1" in i for i in items)

    def test_yaml_top_level_keys(self, leerie, tmp_path):
        (tmp_path / "config.yaml").write_text(
            "database:\n  host: localhost\nredis:\n  port: 6379\n")
        items = leerie.extract_task_file_structure(
            "audit config.yaml", tmp_path)
        assert items is not None
        assert any("database" in i for i in items)
        assert any("redis" in i for i in items)

    def test_empty_file_returns_none(self, leerie, tmp_path):
        (tmp_path / "empty.md").write_text("")
        assert leerie.extract_task_file_structure(
            "check empty.md", tmp_path) is None


# --- check_task_file_coverage ------------------------------------------- #

class TestCheckTaskFileCoverage:
    def test_full_coverage(self, leerie):
        extracted = ["spec.md: Overview", "spec.md: Details"]
        subtasks = [
            {"title": "Fix overview", "intent": "Overview fix",
             "investigation_notes": ""},
            {"title": "Fix details", "intent": "Details fix",
             "investigation_notes": ""},
        ]
        assert leerie.check_task_file_coverage(extracted, subtasks) == []

    def test_low_coverage(self, leerie):
        extracted = ["spec.md: A", "spec.md: B", "spec.md: C",
                     "spec.md: D"]
        subtasks = [{"title": "Fix A", "intent": "A",
                     "investigation_notes": ""}]
        issues = leerie.check_task_file_coverage(extracted, subtasks)
        assert any("LOW_COVERAGE" in i for i in issues)

    def test_empty_extracted(self, leerie):
        assert leerie.check_task_file_coverage([], []) == []

    def test_just_above_threshold(self, leerie):
        extracted = ["a: X", "a: Y"]
        subtasks = [{"title": "covers X", "intent": "X",
                     "investigation_notes": ""}]
        # 1/2 uncovered = 50%, which is the threshold — should not fire
        assert leerie.check_task_file_coverage(extracted, subtasks) == []

    def test_over_threshold(self, leerie):
        extracted = ["a: X", "a: Y", "a: Z"]
        subtasks = [{"title": "covers X", "intent": "X",
                     "investigation_notes": ""}]
        # 2/3 uncovered = 66% > 50%
        issues = leerie.check_task_file_coverage(extracted, subtasks)
        assert any("LOW_COVERAGE" in i for i in issues)

    def test_skipped_when_too_many_items(self, leerie):
        extracted = [f"spec.md: item-{i}" for i in range(51)]
        subtasks = [{"title": "fix one", "intent": "item-0",
                     "investigation_notes": ""}]
        assert leerie.check_task_file_coverage(extracted, subtasks) == []

    def test_gates_when_under_cap(self, leerie):
        extracted = [f"spec.md: item-{i}" for i in range(50)]
        subtasks = [{"title": "fix one", "intent": "item-0",
                     "investigation_notes": ""}]
        issues = leerie.check_task_file_coverage(extracted, subtasks)
        assert any("LOW_COVERAGE" in i for i in issues)


# --- _format_task_file_structure ---------------------------------------- #

class TestFormatTaskFileStructure:
    def test_format(self, leerie):
        items = ["spec.md: Overview", "spec.md: Details"]
        result = leerie._format_task_file_structure(items)
        assert "mechanically extracted" in result
        assert "Overview" in result
        assert "coverage checklist" in result
