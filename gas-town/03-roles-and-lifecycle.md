# 03. Gas Town — roles, lifecycle and recovery

> Read from `gastownhall/gastown` @ `649b832b76`. `docs/concepts/{polecat-lifecycle,heartbeats,convoy}.md`,
> `docs/design/mail-protocol.md`, `docs/design/convoy/mountain-eater.md`, `internal/deacon/`. MIT.

## 1. The supervision tree

```
                    Overseer (human)
                          │
                       Mayor            ← town: decompose intent, create convoys, dispatch, notify
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
     Deacon             Boot              Dogs        ← town: watchdog + its own watchdog + maintenance
        │                               (checks Deacon)
        │ (patrol)
   ┌────┴────┐
   │         │
Witness   Refinery     ← rig: supervise workers / serialize merges
   │
Polecats  (crews)      ← rig: ephemeral-session workers / human workspaces
```

The line that matters is **Mayor → (Deacon, Dogs)** vs **Witness → (Polecats, Refinery)**.
Cross-*rig* coordination and within-*rig* supervision are different jobs with different failure
modes, and Gas Town gives each its own agent. A rig can be entirely dead and the Mayor still
coordinates; a Deacon can be flapping without any worker noticing.

**Boot is the part most systems skip.** It is a Dog whose only job is to check that the Deacon is
still watching (on a ~5 min cadence). The argument is general: *the supervisor's liveness is its
own failure mode, and it needs a supervisor.* Every orchestrator that monitors workers eventually
needs something that monitors the monitor, or it has an unfalsifiable claim of health.

## 2. The polecat state machine

`docs/concepts/polecat-lifecycle.md`. Five states, and the transitions are what make the fleet
legible:

| State | What it means | How it arises |
|---|---|---|
| **Working** | actively executing, hook set | normal after `gt sling` |
| **Idle** | spawned, unassigned, safe to hand work to | on spawn / explicit prep |
| **Done** | work finished, **session retired** | after `gt done` |
| **Stalled** | should be working, stopped | crashed / interrupted / timed out |
| **Zombie** | work done but exit/cleanup failed | `gt done` itself failed |

The happy path is deliberately *not* a pool: `IDLE → WORKING → DONE`, no return to idle. This is
the **retired completion model** — a finished worker's session is retired (branch and MR evidence
preserved, session killed), while its *identity* persists for its work history. An idle pool of
half-used sessions was found to accumulate state and confusion; clean completion retires the live
session instead.

**Zombie** is the state most orchestrators lack, and it is the interesting one: the work is done
but the agent could not stand down. That is the seam where a supervisor has to decide between
"retry" and "force cleanup," and having it named makes it observable.

## 3. Heartbeats — and the false-positive lesson

There are **three** heartbeat stores, with different readers (`docs/concepts/heartbeats.md`):

1. **Deacon file** — `<town>/deacon/heartbeat.json`, read by the stuck-agent-dog plugin and the
   Go daemon (thresholds: 5 min stale / 20 min very-stale).
2. **Session store** — per-session state, written by `gt heartbeat --state=…`, read by the
   Witness. This is a **self-reported** state, not a liveness inference.
3. **Agent-bead label** — `heartbeat:<epoch>` on the agent bead, read by Witnesses watching the
   Deacon ("who watches the watchers"). Known gotcha: a session that never reaches `await-signal`
   leaves this stale for hours even though it is healthy.

The rule the doc lands on is the transferable one:

> **Never declare an agent stuck from a single store.** A live session with a stale store is
> *heartbeat-write divergence*, not a stuck agent. Cross-check tmux activity before escalating.

This is the same species of bug as this repository's four false "0"s
([`SYNTHESIS.md` §7](../SYNTHESIS.md)): a liveness signal that depends on a *delivery* that can
itself fail will, given enough fleet size, lie — and the recovery it triggers (kill, re-dispatch)
can be more damaging than the fault it was watching for. The design answer is not a better
heartbeat; it is **two independent channels and a documented tolerance for disagreement.**

