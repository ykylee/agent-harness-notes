# 08. Aside — code-level analysis

> Method: installed the Linux x64 CLI binary and **extracted its Node SEA payload.** What came out is
> an unobfuscated ESM bundle of 2,511,722 bytes / 67,774 lines. Everything below is **read directly
> from that bundle**, not from product documentation or marketing. Analysed 2026-09-23, CLI
> v1.26.916.1741.
>
> ⚠️ Grade: 🔧 **observed implementation.** Not a vendor-guaranteed specification, and subject to
> change without notice — the same grade as the Comet reverse engineering in
> [04](04-comet-architecture.md).

## 1. Reproduction

```bash
# 1. Read the install script before running it
curl -sSL https://releases.aside.com/install.sh -o aside-install.sh
cat aside-install.sh          # ← the linux-x64 / linux-arm64 branch is here

# 2. Install (~/.aside/cli, ~/.local/bin; no sudo)
bash aside-install.sh

# 3. Find and carve out the SEA blob
B=~/.aside/cli/aside
grep -abo NODE_SEA_BLOB "$B"          # the second hit is the payload offset
dd if="$B" of=sea_blob.bin bs=1 skip=<offset> status=none

# 4. The JS body begins after the blob header
python3 -c "
import pathlib
b=pathlib.Path('sea_blob.bin').read_bytes()
i=b.find(b'Object.defineProperty'); s=b.rfind(b'\x00',0,i)+1
pathlib.Path('aside_cli.js').write_bytes(b[s:])"
```

## 2. Facts absent from the documentation

| Finding | How it differs from the docs |
|---|---|
| **The CLI supports Linux x64 and arm64 as first-class targets** | The docs cover only macOS and Windows. The install script branches on `linux-x64`/`linux-arm64` and the archives (~47MB) really exist |
| **A Node SEA single executable (Node v26.5.0)** | Appears in no document. 144MB, not stripped, with debug_info |
| **Internal repository `bro-components`, monorepo `apps/cli`** | The build path `/home/runner/work/bro-components/bro-components/apps/cli/build` survives in the blob header. Built on GitHub Actions |
| **Depends on tRPC, the MCP SDK, zod, rxjs** | The stack was undisclosed |
| `../Resources/native/aside-native.node` | A native addon exists |

> 📌 The first item matters practically. **The CLI installs and runs on headless Linux.** Its
> functional surface is constrained as described in §5, though.

## 3. Perception model — `snapshot()` gives the answer

This fills the cell left blank in the comparison table at
[04 §10](04-comet-architecture.md). The bundle contains **the guide text written for agents**, and
the API specification is in it verbatim.

```ts
async function snapshot(
  page: Page,
  options?: {
    interactive?: boolean;   // interactive elements only
    showHidden?: boolean;    // include hidden elements (collapsed navbar, aria-hidden)
    ref?: string;            // e.g. "e31"
    selector?: string;       // CSS selector
  },
): Promise<{ tree: string; diff: string }>;
```

Key rules, summarised from the original:

| Rule | Detail |
|---|---|
| **Representation** | "compact accessibility tree with unique ref IDs such as `e12` or `f1e1`" |
| **Coverage** | page title, URL, **child-iframe contents and elements outside the scroll viewport** |
| **Nature of a ref** | "**virtual locator IDs, not actual DOM properties**." Pass them straight to `page.locator('e31')`; never mix them into CSS selectors |
| **Invalidation** | "Each new snapshot invalidates all earlier ref IDs" — take a new one after each action |
| **diff** | print `tree` first; **after an action print only `diff`** to capture the changes |
| Forbidden | do not truncate a snapshot with `substring`/`slice`; never guess a ref |

### 3.1 Perception and action share a namespace

[06 §2](06-architecture-axes.md) argued that "symmetry is structurally more robust," citing Browser
Use. **Aside made the same choice.**

| | Perception | Action |
|---|---|---|
| Aside | accessibility tree + ref (`e31`) | `page.locator('e31')` |
| Browser Use | SoM index (`[14]`) | `click_element(index=14)` |
| Comet | accessibility tree (YAML) | **pixel-coordinate `ComputerBatch`** ← asymmetric |

