# 12. The Product Surface as a Build Checklist

> Earlier notes treated the ~80 non-core App Server methods as "Codex product surface" and set them
> aside. For a harness that is itself a product, that framing is wrong: those methods **are** the
> product requirements, already enumerated by someone who shipped across five clients.
> This document re-reads all 104 `ClientRequest` methods as a feature checklist.
> Source: `codex-rs/app-server-protocol/schema/typescript/ClientRequest.ts`.

## 1. How the surface actually divides

| Tier | Methods | What it is |
|---|---|---|
| **Agent core** | ~20 | The loop: threads, turns, items, approvals |
| **Capability system** | ~25 | Skills, plugins, marketplaces, apps, hooks, MCP |
| **Host services** | ~15 | Filesystem, PTY, fuzzy search, git |
| **Identity & policy** | ~20 | Accounts, auth, rate limits, config, permission profiles |
| **Platform & migration** | ~10 | Windows sandbox, external agent import, feedback |
| **Realtime** | ~11 notifications | Voice sessions |

A harness that is a product needs something from **every tier**. The core is the part you can copy
from a design; the rest is the part that determines whether anyone can actually use it.

## 2. Tier by tier

### 2.1 Agent core — build first

```
initialize                        turn/start
thread/start   thread/resume      turn/steer
thread/fork    thread/read        turn/interrupt
thread/list    thread/revert      review/start
thread/items/list  thread/turns/list
thread/compact/start  thread/inject_items
```

Server-initiated: the three `*/requestApproval` methods plus `item/tool/call`.

Notes:
- **`thread/fork`** — branching a conversation is cheap to design in and expensive to retrofit
- **`thread/revert`** replaced a removed `thread/rollback`; design undo around *pagination boundaries*
  rather than arbitrary rewind
- **`thread/inject_items`** lets the host insert items the model did not produce — needed for
  "restore this from our own store" and for replaying external context
- **`review/start`** makes review a first-class operation, not a prompt convention

### 2.2 Session organization — the part everyone underestimates

```
thread/name/set          thread/metadata/update    thread/goal/set|get|clear
thread/archive           thread/unarchive          thread/delete
thread/attachment/add|list|remove
thread/section/move
threadSection/list|create|update|delete
thread/loaded/list       thread/unsubscribe
```

Once users have hundreds of threads, **naming, sectioning, archiving, and attaching external
resources stop being optional.** Specific ideas worth stealing:

- **Goals** (`thread/goal/*`) are separate from instructions and survive across turns
- **Attachments** are idempotent on `(threadId, attachmentType, identityKey)` and can be manipulated
  **without loading the thread** — essential at scale
- **`thread/loaded/list`** distinguishes *loaded* from *stored*. Memory management is explicit
- **`thread/unsubscribe`** lets a client stop receiving a thread's events without ending it —
  necessary for multi-window and multi-client hosts

### 2.3 Capability system

```
skills/list         skills/extraRoots/set     skills/config/write
hooks/list
plugin/list         plugin/installed          plugin/read
plugin/install      plugin/uninstall          plugin/reconcile
plugin/skill/read
plugin/share/save   plugin/share/list         plugin/share/checkout
plugin/share/delete plugin/share/updateTargets
marketplace/add     marketplace/remove        marketplace/upgrade
app/list            app/read                  app/installed
mcpServer/tool/call mcpServer/resource/read   mcpServer/oauth/login
mcpServerStatus/list  config/mcpServer/reload
```

Detail in [13-marketplace-and-plugins.md](13-marketplace-and-plugins.md). Structural points:

- **Install, enable, and share are three different verbs.** Conflating them produces a system where
  you cannot ship a plugin to a team without also turning it on for everyone
- **`plugin/reconcile`** — an explicit "make installed state match configured state" operation
- **`config/mcpServer/reload`** — MCP config changes without restarting the server
- **`mcpServerStatus/list`** returns advertised capabilities, **never inferred from the tool list**

### 2.4 Host services

```
fs/readFile      fs/writeFile      fs/createDirectory
fs/readDirectory fs/getMetadata    fs/remove          fs/copy
fs/watch         fs/unwatch
fuzzyFileSearch
command/exec     command/exec/write  command/exec/terminate  command/exec/resize
thread/shellCommand
gitDiffToRemote  getConversationSummary
```

