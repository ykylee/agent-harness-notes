---
type: concept
status: active
last_ingested_from: browser-agents/07-security.md + browser-agents/11-dia-and-neon.md
related_pages: [concepts/perception-model, concepts/credential-shielding, concepts/approval-gate, concepts/os-sandbox-policy]
created: 2026-09-23
updated: 2026-09-23
---

# Indirect Prompt Injection — the structural risk of this class

- Purpose: the attack surface created when an agent reads untrusted content, and which mitigations are actually implemented.
- Scope: the attack chain, the structural cause, the four mitigation categories and where each product stands, the unsolved status
- Character: **a surface-specific axis** — though a shell harness reading files or the web develops the same problem
- Updated: 2026-09-23

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | Preconditions | **access to logged-in sessions** plus **reading untrusted content as context** |
| 2 | What stops helping | **the same-origin policy** — the agent crosses origins with the user's own authority |
| 3 | What the user did | **pressed "summarize this page"** |
| 4 | As of 2026 | **unsolved.** OpenAI's own words: "unlikely to ever be fully 'solved'" |
| 5 | The substance of mitigation | **reducing privilege** — not signing sensitive accounts into the agent browser |

## §2 The attack chain (Brave's demonstration against Comet)  {#s2-chain}

| Step | Detail |
|---|---|
| 1. Plant | hide instructions in the page — "white text on white backgrounds, HTML comments, or other invisible elements." Or inject into **user-generated content** such as a Reddit comment |
| 2. Trigger | the user invokes the AI on that page — **"summarize"** |
| 3. Inject | the system processes it **without distinguishing user instruction from untrusted page content** |
| 4. Execute | the AI treats the injected commands as a legitimate request |
| 5. Exfiltrate | demonstrated: obtain the email address → **extract an OTP from Gmail** → send both to the attacker → account takeover |

## §3 The structural cause  {#s3-cause}

> Comet **"feeds a part of the webpage directly to its LLM without distinguishing between the user's
> instructions and untrusted content from the webpage."**

Once the input stream merges, the model has no means of telling legitimate intent from an inserted
payload.

> 📌 **This connects directly to [[concepts/perception-model]].** Deciding what goes into the context
> means also deciding **its trust grade.** Perception design and security design are one decision.

## §4 Brave's four mitigation categories, and reality  {#s4-mitigations}

| # | Category | Gist | Products that document it |
|---|---|---|---|
| 1 | **Input separation** | "page content should **always be treated as untrusted**" | **Dia** (partially — §5) |
| 2 | Output validation | **independently check** model output against the user's request | none found in scope |
| 3 | Security checkpoints | sensitive actions **require user interaction** | Aside, Dia ([[concepts/approval-gate]]) |
| 4 | Mode isolation | agentic browsing is "inherently powerful-but-risky" — **prevent accidental activation** | Aside (incognito task mode), Dia |

> 📌 **The most fundamental — #1 — is the least visible.** Several products cover #3 and #4, but
> partitioning trust grades at the input layer is rare.

## §5 Dia — defence at the perception layer  {#s5-dia}

**The only product in scope that documents concrete defences.**

| Defence | Original wording |
|---|---|
| No following LLM-generated URLs | "Dia won't automatically open or follow LLM-generated URLs" |
| **No verbatim URL passing** | "Dia won't pass URLs to the LLM verbatim" |
| **Sensitive elements removed from perception** | password fields and irreversible action buttons are "**invisible to the agentic system**" |
| Minimal initial privilege | chat "starts with **no access to other tabs** or ability to take write actions" |
| No autonomous navigation | the agent cannot move to another site on its own |

And it **states its own limits** — tone shifts and nudging content toward misinformation remain
possible.

> 📌 **Listing defences and also saying what remains** is the most trustworthy part of the document.
> It does not claim the problem is solved.
>
> 📌 "Does not pass URLs verbatim" and "erases dangerous elements from perception" are not identical
> to Brave's #1 — they do not structurally partition user instruction from page content. But they
> operate **at the same layer, controlling what enters perception.**

## §6 Unsolved as of 2026  {#s6-unsolved}

| Fact | Grade |
|---|---|
| Researchers confirmed in 2026 that **prompt injection cannot be fully patched** in Atlas, Comet or Dia | 📰 secondary |
| 2026-06, University of Washington: **four of seven** popular agentic browsers allowed SOP bypass; a working data-theft PoC against Atlas | 📰 secondary |
| OpenAI (2025-12): prompt injection is **"unlikely to ever be fully 'solved'"** | primary quote, via secondary |
| **Security maintenance is among the reasons for retiring Atlas** | 📰 secondary |

### §6.1 Do not treat a vendor's reaction as the verdict  {#s6-1-vendor}

| Incident | The vendor's first reaction |
|---|---|
| CometJacking (Comet) | **disputed the security impact** → later independently found and patched it |
| Tainted Memories (Atlas) | **disputed reproducibility** |
| Brave's Comet injection | two rounds of fixes, **both incomplete** |

## §7 As the surface widens  {#s7-surface}

The size of this risk is **directly proportional to what the agent can reach.**

> ⚠️ Aside's `Computer Use` reaches the system-wide accessibility tree, an event tap, screen capture
> and Contacts ([[concepts/os-sandbox-policy]] §8.6). A fooled agent's range there is **the whole
> desktop, not a browser tab.**
>
> 📌 **A vendor's "we are local, so we are safe" is a separate matter.** Local execution reduces data
> transmission; it does not stop the agent being fooled.

## §8 Practical summary  {#s8-practical}

- **You are accepting that one "summarize this" can lead to account takeover.**
- Risk scales with **which logged-in sessions that browser holds.**
- **The substance of mitigation is reducing privilege** — not signing sensitive accounts in at all is
  the surest measure
- **Do not turn off the approval gate.** It is one of the few defences actually working
- For enterprise, check for **domain blacklists via managed policy** (Comet's managed storage)

## §9 Read next  {#s9-next}

- [[concepts/perception-model]] — what enters the context is the attack surface
- [[concepts/credential-shielding]] — the design of taking things out
- [[concepts/approval-gate]] — the defence that currently works
- Original: [`browser-agents/07-security.md`](../../../browser-agents/07-security.md)
