"""Tests for `resolve_run_id()` — pick the run_id to operate on for
`--resume` / `--list`. Policy is fails-closed: ambiguity is a hard error,
never a heuristic guess.

Cases:
- Zero runs → die.
- Exactly one run → auto-pick (common case for single-run users).
- Multiple runs, no --run-id → die with the available list.
- Multiple runs, --run-id matches → use it.
- Multiple runs, --run-id doesn't match → die with the available list.

`resolve_run_id` exits via `die()` (which calls `sys.exit(1)`) on failures,
so we catch `SystemExit`."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


def _make_run(pila_root: Path, run_id: str, state: dict) -> None:
    run_dir = pila_root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "state.json").write_text(json.dumps(state))


def test_resolve_zero_runs_dies(pila, tmp_path):
    """Empty `.pila/runs/` is a hard error — there's nothing to resume."""
    with pytest.raises(SystemExit):
        pila.resolve_run_id(tmp_path, None)


def test_resolve_single_run_auto_picks(pila, tmp_path):
    """One run + no --run-id → use it. Preserves the existing
    single-run experience."""
    _make_run(tmp_path, "feat-foo-abc123",
              {"task": "x", "started_at": "2026-05-26T10:00:00+00:00"})
    assert pila.resolve_run_id(tmp_path, None) == "feat-foo-abc123"


def test_resolve_single_run_explicit_match(pila, tmp_path):
    """One run + matching --run-id → use it."""
    _make_run(tmp_path, "feat-foo-abc123",
              {"task": "x", "started_at": "2026-05-26T10:00:00+00:00"})
    assert pila.resolve_run_id(tmp_path, "feat-foo-abc123") == "feat-foo-abc123"


def test_resolve_single_run_wrong_explicit_dies(pila, tmp_path):
    """Even with only one run, a wrong --run-id dies — `--run-id` requires
    an exact match, never a fuzzy auto-pick."""
    _make_run(tmp_path, "feat-foo-abc123",
              {"task": "x", "started_at": "2026-05-26T10:00:00+00:00"})
    with pytest.raises(SystemExit):
        pila.resolve_run_id(tmp_path, "feat-bar-xyz999")


def test_resolve_multiple_runs_no_run_id_dies(pila, tmp_path):
    """Ambiguity is never resolved by heuristic. User must pass --run-id."""
    _make_run(tmp_path, "feat-a-aaaaaa",
              {"task": "a", "started_at": "2026-05-26T10:00:00+00:00"})
    _make_run(tmp_path, "feat-b-bbbbbb",
              {"task": "b", "started_at": "2026-05-26T11:00:00+00:00"})
    with pytest.raises(SystemExit):
        pila.resolve_run_id(tmp_path, None)


def test_resolve_multiple_runs_explicit_match(pila, tmp_path):
    """With --run-id and multiple runs, the exact match wins."""
    _make_run(tmp_path, "feat-a-aaaaaa",
              {"task": "a", "started_at": "2026-05-26T10:00:00+00:00"})
    _make_run(tmp_path, "feat-b-bbbbbb",
              {"task": "b", "started_at": "2026-05-26T11:00:00+00:00"})
    assert pila.resolve_run_id(tmp_path, "feat-b-bbbbbb") == "feat-b-bbbbbb"


def test_resolve_multiple_runs_wrong_explicit_dies(pila, tmp_path):
    _make_run(tmp_path, "feat-a-aaaaaa",
              {"task": "a", "started_at": "2026-05-26T10:00:00+00:00"})
    _make_run(tmp_path, "feat-b-bbbbbb",
              {"task": "b", "started_at": "2026-05-26T11:00:00+00:00"})
    with pytest.raises(SystemExit):
        pila.resolve_run_id(tmp_path, "feat-nope-zzz999")


def test_resolve_ignores_bootstrap_runs(pila, tmp_path):
    """A bootstrap directory (pre-classify) is not a real run — resolution
    treats it as not existing. If only a bootstrap dir exists, resolve dies."""
    _make_run(tmp_path, "_bootstrap-abcdef",
              {"task": "bootstrap", "started_at": "2026-05-26T10:00:00+00:00"})
    with pytest.raises(SystemExit):
        pila.resolve_run_id(tmp_path, None)


def test_resolve_message_includes_available_runs(pila, tmp_path, capsys):
    """When resolution fails, the error should list available run ids so
    the user can copy-paste one — not just 'try again'."""
    _make_run(tmp_path, "feat-foo-abc123",
              {"task": "x", "started_at": "2026-05-26T10:00:00+00:00"})
    _make_run(tmp_path, "fix-bar-def456",
              {"task": "y", "started_at": "2026-05-26T11:00:00+00:00"})
    with pytest.raises(SystemExit):
        pila.resolve_run_id(tmp_path, None)
    err = capsys.readouterr().err
    assert "feat-foo-abc123" in err
    assert "fix-bar-def456" in err


# --- F1 carve-out: explicit _bootstrap-* ids are accepted ---------------
# Pre-classify resume scenario: user paused a remote run via
# `pila --stop _bootstrap-XXX` before phase_classify completed. The
# run dir on the machine is still _bootstrap-XXX. discover_runs filters
# these dirs, so without the carve-out, --resume --run-id _bootstrap-XXX
# dies with "no runs found". The carve-out in resolve_run_id allows
# explicit naming of a bootstrap dir as long as state.json exists.

