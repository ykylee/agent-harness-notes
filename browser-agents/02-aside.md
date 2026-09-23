# 02. Aside — features, composition, structure

> Sources: the whole of `docs.aside.com` read **as raw Markdown** (`/llms.txt` is the index; append
> `.md` to any page for the original). The landing pages are marketing copy and were not used as
> evidence. Extracted 2026-09-22.

## 1. In one sentence

> "The most intelligent AI assistant, but it's a browser."

Aside is a **standalone Chromium desktop browser**, not an extension. It acts as an everyday browser
and hands the page over to an agent when needed. The product's pitch opens by attacking its
competitors: *"Today's AI browsers are broken. They never complete a task."*

The bet: **the surface is the logged-in web itself, not a list of integrations.** Going into sites
and working the way a person does covers far more ground than any set of connector APIs.

## 2. Feature map

| Feature | What it is |
|---|---|
| **Browser Agent** | Multi-step work across logged-in sites — email, dashboards, internal tools, files |
| **Aside Vault** | "The first password manager built for agents." Fills credentials **without giving the agent the raw password** |
| **Memory** | Accumulates context from browsing, chats and tasks. Stays on the device |
| **Ultrabrowse** | A deeper mode for source-heavy research and comparison (Pro and above) |
| **Routines** | Recurring work — cron and heartbeat forms |
| **Side panel** | Start a task with the page you are looking at attached as context |
| **CLI / MCP / REPL** | Launch browser work from a terminal or an external tool |
| **Channels / Cloud handoff** | Remote control and cloud handoff (Pro and above) |

## 3. Structure — the permission model is the centre of the design

Permissions get the most space in Aside's documentation. Control points divide into **three zones.**

| Zone | What it governs |
|---|---|
| **Sandbox** | OS-level isolation |
| **File permissions** | folder access |
| **Tool permissions** | Allow / Ask / Deny per capability |

> 📌 The documentation covers only the vocabulary below. **The real policy engine is considerably
> richer** — tool globs, per-argument eq/regex matchers, browser and network matchers, and a fourth
> bucket (`approved`) that appears in no document. The full picture from code is in
> [10 §1](10-aside-enforcement-and-native.md).

### 3.1 Rule vocabulary

| Rule | Behaviour |
|---|---|
| `Allow` | "Let the agent use the capability without asking" |
| `Ask` | Requires confirmation before proceeding |
| `Deny` | Blocks. **Takes precedence** |

That Deny wins is stated explicitly — the adjudication when allow and deny overlap is not left vague.

### 3.2 Session permission modes

| Mode | Meaning |
|---|---|
| `Read only` | "Let Aside inspect browser and file context without changing your files" |
| **`Guard`** (default) | Works in approved folders and asks about anything else |
| `Full access` | "Let Aside read and write anywhere on the computer" |

Settings apply at **two levels** — agent defaults under `Settings > Agents`, and a per-session
override attached to each task.

> 📌 **Worth copying**: saved password values stay **hidden from the AI even in full-access mode.**
> Permission level and credential exposure are kept on **separate axes.** "Highest privilege" does
> not mean "can see everything." Access policy and target URL are both checked before autofill.

### 3.3 Task modes

| Mode | Behaviour |
|---|---|
| `Default` | "Run the task in the normal browser profile" |
| `Incognito` | Runs without normal profile state; leaves no browser state behind |

**The agent cannot use the password manager in an incognito session.** Isolation is applied
consistently through credentials.

## 4. Vault — credential design

The claim: *"passwords [are filled] into websites without showing them to the agent."*

| Axis | Detail |
|---|---|
| AI access policy | `Always allow` (default) / `While unlocked` / `Never` |
| Per-item override | Imported items can override the global policy individually |
| Biometric unlock | Touch ID / Windows Hello — **changes how the vault is opened, not what the agent may do once it is** |
| Import | 1Password, Apple Passwords, Bitwarden, Chrome, Dashlane, Edge, Firefox, LastPass CSV, generic CSV (`name,url,username,password`) |
| Landing-page claims | hardware-backed E2E encryption, Secure Enclave, post-quantum cryptography, audit logging |

> ✅ **Verified later**: the encryption claims turned out to have substance — libsodium with Argon2id,
> XChaCha20-Poly1305 and sealed boxes, plus real Secure Enclave key-pair creation, ML-KEM-768 and a
> dedicated audit-log directory. See [09 §7](09-aside-browser-internals.md) and
> [10 §3](10-aside-enforcement-and-native.md). Note that **verifying them required binary analysis** —
> no product document supports any of it.

> ⚠️ The default is `Always allow`, the loosest setting. The design is good; the default points the
> other way.

## 5. Memory

| Axis | Detail |
|---|---|
| Inputs | browsing history, chats, tasks |
| Retention | `Never forget` / `30 days` / `90 days` |
| Management | `Settings > Memory` — Overview (inspect and edit) / History (changes) / Configure (retention) |
| Location claim | "stays local on your device and is never shared" |

> ✅ **Verified later**: memory really is **plain Markdown files** — the CLI bundle states it and
> ships `aside memory show MEMORY.md` and `aside memory path`. Direct editing is forbidden, though;
> writes go through the agent. [08 §4](08-aside-code-level.md).

## 6. Developer surface — CLI, MCP, REPL

