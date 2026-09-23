# 04. Perplexity Comet — architecture

> Sources: Zenity Labs' reverse-engineering record (extension bundles and service-worker analysis),
> Wikipedia (dates and platforms), Brave's security research (§5). This is **reverse-engineered
> implementation, not a vendor-guaranteed specification** — by this repository's grading, "observed
> implementation" ([99](99-sources.md) §5).

## 1. Why look at Comet closely

Open it up and Comet is **a browser implemented as three extensions.** A useful case of the outer
classification and the inner structure diverging.

> ❌ **Correction (2026-09-23)**: this paragraph originally read "the **exact opposite structure**
> to Aside." **That was wrong.** Opening Aside's browser binary showed its agent is also an **MV3
> Chrome extension** (`Aside Browsing Agent`) — [09 §3](09-aside-browser-internals.md).
> The two are not opposites; they made **the same structural choice.** The real difference is not
> the shell but **where planning runs** (Comet: server; Aside: local daemon).
> The wrong statement is kept rather than deleted, with its verdict attached.

## 2. Four components

| Component | Role |
|---|---|
| **Perplexity API Backend** | "Where the AI model lives, plans tasks, and issues commands" — **model and planning live on the server** |
| **UI** | the user interface |
| **Three custom Chrome extensions** | the actual browser control |
| **Chromium** | the browser itself |

> 📌 **The decisive difference: planning lives on the server.** The backend plans the task and
> **issues commands**; local extensions carry them out. Aside advertises local-first and accepts the
> user's own API keys and subscriptions; in Comet the control loop itself runs on Perplexity's
> infrastructure.

## 3. The three extensions

| Extension | Contents |
|---|---|
| **comet-agent** (`agents.crx`) | A **700KB service worker** implementing a full RPC system that receives commands from the backend. The core router is `dispatchRpcRequest`, which passes incoming requests through security validation to handlers |
| **Comet** (`perplexity.crx`) | Tab lifecycles, the sidecar AI panel, split-view sessions. PDF parsing and exception monitoring |
| **Comet Web Resources** (`comet_web_resources.crx`) | A local CDN for UI assets. **No permissions, no background script** |

Extensions auto-update from `https://www.perplexity.ai/rest/browser/update-crx` — **central control
is retained.**

> 📌 The separation of concerns is clean: what needs permissions (agent), browser integration
> (Comet), and entirely unprivileged static assets (Web Resources). That the third has neither
> permissions nor a background script is **deliberate least privilege.**

## 4. Dual-channel communication

Two parallel streams coordinate automation.

| Channel | Endpoint | Purpose |
|---|---|---|
| **SSE** | `/rest/sse/perplexity_ask` | streams model reasoning and conversational responses |
| **WebSocket** | `wss://www.perplexity.ai/agent` | high-frequency bidirectional RPC for browser automation |

The sidecar unpacks incoming `entropy_request` messages and forwards them to extensions through
Chrome's extension messaging API.

> 📌 **Separating the conversational flow from the automation flow onto different transports** is a
> design judgement. A stream a human reads (SSE, one-way, latency-tolerant) and machine control
> (WebSocket, bidirectional, latency-sensitive) have different requirements. Contrast the App Server
> in this repository's other study, which handles both over a single bidirectional JSON-RPC
> ([`docs/02-app-server-protocol.md`](../docs/02-app-server-protocol.md)).

## 5. Agent perception — the accessibility tree

The model sees the page as a **"simplified HTML representation with special annotations."**

The `ReadPage` RPC calls `chrome.debugger` to use Chrome's **`Accessibility.getFullAXTree`** and
returns a **YAML representation of the accessibility tree.**

> 📌 An important choice. Not screenshots (pixels) and not the raw DOM but the **accessibility tree**
> as the perceptual basis. It arrives already refined into "meaningful interactive elements," which
> is token-efficient, and it is the same representation screen readers use, so **the semantics are
> already settled.** The three approaches are compared in [06 §2](06-architecture-axes.md).

