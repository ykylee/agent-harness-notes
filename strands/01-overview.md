# 01. Strands — what it is, where it came from, how to read its artifacts

> The third case in this repository, and the first that is **a library you embed** rather than a
> product you run. Read out of the `strands-agents/harness-sdk` monorepo at `15da9dc`
> (2026-09-25; Python SDK 1.57.1, TypeScript SDK 1.19.0, harness 0.1.x), its `team/` governance
> and design documents, its documentation source (`site/`), and the live `strandsagents.com/llms.txt`.
> Researched 2026-09-26.
>
> Grade: mostly ✅ **confirmed from source.** Design-document status is graded against code, not
> taken from the document (§5).

## 1. The name now means two things

"Strands" was an agent SDK. Since 2026-09-22 it is also **a product literally called a harness.**

| Layer | Package | What it is | Version |
|---|---|---|---|
| **SDK** ("Strands Agents", increasingly "Strands Harness SDK") | `strands-agents` (PyPI) · `@strands-agents/sdk` (npm) | the agent loop, model providers, tools, hooks, interventions, sessions, multi-agent | 1.57.1 · 1.19.0 |
| **Strands harness** | `strands-harness` · `@strands-agents/harness` | `create_harness()` — a factory returning a plain SDK `Agent` with defaults wired in | **0.1.x** |
| **CLI** | `@strands-agents/cli` | a TS/Ink terminal app that runs the harness in-process | pins harness `~0.1.1` |
| Docs MCP server | `strands-mcp` | `search_docs` / `fetch_doc` over the docs site — **not** the agent served over MCP ([06](06-multi-agent-and-exposure.md)) | `mcp/v0.3.0` |

The README's own positioning is exact and worth quoting, because it names the comparison this
repository cares about:

> "Choose Strands when you would otherwise write your own agent loop: it runs in your process with
> **no hosted control plane**" — `README.md` (monorepo root)

> 📌 **This is the contrast the repository was missing.** Codex is a harness you *talk to* (a binary
> behind JSON-RPC, or a managed API). Aside is a harness you *use* (a browser). Strands is a harness
> you *link against*: there is no wire between caller and loop at all. Every axis that Codex expresses
> as a protocol message, Strands expresses as a Python/TS call — and §2 of [02](02-agent-loop.md),
> [03](03-tools-and-approval.md) shows what that costs.

## 2. Where it came from — a renamed repository, not a new one

