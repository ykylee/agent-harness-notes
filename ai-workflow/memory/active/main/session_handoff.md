<!-- standard-ai-workflow-kit: v1.10.0 -->

# Session Handoff

- Purpose: Compact restore context for the next AI agent session.
- Scope: current focus, task status, key changes, next actions, risks
- Audience: AI agents, maintainers
- Status: active
- Updated: 2026-09-22
- Related docs: [Project Profile](../../../docs/PROJECT_PROFILE.md), [state.json](./state.json), [backlog](./backlog/)

## Current Focus

- 1차 세션 (2026-09-22) — 조사 완결 상태의 문서 저장소를 표준 AI 워크플로우에 편입했다. 조사 내용 자체는 건드리지 않았다. 다음 축은 문서의 사실 드리프트 점검이다.

## Work Status

- TASK-2026-09-22-agent-harness-notes-001 표준 AI 워크플로우 초기 도입: done
- TASK-2026-09-22-agent-harness-notes-002 openai/codex 드리프트 재확인: planned
- TASK-2026-09-22-agent-harness-notes-003 Agents API 서버측 모델 목록 검증: planned
- TASK-2026-09-22-agent-harness-notes-004 Windows 샌드박스 내부 구조 추론→확인 승격: planned
- TASK-2026-09-22-agent-harness-notes-005 wiki concepts 계층 구성: done

## 현재 `in_progress` 작업

-

## 현재 `blocked` 작업

-

## Key Changes

- `ai-workflow/` 스캐폴딩 생성 (adoption-mode=existing, harness=claude-code). 기존 문서 16편·REPORT 2종은 무변경.
- `docs/PROJECT_PROFILE.md` 자리표시자 전부 실내용으로 교체 — 이 저장소에는 빌드·실행·테스트가 없고 "검증"은 **출처 재검증**을 뜻한다고 명시.
- `ai-workflow/memory/active/PURPOSE.md` 신규 작성 (G1–G4, Q1–Q4, 포함/제외 영역, evolving thesis).
- `.claude/` 진입점(CLAUDE.md, commands 4종, skill) 생성.
- `ai-workflow/wiki/` 계층 추가 + **concept 13종** 작성 — 기존 조사 문서에서 추출했을 뿐 새 조사는 없다.
  위키는 `docs/` 의 대체가 아니라 **개념 축 재색인**이고, 사실의 SSOT 는 `docs/` 에 남는다.
  원문의 추론·반증 등급을 페이지에서도 유지하는 것이 이 ingest 의 제약이었다.

## Next Actions

- [ ] TASK-002: 조사 기준일 2026-09-15 이후 `openai/codex` 변경분 대조. 재조사의 첫 수는 새 사실 수집이 아니라 기존 사실의 드리프트 확인이다.
- [ ] TASK-003: Agents API 서버측 모델 목록과 클라이언트 카탈로그 9종의 일치 여부 — `99-sources.md`에 유일하게 미확인으로 남은 항목.
- [ ] TASK-004: `windows-sandbox-rs` 내부 구조를 모듈명 추론에서 소스 독해로 승격.

## Risks & Blockers

- `openai/codex`는 빠르게 움직인다. 기존 문서의 결론을 뒤집는 수정은 사용자 확인을 거친다 (PROJECT_PROFILE §5).
- 위키 페이지의 `last_ingested_from` 이 원 문서를 가리킨다. `docs/` 를 고치면 해당 concept 페이지를 재ingest 해야 한다 — 지금은 이 동기화를 강제하는 장치가 없다.
- 로드맵(`roadmap/`)은 bootstrap 초안 그대로 4개 마일스톤이 전부 `planned`이다. 이 저장소는 SDLC 단계로 나누기 어려운 조사물이라 현 단계 선언을 보류했다 — 소유자 판단이 필요하다.
