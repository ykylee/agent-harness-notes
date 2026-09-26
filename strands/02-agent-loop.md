# 02. The Agent Loop — cycles, messages, and who owns history

> Read: the Python event loop, `Agent`, `types/`, conversation/context/session managers and the
> providers where they touch history; the TS SDK cross-checked on the same points; designs 0003–0005,
> 0008, 0009, 0011, 0014, 0015, 0018 (`team/designs/`); the `site/` loop, streaming, conversation and
> session pages. Method: **static reading only** — no probe was run for this document.
> Source: `strands-agents/harness-sdk` @ `15da9dc` (2026-09-25; python/v1.57.1, typescript/v1.19.0,
> harness 0.x). Researched 2026-09-26.
>
> Grade: mostly ✅ **confirmed from source**. There are two ❌ refutations: one against the site docs
> and one against design 0004.

## 1. The loop in one picture

### 1.1 Python recurses; TypeScript iterates ✅

```
Agent.stream_async                        agent.py:1250
 └─ _run_loop  (while: hook-driven resume/continuation passes)   agent.py:1447
     └─ AgentStreamStage middleware → _execute_event_loop_cycle   agent.py:1719
         └─ event_loop_cycle                                      event_loop.py:189
             ├─ _check_limits            (top of every cycle)      :240
             ├─ _handle_model_execution  (while True: hook retry)  :470, :504
             └─ stop_reason == "tool_use"
                 └─ _handle_tool_execution                         :802
                     └─ recurse_event_loop → event_loop_cycle      :1023 → :413
```

- **Python.** Each tool round is one more nested async generator
  (`strands-py/src/strands/event_loop/event_loop.py:413-454`). Every streamed event of cycle *N*
  bubbles up through *N* `async for` frames.
- **Python, context overflow.** Recovery is a second recursion: `_execute_event_loop_cycle` catches
  `ContextWindowOverflowException`, calls `conversation_manager.reduce_context`, and calls itself
  (`strands-py/src/strands/agent/agent.py:1755-1765`).
- **TypeScript.** A flat `while (true)` ("Main agent loop", `strands-ts/src/agent/agent.ts:1582-1584`)
  inside an outer resume loop (`:1157`). The site's "recursive structure at the heart of the loop"
  (`agent-loop.mdx:45`) is literal for Python, metaphorical for TS. ✅

> ⚠️ Neither SDK bounds the loop by default. `limits` is optional
> (`strands-py/src/strands/types/agent.py:113-145`), and a grep for `max_cycles`, `max_turns` or
> `recursion` finds no guard in the Python loop. No test was found for how deep the nested
> async-generator chain can go before it degrades. This is an open risk, not a measured one.

### 1.2 One cycle, step by step ✅

| Step | What happens | Where |
|---|---|---|
| 1 | Limit check. If tripped, stop with `limit_*` and `agent.messages[-1]` | `event_loop.py:240-251` |
| 2 | Skip the model call if resuming a tool interrupt, or if the last message already holds a `toolUse` | `:285-293` |
| 3 | Estimate input tokens (last `metadata.usage` baseline + `count_tokens` on newer messages) | `:125-165`, `:509` |
| 4 | `BeforeModelCallEvent` hooks. May `cancel`, which yields a synthetic `end_turn` | `:533-562` |
| 5 | **Deep-copy `agent.messages`**, snapshot `_model_state`, run the `InvokeModelStage` middleware chain | `:584`, `:597`, `:603-609` |
| 6 | `AfterModelCallEvent` hooks. `retry=True` loops back. Throttling retry is itself a hook strategy | `:633-681`, `event_loop/_retry.py` |
| 7 | Append the assistant message to history | `:699` |
| 8 | `max_tokens`: rewrite every `toolUse` into an error text block, then raise `MaxTokensReachedException` | `_recover_message_on_max_tokens_reached.py:14-74`, `event_loop.py:313-322` |
| 9 | `tool_use`: `BeforeToolsEvent`, then the executor, then `AfterToolsEvent` (always paired, inside `finally`) | `:850-935` |
| 10 | Append all tool results as **one `user` message**, then recurse | `:960`, `:1023` |

After every pass, `conversation_manager.apply_management` runs in a `finally` block
(`agent.py:1611`). This is where the default sliding window trims.

### 1.3 Stop reasons ✅

