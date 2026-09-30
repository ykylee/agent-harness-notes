---
type: concept
status: active
last_ingested_from: docs/02-app-server-protocol.md + docs/06-choosing.md + docs/05-agents-api.md + browser-agents/10-aside-enforcement-and-native.md + browser-agents/11-dia-and-neon.md + browser-agents/12-dia-binary.md + strands/03-tools-and-approval.md + strands/07-security.md + strands/06-multi-agent-and-exposure.md + agent-ux/08-primitives-rendered.md + agent-ux/07-paseo-conductor.md + agent-ux/10-acp.md
related_pages: [concepts/thread-turn-item, concepts/harness, concepts/os-sandbox-policy, concepts/execution-environment-topology, concepts/credential-shielding, concepts/agent-client-protocol]
created: 2026-09-22
updated: 2026-09-30
---

# Approval Gate — making human intervention a protocol primitive

- Purpose: how human intervention was designed as **a protocol-level safety mechanism** rather than a UI convenience.
- Scope: Codex's ten server→client requests, ACP's one permission RPC, the decision vocabulary, the managed API's counterpart, implementation obligations, and how browser agents and Strands extend it
- Updated: 2026-09-30 (ACP engine-side: one permission RPC vs Codex's ten; Strands harness path never sends it)

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | Direction | **server → client.** This is why the protocol is bidirectional |
| 2 | Effect | **the turn stops** until the client responds |
| 3 | Request types | Codex: **ten**. ACP: **one** (`session/request_permission`) |
| 4 | Implementation obligation | without them **the turn simply stalls** |
| 5 | Managed API counterpart | `requires_action` plus `required_actions[]` |

## §2 The ten server→client requests  {#s2-server-requests}

| Method | Purpose |
|---|---|
| `item/commandExecution/requestApproval` | approve a command execution |
| `item/fileChange/requestApproval` | approve a file change |
| `item/permissions/requestApproval` | approve a permission escalation |
| `item/tool/requestUserInput` | a tool needs user input |
| `item/tool/call` | **delegate a dynamic tool call to the client** (`DynamicToolCallParams`) |
| `mcpServer/elicitation/request` | MCP elicitation |
| `account/chatgptAuthTokens/refresh` | request a ChatGPT token refresh |
| `attestation/generate` | generate the upstream `x-oai-attestation` (requires the capability opt-in) |
| `applyPatchApproval` | (legacy) approve applying a patch |
| `execCommandApproval` | (legacy) approve a command execution |

`item/tool/call` is not an approval but **the protocol implementation of the division of labour** —
the channel through which the agent calls tools owned by the host application. See
[[concepts/harness]] §6.

## §3 The decision vocabulary  {#s3-decisions}

The `ReviewDecision` family: `accept`, `acceptForSession`, `decline`, `cancel`, plus
amendment-carrying variants such as `acceptWithExecpolicyAmendment` (see `ExecPolicyAmendment` and
`NetworkPolicyAmendment`).

> An approval is not a plain yes or no — **it can carry a policy amendment.** "Allow this time, but
> fix the network policy like so" is expressible as a single response.

## §4 Approvals resolved elsewhere  {#s4-resolved-elsewhere}

The `serverRequest/resolved` notification says an approval request was **settled somewhere else** —
another client, or auto-approval. The UI must use it to clear its own pending approval.

Auto-approval path: `item/autoApprovalReview/started` and `completed`,
`autoApprovalReview/strictReviewRequired`.

> If you enable auto-approval, understand **the conditions that escalate to strict review** before
> you do.

## §5 The managed Agents API's counterpart  {#s5-agents-api}

What corresponds to the server→client request is the session's `requires_action` state.

| Action kind | How to handle |
|---|---|
| **function call** | run the named function and return the result, copying `turn_id` and `call_id` |
| **environment connection** | establish the connection using `environment_id` ([[concepts/execution-environment-topology]]) |

The key distinction:

> **Use `required_actions` to decide.** A `function_call` item in session history alone does not
> establish that a result is pending.

Functions with side effects should **store results durably by session, turn and call ID.** If
execution might have succeeded without the result being saved, check the outcome before re-running.

## §6 Implementation obligations and traps  {#s6-obligations}

| # | Item |
|---|---|
| 1 | The three approvals (`commandExecution` / `fileChange` / `permissions`) are **mandatory** — without them the turn stalls and never completes |
| 2 | Handle `serverRequest/resolved` to clear requests settled through another path |
| 3 | Approval gates are **protocol-level safety mechanisms, not UI conveniences** |
| 4 | Separate untrusted content from user input **at the type level** — the Python SDK's `ExternalMessage` is the model (it retains tool-level authority but confers no user authorization) |
| 5 | In the managed API, when `requires_action` is set **nothing proceeds until every required action is handled** |
| 6 | **A gate's availability is a separate axis from its correctness** (2026-09-30, `#49584`). Guardian now skips host skill/plugin discovery because that discovery could block its startup when the primary executor is offline — a gate that cannot run denies nothing. The regression test disconnects the executor and asserts Guardian still **denies** a network permission, so availability was fixed without weakening the gate. Read a "skip" commit as a loosening only after finding what it skips and what still runs. |

## §6.5 Observation — how browser agents extend this  {#s6-5-browser}

### Aside — approval designed to render in a chat channel

The daemon's **suspension** system is the approval UI. Three kinds:

| Kind | Buttons | Hint |
|---|---|---|
| permission approval | `Allow once` / deny | "_deny it. **No lasting permission will be granted.**_" |
| `action-confirmation` | `Confirm` / `Cancel` | "_Confirm to proceed, or reply with what to do instead._" |
| `ask-user-question` | up to five options | "_Pick an option or just reply with your answer._" |

Approval scope renders four ways: `file` (mode + path) · `tool` (name + call summary) · `browser`
(action + url) · `network` (url).

> 📌 **The decisive design**: it builds a button array **and a numbered text fallback**, and every
> hint ends in "or just reply with your answer." **It is designed to render in a chat channel, not a
> native modal.** Contrast App Server's approvals, which assume a client UI — if you need remote or
> asynchronous approval, this is the shape.
>
> There is no "always allow" and **no lasting permission is granted**, which is a conservatively
> chosen default. Nothing in the UI corresponds to `ReviewDecision`'s `acceptForSession`.

### Dia — reduce perception before asking

Beyond approval gates, Dia **documents** reducing what the agent can see: password fields and
**irreversible action buttons** are "invisible to the agentic system."

The 2026-09-30 binary pass found those **exact sentences absent** from the unpacked app. Prompt
mixins do tell the model to treat page/chat/artifact content as untrusted data, and Seatbelt
constrains the bundled Claude Code. Whether the native snapshot actually strips those elements
is still ⚠️ ([12](../../../browser-agents/12-dia-binary.md) §4).

> 📌 **Approval is the last line of defence, not the only one.** Documented perception reduction
> would cut how often you have to ask; it is not confirmed in native code. See
> [[concepts/credential-shielding]] and [[concepts/indirect-prompt-injection]] §5.

## §7 Confirmed by implementation  {#s7-implementation}

Ingested from [`SYNTHESIS.md` §6.2](../../../SYNTHESIS.md). This concept is one of the few whose
claims **survived being built** intact.

| Claim | Result |
|---|---|
| A gate that degrades to "allow" when its approval channel is missing is not a gate | Enforced: a policy that can `ask` with no broker **refuses the action** |
| The request is data, not a rendering | One request object drove a text renderer and would drive a GUI or chat one with no core change |
| Conflict resolution must be stated | `deny > ask > allow > default`. **`ask` beating `allow` is the deliberate part** — a config listing both is a mistake, and the safe reading of a mistake is to ask |
| No lasting permission | "Allow once" / "Deny", no `acceptForSession` equivalent |

> 📌 One thing the gate's *design* did not anticipate: the first implementation rendered a
> 340-character `data:` URL into the prompt in full, and named the element only by its ref. **A
> person cannot consent to what they cannot read**, so a gate that renders like that is decorative.
> Legibility is part of the mechanism, not presentation on top of it.

## §7.5 Observation — approval without a wire, and six properties of a gate  {#s7-5-strands}

**Strands** ([`strands/03`](../../../strands/03-tools-and-approval.md) §4). `interrupt()` raises; the loop stops
with `stop_reason="interrupt"`; the caller passes the answer back as the next prompt; the hook or tool
**re-runs from the top** and the second `interrupt()` returns the stored answer. Side effects before
the call happen twice. The only wire form is A2A `input_required`, and the A2A client refuses to send
interrupt responses.

Strands also has the most policy machinery studied here (interventions, Cedar, allow/ask lists), and
probing its error paths ([`strands/07`](../../../strands/07-security.md) §3, 🧪 with controls) showed placement
outside the loop is one property of six:

| Property | Strands |
|---|---|
| On by default | no — harness ships approval off |
| Fails closed on every error path | no — erroring Cedar `forbid` → allowed; raising steering handler → tool runs |
| Enum answers | no — steering approves any truthy response, including `"no"` |
| Explicit precedence | no — registration order, despite documented `deny > confirm > …` |
| Hard deny | no — the CLI downgrades every deny to an ask |
| Authorizes the final input | no — later hooks/middleware may rewrite after the decision |

> 📌 Add to the checklist: a gate is not done when it sits outside the loop. **Test every error path
> with a control that proves the input arrived** — four of the six gaps contradict Strands' own design
> documents, so reading the design would have found none of them.

## §7.6 Observation — how ten clients render the card  {#s7-6-clients}

From [`agent-ux/08`](../../../agent-ux/08-primitives-rendered.md) §1–2 (extracted strings; nothing seen rendered):

| Axis | Finding |
|---|---|
| Sentence | **"Allow ⟨agent⟩ to ⟨verb⟩?"** (Claude, ChatGPT/Codex, Orca); CLI-derived "Do you want to…?" (Conductor). Always an action, never a tool name |
| Scope | from a long ladder (Claude: once → chat → session → task → **{n} days** → always, with an undo toast) to **none** (Paseo, Aside: trust lives only in the mode) |
| Scope editing | Antigravity and Devin let you **edit the target inside the card** — the card becomes a scope editor |
| Other answerers | Paseo: one request object, **four renderers** (GUI, CLI, MCP — a parent agent answers its child — push); Claude: BLE hardware; Codex: an LED keypad |
| Reply-as-answer | Paseo: a message sent while a prompt is pending **denies it with a reason** and reaches the same turn — §6.5's "or just reply" as a protocol rule |
| Reflex key | Conductor binds **bare Enter** to approve |
| Middle rung | a **machine reviewer** — "Auto", "Approve for me", "Auto-review" — between ask and never |
| Default | three orchestrators launch wrapped agents with **approvals off** — §7.5's first property missing |

## §7.7 Observation — ACP's one permission request  {#s7-7-acp}

[[concepts/agent-client-protocol]]. Spec `protocolVersion` **1**, method
`session/request_permission` (hyphen on the wire; TypeScript accessor `requestPermission`). The
agent supplies labelled options whose `kind` is one of `allow_once` · `allow_always` ·
`reject_once` · `reject_always`. The turn waits on that RPC; on `session/cancel` every pending
request must return `cancelled`.

Codex types the *thing* being approved as the method name and lets the response carry a policy
amendment (§2). ACP types nothing: **the options are data**, which is why Paseo can put one
request on four renderers ([07](../../../agent-ux/07-paseo-conductor.md)).

**Re-verified 2026-09-30 evening against `c81fae79`** (7 commits past the `9b26a3ea` pin, +6791 /
−359): the method and all four option kinds were re-read in `schema/v1/schema.json`, which is
**byte-identical** across the window. One gate, four kinds — still the whole stable contract.

The same window made **MCP-over-ACP request-scoped** (#2223, `*(unstable)*`): MCP payloads move
onto the message rather than a standalone exchange. **Whether that changes what a permission
request can cover is unknown** — the 244 added lines of `docs/protocol/v1/draft/prompt-turn.mdx`
were not read. The unchanged stable schema is **not** evidence that the two are unrelated; the
question stays open. [[concepts/primary-source-verification]] §8.2.

**Strands CLI** implements the RPC only on the imported source-agent path. The harness path
(`createHarness`, default `interventions=None`) never calls it
([`strands/06`](../../../strands/06-multi-agent-and-exposure.md) §5.4,
[`agent-ux/10`](../../../agent-ux/10-acp.md) §7). Source absence ✅; live ACP client ⚠️.

## §8 Read next  {#s8-next}

- [[concepts/thread-turn-item]] — the turn that approval stops
- [[concepts/credential-shielding]] — removing the need to ask
- [[concepts/os-sandbox-policy]] — the defence on the side approval does not cover
- Originals: [`docs/02-app-server-protocol.md`](../../../docs/02-app-server-protocol.md) §7, [`docs/06-choosing.md`](../../../docs/06-choosing.md) §5
- Strands case: [`strands/03-tools-and-approval.md`](../../../strands/03-tools-and-approval.md)
- Client rendering: [`agent-ux/08-primitives-rendered.md`](../../../agent-ux/08-primitives-rendered.md)
- ACP wire: [[concepts/agent-client-protocol]], [`agent-ux/10-acp.md`](../../../agent-ux/10-acp.md)
