# 02. Approval and permissions — the gate, read from the SDK types and the binary's strings

> Sources: `@anthropic-ai/claude-agent-sdk` 0.3.303 (`sdk.d.ts`, cited as `sdk.d.ts:N`), the Claude
> Code 2.1.303 binary's split modules (cited by `chunk-*.js` name, strings and identifiers only),
> and the official docs as Markdown (`https://code.claude.com/docs/en/<page>.md`, cited as
> `docs:<page>#<section>`). Nothing was executed. Grades: ✅ read · 📣 the docs' claim about
> behaviour · ⚠️ not determinable statically · 추정 inference.
>
> The analogue in the Codex study is [`docs/02`](../docs/02-app-server-protocol.md) §7 ("where
> humans step in"); the Strands probe of six gate properties is [`strands/07`](../strands/07-security.md) §3;
> the seventh property is [`SYNTHESIS`](../SYNTHESIS.md) §2.7. [`harness-artifacts/03`](../harness-artifacts/03-tool-use-patterns.md) §2
> recorded the rule grammar, the "don't ask again" button and the auto-mode classifier call from a
> bundle reading; this document is the contract those strings implement.

## 1. The decision pipeline for one tool call

The SDK documentation states the order outright (`docs:agent-sdk/permissions#how-permissions-are-evaluated`):
**hooks → deny rules → ask rules → permission mode → allow rules → `canUseTool`**. The CLI docs say
the same thing in other words: "PreToolUse hooks run before the permission prompt", "A hook that
exits with code 2 stops the tool call before permission rules are evaluated"
(`docs:permissions#extend-permissions-with-hooks`); "Rules are evaluated in order: deny, then ask,
then allow. The first match … rule specificity doesn't change the order" (`#manage-permissions`) ✅.

| Step | Can short-circuit with | Cannot |
|---|---|---|
| `PreToolUse` hook | `deny` / exit 2 (beats allow rules); `ask` (forces a prompt, which also blocks the auto-mode classifier's implicit approval); `defer` (`-p` only → `stop_reason: "tool_deferred"`); `updatedInput` rewrites the call | `allow` does not pass deny/ask rules, `requiresUserInteraction`, critical-path `rm`, or plan-mode writes |
| deny rules | block in every mode, `bypassPermissions` included; a managed deny cannot be undone by `--allowedTools` (`docs:permissions#settings-precedence`) | — |
| ask rules | beat allow rules; force the callback or prompt | under `dontAsk` they become deny |
| mode | `bypassPermissions` approves everything here except critical paths; `acceptEdits` approves edits; `plan` forces writes to the callback | — |
| allow rules | approve; read-only tools and edits inside the working directory resolve here without a rule | network-path reads, critical-path deletes |
| classifier (`auto`) | everything not resolved above, in the order `docs:permission-modes#how-the-classifier-evaluates-actions` gives | a matched ask rule and `requiresUserInteraction` never reach it |
| `canUseTool` / `can_use_tool` | the host's (human's) final decision; runs **concurrently with the `PermissionRequest` hook — "whichever decides first applies"** (`docs:hooks#permissionrequest`) | not called under `dontAsk` or `permissionPrompts: 'none'` → deny |
| sandbox | an OS boundary; in the auto-allow modes it *replaces* the bare `Bash` prompt, otherwise it enforces after approval | Read/Edit/WebFetch, hooks and MCP servers run outside it |

**Precedence among hook answers** is `deny > defer > ask > allow`
(`docs:hooks#pretooluse-decision-control`). The binary's rank table is
`var ybe={deny:3,ask:2,allow:1,none:0}` in `chunk-4jsg44k7.js`; `defer` is a separate branch
(`case "defer": … permissionBehavior, hookSource`) handed to the callback side and applied only when
`strictestHookAnswer?.behavior !== "deny"` — deny covers defer, defer covers ask and allow, which
matches the documented order ✅. One documented exception to the rule layer: a mod's `tool.check`
answers *after* rules and hooks and, outside managed/Team/Enterprise deployments, can approve past a
deny rule (`docs:permissions#precedence-among-rules-hooks-and-mods`) — recorded as the hole it is.
**2026-10-19 (late):** the page now says deny rules hold over the mod on managed/Team/Enterprise
"by default, and your organization can change that"; and **2.1.304** adds the opposite lever —
a mod may answer `{decision: "ask", decider: "person"}`, after which "only the permission dialog
or a host's callback can approve the ask, and it is refused with the mod's reason where nobody can
be asked" (changelog; the binary's `decider==="person"` branch sets `personOnly`, `hooksMayRefuse`,
`suppressAlwaysAllowRule`, 0 → 2 hits, [99](99-sources.md) §E). A mod can widen the gate outside
managed deployments and can now narrow it to a human anywhere.

