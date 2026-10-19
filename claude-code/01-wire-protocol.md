# 01. The wire — stream-json, control requests, and what `initialize` is for

> Sources: `@anthropic-ai/claude-agent-sdk` 0.3.303 (`sdk.d.ts:N`, `browser-sdk.d.ts`, `bridge.d.ts`,
> `sdk.mjs`, `manifest.json`), the 2.1.303 binary's split modules (`chunk-*.js`, strings only), and the
> official docs as Markdown (`docs:<page>`). Nothing was executed. The generated `.d.ts` is treated as
> the contract the way Codex's generated schema is in [`docs/02`](../docs/02-app-server-protocol.md);
> §7 records where the binary's vocabulary exceeds it, as [`docs/99`](../docs/99-sources.md) §E.2
> did for Codex's experimental methods.

## 1. Basic shape — and how it differs from Codex

Codex speaks "JSON-RPC lite" (`{id, method, params}`). Claude Code speaks **type-tagged JSONL**: one
JSON object per stdout line, dispatched on a top-level `type` and then on `subtype`. The union of
everything the engine writes is `StdoutMessage` (`sdk.d.ts:9726`) ✅:

```
StdoutMessage = SDKMessage | SDKActiveGoalMessage | SDKControlResponse
              | SDKControlRequest | SDKControlCancelRequest | SDKKeepAliveMessage
```

