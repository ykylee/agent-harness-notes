# SYNTHESIS — Agent harnesses, where two studies cross

> This repository holds two investigations. **[`docs/`](docs/)** read the OpenAI Codex harness out of
> generated schemas and Rust source; **[`browser-agents/`](browser-agents/README.md)** read
> browser-type agents out of product documentation and binaries. This document crosses them to
> separate what belongs to harnesses in general from what belongs to a particular execution surface.
>
> Concept-level notes live in [`ai-workflow/wiki/`](ai-workflow/wiki/index.md); evidence grades live
> in each study's `99-sources.md`. Updated 2026-09-23.

## 1. What a harness is — the intersection

OpenAI's own definition presumes no surface:

> "A capable agent is more than a prompt and a model response. It needs a way to understand a task,
> maintain context over time, inspect relevant information, call tools, expose progress, handle
> failures, **request human approval when necessary**, and return a useful result."

**A harness is the execution system that sits between a model and a task.** That definition contains
neither "shell" nor "browser." Codex and Aside are therefore **two instances of one abstraction.**

| | Codex | Browser-type agents |
|---|---|---|
| Execution surface | **shell · filesystem** | **browser · OS** |
| What it observes | command output, diffs, files | **pages** |
| Principal risk | destructive commands | **indirect prompt injection** |
| Distribution | binary · SDK · managed API | browser fork · extension · library |

> 📌 **A different surface means a different risk.** Codex asks "may I run this command?" A browser
> agent has to ask "**is this page lying to me?**" That question did not exist for the former — shell
> output is not written by an attacker, but a web page is.

## 2. Surface-independent axes — this repository's reusable asset

Overlay the two studies and a set of axes emerges that applies **whatever the surface is.** This is
where to start when designing a new harness.

### 2.1 Approval as a protocol primitive

| | Codex | Aside | Dia |
|---|---|---|---|
| Direction | server → client, 10 request types | daemon **suspension** | approval before effectful actions |
| Effect | **the turn stops** | same | same |
| Vocabulary | `accept` / `acceptForSession` / `decline` / `cancel` plus amendment-carrying variants | **`Allow once` only** — "No lasting permission will be granted" | — |
| If unimplemented | **the turn stalls and never completes** | — | — |

> 📌 **Aside went one step further.** Its approval prompt builds a button array *and* a **numbered
> text fallback**, and every hint reads "or just reply with your answer" — it is designed to be
> **rendered in a chat channel.** App Server's approvals assume a client UI. **If you need remote or
> asynchronous approval, Aside's shape is the answer.**
>
> Conversely, Aside exposes no UI equivalent of `acceptForSession`. That is a deliberately
> conservative choice.

### 2.2 Permissions as declarative policy

| | Codex | Aside |
|---|---|---|
| Base vocabulary | four sandbox values plus `ExecPolicyAmendment` at approval time | declared as a **zod schema** |
| Matching | — | `tool` (glob plus **per-argument eq/regex**) · `browser` (read/modify/download plus URL glob) · `network` (domain glob) |
| Buckets | — | `allow` / `approved` / `deny` / `ask` plus `default` |

> 📌 Not "allow bash" but **"allow bash only when the first argument matches this regex."** Aside's
> expressiveness is the more concrete of the two, and it is the part worth copying.
>
> 📌 Both studies arrive at the **same principle**: **permission level and defence removal are
> different axes.** Aside keeps the sandbox on and passwords hidden even under `full-access`. Codex
> refuses to let project-local config override provider, auth or telemetry keys.

### 2.3 Providers as data

`ModelProviderInfo`'s premise — a provider is data, not a code branch — holds. What the browser study
adds is **who chooses.**

| Product | Chooser |
|---|---|
| Codex | configuration (`model_providers`) |
| **Aside** | **the user** — reuse an existing ChatGPT/Claude subscription over OAuth, or bring a key |
| **Opera Neon** | **the product** — Opera's AI engine routes each task to a model |

> 📌 **"Model-agnostic" names two opposite designs.** The first removes model cost from the adoption
> barrier; the second makes the product answerable for quality. This choice is tied to §2.4.

### 2.4 Control plane / execution plane

The boundary the Agents API declares — **harness (loop, routing, model calls) vs. compute (files,
commands, state)** — is drawn **in a different place by each browser product.**

