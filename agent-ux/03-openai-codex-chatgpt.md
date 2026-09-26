# 03. OpenAI — the Codex desktop app, which is now the ChatGPT desktop app

> Products:
> - **ChatGPT desktop "superapp"**: Codex lineage, Electron code on OpenAI's "OWL" Chromium shell, 26.924.22138
>   (`codexBuildNumber` 11645). Obtained as the Linux `.deb` from
>   `https://persistent.oaistatic.com/codex-app-prod/linux/deb/latest/chatgpt_amd64.deb` (sha256 `ce3bb1aa…b7014e7`,
>   last-modified 2026-09-26). The Windows MSIX `ChatGPT-x64.msix` (26.924.2738.0) was inspected by ZIP range reads,
>   not downloaded.
> - **Legacy native ChatGPT for macOS**: `com.openai.chat` 1.2026.183 (build 1783607847). Obtained from
>   `https://persistent.oaistatic.com/sidekick/public/ChatGPT.dmg` (sha256 `49b33cad…4a251d3b8d1`, last-modified 2026-07-09).
>
> Method: static extraction (asar, CSS custom properties, the `defaultMessage` string tables, `strings`, LZFSE string tables,
> MSIX manifest). **No display: nothing was seen rendered.** Vendor docs read as `.md` from `learn.chatgpt.com` and
> `developers.openai.com`. Researched 2026-09-26.
>
> Dominant grade: ✅ extracted from shipped artifacts. Everything visual is ⚠️. One premise refuted (§6).

## 1. What it is and how it is built

### 1.1 The premise "two apps" was wrong

The study was scoped as "Codex desktop (Electron) vs ChatGPT desktop (native SwiftUI)". **On 2026-09-26 that is one
product.** The ChatGPT desktop app offered for macOS, Windows and Linux is the Codex Electron app renamed. The native
SwiftUI ChatGPT still downloads, but it is a legacy build whose job now includes telling you to leave.

| Fact | Where | Grade |
|---|---|---|
| The Linux package `chatgpt` 26.924.22138 is served from `codex-app-prod/`. Its `Homepage:` is `https://developers.openai.com/codex/app` | deb `control` | ✅ |
| `app.asar` `package.json`: `"name": "openai-codex-electron"`, `"productName": "Codex"`, `"desktopName": "chatgpt.desktop"` | `resources/app.asar` in ChatGPT 26.924.22138 | ✅ |
| `codex-app-prod/Codex.dmg` and `codex-app-prod/ChatGPT.dmg` are both 710,245,920 B, and 1 MiB range hashes match at offsets 0 and 700,000,000 | HTTP range reads | ✅ (sampled, not a full-file hash) |
| MSIX `<Identity Name="OpenAI.Codex">`, `<DisplayName>ChatGPT</DisplayName>`. Payload has both `app/ChatGPT.exe` and `app/Codex.exe`. `owl-app.ini`: `UserDataDirectoryName=Codex` | `AppxManifest.xml`, `app/resources/owl-app.ini` in MSIX 26.924.2738.0 | ✅ |
| Settings: `Use ChatGPT Dock icon` / `Use Codex Dock icon` | string ids `settings.general.appearance.dockIcon.*` | ✅ |
| "Download ChatGPT for macOS or Windows… Choose ChatGPT or Codex. In ChatGPT, use the toggle above the composer to select Chat or Work." | https://learn.chatgpt.com/docs/app.md | 📣 |
| The native app ships `ChatGPTCodexUpgrade/CodexUpgradeScreen.swift`: `There's a new ChatGPT app for you`, `We're introducing a new ChatGPT app with Work… Download the new app to keep getting the latest features.`, `Download new ChatGPT app`, plus a `CodexUpgradeInstaller` (download → signature-validate → install) and `superapp-header.png` | `ChatGPT.framework` in com.openai.chat 1.2026.183 | ✅ |

> 📌 The useful comparison is therefore **(A) the Electron superapp** against **(B) the legacy SwiftUI app**: one vendor,
> the same harness primitives, two rendering stacks. §5 shows the *words* converged while the *pixels* did not.

### 1.2 (A) Superapp: stack and runtime

