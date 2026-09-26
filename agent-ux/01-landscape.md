# 01. Landscape — ten agent clients, what they are built from, and how they are related

> The map for this study. Ten products, each read out of its **shipped artifact** — an installer
> unpacked and its bundles searched, or its source cloned at a pinned commit — plus official
> documentation. Researched 2026-09-26. No display was available: **nothing here was seen rendered.**
> What a bundle or a source file contains is ✅; what a screenshot or a video would show is ⚠️ at best.
>
> Grade: ✅ for identity, framework and version (read from package metadata); 📣 for positioning quotes.

## 1. Three families, one question

Every product below answers the same question — *how does a person supervise an agent?* — and they
fall into three families by **who owns the agent loop**.

| Family | Owns the loop? | Products |
|---|---|---|
| **First-party agent apps** | yes — the vendor's own harness | Claude desktop · ChatGPT/Codex desktop · Antigravity 2.0 |
| **Agent-first editors** | yes, inside an IDE | Cursor (Glass + IDE) · Antigravity 1.x/IDE · Windsurf → Devin Desktop |
| **Orchestrators (ADEs)** | **no** — they wrap other vendors' CLIs | Orca · Superset · Paseo · Conductor |
| (prior study) browser agent | yes | Aside ([`browser-agents/03`](../browser-agents/03-aside-design-ux.md)) |

> 📌 **The third family is new to this repository and changes what "client" means.** The Codex study
> ([`docs/02`](../docs/02-app-server-protocol.md)) assumed one client rendering one harness's event
> stream. Orchestrators render **someone else's** agent — and have to *infer* its state from hooks,
> escape codes and terminal titles, or replace its TUI with the vendor's programmatic API
> ([06](06-orca-superset.md) §3). Three of the four ship with the wrapped agents' **approvals switched off**.

## 2. Build inventory

| Product | Version studied | Obtained from | Runtime | UI stack | Doc |
|---|---|---|---|---|---|
| **Claude desktop** | 2.9939.2 | Windows `.nupkg` from the update feed | Electron (Forge + Vite); claude.ai accounts load `claude.ai` remotely, Bedrock/Vertex/gateway accounts load a bundled copy (`ion-dist`, 191 MB) | **CDS** (`@ant/cds`, 119 components) on Base UI + Radix + Tailwind v4 | [02](02-claude-desktop.md) |
| **ChatGPT desktop = Codex app** | 26.924.22138 (Linux `.deb`); legacy native 1.2026.183 | `codex-app-prod` CDN; native `.dmg` | Electron 42 on OpenAI's own Chromium shell "OWL"; spawns a bundled `codex app-server` | React + Tailwind v4.3, lucide, Pierre diffs | [03](03-openai-codex-chatgpt.md) |
| **Cursor** | 3.22.7 (VS Code 1.128.0) | Linux `.deb` | Electron, VS Code fork, **two front ends**: IDE and "Glass" (Agents Window) | Glass: React + **StyleX** + Base UI + cmdk + Lexical; "Cursor Icons 16" | [04](04-cursor.md) |
| **Antigravity 1.x / IDE** | 1.23.2 · IDE 2.5.5 | Linux `.tar.gz` | VS Code fork + separate Agent Manager window | React + Tailwind v3, bound to `--vscode-*` | [05](05-antigravity-windsurf.md) |
| **Antigravity 2.0** | 2.17.0 | Linux `.tar.gz` | thin Electron shell; UI is a zip **inside the Go `language_server` binary** ("Jetski Web") | React + Tailwind v4 + Base UI + **Material Symbols** | [05](05-antigravity-windsurf.md) |
| **Windsurf → Devin Desktop** | 3.10.35 (VS Code 1.126.0) | Linux updater | VS Code fork; embeds the Devin web chat client; Cascade → "Devin Local" over ACP | `@cognitionai/ds` (Figma-exported tokens) + Base UI + Central Icons | [05](05-antigravity-windsurf.md) |
| **Orca** | `da6d483` (1.4.197; MIT) | source | Electron 43 | React 19 + Tailwind v4 + shadcn/Radix, lucide, Geist; in-repo `STYLEGUIDE.md` | [06](06-orca-superset.md) |
| **Superset** | `2370f60` (desktop 1.30.2; **Elastic License 2.0**) | source | Electron 41 | shadcn neutral kit + Vercel ai-elements, react-mosaic panes | [06](06-orca-superset.md) |
| **Paseo** | 0.9.2 `76a9781` | source | daemon + **Expo / React Native** (mobile) + Electron 44 loading the Expo web export | react-native-unistyles, lucide, system fonts | [07](07-paseo-conductor.md) |
| **Conductor** | 0.87.5 (arm64) | `.dmg`; assets from the binary's brotli table | **Tauri 2** + Bun sidecar with the Claude Agent SDK | React 19 + Tailwind v4 + Base UI, lucide, Geist + iA Writer Mono | [07](07-paseo-conductor.md) |

