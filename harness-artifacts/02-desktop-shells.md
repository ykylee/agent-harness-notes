# 02. Desktop shells — Claude Desktop 2.42304.2 and ChatGPT 26.1013.40934, three weeks on

> A drift and depth pass on the two desktop clients studied on 2026-09-26 in
> [`agent-ux/02`](../agent-ux/02-claude-desktop.md) (Claude Desktop 2.9939.2, Windows nupkg) and
> [`agent-ux/03`](../agent-ux/03-openai-codex-chatgpt.md) (ChatGPT 26.924.22138, Linux deb). This
> time both were taken as **Linux debs** on 2026-10-19 and read with REA's Electron tools plus the
> bundles' own chunk names and message catalogues. **No display was available; nothing was
> launched.** Every statement about what a user *sees* is therefore a reading of names and
> strings (⚠️ for layout), while runtime, fuses, files and strings are ✅.
>
> The legacy native ChatGPT for macOS (`com.openai.chat` 1.2026.183) was re-downloaded and is
> **byte-identical** to the September read (SHA-256 `49b33cad…`). §4 adds a type-level inventory
> of its UI that the earlier note did not have.

## 1. Both shells side by side

| | Claude Desktop 2.42304.2 | ChatGPT (Codex superapp) 26.1013.40934 |
|---|---|---|
| Package | `claude-desktop_2.42304.2_amd64.deb`, 183,213,384 B, SHA-256 `38a7d58b…`, apt pool `last-modified` 2026-10-19 07:32 UTC. The Windows Squirrel feed and macOS `RELEASES.json` name the **same** version (pub_date 2026-10-19T00:30Z) ✅ | `chatgpt_amd64.deb` 502,087,434 B, SHA-256 `3ca59e7f…`, `last-modified` 2026-10-16 22:32 UTC ✅ |
| Since the last read | 2.9939.2 → 2.42304.2. The apt pool lists 57 Linux versions from 1.17180.0; the September Linux build was 2.9939.4 ✅ | 26.924.22138 → 26.1013.40934 (`owl-app.ini` `AppVersion`) ✅ |
| `package.json` | `@ant/desktop`, `productName: Claude`, `main: .vite/build/index.pre.js`, Electron Forge `8.0.0-alpha.10` with patched deb/pkg makers, `@electron/fuses ^2.1.3`; runtime deps only `@ant/claude-for-chrome-mcp`, `@ant/claude-native`, `@ant/claude-swift`, `@ant/computer-use-mcp`, `@loc/electron-window`, `https-proxy-agent`; devDeps include `@anthropic-ai/electron-devtools-mcp` ✅ | `openai-codex-electron`, `productName: Codex`, `desktopName: chatgpt.desktop`, `main: .vite/build/early-bootstrap.js`, Electron **42.3.0** (unchanged), Vite 8.2.0, Forge 7.11.2, deps `node-pty`, `@sentry/electron`, `@tanstack/query-core`, `external-agent-migration workspace:*` ✅ |
| Runtime | stock Electron binary `claude-desktop` 228,580,680 B | OpenAI **OWL** runtime: `owl-electron-app.json` `runtimeName: "owl"`, `runtimeArchiveSha 8599728…`, `packagedFrom …/minirepo/codex/codex-apps/electron/out/ChatGPT-linux-x64`; binary `ChatGPT` 322,747,616 B; `version` file says `42.3.0` ✅ |
| Fuses (REA `inspect-electron-fuses`, wire v1, 9 fuses) | `RunAsNode` off · `EnableCookieEncryption` on · `EnableNodeOptionsEnvironmentVariable` off · `EnableNodeCliInspectArguments` off · `EnableEmbeddedAsarIntegrityValidation` on · `OnlyLoadAppFromAsar` on · `LoadBrowserProcessSpecificV8Snapshot` off · **`GrantFileProtocolExtraPrivileges` on** · `WasmTrapHandlers` on ✅ | identical except **`GrantFileProtocolExtraPrivileges` off** ✅ |
| REA's caveat on fuses | "Electron compiles embedded ASAR integrity validation only on macOS and Windows; the observed fuse byte … does not establish enforcement" — so on Linux the integrity fuse is declared, not enforced ⚠️ | same |
| `app.asar` | 49,232,410 B, 540 entries; `node_modules` holds only `@ant/claude-native`, `agent-base`, `node-pty`, `ws` — the Agent SDK that 2.9939.2 exposed as `node_modules/@anthropic-ai/claude-agent-sdk 0.3.281` is no longer a visible package (bundled into chunks or moved; version ⚠️ unknown) | 578,643,106 B, 21,627 entries: 20,360 under `/webview` (20,107 in `webview/assets`), 1,164 `node_modules`, 65 `native-menu-locales`, 37 `.vite/build` |
| Renderer HTML entries | 6, unchanged: `main_window`, `quick_window`, `local_exec_consent`, `buddy_window`, `find_in_page`, `about_window` ✅ | 2: `webview/index.html` (single `<div id="root">` with a startup-loader SVG) and `webview/detached-window.html` (`detachedWindow` chunk) ✅ |
| Main-process entries | 13 `.vite/build/*.js` plus six workers. **New since 2.9939.2:** `designWindow.js`, `claudePagePreview.js`, `coworkArtifact.js`, `computerUseTeach.js`, `mainView.js`; `mcp-runtime/{directMcpHost,nodeHost}.js`; workers `file-index`, `heavy-work`, `pty-host`, `shell-path`, `stall-sampler`, `transcript-search` ✅ | 37 files: `early-bootstrap`, `bootstrap`, `main-CLu1A25j` (the shell), `preload`, `sandbox-preload`, `browser-page-preload`, `worker`, `service-*`, `skills-*`, `mcp-app-attachment-*`, `record-aeon-assistant-message-delivery-*`, `startup-requirements-*`, `watcher-*`, `upload-*`, `windows-file-copy-*`, `external-agent-migration` ✅ |
| Unpacked natives | `github-mcp-server` (Linux), `claude-native-binding.node`, `pty.node` | `pty.node`, `better_sqlite3.node`, `@parcel/watcher`, and `@worklouder/device-kit-oai` (node-hid, serialport prebuilds for 12 platforms) — the hardware keypad |
| Sidecars in `resources/` | `ion-dist` 201 MB (the claude.ai SPA), `cowork-linux-helper` 3.2 MB, `virtiofsd` 2.6 MB, `smol-bin.x64.img` 27 MB, `claude-ssh-askpass`, `chrome-native-host` 1.2 MB, `claude-browser-shim.js`, `gnome-search-provider`, `disclaimer`, 40 locale JSONs (en-US 837 keys) | `codex` 296,885,960 B + `codex-code-mode-host` 74,277,776 B + `rg`, `cua_node` 211 MB, `plugins/openai-bundled` 40 MB + `plugin-signatures` 17 MB, `tectonic` 26 MB (a TeX engine), `skills`, `artifact-template-picker/server.mjs`, `native/{hid-topology-watcher,remote-control-device-key}.node`, `masque-proxy-origins.txt` = `https://codex-portals.api.openai.com`, `codex-notification.wav`, `codex-classic.wav` |
| deb `Depends`/`Recommends` that tell a story | Depends `xdg-desktop-portal`, `libpipewire-0.3-0` (screen capture through the portal), `libsecret`; Recommends `qemu-system-x86`, `ovmf`, `virtiofsd`, `bubblewrap`, `socat`, `openssh-client` — the Cowork VM and sandbox on Linux ✅ (📣 `desktop-linux.md`: Cowork "runs those tasks in a virtual machine that the desktop app hosts with QEMU and KVM") | Depends `libtss2-esys`, `libtss2-mu`, `libtss2-tcti-device0` (**TPM 2.0**), `libusb-1.0-0`; Recommends `git` ✅ |

