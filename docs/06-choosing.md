# 06. 어떤 통합 경로를 고를 것인가

## 1. 비교표

| 기준 | `codex exec` | Codex SDK | `codex mcp-server` | **App Server** | Agents API |
|---|---|---|---|---|---|
| 형태 | CLI | TS/Python 라이브러리 | MCP stdio 서버 | JSON-RPC 프로세스 | HTTPS 관리형 API |
| 실행 주체 | 내 머신/CI | 내 머신 | 내 머신 | 내 머신/컨테이너 | **OpenAI** |
| 표면적 | 좁음 | 중간 | MCP가 노출하는 것만 | **전체** | 전체(관리형) |
| 스트리밍 진행 | `--json` JSONL | `runStreamed()` | 제한적 | 84종 알림 | 스트리밍/웹훅 |
| 승인 개입 | 플래그로 정책만 | 정책 | 제한적 | **서버 요청으로 실시간** | requires_action |
| 앱 소유 도구 주입 | ✗ | 제한적 | ✗ | **`item/tool/call`** | function calls / MCP |
| 인증 · 모델 발견 · 설정 관리 | 부분 | 부분 | ✗ | **전부** | 관리형 |
| 통합 비용 | 최저 | 낮음 | 낮음 | **높음(바인딩 작성)** | 중간 |
| 인프라 운영 | 내가 | 내가 | 내가 | 내가 | **OpenAI** |

## 2. 의사결정 흐름

```
에이전트가 "제품 그 자체"인가? (UI에 임베드, 승인 흐름, 실시간 스트리밍)
├─ 예 ──▶ 하네스를 내가 운영해야 하나? (온프렘/데이터 경계/커스텀 샌드박스)
│         ├─ 예 ──▶ ★ App Server
│         └─ 아니오 ──▶ ★ Agents API
└─ 아니오
   ├─ 이미 MCP 워크플로가 있고 Codex를 "도구 하나"로 부르고 싶다 ──▶ codex mcp-server
   ├─ 서버사이드 코드에서 프로그래매틱하게 부르고 싶다 ──▶ Codex SDK
   └─ CI/스크립트에서 한 방에 끝내고 싶다 ──▶ codex exec
```

## 3. OpenAI의 공식 권고

> "Codex App Server will be the first-class integration method we maintain moving forward."
> 기본적으로 App Server를 쓰라고 권장합니다.

각 경로의 트레이드오프에 대한 공식 코멘트:

**MCP 서버로 쓸 때**
> "you only get what MCP exposes, so Codex-specific interactions that rely on richer session semantics
> (e.g., diff updates) may not map cleanly through MCP endpoints."

**크로스 프로바이더 하네스 프로토콜(포터블 인터페이스)을 쓸 때**
> "these protocols often converge on the common subset of capabilities, which can make richer interactions
> harder to represent, especially when provider-specific tool and session semantics matter."
> 다만 이 공간은 빠르게 변하고 있고, skills처럼 공통 표준이 더 나올 것으로 예상한다고 덧붙입니다.

**App Server의 비용**
> "The main cost is integration work, since you need to build the client-side JSON-RPC binding in your language.
> In practice, however, Codex is able to do a lot of the heavy lifting if you feed it the JSON schema and documentation."

## 4. App Server 통합 시 실무 체크리스트

### 초기 설계
- [ ] **버전 핀 전략 결정** — 바이너리를 번들해 핀 고정(VS Code/Desktop 방식) vs
      클라이언트 고정 + 서버만 갱신(Xcode 방식). 프로토콜이 하위 호환이므로 후자가 릴리스 주기 분리에 유리.
- [ ] `codex app-server generate-ts` 또는 `generate-json-schema`로 **바인딩 생성** (수기 작성 금지)
- [ ] `initialize`의 `capabilities`에서 필요한 옵트인만 켜기
      (`experimentalApi`는 켜면 표면이 크게 늘어나므로 실제로 쓸 때만)
