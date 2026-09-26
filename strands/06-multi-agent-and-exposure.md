# 06. Multi-agent patterns, exposure to other harnesses, deployment

> Scope: the Python SDK's `multiagent/` package (Graph, Swarm, A2A), agents-as-tools, and the harness
> `subagent` tool. Also the ways a Strands agent can be driven by *another* harness (A2A, ACP,
> `strands-mcp`) and what the deployment docs actually ship. History, governance, design-doc status
> and llms.txt are covered in [01-overview.md](01-overview.md).
>
> Method: static reading of source and docs only. No probe was run.
> `strands-agents/harness-sdk` @ `15da9dc` (2026-09-25; python/v1.57.1, typescript/v1.19.0,
> harness 0.x). Sibling repo `strands-agents/tools` was read for the `workflow` tool.
> Researched 2026-09-26.
>
> Grade: mostly ✅ **confirmed (source read)**. Runtime claims are marked ⚠️.

## 1. The multi-agent set, in one table

| Primitive | Who chooses the next agent | Unit of transfer | Concurrency | Remote members |
|---|---|---|---|---|
| **Graph** (`GraphBuilder`) | Code: edges plus Python predicates | Upstream final text, concatenated | `asyncio` tasks per ready batch | ✅ any `AgentBase`, including `A2AAgent` |
| **Swarm** | The model, via an injected `handoff_to_agent` tool | Handoff message + JSON dict rendered as prose | One agent at a time | ❌ concrete `Agent` only |
| **Agents-as-tools** (`Agent.as_tool`) | The parent model (it's a tool call) | One `input` string in, text out | Whatever the tool executor does | via tool wrapping |
| **Workflow** | Not an SDK primitive. It is a docs pattern plus a tool in `strands-agents/tools` | — | Thread pool (tool) | — |
| Harness `subagent` | The parent model | Task + optional forked parent messages | Per tool call | — |

Exports: `strands-py/src/strands/multiagent/__init__.py:11-25`. TypeScript has the same set in
`strands-ts/src/multiagent/{graph,swarm}.ts` ✅ (existence only).

> 📌 **Everything runs in one process.** The site's own llms.txt blurb says "Agents run in-process with no hosted
> control plane" (`site/src/pages/llms.txt.ts:67`) 📣, and the code agrees ✅. A Graph's parallelism
> is `asyncio.create_task` feeding one `asyncio.Queue` polled every 0.1 s
> (`strands-py/src/strands/multiagent/graph.py:823-881`). A Swarm is a `while True` loop over a single
> `current_node` (`swarm.py:786-800`). The only thing that crosses a process boundary is `A2AAgent`.
> Compare Codex's split in [control-plane-execution-plane](../ai-workflow/wiki/concepts/control-plane-execution-plane.md):
> Strands multi-agent has no control plane at all. The orchestrator is a Python object in the caller's
> event loop.

## 2. Graph

### 2.1 Routing is code, "handoff" is only an event ✅

Edge conditions are plain callables, `EdgeCondition(state)` or
`EdgeConditionWithContext(state, *, invocation_state)` (`graph.py:74-110, 207-222`). No model call
decides where control goes. Between batches the orchestrator emits
`MultiAgentHandoffEvent(from_node_ids, to_node_ids)` (`graph.py:808-818`) purely for observers.

### 2.2 What the next node sees ✅

`_build_node_input` (`graph.py:1158-1242`) builds a text prompt from the upstream results.

```
Original Task: <task>

Inputs from previous nodes:

From data_processor:
  - Agent: <str(result)>
```

Only the final text of each dependency is passed, not its transcript. Nodes are reset to their
construction-time messages and state before each run (`graph.py:257-275, 985`). `reset_on_revisit`
covers cyclic graphs (`graph.py:382`).

### 2.3 Shared state and limits ✅

- `GraphState` (`graph.py:116-157`) holds the completed/failed/interrupted sets, per-node results and
  accumulated usage. It belongs to the orchestrator, not the model.
- `invocation_state` is one dict passed to every node's `stream_async` (`graph.py:1021, 1046`) and to
  context-aware edge conditions. The model never sees it.
- Limits are `max_node_executions`, `execution_timeout` and `node_timeout` (`graph.py:159-179, 395-420`).
  **All are unset by default.** A cyclic graph with no limit is bounded only by its conditions.
- Agent nodes with a session manager are rejected:
  `"Session persistence is not supported for Graph agents yet."` (`graph.py:306`). Persistence goes
  through the graph-level `set_session_manager` (`graph.py:431`) and `serialize_state` (`graph.py:1270`).

## 3. Swarm

### 3.1 Handoff is a tool the swarm injects ✅

```python
@tool
def handoff_to_agent(agent_name: str, message: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Transfer control to another agent in the swarm for specialized help.
```
(`strands-py/src/strands/multiagent/swarm.py:612-613`)

- The tool is registered into every member's `tool_registry`. A pre-existing tool with the same name
  is a `ValueError` (`swarm.py:578-606`).
- The tool only records the target. `_handle_handoff` sets `handoff_node`/`handoff_message` and merges
  `context` into `SharedContext` under the *current* node's key (`swarm.py:641-665`). The loop does the
  switch.
- Completion is implicit. The rendered prompt ends with "If you don't hand off to another agent, the
  swarm will consider the task complete." (`swarm.py:744-747`).

### 3.2 "Shared working memory" is re-prompted text 📣 → ✅

The module docstring promises "Self-organizing agent teams with shared working memory … Collective
intelligence through shared context" (`swarm.py:1-14`) 📣. Mechanically:

1. `SharedContext` is a dict of JSON-serialisable values keyed by node (`swarm.py:129-176`).
2. Before each turn the next agent's **messages are reset** to their initial snapshot
   (`swarm.py:110-127, 958`).
3. Its user turn is `"Context:\n"` + handoff message + user request + `"Previous agents who worked on
   this: a → b"` + `"Shared knowledge from previous agents:\n• {node}: {dict}"` + a roster of the other
   agents and their descriptions (`swarm.py:679-751, 947-951`).

So no agent keeps its own history across turns inside a swarm. Continuity comes only from what the
previous agent chose to write into `message` and `context`.

### 3.3 Limits, and a refutation ❌

The docs table (`site/src/content/docs/user-guide/sdk/multi-agent/swarm.mdx:116-117`) says:

> | `max_handoffs` | Maximum number of agent handoffs allowed | 20 |
> | `max_iterations` | Maximum total iterations across all agents | 20 |

In code both test the same quantity (`swarm.py:209-215`):

```python
if len(self.node_history) >= max_handoffs:
    return False, f"Max handoffs reached: {max_handoffs}"
if len(self.node_history) >= max_iterations:
    return False, f"Max iterations reached: {max_iterations}"
```

❌ The two limits are not distinct. The effective cap is `min(max_handoffs, max_iterations)` node
executions, and the entry node counts even though nothing was handed off. Hitting any limit sets
`Status.FAILED` (`swarm.py:799-800`). There is no partial-success status. Other defaults:
`execution_timeout=900`, `node_timeout=300`, and ping-pong detection off (`window=0`)
(`swarm.py:269-313`).

### 3.4 Both patterns are injection conduits ⚠️

Graph splices `str(result)` and Swarm splices model-authored `message`/`context` **verbatim into the
next agent's user turn**, with no delimiter, provenance tag or size cap (`graph.py:1234-1240`,
`swarm.py:709-736`) ✅ (code path). An `A2AAgent` node's remote output enters a Graph the same way.
This is the multi-agent form of
[indirect-prompt-injection](../ai-workflow/wiki/concepts/indirect-prompt-injection.md). One agent that
read hostile content can address every downstream agent as "the user". ⚠️ No exploit was attempted.
See [07-security.md](07-security.md).

