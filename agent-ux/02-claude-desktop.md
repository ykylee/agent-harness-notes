# 02. Claude Desktop — Chat, Cowork and Code in one Electron shell

> Product: Anthropic **Claude Desktop 2.9939.2**, including the Chat, Cowork and Code tabs and the agent surfaces they host (Claude Code sessions, Cowork tasks, computer use, Dispatch, Quick Entry).
> Obtained from the public Squirrel update feed on 2026-09-26: `https://downloads.claude.ai/releases/win32/x64/RELEASES` → `AnthropicClaude-2.9939.2-full.nupkg` (sha1 `c4d5e0fe…6b62`, 255,805,374 B). The macOS universal `RELEASES.json` names the same version (pub_date 2026-09-24). The `claude.ai/api/desktop/…/redirect` installer links return 403 to scripted clients.
>
> Method: static extraction only (`app.asar`, `resources/ion-dist`, i18n catalogues, CSS, bundled fonts) plus Anthropic docs and help centre pages. **No display was available. I never saw a rendered screen**, so every statement about how something *looks* is ⚠️. Researched 2026-09-26.
>
> Dominant grade: ✅ for tokens, strings and wiring; 📣 for layout and behaviour; one ❌ (a label).

## 1. What it is and how it is built

### 1.1 Runtime

- **Electron**, built with Electron Forge 8 (alpha) and Vite. Makers are deb, rpm, dmg, msix, pkg, squirrel and zip, so one codebase ships to macOS, Windows and Linux (`app.asar/package.json`, `"name":"@ant/desktop"`, in Claude Desktop 2.9939.2) ✅. The Linux build is a beta delivered by apt (📣 `https://code.claude.com/docs/en/desktop-linux.md`). On Linux it has no computer use and no dictation.
- The main process embeds the Claude Agent SDK `0.3.281`, node-pty/ConPTY for the Code-tab terminal, bundled MCP servers (`github-mcp-server.exe`, `office365-mcp`), and bundled skills (`docx`, `pptx`, `xlsx`, `pdf`, `pdf-reading`, `frontend-design`) (`app.asar/resources/bundled-skills/manifest.json`) ✅.
- Cowork runs code locally inside a Linux VM. Shell strings include `Cowork requires QEMU…`, `…hardware virtualization (KVM)…` and `Cowork requires macOS 14.0 (Sonoma) or later` (`resources/en-US.json`) ✅. 📣 "Shell commands and any code Claude writes execute inside a dedicated Linux VM … (Apple Virtualization.framework on macOS, Hyper-V on Windows)" (`https://support.claude.com/en/articles/14479288`).

### 1.2 Is the local bundle thin? It depends on the account

| Account type | Main-window URL | Evidence |
|---|---|---|
| claude.ai account (1P) | `this.deps.anthropicOriginUrl()` → `https://claude.ai` (remote) | `.vite/build/index.chunk-6aZ703Pj.js` in 2.9939.2 ✅ |
| Bedrock / Vertex / gateway ("custom-3p") | `Uu = "app://localhost"`, served from `resources/ion-dist/` by an `app://` protocol handler; navigating elsewhere logs `Blocked bundled-SPA window navigation` | same file ✅ |

`ion-dist` (191 MB) is a complete snapshot of the claude.ai SPA: 3,292 JS chunks, 21 CSS files, 39 woff2 fonts and 31,680 strings × 11 locales. Its `index.html` root is `class="cds-root" data-theme="claude" data-mode="system" data-density="comfortable" data-color-version="v2"` ✅. The local artifact is therefore the full web UI, and the design-system evidence below comes from it.

> ⚠️ 1P users load claude.ai live and may get a newer build than the one frozen in `ion-dist`.

The shell renders only a few windows of its own (`app.asar/.vite/renderer/*`) ✅:

