# 99. Sources and Verification Status

Research date: 2026-09-14 (Agents API reference extracted 2026-09-15)

## A. Primary sources — verified directly ✅

### Repository (highest confidence; the generated schemas are authoritative)

| Path | Contents |
|---|---|
| [`openai/codex` README](https://github.com/openai/codex/blob/main/README.md) | Installation, authentication, doc links |
| [`codex-rs/app-server/README.md`](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md) | Recent protocol changes, user verification, attachments, plugin settings |
| [`codex-rs/docs/protocol_v1.md`](https://github.com/openai/codex/blob/main/codex-rs/docs/protocol_v1.md) | The legacy SQ/EQ core protocol |
| `codex-rs/app-server-protocol/schema/typescript/ClientRequest.ts` | **104 client methods** |
| `codex-rs/app-server-protocol/schema/typescript/ServerRequest.ts` | **10 server requests** |
| `codex-rs/app-server-protocol/schema/typescript/ServerNotification.ts` | **84 server notifications** |
| `.../InitializeParams.ts`, `InitializeResponse.ts`, `InitializeCapabilities.ts`, `ClientNotification.ts` | Handshake |
| `.../v2/ThreadStartParams.ts`, `ThreadStartResponse.ts`, `TurnStartParams.ts`, `TurnStartResponse.ts`, `ThreadItem.ts` | Payloads |
| [`sdk/typescript/README.md`](https://github.com/openai/codex/blob/main/sdk/typescript/README.md) | Full TS SDK docs |
| [`sdk/python/README.md`](https://github.com/openai/codex/blob/main/sdk/python/README.md), `docs/getting-started.md` | Full Python SDK docs |

License: **Apache-2.0**

### OpenAPI spec — authoritative for the Agents API

| Path | Contents |
|---|---|
| [`openai/openai-openapi` → `openapi.yaml`](https://github.com/openai/openai-openapi/blob/master/openapi.yaml) | ~3.5MB. **33 endpoints** and their full schemas under `tags: Agents` |

Extracted directly from it: endpoint paths/methods/operationIds, `CreateAgentSessionParams`,
`SessionAgentConfigParam`, `EnvironmentParam` (3 variants), `AgentToolConfigParam` (5 kinds),
`MultiAgentConfigCurrentParam`, `SessionResource`, `TurnResource`, `TokenUsageResource`,
`SessionEvent` (30 kinds), `SessionInputParam` (3 kinds), `SessionTurnItemResource` (14 kinds),
`SessionTurnErrorCodeResource` (17 codes), `SessionArtifactResource`, and the pagination envelope.

→ [08-agents-api-reference.md](08-agents-api-reference.md)

### Official documentation

**All of these were read as raw Markdown** by appending `.md` to the page URL — the docs state:
*"Markdown versions of documentation pages are available by appending `.md` to the page URL"*
(and `/llms.txt` is the complete index). This returns source text with code samples intact instead
of a rendered page, so these are effectively primary sources rather than summaries.

| URL (append `.md` to fetch source) | Contents |
|---|---|
| `.../guides/agents-api/overview` | Agents API overview |
| `.../guides/agents-api/quickstart` | Quickstart, API key scopes, cleanup |
| `.../guides/agents-api/configuration` | Agent config, saved agents, per-session overrides |
| `.../guides/agents-api/architecture` | The three pieces and three topologies |
| `.../guides/agents-api/sessions` | Running and continuing sessions |
| `.../guides/agents-api/sessions/manage` | Session management |
| `.../guides/agents-api/sessions/events` | Session events |
| `.../guides/agents-api/sessions/webhooks` | The 5 webhook events, handler setup |
| `.../guides/agents-api/multi-agent` | Subagents (examples in 6 languages) |
| `.../guides/agents-api/observability` | Dashboard, pagination, cost model |
| `.../guides/agents-api/tracing` | Span types, trace reading |
| `.../guides/agents-api/environments/openai-hosted` | Hosted sandbox config, network, expiry, pricing |
| `.../guides/agents-api/environments/self-hosted` | Executor connection |
| `.../guides/agents-api/environments/lifecycle` | Start/stop compute, webhook-managed sandboxes |
| `.../guides/agents-api/environments/files` | Files, artifacts, limits |
| `.../guides/agents-api/environments/security` | Key separation, isolation, brokering |
| `.../guides/agents-api/tools/functions` | Function tools, required actions, recovery |
| `.../guides/agents-api/tools/mcp` | Three connection modes, authentication |
| `.../guides/agents-api/tools/vaults` | Vault and credential lifecycle |
| `.../guides/agents-api/tools/plugins` | Plugin packaging and registration |
| `.../guides/tools-skills`, `.../guides/tools-tool-search` | Skills, tool search |
| `.../codex/app-server` (→ learn.chatgpt.com/docs/app-server) | Official App Server guide |
| `.../codex/sdk` (→ learn.chatgpt.com/docs/codex-sdk) | SDK overview |
| `.../codex/noninteractive` (→ learn.chatgpt.com/docs/non-interactive-mode) | `codex exec` |
| `.../blog/codex-as-a-platform` | The "Codex as a platform" blog post |

Base for the guide paths: `https://developers.openai.com/api/docs`.

**Codex product docs** (index: `https://learn.chatgpt.com/llms.txt`, 323 entries) — also read as `.md`:

| URL | Contents |
|---|---|
| `learn.chatgpt.com/docs/agent-approvals-security` | Sandbox/approvals, OS-level sandbox, network isolation (34KB) |
| `learn.chatgpt.com/docs/windows/windows-sandbox` | Native Windows sandbox modes and version matrix |
| `learn.chatgpt.com/docs/config-file/config-reference` | Full `config.toml` + `requirements.toml` reference (112KB) |
| `learn.chatgpt.com/docs/amazon-bedrock` | Bedrock provider configuration |
| `developers.openai.com/plugins/build/plugins` | Plugin packaging, marketplace catalog format (29KB) |
| `developers.openai.com/plugins` | Plugin docs index |

**Repository sources read directly for this pass:**

| Path | Used for |
|---|---|
| `codex-rs/model-provider-info/src/lib.rs` | `WireApi`, `ModelProviderInfo`, built-in provider list |
| `codex-rs/responses-api-proxy/README.md` | Provider-shaped local proxy pattern |
| `codex-rs/windows-sandbox-rs/src/`, `windows-sandbox-service/src/` | Windows sandbox module map (**inference from the source tree, not prose docs**) |
| `openai/openai-openapi` `openapi.yaml` | `/vaults` endpoints; `CreateChatCompletionRequest`, `ChatCompletionStreamResponseDelta`, `ModelResponseProperties` |
| `codex-rs/codex-api/src/common.rs` | `ResponsesApiRequest` — the exact wire payload (17 fields) |
| `codex-rs/core/src/client.rs` | The constant values Codex fills in (`store: false`, `include`, `tool_choice`) |
| `codex-rs/protocol/src/models.rs` | `ResponseItem` — 18 input item variants |
| `codex-rs/codex-api/src/sse/responses.rs` | The 25 SSE event types Codex parses |
| `codex-rs/core/src/client_common.rs` | `Prompt` — the pre-serialization turn payload |

> Note: `developers.openai.com/codex/*` currently 308-redirects to `learn.chatgpt.com/docs/*`.
> `developers.openai.com/api/reference/...` pages returned 404 to plain fetches; the OpenAPI spec
> covers that ground more precisely.

### Official blog posts (openai.com returned 403 here → read via a full-text mirror)

| Post | Author | Date |
|---|---|---|
| [Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/) | Celia Chen | 2026-02-04 |
| [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) | Ryan Lopopolo | 2026-02-11 |

Both were read through full-text mirrors (`raw/openai-com-index-*.md`) in the
[`newton20/harness-engineering-kb`](https://github.com/newton20/harness-engineering-kb) repository.
**The mirror is third-party, so re-verify against the original before relying on a decisive quote.**
That said, the code examples, footnotes, authors, and dates are all internally consistent, so
confidence is high.

## B. Secondary sources — used for context and timeline ⚠️

Facts drawn from these are marked "per secondary sources" in the body text.

| URL | What was taken |
|---|---|
| <https://www.marktechpost.com/2026/09/10/openai-launches-the-agents-api-in-public-beta-putting-the-codex-harness-behind-one-api-call/> | Agents API beta date, partner list, pricing structure |
| <https://kenhuangus.substack.com/p/from-software-engineering-to-harness> | "Codex as a platform" publication date (2026-08-19), ARC-AGI-3 figures |
| <https://codex.danielvaughan.com/2026/04/15/codex-app-server-complete-guide/> | 30-minute idle thread unload, `-32001` backpressure, WebSocket port |
| <https://www.opensourceforu.com/2026/08/openai-open-sources-codex-harness/> | Open-source release date (2026-08-20), Apache-2.0 |
| <https://blog.sandbase.ai/openai-codex-app-server-harness-2026/> | General context |

### Unverified / conflicting items

| Item | Status |
|---|---|
| Exact publication date of "Codex as a platform" | Secondary sources disagree: **Aug 19 vs Aug 20**. The body text says "August 2026" |
| GPT-5.6 Sol on ARC-AGI-3: 13.3% → 38.3%, 6× fewer output tokens | Cited from secondary sources. **Original not verified** |
| App Server WebSocket default port `127.0.0.1:9090`, CSRF (rejecting `Origin` headers) | Only mentioned in secondary sources. Not found in the repo or official docs |
| 30-minute idle thread unload | Only mentioned in secondary sources |
| JSON-RPC `-32001` (server overloaded) | Only mentioned in secondary sources |
| Claims that the `initialize` response contains `serverInfo`/`capabilities` | **Wrong.** Per the generated schema, `InitializeResponse` has 4 fields: `userAgent`, `codexHome`, `platformFamily`, `platformOs`. These notes follow the repository |
| Agents API model IDs (`gpt-6-astra`, `gpt-5.6-terra`) | Values appearing in doc examples. The list of available models needs separate verification |
| Windows sandbox internals (ACL / WFP / token / desktop mechanisms) | **Inferred from module names** in `windows-sandbox-rs`, not from prose documentation. [14](14-windows-sandbox.md) labels this explicitly. Treat as a map of the problem space |
| The list of 9 Agents API partner sandboxes | The secondary source (MarkTechPost) and the Agents SDK client table partially disagree (DigitalOcean and Oracle are absent from the SDK client table). Agents API environment options and Agents SDK sandbox providers **may be different lists**. The `environments/self-hosted` guide has a "Sandbox providers" section that should settle this — not yet extracted |

### Resolved since the first pass ✅

| Item | Resolution |
|---|---|
| `POST /agents/environments/{id}/files` body schema | It is `HostedEnvironmentFileParam` (`file_id` \| `inline`). See [08 §1.8](08-agents-api-reference.md) |
| Vault management endpoints | 9 endpoints under `/v1/vaults`, outside the `Agents` tag. See [10 §3](10-agents-api-tools.md) |
| Required API key scopes | `api.agents.read`, `api.agents.write`, `api.responses.write`, plus `api.vaults.*`. From the quickstart and security guides |
| Webhook event list | 5 events, documented in `sessions/webhooks`. See [11 §2](11-agents-api-operations.md) |
| Hosted sandbox limits and expiry | Documented in `environments/openai-hosted` and `environments/files`. See [09](09-agents-api-environments.md) |

## C. Could not be reached from this environment

- `openai.com/index/*` — HTTP 403 (both WebFetch and curl with a browser UA). Worked around via mirrors
- `developers.openai.com/api/reference/...` — 404 to plain fetches (client-rendered).
  **Replaced by the OpenAPI spec, which is more precise anyway**
- `.../guides/agents-api/webhooks.md` and `.../limits.md` — 404; the real paths are
  `.../sessions/webhooks.md`, and limits are distributed across the environment guides

## D. Reproduction

```bash
# Count the protocol methods yourself
B=https://raw.githubusercontent.com/openai/codex/main/codex-rs/app-server-protocol/schema/typescript
curl -s $B/ClientRequest.ts      | grep -o '"method": "[^"]*"' | wc -l   # 104
curl -s $B/ServerRequest.ts      | grep -o '"method": "[^"]*"' | wc -l   # 10
curl -s $B/ServerNotification.ts | grep -o '"method": "[^"]*"' | wc -l   # 84

# Generate locally
codex app-server generate-ts
codex app-server generate-json-schema

# Read any documentation page as raw Markdown
curl -sL https://developers.openai.com/api/docs/guides/agents-api/tools/mcp.md

# Agents API endpoints from the OpenAPI spec
curl -sL https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml -o /tmp/openapi.yaml
grep -nE '^  /(agents|vaults)' /tmp/openapi.yaml
```
