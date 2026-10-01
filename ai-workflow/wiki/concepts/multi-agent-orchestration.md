---
type: concept
status: active
last_ingested_from: gas-town/01-vocabulary.md + gas-town/02-architecture.md + gas-town/03-roles-and-lifecycle.md + gas-town/04-orchestration-techniques.md + gas-town/99-sources.md + gas-city/01-vocabulary.md + gas-city/02-architecture.md + gas-city/03-roles-and-lifecycle.md + gas-city/04-orchestration-techniques.md + gas-city/99-sources.md
related_pages: [concepts/control-plane-execution-plane, concepts/approval-gate, concepts/harness, concepts/agent-client-protocol, concepts/stateless-conversation-wire, concepts/primary-source-verification]
created: 2026-09-30
updated: 2026-09-30
---

# Multi-Agent Orchestration — driving many harness instances at once

- Purpose: the layer **above** a harness. The four other studies read one agent loop; this one is
  about scheduling, attributing and reconciling many of them.
- Scope: the container and role taxonomy, durable work state, identity and attribution, dispatch
  under a capacity cap, liveness, and the control/execution split when workers are untrusted
- Primary sources: `gastownhall/gastown` @ `649b832b76` (`v1.2.1-304-g649b832b`) and
  `gastownhall/gascity` @ `3ef7fadd42` (2026-09-30). Read from source and first-party design docs.
  **Not run** — no binary executed, so every mechanism here is source-read, never observed
- Updated: 2026-09-30 (Gas City ingest: platform extraction of the same axis)

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | Unit of analysis | the **fleet**, not the agent. The harness is a given; the problem is who assigns work and where state lives when a session dies |
| 2 | The load-bearing split | **persistent identity, ephemeral session** — a worker is a durable id plus a disposable workspace |
| 3 | Where work state lives | a **git-backed ledger** (Beads on Dolt), never in agent context |
| 4 | First-action rule | **propulsion / GUPP**: "if you find something on your hook, YOU RUN IT" — checked before asking anyone |
| 5 | Coordinator | **stateless.** The plan is the ledger; any worker re-derives it. The failure this avoids is called **hysteresis** — losing the thread at context compaction |
| 6 | NDI | **nondeterministic idempotence** — the path varies by worker, the criteria are fixed in the formula, the outcome converges |
| 7 | Merge safety | one serializer owns the queue; the lock is a **ledger item**, not a file lock |
| 8 | Liveness | **two independent channels.** Never escalate on one store; cross-check the second |
| 9 | Supervision | the watchdog has its own watchdog |
| 10 | Grades | source-read ✅ · self-described capability 📣 · **runtime unobserved ⚠️** |

## §2 Why this is a separate axis  {#s2-why-separate}

A harness answers *"how does one agent take a turn."* Orchestration answers *"how do I run thirty
of them without losing work, colliding, or trusting a stall."* The primitives that matter change
with the cardinality: at one agent, context is the memory; at thirty, **the ledger is the memory
and context is a cache**.

The failure that forces the change is not throughput — it is that a single coordinator's plan does
not survive compaction. Every orchestrator eventually meets this, and the durable-state answer
("write the plan down, make the coordinator replaceable") is the same move this repository already
makes once per session in `session_handoff.md`. **The handoff file is the single-worker case of the
fleet ledger.**

## §3 The five moves  {#s3-five-moves}

This is the reusable core — the minimum that makes the rest work.

1. **Externalize the plan.** Workflow state lives in a durable ledger, not in a coordinator. Any
   worker can pick it up cold; no one holds the thread.
2. **Split identity from session.** The identity (work history, capability record) outlives the
   session (workspace, process). Resume re-attaches to a deliberately-kept branch; completion
   retires the session and keeps the identity.
3. **Make the first action mandatory and observable.** A hook is a durable pinned work item; the
   startup contract is *check hook → work → execute*, and a supervisor that infers progress from
   silence will supervise a stall.
