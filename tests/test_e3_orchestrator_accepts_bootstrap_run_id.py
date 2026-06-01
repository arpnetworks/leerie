"""E3: the orchestrator's `main()` accepts a launcher-supplied
`_bootstrap-<hex>` run-id verbatim instead of generating its own.

This is the receiving end of the contract DESIGN §6 documents: the
remote-mode launcher generates the bootstrap id host-side (so it has a
stable orchestrator.log path to tail), passes it via `--run-id <id>`,
and the orchestrator honors that id until phase_classify completes and
`State.rename_to` promotes it to the final id.

Without this branch, the orchestrator would silently generate its own
`_bootstrap-<hex>` (line ~11608) and the launcher's tail would attach
to a different (orphaned) log path.

This test pins the branch by source-text coupling — the same pattern as
`test_launcher_no_push_skips.py` — because the surrounding `main()`
function is too large for clean monkeypatching.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PILA_PY = REPO_ROOT / "orchestrator" / "pila.py"


def test_main_honors_launcher_supplied_bootstrap_run_id():
    """The elif branch must accept `args.run_id` verbatim when it starts
    with `_bootstrap-` AND `args.resume` is False. This preserves the
    launcher's chosen id through to State construction so the launcher
    and orchestrator agree on the log/state path."""
    src = PILA_PY.read_text()
    # The elif guard. Order matters — must be checked AFTER args.resume
    # (which has its own resolve_run_id path) and BEFORE the unconditional
    # bootstrap-id generator.
    assert (
        'elif args.run_id and args.run_id.startswith("_bootstrap-"):'
        in src
    ), "main() must accept a launcher-supplied _bootstrap-* run-id"
    # The branch body assigns args.run_id verbatim — no transformation.
    # Find the elif and assert the next non-comment statement is the
    # assignment.
    lines = src.splitlines()
    elif_idx = next(
        i for i, ln in enumerate(lines)
        if 'elif args.run_id and args.run_id.startswith("_bootstrap-"):' in ln
    )
    # Walk forward until we hit the first non-comment, non-blank line.
    body_idx = elif_idx + 1
    while body_idx < len(lines):
        s = lines[body_idx].strip()
        if s and not s.startswith("#"):
            break
        body_idx += 1
    # The first executable statement must be `run_id = args.run_id`.
    assert lines[body_idx].strip() == "run_id = args.run_id", (
        f"expected `run_id = args.run_id` after elif; got: "
        f"{lines[body_idx].strip()!r}"
    )


def test_main_bootstrap_branch_ordered_correctly():
    """The branch ordering must be: args.resume → bootstrap-* → fallback.
    A reversed order would either ignore the bootstrap path on resume
    (correct: resume has its own resolver) or skip the launcher id
    silently (wrong: orchestrator would self-generate)."""
    src = PILA_PY.read_text()
    # Find the three lines in order.
    resume_idx = src.find("if args.resume:")
    elif_idx = src.find('elif args.run_id and args.run_id.startswith("_bootstrap-"):')
    else_idx = src.find('run_id = "_bootstrap-" + hashlib.sha1')
    assert resume_idx != -1
    assert elif_idx != -1
    assert else_idx != -1
    assert resume_idx < elif_idx < else_idx, (
        "ordering broken: expected `if args.resume` < `elif bootstrap` "
        "< fallback `_bootstrap-` generation"
    )
