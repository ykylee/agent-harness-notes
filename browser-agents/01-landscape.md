# 01. The field — browser-type agents in 2026

> Researched 2026-09-22. This field went from research demo to mass-market product in fifteen months
> and still moves weekly. Every date below is primary or cross-confirmed; grades are in
> [99-sources.md](99-sources.md).

## 1. Three classes — the criterion is the control surface

Three quite different things hide inside the single phrase "browser agent." What separates them is
neither the model nor the feature set but **where the agent grips the browser.**

| Class | Control surface | Examples | What the user sees |
|---|---|---|---|
| **A. Native AI browser** | builds the browser itself | Aside, Comet, Dia, Opera Neon, (former) Atlas | you switch your daily browser |
| **B. Extension / attached** | attaches to an existing browser | Claude for Chrome, Gemini in Chrome | a panel appears in the Chrome you already use |
| **C. Library / infrastructure** | code drives a headless browser | Browser Use, Stagehand, Skyvern | a program uses it, not a person |

This choice **determines permissions, credentials and the security boundary entirely.** Details in
[06-architecture-axes.md](06-architecture-axes.md).

> Caution: the line between A and B is blurrier in implementation than it looks. Comet is **a native
> browser implemented as three extensions** ([04](04-comet-architecture.md)) — and so is Aside
> ([09 §3](09-aside-browser-internals.md)). The outer classification and the inner structure can
> differ.

## 2. Timeline

| Date | Event | Significance |
|---|---|---|
| 2025-05 | Opera Neon limited release | Among the first consumer browsers to ship agentic features |
| 2025-07-09 | **Comet** released (Windows/macOS) | Perplexity moves down into the browser. Paid subscribers only at first |
| 2025-07-25 – 08-20 | Brave discloses indirect prompt injection in Comet | The moment this class's specific risk was **publicly demonstrated** ([07](07-security.md)) |
| 2025-08 | Claude for Chrome pilot (1,000 users) | The extension axis gets serious |
| 2025-10 | Comet goes free | Price drops out of the competitive picture |
| 2025-10-21 | **ChatGPT Atlas** released (macOS only) | OpenAI enters |
| 2025-10 | Arc/Dia team acquired by Atlassian ($610M, closed October) | Repositioned from consumer browser to knowledge-worker tool |
| 2025-12 | Claude for Chrome opens to all paid plans | |
| 2026-03-18 | Comet on iOS | Four platforms |
| 2026-03 | Comet fully free, agent mode included | |
| **2026-08-09** | **ChatGPT Atlas retired** | §3 below |
| 2026-09 (now) | New entrants such as Aside keep arriving | |

## 3. Atlas's retirement changes how to read this field

**OpenAI discontinued its own browser, ChatGPT Atlas, on 2026-08-09**, less than ten months after
release. The browser-based agentic capabilities were absorbed into ChatGPT and Codex; users were
given a 30-day wind-down and told to export bookmarks by hand (bookmarks, history and open tabs did
not transfer automatically).

Two stated reasons, from different kinds of source:

| Reason | Source character |
|---|---|
| Consolidating Atlas, the ChatGPT app and Codex into **one desktop application** | secondary (CNBC, reported 2026-03-19) |
| **A browser demands ongoing security maintenance** — they did not want users left on a discontinued one | OpenAI help centre (direct fetch failed with 403; obtained via secondary) |

Why this matters, three ways:

1. **Most comparison articles are stale.** Plenty of 2026 pieces in the "Atlas vs Comet vs Dia" shape
   are still surfacing, and many assume Atlas is alive. Check the date first.
2. **Building a browser is a maintenance debt.** Not a product feature but **the standing cost of
   chasing Chromium** — a cost that became a problem even at the best-resourced company. Aside's
   changelog bumping Chromium every week or two ([02 §7](02-aside.md)) is the same cost wearing a
   different face.
3. **Security entered the reasons for retirement.** Read that together with the fact that prompt
   injection remains unsolved ([07](07-security.md)).

> ⚠️ The exact weighting of Atlas's reasons is **unverified.** Public documents give both
> consolidation and security and do not say which dominated. Both are recorded here.

## 4. What is still alive (snapshot, 2026-09)

| Product | Class | Platforms | Price | One line |
|---|---|---|---|---|
| **Aside** | A | macOS 15+, Windows | free / $20 / $200 | Bets entirely on working like a person inside sites you are logged into |
| **Comet** | A (extensions inside) | Win/mac/iOS/Android | free (Comet Plus $5) | Four platforms, free. Coupled to a search asset |
| **Dia** | A | **macOS 14+, Apple Silicon only** | free / Pro $20 | Skills (reusable routines). Emphasises local encryption |
| **Opera Neon** | A | desktop | $19.90/mo | Parallel work, project-level management |
| **Claude for Chrome** | B | Chrome only | paid Claude plans | Keep the browser you have |
| **Gemini in Chrome** | B | Chrome | Workspace / AI Pro·Ultra | Market share *is* the distribution channel |
| **Browser Use** | C | library | OSS | ~108k GitHub stars. Top of the leaderboard |

Prices and plans are a **snapshot at the time of research.** This field repriced quarterly — Comet
went from paid to free within a year. [SCOPE.md](SCOPE.md) records that tracking them is out of scope.

## 5. Where the competitive axis moved

Early on (2025) the differentiator was "summaries and a sidebar chat." By 2026 everyone has that.
What separates products now:

| Axis | The question |
|---|---|
| **Completion rate** | Does it finish a multi-step task or stop halfway — the point Aside attacks head-on with "Today's AI browsers… never complete a task" |
| **Behind the login** | Can it work inside authenticated sites? Is the surface an integration list or the browser itself? |
| **Credential handling** | Does the agent see your password, or does something fill it without showing it? ([06 §4](06-architecture-axes.md)) |
| **Trust boundary** | Is page content separated from user instruction? ([07](07-security.md)) |
| **Local-first** | Do memory and history stay on the device, or go to a server? |

> Benchmark scores are **hard to use as a competitive axis.** Most in this field are vendor
> self-reported with inconsistent grading, so direct comparison does not hold. Aside's claims are
> graded as an example in [99](99-sources.md) §3.
