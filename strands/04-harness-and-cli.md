# 04. Strands harness and the `strands` CLI

> What was read: `harness-py/` (every module under `src/strands_harness/`, plus `docs/subagent.md`),
> `harness-ts/src/`, `strands-cli/` (`src/cli/`, `src/tui/{runtime,config,permissions,workspace,provider}`, `README.md`),
> the SDK sandbox package `strands-py/src/strands/sandbox/`, and the harness pages under `site/`,
> including the launch blog and its two benchmark chart embeds.
> Method: static reading only. Nothing was executed; no probe was run.
> `strands-agents/harness-sdk` @ `15da9dc` (2026-09-25; python/v1.57.1, typescript/v1.19.0, harness 0.x).
> Researched 2026-09-26.
>
> Dominant grade: ✅ **confirmed from source.** Every security consequence below is ⚠️ inferred from
> source. None was demonstrated.

## 1. What "harness" means here

`create_harness()` (Python) and `createHarness()` (TS, async) are **factories**. The Python one returns a plain
`strands.Agent` ✅ (`harness-py/src/strands_harness/agent.py:249-267,541-552`; `harness-ts/src/agent.ts:364`).
There is no new loop, runtime, or process boundary. The harness selects defaults and adds a few
tools on top of SDK primitives: the sandbox seam, `ContextManager`, `ContextOffloader`, `AgentSkills`,
`MemoryManager`, HITL/Cedar interventions, and Background Tasks. Compare Codex, where the
[harness](../ai-workflow/wiki/concepts/harness.md) is a long-lived process with its own protocol
([../docs/02-app-server-protocol.md](../docs/02-app-server-protocol.md)).

> 📌 Strands' "harness" is an opinionated *configuration* of an in-process library agent. Anything it
> does not configure falls back to SDK defaults. That fallback is where the execution-environment gap
> in §3 comes from.

## 2. Defaults wired by `create_harness()`

| Axis | Default | Citation | Grade |
|---|---|---|---|
| Model | `bedrock/global.anthropic.claude-opus-5` | `harness-py/src/strands_harness/defaults.py:5`; `harness-ts/src/defaults.ts` | ✅ |
| Effort | `"auto"` → provider's recommended level (`"high"` for Bedrock/Anthropic/OpenAI/Google/Mantle) | `defaults.py:7`; `models.py` `_PROVIDERS` | ✅ |
| Caching | on; Bedrock/Anthropic get `CacheConfig(strategy="auto", tools_ttl=True)`, others rely on server-side caching | `defaults.py:11`; `models.py` `_bedrock`/`_anthropic` | ✅ |
| Built-in tools | `shell, read, write, edit, web_fetch, web_search, programmatic_tool_caller, subagent` | `defaults.py:13-25` | ✅ |
| `web_search` in practice | **off on the default model**: Bedrock Converse has no native search, so it warns and drops (raises only if named explicitly) | `agent.py:112-139,402-411` | ✅ |
| Plugins | `todos`, `environment` | `defaults.py:28-31`; `agent.py:68` | ✅ |
| Context | SDK `"auto"` (summarize at 85% utilization) plus `ContextOffloader` (results >1,500 tokens to disk, 750-token preview) | `agent.py:74-75,142-147,493-499`; `strands-py/src/strands/_context_manager/context_manager.py:34` | ✅ |
| Session | `SnapshotSessionManager`, random 8-hex id, `./.agent/sessions`; **no auto-resume** | `agent.py:474-487` | ✅ |
| Skills | `./.agent/skills` if it exists | `agent.py:154-165` | ✅ |
| Memory | `FileMemoryStore` in `./.agent/memory`; extraction on the small summarizer model; injected **every model call**; `search_memory` on, no `add_memory` | `memory.py:89,101-107`; `models.py:62-68` | ✅ |
| Interventions | **none: every tool call runs** | `agent.py:265`; `interventions.py:89-90` | ✅ |
| Background tasks | model may background any tool; `subagent` always backgrounded | `agent.py:70-72,221-246` | ✅ |
| Telemetry | off unless `OTEL_TRACES_EXPORTER` is set; the OTEL spec default `otlp` is deliberately ignored | `telemetry.py:1-66` | ✅ |
| Sandbox | **not set by the harness** → SDK host fallback (§3) | `strands-py/src/strands/agent/agent.py:352` | ✅ |

