# Session Handoff

- 문서 목적: 다음 세션이 바로 이어받을 수 있도록 현재 상태를 요약한다.
- 범위: 현재 기준선, 진행 상태, 다음 시작 포인트, 남은 리스크
- 대상 독자: AI agent, 저장소 관리자
- 상태: active
- 최종 수정일: 2026-09-30
- 관련 문서: [backlog](./backlog/), [sessions](./sessions/)

## 1. 현재 작업 요약

- 현재 기준선: **조사 축 4개(Codex · Strands · ACP · Gas Town) 처리 완료, 이 워크스페이스에 남은 ⚠️ 0건.**
- **드리프트 축 3곳은 전부 대조 완료, 반박 0건.** 다음 기준선 — Codex `92bc601ad6` ·
  Strands `4dfeca8c` · ACP `7d794e0e`(문서 1건으로 추가 이동).
- **다섯 번째 조사 축 신설 — `gas-town/`** (Gas Town `649b832b76`). 목적은 **오케스트레이션 기법
  참고**였고 기법 11종(A1–A11)을 `gas-town/04` 에 발쑌다. 범위는 `PURPOSE.md` §0.3 에 선기재.
  위키 개념 **19종**(신규 `multi-agent-orchestration`). ⚠️ **관찰 0건 — 바이너리 미실행, 전부 source-read.**
- **정본 참조 클론을 확보했다** — `strands-harness-sdk`(`4dfeca8c74`) · `agent-client-protocol`
  (`7d794e0e2d`) · `gastown`(`649b832b76`). 이제 임시 클론이 필요 없다.
- 현재 주 작업 축: 1차 출처 기반 하네스 조사 (드리프트 대조 + 오케스트레이션) — main 기준선 계승
- 범위 밖(건드리지 않는다): 구현 코드 편입 (PURPOSE §0.1 — 측정만), GUI/기기 관찰, heddle 작업

## 2. 진행 중 작업

- 현재 `in_progress` 작업:
-

## 3. 차단 작업

- 현재 `blocked` 작업:
- TASK-2026-09-27-main-002 (main 워크스페이스 소관) — agent-ux GUI 패스, 앱별 스크래치 프로젝트 지정 대기

## 4. 최근 완료 작업

- 최근 완료 작업 목록:
- TASK-2026-09-30-feat-auto-20260930-a5e9e422-003 — Gas Town 오케스트레이션 조사: 기법 A1–A11, **control/execution plane 을 credential 경계로 강화**(`control-plane-execution-plane` §5.6 신설), 위키 19종.
- TASK-2026-09-30-feat-auto-20260930-a5e9e422-002 — Strands · ACP 드리프트 대조: Strands 2커밋(보안 계층 무변경), ACP 7커밋(stable 스키마 바이트 동일). **참조 클론 부재 발견** → 재생성.
- TASK-2026-09-30-feat-auto-20260930-a5e9e422-001 — Codex 8커밋 대조: goal API `origin` 신설, Guardian 스킵 warmup.

## 5. 다음 세션 시작 포인트

- **Gas Town 런타임 검증이 미완이다 — `gas-town/` 의 가장 큰 구멍.** 전부 소스 읽기였고 실행은 0건.
  `gt` 로 소규모(3~5 polecat) town 을 구성해 sling→merge 사이클을 재현하면 §5 의 Stalled/Zombie
  상태와 propulsion 이 **관찰** 가능해진다. 별도 task 로 등록하는 게 좋다.
- Gas City(분해 SDK)와 Beads standalone 은 미독 — 개념 축 연속성 확인용.

