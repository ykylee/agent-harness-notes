# Codex Harness Findings

What OpenAI actually opened up, read from the source rather than the announcements — and what it
means for building a harness of our own.

| | |
|---|---|
| Research period | 2026-09-14 → 09-15 |
| Primary sources | `openai/codex` repository, `openai/openai-openapi`, official documentation |
| Output | 17 documents, ~5,000 lines |
| Web version | <https://claude.ai/artifact/6J9zrjCvZQcfDXcKvgUsxo> |
| Korean edition | [REPORT.ko.md](REPORT.ko.md) · <https://claude.ai/artifact/NC1DXYvqdUp1J1sSeKH9bh> |

## Summary — one requirement collides with the platform

Codex removed `wire_api = "chat"`. The `WireApi` enum now has a single variant, `Responses`, and the
old value produces a deliberate deserialization error pointing at a discussion thread.
**Chat Completions support cannot be obtained by wrapping `codex app-server` as-is.**

That single fact reorders the options. Multi-provider support, marketplace, Windows sandboxing and
the full product surface are all well-served by what Codex publishes. The wire protocol is the one
place the platform says no.

## What was opened, and when

A harness is the execution system between a model and a task — thread lifecycle and persistence,
config and auth, sandboxed tool execution. OpenAI opened theirs in three layers: an open-source
binary and protocol, per-language SDKs, and a managed API they operate.

| Date | Release | Significance |
|---|---|---|
| 2026-02-04 | Unlocking the Codex harness | App Server architecture and the JSON-RPC protocol design published |
| 2026-02-11 | Harness engineering | The internal "zero hand-written code" experiment; harness work named as a discipline |
| 2026-08-19 | Codex as a platform | CLI, app-server and SDK positioned as an open agent harness under Apache-2.0 |
| 2026-09-10 | Agents API public beta | The same harness offered as a managed service OpenAI runs |

## Requirement assessment

| Requirement | Verdict | Detail |
|---|---|---|
| **Full product surface** | Well covered | 104 client methods, 10 server requests, 84 notifications. Only ~20 are the agent loop; ~45 is the minimum for a deployable product |
| **Marketplace** | Adopt, don't invent | A vendor-neutral schema exists at `agent-plugins.org`; Codex accepts Claude-compatible manifests. Four source kinds, versioned install cache, per-entry install policy |
| **Windows sandbox** | Heavier than it looks | `elevated` and `unelevated` modes. The strong mode needs a privileged Windows service — an installer and lifecycle problem |
| **Third-party models** | First-class | Providers modelled as data. Five built in deliberately; everything else via `model_providers`. Command-backed token minting absorbs most bespoke auth |
| **Chat Completions** | **Blocked** | Removed. `ollama-chat` retired alongside it. No configuration restores it |

## Adapter feasibility

We read the exact payload Codex constructs rather than comparing specifications. That changed the
answer twice, in both directions.

### The constants that make it tractable

```
store: false,          // entire history resent each turn
stream: true,          // non-streaming path can be skipped
tool_choice: "auto",   // no required/named-tool mapping
include: ["reasoning.encrypted_content"]   // hardcoded
```

Codex is fully stateless on the wire, so an adapter needs **no session store, no response-id registry
and no expiry path** — normally the hardest part of emulating the Responses API.

### Where it holds and where it breaks

| Dimension | Result | Detail |
|---|---|---|
| Request fields | 13 of 17 | Direct or acceptable mappings, including `prompt_cache_key` |
| Session state | Not needed | Stateless adapter, horizontally scalable for free |
| Streaming events | 7 needed | 25 recognised, only 12 handled; tool-call argument deltas ignored entirely |
| Input items | 8 of 18 | 4 droppable, 5 are Responses-native server-side tools |
| Tool translation | Two problems | Namespaces need bidirectional name rewriting; freeform tools lose their grammar |
| Retained reasoning | **Impossible** | Chat Completions has no reasoning item and no slot to return one |