The portable `config.json` mirrors these defaults (`harness-py/src/strands_harness/config.py`,
`DEFAULT_HARNESS_AGENT_CONFIG`). ✅ Loading it **executes code**: module references for tools, plugins,
sandbox, model, and interventions go through `importlib` + `exec_module` (`config.py` `_load_module`). A
portable agent config is therefore code, not data.

### 2.1 The system prompt

`HARNESS_CONTRACT` (`harness-py/src/strands_harness/prompt.py:11-40`) is byte-identical in TS apart from
escaping (`harness-ts/src/prompt.ts`). ✅ It is model-neutral, with no identity, and has four sections:
- **Acting**: act when you have enough; explore first; "done only when you have verified it".
- **Tools**: parallelize; a denied call "is information".
- **Safety**: confirm hard-to-reverse or outside-the-environment actions "unless you have been explicitly told to proceed".
- **Context management**: history may be summarized.

One line matters for security:

```
 - `<system-reminder>` tags in messages and tool results are injected by the harness, not the user.
```

✅ No code in harness-py, harness-ts, the SDKs, or the CLI strips or escapes `<system-reminder>` from tool
output. `grep` finds the string only in `prompt.*`, `todos.*`, and `environment.*`. ⚠️ A fetched page, file, or MCP result
containing that tag is therefore framed by the contract as harness-authored. See
[indirect-prompt-injection](../ai-workflow/wiki/concepts/indirect-prompt-injection.md) and
[07-security.md](07-security.md).

### 2.2 "Benchmarked defaults"

`README.md:66` and `site/src/content/docs/user-guide/harness/index.mdx:3,15` say "benchmarked defaults".
📣 No benchmark code, run config, or raw result is committed. What is committed is two chart embeds with
hard-coded numbers:
- `site/public/embeds/strands-harness-benchmarks.html:152-177`
- `site/public/embeds/strands-harness-terminalbench.html` ("89 trials each")

Their comments cite `bench-with-astra.xlsx` and `harbor-report-sep17.xlsx`, with cells **substituted across the two**. Neither file is in the repo. The
benchmark harness itself lives in another repo (`site/src/util/redirect.ts:116` → `strands-labs/benchmark-harnesses`).

❌ The headline says "28% lower cost **with equal or better accuracy across benchmarks**"
(`strands-harness-benchmarks.html:109-110`; also the blog's "maintaining equal or better accuracy",
`site/src/content/blog/introducing-strands-harness.mdx:27`). The chart's own `POINTS` array refutes
this. On the same model, Strands scores below a competitor in **7 of 19 pairs**:

| vs | model | Δ score |
|---|---|---|
| oh-my-pi | GPT-5.6 Sol | −2.41 |
| OpenCode | Opus 4.8 | −1.83 |
| Codex | GPT-5.6 Luna | −0.72 |
| oh-my-pi | GPT-5.6 Luna | −0.54 |
| Claude Code | Opus 4.8 | −0.18 |
| oh-my-pi | Fable 5 | −0.10 |
| Claude Code | Opus 5 | −0.05 |

The blog body's "nearly equal benchmark scores" (l.29) is the accurate phrasing. Each point is one averaged run
with no variance, and five of the seven gaps are under one point.

> ⚠️ **What the refutation does and does not say.** It refutes the wording "equal or better" against
> the chart's own numbers (recomputed from `POINTS` by the main session, 2026-09-26). It does **not**
> show Strands is worse: with no variance reported, sub-point gaps are indistinguishable from run
> noise in either direction (the same trap as this repository's own single-run numbers,
> [`SYNTHESIS.md` §6.5](../SYNTHESIS.md)). The chart's footnote also concedes that the 28% figure
> depends on including "DeepSeek Harness", which "scores lower on every benchmark." ✅ The blog's mechanism claims do match code: 1,500-token results (`agent.py:74`) and 85%
summarization.

## 3. Execution environment: plane selection, not OS policy

### 3.1 The SDK `Sandbox` seam