4. **Serialize the dangerous shared resource — and record the lock as work.** A merge queue with a
   single owner; the mutual exclusion is an auditable ledger item, so a crashed holder leaves a
   *visible* stale lock instead of an invisible one.
5. **Verify liveness on two channels.** Escalate only on their agreement; a stale signal that
   depends on a fallible delivery will lie, and the recovery it triggers can exceed the fault.

> 📌 **Moves 1 and 3 are a package.** An obligation to act is only enforceable if there is a
> durable thing to act on. Without the ledger there is no hook, and propulsion is a slogan.

## §4 Durable work state  {#s4-durable-state}

Two choices that generalise beyond any one tool:

- **Derive readiness, don't store it.** "Unblocked" is computed at read time by joining queued work
  against the dependency graph, not held in a field that a close event updates. A stored readiness
  is a cache of a graph property and goes stale the moment the graph changes.
- **Choose durability per workflow, not globally.** Cheap high-frequency runs stream their steps
  from the template; expensive rare runs materialise each step as a checkpoint that survives a
  crash. The heuristic worth keeping: *if you would curse losing the progress after a crash,
  checkpoint it* — and default to the cheap mode, justified by a measured row count rather than
  taste.

## §5 Identity is a storage property  {#s5-identity}

Attribution works when it is **structural, not conventional**. The pattern: an actor id that is
simultaneously the actor, the hierarchy key, and the address; plus a git commit shape that keeps
*who did it* and *who owns it* in separate fields (`GIT_AUTHOR_NAME` vs `GIT_AUTHOR_EMAIL`), so the
distinction survives in history forever.

The argument that sells this inside an organisation is compliance — "auditors ask who approved
this." The engineering win is quieter and larger: the format already requires the fields, so
attribution cannot be forgotten.

## §6 Supervision, and watching the watchers  {#s6-supervision}

- **Cross-scope vs within-scope are different jobs.** A coordinator that spans projects and a
  supervisor that watches one project's workers have different failure modes and get different
  agents.
- **The watchdog needs a watchdog.** A dedicated role exists whose only job is to confirm the
  watchdog is alive. Without it, "the fleet is healthy" is an unfalsifiable claim emitted by the
  exact component whose failure you are trying to catch.
- **Named failure states make a fleet legible.** Alongside working/idle/done, the useful states are
  *stalled* (should be working, stopped) and *zombie* (work done but could not stand down). A
  supervisor needs a decision procedure for each; a system that only models happy-path states
  will mishandle exactly the cases it is there for.

## §7 The plane split, sharpened  {#s7-plane-split}

[[concepts/control-plane-execution-plane]] draws the plane boundary from the browser studies and
from Strands, where the recorded conclusion is that a `Sandbox` abstraction "only decides *where*
it runs" and applies no policy on the plane it selects.

Orchestration contributes the sharper question. When a worker is moved somewhere untrusted, the
thing at risk is not only the filesystem — **it is the worker's ability to write its own results.**
An orchestrator's identity plus ledger-write access is enough to forge a completed task. So the
boundary is not *(planning | execution)* but:

> **(credential-bearing control | untrusted execution)**

The control channel — assign, report, update the ledger — stays reachable and credentialed; the
execution plane (inference, edits, `git`) goes where it is constrained. **A harness that sandboxes
files but leaves the result ledger writable has not separated the planes.** This connects three
previously separate findings: the Codex Windows sandbox mechanisms, Strands' `sandbox: host`
default, and the browser agents' credential-shielding axis.

## §8 What this does *not* establish  {#s8-limits}

Recorded because a graded concept page has to carry its own negative findings.

- **It does not weaken the approval gate.** This orchestration model is largely *post-hoc* — a
  witness verifies, a refinery gates the merge — and relocates trust from prevention to detection.
  That is a different trust model, not evidence that pre-execution gates
  ([[concepts/approval-gate]]) are unnecessary. Treat it as a contrast.
