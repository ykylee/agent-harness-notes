# 16. Feasibility: A Responses → Chat Completions Adapter

> Method: read the **exact wire payload Codex constructs** (`codex-rs/codex-api/src/common.rs`,
> `codex-rs/core/src/client.rs`), the **input item enum** (`codex-rs/protocol/src/models.rs`), and the
> **SSE events Codex parses** (`codex-rs/codex-api/src/sse/responses.rs`), then compared against
> `CreateChatCompletionRequest` / `ChatCompletionStreamResponseDelta` in the OpenAI OpenAPI spec.
> Analysed 2026-09-15.

## 0. Verdict

**Feasible, and easier than expected on the transport side — but it costs retained reasoning.**

| Dimension | Assessment |
|---|---|
| Request field mapping | ✅ Nearly complete. One constant value, no negotiation |
| Session state emulation | ✅ **Not needed.** Codex sends `store: false` and no `previous_response_id` |
| Input item mapping | ⚠️ 8 of 18 variants map cleanly; 5 are Responses-only tools; **1 has no equivalent at all** |
| Streaming output | ⚠️ Mechanical but real work — synthesize 25 semantic events from flat deltas |
| Reasoning continuity | ❌ **Structurally impossible.** Chat Completions has no reasoning item |
| Responses built-in tools | ❌ Absent. Must be disabled |

Build it if your target is **text + function calling against a third-party model**.
Do not build it expecting parity on OpenAI reasoning models.

## 1. What Codex actually sends

`ResponsesApiRequest` — the complete payload, 17 fields:

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

And the values it actually fills in (`client.rs`):

```rust
tool_choice: "auto".to_string(),
store: false,
stream: true,
include: vec!["reasoning.encrypted_content".to_string()],
reasoning: Some(reasoning),          // always present
```

> `previous_response_id` exists only on the **WebSocket** request variant, and the conversion from the
> HTTP payload sets it to `None`.

### Why this is good news

**`store: false` plus no `previous_response_id` means Codex is fully stateless on the wire.**
The entire conversation is resent as `input[]` on every turn.

An adapter therefore needs **no session store, no response-id registry, and no cleanup path**. It is a
pure function from one request to one upstream request, and it scales horizontally for free. This
removes what is normally the hardest part of emulating the Responses API.

Three more constants simplify things further:
- `tool_choice` is always `"auto"` — no `required` / named-tool mapping to implement
- `stream` is always `true` — the non-streaming path can be omitted entirely
- `instructions` is a top-level string, trivially prepended as a `system` / `developer` message

## 2. Request field mapping

| Responses field | Chat Completions | Notes |
|---|---|---|
| `model` | `model` | ✅ Direct |
| `instructions` | leading `system`/`developer` message | ✅ Straightforward |
| `input[]` | `messages[]` | ⚠️ See §3 |
| `tools` | `tools` | ⚠️ Function tools only |
| `tool_choice: "auto"` | `tool_choice: "auto"` | ✅ Constant |
| `parallel_tool_calls` | `parallel_tool_calls` | ✅ Direct |
| `reasoning.effort` | `reasoning_effort` | ✅ Request side maps |
| `reasoning.summary` | — | ❌ No output channel for it |
| `store: false` | `store` | ✅ Direct |
| `stream: true` | `stream` | ✅ Direct |
| `stream_options` | `stream_options` | ⚠️ Different meaning; Codex's carries `reasoning_summary_delivery` |
| `include: ["reasoning.encrypted_content"]` | — | ❌ No equivalent |
| `service_tier` | `service_tier` | ✅ Direct |
| `prompt_cache_key` | `prompt_cache_key` | ✅ Both inherit `CreateModelResponseProperties` |
| `text.format` (structured output) | `response_format` | ✅ Equivalent capability |
| `text.verbosity` | `verbosity` | ✅ Direct |
| `client_metadata` | `metadata` | ⚠️ Different semantics; can be dropped |
| `access_programs` | — | Codex sets `None`. Ignore |

**Score: 13 of 17 map directly or acceptably.** The two that matter are `reasoning.summary` and
`include: reasoning.encrypted_content`.

## 3. Input item mapping — `ResponseItem` has 18 variants

