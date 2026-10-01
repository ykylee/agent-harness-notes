# 03. Gas City — roles, lifecycle, and liveness

> Read from `gastownhall/gascity` @ `3ef7fadd42`. The role map is
> `docs/getting-started/coming-from-gastown.md`. The state machine is
> `cmd/gc/session_reconciler.go` as described by `engdocs/architecture/health-patrol.md` and
> checked against `internal/runtime/liveness.go`.

## 1. There is no role taxonomy in the platform

Gas Town's taxonomy ([`gas-town/01`](../gas-town/01-vocabulary.md) §2.2) is a table of types.
Gas City's equivalent table is a **translation guide**, and every right-hand cell is
configuration:

| Gas Town role | Where the behaviour went |
|---|---|
| Mayor | A pack agent with a coordinating prompt. The Gastown pack still names it `mayor`. `gc session attach mayor` |
| Deacon | Controller health patrol and thresholds. A configured agent is optional |
| Witness | Events, waits, session scale, wake/sleep. A "witness" agent is optional |
| Refinery | A formula or order step. Not a standing platform role |
| Polecat | An agent with `min_active_sessions` / `max_active_sessions` and usually a worktree. An operating style |
| Crew | A persistent named agent. An operating style |
| Dog | Usually an exec order. The Gastown pack's `dog` pool covers the residue that needs a model |

The platform instantiates an agent from `config.Agent`. Scope `city` means one per city. Scope
`rig` means one per rig. Unset means both expansion contexts. Pools size themselves from
`scale_check` (a shell command whose output is a count), bounded by `max_active_sessions`, with
`min_active_sessions` as a floor. Sessions are disposable. The beads they closed are not.

`coming-from-gastown.md` says path-derived identity must not be ported. `dir` carries scope.
`work_dir` is set only when the session has to run somewhere other than the rig root. That is
the lifecycle consequence of [`01`](01-vocabulary.md) §6.

## 2. The Gastown pack is still the example, and it is bundled

`examples/gastown/pack.toml` imports `gastown` from `gascity-packs` at `sha:33d3a430…` and then
patches `mayor`, `deacon`, and `boot` with `max_session_age = "6h"`. The comment is operational,
not theatrical: those sessions are long-lived Claude TUIs, idle detection has regressed before
(`ga-07mi8`, PR #5468), and a wall-clock cap also refreshes a credential cache around eight
hours. The witness in the pack already had a 5h cap; these three did not.

`builtinpacks` embeds that pack in the `gc` binary so `gc init` can resolve it offline. Roles
are data. The data is on by default if you install the Gastown-shaped city. A city that never
imports the pack does not have a mayor, and the orchestrator does not notice.

## 3. Reconciliation

`reconcileSessionBeads` compares the desired set from config with `ListRunning()` plus liveness:

| State | Action |
|---|---|
| Not alive, should be | Start |
| Alive and desired, fingerprint matches | Skip |
| Not desired (orphan, pool excess, suspended) | Drain, or kill if it is a true orphan |
| Config fingerprint differs | Drain and restart |
| Self-requested restart (context exhaustion) | Stop and start |
| Idle past the opt-in timeout | Stop, emit `session.idle_killed` |
| Crash-loop quarantined | Skip until the in-memory window expires |

Zombie capture, in the health-patrol note: the session exists and the process inside it is dead.
The controller peeks pane output for forensics, then restarts. That is the same *word* as Gas
Town's Zombie (work done, could not stand down) and not the same state. Do not merge the two
tables.

On orchestrator restart the orientation doc says live sessions are **adopted**: a session bead is
created for each, rather than respawning them. That adoption is why liveness has to be honest.
Killing a session the probe merely failed to see is the failure mode the next section exists to
prevent.

## 4. The claim protocol

The core pack fragment `template-fragments/claim-protocol.template.md` is the startup contract,
and it is stricter than the slogan:

```bash
gc hook --claim --drain-ack --json
```

- Result `work`: read that bead and run it.
- Result `drain`: the session is done. Exit.

The fragment forbids `gc bd list --assignee=…` and `gc bd ready`. Pool work is invisible to those
queries twice: an unclaimed routed item has no assignee, and a wisp is hidden by default. The
named failure is a scheduled maintenance order that sat 41 hours (`ga-tmzjx6`) because a worker
reported "no work" while its wisp was open.

`config.Agent.Nudge` has a fallback that types the same command into a known pool session whose
trigger is still unclaimed after 90 seconds, when nudge text is empty. The obligation is no
longer only a sentence in the prompt. The platform will paste the command.

This is Gas Town's propulsion (GUPP), moved from "look at your hook" to "call this one command,
because the obvious queries lie." [`gas-town/04`](../gas-town/04-orchestration-techniques.md) A4
said the rule is unenforceable without a durable hook. Gas City's addition is that the durable
thing is not enough if the worker is allowed to query around it.

## 5. Three-outcome liveness

HEAD's own commit is this fix. `runtime.Liveness` is two booleans, `Running` (provider runtime
present) and `Alive` (configured agent process present). That pair is not the third outcome.

