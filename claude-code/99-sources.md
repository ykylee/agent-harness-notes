# 99. Sources and grades

> **✅** read in the named artifact on 2026-10-19. **📣** the documentation's statement about
> behaviour, not observed. **⚠️** not determinable statically. **추정** inference, marked inline.

## A. Primary sources ✅

| Source | What was taken | Grade |
|---|---|---|
| `@anthropic-ai/claude-agent-sdk` **0.3.303** — npm tarball, published 2026-10-18T22:28Z; files `sdk.d.ts` (10,128 lines), `sdk-tools.d.ts` (4,222), `core.d.ts`, `bridge.d.ts`, `browser-sdk.d.ts`, `extractFromBunfs.d.ts`, `sdk.mjs`, `bridge.mjs`, `manifest.json` (CLI 2.1.303, commit `07df2aed`, buildDate 2026-10-18T20:40:12Z), `README.md`, `package.json` (8 platform `optionalDependencies`) | every type, option, enum, count and doc comment cited as `sdk.d.ts:N` | ✅ the generated contract |
| Claude Code CLI **2.1.303** binary (`~/.local/share/claude/versions/2.1.303`, SHA-256 `375988f4…`), split into 2,435 JS modules with `scripts/bun_split.py` | control subtypes, zod schemas, strings (classifier call, fail-closed messages, managed paths, sandbox runtime names, transcript record fields, `context_hint`, memory recall), cited by `chunk-*.js` | ✅ strings; control flow ⚠️ (minified, bytecode alongside) |
| `@anthropic-ai/claude-agent-sdk` **0.3.304** — npm tarball (`manifest.json`: CLI **2.1.304**, commit `17ab7040`, buildDate 2026-10-19T18:30:38Z; `sdkCompat.testedWrapperVersions` window slid 0.3.270→0.3.303, still 30 entries), `sdk.d.ts` 10,179 lines (+51), `sdk-tools.d.ts` unchanged (4,222), `browser-sdk.d.ts` +17 | the §E drift pass: every `+` line of the type diff classified | ✅ |
| Claude Code CLI **2.1.304** binary (`~/.local/share/claude/versions/2.1.304`, 288,730,480 B, SHA-256 `ea0f1357…` = `manifest.json` linux-x64), split with `scripts/bun_split.py`: 2,710 modules, 2,463 `.js` (2,459 with bytecode), flags `0x1bff`, Bun v1.4.4 | §E string counts side by side with 2.1.303 | ✅ strings |
| `https://code.claude.com/docs/en/changelog.md` (1,126,573 B) and re-reads of `headless`, `cli-reference`, `permissions`, `permission-modes`, `settings`, `sessions`, `context-window`, `remote-control`, `agent-sdk/{permissions,hooks,sessions}` on 2026-10-19 (late) | the 2.1.304 and 2.1.302 entries; version-gated sentences ≥ 2.1.300 | ✅ the vendor's statement |
| `https://code.claude.com/docs/en/*.md` read 2026-10-19: `headless`, `cli-reference`, `permissions`, `permission-modes`, `hooks`, `settings`, `settings-reference`, `managed-settings`, `security`, `agent-sdk/permissions`, `sessions`, `checkpointing`, `context-window`, `prompt-caching`, `memory`, `model-config`, `claude-directory`, `remote-control`, `channels`, `cross-session-messaging`, `agents`, `agent-teams`, `workflows`, `claude-code-on-the-web`, `desktop`, `deep-links` | pipeline order, exit-code semantics, retention, compaction thresholds, cache rules, client descriptions | ✅ as the vendor's statement; behaviour 📣 |

## B. Counts (reproducible by grep)

| Item | Count | Where |
|---|---|---|
| `SDKMessage` members / top-level types / `system` subtypes / `result` subtypes | 39 / 11 / 28 / 5 | `sdk.d.ts:5442` |
| `StdoutMessage` top-level types | 16 | `:9726` |
| `control_request` subtypes (typed) | 40 (36 client→engine, 5 engine→client, `mcp_message` both) | `:5097` |
| engine→client requests incl. `sdk.mjs` runtime | 13 | [01 §4](01-wire-protocol.md) |
| `query()` options / `Query` methods | 69 / 30 | `:1552-2490`, `:2892` |
| tool input schemas / `BUILTIN_TOOL_NAMES` | 44 / 54 | `sdk-tools.d.ts`, `sdk.d.ts:216` |
| `HOOK_EVENTS` / `PermissionMode` | 33 / 6 | `:975`, `:2529` |
| `subtype:"…"` literals in the bundle | ~160 (~185 with `===` comparisons, 추정) | `chunk-*.js` |
| bundle `.js` modules / byte-identical files across 2.1.303→2.1.304 | 2,435 → 2,463 / 224 of 2,687 (chunk names are content hashes, so names do not match) | `scripts/bun_split.py` index |

