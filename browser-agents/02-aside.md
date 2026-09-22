# 02. Aside — 기능 · 구성 · 구조

> 출처: `docs.aside.com` 의 전체 문서를 **원본 마크다운으로** 읽었다 (`/llms.txt` 가 색인,
> 각 페이지에 `.md` 를 붙이면 원문). 랜딩 페이지는 마케팅 문구뿐이라 근거로 쓰지 않았다.
> 추출일 2026-09-22.

## 1. 한 문장

> "The most intelligent AI assistant, but it's a browser."

Aside 는 **독립 Chromium 데스크톱 브라우저**다. 확장이 아니다. 일상 브라우저 노릇을 하면서,
필요할 때 에이전트가 페이지를 넘겨받는다. 제품의 정면 주장은 경쟁 제품 비판으로 시작한다 —
*"Today's AI browsers are broken. They never complete a task."*

베팅의 요지: **통합(integration) 목록이 아니라 로그인된 웹 그 자체를 표면으로 삼는다.**
사람이 하듯 사이트에 들어가 일하면 연동 API 가 있는 서비스보다 훨씬 넓은 면적을 얻는다.

## 2. 기능 지도

| 기능 | 무엇인가 |
|---|---|
| **Browser Agent** | 로그인된 사이트를 가로질러 다단계 작업을 수행 — 이메일, 대시보드, 내부 도구, 파일 |
| **Aside Vault** | "에이전트를 위해 만든 최초의 비밀번호 관리자". 에이전트에게 **원문 비밀번호를 주지 않고** 채운다 |
| **Memory** | 브라우징·대화·작업에서 맥락을 축적. 기기에 남는다 |
| **Ultrabrowse** | 출처가 많은 조사·비교용 심화 모드 (Pro 이상) |
| **Routines** | 반복 작업 — cron 형과 heartbeat 형 |
| **Side panel** | 보고 있는 페이지를 맥락으로 붙여 작업 시작 |
| **CLI / MCP / REPL** | 터미널·외부 도구에서 브라우저 작업을 띄운다 |
| **Channels / Cloud handoff** | 원격 제어와 클라우드 인계 (Pro 이상) |

## 3. 구조 — 권한 모델이 설계의 중심이다

Aside 문서에서 가장 분량이 실린 곳이 권한이다. 제어 지점이 **세 구역**으로 갈린다.

| 구역 | 통제 대상 |
|---|---|
| **Sandbox** | OS 수준 격리 |
| **File permissions** | 폴더 접근 |
| **Tool permissions** | 능력별 Allow / Ask / Deny |

### 3.1 규칙 어휘

| 규칙 | 동작 |
|---|---|
| `Allow` | "Let the agent use the capability without asking" |
| `Ask` | 진행 전 확인 요구 |
| `Deny` | 차단. **우선한다** |

Deny 가 우선한다는 것이 명시돼 있다 — 허용과 거부가 겹칠 때의 판정을 애매하게 두지 않았다.

### 3.2 세션 권한 모드 3종

| 모드 | 의미 |
|---|---|
| `Read only` | "Let Aside inspect browser and file context without changing your files" |
| **`Guard`** (기본) | 승인된 폴더에서 작업하고, 그 밖은 물어본다 |
| `Full access` | "Let Aside read and write anywhere on the computer" |

설정은 **두 층**에서 걸린다 — `Settings > Agents` 의 에이전트 기본값, 그리고 작업마다 거는
세션 단위 override.

> 📌 **베낄 만한 설계**: 저장된 비밀번호 값은 **full access 모드에서도 AI 에게 숨겨진다.**
> 권한 등급과 자격증명 노출을 **다른 축으로 분리**한 것이다. "가장 센 권한 = 전부 볼 수 있음"
> 이 아니다. 자동완성 전에 접근 정책과 대상 URL 을 함께 검증한다.

### 3.3 작업 모드

| 모드 | 동작 |
|---|---|
| `Default` | "Run the task in the normal browser profile" |
| `Incognito` | 일반 프로필 상태 없이 실행. 브라우저 상태를 남기지 않는다 |

**시크릿 세션에서는 에이전트가 비밀번호 관리자를 쓸 수 없다.** 격리가 자격증명까지 일관되게 적용된다.

## 4. Vault — 자격증명 설계

주장: *"passwords [are filled] into websites without showing them to the agent"*.

