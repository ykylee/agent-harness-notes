# 09. The shared design language — and where the philosophies part

> The study's answer. [08](08-primitives-rendered.md) crossed the ten clients by harness primitive; this
> document asks what they share **as a design language** — structure, visual system, words, behaviour —
> and what each one believes. Every claim traces to a product document ([02](02-claude-desktop.md)–[07](07-paseo-conductor.md))
> where the artifact is cited. Researched 2026-09-26.
>
> Grade: token values, font files, icon sets and strings are ✅ (extracted). Anything about how they
> **look together** is ⚠️ — the design language here is read from the parts list, not from the screen.

## 1. In one paragraph

Agent clients in 2026 speak one language with regional accents. **Chrome is quiet and near-monochrome;
colour is spent on state.** The layout is a **sidebar of agents, a conversation spine, and a right-hand
rail of artifacts.** Density is an IDE's (13–14 px base), and borders are **ink at low alpha**, not greys.
The words are shared almost verbatim — *Allow … to …?*, *Queue / Steer*, *Needs you*, *Ready for review*,
verb pairs that go from *Reading* to *Read 3 files*. Autonomy is **a dial with a machine reviewer in the
middle.** Where they part is not style but **belief**: whether the IDE survives, whether trust lives in a
card or a mode, whether the agent should be visible or ambient.

## 2. Structure

| Convention | Evidence |
|---|---|
| **Three columns**: agents · conversation · artifacts | Claude Code tab, ChatGPT/Codex side panel, Cursor Glass, Antigravity 2.0, Orca, Superset, Conductor ([08](08-primitives-rendered.md) §6.1) |
| **The conversation is the spine**; diff, terminal, browser, plan are **peer panes** around it | Claude ("chat, diff, browser, terminal, file, plan, tasks, and subagent" panes), Codex side-panel tabs, Cursor right panel |
| **A second, agent-first surface beside the IDE** | Cursor Glass vs IDE (every setting tagged `surface:"glass"` or `"ide"`); Antigravity Manager vs Editor → split into two apps; Devin's Command Center as the default screen |
| **The board** as the fleet view | Devin Kanban, Orca dashboard, Superset board — with **agent state and PR state fused** into one column set (Superset, Conductor) |
| **A floating composer** summoned from anywhere | Claude Quick Entry (double-tap Option), Codex popout (Option+Space), Cursor full-screen tabs "replace the agent chat with a floating prompt bar" |

> 📌 **The editor stopped being the centre.** In every agent-first surface the conversation is the spine
> and the editor is one pane among several. The products that kept the editor central did it by giving
> the agent **its own window** rather than a side panel.

## 3. The visual system

### 3.1 Colour: quiet chrome, loud state

| Principle | Where it is written down or shipped |
|---|---|
| Neutral chrome, **colour reserved for state** | Orca `STYLEGUIDE.md`: "monochrome and quiet — neutral grays carry the chrome, color is reserved for state"; OpenAI's primary intent is **greyscale** (`primary-solid` = `gray-900`); Cursor's semantic ladder is five `color-mix` alphas of one foreground |
| **Brand ≠ interactive accent** | Claude: clay `#d97757` is brand-only, accent is blue `#2a78d6`, Pro is violet; OpenAI keeps blue for info/accent; Paseo: "Accent is the one CTA per surface" |
| **Borders and fills are ink at low alpha** | Claude `--cds-alpha-2` (ink 10%); OpenAI borders ink at 5/8/12%; Cursor surfaces `color-mix(base N%, transparent)`; Superset fills `color-mix(fg 7%/10%)` |
| **Git and PR states are first-class tokens** | Claude `--cds-*-git-{added,removed,modified,merged,opened,closed,draft,queued,conflicting}`; Cursor `--cursor-added/removed/modified`; Orca `git-decoration-*` "mirroring VS Code's palette"; Conductor `--git-*`, `--status-*` |
| **Status colour generated, not picked** | Paseo: one OKLCH lightness + one chroma fraction per set, "Regenerate the set, never one hue", a louder band for 6 pt dots |
| **Trust surfaces immune to theming** | Orca `--orca-security-*`: "a pack cannot disguise a trust decision"; Claude's consent window copies token *values* into a React-free page, pinned by a test |

**Warm dark is a recurring default** — Superset "ember" `#151110` with terracotta `#e07850`, Conductor
stone/brown `#141110`, Paseo ships a "claude" theme (accent `#d97757`) — next to OpenAI's and Cursor's
pure neutrals. ⚠️ Whether that reads as a trend on screen was not seen.

### 3.2 Theme bridging — the VS Code theme became a token API

Four products map their own semantic tokens **onto VS Code theme keys**, so one component library renders
inside any editor theme:

