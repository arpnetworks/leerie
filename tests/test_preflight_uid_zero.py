"""Preflight UID-zero detection tests.

Claude Code rejects --dangerously-skip-permissions from UID 0.  Acting
workers (autonomous=True in claude_p) unconditionally pass the flag, so
no acting worker can run as root.  preflight() must detect UID 0 and
die() before any workers spawn.

Source-text pins (same mockless style as test_preflight_cli_version.py).
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEERIE_PY = REPO_ROOT / "orchestrator" / "leerie.py"


def _preflight_body() -> str:
    src = LEERIE_PY.read_text()
    start = src.index("async def preflight(")
    next_async = src.index("\nasync def ", start + 1)
    next_sync = src.index("\ndef ", start + 1)
    end = min(next_async, next_sync)
    return src[start:end]


def test_preflight_checks_uid_zero():
    """preflight() must call os.getuid() and gate on UID 0."""
    body = _preflight_body()
    assert "os.getuid()" in body, (
        "preflight must check os.getuid() — without it, rootless "
        "containerd workers crash with a cryptic Claude Code error."
    )


def test_uid_zero_check_runs_before_smoke_test():
    """The UID 0 check must precede the skip_smoke gate so it fires
    regardless of --skip-smoke."""
    body = _preflight_body()
    uid_pos = body.index("os.getuid()")
    skip_pos = body.index("if not skip_smoke")
    assert uid_pos < skip_pos, (
        "os.getuid() check must run before the skip_smoke gate"
    )


def test_uid_zero_check_dies_with_actionable_message():
    """The die() call must mention the root cause and alternatives."""
    body = _preflight_body()
    assert "--dangerously-skip-permissions" in body, (
        "UID 0 die() must name the rejected flag"
    )
    assert "rootless" in body.lower(), (
        "UID 0 die() must mention rootless containerd"
    )
