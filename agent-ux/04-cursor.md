# 04. Cursor — the Agents Window, run modes, and Keep/Undo

> Product: **Cursor 3.22.7** (Anysphere), stable. Linux `.deb` obtained 2026-09-26 via
> `cursor.com/api/download?platform=linux-x64&releaseTrack=stable` →
> `downloads.cursor.com/production/37076c6c…2268/linux/x64/deb/amd64/deb/cursor_3.22.7_amd64.deb`
> (sha256 `923fd2d2…37800ab`); `product.json` `vscodeVersion` 1.128.0, built 2026-09-24.
>
> Method: static extraction from the shipped bundles; no display, so **nothing was seen rendered** and
> anything visual is ⚠️. Docs via `cursor.com/docs/*.md`, changelog RSS, two blog posts. Researched 2026-09-26.
> Paths are relative to `/usr/share/cursor/resources/app/` in Cursor 3.22.7.
>
> Dominant grade: ✅ (strings, tokens and mode logic from `workbench.glass.main.js`); 📣 for philosophy; four ❌ (§6).

## 1. What it is and how it is built

### 1.1 Two workbenches in one VS Code fork

| Aspect | Finding | Grade |
|---|---|---|
| Shell | Electron, a VS Code fork (`product.json`: `vscodeVersion` 1.128.0) | ✅ |
| Classic IDE | `out/vs/workbench/workbench.desktop.main.js` (38.7 MB) and `.css` (1.27 MB) | ✅ |
| **Agents Window** | `out/vs/workbench/workbench.glass.main.js` (45.4 MB) and `.css` (1.26 MB). The internal codename is **Glass**: `GlassWorkbench`, the body flag `data-cursor-glass-mode`, and `out/main.js` pointing at the glass bundle | ✅ |
| Glass is still VS Code underneath | The glass bundle contains `workbench.parts.editor` (85×), `activitybar` (55×), Monaco (794×), and the message `GlassWorkbench requires INotificationService to be backed by the workbench NotificationService` | ✅ |
| UI layer | React compiled by the React Compiler (`react.memo_cache_sentinel` 2,722×) | ✅ |
| Styling | **StyleX**: 45 `*.stylex.js` modules, including `tokens.stylex.js` and `row-active-reveal.stylex.js`. Classes are atomic `ui-xxxxxx` (the shared library) and `glass-xxxxxx` (Agents Window surfaces); keyframes use StyleX's `…-B` names. Tailwind variables (`--tw-ring`, `--tw-shadow`) remain as residue | ✅ |
| Components | **Base UI** (its error string `"Base UI: Render element or function are not defined."`, 81×), **cmdk** (81×), Lexical for the prompt input, and Shiki for code. No `@radix-ui`, no framer-motion | ✅ |
| Agent runtime | Extensions `cursor-agent-host` (with an `agent-host-daemon`), `cursor-agent-exec`, `cursor-agent-worker`, `cursor-local-agent-runtime`, `cursor-computer-use`, `cursor-browser-automation`, `cursor-shadow-workspace`, `cursor-mcp` | ✅ |

> 📌 Cursor did not replace the IDE; it shipped a **second renderer entry point** into the same platform
> with a new React/StyleX layer. Both can be open at once (`Open Agents Window`, `Open IDE`, `New Agents Window`) ✅.

### 1.2 Where the agent lives

- **Agents Window.** On the left, a **sidebar of agents** across all workspaces, with `Group by`,
  `Sort by`, `Pinned`, `Today` / `Yesterday` / `Older`, `Archived` and `Draft`. The centre holds the
  conversation. On the right, a **tab panel** for Files, Changes, Canvases, PRs, Browser and
  Terminals. Several conversations can sit side by side in a **tileset**: `Split Tile Horizontally`,
  `Split Tile Vertically`, `Focus Adjacent Tile`, `Remove from Tileset`. Inactive tiles dim through
  `--glass-agent-panel-inactive-tile-opacity` (0.8 / 0.96 / 1) ✅ from strings and tokens; the exact
  geometry is ⚠️.
- **Full-screen tabs (3.4).** A right-panel tab can take over the working area, which "**replaces the
  agent chat with a floating prompt bar**" 📣 ([changelog 3.4](https://cursor.com/changelog/3-4)).
