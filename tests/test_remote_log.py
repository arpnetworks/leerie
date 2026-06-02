"""Tests for scripts/remote/_log.sh and lib.sh's remote_log helper.

Asserts the HH:MM:SS [leerie] [<repo>] <msg> prefix shape — the user-
visible contract for telling parallel runs apart in interleaved stderr.
Time first so a glance at the leftmost column gives a chronological scan.
The helper lives in _log.sh; lib.sh sources it. Tests exercise both
sourcing routes so the two can't drift silently.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_SH = REPO_ROOT / "scripts" / "remote" / "_log.sh"
LIB_SH = REPO_ROOT / "scripts" / "remote" / "lib.sh"

PREFIX_RE = re.compile(
    r"^\d{2}:\d{2}:\d{2} \[leerie\] \[(?P<repo>[^\]]+)\] (?P<body>.*)$"
)


def _run(source_path: Path, msg: str, user_repo: str | None = None) -> str:
    env = {"PATH": "/usr/bin:/bin"}
    if user_repo is not None:
        env["USER_REPO"] = user_repo
    r = subprocess.run(
        ["bash", "-c", f"source {source_path}; remote_log {msg!r}"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return r.stderr.rstrip("\n")


def test_log_sh_exists():
    assert LOG_SH.exists(), "scripts/remote/_log.sh is missing"


def test_log_sh_is_executable():
    assert os.access(LOG_SH, os.X_OK), (
        "scripts/remote/_log.sh is not executable"
    )


def test_remote_log_format_via_log_sh():
    line = _run(LOG_SH, "hello world", user_repo="/tmp/myapp")
    m = PREFIX_RE.match(line)
    assert m, f"no prefix match: {line!r}"
    assert m.group("repo") == "myapp"
    assert m.group("body") == "hello world"


def test_remote_log_format_via_lib_sh():
    # Same shape must come out of lib.sh, which sources _log.sh.
    line = _run(LIB_SH, "hello world", user_repo="/tmp/myapp")
    m = PREFIX_RE.match(line)
    assert m, f"no prefix match: {line!r}"
    assert m.group("repo") == "myapp"
    assert m.group("body") == "hello world"


def test_remote_log_falls_back_when_user_repo_unset():
    # No USER_REPO in env → "?" placeholder. Bootstrap-path defense.
    line = _run(LOG_SH, "hi")
    m = PREFIX_RE.match(line)
    assert m and m.group("repo") == "?"


def test_remote_log_passes_percent_through_unchanged():
    # Literal % in body must not be interpreted as printf format spec.
    line = _run(LOG_SH, "machine at 95% CPU", user_repo="/tmp/myapp")
    m = PREFIX_RE.match(line)
    assert m and m.group("body") == "machine at 95% CPU"