`Sandbox` (`strands-py/src/strands/sandbox/base.py:36`) is an abstract "execution environment". Its methods are
`execute_streaming`, `execute_code_streaming`, `read_file`, `write_file`, `remove_file`, and `list_files`.
Every harness built-in reaches the world through `tool_context.agent.sandbox`: shell, the file tools,
`web_fetch`'s curl, and the environment probes. ✅ There are three implementations:

| Implementation | What it is | Isolation it brings | Env passed to commands |
|---|---|---|---|
| `NotASandboxLocalEnvironment` (default) | host `sh -c "cd <cwd> && …"`, native file I/O | **none**: "not a security boundary" | full host env (`stream_process.py:73-79`, no `env=`) |
| `DockerSandbox` | `docker exec` into an **existing, running** container (`docker.py:27-38`) | whatever the container was started with (mounts, network, user) | only explicit `-e` pairs |
| `SshSandbox` | fresh `ssh` per call, `BatchMode=yes`, AppSec-reviewed option allowlist (`ssh.py:19-24,67-78`) | a different machine | only explicit prefix |

The default's own docstring states the posture:

```
:class:`NotASandboxLocalEnvironment` runs commands, code, and file operations
directly on the host with **no isolation**. The deliberately blunt name (...) is a warning:
this is the fallback an :class:`~strands.agent.agent.Agent` uses when no sandbox
is passed, not a security boundary.
```
(`strands-py/src/strands/sandbox/not_a_sandbox_local_environment.py:1-12`; TS equivalent
`strands-ts/src/sandbox/register-node-defaults.ts:7`.)

> 📌 Codex separates two questions. *Where* commands run is the
> [execution-environment topology](../ai-workflow/wiki/concepts/execution-environment-topology.md)
> (`none` / `openai_hosted` / `self_hosted`, [../docs/09-agents-api-environments.md](../docs/09-agents-api-environments.md)).
> *What they may touch there* is an [OS sandbox policy](../ai-workflow/wiki/concepts/os-sandbox-policy.md)
> (`readOnly` / `workspaceWrite` / `dangerFullAccess` / `externalSandbox`), enforced by Seatbelt, bwrap+seccomp,
> or the native Windows sandbox ([../docs/14-windows-sandbox.md](../docs/14-windows-sandbox.md)).
> Strands' `Sandbox` answers only the first question. It has no policy vocabulary, no workspace-write
> mode, and no network switch. Confinement is delegated wholesale to how *you* built the container
> or remote host. The closest Codex analogue is `externalSandbox` everywhere, with the host default
> being `dangerFullAccess`.

### 3.2 What the harness adds: nothing

✅ `create_harness` never sets `sandbox=`. It only forwards a consumer-supplied one to subagent children
(`agent.py:428-429,463`) and drops sandbox-vended duplicate tools (`agent.py:210-213,551`).

✅ The file tools' only guard is `_validate_path` (`harness-py/src/strands_harness/tools/file_tools.py:25-29`), shared with TS `validatePath`:

```python
if not path.startswith("/"):
    raise ValueError(f"The path {path} is not absolute; it should start with '/'.")
if ".." in re.split(r"[/\\]", path):
    raise ValueError("Invalid path: path traversal is not allowed.")
```

It has no workspace root, does not resolve symlinks, and applies no write allowlist. `write(path="/home/u/.bashrc")` is accepted.

❌ The site says "All three take absolute paths and reject path traversal (a `..` segment), so a tool call
**cannot walk outside the intended location** by relative path"
(`site/src/content/docs/user-guide/harness/tools/shell-and-files.mdx:39-40`). The sentence is literally true for
relative paths. But no "intended location" exists in code, and any absolute path reaches the host
filesystem. The same page (l.47-49) and `production.mdx:67-73` do tell users to confine with a sandbox.

### 3.3 The `environment` plugin

✅ Before each user turn it runs `uname -s` and `pwd` through the sandbox. It injects `AGENTS.md` **verbatim up
to 16,000 chars** and links nearby AGENTS.md/README.md files (depth 2), all wrapped in
`<system-reminder>` (`harness-py/src/strands_harness/plugins/environment.py:33,91,106-108`). The TS source
records the trust decision explicitly:

```
`AGENTS.md` contents are injected verbatim — a prompt-injection surface, but repo docs are treated
as trusted, the same files the agent's `read` tool already surfaces, so they aren't escaped.
```
(`harness-ts/src/plugins/environment.ts:15-16`)

## 4. Web tools

- ✅ **`web_fetch`** (`harness-py/src/strands_harness/tools/web_fetch.py`) runs `curl` inside the agent's sandbox by default (l.74-117).
  Under the default sandbox, that is the host. `transport="direct"` uses urllib in-process (l.129-151).
  - URL guard: RFC 3986 characters only, http(s) only, redirects restricted to http(s).
  - Caps: 5 MiB and 50k chars; 15-minute cache.
  - With a `prompt`, a separate small-model `Agent` answers over the page (l.200-204). Its system prompt is "Use only the provided content…" (l.43-47).
  - **With an empty prompt, the raw text returns verbatim to the main agent** (l.197-198). This is documented (`tools/web-access.mdx:24-25`).
  - ⚠️ There is no private-IP or metadata-address block and no untrusted-content framing.
- ✅ **`web_search`**: `True` turns on the *provider-native* search flag, e.g. Anthropic `web_search_20260318` (`models.py:33`), OpenAI Responses, or Gemini GoogleSearch.
  `"exa"` swaps in Exa's hosted MCP server, `https://mcp.exa.ai/mcp` (`tools/web_search.py:24`). It is keyless by default, `EXA_API_KEY` is optional, and it logs a privacy warning (`agent.py:119-124`).

## 5. Subagents and programmatic tool calling

### 5.1 `subagent`

- ✅ Each axis (instructions, tools, mcp_servers, model, context) takes an authority mode, `Fixed`, `Inherit`, `Open`, or `Choice`, which decides whether it becomes a model-facing parameter (`harness-py/src/strands_harness/tools/subagent.py:1-15`).
- ✅ The default `generalist` child is **rebuilt through `create_harness`** from the parent's kwargs, with `session` forced off (`agent.py:446-464`; `subagent.py:687-766`). It therefore inherits interventions, hooks, and sandbox.
- ✅ Tools can only be narrowed (`subagent.py:296-301`). Depth is capped at 2 through `agent.state` (l.462,512-532), and HITL interrupts propagate to the parent (l.556-559).
- ✅ Memory for the child is recall-only at the manager layer (l.743-752). ⚠️ The child still has `write` and `shell`, so it can edit `./.agent/memory/*.md` directly.

❌ The site says the generalist "starts from a blank conversation, so the model must put everything the subtask
needs into the call" (`site/src/content/docs/user-guide/harness/configure/subagents.mdx:61-63`). The tool's own
`task` description repeats it (`subagent.py:203`). But the default tool is built with
`context=Choice(list(_CONTEXT_MODES))`, where the modes are `none`, `all`, and `no_tools` (`subagent.py:765`). The model can therefore choose `"all"`
and fork the parent's full history, tool results included (`_fork_messages`, l.361). `harness-py/docs/subagent.md:105-106`
documents this correctly.

### 5.2 `programmatic_tool_caller`

- ✅ This is code-execution tool calling. Model-written Python runs in **Monty**, pydantic's Rust Python-subset VM (`pydantic-monty==0.0.23`, pinned pre-1.0).
  - In Python it runs in a separate worker process (`tools/programmatic_tool_caller.py:9-14,297-300`).
  - In TS it falls back to **in-process WASM** when the native addon fails to load (`harness-ts/src/tools/programmatic-tool-caller.ts:15-19,118-132`).
- ✅ Limits: 60 s interpreter time, 256 MiB, 1,000 suspensions, 10 concurrent calls, 900 s wall clock (l.43-66).
- ✅ By default it exposes **every registered tool except itself**, `shell` and `write` included (l.208-222). The "no filesystem/network/process" VM therefore removes no capability. The module docstring and `production.mdx:67-70` say so ✅.
- ✅ Interrupt-based HITL cannot prompt from inside a run, so a gated inner call raises (fail-closed) (l.16-20; TS l.351).

## 6. Interventions, memory, todos