| Item | Value | Grade |
|---|---|---|
| App code | Electron 42.3.0 API, electron-forge (deb/rpm/msix/zip makers), Vite 8 + rolldown, React, **Tailwind v4.3.3** | ✅ `package.json`, CSS licence banner |
| Runtime | **Not stock Electron.** `owl-electron-app.json` has `"runtimeName": "owl"`. Scripts include `owl:ensure` and `ensure-owl-electron-types`. On Windows the payload is a full Chromium (`chrome.dll`, `elevation_service.exe`, `chrome_pwa_launcher.exe`, `154.0.8037.57.manifest`) | ✅ files; ⚠️ that OWL is the Atlas browser's runtime is inferred |
| Agent backend | Bundled `resources/codex` (285 MB) is spawned as `app-server --analytics-default-enabled`, version-checked with `app-server daemon version`. Also bundled: `codex-code-mode-host`, `rg`; on Windows `codex-windows-sandbox-service.exe` registered as LocalSystem service `CodexSandboxService.OpenAI.Codex`, and `codex-command-runner.exe` | ✅ `.vite/build/main-*.js`, `AppxManifest.xml` |
| Other runtimes | `cua_node/` (Node, Playwright, `@oai/browser-desktop` including agent-facing `environment-docs/codex-app/confirmations.md`), `node-pty`, `better-sqlite3`, `@parcel/watcher`, `yjs`, `vscode-jsonrpc` | ✅ |
| One bundle, four hosts | CSS branches on `data-codex-window-type` = `electron` · `extension` (IDE extension) · `browser` · `chrome-extension` | ✅ `webview/assets/app-shared-*.css` |

**App Server client, confirmed ✅.** The main-process and webview bundles contain 169 distinct method or notification literals.
The most referenced are `item/completed` (46), `turn/completed` (42), `turn/started`, `thread/start`, `turn/start`,
`item/agentMessage/delta`, `item/commandExecution/requestApproval` (24), `item/fileChange/requestApproval` (19),
`item/permissions/requestApproval` (17), `item/tool/requestUserInput` (17), `turn/steer`, `turn/interrupt`, `thread/fork`,
`thread/rollback`, `turn/plan/updated`, `turn/diff/updated`, `thread/goal/*` and `thread/realtime/*`. The webview switches on the item
types `userMessage, agentMessage, reasoning, plan, commandExecution, fileChange, mcpToolCall, dynamicToolCall,
collabAgentToolCall, webSearch, imageView, imageGeneration, hookPrompt, contextCompaction, enteredReviewMode,
exitedReviewMode`, the taxonomy in [../docs/02-app-server-protocol.md](../docs/02-app-server-protocol.md).

Server requests are **bucketed per turn** before rendering. One switch collects
`item/commandExecution/requestApproval | item/fileChange/requestApproval | item/permissions/requestApproval |
item/tool/requestOptionPicker | item/tool/requestUserInput` into a `Map` keyed on `params.turnId`. Replies go through
`replyWithCommandExecutionApprovalDecision` / `replyWithFileChangeApprovalDecision` ✅ (`webview/assets/app-initial-*.js`).

#### 1.2.1 Methods the shipped client uses that the open-source engine does not have

> **Resolved 2026-09-27** ([../docs/99-sources.md §E.3](../docs/99-sources.md)). This section first read "either
> these are experimental or internal, or `docs/02` has drifted." **Neither held: the app drives a second engine.**

Besides the bundled `codex app-server`, the main process defines a host `durable` ("Long-lived") at
`wss://codex-cloud-backend.chatgpt.com/`, reached through an adapter that rewrites requests into its own dialect
(`thread/queue/add` → `turn/addUserMessage`, `thread/start` → `thread/prewarm`, `environmentConfigId`) and answers
`config/*` from an in-memory config ✅ (`.vite/build/main-*.js`, `src-*.js`). The webview calls these threads **Aeon**
(`aeonThreads`, `aeonExecutionTarget`, `isAeonThread`).

| Method | Bundle refs | Verdict |
|---|---|---|
| `thread/startAeon` | 8 | ✅ durable-host dialect: starts a long-lived (Aeon) thread |
| `item/tool/requestOptionPicker` | 14 | ⚠️ a server→client multiple-choice ask no open-source engine sends; by elimination, from the durable host. Also accepted as the dynamic tool `request_option_picker` |
| `item/plan/requestImplementation` | 12 | ✅ **client-local**: pushed into the client's own request queue (`implement-plan:<turnId>`) to render `Yes, implement this plan` (`codex.userMessage.implementPlan`) |

