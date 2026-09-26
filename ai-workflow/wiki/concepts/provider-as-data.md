---
type: concept
status: active
last_ingested_from: docs/15-model-providers.md + browser-agents/11-dia-and-neon.md + browser-agents/09-aside-browser-internals.md + strands/05-providers-and-telemetry.md
related_pages: [concepts/wire-protocol-boundary, concepts/retained-reasoning, concepts/capability-distribution, concepts/control-plane-execution-plane]
created: 2026-09-22
updated: 2026-09-26
---

# Provider as Data — model providers as data, not code branches

- Purpose: how `ModelProviderInfo` expresses a provider as data, and which parts of that design a custom harness should copy outright.
- Scope: why the built-in list is short, the full field set, command-backed auth, the config deny-list, in-flight threads
- Primary source: `codex-rs/model-provider-info/src/lib.rs` (710 lines, read directly)
- Updated: 2026-09-26 (Codex drift re-check against `e72da2b538`)

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | Built-in providers | five (`openai`, `amazon-bedrock`, `amazon-bedrock-runtime`, `ollama`, `lmstudio`) |
| 2 | Why so few | **deliberate** — a declaration not to adjudicate which third parties get bundled |
| 3 | Extension point | `model_providers` in `config.toml` |
| 4 | The real constraint | the wire protocol, not the vendor ([[concepts/wire-protocol-boundary]]) |
| 5 | Most reusable idea | **command-backed token minting** |
| 6 | Security boundary to copy | a **deny-list** on provider, auth and telemetry keys in project-local config |

## §2 The short built-in list is a design choice  {#s2-builtin-short}

```rust
// We do not want to be in the business of adjucating which third-party
// providers are bundled with Codex CLI, so we only include the OpenAI and
// open source ("oss") providers by default. Users are encouraged to add to
// `model_providers` in config.toml to add their own providers.
```

**Multi-provider is a first-class design point.** The constraint is the wire protocol, not the vendor.

## §3 The full shape of `ModelProviderInfo`  {#s3-shape}

