---
type: concept
status: active
last_ingested_from: browser-agents/06-architecture-axes.md + browser-agents/08-aside-code-level.md + browser-agents/04-comet-architecture.md + browser-agents/05-comparables.md
related_pages: [concepts/harness, concepts/indirect-prompt-injection, concepts/control-plane-execution-plane, concepts/credential-shielding, concepts/os-sandbox-policy]
created: 2026-09-23
updated: 2026-09-23
---

# Perception Model — how an agent sees a screen

- Purpose: what representation an agent reads a web page (or a screen) through, and what failure mode each choice produces.
- Scope: four approaches, symmetry between perception and action, the cost ladder, recovery
- Character: **a surface-specific axis.** A shell-based harness (Codex) does not have this problem
- Updated: 2026-09-23

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | Why it is hard | a raw DOM is 2MB+ — **the token budget breaks first** |
| 2 | Approaches in use | raw DOM · accessibility tree · screenshot · DOM distillation + SoM |
| 3 | **The decisive split** | do perception and action share **one namespace** |
| 4 | If symmetric | "clicked somewhere other than what I saw" becomes **structurally impossible** |
| 5 | Asymmetric cases in scope | **Comet alone** |

## §2 Four approaches and their failure modes  {#s2-four-ways}

| Approach | Adopted by | Strength | Failure mode |
|---|---|---|---|
| **Raw DOM** | (effectively nobody) | no information loss | **2MB+** — the token budget collapses |
| **Accessibility tree** | Comet (`Accessibility.getFullAXTree` → YAML), Aside (injected script) | semantics already settled, token-efficient | collapses on sites with poor accessibility |
| **Screenshot** | Atlas (computer-use model) | the actual rendered appearance | **popups and dropdowns render as separate surfaces** and need compositing; coordinate precision |
| **DOM distillation + SoM** | Browser Use | 2MB → **1,500–3,000 tokens** | whatever distillation discarded is gone |

### §2.1 The screenshot trap — what Atlas left on record  {#s2-1-screenshot-trap}

> The computer-use model takes **one screenshot** as input, but UI such as dropdowns renders in **a
> separate window outside the main tab's bounds.** Atlas had to **composite those popups back into
> the main image at their correct coordinates.**

> 📌 "Capture the screen and give it to the model" is conceptually simple, but **a browser's actual
> rendering is not one image.** Choose this and you must solve compositing yourself. Tree-based
> approaches never meet the problem.

## §3 The core axis — the namespace of perception and action  {#s3-naming}

| Product | Perception | Action | Symmetric |
|---|---|---|---|
| **Aside** | accessibility tree plus **virtual ref IDs** (`e31`, `f1e1`) | `page.locator('e31')` | ✅ |
| **Browser Use** | SoM numbered badges (`[14]`) | `click_element(index=14)` | ✅ |
| **Comet** | accessibility tree (semantics) | **`ComputerBatch` pixel coordinates** (geometry) | ❌ |

> 📌 **Symmetry is structurally more robust.** When what you saw and what you point at share a
> namespace, the failure mode "clicked somewhere other than what I saw" **cannot exist.** Browser Use
> reports action precision above 95% on this basis.
>
> For a custom harness, starting here is the safe choice.

### §3.1 Aside's ref convention (confirmed in code)  {#s3-1-aside-refs}

```ts
snapshot(page, { interactive?, showHidden?, ref?, selector? })
  : Promise<{ tree: string; diff: string }>
```

| Rule | Detail |
|---|---|
| Representation | "compact accessibility tree with unique ref IDs such as `e12` or `f1e1`" |
| Coverage | title, URL, **child-iframe contents and elements outside the scroll viewport** |
| Nature of a ref | "**virtual locator IDs, not actual DOM properties**" — never mix into CSS selectors |
| Invalidation | a new snapshot **invalidates every earlier ref** |
| **diff** | print `tree` first, then **only `diff` after an action** |

> 📌 **`diff` is the key to token efficiency.** Re-reading the whole tree after each action burns
> thousands of tokens per step. Giving only the delta keeps cost from growing linearly with
> conversation length. Aside is the only product in scope that offers diffs as a first-class result.

## §4 The cost ladder — cheapest first  {#s4-escalation}

Aside's **reading escalation**, stated explicitly in code:

| Order | Means |
|---|---|
| 1 | `snapshot(page, { interactive: true })` — interactive elements only |
| 2 | `snapshot(page)` — everything |
| 3 | wait briefly and re-snapshot (only while the page is still changing) |
| 4 | **`annotatedScreenshot(page)`** — **bounding boxes carrying ref IDs** |
| 5 | `page.screenshot()` — raw visual state |

> 📌 Step 4 is good design. Even dropping to visual confirmation **preserves the namespace.** Same
> idea as Browser Use's SoM, but Aside placed it **as a fallback rather than the default path.**

## §5 Recovery strategy  {#s5-recovery}

How to escape when perception was wrong. What Browser Use publishes:

> If **three consecutive clicks** on an element leave the DOM topology unchanged, a watchdog forces a
> clean page reload and injects **contextual feedback steering the model toward alternative
> strategies** such as modal detection or scrolling.

> 📌 **Stagnation detection is part of perception design.** An agent cannot tell on its own that it
> has changed nothing — an external watchdog has to say so.

## §6 When it extends to the OS  {#s6-os}

Aside's `Computer Use` carries the same philosophy onto the desktop — **`AXTreeSerializer`**
serialises the whole screen's accessibility tree. Reading structure before screenshot coordinates is
consistent. Detail in [[concepts/os-sandbox-policy]] §8.6.

## §7 Read next  {#s7-next}

- [[concepts/indirect-prompt-injection]] — what you put into perception is the attack surface
- [[concepts/credential-shielding]] — the design of what you take **out**
- [[concepts/harness]] §7.6 — the split between surface-specific and surface-independent axes
- Original: [`browser-agents/06-architecture-axes.md`](../../../browser-agents/06-architecture-axes.md) §2
