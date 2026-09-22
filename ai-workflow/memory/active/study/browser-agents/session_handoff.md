<!-- standard-ai-workflow-kit: v1.10.0 -->

# Session Handoff

- Purpose: Compact restore context for the next AI agent session.
- Scope: current focus, task status, key changes, next actions, risks
- Audience: AI agents, maintainers
- Status: active
- Updated: 2026-09-22
- Related docs: [SCOPE](../../../../browser-agents/SCOPE.md), [state.json](./state.json), [backlog](./backlog/)

## Current Focus

- 브랜치 `study/browser-agents` 1차 세션 (2026-09-22) — 브라우저형 에이전트 도구 조사를 새로 시작했다. Aside 중심 문서 8편 작성 완료. 기존 Codex 조사(`docs/`)와는 별개 주제다.

## Work Status

- TASK-2026-09-22-browser-agents-001 브라우저형 에이전트 도구 조사 — Aside 중심: done

## 현재 `in_progress` 작업

-

## 현재 `blocked` 작업

-

## Key Changes

- `browser-agents/` 신설 — README, SCOPE, 문서 8편 (판세 / Aside 심층 / Aside UX / Comet 아키텍처 / 비교군 / 교차분석 / 보안 / 출처).
- `docs.aside.com` 의 `.md` + `/llms.txt` 수법으로 Aside 제품 문서 16종을 **1차 텍스트로** 확보. 기존 조사가 OpenAI 문서에서 쓴 것과 같은 기법 — 두 번째 사례다.
- 루트 `README.md` 에 이 브랜치 조사로 가는 포인터 추가.

## Next Actions

- [ ] **scope 결정이 필요하다** — `browser-agents/SCOPE.md` 의 A/B/C 중 선택. 공용 `PURPOSE.md` 의 제외 영역과 충돌하며, 이를 말없이 고치지 않았다.
- [ ] Aside 를 실제 설치해 UI/UX 1차 확인 (승인 흐름·진행 상태 표현이 문서에 없다)
- [ ] `aside repl` / `aside mcp` 실제 표면 확인 — 구조적으로 가장 흥미로운 부분
- [ ] Aside 네트워크 트래픽 관찰 → "local-first" 주장 실증
- [ ] 문서 언어 결정 — 이번엔 한국어로 썼다. `docs/` 는 영어이고 PROJECT_PROFILE §6 은 "문서 본문은 영어"라 적혀 있다. 기존 Codex 조사도 한국어로 시작해 나중에 일괄 번역한 이력이 있어 같은 경로를 택했다. main 병합 전 결정 필요.

## Risks & Blockers

- **공용 PURPOSE.md 와의 scope 충돌 미해소** — 위 Next Actions 첫 항목. 병합 전 반드시 정리.
- 이 분야는 분기 단위로 뒤집힌다. 조사 기간 중에만 Atlas 종료(2026-08), Comet 무료화(2026-03)가 있었다. `99-sources.md` §4 의 불일치 항목과 §8 유효기간 참조.
- 제품을 직접 실행하지 못했다 — 시각 디자인과 실제 UI 는 미확인이며 추정으로 채우지 않았다.
- 위키 재색인 훅(`scripts/check_wiki_freshness.py`)은 `docs/` 만 매핑한다. `browser-agents/` 는 concept 페이지가 없어 훅이 아무 말도 하지 않는다 — 이 조사도 위키에 올릴지는 별도 결정.
