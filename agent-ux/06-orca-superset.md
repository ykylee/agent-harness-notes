# 06. Orca and Superset — orchestrators that wrap other vendors' agent TUIs

> Products: **Orca** (Stably, MIT) — `stablyai/orca` @ `da6d483` (2026-09-26; `package.json` 1.4.197,
> latest git tag `v1.4.212`). **Superset** (Elastic License 2.0, source-available) —
> `superset-sh/superset` @ `2370f60` (2026-09-25; `apps/desktop` 1.30.2, tag `desktop-v1.30.2`).
> Both obtained by shallow clone; the source is public, so no installer was needed.
>
> Method: static reading of source, in-repo docs sites (`docs/site/content/docs/` in Orca,
> `apps/docs/content/docs/` in Superset), and in-repo design and plan documents. No display —
> **nothing was seen rendered**; colours, glyphs and motion are read from code.
>
> Researched 2026-09-26. Dominant grade: ✅ from source; 📣 for docs; three ❌ (Orca docs vs Orca code).
>
> **GUI pass 2026-09-27 (macOS, same build, `orca computer` screenshots; passive — no agent was run), Orca 1.4.209, no workspace open.** ✅ Sidebar = projects → worktrees, each worktree with a host badge
> (`Local Mac` or a remote host name) and a status dot; a bottom status bar with **per-provider usage meters**. The
> agent states (`blocked`/`waiting`, §4.7) and the wrapped-agent approval default (§4.1) need a running agent and were not
> seen. The UI face looks like Geist but a screenshot cannot prove the font ⚠️.

Both are **agent orchestrators**. They do not own an agent loop. They run third-party CLI agents
(Claude Code, Codex, Gemini, Grok, Cursor, Droid, Pi…) in their own PTYs, one git worktree per
task, and build a fleet UI around them. That is the key contrast with first-party clients
([02](02-claude-desktop.md), [03](03-openai-codex-chatgpt.md)): the host must **infer** what an
agent is doing, and to change what the agent does it must **act back into a TUI it did not
write**. §3 is about that problem.

## 1. What they are and how they are built

| | Orca | Superset |
|---|---|---|
| Runtime | Electron 43.7.0, React 19, electron-vite | Electron 41.10.3, React 19, Turborepo/bun monorepo |
| Styling | Tailwind v4, shadcn `new-york-v4` over `radix-ui` (`components.json`) | Tailwind v4, shadcn over `@radix-ui/*` (`packages/ui`) plus Vercel **`ai-elements`** and `streamdown` |
| Terminal | xterm.js `6.1.0-beta`; README "Ghostty-class terminals with WebGL rendering" | xterm.js `6.1.0-beta` with the webgl, image, ligatures and serialize addons; persistent `pty-daemon` |
| Editor / diff | Monaco (`@monaco-editor/react`), Monaco-based diff | CodeMirror 6, `@pierre/diffs`, `@pierre/trees` |
| Panes | own tab-group splits | `react-mosaic-component` via `@superset/panes` |
| Agent SDKs bundled | `@anthropic-ai/claude-agent-sdk` 0.3.251 (structured sessions) | `@anthropic-ai/claude-agent-sdk` 0.3.201 plus a Codex app-server RPC client (`packages/chat-runtime/src/harness/`) |
| Platforms | macOS, Windows, Linux; iOS and Android companion apps | macOS primary; Linux AppImage "experimental"; no Windows build; iPhone app requires Pro |

**Layout.** Both use the genre's three-column shape ✅: projects → worktrees with per-row agent
state on the left; tabs and splits (terminal · editor · diff · browser · chat) in the centre;
source control, checks and files on the right.

