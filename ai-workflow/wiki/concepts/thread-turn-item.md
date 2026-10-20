---
type: concept
status: active
last_ingested_from: docs/02-app-server-protocol.md + claude-code/01-wire-protocol.md + claude-code/03-sessions-context-and-clients.md + harness-artifacts/05-agent-loop.md
related_pages: [concepts/harness, concepts/approval-gate, concepts/stateless-conversation-wire]
created: 2026-09-22
updated: 2026-10-20
---

# Thread / Turn / Item — the conversation primitives

- Purpose: the three primitives Codex chose to express an agent loop as an API, and each one's lifecycle.
- Scope: the boundaries between them, item lifecycle, thread unloading and eviction, the sticky semantics of turn parameters
- Primary sources: the generated schemas under `codex-rs/app-server-protocol/schema/`, `config_toml.rs`
- Updated: 2026-10-20 (§8.7: four meanings of "turn" and the continue signal across five engines, from `harness-artifacts/05`). Previous: 2026-10-20 (`docs/99` §E.8: `runtime-agent-instance` unwired; the live identity leg is `AuthMode::AgentIdentity` + attestation — §8.5 addendum corrected). Previous: 2026-10-20 (Codex drift `b1fd48c48`→`79a19cbb3`: counts unchanged, + experimental `thread/sample`, Thread/Turn types byte-identical — §8.5 addendum; 2026-10-19: `claude-code/01·03` drift 0.3.304/2.1.304 — no change to the flat wire; `keep_alive` gains an out-of-schema `startup_mark`, dialogs may have no deadline, context-usage rows get stable ids; §8.6 unchanged; `claude-code/01·03`: the flat alternative to Thread/Turn/Item — §8.6; evening: `docs/02` §4 Item table and §9 27-field `ThreadStartParams` supplement; drift 2026-10-19 `b1fd48c48`: counts 108/10/87, turn lineage fields, read state, `codexErrorInfo` open set — §8.5). Previous: 2026-09-30 (date bump: generated-schema counts / catalog follow-up) (Codex drift re-check against `e72da2b538`)

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
| **sticky** (applies to later turns too) | `cwd`, `approvalPolicy`, `approvalsReviewer`, `sandboxPolicy`, `model`, `serviceTier`, `effort`, `summary`, `personality` (deprecated 2026-09 — no longer selects a style, #45809) |
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

## §8.5 Observation — three weeks of drift, `d42056091` → `b1fd48c48`  {#s8-5-drift-2026-10-19}

`docs/99` §E.6: four client methods and one notification added, none removed or renamed —
generated `ClientRequest` 107 → **108**, `ServerRequest` 10, `ServerNotification` 86 → **87**.
`TurnStartParams` gains `parentTurnId` / `rootTurnId` (#51415, turn lineage is now wire data);
`ThreadForkParams.experimentalPredictionMode`; experimental **thread read state**
(`thread/readState/update`, `thread/items/read`, `thread/readState/changed`, `-32600` +
`readStateConflict` on a stale `expectedRevision`); `subAgentActivity` carries `model` and
`reasoningEffort`; `imageGeneration` restructured. `codexErrorInfo` is an **open set** (#49806) — a
client that matches a closed enum breaks. The durable-host dialect of `agent-ux/03` §1.2.1 is still
absent from the engine. Unload delay (60 s) unchanged, now applied per thread (#55270).

`docs/02` §4 and §9 were supplemented the same evening: the Item table now carries the new
`imageGeneration` shape (`image: GeneratedImageRef`, untagged `{ fileId }` | `{ result }`, plus
`inputImages[]` with `sha256`) and `subAgentActivity.model/reasoningEffort`; `ThreadStartParams` is
listed as the full 27-field Rust definition with the 12 experimental fields marked ⚗ — the
engine-side half of the client's durable-host dialect (`environments`, `dynamicTools`,
`selectedCapabilityRoots`, `experimentalRawEvents`).

**2026-10-20, `b1fd48c48` → `79a19cbb3`** (`docs/99` §E.7, 46 commits, no tag): generated counts
108 / 10 / 87 unchanged; one experimental request `thread/sample` (`{thread_id, expected_turn_id, prompt,
effort?, turn_trigger?}` — a sample against a thread without opening a turn); every approval and
Thread/Turn type byte-identical; durable-host dialect still absent (fourth check). New outside the
wire: a `runtime-agent-instance` crate registering ephemeral runtimes with Ed25519 assertions —
checked 2026-10-20 (`docs/99` §E.8): no crate depends on it yet; the identity that *is* wired is
`AuthMode::AgentIdentity` (persisted Ed25519 key, task-scoped `Authorization: AgentAssertion …`,
behind `use_agent_identity`), distinct from the client-side `x-oai-attestation`.

## §8.7 Observation — four meanings of "turn", and what decides "continue"  {#s8-7-loop}

[`harness-artifacts/05`](../../../harness-artifacts/05-agent-loop.md) (2026-10-20) read the loop code
of five engines. Only the App Server's turn is a *user* unit; Claude Code (`maxTurns`, `num_turns`),
opencode (steps), Gemini (`Turn`, `MAX_TURNS 100`) and Strands (`turns`) all mean one model call. The
continue signal differs accordingly: Codex `needs_follow_up` = "a tool was called ∨ a steer arrived"
with no step cap and a Stop hook that can add rounds; Claude Code folds 26 internal terminal reasons into
five `result` subtypes and caps stop-hook blocking at 8; opencode's step returns `compact | stop |
continue`; Gemini asks an LLM who speaks next and sends "Please continue." itself. Steering is an
Item-level fact in Codex (`TurnInputMode::Steer{expected_turn_id}`, pending input absorbed between
samplings, a separate next-turn queue) and a priority queue with interrupt receipts in Claude Code.
The same-day second pass (TASK-2026-10-20-main-005) closed four gaps: opencode has **no server queue** —
a prompt during a run is stored and joins the running fiber, becoming the next step's `lastUser`
(the first pass's "busy → refused" was wrong; `assertNotBusy` guards edits and shells, not prompts);
Gemini's TUI queues on the client and, behind `experimental.modelSteering`, injects hints before the
next tool results; Claude Code compacts at *effective window − 13k* (effective = window − min(maxOutput,
20k); 1M → 967k) with a rapid-refill breaker of 3 refills within 3 turns each; and Codex has **no loop
detector** — its only bound is the context window, on the comment's assumption that compaction converges.

## §8.6 Observation — the flat alternative: `session_id` + `uuid` + `parent_tool_use_id`  {#s8-6-claude-code}

Claude Code has no Thread/Turn/Item ([`claude-code/01`](../../../claude-code/01-wire-protocol.md) §3):
a message is the item (`SDKMessage`, 39 members, 11 top-level types), `result` closes the turn with
usage, cost and `permission_denials`, and `session_id` is the thread. Lineage is `uuid` per message
and `parent_tool_use_id` for subagent output; `conversation_reset` swaps the thread inside one
process. Persistence is a JSONL transcript per session under `~/.claude/projects/<cwd>/`, with
`parentUuid`, `isSidechain` and `compact_boundary` lines; there is **no unload timer** — the process
is the session and a dropped one reloads from disk, swept after `cleanupPeriodDays` (30) except
Desktop and Cowork transcripts ([`claude-code/03`](../../../claude-code/03-sessions-context-and-clients.md) §1).
`/branch` copies the transcript and keeps session approvals; `--fork-session` is a new process and
drops them.

## §7 Read next  {#s7-next}

- [[concepts/approval-gate]] — the server→client requests that stop a turn
- [[concepts/stateless-conversation-wire]] — how this conversation reaches the model
- [[concepts/harness]] — the whole picture
- Original: [`docs/02-app-server-protocol.md`](../../../docs/02-app-server-protocol.md)
