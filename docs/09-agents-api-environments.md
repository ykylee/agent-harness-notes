# 09. Agents API — Architecture and Environments

> Source: the official guides under `developers.openai.com/api/docs/guides/agents-api/`
> (`architecture`, `environments/openai-hosted`, `environments/self-hosted`, `environments/lifecycle`,
> `environments/files`, `environments/security`), read as **raw Markdown** by appending `.md` to each
> page URL. Extracted 2026-09-15.

## 1. The three pieces

| Piece | What it is |
|---|---|
| **Harness** | The OpenAI-hosted Codex instance that runs the model and tool loop and maintains the session |
| **Environment** | Where the agent runs commands, executes code, and works with files — a remote sandbox, your laptop, a Docker container, or an AWS Lambda function |
| **Application server** | Your code. Submits tasks, receives events, handles function tools. When you provide the environment, it also manages that lifecycle |

> "OpenAI runs the agent harness. Your application sends it work and receives results.
> Add an environment when the agent needs compute or files."

## 2. Three topologies

### (a) `environment.type: "none"` — no environment

For agents that answer questions or reach external services. The harness calls remote MCP tools
directly; function tools are handled by your code.

**What you lose without an environment:**
> the built-in Bash and apply-patch tools, workspace files, and executor MCPs are unavailable.

You can still simulate a filesystem and shell through your own function tools (the docs call this an
optional "virtual runtime").

### (b) `environment.type: "openai_hosted"`

OpenAI creates and manages a sandbox for the session. The harness runs commands in it directly.
You configure packages, files, and network access.

### (c) `environment.type: "self_hosted"`

For your infrastructure, private network, or custom software. Your code starts the environment and
connects an executor; the executor runs what the harness requests.
**You own provisioning, reconnection, shutdown, and preserving any files you need.**

## 3. OpenAI-hosted sandbox configuration

A Linux workspace with Python, Node.js, and command-line tools. The working directory is `/workspace`.

| Field | Purpose |
|---|---|
| `packages` | `python`, `system`, or `npm` lists. Pin versions when needed, e.g. `pandas==2.2.3` |
| `setup_commands` | Ordered shell commands run before the agent starts, e.g. `[{ "command": "mkdir -p reports" }]`. Each has its own optional `cwd`, defaulting to `/workspace` |
| `files` | Input files by Files API ID or inline base64 |
| `env` | String-valued environment variables. **Runtime-reserved names — including `PATH`, `CODEX_*`, and `OPENAI_API_KEY` — are rejected** |
| `skills`, `plugins`, `capability_directories` | Skills and plugins |
| `environment_template_id` | Reuse saved configuration. Omitted settings inherit the template; **network overrides cannot broaden its policy** |

**Ordering that matters:**
> Packages and input files are prepared **before** setup commands run.
> **A nonzero setup exit status prevents the agent from starting.**

Use a setup command to check required dependencies or files.
**Templates save configuration, not a running workspace.**

### Network access

| `network.access` | Behavior |
|---|---|
| `enabled` | Allow outbound access. Default unless you inherit a template policy |
| `disabled` | Block outbound access |
| `restricted` | Allow only the hosts in `allowed_domains` |

Restricted mode accepts **1–100 exact host names** such as `api.example.com`.
**No wildcards, protocols, paths, or ports.**
**Subdomains and redirect destinations need their own entries.**

Hosted **stdio** MCP servers currently require `enabled`.

### Verifying setup

The create-session response only means setup has *started*.
`GET /v1/agents/environments/{environment_id}` (using `session.environment.id`):

| Status | Meaning |
|---|---|
| `provisioning` | Setup is running |
| `connected` | Setup succeeded |
| `failed` | Read `environment.error` in the `agent.session.environment.failed` event |

**Wait for `connected` before adding or listing live files.**

### Expiry

> Connected sandboxes receive keep-alives, including between turns. If activity and keep-alives stop
> for **an hour**, the sandbox can be deleted. **This timeout isn't configurable.**

Delete the session when done to request cleanup. If deletion returns **`409`** while setup or
execution finishes, wait and retry **with a limit on attempts**.

> **Closing an event stream does not cancel the task.**

### Pricing

Hosted sandboxes use standard **container rates**; model usage is billed separately at the model's
API rates.

## 4. Files and artifacts

**File** = lives in the agent's environment. **Artifact** = a published copy of a file from an
OpenAI-hosted environment, downloadable **after the environment expires**.

| Environment | How to retrieve files |
|---|---|
| `self_hosted` | Your provider's file API or mounted filesystem |
| `openai_hosted` | The session Artifacts API, for files under `/workspace/outputs` |
| `none` | No filesystem — read output from session items |

> **Files from self-hosted environments are not published through the Artifacts API, including files
> under `/workspace/outputs`.** This asymmetry is easy to miss.

