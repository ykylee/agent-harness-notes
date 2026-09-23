# 09. Aside Browser — binary internals

> Method: downloaded the macOS DMG (334MB) and analysed it **statically** on Linux. It was not run —
> analysis does not require execution. App bundle unpacked → three internal extensions identified →
> the daemon's Node SEA payload extracted (70MB / 258,965 lines) → Vault cryptography call sites
> confirmed. Target `Aside-1.0.922.1.dmg`, analysed 2026-09-23.
>
> ⚠️ Grade: 🔧 **observed implementation**, as in [08](08-aside-code-level.md) and
> [04](04-comet-architecture.md).

## 1. Reproduction

```bash
# The real distribution URL is given by a 302 from /api/download/<os>
curl -sSI https://aside.com/api/download/macos   | grep -i location
# → https://releases.aside.com/dev-updater/Aside-1.0.922.1.dmg
curl -sSI https://aside.com/api/download/windows | grep -i location
# → .../dev-updater/windows/1.0.922.1/AsideInstaller-1.0.922.1-win-x64.exe  (10.7MB stub)

curl -sSL -o Aside.dmg https://releases.aside.com/dev-updater/Aside-1.0.922.1.dmg
7z x -y -oDMG Aside.dmg        # Aside.app comes straight out
```

## 2. The big picture — this is not Electron

The `Aside Framework.framework` layout matches Chromium's own `Chromium Framework`. **A real Chromium
fork**, not an Electron wrapper.

| Item | Value |
|---|---|
| Bundle ID | **`at.studio.AsideBrowser`** |
| Framework | `Aside Framework.framework/Versions/1.0.922.1/` (498MB) |
| Internal extensions | `Libraries/AsideAgentManager` (52M), `AsidePasswordManager` (5.4M), `AsideDaemon` (353M) |
| Other | `libaperitif.dylib`, SwiftShader/Vulkan (Chromium standard) |

### Three separate version lines

| Component | Version |
|---|---|
| Browser shell | **1.0.922.1** |
| Internal extensions (Agent / Vault) | **1.26.923.310** |
| CLI | **1.26.916.1741** |

> 📌 Extensions and CLI share a `1.26.x` line while only the browser shell is `1.0.x`. **Agent logic
> and the browser shell have separate release cadences.** That lets chasing Chromium
> ([01 §3](01-landscape.md)) run independently of agent feature work — the same motivation behind
> Comet auto-updating its extensions from the server.

## 3. ⚠️ A correction to an earlier statement — Aside also implements this as extensions

[04 §1](04-comet-architecture.md) described Comet as *"a native browser whose internal
implementation is three extensions"* and contrasted it with Aside. **That contrast was wrong.**

`AsideAgentManager/manifest.json`:

```json
{ "name": "Aside Browsing Agent", "version": "1.26.923.310", "manifest_version": 3,
  "background": { "service_worker": "background.js", "type": "module" } }
```

**Aside's agent is an MV3 Chrome extension too.** Both products made the same structural choice.
The warning in [01 §1](01-landscape.md) — that the outer classification can differ from the inner
structure — turns out not to be specific to Comet but **the general pattern of this class.**

> This is **the first statement this study overturned about itself.** The relevant paragraph in 04
> carries a correction marker.

## 4. The agent extension's permissions — the real trust boundary

```
sidePanel, contextMenus, storage, activeTab, tabCapture, offscreen,
debugger, downloads, favicon, history, bookmarks, topSites, browsingData,
privacy, management, nativeMessaging, cookies, tabs, scripting, userScripts,
webNavigation, sessions, tabGroups, alarms, notifications
```

`host_permissions`: **`<all_urls>`** and **`https://api.anthropic.com/*`**

### Eight custom Chromium extension APIs

Things standard Chrome does not have, added directly. **This is why the fork exists.**

