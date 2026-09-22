---
type: concept
status: active
last_ingested_from: docs/02-app-server-protocol.md + docs/06-choosing.md + docs/05-agents-api.md
related_pages: [concepts/thread-turn-item, concepts/harness, concepts/os-sandbox-policy, concepts/execution-environment-topology]
created: 2026-09-22
updated: 2026-09-22
---

# Approval Gate — 승인을 프로토콜 원시형으로 만들기

- 문서 목적: 사람의 개입이 UI 편의가 아니라 **프로토콜 차원의 안전 기전**으로 설계된 방식을 정리한다.
- 범위: 서버→클라이언트 요청 10종, 승인 결정 어휘, 관리형 API 의 대응물, 구현 의무
- 1차 출처: `ServerRequest.ts` 생성 스키마, `ReviewDecision` 타입군
- 최종 수정일: 2026-09-22

## §1 TL;DR  {#s1-tldr}

| # | 항목 | 값 |
|---|---|---|
| 1 | 방향 | **서버 → 클라이언트**. 프로토콜이 양방향인 이유가 이것이다 |
| 2 | 효과 | 클라이언트가 응답할 때까지 **turn 이 멈춘다** |
| 3 | 요청 수 | 10종 |
| 4 | 구현 의무 | 승인 3종을 구현하지 않으면 **turn 이 그대로 정지한다** |
| 5 | 관리형 API 대응물 | `requires_action` + `required_actions[]` |

## §2 서버 → 클라이언트 요청 10종  {#s2-server-requests}

| 메서드 | 목적 |
|---|---|
| `item/commandExecution/requestApproval` | 명령 실행 승인 |
| `item/fileChange/requestApproval` | 파일 변경 승인 |
| `item/permissions/requestApproval` | 권한 상승 승인 |
| `item/tool/requestUserInput` | 도구가 사용자 입력을 요구 |
| `item/tool/call` | **동적 도구 호출을 클라이언트에 위임** (`DynamicToolCallParams`) |
| `mcpServer/elicitation/request` | MCP elicitation |
| `account/chatgptAuthTokens/refresh` | ChatGPT 토큰 갱신 요청 |
| `attestation/generate` | 상위 `x-oai-attestation` 생성 (capability opt-in 필요) |
| `applyPatchApproval` | (legacy) 패치 적용 승인 |
| `execCommandApproval` | (legacy) 명령 실행 승인 |

`item/tool/call` 은 승인이 아니라 **분업의 프로토콜 구현체**다 — 에이전트가 호스트 애플리케이션이
소유한 도구를 호출하는 통로. [[concepts/harness]] §6 참조.

## §3 승인 결정 어휘  {#s3-decisions}

`ReviewDecision` 계열: `accept`, `acceptForSession`, `decline`, `cancel`, 그리고 수정 사항을 실어
보내는 변형(`acceptWithExecpolicyAmendment` 등 — `ExecPolicyAmendment`, `NetworkPolicyAmendment`).

> 승인은 단순 yes/no 가 아니라 **정책 수정을 동반할 수 있다**. "이번엔 허용하되 네트워크 정책은
> 이렇게 고쳐라"가 하나의 응답으로 표현된다.

## §4 다른 경로로 해소된 승인  {#s4-resolved-elsewhere}

`serverRequest/resolved` 알림은 승인 요청이 **다른 곳에서 결정됐음**을 알린다 — 다른 클라이언트,
혹은 자동 승인. UI 는 이걸 받아 자기 화면의 승인 대기를 정리해야 한다.

자동 승인 경로: `item/autoApprovalReview/started` · `completed`,
`autoApprovalReview/strictReviewRequired`.

> 자동 승인을 켠다면 **엄격 검토로 에스컬레이션되는 조건**을 반드시 이해하고 켠다.

## §5 관리형 Agents API 의 대응물  {#s5-agents-api}

App Server 의 서버→클라이언트 요청에 해당하는 것이 세션의 `requires_action` 상태다.

| action 종류 | 처리 방법 |
|---|---|
| **function call** | 지정된 함수를 실행하고 `turn_id` + `call_id` 를 복사해 결과를 반환 |
| **environment connection** | `environment_id` 로 연결을 수립 ([[concepts/execution-environment-topology]]) |

핵심 구분:

> **`required_actions` 로 판단한다.** 세션 이력에 `function_call` item 이 있다는 사실만으로는
> 결과가 대기 중임이 성립하지 않는다.

부작용이 있는 함수는 **session · turn · call ID 기준으로 결과를 내구 저장**한다. 실행은 성공했는데
결과를 저장하지 못했을 수 있으면, 다시 실행하기 전에 결과를 먼저 확인한다.

## §6 구현 의무와 함정  {#s6-obligations}

| # | 항목 |
|---|---|
| 1 | 승인 3종(`commandExecution` / `fileChange` / `permissions`)은 **필수** — 없으면 turn 이 멈춘 채 끝나지 않는다 |
| 2 | `serverRequest/resolved` 를 처리해 다른 경로로 해소된 요청을 정리한다 |
| 3 | 승인 게이트는 **UI 편의가 아니라 프로토콜 차원의 안전 기전**이다 |
| 4 | 신뢰할 수 없는 콘텐츠와 사용자 입력을 **타입 수준에서 분리**한다 — Python SDK 의 `ExternalMessage` 가 모델이다 (도구 수준 권한은 유지하되 사용자 권한은 부여하지 않음) |
| 5 | 관리형 API 는 `requires_action` 이면 **모든 required action 이 처리되기 전까지 아무것도 진행되지 않는다** |

## §7 다음에 읽을 문서  {#s7-next}

- [[concepts/thread-turn-item]] — 승인이 멈추는 대상인 turn
- [[concepts/os-sandbox-policy]] — 승인이 없어도 되게 만드는 쪽의 방어
- [[concepts/execution-environment-topology]] — environment connection action 의 맥락
- 원문: [`docs/02-app-server-protocol.md`](../../../docs/02-app-server-protocol.md) §7, [`docs/06-choosing.md`](../../../docs/06-choosing.md) §5
