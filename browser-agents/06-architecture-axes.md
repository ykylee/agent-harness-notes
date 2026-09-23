# 06. Cross-cutting analysis — four axes

> Cutting across the per-product write-ups to isolate **the design decisions themselves**, from the
> angle of "what would I have to decide first if I built one?" Evidence for each axis is in
> [02](02-aside.md), [04](04-comet-architecture.md) and [05](05-comparables.md).
>
> Crossed with the Codex study in [`SYNTHESIS.md`](../SYNTHESIS.md).

## 1. Axis one: where the control surface sits

**Decide this first; everything else hangs off it.**

| Choice | What you get | What you pay |
|---|---|---|
| **Native browser** | browser-chrome-level UX (split tabs), a full permission model, ownership of credentials | **the standing debt of chasing Chromium**, and a user migration to ask for |
| **Extension** | no migration, no maintenance debt, immediate distribution | only what extension APIs permit; cannot change browser UI |
| **Library** | complete control, headless scaling, programmatic composition | not a product a person uses |

### Evidence for this axis

- **Atlas's retirement (2026-08-09)** showed the cost of native. Security maintenance was among the
  stated reasons.
- **Aside's changelog** is the same cost in another form — several releases a week, Chromium every
  one to two weeks.
- **Comet mixed the two** — ships a native browser while implementing control as three extensions.
  **And so does Aside** ([09 §3](09-aside-browser-internals.md)).

> 📌 **That the boundary is blurry is the important finding.** "Building a native browser" does not
> mean control is implemented in native code. Using the Chromium extension layer as the control
> surface — as Comet and Aside both do — lets you ship the browser natively while keeping agent logic
> in extensions, **separating their release cadences.** Comet's extensions auto-update from the
> server; Aside runs shell `1.0.x` against extensions and CLI at `1.26.x`.

## 2. Axis two: how the agent sees the page

Four approaches are genuinely in use, and each has **its own failure mode.**

| Approach | Adopted by | Strength | Failure mode |
|---|---|---|---|
| **Raw DOM** | (effectively nobody) | no information loss | 2MB+ — the token budget collapses |
| **Accessibility tree** | Comet (`Accessibility.getFullAXTree` → YAML), Aside (injected script) | semantics already settled, token-efficient | collapses on sites with poor accessibility |
| **Screenshot** | Atlas (computer-use model) | the actual rendered appearance, visual elements | **popups and dropdowns render as separate surfaces and need compositing**; coordinate precision |
| **DOM distillation + SoM** | Browser Use | 2MB → 1.5–3k tokens, **index references remove coordinate error** | whatever distillation discarded is gone for good |

### The screenshot trap — what Atlas left on record

The Atlas engineering post recorded the problem concretely. The computer-use model takes **one
screenshot**, but UI such as dropdowns renders in **a separate window outside the main tab's
bounds.** Atlas had to **composite those popups back into the main image at the right coordinates.**

> 📌 "Capture the screen and hand it to the model" is conceptually simple, but **a browser's actual
> rendering is not a single image.** Choose this and you must solve compositing yourself. Tree-based
> approaches never meet the problem.

### Do perception and action share a namespace?

This is where it divides.

| | Perception | Action | Result |
|---|---|---|---|
| **Comet** | accessibility tree (semantics) | `ComputerBatch` pixel coordinates (geometry) | **asymmetric.** Flexible but exposed to coordinate error |
| **Browser Use** | SoM indices | `click_element(index=14)` | **symmetric.** No coordinate-error failure mode. 95%+ precision |
| **Aside** | accessibility tree plus virtual refs (`e31`) | `page.locator('e31')` | **symmetric.** Same perceptual basis as Comet, different action layer |

> 📌 **Symmetry is structurally more robust.** When what you saw and what you point at share a
> namespace, "clicked somewhere other than what I saw" cannot happen. Starting here is the safe
> choice for a custom harness.
>
> ✅ **This judgement was later supported at code level.** Aside also chose symmetry
> ([08 §3.1](08-aside-code-level.md)), and even its visual fallback `annotatedScreenshot` preserves
> the namespace with **boxes carrying ref IDs.** Comet is the only asymmetric case in this study.

## 3. Axis three: where planning runs

| Location | Adopted by | Implications |
|---|---|---|
| **Server** | Comet (backend plans and issues commands) | central control, easy updates. **User data passes through a server.** Model choice constrained |
| **Local daemon** | **Aside** (`127.0.0.1:21420`, 353MB) | confirmed structurally. Gives model sovereignty through BYO subscription/keys |
| **Cloud model** | **Opera Neon** | execution is the local browser, **planning is a cloud LLM**. The product FAQ says so |
| Via own servers | Dia | AI requests pass through its servers to partner models |
| **Caller** | Browser Use | entirely the integrator's business |

