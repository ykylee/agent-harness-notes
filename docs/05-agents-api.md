# 05. Agents API — the Managed (Hosted) Codex Harness

**Public beta on 2026-09-10.** OpenAI extracted the control layer it had been using to run Codex —
session management, context compaction, failure recovery, multi-agent coordination — and turned it
into **an API that OpenAI itself operates**.

> The **exact definitions** of endpoints, schemas, and events live in
> [08-agents-api-reference.md](08-agents-api-reference.md).
> This document covers concepts and usage scenarios.

Official wording: *"application access to OpenAI's managed Codex harness through an API."*
OpenAI handles sessions, orchestration, context management, and recovery, while the application
**provides tools and chooses the execution environment.**

## 1. Core objects

| Object | Definition |
|---|---|
| **Agent** | Model + instructions + tools + MCP servers |
| **Environment** | An optional sandbox or computer: file access, skill loading, command execution |
| **Session** | A **persistent instance of an agent** that works on tasks and responds to input |
| **Events / Items** | Inputs sent to a session and outputs it produces |

## 2. Session lifecycle

1. **Create a session** with the agent configuration
2. **Provide a task** via user input
3. Monitor progress through **streaming or webhooks**
4. Send additional tasks, or **steer** the current turn

## 3. What the managed harness provides

- Command and code execution in a sandbox
- Applying skills and instructions
- Connecting external data via tools or MCP
- **Steering mid-work**
- **Automatic compaction** as a session nears its context limit
  ("automatically compacts earlier context as a session nears its limit")
- **Subagent** delegation
- Session resumption
- **Tool search** — loading tool definitions selectively to save tokens
- **Programmatic tool calling** — parallel execution

## 4. Endpoints (as used through the SDKs)

SDKs: examples are provided in JavaScript, Python, Go, Java, Ruby, and curl.

```javascript
// Create a session
client.beta.agents.sessions.create({ /* agent, environment, input */ })
```

| Operation | Description |
|---|---|
| create | Create a session from an agent configuration, environment, and initial input |
| list | Paginated (`hasNextPage()`, `getNextPage()` helpers) |
| retrieve | Inspect status, agent configuration, environment, and **required actions** by ID |
| delete | Logical deletion (cleanup may be asynchronous). To stop current work but keep the conversation, **cancel the turn** instead |

> The API assumes you **store the session ID in your application's data store.**
> After a restart or disconnect, retrieve the session to identify pending work.

### Handling `requires_action`

When a session returns `requires_action`, the response contains an array of pending actions.

| Action | How to handle |
|---|---|
| **Function calls** | Execute the specified function and return the result using `turn_id` + `call_id` |
| **Environment connections** | Establish the connection using `environment_id` |

## 5. Execution environments (sandboxes)

### Options

1. **OpenAI-hosted** — running on Codex/ChatGPT infrastructure
2. **Self-hosted** — connect your own environment via `codex exec-server`
3. **Partner providers** — Blaxel, Cloudflare, Daytona, DigitalOcean, E2B, Modal, Oracle, Runloop, Vercel
4. **No sandbox**

### The architectural boundary (important)

> **harness (control plane)** — the agent loop, model calls, routing
> **compute (execution plane)** — files, commands, state

This boundary is what allows **sensitive orchestration to stay in trusted infrastructure while
sandboxes handle provider-specific execution.**

### Connecting a self-hosted environment

```bash
# 1. Prepare the workspace
mkdir -p /workspace
npm install -g @openai/codex@alpha
```

Networking: you only need **outbound** access to `https://api.openai.com` and
`wss://codex-cloud-environments.chatgpt.com` (all connections flow from your environment to OpenAI).

Authentication: generate a **restricted executor key** in the platform dashboard's Agents tab and
supply it as `CODEX_API_KEY`.

```bash
# 2. Create the session with a self_hosted environment
#    { "type": "self_hosted", "workspace_directory": "/workspace" }

# 3. Start the executor inside your environment
codex exec-server \
  --remote "<session.environment.remote_url>" \
  --environment-id "<session.environment.id>"
```

The executor registers using the environment ID and the restricted API key, then **connects over
WebSocket to receive commands and return results.**

Connection state events: `agent.session.environment.pending` → `connected` / `failed`.

## 6. Sandbox agents (the Agents SDK side)

> What follows is the path for **running the harness in your own infrastructure with the Agents SDK**.
> Keep it distinct from the managed Agents API.

### When to use a sandbox

