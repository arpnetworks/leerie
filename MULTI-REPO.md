# Multi-repo support for leerie — the "run-group" design

## Next actions to raise the sub-90% rows (chosen 2026-07-06)

Investigation has hit its floor: the three rows still under 90% solution confidence are
**unbuilt/unrun code**, and only running or building moves them. Concrete plan:

1. **Row 6 (fly tag-back, 88%) + Row 10-fly (70%)** → **run one fly-runtime group spike.**
   Two throwaway repos, `--group`-style fan-out with `--runtime fly`, then verify the
   `remote/<pid>.json` / `fly-machine.json` tag-back (`leerie:2263-2289`) resolves each member's
   run-id and stamps `group_id` across the two state dirs. Cost: real Fly machines + a few minutes.
   Pass = both fly members discovered by a cross-dir `group_id` scan, mirroring the local spike.
2. **Row 8 (deploy-note plumbing, 85%)** → **build the Stage 3d slice + its test.** Thread
   `external_preconditions` → pr_writer payload (`:14402`) + `compose_pr_body` (`:2031`); extend
   `tests/test_compose_pr_body.py` with a deploy-note case. Row moves when the test passes.

These are execution steps, not further analysis — the matrix will not change until they run.

## Context

**The problem (from `feedback.txt`).** A power user (Garry) described a real change that
had to span **two repos** — an API repo and a frontend repo — for one logical feature
("customers add storage volumes to their servers, self-service"). Leerie only works on one
repo, so the user's workaround is: run a *prompt decomposer* to split the task into two
prompts, then fire **two independent `leerie` invocations, one per repo**, each side
**blind to the other**. It worked, but it's manual toil and the two planners never see each
other's contract.

**What the user wants** (decided in planning): cross-repo-*aware planning* — repo B's
planner should see repo A's actual contract — via the **lean run-group** shape (not the
deep "one run, N run-branches" rewrite), on **both runtimes** (local + fly), with cross-repo
prerequisites surfaced as **deploy-ordering notes**.

**Why the lean shape.** The value the user described (a coordinated, contract-accurate
feature) comes from the **shared plan**, not from atomic joint execution: two PRs across two
repos *cannot* merge atomically on GitHub regardless of design — the inconsistency window
(frontend calls an endpoint not yet deployed) is a deploy-ordering fact, which the user
already handles with beta-feature flags. So we keep each repo's run **fully isolated** (one
repo, one run-branch, one PR, unchanged resume/state) and add a thin **group** layer:
launch them together, share a brief, give read-only cross-repo visibility, and render
deploy-ordering notes. The deep alternative (one run spanning N repos) was rejected because
it rewrites leerie's single most load-bearing invariant — the run branch as the resume
contract (`DESIGN.md` §6, "a run branch, once created, is never reset").

---

## Confidence: what investigation established (executed, not just read)

This plan was pressure-tested by **reading the exact control-flow paths, running the relevant
test suite, and executing a subshell simulation of the state-dir resolution.** Confidence
below is per-claim, split into *diagnosis* (is my understanding of current code correct?) and
*solution* (will the proposed change work?).

**Executed during investigation:**
- `pytest tests/{test_chain_launcher_id_dispatch,test_chain_launcher_sequencer,test_resolve_state_dir,test_state_per_run,test_launcher_verb_filter,test_fly_state_dir_sidecar}.py`
  → **93 passed in 23s.** The bash-harness approach a `--group` feature extends is proven and fast.
- **Subshell simulation of `leerie:431-463`** to observe env-inheritance directly (below).
- Three parallel deep code-traces (launcher fan-out/verbs, preconditions→PR path, inspect-dir
  seeding + planner steering), each cross-checked against my own reads.
- **Live inspect-dir probe (2026-07-06)** — ran a real single-repo leerie with `--inspect-dir`;
  5 workers read the sibling contract (row 11).
- **Inspected the machine's real state** — 12 coexisting per-repo state dirs and 12+ completed
  `run.json` files, confirming the tag-back discovery target and per-repo isolation *at scale*
  (rows 5/6/7) rather than by inference.