> 📌 Aside shares Comet's perceptual basis (the accessibility tree) but **diverges on action.**
> It points with a ref instead of dropping to coordinates, so the failure mode "clicked somewhere
> other than what I saw" does not structurally exist.

### 3.2 Reading escalation — cheapest first

The code states an explicit **cost ladder.**

| Order | Means | Cost |
|---|---|---|
| 1 | `snapshot(page, { interactive: true })` | cheapest |
| 2 | `snapshot(page)` | |
| 3 | wait briefly and re-snapshot (only while the page is still changing) | |
| 4 | `annotatedScreenshot(page)` — **bounding boxes carrying ref IDs** | expensive |
| 5 | `page.screenshot()` — raw visual state | |

`page.content()` and `page.evaluate()` are explicitly reserved for **when you know the exact
selector.**

> 📌 That `annotatedScreenshot` is **a screenshot with ref IDs painted on it** is good design.
> Even dropping to visual confirmation preserves the namespace. Same idea as Browser Use's SoM, but
> Aside placed it **as an escalation step rather than the default path.**

## 4. Memory — plain Markdown, settled

The item held at "secondary claim only, unverified" in [99 §4](99-sources.md) is now **settled.**

> "Aside has an accurate memory system for user, which distills user's context into
> **plain-Markdown files** (who they are, people, projects, sites, preferences)."

```bash
aside memory search "<query>" --json
aside memory list --json
aside memory show MEMORY.md      # ← the filename is exposed
aside memory path                # ← a command to query the on-disk path exists
```

And one discipline is stated explicitly:

> "**Never edit memory files yourself.** If the user wants Aside to remember something,
> run it through `aside exec`."

> 📌 The files are plain Markdown and the path is queryable, yet **direct editing is forbidden.**
> Consolidating the write path through the agent keeps it consistent.

## 5. Runtime boundary — measured

It installs, but **what actually works is another matter.** Run without logging in, on this machine:

| Command | Result |
|---|---|
| `aside guide` | ✅ works — `Aside CLI 1.26.916.1741 · Skill version 3` (the guide is bundled) |
| `aside skills list` | ❌ `Failed to request daemon auth challenge: fetch failed` |
| `aside host list` / `memory list` | ❌ same |
| `aside repl "console.log(1)"` | ❌ `Aside isn't running on this machine.` |

**The CLI is not a standalone runtime but a front end to the local daemon (Aside Browser).** Using it
requires one of:

1. **Aside Browser running on the same machine** — impossible here, as there is no Linux browser build
2. `aside login` plus **a remote host** (§6)

> No login was performed. That would use the user's account credentials and was not requested.

## 6. Remote control — a designed path for headless Linux

The bundled guide uses **exactly this situation** as its example.

> "If user's Aside runs on a remote machine (**e.g., this host is Linux but user runs Aside on
> their macOS laptop**), you can control it with following commands"

```bash
aside host list
aside exec --host <id-or-name> "..."
aside repl --host <id-or-name>
aside host use <host>            # remember as the default host
```

Requirements: **remote control enabled under Settings > Developers** on the remote machine, and that
machine online. `aside login` is needed on the current host.

> 📌 In other words **headless Linux is a supported scenario** for this product — as long as a
> separate machine (macOS/Windows) is running the browser. Linux is the cockpit, not the engine.
> This is what the Pro plan's "Channels (Remote control)" is ([02 §8](02-aside.md)).

## 7. Built-in site skills — an undocumented feature

```bash
aside skills list
aside skills show <name>
```

> "Aside ships skills for services it already knows how to drive — **Slack, Gmail, Notion,
> Google Docs/Sheets/Search, YouTube, LinkedIn, iMessage, and Aside itself.** Each one documents
> a ready-made REPL global (`slack`, `gmail`, `notion`, ...) that works inside `aside repl`,
> so check for one before driving a site through `snapshot()` by hand"

