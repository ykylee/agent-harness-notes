# 03. The control ladder

The playbook's useful split, stated in its own words and then checked where a Claude Code doc was
opened. Read date for both doc pages: **2026-10-06**. Docs at `code.claude.com` carry many
"before v2.1.x" notes. A version pin in the playbook's example
(`requiredMinimumVersion` `"2.1.193"`) is that example's floor, not a current version.

## Five rungs

| Rung | What it is on the page | What it can force |
|---|---|---|
| `CLAUDE.md` | Context read at the start of every session. Under a page. A repeated mistake is written back into it | Nothing. A stale line spends context. A missing line is a miss the session will not notice |
| Skill | Advisory. Frontmatter says when it triggers. Invocations show up in session traces | Likelihood. The page says nothing forces compliance |
| Hook | A script on a tool call. Team copy in `.claude/settings.json`. Non-negotiable copy in managed settings | A block, when the hook actually runs and exits 2 or returns deny. See the fail-open rows below |
| Human gate the writer cannot pass | Branch protection requires a code owner. Findings do not approve. A production deploy waits on a named release manager | The approval the agent is not allowed to grant itself |
| Managed settings | MDM or the admin console. The engineer cannot widen permissions, swap the hooks, sideload a plugin, or add an MCP server | Whatever those keys actually enforce. The page's JSON was not executed and was not checked key by key |

This is the same split [`docs/07`](../docs/07-harness-engineering.md) draws for Codex, with
different names. There, `AGENTS.md` is a short map and custom linters enforce invariants, with the
remediation written into the lint error so the agent can read it. Here, `CLAUDE.md` is the map and
the hook's stderr is the remediation. OpenAI's recurring cleanup PR and this page's scheduled
scan are the same job: drift is collected by a job that can only propose a change.

The approval-gate concept in this repository already requires the gate to fail closed, to name
what is being approved, and to be something the writer cannot satisfy alone. The playbook is a
Claude Code instance of that requirement. It is not a new property of the gate.

## Exit 2, checked

Hooks reference, <https://code.claude.com/docs/en/hooks>, read 2026-10-06.

The playbook's production-gate script exits 2 to block and exits 0 otherwise, and its comment says
exit 2 blocks the action and the stderr message goes to Claude. Against the reference:

- **Exit 2 is a blocking error.** On `PreToolUse` it blocks the tool call. JSON cannot override that block: a `permissionDecision` of `"allow"` on stdout still loses to exit 2. ✅ for the playbook's comment.
- **Exit 0 with no decision is not an approval.** The reference: staying silent does not approve the call. The normal permission flow continues. ✅, and stronger than the playbook's script needs to be.
- **Exit 1 does not block.** For most events the only exit code that blocks by itself is 2. A conventional failure code proceeds, and the transcript shows a non-blocking hook error. The playbook's script uses 2, so this does not break the example. It does mean a hook written to the usual Unix habit is not a gate.
- **A hook that never starts is not a gate.** A missing or non-executable script exits like 127 and is a non-blocking error. The reference says a mistyped path leaves the gate silently disabled. The playbook does not say this.
- **A timed-out command, HTTP, or MCP-tool `PreToolUse` hook does not block.** The call continues through the normal permission flow. An Agent SDK callback hook that times out does block. The playbook does not distinguish these.
- **`PermissionRequest` does not honor exit 2.** Deny has to be the decision object. The playbook's example is `PreToolUse`, so the example still matches. A gate hung on the wrong event would not.
- **Decisions, when several hooks disagree:** `deny` > `defer` > `ask` > `allow`. Exit 2 is routed as deny. ✅ as the reference, not stated on the playbook.
- **`PreToolUse` does not fire for an `@` file mention.** The contents are inserted while the prompt is built. A `Read` deny rule is what blocks that path. The playbook's "secrets stay out of context" deny list is the mechanism that covers it; a `PreToolUse` hook on `Read` does not.
- **A hook `allow` does not approve `rm` / `rmdir` of a critical path.** Permission-modes page. The playbook's script does not claim otherwise.
- **Deny rules block in every mode, including `bypassPermissions`.** Permission-modes page. A hook deny is the hook's own decision; the permission-rule deny is a separate control. Both are harder than a skill.
- **`allowManagedHooksOnly` exists** in the reference's managed-settings discussion: user, project, local, and plugin hooks are blocked, with an exemption for plugins force-enabled in managed settings. `disableAllHooks` in user, project, or local settings cannot turn managed hooks off. The playbook's "engineers cannot switch them off" matches that sentence. The rest of the example JSON was not checked key by key. ⚠️ for the object, ✅ for this one key's existence.

