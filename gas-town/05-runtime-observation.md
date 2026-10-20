# 05. Runtime observation — one town, two polecats, no model

> **What this is.** The first *executed* record in this study. Until now every Gas Town mechanism
> here was read from source or design docs ([README](README.md) "Read status"). On 2026-10-20 a
> throwaway town was built from the studied revision and driven through sling → done → merge
> queue → post-merge → convoy close, then through a deliberately stalled worker → health checks →
> force-kill → stranded convoy → re-dispatch. TASK-2026-10-20-main-007.
>
> **What it is not.** No language model ran. The "agent" was a shell script registered as a Tier-1
> preset (`settings/agents.json`), which logs everything it receives, commits one line, and calls
> `gt done`. That isolates the **orchestration mechanics** (hooks, beads, merge queue, heartbeat
> stores, deacon patrol commands) from model behaviour. Anything that needs an LLM to act —
> Witness verification, Refinery judgement, Dog formulas, Mayor decomposition — is observed only
> as the *shape* of the hand-off, not as behaviour. Cost, throughput and conflict-rate claims stay
> ⚠️ ([99](99-sources.md) §C).
>
> **Grades.** ✅ observed at runtime in this lab · 📖 source line cited to explain an observation ·
> ⚠️ not observed / could not be closed here.

## 0. Setup

| Item | Value |
|---|---|
| Gas Town | `gastownhall/gastown` `649b832b` (`v1.2.1-304-g649b832b`, 2026-07-23) — the same revision the study read; built with Go 1.26.8 and ICU 78 headers (the `dolthub/go-icu-regex` cgo dependency needs `unicode/uregex.h`; no system `libicu-dev`, so the Ubuntu package was unpacked into a scratch include dir) |
| Beads | `bd` **1.0.5** (`6a3f515ce`, 2026-05-28), the version `gastown/go.mod` pins. `gt` shells out to the `bd` binary on `PATH` (148 call sites, `internal/beads/exec.go:26`) |
| Dolt | 2.4.0 (installed on the host; `gt install` starts `dolt sql-server` on 3307 with `.dolt-data/`) |
| tmux | 3.6. Gas Town runs its own tmux server (`tmux -L town-<hash>`), so `tmux ls` on the default server shows nothing |
| Rig | a bare repo `file:///…/remote/lab.git` with one commit; `gt rig add lab file:///…` (a bare path without `file://` is rejected: "expected a remote URL") |
| Agent | `fakeagent` preset: `{"command": "<script>", "args": [], "process_names": ["fakeagent","bash"], "prompt_mode": "arg", "ready_prompt_prefix": "> ", "ready_delay_ms": 1000}`; a second preset `fakeagent-stall` adds `"env": {"FAKEAGENT_NO_WORK": "1"}` so the worker never calls `gt done` |
| Town | `~/.cache/gt-lab/town` (outside the repository). Logs: `fakeagent.log`, `sling-2.log`, `gt-done-1.log`, `healthcheck-2.log`, `feed-stranded.log`, `redispatch.log` in `~/.cache/gt-lab/` |

**Version skew is the first runtime fact.** With the current `bd` (1.3.0, `4f9174e6b`) on `PATH`,
`gt install` created the Dolt database at schema **v49** through the embedded library and the
standalone `bd` then refused: "refusing to auto-apply 23 pending schema migrations to a shared
server database (v49 -> v72): migrating would lock out every co-resident bd client". Even reads
failed (`table not found: leases`). The documented install path (`go install …/bd@latest`) would
hit this with any `gt` older than its `bd`; the fix here was to build the pinned `bd` 1.0.5.
`gt install` also warned "Could not create town-level agent beads" and "Could not set
routing.mode" before the skew was resolved. ✅

## 1. The happy path, as it actually ran ✅

