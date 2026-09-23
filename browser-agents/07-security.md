# 07. Security — indirect prompt injection

> Sources: Brave's published research on Comet (disclosed 2025-08-20), Wikipedia's record of
> CometJacking, and 2026 research and reporting. Only risks **specific to this class** are covered;
> general browser security is out of scope.

## 1. Why this is the central problem here

A browser-type agent holds two things at once.

1. **Access to logged-in sessions** — email, banking, internal tools
2. **The ability to read web page content as context** — and web pages **can be written by an
   attacker**

Where those two meet, a new attack surface appears. The web's existing defence, **the same-origin
policy, stops helping** — the agent is an entity that crosses origins with the user's own authority.

## 2. The attack chain — Brave's demonstration against Comet

| Step | Detail |
|---|---|
| **1. Plant** | The attacker hides instructions in the page — "white text on white backgrounds, HTML comments, or other invisible elements." Or injects into **user-generated content** such as a Reddit comment |
| **2. Trigger** | The user visits the page and invokes the AI — for example, **"Summarize this page."** |
| **3. Inject** | The system processes page content **without distinguishing user instruction from untrusted page content** |
| **4. Execute** | The AI treats the injected commands as a legitimate user request and performs browser actions |
| **5. Exfiltrate** | In the proof of concept: obtain the user's email address, **pull an OTP out of Gmail**, send both to the attacker's server → account takeover |

> All the user did was **press "summarize."** No malicious link was clicked, no credential typed.
> That is the character of this attack.

## 3. The structural cause

Brave's diagnosis points at architecture, not an implementation bug.

> Comet **"feeds a part of the webpage directly to its LLM without distinguishing between the user's
> instructions and untrusted content from the webpage."**

Once the input stream is merged, the model has no means of telling legitimate intent from an inserted
payload. That connects directly to the perception axis in
[06 §2](06-architecture-axes.md) — deciding **what goes into the context** means also deciding **its
trust grade.**

## 4. Brave's four mitigation categories

| # | Category | Detail |
|---|---|---|
| 1 | **Input separation** | "The browser should clearly separate the user's instructions from the website's contents when sending them as context to the backend. **The contents of the page should always be treated as untrusted.**" |
| 2 | **Output validation** | Model output should be "independently checked for alignment against the user's requests" |
| 3 | **Security checkpoints** | "Security and privacy sensitive actions should require user interaction" |
| 4 | **Mode isolation** | "Agentic browsing is an inherently powerful-but-risky mode" — keep it clearly separated from ordinary browsing and **prevent accidental activation** |

## 5. Disclosure timeline — it was not fixed in one pass

| Date | Event |
|---|---|
| 2025-07-25 | Discovered and reported |
| 2025-07-27 | Perplexity acknowledges, ships an initial fix |
| 2025-07-28 | **Retesting shows the fix incomplete** |
| 2025-08-11 | Seven-day disclosure notice |
| 2025-08-13 | Patch appears complete |
| 2025-08-20 | Published |
| after | **A later note records Perplexity's fix as still incomplete** |

> 📌 The timeline is itself part of the conclusion. **Two rounds of fixes were incomplete.** That is
> the evidence this is not a single-point bug.

## 6. As of 2026 — unsolved

| Fact | Grade |
|---|---|
| Researchers confirmed in 2026 that **prompt injection cannot be fully patched** in ChatGPT Atlas, Perplexity Comet or Dia | secondary |
| 2026-06, University of Washington: **four of seven** popular agentic browsers let a malicious page bypass the same-origin policy, with a **working data-theft PoC against Atlas** | secondary |
| OpenAI's own words (2025-12): prompt injection is **"unlikely to ever be fully 'solved'"** | primary quote, via secondary |
| **Security maintenance appears among the reasons for retiring Atlas** | secondary |

> ⚠️ These are **secondary sources.** The original papers and OpenAI's own text were not read
> directly (the OpenAI help centre returns 403). Several sources agree on the direction, but the
> individual figures and wording are not primary-confirmed.

## 7. Other security incidents

| Incident | Target | Detail |
|---|---|---|
| **CometJacking** | Comet | Sensitive personal data exfiltration. Perplexity **initially disputed the impact**, then independently found and patched it |
| **ChatGPT Tainted Memories** (LayerX, 2025-10) | Atlas | Memory poisoning via CSRF; the memory feature compromised through social engineering. **OpenAI disputed reproducibility** |

> Both share a trait: **the vendor initially denied it.** When reading security claims in this field,
> do not take the vendor's reaction as the final verdict.

## 8. Where each product stands

| Product | Confirmed response | Grade |
|---|---|---|
| **Aside** | Human approval for sensitive actions (payments, posts, messages), `Ask`/`Deny` rules, `Guard` as the default mode, **credential value hiding**, vault disabled in incognito | documentation, plus [10 §1.5](10-aside-enforcement-and-native.md) for the approval UI |
| **Comet** | **URL-level blocking** via `isInternalPage` / `isUrlBlocked`, administrator blacklists | reverse-engineered |
| **Dia** | ✅ **Documented concretely** — will not follow LLM-generated URLs, does not pass URLs to the LLM verbatim, removes password fields and irreversible buttons from the agent's perception, no tab access initially, no autonomous navigation, approval before writing to third-party sites. **It also states what remains** | primary documentation ([11 §2](11-dia-and-neon.md)) |
| **Opera Neon** | Credentials and payment details are not sent to Opera's servers. What the agent can see is unconfirmed | primary documentation |

> ⚠️ **Correction (2026-09-23)**: this section originally read "no product in scope documents having
> implemented input separation (#1)." **That was partly wrong.** Dia's defences were later confirmed
> — refusing LLM-generated URLs, **not passing URLs verbatim**, and making password fields and
> irreversible buttons "**invisible to the agentic system**." It is not identical to Brave's #1 (it
> does not structurally partition user instruction from page content) but it operates **at the same
> layer, controlling what enters perception.** Detail: [11 §2](11-dia-and-neon.md).
>
> For the remaining products the original observation stands — most stop at #3 (checkpoints) and #4
> (mode isolation), and the most fundamental defence is the least visible.

## 9. Practical summary for an adoption decision

- **Using this class means accepting that one "summarize this" can lead to account takeover.** The
  risk scales directly with which logged-in sessions that browser holds.
- **The substance of mitigation is reducing privilege** — not signing sensitive accounts into the
  agent browser at all is the surest measure. Aside's incognito task mode fits this use.
- **Do not turn off the approval gate.** Brave's #3 is one of the few defences actually working today.
- For enterprise adoption, check whether there is an axis for **domain blacklists via managed policy**
  (Comet's managed storage).
- A vendor's "we are local, so we are safe" **is a separate matter from prompt injection.** Local
  execution reduces data transmission; it does not stop the agent being fooled.

> ⚠️ And the surface keeps widening. Aside's `Computer Use` reaches the system-wide accessibility
> tree, an event tap, screen capture and Contacts ([10 §2](10-aside-enforcement-and-native.md)) — a
> fooled agent's range there is **the whole desktop, not a browser tab.**