## 2. Claude Desktop 2.42304.2

### 2.1 What the shell does (REA graph of `app.asar`, evidence `ev_49ecce1c…`)

REA's summary for the 416 JavaScript modules it analysed ✅: `browser_windows: 15`,
`explicit_web_preferences: 41`, `context_bridge_apis: 50` (37 exposed members),
`sender_validation_observations: 63`, `utility_processes: 4`, IPC `operations: 1491` of which
`literal_channels: 10` and `dynamic_channel_operations: 1480`. The dynamic count is the
`$eipc_message$_<uuid>_$_claude.<namespace>_$_<method>` convention (seen in
`coworkArtifact.js` and `computerUseTeach.js`), which REA cannot pair statically — its own
limitation reads "IPC pairing is an inference, not an observation." Context-bridge labels REA
recovered: on the main side `buddy`, `claudeDesktopArtifactPane`, `desktopEssentialTelemetryDisabled`,
`omeletteDesktopPdf`, `process`; on the renderer side `cowork`. Eight of 447 sources exceeded the
analyser's budget and kept static facts only (`findInPage.js`, the heavy-work worker, six
`index.chunk-*` files) ⚠️.

Window option objects visible in the main-process chunks ✅ (titles are `defaultMessage` strings):

| Window | Options |
|---|---|
| Overlay / glow (computer use, `cu-glow.html`) | `transparent, frame:false, alwaysOnTop, skipTaskbar, focusable:false, movable:false, hasShadow:false`; one variant `hiddenInMissionControl`, `titleBarStyle:"hidden"` |
| `About Claude` | 320×428, modal, parent-bound |
| `Configure Third-Party Inference…` | 900×720, min 720×560 |
| `Hardware Buddy & Maker Devices` | 700×460 |
| `Verify sign-in code` | sized to content, `alwaysOnTop` unless `codeEmbedded` |
| `Record a skill` / `Share screen` | picker window, parent-bound |
| `Connect connector` consent | parent-bound, title `{action, select, connect {Connect connector…` |
| Main | `webPreferences:{…, sandbox:true, contextIsolation:true, nodeIntegration:false}` |