| Field | Purpose |
|---|---|
| `name` | display name. **Also the main lever that selects the non-OpenAI path** ([[concepts/stateless-conversation-wire]] §5) |
| `model_catalog_url` | *(added 2026-09, #46561)* a remote model catalog — which also decides each model's request shape |
| `gateway_oauth` | *(added 2026-09, #46482)* gateway OAuth sign-in, surfaced as `account/gatewayOAuth/*` |
| `include_internal_metadata` | *(added 2026-09, #48344, runtime-only)* set only by the built-in `openai` provider |
| `base_url` | base URL for the provider's OpenAI-compatible API |
| `env_key` / `env_key_instructions` | the environment variable holding the key, and help text for it |
| `experimental_bearer_token` | a literal `Authorization: Bearer` value. **Discouraged** versus `env_key`, but needed programmatically |
| `auth` | **command-backed** bearer token (§4) |
| `aws` | AWS SigV4 configuration |
| `wire_api` | Responses (the only value) |
| `query_params` / `http_headers` | query parameters appended to the base URL; literal extra headers |
| `env_http_headers` | header name → **environment variable**. Omitted when unset or empty |
| `request_max_retries` / `stream_max_retries` / `stream_idle_timeout_ms` / `websocket_connect_timeout_ms` | retry and timeout knobs |
| `requires_openai_auth` | whether to show the login screen and store credentials in `auth.json` |
| `supports_websockets` / `supports_standalone_web_search` | **capability flags** |

> **Separate capability from identity.** `supports_websockets` and
> `supports_standalone_web_search` are **per-provider facts the UI must read**, not assume.
> [[concepts/retained-reasoning]] §5 argues for adding `supports_retained_reasoning` alongside them.

## §4 Command-backed auth — the most reusable idea  {#s4-command-auth}

For providers whose tokens are minted by an external tool (cloud CLIs, internal brokers).

| Key | Purpose |
|---|---|
| `model_providers.<id>.auth.command` | executable to run |
| `...auth.args` | arguments |
| `...auth.cwd` | working directory |
| `...auth.timeout_ms` | per-invocation timeout |
| `...auth.refresh_interval_ms` | how often to re-mint |

> This is **the most reusable idea in the whole provider design** for a custom harness — it turns
> "support provider X's bespoke auth" into "shell out to something that prints a token."

### §4.1 AWS's mutual exclusion  {#s4-1-aws}

`aws.region` · `aws.profile` · `aws.credential_export`.
**`credential_export` and `profile` cannot both be set.** When `credential_export` is configured,
Bedrock setup and login return an error **without changing configuration or saved credentials.**

## §5 The security boundary to copy — a config deny-list  {#s5-deny-list}

Project-scoped `.codex/config.toml` **cannot** override machine-local provider, auth, notification,
profile or telemetry keys. Codex ignores these when they appear in a project-local file:

```
openai_base_url   chatgpt_base_url   apps_mcp_product_sku
model_provider    model_providers    notify
profile           profiles           experimental_realtime_ws_base_url   otel
```

> A cloned repository must never be able to redirect your agent's model traffic or exfiltrate
> telemetry. **Any custom harness that reads per-project config needs the same deny-list.**

## §6 Policy changes and in-flight threads  {#s6-in-flight}

> Existing threads retain their provider configuration. When managed `model_provider` /
> `model_providers` requirements no longer match, or cannot be loaded, **input-family RPCs are
> rejected** — turn start/steer, review, compaction, manual queue start, active goal updates.
> **Interrupt, realtime stop and goal pause/clear remain available.** User and project configuration
> changes alone do not invalidate existing threads.

> A pattern worth copying: an enterprise policy change **must not silently move a running
> conversation onto a different model.** Fail the *input* path while leaving *control* paths open.

Realtime connections use separate routing configuration and are exempt from this check.

## §5.5 Observation — two cases pointing opposite ways  {#s5-5-two-directions}

`ModelProviderInfo` only says "a provider is data." Browser-type agents diverge on **who chooses it.**

| Product | Chooser | Implementation |
|---|---|---|
| **Aside** | **the user** | 16+ provider ids. **Reuses an existing subscription over OAuth** (ChatGPT, Claude, Copilot) plus BYO API keys |
| **Opera Neon** | **the product** | "Opera's AI engine, **model-agnostic**" **routes** each task to a model. The user chooses only in Chat |
| Dia | the product | fixed: GPT (OpenAI Azure) · Claude (Anthropic, Vertex, AWS) · Gemini (Vertex) |

> 📌 **"Model-agnostic" names two opposite product designs.** Aside gives the user sovereignty; Neon
> chooses on their behalf. When designing a custom harness these are **different products** — the
> first removes model cost from the adoption barrier, the second makes the product answerable for
> quality.
>
> The choice is bound to the planning location in [[concepts/control-plane-execution-plane]].
> Planning has to be local for a user's own subscription to be usable.

## §7 Checklist for a multi-provider harness  {#s7-checklist}

- [ ] **Settle the wire protocol boundary first** — it decides whether Codex core is reusable at all
- [ ] If Chat Completions is required, design the adapter as **a provider-shaped proxy, not a fork**
- [ ] Model providers **as data** (`ModelProviderInfo`-shaped), not as code branches
- [ ] Support **command-backed token minting from day one**
- [ ] Separate capability from identity
- [ ] Give each provider its own retry and timeout knobs (a local Ollama and a hosted API differ)
- [ ] Deny project-local config the ability to set provider, auth or telemetry keys
- [ ] Decide what happens to **in-flight threads** when provider policy changes — reject input, keep control
- [ ] Decide **who chooses the model**, and know which product that makes you

## §6.5 Observation — the opposite design, and where each holds  {#s6-5-strands}

**Strands** ([`strands/05`](../../../strands/05-providers-and-telemetry.md)) makes providers **code**: 12 Python
classes and 5 TS, each converting to an internal wire that is literally Bedrock ConverseStream
(`types/streaming.py:1-5`, "modeled after the Bedrock API"). There is no base-URL + wire + auth
record; the harness's `"provider/model"` strings go through a closed table of builder functions, and
a bare string in the core `Agent` is always a Bedrock model id.

| | Codex | Strands |
|---|---|---|
| Fixed | the **external** wire (Responses) | an **internal** wire (Converse) |
| Varies | provider rows (data) | converter classes (code) |
| Adding a provider | a config entry | a class |
| Vendor-native features | only what the wire carries | per converter |
| Retained reasoning | kept ([[concepts/retained-reasoning]]) | **dropped on every OpenAI path** |

> 📌 **Provider-as-data holds where the wire is shared.** Where it is not, the unit of variation is the
> converter, and a converter is code. Choose which wire you fix before choosing how providers are
> expressed — the second decision follows from the first.

## §8 Read next  {#s8-next}

- [[concepts/wire-protocol-boundary]] — the constraint this data model sits under
- [[concepts/retained-reasoning]] — a capability that should be a flag
- [[concepts/control-plane-execution-plane]] — where planning runs, which this follows
- Original: [`docs/15-model-providers.md`](../../../docs/15-model-providers.md)
- Strands case: [`strands/05-providers-and-telemetry.md`](../../../strands/05-providers-and-telemetry.md)
