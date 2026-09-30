# 14. Windows Sandbox

> Sources: `learn.chatgpt.com/docs/windows/windows-sandbox.md`,
> `learn.chatgpt.com/docs/agent-approvals-security.md` (§OS-level sandbox, §Network access),
> plus the `codex-rs/windows-sandbox-rs` and `codex-rs/windows-sandbox-service` source trees.
> Extracted 2026-09-15.
> Drift-checked against `openai/codex@e72da2b538` (2026-09-26); internals source-read at HEAD
> `bcd6d9ab6b` (2026-09-30).

## 1. Where Windows sits among the OS sandboxes

| OS | Mechanism |
|---|---|
| **macOS** | Seatbelt policies via `sandbox-exec` with a `-p` profile matching the `--sandbox` mode. When restricted read access enables platform defaults, a curated macOS platform policy is appended instead of broadly allowing `/System` |
| **Linux** | `bwrap` + `seccomp` |
| **Windows (WSL2)** | The Linux sandbox implementation |
| **Windows (native)** | A dedicated Windows sandbox implementation — the subject of this document |

> WSL1 was supported through Codex `0.114`. **Starting in `0.115` the Linux sandbox moved to `bwrap`,
> so WSL1 is no longer supported.**

The IDE extension can be kept inside WSL2:

```json
{ "chatgpt.runCodexInWindowsSubsystemForLinux": true }
```

This makes the extension inherit Linux sandbox semantics for commands, approvals, and filesystem
access even on a Windows host.

## 2. Two native modes

```toml
[windows]
sandbox = "unelevated"          # or "elevated", or "mxc"
```

