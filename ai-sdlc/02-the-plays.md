# 02. The plays

Each play on the page has the same shape: what changes, how to start, the steps, who still
decides, and a leading indicator plus a lagging indicator. The indicators are instructions. None
were computed here. Expectations such as "weeks to hours" or "time to first review falls to
minutes" are the page's 📣, not findings.

Worked examples on the page (a claims-status intent, a payments-service `CLAUDE.md`, a
`secure-api-review` skill, a verifier subagent, a `REVIEW.md`, a `bands.yaml`, a production-gate
script, a managed-settings JSON) are illustrations. They are summarized by the fields they carry.
They were not copied in as config, and they were not run.

Acknowledgments on the page: Jim Blackhurst, Will Steuk, Jamal Arif.

## Plan — capture `intent.md`

**Prerequisites:** none.

An idea, a ticket, or an incident (Stage 6) becomes one markdown file. The originator talks to
Claude in their own words. Claude asks for scope, users, constraints, and what success looks like,
then writes `intent.md` from an organizational template. The originator corrects it. The product
owner reviews and corrects an agent-written intent before commit, whether the origin was a person,
a ticket, or an incident.

The home is an `intent/` directory in the product repo when there is one product, a directory in a
monorepo, or a dedicated repo only when intent spans repositories. Contributors who do not use git
commit through a version-control connector from claude.ai or Cowork. Standing the home up, and
deciding who may write to it, is a one-time platform task.

Fields the page's template covers: problem, proposed outcome, affected users and systems,
constraints, open questions, author, status. The worked example is a claims-status portal written
by someone in claims operations. Repeat processes are encoded as skills.

**Governance.** The evidence is the committed file: author, timestamp, history. The product
owner's accept or reject is the merge or the closed review, and that decision is what sends the
intent into Design.

**Measures.** Leading: time from the first conversation to the commit. Lagging: the share of
intents the product owner accepts into Design, and how often `intent.md` still changes after the
first `spec.md` for the same change.

## Design — requirements and design in one session

**Prerequisites:** an accepted `intent.md`, and brand, security, compliance, and UX policies
written as skills. The product owner needs Claude. The page says no engineering skill is required
to run the session.

Claude reads the intent and writes `spec.md`, applying those skills and flagging where policies
contradict. Run the prompt by hand first, then as an organization slash command, then as a
non-interactive job on intent merge that commits `spec.md` as a pull request. From then on the
product owner's first touch is the review.

The product owner checks the spec against the idea, resolves each flagged concern with the named
policy owner before engineering sees the spec, and decides whether it progresses. Higher risk goes
to a technical lead. The page says a person always makes that call. Accepting the spec is what
starts plan mode.

**Governance.** Policy is applied while the spec is written. The spec, the prompt, and the skill
versions are in version control. The product owner signs the spec off.

**Measures.** Leading: time from the `intent.md` commit to the `spec.md` commit. Lagging:
`spec.md` commits dated after the first `plan.md` for the same change.

## Build — plan mode

**Prerequisites:** the intent or the spec if one exists. A `CLAUDE.md` helps.

The engineer starts in plan mode, which the page describes as read-only until the plan is
accepted. The plan names files, order, and tests. The engineer asks what could break, which step
is riskiest, and which options were not taken, and iterates until a stranger could implement from
the plan alone. The approved plan is committed as `plan.md`. Implementation often follows in one
pass. A departure updates `plan.md` in the same commit.

The page's example plan names a new portal panel, a status route and its test, a rate-limit risk,
and proof as that test plus a screenshot against an approved mock.

**Governance.** Routine approval is the engineer's. Higher risk goes to a tech lead or architect.
The page says plan mode itself stops file edits until acceptance. That sentence is graded in
[`03`](03-the-control-ladder.md): it matches the normal documented case, with a bypass exception
the page does not mention.

