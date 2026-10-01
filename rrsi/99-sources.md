# 99. RRSI — sources and verification status

> **✅** read from `google-research/rrsi` @ `be50316e1d` or from the paper's algorithm as
> implemented there. **📣** the authors' or the press's number, not re-run. **⚠️** not
> verified here.

## A. Primary ✅

| Source | Taken | Grade |
|---|---|---|
| `google-research/rrsi` @ **`be50316e1db05914068a973f322770ef08ed7ba1`** (2026-09-23), Apache-2.0, "not an officially supported Google product" | the study | ✅ |
| `rrsi/schedule.py` `edit_budget` | cosine anneal of the edit count | ✅ |
| `rrsi/history.py` | JSONL history, tried set, yield, stall, prune set, exploration text | ✅ |
| `rrsi/components.py` | `K`, `K_STR`, tag recovery, novelty | ✅ |
| `rrsi/critic.py` | regex precheck + LLM review prompt + repair | ✅ the screen; ⚠️ its accuracy |
| `rrsi/selection.py` `judge` / `cost_rule` | floor, cost rule, argmax | ✅ |
| `rrsi/evaluate.py` `aggregate` | missing trial → reward 0, full denominator | ✅ |
| `rrsi/loop.py` | round order; invalid if missing fraction exceeded; one retry | ✅ |
| `rrsi/domain.py` | domain seam, `harness_path` | ✅ |
| `domains/coding/rrsi.json` | T, k, m, betas, delta 0.017, `w_s = 0` | ✅ config |
| `domains/coding/README.md` | Terminus-2 base, 89 tasks, infra failure vs harness failure | ✅ first-party |
| `domains/workspace/README.md`, `domains/eng/README.md` | the other two instances' splits | ✅ first-party, skimmed for the split, not every script |
| arXiv:2609.24972 (2026-09-21), Xia et al. | the algorithm names and the claim that regularization is on the search | ✅ as the paper the code cites. The PDF's experimental tables were not re-derived |

## B. Recorded, not adopted 📣

| Claim | Where |
|---|---|
| Terminal-Bench 74.2 → 80.2, SWE-bench 82.0 → 83.8, and the rest of the README table | README "Results", attributed to the paper |
| Gemini 3.5 Flash 64.6 → 78.7 / 76.8 → 79.0 | same table |
| "30% fewer policy tokens" / "36% fewer" | paper abstract and secondary writeups. The two percentages already disagree across writeups. Neither was recomputed |
| L0 / L1 / L2 as the right names for budget, prune, and cost | authors' analogy. The predicates are ✅; the names are theirs |
| Press summaries (MarkTechPost, StackSweep, and others) | not used. Where they disagree with the README table, the README table is the one quoted, still as 📣 |

## C. Not verified ⚠️

| Item | Why |
|---|---|
| Any score | not re-run. No Vertex project, no Docker, no harbor |
| Critic false-accept / false-reject rate | the prompt was read. The model's decisions were not |
| Whether `C` is populated for every domain | `aggregate` allows `C is None`. Per-domain token plumbing was not fully traced |
| Run artifacts | the clone has no `runs/` history. The published incumbent commit of each domain was not checked out |
| Dream-RSI (arXiv:2609.14858) | a different system. Not read |
| Transfer onto Codex, Strands, ACP, Gas Town, Gas City | not claimed by the code, not tested |

## D. Method

Same rule as the other studies: the code is the contract, the score is a claim. Two
consequences:

- The "open edit space" sentence was checked against `harness_path` and `K`. The space of
  *mechanisms inside the harness directory* is open. The rest of the repo is not the search
  state.
- The missing-trial rule was read in both directions: a zero with a full denominator stops a
  candidate from dropping hard tasks, and the invalid-fraction stops a dead runner from
  becoming a score. Inside the fraction, the two causes are still added together.

## E. Cross-references

- [`PURPOSE.md` §0.5](../ai-workflow/memory/active/PURPOSE.md)
- [`docs/07-harness-engineering.md`](../docs/07-harness-engineering.md) and
  [`harness-engineering`](../ai-workflow/wiki/concepts/harness-engineering.md) §11 — the
  discipline this method automates, and the way it can overfit
- [`SYNTHESIS.md`](../SYNTHESIS.md) §7 — a failed delivery is not a clean negative; here a
  failed delivery inside the allowed fraction is a zero
