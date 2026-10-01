# 99. Gas Town — sources and verification status

> Every claim in `gas-town/` is graded. **✅** = read from source or first-party design docs at a
> named commit. **📣** = a claim made by the project or its community, recorded but not adopted.
> **⚠️** = not verified here.

## A. Primary sources — read directly ✅

| Source | What was taken | Grade |
|---|---|---|
| [`gastownhall/gastown`](https://github.com/gastownhall/gastown) @ **`649b832b76`** (2026-07-23, `v1.2.1-304-g649b832b`), MIT, Go | the entire study | ✅ source |
| `docs/glossary.md` | role + work-unit vocabulary, GUPP / MEOW / NDI definitions | ✅ first-party |
| `docs/concepts/propulsion-principle.md` | the propulsion rule, the stall failure mode, startup contract | ✅ first-party |
| `docs/concepts/identity.md` | `BD_ACTOR` slash format, three-field attribution, `GIT_AUTHOR_*` split | ✅ first-party |
| `docs/concepts/molecules.md` | Formula → Protomolecule → Molecule/Wisp, `pour` trade, row-count rationale | ✅ first-party |
| `docs/concepts/polecat-lifecycle.md` | Working/Idle/Done/Stalled/Zombie, retired-completion model | ✅ first-party |
| `docs/concepts/heartbeats.md` | three heartbeat stores, the "never one store" rule, tmux cross-check | ✅ first-party |
| `docs/concepts/convoy.md` | convoy vs swarm vs stranded convoy | ✅ first-party |
| `docs/design/architecture.md` | two-level beads split, directory layout, agent taxonomy | ✅ first-party |
| `docs/design/scheduler.md` | dispatch modes, capacity cap, step-14-after-health, `bd ready` join | ✅ first-party |
| `docs/design/mail-protocol.md` | `POLECAT_DONE` / `MERGE_READY` / `MERGED` message routes | ✅ first-party |
| `docs/design/sandboxed-polecat-execution.md` (status: **Proposal**, 2026-03-02) | control/execution plane split, identity-forgery threat | ✅ first-party (proposal) |
| `docs/design/convoy/mountain-eater.md` | the judgment layer, hysteresis, "no agent holds the thread", NDI | ✅ first-party (design) |
| `docs/design/property-layers.md` | four-layer config, the `Blocked` override value | ✅ first-party |
| `internal/polecat/manager.go` | spawn = `WorktreeAddFromRef`; resume = `WorktreeAddExistingForce` | ✅ source |
| `internal/beads/beads_merge_slot.go` | merge slot as a labelled bead (holder in Description) | ✅ source |
| `internal/deacon/heartbeat.go`, `redispatch.go` | 5 min stale / 20 min very-stale / 5 min re-dispatch cooldown | ✅ source |
| `README.md` | the problem framing, 20–30 agent claim, role blurbs | ✅ first-party (self-description) |

## B. Recorded but not adopted 📣

| Claim | Where from | Why not adopted |
|---|---|---|
| "Kubernetes for AI agents" | community/press framing | analogy does not survive the implementation; defensible comparison is narrow (Part C of [`04`](04-orchestration-techniques.md)) |
| "$100/hour at 12–30 agents"; "chaotic at that scale" | operator anecdotes via secondary coverage | **not measured here**; do not cite as a benchmark |
| "scale comfortably to 20–30 agents" | README | a self-description of capability, not an independent measurement |
| "100% vibe coded" (Yegge, via press) | press | provenance is a quotation, not something this study can grade |

## C. Not verified here ⚠️

| Item | Why |
|---|---|
| Runtime behaviour | **not run.** No `gt`/`bd` binary executed, no town created, no Dolt server started. Every mechanism here is read from source and design docs |
| Hosted "Gas Town by Kilo" and the Wasteland federation | secondary coverage only; not read from a first-party repo here |
| Gas City (the platform this operating model was extracted into) | read in [`gas-city/`](../gas-city/99-sources.md) @ `3ef7fadd42`. This row is closed |
| Beads (`gastownhall/beads`) as a separate project | used here only through Gas Town's `internal/beads` + docs; the standalone project was not cloned |
| Cost, throughput, and merge-conflict-rate numbers | not measured; see 📣 above |
| Live behaviour of a polecat under the (proposed) sandbox | the doc is a **Proposal**; the split is a design, not an observed deployment |

## D. Method note

This study followed this repository's standing rule: **read the generated schemas and source, not
the marketing**. Two things that pass here because of it:

- The vocabulary in [`01`](01-vocabulary.md) is reconciled against the source (`internal/`), not
  just the glossary — e.g. the polecat spawn/resume pair was confirmed as real git plumbing
  (`WorktreeAddFromRef` vs `WorktreeAddExistingForce`), and the merge "lock" was confirmed to be a
  bead, not a file lock.
- The ⚠️ column above is non-empty on purpose. A study that reported Gas Town's capability claims
  as findings would be indistinguishable from the press coverage it was meant to replace.

## E. Cross-references into this repository

- [`PURPOSE.md` §0.3](../ai-workflow/memory/active/PURPOSE.md) — why this study was admitted
- [`04-orchestration-techniques.md`](04-orchestration-techniques.md) — Part B maps this onto
  `SYNTHESIS.md` §2.4 (planes), §2.7 (gates), §6.5–6.7 (context drift, false checks), §7 (method)
- [`ai-workflow/wiki/concepts/multi-agent-orchestration.md`](../ai-workflow/wiki/concepts/multi-agent-orchestration.md)
  — the shared-concept page this study contributes
