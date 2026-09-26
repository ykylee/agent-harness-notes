# 03. Tools, extension points, and the approval model

> Read: the tool layer (`strands-py/src/strands/tools/`), hooks, interrupts, interventions and their
> vended handlers (Cedar, human-in-the-loop), steering, the Bedrock guardrail path, the MCP client,
> `harness-py`'s interventions sugar, `strands-cli`'s permission policy, and design docs
> `team/designs/0001`, `0006` and `0007`. Also the separate catalogue `strands-agents/tools` @ `8c82c29`.
>
> Method: mostly static reading. **Two probes ran against a scripted mock model**
> (`MockedModelProvider` from `strands-py/tests/fixtures`; no LLM involved, so one run is
> deterministic). The Cedar + HITL probe was re-run independently in a fresh venv and reproduced,
> control included. The steering probe had a control appended afterwards.
>
> Source: `strands-agents/harness-sdk` @ `15da9dc` (2026-09-25; python/v1.57.1, typescript/v1.19.0,
> harness 0.x). Researched 2026-09-26.
>
> Dominant grade: ✅ confirmed by source; 🧪 on the four behaviours that matter most; eight ❌.

## 1. Tools

### 1.1 Shapes and `@tool`

Shapes follow Bedrock Converse (`strands-py/src/strands/types/tools.py`) ✅:

| Type | Fields |
|---|---|
| `ToolSpec` | `name`, `description`, `inputSchema{json}`, `outputSchema?`, `annotations?` |
| `ToolUse` | `toolUseId`, `name`, `input`, `reasoningSignature?` |
| `ToolResult` | `toolUseId`, `status: "success"\|"error"`, `content: [text\|json\|image\|document]` |
| `ToolContext` | `tool_use`, `agent`, `invocation_state`, `cancel_signal: threading.Event`, `.interrupt()` |

`annotations` carries MCP hints and is documented as "untrusted hints … consumers such as permission
layers must not treat them as a security boundary". No code in either SDK reads
`destructiveHint`/`readOnlyHint` ✅.

`@tool` (`tools/decorator.py`) builds a Pydantic model from type hints (l.192) and takes the
description from the docstring minus `Args` (l.109, 285–314). `@tool(name=, description=,
inputSchema=, context=)` overrides it; `agent`/`tool_context` parameters are injected and hidden
from the schema (l.397–432). Async generators stream, coroutines are awaited, **sync functions run
in `asyncio.to_thread`** (l.654), so cancellation is cooperative only. Any exception becomes an
error `ToolResult`; `InterruptException` becomes a `ToolInterruptEvent` (l.657) ✅.

### 1.2 Registry, loading, executors, direct calls

- **Registry** (`tools/registry.py:44–159`) accepts paths, `module:function`, modules, `AgentTool`,
  `ToolProvider` (how MCP plugs in) and `Agent` (auto `.as_tool()`). Duplicate names raise, as do
  names differing only by `-`/`_` (l.249–268) ✅.
- **Hot reload** is off by default (`agent/agent.py:199`). When on, it `exec_module`s every `*.py`
  in `Path.cwd()/"tools"` (`registry.py:315`, `loader.py:66`) and a watchdog reloads on modify
  (`tools/watcher.py:52–65`) ✅. ⚠️ That is arbitrary code from the cwd, with no allow-list.
- **Executors.** The default `ConcurrentToolExecutor` (`agent/agent.py:534`) creates one task per
  tool use with **no concurrency cap** (`executors/concurrent.py:54–70`); siblings of an interrupted
  tool keep running. `SequentialToolExecutor` stops at the first interrupt (`sequential.py:48–71`) ✅.
  TypeScript offers the same two strategies (`strands-ts/src/agent/agent.ts:143–153`).
- **Direct calls** (`agent.tool.x(...)`, `tools/_caller.py`) go through the same executor, so
  hooks and interventions fire. An interrupt raised during a direct call becomes
  `RuntimeError("cannot raise interrupt in direct tool call")` (l.123–126), so an interrupt-mode
  gate fails closed there ✅. Tool kwargs double as `invocation_state` (l.119).

## 2. Hooks and middleware

### 2.1 Events and what each may mutate

