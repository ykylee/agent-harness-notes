# 05. Model Providers, the Model Abstraction, and Telemetry

> Read: the `Model` base classes and every first-party provider in `strands-py` and `strands-ts`, the event-loop streaming path, `models/routing/`, `experimental/bidi/`, `telemetry/`, the harness model resolver (`harness-py`, `harness-ts`), designs `0004` / `0015` / `0016`, and the `site/` provider and observability pages. Method: static reading only. No probe was run for this document. Source: `strands-agents/harness-sdk` @ `15da9dc` (2026-09-25; python/v1.57.1, typescript/v1.19.0, harness 0.x). Researched 2026-09-26.
>
> Dominant grade: ✅ **confirmed from source.** The designs are 📐. There are nine ❌ docs-vs-code refutations (§9).

## 1. The opposite of provider-as-data

Codex treats a provider as **a row of data on one wire**. `ModelProviderInfo` holds `base_url`, auth, headers and retries, and `wire_api` has one legal value, `Responses` ([../docs/15-model-providers.md](../docs/15-model-providers.md), [provider-as-data](../ai-workflow/wiki/concepts/provider-as-data.md), [wire-protocol-boundary](../ai-workflow/wiki/concepts/wire-protocol-boundary.md)). Strands makes the opposite choice. Its **internal wire is Bedrock Converse**, and **each provider is a class that translates into and out of that wire**.

### 1.1 The internal stream is ConverseStream, by declaration

```python
"""Streaming-related type definitions for the SDK.

These types are modeled after the Bedrock API.
"""
```
`strands-py/src/strands/types/streaming.py:1-5` ✅

- `StreamEvent` (`types/streaming.py:214-242`) is a `TypedDict` with the ConverseStream union keys: `messageStart`, `contentBlockStart`, `contentBlockDelta`, `contentBlockStop`, `messageStop`, `metadata`, `redactContent`, and Bedrock's own exception members (`throttlingException`, `validationException`, …). ✅
- `Usage` uses Converse's camelCase counters `inputTokens`, `outputTokens`, `totalTokens`, `cacheReadInputTokens` and `cacheWriteInputTokens` (`types/event_loop.py:8-23`). `StopReason` keeps Converse's snake_case values (`end_turn`, `tool_use`; `:43-66`). ✅
- **Bedrock does no translation.** `BedrockModel._stream` calls `converse_stream` and forwards each raw chunk (`strands-py/src/strands/models/bedrock.py:1448`, `:1475-1496`). The only thing it adds is synthesized guardrail-redaction events. ✅
- Every other provider pairs a `format_request` (Strands → vendor) with a `format_chunk` (vendor → ConverseStream). Examples: Anthropic `models/anthropic.py:465/699`, OpenAI Chat `models/openai.py:484/545`, OpenAI Responses `models/openai_responses.py:546/845`. ✅
- TypeScript keeps the Converse structure but renames it into a discriminated union (`modelMessageStartEvent` … `modelMetadataEvent`, `strands-ts/src/models/streaming.ts:21-28`). It also normalizes stop reasons, so `end_turn` becomes `endTurn` (`strands-ts/src/models/bedrock.ts:117`). ✅
- Before the call, messages are reduced to `role` and `content`, so metadata never reaches a provider (`strands-py/src/strands/event_loop/streaming.py:553-555`). ✅

### 1.2 What the choice buys and costs

| | Codex: one wire, many endpoints | Strands: one internal dialect, many wires |
|---|---|---|
| Adding a vendor | a TOML row, if the vendor speaks Responses | a class (a few hundred to 1,800 lines), or `client_args` / a Vercel adapter |
| Vendor-native features | only what the Responses API carries | reachable: Anthropic `cache_control` and signed thinking, Gemini `response_schema`, Bedrock guardrails |
| Chat Completions | removed; a proxy is needed ([../docs/16-responses-chat-adapter.md](../docs/16-responses-chat-adapter.md)) | first-class (`OpenAIModel` in Python) |
| Fidelity | a single lossless path | **N separate lossy translations**, each losing different things (§2.3, §6) |
| Cross-provider semantics | one usage schema | `Usage` looks uniform but its meaning differs by provider, so totals are **inferred arithmetically** (§6.2) |
| Extension by operators | config only | code only (§3) |
| Bedrock | one provider among several | zero-translation home turf; bare model strings default to Bedrock (§3) |

