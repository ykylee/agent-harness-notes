# 01. The loop

The page's thesis, graded as a reading of the page. Productivity outcomes attached to it are 📣.

## The bottleneck moves

Code generation got faster. Plan, review and test, and deploy still run at human speed. Controls
were built on the assumption that a person wrote every line. Exceptions still wait for a committee
that meets weekly. A security team sized for human output then either queues or ships
under-reviewed. The page's answer is to keep the old control objectives and replace the
enforcement: the lifecycle becomes a loop, with an agent at each point and an automated handover
between points. "Agentic SDLC", "AI SDLC", and "agentic software development" are the same thing
on this page. People stay accountable for judgment. Their attention moves to the artifacts that
have to be reviewed. Most organizations, the page says, sit between the two columns below.

## Six stages

| Stage | Traditional, as the page states it | AI-native, as the page states it |
|---|---|---|
| Plan | Requirements gathered in workshops and written by hand | Claude synthesizes sources into `intent.md` |
| Design | Analysts, then designers | One session, guided by skills, versioned in git. Front-end example: a product owner mocks in Claude Design (beta) from `intent.md` and exports to Claude Code |
| Build | Handwritten tests and code; docs after | AI-written tests and code; knowledge in a versioned `CLAUDE.md` and in skills |
| Test | QA gates at stage boundaries | Continuous evals through implementation |
| Deploy | People read every line; governance cycles are inconsistent | Layered agent review; human review kept for regulated and critical code; hooks gate the agent while it acts |
| Maintain | People watch production | Agents monitor. A breached band is diagnosed and written back as a new `intent.md` |

Claude Design, Claude Tag, Claude Security, and the managed Code Review service are product names
on the page (2026-08-21). They are recorded as the packaging the plays use. They are not tracked
past that date.

## The artifact chain

Each stage ends by committing something the next stage reads. Early stages are markdown because a
product owner and an agent can both read them. From Build onward the artifact is code and its
records. The page treats the commit chain as the audit trail: who asked, what the agent produced,
who approved.

| Stage | Artifact | What it holds |
|---|---|---|
| Plan | `intent.md` | What is wanted, why, and the constraints. Author and timestamp come from git |
| Design | `spec.md`, next to the intent | The pair records what was asked and what was decided |
| Build | `plan.md`, then the diff and its tests | Files, order, risks, and the proof. If implementation departs, `plan.md` is updated in the same commit. A hook may require that sync |
| Test | Toolchain evidence | `make test` output, a build log, or a screenshot diff, in the session transcript, the OpenTelemetry export, or the PR check run |
| Deploy | The PR and `REVIEW.md` findings | Findings do not themselves approve or block. Branch protection still requires a code owner |
| Maintain | A new `intent.md` | Diagnosis of a breach, in the same shape as a Plan intent |

Triggers the page names: an accepted intent fires the design pass; an approved spec fires plan
mode; a merged PR fires the pipeline; a breached band writes the next intent. The starting
practice is to prompt each step by hand. The end state is each accepted artifact firing the next
gate, so human attention sits at the gates.

Stage 6's introduction adds one more gate the band table does not spell out: between stages, a
headless run uses an independent confidence check — a deterministic check, or a second agent that
reviews the previous stage — and escalates to a person when that check fails.

## Where the record lives

The page's sidebar applies to every artifact. Name one system as the source of truth.

1. **The repo is authoritative.** The legacy tracker stores a reference to the commit.
2. **The legacy system is authoritative** (Jira, ServiceNow, a requirements tool). Markdown is a working copy. Claude reads the record at session start and writes the outcome back through an MCP connector in the same session.
3. **Linkage is the minimum.** Artifacts note the record id. Legacy records contain the commit SHA.

Two systems may coexist when one is declared authoritative, or when they are linked. The page
presents (3) as a place to start, and it says outright that (3) accepts two sources of truth.

## Order of adoption

The page prints a dependency graph. The image was not read on 2026-10-06, so the order below is
**reconstructed from each play's Prerequisites text**, not transcribed from the arrows. The page's
own caption: stage order and adoption order are different, and a play with nothing pointing into
it can be started on its own.

Nothing named first:

- Capture `intent.md`
- `CLAUDE.md`
- Skills (a `CLAUDE.md` helps; a skill does not depend on it)
- A feedback loop (one command that exits non-zero)
- Hooks as approval gates (a written list of approvals that must survive)

Then, from the text:

| Play | What the text requires first |
|---|---|
| Requirements and design | An `intent.md`, plus brand, security, compliance, and UX policies written as skills |
| Plan mode | The intent or the spec, if one exists. A `CLAUDE.md` helps |
| Auto mode | Described as the follow-on once `CLAUDE.md`, skills, hooks, and a runnable test suite exist. See the doc delta in [`03`](03-the-control-ladder.md) |
| Parallel sessions | A `CLAUDE.md`. The feedback loop helps |
| Continuous evals | A `CLAUDE.md` and the feedback loop |
| PR review | An updated `CLAUDE.md`. Skills and subagents when the passes enforce written policy |
| CI/CD | Claude already in the PR review loop, **and** hooks as approval gates. The page's reason: the gates have to exist before automation accelerates anything through them |
| Closing the loop | The `intent.md` format, accelerated PR reviews, hooks as an action boundary, and a rollback path |
| Recurring scans | The PR review gate and approval hooks. The intent format, for a finding wider than one patch |

Build-time guardrail hooks are a short section under Build, not a play with its own Prerequisites
header. They back a skill whose policy must hold without exception. Claude Tag is described as
another way work enters the same loop. The page does not give it a Prerequisites block.

## What matches an axis already in this repository

[`docs/07`](../docs/07-harness-engineering.md) already records OpenAI's version of the same move:
keep `AGENTS.md` short, as a map; enforce invariants with linters whose errors tell the agent how
to fix the violation; commit plans; run a recurring scan that opens small pull requests. The
playbook is Anthropic's Claude Code instance of that split, with the enforcement named as hooks
and the map named `CLAUDE.md`. The grades for the Claude Code mechanisms are in
[`03`](03-the-control-ladder.md). The plays themselves are in [`02`](02-the-plays.md).
