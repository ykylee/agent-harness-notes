---
type: concept
status: active
last_ingested_from: docs/09-agents-api-environments.md + docs/05-agents-api.md + strands/04-harness-and-cli.md
related_pages: [concepts/control-plane-execution-plane, concepts/approval-gate, concepts/capability-distribution, concepts/os-sandbox-policy]
created: 2026-09-22
updated: 2026-09-26
---

# Execution Environment Topology — the three shapes of an execution environment

- Purpose: the three kinds of execution environment a managed harness can attach to, and each one's lifecycle and constraints.
- Scope: the three topologies, hosted configuration, the file/artifact asymmetry, the self-hosted lifecycle, the two provider rosters
- Primary sources: the `agents-api/environments/{openai-hosted,self-hosted,lifecycle,files,security}` guides (raw Markdown)
- Updated: 2026-09-26 (re-checked against the Codex drift re-check of `e72da2b538`; no change to this concept)

## §1 TL;DR  {#s1-tldr}

| `environment.type` | Who creates it | How files come back |
|---|---|---|
| `none` | — (no environment) | none — read output from session items |
| `openai_hosted` | OpenAI | the session Artifacts API (`/workspace/outputs` only) |
| `self_hosted` | you | your provider's file API or a mounted filesystem |

## §2 The three topologies  {#s2-topologies}

### §2.1 `none`  {#s2-1-none}

For agents that answer questions or reach external services. The harness calls remote MCP tools
directly; function tools are handled by your code.

**What you lose:** the built-in Bash and apply-patch tools, workspace files, and executor MCPs.
You can still simulate a filesystem and shell through your own function tools (the docs call this an
optional "virtual runtime").

### §2.2 `openai_hosted`  {#s2-2-hosted}

OpenAI creates and manages a sandbox for the session and runs commands in it directly. You configure
packages, files and network access.

### §2.3 `self_hosted`  {#s2-3-self-hosted}

For your infrastructure, private network or custom software. Your code starts the environment and
connects an executor. **You own provisioning, reconnection, shutdown and preserving any files you
need.**

## §3 OpenAI-hosted sandbox configuration  {#s3-hosted-config}

A Linux workspace with Python, Node.js and command-line tools. The working directory is `/workspace`.

| Field | Purpose |
|---|---|
| `packages` | `python` / `system` / `npm` lists. Pin versions when needed (`pandas==2.2.3`) |
| `setup_commands` | ordered shell commands run **before** the agent starts, each with an optional `cwd` (default `/workspace`) |
| `files` | input files by Files API ID or inline base64 |
| `env` | string environment variables. **Runtime-reserved names — `PATH`, `CODEX_*`, `OPENAI_API_KEY` — are rejected** |
| `skills`, `plugins`, `capability_directories` | skills and plugins |
| `environment_template_id` | reuse saved configuration. Omitted settings inherit the template, but **network overrides cannot broaden its policy** |

> **Ordering that matters**: packages and input files are prepared **before** setup commands run.
> **A nonzero setup exit status prevents the agent from starting.**
> **Templates save configuration, not a running workspace.**

### §3.1 Network policy  {#s3-1-network}

| `network.access` | Behaviour |
|---|---|
| `enabled` | allow outbound. The default unless a template policy is inherited |
| `disabled` | block outbound |
| `restricted` | allow only the hosts in `allowed_domains` |

`restricted` takes **1–100 exact host names.** **No wildcards, protocols, paths or ports.**
**Subdomains and redirect destinations need their own entries.**
Hosted **stdio** MCP servers currently require `enabled`.

### §3.2 Status and expiry  {#s3-2-status-expiry}

The create-session response means only that setup has *started*. Check with
`GET /v1/agents/environments/{environment_id}`.

| Status | Meaning |
|---|---|
| `provisioning` | setup is running |
| `connected` | setup succeeded |
| `failed` | read `environment.error` in the `agent.session.environment.failed` event |

**Wait for `connected` before adding or listing live files.**

> Connected sandboxes receive keep-alives, including between turns. If activity and keep-alives stop
> for **an hour**, the sandbox can be deleted. **That timeout is not configurable.**
> If deletion returns `409` while setup or execution finishes, wait and retry **with a limit on
> attempts**. **Closing an event stream does not cancel the task.**

## §4 Files and artifacts — an easily missed asymmetry  {#s4-files-artifacts}

**File** = lives in the agent's environment. **Artifact** = a published copy, downloadable **after
the environment expires.**

> ⚠️ **Files from self-hosted environments are not published through the Artifacts API, including
> files under `/workspace/outputs`.**

