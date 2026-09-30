# 99. Sources and verification record

> Applies this repository's [method of knowing](../ai-workflow/wiki/concepts/primary-source-verification.md)
> unchanged: **committed artifacts over prose**, no secondary source settled before cross-checking,
> inference labelled as inference, refutations kept rather than deleted. Researched 2026-09-26.
> Drift re-check: 2026-09-30 against HEAD `a9a62d4e` — see [§6](#6-drift-re-check-2026-09-30).

## 1. Grade vocabulary

| Grade | Meaning |
|---|---|
| ✅ **confirmed** | read directly in source at the pinned commit |
| 🧪 **probed** | ran against the SDK's own scripted `MockedModelProvider` (no LLM, deterministic), **with a control that proves the input arrived** |
| 📐 **designed-only** | stated in a `team/designs/` document; no implementing code found |
| 📣 **self-reported** | a README, blog or docs claim — including benchmark numbers — not independently verified |
| ⚠️ **inferred / unverified** | follows from source but was not exercised, or was not reached |
| ❌ **refuted** | a documentation, design or docstring claim contradicted by code or by the claim's own data |

> 📌 **New in this study: 📐.** Strands commits its design documents next to the code, and their
> `Status:` lines are unreliable ([01](01-overview.md) §5). A design is therefore graded as its own
> kind of evidence — intent — and never as evidence of behaviour.

## 2. Primary sources

### 2.1 Repositories (pinned)

| Repository | Commit | Date | Notes |
|---|---|---|---|
| **`strands-agents/harness-sdk`** | **`15da9dc`** | 2026-09-25 | the study pin; `git clone …/sdk-python` lands here (renamed). Original read was a shallow clone, depth 50 |
| same, recheck | **`a9a62d4e`** | 2026-09-29 | 31 commits past the pin. Local checkout `~/repos/harness-refs/strands-harness-sdk`, origin `https://github.com/strands-agents/sdk-python.git` (`blob:none`, full history). No new SDK/harness tags |
| `strands-agents/tools` | `8c82c29` | 2026-09-21 | community tool package; consent prompts |
| `strands-agents/samples` | `11dd549` | 2026-09-21 | still separate |
| `strands-agents/agent-builder` | `136b6f9` | 2026-05-12 | not analysed beyond existence |
| `strands-agents/docs` · `sdk-typescript` · `mcp-server` | — | archived 2026-06-02 / 2026-06-02 / 2026-07-27 | archive notices read |
| **`agentclientprotocol/agent-client-protocol`** | **`9b26a3ea`** | 2026-09-30 | ACP spec + `schema/v1/schema.json`. Local `~/repos/harness-refs/agent-client-protocol`. Engine-side notes in [`agent-ux/10`](../agent-ux/10-acp.md) |
| `@agentclientprotocol/sdk` **1.3.0** | tag `v1.3.0` / git `fa325709` | 2026-07-21 | Strands CLI pin. `PROTOCOL_VERSION = 1`; wire method `session/request_permission` |

Inside the monorepo:

| Path | Read for |
|---|---|
| `strands-py/src/strands/` (~69k lines) | the loop, types, tools, hooks, interventions, sandbox, models, telemetry, multi-agent |
| `strands-ts/src/` (~52k lines) | parity checks — partly through a delegated read, spot-checked (see §5) |
| `harness-py/`, `harness-ts/` | `create_harness()` defaults, prompt, tools, plugins |
| `strands-cli/` | the TS/Ink CLI: permissions, workspace sandbox, credentials, ACP |
| `strands-mcp/` | the documentation MCP server |
| `team/` | `TENETS.md`, `DECISIONS.md`, `FEATURE_LIFECYCLE.md`, `COMPATIBILITY.md`, `AI_USAGE_POLICY.md`, `AGENT_GUIDELINES.md`, **20 design documents** |
| `site/` | documentation source (MDX), changelog pages, blog, chart embeds, `llms.txt` generator |

### 2.2 Documentation site — live

| Probe (2026-09-26) | Result |
|---|---|
| `https://strandsagents.com/llms.txt` | ✅ 200, 137,208 bytes, 537 entries |
| `…/docs/user-guide/harness/index.md` | ✅ 200 `text/markdown` |
| `…/docs/user-guide/harness.md` | ❌ 404 |

> 📌 Technique record, updated: OpenAI ✅ · Aside ✅ · Opera ✅ · Dia ❌ · **Strands ✅ with a
> variant** — `llms.txt` works and its links point at `<page>/index.md`; a constructed `<page>.md`
> 404s. **Use the links `llms.txt` gives; do not construct URLs.**

## 3. Probes

Two scripts, run first by a research agent and then **re-run independently by the main session in a
fresh virtualenv** (`pip install -e strands-py[cedar]`). Both use `tests/fixtures/mocked_model_provider.py`
from the repository — no model, no network, one deterministic run each.

| # | Probe | Result | Control |
|---|---|---|---|
| P1 | Cedar `call_count` across a `HumanInTheLoop` interrupt/resume | count **2**, tool ran **1** time | — (the count is the observation) |
| P2 | `permit` + `forbid … when { context.session.role != "admin" }`, no context enricher | tool **ran** | same policy with `role="user"` supplied → tool **blocked** |
| P3 | `HumanInTheLoop(enable_trust=True)`, answer `"t"` | trust stored in `agent.state["hitl:trusted_tools"]` — survives session restore | — |
| P4 | steering `Interrupt`, response `"no"` | tool **ran** | response `False` → tool **blocked**; interrupt fired (`stop_reason="interrupt"`) |
| P5 | steering handler raises | tool **ran** | (P4 control shows the handler path is reached) |

> ⚠️ The steering control (P4 `False`) was **added by the main session** — the original script had
> none. Without it, "`no` passes" could not be told apart from "the interrupt never fired." This is
> the discipline recorded in [`SYNTHESIS.md` §7](../SYNTHESIS.md#7-on-method): a pass is evidence
> only if the input provably arrived.

No probe touched a live model. **Every injection path in [07](07-security.md) §2 remains ⚠️.**

## 4. Refutation ledger

Claims are quoted from the source named; the contradicting code is cited in the linked document.

### 4.1 Security and approval

| # | Claim | Where | Reality | Doc |
|---|---|---|---|---|
| R1 | "Cedar engine failures (malformed policies, evaluation errors) are always **fail-closed**" | `site/…/cedar-authorization.mdx:239` | an erroring `forbid` is skipped → **allowed** | [03](03-tools-and-approval.md), [07](07-security.md) §3.2 · 🧪 |
| R2 | `call_count` tracks "how many times each tool has been invoked successfully" | `cedar-authorization.mdx:75` | incremented on Cedar allow; **doubles** across interrupt/resume | [03](03-tools-and-approval.md) · 🧪 |
| R3 | "well-defined precedence (deny > confirm > guide > transform > proceed)" | `site/…/interventions/index.mdx:204`; design 0007 | **registration order**, first short-circuit wins | [03](03-tools-and-approval.md) |
| R4 | "unified audit trail … `agent.interventions.auditLog`" | design 0007 | exists in neither SDK; the TS test for it asserts nothing | [03](03-tools-and-approval.md) |
| R5 | "if principal identity cannot be resolved, all tool calls are denied" | `cedar-authorization.mdx:25` | only with a `principal_resolver`; otherwise `User::"anonymous"` | [03](03-tools-and-approval.md) · partial |
| R6 | file tools "cannot walk outside the intended location" | `site/…/shell-and-files.mdx:39-40` | there is no intended location; any absolute path is accepted | [04](04-harness-and-cli.md) · misleading, not literally false |
| R7 | the generalist subagent "starts from a blank conversation" | `site/…/subagents.mdx:61-63`; the tool's own description | the model may choose `context="all"` and fork full history | [04](04-harness-and-cli.md) |

### 4.2 Claims about performance

| # | Claim | Where | Reality | Doc |
|---|---|---|---|---|
| R8 | "28% lower cost **with equal or better accuracy** across benchmarks" | chart embed, launch blog | the chart's own data: lower in **7 of 19** same-model pairs (−0.05 … −2.41); no variance; 28% depends on including a harness that "scores lower on every benchmark" | [04](04-harness-and-cli.md) · recomputed by the main session |

> ⚠️ R8 refutes a **wording**, not a ranking. Sub-point gaps without variance support neither
> "better" nor "worse." The benchmark code lives in `strands-labs/benchmark-harnesses`, not fetched.

### 4.3 Loop, wire, providers, telemetry

| # | Claim | Where | Reality | Doc |
|---|---|---|---|---|
| R9 | Python redacted-reasoning stream field is `redactedContent` | `site/…/streaming/events.mdx:63` | code emits `reasoningRedactedContent` | [02](02-agent-loop.md) |
| R10 | stateful models clear history **at the start** of an invocation; a conversation manager triggers a **warning** | design 0004 | cleared **after**; `ValueError` | [02](02-agent-loop.md), [05](05-providers-and-telemetry.md) |
| R11 | Llama API supports structured output (✓ in the provider table) | `site/…/model-providers/index.mdx` | `raise NotImplementedError` | [05](05-providers-and-telemetry.md) |
| R12 | cache-token span attributes "default to 0" | `site/…/traces.mdx` | omitted when absent | [05](05-providers-and-telemetry.md) |
| R13 | setting `OTEL_EXPORTER_OTLP_ENDPOINT` sends traces | `Tracer` docstring | the `Tracer` installs no exporter; `StrandsTelemetry` does | [05](05-providers-and-telemetry.md) |
| R14 | the router owns fallback; string candidates allowed | design 0016 | the strategy owns fallback; no `str` | [05](05-providers-and-telemetry.md) |
| R15 | harness Anthropic web search stays off until a later SDK | harness docstrings (Py, TS) | Py table already sets it; TS already requires that SDK | [05](05-providers-and-telemetry.md) |

### 4.4 Multi-agent and project records

| # | Claim | Where | Reality | Doc |
|---|---|---|---|---|
| R16 | Swarm `max_handoffs` and `max_iterations` are distinct limits | `site/…/swarm.mdx:116-117` | both check `len(node_history)` | [06](06-multi-agent-and-exposure.md) |
| R17 | subagent implements "design 0017-subagents" | `harness-py/…/tools/subagent.py:1` | 0017 is the file-memory-store design | [06](06-multi-agent-and-exposure.md) |
| R18 | deploy examples: one module-level `Agent` serving all requests | Docker/FastAPI, AgentCore guides | the SDK's A2A server calls this "not multi-tenant safe"; overlapping calls raise `ConcurrencyException` | [06](06-multi-agent-and-exposure.md) |
| R19 | "No designs have been accepted yet" | `team/designs/README.md:129` (at the pin) | two designs declare Accepted. **Drift 2026-09-30:** the README sentence was deleted in #4696; 0009-context-offloader and 0010 still say Accepted. The false sentence is gone; the status-line lesson stands | [01](01-overview.md) §5 |
| R20 | 13 designs marked "Proposed" | `team/designs/*` | **11** implemented in full or part | [01](01-overview.md) §5 |

> 📌 **Where the refutations cluster.** Of the twenty, the ones with consequences are in approval
> (R1–R5) — the layer where a wrong document leads someone to believe they are protected. Most of the
> rest are drift between a fast-moving codebase and prose written beside it. The benchmark wording
> (R8) is the only marketing claim; the others are engineering documents disagreeing with engineering
> code.

## 5. What was not verified

| Item | Why | Grade |
|---|---|---|
| TypeScript details beyond spot checks (loop, stop reasons, reasoning types and stateful clearing were checked) | event union and `modelState` write-back re-read at `a9a62d4e` ([02](02-agent-loop.md) §3.2, §4.2). Remaining TS surface still ⚠️ where marked | ✅ those two · ⚠️ rest |
| Stateful Responses mode resending the invocation's items alongside `previous_response_id` inside a tool loop | formatter confirmed: full `input` + `previous_response_id`, no slice ([02](02-agent-loop.md) §4.2). API outcome not captured. TS live integ exists, body unasserted | ✅ formatter · ⚠️ API |
| Native Anthropic provider on a redacted-only thinking block (`KeyError` suspected) | not run | ⚠️ |
| Snapshot portability between the Python and TS SDKs | message key names differ; not run | ⚠️ |
| The harness ACP path not forwarding permission requests to the client | source: no `session/request_permission` in `server.ts:102-147`; spec method confirmed hyphenated. Not run against an ACP client | ✅ source absence · ⚠️ runtime |
| Anything a live model would do with the injection paths in [07](07-security.md) §2 | no model was used | ⚠️ |
| The benchmark repository `strands-labs/benchmark-harnesses` | not fetched | 📣 |
| The Evals SDK (`strands-agents/evals`) | separate repository, not inspected | — |
| Where the harness lived before PR #4447 | squash-merged as `4095cf5a` (2026-09-21), single parent; the prior tree is not in this history | ⚠️ |

## 6. Drift re-check 2026-09-30

Range: `15da9dc` (2026-09-25, `python/v1.57.1`) → HEAD `a9a62d4e` (2026-09-29 19:26:59 −0400,
`refactor(bidi): make tool execution internals private (#4708)`). **31 commits.** Local checkout
`~/repos/harness-refs/strands-harness-sdk`, origin `https://github.com/strands-agents/sdk-python.git`
(`blob:none`). `git describe` `harness-cli/v0.1.4-35-ga9a62d4e`.

No new version tags. Still Python SDK **1.57.1**, TypeScript SDK **1.19.0**, harness **0.1.x**
(`harness-python/v0.1.2`, `harness-typescript/v0.1.1`, CLI pin `~0.1.1`). The `cedar` extra bumped
`cedar-policy-mcp-schema-generator` 0.6.0 → 0.6.1 (#4650); evaluation code is untouched.

Probes P1–P5 were **not re-run**. `git diff 15da9dc..HEAD` is empty on
`strands-py/src/strands/vended_interventions/cedar/`, `strands-py/src/strands/interventions/`,
`strands-py/src/strands/sandbox/`, `harness-py/src/strands_harness/defaults.py`,
`harness-py/src/strands_harness/interventions.py`. The three claims this re-check was for:

| Claim | At HEAD | Grade |
|---|---|---|
| `create_harness(..., interventions=None)` — approval **default off** | `agent.py:266`, docstring l.390 | ✅ unchanged |
| Cedar fail-open (R1): erroring `forbid` skipped → allowed; docs still say engine failures are always fail-closed (`cedar-authorization.mdx:239`) | cedar sources byte-identical | ✅ R1 stands; P2 not re-run |
| Sandbox default **host** (`None` → `NotASandboxLocalEnvironment`) | `strands-py/…/agent.py:219-352`; harness `config.py` `"sandbox": None` | ✅ unchanged |
| Intervention **registration order**, first short-circuit (R3) | `registry.py:4,200-235` | ✅ unchanged |

Harness factory files that *did* change are caching validation only (`_check_caching`, #4631):
reject anything other than `"auto"` / bool / `None`. Defaults, skills, and sandbox wiring are the
same. The latent experimental import `strands.experimental.context_manager.ContextManager`
([01](01-overview.md) §4.2) is still on the default path.

What moved, and is **not** a security-default change:

| Change | Commit |
|---|---|
| Bidirectional streaming graduated out of `experimental` (deprecated aliases remain) | #4707 |
| Context-manager keeps stashed originals across session resume | #4699 |
| OpenAIResponses skips location-source documents when formatting | #4706 |
| Context-window numbers for Sonnet 5.5, Opus 5.5, Fable 5.1 | #4694 |
| Bedrock normalizes tool inputs before replay | #4625 |
| `FileStorage.store` returns a portable filename, not a host path | #4568 |
| Harness docs default model `opus-4-8` → `opus-5` (code at the pin was already opus-5) | #4661 |
| TS vended `a2a-client` | #4575 |
| Design README drops "No designs have been accepted yet" and the Status line from the template (R19) | #4696 |

R1–R18 and R20 are unchanged. R19's contradicting README sentence is gone; the two Accepted
designs remain. §5 items other than #4447's arrival shape are still unverified — including the
TypeScript details this study delegated.
