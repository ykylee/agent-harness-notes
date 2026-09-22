---
type: concept
status: active
last_ingested_from: docs/13-marketplace-and-plugins.md + docs/10-agents-api-tools.md + docs/12-product-surface.md
related_pages: [concepts/execution-environment-topology, concepts/harness, concepts/provider-as-data]
created: 2026-09-22
updated: 2026-09-22
---

# Capability Distribution — plugin · marketplace · skill 의 유통 체계

- 문서 목적: 능력(skill·MCP)을 포장·배포·설치·활성화하는 체계를 정리하고, 커스텀 하네스가 자기 형식을 발명하기 전에 알아야 할 것을 짚는다.
- 범위: 한 문단 모델, 이식 가능 manifest, 카탈로그 형식, 설치 캐시, 세 동사, 프로토콜 표면
- 1차 출처: `developers.openai.com/plugins/build/plugins.md`, App Server `ClientRequest`
- 최종 수정일: 2026-09-22

## §1 TL;DR  {#s1-tldr}

| # | 항목 | 값 |
|---|---|---|
| 1 | **plugin** | skill · MCP 설정 · 또는 둘 다를 포장한 폴더. **능력의 단위** |
| 2 | **marketplace** | plugin 을 나열하고 각각의 출처를 적은 JSON 카탈로그. **배포와 정책의 단위** |
| 3 | 식별자 | `plugin-name@marketplace-name` — config · 프로토콜 · UI 전부에서 동일 |
| 4 | manifest | **벤더 중립 개방 스키마** (`agent-plugins.org`). Claude 호환 manifest 도 수용 |
| 5 | 세 동사 | **install ≠ enable ≠ share** |
| 6 | 실패 의미론 | 항목 하나가 풀리지 않으면 **그 항목만 건너뛴다**. 카탈로그 전체를 죽이지 않는다 |

## §2 형식을 발명하기 전에  {#s2-open-schema}

```json
{ "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", ... }
```

`agent-plugins.org` 는 벤더 중립 스키마 호스트이고, Codex 는 **Claude 호환 manifest** 와 레거시
경로(`$REPO_ROOT/.claude-plugin/marketplace.json`)를 명시적으로 받아들인다.

> 자기 plugin 형식을 발명하면 **이미 존재하는 패키지를 소비할 능력을 포기**하는 것이다. 이식 가능
> manifest 를 채택하고 자기 추가분을 namespace 된 `extensions.<your-org>` 객체로 두는 쪽이 싸다 —
> OpenAI 가 `extensions.com.openai` 로 하는 바로 그것이다.

### §2.1 root 와 overlay 의 분할  {#s2-1-root-overlay}

| 위치 | 담는 것 |
|---|---|
| **root** (`plugin.json`) | 정체성과 메타데이터 — `name`, `version`, `description`, `author`, `license`, `keywords` |
| **overlay** (`extensions.com.openai`) | 표현·MCP 매핑·생명주기 훅 — `interface`, `apps`, `hooks` |

**흉내 낼 가치가 있는 분할이다.** `name` 은 안정적 **kebab-case** 여야 한다 — 호스트가 plugin
식별자이자 컴포넌트 namespace 로 쓴다.

## §3 카탈로그 형식  {#s3-catalog}

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

| 필드 | 규칙 |
|---|---|
| 최상위 `name` | marketplace 식별. plugin id 의 `@marketplace` 쪽이 된다 |
| `plugins[].policy.installation` | `AVAILABLE` \| `INSTALLED_BY_DEFAULT` \| `NOT_AVAILABLE` |
| `plugins[].policy.authentication` | 설치 시점 인증인지 최초 사용 시점인지 (`ON_INSTALL`) |

### §3.1 source 종류 4가지  {#s3-1-sources}

| 종류 | 형태 |
|---|---|
| `local` | `{ "source": "local", "path": "./plugins/my-plugin" }` — marketplace root 기준 상대경로. 평문 문자열도 허용 |
| `url` (git, 저장소 루트) | `{ "source": "url", "url": "...git", "ref": "main" }` |
| `git-subdir` | `{ "source": "git-subdir", "url": "...", "path": "./plugins/x", "ref": "main" }` |
| `npm` | `{ "source": "npm", "package": "@example/codex-plugin", "version": "^1.2.0", "registry": "..." }` |