Hosts the shell names ✅: `https://preview.claude.ai` / `preview.claude.com` (24 / 23 refs — a
preview origin for the new artifact pane), `https://code.claude.com/docs/en/hooks` (10),
`api.anthropic.com` and `api-staging.anthropic.com`,
`https://downloads.claude.ai/model-catalog/v1/catalog.json` (4 — a **served model catalog**, cf.
the providers-as-data axis in `SYNTHESIS` §2), `microsoft365.mcp.claude.com/mcp`,
`mcp-proxy.anthropic.com`, `platform.claude.com/oauth/…` and `console.anthropic.com/oauth/code/callback`,
`oauth2.googleapis.com/token` + `www.googleapis.com/auth/cloud-platform` (Vertex). REA's
"endpoint" nodes also surfaced a set of **policy keys** as literals: `deniedMcpServers`,
`allowedMcpServers`, `deniedModels`, `availableModels`, `enabledPlugins`, `blockedMarketplaces`,
`forceLoginOrgUUID`, `gatewayInternalNetworks`, `wslInheritsWindowsSettings`, `policyHelpers`,
`hooks`, `modelPricing.{multiplier,overrides}`, `sandbox.credentials.{sigv4,awsPairs,allowPlaintextInject}` —
the managed-settings vocabulary the playbook note ([`ai-sdlc/03`](../ai-sdlc/03-the-control-ladder.md))
described from docs is present in the shipped shell ✅.

### 2.2 The bundled SPA (`ion-dist`)

`index.html` root ✅: `data-build-id="spa-dev" data-git-hash="local"
data-build-timestamp="1792369226"` (= 2026-10-19T00:20:26Z) `data-color-version="v2"
data-document-variant="full" data-entry-document="app" data-theme="claude" data-mode="system"
data-density="comfortable" class="cds-root …"`. 3,554 JS chunks (`scc.json`: 3,548 chunks,
44,988 edges, 0 multi-chunk SCCs — a build-time acyclicity check ships with the app), 25 CSS, 40
woff2, i18n `en-US.json` **35,441 keys** (hashed keys, so namespaces are not readable). CDS
`data-cds` component markers: **124 distinct** (119 in 2.9939.2). The same four theme axes as
before. Chunk names are content hashes (`c71860c77-…`), so unlike ChatGPT the SPA's regions are
only readable from strings.

What the strings say about the **UI composition** (counts are matching values in `en-US.json`) ✅:

| Region | Evidence |
|---|---|
| App switch | the mode-transition table in the JS (`"cowork":"chat"` 35, `"chat":"cowork"` 17, `"code":"chat"` 9, `"code":"cowork"` 6, `"chat":"code"` 3, `"code":"code_feed"` 2, `"code":"nonrenderable"` 3) — three modes still exist as states; the shell menu has `Show Main Window`, `Open Quick Entry` |
| Code tab panes | shell menu: `Show/Hide Sidebar`, `Show/Hide Terminal`, `Show/Hide Side Chat` + `New Side Chat`, `Show/Hide Files`, `Show/Hide Browser`, `Show/Hide Preview`, `Show/Hide Changes`, `Split View`, `Move Split View Left/Right/Up/Down`, `Focus Next/Previous Split View`, `Close Split View`, `Close Pane`, **`Design`** and `Leave Design?`. SPA: `Secondary pane`, `Resize pane rows`, `Open in split view`, `Split view now tiles into an adaptive grid — fit more sessions on a wide screen`, `[[ctrl+]]] and [[ctrl+[]] cycle focus between split panes`, `This file is over 512 KB, too large for the Browser pane, so it opened in the Files pane` |
| Side chat | 22 strings (`Start a side chat`, `Ask in side chat`, `Send to side chat`, `Side chat {n}`) |
| Subagents | 21 (`Message from subagent`, `Dynamic workflows let Claude fan out to many subagents on a single task`, `Most usage on this machine in the last 24 hours came from subagent-heavy sessions`) |
| Worktrees | **158** strings (`In a worktree`, `Leaving the worktree`, `This session's worktree has uncommitted changes…`) |
| iOS Simulator pane | 27, all gated `Claude Code iOS Simulator requires macOS` |
| Claude Design | **109** values with the product name: `Claude Design is in research preview with its own weekly limit`, `Claude Design is included in Pro and Max`, `As of October 15, Claude Docs, Slides, and Design are on by default for your organization`, `Design systems give Claude your colors, type and components to use when making designs, decks and prototypes`, `Draft a design on a canvas Artifact — editable where saving is enabled (Claude Design preview)`, `Claude Design [standalone]` — the new `designWindow.js` entry and the `Design` menu item belong to this |
| Dispatch | 19 (`Let Claude work on tasks from your phone using this computer`) |
| Computer use | 21 (`Computer use is available on the Pro and Max plans`, `Computer use isn't available on the Team and Enterprise plans yet`); the shell's `computerUseTeach.js` exposes `CuTeach_$_{exit,hide,next,mouseEnter,mouseLeave}` — a teach-mode overlay |
| Approval | 93 `Allow Claude to …` templates (2.9939.2: "more than 40"); new examples `Allow Claude to use the browser on <bold>{domain}</bold>? This site is high-risk, so Claude asks before each visit.`, `Allow Claude to copy files from another artifact into "{title}"?` |
| Modes | exactly `Manual`, `Accept edits`, `Plan`, `Auto`, `Bypass permissions` — unchanged |
| Hardware Buddy | `Allow pairing Hardware Buddy Bluetooth devices in Cowork.` |

