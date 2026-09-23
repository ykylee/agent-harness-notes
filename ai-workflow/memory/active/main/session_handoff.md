<!-- standard-ai-workflow-kit: v1.10.0 -->

# Session Handoff

- Purpose: Compact restore context for the next AI agent session.
- Scope: current focus, task status, key changes, next actions, risks
- Audience: AI agents, maintainers
- Status: active
- Updated: 2026-09-23 (브라우저형 에이전트 조사 병합)
- Related docs: [Project Profile](../../../docs/PROJECT_PROFILE.md), [PURPOSE](../PURPOSE.md), [SYNTHESIS](../../../SYNTHESIS.md), [state.json](./state.json), [backlog](./backlog/)

## Current Focus

- 2026-09-23 — `study/browser-agents` 를 병합해 **저장소 범위가 '에이전트 하네스 조사'로 확장**됐다. 조사가 둘이 됐고(`docs/` Codex · `browser-agents/` 브라우저형), 위키 개념층이 둘을 재색인하며, `SYNTHESIS.md` 가 교차 종합이다. 다음 축은 여전히 **기존 사실의 드리프트 점검**이다.

## Work Status

- TASK-2026-09-22-agent-harness-notes-001 표준 AI 워크플로우 초기 도입: done
- TASK-2026-09-22-agent-harness-notes-002 openai/codex 드리프트 재확인: planned
- TASK-2026-09-22-agent-harness-notes-003 Agents API 서버측 모델 목록 검증: planned
- TASK-2026-09-22-agent-harness-notes-004 Windows 샌드박스 내부 구조 추론→확인 승격: planned
- TASK-2026-09-22-agent-harness-notes-005 wiki concepts 계층 구성: done
- TASK-2026-09-22-agent-harness-notes-006 docs 수정 시 위키 재색인 강제: done
- TASK-2026-09-22-browser-agents-001 브라우저형 에이전트 도구 조사 — Aside 중심: done
- TASK-2026-09-23-browser-agents-002 Aside 코드레벨 분석 — CLI 바이너리 추출: done
- TASK-2026-09-23-browser-agents-003 Aside 브라우저 바이너리 정적 분석: done
- TASK-2026-09-23-browser-agents-004 Aside 권한 집행·Computer Use·암호층 분석: done
- TASK-2026-09-23-browser-agents-005 Dia·Neon 1차 출처 심화: done
- TASK-2026-09-23-browser-agents-006 두 조사 융합 — 위키 개념층 + 교차 종합: done
- TASK-2026-09-23-browser-agents-007 문서 언어 영어 통일: done

## 현재 `in_progress` 작업

-

## 현재 `blocked` 작업

-

## Key Changes

- **`study/browser-agents` 병합 (2026-09-23)** — `--no-ff` 로 8커밋을 하나의 조사 단위로 남겼다.
- **공용 `PURPOSE.md` 확장** — §0 에 범위 확장 기록. 제외 영역에서 "OpenAI 외 벤더" 삭제, Goals G5(표면 무관/고유 축 구분) 추가. `SCOPE.md` A안의 조건 이행.
- `browser-agents/` 14편, `SYNTHESIS.md`, 위키 개념 13 → **16종**.
- **내용 문서 전체 영어**. 규칙은 `docs/PROJECT_PROFILE.md` §6.
- 재색인 훅(`scripts/check_wiki_freshness.py`)이 `last_ingested_from` 을 통해 **두 트리를 자동으로 덮는다**.

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