| Item | Rule |
|---|---|
| Publishing | write under `/workspace/outputs` and they are **published as immutable artifacts when the turn completes** |
| Identification | **turn ID plus path** |
| Download | **one artifact per request.** No batch endpoint — ask the agent to bundle a ZIP |
| Modification | artifacts **cannot be uploaded or edited.** Publish a new version by updating the file and completing another turn |
| Deletion | deleting an artifact **leaves the file in the environment intact** |

### §4.1 Limits  {#s4-1-limits}

| Operation | Limit |
|---|---|
| Files included when creating a session | 50 per request |
| Inline upload | 5 MiB per file, measured **before** base64 encoding |
| Inline uploads in one creation request | 10 MiB total, before encoding |
| File copied from the Files API | 50 MiB per file |
| Published artifact | 200 MiB per file |
| Outputs published together | 500 MiB total |

## §5 Self-hosted lifecycle  {#s5-lifecycle}

### §5.1 Starting — only spinning up compute when needed  {#s5-1-start}

The API emits `agent.session.action_required` with
`required_action.type: "environment_connection"` **before waiting** for the executor.

| Path | What to do |
|---|---|
| **Handler (fast)** | ① verify the webhook signature ② queue connection requests only when the type is `environment_connection` (and queue session failures) ③ **return a successful HTTP response only after queuing succeeds** |
| **Worker (slow)** | ① retrieve the session; ignore deleted sessions and resolved actions ② for a self-hosted session still needing a connection, start or reconnect its executor using `session.environment.id` and `remote_url` ③ for one still failed, **release its compute** |

> ⏱ **Timing**: turn creation and `agent.session.in_progress` events arrive **too late** to start an
> offline executor. A `function_call` required action needs a function result, not environment startup.

### §5.2 Stopping  {#s5-2-stop}

Keep compute running between turns for reuse, or allow a grace period after a turn ends. Coordinate
shutdown with incoming work — cancel a pending shutdown when a connection is requested or execution
starts, and recheck state before stopping.

> **An idle event alone is not a safe shutdown signal.** It can arrive when a connection request
> clears, before waiting input starts its turn.

### §5.3 Avoiding duplicates  {#s5-3-dedup}

> Use **one component** to manage each session's environment. Store the session-to-compute mapping.
> **Repeated or concurrent requests must not create duplicate environments.**

## §6 There are two provider rosters — why they confuse  {#s6-two-rosters}

Each has nine entries, which is exactly why they look contradictory. **They belong to different
products.**

| | Providers |
|---|---|
| **Both (7)** | Blaxel, Cloudflare, Daytona, E2B, Modal, Runloop, Vercel |
| **Agents API only** | DigitalOcean, Oracle Cloud Infrastructure |
| **Agents SDK only** | Unix-local, Docker — local runtimes, not cloud partners |

- The **Agents API roster** lists cloud providers hosting an environment the *managed harness*
  connects to.
- The **Agents SDK roster** lists client classes you instantiate when running *the harness in your
  own infrastructure*.

> Pick the roster that matches **who runs the harness**, not the provider you already use.

## §6.5 Observation — the topology as a constructor argument  {#s6-5-strands}

**Strands** ([`strands/04`](../../../strands/04-harness-and-cli.md) §3) expresses this page's topology inside a
library: `Agent(sandbox=…)` takes one of `NotASandboxLocalEnvironment` (the default — "no isolation …
full privileges of the host process"), `DockerSandbox` or `SshSandbox`. Every harness tool (shell,
files, `web_fetch`'s curl, environment probes) routes through it.

| Agents API | Strands |
|---|---|
| `none` | — |
| `openai_hosted` | — (no hosted plane) |
| `self_hosted` | `DockerSandbox` · `SshSandbox` |
| (local CLI) | `NotASandboxLocalEnvironment` — the default |

> 📌 **Selecting a plane is not restricting it.** The `Sandbox` object decides *where* a command runs;
> nothing in it limits *what* the command touches ([[concepts/os-sandbox-policy]] is the other half).
> Even the host plane passes the full process environment — credentials included — to every child.

## §7 Read next  {#s7-next}

- [[concepts/control-plane-execution-plane]] — the higher-level separation
- [[concepts/capability-distribution]] — loading skills and plugins into an environment
- [[concepts/approval-gate]] — handling `requires_action`
- Original: [`docs/09-agents-api-environments.md`](../../../docs/09-agents-api-environments.md)
- Strands case: [`strands/04-harness-and-cli.md`](../../../strands/04-harness-and-cli.md)
