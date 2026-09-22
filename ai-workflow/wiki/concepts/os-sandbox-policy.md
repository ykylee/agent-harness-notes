---
type: concept
status: active
last_ingested_from: docs/14-windows-sandbox.md + docs/02-app-server-protocol.md
related_pages: [concepts/approval-gate, concepts/control-plane-execution-plane, concepts/execution-environment-topology, concepts/primary-source-verification]
created: 2026-09-22
updated: 2026-09-22
---

# OS Sandbox Policy — 실행 면 안쪽의 방어

- 문서 목적: 프로토콜 수준 샌드박스 모드와 OS 수준 구현(특히 Windows 네이티브)을 정리하고, 커스텀 하네스가 그대로 옮길 만한 설계 원칙을 뽑는다.
- 범위: 4개 정책 값, OS별 기전, Windows 두 모드, 네트워크의 두 스위치, 권한 모델
- 1차 출처: 생성 스키마, `learn.chatgpt.com/docs/windows/windows-sandbox.md`, `codex-rs/windows-sandbox-rs` 소스 트리
- 최종 수정일: 2026-09-22

## §1 TL;DR  {#s1-tldr}

| # | 항목 | 값 |
|---|---|---|
| 1 | 프로토콜 정책 값 | `readOnly` · `workspaceWrite` · `dangerFullAccess` · `externalSandbox` |
| 2 | Windows 네이티브 모드 | `elevated` (권장) · `unelevated` (대체) |
| 3 | 기본 UI 격리 | **private desktop** — 둘 다 기본 활성 |
| 4 | 네트워크 | **스위치가 둘이다** — "허용되는가" 와 "정책으로 제한되는가" |
| 5 | 권한의 출처 | **OS package identity**. 경로나 manifest 문자열이 아니다 |
| 6 | Windows 내부 구조의 근거 | ⚠️ **모듈명에서 추론** — 산문 문서가 아님 |

## §2 프로토콜 수준 정책  {#s2-protocol-policy}

| 값 | 의미 |
|---|---|
| `readOnly` | 읽기 전용 파일시스템 |
| `workspaceWrite` | 지정된 root 안에서만 쓰기 허용 |
| `dangerFullAccess` | 무제한 |
| `externalSandbox` | **클라이언트가 샌드박스를 직접 관리** |

선택적 `networkAccess` 설정이 아웃바운드 연결을 통제한다.

## §3 OS 별 기전  {#s3-os-mechanisms}

| OS | 기전 |
|---|---|
| **macOS** | `sandbox-exec` 의 Seatbelt 정책 (`--sandbox` 모드에 대응하는 `-p` 프로파일). 제한된 읽기 접근이 플랫폼 기본값을 켤 때는 `/System` 을 넓게 허용하는 대신 **큐레이션된 macOS 플랫폼 정책**을 덧붙인다 |
| **Linux** | `bwrap` + `seccomp` |
| **Windows (WSL2)** | Linux 샌드박스 구현을 그대로 |
| **Windows (native)** | 전용 Windows 샌드박스 구현 |

> WSL1 은 Codex `0.114` 까지 지원됐다. **`0.115` 부터 Linux 샌드박스가 `bwrap` 으로 옮겨가면서
> WSL1 은 더 이상 지원되지 않는다.**

## §4 Windows 네이티브 두 모드  {#s4-windows-modes}

```toml
[windows]
sandbox = "unelevated"          # 또는 "elevated"
# sandbox_private_desktop = true  # 기본값; 호환성 때문일 때만 false
```

| 모드 | 기전 | 요건 |
|---|---|---|
| **`elevated`** (권장) | 전용 저권한 샌드박스 사용자, 파일시스템 권한 경계, 방화벽 규칙, 필요한 로컬 정책 변경 | 관리자 승인 셋업 |
| **`unelevated`** (대체) | 현재 사용자에서 파생된 **제한된 Windows 토큰**, ACL 기반 파일 경계, 전용 offline-user 방화벽 규칙 대신 **환경 수준 오프라인 통제** | 없음 |

> 둘 다 가능하면 `elevated` 를 쓴다. `unelevated` 는 "관리자 승인 셋업이 로컬/기업 정책에 막힐 때
> 여전히 쓸모 있는" 약한 모드다.

관리자는 `requirements.toml` 로 허용 구현을 제약할 수 있다 — `elevated` 를 **요구하고 fallback 을
막을** 수 있고, 둘 다 나열하면 아무거나 되며, 미선택 시 Codex 는 `elevated` 를 선호한다.

> 형태에 주목: **관리자 산출물이 사용자 설정과 별도 파일**이고, 단일 값이 아니라 **허용 집합**을
> 표현한다. 커스텀 하네스가 그대로 옮길 만한 모양이다.

### §4.1 private desktop  {#s4-1-private-desktop}

두 모드 모두 기본적으로 **더 강한 UI 격리를 위해 private desktop 을 쓴다**.
`windows.sandbox_private_desktop = false` 는 옛 `Winsta0\Default` 동작이 호환성 때문에 필요할 때만.

> 대부분의 하네스가 잊는 방어다 — 데스크톱 격리가 없으면 샌드박스 안의 GUI 프로세스가 대화형
> 데스크톱에 닿아 다른 창을 조종할 수 있다.

