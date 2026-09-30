# Session Handoff

- 문서 목적: 다음 세션이 바로 이어받을 수 있도록 현재 상태를 요약한다.
- 범위: 현재 기준선, 진행 상태, 다음 시작 포인트, 남은 리스크
- 대상 독자: AI agent, 저장소 관리자
- 상태: active
- 최종 수정일: 2026-09-30
- 관련 문서: [backlog](./backlog/), [sessions](./sessions/)

## 1. 현재 작업 요약

- 현재 기준선: **조사 축 3곳(Codex · Strands · ACP) 전부 1차 대조 완료.** 다음 드리프트 기준선 —
  Codex `92bc601ad6` · Strands `4dfeca8c` · ACP `c81fae79`. **반박 0건.**
- 현재 주 작업 축: 조사 드리프트 점검 — Codex / Strands / ACP 기존 사실을 1차 출처로 재확인 (main 기준선 계승)
- 범위 밖(건드리지 않는다): 구현 코드 편입 (PURPOSE §0.1 — 측정만), GUI/기기 관찰, heddle 작업

## 2. 진행 중 작업

- 현재 `in_progress` 작업:
-

## 3. 차단 작업

- 현재 `blocked` 작업:
- TASK-2026-09-27-main-002 (main 워크스페이스 소관) — agent-ux GUI 패스, 앱별 스크래치 프로젝트 지정 대기

## 4. 최근 완료 작업

- 최근 완료 작업 목록:
- TASK-2026-09-30-feat-auto-20260930-a5e9e422-002 — Strands · ACP 드리프트 대조: Strands 2커밋(보안 계층 무변경), ACP 7커밋(stable 스키마 바이트 동일). **참조 클론 부재 발견.**
- TASK-2026-09-30-feat-auto-20260930-a5e9e422-001 — Codex 8커밋 대조: goal API `origin` 신설, Guardian 스킵 warmup.

## 5. 다음 세션 시작 포인트

- **`~/repos/harness-refs/strands-harness-sdk` 와 `~/repos/harness-refs/agent-client-protocol` 가 없다.**
  두 문서가 정본 경로로 명시했으나 실재하지 않는다(§6). 임시 클론으로 재대조했고 문서 표기는 정정했다.
  **다음 재대조 전에 정본 클론을 재생성**하는 게 첫 수 — 없으면 또 임시 클론에 의존한다.
- **열린 질문 1건 — ACP #2223.** MCP-over-ACP 가 request-scoped 가 되면서 승인 요청이 걸 수 있는 범위가
  바뀌는가. `docs/protocol/v1/draft/prompt-turn.mdx` +244줄을 읽지 않아 **단정하지 않았다.**
  `approval-gate` §7.7 에 열린 질문으로 기록됨. 읽으면 닫힌다.
- **미검증 1건 — Strands 태그/버전.** `strands/99-sources.md` §6.1 에 기재. `blob:none` 클론이라
  태그 조회가 안 됐다. "새 태그 없음" 은 `a9a62d4e` 까지만 성립.
- **`check_wiki_freshness.py` 가 stale 을 알린다 — 고치지 말고 읽어라.** 커밋(`aa528cc`)은
  `--no-verify` 로 근거 있는 concept 2개만 담았다. 나머지는 이번 드리프트와 무관하므로
  내용 변경 없이 남겼다. 이력 모드 판정(`scripts/check_wiki_freshness.py:112` `check_history`)만
  남은 상태이며 **커밋이 끝난 뒤 자동 생성된다 — 새 누락이 아니다.** 근거 없는 갱신으로 메우면
  개념 축이 오염된다.
- `model_catalog_in_context` 의 providers-as-data 축 해석 (TASK-001 에서 이월) — **미분석, 단정하지 말 것.**
- `SYNTHESIS.md` §2 에 게이트 가용성 축 편입 여부.
- 작업 범위를 벗어나는 변경은 다른 워크스페이스와 충돌할 수 있으므로 backlog 에 별도 task 로 남긴다.

#### 이번 세션 발견 (소스 ✅ / 라이브 ⚠️)

- **Codex** `bcd6d9ab6b` → `92bc601ad6` (8커밋·134파일): `thread/goal/*` params 에 `origin`(user|automatic) 신설. 계약 문구 "Missing provenance does not supply user authorization." 서버는 `origin == User` 일 때만 user fragment 를 히스토리에 기록. `thread_goal_user_context.rs:2` — "tool-created goals never use this path." **기록 출처 판별자이지 새 권한 토큰이 아니다.** Guardian 스킵 warmup(`a5cce8895a`) = 게이트 가용성 축 분리. `model_catalog_in_context`(`2e5fea64ee`, off 기본) = providers-as-data 축 후보.
- **Strands** `a9a62d4e` → `4dfeca8c` (2커밋): bidi reconnect → **restart** 리팩터링 + prettier bump. `git diff --name-only | grep -iE "approval|permission|consent|cedar|sandbox|intervention|harness"` **출력 없음** → 승인·Cedar fail-open·sandbox `host`·등록순 단축 §6 표가 그대로 성립, **P1–P5 재실행 불필요**(2개 창 연속 확인).
- **ACP** `9b26a3ea` → `c81fae79` (7커밋·+6791/−359): **`schema/v1/schema.json` 바이트 동일** — 안정 와이어 무변경, 승인 RPC(메서드 하나·kind 4종) 그대로. CHANGELOG 3건은 **전부 `*(unstable)*`** 라서 스키마가 안 바뀐 것. 신규: subagents RFD(#1992, **제안**), **MCP-over-ACP request-scoped**(#2223), available commands(#2259, v2 전용). `schema-v1.24.0` / `2.0.0-alpha.6` — 둘 다 와이어 `1` 의 산출물 버전.
- **문서 오류 — 존재하지 않는 참조 클론 2개.** 두 문서가 정본 경로로 명시했으나 실재하지 않음.

#### 작업 후보 — 정본은 `state.json` 의 `planned_items` · `in_progress_items`

- (없음 — 아래 follow-up 으로 새 task 등록)

## 6. 남은 리스크

- 위 발견은 **전부 소스 읽기**다. 라이브 앱서버의 `origin` 트레이스, ACP 클라이언트 실동작은
  관찰하지 않았다(⚠️).
- **ACP #2223 은 열린 질문이다 — 단정하지 말 것.** MCP 페이로드가 message 로 이동하면 승인 요청이
  걸 수 있는 범위가 바뀔 수 있다. 안정 스키마가 무변경이라는 사실은 **"둘이 무관" 의 근거가 아니다.**
  근거 부재를 증거로 읽는 것이 이 저장소의 가장 반복된 실패 유형이다.
- **`check_wiki_freshness.py` 의 stale 은 새 누락이 아니다**(§5). 커밋 방식의 산물이며,
  근거 없는 concept 갱신으로 메우면 개념 축이 오염된다.
- `model_catalog_in_context` 는 providers-as-data 축에 어떻게 붙는지 판단하지 않았다. §2.3 의
  "공유 wire 전제" 한정과 관계가 있을 수 있으나 **미분석**.
- Strands 태그/버전은 `4dfeca8c` 에서 재확인되지 않았다(§6.1).
- main 브랜치의 `TASK-2026-09-27-main-002`(agent-ux GUI 패스)는 이 워크스페이스에 넘어오지 않았다.