| Window | What it is |
|---|---|
| `main_window` | the offline chrome around the web view: `Couldn't connect to Claude`, `Retrying automatically…`, `Restart Claude` |
| `quick_window` | Quick Entry, a floating composer. Its single string is `What can I help you with today?` |
| `local_exec_consent` | the trusted consent window (§3.1) |
| `buddy_window` | Hardware Buddy BLE pairing (§3.7) |
| `find_in_page`, `about_window` | utility windows |

Beyond these windows, the shell provides native menus, the tray, the dock/jump list (`Needs Your Input`, `Sessions Waiting for You`, `Continue “{title}”`) and global shortcuts. Quick Entry defaults to `quickEntryShortcut: "double-tap-option"`; dictation uses `quickEntryDictationShortcut: "capslock"` ✅ (📣 "Double-tap the Option key to open Claude from any app", `https://support.claude.com/en/articles/12626668`).

### 1.3 Layout: where the agent lives

- **Top level.** A segmented app switch with `data-mode=chat|cowork|code` (`.df-app-switch`; `df`/`dframe` = desktop frame) ✅. 📣 "three tabs: **Chat** … **Cowork** … and **Code**" (`https://code.claude.com/docs/en/desktop.md`). The switch is being removed for Pro/Max: "Claude Cowork and chat are now one Claude" (§4).
- **Code tab.** A pane workspace with the chat as its spine. 📣 "panes you can arrange in any layout: chat, diff, browser, terminal, file, plan, tasks, and subagent, along with the iOS Simulator". Panes are dragged by their header and can pop out into their own windows. A left sidebar lists parallel sessions, and Cmd/Ctrl-click opens a second session in a split. There is also a side chat (`Cmd+;` / `/btw`). The native menu strings confirm this ✅: `Move Split View Left|Right|Up|Down`, `Focus Next Split View`, `Show Terminal`/`Hide Terminal`, `Show Side Chat`, `Show Changes`, `Command Palette…`, `New Session Below`, `Reopen Closed Session`.
- **Where the agent sits.** The agent is the conversation itself. Editor, terminal and browser are peer panes around it, never a host that the agent is docked into. This is the reverse of the IDE-extension pattern.

## 2. Design system: CDS (`@ant/cds`)

Anthropic built its own design system (it is not shadcn). `data-cds="…"` markers in the JS list **119 components** ✅. The agent-specific ones are `AskUserQuestion`, `TurnStatus`, `TurnStatusStep`, `WorkingMark`, `ShimmerText`, `Spark`, `Pulse`, `ChatComposer{Dock,Chin,Tray,Notices,QueuedMessages,PrimaryAction,DropScrim}`, `ModelSelector`, `ModelSelectorEffort`, `FileDiff`, `DiffIndicator`, `CodeView`, `CommentCard`, `CommentPin`, `MessageActions`, `Shortcut`/`Kbd`.

Underneath: both **Base UI** (`data-base-ui-*`, 11 chunks) and **Radix** (`radix-popper-*`, 16 chunks), which suggests a migration in progress ⚠️. Tailwind v4 sits below the CDS tokens. Also present: vaul, cmdk, TipTap/ProseMirror, Monaco, CodeMirror, xterm and shiki ✅.

Theme axes on `.cds-root` ✅:
- `data-theme` = `claude` | `console`
- `data-mode` = `light` | `dark` | `system`
- `data-density` = `comfortable` | `compact`
- `data-font=system` (opt out of the brand fonts)
- message `data-text-size` = `sm` | `lg`
- `data-dyslexic-font`

Components size themselves with `data-size` (xs/sm/lg) or `data-step` (1–5), which remap height, padding, radius and font size together.

### 2.1 Tokens (`ion-dist/assets/v1/c6a992d55-BeQte42g.css` and sibling CSS in 2.9939.2) ✅

