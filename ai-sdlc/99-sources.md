# 99. The AI-native SDLC playbook — sources and verification status

> **✅** read on the named page on 2026-10-06, and recorded as what that page says.
> **📣** the page's expectation, a product claim, or a number this repository did not measure.
> **⚠️** not verified here, or verified only in part.

No play was executed. There is no 🧪 row.

## A. Primary ✅

| Source | Taken | Grade |
|---|---|---|
| <https://claude.com/blog/the-ai-native-sdlc-playbook>, Louis Claxton, 2026-08-21 | the six stages, the artifact chain, every play's prerequisites, steps, governance, and indicators, the worked-example fields, the managed-settings example as printed | ✅ as a reading of the page |
| <https://academy.claude.com/courses/ai-native-sdlc-playbook> | 14 lessons; the blog is the single-page full playbook; audience is engineering, platform, and security leads, especially in regulated enterprises | ✅ the course page. Individual lesson URLs were not fetched |
| <https://code.claude.com/docs/en/hooks>, read 2026-10-06 | exit 2 blocks `PreToolUse` and JSON cannot override it; exit 0 does not approve; exit 1 does not block; a missing script and a timed-out command hook do not block; precedence `deny` > `defer` > `ask` > `allow`; `PermissionRequest` ignores exit 2; `@` mentions do not fire `PreToolUse`; `allowManagedHooksOnly` exists | ✅ the sections opened. The page is long and was not read end to end |
| <https://code.claude.com/docs/en/permission-modes>, read 2026-10-06 | plan mode blocks edits until approval; the interactive-terminal bypass exception; auto mode is a classifier and, at v2.1.283 or later, the built-in start mode for interactive terminal and VS Code | ✅ those sections. The page is version-dense and was not read end to end |

## B. The page's own claims, not adopted 📣

| Claim | Where |
|---|---|
| "Applied AI team's best practices", and the framing that the plays realize productivity gains | opening and closing of the playbook |
| Time from intent conversation falls from weeks to hours. Time to first review falls to minutes. PR findings that cite a policy fall toward zero | each play's "how to measure it". These are instructions plus an expectation |
| A hook makes a violation "close to impossible" | skills play. Exit 2 is ✅. The silent-disable and timeout rows in the hooks reference are why the sentence stays 📣 |
| A tool-level `WebFetch` deny does not stop a shell, and the OS domain allowlist does | managed-settings commentary. The sandboxing doc was not opened |
| Claude Security validates findings before report, attaches a confidence rating, and runs on Mythos 5 | the scans play. Product snapshot, not re-checked |
| Claude Tag as a channel member under its own identity, public beta in Slack | the Tag section. Product snapshot |

## C. Not verified ⚠️

| Item | Why |
|---|---|
| The dependency-graph image | not read. Adoption order in [`01`](01-the-loop.md) is reconstructed from Prerequisites text |
| The PDF | not downloaded. The page says it is the same six stages |
| Academy lesson bodies | the course index was read. The lessons were not |
| Managed-settings JSON, key by key | printed on the page, not checked against <https://code.claude.com/docs/en/settings>, not deployed |
| `requiredMinimumVersion` `"2.1.193"` as a current floor | the example's string. Docs read the same day already discuss v2.1.283 |
| The production-gate script as enforcement | substring match on two words plus an env var. Not installed |
| The eval workflow YAML | illustration. Not run. No pass rate exists to adopt |
| "How Anthropic secures its AI-native software development lifecycle" (2026-07-21) | linked, not read. No figure from it is used |
| "how Claude Tag runs on-call for CI/CD" | linked, not read |
| "Running an AI-native engineering org" (2026-06-03) and "The founder's playbook" (2026-05-14) | different posts. Named so they are not folded into this note |
| Any DORA number, any survival rate, any share of merged code | not stated as a result of this reading, and not measured |

## D. Docs the playbook lists and this note did not open

The page ends with a rollout list: admin setup, settings, server-managed settings, permissions,
sandboxing, the hooks guide, skills, plugin marketplaces, managed MCP, third-party integrations,
network config, OpenTelemetry, the analytics dashboard, the Compliance API, and the security
model. Only the hooks reference and the permission-modes page were opened. The others stay unread.
