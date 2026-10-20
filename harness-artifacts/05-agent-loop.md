# 05. 에이전트 대화 루프 — 레퍼런스 하네스들이 한 턴을 도는 방식

> **무엇인가.** 사용자 입력이 들어온 뒤 모델 요청 → 스트리밍 → 도구 호출 → 재요청 → 종료까지, 각 레퍼런스가 **루프를 어떻게 짜고 무엇으로 끝내는지**를 소스와 분리 번들에서 읽어 비교한 기록이다. 단위(스레드/턴/항목인지, 메시지/파트인지), 한 사이클의 단계, 계속 조건과 종료 사유, 진행 중 입력(조종)과 큐, 압축이 끼어드는 자리, 서브에이전트 생성, 재시도와 루프 탐지, 승인이 루프를 멈추는 지점, 영속화 단위를 다룬다. 2026-10-20, TASK-2026-10-20-main-004.
>
> **읽은 것.** Codex `openai/codex` `origin/main` `79a19cbb3`(루프 코드는 `1a35bc4cc` 까지 변화 없음) 의 `core/src/session/{turn,turn_input,input_queue}.rs`·`ext/queue`·`agent/control/spawn.rs`·`protocol/src/protocol.rs`; Claude Code CLI **2.1.304** 분리 번들의 쿼리 루프 모듈 `chunk-gzc5bc6y.js` 와 Agent SDK **0.3.304** `sdk.d.ts`; opencode **1.17.12** 분리 번들의 `chunk-f6y47634.js`(SessionPrompt/SessionProcessor/SessionCompaction/SessionStatus); Gemini CLI `main`(2026-10-20) `packages/core/src/core/{client,turn,geminiChat}.ts`·`services/loopDetectionService.ts`·`utils/nextSpeakerChecker.ts`·`scheduler/scheduler.ts`·`packages/cli/src/nonInteractiveCli.ts`; Strands 는 [`strands/02`](../strands/02-agent-loop.md) 의 기존 독해를 요약만 한다. **어느 것도 실행하지 않았다.** 등급: ✅ 소스/번들에서 직접 읽음 · 📣 문서 진술 · ⚠️ 미독/정적 판정 불가 · 추정 은 표시.
>
> 관련: 와이어 단위는 [`docs/02`](../docs/02-app-server-protocol.md) §4–5 와 [`claude-code/01`](../claude-code/01-wire-protocol.md) §3, 세션·압축 수치는 [`claude-code/03`](../claude-code/03-sessions-context-and-clients.md) §2, 도구 호출 메커니즘은 [03](03-tool-use-patterns.md), 위키 [`thread-turn-item`](../ai-workflow/wiki/concepts/thread-turn-item.md).

## 0. 한눈에