## 2. The wire shape of an approval

The engine asks the host with `control_request { subtype: "can_use_tool" }` (`sdk.d.ts:4875-4930`;
zod original in `chunk-pj5cyqhw.js`: `subtype:A("can_use_tool"), tool_name, mcp_server, input,
permission_suggestions, blocked_path, decision_reason …`) ✅:

| Field | Meaning |
|---|---|
| `tool_name`, `input`, `tool_use_id`, `agent_id?` | the call; `agent_id` when a subagent is asking |
| `mcp_server? { name, source }` | "Key trust decisions on `source`, not on the name" (`sdk.d.ts:245-252`) |
| `permission_suggestions?: PermissionUpdate[]` | the rule set an "always allow" answer sends straight back |
| `blocked_path?` | a path outside the working directories |
| `decision_reason?` + **`decision_reason_type?`** | enum `'rule' \| 'mode' \| 'subcommandResults' \| 'permissionPromptTool' \| 'hook' \| 'asyncAgent' \| 'sandboxOverride' \| 'workingDir' \| 'safetyCheck' \| 'classifier' \| 'other'` — "Lets SDK hosts make policy (e.g. auto-deny safetyCheck) without parsing decision_reason text" (`sdk.d.ts:4891`) |
| `classifier_approvable?`, `suppress_always_allow_rule?`, `default_to_no?`, `matched_ask_rule?`, `requires_user_interaction?`, `title`, `display_name`, `description` | rendering and policy hints |

The host answers with `PermissionResult` (`sdk.d.ts:2552-2564`; zod
`behavior:A("allow") … updatedInput, updatedPermissions, toolUseID, decisionClassification` |
`behavior:A("deny"), message, interrupt?`) ✅:

- **`allow`** with optional `updatedInput`, `updatedPermissions`, `decisionClassification`
  (`'user_temporary' | 'user_permanent' | 'user_reject'`);
- **`deny`** with a required `message` (delivered to the model as the reason) and optional `interrupt`;
- returning `null` is allowed only when the host already answered out of band; otherwise "the tool
  stays blocked indefinitely — permission prompts have no park deadline" (`sdk.d.ts:226`);
- a result that fails the schema is replaced by the engine with
  `{behavior:"deny", message:"The canUseTool callback returned an invalid permission result…"}` (`chunk-4jsg44k7.js`).

`PermissionUpdate` (`sdk.d.ts:2571-2600`): `addRules | replaceRules | removeRules { rules[{toolName,
ruleContent?}], behavior }`, `setMode { mode }`, `addDirectories | removeDirectories { directories[] }`,
each with `destination: 'userSettings' | 'projectSettings' | 'localSettings' | 'session' | 'cliArg'`.
`setMode: 'bypassPermissions'` is honoured only if the session was launched in that mode; otherwise it
is a no-op with a logged reason ("Ignoring permission update: setMode 'bypassPermissions' rejected —
mode is not available (disableBypassPermissionsMode set, or session not launched in bypassPermissions
mode)", `chunk-8fgrwnc5.js`) and "never persisted as `defaultMode`".

> 📌 **Rendered (2026-10-19).** The Claude Desktop 2.42304.2 Code tab maps this request one-to-one
> into its card state ([`agent-ux/02`](../agent-ux/02-claude-desktop.md) §3.1): `'mode'` and `'hook'`
> get copy of their own, `suppress_always_allow_rule` removes the standing options, and the card's
> answer never carries `decisionClassification`. The renderer also reads fields this union does
> not declare — and **the engine sends them**: the request builder in `chunk-88j6ans0.js` (2.1.303
> and 2.1.304 alike) adds `decision_reason_code`, `decision_reason_rule_source`, the hook triple
> `decision_reason_hook_event / _source / _plugin_id`, `server_policy_ask_only`, `tool_kind:
> "browser"`, `server_prompt`, `provenance_prompt_line`, `plugin` and `computer_folder`, none of them
> in `sdk.d.ts` 0.3.303 or 0.3.304. Only `via_host_cli_launcher` is the desktop host's own (0 hits in
> both binaries). The types lag the engine here, as they do for `set_mcp_permission_mode_override`
> ([99](99-sources.md) §D, corrected 2026-10-19 late).

