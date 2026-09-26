# 03. Codex SDK (TypeScript / Python)

> Drift-checked against `openai/codex@e72da2b538` (2026-09-26); changes marked *(2026-09-26)*.

The SDKs are wrappers that **spawn the `codex` CLI as a child process** and give you a native
library interface without writing a JSON-RPC client. *(corrected 2026-09-26: the transports differ —
the TypeScript SDK runs `codex exec --experimental-json` and reads JSONL events
(`sdk/typescript/src/exec.ts:92`); the Python SDK runs `codex app-server --listen stdio://` and
speaks App Server JSON-RPC (`sdk/python/src/openai_codex/client.py:256`).)*

## 1. TypeScript SDK

### Installation

```bash
npm install @openai/codex-sdk    # Node.js 18+
```

### Basics

```typescript
import { Codex } from "@openai/codex-sdk";

const codex = new Codex();
const thread = codex.startThread();
const turn = await thread.run("Diagnose the test failure and propose a fix");

console.log(turn.finalResponse);
console.log(turn.items);
```

Call `run()` repeatedly on the same `Thread` instance to continue that conversation.

```typescript
const nextTurn = await thread.run("Implement the fix");
```

### Streaming

`run()` buffers events until the turn finishes. To react to intermediate progress — tool calls,
streaming responses, file change notifications — use `runStreamed()`:

```typescript
const { events } = await thread.runStreamed("Diagnose the test failure and propose a fix");

for await (const event of events) {
  switch (event.type) {
    case "item.completed":
      console.log("item", event.item);
      break;
    case "turn.completed":
      console.log("usage", event.usage);
      break;
  }
}
```

> Note the event names use **dot notation (`item.completed`)**, not the App Server's
> `item/completed`. The SDK exposes its own event surface.

### Structured output

```typescript
const schema = {
  type: "object",
  properties: {
    summary: { type: "string" },
    status: { type: "string", enum: ["ok", "action_required"] },
  },
  required: ["summary", "status"],
  additionalProperties: false,
} as const;

const turn = await thread.run("Summarize repository status", { outputSchema: schema });
console.log(turn.finalResponse);
```

Converting from Zod requires `zod-to-json-schema` with `target: "openAi"`:

```typescript
const schema = z.object({
  summary: z.string(),
  status: z.enum(["ok", "action_required"]),
});

const turn = await thread.run("Summarize repository status", {
  outputSchema: zodToJsonSchema(schema, { target: "openAi" }),
});
```

### Attaching images

Text entries are concatenated into the final prompt; image entries are passed to the CLI via `--image`.

```typescript
const turn = await thread.run([
  { type: "text", text: "Describe these screenshots" },
  { type: "local_image", path: "./ui.png" },
  { type: "local_image", path: "./diagram.jpg" },
]);
```

### Resuming a thread

Threads are persisted in `~/.codex/sessions`.

```typescript
const savedThreadId = process.env.CODEX_THREAD_ID!;
const thread = codex.resumeThread(savedThreadId);
await thread.run("Implement the fix");
```

### Working directory

Defaults to the current directory, and **requires a Git repository to avoid unrecoverable errors.**

```typescript
const thread = codex.startThread({
  workingDirectory: "/path/to/project",
  skipGitRepoCheck: true,
});
```

### Controlling the CLI environment (for sandboxed hosts like Electron)

```typescript
const codex = new Codex({
  env: { PATH: "/usr/local/bin" },
});
```

The SDK injects its required variables (such as `CODEX_API_KEY`) on top of what you provide.
If you set `baseUrl`, it is passed as a `--config openai_base_url=...` override.

### `--config` overrides

A JSON object is flattened into dotted paths, serialized as TOML literals, and passed as repeated
`--config key=value` flags:

```typescript
const codex = new Codex({
  config: {
    show_raw_agent_reasoning: true,
    sandbox_workspace_write: { network_access: true },
  },
});
```

Keys that cannot be expressed as dotted paths go through `configOverrides` as raw TOML:

```typescript
const codex = new Codex({
  config: { default_permissions: "audit" },
  configOverrides: ['permissions.audit.filesystem={":root"="read","/path/to/project/.env"="deny"}'],
});
```

**Precedence**: structured `config` → raw `configOverrides` → SDK-managed settings (`baseUrl`) and
thread options (later wins).

## 2. Python SDK

### Installation

```bash
pip install openai-codex    # Python 3.10+
```

The matching `openai-codex-cli-bin` runtime dependency installs automatically; stable SDK releases
track the corresponding stable CLI release.

### Basics

```python
from openai_codex import Codex

with Codex() as codex:
    thread = codex.thread_start()
    result = thread.run("Explain this repository in three bullets.")
    print(result.final_response)
```

`thread.run(...)` returns a `TurnResult` containing the final response, collected items, and token
usage. Plain strings are shorthand for `TextInput(...)`. `ImageUserInput` remains the image-input
type name (preserved across the v2 `ImageReference` change, #45796, 2026-09-26).

*(2026-09-26, #45809)* `Personality` is still exported, but `Personality.friendly` /
`Personality.pragmatic` are deprecated and no longer select a style; `Model.supports_personality`
is always `False`.

### Sandbox presets

```python
from openai_codex import Codex, Sandbox

with Codex() as codex:
    thread = codex.thread_start(model="gpt-5.6-terra", sandbox=Sandbox.workspace_write)
    thread.run("Make the requested changes.")
    review = thread.run("Review the diff only.", sandbox=Sandbox.read_only)
```

| Preset | Meaning |
|---|---|
| `Sandbox.read_only` | Read files without allowing writes |
| `Sandbox.workspace_write` | Read, and write inside the workspace and configured writable roots (the normal default) |
| `Sandbox.full_access` | No filesystem restrictions |

**A turn-level override also applies to subsequent turns** — the same sticky semantics as the
App Server.

### Streaming / steering / interrupting

`Thread.run(...)` waits for completion. When you need to stream, steer, or interrupt, use
`Thread.turn(...)` to get a **`TurnHandle`**.

### Untrusted input — `ExternalMessage`

**Untrusted content** from another agent, tool, or application must be passed as an
`ExternalMessage`.

> It retains tool-level authority and **does not establish user authorization or approval.**
> Plain strings and `TextInput` represent *user* input.

This is prompt-injection defense expressed at the type level — worth honoring strictly in practice.

### Authentication

```python
# ChatGPT browser login
with Codex() as codex:
    login = codex.login_chatgpt()
    print(login.auth_url)
    print(login.wait().success)

# Device code
with Codex() as codex:
    login = codex.login_chatgpt_device_code()
    print(login.verification_url, login.user_code)
    login.wait()

# API key
with Codex() as codex:
    codex.login_api_key("sk-...")
    print(codex.account().account)
```

Existing Codex authentication is reused automatically.

### Async

```python
import asyncio
from openai_codex import AsyncCodex, Sandbox

async def main() -> None:
    async with AsyncCodex() as codex:
        thread = await codex.thread_start(sandbox=Sandbox.workspace_write)
        result = await thread.run("Continue where we left off.")
        print(result.final_response)

asyncio.run(main())
```

### Resuming a thread

```python
with Codex() as codex:
    thread = codex.thread_resume("thr_123")
    print(thread.run("Continue where we left off.").final_response)
```

### Built-in help

```python
import openai_codex
from openai_codex import Codex, CodexConfig
help(openai_codex); help(Codex); help(CodexConfig)
# or: python -m pydoc openai_codex
```

## 3. SDK vs. App Server

A candid assessment from the blog post:

> Since the Codex SDK **shipped earlier** than the App Server, it currently supports fewer languages
> and a smaller surface area. If there is developer interest, we may add additional SDKs that wrap
> the App Server protocol so teams can cover more of the harness surface without writing JSON-RPC
> bindings.

In other words the relationship is **SDK ⊂ App Server**. *(corrected 2026-09-26: the "rebuilt on
top of the App Server later" possibility already holds for Python — the Python SDK is an App Server
JSON-RPC client over stdio; only the TypeScript SDK still wraps `codex exec`.)*