| 축 | Codex | Claude Code | opencode | Gemini CLI | Strands |
|---|---|---|---|---|---|
| **단위** | Thread / Turn / Item(와이어), 내부는 `Op` 31종 → `EventMsg` 84종 | 스레드 없음: `session_id` + `SDKMessage` 스트림, `result` 가 턴을 닫음 | Session / Message(`parentID`) / Part(step-start·text·reasoning·tool·step-finish) | `Content[]` 히스토리 + 요청당 `Turn` 객체, `GeminiEventType` 18종 | `messages[]` + 호출(invocation); "turn" = 모델 호출 1회 |
| **한 사이클** | 보류 입력 흡수 → 훅 → 월드스테이트 → 프롬프트 → 샘플링(스트림) → 도구 future → 사후 판정 | 메시지 준비 → API 호출 → 도구 drain → 종료 사유 분류 → 재귀 | 마지막 user 메시지 → (압축 메시지/오버플로 처리) → 에이전트·스텝 확인 → `streamText` → 파트 갱신 → `compact\|stop\|continue` | 압축/오버플로 가드 → 루프 탐지 → `turn.run` 스트림 → (도구 없음이면) 다음 화자 판정 → CLI 가 스케줄러로 도구 실행 → 재귀 | 한도 검사 → 모델 호출 → `tool_use` 면 도구 실행 → 재귀 |
| **계속 조건** | `needs_follow_up = 모델이 도구를 불렀다 ‖ 보류 입력이 있다` — **스텝 상한 없음** | `stop_reason==="tool_use"` 등 → `next_turn`; `maxTurns`(API 왕복 수)·`maxBudgetUsd` | 스텝 결과 `"continue"`; 에이전트별 `steps`(기본 ∞) 초과 시 텍스트 전용 유도 | `pendingToolCalls` 가 있으면 CLI 가 재호출; 없으면 LLM 에게 다음 화자를 묻고 `model` 이면 "Please continue."; `MAX_TURNS = 100` 재귀 상한 + `maxSessionTurns` | `stop_reason == tool_use`; `turns`/토큰 한도 |
| **종료 어휘** | `TurnComplete` / `TurnAborted` / `Error`(`codexErrorInfo` 개방 집합) | 내부 26 종(`completed`, `max_turns`, `hook_stopped`, `tool_deferred`, `background_requested`, `rapid_refill_breaker`, `refusal_retry` …) → 와이어 `result.subtype` 5종 + `stop_reason` | `session.status` `idle\|busy\|retry{attempt,next}`, `session.idle`, `session.error`, 메시지 `finish` | `Finished(finishReason)`, `MaxSessionTurns`, `LoopDetected`, `ContextWindowWillOverflow`, `UserCancelled`, `Error` | Python 12 / TS 15+ 개 `stop_reason` |
| **조종(진행 중 입력)** | `TurnInputMode::{StartOrSteer, StartIfIdle, ContinueIfIdle, Steer{expected_turn_id}}`; 보류 입력은 **샘플링 사이**에 흡수, `preempt` 로 진행 중 샘플링 취소 가능; 별도 `thread/queue/*` 는 **다음 턴** 큐(10 s 디스패처) | uuid 가 붙은 **비동기 사용자 메시지 큐**(`priority: now\|next\|later`), `cancel_async_message`, `interrupt` 영수증 `still_queued`(+`cancel_queued`), 도구 배치 사이에 폴 이벤트 흡수(`absorbed_mid_turn`) | UI 설정 `followup: steer\|queue`, 서버는 `assertNotBusy`(`RunnerBusy`) 가드; 조종 경로 세부 ⚠️ | 비대화형 경로에는 없음; 대화형 `useGeminiStream` 미독 ⚠️ | 없음(취소만) |
| **압축** | 샘플링 **사이**에 `MidTurn`/`PostTurn` 자동 압축, 비동기 후보, `token_limit_reached`, Guardian 예산 초과 시 1회 | 임계 도달 시 자동, `compact_boundary` 시스템 메시지, "prompt too long" 뒤 압축 재시도, 과열 차단기(`autocompact_thrashing`) | 오버플로 시 **압축 메시지**를 대화에 넣고 처리, `prune`, `preserve_recent_tokens`/`reserved`; 압축해도 넘치면 stop | 전송 **전** `tryCompressChat`(실패-팽창 플래그), 전송 전 `remainingTokenCount` 가드 → `ContextWindowWillOverflow` | 매 사이클 뒤 슬라이딩 윈도 |
| **루프 탐지** | 명시적 없음 ⚠️(mailbox 선점·Stop 훅만) | 사고만 반복 시 넛지 1회, 깨진 tool_use 재시도 1회, Stop 훅 차단 상한 8 | 동일 도구+입력 **3회** 연속 → `doom_loop` 권한 질문 | 동일 도구 호출 5회 / 50자 청크 10회 반복 / 30턴 이후 LLM 판정(간격 5–15, 신뢰도 0.9, 더블체크 모델) → 1회 복구 후 종료 | 없음 |
| **서브에이전트** | `spawn_agent` 포크: 부모 롤아웃 스냅샷 + 기준선 보존 규칙, 메일박스로 결과 전달 | `Agent`/`Task` 도구 → 사이드체인(`isSidechain`, `parent_tool_use_id`), `task_started`/`task_notification`, `SubagentStop` 훅 | `task` 도구(`subagent_type`) → 자식 세션(`parentSessionID`), 배경 실행 플래그 | 에이전트 프레임워크 이벤트(`AgentExecutionStopped/Blocked`) ⚠️ 미독 | 스윔·그래프 도구(별도) |
| **재시도** | 스트림 5(상한 100)·요청 4, 200 ms × 2ⁿ ±10 % | API 재시도 + 모델 폴백, 거절 재시도/폴백 대화 | 공급자별 정책, `retry{attempt, next}` 상태로 노출 | `maxAttempts 4`(1+3 mid-stream), 1 s 초기, 429 → 폴백 모델 | 훅 전략(스로틀 재시도) |
| **영속화** | 롤아웃(`RolloutItem::{TurnContext, WorldState, Compacted…}`) + 스레드 스토어 | 세션별 JSONL 트랜스크립트(`compact_boundary` 포함) | 메시지·파트 저장소 + 스텝별 스냅샷/`revert` | `ChatRecordingService` 대화 파일; 압축 시 새 chat 으로 재시작 | 호출자 소유 `messages` |

> 📌 **한 줄.** 다섯 하네스 모두 원자는 "모델 호출 한 번 + 그 결과의 도구 실행"이지만, **"계속할지"를 누가 정하는가**가 갈린다. Codex 는 *모델이 도구를 불렀는가 + 사용자가 끼어들었는가*(상한 없음), Claude Code 는 *stop_reason + 훅 + 턴 상한*, opencode 는 *스텝 결과 세 값 + 에이전트별 스텝 상한*, Gemini 는 *도구 유무 + LLM 에게 "다음 화자가 누구냐"고 되묻는 판정 + 재귀 상한 100*, Strands 는 *stop_reason + 호출자 한도*. 압축과 조종이 **루프의 분기**로 들어와 있는지(Codex·Claude·opencode) 아니면 **전송 전 전처리**인지(Gemini) 도 설계 차이다.

## 1. Codex — `needs_follow_up` 하나로 도는 루프 ✅

### 1.1 단위와 입구

와이어 단위는 [`docs/02`](../docs/02-app-server-protocol.md) §4 의 Thread / Turn / Item 이고, 엔진 안에서는 `Op`(클라이언트→코어 제출, 31 변종: `TurnInput`, `Interrupt`, `InterruptIfNoPendingInput`, `ExecApproval`, `PatchApproval`, `ResolveElicitation`, `UserInputAnswer`, `RequestPermissionsResponse`, `DynamicToolResponse`, `Compact`, `Review`, `InterAgentCommunication`, `RecoverTurn`, `SuspendTurnAndShutdown`, `Shutdown`, `RunUserShellCommand`, 실시간 대화 8종 …)과 `EventMsg`(코어→클라이언트, 84 변종: `TurnStarted`/`TurnComplete`/`TurnAborted`, `AgentMessage`, `AgentReasoning*`, `ExecCommandBegin/OutputDelta/End`, `McpToolCallBegin/End`, `ExecApprovalRequest`, `RequestPermissions`, `RequestUserInput`, `ContextCompacted`, `ThreadRolledBack`, `ThreadQueueChanged`, `TokenCount` …)가 `protocol/src/protocol.rs` 에 있다.

