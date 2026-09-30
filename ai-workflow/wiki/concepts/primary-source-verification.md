---
type: concept
status: active
last_ingested_from: docs/99-sources.md + REPORT.md + browser-agents/99-sources.md (§4.5 incl. the Brave paraphrase) + browser-agents/11-dia-and-neon.md + browser-agents/12-dia-binary.md + strands/99-sources.md + strands/01-overview.md + agent-ux/10-acp.md + agent-ux/99-sources.md
related_pages: [concepts/harness, concepts/retained-reasoning, concepts/os-sandbox-policy, concepts/thread-turn-item, concepts/credential-shielding]
created: 2026-09-22
updated: 2026-09-30
---

# Primary-Source Verification — this repository's method of knowing

- Purpose: fix as rules how this repository grades claims and verifies them. New research follows this.
- Scope: the grade vocabulary, the method, preserving refutations, what was actually overturned, reproduction
- Primary sources: `docs/99-sources.md`, `REPORT.md`, `browser-agents/99-sources.md`
- Updated: 2026-09-30 (Strands native Anthropic redacted_thinking: Python KeyError probed; TASK-013)

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

> **Refinement, 2026-09-26: a generated artifact can be a filtered view.** The Codex protocol schema
> drops every `#[experimental]` client method at generation — 104 in the schema, 166 in source at the
> snapshot — while keeping experimental notifications. The count was right about the file and wrong about
> the protocol. Before treating a generated artifact's count as a total, **read the generator for what it
> excludes.** (`docs/99-sources.md` §E.2)
>
> The same re-check found the converse: a shipped client (ChatGPT desktop) calling methods that exist in
> neither the open-source engine nor the engine the app bundles. Traced on 2026-09-27, they belong to a
> **second, cloud-hosted engine** the client also drives (`durable`, `wss://codex-cloud-backend.chatgpt.com/`),
> or never leave the client at all. **An open-source surface is not necessarily the whole surface its own
> vendor's client targets** — and a literal in a bundle is not evidence of a wire call until you have
> found who sends it. (§E.3)

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

### Crate, SDK and schema release numbers are not the wire

> Real case: Agent Client Protocol. The spec crate is `1.9.1`, generated schema `schema-v1.23.0`,
> Strands CLI pins `@agentclientprotocol/sdk` **1.3.0**, npm latest is **1.5.1**. The **wire** is
> the integer `protocolVersion` exchanged at `initialize`, and that is **`1`**. The spec README
> says not to infer wire compatibility from artifact versions
> ([`agent-ux/10`](../../../agent-ux/10-acp.md) §2).

**Rule: when a protocol publishes both a wire version and artifact versions, cite the negotiated
wire field. SDK pin drift is capability surface, not a different protocol.**

## §3.7 Do not read an information gap as a maturity gap  {#s3-7-asymmetry}

Early in the browser study, Comet's internals were well known and Aside's were largely "not
published." That difference was **not product maturity but who had taken it apart** — opening Aside's
binaries filled most of it in.

