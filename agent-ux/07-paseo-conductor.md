# 07. Paseo and Conductor — a daemon-first client and a worktree-first cockpit

> Products:
> - **Paseo 0.9.2** (all workspace packages). Source `getpaseo/paseo` @ `76a9781` (2026-09-26, Apache-2.0),
>   shallow clone. Read TypeScript source plus the in-repo design documents (`docs/design.md`,
>   `docs/glossary.md`, `docs/product.md`, `public-docs/*.md`).
> - **Conductor 0.87.5** (closed source, macOS). `Conductor_0.87.5_aarch64.dmg` (80,504,300 B, sha256
>   `6eec4450…ee337eba`) from the CrabNebula CDN link in conductor.build's download dialog. 2,906 frontend
>   assets recovered from the brotli asset table embedded in the Tauri binary `Contents/MacOS/conductor`;
>   the Bun-compiled sidecar `Contents/Resources/bin/.internal/conductor-runtime` read as strings; docs
>   from `conductor.build/llms-full.txt` and `/changelog.md`.
>
> Method: static extraction only. There is no display, so **nothing was seen rendered**; every visual
> claim is inferred from tokens and class names. Researched 2026-09-26.
>
> Dominant grade: ✅ for both. Paseo's is source plus design documents that state intent (📣).
> Conductor's is shipped bundle plus sidecar. Two ❌ minor, two ⚠️ disclosure gaps.

Same question — one person running many coding agents — from opposite ends. **Paseo** starts from the
*daemon*: agents run on a host you own, and desktop, mobile, web, CLI and other agents are interchangeable
clients of one wire protocol. **Conductor** starts from the *worktree*: each task is a city-named git
working tree, and the product walks it to a merged PR. The difference is sharpest in approval (§3.1).

## 1. What they are and how they are built

### 1.1 Paseo ✅

| Layer | Implementation |
|---|---|
| App | `packages/app`: **Expo 54 / React Native 0.81.5 / React 19.1**, `expo-router`, `react-native-web ~0.21` |
| Styling | `react-native-unistyles` v3. `useUnistyles()` is banned: "Reviewers MUST reject PRs that introduce a new `useUnistyles()` call" (`docs/unistyles.md`), because it re-renders warm agent-stream subtrees in lockstep |
| Desktop | **Electron 44** (`packages/desktop`) loads the Expo *web export* via the custom scheme `paseo://app` (`src/main.ts:790`, `app-dist` resource) |
| Mobile | Native RN. 📣 "The mobile app is built in React Native, not a webview" (`public-docs/why.md`) |
| Daemon | `packages/server`. It wraps providers: Claude via Agent SDK `canUseTool`, Codex app-server, ACP (Copilot, Cursor, Kimi, Kiro, generic), OpenCode, Pi, OMP |
| Wire | `packages/protocol`: zod schemas over WebSocket. `packages/relay` provides the E2E relay |
| Other clients | `packages/cli` (`paseo …`), an MCP tool surface for agents, and the Hub (a separate service) |
| Libraries | lucide-react-native, @gorhom/bottom-sheet, @floating-ui/react-native, xterm.js 6, CodeMirror 6 (+vim), mermaid, Skia, i18next (10 locales), zustand, TanStack Query/Virtual. **No web component kit** (no Radix, shadcn or Base UI); primitives are hand-built in `components/ui/` |

**One design system across desktop and mobile** comes from one RN component tree plus a single
`useIsCompactFormFactor()` branch at the top of each screen. 📣 `docs/design.md` §9: "Compact-first.
The small case is designed; the large case adds chrome around it."

List+detail is a stacked push on compact and a 320px sidebar + pane on desktop; the workspace is tabs vs
splits; `<AdaptiveModalSheet>` is a bottom sheet vs a centred card; the left sidebar overlays vs pins.
Electron window controls are modelled as "top-corner obstructions, not a compact-layout condition".

