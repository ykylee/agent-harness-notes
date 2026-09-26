# 10. Agents API — Tools (Functions, MCP, Vaults, Plugins)

> Source: the official guides `agents-api/tools/{functions,mcp,vaults,plugins}`, read as raw
> Markdown. Extracted 2026-09-15.
> Drift-checked against `openai/openai-openapi@d983890f77` (2026-09-26); changes marked *(2026-09-26)*.

## 1. Function tools

Your application code, called by the agent.

> Your handler can run in an application server, a worker, or an environment you control.
> **Attaching an environment to a session does not automatically run function tools there.**

### Defining

Add to `agent.tools`: `name`, `description`, and a JSON Schema for the arguments.

### Handling a call — the three-step loop

1. The session emits **`agent.session.requires_action`**. Read pending calls from
   `event.session.required_actions`. (You can also just retrieve the session and read
   `session.required_actions` — no streaming required.)
2. Run the named function with the supplied arguments.
3. Send **`agent.session.input.tool_result`** to the session events endpoint, copying `turn_id` and
   `call_id` from the pending action.

| Outcome | Fields |
|---|---|
| Success | `success: true`, `output` as a string or a supported content array. **Serialize JSON objects to strings** |
| Failure | `success: false`, `error` message the agent can use |

> **Critical distinction**: use `required_actions` to decide which calls need results —
> "a `function_call` item in session history alone does not establish that a result is pending."

### Recovering after a disconnect

Retrieve the session to find pending actions. If you already ran the function, submit the saved
result with **the same `turn_id` and `call_id`**.

> For functions with side effects, **store results durably by session, turn, and call ID.**
> If execution might have succeeded but no result was saved, check the outcome before running again.

### Deferred loading

Functions load eagerly by default. Set `defer_loading: true` on the definition **and** include
`{ "type": "tool_search" }` in `agent.tools`. Discovered definitions are appended at the end of the
conversation, which preserves the earlier prefix for prompt-cache reuse.

## 2. MCP connections

The Agents API discovers the tools, calls the server, and returns results.
**Your application does not handle each call.**

| Connection | Where it runs | Requires an environment |
|---|---|:---:|
| HTTP with `connection_origin: "service"` (default) | OpenAI | No |
| HTTP with `connection_origin: "environment"` | Your session's environment | Yes |
| stdio | A process in your session's environment | Yes |

### From OpenAI (default)

Add an HTTP MCP server to `agent.tools`. The server must be reachable from OpenAI.
Works with or without an environment.

### From your environment

> A `localhost` URL refers to the session's environment. **If you omit `connection_origin`, OpenAI
> makes the connection instead** — a silent misconfiguration worth guarding against.

For a self-hosted environment, connect the executor before the agent uses these tools.

### stdio

The executor starts the server process. Install the server and its dependencies in the environment first.

- **`command` and an absolute `cwd` are required**; `args` is optional
- **Omit `connection_origin`**
- For OpenAI-hosted stdio MCPs, omit the network policy or set it to `enabled`.
  **`disabled` and `restricted` are not supported for these connections**

### Authentication