## §5 네트워크 — 독립된 두 스위치  {#s5-network}

`workspace-write` 기본값은 네트워크를 끈 상태다.

```toml
[sandbox_workspace_write]
network_access = true          # 스위치 1: 네트워크가 아예 허용되는가

[features.network_proxy]
enabled = true                 # 스위치 2: 그 트래픽이 정책으로 제한되는가
domains = { "api.openai.com" = "allow", "example.com" = "deny" }
```

> **도메인 규칙을 추가하는 것만으로 프록시가 켜지지 않는다.** 두 스위치는 독립이다.

보안 문서는 DNS rebinding 방어, 로컬/사설 목적지 처리, 명령 네트워크 프록시를 빠져나가는 트래픽도
다룬다 — 커스텀 구현이 **상속받는 것이 아니라 명시적으로 다뤄야** 할 영역이다.

## §6 구현 구조 — 추론임을 명시  {#s6-implementation}

> ⚠️ **추론 경고**: 아래는 `codex-rs/windows-sandbox-rs` 와 `windows-sandbox-service` **소스 트리의
> 모듈명과 배치**에서 읽은 것이지 산문 문서가 아니다. 명세가 아니라 **문제 공간의 지도**로 다룬다.
> 등급의 의미는 [[concepts/primary-source-verification]].

| 영역 | 모듈 |
|---|---|
| 패키지/프로세스 정체성 | `app_package.rs`, `package_identity.rs`, `service_identity.rs`, `identity.rs` |
| 토큰 제한 | `token.rs`, `token_user.rs`, `token_groups_tests.rs` |
| 파일시스템 ACL | `acl.rs`, `workspace_acl.rs`, `deny_read_acl.rs`, `deny_read_resolver.rs`, `deny_read_walker.rs`, `file_write.rs` |
| symlink/reparse 방어 | `no_reparse_dir.rs`, `path_normalization.rs` |
| 네트워크 필터링 | `wfp.rs`, `wfp_setup.rs` (Windows Filtering Platform) |
| 데스크톱 격리 | `desktop.rs`, `hide_users.rs` |
| 터미널 | `conpty/`, `unified_exec/`, `stdio_bridge.rs` |
| 비밀 저장 | `dpapi.rs` |
| 상승·셋업 | `elevated/`, `setup.rs`, `setup_launch.rs`, `setup_provisioning.rs`, `setup_mutex.rs`, `installation_record.rs` |
| 특권 서비스 | `windows-sandbox-service`: `service.rs`, `ipc.rs`, `provisioning.rs`, `machine_policy.rs`, `package_lifecycle.rs`, `registered_runtime.rs` |
| 감사 | `audit.rs`, `logging.rs` |

구조적 결론 둘:

1. **elevated 모드는 특권 Windows 서비스를 요구한다.** `windows-sandbox-service` 는 자체 IPC ·
   provisioning · machine policy 를 갖는 별도 crate 다. 단일 사용자 모드 프로세스로는 불가능하니
   **설치 프로그램과 서비스 생명주기를 일찍 계획**해야 한다.
2. **셋업은 부수효과가 아니라 1급의 재개 가능한 연산이다.** `setup_mutex.rs`,
   `installation_record.rs`, 그리고 §7 의 프로토콜 메서드가 그 증거다.

## §7 권한 모델 — 옮길 만한 원칙  {#s7-authority}

소스 주석이 권한 모델을 그대로 말한다:

> "Select the requested runtime without inferring authority from directory or manifest text.
> Registered runners still require OS package identity and the exact staged runner image."

**권한은 OS package identity 에서 나오지 경로나 manifest 문자열에서 나오지 않는다.**
어떤 샌드박스 설계에도 옮겨지는 원칙이다.

## §8 프로토콜 표면과 그것이 말하는 것  {#s8-protocol-surface}

| 방향 | 메서드 | 역할 |
|---|---|---|
| C→S | `windowsSandbox/setupStart` | 셋업 시작 (elevated 경로는 관리자 승인 필요) |
| C→S | `windowsSandbox/readiness` | 준비 상태 조회. 파라미터 없음 |
| S→C | `windowsSandbox/setupCompleted` | 셋업 완료 |
| S→C | `windows/worldWritableWarning` | world-writable 경로 감지 |

> 전용 **readiness** RPC 와 **setupCompleted** 알림이 있다는 사실이 말하는 것: 셋업은 비동기이고,
> turn 보다 오래 살 수 있고, UI 에 드러나야 한다. Windows 를 겨냥하는 커스텀 하네스는 같은 2단계
> 모양이 필요하다 — **샌드박스 가용성을 부팅 시점 boolean 으로 다룰 수 없다.**

`windows/worldWritableWarning` 은 개념으로 옮길 가치가 있다 — 샌드박스가 올바르게 설정돼 있어도
느슨한 경로 하나가 그것을 무력화할 수 있으므로, **탐지는 집행과 별개**다.

## §9 다음에 읽을 문서  {#s9-next}

- [[concepts/approval-gate]] — 샌드박스가 막지 못하는 지점의 사람 개입
- [[concepts/control-plane-execution-plane]] — 이 방어가 놓이는 면
- 원문: [`docs/14-windows-sandbox.md`](../../../docs/14-windows-sandbox.md)
