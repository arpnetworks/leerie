"""Tests for resolve_verbosity().

Mirrors test_resolve_source_of_truth.py's structure: CLI > env >
leerie.toml > default, with bad values rejected at startup via die().
Also pins the 4-level enum and the default.

The -v/-vv/-q/-qq shortcuts are NOT exercised here — they are resolved
in main() and pass through resolve_verbosity as the cli_value
argument. See test_verbosity_shortcuts.py for the shortcut logic.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def repo_root(tmp_path, monkeypatch):
    """An empty repo-root directory with LEERIE_VERBOSITY unset."""
    monkeypatch.delenv("LEERIE_VERBOSITY", raising=False)
    return tmp_path


def test_default_is_stream(leerie):
    """The default is `stream` because a user invoking leerie is
    typically opening to watch. See clig.dev / research notes."""
    assert leerie.VERBOSITY_DEFAULT == "stream"


def test_four_levels(leerie):
    """Pin the level enum so a future change that adds/removes a
    level is a deliberate choice and not a silent drift."""
    assert leerie.VERBOSITY_VALUES == ("quiet", "normal", "stream", "debug")


def test_unset_falls_back_to_default(leerie, repo_root):
    assert leerie.resolve_verbosity(repo_root) == "stream"


def test_file_present_env_unset(leerie, repo_root):
    (repo_root / "leerie.toml").write_text("verbosity = quiet\n")
    assert leerie.resolve_verbosity(repo_root) == "quiet"


def test_env_set(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_VERBOSITY", "debug")
    assert leerie.resolve_verbosity(repo_root) == "debug"


def test_env_wins_over_file(leerie, repo_root, monkeypatch):
    (repo_root / "leerie.toml").write_text("verbosity = quiet\n")
    monkeypatch.setenv("LEERIE_VERBOSITY", "debug")
    assert leerie.resolve_verbosity(repo_root) == "debug"


def test_cli_wins_over_env_and_file(leerie, repo_root, monkeypatch):
    (repo_root / "leerie.toml").write_text("verbosity = quiet\n")
    monkeypatch.setenv("LEERIE_VERBOSITY", "debug")
    assert leerie.resolve_verbosity(repo_root, cli_value="normal") == "normal"


@pytest.mark.parametrize("value", ["quiet", "normal", "stream", "debug"])
def test_all_levels_accepted(leerie, repo_root, value):
    (repo_root / "leerie.toml").write_text(f"verbosity = {value}\n")
    assert leerie.resolve_verbosity(repo_root) == value


def test_bad_file_value_dies(leerie, repo_root, capsys):
    (repo_root / "leerie.toml").write_text("verbosity = chatty\n")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_verbosity(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "is not one of" in err
    assert "chatty" in err


def test_bad_env_value_dies(leerie, repo_root, monkeypatch, capsys):
    monkeypatch.setenv("LEERIE_VERBOSITY", "loud")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_verbosity(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "is not one of" in err


def test_empty_env_treated_as_unset(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_VERBOSITY", "")
    assert leerie.resolve_verbosity(repo_root) == "stream"


def test_cli_value_none_falls_back(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_VERBOSITY", "normal")
    assert leerie.resolve_verbosity(repo_root, cli_value=None) == "normal"