### Why reasoning is the one that matters

Because `store` is false, Codex must resend the model's own prior reasoning — carried in
`encrypted_content` — on every turn. That is how a stateless client keeps a reasoning chain alive.
Chat Completions has nowhere to put it.

OpenAI's own framing makes the cost concrete: on ARC-AGI-3, retained reasoning and context compaction
raised GPT-5.6 Sol from 13.3% to 38.3% while cutting output tokens sixfold. Two harness settings, not
a model change. **The loss is proportional to how much the target model reasons** — for a
non-reasoning third-party model there is no chain to lose.

## Verification record

Every claim taken from a secondary source was re-checked against the repository or the OpenAPI spec.
Two widely repeated facts turned out to be wrong, and one disagreement turned out not to be one.

| Claim | Verdict | Evidence |
|---|---|---|
| JSON-RPC `-32001`, "Server overloaded; retry later.", queue capacity 128 | **Confirmed** | Exact string and `CHANNEL_CAPACITY = 128` in the transport layer |
| WebSocket rejects requests carrying an `Origin` header | **Confirmed** | Dedicated CSRF middleware in the websocket transport |
| ARC-AGI-3: 13.3% → 38.3%, output tokens sixfold lower | **Promoted to primary** | Stated verbatim in OpenAI's own post, with a dedicated write-up linked |
| WebSocket listens on `127.0.0.1:9090` by default | **Refuted** | The default transport is `stdio://`; a WS port must be given explicitly |
| Threads unload after 30 minutes idle | **Refuted** | `thread_unload_delay_secs` defaults to **60 seconds**, and needs no subscribers *and* no activity |
| `initialize` response carries `serverInfo` / `capabilities` | **Refuted** | The generated schema has four fields: user agent, Codex home, platform family, OS |
| Platform post dated Aug 19 or Aug 20 | **Resolved** | Archive's first capture is 2026-08-19 21:07 UTC. Both sources were right in their own timezone |
| Two nine-entry sandbox provider lists contradict each other | **Resolved** | Different products: 7 shared, DigitalOcean and OCI are API-only, Unix-local and Docker are SDK-only |
| Windows sandbox internals (ACL, WFP, token restriction) | **Inferred** | Read from module names in the source tree, not prose docs. Labelled as such throughout |

## Recommendations

1. **Settle the wire protocol boundary first.** It determines whether Codex core is reusable at all.
   Everything else is downstream of this one call.
2. **Build the adapter as a provider-shaped proxy, not a fork.** It wires in at a supported extension
   point and leaves Codex core untouched. Keep it stateless — the moment a response-id store appears,
   the free win is gone.
3. **Make retained reasoning a per-provider capability.** The provider struct already has the shape
   for this.
4. **Ship an explicit model catalog.** Request shape is decided by a per-model flag resolved through
   *longest-prefix slug matching*, with no config override. Naming a model `gpt-6-astra-turbo`
   silently inherits another model's flags.
5. **Adopt the portable plugin schema.** Namespace your own additions rather than inventing a format.
6. **Plan the privileged Windows service early.** It gates the stronger sandbox mode.

## Method

Most corrections came from reading generated schemas and Rust source rather than prose. The method
list, the exact request payload, the error codes and the timeout defaults are all committed artifacts;
blog posts and third-party write-ups drift from them.

One practical discovery paid for itself repeatedly: **appending `.md` to any OpenAI documentation URL
returns the raw Markdown source.** It turned lossy page summaries into primary text with code samples
intact, and surfaced fourteen guide pages we did not know existed.

Three items remain open by design: a corrected secondary-source error kept on the record, the Windows
internals labelled as inference, and the Agents API server-side model list, which is a different
surface from the client catalog. See [99-sources.md](docs/99-sources.md).

---

Findings reflect the state of `openai/codex` on 2026-09-15 — a fast-moving repository.
