# 01. Codex Harness Overview

> Drift-checked against `openai/codex@e72da2b538` (2026-09-26); changes marked *(2026-09-26)*.

## 1. What a harness is

OpenAI's definition (from the "Codex as a platform" blog post):

> "A capable agent is more than a prompt and a model response. It needs a way to understand a task,
> maintain context over time, inspect relevant information, call tools, expose progress, handle failures,
> request human approval when necessary, and return a useful result."

In short, a **harness is the execution system that sits between a model and a task**.
OpenAI's argument is that this execution layer — not the chat UI — is where the product value lives.

The `harness engineering` post puts it more sharply: where classical software engineering assumes
*predictable behavior*, harness engineering is the work of *bounding, observing, and governing an
autonomous runtime whose exact trajectory no developer can predict in advance*.

## 2. What is inside the harness

Per the "Unlocking the Codex harness" post, beyond the core agent loop it includes:

1. **Thread lifecycle & persistence** — creating, resuming, forking, and archiving threads, and
   persisting event history so clients can reconnect and render a consistent timeline.
2. **Config & auth** — loading configuration, managing defaults, and running authentication flows
   like "Sign in with ChatGPT," including credential state.
3. **Tool execution & extensions** — executing shell/file tools in a sandbox and wiring up
   integrations such as MCP servers and skills so they participate in the agent loop under a
   consistent policy model.

All of this agent logic lives in a part of the Codex CLI codebase called **Codex core**.
Codex core is both (a) the **library** where the agent code lives and (b) a **runtime** that can be
spun up to run the agent loop and manage the persistence of one Codex thread.

## 3. Where the App Server sits

```
┌──────────────────────────────────────────────────────────┐
│  Clients: Web app / CLI (TUI) / VS Code·JetBrains·Xcode  │
│           / macOS Desktop / partner products             │
└───────────────────────────┬──────────────────────────────┘
                            │  bidirectional JSON-RPC (JSONL)
┌───────────────────────────▼──────────────────────────────┐
│  Codex App Server (long-lived process)                   │
│   ├─ stdio reader                                        │
│   ├─ Codex message processor   ← translation layer       │
│   ├─ thread manager            ← one core session/thread │
│   └─ core threads (N Codex core runtimes)                │
└───────────────────────────┬──────────────────────────────┘
                            │
                     Model (Responses API) · tools · MCP · sandbox
```

- The **thread manager** spins up one core session per thread.
- The **message processor** translates client JSON-RPC requests into Codex core operations, and
  transforms core's low-level internal event stream into **a small set of stable, UI-ready
  JSON-RPC notifications**.
- The protocol is **fully bidirectional**. When an approval is needed, *the server* issues a request
  and pauses the turn until the client responds.

### Origins (why JSON-RPC and not MCP)

- Codex CLI began as a TUI, handling Rust types directly in the same process as the agent loop.
- Building the VS Code extension meant reusing the same harness → which required interaction
  patterns beyond simple request/response: exploring the workspace, streaming progress as the agent
  reasons, emitting diffs.
- **They first experimented with exposing Codex as an MCP server**, but maintaining MCP semantics in
  a way that made sense for VS Code proved difficult.
- Instead they introduced a JSON-RPC protocol mirroring the TUI loop — this became the unofficial
  first version of the App Server.
- Later demand from JetBrains, Xcode, and the Desktop app (orchestrating agents in parallel) pushed
  it into a **platform surface with backward-compatibility guarantees**.

## 4. The three-layer open structure

| Layer | Artifact | Who runs it | Good for |
|---|---|---|---|
| CLI | `codex exec` | Your machine / CI | Scripts, CI jobs, one-off batches |
| SDK | `@openai/codex-sdk`, `openai-codex` | Your machine (spawns the CLI: TS via `codex exec`, Python via `codex app-server` *(corrected 2026-09-26)*) | Embedding in server-side tools and workflows |
| Protocol | `codex app-server` | Your machine / container | When the agent **is the product** |
| Managed | Agents API | **OpenAI-hosted** | When you want the harness operated for you |

Official wording:
- "For a script, CI job, or one-off background task, `codex exec` can run a bounded agent workflow and return structured output."
- "The official Codex SDK provides a direct programmatic interface."
- "Use Codex app-server when the agent is part of the product itself."
- "Your application owns product context, business rules, and tools; Codex app-server provides the agent loop and sandboxed execution."

## 5. What the application controls

1. **Interface** — keep your existing dashboards and workflows.
2. **Context & tools** — expose application-owned MCP services.
3. **Operational boundaries** — file access scope, where approvals are required, execution scope,
   observation and logging.

The reference example is **Relay**, a shipment-operations dashboard: the agent is embedded beside
the dashboard, data retrieval goes through application-owned MCP tools, consequential actions
require human approval, and the application owns refreshing the dashboard after a tool changes data.

## 6. Reference adopters (officially named)

- **GitHub, JetBrains** — bringing Codex into existing IDE workflows
- **Cisco** — using the Codex SDK in App Builder inside Cisco Cloud Control
- **Thrive Holdings + Crete** — a tax-preparation workflow. Their pilot processed 7,000 returns and
  reduced preparation time by about a third

## 7. A sense of the codebase

`codex-rs/` in the `openai/codex` repository spans over 100 Rust crates. The harness-relevant ones:

```
codex-rs/
├── core/                      # Codex core: the agent loop itself
├── app-server/                # the App Server process
├── app-server-protocol/       # protocol types + generated JSON Schema / TS definitions
├── app-server-client/         # client implementation
├── app-server-transport/      # stdio / WebSocket / UDS transports
├── app-server-daemon/
├── exec/  exec-server/  exec-server-protocol/   # non-interactive · self-hosted executor
├── codex-mcp/  rmcp-client/   # MCP server/client
├── sandboxing/  linux-sandbox/  windows-sandbox-rs/  mxc-sandbox/  bwrap/
├── skills/  plugin/  hooks/  memories/  connectors/
├── agent-roles/  agent-identity/  agent-graph-store/   # subagents / multi-agent
├── rollout/  thread-store/  history/  state/           # persistence
├── otel/  analytics/  diagnostics/                     # observability
└── tui/  cloud-tasks/  realtime-webrtc/  voice-host/
```

License: **Apache-2.0**.