입력이 턴을 **시작**하는지 **조종**하는지는 `TurnInputMode` 가 정한다(`protocol/src/turn_input.rs`, 처리 `core/src/session/turn_input.rs`): `StartOrSteer`("Start a regular turn when idle, otherwise steer the active regular turn"), `StartIfIdle`, `ContinueIfIdle`(내부 연속; 기대한 직전 턴 이후 다른 작업이 시작됐으면 거부), `Steer { expected_turn_id }`. 조종이 성공하면 영속 설정만 적용된다("Persistent thread settings apply on Started and Steered"). 별도로 app-server 의 `thread/queue/add`(`ext/queue/src/service.rs`)는 **다음 턴에 시작할 사용자 메시지**의 큐다: `QueuedItemService` 가 10초 간격으로 스레드별 디스패치 락을 잡고 비어 있는 스레드에 큐 항목을 흘려보낸다("dispatch tasks keep a blocked or failed thread from starving other queues"). 즉 "끼어들기"(steer)와 "줄서기"(queue)가 서로 다른 메커니즘이다.

### 1.2 한 턴 — `run_turn` 의 `loop`

`core/src/session/turn.rs` `run_turn` 은 다음을 반복한다.

1. **보류 입력 흡수** — `can_drain_pending_input` 이면 `input_queue.get_pending_input(active_turn)` 으로 조종 입력을 꺼낸다. 턴 시작 직후와 자동 압축 직후에는 미룬다("so the fresh turn input … gets sampled first").
2. **훅과 기록** — `run_hooks_and_record_inputs(… PersistContext::SteeredUserInput)` 가 입력을 롤아웃에 적고 훅을 돌린다; 훅이 턴을 막으면 `break`.
3. **스텝 컨텍스트 캡처** — "context, advertised tools, and tool calls share one request view"; 보류 입력이 있으면 필요한 MCP 서버까지 다시 잡는다.
4. **월드스테이트 → 프롬프트** — `build_world_state_for_step`(증분 도구 카탈로그·모델 지시문·환경·토큰 예산 섹션, [`docs/16`](../docs/16-responses-chat-adapter.md) §10.3) → `build_prompt`.
5. **샘플링** — `run_sampling_request`: `stream_max_retries`(기본 5, 상한 100; 요청 재시도 기본 4; `backoff(n) = 200 ms × 2^(n−1) × U(0.9,1.1)`) 안에서 `try_run_sampling_request` 를 돈다. 스트림 이벤트는 `ResponseEvent` 17종(`Created`, `OutputItemAdded/Done`, `OutputTextDelta`, `ReasoningSummaryDelta/Done`, `ToolCallInputDelta`, `Completed`, `RateLimits`, `ServerModel`, `TurnModerationMetadata` …). `OutputItemDone` 마다 `handle_output_item_done` 이 도구 future 를 `in_flight` 에 넣고 **`needs_follow_up |= 출력이 후속을 요구했는가`**(도구 호출이 있었는가)를 누적한다. 진행 중 사용자 입력을 `watch_user_input` 이 감지하면 `preempt` 토큰으로 스트림을 끊고(Responses Lite 는 `ResponseInterrupt::Drain`) `needs_follow_up = true` 로 돌아온다; 메일박스(다른 에이전트의 메시지)가 오면 `codex.mailbox_preemption` 으로 선점한다(`DeferMailboxPreemption` 플래그로 미룰 수 있음).
6. **사후 판정** — `needs_follow_up = model_needs_follow_up || has_pending_input`; 토큰 상태를 재고 `async_compaction::maybe_start`(후속이 있으면 `MidTurn`, 없으면 `PostTurn`)를 건다. `should_roll_over = 자동 압축 on && needs_follow_up && (새 창 요청 || token_limit_reached || 비동기 후보 준비됨)` 이면 `run_auto_compact(ContextLimit, MidTurn)` 후 `continue`.
7. **종료 분기** — `!needs_follow_up` 이면 **Stop 훅**(`run_turn_stop_hooks`): `should_block` 이면 훅의 프롬프트를 사용자 메시지로 기록하고 `stop_hook_active = true` 로 **계속**(프롬프트 없이 막으면 경고 후 무시), `should_stop` 이면 `break`; 레거시 after-agent 훅; `model_post_turn_compact_threshold_percent > 0` 이고 보류 입력이 없으면 턴 끝 압축(`PostTurn`); `break`. 후속이 있으면 `continue`.
8. **오류 분기** — `ContextWindowExceeded` + Guardian 예산 소진 상태면 압축 1회 후 재시도(`guardian_budget_compacted`), `TurnAborted` 는 그대로 전파, 잘못된 이미지는 사용자용 오류로 끝, 그 외는 `Error` 이벤트와 함께 `break`.

**스텝 상한이 없다.** `max_steps` 류 상수는 `core/src`·`config/src` 어디에도 없다(grep 0건). 턴은 모델이 더 이상 도구를 부르지 않고 사용자가 끼어들지 않을 때, 또는 인터럽트·오류로만 끝난다. 반복 방어는 훅·승인·Guardian·토큰 예산 쪽에 있다.

### 1.3 조종과 메일박스

`InputQueue`(`session/input_queue.rs`)는 턴 단위 `pending_input` 과 세션 단위 **메일박스**(에이전트 간 메시지)를 함께 관리하며 활동 종류를 `InputQueueActivity::{Mailbox, Steer}` 로 방송한다. 조종 입력은 `extend_pending_input_and_accept_mailbox_delivery_for_turn_state` 로 들어가 `Steer` 가 되고, 턴이 메일박스 전달을 받아들이는 상태일 때만 `get_pending_input` 이 꺼낸다. `Op::InterruptIfNoPendingInput` 은 "조종할 게 없을 때만 중단"이라는 클라이언트 의도를 그대로 실어 나른다.

### 1.4 서브에이전트