**Measures.** Leading: share of changes that merge from the first implementation pass, and time
from plan approval to merged PR. Lagging: rework cycles, and how often the merged diff still
matches `plan.md`.

### Auto mode, as the page describes it

After the engineer accepts the plan, Claude can apply edits without a per-edit prompt. The page
says this becomes the default for routine work once `CLAUDE.md`, skills, blocking hooks, and a
test suite exist: a tight spec, a small blast radius, code the tests already cover. Review shifts
from watching edits to reading artifacts after longer sessions. Worktrees are how one person runs
several of those sessions. The page calls this fundamental to the Stage 6 loop.

Current Claude Code docs describe a different auto mode. The delta is in
[`03`](03-the-control-ladder.md). This section records the playbook's prescription and does not
rewrite it into the later classifier.

## Build — `CLAUDE.md`

**Prerequisites:** none. One engineer who knows the repo, and Claude Code.

Run `/init`, then cut the file to what a new joiner needs on day one: build, test, and lint
commands, the conventions that matter, and the mistakes that recur. Commit it at the repo root.
Rule on the page: a mistake twice means the correction goes into `CLAUDE.md`. Keep it under a
page, because the whole file is read at session start and a stale line spends context.

The page's example is a payments service: Java 21, Spring Boot 3, no new Lombok, money as
`BigDecimal`, an integration test per endpoint, an `api` / `core` / `adapters` split, Kafka
schemas left generated, dependencies owned by a platform team, a frozen `v1` package.

**Governance.** Code owners approve changes to the file. It is the instructions the agent works
to, and it is reviewable because it is in git. It is context, not a gate. Enforcement is the hook
section below.

**Measures.** Leading: how often a mistake the file should have caught still repeats, read from
later edits to the file. Lagging: time to a new teammate's first merged PR.

## Build — skills

**Prerequisites:** none required.

Write a skill for knowledge that must be applied consistently, and that does not belong in
`CLAUDE.md` or in a single prompt. One policy, one named owner, one written source. `SKILL.md`
frontmatter says when it triggers. The body says what to do. Place it at
`.claude/skills/<name>/` or ship it org-wide as a plugin. Test that it loads when the task is
asked several different ways. A policy change is a skill change plus the policy owner's sign-off.
The next session picks the new version up.

The page's example skill is an API review: gateway JWT, no anonymous route outside `/health`,
validate bodies and reject unknown fields, an audit event with actor, action, entity, and
timestamp, `pii` fields never in logs, and a local `scripts/check-endpoints.sh` whose output is
included in the summary.

**Governance.** The page's sentence, which this note treats as the load-bearing distinction: a
skill is an advisory control. It makes Claude likely to apply the policy. Nothing forces the
session to comply. A policy that must always hold needs a hook that blocks, or a review pass that
re-checks. "The skill makes violations rare and the hook makes them close to impossible." Skill
invocations are logged in session traces. The "close to impossible" half is graded against the
hooks reference in [`03`](03-the-control-ladder.md).

**Measures.** Leading: time from the policy owner's approval to the skill's merge. Lagging: PR
findings that cite the policy, which should fall toward zero. If they do not, the skill is not
triggering or its text has drifted.

## Build — hooks as guardrails

Not a full play header. Build-phase hooks block edits to protected paths, run a formatter or
linter after an edit, and keep credentials out of the diff. They back a skill whose policy must
hold without exception. They should be fast and scoped to the file that changed. The full test
suite belongs at commit or at the PR. A hook that asks a person for approval belongs in Deploy:
during Build it puts that person back on the critical path of every parallel session.

## Build — parallel sessions and subagents

**Prerequisites:** `CLAUDE.md`. The feedback loop helps, because a session that can check itself
needs less watching. Isolation is git worktrees, plus permission settings so safe commands are not
waiting on a prompt.

A parallel session is another full Claude Code instance in its own worktree (`claude --worktree
feature-auth`). It knows nothing of the others. The engineer is the only shared thing. Tasks that
share files stay in one session, sequentially. Start with two or three sessions. The ceiling is
how many streams one person can still review.

