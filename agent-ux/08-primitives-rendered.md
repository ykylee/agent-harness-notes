# 08. The primitives, rendered — a cross-product matrix

> The three engine-side studies in this repository found a set of harness primitives: approval,
> autonomy policy, plans, thread/turn/item, diffs, parallel work, steering
> ([`SYNTHESIS.md` §2](../SYNTHESIS.md), [`docs/02`](../docs/02-app-server-protocol.md)). This document
> crosses the ten clients of [01](01-landscape.md) **one primitive at a time**. Every row is drawn
> from the product documents [02](02-claude-desktop.md)–[07](07-paseo-conductor.md), where each
> string is cited; the Aside rows come from [`browser-agents/03`](../browser-agents/03-aside-design-ux.md).
> Researched 2026-09-26.
>
> Grade: strings and enums are ✅ (extracted); how anything **looks** is ⚠️ — no display was used.

## 1. Approval

### 1.1 The sentence

| Product | Prompt grammar (verbatim) |
|---|---|
| Claude desktop | `Allow Claude to <b>{action}</b>?` — one template, 40+ variants; the verb is bold, Claude is always the subject |
| ChatGPT/Codex | `Allow ChatGPT to run this command?` · `Do you want {actor} to run this command?` — **the actor is a parameter** (ChatGPT vs Codex persona) |
| Cursor | `Allow this action?` |
| Antigravity 2.0 | `Approve this action` · `Requesting your permission in Terminal:` |
| Devin Desktop | `Devin is requesting to perform the following actions` |
| Orca (chat UI) | `Allow {tool}?` |
| Superset (chat pane) | approval row: **Allow** / **Allow for session** / **Deny** |
| Paseo | `request.title ?? name ?? "Permission Required"` + "How would you like to proceed?" |
| Conductor | `Do you want to run this command?` · `Do you want to make these changes?` — **Claude Code CLI copy, verbatim** |

> 📌 **"Allow ⟨agent⟩ to ⟨verb⟩?" is the de-facto sentence.** Three vendors name the agent as the
> grammatical subject; the CLI-derived ones ask "Do you want to…". None asks "Approve tool call?" —
> every product translates the tool call into **an action a person would recognise.**

### 1.2 The scope ladder

| Product | Rungs, narrowest → widest |
|---|---|
| Claude desktop | Allow once · for this chat · for this session · for this task · for all tasks · for all scheduled runs · **for {n} days** · Always allow · Always allow for this website · Always allow reads on this host · Don't ask again for this tool · Deny |
| ChatGPT/Codex | Allow once · Allow this conversation · Always allow · **Allow commands that start with {command}** (prefix rule) · Deny |
| Cursor | Allow · Allow all · Always run · Add to allowlist |
| Antigravity 2.0 | Allow Once · Always Allow · Deny — **target string editable in the card** |
| Devin Desktop | `allow_once · allow_always · reject_once · reject_always` (ACP) — **command editable, or rewritten from a description by a fast model** |
| Superset | Allow · Allow for session · Deny |
| Conductor | Yes · (per tool) "Allow all edits during this session" / "Yes, and don't ask again for: …" / "Yes for this session" · No |
| **Paseo** | **none** — no client ever sends a standing grant; persistence comes only from choosing a mode |
| Aside | **Allow once** only — "No lasting permission will be granted" |

> 📌 **Two poles.** Claude has the longest ladder of any product studied, including a **time-boxed**
> rung ("for {n} days") and an upgrade nudge ("Allowed once. Skip this card next time?") with an undo
> toast. Paseo and Aside have **no ladder at all** — standing trust lives in the mode, never in a card.
> Between them, Antigravity and Devin turn the card into a **scope editor**: you narrow or widen the
> target before approving, rather than choosing from fixed rungs.

### 1.3 Where it lives, and who else can answer

| Product | Placement | Keyboard | Other answerers |
|---|---|---|---|
| Claude desktop | inline card + approval dock; **connector consent in a React-free native window** | **1–9** pick an option | **Hardware Buddy** (BLE devices), Dispatch phone push |
| ChatGPT/Codex | inline request card in the thread | palette "Approve request" | **Codex Micro** keypad LEDs; "Approve for me" reviewer agent |
| Conductor | composer area | **bare Enter = approve**, ⌘Enter = alternate, Backspace = deny | — |
| **Paseo** | GUI card | — | **CLI** (`paseo permit allow …`), **MCP** (a parent agent answers its child), push — **one request object, four renderers** |
| Orca | card in the optional chat UI | — | the card **types `1` / `ESC` into the vendor's own TUI** |

