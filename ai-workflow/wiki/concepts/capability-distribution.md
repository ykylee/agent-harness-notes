---
type: concept
status: active
last_ingested_from: docs/13-marketplace-and-plugins.md + docs/10-agents-api-tools.md + docs/12-product-surface.md + browser-agents/11-dia-and-neon.md + browser-agents/08-aside-code-level.md
related_pages: [concepts/execution-environment-topology, concepts/harness, concepts/provider-as-data]
created: 2026-09-22
updated: 2026-09-23
---

# Capability Distribution — how plugins, marketplaces and skills circulate

- Purpose: how capabilities (skills and MCP) are packaged, distributed, installed and enabled — and what to know before inventing your own format.
- Scope: the model in a paragraph, the portable manifest, catalog format, the install cache, three verbs, the protocol surface
- Primary sources: `developers.openai.com/plugins/build/plugins.md`, App Server `ClientRequest`
- Updated: 2026-09-23

## §1 TL;DR  {#s1-tldr}

| # | Item | Value |
|---|---|---|
| 1 | **plugin** | a folder packaging skills, MCP configuration, or both. **The unit of capability** |
| 2 | **marketplace** | a JSON catalog listing plugins and where to fetch each. **The unit of distribution and policy** |
| 3 | Identifier | `plugin-name@marketplace-name` — the same in config, protocol and UI |
| 4 | Manifest | a **vendor-neutral open schema** (`agent-plugins.org`). Claude-compatible manifests are accepted too |
| 5 | Three verbs | **install ≠ enable ≠ share** |
| 6 | Failure semantics | an unresolvable entry is **skipped**, not allowed to fail the catalog |

## §2 Before you invent a format  {#s2-open-schema}

```json
{ "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", ... }
```

`agent-plugins.org` is a vendor-neutral schema host, and Codex explicitly accepts **Claude-compatible
manifests** and a legacy path (`$REPO_ROOT/.claude-plugin/marketplace.json`).

> Inventing your own plugin format means **giving up the ability to consume packages that already
> exist.** Adopting the portable manifest and namespacing your additions under
> `extensions.<your-org>` is cheaper — which is exactly what OpenAI does with `extensions.com.openai`.

### §2.1 The root/overlay split  {#s2-1-root-overlay}

| Location | Holds |
|---|---|
| **root** (`plugin.json`) | identity and metadata — `name`, `version`, `description`, `author`, `license`, `keywords` |
| **overlay** (`extensions.com.openai`) | presentation, MCP mappings, lifecycle hooks — `interface`, `apps`, `hooks` |

**A split worth imitating.** `name` must be stable **kebab-case** — hosts use it as the plugin
identifier *and* the component namespace.

## §3 Catalog format  {#s3-catalog}

```json
{
  "name": "local-example-plugins",
  "interface": { "displayName": "Local Example Plugins" },
  "plugins": [{
    "name": "my-plugin",
    "source": { "source": "local", "path": "./plugins/my-plugin" },
    "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
    "category": "Productivity"
  }]
}
```

| Field | Rule |
|---|---|
| top-level `name` | identifies the marketplace. Becomes the `@marketplace` half of a plugin id |
| `plugins[].policy.installation` | `AVAILABLE` \| `INSTALLED_BY_DEFAULT` \| `NOT_AVAILABLE` |
| `plugins[].policy.authentication` | whether auth happens on install or first use (`ON_INSTALL`) |

### §3.1 Four source kinds  {#s3-1-sources}

| Kind | Shape |
|---|---|
| `local` | `{ "source": "local", "path": "./plugins/my-plugin" }` — relative to the marketplace root; a plain string is also accepted |
| `url` (git, repo root) | `{ "source": "url", "url": "...git", "ref": "main" }` |
| `git-subdir` | `{ "source": "git-subdir", "url": "...", "path": "./plugins/x", "ref": "main" }` |
| `npm` | `{ "source": "npm", "package": "@example/codex-plugin", "version": "^1.2.0", "registry": "..." }` |

- Git entries accept a **`ref` or `sha`** selector
- npm: `version` accepts versions, dist tags and ranges but **not path or URL selectors**. `registry`
  must be **HTTPS without embedded credentials, query or fragment**
- **The package is downloaded without running lifecycle scripts**

### §3.2 Failure semantics worth copying  {#s3-2-failure}

> If a source cannot be resolved, Codex **skips that plugin entry rather than failing the whole
> marketplace.**

One bad entry must not take down a team's entire catalog.

## §4 Separating the catalog from the installed artifact  {#s4-catalog-vs-installed}

| Catalog location | Scope |
|---|---|
| `$REPO_ROOT/.agents/plugins/marketplace.json` | repository |
| `~/.agents/plugins/marketplace.json` | personal |
| `$REPO_ROOT/.claude-plugin/marketplace.json` | legacy compatibility |