### Uploading

- At session creation: `environment.files`, each entry either
  `{ "type": "file_id", "file_id": "...", "path": "..." }` or
  `{ "type": "inline", "data": "<base64>", "path": "..." }`. **Both forms require a `path`**, an
  absolute destination under `/workspace`.
- After the environment connects: the environment Files API
  (`POST /v1/agents/environments/{id}/files`, same `HostedEnvironmentFileParam` body).

### Retrieving

Ask the agent to write under `/workspace/outputs`. OpenAI publishes those as **immutable artifacts
when the turn completes**. Identify a file by **turn ID + path**.

> The API downloads **one artifact per request**; there is no batch-download endpoint.
> For several files, ask the agent to bundle them into a ZIP under `/workspace/outputs`.

Artifacts **cannot be uploaded or edited** through the API. To publish a new version, have the agent
update the file and complete another turn. Deleting an artifact **leaves the file in the environment
intact**.

### Limits

| Operation | Limit |
|---|---|
| Files included when creating a session | 50 files per request |
| Inline upload | 5 MiB per file, measured **before** base64 encoding |
| Inline uploads in one creation request | 10 MiB total, before base64 |
| File copied from the Files API | 50 MiB per file |
| Published artifact | 200 MiB per file |
| Outputs published together | 500 MiB total |

## 5. Self-hosted lifecycle

### Starting

Create the session, start your compute, then connect the executor with the environment ID and an
**environment key**.

> Use **one component** to manage each session's environment. Store the mapping between session and
> provider compute. **Repeated or concurrent requests must not create duplicate environments.**

### Webhook-managed starting (start compute only when needed)

The API emits `agent.session.action_required` with `required_action.type: "environment_connection"`
**before waiting** for the executor.

**Handler (fast path)**
1. Verify the webhook signature
2. Queue connection requests only when `data.required_action.type` is `environment_connection`;
   also queue session failures
3. **Return a successful HTTP response only after queuing succeeds**

**Worker (slow path)**
1. Retrieve the session. Ignore deleted sessions and resolved actions
2. For a self-hosted session still needing a connection, start or reconnect its executor using
   `session.environment.id` and `session.environment.remote_url`
3. For a session that is still failed, **release its compute**

**Critical timing note:**
> Turn creation and `agent.session.in_progress` events arrive **too late** to start an offline executor.

A `function_call` required action needs a function result, not environment startup.

### Stopping

Keep compute running between turns for reuse, or allow a grace period after a turn ends.
Coordinate shutdown with incoming work — cancel a pending shutdown when a connection is requested or
execution starts, and recheck state before stopping.

> **An idle event alone is not a safe shutdown signal.** It can arrive when a connection request
> clears, before waiting input starts its turn.

### Connecting the executor

```bash
mkdir -p /workspace
npm install -g @openai/codex@alpha

codex exec-server \
  --remote "<session.environment.remote_url>" \
  --environment-id "<session.environment.id>"
```

Outbound access required: `https://api.openai.com` and `wss://codex-cloud-environments.chatgpt.com`.

## 6. Security

> **Agent-generated code can access the files, credentials, and network available to its environment.**

### Key separation (the most important rule)

| Key | Scopes | Where it lives |
|---|---|---|
| Application API key | `api.agents.read`, `api.agents.write`, `api.responses.write` (+ `api.vaults.read` / `api.vaults.write` for vaults) | **Outside** the environment |
| Environment key (`CODEX_API_KEY`) | Connecting environments **only** — "cannot authorize any other API action" | Inside the environment |

> **Agent-generated code can read the environment key.** That is acceptable precisely because the
> key's authority is limited to connecting environments. Your application API key must never be in
> the environment, in images, in source code, or in logs.

### Other measures

- **Isolate workloads** — run in isolated compute such as VMs; use separate environments for users or
  workloads that must not share data; create a dedicated OpenAI project per application
- **Restrict network access** — allow outbound traffic only to approved endpoints, including the
  executor's required hosts. Executor MCPs connect *from your environment*; remote MCPs connect *from
  OpenAI's service* and their endpoints must be reachable from there
- **Broker third-party access** — route requests through a credential broker that injects secrets into
  approved outbound requests. **Injecting a stored secret into the environment still exposes it to
  agent-generated code**

## 7. Troubleshooting (hosted sandbox)

| Problem | What to check |
|---|---|
| Setup fails | Inspect the environment-failure event; fix the package, input-file, or setup-command error before creating another session |
| A sandbox request is blocked | Check `network` and any hosts reached through redirects |
| A live file operation fails | Confirm the sandbox is `connected`. If it expired, create a new session and supply the inputs again |
| A status or file-list request returns `5xx` | Retry with increasing delays and a deadline. Keep the request ID if the error persists |
