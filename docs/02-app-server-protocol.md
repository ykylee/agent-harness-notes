# 02. The Codex App Server Protocol (Core)

> Sources: the official docs at <https://developers.openai.com/codex/app-server>
> (→ learn.chatgpt.com/docs/app-server), the OpenAI engineering blog (2026-02-04), and
> **the schemas generated in the `openai/codex` repository**
> (`codex-rs/app-server-protocol/schema/`). Where they disagree, the generated schemas are authoritative.

## 1. Basic shape of the protocol

**"JSON-RPC lite"** — stated directly in a footnote of the blog post:

> It keeps the request/response/notification shape, but **omits** the `"jsonrpc": "2.0"` header
> and is framed as **JSONL over stdio** rather than strict JSON-RPC 2.0.

Three message kinds:

| Kind | Shape | Direction |
|---|---|---|
| Request | `{ id, method, params }` | client→server, **and server→client** |
| Response | `{ id, result }` or `{ id, error }` | opposite of the request |
| Notification | `{ method, params }` (no id) | mostly server→client |

## 2. Transports

| Transport | Status | Notes |
|---|---|---|
| **stdio** | default | Newline-delimited JSON (JSONL). Single client. Used by the VS Code extension and the Python SDK |
| **WebSocket** | experimental | `ws://` / `wss://`, optional authentication. Multiple clients |
| **Unix socket** | supported | Standard HTTP upgrade handshake |
| **off** | — | No local transport exposed |

`--listen` accepts exactly: **`stdio://` (the default)**, `unix://`, `unix://PATH`, `ws://IP:PORT`, `off`
(`AppServerTransport::DEFAULT_LISTEN_URL = "stdio://"`).

> **There is no default WebSocket port.** The listener exists only when you pass an explicit
> `ws://IP:PORT`. A secondary source claiming a default of `127.0.0.1:9090` is not supported by the
> repository.

Health probes `/readyz` and `/healthz` are registered as routes on the WebSocket listener.

WebSocket hardening, verified in `app-server-transport/src/transport/websocket.rs`:
- **Any request carrying an `Origin` header is rejected** (`reject_requests_with_origin_header`
  middleware) — CSRF defense, since a browser cannot suppress `Origin`
- Binds **localhost only**; the startup notice suggests SSH port-forwarding for remote access
- A **non-loopback listener refuses to start without auth**: "refusing to start non-loopback websocket
  listener {addr} without auth; configure `--ws-auth capability-token` or `--ws-auth signed-bearer-token`"

In hosted environments (such as Codex Web), the container's stdin/stdout are tunneled over a
persistent connection (WebSocket-like). In other words it "behaves like stdio even if it isn't a
literal local pipe."

## 3. Handshake

The client must send **exactly one `initialize` before any other method**, and every request
before initialization completes is rejected.

```json
{
  "method": "initialize",
  "id": 0,
  "params": {
    "clientInfo": {
      "name": "codex_vscode",
      "title": "Codex VS Code Extension",
      "version": "0.1.0"
    },
    "capabilities": {
      "experimentalApi": true
    }
  }
}
```

Server response (`InitializeResponse`, per the generated schema):

```json
{
  "id": 0,
  "result": {
    "userAgent": "codex_vscode/0.94.0-alpha.7 (Mac OS 26.2.0; arm64) vscode/2.4.22 (codex_vscode; 0.1.0)",
    "codexHome": "/Users/you/.codex",
    "platformFamily": "unix",
    "platformOs": "macos"
  }
}
```

| Field | Meaning |
|---|---|
| `userAgent` | UA string assembled by the server |
| `codexHome` | Absolute path to the server's `$CODEX_HOME` |
| `platformFamily` | `"unix"` / `"windows"` |
| `platformOs` | `"macos"` / `"linux"` / `"windows"` |

The client then acknowledges with a notification:

```json
{ "method": "initialized" }
```

> `ClientNotification` has **exactly one variant: `initialized`**.

