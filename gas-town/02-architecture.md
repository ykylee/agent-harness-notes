# 02. Gas Town — architecture and composition

> Read from `gastownhall/gastown` @ `649b832b76` (`v1.2.1-304-g649b832b`). `docs/design/architecture.md`,
> `internal/`, plus the sandbox and scheduler design docs. MIT.

## 1. The storage answer, first

Before the agent architecture, the substrate — because *this* is the part that answers a question
the other studies in this repository keep circling.

**Beads** is a git-backed issue tracker. Gas Town's database engine is **Dolt** (git-versioned
SQL), one database per rig plus one for the town, living under `~/gt/.dolt-data/`. The property
that matters for orchestration is not "it's a database" — it is that **the ledger is itself
versioned, diffable and branchable**, and every clone of a repo shares the same durable work
state. An agent's assignment does not live in the agent.

The beads layer is split in two, mirroring the org split:

| Level | Location | Prefix | Holds |
|---|---|---|---|
| **Town** | `~/gt/.beads/` | `hq-*` | cross-rig coordination, mayor mail, convoys, town agent beads, role templates |
| **Rig** | `<rig>/mayor/rig/.beads/` | project prefix | issues, MRs, project molecules, rig agent beads |

The split is not cosmetic. An epic that spans projects is town-level because *the thing being
tracked crosses a boundary that no single rig owns.*

## 2. Directory layout — the composition

```
~/gt/                              Town root
├── .beads/                        Town beads (hq-*) + routes.jsonl (prefix → rig)
├── .dolt-data/                    Dolt databases, one per rig + hq
├── daemon/                        Go daemon runtime (dolt server, pid, state)
├── deacon/                        Deacon workspace; dogs/ live here
├── mayor/                         Mayor home
│   ├── town.json  rigs.json  daemon.json  accounts.json
├── settings/                      config.json (agents, themes) + escalation.json (routes)
├── directives/<role>.md           **operator policy, injected at prime time**
├── formula-overlays/<f>.toml      per-formula step overrides (replace/append/skip)
└── <rig>/                         Project container — NOT a clone
    ├── mayor/rig/                 the canonical clone (beads live here)
    ├── refinery/rig/              refinery worktree off mayor/rig
    ├── witness/                   no clone
    ├── crew/<name>/               human workspace, full clone
    └── polecats/<name>/<rig>/     worker worktrees off mayor/rig
```

Three things in that tree are worth pausing on:

1. **The rig is not a clone; `mayor/rig/` inside it is.** Every agent workspace is a worktree off
   one canonical clone. Spawn cost is a worktree, not a clone.
2. **`directives/<role>.md` is operator policy, injected at prime time.** The role definition is a
   document, not code — the operator can rewrite what a Witness *is* without recompiling. (Role
   beads are the equivalent in the ledger, referenced by a `role_bead` field.)
3. **Formula overlays are a per-rig override layer for workflows** — the same layering idea as
   `property-layers.md` applied to process rather than config.

## 3. Persistent configuration layers

`docs/design/property-layers.md` defines a four-layer lookup where earlier wins:

```
1. WISP     <rig>/.beads-wisp/config/   transient, never synced   — local override
2. RIG BEAD <rig>/.beads/               git-synced, all clones   — project state
3. TOWN     ~/gt/config.json            per-town                  — policy
4. SYSTEM   compiled-in                 — fallback
```

Note the special value **`Blocked`** in layer 1: a wisp can set a property to *explicitly nothing*,
which is different from "unset" and stops the lookup. That is a real distinction — "override to
'no value'" is a thing operators need, and most layered-config systems conflate it with absence.

## 4. How a worker is actually spawned

`internal/polecat/manager.go` is the answer, and it is ordinary git plumbing:

- `WorktreeAddFromRef(clonePath, branchName, startPoint)` for a fresh worker
  (branch `polecat/<name>-<timestamp>`), and
- `WorktreeAddExistingForce(clonePath, resumeBranch)` when a **named branch already exists** —
  the resume path for a crashed or handed-off session.

So an ephemeral session is a *worktree + branch + tmux pane*, and resuming one is *re-attaching to
a branch that was deliberately kept*. The identity (the agent bead, the CV, the work history)
never lived in the worktree. That is the whole design in one function pair.

The manager also has `reclaim.go` and `reuse.go` — after `gt done`, the worktree is reclaimed and
the identity kept. **Cattle, not pets** for the session; pets for the identity.

## 5. The control / execution plane split

`docs/design/sandboxed-polecat-execution.md` (status: **Proposal**, 2026-03-02) is the most
forward-looking document in the repo, and it is the one that speaks this repository's language
directly. The problem it states:

