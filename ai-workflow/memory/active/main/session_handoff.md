<!-- standard-ai-workflow-kit: v1.10.0 -->

# Session Handoff

- Purpose: Compact restore context for the next AI agent session.
- Scope: current focus, task status, key changes, next actions, risks
- Audience: AI agents, maintainers
- Status: active
- Updated: 2026-09-30 (저녁: 드리프트 3축 대조 + Gas Town 오케스트레이션 축, 병합 `6a2bb44`)
- Related docs: [Project Profile](../../../docs/PROJECT_PROFILE.md), [PURPOSE](../PURPOSE.md), [SYNTHESIS](../../../SYNTHESIS.md), [state.json](./state.json), [backlog](./backlog/)

## Current Focus

- **2026-09-30 저녁 — 드리프트 3축 대조 + 오케스트레이션 축 신설 완료 (병합 `6a2bb44`).** worktree `feat/auto-20260930-a5e9e422` 에서 수행해 main 에 `--no-ff` 병합. **반박 0건.**
  - **Codex** `bcd6d9ab6b` → `92bc601ad6` (8커밋·134파일): `thread/goal/set|clear` params 에 `origin`(user|automatic) 신설. Rust 정의 + **생성 Python SDK** 양쪽 확인 = 와이어 계약. 계약 문구 "Missing provenance does not supply user authorization." 서버는 `origin == User` 일 때만 user fragment 를 히스토리에 기록. `thread_goal_user_context.rs:2` — "tool-created goals never use this path." → **기록 출처 판별자이지 권한 확장이 아니다.** Guardian 스킵 warmup(`a5cce8895a`) = **게이트 가용성과 정확성이 분리된 축**(회귀 테스트가 executor 오프라인 상태에서 deny 를 검증). `model_catalog_in_context`(`2e5fea64ee`, off 기본) = providers-as-data 축 후보. `docs/02` §9 · `docs/12` §2.2 · `docs/99` §E.5 반영
  - **Strands** `a9a62d4e` → `4dfeca8c` (2커밋): bidi reconnect → **restart** 리팩터링 + prettier bump. `git diff --name-only | grep -iE "approval|permission|consent|cedar|sandbox|intervention|harness"` **출력 없음** → 승인 기본 off·Cedar fail-open·sandbox `host`·등록순 단축이 그대로 성립, **P1–P5 재실행 불필요**(2개 창 연속 확인)
  - **ACP** `9b26a3ea` → `7d794e0e` (8커밋): **`schema/v1/schema.json` 바이트 동일** — 안정 와이어 무변경, 승인 RPC(메서드 하나·kind 4종) 그대로. CHANGELOG 3건은 **전부 `*(unstable)*`** 라서 스키마가 안 바뀐 것 — 6,791줄 diff 를 "계약 변경"으로 읽으면 오판이다. **MCP-over-ACP request-scoped(#2223)는 승인과 무관** — `mcp/message` payload 에 `sessionId`·`toolCall`·`PermissionOption` 을 실을 자리가 없고, `MessageMcpResponse` 가 outer ACP error 를 "binding and runtime failures" 로 예약한다. **근거는 페이로드 형태이지 "스키마 불변" 이 아니다**
  - **Gas Town 신설 — `gas-town/` 6편, 위키 19종.** Steve Yegge `gastownhall/gastown` @ `649b832b76`. 목적은 **오케스트레이션 기법 참고**였고 A1–A11 을 발쑌다(`gas-town/04`). **기여하지 않는 축을 명시** — approval 은 약화가 아니라 대비(post-hoc 신뢰 모델), provider-as-data 는 wire 전제 유지. **관찰 0건** — 바이너리 미실행, 전부 source-read
  - **문서 오류 1건 정정 — 존재하지 않던 참조 클론 2개.** `~/repos/harness-refs/{strands-harness-sdk,agent-client-protocol}` 가 문서에 정본 경로로 적혀 있으나 실재하지 않았다. 재생성함
  - **기존 축 1곳 강화** — control/execution plane 을 **credential 경계**로: 파일만 격리하고 결과 원장이 쓰기 가능하면 plane 분리는 실패다(`control-plane-execution-plane` §5.6 신설)
- **이 저장소의 조사는 안정 상태다. 남은 작업은 전부 기기나 동적 관찰을 요구하거나, 기존 사실의 드리프트 점검이다.** 조사 넷(`docs/` Codex · `browser-agents/` · `strands/` · `agent-ux/`), 위키 개념 18종, `SYNTHESIS.md` 가 교차 종합, `REPORT`(영/한)에 외부 증거·Strands·클라이언트 절 반영.
- **조사 ↔ 구현 되먹임 루프가 자리잡았다.** 구현은 `ykylee/heddle` (private), 이 저장소 범위 밖이다(`PURPOSE.md` §0.1: **측정만 편입하고 코드는 밖에 둔다**). 이번 세션에 그 경로로 들어온 것이 `SYNTHESIS.md` §6 이다 — 반박 5건, 확인 6건, 방어 공격 5건 관통, 모델 실측 2공급자.
- **주입 위협 모델 재검토 완료 (TASK-015).** Brave 원문을 다시 읽으니 유출은 "공격자 서버로 navigate"가 아니라 **Reddit 댓글에 답글 달기(쓰기 1회)** 였다. 체인 어디에도 공격자 목적지가 없다. 어긋남은 시연과 실측 사이가 아니라 **우리 한 줄 요약과 원문 사이**에 있었고, 그 요약이 heddle 프로브 설계까지 흘러갔다. 정정하면 시연과 실측은 일치한다 — **목적지 기반 방어는 둘 다 못 막는다. 쓰기를 게이트해야 한다.**
- **세 번째 사례 Strands 편입 (TASK-2026-09-26-main-001).** `strands/` 8편 — AWS Strands Agents SDK 와 2026-09-22 에 나온 **Strands harness**(`create_harness()`)를 `harness-sdk@15da9dc` 소스로 읽었다. 호출자와 루프 사이에 wire 가 없는 **임베드형** 하네스라 Codex·Aside 와 다른 축에서 추상을 시험한다. 결론: **루프 밖 승인 게이트는 필요조건일 뿐** — Strands 는 그 게이트를 가졌지만 기본 off, 오류 경로 fail-open(Cedar·steering, 🧪 대조군 포함), 등록순 합성, hard deny 없음 (`SYNTHESIS.md` §2.7). provider-as-data 는 **공유 wire 전제에서만** 성립한다는 한정도 붙었다 (§2.3)
- **클라이언트 측 조사 `agent-ux/` 편입 (TASK-2026-09-26-main-002).** 범위는 `PURPOSE.md` §0.2 로 먼저 기록. 제품 10종(Claude·ChatGPT/Codex·Cursor·Antigravity·Devin(구 Windsurf)·Orca·Superset·Paseo·Conductor + Aside)을 설치본 번들·소스에서 정적 추출. **공통 디자인 언어는 수렴했고(“Allow ⟨agent⟩ to ⟨verb⟩?”, Queue/Steer, amber=needs you, 자율성 다이얼 중간의 기계 리뷰어) 감독 이론은 갈렸다** (`agent-ux/09`, `SYNTHESIS.md` §2.8). 오케스트레이터 3종이 감싼 에이전트의 승인을 기본 off 로 띄운다 — §2.7 "기본 on" 속성 결여. 디스플레이가 없어 시각 인상은 전부 ⚠️
- **Codex 드리프트 재확인 완료 (TASK-002).** `openai/codex` `2fdcdeaf0e`(09-15) → `e72da2b538`(09-26), 686커밋, `docs/` 16편 전수 대조. 드리프트보다 **반박(기준 시점부터 틀림) 14건**이 더 무겁다 — 핵심은 `docs/02` "104 total" 이 stable 부분집합이었다는 것: 생성 TS 스키마가 `#[experimental]` 클라이언트 메서드 62개(현재 63)·서버 요청 1개(`currentTime/read`)를 빼고, experimental 알림 22개는 남긴다. agent-ux 단서 3종은 드리프트가 아니라 **오픈소스·번들 엔진 어디에도 없는 webview 전용 메서드**(8개). 기록은 `docs/99-sources.md` §E
- **작업 환경이 macOS 로 이동했다 (2026-09-26).** 두 저장소가 공유하던 막힌 지점(디스플레이 있는 기기)이 풀렸다 — 설치된 ChatGPT.app 번들을 이번 세션에서 직접 읽었다. GUI 패스·동적 관찰이 이제 실행 가능한 작업이다

## Work Status

- 2026-09-30 저녁 (병합 `6a2bb44`): Codex 8커밋 · Strands 2커밋 · ACP 8커밋 드리프트 대조 + Gas Town 오케스트레이션 조사 — **done**. **반박 0건.** 상세는 `ai-workflow/memory/active/feat/auto-20260930-a5e9e422/`
- 2026-09-30 저녁 드리프트 3축 + Gas Town 조사: done
- TASK-2026-09-30-main-013 Anthropic redacted_thinking KeyError 확인: done
- TASK-2026-09-30-main-012 REPORT 개념 수 16→18 및 agent-ux 편입: done
- TASK-2026-09-30-main-011 ACP 엔진측 독해 (스펙·스키마 vs Strands CLI / Codex App Server): done
- TASK-2026-09-30-main-010 Strands TS SDK 세부 직접 확인 (event union · modelState · stateful formatter): done
- TASK-2026-09-30-main-009 Strands harness 0.x 드리프트 재확인 (`15da9dc`→`a9a62d4e`, 31커밋): done
- TASK-2026-09-30-main-008 Aside Computer Use 호출 흐름 (데몬 spawn + JSON-lines IPC): done
- TASK-2026-09-30-main-007 Dia macOS 바이너리 정적 분석 · Neon netinstaller 스텁: done
- TASK-2026-09-30-main-006 harness-refs/codex origin 을 GitHub 로 고정: done
- TASK-2026-09-30-main-005 Agents 플러그인 `./` 규칙과 onboardingSkill 예외 관계: done
- TASK-2026-09-22-agent-harness-notes-004 Windows 샌드박스 내부 구조 추론→확인 승격: done


> 상한(10) 이전의 완료 항목은 `backlog/tasks/` 에 있다 — 09-30-004 (CLAUDE.md kit), 09-30-003 (다른 저장소 overlay), 09-30-002 (형제 스킬 overlay), 09-30-001 (session-start overlay), 09-27-001 (ChatGPT webview/durable), 015·014·013·012·011·010·009·008 (위협 모델, 공급자 정정, 모델 측정, 주입 방어, SYNTHESIS §6, REPORT, 파서 라벨, 브랜치 병합), 001·005·006 (워크플로우 도입, 위키 계층, 재색인 강제), browser-agents-001~007 (조사 착수, CLI 바이너리 추출, Aside 바이너리·집행 분석, Dia·Neon 심화, 두 조사 융합, 영어 통일). `blocked`: TASK-2026-09-27-main-002 (GUI 패스 — 스크래치 프로젝트 지정 필요).

## 현재 `in_progress` 작업

-

## 현재 `blocked` 작업

- TASK-2026-09-27-main-002 agent-ux GUI 패스 — 수동 패스는 끝났고, 승인 카드·에이전트 상태(blocked/waiting)는 에이전트 실행이 필요하다. 각 앱이 사용자 프로젝트를 가리키고 스크래치 폴더 지정은 파일 대화상자라 `orca computer` 로 못 연다 → 사용자가 앱별 스크래치 프로젝트를 한 번 지정하면 재개

## Key Changes

- **Anthropic redacted_thinking KeyError (TASK-013)** — Python `_format_request_message_content` 가 redacted-only 블록에서 `KeyError: 'reasoningText'`. stream `redacted_thinking` start 는 `data` 폐기. TS 는 stream·replay 모두 처리. 라이브 키 없이 메서드 컴파일 실행. `strands/02` §5.2, 위키 `retained-reasoning` §5.5
- **REPORT 개념 18종 · agent-ux 편입 (TASK-012)** — 영/한 REPORT에 § The client side / § 클라이언트 쪽, 권고 11(래퍼는 감싼 에이전트 승인을 켜 둔다). 개념 수 16→18. Method에 ACP 산출물≠와이어. Windows 내부·Agents API 모델 목록은 정착으로 표기. PSV 재ingest
- **ACP 엔진측 독해 (TASK-011)** — 스펙 HEAD `9b26a3ea`. 안정 와이어는 `protocolVersion` **1** (crate 1.9.1 / schema-v1.23.0 / SDK 1.3.0 은 산출물 버전). 승인은 메서드 하나 `session/request_permission`, kind 네 개 `allow_once` · `allow_always` · `reject_once` · `reject_always`. Codex App Server 는 요청 10종. Strands harness ACP 경로는 그 RPC 를 안 보냄 (소스 ✅, 라이브 클라이언트 ⚠️). `agent-ux/10`, 위키 개념 `agent-client-protocol` (18종)
- **Strands TS SDK 직접 확인 (TASK-010)** — `AgentStreamEvent` 16종. `modelState` 는 미들웨어 전 스냅샷, temp `StateStore` 로 모델에 전달, 성공 시에만 write-back. stateful Responses formatter 는 invocation 전체 `input` + `previous_response_id` (슬라이스 없음). API 반응은 ⚠️. `strands/02` §3.2·§4.2
- **Strands 0.x 드리프트 재확인 (TASK-009)** — `15da9dc`→`a9a62d4e` 31커밋. 버전 태그 없음 (1.57.1 / 1.19.0 / 0.1.x). 승인 기본 off · Cedar fail-open · sandbox host · 등록순 합성 유지. Cedar/intervention/sandbox 빈 diff 라 P1–P5 미재실행. R19 README 문장 #4696 에서 삭제. #4447 은 squash `4095cf5a`. 로컬 `~/repos/harness-refs/strands-harness-sdk`. `strands/99` §6
- **Aside Computer Use 호출 흐름 (TASK-008)** — `Aside-1.0.928.1.dmg`. 데몬이 `aside-computer-use` 를 stdin/stdout 파이프로 spawn. JSON-line `invoke`/`policy`/`permissions`/…. iMessage·카카오·Contacts 는 invoke 이름. stdout 은 `mac_ax` 스냅샷(fullTree/diff). Swift 내부 미분해, 미실행. `browser-agents/10` §2.3
- **Dia macOS 바이너리 열림 (TASK-007)** — `Dia-1.50.1-87750.dmg`. ArcCore Chromium fork + 로컬 `agent-server` 가 bundled Claude Code 2.1.270 을 Seatbelt 안에서 spawn. 보안 페이지 문장(LLM URL 비추적·verbatim URL 차단·요소 숨김)은 번들에 없고, 프롬프트 층 untrusted-data + `url://` 단축 + Seatbelt 가 있다. 스냅샷 요소 숨김은 ⚠️. Neon 공개 URL 은 4.1MB netinstaller 스텁(Linux 404). MCP 방향이 반대: Dia 는 import, Aside·Neon 은 export. `browser-agents/12`, 위키 10종 재ingest
- **ChatGPT 앱은 엔진을 둘 몬다 (TASK-2026-09-27-main-001)** — 로컬 `codex app-server` + 클라우드 `durable`("Long-lived", `wss://codex-cloud-backend.chatgpt.com/`). durable 전용 어댑터가 방언 변환(`thread/queue/add`→`turn/addUserMessage`, `thread/start`→`thread/prewarm`)하고 `config/*` 는 클라이언트 메모리에서 답한다. webview 전용 8개 재분류, 그중 `plugin/codex` 는 메서드가 아니었다(09-26 스윕 오류). 이 계정엔 durable 미개통(로그 `state=disconnected`). `docs/99` §E.3
- **agent-ux 수동 GUI 패스 (TASK-2026-09-27-main-002, 일부)** — `orca computer` 로 설치 5종 캡처. 레이아웃 확인, **amber 규칙 완화**(ChatGPT 는 Full access 위험 상태를 주황으로, Claude 작업 중 = 점토색 스파크). `agent-ux/99` GUI pass 절. 스크린샷은 사용자 데이터라 저장소에 넣지 않았다
- **Codex 드리프트 재확인 (TASK-002)** — 반박 14건(`docs/99` §E.1): `codex mcp-server`·`--full-auto` 는 기준일 전 이미 제거, Python SDK 는 이미 app-server JSON-RPC, Windows elevated 는 특권 서비스 필수 아님(`service_identity.rs`), `hide_users.rs` 추론 반박, `worldWritableWarning` 은 아무도 안 보냄, `ResponsesApiRequest` 16필드, WebSocket 은 `previous_response_id` 를 잇는다(무상태는 HTTP 한정). 드리프트: gatewayOAuth 4종, Windows `mxc`·private desktop opt-out 제거, `model_catalog_url`, 로컬 모델 +gpt-6-sol/luna −gpt-5.4, Agents API 턴 오류코드 17→18. 방법론 교훈을 `primary-source-verification` 에 추가 — **생성 산출물의 개수를 총계로 쓰기 전에 생성기가 무엇을 빼는지 읽어라**. 위키 12종 재ingest, `SYNTHESIS`·`REPORT`(영/한)·`README` 수치 정정
- **agent-ux 조사 (TASK-2026-09-26-main-002)** — `agent-ux/` 01~09·99. 전제 2건이 틀렸다: **ChatGPT 데스크톱 = Codex Electron 앱**(네이티브 SwiftUI 는 업그레이드 화면을 띄우는 레거시), **Windsurf = Devin Desktop**, Antigravity 와 `CortexStepType` 45개 중 43개 필드 번호 일치. Paseo 가 `SYNTHESIS` §2.1 의 "그냥 답장" 을 프로토콜 규칙으로 구현(보류 중 메시지 = 사유 붙은 거부). 반박 13건은 대부분 문서 지연(`agent-ux/99` §4). 새 위키 개념 `agent-client-design-language`(17종)
- **Strands 조사 (TASK-2026-09-26-main-001)** — `strands/` 01~07·99. 반박 20건(`strands/99` §4): 승인 계층 R1–R5 가 가장 무겁다 — 문서는 "Cedar 평가 오류는 항상 fail-closed", "deny > confirm > … 우선순위", `auditLog` 를 약속하지만 코드는 아니다. 벤치마크 "동등 이상 정확도"는 차트 자체 데이터로 19쌍 중 7쌍에서 낮다 — **문구 반박이지 순위 반박이 아니다**(분산 없음). 설계 문서 "Proposed" 13건 중 11건이 이미 구현 → 새 등급 📐 designed-only. `llms.txt` 기법 기록에 변형 추가(`<page>/index.md` 만 200). 위키 개념 7종 재ingest, `PURPOSE.md` 포함 영역에 임베드형 SDK 하네스 명시
- **Brave 시연 요약 정정 (TASK-015)** — "공격자 서버로 전송"은 원문에 없다. 원문 4단계는 perplexity.ai(trailing-dot 변형 포함)·gmail.com 을 읽고 **원래 댓글에 답글로 유출**한다. `browser-agents/99-sources.md` §4.5 반박, 위키 `indirect-prompt-injection`·`primary-source-verification` 재ingest, `SYNTHESIS.md` §7 에 방법론 항목 "요약 위에 테스트를 짓기 전에 원문을 다시 읽어라" 추가. §6.5·§6.7 에 남아 있던 단일 실행 수치(9/20→3/20, 45%)와 "one model" 표현도 함께 정정

- **저장소 범위 확장** — `PURPOSE.md` §0 에 기록. 제외 영역에서 "OpenAI 외 벤더" 삭제, Goals G5 추가. `study/browser-agents` 의 A안 조건 이행.
- **조사가 둘이 됐다** — `browser-agents/` 14편 신설. Aside 는 제품 문서 1차 확보 후 **CLI·브라우저 바이너리까지 정적 분석**했다.
- **위키 개념 13 → 16종** — 기존 8종에 브라우저 근거 추가, 신규 3종(`perception-model`·`indirect-prompt-injection`·`credential-shielding`).
- **`SYNTHESIS.md` 신설** — 핵심 주장은 **표면 무관 축과 표면 고유 축의 구분**이다.
- **모델을 넣어 나머지 절반을 쟀고, 두 번째 공급자로 앞선 결론 2건을 정정했다 (§6.5)** — navigate 유출형은 **두 모델 모두 0/120**, 즉 연구가 중심에 둔 공격 모양은 재현되는 음성 결과다. 그러나 "버튼에는 넘어간다"는 **재현되지 않았다** — MiniMax 약 40%, DeepSeek 0/40. 그건 모델의 성질이 아니라 그 모델의 성질이다. 봉투는 3회 풀링 24/60 → 10/60 이지만 회차별 1~6 로 흔들려 **방향은 실측, 비율은 아니다**(처음 보고한 9/20→3/20 은 단일 실행이었다). 그리고 **두 번째 공급자는 봉투를 확인해주지 못했다** — 아무것도 안 따르는 모델에는 줄일 신호가 없다(바닥 효과)
- **주입 방어를 처음으로 공격했다 (§6.4)** — 조사가 "이 분야의 중심 위험인데 누구도 자기 방어를 검증하지 않았다"고 기록한 바로 그 지점. Dia 의 공개 방어를 구현해 공격했더니 **16건 중 5건 관통**. 차폐가 입력 *타입* 만 봤고, 필드를 다 막아도 비밀이 **URL** 로 샜고, 보이지 않는 문자가 단어 경계를 이겼다. **인지 계층 방어는 전부 공격자가 연구할 수 있는 휴리스틱이고, 게이트만 모델의 통제 루프 바깥에 있다.**
- **`SYNTHESIS.md` §6 구현 피드백 편입** — 이 저장소에서 가장 강한 근거 등급이 생겼다: 다른 모든 주장은 남의 산출물을 **읽은** 것이고 §6 은 **실행한** 것이다. 반박 5건·확인 6건. 개념 페이지 3종(`perception-model`·`approval-gate`·`primary-source-verification`)과 `PURPOSE.md` §0.1 경계를 함께 갱신했다. **구현 코드는 여전히 이 저장소 밖이다 — 들어온 것은 측정뿐이다.**
- **내용 문서 전체 영어**. 규칙과 예외는 `docs/PROJECT_PROFILE.md` §6.
- **`REPORT`(영/한)에 외부 증거 절 추가** — 권고 여럿이 서드파티 시스템에서 독립 구현된 것으로 확인됐다.
- 브랜치 병합(`--no-ff`)·삭제, 고아 메모리를 `memory/archived/` 로 아카이브.
- **하류 구현 착수 (이 저장소 외부, 기록만)** — `SYNTHESIS.md` 의 표면 무관 축(대칭 네임스페이스·정책 우선순위·승인·비밀 핸들)을 `ykylee/heddle` 에서 코드로 옮겼다. 설계 주장 5건이 실측에 반박당했다. 드러난 버그 중 **세 건은 같은 결함의 반복**이었다 — 요소 식별자가 구별 축(스냅샷 세대 · 프레임 · 프로세스 생애)을 담지 못해 옛 참조가 조용히 다른 요소로 해석됐다. **이 결과는 `SYNTHESIS.md` §6 으로 편입됐다.**

## Next Actions

**2026-09-30 저녁 세션이 남긴 것 (feat 워크스페이스에서 이월)**
- [ ] **Gas Town 런타임 검증 — 이 축의 가장 큰 구멍.** `gt`/`bd` 미실행이라 관찰 0건. 소규모(3~5 polecat) town 을 구성해 sling→merge 사이클을 재현하면 `gas-town/03` §5 의 Stalled/Zombie 상태와 propulsion 이 **관찰** 가능해진다
- [ ] `model_catalog_in_context`(`2e5fea64ee`, off 기본) 의 providers-as-data 축 해석 — **미분석, 단정하지 말 것** (§2.3 의 "공유 wire 전제" 한정과 관계 있음)
- [ ] `SYNTHESIS.md` §2 에 **게이트 가용성 축** 편입 여부 (Guardian 스킵 warmup 근거)
- [ ] `SYNTHESIS.md` §2.4 에 **credential plane** 편입 — `control-plane-execution-plane` §5.6 에 이미 기록됨
- [ ] Gas City(분해 SDK) · Beads standalone 미독 — 개념 축 연속성 확인용
- [ ] Strands 태그/버전은 `4dfeca8c` 까지만 확인 — 다음 창에서 재확인
- [ ] `check_wiki_freshness.py` 가 stale 을 알린다 — **근거 없는 갱신으로 메우지 말 것**(§ Risks)

**Codex 조사 (`docs/`)**
- [x] ~~TASK-002: 2026-09-15 이후 `openai/codex` 변경분 대조~~ — 완료, `docs/99` §E. 2026-09-30 HEAD `bcd6d9ab6b` 후속 107 / 10 / 86. 다음 드리프트 기준은 `bcd6d9ab6b`
- [x] ~~webview 전용 메서드의 수신 엔진~~ — 클라우드 durable 호스트(TASK-2026-09-27-main-001). 남은 것: durable(Aeon) 엔진의 실체·동작은 개통된 계정에서만 관찰 가능
- [x] ~~`docs/10` L200 Agents API 플러그인 `./` 규칙과 `onboardingSkill` 예외~~ — 두 표면. Agents 는 `./` 강제·필드 없음. Codex overlay 만 `./` 생략 허용 (`resolve_openai_onboarding_skill`, #46544). TASK-2026-09-30-main-005
- [x] ~~참조 체크아웃 `~/repos/harness-refs/codex` origin~~ — 이 Linux 호스트에는 경로가 없어 GitHub origin 으로 생성 (`blob:none`, HEAD `d42056091a`). 다른 기기에서 origin 이 개인 Gitea 이면 `upstream` 으로 GitHub 를 fetch. TASK-2026-09-30-main-006
- [x] ~~TASK-003: Agents API 서버측 모델 목록~~ — 2026-09-30 세 표면으로 정착 (unconstrained string / 카탈로그 11 / ModelIdsShared 89). 라이브 POST 는 키 필요
- [x] ~~TASK-004: Windows 샌드박스 내부를 모듈명 추론에서 소스 독해로 승격~~ — HEAD `bcd6d9ab6b`. `CreateRestrictedToken` / deny ACE / WFP 12 + `INetFwPolicy2` / `CreateDesktopW`. Windows 런타임 미실시

**브라우저 조사 (`browser-agents/`)**
- [x] ~~검증 비대칭 해소 (Dia)~~ — macOS DMG 정적 분석 [12]. ArcCore + 로컬 Claude Code 2.1.270. Neon 은 netinstaller 스텁만 (Linux 404). TASK-2026-09-30-main-007
- [x] ~~`Aside Computer Use` 호출 흐름~~ — 데몬 spawn + JSON-lines IPC ([10] §2.3). Swift 내부는 ⚠️. TASK-2026-09-30-main-008
- [ ] 동적 관찰 (서버로 가는 내용) — **macOS 환경에서 이제 가능**
- [ ] 브라우저 GUI 1차 확인 — **macOS 환경에서 이제 가능** (리눅스 빌드는 없다)

**Strands 조사 (`strands/`)**
- [ ] 위조 `<system-reminder>` 태그를 모델이 하네스 권위로 받아들이는지 — 프롬프트 계약이 그렇게 말하고 아무도 이스케이프하지 않는다(`strands/07` §2.1). **실측은 heddle 측 작업**, 결과만 편입
- [ ] 장기 메모리가 주입 지시를 세션 너머로 나르는지 (⚠️ 소스상 경로만 확인)
- [x] ~~Native Anthropic `redacted_thinking` KeyError~~ — Python replay KeyError, stream drop. TS 는 양쪽 처리. 라이브 API ⚠️. TASK-2026-09-30-main-013
- [x] ~~TS SDK 세부의 직접 확인 · stateful Responses 툴 루프 중복 전송~~ — event union 16종, `modelState` 스냅샷/write-back 확인. formatter 는 invocation 전체 `input` + `previous_response_id` (슬라이스 없음). API 반응은 ⚠️. TASK-2026-09-30-main-010
- [x] ~~`REPORT`(영/한)에 세 번째 사례 반영~~ — `§ A third case` / `§ 세 번째 사례` 신설, 권고 9·10 추가, 두 결론(권고 7 게이트, 프로바이더-데이터)에 단서. 무효화된 결론 없음
- [x] ~~harness 는 0.x, 출시 3일차 스냅샷이다 — 재조사의 첫 수는 드리프트 확인~~ — `a9a62d4e` 31커밋, 보안 기본값 유지. TASK-2026-09-30-main-009. 다음 드리프트 기준은 `a9a62d4e`

**agent-ux 조사 (`agent-ux/`)**
- [ ] GUI 패스 — 수동 패스 완료(설치 5종). 남은 것: 앱별 스크래치 프로젝트에서 에이전트 실행해 승인 카드·상태 관찰. 미설치 5종(Cursor·Devin·Superset·Paseo·Conductor)은 ⚠️ 그대로
- [x] ~~Codex 드리프트 단서 3종~~ — TASK-002 에서 판정: 드리프트 아님, webview 전용 (`agent-ux/03` §1.2.1 갱신)
- [x] ~~ACP(Agent Client Protocol) 엔진측 독해~~ — `agent-ux/10`. 안정 와이어 1, 승인 RPC 하나. 라이브 클라이언트와 Devin/Paseo/Superset 트레이스는 남음. TASK-2026-09-30-main-011
- [x] ~~`REPORT`(영/한) 개념 수 16→18 및 agent-ux 반영~~ — § The client side / § 클라이언트 쪽, 권고 11, 개념 18종. PSV 재ingest. TASK-2026-09-30-main-012
- [ ] 모바일 컴패니언(Orca·Superset·Paseo)은 이번 패스에서 제외

**저장소**
- [x] ~~위키 신선도 검사기 오탐 4건~~ — 수정(`parse_source`). 버그가 가리던 실제 경고 3건도 드러나 절 단위 대조로 처리. 남은 한계: 검사가 파일 단위라 절(§) 선언을 무시한다
- [x] ~~pre-commit 훅 활성화~~ — 이 clone 에 `core.hooksPath .githooks` 설정 (2026-09-26)
- [x] ~~`SYNTHESIS.md` 구현 피드백 절 편입~~ — TASK-011 완료. `PURPOSE.md` §0.1 에 "측정만 편입, 코드는 아님" 경계를 명시했다
- [x] ~~간접 프롬프트 주입 방어 검증~~ — TASK-012. Dia 의 공개 방어를 구현해 공격했다. **16건 중 5건 관통.** 결과는 `SYNTHESIS.md` §6.4
- [x] ~~나머지 절반: 모델이 루프에 있을 때~~ — TASK-013. `SYNTHESIS.md` §6.5
- [x] ~~두 번째 모델~~ — DeepSeek 추가. 취약성 질문은 갈렸고 **방어 질문은 갈리지 않았다**
- [ ] **봉투 검증에는 실제로 취약한 모델이 필요하다.** DeepSeek 은 아무것도 안 따라서 방어 효과를 보여줄 수 없다(바닥 효과). 취약한 세 번째 공급자, 또는 MiniMax 회차를 더 쌓는 것 중 하나 — 아무도 명시하지 않는 요건이고 모델을 붙여본 뒤에야 알게 된다
- [ ] Google 키는 402(크레딧 소진)라 측정 불가. 복구되면 세 번째 점이 생긴다
- [x] ~~§2/§3.2 위협 모델 재검토~~ — TASK-015. 원문 재독으로 요약 오류 발견·정정. `browser-agents/07` §2·§10, `SYNTHESIS.md` §3.2·§7
- [ ] **원문 체인 그대로의 측정은 아직 없다** — 세션 횡단 읽기 여러 번 → 쓰기 1회, 다단계. 지금 실측은 단발·합성 페이지·공격자 origin navigate 였다. 프로브는 heddle 쪽 작업이다(범위 밖) — 측정이 나오면 §6.5 로 편입
- [ ] Dia 의 "되돌릴 수 없는 버튼"에 공개 정의가 없다 — 우리 측정은 *서술의 구현* 을 공격한 것이라 Dia 코드에 대한 평가가 아니다. 1차 출처가 생기면 이 경계를 갱신할 것
- [ ] `SYNTHESIS.md` §6 은 heddle 의 2026-09-23 시점 실측이다. heddle 이 진행되면 여기도 드리프트한다

## Risks & Blockers

- **"0 은 입력이 도달했음을 증명할 수 있을 때만 증거다."** 이번 작업에서 전달 실패가 *좋은 숫자*로 찍힌 사례가 네 번 나왔다 — 프레임 미순회, charset 모지바케, interactive 모드가 페이로드를 버림, 그리고 공급자가 404 를 200번 내는데 **완벽한 방어로 렌더**. 네 번 다 assertion 은 리뷰에서 멀쩡해 보였고, 실제로 도달한 것을 출력해서야 잡혔다. `SYNTHESIS.md` §7 에 방법론 항목으로 올렸다
- **근거 등급이 칸마다 다르다.** Aside 는 바이너리까지, Dia macOS 는 같은 방법으로 열림 ([12] — ArcCore + seatbelted Claude Code), Neon 은 문서+netinstaller 스텁, Comet 은 3자 리버싱이다. 비교표를 읽을 때 이 비대칭을 잊으면 안 된다 — `SYNTHESIS.md` §8 에 경고로 달아뒀다.
- 두 분야 모두 빠르게 낡는다. Codex 는 2026-09-15, 브라우저는 2026-09-22/23 기준이다. 재조사의 첫 수는 **기존 사실의 드리프트 확인**이다.
- `docs/` 또는 `browser-agents/` 를 고치면 **위키 재색인이 따라와야 한다.** pre-commit 훅이 막지만 `core.hooksPath` 를 설정한 clone 에서만 돈다 — 새 clone 에서는 `git config core.hooksPath .githooks` 가 필요하다.
- `wiki/SCHEMA.md` 는 kit 생성물이라 한국어로 남아 있다. 번역하면 kit 재생성과 갈린다.
