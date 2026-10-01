# Gas City — the platform under the operating model

> **What this is.** A study of [Gas City](https://github.com/gastownhall/gascity) (`gastownhall/gascity`,
> MIT, Go), read from source at **`3ef7fadd42`** (2026-09-30, `fix(runtime): honest acp/subprocess
> listing and three-outcome liveness (#6879)`; the shallow clone also carried the moving tag
> `edge`). First-party docs under `docs/` and `engdocs/architecture/` were read with the code, and
> where they disagree the code wins. The disagreement is recorded, not smoothed.
>
> **Why.** [`gas-town/`](../gas-town/README.md) read one operating model: named roles, a town
> directory, a witness and a refinery. Gas City is the extraction of that machinery into a
> toolkit whose orchestrator is not supposed to know those names. It is the same axis — who
> assigns work, where state lives when a session dies — read from the platform side. Scope is
> the continuation of [`PURPOSE.md` §0.3](../ai-workflow/memory/active/PURPOSE.md), recorded in
> §0.4.
>
> **Not an endorsement.** A configurable factory is still one team's factory. Nothing here is a
> recommendation to adopt `gc`.

## ⚠️ Read status

**Nothing in this study was executed.** No `gc` binary was built, no city was created, no Dolt
server started, no agent was attached. Every mechanism is **source-read** (`cmd/gc`,
`internal/`) or **read from a first-party doc that was checked against that source**. Capability
claims ("hundreds of concurrent agents", "software factory") are 📣 and are not adopted. See
[`99-sources.md`](99-sources.md).

Several architecture notes in the repo are older than the code they describe (`engdocs/architecture/glossary.md`
says "last verified 2026-04-25"). This study treats those dates as a warning, not as authority.

## Files

| # | File | What it covers |
|---|---|---|
| 01 | [Vocabulary](01-vocabulary.md) | The six primitives and the three pieces of machinery; orders; why "zero roles" is true of the type system and false of the bundled core pack |
| 02 | [Architecture](02-architecture.md) | One Dolt server and prefix isolation; class-typed stores; formula v1 vs v2; the control dispatcher as a `gc` process; session providers; trust and city-write grants |
| 03 | [Roles & lifecycle](03-roles-and-lifecycle.md) | Agent config instead of a role enum; the Gastown pack as data; reconciliation; three-outcome liveness; the claim protocol; ACP as a transport that does not answer permission |
| 04 | [Orchestration techniques](04-orchestration-techniques.md) | **The point of the study.** What changes relative to [`gas-town/04`](../gas-town/04-orchestration-techniques.md); where it meets this repository; what it does not establish |
| 99 | [Sources](99-sources.md) | Verification status per claim |

## If you only have two minutes

Read [`04` §"A compact card"](04-orchestration-techniques.md). The five moves, on top of the Gas
Town card:

1. **Keep judgment out of the orchestrator.** Control flow is a bead kind the dispatcher executes. A role with an opinion is a prompt in a pack.
2. **Do not treat a failed observation as a dead worker.** Liveness has a third outcome: incomplete.
3. **Make the claim a command, not a query the worker invents.** `gc hook` exists because `bd ready` hides the work.
4. **Isolate projects by prefix on one ledger**, not by standing up a database per project.
5. **Treat config as code and bead text as data.** A formula variable interpolated into a shell is an injection, not a template.

## The one finding that changes an existing page

**Hosting an agent over ACP is not the same as answering its permission request.** Gas City's ACP
session provider sends prompts and reads `session/update`, and `Pending` / `Respond` return
`ErrInteractionUnsupported`. A conformance test records the consequence: the fake agent sends
`session/request_permission`, the client writes no reply, the permission times out, and the tool
is rejected. An orchestrator can therefore sit on the ACP wire and still drop the approval
primitive this repository already treats as load-bearing.

Recorded in [`approval-gate` §7.7](../ai-workflow/wiki/concepts/approval-gate.md) and in
[`04`](04-orchestration-techniques.md) Part B.

## What this study does **not** establish

- It does **not** retire the Gas Town role model. Mayor, deacon, witness, refinery, and polecat
  still ship, as the bundled Gastown pack (`gascity-packs`), which the `gc` binary embeds.
- It does **not** replace the credential-plane finding. City-write grants authorize *config*
  mutations. They say nothing about a worker forging its own result bead.
- It does **not** weaken the approval gate. Dropping `session/request_permission` is another way
  to run with the gate unanswered, which is the failure mode, not a counterexample.
- **Nothing was run.** The architecture notes inside the Gas City repo already drift from its code;
  a runtime would drift further.

## Related

- [`gas-town/`](../gas-town/README.md) — the operating model this platform was extracted from
- [`SYNTHESIS.md`](../SYNTHESIS.md) — §2.4 (planes), §2.7 (gates), §7 (method)
- [`ai-workflow/wiki/concepts/multi-agent-orchestration.md`](../ai-workflow/wiki/concepts/multi-agent-orchestration.md)
