---
type: concept
status: active
last_ingested_from: docs/01-overview.md + docs/06-choosing.md + docs/12-product-surface.md
related_pages: [concepts/harness-engineering, concepts/thread-turn-item, concepts/control-plane-execution-plane, concepts/wire-protocol-boundary]
created: 2026-09-22
updated: 2026-09-22
---

# Harness (에이전트 실행 시스템)

- 문서 목적: "하네스"가 무엇이고 그 안에 무엇이 들어가는지, 그리고 OpenAI 가 이 실행 시스템을 몇 겹으로 열었는지를 정리한다.
- 범위: 정의, 내부 구성요소, 3+1 계층 개방 구조, 애플리케이션이 쥐는 몫, 표면의 크기
- 1차 출처: `openai/codex` 저장소 + "Codex as a platform" / "Unlocking the Codex harness" 포스트
- 최종 수정일: 2026-09-22

## §1 TL;DR  {#s1-tldr}

| # | 항목 | 값 |
|---|---|---|
| 1 | 한 줄 정의 | **모델과 과업 사이에 앉은 실행 시스템** |
| 2 | 제품 가치의 위치 | 채팅 UI 가 아니라 이 실행 계층 |
| 3 | 코드 위치 | `codex-rs/core/` (= Codex core). 저장소 전체는 100+ Rust crate |
| 4 | 라이선스 | Apache-2.0 |
| 5 | 개방 계층 | CLI · SDK · App Server 프로토콜 · 관리형 Agents API (4) |
| 6 | 에이전트 루프가 차지하는 비중 | **104 메서드 중 약 20 — 전체의 20%** |

## §2 정의  {#s2-definition}

OpenAI 자신의 표현:

> "A capable agent is more than a prompt and a model response. It needs a way to understand a task,
> maintain context over time, inspect relevant information, call tools, expose progress, handle
> failures, request human approval when necessary, and return a useful result."

`harness engineering` 포스트는 더 날카롭게 말한다 — 고전적 소프트웨어 공학이 **예측 가능한 동작**을
전제하는 반면, 하네스 엔지니어링은 **개발자가 정확한 궤적을 미리 알 수 없는 자율 런타임을 한정하고
관찰하고 통치하는 일**이다. 자세한 운영 원칙은 [[concepts/harness-engineering]].

## §3 하네스 안에 들어가는 것  {#s3-components}

에이전트 루프 자체 말고도 다음이 포함된다.

| # | 구성요소 | 내용 |
|---|---|---|
| 1 | **Thread lifecycle & persistence** | thread 생성·재개·fork·archive, 이벤트 이력 영속화 (클라이언트가 재접속해도 같은 타임라인) |
| 2 | **Config & auth** | 설정 로딩, 기본값 관리, "Sign in with ChatGPT" 등 인증 흐름과 자격증명 상태 |
| 3 | **Tool execution & extensions** | 샌드박스 안에서 shell/file 도구 실행, MCP 서버·skill 을 일관된 정책 모델 아래 루프에 편입 |

**Codex core** 는 이 둘을 겸한다 — 에이전트 코드가 사는 **라이브러리**이자, 하나의 thread 를 돌리고
그 영속성을 관리하도록 띄울 수 있는 **런타임**.

## §4 App Server 의 자리  {#s4-app-server}

```
Clients (Web / TUI / VS Code · JetBrains · Xcode / Desktop / partners)
        │  bidirectional JSON-RPC (JSONL)
Codex App Server (long-lived process)
   ├─ stdio reader
   ├─ Codex message processor   ← 번역 계층
   ├─ thread manager            ← thread 당 core session 하나
   └─ core threads (N Codex core runtimes)
        │
Model (Responses API) · tools · MCP · sandbox
```

- **thread manager** 는 thread 하나당 core session 하나를 띄운다.
- **message processor** 는 클라이언트 JSON-RPC 요청을 core 연산으로 번역하고, core 의 저수준 내부
  이벤트 스트림을 **작고 안정적인 UI-ready 알림 집합**으로 변환한다.
- 프로토콜은 **완전 양방향**이다. 승인이 필요하면 *서버가* 요청을 보내고 turn 을 멈춘다
  ([[concepts/approval-gate]]).

