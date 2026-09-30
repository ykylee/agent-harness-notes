# 01. Gas Town — the vocabulary

> Read from `gastownhall/gastown` @ `649b832b76` (2026-07-23, `v1.2.1-304-g649b832b`).
> `docs/glossary.md`, `docs/concepts/`, `docs/design/`. MIT.
>
> **This file is a vocabulary, not an endorsement.** Gas Town is one team's operating model with
> one set of trade-offs. It is recorded here because its abstractions are testable against the
> other studies in this repository, not because it is the right answer for everyone.

## 1. Why this belongs in a study of *harnesses*

The other four studies in this repository read **one** harness at a time: a loop, a set of
primitives, a wire. Gas Town sits one level above all of them. It does not implement an agent
loop — it **schedules, attributes and reconciles** many loop instances running at once. Its stated
problem is the operator's problem, not the agent's:

> Operators now run 20–30 agent instances against the same repository. The hard questions move up
> a level: who assigns the work, where does the work state live when a session dies, how do two
> agents avoid colliding, and how do you tell "running" apart from "done"?

That framing is the reason to read it here. The unit of analysis changes from *the agent* to *the
fleet*, and the primitives that matter change with it: identity, durable assignment, capacity,
and attribution of outcomes.

## 2. The two namespaces

Gas Town has two separate vocabularies that are easy to confuse. Almost every confusion in reading
the docs comes from mixing them.

### 2.1 **Where things live** — the container hierarchy

| Term | What it is |
|---|---|
| **Town** | The management root, e.g. `~/gt/`. Owns rigs, the mayor, town-level beads (`hq-*` prefix). **Not a git repo itself** — a container for them. |
| **Rig** | One project's container. Wraps a git repository (the canonical clone lives at `<rig>/mayor/rig/`) and owns that project's agents. Rigs are the unit of isolation. |
| **Hook** | A worktree-based persistent store that is an agent's *work queue*. Survives crash and restart. This is the durable-identity anchor. |
| **Convoy** | A persistent tracking unit that watches a set of beads until they land. `hq-cv-*`. |
| **Swarm** | *Not* a stored object. "The polecats currently working a convoy's issues" — an emergent set, no ID. |
| **Formula / Molecule / Wisp** | The workflow layer (§3). |

The two-level beads split follows the same seam: `~/gt/.beads/` holds **cross-rig** coordination
(`hq-*`); each rig's `.beads/` holds **implementation** work (project prefix). An epic that spans
projects lives at town level; a bug does not.

### 2.2 **Who does what** — the role taxonomy

Two tiers, deliberately: town-level agents coordinate *across* projects, rig-level agents work
*within* one.

| Role | Scope | Lifetime | Responsibility |
|---|---|---|---|
| **Mayor** | Town | persistent | The operator's interface. Decomposes intent, creates convoys, dispatches, notifies. |
| **Deacon** | Town | persistent | Town watchdog. Runs patrol cycles, receives heartbeats, triggers recovery. |
| **Boot** | Town | ephemeral | *The Dog that checks the Deacon* every ~5 min. The watchman's own supervisor. |
| **Dogs** | Town | variable | Deacon's maintenance crew: cleanup, health, batch work. |
| **Witness** | Rig | persistent | Supervises that rig's polecats and refinery; nudges, cleans up, detects stuck workers. |
| **Refinery** | Rig | persistent | Owns the **merge queue** for the rig. Serializes merges, runs verification, CI gates. |
| **Polecat** | Rig | **persistent identity, ephemeral session** | The worker. Spawned for a task, session ends on `gt done`, but identity + work history persist. Works in an isolated git worktree. |
| **Crew** | Rig | persistent, human-managed | A named long-lived workspace for collaborative human+agent work. Full clone. |

**Polecat is the load-bearing concept.** It encodes the central claim in one type: *the identity
is durable, the session is disposable.* Every other role is a variation on who supervises whom.

## 3. The work-unit vocabulary

This is the part worth stealing, because it answers "where does work state live" without
depending on any agent's memory.

| Term | Storage | Lifetime | What it is |
|---|---|---|---|
| **Bead** | Dolt DB (git-backed) | durable | The atomic work record. "Issue" and "bead" are used interchangeably. |
| **Formula** | TOML source | durable template | A reusable multi-step workflow definition. |
| **Protomolecule** | frozen | template | A Formula compiled and ready to instantiate. |
| **Molecule** | — | active instance | A running workflow; each step is tracked. |
| **Wisp** | `.beads/` (ephemeral) | destroyed after run | A throwaway workflow instance — patrols, polecat runs. Never synced. |
| **Hook** | worktree | durable per agent | The pinned bead that is that agent's current assignment. |

A **hook** is the pivot: it is a pinned bead, and the propulsion rule (§4) makes looking at it
mandatory. Work is not "assigned in a message" that can be lost; it is *sitting on a durable
object the agent is obligated to inspect*.

