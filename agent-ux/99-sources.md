# 99. Sources and verification record

> Applies this repository's [method of knowing](../ai-workflow/wiki/concepts/primary-source-verification.md)
> unchanged — shipped artifacts over prose, grades on every claim, refutations kept — to a subject where
> the most important evidence (the rendered screen) was **not available.** Researched 2026-09-26.

## 1. Grade vocabulary

| Grade | Meaning here |
|---|---|
| ✅ **extracted** | read from a shipped bundle, binary, package manifest or source at a pinned commit |
| 📣 **vendor-stated** | documentation, blog, changelog — quoted with URL in the product document |
| 📰 **secondary** | third-party write-up; used only for dates and landscape |
| ⚠️ **inferred / unseen** | follows from the artifact but was not observed — **this includes every claim about how something looks** |
| ❌ **refuted** | a vendor statement contradicted by the vendor's own artifact |

> ⚠️ **The limit of this study.** No display was available (`$DISPLAY` empty) — the same device
> constraint the session handoff has recorded since 2026-09-23. A token value, a font file and a UI
> string are facts; the *impression* they add up to is not. "Design language" here is reconstructed from
> the parts list.

## 2. Builds studied

| Product | Build | Source (2026-09-26) | Integrity |
|---|---|---|---|
| Claude desktop | 2.9939.2 | `downloads.claude.ai/releases/win32/x64/RELEASES` → `AnthropicClaude-2.9939.2-full.nupkg` | sha1 `c4d5e0fe…6b62`, 255,805,374 B |
| ChatGPT/Codex desktop | 26.924.22138 (`codexBuildNumber` 11645) | `persistent.oaistatic.com/codex-app-prod/linux/deb/latest/chatgpt_amd64.deb`; Windows MSIX by ZIP range reads | sha256 `ce3bb1aa…b7014e7` |
| Legacy ChatGPT (macOS native) | 1.2026.183 | `persistent.oaistatic.com/sidekick/public/ChatGPT.dmg` | sha256 `49b33cad…4a251d3b8d1` |
| Cursor | 3.22.7 (VS Code 1.128.0) | `downloads.cursor.com/production/37076c6c…/cursor_3.22.7_amd64.deb` | sha256 `923fd2d2…37800ab` |
| Antigravity | 1.23.2 · IDE 2.5.5 · 2.17.0 | `edgedl.me.gvt1.com/…/antigravity/stable/…`; `storage.googleapis.com/antigravity-public/antigravity-hub/2.17.0-…` | commits `15487b30`, `ecfbad74` |
| Windsurf → Devin Desktop | 3.10.35 (VS Code 1.126.0) | `windsurf-stable.codeium.com/api/update/linux-x64/stable/latest` → `Devin-linux-x64-3.10.35.tar.gz` | sha256 `fd50eb54…6ec6`, commit `dfa4a2d6` |
| Orca | 1.4.197 | `stablyai/orca` @ `da6d483` (MIT) | commit |
| Superset | desktop 1.30.2 | `superset-sh/superset` @ `2370f60` (Elastic License 2.0 — source-available, not open source) | commit |
| Paseo | 0.9.2 | `getpaseo/paseo` @ `76a9781` (Apache-2.0) | commit |
| Conductor | 0.87.5 (aarch64) | CrabNebula CDN link from conductor.build | sha256 `6eec4450…ee337eba`, 80,504,300 B |
| Aside | 1.0.922.1 | prior study, [`browser-agents/`](../browser-agents/README.md) | — |

Extraction techniques, recorded because each was needed once: Squirrel `.nupkg` (a zip) for Claude
where the web installer returned 403 to scripts; ZIP **range reads** of a Windows MSIX without
downloading it (OpenAI); a web-UI zip **carved out of a Go binary** (Antigravity 2.0); CSS source-map
`sourcesContent` to recover pre-build token files (Devin); a **brotli asset table** inside a Tauri binary
(Conductor); LZFSE-compressed string tables in a native macOS app (legacy ChatGPT).

