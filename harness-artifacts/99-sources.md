# 99. Sources, artifacts and grades

> **✅** read from the named bytes on 2026-10-19 on this Linux host. **📣** a vendor statement or
> a tool's own count, not independently checked. **⚠️** not established here (engine missing,
> budget exceeded, or not run).

## A. Instrument

| Item | Value |
|---|---|
| REA | `rea-agents` 6.7.0 from npm (global install under nvm Node 24.16.0); checkout `morluto/rea` @ `3ea0d9489` (2026-10-19) read for docs (`AGENTS.md`, `docs/mcp-contracts.md`, `docs/tool-design.md`, `docs/electron-fuses.md`, `docs/javascript-artifact-reconstruction.md`, `docs/rust-binaries.md`, `docs/binary-diagnostics.md`) |
| `rea doctor` | `healthy: false` — `hopper`, `ghidra` (`GHIDRA_INSTALL_DIR` unset), `ida-registration`, `jadx`, `kuna-installation` all `missing_analysis_engine`; host `ubuntu 26.04` |
| Other tools | `readelf`/`objcopy`/`strings` (binutils), `7z` (p7zip), `dpkg-deb`, `@electron/asar` via `npx`, Python 3 (`-I`) |
| Bun source | `oven-sh/bun` `src/standalone_graph/StandaloneModuleGraph.zig` @ `bun-v1.3.14` (released 2026-05-13) and `StandaloneModuleGraph.rs` @ `bun-v1.4.3` (2026-10-10); tags `bun-v1.4.0`–`1.4.3` exist, `1.4.4` does not |
| Codex tags | `openai/codex` `rust-v0.159.3` (`01fc69f40`, 2026-09-30 21:46 UTC) and `rust-v0.163.0` (`83086188a`, 2026-10-15 18:57 UTC), fetched into `~/repos/harness-refs/codex` for the ancestry test |

## B. Artifacts

