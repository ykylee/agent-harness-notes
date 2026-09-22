---
type: concept
status: active
last_ingested_from: docs/16-responses-chat-adapter.md + docs/07-harness-engineering.md + docs/99-sources.md
related_pages: [concepts/stateless-conversation-wire, concepts/wire-protocol-boundary, concepts/harness-engineering, concepts/primary-source-verification]
created: 2026-09-22
updated: 2026-09-22
---

# Retained Reasoning — 하네스가 성능 변수인 이유

- 문서 목적: 유지된 추론(retained reasoning)이 최적화가 아니라 **설계의 하중 부재**인 이유와, Chat Completions 로 건너갈 때 구조적으로 사라지는 이유를 정리한다.
- 범위: 기전, Chat Completions 의 부재, 실제로 잃는 것, 설계 귀결
- 1차 출처: `codex-rs/protocol/src/models.rs`, `codex-rs/core/src/client.rs`, "Codex as a platform" 포스트
- 최종 수정일: 2026-09-22

## §1 TL;DR  {#s1-tldr}

| # | 항목 | 값 |
|---|---|---|
| 1 | 무엇인가 | 모델의 이전 추론을 다음 turn 에 **되돌려 보내** 사슬을 잇는 것 |
| 2 | 통로 | `Reasoning.encrypted_content` — **1급 입력 item** |
| 3 | 요청 방식 | `include: ["reasoning.encrypted_content"]` — **조건 없이 항상** |
| 4 | Chat Completions | **대응물 없음.** 구조적으로 불가능 |
| 5 | 손실의 크기 | **대상 모델이 추론하는 만큼에 비례**. 비추론 모델이면 0 |
| 6 | 성격 | 성능 최적화가 아니라 **기능 퇴행** |

## §2 기전  {#s2-mechanism}

```rust
Reasoning {
    id: Option<ResponseItemId>,
    summary: Vec<ReasoningItemReasoningSummary>,
    content: Option<Vec<ReasoningItemContent>>,
    encrypted_content: Option<String>,
    internal_chat_message_metadata_passthrough: Option<...>,
}
```

`store: false` 이므로 ([[concepts/stateless-conversation-wire]]) Codex 는 매 turn 대화 전체를
재전송한다. **모델 자신의 이전 추론도 함께 보내야 하고**, 그 운반체가 `encrypted_content` 다.
이것이 stateless 클라이언트가 추론 모델의 사슬을 다단계 과업 내내 유지하는 방식이다.

그리고 Codex 는 이를 무조건 요청한다:

```rust
let include = vec!["reasoning.encrypted_content".to_string()];
```

기능 게이트도 없고, 모델별 조건도 없다. **항상.**

## §3 Chat Completions 에는 자리가 없다  {#s3-no-slot}

| 축 | Responses | Chat Completions |
|---|---|---|
| 요청측 노력 지정 | `reasoning.effort` | `reasoning_effort` ✅ |
| **출력측 표현** | `Reasoning` item | **없음** ❌ |
| 다음 요청에 되돌릴 슬롯 | `input[]` 의 `Reasoning` 변형 | **없음** ❌ |
| 요약 채널 | `reasoning.summary` | 없음 ❌ |

`ChatCompletionStreamResponseDelta` 에는 reasoning 필드가 없고, 불투명한 추론 blob 을 다음 요청에
실어 보낼 assistant-message 슬롯도 없다.

일부 서드파티 서버가 비표준 `reasoning_content` 필드를 내보낸다(vLLM/DeepSeek 생태계 관행). 그러나
OpenAI 스펙에 없고, 암호화돼 있지 않으며, **불투명 토큰으로 왕복되지 않는다**. 어댑터가 표시용
*요약*으로 노출할 수는 있어도 연속성을 복원하지는 못한다.

## §4 실제로 잃는 것  {#s4-what-is-lost}

추론은 **turn 경계에서 버려진다**. 매 turn 모델의 추론이 처음부터 다시 시작한다.

그리고 이것이 바로 하네스 재료가 큰 이득으로 지목한 바로 그 능력이다:

> "Harness design can materially change results: on ARC-AGI-3, retained reasoning and context
> compaction raised GPT-5.6 Sol's score from **13.3% to 38.3%** while reducing output tokens
> **sixfold**."

두 개의 **하네스 수준 설정** — 유지된 추론과 컨텍스트 압축 — 이지 모델 교체가 아니다.

> 📌 **출처 등급**: 이 수치는 처음 2차 출처에서 나왔으나, "Codex as a platform" 포스트 본문에
> 그대로 실려 있고 전용 글(`openai.com/index/how-two-settings-tripled-our-arc-agi-3-scores/`)을
> 링크하고 있어 **1차로 승격**됐다. 등급 이력은 [[concepts/primary-source-verification]].

정확한 수치가 무엇이든 결론은 같다 — **유지된 추론은 최적화가 아니라 설계의 하중 부재다.**

## §5 설계 귀결  {#s5-consequences}

| # | 귀결 |
|---|---|
| 1 | 추론 유지를 **전역 가정이 아니라 프로바이더별 capability** 로 다룬다. `ModelProviderInfo` 에 이미 그 모양이 있다 (`supports_websockets`, `supports_standalone_web_search`) — `supports_retained_reasoning` 을 더하고 하네스가 적응하게 한다 |
| 2 | Chat 백엔드 프로바이더에서는 Responses 네이티브 도구 item 5종을 비활성화하고, 그 사실을 **UI 에 보이게** 한다. 조용한 부재로 두지 않는다 |
| 3 | `include` 를 조건부로 만든다. Codex 는 `reasoning.encrypted_content` 를 하드코딩하지만 다중 프로바이더 하네스는 그럴 수 없다 |
| 4 | 어댑터를 **지을지 말지**의 기준: 목표가 "Chat Completions 만 말하는 서드파티 모델 지원"이면 짓는다. "OpenAI 추론 모델을 Chat Completions 로 돌리기"면 짓지 않는다 — 이미 잘 되는 경로의 엄밀히 열등한 판본에 어댑터 복잡도를 지불하는 셈이다 |

## §6 다음에 읽을 문서  {#s6-next}

- [[concepts/stateless-conversation-wire]] — 어댑터를 쉽게 만드는 반대쪽
- [[concepts/harness-engineering]] — 하네스를 성능 변수로 보는 관점
- [[concepts/provider-as-data]] — capability 를 데이터로 표현하기
- 원문: [`docs/16-responses-chat-adapter.md`](../../../docs/16-responses-chat-adapter.md) §5