> ⚠️ **Check which side a vendor means by "local."** Opera's `llms.txt` says "All AI processes run
> locally on the device"; the product FAQ says "Neon Do runs locally… **However, it uses cloud-based
> LLMs to generate the plans**." Two first-party sources from the same company disagree — execution
> is local, planning is not. [11 §3.1](11-dia-and-neon.md)

> This axis **decides the privacy story and the model economics at once.** Aside letting users pull
> in their existing ChatGPT/Claude subscriptions over OAuth ([02 §9](02-aside.md)) pairs with keeping
> planning local — if you planned on a server there would be no reason to use the user's subscription.

> ✅ **Verified**: Aside's "local-first" has structural grounding. The 353MB daemon does the planning
> ([09 §5](09-aside-browser-internals.md)). What goes to a server is still unconfirmed — static
> analysis cannot answer that.

## 4. Axis four: how credentials are handled

The sharpest design difference in the field. Working behind a login needs credentials, and agents are
vulnerable to prompt injection ([07](07-security.md)). Two approaches:

| Approach | Adopted by | Principle |
|---|---|---|
| **URL blocking** | Comet | **blocks** access to credential pages such as `chrome://password-manager`; also `file://` |
| **Value hiding** | Aside | the browser fills the field **without giving the agent the raw password** |
| **Element hiding** | Dia | password fields and irreversible action buttons are **removed from the agent's perception** |

> 📌 **Hiding the value is the more fundamental move.** URL blocking is enumerative — it fails when a
> new path appears. Value hiding **removes the secret from the agent's observable range entirely**,
> independent of path.
>
> 📌 **Dia's element hiding reaches further still** — extending past credentials to irreversible
> action buttons. [11 §2](11-dia-and-neon.md).

### Two things to copy from Aside's design

1. **Keep permission level and credential exposure on separate axes.** Passwords stay hidden even in
   `full-access` mode. "Highest privilege" does not mean "can see everything." Access policy **and
   target URL** are both checked before autofill.
2. **Apply isolation modes consistently through credentials.** The agent cannot use the vault in an
   incognito session.

> ⚠️ Aside's AI access policy nonetheless defaults to the loosest setting, `Always allow`. The design
> is good; the default points the other way.

## 5. A secondary axis: turning repeated delegation into a unit of reuse

Three products solved the same problem differently. **That is a signal it is a shared problem.**

| Product | Name | Axis |
|---|---|---|
| Dia | **Skills** | reusable routines invoked by name |
| Opera Neon | **Cards** | prebuilt actions grounded in page context |
| Aside | **Routines** | **time** — cron (a new task) vs. heartbeat (continuing an existing chat) |

> 📌 **Update (2026-09-23)**: Neon's official name is **Cards**, not Skills, and its axis differs —
> it holds "handle **this kind of task** like this" and groups into decks. It is **methodology, not
> scheduling**, and therefore **orthogonal** to Aside's Routines. One product could have both; none
> does yet. [11 §3.4](11-dia-and-neon.md)

> 📌 Aside's cron/heartbeat split is the most precise of the three. Recurring work carries two
> different meanings — "start fresh" and "continue" — and most schedulers give only the first. An
> agent with conversational context needs the second. Aside goes further and **scans for recurring
> work to propose routines**, solving the problem that users do not discover their own reusable units.

## 6. If you were building one — decision order

1. **Decide the control surface first** (§1). Everything else hangs off it. Without the resources to
   build a browser, start with an extension — it is a debt Atlas could not carry either.
2. **Put perception and action in one namespace** (§2). SoM-style indexing structurally removes the
   coordinate-error failure mode.
3. **Do not pick screenshots as the primary perception.** If you do, build the popup compositing
   problem into the design.
4. **Shield credentials by hiding the value** (§4). URL blocking is enumerative.
5. **Keep permission level and secret exposure on separate axes.** Highest privilege must not mean
   highest exposure.
6. **Apply isolation modes consistently through credentials.**
7. **Provide a unit of reuse and suggest it automatically** (§5). Users do not find it themselves.
8. **Keep a deterministic path.** Like Aside's `repl`, you need somewhere to drop to where the model
   is weak.
9. **Expose your own tool over MCP.** You may be an execution surface for another harness rather than
   a final product.
   — ✅ Aside (`aside mcp`) and Opera Neon (**an MCP server**) reached this independently. It looks
   like a convergence point for the field. [11 §3.3](11-dia-and-neon.md)
10. **Separate page content from user instruction** — [07](07-security.md). This is not optional.
