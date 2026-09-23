---
type: concept
status: active
last_ingested_from: docs/99-sources.md + REPORT.md + browser-agents/99-sources.md + browser-agents/11-dia-and-neon.md
related_pages: [concepts/harness, concepts/retained-reasoning, concepts/os-sandbox-policy, concepts/thread-turn-item]
created: 2026-09-22
updated: 2026-09-23
---

# Primary-Source Verification — 이 저장소의 인식 방법

- 문서 목적: 이 저장소가 주장을 어떤 등급으로 나누고 어떻게 검증하는지를 규칙으로 고정한다. 새 조사가 들어올 때 따라야 할 절차다.
- 범위: 등급 어휘, 검증 방법, 반증의 보존, 실제로 뒤집힌 사례, 재현 명령
- 1차 출처: `docs/99-sources.md`, `REPORT.md`
- 최종 수정일: 2026-09-22

## §1 TL;DR  {#s1-tldr}

| # | 규칙 | 내용 |
|---|---|---|
| 1 | 우선순위 | **커밋된 아티팩트 > 산문.** 생성 스키마·소스·기본값이 이긴다 |
| 2 | 2차 출처 | 1차 대조 전에는 **확정으로 적지 않는다** |
| 3 | 추론 | 문서 안에서 **추론이라고 명시**한다 |
| 4 | 반증 | **지우지 않고 반증으로 보존**한다 |
| 5 | 결과 | 검증한 2차 출처 5건 중 **2건이 틀렸다** |
| 6 | 실무 발견 | OpenAI 문서 URL 끝에 **`.md` 를 붙이면 원본 마크다운**이 온다 |

## §2 등급 어휘  {#s2-grades}

| 등급 | 의미 | 문서에서의 표기 |
|---|---|---|
| **Confirmed** | 저장소의 생성 스키마 또는 소스에서 직접 확인 | 근거 파일 경로를 함께 적는다 |
| **Promoted to primary** | 2차 출처로 시작했으나 1차 본문에서 같은 문장을 찾음 | 승격 사실과 근거를 남긴다 |
| **Inferred** | 모듈명·디렉터리 배치 등 간접 근거에서 읽음 | ⚠️ **추론 경고를 본문에** 단다 |
| **Refuted** | 2차 출처가 틀렸음을 1차로 확인 | **지우지 않고** 무엇이 왜 틀렸는지 남긴다 |
| **Narrowed** | 범위를 좁혔으나 완전히 닫지는 못함 | 무엇이 여전히 열려 있는지 적는다 |

## §3 검증 방법  {#s3-method}

교정의 대부분은 **산문이 아니라 생성 스키마와 Rust 소스를 읽어서** 나왔다. 메서드 목록, 정확한 요청
payload, 에러 코드, 타임아웃 기본값은 전부 커밋된 아티팩트다. 블로그 포스트와 3자 요약은 그것들로부터
드리프트한다.

> 스스로를 갚은 실무 발견 하나: **OpenAI 문서 URL 끝에 `.md` 를 붙이면 원본 마크다운이 돌아온다.**
> 렌더된 페이지의 손실 있는 요약을 코드 샘플이 온전한 1차 텍스트로 바꿔 줬고, 존재하는지도 몰랐던
> 가이드 페이지 14개를 드러냈다. (`/llms.txt` 가 전체 색인이다.)

## §4 실제로 뒤집힌 것들  {#s4-refuted}

| 주장 | 판정 | 근거 |
|---|---|---|
| JSON-RPC `-32001` "Server overloaded; retry later.", 큐 용량 128 | ✅ **정확히 확인** | `app-server/src/error_code.rs`, `app-server-transport/src/transport/mod.rs` (`CHANNEL_CAPACITY = 128`, 리터럴 메시지) |
| ARC-AGI-3 13.3% → 38.3%, 출력 토큰 1/6 | ✅ **1차로 승격** | "Codex as a platform" 포스트 본문에 그대로 있고 전용 글을 링크 |
| WebSocket CSRF — `Origin` 헤더 있는 요청 거부 | ✅ **확인** | `transport/websocket.rs`, `reject_requests_with_origin_header` |
| WebSocket **기본 포트 `127.0.0.1:9090`** | ❌ **반증** | `AppServerTransport::DEFAULT_LISTEN_URL = "stdio://"`. 기본 WS 포트는 없고 `9090` 은 저장소 어디에도 관련 형태로 없다 |
| **30분** idle thread 언로드 | ❌ **반증** | `thread_unload_delay_secs` — "Defaults to **60**". 구독자 없음 **그리고** 활동 없음을 함께 요구 |
| `initialize` 응답에 `serverInfo`/`capabilities` | ❌ **반증** | `InitializeResponse` 는 4필드: `userAgent`, `codexHome`, `platformFamily`, `platformOs` |

> 5건 중 2건이 틀렸다. **반증을 기록에 남기는 것이 이 저장소의 신뢰를 만든다** — 지우면 다음 사람이
> 같은 2차 출처를 다시 믿는다.

## §5 조사 스스로를 교정한 사례  {#s5-self-corrections}

이 저장소는 자기 앞선 서술도 같은 규칙으로 뒤집었다.

| 앞선 주장 | 교정 |
|---|---|
| "SSE 이벤트 25종을 합성해야 하며 이것이 일의 대부분" | 실제로 처리되는 것은 **12종**, **7종이면 충분**. 도구 호출 인자 스트리밍은 아예 무시된다 |
| `AdditionalTools` 는 버려도 되는 Responses 네이티브 변형 | `responses_lite` 모드에서는 **그것이 도구 목록**이다. 두 번째 요청 형태를 놓쳤다 |
| 9개짜리 샌드박스 프로바이더 명단 둘이 모순 | **둘 다 옳았다.** 서로 다른 제품의 명단 — 7개 공유, DigitalOcean·OCI 는 API 전용, Unix-local·Docker 는 SDK 전용 |
| 게시일이 8/19 인가 8/20 인가 | **타임존 산물.** Archive 최초 캡처 2026-08-19 21:07 UTC = IST 로는 8/20. 두 출처 모두 자기 시간대에서 옳았다 |

