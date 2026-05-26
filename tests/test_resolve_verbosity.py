"""Tests for resolve_verbosity().

Mirrors test_resolve_source_of_truth.py's structure: CLI > env >
centella.toml > default, with bad values rejected at startup via die().
Also pins the 4-level enum and the default.

The -v/-vv/-q/-qq shortcuts are NOT exercised here — they are resolved
in main() and pass through resolve_verbosity as the cli_value
argument. See test_verbosity_shortcuts.py for the shortcut logic.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def repo_root(tmp_path, monkeypatch):
    """An empty repo-root directory with CENTELLA_VERBOSITY unset."""
    monkeypatch.delenv("CENTELLA_VERBOSITY", raising=False)
    return tmp_path


def test_default_is_stream(centella):
    """The default is `stream` because a user invoking centella is
    typically opening to watch. See clig.dev / research notes."""
    assert centella.VERBOSITY_DEFAULT == "stream"


def test_four_levels(centella):
    """Pin the level enum so a future change that adds/removes a
    level is a deliberate choice and not a silent drift."""
    assert centella.VERBOSITY_VALUES == ("quiet", "normal", "stream", "debug")


def test_unset_falls_back_to_default(centella, repo_root):
    assert centella.resolve_verbosity(repo_root) == "stream"


def test_file_present_env_unset(centella, repo_root):
    (repo_root / "centella.toml").write_text("verbosity = quiet\n")
    assert centella.resolve_verbosity(repo_root) == "quiet"


def test_env_set(centella, repo_root, monkeypatch):
    monkeypatch.setenv("CENTELLA_VERBOSITY", "debug")
    assert centella.resolve_verbosity(repo_root) == "debug"


def test_env_wins_over_file(centella, repo_root, monkeypatch):
    (repo_root / "centella.toml").write_text("verbosity = quiet\n")
    monkeypatch.setenv("CENTELLA_VERBOSITY", "debug")
    assert centella.resolve_verbosity(repo_root) == "debug"


def test_cli_wins_over_env_and_file(centella, repo_root, monkeypatch):
    (repo_root / "centella.toml").write_text("verbosity = quiet\n")
    monkeypatch.setenv("CENTELLA_VERBOSITY", "debug")
    assert centella.resolve_verbosity(repo_root, cli_value="normal") == "normal"


@pytest.mark.parametrize("value", ["quiet", "normal", "stream", "debug"])
def test_all_levels_accepted(centella, repo_root, value):
    (repo_root / "centella.toml").write_text(f"verbosity = {value}\n")
    assert centella.resolve_verbosity(repo_root) == value


def test_bad_file_value_dies(centella, repo_root, capsys):
    (repo_root / "centella.toml").write_text("verbosity = chatty\n")
    with pytest.raises(SystemExit) as exc:
        centella.resolve_verbosity(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "is not one of" in err
    assert "chatty" in err


def test_bad_env_value_dies(centella, repo_root, monkeypatch, capsys):
    monkeypatch.setenv("CENTELLA_VERBOSITY", "loud")
    with pytest.raises(SystemExit) as exc:
        centella.resolve_verbosity(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "is not one of" in err


def test_empty_env_treated_as_unset(centella, repo_root, monkeypatch):
    monkeypatch.setenv("CENTELLA_VERBOSITY", "")
    assert centella.resolve_verbosity(repo_root) == "stream"


def test_cli_value_none_falls_back(centella, repo_root, monkeypatch):
    monkeypatch.setenv("CENTELLA_VERBOSITY", "normal")
    assert centella.resolve_verbosity(repo_root, cli_value=None) == "normal"
