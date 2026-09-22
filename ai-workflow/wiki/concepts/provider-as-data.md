---
type: concept
status: active
last_ingested_from: docs/15-model-providers.md
related_pages: [concepts/wire-protocol-boundary, concepts/retained-reasoning, concepts/capability-distribution]
created: 2026-09-22
updated: 2026-09-22
---

# Provider as Data — 프로바이더를 코드 분기가 아니라 데이터로

- 문서 목적: `ModelProviderInfo` 가 프로바이더를 어떻게 데이터로 표현하는지, 그 중 커스텀 하네스가 그대로 베낄 만한 설계가 무엇인지 정리한다.
- 범위: 내장 목록이 짧은 이유, 전체 필드, 커맨드 기반 인증, 설정 deny-list, in-flight thread 처리
- 1차 출처: `codex-rs/model-provider-info/src/lib.rs` (710줄 직접 독해)
- 최종 수정일: 2026-09-22

## §1 TL;DR  {#s1-tldr}

| # | 항목 | 값 |
|---|---|---|
| 1 | 내장 프로바이더 | 5개 (`openai`, `amazon-bedrock`, `amazon-bedrock-runtime`, `ollama`, `lmstudio`) |
| 2 | 내장이 짧은 이유 | **의도적** — 어떤 서드파티를 번들할지 심판하지 않겠다는 선언 |
| 3 | 확장 지점 | `config.toml` 의 `model_providers` |
| 4 | 제약의 정체 | 벤더가 아니라 **wire protocol** ([[concepts/wire-protocol-boundary]]) |
| 5 | 가장 재사용성 높은 아이디어 | **커맨드 기반 토큰 발급** |
| 6 | 반드시 베낄 보안 경계 | 프로젝트 로컬 설정의 **프로바이더·인증·텔레메트리 키 deny-list** |

## §2 내장이 짧은 것은 설계다  {#s2-builtin-short}

```rust
// We do not want to be in the business of adjucating which third-party
// providers are bundled with Codex CLI, so we only include the OpenAI and
// open source ("oss") providers by default. Users are encouraged to add to
// `model_providers` in config.toml to add their own providers.
```

**다중 프로바이더는 1급 설계 지점이다.** 제약은 벤더가 아니라 wire protocol 이다.

## §3 `ModelProviderInfo` 전체 모양  {#s3-shape}

| 필드 | 용도 |
|---|---|
| `name` | 표시 이름. **비-OpenAI 경로를 가르는 레버이기도 하다** ([[concepts/stateless-conversation-wire]] §5) |
| `base_url` | OpenAI 호환 API 의 base URL |
| `env_key` / `env_key_instructions` | API 키를 담은 환경변수와 그 안내 문구 |
| `experimental_bearer_token` | 리터럴 `Authorization: Bearer` 값. `env_key` 대비 **비권장**이나 프로그램적으로 필요 |
| `auth` | **커맨드 기반** bearer 토큰 (§4) |
| `aws` | AWS SigV4 설정 |
| `wire_api` | Responses (유일 값) |
| `query_params` / `http_headers` | base URL 에 붙는 쿼리, 리터럴 추가 헤더 |
| `env_http_headers` | 헤더 이름 → **환경변수**. 미설정이거나 비면 생략 |
| `request_max_retries` / `stream_max_retries` / `stream_idle_timeout_ms` / `websocket_connect_timeout_ms` | 재시도·타임아웃 손잡이 |
| `requires_openai_auth` | 로그인 화면을 띄우고 `auth.json` 에 자격증명을 저장할지 |
| `supports_websockets` / `supports_standalone_web_search` | **capability 플래그** |

> **capability 와 identity 를 분리한다.** `supports_websockets`, `supports_standalone_web_search` 는
> UI 가 **읽어야 할 프로바이더별 사실**이지 가정할 것이 아니다. [[concepts/retained-reasoning]] §5 는
> 여기에 `supports_retained_reasoning` 을 더하라고 권한다.

## §4 커맨드 기반 인증 — 가장 베낄 만한 것  {#s4-command-auth}

클라우드 CLI 나 사내 브로커가 토큰을 발급하는 프로바이더용.

