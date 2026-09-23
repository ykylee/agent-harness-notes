# Scope declaration for this study

- Status: **resolved (2026-09-23)** — began as option A, closed by extending the shared PURPOSE as
  part of the fusion decision
- Updated: 2026-09-23 (second revision)

## Why a separate declaration was needed

The shared [`PURPOSE.md`](../ai-workflow/memory/active/PURPOSE.md) originally excluded "comparative
research on non-OpenAI vendors' harnesses — work for a separate repository." By that declaration, a
browser-agent study was out of scope.

**The shared PURPOSE was not quietly edited.** That file is the basis on which the existing study was
judged; widening it silently would erase the terms the existing documents were written under.
Instead this branch's scope was declared separately.

## Resolution — option A (2026-09-23)

| Option | Result | |
|---|---|---|
| **A. Keep it branch-scoped** | **This document is the scope.** The shared `PURPOSE.md` is untouched | ✅ **chosen** |
| B. Extend the shared PURPOSE | Redefine the repository as "agent harnesses generally" | not chosen |
| C. Split into a separate repository | This branch becomes a draft for migration | not chosen |

### ⚠️ Follow-up (2026-09-23) — option A's condition fired

Option A carried the condition "when merging, widen the shared PURPOSE along with it." **Fusing the
wiki concept layer was effectively that merge**, so the condition was honoured:
[`PURPOSE.md`](../ai-workflow/memory/active/PURPOSE.md) now records the extension in §0, drops
"non-OpenAI vendors" from its exclusions, and adds goal G5.

**This document is now history.** The shared PURPOSE is the operative criterion.

### What option A meant (historical)

| While on the branch | When attempting to merge |
|---|---|
| The shared `PURPOSE.md` is untouched; its exclusion stands | **The merge itself is the act of widening scope.** The exclusion must be edited **in the same PR** |
| This document is the branch's criterion | While the work stays on a branch, the conflict does not bite |
| `main`'s existing study remains under its own declaration | Deferred to the merge, not eliminated |

> ⚠️ **Option A was not a way of postponing a decision but of drawing a boundary.** While the work
> stayed on the branch, neither study trespassed on the other's declaration. But **a merge could not
> be done quietly** — the moment it happened the shared PURPOSE would have become false.

## This branch's scope

### Included

- **Features, composition and structure** of agent tools that use the browser as a control surface
- **Design and UI/UX** — entry points, state representation, approval flow, shortcut systems
- Architecture by control-surface type (native browser / extension / library)
- Credential, permission and sandbox design
- Security problems specific to this class, such as indirect prompt injection
- **Aside first**, the rest as comparative context

### Excluded

- General web scraping and crawling infrastructure (Firecrawl, Browserbase and so on) — mentioned
  only as context
- Benchmarking or reproducing model performance
- Tracking each product's pricing policy (only a snapshot at the time of research is recorded)
- Actually implementing or forking anything

## Inherited discipline

The subject differs, but [the existing study's method of
knowing](../ai-workflow/wiki/concepts/primary-source-verification.md) carries over unchanged.

| Discipline | How it applies here |
|---|---|
| Committed artifacts over prose | Product documentation (`.md` originals), source and reverse-engineering records before landing pages |
| No secondary source is settled before cross-checking | Numbers from comparison blogs are marked "self-reported" until checked |
| Inference is labelled as inference | Estimates of undisclosed internals carry a grade |
| Refutations are kept, not deleted | Claims shown to be wrong stay on the record with their verdict |

**This field is especially full of vendor self-reported benchmarks.** Grading matters more here than
it did in the existing study.