> 📌 **Paseo implements what [`SYNTHESIS.md` §2.1](../SYNTHESIS.md) recommended.** Aside hinted "or just
> reply with your answer"; Paseo makes it a **protocol rule**: a message sent while a prompt is pending
> **denies it with a reason** ("The user answered with a message instead of approving. Their message
> follows.") and delivers the message into the same turn. Approval is data with server-supplied buttons,
> so any channel can render it.
>
> ⚠️ **Bare Enter approves in Conductor.** The key most often pressed by reflex is bound to *yes*.

## 2. Autonomy — every product now has a dial, and a machine in the middle

| Product | Modes (verbatim) | The machine-reviewer rung | Default |
|---|---|---|---|
| Claude desktop | Manual · Accept edits · Plan · **Auto** · Bypass permissions | Auto: "checks each tool call for risky actions and prompt injection" | Manual (Auto flag-gated ⚠️) |
| ChatGPT/Codex | Ask for approval · **Approve for me** · Full access · Custom (config.toml) · Managed | "A carefully prompted reviewer agent" | — |
| Cursor | Ask Every Time (hidden) · Allowlist (with Sandbox) · **Auto-review** (with Sandbox) · Run Everything (Unsandboxed) | LLM classifier; blocks go back to the agent first | — |
| Antigravity 2.0 | Default · Request Review · Turbo (+ Autonomous mode banner) | — | Default: auto inside sandbox, ask outside |
| Devin Desktop | (Cascade) Disabled · Allowlist Only · Auto · **Turbo** | — | — |
| Paseo | per provider, one shield-icon family | Claude `auto`, Codex `auto-review` | **machine review** |
| Orca | Yolo · Manual | — | **Yolo — every wrapped agent launched with its bypass flag** |
| Superset | per agent preset; chat pane Read Only · Auto · Full Access | — | **bypass in terminal**, ask in chat |
| Conductor | "Claude Code tool approvals" on/off | — | **off → `bypassPermissions`** |

> 📌 **The reviewer agent is the new middle rung.** Claude ("Auto"), OpenAI ("Approve for me"), Cursor
> ("Auto-review") and Paseo's defaults all insert **a model that approves on the human's behalf** between
> "ask me" and "never ask". Cursor states the reason: "asking for permission too often creates its own
> safety problem." Cursor also names the limit: "Auto-review is not a security boundary."
>
> 📌 **Sandbox state is moving into the mode label.** Cursor: "Allowlist (with Sandbox)", "Run Everything
> (Unsandboxed)". Codex's Full-access confirm lists Files / Terminal / Internet as three risk rows.
> OpenAI's docs draw the line exactly: "Changing who reviews a request doesn't expand the sandbox."
>
> ⚠️ **The orchestrators invert the default.** Orca, Superset (terminal) and Conductor launch wrapped
> agents with approvals off, so their attention UI is built around *questions* and *completions*, not
> permission prompts. Measured against [`strands/07`](../strands/07-security.md) §5 — a gate must be
> *on by default* — the fleet tools are where that property is most often missing.

## 3. Plans and todos

| Product | Plan is… | Approve with |
|---|---|---|
| Claude desktop | a mode **and** a pane; **commentable** like a diff | "You can comment on the plan in plan mode" |
| ChatGPT/Codex | a collapsible "Plan summary" card, "Step {n} / {m}" | **"Yes, implement this plan"** (`item/plan/requestImplementation`) |
| Cursor | an **editable markdown document**; todos sync into the file | Build Plan · Start Plan Now · build selected todos in a new agent |
| Antigravity | an **Artifact** with Google-Docs-style comments | **Proceed** |
| Devin Desktop | in-conversation todo list + a plan markdown file; keyword `megaplan` switches mode | Implement |
| Paseo | a permission of `kind:"plan"` | Reject · Implement · "Implement with Bypass" |
| Conductor | "Needs plan response"; feedback typed in the composer | Approve · **Hand off** to a new chat |

> 📌 **The plan became a document.** Four products make it editable or commentable text; none treats it
> as a read-only preview. The approval verb converged on **Implement / Proceed**, not "Approve".

## 4. The transcript — tool calls as sentences, detail as a lens

| Product | Tool-call grammar | Detail control |
|---|---|---|
| Claude desktop | "Reading files" → "Read 3 files"; interrupted "Stopped reading {file}" (373 strings) | **Normal / Thinking / Verbose** (Ctrl+O) |
| ChatGPT/Codex | ~900 hand-written active/past pairs, rolled up: "Worked · Ran commands · Edited files" | — |
| Cursor | Reading/Read, Grepping/Grepped… | **Tool Call Density**: Detailed · Diff Focus · Balanced · Grouped · Compact |
| Orca | "Reading 3 files" → "Read 3 files"; "Worked for {t}" | — |
| Paseo | one sentence per run: "edited 3 files, ran 2 commands and read 4 files" | — |
| Conductor | collapsed by default | "Don't collapse tool calls (**Garry Mode**)" |
| Devin Desktop | worklog; status fallback "**Cooking**" | — |

> 📌 **Present progressive while running, past tense and counted when done** — the same grammar in six
> products, independently. And **how much to show is the user's choice**, not a fixed fold policy
> (Claude three views, Cursor five densities, Conductor a toggle).

## 5. Diffs and review

| Product | Verbs | Review → agent |
|---|---|---|
| Claude desktop | **comments, not accept/reject**; "Resolved review comments collapse" | batch line comments with Cmd+Enter |
| ChatGPT/Codex | Undo / Reapply; colour-blind diff themes; "+/−" non-colour markers | inline diff comments |
| Cursor | **Keep / Undo** (Keep primary; Undo All needs a second click) | Agent Review / Bugbot |
| Antigravity | Accept Step / Reject Step; Accept all / Reject all | file-diff comments |
| Devin Desktop | Accept all / Reject all; in Devin Local, edits are approved **before** they apply | Quick Review subagent |
| Orca | — | **"Send to agent"**: one line-anchored batch ("sending comments one at a time causes the agent to swing back and forth") |
| Paseo | — | review comments become a **composer attachment** (`application/paseo-review`) |
| Conductor | viewed-file toggle, edit in diff | inline comments become a composer attachment; **todos block merge** |

> 📌 **The diff comment became a prompt.** Five products route review back to the agent as a batch.
> And the verb pair split three ways by *when* the edit applies: **Keep/Undo** (already applied —
> Cursor), **Accept/Reject** (proposed — Antigravity, Devin Local), **comment** (neither — Claude).

## 6. Parallel work and attention

### 6.1 Layout — one skeleton everywhere

```
[ sidebar: agents / sessions / workspaces, each with a state ]  [ centre: the conversation ]  [ right: tabs — diff · files · terminal · browser · plan · PR ]
```

Claude (Code tab panes), ChatGPT/Codex (side-panel tabs), Cursor Glass (right tab panel), Antigravity 2.0
(side pane), Orca, Superset, Conductor. The Kanban board is the variant: Devin Desktop's Agent Command
Center (default screen), Orca's dashboard (Needs You / Working / Done / Idle), Superset's board.

### 6.2 Colour of "needs you"

| Product | Working | **Needs you** | Done | Error |
|---|---|---|---|---|
| ChatGPT/Codex (Micro LEDs) | blue | **amber** | green | red |
| Paseo | blue | **amber** ("because it wants something from you") | — | — |
| Orca | yellow spinner | **orange** — "Orange, not amber: it has to stay separable from working-yellow" | emerald | red |
| Superset | amber, static | **yellow, pulsing** — only human-needed states pulse | green "Ready for review" | red, pulsing |
| Devin Desktop | pulsing icon | **amber dot** + ring | — | — |

> 📌 **Amber/orange means "needs you" in every product that declares a colour.** The disagreement is over
> *working*: blue (OpenAI, Paseo) keeps amber unambiguous; yellow (Orca, Superset) forces a second
> channel — a shifted hue (Orca) or motion (Superset).

### 6.3 Naming completion, and leaving the window

- **Completion is named for the person's next step.** Superset "Ready for review", Devin "Ready for
  review", Conductor "Ready to merge", Claude "waiting on you", Orca "Needs You".
- **Status leaves the screen.** Claude's **Window Halo** (the model calls `halo_attach` to glow the macOS
  window it is driving) and BLE **Hardware Buddy**; OpenAI's **Pets** and **Codex Micro** LED keypad;
  Paseo's presence-routed push ("never for errors"); Conductor's transit-chime completion sounds;
  Antigravity's action-required/done sounds.