| Python (`types/event_loop.py:39`) | TS (`strands-ts/src/types/messages.ts:710-725`) | Origin |
|---|---|---|
| `end_turn`, `tool_use`, `max_tokens`, `stop_sequence`, `content_filtered`, `guardrail_intervened` | camelCase equivalents | model |
| `limit_turns`, `limit_total_tokens`, `limit_output_tokens` | `limitTurns`, … | loop (`limits`) |
| `cancelled`, `interrupt`, `checkpoint` | same | loop |
| — | `pauseTurn`, `refusal`, `modelContextWindowExceeded`, plus any string (`(string & {})`) | TS only |

- Python's `StopReason` is closed at 12 values. TS has 15 named values and is open-ended.
- Hook cancellation produces `end_turn` with a synthetic assistant message, not `cancelled`
  (`agent.py:1480-1488`; `event_loop.py:533-562`, `:968-988`).
- The site's stop-reason list (`agent-loop.mdx:99-128`) omits `interrupt` and `checkpoint`, as well as
  the three TS-only values. That is a gap in the docs, not an error.

### 1.4 Limits and cancellation ✅

```python
turns: Maximum number of agent loop iterations (turns). One turn is one model
    call plus any tool execution that follows.
```

— `strands-py/src/strands/types/agent.py:129-131`

