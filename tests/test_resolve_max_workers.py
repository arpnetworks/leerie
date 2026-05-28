"""Tests for resolve_max_workers() and the max_total_workers cap.

Covers the CLI flag → env var → per-repo file → DEFAULT_CAPS resolution
order, positive-int validation, and the die() path for invalid values.
Mirrors the structure of test_resolve_confidence_rounds.py.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def repo_root(tmp_path, monkeypatch):
    """An empty repo-root directory with CENTELLA_MAX_WORKERS unset."""
    monkeypatch.delenv("CENTELLA_MAX_WORKERS", raising=False)
    return tmp_path


def test_default_cap_is_sixty(centella):
    assert centella.DEFAULT_CAPS["max_total_workers"] == 60


def test_default_when_nothing_set(centella, repo_root):
    assert centella.resolve_max_workers(repo_root) == 60


def test_file_value(centella, repo_root):
    (repo_root / "centella.toml").write_text("max_workers = 80\n")
    assert centella.resolve_max_workers(repo_root) == 80


def test_env_value(centella, repo_root, monkeypatch):
    monkeypatch.setenv("CENTELLA_MAX_WORKERS", "100")
    assert centella.resolve_max_workers(repo_root) == 100


def test_env_wins_over_file(centella, repo_root, monkeypatch):
    (repo_root / "centella.toml").write_text("max_workers = 80\n")
    monkeypatch.setenv("CENTELLA_MAX_WORKERS", "100")
    assert centella.resolve_max_workers(repo_root) == 100


def test_cli_wins_over_env_and_file(centella, repo_root, monkeypatch):
    (repo_root / "centella.toml").write_text("max_workers = 80\n")
    monkeypatch.setenv("CENTELLA_MAX_WORKERS", "100")
    assert centella.resolve_max_workers(repo_root, cli_value=120) == 120


def test_cli_none_falls_back(centella, repo_root, monkeypatch):
    monkeypatch.setenv("CENTELLA_MAX_WORKERS", "100")
    assert centella.resolve_max_workers(repo_root, cli_value=None) == 100


def test_bad_env_value_dies(centella, repo_root, monkeypatch, capsys):
    monkeypatch.setenv("CENTELLA_MAX_WORKERS", "not-a-number")
    with pytest.raises(SystemExit) as exc:
        centella.resolve_max_workers(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "not a positive integer" in err


def test_zero_env_value_dies(centella, repo_root, monkeypatch, capsys):
    monkeypatch.setenv("CENTELLA_MAX_WORKERS", "0")
    with pytest.raises(SystemExit) as exc:
        centella.resolve_max_workers(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "not a positive integer" in err


def test_negative_env_value_dies(centella, repo_root, monkeypatch, capsys):
    monkeypatch.setenv("CENTELLA_MAX_WORKERS", "-3")
    with pytest.raises(SystemExit) as exc:
        centella.resolve_max_workers(repo_root)
    assert exc.value.code != 0


def test_bad_file_value_dies(centella, repo_root, capsys):
    (repo_root / "centella.toml").write_text("max_workers = bogus\n")
    with pytest.raises(SystemExit) as exc:
        centella.resolve_max_workers(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "not a positive integer" in err


def test_zero_file_value_dies(centella, repo_root, capsys):
    (repo_root / "centella.toml").write_text("max_workers = 0\n")
    with pytest.raises(SystemExit) as exc:
        centella.resolve_max_workers(repo_root)
    assert exc.value.code != 0


def test_empty_env_treated_as_unset(centella, repo_root, monkeypatch):
    monkeypatch.setenv("CENTELLA_MAX_WORKERS", "")
    assert centella.resolve_max_workers(repo_root) == 60


def test_whitespace_only_env_treated_as_unset(centella, repo_root, monkeypatch):
    monkeypatch.setenv("CENTELLA_MAX_WORKERS", "   ")
    assert centella.resolve_max_workers(repo_root) == 60
