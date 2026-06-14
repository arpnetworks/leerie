"""Tests for chain.server — the leerie-chain HTTP server.

The server is spun up in-process using a real HTTPServer on an ephemeral
port (port 0 — OS picks a free port).  fly_client.launch_machine and
git_ops.clone_target / create_stage_branch are stubbed so no live Fly API
calls or git network access is required.

Test coverage:
  POST /chains   — creates a chain row, stubs launch_machine for wave 0
  GET  /chains/<id>  — returns the snapshot
  GET  /chains/<missing-id>  — returns 404
  POST /webhooks/fly
      — Wave-A-final exit event triggers wave 1 launch
      — Bad signature returns 400
      — Non-exit event is silently ignored (200 ok)
      — wave 0 failure pauses chain (no wave 1 launch)
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
import urllib.request
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from chain.config import Settings
from chain.server import make_server
from chain.state import ChainState

_FLY_EXIT_EVENT = "io.fly.machine.exited"
_SECRET = "test-webhook-secret"
_SETTINGS = Settings(
    gh_dispatch_pat="test-pat",
    fly_api_token="test-fly-token",
    chain_webhook_secret=_SECRET,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def cs() -> ChainState:
    return ChainState.init_db(":memory:")


@pytest.fixture()
def server_url(cs: ChainState, monkeypatch: pytest.MonkeyPatch):
    """Start the HTTP server on an ephemeral port in a background thread.

    Yields the base URL ``http://127.0.0.1:<port>``.
    """
    # Stub git_ops so no real git operations happen.
    monkeypatch.setattr(
        "chain.server.git_ops.clone_target",
        lambda repo_url, pat, clone_dir: _fake_clone(clone_dir),
    )
    monkeypatch.setattr(
        "chain.server.git_ops.create_stage_branch",
        lambda repo_path, chain_id, base_branch="main": f"stage-{chain_id}",
    )

    httpd = make_server(cs, _SETTINGS, host="127.0.0.1", port=0)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.handle_request, daemon=True)
    # We start a thread that handles ONE request at a time. Use serve_forever
    # instead for multi-request tests, but most test helpers dispatch one call.
    # Use serve_forever with a shorter poll so shutdown is fast.
    thread = threading.Thread(target=httpd.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    httpd.shutdown()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_clone(clone_dir: str) -> "Path":
    from pathlib import Path
    p = Path(clone_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _sign(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"hmac-sha256={digest}"


def _post(url: str, body: Any, extra_headers: dict[str, str] | None = None) -> tuple[int, dict]:
    payload = json.dumps(body).encode()
    headers = {"Content-Type": "application/json", "Content-Length": str(len(payload))}
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=payload, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _get(url: str) -> tuple[int, dict]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _delete(url: str) -> tuple[int, dict]:
    req = urllib.request.Request(url, method="DELETE")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _post_webhook(base_url: str, payload: Any, secret: str = _SECRET) -> tuple[int, dict]:
    body = json.dumps(payload).encode()
    sig = _sign(secret, body)
    req = urllib.request.Request(
        f"{base_url}/webhooks/fly",
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),
            "fly-signature-256": sig,
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


# ---------------------------------------------------------------------------
# POST /chains
# ---------------------------------------------------------------------------

class TestPostChains:
    def test_creates_chain_returns_201(
        self, server_url: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        machine_ids = iter(["m-001", "m-002"])

        with patch("chain.server.fly_client.launch_machine", side_effect=lambda **kw: next(machine_ids)):
            status, body = _post(
                f"{server_url}/chains",
                {
                    "target": "https://github.com/org/repo",
                    "runs": [
                        {"prompt": "Task A1", "wave": "0"},
                        {"prompt": "Task A2", "wave": "0"},
                    ],
                },
            )

        assert status == 201
        assert "id" in body
        assert body["target"] == "https://github.com/org/repo"

    def test_launches_wave_0_machines(
        self, server_url: str, cs: ChainState
    ) -> None:
        launched: list[dict] = []

        def fake_launch(**kw: Any) -> str:
            launched.append(kw)
            return f"m-{len(launched):03d}"

        with patch("chain.server.fly_client.launch_machine", side_effect=fake_launch):
            status, body = _post(
                f"{server_url}/chains",
                {
                    "target": "https://github.com/org/repo",
                    "runs": [
                        {"prompt": "wave 0 Task", "wave": "0"},
                        {"prompt": "wave 1 Task", "wave": "1"},
                    ],
                },
            )

        assert status == 201
        # Only wave 0 should have been launched.
        assert len(launched) == 1

    def test_does_not_launch_wave_1_machines_on_create(
        self, server_url: str, cs: ChainState
    ) -> None:
        launched_waves: list[str] = []

        def fake_launch(**kw: Any) -> str:
            # The env dict in the server call does not encode the wave; we
            # infer by checking how many calls happened vs wave composition.
            launched_waves.append("launched")
            return f"m-{len(launched_waves):03d}"

        with patch("chain.server.fly_client.launch_machine", side_effect=fake_launch):
            _, body = _post(
                f"{server_url}/chains",
                {
                    "target": "https://github.com/org/repo",
                    "runs": [
                        {"prompt": "A1", "wave": "0"},
                        {"prompt": "B1", "wave": "1"},
                        {"prompt": "B2", "wave": "1"},
                    ],
                },
            )

        # Only wave 0 (1 run) launched.
        assert len(launched_waves) == 1

    def test_wave_0_runs_marked_running(
        self, server_url: str, cs: ChainState
    ) -> None:
        with patch("chain.server.fly_client.launch_machine", return_value="m-test"):
            _, body = _post(
                f"{server_url}/chains",
                {
                    "target": "https://github.com/org/repo",
                    "runs": [{"prompt": "A task", "wave": "0"}],
                },
            )

        chain_id = body["id"]
        snap = cs.load_chain(chain_id)
        assert snap is not None
        wave_0_run = next(r for r in snap["runs"] if r["wave"] == "0")
        assert wave_0_run["status"] == "running"
        assert wave_0_run["machine_id"] == "m-test"

    def test_missing_target_returns_400(self, server_url: str) -> None:
        status, body = _post(
            f"{server_url}/chains",
            {"runs": [{"prompt": "p", "wave": "0"}]},
        )
        assert status == 400
        assert "target" in body.get("error", "").lower()

    def test_missing_runs_returns_400(self, server_url: str) -> None:
        status, body = _post(
            f"{server_url}/chains",
            {"target": "https://github.com/org/repo"},
        )
        assert status == 400

    def test_invalid_wave_returns_400(self, server_url: str) -> None:
        status, body = _post(
            f"{server_url}/chains",
            {
                "target": "https://github.com/org/repo",
                "runs": [{"prompt": "p", "wave": "c"}],
            },
        )
        assert status == 400

    def test_empty_runs_returns_400(self, server_url: str) -> None:
        status, body = _post(
            f"{server_url}/chains",
            {
                "target": "https://github.com/org/repo",
                "runs": [],
            },
        )
        assert status == 400

    def test_malformed_body_does_not_create_chain(
        self, server_url: str, cs: ChainState
    ) -> None:
        """A 400 response must not persist a chain row in the DB."""
        status, _ = _post(
            f"{server_url}/chains",
            {"runs": [{"prompt": "p", "wave": "0"}]},  # missing target
        )
        assert status == 400
        assert cs.list_chains() == []

    def test_invalid_json_body_returns_400(self, server_url: str) -> None:
        """Non-JSON content in the request body returns 400."""
        payload = b"not-json"
        req = urllib.request.Request(
            f"{server_url}/chains",
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(payload)),
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                status = resp.status
        except urllib.error.HTTPError as exc:
            status = exc.code
        assert status == 400


# ---------------------------------------------------------------------------
# GET /chains/<id>
# ---------------------------------------------------------------------------

class TestGetChain:
    def test_returns_chain_snapshot(
        self, server_url: str, cs: ChainState
    ) -> None:
        chain_id = cs.create_chain(
            target="https://github.com/org/repo",
            run_prompts=[("Task A", "0"), ("Task B", "1")],
        )
        status, body = _get(f"{server_url}/chains/{chain_id}")
        assert status == 200
        assert body["id"] == chain_id
        assert body["target"] == "https://github.com/org/repo"
        assert len(body["runs"]) == 2

    def test_returns_404_for_missing_chain(self, server_url: str) -> None:
        status, body = _get(f"{server_url}/chains/nonexistent-id")
        assert status == 404

    def test_snapshot_includes_run_fields(
        self, server_url: str, cs: ChainState
    ) -> None:
        chain_id = cs.create_chain(
            target="https://github.com/org/repo",
            run_prompts=[("Task A", "0")],
        )
        snap = cs.load_chain(chain_id)
        assert snap is not None
        run_id = snap["runs"][0]["id"]
        cs.transition_run(run_id, "running", machine_id="fly-m-123")

        _, body = _get(f"{server_url}/chains/{chain_id}")
        run = body["runs"][0]
        assert run["status"] == "running"
        assert run["machine_id"] == "fly-m-123"


# ---------------------------------------------------------------------------
# POST /webhooks/fly
# ---------------------------------------------------------------------------

class TestWebhookFly:
    def test_unsigned_webhook_returns_400(self, server_url: str) -> None:
        payload = {
            "type": _FLY_EXIT_EVENT,
            "machine_id": "m-unknown",
            "exit_code": 0,
        }
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{server_url}/webhooks/fly",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(body)),
                "fly-signature-256": "hmac-sha256=deadbeef",  # wrong
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                status = resp.status
        except urllib.error.HTTPError as exc:
            status = exc.code
        assert status == 400

    def test_valid_exit_event_marks_run_done(
        self, server_url: str, cs: ChainState
    ) -> None:
        chain_id = cs.create_chain(
            target="https://github.com/org/repo",
            run_prompts=[("Task A", "0")],
        )
        snap = cs.load_chain(chain_id)
        assert snap is not None
        run_id = snap["runs"][0]["id"]
        cs.transition_run(run_id, "running", machine_id="m-exit-test")

        payload = {
            "type": _FLY_EXIT_EVENT,
            "machine_id": "m-exit-test",
            "exit_code": 0,
        }
        status, body = _post_webhook(server_url, payload)
        assert status == 200
        assert body.get("ok") is True

        updated = cs.load_chain(chain_id)
        assert updated is not None
        assert updated["runs"][0]["status"] == "done"

    def test_wave_0_complete_launches_wave_1(
        self, server_url: str, cs: ChainState
    ) -> None:
        """When the last wave 0 run exits 0, wave 1 machines are launched."""
        chain_id = cs.create_chain(
            target="https://github.com/org/repo",
            run_prompts=[
                ("wave 0 task", "0"),
                ("wave 1 task 1", "1"),
                ("wave 1 task 2", "1"),
            ],
        )
        snap = cs.load_chain(chain_id)
        assert snap is not None
        run_0 = next(r for r in snap["runs"] if r["wave"] == "0")
        cs.transition_run(run_0["id"], "running", machine_id="m-wave-0")

        wave_1_launches: list[str] = []

        def fake_launch(**kw: Any) -> str:
            wave_1_launches.append("launched")
            return f"m-1-{len(wave_1_launches)}"

        with patch("chain.server.fly_client.launch_machine", side_effect=fake_launch):
            payload = {
                "type": _FLY_EXIT_EVENT,
                "machine_id": "m-wave-0",
                "exit_code": 0,
            }
            status, _ = _post_webhook(server_url, payload)

        assert status == 200
        # Both wave 1 runs must have been launched.
        assert len(wave_1_launches) == 2

        updated = cs.load_chain(chain_id)
        assert updated is not None
        assert updated["wave_state"] == "wave_1"
        wave_1_runs = [r for r in updated["runs"] if r["wave"] == "1"]
        assert all(r["status"] == "running" for r in wave_1_runs)

    def test_wave_0_failure_pauses_chain(
        self, server_url: str, cs: ChainState
    ) -> None:
        """A non-zero wave 0 exit pauses the chain — no wave 1 launch."""
        chain_id = cs.create_chain(
            target="https://github.com/org/repo",
            run_prompts=[
                ("wave 0 task", "0"),
                ("wave 1 task", "1"),
            ],
        )
        snap = cs.load_chain(chain_id)
        assert snap is not None
        run_0 = next(r for r in snap["runs"] if r["wave"] == "0")
        cs.transition_run(run_0["id"], "running", machine_id="m-fail")

        launched: list[str] = []
        with patch(
            "chain.server.fly_client.launch_machine",
            side_effect=lambda **kw: launched.append("1") or "m-1-1",
        ):
            payload = {
                "type": _FLY_EXIT_EVENT,
                "machine_id": "m-fail",
                "exit_code": 1,
            }
            status, _ = _post_webhook(server_url, payload)

        assert status == 200
        assert len(launched) == 0

        updated = cs.load_chain(chain_id)
        assert updated is not None
        assert updated["status"] == "paused"
        # wave_state remains wave_0 — never advanced.
        assert updated["wave_state"] == "wave_0"

    def test_non_exit_event_ignored(
        self, server_url: str, cs: ChainState
    ) -> None:
        """Non-exit Fly events are accepted (200) but do not change state."""
        chain_id = cs.create_chain(
            target="https://github.com/org/repo",
            run_prompts=[("Task A", "0")],
        )
        snap = cs.load_chain(chain_id)
        assert snap is not None
        run_id = snap["runs"][0]["id"]
        cs.transition_run(run_id, "running", machine_id="m-started")

        payload = {
            "type": "io.fly.machine.started",
            "machine_id": "m-started",
        }
        status, body = _post_webhook(server_url, payload)
        assert status == 200

        updated = cs.load_chain(chain_id)
        assert updated is not None
        assert updated["runs"][0]["status"] == "running"

    def test_missing_sig_header_returns_400(self, server_url: str) -> None:
        payload = {
            "type": _FLY_EXIT_EVENT,
            "machine_id": "m-unknown",
            "exit_code": 0,
        }
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{server_url}/webhooks/fly",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(body)),
                # no fly-signature-256 header
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                status = resp.status
        except urllib.error.HTTPError as exc:
            status = exc.code
        assert status == 400

    def test_wave_0_done_no_wave_1_marks_chain_done(
        self, server_url: str, cs: ChainState
    ) -> None:
        """When wave 0 completes and there is no wave 1, the chain is marked done."""
        chain_id = cs.create_chain(
            target="https://github.com/org/repo",
            run_prompts=[("Task A only", "0")],
        )
        snap = cs.load_chain(chain_id)
        assert snap is not None
        run_0 = snap["runs"][0]
        cs.transition_run(run_0["id"], "running", machine_id="m-solo")

        payload = {
            "type": _FLY_EXIT_EVENT,
            "machine_id": "m-solo",
            "exit_code": 0,
        }
        status, _ = _post_webhook(server_url, payload)
        assert status == 200

        updated = cs.load_chain(chain_id)
        assert updated is not None
        assert updated["wave_state"] == "done"
        assert updated["status"] == "done"


# ---------------------------------------------------------------------------
# GET /chains  (list)
# ---------------------------------------------------------------------------

class TestListChains:
    def test_empty_db_returns_empty_list(self, server_url: str) -> None:
        status, body = _get(f"{server_url}/chains")
        assert status == 200
        assert body == {"chains": []}

    def test_lists_all_chains(self, server_url: str, cs: ChainState) -> None:
        c1 = cs.create_chain(
            target="https://github.com/org/r1",
            run_prompts=[("A", "0")],
        )
        c2 = cs.create_chain(
            target="https://github.com/org/r2",
            run_prompts=[("B", "0")],
        )
        status, body = _get(f"{server_url}/chains")
        assert status == 200
        ids = {c["id"] for c in body["chains"]}
        assert ids == {c1, c2}

    def test_list_does_not_include_runs(
        self, server_url: str, cs: ChainState
    ) -> None:
        """The list endpoint is a summary; per-chain runs live behind GET /chains/<id>."""
        cs.create_chain(
            target="https://github.com/org/r",
            run_prompts=[("A", "0"), ("B", "1")],
        )
        _, body = _get(f"{server_url}/chains")
        for c in body["chains"]:
            assert "runs" not in c


# ---------------------------------------------------------------------------
# GET /chains/<id>/log  (event history)
# ---------------------------------------------------------------------------

class TestGetChainLog:
    def test_returns_event_history(
        self, server_url: str, cs: ChainState
    ) -> None:
        chain_id = cs.create_chain(
            target="https://github.com/org/r",
            run_prompts=[("Task A", "0"), ("Task B", "1")],
        )
        status, body = _get(f"{server_url}/chains/{chain_id}/log")
        assert status == 200
        assert body["chain_id"] == chain_id
        # Three events: one chain-level + one per run.
        kinds = [e["kind"] for e in body["events"]]
        assert kinds.count("chain") == 1
        assert kinds.count("run") == 2

    def test_events_include_machine_id_after_transition(
        self, server_url: str, cs: ChainState
    ) -> None:
        chain_id = cs.create_chain(
            target="https://github.com/org/r",
            run_prompts=[("Task", "0")],
        )
        snap = cs.load_chain(chain_id)
        assert snap is not None
        cs.transition_run(snap["runs"][0]["id"], "running", machine_id="m-abc")

        _, body = _get(f"{server_url}/chains/{chain_id}/log")
        run_events = [e for e in body["events"] if e["kind"] == "run"]
        assert len(run_events) == 1
        assert run_events[0]["machine_id"] == "m-abc"
        assert run_events[0]["status"] == "running"

    def test_missing_chain_returns_404(self, server_url: str) -> None:
        status, _ = _get(f"{server_url}/chains/nonexistent-id/log")
        assert status == 404


# ---------------------------------------------------------------------------
# DELETE /chains/<id>  (cancel)
# ---------------------------------------------------------------------------

class TestDeleteChain:
    def test_cancels_chain_and_returns_snapshot(
        self, server_url: str, cs: ChainState
    ) -> None:
        chain_id = cs.create_chain(
            target="https://github.com/org/r",
            run_prompts=[("Task", "0")],
        )
        with patch("chain.server.fly_client.destroy_machine"):
            status, body = _delete(f"{server_url}/chains/{chain_id}")
        assert status == 200
        assert body["chain"]["id"] == chain_id
        assert body["chain"]["status"] == "cancelled"

    def test_destroys_running_machines(
        self, server_url: str, cs: ChainState
    ) -> None:
        chain_id = cs.create_chain(
            target="https://github.com/org/r",
            run_prompts=[("A1", "0"), ("A2", "0"), ("B1", "1")],
        )
        snap = cs.load_chain(chain_id)
        assert snap is not None
        running_machines = ["m-running-1", "m-running-2"]
        for run, mid in zip(
            [r for r in snap["runs"] if r["wave"] == "0"],
            running_machines,
        ):
            cs.transition_run(run["id"], "running", machine_id=mid)

        destroyed: list[str] = []

        def fake_destroy(machine_id: str) -> None:
            destroyed.append(machine_id)

        with patch("chain.server.fly_client.destroy_machine", side_effect=fake_destroy):
            status, body = _delete(f"{server_url}/chains/{chain_id}")
        assert status == 200
        assert set(destroyed) == set(running_machines)

    def test_skips_non_running_runs(
        self, server_url: str, cs: ChainState
    ) -> None:
        """Queued and already-done runs do not trigger destroy_machine calls."""
        chain_id = cs.create_chain(
            target="https://github.com/org/r",
            run_prompts=[("A", "0"), ("B", "0")],
        )
        snap = cs.load_chain(chain_id)
        assert snap is not None
        # One run is done, one is still queued — neither should be destroyed.
        cs.transition_run(snap["runs"][0]["id"], "done", machine_id="m-done")

        destroyed: list[str] = []
        with patch(
            "chain.server.fly_client.destroy_machine",
            side_effect=lambda m: destroyed.append(m),
        ):
            status, _ = _delete(f"{server_url}/chains/{chain_id}")
        assert status == 200
        assert destroyed == []

    def test_marks_running_runs_failed(
        self, server_url: str, cs: ChainState
    ) -> None:
        """Cancelling transitions still-running runs to 'failed' in the DB."""
        chain_id = cs.create_chain(
            target="https://github.com/org/r",
            run_prompts=[("A", "0")],
        )
        snap = cs.load_chain(chain_id)
        assert snap is not None
        cs.transition_run(snap["runs"][0]["id"], "running", machine_id="m-x")

        with patch("chain.server.fly_client.destroy_machine"):
            _delete(f"{server_url}/chains/{chain_id}")

        updated = cs.load_chain(chain_id)
        assert updated is not None
        assert updated["runs"][0]["status"] == "failed"
        assert updated["status"] == "cancelled"

    def test_missing_chain_returns_404(self, server_url: str) -> None:
        status, _ = _delete(f"{server_url}/chains/nonexistent-id")
        assert status == 404

    def test_destroy_error_is_reported_as_warning(
        self, server_url: str, cs: ChainState
    ) -> None:
        """If destroy_machine raises, DB state is still consistent and the
        warning is surfaced — the caller may retry the DELETE."""
        from chain import fly_client as _fc

        chain_id = cs.create_chain(
            target="https://github.com/org/r",
            run_prompts=[("A", "0")],
        )
        snap = cs.load_chain(chain_id)
        assert snap is not None
        cs.transition_run(snap["runs"][0]["id"], "running", machine_id="m-bad")

        with patch(
            "chain.server.fly_client.destroy_machine",
            side_effect=_fc.FlyClientError("nope"),
        ):
            status, body = _delete(f"{server_url}/chains/{chain_id}")
        assert status == 200
        assert body["chain"]["status"] == "cancelled"
        assert "warnings" in body
        assert any("nope" in w for w in body["warnings"])

    def test_idempotent_on_already_cancelled_chain(
        self, server_url: str, cs: ChainState
    ) -> None:
        chain_id = cs.create_chain(
            target="https://github.com/org/r",
            run_prompts=[("A", "0")],
        )
        with patch("chain.server.fly_client.destroy_machine"):
            _delete(f"{server_url}/chains/{chain_id}")
            # Assert the chain is already cancelled BEFORE the second
            # DELETE — without this, the final-state assertion below
            # would also pass if a buggy DELETE toggled the chain
            # through an intermediate state and back to cancelled.
            mid = cs.load_chain(chain_id)
            assert mid is not None and mid["status"] == "cancelled"
            status, body = _delete(f"{server_url}/chains/{chain_id}")
        assert status == 200
        assert body["chain"]["status"] == "cancelled"


# ---------------------------------------------------------------------------
# Launcher-server coupling: every URL the launcher hits must be a real route
# ---------------------------------------------------------------------------

class TestLauncherServerCoupling:
    """Bridge the launcher and the server: every (method, path) the bash
    launcher invokes via curl must land on a handler in chain/server.py.

    The bug class this prevents: launcher tests stub curl (so they happily
    pass with any URL) and server tests don't drive the missing endpoints
    (so the gap stays invisible). One coupling test closes the loop —
    same pattern as ``tests/test_retry_policy_strings.py`` which couples
    retry-policy markers to their check-function strings.
    """

    def test_every_launcher_curl_call_hits_a_real_route(
        self, server_url: str
    ) -> None:
        import re
        from pathlib import Path as _Path

        launcher = _Path(__file__).resolve().parent.parent / "leerie"
        # Collapse bash line-continuations so multi-line curl calls
        # (POST /chains uses several backslash-continued lines) appear as
        # one logical line to the regex.
        text = launcher.read_text().replace("\\\n", " ")

        # Grep for curl invocations in the chain-verb fast-paths. The
        # pattern matches the lines actually present in the launcher
        # (optional -X METHOD, then the URL with $_chain_url and a fixed path).
        # We allow $_chain_id / $_ck_chain_id / $_ca_chain_id placeholders.
        invocations: list[tuple[str, str]] = []
        for m in re.finditer(
            r'curl\s+-fsSL\s+(?:-X\s+(POST|DELETE|GET)\s+)?'
            r'[^\n]*?"\$_chain_url(/[^"\s]+)"',
            text,
            flags=re.DOTALL,
        ):
            method = m.group(1) or "GET"
            path = m.group(2)
            # Substitute live placeholders with literals so we can drive
            # the real server. The placeholders only appear in path
            # segments (chain ids), not in the route prefix.
            path = re.sub(r"\$_chain_id|\$_ck_chain_id|\$_ca_chain_id",
                          "coupling-probe", path)
            invocations.append((method, path))

        assert invocations, "no curl invocations parsed from launcher"
        # Every chain verb must be represented.
        verbs_seen = {(m, p) for m, p in invocations}
        assert ("POST", "/chains") in verbs_seen, "missing POST /chains"
        assert ("GET", "/chains") in verbs_seen, "missing GET /chains (--list-chains)"
        assert ("DELETE", "/chains/coupling-probe") in verbs_seen, (
            "missing DELETE /chains/<id> (--chain-kill)"
        )
        assert ("GET", "/chains/coupling-probe/log") in verbs_seen, (
            "missing GET /chains/<id>/log (--chain-attach)"
        )

        # For each (method, path), confirm the server's route exists.
        # Distinguish two kinds of 404:
        #   - "no such route"  → {"error": "not found: <path>"}   (real failure)
        #   - "chain id missing" → {"error": "chain 'X' not found"} (route is fine)
        # A 405 also signals a missing handler method.
        for method, path in invocations:
            url = f"{server_url}{path}"
            req_kwargs: dict[str, Any] = {"method": method}
            if method == "POST":
                # POST /chains expects a body. Drive a 400 (invalid body)
                # not a 404 (route missing) — the test only cares about
                # routing, not validation.
                req_kwargs["data"] = b"{}"
                req_kwargs["headers"] = {
                    "Content-Type": "application/json",
                    "Content-Length": "2",
                }
            req = urllib.request.Request(url, **req_kwargs)
            try:
                with urllib.request.urlopen(req) as resp:
                    status = resp.status
                    body = json.loads(resp.read())
            except urllib.error.HTTPError as exc:
                status = exc.code
                try:
                    body = json.loads(exc.read())
                except (ValueError, json.JSONDecodeError):
                    body = {}
            assert status != 405, (
                f"launcher route {method} {path}: server has no handler "
                f"for this HTTP method (405)"
            )
            if status == 404:
                err = (body or {}).get("error", "")
                assert err.startswith("chain "), (
                    f"launcher route {method} {path}: server returned a "
                    f"'no such route' 404 ({err!r}) — the route is missing"
                )


# ---------------------------------------------------------------------------
# Unknown routes
# ---------------------------------------------------------------------------

class TestRouting:
    def test_unknown_get_returns_404(self, server_url: str) -> None:
        status, _ = _get(f"{server_url}/unknown/path")
        assert status == 404

    def test_unknown_post_returns_404(self, server_url: str) -> None:
        status, _ = _post(f"{server_url}/unknown/path", {})
        assert status == 404

    def test_unknown_delete_returns_404(self, server_url: str) -> None:
        status, _ = _delete(f"{server_url}/unknown/path")
        assert status == 404
