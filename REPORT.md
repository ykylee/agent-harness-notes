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

> **Scope note (2026-09-23).** This is the report for **the Codex study.** The repository has since
> widened to *agent harnesses generally* and holds a second investigation —
> [`browser-agents/`](browser-agents/README.md), covering browser-type agents (Aside, Comet, Dia,
> Neon, Browser Use). The two are crossed in **[`SYNTHESIS.md`](SYNTHESIS.md)**, which separates the
> design axes that depend on the execution surface from the ones that do not.
>
> Nothing below was invalidated by that study. **Several findings gained external corroboration**,
> collected in [§ External corroboration](#external-corroboration-what-the-browser-study-confirmed).
>
> **Update (2026-09-26).** A third investigation, [`strands/`](strands/README.md), read the Strands
> Agents SDK and the Strands harness (AWS) — a harness linked into the caller's process rather than
> served behind a wire. It invalidated nothing here either; it **qualified two findings** and
> corroborated several others from the negative side, in
> [§ A third case](#a-third-case-what-strands-tested).

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

## External corroboration: what the browser study confirmed

The Codex study was a reading of one vendor's repository. A second study, of browser-type agents,
later examined products built by other people — and several of the recommendations below turned up
**independently implemented in a third-party system.** That is stronger evidence than internal
consistency.

The strongest case is **Aside**, a Chromium-fork AI browser whose daemon binary was extracted and
read ([`browser-agents/09`](browser-agents/09-aside-browser-internals.md)):

```js
CODEX_TOOL_CALL_PROVIDERS = new Set([`openai`, `openai-codex`, `opencode`])
// nearby: supportsAdditionalTools, supportsToolSearch, supportsMidConvoSystemMessages
```

| Finding here | What the browser study showed |
|---|---|
| **The wire protocol boundary is the first decision** (rec. 1) | `openai-codex` is registered **as a model provider id** in a third-party harness. The boundary is not theoretical — other people cross it |
| **`responses_lite` is a second request shape an adapter must handle** ([docs/16 §10.2](docs/16-responses-chat-adapter.md)) | The same daemon carries a **`supportsAdditionalTools` capability flag.** A third-party harness absorbed Codex's two request shapes exactly as recommended |
| **Model a provider as data, not code branches** (rec. 2, 4) | Aside carries **16+ provider ids** as data, with user-supplied subscriptions and API keys. Multi-provider is a real design point, not a hypothetical |
| **Make retained reasoning a per-provider capability** (rec. 3) | The capability-flag pattern is already how that daemon expresses per-provider differences. The shape recommended here is the shape in use |
| **Approval must be a protocol primitive** | Confirmed, and **extended** — Aside's approval prompts carry a button array *and* a numbered text fallback, because they are designed to render in a chat channel. App Server's approvals assume a client UI |
| **Permission expressiveness** | Aside's policy engine matches **tool globs plus per-argument eq/regex**, going beyond `ExecPolicyAmendment`'s shape. Worth copying back |

One thing the browser study **did not** corroborate, because it could not: nothing there speaks to
retained reasoning. Browser agents in scope do not expose that layer.

For the combined build checklist across both studies, see
[`SYNTHESIS.md` §5](SYNTHESIS.md).

### And one recommendation that was later measured, not just corroborated

Rec. 7 — **approval prompts a channel can render** — stopped being an argument from design taste when the
conclusions of both studies were implemented and the injection defences around that gate were
attacked ([`SYNTHESIS.md` §6.4](SYNTHESIS.md)). Sixteen attacks, five through: the perception-layer
filters fell, the gate did not.

> 📌 Assuming the model had been completely persuaded by injected page content, the action was still
> refused and the page never changed. **The gate is the only defence in the stack that is not a
> heuristic an attacker can study**, because it sits outside the model's control loop. That is an
> argument for making approval a protocol primitive rather than a UI feature — and it is now
> measured rather than reasoned.
>
> ⚠️ Qualified by the Strands study below: sitting outside the loop is **necessary, not sufficient.**

## A third case: what Strands tested

Codex and Aside both put a boundary between whoever drives the agent and the loop. **Strands has
none** — "it runs in your process with no hosted control plane." That makes it a test of this
report's recommendations from an angle the first two studies could not reach: what happens to each
one when there is no wire at all. Read from `strands-agents/harness-sdk` @ `15da9dc` (2026-09-25),
its design documents, and probes of its approval paths against the SDK's own scripted mock model.

| Finding here | What Strands showed |
|---|---|
| **Approval must be a protocol primitive** | Corroborated from the negative. Without a wire, Strands' approval is an exception plus a re-entry convention: the tool or hook **re-runs from the top**, so side effects before the approval call happen twice, and nothing outside the process can answer it. Its A2A client refuses to send approval answers at all |
| **The gate outside the loop is the one defence that held** (rec. 7, measured) | **Qualified.** Strands has exactly such a gate, with a Cedar policy backend — and ships it **off**. Probing its error paths found a Cedar `forbid` that errors is **allowed**, a steering handler approves on **any truthy answer, including `"no"`**, policies compose in registration order despite documented precedence, and the CLI turns every deny into an ask. Placement is one property of six ([`SYNTHESIS.md` §2.7](SYNTHESIS.md)) |
| **Model a provider as data** (rec. 2, 4) | **Qualified.** Strands made the opposite choice deliberately: an internal wire that is literally Bedrock ConverseStream, and one converter *class* per vendor. That buys vendor-native features and first-class Chat Completions; it costs operator-level extension. **Provider-as-data holds where the wire is shared** — which it is in Codex, so the recommendation stands there |
| **Make retained reasoning a per-provider capability** (rec. 3) | Corroborated. Every OpenAI path in Strands — Chat Completions **and** Responses — drops reasoning between turns, with a warning. A converter-per-vendor design loses it unless someone decides to keep it; nobody did |
| **Keep the adapter stateless** (rec. 2) | Corroborated. Strands' opt-in stateful Responses mode clears local history after each invocation, refuses a conversation manager outright, and — unverified — appears to resend the invocation's items alongside `previous_response_id` inside a tool loop. State brought its own failure modes, as predicted |
| **Adopt the portable plugin schema** (rec. 5) | Corroborated from the negative. A Strands plugin is a `pip` package with no manifest — nothing a policy layer could inspect or refuse; skills' `allowed-tools` is not enforced |
| **Tool globs with per-argument matchers** (rec. 8) | Corroborated from the negative. Strands' finest policy grain is the tool name; "always allow" for `shell` allows every command |

Two findings are new rather than confirming, and both become recommendations below:

- **The harness's own credentials reach the model's tools.** Provider keys sit in the process
  environment, which every shell call inherits; one approved `env` prints them.
- **An authority tag the model is told to trust is forgeable.** The harness prompt says
  `<system-reminder>` tags in tool results come from the harness; nothing escapes that tag in fetched
  pages, files or MCP output. Read in source, not run against a model.

And one record for this report's own claims: Strands' benchmark headline — "28% lower cost with
equal or better accuracy" — is contradicted by its chart's own data in 7 of 19 same-model pairs.
With no variance reported, that refutes the **wording**, not a ranking.

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

Two more, added after the browser study and grounded in systems other people shipped:

7. **Design approval prompts so a channel can render them.** Buttons plus a numbered text fallback,
   with a hint that a plain reply also works. Remote and asynchronous approval becomes possible for
   free; a client-UI assumption forecloses it.
8. **Reach for tool globs with per-argument matchers** in permission policy. "Allow `bash`" is too
   coarse; "allow `bash` when the first argument matches this regex" is the level that is actually
   useful — and a third party already ships it.

Two more after the Strands study, grounded in what its error paths did when probed:

9. **Give the approval gate all six properties, not just its placement:** on by default, fail closed
   on every error path, answers parsed as an enum, an explicit precedence, a hard deny nothing can
   downgrade, and authorization of the *final* tool input. Test each error path with a control that
   proves the input arrived — Strands' design documents describe the right behaviour for four of the
   six, and the code does otherwise.
10. **Keep the harness's own credentials out of every tool process's environment,** and never tell
    the model that an authority marker can appear in tool results unless every tool result escapes it.

## Method

Most corrections came from reading generated schemas and Rust source rather than prose. The method
list, the exact request payload, the error codes and the timeout defaults are all committed artifacts;
blog posts and third-party write-ups drift from them.

One practical discovery paid for itself repeatedly: **appending `.md` to any OpenAI documentation URL
returns the raw Markdown source.** It turned lossy page summaries into primary text with code samples
intact, and surfaced fourteen guide pages we did not know existed.

**That technique generalises — but not universally.** Applied later to other vendors: Aside ✅ (a
`/llms.txt` index plus `.md` originals, 16 documents), Opera ✅, **Dia ❌** (every path returns the
same client-rendered shell), **Strands ✅ with a variant** (`/llms.txt` works, but raw pages live at
`<page>/index.md` and a constructed `<page>.md` returns 404). Try it first, follow the links the index
gives rather than building URLs, and fall back to the rendered page when it fails.

The browser study also added two verification rules worth carrying back here:

- **Do not mistake inheritance for a product feature.** Post-quantum symbols appear in any Chromium
  fork, because Chromium ships X25519MLKEM768 TLS by default. File location had to be separated
  before a finding could be attributed to the product.
- **Cross-check primary sources against each other.** A vendor's own documentation index and its
  product FAQ contradicted each other on whether planning runs locally. The more specific source wins,
  and the contradiction itself gets recorded.

The Strands study added one more:

- **A design document's status line is not implementation status.** Eleven of thirteen designs
  marked "Proposed" were already implemented — and deviated from their designs exactly where it
  mattered. Designs committed beside code look authoritative; they are graded as intent (📐), never as
  behaviour.

Three items remain open by design: a corrected secondary-source error kept on the record, the Windows
internals labelled as inference, and the Agents API server-side model list, which is a different
surface from the client catalog. See [99-sources.md](docs/99-sources.md).

## Read next

| Interest | Path |
|---|---|
| Codex detail | [`docs/`](docs/) — 16 documents |
| Browser-type agents | [`browser-agents/README.md`](browser-agents/README.md) |
| An embeddable SDK harness (Strands) | [`strands/README.md`](strands/README.md) |
| **All three, crossed** | **[`SYNTHESIS.md`](SYNTHESIS.md)** |
| By concept | [`ai-workflow/wiki/index.md`](ai-workflow/wiki/index.md) — 16 concepts |
| Which claims to trust | [`docs/99-sources.md`](docs/99-sources.md) · [`strands/99-sources.md`](strands/99-sources.md) |

---

Findings reflect the state of `openai/codex` on 2026-09-15 — a fast-moving repository.
External corroboration added 2026-09-23. The Strands case added 2026-09-26 (`harness-sdk` @ `15da9dc`).
