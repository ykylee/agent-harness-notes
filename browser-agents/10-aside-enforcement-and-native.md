# 10. Aside — enforcement, Computer Use, native cryptography

> The result of digging into the three items left unverified in
> [09 §10](09-aside-browser-internals.md). Same method — static DMG analysis, searching the daemon's
> SEA payload (258,965 lines), and reading symbols out of native binaries. Nothing was executed.
> Analysed 2026-09-23, `Aside-1.0.922.1.dmg`.
>
> ⚠️ Grade: 🔧 **observed implementation.**

## 1. Permission enforcement — far richer than the documentation

The documentation ([02 §3](02-aside.md)) stops at "three zones, Allow/Ask/Deny, three session
modes." Reading the daemon's zod schema reveals the actual policy engine.

### 1.1 Rule matching — three kinds (discriminated union on `type`)

| Kind | Fields | Description (verbatim) |
|---|---|---|
| **`tool`** | `tool` | "Tool name or glob, e.g. \`bash\` or \`mcp__*\`." |
| | `args` | "Optional argument matchers **keyed by input field name**." |
| **`browser`** | `action` | `read` \| `modify` \| `download` |
| | `url` | "Optional URL glob." |
| **`network`** | `url` | "URL or domain glob." |

The **argument matcher** (`argMatchSchema`) takes two forms:

```
{ $: "eq",    value: string | number | boolean | null }
{ $: "regex", value: string }
```

> 📌 **Tool-name globs plus per-argument regex matching.** You can express not "allow bash" but
> "allow bash only when its first argument matches this regex." That is the same concern as Codex's
> `ExecPolicyAmendment`
> ([`docs/02-app-server-protocol.md`](../docs/02-app-server-protocol.md) §7), expressed more
> concretely here.

### 1.2 Four buckets — including one no document mentions

```js
permissionRulesSchema = {
  allow:    [rule], approved: [rule],
  deny:     [rule], ask:      [rule],
  default:  "allow" | "deny" | "ask"   // default: allow
}
```

> ⚠️ **`approved` is a fourth bucket that appears in no documentation.** By name and position it
> looks like the place for "the user approved this during this session" — where the "Allow once" of
> §1.5 would accumulate. **Graded as inference.**
>
> ⚠️ **The default for `default` is `allow`.** Anything no rule matches passes. Restriction is
> carried by the file roots of `guard` mode instead.

### 1.3 File permissions

```js
filePermissionConfigSchema = {
  readableRoots: [], writableRoots: [],
  outsideRead:  "deny" | "ask",   // default ask
  outsideWrite: "deny" | "ask",   // default ask
}
sandbox: { enabled: boolean }     // default true
```

What appears to be the `full-access` preset is in the code:

```js
{ rules: { allow:[], deny:[], ask:[], default:"allow" },
  files: { readableRoots:["/"], writableRoots:["/"],
           outsideRead:"deny", outsideWrite:"deny" },
  sandbox: { enabled: true } }
```

> 📌 Interesting: **even under full access, `outsideRead`/`Write` are `deny`.** It looks
> contradictory until you notice the roots are already `/`, so there is no "outside." **Separating
> root expansion from outside policy** keeps the expression consistent.
>
> And **even full access leaves `sandbox.enabled: true`.** Permission level and sandbox are different
> axes — the same pattern as the separation of permission level and credential exposure in
> [02 §3.2](02-aside.md).

### 1.4 Resolution order — account then session

```js
resolvePermission({ accountRoot, permissionMode, accountPermission, sessionPermission })
  → mergePermissionConfig({}, accountPermission)     // account defaults
  → mergePermissionConfig(ei, sessionPermission)     // session override
  → mergePermissionConfig(ei, { sandbox, files:{ readableRoots:[accountRoot, RUNTIME_DIR] }})
  → special handling when permissionMode === "read-only"

checkPermission(ctx, callId, request)
  → hasPermission(resolvePermission({...}), request)
```

`hasPermission` branches on **`process.platform === "win32"`** when `request.type === "file"` — path
comparison differs by OS.

The documentation's "two levels (agent defaults / session override)" ([02 §3.1](02-aside.md)) is
confirmed in code. In practice it is **three layers**: account → session → runtime-enforced roots.

