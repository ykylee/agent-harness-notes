# 08. Aside — 코드레벨 분석

> 방법: Linux x64 CLI 바이너리를 설치해 **Node SEA 페이로드를 추출**했다. 난독화되지 않은
> ESM 번들 2,511,722 bytes / 67,774줄이 나왔다. 아래는 전부 **그 번들에서 직접 읽은 것**이며,
> 제품 문서나 마케팅이 아니다. 분석일 2026-09-23, CLI v1.26.916.1741.
>
> ⚠️ 등급: 🔧 **관측된 구현**. 벤더가 보증한 명세가 아니고 예고 없이 바뀔 수 있다.
> [04](04-comet-architecture.md) 의 Comet 리버싱과 같은 등급이다.

## 1. 재현 절차

```bash
# 1. 설치 스크립트를 실행하지 말고 먼저 읽는다
curl -sSL https://releases.aside.com/install.sh -o aside-install.sh
cat aside-install.sh          # ← linux-x64 / linux-arm64 분기가 여기 있다

# 2. 설치 (~/.aside/cli, ~/.local/bin, sudo 불필요)
bash aside-install.sh

# 3. SEA blob 위치를 찾아 도려낸다
B=~/.aside/cli/aside
grep -abo NODE_SEA_BLOB "$B"          # 두 번째 히트가 페이로드 시작
dd if="$B" of=sea_blob.bin bs=1 skip=<offset> status=none

# 4. blob 헤더 뒤부터가 JS 본문
python3 -c "
import pathlib
b=pathlib.Path('sea_blob.bin').read_bytes()
i=b.find(b'Object.defineProperty'); s=b.rfind(b'\x00',0,i)+1
pathlib.Path('aside_cli.js').write_bytes(b[s:])"
```

## 2. 문서에 없던 사실들

| 발견 | 문서와의 차이 |
|---|---|
| **CLI 는 Linux x64·arm64 를 1급 지원한다** | 문서는 macOS·Windows 만 안내. 설치 스크립트에 `linux-x64`/`linux-arm64` 분기가 있고 아카이브(≈47MB)도 실재한다 |
| **Node SEA (Node v26.5.0) 단일 실행파일** | 어느 문서에도 없음. 144MB, not stripped, debug_info 포함 |
| **내부 저장소명 `bro-components`, 모노레포 `apps/cli`** | 빌드 경로 `/home/runner/work/bro-components/bro-components/apps/cli/build` 가 blob 헤더에 남아 있다. GitHub Actions 빌드 |
| **tRPC · MCP SDK · zod · rxjs 의존** | 스택 미공개였음 |
| `../Resources/native/aside-native.node` | 네이티브 애드온 존재 |

> 📌 첫 항목이 실용적으로 중요하다. **헤드리스 리눅스에서도 CLI 는 설치·실행된다.**
> 다만 기능 표면은 §5 의 제약을 받는다.

## 3. 인식 모델 — `snapshot()` 이 정답을 말한다

[04 §10](04-comet-architecture.md) 비교표에서 "미공개"로 비워뒀던 칸이 채워졌다.
번들에 **에이전트용 가이드 원문**이 들어 있고, 거기에 API 규격이 그대로 있다.

```ts
async function snapshot(
  page: Page,
  options?: {
    interactive?: boolean;   // 상호작용 요소만
    showHidden?: boolean;    // 숨은 요소 포함 (접힌 navbar, aria-hidden)
    ref?: string;            // 예: "e31"
    selector?: string;       // CSS 선택자
  },
): Promise<{ tree: string; diff: string }>;
```

핵심 규칙 (원문 요약):

