---
type: concept
status: active
last_ingested_from: docs/07-harness-engineering.md
related_pages: [concepts/harness, concepts/retained-reasoning, concepts/primary-source-verification]
created: 2026-09-22
updated: 2026-09-23
---

# Harness Engineering — the discipline of governing an autonomous runtime

- Purpose: the operating principles drawn from OpenAI's internal "zero hand-written code" experiment.
- Scope: the experiment's facts, redefining the engineer's role, legibility, mechanical enforcement, entropy and garbage collection, how to apply it
- Primary source: [Harness engineering](https://openai.com/index/harness-engineering/), Ryan Lopopolo, 2026-02-11
- Updated: 2026-09-23

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | The experiment | an internal beta product shipped over five months **with no hand-written code** |
| 2 | Scale | about **a million lines**, roughly **1,500 PRs**, three engineers (now seven) |
| 3 | Throughput | **3.5 PRs per engineer per day** — and it *increased* as the team grew |
| 4 | Estimate | about **one tenth** the time it would have taken by hand |
| 5 | Slogan | **"Humans steer. Agents execute."** |
| 6 | Where discipline shows up | in the **scaffolding**, not the code |

## §2 The bottleneck was the environment, not the model  {#s2-environment}

Early progress was slower than expected — not because Codex was incapable, but because **the
environment was underspecified.**

When something failed, the answer was never "try harder" but always:

> **"What capability is missing, and how do we make it both legible and enforceable for the agent?"**

The working style was **depth-first** — break large goals into smaller building blocks (design, code,
review, test), have the agent construct them, and use them to unlock more complex tasks.

Review was pushed almost entirely **agent-to-agent**: Codex reviews its own changes locally →
requests additional agent reviews locally and in the cloud → responds to feedback → iterates until
every agent reviewer is satisfied.

## §3 Making the application legible to agents  {#s3-legibility}

As code throughput rose the bottleneck became **human QA capacity.** So the UI, logs and metrics
themselves were made directly legible to Codex.

| Measure | Effect |
|---|---|
| Made the app **bootable per git worktree** | Codex could launch and drive one instance per change |
| **Wired the Chrome DevTools Protocol into the agent runtime** (DOM snapshots, screenshots, navigation skills) | reproduce bugs, validate fixes, reason about UI behaviour |
| Exposed observability through a local stack, ephemeral per worktree | agents query **logs with LogQL and metrics with PromQL** → prompts like "ensure service startup completes in under 800ms" become tractable |

> Single Codex runs regularly work on one task for **upwards of six hours** (often while the humans
> are sleeping).

## §4 A map, not a manual  {#s4-map-not-manual}

> **"give Codex a map, not a 1,000-page instruction manual."**

How the "one big `AGENTS.md`" approach failed:

| # | Failure |
|---|---|
| 1 | **Context is a scarce resource** — a giant instruction file crowds out the task, the code and the relevant docs |
| 2 | **Too much guidance becomes non-guidance** — when everything is "important," nothing is. Agents pattern-match locally instead of navigating intentionally |
| 3 | **It rots instantly** — a monolithic manual becomes a graveyard of stale rules and quietly turns into an attractive nuisance |

> That Slack discussion that aligned the team on an architectural pattern? If it is not discoverable
> to the agent, it is **illegible in the same way** it would be unknown to a new hire joining three
> months later.

## §5 Mechanical enforcement — invariants, not prescriptions  {#s5-mechanical}

> **Enforce invariants; don't micromanage implementations.**

For example: they **require** parsing data shapes at the boundary but are not prescriptive about
*how*.

The layering rule — within each business domain, code may only depend "forward":

```
Types → Config → Repo → Service → Runtime → UI
```

Cross-cutting concerns (auth, connectors, telemetry, feature flags) enter through **a single explicit
interface: Providers.** Anything else is disallowed and enforced mechanically by custom linters and
structural tests (Codex-generated, of course).

> **Because the lints are custom, the error messages are written to inject remediation instructions
> into agent context.**

> "This is the kind of architecture you usually postpone until you have hundreds of engineers.
> With coding agents, it's **an early prerequisite**: the constraints are what allows speed without
> decay."

## §6 Throughput changes the merge philosophy  {#s6-merge}

- Minimal blocking merge gates
- Pull requests are short-lived
- Test flakes are addressed with follow-up runs rather than blocking indefinitely

> "In a system where agent throughput far exceeds human attention, **corrections are cheap, and
> waiting is expensive.**" This would be irresponsible in a low-throughput environment. Here it is
> often the right trade-off.

## §7 Entropy and garbage collection  {#s7-entropy}

**Codex replicates patterns that already exist in the repository** — including the uneven and
suboptimal ones. Drift is inevitable.

At first humans handled it manually: every Friday (20% of the week) cleaning up "AI slop."
Unsurprisingly that did not scale. Instead they encoded **"golden principles"** directly into the
repository and built a recurring cleanup process.

- Prefer shared utility packages over hand-rolled helpers, to centralise invariants
- Do not probe data "YOLO-style" — validate boundaries or rely on typed SDKs, so the agent cannot
  build on guessed shapes

On a regular cadence, background Codex tasks scan for deviations, update quality grades and open
targeted refactoring pull requests. Most are reviewed in under a minute and automerged.

> Technical debt is like a high-interest loan — **it is almost always better to pay it down
> continuously in small increments** than to let it compound.

## §8 The level of autonomy reached  {#s8-autonomy}

Given one prompt, the agent can: validate the current state of the codebase → reproduce a reported
bug → **record a video demonstrating the failure** → implement a fix → validate it by driving the
application → **record a second video demonstrating the resolution** → open a pull request → respond
to agent and human feedback → detect and remediate build failures → escalate to a human only when
judgment is required → merge.

> The author explicitly notes this behaviour **depends heavily on that repository's structure and
> tooling** and should not be assumed to generalise without similar investment.

## §9 Applying it to your own project  {#s9-applying}

| Principle | Action |
|---|---|
| A map, not a manual | keep `AGENTS.md` / `CLAUDE.md` around 100 lines as a table of contents; push depth into `docs/` |
| Mechanical enforcement | lint doc freshness and cross-links in CI. **Put remediation instructions in the lint error messages** |
| Plans as first-class artifacts | commit active, completed and tech-debt plans to the repository |
| Make the app legible to agents | per-worktree boot, log and metric query paths, browser-control skills |
| Invariants over prescriptions | enforce layer dependency direction; leave library choice free |
| Continuous GC | periodic background tasks that scan for drift and open targeted PRs |
| Move context into the repository | migrate decisions living in chat or doc tools into versioned artifacts |

## §10 The harness is a performance variable  {#s10-perf-variable}

Stated directly in the "Codex as a platform" post:

> "Harness design can materially change results: on ARC-AGI-3, retained reasoning and context
> compaction raised GPT-5.6 Sol's score from 13.3% to 38.3% while reducing output tokens sixfold."

**Two harness-level settings, not a model change.** Detail in [[concepts/retained-reasoning]].

## §11 Read next  {#s11-next}

- [[concepts/harness]] — the structure of what is being governed
- [[concepts/retained-reasoning]] — a concrete case of harness settings changing performance
- Original: [`docs/07-harness-engineering.md`](../../../docs/07-harness-engineering.md)