`agent/control/spawn.rs`: `spawn_agent` 는 **포크**이면 부모 롤아웃을 스냅샷해 자식 히스토리로 삼는다("Flush before snapshotting store history for a fork"). 마지막 `Compacted` 체크포인트에 `replacement_history` 가 없으면(레거시) `preserve_context_baselines = false` 로 자식이 컨텍스트를 다시 짓고, V2 에서는 `multi_agent_v2.preserve_fork_prefix` 가 켜져 있고 기준선이 보존될 때만 포크 접두사를 유지한다. 상속 시 개발자 메시지에서 `BaseInstructionsFragment`·`IncrementalToolsHint` 는 기준선 보존 여부에 따라 남기거나 뺀다. 한도: `MAX_SPAWN_AGENT_MODEL_OVERRIDES = 5`, `MAX_ROOT_MESSAGES = 16`(사용자 승인 메시지), 종료 실패 보존 64. 자식의 결과는 메일박스로 부모 턴에 전달돼 §1.2 의 선점/후속 경로를 탄다. `Op::InterAgentCommunication` 이 그 와이어다.

### 1.5 영속화

롤아웃 항목은 `TurnContext`, `WorldState`(섹션 스냅샷), `Compacted`, 응답 항목이며 스레드 스토어가 재개·포크·되감기(`ThreadRolledBack`)를 지탱한다. 클라이언트는 `item/*` 알림으로 같은 흐름을 본다([`docs/02`](../docs/02-app-server-protocol.md) §5).

## 2. Claude Code — 재귀 제너레이터와 26 가지 종료 사유 ✅

### 2.1 단위

Thread/Turn/Item 이 없다([`claude-code/01`](../claude-code/01-wire-protocol.md) §3): 메시지가 곧 항목이고, `result` 메시지가 턴을 닫으며(`subtype: success | error_during_execution | error_max_turns | error_max_budget_usd | error_max_structured_output_retries`, `num_turns`, `stop_reason`, `duration_api_ms`, `total_cost_usd`, `permission_denials`, `usage` — "MAIN AGENT LOOP ONLY"), `session_id` 가 스레드다. SDK 옵션 `maxTurns` 는 "Maximum number of agentic turns (API round-trips) before stopping", `maxBudgetUsd` 는 비용 상한이다.

### 2.2 루프 — `chunk-gzc5bc6y.js`

쿼리 루프는 제너레이터 `su()` 가 자기 자신을 `query_recursive_call` 로 다시 부르는 **재귀**다. 한 라운드는 메시지 준비(`message_prep`) → API 호출(`stop_reason` ∈ `end_turn | tool_use | max_tokens | stop_sequence | pause_turn | refusal | model_context_window_exceeded`) → 도구 drain(`In()`; `tool_use` 블록을 실행하고 `tool_result` 를 모음) → 종료 판정이다. 판정은 `transition.reason` 으로 다음 라운드를 열거나(`next_turn`, `thinking_only_retry`, `malformed_tool_use_retry`), `{reason}` 을 돌려주며 끝난다. 번들에 있는 종료 사유 26종:

`completed`, `next_turn`, `max_turns`, `hook_stopped`, `stop_hook_prevented`, `stop_hook_blocking`, `tool_deferred`, `background_requested`, `aborted_streaming`, `aborted_tools`, `api_error`, `model_error`, `image_error`, `error`, `blocking_limit`, `rapid_refill_breaker`, `max_output_tokens_recovery`, `truncated_response_recovery`, `thinking_only_retry`, `malformed_tool_use_retry`, `malformed_tool_use_exhausted`, `refusal_retry`, `interjected`, `absorbed_mid_turn`, `fallback_sweep`, `before_write`.

읽을 수 있는 규칙들:

- **턴 상한**: 라운드 수 `K > maxTurns` 면 `max_turns_reached` 이벤트를 내고 `{reason: "max_turns"}`; Stop 훅이 턴 종료를 막고 있어도 상한은 이긴다(`hit_max_turns: true`).
- **Stop/SubagentStop 훅**: 훅이 `blockingErrors` 로 종료를 막으면 재귀로 계속하되 `stop_hook_active` 를 입력에 실어 준다; **연속 차단 상한 `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`(기본 8)** 을 넘기면 "A hook blocked the turn from ending N consecutive times — overriding and ending turn" 경고와 함께 강제 종료. `shouldPreventContinuation` 이면 `hook_stopped`.
- **도구가 턴을 끝낼 수 있다**: MCP 도구 결과의 메타가 `toolRequestedEndTurn` 을 요청하면 끝내되, Stop 훅이나 실패한 형제 도구가 이를 뒤집는다(`tengu_mcp_end_turn_overridden_by_stop_hook / _by_failed_sibling`).
- **배경·유예**: `shouldStopBeforeNextApiCall()` 이 참이면 `background_requested`(작업을 배경으로 넘기고 턴을 돌려줌), 도구가 유예되면 `tool_deferred`.
- **복구 라운드**: 사고(thinking)만 내고 끝나면 넛지 메시지로 1회 재시도(`thinking_only_retry`, 소진 시 `nudge_exhausted`), 파싱 불가한 tool_use 는 1회 재시도 후 "The model's tool call could not be parsed (retry also failed)"(`malformed_tool_use_exhausted`), `max_tokens` 로 잘리면 출력 한도 복구/잘린 응답 복구, `refusal` 은 같은 모델 재시도 또는 폴백 모델 대화(`CLAUDE_CODE_DISABLE_REFUSAL_RETRY` 로 끔).
- **압축**: 임계에 닿으면 자동 압축 후 시스템 메시지 `compact_boundary { trigger: manual|auto, pre_tokens, post_tokens, duration_ms }` 를 트랜스크립트에 남기고 계속; "Prompt is too long" 뒤에도 압축해 재시도(`tengu_compact_after_prompt_too_long`); 압축 직후 다시 가득 차는 **과열 차단기** `rapid_refill_breaker`(`autocompact_thrashing` 오류로 턴 종료).
- **텔레메트리** `tengu_turn_end { terminal_reason, error_kind, … }` 가 위 사유를 그대로 싣는다.

