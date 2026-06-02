"""Tests for resolve_confidence_rounds() and the confidence_rounds cap.

Covers the CLI flag → env var → per-repo file → DEFAULT_CAPS resolution
order, positive-int validation, and the die() path for invalid values.
Mirrors the structure of test_resolve_source_of_truth.py.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def repo_root(tmp_path, monkeypatch):
    """An empty repo-root directory with LEERIE_CONFIDENCE_ROUNDS unset."""
    monkeypatch.delenv("LEERIE_CONFIDENCE_ROUNDS", raising=False)
    return tmp_path


def test_default_cap_is_eight(leerie):
    assert leerie.DEFAULT_CAPS["confidence_rounds"] == 8


def test_default_when_nothing_set(leerie, repo_root):
    assert leerie.resolve_confidence_rounds(repo_root) == 8


def test_file_value(leerie, repo_root):
    (repo_root / "leerie.toml").write_text("confidence_rounds = 12\n")
    assert leerie.resolve_confidence_rounds(repo_root) == 12


def test_env_value(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_CONFIDENCE_ROUNDS", "5")
    assert leerie.resolve_confidence_rounds(repo_root) == 5


def test_env_wins_over_file(leerie, repo_root, monkeypatch):
    (repo_root / "leerie.toml").write_text("confidence_rounds = 12\n")
    monkeypatch.setenv("LEERIE_CONFIDENCE_ROUNDS", "3")
    assert leerie.resolve_confidence_rounds(repo_root) == 3


def test_cli_wins_over_env_and_file(leerie, repo_root, monkeypatch):
    (repo_root / "leerie.toml").write_text("confidence_rounds = 12\n")
    monkeypatch.setenv("LEERIE_CONFIDENCE_ROUNDS", "3")
    assert leerie.resolve_confidence_rounds(repo_root, cli_value=20) == 20


def test_cli_none_falls_back(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_CONFIDENCE_ROUNDS", "3")
    assert leerie.resolve_confidence_rounds(repo_root, cli_value=None) == 3


def test_bad_env_value_dies(leerie, repo_root, monkeypatch, capsys):
    monkeypatch.setenv("LEERIE_CONFIDENCE_ROUNDS", "not-a-number")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_confidence_rounds(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "not a positive integer" in err


def test_zero_env_value_dies(leerie, repo_root, monkeypatch, capsys):
    monkeypatch.setenv("LEERIE_CONFIDENCE_ROUNDS", "0")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_confidence_rounds(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "not a positive integer" in err


def test_negative_env_value_dies(leerie, repo_root, monkeypatch, capsys):
    monkeypatch.setenv("LEERIE_CONFIDENCE_ROUNDS", "-3")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_confidence_rounds(repo_root)
    assert exc.value.code != 0


def test_bad_file_value_dies(leerie, repo_root, capsys):
    (repo_root / "leerie.toml").write_text("confidence_rounds = bogus\n")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_confidence_rounds(repo_root)
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "not a positive integer" in err


def test_zero_file_value_dies(leerie, repo_root, capsys):
    (repo_root / "leerie.toml").write_text("confidence_rounds = 0\n")
    with pytest.raises(SystemExit) as exc:
        leerie.resolve_confidence_rounds(repo_root)
    assert exc.value.code != 0


def test_empty_env_treated_as_unset(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_CONFIDENCE_ROUNDS", "")
    assert leerie.resolve_confidence_rounds(repo_root) == 8


def test_whitespace_only_env_treated_as_unset(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_CONFIDENCE_ROUNDS", "   ")
    assert leerie.resolve_confidence_rounds(repo_root) == 8


def test_positive_int_argparse_helper(leerie):
    """The _positive_int argparse type helper rejects bad values with the
    standard ArgumentTypeError so argparse surfaces a clean error."""
    import argparse
    assert leerie._positive_int("8") == 8
    assert leerie._positive_int("1") == 1
    with pytest.raises(argparse.ArgumentTypeError):
        leerie._positive_int("0")
    with pytest.raises(argparse.ArgumentTypeError):
        leerie._positive_int("-1")
    with pytest.raises(argparse.ArgumentTypeError):
        leerie._positive_int("nope")
