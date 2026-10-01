# 01. Gas City — the vocabulary

> Read from `gastownhall/gascity` @ `3ef7fadd42` (2026-09-30). Orientation:
> `docs/getting-started/how-gas-city-works.md`, `docs/getting-started/coming-from-gastown.md`.
> Types: `internal/config.Agent`, `internal/beadmeta`. MIT.
>
> **This file is a vocabulary, not an endorsement.** Gas City is the platform Gas Town's machinery
> was extracted into. It is recorded because that extraction is a testable claim about what is
> infrastructure and what is a role.

## 1. Why this is the same axis as Gas Town

[`gas-town/01`](../gas-town/01-vocabulary.md) reads a fleet whose roles have names: Mayor, Witness,
Refinery, Polecat. Gas City's own migration note says two things changed. The orchestrator
hardcodes **zero roles**, and it can run a formula as a **graph across many agents, outside the
session that asked for the work**.

Both sentences are the reason to read it here, and both need a grade. The second is the
load-bearing design and it holds in source (§3, and [`02`](02-architecture.md)). The first holds
for the Go type system and does not hold for what the binary ships (§4).

## 2. Two layers that are easy to mix

Gas Town mixed up *where things live* and *who does the work*. Gas City adds a third mix-up:
*the primitive* versus *the machinery that runs primitives*. The orientation doc separates them
on purpose.

### 2.1 Machinery — role-agnostic plumbing

| Piece | What it is | Where it lives |
|---|---|---|
| **Orchestrator** | Reconciles desired sessions to running ones, drives formula graphs, evaluates orders | `cmd/gc/controller.go`, `internal/dispatch` |
| **Bead store** | Durable work. Tasks, mail, sessions, convoys, and formula steps are beads that differ by type and `gc.kind` | `internal/beads` |
| **Event bus** | Append-only activity log with a monotonic sequence. Fired, not polled | `internal/events` |

The loop the docs describe is the one worth keeping: the orchestrator **acts** on sessions
(start, stop, restart) and **reads** progress from the store and the bus. It is not called back
with the truth. That is why a crash on either side can resume.

### 2.2 The six primitives

The user-facing set in `how-gas-city-works.md`. Pack is in this list; Order is not — an order is
a derived mechanism that says *when* a formula runs.

| Primitive | Question | What it is in source |
|---|---|---|
| **Agent** | who | `config.Agent`: a name, a prompt template, a provider, a scope (`city` / `rig` / unset), session caps. No role field |
| **Bead** | what | One record: id, title, status `open` / `in_progress` / `closed`, type, assignee, needs, labels, metadata |
| **Formula** | how | A TOML method. Applying it materializes beads. Two live contracts, v1 and v2 ([`02`](02-architecture.md) §3) |
| **Rig** | where | A project registered on the city. Its own `issue_prefix` on a shared Dolt server, not its own server |
| **Pack** | configures | A directory with `pack.toml`. The city is the root pack and imports others |
| **Event** | observe | Immutable record. Orders may *read* the stream to decide when to fire; other primitives do not consume events as their state |

**City** is not a seventh primitive. It is the root pack plus deployment: `city.toml`, `.gc/`
runtime state, and the registered rigs.

### 2.3 Orders — when, not who

An order pairs a trigger with either a shell command (**exec order**: no LLM, no session) or a
formula (**formula order**: materializes work for agents). Triggers in `internal/orders/triggers.go`:

| Trigger | Tick behaviour |
|---|---|
| `cooldown` | Due after an interval since the last run |
| `cron` | Minute-granularity schedule |
| `condition` | A shell command exits 0 |
| `event` | A matching event exists after the cursor. Events emitted by order-tracking beads are excluded |
| `manual` | Never tick-fired. `gc order run` |
| `webhook` | Never tick-fired. The supervisor's webhook receiver dispatches it |

Health patrol is not a role. It is the controller tick (default 30s, `[daemon] patrol_interval`)
that reconciles sessions and wakes the orders lane. The Deacon's job, in the Gas Town vocabulary,
moved here.

## 3. Work-unit words that survived

