# 99. Sources and grades

> **✅** read in the named artifact on 2026-10-19. **📣** the documentation's statement about
> behaviour, not observed. **⚠️** not determinable statically. **추정** inference, marked inline.

## A. Primary sources ✅

| Source | What was taken | Grade |
|---|---|---|
| `@anthropic-ai/claude-agent-sdk` **0.3.303** — npm tarball, published 2026-10-18T22:28Z; files `sdk.d.ts` (10,128 lines), `sdk-tools.d.ts` (4,222), `core.d.ts`, `bridge.d.ts`, `browser-sdk.d.ts`, `extractFromBunfs.d.ts`, `sdk.mjs`, `bridge.mjs`, `manifest.json` (CLI 2.1.303, commit `07df2aed`, buildDate 2026-10-18T20:40:12Z), `README.md`, `package.json` (8 platform `optionalDependencies`) | every type, option, enum, count and doc comment cited as `sdk.d.ts:N` | ✅ the generated contract |
| Claude Code CLI **2.1.303** binary (`~/.local/share/claude/versions/2.1.303`, SHA-256 `375988f4…`), split into 2,435 JS modules with `scripts/bun_split.py` | control subtypes, zod schemas, strings (classifier call, fail-closed messages, managed paths, sandbox runtime names, transcript record fields, `context_hint`, memory recall), cited by `chunk-*.js` | ✅ strings; control flow ⚠️ (minified, bytecode alongside) |
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
- `set_mcp_permission_mode_override` has a `Query` method but is absent from the request union; `get_binary_version`, `set_color`, `seed_read_state` are typed but were not found as bundle literals.
- The SDK release is the engine's distribution channel (`manifest.json` pins the CLI); a later SDK may ship a different CLI than the one installed locally. Next baseline: CLI 2.1.303 / SDK 0.3.303 / docs 2026-10-19.
