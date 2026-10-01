# 04. Gas City — orchestration techniques, and where they meet this repository

> The purpose of this file is the same as [`gas-town/04`](../gas-town/04-orchestration-techniques.md):
> a reference for orchestration technique. Gas Town recorded eleven moves from one operating
> model. This file records what changes when that model is extracted into a platform, and what
> this repository's existing evidence does with the change.
>
> Read from `gastownhall/gascity` @ `3ef7fadd42`. Nothing was executed.

---

## Part A — What is new relative to Gas Town

Gas Town's A1–A5 still apply: externalize the plan, split identity from session, serialize the
dangerous shared resource, make the first action mandatory, verify liveness on more than one
signal. The techniques below are the ones Gas City adds or sharpens. They are not a replacement
list.

### A1. Put judgment in the pack and control flow in the bead kind

**The technique.** The orchestrator executes a closed set of control kinds (`retry`, `ralph`,
`check`, `retry-eval`, `fanout`, `drain`, `scope-check`, `workflow-finalize`) by switching on
`gc.kind`. Agents claim plain work beads. A role is a `config.Agent` plus a prompt template.
The glossary rule is "keep judgment out of Go."

**Why it transfers.** Gas Town hardcoded the supervision tree in the binary (Mayor, Deacon, Boot,
Witness, Refinery). That tree is one useful operating model and a bad type system: every new
behaviour wanted a new role. Gas City's split is the reusable part. **Policy that is a graph
(retry, fan-out, drain, finalize) is data the dispatcher runs. Policy that is a judgement is a
prompt. Policy that is a shell command is an exec order, and does not get an agent.**

**Caveat.** The bundled core pack still ships a `control-dispatcher` session, and the bundled
Gastown pack still ships the old names. "Zero roles" describes the type system. The product
people install can look exactly like Gas Town. Also, control beads are forgeable by anything
that can write the store: a worker that flips one to `in_progress` strands the graph
(`ga-fw2fm`). The split only works if workers cannot write control state. That is the credential
finding again, one level down.

### A2. A failed observation is not absence

**The technique.** `ObserveLivenessBounded` returns `ObservationIncomplete` when the probe errors
with `ErrRuntimeUnavailable` or the timeout wins, and that result must not be read as "the
session is gone." ACP and subprocess seams pass the three-outcome value through; a boolean seam
used to drop it. `ListRunningComplete` is the same honesty for lists.

**Why it transfers.** This is Gas Town A5 (two channels) plus this repository's false-zero rule,
at the probe API itself. The boolean `IsRunning` is documented as insufficient. Collapsing
"could not look" into "not there" is how a reconciler restarts a live worker.

**Caveat.** Providers that do not implement `LivenessObserverWithError` still resolve to
`ObservationComplete` with the legacy boolean. The third outcome is opt-in per provider. tmux's
behaviour under that fallback was not re-derived line by line in this pass ⚠️.

### A3. The claim is a command, because the obvious query lies

**The technique.** Workers must call `gc hook --claim --drain-ack --json` and must not invent a
`bd ready` / `bd list --assignee` lookup. Wisps are hidden. Unclaimed pool work has no assignee.
A nudge fallback pastes the hook command when a pool session sits unclaimed for 90 seconds.

**Why it transfers.** Propulsion (Gas Town A4) fails in a specific way once work is routed
through a pool: the worker checks the query a human would check, reports idle, and the order
waits (41 hours, `ga-tmzjx6`). The fix is to make the legal lookup a single command whose
implementation is allowed to be hundreds of characters of shell, and to forbid the shortcut in
the prompt the agent actually sees.

**Caveat.** The forbid is a prompt plus a nudge. A model can still run `bd ready`. The platform
cannot see that it did, except by the work remaining unclaimed. This is an obligation, not a
sandbox.

### A4. One ledger, prefix filters, not a database per project

**The technique.** One Dolt server per city. Each rig inherits the endpoint and carries an
`issue_prefix` that `bd` applies as a hard filter. Agents in rig A cannot see rig B's ids.
Cross-rig work is an explicit route (`routes.jsonl`, `gc bd --rig`), not an accidental join.

**Why it transfers.** Gas Town's two-level split (`hq-*` at town, project prefix at the rig) was
the same idea with a directory tree as the architecture. Gas City keeps the prefix and drops the
requirement that the directory tree *be* the design. Isolation is a query predicate. A second
server per repo buys operational cost and does not buy a stronger boundary than the filter,
unless the server is the trust boundary — which, if workers share a Dolt credential, it is not.

**Caveat.** Class stores (work vs graph vs mail) may still be separate backends, with
`gc.source_store_ref` crossing them. "One ledger" is the default rig topology, not a promise
that every bead class shares a file. And a prefix filter enforced in the client (`bd` reading
local `config.yaml`) is not a server-side grant. A client that skips the filter sees every row.
That is a client convention, graded as such.