A subagent runs inside one session, with its own context and its own tool list, defined in
`.claude/agents/`. The page's verifier reads and runs shell commands, starts the app, exercises
the change and two neighboring flows, reports against `plan.md`, and does not fix anything.

The feedback loop (below) and this verifier are different. The loop runs through the whole task,
as many times as the work needs. The verifier is one packaging of the final check in a fresh
context, so the verdict is not colored by the assumptions that produced the code.

**Governance.** Hooks and permission settings in the repo apply to every session. Actions are
attributed to the engineer who ran the session.

**Measures.** Leading: concurrent sessions per engineer while review quality holds, from the
OpenTelemetry export. Lagging: changes merged per engineer per week, read next to the rework rate.

## Test — a feedback loop

**Prerequisites:** none. Needs one local command for tests and one for the build. UI work needs a
browser or screenshot tool over MCP.

Wrap today's check in a single command that exits non-zero on failure. List it in `CLAUDE.md`
with an example of healthy output. State a quantifiable target ("these tests pass", "the
screenshot matches the mock", "the endpoint returns 200 with the new field"). For a bug, write
the failing test first, commit it, then fix without editing the test. A hook can block test-file
edits during the fix; the alternative is to reject that diff in review. For UI, iterate
implement / screenshot / compare for two or three rounds. Verification is part of done: run the
checks and paste the output before reporting complete.

**Governance.** The evidence is toolchain output, not the agent's summary. It lives in the session
transcript (forwarded by OpenTelemetry) and in the PR check run. The code owner reviews intent and
risk on top of that evidence.

**Measures.** Leading: first-pass CI success for agent-written changes. Lagging: review time per
PR, and change-failure rate from the incident tracker.

## Test — continuous evals

**Prerequisites:** `CLAUDE.md` and the feedback loop. CI that can run Claude Code
non-interactively, and a key with budget.

Collect 20 to 50 real recent tasks. Each eval is a prompt plus checks: tests pass, lint is clean,
behavior is unchanged, the policy was followed. Run the suite on a schedule and on any change to
`CLAUDE.md`, skills, or hooks. Gate a configuration change on the pass rate. Each production
incident becomes a permanent eval, written by the team that owned the incident. Some teams, the
page says, may run the suite offline on a cadence; the steps are written for the continuous case.

The page's workflow sketch installs `@anthropic-ai/claude-code` and runs `claude -p` per
`evals/*.json` with `--allowedTools` and `--output-format json`, on pull requests that touch
`CLAUDE.md` or `.claude/**`, and on a nightly cron. That file is an illustration. It was not run,
and it is not recorded here as a working workflow.

This suite is a regression check for the agent's setup. It is not a vendor model benchmark, and
this repository does not adopt a pass rate from it. No pass rate is stated on the page.

**Governance.** The threshold is a merge check. The team that owns the configuration change
approves it.

**Measures.** Leading: pass rate over time, and how long an incident takes to become an eval.
Lagging: regressions caught in CI against regressions found in production.

## Deploy — review in the PR loop

**Prerequisites:** an updated `CLAUDE.md`. Skills and subagents when the passes enforce written
policy. Branch protection that requires a code owner.

Two packagings: managed Code Review (called a research preview on the page) enabled by an admin,
or `claude-code-action` in the organization's own CI, with model calls through Bedrock, Vertex, or
Foundry where the traffic has to stay on that agreement.

`REVIEW.md` at the repo root defines three passes: Bugs, Security, and Compliance against
`spec.md`, `plan.md`, and the design principles. It defines Important against Nit, caps nits (the
example cap is five, with the rest summarized as a count), and skips generated paths and anything
CI already enforces. Findings do not approve or block. A team that wants a merge gate on severity
can read a machine-readable tally the check publishes. A person still approves through branch
protection.

`@claude` on a comment makes Claude address it and push, through `claude-code-action`. In the
managed service, `@claude review` requests a fresh review. For a PR Claude opened, the page
describes a slash command that sweeps unresolved comments and failing checks until the PR is green
and waiting only on the code owner.

A review mistake the second time goes into `CLAUDE.md`. Review also flags a `CLAUDE.md` the change
has made stale. Once a month the tech lead rates findings and caps nit volume.

**Governance.** The agent that wrote the code cannot approve it. The PR history is the audit
record. The page points at a separate post for how the controls compose in production. That post
was not read. No productivity or "share of code written by Claude" figure is adopted from it or
from anywhere else.

**Measures.** Leading: time to first review, and the share of comments resolved without a person
touching the branch. Lagging: defects caught before merge against defects that escape.

## Deploy — hooks as approval gates

**Prerequisites:** none. A written list of the approvals that must survive (change-management
sign-off, release authorization, edits to protected paths).

Team hooks live in `.claude/settings.json`. Hooks that engineers must not be able to switch off
live in managed settings. A block explains itself: the reason and the route to approval appear in
Claude's output.

The page's script reads `tool_input.command` from stdin. If the command string contains both
"deploy" and "production" and `RELEASE_APPROVAL` is empty, it writes a reason to stderr and exits
2. Otherwise it exits 0. That is a substring illustration. Exit 2 as a block is graded against the
hooks reference in [`03`](03-the-control-ladder.md). The script was not installed, and an empty
environment variable is not, by itself, a named person's approval. Something outside the script
has to set that variable from a real authorization.

The same mechanism is not deploy-only. The page also uses it to block migration and infra edits
without a ticket, and to stop test-file edits during a fix.

### Managed settings, as a starting point on the page

The page prints one JSON object for a regulated enterprise, deployed by MDM or the admin console,
and says to tailor it rather than copy it. Every deny trades capability. The keys were not checked
one by one against the settings reference on 2026-10-06, so the block is the page's example, not a
config this note recommends. What the page says each group buys:

| Group on the page | What the page says it buys |
|---|---|
| `permissions.deny` | Secrets stay out of context (`Read` of `.env*` and `./secrets/**`). `WebFetch`, `curl`, and `wget` are denied |
| `permissions.allow` | `git` and `make build` / `test` / `lint` are pre-approved so the deny list does not become prompt fatigue |
| `disableBypassPermissionsMode: "disable"` and `allowManagedPermissionRulesOnly` | No engineer, project file, or flag can widen the rules |
| `sandbox` with `failIfUnavailable`, `allowUnsandboxedCommands: false`, a domain allowlist | The page's claim: a tool-level deny on `WebFetch` does not stop a shell from reaching the network; an OS-level domain allowlist does. Refusing to start when the sandbox cannot initialize, and refusing an unsandboxed retry, makes the sandbox a gate. The sandboxing doc was not re-read for this note |
| `credentials` deny of `~/.ssh`, `~/.aws/credentials`, and `GITHUB_TOKEN` | Closes the gap the page says `permissions.deny` leaves for a sandboxed shell |
| `allowManagedHooksOnly` | Only these approval hooks run |
| `disableSideloadFlags` and `strictKnownMarketplaces` | Skills, agents, hooks, and MCP servers arrive through the named marketplace |
| `allowManagedMcpServersOnly` | The tool surface is a platform allowlist |
| `requiredMinimumVersion` | The page's example floor is `"2.1.193"`. That string is the example's pin, not a current version |

**Measures for the hooks.** Leading: time spent waiting on each gate, from OpenTelemetry (timestamp
and allow or block). Lagging: gate violations that reach production, before and after, from the
incident tracker.

## Deploy — CI/CD

**Prerequisites:** Claude already reviews PRs, and approval hooks already exist.

Start with read-only `claude -p`: triage a failed build, summarize a flake, draft a changelog.
Writes (lint, generated docs, review comments) arrive as pull requests. There is no route to
`main`. Agent jobs run in containers, under a network policy, with short-lived tokens and no
standing production credentials. Deploy, status, and rollback are MCP tools, scoped per
environment. Autonomy is tiered: development is free, staging is in the middle, production
prepares the release and a named release manager authorizes it through the hook. Rollback is the
most rehearsed path, a single command exercised in staging, because Stage 6's highest tier calls
it. Non-interactive runs act under the agent's own identity so the log separates the agent's
actions from the engineer who triggered the job.

The page's principle: the agent may act up to the production gate and cannot pass it.

**Measures.** Leading: share of pipeline failures triaged without paging a person. Lagging: the
DORA measures the CI system already emits. No DORA number is stated, and none is invented here.

## Maintain — closing the loop

**Prerequisites:** the intent format, accelerated PR reviews, hooks as an action boundary, and a
rollback path.

So far every stage started because a person prompted it. This play starts from a trigger: a
control-band breach, a ticket, a channel message, or a schedule. Detection is a script. One metric
with a stable rolling baseline (CI failure rate, post-deploy 5xx, PR cycle time). Mean and
standard deviation over a rolling window, Western Electric or similar, version-controlled and unit
tested. No model in the detector.

Tiers in the page's `bands.yaml`: at 1σ, log only; at 2σ, invoke Claude read-only to diagnose; at
3σ, Claude may act only by opening a PR into the review gate or by triggering a pre-approved
runbook. The trigger is a scheduled workflow, a webhook, or a CronJob. Claude runs stateless
(`claude -p` on a CI runner, or an Agent SDK service in a sandbox). It writes the diagnosis as
`intent.md`. The service owner or on-call triages: fix now, schedule, or dismiss. Dismissals tune
the bands. When a fix ships, add an eval.

Examples on the page: a 3σ CI failure quarantines a flake or opens a revert PR; a 3σ 5xx rate with
a deploy in the window triggers the existing rollback; PR cycle-time drift writes a report for
leadership. The last one is there to show the same harness on a process metric.

**Measures.** Leading: time from breach to an `intent.md` in the triage queue. Lagging: share of
findings that become merged fixes, and repeat incidents of the same class.

## Maintain — recurring scans

**Prerequisites:** the PR review gate and approval hooks.

Claude Security, described as a public beta for Claude Enterprise. Scheduled scans on Mythos 5 in
Anthropic's infrastructure. Findings are validated before the report, with a confidence rating.
Patches are reviewed in Claude Code on the web. The first scan is a baseline and, the page says,
will surface findings in code that was considered clean. Weekly is the suggested default. Dismiss
with a reason so the same finding does not return as new. A bounded finding becomes a suggested
patch through the PR gate. The proposer cannot approve it. Anything wider than one patch becomes
an `intent.md`. After a fix reaches production, add an eval for that vulnerability class. Export
CSV, Markdown, or webhooks when auditors expect the existing tracker to stay the system of record.

The page says this augments static analysis and dependency scanning. Deterministic checks stay in
CI. Billing is consumption at Mythos 5 rates. The product name, the model name, and the beta
status are a snapshot of the page. They were not re-checked against a product changelog.

**Measures.** Leading: share of connected repositories on a schedule, and time from a reported
finding to a patch entering review. Lagging: vulnerabilities the scheduled scan found, set against
those found in production or by an external report, and the trend in findings per scan.

## Maintain — Claude Tag

Public beta, Slack, as of the page. Claude is a channel member under its own identity. The
conversation stays in the channel. MCP is how it checks that a metric is back at baseline. The
post-mortem is written to a version-controlled lessons file. A small fix goes through the PR
gate. Anything larger is an `intent.md`. The page points at a separate post on Claude Tag for
on-call CI/CD. That post was not read.

The channel, on the page's caption, is the audit trail for that path: request, diagnosis, human
authorization, and the fix stay where the incident was handled.