The three message kinds are the same as Codex's — a request `{type: 'control_request',
request_id, request: {subtype, …}}`, a response `{type: 'control_response', response: {subtype:
'success' | 'error', request_id, …}}`, and notifications (`SDKMessage`, no id). The difference is
that **engine→client and client→engine requests share one `SDKControlRequestInner` union**
(`sdk.d.ts:5097`): direction is a per-subtype convention stated in doc comments, not a type.

Three further structural differences, developed below: there is no Thread/Turn/Item triple
(§2 — a message is the item, `result` ends the turn, `session_id` is the thread); `initialize`
injects configuration rather than negotiating capabilities (§1.3); and the binary runs two to four
times more control subtypes than the types publish (§7).

## 2. Transports and handshake

### 2.1 Three transports

| Transport | Entry | Evidence |
|---|---|---|
| stdio JSONL (default) | `query()` spawns the CLI as a child with `--output-format stream-json --input-format stream-json -p` | `Options.pathToClaudeCodeExecutable`, `executable: 'bun' \| 'deno' \| 'node'`, `spawnClaudeCodeProcess` (`sdk.d.ts:1552-2490`) |
| WebSocket, or SSE + POST (browser) | `@anthropic-ai/claude-agent-sdk/browser` `query(BrowserQueryOptions)` | `browser-sdk.d.ts:22-27`: `WebSocketOptions { url, authMessage: {type: 'auth', credential: {type: 'oauth', token}} }`, `SSEOptions { streamUrl: '…/v1/code/sessions/{id}/events/stream', sendUrl, sessionId }` |
| Bridge (Remote Control, reversed) | `/bridge` `attachBridgeSession({ sessionId, ingressToken, apiBaseUrl, epoch, initialSequenceNum })` | `bridge.d.ts:96-246` |

The browser and bridge paths go through a server the types call **CCR** (`bridge.d.ts:19`
"Session state reported to the CCR /worker endpoint"): the local CLI attaches with
`attachBridgeSession`, a browser reads the same session over SSE. `docs:remote-control` says only
"Remote Control executes on your machine" and does not describe the wire. CCR = Claude Code Remote
(추정).

### 2.2 CLI flags (`docs:cli-reference`, matched against bundle strings ✅)

`-p` / `--print`, `--output-format text | json | stream-json`, `--input-format text | stream-json`,
`--include-partial-messages`, `--replay-user-messages` ("Re-emit user messages from stdin back on
stdout for acknowledgment"), `--include-hook-events`, `--resume <id | name | .jsonl path>`,
`--continue`, `--session-id <uuid>`, `--fork-session`, `--permission-prompt-tool <mcp tool>`,
`--permission-prompts host | none`, `--json-schema`, `--max-turns`, `--max-budget-usd`,
`--forward-subagent-text`, `--prompt-suggestions`, `--bare`, `--remote-control` / `--rc`,
`--channels`, and `--sdk-url` (bundle only, undocumented). Token-level events in stream-json need
`--verbose --include-partial-messages` together (`docs:headless`).

### 2.3 `query()` and its 69 options (`sdk.d.ts:1552-2490`)

`query({ prompt: string | AsyncIterable<SDKUserMessage>, options? }): Query` (`sdk.d.ts:3297`).
Grouped ✅:

| Group | Options |
|---|---|
| process / transport (8) | `pathToClaudeCodeExecutable`, `executable`, `executableArgs`, `extraArgs`, `env`, `spawnClaudeCodeProcess`, `stderr`, `loadTimeoutMs` |
| session (9) | `resume`, `continue`, `sessionId`, `forkSession`, `resumeSessionAt`, `resumeDropsTurn`, `persistSession`, `sessionStore`, `sessionStoreFlush` |
| permission (8) | `permissionMode`, `canUseTool`, `permissionPromptToolName`, `permissionPrompts: 'host' \| 'none'`, `allowDangerouslySkipPermissions`, `allowedTools`, `disallowedTools`, `sandbox` |
| tools / MCP / plugins / skills (10) | `tools`, `toolAliases`, `toolConfig`, `mcpServers`, `strictMcpConfig`, `plugins`, `pluginDelivery: 'argv' \| 'initialize'`, `skills`, `agents`, `agent` |
| model / budget (9) | `model`, `fallbackModel`, `thinking`, `effort`, `maxThinkingTokens`, `maxTurns`, `maxBudgetUsd`, `taskBudget`, `betas` |
| prompt / settings (9) | `systemPrompt`, `planModeInstructions`, `settings`, `managedSettings`, `settingSources`, `cwd`, `additionalDirectories`, `projectConfigRoot`, `title` |
| callbacks / stream shape (10) | `hooks`, `onElicitation`, `onUserDialog`, `supportedDialogKinds`, `includePartialMessages`, `includeHookEvents`, `forwardSubagentText`, `verbatimPrompts`, `promptSuggestions`, `agentProgressSummaries` |
| other (6) | `abortController`, `outputFormat`, `enableFileCheckpointing`, `perTaskStopAffordance`, `debug`, `debugFile` |

The `Query` handle (`sdk.d.ts:2892`) wraps control requests in **30 methods**: `interrupt`,
`setPermissionMode`, `setMcpPermissionModeOverride`, `setModel`, `setMaxThinkingTokens`,
`applyFlagSettings`, `updateSettings`, `initializationResult`, `reinitialize`,
`supportedCommands / Models / Agents`, `mcpServerStatus`, `getContextUsage`, `usage_EXPERIMENTAL…`,
`readFile`, `reloadPlugins / Skills / OutputStyles`, `accountInfo`, `rewindFiles`, `seedReadState`,
`reconnectMcpServer`, `toggleMcpServer`, `readMcpResource`, `setMcpServers`, `streamInput`,
`stopTask`, `backgroundTasks`, `close`. `startup()` → `WarmQuery` (`sdk.d.ts:9718`) pre-spawns a
process (`result.warm_spare_claimed`). **0.3.304**: `startup()` and `prewarm()` take
`initializeTimeoutMs` (default 60,000 ms; when unset, time a `SessionStart` or `Setup` hook spends is
not counted, for at most 10 minutes), and with `CLAUDE_CODE_SDK_READS_STARTUP_MARKS` the CLI reports
35 named start-up checkpoints as `keep_alive` lines before `initialize` answers ([99](99-sources.md) §E).

### 2.4 `initialize` is configuration injection, not capability negotiation

`initialize` (`sdk.d.ts:4539-4686`) is client→engine and carries **settings**: `hooks` (per-event
matchers with `callback_ids`), `sdkMcpServers` / `sdkMcpServerConfigs` / `sdkMcpServerManifests`
(an in-process MCP server's `initializeResult` handed over up front), `jsonSchema`, `systemPrompt`,
`appendSystemPrompt`, `agents`, `skills`, `plugins`, `toolAliases`, `supportedDialogKinds`,
`promptSuggestions`, `forwardSubagentText`. The reply `SDKControlInitializeResponse` reports
`commands: SlashCommand[]`, `agents: AgentInfo[]`, `models: ModelInfo[]`, `account: AccountInfo`,
`output_style`, `available_output_styles`, `hooks_applied`, `plugins_applied`,
`sdk_mcp_manifests_parked`, `claude_code_version`, `fast_mode_state` ✅. The only thing a client
*declares* about itself is `supportedDialogKinds`.

> 📌 Codex's `initialize` exchanges `clientInfo` and `InitializeCapabilities` and the server
> answers with four fields. Claude Code's hands the engine its hooks, MCP servers, agents and skills
> and gets back the catalog it built from them. The handshake is where configuration becomes wire
> data — which is also why the engine's version is a field of the reply rather than a negotiation.

`interrupt` → `{subtype: 'interrupt', cancel_queued?}` returns `{still_queued: string[],
cancelled?: string[]}` (`sdk.d.ts:4686-4705`). `control_cancel_request {request_id}` goes either
way and has no reply ("Either side may send it for a request it originated… There is no reply to
the cancel itself", comment above `sdk.d.ts:3958`). `{type: 'keep_alive'}` is engine→client with
no fields (`sdk.d.ts:5375`) — **0.3.304** adds one use outside the schema: a `startup_mark` field
naming a start-up checkpoint, written only when the SDK set `CLAUDE_CODE_SDK_READS_STARTUP_MARKS`.
The same release lets the CLI send a `request_user_dialog` with **no deadline**, withdrawn with
`control_cancel_request` ([99](99-sources.md) §E).

## 3. Message primitives — `SDKMessage`

No Thread/Turn/Item. **A message is the item, `result` closes the turn, `session_id` is the
thread.** `SDKMessage` has **39** members (`sdk.d.ts:5442`): 11 top-level `type`s, of which
`system` carries 28 subtypes ✅.

| `type` | Subtypes / key fields |
|---|---|
| `assistant` | `message: BetaMessage`, `parent_tool_use_id`, `error?`, `agent_id?`, `subagent_type?`, `user_message_uuid(s)?`, `supersedes?: UUID[]`, `aborted?` (`:3662`) |
| `user` | `SDKUserMessage` (input; optional `uuid` / `session_id`, `priority: now \| next \| later`, `origin: SDKMessageOrigin`, `shouldQuery?`) and `SDKUserMessageReplay` (`isReplay: true`, uuid required — the `--replay-user-messages` echo) (`:6392`, `:6487`) |
| `stream_event` | `event: BetaRawMessageStreamEvent` (the Anthropic API's raw stream event, verbatim), `parent_tool_use_id`, `ttft_ms?` (`:5602`) |
| `result` | `subtype: 'success'` or `'error_during_execution' \| 'error_max_turns' \| 'error_max_budget_usd' \| 'error_max_structured_output_retries'`. Common: `duration_ms`, `duration_api_ms`, `is_error`, `num_turns`, `stop_reason`, `total_cost_usd`, `usage`, `modelUsage`, `permission_denials: {tool_name, tool_use_id, tool_input}[]`, `queued_turn_count?`, `terminal_reason?`, `result_index?`, `origin?`. Success only: `result: string`, `structured_output?`, `deferred_tool_use?`, and ~17 latency fields (`ttft_ms`, `first_stream_post_ms`, `warm_spare_claimed` …) (`:5794-5955`) |
| `system` | 28: `init` (`cwd`, `tools[]`, `mcp_servers`, `model`, `permissionMode`, `slash_commands`, `skills`, `plugins`, `claude_code_version`, `apiKeySource`), `compact_boundary` (`compact_metadata: {trigger: 'manual' \| 'auto', pre_tokens, post_tokens?, preserved_segment?: {head_uuid, anchor_uuid, tail_uuid}}`, `:3810`), `status` (`'compacting' \| 'requesting' \| null`, `permissionMode?`), `api_retry`, `control_request_progress`, `model_refusal_fallback / no_fallback`, `local_command_output`, `hook_started / progress / response`, `plugin_install`, `task_started / updated / progress / notification`, `background_tasks_changed`, `thinking_tokens`, `session_state_changed` (`idle \| running \| requires_action`), `worker_shutting_down`, `commands_changed`, `notification`, `files_persisted`, `memory_recall`, `elicitation_complete`, `permission_denied`, `mirror_error`, `informational` |
| `tool_progress` | `tool_use_id`, `tool_name`, `elapsed_time_seconds`, `heartbeat?`, `task_id?` (`:6287`) |
| `tool_use_summary` | `summary`, `preceding_tool_use_ids[]` |
| `auth_status`, `rate_limit_event`, `prompt_suggestion`, `conversation_reset` | `conversation_reset` carries `new_conversation_id` and `trigger: clear \| plan_mode_exit \| fresh_session \| onboarding` — the thread is swapped inside one process, a concept Codex does not have |

`SDKMessageOrigin` (`:5447`) tags where an input came from: `human | channel {server} | peer {from,
fromSession} | task-notification {subkind: scheduled-trigger | peer-send-message | projects-relay |
session-inbox} | coordinator` — the "channel" and "peer" of [03](03-sessions-context-and-clients.md)
§3 as a wire field.

## 4. The control plane

`SDKControlRequestInner` has **40** subtypes (`sdk.d.ts:5097`). A response is `{subtype:
'success', request_id, response?}` or `{subtype: 'error', request_id, error}`, and either may
piggyback `pending_permission_requests?` / `pending_user_dialog_requests?` (`:396-430`) — a list of
prompts still unanswered, carried on every reply ✅.

**Client → engine (36).** Session: `initialize`, `interrupt`, `rename_session`, `set_color`,
`cancel_async_message`, `rewind_files`, `seed_read_state`, `register_repo_root`. Mode and model:
`set_permission_mode`, `set_model`, `set_max_thinking_tokens`, `apply_flag_settings`,
`update_settings`, `get_settings`. Queries: `get_context_usage`, `get_session_cost`, `get_usage`,
`get_binary_version`, `list_models`, `list_permission_rules`, `get_hooks_listing`,
`file_suggestions`, `read_file`. MCP: `mcp_status`, `mcp_call`, `mcp_set_servers`, `mcp_reconnect`,
`mcp_toggle`, `mcp_read_resource`, `mcp_message`. Tasks: `stop_task`, `background_tasks`,
`get_task_output`. Reload: `reload_plugins`, `reload_skills`, `reload_output_styles`.

**Engine → client — the analogue of Codex's ten server→client requests.** Five in the types, eight
more answered by the `sdk.mjs` runtime:

| Subtype | Purpose | Client's answer | Evidence |
|---|---|---|---|
| `can_use_tool` | tool permission (Codex's three `*/requestApproval` requests in one): `tool_name`, `input`, `permission_suggestions: PermissionUpdate[]`, `decision_reason_type`, `blocked_path?` | `PermissionResult` (allow + `updatedInput` / deny + `message`) — [02](02-approval-and-permissions.md) §2 | `sdk.d.ts:4877`; bundle `sendRequest({subtype:"can_use_tool",…})` |
| `hook_callback` | run a hook registered in `initialize.hooks` by `callback_id`: `input: HookInput`, `tool_use_id?` | hook output | `:5297`; bundle `sendRequest({subtype:"hook_callback",callback_id:…})` |
| `mcp_message` | JSON-RPC to an in-process SDK MCP server (**both directions**) | `mcp_response` | `:4796` "Flows in both directions" |
| `elicitation` | MCP elicitation (`mode: form \| url`, `requested_schema`) | `ElicitationResult` | `:3969` |
| `request_user_dialog` | a blocking dialog a tool raises (`dialog_kind`, `payload`) — cf. Codex `item/tool/requestUserInput` | the user's choice | `:5121` |
| `oauth_token_refresh`, `host_auth_token_refresh`, `remote_control_work_secret` | credential refresh (untyped) | a token | `sdk.mjs` `e.request.subtype==="oauth_token_refresh"` → `getOAuthToken` |
| `ui_prompt_read`, `ui_prompt_fill`, `ui_prompt_suggest`, `ui_read_selection`, `ui_copy` | host-UI operations (untyped) | `uiHost.*` | `sdk.mjs` `this.uiHost?.promptFill` |

The bundle also has the engine sending `read_file` **to the host** (`sendControlRequest({subtype:
"read_file", path})`, timeout text "remote read_file timed out") — the same subtype that
`Query.readFile()` sends the other way; 추정: the reversed use is Remote Control, where the file is
on the host. `side_question` is commented "client-originated" (`:5100`) yet appears in the bundle
as `sendControlRequest({subtype:"side_question", question})`; since the bundle holds both the
worker and the TUI (`ui_*`, `worker_shutting_down`), 추정: **the TUI is itself a client of the
worker over this protocol**. There is no typed counterpart of Codex's `item/tool/call` (host-owned
tool delegation); the bundle's `remote_tool_call` / `tool_host_result` / `remote_tools_announce`
look like it and are untyped (추정).

## 5. Session identity and continuity on the wire

- `session_id` is a required field on almost every output message (the thread id). `uuid` is the
  per-message id; `SDKAssistantMessage.uuid` is the chain-entry id that `resumeSessionAt` forks at
  (`:2132` "Accepts any chain-entry UUID — typically SDKAssistantMessage.uuid").
- `parent_tool_use_id: string | null` — a subagent's messages point at the parent's `Agent`
  tool_use id; they appear on the stream only with `--forward-subagent-text`. Also `agent_id?`,
  `subagent_type?`, `task_description?` (`:3662`, `:6392`); task messages carry `task_id`,
  `run_id`, `parent_task_id`, `spawn_depth`.
- `isSidechain` is not a wire field — it exists in the session-store summary (`:825`) and the
  JSONL transcript ([03](03-sessions-context-and-clients.md) §1).
- Fork and resume: `resume` + `forkSession` → a new session id (`:2124` "Cannot be used with
  continue or resume unless forkSession is also set"), `resumeSessionAt` / `resumeDropsTurn` for a
  mid-chain fork, `forkSession(sessionId, {upToMessageId})` as an offline JSONL copy (`:854-888`);
  `--resume` accepts an absolute `.jsonl` path (`docs:headless`).
- `conversation_reset` swaps the thread inside a running process (§3).

## 6. How the SDK is packaged

- `extractFromBunfs(embeddedPath)` runs **the other way round** from what its name suggests: it does
  not unpack the CLI; it lets a *user's* app that was itself `bun build --compile`d, with the CLI
  binary embedded `with {type: 'file'}`, copy that binary out of the `$bunfs` / `~BUN` virtual
  filesystem into `{tmpdir}/claude-{uid}/claude-agent-sdk-{sha256[:16]}/` so it can be spawned
  (owner and `0o700` mode checks included) ✅.
- The CLI binary arrives through eight `optionalDependencies` platform packages
  (`@anthropic-ai/claude-agent-sdk-linux-x64` …, all 0.3.303). `manifest.json` lists CLI 2.1.303's
  per-platform sha256 and size (commit `07df2aed`, buildDate 2026-10-18T20:40:12Z) with
  `manifestSignatureEnforcement: "flag"` ✅ — the SDK release is the engine's distribution channel,
  as [`SYNTHESIS`](../SYNTHESIS.md) §2.9 observed of the desktop apps.
- `bridge.d.ts` / `bridge.mjs` is the Remote Control bridge: `BridgeSessionHandle` has
  `write(SDKMessage)`, `sendControlRequest / Response / CancelRequest`, `reportState(idle | running
  | requires_action)`, `reportDelivery(eventId, 'processing' | 'processed')`, `getSequenceNum()`
  (the SSE high-water mark); `AttachBridgeSessionOptions` callbacks `onPermissionResponse`,
  `onInterrupt`, `onSetModel`, `onSetPermissionMode`, `onRenameSession` deliver remote control to
  the local engine; `createCodeSession(baseUrl, accessToken, title, …)` and
  `fetchRemoteCredentials(sessionId, …)` create and authorise sessions ✅.
- `browser-sdk` is §2.1; `core` re-exports `query / startup / tool / createSdkMcpServer` without
  inlined peer dependencies (README).
- `sdk-tools.d.ts` is json-schema-to-typescript output: **the built-in tools' input and output
  schemas**, `ToolInputSchemas` with 44 members (`AgentInput, BashInput, FileEditInput,
  FileReadInput, FileWriteInput, GlobInput, GrepInput, NotebookEditInput, WebFetchInput,
  WebSearchInput, TodoWriteInput, TaskCreate/Get/Update/List/StopInput, CronCreate/Delete/ListInput,
  ScheduleWakeupInput, MonitorInput, WorkflowInput, ArtifactInput, ClaudeDesignInput,
  ProjectsInput, AskUserQuestionInput, EnterPlanMode/ExitPlanModeInput,
  EnterWorktree/ExitWorktreeInput, McpInput, RefreshMcpToolsInput, ListMcpResourcesInput,
  ReadMcpResource(Dir)Input, ReportFindingsInput, SendFeedbackInput, PushNotificationInput,
  RemoteTriggerInput, ReadNotificationsInput, ProposeSkillsInput, ProposeGoalInput,
  ShowOnboardingRolePickerInput, OfferChromeSetupInput`), 44 outputs, 90 exports.
  `BUILTIN_TOOL_NAMES` (`sdk.d.ts:216`) lists **54** — `Skill`, `SendMessage`, `SubagentHandback`,
  `ToolSearch`, `LSP`, `PowerShell`, `ListAgents`, `EndConversation`, `WaitForMcpServers` and others
  have a name but no published schema.

## 7. Counts — and what the binary runs beyond the types

| Item | Count | Evidence |
|---|---|---|
| `SDKMessage` members | 39 (11 top-level `type`s; `system` 28 subtypes; `result` 5) | `sdk.d.ts:5442` |
| `StdoutMessage` top-level `type`s | 16 (the 11 + `active_goal`, `control_request`, `control_response`, `control_cancel_request`, `keep_alive`) | `:9726` |
| `control_request` subtypes (typed) | 40 — client→engine 36, engine→client 5 (`mcp_message` counted on both) | `:5097` |
| engine→client requests incl. runtime | 13 (5 typed + 8 in `sdk.mjs`) | §4 |
| `query()` options | 69 | `:1552-2490` |
| `Query` methods | 30 | `:2892` |
| tool input schemas in `sdk-tools.d.ts` | 44 (44 outputs, 90 exports) | `ToolInputSchemas` |
| `BUILTIN_TOOL_NAMES` | 54 | `:216` |
| bundle `.js` modules | 2,435 (2.1.303) → 2,463 (2.1.304); none of the counts above changed in 0.3.304 | `scripts/bun_split.py`, [99](99-sources.md) §E |
| `HOOK_EVENTS` | 33 | `:975` |
| `PermissionMode` | 6 | `:2529` |
| `subtype:"…"` literals in the bundle | ~160 (~185 counting `subtype ===` comparisons, 추정) | `chunk-*.js` grep |

**In the bundle, not in the types** (the analogue of Codex's experimental methods, `docs/99` §E.2):

- remote / bridge: `remote_tool_call`, `remote_plumbing_call`, `remote_tools_announce / probe /
  reannounce`, `remote_control`, `remote_control_work_secret`, `register_device_hooks`,
  `upload_device_hook_template`, `bridge_status / state`, `cloud_session_status / delta`,
  `claim_session`, `end_session`;
- TUI ↔ worker: ~25 `ui_*` (`ui_invalidate, ui_toast, ui_panes, ui_render, ui_press,
  ui_attach / detach …`), `side_question`, `get_plan`, `dev_intent`, `set_cwd`, `add_directory`,
  `list_directory`, `stage_file`, `poll_event`, `fork_conversation`, `rewind_conversation`,
  `get_workspace_diff`, `export_conversation`, `generate_session_title`, `submit_feedback`,
  `set_proactivity_level`, `set_prompt_suggestions_paused`, `set_mcp_permission_mode_override`
  (a `Query` method exists; the union lacks it);
- auth: `claude_authenticate`, `claude_oauth_callback`, `claude_oauth_wait_for_completion`,
  `mcp_authenticate`, `mcp_clear_auth`, `mcp_oauth_callback_url`, `oauth_token_refresh`,
  `host_auth_token_refresh`;
- Chrome and dialogs: `get_chrome_browsers / dialog`, `select_chrome_browser`,
  `set_chrome_browser_hints`, `get_memory / sandbox / skills_dialog`, `get_status`;
- system notifications: `model_fallback`, `model_consent_fallback`, `microcompact_boundary`,
  `turn_starting / preempted / duration / handoff_available`, `post_turn_summary`, `task_summary`,
  `stop_hook_summary`, `away_summary`, `memory_saved`, `account_memory_saved`, `message_rated`,
  `init_milestone`, `instruction_size_warning`, `vcs_state_changed`, `session_title_changed`,
  `session_metadata`, `scheduled_task_fire`, `per_turn_effort_changed`, `peer_message_hold`,
  `permission_check_status`, `permission_retry`, `file_snapshot`, `file_attachments_missing`,
  `code_change_published`, `agents_killed`, `api_error`, `read_divider`, `rewind_stand_in`,
  `channel_enable`, `ultrareview_launch`, `tool_host_result`.

~~**In the types, not found as a bundle literal**: `get_binary_version`, `set_color`,
`seed_read_state`~~ — **refuted 2026-10-19 (late)**: the engine spells its subtypes as zod literals
`A("get_binary_version")`, `A("set_color")`, `A("seed_read_state")` (`chunk-4qs43hr1.js`, whose
`.describe()` strings are the `sdk.d.ts` doc comments verbatim — the types are generated from these
schemas) and lists all three in a per-subtype boolean table (`ZC`, `chunk-8w3jrzn0.js`). The first
search matched `subtype:"<name>"` only ([99](99-sources.md) §D). The engine-originated subtypes
confirmed at direct `type: "control_request"` construction sites are `can_use_tool`, `initialize`,
`interrupt`, `mcp_message`, `request_user_dialog`; the rest go through a `sendRequest(...)` helper.

> 📌 **In one line.** Codex's generated schema was a filtered view counted at 107 / 10 / 86.
> Claude Code's `sdk.d.ts` publishes 40 control subtypes and 39 messages while the binary runs two
> to four times as many, and nearly the whole control surface used by the Remote Control bridge and
> the TUI–worker split lies outside the types. The three structural differences: no
> Thread/Turn/Item (flat `session_id` + `uuid` + `parent_tool_use_id`); a request union that does
> not encode direction; and an `initialize` that injects hooks, MCP servers, agents and skills
> instead of negotiating capabilities.
