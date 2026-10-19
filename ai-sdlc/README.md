# The AI-native SDLC playbook — an operating note, not a harness

> **What this is.** A reading of Anthropic's [The AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)
> (Louis Claxton, 2026-08-21). The same text is the Claude Academy course of that name
> (14 lessons; the course page says the blog is the single-page full playbook). Audience on the
> course page: engineering, platform, and security leads whose organization already uses Claude
> Code, especially in a regulated enterprise.
>
> **Why.** The playbook is a prescription for running Claude Code across a software lifecycle.
> It sits on the harness-engineering axis already in scope
> ([`PURPOSE.md`](../ai-workflow/memory/active/PURPOSE.md) §0.6), next to OpenAI's operating note
> in [`docs/07`](../docs/07-harness-engineering.md). It is not a sixth product study. There is no
> harness binary here.
>
> **Not an endorsement, and not a measurement.** Indicators in the playbook are instructions to
> measure (git timestamps, PR metadata, OpenTelemetry, an incident tracker). They are not results.
> Time-to-intent targets and "Applied AI best practices" framing stay 📣. Nothing here was run.

## ⚠️ Read status

**The plays were not executed.** No Claude Code session, no hook, no managed-settings file, no
eval workflow. The page was read on 2026-10-06. Two Claude Code doc pages were spot-checked the
same day: [hooks](https://code.claude.com/docs/en/hooks) and
[permission modes](https://code.claude.com/docs/en/permission-modes). The dependency-graph image
was not read; the adoption order in [`01`](01-the-loop.md) is reconstructed from each play's
Prerequisites text. The PDF was not downloaded. Individual Academy lesson pages were not fetched.
The security post the playbook links for "how these controls compose at production scale" was not
read, and no figure from it is adopted.

Three nearby posts are different documents and are not this note: "How Anthropic secures its
AI-native software development lifecycle" (Jason Clinton, 2026-07-21), "Running an AI-native
engineering org" (Fiona Fung, 2026-06-03), and "The founder's playbook" (2026-05-14).

## Files

| # | File | What it covers |
|---|---|---|
| 01 | [The loop](01-the-loop.md) | The thesis, the six-stage shift, the committed artifact chain, where a record is allowed to live |
| 02 | [The plays](02-the-plays.md) | Each play: what changes, what it needs first, the steps, who still decides, what to measure |
| 03 | [The control ladder](03-the-control-ladder.md) | Context file, advisory skill, deterministic hook, a human the writer cannot pass, settings the engineer cannot edit — graded against the docs that were opened |
| 99 | [Sources](99-sources.md) | Grades |

## If you only have two minutes

The page's claim is that writing code is no longer the slow step, so the lifecycle has to be
rebuilt around artifacts an agent and a person can both read, while the old control objectives
stay.

1. **Each stage commits an artifact the next stage reads.** `intent.md` → `spec.md` → `plan.md` → the diff and its tests → a PR plus `REVIEW.md` findings → a new `intent.md` when a production band breaks. The commit chain is the audit trail the page wants.
2. **A skill does not enforce a policy.** The page's own sentence: a skill makes violations rare; a hook that blocks makes them close to impossible. The human who must approve a release is still a person, and the agent that wrote the change cannot approve it.
3. **Detection of a breach stays a script.** Mean and standard deviation, version-controlled, no model. Claude is invoked only after a band breaks, and the tier says whether it may only diagnose or may open a pull request.
4. **The indicators are a measurement plan.** "Weeks to hours" is the page's expectation, not a number this repository measured.

## What this study does **not** establish

- It does **not** establish that any play shortens a cycle. No timestamp was read from a repository that runs this process.
- It does **not** establish the managed-settings JSON as a config to deploy. The page itself says to tailor it. The keys were not checked one by one against the settings reference.
- It does **not** establish current Claude Code behavior beyond the two doc pages opened on 2026-10-06. Those docs move by version. Where they differ from the playbook, both are recorded in [`03`](03-the-control-ladder.md).
- It does **not** replace this repository's own memory, backlog, or handoff. Those are a different record.
