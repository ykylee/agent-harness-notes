# 04. Gas Town — orchestration techniques, and where they meet this repository

> The purpose of this file is the user's stated one: **a reference for orchestration technique.**
> It separates (a) what Gas Town does that is worth reusing, (b) how that lines up with what the
> Codex / Strands / ACP / browser studies already found here, and (c) what Gas Town does that
> *this repository's evidence does not support*.
>
> Read from `gastownhall/gastown` @ `649b832b76`. Cross-references are to this repository's own
> graded findings, not to opinion.

---

## Part A — Techniques worth taking

Each entry: the technique, where it comes from in Gas Town, why it is transferable, and the
caveat. Ordered by how much I would actually reuse them.

### A1. Externalize the plan so the coordinator is replaceable

**The technique.** The coordinating agent holds no state. The workflow *is* the ledger; each check
re-derives state fresh; any worker can make the same judgement from the same artifacts
(`docs/design/convoy/mountain-eater.md`, the "No agent holds the thread" principle).

**Why it transfers.** This is the single most transferable idea in the repo, because it is the
orchestration-layer answer to a problem this repository has hit repeatedly **inside** a single
harness: an agent's plan does not survive context compaction, so a re-primed agent with the same
task re-derives a different plan. Gas Town's response is to make the plan an artifact no agent
owns.

**Caveat.** It trades a cheap in-context loop for ledger reads. That is the right trade at 20+
agents and probably the wrong one at 2. The Mountain-Eater doc is explicit that the mechanical
convoy feed was *already working* — the judgment layer exists because a purely mechanical feeder
re-slings a failing issue forever.

### A2. Persistent identity, ephemeral session

**The technique.** A worker = durable identity (agent bead, work history, CV) + disposable session
(worktree, branch, tmux pane). Resume is re-attaching to a deliberately-kept branch; completion
retires the session and keeps the identity (`docs/concepts/polecat-lifecycle.md`,
`internal/polecat/{manager,reclaim,reuse}.go`).

**Why it transfers.** It answers "the agent died, now what" without a state-migration problem,
because there is no session state to migrate. It also composes with A1: replaceable sessions are
what make a replaceable coordinator possible.

**Caveat.** Retiring rather than pooling idle sessions is a real design decision with a real cost
— you pay a spawn per task. Gas Town's own reasoning is that pooled sessions accumulated state;
your workload may not.

### A3. A dedicated merge serializer, and a lock that is a work item

**The technique.** N writers never merge concurrently; a single Refinery owns the queue. The
mutual exclusion is a **bead** labelled `gt:merge-slot` whose description holds the holder, not
a `flock` (`internal/beads/beads_merge_slot.go`).