**Layout.** The agent is the centre of a *workspace*. Agents, terminals, a browser, files and the diff are
tabs or splits in one workspace. The Explorer sidebar (Files, Changes) sits on the right, and the
workspace list sits on the left. 📣 `docs/product.md`: "Agents are the focus … Files, terminals, diffs,
and other supporting tools help you do that."

### 1.2 Conductor ✅

| Layer | Implementation |
|---|---|
| Shell | **Tauri 2.11.1** (wry). Plugins: clipboard-manager, deep-link, dialog, fs, http, notification, opener, os, shell, sql, store, updater, window-state |
| Frontend | Vite + **React 19.2.3** + **Tailwind v4** + **Base UI**. The `index.html` comment reads "body-level portals (Base UI ContextMenu, Menu, etc.) … Required by Base UI's quick-start" |
| Icons | **lucide**, one lazy chunk per icon (`assets/list-check-*.js`, `assets/badge-japanese-yen-*.js`, …), plus `material-icons/` for file types |
| Sidecar | `bin/.internal/conductor-runtime`, Bun-compiled, **embeds the Claude Agent SDK** (`canUseTool`, `permissionMode`, `allowDangerouslySkipPermissions`) and an ACP client |
| Bundled tools | `gh`, `watchexec`, `checkpointer.sh`, `spotlighter.sh`, `git-busy-check.sh`, and a Conductor skill/plugin (`conductor-skill/skills/conductor/SKILL.md`) |
| Leftover | `index.html` `<title>` is still `Tauri + React + Typescript` |

**Layout** ⚠️ (from settings keys and strings, not seen): left sidebar of workspaces (city, branch,
status); centre chat with tabs (`nav.splitTab` ⌘D, `view.toggleZenMode` ⌘.), replaceable by Big Terminal
Mode; right panel (`right_panel_visible`) with git/Checks, terminal, Run/Spotlight. The agent lives *in
the workspace*, and the workspace *is* the branch.

## 2. Design system

### 2.1 Paseo tokens — `packages/app/src/styles/theme.ts` ✅

| Role | Light | Dark (default "paseo" tint) |
|---|---|---|
| surface0 / 1 / 2 / 3 | `#ffffff` `#fafafa` `#f4f4f5` `#e4e4e7` | `#181B1A` `#1E2120` `#272A29` `#434645` |
| foreground / muted / extraMuted | `#1a1a1e` `#71717a` `#a1a1aa` | `#fafafa` `#A1A5A4` `#717574` |
| accent (one CTA per surface) | `#20744A` | `#20744A` (bright `#7ccba0`) |
| destructive | `#b04138` | `#c64f43` |
| status success/danger/warning/merged | `#3e704a #9d433b #7b5d39 #7347af` (L 0.50, 60% gamut chroma) | `#6cb17b #d8847b #c09664 #a890d5` (L 0.70, 55%) |
| status **dots** success/danger/warning/running | `#299f51 #f12e2f #b37824 #268ae0` (L 0.62, 90%) | `#35c264 #f7796d #db932e #5caaf6` (L 0.72, 90%) |
| diff +/− | `#15803d` / `#b91c1c` | `#4ade80` / `#ef4444` |

| Scale | Values |
|---|---|
| Themes | light, dark, zinc, midnight, **claude** (accent `#d97757`), ghostty, pureBlack, plus plugin themes |
| Spacing | 0 2 4 6 8 12 16 24 32 48 64 80 96 128 ("`padding: 20` and `gap: 10` are wrong") |
| Font size | code 12, sm 12, **base 14**, content 15 (16 native), lg 16, xl 18, 2xl 20, 3xl 22, 4xl 26 |
| Weight | normal / 500 / 600 / bold. Medium is reserved for "structural labels" |
| Radius | 0 2 4 6 8 12 16 full |
| Icon size | 12 14 16 20 |
| Fonts | **system stacks only**. No bundled font files. Interface and code size are user settings |
| Motion | Reanimated, mostly `Easing.inOut(Easing.ease)` at 800–1200 ms pulses. No motion tokens |

