# 99. 출처 및 검증 상태

조사일: 2026-09-14

## A. 1차 출처 — 직접 확인함 ✅

### 리포지터리 (가장 신뢰도 높음, 생성된 스키마가 정본)

| 경로 | 내용 |
|---|---|
| [`openai/codex` README](https://github.com/openai/codex/blob/main/README.md) | 설치, 인증, 문서 링크 |
| [`codex-rs/app-server/README.md`](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md) | 최근 프로토콜 변경사항, user verification, attachment, plugin 설정 |
| [`codex-rs/docs/protocol_v1.md`](https://github.com/openai/codex/blob/main/codex-rs/docs/protocol_v1.md) | 레거시 SQ/EQ 코어 프로토콜 |
| `codex-rs/app-server-protocol/schema/typescript/ClientRequest.ts` | **클라이언트 메서드 104개** |
| `codex-rs/app-server-protocol/schema/typescript/ServerRequest.ts` | **서버 요청 10개** |
| `codex-rs/app-server-protocol/schema/typescript/ServerNotification.ts` | **서버 알림 84개** |
| `.../InitializeParams.ts`, `InitializeResponse.ts`, `InitializeCapabilities.ts`, `ClientNotification.ts` | 핸드셰이크 |
| `.../v2/ThreadStartParams.ts`, `ThreadStartResponse.ts`, `TurnStartParams.ts`, `TurnStartResponse.ts`, `ThreadItem.ts` | 페이로드 |
| [`sdk/typescript/README.md`](https://github.com/openai/codex/blob/main/sdk/typescript/README.md) | TS SDK 전문 |
| [`sdk/python/README.md`](https://github.com/openai/codex/blob/main/sdk/python/README.md), `docs/getting-started.md` | Python SDK 전문 |

라이선스: **Apache-2.0**

### OpenAPI 스펙 — Agents API의 정본

| 경로 | 내용 |
|---|---|
| [`openai/openai-openapi` → `openapi.yaml`](https://github.com/openai/openai-openapi/blob/master/openapi.yaml) | 약 3.5MB. `tags: Agents` 아래 **엔드포인트 33개**와 전체 스키마 |

여기서 직접 추출한 것: 엔드포인트 경로/메서드/operationId, `CreateAgentSessionParams`,
`SessionAgentConfigParam`, `EnvironmentParam`(3 variant), `AgentToolConfigParam`(5종),
`MultiAgentConfigCurrentParam`, `SessionResource`, `TurnResource`, `TokenUsageResource`,
`SessionEvent`(30종), `SessionInputParam`(3종), `SessionTurnItemResource`(14종),
`SessionTurnErrorCodeResource`(17종), `SessionArtifactResource`, 페이지네이션 봉투.

→ [08-agents-api-reference.md](08-agents-api-reference.md)

### 공식 문서

| URL | 내용 |
|---|---|
| <https://developers.openai.com/codex/app-server> (→ learn.chatgpt.com/docs/app-server) | App Server 공식 가이드 |
| <https://developers.openai.com/codex/sdk> (→ learn.chatgpt.com/docs/codex-sdk) | SDK 개요 |
| <https://developers.openai.com/codex/noninteractive> (→ learn.chatgpt.com/docs/non-interactive-mode) | `codex exec` |
| <https://developers.openai.com/api/docs/guides/agents-api/overview> | Agents API 개요 |
| <https://developers.openai.com/api/docs/guides/agents-api/sessions/manage> | 세션 관리 |
| <https://developers.openai.com/api/docs/guides/agents-api/environments/self-hosted> | 셀프호스팅 실행기 |
| <https://developers.openai.com/api/docs/guides/agents/sandboxes> | 샌드박스 에이전트 (Agents SDK) |
| <https://developers.openai.com/api/docs/guides/agents-api/quickstart> | Agents API 퀵스타트 (curl/Python 예제) |
| <https://developers.openai.com/api/docs/guides/agents-api/multi-agent> | 멀티에이전트 (6개 언어 예제) |
| <https://developers.openai.com/api/docs/guides/agents-api/observability> | 관측 · 토큰 사용량 |
| <https://developers.openai.com/blog/codex-as-a-platform> | "Codex as a platform" 블로그 |

> 참고: `developers.openai.com/codex/*` 경로는 현재 `learn.chatgpt.com/docs/*`로 308 리다이렉트됩니다.

### 공식 블로그 (openai.com은 이 환경에서 403 → 전문 미러로 확인)

| 글 | 저자 | 날짜 |
|---|---|---|
| [Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/) | Celia Chen | 2026-02-04 |
| [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) | Ryan Lopopolo | 2026-02-11 |

두 글은 [`newton20/harness-engineering-kb`](https://github.com/newton20/harness-engineering-kb) 저장소의
전문 미러(`raw/openai-com-index-*.md`)로 읽었습니다. **미러는 3자 제공이므로 결정적 인용 시 원문 재확인 권장.**
다만 본문 내 코드 예제·각주·저자·날짜가 모두 일관되어 신뢰도는 높습니다.

## B. 2차 출처 — 맥락/타임라인 확인용 ⚠️

이 문서들에서 가져온 사실은 본문에서 "2차 출처 기준"으로 표시했습니다.

| URL | 가져온 내용 |
|---|---|
| <https://www.marktechpost.com/2026/09/10/openai-launches-the-agents-api-in-public-beta-putting-the-codex-harness-behind-one-api-call/> | Agents API 베타 날짜, 파트너 목록, 가격 구조 |
| <https://kenhuangus.substack.com/p/from-software-engineering-to-harness> | "Codex as a platform" 게시일(2026-08-19), ARC-AGI-3 수치 |
| <https://codex.danielvaughan.com/2026/04/15/codex-app-server-complete-guide/> | thread 30분 유휴 언로드, `-32001` 백프레셔, WebSocket 포트 |
| <https://www.opensourceforu.com/2026/08/openai-open-sources-codex-harness/> | 오픈소스 공개일(2026-08-20), Apache-2.0 |
| <https://blog.sandbase.ai/openai-codex-app-server-harness-2026/> | 일반 맥락 |

### 미검증 / 상충 항목

| 항목 | 상태 |
|---|---|
| "Codex as a platform" 정확한 게시일 | 2차 출처가 **8/19 vs 8/20**으로 엇갈림. 본문에서는 "2026년 8월"로 표기 |
| ARC-AGI-3에서 GPT-5.6 Sol 13.3% → 38.3%, 출력 토큰 1/6 | 2차 출처 인용. **원문 미확인** |
| App Server WebSocket 기본 포트 `127.0.0.1:9090`, CSRF(Origin 헤더 거부) | 2차 출처만 언급. 리포/공식문서에서 미확인 |
| thread 30분 유휴 언로드 | 2차 출처만 언급 |
| JSON-RPC `-32001` (서버 과부하) | 2차 출처만 언급 |
| `initialize` 응답에 `serverInfo`/`capabilities`가 있다는 서술 | **틀림.** 생성 스키마상 `InitializeResponse`는 `userAgent`, `codexHome`, `platformFamily`, `platformOs` 4필드. 리포 기준을 따름 |
| Agents API 모델 ID (`gpt-6-astra`, `gpt-5.6-terra`) | 문서 예제에 등장한 값. 가용 모델 목록은 별도 확인 필요 |
| Agents API 파트너 샌드박스 9곳 목록 | 2차 출처(MarkTechPost)와 Agents SDK 문서의 클라이언트 목록이 부분 불일치 (DigitalOcean·Oracle은 SDK 클라이언트 표에 없음). Agents API 환경 옵션과 Agents SDK 샌드박스 제공자는 **서로 다른 목록일 수 있음** |
| `/agents/environments/{id}/files` POST의 요청 스키마 | 엔드포인트 존재만 확인, 본문 스키마 미추출 |
| vault (`vault_ids`, `credential_id`) 관리 엔드포인트 | Agents 태그 밖에 있어 이번 추출 범위에서 제외 |

## C. 이 환경에서 접근 실패한 것

- `openai.com/index/*` — HTTP 403 (WebFetch, curl + 브라우저 UA 모두). 미러로 우회함
- `developers.openai.com/api/reference/resources/agents/...` — 404. **OpenAPI 스펙으로 대체 확보(더 정확)**

## D. 재현 방법

```bash
# 프로토콜 메서드 목록을 직접 세보기
B=https://raw.githubusercontent.com/openai/codex/main/codex-rs/app-server-protocol/schema/typescript
curl -s $B/ClientRequest.ts      | grep -o '"method": "[^"]*"' | wc -l   # 104
curl -s $B/ServerRequest.ts      | grep -o '"method": "[^"]*"' | wc -l   # 10
curl -s $B/ServerNotification.ts | grep -o '"method": "[^"]*"' | wc -l   # 84

# 로컬에서 직접 생성
codex app-server generate-ts
codex app-server generate-json-schema
```
