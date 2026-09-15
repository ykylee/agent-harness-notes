# 11. Agents API — Webhooks, Observability, Tracing, and Cost

> Source: the official guides `agents-api/sessions/webhooks`, `agents-api/observability`,
> `agents-api/tracing`, read as raw Markdown. Extracted 2026-09-15.

## 1. API key scopes

A restricted application key needs:

| Scope | For |
|---|---|
| `api.agents.read` | Reading sessions, turns, items, artifacts |
| `api.agents.write` | Creating sessions and submitting input |
| `api.responses.write` | Inference |
| `api.vaults.read` / `api.vaults.write` | Managing vaults (only if you use them) |

Separately, the executor uses an **environment key** as `CODEX_API_KEY`, which authorizes nothing but
connecting environments.

## 2. Webhooks

Respond to session state changes **without keeping an event stream open**.

### Supported events (5)

| Event | When it fires |
|---|---|
| `agent.session.created` | A session is created |
| `agent.session.action_required` | The session needs a function result, an initial environment connection, or a reconnection |
| `agent.session.in_progress` | The session starts processing a turn |
| `agent.session.idle` | The session is idle and ready for more input |
| `agent.session.failed` | The session enters a failed state |

> **Name mismatch to watch for**: the webhook is `agent.session.action_required`, while the *stream*
> reports the same condition as **`agent.session.requires_action`**. Two different names for one thing.

### What the payload contains

`agent.session.action_required` includes the session ID and a `required_action.type` of
`function_call` or `environment_connection`.

> **The webhook does not include the details.** Retrieve the session and inspect `required_actions`
> for call IDs, arguments, or environment IDs.

For self-hosted sessions, `agent.session.created` includes the environment ID and connection URL:
set `ENVIRONMENT_ID` from `data.environment_id` and `REMOTE_URL` from `data.connect.remote_url`
(the same URL returned as `environment.remote_url` on the session). **Save both and reuse them on reconnect.**

### Setup

Create an endpoint through the shared webhook setup flow, select the Agents API events, and store
the signing secret for signature verification. OpenAI sends a signed HTTP POST per event.

Environment variables in the reference handlers: `OPENAI_API_KEY`, `OPENAI_WEBHOOK_SECRET`.
Python needs `fastapi`, `uvicorn`, `openai`; JavaScript needs `express`, `openai`. Default port 8000.

> In production, **queue slower work** rather than doing it inside the handler.

## 3. Observability

Four things you can do:

1. View session logs in the Platform dashboard
2. Follow the session through its events and saved history
3. Inspect turns and identify delegated command execution
4. Review recorded token usage for root-agent and subagent turns

### Dashboard

[platform.openai.com/logs?api=agents](https://platform.openai.com/logs?api=agents) → **Agents** tab.
Search by session ID to inspect turns, tool calls, and subagents.

> **Trace retrieval and external trace exporters are not part of the public beta API.**
> "Detailed trace retrieval is not available through an ordinary project API key. Dashboard trace
> endpoints require separate access and are not a supported customer API."

### Event stream

> The stream stays open across idle events so you don't miss queued work.

### Pagination for turns and items

Use the returned `last_id` as the next page's `after` value when `has_more` is `true`.

### Attributing a command to an agent

Command items contain `turn_id`. Retrieve that turn and read `subagent_id`:
**`null` identifies root-agent work.**

> **Command-output truncation is not reported** by the customer API.

## 4. Tracing

**Tracing is enabled by default for new sessions.** The public beta API exposes no tracing
configuration and no external trace exporters — it is a dashboard feature.

### Hierarchy

```
Session  ── conversation and work; several turns
└─ Turn  ── one cycle of work; several model responses and tool calls
   └─ Span ── one recorded step, grouped under the agent that performed it
```

### Span types

| Span | What you inspect |
|---|---|
| **Agent** | Agent type (`root` or `subagent`), its ID/name/model/instructions, recorded token usage, duration, outcome status |
| **Generation** | The recorded input and output for one model response |
| **Tool** | Which tool was called, the arguments sent, and the result when available |

> **An Agent span's usage covers that agent only — it does not include its subagents.**
> Sum across spans when attributing cost.

The session summary shows status, model, start time, last activity, number of turns, and recorded
token usage.

## 5. Model usage and cost

Billing follows the model's normal token pricing and prompt-caching rules, as in the Responses API.

### What contributes

| Category | Includes |
|---|---|
| **Input tokens** | Agent instructions, tool definitions, conversation history, user input, files or images, tool results |
| **Cached input tokens** | Input reused from a matching prompt prefix, billed at the cached-input rate |
| **Output tokens** | Generated text, tool-call arguments, and reasoning |

> **Reasoning tokens are billed as output tokens.**

Account for root-agent **and** subagent work, **including retries**, plus any tool, sandbox compute,
and third-party service charges.

### A real gap in the usage fields

> For models with cache-write pricing, writing input to the cache also has a cost.
> **The Agents API usage fields do not expose a separate cache-write count**, so they cannot determine
> the exact model charge when that pricing applies.

Budget for this rather than deriving exact costs from `usage`.

### Prompt caching

Agents carry context forward within a session, so successive calls often share a prompt prefix.

> The model generates a new response; **caching does not replay an old answer.**
> **Maintaining a session does not guarantee a cache hit** — reuse depends on a matching prefix and
> the model's cache eligibility and lifetime rules.

Practical guidance:
- Keep initial **instructions and tool definitions stable**
- Put new task details in **follow-up messages**
- With **tool search**, discovered definitions are appended at the end of the conversation,
  preserving earlier content for cache reuse

> **"A high cached-input percentage does not measure savings on the total task cost."**

### Token usage shape

```ts
TokenUsageResource = {
  input_tokens: number,
  input_tokens_details: { /* includes cached */ },
  output_tokens: number,
  output_tokens_details: { /* includes reasoning */ },
  total_tokens: number,
}
```

Present on both `SessionResource` and `TurnResource`, **best-effort**, `null` when unknown,
and **may change after the fact**.

## 6. Operational checklist

- [ ] Grant the application key only `api.agents.read` / `api.agents.write` / `api.responses.write`
- [ ] Keep the application key **out of** the environment; use an environment key for the executor
- [ ] Subscribe to `agent.session.action_required` **and** `agent.session.failed` if you manage compute
- [ ] Remember the webhook/stream name split: `action_required` vs `requires_action`
- [ ] Always **retrieve the session** after a webhook — the payload carries no details
- [ ] Return 2xx from the webhook **only after queuing succeeds**
- [ ] Page turns and items with `last_id` → `after` while `has_more`
- [ ] Sum Agent-span usage across root and subagents; don't read a parent span as a total
- [ ] Treat `usage` as best-effort and mutable; don't bill customers directly from it
- [ ] Keep instructions and tool definitions stable to preserve cache prefixes
