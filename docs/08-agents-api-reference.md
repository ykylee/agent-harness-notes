# 08. Agents API Reference (from the OpenAPI Spec)

> **Authoritative source**: `openapi.yaml` in [`openai/openai-openapi`](https://github.com/openai/openai-openapi)
> (~3.5MB, entries tagged `Agents`). Extracted **directly from the spec**, not from guide pages.
> Extracted 2026-09-15. Reproduction steps at the bottom.

## 0. Calling convention

```bash
curl --no-buffer --fail-with-body https://api.openai.com/v1/agents/sessions \
  -H "OpenAI-Beta: agents=v1" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

- Base: `https://api.openai.com/v1`
- **The `OpenAI-Beta: agents=v1` header is required** (public beta)
- Required API key scopes: **`api.agents.read`**, **`api.agents.write`**, **`api.responses.write`**
  (plus `api.vaults.read` / `api.vaults.write` to manage vaults)
- SDK paths: `client.beta.agents.sessions.*` (JS/Python/Ruby), `client.Beta.Agents.Sessions.*` (Go),
  `client.beta().agents().sessions()` (Java)
- Streaming responses are `text/event-stream`; non-streaming are `application/json`

## 1. All endpoints (33)

### 1.1 Agents — reusable saved agents

| Method | Path | operationId |
|---|---|---|
| GET | `/agents` | `listAgents` |
| POST | `/agents` | `createAgent` |
| GET | `/agents/{agent_id}` | `retrieveAgent` |
| POST | `/agents/{agent_id}` | `updateAgent` |
| DELETE | `/agents/{agent_id}` | `deleteAgent` |

> **Note**: update is **`POST /agents/{agent_id}`**, not `PATCH`.

### 1.2 Sessions — running instances

| Method | Path | operationId |
|---|---|---|
| GET | `/agents/sessions` | `listAgentSessions` |
| POST | `/agents/sessions` | `createAgentSession` |
| GET | `/agents/sessions/{session_id}` | `retrieveAgentSession` |
| POST | `/agents/sessions/{session_id}` | `updateAgentSession` |
| DELETE | `/agents/sessions/{session_id}` | `deleteAgentSession` |

### 1.3 Session input and output

| Method | Path | operationId |
|---|---|---|
| GET | `/agents/sessions/{session_id}/events` | `listAgentSessionEvents` |
| POST | `/agents/sessions/{session_id}/events` | `createAgentSessionEvents` |
| GET | `/agents/sessions/{session_id}/items` | `listAgentSessionItems` |
| GET | `/agents/sessions/{session_id}/turns` | `listAgentSessionTurns` |
| GET | `/agents/sessions/{session_id}/turns/{turn_id}` | `retrieveAgentSessionTurn` |

> **`POST .../events` is the only input channel.** Messages, cancellation, and tool results all go
> through it.

### 1.4 Artifacts — files published by completed turns

| Method | Path | operationId |
|---|---|---|
| GET | `/agents/sessions/{session_id}/artifacts` | `listAgentSessionArtifacts` |
| GET | `/agents/sessions/{session_id}/artifacts/{artifact_id}` | `retrieveAgentSessionArtifact` |
| GET | `/agents/sessions/{session_id}/artifacts/{artifact_id}/content` | `retrieveAgentSessionArtifactContent` |
| DELETE | `/agents/sessions/{session_id}/artifacts/{artifact_id}` | `deleteAgentSessionArtifact` |

### 1.5 Subagents — read-only

| Method | Path | operationId |
|---|---|---|
| GET | `/agents/sessions/{session_id}/subagents` | `listAgentSessionSubagents` |
| GET | `/agents/sessions/{session_id}/subagents/{subagent_id}` | `retrieveAgentSessionSubagent` |
| GET | `/agents/sessions/{session_id}/subagents/{subagent_id}/items` | `listAgentSessionSubagentItems` |
| GET | `/agents/sessions/{session_id}/subagents/{subagent_id}/turns` | `listAgentSessionSubagentTurns` |
| GET | `.../subagents/{subagent_id}/turns/{turn_id}` | `retrieveAgentSessionSubagentTurn` |
| GET | `.../subagents/{subagent_id}/turns/{turn_id}/items` | `listAgentSessionSubagentTurnItems` |

> Subagents have **no create or delete endpoints.** The main agent creates them through tool calls;
> the API only lets you observe them.

### 1.6 Environments

| Method | Path | operationId |
|---|---|---|
| GET | `/agents/environments/{environment_id}` | `retrieveAgentEnvironment` |
| GET | `/agents/environments/{environment_id}/files` | `listAgentEnvironmentFiles` |
| POST | `/agents/environments/{environment_id}/files` | `createAgentEnvironmentFile` |
| GET | `/agents/environments/templates` | `listAgentEnvironmentTemplates` |
| POST | `/agents/environments/templates` | `createAgentEnvironmentTemplate` |
| GET | `/agents/environments/templates/{id}` | `retrieveAgentEnvironmentTemplate` |
| POST | `/agents/environments/templates/{id}` | `updateAgentEnvironmentTemplate` |
| DELETE | `/agents/environments/templates/{id}` | `deleteAgentEnvironmentTemplate` |

> Environments are created by sessions; there is **no endpoint to create one directly.**
> Only templates support full CRUD.

### 1.7 Vaults (under `/v1/vaults`, not `/v1/agents`)

| Method | Path | operationId |
|---|---|---|
| GET | `/vaults` | `listVaults` |
| POST | `/vaults` | `createVault` |
| GET | `/vaults/{vault_id}` | `retrieveVault` |
| DELETE | `/vaults/{vault_id}` | `deleteVault` |
| GET | `/vaults/{vault_id}/credentials` | `listVaultCredentials` |
| POST | `/vaults/{vault_id}/credentials` | `createVaultCredential` |
| GET | `/vaults/{vault_id}/credentials/{credential_id}` | `retrieveVaultCredential` |
| POST | `/vaults/{vault_id}/credentials/{credential_id}` | `rotateVaultCredential` |
| DELETE | `/vaults/{vault_id}/credentials/{credential_id}` | `deleteVaultCredential` |

Vaults hold MCP credentials for connections made **from OpenAI**. They live outside the `Agents`
tag, which is why a scan of `/agents` paths alone misses them. Details in
[10-agents-api-tools.md](10-agents-api-tools.md#3-vaults).

### 1.8 `HostedEnvironmentFileParam` — the environment-files body

`POST /agents/environments/{environment_id}/files` takes this discriminated union (also used by
`environment.files` at session creation):

```ts
// discriminator: type
{ type: "file_id", file_id: string, path: string }   // path = absolute destination inside /workspace
{ type: "inline",  data: string,    path: string }   // data = standard-base64 file contents
```

The response is an `EnvironmentFileResource`:

```ts
{ object: "agent.environment.file", environment_id: string, path: string, size_bytes: number }
```

Size limits are in [09-agents-api-environments.md](09-agents-api-environments.md#4-files-and-artifacts).

## 2. `POST /agents/sessions` — create a session

### Request (`CreateAgentSessionParams`)

| Field | Type | Required | Description |
|---|---|:---:|---|
| `environment` | `EnvironmentParam` | ✅ | An inline execution environment or a template reference |
| `agent` | `SessionAgentConfigParam` | | With `agent_id`, supplied fields **override** the saved agent. Without `agent_id`, `model` is required |
| `agent_id` | `string` (≤64) | | ID of a saved reusable agent. Omit `agent` to use its configuration unchanged |
| `input` | `string` \| `InputMessageParam[]` | conditional | Initial input. A string is shorthand for a single user message |
| `metadata` | `object` | | Up to 16 pairs, keys ≤64 chars, values ≤512 chars |
| `vault_ids` | `string[]` | | IDs of vaults made available to the session |
| `stream` | `boolean` (default `false`) | | Stream session events as SSE |

**When `input` becomes required** (spec wording):
> When `environment.type` is `none`, or when `stream` is `true` for an environment that is not
> `self_hosted`; optional for self-hosted and non-streaming execution environments.

### Responses

- `201` + `SessionResource` (JSON)
- `201` + a `SessionEvent` stream (`text/event-stream`, when `stream: true`)
- Errors: `400 401 403 404 409 500 503` — all `ErrorResponse-2`

### `SessionAgentConfigParam`

| Field | Type | Description |
|---|---|---|
| `model` | `string` | The requested model name is preserved as given |
| `instructions` | `string \| null` | Additional instructions **appended to the agent's default base instructions** |
| `reasoning` | `ReasoningParam \| null` | Omit to keep current settings; `null` resets to the model's default effort |
| `text` | `TextParam \| null` | Configuration for generated text |
| `service_tier` | `ServiceTierParam \| null` | Service tier for model requests |
| `multi_agent` | `MultiAgentConfigCurrentParam \| null` | Subagent configuration |
| `tools` | `AgentToolConfigParam[] \| null` | Omit to inherit; `null` clears them |

> **Merge rules (spec wording)**: omitted fields inherit from `agent_id`. Supplied objects and
> arrays **replace the whole field**. `null` resets nullable fields.

### `EnvironmentParam` (discriminator: `type`)

**`none`** — run the agent with no execution environment
```json
{ "type": "none" }
```

**`openai_hosted`**
| Field | Description |
|---|---|
| `environment_template_id` | A reusable template applied **before** inline session configuration. Omitted fields inherit the template. **Network overrides cannot broaden the template's policy** |
| `packages` | Packages to install (default: empty lists) |
| `setup_commands` | Ordered, **confidential** setup commands, max 16. **Command bodies are never returned** |
| `network` | Network access policy (default: enabled) |
| `env` | Environment variables, max 1024 (keys ≤256 chars) |
| `capability_directories` | Directories exposing capabilities to the agent, max 16384 |
| `skills` | Referenced by ID or provided as inline ZIPs, max **200** |
| `plugins` | Inline ZIPs, max **32** |
| `files` | Files available before the agent starts, max **50** |

**`self_hosted`**
| Field | Required | Description |
|---|:---:|---|
| `workspace_directory` | ✅ | **Absolute** project directory inside the self-hosted environment |
| `capability_directories` | | Capability directories |

The response-side `EnvironmentResourceSelfHosted` additionally carries `remote_url` and `id` —
feed both into `codex exec-server --remote <remote_url> --environment-id <id>`.

### `MultiAgentConfigCurrentParam`

| Field | Required | Default | Description |
|---|:---:|---|---|
| `enabled` | ✅ | — | Enable subagent tools |
| `max_concurrent_subagents` | | **6** | Concurrency cap (excluding the coordinator), minimum 1 |

### `AgentToolConfigParam` (discriminator: `type`, 5 kinds)

| type | Purpose |
|---|---|
| `function` | Custom function. Requires `name`, `description`, `parameters` (JSON Schema); plus `defer_loading` (default false) |
| `mcp` | MCP server |
| `web_search` | Web search |
| `tool_search` | Discover tools lazily (saves tokens) |
| `programmatic_tool_calling` | Programmatic parallel calling |

**`defer_loading: true` on a `function`** → its definition is not preloaded and is discovered via
`tool_search`. Saves context.

**Key `mcp` fields**
| Field | Description |
|---|---|
| `server_label` | Label identifying the server in tool calls |
| `transport` | `McpTransportConfigParam` |
| `credential_id` | Vault credential. Optional when exactly one attached credential matches the server URL |
| `allowed_tools` | Tools the agent may call. **All server tools are allowed when omitted** |
| `required` | Whether the server must initialize before the first turn (default `false`) |
| `request_metadata` | Metadata included with requests |
| `connection_origin` | Selects where outbound MCP HTTP connections originate |

### `CreateSessionInputParam`

```json
// Shorthand
"input": "Create tree.py and run it."

// Full form
"input": [{
  "type": "message",
  "role": "user",
  "content": [
    { "type": "input_text",  "text": "..." },
    { "type": "input_image", "image_url": "https://..." }
  ]
}]
```

`role` accepts **only `user`**.

## 3. `SessionResource`

```ts
{
  id: string,
  object: "agent.session",
  created_at: number,           // Unix seconds
  last_active_at: number,
  status: "idle" | "in_progress" | "requires_action" | "failed",
  required_actions: SessionRequiredActionResource[],   // max 2000
  error: string | null,
  agent: SessionAgentResource,
  environment: EnvironmentResource,                    // none | openai_hosted | self_hosted
  vault_ids: string[],
  metadata: Record<string, string>,
  usage: TokenUsageResource | null,                    // best effort, may change
}
```

### `status` meanings (spec wording)

| Value | Meaning |
|---|---|
| `idle` | No turn in progress; ready for input. **A hosted environment may still be provisioning** |
| `in_progress` | Processing a turn |
| `requires_action` | Waiting for one or more required actions |
| `failed` | The session failed |

> Do not treat `idle` alone as success. The official guide also says to inspect both the status and
> the agent's output.

### `required_actions` (discriminator: `type`)

| type | How to handle |
|---|---|
| `function_call` | Run the function and return the result using `turn_id` + `call_id` |
| `environment_connection` | Establish the executor connection using `environment_id` |

### `TokenUsageResource`

```ts
{
  input_tokens: number,
  input_tokens_details: InputTokensDetailsResource,     // includes cached
  output_tokens: number,
  output_tokens_details: OutputTokensDetailsResource,   // includes reasoning
  total_tokens: number,
}
```

> **Cached tokens are included in `input_tokens`**, and **reasoning tokens are included in
> `output_tokens`**. These are breakdowns, not additions.

## 4. `TurnResource`

```ts
{
  id: string,
  object: "agent.session.turn",
  session_id: string,
  agent_id: string,
  subagent_id: string | null,   // null = executed by the main coordinator
  status: "queued" | "in_progress" | "waiting" | "completed" | "failed" | "cancelled",
  created_at: number,
  started_at: number | null,
  completed_at: number | null,
  error: SessionTurnErrorResource | null,   // non-null only when failed
  usage: TokenUsageResource | null,
}
```

`waiting` = waiting for external input.

For subagent turns, `created_at` uses the start time, falling back to the completion time and then
to the subagent opening time when earlier timestamps are unavailable.

## 5. Turn failure codes — `SessionTurnErrorCodeResource` (17)

| Code | Meaning |
|---|---|
| `context_length_exceeded` | Exceeds the model's context window |
| `session_budget_exceeded` | The session reached its usage budget |
| `usage_limit_exceeded` | The organization hit a usage, plan, or billing limit |
| `credit_balance_exhausted` | No API credits remaining |
| `rate_limit_exceeded` | Rate limit exceeded |
| `server_overloaded` | The model service is temporarily overloaded |
| `cyber_policy` | Rejected by a safety policy |
| `connection_failed` | Could not connect to the model service |
| `server_error` | Unexpected error from the model service |
| `authentication_error` | Invalid credentials or insufficient access |
| `invalid_request` | Invalid input or configuration |
| `resource_not_found` | The requested model or resource is unavailable |
| `sandbox_error` | Could not complete in the execution environment |
| `executor_version_incompatible` | **The executor must be upgraded** |
| `active_turn_not_steerable` | Cannot accept more input while a request is running |
| `request_timeout` | Timed out before the model service responded |
| `internal_error` | Unexpected internal error |

> Separate the retryable family (`server_overloaded`, `rate_limit_exceeded`, `connection_failed`,
> `request_timeout`) from the ones requiring a configuration fix (`invalid_request`,
> `authentication_error`, `executor_version_incompatible`).

## 6. `POST /agents/sessions/{id}/events` — the input channel

### Request (`CreateSessionEventsParams`)

```json
{ "events": [ /* SessionInputParam, max 16384 */ ] }
```

### `SessionInputParam` (discriminator: `type`, 3 kinds)

**Send a message / steer**
```json
{
  "type": "agent.session.input.message",
  "input": [{
    "role": "user",
    "content": [{ "type": "input_text", "text": "Your message" }]
  }]
}
```
> **Steers** an active turn; **starts a new turn** on an idle session (conversation context preserved).

**Cancel**
```json
{ "type": "agent.session.input.cancel" }
```
> Stops only the active turn. The session and prior work remain. (Distinct from deleting the session.)

**Return a tool result**
```json
{ "type": "agent.session.input.tool_result", ... }
```
> The response to a `function_call` in `required_actions`. Matched via `turn_id` + `call_id`.

## 7. Streaming events — `SessionEvent` (30, discriminator: `type`)

### Session lifecycle
```
agent.session.created
agent.session.in_progress
agent.session.idle
agent.session.requires_action
agent.session.failed
error
```

### Environment
```
agent.session.environment.pending
agent.session.environment.connected
agent.session.environment.ready
agent.session.environment.disconnected
agent.session.environment.failed
```

### Turn lifecycle
```
agent.session.turn.created
agent.session.turn.in_progress
agent.session.turn.completed
agent.session.turn.failed
agent.session.turn.cancelled
```

### Turn content streaming
```
agent.session.turn.item.added
agent.session.turn.item.done
agent.session.turn.content_part.added
agent.session.turn.content_part.done
agent.session.turn.output_text.delta
agent.session.turn.output_text.done
agent.session.turn.reasoning_summary_part.added
agent.session.turn.reasoning_summary_part.done
agent.session.turn.reasoning_summary_text.delta
agent.session.turn.reasoning_summary_text.done
```

### Command output
```
agent.output.command_execution_output.delta
```
> This one alone lives in the **`agent.output.*`** namespace rather than `agent.session.*`.
> Easy to miss in a parser.

### Subagents
```
agent.session.subagent.created
agent.session.subagent.active
agent.session.subagent.closed
```

### The error event (`SessionEventError`)

```json
{
  "type": "error",
  "event_id": "event_123",
  "session_id": "sess_123",
  "error": {
    "type": "server_error",
    "code": null,
    "message": "The session failed due to an internal server error.",
    "param": null
  }
}
```
> The spec states that `SessionErrorResource` has "the same public fields as Responses API
> streaming errors."

> The stream **stays open across idle events**, so you don't miss queued work.

## 8. Turn items — `SessionTurnItemResource` (14)

```
message                  reasoning
function_call            function_call_output
agent_message            mcp_call
web_search_call          command_execution
create_subagent_call     send_subagent_input_call
resume_subagent_call     wait_for_subagents_call
interrupt_subagent_call  close_subagent_call
```

The last six are **multi-agent coordination actions**. Seeing them in the stream means delegation
is happening.

## 9. Artifacts

```ts
SessionArtifactResource = {
  id: string,
  object: "agent.session.artifact",
  session_id: string,
  environment_id: string,
  turn_id: string,          // the completed turn that published this artifact
  path: string,             // the original absolute path in the execution environment
  size_bytes: number,
  created_at: number,
}
```

> **"An immutable file published by a completed hosted session turn."** This is the official way to
> retrieve what the agent produced (reports, CSVs, screenshots). Fetch contents from
> `GET .../artifacts/{id}/content`.

## 10. Pagination (common to every list endpoint)

**Query parameters**: `limit` (≥1), `order` (`asc`/`desc`, default `desc`), `after` (cursor).
`GET /agents/sessions` also takes an `agent_id` filter; `GET .../artifacts` takes `environment_id`.

**Response envelope**
```ts
{
  object: "list",
  data: T[],              // max 2000
  first_id: string | null,
  last_id: string | null,
  has_more: boolean,
}
```

SDK helpers: `hasNextPage()` / `getNextPage()`.

## 11. Minimal working examples

### Create a session with streaming (curl)

```bash
curl --no-buffer --fail-with-body https://api.openai.com/v1/agents/sessions \
  -H "OpenAI-Beta: agents=v1" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {
      "model": "gpt-6-astra",
      "instructions": "Write clean code, run it, and report the actual output."
    },
    "environment": { "type": "openai_hosted" },
    "input": "Create tree.py, a Python script that prints a readable tree of the files in the current directory. Run it and show me the output.",
    "stream": true
  }'
```

### Python

```python
from openai import OpenAI

with OpenAI() as client:
    with client.beta.agents.sessions.create(
        agent={
            "model": "gpt-6-astra",
            "instructions": "Write clean code, run it, and report the actual output.",
        },
        environment={"type": "openai_hosted"},
        input="Create tree.py ... Run it and show me the output.",
        stream=True,
    ) as events:
        for event in events:
            print(event.to_json(indent=None), flush=True)
```

### Multi-agent (JavaScript)

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const events = await client.beta.agents.sessions.create({
  agent: {
    model: "gpt-6-astra",
    instructions: "Delegate each release to a separate subagent. ...",
    multi_agent: { enabled: true, max_concurrent_subagents: 2 },
  },
  environment: { type: "none" },
  input: "Release A: ... Release B: ...",
  stream: true,
});

for await (const event of events) {
  console.log(JSON.stringify(event));
}
```

### Follow-up, cancellation, and retrieving results

```javascript
// Continue the conversation (steers an active turn, or starts a new one when idle)
await client.beta.agents.sessions.events.create(sessionId, {
  events: [{
    type: "agent.session.input.message",
    input: [{ role: "user", content: [{ type: "input_text", text: "Your message" }] }],
  }],
});

// Cancel the active turn (the session survives)
await client.beta.agents.sessions.events.create(sessionId, {
  events: [{ type: "agent.session.input.cancel" }],
});

// Retrieve saved work
const items = await client.beta.agents.sessions.items.list(sessionId, {
  order: "asc",
  limit: 100,
});

// Which agent ran this command?
const turn = await client.beta.agents.sessions.turns.retrieve(
  command.turn_id, { session_id: sessionId }
);
console.log(turn.subagent_id);   // null = the main coordinator
```

### Self-hosted environment

```json
{
  "agent": { "model": "gpt-6-astra", "instructions": "..." },
  "environment": { "type": "self_hosted", "workspace_directory": "/workspace" }
}
```

```bash
# Use environment.remote_url / environment.id from the response
codex exec-server \
  --remote "<session.environment.remote_url>" \
  --environment-id "<session.environment.id>"
```

## 12. Subagent inheritance rules

**Inherited**
- Configured MCP tools, their credentials, and `allowed_tools`
- Web search settings
- The environment's files and command-line tools

**Not inherited**
- **Subagents cannot use function tools**

**When to delegate** (official guidance):
> Use subagents for independent tasks — reviewing separate documents, investigating different
> causes of a failure. Keep dependent steps and short tasks in the main agent.

## 13. Practical checklist

- [ ] Confirm the `OpenAI-Beta: agents=v1` header is present (public beta)
- [ ] **Store `session_id` in your application database** — recover via retrieve after a restart or disconnect
- [ ] When `status` is `requires_action`, nothing proceeds until every required action is handled
- [ ] Never treat `agent.session.idle` alone as success — check the turn status and the output
- [ ] `agent.output.command_execution_output.delta` is in a different namespace — watch your parser branches
- [ ] `agent`/`agent_id` merge rules: objects and arrays **replace the whole field**, `null` resets, omission inherits
- [ ] When mixing `environment_template_id` with inline settings, **network policy cannot be broadened**
- [ ] `setup_commands` bodies are never returned in responses — manage them separately
- [ ] `usage` is best effort and **may change later**. Be careful using it for billing
- [ ] Prepare an upgrade path for `executor_version_incompatible` (self-hosted `@openai/codex@alpha`)
- [ ] Retrieve produced files from **`artifacts`**, not `items`
- [ ] To stop work, send `agent.session.input.cancel` — not a session delete

## 14. Reproduction

```bash
S=/tmp/openai-spec && mkdir -p $S
curl -sL https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml -o $S/openapi.yaml

# Endpoint list
grep -nE '^  /agents' $S/openapi.yaml

# Open one schema
L=$(grep -n '^    CreateAgentSessionParams:' $S/openapi.yaml | cut -d: -f1)
sed -n "${L},$((L+70))p" $S/openapi.yaml

# All event types
L=$(grep -n '^    SessionEvent:' $S/openapi.yaml | cut -d: -f1)
sed -n "${L},$((L+130))p" $S/openapi.yaml | grep -E '^        - agent\.|^        - error'
```

## 15. Reading the official docs as Markdown

Every documentation page serves a raw Markdown version — **append `.md` to the page URL**:

```bash
curl -sL https://developers.openai.com/api/docs/guides/agents-api/overview.md
curl -sL https://developers.openai.com/api/docs/guides/agents-api/tools/mcp.md
```

This returns the source text with all code samples intact, rather than a rendered page.
The docs also point to `/llms.txt` as a complete index.

## 16. Related documents

| Topic | Document |
|---|---|
| Concepts and scenarios | [05-agents-api.md](05-agents-api.md) |
| Architecture, environments, files, security | [09-agents-api-environments.md](09-agents-api-environments.md) |
| Functions, MCP, vaults, plugins | [10-agents-api-tools.md](10-agents-api-tools.md) |
| Webhooks, observability, tracing, cost | [11-agents-api-operations.md](11-agents-api-operations.md) |
