"""Tests for push_will_happen() — the orchestrator's intent-vs-mechanism
gate that decides whether pr_writer runs and what value goes into
run.json.no_push.

DESIGN §6 *Finalization*: `--no-push` on the orchestrator's argv is the
mechanism flag (on Fly the launcher always passes it because the
Machine has no GitHub auth); `--host-no-push true|false` is the user's
intent. The function answers: will a push happen on the host?

Truth table (`push_will_happen(no_push, host_no_push)`):

  no_push | host_no_push | result | meaning
  ------- | ------------ | ------ | ------------------------------------
  False   | None         | True   | local, default — push
  True    | None         | False  | local + user opted out — no push
  True    | False        | True   | Fly happy path — mechanism flag is
                                  | a lie; host pushes
  True    | True         | False  | Fly + user opted out — no push
"""
from __future__ import annotations


def test_local_default_pushes(leerie):
    """Local runtime, no opt-out — pushes by default."""
    assert leerie.push_will_happen(no_push=False, host_no_push=None) is True


def test_local_opt_out_skips(leerie):
    """Local runtime, --no-push — skips push."""
    assert leerie.push_will_happen(no_push=True, host_no_push=None) is False


def test_fly_happy_path_pushes_despite_mechanism_flag(leerie):
    """Fly runtime: in-Machine orchestrator always sees no_push=True
    because the launcher injects it as a mechanism flag (the Machine
    can't reach origin). But host_no_push=False says the user wants
    a push — intent wins."""
    assert leerie.push_will_happen(no_push=True, host_no_push=False) is True


def test_fly_user_opt_out_skips(leerie):
    """Fly runtime + user passed --no-push at launch.
    host_no_push=True overrides intent: host should not push."""
    assert leerie.push_will_happen(no_push=True, host_no_push=True) is False