> 📌 **Narrowed 2026-09-30.** Aside was verified down to its binaries; Dia's macOS app was opened
> the same way ([12](../../../browser-agents/12-dia-binary.md) — ArcCore + seatbelted Claude
> Code). Neon remains a netinstaller stub. A good document is still not the same as a good
> implementation — when reading a comparison table, **remember that the evidence grade differs
> cell by cell.**

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
| Agents API plugin `./` rule and Codex `onboardingSkill` `./`-optional exception are one rule | **Two surfaces.** Live Agents `plugins.md` still requires `./` and has no `onboardingSkill`. Codex `resolve_openai_onboarding_skill` (#46544) prepends `./`, then the shared resolver still rejects `..` |
| "Dia and Neon are taken on their documentation" | ❌ **Narrowed.** Dia macOS opened 2026-09-30 ([12](../../../browser-agents/12-dia-binary.md)). Neon remains a stub |

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
| The Windows sandbox internals (ACL/WFP/token/desktop) | **settled 2026-09-30.** Source-read at HEAD `bcd6d9ab6b`. [[concepts/os-sandbox-policy]] §6. Runtime on Windows not exercised |
| Agents API model ids | **settled 2026-09-30.** Agents API `model` is an unconstrained string (no enum). Bundled Codex catalog is 11 entries, all `supported_in_api: true`. Platform `ModelIdsShared` (Chat/Responses, 89 values) is a third roster. They are three surfaces. 2026-09-27 had closed this as unanswerable from public artifacts; the three-surface reading is that settlement |

## §7 Reproduction  {#s7-reproduction}

```bash
# Count the protocol methods yourself
B=https://raw.githubusercontent.com/openai/codex/main/codex-rs/app-server-protocol/schema/typescript
curl -s $B/ClientRequest.ts      | grep -o '"method": "[^"]*"' | wc -l   # 107 stable as of 2026-09-30
curl -s $B/ServerRequest.ts      | grep -o '"method": "[^"]*"' | wc -l   # 10
curl -s $B/ServerNotification.ts | grep -o '"method": "[^"]*"' | wc -l   # 86 as of 2026-09-30

# Generate locally
codex app-server generate-ts
codex app-server generate-json-schema

# Read any documentation page as raw Markdown
curl -sL https://developers.openai.com/api/docs/guides/agents-api/tools/mcp.md

# Agents API endpoints from the OpenAPI spec
curl -sL https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml -o /tmp/openapi.yaml

# Bundled Codex catalog slugs (11 as of 2026-09-30)
curl -sL https://raw.githubusercontent.com/openai/codex/main/codex-rs/models-manager/models.json \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(len(d["models"]));
[print(m["slug"], m.get("visibility"), m.get("supported_in_api"), m.get("use_responses_lite")) for m in d["models"]]'
grep -nE '^  /(agents|vaults)' /tmp/openapi.yaml
```

## §8 Shelf life  {#s8-validity}

The Codex study reflects `openai/codex` **as of 2026-09-15**, with the App Server protocol
re-counted at HEAD `bcd6d9ab6b` on 2026-09-30 (107 / 10 / 86) and re-checked again the same
afternoon at `92bc601ad6` (**counts unchanged**); the browser study reflects 2026-09-22/23.
Both move fast. **The first move of a re-investigation is not gathering new facts but checking
existing facts for drift.**

### §8.1 What an 8-commit window actually contains  {#s8-1-eight-commit-window}

Re-check `bcd6d9ab6b` → `92bc601ad6`: 8 commits, 134 files, +2462 / −598, all authored on
2026-09-30. **Zero refutations** — nothing previously recorded turned out to be wrong — and two
drifts. Recorded in [`docs/99-sources.md` §E.5](../../../docs/99-sources.md).

The useful shape of that window:

- **One client-visible contract change** in 134 files. `thread/goal/set` and `thread/goal/clear`
  params gained `origin` (`user` | `automatic`). Confirmed in **both** the Rust protocol
  definition and the *generated* Python SDK, which is the check that matters: a field that appears
  only in the hand-written schema has not been proven to be on the wire.
- **One change that reads like a security loosening and is not.** Guardian now skips host
  skill/plugin discovery. The reason is availability — discovery could block Guardian's startup when
  the primary executor is offline — and the regression test disconnects that executor and asserts
  Guardian still **denies** a network permission request. **The gate's availability and its
  correctness are separate axes**; fixing one did not weaken the other.
- **Six commits with no client-visible contract** (TUI ergonomics, thread-store internals, one
  test-isolation fix) — more than half the window. Counting commits would have overstated the
  drift by 3×.

> 📌 **A field named like an authorization flag may not be one.** `origin` reads as a permission,
> and the generated description does say *"Missing provenance does not supply user
> authorization."* But the server only uses it to decide **whether to write a user fragment into
> model history**; `thread_goal_user_context.rs` states the boundary outright — *"tool-created goals
> never use this path."* The set of actors who may change a goal did not widen. **Reading the
> field's role in the branch, not in the name, is what separates drift from a new capability.**

### §8.2 A re-check can fail before it starts  {#s8-2-missing-clone}

The Strands and ACP passes on the same evening hit a failure mode the earlier passes never
recorded, and it is worth keeping because it is cheap to hit and silent if unnoticed.

Both source documents named a **durable local checkout** —
`~/repos/harness-refs/strands-harness-sdk` and `~/repos/harness-refs/agent-client-protocol` as
the thing that had been read. **Neither directory existed.** The Strands document even gave the
origin URL and the `blob:none` detail, so the entry looked verified.

What made it catchable was a step that is easy to skip: *read the provenance line before trusting
the read.* Both re-checks were then done against temporary clones, and both documents were
corrected to say the durable path is absent and must be recreated.

- `strands-agents/sdk-python` `a9a62d4e` → **`4dfeca8c`**, 2 commits. The decisive test was
  negative and cheap: `git diff --name-only … | grep -iE "approval|permission|consent|cedar|sandbox|intervention|harness"`
  returned **nothing**, so the approval, Cedar fail-open, sandbox-`host` and registration-order
  findings stand without re-running the probes. Two windows, same conclusion.
- `agentclientprotocol/agent-client-protocol` `9b26a3ea` → **`c81fae79`**, 7 commits,
  +6791 / −359. **`schema/v1/schema.json` is byte-identical.** The project's own CHANGELOG marks
  all three additions `*(unstable)*`, which is the mechanism: **the spec can take a large unstable
  step without the stable wire moving at all.** A count of changed files would have read as a
  large protocol change; the stable schema says otherwise.

> 📌 **Read the CHANGELOG before reading the diff.** "All three entries are unstable" is one line
> and it reclassifies a 6,791-line diff from *drift in the contract* to *drift in the draft*.
> And when a large unstable change lands near an approval primitive — here MCP-over-ACP became
> request-scoped — **record it as an open question, not as a null result.** The unchanged stable
> schema does not license the claim that the two do not interact; that would be an absence of
> evidence read as evidence of absence, which is this repository's most repeated failure.

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

## §9.5 Observation — designs committed beside code, and a third `llms.txt` variant  {#s9-5-strands}

**A new grade, 📐 designed-only** ([`strands/99`](../../../strands/99-sources.md) §1). Strands commits 20 design
documents next to its code. 11 of the 13 marked "Proposed" are implemented — and the implementations
deviate from the designs where it matters (approval precedence, Cedar fail-closed, stateful history).
A design is intent; grade it as intent, and never let its status line stand in for grep.

**The `llms.txt` record gains a variant.** `strandsagents.com/llms.txt` ✅ — but raw pages live at
`<page>/index.md`; a constructed `<page>.md` 404s. Follow the links the index gives.

**Recomputing a vendor chart from its own data** refuted a headline ("equal or better accuracy": lower
in 7 of 19 same-model pairs) without refuting a ranking — no variance was reported, so sub-point gaps
say nothing either way.

These three now also stand in [`REPORT.md`](../../../REPORT.md) § Method and § A third case (and the
Korean edition), so the report and this page rest on the same record (G4).

**REPORT 2026-09-30** (TASK-012). The Codex report now carries the client study: § The client side,
rec. 11 (wrappers leave wrapped-agent approval on), 18 wiki concepts, and the ACP artifact-vs-wire
rule in § Method. Korean edition in lockstep. Windows internals and the Agents API server-side
model list, previously left open in that Method paragraph, are marked settled. The visual layer of
`agent-ux/` remains ⚠️.

**Strands Anthropic `redacted_thinking` 2026-09-30** (TASK-013). Python
`_format_request_message_content` raises `KeyError: 'reasoningText'` on a redacted-only block;
`format_chunk` drops stream `data`. TS keeps both directions. Probed by executing those two methods
from `anthropic.py` @ `a9a62d4e` with no live key. See [[concepts/retained-reasoning]] §5.5.

**Drift re-check 2026-09-30** ([`strands/99`](../../../strands/99-sources.md) §6). HEAD `a9a62d4e`,
31 commits past the study pin, no new version tags. Cedar / interventions / sandbox / `create_harness`
defaults are byte-identical, so P1–P5 were not re-run — empty diff is the skip condition, not "looks
the same." R1–R18 and R20 stand. R19's README sentence ("No designs have been accepted yet") was
deleted in #4696; the two designs still declare Accepted. #4447 is a squash (`4095cf5a`, one parent);
the prior harness tree is not in this history.

**TS SDK re-read 2026-09-30** (TASK-010). `AgentStreamEvent` union and `modelState` write-back
confirmed from `strands-ts` source ([`strands/02`](../../../strands/02-agent-loop.md) §3.2, §4.2).
Stateful Responses formatter resends the full invocation `input` with `previous_response_id`; the
API outcome is still unverified.

**ACP engine-side 2026-09-30** (TASK-011). Spec @ `9b26a3ea`, stable `protocolVersion` 1, permission
method `session/request_permission`, four `PermissionOptionKind` values. Strands harness ACP path
has no such call (source ✅). Live client ⚠️. See [[concepts/agent-client-protocol]].

## §10 Read next  {#s10-next}

- [[concepts/os-sandbox-policy]] §6 — where the inferred grade is actually applied
- [[concepts/thread-turn-item]] §3 — where a refutation is actually applied
- [[concepts/credential-shielding]] §4 — where the inheritance trap was actually avoided
- Originals: [`docs/99-sources.md`](../../../docs/99-sources.md), [`browser-agents/99-sources.md`](../../../browser-agents/99-sources.md)
- Strands case: [`strands/99-sources.md`](../../../strands/99-sources.md)
- ACP: [[concepts/agent-client-protocol]], [`agent-ux/10-acp.md`](../../../agent-ux/10-acp.md)
