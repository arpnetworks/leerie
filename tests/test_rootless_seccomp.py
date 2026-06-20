"""Source-text pin: launcher lifts seccomp for rootless containerd.

The OCI default seccomp profile blocks unshare(CLONE_NEWUSER) inside
containers. The launcher must pass --security-opt seccomp=unconfined to
nerdctl run for rootless runs so container-entry.sh's unshare succeeds.
The check is gated on the containerd-rootless/child_pid sentinel (not
id -u) so macOS/Colima runs are unaffected.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LAUNCHER = REPO_ROOT / "leerie"


def _nerdctl_run_block() -> str:
    """Return the launcher source from ROOTLESS_SECOPT through the
    nerdctl run invocation that uses it."""
    src = LAUNCHER.read_text()
    start = src.index("ROOTLESS_SECOPT=()")
    end = src.index("nerdctl run", start)
    end = src.index("\n", src.index("ROOTLESS_SECOPT[@]", end))
    return src[start:end]


def test_seccomp_unconfined_present():
    """The launcher must pass seccomp=unconfined for rootless runs."""
    block = _nerdctl_run_block()
    assert "seccomp=unconfined" in block, (
        "launcher must pass --security-opt seccomp=unconfined — without it, "
        "unshare(CLONE_NEWUSER) fails inside the container"
    )


def test_seccomp_gated_on_rootless_sentinel():
    """The seccomp lift must be gated on the containerd-rootless sentinel,
    not on id -u (which over-fires on macOS/Colima)."""
    block = _nerdctl_run_block()
    assert "containerd-rootless/child_pid" in block, (
        "seccomp lift must be gated on containerd-rootless/child_pid — "
        "id -u fires on macOS where containerd is rootful"
    )


def test_seccomp_expansion_in_nerdctl_run():
    """ROOTLESS_SECOPT must be expanded in the nerdctl run argv."""
    block = _nerdctl_run_block()
    assert "ROOTLESS_SECOPT[@]" in block, (
        "ROOTLESS_SECOPT must be expanded in the nerdctl run invocation"
    )
