"""Tests for the launcher's shallow-seed knob resolution.

The launcher resolves two bash-only knobs consumed by
`scripts/remote/seed-repo.sh` on fresh remote provisions
(DESIGN §6 *Shallow seeding for heavy repos*):

  - LEERIE_SEED_DEPTH (default 50; 0 = full history / disable shallow)
  - LEERIE_SEED_SHALLOW_THRESHOLD_MB (default 200)

Resolution precedence mirrors FLY_VM_DISK_GB: CLI flag > env var >
`leerie.toml` flat key > default. Unlike `confidence_rounds`, these are
NOT read by the Python orchestrator — they live entirely in bash — so
the resolution is tested at the launcher layer.

These tests reproduce the launcher's `_resolve_seed_knob` helper +
validation byte-for-byte (see `test_block_present_in_launcher`), so a
refactor that changes parsing surfaces a coupling failure.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
LAUNCHER = REPO_ROOT / "leerie"


# The launcher's seed-knob resolution helper + CLI-scan + validation,
# reproduced so the tests exercise the launcher's logic and a refactor
# that changes parsing makes the coupling test fail.
_LAUNCHER_SEED_BLOCK = r"""
_resolve_seed_knob() {
  local _cli="$1" _envname="$2" _tomlkey="$3" _default="$4" _envval _tomlval
  if [ -n "$_cli" ]; then printf '%s' "$_cli"; return; fi
  eval "_envval=\"\${$_envname:-}\""
  if [ -n "$_envval" ]; then printf '%s' "$_envval"; return; fi
  if [ -f "$USER_REPO/leerie.toml" ]; then
    _tomlval="$( { grep -E "^[[:space:]]*${_tomlkey}[[:space:]]*=" \
                        "$USER_REPO/leerie.toml" 2>/dev/null \
                      | head -1 \
                      | sed -E "s/^[[:space:]]*${_tomlkey}[[:space:]]*=[[:space:]]*//; s/[[:space:]]*\$//; s/^\"//; s/\"\$//" ; } || true)"
    if [ -n "$_tomlval" ]; then printf '%s' "$_tomlval"; return; fi
  fi
  printf '%s' "$_default"
}
_cli_seed_depth=""
_cli_seed_threshold=""
_prev_seed_arg=""
for arg in "$@"; do
  if [ -n "$_prev_seed_arg" ]; then
    case "$_prev_seed_arg" in
      depth)     _cli_seed_depth="$arg" ;;
      threshold) _cli_seed_threshold="$arg" ;;
    esac
    _prev_seed_arg=""
    continue
  fi
  case "$arg" in
    --seed-depth=*)                  _cli_seed_depth="${arg#--seed-depth=}" ;;
    --seed-depth)                    _prev_seed_arg="depth" ;;
    --seed-shallow-threshold-mb=*)   _cli_seed_threshold="${arg#--seed-shallow-threshold-mb=}" ;;
    --seed-shallow-threshold-mb)     _prev_seed_arg="threshold" ;;
  esac
done
LEERIE_SEED_DEPTH="$(_resolve_seed_knob "$_cli_seed_depth" LEERIE_SEED_DEPTH seed_depth 50)"
LEERIE_SEED_SHALLOW_THRESHOLD_MB="$(_resolve_seed_knob "$_cli_seed_threshold" LEERIE_SEED_SHALLOW_THRESHOLD_MB seed_shallow_threshold_mb 200)"
case "$LEERIE_SEED_DEPTH" in
  ''|*[!0-9]*)
    echo "LEERIE_SEED_DEPTH='$LEERIE_SEED_DEPTH' is not a non-negative integer (0 = full history)" >&2
    exit 1
    ;;
esac
case "$LEERIE_SEED_SHALLOW_THRESHOLD_MB" in
  ''|*[!0-9]*|0)
    echo "LEERIE_SEED_SHALLOW_THRESHOLD_MB='$LEERIE_SEED_SHALLOW_THRESHOLD_MB' is not a positive integer (MB)" >&2
    exit 1
    ;;