- **Live group-layer spike (2026-07-06)** — ran the run-group coordination flow end-to-end on the
  **local** runtime with two throwaway repos: fanned out two real `leerie` runs (each `cd`'d into
  its repo, sibling as `--inspect-dir`), both finished rc=0 in **distinct** state dirs, then tagged
  both `run.json` with a shared `group_id` and discovered **exactly 2 members** via a cross-state-dir
  scan. **Every group-layer checkpoint passed** (rows 7/9/10-local). Fly path remains unrun.

### Confidence matrix (post-investigation)

| # | Claim | Diagnosis | Solution | Evidence |
|---|---|---|---|---|
| 1 | Per-repo isolation is free (basename-keyed state dirs) | **98%** | **95%** | Read `:431/:502`; **ran** subshell sim confirming `:437` clobbers inherited value |
| 2 | Cross-repo read visibility via `--inspect-dir` | **97%** | **93%** | Traced `:3359-3407` (`:ro` `:3401`), seed `:711/:962`, `--add-dir` `:6609` |
| 3 | Write-confinement stays enforced | **97%** | **95%** | Read `filter_offtree_subtasks` `:4450`, soft-drop `:4487-4506` |
| 4 | `external_preconditions` durable + exact shape known | **97%** | **93%** | Shape `{tag,reasons:[{sid,reason}],originating_subtasks}` at `:8861`; plan.json `:12306` |
| 5 | Local group tag-back (scan newest `run.json`, no `--rm` race) | **97%** | **92%** | Traced `:4967-4992`; **inspected 12+ real local `run.json` on this machine — all carry `{branch,working_branch,finished_at,pushed_at,pr_url}`, the discovery fields, and are distinguishable from fly runs (no `fly_machine_id`)** |
| 6 | Fly group tag-back (existing pointer path) | **93%** | **90%** | Read `:2263-2289`; **`update_run_json` (`lib.sh:70-113`) confirmed runtime-agnostic atomic merge**; real fly `run.json` seen carrying `fly_machine_id` |
| 7 | `--group` fan-out isolates state per member | **99%** | **98%** | **LIVE SPIKE (2026-07-06):** fanned out two real local runs (`grp-api`, `grp-web`) → **two distinct state dirs, two run-ids, two run branches, both rc=0** — isolation observed, not inferred |
| 8 | Deploy-note plumbing (State→PR body) | **95%** | **85%** | 5 gaps mapped exactly; `reason` is **unstructured free text** (no `repo` field) — *not exercised by the spike* |
| 9 | Group-scoped verbs (cross-state-dir scan) | **94%** | **92%** | **LIVE SPIKE:** `update_run_json … group_id` tagged both members via the finalize-mirror discovery scan; a single cross-dir `group_id` scan then found **exactly 2 members** across the two separate state dirs — the core verb mechanic, executed |
| 10 | Both runtimes end-to-end → N PRs | **88%** | **88%** | **LIVE SPIKE validated the full LOCAL flow** (fan-out → tag-back → cross-dir discovery). **Fly path still unrun** (traced-only `remote/<pid>.json` tag-back) — that's the remaining ceiling on this row |
| 11 | Brief + visibility yields **good** cross-repo planning | **92%** | **85%** | **LIVE PROBE (2026-07-06):** ran real single-repo leerie in `frontend` with `--inspect-dir ../api` + a contract-honoring task. **5 workers — classifier, provision, and all 3 planner samples (s0/s1/s2) — each autonomously `Read` `/inspect/api/api/volumes.py`** and picked up the trap (`size_gib` not `size_gb`). Reading behavior is robust/repeated, not a fluke. |

### The three findings that moved the numbers (all executed/traced this round)

1. **State-dir isolation is safe — proven by running it.** The launcher exports the *output*
   var `LEERIE_STATE_HOST_DIR` (`:490`) but resolution reads the *input* var `LEERIE_STATE_DIR`
   (`:461`) — different names — and `:437` unconditionally re-derives from cwd basename. My
   subshell sim confirmed: a child that `cd`s into `../frontend` gets `~/.leerie/frontend`
   even while inheriting the parent's `LEERIE_STATE_HOST_DIR=~/.leerie/api`. **Trap found:** if
   `LEERIE_STATE_DIR` or `--state-dir` is set, the `:461` override pins **all** members to one
   dir (`.owner` then errors on member 2). The chain passthrough (`:2077-2083`) forwards any
   `--flag value` blindly. **→ New plan requirement: the `--group` arm must reject / per-member-
   namespace `--state-dir` and `LEERIE_STATE_DIR`.**