| Role | Light | Dark |
|---|---|---|
| Surfaces `--cds-surface-0/1/2/3` | `#f9f9f7` / `#fcfcfb` / `#fff` / `#fff` | `#0b0b0b` / `#151515` / `#1a1a19` / `#20201f` |
| Text primary / secondary | `#0b0b0b` / gray-600 | `#f0efec` / `#c3c2b7` |
| Border `--cds-border` | `--cds-alpha-2` = neutral-900 at 10% (alpha hairline) | same formula, inverted |
| **Brand** `--cds-clay` / `-emphasized` → `--cds-fill-brand` | `#d97757` / `#c6613f` | — |
| **Interactive accent** `--cds-role-accent-fill` | blue-450 `#2a78d6` | — |
| danger / success / warning / **pro** | `#d03b3b` / `#009300` / `#fab219` / violet `#7161e0` | — |
| Secondary swatches | heather `#cbcadb`, cactus `#bcd1ca`, mineral `#629987`, plum `#827dbd` | — |
| Git states | `--cds-{bg,border,fill,text,on}-git-{added,removed,modified,merged,opened,closed,draft,queued,conflicting}` | — |
| Radius xs/sm/lg | 5/5/7 px compact → 6/7/10 px comfortable; composer 12 → 14 px | |
| Gap xs…xl | 6/8/12/20/32 px compact → 8/12/16/28/40 px comfortable | |
| Control height `data-step` 1–5 | 20/24/28/32/40 px | |
| Motion | `--cds-dur-fast 60ms`, `snap 120ms`, `base 200ms`, `sheet 300ms`, `slow 450ms`; `--cds-ease-out cubic-bezier(.165,.84,.44,1)`, `ease-snap (.32,.72,0,1)`, `ease-overshoot (.34,1.3,.64,1)`; `--cds-btn-spring` = CSS `linear()` spring overshooting to 1.09 | |
| Conversation rhythm | `--chat-turn-gap` = body × leading × .75; `--chat-item-gap` = × .5; `--approval-dock-floor: 208px` in narrow tiles | |

Also present: 10 hue ramps × 35 steps, chart palettes (categorical 8, sequential 7, diverging 7), and `--cds-rem-scale: calc(16/17)` under `-apple-system-body` (iOS Dynamic Type).

> 📌 Brand and accent are split. Clay orange is reserved for brand (and is the default hue of the Window Halo, §3.7). Everything interactive is blue, and paid features ("pro") are violet. Git/PR states get a token family of their own, on the same level as the danger/success roles.

### 2.2 Typography and iconography ✅

| Face (family name via `fc-scan`) | Weights | Role |
|---|---|---|
| Anthropic Sans Variable | 300–800, roman and italic, `"dlig" 0` | UI, `--cds-font-sans`; system stack with a CJK fallback |
| Anthropic Serif Variable | 300–800 | `--cds-font-voice`, prose serif |
| Anthropic Mono Web | 300–800 | `--cds-font-mono` |
| Atkinson Hyperlegible Next, OpenDyslexic | — | accessibility options |

- Prose and UI use separate type ramps: prose runs 0.8125–1.125 rem, body runs 0.75–0.9375 rem.
- The serif is named **voice** (serif = Claude speaking); that this is the intent is ⚠️ inferred from the name.
- **Icons: `Anthropicons-Variable`.** A custom variable icon font: `woff2-variations`, weight axis 400–700, about 373 glyphs at U+E000–E176. It is rendered by `[data-cds=Icon]:not(svg){font-family:…;font-optical-sizing:auto}`. The weight axis is used for state; for example, the selected app-switch segment's icon gets `font-weight:700`.
- `codicon` covers code surfaces.
- `lucide-react` appears only as an allowed import for user artifacts, not in the app chrome.

## 3. How harness primitives are rendered

### 3.1 Approval and permission

**One sentence template covers every approval** (`ion-dist/i18n/en-US.json` in 2.9939.2) ✅: `Allow Claude to <b>{action}</b>?`, `Allow Claude to <b>use</b> <meta>{app}</meta>?`, `Allow Claude to fetch pages from <bold>{domain}</bold>?`, `Allow Claude to change files in “{directory}”?`, `Allow Claude to control {apps}?`, plus more than 40 artifact variants (`Allow Claude to publish an artifact?`). Claude is always the subject, and the verb is always bold.

