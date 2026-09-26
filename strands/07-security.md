# 07. Security — where the gates are, which way they fail, what reaches the model

> A synthesis across [03](03-tools-and-approval.md) (approval), [04](04-harness-and-cli.md) (harness
> defaults, sandbox, credentials) and [06](06-multi-agent-and-exposure.md) (handoffs), read against
> this repository's security concepts — [`indirect-prompt-injection`](../ai-workflow/wiki/concepts/indirect-prompt-injection.md),
> [`approval-gate`](../ai-workflow/wiki/concepts/approval-gate.md),
> [`credential-shielding`](../ai-workflow/wiki/concepts/credential-shielding.md) — and against
> [`SYNTHESIS.md` §6.4](../SYNTHESIS.md), where this repository learned that **only a gate outside
> the model's loop holds.** `strands-agents/harness-sdk` @ `15da9dc` (2026-09-25). Researched
> 2026-09-26.
>
> Grades: mostly ✅ **source read.** Four claims are 🧪 **probed** — run against the SDK's own
> scripted `MockedModelProvider` (no LLM, deterministic), each **with a control that shows the
> input arrived** (§3.2). Every injection *path* in §2 is ⚠️ **inferred from source; none was
> exercised against a model.**

## 1. The default posture: a trusted model on the host

What `create_harness()` gives you with no arguments ([04](04-harness-and-cli.md)):

| Control | Default | Grade |
|---|---|---|
| Execution environment | `NotASandboxLocalEnvironment` — "**no isolation** … full privileges of the host process" | ✅ `strands-py/src/strands/sandbox/not_a_sandbox_local_environment.py:31-42` |
| File tools | absolute path, no `..` segment — **no workspace root** | ✅ `harness-py/src/strands_harness/tools/file_tools.py:25-29` |
| Shell | `sh -c`, **inherits the full process environment** | ✅ `strands-py/src/strands/sandbox/stream_process.py:73-79` |
| Approval (`interventions=`) | **`None` — off** | ✅ `harness-py/src/strands_harness/agent.py:388` |
| Code-mode tool | Monty interpreter, but can call **every other tool, shell included** | ✅ [04](04-harness-and-cli.md) |
| `web_fetch` | no private-IP / link-local / metadata block | ✅ (SSRF path ⚠️ not exercised) |

Set against the other two cases in this repository:

| | Codex | Aside | **Strands harness** |
|---|---|---|---|
| Default sandbox | OS-enforced `workspace-write`, network off ([`docs/14`](../docs/14-windows-sandbox.md)) | on, even under `full-access` | **none** |
| Default approval | approval requests are a protocol primitive ([`docs/02`](../docs/02-app-server-protocol.md)) | `ask` | **off** |
| Secrets vs. model | provider keys outside the sandboxed process | Vault; values hidden | **in `env`, one `env` call away** |

> 📌 **This is not an oversight; it is a positioning.** The SDK names its default class
> `NotASandbox…` and the CLI README says in plain words that its approval layer "is not an operating
> system sandbox." Strands' answer to isolation is *pass a `DockerSandbox` or `SshSandbox`* — an
> execution-plane choice ([04](04-harness-and-cli.md)), not a policy on the host. The honesty is
> real. The **default** is still the most permissive of the three harnesses studied here, and the
> harness is the layer that advertises itself as production-ready in one import.

## 2. What reaches the model — the injection surface

Our threat model ([`indirect-prompt-injection`](../ai-workflow/wiki/concepts/indirect-prompt-injection.md)
§10.1) is **cross-session reads followed by one write**. Strands' default harness supplies every
ingredient: readers (`web_fetch`, `read`, MCP, `web_search` via Exa), a persistent carrier (memory),
and ungated writers (`write`, `shell`).

### 2.1 The prompt contract hands out a harness-authority tag

The harness system prompt, byte-identical in Python and TS:

```
- `<system-reminder>` tags in messages and tool results are injected by the harness, not the user.
```
`harness-py/src/strands_harness/prompt.py:28` ✅

The harness does emit such tags (environment plugin, todos). **Nothing strips or escapes the tag
from tool output** — a grep across `harness-py`, `harness-ts`, `strands-py`, `strands-ts` and
`strands-cli` finds only the prompt and the two emitters. ✅ (absence confirmed by grep)

