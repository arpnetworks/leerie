#!/bin/sh
# container-entry.sh — PID 1 of the leerie container.
#
# Bind-mounted from $LEERIE_HOME/scripts/container-entry.sh on the host to
# /opt/leerie-image/scripts/container-entry.sh inside the container, and
# referenced by Dockerfile's ENTRYPOINT.
#
# All it does: cd into the user's repo (bind-mounted at /work) and exec the
# orchestrator. PID 1 in a container is what the kernel reaps the namespace
# under when it exits — see docs/DESIGN.md §6 and docs/IMPLEMENTATION.md §0.5.
set -e
# Suppress core dumps from OOM-killed workers — on large codebases
# (e.g. Next.js apps with heavy tsc + bundler memory use), `next build`
# or vitest can be OOM-killed inside Colima and otherwise leave
# multi-GB core files behind in each per-subtask worktree. Setting
# RLIMIT_CORE=0 at PID 1 is inherited by every worker subprocess.
# shellcheck disable=SC3045  # ulimit -c is non-POSIX but supported by dash (Debian's /bin/sh) and bash
ulimit -c 0
cd /work

# Idempotent /home/leerie subtree population. On the Fly path, when
# FLY_VM_DISK_GB is set in provision.sh a per-machine Fly volume is
# mounted at /home/leerie — and the mount masks the Dockerfile's baked
# layout (the COPY layer becomes invisible underneath the fresh
# volume). Re-create the standard subtree here so workers find their
# expected cache directories regardless of whether they're running on
# the bare rootfs (no volume) or on a freshly-attached Fly volume.
# `mkdir -p` and `chown -R` are no-ops on already-populated trees, so
# the local nerdctl path (which never sees this code mid-runtime,
# because container-entry runs once at startup) is unaffected.
# (DESIGN §6 *Remote disk policy*; IMPLEMENTATION §0.5 *Container shape*.)
if getent passwd leerie >/dev/null 2>&1; then
  mkdir -p \
    /home/leerie/.local/share/mise \
    /home/leerie/.cache/leerie/pnpm-store \
    /home/leerie/.cache/leerie/pip \
    /home/leerie/.cache/leerie/go-mod \
    /home/leerie/.cache/leerie/cargo \
    /home/leerie/.claude \
    2>/dev/null || true
  chown -R leerie:leerie /home/leerie/.local /home/leerie/.cache /home/leerie/.claude 2>/dev/null || true
  # .gnupg permissions matter to gpg (refuses to use a directory with
  # group-readable permissions). Only chmod if it exists — we don't
  # want to materialize one and trip a worker into thinking GPG is
  # configured.
  if [ -d /home/leerie/.gnupg ]; then
    chmod 700 /home/leerie/.gnupg 2>/dev/null || true
  fi
fi

# When invoked with no args (remote/Fly path), idle as PID 1 so the
# machine stays up. The remote launcher invokes the orchestrator
# separately by piping a Python wrapper through
# `flyctl ssh console -C "python3 -"` (the wrapper uses
# subprocess.Popen with start_new_session=True + user="leerie" so the
# orchestrator detaches cleanly with the right identity). The
# container entrypoint just needs to keep the namespace alive. Local
# nerdctl always passes argv (the task + flags), so this branch
# never fires in local mode.
if [ "$#" -eq 0 ]; then
  exec sleep infinity
fi

exec python3 /opt/leerie-image/orchestrator/leerie.py "$@"