## 3. Documentation reached

| Vendor | `/llms.txt` or `.md` | Record |
|---|---|---|
| Anthropic | `docs.claude.com/llms.txt`, `code.claude.com/docs/en/*.md` | ✅ |
| OpenAI | `learn.chatgpt.com/docs/*.md`, `developers.openai.com/*.md` | ✅ |
| Cursor | `cursor.com/docs/*.md` | ✅ |
| Antigravity | `antigravity.google/docs/*.md` | ✅ |
| Windsurf | `docs.windsurf.com/*.md` now points at `docs.devin.ai/llms.txt` | ✅ — the rename reached the docs |
| Conductor | `conductor.build/llms-full.txt`, `/changelog.md` | ✅ |
| Orca, Superset, Paseo | in-repo docs sites and design documents | ✅ (source) |

> 📌 Technique record, extended: every vendor in this study serves raw Markdown. The failure seen with
> Dia ([`browser-agents/99`](../browser-agents/99-sources.md)) did not recur.

## 4. Refutation ledger

| # | Product | Claim (where) | Artifact | Doc |
|---|---|---|---|---|
| U1 | OpenAI | the brief's premise: ChatGPT desktop is a native app distinct from Codex desktop | the current ChatGPT download **is** the Codex Electron build; native survives as legacy with an upgrade screen | [03](03-openai-codex-chatgpt.md) §6 — a premise, not a vendor claim |
| U2 | Claude | "click **Review code** in the top-right toolbar" (desktop docs) | no such string; `Review`, `Review changes` | [02](02-claude-desktop.md) §6 · minor |
| U3 | Cursor | Cursor 3's interface was built "from scratch" (blog) | the UI layer is new; it still runs on the VS Code workbench | [04](04-cursor.md) §6 · partial |
| U4 | Cursor | three density levels (3.4 changelog) | five ship | [04](04-cursor.md) §6 · stale |
| U5 | Cursor | queue/steer keys (overview page, two models on one page) | docs contradict themselves; live binding not confirmed | [04](04-cursor.md) §6 |
| U6 | Cursor | download-URL build sha `…2268` | `product.json` commit `…2260` | [04](04-cursor.md) §6 · minor |
| U7 | Antigravity | "choose between … Planning Mode / Fast Mode" (`docs/artifact-review.md`) | 2.17.0: `throw Error("Planning mode is no longer supported")` | [05](05-antigravity-windsurf.md) §6 · moderate |
| U8 | Orca | an "amber" question mark (docs) | the token is orange: "Orange, not amber" | [06](06-orca-superset.md) §6 |
| U9 | Orca | state is detected from terminal titles (docs) | source header: "never inferred from terminal titles" — yet a lower-authority title channel exists | [06](06-orca-superset.md) §6 |
| U10 | Orca | "the worktree itself is the sandbox" (one docs page) | another page: "not a security sandbox"; code launches agents in bypass mode | [06](06-orca-superset.md) §6 |
| U11 | Paseo | "Title case is wrong" (`docs/design.md`) | fallback string "Permission Required" | [07](07-paseo-conductor.md) §6 · minor |
| U12 | Paseo | bypass modes tagged `colorTier: "dangerous"` | nothing colours them | [07](07-paseo-conductor.md) §6 · minor |
| U13 | Conductor | "295 cities" (docs) | changelog: Adelaide is the 296th | [07](07-paseo-conductor.md) §6 · trivial |

Inconsistencies inside vendor documentation, not refuted by an artifact: Windsurf's docs name Cascade's
modes as "Code/Chat" on one page and "Code/Plan/Ask" on another; Devin's blog ended legacy Cascade on
July 1, yet it ships in the September build (usability ⚠️); Claude's docs say a mid-run correction is read
"after the current action", its UI strings say "after the current turn" (⚠️, unresolved).

> 📌 **Where the refutations cluster.** Unlike the Strands study ([`strands/99`](../strands/99-sources.md)),
> none of these is a safety claim that fails. They are **docs lagging fast-moving artifacts** — a mode
> removed, a count grown, a label renamed. The one with consequences is U10: the same vendor calling the
> worktree a sandbox on one page and not on another, while defaulting agents to bypass.

