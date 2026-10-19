<!-- standard-ai-workflow-kit: v1.10.0 -->

# Project Workflow Profile

- Purpose: define project-specific rules and the execution/validation criteria.
- Scope: project overview, document layout, standard commands, validation points, policy exceptions
- Audience: developers, operators, AI agents, anyone onboarding
- Status: draft
- Updated: 2026-10-19 (nine study folders, 19 concepts, drift baselines; was 2026-09-23)
- Related: [PURPOSE](../ai-workflow/memory/active/PURPOSE.md), [SYNTHESIS](../SYNTHESIS.md)

## 1. Project overview
- 프로젝트명: Codex Harness — Study Notes
- Purpose: investigate agent harnesses against primary sources and record the findings. Codex is the
  first case; browser-type agents, an embeddable SDK (Strands), ten clients and ACP, two
  orchestration layers (Gas Town, Gas City) followed; three notes (RRSI, the AI-native SDLC playbook,
  the shipped artifacts read with REA) sit beside them. `SYNTHESIS.md` crosses all of it.
- Stakeholders: ykylee (sole researcher and maintainer)
- Nature: **a research repository with no code.** The deliverables are the Markdown documents under
  the nine study folders, plus `REPORT.md` / `REPORT.ko.md` and `SYNTHESIS.md`. There is no build, no
  deploy, no runtime. "Testing" here therefore means **re-verifying sources**, not running anything.
  Measurements come in from the separate implementation repository (`ykylee/heddle`) as results only
  (`PURPOSE.md` §0.1); shipped binaries are read as bytes, never executed (`PURPOSE.md` §0.7).

## 2. Document layout
- 문서 위키 홈: `README.md` · Codex study: `docs/` (16 documents + `99-sources.md`)
- Claude Code as an engine: `claude-code/` (3 documents + `99-sources.md`)
- Browser-agent study: `browser-agents/` (13 documents) · Strands: `strands/` (8) · clients and ACP:
  `agent-ux/` (11) · orchestration: `gas-town/` (5), `gas-city/` (5) · notes: `rrsi/` (4),
  `ai-sdlc/` (4), `harness-artifacts/` (4) — each folder has a `README.md` and a `99-sources.md`
- Cross-study synthesis: `SYNTHESIS.md`
- Reports: `REPORT.md` (English), `REPORT.ko.md` (Korean); web versions linked from `README.md`
- Source and verification records: every `99-sources.md`; drift ledgers in `docs/99` §E and
  `strands/99` §6
- Concept re-index: `ai-workflow/wiki/` (19 concepts)
- Reference checkouts (outside this repo): `~/repos/harness-refs/{codex,strands-harness-sdk,
  agent-client-protocol,gascity,rrsi,beads}` — pinned commits are recorded in each `99-sources.md`
- 환경 기록 위치: `ai-workflow/memory/active/repository_assessment.md`
- 운영 문서 위치: `ai-workflow/memory/active/`
- 백로그 위치: `ai-workflow/memory/active/<branch>/backlog/`
- 세션 인계 문서 위치: `ai-workflow/memory/active/<branch>/session_handoff.md`

## 3. Standard commands
- Install: none — a Markdown repository with no dependencies
- Run locally: none — there is nothing to run
- 빠른 테스트: `python3 scripts/check_wiki_freshness.py --show-uncovered` — checks that the concept
  re-index has kept up with its source documents
- 격리 테스트: `grep -rn "](" docs/ browser-agents/ strands/ agent-ux/ gas-town/ gas-city/ rrsi/ ai-sdlc/ harness-artifacts/ README.md SYNTHESIS.md`
  to eyeball broken relative links (a Python walk that resolves each target is what the sessions
  actually run)
- Smoke check: re-fetch a primary source. Appending `.md` to an OpenAI (and many other) documentation
  URL returns the raw Markdown; `/llms.txt` is often a full index.

## 4. Validation points
- Code changes: none
- Document changes:
  - **One claim, one source.** Do not add a sentence that has no grounding.
  - A secondary-source claim is not written as settled until it has been checked against a primary
    artifact — generated schemas, source, or a binary.
  - Anything filled in by inference is **labelled as inference** in the document itself.
  - When a fact changes, update the matching verification table in the same commit.
  - Editing an English document means updating the matching part of `REPORT.ko.md` in the same commit.
  - **Editing a document under `docs/` or `browser-agents/` means re-ingesting the wiki concept pages
    that cite it.** The mapping lives in each concept page's `last_ingested_from`; the check is
    `scripts/check_wiki_freshness.py`. Enforcement points are in §5.
- UI changes: none
- Deploy/ops: none — changes are committed directly to the working branch

## 5. Enforcing wiki re-ingest

