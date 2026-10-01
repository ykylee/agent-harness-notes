# 01. RRSI — what it edits

> Read from `google-research/rrsi` @ `be50316e1d`. Component vocabulary:
> `rrsi/components.py`. Domain seam: `rrsi/domain.py`. Paper arXiv:2609.24972 states the same
> split; the code is the grade.

## 1. The model is not the object

RRSI's own sentence, in the README and the paper's opening: an agent's capability is largely
set by the harness around a **frozen** model — prompts, control flow, tools, memory, context
management. The search roles (proposer, analyst, critic) and the policy that *runs* the
harness are configured separately. In `domains/coding/rrsi.json` the policy string is
`vertex_ai/claude-opus-4-8`. The README says any LiteLLM model string works, and reports a
second coding run with Gemini 3.5 Flash as that frozen policy.

The weights are not a parameter of the search. An edit that would fine-tune them is outside
the edit space below. That is the sense in which this is harness engineering rather than
training.

## 2. The incumbent is a commit

Each domain evolves on a branch `evolve/<domain>`. A round drafts candidates in their own git
worktrees. Accepting one fast-forwards the branch. The frontier file records the incumbent
commit, its score and its cost. Resume is "reuse `eval.json` if it is already there."

So the harness under search is a directory (`Domain.harness_path`, default `harness`, resolved
under `domains/<name>/`), and the thing that survives a round is a commit, not a chat. That
matches the rule this repository already treats as load-bearing: the plan has to outlive the
session that wrote it. Here the plan *is* the harness tree.

## 3. The edit space is open. The tags are not.

`rrsi/components.py` fixes the vocabulary a proposer must tag each edit with:

| Tag | Kind |
|---|---|
| `prompt` | model-facing text. A diff whose every changed line is a string literal or a comment is classified as this |
| `control_flow` | control structure |
| `config` | configuration |
| `output_plumbing` | how results are shaped for the caller |
| `context_mgmt` | context handling |
| `client_tool` | a tool the client registers. Structural |
| `skill` | a skill file or registry. Structural |
| `memory` | a memory store. Structural |
| `subagent` | an extra policy call. Structural |

`K_STR` is the last four. Novelty (`nu`) counts how many of those four the candidate touches
that the incumbent has never had an **accepted** edit on. It is only a tie-break inside the
noise band (`selection.py`). It is not permission to add them.

A declared tag is kept only when the diff matches a signal for that tag (`has_evidence`).
Otherwise `classify_diff` recovers a tag from the diff, defaulting to `prompt`. The generic
signals only recognise memory, skill, tool and subagent. `control_flow`, `config`,
`context_mgmt` and `output_plumbing` stick when the domain's own `component_signals` match
(the coding adapter does: `_run_agent_loop`, `threshold`, `_summarize`, truncation helpers).
The comment says why the check exists: a proposer can name an untried component to fill a
reserved exploration slot without shipping that component, and a false tag corrupts the
tried-set and the novelty term.

The README's claim "the constraints act on how the search moves, not on what the harness may
contain" is ✅ for the budget: `schedule.edit_budget` bounds the count of edits in one
candidate, and the module docstring says the set of mechanisms is not restricted. It is not
a claim that any file in the repo may change. The domain adapter, the critic's denylist, and
the benchmark runners sit outside `harness_path`.

## 4. Three instances, one loop

A domain is a `Domain` object: task splits, a `run`/`score` pair, trace rendering for the
analyst, a leakage denylist, and optional non-compensatory guards. The core never reads a
trajectory format itself.

| Instance | Evolve set | Starting harness | Held out of selection |
|---|---|---|---|
| `coding` | Terminal-Bench 2.1, all 89 tasks, `k = 2` | Terminus-2 from harbor (`third_party/harbor_terminus2/`) | SWE-bench Verified |
| `workspace` | Harvey LAB split generated from a pinned checkout | react toolbelt from archipelago | Harvey held-out tasks, JobBench, GDPval, APEX-Agents |
| `eng` | EngDesign | same react toolbelt family | EngDesign v1, Frontier-Eng |

The starting harnesses are other projects' agents. RRSI does not define a loop of its own for
the policy. It edits someone else's.

## 5. What a domain may still forbid

`Domain.guards` is a non-compensatory check on top of the score. The engineering instance
uses it for a valid-rate drop and a rise in no-submission. A candidate can win on `S` and
still be inadmissible. That is domain policy, not part of Algorithm 2's cost rule. It is the
one place the "open edit space" is closed by a predicate the score cannot buy off.