> 📌 **Paseo's status colours are generated, not picked**: one OKLCH lightness and one gamut-relative
> chroma fraction per family, "Regenerate the set, never one hue", level set "by the densest consumer, the
> sidebar workspace list". Dots get a louder band because "at 6pt four dark hues … all read as one dark
> blob"; light dots sit at L=0.62, "the last step where all four clear 3:1". The only colour policy in
> this study written down as an algorithm with its reasons.

### 2.2 Conductor tokens — `assets/renderApp-BYEcFwvt.css` in Conductor 0.87.5 ✅

The naming is shadcn-style (`--background --card --popover --primary --muted --accent --destructive
--border --input --ring --sidebar-*`), extended with product roles.

| Role | Light | Dark |
|---|---|---|
| background / foreground | `#fff` / `#2c2826` | `#141110` / `#eae8e6` |
| primary | `#413030` | `#f3f2f1` |
| card / sidebar | `#fff` / `#fafaf9` | `#2c2826` / `#211e1c` |
| highlight · unread · special | `#faf7f5` · `#a4847f` · `#cca694` | `#2a1e1d` · `#cca694` · `#cca694` |
| destructive / success / info | `#dc2828` / `#16a249` / `#0da2e7` | `#f87272` / `#4ade80` / `#3c83f6` |
| `--plan-border` | `#cca694` | `#836967` |
| `--status-backlog / in-progress / in-review / done / canceled` | `#8e8885 #e0bb00 #16a249 #cca694 #a5a09c` | `#8e8885 #ffdc2e #4ade80 #cca694 #a5a09c` |
| `--todo-in-progress / completed / pending` | `#2463eb #16a249 #766f6b` | `#61a6fa #4ade80 #a5a09c` |
| diff line bg | `oklab(72.12% -.169 .102 / .1)` (border `/ .6`, highlight `/ .2`) | same |

| Scale | Values |
|---|---|
| Variants | light, dark (default; pre-paint `hsl(24 10% 7%)`), `html.dark.low-contrast-dark` |
| Radius | `--radius: .5rem` (Tailwind derived) |
| Letter-spacing | per size, `-.04em` at 5xl up to `+.04em` at 3xs |
| Motion | `--default-transition-duration .15s`, Tailwind easings. `loadout-equip .22s cubic-bezier(.23,1,.32,1)`, `slow-pulse 2.4s`, `equalizer .8s`, `coach-mark-bounce 2s` |
| Fonts bundled | **Geist** and **Geist Mono** (variable 300–700), **iA Writer Mono** (variable 100–900), Symbols Nerd Font Mono. `--font-sans` stays `system-ui` ⚠️ (where Geist actually applies is unseen) |
| Sounds | transit chimes as "Completion sound": NYC subway doors, Paris Métro, SNCF jingle, SF Muni gong, `choo-choo`, `quack` |

Warm stone/brown palette and a playful personality — city-named workspaces, a "Passport" travel log,
train chimes ("Choo choo!" signs off the Series A post). Paseo is the opposite: "Nothing crowds, nothing
decorates, nothing apologizes."

## 3. How harness primitives are rendered

### 3.1 Approval — Paseo: a request object, and a message is an answer ✅

The wire shape (`packages/protocol/src/messages.ts:450–487`):

```ts
AgentPermissionRequest = { id, provider, name,
  kind: "tool" | "plan" | "question" | "mode" | "other",
  title?, description?, input?, detail?: ToolCallDetail, suggestions?,
  actions?: { id, label, behavior: "allow" | "deny",
              variant?: "primary" | "secondary" | "danger",
              intent?: "implement" | "implement_resume" | "dismiss" }[],
  metadata? }
AgentPermissionResponse =
  | { behavior: "allow", selectedActionId?, updatedInput?, updatedPermissions? }
  | { behavior: "deny",  selectedActionId?, message?, interrupt? }
```

**The provider supplies the buttons as data.** The client's fallback, when `actions` is absent, is
`Deny` (danger) and `Accept` (primary), or `Implement` for plans. The same object is rendered four ways:

| Renderer | Surface | Strings / verbs |
|---|---|---|
| GUI card | `PermissionRequestCard`, `packages/app/src/agent-stream/view.tsx` | title `request.title ?? name ?? "Permission Required"`; tool detail capped at 200px; `How would you like to proceed?`; the action buttons |
| CLI | `paseo permit ls \| allow <agent> [req] [--all] [--input <json>] \| deny [--message] [--interrupt]` | edits input on allow; reason and interrupt on deny |
| MCP (agents) | `list_pending_permissions`, `respond_to_permission` | a **parent agent answers its child's prompt**. The child's "needs permission" notice embeds the request inside `<permission-request>` JSON (`server/agent/agent-prompt.ts`) |
| Push | `Agent needs permission`, body = title + description, or input JSON, ≤220 chars | not actionable (no notification categories). Tapping opens the app |

**A message sent while a prompt is pending denies it, with the message as the reason.** 📣 `docs/glossary.md`
("Steer"): "Sending while the agent waits on a permission denies that request first, so the message
reaches the same turn instead of stalling behind it." ✅ The Claude provider resolves the pending
`canUseTool` with `"The user answered with a message instead of approving. Their message follows."`
(`STEER_SUPERSEDED_PERMISSION_MESSAGE`, `providers/claude/agent.ts:377`); the composer comment reads
"Queueing behind a permission prompt would strand the message."