| Source | How | Constraint |
|---|---|---|
| **HTTP, one session** | `transport.authorization` or `transport.headers` at session creation | Values are encrypted and **omitted from the returned session resource** |
| **HTTP, reusable** | A [vault](#3-vaults) attached via `vault_ids` | **Vaults apply only to connections from OpenAI.** Credentials match the server URL; use `credential_id` when several match |
| **stdio** | Supply values in the environment, list names in `transport.env_vars` | **These values can be read by code running in the environment.** Self-hosted sessions do not accept inline values in `transport.env` |

Rules:
- Use **one source** for `Authorization` — inline configuration *or* a matching vault credential.
  Other headers can accompany vault authentication
- **Environment-origin HTTP does not use vault credentials** — use inline auth or a trusted proxy
- Keep secrets out of reusable agent definitions, plugin archives, and logs

### Access control and startup

- `allowed_tools` — limit which tools the agent can discover and call
- `required: true` — **fail the turn** if the server cannot initialize (initialization is optional by default)

### Troubleshooting

If a required server cannot initialize, inspect the error in `agent.session.turn.failed`.
For stdio servers, also check the MCP process logs.

| Area | Check |
|---|---|
| Network access | The URL and `connection_origin`. For environment connections, that the executor is connected and can reach the server |
| Credentials | The token or headers. For a vault, that the credential matches the server URL |
| Executable and dependencies | That the configured command runs inside the environment |
| Working directory | An existing absolute `cwd` for an inline stdio configuration |

## 3. Vaults

> A vault stores credentials for **MCP connections from OpenAI**. Attach it to a session so the agent
> can use authenticated tools **without receiving the secret values.**

For connections from your environment, use the other MCP authentication options instead.

### Permissions

| Scope | Grants |
|---|---|
| `api.vaults.read` | List and retrieve vaults and credentials |
| `api.vaults.write` | Create, update, or delete them |

### Endpoints

| Method | Path | operationId |
|---|---|---|
| GET | `/vaults` | `listVaults` |
| POST | `/vaults` | `createVault` |
| GET | `/vaults/{vault_id}` | `retrieveVault` |
| DELETE | `/vaults/{vault_id}` | `deleteVault` |
| GET | `/vaults/{vault_id}/credentials` | `listVaultCredentials` |
| POST | `/vaults/{vault_id}/credentials` | `createVaultCredential` |
| GET | `/vaults/{vault_id}/credentials/{credential_id}` | `retrieveVaultCredential` |
| POST | `/vaults/{vault_id}/credentials/{credential_id}` | `rotateVaultCredential` — now "Update a vault credential" *(2026-09-26)* |
| DELETE | `/vaults/{vault_id}/credentials/{credential_id}` | `deleteVaultCredential` |

> These sit under `/v1/vaults`, **not** under `/v1/agents` — which is why they were missed in the
> first pass over the `Agents`-tagged endpoints.

### Schemas

```ts
CreateVaultParams = {
  name: string,                       // trimmed; 1–256 UTF-8 bytes after trimming
  metadata?: Record<string,string> | null,  // e.g. application or team identifier
}

CreateVaultCredentialParams = {
  name: string,                       // required, same trimming rule
  auth: CreateVaultCredentialAuthParam,   // required
}

// (2026-09-26) update body — was rotate-only with `auth` required
RotateVaultCredentialParams = {
  auth?: RotateVaultCredentialAuthParam,  // replacement values for the existing auth method
  metadata?: Record<string,string>,       // ≤16 pairs; replaces the whole map; {} clears it
}                                         // at least one of auth or metadata

// discriminator: type
CreateVaultCredentialAuthParam = mcp_oauth | static_bearer
```

`mcp_server_url` binds a credential to that server.
**Retrieving a vault or credential does not return its secret values.**

### OAuth credentials

Your application handles the provider's authorization and consent flow, then stores the grant with
`auth.type: "mcp_oauth"`:

- `expires_at` — the access token's expiry as an **RFC 3339** timestamp, if known
- Include `refresh` to let the Agents API refresh the token
- Token endpoint auth methods: **`none`**, **`client_secret_basic`**, **`client_secret_post`**

If an expired token cannot be refreshed, supply a valid replacement.
**Token expiry does not delete the credential or its vault.**

### Rotating and deleting

Updating a credential replaces its token **without changing its ID, authentication type, or server URL.**
*(2026-09-26: the same endpoint can now update `metadata` alone — `auth` is no longer required; supply at
least one of `auth` or `metadata`. The operationId is still `rotateVaultCredential`.)*

> Supplying a new access token **without** an expiry **clears the stored expiry**; an explicit `null`
> also clears it. Include `expires_at` when the replacement token expires.

> **Deleting stored credentials does not revoke the original tokens with their providers or stop a
> running session.** Your application handles provider-side revocation and session cancellation.

## 4. Plugins

> A plugin packages **skills, MCP configuration, or both.**

### Packaging

```
docs-helper/
├── .codex-plugin/
│   └── plugin.json        # manifest: declares skill dirs and MCP config
├── .mcp.json              # plugin-format MCP config (differs from agent.tools)
└── skills/
    └── docs-search/
        └── SKILL.md
```

> Paths resolve from the plugin root. They **must start with `./`, stay inside the plugin, and
> contain no `..` components.**

Note the format split: **`.mcp.json` uses the plugin format, which differs from `agent.tools`.**

### Registering in a self-hosted sandbox

Copy the plugin into the environment and add its **absolute path** to
`environment.capability_directories`. Select the **plugin root** — the directory containing
`.codex-plugin/plugin.json`.

> For multiple plugins, list each root. **A parent directory can discover nested skills, but does not
> load every child plugin's MCP configuration.**

### Uploading to an OpenAI-hosted sandbox

Supply **one ZIP per plugin** in `environment.plugins`. Each ZIP must contain **one plugin folder**
with `.codex-plugin/plugin.json` inside it.
**The request's name and description must match the manifest.**

### Reusing across sessions

Create an environment template with the plugin list, then set `environment.environment_template_id`
on later sessions. Omitting `environment.plugins` inherits the template's list; supplying one replaces it.

> Each session gets its own environment; **the root agent and its subagents share it.**

### Authenticating plugin MCP servers

| Transport | Mechanism |
|---|---|
| HTTP | `bearer_token_env_var` reads an environment variable and sends its value as a bearer token. Other `http_headers` values are **literal**; **`env_http_headers` is not supported** |
| stdio | `env_vars` lists environment variables passed to the server process. Install the executable and dependencies in the environment. A **relative `cwd` resolves from the plugin root** |

Plugin MCP connections run **from the session's environment**. Keep secrets out of plugin files and archives.
