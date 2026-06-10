"""Tests for the CRITIC-pattern cap resolvers: judgment_check_rounds,
planner_check_rounds, implementer_confidence_retries, planner_samples.

Same resolution order as confidence_rounds: CLI → env → TOML → default.
"""
from __future__ import annotations

import pytest


# --- Fixtures ----------------------------------------------------------- #

@pytest.fixture
def repo_root(tmp_path, monkeypatch):
    for var in ("LEERIE_JUDGMENT_CHECK_ROUNDS",
                "LEERIE_PLANNER_CHECK_ROUNDS",
                "LEERIE_IMPLEMENTER_CONFIDENCE_RETRIES",
                "LEERIE_PLANNER_SAMPLES"):
        monkeypatch.delenv(var, raising=False)
    return tmp_path


# --- judgment_check_rounds ---------------------------------------------- #

def test_judgment_check_rounds_default(leerie, repo_root):
    assert leerie.resolve_judgment_check_rounds(repo_root) == 2


def test_judgment_check_rounds_env(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_JUDGMENT_CHECK_ROUNDS", "4")
    assert leerie.resolve_judgment_check_rounds(repo_root) == 4


def test_judgment_check_rounds_toml(leerie, repo_root):
    (repo_root / "leerie.toml").write_text("judgment_check_rounds = 5\n")
    assert leerie.resolve_judgment_check_rounds(repo_root) == 5


def test_judgment_check_rounds_cli_wins(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_JUDGMENT_CHECK_ROUNDS", "4")
    assert leerie.resolve_judgment_check_rounds(repo_root, cli_value=1) == 1


# --- planner_check_rounds ---------------------------------------------- #

def test_planner_check_rounds_default(leerie, repo_root):
    assert leerie.resolve_planner_check_rounds(repo_root) == 3


def test_planner_check_rounds_env(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_PLANNER_CHECK_ROUNDS", "6")
    assert leerie.resolve_planner_check_rounds(repo_root) == 6


def test_planner_check_rounds_cli_wins(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_PLANNER_CHECK_ROUNDS", "6")
    assert leerie.resolve_planner_check_rounds(repo_root, cli_value=2) == 2


# --- implementer_confidence_retries ------------------------------------ #

def test_implementer_confidence_retries_default(leerie, repo_root):
    assert leerie.resolve_implementer_confidence_retries(repo_root) == 2


def test_implementer_confidence_retries_env(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_IMPLEMENTER_CONFIDENCE_RETRIES", "3")
    assert leerie.resolve_implementer_confidence_retries(repo_root) == 3


def test_implementer_confidence_retries_cli_wins(
        leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_IMPLEMENTER_CONFIDENCE_RETRIES", "3")
    assert leerie.resolve_implementer_confidence_retries(
        repo_root, cli_value=1) == 1


# --- planner_samples --------------------------------------------------- #

def test_planner_samples_default(leerie, repo_root):
    assert leerie.resolve_planner_samples(repo_root) == 3


def test_planner_samples_env(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_PLANNER_SAMPLES", "3")
    assert leerie.resolve_planner_samples(repo_root) == 3


def test_planner_samples_toml(leerie, repo_root):
    (repo_root / "leerie.toml").write_text("planner_samples = 2\n")
    assert leerie.resolve_planner_samples(repo_root) == 2


def test_planner_samples_cli_wins(leerie, repo_root, monkeypatch):
    monkeypatch.setenv("LEERIE_PLANNER_SAMPLES", "3")
    assert leerie.resolve_planner_samples(repo_root, cli_value=5) == 5


# --- DEFAULT_CAPS keys exist ------------------------------------------- #

def test_default_caps_contains_new_keys(leerie):
    for key in ("judgment_check_rounds", "planner_check_rounds",
                "implementer_confidence_retries", "planner_samples"):
        assert key in leerie.DEFAULT_CAPS, f"DEFAULT_CAPS missing {key!r}"
