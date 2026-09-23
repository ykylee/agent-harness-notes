# 99. 출처와 검증 기록

> 이 저장소의 [인식 방법](../ai-workflow/wiki/concepts/primary-source-verification.md)을 그대로
> 적용한다: **커밋된 아티팩트 > 산문**, 2차 출처는 1차 대조 전 확정 금지, 추론은 추론이라 표기,
> 반증은 지우지 않고 보존. 조사일 2026-09-22.

## 1. 등급 어휘

| 등급 | 의미 |
|---|---|
| ✅ **확인** | 1차 출처(제품 문서 원본, 소스, 리버싱)에서 직접 읽음 |
| 🔧 **관측된 구현** | 리버싱으로 드러난 것. 벤더가 보증한 명세는 아님 |
| 📣 **자체보고** | 벤더 자신이 발표한 수치·주장. 독립 검증 없음 |
| 📰 **2차** | 언론·블로그. 1차 대조 전 |
| ⚠️ **미확인** | 확인 시도했으나 닿지 못함 |
| ❌ **반증** | 틀린 것으로 확인 |

## 2. 1차 출처

### Aside — 제품 문서 전체를 원본 마크다운으로

**`docs.aside.com` 은 `/llms.txt` 를 전체 색인으로 제공하고, 각 페이지에 `.md` 를 붙이면
원본 마크다운을 돌려준다.** 렌더된 페이지 요약이 아니라 1차 텍스트다.

> 📌 이것은 이 저장소의 기존 조사가 OpenAI 문서에서 발견한 것과 **같은 수법**이다
> ([`docs/99-sources.md`](../docs/99-sources.md)). 두 번째 사례가 생겼으니 일반적 기법으로
> 승격할 만하다 — 문서 사이트에 `.md` 와 `/llms.txt` 를 먼저 시도하라.

| 읽은 문서 | 추출한 것 |
|---|---|
| `/llms.txt` | 전체 문서 색인 18항목 |
| `help/get-started.md` | 시스템 요구사항, 가져오기, 온보딩 |
| `help/security.md` | **권한 3구역, Allow/Ask/Deny, 세션 모드 3종, 자격증명 은닉** |
| `help/tasks.md` | 작업 모드, 권한, Queue/Steer, 파일 결과 |
| `help/password-manager.md` | Vault 정책 3종, 생체 잠금 의미 |
| `help/passwords.md` | 자동완성 설정, 가져오기 9종, AI 접근 정책 기본값 |
| `help/memory.md` | 입력원, 보존 3종, 설정 3섹션 |
| `help/browser-basics.md` | **전체 단축키, 분할 탭, 라쏘, Ask AI** |
| `help/side-panel.md` | 페이지 첨부 모델, 탭별 초안 |
| `help/ultrabrowse.md` | 모델 선택기 내 위치, 용례 |
| `help/automation.md` | **cron / heartbeat 루틴, 제안 기능, 한도** |
| `help/ai.md` | 프로바이더 3갈래, OAuth 구독, API 키 7종 |
| `help/privacy.md` | 로컬 데이터 삭제 항목, 분석 공유 기본 on |
| `help/subscription.md` | 플랜 구성 |
| `changelog/native.md` | **버전, 플랫폼, 릴리스 주기, Chromium 추격** |
| `aside.com/pricing` | 가격 4단계 |

### 기타 1차·준1차

| 출처 | 성격 | 쓴 곳 |
|---|---|---|
| Zenity Labs, "Perplexity Comet: A Reversing Story" | 🔧 리버싱 | [04](04-comet-architecture.md) 전체 |
| Brave, "Agentic Browser Security: Indirect Prompt Injection in Perplexity Comet" | ✅ 보안 연구 원문 | [07](07-security.md) |
| `leaderboard.steel.dev` Online-Mind2Web | ✅ 3자 리더보드 | §3 |
| `github.com/OSU-NLP-Group/Online-Mind2Web` | ✅ 벤치마크 정본 | §3 |
| Wikipedia — Comet, ChatGPT Atlas | 📰 (날짜는 출처 표기됨) | [01](01-landscape.md), [04](04-comet-architecture.md) |

## 3. 벤치마크 주장 — 판정

**Aside 는 3개 벤치마크 1위를 주장한다.** 검증 결과:

| 주장 | 판정 | 근거 |
|---|---|---|
| Online-Mind2Web **99.0%** (297/300), Browser Use 97.7% | 📣 **자체보고** | 수치가 **Aside 자신의 GitHub 저장소**에 있고, **Aside 자신의 설정으로 채점**됐다. 감사된 리더보드가 아니다 |
| **3자 리더보드에 Aside 없음** | ✅ 확인 | `leaderboard.steel.dev` 의 Online-Mind2Web 목록에 Aside 항목이 **존재하지 않는다.** 1위는 Browser Use Cloud 97.0% (커스텀 에이전트 채점, 2026-03) |
| BU Bench V1 1위 | 📣 자체보고 | BU Bench V1 = WebBenchREAD·Online-Mind2Web 2·InteractionTests·GAIA·BrowseComp 에서 20개씩 뽑은 100개 과제 |
| Odyssey 1위 (OpenAI·Anthropic 등 상대로) | 📣 **자체보고, 그리고 경합** | Browser Use 는 **Odysseys 87.4% 로 자기가 선두**라고 발표한다. 양쪽이 같은 벤치마크에서 각자 1위를 주장 |