| 규칙 | 내용 |
|---|---|
| **표현** | "compact accessibility tree with unique ref IDs such as `e12` or `f1e1`" |
| **범위** | 페이지 제목·URL·**자식 iframe 내용·스크롤 뷰포트 밖 요소**까지 포함 |
| **ref 의 성질** | "**virtual locator IDs, not actual DOM properties**". `page.locator('e31')` 에 그대로 넘긴다. CSS 선택자에 섞지 말 것 |
| **무효화** | "Each new snapshot invalidates all earlier ref IDs" — 동작마다 새로 찍어야 한다 |
| **diff** | 최초엔 `tree` 를 출력하고, **동작 후에는 `diff` 만** 출력해 변화분만 잡는다 |
| 금지 | snapshot 을 `substring`/`slice` 로 자르지 말 것, ref 를 추측하지 말 것 |

### 3.1 인식/동작 이름 공간이 대칭이다

[06 §2](06-architecture-axes.md) 에서 "대칭 쪽이 구조적으로 견고하다"고 적고 Browser Use 를
근거로 들었는데, **Aside 도 같은 선택을 했음이 확인됐다.**

| | 인식 | 동작 |
|---|---|---|
| Aside | 접근성 트리 + ref (`e31`) | `page.locator('e31')` |
| Browser Use | SoM 인덱스 (`[14]`) | `click_element(index=14)` |
| Comet | 접근성 트리 (YAML) | **픽셀 좌표 `ComputerBatch`** ← 비대칭 |

> 📌 Aside 는 Comet 과 인식 기반(접근성 트리)은 같지만 **동작에서 갈린다.** 좌표로 내려가지
> 않고 ref 로 가리킨다. "본 것과 다른 곳을 눌렀다"라는 실패 모드가 구조적으로 없다.

### 3.2 읽기 에스컬레이션 — 싼 것부터

코드가 **비용 순 사다리**를 명시한다.

| 순서 | 수단 | 비용 |
|---|---|---|
| 1 | `snapshot(page, { interactive: true })` | 가장 쌈 |
| 2 | `snapshot(page)` | |
| 3 | 잠깐 대기 후 재촬영 (페이지가 아직 변하는 중일 때만) | |
| 4 | `annotatedScreenshot(page)` — **ref ID 가 적힌 바운딩 박스** | 비쌈 |
| 5 | `page.screenshot()` — 원시 시각 상태 | |

`page.content()` 와 `page.evaluate()` 는 **정확한 선택자를 알 때만** 쓰라고 명시된다.

> 📌 `annotatedScreenshot` 이 **ref ID 를 박은 스크린샷**이라는 점이 좋다. 시각 확인으로
> 내려가도 이름 공간이 유지된다. Browser Use 의 SoM 과 같은 아이디어인데, Aside 는 그것을
> **기본 경로가 아니라 에스컬레이션 단계**로 뒀다.

## 4. 메모리 — plain Markdown 확정

[99 §4](99-sources.md) 에서 "2차 출처만 주장, 미확인"으로 뒀던 항목이 **확정**됐다.

> "Aside has an accurate memory system for user, which distills user's context into
> **plain-Markdown files** (who they are, people, projects, sites, preferences)."

```bash
aside memory search "<query>" --json
aside memory list --json
aside memory show MEMORY.md      # ← 파일명이 그대로 노출
aside memory path                # ← 디스크 경로 조회 명령이 존재
```

그리고 규율 하나가 명시돼 있다:

> "**Never edit memory files yourself.** If the user wants Aside to remember something,
> run it through `aside exec`."

> 📌 파일은 평문 Markdown이고 경로도 조회 가능한데 **직접 편집은 금지**한다. 쓰기 경로를
> 에이전트로 단일화해 일관성을 지키는 설계다.

## 5. 런타임 경계 — 실측

설치는 되지만 **무엇이 동작하는지는 다르다.** 로그인 없이 이 환경에서 직접 실행한 결과:

| 명령 | 결과 |
|---|---|
| `aside guide` | ✅ 동작 — `Aside CLI 1.26.916.1741 · Skill version 3` (가이드가 번들 내장) |
| `aside skills list` | ❌ `Failed to request daemon auth challenge: fetch failed` |
| `aside host list` / `memory list` | ❌ 동일 |
| `aside repl "console.log(1)"` | ❌ `Aside isn't running on this machine.` |