| 키 | 용도 |
|---|---|
| `model_providers.<id>.auth.command` | 실행 파일 |
| `...auth.args` | 인자 |
| `...auth.cwd` | 작업 디렉터리 |
| `...auth.timeout_ms` | 호출당 타임아웃 |
| `...auth.refresh_interval_ms` | 재발급 주기 |

> 이것이 프로바이더 설계 전체에서 **커스텀 하네스에 가장 재사용성 높은 아이디어**다 —
> "프로바이더 X 의 별난 인증을 지원하라"를 "토큰을 출력하는 무언가를 셸로 부르라"로 바꾼다.

### §4.1 AWS 의 상호 배타 규칙  {#s4-1-aws}

`aws.region` · `aws.profile` · `aws.credential_export`.
**`credential_export` 와 `profile` 은 동시에 설정할 수 없다.** `credential_export` 가 설정돼 있으면
Bedrock 셋업과 로그인은 **설정이나 저장된 자격증명을 바꾸지 않은 채** 에러를 반환한다.

## §5 반드시 베낄 보안 경계 — 설정 deny-list  {#s5-deny-list}

프로젝트 범위 `.codex/config.toml` 은 머신 로컬의 프로바이더·인증·알림·프로파일·텔레메트리 키를
**덮어쓸 수 없다.** 프로젝트 로컬 파일에 나타나면 Codex 가 무시하는 키:

```
openai_base_url   chatgpt_base_url   apps_mcp_product_sku
model_provider    model_providers    notify
profile           profiles           experimental_realtime_ws_base_url   otel
```

> 클론한 저장소가 내 에이전트의 모델 트래픽을 돌리거나 텔레메트리를 빼돌릴 수 있어서는 안 된다.
> **프로젝트별 설정을 읽는 커스텀 하네스는 같은 deny-list 가 필요하다.**

## §6 정책 변경과 in-flight thread  {#s6-in-flight}

> 기존 thread 는 자기 프로바이더 설정을 유지한다. 관리형 `model_provider` / `model_providers` 요건이
> 더 이상 맞지 않거나 로드할 수 없으면 **입력 계열 RPC 가 거부된다** — turn start/steer, review,
> compaction, 수동 queue start, 활성 goal 갱신. **interrupt, realtime stop, goal pause/clear 는
> 계속 가능하다.** 사용자·프로젝트 설정 변경만으로는 기존 thread 가 무효화되지 않는다.

> 베낄 패턴: 기업 정책 변경이 **돌고 있는 대화를 조용히 다른 모델로 옮겨서는 안 된다.**
> *입력* 경로를 실패시키되 *제어* 경로는 열어 둔다.

realtime 연결은 별도 라우팅 설정을 쓰며 이 검사에서 면제된다.

## §7 다중 프로바이더 하네스 체크리스트  {#s7-checklist}

- [ ] **wire protocol 경계를 가장 먼저** 정한다 — Codex core 재사용 가능 여부가 여기서 갈린다
- [ ] Chat Completions 가 필요하면 어댑터를 **fork 가 아니라 프로바이더 모양의 프록시**로 설계한다
- [ ] 프로바이더를 **코드 분기가 아니라 데이터**(`ModelProviderInfo` 모양)로 모델링한다
- [ ] 커맨드 기반 토큰 발급을 **첫날부터** 지원한다
- [ ] capability 와 identity 를 분리한다
- [ ] 프로바이더마다 자기 재시도·타임아웃 손잡이를 준다 (로컬 Ollama 와 호스팅 API 는 다르다)
- [ ] 프로젝트 로컬 설정이 프로바이더·인증·텔레메트리 키를 못 쓰게 막는다
- [ ] 프로바이더 정책이 바뀔 때 **in-flight thread** 를 어떻게 할지 정한다 — 입력 거부, 제어 유지

## §8 다음에 읽을 문서  {#s8-next}

- [[concepts/wire-protocol-boundary]] — 이 데이터 모델이 놓인 제약
- [[concepts/retained-reasoning]] — capability 플래그로 다뤄야 할 대상
- 원문: [`docs/15-model-providers.md`](../../../docs/15-model-providers.md)
