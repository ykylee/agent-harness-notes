---
purpose_version: 1
last_purpose_review: 2026-09-23
---

# Purpose — why this repository exists

## 0. Scope extension, 2026-09-23

This repository began as an investigation into the **OpenAI Codex harness**, and its excluded areas
originally read "comparative research on non-OpenAI vendors' harnesses — work for a separate
repository."

The browser-agent study (`browser-agents/`) turned out to be **another instance of the same
abstraction**, which made that exclusion untenable. Two decisive reasons:

1. **They meet in code.** Aside's daemon registers `openai-codex` and `opencode` as model provider
   ids, and carries a `CODEX_TOOL_CALL_PROVIDERS` set plus a `supportsAdditionalTools` flag — it
   **implements Codex's `responses_lite` request-shape branching**. The two studies touch at the
   level of source.
2. **They share concepts.** Eight of the sixteen wiki concepts are now supported by evidence from
   both. Approval gates, providers-as-data, capability distribution and the control/execution plane
   turned out to be axes that do not depend on the execution surface at all.

The repository is therefore redefined as **an investigation into agent harnesses**. Codex remains the
first case; the rest are the contrast group that tests the abstraction.

**What changed is the scope, not the method.** The discipline in §5 is unchanged.

## 0.1 Implementation feedback, 2026-09-23 — a clarification, not an extension

The conclusions of `SYNTHESIS.md` were implemented in a **separate repository** (`ykylee/heddle`,
private). That repository is not part of this one, and the exclusion in §3 stands unchanged: no
implementation, fork or redistribution lives here.

What was admitted is narrower — **the measurements that implementation produced**, recorded in
`SYNTHESIS.md` §6. Five of this repository's own conclusions were refuted by running them.

Two reasons this belongs here rather than only in the other repository:

1. **It is a grade, and a stronger one than anything else here.** G3 requires a verification status
   on every claim. Every other claim in these notes is read out of someone else's artifact;
   these were run. A repository whose purpose is to grade claims cannot discard its best grade.
2. **G3 also requires keeping refutations.** Deleting a conclusion that measurement contradicted, or
   leaving it standing unmarked, would be the same failure the rule exists to prevent — and the
   refuted claims here are **this repository's own**, which makes keeping them harder and more
   necessary.

The boundary to hold: **import measurements, never the code.** If a future session finds itself
maintaining heddle from inside this repository, §3's exclusion has been breached.

- Purpose: define *why* this repository exists and where it is going (directional intent). AI agents
  read it at session-start and backlog-update to classify work and judge scope.
- Scope: the four elements (Goals / Key Questions / Research Scope / Evolving Thesis)
- Audience: AI agents, repository maintainer
- Status: active — scope extended to agent harnesses generally on 2026-09-23 (§0)
- Updated: 2026-09-23
- Related: [PROJECT_PROFILE.md](../../../docs/PROJECT_PROFILE.md), [99-sources.md](../../../docs/99-sources.md), [SYNTHESIS.md](../../../SYNTHESIS.md)

## 1. Goals

- **G1**: record the **actual contract** of agent harnesses by reading **generated schemas, source
  and binaries** rather than blog summaries. OpenAI Codex first (App Server JSON-RPC, SDK, Agents
  API), with browser-type agents as the contrast group.
- **G2**: leave behind, in a form that **converts into a build checklist**, what you would have to
  implement to build your own harness — methods, events, approval flow, perception model, sandbox,
  credentials, plugins.
- **G3**: attach a verification status to every claim (confirmed / inferred / refuted), and **keep
  wrong secondary sources on the record as refutations rather than deleting them.** The record of
  what was wrong is what makes the rest trustworthy.
- **G4**: keep the English bodies and the Korean report resting on the same facts.
- **G5**: re-index harnesses with different execution surfaces (shell/filesystem vs. browser/OS)
  **onto the same conceptual axes**, so it is clear which properties belong to a surface and which
  belong to harnesses in general.

## 2. Key Questions

- **Q1**: where exactly is the boundary between model and execution (the wire protocol) in the Codex
  harness? Is the core reusable at all?
- **Q2**: are the managed Agents API and the open-source App Server the same harness or different
  surfaces? How far do they agree?
- **Q3**: is an adapter that maps Responses payloads back onto Chat Completions possible without a
  fork?
- **Q4**: which claims are settled by a primary source and which are still inference? Does the
  document say so itself?
- **Q5**: among the design axes of a harness, which **depend on the execution surface** and which do
  not?

## 3. Research Scope

### 포함 영역

- Reading the generated schemas and Rust source of `openai/codex`
- The App Server JSON-RPC protocol (methods / notifications / approvals / transports / error codes)
- Agents API (endpoints, environment types, sandboxes, tools, webhooks, observability, cost)
- CLI `codex exec`, the TypeScript and Python SDKs
- Model provider configuration, and the feasibility of a Responses↔Chat Completions adapter
- The native Windows sandbox, marketplace and plugin distribution formats
- Harness engineering operating principles (OpenAI's internal experiment)
- Source verification records and the history of refutations (`99-sources.md`)
- **Control surface, perception model and credential design of browser-type agents**
  (`browser-agents/`)
- **The axes shared by agent harnesses generally** — the concept layer
  (`ai-workflow/wiki/concepts/`) and the cross-study synthesis (`SYNTHESIS.md`)

### 제외 영역

- **Actually implementing, forking or redistributing a harness** — these are research notes, not a
  codebase. Implementation lives in a separate repository; only its **measurements** come back here,
  as evidence (§0.1)
- **Tracking or reviewing a specific vendor's product features** — only a snapshot at the time of
  investigation is recorded. Price and feature changes are not chased.
- Reproducing model benchmarks (a vendor's self-reported score is something to **adjudicate**, not a
  basis for comparison)
- Internal product design documents — take conclusions from here, do not write them here
- Anything asserted from a secondary source alone — it stays "unverified" until checked against a
  primary one

## 4. Evolving Thesis

*Working hypotheses so far; these can change.*

- A harness is the **execution system** that sits between a model and a task. OpenAI opened theirs in
  three layers: a binary, SDKs and a managed API.
- **Committed artifacts** — generated schemas, source, defaults, binaries — are closer to the truth
  than prose. Prose drifts.
- An adapter is only free when it attaches as a **provider-shaped proxy** rather than a fork. The
  moment it holds state, that advantage is gone.
- Research baselines go stale quickly. The first move of a re-investigation is not gathering new
  facts but **checking existing facts for drift.**
- The design axes of a harness split into those that are **surface-independent** (approval,
  permissions, providers, capability distribution) and those that are **surface-specific**
  (perception model, prompt injection, credential shielding). The former is this repository's
  reusable asset.
- **Trying `.md` and `/llms.txt` on a documentation site first** is a general technique, but not a
  universal one — it fails on client-rendered sites.
