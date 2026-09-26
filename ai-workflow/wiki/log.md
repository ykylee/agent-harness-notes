---
type: meta
status: active
r9_skip: true
title: Wiki Ingest/Query Log
related_pages: [index]
last_touched: 2026-09-22
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