## 7. Steering while it runs

| Product | Vocabulary | Default |
|---|---|---|
| ChatGPT/Codex | Send / **Queue / Steer** / Stop — "Steer — Submit without interrupting the model" | setting |
| Cursor | Queue / **Steer** — "applied at the next tool call" | setting |
| Claude desktop | **Queue** — "Claude will read this after the current turn" | queue (⚠️ docs say "after the current action") |
| Devin Desktop | "Guide Devin while it works, or press {shortcut} to queue" — **per message by modifier** | steer |
| Paseo | Interrupt / **Steer** / Queue; a pending permission is **denied** by the message | steer |
| Conductor | Queue / **Steer** | steer |
| Aside | Queue / Steer | — |

> 📌 **"Steer" is now a shared word** across seven products and three vendors. Its meaning converged too:
> deliver at the next safe boundary (a tool call), don't cut work off mid-action.

## 8. What this means if you are building an agent client

- [ ] Phrase approval as **"Allow ⟨agent⟩ to ⟨verb⟩ ⟨object⟩?"** — an action, not a tool name
- [ ] Decide deliberately between a **scope ladder** (Claude) and **mode-only trust** (Paseo, Aside); if
      you ship a ladder, offer an undo for every standing grant
- [ ] Make the approval request **data** so any channel — card, CLI, another agent, a phone — can answer it
- [ ] Never bind the reflex key (bare Enter) to approve
- [ ] Put the sandbox state **in the mode label**
- [ ] Use amber/orange for "needs you", and keep *working* in a hue that cannot be confused with it
- [ ] Render tool calls as progressive → past-tense counted sentences; let the user pick the density
- [ ] Treat the plan as an editable document and the diff comment as a prompt
- [ ] Name completion for the human's next action ("Ready for review")
- [ ] If you wrap other agents, **do not default their approvals off** — or say so on the first screen

## 9. Open questions

- How any of this looks: card weight, pulse rates, halo appearance ⚠️ (no display)
- Whether the reviewer-agent rung measurably reduces prompts without raising risk — vendors report
  numbers (Cursor: ~4% blocked) that were not verified 📣
- Whether Paseo's "message denies the pending prompt" rule surprises users who meant to approve and comment
