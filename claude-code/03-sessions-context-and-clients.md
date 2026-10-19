# 03. Sessions, context and clients — what persists, what loads, and who drives the engine

> Sources: official docs as Markdown (`docs:<page>#<section>` = `https://code.claude.com/docs/en/<page>.md`,
> read 2026-10-19), `@anthropic-ai/claude-agent-sdk` 0.3.303 (`sdk.d.ts:N`, `bridge.d.ts`), and the
> 2.1.303 binary's split modules (`chunk-*.js`, strings and identifiers only). Nothing was executed.
> Grades: ✅ read · 📣 the docs' behavioural claim · 추정 inference.
>
> Codex analogues: [`docs/02`](../docs/02-app-server-protocol.md) §4 (Thread/Turn/Item persistence,
> the 60-second unload), [`SYNTHESIS`](../SYNTHESIS.md) §2.9 (one engine, many clients).
> [`harness-artifacts/03`](../harness-artifacts/03-tool-use-patterns.md) §2 already records cache
> placement, the auto-compact margin, time-based microcompaction and the persisted-output flow;
> this document builds on it rather than repeating it.

## 1. Session persistence

**Where.** `~/.claude/projects/<project>/<session-id>.jsonl`, where `<project>` is the working
directory with non-alphanumerics replaced by `-` and truncated-plus-hashed past 200 characters
(`docs:sessions#where-transcripts-are-stored`) ✅. The binary agrees (`O(w,"projects",m)` →
`` `${s}.jsonl` ``, `chunk-5gektv5j.js`); subagents and workflow agents write `` `agent-${id}.jsonl` ``
(`chunk-y1msp0ps.js`, `chunk-86sy5g2n.js`). `CLAUDE_CONFIG_DIR` relocates the tree;
`CLAUDE_CODE_PROJECT_DIR_NAME` (≥2.1.234) pins one project directory for every cwd.

