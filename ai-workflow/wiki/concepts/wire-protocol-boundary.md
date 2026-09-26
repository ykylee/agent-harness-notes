---
type: concept
status: active
last_ingested_from: docs/15-model-providers.md + docs/16-responses-chat-adapter.md + browser-agents/09-aside-browser-internals.md
related_pages: [concepts/provider-as-data, concepts/stateless-conversation-wire, concepts/retained-reasoning, concepts/harness]
created: 2026-09-22
updated: 2026-09-26
---

# Wire Protocol Boundary — what decides whether the core is reusable

- Purpose: which wire protocol Codex core presumes, and what that presumption forces on a custom harness.
- Scope: the current state of `WireApi`, three ways out, the in-repo proxy precedent, and the two request shapes
- Primary sources: `codex-rs/model-provider-info/src/lib.rs` (710 lines, read directly), `codex-rs/core/src/client.rs`
- Updated: 2026-09-26 (Codex drift re-check against `e72da2b538`)

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | Variants of `WireApi` | **exactly one — `Responses`** |
| 2 | Chat Completions | **removed.** Configuring it produces an explicit error |
| 3 | Consequence | you **cannot** get a Chat Completions harness by wrapping `codex app-server` as is |
| 4 | Recommended way out | **a provider-shaped proxy**, not a fork |
| 5 | Request shapes | **there are two** — classic and `responses_lite` |
| 6 | First decision | settle this boundary **first.** Everything else is downstream |

## §2 Chat Completions is gone  {#s2-chat-removed}

```rust
pub enum WireApi {
    /// The Responses API exposed by OpenAI at `/v1/responses`.
    #[default]
    Responses,
}
```

Configuring the old value produces a deliberately designed error:

```
`wire_api = "chat"` is no longer supported.
How to fix: set `wire_api = "responses"` in your provider config.
More info: https://github.com/openai/codex/discussions/7782
```

The removal went past the enum — the `ollama-chat` provider id was retired too, and `ollama` now runs
as `WireApi::Responses`.

## §3 Three ways out  {#s3-escape-routes}

| Approach | How | Cost |
|---|---|---|
| **An adapter in front** | run a local proxy that accepts `/v1/responses` and translates to `/v1/chat/completions` upstream; point a `model_providers` entry at it | low to medium. Translation fidelity is yours |
| **Re-add the wire API** | fork and restore a `Chat` variant plus its request/response mapping | medium to high. Permanent divergence from upstream |
| **Own the model layer** | take the protocol design and write your own core | high, but no wire-protocol constraint at all |

## §4 The proxy precedent — evidence the shape works  {#s4-proxy-precedent}

The repository itself ships `codex-responses-api-proxy`.

```toml
[model_providers.codex-responses-api-proxy]
name = 'codex-responses-api-proxy'
base_url = 'http://127.0.0.1:60001/v1'
wire_api = 'responses'
```

Its purpose is request/response dumping rather than protocol translation, but it proves the shape —
**anything that speaks Responses at a `base_url` is a valid provider.** A Responses→Chat adapter
slots into exactly that position.

## §5 There is more than one request shape — `responses_lite`  {#s5-responses-lite}

When `model_info.use_responses_lite` is set, the request is assembled differently.

| Item | classic | lite |
|---|---|---|
| top-level `instructions` | the base-instructions string | **empty** |
| top-level `tools` | tool JSON | **`None`** |
| where tools and instructions actually go | top-level fields | the input array is prefixed with `ResponseItem::AdditionalTools { role: "developer", tools }` and a base-instructions message |
| item ids | — | `Uuid::v5` over the thread id and serialised payload (stable across retries and resumed sessions) |

> ⚠️ **An adapter must handle both shapes**, or it will see a request with no tools and no
> instructions and silently drop both. `AdditionalTools` is **not droppable in lite mode — it *is*
> the tool list.**

### §5.1 Which models are lite  {#s5-1-which-models}

From `codex-rs/models-manager/models.json` (nine entries at the snapshot; ten at 2026-09-26):

| `use_responses_lite` | Models |
|---|---|
| **true** | `gpt-6-astra`, `gpt-6-sol`, `gpt-6-luna` (both added 2026-09, #47332), `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-daybreak-blue-latest`, `gpt-daybreak-red-latest`, `codex-auto-review` |
| false | `gpt-5.5` (`gpt-5.4` removed 2026-09, #47932) |

**Every current-generation model is lite.** An adapter that handles only the classic shape is writing
against the legacy path.

### §5.2 How a slug resolves to that flag  {#s5-2-slug-matching}

`construct_model_info_from_candidates` tries three things in order:

| Order | Method |
|---|---|
| 1 | **longest-prefix match** — among candidates where `model.starts_with(&candidate.slug)`, the longest slug wins |
| 2 | **one-level namespace strip** — split a `namespace/model` slug and retry the prefix match |
| 3 | **fallback** — warn, set `used_fallback_model_metadata: true`, `use_responses_lite: false`, generic `context_window` of 272,000 |

```
"gpt-6-astra-turbo"        → prefix-matches "gpt-6-astra"  → use_responses_lite = true
"myprovider/gpt-6-astra"   → namespace strip, same match   → use_responses_lite = true
"llama-3.3-70b"            → no match → fallback           → use_responses_lite = false
```

> **The trap**: naming a third-party model with an OpenAI-shaped prefix **silently changes the
> request shape.** `config.toml` has no key to override it — the control points are a catalog:
> **`model_catalog_json`**, or since 2026-09 a per-provider **`model_catalog_url`** serving a remote
> catalog (#46561). Lite mode also forces `parallel_tool_calls` off. Ship a catalog with an explicit entry for every model you support. Do not
> rely on prefix-match luck, and do not rely on the fallback.

## §5.5 Observation — Aside implements this branching  {#s5-5-aside}

Evidence that `responses_lite` is not a theoretical trap. In Aside's browser daemon binary:

```js
CODEX_TOOL_CALL_PROVIDERS = new Set([`openai`, `openai-codex`, `opencode`])
AZURE_TOOL_CALL_PROVIDERS  = new Set([`openai`, `openai-codex`, `opencode`, `azure-openai-responses`])
// nearby: supportsAdditionalTools, supportsToolSearch, supportsMidConvoSystemMessages
```

> 📌 **`openai-codex` is registered as a model provider id**, with a `supportsAdditionalTools` flag
> beside it. `AdditionalTools` is the item that carries the tool list in lite mode (§5). In other
> words **a third-party harness absorbed Codex's two request shapes as a per-provider capability
> flag.**
>
> This is where this repository's two studies meet at the level of source, and it shows the
> recommendation in §5 — that an adapter must handle both shapes — being demanded in practice.

## §6 Read next  {#s6-next}

- [[concepts/stateless-conversation-wire]] — what makes an adapter easy
- [[concepts/retained-reasoning]] — what an adapter loses
- [[concepts/provider-as-data]] — modelling providers as data rather than code branches
- Originals: [`docs/15-model-providers.md`](../../../docs/15-model-providers.md), [`docs/16-responses-chat-adapter.md`](../../../docs/16-responses-chat-adapter.md)
