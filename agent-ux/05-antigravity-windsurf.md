# 05. Google Antigravity and Windsurf (now Devin Desktop) — one ancestor, two opposite answers

> Products: **Google Antigravity** in three shipped forms, all obtained 2026-09-26 as official Linux x64 tarballs:
> - **Antigravity 1.23.2**: the IDE plus Agent Manager; VS Code 1.107.0, commit `15487b30`, built 2026-04-16. From
>   `edgedl.me.gvt1.com/…/antigravity/stable/1.23.2-4781536860569600/linux-x64/Antigravity.tar.gz`, the only
>   build linked from `antigravity.google/download/linux`.
> - **Antigravity IDE 2.5.5**: VS Code 1.107.0, commit `ecfbad74`, built 2026-08-13. From
>   `…/stable/2.5.5-4923483625488384/linux-x64/Antigravity%20IDE.tar.gz`.
> - **Antigravity 2.17.0**: the standalone agent app, built 2026-09-22. From
>   `storage.googleapis.com/antigravity-public/antigravity-hub/2.17.0-5217732355031040/linux-x64/Antigravity.tar.gz`.
>
> **Windsurf (now Devin Desktop)**: `windsurfVersion` 3.10.35, VS Code 1.126.0, `codeiumVersion` 1.48.2, commit
> `dfa4a2d6`, built 2026-09-23. The updater endpoint `windsurf-stable.codeium.com/api/update/linux-x64/stable/latest`
> returns `Devin-linux-x64-3.10.35.tar.gz` (sha256 `fd50eb54…6ec6`).
>
> Method: static extraction from the shipped bundles, CSS, and the CSS source maps' `sourcesContent`. The
> Antigravity 2.x web UI was carved out of a zip embedded in its Go `language_server` binary. There was no
> display, so **nothing was seen rendered** and anything visual is ⚠️. Docs were read from
> `antigravity.google/docs/*.md`, `docs.windsurf.com/*.md` (now served from docs.devin.ai), the Antigravity
> changelog and four launch posts. Researched 2026-09-26.
>
> Dominant grade: ✅ (enums, tokens and strings from bundles); 📣 for philosophy; one ❌ and two doc
> inconsistencies (§7).

## 1. What they are and how they are built

### 1.1 Build inventory

| Build | Shell | Where the agent UI lives | Grade |
|---|---|---|---|
| Antigravity 1.23.2 | Electron, VS Code fork | Side panel: React inside `out/vs/workbench/workbench.desktop.main.js`, mounted from `extensions/antigravity/cascade-panel.html` (`<div id="react-app" class="react-app-container">`). **Agent Manager**: a separate window, `out/jetskiAgent/main.js` + `main.css` | ✅ |
| Antigravity IDE 2.5.5 | same | Same structure; `jetskiAgent` still ships. The vendor says it will later be removed "turning the IDE into a purely agent-powered IDE" 📣 | ✅ |
| Antigravity 2.17.0 | **Not a VS Code fork.** `resources/app.asar` (4.6 MB: tray, updater, WSL, host bridge) calls `win.loadURL("https://127.0.0.1:PORT/")`. The UI is a zip embedded in `resources/bin/language_server` (Go): `index.html` titled **`Jetski Web`**, `main.js` 9.5 MB, `compiled_tailwind.css`, `jetbox.css`, `antigravityActionRequired.mp3`, `antigravityCascadeDone.mp3` | Web app served locally by the agent server | ✅ |
| Windsurf (now Devin Desktop) 3.10.35 | Electron, VS Code fork; `product.json` has `nameLong:"Devin"`, `applicationName:"devin-desktop"`, `oldNameShort:"Windsurf"`, `oldDataFolderName:".windsurf"` | Chat: `out/vs/workbench/windsurf-chat-client/index.js` (25 MB, identical to `node_modules/@exa/chat-client`). **Agent Command Center**: the VS Code `vs/sessions` window (`out/vs/sessions/sessions.desktop.main.js`, 44 MB, `KanbanSessionCard`). Also bundles the `devin` CLI binary (`extensions/windsurf/devin/bin/devin`) and `@exa/windsurf-acp` | ✅ |

Component stacks ✅:
- **Antigravity 1.x / IDE**: React, Tailwind v3, Lexical, codicons, a few lucide icons; Base UI traces appear in IDE 2.5.5.
- **Antigravity 2.17.0**: React, **Tailwind v4.2.2**, **Base UI** (`--popup-width`, `--transform-origin`,
  `--drawer-swipe-*`, `data-base-ui-*`), Lexical, **Material Symbols** (`name:"more_vert"`, `"progress_activity"`,
  `"smart_toy"`), prism, pdf.js, and google3 paths (`third_party/javascript/react_tooltip`, `webutil/sass`).
