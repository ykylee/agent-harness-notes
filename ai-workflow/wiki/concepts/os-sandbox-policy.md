---
type: concept
status: active
last_ingested_from: docs/14-windows-sandbox.md + docs/02-app-server-protocol.md + browser-agents/10-aside-enforcement-and-native.md
related_pages: [concepts/approval-gate, concepts/control-plane-execution-plane, concepts/execution-environment-topology, concepts/primary-source-verification, concepts/credential-shielding, concepts/indirect-prompt-injection]
created: 2026-09-22
updated: 2026-09-26
---

# OS Sandbox Policy — defence inside the execution plane

- Purpose: protocol-level sandbox modes and their OS-level implementations (especially native Windows), plus the design principles a custom harness can carry over.
- Scope: the four policy values, per-OS mechanisms, the two Windows modes, the two network switches, the authority model
- Primary sources: generated schemas, `learn.chatgpt.com/docs/windows/windows-sandbox.md`, the `codex-rs/windows-sandbox-rs` source tree
- Updated: 2026-09-26 (Codex drift re-check against `e72da2b538`)

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | Protocol policy values | `readOnly` · `workspaceWrite` · `dangerFullAccess` · `externalSandbox` |
| 2 | Native Windows modes | `elevated` (preferred) · `unelevated` (fallback) · `mxc` (added 2026-09, behind `prefer_mxc`) |
| 3 | Default UI isolation | **a private desktop** — always on; the opt-out was removed 2026-09 |
| 4 | Network | **two switches** — "is it allowed at all" and "is it constrained by policy" |
| 5 | Source of authority | **OS package identity.** Never a path or a manifest string |
| 6 | Basis for the Windows internals | ⚠️ mostly **inferred from module names**; four modules confirmed and one refuted from their doc comments (§6) |

## §2 Protocol-level policy  {#s2-protocol-policy}

| Value | Meaning |
|---|---|
| `readOnly` | read-only filesystem |
| `workspaceWrite` | writes allowed within the specified roots |
| `dangerFullAccess` | unrestricted |
| `externalSandbox` | **the client manages the sandbox itself** |

An optional `networkAccess` setting controls outbound connectivity.

## §3 Per-OS mechanisms  {#s3-os-mechanisms}

| OS | Mechanism |
|---|---|
| **macOS** | Seatbelt policies via `sandbox-exec` with a `-p` profile matching the `--sandbox` mode. When restricted read access enables platform defaults, a **curated macOS platform policy** is appended instead of broadly allowing `/System` |
| **Linux** | `bwrap` plus `seccomp` |
| **Windows (WSL2)** | the Linux sandbox implementation |
| **Windows (native)** | a dedicated implementation |

> WSL1 was supported through Codex `0.114`. **From `0.115` the Linux sandbox moved to `bwrap`, so
> WSL1 is no longer supported.**

## §4 The two native Windows modes  {#s4-windows-modes}

```toml
[windows]
sandbox = "unelevated"          # or "elevated", or "mxc" (new)
# sandbox_private_desktop was removed 2026-09 (#46554); setting it now draws a warning
```

| Mode | Mechanism | Requirement |
|---|---|---|
| **`elevated`** (preferred) | dedicated lower-privilege sandbox users, filesystem permission boundaries, firewall rules, the local policy changes commands need | administrator-approved setup |
| **`unelevated`** (fallback) | a **restricted Windows token derived from your current user**, ACL-based filesystem boundaries, **environment-level offline controls** instead of the dedicated offline-user firewall rule | none |

> Use `elevated` when both are available. `unelevated` is the weaker mode that is "still useful when
> administrator-approved setup is blocked by local or enterprise policy."