### 2.3 조종 — 명령 큐

Claude Code 의 조종은 **uuid 가 붙은 비동기 사용자 메시지 큐**다. `SDKUserMessage` 에 `priority: 'now' | 'next' | 'later'` 가 있고, `cancel_async_message` 제어 요청이 "Drops a pending async user message from the command queue by uuid", `interrupt` 는 `interrupt_receipt_v1` 능력이 있는 CLI 에서 **영수증** `{ still_queued: uuid[] }`("async user messages that WILL still run unless cancelled first")를 돌려주며 `cancel_queued: true` 면 큐의 메인 스레드 명령까지 취소한다. 루프 안에서는 도구 배치 사이에 폴 이벤트를 흡수하고(`absorbed_mid_turn`, `poll_event_delivery`; 중단·접힘 중이면 "leaving N poll event(s) queued"), 사용자가 끼어들면 `interjected` 로 분류한다. 스트리밍 입력 모드에서는 `streamInput()` 으로 메시지를 밀어 넣는다.

### 2.4 서브에이전트와 영속화

`Agent`/`Task` 도구가 **사이드체인**을 연다: 메시지에 `isSidechain`, `parent_tool_use_id` 가 붙고, 시스템 메시지 `task_started` / `task_notification` 이 진행을 알리며, `SubagentStop` 훅이 자식의 종료를 막을 수 있다(`agent_transcript_path` 포함). 사이드체인의 사용량은 메인 루프의 `usage` 에서 제외된다. 영속화는 세션별 JSONL 트랜스크립트([`claude-code/03`](../claude-code/03-sessions-context-and-clients.md) §1)이고 `compact_boundary` 줄이 압축 지점을 표시한다. 훅 이벤트 33종이 루프의 각 단계에 걸려 있다([`claude-code/02`](../claude-code/02-approval-and-permissions.md) §4).

## 3. opencode — 스텝 결과 세 값 `compact | stop | continue` ✅

### 3.1 단위와 이벤트

Session → Message(`role: user|assistant`, assistant 는 `parentID` 로 user 메시지를 가리킴) → Part. 파트는 Vercel AI SDK 의 UI 스트림 어휘(`start-step`→`step-start` 파트, `text-*`, `reasoning-*`, `tool-input-start`/`tool-call`/`tool-result`, `finish-step`, `finish{finishReason: stop|length|…}`)를 그대로 쓴다. 상태는 이벤트 버스로 나간다: `session.status { type: idle | busy | retry{attempt, message, action?, next} }`, `session.idle`, `session.error`, `message.updated`, `message.part.updated`.

### 3.2 루프 — `SessionPrompt` 와 `SessionProcessor`

바깥 루프(`chunk-f6y47634.js`)는 메시지 목록을 보며 돈다: 마지막 항목이 **압축 메시지**면 `SessionCompaction.process` 를 돌리고 결과가 `"stop"` 이면 `break`, 아니면 `continue`; 마지막 assistant 가 요약이 아니고 `isOverflow({tokens, model})` 면 압축 메시지를 **대화에 추가**하고 `continue`; 에이전트를 찾고(`Agent not found` 는 오류 이벤트), `eo = agent.steps ?? ∞`, `P = R >= eo` 면 스텝 상한 — 이때 모델 메시지 뒤에 assistant 메시지 하나를 덧붙여 텍스트 전용 응답을 유도한다(스키마 설명: "Maximum number of agentic iterations before forcing text-only response"; 삽입 문구 자체는 미독 ⚠️); 그런 뒤 `SessionProcessor.process` 를 호출한다.

`process` 는 `session.status = busy` 로 두고 `streamText` 스트림을 소비하며 파트를 갱신한다. 그 안의 판정:

- `tool-call` 전에 **doom loop 검사**: 직전 `ri = 3` 개의 파트가 모두 같은 도구·같은 입력(JSON 비교)이고 pending 이 아니면 `permission: "doom_loop"` 로 **승인 질문**을 던진다(UI 라벨 "Detect repeated tool calls (doom loop)"); 거부되면 차단.
- `tool-result` 가 오류면 처리 후 계속; 스텝 끝(`finish-step`)에 토큰을 재고 `Dl(cfg, tokens, model)` 이 넘치면 `needsCompaction = true`.
- `ContextOverflowError` 는 `compaction.auto === false` 가 아니면 `needsCompaction = true`(자동 압축이 꺼져 있으면 오류로 끝).
- 재시도는 `h.retry(cl.policy({provider}))` 로 공급자별 정책을 적용하고 매 시도를 `status: retry{attempt, next}` 로 **클라이언트에 보여 준다**.
- 중단은 `DOMException("Aborted")`; `continue_loop_on_deny`(experimental) 가 아니면 거부(`blocked`) 시 멈춘다.
- 반환: `needsCompaction → "compact"`, `blocked || error → "stop"`, 그 외 `"continue"`.

압축(`SessionCompaction`)은 요약용 자식 처리(`tools: {}`, 시스템 프롬프트 없이 요약 지시 사용자 메시지)로 돌고, 그 결과가 또 `"compact"` 면 "Conversation history too large to compact — exceeds model context limit"(미디어를 벗겨도 넘치면 다른 문구)로 **stop**. `compaction.auto` 외에 `prune`(오래된 도구 출력 가지치기), `preserve_recent_tokens`(keep), `reserved`(buffer) 설정이 있다. 세션이 바쁠 때의 두 번째 프롬프트는 `SessionRunState.assertNotBusy` → `RunnerBusy` 로 거절되고, UI 의 `followup: steer | queue`(기본 `steer`, `queue` 는 `steer` 로 마이그레이션) 설정이 사용자 메시지를 어떻게 넣을지 정한다 — 서버 측 조종 경로의 세부는 이번에 읽지 못했다 ⚠️.