Why the harness exposes a filesystem API at all: **the client may not be on the same machine as the
agent.** Once you support a remote or containerized runtime, every file picker, diff view, and
"reveal in folder" in your UI has to go through the protocol.

The `command/exec/*` family is a **client-driven PTY**, separate from the agent's own tool calls —
that is what powers a terminal pane sitting next to the agent. `resize` and `write` mean you are
committing to real terminal semantics.

`fs/watch` / `fs/unwatch` plus the `fs/changed` notification give the client live file state.

### 2.5 Identity, policy, and configuration

```
account/login/start   account/login/cancel     account/logout
account/read          getAuthStatus
account/rateLimits/read           account/usage/read
account/rateLimitResetCredit/consume
account/workspaceMessages/read    account/sendAddCreditsNudgeEmail
config/read           config/value/write       config/batchWrite
configRequirements/read
permissionProfile/list
experimentalFeature/list          experimentalFeature/enablement/set
model/list            modelProvider/capabilities/read
```

This tier is what turns a demo into something an organization can deploy:

- **`configRequirements/read`** — admin-enforced requirements are a *separate read* from user config.
  The client must be able to show "your administrator requires X"
- **`config/batchWrite`** — settings changes are atomic. A half-applied config is a support ticket
- **`permissionProfile/list`** — named permission profiles instead of scattered booleans
- **`experimentalFeature/*`** — runtime feature flags with an explicit enablement RPC, so features can
  be toggled without a restart or a rebuild
- **Rate limits and usage are first-class reads**, not error-path discoveries. Users see remaining
  quota before hitting a wall

### 2.6 Platform and migration

```
windowsSandbox/setupStart          windowsSandbox/readiness
externalAgentConfig/detect         externalAgentConfig/import
externalAgentConfig/import/recordHistory
externalAgentConfig/import/readHistories
feedback/upload
```

- Windows sandbox: [14-windows-sandbox.md](14-windows-sandbox.md)
- **`externalAgentConfig/*`** — detect and import configuration from *other agent tools*, with import
  history recorded and readable. A deliberate migration on-ramp. If you are entering a market with
  incumbents, this is the cheapest adoption lever in the whole protocol
- **`feedback/upload`** — in-product feedback is a protocol method, which means it can attach session
  context automatically

### 2.7 Realtime (voice)

Eleven notifications: `thread/realtime/started|closed|error`, `itemAdded`,
`item/started|completed`, `item/transcript/delta`, `transcript/delta|done`,
`outputAudio/delta`, `sdp`.

The `sdp` notification says this is WebRTC. **Realtime routes through separate configuration and is
explicitly exempt from managed-provider checks** — plan for it as a parallel path, not a mode of the
text loop.

## 3. What the shape of this surface teaches

**1. The agent loop is maybe 20% of the work.** 104 methods, ~20 of them are the loop.
Budget accordingly.

**2. Everything user-visible needs a protocol method.** If the client can be remote, "just read the
file" and "just run the command" are no longer local operations.

**3. Policy is a read, not just an enforcement.** `configRequirements/read`,
`permissionProfile/list`, `account/rateLimits/read` all exist so the UI can *explain* the boundary
before the user hits it.

**4. Migration is a feature.** `externalAgentConfig/*` is a product decision encoded in the protocol.

**5. Capability distribution is a three-verb system.** Install ≠ enable ≠ share.

## 4. Minimum viable product-grade harness

Beyond the ~20 core methods, this is the smallest set that makes a harness deployable:

```
Organization   thread/name/set, thread/archive, thread/list (paginated), thread/loaded/list
Capability     skills/list, plugin/list, plugin/install, plugin/reconcile, marketplace/add
MCP            mcpServerStatus/list, config/mcpServer/reload
Host services  fs/readFile, fs/writeFile, fs/watch, fuzzyFileSearch, command/exec (+ write/resize/terminate)
Identity       account/login/start, getAuthStatus, account/rateLimits/read
Policy         config/read, config/batchWrite, configRequirements/read, permissionProfile/list
Platform       windowsSandbox/setupStart, windowsSandbox/readiness
Adoption       externalAgentConfig/detect, externalAgentConfig/import
```

Roughly 25 methods on top of the core — about 45 total, against Codex's 104. The remainder
(`plugin/share/*`, `app/*`, realtime, credits and nudge emails, `thread/section/*`) is genuinely
optional until the corresponding product need appears.