| When | Event | Grade |
|---|---|---|
| 2025-05-16 | Python SDK v0.1.0 | ✅ `site/src/content/changelog/sdk/python-v0.1.0.md` |
| 2025-07-15 | Python v1.0.0 | ✅ |
| 2025-12-03 | TypeScript SDK v0.1.0 | ✅ |
| 2026-05-05 | Design `0009-mono-repository.md` (Status: Proposed — never updated) | ✅ |
| ≤ 2026-06-01 | docs and sdk-typescript merged in (#2339, #2350; released in python v1.42.0) | ✅ |
| 2026-06-02 | `strands-agents/docs` and `strands-agents/sdk-typescript` archived with notices | ✅ |
| ≤ 2026-06-12 | references renamed `sdk-python` → `harness-sdk` (#2618, #2701) | ✅ |
| 2026-07-27 | `mcp-server` merged and archived | ✅ |
| **2026-09-22** | **"merge in the Strands harness" (#4447)**, released with python v1.57.0 / TS v1.19.0 | ✅ |
| 2026-09-23 | harness versioning policy (0.x: patch = features, minor = breaking) | ✅ |

- The old `sdk-python` repository **became** the monorepo: Python tags back to `v0.1.0` resolve under
  `harness-sdk`, and `git clone …/sdk-python` still lands there. ✅ (inferred from artifacts)
- The harness arrived by merge from somewhere not visible in a shallow clone ⚠️. At HEAD it was
  **three days old.** Everything in [04](04-harness-and-cli.md) is a snapshot of a 0.x product in its
  first week.
- `samples`, `tools` and `agent-builder` stayed separate. Design 0009 expected `samples` to move;
  it did not ❌ (a plan, not a claim — recorded for completeness).

## 3. The layer map, read against this repository's axes

| Axis ([`harness`](../ai-workflow/wiki/concepts/harness.md)) | Strands SDK | Strands harness adds | Detail |
|---|---|---|---|
| Loop | recursive (Py) / iterative (TS) cycle, **no default bound** | context "auto" preset, background tasks | [02](02-agent-loop.md) |
| Conversation state | client-side list replayed each call; opt-in server state via Responses | snapshot sessions, long-term memory | [02](02-agent-loop.md) |
| Wire to the model | **Bedrock Converse shape internally**; providers convert | `"provider/model"` string table | [05](05-providers-and-telemetry.md) |
| Tools | `@tool`, registry, MCP client, concurrent executor | shell, read/write/edit, web, code-mode, subagent | [03](03-tools-and-approval.md), [04](04-harness-and-cli.md) |
| Approval | **interrupts** (exception + re-entry), interventions, Cedar | `interventions=` string grammar — **default off** | [03](03-tools-and-approval.md) |
| Execution environment | `Sandbox` = host / Docker / SSH — **default host, "no isolation"** | routes every built-in through it | [04](04-harness-and-cli.md) |
| Multi-agent | Graph, Swarm, agents-as-tools, in one process | generalist subagent | [06](06-multi-agent-and-exposure.md) |
| Exposure | A2A server, ACP (via CLI) | — | [06](06-multi-agent-and-exposure.md) |
| Observability | OTel spans, `gen_ai.*` names | off unless an exporter is set | [05](05-providers-and-telemetry.md) |

## 4. Governance — what the project promises about itself

### 4.1 Tenets and the "model-driven" tagline

`team/TENETS.md:5-10` lists six tenets: simple at any scale; extensible by design; composability;
obvious path is the happy path; **accessible to humans and agents**; embrace common standards (MCP,
A2A, ACP, OTel).

**"Model-driven" — the README's headline — is not among them.** 📣 It is a tagline (`README.md:16`,
the AGENTS.md files, one blog post). In code the phrase appears exactly once, as the description of
the `"agentic"` context-manager preset ("Model-driven context management via injected tools",
`strands-py/src/strands/_context_manager/context_manager.py:36-42`). ✅

`team/DECISIONS.md` is the more useful document — dated, short, and binding. Two entries matter to a
harness builder:

- **2026-01-28 — pay-for-play breaking changes are allowed in minors** when opt-in.
- **2026-04-23 — LLM-native units: tokens, not characters.**

### 4.2 Stability, and one tension the harness introduces

| Surface | Rule | Source |
|---|---|---|
| SDK | semver; majors supported ≥ 6 months after the next; **`strands.experimental` is outside semver** | `team/FEATURE_LIFECYCLE.md:19-27,66,82` ✅ |
| Harness / CLI | 0.x: **patch = fixes and features, minor = breaking**; prompt text and tool descriptions are not breaking | `site/…/harness/versioning.mdx` ✅ |

> ⚠️ **The harness depends on an experimental SDK API in its default path** —
> `strands.experimental.context_manager.ContextManager` (`harness-py/src/strands_harness/agent.py:13`)
> — while declaring `strands-agents>=1.56.0,<2.0.0` (`harness-py/pyproject.toml:33`). By the SDK's own
> policy any minor inside that range may legally break it. Not a bug today; a latent one.

### 4.3 AI in the project itself

`team/AI_USAGE_POLICY.md` and `team/AGENT_GUIDELINES.md` govern agents that work *on* the repository:
disclosure, never the sole approver, **never give agents maintainer tokens**, a named human owner,
anyone may "pull the cord." 📣 (policy). In practice a disclosed bot account authored 6 of the 50
commits in the shallow window, including the harness versioning policy. ✅

## 5. Design documents are not status reports

`team/designs/` holds 20 files. Their `Status:` lines were checked against code:

| Status line says | Count | Reality |
|---|---|---|
| Proposed | 13 | **11 implemented in full or in part** — including 0009 (the monorepo it proposed now exists), 0004 (stateful models), 0008, 0014 (storage), 0016 (routing), 0017 (file memory), 0018 |
| — | — | Not implemented: 0012/0013 (Strandslator), 0015a (WebRTC transport). 0005 (state machine) exists only as its middleware layer |
| Accepted | 2 | while `team/designs/README.md:129` says "**No designs have been accepted yet.**" ❌ |

Three numbers (0009, 0011, 0015) are used twice; 0002 is missing. And the implementations
**deviate from the designs** in ways that matter — stateful models clear history *after* an invocation
rather than before and raise instead of warn ([02](02-agent-loop.md)); Cedar shipped as an intervention
handler with a fixed resource rather than the designed plugin ([03](03-tools-and-approval.md)); the
intervention precedence order the design promises is not in the code ([03](03-tools-and-approval.md)).

> 📌 **Read the code, not the status line.** This is the same lesson as Codex's generated schemas vs.
> its prose ([`primary-source-verification`](../ai-workflow/wiki/concepts/primary-source-verification.md)),
> in a sharper form: here the stale artifact is *committed alongside the code*, so it looks
> authoritative.

## 6. The documentation site — `llms.txt` works, `.md` needs `index.md`

| Probe (2026-09-26) | Result |
|---|---|
| `strandsagents.com/llms.txt` | ✅ 200, `text/plain`, 137 KB, 537 entries — generated from the sidebar (`site/src/pages/llms.txt.ts`) |
| `…/docs/user-guide/harness/index.md` | ✅ 200, `text/markdown` |
| `…/docs/user-guide/harness.md` | ❌ **404** |

The route is `site/src/pages/[...slug]/index.md.ts`: raw Markdown lives at **`<page>/index.md`**, not
`<page>.md`. `/llms-full.txt` is also generated, and `robots.txt` explicitly admits AI crawlers.

> 📌 **A third variant of the technique.** Aside and Opera: `.md` suffix works. Dia: nothing works
> (SPA shell). Strands: `llms.txt` works and its links already point at `index.md` — but a guessed
> `<page>.md` 404s. **Follow the links `llms.txt` gives you rather than constructing URLs.**

## 7. What this means if you are building a harness

- [ ] Decide whether callers **link** your loop or **talk** to it. Strands chose linking — and
      every later document shows approval, streaming and state losing their wire shape as a result
- [ ] If you ship a batteries-included layer over an SDK, do not let its default path import APIs
      the SDK excludes from semver
- [ ] Keep design-doc status machine-checked, or drop the field — a stale `Proposed` is worse than none
- [ ] Publish `llms.txt` with **absolute links to the raw form** so agents never guess a URL scheme

## 8. Open questions

- Where the harness lived before #4447 (a shallow clone cannot see it) ⚠️
- Whether the `strands-labs/benchmark-harnesses` repository reproduces the published charts — not
  fetched; see [99](99-sources.md) §4 for what the committed chart data does and does not show
