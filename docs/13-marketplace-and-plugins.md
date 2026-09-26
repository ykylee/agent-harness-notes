# 13. Marketplace and Plugin Distribution

> Sources: `developers.openai.com/plugins/build/plugins.md` (29KB, read as raw Markdown),
> `developers.openai.com/plugins.md` index, and the plugin/marketplace methods in the App Server
> protocol. Extracted 2026-09-15.
> Drift-checked against `openai/codex@e72da2b538` (2026-09-26); changes marked *(2026-09-26)*.

## 1. The model in one paragraph

A **plugin** is a folder that packages skills, MCP server configuration, or both.
A **marketplace** is a JSON catalog that lists plugins and where to fetch each one from.
Marketplaces are the unit of distribution and policy; plugins are the unit of capability.

> "A marketplace is a JSON catalog of plugins." It can hold one plugin while you test, then grow
> into a curated catalog.

## 2. There is an open schema — worth knowing before you invent one

The portable plugin manifest declares:

```json
{ "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", ... }
```

`agent-plugins.org` is a vendor-neutral schema host, and Codex explicitly accepts
**Claude-compatible manifests** and a legacy marketplace path
(`$REPO_ROOT/.claude-plugin/marketplace.json`).

> If your harness invents its own plugin format, you give up the ability to consume packages that
> already exist. Adopting the portable manifest and treating your own additions as a namespaced
> `extensions.<your-org>` object is the cheaper path — which is exactly what OpenAI does with
> `extensions.com.openai`.

## 3. Marketplace catalog format

```json
{
  "name": "local-example-plugins",
  "interface": { "displayName": "Local Example Plugins" },
  "plugins": [
    {
      "name": "my-plugin",
      "source": { "source": "local", "path": "./plugins/my-plugin" },
      "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
      "category": "Productivity"
    }
  ]
}
```

| Field | Rule |
|---|---|
| `name` (top level) | Identifies the marketplace. Becomes the `@marketplace` half of a plugin id |
| `interface.displayName` | Title shown in the picker |
| `plugins[]` | One object per plugin |
| `plugins[].name` | Plugin entry name |
| `plugins[].source` | Where to fetch it — see below |
| `plugins[].policy.installation` | `AVAILABLE` \| `INSTALLED_BY_DEFAULT` \| `NOT_AVAILABLE` |
| `plugins[].policy.authentication` | Whether auth happens on install or on first use (`ON_INSTALL`) |
| `plugins[].category` | e.g. `Productivity` |

> `policy.installation`, `policy.authentication`, and `category` should always be present on each entry.

### Source kinds (four)

```json
// local — path relative to the marketplace root, "./"-prefixed, inside that root
{ "source": "local", "path": "./plugins/my-plugin" }
// a plain string "./plugins/my-plugin" is also accepted for local entries

// git, plugin at the repository root
{ "source": "url", "url": "https://github.com/example/codex-plugins.git", "ref": "main" }

// git, plugin in a subdirectory
{ "source": "git-subdir", "url": "...", "path": "./plugins/remote-helper", "ref": "main" }

// npm registry
{ "source": "npm", "package": "@example/codex-plugin",
  "version": "^1.2.0", "registry": "https://registry.npmjs.org" }
```

- Git entries accept **`ref` or `sha`** selectors
- npm: `package` required (scopes allowed); `version` optional and accepts versions, **dist tags,
  and ranges — but not path or URL selectors**; `registry` optional, must be **HTTPS without embedded
  credentials, query, or fragment**
- **The package is downloaded without running lifecycle scripts.** The `npm` CLI must be installed;
  registry auth comes from its configuration

### Failure semantics worth copying

> If Codex can't resolve a marketplace entry's source, **it skips that plugin entry instead of
> failing the whole marketplace.**

One bad entry must not take down a team's entire catalog.

## 4. Where catalogs live, and where plugins land

**Catalog locations**

| Path | Scope |
|---|---|
| `$REPO_ROOT/.agents/plugins/marketplace.json` | Repo |
| `~/.agents/plugins/marketplace.json` | Personal |
| `$REPO_ROOT/.claude-plugin/marketplace.json` | Legacy compatibility |

**Install cache**

```
~/.codex/plugins/cache/$MARKETPLACE_NAME/$PLUGIN_NAME/$VERSION/
```

For local plugins `$VERSION` is the literal `local`, and **the host loads the installed copy from the
cache path rather than directly from the marketplace entry.** Editing the source folder therefore
requires a refresh — a deliberate separation of "catalog" from "installed artifact."

`source.path` resolves **relative to the marketplace root**, not relative to `.agents/plugins/`.

## 5. CLI surface

```bash
codex plugin marketplace add owner/repo
codex plugin marketplace add owner/repo --ref main
codex plugin marketplace add https://github.com/example/plugins.git --sparse .agents/plugins
codex plugin marketplace add ./local-marketplace-root

codex plugin marketplace list
codex plugin marketplace upgrade [marketplace-name]
codex plugin marketplace remove marketplace-name
```

Accepted sources: GitHub shorthand (`owner/repo`, `owner/repo@ref`), HTTP/HTTPS git URLs, SSH git
URLs, and local marketplace roots. `--ref` pins a ref; `--sparse PATH` (repeatable) does a sparse
checkout and is **valid only for git sources**.

