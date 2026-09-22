<!-- standard-ai-workflow-kit: v1.10.0 -->

# Master Knowledge Index

> 형식과 규칙은 [`./SCHEMA.md`](./SCHEMA.md). ingest 가 page 를 만들 때마다 항목이 추가된다.
> 원 소스는 저장소 루트의 `docs/` 16편과 `REPORT.md` — 위키는 그것을 **개념 축으로 재색인**한 계층이다.

## Concepts

### [[concepts/harness]] {#harness}
모델과 과업 사이의 실행 시스템. 내부 구성요소, 4계층 개방 구조, 표면 104 메서드 중 루프는 20%.

### [[concepts/harness-engineering]] {#harness-engineering}
손으로 쓴 코드 0으로 5개월. 병목은 모델이 아니라 환경이었다 — legibility, 기계적 집행, 지속적 GC.

### [[concepts/thread-turn-item]] {#thread-turn-item}
대화 원시형 셋. item 생명주기, thread 언로드(60초)와 용량 축출, turn override 의 sticky 의미론.

### [[concepts/approval-gate]] {#approval-gate}
승인을 UI 편의가 아니라 프로토콜 원시형으로. 서버→클라이언트 요청 10종, 구현하지 않으면 turn 이 멈춘다.

### [[concepts/wire-protocol-boundary]] {#wire-protocol-boundary}
`WireApi` 변형은 하나뿐 — Responses. 코어 재사용 가능성을 가르는 경계와 `responses_lite` 라는 두 번째 요청 형태.

### [[concepts/stateless-conversation-wire]] {#stateless-conversation-wire}
`store: false` + `previous_response_id` 부재 = 세션 저장소·id 레지스트리·만료 처리 전부 면제.

### [[concepts/retained-reasoning]] {#retained-reasoning}
유지된 추론은 최적화가 아니라 설계의 하중 부재. Chat Completions 로 건너가면 구조적으로 사라진다.

### [[concepts/control-plane-execution-plane]] {#control-plane-execution-plane}
harness(루프·라우팅)와 compute(파일·명령)의 분리, 그리고 그 경계가 강제하는 키 분리.

### [[concepts/execution-environment-topology]] {#execution-environment-topology}
`none` / `openai_hosted` / `self_hosted` 세 형태, 파일·아티팩트 비대칭, self-hosted 생명주기, 프로바이더 명단 두 개.

### [[concepts/os-sandbox-policy]] {#os-sandbox-policy}
정책 4값과 OS별 기전. Windows 두 모드, 네트워크의 독립된 두 스위치, OS package identity 로부터의 권한.

### [[concepts/capability-distribution]] {#capability-distribution}
plugin·marketplace·skill 유통. 벤더 중립 manifest, 카탈로그와 설치본의 분리, install ≠ enable ≠ share.

### [[concepts/provider-as-data]] {#provider-as-data}
프로바이더를 코드 분기가 아니라 데이터로. 커맨드 기반 토큰 발급, 프로젝트 로컬 설정 deny-list.

### [[concepts/primary-source-verification]] {#primary-source-verification}
이 저장소의 인식 방법. 등급 어휘, 반증의 보존, 검증한 2차 출처 5건 중 2건이 틀렸다는 기록.

## Topics

## Patterns

## Decisions

## Entities