```
bd create "Append one line to notes.txt"            → lab-1a6 (open)
gt sling lab-1a6 lab --no-boot                      → polecat "rust" (namepool "wasteland"),
                                                      worktree lab/polecats/rust/lab,
                                                      branch polecat/rust/lab-1a6+mvg4ya32,
                                                      convoy hq-cv-s453s (auto),
                                                      formula mol-polecat-work bonded,
                                                      lab-1a6 status=hooked assignee=lab/polecats/rust
tmux -L town-… new-session -s lab-rust … fakeagent "[GAS TOWN] polecat rust (rig: lab) <- witness • 2026-10-20T03:40 • assigned\n\nRun `gt prime` to initialize your context."
gt prime (inside the worker)                        → role/hook/completion protocol text (~500 lines)
<work> commit                                       → 425f189
gt done                                             → ✗ "cannot complete: uncommitted changes would be lost"   (§2)
gt done (after .gitignore)                          → branch pushed; MR bead lab-wisp-dfr (ephemeral,
                                                      label gt:merge-request, description = branch/target/
                                                      source_issue/rig/commit_sha); lab-1a6 → closed;
                                                      "Witness notified of COMPLETED (via nudge)";
                                                      session terminated
gt mq list lab                                      → lab-wisp-dfr  score 1200.0  P2  ready
gt refinery claim lab-wisp-dfr                      → MR assignee = refinery-1
git merge --ff-only + push (by hand, in refinery/rig) → main = e4e9c51
gt mq post-merge lab lab-wisp-dfr                   → MR closed (merged); "Skipping remote branch
                                                      delete …: open PR exists (gas-fk4)"             (§3)
gt convoy check                                     → hq-cv-s453s auto-closed, close_reason
                                                      "All tracked issues completed"; mail to mayor/
```