```
AdditionalTools   Message         AgentMessage        Reasoning
LocalShellCall    FunctionCall    ToolSearchCall      FunctionCallOutput
CustomToolCall    CustomToolCallOutput                ToolSearchOutput
WebSearchCall     ImageGenerationCall                 Compaction
ConfigurationUpdate   CompactionTrigger   ContextCompaction   Other
```

| Variant | Chat Completions equivalent | Verdict |
|---|---|---|
| `Message` | `user` / `assistant` / `system` message | ✅ |
| `AgentMessage` | `assistant` message | ✅ |
| `FunctionCall` | `assistant.tool_calls[]` | ✅ |
| `FunctionCallOutput` | `tool` message with `tool_call_id` | ✅ |
| `Compaction`, `ContextCompaction`, `CompactionTrigger` | flatten into message text | ✅ Internal bookkeeping |
| `ConfigurationUpdate` | flatten or drop | ✅ |
| `Other` | drop | ✅ |
| `CustomToolCall` / `CustomToolCallOutput` | function call with a string payload | ⚠️ Lossy. Custom tools accept **freeform, non-JSON** input; Chat's function calling is JSON-argument shaped |
| `LocalShellCall` | — | ❌ Responses-native tool |
| `WebSearchCall` | — | ❌ Server-side tool at OpenAI |
| `ImageGenerationCall` | — | ❌ Server-side tool |
| `ToolSearchCall` / `ToolSearchOutput` | — | ❌ Responses-native |
| `AdditionalTools` | — | ❌ Responses-native |
| **`Reasoning`** | **— (none)** | ❌ **The blocker. See §5** |

**8 variants map cleanly, 4 are droppable bookkeeping, 5 are Responses-native tools, 1 is the blocker.**

The five Responses-native tools are not an adapter problem — they are server-side capabilities that a
third-party Chat endpoint simply does not have. Codex must be configured without them.

## 4. Output: synthesizing 25 events from flat deltas

Codex's SSE parser handles these:

```
response.created                     response.in_progress
response.output_item.added           response.output_item.done
response.content_part.added          response.content_part.done
response.output_text.delta           response.output_text.done
response.function_call_arguments.delta / .done
response.custom_tool_call_input.delta / .done
response.mcp_call_arguments.delta
response.reasoning_summary_part.added / .done
response.reasoning_summary_text.delta / .done
response.reasoning_text.delta        response.refusal.delta
response.new_tool_event              response.metadata
response.completed  response.failed  response.incomplete  error
```

Chat Completions gives you one chunk type. `ChatCompletionStreamResponseDelta` has exactly:

```
content   function_call   tool_calls   role   refusal   (+ logprobs)
```

So the adapter must run a **state machine that manufactures item lifecycles from a flat token stream**:

| Chat signal | Events to synthesize |
|---|---|
| first `delta.content` | `response.created` → `output_item.added`(message) → `content_part.added` |
| subsequent `delta.content` | `response.output_text.delta` |
| content ends | `content_part.done` → `output_text.done` → `output_item.done` |
| `delta.tool_calls[i]` first seen | `output_item.added`(function_call) with a **generated id** |
| `delta.tool_calls[i].function.arguments` | `function_call_arguments.delta` |
| `finish_reason: "tool_calls"` | `function_call_arguments.done` → `output_item.done` |
| `delta.refusal` | `response.refusal.delta` |
| `finish_reason: "stop"` + usage | `response.completed` with the assembled `output[]` and usage |
| `finish_reason: "length"` | `response.incomplete` |
| upstream error | `response.failed` / `error` |

Two things the adapter must own that Chat does not provide:
- **Item IDs.** Responses items are addressable; Chat chunks are not. Generate stable synthetic ids
- **The assembled `output[]` array** on `response.completed`. Chat never sends the final assembled
  message in the stream, so the adapter must accumulate it

This is bounded, testable work — a few hundred lines with a good test matrix — but it is the bulk of
the implementation.

## 5. The blocker: reasoning

### What Codex sends and expects back

```rust
Reasoning {
    id: Option<ResponseItemId>,
    summary: Vec<ReasoningItemReasoningSummary>,
    content: Option<Vec<ReasoningItemContent>>,
    encrypted_content: Option<String>,
    internal_chat_message_metadata_passthrough: Option<...>,
}
```

`Reasoning` is a **first-class input item**. Because `store: false`, Codex must resend the model's own
prior reasoning — carried in `encrypted_content` — on every subsequent turn. That is the mechanism by
which a stateless client keeps a reasoning model's chain across a multi-step task.

