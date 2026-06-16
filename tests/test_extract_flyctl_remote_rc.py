"""Tests for _extract_flyctl_remote_rc (scripts/remote/lib.sh).

flyctl ssh console does not forward the remote process's exit code — it
returns 1 for any non-zero remote exit. The actual code appears only in
stderr: ``Error: ssh shell: Process exited with status <N>``. The helper
parses it from a captured stderr file.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LIB_SH = REPO_ROOT / "scripts" / "remote" / "lib.sh"
LEERIE = REPO_ROOT / "leerie"

_HARNESS = f"""
set -uo pipefail
remote_log() {{ echo "[leerie] $*" >&2; }}
. {LIB_SH}
echo "$(_extract_flyctl_remote_rc "$1" "$2")"
"""


def _run(tmp_path: Path, stderr_content: str, flyctl_rc: str) -> str:
    stderr_file = tmp_path / "stderr.log"
    stderr_file.write_text(stderr_content)
    r = subprocess.run(
        ["bash", "-c", _HARNESS, "_", str(stderr_file), flyctl_rc],
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_extracts_remote_rc_from_stderr(tmp_path: Path):
    result = _run(tmp_path,
                  "Error: ssh shell: Process exited with status 75\n",
                  "1")
    assert result == "75"


def test_returns_original_rc_when_pattern_absent(tmp_path: Path):
    result = _run(tmp_path,
                  "Error: some other flyctl error\n",
                  "1")
    assert result == "1"


def test_returns_zero_on_success(tmp_path: Path):
    result = _run(tmp_path,
                  "Error: ssh shell: Process exited with status 75\n",
                  "0")
    assert result == "0"


def test_returns_original_rc_for_empty_stderr(tmp_path: Path):
    result = _run(tmp_path, "", "1")
    assert result == "1"


def test_returns_last_match_on_multiple_lines(tmp_path: Path):
    result = _run(tmp_path,
                  "Error: ssh shell: Process exited with status 42\n"
                  "Error: ssh shell: Process exited with status 75\n",
                  "1")
    assert result == "75"


def test_extracts_arbitrary_exit_codes(tmp_path: Path):
    for code in ("10", "11", "130", "143", "255"):
        result = _run(tmp_path,
                      f"Error: ssh shell: Process exited with status {code}\n",
                      "1")
        assert result == code, f"Expected {code}, got {result}"


# =========================================================================
# Coupling: launcher uses _extract_flyctl_remote_rc at the launch site
# =========================================================================

def test_launcher_uses_extract_helper_for_launch_rc():
    """The launcher must capture flyctl stderr and parse the real remote
    exit code via _extract_flyctl_remote_rc before the rc=75 pivot.
    Without this, flyctl's rc=1 falls through to the pause-on-failure
    branch and kills the live orchestrator."""
    launcher = LEERIE.read_text()
    assert "_extract_flyctl_remote_rc" in launcher, (
        "Launcher must call _extract_flyctl_remote_rc to recover the "
        "real remote exit code from flyctl ssh console's stderr."
    )
    assert "_launch_stderr" in launcher, (
        "Launcher must capture flyctl stderr to a tempfile for parsing."
    )


def test_lib_sh_defines_extract_helper():
    libsh = LIB_SH.read_text()
    assert "_extract_flyctl_remote_rc()" in libsh, (
        "_extract_flyctl_remote_rc() not defined in lib.sh"
    )
