---
type: concept
status: active
last_ingested_from: docs/09-agents-api-environments.md + docs/05-agents-api.md
related_pages: [concepts/control-plane-execution-plane, concepts/approval-gate, concepts/capability-distribution, concepts/os-sandbox-policy]
created: 2026-09-22
updated: 2026-09-22
---

# Execution Environment Topology — 실행 환경의 세 형태

- 문서 목적: 관리형 하네스가 붙을 수 있는 실행 환경 세 종류와 각각의 생명주기·제약을 정리한다.
- 범위: 세 topology, hosted 설정, 파일/아티팩트 비대칭, self-hosted 생명주기, 프로바이더 명단 두 개
- 1차 출처: `agents-api/environments/{openai-hosted,self-hosted,lifecycle,files,security}` (raw Markdown)
- 최종 수정일: 2026-09-22

## §1 TL;DR  {#s1-tldr}

| `environment.type` | 누가 만드나 | 파일 회수 경로 |
|---|---|---|
| `none` | — (환경 없음) | 없음 — 세션 item 에서 출력을 읽는다 |
| `openai_hosted` | OpenAI | 세션 Artifacts API (`/workspace/outputs` 한정) |
| `self_hosted` | 나 | 내 프로바이더의 파일 API 또는 마운트된 파일시스템 |

## §2 세 topology  {#s2-topologies}

### §2.1 `none`  {#s2-1-none}

질문에 답하거나 외부 서비스에 닿는 에이전트용. 하네스가 remote MCP 도구를 직접 호출하고, function
tool 은 내 코드가 처리한다.

**잃는 것:** 내장 Bash 와 apply-patch 도구, 워크스페이스 파일, executor MCP.
직접 만든 function tool 로 파일시스템과 셸을 흉내 낼 수는 있다(문서가 "virtual runtime"이라 부른다).

### §2.2 `openai_hosted`  {#s2-2-hosted}

OpenAI 가 세션용 샌드박스를 만들고 관리한다. 패키지·파일·네트워크 접근을 내가 설정한다.

### §2.3 `self_hosted`  {#s2-3-self-hosted}

내 인프라, 사설망, 커스텀 소프트웨어용. 내 코드가 환경을 띄우고 executor 를 연결한다.
**프로비저닝·재연결·종료·필요한 파일의 보존이 전부 내 몫이다.**

## §3 OpenAI-hosted 샌드박스 설정  {#s3-hosted-config}

Python · Node.js · CLI 도구를 갖춘 Linux 워크스페이스. 작업 디렉터리는 `/workspace`.

| 필드 | 용도 |
|---|---|
| `packages` | `python` / `system` / `npm` 목록. 필요하면 버전 고정 (`pandas==2.2.3`) |
| `setup_commands` | 에이전트 시작 **전에** 순서대로 도는 셸 명령. 각각 선택적 `cwd`(기본 `/workspace`) |
| `files` | Files API ID 또는 inline base64 |
| `env` | 문자열 환경변수. **런타임 예약 이름(`PATH`, `CODEX_*`, `OPENAI_API_KEY`)은 거부** |
| `skills`, `plugins`, `capability_directories` | skill 과 plugin |
| `environment_template_id` | 저장된 설정 재사용. 생략한 설정은 템플릿을 상속하되 **네트워크 override 로 정책을 넓힐 수는 없다** |

> **순서가 중요하다**: 패키지와 입력 파일이 setup command **전에** 준비된다.
> **setup 이 0 이 아닌 종료 코드를 내면 에이전트가 시작되지 않는다.**
> 템플릿은 **설정을 저장하지, 돌고 있는 워크스페이스를 저장하지 않는다.**

### §3.1 네트워크 정책  {#s3-1-network}

| `network.access` | 동작 |
|---|---|
| `enabled` | 아웃바운드 허용. 템플릿 정책을 상속하지 않는 한 기본값 |
| `disabled` | 아웃바운드 차단 |
| `restricted` | `allowed_domains` 의 호스트만 허용 |

`restricted` 는 **정확한 호스트 이름 1~100개**만 받는다. **와일드카드·프로토콜·경로·포트 불가.**
**서브도메인과 리다이렉트 목적지는 각자 항목이 필요하다.**
호스팅된 **stdio** MCP 서버는 현재 `enabled` 를 요구한다.

### §3.2 상태 확인과 만료  {#s3-2-status-expiry}

세션 생성 응답은 셋업이 *시작*됐다는 뜻일 뿐이다.
`GET /v1/agents/environments/{environment_id}` 로 확인한다.

| 상태 | 의미 |
|---|---|
| `provisioning` | 셋업 진행 중 |
| `connected` | 셋업 성공 |
| `failed` | `agent.session.environment.failed` 이벤트의 `environment.error` 를 읽는다 |

**라이브 파일을 추가/조회하기 전에 `connected` 를 기다린다.**

> 연결된 샌드박스는 turn 사이에도 keep-alive 를 받는다. 활동과 keep-alive 가 **한 시간** 멈추면
> 샌드박스가 삭제될 수 있다. **이 타임아웃은 설정 불가.**
> 삭제가 `409` 를 내면 셋업/실행이 끝날 때까지 기다렸다 **시도 횟수 상한을 두고** 재시도한다.
> **이벤트 스트림을 닫는 것은 작업을 취소하지 않는다.**

