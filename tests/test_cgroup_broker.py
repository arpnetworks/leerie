"""Tests for the root cgroup broker (`scripts/cgroup-broker.py`).

The broker is the single root-privileged surface in the worker
containment path (DESIGN §6 *Memory containment*), so its input
validation and protocol dispatch are security-relevant and pinned here.
We import the broker module and point its `V2_ROOT` at a tmp directory
acting as a fake unified cgroupfs — the file writes are ordinary file
writes there, which is enough to test the protocol, sid validation, and
create/enroll/destroy dispatch. Real cgroupfs behavior (v1 vs v2, the
kernel's cgroup.kill / migration semantics) is covered by an
in-container reproduction, not this unit test.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_BROKER_PATH = (Path(__file__).resolve().parent.parent
                / "scripts" / "cgroup-broker.py")


@pytest.fixture
def broker(tmp_path, monkeypatch):
    """Load cgroup-broker.py as a module with V2_ROOT pointed at a tmp
    dir that looks like a unified (v2) cgroupfs, and force v2 hierarchy."""
    spec = importlib.util.spec_from_file_location("cgroup_broker",
                                                  _BROKER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    root = tmp_path / "cgroup"
    slice_dir = root / mod.SLICE
    slice_dir.mkdir(parents=True)
    # Make _detect pick v2: expose the unified marker + controllers.
    (root / "cgroup.controllers").write_text("cpu memory pids")
    (slice_dir / "cgroup.subtree_control").write_text("")
    (slice_dir / "cgroup.controllers").write_text("memory pids")

    monkeypatch.setattr(mod, "V2_ROOT", str(root))
    mod._HIER = mod._detect()
    return mod


# ---- hierarchy detection --------------------------------------------------

def test_detect_v2(broker):
    assert broker._HIER == "v2"


# ---- sid validation (security-critical) -----------------------------------

@pytest.mark.parametrize("sid,ok", [
    ("feat-007-conformer", True),
    ("abc123", True),
    ("a.b_c-d", True),
    ("", False),
    ("../escape", False),
    ("a/b", False),
    ("a b", False),
    ("foo;rm", False),
])
def test_valid_sid(broker, sid, ok):
    assert broker._valid_sid(sid) is ok


def test_create_rejects_bad_sid(broker):
    assert broker._handle("create ../evil 0 64") == "ERR bad sid"


def test_create_rejects_negative_limits(broker):
    assert broker._handle("create good 0 -5") == "ERR bad limit"


def test_enroll_rejects_bad_pid(broker):
    assert broker._handle("enroll good 0").startswith("ERR")
    assert broker._handle("enroll good notanint").startswith("ERR")


# ---- protocol dispatch ----------------------------------------------------

def test_ping(broker):
    assert broker._handle("ping") == "OK"


def test_empty_request(broker):
    assert broker._handle("") == "ERR empty"


def test_unknown_verb(broker):
    assert broker._handle("frobnicate x").startswith("ERR unknown verb")


def test_create_writes_v2_limit_files(broker, tmp_path):
    assert broker._handle("create wsid 268435456 64") == "OK"
    d = Path(broker.V2_ROOT) / broker.SLICE / "leerie-w-wsid"
    assert (d / "pids.max").read_text() == "64"
    assert (d / "memory.max").read_text() == "268435456"


def test_enroll_writes_cgroup_procs(broker):
    broker._handle("create wsid 0 64")
    assert broker._handle("enroll wsid 4321") == "OK"
    d = Path(broker.V2_ROOT) / broker.SLICE / "leerie-w-wsid"
    assert "4321" in (d / "cgroup.procs").read_text()


def test_destroy_removes_dir(broker):
    broker._handle("create wsid 0 64")
    d = Path(broker.V2_ROOT) / broker.SLICE / "leerie-w-wsid"
    assert d.is_dir()
    assert broker._handle("destroy wsid") == "OK"
    # cgroup.kill is a stray file on a regular fs, so rmdir may be blocked;
    # the contract is that destroy returns OK and does not raise.


def test_no_hierarchy_errors(broker, monkeypatch):
    """When no usable hierarchy is detected, ops report ERR rather than
    silently pretending to enforce."""
    monkeypatch.setattr(broker, "_HIER", "none")
    assert broker._handle("create wsid 0 64") == "ERR no usable cgroup hierarchy"


# ---- probe round-trip -----------------------------------------------------

def test_probe_round_trips_ok(broker):
    """`probe` forks a real child, creates+enrolls+destroys a throwaway
    cgroup, and returns OK with the hierarchy. On the fake cgroupfs the
    writes are regular-file writes, so this exercises the full control
    flow (including the fork/kill/reap) without a real kernel cgroup."""
    resp = broker._handle("probe")
    assert resp == "OK v2"


def test_probe_robust_when_child_already_reaped(broker, monkeypatch):
    """The v2 hazard: `destroy` writes cgroup.kill which the kernel uses to
    SIGKILL the enrolled probe child; if the zombie is reaped before the
    broker's own os.kill/waitpid, those raise ProcessLookupError/
    ChildProcessError. The probe must tolerate an already-gone child and
    still return OK, not falsely fail (which would trip the fail-closed
    gate and abort a healthy run).

    Simulate without a real fork: os.fork returns a bogus pid in the
    parent, and os.kill/os.waitpid raise the already-gone errors. The
    suppress() wrappers must swallow both and the probe must return OK."""
    monkeypatch.setattr(broker.os, "fork", lambda: 999999)  # parent branch

    def gone_kill(pid, sig):
        raise ProcessLookupError

    def gone_wait(pid, opts):
        raise ChildProcessError

    monkeypatch.setattr(broker.os, "kill", gone_kill)
    monkeypatch.setattr(broker.os, "waitpid", gone_wait)
    resp = broker._handle("probe")
    assert resp == "OK v2"
