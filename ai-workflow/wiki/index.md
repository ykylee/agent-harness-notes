<!-- standard-ai-workflow-kit: v1.10.0 -->

# Master Knowledge Index

> Format and rules in [`./SCHEMA.md`](./SCHEMA.md). Entries are added as ingests create pages.
> The sources are the study folders — `docs/` (the Codex harness), `browser-agents/`, `strands/`,
> `agent-ux/`, `gas-town/`, `gas-city/`, `claude-code/`, and the notes `rrsi/`, `ai-sdlc/`, `harness-artifacts/` —
> plus [`SYNTHESIS.md`](../../SYNTHESIS.md); this wiki **re-indexes them by concept** (19 pages, 2026-10-19).
>
> For the split between **surface-specific** axes (perception, injection, credentials) and
> **surface-independent** ones (approval, providers, capability, planes), see [[concepts/harness]] §7.6.

## Concepts

### [[concepts/harness]] {#harness}
The execution system between a model and a task. Internal components, the four-layer opening, and the
split between surface-specific and surface-independent axes.

### [[concepts/harness-engineering]] {#harness-engineering}
Five months with no hand-written code. The bottleneck was the environment, not the model — legibility,
mechanical enforcement, continuous garbage collection. §11 adds RRSI: a search that edits the
harness while the model stays frozen. The published scores are not adopted. §12 reads Anthropic's
AI-native SDLC playbook as the same split (context file, advisory skill, hook, human gate). The
plays were not run.

### [[concepts/thread-turn-item]] {#thread-turn-item}
The three conversation primitives. Item lifecycle, thread unloading (60 seconds) and capacity
eviction, the sticky semantics of turn overrides. §8.5: three weeks of drift (108/10/87, turn lineage, read state, open `codexErrorInfo`); 2026-10-20 re-check `79a19cbb3`: unchanged, + experimental `thread/sample`. §8.6: Claude Code's flat `session_id` + `uuid` alternative, JSONL transcripts, no unload timer.

### [[concepts/approval-gate]] {#approval-gate}
Approval as a protocol primitive rather than a UI convenience. Codex: ten server→client requests.
ACP: one `session/request_permission`. Without an answer the turn stalls. §7.9 adds availability as
a seventh gate property (Codex Guardian warmup, #49584) and where the gate lives behind the wire. §7.10: Claude Code's `can_use_tool` answer can rewrite the input; fail-open hook layer by default — opt-in `onFailure: "block"` since 2.1.295 (§7.8 addendum); the Desktop 2.42304.2 card is drawn from those fields, several of which the engine sends but the types omit (§7.10 rendered; 0.3.304/2.1.304 drift: approval wire unchanged, mod `decider: "person"`).

### [[concepts/agent-client-protocol]] {#agent-client-protocol}
Editor ↔ coding-agent JSON-RPC. Stable `protocolVersion` is `1`. Permission option kinds
`allow_once` · `allow_always` · `reject_once` · `reject_always`. Distinct from model `WireApi`.

### [[concepts/wire-protocol-boundary]] {#wire-protocol-boundary}
`WireApi` has one variant — Responses. The boundary deciding whether the core is reusable, and
`responses_lite` as a second request shape. 2026-10-19: Claude Code's `sdk.d.ts` as a second filtered contract. §7.5 (2026-10-20): under `incremental_tools` the lite tool list is a fold over history, not a request field.

### [[concepts/stateless-conversation-wire]] {#stateless-conversation-wire}
`store: false` plus no `previous_response_id` exempts you from session stores, id registries and
expiry handling.

### [[concepts/retained-reasoning]] {#retained-reasoning}
Retained reasoning is load-bearing design, not an optimisation. It disappears structurally when
crossing to Chat Completions.

### [[concepts/control-plane-execution-plane]] {#control-plane-execution-plane}
Separating the harness (loop, routing) from compute (files, commands), and the key separation that
boundary forces. §5.6 sharpens it to a **credential** boundary: control channel vs untrusted
execution.

### [[concepts/multi-agent-orchestration]] {#multi-agent-orchestration}
The layer *above* a harness. Durable work ledgers, persistent identity vs ephemeral session,
capacity-capped dispatch, two-channel liveness, and stateless coordination (no agent holds the
thread). Source-read from Gas Town and, at `3ef7fadd42`, from Gas City (the platform that model
was extracted into). **Not executed**.

### [[concepts/execution-environment-topology]] {#execution-environment-topology}
`none` / `openai_hosted` / `self_hosted`, the file-artifact asymmetry, the self-hosted lifecycle, the
two provider rosters.

### [[concepts/os-sandbox-policy]] {#os-sandbox-policy}
Four policy values and per-OS mechanisms. Two Windows modes, two independent network switches,
authority from OS package identity. Windows internals source-read 2026-09-30. Drift 2026-10-19: integrity checks observe-only, proxy DNS gating, mxc probe.

### [[concepts/capability-distribution]] {#capability-distribution}
Circulating plugins, marketplaces and skills. The vendor-neutral manifest, catalog versus installed
artifact, install ≠ enable ≠ share.

### [[concepts/provider-as-data]] {#provider-as-data}
Providers as data, not code branches. Command-backed token minting, and the deny-list on
project-local configuration. §6.6: the catalog itself is served (`model_catalog_url`, Claude's
`model-catalog/v1/catalog.json`) and a managed policy filters it — a fourth chooser. §6.7 (2026-10-20): the update channel is served data too — channel pointers, `channelUuid`, a rollout flag — and the release manifest shares the catalog's signing key (`harness-artifacts/04`).

### [[concepts/perception-model]] {#perception-model}
How an agent sees a screen. Four representations, **symmetry between perception and action**, the
cost ladder, diffs.

### [[concepts/indirect-prompt-injection]] {#indirect-prompt-injection}
The structural risk of this class. The attack chain (no attacker destination — a read across sessions, then one write), four mitigation categories and where products
stand, the unsolved status.

### [[concepts/credential-shielding]] {#credential-shielding}
Logging in without handing over the secret. Value hiding / element hiding / URL blocking, and
separating permission level from exposure.

### [[concepts/agent-client-design-language]] {#agent-client-design-language}
How ten agent clients render harness primitives — "Allow ⟨agent⟩ to ⟨verb⟩?", amber for "needs you",
a machine reviewer in the autonomy dial — and where their theories of supervision part.

### [[concepts/primary-source-verification]] {#primary-source-verification}
This repository's method of knowing. Grade vocabulary, preserving refutations, the record and traps
of the `llms.txt` technique. 2026-10-19: record the tag, not the string count; keep the counting script with the count.

## Topics

## Patterns

## Decisions

## Entities
