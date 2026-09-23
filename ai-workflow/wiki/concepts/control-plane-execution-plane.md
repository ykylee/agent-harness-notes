---
type: concept
status: active
last_ingested_from: docs/05-agents-api.md + docs/09-agents-api-environments.md + browser-agents/11-dia-and-neon.md + browser-agents/06-architecture-axes.md
related_pages: [concepts/execution-environment-topology, concepts/harness, concepts/os-sandbox-policy]
created: 2026-09-22
updated: 2026-09-23
---

# Control Plane / Execution Plane — 하네스와 compute 의 분리

- 문서 목적: 관리형 Agents API 가 그은 가장 중요한 구조 경계 하나를 정리한다.
- 범위: 경계의 정의, 세 조각, 그 경계가 가능하게 하는 것, 키 분리
- 1차 출처: `developers.openai.com/api/docs/guides/agents-api/architecture` (raw Markdown)
- 최종 수정일: 2026-09-22

## §1 TL;DR  {#s1-tldr}

| # | 면 | 무엇이 사는가 |
|---|---|---|
| 1 | **harness (control plane)** | 에이전트 루프, 모델 호출, 라우팅 |
| 2 | **compute (execution plane)** | 파일, 명령, 상태 |

> 이 경계가 있어서 **민감한 오케스트레이션은 신뢰된 인프라에 남고, 샌드박스는 프로바이더별 실행만
> 담당**할 수 있다.

## §2 세 조각  {#s2-three-pieces}

| 조각 | 무엇인가 |
|---|---|
| **Harness** | 모델과 도구 루프를 돌리고 세션을 유지하는, OpenAI 가 호스팅하는 Codex 인스턴스 |
| **Environment** | 에이전트가 명령을 돌리고 코드를 실행하고 파일을 다루는 곳 — 원격 샌드박스, 내 노트북, Docker 컨테이너, AWS Lambda 함수 |
| **Application server** | 내 코드. 과업을 제출하고 이벤트를 받고 function tool 을 처리한다. 환경을 내가 제공하면 그 생명주기도 관리한다 |

> "OpenAI runs the agent harness. Your application sends it work and receives results.
> Add an environment when the agent needs compute or files."

## §3 경계가 강제하는 키 분리  {#s3-key-separation}

두 면이 갈리므로 **자격증명도 갈린다**. 이것이 보안 규칙 중 가장 중요한 하나다.

| 키 | scope | 어디에 사는가 |
|---|---|---|
| **Application API key** | `api.agents.read`, `api.agents.write`, `api.responses.write` (+ vault 용 `api.vaults.read`/`write`) | **환경 바깥** |
| **Environment key** (`CODEX_API_KEY`) | 환경 연결 **전용** — "cannot authorize any other API action" | 환경 안 |

> **에이전트가 생성한 코드는 environment key 를 읽을 수 있다.** 그래도 되는 이유는 그 키의 권한이
> 환경 연결로만 한정돼 있기 때문이다. Application API key 는 환경·이미지·소스코드·로그 어디에도
> 있어서는 안 된다.

이것이 경계 설계의 핵심 교훈이다 — **실행 면에 놓이는 자격증명은 실행 면에서 읽힌다고 전제하고,
그 전제 위에서 권한을 깎는다.**

## §4 실행 면이 노출하는 위험  {#s4-execution-risk}

> **Agent-generated code can access the files, credentials, and network available to its environment.**

| 대책 | 내용 |
|---|---|
| **워크로드 격리** | VM 같은 격리 compute 에서 실행. 데이터를 공유하면 안 되는 사용자/워크로드는 환경을 분리. 애플리케이션마다 전용 OpenAI 프로젝트 |
| **네트워크 제한** | 승인된 엔드포인트로만 아웃바운드 허용. executor 필수 호스트 포함. **executor MCP 는 내 환경에서**, **remote MCP 는 OpenAI 서비스에서** 연결된다 — 도달 가능성 요구가 다르다 |
| **서드파티 접근 중개** | 승인된 아웃바운드 요청에 비밀값을 주입하는 credential broker 경유. **저장된 비밀을 환경에 주입하는 것 자체가 에이전트 코드에 노출하는 것**임을 기억한다 |

## §5 이 경계를 커스텀 하네스에 옮길 때  {#s5-porting}

| # | 옮길 것 |
|---|---|
| 1 | 오케스트레이션(루프·라우팅·모델 호출)과 실행(파일·명령)을 **프로세스 경계로** 가른다 |
| 2 | 실행 면에 두는 자격증명은 **읽힌다고 가정**하고 권한을 그 전제에 맞춘다 |
| 3 | 연결 방향을 **아웃바운드 전용**으로 만든다 — self-hosted 환경이 인바운드 포트를 요구하지 않는 이유 |
| 4 | 실행 면의 수명과 제어 면의 수명을 분리한다 ([[concepts/execution-environment-topology]] §5) |


## §5.5 브라우저형 에이전트가 이 축을 3분화한다  {#s5-5-browser-evidence}

Agents API 는 이 경계를 **제품이 선언**한다. 브라우저형 에이전트에서는 같은 경계가
**제품마다 다른 자리에 그어져** 있고, 그래서 축이 더 선명해진다.

| 제품 | 계획 (control) | 실행 (execution) | 근거 |
|---|---|---|---|
| **Comet** | **서버** — Perplexity 백엔드가 계획하고 명령을 발행 | 로컬 확장 | 리버싱 |
| **Aside** | **로컬 데몬** (`127.0.0.1:21420`, 353MB Node SEA) | 로컬 브라우저 | 바이너리 분석 |
| **Opera Neon** | **클라우드 LLM** | 로컬 브라우저 (Neon Do) | 제품 FAQ |
| Dia | 자사 서버 경유 → 파트너 모델 | 로컬 | 보안 문서 |

> 📌 **이 축이 모델 경제를 결정한다.** Aside 가 사용자의 ChatGPT·Claude 구독을 OAuth 로
> 끌어 쓸 수 있는 것은 계획이 로컬이기 때문이다. 계획이 서버에 있으면 사용자 자격증명을
> 쓸 이유가 없다 — Comet 은 Max 구독자에게만 모델 선택을 준다.

> ⚠️ **"로컬"이라는 단어를 벤더가 어느 면에 쓰는지 확인하라.** Opera 의 `llms.txt` 는
> "All AI processes run locally on the device" 라 하는데 제품 FAQ 는 "**계획은 클라우드
> LLM**"이라고 한다. 같은 회사의 두 1차 출처가 어긋난 사례다.

## §6 다음에 읽을 문서  {#s6-next}

- [[concepts/execution-environment-topology]] — 실행 면의 세 가지 형태
- [[concepts/os-sandbox-policy]] — 실행 면 안쪽의 OS 수준 방어
- 원문: [`docs/09-agents-api-environments.md`](../../../docs/09-agents-api-environments.md)
