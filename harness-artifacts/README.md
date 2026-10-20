# Harness artifacts — what the shipped binaries say, read with REA

> **What this is.** A reading of the **shipped artifacts** of six agent harnesses as installed on
> one Linux host on 2026-10-19, using [REA](https://github.com/morluto/rea) 6.7.0 ("Reverse
> Engineer Anything", MIT, checkout `3ea0d9489`) as the instrument plus `readelf`/`strings`/`7z`
> where REA needed an engine this host does not have. Nothing was executed; every artifact was
> read as inert bytes.
>
> **Why.** This repository's purpose is the *actual contract* of a harness, read from "generated
> schemas, source, or a binary" ([`PURPOSE.md`](../ai-workflow/memory/active/PURPOSE.md) G1).
> Until now the binary leg was a one-off (the Dia DMG in
> [`browser-agents/12`](../browser-agents/12-dia-binary.md)). This note makes it a method: which
> packaging each vendor ships, what a static reader can establish from it, and where source
> reading and the shipped bytes disagree. It also records a **drift pass** on the two desktop
> clients studied in [`agent-ux/02`](../agent-ux/02-claude-desktop.md) and
> [`agent-ux/03`](../agent-ux/03-openai-codex-chatgpt.md), three weeks after that study.
>
> **Not a product review, and not a measurement of behaviour.** Static facts only. Where a
> number is REA's own count it is labelled as such; REA's results carry explicit limitations and
> they are quoted, not dropped.

## ⚠️ Read status

- **No binary was run.** Bun bundles were split by parsing the `.bun` section; Electron `app.asar`
  files were listed and extracted with `@electron/asar`; the DMG and debs were unpacked with `7z`
  and `dpkg-deb -x`.
- **Engine matrix on this host** (`rea doctor`, 2026-10-19): Node 24.16.0, Ubuntu 26.04;
  **no Hopper, Ghidra, IDA, JADX, Kuna**, no pwntools. Consequences: no native decompilation,
  `inspect-binary-layout` unavailable, `inspect-macho` / `inspect-asset-catalog` /
  `demangle-swift` / `inspect-native-dispatch-metadata` refused ("Native macOS utilities require
  macOS" / provider unavailable). What *did* work: `inspect-electron-fuses`,
  `analyze-javascript-application`, `inspect-rust-binary` (under 256 MiB), `decode-interface-builder`.
- **REA's JavaScript analyser has budgets.** Three of six graphs were partial on the first pass: the Claude Code CLI
  bundle (2,439 sources) exhausted the parent result capacity at source 526, and a `--source-path`
  run on its 150 largest chunks completed in the evening; the Gemini CLI bundle
  (three 14.7 MB chunks) hit the 300 s per-source default, a 1,800 s re-run was stopped by hand
  after an hour at 16/102, and a `--source-path` run on the other 69 sources completed; the ChatGPT shell retained only static
  facts for its largest modules. Each partial result is marked ⚠️ where it is used.
- The user-facing REA Evidence JSON (several hundred MB) lives in the session scratch directory
  and is **not committed**. Evidence IDs and SHA-256 digests are recorded in
  [`99-sources.md`](99-sources.md) so a re-run can be compared.

## Documents

| # | Document | Subject |
|---|---|---|
| 01 | [Single-file executables](01-single-file-executables.md) | Claude Code CLI 2.1.303 and opencode 1.17.12 as **Bun** executables (module table, bytecode, embedded skills); Codex 0.159.3 as a 287 MB **Rust static-pie** (what `strings` confirms of the source-read contract, and what it cannot); Gemini CLI 0.42.0 as a plain **JS bundle** |
| 02 | [Desktop shells](02-desktop-shells.md) | Claude Desktop **2.42304.2** (Linux deb, published the morning of the read) and ChatGPT/Codex **26.1013.40934** (Linux deb): Electron fuses, windows, preloads, context bridges, IPC, utility processes, and the **UI composition** recovered from chunk names and message catalogues; drift from 2.9939.2 / 26.924.22138; the unchanged legacy native ChatGPT 1.2026.183 |
| 03 | [Tool-use patterns](03-tool-use-patterns.md) | How each reference defines, invokes and post-processes tools, read across Claude Code, Codex, Gemini CLI, opencode, Strands and REA itself — the mechanisms that decide tokens per tool call |
| 04 | [Update channels](04-update-channels.md) | How each reference updates **itself** — version pointer, manifest, artifact; who signs what; channels and staggered rollout; install/replace state machines; policy ceilings. Claude Code's manifest signature verified locally against the key embedded in the binary; Desktop Squirrel feed read across three channels; OpenAI Sparkle appcast, Codex R2 host, opencode's pipe-to-shell upgrade, Gemini's npm path, Cursor/Devin update APIs (2026-10-19/20, Korean) |
| 99 | [Sources](99-sources.md) | Artifacts (URL, size, SHA-256, last-modified), REA evidence IDs, grades |

## Artifacts read

| Harness | Version | Packaging | Size | Where it came from |
|---|---|---|---|---|
| Claude Code CLI | 2.1.303 | Bun 1.4.4 single-file ELF, not stripped, **bytecode** modules | 285,809,912 B | `~/.local/share/claude/versions/2.1.303` (native installer) |
| Codex CLI | 0.159.3 | npm wrapper → `@openai/codex-linux-x64` vendor dir: `codex` static-pie musl, stripped; `codex-code-mode-host`; `rg`; voice host | 287,086,056 B (codex) | npm global |
| opencode | 1.17.12 | Bun 1.3.14 single-file ELF, not stripped, no bytecode | 167,577,728 B | npm global (`opencode-linux-x64`) |
| Gemini CLI | 0.42.0 | plain ESM bundle, 102 chunks | 91 MB | npm global (`@google/gemini-cli`) |
| Claude Desktop | 2.42304.2 | Electron (Forge 8 alpha), Linux deb from Anthropic's apt pool | 183,213,384 B | `downloads.claude.ai/claude-desktop/apt/stable` |
| ChatGPT (Codex superapp) | 26.1013.40934 | Electron 42.3.0 on OpenAI's **OWL** runtime, Linux deb | 502,087,434 B | `persistent.oaistatic.com/codex-app-prod/linux/deb/latest/chatgpt_amd64.deb` |
| ChatGPT legacy native | 1.2026.183 | SwiftUI/AppKit, macOS DMG | 78,575,566 B | `persistent.oaistatic.com/sidekick/public/ChatGPT.dmg` — byte-identical to the 2026-09-26 read |

## Three things this pass established

1. **Two of the four CLIs are Bun executables, and only Claude Code ships bytecode.** The format
   is the same (a `.bun` ELF section holding a module table), but Claude Code 2.1.303 compiles
   2,431 of 2,433 modules to JSC bytecode next to the source, bundles 79 Markdown files (skills,
   READMEs) and 141 zstd-compressed assets, while opencode ships source only plus 134 UI assets.
   Neither vendor documents the layout; [01 §1](01-single-file-executables.md) records the parse
   that recovered it and its confirmation against Bun's own `StandaloneModuleGraph` source (1.3.14 Zig,
   1.4.3 Rust), including the flag bits that say Claude Code is built for bytecode-first startup.
2. **The desktop clients moved in three weeks, in the same direction.** Both shells are the
   same Electron skeleton as before, with the same six (Claude) and two (ChatGPT) renderer HTML
   entries. What changed is *around* the agent: Claude Desktop added four main-process entries
   (`designWindow`, `claudePagePreview`, `coworkArtifact`, `computerUseTeach`) and ships a Linux
   Cowork VM toolchain (QEMU/KVM, `virtiofsd`, a 27 MB `smol-bin.x64.img`); ChatGPT's permission
   dropdown (`Ask for approval` / `Approve for me` / `Full access` / `Custom (config.toml)` /
   `Managed`, labels already recorded in September) now shows its explanatory copy and an
   `Approve for me` nudge that says it "may use more credits", a **Chronicle** ("Computer history") settings page, a
   **hooks** settings page, workspace **Agents**, and a hardware keypad onboarding (Work Louder
   "Codex Micro"). Fuses are identical except one bit: Claude grants `GrantFileProtocolExtraPrivileges`,
   ChatGPT does not. [02](02-desktop-shells.md).
3. **A string's absence in a stripped binary is a question, not an answer.** The 0.159.3 `codex`
   binary carries `approval_policy` (44), `sandbox_mode` (39), `responses_lite` (18),
   `thread/goal/set` (4) and `guardian` (310) as expected from the source read, but **0** hits for
   `model_catalog_in_context`, the feature flag added on 2026-09-30. Rust can serialise a flag with
   no literal left, so the zero on its own proved nothing; tag ancestry did: the flag commit is not
   in `rust-v0.159.3` and is in `rust-v0.163.0`, and the 0.163.0 build that ChatGPT desktop bundles
   carries the literal 8 times ([01 §3](01-single-file-executables.md)).

4. **Self-update is where the trust root is easiest to compare** (added 2026-10-20, [04](04-update-channels.md)).
   Claude Code verifies a release *manifest* with an RSA-4096 key compiled into the binary (domain
   prefix `claude-code-manifest-v1\0`, sidecar `manifest.json.raw-sig.json`, enforced from 2.1.207 —
   reproduced locally), and the desktop app updates its embedded CLI under a remote flag with a
   floor, a high-water mark and a per-install hashed spread. Sparkle signs the *artifact* (Ed25519);
   Codex publishes sha256 digests and sigstore attestations but delegates its own update to the
   package manager; opencode's curl path pipes `opencode.ai/install` into a shell with no checksum
   and auto-applies patch releases by default; Gemini and the npm paths trust the registry. The
   Desktop Squirrel feed answered three channels with three versions (stable 2.42304.2, latest
   2.42585.0, staggered 2.31226.1) and honoured `maxVersion` server-side.

## Method notes worth keeping

- **REA's "limitations" array is the result.** Every graph came back with explicit statements
  such as "Graph coverage is incomplete; unavailable facts remain explicit and must not be read as
  absence" and "IPC pairing is an inference, not an observation." Those sentences were copied into
  the notes next to the numbers they qualify.
- **Size limits are the first failure, not analysis depth.** `inspect-rust-binary` refuses files
  over 268,435,456 B (the 287 MB `codex` binary); the JS analyser's per-source timeout and the
  parent result budget decide how much of a 2,000-module bundle is retained. Splitting the input
  (Bun modules into a directory; `--source-path` for the Electron shell only) is what made the
  runs finish.
- **The desktop UI is not in the shell.** In both apps the Electron shell is a few hundred KB of
  window management; the surface users see is a bundled SPA (Claude: `ion-dist`, 3,554 chunks;
  ChatGPT: `webview/assets`, 20,107 files). Chunk names and `defaultMessage` catalogues, not the
  shell, are where the UI composition is readable.