### 1.5 The approval prompt — filling the blank in §10 of doc 03

[03 §10](03-aside-design-ux.md) recorded "the actual shape of the approval UI is not documented;
verdict withheld." The daemon's **suspension** system is it.

| Kind | Buttons | Hint |
|---|---|---|
| permission approval | `Allow once` / (deny) | "_… deny it. **No lasting permission will be granted.**_" |
| `action-confirmation` | `Confirm` / `Cancel` | "_Confirm to proceed, or reply with what to do instead._" |
| `ask-user-question` | up to **five** options | "_Pick an option or just reply with your answer._" |

Approval scope renders four ways (`formatApprovalScope`):

```
file    → "{mode}: {path}"
tool    → "Tool: {tool}\n{toolCallTitle(tool, args)}"
browser → "Browser: {action}\n{url}"
network → "Network: {url}"
```

> 📌 **The most important finding here**: the prompt carries an array of `{id, label, value, style}`
> buttons **and also builds a numbered text fallback** (`${i+1}. ${label}`). Every hint ends in
> *"or just reply with your answer."*
>
> **This approval UI is designed to render in a chat channel, not a native window.** That is what the
> Pro plan's "Channels (Remote control)" ([02 §8](02-aside.md)) is, and why discord.js is in the
> bundle. A user can receive the agent's approval request in Slack or Discord and either press a
> button or simply reply.
>
> That there is only "Allow once" and no "always allow," and that **no lasting permission** is stated
> explicitly, is a conservatively chosen default.

## 2. Aside Computer Use — an undocumented OS-control axis

The separate binary whose existence was noted in [09 §5](09-aside-browser-internals.md).
Control flow traced 2026-09-30 against `Aside-1.0.928.1.dmg` (SHA-256
`c6997299dc1ea7c0b15e3efbc6ebca104f331205c9bb83fb2b424c2c5500258c`) — the daemon's Node SEA
payload plus the helper's Mach-O strings. Nothing was executed.

| Item | Value |
|---|---|
| Form | **native Mach-O** (not Node), 2.0MB |
| Location in the DMG | `AsideDaemon/mac-{arm64,x64}/Aside Computer Use.app` |
| Bundle ID | `at.studio.AsideBrowser.computer-use` |
| Version | **1.26.928.1922** (same line as the daemon; browser shell is `1.0.928.1`) |
| `LSUIElement` | **true** — no Dock icon |
| Runtime copy | `~/.aside/runtime-computer-use/Aside Computer Use.app` (`ditto` + quarantine strip + `codesign --verify`) |
| CLI usage | `aside-computer-use <command> [--json <payload>] [--no-dialog]` |

### 2.1 Linked system frameworks

```
AppKit, ApplicationServices, Carbon, Contacts, CoreFoundation,
CoreGraphics, CoreServices, Foundation, IOKit, QuartzCore,
ScreenCaptureKit, Security, Vision
```

### 2.2 What the symbols say it can do

| Capability | Symbols |
|---|---|
| **System-wide accessibility tree** | `AXUIElementRef`, **`AXTreeSerializer`**, `AXValueGetValue`, `AXValueGetTypeID` |
| **Event tap (observe and inject)** | `CGEventTapCreate`, `CGEventTapEnable`, `CGEventTapIsEnabled` |
| Keyboard and mouse | `CGEventKeyboardGetUnicodeString`, `CGEventGetLocation`, `CGEventGetFlags`, `CGEventGetIntegerValueField` |
| Screen capture | `ScreenCaptureKit`, `ScreenCaptureAccess` |
| Image analysis | **`Vision.framework`** |
| Contacts | **`Contacts.framework`** |

> 📌 **The perception philosophy is consistent.** Just as the browser uses an accessibility tree with
> refs ([08 §3](08-aside-code-level.md)), OS control uses **`AXTreeSerializer` to serialise the whole
> desktop's accessibility tree.** Structure is read before screenshot coordinates.
>
> ⚠️ But the capability range **reaches well beyond the browser.** An event tap can observe and
> inject system-wide keystrokes, screen capture and Vision OCR are attached, and there is **Contacts
> access.** Read together with prompt injection ([07](07-security.md)), a fooled agent's range here
> is **the whole desktop, not a browser tab.**
>
> This component appears in **no product document.** The existence of an iMessage skill
> ([08 §7](08-aside-code-level.md)) and the `Contacts.framework` link point the same way.