**The scope ladder is spelled out in the button labels** ✅:

| Breadth | Labels |
|---|---|
| single call | `Allow once`, `Deny`, `Don’t allow` |
| conversation | `Allow for this chat`, `Allow for this session`, `Allow for this task` |
| recurring | `Allow for all tasks`, `Allow for all scheduled runs`, `Allow for {days} days` |
| standing | `Always allow`, `Always allow for this website`, `Always allow reads on this host`, `Don’t ask again for this tool` |
| organisation | `Allow for your organization` (admin surfaces) |

- **Escalation and reversal.** After `Allow once` the UI offers `Allowed once. Skip this card next time?`. Undo toast: `Undo: stop always allowing {tool}`. Summary row: `{count} connector tools always allowed · <forget>Forget</forget>`. Admins can suppress the offer (`Offer the persistent “Always allow” approval options for MCP tools…`) ✅.
- **Hotkeys.** Cards bind digits **1–9** to options (`data-approval-card-root`, `data-approval-card-digits`, `data-approval-digit` in `ion-dist/assets/v1/shared-6-BrmMFhdH.js`) ✅. This mirrors the CLI's numbered menu.
- **Where cards render.** Components `InlineToolApproval`, `ToolApprovalHoverCard`, `CoworkToolApproval`, `EpitaxyApprovalCards` (`epitaxy` = the Code transcript) and an approval dock above the composer ✅. The exact placement is ⚠️ unseen.
- **Trusted consent window.** Connector connect/disconnect, the standing Chat grant and 3P bootstrap settings go to a separate React-free native window. The header comment of `app.asar/.vite/renderer/local_exec_consent/localExecConsent.html` reads: "Deliberately dependency-free (no windowBase / React): the consent surface must not run any stack the web-origin renderer could influence. Content arrives via query; the page renders it with textContent only. Color values are the resolved CDS tokens" ✅. A test (`surface-sync.test.ts`) pins those copied values to CDS.
- **Computer-use tiers.** 📣 `View only` (browsers, trading platforms), `Click only` (terminals, IDEs) and `Full control`, fixed by app category. Buttons are `Allow for this session` / `Deny`, and approvals expire after 30 min in Dispatch sessions (`https://code.claude.com/docs/en/desktop.md`).
- **Mode-independent cards.** 📣 "Before archiving any session, Claude asks you first. You see the approval card in every permission mode, including Auto and Bypass permissions." ✅ `Claude is in plan mode, so only you can approve this.`

> 📌 This is the approval-as-primitive shape of [SYNTHESIS §2.1](../SYNTHESIS.md): one card type, reused on every surface, with scope as data. Compare the Codex item/approval protocol in [docs/02](../docs/02-app-server-protocol.md) and the gate properties in [strands/07](../strands/07-security.md). What Claude Desktop adds is **physical separation of the trust-critical prompts** into a window that the web origin cannot script. The wiki's [approval-gate](../ai-workflow/wiki/concepts/approval-gate.md) concept has no such rendering-isolation property yet.

### 3.2 Autonomy modes

| Surface | Labels (✅ strings) | Notes |
|---|---|---|
| Code tab | `Manual` · `Accept edits` · `Plan` · `Auto` · `Bypass permissions` | 📣 "Earlier versions of the Code tab labeled these modes Ask permissions, Auto accept edits, and Plan mode." The old labels are absent from the bundle ✅ |
| Cowork / merged Claude | `Manual` (default) · `Auto` | picker copy: `Claude asks before making changes. Auto is recommended.` |