> 📌 **Against Codex's `ReviewDecision`.** Codex's `accept / acceptForSession / decline / cancel /
> acceptWithExecpolicyAmendment` and Claude Code's `allow + updatedPermissions[addRules,
> destination: 'session' | 'localSettings' | …]` are the same idea — an approval carries the policy
> amendment it creates — and `acceptForSession` is `destination: 'session'`. Claude Code's answer is
> wider in four ways: (a) **`updatedInput` lets the host rewrite the input it approves**, (b)
> `interrupt` ends the turn, (c) `decision_reason_type` lets a host branch on *why* it was asked, (d)
> `setMode` and `addDirectories` ride in the same answer. Codex's `cancel` has no counterpart; a
> `deny + message` reaches the model as text.

## 3. Modes

`PermissionMode = 'default' | 'acceptEdits' | 'bypassPermissions' | 'plan' | 'dontAsk' | 'auto'`
(`sdk.d.ts:2529`; `manual` is an alias of `default`) ✅.

| Mode | Auto-approves | Disabled by policy | Notes |
|---|---|---|---|
| `default` | reads, built-in read-only commands | — | the interactive terminal and VS Code default is **`auto`** since 2026-W32 (📣 `docs:security#permission-based-architecture`) |
| `acceptEdits` | edits plus `mkdir`/`touch`/`mv`/`cp`-class commands inside the working directory | — | protected paths excluded |
| `plan` | reads, and (where auto is available) classifier-approved commands | — | edits are forced to `canUseTool`: "never auto-approved … even when an allow rule matches or a `PreToolUse` hook returns `allow`" (`docs:agent-sdk/permissions#plan-mode-plan`). Exception: an interactive terminal with bypass in its mode cycle does not enforce the plan block |
| `auto` | everything, subject to the classifier | `permissions.disableAutoMode: "disable"` (`sdk.d.ts:9331`) | §3.1 |
| `dontAsk` | only what rules approve; anything that would prompt is **denied** | — | `AskUserQuestion`, `requiresUserInteraction` MCP tools, critical-path deletes and network-path reads are denied too; cloud sessions ignore the mode |
| `bypassPermissions` | everything, protected-path writes included | `permissions.disableBypassPermissionsMode: "disable"` (`sdk.d.ts:6987`, effective from any scope) | the SDK requires `allowDangerouslySkipPermissions: true` (`sdk.d.ts:2037`); refused under root/sudo ("cannot be used with root/sudo privileges for security reasons", waived inside a recognised sandbox); deny rules, ask rules, critical-path deletes and `requiresUserInteraction` still prompt |

### 3.1 The auto-mode classifier

A separate API call (`chunk-4jsg44k7.js`): `querySource: "auto_mode"`, `max_tokens: 8192+…`,
`stop_sequences: [ke ? "</severity>" : "</block>"]`, two stages `classifierStage: "xml_s1"` →
`"xml_s2"`, a `classifierJudgesServedCall` flag, cache control on its input ✅. 📣 The model defaults
to Sonnet 5, a server setting takes precedence, and a Fable session falls back to Opus
(`docs:permission-modes#cost-and-latency`). Its input is the user messages, the non-read-only tool
calls and CLAUDE.md, with **tool results removed**; a `PostToolUse` hook can inject up to 2,000
UTF-16 units of `classifierContext` (`sdk.d.ts:2716`). Billing: Enterprise, API, Bedrock, Vertex and
Foundry pay for the classifier's tokens; where a server-side review (v2.1.271+) replaces it there is
no separate call. **Failure denies**: `"Classifier unavailable"`, `"Classifier unavailable - blocking
for safety"`, a server returning no verdict also denies, ten consecutive failures end the turn; after
three consecutive or twenty cumulative blocks the engine falls back to manual prompts. Entering
`auto` temporarily drops broad allow rules such as `Bash(*)`, `Bash(python*)`, `Agent`, `Monitor` ✅.