## 6. The action vocabulary

| RPC | Contents |
|---|---|
| **`ComputerBatch`** | Executes sequences of low-level actions (clicks, drags, scrolls, keystrokes) **using raw pixel coordinates** |
| `FormInput` | form entry |
| `Navigate` | navigation |
| `GetPageText` | text extraction |
| `TabsCreate` | tab creation |
| **`CreateSubagent`** | **spawns a subagent** |

> 📌 The asymmetry is interesting — **perception in the accessibility tree (semantics), action in
> pixel coordinates (geometry).** Reading uses a refined semantic structure; manipulation drops to
> coordinates. Contrast Browser Use, which **binds perception and action to the same index space**
> ([05 §5](05-comparables.md)) — Comet is more flexible but vulnerable to coordinate error.

The presence of `CreateSubagent` means **multi-agent delegation sits at the protocol level.**

## 7. Security boundaries

Two validation functions constrain the agent.

| Function | What it blocks |
|---|---|
| **`isInternalPage`** | `chrome://settings`, `chrome://password-manager`, `comet://` URLs |
| **`isUrlBlocked`** | `file://` filesystem access, disallowed document types, **administrator blacklists via managed storage**, user-configured domain blacklists |

> 📌 Explicitly blocking `chrome://password-manager` is **credential isolation at the URL level.**
> A different approach from Aside, which **never gives the agent the credential in the first place**
> ([02 §4](02-aside.md)) — Comet says "you cannot go to that page," Aside says "you never see the
> value."
>
> Taking administrator blacklists from **managed storage** is a design made for enterprise
> deployment.

## 8. Facts

| Axis | Detail |
|---|---|
| Engine | Blink (Chromium) |
| Released | Windows/macOS 2025-07-09 / Android 2025-11-20 / iOS 2026-03-18 |
| Requirements | Windows 10+, macOS Big Sur+, Android 12+, iOS 18+, visionOS 2.0+ |
| Pricing | premium-only at first → free in 2025-10 → agent mode free in 2026-03 |
| Models | Max subscribers can pick the agent model (default Opus 4.6, alternative Sonnet 4.5) |

## 9. Security history

| Incident | Detail |
|---|---|
| **Indirect prompt injection** (Brave, 2025) | Page content is not separated from user instruction; email and OTP exfiltration demonstrated. Detail in [07](07-security.md) |
| **CometJacking** | Sensitive personal data exfiltration. Perplexity initially disputed the impact, then independently found and patched it |

> Both **follow from the architecture** rather than being implementation bugs. Where model and
> planning live on a server and page content enters the context directly, this class of thing is
> structurally possible.

## 10. Structural contrast with Aside

| Axis | Comet | Aside |
|---|---|---|
| Control surface | native browser + **three extensions** | **Chromium fork + three extensions** (the same) |
| Planning location | **server (Perplexity backend)** | **local daemon `127.0.0.1:21420` (353MB)** — confirmed structurally |
| Models | Perplexity-supplied (Max may choose) | **BYO subscription / BYO API key / bundled** |
| Perception | accessibility tree (YAML) | **accessibility tree plus virtual ref IDs** ([08](08-aside-code-level.md)) |
| Action | pixel-coordinate batches plus high-level RPC | **ref-based Playwright locators** — symmetric |
| Credentials | isolated by **URL blocking** | **libsodium vault** (Argon2id / XChaCha20 / sealed box) |
| Transport | dual SSE + WebSocket | local daemon plus tRPC (external endpoints unconfirmed) |
| Developer surface | none published | **CLI · MCP · REPL** |

> 📌 **Update (2026-09-23)**: the Aside column originally had many "not published" cells, because
> Comet had been reverse-engineered and Aside had not. **Opening Aside's CLI and browser binaries**
> filled most of them — [08](08-aside-code-level.md), [09](09-aside-browser-internals.md),
> [10](10-aside-enforcement-and-native.md). The original warning — do not read a difference in
> available information as a difference in product maturity — proved itself exactly.
