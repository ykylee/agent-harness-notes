# 05. Agents API — 관리형(호스팅) Codex Harness

**2026-09-10 퍼블릭 베타.** 지금까지 Codex를 돌려온 제어 계층(세션 관리, 컨텍스트 컴팩션,
실패 복구, 멀티 에이전트 조정)을 **OpenAI가 직접 운영하는 API**로 떼어낸 것.

> 엔드포인트·스키마·이벤트의 **정확한 정의는 [08-agents-api-reference.md](08-agents-api-reference.md)** 에 있습니다.
> 이 문서는 개념과 사용 시나리오를 다룹니다.

공식 표현: *"application access to OpenAI's managed Codex harness through an API."*
OpenAI가 세션·오케스트레이션·컨텍스트 관리·복구를 담당하고,
애플리케이션은 **도구를 제공하고 실행 환경을 고른다.**

## 1. 핵심 객체

| 객체 | 정의 |
|---|---|
| **Agent** | 모델 + 지시문(instructions) + 도구 + MCP 서버 |
| **Environment** | 선택적 샌드박스/컴퓨터. 파일 접근, skill 로딩, 명령 실행 |
| **Session** | 과업을 수행하고 입력에 반응하는 **지속되는 에이전트 인스턴스** |
| **Events / Items** | 세션에 보내는 입력과 세션이 만드는 출력 |

## 2. 세션 수명주기

1. 에이전트 설정과 함께 **세션 생성**
2. 사용자 입력으로 **과업 부여**
3. **스트리밍 또는 웹훅**으로 진행 관찰
4. 추가 과업 전달 또는 진행 중인 턴 **steer**

## 3. 관리형 harness가 제공하는 것

- 샌드박스에서 명령/코드 실행
- skills 및 지시문 적용
- 도구 또는 MCP로 외부 데이터 연결
- **작업 도중 steering**
- 컨텍스트 한계 근처에서 **자동 컴팩션** ("automatically compacts earlier context as a session nears its limit")
- **서브에이전트**에 하위 과업 위임
- 세션 재개
- **Tool search** — 도구 정의를 선택적으로 로드해 토큰 절감
- **프로그래매틱 툴 콜링** — 병렬 실행

## 4. 엔드포인트 (SDK 기준)

SDK: JavaScript, Python, Go, Java, Ruby, curl 6종 예제 제공.

```javascript
// 세션 생성
client.beta.agents.sessions.create({ /* agent, environment, input */ })
```

| 작업 | 설명 |
|---|---|
| create | 에이전트 설정 + 환경 + 초기 입력으로 세션 생성 |
| list | 페이지네이션 (`hasNextPage()`, `getNextPage()` 헬퍼) |
| retrieve | ID로 상태 / 에이전트 설정 / 환경 / **required actions** 조회 |
| delete | 논리 삭제 (비동기 정리 가능). 대화를 남기고 현재 작업만 멈추려면 **turn cancel** |

> **세션 ID를 애플리케이션 데이터스토어에 저장**하는 것이 전제입니다.
> 재시작·연결 끊김 후에는 세션을 retrieve해서 밀린 작업을 확인하세요.

### `requires_action` 처리

세션이 `requires_action` 상태를 반환하면 응답에 대기 중 액션 배열이 들어옵니다.

| 액션 | 처리 |
|---|---|
| **Function calls** | 지정 함수를 실행하고 `turn_id` + `call_id`로 결과 반환 |
| **Environment connections** | `environment_id`로 외부 환경에 연결 수립 |

## 5. 실행 환경 (샌드박스)

### 옵션

1. **OpenAI 호스팅** — Codex/ChatGPT 인프라 사용
2. **셀프호스팅** — `codex exec-server`로 내 환경에 연결
3. **파트너 제공자** — Blaxel, Cloudflare, Daytona, DigitalOcean, E2B, Modal, Oracle, Runloop, Vercel
4. **샌드박스 없음**

### 아키텍처 경계 (중요)

> **harness(컨트롤 플레인)** — 에이전트 루프, 모델 호출, 라우팅
> **compute(실행 플레인)** — 파일, 명령, 상태

이 경계 덕분에 **민감한 오케스트레이션은 신뢰 인프라에 남기고, 샌드박스는 제공자별 실행만** 담당합니다.

### 셀프호스팅 연결 절차

```bash
# 1. 워크스페이스 준비
mkdir -p /workspace
npm install -g @openai/codex@alpha
```

네트워크: `https://api.openai.com` 과 `wss://codex-cloud-environments.chatgpt.com`으로의
**아웃바운드**만 열면 됩니다 (모든 연결이 내 환경 → OpenAI 방향).

인증: 플랫폼 대시보드 Agents 탭에서 **제한된 executor 키**를 발급해 `CODEX_API_KEY`로 주입.

```bash
# 2. 세션 생성 시 environment를 self_hosted로
#    { "type": "self_hosted", "workspace_directory": "/workspace" }

# 3. 내 환경 안에서 실행기 기동
codex exec-server \
  --remote "<session.environment.remote_url>" \
  --environment-id "<session.environment.id>"
```

실행기는 environment ID와 제한된 API 키로 등록하고 **WebSocket으로 명령을 받아 결과를 반환**합니다.

연결 상태 이벤트: `agent.session.environment.pending` → `connected` / `failed`.

## 6. 샌드박스 에이전트 (Agents SDK 쪽)

> 아래는 **Agents SDK로 harness를 내 인프라에서 돌리는** 경로입니다.
> Agents API(관리형)와 구분하세요.

### 언제 샌드박스를 쓰나

