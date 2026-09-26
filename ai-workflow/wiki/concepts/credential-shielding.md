---
type: concept
status: active
last_ingested_from: browser-agents/06-architecture-axes.md + browser-agents/09-aside-browser-internals.md + browser-agents/11-dia-and-neon.md + SYNTHESIS.md §6.4 + strands/04-harness-and-cli.md + strands/07-security.md
related_pages: [concepts/indirect-prompt-injection, concepts/perception-model, concepts/approval-gate, concepts/control-plane-execution-plane, concepts/primary-source-verification]
created: 2026-09-23
updated: 2026-09-26
---

# Credential Shielding — logging an agent in without giving it the secret

- Purpose: compare the design patterns that let an agent work behind a login without seeing the credentials.
- Scope: three approaches, separating the axes, what the implementation really is, what remains
- Character: **a surface-specific axis** — though "separate permission level from secret exposure" is a general principle
- Updated: 2026-09-26 (re-checked against `SYNTHESIS.md` changes since the last ingest — none touch the sections this page draws on; previously masked by a freshness-checker parsing bug)

## §1 The problem  {#s1-problem}

An agent working inside logged-in sites needs credentials. But agents are **vulnerable to prompt
injection** ([[concepts/indirect-prompt-injection]]). **Hand it the secret and a fooled agent hands
it straight out.**

## §2 Three approaches  {#s2-approaches}

| Approach | Adopted by | Principle | Assessment |
|---|---|---|---|
| **URL blocking** | Comet | **blocks** access to credential pages such as `chrome://password-manager`, and `file://` | **enumerative** — a new path defeats it |
| **Value hiding** | **Aside** | the browser fills the field **without giving the agent the raw password** | **fundamental** — removes the secret from what the agent can observe |
| **Element hiding** | **Dia** | password fields and **irreversible action buttons** are "invisible to the agentic system" | **fundamental, and broader** — reaches past credentials. ⚠️ the grade is for the *mechanism*; §7.1 measures how easily the implementation of it leaks |
| (for contrast) transmission limits | Opera Neon | credentials and payment details are **not sent to Opera's servers** | **a different layer** — agent visibility is a separate question |

> 📌 **Value hiding and element hiding are two solutions to one problem.** Aside hides the **value**;
> Dia hides the **element.** Dia's reaches further — erasing "irreversible action buttons" too
> extends past credentials to destructive actions generally.
>
> ⚠️ Neon's guarantee is on another layer. "It does not go to Opera's servers" does not mean **the
> agent cannot see it.** Since planning runs on cloud models
> ([[concepts/control-plane-execution-plane]]), what is included when page context reaches the model
> is **unverified.**

## §3 The core principle — permission level and secret exposure are different axes  {#s3-axis-split}

The most copyable piece of Aside's design.

> A saved password value stays **hidden from the AI even in `full-access` mode.**
> Access policy **and target URL** are both checked before autofill.

> 📌 **"Highest privilege" does not mean "can see everything."** The same pattern appears in the
> sandbox — even `full-access` keeps `sandbox.enabled: true`
> ([[concepts/os-sandbox-policy]] §8.5). Raising the privilege level and removing a defence were
> **kept separate.**

### §3.1 Consistency of isolation modes  {#s3-1-consistency}

> **The agent cannot use the password manager in an incognito session.**

If you declare isolation, apply it **consistently through credentials.** Partial isolation is not
isolation.

## §4 What the implementation really is — Aside Vault  {#s4-implementation}

Verifying the marketing claims ("hardware-backed E2E encryption, Secure Enclave, post-quantum") in
the binary. Based on **real call sites in `background.js`, not libsodium's exported constants**:

| Primitive | Calls | Role |
|---|---|---|
| `crypto_pwhash_str` | 13 | password hashing |
| **`crypto_box_seal`** | 12 | **anonymous public-key sealing** |
| `crypto_aead_xchacha20poly1305_ietf_encrypt`/`_decrypt` | 7/7 | AEAD |
| `crypto_secretbox_easy`/`_open_easy` | 4/4 | symmetric |
| `crypto_kdf_derive` | 3 | key derivation |

Key derivation uses **`ARGON2ID13`** with `memlimit_interactive`.
Post-quantum is **ML-KEM-768** (`crypto_kem_mlkem768_*`, with wrappers `mlKemEncapsulate` and
`mlKemDecapsulate`). Secure Enclave appears as `kSecAttrTokenIDSecureEnclave` and
`CanCreateSecureEnclaveKeyPairBlocking`. Audit logging is `appendAuditEvent` plus
`getPasswordAuditLogsDir`.

> 📌 **That `crypto_box_seal` appears 12 times fits the design.** A sealed box is encrypted to the
> recipient's public key such that **even the sender cannot decrypt it** — the right primitive for
> "never give the agent the raw value."

