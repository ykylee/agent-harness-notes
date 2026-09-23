<!-- standard-ai-workflow-kit: v1.10.0 -->

# Session Handoff

- Purpose: Compact restore context for the next AI agent session.
- Scope: current focus, task status, key changes, next actions, risks
- Audience: AI agents, maintainers
- Status: active
- Updated: 2026-09-23 (2차 세션)
- Related docs: [SCOPE](../../../../browser-agents/SCOPE.md), [state.json](./state.json), [backlog](./backlog/)

## Current Focus

- 브랜치 `study/browser-agents` 1차 세션 (2026-09-22~23) — 브라우저형 에이전트 도구 조사를 새로 시작했다. Aside 중심 문서 8편 작성 완료. 기존 Codex 조사(`docs/`)와는 별개 주제이고, **scope 는 A안(브랜치 국한)으로 확정**됐다.

## Work Status

- TASK-2026-09-22-browser-agents-001 브라우저형 에이전트 도구 조사 — Aside 중심: done
- TASK-2026-09-23-browser-agents-002 Aside 코드레벨 분석 — CLI 바이너리 추출: done

## 현재 `in_progress` 작업

-

## 현재 `blocked` 작업

-

## Key Changes

- `browser-agents/` 신설 — README, SCOPE, 문서 8편 (판세 / Aside 심층 / Aside UX / Comet 아키텍처 / 비교군 / 교차분석 / 보안 / 출처).
- `docs.aside.com` 의 `.md` + `/llms.txt` 수법으로 Aside 제품 문서 16종을 **1차 텍스트로** 확보. 기존 조사가 OpenAI 문서에서 쓴 것과 같은 기법 — 두 번째 사례다.
- 루트 `README.md` 에 이 브랜치 조사로 가는 포인터 추가.
- **scope A안 확정** (2026-09-23) — 공용 `PURPOSE.md` 는 건드리지 않고 `browser-agents/SCOPE.md` 가 이 브랜치의 판정 기준이 된다.
- **`08-aside-code-level.md` 추가 (2차 세션)** — Aside Linux CLI 를 설치해 **Node SEA 페이로드를 추출**, 난독화 안 된 ESM 번들 67,774줄을 분석했다. 문서에 없던 사실 다수 확보. 이로써 `99-sources` 의 미확인 항목 2건(**메모리 형식**, **인식·동작 방식**)이 해소됐고, `04`·`06` 의 비교표와 판단이 갱신됐다.
- 설치물: `~/.aside/cli/aside` (144MB), `~/.local/bin/aside` 심볼릭 링크. sudo 없이 설치됐고 제거는 두 경로 삭제로 끝난다.

## Next Actions

- [x] ~~`aside repl`/`mcp` 표면 확인~~ — 완료. 번들에서 규격까지 확보
- [ ] **GUI 확인은 macOS/Windows 기기가 필요하다.** 이 환경(헤드리스 리눅스)에서는 불가능함이 실측으로 확정됐다 — Aside 브라우저는 리눅스 빌드가 없고, CLI 는 로컬 데몬 없이는 `guide` 외 전부 실패한다
- [ ] 대안 경로: 원격 호스트(`aside --host`). macOS/Windows 기기에서 Settings > Developers 의 원격 제어를 켜고 `aside login` 하면 이 리눅스에서 조종 가능하다 — 번들 가이드가 정확히 이 시나리오를 예시로 든다
- [ ] **브라우저 바이너리**를 CLI 와 같은 방식으로 열기 — 권한 강제·Vault 암호화·인식 파이프라인의 실체가 거기 있다
- [ ] Aside 네트워크 트래픽 관찰 → "local-first" 주장 실증
- [ ] 문서 언어 결정 — 이번엔 한국어로 썼다. `docs/` 는 영어이고 PROJECT_PROFILE §6 은 "문서 본문은 영어"라 적혀 있다. 기존 Codex 조사도 한국어로 시작해 나중에 일괄 번역한 이력이 있어 같은 경로를 택했다. main 병합 전 결정 필요.

## Risks & Blockers

- **⚠️ main 병합 시 공용 PURPOSE.md 수정이 필수다.** scope 는 A안으로 확정됐고(2026-09-23), 브랜치에 머무는 동안은 충돌이 없다. 그러나 **병합하는 순간 공용 `PURPOSE.md` 의 제외 영역 문구가 거짓이 된다** — 병합 PR 에 그 수정을 반드시 포함시킨다. 근거: `browser-agents/SCOPE.md` §결정.
- 이 분야는 분기 단위로 뒤집힌다. 조사 기간 중에만 Atlas 종료(2026-08), Comet 무료화(2026-03)가 있었다. `99-sources.md` §4 의 불일치 항목과 §8 유효기간 참조.
- **GUI 는 여전히 미확인**이고 이 환경에서는 원리적으로 불가능하다. 시각 디자인·애니메이션·승인 모달은 추정으로 채우지 않았다.
- **로그인하지 않았다.** `aside login` 은 사용자 계정 자격증명이 필요해 요청 없이 하지 않았다. 따라서 `skills list` 실제 목록·메모리 내용·원격 호스트 동작은 미확인.
- `08` 의 내용은 전부 🔧 **관측된 구현** 등급이다 — 벤더 보증 명세가 아니고 예고 없이 바뀐다. CLI v1.26.916.1741 기준.
- 위키 재색인 훅(`scripts/check_wiki_freshness.py`)은 `docs/` 만 매핑한다. `browser-agents/` 는 concept 페이지가 없어 훅이 아무 말도 하지 않는다 — 이 조사도 위키에 올릴지는 별도 결정.