### 3.1 Molecule lifecycle, and the `pour` decision

```
Formula (source TOML) ──bd cook──▶ Protomolecule ──bd mol pour──▶ Molecule (persistent)
                                     │
                                     └──bd mol wisp (default)──▶ Root Wisp (ephemeral)
```

The default (`root-only`) materializes **one** row and has the agent read steps inline from the
embedded formula at prime time. The alternative (`pour = true`) materializes each step as a
sub-wisp with checkpoint recovery, so a crashed session resumes from the last closed step.

The stated reason for the default is worth recording because it is an *operational* number, not a
design preference: root-only avoids ~6,000 rows/day of wisp accumulation, dropping it to ~400/day.
The doc's own heuristic:

> If you would curse losing the progress after a crash, set `pour = true`.

i.e. **cheap high-frequency runs stream their steps; expensive rare runs checkpoint them.** That
is a storage-vs-durability trade made per workflow rather than globally.

## 4. The propulsion principle (GUPP)

> **If you find something on your hook, YOU RUN IT.**

This is the system's engine, and it is stated more bluntly than most orchestrators dare. There is
no supervisor polling "did you start?" — the hook *is* the assignment, and waiting is a stall.
The failure mode it names is precise and worth stealing:

```
Polecat restarts with work on hook
  → Polecat announces itself
  → Polecat waits for confirmation          ← the bug
  → Witness assumes work is progressing
  → Nothing happens
  → Gas Town stops
```

The lesson generalizes past this tool: **a supervisor that infers progress from silence will
happily supervise a stall.** Whatever the agent does next has to be non-negotiable enough that a
fresh session with an empty context window still does it.

The startup contract is correspondingly blunt: check hook → if work, execute → if empty, check
mail → if nothing, escalate. Note the ordering — the hook is checked *before* asking anyone.

## 5. Identity and attribution

`BD_ACTOR` is a slash-formatted path — `gastown/polecats/toast`, `gastown/witness` — and the
slashes are load-bearing, not cosmetic: they make the actor **hierarchically parseable** (rig,
role, name) and **directly addressable** as a mail route. The filename convention is the
addressing scheme.

Attribution is three-field, and the git case is the sharp one:

```
GIT_AUTHOR_NAME  = gastown/crew/joe      # who did it (the agent)
GIT_AUTHOR_EMAIL = steve@example.com     # who owns it (the human)
```

So a commit reads `gastown/crew/joe <steve@example.com>` — **agent and owner are separable in
history, permanently.** The doc's justification is worth quoting because it is the compliance
argument, not the engineering one: "Auditors ask *who approved this code* — you need an answer."
Beads records carry `created_by`/`updated_by`; events carry `actor`.

**The generalizable idea:** make attribution a *structural property of the storage format* rather
than a convention people are asked to follow. Gas Town gets it free because the actor id is the
address and the ownership is the email, both already required by git.

## 6. What to take from this, and what to be careful about

Worth taking:

- **Persistent identity + ephemeral session** as the unit of a worker.
- **Work state in a durable ledger, not in agent context** — and make the agent *obligated* to read
  it at startup (propulsion).
- **A dedicated merge serializer** (Refinery) so N writers never merge concurrently.
- **Watch the watchers** (Boot checks Deacon) — liveness of the supervisor is its own problem.
- **Two planes** (control vs execution) kept separable, so the control plane keeps its identity
  even when the worker is sandboxed.
- **Per-workflow durability choice** (stream steps vs checkpoint steps).

Be careful about:

- **The operational surface is large** — a Go binary, a Dolt server, tmux, per-rig worktrees, a
  Dolt database per rig. That is a real cost, not a free abstraction.
- **"Kubernetes for AI agents" is 📣 marketing, not a claim.** The accurate comparison is narrower:
  both reconcile a fleet against a durable source of truth; the difference is what you ask
  (k8s: *is it running?* — Gas Town: *is it done?*). Do not adopt the analogy further than that.
- **The self-reported cost is high** and unverified by me: operators report ~$100/hour at 12–30
  agents. I have not measured it. Treat as a vendor-adjacent anecdote, not a benchmark.
- **The "hysteresis" argument is a real limitation, not a solved problem** — see
  [`04-orchestration-techniques.md`](04-orchestration-techniques.md), which is where that lands
  against this repository's own findings.

## Read next

- [`02-architecture.md`](02-architecture.md) — the directory and storage layout, the two-level
  beads split, and how a worker is actually spawned.
- [`03-roles-and-lifecycle.md`](03-roles-and-lifecycle.md) — the supervision tree, heartbeats,
  and the mail protocol that binds the roles into a workflow.
- [`04-orchestration-techniques.md`](04-orchestration-techniques.md) — the techniques worth
  reusing, and this repository's own evidence about them.
- [`99-sources.md`](99-sources.md) — verification status, what was read, what was not.