- **Orca** ✅: `components/Sidebar.tsx` holds worktree cards with their own token family
  (`--worktree-sidebar-*`). There is a titlebar tab strip (`TerminalTitlebarTabs.tsx`), tab-group
  splits with a dedicated divider token that meets ≥3:1 contrast, and `right-sidebar/` (file
  explorer, `ChecksPanel`, "AI Vault" of past sessions). The jump palette (`WorktreeJumpPalette`)
  uses cmdk. The experimental **Agent Dashboard** is a kanban with columns `Needs You` · `Working` ·
  `Done` · `Idle`; Idle is hidden by default, and the board can run in-window or pop out
  (📣 [agents-sessions](https://www.onorca.dev/docs/model/agents-sessions)).
- **Superset** ✅: pane types are registered in `usePaneRegistry` (Terminal, FilePane, DiffPane,
  ChatV3Pane, Browser). The sidebar row carries an "activity strip" of running agents and open
  ports. The board columns are `Idle` · `Working` · `Needs attention` · `Needs review` · `Merged` ·
  `Deleted`, in a "Fixed Linear-style workflow order — never user-reorderable"
  (`v2-workspaces/utils/deriveBoardColumn.ts`).
- In both, **the agent is a terminal tab, not a chat surface.** Chat is optional: Orca's "Chat UI"
  is behind Settings → Experimental; Superset's ChatV3Pane is one pane type among several.

> 📌 Superset's board **fuses agent state with PR lifecycle**. An open or draft PR puts the
> workspace in `Needs review`, a merged PR in `Merged`, and a permission prompt or failure in
> `Needs attention`. Orca's dashboard columns are agent state only; PR state is a filter there.
> Superset's latest commit (#7872) also turned the per-workspace "agents chip" **off by default**.
> The trend is to subtract per-agent detail from the workspace row.

## 2. Design system

### 2.1 Colour tokens

Orca — `src/renderer/src/assets/main.css` (canonical per `docs/STYLEGUIDE.md`) ✅:

| Role | Light | Dark | Note |
|---|---|---|---|
| background / foreground | `#fff` / `#0a0a0a` | `#0a0a0a` / `#fafafa` | shadcn neutral as hex |
| primary | `#171717` | `#e5e5e5` | no brand hue in the chrome |
| muted-foreground | `#737373` | `#a1a1a1` | |
| border | `#e5e5e5` | `rgb(255 255 255 / .07)` | |
| destructive | `#e40014` | `#ff6568` | |
| editor-surface | `#ffffff` | `#1e1e1e` | matches VS Code dark |
| worktree-sidebar | `#f5f5f5` | `#2a2a2a` | its own family, not `--sidebar` |
| **agent-question** | `orange-600` | `orange-500` | "Orange, not amber: it has to stay separable from working-yellow at a glance." |
| ai-action-accent | `violet-500` | `violet-400` | the only "AI" hue |
| status-success / warning | `#15803d` / `#ca8a04` | `#86efac` / `#eab308` | warning = "Needs-attention state that is not an error" |
| workspace-status done / review / progress | `#c7a594` / `#16a34a` / `#d4a300` | same | "same hue in both themes so a status keeps its identity" |
| git-decoration-* | VS Code palette | VS Code palette | "so users transferring from VS Code aren't surprised" |
| `--orca-security-*` | full neutral set | full neutral set | re-pinned by `.plugin-security-chrome` (below) |

> 📌 `.plugin-security-chrome` resets every core token to the `--orca-security-*` values: "plugin
> themes may style the app, but provenance and consent must retain host-owned contrast so a pack
> cannot disguise a trust decision." It is the only theming-proof consent chrome found in this
> study.

Superset — `packages/ui/src/globals.css`, `apps/desktop/src/renderer/globals.css`,
`packages/shared/src/themes/built-in/*.ts` ✅:

| Role | Default "Dark" (`ember.ts`) | Light | Note |
|---|---|---|---|
| background / foreground | `#151110` / `#eae8e6` | `#f9f9fa` / `oklch(0.145 0 0)` | "Warm dark theme inspired by the Figma start screen design" |
| card / popover | `#201E1C` | `oklch(1 0 0)` | |
| muted / muted-fg | `#2a2827` / `#a8a5a3` | shadcn | |
| brand / highlight | **`#e07850`** (terracotta, also `--sidebar-primary`) | `oklch(0.646 0.222 41.1)` | search matches reuse it |
| destructive / warning / success | `#cc4444` / `#e5c07b` / `#5fb37f` | oklch | |
| row fills | `--fill-hover` = fg 7%, `--fill-selected` = fg 10% | 4% / 6% | `color-mix` washes that track any theme |

`packages/ui` itself is **stock shadcn neutral in oklch**. The desktop theme store rewrites the
variables at runtime; `globals.css` holds only pre-hydration fallbacks. The built-in themes are
Dark, Light, Vellum, Monokai, Catppuccin Latte and Solarized Light, and they are JSON-importable
📣 ([custom-themes](https://docs.superset.sh/custom-themes)).

### 2.2 Type, shape, motion, icons, components

| | Orca ✅ | Superset ✅ |
|---|---|---|
| Sans | **Geist** variable woff2 bundled (100–900); STYLEGUIDE: "never `Inter` or system sans" | ⚠️ none bundled; probably Tailwind's system `font-sans` |
| Mono | system stack (SF Mono → Cascadia → Menlo …); bundled **Symbols Nerd Font** for PUA glyphs in agent TUIs | SF Mono via a custom `superset-font://` protocol; ⚠️ no font files in the repo |
| Sizes | 11 / 12 / 13 / 14 px; 11 px uppercase labels at 600 weight and 0.05em tracking; body tracking 0.01em | Tailwind defaults |
| Radius | `--radius: 0.625rem`, others as multipliers (0.6×, 0.8×, 1.4×) | `0.625rem` with shadcn's ±2/4 px |
| Elevation | exactly three levels; `--shadow-floating: 0 10px 24px rgb(0 0 0/.18)`; "Don't add a fourth level." | shadcn defaults |
| Motion | 100–200 ms; house easing `cubic-bezier(0.16,1,0.3,1)` at 180 ms; reduced motion respected everywhere | `framer-motion`/`motion`; `animate-ping` for attention |
| Icons | `lucide-react` only ("Don't import a second icon library") | `lucide-react` plus `react-icons` (agent logos) |
| Components | shadcn wrappers in `components/ui/` (`data-slot`, CVA), cmdk, sonner | shadcn, cmdk, sonner, **ai-elements** (`confirmation`, `plan`, `queue`, `tool-call`, `reasoning`, `braille-spinner` …) |

Orca's STYLEGUIDE also sets feedback by duration ✅: nothing under 100 ms, disabled state up to
1 s, spinner 1–3 s, stage labels beyond, with visible loading deferred ~200 ms for SSH.

## 3. Three levels of control over a foreign agent

A first-party client renders its own event stream: the approval is an item in a protocol it
defines ([Codex app-server](../docs/02-app-server-protocol.md)). An orchestrator has no such
stream. It has three options, and each adds fidelity and coupling:

| Level | What the host does | Orca | Superset |
|---|---|---|---|
| **1. Observe** | infer state from side channels | hooks, in-band OSC 9999, title glyphs, silence-based idle | hooks only |
| **2. Drive by keystrokes** | synthesise input into the vendor TUI | Chat UI card: `Allow` → writes `1`, `Deny` → writes `ESC` | not found |
| **3. Replace with the vendor API** | run the agent through its SDK or app-server; render natively | structured sessions via the Claude Agent SDK (`canUseTool`) | ChatV3Pane: Claude Agent SDK and Codex app-server |

### 3.1 Observe — hooks written into the agent's own config

The shared mechanism ✅: (1) the PTY environment carries identity — Orca `ORCA_PANE_KEY` /
`ORCA_AGENT_HOOK_ENDPOINT`; Superset `SUPERSET_TERMINAL_ID`/`TAB_ID`/`PANE_ID`/`WORKSPACE_ID`, plus
`SUPERSET_AGENT_ID` from PATH-shim wrappers in `~/.superset/bin/<agent>`. (2) Hooks are written into
the agent's **user-global** config (`~/.claude/settings.json`, `~/.codex/hooks.json`,
`~/.factory/settings.json`, Kimi TOML…): 16 agents in Orca's
`src/main/agent-hooks/managed-agent-hook-registry.ts`, Superset's in
`packages/agent-setup/src/agent-wrappers-*.ts`. (3) The script no-ops outside the app's terminals —
Superset's `notify-hook.template.sh`: `[ -n "$SUPERSET_TERMINAL_ID" ] || [ -n "$SUPERSET_TAB_ID" ] || exit 0`,
"the agent-supplied payload alone must never dispatch." (4) The endpoint is re-read on every call,
since a live PTY's env can't change (Orca `{userData}/agent-hooks/endpoint.env`; Superset
`~/.superset/host/<orgId>/manifest.json`). (5) Every vendor dialect — Claude's
`UserPromptSubmit`/`PreToolUse`/`PostToolUse`/`PermissionRequest`/`Stop`/`StopFailure`/`Subagent*`/`PostCompact`,
Codex's `exec_approval_request`/`request_user_input`, Grok's lowercase `notification`, Pi's
`session_start` — is normalised into one small state set.

Superset stops there ✅. `packages/shared/src/agent-status.ts` orders
`ACTIVE_AGENT_STATUSES = ["review","working","failed","permission"]` **by urgency** and maps
`Start→working`, `PermissionRequest→permission`, `Failed→failed`, **`Stop→review`**. A workspace
shows the maximum over its panes. The hook script prefers a missed event to a wrong one: "Never
default to "Stop" on parse failure — silent drop is safer than a false completion notification."
It drops foreign-harness replays: cursor-agent replays `~/.claude/settings.json`, and a nested
`codex exec` fires Codex's hooks inside a Claude terminal. There is no title or output parsing for
agent state; OSC 133 and OSC 777 are used only for shell readiness (I searched host-service,
pty-daemon and the renderer). Its docs admit the limits 📣
([agent-status](https://docs.superset.sh/agent-status)): "status only works for agents launched
through Superset"; "Some agents don't emit a waiting-for-input signal yet". A manual `Clear Status`
exists for indicators that stick.

Orca adds more evidence and ranks it ✅:

- `src/shared/agent-status-types.ts` says status "comes from hooks … — never inferred from terminal
  titles; a narrow interrupt fallback synthesizes a final `done`". States are `working` · `blocked`
  · `waiting` · `done`, plus `workingMode: 'monitoring'` and per-subagent child rows.
- **In-band OSC 9999.** `\x1b]9999;{json}\x07` carries a full status payload inside the PTY stream
  (`src/shared/agent-status-osc.ts`). It is parsed and stripped in main and joins the HTTP hooks on
  one `applyNormalizedStatus` path. Relayed, SSH and plugin-based agents report this way.
- **Title glyphs** are a lower-authority channel (`src/shared/agent-title-core.ts`). Claude idle is
  `✳`. Gemini uses `✦` for working, `✋` for permission and `◇` for idle. Braille spinners
  (`U+2800–28FF`) and `◐–◓` mean working. Word-boundary regexes match
  `working|thinking|running` and `ready|idle|done`. A stale working title clears after 3 s.
- **Evidence ranking** (`src/main/runtime/tui-idle-evidence.ts`): "a thinking TUI and a finished
  TUI are both silent, so the absence of a working marker can never prove completion". Tier 1 is
  an explicit idle marker (POSITIVE). Tier 2 is a fresh OSC 9999 status (VETO): "The agent's own
  account of itself outranks anything inferred." Tier 3 is sustained silence (ABSENCE).
- **Store doctrine** (`docs/reference/agent-status-store.md`): "The execution host owns agent
  status, in one store, and every reader subscribes to it. … Precedence is decided once, at write
  time, with provenance recorded on the row." The same doc records an audit that found **six
  producers and three consumers**, with three copies of one row inside the main process. That is
  the complexity cost of level 1.

> ⚠️ **Observing costs a global side effect.** Superset's public post-mortem
> (`HOOKS_INVESTIGATION.md`) found its hooks firing in *non-Superset* Droid sessions. Droid, Codex,
> Mastra, Cursor, Gemini and Copilot configs had received unguarded absolute paths. Even a guarded
> hook stays visible, because "tools that render hook execution in their UI (as Droid does) will
> still show a 'Hooks' line". The remediation is marked implemented. Both products also print
> `{}` first from the hook, because "Claude-compatible permission hooks fail closed on empty
> stdout (#14818)" (Orca `src/main/claude/hook-script.ts`). The observer runs inside the agent's
> permission path.

### 3.2 Drive by keystrokes — puppeting the vendor's menu

When a hook reports a `PermissionRequest` for a PTY session, Orca's optional Chat UI renders a
native card ✅ (`components/native-chat/native-chat-interactive-prompt.ts`):

| Card element | Value |
|---|---|
| Title | `Allow {{value0}}?` (the tool name from the hook payload) |
| Detail | the hook's `summary` |
| Options | `Allow` → sends `"1"` · `Deny` → sends `ESC` (`String.fromCharCode(27)`) |
| Icon | lucide `ShieldQuestion`; "The first option gets the primary styling" |

The file header: "PTY callers supply literal replies while structured callers supply journal
option IDs." The prompt's *content* comes from the hook payload (`tool_name`, `tool_input`), not
from reading the screen. The *answer* is a keystroke aimed at the vendor TUI's own menu.

> ⚠️ I found no guard tying `1` to the vendor's current menu order. If a CLI reorders its options,
> the card sends the wrong answer silently. Grade: inferred risk, not observed.

Orca's Chat UI is also a **transcript decoder** for PTY sessions: it reads the agent's own JSONL
session files (`src/main/native-chat/transcript-line-decoders-{claude,codex,grok,omp}.ts`). 📣
[native-chat](https://www.onorca.dev/docs/agents/native-chat): "The terminal remains the source of
truth; Chat UI is a structured transcript + composer for the same PTY."

### 3.3 Replace with the vendor API — render your own items

Superset ✅ went this way for chat. ChatV3Pane has a first-party item protocol
(`packages/chat/src/protocol/items.ts`) fed by programmatic harnesses, not the TUI:

- **Claude via the Agent SDK** (`chat-runtime/src/harness/claude/claudeAdapter/claudeAdapter.ts`):
  `permissionMode: "default"`, `canUseTool → requestApproval`, **`settingSources: []`**.
- **Codex via `app-server` RPC**, with modes `Read Only` · `Auto` · `Full Access`
  (`codexModes.ts`). The default is `Auto`, which is `approvalPolicy:"on-request"` with
  `sandbox:"workspace-write"`.
- **Item kinds**: `user_message` · `agent_message` · `reasoning` · `tool_call` · `plan` ·
  `approval_request` · `notice`. `ToolKind` is `read|edit|delete|move|search|execute|think|fetch|other`.
  ⚠️ That matches ACP's tool kinds, consistent with the plan's "start from ACP v2's shapes".
- **Decisions**: `accept` · `accept_for_session` · `decline` · `cancel` · `option`. This is the
  same four-way ladder as Codex's app-server ([docs/02](../docs/02-app-server-protocol.md)).

Orca ✅ has the same path for Claude in **structured sessions**
(`src/main/claude/claude-stream-json-connection.ts` imports `CanUseTool` from the Agent SDK). Orca
spawns the Claude child itself so it keeps its own kill ladder.

> ⚠️ `settingSources: []` would make Superset's chat-pane Claude load no user or project settings,
> which probably includes `CLAUDE.md` and user hooks. Not verified at runtime.

> 📌 Superset's internal design synthesis (`plans/chat-ui-greenfield-research.md`, 2026-08-04)
> argues for level 3 as an industry convergence: "agent harness(es) → normalize (per-harness
> adapter) → ONE semantic item vocabulary → durable append-only event spine". It adds: "Approvals
> are items, with rich decision enums. Bound to the transcript row that already exists (not a
> detached modal)". This is the same conclusion as [SYNTHESIS §2.1](../SYNTHESIS.md) — approval as
> a protocol primitive — reached from the wrapper side.

## 4. How harness primitives are rendered

### 4.1 Approval / permission

| | Orca | Superset |
|---|---|---|
| Terminal agents (default) | none: launched with bypass flags (§4.2) | Claude, Codex and Grok bypassed; the others show their own TUI prompt |
| Terminal agents (manual mode) | the vendor's TUI prompt, plus the optional card `Allow {tool}?` [`Allow`][`Deny`] (§3.2) | the vendor's TUI prompt; the workspace is flagged `permission` |
| Chat / structured | SDK `canUseTool` | `ApprovalRow`: `Allow` (primary) · `Allow for session` · `Deny` (outline); vendor-supplied `options` shown as outline buttons instead |
| Pending look | card plus composer takeover (`onCancel` = "Cancel the active provider turn") | `border-warning/50 bg-warning/5` |
| After the answer | card clears | badge: `Allowed` · `Allowed for session` · `Denied` · `Canceled`; `Expired` when stale |

Scope ladder in Superset ✅: once (`accept`), this session (`accept_for_session`), deny and continue
(`decline`), deny and stop the turn (`cancel`). Orca's PTY card has two rungs only, because the TUI
menu behind it is what actually decides.

### 4.2 Autonomy modes

- ✅ **Orca launches every supported agent in bypass mode by default.**
  `src/shared/tui-agent-permissions.ts` sets `YOLO_TUI_AGENT_ARGS`, which is re-exported as
  `DEFAULT_TUI_AGENT_ARGS`:

  | Agent | Flag |
  |---|---|
  | claude | `--dangerously-skip-permissions` |
  | codex | `--dangerously-bypass-approvals-and-sandbox` |
  | gemini, cursor, copilot, kimi, muse, hermes | `--yolo` |
  | amp | `--dangerously-allow-all` |
  | grok | `--permission-mode bypassPermissions` |
  | devin | `--permission-mode bypass --respect-workspace-trust false` |
  | droid | `--auto high` |
  | goose | `GOOSE_MODE=auto` (env) |

  The Agent Permissions setting reads `Yolo` / `Manual`, or `mixed` when per-agent overrides
  differ. Onboarding shows `Yolo / Dangerously skip permissions`, with the tooltip
  `Skip permission checks for agents for less interruptions`.
- ✅ **Superset is mixed, and it walked some defaults back.** In
  `packages/shared/src/builtin-terminal-agents.ts`, Claude and Codex are bypassed (Codex adds
  `--dangerously-bypass-hook-trust`), as are `grok --always-approve`, `hermes chat --yolo`,
  `devin --permission-mode dangerous` and `kiro-cli chat --trust-all-tools`. But the file also has
  `gemini --approval-mode=auto_edit`, `copilot --allow-tool=write` and `agy --mode accept-edits`,
  and plain `amp`, `opencode`, `cursor-agent`, `droid`. `agent-permissions-migration.ts` records
  that pre-#3546 builds seeded bypass defaults "before we swapped in safer ones". The chat pane is
  safer still: Claude `permissionMode:"default"`, Codex `Auto`.

> 📌 In both products **the fleet UI assumes "needs you" is rare**. Launch flags take permission
> prompts out of the loop, so the attention channel mostly carries questions and completions. The
> approval-card UI mainly serves Manual mode or the chat pane. See
> [strands/07](../strands/07-security.md) for why a bypass flag plus a worktree is not a gate.

### 4.3 Plan / todos

Orca ✅ `NativeChatTaskList`: `Tasks`, `{{completed}} of {{total}} tasks completed`, `In progress` /
`Pending` / `Completed`; summary `Updated the plan`. Superset ✅ `PlanRow`; the `plan` item's entries
are `pending`/`in_progress`/`completed`, replaced wholesale.

### 4.4 Tool-call transcript

- Orca ✅ collapses runs into summaries with present and past forms: `Reading {{n}} files` →
  `Read {{n}} files`, `Running 1 command` → `Ran 1 command`,
  `Ran {{commandCount}} commands and used {{toolCount}} tools`, `Searched the web {{n}} times`.
  The turn header reads `Working for {{t}}` → `Worked for {{t}}`. Details: `exit {{code}}`, `Copy diff`,
  `Diff truncated`.
- Superset ✅ `ToolCallRow` with status `running`/`completed`/`failed`/`declined`/`canceled`,
  `exit {code}` and `Output truncated`. Its research doc: "The backend ships semantics, not raw
  payloads … ("Read foo.ts", not `sed -n '1,50p' foo.ts`)".

### 4.5 Diff / review

- Orca 📣 [annotate-ai-diff](https://www.onorca.dev/docs/review/annotate-ai-diff): a gutter `+` or
  the `c` key adds a comment, and Cmd-Enter saves it. `Send to agent` composes one line-anchored
  batch and opens a `Send notes to` menu, where you pick an existing agent or start a new one.
  "Why batch? Sending comments one at a time causes the agent to swing back and forth." Comments
  stay pinned after the revision so you can verify the fix.
- Superset 📣 [README](https://github.com/superset-sh/superset): "select diff lines, and send
  feedback to a running or new agent session. Posting to GitHub is optional." The diff viewer is
  `@pierre/diffs` plus CodeMirror.
- Both ship **Design Mode** 📣: click an element in the embedded Chromium browser and its
  HTML/CSS (Orca adds a cropped screenshot) goes into the agent prompt.

### 4.6 Parallel and background work

Orca ✅: `workingMode:'monitoring'` → `Monitoring background tasks` (yellow `Activity`), with `Stop` /
`Stop background tasks`; subagents as indented child rows; worktree creation runs in the background
with a progress row. Superset ✅: a per-terminal subagent roster; subagent events "must not drive
terminal-level agent status"; a workspace shows the highest status over its panes.

### 4.7 Status and attention

| State | Orca `AgentStateDot.tsx` ✅ | Superset `StatusIndicator.tsx` ✅ |
|---|---|---|
| working | **yellow-500 ring spinner** (CSS; phase-synced) | **amber-500 dot, static**, `Agent working` |
| needs you | **orange `MessageCircleQuestion`**, `Waiting for input` / `Needs attention` | **yellow-500 dot, pulsing** (`animate-ping`), `Needs input` |
| done | emerald `CircleCheck` (dashboard) / emerald dot (sidebar), `Done` | **green dot**, `Ready for review` |
| failed / blocked / interrupted | red dot, `Blocked` / `Interrupted` / `Failed` | red dot, pulsing, `Agent failed` |
| idle | `neutral-500/40` dot, `Idle` | no indicator |
| stale | amber `CircleDashed`, `No recent update` | — (manual `Clear Status`) |

- **Urgency channel.** Orca encodes it in **hue**: orange for questions, deliberately apart from
  the yellow working spinner. Superset encodes it in **motion**: only the states that need a
  person pulse.
- Orca's comment on its two glyphs: "one for *who* (agent icon) and one for *what state*".
- **Spinner cost** ✅: Orca's spinner is one keyframe of `86400s steps(1036800)`, so rotation stays
  on the compositor. `animation.startTime = 0` phase-syncs every spinner.
  `docs/reference/spinner-rendering-performance.md` records the typing stalls this fixed (#12359).
- **Notifications** 📣: Orca ([notifications](https://www.onorca.dev/docs/notifications)) — finished
  pings (system, sound, worktree chip), a header bell inbox with `Mark unread`, Dock badge, ten
  sounds or a custom file; ✅ `suppressWhenFocused`. Superset ([agent-status](https://docs.superset.sh/agent-status))
  — finished/waiting sounds and a Dock badge for workspaces that "need your attention".

### 4.8 Steering, queueing, errors

- Orca: the composer sends or stops a turn; model / thought-level / mode pills, with the Claude model
  list taken "from the installed Claude CLI on that host" 📣. An exited agent shows a red dot and a
  `Restart` chip 📣; the STYLEGUIDE puts transient failures in toasts and persistent ones inline ✅.
- Superset ✅: protocol commands `steer`, `cancelTurn`, `setMode`, `setModel`, `setConfigOption`;
  queued messages render `Queued`; failures `Failed to send` + `Retry`. Session states: `starting` ·
  `running` · `awaiting_input` · `idle` · `not_loaded` · `offline` · `dead`.

## 5. Stated design philosophy

- 📣 Orca [README](https://github.com/stablyai/orca): "The AI Orchestrator for 100x builders. Run
  Codex, ClaudeCode, OpenCode or Pi side-by-side — each in its own worktree, tracked in one place."
  And: "Works with any CLI agent — if it runs in a terminal, it runs in Orca."
- ✅ Orca `docs/STYLEGUIDE.md` @ `da6d483`: "The visual identity is monochrome and quiet — neutral
  grays carry the chrome, color is reserved for state … The product spends most of its time hosting
  other people's tools (Monaco, xterm, Markdown previews), so Orca's own UI should recede and frame."
- ✅ Same file: "UI copy must not overclaim. Never imply the app has taken an action, made a
  decision, or observed a fact unless the code has real state or result data to support it."
- 📣 Orca [What is Orca?](https://www.onorca.dev/docs): "designed for people who already write code
  for a living and want to use AI as leverage — not as a replacement. It assumes you read diffs,
  care about commits, and keep a worktree tidy."
- 📣 Superset [The Superset Model](https://docs.superset.sh/superset-model): "Superset has one mental
  model: delegate in workspaces, integrate through branches and PRs." And: "It never touches model
  traffic: prompts and tokens go directly from the agent CLI to your provider, on your own accounts."
- 📣 Superset [README](https://github.com/superset-sh/superset): "Worktrees separate working files;
  they do not sandbox processes or prevent merge conflicts."

## 6. What is distinctive

1. **Three levels of control** (§3): Superset observes for status only and moved chat to vendor
   APIs; Orca invests in all three, including a keystroke bridge.
2. **One hue per meaning across every surface.** Orca's `--agent-question` has a single component,
   `AgentQuestionIcon`, "so they never drift apart". Superset's `STATUS_CONFIG` is one lookup table.
3. **The UI can admit ignorance** (Orca). The `unverifiable` state "asserts nothing about the agent,
   only about what Orca last heard"; hydrated rows are stamped `restoredUnconfirmed`.
4. **Consent chrome that plugin themes can't restyle** (Orca `--orca-security-*`).
5. **Completion is named for the human's next step** (Superset `Stop → review`, `Ready for review`,
   and a board that merges agent-done with PR-open).
6. **Review notes go back to the agent as one batch**, with a stated rationale (Orca).
7. **A companion phone app as the forcing function**: both run a remote control of desktop PTYs,
   which drove Orca's single status store and Superset's rewrite around an item and event spine.

## 7. Refutations and contradictions

- ❌ **Glyph colour.** Orca's
  [agents-sessions](https://www.onorca.dev/docs/model/agents-sessions) says "Amber question mark —
  waiting on you". `main.css` defines `--agent-question: var(--color-orange-600)` with the comment
  "Orange, not amber". A code comment in `agent-hook-listener/providers/claude-events.ts` also says
  "amber attention".
- ❌ **Detection source.** The same docs page says "State is detected from the terminal's OSC title
  sequence and agent hooks", with lifecycle step "Work — OSC titles update state". The
  `agent-status-types.ts` header says "never inferred from terminal titles". Both are partly
  right: the authoritative store takes hooks and OSC 9999, while title glyphs drive the older
  sidebar indicator, idle waits and notifications. Neither text describes both channels.
- ❌ **Is the worktree a sandbox?** agents-sessions: "The intent is that the worktree itself is the
  sandbox". [supported](https://www.onorca.dev/docs/agents/supported): "A worktree is an isolated
  checkout, not a security sandbox … Choose Manual … unless you intentionally trust the agent and
  the task." The code follows the first page's *behaviour*: bypass is the default.
- ⚠️ **Guarded hooks.** Superset's `HOOKS_INVESTIGATION.md` lists Codex, Droid and others as
  unguarded and marks the remediation implemented. The current Codex test shows the guarded
  command; I did not audit every agent's writer.
- ⚠️ **`blocked` vs `waiting`** (Orca). The Pi-family mapper sends an ask tool to `blocked`, while
  Claude's mapper sends it to `waiting`. `AgentStateDot` renders `blocked` as a red dot and
  `waiting` as the orange question, so the same human wait may look different by provider.

## 8. What this means if you are building an agent client

- [ ] If you wrap agents you don't own, **rank your evidence**. Silence is not completion, and the
      agent's own report outranks inference (Orca `tui-idle-evidence.ts`).
- [ ] When a hook payload is ambiguous, **drop it rather than claim completion** (Superset
      `notify-hook`).
- [ ] Guard every globally installed hook with an app-only environment check, and expect it to stay
      visible in other sessions anyway.
- [ ] Hooks sit in the permission path: print a valid empty response first, or you fail closed.
- [ ] Don't send approvals by keystroke without pinning the vendor menu. Prefer level 3: the
      vendor SDK or app-server with typed decisions ([docs/02](../docs/02-app-server-protocol.md)).
- [ ] Give approvals a scope ladder (`once` / `session` / `decline` / `cancel`) and render the
      answered state on the same row.
- [ ] Separate "needs you" from "working" on at least one channel: hue (Orca) or motion (Superset).
- [ ] Provide a state for "no recent evidence" instead of defaulting to idle or done.
- [ ] Keep consent and provenance chrome immune to user or plugin theming.
- [ ] If your default is bypass, say plainly in the UI that a worktree is not a sandbox. See
      [approval gate](../ai-workflow/wiki/concepts/approval-gate.md) and
      [strands/07](../strands/07-security.md).
- [ ] Name completion after the next human action ("Ready for review"), and let PR state feed the
      same board.

## 9. Open questions

- Visual: spacing, density, glyph sizes (Orca 2.5–3 px boxes, Superset 1.5 px dot) and animation
  feel were not seen rendered. Superset's rendered sans and the source of `superset-font://` SF Mono
  are unknown.
- Does Orca's `Allow` = `1` still match each vendor's permission menu? Is there a version check?
- Does Superset's `settingSources: []` exclude `CLAUDE.md` and user hooks from chat-pane sessions?
- Which Superset surfaces still run the older mastra/ACP chat stacks the ship plan keeps alive?
- Orca `package.json` (1.4.197) lags the release tags (v1.4.212); which build matches `main`?
