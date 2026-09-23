---
type: concept
status: active
last_ingested_from: docs/99-sources.md + REPORT.md + browser-agents/99-sources.md (§4.5 incl. the Brave paraphrase) + browser-agents/11-dia-and-neon.md
related_pages: [concepts/harness, concepts/retained-reasoning, concepts/os-sandbox-policy, concepts/thread-turn-item, concepts/credential-shielding]
created: 2026-09-22
updated: 2026-09-23
---

# Primary-Source Verification — this repository's method of knowing

- Purpose: fix as rules how this repository grades claims and verifies them. New research follows this.
- Scope: the grade vocabulary, the method, preserving refutations, what was actually overturned, reproduction
- Primary sources: `docs/99-sources.md`, `REPORT.md`, `browser-agents/99-sources.md`
- Updated: 2026-09-23

## §1 TL;DR  {#s1-tldr}

| # | Rule | Detail |
|---|---|---|
| 1 | Priority | **committed artifacts over prose.** Generated schemas, source and defaults win |
| 2 | Secondary sources | **not written as settled** before a primary cross-check |
| 3 | Inference | **labelled as inference** inside the document |
| 4 | Refutations | **kept as refutations, not deleted** |
| 5 | Result | of five secondary-source claims checked, **two were wrong** |
| 6 | Practical technique | appending **`.md`** to a documentation URL returns the raw Markdown |

## §2 The grade vocabulary  {#s2-grades}

| Grade | Meaning | How it appears |
|---|---|---|
| **Confirmed** | read directly from a generated schema, source or binary | the evidence path is cited |
| **Promoted to primary** | began as secondary; the same sentence was found in a primary source | the promotion and its basis are recorded |
| **Observed implementation** | revealed by reverse engineering or binary analysis, not vendor-guaranteed | ⚠️ marked as such |
| **Inferred** | read from module names, directory layout or other indirect evidence | ⚠️ **an inference warning in the body** |
| **Self-reported** | a figure published by the vendor with no independent verification | recorded, not used for comparison |
| **Refuted** | confirmed wrong against a primary source | **not deleted**; what was wrong and why is kept |
| **Narrowed** | the range was reduced without closing | what remains open is written down |

## §3 The method  {#s3-method}

Most corrections came from **reading generated schemas and source rather than prose.** Method lists,
exact request payloads, error codes and timeout defaults are all committed artifacts. Blog posts and
third-party write-ups drift from them.

> One practical discovery paid for itself repeatedly: **appending `.md` to an OpenAI documentation
> URL returns the raw Markdown source.** It turned lossy page summaries into primary text with code
> samples intact, and surfaced fourteen guide pages we did not know existed. (`/llms.txt` is the full
> index.)

## §3.5 Generalising the technique, and its limits  {#s3-5-generalization}

**The `.md` suffix and `/llms.txt`** were found in OpenAI's documentation but work elsewhere too —
depending on **how the documentation site renders.**

| Target | `llms.txt` | `.md` | Result |
|---|---|---|---|
| OpenAI docs | — | ✅ | fourteen guides discovered |
| **Aside** | ✅ | ✅ | all 16 product documents obtained as primary text |
| **Opera** | ✅ | — | the Neon entry obtained |
| **Dia** | ❌ | ❌ | every path returns the same SPA shell |

> 📌 **Try it first, but do not trust it as universal.** A client-rendered site is out of reach for a
> static technique. On failure, fall back to the rendered page or the framework payload (a Next.js
> flight payload, for instance).

> This record, and the two traps in §3.6, were **carried back into the Codex study's report**
> ([`REPORT.md`](../../../REPORT.md) § Method, and its Korean edition). A rule learned in one study
> belongs in both.

## §3.6 Two newly recorded traps  {#s3-6-traps}

### Mistaking inheritance for a product feature

Traces of a capability in a fork's binary **may have been inherited from upstream.**

> Real case: post-quantum cryptography (ML-KEM) strings appeared in Aside's browser. But **Chromium
> has shipped X25519MLKEM768 TLS by default since 2024** — any fork shows them. **File location had
> to be separated first**, and only after confirming they sat in the product's own code (the Vault
> extension and the daemon) was it recorded as a product feature.

**Rule: whatever you find in a fork, check first whether upstream already has it.**

### A vendor's own primary sources contradicting each other

> Real case: Opera's `llms.txt` and the Opera Neon product FAQ say opposite things about whether AI
> processing is local.

**Rule: cross-check primary sources against each other too. When they diverge, take the more specific
one and record the contradiction itself.**

## §3.7 Do not read an information gap as a maturity gap  {#s3-7-asymmetry}

Early in the browser study, Comet's internals were well known and Aside's were largely "not
published." That difference was **not product maturity but who had taken it apart** — opening Aside's
binaries filled most of it in.

> 📌 **The same asymmetry persists now.** Aside was verified down to its binaries; Dia and Neon are
> taken on their documentation. A good document is not the same as a good implementation — when
> reading a comparison table, **remember that the evidence grade differs cell by cell.**

## §4 What was actually overturned  {#s4-refuted}

| Claim | Verdict | Evidence |
|---|---|---|
| JSON-RPC `-32001` "Server overloaded; retry later.", queue capacity 128 | ✅ **confirmed exactly** | `app-server/src/error_code.rs`, `app-server-transport/src/transport/mod.rs` (`CHANNEL_CAPACITY = 128`, the literal message) |
| ARC-AGI-3 13.3% → 38.3%, output tokens sixfold lower | ✅ **promoted to primary** | stated verbatim in the "Codex as a platform" post, which links a dedicated write-up |
| WebSocket CSRF — requests with an `Origin` header are rejected | ✅ **confirmed** | `transport/websocket.rs`, `reject_requests_with_origin_header` |
| WebSocket **default port `127.0.0.1:9090`** | ❌ **refuted** | `AppServerTransport::DEFAULT_LISTEN_URL = "stdio://"`. There is no default WS port, and `9090` appears nowhere relevant |
| **30-minute** idle thread unload | ❌ **refuted** | `thread_unload_delay_secs` — "Defaults to **60**." Requires no subscribers **and** no activity |
| `initialize` response carries `serverInfo`/`capabilities` | ❌ **refuted** | `InitializeResponse` has four fields: `userAgent`, `codexHome`, `platformFamily`, `platformOs` |

