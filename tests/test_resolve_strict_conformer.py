"""Tests for resolve_strict_conformer() — the --strict-conformer
opt-in that makes the conformer phase blocking instead of advisory.

Covers the precedence order: CLI flag → LEERIE_STRICT_CONFORMER env
var → strict_conformer in leerie.toml → False.

Mirrors test_resolve_skip_budget_check.py — both resolvers share
`_resolve_bool_pref`, so this file locks the wiring (env var name +
file key), not the resolution logic.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def repo_root(tmp_path, monkeypatch):
    monkeypatch.delenv("LEERIE_STRICT_CONFORMER", raising=False)
    return tmp_path


def test_default_is_off(leerie, repo_root):
    assert leerie.resolve_strict_conformer(
        repo_root, cli_value=False) is False


def test_cli_flag_wins(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_STRICT_CONFORMER", "0")
    (repo_root / "leerie.toml").write_text(
        "strict_conformer = false\n")
    assert leerie.resolve_strict_conformer(
        repo_root, cli_value=True) is True


def test_env_set_true(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_STRICT_CONFORMER", "1")
    assert leerie.resolve_strict_conformer(
        repo_root, cli_value=False) is True


def test_file_set_true_no_env(leerie, repo_root):
    (repo_root / "leerie.toml").write_text(
        "strict_conformer = true\n")
    assert leerie.resolve_strict_conformer(
        repo_root, cli_value=False) is True


def test_env_wins_over_file(leerie, repo_root, monkeypatch):
    (repo_root / "leerie.toml").write_text(
        "strict_conformer = true\n")
    monkeypatch.setenv("LEERIE_STRICT_CONFORMER", "false")
    assert leerie.resolve_strict_conformer(
        repo_root, cli_value=False) is False


def test_env_garbage_dies(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_STRICT_CONFORMER", "maybe")
    with pytest.raises(SystemExit):
        leerie.resolve_strict_conformer(
            repo_root, cli_value=False)