`list` prints each marketplace under consideration **and the root path it resolves from**, including
local defaults and configured snapshots — a genuinely useful debugging affordance.

## 6. Enable / disable, and the plugin id format

```toml
# repo .codex/config.toml
[plugins."my-plugin@local-repo"]
enabled = true
```

The quoted key is **`plugin-name@marketplace-name`** — the same identifier the App Server protocol
uses in `disabledPluginIds`. *(2026-09-26: that field is still documented as saved-but-not-filtering, but
disabled plugins now hide their connectors via plugin config, #45755, #47939 — ⚠️ inferred distinction.)*

> During marketplace refresh, Codex can install or refresh files for configured plugins **even when
> `enabled = false`.** Connected services still require authentication.

Install/enable state resolves across user (`~/.codex/config.toml`), repo, cloud-managed, and system
configuration.

## 7. Plugin package structure

```
my-plugin/
├── plugin.json            # portable manifest — the entry point
├── mcp.json               # bundled MCP servers (plugin format ≠ agent.tools format)
├── skills/
│   └── <skill-name>/SKILL.md
├── assets/
└── .codex-plugin/
    └── plugin.json        # OPTIONAL compatibility fallback only
```

Rules:
- Keep `plugin.json`, `mcp.json`, `skills/`, `assets/` **at the plugin root**
- When adding a Codex overlay, keep **only its `plugin.json`** inside `.codex-plugin/`; hooks,
  `.app.json`, and other resources stay at the root
- `name` must be stable **kebab-case** — hosts use it as the plugin identifier *and* the component
  namespace
- Portable packages discover skills from the root `skills/` directory, so the manifest needs no
  `skills` field

### Portable manifest

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "my-plugin",
  "version": "0.1.0",
  "description": "Bundle reusable skills and MCP servers.",
  "author": { "name": "Your team", "email": "team@example.com", "url": "https://example.com" },
  "homepage": "https://example.com/plugins/my-plugin",
  "repository": "https://github.com/example/my-plugin",
  "license": "MIT",
  "keywords": ["research", "crm"]
}
```

### Vendor overlay

```json
"extensions": {
  "com.openai": {
    "apps": "./.app.json",
    "hooks": "./hooks/hooks.json",
    "interface": {
      "displayName": "My Plugin",
      "shortDescription": "...",
      "longDescription": "...",
      "developerName": "Your team",
      "category": "Productivity",
      "capabilities": ["Read", "Write"],
      "websiteURL": "...",
      "privacyPolicyURL": "...",
      "termsOfServiceURL": "...",
      "defaultPrompt": [ ... ]
    },
    "onboardingSkill": "skills/setup/SKILL.md"
  }
}
```

*(2026-09-26: `onboardingSkill` is new — exposed as `onboarding_skill` in plugin details, #46544.)*

**Identity and metadata stay at the root; presentation, MCP mappings, and lifecycle hooks go in the
namespaced overlay.** This is the split to imitate.

### Path rules (repeated everywhere, so enforce them once)

Paths must **start with `./`, stay inside the plugin, and contain no `..` components.**
*(2026-09-26: exception — `extensions["com.openai"].onboardingSkill` accepts relative paths with or
without the legacy `./` prefix, #46544.)*

### A minimal skill

```md
---
name: hello
description: Greet the user with a friendly message.
---

Greet the user warmly and ask how you can help.
```

## 8. Protocol surface for marketplaces and plugins

From `ClientRequest` (see [02](02-app-server-protocol.md)):

```
marketplace/add        marketplace/remove      marketplace/upgrade
plugin/list            plugin/installed        plugin/read        plugin/search (experimental)
plugin/install         plugin/uninstall        plugin/reconcile
plugin/skill/read
plugin/share/save      plugin/share/list       plugin/share/checkout
plugin/share/delete    plugin/share/updateTargets
app/list               app/read                app/installed
skills/list            skills/extraRoots/set   skills/config/write
hooks/list
```

*(corrected 2026-09-26: `plugin/search` exists at both revisions as an experimental method, which the
generated `ClientRequest` schema omits.)*

Notifications: `app/list/updated`, `skills/changed`.

Notes for a custom implementation:
- **`plugin/reconcile`** is the one that is easy to forget — catalogs drift, and you need an explicit
  "make installed state match configured state" operation rather than doing it implicitly on startup
- **`plugin/share/*`** is a separate concern from install: publishing a plugin to a workspace and
  checking one out are distinct from marketplace consumption
- `skills/extraRoots/set` lets a client add skill search roots at runtime, independent of plugins

## 9. Checklist for building a marketplace

- [ ] Adopt the portable `plugin.json` schema; put your own fields in `extensions.<your-org>`
- [ ] Support at least `local` and one git source kind; npm can come later
- [ ] Make an unresolvable entry **skip**, never fail the catalog
- [ ] Separate catalog from installed artifact — install into a versioned cache path
- [ ] Use `plugin-name@marketplace-name` as the stable id across config, protocol, and UI
- [ ] Enforce path rules (`./` prefix, no `..`, inside root) in one place
- [ ] Allow refresh-while-disabled so policy and payload stay independent
- [ ] Give the CLI a `list` that prints **resolved roots**, not just names
- [ ] Decide the precedence order across user / repo / managed / system config before you ship
