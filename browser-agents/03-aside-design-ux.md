# 03. Aside — design and UI/UX

> Sources: raw Markdown from `docs.aside.com` (`browser-basics.md`, `side-panel.md`, `tasks.md`,
> `ultrabrowse.md`, `security.md`). This is **the interaction model the documentation specifies**,
> not a visual analysis from screenshots. Visual language — colour, typography — cannot be confirmed
> this way and is not covered.
>
> **GUI pass 2026-09-27** (macOS, Aside 1.0.922.1, one passive screenshot): ✅ a left sidebar in three sections —
> `Bookmarks`, `Chats` (with `New Chat`), `Tabs` (vertical tab list) — and an `Ask Aside` button at the right of the
> toolbar, matching the side-panel model below. Split tabs and the agent at work were not seen.

## 1. The core design problem

The UX difficulty of a browser-type agent reduces to one thing.

> **The same window does two jobs — it is the browser I use and the browser the agent uses.**

Four questions follow:

| # | Question | Aside's answer |
|---|---|---|
| 1 | **Where** do I start a task | four entry points (§2) |
| 2 | What do **I** see while the agent works | split tabs (§4) |
| 3 | How is context **handed over** | the side panel's page attachment (§3) |
| 4 | How do I **correct** a running agent | Queue / Steer (§5) |

## 2. Four entry points, graded by weight

| Entry point | Weight | When |
|---|---|---|
| **Ask AI** (new-tab omnibox) | light | start straight from the browser UI. The omnibox has Search and Ask AI modes |
| **Side panel** | medium | start a task **anchored to the page you are looking at** |
| **Task page** | heavy | multiple sites, multiple accounts, file work |
| **CLI** (`aside "..."`) | external | from a terminal |

The task composer's placeholder exposes the intent directly — **`"Ask AI a task, @ for context"`**.
`@` is the context-attachment sigil. The documentation advises naming **the site, the desired outcome
and any constraints** for best results.

> 📌 Putting Search and Ask AI **in the same place but as modes** is notable. Search and delegation
> were not split into separate UI. It reuses the habit users already have of typing intent into the
> address bar.

## 3. Side panel — making context attachment explicit

The best-designed part. Opening the side panel:

1. **Shows the page attachment as `title + hostname`** — you can see what is being handed over
2. Keeping it lets Aside read that page; **removing it starts without it**
3. **Drafts are kept per tab** — leave and come back and the draft is still tied to the tab you
   started in

> 📌 **Making context attachment visible and removable** is the key move. Most sidebar AIs treat
> "reads the current page" as an implicit default; Aside materialises it as a **removable chip.**
> That also matters for prompt injection ([07-security.md](07-security.md)) — the user can **see**
> whether page content entered the context.

> 📌 **Tying drafts to tabs** is a small detail but the right one. Browser work scatters across tabs
> and users move between them; a single global draft would be destroyed by that movement.

## 4. Split tabs — observability as layout

