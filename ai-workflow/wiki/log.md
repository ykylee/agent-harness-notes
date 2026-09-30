---
type: meta
status: active
r9_skip: true
title: Wiki Ingest/Query Log
related_pages: [index]
last_touched: 2026-09-30
created: 2026-09-22
---

<!-- standard-ai-workflow-kit: v1.10.0 -->

# Wiki Ingest/Query Log

> Format in [`./SCHEMA.md`](./SCHEMA.md) §2. An entry is appended per ingest or query.

## [2026-09-22] ingest | bootstrap + 13 concepts (extracted from the existing 16 documents)

Sources: `docs/01`–`docs/16`, `docs/99-sources.md`, `REPORT.md` (all previously committed documents; no new research)

Pages updated (13):
`concepts/harness`, `concepts/harness-engineering`, `concepts/thread-turn-item`,
`concepts/approval-gate`, `concepts/wire-protocol-boundary`,
`concepts/stateless-conversation-wire`, `concepts/retained-reasoning`,
`concepts/control-plane-execution-plane`, `concepts/execution-environment-topology`,
`concepts/os-sandbox-policy`, `concepts/capability-distribution`,
`concepts/provider-as-data`, `concepts/primary-source-verification`

Notes:
- The wiki is **a re-index of `docs/`, not a replacement.** The documents are ordered by source
  (App Server / Agents API / adapter); the wiki is ordered **by concept.** The source of truth for
  facts stays in `docs/`.
- Each page's `last_ingested_from` points at its source documents. When a source changes, that page
  is re-ingested.
- Zero `[CONTRADICTION]` tags. A refuted secondary source is not a contradiction but **a settled
  verdict**, preserved with its grade in `concepts/primary-source-verification` §4.
- The Windows sandbox internals carry an **inference grade** in the page body, as in the original —
  carrying grades across without losing them was this ingest's constraint.

## [2026-09-23] ingest | fusing two studies — 8 enriched, 3 new

Sources: the 11 documents of `browser-agents/` (the browser-agent study, branch `study/browser-agents`)

**Enriched (8)**: `control-plane-execution-plane` (planning location splits three ways) ·
`wire-protocol-boundary` (Aside implements `CODEX_TOOL_CALL_PROVIDERS`) ·
`primary-source-verification` (the technique's record and two traps) ·
`approval-gate` (channel-rendered approval) · `provider-as-data` (two cases pointing opposite ways) ·
`capability-distribution` (three orthogonal axes of reuse) ·
`harness` (three shells, **the surface-specific/independent split**) ·
`os-sandbox-policy` (policy expressiveness, Computer Use)

**New (3)**: `perception-model` · `indirect-prompt-injection` · `credential-shielding`
— all axes that emerged only from the browser study. Codex is a coding harness, so page perception
was never a problem it had.

Notes:
- With this ingest the wiki **covers both studies**, which was itself a change in the repository's
  character. The scope extension is recorded in the shared `PURPOSE.md` §0 — option A's condition in
  `browser-agents/SCOPE.md` firing.
- Adding `browser-agents/*` to each concept page's `last_ingested_from` means **the re-ingest
  enforcement hook automatically covers both trees.** No new machinery was needed.
- Zero `[CONTRADICTION]` tags. The two studies' conclusions nowhere collide; instead they **meet at
  the level of source** in `wire-protocol-boundary`.
- A cross-study synthesis, `SYNTHESIS.md`, was added at the root — the wiki is per concept, the
  synthesis is for reading.

## [2026-09-23] ingest | language unified to English

All concept pages, `index.md` and this log translated from Korean to English, together with
`browser-agents/` (14 documents), `SYNTHESIS.md`, `docs/PROJECT_PROFILE.md` and `PURPOSE.md`.

The convention is now recorded in `docs/PROJECT_PROFILE.md` §6: **document bodies are English;
commit messages and operational documents (`session_handoff.md`, backlog tasks) stay Korean.**

Note: the browser study was drafted in Korean and then translated — the same path the Codex study
took. No facts changed in translation; only the language did.


## [2026-09-23] ingest | Brave's demonstration re-read against the original

Re-ingested `browser-agents/07-security.md` §2 (corrected) and §10 (new) into
`indirect-prompt-injection`, and `browser-agents/99-sources.md` §4.5 into
`primary-source-verification`.

The study had paraphrased Brave's Comet chain as ending "send both to the attacker's server."
Brave's fourth step reads "Exfiltrate both the email address and the OTP **by replying to the
original Reddit comment**." Every navigation in the chain went to a legitimate, logged-in origin.

Notes:
- One `[CONTRADICTION]` resolved rather than tagged: `indirect-prompt-injection` §10.1 had set the
  demonstration against the measurement ("the demonstration may be the wrong threat shape"). With
  the original read, **they agree** — neither has an attacker destination. The contradiction was
  between the measurement and this wiki's paraphrase.
- The paraphrase had travelled into the implementation's probe design (navigation to an attacker
  origin). That repository is out of scope here; the note stands so the next probe is built on the
  original four steps.