2. **Deploy-notes need more than rendering — the data is unstructured.** `external_preconditions`
   entries carry `reason` as **free text** (schema-optional; `required` is only `[tag, extent]`,
   `:691`). The planner prompt *asks* it to "name the owner" (`planner.md:108`) but a group
   **cannot reliably parse** which sibling repo a precondition names. **→ To render "depends on
   repo A" reliably, the group must inject the sibling-repo identity itself** (it knows the
   member repos), not scrape planner free-text. Five plumbing gaps confirmed (not in run.json,
   pr_writer payload, pr_writer prompt, `compose_pr_body`, or host-finalize.sh).

3. **Planner steering — the load-bearing risk — is now VALIDATED by a live probe.** The
   inspect-dir *plumbing* works (kernel `:ro` locally; `--add-dir` so Read/Grep/Glob reach
   `/inspect/<A>`). The open question was whether workers *actually read* a sibling's contract,
   since the only inspect-dir prompt mentions are *constraints* (`planner.md:279-284`). **Probe
   answer (2026-07-06): yes, robustly.** A real single-repo leerie run in a `frontend` repo with
   `--inspect-dir ../api` and a task saying "read the api contract and honor it" produced **5
   workers (classifier + provision + all 3 planner samples) each independently `Read`
   `/inspect/api/api/volumes.py`** and absorbing the deliberate trap (`size_gib`, `reboot_required`,
   response fields). The §12 read-only gate also fired live (a compound `git -C /inspect/api`
   Bash was soft-blocked; the worker adapted). **Consequence for the plan:** Stage 3e drops from
   "load-bearing for reading" to "reliability polish" — the reading already happens from task/brief
   wording; the prompt change just makes it dependable *without* the user hand-writing "read the
   sibling" each time. The shared brief is what supplies that directive.
   *Caveat unchanged:* Fly read-only is convention (`chown leerie:`), not kernel-enforced — fine
   for a read-only sibling, but note the asymmetry.

**Bottom line:** every code-checkable claim (rows 1–9) is now diagnosed at **92–98%** and
solutioned at **82–95%** — the remaining solution risk is "new code to write," not "unknown
behavior." Rows 10–11 (end-to-end + planning quality) reach **75–78%** on paper; they are
gated by the live 2-repo smoke test (verification step 5), which is the only thing that can
push them to 90%+. The investigation **converted the two biggest unknowns into concrete,
code-level plan requirements** (the `--state-dir` guard and the load-bearing planner-prompt
change) rather than leaving them as hopes.

**Net:** execution isolation and cross-repo *read* visibility are verified-free. The genuinely-new
work is a modest **group-coordination layer** (group tagging across state dirs on both runtimes,
group-scoped verbs, deploy-note plumbing) — larger than first sold, but still far cheaper and
lower-risk than the deep design's resume-contract rewrite.

---

## The design in one paragraph

A **run-group** is N ordinary single-repo leerie runs, launched together, sharing a
`group_id` (UUID) written into each member's `run.json`. Each member is **unchanged**: one
writable repo (its own basename-keyed state dir), one `leerie/runs/<run-id>` branch, one
flat `state.json`, one PR, ordinary `--resume`. The group adds: (a) a **shared brief** — the
joint intent + each side's contract — authored once and prepended to every member's prompt;
(b) each member launched with its **siblings seeded read-only** via existing `--inspect-dir`;
(c) **deploy-ordering notes** — a member's `external_preconditions` naming a sibling repo are
rendered as a "merge/deploy sibling first" section in that repo's PR body; (d) **group-scoped
verbs** (`--status`/`--resume`/`--finalize`/`--kill`/`--list --groups`) that discover members
by `group_id` **across** their separate state dirs. The laptop is the sequencer; no
in-container coordinator (per §19). Because each member is a normal run, **resume, isolation,
state, and finalize mechanics are untouched.**

---

## PHASE 1 — `docs/DESIGN.md` (canonical, land first)