| 축 | 내용 |
|---|---|
| AI 접근 정책 | `Always allow` (기본) / `While unlocked` / `Never` |
| 개별 override | 가져온 항목별로 전역 정책을 덮어쓸 수 있다 |
| 생체 잠금 | Touch ID / Windows Hello — **금고 접근 방식만 바꾸지, 열린 뒤 에이전트 권한은 바꾸지 않는다** |
| 가져오기 | 1Password, Apple Passwords, Bitwarden, Chrome, Dashlane, Edge, Firefox, LastPass CSV, Generic CSV (`name,url,username,password`) |
| 랜딩 페이지 주장 | 하드웨어 기반 E2E 암호화, Secure Enclave, 포스트양자 암호, 감사 로깅 |

> ⚠️ **등급 주의**: 암호화·Secure Enclave·포스트양자·감사 로깅은 **랜딩 페이지 주장이고 헬프
> 문서에 뒷받침이 없다.** 문서 쪽은 정책 이름과 동작만 말한다. 구현 검증 불가 —
> [99-sources.md](99-sources.md) §4.

> ⚠️ 기본값이 `Always allow` 라는 점은 짚어둘 만하다. 가장 느슨한 쪽이 기본이다.

## 5. Memory

| 축 | 내용 |
|---|---|
| 입력원 | 브라우징 기록, 채팅, 작업 |
| 보존 기간 | `Never forget` / `30 days` / `90 days` |
| 관리 | `Settings > Memory` — Overview(열람·편집) / History(변경 이력) / Configure(보존 설정) |
| 위치 주장 | "stays local on your device and is never shared" |

> ⚠️ 2차 출처들이 "plain markdown 으로 저장돼 직접 편집 가능"이라고 말하지만 **헬프 문서는
> 파일 형식도 디스크 경로도 명시하지 않는다.** 편집 가능하다는 것만 UI 수준에서 확인된다.
> 형식 주장은 미확인으로 둔다.

## 6. 개발자 표면 — CLI · MCP · REPL

이 제품에서 가장 덜 알려졌지만 구조적으로 가장 흥미로운 부분이다. **브라우저가 자동화
엔드포인트로도 노출된다.**

```bash
# 설치 (macOS)
curl -fsSL https://releases.aside.com/install.sh | bash
aside --update

# 브라우저 작업을 터미널에서
aside "Open localhost:3000 and run a smoke test"
aside --session <session-id> "Continue"

# 계정 전환
aside account list | status | use u1
aside --account u1 "..."

# MCP 서버로 노출 → mcp.json 에 등록하면 외부 클라이언트가 붙는다
aside mcp

# 결정적 브라우저 조작용 REPL
aside repl "const p = await openTab('https://example.com')"
```

세 층이 목적별로 갈린다:

| 표면 | 성격 | 쓰임 |
|---|---|---|
| `aside "<task>"` | 자연어 | 에이전트에게 맡김 |
| `aside mcp` | 프로토콜 | **다른 에이전트가 Aside 를 도구로 쓴다** |
| `aside repl` | 결정적 | "직접 페이지 검사, 스크린샷, 다운로드, 결정적 브라우저 단계" |

> 📌 **구조적 의미**: `aside repl` 의 존재는 이 제품이 **모델에 맡기는 경로와 맡기지 않는
> 경로를 둘 다 제공**한다는 뜻이다. 에이전트가 불확실한 곳에서는 결정적 스크립트로 내려갈 수
> 있다. `aside mcp` 는 Aside 를 최종 제품이 아니라 **다른 하네스의 실행 표면**으로 만든다 —
> 이 저장소의 기존 조사([`docs/01-overview.md`](../docs/01-overview.md))에서 본 계층 개방과
> 같은 모양이다.

## 7. 플랫폼과 릴리스

| 축 | 내용 |
|---|---|
| 엔진 | Chromium |
| macOS | 문서상 **15.0 이상** |
| Windows | **v1.0.914.1 부터 정식** |
| 현재 버전 | v1.0.922.1 (Chromium 153.0.8010.53) |
| 릴리스 주기 | 주 수회. Chromium 은 1~2주마다 |
| 가져오기 | 방문기록·쿠키·북마크. Safari 는 `File > Export` ZIP 만 허용 |

