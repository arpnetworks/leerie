"""Tests for migration-surface completeness checks (DESIGN §5).

Two layers:
1. _check_migration_surface (intra-domain, CRITIC-enforced via
   check_planner_output) — greps for old-pattern call sites.
2. warn_layer_gaps (cross-domain, advisory) — schema-without-seed
   and env-provider-without-template heuristics.
"""
from __future__ import annotations


def _conf(**axes: float) -> dict:
    return {**axes, "basis": "test", "falsifiers_tested": [],
            "contradictions_reconciled": [], "gap_to_close": {}}


# --- _check_migration_surface --------------------------------------------- #

class TestCheckMigrationSurface:
    def test_migration_signal_detected(self, leerie, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        for i in range(20):
            (src / f"route{i}.ts").write_text(
                f"const id = auth.user.funeralHomeId;\n")
        (src / "seam.ts").write_text("export function getActiveTenantId() {}")

        subtasks = [{
            "id": "refactor-001",
            "title": "Extract getActiveTenantId",
            "intent": "replaces direct auth.user.funeralHomeId reads",
            "investigation_notes": "",
            "files_likely_touched": ["src/seam.ts", "src/route0.ts"],
            "depends_on": [], "size": "small",
            "success_criteria_seed": "check",
        }]
        issues = leerie._check_migration_surface(subtasks, tmp_path)
        assert any("UNCOVERED_MIGRATION_SURFACE" in i for i in issues)
        assert "auth.user.funeralHomeId" in issues[0]

    def test_covered_migration_clean(self, leerie, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        for i in range(10):
            (src / f"route{i}.ts").write_text(
                f"const id = auth.user.funeralHomeId;\n")

        files_touched = [f"src/route{i}.ts" for i in range(10)]
        subtasks = [{
            "id": "refactor-001",
            "title": "Extract getActiveTenantId",
            "intent": "replaces direct auth.user.funeralHomeId reads",
            "investigation_notes": "",
            "files_likely_touched": files_touched,
            "depends_on": [], "size": "small",
            "success_criteria_seed": "check",
        }]
        issues = leerie._check_migration_surface(subtasks, tmp_path)
        assert not any("UNCOVERED_MIGRATION_SURFACE" in i for i in issues)

    def test_small_uncovered_ignored(self, leerie, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        for i in range(3):
            (src / f"route{i}.ts").write_text(
                f"const id = auth.user.funeralHomeId;\n")

        subtasks = [{
            "id": "refactor-001",
            "title": "Extract accessor",
            "intent": "replaces direct auth.user.funeralHomeId reads",
            "investigation_notes": "",
            "files_likely_touched": [],
            "depends_on": [], "size": "small",
            "success_criteria_seed": "check",
        }]
        issues = leerie._check_migration_surface(subtasks, tmp_path)
        assert not any("UNCOVERED_MIGRATION_SURFACE" in i for i in issues)

    def test_no_migration_signal_clean(self, leerie, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        for i in range(20):
            (src / f"route{i}.ts").write_text("const x = 1;\n")

        subtasks = [{
            "id": "feat-001",
            "title": "Add login endpoint",
            "intent": "adds a new login endpoint for platform admins",
            "investigation_notes": "",
            "files_likely_touched": ["src/route0.ts"],
            "depends_on": [], "size": "small",
            "success_criteria_seed": "check",
        }]
        issues = leerie._check_migration_surface(subtasks, tmp_path)
        assert not any("UNCOVERED_MIGRATION_SURFACE" in i for i in issues)

    def test_extract_signal_variant(self, leerie, tmp_path):
        """'extracting X as the new seam' signal variant."""
        src = tmp_path / "src"
        src.mkdir()
        for i in range(10):
            (src / f"file{i}.ts").write_text("use(oldHelper);\n")

        subtasks = [{
            "id": "refactor-001",
            "title": "Extract helper",
            "intent": "extracting oldHelper as the centralized accessor",
            "investigation_notes": "",
            "files_likely_touched": ["src/file0.ts"],
            "depends_on": [], "size": "small",
            "success_criteria_seed": "check",
        }]
        issues = leerie._check_migration_surface(subtasks, tmp_path)
        assert any("UNCOVERED_MIGRATION_SURFACE" in i for i in issues)

    def test_short_pattern_ignored(self, leerie, tmp_path):
        """Patterns shorter than 4 chars are skipped (too generic)."""
        src = tmp_path / "src"
        src.mkdir()
        for i in range(20):
            (src / f"file{i}.ts").write_text("use(foo);\n")

        subtasks = [{
            "id": "refactor-001",
            "title": "Rename",
            "intent": "replaces direct foo usage",
            "investigation_notes": "",
            "files_likely_touched": [],
            "depends_on": [], "size": "small",
            "success_criteria_seed": "check",
        }]
        issues = leerie._check_migration_surface(subtasks, tmp_path)
        assert not any("UNCOVERED_MIGRATION_SURFACE" in i for i in issues)

    def test_wired_through_check_planner_output(self, leerie, tmp_path):
        """UNCOVERED_MIGRATION_SURFACE surfaces through check_planner_output."""
        src = tmp_path / "src"
        src.mkdir()
        for i in range(20):
            (src / f"route{i}.ts").write_text(
                "const id = auth.user.funeralHomeId;\n")

        result = {
            "subtasks": [{
                "id": "refactor-001",
                "title": "Extract accessor",
                "intent": "replaces direct auth.user.funeralHomeId reads",
                "investigation_notes": "",
                "files_likely_touched": ["src/route0.ts"],
                "depends_on": [], "size": "small",
                "success_criteria_seed": "check",
            }],
            "status": "ready",
            "confidence": _conf(task_understanding=9.5,
                                decomposition_quality=9.5),
        }
        issues = leerie.check_planner_output(result, tmp_path, "refactoring")
        assert any("UNCOVERED_MIGRATION_SURFACE" in i for i in issues)


# --- warn_layer_gaps ------------------------------------------------------ #

class TestWarnLayerGaps:
    def _make_plan(self, subtasks: list[dict]) -> dict:
        return {"domain": "feature-implementation",
                "subtasks": subtasks}

    def test_schema_without_seed_warns(self, leerie, capsys):
        plans = [self._make_plan([{
            "id": "feat-001", "title": "Add model",
            "files_likely_touched": ["prisma/schema.prisma"],
            "provides": [],
        }])]
        leerie.warn_layer_gaps(plans)
        captured = capsys.readouterr()
        assert "LAYER_GAP" in captured.err or "LAYER_GAP" in captured.out

    def test_schema_with_seed_clean(self, leerie, capsys):
        plans = [self._make_plan([
            {"id": "feat-001", "title": "Add model",
             "files_likely_touched": ["prisma/schema.prisma"],
             "provides": []},
            {"id": "config-001", "title": "Seed data",
             "files_likely_touched": ["prisma/seed.ts"],
             "provides": []},
        ])]
        leerie.warn_layer_gaps(plans)
        captured = capsys.readouterr()
        assert "LAYER_GAP" not in captured.err
        assert "LAYER_GAP" not in captured.out

    def test_schema_with_migration_clean(self, leerie, capsys):
        plans = [self._make_plan([
            {"id": "feat-001", "title": "Add model",
             "files_likely_touched": ["prisma/schema.prisma"],
             "provides": []},
            {"id": "feat-002", "title": "Migration",
             "files_likely_touched": [
                 "prisma/migrations/001_add_model/migration.sql"],
             "provides": []},
        ])]
        leerie.warn_layer_gaps(plans)
        captured = capsys.readouterr()
        assert "LAYER_GAP" not in captured.err
        assert "LAYER_GAP" not in captured.out

    def test_env_provider_without_template(self, leerie, capsys):
        plans = [self._make_plan([{
            "id": "feat-001", "title": "Add bootstrap",
            "files_likely_touched": ["src/lib/platform/bootstrap.ts"],
            "provides": ["superadmin-bootstrap-env-contract"],
        }])]
        leerie.warn_layer_gaps(plans)
        captured = capsys.readouterr()
        assert "LAYER_GAP" in captured.err or "LAYER_GAP" in captured.out

    def test_env_provider_with_template_clean(self, leerie, capsys):
        plans = [self._make_plan([
            {"id": "feat-001", "title": "Add bootstrap",
             "files_likely_touched": ["src/lib/platform/bootstrap.ts"],
             "provides": ["superadmin-bootstrap-env-contract"]},
            {"id": "config-001", "title": "Update env docs",
             "files_likely_touched": [".env.example"],
             "provides": []},
        ])]
        leerie.warn_layer_gaps(plans)
        captured = capsys.readouterr()
        assert "LAYER_GAP" not in captured.err
        assert "LAYER_GAP" not in captured.out

    def test_non_env_provides_clean(self, leerie, capsys):
        plans = [self._make_plan([{
            "id": "feat-001", "title": "Add CRUD",
            "files_likely_touched": ["src/api/users.ts"],
            "provides": ["user-crud-api"],
        }])]
        leerie.warn_layer_gaps(plans)
        captured = capsys.readouterr()
        assert "LAYER_GAP" not in captured.err
        assert "LAYER_GAP" not in captured.out

    def test_secret_keyword_triggers(self, leerie, capsys):
        plans = [self._make_plan([{
            "id": "infra-001", "title": "Add secrets bundle",
            "files_likely_touched": ["infra/lib/app-stack.ts"],
            "provides": ["platform-secret-bundle-provisioned"],
        }])]
        leerie.warn_layer_gaps(plans)
        captured = capsys.readouterr()
        assert "LAYER_GAP" in captured.err or "LAYER_GAP" in captured.out

    def test_no_subtasks_no_crash(self, leerie, capsys):
        plans = [{"domain": "testing", "subtasks": []}]
        leerie.warn_layer_gaps(plans)
        captured = capsys.readouterr()
        assert "LAYER_GAP" not in captured.err
        assert "LAYER_GAP" not in captured.out