- [ ] `optOutNotificationMethods`로 **안 쓰는 알림 차단** — 84종을 다 처리할 필요 없음

### 렌더링
- [ ] `item/started` → 즉시 플레이스홀더 렌더 → `*/delta`로 증분 → `item/completed`로 확정하는
      3단 파이프라인을 UI에 구현 (이게 프로토콜이 의도한 사용법)
- [ ] `serverRequest/resolved`를 처리해 **다른 경로로 해소된 승인 요청**을 UI에서 정리
- [ ] `thread/status/changed`, `thread/tokenUsage/updated`로 상태 표시

### 승인 / 안전
- [ ] `item/commandExecution/requestApproval`, `item/fileChange/requestApproval`,
      `item/permissions/requestApproval` 3종은 **반드시 구현** — 미구현 시 턴이 멈춤
- [ ] 결정값은 `accept` / `acceptForSession` / `decline` / `cancel` + amendment 계열
- [ ] 샌드박스 정책을 제품 요구에 맞게 고정 (`readOnly` / `workspaceWrite` / `dangerFullAccess` / `externalSandbox`)

### 에러 / 복원력
- [ ] `turn/completed`의 `status: "failed"` + `codexErrorInfo`로 분기
      (`ContextWindowExceeded`, `UsageLimitExceeded`, `HttpConnectionFailed`, `SandboxError`)
- [ ] JSON-RPC 에러는 **메시지 텍스트가 아니라 `{type, reason}` 값으로 분기**
- [ ] 백프레셔: 큐 포화 시 `-32001` → 지수 백오프 + 지터
- [ ] 재연결 설계 — 웹처럼 세션이 휘발적인 환경이면 **상태는 서버에 두고** thread 재개로 복구

### 앱 고유 기능 연결
- [ ] 앱이 소유한 MCP 서버를 붙여 비즈니스 데이터/액션 노출
- [ ] 동적 도구가 필요하면 `item/tool/call` 서버 요청 처리
- [ ] `thread/attachment/*`로 PR·티켓 등 외부 리소스를 thread에 연결
      (identity key 규약을 팀 전체가 공유해야 표면 간 일치)

### 함정
- [ ] `turn/start`의 오버라이드는 대부분 **이후 턴에도 남는다(sticky)** — 한 턴만 바꾸려면 되돌려야 함
- [ ] `thread/rollback`은 **제거됨** → `thread/revert` 사용
- [ ] `disabledPluginIds`는 현재 **저장만 되고 실제 능력 필터링은 안 함**
- [ ] 살아있는 내부 워커가 붙은 thread는 archive/delete 불가 (`-32600`)
- [ ] `mcpServerStatus/list`의 `serverCapabilities`는 초기화 실패 시 `null` — 도구 목록으로 추론 금지

## 5. 보안 관점

- 신뢰할 수 없는 콘텐츠는 **사용자 입력과 타입을 분리**하세요.
  Python SDK의 `ExternalMessage`가 그 예 — 도구 수준 권한은 유지하되 사용자 승인 권한은 부여하지 않습니다.
- 승인 게이트는 UI 편의가 아니라 **프로토콜 레벨의 안전 장치**입니다.
  자동 승인(`item/autoApprovalReview/*`, `autoApprovalReview/strictReviewRequired`)을 켤 때
  어떤 조건에서 엄격 검토로 승격되는지 확인하세요.
- 셀프호스팅 Agents API 환경은 **아웃바운드 전용**(`api.openai.com`, `wss://codex-cloud-environments.chatgpt.com`)이라
  인바운드 포트를 열 필요가 없습니다. 실행기 키는 **제한된 executor key**를 쓰세요.
- Agents API는 현재 **미국 데이터 레지던시만** 지원하고 **ZDR 미지원**입니다.
  셀프호스팅 샌드박스를 써도 ZDR 자격이 생기지 않습니다.