### `InitializeCapabilities` (capabilities declared by the client)

```ts
type InitializeCapabilities = {
  experimentalApi: boolean,               // opt into experimental methods/fields
  requestAttestation: boolean,            // opt into attestation/generate (x-oai-attestation)
  mcpServerOpenaiFormElicitation?: boolean, // legacy opt-in for the openai/form MCP extension
  optOutNotificationMethods?: string[] | null, // notification methods to suppress on this connection (e.g. "thread/started")
  extensions?: Record<string, JsonValue> | null, // MCP extension settings
}
```

Experimental features are exposed **only when you opt in with `experimentalApi: true`**.

## 4. Conversation primitives — Thread / Turn / Item

Designing an API for an agent loop is hard because the user↔agent interaction is not a simple
request/response: one request unfolds into a **structured sequence of actions**. Hence three
primitives with clear boundaries and lifecycles:

### Item — the atomic unit of input/output

Its lifecycle is **explicit**:

```
item/started  →  item/*/delta (0..N)  →  item/completed
```

Clients render immediately on `started`, apply increments on `delta`, and finalize with the
terminal payload on `completed`.

`ThreadItem` `type` values (per the generated `v2/ThreadItem.ts`):

| type | Key fields |
|---|---|
| `userMessage` | `content: UserInput[]`, `clientId` |
| `hookPrompt` | `fragments` |
| `agentMessage` | `text`, `phase`, `memoryCitation`, `delivery`, `questions` |
| `reasoning` | `summary[]`, `content[]` |
| `plan` | `text` |
| `commandExecution` | `command`, `cwd`, `processId`, `source`, `status`, `commandActions[]`, `aggregatedOutput`, `exitCode`, `durationMs`, `pluginId`, `scriptPath` |
| `fileChange` | `changes: FileUpdateChange[]`, `status` |
| `mcpToolCall` | `server`, `tool`, `status`, `arguments`, `appContext`, `readOnlyHint`, `result`, `error`, `durationMs` |
| `dynamicToolCall` | `namespace`, `tool`, `arguments`, `status`, `contentItems`, `success`, `durationMs` |
| `functionCallOutput` | `name`, `namespace`, `output` |
| `collabAgentToolCall` | `tool`, `status`, `senderThreadId`, `receiverThreadIds[]`, `prompt`, `model`, `reasoningEffort`, `agentsStates` |
| `subAgentActivity` | `kind`, `agentThreadId`, `agentPath` |
| `webSearch` / `imageView` / `imageGeneration` / `sleep` | Dedicated payloads |
| `enteredReviewMode` / `exitedReviewMode` | `review` |
| `contextCompaction` | — |

> `commandActions` on `commandExecution` is a **best-effort parse of a shell command that may be
> several commands piped together**. Use it in the UI to explain what a command will do.

### Turn — one unit of agent work started by user input

Begins when the client submits input, ends when the agent finishes producing outputs for it.
It is the **unit of interruption and rollback**, and contains a sequence of items.

### Thread — the durable container for a conversation

Holds multiple turns; can be created, resumed, forked, and archived, with persisted history.

**Unloading is time-based and configurable.** From `config_toml.rs`:

> "Seconds a thread must have no subscribers and no activity before app-server unloads it.
> **Defaults to 60**; zero unloads immediately. Changes require a server restart."
> — `thread_unload_delay_secs`

The trigger requires **both** conditions: the unload target is
`max(has_no_subscribers_since, is_inactive_since) + delay`. Activity or a new subscriber resets it.

> A secondary source describing a *30-minute* idle unload is wrong; the default is **60 seconds**.

Separately, loaded threads are also evicted by **capacity** — `V2Residency` keeps an LRU
`VecDeque<ThreadId>` bounded by `effective_agent_max_threads`. Time-based unload and capacity-based
eviction are two different mechanisms.

## 5. A typical turn

