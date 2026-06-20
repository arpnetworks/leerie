"""Source-text pin: rootless entrypoint sets IS_SANDBOX=1.

Claude Code rejects --dangerously-skip-permissions from UID 0 unless
IS_SANDBOX=1 is set. The rootless path in container-entry.sh must set
this variable so acting workers run identically to non-rootless mode.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENTRY_SH = REPO_ROOT / "scripts" / "container-entry.sh"


def _orchestrator_rootless_block() -> str:
    """Return the rootless if-block that launches the orchestrator
    (the one referencing leerie.py, not the Fly idle sleep block)."""
    src = ENTRY_SH.read_text()
    marker = "python3 /opt/leerie-image/orchestrator/leerie.py"
    py_pos = src.index(marker)
    # Walk backward to the enclosing ROOTLESS if-block.
    block_start_marker = 'if [ "$ROOTLESS" = "true" ]; then'
    start = src.rindex(block_start_marker, 0, py_pos)
    end = src.index("\nfi", start) + len("\nfi")
    return src[start:end]


def test_rootless_sets_is_sandbox():
    """The rootless exec must export IS_SANDBOX=1 so Claude Code accepts
    --dangerously-skip-permissions from mapped root."""
    block = _orchestrator_rootless_block()
    assert "IS_SANDBOX=1" in block, (
        "rootless entrypoint must set IS_SANDBOX=1 — without it, "
        "Claude Code rejects --dangerously-skip-permissions from UID 0"
    )


def test_is_sandbox_precedes_exec():
    """IS_SANDBOX=1 must appear in the env block before python3, not
    after exec (where it would be a no-op)."""
    block = _orchestrator_rootless_block()
    sandbox_pos = block.index("IS_SANDBOX=1")
    exec_pos = block.index("python3")
    assert sandbox_pos < exec_pos, (
        "IS_SANDBOX=1 must precede the python3 invocation"
    )
