# 02. Gas City — architecture and composition

> Read from `gastownhall/gascity` @ `3ef7fadd42`. Where an architecture note and the code
> disagree, the code is the grade and the note is the drift.

## 1. What a city is on disk

A city is a directory.

| Path | Holds |
|---|---|
| `city.toml` | Deployment: workspace defaults, rigs, daemon, provider, scale. The shared declaration |
| `pack.toml` | This city's behaviour: imports and local agents, formulas, orders |
| `.gc/` | Runtime state, including machine-local rig path bindings (`.gc/site.toml`) |
| `.beads/` | This scope's bead config: `issue_prefix`, and who owns the Dolt endpoint |
| `agents/<name>/` | A local agent definition (`agent.toml` + prompt). Not a role home |

`gc rig add` writes the rig's name into `city.toml` and the path into `.gc/site.toml`. The
tutorial prints "Initialized beads database". That line means a `.beads/` directory was created.
It does not mean a second Dolt server.

## 2. One server, prefix isolation, and a class seam

Two facts are both true, and the older glossary collapses them.

**Scopes share a server.** `docs/reference/internal/beads-topology.md`, checked against
`internal/beads/contract/files.go`:

- One Dolt sql-server per city. The port is `.beads/dolt-server.port` at the city root.
- Each scope has an `issue_prefix` (`mc`, `riga`, …). `bd` filters every read and write to that
  prefix. From rig A, rig B's bead id is "not found" even though the row is on the same server.
- `gc.endpoint_origin` is `managed_city` at the city and `inherited_city` at a default rig. Rigs
  do not run Dolt. `gc bd --rig <name>` is "cd and run `bd`", not a federation join.

The April 2026 glossary line "each rig gets its own beads database" is **stale**. The on-disk
`.beads/` directory is per scope. The server is not.

**Classes are a typed seam, and they may be separate stores.** `internal/beads/class_store.go`
defines `WorkStore`, `GraphStore`, `SessionStore`, `MailStore`, `OrdersStore`, `NudgesStore`.
Each embeds `Store`. The wrapper does not open a new backend by itself — it exists so a function
that wants graph beads cannot be handed the mail store at compile time. Call sites may still open
**different** underlying stores per class. `dispatch.ProcessOptions.MemberStores` exists because
a drain's control bead can live in the graph store while the convoy members it expands live in
the work store. `ResolveStoreRef` closes a source bead in another store when a workflow
finalizes (`gc.source_store_ref`).

So the durable-state claim is narrower than "one database for everything":

> Default topology: **one Dolt server, hard prefix filters per rig.** Class split: **a compile-time
> seam that is allowed to be more than one store**, with explicit cross-store refs when a graph
> and its work do not share a backend.

`bd` remains the production beads backend (Dolt underneath). `GC_BEADS=file` or
`[beads] provider = "file"` is the file store, which the formula architecture note limits to
tests and tutorials for full formula execution. Exec providers exist for beads, mail, and events:
a user script, trusted as operator code (`docs/reference/trust-boundaries.md`).

## 3. Two formula contracts, both live

`docs/reference/specs/formula-spec-v2.md` (last verified 2026-06-12 in-repo; the implementation
was re-read at this commit) and `internal/config.DaemonConfig.FormulaV2Enabled`:

| | v1 | v2 |
|---|---|---|
| Opt-in | Default shape when no requirement is declared | `[requires] formula_compiler = ">=2.0.0"`. Deprecated alias `contract = "graph.v2"` |
| Host default | — | **Enabled.** `FormulaV2 == nil` means on. Only an explicit `formula_v2 = false` (or the deprecated `graph_workflows = false`) turns it off |
| Materialized shape | Parent-child molecule under a `molecule` root. Conditions resolve at cook time; afterwards the tree is inert | Flat graph: workflow root (`gc.kind = workflow`) + step beads linked by blocking deps + control beads |
| Who advances it | The agent the molecule was slung to | `ProcessControl` executes every control bead. Agents execute only plain work beads |
| `gc converge` | Accepted | Rejected until it has an explicit input convoy (formula guide; issue tracked in the spec) |

`ProcessControl` (`internal/dispatch/runtime.go`) switches on `gc.kind` and hard-errors on an
unknown kind. The set is `internal/beadmeta.ControlKinds`, lockstep-tested against the switch:

`retry`, `ralph`, `check`, `retry-eval`, `fanout`, `drain`, `scope-check`, `workflow-finalize`.

A control bead that is not `open` is skipped with a trace line. The comment records why: a worker
that ran `bd update --status in_progress` on a control bead stranded a workflow for 20 minutes
because the serve loop treated the skip as a successful cycle (`ga-ttn5z` / `ga-fw2fm`). Control
beads are orchestrator state. A worker writing them is a bug, and the code treats it as one.

The spec sentence "no agent participates in control execution" is ✅ as a statement about **work
agents**. The process that runs `ProcessControl` is the core pack's `control-dispatcher` session:
`gc convoy control --serve` ([`01`](01-vocabulary.md) §5). Routing stamps
`gc.routed_to=<rig>/core.control-dispatcher`. Control is outside the *model* session. It is not
outside the *process* model — the reconciler can restart it, which is the point.

