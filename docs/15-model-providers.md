# 15. Model Providers — and the Chat Completions Problem

> Sources: `codex-rs/model-provider-info/src/lib.rs` (710 lines, read directly),
> `learn.chatgpt.com/docs/config-file/config-reference.md`, `learn.chatgpt.com/docs/amazon-bedrock.md`,
> `codex-rs/responses-api-proxy/README.md`. Extracted 2026-09-15.

## 1. The headline: Chat Completions is gone

`WireApi` in the current tree has **exactly one variant**:

```rust
/// Wire protocol that the provider speaks.
pub enum WireApi {
    /// The Responses API exposed by OpenAI at `/v1/responses`.
    #[default]
    Responses,
}
```

Configuring the old value produces an explicit, deliberate error:

```rust
const CHAT_WIRE_API_REMOVED_ERROR: &str =
  "`wire_api = \"chat\"` is no longer supported.\n\
   How to fix: set `wire_api = \"responses\"` in your provider config.\n\
   More info: https://github.com/openai/codex/discussions/7782";
```

```rust
"chat" => Err(serde::de::Error::custom(CHAT_WIRE_API_REMOVED_ERROR)),
```

The removal went further than the enum — the `ollama-chat` provider id was retired too:

```rust
pub const OLLAMA_CHAT_PROVIDER_REMOVED_ERROR: &str =
  "`ollama-chat` is no longer supported.\n\
   How to fix: replace `ollama-chat` with `ollama` in `model_provider`, `oss_provider`, \
   or `--local-provider`.";
```

`ollama` now runs as `WireApi::Responses`.

### What this means for a custom harness

**Codex core assumes the Responses wire protocol everywhere.** A harness that must speak Chat
Completions cannot be obtained by wrapping `codex app-server` as-is. Three ways out:

| Option | How | Cost |
|---|---|---|
| **Adapter in front** | Run a local proxy that accepts `/v1/responses` and translates to `/v1/chat/completions` upstream. Point a `model_providers` entry at it | Low–medium. You own the translation fidelity |
| **Re-add the wire API** | Fork and restore a `Chat` variant plus its request/response mapping | Medium–high. Permanent divergence from upstream |
| **Own the model layer** | Take the protocol design (docs [02](02-app-server-protocol.md)) but write your own core | High, but no wire-protocol constraint at all |

The adapter route has a precedent inside the repo itself.

### Precedent: `codex-responses-api-proxy`

The repo ships a proxy that sits between Codex and a provider:

```bash
echo $OPENAI_API_KEY | ./target/debug/codex-responses-api-proxy \
    --port 60001 \
    --dump-dir /tmp/proxy
```

```toml
[model_providers.codex-responses-api-proxy]
name = 'codex-responses-api-proxy'
base_url = 'http://127.0.0.1:60001/v1'
wire_api = 'responses'

