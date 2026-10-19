# 01. Single-file executables — Bun bundles, a Rust static-pie, and a plain JS bundle

> Four CLIs as installed on this host on 2026-10-19. Read statically; nothing was run.
> REA 6.7.0 was the instrument for the JavaScript graphs and the Rust metadata; `readelf`,
> `objcopy`, `strings` and a 60-line Python parser did the Bun part because REA has no Bun
> single-executable reader. Grades: ✅ read from the bytes · 📣 vendor statement · ⚠️ not
> established here.

## 1. Bun single-file executables: Claude Code CLI and opencode

### 1.1 What the ELF looks like

| | Claude Code CLI 2.1.303 | opencode 1.17.12 |
|---|---|---|
| File | `~/.local/share/claude/versions/2.1.303` (symlinked from `~/.local/bin/claude`) | `opencode-ai/node_modules/opencode-linux-x64/bin/opencode` (`bin/opencode.exe` is a byte-identical copy, despite the extension) |
| Size · SHA-256 | 285,809,912 B · `375988f4…` | 167,577,728 B · `f52fea2e…` |
| ELF | x86-64, dynamically linked, **not stripped**, BuildID `3dd259da…` | x86-64, dynamically linked, **not stripped**, BuildID `c30f169b…` |
| Runtime | `Bun v1.4.4` (string) | `Bun v1.3.14` (string) |
| Bundle section | `.bun` PROGBITS, 0x0a420443 B (172,098,627) at file offset 0x6c63000, plus `.bun_builtins` (0x2858dc B) | `.bun` PROGBITS, 73,951,046 B at 0x593f000; no `.bun_builtins` section listed |
| Trailer | `\n---- Bun! ----\n` | same |

The module graph lives in the `.bun` section ✅. Its layout was **not** taken from Bun's source;
it was recovered by parsing and then checked for self-consistency (every name pointer resolved to
a `/$bunfs/root/…` string in both binaries, 0 failures). Treat the field names as 추정:

```
section = u64 byte_count_without_header ‖ data … ‖ Offsets(32 B) ‖ "\n---- Bun! ----\n"
Offsets = { byte_count: u64, modules: {offset: u32, len: u32}, entry_point_id: u32,
            compile_argv: {offset: u32, len: u32}, flags: u32 }          # offsets are from data start
module record (52 B) = name{off,len} contents{off,len} sourcemap{off,len} bytecode{off,len}
                       + 5 × u32 (loader / encoding / module-format / side flags; last word 0x010101 or 0x01000100)
```

| | Claude Code | opencode |
|---|---|---|
| Module records | **2,686** | **1,200** |
| Entry module | `cli` (24,620 B), first line `// @bun @bytecode` | `src/index.js` (205,724 B), first line `// @bun` |
| `// @bun` JS modules | 2,433 | 320 (+746 `.js` without the marker: vendored UI assets served by the TUI) |
| With a bytecode blob | **2,431** | 0 |
| With a source map | 0 | 0 |
| Other embedded files | 141 `.zst` (zstd-compressed `README-*.md.zst`, `SKILL-*.md.zst`, `SCHEMA-*.md.zst`), 79 `.md`, 24 `.txt` (NOTICE), 2 `.node` (`clipboard-napi.node` 1,072,864 B, …), 2 `.asset`, 2 `.mjs` | 26 `.aac`, 21 `.ttf`, 20 `.woff2`, 20 `.woff`, 9 `.wasm`, 8 `.png`, 7 `.svg`, 6 `.scm` (tree-sitter queries), 5 `.mp3`; `libopentui-c48jzvfh.so` 10,139,328 B; `libfff_c-71argf42.so` 5,576,816 B |
| Largest JS module | `chunk-4jsg44k7.js` 4,994,887 B | `index-DaUQTD8K-e2bvt10k.js` 2,641,212 B |
| `compile_argv` | empty | `--user-agent=opencode/1.17.12 --use-system-ca --` |
| `flags` | 0x1bff | 0x3 |

Reading of the differences ✅:

- **Claude Code ships source *and* bytecode.** Every JS module keeps its text (the parser above
  wrote 56 MB of it) and 2,431 of them also carry a JSC bytecode blob — the `// @bun @bytecode`
  marker on the entry says so. The text is still what REA parsed; whether the runtime loads text
  or bytecode is a runtime fact and ⚠️ not established here.
- **Claude Code bundles its skills and docs as files.** 79 Markdown files plus 141 zstd-compressed
  ones named `SKILL-<hash>.md.zst`, `README-…`, `SCHEMA-…`. The tool-use note
  ([03](03-tool-use-patterns.md)) reads those for what they instruct.
- **opencode bundles a terminal UI toolkit as native code** (`libopentui`, 10 MB) and fonts, audio
  and tree-sitter query files; it compiles nothing to bytecode. Its only compile-time argument is
  a user-agent string and `--use-system-ca`.

### 1.2 What REA's JavaScript analyser returned

Both split directories were given to `rea analyze-javascript-application` (1,800 s per-source
timeout, 2 GiB analyser heap).