Install cache: `~/.codex/plugins/cache/$MARKETPLACE_NAME/$PLUGIN_NAME/$VERSION/`

For a local plugin `$VERSION` is the literal `local`, and **the host loads the installed copy from
the cache path rather than the marketplace entry.** Editing the source folder therefore requires a
refresh — **a deliberate separation of "catalog" from "installed artifact."**

## §5 install ≠ enable ≠ share  {#s5-three-verbs}

```toml
[plugins."my-plugin@local-repo"]
enabled = true
```

> During a marketplace refresh Codex can install or refresh files for plugins **even when
> `enabled = false`**, keeping policy and payload independent. (Connected services still require
> authentication.)

Install and enable state resolves across user (`~/.codex/config.toml`), repository, cloud-managed and
system configuration. **Decide the precedence order before you ship.**

## §6 How the Agents API loads them  {#s6-agents-api}

| Environment | Method |
|---|---|
| **self-hosted** | copy the plugin into the environment and add its **absolute path** to `environment.capability_directories`. Select the **plugin root** (the directory containing `.codex-plugin/plugin.json`) |
| **openai-hosted** | **one ZIP per plugin** in `environment.plugins`. Each ZIP holds one plugin folder containing `.codex-plugin/plugin.json`, and **the request's name and description must match the manifest** |

> For multiple plugins, list each root. **A parent directory can discover nested skills but does not
> load every child plugin's MCP configuration.**
> Each session gets its own environment, and **the root agent and its subagents share it.**

Path rules (repeated everywhere, so enforce them once): **start with `./`, stay inside the plugin,
contain no `..` components.**

## §7 Protocol surface  {#s7-protocol}

```
marketplace/add        marketplace/remove      marketplace/upgrade
plugin/list            plugin/installed        plugin/read
plugin/install         plugin/uninstall        plugin/reconcile
plugin/skill/read
plugin/share/save      plugin/share/list       plugin/share/checkout
plugin/share/delete    plugin/share/updateTargets
app/list               app/read                app/installed
skills/list            skills/extraRoots/set   skills/config/write
hooks/list
```

| Item | Why it is easy to miss |
|---|---|
| **`plugin/reconcile`** | catalogs drift. "Make installed state match configured state" needs to be an explicit operation, not something done implicitly at startup |
| **`plugin/share/*`** | a separate concern from installing — publishing to a workspace and checking out are not marketplace consumption |
| `skills/extraRoots/set` | lets a client add skill search roots at runtime, independent of plugins |

> ⚠️ `disabledPluginIds` currently **saves the selection without actually filtering capabilities.**

## §8.5 Observation — three orthogonal axes of reuse  {#s8-5-reuse-axes}

Plugins and marketplaces are the unit of **distribution.** Separately, browser-type agents each
solved **"how do you turn a repeated delegation into a reusable unit?"** — on three different axes.

| Product | Name | Axis | Contents |
|---|---|---|---|
| **Opera Neon** | **Cards** | **task type** | "handle this kind of work like this." Grouped into decks, working across Chat, Do and Research |
| Dia | Skills | **invocation** | reusable routines called by name |
| **Aside** | **Routines** | **time** | `cron` (start a new task) vs. `heartbeat` (wake an existing chat and continue) |

> 📌 **The three axes are orthogonal.** One product could have all three; none does yet. Aside's
> cron/heartbeat distinction in particular has no counterpart — recurring work carries two different
> meanings, and ordinary schedulers give only the first. An agent with conversational context needs
> the second.
>
> Aside goes further and **scans for recurring work to propose routines**, solving ahead of the user
> the problem that they do not discover their own reusable units.

## §8.6 Observation — hand-built site skills  {#s8-6-builtin-skills}

Aside ships **built-in skills** for Slack, Gmail, Notion, Google Docs/Sheets/Search, YouTube,
LinkedIn and iMessage, and its guide instructs agents to "check for one before driving a site through
`snapshot()` by hand."

> ⚠️ This **partially overturns** the narrative that the surface is the browser itself rather than an
> integration list. Generic browsing is the fallback; major sites have a dedicated path. Pragmatic —
> but **read it alongside vendor self-reported benchmarks**: if the benchmark tasks include those
> sites, the score may be measuring skill coverage rather than general capability.

## §9 Read next  {#s9-next}

- [[concepts/execution-environment-topology]] — the environment plugins load into
- [[concepts/harness]] §7 — the capability system's share of the surface
- Originals: [`docs/13-marketplace-and-plugins.md`](../../../docs/13-marketplace-and-plugins.md), [`docs/10-agents-api-tools.md`](../../../docs/10-agents-api-tools.md) §4
