---
type: concept
status: active
last_ingested_from: docs/05-agents-api.md + docs/09-agents-api-environments.md + browser-agents/11-dia-and-neon.md + browser-agents/12-dia-binary.md + browser-agents/06-architecture-axes.md + gas-town/02-architecture.md + gas-town/04-orchestration-techniques.md + gas-city/02-architecture.md + gas-city/04-orchestration-techniques.md
related_pages: [concepts/execution-environment-topology, concepts/harness, concepts/os-sandbox-policy, concepts/provider-as-data, concepts/multi-agent-orchestration]
created: 2026-09-22
updated: 2026-09-30
---

# Control Plane / Execution Plane — separating the harness from compute

- Purpose: the single most important structural boundary the managed Agents API draws.
- Scope: the definition, the three pieces, what the boundary enables, key separation, and how browser agents split it three ways
- Primary source: `developers.openai.com/api/docs/guides/agents-api/architecture` (raw Markdown)
- Updated: 2026-09-30 (Dia planning relocated: local `agent-server` + Claude Code; model tokens still remote)

## §1 TL;DR  {#s1-tldr}

| # | Plane | What lives there |
|---|---|---|
| 1 | **harness (control plane)** | the agent loop, model calls, routing |
| 2 | **compute (execution plane)** | files, commands, state |

> The boundary is what lets **sensitive orchestration stay in trusted infrastructure while sandboxes
> handle provider-specific execution.**

## §2 The three pieces  {#s2-three-pieces}

| Piece | What it is |
|---|---|
| **Harness** | The OpenAI-hosted Codex instance that runs the model and tool loop and maintains the session |
| **Environment** | Where the agent runs commands, executes code and works with files — a remote sandbox, your laptop, a Docker container, an AWS Lambda function |
| **Application server** | Your code. Submits tasks, receives events, handles function tools. When you provide the environment, it manages that lifecycle too |

> "OpenAI runs the agent harness. Your application sends it work and receives results.
> Add an environment when the agent needs compute or files."

## §3 The key separation the boundary forces  {#s3-key-separation}

Two planes means **two kinds of credential.** This is the most important of the security rules.

| Key | Scopes | Where it lives |
|---|---|---|
| **Application API key** | `api.agents.read`, `api.agents.write`, `api.responses.write` (plus `api.vaults.read`/`write`) | **outside the environment** |
| **Environment key** (`CODEX_API_KEY`) | connecting environments **only** — "cannot authorize any other API action" | inside the environment |

> **Agent-generated code can read the environment key.** That is acceptable precisely because the
> key's authority is limited to connecting environments. The application API key must never be in the
> environment, in images, in source code or in logs.

This is the core lesson of the boundary — **assume a credential placed on the execution plane will be
read there, and cut its authority on that assumption.**

## §4 What the execution plane exposes  {#s4-execution-risk}

> **Agent-generated code can access the files, credentials, and network available to its environment.**

| Measure | Detail |
|---|---|
| **Isolate workloads** | run in isolated compute such as VMs; separate environments for users or workloads that must not share data; a dedicated OpenAI project per application |
| **Restrict network access** | allow outbound only to approved endpoints, including the executor's required hosts. **Executor MCPs connect from your environment; remote MCPs connect from OpenAI's service** — different reachability requirements |
| **Broker third-party access** | route through a credential broker that injects secrets into approved outbound requests. Remember that **injecting a stored secret into the environment is itself exposing it to agent-generated code** |

## §5 Porting the boundary to a custom harness  {#s5-porting}

| # | What to carry over |
|---|---|
| 1 | Split orchestration (loop, routing, model calls) from execution (files, commands) **at a process boundary** |
| 2 | **Assume credentials on the execution plane will be read**, and scope them accordingly |
| 3 | Make the connection direction **outbound-only** — why a self-hosted environment needs no inbound ports |
| 4 | Separate the lifetime of the execution plane from that of the control plane ([[concepts/execution-environment-topology]] §5) |

## §5.5 Observation — browser agents split this three ways  {#s5-5-browser-evidence}

The Agents API **declares** this boundary. Among browser-type agents the same boundary is **drawn in
a different place by each product**, which makes the axis sharper.

| Product | Planning (control) | Execution | Evidence |
|---|---|---|---|
| **Comet** | **server** — the Perplexity backend plans and issues commands | local extensions | reverse engineering |
| **Aside** | **local daemon** (`127.0.0.1:21420`, a 353MB Node SEA) | local browser | binary analysis |
| **Opera Neon** | **cloud LLM** | local browser (Neon Do) | product FAQ |
| Dia | **local `agent-server` spawning Claude Code 2.1.270**; model tokens still remote | local | binary analysis ([12](../../../browser-agents/12-dia-binary.md)) |

> 📌 **This axis decides the model economics.** Aside can pull in a user's ChatGPT or Claude
> subscription over OAuth because planning is local. If planning ran on a server there would be no
> reason to use the user's credentials — Comet gives model choice only to Max subscribers.
>
> 📌 **Dia's loop is local; its model tokens are not.** Opening the binary relocated planning from
> "via its own servers" to a local harness. The security page still says request data is "sent
> through our servers" to partner models. Record both.

> ⚠️ **Check which side a vendor means by "local."** Opera's `llms.txt` says "All AI processes run
> locally on the device," while the product FAQ says **planning uses cloud LLMs.** Two first-party
> sources from the same company disagree.

## §5.6 Observation — orchestration sharpens the boundary to a credential  {#s5-6-orchestration}

[[concepts/multi-agent-orchestration]] contributes the sharpest form of this axis so far, from
Gas Town's sandbox proposal. Every version of the boundary on this page asks *where execution runs*.
The orchestration case asks a different question: when a worker is moved somewhere untrusted, **the
thing at risk is not only the filesystem — it is the worker's ability to write its own results.**
An orchestrator's identity plus ledger-write access is enough to forge a completed task.

So the boundary is not *(planning | execution)* but:

> **(credential-bearing control | untrusted execution)**

The control channel — assign work, report status, update the result ledger — stays reachable and
credentialed on the host; the execution plane (inference, file edits, `git`) goes where it is
constrained. **A harness that sandboxes files but leaves the result ledger writable has not
separated the planes.** This also explains why §3's "key separation" needs the *channel* protected
and not only the compute: the ledger is a control surface.

Gas City (`3ef7fadd42`) adds a second door and does not close the first. `internal/citywriteauth`
verifies ed25519 single-use grants for **city configuration** mutations, bound to one request.
The package mints nothing; the bundled dashboard is rejected once the gate is on. That credential
does not cover `bd` writes, and a worker that can write a control bead can strand a workflow
([`gas-city/02`](../../../gas-city/02-architecture.md) §6, [`gas-city/04`](../../../gas-city/04-orchestration-techniques.md) A1).
Prefix isolation between rigs is a `bd` query filter on a shared server, not a credential either.

## §6 Read next  {#s6-next}

- [[concepts/execution-environment-topology]] — the three shapes of the execution plane
- [[concepts/provider-as-data]] — who chooses the model, which follows from planning location
- [[concepts/os-sandbox-policy]] — OS-level defence inside the execution plane
- [[concepts/multi-agent-orchestration]] — the layer above the harness; §5.6 is its contribution here
- Original: [`docs/09-agents-api-environments.md`](../../../docs/09-agents-api-environments.md)