`Cmd/Ctrl+Shift+\` (or `Cmd/Ctrl+Shift+-`) shows two pages at once. Of the four use cases the
documentation gives, **the last two are agent-specific.**

| Use case | Character |
|---|---|
| comparing product pages | ordinary browsing |
| keeping a source document visible while filling a form | ordinary browsing |
| **watching a task execute on the target site** | agent |
| **placing the task transcript beside the page being driven** | agent |

> 📌 One of the central UX ideas in this product. **The user is not pushed out** while the agent
> drives a page: the agent works on one side, the user watches on the other. Instead of a mode switch
> that says "the agent has the screen," it is solved **by splitting space.**
>
> Contrast: Atlas solved it by giving the AI a cursor and **tinting the browser UI blue** — that is,
> **by marking a mode** ([05](05-comparables.md) §1). Splitting the screen versus painting a mode on
> it: two answers to the same problem.

## 5. Queue vs. Steer — the mid-run intervention model

Chosen under `Settings > Agents > Chat`.

| Mode | Behaviour | Use when |
|---|---|---|
| **Queue** | a new message applies **after the current run finishes** | you want to see the current path through |
| **Steer** | the message **enters the running turn** for live adjustment | you need an immediate correction |

> 📌 **Any tool with long autonomous runs needs this distinction.** If it is ambiguous whether typing
> something means "interrupt now" or "next in line," the user simply stops speaking while the agent
> runs. Exposing it as a setting suggests the preference genuinely varies by person.
>
> It is the same problem as `turn/steer` in this repository's other study — see
> [`docs/12-product-surface.md`](../docs/12-product-surface.md).

## 6. Results — files are first class

The task detail page **shows the files a task created or changed.** Images, PDFs, HTML and text
preview inline. Transcripts are stored in the task folder, and generated files persist until the task
is deleted. Incognito tasks leave no browser state.

> 📌 Making the **artifact, not the chat log, the protagonist of the result screen** suits a
> delegation tool. What was produced matters more than what was said.

## 7. Selection shortcuts — the lasso

Defaults:

| Selection kind | Default actions |
|---|---|
| Text selection | Summarize, Translate |
| **Lasso selection** | Copy code, Search image |

`Settings > Lasso` allows disabling, reordering, editing, deleting and adding.
Templates take variables — `{text}`, and for lasso also `{code}` and `{image}`.

> 📌 Having a **lasso (region selection)** is distinctive. Text selection alone makes it hard to grab
> a code block or an image precisely. And the shortcuts are **user-defined templates**, not a fixed
> menu — users can register their own prompts as standing actions.

## 8. Full keyboard shortcuts

| Function | Binding |
|---|---|
| Toggle Sidebar | `Cmd/Ctrl+S` |
| **Ask Aside** | `Cmd/Ctrl+E` |
| **New Task** | `Cmd/Ctrl+Shift+E` |
| Copy URL | `Cmd/Ctrl+Shift+C` |
| Split tab | `Cmd/Ctrl+Shift+\` |
| Split tab (alternate) | `Cmd/Ctrl+Shift+-` |

> 📌 `Cmd+E` is a light question, `Cmd+Shift+E` real work. **Adding Shift to the same key raises the
> weight** — a consistent rule the hand learns without the user memorising the relationship.
>
> ⚠️ Binding `Cmd/Ctrl+S` to the sidebar toggle is aggressive, though. `Cmd+S` is Save on the web,
> and the documentation says nothing about the collision.

## 9. Ultrabrowse as a mode selection

Ultrabrowse is not a separate screen but **an entry in the model picker under "Reasoning."** Free
users who select it get an upgrade prompt for Pro.

| Normal task | Ultrabrowse |
|---|---|
| single-page questions, basic search | research needing citations, vendor/product comparison, migration planning, security/compliance/pricing checks across several sites |

> 📌 **Expressing depth as a model choice rather than a separate feature** is clean. Users already
> know where they pick a model, and they pick "deeper" there. No new concept to learn.
> It doubles as the **paid conversion point** — the place where you choose weight is also the
> billing boundary.

## 10. Approval flow

- Landing-page claim: sensitive actions such as payments, posts and messages **require human
  approval**
- Documentary support: the `Ask` permission rule, and `Guard` mode asking about folders outside the
  approved set
- "request approvals" appears among the actions a running task can take

> ✅ **Resolved (2026-09-23)**: the daemon's **suspension** system *is* the approval UI —
> `Allow once` / `Confirm`·`Cancel` / up to five options, with the hint *"or just reply with your
> answer."* Decisively, it builds **a button array and a numbered text fallback together** — it is
> designed to be **rendered in a chat channel (Slack/Discord).** There is no "always allow," and it
> states that **no lasting permission is granted.**
> Detail: [10 §1.5](10-aside-enforcement-and-native.md).

## 11. What to take from this UX

| # | Principle | Aside's implementation |
|---|---|---|
| 1 | **Make context attachment visible — and detachable** | the `title+hostname` chip in the side panel |
| 2 | **Give observability through space, not a mode switch** | split tabs |
| 3 | **Let the user choose what an intervention means** | Queue / Steer |
| 4 | **A delegation tool's result is an artifact, not a conversation** | file previews on the task detail page |
| 5 | **Express weight as a shortcut modifier** | `Cmd+E` / `Cmd+Shift+E` |
| 6 | **Put depth inside an existing choice, not a new concept** | Ultrabrowse in the model picker |
| 7 | Bind drafts to their **work context (the tab)** | per-tab side-panel drafts |
| 8 | **Shape approval prompts so a channel can render them** | buttons plus a numbered text fallback |

> Limitation: this analysis rests on **the interactions the documentation specifies.** The actual
> visual design, animation, the visual representation of agent progress and the appearance of error
> states require running the product. None of that was investigated, and none of it was filled in by
> guesswork.