Writes are enforced by `__setattr__` + `_can_write` (`hooks/registry.py:77–95`), which guards
**top-level fields only**: `tool_use["input"]` stays mutable ✅.

| Event (`hooks/events.py`) | Writable | Effect |
|---|---|---|
| `BeforeInvocationEvent` (l.39) | `messages`, `cancel` | rewrite input, cancel |
| `AfterInvocationEvent` (l.70) | `resume` | re-invoke with new input |
| `BeforeToolsEvent` (l.150) | `cancel` · interruptible | cancel the batch |
| `AfterToolsEvent` (l.186) | `end_turn` | stop without another model call |
| `BeforeToolCallEvent` (l.221) | `cancel_tool`, `selected_tool`, `tool_use` · interruptible | cancel, **swap implementation**, rewrite input |
| `AfterToolCallEvent` (l.261) | `result`, `retry` | **replace result**, re-run |
| `BeforeModelCallEvent` (l.318) | `cancel` | cancel model call |
| `AfterModelCallEvent` (l.348) | `retry` | discard and re-call (streamed chunks already emitted) |
| `BeforeNodeCallEvent` (l.424) | `cancel_node` · interruptible | multi-agent node gate |

Order is a float passed to `add_callback(..., order=)`; ties keep registration order
(`hooks/registry.py:192–266`). The constants are `SDK_FIRST=-100`, `INTERVENTION_OUTPUT=-90`,
`DEFAULT=0`, `MODEL_ROUTING=50`, `INTERVENTION_INPUT=90`, `SDK_LAST=100` (l.30–39). "After" events
reverse registration order only within an order group (l.436–448). Each callback may raise one
interrupt, with names unique per event (l.334–353) ✅.

> ⚠️ Input interventions run at order 90. A user hook at order > 90, or `ExecuteToolStage`
> middleware (`tools/executors/_executor.py:302–320`), can rewrite `tool_use` **after**
> authorization decided. Inferred from ordering; not probed.

### 2.2 Middleware

Three stages exist — `InvokeModelStage`, `ExecuteToolStage`, `AgentStreamStage`
(`strands-py/src/strands/_middleware/stages.py`). The Python package is private and used by
routing, memory, delegation (`agent/_agent_delegation.py:117`); TypeScript exports it
(`strands-ts/src/index.ts:361`) ✅. Its README self-reports two hazards 📣: `except Exception`
swallows interrupts (`InterruptException(Exception)`, `interrupt.py:37` ✅), and agent-stream
interrupt ids are unscoped, so an orchestrator can "cross-wire one human approval to both" agents.

## 3. Plugins and skills — the capability-distribution axis

`Plugin` (`plugins/plugin.py`) is an ABC with a `name`; it auto-discovers `@hook`/`@tool` methods
and may define `init_agent(agent)` ✅. Design 0001 says plugins are shared "by vending their own
packages through some distributions mechanism (pypi, npm, github, etc)" (`0001-plugins.md:57`) 📐.
There is **no manifest, entry-point discovery, install verb or capability declaration** ✅.

`AgentSkills(Plugin)` (`vended_plugins/skills/agent_skills.py`) loads `SKILL.md` directories through
the agent's sandbox, `Skill` objects, or raw `https://` URLs (l.84–134, 507). It injects
`<available_skills>` XML into the system prompt each invocation (l.188–243) and exposes a `skills`
tool. `allowed-tools` is only echoed as text (l.391–392; "Experimental: not yet enforced",
`skill.py:238`); the docs say so (`site/src/content/docs/user-guide/sdk/plugins/skills.mdx:265`) ✅.

> 📌 Against [capability-distribution](../ai-workflow/wiki/concepts/capability-distribution.md) and
> Codex's marketplace ([../docs/13-marketplace-and-plugins.md](../docs/13-marketplace-and-plugins.md)),
> Strands sits at the **code-library** end. Codex separates the capability unit (plugin + portable
> manifest) from the distribution/policy unit (marketplace) and keeps install ≠ enable. A Strands
> plugin is an in-process object with full agent access, installed by `pip`, declaring nothing a
> policy layer could refuse.

## 4. Approval — an exception with replay

### 4.1 The mechanism