### 3.3 서브에이전트와 영속화

`task` 도구(`subagent_type`, `description`)가 자식 세션을 만들며 `process` 에 `parentSessionID` 가 전달된다; UI 는 `metadata.sessionId` 로 탭을 열고 `background` 플래그·`toolCalls` 수를 보여 준다. 긴 도구 출력이 잘리면 "Use the Task tool to have explore agent process this file" 로 위임을 권한다. 영속화는 메시지·파트 저장소와 스텝별 스냅샷(`snapshot`/`revert` 로 파일 상태 되감기)이다.

## 4. Gemini CLI — 재귀 상한 100 과 "다음 화자" 판정 ✅

### 4.1 단위와 이벤트

히스토리는 Gemini API 의 `Content[]`, 요청마다 `Turn` 객체(`pendingToolCalls`, `finishReason`)를 만든다. `GeminiEventType` 18종: `Content`, `Thought`, `ToolCallRequest`, `ToolCallResponse`, `ToolCallConfirmation`, `UserCancelled`, `Error`, `ChatCompressed`, `MaxSessionTurns`, `Finished`, `LoopDetected`, `Citation`, `Retry`, `ContextWindowWillOverflow`, `InvalidStream`, `ModelInfo`, `AgentExecutionStopped`, `AgentExecutionBlocked`.

### 4.2 루프

**바깥 루프는 CLI 에 있다**(`nonInteractiveCli.ts`): `while (true) { turnCount++; maxSessionTurns 초과면 종료; sendMessageStream(currentMessages) 를 소비해 ToolCallRequest 를 모으고(LoopDetected/MaxSessionTurns/InvalidStream 은 종료); 요청이 있으면 Scheduler.schedule(requests) 로 실행한 뒤 functionResponse 파트를 다음 사용자 메시지로 삼아 반복; 없으면 끝 }`. `InvalidStream` 의 `MAX_TOKENS_EXCEEDED` 는 안내 문구로 바꾼다.

**안쪽**(`client.ts` `processTurn`, `MAX_TURNS = 100` 을 재귀마다 1씩 줄임): 세션 턴 수 검사 → 컨텍스트 관리(`contextManager` 가 켜져 있으면 히스토리 렌더링, 아니면 `tryCompressChat` — 압축되면 `ChatCompressed`, 토큰이 오히려 **팽창**하면 `COMPRESSION_FAILED_INFLATED_TOKEN_COUNT` 로 이후 자동 압축을 끈다, `CONTENT_TRUNCATED` 경로도 있음) → `remainingTokenCount` 보다 요청 추정이 크면 **`ContextWindowWillOverflow` 로 보내지 않고 종료** → IDE 컨텍스트 주입(도구 호출 대기 중이 아닐 때) → `loopDetector.turnStarted` → `turn.run` 스트림(`Content`/`Thought`/`ToolCallRequest`/`Finished(finishReason)`/`Retry`/`Citation`) 과 `addAndCheck` → 스트림이 끝났는데 `pendingToolCalls` 가 없으면 **`checkNextSpeaker`**: 휴리스틱(마지막 모델 메시지에 함수 호출이 있으면 `model`, 비어 있으면 `model`) 뒤 LLM 에게 JSON `{reasoning, next_speaker: user|model}` 을 묻고 `model` 이면 `"Please continue."` 를 스스로 보내 `boundedTurns − 1` 로 재귀한다(쿼터 오류 뒤나 `skipNextSpeakerCheck` 면 생략).

**루프 탐지**(`loopDetectionService.ts`) 는 세 겹이다: 동일 도구 호출 `TOOL_CALL_LOOP_THRESHOLD = 5`, 50자 청크의 콘텐츠 반복 `CONTENT_LOOP_THRESHOLD = 10`, 그리고 `LLM_CHECK_AFTER_TURNS = 30` 이후 `DEFAULT_LLM_CHECK_INTERVAL = 10`(5–15 적응) 턴마다 최근 20 항목을 진단 프롬프트로 LLM 에 묻고 신뢰도 ≥ 0.9 면 `loop-detection-double-check` 모델로 재확인. 첫 탐지는 `_recoverFromLoop` 로 복구를 시도하고, 두 번째(`count > 1`) 또는 남은 재귀가 1 이하면 `LoopDetected`/`MaxSessionTurns` 로 끝낸다.

**스케줄러**(`scheduler/scheduler.ts`): 큐 앞의 도구가 병렬 가능하면 연속된 병렬 가능 도구를 **한 배치**로 꺼내 `Promise.all` 로 검증·실행하고, 아니면 하나씩; 검증 단계에서 정책 엔진(`PolicyDecision`, `ApprovalMode`)과 확인 버스(`confirmation-bus`)로 승인을 받는다(`awaiting_approval` 상태). 재시도(`geminiChat.ts`): `maxAttempts 4`("1 initial call + 3 retries mid-stream"), `initialDelayMs 1000`, 연결 단계는 `retryWithBackoff`, 429/쿼터는 `handleFallback` 으로 폴백 모델. 영속화는 `ChatRecordingService` 의 대화 파일이고, 압축 성공 시 새 히스토리로 chat 을 **재시작**하며 IDE 컨텍스트를 다시 전부 보낸다. 대화형 TUI 의 큐·조종(`useGeminiStream.ts` 80 KB)과 에이전트 프레임워크(`AgentExecution*`)는 이번 패스에서 읽지 않았다 ⚠️.