> ⚠️ **A verification trap on record**: post-quantum symbols appear in any Chromium fork because
> **Chromium ships X25519MLKEM768 TLS by default.** Only after **separating by file location** and
> confirming they sit in the product's own code (Vault and daemon) was this written as a product
> feature. [[concepts/primary-source-verification]] §3.6.

## §5 And yet — which way the defaults point  {#s5-defaults}

Good design does not guarantee good defaults.

| Product | Item | Default |
|---|---|---|
| Aside | AI credential access policy | **`Always allow`** (the loosest) |
| Aside | permission rule `default` | **`allow`** |
| Dia | content data collection | **on** (30-day retention) |

> ⚠️ **Writing good cryptography and setting narrow defaults are different jobs.** Check the defaults
> first when adopting.

## §6 What to carry into a custom harness  {#s6-porting}

- [ ] Go with **value hiding.** URL blocking is enumerative
- [ ] Consider also **removing dangerous elements from perception** (Dia's approach) — it extends past credentials
- [ ] Keep **permission level and secret exposure on different axes**
- [ ] Apply isolation modes **consistently through credentials**
- [ ] Check **access policy and target URL together** before autofill
- [ ] **Set defaults narrow**
- [ ] Keep an **audit log** of credential access

## §7 Measured — what "hide the element" and "hide the value" cost in practice  {#s7-measured}

Ingested from [`SYNTHESIS.md` §6.4](../../../SYNTHESIS.md). Both approaches in §2 were implemented
and attacked. Two findings, and the second is not about fields at all.

### §7.1 "Element hiding" and "value hiding" both need a definition of *which* element  {#s7-1-which}

§2 grades element hiding as **fundamental**. That grade holds only for the choice of mechanism. The
implementation is where it is won or lost:

| Test used | Result |
|---|---|
| `type === "password"` | 🚨 **leaks.** `<input type="text" autocomplete="current-password">` and a field masked only by `-webkit-text-security` both handed the value to the model |
| the field's declared behaviour — `autocomplete` token, computed text-security, then a name hint | ✅ holds against the same attacks |

> 📌 **A page that wants the value out does not attack the shield — it declares the field
> differently.** The first three signals cost nothing to honour, because they are declarations the
> page already makes to the browser and to password managers. A type check is not a weaker version of
> this; it is a different and much smaller claim.

### §7.2 The credential that is not in a field  {#s7-2-url}

With every field on the page correctly shielded, the secret still reached the model — **in the page
URL**, printed in the snapshot header.

```
# http://host/reset?token=hunter2&user=a%40b.com
```

Password-reset tokens, OAuth `code`, magic links and session ids live in URLs as a matter of routine.

> 📌 This retroactively explains a Dia defence that looks like a footnote in §5 of
> [[concepts/indirect-prompt-injection]]: **"Dia won't pass URLs to the LLM verbatim."** Read as a
> product note it seems fussy. Measured, it is a credential channel — and the only one on this page
> that no amount of field shielding reaches.
>
> 📌 The failure was **inconsistency between renderers**, not a missing rule: the approval prompt had
> shortened URLs for months while the snapshot header printed them whole. The same value was
> dangerous in one renderer and harmless in another. A rule each call site must remember is a rule
> one call site will forget.

### §7.3 What this does not cover  {#s7-3-limits}

Shielding by behaviour is still a list of signals. A field that declares nothing — no
`autocomplete`, no masking, a neutral name — is invisible to all of them. And shielding stops the
*model* seeing the value; it says nothing about where the page itself sends it.

## §7.4 Observation — a harness that holds keys in its own environment  {#s7-4-strands}

The Strands CLI never writes API keys to its config file ✅ — then loads them into `process.env`,
which every `shell` call inherits; the library's host sandbox inherits `env` the same way
([`strands/07`](../../../strands/07-security.md) §4). One approved `env` prints every key the harness holds.

> 📌 §3's axis split has a precondition: the harness's **own** credentials must not be in the tool
> process's environment. Scrubbing provider variables from child processes is the cheapest shielding
> there is, and it is the one most easily forgotten because nothing about the *user's* secrets is involved.

## §8 Read next  {#s8-next}

- [[concepts/indirect-prompt-injection]] — why the agent must not hold the secret
- [[concepts/perception-model]] — element hiding is an operation on the perception layer
- [[concepts/control-plane-execution-plane]] — planning location decides how the execution plane treats secrets
- Original: [`browser-agents/06-architecture-axes.md`](../../../browser-agents/06-architecture-axes.md) §4
- Strands case: [`strands/04-harness-and-cli.md`](../../../strands/04-harness-and-cli.md)
