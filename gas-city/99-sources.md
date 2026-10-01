# 99. Gas City — sources and verification status

> Every claim in `gas-city/` is graded. **✅** = read from source or from a first-party doc that
> was checked against that source, at the named commit. **📣** = a claim made by the project or
> its community, recorded but not adopted. **⚠️** = not verified here.
>
> When a first-party architecture note and the code disagree, the note is listed under drift,
> not under ✅.

## A. Primary sources — read directly ✅

| Source | What was taken | Grade |
|---|---|---|
| [`gastownhall/gascity`](https://github.com/gastownhall/gascity) @ **`3ef7fadd42b44d6d902bc135bd8d9aa1d5fce7ce`** (2026-09-30, `#6879`), MIT, Go 1.26.6. Shallow clone; tag `edge` on that commit is a moving tag, not a release pin | the whole study | ✅ source |
| `docs/getting-started/how-gas-city-works.md` | six primitives, machinery vs primitives, prefix-isolation claim | ✅ first-party, claim checked |
| `docs/getting-started/coming-from-gastown.md` | role translation table, "zero roles", what not to port | ✅ first-party |
| `docs/reference/specs/formula-spec-v2.md` | v1/v2 peer contracts, control vs work beads | ✅ spec; switch re-read in code |
| `docs/reference/internal/beads-topology.md` | one Dolt server, `issue_prefix`, `inherited_city` | ✅ first-party; keys re-read in `internal/beads/contract/files.go` |
| `docs/reference/trust-boundaries.md` | trusted config vs untrusted bead text; ambient secret strip | ✅ first-party |
| `docs/guides/understanding-formulas.md` | which contract to choose; `gc converge` still v1-only | ✅ first-party |
| `internal/config/config.go` `Agent`, `DaemonConfig.FormulaV2Enabled` | no role enum; formula v2 default on | ✅ source |
| `internal/beadmeta/values.go`, `kindsets.go` | `ControlKinds` | ✅ source |
| `internal/dispatch/runtime.go` `ProcessControl` | one case per control kind; skip when status ≠ open | ✅ source |
| `internal/dispatch/control.go` | retry / ralph attempt loop | ✅ source (header and strategy) |
| `internal/runtime/liveness.go` | `Liveness`, `ObservationIncomplete` | ✅ source |
| `internal/runtime/acp/cutover.go`, `acp.go` `Pending`/`Respond`/`SetMeta` | three-outcome passthrough; permission unsupported; sidecar threat comment | ✅ source |
| `internal/runtime/acp/protocol_conformance_test.go` `TestACPProtocolPermissionTimeoutRejects` | no client reply to `session/request_permission` | ✅ source (test) |
| `internal/orders/triggers.go` `CheckTriggerWithOptions` | cooldown, cron, condition, event, manual, webhook | ✅ source |
| `internal/beads/class_store.go` | typed class wrappers over `Store` | ✅ source |
| `internal/citywriteauth/doc.go` | verify-only ed25519 city-write grants | ✅ source |
| `internal/builtinpacks/registry.go` | core, bd, dolt, gastown, gascity embedded | ✅ source |
| `internal/bootstrap/packs/core/pack.toml`, `agents/control-dispatcher/agent.toml`, `template-fragments/claim-protocol.template.md` | control-dispatcher command; claim protocol; `ga-tmzjx6` | ✅ source |
| `examples/gastown/pack.toml` | Gastown import pin `sha:33d3a430…`; mayor/deacon/boot `max_session_age` | ✅ source |
| `README.md` | provider list, tmux still required, file beads provider | ✅ first-party (self-description) |

## B. Recorded but not adopted 📣

| Claim | Where from | Why not adopted |
|---|---|---|
| "Zero roles" as a description of the product | `how-gas-city-works.md`, `coming-from-gastown.md` | ✅ for `config.Agent`. The binary embeds the Gastown pack and `mol-polecat-*` formulas. See [`01`](01-vocabulary.md) §4–§5 |
| "No agent participates in control execution" | formula spec v2 | ✅ for model workers. Control runs in a `control-dispatcher` session whose command is `gc` |
| "Hundreds of concurrent agents" / software factory / dark factory | project and secondary announcements | not measured |
| Kubernetes analogy | reconciler shape, and press around Gas Town | the reconciler is the part that fits. The rest does not |
| `engdocs/architecture/glossary.md` "each rig gets its own beads database" (verified 2026-04-25) | stale architecture note | contradicted by `beads-topology.md` and `contract/files.go` at this commit |
| `engdocs/architecture/formulas.md` (verified 2026-03-17) as the current formula engine | stale architecture note | predates the v2 control dispatcher. The spec and `ProcessControl` are current |

## C. Not verified here ⚠️

| Item | Why |
|---|---|
| Runtime behaviour | **not run.** No `gc` binary built, no city created, no Dolt server, no session attached |
| tmux liveness fallback line-by-line | A2 caveat. Providers without `LivenessObserverWithError` collapse to the boolean path; tmux's branch was not walked |
| Per-provider `permission_mode` defaults | ACP client silence is ✅. Whether Claude/Codex presets disable permission inside the CLI was not enumerated |
| Beads standalone (`gastownhall/beads`) | used through Gas City's `bd` integration and docs. The beads repo was not cloned |
| Wasteland, Gas Town by Kilo | out of this pass. Still ⚠️ in [`gas-town/99`](../gas-town/99-sources.md) |
| Cost, throughput, conflict rates | not measured |
| History before `3ef7fadd42` | shallow clone. Drift inside the Gas City repo was judged from in-file "last verified" dates plus the current tree, not from a bisect |

## D. Method note

Same rule as the Gas Town study: read source, not the announcement. Three consequences:

- The orientation doc's "zero roles" was checked against `builtinpacks` and the core pack, and
  narrowed.
- The glossary's per-rig database was checked against `beads-topology.md` and
  `issue_prefix` / `endpoint_origin` in code, and marked stale.
- The formula spec's "orchestrator executes control beads" was checked against `ProcessControl`
  and against `control-dispatcher`'s start command, and split into "no model" versus "no process".

## E. Cross-references into this repository

- [`PURPOSE.md` §0.4](../ai-workflow/memory/active/PURPOSE.md) — why this study was admitted
- [`gas-town/99-sources.md`](../gas-town/99-sources.md) — this pass closes that file's "Gas City not read" row
- [`04-orchestration-techniques.md`](04-orchestration-techniques.md) Part B — planes, gates, false checks
- [`ai-workflow/wiki/concepts/multi-agent-orchestration.md`](../ai-workflow/wiki/concepts/multi-agent-orchestration.md)
- [`ai-workflow/wiki/concepts/approval-gate.md`](../ai-workflow/wiki/concepts/approval-gate.md) §7.7 — ACP permission unanswered
- [`ai-workflow/wiki/concepts/control-plane-execution-plane.md`](../ai-workflow/wiki/concepts/control-plane-execution-plane.md) §5.6 — city-write grants are a different door
