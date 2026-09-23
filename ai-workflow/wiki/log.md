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

