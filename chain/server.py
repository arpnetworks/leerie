"""chain.server — stdlib HTTP server for the leerie-chain orchestrator app.

Six endpoints (the five launcher chain verbs from QUEUE_JOBS.md plus the
webhook receiver):

  POST /chains
      Create a new chain. Request body (JSON):
        {
          "target": "<repo https url>",
          "runs": [
            {"prompt": "<task text>", "wave": "0"},
            {"prompt": "<task text>", "wave": "1"},
            ...
          ]
        }
      Clones the target repo, creates the stage-<chain_id> branch, launches
      all wave 0 machines immediately via the Fly Machines API, and persists
      the chain in SQLite. Returns 201 with the full chain snapshot.

  GET /chains
      List all chains as a JSON array (no run rows; call GET /chains/<id>
      for a full snapshot). Mirrors ``leerie --list-chains``.

  GET /chains/<id>
      Return the chain snapshot for *id* as JSON, or 404 if not found.

  GET /chains/<id>/log
      Return a JSON event history derived from the chain's run-status
      transitions (one event per run state change). Polling-only; true
      streaming requires a per-chain log file that the current data
      model does not maintain. Returns 404 if the chain is not found.

  DELETE /chains/<id>
      Cancel a chain. Destroys every still-running per-run Fly machine via
      the Machines API, then transitions the chain to ``'cancelled'``.
      Returns 200 with the updated snapshot, or 404 if not found. Idempotent
      against an already-terminal chain (returns 200 with the snapshot).

  POST /webhooks/fly
      Receive Fly machine-exit events. Verifies the HMAC-SHA256 signature
      in the ``fly-signature-256`` header; rejects with 400 on mismatch.
      Dispatches to ``handle_machine_exit`` from chain.webhooks; if all
      runs in the current wave are done, advances to the next wave and
      launches its machines.

The handler is intentionally stateless across requests — all mutable state
lives in the ``ChainState`` SQLite DB. The server is single-threaded on a
single-process Fly app; all requests are serialised on the Python GIL.

Usage::

    from chain.server import make_server
    from chain.state import ChainState
    from chain.config import load_settings

    cs = ChainState.init_db("/data/chain.db")
    settings = load_settings()
    httpd = make_server(cs, settings, host="0.0.0.0", port=8080)
    httpd.serve_forever()
"""
from __future__ import annotations

import json
import os
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from chain import fly_client, git_ops
from chain.config import Settings
from chain.state import ChainState
from chain.webhooks import WebhookError, handle_machine_exit


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------