## 5. Strands — 기존 독해 요약 ✅ ([`strands/02`](../strands/02-agent-loop.md))

Python 은 재귀, TypeScript 는 반복. 한 사이클 = 한도 검사 → (도구 인터럽트 재개면 모델 호출 생략) → 입력 토큰 추정 → `BeforeModelCall` 훅(취소 시 합성 `end_turn`) → 메시지 딥카피 + 모델 호출 미들웨어 → `AfterModelCall` 훅(`retry=True` 면 되돌림) → assistant 추가 → `max_tokens` 면 `toolUse` 를 오류 텍스트로 바꾸고 예외 → `tool_use` 면 `BeforeTools`/실행/`AfterTools` → 도구 결과를 **하나의 user 메시지**로 추가 → 재귀. 매 사이클 끝에 `conversation_manager.apply_management`(슬라이딩 윈도). 종료 어휘는 Python 12 값(모델 6 + 한도 3 + `cancelled`/`interrupt`/`checkpoint`), TS 15+ 개방. 한도(`turns`, 토큰)는 사이클 경계에서만 검사돼 "한 번의 큰 응답은 넘칠 수 있다". 취소는 스트림 청크 사이·도구 전·도구 후 네 지점.

## 6. 교차 독해

### 6.1 "턴"이라는 말의 네 뜻

| 하네스 | 한 "턴" | 상한 |
|---|---|---|
| Codex(App Server) | 사용자 입력 하나로 시작하는 **작업 단위**(샘플링 여러 번 포함) | 없음 |
| Claude Code | **API 왕복 1회**(`maxTurns`, `num_turns`) | `maxTurns`, `maxBudgetUsd` |
| opencode | 스텝(`step-start`…`finish-step`); 바깥은 메시지 단위 | 에이전트별 `steps`(기본 ∞) |
| Gemini CLI | `Turn` 객체 = 요청 1회; 세션 턴 수는 CLI 가 셈 | `MAX_TURNS 100`(재귀), `maxSessionTurns` |
| Strands | 모델 호출 1회 | `turns`, 토큰 |

Codex 만이 "턴"을 사용자 단위로 정의한다. 나머지는 모델 호출을 턴이라 부르므로, 같은 숫자(예: `maxTurns = 10`)가 Codex 에서는 의미가 없고 Claude Code 에서는 열 번의 API 호출이다. 위키 [`thread-turn-item`](../ai-workflow/wiki/concepts/thread-turn-item.md) §6 의 어휘 함정이 여기서 다시 확인된다.

### 6.2 계속할지를 정하는 신호

- **Codex**: 출력에 도구 호출이 있었는가(`needs_follow_up`) ∨ 보류 입력이 있는가. 모델의 `stop_reason` 을 보지 않는다 — Responses API 의 `Completed` 이후 항목 종류로 판단한다.
- **Claude Code**: `stop_reason` + 도구 결과 + 훅 + 상한. `end_turn` 이어도 Stop 훅이 막으면 계속, `tool_use` 여도 도구가 유예되면 끝.
- **opencode**: 스텝 함수의 반환값 세 가지. 압축이 "계속"과 같은 층위의 분기다.
- **Gemini**: 도구 호출 유무 → 없으면 **LLM 에게 묻는다**("Model Continues / Question to User / Waiting for User" 세 규칙). 다른 넷에 없는 설계로, 모델이 "다음에 …하겠다"고 말만 하고 멈추는 경우를 자동으로 밀어 준다. 대가는 턴마다 추가 호출 1회.
- **Strands**: `stop_reason == tool_use` 뿐.

### 6.3 조종(진행 중 입력)의 세 모델

Codex 는 **의도를 모드로**(`StartOrSteer`/`Steer{expected_turn_id}`) 받아 샘플링 사이에 흡수하고 필요하면 진행 중 샘플링을 선점한다; 줄서기는 별도 서비스. Claude Code 는 **큐에 우선순위를**(`now|next|later`) 두고 인터럽트가 "아직 남은 것"의 영수증을 돌려준다 — 클라이언트가 무엇이 취소되고 무엇이 살아남았는지 알 수 있다. opencode 는 서버가 **바쁘면 거절**하고 UI 가 `steer|queue` 를 정한다(세부 ⚠️). Gemini 비대화형과 Strands 에는 없다. 이 축은 [`agent-ux/02`](../agent-ux/02-claude-desktop.md) §3.8 의 "Queued. Claude will read this after the current turn" 같은 UI 문구의 엔진 쪽 근거다.

### 6.4 압축이 끼는 자리

Codex 와 Claude Code 는 압축을 **루프의 한 분기**로 둔다(샘플링 사이, 자동, 비동기 후보, 턴 끝). opencode 는 압축을 **대화의 메시지**로 표현해 같은 루프가 처리한다(압축 결과가 또 넘치면 멈춤). Gemini 는 **보내기 전** 전처리이고, 넘칠 것 같으면 보내지 않고 끝낸다(`ContextWindowWillOverflow`), 팽창 실패를 기억해 재시도하지 않는다. Strands 는 사이클 뒤의 윈도 트림이다. 네 가지 모두 "압축 뒤 첫 요청"을 특별 취급한다(Codex 의 보류 입력 유예, Claude 의 `compact_boundary`·과열 차단기, Gemini 의 IDE 컨텍스트 전체 재전송).

### 6.5 반복 방어

Gemini 가 가장 두텁다(결정적 2겹 + LLM 판정 + 복구 1회). opencode 는 **승인 게이트**로 만든다 — 같은 호출 3회면 사람에게 묻는다(doom loop 이 권한의 한 종류). Claude Code 는 특정 실패 모양(사고만, 깨진 tool_use, 잘린 출력, 거절)에 각각 1회 복구를 두고, 훅이 끝을 막는 횟수를 8로 제한한다. Codex 는 루프 자체에 탐지가 없다 ⚠️ — 승인 캐시·Guardian·토큰 예산·훅이 그 역할을 나눠 맡는다(추정).