- The task requires a **directory of documents**, not a single prompt
- The agent must write files for later inspection
- Commands, packages, or scripts are involved
- The work produces artifacts (Markdown, CSV, screenshots, websites)
- Services or previews must run on exposed ports
- Work pauses for human review and then **resumes in the same workspace**

Skip the sandbox when you only need a brief model response.

### Manifest — defining the starting workspace

| Entry | Description |
|---|---|
| File / Dir entries | Small synthetic inputs, helper files |
| Local paths | Host files materialized into the sandbox |
| Git repos | Repositories fetched into the workspace |
| Cloud mounts | S3, GCS, R2, Azure Blob, Box, FileMounts |
| Environment variables | Values needed at startup |
| OS accounts | Users and groups, for supported providers |

Paths must be **workspace-relative**, with no absolute paths or escape sequences.

### Capabilities

`SandboxAgent` defaults: filesystem + shell + compaction.

| Capability | Purpose |
|---|---|
| `Shell` | Command execution, interactive input |
| `Filesystem` | File editing, image inspection |
| `Skills` | Skill discovery and materialization |
| `Memory` | Retain lessons across runs |
| `Compaction` | Context trimming for long-running flows |

### Running

```javascript
const manifest = new Manifest({ entries: { /* ... */ } });
const agent = new SandboxAgent({
  name: "Agent Name",
  model: "gpt-6-astra",
  instructions: "Task instructions",
  defaultManifest: manifest,
  capabilities: [shell()]
});

const result = await run(agent, "User prompt", {
  sandbox: { client: new UnixLocalSandboxClient() }
});
```

```python
result = await Runner.run(
    agent,
    "User prompt",
    run_config=RunConfig(
        sandbox=SandboxRunConfig(client=UnixLocalSandboxClient())
    )
)
```

### Switching providers

Change the run configuration only — the agent definition stays the same.

| Provider | Client |
|---|---|
| Unix-local | `UnixLocalSandboxClient` |
| Docker | `DockerSandboxClient` |
| E2B | `E2BSandboxClient` |
| Blaxel | `BlaxelSandboxClient` |
| Cloudflare | `CloudflareSandboxClient` |
| Daytona | `DaytonaSandboxClient` |
| Modal | `ModalSandboxClient` |
| Runloop | `RunloopSandboxClient` |
| Vercel | `VercelSandboxClient` |

Start with Unix-local for development, Docker for container isolation.

### Three kinds of state, and their resolution order

| Concept | Contents |
|---|---|
| **RunState** | Harness-side model items, tool state, approvals |
| **Session state** | A serialized sandbox session for reconnection |
| **Snapshot** | Saved workspace contents for seeding a fresh session |

Resolution order: **live session → resumed RunState → explicit serialized state → fresh session**

### Sandbox memory

Persists reusable lessons across runs, **separately from** message history.

```
memory_summary.md      # high-level summary
MEMORY.md              # consolidated lessons
raw_memories/          # per-run summaries
rollout_summaries/     # detailed rollouts
```

### Composition

- **Handoffs** — route workspace-heavy tasks to sandbox agents
- **Tools** — call sandbox agents as nested tools with independent configurations

## 7. Observability

Search by session ID at `platform.openai.com/logs?api=agents` to inspect **turns, tool calls, and
subagents.**

When successive model calls share the same prompt prefix, **prompt caching** reuses the earlier
processing.

## 8. Pricing and constraints

- **No additional service fee for the Agents API itself.** Billing accrues separately across:
  - model tokens
  - OpenAI-provided tools
  - **container time** for OpenAI-hosted sandboxes
- Data residency: **US only**
- **Zero Data Retention is not supported.** Using a self-hosted sandbox does not confer ZDR eligibility
- Models appearing in the docs' examples: `gpt-6-astra` (SDK examples), `gpt-5.6-terra` (Codex SDK examples)

## 9. How it relates to the open-source harness

```
       open source                            managed
┌──────────────────────────┐        ┌──────────────────────────┐
│  openai/codex (Apache-2) │        │  Agents API (run by      │
│  ├─ codex exec           │        │  OpenAI)                 │
│  ├─ Codex SDK            │  ───▶  │  ├─ sessions             │
│  └─ app-server           │ same   │  ├─ hosted sandboxes     │
│      (JSON-RPC)          │harness │  ├─ subagents            │
└──────────────────────────┘        │  └─ auto compaction      │
       you operate it               └──────────────────────────┘
                                     OpenAI operates it (with versioned
                                     access aligned to model releases)
```

*"a managed service built on the open-source Codex harness"* — **the same harness; only the
operator differs.**