**CLI 는 독립 실행체가 아니라 로컬 데몬(Aside Browser)의 프런트엔드다.** 기능을 쓰려면 둘 중 하나:

1. 같은 기기에서 **Aside Browser 가 돌고 있을 것** — 리눅스 빌드가 없으므로 **이 환경에선 불가**
2. `aside login` 후 **원격 호스트**를 쓸 것 (§6)

> 로그인은 하지 않았다. 사용자 계정 자격증명이 필요한 행위이고 요청받지 않았다.

## 6. 원격 제어 — 헤드리스 리눅스를 위한 설계된 경로

번들의 가이드가 **정확히 이 상황**을 예시로 든다.

> "If user's Aside runs on a remote machine (**e.g., this host is Linux but user runs Aside on
> their macOS laptop**), you can control it with following commands"

```bash
aside host list
aside exec --host <id-or-name> "..."
aside repl --host <id-or-name>
aside host use <host>            # 기본 호스트로 기억
```

조건: 원격 기기에서 **Settings > Developers 의 원격 제어 활성화** + 온라인 상태.
현재 호스트에서는 `aside login` 이 필요하다.

> 📌 즉 **헤드리스 리눅스는 이 제품의 지원 대상 시나리오**다. 다만 브라우저 자체가 도는
> 기기(macOS/Windows)가 따로 있어야 한다. 리눅스는 조종석이지 실행부가 아니다.
> Pro 플랜의 "Channels (Remote control)" 이 이것이다 ([02 §8](02-aside.md)).

## 7. 내장 사이트 스킬 — 문서에 없던 기능

```bash
aside skills list
aside skills show <name>
```

> "Aside ships skills for services it already knows how to drive — **Slack, Gmail, Notion,
> Google Docs/Sheets/Search, YouTube, LinkedIn, iMessage, and Aside itself.** Each one documents
> a ready-made REPL global (`slack`, `gmail`, `notion`, ...) that works inside `aside repl`,
> so check for one before driving a site through `snapshot()` by hand"

> 📌 이것이 [01 §5](01-landscape.md) 의 "통합 목록이 아니라 브라우저가 표면"이라는 서사를
> **부분적으로 뒤집는다.** Aside 는 주요 사이트에 대해 **손으로 만든 스킬을 미리 싣고 있다.**
> 범용 브라우징은 폴백이고, 알려진 사이트에는 전용 경로가 있다. 마케팅이 말하지 않는 부분이다.
>
> 이것이 나쁘다는 뜻은 아니다 — 오히려 실용적이다. 다만 "통합 없이 아무 사이트나"라는 주장과
> "주요 사이트엔 전용 스킬"이라는 구현은 결이 다르고, **후자가 벤치마크 점수에 기여할 수 있다**
> ([99 §3](99-sources.md) 의 자체보고 벤치마크 판정과 함께 읽어야 한다).

## 8. 에이전트 위임 모델 — 두 경로

번들의 가이드가 **다른 코딩 에이전트에게 주는 지침**으로 쓰여 있다. Aside 가 자신을
**다른 하네스의 하위 에이전트**로 포지셔닝한다는 뜻이다.

| 경로 | 언제 | 가이드 원문 |
|---|---|---|
| **`aside exec`** (권장) | 대부분 | "delegates the task to Aside agent... **think of it like spawning subagent**" — 컨텍스트 효율적이고 스킬·메모리를 갖고 있다 |
| **`aside repl`** | 스크린샷·DOM 직접 검사가 필요할 때만 | "**ONLY USE IT when** you need to inspect screenshot and DOM directly" |

그리고 설치 대상이 명시돼 있다:

> "Install the aside-browser skill into your coding agents (**Codex, Claude Code, Cursor, OpenCode**)"

> 📌 [02 §6](02-aside.md) 에서 `aside mcp` 를 보고 "Aside 를 다른 하네스의 실행 표면으로
> 만든다"고 적었는데, **코드가 그 의도를 명시적으로 확인해 준다.** 경쟁 도구 이름을 직접
> 나열하며 자기 스킬을 설치하라고 한다.