| Product | Direction |
|---|---|
| ChatGPT/Codex | `--color-token-*` **is** VS Code's key vocabulary; in the IDE extension every one is rebound to `--vscode-*` (413 references) |
| Cursor | `--cursor-*` re-pointed at `--vscode-*` in IDE mode (`--cursor-blue: var(--vscode-terminal-ansiBlue)`) |
| Antigravity 1.x | Tailwind classes bound straight to `--vscode-*`; 2.0 reverses it — **three seeds** → own tokens → legacy VS Code keys |
| Devin Desktop | VS Code theme → `@cognitionai/ds` tokens at runtime, with a `contrastGuard` |

> 📌 **VS Code's theme schema is the lingua franca of agent-client theming**, even for products that are
> no longer IDEs. It is the only colour vocabulary that already has thousands of community themes.

### 3.3 Type, shape, motion, icons

| Axis | Convergence | Outliers |
|---|---|---|
| **Density** | 13–14 px base (OpenAI remaps Tailwind `text-base` to 14; Cursor 13; Paseo 14; Orca 11–14) | Claude offers `comfortable` / `compact` density and `sm`/`lg` message text |
| **UI font** | **system font** (OpenAI, Cursor, Paseo, Antigravity follows the host, Superset) | **Anthropic bundles its own** Sans/Serif/Mono (serif token named `--cds-font-voice`); Orca and Conductor bundle **Geist**; OpenAI Sans only in onboarding |
| **Mono** | system or JetBrains Mono (Cursor); **Symbols Nerd Font** bundled so wrapped TUIs render (Orca, Conductor) | Conductor also bundles iA Writer Mono |
| **Radius** | ~6–10 px controls | OpenAI switches to **squircles** (`corner-shape: superellipse(1.5)`, radii ×1.25) where the engine supports it |
| **Motion** | short: 100–200 ms, expo-out (`cubic-bezier(.16,1,.3,1)` Orca, `(.19,1,.22,1)` OpenAI); **Reduce Motion** setting in Claude, OpenAI, Cursor | Claude's CSS `linear()` **spring** button; Cursor Glass translucency with **Reduce Transparency** |
| **Icons** | **vendors own theirs** — Anthropicons (variable icon font), Cursor Icons 16 (1,620 glyphs), Material Symbols (Google), Central Icons (Cognition) | **orchestrators use lucide** (Orca: "Don't import a second icon library", Superset, Paseo, Conductor; OpenAI too) |
| **Primitives** | **Base UI** — Claude, Cursor Glass, Antigravity 2.0, Devin, Conductor (Radix still present in several, a migration in progress ⚠️) | Paseo: no component library (React Native) |

## 4. The words

The strongest convergence in this study is **lexical**. Products that share no code share sentences.

| Pattern | Examples |
|---|---|
| **"Allow ⟨agent⟩ to ⟨verb⟩?"** | Claude, ChatGPT/Codex, Orca; Devin "Devin is requesting to…" |
| **Scope words** | *once · this chat/conversation · this session · always* — in Claude, Codex, Superset, Conductor, Antigravity, Devin (ACP `allow_once/allow_always`) |
| **Progressive → past, counted** | "Reading files → Read 3 files" (Claude, Orca), "Running JavaScript → Ran JavaScript" (Codex), "Grepping → Grepped" (Cursor) |
| **"Needs you" / "waiting on you"** | Claude, Orca, Superset "Needs attention", Conductor "Needs permission / input / plan response", Cursor "Needs Attention" |
| **Completion as next step** | "Ready for review" (Superset, Devin), "Ready to merge" (Conductor) |
| **Queue / Steer** | Codex, Cursor, Paseo, Conductor, Devin ("Guide"), Aside |
| **Turbo / YOLO / Bypass** for no-ask | Antigravity & Devin "Turbo" (shared Codeium enum `EAGER`), Cursor's code still says `YoloMode`, Orca "Yolo", Claude "Bypass permissions" |
| **Machine reviewer** | "Auto" (Claude), "Approve for me" (OpenAI), "Auto-review" (Cursor, Codex in Paseo) |

> 📌 **Words converge faster than pixels.** OpenAI's two stacks (Electron and legacy SwiftUI) share
> strings — "Approve for me", "A carefully prompted reviewer agent…" — while sharing no components.
> The vocabulary is the portable layer of the design language; a new client adopting it inherits users'
> expectations for free.

## 5. The behaviours

1. **Autonomy is a dial, not a switch** — Cursor's phrase, everyone's structure: ask · allowlist ·
   machine review · no-ask, with the sandbox named in the label ([08](08-primitives-rendered.md) §2).
2. **Detail is a lens the user holds** — Claude Normal/Thinking/Verbose, Cursor's five densities,
   Conductor's "Garry Mode". Not a fixed fold policy.
3. **Review is a conversation** — diff comments batch into a prompt (Claude, Orca, Paseo, Conductor,
   Superset). Plans are commentable documents (Claude, Cursor, Antigravity Artifacts).
4. **Attention is budgeted** — "asking for permission too often creates its own safety problem"
   (Cursor); presence-routed notifications, "never for errors" (Paseo); pulse only for human-needed states
   (Superset); **"UI copy must not overclaim"** and an explicit "No recent update" state (Orca).