- How Auto is explained in the UI: `Claude checks each tool call for risky actions and prompt injection before executing, runs the ones it assesses as lower-risk, and blocks the rest.`
- Billing is shown in the UI too: `Auto mode is using Claude Code’s built-in classifier in this session, and those classifier requests are billed. Continue to keep going in auto mode, or Stop to end this turn.`
- Downgrades always name the replacement mode: `Bypass permissions isn’t allowed here, so this session switched to Accept edits.` and `Auto mode isn’t available for the selected model. Switched to {newMode}.`
- Sandbox markers: `Strict sandbox mode`, `Runs outside Claude’s sandbox.`, `Local sandbox`, `Enable additional VM-level isolation for the Cowork sandbox.`

> 📌 Renaming "Ask permissions" to **Manual** moves the subject from Claude to you: the default describes what the human does, not what the agent does.

### 3.3 Plan and todos

- Plan is both a mode and a pane ✅ (`Open plan`, `Copy plan`, `Failed to propose a plan`). Plans are commentable: `You can comment on the plan in plan mode, or when Claude asks you to approve it.` They use the same comment machinery as diffs and artifacts.
- Todos have almost no vocabulary of their own: `Updating todos`, `Updated todos`, `Cleared todos` and `Regarding Todo item: “{content}”` (you can reply to an item). ⚠️ The checklist visual is presumably inside `TurnStatus` or the tasks pane.
- Agent teams: `Approved plan from @{to}`, `Rejected plan from @{to}`, `Approved shutdown request from @{to}` ✅.

### 3.4 Tool-call transcript

- Structure ✅: `AssistantMessage` / `UserMessage` → `TurnStatus` → `TurnStatusStep`; `MessageActions` fade in on hover (the `--cds-message-actions-reveal-*` motion tokens); `WorkingMark` and `ShimmerText` show in-progress state.
- **Tool calls read as a verb plus a count** (373 such strings) ✅:

| State | Examples |
|---|---|
| running | `Reading files`, `Running a command`, `Running {count} agents`, `Reading the screen…` |
| done | `Read {count} files`, `Ran {count} commands`, `Edited {count} files`, `Used Claude in Chrome ({count} actions)` |
| interrupted | `Stopped reading {file}`, `Stopped {count} commands`, `Stopped before it started` |
| thinking | `Thinking…`, `Thinking some more…`, `Thought for {minutes}m {seconds}s` |

- 📣 **View modes act as a lens over the transcript** (`Ctrl+O`): **Normal** (tool calls collapsed), **Thinking**, **Verbose** (every call). ✅ Strings: `Transcript view`, `Default transcript view`.

### 3.5 Diff and review

- 📣 A `+12 -1` diff-stats indicator (✅ `DiffIndicator`) opens a diff pane with the file list on the left. Clicking a line opens a comment; `Cmd/Ctrl+Enter` sends all comments as one batch, and Claude replies with a new diff.
- 📣 The review scope is stated as "high-signal issues … does not flag style". A CI status bar has Auto-fix and Auto-merge toggles (✅ `Auto-fix`, `Auto-merge when ready`).
- ✅ `Resolved review comments collapse in the diff view so you can focus on what’s open`, `Claude’s edits`, `Claude’s edits merged`.
- The bundle has no `Accept all` or `Reject all` string. Review is expressed as comments. In Manual mode, per-change accept/reject is the approval card itself.

### 3.6 Parallel and background work

- 📣 Sessions can run in parallel, each optionally in its own git worktree (`<project>/.claude/worktrees/`). The tasks pane shows subagents, background shells and dynamic workflows, each stoppable. "Task chips" spin out-of-scope work into a new session. Cross-session messages arrive "as a card labeled with the sending session's title". `Continue in` hands a session to the cloud or an IDE.
- ✅ `Cloud sessions keep running, even with the lid closed.`, `Claude was interrupted when your computer went to sleep.`, `Claude picked up where it left off.`, `Claude is working in {count} sessions. Quitting now will interrupt that work.`

### 3.7 Status and attention