- **남은 ⚠️ 가 없다.** ACP #2223(승인과 무관함)·Strands 태그/버전 모두 해소됐다(§6).
  다음 수는 새 드리프트가 쌓이는 것 — Codex `92bc601ad6` · Strands `4dfeca8c` · ACP `7d794e0e` 이후.
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
- **ACP #2223 해소 — 승인과 무관하다.** `mcp/message` payload 에 `sessionId`·`toolCall`·`PermissionOption` 을 실을 자리가 없고, `MessageMcpResponse` 는 outer ACP error 를 "binding and runtime failures" 로 예약한다 → 거절된 MCP 호출은 *성공한* outer RPC. **근거는 페이로드 형태이지 "스키마 불변" 이 아니다.** 출처 `draft/schema.mdx` (앞선 ⚠️ 가 가리킨 `prompt-turn.mdx` +244줄은 subagent transcript 였다).
- **문서 오류 — 존재하지 않는 참조 클론 2개.** 두 문서가 정본 경로로 명시했으나 실재하지 않음 → 재생성함.
- **Gas Town(`649b832b76`)** — 오케스트레이션 축 신설. 코드에서 확인한 것: polecat spawn = `WorktreeAddFromRef`(신규)/`WorktreeAddExistingForce`(resume), merge "lock" = `gt:merge-slot` **bead 하나**(flock 아님), deacon 임계 5분/20분·재디스패치 5분. **기여하지 않는 축을 명시함** — approval 은 약화가 아니라 **대비**(post-hoc 신뢰 모델), provider-as-data 는 wire 전제 유지.

#### 작업 후보 — 정본은 `state.json` 의 `planned_items` · `in_progress_items`

- (없음 — 위 follow-up 으로 새 task 등록)

## 6. 남은 리스크

- 위 발견은 **전부 소스 읽기**다. 라이브 앱서버의 `origin` 트레이스, ACP 클라이언트 실동작은
  관찰하지 않았다(⚠️).
- **ACP #2223 은 해소됐다 — 무관하다.** `mcp/message` payload 에 `sessionId`·`toolCall`·
  `PermissionOption` 을 실을 자리가 없고, `MessageMcpResponse` 는 outer ACP error 를
  "binding and runtime failures" 로 예약하므로 거절된 MCP 호출은 *성공한* outer RPC 다.
  **근거는 페이로드의 형태이지 "안정 스키마가 안 바뀌었으므로" 가 아니다** — 후자는 근거 부재를
  증거로 읽는 것이고, 이 저장소의 가장 반복된 실패 유형이다. 출처는 `draft/schema.mdx`.
  앞선 세션이 미독으로 남긴 `prompt-turn.mdx` +244줄은 subagent transcript 였다.
- **얇은 클론에서 나온 부정 결과를 기록하지 말 것.** Strands 태그 ⚠️ 는 `blob:none` 클론이 질의에
  답하지 못한 것이지 저장소 사실이 아니었다. 정본 클론에서 `v0.1.4-35` → `v0.1.4-37`, 새 태그 없음이
  확인됐다. `SYNTHESIS.md` §7 의 가짜 0 네 건과 같은 형태다.
- **`check_wiki_freshness.py` 의 stale 은 새 누락이 아니다**(§5). 커밋 방식의 산물이며,
  근거 없는 concept 갱신으로 메우면 개념 축이 오염된다.
- `model_catalog_in_context` 는 providers-as-data 축에 어떻게 붙는지 판단하지 않았다. §2.3 의
  "공유 wire 전제" 한정과 관계가 있을 수 있으나 **미분석**.
- **`gas-town/` 은 관찰 0건이다.** `gt`/`bd` 바이너리를 실행하지 않았고 town·Dolt 서버를 만들지
  않았다. §5 Stalled/Zombie 상태와 propulsion 은 **소스 읽기 결과이며 관찰된 사실이 아니다.**
  "Kubernetes for AI agents"·"$100/hr"·"20–30 에이전트" 는 전부 자기보고(📣)로 채택하지 않았다.
- main 브랜치의 `TASK-2026-09-27-main-002`(agent-ux GUI 패스)는 이 워크스페이스에 넘어오지 않았다.
