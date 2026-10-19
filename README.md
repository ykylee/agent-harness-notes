# Codex Harness — Study Notes

Notes on OpenAI's **Codex harness** (the execution engine behind the Codex agent) and the API
surfaces built on top of it, compiled from primary sources: official blog posts, official docs,
and the generated schemas in the [`openai/codex`](https://github.com/openai/codex) repository.

Research date: 2026-09-14 (Agents API deep dive: 2026-09-15); drift-checked through 2026-10-19
Repository: <https://github.com/ykylee/agent-harness-notes>

## Seven subjects and three notes

This repository holds **seven investigations into agent harnesses** — four from the engine side,
one from the client side, and two from *above* them (an operating model, then the platform it was
extracted into) — plus three notes that are not product studies: a harness-search procedure, an
operating prescription, and a method for reading the shipped binaries.

| Study | Subject | Execution surface |
|---|---|---|
| [`docs/`](docs/) + [REPORT.md](REPORT.md) | OpenAI Codex harness | shell · filesystem |
| [`claude-code/`](claude-code/README.md) | Anthropic Claude Code, read as an engine from the Agent SDK's generated types | shell · filesystem, **driven over stream-json by twelve clients** |
| [`browser-agents/`](browser-agents/README.md) | Browser-type agents (Aside, Comet, Dia, Neon, Browser Use) | browser · OS |
| [`strands/`](strands/README.md) | Strands Agents SDK and Strands harness (AWS) — an embeddable library | shell · filesystem, **linked into the caller's process** |
| [`agent-ux/`](agent-ux/README.md) | UX/UI of ten agent clients (Claude, ChatGPT/Codex, Cursor, Antigravity, Devin/Windsurf, Orca, Superset, Paseo, Conductor, Aside) | the **client** — how harness primitives are shown to people |
| [`gas-town/`](gas-town/01-vocabulary.md) | Gas Town — one operating model for **orchestrating many harness instances** | the **fleet** — named roles, a town tree, a ledger |
| [`gas-city/`](gas-city/01-vocabulary.md) | Gas City — the platform that model was extracted into | the **fleet** — roles as pack config, formula graphs driven outside the model session |

**→ [SYNTHESIS.md](SYNTHESIS.md)** crosses them: which design axes are surface-independent
(approval, permissions, providers, control/execution plane) and which are surface-specific
(perception, prompt injection, credential shielding). It also records where the two studies
**meet in code** — Aside's daemon registers `openai-codex` as a model provider and implements
Codex's `responses_lite` request-shape branching. Strands, the third case, tests the abstraction on
a different axis — no wire between caller and loop — and found that an approval gate outside the loop
is necessary but not sufficient (SYNTHESIS §2.7). The fifth study sits one level *above* all of
them: it tests whether those axes survive at fleet cardinality, and contributes the sharpest form
of the control/execution split — **the plane boundary has to be drawn around credentials, not just
files**, because a worker that can write its own result ledger can forge its own work
([`gas-town/04`](gas-town/04-orchestration-techniques.md) Part B). Gas City, read at `3ef7fadd42`,
does not replace that finding: its city-write grants authorize config mutations, not result-ledger
writes, and its ACP session provider leaves `session/request_permission` unanswered
([`gas-city/04`](gas-city/04-orchestration-techniques.md) Part B).

A separate note, not a sixth study: [`rrsi/`](rrsi/README.md) reads Google Cloud AI Research's
RRSI, a search that edits a harness while the model stays frozen
(`google-research/rrsi` @ `be50316e1d`). The published benchmark table is the authors' report
and is not adopted.

Another note, also not a product study: [`ai-sdlc/`](ai-sdlc/README.md) reads Anthropic's
"The AI-native SDLC playbook" (Louis Claxton, 2026-08-21) as an operating prescription for
Claude Code. The plays were not run. The page's time-to-intent targets are not adopted.

A third note, about **method**: [`harness-artifacts/`](harness-artifacts/README.md) reads the
shipped binaries of six harnesses (Claude Code CLI 2.1.303, Codex 0.159.3, opencode 1.17.12,
Gemini CLI 0.42.0, Claude Desktop 2.42304.2, ChatGPT 26.1013.40934) with REA 6.7.0 as the
instrument — Bun single-file layouts, Electron fuses and windows, the desktop UI composition
recovered from chunk names, a drift pass on the two desktop studies, and a cross-reference of how
each harness defines, invokes and truncates **tools**. Nothing was executed.

Concept-level index: [`ai-workflow/wiki/index.md`](ai-workflow/wiki/index.md) (19 concepts).

## Start with the report

**[REPORT.md](REPORT.md)** — the findings, the requirement assessment, the verification record, and
the recommendations they support. Korean edition: **[REPORT.ko.md](REPORT.ko.md)**.

Web versions: [English](https://claude.ai/artifact/6J9zrjCvZQcfDXcKvgUsxo) ·
[한국어](https://claude.ai/artifact/NC1DXYvqdUp1J1sSeKH9bh)

## In one line

> A "harness" is the **execution system** that sits between a model and a task. OpenAI opened
> this execution system in three layers: (1) an open-source binary and protocol (App Server),
> (2) per-language SDKs, and (3) a managed API (Agents API).

## Release timeline

| Date | What | Significance |
|---|---|---|
| 2026-02-04 | [Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/) (Celia Chen) | App Server architecture and protocol design published |
| 2026-02-11 | [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (Ryan Lopopolo) | Introduces "harness engineering" as a discipline |
| 2026-08-19 | [Codex as a platform: build on the open agent harness](https://developers.openai.com/blog/codex-as-a-platform) | CLI · app-server · SDK officially positioned as an **open agent harness** (Apache-2.0) |
| 2026-09-10 | [Agents API public beta](https://developers.openai.com/api/docs/guides/agents-api/overview) | The same harness offered as a managed API **hosted by OpenAI** |

## Contents

| Document | Topic |
|---|---|
| [01-overview.md](docs/01-overview.md) | What a harness is, its internal components, the 3-layer open structure |
| [02-app-server-protocol.md](docs/02-app-server-protocol.md) | **Core.** The full App Server JSON-RPC protocol — transports, handshake, 107 stable + 63 experimental client methods, 85 notifications, approval flow (108 / 67 at `b1fd48c48`, 2026-10-19) |