> ⚠️ **문서 내부 불일치**: `get-started.md` 는 "macOS 15.0 or later" 만 요구사항으로 말하는데
> 변경로그는 Windows 정식 지원을 기록한다. get-started 쪽이 낡았을 가능성이 높다 — 판정 보류.

주 수회 릴리스와 1~2주 Chromium 추격은 [01 §3](01-landscape.md) 에서 본 **브라우저 유지보수
부채**의 실물이다. 3인 규모 팀이라는 2차 정보가 맞다면 이 속도는 주목할 만하다.

## 8. 요금

| 플랜 | 가격 | 크레딧 | 주요 포함 |
|---|---|---|---|
| Free | $0 | 500/월 | BYO 구독, 루틴 3개, 비밀번호 관리자, 메모리 |
| **Pro** | **$20/월** | 3x | Ultrabrowse, 루틴 무제한, **Channels(원격 제어)**, **Cloud handoff** |
| **Max** | **$200/월** | 40x | 얼리액세스 |
| Enterprise | 문의 | — | 팀 에이전트 관리, 좌석·과금, 공유 프로필, 에이전트 자격증명 취급 |

> ⚠️ **불일치 기록**: 헬프 문서는 Max 를 "30x Free usage" 라 하고 가격 페이지는 "40x" 라 한다.
> 어느 쪽이 최신인지 판정 불가. 크레딧 1단위의 정의는 **어느 쪽에도 없다.**

## 9. 모델 — 하네스와 모델의 분리

세 갈래를 모두 지원한다.

| 갈래 | 내용 |
|---|---|
| **Aside** | 플랜 포함 모델. Free 는 무료 모델셋, Pro/Max 는 우선 모델 |
| **Subscription** | 기존 구독 재사용 — ChatGPT Plus/Pro, Claude Pro/Max, GitHub Copilot. **OAuth 로그인 흐름** |
| **API** | 직접 키 — Anthropic, OpenAI, OpenRouter, Google, xAI, Vercel AI Gateway, Cloudflare AI Gateway |

> 📌 **"구독 재사용"이 영리하다.** 사용자가 이미 내고 있는 ChatGPT·Claude 구독을 OAuth 로 끌어다
> 쓰게 해서, 도입 장벽에서 **모델 비용을 제거**한다. Free 플랜이 "Bring your own subscription"
> 을 첫 줄에 내세우는 이유다. 하네스 값만 받고 모델 값은 사용자가 이미 낸 것을 쓰게 하는 구조다.

특정 모델 버전명은 문서에 없다.

## 10. 루틴

| 유형 | 동작 |
|---|---|
| **Cron** | 일정에 따라 **새 작업**을 시작 — 주간 요약 같은 독립 반복 |
| **Heartbeat** | **기존 대화를 깨워 이어간다** — 같은 맥락을 나중에 계속할 때 |

- 겹치는 실행은 **건너뛴다**. 대상 대화가 없으면 루틴을 **일시정지**한다.
- **제안 기능**: 반복 작업을 스캔해 루틴 초안을 제안. 사용자가 편집 후 활성화하거나 버린다.
- 한도: Free 3개, Pro 이상 무제한.

> 📌 cron 과 heartbeat 의 구분이 설계상 정확하다. 반복 작업에는 "새로 시작"과 "이어하기"라는
> 서로 다른 의미가 있고, 대부분의 스케줄러는 전자만 제공한다. 대화 맥락을 가진 에이전트에게는
> 후자가 필요하다.

## 11. 커스텀 하네스 관점의 시사점

- [ ] **권한 등급과 자격증명 노출을 다른 축으로 분리하라.** full access 여도 비밀번호는 안 보인다
- [ ] **Deny 우선**을 명시하라. 규칙 충돌 판정을 문서에 적어라
- [ ] 격리 모드는 **자격증명까지 일관되게** 적용하라 (시크릿에서 금고 비활성)
- [ ] 자연어 · 프로토콜(MCP) · 결정적(REPL) **세 표면을 모두** 열어라. 모델이 약한 곳은 결정적 경로로 내려간다
- [ ] 반복 작업에 **"새로 시작"과 "이어하기"를 구분**해 제공하라
- [ ] 모델을 **사용자 구독으로 대체 가능**하게 하면 도입 장벽에서 모델 비용이 빠진다
- [ ] 기본값의 방향을 의식하라 — Aside 의 자격증명 기본값은 가장 느슨한 `Always allow` 다
