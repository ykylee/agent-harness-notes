# 10. Agent Client Protocol — engine-side reading

> The JSON-RPC that editors (clients) use to drive coding agents (typically a subprocess). This is
> the **engine-side** of a surface the client study already met as UI: Devin Local, Paseo, Superset
> and Strands' CLI all speak it ([01](01-landscape.md), [05](05-antigravity-windsurf.md),
> [06](06-orca-superset.md), [07](07-paseo-conductor.md),
> [`strands/06`](../strands/06-multi-agent-and-exposure.md) §5.4).
>
> Read 2026-09-30 from the spec repo and generated schema, then contrasted with Codex App Server
> ([`docs/02`](../docs/02-app-server-protocol.md) §7) and the Strands CLI implementation at
> `a9a62d4e`. **No live ACP client was started.**
>
> Grade: method names, session model and permission option kinds ✅ from schema and spec prose.
> Runtime behaviour of any client or of Strands' ungated harness path ⚠️.

## 1. What it is

ACP standardises **editor ↔ coding-agent** communication. Agents are typically **client
subprocesses**. Framing is [JSON-RPC 2.0](https://www.jsonrpc.org/specification). The defined
transport is **stdio**: newline-delimited JSON-RPC, no embedded newlines, `stderr` for logs only
(`docs/protocol/v1/transports.mdx`). Streamable HTTP is a draft.

Official spec: [`agentclientprotocol/agent-client-protocol`](https://github.com/agentclientprotocol/agent-client-protocol)
(same content as `zed-industries/agent-client-protocol`). Site: <https://agentclientprotocol.com>.
Official libraries: TypeScript, Python, Rust, Kotlin, Java.

Local clone: `~/repos/harness-refs/agent-client-protocol`, origin
`https://github.com/agentclientprotocol/agent-client-protocol.git` (`blob:none`). HEAD
**`9b26a3eaa8d3644c2a899f56171bd25f7a5a884f`** (2026-09-30, `docs: update registry agents (#2258)`).

## 2. Versioning — three numbers, one wire

| Number | What it is | This read |
|---|---|---|
| **`protocolVersion`** | integer exchanged at `initialize`; **the wire version** | **`1` is stable.** `0` is pre-release. `2` exists only behind `unstable_protocol_v2` |
| Schema / crate release | artifact version for generators (`schema-v1.23.0`, crate `agent-client-protocol-schema` **1.9.1**, repo tag `v1.9.1`) | many schema releases describe the **same** wire version `1` |
| Language SDK | `@agentclientprotocol/sdk` **1.3.0** (Strands CLI pin, 2026-07-21) … latest npm **1.5.1** (2026-09-28) | `PROTOCOL_VERSION = 1` at the 1.3.0 pin (`typescript-sdk` `src/schema/index.ts:320`) |

The spec README states this as a rule: **do not infer wire compatibility from crate or schema
release numbers.** Negotiate `protocolVersion`; then use capabilities for optional methods
(`README.md`).

Rust (`agent-client-protocol-schema/src/version.rs`): `V0 = 0`, `V1 = 1`, `V2 = 2` only with
`unstable_protocol_v2`, and `LATEST = V1` when that feature is off. Deserialising `"1.0.0"` as
`protocolVersion` **errors** — it is a number, not a semver string.

> 📌 **v2 is an unstable draft**, not the current wire. `docs/protocol/v2/migration.mdx` says to
> keep serving v1, negotiate per connection, and gate v2 behind feature flags until it stabilises.
> Negotiating `protocolVersion: 2` does not imply the unstable extras (`schema/v2/schema.unstable.json`).

## 3. Message flow

From `docs/protocol/v1/overview.mdx`:

1. Client → Agent `initialize` (version + capabilities). Optional `authenticate`.
2. `session/new`, or `session/load` if the agent advertised `loadSession`.
3. Prompt turn: Client `session/prompt` → Agent `session/update` notifications, and as needed
   file-system / terminal / **permission** requests → Client may `session/cancel` → the
   `session/prompt` **response** carries a `stopReason`.

`StopReason` in `schema/v1/schema.json`: `end_turn` · `max_tokens` · `max_turn_requests` ·
`refusal` · `cancelled`. On `session/cancel` the agent MUST still return `cancelled`, and the
client MUST answer every pending `session/request_permission` with `outcome: "cancelled"`.

## 4. Methods (stable v1 schema)

Generated JSON Schema `schema/v1/schema.json` (`$defs` count 170). Method names below are the
`x-method` values on request/response types. Rust constants in
`agent-client-protocol-schema/src/v1/{agent,client,protocol_level}.rs` match.

### 4.1 Client → Agent (agent methods)

| Method | Role | Notes |
|---|---|---|
| `initialize` | baseline | negotiate `protocolVersion`, exchange capabilities |
| `authenticate` | baseline if the agent requires it | |
| `session/new` | baseline | create a session (`cwd`, optional `mcpServers`) |
| `session/prompt` | baseline | one user turn |
| `session/cancel` | notification | interrupt the turn |
| `session/load` | optional | requires `agentCapabilities.loadSession` |
| `logout` | optional | requires `agentCapabilities.auth.logout` |
| `session/set_mode` | optional | session modes |
| `session/set_config_option` | optional | |
| `session/list` | optional | |
| `session/delete` | optional | |
| `session/close` | optional | |
| `session/resume` | optional | |
| `$/cancel_request` | protocol-level | cancel an in-flight JSON-RPC request |

### 4.2 Agent → Client (client methods)

| Method | Role | Notes |
|---|---|---|
| **`session/request_permission`** | **baseline** | the approval gate. Schema `x-side: client` |
| `session/update` | notification | progress (`SessionUpdate` variants below) |
| `fs/read_text_file` · `fs/write_text_file` | optional | `clientCapabilities.fs` |
| `terminal/create` · `output` · `release` · `wait_for_exit` · `kill` | optional | `clientCapabilities.terminal` |
| `elicitation/create` | optional | structured user input; `elicitation/complete` is a notification |

`session/update` variants in the stable schema: `user_message_chunk` · `agent_message_chunk` ·
`agent_thought_chunk` · `tool_call` · `tool_call_update` · `plan` · `available_commands_update` ·
`current_mode_update` · `config_option_update` · `session_info_update` · `usage_update`.

### 4.3 Unstable extras (not in `schema/v1/schema.json`)

`schema/v1/schema.unstable.json` adds, behind crate features such as `unstable_llm_providers`,
`unstable_mcp_over_acp`, `unstable_nes`, `unstable_session_fork`:

`providers/list|set|disable` · `mcp/message` (both sides) · `nes/start|suggest|accept|reject|close` ·
`document/didOpen|didChange|didClose|didSave|didFocus` · `session/fork`.

These are **not** part of wire version 1's stable surface. An SDK pin that lacks them is still
v1-compatible.

### 4.4 JS accessor vs wire name

The TypeScript SDK exposes camelCase accessors (`acp.methods.client.session.requestPermission`)
that send the hyphenated wire string `session/request_permission`
(`@agentclientprotocol/sdk@1.3.0` `src/schema/index.ts:300`, `src/acp.ts:158`). Strands CLI uses
the accessor. Spec documents, JSON Schema `x-method`, and Rust constants use the hyphen.

## 5. Permission

The agent **MAY** call `session/request_permission` before executing a tool
(`docs/protocol/v1/tool-calls.mdx`). Params: `sessionId`, `toolCall` (`ToolCallUpdate`),
`options` (`PermissionOption[]`). Required fields on each option: `optionId`, `name`, `kind`.

`PermissionOptionKind` in **stable v1** (`schema/v1/schema.json`, Rust
`client.rs:1088-1096`):

| `kind` | Spec gloss |
|---|---|
| `allow_once` | Allow this operation only this time |
| `allow_always` | Allow this operation and remember the choice |
| `reject_once` | Reject this operation only this time |
| `reject_always` | Reject this operation and remember the choice |

The client study already recorded these four strings on Devin Desktop
([08](08-primitives-rendered.md) §1.2). They are the protocol enum, not a Devin invention.

Response `RequestPermissionOutcome`: `cancelled`, or `selected` plus `optionId`. Clients MAY
auto-allow or auto-reject from user settings. `kind` is a **UI hint** — the agent decides what
"remember" means.

v2 keeps the four kinds and adds an `other` / future-kind escape (`schema/v2`). The method
**name** is unchanged; params grow a required `title` and optional `subject`
(`docs/protocol/v2/migration.mdx`).

`ToolCallStatus`: `pending` (input still streaming, **or awaiting approval**) · `in_progress` ·
`completed` · `failed`. `ToolKind`: `read` · `edit` · `delete` · `move` · `search` · `execute` ·
`think` · `fetch` · `switch_mode` · `other`.

## 6. Contrast: Codex App Server

Both are bidirectional JSON-RPC with a human in the loop. They are **different wires**.

| | ACP v1 | Codex App Server ([`docs/02`](../docs/02-app-server-protocol.md) §7) |
|---|---|---|
| Relationship | editor (client) drives a coding-agent subprocess | app / SDK drives the Codex engine |
| Approval shape | **one** method, `session/request_permission`, with a list of labelled options | **ten** server→client requests, three of them typed `*/requestApproval` plus input, tool delegation, MCP elicitation, token refresh, attestation, two legacy |
| Decision vocabulary | `optionId` chosen from agent-supplied options; `kind` is a hint | `ReviewDecision`: `accept` / `acceptForSession` / `decline` / `cancel`, plus amendment-carrying variants |
| What stalls | the prompt turn, until the permission RPC returns (or `cancelled`) | the turn, until the matching request is answered; without the three approvals it never completes |
| Tool-on-the-host | client `fs/*` and `terminal/*` (capability-gated); MCP servers passed into `session/new` | `item/tool/call` — the host owns product tools |
| Session | ACP `session/*` (new / load / prompt / cancel / …) | Codex `thread/*` + `turn/*` |
| Wire version | integer `protocolVersion` | App Server method catalog; experimental methods filtered from the generated TS schema ([`docs/99`](../docs/99-sources.md) §E) |

> 📌 ACP collapses command / file / permission / "ask the user" into **one request whose options
> are data.** Codex types the thing being approved (`commandExecution`, `fileChange`,
> `permissions`) as **the method name**, and lets the response carry a policy amendment. Paseo's
> "one request object, four renderers" ([07](07-paseo-conductor.md)) is the ACP shape.

## 7. Contrast: Strands CLI (`strands --acp-server`)

Implementation: `strands-cli/src/tui/acp/server.ts` on harness-sdk `a9a62d4e`, SDK pin
`@agentclientprotocol/sdk` **1.3.0** (`strands-cli/package.json:62`). Transport: the SDK's
`ndJsonStream` over stdin/stdout.

### 7.1 What `createAcpApp` actually registers

`server.ts:209-221` handles:

`initialize` · `session/new` · `session/load` · `authenticate` (empty `{}`) · `session/prompt` ·
`session/cancel`.

It does not register `session/list|delete|close|resume|set_mode|set_config_option`, `logout`,
`fs/*`, `terminal/*`, or elicitation. That is a legal v1 subset: optional methods are
capability-gated, and this agent does not advertise them.

`initialize` advertises `loadSession`, `promptCapabilities.image` + `embeddedContext`,
`mcpCapabilities.http` + `sse` (`server.ts:57-74`). `agentInfo.version` is hard-coded `'0.0.1'`
even though `HARNESS_VERSION` is imported in the same file (used for MCP
`applicationVersion`, not `agentInfo`). One workspace per process — a second `cwd` throws
(`server.ts:194-206`). One prompt at a time (`server.ts:107-109`).

### 7.2 Approval asymmetry (confirmed against the spec method)

| Path | Permission RPC | Source |
|---|---|---|
| **Imported Python source agent** | tool-permission events become `session/request_permission` round-trips | `strands-cli/src/tui/project/acp.ts:66-82` — `client.request(acp.methods.client.session.requestPermission, …)` |
| **Harness path** (`createHarness`) | the prompt loop projects events and usage; **no `requestPermission` call** | `server.ts:102-147` |

The harness default is `interventions=None` ([`strands/03`](../strands/03-tools-and-approval.md)).
An ACP client driving `strands --acp-server` on the harness therefore has **no protocol-level
approval prompt** to answer. The spec says the agent MAY request permission; this path never
does. That is an implementation choice, not a protocol gap.

On the source-agent path, a `cancelled` outcome is forwarded as `'deny'`
(`acp.ts:79-81`: `result.outcome.outcome === 'selected' ? result.outcome.optionId : 'deny'`).
The spec distinguishes `cancelled` from a selected reject. Whether the Python backend treats
`'deny'` as `reject_once` is ⚠️ (not followed into `PythonBackend.respondPermission`).

Runtime: still **not** exercised against a live ACP client. Source absence of the call on the
harness path is ✅.

## 8. v2 draft, in one table

From `docs/protocol/v2/migration.mdx` (still labeled draft). Kept here so a later drift check
does not confuse artifact churn with a wire bump.

| v1 | v2 draft |
|---|---|
| `session/prompt` response ends the turn (`stopReason`) | response only acknowledges; completion is a `state_update` notification |
| `authenticate` / `logout` | `auth/login` / `auth/logout` |
| `session/load` | **removed** — use `session/resume` with `replayFrom: { type: "start" }` |
| `session/set_mode` | **removed** — config options |
| `fs/*`, `terminal/*` | **removed** — client-provided MCP for client-side tools |
| `session/request_permission` | **same name**; params restructured |
| `protocolVersion: 1` | send `2`; a v1-only peer answers `1` |

Stable v1 remains the wire to implement against today.

## 9. What this means if you are building a harness

- [ ] Treat `protocolVersion` as the compatibility key. SDK 1.3.0 vs crate 1.9.1 vs
      `schema-v1.23.0` are artifact versions of wire `1`.
- [ ] Implement `session/request_permission` if the agent can do anything a person should see.
      Advertising a session without ever sending it is how Strands' harness ACP path ships.
- [ ] Send options as data (`optionId` + `name` + `kind`). Let the client render; do not invent a
      second method per tool kind unless you need Codex-style amendments on the response.
- [ ] On `session/cancel`, reply to every outstanding permission request with `cancelled`.
- [ ] Keep v2 behind an explicit negotiated version. Do not drop v1.

## 10. Open questions

- Live round-trip: does the harness ACP path actually run tools ungated under
  `interventions=None` when a real client is attached? Source says yes; needs a mock-model run.
- How Devin Local / Paseo / Superset map ACP option kinds onto their cards — strings match the
  enum ([08](08-primitives-rendered.md)); the RPC was not traced in those binaries this pass.
- Source-agent `'deny'` vs spec `cancelled` / `reject_*`.
- Unstable extras (`session/fork`, NES, MCP-over-ACP, providers) — unread beyond method names.
- Streamable HTTP transport — draft, unread.
