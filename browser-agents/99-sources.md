# 99. Sources and verification record

> Applies this repository's [method of knowing](../ai-workflow/wiki/concepts/primary-source-verification.md)
> unchanged: **committed artifacts over prose**, no secondary source settled before cross-checking,
> inference labelled as inference, refutations kept rather than deleted. Researched 2026-09-22/23.

## 1. Grade vocabulary

| Grade | Meaning |
|---|---|
| ✅ **confirmed** | read directly from a primary source (product documentation originals, source, binaries) |
| 🔧 **observed implementation** | revealed by reverse engineering. Not a vendor-guaranteed specification |
| 📣 **self-reported** | a figure or claim published by the vendor itself. No independent verification |
| 📰 **secondary** | press or blog. Not yet cross-checked against a primary source |
| ⚠️ **unverified** | attempted but not reached |
| ❌ **refuted** | confirmed wrong |

## 2. Primary sources

### Aside — the whole product documentation as raw Markdown

**`docs.aside.com` publishes `/llms.txt` as a full index, and appending `.md` to any page returns the
original Markdown.** That is primary text, not a summary of a rendered page.

> 📌 The same technique this repository's existing study found in OpenAI's documentation
> ([`docs/99-sources.md`](../docs/99-sources.md)). Try `.md` and `/llms.txt` on a documentation site
> first.
>
> **Record (2026-09-23)**: Aside ✅ (16 documents) · Opera ✅ (`www.opera.com/llms.txt`) ·
> **Dia ❌** (every path returns the same SPA shell). **Not universal — it depends on how the
> documentation site renders.** On failure, fall back to the rendered page —
> [11 §1](11-dia-and-neon.md).

| Document read | What it gave |
|---|---|
| `/llms.txt` | the full 18-item documentation index |
| `help/get-started.md` | system requirements, import, onboarding |
| `help/security.md` | **three permission zones, Allow/Ask/Deny, three session modes, credential hiding** |
| `help/tasks.md` | task modes, permissions, Queue/Steer, file results |
| `help/password-manager.md` | three vault policies, what biometric unlock means |
| `help/passwords.md` | autofill settings, nine import sources, the AI access default |
| `help/memory.md` | inputs, three retention settings, three settings sections |
| `help/browser-basics.md` | **all keyboard shortcuts, split tabs, lasso, Ask AI** |
| `help/side-panel.md` | the page-attachment model, per-tab drafts |
| `help/ultrabrowse.md` | its place in the model picker, use cases |
| `help/automation.md` | **cron / heartbeat routines, suggestions, limits** |
| `help/ai.md` | three provider routes, OAuth subscriptions, seven API-key providers |
| `help/privacy.md` | local data deletion items, analytics sharing on by default |
| `help/subscription.md` | plan composition |
| `changelog/native.md` | **versions, platforms, release cadence, Chromium chasing** |
| `aside.com/pricing` | four price tiers |

### Other primary and near-primary sources

| Source | Character | Used in |
|---|---|---|
| Zenity Labs, "Perplexity Comet: A Reversing Story" | 🔧 reverse engineering | all of [04](04-comet-architecture.md) |
| Brave, "Agentic Browser Security: Indirect Prompt Injection in Perplexity Comet" | ✅ original security research | [07](07-security.md) |
| `leaderboard.steel.dev` Online-Mind2Web | ✅ third-party leaderboard | §3 |
| `github.com/OSU-NLP-Group/Online-Mind2Web` | ✅ canonical benchmark | §3 |
| `www.diabrowser.com/security` | ✅ Dia security documentation | [11 §2](11-dia-and-neon.md) |
| `www.opera.com/llms.txt` | ✅ Opera product index | [11 §3](11-dia-and-neon.md) |
| `operaneon.com/faq` (Next.js payload) | ✅ Neon FAQ answers | [11 §3](11-dia-and-neon.md) |
| Wikipedia — Comet, ChatGPT Atlas | 📰 (dates are sourced) | [01](01-landscape.md), [04](04-comet-architecture.md) |