`event.interrupt(name, reason)` uses a deterministic id
(`v1:before_tool_call:<toolUseId>:<uuid5(name)>`, `hooks/events.py:248–259`). With no stored
response it raises `InterruptException`; the loop stops with `stop_reason="interrupt"`. The caller
resumes by passing **as the prompt** a list of only `{"interruptResponse": {"interruptId",
"response"}}` blocks (`interrupt.py:119–152`). The **hook or tool then re-executes from the top**,
and `interrupt()` returns the stored response; the docs agree ("when the tool/hook re-executes",
`site/.../interrupts.mdx:221`) ✅. `PendingToolExecution` skips the model call on resume
(`interrupt.py:44–55`). Interrupt state is session-persisted (`types/session.py:137–138`) but drops
answered invocation-scoped responses:

```python
Exclude deactivated invocation-scoped responses — persisting them would
give a restored agent a standing approval.
```

> 📌 **Replay is the cost of an exception-based pause.** Anything before `interrupt()` — including
> every earlier handler in the same dispatch — runs again on resume. §4.4 shows it corrupting Cedar's
> rate counter.

### 4.2 Is it a protocol primitive?

Inside the SDK, no: an exception plus a content-block shape. The **only wire shape is the A2A
server** (`multiagent/a2a/executor.py`): an interrupt becomes `input_required` with
`DataPart{"interrupts": [{interruptId, name, reason}]}` (l.428–466), and a resume is a strictly
validated `DataPart{"interruptResponse": {...}}` (l.662–720) ✅. The A2A *client* maps remote
`input_required` to `"interrupt"` but will not answer (`multiagent/a2a/_converters.py:50–52`):

```python
raise ValueError("InterruptResponseContent is not supported for A2AAgent")
```

Against Codex ([../docs/02-app-server-protocol.md §7](../docs/02-app-server-protocol.md),
[approval-gate](../ai-workflow/wiki/concepts/approval-gate.md)):

| | Codex App Server | Strands |
|---|---|---|
| Mechanism | server→client JSON-RPC request; the turn pauses | exception unwinds; caller re-invokes |
| Request kinds | commandExecution / fileChange / permissions / userInput / elicitation … | untyped `name` + arbitrary `reason` |
| Decisions | `accept`, `acceptForSession`, `decline`, `cancel`, amendment variants | `response: Any`; each gate interprets it |
| Settled elsewhere | `serverRequest/resolved` | none |
| Resume | same turn continues | hook/tool **re-executes** |

> 📌 Strands has no decision vocabulary, which is why the three gates in §5 read the same answer
> differently. A typed `ReviewDecision` would have prevented the steering bug.

### 4.3 Interventions (design 0007)

`InterventionHandler` (`strands-py/src/strands/interventions/`) declares `name` and `on_error`
(default `"throw"`). Actions are `Proceed`, `Deny`, `Guide`, `Confirm` (before_tool_call only) and
`Transform`. `Agent(interventions=[...])` registers one hook per overridden method at
`INTERVENTION_INPUT`/`OUTPUT` (`registry.py:65–95`); duplicate names raise (l.45–49) ✅.
`_dispatch` (l.194–248) runs handlers **in registration order**: `Deny` or a failed `Confirm`
short-circuits; `Transform` and `Confirm` act immediately; `Guide`s accumulate and apply last.

❌ The docs and design claim a precedence the code does not have:

> "handlers always run in registration order with well-defined precedence (deny > confirm > guide >
> transform > proceed)" — `site/.../agents/interventions/index.mdx:204`
> "**Interrupt** pauses if no handler denied" — `team/designs/0007-intervention-primitive.md:196`

A `Confirm` from handler A pauses for a human **before** handler B's `Deny` is evaluated; B denies on
resume, so the human was asked for nothing. An approved `Confirm` can still be cancelled by `Guide`s
applied afterwards.

❌ "Every decision is logged to a unified audit trail accessible via `agent.interventions.auditLog`"
(0007:162). Neither SDK has one. The TypeScript test named for it asserts nothing
(`strands-ts/src/interventions/__tests__/registry.test.ts:636–646`):