### New section: §20 "Run groups (multi-repo)" (insert after §19 chains, ~`DESIGN.md:3525`)
- **A run-group is N isolated single-repo runs sharing a `group_id`.** Each member is an
  ordinary run; the group coordinates at *launch* and *reporting*, never at
  execution/integration. Note the isolation is free: members live in **separate
  basename-keyed state dirs** (`$HOME/.leerie/<basename>`), each with its own flock and
  resume record.
- **Cross-repo visibility is read-only.** Each member sees siblings via read-only
  `--inspect-dir` (`/inspect/<name>`); it **never writes** a sibling — the existing
  `filter_offtree_subtasks` guard (§12) enforces this, unchanged. The shared brief is
  advisory steering; the write-confinement is the code guarantee.
- **The shared brief** makes planning cross-repo-*aware*: repo B's planner reads repo A's
  actual code (inspect-dir) *and* is told what repo A is building (brief).
- **Non-atomic PRs + deploy-ordering notes.** State plainly: a group opens **N PRs, one per
  repo, NOT atomic** — GitHub merges stay independent. Cross-repo prerequisites are declared
  `requires.extent: external` (existing channel, §5) with a `reason` naming the sibling;
  collected into `external_preconditions`; rendered by finalize as a deploy-ordering note.
  Do not imply atomicity the two-PR reality can't provide.
- **The laptop is the sequencer; no coordinator machine** (cite §19). GitHub touched only
  host-side, per-member, via each member's existing `host_finalize`.
- **Single-repo is the N=1 degenerate case.**

