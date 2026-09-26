---
type: concept
status: active
last_ingested_from: docs/16-responses-chat-adapter.md + docs/07-harness-engineering.md + docs/99-sources.md
related_pages: [concepts/stateless-conversation-wire, concepts/wire-protocol-boundary, concepts/harness-engineering, concepts/primary-source-verification]
created: 2026-09-22
updated: 2026-09-27
---

# Retained Reasoning — why the harness is a performance variable

- Purpose: why retained reasoning is load-bearing design rather than an optimisation, and why it structurally disappears when crossing to Chat Completions.
- Scope: the mechanism, what Chat Completions lacks, what is actually lost, design consequences
- Primary sources: `codex-rs/protocol/src/models.rs`, `codex-rs/core/src/client.rs`, the "Codex as a platform" post
- Updated: 2026-09-27 (re-checked against `docs/99` §E.3 update; no change to this concept)

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | What it is | **sending the model's prior reasoning back** on the next turn to keep the chain |
| 2 | Vehicle | `Reasoning.encrypted_content` — **a first-class input item** |
| 3 | How it is requested | `include: ["reasoning.encrypted_content"]` — **unconditionally, always** |
| 4 | Chat Completions | **no counterpart.** Structurally impossible |
| 5 | Size of the loss | **proportional to how much the target model reasons.** Zero for a non-reasoning model |
| 6 | Character | a **capability regression**, not a performance optimisation |

## §2 The mechanism  {#s2-mechanism}

```rust
Reasoning {
    id: Option<ResponseItemId>,
    summary: Vec<ReasoningItemReasoningSummary>,
    content: Option<Vec<ReasoningItemContent>>,
    encrypted_content: Option<String>,
    internal_chat_message_metadata_passthrough: Option<...>,
}
```

Because `store: false` ([[concepts/stateless-conversation-wire]]), Codex resends the whole
conversation every turn. **That includes the model's own prior reasoning**, carried in
`encrypted_content`. This is how a stateless client keeps a reasoning model's chain across a
multi-step task.

And Codex requests it unconditionally:

```rust
let include = vec!["reasoning.encrypted_content".to_string()];
```

No feature gate. No per-model condition. **Always.**

## §3 Chat Completions has no slot for it  {#s3-no-slot}

| Axis | Responses | Chat Completions |
|---|---|---|
| Request-side effort | `reasoning.effort` | `reasoning_effort` ✅ |
| **Output-side representation** | a `Reasoning` item | **none** ❌ |
| A slot to send it back next request | the `Reasoning` variant in `input[]` | **none** ❌ |
| Summary channel | `reasoning.summary` | none ❌ |

`ChatCompletionStreamResponseDelta` has no reasoning field, and there is no assistant-message slot to
put an opaque reasoning blob into for the next request.

Some third-party servers emit a non-standard `reasoning_content` field (a vLLM/DeepSeek-ecosystem
convention). That is not in the OpenAI spec, is not encrypted and is **not round-trippable as an
opaque token.** An adapter can surface it as a reasoning *summary* for display, but it cannot restore
continuity.

## §4 What is actually lost  {#s4-what-is-lost}

Reasoning is **dropped at the turn boundary.** Each turn starts the model's reasoning fresh.

And that is precisely the capability the harness-engineering material credits for large gains:

> "Harness design can materially change results: on ARC-AGI-3, retained reasoning and context
> compaction raised GPT-5.6 Sol's score from **13.3% to 38.3%** while reducing output tokens
> **sixfold**."

Two **harness-level settings** — retained reasoning and context compaction — not a model change.

> 📌 **Source grade**: this figure first appeared in a secondary source, but it is stated verbatim in
> the "Codex as a platform" post itself, which links a dedicated write-up
> (`openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/`), so it was **promoted to
> primary.** The grading history is in [[concepts/primary-source-verification]].

Whatever the exact figures, the conclusion holds — **retained reasoning is load-bearing design, not
an optimisation.**

## §5 Design consequences  {#s5-consequences}

| # | Consequence |
|---|---|
| 1 | Treat reasoning retention as **a per-provider capability, not a global assumption.** `ModelProviderInfo` already has the shape (`supports_websockets`, `supports_standalone_web_search`) — add `supports_retained_reasoning` and let the harness adapt |
| 2 | For Chat-backed providers, disable the five Responses-native tool item types and **make that visible in the UI** rather than a silent absence |
| 3 | Make `include` conditional. Codex hard-codes `reasoning.encrypted_content`; a multi-provider harness cannot |
| 4 | **Whether to build the adapter at all**: build it if the requirement is "support third-party models that only speak Chat Completions." Do not, if it is "run OpenAI reasoning models over Chat Completions" — you would be paying adapter complexity for a strictly worse version of a path that already works |

## §6 Read next  {#s6-next}

- [[concepts/stateless-conversation-wire]] — the other side, the one that makes adapters easy
- [[concepts/harness-engineering]] — treating the harness as a performance variable
- [[concepts/provider-as-data]] — expressing capability as data
- Original: [`docs/16-responses-chat-adapter.md`](../../../docs/16-responses-chat-adapter.md) §5