```ts
it('is logged in the audit trail', async () => {
  ...
  await hookRegistry.invokeCallbacks(makeBeforeToolCallEvent())
  // Transform was applied (verified by the apply fn mock tests above)
})
```

The design's optional retry cap was not built ("The framework imposes no retry cap on
guide-triggered retries", `actions.py`, `Guide`) ✅.

### 4.4 Cedar authorization (design 0006)

Cedar is **implemented**, as an intervention handler rather than the designed plugin
(`vended_interventions/cedar/cedar_authorization.py` with `cedarpy`;
`strands-ts/src/vended-interventions/cedar/cedar.ts`) ✅. The request (l.155–228) against the design:

| Part | Code | Design 0006 (❌ against code) |
|---|---|---|
| principal | `principal_resolver(invocation_state)` or static; **default `User::"anonymous"`** | from `invocation_state`, "no fail-open path" |
| action | `Action::"<tool>"` | `Action::"use_tool::<tool>"` |
| resource | **always `Resource::"agent"`** | `Tool::"<tool>"` or `resource_resolver` |
| context | `{input: args, session: {…enricher, hour_utc, call_count}}` | flat args + `timestamp`, `environment`, … |
| API | constructor, `reload()` | builder, `from_config` TOML, post-tool audit hook |

The design's "Future: Intervention Handler Primitive" section (0006:488) foresaw the move.
Exceptions and `NoDecision` deny; call counts persist in `agent.state` ✅. Resource-level ownership
policies cannot be expressed.

**Skip-on-error.** 0006 Appendix A (l.175) warned: "if a `forbid` policy is malformed, Cedar skips
it during evaluation, which means you fail open for that constraint … the plugin should check for
and surface these." The code checks only `result.allowed`, in Python and TypeScript
(`cedar.ts:201–206`). 🧪 With `permit delete` + `forbid delete when { context.session.role !=
"admin" }` and no enricher, **the tool ran**. The control, with `role="user"` supplied,
**blocked**, so the pass-through is the missing attribute, not a delivery failure (reproduced
independently). ❌ This refutes "Cedar engine failures (malformed policies, evaluation errors) are
always fail-closed" (`site/.../interventions/cedar-authorization.mdx:239`). With an auto-generated
schema, unknown-attribute validation errors are also **suppressed** (`cedar_authorization.py:52–61`),
so load time does not catch it either.

**Call counting.** 🧪 With `[CedarAuthorization(permit delete), HumanInTheLoop()]`, `call_count` was
1 after the interrupt and **2 after resume**; the tool ran once. ❌ This refutes "`call_count` …
tracks how many times each tool has been invoked successfully" (`cedar-authorization.mdx:75`). No
test covers the pair.

❌ In part: "if principal identity cannot be resolved, all tool calls are denied"
(`cedar-authorization.mdx:25`) holds only with a `principal_resolver`; otherwise the principal is
anonymous.

### 4.5 `HumanInTheLoop`: allow/ask with first-match precedence

`vended_interventions/hitl/hitl.py` ✅ states its order in code (l.257–264): `!tool` → ask; trusted
→ run; `*` → run; listed → run; classifier decides; otherwise ask. There is **no deny tier**.
`ask=None` uses interrupt/resume; `ask="stdio"` reads `input()` in a locked thread; a custom `ask`
returning `None` becomes `Deny` (l.245). Answering `t` writes the tool *name* into
`agent.state["hitl:trusted_tools"]`, which is session-persisted (`types/session.py:145`) 🧪 — a
restored session keeps a standing per-tool approval, exactly what `interrupt.py` avoids for raw
responses. The LLM risk classifier sees `json.dumps(tool_use['input'])` and fails closed on errors
(l.289–314).

> ⚠️ That classifier reads attacker-influenced input
> ([indirect-prompt-injection](../ai-workflow/wiki/concepts/indirect-prompt-injection.md)). Not tested.

### 4.6 `strands-cli`: the only persisted allow/ask policy

`strands-cli/src/tui/permissions/policy.ts` ✅. `CedarPermissions` (`onError='deny'`) permits by
default `read` inside the workspace realpath, `todo_write`, `retrieve_offloaded_content` and
non-destructive `strands_config`. Decision order (l.193–216): `mode === 'bypassPermissions'` →
proceed; tool in `permissions.allow` → proceed; Cedar allows → proceed; a deny whose reason starts
`'Access denied by Cedar policy'` → **ask** (Allow once / Always allow tool, persisted / Deny). The
store is `~/.strands/cli/config.json`, user-level only (`config.ts:86–114`).