## 3. Benchmark claims — adjudicated

**Aside claims first place on three benchmarks.** Verification:

| Claim | Verdict | Basis |
|---|---|---|
| Online-Mind2Web **99.0%** (297/300), Browser Use 97.7% | 📣 **self-reported** | The figures sit in **Aside's own GitHub repository**, graded by **Aside's own setup.** Not an audited leaderboard |
| **Aside is absent from the third-party leaderboard** | ✅ confirmed | There is **no Aside entry** in `leaderboard.steel.dev`'s Online-Mind2Web listing. First place is Browser Use Cloud at 97.0% (custom agentic judge, 2026-03) |
| First on BU Bench V1 | 📣 self-reported | BU Bench V1 = 100 tasks, 20 each from WebBenchREAD, Online-Mind2Web 2, InteractionTests, GAIA and BrowseComp |
| First on Odyssey (against OpenAI, Anthropic and others) | 📣 **self-reported, and contested** | Browser Use publishes **its own claim of leading Odysseys at 87.4%.** Both claim first place on the same benchmark |

> ⚠️ **Do not use this field's benchmark numbers to compare products.** Grading methods vary — the
> Steel leaderboard itself warns that "judge methodology varies" and says not to compare without
> examining it. The canonical Online-Mind2Web produces different scores under WebJudge(o4-mini),
> WebJudge(GPT-4o) and WebVoyager.
>
> And the benchmark **exists in the first place** because earlier web-agent benchmarks "dramatically
> overestimate agent performance" under realistic conditions.

### Benchmark specification (canonical)

| Item | Value |
|---|---|
| Online-Mind2Web | **300 tasks** across 136 live websites |
| Difficulty split | Easy 1–5 steps (83) / Medium 6–10 (143) / Hard 11+ (74) |
| Grading | WebJudge automatic (key-point identification → key-screenshot selection → outcome judgment) or human. WebJudge(o4-mini) agrees with human judgment **85.7%** of the time |
| v2 schema | introduced 2026-05-23 to ease human evaluation |

## 4. Aside — unverified and inconsistent items

| Item | Status |
|---|---|
| Hardware-backed E2E encryption | ✅ **Resolved (2026-09-23)** — the Vault extension ships **libsodium** and its real call sites use `crypto_pwhash` (ARGON2ID13), `crypto_aead_xchacha20poly1305_ietf_*` and `crypto_box_seal`. [09 §7](09-aside-browser-internals.md) |
| **Secure Enclave** | ✅ **Resolved** — `kSecAttrTokenIDSecureEnclave`, `CanCreateSecureEnclaveKeyPairBlocking`. [10 §3.1](10-aside-enforcement-and-native.md) |
| **Post-quantum cryptography** | ✅ **Resolved** — **ML-KEM-768** (`crypto_kem_mlkem768_*`) in both the Vault application code and the daemon. Separated from Chromium TLS inheritance by file location. [10 §3.2](10-aside-enforcement-and-native.md) |
| **Audit logging** | ✅ **Resolved** — `appendAuditEvent`, `getPasswordAuditLogsDir`. [10 §3.3](10-aside-enforcement-and-native.md) |
| Memory stored as **"plain markdown"** and editable | ✅ **Resolved (2026-09-23)** — the CLI bundle states "distills user's context into **plain-Markdown files**" and ships `aside memory show MEMORY.md` and `aside memory path`. Direct editing is **forbidden**, though. [08 §4](08-aside-code-level.md) |
| "local-first" — what goes to a server | ✅ **Structurally grounded** — planning runs in the local daemon, which is what makes BYO model keys work. What is transmitted remains beyond static analysis |
| **Max credit multiplier** | ❌ **Internal inconsistency** — the help documentation says "30x," the pricing page says "40x." Which is current cannot be determined |
| **Platform requirements** | ❌ **Inconsistent, and incomplete** — `get-started.md` gives only macOS 15+ while the changelog records official Windows support. And **the CLI supports Linux x64/arm64 as a first-class target**, which no document mentions (measured from the install script). [08 §2](08-aside-code-level.md) |
| What one credit is | ⚠️ **Defined in no document** |
| Perception and action | ✅ **Resolved (2026-09-23)** — accessibility tree plus virtual ref IDs, returning `{tree, diff}`, with ref-based Playwright locators. [08 §3](08-aside-code-level.md) |
| Transport | ✅ **Resolved** — the CLI attaches to a local daemon (`127.0.0.1:21420`, canary `21421`); a 353MB Node SEA daemon does the planning. [09 §5](09-aside-browser-internals.md) |
| Permission enforcement | ✅ **Resolved** — the zod policy schema (tool globs plus argument eq/regex, browser and network matchers, four buckets) and `resolvePermission`/`checkPermission`. [10 §1](10-aside-enforcement-and-native.md) |
| The shape of the approval UI | ✅ **Resolved** — three suspension kinds, **designed to render in a chat channel.** [10 §1.5](10-aside-enforcement-and-native.md) |
| `Aside Computer Use` | ✅ **Partly resolved** — a native binary reaching the system-wide accessibility tree, an event tap, screen capture, Vision and Contacts. Control flow not traced. [10 §2](10-aside-enforcement-and-native.md) |
| Company details (YC batch, team size, founders) | ⚠️ Secondary sources say "YC Fall 2025 / three people / founded 2024," which is **internally inconsistent** (an F25 batch with a 2024 founding). Not primary-confirmed — not stated as fact in the body |

