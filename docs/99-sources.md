# 99. Sources and Verification Status

Research date: 2026-09-14 (Agents API reference extracted 2026-09-15)
Drift re-check: 2026-09-26 against `openai/codex@e72da2b538` — see [§E](#e-drift-re-check-2026-09-26).
Follow-up: 2026-09-30 against HEAD `bcd6d9ab6b` — App Server notifications 86; Agents roster three surfaces; Windows internals source-read.
Second follow-up: 2026-09-30 against HEAD `92bc601ad6` — goal API `origin` field; Guardian skill-warmup skip; `model_catalog_in_context` ([§E.5](#e5-drift-re-check-2026-09-30-afternoon--bcd6d9ab6b--92bc601ad6)). Third: 2026-10-19 against `b1fd48c48` — +4 methods, +1 notification, approval surface unchanged, `codexErrorInfo` open set, feature defaults ([§E.6](#e6-drift-re-check-2026-10-19--d42056091--b1fd48c48)).
Local checkout: `~/repos/harness-refs/codex`, origin `https://github.com/openai/codex.git` (created 2026-09-30; at creation HEAD `d42056091a`, one TUI commit past the recheck).

## A. Primary sources — verified directly ✅

### Repository (highest confidence; the generated schemas are authoritative **for the stable surface only** — see §E.2)

| Path | Contents |
|---|---|
| [`openai/codex` README](https://github.com/openai/codex/blob/main/README.md) | Installation, authentication, doc links |
| [`codex-rs/app-server/README.md`](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md) | Recent protocol changes, user verification, attachments, plugin settings |
| [`codex-rs/docs/protocol_v1.md`](https://github.com/openai/codex/blob/main/codex-rs/docs/protocol_v1.md) | The legacy SQ/EQ core protocol |
| `codex-rs/app-server-protocol/schema/typescript/ClientRequest.ts` | **107 stable client methods** as of 2026-09-30 (104 at 2026-09-15). Experimental methods are filtered out at generation (`src/protocol/common.rs`; 170 at 2026-09-26) |
| `codex-rs/app-server-protocol/schema/typescript/ServerRequest.ts` | **10 server requests** |
| `codex-rs/app-server-protocol/schema/typescript/ServerNotification.ts` | **86 server notifications** as of 2026-09-30 (84 at 2026-09-15, 85 at 2026-09-26). Experimental notifications are **not** filtered |
| `.../InitializeParams.ts`, `InitializeResponse.ts`, `InitializeCapabilities.ts`, `ClientNotification.ts` | Handshake |
| `.../v2/ThreadStartParams.ts`, `ThreadStartResponse.ts`, `TurnStartParams.ts`, `TurnStartResponse.ts`, `ThreadItem.ts` | Payloads |
| [`sdk/typescript/README.md`](https://github.com/openai/codex/blob/main/sdk/typescript/README.md) | Full TS SDK docs |
| [`sdk/python/README.md`](https://github.com/openai/codex/blob/main/sdk/python/README.md), `docs/getting-started.md` | Full Python SDK docs |

License: **Apache-2.0**

**App Server protocol re-count** — sparse clone of `openai/codex` at HEAD `bcd6d9ab6b`
(2026-09-30 05:29:56 UTC). Method strings extracted from the generated TypeScript schemas with
`grep -o '"method": "[^"]*"'`. Additive since 2026-09-15:

| Delta | Methods | Commit |
|---|---|---|
| +3 client | `account/gatewayOAuth/read`, `account/gatewayOAuth/login`, `account/gatewayOAuth/cancel` | `064e701b0f` 2026-09-22 #47207 |
| +0 server requests | the original 10, including the three `*/requestApproval` methods | — |
| +2 notifications | `account/gatewayOAuth/changed`; `thread/prediction/updated` | `064e701b0f`; `90abcfac02` 2026-09-30 #49480 |

Also new on `initialize.capabilities`: `explicitGatewayOauth`. The prediction commit names
`thread/prediction/request`; that RPC is unimplemented (method-not-found) and is absent from
`ClientRequest.ts`.

Needle search of the schema directory for `item/tool/requestOptionPicker`,
`item/plan/requestImplementation`, and `thread/startAeon`: **0 files**. Public
`learn.chatgpt.com/docs/app-server.md` fetched 2026-09-30: **0 hits**. Those three names live in
the ChatGPT/Codex desktop bundle (26.924.22138); they are outside the generated public protocol.
Recorded in [02 §7.1](02-app-server-protocol.md).

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
| `codex-rs/windows-sandbox-rs/src/`, `windows-sandbox-service/src/` | Windows sandbox internals, source-read 2026-09-30 at HEAD `bcd6d9ab6b` ([14 §6](14-windows-sandbox.md)) |
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

> One entry remains as a record (`initialize`). Agents API model ids and Windows sandbox internals
> are settled 2026-09-30.

| Item | Status |
|---|---|
| Claims that the `initialize` response contains `serverInfo`/`capabilities` | **Wrong.** Per the generated schema, `InitializeResponse` has 4 fields: `userAgent`, `codexHome`, `platformFamily`, `platformOs`. These notes follow the repository |
| Agents API model IDs (`gpt-6-astra`, `gpt-5.6-terra`) | **Settled 2026-09-30.** The Agents API contract is an unconstrained `model` string; official Agents API guides give `gpt-6-astra` as the example slug and enumerate no roster. The bundled Codex catalog is 11 entries (was 9 on 2026-09-15), all `supported_in_api: true`. The platform `ModelIdsShared` enum (Chat/Responses, 89 values) is a different, larger roster. Detail below |
| Windows sandbox internals (ACL / WFP / token / desktop mechanisms) | **Settled 2026-09-30.** Source-read at HEAD `bcd6d9ab6b`. Token: `CreateRestrictedToken` (`DISABLE_MAX_PRIVILEGE \| LUA_TOKEN \| WRITE_RESTRICTED`). ACL: `SetNamedSecurityInfoW` deny ACEs. Network: 12 persistent WFP `FWP_ACTION_BLOCK` filters plus `INetFwPolicy2` offline-user rules. Desktop: `CreateDesktopW` `CodexSandboxDesktop-*`. `hide_users.rs` is Winlogon login-UI hiding, not desktop isolation. No `audit.rs`. Runtime on Windows was not exercised. [14 §6](14-windows-sandbox.md) |

#### Agents API model roster (2026-09-30)

Three published surfaces. They are not the same list.

**1. Agents API contract** — `CreateAgentParams.model` and `SessionAgentConfigParam.model` in
`openai/openai-openapi` `openapi.yaml` (fetched 2026-09-30, 3,880,172 bytes) are `type: string`
with `minLength: 0`, `maxLength: 1048576`, description "The requested model name is preserved."
No enum, no `$ref` to `ModelIdsShared`. Official Agents API Markdown (overview, quickstart,
configuration, multi-agent; fetched 2026-09-30) uses `gpt-6-astra` as the example slug and lists
no other Agents-specific roster.

**2. Bundled Codex catalog** — `codex-rs/models-manager/models.json` (raw `main`, 2026-09-30;
last catalog commit `b1e72963c3` 2026-09-29, #49318). **11** entries, every one
`supported_in_api: true`:

| Slug | `visibility` | `use_responses_lite` | Notes |
|---|---|---|---|
| `gpt-6-astra` | list | true | Agents API example slug |
| `gpt-6.1-sol` | list | true | added 2026-09-29 #49318; catalog default |
| `gpt-6-sol` | list | true | added 2026-09-22 #47332 |
| `gpt-6-luna` | list | true | added 2026-09-22 #47332 |
| `gpt-5.6-sol` | list | true | |
| `gpt-5.6-terra` | list | true | Codex SDK example slug in this study |
| `gpt-5.6-luna` | list | true | |
| `gpt-daybreak-blue-latest` | hide | true | |
| `gpt-daybreak-red-latest` | hide | true | |
| `gpt-5.5` | list | false | classic Responses shape |
| `codex-auto-review` | hide | true | absent from `ModelIdsShared` |

`gpt-5.4` left the bundled catalog on 2026-09-24 (`694d8d45bd`). The 2026-09-15 snapshot of nine
included it.

**3. Platform Chat/Responses enum** — OpenAPI `ModelIdsShared` (89 values, plus an open `string`
arm). Includes the GPT-6 / 5.6 / 5.5 families and `gpt-5.4` (still present). Daybreak aliases sit
on `ModelIdsResponses` (Responses-only). Agents schemas do not reference these enums.

`supported_in_api: true` is the client's claim of API eligibility. This environment has no
`OPENAI_API_KEY`, so a live `POST /v1/agents/sessions` was not exercised.

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
- Live `POST /v1/agents/sessions` — this environment has no `OPENAI_API_KEY`. Runtime acceptance of
  a given Agents `model` slug is therefore unpublished here; the published contract is the
  unconstrained string in the OpenAPI spec

## D. Reproduction

```bash
# Count the protocol methods yourself
B=https://raw.githubusercontent.com/openai/codex/main/codex-rs/app-server-protocol/schema/typescript
curl -s $B/ClientRequest.ts      | grep -o '"method": "[^"]*"' | wc -l   # 107 stable as of 2026-09-30
curl -s $B/ServerRequest.ts      | grep -o '"method": "[^"]*"' | wc -l   # 10
curl -s $B/ServerNotification.ts | grep -o '"method": "[^"]*"' | wc -l   # 86 as of 2026-09-30

# The full client surface, including experimental methods the schema omits
S=https://raw.githubusercontent.com/openai/codex/main/codex-rs/app-server-protocol/src/protocol/common.rs
curl -s $S | awk '/^client_request_definitions! *\{/,/^\}/' | grep -cE '=> "[a-zA-Z/_]+"'   # 170 at 2026-09-26
curl -s $S | grep -oE '#\[experimental\("[^"]*"\)\]' | sort -u | wc -l                       # 86 tags at 2026-09-26

# Generate locally
codex app-server generate-ts
codex app-server generate-json-schema

# Read any documentation page as raw Markdown
curl -sL https://developers.openai.com/api/docs/guides/agents-api/tools/mcp.md

# Agents API endpoints from the OpenAPI spec
curl -sL https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml -o /tmp/openapi.yaml
grep -nE '^  /(agents|vaults)' /tmp/openapi.yaml

# Bundled Codex catalog slugs
curl -sL https://raw.githubusercontent.com/openai/codex/main/codex-rs/models-manager/models.json \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(len(d["models"]));
[print(m["slug"], m.get("visibility"), m.get("supported_in_api"), m.get("use_responses_lite")) for m in d["models"]]'

# Windows sandbox internals (source-read; this clone is sparse)
# CreateRestrictedToken flags, 12 WFP FILTER_SPECS, CreateDesktopW prefix
grep -n 'DISABLE_MAX_PRIVILEGE | LUA_TOKEN | WRITE_RESTRICTED' \
  /tmp/openai-codex/codex-rs/windows-sandbox-rs/src/token.rs
grep -c 'name: "codex_wfp_' \
  /tmp/openai-codex/codex-rs/windows-sandbox-rs/src/wfp/filter_specs.rs
grep -n 'PRIVATE_DESKTOP_PREFIX\|CreateDesktopW' \
  /tmp/openai-codex/codex-rs/windows-sandbox-rs/src/desktop.rs | head

# Durable local checkout for drift checks (this Linux host, 2026-09-30).
# origin MUST be github.com/openai/codex. A personal Gitea mirror as origin
# (e.g. homelab.ddn777.synology.me) lags — fetch GitHub as `upstream` or
# repoint origin before counting.
git -C ~/repos/harness-refs/codex remote get-url origin
# https://github.com/openai/codex.git
git -C ~/repos/harness-refs/codex fetch origin
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
| [agent-ux/03 §1.2.1](../agent-ux/03-openai-codex-chatgpt.md) | Three methods the ChatGPT client calls mean `docs/02` "has drifted" or they are experimental | **Neither.** They belong to a second, cloud-hosted engine or never leave the client. See §E.3 |

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

### E.3 Methods that exist only in the shipped client — they target a second engine

The ChatGPT desktop webview (`app.asar`, build 26.924.22138, extracted 2026-09-26) references protocol
methods found **nowhere** in `openai/codex` — not at head, not in any commit (`git log -S`), and not in
the bundled engine binary. Detection was positive-controlled: the same scan finds `gatewayOAuth` (6) and
`requestUserInput` (3) in the binary. **Resolved 2026-09-27** by tracing the main-process bundle
(`.vite/build/main-*.js`, `src-*.js`):

**The app has a second App Server host.** Beside the local `codex app-server` it spawns, the main process
defines a host with id `durable`, display name `Long-lived`, at `wss://codex-cloud-backend.chatgpt.com/`.
Requests to that host pass through an adapter that the local host does not use:

| Adapter behaviour (host `durable` only) | Evidence |
|---|---|
| `thread/queue/add` is rewritten to `turn/addUserMessage` with `mode: "queue"` | serializer exported as `So`, applied only when `hostId === "durable"` |
| `thread/start` may become `thread/prewarm`; start/turn params gain `environments[].environmentConfigId`, `deferredEnvironment` (for `managed` / `ccarenv_*` environments), `pluginsMcp`, `threadAccess` | same serializer |
| `config/read` and `config/batchWrite` are answered **in the client** from an in-memory config (`/in-memory/config.toml`); `permissionProfile/list` returns an empty list locally | adapter class exported as `xo`, instantiated as `new xo({forwardConfigRequirements: true})` next to the host definition |
| `command/exec` and `fs/*` are refused without an `environmentId`; `thread/read` requires "a server-issued thread ID" | same class — the remote host has no local filesystem |
| `thread/stop` is sent only if the host is durable or the thread's `mode === "durable"`, and falls back to `turn/interrupt` on method-not-found | webview stop handler, then `markDurableAeonStopped` |

So the eight literals sort into four kinds:

| Method | Verdict |
|---|---|
| `thread/startAeon`, `thread/stop`, `turn/addUserMessage` (+ `thread/prewarm`) | ✅ **The durable host's dialect.** "Aeon" is the webview's name for long-lived threads (`aeonThreads`, `aeonExecutionTarget`, `isAeonThread` — 500+ references) |
| `item/tool/requestOptionPicker`, `item/tool/requestSetupCodexContextPicker` | ⚠️ Server→client requests the webview handles but no open-source engine sends — by elimination, the durable host. The option picker also has an open-source-compatible form, a dynamic tool `request_option_picker` over `item/tool/call`; the client handles both |
| `item/plan/requestImplementation` | ✅ **Never on the wire.** The client pushes it into its own request queue (id `implement-plan:<turnId>`) to drive the "Yes, implement this plan" card |
| `plugin/codex` | ❌ **Not a method** — a placeholder string for the marketplace "sparse paths" field. An error in the 2026-09-26 sweep |

`thread/rollback`, removed from the open-source protocol on 2026-09-11 (#44915), is still referenced.

**Dynamic check (2026-09-27, macOS, this account):** the app's own log
(`~/Library/Logs/com.openai.codex/`) records the durable host at every launch —
`remote_connections.connection_state_changed hostId=durable state=disconnected`, followed by
`connection_state_ignored_for_missing_manager`. Across three days of logs it never connects, and none of
the dialect methods appear. The feature is present in the client and **not provisioned for this account**.
A socket-level check cannot settle it either way: `codex-cloud-backend.chatgpt.com` resolves to the same
Cloudflare addresses as `chatgpt.com`. ⚠️ What the durable engine is — a hosted build of the same Rust
engine with a dialect layer, or something else — is not observable from here.

> 📌 This corrects §E.2's framing too. The open-source App Server is **one of two** engines the first-party
> client drives. A third-party client built against `openai/codex` sees the local dialect only.

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
- **Plugins** — Codex overlay `extensions["com.openai"].onboardingSkill` accepts paths without
  `./` (#46544, `resolve_openai_onboarding_skill` prepends the prefix then the shared resolver
  still rejects `..`). Agents API packaging (`skills` / `mcpServers`) still requires `./`; live
  Agents `plugins.md` has no `onboardingSkill`.

### E.5 Drift re-check, 2026-09-30 (afternoon) — `bcd6d9ab6b` → `92bc601ad6`

8 commits, 134 files, +2462 / −598, all authored 2026-09-30. Sparse checkout at
`~/repos/harness-refs/codex`. **No refutation** — nothing previously recorded was wrong; two
drifts and one research-axis item. Method counts (107 stable / 170 experimental, 86 notifications,
10 server requests) were re-checked and are **unchanged**.

- **Protocol — new `origin` field on the goal API (#49598).** `thread/goal/set` and
  `thread/goal/clear` params gain `origin: ThreadGoalMutationOrigin` (`user` | `automatic`).
  Confirmed in the Rust definition (`app-server-protocol/src/protocol/v2/thread.rs:849`) **and** in
  the generated Python SDK (`v2_all.py` — `ThreadGoalSetParams`, `ThreadGoalClearParams`), so this
  is on the wire, not internal. The generated field description states the contract: *"Missing
  provenance does not supply user authorization."* Server behaviour: a user fragment is recorded
  into model history only when `origin === user` and `objective`/`status` is present
  (`thread_goal_processor.rs:199`, `:303`); other combinations still mutate goal state and leave
  history alone. `thread_goal_user_context.rs:2` — *"tool-created goals never use this path."*
  **Read as a provenance discriminator, not a new permission**: the goal API did not widen.
  Recorded in [02 §9](02-app-server-protocol.md).
- **Approval gate — availability is a separate axis from correctness (#49584).** Guardian does not
  consume skills, but host skill/plugin discovery could block its startup or turn creation when the
  primary executor is offline. Both the warmup (`core/src/session/session.rs`) and the per-turn
  snapshot (`core/src/session/turn_context.rs`) now short-circuit on `is_basic_session_source`. The
  regression test disconnects the primary executor and asserts Guardian still **denies** a network
  permission request — i.e. the gate's availability was fixed without weakening the gate.
- **Research axis — `model_catalog_in_context` (#49560), disabled by default.** With the opt-in on
  for multi-agent V1/V2, model listings move out of the `spawn_agent` tool description into
  developer `<model_catalog>` messages, bounded to 1,000 bytes, with picker-visible compatible
  models plus descriptions, reasoning efforts and service tiers. Listings append only when rendered
  content changes. Relevant to the providers-as-data axis; **not yet analysed in `SYNTHESIS.md`.**
- **Not recorded (deliberately).** `d42056091a` TUI fork shortcut (`f`, `agents.fork`) and
  `0b43721d8d` TUI copy treating rendered file targets as plain text are TUI-local ergonomics with
  no client-visible contract change. Four further commits (`de02016798`, `d7b0d4aa66`,
  `92bc601ad6`, `1fc8d54807`) are thread-store internals plus one test-isolation fix — the history
  snapshot work is real but is not part of the protocol surface.
- **Verification status.** Source-read ✅ across protocol definitions, server processors and the
  generated SDK. Live App Server traffic for the new `origin` field ⚠️ **not observed** — the
  behavioural description above is read from the server's own branching, not from a trace.

**Next drift baseline: `92bc601ad6`.** *(superseded by §E.6)*

### E.6 Drift re-check, 2026-10-19 — `d42056091` → `b1fd48c48`

719 commits, 3,281 files, +173,115 / −44,857; tags `rust-v0.160.0` (10-01) … `rust-v0.163.0`
(10-15) in range. Read in three scoped passes (protocol; engine core, features and policy; see
[`harness-artifacts/`](../harness-artifacts/README.md) for the shipped 0.159.3 and 0.163.0 binaries
read the same day). **No refutation** — nothing recorded at the baseline was wrong at the baseline.
The first seven commits of the range are §E.5's. Counts re-done with §E.2's method on both revisions
(the script and both method lists are kept in the session scratch; 171/64 at the baseline against
§E.5's 170/63 — the earlier tally evidently excluded `mock/experimentalMethod`; stable 107 agrees).

| Count | `d42056091` | `b1fd48c48` | Δ |
|---|---|---|---|
| Client requests in `common.rs` (stable + experimental) | 171 (107 + 64) | **175** (108 + 67) | +4 |
| Generated `ClientRequest.ts` (stable only) | 107 | **108** | +1 |
| Server → client requests (`ServerRequest.ts`) | 10 | 10 | 0 |
| Notifications in `common.rs` / generated `ServerNotification.ts` | 85 / 86 | **86 / 87** | +1 |

- **Protocol — four methods and one notification added, none removed or renamed.**
  `thread/attachmentOwner/list` (stable, #50094); `thread/readState/update` and `thread/items/read`
  (experimental, #52395, #52637; `-32600` + `{reason:"readStateConflict", readState}` on a stale
  `expectedRevision`); `account/bedrock/checkGovCloudRequirements` (experimental, #49817);
  notification `thread/readState/changed` (experimental but exported — §E.2's rule holds).
  `TurnStartParams` gains **`parentTurnId` / `rootTurnId`** (stable, #51415 "Expose and persist turn
  lineage") and `responsesapiClientMetadataPatch` (experimental, #54053); `ThreadForkParams.experimentalPredictionMode`
  (#51884); `ThreadListParams.excludedThreadIds` (≤100, #51595); `subAgentActivity` items carry
  `model` and `reasoningEffort` (#51463); `imageGeneration` restructured to `image: GeneratedImageRef`
  + `inputImages[]` (#54398). `ThreadStartParams` unchanged (27 fields, 12 experimental — all already
  at the baseline; [02 §9](02-app-server-protocol.md) lists the generated 15).
- **The approval surface is unchanged.** The ten server→client requests, `CommandExecutionRequestApprovalParams`
  (17 fields), `FileChangeRequestApprovalParams` (7), `ToolRequestUserInputParams` (7) and every
  `ReviewDecision` variant are byte-identical. What moved is *inside* the engine: `SandboxOverride
  { NoOverride, EscalatedSandboxWithRestrictions, BypassSandboxFirstAttempt }` types the controller's
  decision (`protocol/src/sandbox.rs`); MCP elicitation cancellations carry a reason
  (`McpApprovalCancellationReason { User, Interrupted, NonInteractive }`, #54679) and an
  `ElicitationAbandonedEvent`; **Guardian approvals no longer pre-approve an escalated retry**
  (#54263, `RequireEscalated`, `additional_permissions` reset), grants bind to the issuing turn
  (#49880), plugin-hook approvals bind to a bundle content hash (#54619). Widened: `write_stdin`
  review path when held permissions match an active grant (#54119); tools advertised before the
  environment is ready (#54098); sandbox integrity checks are observe-only ("failures and timeouts
  do not prevent command execution", #51843). `item/tool/requestOptionPicker` still has 0 hits in
  the engine — §E.3 stands.
- **The durable-host dialect is still not in the open-source engine.** `turn/addUserMessage`,
  `thread/prewarm`, `thread/startAeon`, `environmentConfigId`, `deferredEnvironment`: 0 files, 0
  commits by `git log -S`. `thread/rollback` survives only as the README removal notice. The
  "read state" feature's word *durable* means locally persisted threads, not the host of §E.3.
- **`codexErrorInfo` became an open set (#49806).** `v2/shared.rs:121-127` adds an `untagged`
  `Other` variant (`"other" | string | {[key]: unknown}`) and the schema export rewrites
  `/definitions/CodexErrorInfo` from `oneOf` to `anyOf` + `{"type":["string","object"]}`. A client
  that `match`es a closed enum breaks. New `-32600` data: `{"reason":"serverShuttingDown"}`;
  `-32603` when `useStateDbOnly:true` cannot answer ("not evidence that history is exhausted").
- **Transport.** WebSocket zstd negotiation (#54930): header `x-codex-app-server-compression`,
  protocol `zstd-stream-v1`, binary frames afterwards; behind `app_server_websocket_compression`
  (UnderDevelopment, off). stdio JSONL and `--listen` unchanged. `codex remote-control` now uses the
  managed daemon by default and `--no-daemon` opts **out** (#50803) — §E.4's reading is inverted.
  `verified_local_daemon_socket()` guards against an SSH-forwarded default socket (#54421). The
  exec-server compatibility baseline rose `0.156.1` → `0.162.1` and became date-selected (#52700,
  #54623); `fs/writeBlock` streaming (#49778), scoped executor credentials (#54346), remote credential
  masking (#54309) are exec-server ↔ app-server internals. No minimum-version string was added on the
  engine side; the one that exists (`0.141.0`) is in the ChatGPT desktop shell
  ([`harness-artifacts/02`](../harness-artifacts/02-desktop-shells.md) §3.1).
- **Features (`features/src/lib.rs`, 168 → 192 keys, 0 removed as keys).** Defaults that flipped:
  `code_mode_interrupt` false→true (Stable, #51835), `instant_interrupt` false→true (#51812),
  `api_key_model_discovery` false→true, `api_key_cyber_access_programs` false→true (#53717);
  `worktrees` and `realtime_conversation` became always-on (#54175); `apply_patch_preserve_line_endings`
  removed (always preserve, #51203). Unchanged: `code_mode` off, `code_mode_only` off,
  `code_mode_host` on, `tool_search` always on, `unified_exec` on, `guardianv2` off,
  `guardian_approval` on, `memories` off, `model_catalog_in_context` off, `shell_snapshot` on,
  `hooks` on. Added (24), all off unless noted: `code_mode_tool_search` (#51209,
  `await tools.tool_search({query, limit: 8})`), `code_mode_host_grpc`, `code_mode_only_strict_3p_tools`
  (#50687), `credential_masking` (#52302), `async_compaction` (#53595), `retain_client_tool_outputs`
  (#52937, 64,000-token budget), `mcp_tool_list_changed` (#54656), `guardian_trust_orchestrator_connectors`
  (#52250), `subagent_default_context_limits`, `wake_on_agent_messages`, `executor_capability_discovery_v2`,
  `output_token_replay`, `app_server_websocket_compression`; on: `cli_daybreak` (#53701),
  `ultrafast_mode` (#51253, `service_tier_enabled("ultrafast")`).
- **Tool catalog.** 29 tool names unchanged. `exec_command` always carries `shell` and `login`
  (#54098); `request_permissions` / `view_image` no longer require `has_environment()`;
  `tool_search` exposure condition changed from `supports_search_tool && namespace_tools_enabled`
  to `supports_search_tool && tool_policy.allows && deferred ≥ 1` (#50447 removed the
  `namespace_tools` capability gate; `spec_plan.rs:392-397`). MCP exposure rule unchanged (search on →
  all `Deferred`). Parallel read-lock paths widened to skill/memory/history reads, plugin and agent
  listings, `get_context_remaining`, `get_goal` and dynamic tools (#52245, #54654). `ToolExposure`
  has **six** variants (`DirectModelOnly`, `CodeModeOnly` in addition to the four) — already at the
  baseline; [`harness-artifacts/03`](../harness-artifacts/03-tool-use-patterns.md) §3 corrected.
- **Numeric limits** (03 §3 table): every value the same or moved by a few lines (exec 1 MiB; model
  output 10,000 tokens; unified_exec 250–30,000 / 5,000 / 300,000 ms / 64; tool_search 8; MCP spec
  8,000 / 64,000 B; code mode 10,000 / 10,000 / 10,000; rejection 900 tokens; 95 % window;
  compaction 20,000 / 64,000; image 7,373 B; file-search 20; wait_agent 30,000 ms; transport 15
  MiB; 4 bytes/token). Changed: `executed_tool_call` argument caps (8 KiB / 32 KiB) **removed**
  (#52268); memories gained `MAX_ROLLOUT_BYTES` 8 MiB and `MAX_RECORD_BYTES` 1 MiB (#53940);
  memory extension resources kept 7 → 14 days (#54033). Corrections to 03 §3 made the same day:
  the 95 % constant lives in `models-manager/src/model_info.rs` (there is no `openai_models.rs`);
  AGENTS.md is capped in **bytes** (`DEFAULT_PROJECT_DOC_MAX_BYTES = 32 * 1024`), the 10,000-token
  figure is the skill-metadata budget. `models.json`: 11 slugs, `gpt-5.5` the only non-lite — unchanged.
- **Policy, sandbox, network.** `execpolicy` grammar untouched (0 commits); `ExecPolicyCommandOrigin::PowerShellLiteral`
  (#54076). Approval cache key `UnifiedExecApprovalKey { environment_id, executable, command, cwd,
  tty, sandbox_permissions, additional_permissions }` unchanged. Network proxy: DNS lookups only
  after allow-list or policy approval, Seatbelt's external port-53 allowance removed (#51650);
  broker credential aliases block MITM-hook bypass (`403 blocked-by-mitm-hook`, #52661). Windows:
  `mxc` moved to split crates and `is_available()` now probes by creating a security environment
  (#52707). Hooks: `PreModelRequest` / `PostModelRequest` observe-only (#55144).
- **Not read (deliberately):** `codex-rs/tui` (1,076 files — TUI ergonomics), `ext/` (175),
  `rmcp-client`, `thread-store`/`state` internals, `.github`. The counts above are the comparable
  measure; everything else in the 719 commits is ⚠️ unread.
- **Verification status.** Source, generated schemas and SDK read statically ✅; live traffic ⚠️.

**Next drift baseline: `b1fd48c48`** → superseded by §E.7 (`79a19cbb3`).

### E.7 Drift re-check, 2026-10-20 — `b1fd48c48` → `79a19cbb3`

46 commits in ten hours (2026-10-19 13:27 → 23:01 UTC), 375 files, +19,418 / −2,937; **no tag** in the
range (last is `rust-v0.163.0`, 10-15). Same scoped method as §E.6, counts re-derived with a fresh
parser on both revisions (the macro tables `client_request_definitions!` etc. in `common.rs`; the
baseline numbers reproduce exactly). **No refutation.**

| Count | `b1fd48c48` | `79a19cbb3` | Δ |
|---|---|---|---|
| Client requests in `common.rs` (stable + experimental) | 175 (108 + 67) | **176** (108 + 68) | +1 experimental |
| Generated `ClientRequest.ts` / `ServerRequest.ts` / `ServerNotification.ts` | 108 / 10 / 87 | 108 / 10 / 87 | 0 |
| Notifications in `common.rs` | 86 (62 + 24) | 86 | 0 |
| `features/src/lib.rs` keys (`key:` occurrences) | 180 | **181** | +1 |

- **Protocol: one experimental request, nothing else.** `thread/sample` (#55339,
  `ThreadSampleParams { thread_id, expected_turn_id, prompt, effort?, turn_trigger? }`) — a side
  sample against a thread without a turn; excluded from the generated schema by §E.2's rule. Every
  approval type is **byte-identical**: `CommandExecutionRequestApprovalParams`,
  `FileChangeRequestApprovalParams`, `ToolRequestUserInputParams`, `ReviewDecision`, `SandboxOverride`,
  `McpApprovalCancellationReason`, `ThreadStartParams` (27), `TurnStartParams`, the `ServerRequest`
  table and `CodexErrorInfo` (md5 of each block equal at both revisions). The generated JSON changed
  only where `PlanType` gained `sci` / `sci_plus` ("Academic Researchers", counted as workspace
  accounts, #55387) and the `ModelInfo` catalog gained `approved_prefixes` (below).
- **The durable-host dialect is still absent**: `turn/addUserMessage`, `thread/prewarm`,
  `thread/startAeon`, `environmentConfigId`, `deferredEnvironment`, `item/tool/requestOptionPicker` —
  0 commits by `git log -S`, 0 files at head. §E.3 stands for a fourth check.
- **Approval, as prompt data.** #55366 lets a served model catalog entry carry a template
  `approved_prefixes: Option<String>` (`protocol/src/openai_models.rs`, "Supports
  `{{ approved_prefixes }}`. Missing or null uses the bundled text; an empty string suppresses the
  approved-prefix section") rendered by `prompts/src/permissions_instructions.rs` from the execpolicy
  `prefix_rule(... decision="allow")` set. The *decision* path is untouched; what moved is how the
  model is **told** which prefixes are pre-approved — the catalog (§2.3 of `SYNTHESIS`, "providers
  as data") now also shapes the permission prose.
- **Guardian (`ext/guardian-reviewer`, 3 commits).** Interrupted reviews **roll back** admitted
  context (`SessionDisposition::Rollback`, "Interrupted turns roll back admitted context; completed
  inference errors can retain it", #55395); native agent messages deduplicated in the review context
  (#55391); retry metrics and turn attribution (#55347). `core/src/guardian/{decision,review}.rs`
  changed by 17 lines; the `RequireEscalated` reading of §E.6 is unchanged.
- **Sandbox.** `sandboxing/src/bwrap.rs` (+93): the pre-sandbox executable lookup now **rejects
  replaceable symlinks** — a path whose parent is writable by the caller (`symlink_metadata`, owner
  `uid == euid` checks, policy matched "through parent aliases without resolving the child symlink")
  no longer resolves to a read-only system target (#55384; test
  `skips_writable_bwrap_symlink_to_read_only_target`). Windows `mxc-sandbox` migrated to `mxc-sdk`
  (#55378, policy.rs −49/+… net −20 lines); `docs/14` §3's `mxc` mode and `prefer_mxc` gate are not
  renamed. `execpolicy`: 0 commits.
- **Features.** `incremental_tools` **UnderDevelopment/off → Stable/on** (#55368, "Enable incremental
  tools by default for Responses Lite" — the request-shape branch of `docs/16` §2 gains incremental
  tool delivery as the default; what "incremental" means on the wire was not read ⚠️);
  `transcript_v2` Deprecated → **Removed** (#55388); new `subagent_thread_environments`
  (UnderDevelopment, off; subagents inherit the configured thread environment, #55327/#55375/#55331).
  My `key:` tally is 180 → 181 where §E.6 reported 192 — a different count, not a removal of 12 keys
  (`features/src/lib.rs` has no deletions in the range); the comparable figure is the Δ.
- **New crate `runtime-agent-instance`** (#55398, #55402): "Ephemeral OpenAI runtimes: composite
  registration and per-request assertions" — one-call registration at
  `https://auth.openai.com/agent/register` with `AuthenticatedActorAuthorization { Oauth |
  PersonalAccessToken | PlatformApiKey }`, `AgentHostAuthorization::InstallationId` ("tracking
  metadata, not proof of device ownership"), `RuntimeRole { Orchestrator | Executor |
  OrchestratorAndExecutor }`, and **Ed25519** per-request assertions (`ed25519-dalek`; "registration
  retries keep the key and sign fresh assertions"). Not wired to the app server in this range; a
  runtime-identity leg for the orchestration axis (`gas-city/`, `SYNTHESIS` §2.4) to watch.
- **Startup and auth plumbing.** `codex app-server --print-startup-config` (#55300,
  `StartupConfigArgs`, `CloudStartupConfig { bootstrap, config }`: "Load local policy before auth,
  then fetch the account's cloud configuration" — one-shot, refuses a subcommand); enterprise-managed
  authorization (EMA) for MCP connections (`McpServerAuth::EmaAuth`, extension id
  `ENTERPRISE_MANAGED_AUTHORIZATION_EXTENSION_ID`, gated by `xaa_enabled`, #55334) and EMA authority
  re-checked at HTTP boundaries (#55288); OAuth provenance and login identity recorded on account
  tokens (#55397); Responses API proxy gains GitHub Actions OIDC and renewable federated auth
  (#55296–#55320). Exec-server: environment disconnect notifications deferred until recovery fails
  (#55401).
- **Unchanged and re-checked:** `models.json` 11 slugs (`gpt-5.5` the only non-lite); tool spec
  files (`spec_plan.rs`) untouched; no `const` numeric limit added or removed under `core/src`,
  `models-manager`, `code-mode`; `thread/rollback` survives only in the README notice.
- **Not read:** `tui/` (TUI backend sessions #55381/#55304, title spinners), `file-search`,
  `thread-store`, `cloud-tasks`, `.github`. Live traffic ⚠️.

**Next drift baseline: `79a19cbb3`.**
