"""Tests for resolve_max_parallel() and the max_parallel cap.

Covers the CLI flag → env var → per-repo file → DEFAULT_CAPS resolution
order, positive-int validation, and the die() path for invalid values.
Mirrors the structure of test_resolve_max_workers.py.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def repo_root(tmp_path, monkeypatch):
    """An empty repo-root directory with LEERIE_MAX_PARALLEL unset."""
    monkeypatch.delenv("LEERIE_MAX_PARALLEL", raising=False)
    return tmp_path


def test_default_cap_is_five(leerie):
    assert leerie.DEFAULT_CAPS["max_parallel"] == 5


def test_default_when_nothing_set(leerie, repo_root):
    assert leerie.resolve_max_parallel(repo_root) == 5


def test_file_value(leerie, repo_root):
    (repo_root / "leerie.toml").write_text("max_parallel = 6\n")
    assert leerie.resolve_max_parallel(repo_root) == 6


def test_env_value(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_MAX_PARALLEL", "8")
    assert leerie.resolve_max_parallel(repo_root) == 8


def test_env_wins_over_file(leerie, repo_root, monkeypatch):
    (repo_root / "leerie.toml").write_text("max_parallel = 6\n")
    monkeypatch.setenv("LEERIE_MAX_PARALLEL", "8")
    assert leerie.resolve_max_parallel(repo_root) == 8


def test_cli_wins_over_env_and_file(leerie, repo_root, monkeypatch):
    (repo_root / "leerie.toml").write_text("max_parallel = 6\n")
    monkeypatch.setenv("LEERIE_MAX_PARALLEL", "8")
    assert leerie.resolve_max_parallel(repo_root, cli_value=12) == 12


def test_cli_none_falls_back(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_MAX_PARALLEL", "8")
    assert leerie.resolve_max_parallel(repo_root, cli_value=None) == 8


def test_bad_env_value_dies(leerie, repo_root, monkeypatch, capsys):
    monkeypatch.setenv("LEERIE_MAX_PARALLEL", "not-a-number")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_max_parallel(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "not a positive integer" in err


def test_zero_env_value_dies(leerie, repo_root, monkeypatch, capsys):
    monkeypatch.setenv("LEERIE_MAX_PARALLEL", "0")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_max_parallel(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "not a positive integer" in err


def test_negative_env_value_dies(leerie, repo_root, monkeypatch, capsys):
    monkeypatch.setenv("LEERIE_MAX_PARALLEL", "-3")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_max_parallel(repo_root)
    assert exc.value.code != 0


def test_bad_file_value_dies(leerie, repo_root, capsys):
    (repo_root / "leerie.toml").write_text("max_parallel = bogus\n")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_max_parallel(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "not a positive integer" in err


def test_zero_file_value_dies(leerie, repo_root, capsys):
    (repo_root / "leerie.toml").write_text("max_parallel = 0\n")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_max_parallel(repo_root)
    assert exc.value.code != 0


def test_empty_env_treated_as_unset(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_MAX_PARALLEL", "")
    assert leerie.resolve_max_parallel(repo_root) == 5


def test_whitespace_only_env_treated_as_unset(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_MAX_PARALLEL", "   ")
    assert leerie.resolve_max_parallel(repo_root) == 5