| | Result |
|---|---|
| opencode | ✅ Complete graph, evidence `ev_9ad22e97…`, directory digest `d30dcd7a…`. 5,014 nodes: 1,976 `javascript-module`, 1,063 `javascript-asset`, 108 `source-map` (REA's inference from vendored maps), 54 `endpoint`, 1 `native-addon`, 1 `electron-renderer` (a false positive on an HTML asset — REA lists it as a candidate, not a fact). Literal endpoint paths: `/chat/completions`, `/responses`, `/embeddings`, `/images/generations` — the OpenAI-shaped provider surface. Limitations quoted by REA: "JavaScript and HTML were parsed as inert text; bundle bootstrap code was never executed", and two chunks exceeded the parent result budget so only static facts were kept for them. |
| Claude Code CLI | ⚠️ `resource_constraint`: "The parent's result capacity was exhausted after retaining static facts for chunk-750bqvg0.js; remaining sources were not analyzed" — at source 526 of 2,439. No Evidence was retained. A smaller `--source-path` selection would be the next step; it was not done in this pass. |

## 2. Gemini CLI 0.42.0 — a bundle REA could not finish on this host

`/usr/local/lib/node_modules/@google/gemini-cli/bundle/`: 91 MB, 102 JS chunks of which three
are 14.7 MB each (`chunk-DN4XSYRG.js`, `chunk-DMWX7UP6.js`, `chunk-7VVHSNDQ.js`) ✅. Entry
`gemini.js` is a plain ESM shim. REA's first run stopped at the 300,000 ms per-source default
("Parsing and projecting chunk-7VVHSNDQ.js (14/102)"), returning a `partial_observation` with the
inventory graph. The 1,800 s re-run (4 GiB heap) was still at 16/102 after an hour and was
stopped by hand because three analysers were sharing a 14 GiB host. **No application graph for
Gemini CLI** ⚠️. The tool-use reading in [03](03-tool-use-patterns.md) used grep on the bundle
instead.

## 3. Codex 0.159.3 — a stripped Rust static-pie, read with `strings`

### 3.1 Packaging

`@openai/codex` is a 1-file npm wrapper (`bin/codex.js`, `files: ["bin/codex.js"]`) with six
platform packages as `optionalDependencies` (`npm:@openai/codex@0.159.3-linux-x64` …) ✅. The
Linux x64 payload under `vendor/x86_64-unknown-linux-musl/`:

| File | Size | `file` |
|---|---|---|
| `bin/codex` | 287,086,056 B · SHA-256 `8bf204b3…` | ELF x86-64 **static-pie**, stripped |
| `bin/codex-code-mode-host` | 74,072,976 B · `fe64bd08…` | static-pie, stripped |
| `codex-path/rg` | 5,408,904 B | static-pie, stripped (ripgrep on the agent's PATH) |
| `codex-resources/voice/bin/codex-voice-host` | 64,531,104 B | dynamically linked, **with debug_info, not stripped** |
| `codex-resources/voice/lib/libgstreamer-1.0.so.0`, `libglib-2.0.so.0`, `libgio-2.0.so.0` | 1.5–2.3 MB | shared objects |

### 3.2 What REA could and could not do

- `rea inspect-rust-binary bin/codex` → `resource_constraint`: "Selected artifact exceeds
  268435456 bytes" (limit 256 MiB). ⚠️ The main binary is 19 MB over REA's admission limit.
- `rea inspect-rust-binary bin/codex-code-mode-host` → ✅ `auditable_metadata: null` (no
  cargo-auditable `.dep-v0` section — "Absence of `.dep-v0` does not mean the binary has no
  dependencies"), `rustc_commit` inferred from 85 `/rustc/59807616e1fa2540724bfbac14d7976d7e4a3860/`
  path strings (`evidence_kind: "inferred"`, "The hash is not a claim that that compiler produced
  the binary").
- Native disassembly needs Ghidra/Hopper/IDA — none on this host.

### 3.3 Contract strings in the shipped binary vs the source read

`strings -n 6 bin/codex` → 616,723 strings. Counts for terms the source studies
([`docs/02`](../docs/02-app-server-protocol.md), [`docs/14`](../docs/14-windows-sandbox.md),
[`docs/99` §E](../docs/99-sources.md)) rely on:

| Term | Hits | Reading |
|---|---|---|
| `approval_policy` / `sandbox_mode` | 44 / 39 | config keys present ✅ |
| `on-request` / `untrusted` / `never` / `danger-full-access` | 32 / 90 / 188 / 33 | enum literals present ✅ |
| `responses_lite` | 18 | the request-shape branch Aside re-implements (`SYNTHESIS` §2) is in the shipped build ✅ |
| `thread/goal/set` | 4 | the method added in the 2026-09-30 window ✅ |
| `guardian` | 310 | the approval-executor feature ✅ |
| `codex-code-mode-host` | 3 | the main binary names its sidecar ✅ |
| `chatgpt.com/backend-api` / `api.openai.com` | 39 / 8 | two backends ✅ |
| `model_catalog_in_context` | **0** | ⚠️ the feature flag from `2e5fea64ee` leaves **no literal**. Rust serialises `serde` names and enum variants at compile time and the symbol table is stripped, so absence here is not absence of the feature. The source read in `docs/99` §E.5 stands; the binary neither confirms nor refutes it. |
| `Missing provenance does not supply user authorization.` | 0 | expected: a doc comment never reaches a binary |
| `/rustc/<40 hex>/` | 85, one hash `59807616e1…` | same toolchain hash as the code-mode host (same build) ✅ |
| `0.159.3` as a bare version line | not matched | the CLI version is formatted at runtime from `CODEX_VERSION` (present as an env/constant name) |

> 📌 The point of the table is the zero row. A stripped Rust binary is a **weak oracle for
> feature flags** and a **good oracle for wire literals** (method names, enum strings, URLs).
> Use it to confirm the wire contract, not to adjudicate what a feature does.

### 3.4 Also bundled: the same binaries inside ChatGPT desktop

The ChatGPT deb carries `resources/codex` (296,885,960 B, SHA-256 `70ea33b7…`) and
`resources/codex-code-mode-host` (74,277,776 B) — a **different build** from the npm 0.159.3
(sizes differ by 9.8 MB; the desktop's version string was not matched by the `^0\.1xx\.y$` probe ⚠️).
See [02 §2](02-desktop-shells.md).