Administrators can constrain which implementations are permitted through `requirements.toml` — a
policy can **require `elevated` and prevent fallback**; listing both permits either, and Codex
prefers `elevated` when no mode is selected. *(2026-09-26: the allowed set still names only the two
native modes and does not constrain the new `mxc` implementation, #46271.)*

> 📌 Note the shape: **the administrator artifact is a separate file from the user configuration**,
> and it expresses **an allowed set** rather than a single pinned value. Worth carrying over.

### §4.1 The private desktop  {#s4-1-private-desktop}

Both modes use **a private desktop for stronger UI isolation**. The `windows.sandbox_private_desktop`
opt-out back to `Winsta0\Default` existed at the 2026-09-15 snapshot and was **removed** by 2026-09-26
(#46554) — legacy sandboxes now always use a private desktop.

> A defence most harnesses forget — without desktop isolation, sandboxed GUI processes can reach the
> interactive desktop and drive other windows.

## §5 Network — two independent switches  {#s5-network}

The `workspace-write` default keeps network access off.

```toml
[sandbox_workspace_write]
network_access = true          # switch 1: is network allowed at all

[features.network_proxy]
enabled = true                 # switch 2: is that traffic constrained by policy
domains = { "api.openai.com" = "allow", "example.com" = "deny" }
```

> **Adding domain rules does not by itself enable the proxy.** The two switches are independent.

The security documentation also covers DNS rebinding protections, local and private destination
handling, and traffic that escapes the command network proxy — all areas a custom implementation must
**address explicitly rather than inherit.**

## §6 Implementation structure — labelled as inference  {#s6-implementation}

> ⚠️ **Inference warning**: what follows is read from **module names and layout** in
> `codex-rs/windows-sandbox-rs` and `windows-sandbox-service`, not from prose documentation. Treat it
> as **a map of the problem space, not a specification.** The meaning of the grade is in
> [[concepts/primary-source-verification]]. **2026-09-26:** reading module doc comments confirmed
> `wfp.rs`, `dpapi.rs`, `setup_mutex.rs`, `installation_record.rs` ✅ and refuted `hide_users.rs` ❌.

| Area | Modules |
|---|---|
| Package and process identity | `app_package.rs`, `package_identity.rs`, `service_identity.rs`, `identity.rs` |
| Token restriction | `token.rs`, `token_user.rs`, `token_groups_tests.rs` |
| Filesystem ACLs | `acl.rs`, `workspace_acl.rs`, `deny_read_acl.rs`, `deny_read_resolver.rs`, `deny_read_walker.rs`, `file_write.rs` |
| Symlink / reparse defence | `no_reparse_dir.rs`, `path_normalization.rs` |
| Network filtering | `wfp.rs` ✅ ("Installs the persistent Codex WFP filters for `account`"), `wfp_setup.rs` |
| Desktop isolation | `desktop.rs` |
| Account hygiene | `hide_users.rs` ❌ *not* desktop isolation, as first inferred — it hides the sandbox user's profile directory |
| Terminals | `conpty/`, `unified_exec/`, `stdio_bridge.rs` |
| Secret storage | `dpapi.rs` ✅ (`CryptProtectData`; decrypts sandbox-account passwords) |
| Elevation and setup | `elevated/`, `setup.rs`, `setup_launch.rs`, `setup_provisioning.rs`, `setup_mutex.rs`, `installation_record.rs` |
| Privileged service | `windows-sandbox-service`: `service.rs`, `ipc.rs`, `provisioning.rs`, `machine_policy.rs`, `package_lifecycle.rs`, `registered_runtime.rs` |
| Logging | `logging.rs` (`audit.rs` deleted 2026-09, #47943) |

Two structural conclusions:

1. **Elevated mode needs administrator elevation once, for setup — not necessarily a service.**
   *(Corrected 2026-09-26.)* This page first said a privileged service was required. `service_identity.rs`
   says unpackaged callers "may use ordinary elevated setup when it is absent"; the packaged app prefers
   the `windows-sandbox-service` provisioning service and falls back to the elevated helper (#46239).
   Still: **plan for an elevated setup step early**, and for a service lifecycle if you ship packaged.
2. **Setup is a first-class, resumable operation**, not a side effect of launching — hence
   `setup_mutex.rs`, `installation_record.rs` and the protocol methods in §8.

## §7 The authority model — a principle worth carrying  {#s7-authority}

A source comment states it plainly:

> "Select the requested runtime without inferring authority from directory or manifest text.
> Registered runners still require OS package identity and the exact staged runner image."

**Authority comes from OS package identity, never from a path or a manifest string.** That transfers
to any sandbox design.

## §8 The protocol surface, and what it says  {#s8-protocol-surface}

| Direction | Method | Role |
|---|---|---|
| C→S | `windowsSandbox/setupStart` | begin setup (the elevated path needs admin approval) |
| C→S | `windowsSandbox/readiness` | query readiness. Takes no params |
| S→C | `windowsSandbox/setupCompleted` | setup finished |
| S→C | `windows/worldWritableWarning` | a world-writable path was detected — ⚠️ vestigial: nothing emits it (§8 note) |

> The existence of a dedicated **readiness** RPC and a **setupCompleted** notification says setup is
> asynchronous, can outlive a turn, and must surface in the UI. A custom harness targeting Windows
> needs the same two-phase shape — **you cannot treat sandbox availability as a boot-time boolean.**

`windows/worldWritableWarning` *looked* worth copying as a concept: a sandbox can be correctly configured
and still be undermined by a permissive path, so detection should be separate from enforcement.
**Corrected 2026-09-26:** the notification is in the schema, but nothing in app-server or core emits it at
either revision; the detector was unused at the snapshot and `audit.rs` is now deleted. The idea stands on
its own merits — Codex just does not implement it. A protocol entry is not evidence of a behaviour.

## §8.5 Observation — the expressiveness of a permission policy  {#s8-5-policy-expressiveness}

App Server's sandbox policy has **four values**, with finer control attached at approval time through
`ExecPolicyAmendment`. Aside's daemon holds **policy as a declarative schema.**

| Matcher | Fields |
|---|---|
| `tool` | name or **glob** (`mcp__*`) plus **per-argument matchers** (`{$:"eq"\|"regex"}`, keyed by input field name) |
| `browser` | `read`/`modify`/`download` plus URL glob |
| `network` | URL or domain glob |

There are **four** buckets — `allow`/`approved`/`deny`/`ask` — with `default` at `allow`.
Files use `readableRoots`/`writableRoots` plus `outsideRead`/`outsideWrite` (`deny`/`ask`).

> 📌 Not "allow bash" but **"allow bash only when its first argument matches this regex."**
> Expressiveness worth copying.
>
> 📌 **Permission level and sandbox are different axes** — even `full-access` keeps
> `sandbox.enabled: true`. Highest privilege does not mean the sandbox is off. The same pattern
> applies to credentials ([[concepts/credential-shielding]]).

## §8.6 Observation — when a browser agent crosses into the OS  {#s8-6-computer-use}

Separately from browser automation, Aside ships a native process called **`Aside Computer Use`**. It
appears in no product document.

| Capability | Symbols |
|---|---|
| System-wide accessibility tree | `AXUIElementRef`, **`AXTreeSerializer`** |
| Event tap (observe and inject) | `CGEventTapCreate/Enable` |
| Screen capture and image analysis | `ScreenCaptureKit`, **`Vision.framework`** |
| Contacts | **`Contacts.framework`** |

> 📌 The perception philosophy is consistent — just as the browser uses an accessibility tree, the OS
> layer serialises one.
> ⚠️ But **the reach is the whole desktop, not a tab.** Read together with prompt injection
> ([[concepts/indirect-prompt-injection]]), a fooled agent's range extends beyond the browser.

## §9 Read next  {#s9-next}

- [[concepts/approval-gate]] — human intervention where the sandbox cannot help
- [[concepts/credential-shielding]] — the separation of permission level from exposure
- [[concepts/control-plane-execution-plane]] — the plane this defence sits on
- Original: [`docs/14-windows-sandbox.md`](../../../docs/14-windows-sandbox.md)