```
client → initialize                        server → result
client → initialized (notification)
client → thread/start                      server → thread/started (notification)
                                           server → result { thread, model, cwd, approvalPolicy, sandbox, ... }
client → turn/start                        server → turn/started
                                           server → item/started (userMessage)
                                           server → item/completed (userMessage)
                                           server → item/started (reasoning)
                                           server → item/reasoning/summaryTextDelta ×N
                                           server → item/started (commandExecution)
   ◀── server REQUEST: item/commandExecution/requestApproval
   ──▶ client RESPONSE: { decision: "accept" }
                                           server → item/commandExecution/outputDelta ×N
                                           server → item/completed (commandExecution)
                                           server → item/started (agentMessage)
                                           server → item/agentMessage/delta ×N
                                           server → item/completed (agentMessage)
                                           server → turn/completed { turn: { status, usage } }
```

To see the actual JSON for a full turn:

```bash
codex debug app-server send-message-v2 "run tests and summarize failures"
```

## 6. Client → server methods (104 total)

The full `ClientRequest` list, grouped by domain.

### 6.1 Handshake
```
initialize
```

### 6.2 Thread lifecycle (core)
```
thread/start            thread/resume           thread/fork
thread/archive          thread/unarchive        thread/delete
thread/unsubscribe      thread/read             thread/list
thread/loaded/list      thread/revert           thread/compact/start
thread/name/set         thread/metadata/update
thread/turns/list       thread/items/list       thread/inject_items
thread/shellCommand     thread/approveGuardianDeniedAction
```

### 6.3 Thread goals / attachments / sections
```
thread/goal/set         thread/goal/get         thread/goal/clear
thread/attachment/add   thread/attachment/list  thread/attachment/remove
thread/section/move
threadSection/list      threadSection/create    threadSection/update   threadSection/delete
```

### 6.4 Turn control (core)
```
turn/start              turn/steer              turn/interrupt
review/start
```

### 6.5 Models / configuration
```
model/list                          modelProvider/capabilities/read
config/read                         config/value/write          config/batchWrite
configRequirements/read
experimentalFeature/list            experimentalFeature/enablement/set
permissionProfile/list
```

### 6.6 MCP
```
mcpServer/tool/call         mcpServer/resource/read     mcpServer/oauth/login
mcpServerStatus/list        config/mcpServer/reload
```

### 6.7 Skills / hooks / plugins / apps (extensions)
```
skills/list                 skills/extraRoots/set       skills/config/write
hooks/list
plugin/list                 plugin/installed            plugin/read
plugin/install              plugin/uninstall            plugin/reconcile
plugin/skill/read
plugin/share/save           plugin/share/list           plugin/share/checkout
plugin/share/delete         plugin/share/updateTargets
marketplace/add             marketplace/remove          marketplace/upgrade
app/list                    app/read                    app/installed
```

### 6.8 Filesystem (client reaches the filesystem through the server)
```
fs/readFile     fs/writeFile    fs/createDirectory
fs/readDirectory fs/getMetadata fs/remove       fs/copy
fs/watch        fs/unwatch
fuzzyFileSearch
```

### 6.9 Command execution (client-driven PTY, outside the agent loop)
```
command/exec            command/exec/write
command/exec/terminate  command/exec/resize
```

### 6.10 Account / auth / usage
```
account/login/start     account/login/cancel    account/logout
account/read            getAuthStatus
account/rateLimits/read account/usage/read
account/rateLimitResetCredit/consume
account/workspaceMessages/read
account/sendAddCreditsNudgeEmail
```

### 6.11 Miscellaneous
```
gitDiffToRemote         getConversationSummary      feedback/upload
windowsSandbox/setupStart   windowsSandbox/readiness
externalAgentConfig/detect  externalAgentConfig/import
externalAgentConfig/import/recordHistory
externalAgentConfig/import/readHistories
```

> `externalAgentConfig/*` is a migration path that **detects and imports configuration from other
> agent tools** (the `codex-rs/external-agent-migration` crate).

## 7. Server → client requests (10) — where humans step in