### Edit §5 (`DESIGN.md:333`, `requires.extent`)
Add a sentence: the canonical `extent: external` example ("a table provisioned by another
repo") now has first-class tooling in a run-group — a sibling repo *in the same group* is
still `external` (not in *this member's* build graph), and its `reason` is what finalize
turns into a deploy-ordering note. Cross-repo deps stay `external` **by design** (they are
not hard DAG edges — the deep design we did not take).

### Edit §15 "Known limitations" (`DESIGN.md:3182-3187`, "Parallelism is single-clone")
Amend: cross-*run* independence is unchanged, but leerie now offers a **run-group** to launch
N single-repo runs together with shared context and read-only cross-repo visibility. State
the boundary: the group does **not** merge across repos, does **not** produce cross-repo DAG
edges, and its PRs are non-atomic.

### Edit §19 "Chain orchestration" (`DESIGN.md:3354`)
Add "Relation to run-groups": chains sequence N *same-repo* runs across waves with
synth-merge; run-groups launch N *different-repo* runs in parallel with **no** synth-merge and
**no** waves. Both share the "laptop-is-sequencer, tag in `run.json`, ID-dispatched verbs"
shape — **but** run-group verbs must scan **across** members' separate state dirs (chains scan
one), so the machinery is shared in spirit, not code. A "multi-repo chain" is out of scope.

---

## PHASE 2 — `docs/IMPLEMENTATION.md` (code-surface spec)

- **`group_id` in `run.json`** — spec alongside `chain_id`; note `_validate_run_json`
  (`orchestrator/leerie.py:1906`) accepts the new optional key.
- **Launcher `--group` verb** — `leerie --group --repo <path> "<prompt>" --repo <path>
  "<prompt>" [--brief <file>]`. Modeled on the `--chain` arm (`leerie:2033`) but: cd's into
  each member repo (so each resolves its own `USER_REPO`/state dir), seeds siblings as
  read-only `--inspect-dir`, prepends the brief. Per-member flags forward like
  `_ch_passthrough`.
- **Group tag-back across state dirs, both runtimes** — spec that after fan-out the launcher
  writes `group_id` into each member's `run.json`, discovering each member's run dir under
  **its own** `$HOME/.leerie/<member-basename>/runs/*`. Unlike chains (single dir, Fly-only
  `remote/<pid>.json`), the group must locate each member run in a per-member state dir on
  **both** local and fly. Spec the discovery mechanism (e.g. each backgrounded member writes
  a `remote/<pid>.json`-equivalent pointer the launcher reads, generalized to a runtime-neutral
  "member ran here" pointer, or the launcher captures each member's resolved run-id from its
  stdout/a sentinel file).
- **Group-scoped verbs** — `--status`/`--resume`/`--kill`/`--finalize`/`--list --groups` on a
  `group_id` iterate members across their state dirs. Spec a `_group_runs_filter` that (unlike
  `_chain_runs_filter`, `leerie:191`) scans a set of state dirs, not one.
- **Deploy-ordering notes** — spec the new State→finalize path: `external_preconditions`
  (already in `plan.json`/State) is threaded into the pr_writer payload and the
  deterministic `compose_pr_body` fallback, rendering a "## ⚠ Deploy-ordering" section
  (a `- **<tag>** — <reason>` bullet per precondition) when the plan declared any
  cross-repo prerequisite.
- **No new subtask schema, no new caps, no state-schema change** — explicitly note each member
  is an ordinary run; `STATE_FIELDS`, `DEFAULT_CAPS`, `filter_offtree_subtasks`, branch helpers
  unchanged. This is the point of the lean shape.

---

## PHASE 3 — Code (staged; single-repo unchanged at every step)

### Stage 3a — the `--group` launcher verb (bulk of the feature)
**File: `leerie`.** New `--group` arm modeled on `--chain` (`:2033-2396`):
1. Parse repeated `--repo <path> "<prompt>"` pairs + optional `--brief <file>`; collect
   per-member passthrough into an array.
2. Fail-fast: each repo path is a git repo (mirror the chain prompt-file check `:2136`).
3. Mint `_group_id` (copy `:2125`).
4. Per member: build prompt as `<brief>\n\n<member prompt>`; append `--inspect-dir
   <sibling-repo>` for every other member (reuse translation `:3337`+).
5. Background `( cd <repo> && "${LEERIE_SELF_CMD:-$0}" "<prompt>" <flags> --group-id
   "$_group_id" ) &` per member (mirror `:2237-2246`); `wait` all.
   **Key difference from `--chain`:** chains reject non-`$USER_REPO` targets (`:2070`) and
   `git -C "$USER_REPO" checkout` (`:2229`); the group cd's into each member repo so each
   resolves its own `USER_REPO`/state dir — **verified free** by `_state_dir_default`
   (`:431`) + `.owner` (`:502`), and confirmed by subshell simulation.
6. **REQUIRED GUARD (found by running the resolution sim).** The `--group` arm must **reject
   or per-member-namespace `--state-dir` and `LEERIE_STATE_DIR`** — both hit the `:461` override
   that pins every member to one shared state dir (`.owner` then errors on member 2). Unlike
   `--chain` (single repo → shared dir is correct), a group needs distinct per-member dirs, so
   it must not forward these blindly the way the chain passthrough does (`:2077-2083`), and must
   not `export LEERIE_STATE_DIR`. Add a test asserting two members land in distinct
   `~/.leerie/<basename>` dirs even when the parent env carries `LEERIE_STATE_HOST_DIR`.

### Stage 3b — group tag-back (both runtimes) + `--group-id` in `run.json`
**File: `orchestrator/leerie.py`.** Add `--group-id` CLI arg; write it into `run.json`
(`_write_run_json`, `:14406`); accept it in `_validate_run_json` (`:1906`). A member with a
`group_id` behaves identically otherwise.
**File: `leerie`.** After fan-out, tag each member's `run.json` with `group_id`, locating each
member's run dir under its **own** `$HOME/.leerie/<member-basename>/runs/*`. **Traced mechanism
(both runtimes, no teardown race):**
- *Local:* after `wait` on the member, scan `<member-state-dir>/runs/*/run.json` for the newest
  with `finished_at` set — the **same discovery the local finalize already uses**
  (`leerie:4967-4992`). The member's `run.json` is durably on disk by then (run-id is the dir
  name). No cidfile read, no `--rm` race.
- *Fly:* the existing `remote/<pid>.json` / `fly-machine.json` path (`leerie:2263-2289`).

The parent knows each child's pid (`$!`) and repo (→ basename → state dir), so the only new code
is: for each member, resolve its state dir from its repo basename and apply the runtime-matched
discovery above, then `update_run_json … group_id "$_group_id"`. No new per-child pointer file is
required — the durable `run.json`-on-disk is the coordination artifact. (Optional hardening: if a
member's state dir could hold a *prior* unrelated run, capture the authoritative run-id from
`.cidfile-<child-pid>` during the run to disambiguate instead of relying on "newest.")

