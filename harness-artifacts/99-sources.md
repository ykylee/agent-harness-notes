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

## B. Artifacts

| Artifact | Version | Bytes | SHA-256 | Origin |
|---|---|---|---|---|
| Claude Code CLI ELF | 2.1.303 | 285,809,912 | `375988f457756524…` | `~/.local/share/claude/versions/2.1.303` |
| opencode ELF | 1.17.12 | 167,577,728 | `f52fea2ee6a6a856…` | npm `opencode-linux-x64` |
| Codex `codex` | 0.159.3 | 287,086,056 | `8bf204b36a2f6dd0…` | npm `@openai/codex-linux-x64` |
| Codex `codex-code-mode-host` | 0.159.3 | 74,072,976 | `fe64bd08c7844ca1…` | same |
| Gemini CLI bundle dir | 0.42.0 | 91 MB (102 JS) | dir digest (REA) `9bbc9a51a3999862…` | npm `@google/gemini-cli` |
| `claude-desktop_2.42304.2_amd64.deb` | 2.42304.2 | 183,213,384 | `38a7d58b58a976c8…` | `https://downloads.claude.ai/claude-desktop/apt/stable/pool/main/c/claude-desktop/` (`Packages` index, `last-modified` 2026-10-19 07:32 UTC) |
| `claude-desktop` ELF (inside) | — | 228,580,680 | `22e8df58ef7b2151…` | — |
| `chatgpt_amd64.deb` | 26.1013.40934 | 502,087,434 | `3ca59e7f9a6641b9…` | `https://persistent.oaistatic.com/codex-app-prod/linux/deb/latest/chatgpt_amd64.deb` (`last-modified` 2026-10-16 22:32 UTC) |
| `resources/codex` (inside) | ⚠️ unread | 296,885,960 | `70ea33b7094a4c20…` | — |
| `ChatGPT.dmg` | 1.2026.183 | 78,575,566 | `49b33cadd2ec659b…` (same as 2026-09-26) | `https://persistent.oaistatic.com/sidekick/public/ChatGPT.dmg` |
| Release feeds read | — | — | — | `downloads.claude.ai/releases/win32/x64/RELEASES` → `AnthropicClaude-2.42304.2-full.nupkg` (262,853,497 B, not downloaded); `downloads.claude.ai/releases/darwin/universal/RELEASES.json` → 2.42304.2 pub_date 2026-10-19T00:30:35Z; `code.claude.com/docs/en/desktop-linux.md` |

## C. REA evidence (session scratch, not committed)

| Run | Evidence ID | Status |
|---|---|---|
| `inspect-electron-fuses claude-desktop` | `ev_dfb78584…` | ✅ complete |
| `inspect-electron-fuses ChatGPT` | (recorded in scratch) | ✅ complete |
| `analyze-javascript-application` opencode split dir | `ev_9ad22e97…` | ✅ complete, 2 chunks static-only |
| `analyze-javascript-application` claude split dir | none | ⚠️ `resource_constraint` at 526/2,439 |
| `analyze-javascript-application` gemini bundle | `ev_b5494fd5…` (partial, first run) | ⚠️ timeout 300 s at 14/102; 1,800 s re-run stopped by hand at 16/102 |
| `analyze-javascript-application` Claude Desktop `app.asar` (extracted) | `ev_49ecce1c…` | ✅ complete, 8 sources static-only |
| `analyze-javascript-application` ChatGPT `.vite/build` (`--source-path` ×37) | `ev_0881fae3…` | ✅ terminal, large modules static-only |
| `inspect-rust-binary codex` | — | ⚠️ refused: >268,435,456 B |
| `inspect-rust-binary codex-code-mode-host` | (recorded) | ✅ no `.dep-v0`; `rustc_commit` inferred |
| `decode-interface-builder ChatGPT.app` | `ev_43cfe8e8…` | ✅ 3 Sparkle nibs only |
| `inspect-macho`, `inspect-asset-catalog`, `demangle-swift`, `inspect-native-dispatch-metadata` | — | ⚠️ need macOS / a native provider |

## D. Grades by claim

| Claim | Grade | Note |
|---|---|---|
| Bun `.bun` layout (header, 52-byte records, trailer) | ✅ parse, 추정 field names | self-consistent on 3,886 records across two binaries; not checked against Bun source |
| Claude Code ships JSC bytecode next to source | ✅ | `// @bun @bytecode` marker + 2,431 non-empty bytecode pointers |
| Which of text/bytecode the runtime loads | ⚠️ | not run |
| Codex 0.159.3 carries `responses_lite`, `thread/goal/set`, `approval_policy` literals | ✅ | `strings` counts |
| `model_catalog_in_context` present in 0.159.3 | ⚠️ | no literal; absence is not evidence |
| Fuse states, both desktops | ✅ | REA; Linux enforcement of asar integrity ⚠️ per REA |
| Six Claude renderer windows, 13 main entries, four new | ✅ | asar listing |
| Claude Desktop window options and titles | ✅ strings | layout ⚠️ |
| `Claude Design`, worktrees, subagents, Dispatch strings | ✅ | `ion-dist/i18n/en-US.json` values |
| ChatGPT permission dropdown labels, `Approve for me` nudge | ✅ | `defaultMessage` strings |
| ChatGPT side-panel tab set, settings pages, Chronicle, pets, keypad | ✅ names/strings | layout ⚠️ |
| 5 `BrowserWindow` + 1 `WebContentsView` in ChatGPT main | ✅ regex count | REA retained static facts only for that file |
| ChatGPT bundled `codex` version | ⚠️ | not matched |
| Legacy native app UI type inventory | ✅ `strings` | which types render on macOS ⚠️ |
| Cowork VM toolchain on Linux | ✅ files + strings | runtime ⚠️ |
| Tool-use mechanisms in [03](03-tool-use-patterns.md) | per-row | source line references for Codex/Strands/REA; module names for Claude Code/opencode/Gemini |