- The attention vocabulary is "waiting on you" ✅: `{title} is waiting on you`, `A session in this folder is waiting on you`, `Needs approval — {title}`, `Claude is waiting on you. Pick a reply or type your own.` (`AskUserQuestion`), `Nothing needs your review right now`. The native jump list has `Needs Your Input` and `Sessions Waiting for You`.
- 📣 An OS notification fires when a Code session finishes and you are not viewing it, and again when CI finishes. Dispatch sends a phone push on "finishes or needs your approval".
- **Window Halo** ✅ (`app.asar/.vite/build/index.chunk-Dnsluztc.js`). The model calls MCP tools `halo_attach` and `halo_detach`, described as: "Draw a coloured glow behind a running macOS app's window so the user can tell at a glance which window you're driving or referring to … auto-removes when the app exits". Parameters are `label` ("shown in a pill above the window's title bar. Defaults to this session's short id") and `hue` ("Omit to use a deterministic per-session hue. Anthropic clay is ~15"). The default hue is a djb2 hash of the session id mod 360. It is macOS-only (native `sessionHalo`).
- **Hardware Buddy** ✅ (`resources/en-US.json`): "Claude for macOS, Windows, and Linux can connect Claude Cowork and Claude Code to maker devices over BLE, so developers can build hardware that displays permission prompts, recent messages…". It is developer-mode only: "we built a desk pet that lives off permission approvals".

> 📌 Three answers to "which surface is the agent driving": Atlas tints its own chrome, Aside splits space ([03-aside](../browser-agents/03-aside-design-ux.md) §4), and Claude Desktop marks the **target** window with a per-session colour. The model itself invokes that mark.

### 3.8 Steering and queueing

- Composer: `ChatComposerQueuedMessages` ✅. Strings: `Queued. Claude will read this after the current turn.`, `{count} messages queued. Will send after the current response.`, `Reorder queued message`, `Send now`, `Queued messages collapse into a stack — click to expand`, `Cancelling a queued message no longer interrupts the turn in progress`.
- Stop: `Stop response`, `Stopped`, `Interrupted`. Model and effort sit next to send: `{model} · {effort}` with low/medium/high/`extra-high`/max, and `Max effort uses your limits faster than High. Consider a lower effort setting.` ✅
- 📣 The Code tab docs describe a steer at a finer grain than the strings do. See §6.

### 3.9 Errors

- Errors say what happened and what to do next ✅: `Stopped by a usage limit. You can try again now.`, `Pushing your branch took too long and was stopped. Press Enter in the terminal to push it without a time limit, then select Continue in cloud again.`, `Cowork requires the vhost_vsock kernel module. Load it with 'sudo modprobe vhost_vsock', then restart Claude.`
- Waiting copy has personality: `Contemplating, stand by...`, `A bit longer, thanks for your patience...`.

## 4. Stated design philosophy 📣