*(2026-09-26: `windows.sandbox_private_desktop` was removed — strict config now warns "Remove
windows.sandbox_private_desktop; legacy Windows sandboxes always use a private desktop"; #46554.)*

A third value, **`mxc`**, was added 2026-09-26 (#46271): `WindowsSandboxModeToml::Mxc`, gated by the
`prefer_mxc` feature. The protocol type is `WindowsSandboxImplementation = "elevated" | "unelevated" | "mxc"`.

### `elevated` — preferred

> It uses **dedicated lower-privilege sandbox users**, **filesystem permission boundaries**,
> **firewall rules**, and **local policy changes** needed for commands that run in the sandbox.

Requires administrator-approved setup.

### `unelevated` — fallback

> It runs commands with a **restricted Windows token derived from your current user**, applies
> **ACL-based filesystem boundaries**, and uses **environment-level offline controls** instead of the
> dedicated offline-user firewall rule.

> "It's weaker than `elevated`, but it is still useful when administrator-approved setup is blocked
> by local or enterprise policy."

**If both are available, use `elevated`.**

### Private desktop

Both modes use a **private desktop for stronger UI isolation**, with no opt-out
*(2026-09-26: was "by default; set `windows.sandbox_private_desktop = false` for the older
`Winsta0\Default` behavior" — the key was removed, #46554)*.

> This is a defense most harnesses forget: without desktop isolation, sandboxed GUI processes can
> reach the interactive desktop and drive other windows.

## 3. Enterprise constraint via `requirements.toml`

Administrators can constrain which native sandbox implementations Codex may use through
`requirements.toml`. A policy can **require `elevated` and prevent fallback to `unelevated`**;
listing both permits either, and Codex prefers `elevated` when no mode is selected.
`windows.allowed_sandbox_implementations` still lists only `elevated` / `unelevated` and does **not**
constrain `mxc` *(2026-09-26, #46271)*.

> Note the shape: the *admin* artifact is a separate file from the *user* config, and it expresses
> allowed sets rather than a single value. Copy that separation — a policy that can only pin one
> value cannot express "either of these two, prefer the stronger."

## 4. Windows version support

| Version | Support | Notes |
|---|---|---|
| **Windows 11** | Recommended | Best baseline; use for standardized enterprise deployment |
| Recent, fully updated **Windows 10** | Best effort | Less reliable than 11. Depends on modern console support including **ConPTY** — in practice **1809 or newer** |
| Older Windows 10 builds | Not recommended | |

ConPTY dependency is the practical floor. Any custom harness that runs interactive terminals on
Windows inherits the same constraint.

## 5. Network policy

Default `workspace-write` keeps network access off:

```toml
[sandbox_workspace_write]
network_access = true
```

Enabling access is separate from *constraining* it. The command network proxy does that:

```toml
[features.network_proxy]
enabled = true
domains = { "api.openai.com" = "allow", "example.com" = "deny" }
```

> **Adding domain rules does not enable the proxy by itself.** Two independent switches —
> "is network allowed at all" and "is that traffic constrained to a policy."

One-off CLI forms:

```bash
codex -c 'features.network_proxy=true' \
      -c 'sandbox_workspace_write.network_access=true'

codex -c 'features.network_proxy.enabled=true' \
      -c 'features.network_proxy.domains={ "api.openai.com" = "allow", "example.com" = "deny" }' \
      -c 'sandbox_workspace_write.network_access=true'
```

The security doc also covers DNS rebinding protections, local and private destination handling, and
traffic that escapes the command network proxy — all areas a custom implementation must address
explicitly rather than inherit.

## 6. What the implementation looks like

> Source-read 2026-09-30 against `codex-rs/windows-sandbox-rs` and `windows-sandbox-service` at
> `openai/codex` HEAD `bcd6d9ab6b`. Official prose (`windows-sandbox.md`) names the modes and the
> nouns (dedicated users, ACLs, firewall, restricted token, private desktop). The Win32 calls below
> are from the Rust sources. This environment did not execute the sandbox on Windows.
> Drift-checked against `e72da2b538` (2026-09-26); internals promoted 2026-09-30.

### 6.1 Token restriction (`token.rs`)

`CreateRestrictedToken` with flags `DISABLE_MAX_PRIVILEGE | LUA_TOKEN | WRITE_RESTRICTED`. The
restricting SID list is **capabilities…, extra restricting SIDs…, logon SID, Everyone**. Elevated
backends also put the dedicated sandbox-account user SID in that list
(`create_*_token_with_caps_and_user_from`). After creation the token gets:

- a **default DACL** of logon-SID `GENERIC_ALL` plus OWNER RIGHTS (`S-1-3-4`) `READ_CONTROL` only,
  so a different logon on the same account cannot rewrite the DACL
- `SeChangeNotifyPrivilege` re-enabled (`AdjustTokenPrivileges`)

This is the `unelevated` path's "restricted Windows token derived from your current user," and the
elevated path applies the same restriction shape to the dedicated sandbox account.

### 6.2 Filesystem ACLs (`acl.rs`, `workspace_acl.rs`, `deny_read_acl.rs`)

DACLs are read and written with `GetSecurityInfo` / `GetNamedSecurityInfoW` /
`SetNamedSecurityInfoW` / `SetEntriesInAclW` on `SE_FILE_OBJECT`. Deny ACEs use `DENY_ACCESS`:

- `add_deny_read_ace` — mask `FILE_GENERIC_READ | GENERIC_READ`
- `add_deny_write_ace` — write data/EA/attributes, `DELETE`, `FILE_DELETE_CHILD`

`workspace_acl` deny-writes `.codex` and `.agents` under the command cwd when those directories
exist. `deny_read_acl` plans **both the lexical path and the canonical target** (so a reparse cannot
be read through the resolved location), refuses a filesystem-root deny ACE, and materializes missing
denied paths as directories before applying the ACE so a later create-then-read cannot skip the
deny. TrustedInstaller (`S-1-5-80-956008885-…`) is treated as a trusted system owner.

### 6.3 Network: WFP plus Windows Firewall

Two stacks, both real in source.

**Windows Filtering Platform** (`wfp.rs`, `wfp/filter_specs.rs`) — a persistent provider and sublayer
with Codex-owned GUIDs (`FwpmProviderAdd0` / `FwpmSubLayerAdd0` / `FwpmFilterAdd0`,
`FWPM_FILTER_FLAG_PERSISTENT`). `install_wfp_filters_for_account` installs **12**
`FWP_ACTION_BLOCK` filters matched on `FWPM_CONDITION_ALE_USER_ID` for the sandbox account:

| What is blocked | Layers |
|---|---|
| ICMP (and ICMPv6) connect + resource assignment | `ALE_AUTH_CONNECT_*`, `ALE_RESOURCE_ASSIGNMENT_*` |
| DNS TCP/UDP port 53 | `ALE_AUTH_CONNECT_V4/V6` |
| DNS-over-TLS port 853 | same |
| SMB ports 445 and 139 | same |

`NAME_RESOLUTION_CACHE` filters are omitted; the comment records `FWP_E_OUT_OF_BOUNDS` during
validation.

**Windows Firewall** (`setup_provisioning/firewall.rs`) — `INetFwPolicy2` / `INetFwRule3` rules with
stable names (`codex_sandbox_offline_block_outbound`, inbound, loopback TCP except proxy, loopback
UDP). This is the "dedicated offline-user firewall rule" in the official `elevated` description.

### 6.4 Private desktop (`desktop.rs`) and account hiding (`hide_users.rs`)

`CreateDesktopW` names `CodexSandboxDesktop-` plus a 32-hex nonce. The process startup desktop is
`Winsta0\<name>`. The DACL (SDDL) grants the owner user `DESKTOP_ALL_ACCESS` and the sandbox SID
participant rights **without** `WRITE_DAC` / `WRITE_OWNER` / `DELETE`. Desktops are cached per
`(sandbox SID, DesktopPolicy)` so GUI hooks do not cross permission policies.

`hide_users.rs` is a **different** control: it writes
`HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList` so the
sandbox accounts stay off the login UI, and marks the profile directory hidden+system. It is not
desktop isolation.

### 6.5 Other confirmed pieces

| Area | Source | Mechanism |
|---|---|---|
| Reparse defence | `no_reparse_dir.rs` | directory opens with `OBJ_DONT_REPARSE`; `STATUS_REPARSE_POINT_ENCOUNTERED` is fatal |
| Secrets | `dpapi.rs` | `CryptProtectData` with `CRYPTPROTECT_UI_FORBIDDEN \| CRYPTPROTECT_LOCAL_MACHINE` so elevated and unelevated processes can decrypt |
| Logging | `logging.rs` | `audit.rs` was deleted 2026-09 together with the `hide_world_writable_warning` config edit (#47943) |

Module locator (2026-09-26 layout, kept as a map):

| Area | Modules |
|---|---|
| Package / process identity | `app_package.rs`, `package_identity.rs`, `service_identity.rs`, `identity.rs` |
| Token restriction | `token.rs`, `token_user.rs`, `token_groups_tests.rs` |
| Filesystem ACLs | `acl.rs`, `workspace_acl.rs`, `deny_read_acl.rs`, `deny_read_resolver.rs`, `deny_read_walker.rs`, `file_write.rs` |
| Symlink / reparse defense | `no_reparse_dir.rs`, `path_normalization.rs` |
| Network filtering | `wfp.rs`, `wfp_setup.rs`, `setup_provisioning/firewall.rs` |
| Desktop isolation | `desktop.rs` |
| Login-UI hiding | `hide_users.rs` |
| Terminals | `conpty/`, `unified_exec/`, `stdio_bridge.rs` |
| Secret storage | `dpapi.rs` |
| Elevation & setup | `elevated/`, `setup.rs`, `setup_launch.rs`, `setup_provisioning.rs`, `setup_mutex.rs`, `installation_record.rs`; `provisioning_client`, `runtime_ownership`, `uninstall_windows/` |
| Launch environment | `environment_transport.rs`, `launch_environment.rs` (#47919) |
| Privileged service | `windows-sandbox-service`: `service.rs`, `ipc.rs`, `provisioning.rs`, `machine_policy.rs`, `package_lifecycle.rs`, `registered_runtime.rs` |
| Logging | `logging.rs` |

Two structural takeaways:

1. **The privileged service is the packaged path, not a requirement.** `windows-sandbox-service` is a
   separate crate with its own IPC, provisioning, and machine-policy handling, but what elevated mode
   actually needs is **elevation (admin) once, for setup**
   *(corrected 2026-09-26: was "needs a privileged service… not something a single user-mode process can
   do"; `service_identity.rs` at base: "Unpackaged callers keep the legacy service lookup and may use
   ordinary elevated setup when it is absent"; head prefers the provisioning service and falls back to
   the elevated helper, #46239)*. Plan for a service lifecycle only if you ship a packaged install.
2. **Setup is a first-class, resumable operation**, not a side effect of launching. Hence
   `setup_mutex.rs`, `installation_record.rs`, and the protocol methods below.

Also since baseline: the sandbox token is scoped to the logon session (#47361), and `.aws` is protected
under writable roots (#48176) *(2026-09-26)*.

One source comment states the authority model plainly:

> "Select the requested runtime without inferring authority from directory or manifest text.
> Registered runners still require OS package identity and the exact staged runner image."

Authority comes from **OS package identity**, never from a path or a manifest string. That principle
transfers to any sandbox design.

## 7. Protocol surface

| Direction | Method | Role |
|---|---|---|
| Client → Server | `windowsSandbox/setupStart` | Begin sandbox setup (the elevated path needs admin approval) |
| Client → Server | `windowsSandbox/readiness` | Query readiness. Takes no params |
| Server → Client | `windowsSandbox/setupCompleted` | Setup finished |
| Server → Client | `windows/worldWritableWarning` | A world-writable path was detected — ⚠️ vestigial: *(corrected 2026-09-26: in the schema, but nothing in app-server/core emits it at base or head)* |

> The presence of a dedicated **readiness** RPC and a **setupCompleted** notification says that setup
> is asynchronous, can outlive a turn, and must be surfaced in the UI. A custom harness targeting
> Windows needs the same two-phase shape — you cannot treat sandbox availability as a boot-time
> boolean.

`windows/worldWritableWarning` is worth copying as a *concept*: the sandbox can be correctly configured
and still be undermined by a permissive path. *(corrected 2026-09-26: Codex itself does not implement
it — the detector was unused at base and is now deleted (#47943), so the notification is a vestigial
protocol entry, not evidence of a separate detection path.)*

## 8. Checklist for a custom Windows sandbox

- [ ] Decide early whether you ship a **privileged service** *(corrected 2026-09-26: it is the packaged path; admin-elevated setup suffices otherwise)*
- [ ] Implement both a strong mode and a **degraded fallback** — enterprise policy will block setup
- [ ] Make setup **asynchronous, resumable, and observable** (start / readiness / completed)
- [ ] Derive authority from **OS package identity**, never from paths or manifest text
- [ ] Use a **private desktop** *(2026-09-26: Codex now always does, with no opt-out; #46554)*
- [ ] Treat "network allowed" and "network constrained" as **two separate switches**
- [ ] Handle reparse points and path normalization, or ACL boundaries are bypassable
- [ ] Target ConPTY; it sets your minimum Windows version (10 1809+)
- [ ] Let administrators express an **allowed set** of implementations, not a single pinned value
- [ ] Warn on world-writable paths even when the sandbox itself is configured correctly
      *(Codex's own warning is vestigial — see §7; corrected 2026-09-26)*