- **It does not settle providers-as-data across a wire.** Config-as-data inside one installed
  system is well supported; the shared-wire premise that [[concepts/agent-client-protocol]] and the
  Codex catalog work depend on is a separate claim with its own qualifier.
- **Its scale and cost figures are self-reported.** "20–30 agents", "$100/hour" and "Kubernetes for
  agents" are the project's and its community's claims, not measurements. No number from this page
  should be cited as a benchmark.
- **Nothing here was executed.** Mechanisms are source-read. Design-vs-implementation drift is
  always possible, and this repository's own record says so repeatedly.

## §9 Read next  {#s9-next}

- Operating model: [`gas-town/`](../../../gas-town/01-vocabulary.md) —
  [vocabulary](../../../gas-town/01-vocabulary.md) ·
  [architecture](../../../gas-town/02-architecture.md) ·
  [roles & lifecycle](../../../gas-town/03-roles-and-lifecycle.md) ·
  [techniques & cross-mapping](../../../gas-town/04-orchestration-techniques.md) ·
  [sources](../../../gas-town/99-sources.md)
- Platform extraction: [`gas-city/`](../../../gas-city/01-vocabulary.md) —
  [vocabulary](../../../gas-city/01-vocabulary.md) ·
  [architecture](../../../gas-city/02-architecture.md) ·
  [roles & lifecycle](../../../gas-city/03-roles-and-lifecycle.md) ·
  [techniques](../../../gas-city/04-orchestration-techniques.md) ·
  [sources](../../../gas-city/99-sources.md)
- Method that produced it: [[concepts/primary-source-verification]] — the same false-positive
  discipline appears here as the two-channel liveness rule, and again as Gas City's
  `ObservationIncomplete`.
- The synthesis it feeds: [`SYNTHESIS.md`](../../../../SYNTHESIS.md) §2.4 (planes), §2.7 (gates),
  §6.5–6.7 (context drift and lying checks), §7 (method).

## §10 The platform extraction  {#s10-gas-city}

Gas Town (§1–§8) is one operating model with named roles. Gas City is that machinery pulled into
a toolkit. Two grades, both source-read at `3ef7fadd42`, neither executed:

| Claim | Grade |
|---|---|
| `config.Agent` has no role enum. A reviewer is a prompt | ✅ |
| The `gc` binary embeds the Gastown pack (mayor, deacon, witness, refinery, polecat) and polecat-named formulas | ✅ — "zero roles" is the type system, not the product |
| v2 formulas (default **on**) split control beads from work beads. `ProcessControl` switches on eight `gc.kind` values | ✅ |
| The process that runs control is a reconciled session, `control-dispatcher`, whose command is `gc convoy control --serve` | ✅ — "no agent" means no model |
| One Dolt server per city; rigs isolate by `issue_prefix`. The April 2026 glossary's "own database per rig" is stale | ✅ |
| `ObservationIncomplete` must not be read as absence. ACP and subprocess seams used to drop that third outcome | ✅ |
| Workers must `gc hook --claim` because `bd ready` hides wisps (`ga-tmzjx6`) | ✅ first-party prompt + code comment |
| ACP `Pending`/`Respond` return `ErrInteractionUnsupported`. The permission conformance test expects no client reply and a rejected tool | ✅ |
| City-write grants (ed25519, single-use, request-bound) authorize **config** mutations. They do not close ledger writes | ✅ — does not replace §7 |

The five moves in §3 still stand. Gas City adds five that sit on top of them: judgment in the
pack and control-flow in the bead kind; incomplete as a liveness result; one claim command;
prefix isolation as a client filter rather than a trust boundary; three doors (config, ledger,
session sidecar) and a grant on only one of them.

Full record: [`gas-city/04`](../../../gas-city/04-orchestration-techniques.md).