> ⚠️ **이 분야 벤치마크 수치를 제품 비교에 쓰지 마라.** 채점 방식이 제각각이다 — Steel 리더보드
> 자체가 "judge methodology varies" 를 경고하며 방법론 확인 없이 비교하지 말라고 적는다.
> Online-Mind2Web 정본도 WebJudge(o4-mini) / WebJudge(GPT-4o) / WebVoyager 별로 다른 점수를 낸다.
>
> 그리고 이 벤치마크가 **존재하는 이유 자체**가 "이전 웹 에이전트 벤치마크들이 현실 조건에서
> 성능을 극적으로 과대평가한다"는 문제의식이었다.

### 벤치마크 사양 (정본 확인)

| 항목 | 값 |
|---|---|
| Online-Mind2Web | 136개 라이브 사이트에서 **300개 과제** |
| 난이도 분할 | Easy 1–5스텝 83개 / Medium 6–10스텝 143개 / Hard 11+스텝 74개 |
| 채점 | WebJudge 자동(핵심포인트 식별 → 핵심 스크린샷 선택 → 결과 판정) 또는 사람. WebJudge(o4-mini)의 사람 판정 일치율 **85.7%** |
| v2 스키마 | 2026-05-23 도입 (사람 평가 용이화) |

## 4. Aside — 미확인·불일치 항목

| 항목 | 상태 |
|---|---|
| 하드웨어 기반 E2E 암호화, **Secure Enclave, 포스트양자 암호, 감사 로깅** | ⚠️ **랜딩 페이지 주장, 헬프 문서에 뒷받침 없음.** 구현 검증 불가 |
| 메모리가 **"plain markdown"** 으로 저장돼 편집 가능 | ✅ **해소 (2026-09-23)** — CLI 번들이 "distills user's context into **plain-Markdown files**" 라고 명시하고 `aside memory show MEMORY.md` · `aside memory path` 가 존재. 단 **직접 편집은 금지**된다. [08 §4](08-aside-code-level.md) |
| "local-first", 서버로 무엇이 가는가 | ⚠️ 프라이버시 문서는 **로컬 삭제 방법만** 말하고 서버 전송 여부는 말하지 않는다 |
| **Max 크레딧 배수** | ❌ **문서 내부 불일치** — 헬프는 "30x", 가격 페이지는 "40x". 어느 쪽이 최신인지 판정 불가 |
| **플랫폼 요구사항** | ❌ **문서 내부 불일치, 그리고 문서가 불완전** — `get-started.md` 는 macOS 15+ 만, 변경로그는 Windows 정식 지원을 기록. 게다가 **CLI 는 Linux x64·arm64 를 1급 지원**하는데 어느 문서에도 없다 (설치 스크립트 실측). [08 §2](08-aside-code-level.md) |
| 크레딧 1단위의 정의 | ⚠️ **어느 문서에도 없다** |
| 승인 UI 의 실제 형태 | ⚠️ 모달인지 인라인인지, 일괄 승인이 되는지 문서에 없음 |
| 회사 정보 (YC 기수, 팀 규모, 창업자) | ⚠️ 2차 출처가 "YC Fall 2025 / 3인 / 2024 설립"이라 하나 **내부 모순**(F25 배치와 2024 설립). 1차 미확인 — 본문에서 사실로 쓰지 않았다 |
| 인식·동작 방식 | ✅ **해소 (2026-09-23)** — CLI 번들 추출로 확인. 접근성 트리 + 가상 ref ID, `{tree, diff}` 반환, ref 기반 Playwright locator. [08 §3](08-aside-code-level.md) |
| 전송 계층 (외부 API) | ⚠️ 번들에 하드코딩된 aside 도메인 없음. 로컬 데몬 경유로 보인다 |
| 권한 강제·Vault 구현 | ⚠️ **CLI 번들 범위 밖** — 브라우저 바이너리에 있다 |

> 📌 이 표의 "미공개"가 많았던 이유는 **제품이 미성숙해서가 아니라 아무도 뜯어보지 않았기
> 때문**이었다. 2026-09-23 에 직접 뜯어서 절반이 해소됐다 — [08](08-aside-code-level.md).
> 정보량 차이를 성숙도 차이로 읽으면 안 된다는 원래 경고가 실증된 셈이다.

## 5. Comet — 등급