| Artifact | Version | Bytes | SHA-256 | Origin |
|---|---|---|---|---|
| Claude Code CLI ELF | 2.1.303 | 285,809,912 | `375988f457756524…` | `~/.local/share/claude/versions/2.1.303` |
| `claude-desktop_2.42304.2_amd64.deb` (re-fetch 2026-10-20) | 2.42304.2 | 183,213,384 | `38a7d58b58a976c8…` (= row above) | same apt pool; extracted to `~/.cache/agent-ux-gui-src/claude-desktop`, `ion-dist` root sha256 `b8d67132…` (3,620 files) |
| `chatgpt_amd64.deb` (re-fetch 2026-10-20) | 26.1013.40934 | 502,087,434 | `3ca59e7f9a6641b9…` (= row above) | same URL; `app.asar` 578,643,106 B extracted (`webview/assets` 16,354 files, root sha256 `37bd40fc…`) |
| `Antigravity.tar.gz` (Linux x64, standalone agent app) | 2.17.0 | 179,494,137 | `6a9b0ff60f7bd0d1…` | `storage.googleapis.com/antigravity-public/antigravity-hub/2.17.0-5217732355031040/linux-x64/`; `resources/app.asar` 4,621,906 B; web UI zip embedded in `resources/bin/language_server` (180,375,760 B, sha256 `016673a9…`) at offset 150,747,311 (3,768,098 B, 304 entries, `main.js` 9,528,635 B) |
| opencode ELF | 1.17.12 | 167,577,728 | `f52fea2ee6a6a856…` | npm `opencode-linux-x64` |
| Codex `codex` | 0.159.3 | 287,086,056 | `8bf204b36a2f6dd0…` | npm `@openai/codex-linux-x64` |
| Codex `codex-code-mode-host` | 0.159.3 | 74,072,976 | `fe64bd08c7844ca1…` | same |
| Gemini CLI bundle dir | 0.42.0 | 91 MB (102 JS) | dir digest (REA) `9bbc9a51a3999862…` | npm `@google/gemini-cli` |
| `claude-desktop_2.42304.2_amd64.deb` | 2.42304.2 | 183,213,384 | `38a7d58b58a976c8…` | `https://downloads.claude.ai/claude-desktop/apt/stable/pool/main/c/claude-desktop/` (`Packages` index, `last-modified` 2026-10-19 07:32 UTC) |
| `claude-desktop` ELF (inside) | — | 228,580,680 | `22e8df58ef7b2151…` | — |
| `chatgpt_amd64.deb` | 26.1013.40934 | 502,087,434 | `3ca59e7f9a6641b9…` | `https://persistent.oaistatic.com/codex-app-prod/linux/deb/latest/chatgpt_amd64.deb` (`last-modified` 2026-10-16 22:32 UTC) |
| `resources/codex` (inside) | 0.163.0 (`strings` substring ×31; tag `rust-v0.163.0` 2026-10-15) | 296,885,960 | `70ea33b7094a4c20…` | — |
| `ChatGPT.dmg` | 1.2026.183 | 78,575,566 | `49b33cadd2ec659b…` (same as 2026-09-26) | `https://persistent.oaistatic.com/sidekick/public/ChatGPT.dmg` |
| Claude Code CLI ELF | 2.1.304 | 288,730,480 | `ea0f135784631619…` (= `manifest.json` linux-x64) | `~/.local/share/claude/versions/2.1.304`, split 2026-10-19 night (2,710 modules) |
| `manifest.json` / `manifest.json.raw-sig.json` / `manifest.json.sig` / `manifest.zst.json` | 2.1.304 | 2,101 / 833 / 833 / — | sidecar `publicKeySha256` `89a24e2e18d2f8fa…` | `downloads.claude.ai/claude-code-releases/2.1.304/` — signature verified locally with the binary's embedded PEM ([04](04-update-channels.md) §1.2) |
| `claude.ai/install.sh` · `opencode.ai/install` · `releases.openai.com/codex/install.sh` | — | 9,704 / 15,443 / 34,564 | — | read, not run |
| Desktop update API (`releases.claude.com/api/desktop/…`), `RELEASES`, `RELEASES.json`, apt `InRelease`/`Packages`, `key.asc` | 2.42304.2 (stable) · 2.42585.0 (latest) · 2.31226.1 (staggered) | — | apt key fp `31DDDE24…1A7ECACE` "Anthropic Claude Code Release Signing" | GET 2026-10-19 night; `claude.ai` host returns a Cloudflare challenge to curl |
| OpenAI `appcast?installation_id&arch&app_version`, `windows-release.json`, `windows-store-update.json` | 26.1013.40934 / 26.1013.4894.0 | 25,351 (arm64 appcast) | Ed25519 `edSignature` per enclosure | `updates.oaistatic.com`, `persistent.oaistatic.com` |
| `ChatGPT.dmg` `Info.plist` | 1.2026.183 | — | `SUPublicEDKey IktUdD7h…`, Sparkle 2.8.1 | re-downloaded, sha256 unchanged `49b33cad…` |
| Codex R2 `channels/latest`, `releases/0.163.0/release.json` | rust-v0.163.0 | 97,344 | 318 assets with `sha256:` digests, 28 `.sigstore` | `releases.openai.com/codex/` |
| `openai/codex` source | `origin/main` `79a19cbb3` (fetched 2026-10-19 night; became the drift baseline in `docs/99` §E.7 on 2026-10-20) | — | — | `codex-rs/tui/src/{updates,update_action,updates_cache,npm_registry}.rs`, `install-context/src/lib.rs`, `scripts/install/install.sh`, `.github/scripts/publish_r2_release.py` |
| opencode Bun bundle (split) | 1.17.12 | 1,200 modules, 1,066 js | — | `opencode-linux-x64/bin/opencode`, [04](04-update-channels.md) §5 |
| ChatGPT Linux deb (2nd pass) | 26.1013.40934 | 502,087,434 | `3ca59e7f9a6641b9…` (= apt `Packages` SHA256) | `persistent.oaistatic.com/codex-app-prod/linux/deb/latest/chatgpt_amd64.deb`; `DEBIAN/postinst` (apt repo + key), `resources/linux-package-metadata.json`, `app.asar` `bootstrap-Dn-4EbjT.js` 523,922 B, [04](04-update-channels.md) §3 |
| ChatGPT apt index (2nd pass) | `stable` 2026-10-16T21:07:28Z | `InRelease` 2,797 · `Packages` 1,653 | — | `persistent.oaistatic.com/codex-app-prod/linux/deb/dists/stable/…`; one version per arch; signature verified with the deb-embedded key `3BFA…60E4` "Codex Linux Repository" |
| Codex release asset + sigstore (2nd pass) | 0.163.0 | 113,680,454 · 8,509 | `406bbe28fbae17b2…` (= `release.json` digest) | `releases.openai.com/codex/releases/0.163.0/codex-package-x86_64-unknown-linux-musl-bazel.tar.zst[.sigstore]`, [04](04-update-channels.md) §4 |
| opencode / Superset / Paseo updater sources (2nd pass) | `sst/opencode` `v1.17.12` · `superset-sh/superset` `9d870d632` · `getpaseo/paseo` `ab6cdb7c8` | — | — | GitHub contents API (authenticated `gh`), [04](04-update-channels.md) §5·§7 |
| Gemini CLI update sources | `main` 2026-10-19 | 3,677 / 6,701 / 8,474 | — | `raw.githubusercontent.com/google-gemini/gemini-cli/main/packages/cli/src/…` |
| Cursor / Devin update APIs | 3.25.9 / 3.10.67 | — | Devin `sha256hash`; Cursor none | `api2.cursor.sh`, `windsurf-stable.codeium.com` |
| Gemini CLI core sources (`main`, 2026-10-20) | — | `client.ts` 42,391 · `turn.ts` 15,722 · `geminiChat.ts` 71,902 · `loopDetectionService.ts` 26,752 · `nextSpeakerChecker.ts` 5,317 · `scheduler.ts` 31,881 · `nonInteractiveCli.ts` 22,365 | — | `raw.githubusercontent.com/google-gemini/gemini-cli/main/packages/…`, for [05](05-agent-loop.md) §4 |
| Codex loop sources | `origin/main` `79a19cbb3` (= `1a35bc4cc` for these files) | — | — | `core/src/session/{turn,turn_input,input_queue}.rs`, `ext/queue`, `agent/control/spawn.rs`, `protocol/src/{protocol,turn_input}.rs`, [05](05-agent-loop.md) §1 |
| opencode sources (2nd pass) | tag `v1.17.12` | `prompt.ts` 64,859 · `processor.ts` 26,331 · `run-state.ts` 5,506 · `runner.ts` — · `handlers/session.ts` — · `max-steps.ts` — | — | `raw.githubusercontent.com/sst/opencode/v1.17.12/packages/…`, for [05](05-agent-loop.md) §3.2 (steer path, `MAX_STEPS_PROMPT`); the bundle is matched to the tag by its version string only |
| Gemini CLI sparse clone (2nd pass) | `main` `76e4d7c04` (2026-10-19T19:45Z) | `packages/{core,cli}/src` only | — | `AppContainer.tsx`, `hooks/useMessageQueue.ts`, `hooks/useGeminiStream.ts`, `config/injectionService.ts`, `utils/fastAckHelper.ts`, `agents/{local-executor,agent-scheduler,types}.ts`, for [05](05-agent-loop.md) §4.2–4.4 |
| Codex loop-detection grep (2nd pass) | `origin/main` `1a35bc4cc` (2026-10-20T00:17Z) | — | — | `git grep` over `codex-rs/*.rs` minus `tui`/tests: 0 hits for `loop_detect|repeated_tool|same_tool|consecutive_identical|max_turns|max_tool_calls`; `has_same_tool_calls` is cache metadata, [05](05-agent-loop.md) §1.6 |
| Release feeds read | — | — | — | `downloads.claude.ai/releases/win32/x64/RELEASES` → `AnthropicClaude-2.42304.2-full.nupkg` (262,853,497 B, not downloaded); `downloads.claude.ai/releases/darwin/universal/RELEASES.json` → 2.42304.2 pub_date 2026-10-19T00:30:35Z; `code.claude.com/docs/en/desktop-linux.md` |

