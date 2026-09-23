---
type: concept
status: active
last_ingested_from: browser-agents/06-architecture-axes.md + browser-agents/08-aside-code-level.md + browser-agents/04-comet-architecture.md + browser-agents/05-comparables.md + SYNTHESIS.md §6 + SYNTHESIS.md §6.5
related_pages: [concepts/harness, concepts/indirect-prompt-injection, concepts/control-plane-execution-plane, concepts/credential-shielding, concepts/os-sandbox-policy, concepts/capability-distribution, concepts/thread-turn-item, concepts/primary-source-verification]
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
| 6 | ⚠️ **Tested by building it** | symmetry held as a principle and **failed three times as an identifier** — §7 |

## §2 Four approaches and their failure modes  {#s2-four-ways}

| Approach | Adopted by | Strength | Failure mode |
|---|---|---|---|
| **Raw DOM** | (effectively nobody) | no information loss | **2MB+** — the token budget collapses |
| **Accessibility tree** | Comet (`Accessibility.getFullAXTree` → YAML), Aside (injected script) | semantics already settled, token-efficient | collapses on sites with poor accessibility |
| **Screenshot** | Atlas (computer-use model) | the actual rendered appearance | **popups and dropdowns render as separate surfaces** and need compositing; coordinate precision |
| **DOM distillation + SoM** | Browser Use | 2MB → **1,500–3,000 tokens** | whatever distillation discarded is gone |

> ⚠️ **Do not carry the 1,500–3,000 figure over to an accessibility tree.** It is Browser Use's
> number for its own distillation. Measured on a pruned accessibility tree, a Wikipedia article came
> to **~10,948 tokens — 3.6× that** — and no pruning rule removes an article's 515 links without
> removing the article. §7.

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
>
> ⚠️ **"Cannot exist" is conditional on the ref, not on the design.** Building this produced the
> misfire three separate times, each from an axis the identifier did not carry. §7.

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
>
> ⚠️ **A diff is only as quiet as the page.** Measured: 0 lines on a re-snapshot of a settled page,
> but **139 lines after 1.5s on Wikipedia with no action taken** — the page's own scripts. A diff
> that attributes the page's self-mutation to the agent is worse than expensive, it is misleading.
> Waiting for the page to settle before both snapshots brought it back to 0. §7.

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

## §7 Implementation feedback  {#s7-implementation}

Ingested from [`SYNTHESIS.md` §6](../../../SYNTHESIS.md) — the one place in this repository whose
claims were tested by building them rather than by reading someone else's artifact. Summarised here
because the claims it refutes are stated on this page.

| This page says | Measured |
|---|---|
| 1,500–3,000 tokens for a page (§2) | ~10,948 for a Wikipedia article on a pruned accessibility tree — **3.6×** |
| `diff` keeps cost sublinear (§3.1) | True on a settled page; **139 lines of delta for doing nothing** on a self-mutating one |
| Symmetry makes the misfire impossible (§3) | True of the principle; **false three times** of the implementation |
| Cost ladder step 3, "wait briefly" (§4) | A guess. Replaced by polling a cheap page fingerprint until it stops changing: **507ms observed** where a safe fixed guess cost 1,200ms |
| Coverage includes child-iframe contents (§3.1) | Claimed in a design document *and* a source comment while the code walked only the main frame. On a page with a payment and a consent iframe, **1 of 5 interactive elements was visible** |

### §7.1 The identifier, not the design  {#s7-1-identifier}

| Axis missing from the ref | Consequence |
|---|---|
| snapshot generation | a bare `e54` from an earlier snapshot resolved to a different element |
| frame | the same DOM path is a different element in a different document |
| host process life | a killed and restarted process reissued generation 1; a held ref resolved silently to `"Save draft"` where it had named `"Beta report"` |

> 📌 **A symmetric namespace prevents the misfire only while the name carries every axis that
> distinguishes one thing from another.** Each axis was invisible until something crossed it. This
> is not browser-specific — it applies to any harness whose identifiers outlive a process, which
> includes [[concepts/thread-turn-item]]-style `conversationId` / `itemId` pairs.

### §7.2 One thing it settled about distribution  {#s7-2-distribution}

Cross-origin iframe content is readable through per-frame CDP evaluation — measured `walked=2,
unreachable=0`, with four interactive elements lifted out of the embedded origin. **That removes the
perception argument for shipping a browser fork**; see [[concepts/capability-distribution]].

### §7.3 The cost ladder is also an exposure ladder  {#s7-3-ladder-exposure}

Found by a probe bug, which is the only reason it was noticed: a measurement of injected instructions
scored a clean sweep for the defences, because the snapshot was taken in `interactive` mode and **the
injected paragraph was never in the prompt.** That rung drops page prose.

> 📌 Page prose is where injections live, so **`interactive` is a genuine injection mitigation** —
> and it cannot do the task in the canonical attack demonstration, which is *"summarise this page."*
> The reading rung and the injection exposure are **the same dial**: the cheaper the rung, the less
> attack surface, and the task decides how far up you are forced to go.
>
> §4's ladder was built as a cost argument. It is also a security argument, and the two point the
> same way for once — which is worth knowing, because they usually do not.

See [[concepts/indirect-prompt-injection]] §10 for what the model did once the text reached it.

### §7.4 Still untested  {#s7-4-untested}

Step 4 of the cost ladder (**annotated screenshot**) and §5's **stagnation watchdog** were both
designed and neither was built. They remain read-from-a-document claims.
