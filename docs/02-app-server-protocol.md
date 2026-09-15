# 02. Codex App Server 프로토콜 (핵심)

> 출처: 공식 문서 <https://developers.openai.com/codex/app-server> (→ learn.chatgpt.com/docs/app-server),
> OpenAI 엔지니어링 블로그(2026-02-04), 그리고 **`openai/codex` 리포지터리에서 자동 생성된 스키마**
> (`codex-rs/app-server-protocol/schema/`). 메서드 목록은 생성 스키마가 정본입니다.

## 1. 프로토콜 기본 형태

**"JSON-RPC lite"** — 블로그 각주에서 직접 밝힌 내용:

> request/response/notification 형태는 유지하되, `"jsonrpc": "2.0"` 헤더를 **생략**하고,
> 엄격한 JSON-RPC 2.0이 아니라 **stdio 위의 JSONL**로 프레이밍한다.

메시지 3종:

| 종류 | 형태 | 방향 |
|---|---|---|
| Request | `{ id, method, params }` | 클라이언트→서버, **그리고 서버→클라이언트** |
| Response | `{ id, result }` 또는 `{ id, error }` | 요청의 반대 방향 |
| Notification | `{ method, params }` (id 없음) | 주로 서버→클라이언트 |

## 2. 전송 (transport)

| 전송 | 상태 | 비고 |
|---|---|---|
| **stdio** | 기본값 | 개행 구분 JSON(JSONL). 단일 클라이언트. VS Code 확장·Python SDK가 사용 |
| **WebSocket** | 실험적 | `ws://` / `wss://`, 인증 옵션. 다중 클라이언트 |
| **Unix socket** | 지원 | 표준 HTTP upgrade 핸드셰이크 |
| **off** | — | 로컬 전송 노출 안 함 |

헬스 프로브: `/readyz`, `/healthz`.

호스팅 환경(Codex Web 등)에서는 컨테이너 내부의 stdin/stdout을 지속 연결(WebSocket 유사)로 터널링합니다.
즉 "실제 로컬 파이프가 아니어도 stdio처럼 동작"합니다.

## 3. 핸드셰이크

클라이언트는 **다른 어떤 메서드보다 먼저 `initialize` 단 1회**를 보내야 하고,
초기화 완료 전 요청은 전부 거부됩니다.

```json
{
  "method": "initialize",
  "id": 0,
  "params": {
    "clientInfo": {
      "name": "codex_vscode",
      "title": "Codex VS Code Extension",
      "version": "0.1.0"
    },
    "capabilities": {
      "experimentalApi": true
    }
  }
}
```

서버 응답 (`InitializeResponse`, 생성 스키마 기준):

```json
{
  "id": 0,
  "result": {
    "userAgent": "codex_vscode/0.94.0-alpha.7 (Mac OS 26.2.0; arm64) vscode/2.4.22 (codex_vscode; 0.1.0)",
    "codexHome": "/Users/you/.codex",
    "platformFamily": "unix",
    "platformOs": "macos"
  }
}
```

| 필드 | 의미 |
|---|---|
| `userAgent` | 서버가 조립한 UA 문자열 |
| `codexHome` | 서버의 `$CODEX_HOME` 절대 경로 |
| `platformFamily` | `"unix"` / `"windows"` |
| `platformOs` | `"macos"` / `"linux"` / `"windows"` |

이어서 클라이언트가 알림으로 확인:

```json
{ "method": "initialized" }
```

> `ClientNotification`은 **`initialized` 하나뿐**입니다.

### `InitializeCapabilities` (클라이언트 선언 능력)

```ts
type InitializeCapabilities = {
  experimentalApi: boolean,               // 실험적 메서드/필드 수신 옵트인
  requestAttestation: boolean,            // attestation/generate 수신 옵트인 (x-oai-attestation)
  mcpServerOpenaiFormElicitation?: boolean, // (레거시) openai/form MCP 확장
  optOutNotificationMethods?: string[] | null, // 이 연결에서 억제할 알림 메서드 이름 (예: "thread/started")
  extensions?: Record<string, JsonValue> | null, // MCP 확장 설정
}
```

