# 05. Comparables — Atlas · Dia · Neon · extensions · libraries

> These lack the primary material available for Aside ([02](02-aside.md)) and Comet
> ([04](04-comet-architecture.md)). Where the depth is shallow it is left shallow rather than filled
> in by guesswork. Grades in [99](99-sources.md).

## 1. ChatGPT Atlas — retired, and instructive for it

| Axis | Detail |
|---|---|
| Released | **2025-10-21**, macOS only (Windows/iOS/Android were "coming soon" and never shipped) |
| Engine | Chromium / Blink |
| Retired | **2026-08-09** — under ten months |
| After | browser-based agentic capabilities absorbed into ChatGPT and Codex |
| Agent mode | paid (Plus/Pro). Gives the AI **a cursor and tints the browser UI blue** |
| Benchmark | Online-Mind2Web 71.0% (OpenAI self-reported, 2026-03) |

### What survives architecturally — OWL

Atlas is described in an engineering post as separating the application from the Chromium runtime
with **its own architecture called OWL.** Most Chromium derivatives embed the web engine directly in
the app, coupling UI tightly to the rendering engine — and that coupling makes certain capabilities
very hard.

**One concrete problem and its fix are on the record for agent mode:**

> The computer-use model that powers agent mode takes **a single screenshot of the browser** as
> input. But some UI, such as dropdown menus, renders in **a separate window outside the main tab's
> bounds.** Atlas **composites those popup windows back into the main page image at their correct
> coordinates**, so the model sees the whole context in one frame.

> 📌 **A case study in the structural trap of screenshot-based perception.** "Capture the screen and
> hand it to the model" sounds simple, but a browser's actual rendering is not one image — native
> popups, dropdowns and modals surface separately. Choose screenshots and **you must solve the
> compositing problem yourself.** Choose an accessibility tree (Comet) or DOM distillation (Browser
> Use) and the problem never arises — [06 §2](06-architecture-axes.md).

### What the retirement teaches

1. **A browser is not a product but a standing debt.** Security maintenance entered the stated reasons.
2. **Agent capability does not require owning a browser.** OpenAI discarded the browser and kept the features.
3. Even the best-resourced company found **maintaining a consumer browser did not pay.** Read Aside's
   three-person team chasing Chromium every week or two ([02 §7](02-aside.md)) in that light.

## 2. Dia — the Arc team, under Atlassian

> 📌 **Dia and Opera Neon were later deepened from primary sources — [11](11-dia-and-neon.md).**
> What follows is an overview; the injection defences, planning location and the reality of Cards
> are there.

| Axis | Detail |
|---|---|
| Developer | The Browser Company (makers of Arc); **acquired by Atlassian for $610M, closed 2025-10** |
| Platforms | **macOS 14+, Apple Silicon only.** No Windows build announced even post-acquisition |
| Pricing | free / Dia Pro $20/mo (unlimited chat plus Skills) |
| Core | chat riding alongside the page, **reading across open tabs** |
| **Skills** | reusable AI routines invoked by name |
| Claimed differentiator | local encryption, granular control over what the AI may access |

> 📌 **Skills** is structurally interesting: not a one-off prompt but a **named reusable unit** the
> user builds. Opera Neon has a comparable concept (§3), and Aside's Routines ([02 §10](02-aside.md))
> attack the same problem from the scheduling side. **"How do you turn a repeated delegation into a
> reusable unit"** is a shared problem for this field.

> Post-acquisition positioning shifted to "the browser for knowledge workers" — out of the consumer
> browser race and into enterprise workflow, the same direction as Atlas's retirement.

## 3. Opera Neon

| Axis | Detail |
|---|---|
| Engine | Chromium |
| Timing | **limited release 2025-05** — among the first consumer browsers to ship agentic features |
| Pricing | $19.90/mo |
| Features | Neon Do (action) · Tasks (ongoing work) · **Cards** (reusable prompts). ⚠️ What secondary sources called "Skills" is not the official name — [11 §3.4](11-dia-and-neon.md) |

> Putting parallel work up front distinguishes it: most products concentrate on "one task to
> completion," Neon sells running several at once.

## 4. Extensions — Claude for Chrome and Gemini in Chrome

**They do not build a browser.** They attach to the Chrome the user already has.

### Claude for Chrome

| Axis | Detail |
|---|---|
| Form | official Chrome extension |
| Character | a sidebar that sees the page **and** an agent — clicking, typing, filling forms, working across tabs |
| History | 1,000-user pilot 2025-08 → all paid plans (Pro/Max/Team/Enterprise) 2025-12 |
| Constraint | **Google Chrome only** |