- **IDE.** Agent in the side pane (`Cmd+I`); `Open Chat as Editor Tabs`, `Toggle Agents Side Bar`, and an
  agents toggle in the title bar (`out/media/agents-toggle-{filled,outline}.svg`) ✅.
- **Every setting is tagged with its surface** (`surface:"glass"` / `"ide"`): `Inline Diffs` is `ide`;
  `Default Environment`, `Tool Call Density`, `Hue` are `glass` ✅.
- **Projects** (Sep 2026). A coordinator agent that "doesn't write code itself; it plans the work,
  delegates it to agents that implement it, and brings the finished work back to you to check" 📣
  ([changelog](https://cursor.com/changelog/projects)).

## 2. Design system

### 2.1 Token architecture

The tokens are a StyleX `defineVars` block emitted as `:root, .ui-1lzgia1{…}` in
`workbench.glass.main.js`, with 773 distinct `--cursor-*` definitions ✅. **A small set of primitive colours
feeds a five-step alpha ladder** built entirely from `color-mix(in srgb, <hue> N%, transparent)`:
`-primary` is the hue itself, then `-secondary` 12%, `-tertiary` 8%, `-quaternary` 6% and `-quinary` 4%
(accent and git hues use 24 / 12 / 8%), with `-hover` = `color-mix(base 10%, hue)`. Neutrals are derived
from the foreground the same way (`--cursor-bg-active` base 16%, `--cursor-bg-focused` base 22%). There is
no hand-picked grey ramp ✅.

**Bridge to the IDE.** Under `body:not([data-cursor-glass-mode=true]) .monaco-workbench`, the glass
CSS re-points the same names at VS Code theme variables. Examples: `--cursor-blue:
var(--vscode-terminal-ansiBlue)`, `--cursor-added:
var(--vscode-gitDecoration-addedResourceForeground)`, `--cursor-text-primary:
var(--vscode-editor-foreground)`. As a result, one component library renders under any third-party
VS Code theme ✅.

### 2.2 Colour roles

| Role | Glass `:root` default | Cursor Dark theme | Cursor Light theme |
|---|---|---|---|
| Foreground / base | `#F0F0F0` | `#F0F0F0` | `#141414` |
| Editor surface | `#181818` | `#181818` | `#FCFCFC` |
| Chrome / sidebar | `#141414` | `#141414` | `#F3F3F3` |
| Accent / button | `#599CE7` | `#81A1C1` | `#2778C1` |
| Added | `#70B489` | `#70B489` | `#007041` |
| Removed | `#FC6B83` | `#FC6B83` | `#BE1744` |
| Modified / warning | `#F1B467` | `#F1B467` | `#A46700` / `#CD4500` |
| Danger / error | `#E34671` | `#E34671` | `#BE1744` |
| Success / green | `#3FA266` | `#3FA266` (ansiGreen) | `#007041` |

Sources: the theme files in `extensions/theme-cursor/themes/`. Cursor ships Dark, Dark High Contrast,
Dark Midnight, Light and Light Colorblind. No theme defines custom `cursor.*` keys; everything flows
through the CSS-variable bridge ✅.

> ⚠️ The static `:root` block holds dark values only. I did not trace how light primitives reach
> Glass at runtime. Several hues (`#81A1C1`, `#D08770`, `#BF616A`, `#A3BE8C`, `#EBCB8B`) are Nord
> palette values; that is my inference, and no vendor statement says so.

### 2.3 Scales, type, icons

| Scale | Values ✅ |
|---|---|
| Spacing `--cursor-spacing-*` | 4 px unit with **quarter steps**: `0-25`=1, `0-5`=2, `0-75`=3, `1`=4, `1-25`=5, `2`=8, `2-5`=10, `3`=12, `4`=16, `5`=20, `6`=24, `8`=32 … `20`=80. Mirrored negatives `--cursor-spacing-ne-*` |
| Radius | `none` 0 · `xs` 2 · `sm` 4 · `base` 6 · `lg` 8 · `xl` 12 · `2xl` 14 · `3xl` 16 · `4xl` 18 · `full` 9999 |
| Motion | `instant` 50 ms · `fast` 100 · `normal` 150 · `slow` 200 · `slower` 300 |
| Type (size/line) | `xs` 11/14 · `sm` 12/16 · `base` 13/18 (Glass sets base to `sm`) · `lg` 14–15/22–24 |
| Weight | normal **418** · medium 500 · semibold 600 (set in JS beside the platform font-stack code) |
| Shadow | One `--cursor-shadow-primary` (black 20%, or `--vscode-widget-shadow`) with 60% and 30% derivatives. `box-shadow-lg/xl` add `inset 0 0 4px #FFFFFF0D`, an inner highlight |
| Focus ring | `--glass-focus-ring-width` 1px, offset 2px, radius `sm` |

- **Fonts.** UI uses the system stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI'`, per-locale CJK
  fallbacks); **no brand sans is bundled**. Bundled: `out/media/jetbrains-mono-regular.ttf`, KaTeX ✅.
- **Icons.** `out/media/cursor-icons-16.woff2` is **"Cursor Icons 16" v0.1, 1,620 glyphs**: 644 `*-legacy`
  (codicon re-draws), 314 `*-filled`. Agent glyphs include `agents-swarm`, `infinity`, `bugbot`, `circles`,
  `list-todo-subtask`, `thinking-low/medium/high`, `threads-single`/`threads-parallel`,
  `shield-check/-question/-x`, `cloud-arrow-up/down`. `codicon.ttf` still ships for the IDE ✅.
- **Glass means literal translucency.** Glass-surface Appearance settings: `Hue` ("Choose a tint color"),
  `Intensity`, `Reduce Transparency` ("Replace translucent surfaces with opaque backgrounds"), `Reduce
  Motion`; `--glass-vibrancy-on/off-*-surface-background` tokens ✅. How it looks is ⚠️.

## 3. How harness primitives are rendered

### 3.1 Approval and permission

The run-mode table below comes from the enum `Tk` with label function `TH1` and description function
`EH1` ✅:

| Internal | Label (sandbox-backed variant) | Description |
|---|---|---|
| `ASK_EVERY_TIME` | `Ask Every Time` | `Ask for permission before running each operation` |
| `USE_ALLOWLIST` | `Allowlist` / `Allowlist (with Sandbox)` | `Automatically run operations after you approve them once` / `Tools will auto-run in a sandbox if possible, otherwise respect the allowlist or ask for approval` |
| `SMART_AUTO` | `Auto-review` / `Auto-review (with Sandbox)` | `Automatically run operations that Auto-review classifies as safe[, using sandboxing when possible]` |
| `RUN_EVERYTHING` | `Run Everything` / `Run Everything (Unsandboxed)` | `Automatically run all operations without asking for permission` |

- **The prompt-every-time mode is hidden.** The option builder adds `ASK_EVERY_TIME` only when it is
  already the current mode (`i===Tk.ASK_EVERY_TIME&&o.push(…)`). New users see three rungs ✅.
- **The containment level is in the label**: `(with Sandbox)` or `(Unsandboxed)` ✅.
- **"YOLO" survives internally**: the `Run Everything Mode Warning` dialog stores `doNotShowYoloModeWarningAgain` ✅.
- **Prompt strings:** `Allow this action?`, `Allow`, `Deny`, `Allow all`, `Always run`, `Always Run Selected`,
  `Add to allowlist`, `Stop command`, `Use Sandbox instead`; reason line (`ToolApprovalReasonStack.js`)
  `Not in allowlist:` / `Not in team allowlist:` ✅.
- **Pending states:** `Awaiting approval` / `terminal` / `edit` / `MCP tool approval`, `Awaiting plan review`,
  `A cloud agent is waiting for your approval.` **Admin locks:** `Run Mode Controlled by Team Admin (Sandbox
  Enabled)`, `Run Everything is disabled by permissions.json`, `Run Everything is not available in Ask mode.` ✅
- **Other gates:** `Read Access`, `Read Allowlist`, `Web Search Tool`, `Web Fetch Tool`,
  `Domain Allowlist`, and `Wait for MCP Authentication` ("otherwise skip prompts after 30 seconds") ✅.
- **Policy is written in plain English.** `permissions.json` takes sentences such as "Every AWS CLI
  command should go through approval first." (`allow_instructions` / `block_instructions`). The
  classifier currently runs on Claude 4.5 Haiku or GPT-5.4 Mini 📣
  ([run-modes](https://cursor.com/docs/agent/security/run-modes.md)).

> 📌 A classifier block goes **back to the agent first**. The agent can narrow the action or choose
> another path, and only an agent that still wants to proceed produces a human prompt. Vendor
> figures: about 4% of classified actions are blocked, and about 7% of Auto-review chats see at least
> one interruption 📣 (not verified). This is a two-hop approval, which contrasts with
> the single-hop request/response of [Codex app-server approvals](../docs/02-app-server-protocol.md)
> and the gate properties in [strands/07](../strands/07-security.md). See also
> [SYNTHESIS §2.1](../SYNTHESIS.md#21-approval-as-a-protocol-primitive) and
> [approval-gate](../ai-workflow/wiki/concepts/approval-gate.md).

> ⚠️ Cursor's own docs: "**Auto-review is not a security boundary.** The classifier can make
> mistakes." 📣

### 3.2 Autonomy modes

These are command registrations with icon and category `Mode` ✅:

| Label | Internal id | Icon |
|---|---|---|
| `Agent Mode` | `agent` | `infinity` |
| `Plan Mode` | `plan` | `list-todo` |
| `Ask Mode` | **`chat`** | `chat-bubble-question` |
| `Debug Mode` | `debug` | `bugbot` |
| `Multitask Mode` | `multitask` | `circles` |
| `Cycle Mode` | `Shift+Tab` | `refresh` |

- Also `Design Mode`, `Custom` modes, and flags `Add spec mode…` / `Add triage mode to composer modes` (unreleased ⚠️).
- **The agent can switch modes itself.** Strings: `Accept Mode Switch`, `Skip Mode Switch`, `User
  rejected the mode switch`. The setting `Auto-Approve Mode Transitions` reads: "Allow agent to
  switch to modes like Plan or Debug without asking. When off, Cursor asks first, **but skips if
  unanswered within 15 seconds**." ✅ An unanswered proposal defaults to *no*.
- **Model picker:** `Auto`, `MAX Mode` (`Max mode is required for cloud agents.`), `Use Multiple Models` with
  `Select model count` (`Nx`). Parameter icons: `fast`→`lightning`, `context`→`book-open`,
  `thinking`→`thinking-high`, `effort`/`reasoning`→`brain` ✅.

### 3.3 Plan and todos

- **The plan is an editable markdown document**: `Markdown Plan Editor`, `Start writing your plan...`,
  `Find in Plan`, `Review Plan`, `Approve this plan?`, `Build Plan`, `Start Plan Now`, `Spin up a
  new thread with this plan as context`, `Execute the plan across parallel subagents.` ✅
- **Todos sync into the plan file** (log strings "[ToolFormer] Failed to sync todo updates to plan file",
  "[PlanTabContent] Failed to build selected todos in new agent"). Tool description: `Keeps a running
  checklist of the steps the agent is working through on a larger task.` ✅

### 3.4 Tool-call transcript

- Paired progressive/past verbs ✅: `Reading`/`Read file`, `Editing`/`Edited`, `Running command`/`Ran command`,
  `Searching`/`Searched files|symbols|web|conversations`, `Grepping`/`Grepped`, `Thinking`/`Thought`,
  `Exploring`/`Explored`, `Calling MCP tool`/`Called MCP tool`, `Planning next moves`, `Working`/`Worked`.
- **`Tool Call Density` is an appearance setting** ("Adjust how much detail is shown for tool calls") ✅:

| Value | Label | aria description |
|---|---|---|
| `detailed` | `Detailed` | `Detailed, edits with diffs and shells with output` |
| `compact-shells` | `Diff Focus` | `Edits with diffs and compact shells` |
| `compact-ungrouped` | `Balanced` | `Compact edits and compact shells, not grouped` |
| `compact-grouped` | `Grouped` | `Compact grouped edits and shells` |
| `compact-all-grouped` | `Compact` | `Compact grouped tool calls` |

- Also `Breadcrumb` / `Island` styles and `agent-transcript-activity-muted-*` classes: tool activity is muted relative to prose ⚠️.

### 3.5 Diff and review

- **The vocabulary is Keep/Undo, not Accept/Reject**: `Keep`, `Keep All`, `Undo`, `Undo All`,
  `Review Changes`, `Review next file`, `Keep all changes`. `Keep` is `variant:"primary"`, and
  `Undo` is `outline`. **`Undo All` requires `Click again to confirm undo`**, a second click in
  place of a modal ✅.
- `Accept` / `Reject` survive for inline Tab suggestions and in telemetry (`Accept Partial Edit`,
  `Reject All Edits`, `Accepted Diff`) ✅.
- **Checkpoints:** `Restore Checkpoint`, `Discard all changes up to this checkpoint?`; limits such as
  `Cloud agent checkpoint restoration not yet supported` ✅. 📣 "Restoring a checkpoint reverts files only;
  it does not remove messages" ([overview](https://cursor.com/docs/agent/overview.md)).
- **Agent Review** (`Quick`/`Deep`, `/agent-review`, reads `BUGBOT.md`) and `Review Code with Bugbot` delegate review to an agent 📣 ✅.

> 📌 Keep/Undo treats the agent's edits as **already applied**, so the human decides whether to keep
> them. That is a different default from a proposal waiting for acceptance ⚠️ (inferred from the
> verbs and the IDE-only `Inline Diffs` setting).

### 3.6 Parallel and background work

- **Environments.** `Default Environment` ("Where new agents start by default": `last used`, `new worktree`, …);
  worktree retention via `Max Worktrees` / `Max Total Size (GB)` ✅.
- **Handoff verbs:** `Apply Changes Locally`, `Checkout Branch Locally`, `Move to cloud and keep working there`,
  `Convert to remote control`, `Steer from Phone`, and `Autopilot` ("keeps the pull request merge-ready by
  triaging review comments, resolving clear conflicts, and fixing CI in a loop") ✅.
- **Naming drift.** UI says `Cloud Agent` (62 strings); internals still say `background-composer` ✅.
- **`/multitask`** runs async subagents "instead of adding them to the queue" 📣 ([changelog 3.2](https://cursor.com/changelog/04-24-26)).

### 3.7 Status and attention

- **Status vocabulary:** `Running`, `Queued`, `Preparing`, `Completed`, `Failed`, `Canceled`,
  `Interrupted`, `Skipped`, `Idle`, `Errored`, `Ready`, `In Progress`, **`Needs Attention`**,
  `Unread` / `Mark as Unread`, `Continue Interrupted Agents` ✅.
- **Notifications:** `Show system notifications when Agent completes or needs attention` and
  `Play a sound when agents finish or need attention` ✅.
- **Errors** name the cause and a remedy: `Network access is locked by your admin. Skip this task or
  ask your admin to disable the lock.`, `Switch Model and Retry` ✅.
- **Delight:** `Give the Agent a Confetti Cannon`, under Appearance → Fun ✅.

### 3.8 Steering and queueing

- The setting "What sending a message while Agent is running does" takes the values `queue` and
  `agent-steering`. Strings: `Send Now`, `Steer`, `Steer without interrupting`, `Keep Queuing`,
  `Edit Queued Message`, `Manually Sent Messages from Queue`, `Interrupt` ✅.
- 📣 A steer message "is delivered at the agent's **next tool call** instead of cutting off work
  mid-action" ([overview](https://cursor.com/docs/agent/overview.md)).
- This is the same Queue/Steer split Aside uses ([Aside §5](../browser-agents/03-aside-design-ux.md)).

## 4. Stated design philosophy

- 📣 "Engineers are still micromanaging individual agents, trying to keep track of different
  conversations, and jumping between multiple terminals, tools, and windows… The new Cursor interface
  brings clarity to the work agents produce, **pulling you up to a higher level of abstraction, with
  the ability to dig deeper when you want**." ([blog: Meet the new Cursor](https://cursor.com/blog/cursor-3), 2026-04-02)
- 📣 "We will also continue to invest in the IDE **until codebases are self-driving**." (same post)
  In the artifact, `self-driving` is a real settings pane id (`cursor-settings-self-driving-prs`) ✅.
- 📣 "The easy answer is to ask the user before any action happens, but **asking for permission too
  often creates its own safety problem**. After enough repeated prompts, people stop reading
  carefully… [Auto-review] makes decisions around agent autonomy behave **more like a dial than a
  switch**." ([blog: Governing agent autonomy with Auto-review](https://cursor.com/blog/agent-autonomy-auto-review), 2026-06-11)
- 📣 "We did not want the classifier to become another approval prompt generator." (same post)

## 5. What is distinctive

1. **Two surfaces, one token system**: fixed in Glass, bridged to `--vscode-*` in the IDE; settings tagged `glass`/`ide`.
2. **Autonomy dial with containment in the label**, a hidden ask-every-time mode, and a classifier rung whose blocks go to the agent first.
3. **Keep/Undo** diff framing with an in-place click-twice `Undo All`.
4. **Five-level transcript density** as an appearance setting, beside tint, translucency and motion.
5. **Agent-proposed mode switches** that time out to *no*.
6. **A custom 1,620-glyph icon font** and a foreground-derived `color-mix` alpha palette.

## 6. Refutations and contradictions

- ❌ (partial) **"From scratch."** 📣 "With Cursor 3, we took that a step further by building this
  new interface from scratch, centered around agents." ([blog](https://cursor.com/blog/cursor-3)).
  The artifact bears this out for the React/StyleX/Base UI layer only. Glass is a second entry point
  on the VS Code workbench platform: editor parts, Monaco and the notification service all come from
  VS Code (§1.1).
- ❌ (stale docs) **Density levels.** 📣 The 3.4 changelog lists "Compact … Balanced … Detailed".
  The shipped build has five levels (§3.4).
- ❌ (docs contradict each other) **Queue/steer keys.** The same docs page says "Press Cmd+Enter to
  send immediately, bypassing the queue" and also "hit **Send now**, or press Enter twice… Press Tab
  to queue" ([overview](https://cursor.com/docs/agent/overview.md)). I did not check which binding
  is live in 3.22.7.
- ❌ (minor) **Build identity.** The download-URL sha is `…2268`, but `product.json` records commit
  `…2260`. The mismatch is one character, and I did not investigate it.
- Not a contradiction: the [run-modes](https://cursor.com/docs/agent/security/run-modes.md) docs list
  three modes and the code has four, because the fourth appears only for users already on it (§3.1).

## 7. What this means if you are building an agent client

- [ ] Name the **containment level** inside the autonomy label ("with Sandbox" / "Unsandboxed"), not
      only in a separate setting.
- [ ] Put a **cheap reviewer between the allowlist and the human**, and route its denials back to the
      agent as feedback before they become prompts. Log how often humans are actually interrupted.
- [ ] Decide whether edits are **proposals** (Accept/Reject) or **faits accomplis** (Keep/Undo), and
      make the verbs match. Confirm bulk-undo with an in-place second click, not a modal.
- [ ] Let users set **transcript density**. Group and compact tool calls by default, and keep
      diffs and shell output one click away.
- [ ] Make the plan an **editable file** that todos sync into, with "build this plan" and "build
      these todos in a new agent" as actions.
- [ ] Separate **queue from steer** explicitly, and deliver steers at tool-call boundaries.
- [ ] If the agent can change its own mode, make an unanswered proposal **time out to no**.
- [ ] Fire OS notifications for "finished" and `Needs Attention`, and keep an `Unread` state per agent.

## 8. Open questions

- What Glass vibrancy and tint look like, and whether they are gated on macOS. The Linux build ships
  the tokens anyway. ⚠️ Visual.
- How light-theme primitives are injected into Glass at runtime; the static `:root` holds dark
  values only.
- Whether the `spec` and `triage` modes are live behind server flags.
- Which queue/steer keybinding model is the default in 3.22.7.
- What `out/vs/workbench/workbench.anysphere-ui-automations.js` (8.9 MB) does. I did not examine it;
  strings mention a smoke-test driver.
- How approval cards are laid out in the transcript (placement, colour, keyboard hints). ⚠️
