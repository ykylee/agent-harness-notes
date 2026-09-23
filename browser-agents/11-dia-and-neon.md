# 11. Dia and Opera Neon — from primary sources

> [05](05-comparables.md) stopped at secondary summaries for these two. This is the result of
> re-running the `llms.txt`/`.md` technique against them. Researched 2026-09-23.
>
> Grade: this document rests on **the products' own documentation** (✅ primary). No binary analysis
> was done.

## 1. How the technique fared — one win, one loss

| Target | `llms.txt` | `.md` suffix | Result |
|---|---|---|---|
| **Aside** | ✅ `docs.aside.com/llms.txt` | ✅ works | all 16 product documents obtained as primary text ([02](02-aside.md)) |
| **Opera** | ✅ **`www.opera.com/llms.txt`** (11,613b, text/plain) | — | the Neon entry obtained (§3) |
| **Dia** | ❌ soft 404 | ❌ **does not work** | every path returns the same 31,692b SPA shell |

> 📌 **How Dia fails is itself information.** `help.diabrowser.com` returns **the same byte count of
> Next.js shell for every path**, including `/start`, `/security` and `/release-notes/latest`.
> Appending `.md` changes nothing. The content is entirely client-rendered, so a static technique
> cannot reach it. A real document was found at `www.diabrowser.com/security` instead (§2).
>
> ⚠️ In other words the technique **depends on how a documentation site renders.** When it works you
> gain a lot; when it does not you fall back to the rendered page. It is not universal.

## 2. Dia — the only product that documents prompt-injection defences

Obtained from `www.diabrowser.com/security`. **In this study's scope, Dia is the only product that
documents concrete defences against indirect prompt injection.**

### 2.1 Stated defences

| Defence | Original wording |
|---|---|
| **No following LLM-generated URLs** | "Dia won't automatically open or follow LLM-generated URLs" |
| **No verbatim URL passing** | "Dia won't pass URLs to the LLM verbatim" |
| **Sensitive elements removed from perception** | password fields and irreversible action buttons are "**invisible to the agentic system**" |
| Minimal initial privilege | a chat session "starts with **no access to other tabs** or ability to take write actions" |
| No autonomous navigation | agentic mode cannot "navigate on its own to another website" |
| Approval before third-party writes | "Dia won't insert data into third-party sites without your approval" |

**Actions requiring approval**: form filling, drafting email, creating calendar entries — before
"the assistant can use anything with real-world effects."

### 2.2 It states its own limits

> It can still "Cause unexpected style or tone shifts" or "Nudge content toward misinformation."

> 📌 **This is the most trustworthy part of the document.** It lists defences and also says what
> remains. That is consistent with [07 §6](07-security.md) — prompt injection is not fully solved.

### 2.3 Correcting the verdict in §8 of doc 07

[07 §8](07-security.md) originally said:

