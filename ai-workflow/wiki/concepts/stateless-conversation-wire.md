---
type: concept
status: active
last_ingested_from: docs/16-responses-chat-adapter.md
related_pages: [concepts/wire-protocol-boundary, concepts/retained-reasoning, concepts/thread-turn-item]
created: 2026-09-22
updated: 2026-09-23
---

# Stateless Conversation Wire — what `store: false` gives away free

- Purpose: why Codex sends conversations to the model completely statelessly, and what that exempts an adapter or proxy from building.
- Scope: the real request payload, the evidence of statelessness, the design burdens removed, the fields pinned to constants
- Primary sources: `codex-rs/codex-api/src/common.rs`, `codex-rs/core/src/client.rs`
- Updated: 2026-09-23

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | `store` | **`false`** — always |
| 2 | `previous_response_id` | **absent** from the HTTP payload (it exists only on the WebSocket variant, and the conversion sets it to `None`) |
| 3 | Conclusion | **the entire conversation is resent as `input[]` every turn** |
| 4 | What is exempted | session store · response-id registry · expiry handling · cleanup path |
| 5 | Scaling | horizontal scaling for free |

## §2 The actual payload  {#s2-actual-payload}

`ResponsesApiRequest` — seventeen fields.

```rust
pub struct ResponsesApiRequest {
    pub model: String,
    pub instructions: String,            // skipped when empty
    pub input: Vec<ResponseItem>,
    pub tools: Option<ResponsesApiTools>,
    pub tool_choice: String,
    pub parallel_tool_calls: bool,
    pub reasoning: Option<Reasoning>,
    pub store: bool,
    pub stream: bool,
    pub stream_options: Option<StreamOptions>,
    pub include: Vec<String>,
    pub service_tier: Option<String>,
    pub prompt_cache_key: Option<String>,
    pub text: Option<TextControls>,
    pub client_metadata: Option<HashMap<String, String>>,
    pub access_programs: Option<AccessPrograms>,
}
```

The values actually filled in (`client.rs`):

```rust
tool_choice: "auto".to_string(),
store: false,
stream: true,
include: vec!["reasoning.encrypted_content".to_string()],
reasoning: Some(reasoning),          // always present
```

## §3 Three constants that remove work  {#s3-constants}

| Field | Value | What disappears |
|---|---|---|
| `tool_choice` | always `"auto"` | no `required` or named-tool mapping to implement |
| `stream` | always `true` | the non-streaming path can be omitted entirely |
| `instructions` | a top-level string | prepend it as a `system`/`developer` message and you are done |

## §4 Why this is good news  {#s4-why-good}

The hardest part of emulating the Responses API is normally **session state emulation.**
`store: false` plus the absence of `previous_response_id` removes the problem itself.

An adapter becomes **a pure function from one request to one upstream request.**

> ⚠️ Design discipline: **keep the adapter stateless.** The moment you add a response-id store, you
> have re-created by hand the hard problem `store: false` handed you for free.

## §5 The non-OpenAI path pre-cleans the input  {#s5-non-openai-path}

```rust
if !is_openai {
    for item in &mut input {
        item.clear_internal_chat_message_metadata_passthrough();
        if let ResponseItem::FunctionCall { encrypted_function_args, .. } = item {
            *encrypted_function_args = None;
        }
    }
}
```

When the provider is **not** named `openai`, Codex strips OpenAI-specific passthrough metadata and
encrypted function arguments before sending. The adapter gets cleaner input for free.

> The lever is the provider's **`name`** alone. A provider *named* `openai` but pointed at a proxy
> takes the OpenAI path and sends fields the adapter must then strip itself.

## §6 What statelessness does not solve  {#s6-what-remains}

Statelessness is a property of **transport**, not a preservation of capability. Resending the whole
conversation every turn means **the model's own prior reasoning must be resent too**, and its vehicle
is `encrypted_content`. What collapses when you cross to a wire without that vehicle is in
[[concepts/retained-reasoning]].

## §7 Read next  {#s7-next}

- [[concepts/retained-reasoning]] — the one thing statelessness cannot solve
- [[concepts/wire-protocol-boundary]] — the boundary that receives this payload
- Original: [`docs/16-responses-chat-adapter.md`](../../../docs/16-responses-chat-adapter.md) §1
