<!-- standard-ai-workflow-kit: v1.10.0 -->

# Session Handoff

- Purpose: Compact restore context for the next AI agent session.
- Scope: current focus, task status, key changes, next actions, risks
- Audience: AI agents, maintainers
- Status: active
- Updated: 2026-09-23 (세션 종료)
- Related docs: [Project Profile](../../../docs/PROJECT_PROFILE.md), [PURPOSE](../PURPOSE.md), [SYNTHESIS](../../../SYNTHESIS.md), [state.json](./state.json), [backlog](./backlog/)

## Current Focus

- **2026-09-23 세션 종료 — 저장소 범위가 '에이전트 하네스 조사'로 확장됐고 브랜치 정리까지 끝났다.** 조사가 둘(`docs/` Codex · `browser-agents/` 브라우저형), 위키 개념 16종이 둘을 재색인, `SYNTHESIS.md` 가 교차 종합, `REPORT`(영/한)에 외부 증거 반영. `study/browser-agents` 브랜치는 병합 후 삭제했고 메모리는 `memory/archived/` 로 옮겼다. **남은 작업은 전부 기기나 동적 관찰을 요구하거나, 기존 사실의 드리프트 점검이다.**

## Work Status

- TASK-2026-09-22-agent-harness-notes-002 openai/codex 드리프트 재확인: planned
- TASK-2026-09-22-agent-harness-notes-003 Agents API 서버측 모델 목록 검증: planned
- TASK-2026-09-22-agent-harness-notes-004 Windows 샌드박스 내부 구조 추론→확인 승격: planned
- TASK-2026-09-23-main-010 REPORT 범위 확장 반영: done
- TASK-2026-09-23-main-009 번역이 깨뜨린 파서 라벨 복구: done
- TASK-2026-09-23-main-008 브랜치 병합 및 메모리 아카이브: done
- TASK-2026-09-23-browser-agents-007 문서 언어 영어 통일: done
- TASK-2026-09-23-browser-agents-006 두 조사 융합 — 위키 개념층 + 교차 종합: done
- TASK-2026-09-23-browser-agents-005 Dia·Neon 1차 출처 심화: done
- TASK-2026-09-23-browser-agents-004 Aside 권한 집행·Computer Use·암호층 분석: done
- TASK-2026-09-23-browser-agents-003 Aside 브라우저 바이너리 정적 분석: done
- TASK-2026-09-23-browser-agents-002 Aside 코드레벨 분석 — CLI 바이너리 추출: done
- TASK-2026-09-22-browser-agents-001 브라우저형 에이전트 도구 조사 — Aside 중심: done

> 상한(10) 이전의 완료 항목은 `backlog/tasks/` 에 있다 — 001·005·006 (워크플로우 도입, 위키 계층, 재색인 강제).

## 현재 `in_progress` 작업

-

## 현재 `blocked` 작업

-

## Key Changes

- **저장소 범위 확장** — `PURPOSE.md` §0 에 기록. 제외 영역에서 "OpenAI 외 벤더" 삭제, Goals G5 추가. `study/browser-agents` 의 A안 조건 이행.
- **조사가 둘이 됐다** — `browser-agents/` 14편 신설. Aside 는 제품 문서 1차 확보 후 **CLI·브라우저 바이너리까지 정적 분석**했다.
- **위키 개념 13 → 16종** — 기존 8종에 브라우저 근거 추가, 신규 3종(`perception-model`·`indirect-prompt-injection`·`credential-shielding`).
- **`SYNTHESIS.md` 신설** — 핵심 주장은 **표면 무관 축과 표면 고유 축의 구분**이다.
- **내용 문서 전체 영어**. 규칙과 예외는 `docs/PROJECT_PROFILE.md` §6.
- **`REPORT`(영/한)에 외부 증거 절 추가** — 권고 여럿이 서드파티 시스템에서 독립 구현된 것으로 확인됐다.
- 브랜치 병합(`--no-ff`)·삭제, 고아 메모리를 `memory/archived/` 로 아카이브.

## Next Actions

**Codex 조사 (`docs/`)**
- [ ] TASK-002: 조사 기준일 2026-09-15 이후 `openai/codex` 변경분 대조
- [ ] TASK-003: Agents API 서버측 모델 목록 — `docs/99-sources.md` 의 유일한 미확인 항목
- [ ] TASK-004: Windows 샌드박스 내부를 모듈명 추론에서 소스 독해로 승격

**브라우저 조사 (`browser-agents/`)**
- [ ] 검증 비대칭 해소 — Aside 만 바이너리까지 뜯었고 Dia·Neon 은 문서를 믿은 상태다
- [ ] `Aside Computer Use` 호출 흐름 추적 (심볼만 봤다)
- [ ] 동적 관찰 (서버로 가는 내용) — **기기 필요**
- [ ] 브라우저 GUI 1차 확인 — **macOS/Windows 기기 필요.** 리눅스 빌드가 없다

**저장소**
- [ ] `study/browser-agents` 브랜치 정리 여부 결정 (병합 완료, 원격에 남아 있음)
- [ ] `REPORT.md`/`REPORT.ko.md` 가 Codex 조사만 다룬다 — 범위 확장을 반영할지 결정

## Risks & Blockers

- **근거 등급이 칸마다 다르다.** Aside 는 바이너리까지, Dia·Neon 은 문서만, Comet 은 3자 리버싱이다. 비교표를 읽을 때 이 비대칭을 잊으면 안 된다 — `SYNTHESIS.md` §7 에 경고로 달아뒀다.
- 두 분야 모두 빠르게 낡는다. Codex 는 2026-09-15, 브라우저는 2026-09-22/23 기준이다. 재조사의 첫 수는 **기존 사실의 드리프트 확인**이다.
- `docs/` 또는 `browser-agents/` 를 고치면 **위키 재색인이 따라와야 한다.** pre-commit 훅이 막지만 `core.hooksPath` 를 설정한 clone 에서만 돈다 — 새 clone 에서는 `git config core.hooksPath .githooks` 가 필요하다.
- `wiki/SCHEMA.md` 는 kit 생성물이라 한국어로 남아 있다. 번역하면 kit 재생성과 갈린다.
