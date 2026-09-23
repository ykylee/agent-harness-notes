---
type: concept
status: active
last_ingested_from: docs/01-overview.md + docs/06-choosing.md + docs/12-product-surface.md + browser-agents/01-landscape.md + browser-agents/06-architecture-axes.md
related_pages: [concepts/harness-engineering, concepts/thread-turn-item, concepts/control-plane-execution-plane, concepts/wire-protocol-boundary, concepts/perception-model]
created: 2026-09-22
updated: 2026-09-23
---

# Harness — the agent execution system

- Purpose: what a "harness" is, what sits inside it, and how many layers OpenAI opened of theirs.
- Scope: definition, internal components, the four-layer opening, what the application owns, the size of the surface
- Primary sources: the `openai/codex` repository plus the "Codex as a platform" and "Unlocking the Codex harness" posts
- Updated: 2026-09-23

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | One-line definition | **the execution system that sits between a model and a task** |
| 2 | Where the product value lives | this execution layer, not the chat UI |
| 3 | Code location | `codex-rs/core/` (Codex core). The repository spans 100+ Rust crates |
| 4 | Licence | Apache-2.0 |
| 5 | Opened layers | CLI · SDK · App Server protocol · managed Agents API (four) |
| 6 | Share taken by the agent loop | **about 20 of 104 methods — a fifth** |

## §2 Definition  {#s2-definition}

OpenAI's own phrasing:

> "A capable agent is more than a prompt and a model response. It needs a way to understand a task,
> maintain context over time, inspect relevant information, call tools, expose progress, handle
> failures, request human approval when necessary, and return a useful result."

The `harness engineering` post puts it more sharply: where classical software engineering assumes
**predictable behaviour**, harness engineering is the work of **bounding, observing and governing an
autonomous runtime whose exact trajectory no developer can predict in advance.** Operating principles
in [[concepts/harness-engineering]].

## §3 What is inside a harness  {#s3-components}

Beyond the agent loop itself:

| # | Component | Contents |
|---|---|---|
| 1 | **Thread lifecycle and persistence** | creating, resuming, forking and archiving threads, and persisting event history so clients reconnect to a consistent timeline |
| 2 | **Config and auth** | loading configuration, managing defaults, running authentication flows such as "Sign in with ChatGPT," and credential state |
| 3 | **Tool execution and extensions** | executing shell and file tools in a sandbox, and wiring MCP servers and skills into the loop under one policy model |

**Codex core** is both at once — the **library** where the agent code lives, and a **runtime** that
can be spun up to run the loop and manage one thread's persistence.

## §4 Where the App Server sits  {#s4-app-server}

```
Clients (Web / TUI / VS Code · JetBrains · Xcode / Desktop / partners)
        │  bidirectional JSON-RPC (JSONL)
Codex App Server (long-lived process)
   ├─ stdio reader
   ├─ Codex message processor   ← translation layer
   ├─ thread manager            ← one core session per thread
   └─ core threads (N Codex core runtimes)
        │
Model (Responses API) · tools · MCP · sandbox
```

- The **thread manager** spins up one core session per thread.
- The **message processor** translates client JSON-RPC into core operations and turns core's
  low-level internal event stream into **a small set of stable, UI-ready notifications.**
- The protocol is **fully bidirectional.** When approval is needed *the server* issues a request and
  pauses the turn ([[concepts/approval-gate]]).

### §4.1 Why JSON-RPC and not MCP  {#s4-1-why-jsonrpc}

| Step | What happened |
|---|---|
| 1 | Codex CLI began as a TUI, handling Rust types in the same process as the agent loop |
| 2 | Building the VS Code extension meant reusing the harness, which required interaction beyond request/response — workspace exploration, streaming reasoning, emitting diffs |
| 3 | **They first tried exposing Codex as an MCP server.** Maintaining MCP semantics in a way that made sense for VS Code proved difficult |
| 4 | Instead they introduced a JSON-RPC protocol mirroring the TUI loop — the unofficial first App Server |
| 5 | Demand from JetBrains, Xcode and the Desktop app (orchestrating agents in parallel) pushed it into **a platform surface with backward-compatibility guarantees** |

## §5 The four-layer opening  {#s5-layers}

| Layer | Artifact | Who runs it | Good for |
|---|---|---|---|
| CLI | `codex exec` | your machine / CI | scripts, CI jobs, one-off batches |
| SDK | `@openai/codex-sdk`, `openai-codex` | your machine (spawns the CLI) | embedding in server-side tools |
| Protocol | `codex app-server` | your machine / container | **when the agent is the product** |
| Managed | Agents API | **OpenAI-hosted** | when you want the harness operated for you |

