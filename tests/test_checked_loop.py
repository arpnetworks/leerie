"""Tests for the mechanical-feedback retry loop infrastructure:
``_confidence_axes_clear``, ``_format_check_feedback``, and
``_run_checked_loop`` (CRITIC pattern — DESIGN §8 + §12).
"""
from __future__ import annotations

import asyncio

import pytest


# --- _confidence_axes_clear ---------------------------------------------- #

def test_axes_clear_all_above(leerie):
    assert leerie._confidence_axes_clear(
        {"a": 9.5, "b": 9.0}, ["a", "b"])


def test_axes_clear_one_below(leerie):
    assert not leerie._confidence_axes_clear(
        {"a": 8.9, "b": 9.5}, ["a", "b"])


def test_axes_clear_exactly_threshold(leerie):
    assert leerie._confidence_axes_clear(
        {"x": 9.0}, ["x"], threshold=9.0)


def test_axes_clear_missing_key(leerie):
    assert not leerie._confidence_axes_clear(
        {"a": 9.5}, ["a", "b"])


def test_axes_clear_non_numeric(leerie):
    assert not leerie._confidence_axes_clear(
        {"a": "high"}, ["a"])


def test_axes_clear_none_value(leerie):
    assert not leerie._confidence_axes_clear(
        {"a": None}, ["a"])


def test_axes_clear_empty_axes(leerie):
    assert leerie._confidence_axes_clear({"a": 1.0}, [])


def test_axes_clear_custom_threshold(leerie):
    assert leerie._confidence_axes_clear(
        {"a": 7.5}, ["a"], threshold=7.0)
    assert not leerie._confidence_axes_clear(
        {"a": 6.9}, ["a"], threshold=7.0)


# --- _format_check_feedback ---------------------------------------------- #

def test_format_feedback_structure(leerie):
    fb = leerie._format_check_feedback(
        ["PHANTOM_PATH: foo.py not found", "DANGLING_DEP: bar"], 0, 3)
    assert "round 1 of 3" in fb
    assert "2 issue(s)" in fb
    assert "PHANTOM_PATH" in fb
    assert "DANGLING_DEP" in fb
    assert "mechanically-derived" in fb


def test_format_feedback_single_issue(leerie):
    fb = leerie._format_check_feedback(["OVERSIZED: x"], 1, 2)
    assert "round 2 of 2" in fb
    assert "1 issue(s)" in fb


# --- _run_checked_loop --------------------------------------------------- #

@pytest.fixture()
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def _run(coro, loop=None):
    """Run an async coroutine synchronously."""
    if loop is None:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    return loop.run_until_complete(coro)


def test_loop_clean_on_first_round(leerie):
    calls = []

    async def invoke():
        calls.append(1)
        return {"status": "ready"}

    result, warnings = _run(leerie._run_checked_loop(
        invoke=invoke, check=lambda r: [], name="test", max_rounds=3))
    assert result == {"status": "ready"}
    assert warnings == []
    assert len(calls) == 1


def test_loop_retries_then_clears(leerie):
    attempt = [0]

    async def invoke():
        attempt[0] += 1
        if attempt[0] < 3:
            return {"bad": True}
        return {"good": True}

    def check(r):
        if r.get("bad"):
            return ["ISSUE: still bad"]
        return []

    result, warnings = _run(leerie._run_checked_loop(
        invoke=invoke, check=check, name="test", max_rounds=5))
    assert result == {"good": True}
    assert len(warnings) == 2
    assert attempt[0] == 3


def test_loop_exhausts_rounds(leerie):
    async def invoke():
        return {"always_bad": True}

    result, warnings = _run(leerie._run_checked_loop(
        invoke=invoke,
        check=lambda r: ["ISSUE: bad"],
        name="test",
        max_rounds=2,
    ))
    assert result == {"always_bad": True}
    assert len(warnings) == 2


def test_loop_crash_breaks(leerie):
    async def invoke():
        raise RuntimeError("boom")

    result, warnings = _run(leerie._run_checked_loop(
        invoke=invoke, check=lambda r: [], name="test", max_rounds=3))
    assert result is None
    assert len(warnings) == 1
    assert "crashed" in warnings[0]


def test_loop_none_result_breaks(leerie):
    async def invoke():
        return None

    result, warnings = _run(leerie._run_checked_loop(
        invoke=invoke, check=lambda r: [], name="test", max_rounds=3))
    assert result is None
    assert len(warnings) == 1
    assert "None" in warnings[0]


def test_loop_feedback_callback_called(leerie):
    feedback_received = []

    async def invoke():
        return {"x": 1}

    async def on_feedback(fb):
        feedback_received.append(fb)

    result, warnings = _run(leerie._run_checked_loop(
        invoke=invoke,
        check=lambda r: ["ISSUE: x"],
        name="test",
        max_rounds=3,
        make_feedback_prompt=on_feedback,
    ))
    assert len(feedback_received) == 2
    assert "ISSUE: x" in feedback_received[0]


def test_loop_feedback_not_called_on_last_round(leerie):
    feedback_received = []

    async def invoke():
        return {"x": 1}

    async def on_feedback(fb):
        feedback_received.append(fb)

    _run(leerie._run_checked_loop(
        invoke=invoke,
        check=lambda r: ["ISSUE: x"],
        name="test",
        max_rounds=2,
        make_feedback_prompt=on_feedback,
    ))
    assert len(feedback_received) == 1
