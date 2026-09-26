---
type: concept
status: active
last_ingested_from: agent-ux/09-design-language.md + agent-ux/08-primitives-rendered.md + agent-ux/01-landscape.md
related_pages: [concepts/approval-gate, concepts/thread-turn-item, concepts/harness, concepts/perception-model]
created: 2026-09-26
updated: 2026-09-27
---

# Agent Client Design Language — how harness primitives are shown to people

- Purpose: the shared design language of agent clients, and where their theories of supervision part.
- Scope: structure, visual system, vocabulary, behaviours; the three client families
- Primary source: ten shipped clients (installers unpacked, source at pinned commits), 2026-09-26 — [`agent-ux/`](../../../agent-ux/README.md)
- Updated: 2026-09-27 (agent-ux/08 §6.2 GUI-pass narrowing of the amber rule)

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | Families | first-party apps · agent-first editors · **orchestrators that wrap other vendors' agents** |
| 2 | Structure | sidebar of agents · **conversation spine** · right rail of artifacts (diff, files, terminal, browser, plan) |
| 3 | Colour | neutral chrome, **colour spent on state**; brand ≠ accent; borders as ink at low alpha |
| 4 | Theming | **VS Code theme keys as the token API** (OpenAI, Cursor, Antigravity 1.x, Devin) |
| 5 | Words | "Allow ⟨agent⟩ to ⟨verb⟩?" · once/session/always · Queue/Steer · Needs you · Ready for review |
| 6 | Autonomy | a dial with a **machine reviewer** in the middle |
| 7 | Attention | **amber/orange = needs you** in declared status vocabularies; working is blue (unambiguous) or yellow (needs a second channel). *Narrowed 2026-09-27 (GUI pass): in-app, orange also marks a risky state (ChatGPT `Full access`) and Claude's working mark is clay — the hue is not reserved* |
| 8 | Divergence | the **theory of supervision** — steps, deliverables, or a board — not the style |

> ⚠️ Read from the parts list: tokens, fonts, icons and strings were extracted; **nothing was seen
> rendered.** Visual impressions stay unverified until a GUI pass. *(2026-09-27: a passive macOS pass of five
> installed apps confirmed the layouts and narrowed row 7; approval cards and live states are still unseen —
> [`agent-ux/99`](../../../agent-ux/99-sources.md).)*

## §2 Words converge faster than pixels  {#s2-words}

OpenAI's Electron app and its legacy SwiftUI app share strings ("Approve for me", "A carefully prompted
reviewer agent…") and no components. Conductor copies Claude Code CLI prompts verbatim. The **vocabulary
is the portable layer** — a new client that adopts it inherits users' expectations.

## §3 The vendor/orchestrator split in the parts list  {#s3-split}

| | Vendors | Orchestrators |
|---|---|---|
| Icons | their own (Anthropicons, Cursor Icons 16, Material Symbols, Central Icons) | lucide |
| Fonts | Anthropic bundles Sans/Serif/Mono; others system | Geist (Orca, Conductor); Nerd Font so wrapped TUIs render |
| Agent state | their own event stream ([[concepts/thread-turn-item]]) | **inferred** — hooks in the agent's global config, in-band escape codes, title glyphs |
| Approval default | ask or machine review | **off** in three of four ([[concepts/approval-gate]] §7.6) |

## §4 Where the philosophies part  {#s4-philosophies}

- **IDE**: "there is no IDE" (Antigravity 2.0) vs "a full IDE with an agent manager built in — not the other way around" (Devin Desktop). Same ancestor, opposite answers.
- **Trust**: in a card (Claude's ladder to "for {n} days") vs only in a mode (Paseo, Aside).
- **Review**: deliverables at milestones (Antigravity Artifacts) vs every step at a chosen density (Cursor, Claude).
- **Personality**: calm ("The app is calm so the user's work is not" — Paseo) vs playful (Conductor's cities and transit chimes, Codex Pets).

## §5 Checklist for an agent client  {#s5-checklist}

- [ ] Adopt the shared vocabulary before inventing your own
- [ ] Neutral chrome; colour for state; git/PR state in the token system
- [ ] Map tokens onto VS Code theme keys if you will live in an editor
- [ ] Approval request as **data** any channel can render; never bind bare Enter to approve
- [ ] Sandbox state in the mode label; amber/orange for "needs you" in status indicators — and if you also use it for risk or working, keep those out of the status channel
- [ ] Density as a user lens; name completion for the next step
- [ ] Protect trust surfaces from theming
- [ ] Write down your theory of supervision — the layout follows from it

## §6 Read next  {#s6-next}

- [[concepts/approval-gate]] §7.6 — the card, across ten clients
- [[concepts/thread-turn-item]] — the items these transcripts render
- Originals: [`agent-ux/09-design-language.md`](../../../agent-ux/09-design-language.md), [`agent-ux/08-primitives-rendered.md`](../../../agent-ux/08-primitives-rendered.md)
