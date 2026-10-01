# RRSI — a search over a harness, not a harness

> **What this is.** A study of [RRSI](https://github.com/google-research/rrsi) (Regularized
> Recursive Self-Improvement of Agent Harnesses), Google Cloud AI Research with UNC, Stanford
> and Washington University in St. Louis. Paper: arXiv:2609.24972 (2026-09-21). Code read at
> **`be50316e1d`** (2026-09-23, Apache-2.0). The name people compress to "RIIS" is this one.
> Dream-RSI (arXiv:2609.14858) is a different paper: it replays past searches and does not edit
> a harness. It is not studied here.
>
> **Why.** This repository's subject is the harness around a frozen model. RRSI is a procedure
> that *edits that harness* and tries to stop the edit from memorizing the eval set. It is a
> method on the harness-engineering axis ([`PURPOSE.md`](../ai-workflow/memory/active/PURPOSE.md)
> §0.5), not a sixth product.
>
> **Not an endorsement, and not a benchmark.** The published scores are the authors'
> measurements. They are listed in [`99-sources.md`](99-sources.md) as 📣 and are not adopted.
> Nothing here was re-run.

## ⚠️ Read status

**The search was not executed.** No Vertex call, no harbor job, no evolve branch. The loop,
the component vocabulary, the selection rule and the missing-trial rule are **source-read**.
The paper states the same algorithms; where a number lives only in the paper or the README
table, it stays 📣.

## Files

| # | File | What it covers |
|---|---|---|
| 01 | [What it edits](01-what-it-edits.md) | Frozen weights, open edit space, the nine component tags, the incumbent as a git commit |
| 02 | [The loop](02-the-loop.md) | Proposal-side budget and history; selection-side critic, noise floor, cost rule, prune |
| 03 | [Measurement](03-measurement.md) | How a score is aggregated, when a missing trial is a zero, why the published table is not a finding |
| 99 | [Sources](99-sources.md) | Grades |

## If you only have two minutes

RRSI does not build an agent. It holds the model fixed and searches the scaffold around it.
The search is what gets regularized:

1. **Cap how many independent edits one candidate may bundle**, and anneal that cap to one, so a late gain can be attributed.
2. **Remember which hypothesis already failed**, and when the score stalls, force a slot onto a component the run has never touched.
3. **Reject a diff that names the test** before spending an evaluation. The rejector is a regex plus another model call, not a proof.
4. **Refuse a gain inside the noise band**, and refuse a real gain that spends tokens it did not earn.
5. **Drop components whose recent measured yield is not positive.**

The incumbent is always a commit on `evolve/<domain>`. A candidate that cannot be repaired, or whose evaluation lost more than a fraction of its trials to infrastructure, is not measured into the history.

## What this study does **not** establish

- It does **not** establish the README's score table. Those numbers were not re-run.
- It does **not** establish that the critic catches leakage. The critic is Claude Opus 4.8 reading a diff.
- It does **not** establish that a harness found this way transfers to a harness this repository has read (Codex, Strands, Gas Town). The three instances start from Terminus-2 and an archipelago react toolbelt.
- Dream-RSI is a different system. Do not cite its call-count claims as RRSI's.