## 4. The mail protocol — roles bound into a workflow

`docs/design/mail-protocol.md`. Inter-agent messages are `type=message` beads routed by `gt mail`.
The message set *is* the control flow; each has a fixed route, subject and body format:

| Message | Route | Trigger | Handler action |
|---|---|---|---|
| `POLECAT_DONE` | Polecat → Witness | `gt done` | Witness creates a cleanup wisp |
| `MERGE_READY` | Witness → Refinery | after verifying a polecat | Refinery enqueues the merge |
| `MERGED` | Refinery → Witness | merge committed | Witness nukes the polecat worktree |

The design point is that **the state machine is expressed in durable messages, not in any agent's
head.** Each hop is auditable in the ledger ("did the refinery ever see MERGE_READY?"), and any
hop can be re-driven because the message is still there. This is event sourcing with a
role-shaped vocabulary — and it is why a crashed agent mid-workflow does not lose the workflow.

## 5. Convoy → swarm → the "mountain"

A **convoy** is a persistent tracker over a set of beads; the **swarm** is just the workers
currently on those beads (no object, no ID). A **stranded convoy** is one with ready work but no
workers assigned — the signal that something upstream failed.

`docs/design/convoy/mountain-eater.md` is the most interesting design document here, because it
adds a **judgment layer** on top of the mechanical convoy feed, and its stated reason is worth the
whole read. Large epics "get stuck at 40% with no indication of why," because:

> The ConvoyManager is mechanical. It feeds the next ready issue when one closes, but it cannot
> reason about failure patterns, make skip decisions, or escalate intelligently. When a polecat
> fails repeatedly on the same issue, the mechanical system re-slings it endlessly.

And the fix is stated as a design principle:

> **No agent holds the thread.** … The epic IS the thread. The beads ARE the state. No agent needs
> to remember anything. Each check discovers state fresh.

The word they use for the failure is **hysteresis**: any agent maintaining an "I'm driving this
epic" loop loses that thread at context compaction, and the re-primed agent does not remember it
even with the epic still hooked. So instead of a persistent coordinator, **a stateless judge
(layered as Dogs/agents) re-reads the ledger on each patrol and decides**: skip-after-N-failures,
escalate, or continue. The outcome is the same whoever checks, because the *state* is in the beads
and the *criteria* are in the formula — that is what the repo calls **NDI, Nondeterministic
Idempotence**: the path varies, the criteria are fixed, the outcome converges.

This is, in this repository's terms, the orchestration-layer answer to the **context-window drift**
problem it has documented repeatedly — a coordinator's plan does not survive compaction, so the
plan is externalized to a ledger and the coordinator becomes replaceable.

## 6. The full happy path, end to end

Read off the docs (MEOW + convoy + mail + propulsion):

```
1. Tell the Mayor          "ship the auth refactor"          → it decomposes into beads
2. Mayor creates a Convoy  grouping the beads, notifies you   → convoy hq-cv-* persists
3. gt sling                beads land on polecat hooks        → scheduler may defer by capacity
4. gt sling → spawn        a polecat gets a worktree+branch   → session, agent bead, hook
5. gt prime                the hook + formula checklist print → propulsion begins
6. work the molecule       steps, inline (root-only wisp)     → bd close <step> --continue
7. gt done                 branch pushed, POLECAT_DONE sent   → session retires
8. Witness verifies        MERGE_READY → Refinery             → merge slot taken, merged
9. MERGED → Witness        evidence preserved, worktree freed → convoy closes, you notified
```

Every step is a durable artifact. Nothing in that chain depends on an agent remembering the
previous step across a restart — which is the entire point.

## Read next

- [`04-orchestration-techniques.md`](04-orchestration-techniques.md) — the reusable techniques,
  cross-referenced against this repository's Codex / Strands / ACP findings.
- [`99-sources.md`](99-sources.md).