The four new main-process entries, read from their own strings ✅: `claudePagePreview.js`
exposes `claudeDesktopArtifactPane` to a page loaded from the `preview.claude.ai` origin (an
artifact/preview pane hosted in a `WebContentsView`); `coworkArtifact.js` exposes
`CoworkArtifactBridge_$_askClaude` and `CoworkArtifactBridge_$_callMcpTool` — an artifact
rendered inside Cowork can call back into the model and into MCP tools; `computerUseTeach.js` is
the teach overlay; `designWindow.js` is the Claude Design surface. The `mcp-runtime` pair
(`directMcpHost`, `nodeHost`) hosts MCP servers in the shell process rather than a child.

### 2.3 Cowork on Linux

The deb ships the VM toolchain the docs describe 📣→✅: `virtiofsd`, `cowork-linux-helper`,
`smol-bin.x64.img` (27 MB) and shell strings `Cowork requires QEMU. Install it with
''{installCommand}'', then restart Claude.`, `Cowork requires hardware virtualization (KVM)…`,
`Cowork requires the vhost_vsock kernel module. Load it with 'sudo modprobe vhost_vsock'`,
`Delete Cowork VM Bundle and Restart…`, `Free Up Cowork Disk Space…`, `Enable Cowork SDK
Debugging`, `Enable Cowork VM Debug Logging`. What the September note could only quote from a
support page is now in the package.

## 3. ChatGPT 26.1013.40934 — the Codex superapp

### 3.1 Shell

REA's graph of the 37 shell sources (evidence `ev_0881fae3…`) retained **static facts only** for
the large ones (`main-CLu1A25j.js`, `core-*`, `conversation-turn-mutations-*`,
`browser-page-preload.js` — "Owned JavaScript worker exhausted its heap") ⚠️, so its Electron
summary (3 context-bridge APIs, 26 IPC operations, 15 sender-validation observations) is a floor,
not a count. A direct scan of the same files ✅: `main-CLu1A25j.js` constructs **5
`BrowserWindow`s and 1 `WebContentsView`**, `bootstrap-Dn-4EbjT.js` one more. Option objects:
two 1×1 transparent, non-focusable helper windows (`alwaysOnTop`, `enableLargerThanScreen` on
darwin — a screen-capture/overlay anchor pattern ⚠️), a 420×176 `Installing ${app.getName()}`
dialog (`closable:false`), a 420×176 titled dialog, and a sized content window
(`useContentSize`, `autoHideMenuBar`, background `#202020`/`#ffffff` by theme, `windowIcon`).
Hosts ✅: `https://api.openai.com/auth` (20), `wss://codex-cloud-backend.chatgpt.com/` (the
**durable** host from [`agent-ux/03` §1.2.1](../agent-ux/03-openai-codex-chatgpt.md) — still
present), `https://ab.chatgpt.com/v1` (Statsig), `chat.openai.com/ces/v1/telemetry/intake`,
`updates.oaistatic.com/codex/app/appcast`, `persistent.oaistatic.com/codex-app-prod/windows-release.json`
and `…/windows-store-update.json`, `gov.chatgpt.com`, `pay.openai.com`, `auth.openai.com`.

