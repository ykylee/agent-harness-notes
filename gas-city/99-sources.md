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
| [`gastownhall/gascity`](https://github.com/gastownhall/gascity) @ **`3ef7fadd42b44d6d902bc135bd8d9aa1d5fce7ce`** (2026-09-30, `#6879`), MIT, Go 1.26.6. Shallow clone; tag `edge` on that commit is a moving tag, not a release pin | the whole study | ✅ source. **Drift re-check 2026-10-20 → `6aa6be55d` (838 commits): [§F](#f-drift-re-check-2026-10-20--3ef7fadd42--6aa6be55d)** — one refutation (F.1), one upstream reversal (F.2), the rest holds |
| `docs/getting-started/how-gas-city-works.md` | six primitives, machinery vs primitives, prefix-isolation claim | ✅ first-party, claim checked |
| `docs/getting-started/coming-from-gastown.md` | role translation table, "zero roles", what not to port | ✅ first-party |
| `docs/reference/specs/formula-spec-v2.md` | v1/v2 peer contracts, control vs work beads | ✅ spec; switch re-read in code |
| `docs/reference/internal/beads-topology.md` | one Dolt server, `issue_prefix`, `inherited_city` | ✅ first-party; keys re-read in `internal/beads/contract/files.go`. ⚠️ its "prefix scoping enforced at the `bd` query layer" sentence is contradicted by Beads and by Gas City's own read store (2026-10-19, [§C](#c-not-verified-here-)) |
| `docs/reference/trust-boundaries.md` | trusted config vs untrusted bead text; ambient secret strip | ✅ first-party |
| `docs/guides/understanding-formulas.md` | which contract to choose; `gc converge` still v1-only | ✅ first-party |
| `internal/config/config.go` `Agent`, `DaemonConfig.FormulaV2Enabled` | no role enum; formula v2 default on | ✅ source |
| `internal/beadmeta/values.go`, `kindsets.go` | `ControlKinds` | ✅ source |
| `internal/dispatch/runtime.go` `ProcessControl` | one case per control kind; skip when status ≠ open | ✅ source |
| `internal/dispatch/control.go` | retry / ralph attempt loop | ✅ source (header and strategy) |
| `internal/runtime/liveness.go` | `Liveness`, `ObservationIncomplete` | ✅ source |
| `internal/runtime/acp/cutover.go`, `acp.go` `Pending`/`Respond`/`SetMeta` | three-outcome passthrough; permission unsupported; sidecar threat comment | ✅ source at the pin. **Reversed upstream 2026-10-11** (#6598): `Pending`/`Respond` moved to `acp/permission.go` and now hold and answer `session/request_permission` — [§F.2](#f2-upstream-reversal--the-acp-provider-answers-the-permission-rpc-since-2026-10-11). Passthrough and sidecar comment unchanged |
| `internal/runtime/acp/protocol_conformance_test.go` `TestACPProtocolPermissionTimeoutRejects` | no client reply to `session/request_permission` | ✅ source (test) at the pin. **Deleted 2026-10-11**; five permission tests now assert exactly one client reply ([§F.2](#f2-upstream-reversal--the-acp-provider-answers-the-permission-rpc-since-2026-10-11)) |
| `internal/orders/triggers.go` `CheckTriggerWithOptions` | cooldown, cron, condition, event, manual, webhook | ✅ source |
| `internal/beads/class_store.go` | typed class wrappers over `Store` | ✅ source |
| `internal/citywriteauth/doc.go` | verify-only ed25519 city-write grants | ✅ source for the package. ❌ the sentence this study derived from it — "ships no minter; bundled clients send only CSRF" — was **wrong at the pin** ([§F.1](#f1-refutation--the-grant-minter-and-the-client-grant-path-existed-at-the-pin)) |
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
| Beads standalone (`gastownhall/beads`) | **Read 2026-10-19** @ `4f9174e6b` (clone at `~/repos/harness-refs/beads`, Go, read-only, `bd` not run). Findings: (1) **the prefix filter in [02](02-architecture.md) §2 / [04](04-orchestration-techniques.md) A4 is not a Beads property** — `issue_prefix` only generates ids and names the per-project database; ❌ corrected in both documents. The claim traces to Gas City's own `docs/reference/internal/beads-topology.md:9,85-90` ("prefix scoping enforced at the `bd` query layer"), which Gas City's code contradicts too: `internal/beads/doltlite_read_store.go:125-142` resolves one database **per scope** from `metadata.json` (`dolt_database` → `database` → `"hq"`). A first-party doc page, refuted by first-party source on both sides — the [§A](#a-primary-sources--read-directly-) row for `beads-topology.md` is downgraded from ✅ to ⚠️ for its filter sentence (its config keys were re-read and hold). (2) **Formula v2 and control vs work beads are Gas City's** — Beads' `internal/formula` is v1 only (`types.go:85 Version int // (currently 1)`), `gc.kind`/`formula_compiler` 0 hits; ✅ confirms [99 §A](#a-primary-sources--read-directly-) row 1. (3) **The forgeable ledger is a Beads property**: `internal/httpapi/claim.go:48-58` "The actor is caller-ASSERTED provenance for the audit trail and is NOT the authenticated principal … The CAS is therefore a correctness fence against CONCURRENT claims, not an authorization boundary"; `SECURITY.md:160-162` "No built-in encryption or access control"; `PROJECT_CHARTER.md:29-42` excludes orchestration policy by design. (4) Orchestrator types (`convoy, merge-request, slot, agent, role, rig`) "were removed from beads core" (`types.go:799-806`); `role_bead`/`hook_bead`/`rig` survive as schema columns only (`0001_create_issues.up.sql:45-50`). (5) Beads has its own merge slot (`internal/storage/merge_slot.go`, label `gt:slot`, Metadata JSON, check-and-set in a transaction). (6) `bd serve` auth is a shared bearer token for the whole surface, loopback unauthenticated; CAS `--if-assignee/--if-status/--if-revision` exists (exit 13); versioned write paths are post-hoc audit, hooks fire after commit. Not read: Dolt storage internals, federation docs beyond the overview, `CHANGELOG.md`. **Drift 2026-10-20 → `d0d9aa214`** (9 commits, 103 files, no clone — GitHub compare API): tags `v1.3.1` and `v1.3.2-rc.2` appeared (the `bd` 1.3.0 that [`gas-town/05`](../gas-town/05-runtime-observation.md) refused for schema skew is no longer the newest); files are `cmd/bd` tests and perf (59), `internal/httpclient` (connect-failure naming, cached external-dependency policy), `internal/configfile` (#7671: a `graph_mode` forward-compatibility **fence** — `dependency` default, `link` recognised, anything else refuses the workspace; *"no graph code, no `--graph-mode` flag"*), `internal/storage/externaldeps`. **`claim.go`, `SECURITY.md`, `serve.go` and the migrations are not in the range**, so findings (3)–(6) stand unread. Next baseline **`d0d9aa214`**. Gas City consumes Beads as the Go module `github.com/steveyegge/beads` (`go.mod:27`, `v1.3.1-rc.2` at `3ef7fadd42`, **`v1.3.1`** at `6aa6be55d`; no vendor, no embed) **and** as the operator-installed `bd` subprocess (`BdStore`), with a read-only SQLite path over bd's doltlite file as a third route — §F.3 |
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

## F. Drift re-check 2026-10-20 — `3ef7fadd42` → `6aa6be55d`

**838 commits** (2026-09-30 → 2026-10-20 04:30 UTC), 3,622 files, +655,470 / −45,135. By scope:
controller 160, session 73, bazel 54, reconciler 51, beads 46, api 23, runtime 21, tmux 21,
dispatch 17, dolt 13, acp 7. No release tag contains the pin or HEAD (`edge` only; `v1.5.0`,
2026-10-04, sits on a release line; `v1.4.2` is the last common ancestor tag). `go 1.26.6 → 1.26.9`.
Method: fresh `--filter=blob:none` clone at `~/repos/harness-refs/gascity`; every path cited in
[§A](#a-primary-sources--read-directly-) was classified (exists / changed / renamed) and the 34
claims were re-read at HEAD in four clusters (ACP + liveness, dispatch + config + formulas + packs,
beads topology + trust + city-write auth, controller + reconciler), each with `git show` at both
revisions. Nothing was executed. Of the first-party docs this study leaned on, `beads-topology.md`,
`coming-from-gastown.md`, `how-gas-city-works.md`, `trust-boundaries.md`, `understanding-formulas.md`,
`glossary.md`, `health-patrol.md` and `formulas.md` are **byte-unchanged**; the code under them is not.

| Claim (as graded in §A / [04](04-orchestration-techniques.md)) | At `6aa6be55d` |
|---|---|
| `config.Agent` has no role enum; `FormulaV2Enabled` default on | ✅ field set byte-identical (`config.go:3484`; `:5134-5136`) |
| `ControlKinds` = 8; `ProcessControl` one case per kind, skip when not open; retry/ralph loop | ✅ (`kindsets.go:35-44`, `dispatch/runtime.go:179-231`); ⚠️ a pre-switch `closeOrphanedControl` step (`:203`) and `SelfClosingControlKinds` (`control_close.go`) were added; no new attempt caps |
| Control beads run with no model but in a process (`control-dispatcher`, `gc convoy control --serve`) | ✅ verbatim (`agents/control-dispatcher/agent.toml` zero diff); now resolved per scope (`graphroute.go:353-360`) |
| Built-in packs core / bd / dolt / gastown / gascity; claim protocol `ga-tmzjx6`; Gastown import pin `33d3a430` | ✅; ⚠️ new **subpack** `gc-roles` (parent `gascity`, `registry.go:209-216`), not a sixth pack; the `examples/gastown/pack.toml` +2/−2 are the core/bd pins (`f895c0ff` → `e38ce9cc`), the gastown pin is unchanged |
| `gc converge` is v1-only | ✅ (`convergence_store.go:197-198`) |
| Trigger kinds cooldown/cron/condition/event/manual/webhook | ✅; +2 lines = `clock.Backstop` floor on cooldown |
| One database per scope from `metadata.json`; `issue_prefix` mints ids only; no prefix query predicate | ✅ (`doltlite_read_store.go:126-143`; the §2/A4 cite of 125-142 is now 126-143); ⚠️ addendum: Gas City does apply **client-side** prefix fences — cache event ownership (`caching_store.go:741-754 ownsBeadID`), pinned-id namespace (`pinned_id_fence.go:42-53`), relocation routing, `ProxiedPrefixAgreement` — all present at the pin, none a SQL predicate, none server-side, none a grant |
| `beads-topology.md` still says "hard query filter" | ✅ byte-unchanged (`:8-10`, `:85-90`, `:138-146` incl. a mermaid `WHERE id LIKE 'riga-%'`); doc rot unchanged |
| Ambient secret strip (`execenv.IsSensitiveKey` / `FilterInherited`) | ✅ unchanged; call sites survive (`bd_env.go:2472,2532`) |
| `citywriteauth` verify-only; fail-closed when a key is configured; not installed otherwise | ✅ package unchanged (`api/writeauth.go:24-26,160-171`); the derived sentence is ❌ — F.1 |
| Three-outcome liveness; `ObservationIncomplete` passthrough in the ACP and subprocess seams | ✅ and **strengthened** (`acp/cutover.go:138-142`, `subprocess/cutover.go:75-79`, `liveness.go:150-154`) — F.3 |
| ACP `Pending`/`Respond` return `ErrInteractionUnsupported`; `TestACPProtocolPermissionTimeoutRejects` | ❌ at HEAD, **correct at the pin** — F.2 |
| README: providers, "tmux still required", file-beads provider | ✅ byte-stable (`README.md:38,65,71-72`); only bd 1.0.0 → **1.3.0** in the prerequisites table |
| Tick phases (02 §4), orders lane separate, crash quarantine in memory | ✅; phases are now a named table (`city_runtime.go:1330-1357`), orders lane paced by a shared `startPacedLane` (`lane_pacing.go:28`) |

### F.1 Refutation — the grant minter and the client grant path existed at the pin

[02](02-architecture.md) §6.1, [04](04-orchestration-techniques.md) A5 and
[`wiki/control-plane-execution-plane`](../ai-workflow/wiki/concepts/control-plane-execution-plane.md)
§5.6 said the city-write package "ships no minter" and that "the bundled API client and dashboard send
only a CSRF header, so turning the gate on rejects those first-party clients". The *package* sentence
is true; the *clients* sentence was false at `3ef7fadd42`:

- `cmd/gc-write-mint/main.go:1-16` (present at the pin) is "the reference `X-GC-City-Write` grant
  minter for a direct hardened city … a re-validating signer, not a blind oracle: the signing key
  never enters gc … a dev/reference tool and deliberately lives outside the verify-only
  `internal/citywriteauth` package".
- `internal/clientgrant/clientgrant.go:1-15` (present at the pin) runs a context's configured
  `grant_command` once per mutation, handing the request binding as JSON in `GC_GRANT_INFO` (never
  argv), and the Go API client attaches the result automatically (`internal/api/client.go:305-309`
  and `:1556` at the pin; `cmd/gc/remote_client.go:103-121` wires `clientgrant.NewGrantSource` for a
  context that sets `grant_command`).
- The **dashboard** sends no grant (no `X-GC-City-Write` in any `.ts`/`.tsx` at either revision).

Corrected statement: the supervisor only verifies; signing is out-of-tree *by contract*, with an
in-repo reference signer; a `gc` CLI context with `grant_command` passes the gate, the dashboard does
not. The structural finding — the grant covers city-config HTTP mutations and never `bd` writes — is
unchanged. How the error happened: `doc.go` was read and generalised to "the clients"; `cmd/` was not
listed. The method rule is the one in [`SYNTHESIS`](../SYNTHESIS.md) §7: a package's self-description
bounds the package, not the repository.

### F.2 Upstream reversal — the ACP provider answers the permission RPC since 2026-10-11

Commit `ee24a477c` (#6598, "serve `session/request_permission` via `Pending`/`Respond` and answer other
agent requests with `-32601`"). At HEAD:

- `internal/runtime/acp/agent_requests.go:75-81` routes `session/request_permission` to
  `holdPermission` (`permission.go:211`: recorded **without replying**; everything else gets JSON-RPC
  `-32601`, and a request with no options or a wrong session gets `-32602`).
- `permission.go:474 Pending` reports the oldest unanswered request as an approval interaction;
  `:493 Respond` maps `approve / approve_always / deny / deny_always` to `allow_once / allow_always /
  reject_once / reject_always` (`:39-44`) and writes the reply on the wire; `cancel`, interrupt, the
  agent's own `$/cancel_request` and the end of the turn all answer `{"outcome":"cancelled"}`
  (`:372-437`). A nudge is refused while a permission is pending (`ErrNudgeRefusedPendingInteraction`).
- Who answers: the HTTP API (`internal/api/handler_session_interaction.go:205`,
  `huma_handlers_sessions_command.go:1198`), `gc session respond` (`cmd/gc/cmd_session.go:1362`), the
  status provider and the worker handle. **No auto-approve exists in gc**: the only `approve_always`
  strings are the `permission_mode` presets that configure the agent CLI itself.
- Tests: `TestACPProtocolPermissionTimeoutRejects` (pin `:312-325`, asserted an empty client-reply log)
  is deleted; `PermissionApproveRoundTrip` / `DenyStringID` / `CancelledOnInterrupt` /
  `CancelledWhenAgentCancelsRequest` / `CancelledWhenTurnEnds` (`protocol_conformance_test.go:398-487`)
  assert **exactly one** reply; `InitializeAdvertisesNoFSOrTerminal` (`:511`) pins
  `{"fs":{"readTextFile":false,"writeTextFile":false},"terminal":false}`.
- The same window made tmux approvals first-class: #6832 answers Claude prompts by menu label and
  returns `409 session-conflict` while one is pending; `5cf1f4580` never types into a pending prompt;
  `internal/pendingwatch` turns observed prompts into `session.pending` / `session.pending_cleared`
  events (exactly once) and the reconciler **holds lifecycle timers** while one is open.
- What did not move: `protocolVersion` 1 (`acp/protocol.go:70`, tests pin `1`); five `session/update`
  kinds decoded (`acp/conn.go:274,281`); zero hits for `notice` / `compaction` / `schema-v1` — the
  ACP spec's `schema-v1.25.0` promotions ([`agent-ux/10`](../agent-ux/10-acp.md) §1.1) are not
  reflected. Upstream carries its own stale comment: `internal/sessionlog/acp_wire_reader.go:615`
  still says both methods return `ErrInteractionUnsupported`.

Reading: Gas City is now a **relay**, not a gate — it surfaces the agent's request to a human or API
caller and forwards one decision, with timeouts resolving to `cancelled` rather than to an agent-side
reject. The [04](04-orchestration-techniques.md) Part B line "same shape as orchestrators launching the
wrapped agent with approval off" no longer describes it; the orchestrator still **decides nothing**.

### F.3 New in the range that this study's axes care about

- **Two new write paths into the bead ledger, and a first-party statement of the forgeable actor.**
  `internal/opjournal` (80 files; conversation *ops* and facts as beads of type `op` in the
  sessions-class store, `doc.go:15-21`; "the principal is a stable logical id, never a bearer,
  credential or box epoch; the actor is an open class string", `:138-139`; `[ops]` rollout gates
  `content | control | lifecycle = off | auto | require`, default **off**, `require` refuses a request it
  cannot record) and `internal/eventfact` (11 files; worker-site events become fact rows the
  controller projects into the city log) — whose `doc.go:12-13` says it in the project's words: *"under
  the user decision D-TRUST: until bd principals (BD-8) a fact's actor, subject and session are what
  the box asserts."* The [`gas-town/02`](../gas-town/02-architecture.md) §5 finding is now upstream text.
- **A per-session transport credential for `bd serve`.** `internal/connect` (#7837, #7930): a secret
  "connect bundle" handed to a box through the runtime provider, **HMAC-SHA256 per-box bearers**
  `gcb1.<session>.<generation>.<mac>` keyed by the city key (`bearer.go:70-78 MintBearer`), rendered
  into the `bd serve --auth-token-file` as operator lines + sentinel + one bearer per session row
  (`tokenfile.go:126-128`). This narrows "`bd serve` has one shared bearer" to *per session
  incarnation, revocable by re-render* in connect-enabled cities — a transport principal; the row-level
  actor stays asserted (above). `gc connect` (CN-2) and exec-provider minting (CN-3b) have **not**
  landed; `.gc/control-plane.toml` worker-site mode (#8003) is groundwork.
- **Writes to session rows are fenced.** v2 effects are CAS through the row's own census leg
  (#7286/#7300, "blind-write-refusing store"); CHANGELOG (Unreleased): the generic bead API returns
  **422** on session rows, mail, waits, nudges and order-run records — "a typed work bead carrying
  `gc:session` is written only by `bd`". #7783: only the controller's own cache closes are trusted,
  because `gc event emit bead.closed` could forge `execution.step_completed`. `[beads] ledger_feed =
  auto` tails the Dolt mutation journal so `bd`/human writes reach the cache in ~1 s (#7873);
  `native_transport = off|auto` decides whether gc opens the Dolt store in-process at all.
- **Reconciler v2 exists, is opt-in, and is off.** `[daemon] session_reconciler = legacy` (default) |
  `v2` ("refused in this build" per `docs/reference/config.md`; latched at boot,
  `cmd/gc/reconcile_mode.go:49-62`); `v2LatchRefusals` reject cities using `max_session_age`,
  `depends_on`, stall timeouts or chat auto-suspend. v2 classifies liveness five ways —
  `unknown / alive / occupied / gone / dead` (`allocator_observe.go:33-60`), "Unknown: Keep, and no
  grant" — and every destructive effect re-proves absence on a fresh read through every composite hop
  (#7346). Legacy gained `ServerDeathConfirmer` (`liveness.go:61-82`, tmux-only: `ErrRuntimeUnavailable`
  counts as gone only when the tmux leaf attests its server dead) and a fresh re-read before a heal.
  `engdocs/architecture/reconciler-v2.md` (added #6988) is **already stale**: it maps a P2 work-queue
  skeleton deleted by #7293 — cite commits, not that page.
- **An execution backstop with the false-zero lesson built in.** #7911/#7922/#7984: a seat holding a
  claim with no `execution.step_started` evidence gets 90 s → nudge → 3 min backoff ×3 → drain as
  `execution-stalled`; the incident that produced it was a seat **waiting on a human approval drained
  56 times**, so evidence is stamped on the row (`execution_claim_started = "<instance_token>|<bead>"`)
  and a pending approval vetoes the drain, not the nudge. `work_ladder = on` paces pool seats (nudges
  back off 3 → 60 min and never stop; a started claim is recycled once, then escalated).
- **Formula v2 spec +70 lines:** `opt_*` precedence (claimed bead → trigger bead → template), a hard
  failure (`gc.failure_class = hard`) ends the ralph loop, a check script that cannot be launched holds
  the step **open** with no attempt spent (`control.stalled` after 15 min), `<step>-fanout` converges
  spawned children, `abort_scope` carries `gc.failure_*`.
- **Beads floor.** Gas City 1.5 requires `bd` ≥ 1.3.0 (was 1.0.4; raw-SQL fallback deleted);
  `docs/getting-started/upgrading.md` has the operator migrate Beads schema v53 → v66 **manually** per
  city and rig or `bd` refuses writes (`table not found: leases`). This is the same skew
  [`gas-town/05`](../gas-town/05-runtime-observation.md) hit from the other side (vendored `bd` 1.0.5
  vs `bd` 1.3.0). API: +4 paths (`session/{id}/pin|unpin`, `work/active-step`, `work/ready`),
  schemas 577 → 627; `docs/reference/exec-session-provider.md` +304 (cancellation, idle sleep, fenced
  input, work-dir export exclusions, session identity); `work_dir_exclude` keeps controller state and
  secrets out of exported work dirs (#7600).

### F.4 Not read, and the next baseline

Not read: `cmd/gc` beyond the files above (559 new files, mostly `reconcile_*` / `allocator_*` and
simulator tests), `internal/session` (+28.7k lines), `internal/api` handlers beyond the interaction
path, `tools/`, CI. Runtime behaviour: still not run ⚠️. **Next drift baseline: `6aa6be55d`.**
The clone stays at `~/repos/harness-refs/gascity`.