> 📌 **No hard-deny tier.** TypeScript Cedar uses that same prefix whether no `permit` matched or an
> explicit `forbid` fired (`cedar.ts:201–206`), so an authored `forbid` becomes a prompt too. Aside's
> engine ([../browser-agents/10-aside-enforcement-and-native.md §1](../browser-agents/10-aside-enforcement-and-native.md))
> has `allow`/`approved`/`deny`/`ask` buckets, per-argument regex matchers and account → session →
> runtime-root layering; this repository's own gate settled on `deny > ask > allow > default`
> ([approval-gate §7](../ai-workflow/wiki/concepts/approval-gate.md)). In the Strands CLI, `deny`
> sits *below* `ask`.

### 4.7 `harness-py` sugar

`harness-py/src/strands_harness/interventions.py:9–65` maps `"off"` → nothing, `"ask"` → HITL,
`"smart"` → HITL + classifier, `*.cedar` → Cedar, and **any other string** → the classifier's system
prompt ✅. The default is `None` ("off — every call runs", `agent.py:388`), while `shell`, `write`,
`edit` and `programmatic_tool_caller` are on (`defaults.py`) and, without a sandbox, run under
`NotASandboxLocalEnvironment` (see [04](04-harness-and-cli.md), [07](07-security.md)). Subagents
inherit interventions, hooks and sandbox (`agent.py:428–466`) ✅. ❌ Minor: the harness says a second
same-named handler "would silently win or be dropped" (l.69–71); the SDK raises `ValueError`
(`interventions/registry.py:45–49`).

## 5. Three gates, three semantics

| Gate | On handler error | What counts as "yes" | Channel |
|---|---|---|---|
| Interventions `Confirm` (SDK) | `on_error`, default `throw` | `True`, `"y"`, `"yes"` | interrupt/resume or inline `ask` |
| Python `SteeringHandler` `Interrupt` (`vended_plugins/steering/core/handler.py`) | **swallowed, tool runs** (l.96–101) 🧪 | **any truthy value** (l.121–125) 🧪 | interrupt/resume |
| `strands-agents/tools` consent | n/a | exactly `y` | terminal prompt `[y/*]` |

🧪 Answering `"no"` to steering let the tool run:

```python
can_proceed: bool = event.interrupt(name=f"steering_input_{tool_name}", reason={"message": action.reason})
if not can_proceed:
    event.cancel_tool = f"Manual approval denied: {action.reason}"
```

The appended control showed the interrupt **does fire** (`stop_reason=interrupt`) and `False`
blocks, so `"no"` passing is the truthiness test, not a missed interrupt. The docs acknowledge the
split ("Python uses plugins; TypeScript uses the interventions framework", `steering.mdx:3`); Python
steering did not inherit the interventions' semantics. ❌ Internal: `core/handler.py:34` documents
"Interrupt: Model response handling paused…", but l.202 says it is unsupported and
`ModelSteeringAction = Proceed | Guide`.

`strands-agents/tools` @ `8c82c29` ✅: `BYPASS_TOOL_CONSENT=true` is read per call in 12 modules
(`shell`, `python_repl`, `file_write`, `editor`, `load_tool`, `environment`, `http_request` non-GET,
`use_aws` mutative ops, `memory`, `mem0_memory`, `cron`, `use_computer`). `STRANDS_NON_INTERACTIVE`
also skips consent in `shell`, `python_repl`, `load_tool` (`python_repl.py:621,634`). EOF/Ctrl-C
cancels (`utils/user_input.py`). The `environment` tool refuses to set `BYPASS_TOOL_CONSENT`
(`PROTECTED_VARS`, `environment.py:168–190`), yet `cron`'s docs recommend scheduling
`BYPASS_TOOL_CONSENT=true strands "…"` (l.102–104).

