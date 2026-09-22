---
type: concept
status: active
last_ingested_from: docs/15-model-providers.md + docs/16-responses-chat-adapter.md
related_pages: [concepts/provider-as-data, concepts/stateless-conversation-wire, concepts/retained-reasoning, concepts/harness]
created: 2026-09-22
updated: 2026-09-22
---

# Wire Protocol Boundary — 코어 재사용 가능성을 가르는 경계

- 문서 목적: Codex core 가 어떤 wire protocol 을 전제하는지, 그 전제가 커스텀 하네스에 무엇을 강제하는지 정리한다.
- 범위: `WireApi` 의 현재 상태, 세 가지 탈출로, 프록시 선례, 두 가지 요청 형태
- 1차 출처: `codex-rs/model-provider-info/src/lib.rs` (710줄 직접 독해), `codex-rs/core/src/client.rs`
- 최종 수정일: 2026-09-22

## §1 TL;DR  {#s1-tldr}

| # | 항목 | 값 |
|---|---|---|
| 1 | `WireApi` 의 변형 수 | **정확히 1개 — `Responses`** |
| 2 | Chat Completions | **제거됨.** 설정하면 명시적 에러 |
| 3 | 함의 | `codex app-server` 를 그대로 감싸서 Chat Completions 하네스를 얻을 수 **없다** |
| 4 | 권장 탈출로 | **프로바이더 모양의 프록시** (fork 아님) |
| 5 | 요청 형태 | **둘이다** — classic 과 `responses_lite` |
| 6 | 첫 결정 | 이 경계를 **가장 먼저** 정한다. 나머지가 전부 여기 딸린다 |

## §2 Chat Completions 는 사라졌다  {#s2-chat-removed}

```rust
pub enum WireApi {
    /// The Responses API exposed by OpenAI at `/v1/responses`.
    #[default]
    Responses,
}
```

옛 값을 설정하면 의도적으로 설계된 에러가 난다:

```
`wire_api = "chat"` is no longer supported.
How to fix: set `wire_api = "responses"` in your provider config.
More info: https://github.com/openai/codex/discussions/7782
```

제거는 enum 을 넘어섰다 — `ollama-chat` 프로바이더 id 도 함께 퇴역했고, `ollama` 는 이제
`WireApi::Responses` 로 동작한다.

## §3 세 가지 탈출로  {#s3-escape-routes}

| 방법 | 어떻게 | 비용 |
|---|---|---|
| **앞단 어댑터** | `/v1/responses` 를 받아 상위 `/v1/chat/completions` 로 번역하는 로컬 프록시. `model_providers` 항목이 이를 가리키게 한다 | 낮음~중간. 번역 충실도는 내 책임 |
| **wire API 재추가** | fork 해서 `Chat` 변형과 요청/응답 매핑을 복원 | 중간~높음. upstream 과 영구 분기 |
| **모델 계층 자체 소유** | 프로토콜 설계만 가져오고 코어는 직접 작성 | 높음. 대신 wire protocol 제약이 아예 없다 |

## §4 프록시 선례 — 이 모양이 동작한다는 증거  {#s4-proxy-precedent}

저장소가 직접 `codex-responses-api-proxy` 를 싣고 있다.

```toml
[model_providers.codex-responses-api-proxy]
name = 'codex-responses-api-proxy'
base_url = 'http://127.0.0.1:60001/v1'
wire_api = 'responses'
```

이 프록시의 목적은 요청/응답 덤프이지 프로토콜 번역이 아니다. 그러나 모양을 증명한다 —
**`base_url` 에서 Responses 를 말하는 것은 무엇이든 유효한 프로바이더다.** Responses→Chat 어댑터는
정확히 이 자리에 꽂힌다.

## §5 요청 형태는 하나가 아니다 — `responses_lite`  {#s5-responses-lite}

`model_info.use_responses_lite` 가 켜지면 요청이 다르게 조립된다.

| 항목 | classic | lite |
|---|---|---|
| 최상위 `instructions` | base instructions 문자열 | **빈 문자열** |
| 최상위 `tools` | 도구 JSON | **`None`** |
| 도구·지시의 실제 위치 | 최상위 필드 | input 배열 앞에 `ResponseItem::AdditionalTools { role: "developer", tools }` + base-instructions 메시지를 prepend |
| item id | — | thread id + 직렬화 payload 에 대한 `Uuid::v5` (재시도·재개에도 동일) |

> ⚠️ 어댑터는 **두 형태를 모두 처리해야** 한다. 아니면 도구도 지시도 없는 요청을 보고 둘 다 조용히
> 버린다. `AdditionalTools` 는 lite 모드에서 **버릴 수 있는 항목이 아니라 그 자체가 도구 목록**이다.

### §5.1 어느 모델이 lite 인가  {#s5-1-which-models}

`codex-rs/models-manager/models.json` 의 9개 항목 기준:

| `use_responses_lite` | 모델 |
|---|---|
| **true** | `gpt-6-astra`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-daybreak-blue-latest`, `gpt-daybreak-red-latest`, `codex-auto-review` |
| false | `gpt-5.5`, `gpt-5.4` |

**현세대 모델은 전부 lite 다.** classic 만 처리하는 어댑터는 레거시 경로를 향해 쓰는 셈이다.

### §5.2 slug → flag 해석과 그 함정  {#s5-2-slug-matching}

`construct_model_info_from_candidates` 는 순서대로 세 가지를 시도한다.

| 순서 | 방법 |
|---|---|
| 1 | **최장 접두 일치** — `model.starts_with(&candidate.slug)` 인 후보 중 가장 긴 slug 가 이긴다 |
| 2 | **한 단계 namespace 제거** — `namespace/model` 을 분리해 재시도 |
| 3 | **fallback** — 경고 로그, `used_fallback_model_metadata: true`, `use_responses_lite: false`, 일반 `context_window` 272,000 |

```
"gpt-6-astra-turbo"        → "gpt-6-astra" 에 접두 일치 → use_responses_lite = true
"myprovider/gpt-6-astra"   → namespace 제거 후 동일 일치 → use_responses_lite = true
"llama-3.3-70b"            → 일치 없음 → fallback        → use_responses_lite = false
```

> **함정**: 서드파티 모델에 OpenAI 모양의 접두를 붙여 이름 지으면 **요청 형태가 조용히 바뀐다.**
> `config.toml` 에는 이를 덮어쓸 키가 없다 — 통제점은 **`model_catalog_json`** 뿐이다.
> 지원하는 모델마다 명시적 항목을 담은 카탈로그를 실어라. 접두 일치의 운에 기대지 말고,
> fallback 에도 기대지 마라.

## §6 다음에 읽을 문서  {#s6-next}

- [[concepts/stateless-conversation-wire]] — 어댑터를 쉽게 만드는 쪽
- [[concepts/retained-reasoning]] — 어댑터가 잃는 것
- [[concepts/provider-as-data]] — 프로바이더를 코드가 아니라 데이터로 모델링하기
- 원문: [`docs/15-model-providers.md`](../../../docs/15-model-providers.md), [`docs/16-responses-chat-adapter.md`](../../../docs/16-responses-chat-adapter.md)