The page's sentence that a hook makes a violation "close to impossible" is the page's claim. The
reference's silent-disable and timeout rows are the reason that sentence stays 📣. A hook is
deterministic only on the path where it runs and exits 2.

The playbook's script matches on the substrings `deploy` and `production` inside
`tool_input.command`. The reference's own example matches a command prefix and returns
`permissionDecision: deny` inside `hookSpecificOutput`, with an optional `if` rule so the script
only spawns when the command already matches. The playbook's script is the shorter illustration.
File tools receive an absolute `file_path`, with `~` and relative paths expanded before the hook
runs; on Windows the separators are backslashes, and a forward-slash comparison misses them. None
of that is in the playbook's example, and none of it was executed here.

## Plan mode and auto mode, checked

Permission modes, <https://code.claude.com/docs/en/permission-modes>, read 2026-10-06.

The playbook says plan mode enforces the design review itself, because Claude cannot edit files
until the engineer accepts the plan.

- The modes page says plan mode blocks edits until the plan is approved. The common-setups row is "Claude Code blocks edits until you approve a plan." ✅ for that sentence, in the normal case.
- The same page's bypass section: in an interactive terminal session where bypass permissions are in the mode cycle, plan mode's blocks are not enforced. Claude is still instructed not to edit, but an edit or a shell command it attempts during planning runs without prompting. Ask rules and critical-path `rm` / `rmdir` still prompt. Plan mode keeps its blocks in non-interactive `-p` runs, Agent SDK sessions, and the VS Code chat panel. ⚠️ The playbook does not mention the exception.
- Approving a plan offers "Yes, and use auto mode", "Yes, manually approve edits", or "No, keep planning". If auto mode is unavailable the first option reads "Yes, auto-accept edits". If the session started with bypass permissions, it reads as a switch to bypass. The playbook's "accept the plan and implement" is this prompt, in shorter form.

Auto mode on the playbook is a stage of the operating model: approve the plan, then accept edits
without a per-edit prompt, and turn that on for routine work only after `CLAUDE.md`, skills,
hooks, and tests exist.

Auto mode on the doc is a classifier. A second model reviews actions and blocks escalation past
the request, unrecognized infrastructure, and actions that look driven by hostile content. With
Claude Code v2.1.283 or later it is the built-in starting permission mode for interactive terminal
and VS Code sessions. An organization can turn it off with `permissions.disableAutoMode`. The doc
says auto mode reduces prompts and does not guarantee safety.

Both descriptions are recorded. The playbook is not rewritten as if it had described the
classifier. Anyone using the playbook's "turn auto mode on once the guardrails mature" as an
instruction is describing an older operating step than the doc's default.

## What was not checked

- The sandboxing page. The playbook's claim that a `WebFetch` deny does not stop a shell, and that the domain allowlist does, is the page's claim only.
- The settings reference, key by key, for the managed-settings example. `allowManagedHooksOnly` was seen on the hooks page. The other keys were not.
- Whether a conversation boundary the user states in prose survives compaction. Not opened.
- Any hook, any plan-mode session, any `claude -p` eval. Not run.

## What this repository should not do with it

The plays are not this repository's workflow. The memory, backlog, and handoff already in
`ai-workflow/` are a different record, for research notes, and this note does not propose
replacing them with `intent.md` / `spec.md` / `plan.md`. Implementation of a gate belongs in the
separate repository named in [`PURPOSE.md`](../ai-workflow/memory/active/PURPOSE.md) §0.1. What
belongs here is the graded reading: context is not enforcement, a skill is not a hook, a hook
fails closed only on the path the reference actually blocks, and the writer of a change is not the
approver.
