# 10. Agent Client Protocol — engine-side reading

> The JSON-RPC that editors (clients) use to drive coding agents (typically a subprocess). This is
> the **engine-side** of a surface the client study already met as UI: Devin Local, Paseo, Superset
> and Strands' CLI all speak it ([01](01-landscape.md), [05](05-antigravity-windsurf.md),
> [06](06-orca-superset.md), [07](07-paseo-conductor.md),
> [`strands/06`](../strands/06-multi-agent-and-exposure.md) §5.4).
>
> Read 2026-09-30 from the spec repo and generated schema, then contrasted with Codex App Server
> ([`docs/02`](../docs/02-app-server-protocol.md) §7) and the Strands CLI implementation at
> `a9a62d4e`. **No live ACP client was started.** Drift pass 2026-10-20 → `ff7ef5169` (§1.1): the
> stable v1 wire moved once (`schema-v1.25.0`, notices + compaction + strict parsing); the
> permission RPC did not.
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

Upstream: [`agentclientprotocol/agent-client-protocol`](https://github.com/agentclientprotocol/agent-client-protocol)
(the `zed-industries/…` URL now redirects there). Checkout `~/repos/harness-refs/agent-client-protocol`
was recreated 2026-10-20 (`--filter=blob:none`) for the drift pass below; the 2026-09-30 clone had
been removed with the other reference checkouts.

Study pin: **`9b26a3eaa8d3644c2a899f56171bd25f7a5a884f`** (2026-09-30, `docs: update registry agents (#2258)`).
Re-checked 2026-09-30 evening against `c81fae79` — 7 commits, `schema/v1/schema.json` byte-identical,
everything substantive in v2 / unstable files (`schema-v1.23.0` → `v1.24.0`, `2.0.0-alpha.5` → `alpha.6`).

### 1.1 Drift pass 2026-10-20 — `9b26a3ea` → `ff7ef5169` (160 commits)

HEAD **`ff7ef5169fd74e7f8921dc24413110a65753168e`** (2026-10-20 04:53 UTC, `docs: update registry
agents (#2443)`). Two generated files per wire version were diffed structurally (`$defs` keys,
`x-method` set, per-definition JSON equality), not by line count. **The stable v1 wire moved once**,
in `schema-v1.25.0` (2026-10-09, PRs #2333 / #2334 / #2336); `v1.26.0` (10-16) is unstable-only.

| Surface | `9b26a3ea` | `ff7ef5169` | What changed |
|---|---|---|---|
| `schema/v1/schema.json` `$defs` | 170 | **178** | +8, −0: `Notice` · `NoticeSeverity` · `NoticeCapabilities` · `CompactionCapabilities` · `CompactionId` · `CompactionStatus` · `CompactionUpdate` · `CompactionSummaryChunk` |
| v1 `x-method` set | 25 | 25 | **unchanged** — no method added or removed (`$/cancel_request` and `session/update` counted) |
| `SessionUpdate` variants | 11 | **14** | + `notice` · `compaction_update` · `compaction_summary_chunk`, each sendable only when the client advertised `clientCapabilities.session.notices` / `.compaction` (`{}` = full contract; omitted or `null` = unsupported) |
| Permission definitions (8: `RequestPermissionRequest/Response`, `PermissionOption`, `PermissionOptionKind`, `RequestPermissionOutcome`, `StopReason`, `ToolCallStatus`, `ToolKind`) | — | — | **byte-identical** — §5 holds as written |
| Lenient-parse annotations (`x-deserialize-default-on-error`, `x-deserialize-skip-invalid-items`) | present on 6 defs | **removed** (#2333) | `terminal/create` `args`/`env`/`cwd`/`outputByteLimit`, `fs/read_text_file` `line`/`limit`, `session/{new,load,resume}` `mcpServers`/`additionalDirectories`, terminal auth-method `args`/`env` → malformed values now fail with `-32602` (or drop the auth method) instead of silently running something else — e.g. `args: ["serve","--port",3000]` used to run `serve --port` |
| `schema/v1/schema.unstable.json` | 265 defs / 40 methods | 225 / **30** | **NES and `document/*` removed** (#2266: 10 methods, 40 defs); added subagents (#1992), client system prompt (#2361), `SessionCancelCapabilities` |
| `schema/v2/schema.json` (draft) | 175 / 16 | 181 / 16 | +notice/compaction defs, `StopReason` → `ErrorStopReason`; permission request/option/kind defs identical, `RequestPermissionOutcome` **description only** (cancel answers scoped to the session, never twice) |
| Artifact versions | crate `1.9.1`, `schema-v1.24.0`, `2.0.0-alpha.6` | crate **`1.12.0`**, **`schema-v1.26.0`**, **`2.0.0-alpha.9`** | still all wire `1`; `LATEST = V1` without `unstable_protocol_v2` (`version.rs:39`) |
| npm `@agentclientprotocol/sdk` | 1.5.1 | **2.0.0** (2026-10-19) | breaking for *library* users (connection classes removed, unstable features behind `/unstable` entrypoints) — its CHANGELOG states *"SDK 2.0 does not switch the default protocol from ACP v1"* |

Reading: the v1 contract gained two capability-gated notification families and lost its tolerance
for malformed values on fields the receiver acts on. Nothing about approval changed. **Next
baseline: `ff7ef5169`.** The 09-30 lesson repeats with the sign flipped — this time the CHANGELOG
entries are tagged `*(schema)*`, and the stable file did change; the tag is the first thing to read.

## 2. Versioning — three numbers, one wire

| Number | What it is | This read |
|---|---|---|
| **`protocolVersion`** | integer exchanged at `initialize`; **the wire version** | **`1` is stable.** `0` is pre-release. `2` exists only behind `unstable_protocol_v2` |
| Schema / crate release | artifact version for generators (`schema-v1.24.0` as of 2026-09-30 evening → **`schema-v1.26.0`** 2026-10-20; crate `agent-client-protocol-schema` **1.9.1** → **1.12.0**) | many schema releases describe the **same** wire version `1` |
| Language SDK | `@agentclientprotocol/sdk` **1.3.0** (Strands CLI pin, 2026-07-21) … latest npm **2.0.0** (2026-10-19; 1.5.1 at the 09-30 read) | `PROTOCOL_VERSION = 1` at the 1.3.0 pin (`typescript-sdk` `src/schema/index.ts:320`); 2.0.0 keeps v1 as the default protocol (§1.1) |

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

Generated JSON Schema `schema/v1/schema.json` (`$defs` count 170 at the pin, **178** at `ff7ef5169` — §1.1). Method names below are the
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
`current_mode_update` · `config_option_update` · `session_info_update` · `usage_update`, and since
`schema-v1.25.0` (2026-10-09) three **capability-gated** ones — `notice` (`severity` `info` ·
`warning` · `error` · open `other`, required non-empty `title`; *"live events rather than session
history"*, the agent *"must not rely on a notice being received, displayed, or seen"*),
`compaction_update` (`compactionId` + `status` `in_progress` · `completed` · `failed` · `cancelled` ·
`other`; an upsert whose first notification fixes the timeline position) and
`compaction_summary_chunk` (append-only content for that compaction). Agents MUST NOT send them to a
v1 client that did not advertise `clientCapabilities.session.notices` / `.compaction`
(`docs/protocol/v1/initialization.mdx`, +32 lines). v2 needs no capability for either.

### 4.3 Unstable extras (not in `schema/v1/schema.json`)

`schema/v1/schema.unstable.json` adds, behind crate features such as `unstable_llm_providers`,
`unstable_mcp_over_acp`, `unstable_nes`, `unstable_session_fork`:

`providers/list|set|disable` · `mcp/message` (both sides) · `nes/start|suggest|accept|reject|close` ·
`document/didOpen|didChange|didClose|didSave|didFocus` · `session/fork`.

These are **not** part of wire version 1's stable surface. An SDK pin that lacks them is still
v1-compatible. **2026-10-20:** the `nes/*` and `document/*` families (10 methods, 40 defs) were
**removed** from the unstable schema (#2266, `schema-v1.26.0`); the TypeScript SDK first isolated
NES behind an experimental entrypoint (1.9.0) and then 2.0.0 dropped it. Added instead:
subagent types (#1992), a client **system prompt** schema (`SystemPrompt`, `SystemPromptMode`,
`SessionSystemPrompt*Capabilities`, #2361) and `SessionCancelCapabilities`. All still `*(unstable)*`.

**Added 2026-09-30 (`schema-v1.24.0`, re-check to `c81fae79`)** — three entries, **all marked
`*(unstable)*` in the project's own CHANGELOG**, which is why the stable schema file did not change:

| # | Entry | PR | What it adds to the unstable surface |
|---|---|---|---|
| 1 | Initial RFD and schema for **subagents** | [#1992](https://github.com/agentclientprotocol/agent-client-protocol/pull/1992) | `SubagentSessionCapabilities` · `SubagentCapabilities` · `SubagentUpdate`; new keys `subagents`, `mcpServers`. Design lives in `docs/rfds/subagents.mdx` (+1185 lines) — an RFD, i.e. still a proposal |
| 2 | **MCP-over-ACP becomes request-scoped** | [#2223](https://github.com/agentclientprotocol/agent-client-protocol/pull/2223) | `MessageMcpRequest` / `MessageMcpResponse`, `McpRequestId`, `McpServerAcpId` — MCP payloads ride the *message* rather than a standalone `mcp/message` exchange |
| 3 | Return **available commands** in session responses | [#2259](https://github.com/agentclientprotocol/agent-client-protocol/pull/2259) | listed as `*(unstable-v2)*` — v2 only, not in the v1 unstable schema |

> 📌 **Entry 2 was the open question, and it is now resolved: it does not touch the permission RPC.**
> `mcp/message` carries exactly `serverId` · `requestId` · `method` · `params` — no `sessionId`, no
> `toolCall`, and nothing that can hold a `PermissionOption`; grepping `MessageMcpRequest` for
> `permission|sessionId|toolCall` returns nothing. `McpRequestId` is *"generated by the caller and
> preserved unchanged by proxies… distinct from the outer ACP JSON-RPC request ID"* — it correlates
> the inner MCP exchange and cannot join it to a tool call. And `MessageMcpResponse` is *"exactly one
> inner MCP outcome"* with **outer ACP errors reserved for "binding and runtime failures"**, so a
> refused MCP operation is a *successful* outer RPC wrapping an inner error — a different layer from
> an approval. Source: `docs/protocol/v1/draft/schema.mdx`, **not** the 244 added lines of
> `prompt-turn.mdx` this entry originally flagged (those cover subagent transcripts). A
> permission-*adjacent* change is evidence of interaction only when the payload can carry the
> primitive.

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

**Re-checked 2026-10-20 at `ff7ef5169`:** across 160 commits and one stable schema release the
eight permission-related definitions are byte-identical to the pin (§1.1). Rust line numbers in
this section are from the pin and were not re-derived.

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
| `session/prompt` response ends the turn (`stopReason`) | response only acknowledges; completion is a `state_update` notification. `StopReason` left the v2 draft at `2.0.0-alpha.9`; failures carry an `ErrorStopReason` (*"details of a failure that ended active work"*) |
| `authenticate` / `logout` | `auth/login` / `auth/logout` |
| `session/load` | **removed** — use `session/resume` with `replayFrom: { type: "start" }` |
| `session/set_mode` | **removed** — config options |
| `fs/*`, `terminal/*` | **removed** — client-provided MCP for client-side tools |
| `session/request_permission` | **same name**; params restructured — required `sessionId` · `title` · `options`, optional `description` · `subject`; `PermissionOptionKind` adds the open `other` string (`_`-prefixed values reserved for implementations). Unchanged `alpha.6` → `alpha.9` except cancel wording |
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
- Unstable extras (`session/fork`, MCP-over-ACP, providers, subagents, system prompt) — unread beyond method names. NES is gone from the schema (2026-10-20), so it is no longer a question.
- Strands CLI pin `@agentclientprotocol/sdk` 1.3.0 vs npm 2.0.0 — whether `strands --acp-server` has moved off the removed connection classes was not re-read this pass.
- Streamable HTTP transport — draft, unread.