## 4. Agents-as-tools and the harness `subagent`

### 4.1 SDK: `Agent.as_tool()` ✅

- The signature is `as_tool(*, name=None, description=None, preserve_context=False, delegate=False)`
  (`strands-py/src/strands/agent/agent.py:1091-1098`). It returns `_AgentAsTool`, which takes one
  `input` string (`agent/_agent_as_tool.py:33`).
- With `preserve_context=False` (the default), messages and state are deep-copied at wrap time and
  restored before every call (`_agent_as_tool.py:94-112, 323-337`). This is refused when the agent has
  a session manager (`_agent_as_tool.py:105-110`).
- With `delegate=True`, the tool description gets the suffix " Calling this tool will return its
  response directly to the user as the final answer. It should be the only tool called in the turn."
  (`_agent_as_tool.py:27-30`). The `AgentDelegation` plugin then enforces "only tool in the turn", exits
  the loop and promotes the sub-agent's content to the final message (`agent/_agent_delegation.py:1-9`).
  The constraint is stated to the model *and* enforced in code.
- An `Agent` placed directly in `tools=[...]` is auto-wrapped (`tools/registry.py:143-145`). Sub-agent
  events surface in the parent stream as `AgentAsToolStreamEvent` (`types/_events.py:348-362`).

### 4.2 Harness: config-derived delegation schema ✅

