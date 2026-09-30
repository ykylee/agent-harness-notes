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

- **`check_wiki_freshness.py` 가 stale 6건을 알린다. 고치지 말고 읽어라.** 이번 커밋(`aa528cc`)은
  `--no-verify` 로 相关 있는 concept 2개만 담았다. 나머지 6개
  (`agent-client-protocol`·`os-sandbox-policy`·`thread-turn-item` ← `docs/02`;
  `capability-distribution`·`harness` ← `docs/12`; `retained-reasoning` ← `docs/99`)
  는 **이번 드리프트와 무관**하므로 내용 변경 없이 남겼다. 이력 모드가
  "원 문서 커밋 시각 > concept 커밋 시각" 으로만 판정하므로 stale 로 뜬다
  (`scripts/check_wiki_freshness.py:112` `check_history`). **커밋이 끝난 뒤 자동으로 생기는 상태이지
  새 누락이 아니다.** 해당 `docs/` 를 다음에 다시 건드릴 때 그때 갱신한다.
  참고로 `os-sandbox-policy` 가 인용하는 `bcd6d9ab6b` 는 여전히 유효 — 그 커밋 이후 샌드박스 변경이 없다.
- `docs/` 본문 반영은 끝났다: `02` §9 에 `ThreadGoalSetParams`/`ClearParams` 절 신설,
  `12` §2.2 goals 항목 보강, `99` §E.5 드리프트 기록 + 헤더 기준선 갱신.
- [`backlog/tasks/TASK-2026-09-30-feat-auto-20260930-a5e9e422-001.md`](./backlog/tasks/TASK-2026-09-30-feat-auto-20260930-a5e9e422-001.md) 의 남은 follow-up 2건:
  `SYNTHESIS.md` §2 에 게이트 가용성 축 편입 여부, `model_catalog_in_context` 의 providers-as-data 해석.
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
- **`check_wiki_freshness.py` 가 stale 6건을 알린다 — 새 누락이 아니다**(§5 첫 항목). 커밋이 끝난 뒤
  자동 생성되는 상태이고, 근거 없는 concept 갱신으로 메우면 개념 축이 오염된다.
- `model_catalog_in_context` 는 providers-as-data 축에 어떻게 붙는지 판단하지 않았다. §2.3 의
  "공유 wire 전제" 한정과 관계가 있을 수 있으나 **미분석** — 단정하지 말 것.
- main 브랜치의 `TASK-2026-09-27-main-002`(agent-ux GUI 패스)는 이 워크스페이스에 넘어오지 않았다.
  앱별 스크래치 프로젝트 지정이 여전히 필요한 blocked 상태.