The official recommendation is the App Server — *"Codex App Server will be the first-class
integration method we maintain moving forward."* Selection criteria in `docs/06-choosing.md`.

## §6 What the application owns  {#s6-application-owns}

The official division of labour: *"Your application owns product context, business rules, and tools;
Codex app-server provides the agent loop and sandboxed execution."*

| # | The application's share |
|---|---|
| 1 | **Interface** — keep your existing dashboards and workflows |
| 2 | **Context and tools** — expose application-owned MCP services |
| 3 | **Operational boundaries** — file access scope, where approvals are required, execution scope, observation and logging |

Its protocol-level implementation is `item/tool/call` — the channel by which the agent calls tools
**owned by the host application.**

## §7 What the size of the surface teaches  {#s7-surface-size}

Reading all 104 `ClientRequest` methods as a list of product requirements:

| Tier | Methods | Contents |
|---|---|---|
| Agent core | ~20 | the loop: threads, turns, items, approvals |
| Capability system | ~25 | skills, plugins, marketplaces, apps, hooks, MCP |
| Host services | ~15 | filesystem, PTY, fuzzy search, git |
| Identity and policy | ~20 | accounts, auth, rate limits, config, permission profiles |
| Platform and migration | ~10 | Windows sandbox, external agent import, feedback |
| Realtime | ~11 (notifications) | voice sessions |

> **The agent loop is maybe a fifth of the work.** The rest decides whether anyone can actually use
> the thing. The minimum product-grade set is core 20 plus about 25 — **roughly 45**
> (`docs/12-product-surface.md` §4).

## §7.5 Observation — the execution surface divides harnesses  {#s7-5-surfaces}

The Codex harness's execution surface is **the shell and the filesystem.** The same abstraction over
**a browser and an OS** becomes a different class of thing. `browser-agents/` is the study of that
class.

| Shell | What you get | What you pay | Examples |
|---|---|---|---|
| **Native browser (fork)** | browser-chrome-level UX, a full permission model, custom extension APIs | **the debt of chasing Chromium**, user migration | Aside, Comet, Dia, Neon |
| **Extension** | no migration, no maintenance debt | only what extension APIs permit | Claude for Chrome, Gemini in Chrome |
| **Library** | full control, programmatic composition | not a product a person uses | Browser Use |

> ⚠️ **The outer classification can differ from the inner structure.** Both Comet and Aside present
> as native browsers, yet **both implement the agent as an MV3 Chrome extension.** The shell is a
> distribution unit; control lives in the extension layer — which is what lets their release cadences
> diverge (Aside: shell `1.0.x`, extensions and CLI `1.26.x`).
>
> 📌 **Building a browser is not a product but a standing debt.** OpenAI retired ChatGPT Atlas within
> ten months (2026-08-09), with **security maintenance** among the stated reasons. The features moved
> into ChatGPT and Codex — agent capability does not require owning a browser.

## §7.6 Surface-independent axes vs. surface-specific ones  {#s7-6-axis-split}

Across both studies, the design axes of a harness split.

| **Surface-independent** (reusable) | **Surface-specific** |
|---|---|
| approval gates [[concepts/approval-gate]] | **perception model** [[concepts/perception-model]] |
| providers as data [[concepts/provider-as-data]] | **indirect prompt injection** [[concepts/indirect-prompt-injection]] |
| capability distribution [[concepts/capability-distribution]] | **credential shielding** [[concepts/credential-shielding]] |
| control/execution plane [[concepts/control-plane-execution-plane]] | sandbox mechanisms [[concepts/os-sandbox-policy]] |
| conversation primitives [[concepts/thread-turn-item]] | |

> 📌 **The left column is this repository's reusable asset.** Whatever surface a new harness targets,
> the left column applies unchanged. The right column only has answers once the surface is chosen.
> The full synthesis is [`SYNTHESIS.md`](../../../SYNTHESIS.md).

## §8 Read next  {#s8-next}

- [[concepts/thread-turn-item]] — the three conversation primitives
- [[concepts/approval-gate]] — where humans step in
- [[concepts/control-plane-execution-plane]] — separating the harness from compute
- [[concepts/wire-protocol-boundary]] — the boundary that decides whether the core is reusable
- Originals: [`docs/01-overview.md`](../../../docs/01-overview.md), [`docs/12-product-surface.md`](../../../docs/12-product-surface.md)