## C. REA evidence (session scratch, not committed)

| Run | Evidence ID | Status |
|---|---|---|
| `inspect-electron-fuses claude-desktop` | `ev_dfb78584…` | ✅ complete |
| `inspect-electron-fuses ChatGPT` | (recorded in scratch) | ✅ complete |
| `analyze-javascript-application` opencode split dir | `ev_9ad22e97…` | ✅ complete, 2 chunks static-only |
| `analyze-javascript-application` claude split dir | none | ⚠️ `resource_constraint` at 526/2,439 |
| `analyze-javascript-application` claude split dir, `--source-path` ×150 largest chunks | `ev_c2ff746e…` | ✅ complete for the selection; 2,289 files out of scope, several chunks static-only |
| `analyze-javascript-application` Claude Desktop `ion-dist` (directory), `--source-path` ×15 GUI chunks (2026-10-20, `agent-ux/99` source-level GUI pass) | `ev_9169cddc…` | ✅ complete for the selection: 9,137 nodes / 15,903 edges, 3,605 files out of scope (28 limitations) |
| `analyze-javascript-application` ChatGPT `app.asar` extracted, `--source-path` ×7 `webview/assets` chunks (2026-10-20) | `ev_783d2550…` | ✅ complete for the selection: 33,865 nodes / 40,151 edges, 16,347 files out of scope (13 limitations) |
| `analyze-javascript-application` Antigravity 2.17.0 `app.asar` extracted (whole, 2026-10-20) | `ev_2eee329b…` | ✅ complete: 688 JS parsed, 3,168 nodes / 4,455 edges (1,100 limitations, Electron relationships inert-syntax only) |
| `analyze-javascript-application` Antigravity 2.17.0 web UI zip, `--source-path main.js` | `ev_0c260c4d…` (1 GiB heap) and `ev_00b01802…` (`--max-heap-mb 6144`, `--max-semantic-nodes-per-file 60000`, 900 s) — **both** `resource_constraint`: the worker heap exhausted on the single 9,528,635-byte bundle, **0 JS parsed** each time. The zero is a non-delivery, not a result; inventory identity (root sha256 `52e60614…`, 9 files) is the only sealed fact. The reading in `agent-ux/05` was done by window search over the bytes | ⚠️ REA graph absent |
| `analyze-javascript-application` gemini bundle | `ev_b5494fd5…` (partial, first run) | ⚠️ timeout 300 s at 14/102; 1,800 s re-run stopped by hand at 16/102 |
| `analyze-javascript-application` gemini bundle, `--source-path` ×69 (without the three 14.7 MB chunks) | `ev_fb798187…` | ✅ complete for the selection; 33 files out of scope, 2 chunks static-only |
| `analyze-javascript-application` Claude Desktop `app.asar` (extracted) | `ev_49ecce1c…` | ✅ complete, 8 sources static-only |
| `analyze-javascript-application` ChatGPT `.vite/build` (`--source-path` ×37) | `ev_0881fae3…` | ✅ terminal, large modules static-only |
| `inspect-rust-binary codex` | — | ⚠️ refused: >268,435,456 B |
| `inspect-rust-binary codex-code-mode-host` | (recorded) | ✅ no `.dep-v0`; `rustc_commit` inferred |
| `decode-interface-builder ChatGPT.app` | `ev_43cfe8e8…` | ✅ 3 Sparkle nibs only |
| `inspect-macho`, `inspect-asset-catalog`, `demangle-swift`, `inspect-native-dispatch-metadata` | — | ⚠️ need macOS / a native provider |