> 📌 Strands bets that **the content-block model matters more than the wire**. Converse blocks already carry `reasoningContent` with a signature, `citationsContent`, `guardContent` and `cachePoint`. That makes the dialect close to a superset, which fits a multi-vendor SDK. The price is that each converter decides on its own what to drop, and nothing enforces that the converters agree. Codex's bet is the reverse: one lossless wire, and vendors adapt to it.

## 2. The `Model` interface

### 2.1 Python

| Member | Kind | Location |
|---|---|---|
| `update_config`, `get_config` | abstract | `strands-py/src/strands/models/model.py:214`, `:224` |
| `structured_output(output_model, prompt, system_prompt)` | abstract async generator, ends with `{"output": T}` | `:234` |
| `stream(messages, tool_specs, system_prompt, *, tool_choice, system_prompt_content, invocation_state, cancel_signal, agent_metadata, **kwargs)` | abstract, returns `AsyncIterable[StreamEvent]` | `:255-267` |
| `stateful` | property, default `False` | `:194` |
| `count_tokens` | tiktoken `cl100k`, else chars/4 for text and chars/2 for JSON | `:299`, `:30-121` |
| `estimate_utilization` | input tokens ÷ `context_window_limit` | `:327` |

✅ The event loop also passes `model_state` and `dynamic_trailing_blocks` (`event_loop/streaming.py:558-569`). They are not in the abstract signature and arrive only through `**kwargs`. `OpenAIResponsesModel.stream` names `model_state` explicitly (`openai_responses.py:304`).

### 2.2 TypeScript

✅ `abstract class Model<T>` (`strands-ts/src/models/model.ts:312`) has abstract `updateConfig`, `getConfig` and `stream(messages, options)` (`:319-359`). `StreamOptions` includes `modelState` as a `StateStore` (`:222-257`). **There is no `structuredOutput` on the TS model.** Structured output exists only at the agent layer (§5).

### 2.3 Providers present at this commit

| Provider | Python | TypeScript |
|---|---|---|
| Bedrock (Converse) | `BedrockModel` `models/bedrock.py:144` | `BedrockModel` `strands-ts/src/models/bedrock.ts:384` |
| Anthropic | `AnthropicModel` `models/anthropic.py:81` | `AnthropicModel` `models/anthropic.ts:142` |
| OpenAI Chat Completions | `OpenAIModel` `models/openai.py:47` | `OpenAIModel({api:'chat'})` |
| OpenAI Responses | `OpenAIResponsesModel` `models/openai_responses.py:133` | `OpenAIModel` (the **default**, `models/openai/model.ts:43-81`) |
| Gemini | `GeminiModel` `models/gemini.py:32` | `GoogleModel` `models/google/model.ts:54` |
| LiteLLM / SageMaker | subclasses of `OpenAIModel` (`litellm.py:38`, `sagemaker.py:169`) | — |
| Mistral, Ollama, Llama API, llama.cpp, Writer | one class each | — (available only through the Vercel adapter) |
| Vercel AI SDK `LanguageModelV3` | — | `VercelModel` `models/vercel.ts:132` |

✅ Python has 12 providers. Only `BedrockModel` is imported eagerly; the others load lazily through `__getattr__` (`models/__init__.py:48-91`). TypeScript has 5. Community providers (xAI, OpenRouter, vLLM, …) are documented under `site/.../integrations/model-providers/` and ship as separate packages. ✅

> ⚠️ Python and TypeScript use **opposite OpenAI defaults**. In Python, `OpenAIModel` means Chat Completions. In TypeScript, `OpenAIModel` means Responses unless `api: 'chat'` is passed. TS's `api` field is the closest thing Strands has to a `wire_api`, and it is a constructor argument that cannot be changed later (`models/openai/model.ts:141-147`).

## 3. Model strings: Bedrock in the SDK, closed aliases in the harness

- ✅ In the core `Agent`, any string is a Bedrock model id, and `None` gives the default Bedrock model:
  ```python
  elif not model:
      self.model = BedrockModel()
  elif isinstance(model, str):
      self.model = BedrockModel(model_id=model)
  ```
  (`strands-py/src/strands/agent/agent.py:343-345`). The default is `global.anthropic.claude-sonnet-4-6` (`models/bedrock.py:44`). Passing `"anthropic/claude-…"` to a plain `Agent` produces a Bedrock request.