def make_server(
    cs: ChainState,
    settings: Settings,
    host: str = "0.0.0.0",
    port: int = 8080,
) -> HTTPServer:
    """Return an ``HTTPServer`` bound to *host*:*port* using the given state.

    The ``ChainState`` and ``Settings`` are captured in the handler class via
    a closure so the ``BaseHTTPRequestHandler`` constructor interface (which
    takes no custom kwargs) is unchanged.
    """

    class _Handler(ChainHTTPHandler):
        _cs = cs
        _settings = settings

    return HTTPServer((host, port), _Handler)


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class ChainHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for the leerie-chain API.

    Subclasses must set ``_cs`` and ``_settings`` as class attributes before
    the server is started (``make_server`` does this via an inner class).
    """

    _cs: ChainState
    _settings: Settings

    # Silence the default per-request log line; callers who want logging can
    # override this or re-enable it by overriding log_message.
    def log_message(self, fmt: str, *args: Any) -> None:
        pass

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def do_GET(self) -> None:
        if self.path == "/chains":
            self._handle_list_chains()
            return
        if self.path.startswith("/chains/"):
            tail = self.path[len("/chains/"):]
            # /chains/<id>/log — event history for the chain
            if tail.endswith("/log") and tail.count("/") == 1:
                chain_id = tail[: -len("/log")]
                self._handle_get_chain_log(chain_id)
                return
            # /chains/<id> — full snapshot
            if "/" not in tail:
                self._handle_get_chain(tail)
                return
        self._send_json(404, {"error": f"not found: {self.path}"})

    def do_POST(self) -> None:
        if self.path == "/chains":
            self._handle_post_chains()
        elif self.path == "/webhooks/fly":
            self._handle_post_webhook()
        else:
            self._send_json(404, {"error": f"not found: {self.path}"})

    def do_DELETE(self) -> None:
        if self.path.startswith("/chains/") and self.path.count("/") == 2:
            chain_id = self.path[len("/chains/"):]
            self._handle_delete_chain(chain_id)
        else:
            self._send_json(404, {"error": f"not found: {self.path}"})

    # ------------------------------------------------------------------
    # GET /chains/<id>
    # ------------------------------------------------------------------

    def _handle_get_chain(self, chain_id: str) -> None:
        snap = self._cs.load_chain(chain_id)
        if snap is None:
            self._send_json(404, {"error": f"chain {chain_id!r} not found"})
            return
        self._send_json(200, snap)

    # ------------------------------------------------------------------
    # GET /chains  (list)
    # ------------------------------------------------------------------

    def _handle_list_chains(self) -> None:
        # list_chains returns one row per chain (no run rows). Callers who
        # want runs walk to GET /chains/<id> for the full snapshot.
        chains = self._cs.list_chains()
        self._send_json(200, {"chains": chains})

    # ------------------------------------------------------------------
    # GET /chains/<id>/log  (event history)
    # ------------------------------------------------------------------

    def _handle_get_chain_log(self, chain_id: str) -> None:
        # First-cut event log: derive a chronological event list from the
        # run rows' current state. The chain DB does not retain a full
        # transition history (only the latest status + updated_at per run),
        # so this is a snapshot of the latest event per run, ordered by
        # updated_at. True streaming would need a per-chain log file; that
        # is a follow-up — see DESIGN.md §19 "Chain attach is polling".
        snap = self._cs.load_chain(chain_id)
        if snap is None:
            self._send_json(404, {"error": f"chain {chain_id!r} not found"})
            return
        events: list[dict[str, Any]] = []
        # Chain-level top entry so a poller sees the wave/status without
        # having to also call GET /chains/<id>.
        events.append({
            "at": snap["updated_at"],
            "kind": "chain",
            "status": snap["status"],
            "wave_state": snap["wave_state"],
        })
        for run in snap["runs"]:
            events.append({
                "at": run["updated_at"],
                "kind": "run",
                "run_id": run["id"],
                "wave": run["wave"],
                "status": run["status"],
                "machine_id": run.get("machine_id"),
            })
        events.sort(key=lambda e: e["at"])
        self._send_json(200, {"chain_id": chain_id, "events": events})

    # ------------------------------------------------------------------
    # DELETE /chains/<id>  (cancel)
    # ------------------------------------------------------------------

    def _handle_delete_chain(self, chain_id: str) -> None:
        snap = self._cs.load_chain(chain_id)
        if snap is None:
            self._send_json(404, {"error": f"chain {chain_id!r} not found"})
            return
        # Destroy every still-running per-run Fly machine. We mark each
        # one failed in the DB *before* the destroy call so a slow/erroring
        # API doesn't leave the DB claiming it's running. fly_client treats
        # 404 as success (machine already gone), so this is safe to retry.
        # The chain-status transition is wrapped in try/finally so the
        # "chain is cancelled" guarantee holds even if a future code path
        # introduces a new exception type through transition_run /
        # destroy_machine — without the finally, a mid-loop raise would
        # leave the chain stuck in an active wave with some runs failed.
        destroy_errors: list[str] = []
        try:
            for run in snap["runs"]:
                if run["status"] != "running":
                    continue
                machine_id = run.get("machine_id")
                if not machine_id:
                    continue
                self._cs.transition_run(run["id"], "failed")
                try:
                    fly_client.destroy_machine(machine_id)
                except fly_client.FlyClientError as exc:
                    destroy_errors.append(f"{machine_id}: {exc}")
        finally:
            self._cs.transition_chain(chain_id, "cancelled")
        updated = self._cs.load_chain(chain_id)
        if destroy_errors:
            # Surface partial failures but still report the cancellation:
            # the DB is consistent (chain is cancelled, runs marked failed),
            # only the Fly-side teardown was incomplete. Caller may want
            # to retry DELETE — it's idempotent.
            self._send_json(
                200,
                {
                    "chain": updated,
                    "warnings": [f"machine destroy failed: {e}" for e in destroy_errors],
                },
            )
            return
        self._send_json(200, {"chain": updated})

    # ------------------------------------------------------------------
    # POST /chains
    # ------------------------------------------------------------------

    def _handle_post_chains(self) -> None:
        body = self._read_json_body()
        if body is None:
            return

        target: str | None = body.get("target")
        runs_raw: list[Any] | None = body.get("runs")

        if not target or not isinstance(target, str):
            self._send_json(400, {"error": "'target' is required and must be a string"})
            return
        if not runs_raw or not isinstance(runs_raw, list):
            self._send_json(400, {"error": "'runs' is required and must be a non-empty list"})
            return

        run_prompts: list[tuple[str, str]] = []
        for item in runs_raw:
            if not isinstance(item, dict):
                self._send_json(400, {"error": "each run must be an object with 'prompt' and 'wave'"})
                return
            prompt = item.get("prompt", "")
            wave = item.get("wave", "")
            if not prompt or not isinstance(wave, str) or not wave.isdigit():
                self._send_json(
                    400,
                    {"error": "each run must have a non-empty 'prompt' and 'wave' (non-negative integer string)"},
                )
                return
            run_prompts.append((str(prompt), str(wave)))

        # Persist the chain row before any external I/O so partial failures
        # are visible in the DB (chain stays 'running' — caller can query it).
        try:
            chain_id = self._cs.create_chain(target=target, run_prompts=run_prompts)
        except Exception as exc:
            self._send_json(500, {"error": f"failed to create chain: {exc}"})
            return

        # Clone the target repo and create the stage branch in a tempdir.
        # git_ops functions call sys.exit on failure; we catch SystemExit so
        # the server process stays alive and we can return a structured error.
        clone_dir = tempfile.mkdtemp(prefix=f"leerie-chain-{chain_id}-")
        try:
            repo_path = git_ops.clone_target(
                repo_url=target,
                pat=self._settings.gh_dispatch_pat,
                clone_dir=clone_dir,
            )
            git_ops.create_stage_branch(repo_path, chain_id)
        except SystemExit as exc:
            self._send_json(500, {"error": f"git setup failed (exit {exc.code})"})
            return
        except Exception as exc:
            self._send_json(500, {"error": f"git setup failed: {exc}"})
            return

        # Launch all wave 0 machines.
        snap = self._cs.load_chain(chain_id)
        if snap is None:
            self._send_json(500, {"error": "chain row disappeared after creation"})
            return

        fly_image = os.environ.get("LEERIE_IMAGE", "registry.fly.io/leerie:latest")
        fly_region = os.environ.get("LEERIE_REGION", "iad")

        for run in snap["runs"]:
            if run["wave"] != "0":
                continue
            try:
                machine_id = fly_client.launch_machine(
                    image=fly_image,
                    env={
                        "LEERIE_CHAIN_ID": chain_id,
                        "LEERIE_CHAIN_RUN_ID": run["id"],
                        "LEERIE_TASK": run["prompt"],
                        "LEERIE_TARGET_REPO": target,
                    },
                    region=fly_region,
                )
            except fly_client.FlyClientError as exc:
                self._send_json(500, {"error": f"failed to launch machine for run {run['id']}: {exc}"})
                return
            self._cs.transition_run(run["id"], "running", machine_id=machine_id)

        # Return the refreshed snapshot.
        updated_snap = self._cs.load_chain(chain_id)
        self._send_json(201, updated_snap)

    # ------------------------------------------------------------------
    # POST /webhooks/fly
    # ------------------------------------------------------------------

    def _handle_post_webhook(self) -> None:
        raw_body = self._read_raw_body()
        if raw_body is None:
            return

        sig_header = self.headers.get("fly-signature-256", "")

        # Parse JSON before calling handle_machine_exit so we have the dict.
        try:
            payload: dict[str, Any] = json.loads(raw_body)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._send_json(400, {"error": f"invalid JSON body: {exc}"})
            return

        try:
            handle_machine_exit(
                cs=self._cs,
                payload=payload,
                secret=self._settings.chain_webhook_secret,
                raw_body=raw_body,
                sig_header=sig_header,
            )
        except WebhookError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except Exception as exc:
            self._send_json(500, {"error": f"webhook handler error: {exc}"})
            return

        # After a successful machine exit, check whether all runs in the
        # current wave are done and it's time to launch the next wave.
        self._maybe_advance_wave(payload)

        self._send_json(200, {"ok": True})

    def _maybe_advance_wave(self, payload: dict[str, Any]) -> None:
        """If all runs in the current wave are done, advance to the next wave."""
        machine_id: str | None = (
            payload.get("machine_id")
            or payload.get("id")
            or payload.get("instance_id")
            or None
        )
        if not machine_id:
            return

        chain_id_or_none = self._cs.find_chain_id_by_machine_id(machine_id)
        if chain_id_or_none is None:
            return
        chain_id: str = chain_id_or_none

        snap = self._cs.load_chain(chain_id)
        if snap is None:
            return

        ws = snap["wave_state"]
        if not ws.startswith("wave_"):
            return
        current_idx = int(ws[5:])
        current_wave = str(current_idx)

        current_runs = [r for r in snap["runs"] if r["wave"] == current_wave]
        if not all(r["status"] in ("done", "failed") for r in current_runs):
            return

        if any(r["status"] == "failed" for r in current_runs):
            self._cs.transition_chain(chain_id, "paused")
            return

        next_idx = current_idx + 1
        next_wave = str(next_idx)
        next_runs = [r for r in snap["runs"] if r["wave"] == next_wave]

        if not next_runs:
            self._cs.advance_wave(chain_id, "done")
            self._cs.transition_chain(chain_id, "done")
            return

        self._cs.advance_wave(chain_id, f"wave_{next_idx}")

        fly_image = os.environ.get("LEERIE_IMAGE", "registry.fly.io/leerie:latest")
        fly_region = os.environ.get("LEERIE_REGION", "iad")
        target = snap["target"]

        for run in next_runs:
            try:
                mid = fly_client.launch_machine(
                    image=fly_image,
                    env={
                        "LEERIE_CHAIN_ID": chain_id,
                        "LEERIE_CHAIN_RUN_ID": run["id"],
                        "LEERIE_TASK": run["prompt"],
                        "LEERIE_TARGET_REPO": target,
                    },
                    region=fly_region,
                )
            except fly_client.FlyClientError:
                self._cs.transition_chain(chain_id, "failed")
                return
            self._cs.transition_run(run["id"], "running", machine_id=mid)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _read_raw_body(self) -> bytes | None:
        """Read and return the raw request body bytes."""
        length_str = self.headers.get("Content-Length", "0")
        try:
            length = int(length_str)
        except ValueError:
            self._send_json(400, {"error": f"invalid Content-Length: {length_str!r}"})
            return None
        return self.rfile.read(length)

    def _read_json_body(self) -> dict[str, Any] | None:
        """Read, parse, and return the request body as a dict, or send 400."""
        raw = self._read_raw_body()
        if raw is None:
            return None
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._send_json(400, {"error": f"invalid JSON body: {exc}"})
            return None
        if not isinstance(data, dict):
            self._send_json(400, {"error": "request body must be a JSON object"})
            return None
        return data

    def _send_json(self, status: int, body: Any) -> None:
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