Same pattern: `thread/stop` and `turn/addUserMessage` (durable dialect), `item/tool/requestSetupCodexContextPicker`
(⚠️ as the option picker). `thread/rollback`, removed from the open-source protocol on 2026-09-11 (#44915), is still
referenced. "Absent from the bundled engine" was checked with `strings` on `codex-cli 0.158.0-alpha.2.1`,
positive-controlled.

Observed on macOS (2026-09-27): the app logs `remote_connections … hostId=durable state=disconnected` at every
launch and never connects — the feature ships and is **not provisioned** for the account used. About 33 other methods
the client calls are **experimental** methods of the open-source engine, filtered out of its generated schema; that
gap was in `docs/02`, now fixed.

### 1.3 (A) Layout: where the agent lives

⚠️ Reconstructed from strings and chunk names (`sidebar-*`, `thread-side-panel-*`, `terminal-panel`, `plan-side-panel`), not from seeing the UI.

> **GUI pass 2026-09-27 (macOS, same build, `orca computer` screenshots; passive — no agent was run).** ✅ Three regions as below: sidebar of projects with threads nested under them, the
> thread in the centre, a right panel. Not in the reconstruction: a **narrow icon rail** left of the sidebar. The right
> panel as seen was a **summary view** (repository, branch with `+n −n`, and a `Sources` list), not the tab set below,
> which it presumably switches to. Composer footer as seen: `+`, the permission chip, model + effort, mic, send/stop;
> a `n files changed +n −n` pill floats above the composer. `Work in` and context status were not visible in that state.
> A running thread shows a **grey** spinner in the sidebar; the stop button is accent blue. The permission chip for
> `Full access` renders in **orange with a warning glyph** — orange marks a *risky state* here, not only "needs you"
> (see [08 §6.2](08-primitives-rendered.md)). Approval cards were not seen (that thread was in Full access).
> Squircles cannot be judged from a screenshot; Chromium 154 is new enough for `corner-shape` ⚠️.

| Region | Contents |
|---|---|
| Left sidebar | Width `clamp(240px, var(--codex-sidebar-preferred-width,275px), …)`, optionally translucent. Projects, chats, **priority threads** (`Waiting, unread, and active chats first`), archived tasks, custom sections |
| Center | Chat thread. The composer footer carries permissions, model+effort, `Work in` location (`Work locally` / `New worktree` / `Remote` / `Cloud`), branch switcher (`Uncommitted: {n} files`) and context status (`Context: {n}% left`) |
| Right side panel (tabs) | `Review`, `Files`, `Browser` (in-app Chromium tab with its own site-permission UI), `Terminal`, `Side chat`, `PR #{number}`, Plan. The terminal can dock `Bottom` or `Right` |
| Outside the window | Popout/Quick-chat on a global hotkey (📣 Option+Space / Win+Alt+P), floating **Pets**, and a hardware keypad (§3.7) |

`Cycle workspace layout — Step from full view to split view, hide tabs, or show tabs beside Chat` ✅. Toggle review panel
⌘⌥B (📣 `reference/commands.md`). **There is no editor pane**: the agent is the centre, code appears only as review/diff and file previews.

### 1.4 (B) Legacy native app

| Item | Value | Grade |
|---|---|---|
| Stack | **SwiftUI + AppKit**. `ChatGPT.framework` (115 MB) links SwiftUI, AppKit, Combine, WebKit, JavaScriptCore, ScreenCaptureKit, Charts, WidgetKit. Third-party: Sparkle, Lottie, LiveKitWebRTC, Highlightr | ✅ |
| Packages | `Styleguide/SwiftUIStyleguide` (ships a `default.metallib`), `OAIMarkdown`, `DotBall`, `ChatGPTPairWithAI` (`OboeDiffViewModel`), `ChatGPTCodexUpgrade` | ✅ |
| Min OS / SDK | macOS 14.0 / macosx26.4, Xcode 26.4.1 | ✅ `Info.plist` |
| Strings | Cross-platform table `Assets.bundle/CompressedStrings/en.json.lzfse` (2,375 keys; includes iOS/CarPlay keys) | ✅ |
| Agent model | Chat plus **Work with Apps** (attach to an editor or terminal and read/edit its content). Codex appears only as the phone "Codex Remote" / voice client strings | ✅ strings; ⚠️ which render on macOS |

## 2. Design system (A)

Source: `webview/assets/app-shared-*.css` (1.15 MB, 2,601 distinct custom properties) in ChatGPT 26.924.22138. All ✅ unless marked.

**Four token layers**:
1. Primitive ramps.
2. The ChatGPT-web intent×variant matrix: `--color-background-{primary|info|danger|caution|discovery|success}-{solid|soft|soft-alpha|ghost|outline|surface}-{hover|active}`.
3. App semantics: `--app-color-*`.
4. **`--color-token-*`, named after VS Code theme keys.** Examples: `--color-token-side-bar-background`, `-list-hover-background`,
   `-editor-warning-foreground`, `-diff-editor-inserted-line-background`, `-activity-error-badge-background`.
   Under `:root[data-codex-window-type=extension]` each one is rebound to `var(--vscode-…)` (413 references).

> 📌 **VS Code's theme schema is the design-token API.** The IDE extension inherits any editor theme for free, and the
> standalone app implements the same keys with its own palette.

| Role | Light | Dark |
|---|---|---|
| Neutral ramp `--gray-0…1000` (25-step) | `#fff` → `#0d0d0d` | mirrored: `#0d0d0d` → `#fff`; pure neutral, no hue tint |
| Surface `--app-color-background-surface` | `gray-fixed-0` `#fff` | `gray-fixed-900` `#181818` |
| Under-surface (sidebar) | `gray-fixed-50` `#f9f9f9` | `black` |
| Foreground `--app-color-text-foreground` | `#1a1c1f` | `gray-fixed-150` `#dfdfdf` |
| Primary button / `primary-solid` | `gray-900` (grayscale, not blue) | `gray-950` |
| Accent text / focus ring | `--blue-300` `#339cff` | same |
| Borders | foreground mixed at 5 / 8 / 12% (`-light` / default / `-heavy`) | same rule |
| Status | error `--red-500`, warning `--orange-500`, success `--green-500` `#00a240` | `red-300`, `orange-300`, `green-300` |
| Windows tile | `BackgroundColor="#3143FF"` (`AppxManifest.xml`) | — |

| Category | Values |
|---|---|
| Type scale | Tailwind remapped **down**: `--text-xs 11px`, `sm 12px`, `base 14px`, `lg 16px`; headings 18/20/24/28 |
| UI font | `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`, the **system font**. Users can override UI, code and content fonts separately |
| Bundled fonts | `OpenAISans-{Regular,Medium,Semibold}.woff2` and `OpenAISerif-Light.woff2`, used only via `.font-openai-sans` in onboarding chunks; Carlito (office previews); KaTeX |
| Mono | `ui-monospace, "SFMono-Regular", "SF Mono", menlo, consolas, …` |
| Radii | `2xs .125rem · xs .25 · sm .375 · md .5 · lg .625 · xl .75 · 2xl 1 · 3xl 1.25 · 4xl 1.5rem`, all × `--corner-radius-scale` |
| Squircles | `@supports (corner-shape: superellipse(1.5))` → `--codex-corner-radius-scale: 1.25`, `--codex-corner-shape: superellipse(1.5)`; menus use `--menu-corner-shape: var(--codex-corner-shape, round)` |
| Hairlines / shadows | `--border-width-hairline: .5px`; `--shadow-hairline: 0 0 0 .5px #0000001a`; `--shadow-sm 0 1px 2px -1px #00000014` … `--shadow-2xl 0 16px 32px -8px #00000030` |
| Spacing / chrome | `--spacing .25rem`; toolbar `46px` / `36px` / pane `40px`; titlebar `44px`; composer button `28px` |
| Motion | `--cubic-enter (.19,1,.22,1)`, `--cubic-exit (.8,0,.4,1)`, `--cubic-move (.65,0,.35,1)`; `.15s` basic / `.3s` relaxed; `--animate-token-pulsing-dot 1.25s`; setting `Reduce motion: Off / On / System` |
| Icons | lucide (3,274 per-icon chunks) plus about 2,300 SVGs, many custom (`agent-mode.svg`, `add-sources.svg`) |
| Components | **sonner** (toasts), **cmdk** (command menu), **Pierre diffs** on Shiki, xterm, ProseMirror/Lexical. Radix present (`radix-popper`, `DismissableLayer` in 7 files; ⚠️ extent unknown). A Snap **Valdi** runtime appears only in finance chunks |
| User theming | Per mode: accent, `ink`, `surface`, `contrast`, fonts, `Translucent sidebar`, code theme (28 presets: Codex, Gruvbox, Xcode, Dracula, Nord, Linear, Raycast, Vercel, Notion, …); **copy/import a theme share string** |

**(B) native ⚠️**: no UI font bundled (only math `.otf`). Code calls `systemFontOfSize:weight:` and `monospacedSystemFontOfSize:weight:`, so SF Pro / SF Mono.
Semantic colours are not recoverable from `Assets.car` statically.

## 3. How harness primitives are rendered

Strings are ✅ (string ids from the `defaultMessage` tables in ChatGPT 26.924.22138 unless noted). Placement and visual weight are ⚠️.

### 3.1 Approval / permission

An inline **request card** in the thread (`pending-request-item-panel`), with the status line `Awaiting approval`.

| Request | Prompt | Label |
|---|---|---|
| command (`item/commandExecution/requestApproval`) | `Allow ChatGPT to run this command?` / `Do you want {actor} to run this command?` | `Terminal` |
| network | `Allow ChatGPT to connect to {destination}?` / `Allow {actor} to connect to {destination}?` | `Internet access` |
| file change (`item/fileChange/requestApproval`) | `Allow ChatGPT to edit the following file(s)?`, moves as `{sourcePath} → {targetPath}` | `Edit files` |
| permissions (`item/permissions/requestApproval`) | `Permission request: {reason}` | `Ask permission` |
| MCP tool | 167 per-tool prompts, e.g. `Allow Google Calendar to decline an event?` | — |

**Scope ladder** and the App Server decision each option most plausibly maps to (⚠️ mapping inferred; the decision names are from `docs/02`):

| Button | Scope | ≈ `ReviewDecision` |
|---|---|---|
| `Allow once` | this call | `accept` |
| `Allow this conversation` | the thread | `acceptForSession` |
| `Allow commands that start with {command} for this conversation` / `Allow similar commands` | a command prefix | amendment-carrying variant |
| `Always allow` | persistent | amendment-carrying variant |
| `Allow all edits` — `Allow this and future file edits in this conversation without asking again` | all file edits, this thread | `acceptForSession` |
| `Deny` | — | `decline` |

- A `Reason` row appears, and long commands get `Expand` / `Collapse`. The command palette has `Approve request` / `Decline request`.
- **Native (B) differs.** Its strings `Allow for this chat`, `Always allow host` and `Always approve` add a **host** scope. Declining takes free text: `Tell Codex what to do`. ✅ string table, ⚠️ platform.

> 📌 The superapp shows no `cancel` (abort the turn) on the card; Stop lives on the composer. The native Remote client pairs
> *decline* with *feedback*, which is the channel-renderable direction of
> [SYNTHESIS §2.1](../SYNTHESIS.md#21-approval-as-a-protocol-primitive).

### 3.2 Autonomy modes and model/effort

The composer's permissions dropdown is titled `How should ChatGPT actions be approved?`.

| Option | Description string |
|---|---|
| `Ask for approval` | `Always ask to edit external files and use the internet` |
| `Approve for me` | `Only ask for actions detected as potentially unsafe` (settings calls it Auto-review) |
| `Full access` | `Unrestricted access to the internet and any file on your computer` |
| `Custom (config.toml)` | `Uses permissions defined in config.toml` |
| `Managed` | `Managed by enterprise policy` |

- Disabled states name the file responsible: `Disabled in config.toml`, `Disabled by requirements.toml`, `Requires default sandboxed permissions in this workspace`.
- **Full access confirm** (`Turn on Full Access?`) splits the risk into three rows:
  - `Files and folders` — `Read, create, modify, upload, or delete files anywhere on this computer`
  - `Terminal commands`
  - `Internet and connected apps`

  It also warns about `prompt injection`. A separate dialog covers `Use Ultra with Full access?`.
- **Auto-review in the thread.** Row titles: `Auto-reviewing` → `Auto-review approved` / `denied` / `denied high risk` / `timed out` / `stopped`. Body: `A carefully prompted reviewer agent is reviewing this request before ChatGPT runs it`.
- After repeated prompts a nudge appears: `Want fewer approval prompts?` — `Approve for me` / `Keep manual approvals`. Messages carry `Auto-review stats ({count} rejected)`, and a refused patch shows `File change declined by auto-review: {file}`.
- **Effort ladder:** `None · Minimal · Light · Medium · High · Extra High · Max · Ultra · Persistent`. Work mode uses `Standard / Extended` and a `Power` slider. Changing model shows the toast `Changing models mid-conversation will degrade performance`.
- **Native (B)** has a different ladder for connectors: `Allow read actions` → `Allow low-risk actions` (`may deny actions involving sensitive information`) → `Allow all actions` (`won't ask before reading or taking action. This comes with elevated risk.`). Browser use has `Approve for me`.

> 📌 The docs state the design split: "The sandbox defines which files and network resources ChatGPT can access. Approvals
> determine when ChatGPT pauses… **Changing who reviews a request doesn't expand the sandbox.**" (§4). The mode picker changes
> *the reviewer*; `Full access` is the only option that changes *the boundary*, and it is the only one with a dedicated confirm.
> Compare gate properties in [../strands/07-security.md](../strands/07-security.md) and
> [../ai-workflow/wiki/concepts/approval-gate.md](../ai-workflow/wiki/concepts/approval-gate.md).

### 3.3 Plan / todos

- Entering plan mode: composer indicator `Plan`, `/plan`, `Toggle plan mode`, placeholder `Describe your task to generate a plan...`.
- The plan renders as `Writing plan` → a collapsible **Plan** card with `Open plan in side panel` and `Download plan`.
- Progress shows as a pill `Step {stepNumber} / {stepCount}`. Native uses `{n} of {m} tasks completed`.
- The hand-off CTA is `Yes, implement this plan`, backed by `item/plan/requestImplementation` (§1.2.1).
- **Thread goal** (`thread/goal/*`) is a composer chip: `Pursuing goal` / `Goal achieved` / `Goal stalled` / `Paused goal` / `Goal limited`, with a token budget `{used} / {budget}` and `ChatGPT will keep working toward this goal when the chat is idle`.

### 3.4 Tool-call transcript

Items collapse per turn into a **past-tense sentence**, not JSON:
- summaries: `Worked`, `Ran commands`, `Edited files`, `Read files`, `Searched the web`, `Used {sources} integrations`, `{toolName} · {count} calls`;
- about 900 hand-written **active/completed verb pairs** per MCP tool (`localConversation.mcpToolActivity.*`), e.g. `Running JavaScript` → `Ran JavaScript`, `Searched Linear for {target}`;
- a WebMCP detail view with `Input` / `Result (truncated)`.

The native voice client says `Running a command`, `Changing files`, `Using an app`, `Show work: {…}`.

### 3.5 Diff / review

- Per-file rows move through `Editing` → `Edited`, `Creating` → `Created`, `Rejected`, `Stopped editing`. Summaries: `{n} files changed`, `Review changed files`.
- **Undo / Reapply** are git-apply based and report `Applied cleanly ({count})` / `Conflicts ({count})` / `Skipped ({count})`.
- View options: `Switch to split diff` / `unified`, plus `Auto: split for additions and removals, unified for one-sided changes`.
- Inline diff comments carry `L` / `R` side markers.
- Diff markers can be `Color` or `+/-`. The Pierre themes include **`pierre-dark-protanopia-deuteranopia` and `pierre-dark-tritanopia`** ✅.
- PR actions: `Create pull request`, and `Repair` with `Failing checks` / `Comments` / `Merge conflicts` / `Everything`.

### 3.6 Parallel and background work

- Panels: `Subagents` and `Background processes`.
- Agent states: `pending init · running · completed · errored · interrupted · shutdown`. Headers `Creating` / `Created {n} agents`; rows `Created {agent} with the instructions: {instructions}`, `Messaged {agent}: {prompt}`.
- `Stop all background terminals`.
- Execution location: `New worktree` (`Create a copy of {repoName} to work in parallel.`).
- **Hand off chat to worktree** is a modal with a visible step list: `Stashing uncommitted changes` → `Creating a new worktree` → `Applying uncommitted changes to worktree` (with `Rolling back changes` on failure). Inline it reads `Handing off to {destination}` / `Handed off to {destination}`.

### 3.7 Status and attention

| Channel | Vocabulary |
|---|---|
| Thread / agent-key status | `Awaiting approval · Awaiting response · Working · Unread · Error · Idle · Off` |
| **Codex Micro** LED legend (Work Louder `kbd-1.0-codex-micro`, `@worklouder/device-kit-oai`) | `Blue – Thinking`, `Amber – Requires input`, `Green – Complete`, `Red – Error`, `White – Idle`, `Off – No Assigned Agent` |
| OS notifications | `Permission approval`, `ChatGPT finished a turn`; sounds `codex-notification.wav`, `codex-classic.wav` |
| Pets | floating animated companions (`Dewey — A tiny blue-screen gremlin.`, `The original Codex companion.`), `Send to Pet` |
| Power | `Prevent sleep while running` |

> 📌 A single status vocabulary, with *amber = needs a human*, drives the sidebar, the hardware LEDs and the Pets. Attention is
> designed to live **outside the window**.

### 3.8 Steering and queueing

- The submit button morphs between `Send · Queue · Steer · Stop · Resume`.
- Queued follow-ups form a list with `Steer — Submit without interrupting the model`, `Edit message`, `Open in side chat`, and `Queue paused because you interrupted`.
- Setting: `Follow-up behavior: Queue | Steer`. These map to `turn/steer` and `turn/interrupt` ✅.

### 3.9 Errors

- Send-blocking conditions are spelled out as remedies: `Set up Agent sandbox to continue`, `Restore the worktree to continue`, `Remote connection needs authentication`, `Select a cloud environment to continue`.
- Queued-message failures: `Delivery could not be confirmed. Check the conversation before deleting this saved message`.
- Auto-review loop: `Auto-review stopped this turn after repeated denials…`.
- Native: `Codex app server is not running.`, `Remote app-server version {v} is older than the required version {w}.`

### 3.10 One UI, two voices

📣 In ChatGPT Work the app will "Hide technical details like Git or shell commands" and "Prefers nontechnical language and finished outputs".
In Codex it will "See developer details, including diff and review views" ([use-chatgpt.md](https://learn.chatgpt.com/docs/use-chatgpt.md)).
✅ The strings carry the split: `…warningDescription.chatgptMode` (`ChatGPT will be able to…`) vs `.codeMode` (`Codex will be able to…`),
and `{actor}`-parameterised prompts. **The same primitive gets a different persona per product mode.**

## 4. Stated design philosophy (📣)

- "Your command center for complex work. Run projects in parallel, work with files, use your computer, and keep long-running work moving from one desktop workspace." — https://learn.chatgpt.com/docs/app.md
- "Two controls work together: The **sandbox** defines which files and network resources ChatGPT can access. **Approvals** determine when ChatGPT pauses before an action or sends the request to automatic review. Changing who reviews a request doesn't expand the sandbox." — https://learn.chatgpt.com/docs/permission-modes.md
- "For most work, start with **Ask for approval**." — same page
- "Auto-review replaces manual approval at the sandbox boundary with a separate reviewer agent." — https://learn.chatgpt.com/docs/sandboxing/auto-review.md
- "Pets are optional animated companions for following work… Choosing a pet changes its appearance, not how ChatGPT completes tasks." — https://learn.chatgpt.com/docs/pets.md
- "The most interesting opportunity is not to reproduce the Codex app with a different logo, but to build software that reflects how a specific person or team already works… A team can keep its existing dashboards, editors, queues, maps, records, and approval flows instead of forcing every interaction into a generic chat window." — https://developers.openai.com/blog/codex-as-a-platform.md

## 5. What is distinctive

1. **Tokens named after VS Code theme keys.** One webview, four hosts, and editor-theme inheritance at no cost ✅.
2. **Progressive squircles.** A web app imitates Apple's continuous corners only where `corner-shape` exists ✅.
3. **Reviewer vs boundary as separate controls.** `Approve for me` swaps the reviewer, `Full access` moves the boundary, and only the latter gets a three-row risk dialog ✅/📣.
4. **The approval card has a scope ladder** (once → conversation → prefix → always) and the mode lives in the composer. Aside by contrast offers only `Allow once` ([../browser-agents/03-aside-design-ux.md](../browser-agents/03-aside-design-ux.md)).
5. **Hand-written verb phrases per tool.** About 900 of them turn a transcript into prose ✅.
6. **Attention outside the window.** A hardware LED legend and floating Pets share the in-app status vocabulary ✅.
7. **Accessibility in diffs.** Colour-blind diff themes and a non-colour `+/-` marker option ✅.
8. **Words converge, pixels diverge.** `Approve for me`, `A carefully prompted reviewer agent…`, `Always allow` and `Reason` appear in *both* the React and the SwiftUI string tables. That points to a shared product/string spec, not a shared component library ✅.

## 6. Refutations and contradictions

| Claim | Artifact | Grade |
|---|---|---|
| Study premise: "ChatGPT desktop (macOS) is native SwiftUI, distinct from Codex desktop" | The official ChatGPT download for macOS/Windows/Linux is the Codex Electron/OWL build (§1.1). SwiftUI survives only as legacy 1.2026.183, which ships an upgrade screen to the new app | ❌ (premise, not vendor claim) |
| "Codex app-server is the interface Codex uses to power rich clients" (📣 `app-server.md`) implies the public doc covers what rich clients use | The shipped client drives a **second, cloud-hosted engine** (`durable`, `wss://codex-cloud-backend.chatgpt.com/`) with its own dialect — `thread/startAeon`, `turn/addUserMessage`, `thread/stop` (§1.2.1) | ❌ refuted 2026-09-27: the open-source App Server is one of two engines the client targets |
| Tool shell presented as "Electron" | Electron API only; the runtime is OWL on a full Chromium 154 | ✅ correction |

## 7. What this means if you are building an agent client

- [ ] Pick a semantic token vocabulary that **a host already defines** (VS Code theme keys). Your panel then themes itself inside any editor.
- [ ] Put the **mode** (who reviews) in the composer and the **decision** (this call) in the thread. Never let a reviewer change widen the sandbox.
- [ ] Give the approval card a **scope ladder** mapped onto protocol decisions (`accept` / `acceptForSession` / amendment), and a free-text decline (`Tell Codex what to do`).
- [ ] Give boundary-widening modes a dedicated confirm that splits risk by capability (files / terminal / internet).
- [ ] Bucket pending server requests **by turn**, and show an `Awaiting approval` state in every list that shows the thread (sidebar, notifications, devices).
- [ ] Write **active/completed verb pairs** per tool; roll a turn up into one sentence; keep raw input/output one click away.
- [ ] Make send-blocking errors state their **remedy** (`…to continue`).
- [ ] Offer non-colour diff markers and colour-blind diff themes.
- [ ] Expect undocumented protocol methods in first-party clients. Pin your App Server version and handle unknown server requests by failing visibly, not stalling ([../docs/02-app-server-protocol.md](../docs/02-app-server-protocol.md)).

## 8. Open questions

- ⚠️ **Everything visual**: approval card weight, density in practice, icon usage, whether squircles are active in the shipped Chromium 154.
- ⚠️ Mapping of `Always allow` and the prefix rule onto App Server amendment decisions. This needs a live run with protocol tracing.
- ⚠️ What the durable (Aeon) engine is, and its behaviour — not provisioned for the account used, so unobserved (§1.2.1).
- ⚠️ How much of the component layer is Radix and how much is in-house.
- ⚠️ Native (B) colour tokens need `assetutil`/`acextract` on macOS. Which `codex_remote_*` strings render on macOS versus only on iOS.
- ⚠️ Whether the pre-superapp Windows ChatGPT (Store) build still exists and what it was built with. Not checked.
- ⚠️ Whether OWL is the Atlas browser runtime.
