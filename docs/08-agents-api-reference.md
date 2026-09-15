# 08. Agents API 레퍼런스 (OpenAPI 스펙 기준)

> **정본 출처**: [`openai/openai-openapi`](https://github.com/openai/openai-openapi)의 `openapi.yaml`
> (약 3.5MB, `tags: Agents`). 가이드 문서가 아니라 **스펙에서 직접 추출**했습니다.
> 추출일 2026-09-15. 재현 방법은 문서 맨 아래.

## 0. 호출 규약

```bash
curl --no-buffer --fail-with-body https://api.openai.com/v1/agents/sessions \
  -H "OpenAI-Beta: agents=v1" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

- 베이스: `https://api.openai.com/v1`
- **`OpenAI-Beta: agents=v1` 헤더 필수** (퍼블릭 베타)
- SDK 경로: `client.beta.agents.sessions.*` (JS/Python/Ruby), `client.Beta.Agents.Sessions.*` (Go),
  `client.beta().agents().sessions()` (Java)
- 스트리밍 응답은 `text/event-stream`, 비스트리밍은 `application/json`

## 1. 엔드포인트 전체 (33개)

### 1.1 Agents — 재사용 가능한 저장된 에이전트

| Method | Path | operationId |
|---|---|---|
| GET | `/agents` | `listAgents` |
| POST | `/agents` | `createAgent` |
| GET | `/agents/{agent_id}` | `retrieveAgent` |
| POST | `/agents/{agent_id}` | `updateAgent` |
| DELETE | `/agents/{agent_id}` | `deleteAgent` |

> **주의**: 업데이트가 `PATCH`가 아니라 **`POST /agents/{agent_id}`** 입니다.

### 1.2 Sessions — 실행 인스턴스

| Method | Path | operationId |
|---|---|---|
| GET | `/agents/sessions` | `listAgentSessions` |
| POST | `/agents/sessions` | `createAgentSession` |
| GET | `/agents/sessions/{session_id}` | `retrieveAgentSession` |
| POST | `/agents/sessions/{session_id}` | `updateAgentSession` |
| DELETE | `/agents/sessions/{session_id}` | `deleteAgentSession` |

### 1.3 Session 입출력

| Method | Path | operationId |
|---|---|---|
| GET | `/agents/sessions/{session_id}/events` | `listAgentSessionEvents` |
| POST | `/agents/sessions/{session_id}/events` | `createAgentSessionEvents` |
| GET | `/agents/sessions/{session_id}/items` | `listAgentSessionItems` |
| GET | `/agents/sessions/{session_id}/turns` | `listAgentSessionTurns` |
| GET | `/agents/sessions/{session_id}/turns/{turn_id}` | `retrieveAgentSessionTurn` |

> **`POST .../events`가 유일한 입력 채널입니다.** 메시지 전송, 취소, 도구 결과 반환 모두 여기로 갑니다.

### 1.4 Artifacts — 완료된 턴이 발행한 파일

| Method | Path | operationId |
|---|---|---|
| GET | `/agents/sessions/{session_id}/artifacts` | `listAgentSessionArtifacts` |
| GET | `/agents/sessions/{session_id}/artifacts/{artifact_id}` | `retrieveAgentSessionArtifact` |
| GET | `/agents/sessions/{session_id}/artifacts/{artifact_id}/content` | `retrieveAgentSessionArtifactContent` |
| DELETE | `/agents/sessions/{session_id}/artifacts/{artifact_id}` | `deleteAgentSessionArtifact` |

### 1.5 Subagents — 읽기 전용

| Method | Path | operationId |
|---|---|---|
| GET | `/agents/sessions/{session_id}/subagents` | `listAgentSessionSubagents` |
| GET | `/agents/sessions/{session_id}/subagents/{subagent_id}` | `retrieveAgentSessionSubagent` |
| GET | `/agents/sessions/{session_id}/subagents/{subagent_id}/items` | `listAgentSessionSubagentItems` |
| GET | `/agents/sessions/{session_id}/subagents/{subagent_id}/turns` | `listAgentSessionSubagentTurns` |
| GET | `.../subagents/{subagent_id}/turns/{turn_id}` | `retrieveAgentSessionSubagentTurn` |
| GET | `.../subagents/{subagent_id}/turns/{turn_id}/items` | `listAgentSessionSubagentTurnItems` |

> 서브에이전트는 **생성/삭제 엔드포인트가 없습니다.** 메인 에이전트가 도구 호출로 만들고,
> API로는 관찰만 합니다.

### 1.6 Environments

| Method | Path | operationId |
|---|---|---|
| GET | `/agents/environments/{environment_id}` | `retrieveAgentEnvironment` |
| GET | `/agents/environments/{environment_id}/files` | `listAgentEnvironmentFiles` |
| POST | `/agents/environments/{environment_id}/files` | `createAgentEnvironmentFile` |
| GET | `/agents/environments/templates` | `listAgentEnvironmentTemplates` |
| POST | `/agents/environments/templates` | `createAgentEnvironmentTemplate` |
| GET | `/agents/environments/templates/{id}` | `retrieveAgentEnvironmentTemplate` |
| POST | `/agents/environments/templates/{id}` | `updateAgentEnvironmentTemplate` |
| DELETE | `/agents/environments/templates/{id}` | `deleteAgentEnvironmentTemplate` |

> 환경은 세션이 만들며 **직접 생성하는 엔드포인트가 없습니다.** 템플릿만 CRUD 가능합니다.

## 2. `POST /agents/sessions` — 세션 생성

### 요청 (`CreateAgentSessionParams`)

| 필드 | 타입 | 필수 | 설명 |
|---|---|:---:|---|
| `environment` | `EnvironmentParam` | ✅ | 인라인 실행 환경 또는 템플릿 참조 |
| `agent` | `SessionAgentConfigParam` | | `agent_id`와 함께 쓰면 저장된 에이전트를 **덮어씀**. `agent_id` 없으면 `model` 필수 |
| `agent_id` | `string` (≤64) | | 저장된 재사용 에이전트 ID. `agent` 생략 시 설정 그대로 사용 |
| `input` | `string` \| `InputMessageParam[]` | 조건부 | 초기 입력. 문자열은 단일 user 메시지의 축약 |
| `metadata` | `object` | | 최대 16쌍, 키 ≤64자, 값 ≤512자 |
| `vault_ids` | `string[]` | | 세션에 제공할 vault ID |
| `stream` | `boolean` (기본 `false`) | | SSE로 세션 이벤트 스트리밍 |

**`input`이 필수가 되는 조건** (스펙 원문):
> `environment.type`이 `none`일 때, 또는 `self_hosted`가 아닌 환경에서 `stream: true`일 때.
> self-hosted 및 비스트리밍 실행 환경에서는 선택.

### 응답

- `201` + `SessionResource` (JSON)
- `201` + `SessionEvent` 스트림 (`text/event-stream`, `stream: true`일 때)
- 에러: `400 401 403 404 409 500 503` — 전부 `ErrorResponse-2`

### `SessionAgentConfigParam`

| 필드 | 타입 | 설명 |
|---|---|---|
| `model` | `string` | 요청한 모델명이 그대로 보존됨 |
| `instructions` | `string \| null` | 에이전트의 **기본 base instruction에 덧붙는** 추가 지시문 |
| `reasoning` | `ReasoningParam \| null` | 생략=현행 유지, `null`=모델 기본 effort로 리셋 |
| `text` | `TextParam \| null` | 텍스트 생성 설정 |
| `service_tier` | `ServiceTierParam \| null` | 모델 요청 서비스 티어 |
| `multi_agent` | `MultiAgentConfigCurrentParam \| null` | 서브에이전트 설정 |
| `tools` | `AgentToolConfigParam[] \| null` | 생략=상속, `null`=전부 제거 |

> **병합 규칙 (스펙 원문)**: 생략한 필드는 `agent_id`에서 상속. 공급된 객체·배열은 **필드 전체를 치환**.
> `null`은 nullable 필드를 리셋.

### `EnvironmentParam` (discriminator: `type`)

**`none`** — 실행 환경 없이 에이전트만 실행
```json
{ "type": "none" }
```

**`openai_hosted`**
| 필드 | 설명 |
|---|---|
| `environment_template_id` | 인라인 설정보다 **먼저** 적용되는 재사용 템플릿. 생략 필드는 템플릿 상속. **네트워크 오버라이드는 템플릿 정책을 넓힐 수 없음** |
| `packages` | 설치할 패키지 (기본: 빈 목록) |
| `setup_commands` | 순서 있는 **기밀** 셋업 명령, 최대 16개. **명령 본문은 절대 반환되지 않음** |
| `network` | 네트워크 접근 정책 (기본: 활성) |
| `env` | 환경 변수, 최대 1024개 (키 ≤256자) |
| `capability_directories` | 에이전트에 노출할 capability 디렉터리, 최대 16384개 |
| `skills` | ID 참조 또는 인라인 ZIP, 최대 **200개** |
| `plugins` | 인라인 ZIP, 최대 **32개** |
| `files` | 시작 전 제공할 파일, 최대 **50개** |

**`self_hosted`**
| 필드 | 필수 | 설명 |
|---|:---:|---|
| `workspace_directory` | ✅ | 셀프호스팅 환경 내 **절대** 프로젝트 경로 |
| `capability_directories` | | capability 디렉터리 |

응답 쪽 `EnvironmentResourceSelfHosted`에는 `remote_url`과 `id`가 추가로 들어옵니다 —
이 둘을 `codex exec-server --remote <remote_url> --environment-id <id>`에 넣습니다.

### `MultiAgentConfigCurrentParam`

| 필드 | 필수 | 기본 | 설명 |
|---|:---:|---|---|
| `enabled` | ✅ | — | 서브에이전트 도구 활성화 |
| `max_concurrent_subagents` | | **6** | 동시 실행 상한 (코디네이터 제외), 최소 1 |

### `AgentToolConfigParam` (discriminator: `type`, 5종)

| type | 용도 |
|---|---|
| `function` | 커스텀 함수. `name`, `description`, `parameters`(JSON Schema) 필수 + `defer_loading`(기본 false) |
| `mcp` | MCP 서버 |
| `web_search` | 웹 검색 |
| `tool_search` | 도구를 지연 탐색 (토큰 절약) |
| `programmatic_tool_calling` | 프로그래매틱 병렬 호출 |

**`function`의 `defer_loading: true`** → 정의를 미리 로드하지 않고 `tool_search`로 발견. 컨텍스트 절약용.

**`mcp` 주요 필드**
| 필드 | 설명 |
|---|---|
| `server_label` | 툴 콜에서 서버를 식별하는 라벨 |
| `transport` | `McpTransportConfigParam` |
| `credential_id` | vault 자격증명. 서버 URL과 일치하는 자격증명이 정확히 하나면 생략 가능 |
| `allowed_tools` | 호출 허용 도구 목록. **생략 시 서버의 모든 도구 허용** |
| `required` | 첫 턴 전에 초기화되어야 하는지 (기본 `false`) |
| `request_metadata` | 요청에 포함할 메타데이터 |
| `connection_origin` | 아웃바운드 MCP HTTP 연결 출발지 선택 |

### `CreateSessionInputParam`

```json
// 축약형
"input": "Create tree.py and run it."

// 전체형
"input": [{
  "type": "message",
  "role": "user",
  "content": [
    { "type": "input_text",  "text": "..." },
    { "type": "input_image", "image_url": "https://..." }
  ]
}]
```

`role`은 **`user`만** 허용됩니다.

## 3. `SessionResource`

```ts
{
  id: string,
  object: "agent.session",
  created_at: number,           // Unix seconds
  last_active_at: number,
  status: "idle" | "in_progress" | "requires_action" | "failed",
  required_actions: SessionRequiredActionResource[],   // 최대 2000
  error: string | null,
  agent: SessionAgentResource,
  environment: EnvironmentResource,                    // none | openai_hosted | self_hosted
  vault_ids: string[],
  metadata: Record<string, string>,
  usage: TokenUsageResource | null,                    // best-effort, 변경될 수 있음
}
```

### `status` 의미 (스펙 원문)

| 값 | 의미 |
|---|---|
| `idle` | 진행 중인 턴이 없고 입력을 받을 준비 완료. **호스팅 환경은 아직 프로비저닝 중일 수 있음** |
| `in_progress` | 턴 처리 중 |
| `requires_action` | 하나 이상의 required action 대기 중 |
| `failed` | 세션 실패 |

> `idle`만으로 성공을 단정하지 마세요. 공식 가이드도 "status와 에이전트 출력을 함께 확인하라"고 명시합니다.

### `required_actions` (discriminator: `type`)

| type | 처리 |
|---|---|
| `function_call` | 함수를 실행하고 `turn_id` + `call_id`로 결과 제출 |
| `environment_connection` | `environment_id`로 실행기 연결 수립 |

### `TokenUsageResource`

```ts
{
  input_tokens: number,
  input_tokens_details: InputTokensDetailsResource,     // cached 포함
  output_tokens: number,
  output_tokens_details: OutputTokensDetailsResource,   // reasoning 포함
  total_tokens: number,
}
```

> **cached 토큰은 `input_tokens`에 포함**되고, **reasoning 토큰은 `output_tokens`에 포함**됩니다.
> 별도 가산이 아니라 내역(details)입니다.

## 4. `TurnResource`

```ts
{
  id: string,
  object: "agent.session.turn",
  session_id: string,
  agent_id: string,
  subagent_id: string | null,   // null = 메인 코디네이터가 실행
  status: "queued" | "in_progress" | "waiting" | "completed" | "failed" | "cancelled",
  created_at: number,
  started_at: number | null,
  completed_at: number | null,
  error: SessionTurnErrorResource | null,   // failed일 때만 non-null
  usage: TokenUsageResource | null,
}
```

`waiting` = 외부 입력 대기 중.

서브에이전트 턴의 `created_at`은 시작 시각을 쓰고, 없으면 완료 시각 → 서브에이전트 개시 시각 순으로 폴백합니다.

## 5. 턴 실패 코드 `SessionTurnErrorCodeResource` (17종)

| 코드 | 의미 |
|---|---|
| `context_length_exceeded` | 모델 컨텍스트 윈도우 초과 |
| `session_budget_exceeded` | 세션 사용량 예산 도달 |
| `usage_limit_exceeded` | 조직의 사용량/플랜/청구 한도 도달 |
| `credit_balance_exhausted` | API 크레딧 소진 |
| `rate_limit_exceeded` | 레이트 리밋 초과 |
| `server_overloaded` | 모델 서비스 일시 과부하 |
| `cyber_policy` | 안전 정책에 의해 거부 |
| `connection_failed` | 모델 서비스 연결 실패 |
| `server_error` | 모델 서비스 예기치 못한 오류 |
| `authentication_error` | 자격증명 무효 또는 권한 부족 |
| `invalid_request` | 입력/설정 무효 |
| `resource_not_found` | 요청한 모델/리소스 없음 |
| `sandbox_error` | 실행 환경에서 완료 실패 |
| `executor_version_incompatible` | **실행기 업그레이드 필요** |
| `active_turn_not_steerable` | 요청 실행 중에는 추가 입력 불가 |
| `request_timeout` | 모델 서비스 응답 전 타임아웃 |
| `internal_error` | 내부 오류 |

> 재시도 가능 계열(`server_overloaded`, `rate_limit_exceeded`, `connection_failed`, `request_timeout`)과
> 설정 수정이 필요한 계열(`invalid_request`, `authentication_error`, `executor_version_incompatible`)을
> 나눠서 처리하세요.

## 6. `POST /agents/sessions/{id}/events` — 입력 채널

### 요청 (`CreateSessionEventsParams`)

```json
{ "events": [ /* SessionInputParam, 최대 16384개 */ ] }
```

### `SessionInputParam` (discriminator: `type`, 3종)

**메시지 전송 / steering**
```json
{
  "type": "agent.session.input.message",
  "input": [{
    "role": "user",
    "content": [{ "type": "input_text", "text": "Your message" }]
  }]
}
```
> 턴이 **진행 중이면 steer**, **idle이면 새 턴 시작** (대화 컨텍스트 유지).

**취소**
```json
{ "type": "agent.session.input.cancel" }
```
> 진행 중인 턴만 중단. 세션과 이전 작업은 남습니다. (세션 삭제와 구분)

**도구 결과 반환**
```json
{ "type": "agent.session.input.tool_result", ... }
```
> `required_actions`의 `function_call`에 대한 응답. `turn_id` + `call_id`로 대응시킵니다.

## 7. 스트리밍 이벤트 `SessionEvent` (30종, discriminator: `type`)

### 세션 수명
```
agent.session.created
agent.session.in_progress
agent.session.idle
agent.session.requires_action
agent.session.failed
error
```

### 환경
```
agent.session.environment.pending
agent.session.environment.connected
agent.session.environment.ready
agent.session.environment.disconnected
agent.session.environment.failed
```

### 턴 수명
```
agent.session.turn.created
agent.session.turn.in_progress
agent.session.turn.completed
agent.session.turn.failed
agent.session.turn.cancelled
```

### 턴 내용 스트리밍
```
agent.session.turn.item.added
agent.session.turn.item.done
agent.session.turn.content_part.added
agent.session.turn.content_part.done
agent.session.turn.output_text.delta
agent.session.turn.output_text.done
agent.session.turn.reasoning_summary_part.added
agent.session.turn.reasoning_summary_part.done
agent.session.turn.reasoning_summary_text.delta
agent.session.turn.reasoning_summary_text.done
```

### 명령 출력
```
agent.output.command_execution_output.delta
```
> 이것만 `agent.session.*`이 아니라 **`agent.output.*`** 네임스페이스입니다. 파서에서 놓치기 쉬운 지점.

### 서브에이전트
```
agent.session.subagent.created
agent.session.subagent.active
agent.session.subagent.closed
```

### 에러 이벤트 (`SessionEventError`)

```json
{
  "type": "error",
  "event_id": "event_123",
  "session_id": "sess_123",
  "error": {
    "type": "server_error",
    "code": null,
    "message": "The session failed due to an internal server error.",
    "param": null
  }
}
```
> `SessionErrorResource`는 "Responses API 스트리밍 에러와 동일한 공개 필드"를 가진다고 스펙에 명시되어 있습니다.

> 스트림은 **idle 이벤트를 넘어서도 열린 채 유지**되므로 대기 중인 작업을 놓치지 않습니다.

## 8. 턴 아이템 `SessionTurnItemResource` (14종)

```
message                  reasoning
function_call            function_call_output
agent_message            mcp_call
web_search_call          command_execution
create_subagent_call     send_subagent_input_call
resume_subagent_call     wait_for_subagents_call
interrupt_subagent_call  close_subagent_call
```

뒤쪽 6개가 **멀티에이전트 조정 행위**입니다. 스트림에서 이것들을 보면 위임이 일어나는 중입니다.

## 9. Artifacts

```ts
SessionArtifactResource = {
  id: string,
  object: "agent.session.artifact",
  session_id: string,
  environment_id: string,
  turn_id: string,          // 이 아티팩트를 발행한 완료된 턴
  path: string,             // 실행 환경 내 원래 절대 경로
  size_bytes: number,
  created_at: number,
}
```

> **"완료된 호스팅 세션 턴이 발행한 불변 파일"** — 에이전트가 만든 산출물(리포트, CSV, 스크린샷 등)을
> 꺼내는 공식 경로입니다. 내용은 `GET .../artifacts/{id}/content`.

## 10. 페이지네이션 (모든 list 엔드포인트 공통)

**쿼리 파라미터**: `limit` (≥1), `order` (`asc`/`desc`, 기본 `desc`), `after` (커서)
`GET /agents/sessions`는 `agent_id` 필터도 받습니다. `GET .../artifacts`는 `environment_id` 필터.

**응답 봉투**
```ts
{
  object: "list",
  data: T[],              // 최대 2000
  first_id: string | null,
  last_id: string | null,
  has_more: boolean,
}
```

SDK 헬퍼: `hasNextPage()` / `getNextPage()`.

## 11. 최소 동작 예제

### 세션 생성 + 스트리밍 (curl)

```bash
curl --no-buffer --fail-with-body https://api.openai.com/v1/agents/sessions \
  -H "OpenAI-Beta: agents=v1" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {
      "model": "gpt-6-astra",
      "instructions": "Write clean code, run it, and report the actual output."
    },
    "environment": { "type": "openai_hosted" },
    "input": "Create tree.py, a Python script that prints a readable tree of the files in the current directory. Run it and show me the output.",
    "stream": true
  }'
```

### Python

```python
from openai import OpenAI

with OpenAI() as client:
    with client.beta.agents.sessions.create(
        agent={
            "model": "gpt-6-astra",
            "instructions": "Write clean code, run it, and report the actual output.",
        },
        environment={"type": "openai_hosted"},
        input="Create tree.py ... Run it and show me the output.",
        stream=True,
    ) as events:
        for event in events:
            print(event.to_json(indent=None), flush=True)
```

### 멀티에이전트 (JavaScript)

```javascript
import OpenAI from "openai";
const client = new OpenAI();

const events = await client.beta.agents.sessions.create({
  agent: {
    model: "gpt-6-astra",
    instructions: "Delegate each release to a separate subagent. ...",
    multi_agent: { enabled: true, max_concurrent_subagents: 2 },
  },
  environment: { type: "none" },
  input: "Release A: ... Release B: ...",
  stream: true,
});

for await (const event of events) {
  console.log(JSON.stringify(event));
}
```

### 후속 메시지 / 취소 / 결과 조회

```javascript
// 이어서 말하기 (진행 중이면 steer, idle이면 새 턴)
await client.beta.agents.sessions.events.create(sessionId, {
  events: [{
    type: "agent.session.input.message",
    input: [{ role: "user", content: [{ type: "input_text", text: "Your message" }] }],
  }],
});

// 진행 중인 턴 취소 (세션은 유지)
await client.beta.agents.sessions.events.create(sessionId, {
  events: [{ type: "agent.session.input.cancel" }],
});

// 저장된 작업 조회
const items = await client.beta.agents.sessions.items.list(sessionId, {
  order: "asc",
  limit: 100,
});

// 어떤 에이전트가 이 명령을 실행했나
const turn = await client.beta.agents.sessions.turns.retrieve(
  command.turn_id, { session_id: sessionId }
);
console.log(turn.subagent_id);   // null = 메인 코디네이터
```

### 셀프호스팅 환경

```json
{
  "agent": { "model": "gpt-6-astra", "instructions": "..." },
  "environment": { "type": "self_hosted", "workspace_directory": "/workspace" }
}
```

```bash
# 응답의 environment.remote_url / environment.id를 사용
codex exec-server \
  --remote "<session.environment.remote_url>" \
  --environment-id "<session.environment.id>"
```

## 12. 서브에이전트 상속 규칙

**상속되는 것**
- 설정된 MCP 도구 + 자격증명 + `allowed_tools`
- 웹 검색 설정
- 환경의 파일과 CLI 도구

**상속되지 않는 것**
- **function tools를 사용할 수 없음**

**위임 판단 기준** (공식 가이드):
> 독립적인 과업(서로 다른 문서 검토, 서로 다른 실패 원인 조사)에 서브에이전트를 쓰고,
> 의존적인 단계와 짧은 과업은 메인 에이전트에 남기세요.

## 13. 실무 체크리스트

- [ ] `OpenAI-Beta: agents=v1` 헤더 누락 확인 (베타)
- [ ] **`session_id`를 애플리케이션 DB에 저장** — 재시작·연결 끊김 후 retrieve로 복구
- [ ] `status`가 `requires_action`이면 `required_actions` 전부 처리 후에야 진행됨
- [ ] `agent.session.idle`만으로 성공 단정 금지 — 턴 status와 출력을 함께 확인
- [ ] `agent.output.command_execution_output.delta`는 다른 네임스페이스 — 파서 분기 주의
- [ ] `agent`/`agent_id` 병합 규칙: 객체·배열은 **전체 치환**, `null`은 리셋, 생략은 상속
- [ ] `environment_template_id` + 인라인 설정 혼용 시 **네트워크 정책은 넓힐 수 없음**
- [ ] `setup_commands` 본문은 응답에 절대 안 돌아옴 — 별도로 관리
- [ ] `usage`는 best-effort이며 **나중에 값이 바뀔 수 있음**. 정산 근거로 쓸 때 주의
- [ ] `executor_version_incompatible` → 셀프호스팅 실행기(`@openai/codex@alpha`) 업그레이드 경로 준비
- [ ] 산출물은 `items`가 아니라 **`artifacts`** 로 꺼냄
- [ ] 취소는 세션 삭제가 아니라 `agent.session.input.cancel`

## 14. 재현 방법

```bash
S=/tmp/openai-spec && mkdir -p $S
curl -sL https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml -o $S/openapi.yaml

# 엔드포인트 목록
grep -nE '^  /agents' $S/openapi.yaml

# 스키마 하나 열어보기
L=$(grep -n '^    CreateAgentSessionParams:' $S/openapi.yaml | cut -d: -f1)
sed -n "${L},$((L+70))p" $S/openapi.yaml

# 이벤트 타입 전체
L=$(grep -n '^    SessionEvent:' $S/openapi.yaml | cut -d: -f1)
sed -n "${L},$((L+130))p" $S/openapi.yaml | grep -E '^        - agent\.|^        - error'
```
