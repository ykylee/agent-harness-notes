# SYNTHESIS — Agent harnesses, where two studies cross

> This repository holds two investigations. **[`docs/`](docs/)** read the OpenAI Codex harness out of
> generated schemas and Rust source; **[`browser-agents/`](browser-agents/README.md)** read
> browser-type agents out of product documentation and binaries. This document crosses them to
> separate what belongs to harnesses in general from what belongs to a particular execution surface.
>
> Concept-level notes live in [`ai-workflow/wiki/`](ai-workflow/wiki/index.md); evidence grades live
> in each study's `99-sources.md`.
>
> **[§6](#6-implementation-feedback--what-survived-contact-with-code) is a third kind of evidence**:
> the conclusions below were implemented in a separate repository, and what measurement said about
> them — including where it refuted them — is recorded there. Updated 2026-09-23.

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
> ⚠️ "Default `ask`, never `allow`" does not survive implementation as literally stated — it prompts
> on every read. [§6.1](#61-refuted) has the corrected form.
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

> ⚠️ **Three claims in this section were tested by implementing them and did not hold as stated** —
> the token budget, scoping as compression, and diff as a sublinear cost. The symmetry guarantee
> held as a principle but failed three times as an implementation. See
> [§6](#6-implementation-feedback--what-survived-contact-with-code) before relying on any of them.

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

## 6. Implementation feedback — what survived contact with code

The surface-independent axes of §2 and the perception model of §3.1 were **built**, in a separate
repository (`ykylee/heddle`, private). That repository is deliberately not part of this one — this is
research notes, and `PURPOSE.md` excludes implementation. What comes back here is only the
measurement.

That measurement is worth importing because it is **a grade this repository did not previously
have.** Every other claim in these notes was read out of someone else's artifact: a schema, a Rust
file, a product page, a binary. These were run.

> ⚠️ It cuts the other way too. Implementing a conclusion tests **the conclusion**, not the vendor it
> was drawn from. Nothing below is evidence about Aside, Dia or Comet. Where a claim here is refuted,
> what failed is this repository's reasoning.

### 6.1 Refuted

| Claim | Where | What measurement said |
|---|---|---|
| A pruned accessibility tree keeps a page around 1.5–3k tokens | §3.1 | **3.6× over.** A Wikipedia article: 515 interactive nodes, ~10,948 tokens. Hacker News ~3,761, 25% over. Pruning halves the tree (515 of 1,220 nodes) and the remainder is still the page — an article has 515 links and no rule removes them without removing the content |
| Scoping to a region is how you get a large page into budget | §3.1 | **The densest region is the page.** Scoping to Wikipedia's `main` returned 94% of the unscoped cost; on Hacker News the top region is the table holding every story, so 100%. Scope turned out to be an *intent* mechanism — worth having, useless as compression |
| Diff keeps context cost sublinear in conversation length | §3.1 | **Only on a quiescent page.** Wikipedia produced 139 lines of delta after 1.5s with no action taken — its own JavaScript collapsing sections and dismissing a banner. Worse than expensive: *misleading*, because none of it was the agent's doing |
| "Default `ask`, never `allow`" | §2.2 | **Unusable as literally stated** — it prompts on every snapshot, including reads. The shipped default allows `browser read` and asks for everything that changes state. The spirit held; the sentence did not |
| A cross-origin iframe is a case a plain extension cannot reach, so a browser fork may be needed for it | §3.1, §5.3 | **Refuted.** Per-frame evaluation over CDP reads a genuinely cross-origin child document: `walked=2, unreachable=0`, four interactive elements lifted out of the embedded origin. This removes the one perception argument for forking |

The last row is the one with a product consequence. Combined with the research finding that Comet
and Aside both implement the agent as an MV3 extension (§5.3), it means **the extension is the
control layer and a fork is only a distribution shell** — you build, find a specific wall, and fork
to get past it, rather than forking first.

### 6.2 Confirmed

| Claim | Result |
|---|---|
| Approval must be able to fail closed (§2.1) | A policy that can `ask` with no approval channel **refuses** rather than degrading to allow. Enforced, not documented |
| An approval request is data, not a rendering (§2.1) | One request object serves a text renderer and would serve a GUI or chat renderer with no core change — the property found in Aside's suspension system |
| Conflict resolution must be written down (§2.2) | `deny > ask > allow > default`. `ask` beating `allow` is the deliberate part: a config listing both is a mistake, and the safe reading of a mistake is to ask |
| Approval should not grant lasting permission (§2.1) | "Allow once" and "Deny", with no "always allow" |
| Secrets travel as handles, not values (§3.3) | Implementable; plaintext exists only between executor and adapter. Not yet stress-tested |
| The agent loop is a consumer of the core, not the core (§2.4) | The core has no model in it, and the driver is not visible from it — checked by grep, not assumed |

### 6.3 The one that is neither — and is the most useful thing that came back

§3.1 argues that a **symmetric perception/action namespace** makes "the agent acted on something
other than what it saw" structurally impossible. As a principle that survived. As an implementation
it failed **three times, the same way each time**:

| Axis that was not in the identifier | What happened |
|---|---|
| **Snapshot generation** | Refs were bare counters. `e54` from an earlier snapshot silently resolved to a different element in the current one — `e54` exists in almost any large tree |
| **Frame** | The same DOM path means a different element in a different document. Before this was fixed, a page with a payment iframe and a consent iframe showed **1 of its 5 interactive elements — 80% invisible** |
| **Process life** | The host process is killed (an MV3 service worker is, when idle) and its replacement restarts the counter, reissuing generation 1. A held ref matched it and resolved, with no error, to an unrelated element: `"Beta report"` → `"Save draft"` |

> 📌 **The guarantee is not a property of the design. It is a property of the identifier.** A
> symmetric namespace prevents the misfire only while the name of a thing carries every axis that
> distinguishes it from another thing. Each of the three axes was invisible until something crossed
> it, and each was found by a different means — a failing assertion, a code review, and a question
> asked about a platform's lifecycle.

This generalises past the browser. Codex's `conversationId` / `itemId` identifiers face the same
question the moment a harness process can restart while a client still holds them.

### 6.4 What this does not license

The feedback covers the axes that were built: perception, action, policy, approval, secrets. It says
nothing about capability distribution (§2.5), exposing a harness to other harnesses (§2.6), or
indirect prompt injection (§3.2) — **the last of which is the field's central risk and remains the
least tested claim in this repository.** Defences against it were designed here and have not been
attacked.

## 7. On method

Both studies used the same discipline, and the browser study **added two lessons.**

| Discipline | Detail |
|---|---|
| Committed artifacts over prose | generated schemas and Rust source / product-document originals and binaries |
| No secondary source is settled before cross-checking | Codex: two of five were wrong / browser: adjudicating vendor self-reported benchmarks |
| Inference is labelled as inference | the Windows sandbox / Aside's `approved` bucket |
| Refutations are kept, not deleted | each study's `99-sources.md` |
| **(new) Do not mistake inheritance for a product feature** | post-quantum symbols in a fork — **Chromium already ships them.** The file location had to be separated first |
| **(new) Cross-check primary sources against each other** | Opera's `llms.txt` contradicts its product FAQ. The more specific one wins |
| **(new) A document describing behaviour is not evidence the behaviour exists** | In the implementation, a design document and a source comment both claimed iframe contents were included while the code walked only the main frame. Documentation and implementation had simply diverged, and nothing failed until it was measured. **This repository reads documents for a living** — §6 is the only place its claims were checked against something that runs |
| **(new) Building a conclusion is a way of testing it** | Five of the conclusions in §2–§3 were refuted by implementing them (§6.1). All five had survived reading |

And one practical technique: **try `.md` and `/llms.txt` on a documentation site first.**
Record: OpenAI ✅ · Aside ✅ · Opera ✅ · **Dia ❌** (client-rendered). **It is not universal.**

## 8. Reading order

| Interest | Path |
|---|---|
| The Codex harness itself | [`REPORT.md`](REPORT.md) → [`docs/`](docs/) |
| Browser-type agents | [`browser-agents/README.md`](browser-agents/README.md) |
| **By concept** | [`ai-workflow/wiki/index.md`](ai-workflow/wiki/index.md) — 16 concepts |
| **Which conclusions were tested by building them** | [§6](#6-implementation-feedback--what-survived-contact-with-code) — five refuted, six confirmed |
| Which claims to trust | [`docs/99-sources.md`](docs/99-sources.md) · [`browser-agents/99-sources.md`](browser-agents/99-sources.md) |

> ⚠️ **Evidence grade differs cell by cell.** Strongest first: the claims in [§6](#6-implementation-feedback--what-survived-contact-with-code)
> were measured in a running implementation; Aside was verified down to its binaries; Codex was read
> out of generated schemas and Rust source; Dia and Neon rest on product documentation; Comet relies
> on third-party reverse engineering. Do not read the comparison tables without that asymmetry in
> mind — and note that §6 grades **this repository's own conclusions**, not any vendor's.