## 4. Hooks as a gate

`HookEvent` has **33** members (`sdk.d.ts:994`): `PreToolUse, PostToolUse, PostToolUseFailure,
PostToolBatch, Notification, UserPromptSubmit, UserPromptExpansion, SessionStart, SessionEnd, Stop,
StopFailure, SubagentStart, SubagentStop, PreCompact, PostCompact, PreModelSwitch, PostModelSwitch,
PermissionRequest, PermissionDenied, Setup, TeammateIdle, TaskCreated, TaskCompleted, Elicitation,
ElicitationResult, ConfigChange, WorktreeCreate, WorktreeRemove, InstructionsLoaded, CwdChanged,
FileChanged, DirectoryAdded, MessageDisplay` ✅.

- **Exit codes** (`docs:hooks#exit-code-output`): 0 = success, JSON applied; 2 = block (stderr is
  the reason; a JSON `allow` cannot override it); **any other code = non-blocking error, the action
  proceeds** — unless the output is schema-valid JSON, whose fields then decide. In
  `PermissionRequest` exit 2 is ignored and only the `decision` object counts.
- **JSON** (`sdk.d.ts:9803`, `SyncHookJSONOutput`): `continue` (false stops everything and
  outranks every decision field), `stopReason`, `systemMessage`, `terminalSequence`, the legacy
  `decision: 'approve' | 'block'`, `hookSpecificOutput`. `PreToolUse`: `permissionDecision: 'allow' |
  'deny' | 'ask' | 'defer'` (`sdk.d.ts:1000`), `permissionDecisionReason`, `updatedInput`,
  `additionalContext`. `PermissionRequest`: `decision { behavior:'allow', updatedInput?,
  updatedPermissions? } | { behavior:'deny', message?, interrupt? }` (`sdk.d.ts:2540`).
  `PostToolUse`: `updatedToolOutput`, `classifierContext`. `PermissionDenied` (fires only on an
  auto-mode denial): `retry: true`.
- **Timeouts** (`docs:hooks#common-fields`): `command` / `http` / `mcp_tool` 600 s by default,
  `prompt` 30 s, `agent` 60 s. A timed-out hook "renders no decision" and the tool call proceeds;
  SDK callback hooks are the opposite — their timeout blocks.