## §4 File 과 Artifact — 놓치기 쉬운 비대칭  {#s4-files-artifacts}

**File** = 에이전트 환경에 사는 것. **Artifact** = OpenAI-hosted 환경에서 게시된 복사본으로,
**환경이 만료된 뒤에도** 내려받을 수 있다.

> ⚠️ **self-hosted 환경의 파일은 `/workspace/outputs` 아래에 있더라도 Artifacts API 로 게시되지
> 않는다.** 이 비대칭을 놓치기 쉽다.

| 항목 | 규칙 |
|---|---|
| 게시 | `/workspace/outputs` 아래에 쓰게 하면 **turn 완료 시 불변 artifact 로 게시** |
| 식별 | **turn ID + path** |
| 내려받기 | **요청당 artifact 하나.** 일괄 다운로드 엔드포인트 없음 → 여러 개면 ZIP 으로 묶게 시킨다 |
| 수정 | artifact 는 **업로드·편집 불가**. 새 판을 내려면 파일을 고치고 turn 을 한 번 더 완료시킨다 |
| 삭제 | artifact 를 지워도 **환경 안의 파일은 그대로** |

### §4.1 한도  {#s4-1-limits}

| 항목 | 한도 |
|---|---|
| 세션 생성 시 포함 파일 | 요청당 50개 |
| inline 업로드 | 파일당 5 MiB (**base64 인코딩 전** 기준) |
| 생성 요청 하나의 inline 총량 | 10 MiB (인코딩 전) |
| Files API 에서 복사 | 파일당 50 MiB |
| 게시된 artifact | 파일당 200 MiB |
| 함께 게시되는 outputs | 총 500 MiB |

## §5 self-hosted 생명주기  {#s5-lifecycle}

### §5.1 시작 — webhook 으로 필요할 때만 띄우기  {#s5-1-start}

API 는 executor 를 **기다리기 전에** `agent.session.action_required` 를
`required_action.type: "environment_connection"` 으로 방출한다.

| 경로 | 할 일 |
|---|---|
| **Handler (fast)** | ① webhook 서명 검증 ② `environment_connection` 일 때만 연결 요청을 큐잉(세션 실패도 큐잉) ③ **큐잉 성공 후에야** 성공 HTTP 응답 반환 |
| **Worker (slow)** | ① 세션 조회, 삭제됐거나 해소된 action 은 무시 ② 연결이 여전히 필요한 self-hosted 세션이면 `session.environment.id` 와 `remote_url` 로 executor 시작/재연결 ③ 여전히 실패 상태면 **compute 를 반납** |

> ⏱ **타이밍 주의**: turn 생성과 `agent.session.in_progress` 이벤트는 꺼져 있는 executor 를 띄우기에
> **너무 늦게 도착한다.** `function_call` required action 은 환경 기동이 아니라 함수 결과를 요구한다.

### §5.2 중지  {#s5-2-stop}

turn 사이에 compute 를 살려 두고 재사용하거나, turn 종료 후 유예 기간을 준다. 종료를 들어오는
작업과 조율한다 — 연결 요청이나 실행 시작이 있으면 대기 중인 종료를 취소하고, 멈추기 전에 상태를
다시 확인한다.

> **idle 이벤트 하나만으로는 안전한 종료 신호가 아니다.** 연결 요청이 해소될 때, 대기 중인 입력이
> turn 을 시작하기 전에도 도착할 수 있다.

### §5.3 중복 방지  {#s5-3-dedup}

> 세션마다 환경을 관리하는 **컴포넌트를 하나로** 둔다. 세션↔프로바이더 compute 매핑을 저장한다.
> **반복되거나 동시에 오는 요청이 중복 환경을 만들면 안 된다.**

## §6 프로바이더 명단은 두 개다 — 헷갈리는 이유  {#s6-two-rosters}

각각 9개 항목이라 모순처럼 보이지만 **서로 다른 제품의 명단**이다.

| | 프로바이더 |
|---|---|
| **양쪽 모두 (7)** | Blaxel, Cloudflare, Daytona, E2B, Modal, Runloop, Vercel |
| **Agents API 만** | DigitalOcean, Oracle Cloud Infrastructure (OCI) |
| **Agents SDK 만** | Unix-local, Docker — 클라우드 파트너가 아니라 로컬 런타임 |

- **Agents API 명단** = 관리형 하네스가 *연결해 가는* 환경을 호스팅하는 클라우드 프로바이더
- **Agents SDK 명단** = 하네스를 *내 인프라에서 돌릴 때* 인스턴스화하는 클라이언트 클래스

> 이미 쓰는 프로바이더가 아니라 **누가 하네스를 돌리는가**에 맞는 명단을 고른다.

## §7 다음에 읽을 문서  {#s7-next}

- [[concepts/control-plane-execution-plane]] — 이 분리의 상위 개념
- [[concepts/capability-distribution]] — 환경에 skill/plugin 을 싣는 방법
- [[concepts/approval-gate]] — `requires_action` 처리
- 원문: [`docs/09-agents-api-environments.md`](../../../docs/09-agents-api-environments.md)