- ✅ **`interventions`** accepts `off`, `ask`, `smart`, `*.cedar`, or **any other string, which becomes the LLM risk classifier's system prompt** (`harness-py/src/strands_harness/interventions.py:52-65`). Duplicate handler names raise (l.68-80). See [approval-gate](../ai-workflow/wiki/concepts/approval-gate.md) and [03-tools-and-approval.md](03-tools-and-approval.md).
- ✅ **Memory** is distilled in the background and injected on every model call, with no provenance or trust tag (`memory.py:89`). ⚠️ Content from one hostile page can persist into later sessions.
- ✅ **Todos**: `todo_write` stores the list in `agent.state`. The list is re-surfaced each call as an ephemeral `<system-reminder>` and never written to history (`plugins/todos.py:1-16,74-90`).

## 7. Python ↔ TS parity

✅ Parity is an explicit goal and mostly holds: same defaults, prompt, and summarizer table ("kept byte-identical",
`models.py:60-61`; `harness-ts/src/models.ts:54,64`), and a shared `config.json` schema. Each runtime refuses the other language's
modules (`harness-ts/src/config.ts:651-652`). Known divergences:

| Area | Python | TS | Citation |
|---|---|---|---|
| Anthropic-direct native web search | on | off until SDK 1.19 | `harness-ts/src/models.ts:314-319,338` |
| Subagent interrupts | yield `ToolInterruptEvent` | throw via `toolContext.interrupt` | `harness-ts/src/tools/subagent.ts:17-30` |
| PTC isolation | worker process | worker, or in-process WASM fallback | `programmatic-tool-caller.ts:118-132` |
| Factory | sync | async | `harness-ts/src/agent.ts:364` |

## 8. The `strands` CLI

### 8.1 Shape

- ✅ `@strands-agents/cli` is a Node ≥22, Ink/React TUI that builds the agent **in-process** with `createHarness` (`strands-cli/src/tui/runtime.ts:3,159`).
- Python agent projects run in a spawned `python3 -u worker.py` subprocess over JSONL stdio, with permissions bridged through a `BeforeToolCallEvent` hook (`strands-cli/src/tui/project/python.ts:152-160`; `strands-cli/src/tui/project/worker.py`).
- The only subcommand is `strands update` (a global `npm install`, `src/cli/update.ts:21-60`).
- Modes: `ink`, `plain`, `print` (`-p`, **or any non-TTY stdin**, `src/cli/run.ts:79`), and `acp` (`--acp-server`).
- Session operations are slash commands: `/compact /clear /fork /agents /rename /sessions /tools /skills /mcp /permissions /setup /export …` (`src/tui/chat/commands.ts:8-37`). A `!cmd` escape runs shell without approval (README:139-146).

| Path | Content |
|---|---|
| `~/.strands/cli/config.json` | profile, permissions, settings. Dir 0700, file 0600, atomic rename (`src/tui/config.ts:86-89,488-492`) |
| `~/.strands/cli/trusted-workspaces.json` | project MCP trust (realpath + content digest) |
| `~/.strands/cli/tool-results/` | shell output overflow |
| `./.agent/{sessions,memory,skills}` | per-project harness state |

### 8.2 Approval UX (Ink only)

- ✅ `CedarPermissions` is installed ahead of user interventions (`src/tui/runtime.ts:269-284`).
- The default policy auto-permits only `read` **inside the workspace** (realpath-canonicalized, so symlink-safe), `todo_write`, `retrieve_offloaded_content`, and scoped config drafts (`src/tui/permissions/policy.ts:12-40,180-190,249-256`).
- Every other call gets **Allow once / Always allow tool / Deny**, with a diff preview for writes (l.42-51,207).
- "Always allow" is **per tool name, not per argument** (l.209-211): always allowing `shell` means any command.
- `bypassPermissions` skips everything (l.196-198). It is user-level only; a project config cannot set it (README:391-394).
- Errors deny (l.164).

✅ **Print, plain, and ACP have no gate.** `runConsole` calls `createHarness(options)` without
`CedarPermissions` and without `WorkspaceSandbox` (`src/cli/run.ts:122-165`). `echo "…" | strands` therefore runs
shell and writes on the host unchecked unless `--interventions` is passed. The README states this ✅:
"Plain, print, and ACP server modes have no permission UI and therefore use stock harness tool
behavior" (`strands-cli/README.md:401-402`).