- git 항목은 **`ref` 또는 `sha`** 선택자를 받는다
- npm: `version` 은 버전·dist tag·범위를 받지만 **경로나 URL 선택자는 안 된다**. `registry` 는
  **자격증명·쿼리·프래그먼트가 박히지 않은 HTTPS** 여야 한다
- **패키지는 lifecycle script 를 돌리지 않고 내려받는다**

### §3.2 베낄 만한 실패 의미론  {#s3-2-failure}

> 항목의 source 를 풀 수 없으면 **그 plugin 항목을 건너뛰지, marketplace 전체를 실패시키지 않는다.**

항목 하나가 팀 전체 카탈로그를 무너뜨려서는 안 된다.

## §4 카탈로그와 설치본의 분리  {#s4-catalog-vs-installed}

| 카탈로그 위치 | 범위 |
|---|---|
| `$REPO_ROOT/.agents/plugins/marketplace.json` | 저장소 |
| `~/.agents/plugins/marketplace.json` | 개인 |
| `$REPO_ROOT/.claude-plugin/marketplace.json` | 레거시 호환 |

설치 캐시: `~/.codex/plugins/cache/$MARKETPLACE_NAME/$PLUGIN_NAME/$VERSION/`

local plugin 의 `$VERSION` 은 문자열 `local` 이고, **호스트는 marketplace 항목이 아니라 캐시 경로의
설치본을 읽는다.** 원본 폴더를 고치면 refresh 가 필요하다 — **"카탈로그"와 "설치된 산출물"의 의도적
분리**다.

## §5 install ≠ enable ≠ share  {#s5-three-verbs}

```toml
[plugins."my-plugin@local-repo"]
enabled = true
```

> marketplace refresh 중 Codex 는 **`enabled = false` 인 plugin 의 파일도 설치·갱신할 수 있다.**
> 정책과 payload 가 독립이도록 한 것이다. (연결된 서비스는 여전히 인증을 요구한다.)

install/enable 상태는 사용자(`~/.codex/config.toml`) · 저장소 · 클라우드 관리 · 시스템 설정을 가로질러
해석된다. **출하 전에 우선순위를 정해 둬야 한다.**

## §6 Agents API 쪽의 적재 방법  {#s6-agents-api}

| 환경 | 방법 |
|---|---|
| **self-hosted** | plugin 을 환경에 복사하고 **절대 경로**를 `environment.capability_directories` 에 추가. **plugin root**(= `.codex-plugin/plugin.json` 을 담은 디렉터리)를 고른다 |
| **openai-hosted** | `environment.plugins` 에 **plugin 당 ZIP 하나**. 각 ZIP 은 `.codex-plugin/plugin.json` 을 가진 plugin 폴더 하나를 담아야 하고, **요청의 name/description 이 manifest 와 일치**해야 한다 |

> 여러 plugin 이면 각 root 를 나열한다. **부모 디렉터리가 중첩된 skill 은 발견하지만, 자식 plugin 의
> MCP 설정을 전부 로드하지는 않는다.**
> 세션마다 자기 환경을 갖고, **루트 에이전트와 그 subagent 가 그 환경을 공유한다.**

경로 규칙(모든 곳에서 반복되므로 한 곳에서 강제하라): **`./` 로 시작, plugin 안에 머무를 것,
`..` 성분 없을 것.**

## §7 프로토콜 표면  {#s7-protocol}

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

| 항목 | 놓치기 쉬운 이유 |
|---|---|
| **`plugin/reconcile`** | 카탈로그는 드리프트한다. "설치 상태를 설정 상태에 맞춰라"를 **시작 시 암묵적으로** 하는 대신 명시적 연산으로 둬야 한다 |
| **`plugin/share/*`** | 설치와 별개 관심사 — 워크스페이스에 게시하고 체크아웃하는 것은 marketplace 소비와 다르다 |
| `skills/extraRoots/set` | 클라이언트가 런타임에 skill 탐색 root 를 추가. plugin 과 독립 |

> ⚠️ 현재 `disabledPluginIds` 는 **선택을 저장할 뿐 실제로 capability 를 걸러내지 않는다.**

## §8 다음에 읽을 문서  {#s8-next}

- [[concepts/execution-environment-topology]] — plugin 이 적재되는 환경
- [[concepts/harness]] §7 — capability system 이 표면에서 차지하는 비중
- 원문: [`docs/13-marketplace-and-plugins.md`](../../../docs/13-marketplace-and-plugins.md), [`docs/10-agents-api-tools.md`](../../../docs/10-agents-api-tools.md) §4
