"""Tests for _get_progress() — the helper that computes the
(done, total, wave_idx, wave_total) tuple shown in each inline log
line once waves are scheduled.

_get_progress returns None before planning (no waves key) and once
waves exist it counts terminal statuses against the total subtask
count and surfaces the in-flight wave index (`completed_waves + 1`).
Terminal statuses are complete, failed, and blocked — anything else
(in_progress, pending, etc.) does not count as done.
"""
from __future__ import annotations

from types import SimpleNamespace


def test_no_waves_returns_none(leerie):
    """Before planning, st.data has no 'waves' key. Returns None so
    classifier/planner workers emit no progress prefix."""
    st = SimpleNamespace(data={})
    assert leerie._get_progress(st) is None


def test_empty_waves_returns_none(leerie):
    """waves=[] means planning produced no subtasks. Returns None
    rather than (0, 0, …) to avoid showing a misleading '[0/0]' prefix."""
    st = SimpleNamespace(data={"waves": [], "subtask_status": {}})
    assert leerie._get_progress(st) is None


def test_all_pending_returns_zero_done(leerie):
    """When waves exist but no subtask has reached a terminal status,
    done=0 and total equals the sum of subtask counts across waves.
    With no completed_waves, the in-flight wave is wave 1."""
    st = SimpleNamespace(data={
        "waves": [["a", "b"], ["c"]],
        "subtask_status": {},
    })
    assert leerie._get_progress(st) == (0, 3, 1, 2)


def test_some_terminal_counted(leerie):
    """Only complete and failed count as terminal; in_progress does not.
    This is the common mid-run state: some done, some still running."""
    st = SimpleNamespace(data={
        "waves": [["a", "b", "c"]],
        "subtask_status": {"a": "complete", "b": "failed", "c": "in_progress"},
    })
    assert leerie._get_progress(st) == (2, 3, 1, 1)


def test_all_terminal(leerie):
    """All subtasks in a terminal state → done == total."""
    st = SimpleNamespace(data={
        "waves": [["a", "b"]],
        "subtask_status": {"a": "complete", "b": "blocked"},
    })
    assert leerie._get_progress(st) == (2, 2, 1, 1)


def test_blocked_counted_as_terminal(leerie):
    """'blocked' is a terminal status — a blocked subtask has stopped
    making progress and must be counted as done for the fraction."""
    st = SimpleNamespace(data={
        "waves": [["a"]],
        "subtask_status": {"a": "blocked"},
    })
    assert leerie._get_progress(st) == (1, 1, 1, 1)


def test_wave_index_advances_with_completed_waves(leerie):
    """`completed_waves` is incremented after each wave settles. The
    in-flight wave is `completed_waves + 1`, so a worker spawned in
    wave 2 sees `wave_idx = 2`. This is the test that pins the wave
    label semantics distinct from the done counter."""
    st = SimpleNamespace(data={
        "waves": [["a"], ["b", "c"], ["d"]],
        "subtask_status": {"a": "complete"},
        "completed_waves": 1,
    })
    assert leerie._get_progress(st) == (1, 4, 2, 3)
