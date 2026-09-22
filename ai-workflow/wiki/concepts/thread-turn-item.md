---
type: concept
status: active
last_ingested_from: docs/02-app-server-protocol.md
related_pages: [concepts/harness, concepts/approval-gate, concepts/stateless-conversation-wire]
created: 2026-09-22
updated: 2026-09-22
---

# Thread / Turn / Item — 대화 원시형

- 문서 목적: 에이전트 루프를 API 로 표현하기 위해 Codex 가 고른 세 가지 원시형과 각각의 생명주기를 정리한다.
- 범위: 세 원시형의 경계, item 생명주기, thread 언로드·축출, turn 파라미터의 sticky 의미론
- 1차 출처: `codex-rs/app-server-protocol/schema/` 생성 스키마, `config_toml.rs`
- 최종 수정일: 2026-09-22

## §1 TL;DR  {#s1-tldr}

| # | 원시형 | 정의 | 핵심 성질 |
|---|---|---|---|
| 1 | **Item** | 입출력의 원자 단위 | 생명주기가 **명시적**: `started → delta(0..N) → completed` |
| 2 | **Turn** | 사용자 입력 하나가 시작시킨 에이전트 작업 단위 | **중단과 롤백의 단위**. item 의 열 |
| 3 | **Thread** | 대화의 영속 컨테이너 | 생성·재개·fork·archive. 이력 영속화 |

설계 이유: 사용자↔에이전트 상호작용은 단순 request/response 가 아니라 **요청 하나가 구조화된 행동의
열로 펼쳐지는** 형태이기 때문이다.

## §2 Item 생명주기  {#s2-item-lifecycle}

```
item/started  →  item/*/delta (0..N)  →  item/completed
```

클라이언트는 `started` 에서 즉시 렌더하고, `delta` 로 증분을 적용하고, `completed` 의 종단 payload 로
확정한다. **이것이 프로토콜이 소비되도록 의도된 방식**이다.

### §2.1 `ThreadItem` 의 type 값  {#s2-1-item-types}

| type | 주요 필드 |
|---|---|
| `userMessage` | `content: UserInput[]`, `clientId` |
| `hookPrompt` | `fragments` |
| `agentMessage` | `text`, `phase`, `memoryCitation`, `delivery`, `questions` |
| `reasoning` | `summary[]`, `content[]` |
| `plan` | `text` |
| `commandExecution` | `command`, `cwd`, `processId`, `source`, `status`, `commandActions[]`, `aggregatedOutput`, `exitCode`, `durationMs`, `pluginId`, `scriptPath` |
| `fileChange` | `changes: FileUpdateChange[]`, `status` |
| `mcpToolCall` | `server`, `tool`, `status`, `arguments`, `appContext`, `readOnlyHint`, `result`, `error`, `durationMs` |
| `dynamicToolCall` | `namespace`, `tool`, `arguments`, `status`, `contentItems`, `success`, `durationMs` |
| `functionCallOutput` | `name`, `namespace`, `output` |
| `collabAgentToolCall` | `tool`, `status`, `senderThreadId`, `receiverThreadIds[]`, `prompt`, `model`, `reasoningEffort`, `agentsStates` |
| `subAgentActivity` | `kind`, `agentThreadId`, `agentPath` |
| `webSearch` / `imageView` / `imageGeneration` / `sleep` | 전용 payload |
| `enteredReviewMode` / `exitedReviewMode` | `review` |
| `contextCompaction` | — |

> `commandExecution.commandActions` 는 **여러 명령이 파이프로 엮였을 수 있는 셸 명령의 best-effort
> 파싱**이다. UI 에서 "이 명령이 무엇을 할 것인가"를 설명하는 데 쓴다.

## §3 Thread 언로드와 축출 — 서로 다른 두 기전  {#s3-unload-evict}