- "You don’t have to choose where a task goes. Claude does more of the work." and "We built Cowork as a separate place for bigger work, and Design for visual work. People used both, and told us the frustrating part was deciding where a task belonged … So we stopped making you choose." (https://claude.com/blog/cowork-is-now-claude, 2026-09-16)
- "…merged into a single conversation, so you don’t need to decide which option better suits your task before getting started … with no mode to choose." (https://support.claude.com/en/articles/16761823)
- "You can choose how Claude checks in with you. By default, Claude asks before taking an action … You keep the final say." (same blog)
- "computer use is the broadest and slowest. It tries the most precise tool first … Screen control is reserved for things nothing else can reach" (https://code.claude.com/docs/en/desktop.md)
- In a source comment ✅: "the consent surface must not run any stack the web-origin renderer could influence."

## 5. What is distinctive

1. **Modes collapse at the top and stay at the bottom.** The product switch (Chat/Cowork/Design) is being dissolved, while the autonomy modes stay explicit and are renamed around the human.
2. **The approval card is a grammar.** One sentence template, a scope ladder in the buttons, 1–9 hotkeys, an upgrade nudge, and undo.
3. **Rendering isolation for trust-critical consent.** It gets a separate React-free window, with token values copied in and test-pinned.
4. **The Window Halo.** A model-invoked, per-session-hued indicator placed on the external app being driven.
5. **Git as a colour system**, and conversation spacing derived from type metrics.
6. **Detail is a user-chosen lens** (Normal/Thinking/Verbose), not a fixed folding policy.
7. **Approvals can leave the screen**: phone push through Dispatch, and BLE maker hardware.
8. **The full web UI ships inside the desktop app** for third-party-inference tenants. The desktop app is also the device-side bridge for cloud Cowork sessions (📣 "the request goes through the Claude Desktop app on that device").

## 6. Refutations and contradictions

- ❌ **Review button label.** The docs say "click **Review code** in the top-right toolbar" (desktop.md, *Review your code*). The bundle has no `Review code` string; the nearest are `Review` and `Review changes`. This is minor, a docs label drift.
- ⚠️ **Steer granularity (unresolved).** The docs say "type a correction and press **Enter** to send it without stopping the running action. Claude reads the correction as soon as the current action completes". The shipped strings say `Queued. Claude will read this after the current turn.` and `Will send after the current response.`, and no "after the current action" string exists. They may describe different surfaces (chat vs Code); it could not be settled statically.
- ⚠️ **Default mode.** A string announces `Auto mode is now Claude Code’s default permission mode`, and a `ccd_auto_default_mode` flag exists. The docs make Auto the starting mode only for terminal and VS Code (v2.1.283+), and the Cowork help pages document **Manual** as the default. It looks cohort-gated; I could not verify it without running the app.
- ⚠️ **Summary view.** The docs say the Summary transcript mode was removed in v1.46388.1, yet a bare `Summary` string is still present. It could not be attributed to that menu.

## 7. What this means if you are building an agent client

- [ ] Give every approval one sentence template with the agent as subject and a bold verb. Put the scope in the button label, not in a separate setting.
- [ ] Offer a scope ladder (once → conversation → task/schedule → N days → always), with an upgrade nudge after repeated `once` and an undo for every standing grant.
- [ ] Bind numeric hotkeys to approval options so the GUI and CLI share muscle memory.
- [ ] Render trust-critical consent (new connector, standing grants, policy import) in a surface the model-influenced renderer cannot script, and pin its styling by test rather than by shared code.
- [ ] Name autonomy modes from the human side (`Manual`), and always state the mode you fell back to.
- [ ] Mark the object being acted on (a halo on the target window, per-session colour), not only the agent's own chrome.
- [ ] Summarise tool calls as verb + count, with explicit running/done/interrupted forms. Make detail a user-selectable lens.
- [ ] Say where a queued message lands (after the action vs after the turn), and offer `Send now`.
- [ ] Keep one attention vocabulary ("waiting on you") across the in-app list, OS menus, notifications and off-screen channels.

## 8. Open questions

- Visual: dock vs inline approval placement, the `WorkingMark`/`Spark` animation, and the appearance of the plan and tasks panes. All ⚠️ unseen.
- **GUI pass 2026-09-27 (macOS, same build, `orca computer` screenshots; passive — no agent was run), Code tab.** ✅ The working mark is the **clay spark** (sampled `#cc7c5e`, the dark-theme clay) followed by
  `elapsed · tokens · thought for n s`. So clay is not brand-only as §2 reads the tokens: it is also the **working** colour.
  Tool calls collapse to one grey line each (`Ran n commands ›`), expandable. A repository bar sits above the composer
  (repo, branch, `+n −n`, `Create PR`); the footer carries `+`, mic, the permission mode, model, effort and a context
  ring. Approval placement is still ⚠️ — the observed session was in Auto, which raised no cards.
- Does the remote claude.ai build that 1P users load match `ion-dist` 2.9939.2 (same CDS version)?
- Which permission mode does the Desktop Code tab start in per cohort (`ccd_auto_default_mode`)?
- In the Code tab, does a mid-run message land after the current action or after the turn?
- `claude.com/download` also links a separate "Claude Science" desktop app (`downloads.claude.ai/claude-science/…`). It was not examined.