### Gemini in Chrome

| Axis | Detail |
|---|---|
| Form | built into Chrome |
| Distribution | generally available to Workspace users; **auto browse** for US AI Pro/Ultra |
| Capability | form filling (for example from information in a PDF) |

> 📌 **Structural advantage**: no user migration, and no browser maintenance debt (the Chrome team
> carries it). After Atlas's retirement this approach looks comparatively favourable.
>
> **Structural limit**: only what the extension APIs permit. You cannot change the browser itself, so
> **browser-chrome-level UX** like Aside's split tabs is impossible. And Gemini in Chrome enjoys an
> asymmetric advantage no competitor can copy — **Chrome's market share is the distribution channel.**

## 5. Browser Use — the library axis

**Not a product a person uses. A library in which code drives the browser.**

| Axis | Detail |
|---|---|
| Form | open-source Python library |
| Scale | **~108,000 GitHub stars** (2026-08) |
| Standing | Online-Mind2Web leaderboard **first at 97.0%** (Browser Use Cloud, custom agentic judge, 2026-03); Odysseys 87.4% |
| Models | many providers via LiteLLM |

### The agent loop (O-P-A-V)

`Agent` is the unit of work. Hand it a task, an LLM and a `BrowserSession`, and each step:

| Step | Action |
|---|---|
| **Observe** | prune the DOM and capture a SoM-annotated screenshot |
| **Reason** | evaluate the user goal against the current interactive state |
| **Plan** | select an atomic action (Click / Type / Scroll / Tab) |
| **Act** | dispatch input through Playwright CDP |
| **Verify** | wait for network idle and DOM mutation, then verify state |

On failure, a self-healing retry or fallback.

### DOM tree distillation

| Item | Value |
|---|---|
| Removed | scripts, styles, SVGs, hidden elements |
| Extracted | interactive nodes (`button`, `input`, `a`, `select`), bounding boxes, viewport visibility |
| Collapsed | non-semantic wrapper `<div>` chains; only nodes with meaningful text or interactive accessibility attributes survive |
| **Result** | **2MB+ raw → 1,500–3,000 tokens** (5–15KB) |

### Set-of-Mark visual grounding

The model is never asked to predict pixel coordinates.

1. JavaScript gets the bounding box of every interactive candidate
2. Brightly coloured boxes carrying **numeric badges (`[1]`, `[2]`, `[15]`)** are painted
3. An annotated screenshot is captured
4. The model emits **high-level actions referencing indices**, not coordinates — `click_element(index=14)`

Action execution precision is reported **above 95%**.

```
click_element(index=14)
input_text(index=3, text="admin@company.com")
scroll_down(amount=500)
switch_tab(tab_id=1)
```

### Stagnation detection

If **three consecutive clicks** on an element leave the DOM topology unchanged, a watchdog forces a
clean page reload and injects contextual feedback steering the model toward alternative strategies
such as modal detection or scrolling.

### Token budget

**800–2,500 tokens per step** on average. Screenshots compress to ~1280px wide, keeping per-image
consumption to a few hundred tokens.

> 📌 **This axis is the most transparent.** Being open source, its perception, action and recovery
> strategies are all readable — you can learn here what the consumer browsers do not publish. The
> **SoM index approach** in particular looks structurally more robust than Comet's pixel-coordinate
> `ComputerBatch` ([04 §6](04-comet-architecture.md)) or Atlas's screenshot compositing (§1): the
> failure mode of coordinate error simply does not exist.

## 6. In one table

| | Aside | Comet | Atlas | Dia | Neon | Claude/Chrome | Browser Use |
|---|---|---|---|---|---|---|---|
| Class | A | A (extensions) | A **retired** | A | A | B | C |
| Platforms | mac, Win | 4 | macOS | **mac/AS only** | desktop | Chrome | library |
| Planning | **local daemon** | **server** | — | server | **cloud LLM** | server | **caller** |
| Perception | **a11y tree + refs** | a11y tree | screenshot compositing | — | — | — | **DOM distill + SoM** |
| Unit of reuse | Routines | — | — | **Skills** | **Cards** | — | code |
| Developer surface | **CLI/MCP/REPL** | — | — | — | **MCP** | — | **all of it** |
| BYO model | **subscription/key** | Max only | — | — | — | — | **all of it** |
| Internals known | **binary analysed** | **reverse-engineered** | partial | low | low | low | **open source** |