esac
"""


def _run(user_repo: Path, *args: str, env_extra: dict | None = None,
         ) -> subprocess.CompletedProcess:
    """Source the launcher's seed-knob block in a subshell with the given
    CLI args and USER_REPO. Prints the two resolved values on success."""
    script = (
        "set -euo pipefail\n"
        f"USER_REPO={user_repo!s}\n"
        f"{_LAUNCHER_SEED_BLOCK}\n"
        'printf "%s %s\\n" "$LEERIE_SEED_DEPTH" "$LEERIE_SEED_SHALLOW_THRESHOLD_MB"\n'
    )
    env = {**os.environ}
    env.pop("LEERIE_SEED_DEPTH", None)
    env.pop("LEERIE_SEED_SHALLOW_THRESHOLD_MB", None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["bash", "-c", script, "bash", *args],
        capture_output=True, text=True, env=env,
    )


def _resolve(user_repo: Path, *args: str, env_extra: dict | None = None,
             ) -> tuple[str, str]:
    result = _run(user_repo, *args, env_extra=env_extra)
    assert result.returncode == 0, f"unexpected failure: {result.stderr}"
    depth, thresh = result.stdout.strip().split()
    return depth, thresh


def test_defaults(tmp_path):
    """No CLI, no env, no toml → depth=50, threshold=200."""
    assert _resolve(tmp_path) == ("50", "200")


def test_cli_wins(tmp_path):
    """--seed-depth / --seed-shallow-threshold-mb on the CLI win."""
    assert _resolve(tmp_path, "--seed-depth", "10",
                    "--seed-shallow-threshold-mb", "500") == ("10", "500")


def test_cli_equals_form(tmp_path):
    """The =form is accepted too."""
    assert _resolve(tmp_path, "--seed-depth=25") == ("25", "200")


def test_env_wins_over_toml(tmp_path):
    """Env beats leerie.toml."""
    (tmp_path / "leerie.toml").write_text(
        "seed_depth = 33\nseed_shallow_threshold_mb = 300\n")
    assert _resolve(tmp_path, env_extra={"LEERIE_SEED_DEPTH": "77"}) == ("77", "300")


def test_cli_wins_over_env_and_toml(tmp_path):
    """CLI beats both env and toml."""
    (tmp_path / "leerie.toml").write_text("seed_depth = 33\n")
    assert _resolve(tmp_path, "--seed-depth", "5",
                    env_extra={"LEERIE_SEED_DEPTH": "77"}) == ("5", "200")


def test_toml_resolution(tmp_path):
    """leerie.toml flat keys are read when no CLI/env."""
    (tmp_path / "leerie.toml").write_text(
        "seed_depth = 12\nseed_shallow_threshold_mb = 150\n")
    assert _resolve(tmp_path) == ("12", "150")


def test_depth_zero_accepted(tmp_path):
    """depth=0 (full history / disable shallow) is a valid value."""
    assert _resolve(tmp_path, "--seed-depth", "0") == ("0", "200")


@pytest.mark.parametrize("bad", ["abc", "-1", "5.5", "1e3"])
def test_garbage_depth_rejected(tmp_path, bad):
    """A non-integer depth is rejected at startup, not silently ignored."""
    result = _run(tmp_path, "--seed-depth", bad)
    assert result.returncode != 0, f"garbage depth {bad!r} should be rejected"
    assert "LEERIE_SEED_DEPTH" in result.stderr


def test_threshold_zero_rejected(tmp_path):
    """threshold=0 is invalid (a 0 MB threshold would make every repo
    shallow, defeating the small-repo carve-out; use depth=0 to disable)."""
    result = _run(tmp_path, "--seed-shallow-threshold-mb", "0")
    assert result.returncode != 0
    assert "LEERIE_SEED_SHALLOW_THRESHOLD_MB" in result.stderr


@pytest.mark.parametrize("bad", ["abc", "-5", "2.0"])
def test_garbage_threshold_rejected(tmp_path, bad):
    result = _run(tmp_path, "--seed-shallow-threshold-mb", bad)
    assert result.returncode != 0
    assert "LEERIE_SEED_SHALLOW_THRESHOLD_MB" in result.stderr


def test_block_present_in_launcher():
    """Coupling test: the reproduced block must stay in lockstep with the
    launcher. Pin the key helper name, flag names, defaults, and the two
    validation vocabularies so a drift surfaces here."""
    src = LAUNCHER.read_text()
    assert "_resolve_seed_knob()" in src, (
        "Launcher's _resolve_seed_knob helper is missing or renamed — "
        "update this test in lockstep."
    )
    assert 'LEERIE_SEED_DEPTH seed_depth 50' in src, (
        "Launcher's LEERIE_SEED_DEPTH resolution (env var, toml key "
        "'seed_depth', default 50) has drifted."
    )
    assert 'LEERIE_SEED_SHALLOW_THRESHOLD_MB seed_shallow_threshold_mb 200' in src, (
        "Launcher's threshold resolution (toml key "
        "'seed_shallow_threshold_mb', default 200) has drifted."
    )
    assert "--seed-depth" in src and "--seed-shallow-threshold-mb" in src, (
        "Launcher must scan the --seed-depth / --seed-shallow-threshold-mb "
        "CLI flags."
    )
    # The two flags must be stripped from REWRITTEN_ARGS (launcher-only),
    # so they never reach the orchestrator's strict parse_args().
    assert "--seed-depth|--seed-shallow-threshold-mb)" in src, (
        "Launcher must strip --seed-depth / --seed-shallow-threshold-mb "
        "from REWRITTEN_ARGS (they are host-only; the orchestrator uses "
        "strict parse_args and would error 'unrecognized arguments')."
    )