The least-publicised part of the product and structurally the most interesting. **The browser is also
exposed as an automation endpoint.**

```bash
# Install (macOS; Linux works too, though no document says so — see 08 §2)
curl -fsSL https://releases.aside.com/install.sh | bash
aside --update

# A browser task from the terminal
aside "Open localhost:3000 and run a smoke test"
aside --session <session-id> "Continue"

# Account switching
aside account list | status | use u1
aside --account u1 "..."

# Expose as an MCP server — register in mcp.json and external clients attach
aside mcp

# A REPL for deterministic browser steps
aside repl "const p = await openTab('https://example.com')"
```

Three layers, split by purpose:

| Surface | Character | Use |
|---|---|---|
| `aside "<task>"` | natural language | delegate to the agent |
| `aside mcp` | protocol | **another agent uses Aside as a tool** |
| `aside repl` | deterministic | "direct page inspection, screenshots, downloads, or deterministic browser steps" |

> 📌 **What this implies structurally**: the product offers **both a path that trusts the model and a
> path that does not.** Where the agent is unreliable you can drop to a deterministic script. And
> `aside mcp` makes Aside **an execution surface for other harnesses** rather than a final product —
> the same shape as the layered opening described in this repository's other study
> ([`docs/01-overview.md`](../docs/01-overview.md)).

## 7. Platforms and releases

| Axis | Detail |
|---|---|
| Engine | Chromium |
| macOS | documented as **15.0 or later** |
| Windows | **official as of v1.0.914.1** |
| Current version | v1.0.922.1 (Chromium 153.0.8010.53) |
| Cadence | several releases per week; Chromium every one to two weeks |
| Import | history, cookies, bookmarks. Safari requires a `File > Export` ZIP |

> ⚠️ **Internal inconsistency**: `get-started.md` lists only "macOS 15.0 or later" as a requirement
> while the changelog records official Windows support. The get-started page is probably stale —
> verdict withheld. **And in fact the CLI supports Linux as a first-class target**
> ([08 §2](08-aside-code-level.md)), which no document mentions at all.

Several releases a week, chasing Chromium every week or two, is the **browser maintenance debt** from
[01 §3](01-landscape.md) made concrete. If the secondary reports of a three-person team are right,
that pace is notable.

## 8. Pricing

| Plan | Price | Credits | Key inclusions |
|---|---|---|---|
| Free | $0 | 500/mo | BYO subscription, 3 routines, password manager, memory |
| **Pro** | **$20/mo** | 3x | Ultrabrowse, unlimited routines, **Channels (remote control)**, **cloud handoff** |
| **Max** | **$200/mo** | 40x | early-access programme |
| Enterprise | contact | — | team agent management, seats and billing, shared profiles, agent credential handling |

> ⚠️ **Inconsistency on record**: the help documentation says Max is "30x Free usage"; the pricing
> page says "40x." Which is current cannot be determined. **Neither defines what one credit is.**

## 9. Models — harness and model kept separate

All three routes are supported.

| Route | Detail |
|---|---|
| **Aside** | Models included with the plan. Free gets the free model set; Pro/Max get priority models |
| **Subscription** | Reuse an existing subscription — ChatGPT Plus/Pro, Claude Pro/Max, GitHub Copilot, over an **OAuth sign-in flow** |
| **API** | Bring a key — Anthropic, OpenAI, OpenRouter, Google, xAI, Vercel AI Gateway, Cloudflare AI Gateway |

> 📌 **"Reuse your subscription" is a clever move.** Pulling in the ChatGPT or Claude subscription a
> user already pays for, over OAuth, **removes model cost from the adoption barrier.** That is why
> the Free plan leads with "Bring your own subscription." The harness charges for itself and lets the
> user's existing spend cover the model.

No specific model versions are named in the documentation. **The daemon binary carries far more
provider ids than the docs list** — see [09 §6](09-aside-browser-internals.md).

## 10. Routines

| Type | Behaviour |
|---|---|
| **Cron** | Starts a **new task** on a schedule — an independent repeat such as a weekly summary |
| **Heartbeat** | **Wakes an existing chat and continues it** — when the same context should resume later |

- Overlapping runs are **skipped.** A routine is **paused** when its target chat is unavailable.
- **Suggestions**: Aside scans for recurring work and proposes draft routines, which the user edits,
  activates or discards.
- Limits: 3 on Free, unlimited on Pro and above.

> 📌 The cron/heartbeat distinction is precise. Recurring work carries two different meanings —
> "start fresh" and "continue" — and most schedulers offer only the first. An agent that holds
> conversational context needs the second.

## 11. What a custom harness should take from this

- [ ] **Keep permission level and credential exposure on separate axes.** Passwords stay hidden even under full access
- [ ] **State that Deny wins.** Write the conflict adjudication into the documentation
- [ ] Apply isolation modes **consistently through credentials** (no vault in incognito)
- [ ] Open **all three surfaces** — natural language, protocol (MCP), deterministic (REPL). Drop to the deterministic path where the model is weak
- [ ] Distinguish **"start fresh" from "continue"** for recurring work
- [ ] Let the **user's own subscription** stand in for the model, and model cost leaves the adoption barrier
- [ ] Watch which way your defaults point — Aside's credential default is the loosest, `Always allow`