## 5. Disclosure gaps (not refutations)

| Product | Gap |
|---|---|
| Paseo | push notification bodies (permission input, assistant text, ≤220 chars) go through Expo's push service, outside the E2E relay; `security.md` does not mention it |
| Conductor | local Claude sessions run `bypassPermissions` unless the user enables approvals; "Yes always" on one cloud-agent prompt silently enables "Always allow local commands" |
| Orca, Superset | hooks are written into each agent's **user-global** config; Superset's own post-mortem shows them firing in sessions launched outside Superset |

## 6. Leads for other studies in this repository

- ~~**Codex drift (TASK-002):** three App Server methods absent from `docs/02`~~ — **resolved 2026-09-26:** not
  drift. They exist nowhere in `openai/codex` nor in the engine the app bundles
  ([03](03-openai-codex-chatgpt.md) §1.2.1, [`docs/99` §E.3](../docs/99-sources.md)). **2026-09-27:** they belong to a
  second, cloud-hosted engine the app drives (`durable`, "Long-lived"), or never leave the client.
- **Antigravity ↔ Windsurf:** a shared protobuf engine (`exa.cortex_pb`) is a protocol surface this
  repository has not read on the engine side.
- **ACP** (Agent Client Protocol) now appears in Devin Desktop, Paseo, Superset and Strands' CLI — a
  candidate for its own engine-side reading.

## 7. What was not verified

| Item | Why |
|---|---|
| Every visual impression — colour in context, density, motion, translucency, halo, pulse | no display |
| Which Claude desktop default permission mode a given user sees (Manual vs Auto) | flag-gated per cohort |
| Superset's interface font; where Conductor applies Geist | not determinable statically |
| Whether Orca's `1`/`ESC` keystrokes match every vendor TUI's current menu order | not run |
| Mobile companions (Orca, Superset, Paseo) as design surfaces | out of this pass |
| Cursor's reported Auto-review figures (~4% blocked) | vendor-reported 📣 |

## GUI pass, 2026-09-27

Passive screenshots on macOS through Orca's `orca computer` (accessibility tree + window capture). Builds matched the
static study: ChatGPT 26.924.22138, Claude 2.9939.2, Antigravity 2.17.0; Orca 1.4.209 (study: source 1.4.197); Aside
1.0.922.1. **No agent was run** — every app pointed at the user's own projects, and choosing a scratch folder needs a
file dialog the tool cannot drive — so approval cards and live agent states remain ⚠️. Screenshots showed the user's
own threads and pages; they are not kept in this repository, and only UI structure is recorded.

| Doc | Moved | Still ⚠️ |
|---|---|---|
| [03](03-openai-codex-chatgpt.md) §1.3 | layout ✅ (+ icon rail, summary right panel), composer footer ✅, orange `Full access` chip | approval card weight, squircles, `Work in` / context status |
| [02](02-claude-desktop.md) §7 | working mark = clay spark ✅, collapsed tool lines, repo/PR bar | approval placement (session was in Auto), serif "voice" |
| [05](05-antigravity-windsurf.md) §1 | 2.17 home ✅, `/plan` move ✅, blue unread dot, `Open IDE` hand-off | `Documents`/`Artifacts` placement, sounds |
| [06](06-orca-superset.md) header | sidebar + host badges, usage meters ✅ | agent states, approval default, font |
| [08](08-primitives-rendered.md) §6.2 | **amber rule narrowed**: orange also marks risk (ChatGPT) and working (Claude) | — |
| [`browser-agents/03`](../browser-agents/03-aside-design-ux.md) | Aside sidebar sections + `Ask Aside` ✅ | split tabs |

Next: a live run per app in a scratch project the user sets up once, to see approval cards and `blocked`/`waiting`.
Not installed here, still fully ⚠️: Cursor, Devin, Superset, Paseo, Conductor.