def test_resolve_explicit_bootstrap_id_accepted_when_state_json_exists(pila, tmp_path):
    """Pre-classify resume: --run-id _bootstrap-XXX is honored when the
    dir exists with a state.json, even though discover_runs filters it."""
    _make_run(tmp_path, "_bootstrap-abc123",
              {"task": "x", "started_at": "2026-05-26T10:00:00+00:00"})
    assert pila.resolve_run_id(tmp_path, "_bootstrap-abc123") == "_bootstrap-abc123"


def test_resolve_bootstrap_id_without_state_json_still_dies(pila, tmp_path):
    """The carve-out requires state.json. A bootstrap dir with only
    e.g. fly-machine.json (the host-side D2 case during in-flight pause)
    is NOT a valid resume target — there's no orchestrator state yet."""
    # Make the dir but NO state.json.
    rd = tmp_path / "runs" / "_bootstrap-empty00"
    rd.mkdir(parents=True)
    (rd / "fly-machine.json").write_text('{"fly_machine_id": "mach-x"}')
    with pytest.raises(SystemExit):
        pila.resolve_run_id(tmp_path, "_bootstrap-empty00")


def test_resolve_bootstrap_id_not_named_explicit_still_filtered(pila, tmp_path):
    """Without an explicit --run-id, bootstrap dirs are still filtered.
    A repo with only a bootstrap dir + no explicit --run-id dies the
    same way as an empty repo. Regression guard for the carve-out
    being narrowly-scoped to the explicit-name case."""
    _make_run(tmp_path, "_bootstrap-abc123",
              {"task": "x", "started_at": "2026-05-26T10:00:00+00:00"})
    with pytest.raises(SystemExit):
        pila.resolve_run_id(tmp_path, None)


def test_resolve_bootstrap_id_does_not_match_wrong_name(pila, tmp_path):
    """A non-matching --run-id _bootstrap-XXX still dies, even with the
    carve-out — the dir must actually exist."""
    _make_run(tmp_path, "_bootstrap-real123",
              {"task": "x", "started_at": "2026-05-26T10:00:00+00:00"})
    with pytest.raises(SystemExit):
        pila.resolve_run_id(tmp_path, "_bootstrap-fake999")


# --- disambiguation hint: status + last-activity per row -----------------

def test_resolve_multiple_runs_message_includes_status(pila, tmp_path,
                                                       capsys):
    """The disambiguation message must show the derived status of each
    run (from _derive_run_status) so the user can spot e.g. a
    `done-pushed-pr` run versus an `in-progress` one without an extra
    `pila --list` invocation."""
    _make_run(tmp_path, "feat-a-aaaaaa",
              {"task": "a", "started_at": "2026-05-26T10:00:00+00:00"})
    _make_run(tmp_path, "feat-b-bbbbbb",
              {"task": "b", "started_at": "2026-05-26T11:00:00+00:00"})
    with pytest.raises(SystemExit):
        pila.resolve_run_id(tmp_path, None)
    err = capsys.readouterr().err
    # Both runs have no run.json sidecar → in-progress.
    assert "status=in-progress" in err


def test_resolve_multiple_runs_message_includes_last_activity(pila, tmp_path,
                                                              capsys):
    """The disambiguation message must show how long ago each run's
    state.json was last touched so the user can spot a hung or
    abandoned run (last-activity hours/days ago) vs. a live one
    (seconds-to-minutes). The exact format is fuzzy (it depends on
    when the test runs vs. when the file was created), but the
    `last-activity=` prefix is pinned."""
    _make_run(tmp_path, "feat-a-aaaaaa",
              {"task": "a", "started_at": "2026-05-26T10:00:00+00:00"})
    _make_run(tmp_path, "feat-b-bbbbbb",
              {"task": "b", "started_at": "2026-05-26T11:00:00+00:00"})
    with pytest.raises(SystemExit):
        pila.resolve_run_id(tmp_path, None)
    err = capsys.readouterr().err
    assert "last-activity=" in err
    # Just-created file should be 0s or seconds ago — never "?".
    assert "last-activity=?" not in err


# --- _format_age: short human-friendly duration --------------------------

def test_format_age_seconds(pila):
    assert pila._format_age(0) == "0s ago"
    assert pila._format_age(5) == "5s ago"
    assert pila._format_age(59) == "59s ago"


def test_format_age_minutes(pila):
    assert pila._format_age(60) == "1m ago"
    assert pila._format_age(180) == "3m ago"
    assert pila._format_age(3599) == "59m ago"


def test_format_age_hours(pila):
    assert pila._format_age(3600) == "1h ago"
    assert pila._format_age(3600 + 720) == "1h12m ago"
    assert pila._format_age(2 * 3600 + 5 * 60) == "2h05m ago"


def test_format_age_days(pila):
    assert pila._format_age(86400) == "1d ago"
    assert pila._format_age(86400 + 4 * 3600) == "1d4h ago"
    assert pila._format_age(5 * 86400) == "5d ago"


def test_format_age_negative_clamps_to_zero(pila):
    """A negative duration (e.g. from clock skew) must not produce a
    nonsense string — clamp to 0s rather than render "-12s ago"."""
    assert pila._format_age(-10) == "0s ago"