The third outcome is `ObservationStatus`:

| Status | Meaning |
|---|---|
| `ObservationComplete` | The provider answered inside the bound. The `Liveness` value may be trusted |
| `ObservationIncomplete` | The provider returned `ErrRuntimeUnavailable`, or the bound expired first. **The accompanying liveness must not be treated as confirmed absence** |

`ObserveLivenessBounded` races the probe against a timeout. A real answer that arrives as the
bound expires is kept. Discarding it to report "incomplete" would fail in the wrong direction.
A cancelled parent context returns incomplete without probing.

ACP and subprocess adapters (`internal/runtime/acp/cutover.go`, `internal/runtime/subprocess/cutover.go`)
pass `ObserveLivenessWithError` through a seam that otherwise exposes only a boolean. The tests
say what the seam used to do: it lost the three-outcome result. Listing has a matching honesty
bit, `ListRunningComplete`, so a partial list is not reported as the full set of live sessions.

This is the same rule as Gas Town's two heartbeat channels, stated at the probe:

> A failed observation is not a dead worker. Escalating on it restarts a session that may be fine,
> and the recovery can exceed the fault.

Gas Town cross-checked two stores because one store can go stale. Gas City refuses to collapse
"probe failed" into "not running" because the boolean API already did that. Both are instances
of the false-zero rule in [`SYNTHESIS.md`](../SYNTHESIS.md) §7.

## 6. ACP transport, permission unanswered

`internal/runtime/acp` implements the provider seam over ACP JSON-RPC: start a process, send
`session/prompt`, read `session/update` into the peek buffer.

`Pending` and `Respond` return `ErrInteractionUnsupported`. The comment says ACP "only tracks
whether an outbound prompt is in flight" and that busy state is not a user-facing blocking
interaction. Structured permission is not surfaced.

`TestACPProtocolPermissionTimeoutRejects` states the consequence in a comment and asserts it:

> gc on this base does not answer `session/request_permission`, so the fake's timeout path fires:
> `$/cancel_request`, then a rejected tool.

The test expects the peek buffer to contain `permission rejected`, and `responses.jsonl` to
contain **no client replies**.

So a Gas City ACP session can host an agent that speaks the permission RPC, and the orchestrator
will not answer it. The agent's own timeout then rejects the tool. That is not an approval gate
implemented elsewhere. It is the gate left unanswered. Whether a given provider preset bypasses
permission inside the agent CLI (a `permission_mode` option default) is a separate config fact
and was not enumerated agent by agent in this pass ⚠️.

## 7. What still has a lifecycle, and what does not

| Thing | Lifetime |
|---|---|
| Agent definition | Durable, in a pack or `city.toml` |
| Session | Disposable. Adopted on restart if still alive; otherwise started to match desired state |
| Work bead | Durable. Survives the session. Ready when blockers close |
| Control bead | Durable, orchestrator-owned. Not a thing an agent should mark in progress |
| Wisp | Ephemeral molecule. Closed, then GC'd past TTL |
| Crash quarantine counter | In-memory. Reset when the controller restarts |
| Order cursor / last-run | Durable enough that a tick does not re-fire; a tracking bead is created synchronously before dispatch |

There is no polecat state machine in platform code (Working / Idle / Done / Stalled / Zombie as
Gas Town defines them). Those words, where they appear, are either the Gastown pack's prompt or
a different mechanism that reused a word (zombie capture, idle kill). The decision procedure for
"stuck" is the reconciler plus three-outcome liveness, not a bead status enum.
