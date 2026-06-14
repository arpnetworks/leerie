---
description: Submit and manage a multi-run leerie chain. Use when the user wants to run a sequence of leerie runs (N sequential waves) via the leerie-chain HTTP API.
argument-hint: <submit|status|list|kill|attach> [<args>]
---

# Manage Leerie Chains

The user wants to perform a chain operation:

```
$ARGUMENTS
```

A *chain* is a sequence of leerie runs orchestrated by the `leerie-chain`
Fly app (DESIGN.md §19). Each chain has N sequential waves (wave 0, 1, …).
Runs within a wave execute in parallel; each wave runs against the
accumulated results of all prior waves (a `stage-<chain-id>` branch).

**Runtime prerequisite**: The `leerie-chain` Fly app must be deployed and
reachable. `LEERIE_CHAIN_URL` controls the endpoint (default:
`http://localhost:8080`). Set it once in the user's shell profile:

```
export LEERIE_CHAIN_URL=https://leerie-chain.fly.dev
```

These verbs are **launcher fast-paths** — they do not spawn a container
and do not consult Claude's OAuth token. They are pure HTTP calls.

## Steps

Parse the first word of `$ARGUMENTS` to decide the subcommand:

### `submit` — start a new chain

Required: at least one `--wave` flag. Optional: a target repo (defaults
to the current repo). Each `--wave` defines one sequential wave; the
launcher reads each prompt file and sends its contents as the run prompt.

```
bash "${CLAUDE_PLUGIN_ROOT}/leerie" --chain-submit \
  --wave <path/to/a1.txt,path/to/a2.txt> \
  --wave <path/to/b1.txt> \
  --target <repo-path-or-url>
```

Capture the returned chain id (the `id` field of the JSON response) so
follow-up verbs can reference it.

### `status` — print a chain snapshot

```
bash "${CLAUDE_PLUGIN_ROOT}/leerie" --chain-status <chain-id>
```

Returns the full chain row plus each run's status, wave, and Fly machine
id. Poll this to watch a chain progress from `wave_0` → `wave_1` → … → `done`.

### `list` — list all chains

```
bash "${CLAUDE_PLUGIN_ROOT}/leerie" --list-chains
```

Returns a summary (no run rows). Use `status` for per-chain detail.

### `kill` — cancel a chain

```
bash "${CLAUDE_PLUGIN_ROOT}/leerie" --chain-kill <chain-id>
```

Destroys every still-running per-run Fly machine and marks the chain
`cancelled`. Idempotent on already-terminal chains.

### `attach` — fetch the chain's event log

```
bash "${CLAUDE_PLUGIN_ROOT}/leerie" --chain-attach <chain-id>
```

Returns a JSON event history of every run-status transition for the
chain. Currently polling-only (the first-cut log is a snapshot of the
latest event per run rather than a true stream — see DESIGN.md §19).

## Relaying results

For every verb, surface the launcher's stdout to the user verbatim — it
is the API response JSON, and the user usually wants to copy the chain
id out of `submit` or read the wave/status fields out of `status`. On a
non-zero exit, surface the error body the same way; it will already
identify which verb failed and why.