> 📌 Many of these cells started as "not published." That was **not because the product was immature
> but because nobody had taken it apart.** Opening it on 2026-09-23 resolved most of them —
> [08](08-aside-code-level.md), [09](09-aside-browser-internals.md),
> [10](10-aside-enforcement-and-native.md). The original warning not to read a difference in
> available information as a difference in maturity proved itself.

## 4.5 What this study overturned about itself

| Earlier statement | Verdict |
|---|---|
| "Comet is the **exact opposite structure** to Aside" ([04 §1](04-comet-architecture.md)) | ❌ **Refuted.** Aside's agent is an MV3 extension too. They made the same structural choice; the real difference is **planning location.** The original text is kept with a correction marker |
| "`opencode` appears 100 times in the daemon" (initial scan) | ❌ **False positive.** Most were the ANSI colour variable `openCodes`. The meaningful occurrences are the provider id and the `x-opencode-*` headers |
| "No product documents input separation" ([07 §8](07-security.md)) | ❌ **Partly refuted.** Dia documents it concretely — no verbatim URL passing, password fields and irreversible buttons removed from the agent's perception. [11 §2.3](11-dia-and-neon.md) |
| "Opera Neon's unit of reuse is Skills" ([05 §3](05-comparables.md)) | ❌ **Refuted.** An error inherited from a secondary source. The official name is **Cards**, and the axis differs (task type, not named invocation). [11 §3.4](11-dia-and-neon.md) |
| Neon "all AI processes run locally" (`opera.com/llms.txt`) | ❌ **The vendor's own two primary sources contradict each other.** The product FAQ states that planning uses cloud LLMs. The more specific source was taken. [11 §3.1](11-dia-and-neon.md) |

> 📌 The first entry is a case of **a conclusion being overturned as primary material accumulated.**
> That is why this repository does not delete refutations — deleting them would also delete the
> reason the earlier belief was held.

## 5. Comet — grade

Everything in [04](04-comet-architecture.md) is 🔧 **observed implementation** — Zenity's reverse
engineering, not a specification Perplexity guarantees. It follows that:

- the vendor can change it without notice; extensions auto-update from the server
- changes after the reverse-engineering date are not reflected
- it is nevertheless **closer to the truth than marketing copy** — this repository's default stance

## 6. Atlas — confirmed and unconfirmed

