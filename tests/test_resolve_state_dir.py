"""Tests for the LEERIE_STATE_HOST_DIR resolution block in the launcher.

The resolution logic lives in the bash launcher (`leerie`); these tests use
a minimal bash harness that mirrors the exact block and echoes the resolved
LEERIE_STATE_HOST_DIR value.

Precedence (lowest → highest):
  default ($HOME/.leerie/<basename>)
  → leerie.toml `state_dir = ...`
  → LEERIE_STATE_DIR env var
  → --state-dir CLI flag

A second harness (`_OWNERSHIP_HARNESS`) covers the `_validate_state_ownership`
sidecar check, which gates cross-repo basename collisions and refuses to
write into the leerie install directory.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Bash harness that mirrors the LEERIE_STATE_HOST_DIR resolution block from
# `leerie`. Takes USER_REPO as $1 and HOME as $2; remaining args are CLI.
_HARNESS = r"""
#!/usr/bin/env bash
set -euo pipefail
USER_REPO="$1"
HOME="$2"
export HOME
shift 2   # remaining args are simulated CLI

_state_dir_default() {
  local basename
  basename="$(python3 -c "import os,sys; print(os.path.basename(sys.argv[1].rstrip('/')))" "$USER_REPO")"
  echo "$HOME/.leerie/$basename"
}

LEERIE_STATE_HOST_DIR="$(_state_dir_default)"

if [ -f "$USER_REPO/leerie.toml" ]; then
  _toml_state_dir="$( { grep -E '^[[:space:]]*state_dir[[:space:]]*=' \
                            "$USER_REPO/leerie.toml" 2>/dev/null \
                        || true; } \
                      | head -1 \
                      | sed -E 's/^[[:space:]]*state_dir[[:space:]]*=[[:space:]]*//;
                                s/[[:space:]]*$//;
                                s/^"(.*)"$/\1/;
                                s/^'"'"'(.*)'"'"'$/\1/')"
  if [ -n "$_toml_state_dir" ]; then
    case "$_toml_state_dir" in
      "~")   _toml_state_dir="$HOME" ;;
      "~/"*) _toml_state_dir="$HOME/${_toml_state_dir#"~/"}" ;;
    esac
    LEERIE_STATE_HOST_DIR="$_toml_state_dir"
  fi
  unset _toml_state_dir
fi

if [ -n "${LEERIE_STATE_DIR:-}" ]; then
  LEERIE_STATE_HOST_DIR="$LEERIE_STATE_DIR"
fi

_cli_state_dir=""
_prev_was_state_dir=false
for arg in "$@"; do
  if $_prev_was_state_dir; then
    _cli_state_dir="$arg"
    _prev_was_state_dir=false
    continue
  fi
  case "$arg" in
    --state-dir=*) _cli_state_dir="${arg#--state-dir=}" ;;
    --state-dir)   _prev_was_state_dir=true ;;
  esac
done
if [ -n "$_cli_state_dir" ]; then
  LEERIE_STATE_HOST_DIR="$_cli_state_dir"
fi
unset _cli_state_dir _prev_was_state_dir

case "$LEERIE_STATE_HOST_DIR" in
  "~")   LEERIE_STATE_HOST_DIR="$HOME" ;;
  "~/"*) LEERIE_STATE_HOST_DIR="$HOME/${LEERIE_STATE_HOST_DIR#"~/"}" ;;
esac

echo "$LEERIE_STATE_HOST_DIR"
"""

# Bash harness covering the _validate_state_ownership sidecar check.
# Takes USER_REPO=$1, LEERIE_STATE_HOST_DIR=$2; exits 0 on accept, 1 on reject.
_OWNERSHIP_HARNESS = r"""
#!/usr/bin/env bash
set -euo pipefail
USER_REPO="$1"
LEERIE_STATE_HOST_DIR="$2"

