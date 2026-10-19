# Claude Code, read as an engine

> **What this is.** The second engine-level case in this repository, read the way the Codex harness
> was read in [`docs/`](../docs/): from the generated contract rather than the prose. For Codex that
> contract was the App Server's generated schema; for Claude Code it is the Agent SDK's generated
> types — `@anthropic-ai/claude-agent-sdk` **0.3.303** (published 2026-10-18), `sdk.d.ts` 10,128 lines
> and `sdk-tools.d.ts` 4,222 — read beside the official documentation as Markdown
> (`code.claude.com/docs/en/*.md`, read 2026-10-19) and the strings of the **2.1.303** binary's 2,435
> split modules ([`harness-artifacts/01`](../harness-artifacts/01-single-file-executables.md) §1).
>
> **Why.** Until now Claude Code appeared here only as what other things embed or render: Dia's bundled
> agent-server, Claude Desktop's Code tab, the playbook's control ladder, the shipped binary's layout.
> [`SYNTHESIS`](../SYNTHESIS.md) §2.9 ("one engine, many clients") needed the second engine at wire
> level, not at the level of a desktop shell. [`PURPOSE.md`](../ai-workflow/memory/active/PURPOSE.md) §0.8.
>
> **Not run, and quoted at identifier level.** Nothing was executed. Claude Code ships under
> Anthropic's commercial terms; the split modules are not committed and are cited by chunk name with
> short strings only. The types and the docs are quoted freely.

> **Drift 2026-10-19 (late) — SDK 0.3.304 / CLI 2.1.304.** Both shipped within a day of the baseline.
> No control subtype, message type, option or tool schema changed; the typed delta is context-usage
> row ids, start-up marks and timeouts, no-deadline dialogs, and browser SSE suspend/resume. The
> approval wire's string counts are identical; 2.1.304 adds a mod's `decider: "person"`. Two of this
> folder's own sentences were refuted by the re-read (three "missing" subtypes were spelled
> `A("…")`; the "untyped" `can_use_tool` fields come from the engine, not the desktop shell).
> Record: [`99`](99-sources.md) §D–§E. Current baseline: **0.3.304 / 2.1.304 / docs 2026-10-19 late**.

## ⚠️ Read status

**Static only.** The `.d.ts` files are the contract; the docs are the vendor's description; the
bundle's strings show what the binary carries beyond both. What any of it does at runtime —
timeouts firing, prompts parking, classifier verdicts — is ⚠️ unless a doc page states it and is
quoted as 📣. Three subagents read the three documents in parallel from the same sources on
2026-10-19; the counts in [01 §7](01-wire-protocol.md) were produced by grep over `sdk.d.ts` and the
bundle and are reproducible from the package tarball and `scripts/bun_split.py`.

## Documents

| # | Document | Subject |
|---|---|---|
| 01 | [The wire](01-wire-protocol.md) | stream-json as type-tagged JSONL; three transports (stdio, browser WebSocket/SSE, the Remote Control bridge); `query()`'s 69 options; `initialize` as configuration injection; the 39-member `SDKMessage` union; 40 typed control subtypes and 13 engine→client requests; session identity; how the SDK packages the engine; what the binary runs beyond the types |
| 02 | [Approval and permissions](02-approval-and-permissions.md) | the six-stage decision pipeline; the `can_use_tool` request and `PermissionResult` answer; six modes and the auto-mode classifier; 33 hook events and their exit-code semantics; managed settings and the keys only policy can set; the sandbox; the seven gate properties graded |
| 03 | [Sessions, context and clients](03-sessions-context-and-clients.md) | JSONL transcripts and what a line holds; resume / branch / fork / rewind; retention (no unload timer); what loads at start; compaction triggers incl. idle compaction; what breaks the prompt cache; auto memory and the undocumented index recall; twelve clients and where the engine runs for each; multi-session rules; cost on the wire; drift between docs, SDK and binary |
| 99 | [Sources](99-sources.md) | the package, the docs pages, the binary, counts, grades |

## Five things this reading settled

1. **The wire is flat where Codex's is layered.** No Thread/Turn/Item: a message is the item,
   `result` closes the turn, `session_id` is the thread, and `conversation_reset` swaps the thread
   inside a running process. The one control-request union does not encode direction
   ([01 §1](01-wire-protocol.md)).
2. **`initialize` injects, it does not negotiate.** A client hands the engine its hooks, in-process
   MCP servers, agents, skills and plugins and gets back the catalog built from them, plus
   `claude_code_version`. The only self-declaration is `supportedDialogKinds` ([01 §2.4](01-wire-protocol.md)).
3. **An approval can rewrite the input, not only the policy.** `PermissionResult.allow` carries
   `updatedInput` and `updatedPermissions` (rules, mode, directories, each with a persistence
   `destination`); `decision_reason_type` is an enum a host can branch on. Codex's `ReviewDecision`
   carries the policy amendment but never the rewritten command ([02 §2](02-approval-and-permissions.md)).
4. **The gate is fail-closed inside the engine and fail-open by default in the hook layer.** A
   `null` callback result blocks forever, a schema-invalid one becomes deny, a silent classifier
   denies; a missing hook script, a timed-out hook and a non-0/2 exit code all let the call proceed
   unless `onFailure: "block"` (2.1.295+) is set. The interactive default reviewer is a model
   (`auto`) ([02 §7](02-approval-and-permissions.md)).
5. **Twelve clients, two places the engine runs.** Terminal, SDK, Desktop, VS Code, Remote Control,
   channels, cross-session messaging, agent teams, workflows, deep links and agent view all drive a
   **local** engine; only cloud sessions run it elsewhere, and `--teleport` copies a conversation
   down one way. No other session can answer a permission prompt for you; the only exceptions are
   human paths (a channel's allow-listed sender, a Remote Control device)
   ([03 §3–§4](03-sessions-context-and-clients.md)).

## What this does to earlier notes

- [`SYNTHESIS`](../SYNTHESIS.md) §2.9's Claude row is restated at wire level (this folder is its
  evidence); §2.7's seventh property gets a second engine's reading.
- [`ai-sdlc/03`](../ai-sdlc/03-the-control-ladder.md) and `approval-gate` §7.8 ("a hook that
  blocks only when it runs") gain the 2.1.295 `onFailure: "block"` switch and the typed
  `permissionDecision` precedence.
- [`harness-artifacts/03`](../harness-artifacts/03-tool-use-patterns.md) §2's bundle reading is
  now anchored to the SDK types it implements.
