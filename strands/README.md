# Strands — research notes

**Strands Agents** (AWS, Apache-2.0) and the **Strands harness** built on it, read out of the
`strands-agents/harness-sdk` monorepo — source, governance and design documents, and the
documentation source — rather than from the launch posts.

Researched 2026-09-26 · `harness-sdk` @ `15da9dc` (2026-09-25) · Python SDK 1.57.1 · TypeScript SDK
1.19.0 · harness 0.1.x (released 2026-09-22)

> **The third case in this repository, and the first harness you link against rather than talk
> to.** Codex ([`docs/`](../docs/)) sits behind a wire; browser agents
> ([`browser-agents/`](../browser-agents/README.md)) sit behind a product. Strands runs in your process
> with no control plane. The cross-study synthesis is [`SYNTHESIS.md`](../SYNTHESIS.md); the
> concept-level re-index is [`ai-workflow/wiki/`](../ai-workflow/wiki/index.md).

## Documents

| Document | Contents |
|---|---|
| [01-overview.md](01-overview.md) | What the name covers now (SDK · harness · CLI), the rename into a monorepo, governance, **design-doc status vs. code**, the `llms.txt` / `index.md` record |
| [02-agent-loop.md](02-agent-loop.md) | The loop (recursive in Python, iterative in TS), Bedrock-Converse messages, stream events, reasoning replay, context management, sessions, stateful models |
| [03-tools-and-approval.md](03-tools-and-approval.md) | `@tool`, hooks, plugins, skills, MCP client — and **approval as exception-plus-replay**, interventions, Cedar, steering, with probes |
| [04-harness-and-cli.md](04-harness-and-cli.md) | `create_harness()` defaults, the `Sandbox` abstraction, file/web/code-mode/subagent tools, memory, the `strands` CLI, credentials, the benchmark claim |
| [05-providers-and-telemetry.md](05-providers-and-telemetry.md) | **Providers as code converting to a Bedrock-shaped wire**, OpenAI Chat vs. Responses, routing, bidi streaming, token accounting, OTel |
| [06-multi-agent-and-exposure.md](06-multi-agent-and-exposure.md) | Graph, Swarm, agents-as-tools, subagents; A2A and ACP exposure; deployment |
| [07-security.md](07-security.md) | **Synthesis**: default posture, the injection surface, which way each gate fails, credentials |
| [99-sources.md](99-sources.md) | Sources, grades, probes, and the **refutation ledger** |

## In one line

> Strands has every primitive a careful harness needs — an out-of-loop approval gate, a Cedar policy
> backend, pluggable execution environments — and **ships the harness with all of them off**: host
> execution, no gate, keys in the environment. The primitives are sound; the defaults, the error
> paths and the documentation are where it breaks.

## Where to start

1. If you want the shape of the thing: [01](01-overview.md) §1–3.
2. If you are designing approval or policy: [03](03-tools-and-approval.md) → [07](07-security.md).
   This is where the probes and most refutations are.
3. If you are comparing wire and provider design with Codex: [02](02-agent-loop.md) →
   [05](05-providers-and-telemetry.md). Strands made the opposite choice on providers.
4. [99](99-sources.md) tells you, by grade, which claims you may believe.