**Why it transfers.** Strongly. The bead-as-lock buys auditability ("who has held the merge slot
for 40 minutes?" is a query, not a log dive), leaves a *visible* stale lock when a holder crashes
rather than an invisible kernel lock, and works across machines because it is in git.

**Caveat / contrast.** Atomicity now depends on bead update being atomic, which is a storage-layer
property you do not get for free. Gas Town uses `flock` for the *scheduler* (a
"do not do this twice on this machine" concern) and a bead for the *merge slot* (an "owned
resource whose ownership is part of the system's story" concern). That distinction is worth
copying verbatim: **file lock for local idempotence, ledger item for shared resource ownership.**

### A4. Propulsion: make the first action non-negotiable

**The technique.** "If you find something on your hook, YOU RUN IT." No supervisor polling
"did you start?"; the hook is the assignment and the agent is obligated to check it at startup,
before asking anyone (`docs/concepts/propulsion-principle.md`).

**Why it transfers.** The named failure mode is the useful part:

```
Polecat restarts → announces itself → waits for confirmation
  → Witness assumes progress → nothing happens → fleet stops
```

**A supervisor that infers progress from silence will happily supervise a stall.** That is a
statement about the supervisor's inference, not about the worker's politeness, and it generalizes
to any fleet.

**Caveat.** This works because a durable hook exists to be checked. Without A1's externalized
state there is nothing on the hook, and the rule is unenforceable. The two are a package.

### A5. Liveness needs two independent channels

**The technique.** Three separate heartbeat stores with different readers, an explicit rule never
to declare an agent stuck from one of them, and a cross-check against tmux activity before
escalating (`docs/concepts/heartbeats.md`). Thresholds are concrete: 5 min stale, 20 min
very-stale, 5 min re-dispatch cooldown (`internal/deacon/`).

**Why it transfers.** This is the orchestration-layer instance of a pattern this repository has
already documented four times: **a signal that depends on a delivery that can itself fail will
lie, and the recovery it triggers can be worse than the fault** ([`SYNTHESIS.md` §7](../SYNTHESIS.md);
the false "0"s in §6.6). Heartbeats are just the liveness-shaped instance of it.

**Caveat.** The gotcha is documented honestly: a session that never reaches `await-signal` leaves
the bead label stale for hours while the agent is fine. There is no fix here, only a documented
tolerance — which is arguably the correct engineering answer for a signal you cannot make
reliable.

### A6. Watch the watchers

**The technique.** Boot is a Dog whose only job is to check that the Deacon (the watchdog) is
alive, on a ~5 min cadence. The witness watches the Deacon's bead; the Mayor escalates if the
witness does.

**Why it transfers.** Any orchestrator that monitors workers eventually needs something that
monitors the monitor. Without it, "the fleet is healthy" is an unfalsifiable claim produced by the
same component whose failure you are trying to detect.

### A7. Derive readiness, don't store it

**The technique.** "Unblocked" is computed at read time by joining queued sling-context beads
against `bd ready`; it is not a field that gets updated (`docs/design/scheduler.md`).

**Why it transfers.** Stored readiness is a cache of a graph property, and it goes stale the
moment the graph changes. Joining at read time trades a query for the elimination of a whole bug
class. The doc names the principle — *discover, don't track*.

### A8. Dispatch after health, not before

**The technique.** The scheduler runs as **step 14** of the daemon heartbeat, after all health
checks, agent recovery and cleanup. It also counts live polecats (via tmux) against a config cap
before spawning.

**Why it transfers.** Obvious in hindsight and easy to get wrong: an orchestrator that spawns work
before checking whether its existing workers are stuck converts one fault into a pile-up. Capacity
(`scheduler.max_polecats`) also flips dispatch mode *without changing the command* — the same
`gt sling` adapts, so there is no per-call flag to get wrong.

### A9. Choose durability per workflow, not globally

**The technique.** Formula steps stream inline from the template (root-only wisp, ~400 rows/day)
or materialize as checkpointed sub-wisps (`pour = true`, for expensive runs whose loss would hurt).
Heuristic: *"if you would curse losing the progress after a crash, set `pour = true`."*

**Why it transfers.** The trade is real and the default is the cheap one, justified by a measured
number rather than taste. Most systems pick one globally and regret it.

### A10. Attribution as a storage-format property

**The technique.** `BD_ACTOR` is a slash-path (`gastown/polecats/toast`) that is simultaneously
the actor id, the hierarchical parse key, and the mail address. Git commits carry
`GIT_AUTHOR_NAME = <agent>` and `GIT_AUTHOR_EMAIL = <owner>`, so history separates *who did it*
from *who owns it*, permanently.

**Why it transfers.** The compliance argument is the one that sells it internally ("auditors ask
who approved this code"), but the engineering win is that attribution is **structural, not a
convention** — the format already requires both fields, so it cannot be forgotten.

### A11. The orchestration identity is itself a credential

**The technique.** Gas Town's own sandbox proposal names the threat: a subverted agent can "call
`gt`/`bd` with a **fabricated identity**" and write its own work history. The fix is to split the
planes so the **control channel** (`gt`/`bd`, mail, events) stays with the host while the
**execution plane** (inference, edits, `git`) goes in the sandbox
(`docs/design/sandboxed-polecat-execution.md`, status: Proposal).

**Why it transfers.** This is the sharpest idea in the repo for anyone building on this
repository's axes, and it connects three previously separate findings — see Part B.

---

## Part B — Where Gas Town meets this repository's other studies

Gas Town is not a fourth subject. It is a test of axes the other four studies already established.

### B1. It confirms §2.4 control/execution plane — and adds a credential dimension

[`SYNTHESIS.md` §2.4](../SYNTHESIS.md) draws the plane split from the browser studies (Comet
server-side vs Aside/Dia local) and from Strands, where the split is "inside the library" as a
`Sandbox` object with three implementations. The recorded conclusion is sharp:

> Strands' `Sandbox` only decides **where** it runs. … What it does *not* do is apply a policy on
> the plane it selects.

Gas Town's sandbox proposal is the same axis with a different emphasis: it does not primarily ask
*where should execution run* but *what must stay reachable when it runs somewhere untrusted* — and
its answer includes the **control channel itself**, because a worker with `BD_ACTOR` + mail + `bd`
access can forge its own results. So the plane boundary is not (planning | execution) but
**(credential-bearing control | untrusted execution)**.

That is a genuine sharpening of the axis, not a restatement: it says the plane split must be drawn
*around the credentials*, and a harness that sandboxes the filesystem but leaves the ledger
writable has not actually separated the planes.

### B2. It is the fleet-scale version of the context-drift finding

[`SYNTHESIS.md` §6.5–6.7](../SYNTHESIS.md) and §7 record that a model's behaviour changes with
context pressure, and this repository's own `session_handoff.md` discipline exists because
in-context state does not survive compaction. The Mountain-Eater names the orchestration-level
instance exactly — **hysteresis**: an agent "driving an epic" loses the thread at compaction, and
re-priming does not restore it *even with the task still assigned*.

This repository solved that one session at a time (write the state to a handoff file, regenerate
`state.json`). Gas Town's answer is the same move at fleet scale: write the state to a ledger and
make the coordinator stateless. **The two are the same technique at different cardinalities** —
which is a reason to trust it, and also a reason to notice that the handoff-file approach is the
degenerate single-worker case of it.

### B3. Approval: Gas Town mostly *sidesteps* the axis rather than solving it

This repository's `approval-gate` concept is one of its load-bearing pages, and Strands is the
instructive counterexample (approval default **off**, Cedar fail-open, no hard deny). Gas Town's
supervision tree is a **post-hoc** control model — Witness verifies, Refinery gates the merge,
dogs clean up — rather than a pre-execution gate. Nothing in `gt sling` asks a human.

The honest reading: Gas Town does **not** contribute evidence to the approval axis. It relocates
trust from "the worker decides correctly" to "the merge serializer and the witness catch it
later," which is a *different* trust model (detection over prevention). For a research repo whose
thesis is that gates are load-bearing primitives, that is a genuine and interesting **contrast**,
not a confirmation — and it should not be read as a data point that gates are unnecessary.

### B4. Provider/config as data (A7, A9) vs. this repository's §2.3

`SYNTHESIS.md` §2.3 records providers-as-data as an axis, with an important qualifier: it holds
**only under a shared-wire premise**. Gas Town's property layers and formula overlays are the same
instinct (operators redefine a Witness or a release workflow as a document, not a recompile), but
they configure *a single installed system* rather than describing *the wire between two
independently-versioned systems*. The Codex `model_catalog_in_context` drift finding is the
provider-data case: model listings moving from a tool description into a developer
`<model_catalog>` message.

So: **config-as-data is well supported; provider-as-data across a wire remains qualified.** Do not
let Gas Town's configurability be read as evidence that the wire case is settled.

### B5. The false-positive discipline is the same discipline

The three-heartbeat rule (A5) and this repository's §6.6 "two green checks that were lying" are
the same failure mode: a monitor that reports health it has not actually verified. The difference
is that Gas Town's answer is structural (three stores, cross-check before escalating) where this
repository's answer has been methodological (print what actually arrived; a 0 is only evidence if
delivery is proven). **Both should be applied together** — a fleet that only has the methodology
will still mis-escalate, and a study that only has the structure will not notice.

---

## Part C — What Gas Town does that this repository's evidence does **not** support

Recording this is the point of a graded study. Three items:

1. **"Kubernetes for AI agents" is 📣 marketing.** The defensible comparison is narrow: both
   reconcile a fleet against a durable source of truth; k8s asks *is it running?*, Gas Town asks
   *is it done?* — a control-loop vs. completion-reconciliation difference. The analogy does not
   survive contact with the implementation details (a `flock` is not a lease API, a merge slot is
   not a ConfigMap).
2. **The self-reported economics are unverified.** Operators report ~$100/hour at 12–30 agents and
   describe the work as chaotic at that scale. These are anecdotes from the project's own
   community, **not measurements I made**, and no cost figure here should be cited as a benchmark.
3. **Nothing here is a recommendation to adopt the tool.** The operational surface is large (Go
   binary, a Dolt SQL server, tmux, a worktree per worker, a ledger per rig). A team that wants the
   *techniques* (A1–A11) can adopt them inside an existing harness; adopting the whole system is a
   different, much larger decision that this study does not make.

---

## A compact card

If you only keep one thing, keep this. Gas Town's orchestration rests on five moves:

1. **Put the plan in a ledger, not in a coordinator** — so any worker can pick it up cold (A1).
2. **Split identity from session** — a worker is a durable id plus a disposable workspace (A2).
3. **Make the first action mandatory and observable** — the hook, checked before anything else (A4).
4. **Serialize the dangerous shared resource, and record the lock as a work item** (A3).
5. **Verify liveness on two channels, and escalate only on their agreement** (A5, A6).

Points 1 and 3 are a package: an obligation to act is only enforceable if there is a durable thing
to act on. Points 4 and 5 are the same discipline applied to resources and to monitors.

---

## Read next

- [`01-vocabulary.md`](01-vocabulary.md) · [`02-architecture.md`](02-architecture.md) ·
  [`03-roles-and-lifecycle.md`](03-roles-and-lifecycle.md) · [`99-sources.md`](99-sources.md)
- The concepts this adds to the shared layer:
  [`multi-agent-orchestration.md`](../ai-workflow/wiki/concepts/multi-agent-orchestration.md)
- The cross-study synthesis: [`SYNTHESIS.md`](../SYNTHESIS.md) §2.4 (planes), §2.7 (gates),
  §6.5–6.7 (context drift, false checks), §7 (method).
