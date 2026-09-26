<!-- standard-ai-workflow-kit: v1.10.0 -->

# Master Knowledge Index

> Format and rules in [`./SCHEMA.md`](./SCHEMA.md). Entries are added as ingests create pages.
> The sources are `docs/` (the Codex harness), `browser-agents/` (browser-type agents) and, since
> 2026-09-26, `strands/` (the Strands SDK and harness) — this wiki **re-indexes them by concept.** The cross-study synthesis is [`SYNTHESIS.md`](../../SYNTHESIS.md).
>
> For the split between **surface-specific** axes (perception, injection, credentials) and
> **surface-independent** ones (approval, providers, capability, planes), see [[concepts/harness]] §7.6.

## Concepts

### [[concepts/harness]] {#harness}
The execution system between a model and a task. Internal components, the four-layer opening, and the
split between surface-specific and surface-independent axes.

### [[concepts/harness-engineering]] {#harness-engineering}
Five months with no hand-written code. The bottleneck was the environment, not the model — legibility,
mechanical enforcement, continuous garbage collection.

### [[concepts/thread-turn-item]] {#thread-turn-item}
The three conversation primitives. Item lifecycle, thread unloading (60 seconds) and capacity
eviction, the sticky semantics of turn overrides.

### [[concepts/approval-gate]] {#approval-gate}
Approval as a protocol primitive rather than a UI convenience. Ten server→client requests; without
them the turn stalls.

### [[concepts/wire-protocol-boundary]] {#wire-protocol-boundary}
`WireApi` has one variant — Responses. The boundary deciding whether the core is reusable, and
`responses_lite` as a second request shape.

### [[concepts/stateless-conversation-wire]] {#stateless-conversation-wire}
`store: false` plus no `previous_response_id` exempts you from session stores, id registries and
expiry handling.

### [[concepts/retained-reasoning]] {#retained-reasoning}
Retained reasoning is load-bearing design, not an optimisation. It disappears structurally when
crossing to Chat Completions.

### [[concepts/control-plane-execution-plane]] {#control-plane-execution-plane}
Separating the harness (loop, routing) from compute (files, commands), and the key separation that
boundary forces.

### [[concepts/execution-environment-topology]] {#execution-environment-topology}
`none` / `openai_hosted` / `self_hosted`, the file-artifact asymmetry, the self-hosted lifecycle, the
two provider rosters.

### [[concepts/os-sandbox-policy]] {#os-sandbox-policy}
Four policy values and per-OS mechanisms. Two Windows modes, two independent network switches,
authority from OS package identity.

### [[concepts/capability-distribution]] {#capability-distribution}
Circulating plugins, marketplaces and skills. The vendor-neutral manifest, catalog versus installed
artifact, install ≠ enable ≠ share.

### [[concepts/provider-as-data]] {#provider-as-data}
Providers as data, not code branches. Command-backed token minting, and the deny-list on
project-local configuration.

### [[concepts/perception-model]] {#perception-model}
How an agent sees a screen. Four representations, **symmetry between perception and action**, the
cost ladder, diffs.

### [[concepts/indirect-prompt-injection]] {#indirect-prompt-injection}
The structural risk of this class. The attack chain (no attacker destination — a read across sessions, then one write), four mitigation categories and where products
stand, the unsolved status.

### [[concepts/credential-shielding]] {#credential-shielding}
Logging in without handing over the secret. Value hiding / element hiding / URL blocking, and
separating permission level from exposure.

### [[concepts/primary-source-verification]] {#primary-source-verification}
This repository's method of knowing. Grade vocabulary, preserving refutations, the record and traps
of the `llms.txt` technique.

## Topics

## Patterns

## Decisions

## Entities