## [2026-09-26] ingest | Strands — a third case, embedded rather than served

New study `strands/` (8 documents) re-indexed into seven concepts: `harness` §7.7,
`approval-gate` §7.5, `provider-as-data` §6.5, `execution-environment-topology` §6.5,
`indirect-prompt-injection` §10.5, `credential-shielding` §7.4, `primary-source-verification` §9.5.

Notes:
- No existing conclusion was overturned. Two were **qualified**: provider-as-data holds where the
  wire is shared (Strands fixes an internal wire and makes providers code); and "only the gate
  outside the loop held" (SYNTHESIS §6.4) is necessary, not sufficient — Strands has such a gate
  and five other properties of it are missing (SYNTHESIS §2.7).
- A new grade, 📐 designed-only, for design documents committed beside code whose status lines are
  unreliable.
- Probe results (🧪) come from the SDK's own scripted mock model, re-run by the main session with
  controls. No live model was used; every injection path stays ⚠️.


## [2026-09-26] ingest | REPORT carries the Strands case

`REPORT.md` / `REPORT.ko.md` gained § A third case and recommendations 9–10. Re-ingested into
`primary-source-verification` §9.5 — no new fact; the page now points at the report so the two stay
on one record. Two report findings were qualified (rec. 7's gate, provider-as-data), none invalidated.


## [2026-09-26] ingest | agent-ux — the client side of the contract

New study `agent-ux/` (11 documents; ten clients read from shipped installers and source). New concept
`agent-client-design-language` (17 concepts now); `approval-gate` §7.6 added.

Notes:
- Scope recorded in `PURPOSE.md` §0.2 before the work began.
- Two premises in the brief were wrong and are recorded as findings: ChatGPT desktop **is** the Codex
  app; Windsurf is now Devin Desktop and shares an engine with Antigravity down to protobuf field numbers.
- Engine-side conclusions: approval-as-primitive confirmed from the client side (Paseo's four renderers,
  Superset's "approvals are items"); SYNTHESIS §2.7's "on by default" is the property the orchestrators
  lack. Nothing overturned.
- No display: every visual impression is ⚠️.


## [2026-09-30] ingest | App Server protocol re-count (TASK-002)

Sources: `docs/02-app-server-protocol.md`, `docs/99-sources.md`, `docs/12-product-surface.md`,
`docs/06-choosing.md`, `REPORT.md` — `openai/codex` HEAD `bcd6d9ab6b` (2026-09-30).

Pages updated (7):
`concepts/thread-turn-item`, `concepts/approval-gate`, `concepts/os-sandbox-policy`,
`concepts/harness`, `concepts/primary-source-verification`, `concepts/capability-distribution`,
`concepts/retained-reasoning`

Notes:
- Counts: `ClientRequest` 104 → **107**, `ServerRequest` **10** (unchanged), `ServerNotification`
  84 → **86**. Additive: `account/gatewayOAuth/read|login|cancel` + `account/gatewayOAuth/changed`
  (`064e701b0f`); `thread/prediction/updated` (`90abcfac02`). `thread/prediction/request` is
  unimplemented (method-not-found) and absent from `ClientRequest`.
- Approval gate: the generated 10 `ServerRequest` methods are unchanged. Three names in the
  shipped ChatGPT/Codex client (`item/tool/requestOptionPicker`, `item/plan/requestImplementation`,
  `thread/startAeon`) are absent from the generated schema and from public `app-server.md` —
  client-bundle-only, recorded in `docs/02` §7.1. No existing conclusion overturned.
- `os-sandbox-policy` protocol values and `capability-distribution` plugin RPCs are unchanged.
  `retained-reasoning` facts are unchanged (date bump only, because `docs/99-sources.md` moved).


## [2026-09-30] ingest | Agents API model roster (TASK-003)

Sources: `docs/99-sources.md`, `docs/08-agents-api-reference.md`, `docs/05-agents-api.md`,
`docs/15-model-providers.md`, `docs/16-responses-chat-adapter.md` — OpenAPI `openapi.yaml`
(2026-09-30), Agents API guides, `models.json` @ `b1e72963c3`.

Pages updated (7):
`concepts/primary-source-verification`, `concepts/wire-protocol-boundary`,
`concepts/provider-as-data`, `concepts/stateless-conversation-wire`,
`concepts/control-plane-execution-plane`, `concepts/execution-environment-topology`,
`concepts/retained-reasoning`

Notes:
- Agents API `model` is an unconstrained string. Bundled Codex catalog is **11** entries (was 9),
  all `supported_in_api: true`. Platform `ModelIdsShared` is a 89-value Chat/Responses enum.
  Three surfaces, not one list. `gpt-5.4` left the bundled catalog 2026-09-24; `gpt-6.1-sol` /
  `gpt-6-sol` / `gpt-6-luna` were added. Classic-shape catalog slug remaining: `gpt-5.5`.
- Live Agents session create was not exercised (no API key).
- `approval-gate` facts unchanged (`docs/05` only gained a model-roster sentence).

## [2026-09-30] ingest | Windows sandbox internals source-read (TASK-004)

Sources: `docs/14-windows-sandbox.md`, `docs/99-sources.md`, `REPORT.md` — `openai/codex`
HEAD `bcd6d9ab6b` (2026-09-30), `codex-rs/windows-sandbox-rs` and `windows-sandbox-service`.

Pages updated (3):
`concepts/os-sandbox-policy`, `concepts/primary-source-verification`,
`concepts/retained-reasoning`

Notes:
- Module-name inference for ACL / WFP / token / desktop is now **source-read**. Token:
  `CreateRestrictedToken` (`DISABLE_MAX_PRIVILEGE | LUA_TOKEN | WRITE_RESTRICTED`). ACL:
  `SetNamedSecurityInfoW` deny ACEs. Network: 12 persistent WFP `FWP_ACTION_BLOCK` filters plus
  `INetFwPolicy2` offline-user rules. Desktop: `CreateDesktopW` `CodexSandboxDesktop-*`.
- Corrections to the earlier map: `hide_users.rs` is Winlogon login-UI hiding, not desktop
  isolation. There is no `audit.rs` (logging is `logging.rs`). Elevated network is WFP **and**
  Windows Firewall, not WFP alone.
- Runtime on Windows was not exercised (this host is Linux). Official
  `learn.chatgpt.com/docs/windows/windows-sandbox.md` still 200.
- `retained-reasoning` facts are unchanged (date bump only, because `docs/99-sources.md` moved).

## [2026-09-30] ingest | Agents `./` vs Codex `onboardingSkill` (TASK-005)

Sources: `docs/10-agents-api-tools.md`, `docs/13-marketplace-and-plugins.md`, `docs/99-sources.md`
— live `developers.openai.com/api/docs/guides/agents-api/tools/plugins.md` and
`openai/codex` HEAD `bcd6d9ab6b` `codex-rs/core-plugins/src/manifest.rs`.

Pages updated (3):
`concepts/capability-distribution`, `concepts/primary-source-verification`,
`concepts/retained-reasoning`

Notes:
- Agents API packaging still requires paths to start with `./`. Live `plugins.md` example
  declares `skills` / `mcpServers` only; no `onboardingSkill`.
- Codex overlay exception is `resolve_openai_onboarding_skill`: prepend `./` when missing,
  then the shared resolver still rejects `..` and empty `./` (#46544).
- Wiki §6 (Agents load path) no longer carries the Codex exception; it lives in §2.1.
- `retained-reasoning` facts are unchanged (date bump only, because `docs/99-sources.md` moved).

## [2026-09-30] ingest | GitHub-origin harness-refs checkout (TASK-006)

Sources: `docs/99-sources.md` — this Linux host had no `~/repos/harness-refs/codex`.
Created `git clone --filter=blob:none https://github.com/openai/codex.git` there.
At creation HEAD `d42056091a` (one TUI commit past the 09-30 recheck `bcd6d9ab6b`).

Pages updated (2):
`concepts/primary-source-verification`, `concepts/retained-reasoning`

Notes:
- origin is `https://github.com/openai/codex.git`. A personal Gitea mirror as origin lags.
- `retained-reasoning` facts are unchanged (date bump only).