## 3. Lineage — three findings that changed the brief

### 3.1 ChatGPT desktop **is** the Codex app ✅

The brief assumed two OpenAI apps. The current ChatGPT download on macOS, Windows and Linux is the
Codex Electron build: `package.json` names itself `openai-codex-electron`, the Windows MSIX identity
is `OpenAI.Codex` with display name ChatGPT, the two macOS DMGs are the same size with matching sampled
hashes, and the legacy SwiftUI app now ships `CodexUpgradeScreen.swift` — "There's a new ChatGPT app
for you". One product, one bundle, **two personas**: ChatGPT mode hides git and shell detail; Codex mode
shows it ([03](03-openai-codex-chatgpt.md) §1).

### 3.2 Antigravity and Windsurf share an engine, down to protobuf field numbers ✅

Antigravity's agent-step enum `CortexStepType` shares 45 names with Windsurf's, and **43 of the 45 carry
identical field numbers.** Antigravity still calls its agent "Cascade" internally (`cascadeId` ×996), still
sends `x-codeium-csrf-token`, and its Tailwind config still points at `../exa/design_system` with the
Codeium teal `#09b6a2`. After the split, each **repainted from the outside in**: skin first (Material
Symbols vs Central Icons; three-seed tokens vs Figma-exported tokens), then vocabulary (Artifacts vs a
todo list), and last — only at Cognition, and by replacing it — the engine ([05](05-antigravity-windsurf.md) §2).

### 3.3 Windsurf is now Devin Desktop, and the two teams drew opposite conclusions 📣

From the same premise — one window for synchronous editing and asynchronous management gets cramped —
Google removed the IDE ("there is no IDE", Antigravity 2.0) and Cognition kept it ("a full IDE with an
agent manager built in — not the other way around", Devin Desktop).

## 4. What moved in 2026 (from the artifacts' own changelogs and version strings)

| Date | Event | Grade |
|---|---|---|
| 2026-03-17 | Orca's first commit | 📰 |
| 2026-04-15 | Windsurf 2.0: the Kanban "Agent Command Center" | 📣 |
| 2026-05-19 | Antigravity 2.0: agent app with no IDE | 📣 |
| 2026-06-02 | "Windsurf is now Devin Desktop" | 📣 |
| 2026-06-11 | Cursor: Auto-review ("autonomy … more like a dial than a switch") | 📣 |
| 2026-07-09 | last legacy native ChatGPT macOS build, carrying the upgrade screen | ✅ |
| 2026-09-16 | "Claude Cowork and chat are now one Claude" | 📣 |
| 2026-09-22 | Antigravity 2.17 drops Planning mode for `/plan` | ✅ |

> ⚠️ Two of the ten products were **renamed or merged within the research window** and a third split
> into three apps. Any comparison older than a few months names products that no longer exist in that
> form — the same shelf-life problem this repository met with Atlas ([`browser-agents/01`](../browser-agents/01-landscape.md)).

## 5. How to read the rest

- Product documents [02](02-claude-desktop.md)–[07](07-paseo-conductor.md) share one section order:
  build → design system → primitives → philosophy → distinctive → refutations → checklist → open questions.
- [08](08-primitives-rendered.md) crosses them **by harness primitive**: approval, autonomy, plan,
  transcript, diff, parallel work, attention, steering.
- [09](09-design-language.md) answers the question the study was asked: **the shared design language**
  and where the philosophies part.
- [99](99-sources.md) holds builds, hashes, grades and the refutation ledger.