| Product | Planning | Execution |
|---|---|---|
| Comet | **server** (Perplexity backend) | local extension |
| **Aside** | **local daemon** (`127.0.0.1:21420`) | local browser |
| Opera Neon | **cloud LLM** | local browser |
| Dia | own servers → partner models | local |

> 📌 **This axis decides the model economics.** Planning has to be local for a user's own
> subscription to be usable. Aside's BYO-subscription is a consequence of the local daemon, not a
> marketing choice.
>
> ⚠️ **Check which side a vendor means by "local."** Opera's `llms.txt` says "All AI processes run
> locally"; the product FAQ says "**it uses cloud-based LLMs to generate the plans.**" Two
> first-party sources from the same company disagree.

### 2.5 Capability distribution and units of reuse

Codex's plugins and marketplaces are units of **distribution.** Separately from that, the browser
products each solved **"how do you turn a repeated delegation into a reusable unit?"** — and the
three axes are **orthogonal.**

| Product | Name | Axis |
|---|---|---|
| Opera Neon | **Cards** | **task type** — "handle this kind of work like this" |
| Dia | Skills | **invocation** — called by name |
| Aside | **Routines** | **time** — cron (start a new task) / heartbeat (wake an existing chat) |

> 📌 **Nobody has all three yet.** The cron/heartbeat distinction in particular exists only in Aside
> — for an agent that carries conversational context, "start fresh" and "continue" mean different
> things, and ordinary schedulers only offer the first.

### 2.6 Exposing yourself to other harnesses

| Product | How |
|---|---|
| Codex | `codex mcp-server`, the App Server protocol, `item/tool/call` |
| **Aside** | **`aside mcp`** — "Install the aside-browser skill into your coding agents (Codex, Claude Code, Cursor, OpenCode)" |
| **Opera Neon** | **MCP server** — "external AI tools can connect to your live Neon browser session" |

> 📌 **They reached this independently.** All three expose themselves not as a final product but as
> **an execution surface for another harness.** It looks like a convergence point for the field.

## 3. Surface-specific axes — what the browser study produced

The Codex study has no counterpart to these, **because a shell harness does not have the problem.**

### 3.1 Perception model

A raw DOM is 2MB or more. **The token budget breaks before anything else does.** Four approaches are
in use, and the decisive split is **whether perception and action share a namespace.**

| Product | Perception | Action | Symmetric |
|---|---|---|---|
| Aside | accessibility tree plus virtual refs (`e31`) | `page.locator('e31')` | ✅ |
| Browser Use | Set-of-Mark badges (`[14]`) | `click_element(index=14)` | ✅ |
| Comet | accessibility tree | **pixel coordinates** | ❌ |

> 📌 **When they are symmetric, "clicked somewhere other than what I saw" is structurally
> impossible.** And Aside's `snapshot()` returns `{tree, diff}`, so after an action only the delta is
> read — cost stops growing linearly with conversation length.

### 3.2 Indirect prompt injection

> All the user did was **click "summarize this page."** The result was an OTP from Gmail landing in an
> attacker's hands (Brave's demonstration against Comet).

**The same-origin policy stops helping** — the agent crosses origins with the user's own authority.
As of 2026 this is **unsolved.** OpenAI itself wrote that it is "unlikely to ever be fully 'solved',"
and security maintenance appears among the stated reasons for retiring Atlas.

> 📌 In this study's scope, **only Dia documents concrete defences** — it will not follow
> LLM-generated URLs, will not pass URLs to the LLM verbatim, and makes password fields and
> irreversible action buttons "invisible to the agentic system." It also **states what remains.**

### 3.3 Credential shielding

| Approach | Product | Assessment |
|---|---|---|
| URL blocking | Comet | **enumerative** — a new path defeats it |
| **Value hiding** | Aside | fundamental |
| **Element hiding** | Dia | fundamental, and **broader than credentials** (irreversible buttons too) |

## 4. Where the two studies meet in code

This is not an abstract resemblance. **Codex is inside Aside's daemon binary.**

```js
CODEX_TOOL_CALL_PROVIDERS = new Set([`openai`, `openai-codex`, `opencode`])
// nearby: supportsAdditionalTools, supportsToolSearch
```

`openai-codex` is registered **as a model provider id**, with a `supportsAdditionalTools` flag beside
it. `AdditionalTools` is the item that carries the tool list in Codex's `responses_lite` mode
([`docs/16`](docs/16-responses-chat-adapter.md) §10.2).

