---
type: concept
status: active
last_ingested_from: docs/02-app-server-protocol.md + docs/06-choosing.md + docs/05-agents-api.md + browser-agents/10-aside-enforcement-and-native.md + browser-agents/11-dia-and-neon.md
related_pages: [concepts/thread-turn-item, concepts/harness, concepts/os-sandbox-policy, concepts/execution-environment-topology, concepts/credential-shielding]
created: 2026-09-22
updated: 2026-09-23
---

# Approval Gate — making human intervention a protocol primitive

- Purpose: how human intervention was designed as **a protocol-level safety mechanism** rather than a UI convenience.
- Scope: the ten server→client requests, the decision vocabulary, the managed API's counterpart, implementation obligations, and how browser agents extend it
- Updated: 2026-09-23

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | Direction | **server → client.** This is why the protocol is bidirectional |
| 2 | Effect | **the turn stops** until the client responds |
| 3 | Request types | ten |
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

Beyond approval gates, Dia **reduces what the agent can see in the first place**: password fields and
**irreversible action buttons** are "invisible to the agentic system."

> 📌 **Approval is the last line of defence, not the only one.** Erasing dangerous elements from
> perception reduces how often you have to ask at all. See [[concepts/credential-shielding]].

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

## §8 Read next  {#s8-next}

- [[concepts/thread-turn-item]] — the turn that approval stops
- [[concepts/credential-shielding]] — removing the need to ask
- [[concepts/os-sandbox-policy]] — the defence on the side approval does not cover
- Originals: [`docs/02-app-server-protocol.md`](../../../docs/02-app-server-protocol.md) §7, [`docs/06-choosing.md`](../../../docs/06-choosing.md) §5
