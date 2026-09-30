# Gas Town — orchestration above the harness

> **What this is.** A study of [Gas Town](https://github.com/gastownhall/gastown) (Steve Yegge,
> `gastownhall/gastown`, MIT), read from source at **`649b832b76`** (2026-07-23,
> `v1.2.1-304-g649b832b`) and from its first-party design documents.
>
> **Why.** The other four studies here read *one* harness at a time. Operators now run **20–30
> agent instances against one repository**, and the hard questions move up a level: who assigns
> work, where does state live when a session dies, how do two workers avoid colliding, and how do
> you tell "running" from "done". Gas Town is the most developed public answer, and it is a direct
> test of this repository's existing axes rather than a fifth parallel subject. Scope recorded in
> [`PURPOSE.md` §0.3](../ai-workflow/memory/active/PURPOSE.md).
>
> **Not an endorsement.** One team's operating model, one set of trade-offs. Recorded because its
> abstractions are testable, not because it is the right answer for you. Nothing here is a
> recommendation to adopt the tool.

## ⚠️ Read status

**Nothing in this study was executed.** No `gt`/`bd` binary was run, no town was created, no Dolt
server started. Every mechanism is **source-read** (`internal/`) or **read from first-party design
docs** — never observed at runtime. Capability and cost claims from the project or its community are
marked 📣 and are not adopted as findings. See [`99-sources.md`](99-sources.md).

## Files

| # | File | What it covers |
|---|---|---|
| 01 | [Vocabulary](01-vocabulary.md) | Why orchestration is a separate axis; the container hierarchy (Town/Rig/Hook/Convoy); the role taxonomy (Mayor, Deacon, Boot, Dogs, Witness, Refinery, Polecat, Crew); the work-unit ladder (Bead, Formula, Protomolecule, Molecule, Wisp, Hook); **propulsion / GUPP**; identity and attribution |
| 02 | [Architecture](02-architecture.md) | The Beads/Dolt substrate and its two-level split; directory composition; the four-layer config with its `Blocked` value; how a worker is actually spawned (`WorktreeAddFromRef` vs `…ExistingForce`); **control/execution plane split**; the capacity-controlled scheduler; supervision thresholds; **the merge slot as a ledger item** |
| 03 | [Roles & lifecycle](03-roles-and-lifecycle.md) | The supervision tree and the watchdog-of-the-watchdog; the polecat state machine (Working/Idle/Done/**Stalled**/**Zombie**) and retired completion; the three heartbeat stores and the two-channel rule; the mail protocol that binds roles into a workflow; convoy/swarm/mountain and the **hysteresis** argument |
| 04 | [Orchestration techniques](04-orchestration-techniques.md) | **The point of the study.** Eleven reusable techniques (A1–A11) with caveats; where they meet this repository's Codex/Strands/ACP findings (Part B); what Gas Town does that this repository's evidence does **not** support (Part C); a one-screen card |
| 99 | [Sources](99-sources.md) | Verification status per claim, what is recorded-but-not-adopted, and what was not verified |

## If you only have two minutes

Read [`04` §"A compact card"](04-orchestration-techniques.md). The five moves:

1. **Put the plan in a ledger, not in a coordinator** — so any worker can pick it up cold.
2. **Split identity from session** — a worker is a durable id plus a disposable workspace.
3. **Make the first action mandatory and observable** — the hook, checked before anything else.
4. **Serialize the dangerous shared resource, and record the lock as a work item.**
5. **Verify liveness on two channels; escalate only on their agreement.**

Moves 1 and 3 are a package: an obligation to act is only enforceable if there is a durable thing
to act on.

## The one finding that changes an existing page

**The control/execution plane boundary is a credential boundary, not a filesystem boundary.** When
a worker runs somewhere untrusted, the thing at risk is not only its files — it is its ability to
**write its own result ledger**. An orchestrator identity plus ledger-write access is enough to
forge a completed task. So the split is *(credential-bearing control | untrusted execution)*, and
a harness that sandboxes files but leaves the result ledger writable has not separated the planes.

Recorded in [`multi-agent-orchestration` §7](../ai-workflow/wiki/concepts/multi-agent-orchestration.md)
and folded into
[`control-plane-execution-plane` §5.6](../ai-workflow/wiki/concepts/control-plane-execution-plane.md).

## What this study does **not** establish

- It does **not** weaken the approval gate. This model is largely post-hoc (verify, then merge) and
  relocates trust from prevention to detection — a **contrast**, not a data point that gates are
  unnecessary.
- It does **not** settle providers-as-data across a shared wire.
- Its scale and cost figures ("20–30 agents", "$100/hour", "Kubernetes for agents") are
  **self-reported** 📣, not measured.
- **Nothing was run.** Design-vs-implementation drift is always possible.

## Related

- [`SYNTHESIS.md`](../SYNTHESIS.md) — §2.4 (planes), §2.7 (gates), §6.5–6.7 (context drift, false
  checks), §7 (method)
- [`agent-ux/`](../agent-ux/README.md) — the client side, one level down
- [`strands/`](../strands/README.md) — the embeddable-harness case, whose `sandbox: host` default
  this study's plane split connects to