- `subagent` is a default built-in tool (`harness-py/src/strands_harness/defaults.py:15-24`). Each axis
  (instructions, tools, mcp_servers, model, context) takes an authority mode, `Fixed` / `Inherit` /
  `Open` / `Choice`, and that decides whether the axis becomes a model-facing parameter
  (`harness-py/src/strands_harness/tools/subagent.py:1-15`).
- The tool set chosen through `Choice` is "re-validated at call time, so a child can never gain a
  capability the parent lacked" (same docstring).
- Depth is capped by `DEFAULT_SUBAGENT_MAX_DEPTH = 2` (`defaults.py:33`), stored in agent state as
  `subagent_depth` and decremented per level (`subagent.py:462-532`).
- `last_messages` forks the parent's real content blocks and deep-copies them, because guardrail
  redaction mutates tool results in place (`subagent.py:361-407`).
- Config-declared `subagents` are just `agent.as_tool()` appended to `tools` (`harness-py/src/strands_harness/config.py:168-170`).
- ❌ Both implementations cite a design that does not exist:
  `"""Delegation tool with a config-derived model-facing schema (design 0017-subagents)."""`
  (`harness-py/src/strands_harness/tools/subagent.py:1`, `harness-ts/src/tools/subagent.ts:2`).
  `team/designs/0017-file-memory-store.md` is the only 0017. The closest real document is
  `harness-py/docs/subagent.md`.

> 📌 This is the most transferable idea in the section: **generate the delegation tool's schema from
> developer policy.** A locked-down harness exposes a three-line schema. An open one exposes model
> choice, tool choice and context depth. Capability monotonicity (a child ≤ its parent) is checked at
> call time, not trusted to the prompt. Codex's equivalent is discussed in
> [../docs/07-harness-engineering.md](../docs/07-harness-engineering.md).

### 4.3 "Workflow" ✅

The SDK has no `Workflow` class. `user-guide/sdk/multi-agent/workflow.mdx` hand-codes a sequence of
`Agent` calls (`workflow.mdx:67-75`). The `workflow` *tool* in `strands-agents/tools`
(`src/strands_tools/workflow.py`) is a `ThreadPoolExecutor` of 2–8 workers (l.107, 162-165). It
persists JSON under `~/.strands/workflows` (`STRANDS_WORKFLOW_DIR`, l.129-130) and watches that
directory with `watchdog` (l.120-121). It is still in-process, with resume based on files.

## 5. Exposing a Strands agent to other harnesses

### 5.1 Compared with the rest of this repository

[SYNTHESIS §2.6](../SYNTHESIS.md) found Codex, Aside and Opera Neon all exposing themselves "as an
execution surface for another harness". Strands does it too, but **not through MCP**:

| Product | Mechanism | Transport | Who drives |
|---|---|---|---|
| Codex | `codex mcp-server`, App Server protocol ([../docs/04-cli-exec.md](../docs/04-cli-exec.md), [../docs/02-app-server-protocol.md](../docs/02-app-server-protocol.md)) | MCP stdio; JSON-RPC | MCP client / IDE |
| Aside | `aside mcp` ([../browser-agents/02-aside.md](../browser-agents/02-aside.md)) | MCP | coding agents |
| Opera Neon | MCP server ([../browser-agents/11-dia-and-neon.md](../browser-agents/11-dia-and-neon.md)) | MCP | external AI tools |
| **Strands SDK** | `A2AServer` | A2A over HTTP (`a2a-sdk` 0.3) | another agent |
| **Strands CLI** | `strands --acp-server` | ACP, newline-delimited on stdio | an ACP client (editor) |
| **`strands-mcp`** | **documentation server, not the agent** | MCP | coding assistants reading docs |

> 📌 Strands is the first product in this repository whose "serve yourself" path is **agent-to-agent
> (A2A)** and **editor-to-agent (ACP)**, not MCP-as-a-tool. The difference matters. MCP makes the
> agent a *tool* of the caller: stateless call, text back. A2A and ACP keep a *session*: context ids,
> tasks, streaming updates, session load. The SYNTHESIS convergence claim should be restated as "expose
> an execution surface", not "expose an MCP server". ⚠️ This is a two-protocol observation from one
> product.

### 5.2 `strands-mcp` is a docs server ✅