5. **The agent's presence leaves the window** — Window Halo, Hardware Buddy, Pets, Codex Micro LEDs,
   mobile companions (Orca, Superset, Paseo), completion sounds.
6. **Say what you fell back to** — "Bypass permissions isn't allowed here, so this session switched to
   Accept edits" (Claude); "Disabled by requirements.toml" (OpenAI); "Run Mode Controlled by Team Admin"
   (Cursor).

## 6. Where the philosophies part

| Question | One answer | The other |
|---|---|---|
| **Does the IDE survive?** | Antigravity 2.0: "there is no IDE" | Devin Desktop: "a full IDE with an agent manager built in — not the other way around"; Cursor: invest in the IDE "until codebases are self-driving" |
| **Where does standing trust live?** | in a **card** — Claude's ladder to "for {n} days" and "Always allow", with nudges | in a **mode** only — Paseo (no client sends a standing grant), Aside ("Allow once" only) |
| **What does the person review?** | **deliverables** — Antigravity: "you review high-level deliverables at key milestones" | **every step, at a chosen density** — Cursor, Claude |
| **Should the user choose where work goes?** | no — Claude: "You don't have to choose where a task goes" (Chat and Cowork merged) | yes — Cursor's two surfaces, Codex's "Work in: locally / worktree / remote / cloud" |
| **Personality** | calm — Paseo: "The app is calm so the user's work is not"; Orca: chrome "should recede and frame" | playful — Conductor's cities, Passport and transit chimes; Codex Pets; Cursor's confetti cannon; Devin's "Cooking" |
| **Who owns the agent?** | the client (first-party apps, editors) | someone else — orchestrators wrap it, infer its state, and mostly turn its approvals off |

> 📌 **The styles converged; the theories of supervision did not.** Every product agrees on how an
> approval card should read and what colour "needs you" is. They disagree on whether a person should be
> watching steps, reviewing deliverables, or directing a board — and that disagreement decides the layout
> more than any token does.

## 7. Against this repository's engine-side findings

| Engine-side conclusion | What the clients show |
|---|---|
| Approval must be a protocol primitive ([`SYNTHESIS.md` §2.1](../SYNTHESIS.md)) | Confirmed on the client side: Superset's own design research says "**Approvals are items** … bound to the transcript row" ([06](06-orca-superset.md)); Paseo's request object with four renderers; Codex's inline request card is a rendered App Server request |
| Approval prompts should render in a channel ([`SYNTHESIS.md` §2.1](../SYNTHESIS.md)) | Paseo made it a protocol rule; Claude routes approvals to hardware; Codex to an LED keypad |
| A gate must be on by default and fail closed ([`SYNTHESIS.md` §2.7](../SYNTHESIS.md)) | **Contradicted in practice by three orchestrators**, which launch wrapped agents with approvals off; the machine-reviewer rung is the industry's answer to prompt fatigue, and at least one vendor says it "is not a security boundary" |
| Permission expressiveness: tool globs + per-argument matchers ([`browser-agents/10`](../browser-agents/10-aside-enforcement-and-native.md)) | Codex's **prefix rule** and Antigravity/Devin's **editable targets** reach per-argument scope from the UI side |
| Thread / turn / item ([`docs/02`](../docs/02-app-server-protocol.md)) | Every transcript renders **items as verb sentences**; turns appear as "Worked for {t}" summaries |

## 8. What this means if you are building an agent client

- [ ] Adopt the **shared vocabulary** before designing your own — Allow…to…?, once/session/always,
      Queue/Steer, Needs you, Ready for review
- [ ] Keep chrome neutral and **spend colour on state**; keep brand colour out of interactive affordances
- [ ] Map your tokens onto **VS Code theme keys** if you will ever live inside an editor
- [ ] Put **git/PR state in the token system**, not in ad-hoc colours
- [ ] Make the conversation the spine and everything else a **peer pane**
- [ ] Give users a **density lens** over the transcript
- [ ] Budget attention: pulse only for human-needed states, route notifications by presence
- [ ] Protect trust surfaces from theming, and render consent where untrusted content cannot reach
- [ ] Decide — and write down — your **theory of supervision** (steps, deliverables or board); the layout follows

## 9. Open questions

- The whole visual layer: nothing was seen rendered. A GUI pass on macOS/Windows would move many ⚠️ to ✅. *(2026-09-27: a passive macOS pass covered ChatGPT, Claude, Antigravity, Orca and Aside — layouts confirmed, the amber rule narrowed ([08 §6.2](08-primitives-rendered.md)); approval cards and agent states still need a live run.)*
  — the same device constraint recorded in the session handoff
- Whether the lexical convergence is deliberate (shared people, shared specs) or independent — Conductor
  copying Claude Code CLI copy verbatim is deliberate; the rest is not established
- Mobile: three orchestrators ship phone companions; their design language was not studied here
