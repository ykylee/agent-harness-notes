# 04. `codex exec` — Non-Interactive Mode

Runs Codex from scripts and CI/CD without the interactive terminal UI. It fits the case where you
want "a single command that runs to completion non-interactively, streams structured output for
logs, and exits with a clear success or failure signal."

## Installation

```bash
# macOS / Linux
curl -fsSL https://chatgpt.com/codex/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"

# Package managers
npm install -g @openai/codex
brew install --cask codex
```

The standalone installers download from `https://releases.openai.com/codex` by default and fall
back to GitHub Releases. To force GitHub Releases, set `CODEX_INSTALLER_USE_RELEASES_OPENAI_COM=false`.

## Basic usage

```bash
codex exec "your task prompt here"
```

- Progress → **stderr**
- Final output → **stdout** (pipeable)

```bash
codex exec "generate release notes" | tee output.md
```

## Permissions / sandbox

The default is **read-only**. You must raise it explicitly.

| Flag | Meaning |
|---|---|
| (default) | Read-only. Safe for inspecting code |
| `--sandbox workspace-write` | Allow file edits |
| `--sandbox danger-full-access` | Full access. Use cautiously |

`--full-auto` is **deprecated** — use explicit sandbox flags.

## Machine-readable output

```bash
codex exec --json "analyze repo" | jq
```

Emits thread-started, turn, item, and error events as JSON Lines, one per line.

## Structured responses (schema-constrained)

```bash
codex exec "extract metadata" --output-schema schema.json -o output.json
```

## Resuming a session

```bash
codex exec resume --last "continue with next step"
```

Resumes a previous run for multi-stage pipelines.

## CI authentication

Avoiding API keys in the job environment is preferred.

- GitHub Actions → [openai/codex-action](https://github.com/openai/codex-action)
- Single invocation → `CODEX_API_KEY=<key> codex exec "task"`

## Other CLI modes

| Command | Purpose |
|---|---|
| `codex` | Interactive TUI |
| `codex app` | Desktop app experience |
| `codex exec` | Non-interactive |
| `codex app-server` | The App Server process (JSON-RPC) |
| `codex app-server generate-ts` | Generate TypeScript protocol definitions |
| `codex app-server generate-json-schema` | Generate a JSON Schema bundle |
| `codex debug app-server send-message-v2 "<msg>"` | Dump the full JSON traffic of one turn |
| `codex mcp-server` | Expose **Codex as an MCP server** (callable as a tool from MCP clients) |
| `codex exec-server` | **Self-hosted executor** (for Agents API self-hosted sandboxes) |

## When to use `codex mcp-server`

A good fit if you already have an MCP-based workflow and want to invoke Codex as a callable tool.
The downside: **you only get what MCP exposes.** Codex-specific interactions that rely on richer
session semantics — diff updates, for instance — may not map cleanly through MCP endpoints.
(OpenAI themselves abandoned the MCP approach for the VS Code extension and built the App Server.)
