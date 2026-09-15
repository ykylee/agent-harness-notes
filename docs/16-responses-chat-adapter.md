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
| Streaming output | ✅ **Smaller than it looks** — Codex acts on 12 events; 7 suffice for a text + function-calling adapter |
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

## 4. Output: only 12 events are actually handled

The parser *recognizes* 25 event types, but most fall into a trace-only arm. The real dispatch
produces a `ResponseEvent` for exactly these:

| Event | Payload Codex reads |
|---|---|
| `response.created` | `response.id` → `ResponseEvent::Created { response_id }` |
| `response.output_item.added` | `item` parsed as a full `ResponseItem` |
| `response.output_item.done` | `item` parsed as a full `ResponseItem` |
| `response.output_text.delta` | `delta` string |
| `response.completed` | `response` parsed as `ResponseCompleted`, `usage` captured separately |
| `response.failed` | `response` → stream error |
| `response.incomplete` | terminal |
| `response.custom_tool_call_input.delta` | freeform-tool input streaming |
| `response.reasoning_summary_text.delta` / `.done` | reasoning summary |
| `response.reasoning_text.delta` | raw reasoning |
| `response.reasoning_summary_part.added` | `summary_index` |

And these are **explicitly ignored** (matched, then `trace!("unhandled responses event")`):

```
response.content_part.added        response.content_part.done
response.custom_tool_call_input.done
response.function_call_arguments.delta    response.function_call_arguments.done
response.in_progress               response.metadata
response.output_text.done          response.reasoning_summary_part.done
responsesapi.websocket_timing
```

Plus two catch-alls: anything ending in `.delta`, and a final `_ =>` debug arm.

### Three consequences that shrink the work

**1. Tool-call argument streaming is not required.**
`response.function_call_arguments.delta` and `.done` are ignored. Codex gets the complete function
call from `response.output_item.done`. The adapter can accumulate Chat's
`delta.tool_calls[i].function.arguments` fragments and emit **one finished item** — no incremental
tool-call plumbing, no per-index streaming state exposed upstream.

**2. Content-part lifecycle is not required.**
`content_part.added` / `.done` and `output_text.done` are all ignored. Text streaming needs only
`output_item.added` → N × `output_text.delta` → `output_item.done`.

**3. The parser is tolerant of omissions and unknowns.**
Unknown event kinds hit the debug catch-all rather than erroring, so the adapter only has to emit
what it can genuinely source.

### The minimum event set

For a text + function-calling adapter, **seven events**:

```
response.created
response.output_item.added        response.output_item.done
response.output_text.delta
response.completed  |  response.failed  |  response.incomplete
```

Reasoning events are moot (Chat has no reasoning), and `custom_tool_call_input.delta` only matters
if freeform tools are in play — which a Chat provider cannot support anyway.

### Mapping from Chat chunks

| Chat signal | Emit |
|---|---|
| stream opens | `response.created` with a generated `response.id` |
| first `delta.content` | `output_item.added` (message item) |
| each `delta.content` | `output_text.delta` |
| first `delta.tool_calls[i]` | buffer; emit nothing yet |
| `finish_reason: "tool_calls"` | one `output_item.done` per accumulated call (function_call item) |
| `finish_reason: "stop"` | `output_item.done` (message) then `response.completed` |
| `finish_reason: "length"` | `response.incomplete` |
| upstream error | `response.failed` |

The adapter still owns **item id generation** and **assembling the final `output[]`** for
`response.completed`.

> **Do not forget `stream_options: {include_usage: true}` on the Chat request.** Without it the
> final chunk carries no usage, and `response.completed` has nothing to report. Note this is a
> *different* `stream_options` than the one Codex sends (see §9).

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
| **Streaming state machine** | **Low–medium** | 7 events; tool-call args accumulate rather than stream. Still owns id generation and `output[]` assembly |
| Error and finish-reason mapping | Low | Small closed set |
| Reasoning bridging | **Not solvable** | Ship the degradation, document it |

No session store, no id registry, no expiry logic — all avoided by `store: false`.
And because Codex ignores the fine-grained lifecycle events, the streaming component is a good deal
smaller than the 25-event surface first suggests.

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

## 9. The three open items, resolved

All three were verified against the source. Two shrink the work; one adds a risk that was missed.

### 9.1 `response.new_tool_event` and `response.metadata` — no Chat source needed ✅

**`response.new_tool_event`** is not handled at all. Its own test case is named `"unknown"` and
asserts that the event produces nothing and falls through to the debug catch-all. It exists as
forward-compatibility tolerance. **The adapter never emits it.**

**`response.metadata`** is in the trace-only arm of the main dispatch, but it carries side-channel
data read through accessor methods:

| Accessor | Reads | Purpose |
|---|---|---|
| `turn_state()` | `headers` | Turn-state passthrough |
| `model_verifications()` | `metadata.openai_verification_recommendation` | Trusted Access for Cyber |
| `turn_moderation_metadata()` | `metadata.openai_chatgpt_moderation_metadata` | ChatGPT moderation presentation |
| `safety_buffering()` | `metadata.type == "safety_buffering"`, or a top-level `safety_buffering` field which **wins** over the nested one | Safety-buffering UI, `retry_model` |
| `response_model()` | `headers["openai-model"]` | Actual model used (rerouting) |

Every one of these is an OpenAI-platform concern. A third-party Chat endpoint has no source for any
of them — and needs none. Omitting `response.metadata` entirely is correct: each accessor returns
`None`, which is exactly "not applicable."

### 9.2 `stream_options` — never sent to a non-OpenAI provider ✅

Codex's `stream_options` is **not** the standard OpenAI field. It is:

```rust
pub enum ReasoningSummaryDelivery { SequentialCutoff }
pub struct StreamOptions { pub reasoning_summary_delivery: ReasoningSummaryDelivery }
```

And it is gated three ways:

```rust
let stream_options = (self.state.concurrent_reasoning_summaries_enabled
    && is_openai
    && reasoning.summary.is_some())
.then_some(StreamOptions { ... });
```

`is_openai()` is a **literal name comparison**:

```rust
pub fn is_openai(&self) -> bool { self.name == OPENAI_PROVIDER_NAME }
```

So any provider not named `openai` **never receives this field at all.** The adapter can ignore it
completely. (It must still set the *standard* `stream_options.include_usage` on its own Chat request
— different field, same name.)

### 9.3 Tool translation — mostly mechanical, with two real problems ⚠️

`ToolSpec` has **five** variants, not one:

```rust
pub enum ToolSpec {
    Function(ResponsesApiTool),        // type: "function"
    Namespace(ResponsesApiNamespace),  // type: "namespace"
    ToolSearch { .. },                 // type: "tool_search"
    WebSearch { .. },                  // type: "web_search"
    Freeform(FreeformTool),            // type: "custom"
}
```

**Function tools translate, but the shape differs.**

```rust
pub struct ResponsesApiTool {
    pub name: String,
    pub description: String,
    pub strict: bool,
    pub defer_loading: Option<bool>,
    pub parameters: JsonSchema,
    #[serde(skip)] pub output_schema: Option<ToolOutputSchema>,  // never sent
}
```

Responses emits this **flat** under `{"type":"function", ...}`. Chat Completions **nests** it:
`{"type":"function","function":{name, description, strict, parameters}}`. A mechanical re-wrap.
`defer_loading` has no Chat equivalent (it belongs to tool search) — drop it.

**Problem 1 — `Namespace` has no Chat equivalent.**

```rust
pub struct ResponsesApiNamespace {
    pub name: String,
    pub description: String,
    pub tools: Vec<ResponsesApiNamespaceTool>,   // Function | Custom
}
```

Chat has a flat tool list. The adapter must **flatten namespaces**, which means prefixing tool names
to avoid collisions across namespaces — and then **un-prefixing them on the way back** when the model
calls one. That is a bidirectional name rewrite, and it is the one place the adapter holds per-request
derived state.

Namespaces are not hypothetical: `create_tools_json_for_responses_lite` builds a default namespace,
and provider capabilities carry a `namespace_tools` flag.

**Problem 2 — `Freeform` (custom) tools cannot round-trip.**

```rust
pub struct FreeformToolFormat { pub r#type: String, pub syntax: String, pub definition: String }
```

A custom tool declares a **grammar** (syntax + definition) and accepts non-JSON input. Chat's function
calling is JSON-arguments only. The best approximation is a function with a single string parameter,
which discards the grammar constraint — the model loses the structure it was supposed to emit against.

`ToolSearch` and `WebSearch` are Responses-native server-side tools; drop them, as established in §3.

## 10. Two findings that change the design

Both surfaced while resolving the open items.

### 10.1 Codex already has a non-OpenAI code path — use it

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

When the provider is not named `openai`, Codex **strips OpenAI-specific passthrough metadata and
encrypted function arguments before sending.** The adapter gets cleaner input for free, and two
fields it would otherwise have to discard never arrive.

The lever is just the provider `name`. Worth knowing that a provider *named* `openai` pointed at a
proxy would take the OpenAI path and send fields the adapter must then strip itself.

### 10.2 There is a second request shape: `responses_lite` ⚠️

This was missed in the first pass. When `model_info.use_responses_lite` is set, the request is built
differently:

```rust
let (instructions, tools) = if model_info.use_responses_lite {
    // ... build an AdditionalTools item + a base-instructions message,
    input.splice(0..0, prefix);
    (String::new(), None)          // top-level instructions AND tools are emptied
} else {
    (prompt.base_instructions.text.clone(), Some(create_tools_raw_json_for_responses_api(...)))
};
```

In lite mode:
- top-level `instructions` is **empty** and `tools` is **`None`**
- instead, the input array is prefixed with a `ResponseItem::AdditionalTools { role: "developer", tools }`
  and a base-instructions message
- item ids are derived as `Uuid::v5` over the thread id and the serialized payload, so retries and
  resumed sessions keep stable identity
- tool JSON is built by `create_tools_json_for_responses_lite` (namespaced) or
  `create_tools_json_for_responses_api`, depending on the provider's `namespace_tools` capability

**An adapter must handle both shapes**, or it will see a request with no tools and no instructions and
silently drop both. Since `AdditionalTools` was listed in §3 as a Responses-native variant with no
mapping, this is a correction: in lite mode it is **not droppable** — it *is* the tool list.

#### When lite mode is actually on

`use_responses_lite` is a **per-model catalog flag**, not a config setting. From
`codex-rs/models-manager/models.json`:

| Model | `use_responses_lite` |
|---|:---:|
| `gpt-6-astra` | **true** |
| `gpt-5.6-sol` | **true** |
| `gpt-5.6-terra` | **true** |
| `gpt-5.6-luna` | **true** |
| `gpt-daybreak-blue-latest` | **true** |
| `gpt-daybreak-red-latest` | **true** |
| `codex-auto-review` | **true** |
| `gpt-5.5` | false |
| `gpt-5.4` | false |

**Every current-generation model is lite; only the older ones use the classic shape.** Lite is the
forward direction, so an adapter that handles only the classic shape is writing against the legacy path.

#### How a slug resolves to that flag

`construct_model_info_from_candidates` tries three things in order:

1. **Longest-prefix match** — `find_model_by_longest_prefix` keeps any candidate where
   `model.starts_with(&candidate.slug)`, and the **longest matching slug wins**
2. **One-level namespace strip** — `find_model_by_namespaced_suffix` splits a single
   `namespace/model` slug (namespace must be `[A-Za-z0-9_-]+`, suffix must contain no further `/`)
   and retries the prefix match
3. **Fallback** — `model_info_from_slug`, which logs
   `warn!("Unknown model {slug} is used. This will use fallback model metadata.")`,
   sets `used_fallback_model_metadata: true`, and leaves `use_responses_lite: false`

#### The trap

**Prefix matching means a slug that merely starts with a catalog slug inherits its flags.**

```
"gpt-6-astra-turbo"        → prefix-matches "gpt-6-astra"  → use_responses_lite = true
"myprovider/gpt-6-astra"   → namespace strip → same match  → use_responses_lite = true
"llama-3.3-70b"            → no match → fallback           → use_responses_lite = false
```

So naming a third-party model with an OpenAI-shaped prefix **silently changes the request shape**
the adapter receives. Conversely, an unrelated name lands in the fallback — which gives the classic
shape but also a generic `context_window` of 272,000 and a warning on every resolution.

#### There is no config knob — use `model_catalog_json`

`with_config_overrides` touches only `context_window`, `auto_compact_token_limit`, the truncation
policy, and base instructions / personality. **`use_responses_lite` cannot be overridden from
`config.toml`.**

The control point is **`model_catalog_json`** — a path to a JSON model catalog loaded at startup
(and overridable per profile). Supplying your own catalog entry for each third-party model is the
way to pin the request shape *and* fix the context window at the same time. Candidates can also
arrive from the provider's own remote model list.

**Recommendation for the adapter:** ship a `model_catalog_json` with explicit entries for every
model you support, each with `use_responses_lite` set deliberately. Do not rely on prefix-match
luck, and do not rely on the fallback — its metadata is wrong for most non-OpenAI models.

## 11. Net effect on the verdict

Nothing overturns §0, but the balance shifts:

| Item | Direction |
|---|---|
| Only 12 events handled, 7 needed | **Easier** |
| Tool-call arguments need no streaming | **Easier** |
| `stream_options` never sent to non-OpenAI providers | **Easier** |
| `response.metadata` / `new_tool_event` need no source | **Easier** |
| Non-OpenAI path pre-strips OpenAI-only fields | **Easier** |
| Namespace flattening needs bidirectional name rewriting | **Harder** |
| Freeform tools lose their grammar | **Harder** |
| `responses_lite` is a second request shape | **Harder — and was missed** |

The streaming work is smaller than estimated; the tool work is larger. Reasoning remains the only
structural loss.