### §4.1 왜 MCP 가 아니라 JSON-RPC 인가  {#s4-1-why-jsonrpc}

| 단계 | 사건 |
|---|---|
| 1 | Codex CLI 는 TUI 로 출발 — 에이전트 루프와 같은 프로세스에서 Rust 타입을 직접 다뤘다 |
| 2 | VS Code 확장을 만들며 같은 하네스를 재사용해야 했고, 단순 request/response 를 넘는 상호작용이 필요해졌다 (워크스페이스 탐색, 추론 진행 스트리밍, diff 방출) |
| 3 | **Codex 를 MCP 서버로 노출하는 실험을 먼저 했다.** VS Code 에 맞게 MCP 의미론을 유지하기가 어려웠다 |
| 4 | 대신 TUI 루프를 그대로 비추는 JSON-RPC 프로토콜을 도입 — 이것이 App Server 의 비공식 1판 |
| 5 | JetBrains · Xcode · Desktop(병렬 에이전트 오케스트레이션)의 요구가 이를 **하위호환 보장을 갖는 플랫폼 표면**으로 밀어올렸다 |

## §5 4계층 개방 구조  {#s5-layers}

| 계층 | 산출물 | 누가 돌리나 | 적합한 용도 |
|---|---|---|---|
| CLI | `codex exec` | 내 머신 / CI | 스크립트, CI 잡, 일회성 배치 |
| SDK | `@openai/codex-sdk`, `openai-codex` | 내 머신 (CLI 를 spawn) | 서버사이드 도구·워크플로우에 임베드 |
| Protocol | `codex app-server` | 내 머신 / 컨테이너 | **에이전트가 곧 제품일 때** |
| Managed | Agents API | **OpenAI 호스팅** | 하네스 운영을 맡기고 싶을 때 |

공식 권고는 App Server 다 — *"Codex App Server will be the first-class integration method we maintain
moving forward."* 선택 기준은 `docs/06-choosing.md`.

## §6 애플리케이션이 쥐는 몫  {#s6-application-owns}

분업의 공식 문장: *"Your application owns product context, business rules, and tools; Codex
app-server provides the agent loop and sandboxed execution."*

| # | 애플리케이션의 몫 |
|---|---|
| 1 | **인터페이스** — 기존 대시보드와 워크플로우를 그대로 유지 |
| 2 | **컨텍스트와 도구** — 애플리케이션 소유 MCP 서비스를 노출 |
| 3 | **운영 경계** — 파일 접근 범위, 승인 지점, 실행 범위, 관측과 로깅 |

프로토콜 차원의 구현체가 `item/tool/call` 이다 — 에이전트가 **호스트 애플리케이션 소유 도구**를
호출하는 통로.

## §7 표면의 크기가 가르치는 것  {#s7-surface-size}

104개 `ClientRequest` 메서드를 제품 요구사항 목록으로 다시 읽으면:

| 티어 | 메서드 수 | 내용 |
|---|---|---|
| Agent core | ~20 | 루프: thread, turn, item, 승인 |
| Capability system | ~25 | skill, plugin, marketplace, app, hook, MCP |
| Host services | ~15 | 파일시스템, PTY, fuzzy search, git |
| Identity & policy | ~20 | 계정, 인증, rate limit, config, permission profile |
| Platform & migration | ~10 | Windows 샌드박스, 외부 에이전트 import, 피드백 |
| Realtime | ~11 (알림) | 음성 세션 |

> **에이전트 루프는 일의 20% 정도다.** 나머지가 실제로 쓸 만한 물건인지를 결정한다.
> 제품급 최소 집합은 core 20 + 약 25 = **약 45개** (`docs/12-product-surface.md` §4).

## §8 다음에 읽을 문서  {#s8-next}

- [[concepts/thread-turn-item]] — 대화 원시형 세 가지
- [[concepts/approval-gate]] — 사람이 끼어드는 지점
- [[concepts/control-plane-execution-plane]] — 하네스와 compute 의 분리
- [[concepts/wire-protocol-boundary]] — 코어 재사용 가능성을 가르는 경계
- 원문: [`docs/01-overview.md`](../../../docs/01-overview.md), [`docs/12-product-surface.md`](../../../docs/12-product-surface.md)