> "Against Brave's four mitigation categories, **no product in scope documents having implemented
> input separation (#1).**"

**Partly wrong.** Dia's "does not pass URLs to the LLM verbatim" and "makes password fields and
irreversible buttons invisible to the agentic system" are **sanitisation at the input layer.** Not
identical to Brave's #1 — it does not structurally partition user instruction from page content —
but it is a defence **at the same layer, controlling what enters perception.**

> 📌 Aside **hides the value** of a credential in a vault ([02 §4](02-aside.md)); Dia **erases the
> element** from the agent's perception. Two solutions to one problem. Aside hides the value, Dia
> hides the **element** — and Dia's reaches further, extending past credentials to irreversible
> action buttons.

### 2.4 But it is not local-first

[05 §2](05-comparables.md) followed a secondary source in saying Dia "emphasises local encryption."
That is true of storage, but **AI processing goes through servers.**

| Axis | Detail |
|---|---|
| Local storage | "conversations, history, bookmarks, and files are **encrypted and stored locally**" (algorithm undisclosed) |
| Sync | "**end-to-end encrypted**, and our servers cannot read the data" (method undisclosed) |
| **AI requests** | "The data needed to fulfill your request… is **sent through our servers** to trusted AI partners" |
| Memory | summaries are "created on **our servers** and stored locally" |
| **Collection by default** | "**By default**, we use some content data to improve Dia" — not tied to the account, **retained 30 days then deleted** |
| Models | GPT (OpenAI Azure), Claude (Anthropic, Vertex, AWS), Gemini (Vertex) |
| No training | providers may not "retain or using your data to train their own models" |

> ⚠️ That **collection is the default** is worth noting — the same pattern as Aside's analytics
> sharing defaulting to on.

## 3. Opera Neon — two primary sources that contradict each other

### 3.1 The contradiction

| Source | Claim |
|---|---|
| **`www.opera.com/llms.txt`** | "**All AI processes run locally on the device**, keeping interactions private and fast." |
| **`operaneon.com/faq`** | "Neon Do runs locally within your browser and directly interacts with webpages. **However, it uses cloud-based large language models (LLMs) to generate the plans and instructions it follows.**" |

**The FAQ wins.** It is more specific, it is the product's own FAQ, and the model list (§3.2) backs
it up.

> ❌ **Verdict: `llms.txt`'s "all AI processes run locally" is wrong** — or at best dangerously
> imprecise. What is local is **execution**; **planning is in the cloud.**
>
> 📌 And that distinction is exactly the **planning location** axis of
> [06 §3](06-architecture-axes.md). Neon sits on the same side as Comet — local browser execution,
> server-side model planning. It is why you have to check **which side** a vendor's "local" refers to.

### 3.2 Models — Opera's own routing layer

> "Neon runs on **Opera's AI engine, which is model-agnostic**, using different Google and OpenAI
> models depending on the task. Opera AI **intelligently routes your task to the most appropriate
> model** each time."

In Neon Chat the user may also pick directly:

```
Gemini, Grok, GPT / GPT Pro, Claude Opus / Claude Sonnet,
Deepseek, GLM-5, Qwen3
+ generative models: Veo 3.1, Nano Banana 2, Nano Banana Pro
```

In Neon Do (the agent), **the agent picks the model for the job** — an image model for image
generation, the best browsing-and-synthesis model for research.

> 📌 **The product owns model routing.** Aside lets the user choose a provider
> ([02 §9](02-aside.md)); Neon chooses on the user's behalf. Both call themselves "model-agnostic,"
> in opposite directions.

### 3.3 Neon is an MCP server

> "MCP, or Model Context Protocol, is an open standard that lets different AI tools communicate
> directly with each other. **Opera Neon acts as an MCP server**, which means external AI tools that
> support MCP can **connect to your live Neon browser session**."

> 📌 **The same pattern as `aside mcp`** ([02 §6](02-aside.md)). Two products reached the same
> conclusion independently — **exposing the browser as an execution surface for other agents.**
> Recommendation 9 in [06](06-architecture-axes.md) ("expose your own tool over MCP") looks like a
> convergence point for this field.

### 3.4 Cards — the unit of reuse

> "They instruct Neon **how to handle a specific type of task** without you having to explain it each
> time. They're organized into **decks** grouped by area of work… When you build a workflow that
> works well for you, you can **turn it into a card and reuse it anytime with one click**.
> Cards work across Neon Chat, Neon Do and all Research Agents."

> 📌 [06 §5](06-architecture-axes.md) called "turning repeated delegation into a reusable unit" a
> shared problem. The three products' axes are now clear:
>
> | Product | Name | Axis |
> |---|---|---|
> | **Neon** | **Cards** | **task type** — "handle this kind of work like this." Grouped into decks |
> | Dia | Skills | routines invoked by name |
> | Aside | **Routines** | **time** — cron (a new task) / heartbeat (continuing a chat) |
>
> Neon's Cards hold **methodology, not scheduling.** They are orthogonal to Aside's Routines — one
> product could have both, and none does.

### 3.5 Credentials

> "when you sign into a site and enter your credentials, those credentials are **not sent to any
> third-party servers (such as Opera's)**. The same is true for payment details, which **stay within
> your browser session** and are never sent to Opera or any third-party servers."

> ⚠️ This says credentials **do not go to Opera's servers.** It does not say **the agent cannot see
> them.** That is **a different layer of guarantee** from Aside's value hiding or Dia's element
> hiding. Since planning is in the cloud (§3.1), what is included when page context reaches the model
> is a separate question. Unverified.

### 3.6 No training

> "No. Opera doesn't train models on user data. Opera's AI engine **orchestrates third-party
> models**, and Opera's agreements with providers such as OpenAI and Google prohibit them from using
> Opera users' data to train their models."

The same shape of commitment as Dia's — no first-party training plus contractual prohibition on
providers.

## 4. Updated comparison

| Axis | Aside | Dia | Opera Neon |
|---|---|---|---|
| Planning location | **local daemon** | **through own servers** | **cloud model** |
| Execution location | local | local | local (Neon Do) |
| Model choice | **the user** (BYO subscription/key) | the product (GPT/Claude/Gemini) | **the product routes** (Chat allows choosing) |
| Unit of reuse | Routines (time) | Skills (invocation) | **Cards (task type)** |
| MCP | ✅ `aside mcp` | — | ✅ **MCP server** |
| CLI | ✅ | — | ✅ (mentioned on the product page) |
| Injection defences documented | partial (approval, permissions) | **✅ concretely** | unverified |
| Credential protection | **value hiding** (vault) | **element hiding** (removed from perception) | not sent to servers (agent visibility unverified) |
| Collection by default | analytics sharing on | **content data on** (30 days) | no-training stated |

## 5. Still unverified

| Item | Status |
|---|---|
| Dia's cryptographic algorithms | ⚠️ says "encrypted" without naming a method |
| Dia's E2E sync implementation | ⚠️ same |
| What Neon's agent can see | ⚠️ whether credentials enter the model context is unverified (§3.5) |
| Details of Neon's Tasks | ⚠️ the FAQ answers were not extracted completely |
| Both products' binaries | ⚠️ not analysed. Nothing here is verified to Aside's standard |

> 📌 **Remember the asymmetry**: Aside's claims were verified down to its binaries
> ([08](08-aside-code-level.md), [09](09-aside-browser-internals.md),
> [10](10-aside-enforcement-and-native.md)); Dia and Neon are **taken on their documentation.**
> That a document is good is not the same as an implementation being so.