## 9. REPL 환경 규격

| 항목 | 값 |
|---|---|
| 언어 | ES2023+ |
| API | **Playwright 호환** |
| 타임아웃 | **120초** |
| 모듈 | **없음.** `import`·`require` 전면 금지 |
| 상태 | `const`/`let` 바인딩이 **호출 간 유지** → 매번 새 변수명을 쓰라고 지시 |
| 전역 | `page`, `tabs`, `listBrowserTabs()`, `attachBrowserTab()`, `attachActiveBrowserTab()`, `getTabByTargetId()`, `openTab()`, `closeTab()`, `snapshot()`, `annotatedScreenshot()`, `fetch()`, `fs`, `path`, `Buffer`, `sleep`, `display`, `pwd` |

주의 사항으로 명시된 것:

- `aside repl` 은 **중립 세션으로 시작**한다. `page` 가 사용자의 현재 탭이라고 **가정하지 말 것**
- 탭 관리는 반드시 `openTab()`/`closeTab()` — `page.context().newPage()` 나 `page.close()` 는 **메모리 누수**
- `fetch()` 는 **쿠키를 들고 간다**. 안전한 동일 출처나 신뢰된 직접 다운로드 GET/HEAD 에만 쓸 것
- 클라우드 세션은 자체 샌드박스 REPL 을 쓴다 — `repl`/`mcp` 는 local 또는 원격 호스트에서만

> ⚠️ **`fetch()` 가 쿠키를 들고 간다**는 점은 보안 관점에서 짚을 만하다. REPL 안의 코드는
> 사용자 세션 권한으로 임의 요청을 보낼 수 있다. 가이드가 스스로 "안전한 것에만"이라고
> 제한하지만 이는 **지침이지 강제가 아니다.** [07](07-security.md) 의 프롬프트 주입과 겹쳐
> 읽으면, REPL 을 모는 주체가 속았을 때의 표면이 된다.

## 10. 비교표 갱신

[04 §10](04-comet-architecture.md) 의 "미공개" 칸들이 채워진다.

| 축 | Comet | **Aside (갱신)** |
|---|---|---|
| 인식 | 접근성 트리 (YAML) | **접근성 트리 + 가상 ref ID, `{tree, diff}`** |
| 동작 | 픽셀 좌표 배치 | **ref 기반 Playwright locator** (대칭) |
| 시각 폴백 | — | **`annotatedScreenshot` — ref 가 박힌 박스** |
| 전송 | SSE + WebSocket | **로컬 데몬 + tRPC** (외부 엔드포인트는 번들에서 미확인) |
| 메모리 | — | **plain Markdown 파일, 경로 조회 가능, 직접 편집 금지** |
| 스킬 | — | **내장 사이트 스킬 8종+** (Slack/Gmail/Notion/Google/YouTube/LinkedIn/iMessage) |
| 개발자 표면 | 없음 | CLI·MCP·REPL + **원격 호스트 제어** |

## 11. 남은 미확인

| 항목 | 상태 |
|---|---|
| 외부 API 엔드포인트·도메인 | ⚠️ 번들에서 하드코딩된 aside 도메인을 찾지 못했다. 설정이나 데몬 경유로 보인다 |
| 권한 강제의 실제 구현 | ⚠️ 권한은 **데몬(브라우저) 쪽**에 있는 것으로 보인다. CLI 번들에는 플래그 전달만 있다 |
| Vault 암호화 구현 | ⚠️ CLI 번들 범위 밖. 브라우저 바이너리를 봐야 한다 |
| 실제 UI·시각 디자인 | ⚠️ **여전히 미확인.** 리눅스 브라우저 빌드가 없다 |

> 다음 단계는 **브라우저 바이너리 자체**(macOS/Windows)를 같은 방식으로 여는 것이다.
> 권한 강제·Vault·인식 파이프라인의 실체가 거기 있다.