`ai-workflow/wiki/` is a re-index of the study folders (`docs/`, `browser-agents/`, `strands/`,
`agent-ux/`, `gas-town/`, `gas-city/`, `ai-sdlc/`, `harness-artifacts/`, `rrsi/`, `claude-code/`, and `SYNTHESIS.md`). If a source document changes and
the re-index does not follow, the wiki goes quietly stale. The mapping exists in exactly one place —
each concept page's `last_ingested_from` — and is read at three points.

| Point | What it does | Kind |
|---|---|---|
| `git commit` (`.githooks/pre-commit`) | **Blocks the commit** if a staged source document's concept pages are not staged with it | **Blocking** |
| Claude Code `PostToolUse` (`.claude/settings.json`) | Tells the agent which pages need re-ingest right after an edit | Advisory (does not block the edit) |
| Manual / session close | `python3 scripts/check_wiki_freshness.py` — full audit against git history | Audit |

```bash
# Once per clone — git does not version the hooks path
git config core.hooksPath .githooks

# Full audit, plus documents no concept page covers
python3 scripts/check_wiki_freshness.py --show-uncovered
```

Bypass: `git commit --no-verify`, for edits that change no facts (typos, formatting) or when the
re-ingest is deliberately deferred. Use it only when that intent is clear.

Limitation: the pre-commit hook only runs in a clone that has set `core.hooksPath`. This repository
is maintained by one person, so there is no server-side enforcement — if that changes, move the
default-mode check into CI.

## 6. Policy exceptions
- Merging: single-maintainer repository, so state-document conflicts do not arise. If one does,
  `backlog/tasks/` is the source of truth.
- Approval: a change that **overturns an existing conclusion** (settled → refuted, and so on) is
  confirmed with the user first.
- Constraints:
  - The Codex study reflects `openai/codex` as of 2026-09-15, drift-checked to `e72da2b538` on
    2026-09-26 (`docs/99-sources.md` §E), with a 2026-09-30 follow-up at HEAD `bcd6d9ab6b`
    (generated schema 107 / 10 / 86; Agents roster three surfaces; Windows internals source-read);
    the browser-agent study reflects
    2026-09-22/23; the Strands study reflects `strands-agents/harness-sdk` @ `15da9dc` (2026-09-25); the agent-client UX
    study reflects builds downloaded on 2026-09-26 (two products were renamed or merged that year). Both move fast. The first move of any re-investigation is checking the existing
    facts for drift, not collecting new ones.
  - **Current drift baselines (2026-10-19):** Codex `b1fd48c48` (generated schema 108 / 10 / 87;
    `docs/99` §E.6), Strands `bd0b6a94` (`strands/99` §6.2), Beads `4f9174e6b` (`gas-city/99` §C),
    Gas City `3ef7fadd42`, ACP spec `9b26a3ea`. Desktop builds read: Claude Desktop 2.42304.2 and
    ChatGPT 26.1013.40934 (Linux debs), legacy ChatGPT macOS 1.2026.183. Shipped CLIs read: Claude
    Code 2.1.303, Codex 0.159.3 / 0.163.0, opencode 1.17.12, Gemini CLI 0.42.0.
  - **The artifact method's host matrix matters.** REA 6.7.0 on this Linux host has no Hopper, Ghidra,
    IDA or pwntools; native and Apple analyses are ⚠️ until run on a host that has them
    (`harness-artifacts/README.md`).
  - Dates diverge between primary sources because of time zones. Record publication dates in UTC and
    add a conversion table where it matters.
- **Language: document bodies are English. Commit messages and operational documents
  (`session_handoff.md`, backlog tasks) are Korean.** This includes `docs/`, `browser-agents/`,
  `SYNTHESIS.md`, the wiki concept pages, this profile, and `PURPOSE.md`. Settled 2026-09-23;
  the browser-agent study was drafted in Korean and translated, the same path the Codex study took.
- **Exception — machine-read labels stay Korean.** `wk` parses this profile and `PURPOSE.md` by
  hard-coded Korean labels (`프로젝트명`, `문서 위키 홈`, `운영 문서 위치`, `백로그 위치`,
  `세션 인계 문서 위치`, `환경 기록 위치`, `빠른 테스트`, `격리 테스트`, and `### 포함 영역` /
  `### 제외 영역` in PURPOSE §3). Translating those labels **silently disables scope-creep
  detection**, which matches task briefs against the excluded areas. The label stays Korean; the
  value stays English.

## Read next
- [Session handoff](../ai-workflow/memory/active/main/session_handoff.md)
- [Backlog](../ai-workflow/memory/active/main/backlog/)
- [Source and verification record](99-sources.md)
- [Cross-study synthesis](../SYNTHESIS.md)