_validate_state_ownership() {
  local dir="$LEERIE_STATE_HOST_DIR"
  if [ ! -e "$dir" ]; then
    if ! mkdir -p "$dir"; then
      echo "leerie: could not create state dir $dir" >&2
      exit 1
    fi
    printf '%s\n' "$USER_REPO" > "$dir/.owner"
    return 0
  fi
  if [ -f "$dir/.owner" ]; then
    local recorded
    recorded="$(head -1 "$dir/.owner" 2>/dev/null || true)"
    if [ "$recorded" = "$USER_REPO" ]; then
      return 0
    fi
    echo "leerie: state-dir collision at $dir" >&2
    echo "  owner on file: $recorded" >&2
    echo "  current repo:  $USER_REPO" >&2
    exit 1
  fi
  if [ -d "$dir/runs" ] || [ -d "$dir/worktrees" ]; then
    printf '%s\n' "$USER_REPO" > "$dir/.owner"
    return 0
  fi
  if [ -d "$dir/.git" ] || [ -x "$dir/leerie" ]; then
    echo "leerie: state-dir target $dir looks like the leerie install directory" >&2
    exit 1
  fi
  printf '%s\n' "$USER_REPO" > "$dir/.owner"
}

_validate_state_ownership
"""


def _run(
    user_repo: Path,
    fake_home: Path,
    env: dict,
    cli_args: list[str],
    *,
    expect_fail: bool = False,
) -> tuple[str, str]:
    """Run the harness; return (stdout, stderr). Raises on non-zero exit
    unless expect_fail=True."""
    result = subprocess.run(
        ["bash", "-c", _HARNESS, "--", str(user_repo), str(fake_home)]
        + cli_args,
        env={**{"PATH": "/usr/bin:/bin"}, **env},
        capture_output=True,
        text=True,
    )
    if not expect_fail:
        assert result.returncode == 0, result.stderr
    return result.stdout.strip(), result.stderr.strip()


def _run_ownership(
    user_repo: str,
    state_dir: Path,
    *,
    expect_fail: bool = False,
) -> tuple[int, str, str]:
    """Run the ownership harness; return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["bash", "-c", _OWNERSHIP_HARNESS, "--", user_repo, str(state_dir)],
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    if not expect_fail:
        assert result.returncode == 0, result.stderr
    return result.returncode, result.stdout.strip(), result.stderr.strip()


# ── default resolution ────────────────────────────────────────────────────────