| 기전 | 트리거 | 설정 |
|---|---|---|
| **시간 기반 언로드** | 구독자 없음 **그리고** 활동 없음 | `thread_unload_delay_secs`, **기본값 60초** |
| **용량 기반 축출** | 로드된 thread 수가 상한 초과 | `V2Residency` 의 LRU `VecDeque<ThreadId>`, `effective_agent_max_threads` |

언로드 목표 시각은 `max(has_no_subscribers_since, is_inactive_since) + delay` 다. 활동이나 새 구독자가
생기면 리셋된다. 0 은 즉시 언로드이고, 변경은 서버 재시작을 요한다.

> ⚠️ **[정정된 2차 출처]** 30분 idle 언로드를 말하는 2차 출처가 있으나 **틀렸다**. 기본값은 60초이고,
> 조건도 하나가 아니라 둘의 동시 충족이다. 검증 기록은 [[concepts/primary-source-verification]].

## §4 Turn 파라미터의 sticky 의미론  {#s4-sticky}

`turn/start` 의 override 대부분은 **이번 turn 만이 아니라 이후 turn 에도 남는다**.

| 범위 | 필드 |
|---|---|
| **sticky** (이후 turn 에도 적용) | `cwd`, `approvalPolicy`, `approvalsReviewer`, `sandboxPolicy`, `model`, `serviceTier`, `effort`, `summary`, `personality` |
| **이번 turn 한정** | `serviceTierForTurn`, `outputSchema` |

> 한 turn 만 바꾸려면 명시적으로 범위가 정해진 필드를 쓰거나, 다음 turn 에서 되돌려야 한다.
> 이것이 통합 시 가장 흔한 함정 중 하나다.

## §5 전형적인 turn 한 번  {#s5-typical-turn}

```
client → initialize                        server → result
client → initialized (notification)
client → thread/start                      server → thread/started
client → turn/start                        server → turn/started
                                           server → item/started (userMessage) → completed
                                           server → item/started (reasoning)
                                           server → item/reasoning/summaryTextDelta ×N
                                           server → item/started (commandExecution)
   ◀── server REQUEST: item/commandExecution/requestApproval
   ──▶ client RESPONSE: { decision: "accept" }
                                           server → item/commandExecution/outputDelta ×N
                                           server → item/completed (commandExecution)
                                           server → item/started (agentMessage)
                                           server → item/agentMessage/delta ×N
                                           server → item/completed (agentMessage)
                                           server → turn/completed { turn: { status, usage } }
```

실제 JSON 을 보려면: `codex debug app-server send-message-v2 "run tests and summarize failures"`

## §6 legacy: protocol_v1 의 turn 은 다른 것이다  {#s6-protocol-v1}

App Server 아래에 있는(그리고 먼저 있었던) **SQ/EQ 모델**에서 `Turn` 은 **모델 요청 한 사이클**을
뜻한다 — App Server 의 turn 과 **다른 개념**이다. 같은 단어가 두 계층에서 다른 것을 가리키므로
문서를 읽을 때 계층을 먼저 확인해야 한다.

| 항목 | protocol_v1 |
|---|---|
| 통신 | Submission Queue (SQ) / Event Queue (EQ) 쌍 |
| 제출 payload | `Op::ConfigureSession`, `Op::UserTurn`, `Op::Interrupt`, `Op::ExecApproval`, `Op::UserInputAnswer` |
| 동시성 | `Session` 은 한 번에 `Task` 하나. 병렬 작업은 **작업 흐름당 Codex 인스턴스 하나** |
| 호환 | `EventMsg::TurnStarted`/`TurnComplete` 가 `task_started`/`task_complete` 로 직렬화 |

> 신규 통합은 **protocol_v1 이 아니라 App Server 프로토콜**을 쓴다.

## §7 다음에 읽을 문서  {#s7-next}

- [[concepts/approval-gate]] — turn 을 멈추는 서버→클라이언트 요청
- [[concepts/stateless-conversation-wire]] — 이 대화가 모델에게 전달되는 방식
- [[concepts/harness]] — 전체 그림
- 원문: [`docs/02-app-server-protocol.md`](../../../docs/02-app-server-protocol.md)