And Codex requests it unconditionally:

```rust
let include = vec!["reasoning.encrypted_content".to_string()];
```

Not feature-gated. Not conditional on the model. Always.

### What Chat Completions offers

Nothing. `ChatCompletionStreamResponseDelta` has no reasoning field, and there is no assistant-message
slot to put an opaque reasoning blob into for the next request. `reasoning_effort` exists on the
**request**, but there is no corresponding **output** representation.

Some third-party servers emit a non-standard `reasoning_content` field (a vLLM/DeepSeek-ecosystem
convention). That is not in the OpenAI spec, is not encrypted, and is not round-trippable as an
opaque token. An adapter can surface it as a reasoning *summary* for display, but it cannot restore
continuity.

### What is actually lost

Reasoning is dropped at the turn boundary. Each turn starts the model's reasoning fresh.

This is precisely the capability that the harness-engineering material credits for large gains —
retained reasoning and context compaction were cited as moving GPT-5.6 Sol on ARC-AGI-3 from 13.3% to
38.3% while using six times fewer output tokens (*secondary source; see
[99-sources.md](99-sources.md)*). Whatever the exact figures, **retained reasoning is a load-bearing
part of the design, not an optimization.**

For a non-reasoning third-party model this costs nothing — there is no chain to retain.
**The loss is proportional to how much the target model reasons.**

## 6. Reference architecture

```
┌───────────────┐   POST /v1/responses      ┌──────────────────────┐
│  Codex core   │   store:false, stream:true│   Responses→Chat     │
│  (unmodified) │ ─────────────────────────▶│   adapter (stateless)│
│               │◀───────────────────────── │                      │
└───────────────┘   SSE: 25 event types     └──────────┬───────────┘
                                                        │ POST /v1/chat/completions
                                                        ▼
                                             ┌──────────────────────┐
                                             │  third-party model   │
                                             └──────────────────────┘
```

Wired in exactly like the in-repo proxy precedent:

```toml
[model_providers.chat-adapter]
name = 'chat-adapter'
base_url = 'http://127.0.0.1:60001/v1'
wire_api = 'responses'
```

Because the adapter is stateless, it can run as a sidecar, a shared service, or in-process.

## 7. Effort shape

| Component | Difficulty | Why |
|---|---|---|
| Request translation | Low | 13/17 fields direct; constants remove branching |
| Input item → messages | Low–medium | 8 real mappings; the rest drop |
| Tool definition translation | Low | Function tools are near-identical |
| **Streaming state machine** | **Medium — the bulk** | Item lifecycle synthesis, id generation, output accumulation |
| Error and finish-reason mapping | Low | Small closed set |
| Reasoning bridging | **Not solvable** | Ship the degradation, document it |

No session store, no id registry, no expiry logic — all avoided by `store: false`.
The risk concentrates in one testable component rather than spreading across the design.

## 8. Recommendation

**Build the adapter** if the requirement is "support third-party models that only speak Chat
Completions." It is a bounded, stateless component wired in at a supported extension point, and it
leaves Codex core untouched — so upstream updates keep working.

**Do not build it** if the requirement is "run OpenAI reasoning models over Chat Completions." You
would be paying adapter complexity to get a strictly worse version of a path that already works.

**Design consequences either way:**
- Treat reasoning retention as a **per-provider capability**, not a global assumption.
  `ModelProviderInfo` already has the shape for this (`supports_websockets`,
  `supports_standalone_web_search`) — add `supports_retained_reasoning` and let the harness adapt
- Disable the five Responses-native tool item types for Chat-backed providers, and make that visible
  in the UI rather than a silent absence
- Make `include` conditional in your fork or your own core. Codex hardcodes
  `reasoning.encrypted_content`; a multi-provider harness cannot
- Keep the adapter stateless. The moment you add a response-id store you have re-created the hard
  problem that `store: false` handed you for free

## 9. Open items

- `response.new_tool_event` and `response.metadata` were not investigated; both appear Codex/OpenAI
  specific and likely need no Chat-side source
- `stream_options.reasoning_summary_delivery: SequentialCutoff` is applied only when the provider is
  OpenAI and summaries are enabled — confirm an adapter can simply omit it
- The `ResponsesApiTools` shape was not expanded field by field; tool translation is assumed
  near-identical based on the function-tool schema but deserves verification before implementation