The server sends a request and **the turn pauses until the client responds.**

| Method | Purpose |
|---|---|
| `item/commandExecution/requestApproval` | Approve a command execution |
| `item/fileChange/requestApproval` | Approve a file change |
| `item/permissions/requestApproval` | Approve a permission escalation |
| `item/tool/requestUserInput` | A tool needs user input |
| `item/tool/call` | Delegate a dynamic tool call to the client (`DynamicToolCallParams`) |
| `mcpServer/elicitation/request` | MCP elicitation |
| `account/chatgptAuthTokens/refresh` | Request a ChatGPT token refresh |
| `attestation/generate` | Generate the upstream `x-oai-attestation` (requires the capability opt-in) |
| `applyPatchApproval` | (legacy) Approve applying a patch |
| `execCommandApproval` | (legacy) Approve a command execution |

### Approval decisions

The `ReviewDecision` family: `accept`, `acceptForSession`, `decline`, `cancel`, plus
amendment-carrying variants such as `acceptWithExecpolicyAmendment`
(see the `ExecPolicyAmendment` and `NetworkPolicyAmendment` types).

`item/tool/call` matters most here — it is the channel through which **the agent calls tools owned
by the host application**. It is the protocol-level implementation of the division of labor:
"your application owns product context, business rules, and tools; Codex provides the agent loop
and sandboxed execution."

## 8. Server notifications (84)

### 8.1 Thread lifecycle
```
thread/started              thread/status/changed       thread/closed
thread/archived             thread/unarchived           thread/deleted
thread/reverted             thread/compacted
thread/name/updated         (thread metadata related)
thread/goal/updated         thread/goal/cleared
thread/attachment/updated   thread/queue/changed
thread/settings/updated     thread/tokenUsage/updated
thread/project/updated      project/changed
thread/environment/connected  thread/environment/disconnected
```

### 8.2 Turn lifecycle
```
turn/started        turn/completed
turn/diff/updated   turn/plan/updated
turn/moderationMetadata
hook/started        hook/completed
```

### 8.3 Item lifecycle & streaming (the heart of the UI)
```
item/started                            item/completed
item/agentMessage/delta
item/plan/delta
item/reasoning/summaryTextDelta         item/reasoning/summaryPartAdded
item/reasoning/textDelta
item/commandExecution/outputDelta       item/commandExecution/terminalInteraction
item/fileChange/outputDelta             item/fileChange/patchUpdated
item/mcpToolCall/progress
item/autoApprovalReview/started         item/autoApprovalReview/completed
autoApprovalReview/strictReviewRequired
rawResponseItem/completed               rawResponse/completed
serverRequest/resolved
```

> `rawResponseItem/completed` and `rawResponse/completed` are the escape hatch when you want the
> raw model response. `serverRequest/resolved` tells you an approval request was settled elsewhere
> (another client, auto-approval), so the UI can clean it up.

### 8.4 Processes / commands
```
command/exec/outputDelta    process/outputDelta     process/exited
```

### 8.5 MCP / apps / account
```
mcpServer/startupStatus/updated     mcpServer/oauthLogin/completed
mcpServer/event/stream/notification
app/list/updated
account/updated     account/rateLimits/updated      account/login/completed
skills/changed
```

### 8.6 Model-related
```
model/rerouted          model/verification
model/safetyBuffering/updated
modelProvider/authRecoveryStarted   modelProvider/authRecoveryCompleted
```

### 8.7 Realtime (voice) sessions
```
thread/realtime/started         thread/realtime/closed      thread/realtime/error
thread/realtime/itemAdded       thread/realtime/item/started  thread/realtime/item/completed
thread/realtime/item/transcript/delta
thread/realtime/transcript/delta  thread/realtime/transcript/done
thread/realtime/outputAudio/delta  thread/realtime/sdp
```

