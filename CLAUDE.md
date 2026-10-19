<!-- standard-ai-workflow-kit: v1.21.0 -->
<!-- standard-ai-workflow-kit-overlay: plugin-only — 워크플로우 스킬은 플러그인 채널(standard-ai-workflow 1.21.0)로만 소비한다. .claude/commands·skills 의 프로젝트 overlay 사본은 두지 않는다. 두 채널이 같은 스킬을 이중 노출해 정리 (TASK-2026-09-30-main-001) -->

# CLAUDE.md (Claude Code entry point)

- Purpose: the *directional intent* of the standard AI workflow, plus the entry rules Claude Code needs every session
- Scope: session restore, the order to consult workflow state docs, working principles, session close order
- Audience: Claude Code, repository maintainer, workflow designer
- Status: beta
- Last updated: 2026-10-19
- Related: `ai-workflow/memory/active/<branch>/state.json`, `docs/PROJECT_PROFILE.md`

## Read these first

- Restore the session with `python -m workflow_kit session-start` — it reads `ai-workflow/memory/active/<branch>/` (`state.json`, handoff, backlog), `docs/PROJECT_PROFILE.md`, and `PURPOSE.md` (`<branch>` = current git branch).
- `ai-workflow/` is the workflow meta layer — keep it out of code and document searches; open it only to restore or update workflow state.
- `ai-workflow/wiki/index.md` — R4 anchor based; load this first when an AI agent queries project concepts (project-specific pointer, kept outside the generated blocks).
- Relationship to AGENTS.md: Claude Code does not read `AGENTS.md` — if the project has one, add a single `@AGENTS.md` line to this file.
- Missing `state.json` / `PURPOSE.md` is not a failure — session-start skips them and offers to scaffold.

## Plugin skills (standard-ai-workflow 1.21.0)

Project-local `.claude/commands` / `.claude/skills` copies are not kept. Use the plugin skills:

- `session-start` — restore the `state.json` + `session_handoff.md` + `backlog` baseline
- `backlog-update` — register/update a task + scope-creep warning
- `doc-sync` — sync affected documents (advisory)
- `session-end` — update handoff + backlog and regenerate `state.json` at session close
- `compact-relay` — record verified / unverified facts and the next step before a context compaction

## Working Principles

<!-- generated-from: core/global_workflow_standard.md §1 · §3 · §8 · §11 — do not edit this block directly; edit the standard document and regenerate. -->

- Read the state summary documents first, every session.
- Before starting work, state its purpose, scope, deliverables, and affected documents, and record the plan in the task file (files, order of work, risks, proof).
- Track work in the state documents with exactly one status: `planned`, `in_progress`, `blocked`, `done`.
- Never mark an unverified result as done.
- Before ending a session, leave a state summary the next session can resume from.
- With multiple agents: sync with the remote first, check what the others are doing, and pick work that does not overlap.
- Never decide irreversible actions alone — deleting or overwriting another agent's work needs the user's confirmation.
- Keep the shared standard thin; project-specific differences go in the project profile.

## Session Close Order

Close a session in the order **update memory → commit → push** — the memory update rides in the pushed commit, never in a later turn.

- Update before closing: `state.json`, `session_handoff.md`, the latest backlog

## Memory Update Paths

- Restore session-start baseline: `python -m workflow_kit session-start`
- Register / update a task: `python -m workflow_kit backlog-update`
- Sync affected documents (advisory): `python -m workflow_kit doc-sync`
- Regenerate state.json at session close: `python -m workflow_kit refresh-state`
- Roll off handoff §1 baselines over cap: `python -m workflow_kit rollover-baselines`
- Roll off handoff §5 notes over budget: `python -m workflow_kit rollover-handoff-notes`
- Propose memory_index entries at close (advisory): `python -m workflow_kit suggest-memory-entries`
- Relay working state across compaction: `python -m workflow_kit compact-checkpoint`

- Run them with the Python that has `workflow_kit` installed (`python` on Windows, usually `python3` elsewhere) — not a `wk` executable, which Windows antivirus blocks.
- Empty handoff `in_progress` / `blocked` lists hold an **empty bullet `-`** — prose there is parsed as a work item.
- Handoff recently-completed entries start with `TASK-`, at most 10.
- `state.json` is a **generated artifact** — never hand-edit it; regenerate with `refresh-state` (sources: `backlog/tasks/` + `session_handoff.md`).
- Over the handoff §1 baseline cap, **move** lines with `rollover-baselines` — never delete them.
- Over the handoff §5 notes budget, **move** the oldest with `rollover-handoff-notes` (rules → `lessons.md`, notes → `sessions/`).
- Write the handoff and backlog only in their format — they feed the state.json generator.

## Language and context principles

- Write user-facing reports, summaries, and document updates in Korean; keep code, commands, paths, and product names verbatim.
- Give the user the conclusion and the next action — skip long intermediate reasoning and repeated summaries.
- Keep only the facts the next session needs in the handoff and backlog.

## self-bootstrap (when PURPOSE.md / state.json are absent)

When `state.json` or `PURPOSE.md` is absent, the session-start skill *skips gracefully*.
When the user invokes `session-start` (or on automatic read), it attempts a
*minimum-effort* baseline restore:

1. `ai-workflow/memory/active/<branch>/state.json` missing → offer to scaffold it
2. `PURPOSE.md` missing → 4-element placeholder + suggest a light `init` call
3. `work_backlog.md` missing → empty index + guidance for registering the first task

## Project run defaults

These commands come from `docs/PROJECT_PROFILE.md` §3. This is a Markdown research
repository: there is no install, no local run, and no runtime.

- **install**: none
- **run**: none
- **quick test**: `python3 scripts/check_wiki_freshness.py --show-uncovered`
- **isolated test**: `grep -rn "](" docs/ browser-agents/ README.md SYNTHESIS.md`
- **smoke check**: re-fetch a primary source (append `.md` to an OpenAI docs URL; `/llms.txt` is often a full index)

## Read next

- `ai-workflow/README.md` (kit overview)
- `docs/PROJECT_PROFILE.md` (project metadata)
- `ai-workflow/memory/active/<branch>/sessions` (current session handoff)
- `ai-workflow/memory/active/PURPOSE.md` (directional intent)