- ✅ The harness adds `"provider/name"` parsing (`harness-py/src/strands_harness/models.py:339-344`; a string without `/` is still treated as Bedrock). The lookup table `_PROVIDERS` (`:296-304`) maps seven ids to **builder functions**, not records. For example, `openai` → `OpenAIResponsesModel` (`:208-218`) and `bedrock-mantle` → `OpenAIResponsesModel(bedrock_mantle_config=…)` (`:221-230`). An unknown id fails:
  ```python
  "Pass a strands.models.Model instance for anything else."
  ```
  (`:443-449`). Endpoints can be overridden only through env vars (`ANTHROPIC_BASE_URL`, `OPENAI_BASE_URL`, `OLLAMA_HOST`, `LITELLM_BASE_URL`; `:74`, `:254`, `:265`). TypeScript has the same table (`harness-ts/src/models.ts:329-343`). The harness default is `bedrock/global.anthropic.claude-opus-5` (`harness-py/src/strands_harness/defaults.py:5`). ✅
- ✅ Per-model knowledge also lives in code tables keyed by id substrings: Claude `max_tokens` ceilings (`models.py:38-49`), adaptive vs extended thinking chosen by a version regex (`:89-111`), and reasoning-level vocabularies for gpt-5.6, gpt-oss, qwen and xai on Bedrock (`:81-175`).
- ✅ The harness config file extends models through a **code** reference. `modelModule` is `{kind:"model", module, export?, language?}` (`harness-py/src/strands_harness/config.py:283-315`, `:139-149`).

> 📌 `provider-as-data` gets a clear ❌ for Strands. There is no base_url + wire + auth record that an operator can add. A harness that needs operator-defined endpoints would have to build the layer Codex already ships: a data record that selects one of a small set of converter classes.

### 3.1 Parity drift inside the harness

- ❌ Python docstring (`harness-py/src/strands_harness/models.py:279-281`): Anthropic-direct web search should "stay `False` until the SDK grows a safe seam". The table right below it sets `"anthropic": Provider(..., web_search=True, ...)` (`:299`) and wires `anthropic_tools` (`:199-200`).
- ❌ TS comment (`harness-ts/src/models.ts:311-314`): Anthropic stays `false` until `@strands-agents/sdk 1.19.0`. But `harness-ts/package.json:72` already requires `>=1.19.0`, `anthropicTools` exists (`strands-ts/src/models/anthropic.ts:61-66`), and the flag is still `false` (`models.ts:338`). The docs say native web search "works on OpenAI, Anthropic, Google…" with no caveat for the TS harness (`site/src/content/docs/user-guide/harness/configure/model.mdx:162`).

## 4. Conversation state and reasoning across turns

### 4.1 Stateless by default, with one opt-out on Responses

✅ Every provider resends the full history on each request by default ([stateless-conversation-wire](../ai-workflow/wiki/concepts/stateless-conversation-wire.md)). The only exception is `OpenAIResponsesModel(stateful=True)` in Python, or `OpenAIModel({api:'responses', stateful:true})` in TS:

```python
"store": self.stateful,
...
response_id = model_state.get("response_id") if model_state else None
if response_id and self.stateful:
    request["previous_response_id"] = response_id
```
`strands-py/src/strands/models/openai_responses.py:578-583` ✅. In non-stateful mode the request **explicitly** sends `store: false`, as Codex does.

What stateful mode involves (all ✅):
- The response id is captured into `model_state` (`openai_responses.py:350-352`).
- `model_state` is owned by the agent (`agent/agent.py:496`). It is snapshotted before the model call and written back only on success (`event_loop/event_loop.py:601-624`), and it is persisted in sessions (`types/session.py:139,168`).
- `_ModelPlugin` clears `agent.messages` **after** each invocation (`models/model.py:353-381`; TS `strands-ts/src/plugins/model-plugin.ts:27-30`).
- Combining a stateful model with a conversation or context manager raises `ValueError` (`agent/agent.py:372-376`), and `NullConversationManager` is forced (`:398-399`).
- Routers reject stateful candidates (`models/routing/router.py:522-527`). Delegation is disabled (`agent/_agent_delegation.py:99-124`).

Design 0004 (`team/designs/0004-stateful-models.md`, **Status: Proposed**) against the code:

| Design | Code | Grade |
|---|---|---|
| `model_state` owned by the agent, passed through kwargs, persisted in the session, reset per swarm/graph node | as designed | ✅ |
| "the Agent clears `agent.messages` at the start of each top-level invocation" | cleared at `AfterInvocationEvent` (`models/model.py:362-369`) | ❌ |
| "If the user provides a different conversation manager, we emit a warning (not an exception)" | `raise ValueError` (`agent/agent.py:372-376`). The site docs agree with the code (`openai-responses.mdx:293`) | ❌ |
| `BedrockModel` split into `bedrock/{converse,responses}.py` with `api="responses"` | `bedrock.py` is still a single 1,790-line file. Mantle is reached through `OpenAIResponsesModel(bedrock_mantle_config=…)` | 📐 |
| user `conversation_id` → response-id map | no `conversation_id` anywhere in `strands-py/src`; only a single `response_id` | 📐 |

> ⚠️ In stateful mode, `_format_request` still puts **all** of the current invocation's messages into `input` alongside `previous_response_id` (`openai_responses.py:573-583`). Nothing trims to "messages since the last response". Inside a tool loop, the second request would therefore resend the user turn and the function call that the server already holds. The only stateful integration test has no tool call (`strands-py/tests_integ/models/test_model_openai.py:304-322`). This is unverified.

### 4.2 Retained reasoning depends on the provider

Compare [retained-reasoning](../ai-workflow/wiki/concepts/retained-reasoning.md): Codex always round-trips `encrypted_content`.

| Path | Reasoning on the next turn | Evidence |
|---|---|---|
| Anthropic direct | replayed as a signed `thinking` block | `models/anthropic.py:231-235`, `:738-756` ✅ |
| Bedrock Converse | `reasoningContent` kept in messages; filtered for DeepSeek | `models/bedrock.py:~895` ✅ |
| OpenAI Chat Completions | **dropped**, with a warning | `models/openai.py:410-419` ✅ |
| OpenAI Responses (py and ts) | **dropped**: "reasoningContent is not yet supported in multi-turn conversations" | `openai_responses.py:652-665`; `strands-ts/src/models/openai/responses-adapter.ts:205-207` ✅ |
| OpenAI Responses, `stateful=True` | held on the server | inferred from `store` + `previous_response_id` ⚠️ |

> 📌 Strands has no `include: ["reasoning.encrypted_content"]` anywhere. When an OpenAI reasoning model is used statelessly, its reasoning chain is lost every turn. That is the capability regression the wiki page describes for Chat Completions, and here it happens on the Responses path too.

## 5. Structured output: tool forcing at the agent layer

- ✅ In both SDKs the agent registers a `StructuredOutputTool` whose description begins `"IMPORTANT: This StructuredOutputTool should only be invoked as the last and final tool before returning the completed result to the caller."` (`strands-py/src/strands/tools/structured_output/structured_output_tool.py:38-42`). If the model ends on `end_turn` without calling it, the loop tries **once** more with `tool_choice={"tool":{"name":…}}` and an appended user prompt (`event_loop/event_loop.py:369-385`, `_structured_output_context.py:77-87`). A second miss raises `StructuredOutputException`. TS does the same (`strands-ts/src/agent/agent.ts:1540-1667`). See [02-agent-loop.md](02-agent-loop.md).
- ✅ Python also has a **deprecated** per-provider path (`Agent.structured_output`, `DeprecationWarning` at `agent/agent.py:1011-1014`), and it still has internal callers: the routing classifier, the goal judge and the HITL classifier (`models/routing/classifier_strategy.py:87`). Mechanism by provider:

| Mechanism | Providers |
|---|---|
| tool forcing (`tool_choice any`) | Bedrock (`bedrock.py:1693-1740`), Anthropic, Mistral |
| native schema | OpenAI Chat `beta.chat.completions.parse`, Responses `responses.parse(text_format=)` (`openai_responses.py:530`), Gemini `response_schema`, Ollama `format`, llama.cpp `json_schema`, SageMaker/Writer `response_format` |
| native if supported, else tool | LiteLLM |
| **none** | Llama API: `raise NotImplementedError(...)` (`models/llamaapi.py:479`) |

## 6. Caching and token accounting

### 6.1 Cache points