> 📌 This **partially overturns** the "the surface is the browser, not an integration list" narrative
> from [01 §5](01-landscape.md). Aside **ships hand-built skills for the major sites.** Generic
> browsing is the fallback; known sites have a dedicated path. Marketing does not mention this.
>
> That is not a criticism — it is pragmatic. But "any site, without integrations" and "dedicated
> skills for the major sites" are different claims, and **the latter can contribute to benchmark
> scores** (read alongside the self-reported benchmark verdict in [99 §3](99-sources.md)).

## 8. The delegation model — two paths

The bundled guide is written **as instructions to other coding agents.** Aside positions itself as
**a subagent of another harness.**

| Path | When | Guide's own words |
|---|---|---|
| **`aside exec`** (recommended) | most work | "delegates the task to Aside agent… **think of it like spawning subagent**" — more context-efficient, and it carries skills and memory |
| **`aside repl`** | only when you must inspect screenshots and DOM directly | "**ONLY USE IT when** you need to inspect screenshot and DOM directly" |

And the installation target is named:

> "Install the aside-browser skill into your coding agents (**Codex, Claude Code, Cursor, OpenCode**)"

> 📌 [02 §6](02-aside.md) read `aside mcp` as "making Aside an execution surface for other
> harnesses." **The code confirms that intent explicitly** — it names competing tools directly and
> tells them to install its skill.

## 9. REPL environment specification

| Item | Value |
|---|---|
| Language | ES2023+ |
| API | **Playwright-compatible** |
| Timeout | **120 seconds** |
| Modules | **none.** `import` and `require` are both forbidden |
| State | `const`/`let` bindings **persist across calls** → the guide instructs using fresh variable names each time |
| Globals | `page`, `tabs`, `listBrowserTabs()`, `attachBrowserTab()`, `attachActiveBrowserTab()`, `getTabByTargetId()`, `openTab()`, `closeTab()`, `snapshot()`, `annotatedScreenshot()`, `fetch()`, `fs`, `path`, `Buffer`, `sleep`, `display`, `pwd` |

Explicit cautions:

- `aside repl` **starts as a neutral session.** Do **not** assume `page` is the user's current tab
- Manage tabs only with `openTab()`/`closeTab()` — `page.context().newPage()` and `page.close()`
  **leak memory**
- `fetch()` **carries cookies.** Use it only for safe same-origin or trusted direct-download GET/HEAD
- Cloud sessions use their own sandboxed REPL; `repl` and `mcp` run only on local or remote hosts

> ⚠️ **That `fetch()` carries cookies** is worth flagging. Code inside the REPL can issue arbitrary
> requests with the user's session authority. The guide limits it to "safe" uses, but that is
> **guidance, not enforcement.** Read together with prompt injection ([07](07-security.md)), it is
> the surface exposed when whatever drives the REPL has been fooled.

## 10. Comparison table update

The "not published" cells in [04 §10](04-comet-architecture.md) fill in.

| Axis | Comet | **Aside (updated)** |
|---|---|---|
| Perception | accessibility tree (YAML) | **accessibility tree + virtual ref IDs, returns `{tree, diff}`** |
| Action | pixel-coordinate batches | **ref-based Playwright locators** (symmetric) |
| Visual fallback | — | **`annotatedScreenshot` — boxes carrying refs** |
| Transport | SSE + WebSocket | **local daemon + tRPC** (external endpoints unconfirmed in the bundle) |
| Memory | — | **plain Markdown files, path queryable, direct editing forbidden** |
| Skills | — | **8+ built-in site skills** (Slack/Gmail/Notion/Google/YouTube/LinkedIn/iMessage) |
| Developer surface | none | CLI · MCP · REPL + **remote host control** |

## 11. Still unverified

| Item | Status |
|---|---|
| External API endpoints and domains | ⚠️ No hard-coded Aside domain found in the bundle. Apparently via configuration or the daemon |
| Actual enforcement of permissions | ✅ **Resolved later** — the policy engine lives in the daemon. [10 §1](10-aside-enforcement-and-native.md) |
| Vault encryption implementation | ✅ **Resolved later** — [09 §7](09-aside-browser-internals.md) |
| Actual UI and visual design | ⚠️ **Still unverified.** There is no Linux browser build |