### Stage 3c — group-scoped verbs
**File: `leerie`.** Add `_group_runs_filter` that scans the set of member state dirs (derived
from the group's member repos, or a small group-manifest the launcher drops) for
`group_id`-tagged `run.json`. Wire `--status`/`--resume`/`--kill`/`--finalize` on a `group_id`
and `--list --groups`. Cannot reuse `_chain_runs_filter` (`:191`) directly — it assumes one
state dir; factor the shared JSON-scan and give it a set-of-dirs mode.

### Stage 3d — deploy-ordering notes in PRs
**File: `orchestrator/leerie.py`.** Thread `external_preconditions` (durable in State `:222` /
`plan.json` `:12306`; verified entry shape `{tag, reasons:[{sid,reason}], originating_subtasks}`)
into the pr_writer payload (`:14402`), `prompts/pr_writer.md` input spec, and the deterministic
`compose_pr_body` fallback (`:2031`) — **all five gaps** the trace found (also `_write_run_json`
and the `host-finalize.sh` bash fallback if the note must survive the LLM-less path). Render a
"⚠ Deploy-ordering" section. **Key design consequence (found in trace): `reason` is unstructured
free text — the group must NOT scrape it to identify the sibling.** Instead, the launcher (which
knows the member repos) passes the group's repo list to each member so the orchestrator can label
a precondition as sibling-owned by matching, or simply render the group members as "related PRs"
regardless of `reason` parsing. No `host-finalize.sh` push/PR-mechanic change — each member still
opens its own PR. **Extend `tests/test_compose_pr_body.py`** (17 existing tests) with a deploy-note case.

### Stage 3e — planner steering (LOAD-BEARING, not optional — §12)
**File: `prompts/planner.md`.** The trace found **no existing prompt instruction steering the
planner to read a sibling repo's contract** — the only inspect-dir mentions are *constraints*
(`planner.md:279-284`, "you may not write there"). So without this change, "repo B's planner
sees repo A's contract" is emergent/task-text-driven, not reliable — this is the single change
that lifts the feature's core value (row #11) from ~50% to ~78%. Add a **positive** instruction:
when an inspect-dir is a group sibling (signaled via the brief/a new marker), it is a **peer repo
whose interface/contract you must read (Read/Grep/Glob under `/inspect/<name>`) and honor**, and
declare cross-repo prerequisites as `requires.extent: external` naming the sibling. This is still
"advisory" in the §12 sense (the write-confinement *guarantee* stays code via
`filter_offtree_subtasks`), but it is **functionally required** for the feature to deliver value —
promote it from a footnote to a first-class stage. *Note the runtime asymmetry:* inspect-dir
read-only is kernel-enforced locally (`:ro`) but convention-only on Fly (`chown leerie:`,
`seed-repo.sh:798`) — acceptable for read-only siblings since acting workers get no `--add-dir`,
but document it.

---

## What we deliberately do NOT build (deferred)

- **N run-branches in one run / per-repo state substructure** (the deep design's
  resume-contract rewrite). Each member is its own resumable run — not needed.
- **Cross-repo `in_plan` DAG edges** (repo A's subtask as a hard predecessor of repo B's).
  Cross-repo deps stay `external` deploy notes. A future group-level shared-planning pre-pass
  is out of scope unless evidence shows read-only visibility + brief miss couplings.
- **Writable sibling repos in one process / a repo registry replacing `os.getcwd()`.**
- **Cross-repo synth-merge** (impossible across repos).
- **Atomic 2-PR landing** (not achievable; handled by deploy notes + the user's beta-flag gating).

---

## Critical files

| File | Change |
|---|---|
| `docs/DESIGN.md` | **First.** New §20 "Run groups"; edits to §5, §15, §19. |
| `docs/IMPLEMENTATION.md` | `group_id`; `--group` verb; **cross-state-dir** group tag-back + verbs (note: NOT a chain-verb generalization); deploy-note plumbing; "no schema/state/caps change." |
| `leerie` (launcher) | New `--group` arm (`:2033` model); reuse inspect-dir translation (`:3337`); **new** runtime-neutral group tag-back + `_group_runs_filter` (cannot reuse single-dir `_chain_runs_filter` `:191`). |
| `orchestrator/leerie.py` | `--group-id` arg + `run.json` (`:14406`, `:1906`); `external_preconditions` → pr_writer payload (`:14402`)/`compose_pr_body`. |
| `prompts/planner.md` | Advisory cross-repo steering note. |
| `tests/` | `--group` fan-out (stubbed `./leerie`, model on `tests/test_chain_launcher_id_dispatch.py`); group-id run.json validation; **cross-state-dir** group-verb filtering; deploy-note rendering. |

**Unchanged (verified reuse):** `filter_offtree_subtasks`, `STATE_FIELDS`/`state.json`,
planner/subtask schemas, `DEFAULT_CAPS`, branch helpers, `new-worktree.sh`/`setup-run.sh`/
`integrate.sh`/`finalize.sh`/`host-finalize.sh` mechanics, the seed-repo inspect-dir path,
per-repo state-dir isolation (`_state_dir_default`/`.owner`).

---

## Pre-build spike — ✅ DONE (2026-07-06, PASSED)

**Result:** ran end-to-end on the **local** runtime with two throwaway repos (`grp-api`, `grp-web`).
Fan-out → two distinct state dirs / run-ids / run branches (both rc=0) → `update_run_json` tag-back
via the finalize-mirror scan → cross-state-dir `group_id` scan found **exactly 2 members**. All
group-layer checkpoints passed. **Not covered:** the fly runtime and the deploy-note plumbing —
those remain for the full verification below. The spike spec is retained below for reference/repro.

## Fly-runtime smoke — ✅ DONE (2026-07-07, group mechanics PASSED)

Ran `./leerie --group --runtime fly` on two throwaway repos (`grp-api-smoke`, `grp-web-smoke`,
region `sjc`). Rows validated on the **fly** runtime for the first time:

- ✅ **Fan-out reaches every member** — after a bug fix (below), both members provisioned in
  **parallel** (two Fly machines, two volumes, one per member), each seeded independently.
- ✅ **Fly cross-dir `group_id` tag-back (row 6 / fly-half of row 10)** — the `grp-api-smoke`
  member finished (`finished_at` set) and its `run.json`, in its **own** basename-keyed state
  dir `~/.leerie/grp-api-smoke/`, carries `group_id=43406ab7-…` **and** `fly_machine_id` — i.e.
  the fly `remote/<pid>.json` → `update_run_json … group_id` path works, distinct per member.
- ✅ **Cross-repo read visibility + §12 read-only on fly** — both members' workers bundled and
  read the sibling under `/inspect/<name>/`; the kernel `--add-dir` scoping fired live
  (`ls in '/inspect' blocked … only '/work', '/inspect/grp-api-smoke'`), matching the local probe.
- ✅ **Planner steering (Stage 3e) with real depth** — the web planner read the sibling, found the
  API contract wasn't yet materialized, and **declared it `requires.extent: external` owned by the
  sibling** — exactly the deploy-note precondition path. The web implementer later did a live
  field-name contract check (`createVolume({name, sizeGb})`) against `volumesClient.js`.

**Found + fixed a real bug (the smoke's first attempt caught it):** the `--group` fan-out
re-invoked the launcher via a relative `$0` **after** `cd`-ing into each member repo, so the
documented `./leerie --group` form failed with `./leerie: No such file or directory` (chains never
`cd`, so they were immune). Fixed by resolving an absolute `_grp_self_cmd` before fan-out;
source-level regression guard in `tests/test_group_launcher_fanout.py`.

**Not fully closed:** both members ultimately **paused** (`reason=worker-error`) on a flyctl SSH
transport drop (`ssh shell: wait: remote command exited without exit status`) mid-run — a known
flaky-flyctl mode, not a leerie logic defect. The `grp-web-smoke` member's `run.json` never synced
back to the host before its machine was stopped (then removed), so the cross-dir scan found 1 of 2.
leerie handled this correctly: both machines paused and printed `--resume` recovery hints. The full
2-of-2 finalize + N-PR landing is the one remaining item (blocked on flyctl transport stability,
not code); the tag-back **mechanism** itself is proven by the api member.

---

Before committing to the full build, prototype **just the `--group` launcher fan-out + tag-back**
end-to-end on the local runtime, no DESIGN/impl-doc work. This exercises the group layer that the
single-repo probe could not. Grounded in confirmed mechanics: per-repo state dirs coexist by
construction (12 seen on this machine); local `run.json` carries `{branch,working_branch,
finished_at}` (12+ seen); `update_run_json <sidecar> group_id <uuid>` is a runtime-agnostic atomic
merge (`lib.sh:70-113`); verb helpers take `state_dir=Path(sys.argv[1])` (`:208/:269`).

**Cheapest viable spike (a throwaway bash wrapper around today's launcher — no leerie edits):**
1. Two tiny git repos under `$HOME` (Colima-mounted), distinct basenames (e.g. `grp-api`,
   `grp-web`), each with an `origin`-less trivial commit; use a task like `"add a one-line
   comment to README"` so each run is fast.
2. Mint a `group_id` UUID. For each repo: `( cd <repo> && leerie "<task>" --inspect-dir <sibling>
   --skip-smoke --no-push -q ) &`; `wait` both.
3. After `wait`, for each repo scan `~/.leerie/<basename>/runs/*/run.json` for the newest with
   `finished_at` (mirroring `:4967-4992`) and `update_run_json … group_id "$group_id"`.
4. **Pass/fail signal:**
   - ✅ two runs land in **distinct** `~/.leerie/grp-api/` and `~/.leerie/grp-web/` dirs;
   - ✅ both `run.json` end up carrying the **same** `group_id`;
   - ✅ a cross-state-dir scan (`for d in ~/.leerie/grp-*; do jq 'select(.group_id=="…")' …`)
     finds exactly the two members — proving the group-verb discovery works across dirs.
   - ✗ if `--state-dir`/`LEERIE_STATE_DIR` leaks (Case-3 trap) or the two collide → confirms the
     Stage-3a guard is mandatory before any real build.

This settles **row 9** (cross-state-dir discovery works) and most of **row 10** (fan-out +
tag-back end-to-end on local) with running code, *before* writing the real `--group` arm. It does
**not** need the deploy-note or fly paths (deferred to the full verification below). Estimated cost:
two fast, no-push local runs.

## Verification (end-to-end)

1. **Single-repo unchanged (regression gate).** `pytest tests/` green; a normal `./leerie
   "task"` (no `--group`) is byte-identical. Static: `python3 -c "import ast;
   ast.parse(open('orchestrator/leerie.py').read())"`.
2. **Group fan-out (launcher, stubbed `./leerie`).** `./leerie --group --repo ../api "add
   /volumes endpoint" --repo ../frontend "add-disk dialog"` → two children, each `cd`'d into
   the right repo, each carrying `--group-id <uuid>`, the frontend child carrying
   `--inspect-dir <api>` (and vice versa), brief prepended to both. (Model on
   `tests/test_chain_launcher_id_dispatch.py`.)
3. **Cross-state-dir tag-back + verbs.** Assert both members' `run.json` (in their **separate**
   `~/.leerie/api/` and `~/.leerie/frontend/` dirs) carry the same `group_id`; `./leerie
   --status <group-id>` renders both; `--list --groups` groups them; `_validate_run_json`
   accepts the tag. Test on **both** a local-stub and a fly-stub member.
4. **Deploy-ordering note.** Feed a plan whose `external_preconditions` reference a sibling;
   assert the PR body contains the "## ⚠ Deploy-ordering" section with a
   `- **<tag>** — <reason>` bullet. Covered for the Python renderer by
   `tests/test_compose_pr_body.py` and for the LLM-less bash fallback by
   `tests/test_host_finalize_sh.py`.
5. **Live smoke (both runtimes) — the real hypothesis test.** A 2-repo run on two small git
   repos, `--runtime local` and `--runtime fly`: two PRs (one per repo), the frontend PR
   demonstrably informed by reading the API repo during planning (check the plan/PR
   references the real endpoint), the frontend PR body carrying the deploy-note, and each
   member `--resume`-able independently. This is where the "cross-repo planning quality"
   hypothesis is finally validated.
6. **Checklist (`CLAUDE.md`).** Update `IMPLEMENTATION.md`; regenerate `docs/ANALYSIS.md`
   (`python3 docs/tools/leerie_extract.py orchestrator/leerie.py`); validate plugin manifests
   if touched; confirm the deprecated chain-alias case-arms still present (checklist `grep`).