| Permission | Likely purpose |
|---|---|
| `at.studio.Aside.ext.private.account` | accounts |
| `...adblock` | ad blocking |
| `...browser-import` | importing data from other browsers |
| `...notification` | notifications |
| `...omnibox` | the address bar (the Ask AI mode in [03 §2](03-aside-design-ux.md)) |
| `...pref-get-set` | reading and writing browser preferences |
| **`...capture-tab-without-userinteraction`** | **capturing a tab without user interaction** |
| `...launch-extension` | launching extensions |

> 📌 `capture-tab-without-userinteraction` stands out. Standard `tabCapture` requires a user gesture;
> they **built a dedicated API into the fork to bypass that constraint.** The agent has to see the
> screen in the background, so it is necessary — but thinking about **why the standard imposes that
> constraint** is exactly the price of the fork.
>
> That **Anthropic's API is named explicitly** in `host_permissions` is also worth recording. Other
> providers are covered by `<all_urls>`; only Anthropic is listed separately.

## 5. AsideDaemon — 353MB, the real engine

```
AsideDaemon/
├── mac-arm64/
│   ├── Aside Daemon.app/Contents/MacOS/aside-daemon      ← 151MB Mach-O, Node SEA
│   └── Aside Computer Use.app/Contents/MacOS/aside-computer-use
└── mac-x64/ (identical layout)
```

This is what the CLI attaches to ([08 §5](08-aside-code-level.md)):

| Channel | Address |
|---|---|
| stable | **`http://127.0.0.1:21420`** |
| canary | **`http://127.0.0.1:21421`** |

> 📌 That **`Aside Computer Use.app` is a separate executable** matters. Browser automation and
> **computer use (OS-level control) run as different processes.** That axis appears in no document.

### The daemon payload

`aside-daemon` is also a Node SEA. Extracted, it yields **70,121,815 bytes / 258,965 lines** of JS —
28× the CLI bundle (2.5MB). The agent loop, the providers and the storage all live here.

`drizzle` ORM is present, so **the daemon has a SQL database.**

## 6. Model providers — far broader than the documentation

The documentation ([02 §9](02-aside.md)) lists seven API-key providers. The ids visible in the daemon
go well past that.

```
anthropic, openai, google, xai, openrouter, cloudflare, mistral, fireworks,
github-copilot, together, groq, deepseek, ollama,
azure-openai-responses, openai-codex, opencode
```

Endpoint strings also include Bedrock (`bedrock-runtime.us-east-1.amazonaws.com`), NVIDIA, Aliyun
MaaS and `radius.pi.dev`.

> 📌 **`openai-codex` and `opencode` are present as provider ids.** The Codex this repository's main
> study covers ([`docs/`](../docs/)) is **treated here as a model provider.** The two studies meet at
> this point.
>
> There is also a set `CODEX_TOOL_CALL_PROVIDERS = {openai, openai-codex, opencode}`, with
> `supportsAdditionalTools` and `supportsToolSearch` flags nearby. `AdditionalTools` is the item that
> carries the tool list in Codex's `responses_lite` request shape
> ([`docs/16-responses-chat-adapter.md`](../docs/16-responses-chat-adapter.md) §10.2).
> **Aside implements Codex's request-shape branching.**

> ⚠️ Correction: an initial scan counted `opencode` appearing 100 times, but most of those were the
> ANSI colour variable `openCodes`. The meaningful occurrences are the provider id and the
> `x-opencode-client` / `x-opencode-session` headers.

## 7. Vault cryptography — what the marketing claim rests on

Held at "landing-page claim, unverifiable" in [02 §4](02-aside.md) and [99 §4](99-sources.md).
`AsidePasswordManager` ships **libsodium**, and **the actual call sites** — not merely the library's
exported constants — were confirmed in `background.js`.