| Term | What it is now |
|---|---|
| **Bead** | Still the atom. Mail is a bead of type message. A session is a bead. A convoy is a container bead |
| **Formula** | TOML method. Canonical filename `formulas/<name>.toml`; `*.formula.toml` is a deprecated alias |
| **Molecule** | A formula instantiated as beads. v1 is a parent-child tree. v2 is a flat graph of blocking edges |
| **Wisp** | An ephemeral molecule. The controller garbage-collects closed wisps past `wisp_ttl` |
| **Hook** | No longer "a worktree that is the queue". The startup contract is the command `gc hook --claim --drain-ack --json` ([`03`](03-roles-and-lifecycle.md) §4) |
| **Sling** | `gc sling` — create and route in one motion |
| **Convoy** | Still a bead-backed batch, not a separate runtime. v2 control beads (fan-out, drain) drive it |
| **Control bead** | Orchestrator-owned step: `retry`, `ralph`, `check`, `retry-eval`, `fanout`, `drain`, `scope-check`, `workflow-finalize` (`internal/beadmeta.ControlKinds`) |
| **Work bead** | A plain step an agent may claim. Independently ready |

The propulsion slogan survived verbatim in `engdocs/architecture/glossary.md`: *"If you find work
on your hook, YOU RUN IT."* The mechanism under it changed. The hook is a platform command that
hides the query, because a worker-composed `bd ready` misses pool wisps (the core pack's claim
protocol names a 41-hour miss, bead `ga-tmzjx6`).

## 4. "Zero roles" — what the slogan gets right

`config.Agent` (`internal/config/config.go`) has `Name`, `PromptTemplate`, `Provider`, `Scope`,
`StartCommand`, `MaxActiveSessions`, `ScaleCheck`. There is no `Role` enum. Tests that say
`"mayor"` or `"polecat"` are using those strings as fixture names. `coming-from-gastown.md` maps
every Gas Town role onto "a configured agent plus a prompt", and says the platform does not force
the crew/polecat distinction.

That claim is ✅ for the type system. A reviewer is a prompt. Adding a behaviour is a pack edit,
not a Go type.

## 5. "Zero roles" — what the binary still ships

The slogan fails if it is read as "the installed system contains no role-shaped defaults."

The `gc` binary embeds packs (`internal/builtinpacks.All`):

| Bundled pack | What it contributes |
|---|---|
| `core` | Skills, housekeeping **exec orders**, provider hook overlays, formulas including `mol-polecat-base` / `mol-polecat-commit` / `mol-polecat-report`, and the agent `control-dispatcher` |
| `bd`, `dolt` | Beads / Dolt provider packs |
| `gastown` | From the `gascity-packs` module, not a checked-in tree. City agents mayor, deacon, boot; rig agents witness, refinery, polecat. `examples/gastown/pack.toml` pins that import at `sha:33d3a430…` |
| `gascity` | Public-registry planning pack |

`control-dispatcher` is the important boundary case. Its `agent.toml` sets `prompt_mode = "none"`,
`process_names = ["gc"]`, `max_active_sessions = 1`, and a start command of
`gc convoy control --serve --follow …`. It is a configured session whose program is the
orchestrator, not an LLM playing a role. The formula spec's sentence "no agent participates in
control execution" means **no worker model executes control beads**. A `gc` process does, and
that process is adopted as a session so the reconciler can restart it.

Polecat-named formulas in the core pack are v1 workflow templates that kept the old name. They
are not a polecat type.

**Grade.** ✅ the orchestrator has no role enum. ✅ the Gastown roster is a pack, and the binary
embeds that pack. The absolute slogan "zero roles" is a description of the type system. Stated
as a description of the product, it is over-strong, and this file records it that way rather than
adopting it.

## 6. Identity is no longer a path

Gas Town derived a great deal from directory layout (`~/gt/mayor/`). Gas City's migration note
forbids porting that. `dir` is the identity scope. `work_dir` is a session working directory,
set only when the session must run somewhere else. A rig path is a machine-local binding in
`.gc/site.toml`, not a line in the shared `city.toml`.

The design rule in the glossary — *"Keep judgment out of Go. Go handles transport, not
reasoning."* — is the sentence the rest of this study tests. The control dispatcher is the place
it holds. The bundled Gastown pack is the place the judgment went.
