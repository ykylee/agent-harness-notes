---
type: concept
status: active
last_ingested_from: agent-ux/10-acp.md + strands/06-multi-agent-and-exposure.md + docs/02-app-server-protocol.md
related_pages: [concepts/approval-gate, concepts/wire-protocol-boundary, concepts/agent-client-design-language, concepts/harness]
created: 2026-09-30
updated: 2026-09-30
---

# Agent Client Protocol — editor-to-agent JSON-RPC

- Purpose: the wire between a code editor (client) and a coding agent (typically a subprocess), as distinct from Codex App Server and from model `WireApi`.
- Scope: stable `protocolVersion` 1 methods, the permission RPC, session model; Codex and Strands CLI contrasted
- Primary sources: [`agent-ux/10-acp.md`](../../../agent-ux/10-acp.md); spec repo `agentclientprotocol/agent-client-protocol` @ `9b26a3ea`
- Updated: 2026-09-30 (first ingest)

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | Wire version | integer `protocolVersion` at `initialize`. **Stable is `1`.** `2` is an unstable draft |
| 2 | Artifact versions | crate `1.9.1`, `schema-v1.23.0`, SDK `1.3.0`–`1.5.1` — **not** wire versions |
| 3 | Transport | JSON-RPC 2.0, newline-delimited stdio |
| 4 | Approval | **one** agent→client method: `session/request_permission` |
| 5 | Option kinds | `allow_once` · `allow_always` · `reject_once` · `reject_always` |
| 6 | Strands harness ACP | registers a v1 subset; **never sends** the permission RPC |

## §2 Versioning  {#s2-versioning}

ACP wire compatibility is the integer exchanged at `initialize`. Schema/crate/SDK release numbers
can move while `protocolVersion` stays `1`. The spec README says not to infer wire compatibility
from those artifact versions. `protocolVersion` is a number: deserialising `"1.0.0"` errors.

v2 (`unstable_protocol_v2`) redesigns the prompt lifecycle, drops `session/load` / `fs/*` /
`terminal/*` / `session/set_mode`, and keeps the permission **method name**. Keep serving v1 until
v2 is stable. See [[concepts/primary-source-verification]] §3.8.

## §3 Methods (stable v1)  {#s3-methods}

Client → agent (baseline): `initialize`, `authenticate`, `session/new`, `session/prompt`;
notification `session/cancel`. Optional: `session/load` (`loadSession` capability), `logout`,
`session/set_mode`, `session/set_config_option`, `session/list`, `session/delete`, `session/close`,
`session/resume`.

Agent → client (baseline): **`session/request_permission`**, notification `session/update`.
Optional: `fs/read_text_file`, `fs/write_text_file`, `terminal/*`, `elicitation/create`.

The TypeScript SDK's camelCase accessor `requestPermission` sends the hyphenated wire string
`session/request_permission`.

Unstable extras (`session/fork`, `providers/*`, `nes/*`, `document/*`, `mcp/message`) live in
`schema.unstable.json`, not in the stable v1 schema.

## §4 Permission  {#s4-permission}

The agent MAY request permission before a tool call. Params: `sessionId`, `toolCall`, `options[]`
(`optionId`, `name`, `kind`). Outcome: `selected` + `optionId`, or `cancelled`. On
`session/cancel` the client MUST answer every outstanding permission request with `cancelled`.
`kind` is a UI hint; the agent defines what "remember" means.

This is the protocol enum Devin Desktop already rendered ([`agent-ux/08`](../../../agent-ux/08-primitives-rendered.md)
§1.2). Contrast Codex: ten typed server→client requests and a `ReviewDecision` family that can
carry policy amendments — [[concepts/approval-gate]] §2.

## §5 Session  {#s5-session}

A prompt turn is `session/prompt` → `session/update` stream → `stopReason` on the prompt
response (`end_turn` · `max_tokens` · `max_turn_requests` · `refusal` · `cancelled`). Agents are
typically client subprocesses. This is **not** Codex `thread`/`turn`, and **not** model
`WireApi::Responses` ([[concepts/wire-protocol-boundary]]).

## §6 Strands CLI  {#s6-strands}

`strands --acp-server` pins `@agentclientprotocol/sdk` 1.3.0 (`PROTOCOL_VERSION = 1`).
`createAcpApp` handles `initialize`, `session/new`, `session/load`, no-op `authenticate`,
`session/prompt`, `session/cancel`.

The **imported source-agent** path forwards tool-permission events as
`session/request_permission`. The **harness** path (`createHarness`, default
`interventions=None`) never calls it. An ACP client driving the harness therefore has no
protocol-level card to answer. Source absence ✅; live client ⚠️
([`strands/06`](../../../strands/06-multi-agent-and-exposure.md) §5.4).

## §7 Read next  {#s7-next}

- [[concepts/approval-gate]] — Codex's ten requests and Strands' out-of-loop interrupt
- [[concepts/wire-protocol-boundary]] — model HTTP wire, a different boundary
- [[concepts/agent-client-design-language]] — how clients render the four option kinds
- Original: [`agent-ux/10-acp.md`](../../../agent-ux/10-acp.md)