> 📌 **This is what [SYNTHESIS §2.1](../SYNTHESIS.md#21-approval-as-a-protocol-primitive) asked for,
> implemented rather than hinted.** [Aside](../browser-agents/03-aside-design-ux.md) makes prompts
> channel-renderable (buttons, numbered text fallback, *"or just reply with your answer."*); SYNTHESIS
> concluded "If callers will ever be remote, approval needs a shape before it needs a UI." Paseo has both
> halves: a typed request with server-supplied `actions`, answerable from GUI, CLI, MCP or another agent;
> and the free-text reply **defined in the protocol, not in copy** — any user message is a `deny` whose
> `message` is the text, delivered into the *same* turn.
>
> Aside's free-text reply *answers* the question. Paseo's *declines* the tool and hands the words to the
> model. For a tool gate that is the safer reading: silence or prose never becomes consent.
> Codex's app-server ([../docs/02-app-server-protocol.md](../docs/02-app-server-protocol.md)) has the
> typed request but not this rule. There, an unanswered request stalls the turn.

**No lasting grant in any Paseo client** ✅ (absence). The Claude provider forwards SDK `suggestions`,
but no client sends `updatedPermissions` (zero hits in `packages/app/src`, `packages/cli/src`); standing
permission exists only as a **mode** (§3.2). This matches Aside's `Allow once` and "No lasting permission will be granted" (SYNTHESIS §2.1). It meets
the [approval gate](../ai-workflow/wiki/concepts/approval-gate.md) property that one approval does not
widen scope. Contrast Conductor (§3.1b).

**Voice mode** auto-allows only the `speak` tool (`server/voice-permission-policy.ts`). Every other
prompt stays visual, and the voice system prompt opens "The user cannot see your chat messages or tool
calls." ⚠️ No spoken approval path was found.

### 3.1b Approval — Conductor: off by default, CLI-parity when on ✅

The default lives in the sidecar (`conductor-runtime`, Conductor 0.87.5):

```js
requiresToolApprovals: B.requiresToolApprovals ?? false
function W$4({ requiresToolApprovals: U, autoPermissionModeEnabled: B }) {
  if (!U) return "bypassPermissions";  return B ? "auto" : "default"; }
function Pa6(U) { return U.requiresToolApprovals === true ? "ask" : "auto_approve"; }   // ACP agents
```

Unless the user enables **`Claude Code tool approvals`** ("Require manual approval before agents can run
tools."), local Claude sessions run in `bypassPermissions` and ACP agents `auto_approve`. Codex has its own
setting: **`Codex tool approvals`** `Default` / `Always approve`.

📣 The docs agree: "Some tool calls may ask for approval before the agent continues"; Big Terminal
presets "start in full-access mode" when approvals are off (`claude --dangerously-skip-permissions`).
Approvals are **user-only keys** (a repository file setting them is ignored); an organisation can force
them on ("Managed by your organization. Agents require manual approval for tool calls.").

With approvals on, the card mirrors Claude Code's CLI (`assets/renderApp-ChvbbKhl.js`).

Headlines by tool: `Do you want to run this command?` (Bash) · `Do you want to make these changes?` (edit
tools) · `Do you want to run this agent?` (Task/Agent) · `Do you want to fetch this page?` · `Do you want to
do this search?` · `Do you want to run this tool?` · `Do you want to run this command on your Mac?` (remote →
local). The subline is `decisionReason ?? "Approve this tool request to continue"`. The scope ladder, from
narrowest to widest:

| Button | Key | Decision / scope |
|---|---|---|
| `Yes` | **Enter** (bare) | allow once |
| `Yes, and don't ask again for: <rule ≤40 chars>` | ⌘Enter | `allow_with_permissions` (the SDK suggestion rule) |
| `Allow all edits during this session` | ⌘Enter | `allow_edits_for_session` (edit tools) |
| `Always allow <tool>` | ⌘Enter | `always_allow` (mcp__*, WebSearch, WebFetch without a rule) |
| `Yes for this session` | ⌘Enter | local command, session |
| `Yes always` | — | local command. **Flips `Always allow local commands`** ("Run local commands from remote agents without asking. Turned on when you choose Yes always on a local command approval.") |
| `No` | Backspace | deny |

Codex permission-profile requests render `Deny` / `Approve` (`scope: "turn"`). All keys are configurable
(`chat.approveToolCall`, `chat.autoAcceptToolCall`, `chat.denyToolCall`, priority HIGH).

> ⚠️ **Bare Enter approves.** Where the composer and the approval share a surface, a user typing a
> follow-up can press Enter into an approval. What Conductor does with text typed while a request is
> pending was not determinable statically.

> ⚠️ **One standing grant crosses a machine boundary on one click.** Cloud agents may request "approved
> one-shot commands on this Mac. Each command still requires your approval." — until a single `Yes always`
> turns the global setting on. By [strands/07](../strands/07-security.md)'s gate properties, that is a
> widening grant with no scope beyond "all remote agents".

### 3.2 Autonomy modes

**Paseo** ✅ `packages/protocol/src/provider-manifest.ts`. Each provider's native modes keep their native
labels but get one **shield icon family** and a `colorTier`:

| Provider | Mode label | Icon | colorTier |
|---|---|---|---|
| Claude | `Plan Mode` | ShieldEllipsis | planning |
| Claude | `Always Ask` | Shield | safe |
| Claude | `Accept File Edits` | ShieldPlus | moderate |
| Claude | `Auto mode` ("Uses a model classifier to review permission prompts automatically") — **default** | ShieldCheck | moderate |
| Claude | `Bypass` ("Skip all permission prompts (use with caution)"), `isUnattended` | ShieldOff | dangerous |
| Codex | `Default Permissions` | Shield | moderate |
| Codex | `Auto-review` — **default** | ShieldCheck | moderate |
| Codex | `Full Access`, `isUnattended` | ShieldOff | dangerous |

The mode control is "icon-only" (glossary). Both defaults are *machine-reviewed* approval, not human
prompts. Cross-provider mode inheritance fails closed (`server/agent/create-agent-mode.ts`): an unattended
parent yields the target's unattended mode; anything else throws "cannot inherit mode … Pass an explicit mode".

**Conductor** ✅: controls are Plan (⇧Tab), Fast (⇧⌘E), effort cycle (⇧⌘/), model picker (⌘/),
**Loadouts** 1–5, Codex personalities and Codex `/goal` (goal bar). Beyond these, autonomy is the single
approvals toggle, plus `Auto permission mode` ("Turns on Claude auto mode.", Experimental, search terms
include `yolo`).

### 3.3 Plan and todos

| | Paseo ✅ | Conductor ✅ |
|---|---|---|
| Plan prompt | a permission of `kind:"plan"` rendered as `PlanCard` (markdown) | status `Needs plan response` |
| Actions | Claude `Reject` / `Implement` / `Implement with Bypass` (only if pre-plan mode was bypass); Codex `Dismiss` / `Implement` | Approve (⇧⌘Enter); **`Hand off` — "Send plan to a new chat for implementation"** vs "Execute plan in current chat" |
| After approve | mode → `acceptEdits` (or back to bypass) | mode → approvals-derived, i.e. **bypass by default** |
| Feedback | deny + message | typed in the composer: `Enter your plan adjustments here...` |
| Transcript outcome | `Approved plan` / `Rejected plan` / `Canceled plan` | — |
| Todos | agent `todo` timeline item → **Tasks track** pill, `{{completed}}/{{total}} tasks` | **merge-blocking, user-owned** Todos in Checks: "Workspaces are blocked until todos are checked off"; `@todos` sends them to the agent |

> 📌 Conductor separates *agent todos* (organising a turn) from *merge todos* (a human's definition of
> done). Paseo only has the former.

### 3.4 Tool-call transcript

**Paseo** ✅ timeline items: `user_message`, `assistant_message`, `reasoning`,
`tool_call{running|completed|failed|canceled}`, `todo`, `error`, `notification{info|warning|error}`,
`compaction{loading|completed; auto|manual}`, `plugin`.

Detail variants: `shell read edit write search fetch sub_agent plan worktree_setup unknown`. Runs group
into one sentence (`edited 3 files`, `ran 2 commands`, `read 4 files`, `called Paseo N times`, joined with
`and`). Turn footer: `Fork in a new tab` / `Fork in a new workspace` (in-flight fork omits the boundary to
capture the streaming response). Rewind: `Rewind conversation` / `files` / `both`.

**Conductor** ✅: tool calls are collapsed by default. `Don't collapse tool calls (Garry Mode)` — "Show
all tool calls expanded by default instead of collapsed." — toggled with ⌃O. Fork: `Fork chat to new
tab` (⌥⌘Enter).

### 3.5 Diff and review

Both products turn a diff comment into **a prompt**, not a forge post:

- **Paseo** ✅ `ReviewAttachmentSchema`: `mimeType: "application/paseo-review"`, `mode: uncommitted|base`,
  comments with hunk context. It rides in the composer (`Open review attachment`).
- **Conductor** 📣✅ Diff Viewer (⇧⌘D): "Inline comments become composer attachments that you can send
  back to the agent that made the change."
  Viewed toggle (⌃V), unified view, commit filter, in-diff editing (0.84); `Review` = agent review with
  its own `review_model`; Checks tab (git, PR, CI, deployments, comments, todos); ⇧⌘ verbs P `Create PR`,
  Y `Commit and push`, M `Merge PR`, **X `Fix errors`**, R `Start review`; `Treat optional checks as blocking`.

### 3.6 Parallel and background work

**Paseo** ✅: workspaces with Isolation `Local` / `New worktree`, per-worktree service ports behind
`*.localhost` proxy URLs, and a **Subagents track** (`N subagents`, `N ready to review`). Agents drive
Paseo itself via MCP (create workspaces, spawn agents).

**Conductor** ✅📣: one workspace per "shippable unit".

- City-named directories (`warsaw-v2`), renamed to the branch once named; per-workspace `CONDUCTOR_PORT`,
  `.worktreeinclude`, `Files to copy`, `.context/` notes.
- **Spotlight**: `spotlighter.sh` uses `watchexec` to checkpoint the workspace on change and restore it
  into the repo root. You test a workspace in the main checkout; checkpoints double as a sync transport.
- **Checkpoints**: `checkpointer.sh` writes `refs/conductor-checkpoints/<id>` before each agent response
  (HEAD, index and worktree, including untracked files; HEAD never moves). It refuses when the repo root
  ≠ cwd (exit 103).
- 📣 Checkpoint restore "will **permanently delete** all user and AI messages from the selected turn and
  later", so code and chat roll back together.

### 3.7 Status and attention

**Paseo** ✅:

- Buckets `needs_input > failed > running > attention > done`; dots amber / red / **blue** / green; tabs
  show a filled `CircleAlert` for needs-input. 📣 in code (`utils/status-dot-color.ts`): "needs_input is
  amber because it wants something from you. Working is blue: an agent doing its job is the one busy state
  that asks for nothing."
- Notifications are **presence-routed** (`server/agent-attention-policy.ts`): a visible client focused on
  the agent suppresses it; else the most recently active client (≤180 s) gets one in-app notice; push only
  when nobody is present, **never for errors**. Titles: `Agent needs permission` / `Agent needs attention` / `Agent finished`.

**Conductor** ✅ merges agent and PR state into one workspace status:

`Unstarted` · `Setting up` · `Failed` · `Needs plan response` · `Needs permission` · `Needs input` ·
`Working` · `Cancelling` · `Waiting for background tasks` · `Merged` · `In merge queue` ·
`Ready to merge` · `Draft pull request` · `Merge conflict` · `Checks failing` · `Checks running` ·
`Pull request open` · `Local workspace` · `Ready`

`Agent notifications` ("Get notified when an agent finishes working") are suppressed while the session is
selected and focused; `Completion sound` plays the §2.2 transit chimes.

### 3.8 Steering and queueing

| | Paseo ✅ | Conductor ✅ |
|---|---|---|
| Setting | `Default send`: `Interrupt` / `Steer` / `Queue` | `Follow-up behavior`: "Queue messages to send after the agent finishes, or steer the agent mid-turn." |
| Default | **steer** (migrated from interrupt) | **`"steering"`** |
| Copy | "When the agent is running, Enter steers the active turn. Command/Ctrl+Enter queues." | queue editable, reorderable, pausable (`Queue paused`); `Steer with queued message` (Enter) |
| Pending permission | a message **denies** it and joins the turn (§3.1) | ⚠️ unknown |

Both converged on the Aside distinction (Queue vs Steer,
[03-aside §5](../browser-agents/03-aside-design-ux.md)), and both chose steer as the default.

### 3.9 Errors

- **Paseo** 📣 `design.md` §11: "Error copy is direct. 'Unable to remove host' … not 'Sorry, we couldn't
  remove the host.'" State surfaces at the smallest scope; "Changing state must not move the layout."
- **Conductor** ✅: provider errors are prefixed (`<Provider> error: …`), plus `Interrupted by user` and
  `You hit your spend cap set by the owner of your workspace.`

## 4. Stated design philosophy (📣)

- Paseo, `docs/design.md` (repo @ `76a9781`): "Paseo is minimal, spacious, quiet, confident. …
  The app is calm so the user's work is not. Every visual decision serves either _act on this_ or
  _understand this_ — never _look at this_." / "Accent is the one CTA per surface." / "Destructive is a
  color, not a click." / "The whitespace is the design."
- Paseo, `docs/product.md`: "A feature can work exactly as intended and still be the wrong addition."
  `public-docs/why.md`: "Not a hosted agent, not an IDE, not a model provider."
- Paseo, `docs/glossary.md`: "Authoritative terminology. UI label wins." It forbids "Task/Job/Run" for an
  agent, "checkout" for a workspace, "Repo" for a project.
- Conductor, https://www.conductor.build/docs/concepts/workflow: "The workspace is the unit of
  delegation. The branch and pull request are the unit of integration."
- Conductor, https://www.conductor.build/docs/concepts/workspaces-and-branches: "Workspace isolation is
  development isolation, not a security boundary."
- Conductor, https://www.conductor.build/blog/series-a: "most software would soon be built by AI teams,
  and we'd need new interfaces to manage them."

## 5. What is distinctive

1. **Paseo: approval as a multi-renderer request with a message-means-deny rule** (§3.1). This is the
   most complete answer to SYNTHESIS §2.1 in this study.
2. **Paseo: no lasting grant in the UI.** Autonomy is a mode, and modes are normalised into one icon family.
3. **Paseo: a colour policy as an algorithm**, and notifications routed by presence.
4. **Paseo: one RN tree for iOS, Android, web and Electron**, branched once per screen.
5. **Conductor: the workspace is the branch.** One status vocabulary runs from `Needs permission` to
   `Ready to merge`. Merge-blocking human todos. Checkpoints reused for Spotlight.
6. **Conductor: keyboard-first approval**, cloned from the Claude Code CLI with a once → rule → session → always scope ladder.
   The default is that it never appears.
7. **Shared:** review comments become prompts; follow-ups default to steer; approval state is lifted into
   the work item's status.

## 6. Refutations and contradictions

- ❌ minor (Paseo). `docs/design.md` §10: "Sentence case … Title case is wrong." Yet `en.ts:236`
  `required: "Permission Required"`.
- ❌ minor (Paseo). The manifest tags every bypass mode `colorTier: "dangerous"`, but no code in
  `packages/app/src` maps `colorTier` to a colour; only `planning` is read (`agent-controls/policy.ts`).
  "Dangerous" renders exactly like "moderate".
- ⚠️ disclosure gap (Paseo). `public-docs/security.md`: "Your code never leaves your machine … The relay
  cannot read your messages". But push payloads go to `https://exp.host/--/api/v2/push/send`
  (`server/push/push-service.ts:24`), with the permission input or assistant text (≤220 chars) as the
  body. They are outside the E2E channel, and the security page does not mention them.
- ❌ minor (Conductor). `/docs/reference/cities`: "Conductor currently has 295 cities." Changelog 0.50.0:
  "Adelaide, AUS joins us as the 296th Conductor city."
- ⚠️ framing gap (Conductor). The docs describe approvals as something that "may" happen. The artifact
  shows they are **off unless enabled**, so the local Claude default is `bypassPermissions`.

## 7. What this means if you are building an agent client

- [ ] Give approval a **request shape with its own action list** (`id, label, behavior, variant`), so
      GUI, CLI, MCP and push can all render it without new code (SYNTHESIS §2.1).
- [ ] Decide what a **free-text message during a pending approval** means, and put that in the protocol.
      Paseo's "deny, then deliver the message into the same turn" never stalls and never turns prose into consent.
- [ ] Let **another agent** answer a child's approval only through the same typed request, and embed the
      request verbatim in the parent's notification.
- [ ] Prefer **modes over sticky grants**. If you offer "don't ask again", show the exact rule (Conductor
      truncates it to 40 chars) and never let one click widen scope across machines.
- [ ] Do not bind **bare Enter** to approve on a surface that shares focus with the composer.
- [ ] Route attention by **presence**: suppress if the user is looking, notify one device, push only when
      nobody is there. Keep push bodies inside your encryption story, or disclose that they are not.
- [ ] Put the "needs you" state in the **work item's status**, in a colour distinct from "working".
- [ ] Make diff comments **attachments to the next prompt**.
- [ ] Default follow-ups to **steer**, and expose Queue and Interrupt.
- [ ] If a field says "dangerous", make it look dangerous.

## 8. Open questions

- Paseo Hub (separate service, not in this repo): does a Slack or Discord-triggered agent ever raise an
  in-channel approval, or is authority always preset? The docs' examples use `approval_policy: never` and
  `disallowedTools`.
- Conductor: what happens to a pending tool approval when the user sends a message? Steer, queue or deny?
- Conductor: exact pane geometry and where Geist and iA Writer Mono actually apply. Visual, unseen.
- Paseo: how the permission card's option buttons lay out on compact vs desktop
  (`optionsContainerDesktop`). Unseen.
- Both: animation and pacing of the running indicators. Only durations were extracted.