v1 and v2 are peers. The in-repo `engdocs/architecture/formulas.md` (verified 2026-03-17) still
describes only the `bd mol wisp` path and a deferred rename (`#586`). That note is behind the
spec and behind `internal/formula` / `internal/dispatch`. Do not cite it as current.

## 4. The controller tick

Health patrol is not a package. `engdocs/architecture/health-patrol.md` (verified 2026-05-29)
describes the loop in `cmd/gc/controller.go`, and the part that has drifted is labelled in the
doc itself: **the tick no longer dispatches orders inline.** It wakes an orders lane
(`cmd/gc/orders_lane.go`) that runs dispatch on its own goroutine.

One tick, as that note describes it:

1. Reload `city.toml` if the config watch marked it dirty.
2. Rebuild the desired agent set, including pool `scale_check` commands.
3. `reconcileSessionBeads` — start missing, drain or close undesired, restart on config-fingerprint drift, honour crash quarantine and idle timeout.
4. Wisp GC.
5. Wake the orders lane.

Crash-loop quarantine is in-memory on purpose (lost when the controller restarts, Erlang-style).
`session.quarantined` is a registered event type with **no production emitter**. Subscribing to it
will not observe the transition. Suspension is derived from workspace, rig, and agent flags, not
from the reserved `session.suspended` event, which also has no production emitter. Those two
reserved-but-unemitted events are ✅ gaps, not documentation lag I failed to check.

Desired-vs-running is the Kubernetes-shaped part, and it is narrow: child spec in, reconcile
out, restart with backoff. It is not a claim that the rest of the system is Kubernetes.

## 5. Session providers

`runtime.Provider` (`internal/runtime/runtime.go`) is the seam: `Start`, `Stop`, `Interrupt`,
`IsRunning`, `ProcessAlive`, `Nudge`, `Attach`, metadata. `IsRunning` is explicitly **not** proof
the agent process is alive. Implementations named by the README and the runtime tree: tmux
(default and required fallback), subprocess, exec, ACP, Kubernetes, herdr, hybrid, plus `Fake`
for tests.

tmux stays a prerequisite even when another backend is selected. That is an install fact in the
README, not a measured requirement from this study.

ACP is a **session transport** here (`agent.session = "acp"`), speaking JSON-RPC over stdio. It
is the same protocol this repository studies in [`agent-ux/10`](../agent-ux/10-acp.md). What Gas
City does with the permission method is in [`03`](03-roles-and-lifecycle.md) §5, not here.

## 6. Trust is split by input class, not by folder

`docs/reference/trust-boundaries.md`, consistent with the code comments it describes:

| Input | Grade the project assigns |
|---|---|
| `city.toml`, local site config, imported packs, agent `command`, exec-provider scripts | **Trusted operator code.** Review them as shell |
| Bead titles, descriptions, mail, formula vars, PR text, API fields | **Untrusted data.** Do not concatenate into shell. Pass as env, JSON, stdin, or argv |
| Ambient environment | Untrusted for secret propagation. Orchestrator-side helpers strip keys whose names contain `TOKEN`, `PASSWORD`, `SECRET`, `PRIVATE_KEY`, `API_KEY`, `ACCESS_KEY`, `CREDENTIAL`, `OAUTH`, `AUTH_JSON` |

An explicit config value is kept, because it is an operator decision. Failure logs redact known
secret values. This is a **command-injection and secret-propagation** boundary. It is not the
ledger-forgery boundary from [`gas-town/02`](../gas-town/02-architecture.md).

### 6.1 City-write grants are a third credential

`internal/citywriteauth` verifies single-use, request-bound grants for **city configuration
mutations**. An external authority mints them with an ed25519 private key. The supervisor only
verifies. The token binds `kid`, audience, city name, optional tenant id, epoch, `iat`/`exp`, a
single-use `jti`, and a digest of method + path + query + body. When a verifying key is
configured, a missing or bad `X-GC-City-Write` header fails closed. With no key, the middleware
is not installed.

The package ships no minter. The bundled API client and dashboard send only a CSRF header, so
turning the gate on **rejects those first-party clients**. That is an intentional split: the
writer of city config is not the process that serves the dashboard.

This does not answer "can a worker close its own task bead?". It answers "can a captured request
mutate `city.toml`'s API twin?". Different credential, different surface. The Gas Town finding
stands.

### 6.2 A sidecar that can impersonate a session

ACP `SetMeta` stores session identity and drain state in an owner-only sidecar. The comment in
`internal/runtime/acp/acp.go` states the threat directly: a reader can impersonate the session,
and a writer can forge a drain acknowledgement. The directory is re-checked on every write.
Source-read ✅ as a threat the code acknowledges. Not observed at runtime ⚠️.

## 7. What is infrastructure, stated as a rule

`coming-from-gastown.md` is explicit, and the code matches it: reconciling sessions, scaling
pools, evaluating orders, health patrol, and wisp GC belong to the orchestrator. A witness-shaped
agent on top of those mechanisms is optional pack behaviour. An exec order is preferred to a new
"dog" whenever the work is a shell command.

That rule is the architectural content of "zero roles". The bundled Gastown pack is a choice to
put the old names back on, not a type the rule failed to delete.
