# Browser-type agent tools — research notes

Centred on **Aside**, an investigation into agent tools that use the browser as their control
surface. Read along the axes of features, composition, structure, design and UI/UX — and read from
**documentation, source and reverse-engineering records** rather than marketing copy.

Researched 2026-09-22/23 · branch `study/browser-agents`

> **Another instance of the same abstraction as this repository's other study** (`docs/`, the Codex
> harness). The cross-study synthesis is **[`SYNTHESIS.md`](../SYNTHESIS.md)**; the concept-level
> re-index is [`ai-workflow/wiki/`](../ai-workflow/wiki/index.md).
> Scope history is in [SCOPE.md](SCOPE.md) (resolved 2026-09-23 by extending the shared PURPOSE).

## Documents

| Document | Contents |
|---|---|
| [01-landscape.md](01-landscape.md) | The field — a three-way taxonomy, a 2026 timeline, and what **Atlas's retirement** changed |
| [02-aside.md](02-aside.md) | **Aside in depth** — features, composition, structure, permission model, Vault, memory, CLI/MCP |
| [03-aside-design-ux.md](03-aside-design-ux.md) | **Aside design and UI/UX** — four entry points, shortcuts, split tabs, lasso, approval flow |
| [04-comet-architecture.md](04-comet-architecture.md) | Perplexity Comet's architecture — the three extensions, RPC and perception model revealed by reverse engineering |
| [05-comparables.md](05-comparables.md) | Atlas (retired) · Dia · Opera Neon · Claude for Chrome · Gemini in Chrome · Browser Use |
| [06-architecture-axes.md](06-architecture-axes.md) | **Cross-cutting** — control surface / perception / planning location / credentials |
| [07-security.md](07-security.md) | Indirect prompt injection — the attack chain, its structural cause, mitigations, unsolved status |
| [08-aside-code-level.md](08-aside-code-level.md) | **Aside at code level** — perception model, memory format, remote control and built-in skills, extracted from the binary |
| [09-aside-browser-internals.md](09-aside-browser-internals.md) | **Aside browser internals** — a Chromium fork, three internal extensions, a 353MB local daemon, Vault cryptography |
| [10-aside-enforcement-and-native.md](10-aside-enforcement-and-native.md) | **Enforcement, Computer Use, cryptography** — the policy engine, system-wide OS control, ML-KEM-768 confirmed |
| [11-dia-and-neon.md](11-dia-and-neon.md) | **Dia and Neon from primary sources** — Dia's injection defences, Neon's planning-location contradiction, Cards |
| [99-sources.md](99-sources.md) | Sources and **evidence grades** — confirmed / self-reported / inferred / refuted |

## In one line

> The competitive axis for browser-type agents is not the model but **where the control surface
> sits** — an extension (Comet), a native browser (Aside), or a library (Browser Use). That choice
> determines permissions, credentials and the security boundary entirely.

## Where to start

1. If you do not know the field, begin with [01](01-landscape.md). Atlas disappearing on 2026-08-09
   made most existing comparison articles stale.
2. If you only care about Aside: [02](02-aside.md) → [03](03-aside-design-ux.md) →
   [08](08-aside-code-level.md) → [09](09-aside-browser-internals.md) → [10](10-aside-enforcement-and-native.md).
3. For the "if I were building one" angle, [06](06-architecture-axes.md) is the core — and
   [`SYNTHESIS.md`](../SYNTHESIS.md) crosses it with the Codex study.
4. [99](99-sources.md) tells you, by grade, which claims you may believe.
