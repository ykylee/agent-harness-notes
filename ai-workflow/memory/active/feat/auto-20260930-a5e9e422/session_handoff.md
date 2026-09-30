# Session Handoff

- 문서 목적: 다음 세션이 바로 이어받을 수 있도록 현재 상태를 요약한다.
- 범위: 현재 기준선, 진행 상태, 다음 시작 포인트, 남은 리스크
- 대상 독자: AI agent, 저장소 관리자
- 상태: active
- 최종 수정일: 2026-09-30
- 관련 문서: [backlog](./backlog/), [sessions](./sessions/)

## 1. 현재 작업 요약

- 현재 기준선: Codex 드리프트 1차 대조 완료. `bcd6d9ab6b` → `92bc601ad6` **8커밋·134파일·+2462/−598**(전부 2026-09-30자)을 소스로 읽었다. **다음 드리프트 기준선은 `92bc601ad6`.**
- 현재 주 작업 축: 조사 드리프트 점검 — Codex / Strands / ACP 기존 사실을 1차 출처로 재확인 (main 기준선 계승)
- 범위 밖(건드리지 않는다): 구현 코드 편입 (PURPOSE §0.1 — 측정만), GUI/기기 관찰, heddle 작업

## 2. 진행 중 작업

- 현재 `in_progress` 작업:
- TASK-2026-09-30-feat-auto-20260930-a5e9e422-001 — Codex 2026-09-30 이후 드리프트 대조 (bcd6d9ab6b 이후)

## 3. 차단 작업

- 현재 `blocked` 작업:

## 4. 최근 완료 작업

- 최근 완료 작업 목록:

## 5. 다음 세션 시작 포인트

- **`docs/` 본문에 `thread/goal/*` params 목록이 있는지 먼저 grep 한다.** 있으면 `origin` 필드를 반영하고, `docs/99-sources.md` §E 에 드리프트 2건을 기록한다. 반영 전까지 위 발견은 **소스 확인만 되고 문서 미반영** 상태다.
- [`backlog/tasks/TASK-2026-09-30-feat-auto-20260930-a5e9e422-001.md`](./backlog/tasks/TASK-2026-09-30-feat-auto-20260930-a5e9e422-001.md) 의 Follow-up 3건.
- 작업 범위를 벗어나는 변경은 다른 워크스페이스와 충돌할 수 있으므로 backlog 에 별도 task 로 남긴다.

#### 이번 세션 발견 (소스 ✅ / 라이브 ⚠️)

- **`thread/goal/set` · `thread/goal/clear` params 에 `origin` 신설** — enum `user` | `automatic`. 계약 문구는 "Missing provenance does not supply user authorization." 서버는 `origin == User` 일 때만 user fragment 를 히스토리에 기록한다. `thread_goal_user_context.rs:2` — "tool-created goals never use this path." **기록 출처 판별자이지 새 권한 토큰이 아니다.**
- **Guardian 스킵 warmup** (`a5cce8895a`) — primary executor 오프라인에도 Guardian 이 네트워크 권한을 deny 해야 한다는 회귀 테스트가 붙었다. **게이트의 가용성과 정확성이 분리된 축**이라는 증거.
- **`model_catalog_in_context`** (`2e5fea64ee`, off 기본) — `spawn_agent` 설명의 모델 목록을 developer `<model_catalog>` 메시지로. providers-as-data 축 후보.
- 나머지(`d42056091a` fork 단축키 · `0b43721d8d` TUI 복사)는 기록 대상 아님. thread-store 내부 4커밋도 클라이언트 계약이 아니다.

#### 작업 후보 — 정본은 `state.json` 의 `planned_items` · `in_progress_items`

- TASK-2026-09-30-feat-auto-20260930-a5e9e422-001 — Codex 2026-09-30 이후 드리프트 대조 (bcd6d9ab6b 이후)

## 6. 남은 리스크

- 위 발견은 **전부 소스 읽기**다. 라이브 앱서버에 `origin` 이 실제로 어떻게 오가는지는 관찰하지 않았다(⚠️).
- `docs/` 문서가 이미 옛 wire 를 적고 있을 가능성을 아직 grep 으로 확인하지 않았다 — 반영 누락 여부는 다음 세션 첫 수.
- main 브랜치의 `TASK-2026-09-27-main-002`(agent-ux GUI 패스)는 이 워크스페이스에 넘어오지 않았다. 앱별 스크래치 프로젝트 지정이 여전히 필요한 blocked 상태.