> Every polecat today runs on the host under the user's UID, with full filesystem, network and
> credential access. A manipulated agent can read outside its worktree, write `~/.ssh`, call
> `gt`/`bd` with a **fabricated identity**, or exfiltrate credentials.

Note the threat model: **identity forgery and credential theft by a subverted agent**, not just
"the agent might do something unauthorized." The fix is to keep two planes apart:

| Plane | What runs | Where it must run |
|---|---|---|
| **Execution** | inference, file edits, `git`, code | in the sandbox/container — needs the worktree |
| **Control** | `gt prime/done/mail`, `bd show/update`, events, nudges | back on the host — needs Dolt, `.runtime/`, mail |

The control plane keeps the agent's *identity and ledger access*; the execution plane gets the
*code*. A sandboxed worker can still be told what to do and still report what it did, without
holding the credentials that would let it rewrite its own work history.

This is the design answer to a problem this repository has documented from the other side: Codex
mitigates it with `hide_users.rs` / Seatbelt / restricted tokens; Strands defaults to
`sandbox: host`. Gas Town's contribution is the observation that **the orchestration identity is
itself a credential** — `BD_ACTOR` plus mail access is enough to forge a completed task — so the
plane split has to include the control channel, not just the filesystem.

## 6. The dispatcher — capacity as a first-class control

`docs/design/scheduler.md`. Without a scheduler, slinging N beads spawns N polecats at once and
blows through rate limits and RAM. The scheduler is a governor:

- `scheduler.max_polecats` selects mode: `-1`/`0` = dispatch immediately, `N>0` = **defer**.
- `gt sling` is unchanged either way — the same command *adapts* to the config. No per-call flag.
- On the daemon heartbeat (every 3 min) as **step 14, after all health checks** — the system
  dispatches only once it is healthy enough to receive workers.
- Under `flock`, it counts active polecats (via tmux), joins queued sling-context beads with
  `bd ready` to find unblocked work, then runs a plan→execute→report dispatch cycle.

Two details are the real content:

- **"Ready" is derived by joining the queue against `bd ready`, not stored.** Unblocked-ness is a
  property of the dependency graph at read time. This is the "discover, don't track" principle
  applied to scheduling.
- **Dispatch is a heartbeat step, after recovery.** Health and cleanup run first. An orchestrator
  that spawns work before it has checked whether its existing workers are stuck will amplify a
  fault into a pile-up.

## 7. Supervision numbers

From `internal/deacon/`:

| Constant | Value | Meaning |
|---|---|---|
| `HeartbeatStaleThreshold` | 5 min | heartbeat aged past → "stale" |
| `HeartbeatVeryStaleThreshold` | 20 min | → "very stale" → poke/escalate |
| `DefaultRedispatchCooldown` | 5 min | after a re-dispatch, before trying again |

And the rule that makes the heartbeat trustworthy — `docs/concepts/heartbeats.md` documents **three
separate heartbeat stores** (a deacon file, a per-session store, and a label on the agent bead),
each with different readers, and warns:

> Never declare an agent stuck from a single store. A live session with a stale store is
> *heartbeat-write divergence*, not a stuck agent.

The false-positive lesson is the valuable part: **a liveness signal that is itself subject to
delivery failure will eventually lie, and the recovery action triggered by that lie can be worse
than the fault it was watching for.** Cross-check an independent channel (tmux activity) before
escalating.

## 8. Merge serialization — a lock that is a work item

`internal/beads/beads_merge_slot.go`. The Refinery's merge queue needs mutual exclusion, and the
implementation is unusual: **the lock is a bead** — a single issue labelled `gt:merge-slot` whose
`Description` field holds JSON `{holder, acquired_at}`. Not a file lock, not a mutex: a
durable, inspectable, git-versioned work item.

That choice buys three things a `flock` cannot: the holder is **auditable in the same ledger as the
work** ("who has held the merge slot for 40 minutes?" is a query), a crashed holder leaves a
**visible stale lock** rather than an invisible kernel lock, and it survives across machines
because it is in git. The cost is that correctness now depends on bead updates being atomic.

The scheduler's `flock` and this bead-based slot are a useful contrast: **use a file lock for
"do not do this twice on this machine", and a ledger item for "this resource is owned, and the
ownership is part of the system's story."**

## Read next

- [`03-roles-and-lifecycle.md`](03-roles-and-lifecycle.md) — the supervision tree, the mail
  protocol, and the failure-recovery path.
- [`04-orchestration-techniques.md`](04-orchestration-techniques.md) — what to reuse, cross-checked
  against this repository's other studies.
- [`99-sources.md`](99-sources.md) — verification status.