> Two of five were wrong. **Keeping refutations on the record is what makes this repository
> trustworthy** — delete them and the next reader believes the same secondary source again.

## §5 Cases where the research corrected itself  {#s5-self-corrections}

The same rule was applied to this repository's own earlier statements.

| Earlier claim | Correction |
|---|---|
| "Synthesize 25 SSE events; this is the bulk of the work" | Only **12** are handled and **7** suffice. Tool-call argument streaming is ignored entirely |
| `AdditionalTools` listed as a droppable Responses-native variant | In `responses_lite` mode it **is** the tool list — not droppable. A second request shape was missed |
| The two nine-entry sandbox provider lists looked contradictory | **Both sources were correct.** Different rosters for different products |
| Was the platform post dated Aug 19 or Aug 20 | **A time-zone artifact.** The archive's first capture is 2026-08-19 21:07 UTC, which is 8/20 in IST. Both sources were right in their own zone |
| "Comet is the exact opposite structure to Aside" | ❌ **Refuted.** Aside's agent is an MV3 extension too. The real difference is **planning location** |
| "No product documents input separation" | ❌ **Partly refuted.** Dia documents it concretely |
| Opera Neon's unit of reuse is "Skills" | ❌ **Refuted.** The official name is **Cards**, and the axis differs |
| Brave's Comet demonstration exfiltrated "to the attacker's server" | ❌ **Refuted by the original.** The fourth step posts the data **as a reply to the Reddit comment**; no attacker origin appears in the chain |

> 📌 The last entry is a different kind of error, and a costlier one. It was not a secondary source
> being wrong — the primary source had been read, then **paraphrased** in one line. The paraphrase
> became the threat model ("exfiltration by navigation"), the threat model became a probe in the
> implementation, and the probe then measured a shape the demonstration never had
> ([[concepts/indirect-prompt-injection]] §10.1). **Re-read the original before building a test on
> your summary of it.**

> 📌 The three before it are cases of **a conclusion being overturned as primary material accumulated.**
> That is why refutations are not deleted — deleting them would also delete the reason the earlier
> belief was held.

## §6 What remains open by design  {#s6-open-by-design}

| Item | Status |
|---|---|
| The claim that `initialize` carries `serverInfo`/`capabilities` | **a refutation kept as a record** |
| The Windows sandbox internals (ACL/WFP/token/desktop) | **inferred from module names.** [[concepts/os-sandbox-policy]] §6 says so explicitly |
| Agents API model ids | **narrowed.** The bundled client catalog of nine is confirmed; **whether the Agents API's server-side list matches is unverified** — a different surface |

## §7 Reproduction  {#s7-reproduction}

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

## §8 Shelf life  {#s8-validity}

The Codex study reflects `openai/codex` **as of 2026-09-15**; the browser study reflects 2026-09-22/23.
Both move fast. **The first move of a re-investigation is not gathering new facts but checking
existing facts for drift.**

## §9 A document describing behaviour is not evidence of the behaviour  {#s9-doc-vs-code}

Ingested from [`SYNTHESIS.md` §7](../../../SYNTHESIS.md), added after the repository's conclusions
were implemented.

In that implementation a design document **and** a source comment both stated that page snapshots
included child-iframe contents, while the code walked only the main frame. Nothing failed; the
divergence was found by a review and then measured — **1 of 5 interactive elements visible on a page
with a payment and a consent iframe.**

> 📌 **This repository reads documents for a living.** A vendor's own documentation is the strongest
> grade it usually offers, and that grade is bounded by the fact that a document is a *claim about*
> an implementation. Where a claim matters and an artifact exists, the artifact outranks the prose —
> which is the reason Aside was taken down to its binaries.
>
> A second lesson from the same exercise: **building a conclusion tests it.** Five conclusions that
> had survived reading were refuted by implementation. Where a claim can be cheaply built, that is a
> stronger check than another source.

### §9.1 A third grade, and where it now appears  {#s9-1-third-grade}

The grade ladder in this repository used to end at *read from a primary artifact*. It now has a rung
above it — **attacked, and it failed or held** — and two documents carry claims at that rung:

| Document | Claim now measured |
|---|---|
| [`SYNTHESIS.md` §6.4](../../../SYNTHESIS.md) | Dia's published defences: 16 attacks, 5 through |
| [`REPORT.md`](../../../REPORT.md) external-corroboration section | Rec. 7 (approval a channel can render) moved from corroborated to measured — the gate held where the perception filters did not |

> ⚠️ The rung cuts both ways, and the caveat belongs on this page rather than only where the claims
> are. **Attacking an implementation of a published description grades the description, not the
> vendor.** Dia publishes no definition of "irreversible action button," so the measurement bounds
> what such a description can be relied on to mean — it does not report on their code.

## §10 Read next  {#s10-next}

- [[concepts/os-sandbox-policy]] §6 — where the inferred grade is actually applied
- [[concepts/thread-turn-item]] §3 — where a refutation is actually applied
- [[concepts/credential-shielding]] §4 — where the inheritance trap was actually avoided
- Originals: [`docs/99-sources.md`](../../../docs/99-sources.md), [`browser-agents/99-sources.md`](../../../browser-agents/99-sources.md)
