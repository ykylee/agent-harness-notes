---
type: concept
status: active
last_ingested_from: docs/05-agents-api.md + docs/09-agents-api-environments.md + browser-agents/11-dia-and-neon.md + browser-agents/06-architecture-axes.md
related_pages: [concepts/execution-environment-topology, concepts/harness, concepts/os-sandbox-policy, concepts/provider-as-data]
created: 2026-09-22
updated: 2026-09-26
---

# Control Plane / Execution Plane — separating the harness from compute

- Purpose: the single most important structural boundary the managed Agents API draws.
- Scope: the definition, the three pieces, what the boundary enables, key separation, and how browser agents split it three ways
- Primary source: `developers.openai.com/api/docs/guides/agents-api/architecture` (raw Markdown)
- Updated: 2026-09-26 (re-checked against the Codex drift re-check of `e72da2b538`; no change to this concept)

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
| Dia | via its own servers → partner models | local | security documentation |

> 📌 **This axis decides the model economics.** Aside can pull in a user's ChatGPT or Claude
> subscription over OAuth because planning is local. If planning ran on a server there would be no
> reason to use the user's credentials — Comet gives model choice only to Max subscribers.

> ⚠️ **Check which side a vendor means by "local."** Opera's `llms.txt` says "All AI processes run
> locally on the device," while the product FAQ says **planning uses cloud LLMs.** Two first-party
> sources from the same company disagree.

## §6 Read next  {#s6-next}

- [[concepts/execution-environment-topology]] — the three shapes of the execution plane
- [[concepts/provider-as-data]] — who chooses the model, which follows from planning location
- [[concepts/os-sandbox-policy]] — OS-level defence inside the execution plane
- Original: [`docs/09-agents-api-environments.md`](../../../docs/09-agents-api-environments.md)