- **Windsurf (now Devin Desktop)**: React, Tailwind, Radix and Headless UI (the legacy `@exa/design-system`)
  moving to **Base UI** (a comment reads "The new #/ds/tooltip (base-ui)"), the **Central Icon System**
  (`maskId:"round-outlined-radius-2-stroke-1.5-IconCentralIconSystem"`; 1,751 `Icon*` components), and i18next.
  `node_modules` also carry `@anthropic-ai/sandbox-runtime`, `@github/copilot-sdk` and `playwright-core`; whether
  these come from upstream VS Code 1.126 is ⚠️.

### 1.2 Where the agent lives: same premise, opposite layouts

| | Antigravity | Windsurf (now Devin Desktop) |
|---|---|---|
| 2025 form | Two windows: the Editor with an agent side panel **on the right**, and the **Agent Manager** (Inbox, Workspaces, Playground, Knowledge). The strings `Open Agent Manager` / `Open Editor` handle the handoff ✅ | The Cascade panel on the right (`Cmd/Ctrl+L`) 📣 |
| 2026 form | **Antigravity 2.0: "there is no IDE."** Layout: a sidebar (Projects, Conversations, Documents, Artifacts, Scheduled), the conversation, and a side pane (artifacts, files, terminal, VCS review, browser preview, subagent conversations) ✅ strings, 📣 docs | **"a full IDE with an agent manager built in — not the other way around."** The Agent Command Center, a Kanban of local and cloud sessions, is the default surface. **Spaces** group sessions, PRs, files and context (`Cmd/Ctrl+\` split, `Cmd/Ctrl+T`) 📣 |

> **GUI pass 2026-09-27 (macOS, same build, `orca computer` screenshots; passive — no agent was run), Antigravity 2.17.0.** ✅ The standalone app opens on an agent home: sidebar `New Conversation`,
> `Conversation History`, `Scheduled Tasks`, then `Projects` with conversations nested under each; a centred composer
> (`Ask anything, @ to mention, / for actions`, model + effort, execution target `Local`). `Documents` and `Artifacts`
> were **not** sidebar entries on that screen ⚠️ (they may live in the side pane). An **`Open IDE`** button hands off to the
> separately installed Antigravity IDE — "there is no IDE" means the IDE left *this* window, not the product. An
> onboarding card read `Planning mode has moved to /plan`, confirming the 2.17 change in §4. Unread conversations carry a
> **blue** dot.

> 📌 Both started from the same premise: one window is too cramped to hold synchronous editing and
> asynchronous fleet management together. **Google removed the IDE; Cognition kept the IDE and made the manager
> its home screen.** The two launch quotes (§5) mirror each other almost word for word.

## 2. Lineage: what the two products still share, and where they split

Antigravity was built by the team that came from Windsurf. The shipped artifacts show this at every layer,
from wire enums to CSS breakpoints. The table lists each piece of evidence.

### 2.1 Evidence table

| Layer | Antigravity evidence | Windsurf (now Devin Desktop) evidence | Grade |
|---|---|---|---|
| **Agent-step protocol ("Cortex")** | `CortexStepType` in `main.js` (Antigravity 2.17.0 web zip): 118 values | `CORTEX_STEP_TYPE_*` in `windsurf-chat-client/index.js` (3.10.35): 87 values | ✅ |
| — shared names | **45** names in common | | ✅ |
| — shared field numbers | **43 of the 45 carry identical protobuf numbers**. Only `EDIT_NOTEBOOK` (126 vs 83) and `READ_NOTEBOOK` (129 vs 82) differ | | ✅ |
| Run state | `CascadeRunStatus{UNSPECIFIED,IDLE,RUNNING,CANCELING,BUSY}` | `CASCADE_RUN_STATUS_{UNSPECIFIED,IDLE,RUNNING,CANCELING,BUSY}` — identical | ✅ |
| Command auto-execution | `CascadeCommandsAutoExecution{OFF,AUTO,EAGER,PROCEED_IN_SANDBOX}` | `CASCADE_COMMANDS_AUTO_EXECUTION_{OFF,AUTO,EAGER,DISABLED}`. The shared core is OFF/AUTO/EAGER; `EAGER` is "Turbo" in both UIs | ✅ |
| Internal agent name | Antigravity never shows the word "Cascade", but its code does: `cascadeId` ×996, `handleCascadeUserInteraction`, `CascadeNUXTrigger`, the sound file `antigravityCascadeDone.mp3`; `CascadeManager` ×254 and `exa.language_server_pb.LanguageServerService` ×317 in the 2.17.0 Go binary | "Cascade" is the product name of the legacy agent | ✅ |
| Onboarding (NUX) enum | `CASCADE_NUX_*`, 50 values | `CASCADE_NUX_*`, 30 values; shared values include `…_EVENT_PLAN_MODE`, `…_EVENT_REVERT_STEP`, `…_EVENT_WEB_SEARCH`, `…_EVENT_WRITE_CHAT_MODE`, `…_EVENT_ANTHROPIC_API_PRICING` | ✅ |
| Proto namespace | `exa.cortex_pb.WorkflowSpec` survives as a string in the 2.17.0 bundle | `exa.cortex_pb.*` ×730, `exa.codeium_common_pb.*` ×1,380 | ✅ |
| RPC header | `x-codeium-csrf-token` set on every language-server call (2.17.0 `main.js`) | — | ✅ |
| Extension shape | `extensions/antigravity/`: `cascade-panel.html`, `customEditor/`, `schemas/mcp_config.schema.json`, `bin/language_server_linux_x64`, plus siblings `antigravity-{dev-containers,remote-openssh,remote-wsl}` | `extensions/windsurf/`: `customEditor/`, `schemas/mcp_config.schema.json`, `bin/language_server_linux_x64`, plus siblings `windsurf-{dev-containers,remote-openssh,remote-wsl}` | ✅ |
| Design-system source | `extensions/antigravity/tailwind.config.js` (1.23.2, 2.5.5): `content: ['../exa/design_system/src/**', '../exa/agent_ui_toolkit/src/**']`; the bundle contains `exa/agent-ui-toolkit/dist/index.js`. `exa` = Exafunction, Codeium's parent | npm package `@exa/chat-client`; CSS comment "Legacy **@exa/design-system** Tooltip → VS Code hover style" | ✅ |
| Palette | The same config defines brand-dark **`#09b6a2`** (Codeium teal), brand-light `#71E9D8`, red `#cb3d3d`/`#de5555`, orange `#e8975f`/`#e0712f`, gold `#cab43e`, green `#7aae66`/`#63984f`, blue `#6a9fcb`/`#4380b4`, violet `#bb84cc`. **Antigravity 2.17.0's Tailwind v4 theme still overrides Tailwind defaults with it** (`--color-red-500:#de5555; --color-blue-500:#4380b4; --color-green-500:#63984f; --color-gold:#cab43e`) | Residue: `.bg-brand-dark*` and `.text-brand-light` classes, and an `AnimatedButton` gradient `linear-gradient(-60deg, #09b6a2, #6bf8e7, #09b6a2)` | ✅ |
| CSS variable bridge | Tailwind colours `ide-* → var(--codeium-*)` (`ide-chat-background → var(--codeium-chat-background)` and 40+ more) | 67 `--codeium-*` variables in `base.css` (e.g. `--codeium-planning-mode-foreground`) | ✅ |
| Container breakpoints | `screens: {'ws-xs':'16rem','ws-sm':'22rem','ws-md':'30rem'}` | Compiled CSS emits the same `.ws-xs\:flex`, `.ws-sm\:inline` utilities. **`ws` = Windsurf** ⚠️ (naming inference) | ✅ / ⚠️ |
| Shared feature strings | `Explain and Fix`, `Accept all`, `Reject all`, `Allow Once`, `Turbo`, `Knowledge`, `Memories`, `Checkpoint`, `Worktree` appear in both products' bundles | | ✅ |

### 2.2 Where they split

The step types unique to each product show the direction of each fork ✅:

| Antigravity only (73) | Windsurf (now Devin Desktop) only (42) |
|---|---|
| 25+ browser actuation types (`BROWSER_CLICK_ELEMENT`, `BROWSER_DRAG_PIXEL_TO_PIXEL`, `CAPTURE_BROWSER_SCREENSHOT`, `BROWSER_SUBAGENT`…) | `TODO_LIST`, `EXIT_PLAN_MODE`, `ASK_USER_QUESTION` |
| `TASK_BOUNDARY`, `NOTIFY_USER`, `INVOKE_SUBAGENT`, `ASK_QUESTION` | `ARENA_TRAJECTORY_CONVERGE`, `UPSERT_CODEMAP`, `SUGGEST_CODEMAP` |
| `KNOWLEDGE_GENERATION`, `KNOWLEDGE_ARTIFACTS`, `KI_INSERTION` | `DEPLOY_WEB_APP`, `CHECK_DEPLOY_STATUS` |
| Google-internal: `BLAZE_BUILD_TARGETS`, `CIDER_AGENT_DUMMY`, `MOMA`, `DEPLOY_FIREBASE`, `CLOUD_SQL_*` | `SMART_FRIEND`, `TASK_SUBAGENT`, `SKILL`, `LIST_MEMORIES` |

The visual system split along the same line:

| Axis | Antigravity | Windsurf (now Devin Desktop) |
|---|---|---|
| Successor to `@exa/design_system` | 1.x: Tailwind classes bound straight to `--vscode-*`. 2.0: **shadcn-style semantic tokens + Base UI + Material Symbols** | **`@cognitionai/ds`**, Cognition's Figma-exported design system shared with the Devin web app + Base UI + Central Icons |
| Chat client | Owns its own "Jetski" UI | **Embeds the Devin web app's chat client**: its English i18n bundle has 12,328 keys, including the web app's `automations`, `codeScan`, `billing` and `oncall` |
| Agent engine | Same Go `language_server` lineage, protocol extended | Moving to **Devin Local** (Rust, shared with the Devin CLI, attached over ACP). The shipped settings say: `Devin Local is replacing Cascade. These settings apply primarily to the legacy Cascade agent.` |

> 📌 **Rewrites run from the outside in.** Both teams replaced the skin first (tokens, icons, fonts), then the
> vocabulary (Artifacts vs. Todo list and plan file). The data model (the Cortex step numbers) went almost untouched.
> Antigravity kept the engine and widened its vocabulary. Windsurf is swapping out the whole engine, and when
> Cascade goes, the lineage in Windsurf will survive only as residue (palette, `ws-*` breakpoints, `--codeium-*`) ⚠️.

## 3. Design system

### 3.1 Antigravity 2.17.0 — three seeds, everything derived

| Role | Value (`compiled_tailwind.css` `@layer theme`; theme code in `main.js`) | Grade |
|---|---|---|
| Semantic tokens | `--background --foreground --card --card-border --muted --muted-foreground --primary --primary-foreground --secondary --secondary-foreground --sidebar --sidebar-secondary --sidebar-muted --placeholder --border --warning --link --error --success`, editor diff tokens, `--chart-{red,orange,…}` | ✅ |
| Derivation | Each preset supplies only **three seeds** (background, foreground, primary). The rest is computed with `color-mix`: `--muted = color-mix(in srgb, fg m%, bg)`, `--card = color-mix(fg cardDarkPct, bg)` in dark / `color-mix(bg 70%, #ffffff)` in light, `--border = rgba(255,255,255,α)` / `rgba(0,0,0,α)` | ✅ |
| Legacy bridge | The seeds are then **reverse-mapped onto VS Code variables** for embedded legacy components: `"--vscode-button-background":"--primary"`, `"--vscode-editorWidget-background":"--card"`, and so on, behind the flag `vscodeInjectionRemoval` | ✅ |
| Presets | Light: `Default Light` (`#F9F9F9` / `#101010` / `#007acc`), `Catppuccin`, `One Light`, `Solarized Light`. Dark: `Default Dark` (`#101010` / `#cccccc` / `#007acc`), `Catppuccin`, `Dracula`, `Monokai`, `One Dark Pro`, `Tokyo Night`, `Solarized Dark`, `Vesper` (`#101010` / `#FFFFFF` / `#FFC799`). Syntax colours come from `--syntax-*` variables (`jetbox.css`) | ✅ |
| Typography | `--font-sans: var(--vscode-font-family, system-ui, -apple-system, …)`; `--font-mono: var(--editor-font-family, ui-monospace, …)`. The root is pinned at 16px and iframes default to `--font-size:13px`. No bundled fonts; Material Symbols load from Google Fonts | ✅ |
| Radii | xs .125 / sm .25 / md .375 / lg .5 / xl .75 / 2xl 1rem | ✅ |
| Spacing | `--spacing: 0.25rem` | ✅ |
| Motion | `--default-transition-duration:150ms`, `cubic-bezier(.4,0,.2,1)`; `--animate-fade-in: .2s`; **`--animate-unread-ping: unread-ping 4s cubic-bezier(.22,1,.36,1) infinite`** | ✅ |
| Icons | Material Symbols (outlined) for UI; the "Symbols" file-icon theme (`symbols-icons/`, 286 SVGs) | ✅ |

**Antigravity 1.x / IDE 2.5.5.** `out/jetskiAgent/main.css` binds 103 semantic Tailwind classes straight to VS Code
variables, e.g. `.bg-ide-chat-background{background-color:var(--vscode-sideBar-background)}`. The extension config
sets a 13px-based type scale (`base: '0.813rem'`, `sm: '0.75rem'`, `xs: '0.688rem'`) and mono
`SF Mono, Monaco, Menlo`. IDE 2.5.5 adds `card` / `card-border` tokens: the 2.0 vocabulary flowing back into the IDE ✅.

### 3.2 Windsurf (now Devin Desktop) — Figma tokens derived from the editor theme

Recovered verbatim from the css-loader source map inside `windsurf-chat-client/index.js`: `ds/src/design-tokens.css`,
`high-contrast-tokens.css`, `motion.css`, `src/styles/base.css`, `src/styles/windsurf.css` ✅.

| Role | Light | Dark |
|---|---|---|
| `--bg-page` / `--bg-wash` / `--bg-elevated` | `252 252 252` / `248 248 248` / `255 255 255` | `20 20 20` / `25 25 25` / `31 31 31` |
| `--text-primary` / `-secondary` / `-tertiary` | `25 25 25` / `…/0.56` / `…/0.4` | `255 255 255/0.9` / `…/0.52` / `…/0.4` |
| `--bg-accent-primary` | `49 124 255` | `68 137 255` |
| Status (`--text-red/green/orange/purple`) | `245 59 58` / `0 165 88` / `245 142 58` / `149 108 222` | red, orange, purple same; green `0 236 126` |
| Shadows | `--shadow-L1…L4`, `-L2-border`, `-L4-wax` | same scale, heavier alphas |
| **Mode tints** | `--codeium-planning-mode-*` = **orange** (`rgb(var(--tint-orange))`); `--codeium-ask-mode-*` = **green** | same |

- The file's own header: "This file contains design tokens exported from Figma. It is the single source for both design
  system consumers … webapp … chat client (Windsurf + JetBrains)." Tokens are RGB triplets, so utilities apply alpha;
  `.theme-inverse` flips light and dark for one subtree ✅.
- At runtime, **`designTokenCss.ts` derives the DS tokens from the active VS Code theme**. Examples:
  `{kind:"direct",token:"--bg-page",from:"editor.background"}`,
  `{kind:"blended",token:"--text-secondary",from:"foreground",alphaLight:.56,alphaDark:.52}`, and
  `--bg-accent-primary` from `button.background` with a `contrastGuard` that falls back to `focusBorder`
  (`out/vs/workbench/workbench.desktop.main.js`, 23 mapped tokens) ✅.
- Typography: `SF Pro`, `SF Pro Text`, `SF Pro Display` stacks with mono `Menlo`; not bundled ✅. Radii are mostly
  6px, 9999px and 0.25rem. Motion is 150ms (×40), 200ms and 700ms.
- **Reduced motion:** `motion.css` collapses animations to 0.01ms under `prefers-reduced-motion`, with an opt-out class
  `motion-essential` for "motion that carries information the user would otherwise lose" ✅.
- The legacy panel background is `--panel-bg-base: color-mix(in srgb, var(--codeium-editor-background) 50%,
  var(--codeium-chat-background))`, halfway between the editor and chat colours ✅.

> 📌 **Two answers to "carry an app skin across twenty editor themes".** Antigravity 2.0 made the theme tiny
> (three seeds) and derives everything from it. Windsurf keeps a rich Figma token set and translates each
> editor theme into it, with a contrast guard.

## 4. How harness primitives are rendered

### 4.1 Approval and permission

Both products now use the same rule grammar, **Deny > Ask > Allow** (Antigravity `docs/permissions`; Devin Local
docs) 📣. It matches the scope ladder in [SYNTHESIS §2.1](../SYNTHESIS.md) and the Codex vocabulary in
[02-app-server-protocol](../docs/02-app-server-protocol.md).

| | Antigravity 2.17.0 ✅ | Windsurf (now Devin Desktop): Devin Local ✅ | Windsurf: legacy Cascade |
|---|---|---|---|
| Buttons | `Allow Once` · `Always Allow` · `Deny`; `Approve this action`; `Run (unsandboxed)`; `Grant one-time administrator access` | ACP option kinds `allow_once` · `allow_always` · `reject_once` · `reject_always`; i18n `Allow for this session`, `Approve`, `Reject`, `Use edited command`, `Deny` | `Run▾` dropdown with Allowlist → `Prefix` / `Allow`, `Deny`; `Auto-run settings` ✅ strings, 📣 docs |
| Card title | `Requesting your permission in Terminal:`; `Agent needs permission to execute JavaScript` | `Devin is requesting to perform the following actions` | — |
| Scope editing | `Edit permission target`. 📣 "you can directly edit the target string in the prompt card to expand the granted scope" | `Edit command`, `Describe change to command`; 📣 "has a fast model rewrite the command for you to review" | prefix vs. exact allowlist entry |
| Presets | `Default` (auto inside the sandbox, ask outside it) / `Request Review` / `Turbo`. Windows: `Request Review` / `Proceed in Sandbox` / `Always Proceed` | permission modes shared with Devin CLI | `Disabled` / `Allowlist Only` / `Auto` / `Turbo` 📣 |
| Full autonomy | Banner: `Autonomous mode active: the agent works independently and does not ask questions or request new permissions.` (icon `smart_toy`) | — | — |

> 📌 **The approval card is a scope editor.** In both products you can widen or rewrite the target (command,
> path, URL) *before* approving. The grant then becomes exactly what the user edited, not a take-it-or-leave-it
> of what the model proposed. See the gate properties in [strands/07](../strands/07-security.md) and the
> [approval-gate concept](../ai-workflow/wiki/concepts/approval-gate.md).

### 4.2 Autonomy modes

| Axis | Antigravity | Windsurf (now Devin Desktop) |
|---|---|---|
| Task mode | 1.x–2.16: `Planning` / `Fast`. From 2.17: `/plan` plus a **Plan Review Policy** (review always / when the agent judges it worthwhile / never) 📣. Slash commands `/goal`, `/grill-me`, `/boost`, `/teamwork-preview`, `/browser` 📣 | Cascade: `Code` / `Plan` / `Ask` (`⌘+.`); Devin Local: Normal / Plan / Ask 📣 |
| Review policy | **Artifact Review Policy**: `Request Review` / `Always Proceed` ✅ | — |
| Model and effort | Per-model thinking level Low / Medium / High (changelog 2.5.2) 📣 | `Choose a model, thinking effort, and priority` ✅; the Adaptive router and Arena mode 📣 |
| Shared word | **`Turbo`** = enum `EAGER` in both (§2.1) | |

### 4.3 Plans and todos

- **Antigravity: the plan is an artifact.** The Implementation Plan opens in the review pane with inline comments
  (`Add inline comment`, `Select text in the artifact to add a comment`, `Drag to select a region to comment`), then
  `Proceed` / `Proceed with Plan`. Transcript footers read `Auto-proceeded with` / `Proceeded with` ✅. Other artifact
  types are Task, Walkthrough, Screenshot, and browser recordings (webm) 📣.
- **Windsurf: the plan is a todo list plus a file.** `CORTEX_TODO_LIST_ITEM_STATUS_{PENDING,IN_PROGRESS,COMPLETED}`
  with priority LOW / MEDIUM / HIGH ✅. 📣 "a specialized planning agent continuously refines the long-term plan". Plan
  mode writes `~/.devin/plans/plan-<session>.md` and offers an `Implement` button 📣.
- **Keyword mode switch.** Typing `megaplan`, `ultraplan` or `masterplan` anywhere switches the session into Plan mode 📣.
  The CSS then draws an **orange SVG "snake" around the input border** and tints the keyword
  (`.animate-megaplan-border .megaplan-snake-svg rect{animation: megaplan-snake 0.3s linear forwards}`,
  `.megaplan-highlight{color:var(--codeium-planning-mode-foreground)}`) ✅.

### 4.4 Tool-call transcript

- Both products use the **trajectory → step** model (§2.1). Antigravity groups steps under `TASK_BOUNDARY` tasks:
  📣 "the user sees tool calls grouped within tasks, monitoring high level summaries and progress along that task".
- Windsurf renders a Devin-style worklog: 184 `progress.*` keys such as `Clicked at ({{x}}, {{y}})`,
  `Executed JavaScript`, `{{count}} earlier actions`, `Created plan` ✅.
- **Activity verbs** (Windsurf, `windsurf-chat-client/index.js`) ✅: `Deciding action`, `Waiting for shell`,
  `Executing actions`, `Creating a plan`, `Waiting for CI checks`, `Summarizing context`,
  `Waiting for other sessions`, `Waiting for approval`, and the default **`Cooking`**.
- Antigravity has `Working`, `Generating`, `Thought for`, `Worked for` ✅. 2.16 added tool-initialisation progress
  and a retry countdown to the loading indicator 📣.
- **Rewind.** Antigravity: `Undo To Here`, `Undo restores your entire workspace to its state at this point.`, and
  **`Revert and redo turn, best of N:`** (a checkbox plus an N selector) ✅. Windsurf: a revert arrow on each prompt
  and named checkpoints, with the warning 📣 "Reverts are currently irreversible".

### 4.5 Diff and review

- **Antigravity** ✅: `Review Changes` (the bottom toolbar opens a full-pane diff), `Accept Step` / `Reject Step`,
  `Accept all` / `Reject all`, `File Diff Comments`, `Auto-Expand Changes Overview`. 2.0 adds a VCS panel with
  Uncommitted, Branch and **Agent edits** diffs 📣.
- **Windsurf** ✅: `Accept all` / `Reject all`, a **Quick Review** subagent 📣, and a responsive collapse
  (`@container chat-client (max-width: 375px)`). In Devin Local, 📣 "an edit only runs after you approve it, so
  accepted lines equal suggested lines". Review happens **before** the change is applied, not after.

### 4.6 Parallel and background work

| Antigravity | Windsurf (now Devin Desktop) |
|---|---|
| `Background Tasks`, `Cancel All Tasks`, `Stop All Subagents`; subagent live cards (running / waiting / completed, hover to stop; changelog 2.16) 📣 | Kanban session statuses ✅: `Coding`, `Planning`, `Iterating`, `Testing`, `Setting up`, `Sleeping`, `Waiting for CI`, `Working (~{{duration}} left)`, `Needs input`, `Ready for review` |
| **Side questions**: `Ask a quick question without interrupting the main conversation.` (`/btw`) ✅ | Child sessions: `Split into child sessions`, `Auto-approve child sessions` ✅ |
| **Scheduled Tasks** (cron) and **Remote Control** from any browser 📣 | Cloud states carried into the local IDE: `Devin is sleeping. Wake Devin up by sending a message` ✅ |

### 4.7 Steering and queueing

- **Windsurf** ✅: `Guide Devin while it works, or press {{shortcut}} to queue` /
  `Send to the queue, or press {{shortcut}} to send immediately`. **Steer vs. queue is chosen per message with a
  modifier key.** Queued messages can be edited (`Editing queued message`), reordered (`Drag to reorder`), sent now
  (`Send now`) or removed (`Remove from queue`).
- **Antigravity** ✅: `Queue until after the current turn.`, `Queue message`, `Send now`, plus a Queued Messages
  setting.
- Compare Aside, which picks Queue or Steer globally in settings
  ([browser-agents/03 §5](../browser-agents/03-aside-design-ux.md)).

### 4.8 Status, attention and notifications

- **Antigravity** ✅: sound files `antigravityActionRequired.mp3` and `antigravityCascadeDone.mp3`; setting
  `Play a sound when the agent finishes generating a response.`; the 4s `unread-ping` animation. In 1.x,
  `out/vs/workbench/contrib/antigravitySounds/media/` ships **89 piano notes (A0–C8)** with the command
  `antigravity.playNote` and a setting `enableTabSounds`. What triggers the notes is ⚠️. Remote Control adds browser
  push 📣.
- **Windsurf** ✅: an **amber dot** on the session icon when the session is waiting on the user, with a ring that
  animates "to draw the eye without moving the underlying logo" (`.ws-session-activity-badge`). The icon pulses at
  1.6s while working. The animated **Devin persona** icon has `wake`, `sleep`, `thinking_1` and `thinking_2` states,
  converted from Lottie ("Generated from devin_thinking_1.json by _convert.py"). OS notifications
  (`devin.agentNotifications`) are **off by default**, one per session 📣.

### 4.9 Browser use (Antigravity)

- 25+ browser step types, `Browser Subagent Viewer`, `Stop Recording and Send`, a separate Chrome profile, a URL
  allowlist/denylist, and `Browser Javascript Execution Policy` ✅.
- 2.0 made browser use **explicit via `/browser`**: 📣 "We heard the feedback that the agents were still not capable
  enough to determine exactly when to be using the browser."

### 4.10 Errors

Antigravity ✅: `Agent terminated due to error`, `Agent execution failed.`, `Invalid tool call` (a malformed model call
shown as a short note; changelog 2.15), and transient errors retried with backoff for about twelve minutes (changelog
2.14) 📣. Windsurf ✅: `Devin crashed`, and credit or contract sleeps (`Devin is sleeping because your account is out of
credits.`).

## 5. Stated design philosophy

- Antigravity: "Antigravity is our first product that brings four key tenets of collaborative development together:
  trust, autonomy, feedback, and self-improvement." / "Most products today live in one of two extremes: either they show
  the user every single action and tool call … or they only show the final code change … Neither engenders user trust."
  ([blog](https://antigravity.google/blog/introducing-google-antigravity)) 📣
- Antigravity: "You do not need to carefully monitor every individual tool call or step synchronously; instead, you
  review high-level deliverables at key milestones." ([docs/artifacts](https://antigravity.google/docs/artifacts)) 📣
- Antigravity 2.0: "tying together an IDE and agent-first surface in a single application would be confusing and
  potentially daunting to those less familiar with code and IDEs." … "there is no IDE."
  ([blog, 2026-05-19](https://antigravity.google/blog/introducing-google-antigravity-2)) 📣
- Windsurf 2.0: "The Kanban view is an intentional design choice. As agents become more capable, the engineer's job
  shifts from writing code to directing work." / "The command center doesn't replace the IDE."
  ([blog, 2026-04-15](https://devin.ai/blog/windsurf-2-0)) 📣
- Devin Desktop: "Devin Desktop is a full IDE with an agent manager built in — not the other way around."
  ([blog, 2026-06-02](https://devin.ai/blog/windsurf-is-now-devin-desktop)) 📣

## 6. What is distinctive

1. **A proven common ancestor.** The step enum shares field numbers, the internal name "Cascade" survives, and the
   palette, breakpoints and CSS bridge all persist (§2). This is the clearest lineage in this study.
2. **Artifacts as the unit of review** (Antigravity), with Google-Docs-style comments that also work on screenshots and
   PDF regions.
3. **Three-seed theming** (Antigravity 2.0) vs. **theme-to-token translation with a contrast guard** (Windsurf).
4. **The approval card as scope editor** (both).
5. **Keyword mode switching with motion feedback** (`megaplan`), and **per-message steer vs. queue** (Windsurf).
6. **One chat client for web and desktop** (Windsurf): cloud concepts (Sleeping, ACU, child sessions) enter the local IDE
   unchanged.
7. **A public retreat from autonomy**: Antigravity's `/browser` requires the user to ask for the browser.
8. **Sound as signature** (Antigravity): action-required and done cues, plus a piano-note set.

## 7. Refutations and contradictions

- ❌ **Antigravity docs vs. the 2.17.0 artifact on Planning Mode.** `docs/artifact-review.md`: "When starting a new
  Agent conversation, you can choose between two primary execution modes … **Planning Mode** … **Fast Mode**". The
  2.17.0 settings handler in `main.js` reads `case Oi.PLANNING_MODE:throw Error("Planning mode is no longer supported")`,
  and changelog 2.17.0 replaces the mode with `/plan` and the Plan Review Policy. The strings `Planning` and `Fast`
  still ship, so where (or whether) they render is ⚠️. Graded moderate.
- 📣 **Windsurf docs disagree with themselves.** `cascade.md`: "Cascade comes in two primary modes: **Code** and
  **Chat**". `modes.md`: "Code / Plan / Ask".
- ⚠️ **Cascade sunset date.** The 2026-06-02 post says legacy Cascade remains usable "through July 1st", but the
  2026-09-23 build still ships Cascade settings and UI. Whether it is still active was not verified.
- ⚠️ **Antigravity's Linux download page** links only 1.23.2. The 2.x builds appear only on `/download`, and `llms.txt`
  describes the Linux download as "Download CLI for Linux environments", which does not match what is offered.

## 8. What this means if you are building an agent client

- [ ] Keep the **wire protocol stable while the skin churns**. Both forks rewrote tokens and components but kept 43/45
      step numbers. A versioned step enum is what lets a UI be replaced.
- [ ] Make the approval card **edit the scope** (target string or command), not just accept or decline it; grant exactly
      what was edited.
- [ ] Offer **once / session / always / deny** as distinct grants, and send them as data (ACP `allow_once …
      reject_always`, cf. [SYNTHESIS §2.1](../SYNTHESIS.md)).
- [ ] Give the plan a **reviewable object** (an artifact or file) with inline comments and one `Proceed`/`Implement`
      action, and a policy for when review is skipped.
- [ ] Decide steer vs. queue **per message** (modifier key) and let queued messages be edited and reordered.
- [ ] Give attention states their own **colour and position** (the amber "waiting on user" dot) and keep OS
      notifications opt-in, one per session.
- [ ] Derive the theme from **few seeds** or from the host theme **with a contrast guard**. Don't hand-tune tokens per
      theme.
- [ ] Respect `prefers-reduced-motion`, but exempt motion that carries information (`motion-essential`).
- [ ] If a capability is unreliable (browser use), **say so and make it explicit** rather than silently autonomous.

## 9. Open questions

- Is Antigravity 2.0's "Jetski Web" a rewrite of the 1.x Agent Manager or the same code with a new theming adapter?
  Lexical, the `cascadeId` model and the NUX enum carried over; Tailwind v3 → v4 and Headless UI → Base UI changed.
- When Devin Local fully replaces Cascade, does the Cortex protocol leave Windsurf (now Devin Desktop) entirely?
- What do Antigravity's 89 piano notes and `enableTabSounds` actually play on? ⚠️
- Are `vs/sessions` and bundled `@github/copilot-sdk` / `@anthropic-ai/sandbox-runtime` upstream VS Code 1.126 or
  Cognition additions? ⚠️
- Everything visual (the rendered mode tints, the megaplan snake, the Kanban geometry, the artifact review pane) is
  unseen ⚠️.