> ⚠️ `python_repl` with the model-controllable `interactive=False` runs `exec(code,
> self._namespace)` **in the agent process** (l.252–254; `interactive=True` forks, l.350). One
> approved run setting `os.environ["BYPASS_TOOL_CONSENT"]="true"` would disable consent for every
> later tool. Inferred from source; not executed.

> 📌 The wiki's rule "a gate that degrades to allow when its channel is missing is not a gate"
> ([approval-gate §7](../ai-workflow/wiki/concepts/approval-gate.md)) is broken by Python steering:
> an exception in the check means the tool runs.

SDK-vended tools (`vended_tools/shell`, `file_editor`, …) have no consent of their own;
`handoff_to_user` is the only one that raises an interrupt (`handoff_to_user.py:60`) ✅.

## 6. Guardrails and MCP

**Bedrock Guardrails** are service-side: `guardrail_id`/`version` go into Converse
`guardrailConfig` (`models/bedrock.py:435–446`). The SDK rewrites history afterwards, only when the
trace shows a **BLOCKED** action (ANONYMIZED spans are already masked), falling back to
`stop_reason == "guardrail_intervened"` without a trace (l.1181–1207). `guardrail_redact_input`
defaults True, `_output` False (l.1209–1240). When streaming, assistant chunks reach the callback
before the decision (l.1485–1501). `_redact_user_content` keeps `toolResult` blocks and blanks them
(`agent/agent.py:2048`) ✅. No `ApplyGuardrail` intervention is vended; 0007 lists Bedrock
Guardrails as an intervention instance 📐, but only a docs example exists
(`safety-security/guardrails.mdx:56`).

**MCP client** (`tools/mcp/mcp_client.py`, 2,734 lines) ✅: stdio, SSE and streamable HTTP (with
`auth`/`auth_provider`); `load_servers` for mcp.json-style config; `prefix` and `tool_filters`; a
background-thread session; MCP tasks. Annotations pass through to `ToolSpec.annotations`
(`mcp_agent_tool.py:89–97`). Elicitation is a plain `elicitation_callback` handed to `ClientSession`
(l.318, 1476), **not bridged to interrupts**; URL-mode `-32042` errors become result text
(l.1375–1398). Sampling and roots are unsupported. In Codex, elicitation is one of the typed
server→client requests ([../docs/02-app-server-protocol.md §7](../docs/02-app-server-protocol.md));
in Strands it bypasses the approval machinery.

## 7. What this means if you are building a harness

- [ ] Give approvals a **typed decision vocabulary**, not `Any`: three gates reading an untyped
      answer produced three meanings of "yes".
- [ ] Choose **pause** (suspend and continue) or **replay** (unwind and re-execute) deliberately. If
      you replay, make pre-gate steps idempotent or cache them by interrupt id.
- [ ] State conflict resolution as a total order and implement *that*; evaluate every `deny` before
      asking a human.
- [ ] Keep a hard `deny` tier that `ask` cannot override, and never pick the tier by matching a
      reason string.
- [ ] Treat policy-evaluation errors on an *Allow* as failures, not noise.
- [ ] Authorize the **final** call: gate after every stage that can rewrite it.
- [ ] Expire "trust for session" with the process unless persistence was chosen explicitly.
- [ ] Require plugins to declare tools, hooks and permissions
      ([capability-distribution](../ai-workflow/wiki/concepts/capability-distribution.md)).
- [ ] Route MCP elicitation through the same gate channel as tool approval.

## 8. Open questions

- ⚠️ Post-authorization rewriting of `tool_use` (hook at order > 90, or `ExecuteToolStage`) was
  inferred from ordering, not probed.
- ⚠️ The `python_repl` in-process consent bypass was not executed.
- ⚠️ Whether an A2A server authenticates *who* answers `input_required`; server auth was not read.
- ⚠️ Whether sharing one `CedarAuthorization` instance between harness parent and subagent leaks
  call counts, as its docstring warns (`cedar_authorization.py:80–82`).
- ⚠️ Whether subagents parked on an interrupt (in-memory dict, `subagent.py:482`) survive a restart.
- ⚠️ Whether the LLM risk classifier can be steered by injected tool input.
- TypeScript parity was checked only for Cedar decisions, interventions and exports; the TypeScript
  steering intervention's semantics were not read.