Where things live: the **task bead** is in the rig database (`lab-*`); the **convoy**, the
**agent beads** (`lab-polecat-rust`, `lab-witness`, `lab-refinery`) and the mayor's mail are in
the **town database** (`hq`). The MR bead is a *wisp* (ephemeral): `bd show` finds it, `bd list
--all` does not. The agent bead's description is the state record the study described
([03](03-roles-and-lifecycle.md) §2): after `gt done` it read `agent_state: done`,
`cleanup_status: clean`, `active_mr: lab-wisp-dfr`, `exit_type: COMPLETED`,
`completion_time: …`; after `post-merge`, `active_mr: null`. `bd history lab-1a6` showed **10
Dolt commits** for one bead's life — the ledger is versioned per write, as [02](02-architecture.md)
§2 claimed. The retired worker's worktree stayed on disk (`gt polecat list` → `idle`, `reuse:
idle-recovery-needed`; `check-recovery` → `SAFE_TO_NUKE`; `git-state` → `CLEAN (safe to kill)`);
cleanup is a separate decision, not part of `gt done`.

## 2. `gt done` blocks itself on its own overlay files ✅📖

The first `gt done` failed although the work was committed. `gt` had scaffolded three untracked
paths into the polecat worktree — `.beads/`, `.runtime/`, `CLAUDE.md` — and the lab repository,
unlike `gastown` itself, has no `.gitignore` for them. `gt done` then ran its safety net
(`internal/cmd/done.go:795–836`): `git add -A`, **unstage** `CLAUDE.md` (overlay marker),
`CLAUDE.local.md` and every `RuntimeArtifactPaths()` entry, `git commit` → git answers "nothing
added to commit but untracked files present" (exit 1) → "auto-commit: git commit failed" → the
outer guard still counts the same files as uncommitted work and refuses: "cannot complete:
uncommitted changes would be lost". Reproduced by hand with the same three git commands. The
unstage list and the "would be lost" check disagree about what the overlay is. Any rig whose
repository does not ignore Gas Town's runtime files hits this on the first `gt done`; the
`gastown` repo avoids it only because its `.gitignore` lists `.runtime/*` and `.beads/*` state
files. Remedy used here: commit a `.gitignore` on the polecat branch (it rode into `main` with the MR).

## 3. Three places where the source and the run disagree

- **The merge slot is dead code.** [02](02-architecture.md) §8 described the lock-as-a-bead
  (`gt:merge-slot`). At `649b832b` the only non-test callers of `MergeSlotAcquire/Release` are
  `internal/refinery/engineer.go:299–305`, and `Engineer.ProcessMRInfo` / `doMerge` have **no
  non-test caller** in `internal/` or `cmd/`. The `gt mq` / `gt refinery` command sets contain
  `claim`, `release`, `next`, `ready`, `post-merge` but no merge step. Consequently no
  `gt:merge-slot` bead ever appeared in the lab (`bd list --all --label gt:merge-slot` → none), and
  "claim" only sets the MR's assignee. The merge itself is the Refinery *agent's* git work; the
  ledger lock exists in the code base, not in the running product. 📖
- **"Witness notified" is printed whether or not anyone was notified.** `gt done` sends
  `POLECAT_DONE <polecat> exit=<type>` as a tmux nudge (`done.go:1933`) and prints "✓ Witness
  notified of COMPLETED (via nudge)" on the next line unconditionally (`:1934`). With no witness
  session the nudge failed ("Warning: failed to nudge witness lab-witness: session not found") and
  the witness mailbox stayed **empty** — the completion signal is not persisted as mail. The
  durable record of completion is the agent bead and the MR bead, not a message. ✅📖
- **`post-merge` reports an open PR that does not exist.** `HasOpenPullRequest`
  (`internal/git/pr_lookup.go:98`) returns `true` for *any* error other than not-found; a
  `file://` origin yields "remote is not a GitHub repo", so branch deletion is skipped with the
  message "open PR exists (gas-fk4)". Fail-closed is the safe choice — the branch survives — but
  the message names a cause that is false. ✅📖

## 4. The stalled worker — what each store said ✅

Second task `lab-fg5`, slung with `--agent fakeagent-stall --no-boot`: polecat "chrome",
hooked at 03:51:35, the worker prints a prompt and never calls `gt done`.

| Store | Value while stalled | Value after `gt deacon force-kill` |
|---|---|---|
| tmux (`gt polecat status`) | `running`, "Last Activity: 03:51:34" | session gone; status **`stalled`** |
| `gt polecat list` | `● working` | `○ stalled` |
| Agent bead `lab-polecat-chrome` (hq) | `agent_state: spawning`, `hook_bead: lab-fg5` | **unchanged** (`spawning`, `updated_at` 03:51:32) although force-kill printed "3. Updating agent bead state to 'killed'" |
| Heartbeat session store `.runtime/heartbeats/lab-chrome.json` | written by `gt heartbeat --state=working` as the polecat: `{"timestamp":…,"state":"working"}` (rust's read `{"state":"exiting","context":"gt done","bead":"lab-1a6"}`) | unchanged, now stale |
| Deacon file `deacon/heartbeat.json` | `{"cycle":1,"healthy_agents":0,"unhealthy_agents":0}` after `gt deacon heartbeat` | — |
| Agent-bead label `heartbeat:<epoch>` | never written — only `molecule_await_signal.go:447` writes it, i.e. a worker that never reaches `await-signal` has no label (exactly the gotcha [03](03-roles-and-lifecycle.md) §3 quoted) | — |
| Hooked bead `lab-fg5` (rig db) | `hooked`, assignee `lab/polecats/chrome` | still `hooked` after the kill |

Four stores, four answers — the "never from a single store" rule ([03](03-roles-and-lifecycle.md)
§3) is not advice here, it is the observed state of a single stalled worker. The agent-bead
update on force-kill is explicitly best-effort: `updateAgentBeadState` discards the error
(`deacon.go:1212`, "// Best effort"), so the ledger can keep saying `spawning` about a worker the
deacon has already killed and mailed the mayor about ("Agent killed: lab/polecats/chrome" did
arrive in `mayor/`). The `spawning → working` transition also never happened for the scripted
worker: that transition is made by the agent following the formula, not by the orchestrator.

**Health check.** `gt deacon health-check lab/polecats/chrome` nudges the pane with
"HEALTH_CHECK: respond with any action to confirm responsiveness" (the worker's log shows the
text arriving with a trailing escape byte) and waits 30 s for either of two signals: the agent
bead's `updated_at` moving, or tmux session activity moving, both sampled *after* the nudge
(`deacon.go` `runDeaconHealthCheck`). The script answered within milliseconds by printing a
prompt, and an operator `send-keys "ping"` during the second check produced pane output too; both
checks still reported "did not respond (1/3, 2/3)". A responder faster than the baseline sample,
or one whose output does not move tmux's activity clock, is invisible to this check — only a
bead write is a reliable answer. `health-state` then showed the force-kill with a 5-minute
cooldown and the failure counter reset to 0.

**`stale-hooks` looks in the wrong database.** With `lab-fg5` hooked for minutes,
`gt deacon stale-hooks --max-age 1s --dry-run` answered "No hooked beads found" from both the
town and the rig directory. `listHookedBeads` runs `bd list --status=hooked` against the **town**
beads dir (`internal/deacon/…`, `townBeadsDir(townRoot)`), and rig-prefixed task beads live in
the rig database. Unless routing merges them, the deacon's stale-hook patrol cannot see the
hooks it is meant to clear. ✅📖

## 5. Recovery: rollback, stranded, re-dispatch ✅

- Killing the worker's tmux server while its `gt sling` was still in session start made sling fail
  with "starting polecat session: … startup blocked: no tmux server running" and **roll back** the
  polecat: worktree removed, agent bead `agent_state: nuked`, `lab-fg5` back to `open` with no
  assignee. `gt convoy stranded` then reported exactly the documented signal: "Ready issues: 1 (of 1
  tracked) • lab-fg5" for `hq-cv-yxuy4`.
- `gt deacon feed-stranded` is not mechanical: it auto-created a **Dog** ("alpha", pool 1/4) and
  slung the formula `mol-convoy-feed` to it — i.e. recovery is delegated to an infra *agent* that
  would need a model. In this build the sling failed before any session: "creating wisp: failed to
  create issue from mol-convoy-feed: validation failed for issue : title is required" (`bd`
  `internal/types/types.go:223`). `mol-polecat-work` works because it is bonded `--on` an existing
  bead whose title is reused; a formula slung on its own needs a root title that `mol-convoy-feed`
  does not carry. `feed-stranded-state` recorded "Feed count: 0".
- `gt deacon redispatch lab-fg5` is mechanical: it slung the bead again (a fresh "chrome", the
  namepool reuses the name) and, without `--no-boot`, **booted the rig's Witness** as a session of
  the default agent — our script, which immediately learned that "gt done is for polecats only
  (BD_ACTOR=lab/witness)". The result of that second cycle is in §6.

## 6. Second cycle ✅

`gt deacon redispatch lab-fg5` ran `gt sling lab-fg5 lab --force --no-convoy` underneath
(visible in the process list), warned "daemon is not running. Polecat may not auto-start", booted
the Witness (03:57:25) and spawned a new polecat "chrome" (session start 04:00:32 — three minutes
of readiness waits in between, §7). The worker committed `3a3e043`, and `gt done` went through
unaided this time because `main` now carries the `.gitignore` from cycle 1: MR `lab-wisp-qlm`,
`lab-fg5 → closed`, "Purged 3 closed ephemeral bead(s)" (cycle 1's wisps). Operator steps as the
Refinery: `gt refinery claim lab-wisp-qlm`, fast-forward merge in `refinery/rig`, push,
`gt mq post-merge lab lab-wisp-qlm` (same false "open PR exists" line, §3), then `gt convoy check`
auto-closed `hq-cv-yxuy4` and mailed `mayor/` ("Convoy complete", third message in the inbox).
`main` ends with both workers' lines in `notes.txt`:

```
fakeagent rust touched this at 2026-10-20T03:40:42Z
fakeagent chrome touched this at 2026-10-20T04:00:32Z
```

Two things did not go as the design draws them. The Witness session that `redispatch` booted did
not survive its own startup: the script received no nudge at all, and by the time sling reached
"Slinging lab-fg5" the town's tmux server was already gone ("failed to nudge witness lab-witness:
no tmux server running") — a role session that fails Gas Town's readiness/verification checks is
torn down silently. And `redispatch` itself never returned: like both earlier slings it stayed in
session start after the worker had finished, and was killed by the operator (rc 144) after the
merge. The ledger did not need it — every state change had already been written by the commands
that did the work.

## 7. `gt sling` blocks for minutes with an agent it cannot read

`gt sling` is synchronous through session start (`internal/polecat/session_manager.go` `Start`):
`WaitForCommand` (up to `ClaudeStartTimeout` 180 s) → `WaitForRuntimeReady` polling the pane for
`ready_prompt_prefix` every 200 ms (another 180 s) → startup-nudge delivery verification
(`verifyStartupNudgeDelivery`, sleep-then-check up to `StartupNudgeMaxRetries`, which is why
the first worker's log shows "Check your hook with `gt hook`. If work is present, begin
immediately." arriving twice, 27 s apart) → session liveness check. With a scripted agent whose
prompt line scrolled off the pane, the first sling was still running 5½ minutes after the worker
had finished; the second returned only when its session was killed (rc=1, rollback). Readiness
is inferred from the terminal, so an agent that does not look like Claude Code at the prompt
costs the operator minutes per sling even when the work is already done. ✅📖

## 8. What this changes in the study

| Claim | Before | Now |
|---|---|---|
| "Nothing executed" ([README](README.md)) | true | **false for the mechanics**: install, rig, sling, done, mq, post-merge, convoy, deacon patrol commands ran; model behaviour still unobserved |
| Merge slot as a ledger item ([02](02-architecture.md) §8) | source-read | code present, **unreachable from any command** at this revision ⚠️→📖 |
| Three heartbeat stores + "never from a single store" ([03](03-roles-and-lifecycle.md) §3) | design-doc quote | observed: four stores disagreed about one killed worker |
| Retired completion model ([03](03-roles-and-lifecycle.md) §2) | doc | observed: `gt done` retires the session, leaves the worktree, marks the bead `done` |
| Stranded convoy as the upstream-failure signal ([03](03-roles-and-lifecycle.md) §5) | doc | observed after rollback; the *feed* is an agent formula and failed here |
| Beads property: forgeable ledger ([02](02-architecture.md) §5) | source | consistent: every state write here was a `bd update` by whoever held `BD_ACTOR` — the operator shell wrote as `lab/refinery` and `lab/witness` by exporting the variable |

## 9. Not observed ⚠️

| Item | Why |
|---|---|
| Witness verification, Refinery merge judgement, Dog formulas, Mayor | they are model sessions; the scripted agent only showed where they are invoked |
| The merge engine (`doMerge`, merge slot) | no command reaches it |
| Daemon (`gt daemon`), scheduler capacity mode, 3-minute heartbeat dispatch | not started — would have booted model sessions for every role |
| `gt up` / full stack, Deacon session | same |
| Cost, throughput, conflict rate | no model, no numbers |
| Behaviour with a current `bd` (1.3.0) | schema skew blocked it; a newer `gt` would be needed |

## 10. Sources

Lab transcript files under `~/.cache/gt-lab/` (not committed); `gastown` `649b832b`:
`internal/cmd/done.go` (795–836 auto-commit, 1882–1934 nudges), `internal/cmd/deacon.go`
(`runDeaconHealthCheck`, `runDeaconForceKill`, `updateAgentBeadState` 1207–1213,
`runDeaconStaleHooks`), `internal/deacon/*` (`listHookedBeads`), `internal/cmd/mq.go` (548–572,
636–655), `internal/git/pr_lookup.go:98`, `internal/refinery/engineer.go` (278–305, 504, 1030,
1349), `internal/refinery/batch.go:325`, `internal/polecat/session_manager.go` (`Start`,
`verifyStartupNudgeDelivery`), `internal/runtime/runtime.go:332`, `internal/config/env.go:806`,
`internal/config/loader.go:2212`, `internal/beads/exec.go:26`, `internal/constants/constants.go:22`,
`docs/agent-provider-integration.md`, `docs/INSTALLING.md`; `beads` `v1.0.5`
`internal/types/types.go:223`.