- ✅ `CacheConfig` (`models/model.py:135-170`) has `strategy` (`auto` | `anthropic`), `ttl`, `system_prompt_ttl` (default `True`), `tools_ttl` and `cache_key`. `cache_key` defaults to `strands-<session_id>` for providers that route caches by key.
- ✅ On Bedrock, `auto` resolves to `anthropic` **only** when the model id contains `claude` or `anthropic` (`bedrock.py:306-321`). Any other model gets a warning and no cache point (`:903-907`). The provider keeps exactly one `cachePoint` in the last user message, respects a cache point the caller placed, and removes older ones (`_inject_cache_point`, `:689-783`).
- ✅ OpenAI (Chat and Responses) sets only `prompt_cache_key` and `prompt_cache_retention` (`models/_openai_cache.py`). In Responses, `cachePoint` blocks are **dropped with a warning** (`openai_responses.py:657-658`).

### 6.2 Totals are inferred, and were wrong for Anthropic until the day before this commit

```python
Providers either fold cache tokens into ``inputTokens`` or report them separately; the totals tell
us which. ``inputTokens + outputTokens == totalTokens`` means cache is already inside
``inputTokens``; otherwise the cache counters are added on top.
```
`strands-py/src/strands/telemetry/metrics.py:187-190` ✅. This function drives the span's `gen_ai.usage.input_tokens`, `latest_context_size` and `projected_context_size` (`:229-262`). That means it also drives proactive compression.