### 2.3 How the daemon turns it on

`NativeContextAwarenessHelperManager` in the daemon SEA owns the helper. Two modes, both
macOS-only at the JS gate (`Computer Use Helper is only available on macOS` — Windows has a
separate `helper.json` `protocolVersion` 1 path).

**Long-running process (Context Awareness).** Spawn
`COMPUTER_USE_HELPER_BIN_PATH` with **no command**, `stdio: [pipe, pipe, pipe]`. JSON lines on
stdin; JSON lines on stdout. Windows adds `--runtime-root` and `--parent-pid`. Heartbeat every
10s; health timeout 35s; recorder liveness 5 min; idle-exit 5 min once Context Awareness is off
and no `invoke` is in flight.

**One-shot exec.** `aside-computer-use <cmd> --json <payload> [--no-dialog]`, stdout envelope
`{ok, data}` / `{error}`. Used when a caller passes `dbPath` (read the local Messages/Kakao
SQLite without a permission dialog). `imessage.send` timeout is 120s; everything else 30s.

The packaged app is copied to `~/.aside/runtime-computer-use/` before first use (`ditto`,
`xattr -d com.apple.quarantine`, `codesign --verify --strict`).

### 2.4 Stdin protocol (JSON line, one object)

| `command` | Payload | Role |
|---|---|---|
| `invoke` | `{id, name, payload}` | RPC. `id` is `inv-N`. `invoke requires id and name` is a helper string |
| `pause` / `resume` | — | Context Awareness recording |
| `shutdown` | — | process exit (also `lifecycle.shutdown` as a CLI command) |
| `health` | — | status ping |
| `permissions` | `{kind: "observer" \| "messages"}` | TCC sheets |
| `policy` | `excludedBundleIds`, `excludedDomains`, `captureTypedText`, `screenText` | do-not-observe rules + typed-text / OCR switches |
| `menu` | `recentApplications[]` | menubar recents with per-app / per-domain exclusion flags |

`name` values the daemon actually sends:

| Group | Names |
|---|---|
| iMessage | `imessage.list-chats`, `imessage.get-history`, `imessage.search`, `imessage.send`, `imessage.max-rowid` |
| KakaoTalk | `kakaotalk.list-chats`, `kakaotalk.get-history`, `kakaotalk.search` |
| Contacts | `contacts.search`, `contacts.resolve` |
| Desktop | `applications.list`, `applications.icons`, `discard-context-awareness-buffer` |
| Probe | `permissions.check` |

The helper binary also contains `imessage.chat-exists`, `imessage.find-chat-guids`,
`imessage.most-active-sibling`, `imessage.outgoing-delivery`, `keyboard.*`, `mouse.context_menu`,
`applications.list`. Those are reachable as CLI `<command>` names; the daemon does not call every
one.

### 2.5 Stdout events — a second perception surface

The long-running helper emits typed events the daemon validates with zod. Source is one of
`aside_dom` · **`mac_ax`** · `win_uia`. Kinds:

`content.snapshot` (AX `fullTree` or `diffFromPrevious`) · `session.started` / `session.ended` ·
`window.changed` · `mouse.click` / `mouse.context_menu` / `mouse.drag` · `keyboard.shortcut` /
`keyboard.text_input` / `keyboard.submit` · `selection.changed` · `screen.ocr`

> 📌 **Browser `snapshot()` and Computer Use share a tree-plus-diff idea, on different surfaces.**
> The browser tree is a tab. This one is the desktop accessibility tree, with an event tap and
> optional OCR beside it. Context Awareness is the product name for keeping that recorder on.

TCC usage strings in `Info.plist` split the two jobs: Accessibility + Input Monitoring are
**Context Awareness**; AppleEvents + Contacts are **Messages**.

> ⚠️ Swift internals (`EventProtocol.swift`, `AccessibilityRecorder`, `MessagesDB`, `TreeDiffer`)
> were read as strings, not as a decompiled call graph. The process was not run (Linux host).

## 3. Native cryptography — adjudicating three claims

The marketing claims left unverified in [99 §4](99-sources.md).

