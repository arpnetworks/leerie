"""Tests for telemetry/judge/heal config resolvers.

Covers each of:
  resolve_telemetry_enabled  — boolean, default True
  resolve_telemetry_subdir   — string, default "events"
  resolve_judge_dir          — string, default "judge-out"
  resolve_heal_dir           — string, default "heal-out"

For each resolver: CLI > env > toml > default precedence, empty/whitespace
env treated as unset, quoted TOML values, and die() on invalid values.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# resolve_telemetry_enabled
# ---------------------------------------------------------------------------

@pytest.fixture
def repo_root_tel(tmp_path, monkeypatch):
    monkeypatch.delenv("LEERIE_TELEMETRY", raising=False)
    return tmp_path


def test_telemetry_default_is_true(leerie, repo_root_tel):
    assert leerie.resolve_telemetry_enabled(repo_root_tel) is True


def test_telemetry_cli_true_wins(leerie, repo_root_tel, monkeypatch):
    monkeypatch.setenv("LEERIE_TELEMETRY", "0")
    (repo_root_tel / "leerie.toml").write_text("telemetry = false\n")
    assert leerie.resolve_telemetry_enabled(repo_root_tel, cli_value=True) is True


def test_telemetry_cli_false_wins(leerie, repo_root_tel, monkeypatch):
    monkeypatch.setenv("LEERIE_TELEMETRY", "1")
    assert leerie.resolve_telemetry_enabled(repo_root_tel, cli_value=False) is False


def test_telemetry_cli_none_falls_through(leerie, repo_root_tel, monkeypatch):
    monkeypatch.setenv("LEERIE_TELEMETRY", "0")
    assert leerie.resolve_telemetry_enabled(repo_root_tel, cli_value=None) is False


def test_telemetry_env_wins_over_file(leerie, repo_root_tel, monkeypatch):
    (repo_root_tel / "leerie.toml").write_text("telemetry = true\n")
    monkeypatch.setenv("LEERIE_TELEMETRY", "0")
    assert leerie.resolve_telemetry_enabled(repo_root_tel) is False


def test_telemetry_file_value_true(leerie, repo_root_tel):
    (repo_root_tel / "leerie.toml").write_text("telemetry = true\n")
    assert leerie.resolve_telemetry_enabled(repo_root_tel) is True


def test_telemetry_file_value_false(leerie, repo_root_tel):
    (repo_root_tel / "leerie.toml").write_text("telemetry = false\n")
    assert leerie.resolve_telemetry_enabled(repo_root_tel) is False


def test_telemetry_quoted_file_value(leerie, repo_root_tel):
    (repo_root_tel / "leerie.toml").write_text('telemetry = "false"\n')
    assert leerie.resolve_telemetry_enabled(repo_root_tel) is False


@pytest.mark.parametrize("value", ["1", "true", "True", "TRUE", "yes", "on", "ON"])
def test_telemetry_env_truthy_spellings(leerie, repo_root_tel, monkeypatch, value):
    monkeypatch.setenv("LEERIE_TELEMETRY", value)
    assert leerie.resolve_telemetry_enabled(repo_root_tel) is True


@pytest.mark.parametrize("value", ["0", "false", "False", "FALSE", "no", "off", "OFF"])
def test_telemetry_env_falsy_spellings(leerie, repo_root_tel, monkeypatch, value):
    monkeypatch.setenv("LEERIE_TELEMETRY", value)
    assert leerie.resolve_telemetry_enabled(repo_root_tel) is False


def test_telemetry_empty_env_treated_as_unset(leerie, repo_root_tel, monkeypatch):
    monkeypatch.setenv("LEERIE_TELEMETRY", "")
    assert leerie.resolve_telemetry_enabled(repo_root_tel) is True


def test_telemetry_whitespace_env_treated_as_unset(leerie, repo_root_tel, monkeypatch):
    monkeypatch.setenv("LEERIE_TELEMETRY", "   ")
    assert leerie.resolve_telemetry_enabled(repo_root_tel) is True


def test_telemetry_bad_env_dies(leerie, repo_root_tel, monkeypatch, capsys):
    monkeypatch.setenv("LEERIE_TELEMETRY", "maybe")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_telemetry_enabled(repo_root_tel)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "LEERIE_TELEMETRY" in err
    assert "maybe" in err


def test_telemetry_bad_file_dies(leerie, repo_root_tel, capsys):
    (repo_root_tel / "leerie.toml").write_text("telemetry = sometimes\n")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_telemetry_enabled(repo_root_tel)
    assert exc.value.code != 0


# ---------------------------------------------------------------------------
# resolve_telemetry_subdir
# ---------------------------------------------------------------------------

@pytest.fixture
def repo_root_sub(tmp_path, monkeypatch):
    monkeypatch.delenv("LEERIE_TELEMETRY_DIR", raising=False)
    return tmp_path


def test_telemetry_subdir_default(leerie, repo_root_sub):
    assert leerie.resolve_telemetry_subdir(repo_root_sub) == "events"


def test_telemetry_subdir_cli_wins(leerie, repo_root_sub, monkeypatch):
    monkeypatch.setenv("LEERIE_TELEMETRY_DIR", "env-events")
    (repo_root_sub / "leerie.toml").write_text("telemetry_dir = toml-events\n")
    assert leerie.resolve_telemetry_subdir(repo_root_sub, cli_value="cli-events") == "cli-events"


def test_telemetry_subdir_env_wins_over_file(leerie, repo_root_sub, monkeypatch):
    (repo_root_sub / "leerie.toml").write_text("telemetry_dir = toml-events\n")
    monkeypatch.setenv("LEERIE_TELEMETRY_DIR", "env-events")
    assert leerie.resolve_telemetry_subdir(repo_root_sub) == "env-events"


def test_telemetry_subdir_file_value(leerie, repo_root_sub):
    (repo_root_sub / "leerie.toml").write_text("telemetry_dir = my-events\n")
    assert leerie.resolve_telemetry_subdir(repo_root_sub) == "my-events"


def test_telemetry_subdir_quoted_file_value(leerie, repo_root_sub):
    (repo_root_sub / "leerie.toml").write_text('telemetry_dir = "custom"\n')
    assert leerie.resolve_telemetry_subdir(repo_root_sub) == "custom"


def test_telemetry_subdir_empty_env_falls_to_default(leerie, repo_root_sub, monkeypatch):
    monkeypatch.setenv("LEERIE_TELEMETRY_DIR", "")
    assert leerie.resolve_telemetry_subdir(repo_root_sub) == "events"


def test_telemetry_subdir_empty_cli_falls_to_default(leerie, repo_root_sub):
    assert leerie.resolve_telemetry_subdir(repo_root_sub, cli_value="") == "events"


def test_telemetry_subdir_whitespace_cli_falls_to_default(leerie, repo_root_sub):
    assert leerie.resolve_telemetry_subdir(repo_root_sub, cli_value="   ") == "events"


# ---------------------------------------------------------------------------
# resolve_judge_dir
# ---------------------------------------------------------------------------

@pytest.fixture
def repo_root_judge(tmp_path, monkeypatch):
    monkeypatch.delenv("LEERIE_JUDGE_DIR", raising=False)
    return tmp_path


def test_judge_dir_default(leerie, repo_root_judge):
    assert leerie.resolve_judge_dir(repo_root_judge) == "judge-out"


def test_judge_dir_cli_wins(leerie, repo_root_judge, monkeypatch):
    monkeypatch.setenv("LEERIE_JUDGE_DIR", "env-judge")
    (repo_root_judge / "leerie.toml").write_text("judge_dir = toml-judge\n")
    assert leerie.resolve_judge_dir(repo_root_judge, cli_value="cli-judge") == "cli-judge"


def test_judge_dir_env_wins_over_file(leerie, repo_root_judge, monkeypatch):
    (repo_root_judge / "leerie.toml").write_text("judge_dir = toml-judge\n")
    monkeypatch.setenv("LEERIE_JUDGE_DIR", "env-judge")
    assert leerie.resolve_judge_dir(repo_root_judge) == "env-judge"


def test_judge_dir_file_value(leerie, repo_root_judge):
    (repo_root_judge / "leerie.toml").write_text("judge_dir = my-judge\n")
    assert leerie.resolve_judge_dir(repo_root_judge) == "my-judge"


def test_judge_dir_quoted_file_value(leerie, repo_root_judge):
    (repo_root_judge / "leerie.toml").write_text('judge_dir = "custom-judge"\n')
    assert leerie.resolve_judge_dir(repo_root_judge) == "custom-judge"


def test_judge_dir_empty_env_falls_to_default(leerie, repo_root_judge, monkeypatch):
    monkeypatch.setenv("LEERIE_JUDGE_DIR", "")
    assert leerie.resolve_judge_dir(repo_root_judge) == "judge-out"


def test_judge_dir_empty_cli_falls_to_default(leerie, repo_root_judge):
    assert leerie.resolve_judge_dir(repo_root_judge, cli_value="") == "judge-out"


# ---------------------------------------------------------------------------
# resolve_heal_dir
# ---------------------------------------------------------------------------

@pytest.fixture
def repo_root_heal(tmp_path, monkeypatch):
    monkeypatch.delenv("LEERIE_HEAL_DIR", raising=False)
    return tmp_path


def test_heal_dir_default(leerie, repo_root_heal):
    assert leerie.resolve_heal_dir(repo_root_heal) == "heal-out"


def test_heal_dir_cli_wins(leerie, repo_root_heal, monkeypatch):
    monkeypatch.setenv("LEERIE_HEAL_DIR", "env-heal")
    (repo_root_heal / "leerie.toml").write_text("heal_dir = toml-heal\n")
    assert leerie.resolve_heal_dir(repo_root_heal, cli_value="cli-heal") == "cli-heal"


def test_heal_dir_env_wins_over_file(leerie, repo_root_heal, monkeypatch):
    (repo_root_heal / "leerie.toml").write_text("heal_dir = toml-heal\n")
    monkeypatch.setenv("LEERIE_HEAL_DIR", "env-heal")
    assert leerie.resolve_heal_dir(repo_root_heal) == "env-heal"


def test_heal_dir_file_value(leerie, repo_root_heal):
    (repo_root_heal / "leerie.toml").write_text("heal_dir = my-heal\n")
    assert leerie.resolve_heal_dir(repo_root_heal) == "my-heal"


def test_heal_dir_quoted_file_value(leerie, repo_root_heal):
    (repo_root_heal / "leerie.toml").write_text('heal_dir = "custom-heal"\n')
    assert leerie.resolve_heal_dir(repo_root_heal) == "custom-heal"


def test_heal_dir_empty_env_falls_to_default(leerie, repo_root_heal, monkeypatch):
    monkeypatch.setenv("LEERIE_HEAL_DIR", "")
    assert leerie.resolve_heal_dir(repo_root_heal) == "heal-out"


def test_heal_dir_empty_cli_falls_to_default(leerie, repo_root_heal):
    assert leerie.resolve_heal_dir(repo_root_heal, cli_value="") == "heal-out"