- `async: true` cannot decide ("response fields like `decision`, `permissionDecision` … have no
  effect"); `asyncRewake` runs in the background and wakes the model with exit 2 (timeout enforced);
  `once` exists only in skill frontmatter; `type: "prompt"` hooks take `$ARGUMENTS` and answer
  `{ok, reason, impossible}`, with a `model` of their own.
- `allowManagedHooksOnly` (`sdk.d.ts:7432`, managed only) drops user, project, local and plugin
  hooks (and narrows `statusLine`; `disableCommandPluginSources` follows it unless set).
  `disableAllHooks` does not reach managed hooks.
- **The two fail-open modes recorded in [`ai-sdlc/03`](../ai-sdlc/03-the-control-ladder.md) stand**:
  "a hook that can't start is a non-blocking error too … `No such file or directory`", and "A timed-out
  `command`, `http`, or `mcp_tool` hook doesn't block the tool call … don't count on a stalled hook to
  act as a gate." **New since v2.1.295**: `onFailure: "block"` turns both into blocks — the binary's
  `WDo` path logs `'blocking because onFailure is "block"'` ✅. The default is still fail-open.

## 5. Managed settings and policy

Load paths (`docs:managed-settings`; the binary's fallback `default: return "/etc/claude-code"` in
`chunk-c9s0jh80.js`) ✅: macOS `/Library/Application Support/ClaudeCode/managed-settings.json` plus the
`com.anthropic.claudecode` plist domain; Linux/WSL `/etc/claude-code/managed-settings.json` plus
`managed-settings.d/*.json` merged alphabetically; Windows `C:\Program Files\ClaudeCode\managed-settings.json`
plus `HKLM\SOFTWARE\Policies\ClaudeCode\Settings`; a server-managed source (the claude.ai console); a
`policyHelper` executable. Precedence "server-managed > MDM (managed plist / HKLM) >
managed-settings.json" (`chunk-c9s0jh80.js`), composable through `managedSourcesBehavior`. An SDK
session reads managed settings even with an empty `settingSources`, and a host can add policy of its
own through the `managedSettings` option (`sdk.d.ts:2286`).

**Keys only a managed source can set** (`docs:managed-settings#keys-only-a-managed-source-can-set`;
type comments "Read from managed settings only"): `allowManagedHooksOnly`,
`allowManagedPermissionRulesOnly` (`sdk.d.ts:7444`), `allowManagedMcpServersOnly`,
`sandbox.filesystem.allowManagedReadPathsOnly`, `sandbox.network.allowManagedDomainsOnly`,
`strictKnownMarketplaces` / `blockedMarketplaces`, `strictPluginOnlyCustomization`,
`disableSideloadFlags`, `disableCommandPluginSources`, `forceRemoteSettingsRefresh`,
`managedMcpServers`, `allowedChannelPlugins`, `policyHelper`, `availableModels` / `deniedModels` /
`availableModelsMatch`, `modelOverrides` (pricing), `pluginOrder`. Effective from any scope but
"typically managed": `permissions.disableBypassPermissionsMode`, `permissions.disableAutoMode`,
`permissions.deny`. (These are the policy keys REA surfaced as literals in the Claude Desktop shell —
[`harness-artifacts/02`](../harness-artifacts/02-desktop-shells.md) §2.1.)

What a project cannot override: every managed value ("Nothing in your own settings files or
`--settings` overrides a managed key"); the only direction allowed below is **stricter**
(`blockReadsOutsideWorkingDirectories: true`, `useAutoModeDuringPlan: false`, a lower `maxEffortLevel`
— `docs:settings#exceptions-to-managed-settings-precedence`). **Fail-closed parsing** (v2.1.282+): a
corrupt single-value restriction key is read as the restriction; a corrupt `deny`/`ask` list holds
back the same block's `allow`/`additionalDirectories`; corrupt `allowedMcpServers`,
`allowedHttpHookUrls` or `availableModels` become empty allowlists; a corrupt `forceLoginOrgUUID`
prevents login. User and project files are rejected whole instead.

> 📌 **Against Codex's `requirements.toml`.** Codex declares an allowed set and rejects configuration
> outside it, in one document. Claude Code (a) makes a managed file of the same schema the top scope,
> (b) adds per-key `allowManaged*Only` locks that say "read this key from managed only", and (c)
> reflects the lock in the prompt UI itself (`permission_suggestions` hides rule-saving options,
> `suppress_always_allow_rule`). The third axis — reading a broken policy file *as the restriction* —
> has no counterpart found on the Codex side (추정: `config_requirements` reports and refuses).

## 6. Sandbox

`SandboxSettingsSchema` (`sdk.d.ts:3520`): `enabled, failIfUnavailable, autoAllowBashIfSandboxed,
allowUnsandboxedCommands, network { allowedDomains, deniedDomains, strictAllowlist,
allowManagedDomainsOnly, allowUnixSockets, allowLocalBinding, allowMachLookup, httpProxyPort,
socksProxyPort, tlsTerminate }, filesystem { allowWrite, denyWrite, denyRead, allowRead,
allowManagedReadPathsOnly, disabled }, credentials { files[], envVars[] (deny | mask, jwt decode,
injectHosts), awsPairs, sigv4 }`. Default **off** ✅.

Per OS: macOS Seatbelt ("seatbelt: built-in (macOS)", `chunk-352tt7pq.js`), Linux/WSL2 bubblewrap
("bubblewrap (bwrap): installed/not installed", `bwrapPath`, `socatPath`), the
`@anthropic-ai/sandbox-runtime` package. 📣 The docs say it "doesn't run on native Windows", but the
binary carries an `srt-win` runtime ("Path to the srt-win binary … VENDORED_SRT_WIN_EXE",
`sandboxUser` default `srt-sandbox`, `srt-win install`, `chunk-3rfnbzz0.js`) — 추정: a Windows
sandbox behind a flag in 2.1.303. The `/sandbox` override offers `Strict sandbox mode` versus
`Allow unsandboxed fallback` (`allowUnsandboxedCommands: false` is strict). The desktop string
"Runs outside Claude's sandbox" recorded in [`agent-ux/02`](../agent-ux/02-claude-desktop.md) §3.2 is
not in the CLI; its counterpart is the Bash parameter `dangerouslyDisableSandbox` and its description
("…and this one would not (dangerouslyDisableSandbox, an excluded command, or no sandbox for this
shell)").

How the sandbox feeds back into approval ✅: (1) in the auto-allow modes the sandbox boundary
*replaces* the bare `Bash` prompt (not in `plan`); (2) a sandbox denial returns to the model naming
the denied host, and a retry with `dangerouslyDisableSandbox: true` is **a new approval request**
(`decision_reason_type: 'sandboxOverride'`, prompt title "Bash command (unsandboxed)"; `auto` sends it
to the classifier, `dontAsk` denies, `bypassPermissions` does not prompt; an ask rule
`Bash(dangerouslyDisableSandbox:true)` beats allow rules); (3) strict mode ignores the parameter;
`failIfUnavailable` refuses to start without `bwrap`. The `PermissionRequest` hook does not fire for
sandbox network prompts.

## 7. The seven gate properties

| Property ([`SYNTHESIS`](../SYNTHESIS.md) §2.7) | Claude Code 2.1.303 / SDK 0.3.303 | Grade |
|---|---|---|
| On by default | The gate is always on: the SDK's default mode is `default`, unresolved calls go to `canUseTool`, and with no callback or `permissionPrompts: 'none'` the engine logs "no approval surface in this session; permission request denied automatically" (`chunk-4jsg44k7.js`). But the interactive default is **`auto`** — the reviewer is a model unless the user changes mode. Sandbox off by default | ✅ (default reviewer is a model) |
| Fails closed on every error path | **Engine paths close**: a `null` callback result blocks forever, a schema-invalid result is replaced with deny, classifier silence/parse failure/no server verdict deny, a crashed permission check logs `"bashCommandClamp fail-closed: permission check crashed"` and denies "rather than running an unverified command", a corrupt managed key reads as the restriction. **Hook paths open by default**: exit codes other than 0/2, a missing script, a timeout and malformed JSON all proceed; `onFailure: "block"` closes them | ⚠️ mixed: engine ✅, user hooks ✗ unless opted in |
| Parses the answer as an enum | zod `behavior: A("allow") \| A("deny")`, four `HookPermissionDecision` values, three `PermissionBehavior` values; a mismatch becomes deny; a hook's non-JSON stdout is "no decision", never an approval | ✅ |
| Composes by explicit precedence | rules deny → ask → allow regardless of specificity; hook answers `deny > defer > ask > allow` (`ybe` table); the SDK's six stages; `continue: false` outranks all; across scopes "deny at any level wins" | ✅ |
| Keeps a hard deny | "Deny rules block in every mode, including `bypassPermissions`"; a managed deny survives `--allowedTools`; `dontAsk` turns ask into deny. The hole: a mod's `tool.check` can approve past a deny outside managed/Team/Enterprise | ✅ (hole named) |
| Authorizes the final input | `updatedInput` is "re-evaluated against deny and ask rules"; rule and auto-background decisions use "the input your hook returns, not the input Claude sent". No rule is stated for two `PreToolUse` hooks returning different `updatedInput` (`PostToolUse` is documented "last-write-wins", `sdk.d.ts:2716`) | ⚠️ single hook ✅, multiple hooks undetermined |
| Stays available when the rest is not | "permission prompts have no park deadline" (a lost answer keeps the tool blocked); the classifier chain is server → local → deny; `forceRemoteSettingsRefresh` refuses to start when policy cannot be fetched. What happens when the gate itself cannot start is not readable without running | ⚠️ |

> 📌 **In one line.** Claude Code's gate reads as two layers: **fail-closed inside the engine,
> fail-open by default in the user's hook layer** (`onFailure: "block"` since 2.1.295 flips it). The
> structural difference from Codex is that an approval answer can rewrite the **input**, not only the
> policy; `decision_reason_type` is the field that lets a host build policy on top without parsing prose.