### 3.1 Secure Enclave — ✅ confirmed

In the `Aside Framework` binary:

```
kSecAttrTokenIDSecureEnclave
SecureEnclaveOperation
CanCreateSecureEnclaveKeyPairBlocking
```

> A Secure Enclave **key-pair creation** path exists. Because it checks creatability first
> (`CanCreate...Blocking`), there is presumably a fallback on unsupported hardware.

### 3.2 Post-quantum cryptography — ✅ confirmed, avoiding a trap

> ⚠️ **What had to be separated first**: Chromium has shipped **X25519MLKEM768 TLS key agreement by
> default since 2024.** ML-KEM strings turning up in a Chromium fork prove nothing about the product.
> So **file location** was checked first.

The result — **it is in Aside's own code:**

| Location | What was found |
|---|---|
| `AsidePasswordManager/background.js` (Vault application code) | `crypto_kem_mlkem768_keypair`, `_enc`, `_dec`, `_enc_deterministic`, `_seed_keypair`, plus each byte-length constant |
| `aside-daemon` payload | `MLKEM768`, **`mlKemEncapsulate`**, **`mlKemDecapsulate`**, `mlKemImportKey`, `mlKemExportKey` |

**ML-KEM-768** (NIST FIPS 203), with application-layer wrappers. `x25519` appears in the same files,
which suggests a **hybrid construction** (classical plus post-quantum) — the standard approach.

> ⚠️ The hybrid combination itself was not verified. **Graded as inference.**

### 3.3 Audit logging — ✅ confirmed

```
appendAuditEvent        (11)
AuditLogEvent           (11)
AuditLogOptionsType     (11)
getPasswordAuditLogsDir  (4)
```

A **dedicated directory for password audit logs** exists. The "audit logging" claim in
[02 §4](02-aside.md) has substance.

## 4. Summary — marketing claims versus measurement

| Claim | Verdict |
|---|---|
| Hardware-backed E2E encryption | ✅ libsodium plus **Secure Enclave key pairs** |
| Post-quantum cryptography | ✅ **ML-KEM-768**, in Aside's own code. Not Chromium TLS inheritance |
| Audit logging | ✅ dedicated directory plus `appendAuditEvent` |
| Human approval for sensitive actions | ✅ the suspension system; only "Allow once," no lasting permission |
| Passwords never exposed to the agent | ✅ `crypto_box_seal`, 12 call sites ([09 §7](09-aside-browser-internals.md)) |

> 📌 **This product's security claims were largely true.** Items graded down early as "landing-page
> claim, unverifiable" were mostly confirmed in code. That **verifying them required binary
> analysis** is itself worth recording — no product document supports any of it.

## 5. And yet — the size of the surface

The same analysis shows the other side.

| Item | Implication |
|---|---|
| `capture-tab-without-userinteraction` ([09 §4](09-aside-browser-internals.md)) | a dedicated API bypassing the standard browser's gesture requirement |
| `CGEventTapCreate` (§2.2) | system-wide input observation and injection |
| `Contacts.framework` (§2.2) | address book access |
| `ScreenCaptureKit` + `Vision` (§2.2) | screen capture plus OCR |
| `default: "allow"` (§1.2) | anything unmatched by a rule passes |
| AI credential access default `Always allow` ([02 §4](02-aside.md)) | the loosest setting is the default |

> **The cryptography is well built. The surface is wide.** These are not contradictory; they are
> different axes. Keeping a secret well and narrowing what a fooled agent can reach are separate
> problems. The conclusion in [07 §9](07-security.md) — that the substance of mitigation is reducing
> privilege — applies directly.

## 6. Still unverified

| Item | Status |
|---|---|
| The exact meaning of the `approved` bucket | ⚠️ inference |
| The hybrid KEM combination | ⚠️ inference |
| `Aside Computer Use`'s actual control flow | ✅ **daemon-side closed 2026-09-30** — spawn + JSON-lines IPC (§2.3–2.5). Swift internals still strings, not a decompiled graph. Not executed |
| Fallback on hardware without a Secure Enclave | ⚠️ unverified |
| What goes to a server | ⚠️ beyond static analysis; requires runtime observation |
| **GUI and visual design** | ⚠️ requires execution; no Linux build exists |