Checked at cycle boundaries only, so token caps are soft ("a single oversized response can
overshoot", `:132-140`); scoped per invocation via `latest_agent_invocation`
(`event_loop.py:69-102`). TS: `LIMITS_KEYS` (`strands-ts/src/types/agent.ts:199`), `_checkLimits`
(`agent.ts:920-938`).

> 📌 **Vocabulary trap.** A Strands "turn" is **one model-request cycle**. That is what Codex's
> legacy protocol_v1 called a turn
> ([thread-turn-item §6](../ai-workflow/wiki/concepts/thread-turn-item.md)). The App Server's turn is
> different: one unit of work started by user input. Strands' closest equivalent to the App Server
> turn is the *invocation*, which has no durable id.

Python cancellation uses a `threading.Event` (`agent.py:604-639`), optionally linked to a
caller-owned `cancel_signal`. It is observed at four points:

| Point | Effect | Where |
|---|---|---|
| Between stream chunks | Partial message discarded, replaced by "Cancelled by user"; never appended | `streaming.py:461-473` |
| Provider aborts without `messageStop` | Also reported as `cancelled` | `streaming.py:499-507` |
| Before tools | Synthetic error `toolResult`s keep history valid | `event_loop.py:875-889` |
| After tools | Stop with `cancelled` | `:1000-1007` |

TS uses `AbortSignal.any` over its own controller and the caller's signal
(`strands-ts/src/agent/agent.ts:1158-1162`), and checks it at the top of each cycle (`:1585`).

## 2. Units and the message model

### 2.1 No thread/turn/item — messages and content blocks ✅

| Codex App Server ([docs/02 §4](../docs/02-app-server-protocol.md)) | Strands (Python) | Durable id |
|---|---|---|
| Thread | `Session` + `SessionAgent` (`types/session.py:107-188`) | `session_id`, `agent_id` |
| Turn (user-initiated) | invocation, i.e. one `agent(...)` call → `AgentResult` | none |
| — (protocol_v1 "turn") | cycle (`event_loop_cycle_id = uuid4()`, `event_loop.py:254`) | trace only |
| — | `Message{role, content, tracking_id?, metadata?}` (`types/content.py:252-270`) | `tracking_id` (UUIDv4) |
| Item (`started → delta → completed`) | `ContentBlock` | only `toolUseId` |

- Strands has **no item lifecycle** on the wire. A caller sees raw deltas and then a whole `message`
  (§3). There is no per-block "started/completed" with an id.
- `tracking_id` is durable and is stripped before model calls (`content.py:273-300`). It identifies
  messages, not blocks.
- Experimental checkpoints (`after_model` / `after_tools`, indexed by `cycle_index`) make the cycle
  semi-durable when `checkpointing=True`
  (`strands-py/src/strands/experimental/checkpoint/checkpoint.py:42-46`; `agent.py:218`).

### 2.2 The type system is Bedrock Converse ✅

```python
"""... These types are modeled after the Bedrock API.

- Bedrock docs: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_Types_Amazon_Bedrock_Runtime.html
```

— `strands-py/src/strands/types/content.py:4-6`

- `ContentBlock` is a `TypedDict(total=False)` with one key set. The keys are `text`, `toolUse`,
  `toolResult`, `reasoningContent`, `image`, `document`, `video`, `audio`, `cachePoint`,
  `guardContent` and `citationsContent` (`content.py:80-107`).
- `Role = Literal["user", "assistant"]` (`:227`). Tool results ride in `user` messages, as in
  Converse.
- The stream chunk vocabulary is ConverseStream's: `messageStart`, `contentBlockStart`,
  `contentBlockDelta`, `contentBlockStop`, `messageStop`, `metadata`, plus Strands' `redactContent`
  (`streaming.py:475-491`).
- Every other provider translates from this shape. The canonical form is Bedrock's, not neutral.
  Provider-level loss is covered in [05](05-providers-and-telemetry.md).
- **TS diverges**: class-based blocks with `*Data` interfaces, keys `reasoning` (flat
  `{text?, signature?, redactedContent?}`, `strands-ts/src/types/messages.ts:476-491`) and
  `citations`, an extra `JsonBlock`, and `trackingId`. No shared serialized shape (§5.3).

## 3. What a stream consumer sees

### 3.1 Python: dicts, with invocation state mixed in ✅

`stream_async` calls `event.prepare(invocation_state)`, then hands the **same dict** to
`callback_handler(**d)` and to the iterator (`agent.py:1397-1407`). The docs are right that both
paths see the same events (`streaming/events.mdx:12`).

| Emitted keys | Class (`types/_events.py`) |
|---|---|
| `init_event_loop`, `start`, `start_event_loop` | `:58`, `:77`, `:92` |
| `event` (raw Converse chunk) | `ModelStreamChunkEvent` `:104` |
| `data` / `citation` / `reasoningText` / **`reasoningRedactedContent`** / `reasoning_signature`, each with `delta` | `:154-191` |
| `type:"tool_use_stream"`, `current_tool_use` | `:146` |
| `type:"tool_stream"`, `tool_cancel_event`, `tool_interrupt_event` | `:322`, `:365`, `:388` |
| `message` (assistant, or the tool-result user message) | `:416-446` |
| `structured_output`, `event_loop_throttled_delay`, `force_stop` | `:254`, `:266`, `:449` |
| `result` | `:466` |

Three properties make this a weak contract:

- The classes live in a private module, and consumers receive untyped dicts.
- `ToolResultEvent`, `ModelStopReason` and `EventLoopStopEvent` return `is_callback_event = False`
  (`:216`, `:250`, `:318`). **A Python consumer never sees an individual tool result.** It only sees
  the aggregated tool-result `message`.
- `prepare` **merges the whole `invocation_state` into `init_event_loop` and every delta event**
  (`:73-74`, `:141-143`). That state includes the `Agent` object itself (`agent.py:1740`),
  `request_state`, and trace/span objects. Events are not JSON-serializable as emitted. The docs
  concede the point: "The SDK does not include a built-in serialization filter"
  (`events.mdx:180-190`).

❌ **Refuted.** The Python event reference lists the redacted-reasoning field as
**`redactedContent`** (`site/src/content/docs/user-guide/sdk/streaming/events.mdx:63`). The code
emits:

```python
super().__init__({"reasoningRedactedContent": redacted_content, "delta": delta, "reasoning": True})
```

— `strands-py/src/strands/types/_events.py:183`

A consumer keyed on the documented name silently receives nothing.

### 3.2 TypeScript: typed, hookable, serializable ✅

- Events form an `AgentStreamEvent` union of classes with a `type` discriminator
  (`strands-ts/src/types/agent.ts:623-639`).
- Every stream event is also a hook event.
- `toJSON()` strips runtime references (`events.mdx:218`, 📣).
- `ToolResultEvent` **is** streamed.

> 📌 The two SDKs expose **different information**, not just different syntax. A UI built against TS
> can render per-tool results as they complete. The same UI on Python must diff tool-result
> messages. Compare Codex, where the item lifecycle *is* the contract
> ([thread-turn-item §2](../ai-workflow/wiki/concepts/thread-turn-item.md)).

## 4. Who owns history: the stateless wire, with an optional stateful mode

### 4.1 Default: full client-side replay ✅

Every model call replays the whole of `agent.messages`:

- it is deep-copied (`event_loop.py:584`);
- blank text and invalid tool names are repaired (`streaming.py:48-114`);
- then it is whitelisted:

```python
# Whitelist only role and content before sending to the model provider.
# This ensures metadata (and any future non-model fields) never leak to providers.
messages = [Message(role=msg["role"], content=msg["content"]) for msg in messages]
```

— `streaming.py:553-555`

This is the same stance as Codex's `store: false`
([stateless-conversation-wire](../ai-workflow/wiki/concepts/stateless-conversation-wire.md)). The
difference is that the client-side **conversation manager edits the list between calls**, so "what
the model sees" is whatever the manager left in place (§6).

### 4.2 Stateful mode (design 0004) — shipped, but not as designed

`team/designs/0004-stateful-models.md` (Status: Proposed, 2026-03-26) set out a server-owned
history via `previous_response_id`. The implementation is `OpenAIResponsesModel(stateful=True)`
(`strands-py/src/strands/models/openai_responses.py:215-220`):

- it sets `store: self.stateful` and `previous_response_id = model_state["response_id"]`
  (`:578-583`);
- it captures the id on `response.created` (`:347-352`);
- the Agent snapshots `_model_state` and writes it back only on success (`event_loop.py:594-617`).

| Design 0004 says | Code does | Grade |
|---|---|---|
| Clear `agent.messages` **at the start** of each invocation (`_on_before_invocation`) | Clears on **`AfterInvocationEvent`** (`models/model.py:362-369`; TS `strands-ts/src/plugins/model-plugin.ts:25-31`) | ❌ |
| User `conversation_id` → response-id map (`{"default": …, "billing": …}`) | A single `response_id` key. `conversation_id` has 0 hits in `strands-py/src` | ❌ / 📐 |
| Custom conversation manager → **warning**, not exception | `raise ValueError(...)` (`agent.py:372-376`; TS `agent.ts:544-547`) | ❌ |
| `BedrockModel(api="responses")` subpackage facade | `models/bedrock.py` is still one file with no `api=`. Mantle goes through `_openai_bedrock.py` | 📐 |
| `model_state` persisted in `SessionAgent._internal_state` | Yes (`types/session.py:136-141`, `:168-169`) | ✅ |

> ⚠️ **Unverified, and worth a probe.** Inside one invocation, a stateful tool loop still sends every
> message of the invocation **and** `previous_response_id` (`openai_responses.py:569-583`; TS
> `strands-ts/src/models/openai/responses-adapter.ts:62-80`). No slicing to "since the last response"
> was found. From cycle 2 onward, this would re-send items the server already holds. The only
> integration test is the no-tool case
> (`strands-py/tests_integ/models/test_model_openai.py:305-322`).

> 📌 The wiki's warning applies literally. The moment an adapter stores a response id, it
> "re-creates by hand the hard problem `store: false` handed you for free"
> ([stateless-conversation-wire §4](../ai-workflow/wiki/concepts/stateless-conversation-wire.md)).
> Strands took that on, and the design/code gaps above are where it shows.

## 5. Reasoning retention

### 5.1 Assembly ✅

- Stream deltas accumulate `reasoningText` and `signature` (`streaming.py:251-270`).
- The signature is popped per block ("so it belongs to exactly this block and does not leak into
  the next one", `:357-359`).
- Redacted bytes become a separate `{"reasoningContent": {"redactedContent": …}}` block (`:364`).
- For Gemini, `toolUse` can carry a `reasoningSignature` (`content.py:192`).

### 5.2 Replay is a per-provider accident, not a declared capability ✅

| Provider | Next-call behaviour |
|---|---|
| Bedrock | Replays `text` + `signature` (only if truthy) and `redactedContent` verbatim (`models/bedrock.py:1064-1080`). Strips reasoning for DeepSeek (`:854-896`) |
| Gemini | Round-trips `thought_signature` as base64 (`models/gemini.py:177-183`, `:215-223`) |
| Anthropic (native) | Maps to `{"type": "thinking", "thinking", "signature"}` (`models/anthropic.py:231-236`). **No `redacted_thinking` handling**: `redacted` has 0 hits in the file |
| OpenAI Chat / Responses | **Dropped with a warning**: "reasoningContent is not yet supported in multi-turn conversations with the Responses API" (`openai_responses.py:652-655`; `openai.py:410-419`) |

> ⚠️ On the native Anthropic provider, a reasoning block that holds only `redactedContent` would hit
> `content["reasoningContent"]["reasoningText"]` (`anthropic.py:233`) and raise `KeyError`. This was
> inferred from reading and was not run.

> 📌 Codex requests `reasoning.encrypted_content` unconditionally and treats retained reasoning as
> load-bearing ([retained-reasoning](../ai-workflow/wiki/concepts/retained-reasoning.md)). Strands
> retains it on Bedrock and Gemini, but **discards it on OpenAI's own Responses API**, the one wire
> built to carry it. The only signal is a log warning. The wiki's recommendation
> (`supports_retained_reasoning` as provider data) is exactly what is missing here.

### 5.3 Across the persistence boundary ⚠️

| Field | Python | TS |
|---|---|---|
| Reasoning block | `reasoningContent{reasoningText{text,signature}, redactedContent}` | `reasoning{text, signature, redactedContent}` |
| Tracking id | `tracking_id` | `trackingId` |
| Bytes | `{"__bytes_encoded__": true, "data": b64}` (`types/session.py:27-39`) | base64 in `ReasoningBlock.toJSON` (`messages.ts:541-549`) |

`strands-py/src/strands/types/_snapshot.py:20` says "Persisted scope values match the shared
TypeScript on-disk format". That covers **scope names only**. A Python snapshot that contains
reasoning or bytes is not expected to load losslessly in TS. This was inferred from the types and
not run.

## 6. Context management: what shipped vs what is designed

### 6.1 Conversation managers ✅

- **Base class** (`agent/conversation_manager/conversation_manager.py:31`): `apply_management` after
  each pass, `reduce_context` on overflow, and opt-in **proactive compression** at a
  `BeforeModelCallEvent` threshold (default 0.7), best-effort with errors swallowed (`:65-145`).
- **Sliding window** (`window_size=40`, `should_truncate_results=True`, `per_turn=False`) is the
  default when no `context_manager` is given (`_context_manager/context_manager.py:178-181`; TS
  `agent.ts:338-339`). This matches `conversation-management.mdx:29,46`.
- **Summarizing**: `summary_ratio` 0.3, clamped to 0.1–0.8; `preserve_recent_messages` 10; respects
  pinned messages (`summarizing_conversation_manager.py:42-79`, `:147-184`).
- **Null**: forced for stateful models (`agent.py:398-399`).
- The overflow recursion (§1.1) terminates only because `reduce_context` **raises** once it cannot
  trim further (`sliding_window_conversation_manager.py:247,262`).

### 6.2 Design status vs code

| Design | Header status | Code |
|---|---|---|
| 0003 context management | roadmap | umbrella; realised through the rows below |
| 0008 proactive compression | **Proposed** | ✅ shipped (`proactive_compression`, `projected_input_tokens`) |
| 0009 context offloader | Accepted | ✅ `vended_plugins/context_offloader/` |
| 0011 context strategy presets | Proposed ("v1 merged") | ✅ four presets; "Treat the preset name as the stable contract, not its expansion" (`_context_manager/presets.py:3-6`) |
| 0015 ContextManager class | **Proposed** | Partial; see below |
| 0014 unified storage | **Proposed** | ✅ shipped, but as `write/read/delete/list/search` (`storage/storage.py:123-177`), not the designed `put/get/delete/list` (`0014-storage.md:193-199`) |
| 0005 state machine (steps + orchestrator) | Proposed | 📐 no Step/Orchestrator. Only its middleware layer exists (`_middleware/stages.py`), and the Python README says it follows the TS spec (`_middleware/README.md:1-8`) |

**0015 ContextManager, shipped ✅:** `Agent(context_manager="auto" | "agentic" | …)`, the
`Offload.*` pipeline with emergency truncation, the L1 stash, a retrieval tool, an overflow retry
capped at 3 (`context_manager.py:227-246`), and an experimental "agentic" mode that hands the model
`summarize_context`, `truncate_context` and `pin_context` tools.

**0015 ContextManager, missing 📐:** the `contextManagement` stream event, `ContextOffloadEvent` /
`ContextInjectEvent`, `Inject`, and `TokenBudget`. A grep returns 0 hits in both SDKs. 0015's own
first problem statement ("compression fires silently … No event, no log, no metric") is therefore
**still true in code**.

> ⚠️ `ContextManager` lives in `_context_manager`, a private module path, yet it is reachable from
> the public `Agent` constructor. Overflow handling also runs through two independent mechanisms:
> the Agent-level recursion for ConversationManager, and the `AfterModelCallEvent.retry` loop for
> ContextManager.

## 7. Session persistence ✅

| | Repository managers (`FileSessionManager`, `S3SessionManager`) | `SnapshotSessionManager` (recommended) |
|---|---|---|
| Unit | one JSON file per message, integer `message_id` | one versioned blob, `schema_version "1.0"` |
| Layout | `session_<id>/agents/agent_<id>/messages/message_<n>.json` (`file_session_manager.py:30-43`) | `<session>/scopes/agent/<id>/snapshots/snapshot_latest.json` + `immutable_history/snapshot_<uuid7>.json` (`snapshot_session_manager.py:89-157`) |
| Default location | `~/.strands/sessions/`, mode 0700, symlinks refused (`:60-72`, `:119-145`) | `LocalFileStorage("./.strands/")`, **cwd-relative** (`:381`; `storage/local_file_storage.py:58`) |
| Persisted | `state`, `conversation_manager_state`, `_internal_state{interrupt_state, model_state}` | preset `session` = `messages, state, conversation_manager_state, interrupt_state, model_state`; **not** `system_prompt` (`types/_snapshot.py:9-37`) |

TS has only the snapshot model (`strands-ts/src/session/session-manager.ts`). On restore, both SDKs
discard messages for a stateful model (`snapshot_session_manager.py:520-535`;
`session-manager.ts:295-298`).

## 8. Python vs TypeScript: one contract by convention only

- Design 0018 ("Shared Agent and Model Types", Proposed, #3764) is **not** a cross-language schema.
  It covers `Agent`/`BidiAgent` and `Model`/`BidiModel` typing inside Python.
- No shared JSON Schema or codegen artifact exists in the monorepo. Parity is maintained through
  behavioural READMEs and paired `<Syntax py= ts=>` docs.
- Contrast Codex, whose protocol types are generated schemas
  ([docs/02](../docs/02-app-server-protocol.md)).

| Aspect | Python | TS |
|---|---|---|
| Loop | recursive async generators | iterative `while (true)` |
| `StopReason` | 12, snake_case, closed | 15, camelCase, open |
| Message model | TypedDict, Converse keys | classes, renamed keys |
| Stream | untyped dicts, no tool-result event | typed classes, `toJSON`, tool results streamed |
| Middleware | private `_middleware` | exported (`strands-ts/src/index.ts:361`) |
| Sessions | repository **and** snapshot | snapshot only |

They agree on `limits`, stateful clear-after-invocation, conversation-manager rejection, the
`auto`/`agentic` presets and the 40-message window default.

## 9. What this means if you are building a harness

- [ ] Put a **default** bound on the loop, not an opt-in one. Strands ships unbounded and relies on
      users passing `limits`.
- [ ] Name your units exactly. "Turn" meaning one model cycle (Strands, Codex protocol_v1) versus
      one user request (Codex App Server) is a real integration trap.
- [ ] Give streamed content an item lifecycle with ids (`started → delta → completed`). Raw deltas
      plus a final message force consumers to reconstruct structure.
- [ ] Keep stream events serializable and free of runtime objects. Merging `invocation_state` into
      events leaks the agent object to every callback.
- [ ] Stream tool results as first-class events in every SDK, or document the gap.
- [ ] Model reasoning retention as **declared provider capability data**, and fail loudly, not with
      a log warning, when a provider drops it.
- [ ] If you add a stateful wire mode, define exactly which messages are sent alongside the server
      handle **within** a multi-call invocation, and test it with tools in the loop.
- [ ] Make context compression observable: emit an event when history is rewritten.
- [ ] If two SDKs share on-disk formats, generate the types from one schema. Comments claiming a
      "shared format" do not keep them aligned.

## 10. Open questions

| Item | Status |
|---|---|
| Stateful Responses + multi-cycle tool loop: duplicated input, or an API error? | ⚠️ needs a live or mock probe |
| Depth at which Python's nested async-generator recursion degrades or hits the recursion limit | ⚠️ not measured |
| Native `AnthropicModel` with `redacted_thinking`: dropped at stream time, `KeyError` on replay? | ⚠️ inferred |
| Loading a Python-written snapshot into TS `SessionManager`, and the reverse | ⚠️ inferred from types |
| TS details beyond the spot-checked lines (event union, `modelState` write-back) | ⚠️ taken from a delegated read |