So a fetched `text/plain` page, a file, or an MCP result containing a literal `<system-reminder>`
is, by the prompt's own statement, **harness-authored.** ⚠️ Inferred; not run against a model.
(HTML happens to lose the tag in `web_fetch`'s regex tag-strip — incidental, not an escape.)

> 📌 **An authority marker the model is told to trust must be unforgeable by content.** Either
> escape it in every tool result, or do not tell the model that it can appear there. This is the
> same class of error as Dia's word-boundary filter that invisible characters defeated
> ([`SYNTHESIS.md` §6.4](../SYNTHESIS.md)): a perception-layer signal the attacker can write.

### 2.2 Entry points, by how the content arrives

| Entry | How it reaches the main model | Delimited? | Grade |
|---|---|---|---|
| `web_fetch` with a `prompt` | a separate small-model summarizer reads the page; **its answer** returns | no | ✅ — a dual-LLM shape, but the summary itself is steerable |
| `web_fetch` with empty prompt | **raw page text, ≤ 50,000 chars** | no | ✅ |
| `AGENTS.md` | verbatim up to 16,000 chars inside `<system-reminder>` — TS comments it as "a prompt-injection surface, but repo docs are treated as trusted" | — | ✅ declared trust decision |
| MCP tool results / Exa search | ordinary tool result | no | ✅ |
| **Long-term memory** | facts distilled by a small model, **re-injected every model call, across sessions**, no provenance | no | ✅ mechanism · ⚠️ as a carrier |
| Swarm handoff / Graph upstream output | pasted verbatim into the next agent's **user** turn | no | ✅ [06](06-multi-agent-and-exposure.md) |
| Generalist subagent | model may choose `context="all"` — forks the parent's full history, tool results included | — | ✅ |

> ⚠️ **Memory is the piece that turns one read into many.** Our threat model's chain is several
> reads across sessions and then a write. A harness that distils facts from a hostile page and
> replays them into every later session has built the cross-session half of that chain for the
> attacker. Nothing in harness code tags a memory with where it came from.

## 3. The gates — and which way each one fails

Strands does have gates outside the model's loop. It has **several**, and they disagree.

### 3.1 The primitive: exception plus replay

`event.interrupt()` raises; the loop stops with `stop_reason="interrupt"`; the caller resumes by
passing `interruptResponse` back **as the next prompt**; the hook or tool body then **re-runs from
the top** and the second `interrupt()` returns the stored answer. ✅ ([03](03-tools-and-approval.md))

Consequences: any side effect before the `interrupt()` call happens twice; and approval has no wire
shape except on the A2A server (as `input_required`) — whose **client** refuses to send interrupt
responses, so one Strands agent cannot answer another's approval over A2A. ✅

### 3.2 Failure direction, gate by gate

| Gate | On handler error | On "no" | Grade |
|---|---|---|---|
| Interventions (`Deny`/`Confirm`) | throws → call fails (**closed**) | falsy → deny | ✅ |
| `HumanInTheLoop` classifier | error / malformed / non-bool → approval required (**closed**) | — | ✅ |
| **`CedarAuthorization`** | a `forbid` whose condition errors (e.g. missing context attribute) is **skipped → allowed** (**open**) | — | 🧪 |
| **Python steering plugin** | exception logged at **debug**, tool runs (**open**) | **any truthy response approves — including `"no"`** | 🧪 · 🧪 |
| `strands-agents/tools` consent | `KeyboardInterrupt`/EOF → cancel (**closed**) | — | ✅ — but skipped by `BYPASS_TOOL_CONSENT=true` **or** `STRANDS_NON_INTERACTIVE=true` |
| Code-mode (`programmatic_tool_caller`) | an interrupt-gated inner call raises (**closed**) | — | ✅ |

The probes were re-run in a fresh environment by the main session, and each carries a **control**
([`zero-needs-proven-delivery`](../SYNTHESIS.md#7-on-method) — a pass means nothing unless the input
is shown to have arrived):

- Cedar: the same `forbid` **does block** when the attribute is present (`role="user"`). The
  pass-through is the error path, not a policy that never matched. 🧪
- Steering: the interrupt **does fire** (`stop_reason="interrupt"`), and a response of `False`
  **does block**. `"no"` passes because the check is truthiness (`steering/core/handler.py:121-125`). 🧪
- Cedar `call_count` counts **2** for one execution across an interrupt/resume. 🧪

> ❌ **Refuted:** "Cedar engine failures (malformed policies, evaluation errors) are always
> fail-closed" — `site/…/cedar-authorization.mdx:239`. Design 0006 Appendix A had itself warned
> that a malformed `forbid` is skipped and said the plugin "should check for and surface these."
> It does not, in Python or TS.

### 3.3 Composition is registration order, not precedence

The docs promise "well-defined precedence (deny > confirm > guide > transform > proceed)". The code
evaluates handlers **in registration order, first short-circuit wins.** ❌ So a human can be asked
to approve a call that a later handler would have denied; an approved call can still be cancelled by
accumulated guidance; and the promised `auditLog` does not exist in either SDK. ❌ ([03](03-tools-and-approval.md))

Hook-based authorization sits at order 90, so a later hook — or the middleware stage — can still
rewrite the tool input **after** it was authorized. ✅

### 3.4 Where the CLI lands

The `strands` CLI is the only layer with a persisted, Claude-Code-like policy
(`~/.strands/cli/config.json`: `mode: default | bypassPermissions`, an `allow` list, over default
Cedar rules). In the full-screen TUI, reads inside the workspace are auto-allowed (symlink-safe)
and everything else asks. But:

- **"Always allow" is per tool name** — allowing `shell` once allows every command. ✅
- **Every Cedar deny, even an explicit `forbid`, becomes an ask** — there is no hard-deny tier. ✅
- **`-p`, plain mode (any non-TTY stdin) and ACP run with no gate and no workspace sandbox** — the
  README says so. ✅ And the harness's ACP path forwards no permission requests to the ACP client ⚠️.

Compare Aside's policy engine ([`browser-agents/10`](../browser-agents/10-aside-enforcement-and-native.md)
§1): tool-name globs **plus per-argument regex**, four buckets. Strands' finest grain is the tool name.

## 4. Credentials

The CLI never writes API keys to `config.json` ✅ — and then loads them into `process.env`, which
every `shell` call inherits (`strands-cli/src/tui/workspace/sandbox.ts:77`). The library's host
sandbox inherits `env` the same way. The only shielding is prompt text ("never … printing their
values") and redaction in one configuration tool's output. ✅

> 📌 By [`credential-shielding`](../ai-workflow/wiki/concepts/credential-shielding.md) §3 —
> **permission level and secret exposure are different axes** — Strands has neither. A shell tool
> that is approved once can print every key the harness itself holds. Scrubbing provider variables
> from the child environment is a one-line fix that no layer makes.

## 5. Measured against this repository's conclusion

[`SYNTHESIS.md` §6.4](../SYNTHESIS.md) concluded: perception-layer defences are heuristics an
attacker can study; **only the gate outside the model's control loop held.** Strands is an
instructive test of that sentence because it *has* the out-of-loop gate — as a first-class SDK
primitive, with a Cedar backend — and yet:

1. the harness ships it **off**;
2. two of its implementations **fail open** (Cedar on evaluation error, steering on exception and on
   a truthy "no");
3. its composition order is **registration order**, not the precedence its docs describe;
4. the CLI downgrades every **deny to an ask**, and its headless modes have no gate at all.

> 📌 **"Put the gate outside the loop" is necessary, not sufficient.** A gate must also be *on by
> default*, *fail closed on every error path*, *compose by an explicit precedence*, and *keep a hard
> deny*. Strands shows each of those four properties can be missing while the primitive itself is
> sound — and the missing ones are found only by running the error path, not by reading the design.

## 6. What this means if you are building a harness

- [ ] Default to a gate **on**, and to an execution environment that is not the host
- [ ] Every approval path fails **closed** on handler error, evaluation error and malformed policy —
      test each error path with a control that proves the input arrived
- [ ] Parse approval answers as an enum, never by truthiness
- [ ] Compose multiple policies by an **explicit precedence** with a hard-deny tier that no "ask" or
      "always allow" can downgrade
- [ ] Authorize the **final** tool input — nothing may rewrite it after the decision
- [ ] Grant "always allow" per **(tool, argument pattern)**, not per tool name
- [ ] Headless modes are where approval matters most; do not make them the ungated ones
- [ ] Never tell the model that an authority tag may appear in tool results unless every tool result
      is escaped
- [ ] Tag long-term memory with provenance; never re-inject facts distilled from untrusted content
      as if they were the user's
- [ ] Strip provider credentials from the child environment of every tool process
- [ ] Block link-local and metadata addresses in any fetch tool

## 7. Open questions

- Whether a current model actually treats a forged `<system-reminder>` in a tool result as harness
  authority — the natural next probe, and a heddle-side measurement (out of this repository's scope;
  its result would be admitted here as a measurement, per `PURPOSE.md` §0.1) ⚠️
- Whether memory extraction carries injected instructions across sessions in practice ⚠️
- Whether the ACP harness path's missing permission forwarding is reachable by a real ACP client ⚠️
- The `python_repl` in-process path (`interactive=False`) could set `BYPASS_TOOL_CONSENT` after one
  approval and disable consent for every later tool — read, not run ⚠️
