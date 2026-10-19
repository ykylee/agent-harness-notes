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

The module graph lives in the `.bun` section ✅. The layout below was first recovered by parsing
(every name pointer resolved to a `/$bunfs/root/…` string in both binaries, 0 failures) and then
**confirmed against Bun's source on 2026-10-19 evening** — `src/standalone_graph/StandaloneModuleGraph.zig`
at `bun-v1.3.14` (opencode's runtime) and the Rust rewrite
`src/standalone_graph/StandaloneModuleGraph.rs` at `bun-v1.4.3` (the newest public tag; Claude Code
reports `Bun v1.4.4`, which has **no public tag or release** ⚠️, so its layout is assumed equal to
1.4.3). Both versions define the same three structures ✅:

```
section = u64 byte_count ‖ data … ‖ Offsets(32 B) ‖ "\n---- Bun! ----\n"   # "the final 8 bytes … are the length of the module graph"
Offsets  = #[repr(C)] { byte_count: usize, modules_ptr: StringPointer, entry_point_id: u32,
                        compile_exec_argv_ptr: StringPointer, flags: Flags(u32) }      # offsets from data start
record   = #[repr(C)] CompiledModuleGraphFile (52 B) { name, contents, sourcemap, bytecode, module_info,
                        bytecode_origin_path: StringPointer ×6 ; encoding, loader, module_format, side: u8 ×4 }
```

The first parse had read the 20-byte tail as five `u32`s; it is two more `StringPointer`s
(`module_info`, `bytecode_origin_path` — "must match exactly at runtime for bytecode cache hits") plus
four `u8` enums. The 1.4.3 `Flags` bitset decodes the two binaries' `flags` words:

| Bit | 1.4.3 name | Claude Code `0x1bff` | opencode `0x3` |
|---|---|---|---|
| 0–3 | `DISABLE_DEFAULT_ENV_FILES`, `DISABLE_AUTOLOAD_BUNFIG`, `_TSCONFIG`, `_PACKAGE_JSON` | all four | env files + bunfig only |
| 4 | `SOURCE_TEXT_CONTIGUOUS` | ✓ | — |
| 5 | `HAS_SOURCE_HASHES` ("loading a module from bytecode never has to hash — i.e. page in — its source text") | ✓ | — |
| 6 | `HAS_BUILTIN_BYTECODE` | ✓ | — |
| 7 | `HAS_BYTECODE_STRING_TABLE` | ✓ | — |
| 8 | `HAS_STARTUP_MODULE_COUNT` ("the entry point's static import closure … load before the first `import()`") | ✓ | — |
| 9 | `HAS_MODULE_INFO_STRING_TABLE` | ✓ | — |
| 10 | `CROSS_COMPILED_BYTECODE` | — | — |
| 11 | `HAS_PRELINKED_MODULE_GRAPH` | ✓ | — |
| 12 | `HAS_RUNTIME_OPTIONS` | ✓ | — |
| 13 | `HAS_LINKED_BYTECODE_PAYLOAD` | — | — |

So Claude Code 2.1.303 is built with bytecode, source hashes, a prelinked module graph and a
startup-closure count — the Bun features that avoid paging in source text at launch — and opencode
uses none of them (1.3.14 only defines bits 0–3). Bits 4–13 did not exist in 1.3.14, which is why a
1.3.14 reader would reject the Claude binary's flags word.

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
| Claude Code CLI | First run ⚠️ `resource_constraint`: "The parent's result capacity was exhausted after retaining static facts for chunk-750bqvg0.js; remaining sources were not analyzed" — at source 526 of 2,439, no Evidence retained. **Evening re-run on the 150 largest `chunk-*.js`** ✅ (evidence `ev_c2ff746e…`; a first attempt that named the extension-less entry `cli` was refused — "Select an exact relevant file path from the artifact inventory"): 11,355 nodes — 6,238 `javascript-module` (REA splits the bundler chunks into their logical modules), 2,429 `javascript-asset`, 107 `endpoint`, 3 `worker`, 2 `native-addon`. None of the 107 endpoint nodes is a literal URL (the API hosts are assembled at runtime; the tool-use note found them by grep instead). REA's caveats: "Caller-selected source analysis leaves 2289 inventoried files outside analysis scope", and several chunks (e.g. `chunk-07svn3rg.js`) kept static facts only — 292 limitation lines. |

## 2. Gemini CLI 0.42.0 — a bundle REA could finish only without its three largest chunks

`/usr/local/lib/node_modules/@google/gemini-cli/bundle/`: 91 MB, 102 JS chunks of which three
are 14.7 MB each (`chunk-DN4XSYRG.js`, `chunk-DMWX7UP6.js`, `chunk-7VVHSNDQ.js`) ✅. Entry
`gemini.js` is a plain ESM shim. REA's first run stopped at the 300,000 ms per-source default
("Parsing and projecting chunk-7VVHSNDQ.js (14/102)"); a 1,800 s re-run was still at 16/102
after an hour and was stopped by hand.

**Evening re-run with `--source-path` on the other 69 JS sources** ✅ (evidence `ev_fb798187…`):
3,269 nodes — 2,210 `javascript-module`, 763 `javascript-chunk`, 86 `javascript-asset`, 56
`endpoint`, 3 `source-map`. REA's own caveats: "Caller-selected source analysis leaves 33
inventoried files outside analysis scope", and two chunks (`chunk-IUUIT4SU.js`, `chunk-JEW7ZIWE.js`,
the tool-definition chunk) kept static facts only because their relationship expansion exceeded the
parent's result budget — 111 limitation lines in all. Of the 56 endpoint nodes only two are literal
enough to read, and they are the same string: a **local model endpoint**
``http://localhost:${port}/${LITERT_API_VERSION}/models/${GEMMA_MODEL_NAME}:generateContent``
(`mechanism: "call:fetch"`) — the CLI carries a LiteRT-served Gemma path next to the Google API
client ⚠️ (not traced further). The core 14.7 MB chunk that holds the scheduler and policy engine
(`7VV` in [03 §5.1](03-tool-use-patterns.md)) is **not in this graph**; the tool-use reading used
grep on it instead.

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
| `model_catalog_in_context` | **0** | the feature flag from `2e5fea64ee` leaves no literal. **Resolved 2026-10-19 evening:** `git merge-base --is-ancestor 2e5fea64ee rust-v0.159.3` → **no** (the commit is dated 2026-09-30 09:52 UTC, the tag 21:46 UTC the same day, on a release branch that does not contain it); `… rust-v0.163.0` → **yes**. The 0.163.0 build bundled in ChatGPT desktop (§3.4) carries the literal **8 times**. So the zero was true, and the right tool to prove it was tag ancestry, not `strings`. The source read in `docs/99` §E.5 stands for HEAD; 0.159.3 ships without the flag ✅ |
| `Missing provenance does not supply user authorization.` | 0 | expected: a doc comment never reaches a binary |
| `/rustc/<40 hex>/` | 85, one hash `59807616e1…` | same toolchain hash as the code-mode host (same build) ✅ |
| `0.159.3` | 18 (as a substring; the earlier whole-line probe `^0\.159\.3$` missed it because adjacent literals are merged) | version present ✅ |