def test_default_is_under_home(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    out, _ = _run(user_repo, fake_home, {}, [])
    assert out.startswith(str(fake_home))


def test_default_is_not_inside_user_repo(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    out, _ = _run(user_repo, fake_home, {}, [])
    assert not out.startswith(str(user_repo))


def test_default_is_direct_basename_under_leerie(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    out, _ = _run(user_repo, fake_home, {}, [])
    assert out == str(fake_home) + "/.leerie/myproject"


def test_default_no_state_subdirectory(tmp_path):
    """The legacy `state/` subdirectory is gone — paths sit directly under
    $HOME/.leerie/<basename>."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    out, _ = _run(user_repo, fake_home, {}, [])
    assert "/.leerie/state/" not in out


def test_default_key_is_stable(tmp_path):
    """Same inputs → same output (deterministic)."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    out1, _ = _run(user_repo, fake_home, {}, [])
    out2, _ = _run(user_repo, fake_home, {}, [])
    assert out1 == out2


def test_two_repos_sharing_basename_resolve_to_same_default(tmp_path):
    """A consequence of the basename-only key: two different repo paths
    that share a basename map to the same default. The .owner sidecar
    check (separate harness) is what catches the collision at use time."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    repo_a = tmp_path / "src" / "myproject"
    repo_a.mkdir(parents=True)
    repo_b = tmp_path / "work" / "myproject"
    repo_b.mkdir(parents=True)
    out_a, _ = _run(repo_a, fake_home, {}, [])
    out_b, _ = _run(repo_b, fake_home, {}, [])
    assert out_a == out_b
    assert out_a == str(fake_home) + "/.leerie/myproject"


def test_default_path_format(tmp_path):
    """Exact path format: $HOME/.leerie/<basename>, no slashes inside the
    basename segment."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "nested" / "myproject"
    user_repo.mkdir(parents=True)
    out, _ = _run(user_repo, fake_home, {}, [])
    assert out == str(fake_home) + "/.leerie/myproject"


# ── leerie.toml `state_dir` override ─────────────────────────────────────────


def test_toml_state_dir_overrides_default(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    toml_dir = tmp_path / "custom-state"
    (user_repo / "leerie.toml").write_text(f"state_dir = {toml_dir}\n")
    out, _ = _run(user_repo, fake_home, {}, [])
    assert out == str(toml_dir)


def test_toml_state_dir_quoted_value(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    toml_dir = str(tmp_path / "quoted-state")
    (user_repo / "leerie.toml").write_text(f'state_dir = "{toml_dir}"\n')
    out, _ = _run(user_repo, fake_home, {}, [])
    assert out == toml_dir


def test_toml_state_dir_tilde_expansion(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    (user_repo / "leerie.toml").write_text("state_dir = ~/mystate\n")
    out, _ = _run(user_repo, fake_home, {}, [])
    assert out == str(fake_home) + "/mystate"


def test_toml_unrelated_key_leaves_default(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    (user_repo / "leerie.toml").write_text("runtime = local\n")
    out, _ = _run(user_repo, fake_home, {}, [])
    assert out == str(fake_home) + "/.leerie/myproject"


# ── LEERIE_STATE_DIR env override ─────────────────────────────────────────────


def test_env_overrides_default(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    env_dir = str(tmp_path / "env-state")
    out, _ = _run(user_repo, fake_home, {"LEERIE_STATE_DIR": env_dir}, [])
    assert out == env_dir


def test_env_overrides_toml(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    toml_dir = str(tmp_path / "toml-state")
    env_dir = str(tmp_path / "env-state")
    (user_repo / "leerie.toml").write_text(f"state_dir = {toml_dir}\n")
    out, _ = _run(user_repo, fake_home, {"LEERIE_STATE_DIR": env_dir}, [])
    assert out == env_dir


def test_env_empty_leaves_default(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    out, _ = _run(user_repo, fake_home, {"LEERIE_STATE_DIR": ""}, [])
    assert out == str(fake_home) + "/.leerie/myproject"


# ── CLI --state-dir override ──────────────────────────────────────────────────


def test_cli_equals_form_overrides_default(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    cli_dir = str(tmp_path / "cli-state")
    out, _ = _run(user_repo, fake_home, {}, [f"--state-dir={cli_dir}"])
    assert out == cli_dir


def test_cli_space_form_overrides_default(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    cli_dir = str(tmp_path / "cli-state")
    out, _ = _run(user_repo, fake_home, {}, ["--state-dir", cli_dir])
    assert out == cli_dir


def test_cli_overrides_env(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    env_dir = str(tmp_path / "env-state")
    cli_dir = str(tmp_path / "cli-state")
    out, _ = _run(
        user_repo, fake_home, {"LEERIE_STATE_DIR": env_dir}, [f"--state-dir={cli_dir}"]
    )
    assert out == cli_dir


def test_cli_overrides_toml(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    toml_dir = str(tmp_path / "toml-state")
    cli_dir = str(tmp_path / "cli-state")
    (user_repo / "leerie.toml").write_text(f"state_dir = {toml_dir}\n")
    out, _ = _run(user_repo, fake_home, {}, [f"--state-dir={cli_dir}"])
    assert out == cli_dir


# ── precedence summary ────────────────────────────────────────────────────────


def test_precedence_cli_beats_env_beats_toml_beats_default(tmp_path):
    """Full precedence ladder: CLI wins over env wins over toml wins over default."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    user_repo = tmp_path / "myproject"
    user_repo.mkdir()
    toml_dir = str(tmp_path / "toml-state")
    env_dir = str(tmp_path / "env-state")
    cli_dir = str(tmp_path / "cli-state")
    (user_repo / "leerie.toml").write_text(f"state_dir = {toml_dir}\n")

    # All three set; CLI should win.
    out, _ = _run(
        user_repo,
        fake_home,
        {"LEERIE_STATE_DIR": env_dir},
        [f"--state-dir={cli_dir}"],
    )
    assert out == cli_dir

    # Remove CLI; env should win over toml.
    out, _ = _run(
        user_repo, fake_home, {"LEERIE_STATE_DIR": env_dir}, []
    )
    assert out == env_dir

    # Remove env; toml should win over default.
    out, _ = _run(user_repo, fake_home, {}, [])
    assert out == toml_dir


# ── ownership sidecar (.owner) ───────────────────────────────────────────────


def test_ownership_writes_owner_on_fresh_dir(tmp_path):
    state_dir = tmp_path / "state"
    repo = "/tmp/test/myproject"
    rc, _, _ = _run_ownership(repo, state_dir)
    assert rc == 0
    assert (state_dir / ".owner").read_text().strip() == repo


def test_ownership_passes_when_owner_matches(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    repo = "/tmp/test/myproject"
    (state_dir / ".owner").write_text(repo + "\n")
    rc, _, _ = _run_ownership(repo, state_dir)
    assert rc == 0


def test_ownership_fails_on_basename_collision(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    (state_dir / ".owner").write_text("/path/A/myproject\n")
    rc, _, stderr = _run_ownership(
        "/path/B/myproject", state_dir, expect_fail=True
    )
    assert rc != 0
    assert "state-dir collision" in stderr
    assert "/path/A/myproject" in stderr
    assert "/path/B/myproject" in stderr


def test_ownership_backfills_owner_when_runs_subdir_present(tmp_path):
    """A pre-existing state dir from before this commit (has runs/ but no
    .owner) gets the sidecar backfilled rather than rejected."""
    state_dir = tmp_path / "state"
    (state_dir / "runs").mkdir(parents=True)
    repo = "/tmp/test/myproject"
    rc, _, _ = _run_ownership(repo, state_dir)
    assert rc == 0
    assert (state_dir / ".owner").read_text().strip() == repo


def test_ownership_backfills_owner_when_worktrees_subdir_present(tmp_path):
    state_dir = tmp_path / "state"
    (state_dir / "worktrees").mkdir(parents=True)
    repo = "/tmp/test/myproject"
    rc, _, _ = _run_ownership(repo, state_dir)
    assert rc == 0
    assert (state_dir / ".owner").read_text().strip() == repo


def test_ownership_rejects_install_dir_via_git(tmp_path):
    """A dir with .git/ at top level and no runs/ looks like the installer's
    leerie clone, not a state dir — refuse to write."""
    state_dir = tmp_path / "fake-install"
    (state_dir / ".git").mkdir(parents=True)
    rc, _, stderr = _run_ownership(
        "/tmp/something/leerie", state_dir, expect_fail=True
    )
    assert rc != 0
    assert "install directory" in stderr


def test_ownership_rejects_install_dir_via_executable(tmp_path):
    """A dir with a `leerie` executable at top level and no runs/ looks
    like the installer's leerie clone."""
    state_dir = tmp_path / "fake-install"
    state_dir.mkdir()
    leerie_exec = state_dir / "leerie"
    leerie_exec.write_text("#!/bin/sh\n")
    leerie_exec.chmod(0o755)
    rc, _, stderr = _run_ownership(
        "/tmp/something/leerie", state_dir, expect_fail=True
    )
    assert rc != 0
    assert "install directory" in stderr


def test_ownership_claims_empty_dir(tmp_path):
    """An existing empty dir with no markers gets claimed without ceremony."""
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    repo = "/tmp/test/myproject"
    rc, _, _ = _run_ownership(repo, state_dir)
    assert rc == 0
    assert (state_dir / ".owner").read_text().strip() == repo