### 8.8 Warnings / diagnostics / other
```
error       warning     guardianWarning     configWarning   deprecationNotice
fs/changed
fuzzyFileSearch/sessionUpdated      fuzzyFileSearch/sessionCompleted
remoteControl/status/changed
externalAgentConfig/import/progress externalAgentConfig/import/completed
windows/worldWritableWarning        windowsSandbox/setupCompleted
```

> Clients can suppress unwanted notifications **per connection** via `optOutNotificationMethods`
> in `initialize`.

## 9. Key parameter types

### `ThreadStartParams`

```ts
type ThreadStartParams = {
  model?: string | null,
  modelProvider?: string | null,
  serviceTier?: string | null,
  cwd?: string | null,
  approvalPolicy?: AskForApproval | null,
  approvalsReviewer?: ApprovalsReviewer | null,  // where approval requests are routed
  sandbox?: SandboxMode | null,
  config?: Record<string, JsonValue> | null,
  serviceName?: string | null,
  baseInstructions?: string | null,
  developerInstructions?: string | null,
  personality?: Personality | null,
  ephemeral?: boolean | null,                     // a thread that is not persisted
  sessionStartSource?: ThreadStartSource | null,
  threadSource?: ThreadSource | null,
}
```

### `ThreadStartResponse`

```ts
type ThreadStartResponse = {
  thread: Thread,
  model: string,
  modelProvider: string,
  serviceTier: string | null,
  disabledPluginIds: string[],
  cwd: AbsolutePathBuf,
  instructionSources: LegacyAppPathString[],  // instruction files currently loaded (AGENTS.md, etc.)
  approvalPolicy: AskForApproval,
  approvalsReviewer: ApprovalsReviewer,
  sandbox: SandboxPolicy,                      // legacy; experimental clients prefer activePermissionProfile
  reasoningEffort: ReasoningEffort | null,
}
```

### `TurnStartParams`

```ts
type TurnStartParams = {
  threadId: string,
  input: UserInput[],                 // required
  clientUserMessageId?: string | null,
  turnTrigger?: string | null,
  toolOutput?: TurnToolOutput | null,
  disabledPluginIds?: string[] | null, // null = keep, [] = clear

  // all of the following apply to "this turn AND subsequent turns"
  cwd?: string | null,
  approvalPolicy?: AskForApproval | null,
  approvalsReviewer?: ApprovalsReviewer | null,
  sandboxPolicy?: SandboxPolicy | null,
  model?: string | null,
  serviceTier?: string | null,
  effort?: ReasoningEffort | null,
  summary?: ReasoningSummary | null,
  personality?: Personality | null,

  serviceTierForTurn?: string | null,  // this turn only (does not change the thread's tier)
  outputSchema?: JsonValue | null,     // JSON Schema constraining the final assistant message
}
```

> **Semantics to watch**: most `turn/start` overrides are *sticky* — they persist beyond this turn.
> To change only one turn, use an explicitly scoped field like `serviceTierForTurn`, or revert on
> the next turn.

### `UserInput` kinds (per protocol_v1)

| type | Description |
|---|---|
| `text` | Plain text plus optional UI text elements |
| `image` / `local_image` | Image input |
| `skill` | Explicit skill selection (`name`, path to `SKILL.md`) |
| `mention` | Explicit app/connector selection (`name`, path in `app://{connector_id}` form) |

## 10. Sandbox policies

| Value | Meaning |
|---|---|
| `readOnly` | Read-only filesystem |
| `workspaceWrite` | Writes allowed within the specified roots |
| `dangerFullAccess` | Unrestricted |
| `externalSandbox` | The client manages the sandbox itself |

An optional `networkAccess` setting controls outbound connectivity.

## 11. Error handling

Turn failures arrive inside `turn/completed`:

```json
{
  "method": "turn/completed",
  "params": {
    "turn": {
      "status": "failed",
      "error": {
        "message": "...",
        "codexErrorInfo": "ContextWindowExceeded"
      }
    }
  }
}
```

Common `codexErrorInfo` values: `ContextWindowExceeded`, `UsageLimitExceeded`,
`HttpConnectionFailed`, `SandboxError`.