> 📌 The point of the table is the zero row, and what it took to read it. A stripped Rust binary is a
> **good oracle for wire literals** (method names, enum strings, URLs, the version substring) and an
> **ambiguous oracle for feature flags**: a zero can mean "not compiled in" or "serialised without a
> literal". Here it meant the former, but only `git merge-base --is-ancestor` against the release
> tag could say so. Record the tag, not the count.

### 3.4 Also bundled: a newer Codex inside ChatGPT desktop

The ChatGPT deb carries `resources/codex` (296,885,960 B, SHA-256 `70ea33b7…`) and
`resources/codex-code-mode-host` (74,277,776 B). `strings` finds the substring `0.163.0` **31
times** and `0.159.3` none, so the desktop bundles **Codex 0.163.0** (tag `rust-v0.163.0`,
2026-10-15 18:57 UTC, four days after the npm 0.159.3 build) ✅. Same `rustc` toolchain hash
`59807616e1…` (86 path strings). Term counts, 0.163.0 vs 0.159.3: `model_catalog_in_context`
**8 vs 0**, `responses_lite` 19 vs 18, `thread/goal/set` 4 vs 4, `guardian` 337 vs 310,
`code_mode` 92 vs 84, `durable` 29 vs 29, `aeon` 0 vs 0 (the webview's name for durable threads
does not reach the engine). See [02 §1](02-desktop-shells.md).
