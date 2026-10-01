# 02. RRSI — the loop

> Read from `rrsi/loop.py`, `schedule.py`, `history.py`, `critic.py`, `selection.py` @
> `be50316e1d`. One round is Algorithm 1 (propose) then Algorithm 2 (select). The paper names
> those algorithms; the functions below are the implementation that was read.

## 1. One round

`Run.round`, as the module states it:

1. Analyze the incumbent's own evaluation into failure modes.
2. Compute the annealed edit budget `b_t`.
3. Compute stall, tried components, untried components, exploration text, and the prune set.
4. For each of `m` variants, in its own worktree: propose, tag, critic with bounded repair, smoke.
5. Evaluate the screened candidates on the full evolve set.
6. Judge admissibility, take the argmax, or keep the incumbent.
7. Fast-forward `evolve/<domain>` to the winner.

Coding's `rrsi.json` sets `T = 20`, `m = 2`, `b_min = 1`, `b_max = 4`, `k = 2`. Two candidates
a round, at most four edits early and one edit late.

## 2. Proposal side — constrain the move

### 2.1 The budget is a cosine anneal

```
b_t = ceil( b_min + (b_max - b_min) * 1/2 * (1 + cos(pi * t / T)) )
```

`schedule.edit_budget`. Early rounds may bundle coordinated edits. Late rounds are sparse so a
measurement attaches to one component. The history docstring says a bundled candidate shares
one `(ΔS, ΔC)` across every edit in the bundle, and that the record becomes evidence about a
single component only as `b_t` reaches 1. A bundled early win is **not** attributed per edit.
That limit is in the code's own comment.

### 2.2 History is part of the proposal

`History` is a JSONL file, one record per edit: round, component, hypothesis, diff, score
change, cost change, whether it was accepted. `a = 1` only for the edits of the candidate
that became the next incumbent.

Summaries the proposer is conditioned on:

| Symbol | Code | Meaning |
|---|---|---|
| `T_t` | `tried()` | Components with at least one **measured** edit |
| `g_t(l)` | `yield_g` | Best `ΔS` for that component inside the last `n_prune` rounds. Empty is −∞ |
| `U_t` | untried in `exploration` | `K` minus `T_t` |
| `σ_t` | `stall_flag` | 1 when the incumbent's score has not moved by more than `delta` over `w` rounds |
| `B_t` | `prune_set` | Tried components whose recent best gain is ≤ 0, plus the accepted machinery to remove |

A candidate dropped before measurement (critic reject, smoke fail, invalid eval) is stored
with `delta_S = None` and does **not** enter `T_t` or `g_t`. Gate failures are also trimmed
in the prompt view: only the most recent few unmeasured records are shown, "because a wall of
aborts is a feedback loop, not evidence."

When `σ_t = 1` and something is untried, `m_draft` slots (coding: 1) are reserved. A variant
in a reserved slot must put at least one edit on an untried component. The tag check in
`components.normalize` exists so that reservation cannot be satisfied by a relabelled prompt
tweak.

## 3. The critic is a screen, not a proof

`critic.review` runs **before** evaluation. Two layers:

1. Regex. A generic credential pattern, plus the domain's `critic_patterns` (grader paths, task ids, judge references). A hit is an immediate reject.
2. An LLM review. The system prompt tells the reviewer to reject leakage (task names, entity names, magic constants, branching on task identity), degenerate no-ops, grader gaming, undeclared bundling, memory that persists task-specific data across trials, and unbounded retry loops. It tells the reviewer **not** to judge syntax or crashes. Those are the smoke check's job.

A rejection goes back to the proposer for `repair_rounds` (coding: 5). A candidate that cannot
be repaired is dropped and recorded without a measurement.

The reviewer model is the same family as the proposer (the prompt and the pyproject both point
at Claude on Vertex). ✅ that the screen exists and what it is instructed to catch. ⚠️ that it
catches those things. Nothing in this study measured the critic's false accept or false reject
rate. An LLM reading a diff is the same shape as a check that can fail open: a leak that does
not look like a task name passes, and a general procedure that mentions a domain word can be
rejected.

The prompt's litmus test is the right question, and it is still a judgement: "would this change
still help on an unfamiliar task from a different suite?"

## 4. Selection side — a gain has to clear the noise and pay for itself

`selection.judge`, for a screened candidate with score `S'` and cost `C'`, against the
incumbent `(S_t, C_t)` and the best-so-far `S*`:

```
ΔS = S' - S_t
ΔC = (C' - C_t) / C_t
floor:    S' >= S* - delta
cost:     if ΔS > delta:  ΔC <= beta0 + beta1 * ΔS
          else:           w_s * ΔS - w_c * ΔC + w_n * nu > 0
```

Admissible only if the floor holds, the cost rule holds, and every domain guard holds. The
next incumbent is the admissible candidate with the highest `S'`, or the current one if none
is admissible. `S*` becomes `max(S*, S of the chosen incumbent)`.

Coding's constants, from `rrsi.json` and its `_doc` string:

| Knob | Value | What the file says it means |
|---|---|---|
| `delta` | 0.017 | 3 passes out of 178 trials. The noise band |
| `beta0` | 0.10 | token slack when a gain clears the band |
| `beta1` | 44.5 | "25% tokens per additional pass" |
| `w_s` | 0 | inside the band, a score gain alone never admits |
| `w_c` | 15 | weight on relative cost inside the band |
| `w_n` | 0.5 | weight on structural novelty inside the band |
| `n_prune` | 4 | window for `g_t` |

Inside the band, with `w_s = 0`, the only way in is a token saving or a new structural
component whose novelty term beats the cost term. A small score bump does not count. That is
the regularization the paper maps onto L0 (the budget), L1 (pruning components that stopped
helping) and L2 (the cost penalty). The mapping is the authors' analogy. The predicates above
are what the code enforces.

`delta` may be `null`, in which case `calibrate.py` re-estimates it from the base evaluation
(bootstrap, or repeated base runs) at `delta_z` standard deviations. The shipped coding config
pins 0.017 rather than leaving it null.

## 5. Pruning is a prompt, then an edit

`prune_set` lists components whose best recent measured `ΔS` is ≤ 0, and attaches the accepted
edits of that component still in the incumbent. That list is handed to the proposer as
machinery to remove. There is no separate pass that deletes files. Removal happens only if a
later candidate edits them out and that candidate wins selection. A component can be "pruned"
in the prompt and still be in the tree.