## C. Not verified here ⚠️

| Item | Why |
|---|---|
| Any runtime behaviour: prompt parking, hook timeouts, classifier verdicts, idle compaction firing, Remote Control resume window | nothing was run |
| The server side of the bridge (CCR), `context_hint` responses, `storageV5`, hosted-runner fields (`resume_reason`, `warm_spare_claimed`) | server code not available; bundle strings only |
| Composition of two `PreToolUse` hooks returning different `updatedInput` | neither docs nor types state it |
| Windows sandbox (`srt-win` strings) | docs say "doesn't run on native Windows"; the strings suggest a flag — not exercised |
| Which `sessionKind` values exempt a transcript from the sweep | not enumerated in docs or types |
| Desktop metering from `modelUsage` / `get_usage` | inferred from policy keys in the desktop shell |

## D. Drift to watch

- `sdk.d.ts:1747` `betas` comment still says "`context-1m-2025-08-07` … (Sonnet 4/4.5 only)" while the docs describe 1M as the default — the types lag the docs here.
- `set_mcp_permission_mode_override` has a `Query` method but is absent from the typed request union — the bundle does carry its zod schema (`A("set_mcp_permission_mode_override")`, `serverName`, `mode`, an `@internal askForTools`), so this is the types lagging the engine, not a phantom method.
- ~~`get_binary_version`, `set_color`, `seed_read_state` are typed but were not found as bundle literals~~ — **refuted 2026-10-19 (late)**: all three are in the bundle as zod literals `A("get_binary_version")`, `A("set_color")`, `A("seed_read_state")` (`chunk-4qs43hr1.js`, with `.describe()` strings identical to the `sdk.d.ts` doc comments — the types are generated from these schemas) and as keys of a per-subtype boolean table `ZC={claim_session:!0,…,get_binary_version:!0,…,seed_read_state:!1,…,set_color:!1,…}` (`chunk-8w3jrzn0.js`; what the boolean gates is 추정 unread). The first search looked only for `subtype:"<name>"`; the engine spells its own subtypes `A("<name>")`.
- **Corrected 2026-10-19 (late).** The six `can_use_tool` fields the Claude Desktop 2.42304.2 renderer reads but `sdk.d.ts` 0.3.303/0.3.304 do not declare ([`agent-ux/02`](../agent-ux/02-claude-desktop.md) §3.1) are **not** a shell running ahead of the engine: five of them are emitted by the engine's own request builder in **both** 2.1.303 and 2.1.304 (`chunk-88j6ans0.js`: `decision_reason_code`, `decision_reason_hook_event/_source/_plugin_id`, `computer_folder`; counts 13/3/5/3/26 in each version), together with five more the types also omit — `decision_reason_rule_source`, `server_policy_ask_only`, `tool_kind: "browser"`, `server_prompt`, `provenance_prompt_line` (and a `plugin` string). The remote-forwarding filter `[wireFrameShape]` (`chunk-da4t0xdq.js`) whitelists exactly these names. Only `via_host_cli_launcher` is absent from both binaries (0 hits): the desktop host adds it. So the gap is **types lagging the engine**, the same direction as the two bullets above — watch `sdk.d.ts` for `decision_reason_code` and the hook triple.
- The SDK release is the engine's distribution channel (`manifest.json` pins the CLI); a later SDK may ship a different CLI than the one installed locally. Next baseline: **CLI 2.1.304 / SDK 0.3.304 / docs 2026-10-19 (late)** — see §E.

## E. Drift 2026-10-19 (late) — SDK 0.3.303 → 0.3.304, CLI 2.1.303 → 2.1.304

Both appeared within a day of the baseline. Method: `diff` of every file in the two npm tarballs;
both binaries split with `scripts/bun_split.py` and searched for the same string list side by side;
the changelog and ten docs pages re-read. Nothing executed. **Refutations: 0 from the vendor, 2 of this
folder's own sentences** (§D: the three "missing" subtypes, and the "shell ahead of the engine" reading).

