# Agent clients — UX/UI research notes

How ten agent tools **render harness primitives to a person** — approval, autonomy, plans, transcripts,
diffs, parallel work, attention — and the **design language** they share. Read from shipped installers
and source (tokens, fonts, icon sets, UI strings) and official documentation, not from reviews.

Researched 2026-09-26 · scope recorded in [`PURPOSE.md` §0.2](../ai-workflow/memory/active/PURPOSE.md)

> **The client side of the contract this repository studied from the engine side.** Codex
> ([`docs/`](../docs/)), browser agents ([`browser-agents/`](../browser-agents/README.md)) and Strands
> ([`strands/`](../strands/README.md)) described what a harness *does*; this study describes how people
> are shown it. Cross-study synthesis: [`SYNTHESIS.md`](../SYNTHESIS.md) §2.8.
>
> ⚠️ **No display was available.** Every value here was extracted; nothing was seen rendered.

## Documents

| Document | Contents |
|---|---|
| [01-landscape.md](01-landscape.md) | Three families (first-party apps · agent-first editors · orchestrators), build inventory, **lineage**: ChatGPT = Codex app; Antigravity and Windsurf share an engine |
| [02-claude-desktop.md](02-claude-desktop.md) | CDS design system, the `Allow Claude to …?` template and its scope ladder, the React-free consent window, Window Halo |
| [03-openai-codex-chatgpt.md](03-openai-codex-chatgpt.md) | One app, two personas; VS Code theme keys as the token API; "Approve for me" reviewer agent; Pets and the Codex Micro keypad |
| [04-cursor.md](04-cursor.md) | The "Glass" Agents Window beside the IDE; four run modes with the sandbox in the label; Keep/Undo; five transcript densities |
| [05-antigravity-windsurf.md](05-antigravity-windsurf.md) | One ancestor (Codeium), two opposite answers — "there is no IDE" vs "a full IDE with an agent manager built in" |
| [06-orca-superset.md](06-orca-superset.md) | Orchestrators wrapping other vendors' TUIs: observe · drive by keystroke · replace with the vendor API |
| [07-paseo-conductor.md](07-paseo-conductor.md) | Approval as a request object with four renderers; message-while-pending denies; Conductor's worktree-first cockpit |
| [08-primitives-rendered.md](08-primitives-rendered.md) | **Cross-product matrix by primitive** |
| [09-design-language.md](09-design-language.md) | **The answer**: the shared design language and where the philosophies part |
| [99-sources.md](99-sources.md) | Builds and hashes, grades, refutation ledger, leads for other studies |

## In one line

> The styles converged — quiet chrome with colour spent on state, a sidebar of agents around a
> conversation spine, "Allow … to …?", Queue/Steer, amber for "needs you", a machine reviewer in the
> middle of the autonomy dial. **The theories of supervision did not**: watch steps, review deliverables,
> or direct a board — and that choice, not any token, decides the layout.

## Where to start

1. For the answer: [09](09-design-language.md), then [08](08-primitives-rendered.md).
2. For one product: its document, 02–07.
3. For the security-relevant findings: [08](08-primitives-rendered.md) §1–2 — three orchestrators launch
   wrapped agents with approvals off.