[profiles.proxy]
model_provider = "codex-responses-api-proxy"
```

It exists for request/response dumping, not protocol translation — but it proves the shape works:
**anything that speaks Responses at a `base_url` is a valid provider.** A Responses→Chat adapter
would slot into exactly this position.

> Translation is not free. Responses carries reasoning items, encrypted content, and item-level
> semantics that Chat Completions has no place for.
>
> **[16-responses-chat-adapter.md](16-responses-chat-adapter.md) works this out against the real
> payload**: the adapter is stateless and 13 of 17 request fields map, but retained reasoning cannot
> survive the crossing.

## 2. Third-party providers *are* supported — within that constraint

The built-in list is deliberately short:

```rust
// We do not want to be in the business of adjucating which third-party
// providers are bundled with Codex CLI, so we only include the OpenAI and
// open source ("oss") providers by default. Users are encouraged to add to
// `model_providers` in config.toml to add their own providers.
```

| Built-in id | Notes |
|---|---|
| `openai` | Default |
| `amazon-bedrock` | AWS SigV4 auth |
| `amazon-bedrock-runtime` | |
| `ollama` | OSS provider, `WireApi::Responses` |
| `lmstudio` | OSS provider |

Everything else goes in `model_providers` in `config.toml`. So **multi-provider is a first-class
design point** — the constraint is the wire protocol, not the vendor.

## 3. `ModelProviderInfo` — the full provider shape

From `model-provider-info/src/lib.rs`:

| Field | Purpose |
|---|---|
| `name` | Friendly display name |
| `base_url` | Base URL for the provider's OpenAI-compatible API |
| `env_key` | Environment variable holding the API key |
| `env_key_instructions` | Help text for obtaining/setting that variable |
| `experimental_bearer_token` | Literal `Authorization: Bearer` value. **Discouraged** vs `env_key`, but needed programmatically |
| `auth` | **Command-backed** bearer token (see below) |
| `aws` | AWS SigV4 configuration |
| `wire_api` | Responses (the only value) |
| `query_params` | Query parameters appended to the base URL |
| `http_headers` | Literal extra headers |
| `env_http_headers` | Header name → **environment variable** whose value is used. Omitted when unset or empty |
| `request_max_retries` | Max HTTP retries |
| `stream_max_retries` | Retries for reconnecting a dropped stream |
| `stream_idle_timeout_ms` | Idle timeout before treating a stream as lost |
| `websocket_connect_timeout_ms` | WebSocket connect timeout |
| `requires_openai_auth` | Whether to show the login screen and store credentials in `auth.json` |
| `supports_websockets` | Responses API WebSocket transport support |
| `supports_standalone_web_search` | Standalone web-search endpoint support |

### Command-backed auth

For providers whose tokens are minted by an external tool (cloud CLIs, internal brokers):

| Key | Purpose |
|---|---|
| `model_providers.<id>.auth.command` | Executable to run |
| `model_providers.<id>.auth.args` | Arguments |
| `model_providers.<id>.auth.cwd` | Working directory |
| `model_providers.<id>.auth.timeout_ms` | Per-invocation timeout |
| `model_providers.<id>.auth.refresh_interval_ms` | How often to re-mint |

**This is the most reusable idea in the whole provider design** for a custom harness — it turns
"support provider X's bespoke auth" into "shell out to something that prints a token."

### AWS

| Key | Purpose |
|---|---|
| `model_providers.amazon-bedrock.aws.region` | Region |
| `model_providers.amazon-bedrock.aws.profile` | Named AWS profile |
| `...aws.credential_export` | An exporter command. **Mutually exclusive with `aws.profile`** |

Per `app-server/README.md`: when `credential_export` is configured, Bedrock setup and Bedrock login
return an error **without changing configuration or saved credentials**.

## 4. Related config keys

| Key | Meaning |
|---|---|
| `model` | e.g. `gpt-5.5` |
| `model_provider` | Provider id from `model_providers` (default `openai`) |
| `openai_base_url` | Base URL override for the built-in `openai` provider |
| `oss_provider` | `lmstudio` \| `ollama` — default for `--oss` |
| `model_context_window` | Context tokens for the active model |
| `model_auto_compact_token_limit` | Threshold triggering automatic compaction |
| `model_auto_compact_token_limit_scope` | `total` (default) \| `body_after_prefix` |
| `model_catalog_json` | Path to a JSON model catalog loaded at startup; a selected profile file can override it per profile |
| `review_model` | Optional model override used by `/review` |

The repo also ships `codex-rs/models-manager/models.json` — a bundled catalog, which is what
`model_catalog_json` replaces.

### A security boundary worth copying

Project-scoped `.codex/config.toml` **cannot** override machine-local provider, auth, notification,
profile, or telemetry keys. Codex ignores these when they appear in a project-local file:

```
openai_base_url   chatgpt_base_url   apps_mcp_product_sku
model_provider    model_providers    notify
profile           profiles           experimental_realtime_ws_base_url   otel
```

> A cloned repository must never be able to redirect your agent's model traffic or exfiltrate
> telemetry. Any custom harness that reads per-project config needs this same deny-list.

## 5. The provider surface in the App Server protocol

| Method / notification | Role |
|---|---|
| `model/list` | Model discovery |
| `modelProvider/capabilities/read` | Per-provider capability probe |
| `model/rerouted` | The request was routed to a different model |
| `model/verification` | Model verification state |
| `model/safetyBuffering/updated` | Safety buffering state |
| `modelProvider/authRecoveryStarted` / `...Completed` | Provider auth recovery lifecycle |

### Managed provider requirements

> Existing threads retain their provider configuration. Input RPCs are **rejected** when managed
> `model_provider` / `model_providers` requirements no longer match that configuration, or cannot be
> loaded. This covers turn start/steer, review, compaction, manual queue start, and active goal
> updates. Interrupt, realtime stop, and goal pause/clear remain available.
> **User and project configuration changes alone do not invalidate existing threads.**

This is a good pattern to copy: an enterprise policy change must not silently move a running
conversation onto a different model — it fails the *input* path while leaving *control* paths open.

Realtime connections use separate routing configuration and are not checked here.

## 6. Checklist for a multi-provider harness

- [ ] Decide the wire protocol boundary **first** — it determines whether you can reuse Codex core
- [ ] If Chat Completions is required, design the adapter as a provider-shaped proxy, not a fork
- [ ] Model the provider as data (`ModelProviderInfo`-shaped), not as code branches
- [ ] Support command-backed token minting from day one — it absorbs most bespoke auth schemes
- [ ] Separate "capabilities" from "identity": `supports_websockets`, `supports_standalone_web_search`
      are per-provider facts the UI must read, not assume
- [ ] Give providers their own retry/timeout knobs; a local Ollama and a hosted API need different ones
- [ ] Deny project-local config the ability to set provider, auth, or telemetry keys
- [ ] Decide what happens to **in-flight threads** when provider policy changes — reject input, keep control