[04](04-comet-architecture.md) 의 내용은 전부 🔧 **관측된 구현**이다. Zenity 의 리버싱 결과이며
Perplexity 가 보증한 명세가 아니다. 다음이 따라 나온다:

- 벤더가 예고 없이 바꿀 수 있다. 확장은 서버에서 자동 갱신된다
- 리버싱 시점 이후 변경분은 반영돼 있지 않다
- 그럼에도 **마케팅 문구보다는 진실에 가깝다** — 이 저장소의 기본 입장

## 6. Atlas — 확인과 미확인

| 항목 | 등급 |
|---|---|
| 출시 2025-10-21 macOS, 종료 **2026-08-09** | ✅ 여러 출처 일치 |
| 기능이 ChatGPT·Codex 로 흡수, 30일 정리 기간, 북마크 수동 내보내기 | 📰 |
| 종료 사유 — **통합**(CNBC 2026-03-19) vs **보안 유지보수**(OpenAI 헬프센터) | ⚠️ **둘 다 공개돼 있고 무게는 밝혀지지 않았다.** 본문에서 병기했다 |
| OWL 아키텍처, 스크린샷 팝업 합성 | 📰 (OpenAI 엔지니어링 포스트 경유 보도. 원문 직접 확인 실패) |

⚠️ **OpenAI 헬프센터 원문(`help.openai.com/.../evolving-atlas-into-chatgpt...`)은 HTTP 403 으로
직접 읽지 못했다.** 종료 관련 서술은 전부 2차 경유다.

## 7. 조사 방법과 그 한계

### 쓴 방법

1. 제품 문서에 **`.md` 접미사와 `/llms.txt`** 를 먼저 시도 → Aside 문서 전체를 1차 텍스트로 확보
2. 리버싱·보안 연구를 **마케팅 페이지보다 우선**
3. 벤더 벤치마크 주장을 **3자 리더보드와 대조** → §3 의 판정이 나옴
4. 문서 간 **내부 불일치를 적극적으로 찾음** → §4 에 2건
5. **(2026-09-23 추가) 바이너리를 직접 열었다** — Linux CLI 를 설치해 Node SEA 페이로드를
   추출, 난독화되지 않은 ESM 번들 67,774줄을 확보. 재현 절차는 [08 §1](08-aside-code-level.md)

### 하지 못한 것 — 정직하게

| 항목 | 이유 |
|---|---|
| **GUI 를 직접 보지 못했다** | 조사 환경이 헤드리스 리눅스이고 **Aside 브라우저는 리눅스 빌드가 없다**. CLI 는 설치·분석했으나(§08) 브라우저 UI 는 여전히 미확인. 실제 UI·애니메이션·진행 상태 표현·승인 모달의 생김새는 확인 불가. [03](03-aside-design-ux.md) 은 **문서가 규정한 상호작용 모델**에 한정된다 |
| 로그인하지 않았다 | `aside login` 은 사용자 계정 자격증명이 필요한 행위라 하지 않았다. 따라서 `skills list` 의 실제 목록, `memory` 내용, 원격 호스트 동작은 미확인 |
| 브라우저 바이너리 미분석 | 권한 강제·Vault 암호화·인식 파이프라인의 실체는 macOS/Windows 브라우저 바이너리에 있다 |
| 시각 디자인 언어 (색·타이포·간격) | 위와 같은 이유. **추정으로 채우지 않았다** |
| Aside 의 내부 구조 | 문서에 없고 공개 분석도 없다 |
| Dia·Neon 의 아키텍처 | 1차 자료 부재. 2차 요약 수준에서 멈췄다 |
| 원 연구 논문 (워싱턴대 등) | 2차 보도만 확인 |

### 다음 조사에서 할 것

- [x] ~~`aside repl`/`mcp` 표면 확인~~ → [08](08-aside-code-level.md) 에서 규격까지 확보
- [ ] **macOS/Windows 기기에서** Aside 브라우저 GUI 확인 (승인 흐름, 진행 상태 표현) — 리눅스에서는 불가
- [ ] 브라우저 바이너리를 CLI 와 같은 방식으로 열기 — 권한 강제·Vault 가 거기 있다
- [ ] Aside 의 네트워크 트래픽 관찰 → "local-first" 주장의 실증 (§4)
- [ ] `aside skills list` 실제 목록 확인 (로그인 필요)
- [ ] 워싱턴대 2026-06 연구 원문 확보
- [ ] Dia / Opera Neon 의 1차 문서 탐색 (`.md` / `llms.txt` 수법 재시도)

## 8. 유효기간

이 분야는 **분기 단위로 뒤집힌다.** 조사 기간 중에만 해도: Atlas 가 종료됐고(2026-08),
Comet 이 전면 무료화됐고(2026-03), Aside 가 Windows 를 냈다. 재조사의 첫 수는 새 사실 수집이
아니라 **기존 사실의 드리프트 확인**이다 — 특히 §4 의 불일치 항목과 [01 §4](01-landscape.md) 의
가격·플랫폼 표.