실험적 기능은 **반드시 `experimentalApi: true`로 옵트인**해야 노출됩니다.

## 4. 대화 프리미티브 — Thread / Turn / Item

API 설계가 어려운 이유: 사용자↔에이전트 상호작용은 단순 request/response가 아니라,
하나의 요청이 **구조화된 행동 시퀀스**로 펼쳐지기 때문. 그래서 경계와 생명주기가 명확한 3개 프리미티브로 정리:

### Item — 입출력의 원자 단위

생명주기가 **명시적**입니다.

```
item/started  →  item/*/delta (0..N)  →  item/completed
```

클라이언트는 `started`에 즉시 렌더 시작 → `delta`로 증분 갱신 → `completed`에서 최종 페이로드로 확정.

`ThreadItem`의 `type` 값 (생성 스키마 `v2/ThreadItem.ts` 기준):

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
| `webSearch` / `imageView` / `imageGeneration` / `sleep` | 각 전용 페이로드 |
| `enteredReviewMode` / `exitedReviewMode` | `review` |
| `contextCompaction` | — |

> `commandExecution`의 `commandActions`는 **파이프로 엮인 셸 명령을 best-effort 파싱**한 결과 목록입니다.
> UI에서 "이 명령이 뭘 하는지"를 설명하는 데 씁니다.

### Turn — 사용자 입력 1개가 촉발한 에이전트 작업 단위

클라이언트가 입력을 제출할 때 시작, 그 입력에 대한 출력 생성을 끝내면 종료.
**인터럽트/롤백의 단위**이며 내부에 item 시퀀스를 담습니다.

### Thread — 지속되는 대화 컨테이너

여러 turn을 담고, 생성·재개·포크·아카이브가 가능하며 히스토리가 영속화됩니다.
(2차 출처 기준, 유휴 30분 후 언로드되지만 저장된 대화는 남습니다.)

## 5. 전형적인 한 턴의 흐름