**What a line holds.** The docs say only that the entry format "is internal … changes between
versions". The binary's record object (`chunk-4jsg44k7.js`): `{parentUuid, logicalParentUuid,
isSidechain, teamName, agentName, promptId, agentId, sessionKind, userType, entrypoint, cwd,
sessionId, version, gitBranch, slug, …message}`; `type` is `user | assistant | system | attachment`,
a user line can be `isCompactSummary`, a system line `subtype: "compact_boundary"` with
`compactMetadata` ✅. A session-summary sidecar keeps `isSidechain, createdAt, cwd, firstPrompt`
set-once and `customTitle, aiTitle, gitBranch, tag` last-wins (`sdk.d.ts:825`). The bundled skill
text says the same: "`~/.claude/projects/<sanitized-cwd>/*.jsonl`. Each line is a JSON object"
(`chunk-qmy61ttx.js`).

**Resume, continue, fork** (`docs:sessions`) ✅:

| Entry | Semantics |
|---|---|
| `claude --continue` | newest session in the current directory |
| `--resume <id \| name \| transcript path>`, `/resume` picker (`Ctrl+W` all worktrees, `Ctrl+A` all projects, `Ctrl+B` branch filter), `--from-pr` | id lookup: current project and worktree first, then other projects only when exactly one matches; `-p`, SDK and `/loop` sessions are hidden from the picker and from `--continue` (`-p --continue` sees them) |
| Restored | full history (an interrupted tool call is marked "cut off"; `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` re-runs it), model, `--agent`, permission mode (terminal, non-`-p` only), goal, unexpired scheduled tasks. **Not** restored: `--mcp-config`, `--settings`, `--plugin-dir`, `--add-dir`, `--fallback-model` |
| `/branch [name]` | **copies the transcript and the same process writes to the new file** — "allow for this session" approvals, running background subagents, Bash jobs and the Remote Control connection follow the branch |
| `--fork-session` | a new process; session approvals do not carry over. Opening one session in two terminals without forking interleaves both into one transcript |
| SDK | `resume`, `continue`, `forkSession`, `sessionId` (UUID, only with fork), `resumeSessionAt` (truncate to a chain-entry uuid), `resumeDropsTurn` (allowed only when the cut is exactly one turn, otherwise "Resume rejected by --resume-drops-turn:"), `persistSession` (default true → `--no-session-persistence`), `sessionStore` (@alpha; local write then adapter **dual-write**; incompatible with `persistSession: false`) — `sdk.d.ts:1625-2183`. `forkSession()` "remapping every message UUID and preserving the parentUuid chain … start without undo history" |

**Rewind and checkpoints** (`docs:checkpointing`) ✅: a checkpoint per turn-starting prompt, file
snapshots for the last 100 (`file-history/<session>/`), stored with the conversation so `/rewind`
works after resume. `Esc Esc` offers restore conversation / code / both, summarize from here / up to
here. Not restored: Bash-made changes, subagent edits (except foreground fork skills), symlinks. A
rewind returns to an already-cached prefix, so it is cheaper than compaction
(`docs:prompt-caching#rewinding-the-conversation`).

**Names and export**: `--name`, `/rename`, an AI title (replaced when a plan is accepted), a default
display name `<dir>-<2 chars>` (≥2.1.196, not a resume handle); `/clear [name]` saves the previous
session and lists `/resume <id> (previous session)` in the rewind menu; `/export` renders for
people, scripts use `claude -p --resume <id> --output-format json`.

**Retention — the counterpart of Codex's 60-second unload.** There is no in-memory unload timer:
the process is the session, and a dropped session is reloaded from disk. The disk rules
(`docs:claude-directory#cleaned-up-automatically`) ✅: `cleanupPeriodDays` default 30, minimum 1, `0` a
validation error; the sweep covers transcripts, `tool-results/`, `file-history/`, `debug/`,
`tasks/`; `sessions/` holds one file per running session (deleted on exit, crash leftovers cleaned on
the next start); auto memory is excluded; **Claude Desktop and Cowork transcripts are kept regardless
of age**, capped only by `desktopSessionCleanupPeriodDays` (≥2.1.248; the bundle's schema text:
"Retention ceiling in days for session transcripts created or last written by a desktop-host
surface", `chunk-c9s0jh80.js`). `--bare` skips the sweep, and the sweep aborts when the retention
period cannot be determined (OTel `retention_sweep`). The nearest thing to an unload window is the
Remote Control server's **~4-hour** resume window after it stops
(`docs:remote-control#resume-sessions-after-stopping-the-server`) — a server-side lifetime (추정).

## 2. Context lifecycle

**What loads at start** (`docs:context-window#what-the-timeline-shows`, `docs:memory`) ✅, in
order: a managed `CLAUDE.md` (`/etc/claude-code/CLAUDE.md` or managed-settings `claudeMd`) →
`CLAUDE.md` + `CLAUDE.local.md` from the root down to cwd (4 MiB cap, `@import` four hops deep, an
external import asks once) → `.claude/rules/*.md` without a `paths:` key → `AGENTS.md` (≥2.1.277,
default `claude-md-or-agents-md`) → auto memory `MEMORY.md`, first 200 lines / 25 KB → MCP tool
**names only** (schemas deferred; with `ENABLE_TOOL_SEARCH=auto` they preload when they fit in 10 %
of the window) → one-line skill descriptions (not re-injected after `/compact`) → a git status
snapshot. Subdirectory `CLAUDE.md` files and `paths:`-scoped rules enter as messages when their
files are read, so compaction summarises them.

**Compaction triggers** (`docs:model-config#default-auto-compact-thresholds`) ✅: at the model
limit by default; native 1M models (Fable, Sonnet 5+, Haiku 5.5, Opus 4.7+) compact at **~967K**;
non-1M Sonnet/Opus 4.6 and `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` at 200K; cloud sessions "as it
approaches"; `/autocompact 500k` (saved per model in `modelSettings`), `autoCompactWindow`,
`--autocompact`. **Idle compaction** (≥2.1.290, `idleCompaction`): interactive terminal + 1-hour
cache TTL + flag fetch available + ≥200K tokens (`CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS`) + about 54
minutes idle → summarise just before the cache expires (`docs:settings-reference#idlecompaction`);
the bundle's constants `i1o=200000, c1o=0.95, p1o=60000` and strings "Compacted while idle, before
the prompt cache expired" / "Compacted after an hour idle, using a summary" (`chunk-4jsg44k7.js`).

**0.3.304 (2026-10-19 late)**: the `get_context_usage` answer's rows gain a stable `id` enum of 13
values (`system_prompt … messages, autocompact_buffer, compact_buffer, free_space` — "match a
particular row on this", "treat an unknown value as absent"), a per-server `mcpInstructions[]`, and
`pluginId` / `path` on agents and skills, the last three "present only where the CLI answers on its
own stdio and no server stores or forwards the reply" — i.e. absent on cloud, self-hosted runner and
Remote Control connections. The producer is in the 2.1.304 bundle (`chunk-rncrmfyt.js`, the three
buffer ids 0 → 2/4/2 hits). The compaction thresholds above did not change ([99](99-sources.md) §E).

**What survives compaction**: the system prompt and output style; root `CLAUDE.md`, unscoped rules
and auto memory (re-injected from disk); a fresh git snapshot; the plan; the five most recently
modified files re-read (paths only above 5,000 tokens); invoked skill bodies (5,000 per skill,
25,000 total, oldest dropped); `SessionStart` `compact` hook output. The summary request inherits
the session's thinking setting (≥2.1.198).

**What `/compact` costs** (`docs:prompt-caching#compacting-the-conversation`): a **separate
request** with the same system prompt, tools and history plus summarising instructions. With a warm
cache the prefix is read for "a fraction"; after the TTL (resuming an old session) it is a full
uncached input. The next turn re-caches only the short summary.

**What breaks the cache and what keeps it** (`docs:prompt-caching`) ✅. Breaks: a model switch
(per-model caches; a confirmation only while warm; `opusplan`, automatic fallback and a skill's
`model:` frontmatter all switch), an effort change (Opus 5.5 / Sonnet 5.5 / Haiku 5.5 / Fable 5.1
with an API key or subscription are exempt from 2.1.260), the fast-mode header, adding or removing
an MCP server while tool search is off, a tool-name deny rule, image accumulation, an upgrade.
Keeps: **a `CLAUDE.md` edit (the cache stays, and the edit does not apply until `/clear`,
`/compact` or a restart)**, a permission-mode change, output style, skill invocation (appended as a
user message), `/recap`, `/rewind`. TTL 5 minutes by default, 1 hour for subscribers,
`promptCacheTtl` / `subagentPromptCacheTtl` (≥2.1.242); verify with
`usage.cache_creation.ephemeral_1h_input_tokens`. The cache is effectively scoped to machine plus
directory (the auto-memory path sits in the system prompt, cwd and OS in the first message) — SDK
fleets are told to move the memory path out of the system prompt.

**Auto memory** (`docs:memory#auto-memory`) ✅: frontmatter `type: user | feedback | project |
reference`, a `modified` ISO timestamp (≥2.1.214); the directory is keyed to the **git repository**
(worktrees share it), `autoMemoryDirectory`; off by default in background, nested and self-hosted
sessions; a write past the cap succeeds but returns a rewrite error; not passed to subagents except
forks. The bundle carries an **index-based recall** the docs do not describe: an attachment
`relevant_memories { memories[].path, content, mtimeMs }`, `account_memory_recall`,
`cowork_memory_context` (leg `laptop`), telemetry `memory_recall_select { via_index,
below_relevance_floor, no_servable_hits, index_query_term_count }`, candidates `.slice(0,5)`
(`chunk-4jsg44k7.js`) — 추정: per prompt, a local index picks up to five topic files to attach.

**`context_hint`**: absent from the four docs pages; present in the bundle as a beta
`context-hint-2026-04-09` (`chunk-pj5cyqhw.js`): when the estimated saving clears a threshold the
request carries `{context_hint: {enabled: true, target_tokens_saved}}`; the error path logs
`tengu_context_hint_reject { preCompactTokenEstimate, postCompactTokenEstimate, mcApplied }` and
`tengu_context_hint_busy_fallback`; microcompaction has a `trigger: "context_hint"` →
"[KEEP-RECENT MC] context_hint trigger, cleared N tool results" (`chunk-h7kwn2ss.js`,
`chunk-pretnsp4.js`). 추정: a server-initiated request to shrink context, answered by clearing tool
results and retrying.

## 3. The clients that drive the engine

| Client | Transport | Where the engine runs | What it adds · evidence |
|---|---|---|---|
| Terminal CLI | TTY | local process | picker, `/rewind`, terminal-only commands (`terminal_slash_commands` is declared in the `initialize` reply, `sdk.d.ts:6051~`) |
| `-p` / Agent SDK (TypeScript, Python, CLI) | child process over stdio, stream-json | a local child (`pathToClaudeCodeExecutable`, `executable: bun \| deno \| node`, `extraArgs`, `env`) | `canUseTool`, hook callbacks, in-process MCP, the `sessionStore` mirror, control requests (`get_usage`, `reload_plugins { hold_on_cache_impact }`); identified by `CLAUDE_CODE_ENTRYPOINT` (`chunk-31d3wf0j.js`) |
| Claude Desktop Code tab (`claude-desktop`, `-3p`) | embedded SDK + `node-pty` ([`harness-artifacts/02`](../harness-artifacts/02-desktop-shells.md) §2) | local, **a CLI copy the app downloads itself** (📣 "runs its own copy of Claude Code, which has its own version number", `docs:desktop`) | panes, side chat, worktrees, computer use, Dispatch, "Open in > Cloud" (the conversation moves as a summary), auto-connect to Remote Control; transcripts exempt from the sweep; a desktop-only 1M auto-compact map `{"600k","500k"}` (`chunk-4jsg44k7.js`, 추정) |
| VS Code (`claude-vscode`) | extension ↔ CLI | local | `vscode://anthropic.claude-code/open` |
| Remote Control | local → Anthropic API, **outbound HTTPS only**, polling after registration; the server relays streams to web and mobile | **local** (execution and filesystem stay local; the transcript is stored server-side while connected) | `claude remote-control` (server mode, many sessions), `--remote-control`, `/remote-control`; `bridge.d.ts`: `POST /v1/code/sessions` → `cse_*`, `POST …/{id}/bridge` worker JWT (`session_ingress_token`), SSE inbound plus write ACKs, an `outboundOnly` mirror, callbacks `onSetModel / onSetPermissionMode / onSetMaxThinkingTokens / onRenameSession / onInterrupt / onStopTask`, `claudeCodeVersion` → `claude_code_version`; `ultracode` arrives as a bridge `apply_flag_settings` (`chunk-06bgpawv.js`). Not available on Bedrock / Vertex / Foundry / gateways, ZDR or HIPAA |
| Cloud sessions (claude.ai/code, mobile, Desktop Cloud, Projects, Slack) | browser or app ↔ Anthropic | **a cloud VM** (or a self-hosted runner) | `--cloud "task"` (clones from GitHub, uploads the local tree otherwise), `-p --cloud <id \| url>` queues a message, `--teleport <id>` / `/teleport` **copies** the conversation and branch down (one way; clean git, same repo, pushed branch, same account); bundle flags `--attach-serve <cse_…>` "serve-only headless launch (… stream-json)", `--sdk-url`; entrypoints `remote \| remote_mobile \| remote_desktop \| remote_projects \| claude-in-teams` → surface `web` |
| Channels | an MCP server (stdio plugin, Bun) → `notifications/claude/channel { content, meta }` | local | injected as a `channel` block with `source` and key-values, a reply tool, **permission relay** `claude/channel/permission` + `notifications/claude/channel/permission { request_id, behavior }` (`chunk-6bp7hdav.js`); double gate `--channels` and `channelsEnabled`, sender allowlist pairing |
| Cross-session messaging | same machine: Unix socket / named pipe (`/tmp/cc-socks-<uid>`, `--messaging-socket-path`, `CLAUDE_CODE_MESSAGING_SOCKET/_TOKEN`); other machines and cloud: Anthropic relay over the Remote Control connection | each session local | `ListAgents` / `SendMessage`, `/list-agents` (`/peers`), `/status` peer address |
| Agent teams | mailbox JSON `~/.claude/teams/{team}/inboxes/{agent}.json` | local (in-process or tmux split) | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` / `--agent-teams` plus a flag `tengu_amber_flint` (`chunk-sndz13gf.js`); team name `session-<8 chars>`, `config.json` deleted on exit, `tasks/` swept |
| Dynamic workflows | an isolated runtime inside the session | local | the script writes under `~/.claude/projects/<session>/`; 16 concurrent (`CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS` 1–256), 1,000 agents per run, `parallel()` 4,096, a 5,000 ms stagger to share the prefix cache |
| Deep links `claude-cli://` | OS URL handler → terminal | local | registered when the first prompt is sent (`~/Applications/Claude Code URL Handler.app`, a `.desktop` file, HKCU); fills the prompt only, with a "Prompt from an external link" warning; `disableDeepLinkRegistration: "disable"` (`chunk-c9s0jh80.js`) |
| Agent view / Dispatch | `claude agents`, `claude attach \| stop \| rm`, `--bg`; phone → Cowork Dispatch → a Code session | local background (a supervisor, `~/.claude/jobs/`) | Desktop's "Work across sessions" sees only sessions the desktop launched |

> 📌 **`--cloud` and `--remote-control` sound alike and put the engine in opposite places**, and the
> docs say so. Desktop re-attaches to the existing claude.ai session on a Remote Control resume
> rather than adding a new one. Switching conversations from Remote Control (`/resume`, `/teleport`)
> sends the device only new messages, not the prior history — the server-side transcript is the tail
> of the connected conversation, not a full mirror (추정).

## 4. Coordinating several instances

- **Addressing**: a session name (`--name`, `/rename`, or a generated `hostname-graceful-unicorn`),
  a short identifier appended when names collide; a team's names are chosen by its lead. Unlike
  Codex's `spawn_agent` / `send_message` and Gas Town's mail, **the medium splits three ways**: a
  local socket, team mailbox files, or the Anthropic relay.
- **Limits**: plain text only; about 1M characters on the same machine; a 50-message inbound queue;
  loop suppression; no crossing of a session's container or WSL boundary. `crossSessionInbound:
  deliver | hold | refuse`, `isolatePeerMachines` (approval before sending to another machine; the
  bundle's `circuitBreaker: "isolatePeerMachines"`); denying `SendMessage` also removes subagent and
  team messaging.
- **No proxy approval**: 📣 "A teammate can't approve a permission prompt or supply consent on your
  behalf"; routing a denied action through another session is forbidden; the auto-mode classifier
  treats relayed approval claims as untrusted and pre-screens every team message
  (`docs:agent-teams#messages-between-agents`). A teammate's permission prompt appears in the lead
  session for a person to answer (only plan approval is automatic). The only exceptions are **human
  paths**: the Channels permission relay (allow-listed senders) and a Remote Control device.
- Teammates do not receive the lead's history; they reload CLAUDE.md, MCP and skills; their cache TTL
  sits outside the main bucket at 5 minutes.

> 📌 This is [`SYNTHESIS`](../SYNTHESIS.md) §2.7's "on by default" property at fleet cardinality,
> stated by the vendor as a rule rather than left to the wrapper: the three orchestrators that
> switched approvals off ([`agent-ux/08`](../agent-ux/08-primitives-rendered.md) §2) did so from
> outside the engine; inside it, another session cannot answer for you.

## 5. Cost and usage on the wire

`SDKResultSuccess` (`sdk.d.ts:5857~`) ✅: `duration_ms`, `duration_api_ms`, `ttft_ms`, `num_turns`,
`stop_reason`, `total_cost_usd` (cumulative over `query()`), `usage` (**the main loop only**, no
subagents or sidechains), `modelUsage` (per model, including subagents, compaction and workflows:
`inputTokens, outputTokens, thinkingTokens?, cacheReadInputTokens, cacheCreationInputTokens,
webSearchRequests, costUSD, contextWindow, maxOutputTokens, canonicalModel, provider, costBasis:
list | managed | unknown`), `permission_denials`. The control request `get_usage` returns
`session { total_cost_usd, total_api_duration_ms, model_usage }`, `subscription_type` and
`rate_limits.five_hour / seven_day { utilization, resets_at }` (`skip_behaviors` can skip the
seven-day transcript scan). `/usage` dollars are a **local list-price computation** (contracted
when a managed `modelPricing` exists), reset by `/clear` (≥2.1.211), ×1.1 for data residency, a
`Prompt cache (main)` line (≥2.1.251). OTel: `claude_code.cost.usage`, `claude_code.token.usage`.
Desktop metering (추정): the `modelPricing.{multiplier, overrides}` keys REA surfaced in the
desktop shell pair with `costBasis: 'managed'`, so Desktop reads the same `modelUsage` /
`get_usage` and shows subscribers only the rate limits.

## 6. Drift between docs, SDK and binary

- **Bundle or SDK only**: the `context_hint` beta; `sessionStore` dual-write (@alpha);
  `--resume-session-at` / `--resume-drops-turn` (`hideHelp()`); `--attach-serve`, `--sdk-url`,
  `--pool`, `--environment`, `--workload`, `--teammate-mode`, `--correlation-id`,
  `--forward-home-settings`; a `storageV5` key-value backend (`transcript` namespace
  `{sessionId, agentId}`, `chunk-46wnjrvn.js` — hosted storage, 추정); index-based `memory_recall`
  and `account_memory_recall` (claude.ai account memory flowing in); result-frame fields
  `resume_reason` (`host_draining, checkpoint_restore, container_recreated`), `warm_spare_claimed`,
  `first_stream_post_*`, `user_message_uuid(s)`, `initialize` `capabilities` (e.g.
  `interrupt_cancel_queued_v1`), `view_mode: 'focus'` — all hosted-runner plumbing.
- **Docs ahead of the SDK**: the `betas` comment "`context-1m-2025-08-07` … (Sonnet 4/4.5 only)"
  (`sdk.d.ts:1747`) predates the current 1M-by-default docs. `isSidechain` is a transcript field
  only; it appears in SDK comments, not in a message type.
- **Confirmed in all three**: `cleanupPeriodDays` / `desktopSessionCleanupPeriodDays`,
  `CLAUDE_CODE_TRANSCRIPT_LOCAL_GC` (no rewrite below a 10 % saving), the deprecated `--remote`
  alias, the channel permission relay (2.1.234), deep-link registration.
- **Not found**: the server's `context_hint` response format; which client enables `storageV5`;
  the full `sessionKind` list that decides the Desktop transcript exemption.