The README headline links "MCP Server" next to the SDK (`README.md`), which reads like "the agent over
MCP". The package says otherwise: `description = "A Model Context Protocol server that provides
knowledge about building AI agents with Strands Agents"` (`strands-mcp/pyproject.toml`). It is a
`FastMCP` app with two tools, `search_docs(query, k)` and `fetch_doc(uri, section)`
(`strands-mcp/src/strands_mcp_server/server.py:25-88`). It indexes
`["https://strandsagents.com/llms.txt"]` (`strands-mcp/src/strands_mcp_server/config.py:14-16`) with
title TF-IDF, extended to page bodies once they are fetched.

The SDK has no MCP *server* mode for an agent. `mcp.server` appears in `strands-py/src` only as
instrumentation patches (`strands/tools/mcp/mcp_instrumentation.py:166-173`) ✅. MCP is consumed
(`MCPClient`), never offered.

### 5.3 A2A server and client ✅

- The dependency is `a2a-sdk>=0.3.0,<0.4.0` as the extra `strands-agents[a2a]`
  (`strands-py/pyproject.toml:71-73`). TypeScript uses `@a2a-js/sdk ^0.3.10`, exported at
  `@strands-agents/sdk/a2a` and `/a2a/express` (`strands-ts/package.json:95-101, 228`).
- `A2AServer` wraps `A2AStarletteApplication` / `A2AFastAPIApplication` plus `DefaultRequestHandler`
  and, by default, `InMemoryTaskStore`. It is served by `uvicorn` on `127.0.0.1:9000`
  (`strands-py/src/strands/multiagent/a2a/server.py:11-18, 37-42, 126-137, 325-327`).
- The AgentCard (`server.py:163-190`) requires a name and description, declares text in and text out,
  and sets `streaming=True`. **Skills are auto-derived, one per registered tool**, with `tags=[]`
  (`server.py:192-205`). The card therefore advertises the agent's internal tool list to any caller.
- **There is no authentication parameter** (`server.py:32-50`). Auth has to be added by composing
  `to_starlette_app()` / `to_fastapi_app()` into your own app.
- Tenancy: the recommended mode is `agent_factory(context_id) -> Agent`, with an LRU of
  `DEFAULT_MAX_CONTEXTS = 1000` (`a2a/executor.py:129, 190`). The single `agent=` mode is deprecated as
  "Not multi-tenant safe — every A2A context reuses the same instance" (`server.py:66-68`,
  warning at `executor.py:199-206`).
- ✅ **The default stream does not follow the A2A spec, and the code says so:**
  ```python
  "The default A2A response stream implemented in the strands sdk does not conform to "
  "what is expected in the A2A spec. Please set the `enable_a2a_compliant_streaming` "
  ```
  (`a2a/executor.py:401-409`). The docs say the same (`a2a-server-configuration.mdx:36`).
- Client: `A2AAgent(endpoint, name=, timeout=300, client_config=)` is an `AgentBase`
  (`strands-py/src/strands/agent/a2a_agent.py:44`). It always forces `streaming=True`
  (`a2a_agent.py:245-251`). SigV4, OAuth or bearer auth goes through a caller-supplied `ClientConfig`
  (`a2a_agent.py:54-67`).
- ⚠️ The wire details (JSON-RPC methods, SSE framing, the agent-card path) are a2a-sdk library
  defaults. They were not read here.

### 5.4 ACP server in the CLI ✅

`strands --acp-server` "exposes the agent to an ACP client over stdin/stdout. It creates a harness
agent for each ACP session, supports client-supplied MCP servers, and supports loading saved sessions
with transcript replay" (`strands-cli/README.md:465-470`). It is built on `@agentclientprotocol/sdk`
`1.3.0` (`strands-cli/package.json:62`).

- `initialize` advertises `loadSession`, image and embedded-context prompts, and MCP over http/sse
  (`strands-cli/src/tui/acp/server.ts:57-74`).
- One workspace per process. A second `cwd` throws (`server.ts:194-206`).
- One prompt at a time per session (`server.ts:107-109`).
- **Approval asymmetry.** When the CLI serves an *imported Python source agent*, tool-permission
  requests become ACP `session/requestPermission` round-trips (`strands-cli/src/tui/project/acp.ts:66-82`).
  The *harness* path streams events and usage but contains no `requestPermission` call
  (`server.ts:102-147`) ✅. The harness default is `interventions=None` (`harness-py/README.md`,
  interface block). So by default an ACP client driving the harness gets no approval prompts. ⚠️ Not
  exercised at runtime; see [approval-gate](../ai-workflow/wiki/concepts/approval-gate.md) and
  [03-tools-and-approval.md](03-tools-and-approval.md).
