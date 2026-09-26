# 99. Sources and Verification Status

Research date: 2026-09-14 (Agents API reference extracted 2026-09-15)
Drift re-check: 2026-09-26 against `openai/codex@e72da2b538` and `openai/openai-openapi@d983890f77` — see [§E](#e-drift-re-check-2026-09-26)

## A. Primary sources — verified directly ✅

### Repository (highest confidence; the generated schemas are authoritative **for the stable surface only** — see §E.2)

| Path | Contents |
|---|---|
| [`openai/codex` README](https://github.com/openai/codex/blob/main/README.md) | Installation, authentication, doc links |
| [`codex-rs/app-server/README.md`](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md) | Recent protocol changes, user verification, attachments, plugin settings |
| [`codex-rs/docs/protocol_v1.md`](https://github.com/openai/codex/blob/main/codex-rs/docs/protocol_v1.md) | The legacy SQ/EQ core protocol |
| `codex-rs/app-server-protocol/schema/typescript/ClientRequest.ts` | **104 stable client methods** (107 at head). Experimental methods are filtered out at generation — 166 in total at baseline, 170 at head (`src/protocol/common.rs`) |
| `codex-rs/app-server-protocol/schema/typescript/ServerRequest.ts` | **10 server requests** |
| `codex-rs/app-server-protocol/schema/typescript/ServerNotification.ts` | **84 server notifications** (85 at head). Experimental notifications are **not** filtered |
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
`SessionTurnErrorCodeResource` (17 codes; 18 at head), `SessionArtifactResource`, and the pagination envelope.

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
| `codex-rs/tools/src/tool_spec.rs`, `tools/src/responses_api.rs` | `ToolSpec` (5 variants), `ResponsesApiTool`, `ResponsesApiNamespace`, `FreeformTool` |
| `codex-rs/models-manager/models.json` | Which models set `use_responses_lite` |
| `codex-rs/models-manager/src/manager.rs`, `src/model_info.rs` | Slug resolution: longest-prefix match, namespace strip, fallback |
| `codex-rs/protocol/src/openai_models.rs` | `ModelInfo` field list and defaults |

Also read: `.../guides/agents-api/environments/self-hosted.md` §Sandbox providers and
`.../guides/agents/sandboxes.md` §Sandbox providers — the two provider rosters.

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
| <https://www.opensourceforu.com/2026/08/openai-open-sources-codex-harness/> | Open-source release date (dated 2026-08-20 in IST; see below), Apache-2.0 |
| <https://blog.sandbase.ai/openai-codex-app-server-harness-2026/> | General context |

### Unverified / conflicting items

> Three entries remain. Two are deliberate records rather than open questions; the third is narrowed below.

| Item | Status |
|---|---|
| Claims that the `initialize` response contains `serverInfo`/`capabilities` | **Wrong.** Per the generated schema, `InitializeResponse` has 4 fields: `userAgent`, `codexHome`, `platformFamily`, `platformOs`. These notes follow the repository |
| Agents API model IDs (`gpt-6-astra`, `gpt-5.6-terra`) | **Narrowed.** Both are real slugs in the bundled Codex catalog (`models-manager/models.json`), which carried exactly nine at baseline: `gpt-6-astra`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-daybreak-blue-latest`, `gpt-daybreak-red-latest`, `gpt-5.5`, `gpt-5.4`, `codex-auto-review` (ten at head: + `gpt-6-sol`, `gpt-6-luna`, − `gpt-5.4`). What remains unverified is whether the **Agents API** server-side list matches this client catalog — they are separate surfaces. **Re-checked 2026-09-26, still open, and now known to be unanswerable from public artifacts:** the spec's `model` is a free `string` with no enum, no Agents API models page exists (`agents-api/models.md` → 404), and no per-model page lists an Agents row |
| Windows sandbox internals (ACL / WFP / token / desktop mechanisms) | **Partly promoted 2026-09-26.** Originally inferred from module names. Reading the module doc comments confirmed `dpapi.rs`, `wfp.rs`, `setup_mutex`, `installation_record`, and **refuted** `hide_users.rs` (it hides the sandbox user's profile directory, not the desktop). Remaining modules are still name-inferred. [14 §6](14-windows-sandbox.md) |

### Secondary-source claims, re-checked against the repository

Four of the five were settled by reading the source. **Two were wrong.**

| Claim | Verdict | Evidence |
|---|---|---|
| JSON-RPC `-32001` "Server overloaded; retry later.", queue capacity 128 | ✅ **Confirmed exactly** | `app-server/src/error_code.rs` (`OVERLOADED_ERROR_CODE`), `app-server-transport/src/transport/mod.rs` (`CHANNEL_CAPACITY = 128`, the literal message string) |
| ARC-AGI-3: GPT-5.6 Sol 13.3% → 38.3%, output tokens sixfold lower | ✅ **Promoted to primary** | Stated verbatim in the "Codex as a platform" post itself, which links a dedicated write-up (`openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/`) |
| WebSocket CSRF — requests with an `Origin` header are rejected | ✅ **Confirmed** | `transport/websocket.rs`, `reject_requests_with_origin_header` middleware |
| WebSocket **default port `127.0.0.1:9090`** | ❌ **Refuted** | `AppServerTransport::DEFAULT_LISTEN_URL = "stdio://"`. No default WS port exists; `ws://IP:PORT` is explicit. `9090` appears nowhere relevant in the repo |
| **30-minute** idle thread unload | ❌ **Refuted** | `thread_unload_delay_secs` — "Defaults to **60**; zero unloads immediately. Changes require a server restart." Requires no subscribers **and** no activity |

Corrected in [02](02-app-server-protocol.md) §2, §4, §11.

#### The publication date, settled

The page's Markdown carries no publication date and `last-modified` reflects the site build, so the
answer came from the Internet Archive. The **earliest** capture of
`developers.openai.com/blog/codex-as-a-platform` is:

```
20260819210742   →  2026-08-19 21:07:42 UTC
```

The post was therefore live on **2026-08-19**, at 14:07 PDT — ordinary US business hours.

**Both secondary sources were right in their own timezone.** That same instant is:

| Zone | Local time |
|---|---|
| US Pacific (PDT) | 2026-08-19 14:07 |
| US Eastern (EDT) | 2026-08-19 17:07 |
| UTC | 2026-08-19 21:07 |
| India (IST) | **2026-08-20** 02:37 |
| Korea / Japan | **2026-08-20** 06:07 |

The US-based source said Aug 19; the India-based one said Aug 20. Not a contradiction — a timezone
artifact. These notes use **2026-08-19**.

**Every unverified and conflicting item raised in this research is now closed.**

### Resolved in the adapter pass ✅

| Item | Resolution |
|---|---|
| `response.new_tool_event`, `response.metadata` | Neither needs a Chat-side source. `new_tool_event` is unhandled (its test is named `"unknown"`); `metadata` carries only OpenAI-platform side channels. [16 §9.1](16-responses-chat-adapter.md) |
| `stream_options.reasoning_summary_delivery` | Never sent to a non-OpenAI provider — gated on `is_openai()`, a literal provider-name comparison. [16 §9.2](16-responses-chat-adapter.md) |
| `ResponsesApiTools` shape | `ToolSpec` has 5 variants. Function tools re-wrap mechanically (flat → nested), but **namespaces need bidirectional name rewriting** and **freeform tools lose their grammar**. [16 §9.3](16-responses-chat-adapter.md) |

### Corrections this pass made to earlier claims

| Earlier claim | Correction |
|---|---|
| "Synthesize 25 SSE events; this is the bulk of the work" | Only **12** are handled and **7** suffice. Tool-call argument streaming is ignored entirely. Streaming is smaller than estimated |
| `AdditionalTools` listed as a droppable Responses-native variant | In `responses_lite` mode it **is** the tool list — not droppable. A second request shape was missed |
| The two 9-entry sandbox provider lists looked contradictory | **Both sources were correct.** They are different rosters for different products — 7 shared, DigitalOcean + OCI are Agents-API-only, Unix-local + Docker are SDK-only. [09 §8](09-agents-api-environments.md) |
| "Whether lite mode is reachable is worth pinning down" (left open) | Resolved: it is a per-model catalog flag, **true for every current-generation model**, resolved by longest-prefix slug matching, with no `config.toml` override. [16 §10.2](16-responses-chat-adapter.md) |

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
curl -s $B/ClientRequest.ts      | grep -o '"method": "[^"]*"' | wc -l   # 104 (107 at 2026-09-26) — stable only
curl -s $B/ServerRequest.ts      | grep -o '"method": "[^"]*"' | wc -l   # 10
curl -s $B/ServerNotification.ts | grep -o '"method": "[^"]*"' | wc -l   # 84 (85)

# The full client surface, including experimental methods the schema omits
S=https://raw.githubusercontent.com/openai/codex/main/codex-rs/app-server-protocol/src/protocol/common.rs
curl -s $S | awk '/^client_request_definitions! *\{/,/^\}/' | grep -cE '=> "[a-zA-Z/_]+"'   # 170
curl -s $S | grep -oE '#\[experimental\("[^"]*"\)\]' | sort -u | wc -l                       # 86 tags (63 client requests + 1 server request + 22 notifications)

# Generate locally
codex app-server generate-ts
codex app-server generate-json-schema

# Read any documentation page as raw Markdown
curl -sL https://developers.openai.com/api/docs/guides/agents-api/tools/mcp.md

# Agents API endpoints from the OpenAPI spec
curl -sL https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml -o /tmp/openapi.yaml
grep -nE '^  /(agents|vaults)' /tmp/openapi.yaml
```

## E. Drift re-check, 2026-09-26

Baseline `openai/codex@2fdcdeaf0e` (2026-09-15, "Add startup tool allowlists for threads") → head
`e72da2b538` (2026-09-26), **686 commits**. Agents API spec baseline `openai/openai-openapi@de408863f9`
→ head `d983890f77`. Every doc was re-read claim by claim against both revisions; each changed claim
is marked *(2026-09-26)* in the body. Roughly 170 checkable claims were confirmed unchanged.

The re-check found two kinds of change, and they are recorded separately because they mean different
things: **drift** is the world moving; a **refutation** is these notes having been wrong on the day
they were written.

### E.1 Refutations — wrong at the baseline ❌

| Doc | Claim | What the source says |
|---|---|---|
| [02 §6](02-app-server-protocol.md) | "Client → server methods (**104 total**)", "the full `ClientRequest` list" | 104 is the **stable** subset. `client_request_definitions!` held **166** methods at baseline. The TS schema is generated without `#[experimental]` methods — see §E.2 |
| [02 §9](02-app-server-protocol.md) | UserInput kinds `image`/`local_image`/`skill`/`mention` | That table is protocol v1. v2 `UserInput.ts` uses `localImage` and also has `audio`/`localAudio` |
| [02 §11](02-app-server-protocol.md), [06](06-choosing.md) | `codexErrorInfo: "ContextWindowExceeded"` | The wire form is camelCase (`contextWindowExceeded`); `httpConnectionFailed` is an object variant |
| [03](03-sdk.md) | "The SDKs spawn the CLI and exchange JSONL; they may later be rebuilt on App Server" | True of the TS SDK only. The **Python SDK already speaks App Server JSON-RPC** over `codex app-server --listen stdio://` (`sdk/python/src/openai_codex/client.py`) |
| [04](04-cli-exec.md) | `--full-auto` is deprecated | **Removed** from `codex exec` on 2026-07-30 (#36054) |
| [04](04-cli-exec.md), [06](06-choosing.md) | `codex mcp-server` is an integration path | **Removed** on 2026-09-05 (#42993), ten days before the baseline. Only `codex mcp` (manage external servers) remains |
| [12 §2.3](12-product-surface.md), [13 §8](13-marketplace-and-plugins.md) | Plugin method list | Omits `plugin/search` (experimental; present at both revisions) |
| [14 §6](14-windows-sandbox.md) | "Elevated mode needs a privileged service — not something a single user-mode process can do" | `service_identity.rs`: unpackaged callers "may use ordinary elevated setup when it is absent". The service is the **packaged** path, not a requirement |
| [14 §6](14-windows-sandbox.md) | `hide_users.rs` = desktop isolation (inferred) | Hides the sandbox user's **profile directory** (HIDDEN\|SYSTEM). Account hygiene, not UI isolation |
| [14 §7](14-windows-sandbox.md) | `windows/worldWritableWarning` shows detection separate from enforcement | Nothing emits it at either revision. The detector was unused at baseline and is deleted at head (#47943). A vestigial protocol entry ⚠️ |
| [15 §4](15-model-providers.md) | Project-local config denylist | Also contains `responses_api_metadata` and `experimental_realtime_webrtc_call_base_url` |
| [16 §1–2, §7](16-responses-chat-adapter.md) | `ResponsesApiRequest` has **17** fields | **16** at both revisions. The mapping table has more rows because it splits sub-fields |
| [16 §10.1](16-responses-chat-adapter.md) | "The lever is just the provider `name`" | Tool-result metadata and MCP attribution are also filtered by a first-party HTTPS destination check ⚠️ |
| [agent-ux/03 §1.2.1](../agent-ux/03-openai-codex-chatgpt.md) | Three methods the ChatGPT client calls mean `docs/02` "has drifted" or they are experimental | **Neither.** See §E.3 |

Also previously unstated, true at both revisions: `responses_lite` forces `parallel_tool_calls` off,
and the WebSocket transport sends `previous_response_id`, so "fully stateless" holds for HTTP only.

### E.2 The generated schema is a filtered view

This section's own header called the generated schemas authoritative. They are — for what they
contain. `app-server-protocol/src/export.rs` drops every method tagged `#[experimental(...)]` from the
**client request** schema, but keeps experimental **notifications**:

| | In source (`common.rs`) | In `ClientRequest.ts` / `ServerNotification.ts` |
|---|---|---|
| Client requests, baseline | 166 | 104 (62 experimental omitted) |
| Client requests, head | 170 | 107 (63 omitted; new: `rollout/compress`) |
| Server requests | 11 | 10 (`currentTime/read` omitted) |
| Experimental notifications | 22 | 22 — all exported |

So the schema describes `thread/queue/changed` but not `thread/queue/add`, and the realtime
notifications but not `thread/realtime/start`. A reader counting the schema sees a protocol that cannot
drive half of its own events. The omitted methods are not dead code: all of them are in the engine
binary shipped with ChatGPT.app (`codex-cli 0.158.0-alpha.2.1`), and the desktop client calls about 33
of them. They require `experimentalApi: true`. Listed in [02 §6](02-app-server-protocol.md).

**Method note:** "read the generated artifact, not the prose" is still the right rule. The refinement is
to check what the generator **excludes** before treating its count as a total.

### E.3 Methods that exist only in the shipped client

The ChatGPT desktop webview (`app.asar`, build 26.924.22138, extracted 2026-09-26) references protocol
methods found **nowhere** in `openai/codex` — not at head, not in any commit (`git log -S`), and not in
the bundled engine binary. Detection was positive-controlled: the same scan finds `gatewayOAuth` (6) and
`requestUserInput` (3) in the binary.

| Method | Source history | Bundled engine |
|---|---|---|
| `item/tool/requestOptionPicker`, `item/plan/requestImplementation`, `item/tool/requestSetupCodexContextPicker` | 0 commits | absent |
| `thread/startAeon`, `thread/stop`, `turn/addUserMessage`, `plugin/codex` | 0 commits | absent |
| `thread/rollback` | removed 2026-09-11 (#44915) | absent |

`thread/startAeon` shares `thread/start`'s parameter rewriting and request-lifecycle tracing in the
webview, so it is a live code path, not a stray string. Which engine answers it is unknown — the local
one cannot. ⚠️ Plausibly a server-side (cloud) engine or a closed build; neither is verifiable from here.

### E.4 Drift — the world moved

Summarised; details are inline in each doc.

- **Protocol** — `account/gatewayOAuth/{login,read,cancel}` + `account/gatewayOAuth/changed`,
  `InitializeCapabilities.explicitGatewayOauth` (#47207); `mcpAppUi` (#45805); `personality`
  deprecated (#45809); image input `{url} | {fileId}` (#45794); `flexUnavailable` error (#47967).
- **CLI** — `--no-daemon` (#46088), hidden `tcp-tunnel` (#45900); `exec-server` gains `--ws-auth` and
  token flags, none of which apply to remote registration.
- **Windows sandbox** — `windows.sandbox_private_desktop` removed (#46554); a third implementation,
  `mxc` (#46271), not constrained by `allowed_sandbox_implementations`; `audit.rs` deleted (#47943).
- **Model providers** — `model_catalog_url` (#46561) is a second way to control `use_responses_lite`;
  `gateway_oauth` (#46482); `include_internal_metadata` (#48344). Lite table + `gpt-6-sol`,
  `gpt-6-luna`, − `gpt-5.4`; `gpt-5.5` is the only non-lite model.
- **Agents API spec** — turn error codes 17 → 18 (`misalignment_policy_violation`); session update
  can now change model, reasoning effort and service tier; vault credential "rotate" became "update"
  with optional `auth` and a `metadata` map; delete/cancel semantics for still-open turns; `403` on most
  operations. Endpoint paths unchanged.
- **Plugins** — `onboardingSkill` overlay field accepts paths without `./` (#46544).
