---
type: concept
status: active
last_ingested_from: docs/16-responses-chat-adapter.md
related_pages: [concepts/wire-protocol-boundary, concepts/retained-reasoning, concepts/thread-turn-item]
created: 2026-09-22
updated: 2026-09-22
---

# Stateless Conversation Wire — `store: false` 가 공짜로 주는 것

- 문서 목적: Codex 가 모델에게 대화를 보내는 방식이 왜 완전 stateless 인지, 그것이 어댑터·프록시 설계에 무엇을 면제해 주는지 정리한다.
- 범위: 실제 요청 payload, statelessness 의 증거, 면제되는 설계 부담, 상수로 고정된 필드
- 1차 출처: `codex-rs/codex-api/src/common.rs`, `codex-rs/core/src/client.rs`
- 최종 수정일: 2026-09-22

## §1 TL;DR  {#s1-tldr}

| # | 항목 | 값 |
|---|---|---|
| 1 | `store` | **`false`** — 항상 |
| 2 | `previous_response_id` | HTTP payload 에는 **없다** (WebSocket 변형에만 존재하고, 변환 시 `None`) |
| 3 | 결론 | **전체 대화가 매 turn 마다 `input[]` 로 재전송된다** |
| 4 | 면제되는 것 | 세션 저장소 · response-id 레지스트리 · 만료 처리 · 정리 경로 |
| 5 | 확장성 | 수평 확장이 공짜 |

## §2 실제로 보내는 payload  {#s2-actual-payload}

`ResponsesApiRequest` — 필드 17개.

```rust
pub struct ResponsesApiRequest {
    pub model: String,
    pub instructions: String,            // 비었으면 생략
    pub input: Vec<ResponseItem>,
    pub tools: Option<ResponsesApiTools>,
    pub tool_choice: String,
    pub parallel_tool_calls: bool,
    pub reasoning: Option<Reasoning>,
    pub store: bool,
    pub stream: bool,
    pub stream_options: Option<StreamOptions>,
    pub include: Vec<String>,
    pub service_tier: Option<String>,
    pub prompt_cache_key: Option<String>,
    pub text: Option<TextControls>,
    pub client_metadata: Option<HashMap<String, String>>,
    pub access_programs: Option<AccessPrograms>,
}
```

실제로 채워 넣는 값 (`client.rs`):

```rust
tool_choice: "auto".to_string(),
store: false,
stream: true,
include: vec!["reasoning.encrypted_content".to_string()],
reasoning: Some(reasoning),          // 항상 존재
```

## §3 상수로 고정된 세 필드가 줄이는 일  {#s3-constants}

| 필드 | 값 | 없어지는 작업 |
|---|---|---|
| `tool_choice` | 항상 `"auto"` | `required` / 지정 도구 매핑 구현 불필요 |
| `stream` | 항상 `true` | 비스트리밍 경로 전체 생략 가능 |
| `instructions` | 최상위 문자열 | `system`/`developer` 메시지로 앞에 붙이면 끝 |

## §4 왜 이것이 좋은 소식인가  {#s4-why-good}

Responses API 를 흉내 낼 때 보통 가장 어려운 부분이 **세션 상태 에뮬레이션**이다. `store: false` 와
`previous_response_id` 부재가 그 문제 자체를 없앤다.

어댑터는 **요청 하나를 상위 요청 하나로 바꾸는 순수 함수**가 된다.

> ⚠️ 설계 규율: **어댑터를 stateless 로 유지하라.** response-id 저장소를 넣는 순간,
> `store: false` 가 공짜로 건네준 어려운 문제를 스스로 되살리는 것이다.

## §5 비-OpenAI 경로는 입력을 미리 정리해 준다  {#s5-non-openai-path}

```rust
if !is_openai {
    for item in &mut input {
        item.clear_internal_chat_message_metadata_passthrough();
        if let ResponseItem::FunctionCall { encrypted_function_args, .. } = item {
            *encrypted_function_args = None;
        }
    }
}
```

프로바이더 이름이 `openai` 가 **아니면** Codex 가 OpenAI 전용 passthrough 메타데이터와 암호화된 함수
인자를 보내기 전에 벗겨낸다. 어댑터는 더 깨끗한 입력을 공짜로 받는다.

> 레버는 프로바이더의 **`name`** 하나다. 프록시를 가리키면서 이름을 `openai` 로 둔 프로바이더는
> OpenAI 경로를 타고, 어댑터가 직접 벗겨내야 할 필드를 그대로 받는다.

## §6 stateless 라도 남는 것  {#s6-what-remains}

statelessness 는 *전송*의 성질이지 *능력*의 보존이 아니다. 매 turn 전체 대화를 재전송한다는 것은
곧 **모델 자신의 이전 추론도 재전송해야 한다**는 뜻이고, 그 통로가 `encrypted_content` 다.
이 통로가 없는 wire 로 건너가면 무엇이 무너지는지는 [[concepts/retained-reasoning]].

## §7 다음에 읽을 문서  {#s7-next}

- [[concepts/retained-reasoning]] — stateless 가 해결하지 못하는 유일한 것
- [[concepts/wire-protocol-boundary]] — 이 payload 를 받는 경계
- 원문: [`docs/16-responses-chat-adapter.md`](../../../docs/16-responses-chat-adapter.md) §1