- `agentInfo.version` is hard-coded `'0.0.1'` (`server.ts:65-69`), although `HARNESS_VERSION` is
  imported in the same file (`server.ts:16`).

## 6. Deployment

### 6.1 What the docs list 📣

`site/src/content/docs/user-guide/sdk/deploy/index.mdx:17-60` lists these targets: Bedrock AgentCore
(py/ts), Lambda, Fargate, App Runner, EKS, EC2, Docker, Kubernetes, Terraform and the Nx plugin for
AWS. Every target is packaging around the same in-process agent. None is a Strands runtime.

### 6.2 AgentCore: the dependency points the other way ✅

A grep for `agentcore` across `strands-py`, `strands-ts`, `harness-py`, `harness-ts`, `strands-cli`
and `strands-mcp` finds one line:

```python
# Compatibility for AgentCore's root import; remove after AgentCore imports from bidi.agent.
```
(`strands-py/src/strands/experimental/bidi/__init__.py:6`)

The SDK has no AgentCore integration. The external `bedrock-agentcore` package imports Strands'
*experimental* bidi module, and the SDK keeps a shim for it. The AgentCore guide uses
`BedrockAgentCoreApp`, `@app.entrypoint`, `POST /invocations`, `GET /ping` and port 8080
(`deploy/deploy_to_bedrock_agentcore/python.mdx:50-133, 264-265`) 📣. The same page imports it two ways,
`from bedrock_agentcore.runtime import BedrockAgentCoreApp` (l.60, 86) and
`from bedrock_agentcore import BedrockAgentCoreApp` (l.107) ⚠️.

### 6.3 Deploy examples contradict the SDK's tenancy rule ❌

- The Docker/FastAPI example creates `strands_agent = Agent(model=model)` at module level and calls
  it from every request (`site/src/content/docs/user-guide/sdk/deploy/deploy_to_docker/agent.py:15, 33`).
- The AgentCore examples do the same with `agent = Agent()` (`deploy_to_bedrock_agentcore/python.mdx:89-96, 109-112`).

In code this means two things:
1. Every caller's turns accumulate in one `agent.messages`.
2. Overlapping requests hit the default `concurrent_invocation_mode=ConcurrentInvocationMode.THROW`,
   which "raises ConcurrencyException if concurrent invocation is attempted"
   (`strands-py/src/strands/agent/agent.py:217, 307-308`).

The SDK's own A2A server deprecates exactly this shape as not multi-tenant safe (§5.3). The Lambda
guide gets it right: it builds the `Agent` inside `handler()` (`deploy/deploy_to_aws_lambda.mdx:61-66`).
⚠️ AgentCore Runtime may isolate sessions at the platform level. That was not verified.

## 7. What this means if you are building a harness

- [ ] Decide whether multi-agent needs a control plane. Strands shows how far an in-process orchestrator goes (nesting, interrupts, state serialisation) and where it stops (no remote Swarm members, no per-node session persistence).
- [ ] Choose explicitly whether the model or code routes. Keep deterministic edges (Graph) and model-driven handoff (Swarm) as separate primitives.
- [ ] Treat inter-agent text as untrusted input. Delimit and tag provenance on handoff messages and upstream results before splicing them into a user turn.
- [ ] Give each of your limits its own counter, and name them after what they count.
- [ ] Generate the delegation tool's schema from policy, and enforce "child ≤ parent capability" at call time (§4.2).
- [ ] If you expose the agent, pick the protocol by relationship: MCP for "agent as a tool", A2A for agent peers, ACP for an editor driving a session. Forward approvals over whichever you pick.
- [ ] Don't publish your tool list as AgentCard skills by default, and ship auth in the server, not as an exercise for the reader.
- [ ] In deployment examples, build one agent per session (factory), never a module-level singleton.

## 8. Open questions

- The A2A wire (JSON-RPC method names, SSE framing, card path) and the behaviour difference of the "compliant" stream were not read from `a2a-sdk` and not exercised.
- Does the harness ACP path really run tools ungated under `interventions=None`, or does something in the CLI or TUI add a gate? This needs a run against a mock model.
- Does AgentCore Runtime's per-session isolation neutralise the module-level `Agent` pattern (§6.3)?
- The TypeScript Graph/Swarm were not read. Is the `max_handoffs`/`max_iterations` conflation present there too?
- Does Graph's `asyncio` batch parallelism give real concurrency for synchronous (non-async) tools, or do they serialise on the thread pool?
