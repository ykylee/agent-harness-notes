# Codex Harness — Study Notes

Notes on OpenAI's **Codex harness** (the execution engine behind the Codex agent) and the API
surfaces built on top of it, compiled from primary sources: official blog posts, official docs,
and the generated schemas in the [`openai/codex`](https://github.com/openai/codex) repository.

Research date: 2026-09-14 (Agents API deep dive: 2026-09-15)
Repository: <https://github.com/ykylee/agent-harness-notes>

## Start with the report

**[REPORT.md](REPORT.md)** — the findings, the requirement assessment, the verification record, and
the recommendations they support. Also published as a [web version](https://claude.ai/artifact/6J9zrjCvZQcfDXcKvgUsxo).

## In one line

> A "harness" is the **execution system** that sits between a model and a task. OpenAI opened
> this execution system in three layers: (1) an open-source binary and protocol (App Server),
> (2) per-language SDKs, and (3) a managed API (Agents API).

## Release timeline

| Date | What | Significance |
|---|---|---|
| 2026-02-04 | [Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/) (Celia Chen) | App Server architecture and protocol design published |
| 2026-02-11 | [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (Ryan Lopopolo) | Introduces "harness engineering" as a discipline |
| 2026-08-19 | [Codex as a platform: build on the open agent harness](https://developers.openai.com/blog/codex-as-a-platform) | CLI · app-server · SDK officially positioned as an **open agent harness** (Apache-2.0) |
| 2026-09-10 | [Agents API public beta](https://developers.openai.com/api/docs/guides/agents-api/overview) | The same harness offered as a managed API **hosted by OpenAI** |

## Contents

| Document | Topic |
|---|---|
| [01-overview.md](docs/01-overview.md) | What a harness is, its internal components, the 3-layer open structure |
| [02-app-server-protocol.md](docs/02-app-server-protocol.md) | **Core.** The full App Server JSON-RPC protocol — transports, handshake, 104 methods, 84 notifications, approval flow |
| [03-sdk.md](docs/03-sdk.md) | TypeScript / Python SDKs |
| [04-cli-exec.md](docs/04-cli-exec.md) | `codex exec` non-interactive mode |
| [05-agents-api.md](docs/05-agents-api.md) | Managed Agents API concepts (sessions / sandboxes / subagents) |
| [08-agents-api-reference.md](docs/08-agents-api-reference.md) | **Agents API reference** — 33 endpoints, schemas, and 30 event types extracted from the OpenAPI spec |
| [09-agents-api-environments.md](docs/09-agents-api-environments.md) | Agents API architecture, the three environment types, hosted sandbox config, files/artifacts, lifecycle, security |
| [10-agents-api-tools.md](docs/10-agents-api-tools.md) | Agents API tools — function tools, MCP connections, vaults, plugins |
| [11-agents-api-operations.md](docs/11-agents-api-operations.md) | Agents API webhooks, observability, tracing, and the cost model |
| [06-choosing.md](docs/06-choosing.md) | Comparison of the integration paths and how to choose |
| [07-harness-engineering.md](docs/07-harness-engineering.md) | Operating principles from OpenAI's internal "zero hand-written code" experiment |
| [12-product-surface.md](docs/12-product-surface.md) | All 104 protocol methods re-read as a build checklist for a product-grade harness |
| [13-marketplace-and-plugins.md](docs/13-marketplace-and-plugins.md) | Marketplace catalog format, plugin manifest and distribution sources |
| [14-windows-sandbox.md](docs/14-windows-sandbox.md) | Native Windows sandbox — elevated/unelevated modes, mechanisms, policy |
| [15-model-providers.md](docs/15-model-providers.md) | Provider configuration, and why Chat Completions support was removed |
| [16-responses-chat-adapter.md](docs/16-responses-chat-adapter.md) | **Feasibility study** — mapping Codex's real Responses payload onto Chat Completions |
| [99-sources.md](docs/99-sources.md) | Source list and verification status |

## Start here

```bash
# 1. Install the Codex CLI
curl -fsSL https://chatgpt.com/codex/install.sh | sh

# 2. Generate the app-server protocol types yourself
codex app-server generate-ts            # TypeScript definitions
codex app-server generate-json-schema   # JSON Schema bundle

# 3. Watch the full JSON traffic of a single turn
codex debug app-server send-message-v2 "run tests and summarize failures"
```

## License

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

The **notes and original writing** in this repository are licensed under
[Creative Commons Attribution 4.0 International](LICENSE) (CC BY 4.0).
You may share, adapt, and use them commercially, as long as you give attribution.

> © 2026 ykylee · <https://github.com/ykylee/agent-harness-notes> · CC BY 4.0

The documents also contain **attributed quotations and code samples**, which carry their own terms:

| Material | Terms |
|---|---|
| Notes, summaries, tables, and commentary in this repository | **CC BY 4.0** (this repository) |
| Code and schemas quoted from [`openai/codex`](https://github.com/openai/codex) | Apache-2.0 (OpenAI) |
| Spec content extracted from [`openai/openai-openapi`](https://github.com/openai/openai-openapi) | That repository's license (OpenAI) |
| Passages quoted from OpenAI blog posts and official docs | © OpenAI. Included for quotation, with attribution |

This is an independent personal study repository, not affiliated with OpenAI, and it does not
replace the official documentation. Always check the [original sources](docs/99-sources.md)
for authoritative details.