- 과업이 단일 프롬프트가 아니라 **문서 디렉터리**를 요구할 때
- 에이전트가 나중에 검사할 파일을 써야 할 때
- 명령·패키지·스크립트가 개입할 때
- 산출물(Markdown, CSV, 스크린샷, 웹사이트)을 만들 때
- 노출된 포트에서 서비스/프리뷰가 떠야 할 때
- 사람 검토를 위해 멈췄다가 **같은 워크스페이스에서 재개**할 때

짧은 모델 응답만 필요하면 샌드박스는 불필요합니다.

### Manifest — 시작 워크스페이스 정의

| 항목 | 설명 |
|---|---|
| File / Dir 엔트리 | 작은 합성 입력, 헬퍼 파일 |
| 로컬 경로 | 호스트 파일을 샌드박스로 실체화 |
| Git 리포 | 워크스페이스로 fetch |
| 클라우드 마운트 | S3, GCS, R2, Azure Blob, Box, FileMounts |
| 환경 변수 | 기동 시 필요한 값 |
| OS 계정 | 지원 제공자 한정, 사용자/그룹 |

경로는 **워크스페이스 상대경로**여야 하며 절대경로/이스케이프 시퀀스 불가.

### Capabilities

`SandboxAgent` 기본값: filesystem + shell + compaction.

| Capability | 목적 |
|---|---|
| `Shell` | 명령 실행, 대화형 입력 |
| `Filesystem` | 파일 편집, 이미지 검사 |
| `Skills` | skill 탐색/실체화 |
| `Memory` | 실행 간 교훈 유지 |
| `Compaction` | 장기 실행용 컨텍스트 트리밍 |

### 실행

```javascript
const manifest = new Manifest({ entries: { /* ... */ } });
const agent = new SandboxAgent({
  name: "Agent Name",
  model: "gpt-6-astra",
  instructions: "Task instructions",
  defaultManifest: manifest,
  capabilities: [shell()]
});

const result = await run(agent, "User prompt", {
  sandbox: { client: new UnixLocalSandboxClient() }
});
```

```python
result = await Runner.run(
    agent,
    "User prompt",
    run_config=RunConfig(
        sandbox=SandboxRunConfig(client=UnixLocalSandboxClient())
    )
)
```

### 제공자 전환

에이전트 정의를 바꾸지 않고 **run 설정만** 바꿔 제공자를 갈아끼웁니다.

| 제공자 | 클라이언트 |
|---|---|
| Unix-local | `UnixLocalSandboxClient` |
| Docker | `DockerSandboxClient` |
| E2B | `E2BSandboxClient` |
| Blaxel | `BlaxelSandboxClient` |
| Cloudflare | `CloudflareSandboxClient` |
| Daytona | `DaytonaSandboxClient` |
| Modal | `ModalSandboxClient` |
| Runloop | `RunloopSandboxClient` |
| Vercel | `VercelSandboxClient` |

개발은 Unix-local, 컨테이너 격리는 Docker로 시작 권장.

### 상태 3종과 해석 순서

| 개념 | 내용 |
|---|---|
| **RunState** | harness 쪽 모델 아이템, 도구 상태, 승인 |
| **Session state** | 재연결용으로 직렬화된 샌드박스 세션 |
| **Snapshot** | 새 세션을 시드하기 위해 저장한 워크스페이스 내용 |

해석 순서: **살아있는 세션 → 재개된 RunState → 명시적 직렬화 상태 → 새 세션**

### Sandbox Memory

메시지 히스토리와 **별도로** 재사용 가능한 교훈을 실행 간 유지합니다.

```
memory_summary.md      # 상위 요약
MEMORY.md              # 통합 교훈
raw_memories/          # 실행별 요약
rollout_summaries/     # 상세 롤아웃
```

### 조합

- **Handoffs** — 워크스페이스 중심 과업을 샌드박스 에이전트로 라우팅
- **Tools** — 샌드박스 에이전트를 독립 설정을 가진 중첩 도구로 호출

## 7. 관측

`platform.openai.com/logs?api=agents`에서 세션 ID로 검색하면
**턴, 도구 호출, 서브에이전트**를 들여다볼 수 있습니다.

연속 모델 호출이 같은 프롬프트 프리픽스를 공유하면 **프롬프트 캐싱**이 이전 처리를 재사용합니다.

## 8. 가격 / 제약

- **Agents API 자체의 추가 서비스 요금 없음.** 과금은 별도로 누적:
  - 모델 토큰
  - OpenAI 제공 도구
  - OpenAI 호스팅 샌드박스의 **컨테이너 시간**
- 데이터 레지던시: **미국만**
- **Zero Data Retention 미지원.** 셀프호스팅 샌드박스를 써도 ZDR 자격이 생기지 않음
- 문서 예제에 등장하는 모델: `gpt-6-astra` (SDK 예제), `gpt-5.6-terra` (Codex SDK 예제)

## 9. 관계 정리

```
        오픈소스                              관리형
┌──────────────────────────┐        ┌──────────────────────────┐
│  openai/codex (Apache-2) │        │  Agents API (OpenAI 운영) │
│  ├─ codex exec           │        │  ├─ sessions             │
│  ├─ Codex SDK            │  ───▶  │  ├─ 호스팅 샌드박스        │
│  └─ app-server           │  같은   │  ├─ 서브에이전트           │
│      (JSON-RPC)          │ harness │  └─ 자동 컴팩션           │
└──────────────────────────┘        └──────────────────────────┘
       내가 운영                   OpenAI가 운영 (모델 릴리스에 맞춰
                                   버전 관리된 접근 제공)
```

*"a managed service built on the open-source Codex harness"* — 즉 **같은 harness, 운영 주체만 다름.**