| Item | Grade |
|---|---|
| Released 2025-10-21 (macOS), retired **2026-08-09** | ✅ several sources agree |
| Features absorbed into ChatGPT and Codex, 30-day wind-down, manual bookmark export | 📰 |
| Reason — **consolidation** (CNBC 2026-03-19) vs. **security maintenance** (OpenAI help centre) | ⚠️ **Both are published and the weighting is not stated.** Both are recorded in the body |
| The OWL architecture, screenshot popup compositing | 📰 (reported via an OpenAI engineering post; the original was not read directly) |

⚠️ **The OpenAI help centre page (`help.openai.com/.../evolving-atlas-into-chatgpt...`) returned HTTP
403 and could not be read directly.** Everything about the retirement is via secondary sources.

## 7. Method, and its limits

### What was used

1. Try **the `.md` suffix and `/llms.txt`** on product documentation first → Aside's entire
   documentation obtained as primary text
2. Prefer **reverse engineering and security research over marketing pages**
3. **Cross-check vendor benchmark claims against a third-party leaderboard** → the verdicts in §3
4. **Actively look for internal inconsistencies between documents** → two found in §4
5. **(2026-09-23) Opened the binaries.** Installed the Linux CLI, extracted the Node SEA payload,
   obtained an unobfuscated ESM bundle of 67,774 lines. Reproduction in [08 §1](08-aside-code-level.md)
6. **(2026-09-23) Separated Chromium inheritance from product features.** When post-quantum symbols
   appeared, the fact that **Chromium ships X25519MLKEM768 TLS by default** meant **checking file
   location first.** Only after confirming they were in Aside's own code (Vault and daemon) was it
   written as settled
7. **(2026-09-23) Opened the browser DMG too** — statically, without running it. The three internal
   extensions' manifests, the daemon's Node SEA payload (258,965 lines) and the Vault's cryptographic
   call sites. Reproduction in [09 §1](09-aside-browser-internals.md)

### What was not done — plainly

| Item | Why |
|---|---|
| **The GUI was never seen** | The research environment is headless Linux and **Aside's browser has no Linux build.** The CLI was installed and analysed (§08) but the browser UI remains unverified. Actual UI, animation, progress representation and the appearance of approval modals cannot be confirmed. [03](03-aside-design-ux.md) is limited to **the interaction model the documentation specifies** |
| No login | `aside login` would use the user's account credentials and was not requested. So the real `skills list`, memory contents and remote-host behaviour are unverified |
| The daemon was not exhaustively analysed | Permission enforcement was confirmed ([10](10-aside-enforcement-and-native.md)) but the agent loop's details were not explored |
| No dynamic analysis | What goes to a server, and the real execution path, lie beyond static analysis |
| Dia and Neon binaries | Not analysed. Nothing there is verified to Aside's standard |
| Original research papers (University of Washington and others) | Only secondary reporting was checked |

### Next

- [x] ~~`aside repl`/`mcp` surface~~ → specification obtained in [08](08-aside-code-level.md)
- [x] ~~Open the browser binary~~ → [09](09-aside-browser-internals.md)
- [x] ~~Permission enforcement / `Aside Computer Use` / Secure Enclave and post-quantum~~ → [10](10-aside-enforcement-and-native.md)
- [x] ~~Dia and Opera Neon primary documentation~~ → [11](11-dia-and-neon.md)
- [ ] Trace `Aside Computer Use`'s control flow (symbols only so far)
- [ ] Dynamic observation — what goes to a server. Beyond static analysis
- [ ] **Confirm the browser GUI on a macOS/Windows machine** — impossible on Linux
- [ ] Details of Neon's Tasks — the FAQ answers were not extracted completely
- [ ] **Analyse Dia's and Neon's binaries** — they are currently taken on documentation. The
  verification asymmetry remains

## 8. Shelf life

This field **overturns quarterly.** During the research period alone: Atlas was retired (2026-08),
Comet went fully free (2026-03), and Aside shipped Windows. The first move of a re-investigation is
not gathering new facts but **checking existing facts for drift** — especially the inconsistent items
in §4 and the price and platform table in [01 §4](01-landscape.md).