### A5. Config is code; bead text is data

**The technique.** Packs, agent commands, `scale_check`, order checks, and exec orders are
trusted operator code. Bead titles, mail, formula vars, and PR text are untrusted and must not
be interpolated into `sh -c`. Ambient secret-like environment variables are stripped on
orchestrator-side helpers unless the operator passed the value explicitly. City config mutations
can require an ed25519 single-use grant bound to the exact request (`internal/citywriteauth`);
the dashboard does not hold the minting key.

**Why it transfers.** An orchestration ledger is full of attacker-controlled text the moment an
agent reads a ticket or a review comment. The formula engine will substitute `{{var}}` into step
descriptions. The trust doc's rule is the one that keeps that substitution out of the shell.
The city-write grant is the same shape as an approval: the mutation is a request, the
authorization is a separate credential, a captured grant does not apply to a different body.

**Caveat.** The grant covers the city HTTP API, and only when a key is configured. It does not
cover `bd update` on a work bead. Ledger writes and config writes are different doors. Closing
one leaves the other open. The ACP sidecar note (a writable meta file forges a drain ack) is a
third door, acknowledged in a comment, owner-only files as the mitigation.

---

## Part B — Where this meets findings already in this repository

| This repository | Gas City |
|---|---|
| [`SYNTHESIS.md`](../SYNTHESIS.md) §7 — a check that can fail must not be counted as a clean negative | A2. `ObservationIncomplete` exists so a probe error is not "dead". The ACP/subprocess seam lost that bit and HEAD puts it back |
| [`gas-town/04`](../gas-town/04-orchestration-techniques.md) A4 — propulsion needs a durable hook | A3. The hook is now a command, because the durable bead is invisible to the query a worker will otherwise write |
| [`gas-town/04`](../gas-town/04-orchestration-techniques.md) A1 — the coordinator holds no thread | A1. v2 workflows: the plan is the bead graph, `workflow-finalize` closes the root, any control-dispatcher process can resume it. v1 molecules are still inert data worked inside one session |
| [`control-plane-execution-plane`](../ai-workflow/wiki/concepts/control-plane-execution-plane.md) §5.6 — the plane boundary is a credential | A5, and it does not replace §5.6. City-write grants credential **config** mutations. A worker with ledger-write access can still forge a completed task, and can also strand a workflow by writing a control bead |
| [`approval-gate`](../ai-workflow/wiki/concepts/approval-gate.md) §7.7 — ACP's one permission RPC | [`03`](03-roles-and-lifecycle.md) §6. Gas City's ACP provider does not answer `session/request_permission`. The conformance test expects timeout and a rejected tool, with an empty client-reply log. Same shape as "orchestrators launch the wrapped agent with approval off" |
| Strands `sandbox: host`, Codex Windows sandbox | Unchanged. Gas City's trust doc says city config is trusted code that runs as shell. That is a host-scoped orchestrator by default. Providers (k8s, exec, ACP) move the session; they do not, by themselves, take the ledger credential away |

## Part C — What Gas City does that this evidence does not support

- **"Zero roles" as a product claim.** The type system has no role enum. The binary embeds the
  Gastown pack and polecat-named formulas. Cite the type system, not the slogan.
- **"The orchestrator runs the graph with no agent involved."** No *model* executes control
  beads. A `gc convoy control --serve` session does, and it is a reconciled agent entry named
  `control-dispatcher`.
- **ACP integration as an approval implementation.** The provider is a session transport. The
  permission method is unimplemented on the client side, on purpose of the current code, and the
  test locks that in.
- **Scale and cost.** "Hundreds of concurrent agents", "software factory", "Kubernetes for
  agents" — 📣, not measured. The reconciler is Kubernetes-shaped. The system is not thereby
  Kubernetes.
- **Each rig has its own database.** Stale glossary. One Dolt server, prefix filters, optional
  per-class stores.
- **Runtime behaviour.** Not run. Design notes inside the upstream repo are already behind the
  code (glossary 2026-04-25, formulas note 2026-03-17, health patrol 2026-05-29). A study that
  trusted those notes without the switch in `ProcessControl` would have missed v2.

## A compact card

1. **Graph policy in the ledger, judgement in the pack, shell in an exec order.** Three places.
   A new role is the wrong one until the other three have been refused.
2. **Incomplete is a liveness result.** Do not restart what you failed to see.
3. **One claim command.** If the obvious query hides wisps, the worker will trust the query.
4. **Prefix on a shared server is the default isolation.** It is a client filter, not a
   credential. Do not describe it as a trust boundary.
5. **Three doors, three credentials.** Config mutations, ledger writes, session-meta sidecars.
   A grant on one does not close the others. An unanswered ACP permission request closes none
   of them; it only means the tool was rejected by timeout.
