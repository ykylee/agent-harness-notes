---
id: TASK-2026-09-22-agent-harness-notes-004
status: done
created_at: 2026-09-22
source_anchor: generic-task-2026-09-22-agent-harness-notes-004
source_path: backlog/2026-09-22.md
kind: generic
wbs: exempt
wbs_exempt_reason: 조사 로드맵 밖 기존 사실의 1차 출처 검증
---

# TASK-2026-09-22-agent-harness-notes-004 — Windows 샌드박스 내부 구조 추론→확인 승격

## 📝 Description

- Status: done
- Priority: medium
- Request date: 2026-09-22
- Owner: ykylee
- Host:
- Host IP:
- Affected documents:
  - `docs/14-windows-sandbox.md`
  - `docs/99-sources.md`
  - `REPORT.md`
  - `REPORT.ko.md`
  - `ai-workflow/wiki/concepts/os-sandbox-policy.md`
  - `ai-workflow/wiki/concepts/primary-source-verification.md`

- Description: windows-sandbox-rs 의 모듈명 추론으로 남은 ACL/WFP/토큰/데스크톱 메커니즘을 소스 본문 독해로 확정하거나 추론으로 확정 유지한다
- Completion criteria:

## 🛠️ Implementation / Content

- Progress: windows-sandbox-rs / windows-sandbox-service 소스 독해 완료. ACL/WFP/토큰/데스크톱 Win32 호출 확정.
- Next session starting point:
- Remaining risks:

## ✅ Outcome

- Result: Token: CreateRestrictedToken (DISABLE_MAX_PRIVILEGE|LUA_TOKEN|WRITE_RESTRICTED). ACL: SetNamedSecurityInfoW deny ACE.
- Result: Network: WFP 필터 12개 + INetFwPolicy2 오프라인 사용자 규칙. Desktop: CreateDesktopW CodexSandboxDesktop-*.
- Result: hide_users.rs 는 Winlogon 로그인 UI 숨김이지 데스크톱 격리가 아님. audit.rs 없음(logging.rs). Windows 런타임 미실시.
- Verification: HEAD bcd6d9ab6b. token.rs:500 flags. filter_specs 12 names. CreateDesktopW + PRIVATE_DESKTOP_PREFIX. INetFwPolicy2. hide_users SpecialAccounts\UserList. no audit.rs. official windows-sandbox.md HTTP 200. scripts/check_wiki_freshness.py --paths 통과. Windows 런타임은 Linux 호스트라 미실시.
- Follow-up: Windows 호스트에서 elevated/unelevated 런타임 실행은 디스플레이 있는 기기가 생길 때.