## §6 설계상 열려 있는 것  {#s6-open-by-design}

세 항목이 남는다. 둘은 열린 질문이 아니라 **의도적 기록**이고, 하나만 실제로 좁혀진 미확인이다.

| 항목 | 상태 |
|---|---|
| `initialize` 응답에 `serverInfo`/`capabilities` 라는 주장 | **기록으로 보존된 반증** |
| Windows 샌드박스 내부(ACL/WFP/토큰/데스크톱) | **모듈명에서 추론.** [[concepts/os-sandbox-policy]] §6 이 명시 |
| Agents API 모델 ID | **좁혀짐.** 번들 클라이언트 카탈로그 9종은 확인됨. **Agents API 서버측 목록이 이와 일치하는지는 미확인** — 별개 표면이다 |

## §7 재현  {#s7-reproduction}

```bash
# 프로토콜 메서드 수를 직접 세어 본다
B=https://raw.githubusercontent.com/openai/codex/main/codex-rs/app-server-protocol/schema/typescript
curl -s $B/ClientRequest.ts      | grep -o '"method": "[^"]*"' | wc -l   # 104
curl -s $B/ServerRequest.ts      | grep -o '"method": "[^"]*"' | wc -l   # 10
curl -s $B/ServerNotification.ts | grep -o '"method": "[^"]*"' | wc -l   # 84

# 로컬 생성
codex app-server generate-ts
codex app-server generate-json-schema

# 아무 문서 페이지나 원본 마크다운으로 읽기
curl -sL https://developers.openai.com/api/docs/guides/agents-api/tools/mcp.md

# OpenAPI 스펙에서 Agents API 엔드포인트
curl -sL https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml -o /tmp/openapi.yaml
grep -nE '^  /(agents|vaults)' /tmp/openapi.yaml
```

## §8 유효기간  {#s8-validity}

조사 기준은 `openai/codex` 의 **2026-09-15 상태**다. 빠르게 움직이는 저장소이므로 재조사의 첫 수는
새 사실 수집이 아니라 **기존 사실의 드리프트 확인**이다.


## §3.5 수법의 일반화와 그 한계  {#s3-5-generalization}

**`.md` 접미사와 `/llms.txt`** 는 OpenAI 문서에서 발견했지만 다른 곳에서도 통한다.
다만 **문서 사이트의 렌더링 방식에 달렸다.**

| 대상 | `llms.txt` | `.md` | 결과 |
|---|---|---|---|
| OpenAI 문서 | — | ✅ | 가이드 14편 발견 |
| **Aside** | ✅ | ✅ | 제품 문서 16종 전부 1차 확보 |
| **Opera** | ✅ | — | Neon 항목 확보 |
| **Dia** | ❌ | ❌ | 모든 경로가 동일한 SPA 셸 |

> 📌 **먼저 시도하되 만능으로 믿지 마라.** 클라이언트 렌더 사이트는 정적 수법이 닿지 않는다.
> 실패 시 렌더된 페이지나 프레임워크 페이로드(Next.js flight 등)로 돌아간다.

## §3.6 새로 확인된 함정 두 가지  {#s3-6-traps}

### 상속을 고유 기능으로 오인하기

포크 제품의 바이너리에서 어떤 기능의 흔적이 나와도, **상류에서 상속한 것일 수 있다.**

> 실례: Aside 브라우저에서 포스트양자 암호(ML-KEM) 문자열이 나왔다. 그런데 **Chromium 은
> 2024년부터 X25519MLKEM768 TLS 를 기본 탑재**한다. 포크라면 당연히 나온다.
> **파일 위치를 먼저 갈라야** 했고, 제품 자신의 코드(Vault 확장·데몬)에 있음을 확인한
> 뒤에야 고유 기능으로 확정했다.

**규칙: 포크 제품에서 발견한 것은 상류에 없는지 먼저 확인한다.**

### 벤더 자신의 두 1차 출처가 모순되기

> 실례: Opera 의 `llms.txt` 와 Opera Neon 제품 FAQ 가 "AI 처리가 로컬인가"에 대해 반대로 말한다.

**규칙: 1차 출처라도 서로 대조한다. 어긋나면 더 구체적인 쪽을 채택하고 모순 자체를 기록한다.**

## §3.7 정보량 차이를 성숙도 차이로 읽지 않기  {#s3-7-asymmetry}

브라우저 조사 초기, Comet 은 내부가 상세히 알려졌고 Aside 는 "미공개"가 많았다. 그 차이는
**제품 성숙도가 아니라 누가 뜯어봤느냐**의 차이였다 — Aside 바이너리를 직접 열자 대부분 채워졌다.

> 📌 **현재도 같은 비대칭이 남아 있다.** Aside 는 바이너리까지 검증했고 Dia·Neon 은 제품
> 문서를 믿은 상태다. 문서가 좋다는 것과 구현이 그렇다는 것은 다르다 — 비교표를 읽을 때
> **각 칸의 근거 등급이 다르다는 점**을 잊으면 안 된다.

## §9 다음에 읽을 문서  {#s9-next}

- [[concepts/os-sandbox-policy]] §6 — 추론 등급이 실제로 붙은 자리
- [[concepts/thread-turn-item]] §3 — 반증이 실제로 붙은 자리
- 원문: [`docs/99-sources.md`](../../../docs/99-sources.md), [`REPORT.md`](../../../REPORT.md)