- ✅ `21b314f` (2026-09-25), *fix(anthropic): include cache tokens in totalTokens (#4219)*. `totalTokens` changes from `input+output` to `input+output+cache_read+cache_write` in both SDKs (`models/anthropic.py:810-818`). The in-code rationale reads "Anthropic's input_tokens excludes tokens read from or written to the cache". ⚠️ Inference: before this fix, the heuristic treated Anthropic as "cache already folded in", so cache-heavy Anthropic runs under-reported prompt size and context utilization.
- ✅ `15399af` (2026-09-25), *fix(openai-responses): map cache_write_tokens to cacheWriteInputTokens (#4193)* (`openai_responses.py:926-929`). **TS still lacks this mapping.** `responses-adapter.ts:382-397` maps only `cached_tokens`.

> 📌 A cross-provider usage type does not make usage semantics the same across providers. Make each converter declare whether its input count includes cached tokens; do not infer it from sums.

## 7. Routing (design 0016) and bidirectional streaming (0015)

### 7.1 Routing is implemented, with changes from the design

✅ Routing exists in both SDKs (`strands-py/src/strands/models/routing/`, `strands-ts/src/models/routing/`), even though the design scoped TS as "later". `Agent(model=ModelRouter(...))` exposes the first candidate as `agent.model` (`agent/agent.py:338-341`). Selection runs as `InvokeModelStage.Input` middleware and keeps its state in `invocation_state` (`router.py:208`, `:289-305`). The invoke terminal reads `ctx.model` (`event_loop/event_loop.py:728`).

| Design says | Code | Grade |
|---|---|---|
| "Reactive fallback … is owned by `ModelRouter`, not individual selection strategies" | "The router orchestrates only … It has no failover policy" (`router.py:7-9`). The strategy is asked again with `attempts`, and `FallbackStrategy` is the default | ❌ |
| `RoutingCandidate.model: Model \| str \| ModelRouter` | `Model \| ModelRouter` (`router.py:91`, `:459`) | ❌ |
| the judge outcome is recorded on the model-invoke span | no span or attribute code in `models/routing/` or `telemetry/` | ⚠️ |
| sticky, cache-affinity routing (P1) | absent | 📐 |

✅ The code documents its own limitation (`router.py:38-44`): `agent.model` stays the first candidate, so proactive compression sizes against the wrong context window and `Agent.structured_output()` bypasses routing.

### 7.2 Bidi is a different contract

- ✅ Bidi is Python-only and experimental (`strands-py/src/strands/experimental/bidi/`). `BidiModel(Model)` **raises** `NotImplementedError` from both `stream()` and `structured_output()` (`bidi/models/model.py:78-84`). Its real interface is `start(system_prompt, tools, messages)`, `send`, `receive`, `stop`, plus an optional `restart` (`:32-165`).
- ✅ Models: Nova Sonic over `InvokeModelWithBidirectionalStream` (`bidi/models/bedrock.py:212`, `:382`), Gemini Live (`google.py:101`), and OpenAI Realtime over raw websockets (`openai.py:148`, `:311-319`).
- ✅ How it differs from the request/response loop:
  - The connection is held for the whole session, and history is sent only on connect or reconnect (`bidi/agent/loop.py:175`, `:497-509`). This is a second exception to the stateless wire.
  - Input and output run full duplex.
  - Barge-in and transcript events are part of the protocol.
  - `usage_is_cumulative` usage reporting (`model.py:62-66`).
  - Scheduled reconnects are announced 10 s ahead (`loop.py:47-50`).
  - Its own spans: `bidi_session`, `bidi_response`, `bidi_connect`, `bidi_connection_restart` (`bidi/_telemetry.py:33-179`).
- 📐 Design 0015 (WebRTC transport, **Proposed**) specifies `SignalingProvider`, `BidiWebRtcIO` and `BidiIvsIO`. None of them exist. `bidi/io/` contains only audio, text and transcript adapters. The only "webrtc" in the code is `pywebrtc_audio`, used for local echo cancellation (`bidi/_audio/processor.py:3-20`).

## 8. Observability

### 8.1 Spans

| Span | `gen_ai.operation.name` | Location |
|---|---|---|
| `invoke_agent {name}` | `invoke_agent` | `strands-py/src/strands/telemetry/tracer.py:761`, `:796` |
| `execute_event_loop_cycle` | same | `:668-680` |
| `chat` (model call) | `chat` | `:431-443` |
| `execute_tool {tool}` | `execute_tool` | `:527-540` |
| `memory.search/add/inject/extract` | — | `:1033-1246` |

- ✅ Every span is `SpanKind.INTERNAL`, including `chat`. ⚠️ The OTel GenAI conventions recommend `CLIENT` for inference spans.
- ✅ `gen_ai.system` (or, under the latest conventions, `gen_ai.provider.name`) is always the constant `"strands-agents"`, never the model vendor (`tracer.py:1271-1297`). TS uses the service name (`strands-ts/src/telemetry/tracer.ts:1061-1072`). Traces can be split by vendor only through `gen_ai.request.model`. The routed model id does reach the `chat` span (`event_loop.py:728-733`).
- ✅ `OTEL_SEMCONV_STABILITY_OPT_IN` tokens (`tracer.py:116-149`):
  - `gen_ai_latest_experimental`: uses the new attribute names, puts `gen_ai.input/output.messages` into `…inference.operation.details` events, and drops the old aliases.
  - `gen_ai_tool_definitions`.
  - `gen_ai_use_latest_invocation_tokens`.
  - `gen_ai_span_attributes_only`: switched on automatically when the endpoint looks like Langfuse (`:128`, `:198`).
  - `gen_ai_unredacted_attributes=<list>`: opt-in redaction of messages, system instructions and tool arguments/results. **The default is unredacted.**
- ✅ Usage attributes: `gen_ai.usage.input_tokens` and `prompt_tokens` (includes cached tokens, per §6.2), `output_tokens`, `total_tokens`, `cache_read.input_tokens`, `cache_creation.input_tokens`, `gen_ai.server.time_to_first_token`, and `gen_ai.server.request.duration` (`tracer.py:256-281`, `:465-472`).
- ✅ **What is on by default.** Spans are always created against the global OTel provider (`tracer.py:116-121`, which also calls `ThreadingInstrumentor().instrument()` unconditionally). Nothing is exported until `StrandsTelemetry().setup_otlp_exporter()` or `setup_console_exporter()` runs (`telemetry/config.py:126-170`). The harness says so directly: "a plain `Agent` just has nowhere to send them." It enables export only when `OTEL_TRACES_EXPORTER` is set (`harness-py/src/strands_harness/telemetry.py:1-13`).

### 8.2 Metrics

- ✅ `EventLoopMetrics` (`telemetry/metrics.py:206-262`) tracks cycles, per-tool metrics, per-invocation usage, accumulated usage, an in-process `Trace` tree, and `latest_context_size` / `projected_context_size`. It is returned on the agent result.
- ✅ The OTel instruments use **`strands.*` names, not GenAI conventions**: `strands.event_loop.cycle_count`, `strands.tool.duration`, `strands.event_loop.input.tokens`, `strands.model.time_to_first_token`, and others (`telemetry/metrics_constants.py`). `gen_ai.client.token.usage` and `gen_ai.client.operation.duration` do not appear in either SDK. Export is opt-in through `setup_meter(...)` (`config.py:173`).

### 8.3 Evals

✅ Evals are a separate repo and package: `strands-agents/evals`, imported as `strands_evals`, installed with `pip install strands-agents-evals` (`team/designs/0010-multimodal-i2t-evaluation.md:5-13`, `site/src/content/docs/user-guide/evals-sdk/index.mdx:54`). The docs site covers it, but this monorepo has no Evals source. Recorded here, not studied.

## 9. Docs vs code refutations

| # | Claim | Contradicting code | Grade |
|---|---|---|---|
| 1 | "The Python SDK implements structured output on each provider"; the Llama API row shows ✓ (`site/src/content/docs/user-guide/sdk/model-providers/index.mdx:49-66`) | `raise NotImplementedError("Strands sdk-python does not implement this in the Llama API Preview.")` (`models/llamaapi.py:479`) | ❌ |
| 2 | `gen_ai.usage.cache_read.input_tokens` "defaults to 0" when unsupported (`observability-evaluation/traces.mdx`) | emitted only `if "cacheReadInputTokens" in usage`, so the attribute is absent (`tracer.py:266-276`) | ❌ |
| 3 | Model-invoke spans carry `gen_ai.agent.name` (`traces.mdx`) | `start_model_invoke_span` does not set it (`tracer.py:431-443`; the caller is at `event_loop.py:730-737`) | ⚠️ likely ❌ |
| 4 | "When the OTEL_EXPORTER_OTLP_ENDPOINT environment variable is set, traces are sent to the OTLP endpoint" (`tracer.py:88-89`) | the `Tracer` installs no exporter; `StrandsTelemetry` does (`config.py:148-170`); the harness doc says the same | ❌ |
| 5 | Design 0004: messages cleared at invocation start; a warning on manager conflict | cleared after invocation; `ValueError` | ❌ ❌ |
| 6 | Design 0016: the router owns fallback; string candidates are allowed | the strategy owns fallback; no `str` | ❌ ❌ |
| 7 | Harness Anthropic web search "stay[s] False" (py docstring) or waits for 1.19.0 (ts) | py table sets `True`; ts dependency is already `>=1.19.0` | ❌ ❌ |
| 8 | Design 0015 WebRTC IO | not present | 📐 |
| 9 | Stateful Responses uses `previous_response_id`, clears history, and errors on a conversation manager (`openai-responses.mdx:265,293`) | matches | ✅ |

## 10. What this means if you are building a harness

- [ ] Decide first whether your core wire is **one external protocol** (Codex: Responses) or **one internal content model** (Strands: Converse blocks). You cannot defer this choice ([wire-protocol-boundary](../ai-workflow/wiki/concepts/wire-protocol-boundary.md)).
- [ ] If you choose an internal dialect, still keep a **data layer on top**: operator-defined `{base_url, auth, converter}` records. Strands forces users to write code even for a new endpoint that speaks an existing wire.
- [ ] Write down, for each converter, what it drops (reasoning, cache points, citations), and test round-trips. Strands' OpenAI paths drop reasoning without failing.
- [ ] Round-trip encrypted reasoning on Responses ([retained-reasoning](../ai-workflow/wiki/concepts/retained-reasoning.md)). Do not rely on server-side `store` to keep it.
- [ ] Have each provider declare whether its input-token count includes cached tokens. Do not infer it from `input + output == total`.
- [ ] Put the real vendor in `gen_ai.provider.name`, use `CLIENT` for inference spans, and emit `gen_ai.client.*` metrics if you want off-the-shelf GenAI dashboards to work.
- [ ] Redact span content by default. Strands defaults to emitting it unredacted.
- [ ] If you add routing, put the selected model on the per-call context, not on the shared agent. That is the part Strands got right. Also thread it through to context sizing, which Strands has not done.
- [ ] Treat a realtime/duplex model as a separate interface. Do not subclass the request/response `Model` and raise from `stream()`.

## 11. Open questions

- In stateful Responses mode, does a tool-loop turn resend items already stored under `previous_response_id` (§4.1)? This needs a run against the live API or a recording mock.
- How large was the Anthropic under-count before `21b314f` in practice, and did it change when proactive compression fired? The diff is read; the effect is not measured.
- Is `gen_ai.agent.name` ever present on `chat` spans through `trace_attributes` by default?
- Does TS lack Python's `cache_write_tokens` mapping by oversight or on purpose?
- The Evals SDK (`strands-agents/evals`) was not read.
- Shallow git history made it impossible to date when routing, stateful mode or bidi landed.