RPC-level failures use the JSON-RPC error envelope. Some domains (for example user verification)
attach closed-set `{type, reason}` data: `invalidRequest` / `unavailable` / `cancelled` / `failed`.
**UIs must branch on these values rather than on message text.**

Codes, verified in `codex-rs/app-server/src/error_code.rs`:

| Code | Constant | Used for |
|---|---|---|
| `-32600` | `INVALID_REQUEST_ERROR_CODE` | e.g. `thread/archive` / `thread/delete` on a live internal worker; also `server_draining_error()` → "Server is draining; retry after reconnecting" |
| `-32601` | `METHOD_NOT_FOUND_ERROR_CODE` | Unsupported method (e.g. the removed `thread/rollback`) |
| `-32602` | `INVALID_PARAMS_ERROR_CODE` | Invalid params |
| `-32603` | `INTERNAL_ERROR_CODE` | Internal error |
| `-32001` | `OVERLOADED_ERROR_CODE` | Ingress queue saturated |

There is also a string code `input_too_large` (`INPUT_TOO_LARGE_ERROR_CODE`).

**Backpressure is real and specified.** `CHANNEL_CAPACITY = 128` ("a balance between throughput and
memory usage"). When `try_send` on the transport event channel returns `Full` for an incoming
*request*, the server replies:

```json
{ "id": <request id>, "error": { "code": -32001, "message": "Server overloaded; retry later." } }
```

Use exponential backoff with jitter. Note this path applies to requests; a full queue is handled
differently for other message kinds.

## 12. Code generation — building your own bindings

```bash
codex app-server generate-ts            # Rust protocol → TypeScript definitions
codex app-server generate-json-schema   # JSON Schema bundle for any code generator
```

The committed outputs are readable directly in the repository:

```
codex-rs/app-server-protocol/schema/
├── json/
│   ├── ClientRequest.json                        (~197KB)
│   ├── ServerNotification.json                   (~198KB)
│   ├── ServerRequest.json                        (~49KB)
│   ├── codex_app_server_protocol.schemas.json    (~682KB)
│   ├── codex_app_server_protocol.v2.schemas.json (~583KB)
│   └── v1/ , v2/
├── typescript/
│   ├── ClientRequest.ts  ServerRequest.ts  ServerNotification.ts
│   ├── InitializeParams.ts  InitializeResponse.ts  InitializeCapabilities.ts
│   ├── index.ts
│   └── v2/   ← ThreadStartParams, TurnStartParams, ThreadItem, and the other payloads
└── precomputed/
```

Languages with existing implementations: **Go, Python, TypeScript, Swift, Kotlin**.
OpenAI notes that "Codex is able to do a lot of the heavy lifting if you feed it the JSON schema
and documentation."

## 13. Three client integration patterns

### (a) Local apps and IDEs
Bundle or fetch a platform-specific App Server binary, launch it as a **long-running child
process**, and keep a bidirectional stdio channel open. The VS Code extension and the Desktop app
ship a **pinned**, tested version. Partners like Xcode who want to decouple release cycles keep the
client stable and **point it at a newer App Server binary** — the protocol is backward compatible,
so older clients can talk to newer servers safely.

### (b) Codex Web
A worker provisions a container with the checked-out workspace, launches the App Server binary
inside it, and maintains a stdio JSON-RPC channel. The browser talks to the Codex backend over
HTTP + SSE. The key design point: **web sessions are ephemeral (tabs close, networks drop), so the
web app cannot be the source of truth** — state and progress live on the server.

### (c) TUI / Codex CLI
Historically the TUI was a "native" client running in the same process as the agent loop, talking
directly to Rust core types. With the App Server in place, **the TUI is being refactored into an
ordinary client** that launches an App Server child process and speaks JSON-RPC. This unlocks a
TUI that **connects to a Codex server on a remote machine** — keeping the agent near the compute
and continuing work even if the laptop sleeps or disconnects.

## 14. Recent protocol changes (per `app-server/README.md`)

The repo's `codex-rs/app-server/README.md` reads more like release notes. Current contents:

- **`thread/rollback` removed** — request and response types deleted; requests take the
  unknown-method rejection path. **Use `thread/revert`.** Replay and migration of historical
  `ThreadRolledBack` events on disk remain supported.
- **Thread attachments** — `thread/attachment/add|list|remove` plus the `thread/attachment/updated`
  notification. Works without loading the thread. Idempotently identified by
  `(threadId, attachmentType, identityKey)`. For pull requests the recommended canonical identity is
  `JSON.stringify([canonicalHostname, lowercaseOwner, lowercaseRepository, pullRequestNumber])`.
  Up to 100 attachments per thread, 100 per page.
- **Thread removal constraints** — a live internal worker (e.g. a Guardian reviewer) cannot be
  removed via `thread/archive` / `thread/delete` (`-32600`). Only after the owner releases the
  worker.
- **Plugin selection** — `thread/settings/update` and `turn/start` accept `disabledPluginIds`
  (`<plugin-name>@<marketplace-name>` format, from `PluginSummary.id` in `plugin/list`).
  A supplied list replaces the selection; omission or `null` preserves it; `[]` clears it.
  **It does not yet filter plugin capabilities** — it only saves the selection.
- **MCP server capabilities** — `mcpServerStatus/list` returns the server's advertised capabilities
  object (including its `extensions` map) in both `full` and `toolsAndAuthOnly` detail modes.
  Null when the connection has not initialized successfully; **never inferred from the tool list.**
- **Hosted Codex Apps MCP protocol** — Legacy by default. Discover the 2026-07-28 protocol by setting
  `[features] codex_apps_mcp_2026_07_28 = true` or sending a runtime override via
  `experimentalFeature/enablement/set`.
- **User verification (experimental)** — biometric verification via five methods:
  `userVerification/status|enroll|delete|verify|cancel`. P-256 ECDSA with SHA-256,
  `ecdsaP256Sha256X962`, unpadded base64url SPKI-DER. Advertised only for local TUI/Desktop sessions
  with the `experimentalApi` opt-in. One native worker per app-server.
- **Managed model provider** — existing threads retain their provider configuration; input-family
  RPCs (turn start/steer, review, compaction, queue start, goal updates) are rejected when managed
  requirements no longer match. Interrupt, realtime stop, and goal pause/clear remain available.
- **Amazon Bedrock** — if `model_providers.amazon-bedrock.aws.credential_export` is configured,
  Bedrock setup and login return an error without changing configuration or credentials.
  `aws.credential_export` and `aws.profile` cannot be configured together.

## 15. Legacy: the Codex core internal protocol (protocol_v1)

The **SQ/EQ model** that sits beneath (and predates) the App Server. See
`codex-rs/docs/protocol_v1.md`.

- `Codex` ↔ UI communicate through a **Submission Queue (SQ)** / **Event Queue (EQ)** pair.
- `Op` is the submission payload enum (`Op::ConfigureSession`, `Op::UserTurn`, `Op::Interrupt`,
  `Op::ExecApproval`, `Op::UserInputAnswer`); `EventMsg` is the event payload enum.
  Both are `non_exhaustive`.
- A `Session` runs at most one `Task` at a time. For parallel work, **run one Codex instance per
  thread of work**.
- `Turn` here is **not** the App Server's turn — it is **one model-request cycle** (an iteration
  inside a Task).
- For v1 wire compatibility, `EventMsg::TurnStarted` / `TurnComplete` serialize as
  `task_started` / `task_complete`, and the deserializer accepts both `task_*` and `turn_*` tags.
- `response_id` matches the one stored by OpenAI's `/responses` endpoint, so it can resume or fork
  a thread in a later session.

> For a new integration, use the **App Server protocol, not protocol_v1**. The docs state that
> submission payloads should be treated as implementation details unless a specific transport owns
> an explicit adapter.