> 📌 **A third-party harness absorbed Codex's two request shapes as a per-provider capability flag.**
> `docs/16` recommended that "an adapter must handle both shapes"; here is a real system in which
> exactly that was required. Two studies begun independently met at the same source.

## 5. If you were building one — a combined checklist

### 5.1 Before choosing a surface (surface-independent)

- [ ] Make **approval a protocol primitive.** Without it the turn stalls.
- [ ] Shape approval prompts so they can **render in a channel** — buttons plus a text fallback.
- [ ] Express permissions as **declarative policy.** Reach at least tool globs with per-argument matchers.
- [ ] **Separate permission level from defence removal.** Highest privilege must not mean sandbox off and secrets visible.
- [ ] Apply isolation modes **consistently through credentials.**
- [ ] Model providers **as data**, and decide deliberately **who chooses** among them.
- [ ] Support **command-backed token minting** from day one; it absorbs most bespoke auth schemes.
- [ ] **Decide where planning runs first** — model economics and the privacy story both follow from it.
- [ ] Provide a **unit of reuse**, and **suggest it automatically.** Users do not discover it themselves.
- [ ] **Expose your own tool over MCP.** You may be an execution surface, not a final product.
- [ ] **Keep a deterministic path** (Aside's `repl`) for where the model is weak.

### 5.2 After choosing a browser/OS surface

- [ ] Put **perception and action in one namespace.** Do not make the model predict coordinates.
- [ ] Offer **diffs as a first-class result.** A full tree every step is not affordable.
- [ ] Do not pick screenshots as the primary perception. If you do, design for the **popup compositing problem.**
- [ ] Build a **reading cost ladder** — interactive-only → full → wait → annotated screenshot.
- [ ] Add a **stagnation watchdog.** An agent cannot tell that it is stuck.
- [ ] **Separate page content from user instruction.** This is not optional.
- [ ] **Remove dangerous elements from perception** — password fields, irreversible buttons.
- [ ] Shield credentials by **hiding the value.** URL blocking is enumerative.
- [ ] **Set defaults narrow.** Good cryptography and good defaults are different jobs.

### 5.3 Choosing a shell

| Choice | What it costs |
|---|---|
| Browser fork | **a standing debt of chasing Chromium.** Even OpenAI retired Atlas within ten months |
| Extension | only what extension APIs permit; no browser-chrome UX |
| Library | not a product a person uses |

> ⚠️ **The outer classification can differ from the inner structure.** Both Comet and Aside present
> as native browsers, yet both implement the agent as an MV3 extension. The shell is a distribution
> unit; control lives in the extension layer — which is what lets their release cadences diverge.

## 6. On method

Both studies used the same discipline, and the browser study **added two lessons.**

| Discipline | Detail |
|---|---|
| Committed artifacts over prose | generated schemas and Rust source / product-document originals and binaries |
| No secondary source is settled before cross-checking | Codex: two of five were wrong / browser: adjudicating vendor self-reported benchmarks |
| Inference is labelled as inference | the Windows sandbox / Aside's `approved` bucket |
| Refutations are kept, not deleted | each study's `99-sources.md` |
| **(new) Do not mistake inheritance for a product feature** | post-quantum symbols in a fork — **Chromium already ships them.** The file location had to be separated first |
| **(new) Cross-check primary sources against each other** | Opera's `llms.txt` contradicts its product FAQ. The more specific one wins |

And one practical technique: **try `.md` and `/llms.txt` on a documentation site first.**
Record: OpenAI ✅ · Aside ✅ · Opera ✅ · **Dia ❌** (client-rendered). **It is not universal.**

## 7. Reading order

| Interest | Path |
|---|---|
| The Codex harness itself | [`REPORT.md`](REPORT.md) → [`docs/`](docs/) |
| Browser-type agents | [`browser-agents/README.md`](browser-agents/README.md) |
| **By concept** | [`ai-workflow/wiki/index.md`](ai-workflow/wiki/index.md) — 16 concepts |
| Which claims to trust | [`docs/99-sources.md`](docs/99-sources.md) · [`browser-agents/99-sources.md`](browser-agents/99-sources.md) |

> ⚠️ **Evidence grade differs cell by cell.** Aside was verified down to its binaries; Dia and Neon
> rest on product documentation; Comet relies on third-party reverse engineering. Do not read the
> comparison tables without that asymmetry in mind.
