# 01. Codex Harness 개요

## 1. harness의 정의

OpenAI의 정의(“Codex as a platform” 블로그):

> "A capable agent is more than a prompt and a model response. It needs a way to understand a task,
> maintain context over time, inspect relevant information, call tools, expose progress, handle failures,
> request human approval when necessary, and return a useful result."

즉 **harness = 모델과 과업 사이에 있는 실행 시스템(execution system)**.
채팅 UI가 아니라 이 실행 계층이 제품 가치의 핵심이라는 것이 OpenAI의 주장입니다.

`harness engineering` 글에서는 더 강하게 표현합니다 — 고전 소프트웨어 공학이 *예측 가능한 동작*을 전제한다면,
harness 공학은 *어떤 개발자도 궤적을 미리 알 수 없는 자율 런타임을 경계 짓고(bound), 관측하고(observe),
통치하는(govern)* 일이라는 것.

## 2. harness 안에 들어있는 것

“Unlocking the Codex harness” 블로그 기준, 코어 에이전트 루프 외에 다음이 포함됩니다.

1. **Thread lifecycle & persistence** — thread 생성/재개/포크/아카이브, 이벤트 히스토리 영속화.
   클라이언트가 재접속해도 동일한 타임라인을 렌더링할 수 있음.
2. **Config & auth** — 설정 로딩, 기본값 관리, "Sign in with ChatGPT" 등 인증 플로우와 자격증명 상태.
3. **Tool execution & extensions** — 샌드박스 안에서의 shell/file 도구 실행, MCP 서버·skills 연결을
   일관된 정책 모델 아래에서 에이전트 루프에 편입.

이 모든 에이전트 로직은 Codex CLI 코드베이스의 **Codex core**에 있습니다.
Codex core는 (a) 에이전트 코드가 모여 있는 **라이브러리**이자 (b) 하나의 thread를 실행/영속화하는 **런타임**입니다.

## 3. App Server의 위치

```
┌──────────────────────────────────────────────────────────┐
│  Clients: Web app / CLI(TUI) / VS Code·JetBrains·Xcode /  │
│           macOS Desktop / 파트너 제품                      │
└───────────────────────────┬──────────────────────────────┘
                            │  bidirectional JSON-RPC (JSONL)
┌───────────────────────────▼──────────────────────────────┐
│  Codex App Server (long-lived process)                   │
│   ├─ stdio reader                                        │
│   ├─ Codex message processor   ← 번역 계층                │
│   ├─ thread manager            ← thread마다 core session  │
│   └─ core threads (Codex core 런타임 N개)                 │
└───────────────────────────┬──────────────────────────────┘
                            │
                     Model (Responses API) · tools · MCP · sandbox
```

- **thread manager**가 thread마다 core session을 하나씩 띄움.
- **message processor**가 클라이언트 JSON-RPC 요청 → Codex core 오퍼레이션으로 번역하고,
  core의 저수준 내부 이벤트 스트림 → **작고 안정적인 UI-ready JSON-RPC 알림 집합**으로 변환.
- 프로토콜은 **완전 양방향**. 승인이 필요하면 *서버가* 요청을 보내고 클라이언트 응답까지 턴을 일시정지.

### 기원 (왜 MCP가 아니라 JSON-RPC인가)

- Codex CLI는 원래 TUI였고 에이전트 루프와 같은 프로세스에서 Rust 타입을 직접 다뤘음.
- VS Code 확장을 만들면서 같은 harness를 재사용해야 했음 → 워크스페이스 탐색, 추론 진행 스트리밍, diff 방출 등
  단순 request/response를 넘는 상호작용이 필요.
- **처음엔 Codex를 MCP 서버로 노출해봤으나**, VS Code에 맞게 MCP 시맨틱을 유지하는 것이 어려웠음.
- 대신 TUI 루프를 그대로 반영한 JSON-RPC 프로토콜을 도입 → 이것이 App Server의 비공식 1차 버전.
- 이후 JetBrains·Xcode·Desktop(병렬 에이전트 오케스트레이션) 수요로 **하위 호환을 보장하는 플랫폼 표면**으로 재설계.

## 4. 3-Layer 개방 구조

| 레이어 | 산출물 | 실행 주체 | 적합한 상황 |
|---|---|---|---|
| CLI | `codex exec` | 사용자 머신/CI | 스크립트, CI 잡, 일회성 배치 |
| SDK | `@openai/codex-sdk`, `openai-codex` | 사용자 머신 (CLI를 spawn) | 서버사이드 도구/워크플로에 임베드 |
| 프로토콜 | `codex app-server` | 사용자 머신/컨테이너 | 에이전트가 **제품 그 자체**일 때 |
| 관리형 | Agents API | **OpenAI 호스팅** | 하네스 운영을 맡기고 싶을 때 |

공식 문구:
- "For a script, CI job, or one-off background task, `codex exec` can run a bounded agent workflow and return structured output."
- "The official Codex SDK provides a direct programmatic interface."
- "Use Codex app-server when the agent is part of the product itself."
- "Your application owns product context, business rules, and tools; Codex app-server provides the agent loop and sandboxed execution."

## 5. 애플리케이션이 통제하는 것

1. **Interface** — 기존 대시보드/워크플로를 그대로 유지.
2. **Context & tools** — 애플리케이션이 소유한 MCP 서비스 노출.
3. **Operational boundaries** — 파일 접근 범위, 승인 요구 지점, 실행 범위, 관측/로깅.

레퍼런스 예제로 **Relay**(배송 운영 대시보드)가 제시됨: 대시보드 옆에 에이전트를 임베드,
데이터 조회는 앱이 소유한 MCP 도구로, 결과에 영향을 주는 행동 전에는 사람 승인, 도구가 데이터를
바꾸면 대시보드 갱신은 앱이 책임.

## 6. 레퍼런스 도입 사례 (공식 언급)

- **GitHub, JetBrains** — 기존 IDE 워크플로에 Codex 편입
- **Cisco** — Cisco Cloud Control 내 App Builder에서 Codex SDK 사용
- **Thrive Holdings + Crete** — 세무 신고 워크플로. 파일럿에서 7,000건 처리, 준비 시간 약 1/3 단축

## 7. 코드베이스 규모 감

`openai/codex` 리포지터리의 `codex-rs/`는 100개가 넘는 Rust 크레이트로 구성됩니다. harness 관련 주요 크레이트:

```
codex-rs/
├── core/                      # Codex core: 에이전트 루프 본체
├── app-server/                # App Server 프로세스
├── app-server-protocol/       # 프로토콜 타입 + 생성된 JSON Schema / TS 정의
├── app-server-client/         # 클라이언트 구현
├── app-server-transport/      # stdio / WebSocket / UDS 전송
├── app-server-daemon/
├── exec/  exec-server/  exec-server-protocol/   # 비대화형 · 셀프호스팅 실행기
├── codex-mcp/  rmcp-client/   # MCP 서버/클라이언트
├── sandboxing/  linux-sandbox/  windows-sandbox-rs/  mxc-sandbox/  bwrap/
├── skills/  plugin/  hooks/  memories/  connectors/
├── agent-roles/  agent-identity/  agent-graph-store/   # 서브에이전트/멀티에이전트
├── rollout/  thread-store/  history/  state/           # 영속화
├── otel/  analytics/  diagnostics/                     # 관측
└── tui/  cloud-tasks/  realtime-webrtc/  voice-host/
```

라이선스: **Apache-2.0**.
