---
type: concept
status: active
last_ingested_from: docs/02-app-server-protocol.md
related_pages: [concepts/harness, concepts/approval-gate, concepts/stateless-conversation-wire]
created: 2026-09-22
updated: 2026-09-23
---

# Thread / Turn / Item — the conversation primitives

- Purpose: the three primitives Codex chose to express an agent loop as an API, and each one's lifecycle.
- Scope: the boundaries between them, item lifecycle, thread unloading and eviction, the sticky semantics of turn parameters
- Primary sources: the generated schemas under `codex-rs/app-server-protocol/schema/`, `config_toml.rs`
- Updated: 2026-09-23

## §1 TL;DR  {#s1-tldr}

| # | Primitive | Definition | Key property |
|---|---|---|---|
| 1 | **Item** | the atomic unit of input and output | an **explicit** lifecycle: `started → delta(0..N) → completed` |
| 2 | **Turn** | one unit of agent work started by user input | **the unit of interruption and rollback.** A sequence of items |
| 3 | **Thread** | the durable container for a conversation | created, resumed, forked, archived, with persisted history |

The design reason: user↔agent interaction is not simple request/response but **one request unfolding
into a structured sequence of actions.**

## §2 Item lifecycle  {#s2-item-lifecycle}

```
item/started  →  item/*/delta (0..N)  →  item/completed
```

Clients render immediately on `started`, apply increments on `delta` and finalise with the terminal
payload on `completed`. **This is how the protocol is meant to be consumed.**

### §2.1 `ThreadItem` type values  {#s2-1-item-types}

| type | Key fields |
|---|---|
| `userMessage` | `content: UserInput[]`, `clientId` |
| `hookPrompt` | `fragments` |
| `agentMessage` | `text`, `phase`, `memoryCitation`, `delivery`, `questions` |
| `reasoning` | `summary[]`, `content[]` |
| `plan` | `text` |
| `commandExecution` | `command`, `cwd`, `processId`, `source`, `status`, `commandActions[]`, `aggregatedOutput`, `exitCode`, `durationMs`, `pluginId`, `scriptPath` |
| `fileChange` | `changes: FileUpdateChange[]`, `status` |
| `mcpToolCall` | `server`, `tool`, `status`, `arguments`, `appContext`, `readOnlyHint`, `result`, `error`, `durationMs` |
| `dynamicToolCall` | `namespace`, `tool`, `arguments`, `status`, `contentItems`, `success`, `durationMs` |
| `functionCallOutput` | `name`, `namespace`, `output` |
| `collabAgentToolCall` | `tool`, `status`, `senderThreadId`, `receiverThreadIds[]`, `prompt`, `model`, `reasoningEffort`, `agentsStates` |
| `subAgentActivity` | `kind`, `agentThreadId`, `agentPath` |
| `webSearch` / `imageView` / `imageGeneration` / `sleep` | dedicated payloads |
| `enteredReviewMode` / `exitedReviewMode` | `review` |
| `contextCompaction` | — |

> `commandExecution.commandActions` is a **best-effort parse of a shell command that may be several
> commands piped together.** Use it in the UI to explain what a command will do.

## §3 Thread unloading and eviction — two different mechanisms  {#s3-unload-evict}

| Mechanism | Trigger | Setting |
|---|---|---|
| **Time-based unload** | no subscribers **and** no activity | `thread_unload_delay_secs`, **default 60 seconds** |
| **Capacity-based eviction** | loaded threads exceed the cap | `V2Residency`'s LRU `VecDeque<ThreadId>`, `effective_agent_max_threads` |

The unload target is `max(has_no_subscribers_since, is_inactive_since) + delay`. Activity or a new
subscriber resets it. Zero unloads immediately, and changes require a server restart.

> ⚠️ **[Refuted secondary source]** A secondary source describes a 30-minute idle unload. **It is
> wrong.** The default is 60 seconds, and the condition is the conjunction of two states, not one.
> The verification record is in [[concepts/primary-source-verification]].

## §4 The sticky semantics of turn parameters  {#s4-sticky}

Most `turn/start` overrides **persist beyond this turn.**

| Scope | Fields |
|---|---|
| **sticky** (applies to later turns too) | `cwd`, `approvalPolicy`, `approvalsReviewer`, `sandboxPolicy`, `model`, `serviceTier`, `effort`, `summary`, `personality` |
| **this turn only** | `serviceTierForTurn`, `outputSchema` |

> To change a single turn, use an explicitly scoped field or revert on the next one. This is among
> the most common integration traps.

## §5 A typical turn  {#s5-typical-turn}

```
client → initialize                        server → result
client → initialized (notification)
client → thread/start                      server → thread/started
client → turn/start                        server → turn/started
                                           server → item/started (userMessage) → completed
                                           server → item/started (reasoning)
                                           server → item/reasoning/summaryTextDelta ×N
                                           server → item/started (commandExecution)
   ◀── server REQUEST: item/commandExecution/requestApproval
   ──▶ client RESPONSE: { decision: "accept" }
                                           server → item/commandExecution/outputDelta ×N
                                           server → item/completed (commandExecution)
                                           server → item/started (agentMessage)
                                           server → item/agentMessage/delta ×N
                                           server → item/completed (agentMessage)
                                           server → turn/completed { turn: { status, usage } }
```

To see the real JSON: `codex debug app-server send-message-v2 "run tests and summarize failures"`

## §6 Legacy: protocol_v1's "turn" is a different thing  {#s6-protocol-v1}

In the **SQ/EQ model** beneath (and predating) the App Server, `Turn` means **one model-request
cycle** — **a different concept** from the App Server's turn. The same word names different things at
two layers, so check the layer before reading.

| Item | protocol_v1 |
|---|---|
| Communication | a Submission Queue (SQ) / Event Queue (EQ) pair |
| Submission payload | `Op::ConfigureSession`, `Op::UserTurn`, `Op::Interrupt`, `Op::ExecApproval`, `Op::UserInputAnswer` |
| Concurrency | a `Session` runs at most one `Task`. For parallel work, **one Codex instance per thread of work** |
| Compatibility | `EventMsg::TurnStarted`/`TurnComplete` serialise as `task_started`/`task_complete` |

> For a new integration use **the App Server protocol, not protocol_v1.**

## §7 Read next  {#s7-next}

- [[concepts/approval-gate]] — the server→client requests that stop a turn
- [[concepts/stateless-conversation-wire]] — how this conversation reaches the model
- [[concepts/harness]] — the whole picture
- Original: [`docs/02-app-server-protocol.md`](../../../docs/02-app-server-protocol.md)
