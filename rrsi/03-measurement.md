# 03. RRSI — measurement, and what the numbers are not

> Read from `rrsi/evaluate.py` and `rrsi/loop.py` @ `be50316e1d`. The score table in the
> upstream README is quoted only as the authors' report.

## 1. The estimator

For a harness `H`, `k` trials on each task in the evolve set:

```
S_hat = 1/(k|D|)  sum of trial rewards
C_hat = 1/(k|D|)  sum of policy-token counts
```

Rewards are in `[0, 1]`. Coding and engineering trials have weight 1, so `S` is a pass rate.
A Harvey LAB trial has reward = criteria passed / criteria total and weight = criteria total,
so `S` is the fraction of criteria passed. That weighting is in `evaluate.py`'s docstring, not
only in the paper.

`C` is `None` when no token counts were recorded. The cost rule then has nothing numeric to
compare. This study did not trace every domain's token plumbing to see when `C` is actually
filled ⚠️.

## 2. A missing trial is a zero, until too many are missing

`aggregate` puts a missing trial in as reward 0 and keeps it in the denominator. The comment
states the reason: a candidate must not look better by destroying the trials it finds hard.

That is the right defence against one cheat, and it is the wrong reading of an infrastructure
failure. A container that never started is not a wrong answer. The coding README says so, and
the loop treats a **high** missing rate as invalid rather than as a score:

- `invalid_missing_frac` defaults to 0.15 in `RRSIConfig` and is 0.20 in the coding config.
- If missing trials exceed that fraction, the candidate is evaluated a second time.
- If it still exceeds it, the candidate is `eval_invalid`, stored without a `ΔS`, and does not
  enter the tried-set.
- A baseline that fails the same check aborts. It does not become `H_0`.

So a few missing trials pull `S` down and can decide a round. A flood of them voids the round.
Both facts are ✅. Which of a paper's reported points came from a round with a non-zero but
legal missing count is not in the code, and was not re-measured ⚠️.

This is the same discipline as [`SYNTHESIS.md`](../SYNTHESIS.md) §7, aimed the other way. There,
a delivery failure was counted as a clean negative. Here, a delivery failure is counted as a
task failure, which can reject a harness for the runner's fault. The invalid-fraction is the
mitigation, and it is a threshold, not a separation of the two causes inside the band.

## 3. Held-out numbers never enter selection

The evolve set is what `select_round` sees. SWE-bench, JobBench, GDPval, APEX-Agents and
Frontier-Eng are separate scripts run on `H_0` and on the incumbent after the search. They do
not choose the winner. That split is real in the layout (`domains/coding/scripts/swe_eval.sh`,
the workspace `heldout` and `ood/run_*.sh`, `domains/eng/scripts/final_eval.sh`). ✅ as a
procedure. It does not by itself make a transfer result reliable: the critic was trained on
the instruction "would this help on another suite?", and the proposer sees the evolve-set
failures. Leakage the critic misses is exactly a gain that shows up on the evolve set and
shrinks outside it. The procedure is the authors' defence against that. It is not an audit
that the defence worked.

## 4. The table is not a finding of this repository

The upstream README reports, with Claude Opus 4.8 frozen in every instance, and each number
against the unevolved `H_0` in the same window:

| Benchmark | Role | H_0 | RRSI |
|---|---|---:|---:|
| Terminal-Bench 2.1 | evolve | 74.2 | 80.2 |
| SWE-bench Verified | not in selection | 82.0 | 83.8 |
| Harvey LAB evolve | evolve | 89.4 | 90.5 |
| Harvey LAB held-out | not in selection | 86.9 | 89.2 |
| JobBench | not in selection | 36.0 | 40.7 |
| GDPval | not in selection | 48.8 | 52.3 |
| APEX-Agents | not in selection | 34.2 | 37.9 |
| EngDesign | evolve | 50.0 | 54.9 |
| Frontier-Eng | not in selection | 17.7 | 22.0 |

A second policy, Gemini 3.5 Flash, is reported at 64.6 → 78.7 on Terminal-Bench 2.1 and
76.8 → 79.0 on SWE-bench Verified.

**Grade: 📣.** Copied from the README, which says the numbers are from the paper. Not re-run.
Not comparable to any number in [`SYNTHESIS.md`](../SYNTHESIS.md). [`PURPOSE.md`](../ai-workflow/memory/active/PURPOSE.md)
excludes reproducing a vendor's self-reported score and using it as a basis for comparison.
The useful claim that survives without the table is the procedure: regularize the search, keep
the model frozen, and do not let a within-noise gain replace the incumbent.

## 5. What would make a number adoptable

A number from this table becomes adoptable only after someone re-runs `baseline` and the
held-out script against the published incumbent commit, with the missing-trial count recorded,
and the critic's rejects kept. That run is not this study. The code path that would produce
the record is `runs/<domain>/history.jsonl` plus `jobs/<job>/eval.json`. The repository as
cloned does not contain those run artifacts.