| Area | 0.3.303 / 2.1.303 | 0.3.304 / 2.1.304 | Grade |
|---|---|---|---|
| Typed contract (`sdk.d.ts`) | 10,128 lines | 10,179 — **no new control subtype, message type, option or tool schema** (`sdk-tools.d.ts`, `agentSdkTypes.d.ts`, `core.d.ts`, `bridge.d.ts` byte-identical). The +51 lines are: `SDKControlGetContextUsageResponse` rows gain a stable `id` enum (13 values: `system_prompt system_tools mcp_tools mcp_instructions mcp_tools_deferred system_tools_deferred custom_agents memory_files skills messages autocompact_buffer compact_buffer free_space`; "Absent from a CLI that predates it… treat an unknown value as absent"), a per-server `mcpInstructions[]`, and `pluginId` / `path` on agents and `pluginName` / `pluginId` / `path` on skills ("Present only where the CLI answers on its own stdio and no server stores or forwards the reply"); `startup()` and `prewarm()` take `initializeTimeoutMs` (default 60,000 ms; unset, time a `SessionStart`/`Setup` hook spends is not counted, up to 10 min); the `request_user_dialog` comment adds dialogs **with no deadline**, withdrawn by `control_cancel_request`; the `keep_alive` comment adds the `startup_mark` field | ✅ |
| Browser SDK | — | `suspendSseStream(query)` / `resumeSseStream(query)`: close the SSE stream without ending the query; durable events replay on resume, ephemeral frames are lost, permission prompts wait unanswered meanwhile (`browser-sdk.d.ts`) | ✅ types; behaviour 📣 |
| Start-up marks | absent (0 hits in SDK and CLI) | SDK sets `CLAUDE_CODE_SDK_READS_STARTUP_MARKS=1`; the CLI writes `{"type":"keep_alive","startup_mark":"<name>"}` lines before the `initialize` response, from a fixed list of 35 checkpoints (`…preAction_after_init, action_before_permission_context, before_connectMcp, after_sandbox_init, …, stdin_listen_started`, `chunk-sx3g9k86.js`); the host keeps `startupMark {mark, atMs}` | ✅ strings |
| Approval wire | — | **unchanged**: `can_use_tool` 68/68, zod `A("can_use_tool")` 3/3, every request field count equal (see §D), `'blocking because onFailure is "block"'` 2/2, `no approval surface in this session` 1/1, `bashCommandClamp fail-closed` 1/1, `returned an invalid permission result` 3/3, `supportedDialogKinds` 17/17, `allowManagedHooksOnly` 36/36, `disableBypassPermissionsMode` 14/14, `disableAutoMode` 31/31 | ✅ |
| Mod `tool.check` | `decider` only `host` | `decider==="person"` 0 → 2, `hooksMayRefuse` 0 → 2: an ask answered `{decision: "ask", decider: "person"}` is forced to the dialog or the host callback with `personOnly, hooksMayRefuse, suppressAlwaysAllowRule` set (`chunk-rncrmfyt.js`, `chunk-8w2bnd0t.js`). Changelog 2.1.304: "only the permission dialog or a host's callback can approve the ask, and it is refused with the mod's reason where nobody can be asked" | ✅ string + 📣 |
| `server_policy_ask_only` | 4 | 7 — the field (org ask ceiling for MCP tools, `decision_reason_code: "org_ask_ceiling"`) gains call sites; still untyped | ✅ |
| Context rows | `mcp_instructions` 13 | 16; `autocompact_buffer` / `compact_buffer` / `free_space` / `mcpInstructions` 0 → 2 / 4 / 2 / 13 — the typed rows above have their producer in `chunk-rncrmfyt.js` | ✅ |
| Bundled docs | 58 SKILL/README/SCHEMA documents | 57: `whiteboard` skill out, `Secure a Managed Agents deployment` in (`/claude-api managed-agents-secure`, 0 → 14 hits) | ✅ |
| Changelog 2.1.304 claims not checked against strings | — | `e.isReadOnly` on `tool.check` events (identifier count 113 → 119, not attributable), mods' `settings.read` hooks rewriting the merged settings as a ceiling (`settings.read` 24 → 36), the `rm -r` safety prompt for mounted drives, the VS Code 60,000 ms start-up fix (= the `initializeTimeoutMs` note above) | 📣 |
| Docs drift since the morning read | — | `permission-modes.md` / `headless.md` / `agent-sdk/permissions.md`: since **v2.1.302** `claude -p` and SDK runs with no mode set start in `default` (Manual) — "before v2.1.302, these runs could start in auto mode if they didn't fetch feature flags"; `CLAUDE_CODE_AUTO_MODE_MODEL` (2.1.302); `remote-control.md`: `--sandbox` / `--no-sandbox` removed in v2.1.300; `permissions.md` mod precedence now reads "deny rules hold over the mod **by default, and your organization can change that**" on managed/Team/Enterprise | ✅ as statements |

What did **not** move: the six-stage pipeline, the mode set, `PermissionResult`, `PermissionUpdate`,
hook precedence, the managed-settings paths, the retention and compaction keys. Changelog 2.1.303 is
"Bug fixes and reliability improvements" only, so the 303→304 string deltas above are the whole
visible movement of two days.