| Primitive | Calls | Role |
|---|---|---|
| `crypto_pwhash_str` | 13 | password hashing |
| `crypto_box_seal` | 12 | **anonymous public-key sealing** |
| `crypto_aead_xchacha20poly1305_ietf_encrypt` / `_decrypt` | 7 / 7 | AEAD |
| `crypto_secretbox_easy` / `_open_easy` | 4 / 4 | symmetric |
| `crypto_kdf_derive` | 3 | key derivation |
| `crypto_pwhash(` | 2 | key derivation |

Key derivation parameters show **`ARGON2ID13`** and `memlimit_interactive`.

> 📌 **A standard, well-chosen combination.** Argon2id + XChaCha20-Poly1305 + Curve25519 sealed boxes
> is the modern orthodoxy for secret management. The marketing claim of "hardware-backed E2E
> encryption" **has concrete substance.**
>
> That `crypto_box_seal` appears 12 times is telling. A sealed box is encrypted to the recipient's
> public key such that **even the sender cannot decrypt it** — exactly the primitive that fits
> "never give the agent the raw password" ([02 §4](02-aside.md)).

> ✅ **Resolved later**: Secure Enclave and post-quantum cryptography, unconfirmed at this point, were
> both confirmed — [10 §3](10-aside-enforcement-and-native.md).

## 8. Perception model — where the refs come from

[08 §3](08-aside-code-level.md) established that `snapshot()` returns **virtual ref IDs** like `e31`.
In the daemon, raw CDP calls such as `Accessibility.getFullAXTree` are essentially absent
(`Page.captureScreenshot` appears five times) while `injectedScript` does appear.

> That matches the Playwright-style **aria snapshot** approach — inject a script into the page, build
> an accessibility tree and assign refs of the form `e1`, `e2`, and so on. It is **a different
> implementation path** from Comet calling CDP's `getFullAXTree` through `chrome.debugger`
> ([04 §5](04-comet-architecture.md)).
>
> ⚠️ The body of the injected script was not followed to the end. **Graded as inference.**

## 9. Final comparison table

| Axis | Comet | Aside |
|---|---|---|
| Shell | Chromium + three extensions | **Chromium fork + three extensions** (the same) |
| Agent implementation | MV3 extension (`comet-agent`) | **MV3 extension** (`Aside Browsing Agent`) |
| Custom browser APIs | none published | **eight (`at.studio.Aside.ext.private.*`)** |
| Planning location | **server** (Perplexity backend) | **local daemon** (`127.0.0.1:21420`, 353MB) |
| Perception | CDP `getFullAXTree` → YAML | **injected-script aria snapshot → refs** |
| Action | pixel-coordinate `ComputerBatch` | ref-based locators |
| Models | Perplexity (Max may choose) | **16+ provider ids, BYO subscription/key** |
| Credentials | URL blocking | **libsodium** (Argon2id / XChaCha20 / sealed box) |
| OS-level control | — | **`Aside Computer Use.app`, a separate process** |
| Storage | — | **drizzle ORM (SQL)** |

> 📌 **The largest difference is where planning lives.** The structures are strikingly alike, but
> Comet plans on a server and Aside plans in a 353MB local daemon. That is why "BYO subscription or
> API key" ([02 §9](02-aside.md)) is possible at all — planning is local, so the user's own model
> credentials can be used. **The "local-first" claim has structural grounding.**

## 10. Still unverified

| Item | Status |
|---|---|
| Secure Enclave · post-quantum cryptography | ✅ **Resolved later** — [10 §3](10-aside-enforcement-and-native.md) |
| The injected script's ref-generation logic | ⚠️ §8 is inference; not followed to the end |
| Where Allow/Ask/Deny is actually enforced | ✅ **Resolved later** — [10 §1](10-aside-enforcement-and-native.md) |
| What `Aside Computer Use` can do | ✅ **Partly resolved** — [10 §2](10-aside-enforcement-and-native.md) |
| What goes to a server | ⚠️ Beyond static analysis. Requires runtime observation |
| **GUI and visual design** | ⚠️ **Still unverified** — requires execution, and there is no Linux build |