**The engine is the bundled `codex` binary, driven as `app-server`** ✅
(`application-network-startup-DB1VeU3v.js`): the shell builds the launch as
`[…, "app-server", …overrides, "--analytics-default-enabled"]`, reads its stdout as JSONL
("Failed to parse app-server stdout JSONL message") or a WebSocket ("Codex app-server websocket is
not open"), version-checks it with `app-server daemon version` (2.5 s timeout) and refuses anything
below `0.141.0` (`codex-app-server-version-unsupported:` → `update-required`;
`codex-app-server-version-restart-available:` → `restart-required`), and shares `CODEX_HOME`
(`${CODEX_HOME:-$HOME/.codex}`) with the CLI, so sessions, config and login are the same files. Host
kinds: `local`; WSL on Windows (the Linux `codex` is spawned inside `wsl.exe`, `codex.exe` /
`codex-code-mode-host.exe` mapped to `codex` / `code-mode-host`); an `ssh-websocket-v0` transport;
and the durable cloud host `wss://codex-cloud-backend.chatgpt.com/` (`hostConfig.websocket_url`).
The sibling `codex-code-mode-host` is launched next to it (`windowsSiblingExecutableNames`). The
"Chat" half of the app (`chatgpt-conversation-*` chunks) talks to chatgpt.com, not to the engine.

Three preloads instead of one ✅: `preload.js` (the app), `sandbox-preload.js`, and
`browser-page-preload.js` (the in-app browser's pages). The webview CSP ✅ allows `child-src` /
`frame-src` on `codex-sandbox://*.web-sandbox.oaiusercontent.com` and
`https://web-sandbox.oaiusercontent.com` (MCP apps and visualisations run in an isolated origin),
plus Google Docs/Sheets/Slides embeds, YouTube, Vimeo, Plaid, Apple MapKit, and
`script-src 'self' 'sha256-…' 'wasm-unsafe-eval' https://cdn.plaid.com/… https://persistent.oaistatic.com/voice/silero-vad-v6/…`
(a bundled VAD for voice).

### 3.2 UI composition from the webview (4,845 distinct non-icon chunk names)

Unlike Claude's hashed chunks, OpenAI's Vite build keeps **readable chunk names**, so the
information architecture is legible from the file list alone. Labels in quotes are
`defaultMessage` strings from the named chunks ✅. Layout is still ⚠️ (not seen).

| Region | Chunks and labels |
|---|---|
| Shell frame | `floating-navigation-rail`, `thread-app-shell-chrome`, `page-layout`, `pane-layout`, `app-window` / `app-window-mac`, `thread-user-message-navigation-rail` |
| Left sidebar | `sidebar`, `sidebar-actions`, `sidebar-children`, `sidebar-archive-suggestion`, `sidebar-onboarding-checklist.electron`, `sidebar-rename-dialog`; labels `Scheduled tasks`, `Goals`, `Team` / `Personal` ownership filter, `{status, select, in_progress {Running now} failed {Run failed} …}`, `Needs your attention`, `Trigger on {app} event` |
| Centre thread | `thread`, `thread-virtualizer`, `thread-scroll-layout`, `local-conversation-thread`, `chatgpt-conversation-page`, `thread-summary-panel-*`, `thread-recovery-notice`, `thread-usage-breakdown`, `static-thread-transcript` |
| Composer | `composer`, `composer-action-bar-run-location-dropdown` (`Work in` → `This computer` / `Local` / `Cloud` / `Worktree` / `New worktree`; `Run follow-up in`, `Where should this follow-up run?`, `Select a cloud environment`, `Set up an environment via Codex web`), `composer-work-home-plugins-control` + `animated-segmented-toggle` (the **Work / Chat** toggle; `Work with ChatGPT across your favorite tools`, `Turn complex tasks into finished work`), `composer-utility-bar`, `composer-suggestions`, `composer-tip`, `above-composer-fixed-content-surface`, `side-chat-composer`, `inline-composer` |
| **Permission mode dropdown** (`permissions-mode-dropdown`, `permission-dropdown`, `permission-explanation`) | `How should ChatGPT actions be approved?` → **`Ask for approval`** (`Always ask to edit external files and use the internet`), **`Approve for me`** (`Only ask for actions detected as potentially unsafe`), **`Full access`** (`Unrestricted access to the internet and any file on your computer`), `Use Work settings` (`Follow your saved Work settings`), `Custom (config.toml)` (`Uses permissions defined in config.toml`), `Managed by enterprise policy`, `Disabled by requirements.toml`, `Unavailable while working in the cloud`, `Requires default sandboxed permissions in this workspace`; a gate `Enable Full Access for Cyber model?` / `Cyber models carry a higher risk of dangerous actions` |
| Approval cards | `mcp-tool-call-approval` (`Allow ChatGPT to use {appDisplayName}?`, `Always allow`, `Allow this conversation`, `Elevated Risk`, `Requires explicit authorization because this action is considered high risk`), `computer-use-app-approval-request-card`, `auto-review-approval-nudge` (`Want fewer approval prompts?` → `ChatGPT can automatically approve eligible actions while it works. This may use more credits.` / `Keep manual approvals` / `Approve for me`), `automatic-approval-review-details` |
| Right side panel (tab registry) | `thread-side-panel-tabs`, `side-panel-tab-frame`, `chatgpt-entity-side-panel-tab-registry`; tabs: `open-artifact-side-panel-tab`, `open-automation-side-panel-tab`, `open-text-file-editor-side-panel-tab.electron`, `open-thread-pull-request-side-panel-tab`, `thread-mcp-app-side-panel-tab`, `plan-side-panel`, `cloud-browser-side-panel`, `image-side-panel`, `local-conversation-sources-side-panel-tab`, `thread-goal-side-panel-content`; `Toggle side panel`, `Bottom panel` / `Toggle bottom panel` |
| Terminal and background work | `terminal-panel`, `terminal-tab`, `background-terminal`, `local-conversation-background-terminal-tab`, `open-local-conversation-background-agent`, `xterm-window-zoom` |
| Subagents panel | `subagent-panel`, `subagent-row`, `local-conversation-subagents-panel-tab`, `chatgpt-subagents-panel`: statuses `Waiting / Working / Done / Failed`, `Active · {count}`, reasoning `none … xhigh / max / ultra / persistent` |
| Review and PRs | `review`, `review-chat`, `review-file-tree-side-pane`, `inline-file-diff-review`, `virtualized-file-diff-line`, `auto-diff`, `code-review*`, `pull-request-*` (16 chunks), `create-pull-request-modal-content`, `git-branch-picker-dropdown-content`, `git-summary-branch-changes-row` |
| Worktrees and hand-off | `use-codex-worktrees`, `worktree-creation-row`, `worktrees-settings-page` (`Worktree root`, `Always fetch upstream before creating worktrees`, `Automatically delete old worktrees`, `Auto-delete limit`, `ChatGPT snapshots worktrees before deleting`), `thread-handoff-modal` (`Hand off chat to worktree`, `Hand off chat to remote`, `Bring changes back to local checkout`, `Stash or commit your local changes to hand off`) |
| Hotkey / quick window | `hotkey-window-home-page`, `hotkey-window-new-thread-page`, `hotkey-window-thread-page`, `quick-chat-window`, `quick-chat-floating-surface`, `quick-chat-floating-resize-handles`, `content-quick-chat-overlay`; labels `Ask quick questions with Chat`, `Minimize chat to corner`, `Start in` → `Local project` / `Cloud` / `Worktree`, `Standalone chats run in a local folder` |
| Detached window | `detached-window.html` → `detachedWindow` chunk (a pop-out host) |
| In-app browser | 22 `browser-*` chunks (`browser-address`, `browser-address-suggestion-overlay`, `browser-site-settings`, `browser-use-policy-site-permissions`, `browser-extension-setup`, `browser-profile-bridge`, `browser-voice-mode`), `hidden-browser-use-webview-host`, `hidden-background-webview-host` |
| Settings (sidebar sections `General`, `Personal`, `Coding`, `Integrations`, `All settings`) | 51 `*settings*` chunks: `general`, `appearance`, `notifications`, `keyboard-shortcuts`, `personalization`, `memory`, `data-controls`, `security`, `safety`, `age`, `agreements`, `billing`, `account`, `profile`, `member`, `team-settings-page`, **`hooks-settings-*`** (route, navigation, model, copy, source-label), `mcp-settings`, `plugins-settings`, `skills-settings`, `local-environments-settings-page`, `cloud-environments-settings-page`, `worktrees-settings-page`, `git-settings`, `code-review-settings`, `computer-use-settings`, `browser-use-settings`, `browser-extension-settings`, `remote-connections-settings`, `quick-send-settings`, `pets-settings-route`, **`chronicle-settings-page`**, `classic-windows-settings-rows`, `debug-settings`, `dock-icon-setting-visibility` |
| **Chronicle** (`chronicle`, `chronicle-permissions-dialog`, `chronicle-service-queries`) | `Computer history`: `ChatGPT records text summaries of your computer activity.`, `Computer history requires Memories`, `Allow all apps` / `Customize apps`, `Consider pausing or excluding sensitive apps, such as health or finance`, `You also agree that you'll pause Computer History during communications with others … unless you have their prior express consent`, worked examples (`What did I promise to send Sarah after yesterday's meeting?`), `Suggested skill`, `Suggested automation` |
| Pets | `pet-model`, `pet-content`, `pet-install-modal-host`, `pet-settings-dialog`: `Mini` (`The lightweight Codex companion`, `Mini manages chats and surfaces what needs attention`), `Custom pets` folder, `Visibility` `On demand` / `Always visible` |
| Hardware keypad | `codex-micro-*` (12 chunks) + `@worklouder/device-kit-oai`: `Welcome to Codex Micro` / `Creator Micro` (Work Louder), `The 6 frosted Agent Keys give you a live status of your Codex chats/agents`, legend `White – Idle · Blue – Thinking · Green – Complete · Amber – Requires input · Red – Error · Off – No Assigned Agent`, macOS `Input Monitoring` permission flow |
| Workspace Agents | `workspace-agents-page`, `workspace-agent-detail-page`, `workspace-agent-landing`: `Keep work moving 24/7 with agents`, `Team directory`, `{agentName} is working`, `Published to your workspace's directory` |
| Aeon (durable threads) | `aeon-onboarding`, `aeon-thread-detail`, `aeon-message-parts`, `aeon-summary-panel-identity`, `cloud-aeon-onboarding`, `record-aeon-assistant-message-delivery` (also in the shell) |
| Automations | 13 chunks (`automation-side-panel-tab`, `automation-frequency-section`, `automation-plan-summary`, `pull-request-fix-automation`) |
| Sandboxes | `codesandbox`, `connect-code-execution-sandbox`, `native-code-execution-sandbox`, `mcp-sandbox-element`, `mcp-sandbox-rpc`, `visualization-sandbox-{broker,config,html,prewarmer,runtime}` |
| Plugins / MCP apps | 50 `plugin-*` chunks (`plugin-marketplace-context`, `plugin-install-modal`, `plugin-origin-badge`, `plugin-enterprise-upgrade-dialog`), 25 `mcp-*` (`mcp-request-card`, `mcp-server-elicitation-request-panel`, `hosted-mcp-app-adapter`, `webmcp-tool-calls`), `apps/` holds 30 editor and terminal icons (`vscode`, `cursor`, `zed`, `xcode`, `ghostty`, `warp`, `windsurf`, `antigravity`, `devin`, …) for "open in" |
| Voice | 19 `voice`/`realtime-*` chunks (`realtime-voice-stage-layout`, `voice-dsp`, `realtime-buffered-audio-worklet`) |

### 3.3 Drift from 26.924.22138 (what the September note did not have)

- **The permission dropdown's labels are not new.** [`agent-ux/08` §2](../agent-ux/08-primitives-rendered.md)
  already listed `Ask for approval · Approve for me · Full access · Custom (config.toml) · Managed`
  for 26.924.22138, so the 2026-09-26 read had them. What this pass adds is the **surrounding
  copy**: the one-line explanations (`Only ask for actions detected as potentially unsafe`,
  `Unrestricted access to the internet and any file on your computer`), the
  `Managed by enterprise policy` / `Disabled by requirements.toml` / `Unavailable while working in
  the cloud` states, the `Enable Full Access for Cyber model?` gate, and the `Approve for me` nudge
  that names its cost (`This may use more credits`) — the same shape as Claude's `Auto mode is using
  Claude Code's built-in classifier … those classifier requests are billed`
  ([`agent-ux/02` §3.2](../agent-ux/02-claude-desktop.md)). Whether the nudge existed in 26.924 is
  ⚠️ (not recorded then). Both vendors **price the classifier in the UI** ✅.
- **Hooks have a settings page** (`hooks-settings-*`) ✅; the engine side is in `codex-rs/hooks`
  and the Claude side is `code.claude.com/docs/en/hooks` (10 refs in Claude's shell). The
  control-ladder rung "a hook" ([`ai-sdlc/03`](../ai-sdlc/03-the-control-ladder.md)) is now a
  user-facing surface in both desktops.
- **Chronicle / Computer history** is new, and its consent text is unusually explicit about third
  parties ✅. Nothing in the Claude bundle corresponds to it (`Computer use` in Claude is
  per-app approval, not a history).
- **TPM libraries in `Depends`** (`libtss2-*`) and `remote-control-device-key.node` — a device
  key for remote control, ⚠️ purpose not read.
- `thread/rollback` and the durable host persist; `external-agent-migration` is a workspace
  package in `dependencies` (migrating sessions from other agents — ⚠️ not read further).

## 4. The legacy native ChatGPT for macOS, at type level

Byte-identical to September (`ChatGPT.dmg` 78,575,566 B, SHA-256 `49b33cad…`;
`com.openai.chat` 1.2026.183, build 1783607847, `LSMinimumSystemVersion 14.0`, SDK `macosx26.4`,
Xcode 2641) ✅. REA's Apple tools need macOS (`inspect-macho`, `inspect-asset-catalog`,
`demangle-swift` all answered "Native macOS utilities require macOS";
`inspect-native-dispatch-metadata` needs a native provider) ⚠️; `decode-interface-builder` ran
and found only Sparkle's three nibs — a SwiftUI app has no nibs of its own, and `Info.plist` has
no `NSMainStoryboardFile` ✅.

What `strings` on `ChatGPT.framework` (114,840,064 B, arm64) gives instead ✅:

- **129 resource bundles = the feature module list**: `ChatGPTConversationRoot`, `ChatGPTMessageInput`,
  `ChatGPTCanvas`, `ChatGPTCodeExecution`, `ChatGPTConnectors`, `ChatGPTDeepResearch`,
  `ChatGPTAutomation`, `ChatGPTPairWithAI`, `ChatGPTPets`, `ChatGPTVoice`, `ChatGPTMemory`,
  `ChatGPTProjects`, `ChatGPTGPTStore`, `ChatGPTHealth`, `ChatGPTFinance`, `ChatGPTCommerce`,
  `ChatGPTJobs`, `ChatGPTSites`, `ChatGPTSunset`, `ChatGPTXPC`, `OAIDiff`, `OAIMarkdown`,
  `Styleguide`, `Hive`, `DotBall`, `Motion`, `KeyboardShortcuts`, `Sparkle` …
- **638 UI type names**: 461 `*View`, 60 `*Screen`, 54 `*Sheet`, 15 `*Window`, 13
  `*ViewController`, 12 `*Overlay`, 11 `*Menu`, 5 `*Popover`, 4 `*Panel`, 2 `*WindowController`,
  1 `*Toolbar`. Windows: `ChatGPTMainAppWindow`, `ChatGPTMainWindow`, `ChatGPTWindow`,
  `CompactWindow`, `DesktopWindow`, `DiffWindow`, `RecordingWindow`(+Controller), `BrowserWindow`,
  `ChatGPTSettingsAppWindow`, `ChatGPTSharedConversationAppWindow`, `ChatGPTAcknowledgementsAppWindow`,
  `AXFloatingWindow` / `AXStandardWindow`; panels `LauncherPanel`, `ChatGPTLauncherPanel`,
  `MarkdownImagePreviewPanel`, `RemoteFilePreviewPanel`; the agent-adjacent types
  `CodexTaskProgressView`, `CodexUnreadTaskIndicatorView`, `CodexNetworkAccessSettingsView`,
  `CodexUpgradeScreen`, `WorkModePetView`, `WorkModePetSpritesheetFrameView`,
  `WingmanDotComposerDockAnchorOverlay`, `ChatGPTWebView`, `WindowFindingView`.
- Helper: `Contents/Library/LaunchAgents/com.openai.chat-helper.plist` (`MachServices
  com.openai.chat-helper`) and `ChatGPTCodexUpgradeHelper` — the upgrade path to the superapp
  that [`agent-ux/03` §1.1](../agent-ux/03-openai-codex-chatgpt.md) describes.

> 📌 Read against §3.2, the native app's `*Window` list (main, compact, desktop, diff, recording,
> browser, launcher) and the superapp's `hotkey-window-*` / `detached-window` / `review-*` /
> `browser-*` chunks are the **same window vocabulary in two stacks** — the point
> [`agent-ux/09`](../agent-ux/09-design-language.md) makes about words converging before pixels,
> now visible at the type level.

## 5. What this changes in the earlier notes

- [`agent-ux/02`](../agent-ux/02-claude-desktop.md): version 2.9939.2 → 2.42304.2; `node_modules/@anthropic-ai/claude-agent-sdk` no longer visible as a package; four new main-process windows; Linux Cowork VM toolchain shipped; 93 approval templates; `Claude Design` surface. Modes and the six renderer windows unchanged.
- [`agent-ux/03`](../agent-ux/03-openai-codex-chatgpt.md): version 26.924.22138 → 26.1013.40934; permission dropdown labels unchanged, explanatory copy and the `Approve for me` credit nudge recorded; `hooks`, `chronicle`, workspace agents, Codex Micro keypad; three preloads; TPM dependencies. Electron 42.3.0 and the OWL runtime unchanged; the legacy native app unchanged.
- [`agent-ux/08`](../agent-ux/08-primitives-rendered.md) §2 (autonomy modes): the ChatGPT row already matches the shipped labels; no edit needed. The explanatory copy and the credit nudge above are the additions.