✅ `WorkspaceSandbox` (`src/tui/workspace/sandbox.ts`) is a sandbox by name only. It sets `cwd`,
`resolve(this.cwd, path)` ignores that cwd for absolute paths (l.37-39), and commands spawn with `env: { ...process.env,
...options.env }` (l.75-80). The README says so ✅: "This approval layer is not an operating-system sandbox" (README:399).

✅ **Project MCP trust**: `.mcp.json`, `.codex/config.toml`, and similar files need a y/N prompt, pinned to a content digest.
A change aborts startup (`src/tui/workspace/trust.ts:31-90`). User-level discovery reads *other agents'*
configs (`~/.claude.json`, `~/.codex/config.toml`, `~/.gemini/…`; `src/tui/mcp/config.ts:58-67`). Both MCP and skill discovery are
**off by default** (`src/tui/settings.ts:104-105`). ⚠️ No trust gate was found for `./.agent/skills` or `AGENTS.md`
injection.

## 9. Credentials

- ✅ **Library**: provider SDK defaults (the AWS chain, `*_API_KEY` env vars), plus direct reads of `OLLAMA_*`, `LITELLM_*` (`models.py:251-267`), and `EXA_API_KEY`. Nothing is stored.
- ✅ **CLI**: precedence is process env > session-entered > stored non-secret config > explicit `--env-file` (`src/tui/provider/environment.ts:77-111`). `.env` is never auto-loaded (`config.ts:222-225`).
  Secret keys are **stripped from config.json on load and on every write** (`environment.ts:28-37`; `config.ts:116,491,527-548`). No OS keychain is used.
- ⚠️ **Not shielded from the model.** Resolved values are written into `process.env` (`environment.ts:49-67`; `config.ts:246`), and both `WorkspaceSandbox` and the SDK host sandbox pass the full env to every command. One `shell` call (`env`) exposes them, and `web_fetch` could carry them out.
  The only shielding is advisory prompt text: "Never ask the user to paste credentials into chat…" (`src/tui/configuration-instructions.ts:5`). The config tool redacts its own `inspect` output (`src/tui/agent-configuration.ts:123`).
  Contrast [credential-shielding](../ai-workflow/wiki/concepts/credential-shielding.md). `DockerSandbox` and `SshSandbox` do *not* forward host env (§3.1), so the plane choice is also the secret boundary.

## 10. What this means if you are building a harness

- [ ] Keep *where* (execution plane) separate from *what may be touched* (policy). A `Sandbox` interface without a policy vocabulary silently defaults to full access.
- [ ] Never let the fallback execution environment inherit the host env. Pass an explicit allowlist, as Docker/SSH do here.
- [ ] If the system prompt grants authority to a tag (`<system-reminder>`), escape or strip that tag from every tool result.
- [ ] Give file tools a real workspace root (realpath containment), not just a `..` check. The CLI's `pathIsWithinWorkspace` shows the right primitive, but it is applied only to auto-approving `read`.
- [ ] Headless modes need a policy too. "No UI → no gate" turns piped stdin into full autonomy.
- [ ] Approval grants should be able to scope arguments. Per-tool-name "always allow shell" is total.
- [ ] A code-execution tool that can call every other tool reduces round-trips, not capability. Default its `allowed_tools` narrowly.
- [ ] Treat memory as a persistent injection channel: record provenance, and do not auto-inject untrusted-derived facts.
- [ ] Publish benchmark configs and raw results alongside "benchmarked defaults", with variance.

## 11. Open questions

- ⚠️ None of the injection or exfiltration paths (`<system-reminder>` spoofing, `env` exposure, metadata-IP fetch, memory persistence) was demonstrated. All are source-reading inferences.
- Not read: the SDK `ExtractionConfig` turn interval, `HumanInTheLoop(ask="stdio")` behaviour, and `PosixShellSandbox.write_file` internals.
- Not traced end to end: whether the CLI's async Cedar broker prompts correctly for PTC inner calls and for subagent children in Ink mode.
- Whether `DockerSandbox` users are guided to start containers with no network or read-only mounts. The SDK attaches to an existing container and sets no policy.
- The benchmark source spreadsheets and `strands-labs/benchmark-harnesses` were not inspected.