```
client → initialize                        server → result
client → initialized (notification)
client → thread/start                      server → thread/started (notification)
                                           server → result { thread, model, cwd, approvalPolicy, sandbox, ... }
client → turn/start                        server → turn/started
                                           server → item/started (userMessage)
                                           server → item/completed (userMessage)
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

전체 JSON을 실제로 보고 싶으면:

```bash
codex debug app-server send-message-v2 "run tests and summarize failures"
```

## 6. 클라이언트 → 서버 메서드 (총 104개)

`ClientRequest` 전체 목록. 도메인별로 묶었습니다.

### 6.1 핸드셰이크
```
initialize
```

### 6.2 Thread 생명주기 (핵심)
```
thread/start            thread/resume           thread/fork
thread/archive          thread/unarchive        thread/delete
thread/unsubscribe      thread/read             thread/list
thread/loaded/list      thread/revert           thread/compact/start
thread/name/set         thread/metadata/update
thread/turns/list       thread/items/list       thread/inject_items
thread/shellCommand     thread/approveGuardianDeniedAction
```

### 6.3 Thread 목표(goal) / 첨부 / 섹션
```
thread/goal/set         thread/goal/get         thread/goal/clear
thread/attachment/add   thread/attachment/list  thread/attachment/remove
thread/section/move
threadSection/list      threadSection/create    threadSection/update   threadSection/delete
```

### 6.4 Turn 제어 (핵심)
```
turn/start              turn/steer              turn/interrupt
review/start
```

### 6.5 모델 / 설정
```
model/list                          modelProvider/capabilities/read
config/read                         config/value/write          config/batchWrite
configRequirements/read
experimentalFeature/list            experimentalFeature/enablement/set
permissionProfile/list
```

### 6.6 MCP
```
mcpServer/tool/call         mcpServer/resource/read     mcpServer/oauth/login
mcpServerStatus/list        config/mcpServer/reload
```

### 6.7 Skills / Hooks / Plugins / Apps (확장)
```
skills/list                 skills/extraRoots/set       skills/config/write
hooks/list
plugin/list                 plugin/installed            plugin/read
plugin/install              plugin/uninstall            plugin/reconcile
plugin/skill/read
plugin/share/save           plugin/share/list           plugin/share/checkout
plugin/share/delete         plugin/share/updateTargets
marketplace/add             marketplace/remove          marketplace/upgrade
app/list                    app/read                    app/installed
```

### 6.8 파일시스템 (클라이언트가 서버를 통해 FS 접근)
```
fs/readFile     fs/writeFile    fs/createDirectory
fs/readDirectory fs/getMetadata fs/remove       fs/copy
fs/watch        fs/unwatch
fuzzyFileSearch
```

### 6.9 명령 실행 (에이전트 루프 밖, 클라이언트 주도 PTY)
```
command/exec            command/exec/write
command/exec/terminate  command/exec/resize
```

### 6.10 계정 / 인증 / 사용량
```
account/login/start     account/login/cancel    account/logout
account/read            getAuthStatus
account/rateLimits/read account/usage/read
account/rateLimitResetCredit/consume
account/workspaceMessages/read
account/sendAddCreditsNudgeEmail
```

### 6.11 기타
```
gitDiffToRemote         getConversationSummary      feedback/upload
windowsSandbox/setupStart   windowsSandbox/readiness
externalAgentConfig/detect  externalAgentConfig/import
externalAgentConfig/import/recordHistory
externalAgentConfig/import/readHistories
```

> `externalAgentConfig/*`는 **다른 에이전트 도구의 설정을 감지해서 import**하는 마이그레이션 경로입니다
> (`codex-rs/external-agent-migration` 크레이트).

## 7. 서버 → 클라이언트 요청 (10개) — 사람이 개입하는 지점

서버가 요청을 보내고 **클라이언트 응답까지 턴이 멈춥니다.**

| 메서드 | 용도 |
|---|---|
| `item/commandExecution/requestApproval` | 명령 실행 승인 |
| `item/fileChange/requestApproval` | 파일 변경 승인 |
| `item/permissions/requestApproval` | 권한 상승 승인 |
| `item/tool/requestUserInput` | 도구가 사용자 입력을 요구 |
| `item/tool/call` | 동적 도구 호출을 클라이언트에 위임 (`DynamicToolCallParams`) |
| `mcpServer/elicitation/request` | MCP elicitation |
| `account/chatgptAuthTokens/refresh` | ChatGPT 토큰 갱신 요청 |
| `attestation/generate` | 업스트림 `x-oai-attestation` 생성 (capability 옵트인 필요) |
| `applyPatchApproval` | (레거시) 패치 적용 승인 |
| `execCommandApproval` | (레거시) 명령 실행 승인 |

### 승인 결정값

`ReviewDecision` 계열: `accept`, `acceptForSession`, `decline`, `cancel`,
그리고 정책 수정을 동반하는 `acceptWithExecpolicyAmendment` 류
(`ExecPolicyAmendment`, `NetworkPolicyAmendment` 타입 존재).

`item/tool/call`의 존재가 중요합니다 — **호스트 앱이 소유한 도구를 에이전트가 호출**하는 통로이며,
"앱은 제품 컨텍스트/비즈니스 규칙/도구를 소유하고 Codex는 루프와 샌드박스 실행을 제공한다"는 분업이
프로토콜 레벨에서 구현된 지점입니다.

## 8. 서버 알림 (84개)

### 8.1 Thread 수명
```
thread/started              thread/status/changed       thread/closed
thread/archived             thread/unarchived           thread/deleted
thread/reverted             thread/compacted
thread/name/updated         thread/metadata 관련
thread/goal/updated         thread/goal/cleared
thread/attachment/updated   thread/queue/changed
thread/settings/updated     thread/tokenUsage/updated
thread/project/updated      project/changed
thread/environment/connected  thread/environment/disconnected
```

### 8.2 Turn 수명
```
turn/started        turn/completed
turn/diff/updated   turn/plan/updated
turn/moderationMetadata
hook/started        hook/completed
```

### 8.3 Item 수명 & 스트리밍 (UI의 핵심)
```
item/started                            item/completed
item/agentMessage/delta
item/plan/delta
item/reasoning/summaryTextDelta         item/reasoning/summaryPartAdded
item/reasoning/textDelta
item/commandExecution/outputDelta       item/commandExecution/terminalInteraction
item/fileChange/outputDelta             item/fileChange/patchUpdated
item/mcpToolCall/progress
item/autoApprovalReview/started         item/autoApprovalReview/completed
autoApprovalReview/strictReviewRequired
rawResponseItem/completed               rawResponse/completed
serverRequest/resolved
```

> `rawResponseItem/completed` / `rawResponse/completed`는 모델 원시 응답까지 그대로 보고 싶을 때 쓰는 탈출구입니다.
> `serverRequest/resolved`는 승인 요청이 (다른 클라이언트/자동승인 등으로) 해소됐음을 알려 UI 정리를 돕습니다.

### 8.4 프로세스 / 명령
```
command/exec/outputDelta    process/outputDelta     process/exited
```

### 8.5 MCP / 앱 / 계정
```
mcpServer/startupStatus/updated     mcpServer/oauthLogin/completed
mcpServer/event/stream/notification
app/list/updated
account/updated     account/rateLimits/updated      account/login/completed
skills/changed
```

### 8.6 모델 관련
```
model/rerouted          model/verification
model/safetyBuffering/updated
modelProvider/authRecoveryStarted   modelProvider/authRecoveryCompleted
```

### 8.7 실시간(음성) 세션
```
thread/realtime/started         thread/realtime/closed      thread/realtime/error
thread/realtime/itemAdded       thread/realtime/item/started  thread/realtime/item/completed
thread/realtime/item/transcript/delta
thread/realtime/transcript/delta  thread/realtime/transcript/done
thread/realtime/outputAudio/delta  thread/realtime/sdp
```

### 8.8 경고 / 진단 / 기타
```
error       warning     guardianWarning     configWarning   deprecationNotice
fs/changed
fuzzyFileSearch/sessionUpdated      fuzzyFileSearch/sessionCompleted
remoteControl/status/changed
externalAgentConfig/import/progress externalAgentConfig/import/completed
windows/worldWritableWarning        windowsSandbox/setupCompleted
```

> 클라이언트는 `initialize`의 `optOutNotificationMethods`로 원하지 않는 알림을 **연결 단위로 차단**할 수 있습니다.

## 9. 주요 파라미터 타입

### `ThreadStartParams`

```ts
type ThreadStartParams = {
  model?: string | null,
  modelProvider?: string | null,
  serviceTier?: string | null,
  cwd?: string | null,
  approvalPolicy?: AskForApproval | null,
  approvalsReviewer?: ApprovalsReviewer | null,  // 승인 요청을 어디로 라우팅할지
  sandbox?: SandboxMode | null,
  config?: Record<string, JsonValue> | null,
  serviceName?: string | null,
  baseInstructions?: string | null,
  developerInstructions?: string | null,
  personality?: Personality | null,
  ephemeral?: boolean | null,                     // 영속화하지 않는 thread
  sessionStartSource?: ThreadStartSource | null,
  threadSource?: ThreadSource | null,
}
```

### `ThreadStartResponse`

```ts
type ThreadStartResponse = {
  thread: Thread,
  model: string,
  modelProvider: string,
  serviceTier: string | null,
  disabledPluginIds: string[],
  cwd: AbsolutePathBuf,
  instructionSources: LegacyAppPathString[],  // 현재 로드된 지시문 파일 경로들 (AGENTS.md 등)
  approvalPolicy: AskForApproval,
  approvalsReviewer: ApprovalsReviewer,
  sandbox: SandboxPolicy,                      // 레거시 호환, 실험 클라이언트는 activePermissionProfile 선호
  reasoningEffort: ReasoningEffort | null,
}
```

### `TurnStartParams`

```ts
type TurnStartParams = {
  threadId: string,
  input: UserInput[],                 // 필수
  clientUserMessageId?: string | null,
  turnTrigger?: string | null,
  toolOutput?: TurnToolOutput | null,
  disabledPluginIds?: string[] | null, // null=유지, []=해제

  // 아래는 전부 "이번 턴 + 이후 턴"에 적용되는 오버라이드
  cwd?: string | null,
  approvalPolicy?: AskForApproval | null,
  approvalsReviewer?: ApprovalsReviewer | null,
  sandboxPolicy?: SandboxPolicy | null,
  model?: string | null,
  serviceTier?: string | null,
  effort?: ReasoningEffort | null,
  summary?: ReasoningSummary | null,
  personality?: Personality | null,

  serviceTierForTurn?: string | null,  // 이번 턴에만 적용 (thread tier 변경 안 함)
  outputSchema?: JsonValue | null,     // 최종 assistant 메시지를 제약하는 JSON Schema
}
```

> **주의할 시맨틱**: `turn/start`의 오버라이드는 대부분 *sticky*입니다 — 이번 턴뿐 아니라 이후 턴에도 남습니다.
> 한 턴에만 적용하고 싶으면 `serviceTierForTurn`처럼 명시적으로 분리된 필드를 쓰거나, 다음 턴에 되돌려야 합니다.

### `UserInput` 종류 (protocol_v1 기준)

| type | 설명 |
|---|---|
| `text` | 평문 + 선택적 UI 텍스트 요소 |
| `image` / `local_image` | 이미지 입력 |
| `skill` | 명시적 skill 선택 (`name`, `SKILL.md` 경로) |
| `mention` | 명시적 앱/커넥터 선택 (`name`, `app://{connector_id}` 형식 경로) |

## 10. 샌드박스 정책

| 값 | 의미 |
|---|---|
| `readOnly` | 읽기 전용 파일시스템 |
| `workspaceWrite` | 지정된 루트 내 쓰기 허용 |
| `dangerFullAccess` | 무제한 |
| `externalSandbox` | 클라이언트가 샌드박스를 직접 관리 |

`networkAccess` 옵션으로 외부 통신 제어.

## 11. 에러 처리

턴 실패는 `turn/completed`에 실려 옵니다:

```json
{
  "method": "turn/completed",
  "params": {
    "turn": {
      "status": "failed",
      "error": {
        "message": "...",
        "codexErrorInfo": "ContextWindowExceeded"
      }
    }
  }
}
```

대표 `codexErrorInfo`: `ContextWindowExceeded`, `UsageLimitExceeded`, `HttpConnectionFailed`, `SandboxError`.

RPC 자체 실패는 JSON-RPC 에러 봉투를 쓰며, 일부 도메인(예: user verification)은
닫힌 집합 `{type, reason}` 데이터를 함께 실어 보냅니다 —
`invalidRequest` / `unavailable` / `cancelled` / `failed`.
**UI는 메시지 텍스트가 아니라 이 값으로 분기해야 합니다.**

알려진 코드:
- `-32600` — 살아있는 내부 워커를 `thread/archive`/`thread/delete`로 제거하려 할 때
- `-32601` — 미지원 메서드 (제거된 `thread/rollback` 등)
- `-32001` — (2차 출처) 인그레스 큐 포화 시 "Server overloaded; retry later". 지수 백오프 + 지터 권장

## 12. 코드 생성 — 직접 바인딩 만들기

```bash
codex app-server generate-ts            # Rust 프로토콜 → TypeScript 정의
codex app-server generate-json-schema   # JSON Schema 번들 (임의 언어 제너레이터에 투입)
```

리포지터리에 커밋된 산출물도 그대로 읽을 수 있습니다:

```
codex-rs/app-server-protocol/schema/
├── json/
│   ├── ClientRequest.json                        (~197KB)
│   ├── ServerNotification.json                   (~198KB)
│   ├── ServerRequest.json                        (~49KB)
│   ├── codex_app_server_protocol.schemas.json    (~682KB)
│   ├── codex_app_server_protocol.v2.schemas.json (~583KB)
│   └── v1/ , v2/
├── typescript/
│   ├── ClientRequest.ts  ServerRequest.ts  ServerNotification.ts
│   ├── InitializeParams.ts  InitializeResponse.ts  InitializeCapabilities.ts
│   ├── index.ts
│   └── v2/   ← ThreadStartParams, TurnStartParams, ThreadItem 등 실제 페이로드
└── precomputed/
```

실제 구현 언어 사례: **Go, Python, TypeScript, Swift, Kotlin**.
OpenAI는 "JSON schema와 문서를 Codex에게 먹이면 통합 작업의 대부분을 대신해준다"고 안내합니다.

## 13. 클라이언트 통합 패턴 3가지

### (a) 로컬 앱 · IDE
플랫폼별 App Server 바이너리를 번들하거나 내려받아 **장기 실행 자식 프로세스**로 띄우고 stdio 양방향 채널 유지.
VS Code 확장과 Desktop 앱은 검증된 버전으로 **핀 고정**해 배포.
Xcode처럼 릴리스 주기를 분리하고 싶은 파트너는 클라이언트를 고정한 채 **더 새로운 App Server 바이너리를 가리키게** 함
— 프로토콜이 하위 호환이라 구버전 클라이언트가 신버전 서버와 통신해도 안전.

### (b) Codex Web
워커가 워크스페이스를 체크아웃한 컨테이너를 프로비저닝 → 그 안에서 App Server 바이너리 실행 →
stdio JSON-RPC 채널 유지. 브라우저는 Codex 백엔드와 HTTP + SSE로 통신.
**웹 세션은 휘발적(탭 닫힘/네트워크 끊김)이라 진실 공급원이 될 수 없으므로 상태와 진행은 서버에 둔다**는 것이 핵심 설계.

### (c) TUI / Codex CLI
역사적으로 TUI는 에이전트 루프와 같은 프로세스에서 Rust 타입을 직접 다루는 "네이티브" 클라이언트였음.
App Server 도입 후 **TUI도 일반 클라이언트로 리팩터링 예정** — App Server 자식 프로세스를 띄우고 JSON-RPC로 통신.
이렇게 되면 TUI가 **원격 머신의 Codex 서버에 붙는** 워크플로가 가능해짐
(노트북이 잠자거나 끊겨도 컴퓨트 근처에서 작업 지속).

## 14. 최근 프로토콜 변경사항 (`app-server/README.md` 기준)

리포의 `codex-rs/app-server/README.md`는 릴리스 노트에 가까운 성격으로, 현재 담긴 내용:

- **`thread/rollback` 제거** — 요청/응답 타입까지 삭제, 미지원 메서드 경로로 거부됨. **`thread/revert` 사용**.
  단 디스크에 남은 과거 `ThreadRolledBack` 이벤트의 재생/마이그레이션은 계속 지원.
- **Thread 첨부(attachment)** — `thread/attachment/add|list|remove` + `thread/attachment/updated` 알림.
  thread를 로드하지 않고도 조작 가능. `(threadId, attachmentType, identityKey)`로 멱등 식별.
  PR의 경우 `JSON.stringify([canonicalHostname, lowercaseOwner, lowercaseRepository, pullRequestNumber])`를
  정규 identity로 쓰도록 권고. thread당 최대 100개, 페이지당 최대 100개.
- **Thread 제거 제약** — 살아있는 내부 워커(예: Guardian 리뷰어)는 `thread/archive`/`thread/delete`로 제거 불가 (`-32600`).
  소유자가 워커를 놓아준 뒤에야 가능.
- **플러그인 선택** — `thread/settings/update`와 `turn/start`가 `disabledPluginIds` 수용
  (`<plugin-name>@<marketplace-name>` 형식, `plugin/list`의 `PluginSummary.id`).
  리스트를 주면 치환, 생략/`null`이면 유지, `[]`면 해제. **아직 실제 능력 필터링은 안 함**(저장만).
- **MCP 서버 capabilities** — `mcpServerStatus/list`가 서버가 광고한 capabilities 객체(`extensions` 맵 포함)를
  `full` / `toolsAndAuthOnly` 두 모드 모두에서 반환. 초기화 실패 시 null이며, **도구 목록에서 추론하지 않음**.
- **Hosted Codex Apps MCP 프로토콜** — 기본 Legacy. `[features] codex_apps_mcp_2026_07_28 = true` 또는
  런타임 오버라이드(`experimentalFeature/enablement/set`)로 2026-07-28 프로토콜 탐색.
- **User verification (실험적)** — 생체 인증. `userVerification/status|enroll|delete|verify|cancel` 5개 메서드.
  P-256 ECDSA + SHA-256, `ecdsaP256Sha256X962`, unpadded base64url SPKI-DER.
  TUI/Desktop 로컬 세션 + `experimentalApi` 옵트인 조건에서만 광고됨. app-server당 네이티브 워커 1개.
- **Managed model provider** — 기존 thread는 provider 설정을 유지하며, 관리형 요구사항과 안 맞으면
  입력 계열 RPC(턴 시작/steer, review, compaction, 큐 시작, goal 갱신)를 거부. interrupt/pause/clear는 계속 허용.
- **Amazon Bedrock** — `model_providers.amazon-bedrock.aws.credential_export`가 설정돼 있으면 Bedrock 셋업/로그인은
  설정 변경 없이 에러. `aws.credential_export`와 `aws.profile`은 동시 설정 불가.

## 15. 레거시: Codex core 내부 프로토콜 (protocol_v1)

App Server 이전/아래 계층에 있는 **SQ/EQ 모델**. `codex-rs/docs/protocol_v1.md`.

- `Codex` ↔ UI는 **Submission Queue(SQ)** / **Event Queue(EQ)** 쌍으로 통신.
- `Op` = Submission 페이로드 enum (`Op::ConfigureSession`, `Op::UserTurn`, `Op::Interrupt`, `Op::ExecApproval`,
  `Op::UserInputAnswer`), `EventMsg` = Event 페이로드 enum. 둘 다 `non_exhaustive`.
- `Session`은 동시에 최대 1개의 `Task`만 실행. 병렬 작업은 **작업 스레드마다 Codex 인스턴스를 하나씩** 권장.
- 여기서 말하는 `Turn`은 App Server의 turn과 다릅니다 — **모델 요청 1사이클**(Task 내부 반복 단위)입니다.
- v1 와이어 호환을 위해 `EventMsg::TurnStarted`/`TurnComplete`는 `task_started`/`task_complete`로 직렬화되고,
  역직렬화는 `task_*`와 `turn_*`을 모두 수용합니다.
- `response_id`는 OpenAI `/responses`에 저장된 것과 동일 → 나중 세션에서 스레드 재개/포크에 사용.

> 지금 통합을 새로 만든다면 **protocol_v1이 아니라 App Server 프로토콜**을 쓰세요.
> Submission 페이로드는 특정 전송이 어댑터를 명시적으로 소유하지 않는 한 구현 세부사항으로 취급하라고 문서가 명시합니다.
