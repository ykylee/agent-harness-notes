# 06. Choosing an Integration Path

## 1. Comparison

| Criterion | `codex exec` | Codex SDK | `codex mcp-server` | **App Server** | Agents API |
|---|---|---|---|---|---|
| Form | CLI | TS/Python library | MCP stdio server | JSON-RPC process | Managed HTTPS API |
| Who runs it | Your machine / CI | Your machine | Your machine | Your machine / container | **OpenAI** |
| Surface area | Narrow | Medium | Only what MCP exposes | **Full** | Full (managed) |
| Progress streaming | `--json` JSONL | `runStreamed()` | Limited | 84 notification types | Streaming / webhooks |
| Approval interception | Policy flags only | Policy | Limited | **Live, via server requests** | requires_action |
| Injecting app-owned tools | ✗ | Limited | ✗ | **`item/tool/call`** | Function calls / MCP |
| Auth · model discovery · config management | Partial | Partial | ✗ | **All of it** | Managed |
| Integration cost | Lowest | Low | Low | **High (write bindings)** | Medium |
| Infrastructure you operate | Yours | Yours | Yours | Yours | **OpenAI's** |

## 2. Decision flow

```
Is the agent "the product itself"? (embedded in the UI, approval flows, live streaming)
├─ Yes ──▶ Must you operate the harness? (on-prem / data boundary / custom sandbox)
│          ├─ Yes ──▶ ★ App Server
│          └─ No  ──▶ ★ Agents API
└─ No
   ├─ You already have an MCP workflow and want Codex as one tool ──▶ codex mcp-server
   ├─ You want to call it programmatically from server-side code ──▶ Codex SDK
   └─ You want a one-shot run in CI or a script ──▶ codex exec
```

## 3. OpenAI's official recommendation

> "Codex App Server will be the first-class integration method we maintain moving forward."
> By default, they recommend the App Server.

Their commentary on the trade-offs:

**Using Codex as an MCP server**
> "you only get what MCP exposes, so Codex-specific interactions that rely on richer session semantics
> (e.g., diff updates) may not map cleanly through MCP endpoints."

**Using a cross-provider agent harness protocol (a portable interface)**
> "these protocols often converge on the common subset of capabilities, which can make richer interactions
> harder to represent, especially when provider-specific tool and session semantics matter."
> They add that this space is evolving quickly and expect more common standards to emerge, citing
> skills as a good example.

**The cost of the App Server**
> "The main cost is integration work, since you need to build the client-side JSON-RPC binding in your language.
> In practice, however, Codex is able to do a lot of the heavy lifting if you feed it the JSON schema and documentation."

## 4. App Server integration checklist

### Initial design
- [ ] **Decide your version-pinning strategy** — bundle the binary and pin it (VS Code/Desktop
      approach) vs. keep the client fixed and update only the server (Xcode approach). The protocol
      is backward compatible, so the latter decouples release cycles well.
- [ ] Generate bindings with `codex app-server generate-ts` or `generate-json-schema` — **never hand-write them**
- [ ] Opt into only the capabilities you need in `initialize`
      (`experimentalApi` significantly widens the surface — enable it only when you actually use it)
- [ ] Use `optOutNotificationMethods` to **suppress notifications you don't consume** — you do not
      need to handle all 84

### Rendering
- [ ] Implement the three-stage pipeline in the UI: `item/started` → render a placeholder
      immediately → apply `*/delta` → finalize on `item/completed`. This is how the protocol is
      meant to be consumed
- [ ] Handle `serverRequest/resolved` to clear **approval requests settled through another path**
- [ ] Surface state with `thread/status/changed` and `thread/tokenUsage/updated`

### Approvals / safety
- [ ] You **must** implement `item/commandExecution/requestApproval`,
      `item/fileChange/requestApproval`, and `item/permissions/requestApproval` — without them the
      turn stalls
- [ ] Decisions are `accept` / `acceptForSession` / `decline` / `cancel`, plus the amendment variants
- [ ] Fix the sandbox policy to your product's requirements
      (`readOnly` / `workspaceWrite` / `dangerFullAccess` / `externalSandbox`)

### Errors / resilience
- [ ] Branch on `turn/completed` with `status: "failed"` and `codexErrorInfo`
      (`ContextWindowExceeded`, `UsageLimitExceeded`, `HttpConnectionFailed`, `SandboxError`)
- [ ] For JSON-RPC errors, branch on the **`{type, reason}` values, not message text**
- [ ] Backpressure: `-32001` when the queue saturates → exponential backoff with jitter
- [ ] Design for reconnection — in ephemeral contexts like the web, **keep state on the server** and
      recover by resuming the thread

### Wiring in app-specific capabilities
- [ ] Attach app-owned MCP servers to expose business data and actions
- [ ] Handle the `item/tool/call` server request if you need dynamic tools
- [ ] Use `thread/attachment/*` to link external resources such as PRs and tickets to a thread
      (the whole team must share the identity-key convention for surfaces to agree)

### Pitfalls
- [ ] Most `turn/start` overrides **persist into subsequent turns (sticky)** — revert them if you
      meant one turn only
- [ ] `thread/rollback` is **removed** → use `thread/revert`
- [ ] `disabledPluginIds` is currently **saved but does not actually filter capabilities**
- [ ] A thread with a live internal worker cannot be archived or deleted (`-32600`)
- [ ] `serverCapabilities` from `mcpServerStatus/list` is `null` when initialization failed — never
      infer it from the tool list

## 5. Security notes

- **Separate untrusted content from user input at the type level.** The Python SDK's
  `ExternalMessage` is the model: it retains tool-level authority but confers no user authorization.
- Approval gates are **protocol-level safety mechanisms**, not UI conveniences. If you enable
  auto-approval (`item/autoApprovalReview/*`, `autoApprovalReview/strictReviewRequired`), understand
  the conditions that escalate to strict review.
- A self-hosted Agents API environment is **outbound-only** (`api.openai.com`,
  `wss://codex-cloud-environments.chatgpt.com`), so no inbound ports are needed. Use a **restricted
  executor key.**
- The Agents API currently supports **US data residency only** and **does not support ZDR.**
  A self-hosted sandbox does not confer ZDR eligibility.