## D. Grades by claim

| Claim | Grade | Note |
|---|---|---|
| Bun `.bun` layout (header, 52-byte records, trailer, flags) | ✅ | parse self-consistent on 3,886 records, then matched to `StandaloneModuleGraph.zig` @ `bun-v1.3.14` and `.rs` @ `bun-v1.4.3` (`oven-sh/bun`, raw.githubusercontent.com). `Bun v1.4.4` has no public tag ⚠️ |
| Claude Code ships JSC bytecode next to source | ✅ | `// @bun @bytecode` marker + 2,431 non-empty bytecode pointers |
| Which of text/bytecode the runtime loads | ⚠️ | not run |
| Codex 0.159.3 carries `responses_lite`, `thread/goal/set`, `approval_policy` literals | ✅ | `strings` counts |
| `model_catalog_in_context` present in 0.159.3 | ✅ absent | no literal **and** `2e5fea64ee` is not an ancestor of `rust-v0.159.3`; present in `rust-v0.163.0` and in the ChatGPT-bundled 0.163.0 (8 literals) |
| Fuse states, both desktops | ✅ | REA; Linux enforcement of asar integrity ⚠️ per REA |
| Six Claude renderer windows, 13 main entries, four new | ✅ | asar listing |
| Claude Desktop window options and titles | ✅ strings | layout ⚠️ |
| `Claude Design`, worktrees, subagents, Dispatch strings | ✅ | `ion-dist/i18n/en-US.json` values |
| ChatGPT permission dropdown labels, `Approve for me` nudge | ✅ | `defaultMessage` strings |
| ChatGPT side-panel tab set, settings pages, Chronicle, pets, keypad | ✅ names/strings | layout ⚠️ |
| 5 `BrowserWindow` + 1 `WebContentsView` in ChatGPT main | ✅ regex count | REA retained static facts only for that file |
| ChatGPT bundled `codex` version | ✅ 0.163.0 | substring probe; the whole-line probe had missed it |
| Legacy native app UI type inventory | ✅ `strings` | which types render on macOS ⚠️ |
| Cowork VM toolchain on Linux | ✅ files + strings | runtime ⚠️ |
| Tool-use mechanisms in [03](03-tool-use-patterns.md) | per-row | source line references for Codex/Strands/REA; module names for Claude Code/opencode/Gemini |
| Claude Code manifest signature scheme ([04](04-update-channels.md) §1.2) | ✅ **reproduced**: RSASSA-PKCS1-v1_5-SHA512 over `"claude-code-manifest-v1\0" ‖ manifest bytes`, key sha256 `89a24e2e…`, sidecars from 2.1.207 | key custody and the relation to the PGP key ⚠️ |
| Desktop channel UUIDs → versions, server-side `maxVersion` ([04](04-update-channels.md) §2.1) | ✅ GET on `releases.claude.com` | `claude.ai` host ⚠️ (bot challenge) |
| Desktop embedded-CLI auto-update: flag `762798616`, floor/high-water mark, hashed spread, same signing key ([04](04-update-channels.md) §2.4) | ✅ strings | live flag values ⚠️ |
| OpenAI appcast shape, required params, 10 items × 4–5 deltas ([04](04-update-channels.md) §3) | ✅ GET | Electron consumer ✅ (2nd pass: `sparkle.node` addon on mac with `beta`/`plan_type` query params, `windows-updater.node` + MSIX sha256/identity checks, Linux reads `linux-package-metadata.json` every 15 min, no network); Linux apt repo ✅ (InRelease signature verified locally); Ed25519 key identity ⚠️ (key lives in the mac bundle's `Info.plist`) |
| Codex: 20 h cache, per-method sources, no self-replacement; R2 layout ([04](04-update-channels.md) §4) | ✅ source + GET; sigstore bundle **verified locally** (2nd pass: ECDSA over the asset, Fulcio chain to `CN=sigstore`, Rekor SET, signer SAN `openai/codex/.github/workflows/rust-release.yml@refs/tags/rust-v0.163.0`) | sigstore not consumed by CLI/installer (추정) |
| opencode: patch auto-upgrade by default, pipe-to-shell with no checksum ([04](04-update-channels.md) §5) | ✅ bundle + script; 37/37 assets enumerated, desktop = electron-builder with `allowDowngrade: true`, Windows `verifyUpdateCodeSignature: false`, Tauri-format `latest.json` minisign-signed in CI (2nd pass, source `v1.17.12`) | asset hash files beyond 6 names ⚠️ |
| Gemini CLI: npm `latest-version`, channel-stability guard, sandbox block ([04](04-update-channels.md) §6) | ✅ source | — |
| Codex turn loop: `needs_follow_up`, no step cap, steer vs queue, Stop-hook continuation, mid/post-turn compaction ([05](05-agent-loop.md) §1) | ✅ source | runtime ⚠️. **No loop detection at all** ✅ (§1.6, grep 0 on `1a35bc4cc`): the only in-engine bound is the context window, on the code comment's assumption that compaction converges (`turn.rs:681`) |
| Claude Code query loop: 26 terminal reasons, `maxTurns`, stop-hook cap 8, async message queue with interrupt receipt ([05](05-agent-loop.md) §2) | ✅ bundle strings + `sdk.d.ts` | thresholds ✅ (2nd pass, `chunk-rncrmfyt.js`): compact at effective window − 13,000 (effective = window − min(maxOutput, 20,000)), blocked at window − min(maxOutput, 20,000) − 3,000, warn at threshold − 20,000; 1M → 967,000 matches the docs; rapid-refill breaker = 3 refills each within 3 turns, failure breaker 3. Remote flag values `tengu_amber_*` ⚠️ |
| opencode step loop: `compact\|stop\|continue`, doom-loop window 3, per-agent `steps`, busy guard ([05](05-agent-loop.md) §3) | ✅ bundle + source `v1.17.12` | server-side steer ✅ (2nd pass): a prompt during a run stores the message and **joins** the running fiber (`Runner.ensureRunning` → `awaitDone`); the loop re-reads messages per step so it becomes the next step's `lastUser`. **Self-refutation**: the 1st pass said a busy session *refuses* a second prompt — `assertNotBusy` guards revert/delete/shell, not prompt. `MAX_STEPS_PROMPT` text read; tools are still sent on the capped step |
| Gemini loop: `MAX_TURNS 100`, next-speaker LLM check, three-layer loop detection, pre-send compression ([05](05-agent-loop.md) §4) | ✅ source | interactive TUI ✅ (2nd pass, `76e4d7c04`): client-side `useMessageQueue` (joined with `\n\n`, one submit at idle) + experimental `modelSteering` (default false) hints via `InjectionService`, consumed in front of the next tool responses with `buildUserSteeringHintPrompt`; `_recoverFromLoop` = one system feedback line, recursion − 1; local agent executor `maxTurns 30` / `maxTimeMinutes 10` / `complete_task` protocol / 60 s grace turn ✅. Remote/A2A executors ⚠️ |