### 6.6 승인이 루프를 멈추는 지점

Codex 는 도구 future 안에서 서버→클라이언트 요청(`ExecApprovalRequest` 등)을 기다리고 샘플링 루프는 그 future 를 `in_flight` 로 든다; Claude Code 는 도구 drain 안의 `canUseTool`("permission prompts have no park deadline", [`claude-code/02`](../claude-code/02-approval-and-permissions.md) §2); opencode 는 `permission.asked` 로 스텝을 멈추고 거부되면 `blocked → stop`(실험 플래그로 계속 가능); Gemini 는 스케줄러의 `awaiting_approval` 상태; Strands 는 `interrupt` 종료 사유로 호출자에게 돌려준다. 다섯 모두 **승인은 샘플링 밖, 도구 실행 안**에 있다 — [`SYNTHESIS`](../SYNTHESIS.md) §2.1 의 "approval as primitive" 가 루프 위치로도 성립한다.

### 6.7 공통 패턴

1. 원자는 **샘플링 사이클**이고 "계속"은 그 사이클의 출력에서 계산된다 — 모델이 직접 "계속하겠다"고 선언하는 경로는 Gemini 의 다음 화자 판정뿐이다.
2. **턴 끝 훅**이 종료를 뒤집을 수 있는 곳은 Codex(Stop 훅 → 계속)와 Claude Code(Stop/SubagentStop, 상한 8) 둘이며, 둘 다 "프롬프트 없이 막기"를 무시/경고한다.
3. 종료 어휘를 **와이어에 얼마나 드러내는가**: Claude Code 는 26종 내부 사유를 `result.subtype` 5종 + `stop_reason` 으로 접어 내보내고, Codex 는 `TurnComplete`/`TurnAborted`/`Error(codexErrorInfo 개방 집합)` 로, opencode 는 `session.status`·`finish`, Gemini 는 이벤트 타입으로 드러낸다. 클라이언트가 "왜 끝났는가"를 구분할 수 있는 정도가 다르다.
4. **서브에이전트의 컨텍스트 상속**은 Codex 만 규칙을 명시한다(롤아웃 스냅샷 + 기준선 보존 조건); Claude Code 는 사이드체인 표식과 알림, opencode 는 자식 세션으로 분리한다.

## 7. 미검증 ⚠️

| 항목 | 이유 |
|---|---|
| 모든 런타임 동작(실제 재시도 횟수·압축 시점·선점 타이밍) | 실행하지 않았다 |
| Codex 의 `thread/queue` 디스패처가 조종 입력과 경합할 때의 순서 | 코드 경로만 읽음 |
| Claude Code 의 자동 압축 임계 계산식과 `rapid_refill_breaker` 조건값 | 번들에서 상수를 특정하지 못함([`claude-code/03`](../claude-code/03-sessions-context-and-clients.md) §2 의 문서 수치가 기준) |
| opencode 의 서버 측 조종(`steer`) 경로와 스텝 상한 때 삽입되는 문구 | 번들 식별자가 짧아 추적 중단 |
| Gemini 대화형 TUI 의 큐·조종, 에이전트 프레임워크, `_recoverFromLoop` 의 본문 | 미독 |
| Strands 의 최신 커밋 | 기존 노트(`bd0b6a94` 기준)를 요약만 함 |

## 8. 출처

- Codex: `codex-rs/core/src/session/turn.rs`(`run_turn` L455–915, `run_sampling_request` L1714, `try_run_sampling_request` L2628–), `session/turn_input.rs`, `session/input_queue.rs`, `protocol/src/turn_input.rs:188`(`TurnInputMode`), `protocol/src/protocol.rs`(`Op` 31 / `EventMsg` 84), `codex-api/src/common.rs`(`ResponseEvent` 17), `ext/queue/src/service.rs`, `agent/control/spawn.rs`, `async-utils/src/backoff.rs`, `model-provider-info/src/lib.rs:67–73`. 리비전 `79a19cbb3`, 루프 파일은 `1a35bc4cc` 까지 동일.
- Claude Code: 분리 번들 2.1.304 `chunk-gzc5bc6y.js`(종료 사유 26·`tengu_turn_end`·`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`), `chunk-rncrmfyt.js`(Stop/SubagentStop 훅 입력), `chunk-x1sw9a90.js`/`chunk-jgkqy0y7.js`(`compact_boundary`); `sdk.d.ts` 0.3.304 (`maxTurns` L75/1960, `SDKResultError` L5839, `SDKCompactBoundaryMessage`, `Query.interrupt` L2912, `cancel_async_message` L3954, `SDKUserMessage` L6435).
- opencode: 분리 번들 1.17.12 `chunk-f6y47634.js`(`SessionProcessor.process`, `ri = 3`, `SessionCompaction`, `SessionStatus`), `chunk-g5fbberp.js`(에이전트 `steps` 스키마), `chunk-5jzqd20r.js`(task 탭), `index-DaUQTD8K-e2bvt10k.js`(`followup` 설정).
- Gemini CLI: `raw.githubusercontent.com/google-gemini/gemini-cli/main/packages/{core/src/core/client.ts, core/turn.ts, core/geminiChat.ts, services/loopDetectionService.ts, utils/nextSpeakerChecker.ts, scheduler/scheduler.ts, cli/src/nonInteractiveCli.ts}` (2026-10-20 읽음; `coreToolScheduler.ts` 는 `scheduler/` 로 이동).
- Strands: [`strands/02`](../strands/02-agent-loop.md) §1.
