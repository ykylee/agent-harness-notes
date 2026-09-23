<!-- standard-ai-workflow-kit: v1.10.0 -->

# Session Handoff

- Purpose: Compact restore context for the next AI agent session.
- Scope: current focus, task status, key changes, next actions, risks
- Audience: AI agents, maintainers
- Status: active
- Updated: 2026-09-23 (4차 세션 — 영어 통일)
- Related docs: [SCOPE](../../../../browser-agents/SCOPE.md), [state.json](./state.json), [backlog](./backlog/)

## Current Focus

- 브랜치 `study/browser-agents` (2026-09-22~23) — 브라우저형 에이전트 도구 조사를 새로 시작했다. Aside 중심 문서 8편 작성 완료. 기존 Codex 조사(`docs/`)와는 별개 주제이고, **scope 는 A안으로 시작했다가 융합 결정으로 공용 PURPOSE 확장으로 해소**됐다.

## Work Status

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

- `browser-agents/` 신설 — README, SCOPE, 문서 8편 (판세 / Aside 심층 / Aside UX / Comet 아키텍처 / 비교군 / 교차분석 / 보안 / 출처).
- `docs.aside.com` 의 `.md` + `/llms.txt` 수법으로 Aside 제품 문서 16종을 **1차 텍스트로** 확보. 기존 조사가 OpenAI 문서에서 쓴 것과 같은 기법 — 두 번째 사례다.
- 루트 `README.md` 에 이 브랜치 조사로 가는 포인터 추가.
- **scope A안 확정** (2026-09-23) — 공용 `PURPOSE.md` 는 건드리지 않고 `browser-agents/SCOPE.md` 가 이 브랜치의 판정 기준이 된다.
- **`08-aside-code-level.md` 추가 (2차 세션)** — Aside Linux CLI 를 설치해 **Node SEA 페이로드를 추출**, 난독화 안 된 ESM 번들 67,774줄을 분석했다. 문서에 없던 사실 다수 확보. 이로써 `99-sources` 의 미확인 항목 2건(**메모리 형식**, **인식·동작 방식**)이 해소됐고, `04`·`06` 의 비교표와 판단이 갱신됐다.
- 설치물: `~/.aside/cli/aside` (144MB), `~/.local/bin/aside` 심볼릭 링크. sudo 없이 설치됐고 제거는 두 경로 삭제로 끝난다.
- **`09-aside-browser-internals.md` 추가** — macOS DMG(334MB)를 내려받아 **실행하지 않고 정적 분석**. Chromium 포크 확인, 내부 MV3 확장 3종, 353MB 로컬 데몬(Node SEA, 258,965줄), Vault 의 libsodium 호출부 확인.
- **자기 서술 1건을 반증했다** — 04 에서 "Comet 은 Aside 와 정반대 구조"라고 적었으나 Aside 의 에이전트도 MV3 확장이었다. 원문은 지우지 않고 정정 표시를 달았고 `99-sources` §4.5 에 반증 기록을 신설했다.
- 다운로드 산출물은 scratchpad 에만 있고 저장소에 커밋되지 않았다. 재현 절차가 `08 §1`·`09 §1` 에 있어 언제든 복원된다.
- **`10-aside-enforcement-and-native.md` 추가** — 09 에서 남긴 미확인 3건을 전부 해소했다. 권한 정책 엔진(도구 glob + 인자 eq/regex, 4버킷, 문서에 없는 `approved`), 승인 UI(=suspension, **채팅 채널 렌더 전제**), `Aside Computer Use`(네이티브, 시스템 전역 AX 트리·이벤트 탭·화면캡처·Vision·연락처), 그리고 Secure Enclave·**ML-KEM-768**·감사 로깅 확인.
- 검증 장부: 해소 18건 / 미확인 8건.
- **문서 언어를 영어로 통일했다 (4차)** — `browser-agents/` 14편, 위키 개념 16종 + index·log, `SYNTHESIS.md`, `docs/PROJECT_PROFILE.md`, `PURPOSE.md`. 번역에서 사실은 바뀌지 않았고 언어만 바뀌었다.
- **한국어 유지 대상**: 커밋 메시지, `session_handoff.md`, backlog task. kit 생성물인 `wiki/SCHEMA.md` 도 제외했다 — 번역하면 kit 재생성과 갈린다. `README.md` 의 한국어는 `REPORT.ko.md` 링크 라벨이고, 한국어판 보고서는 PURPOSE G4 가 유지하기로 한 산출물이다.
- 규칙을 `docs/PROJECT_PROFILE.md` §6 에 명문화했다.
- **두 조사를 융합했다 (3차)** — 위키 개념 8종에 브라우저 근거 추가, 신규 3종(`perception-model`·`indirect-prompt-injection`·`credential-shielding`) 작성, 루트에 **`SYNTHESIS.md`** 신설. 개념 13 → **16종**.
- **공용 `PURPOSE.md` 를 확장했다** — §0 에 범위 확장 기록, 제외 영역에서 "OpenAI 외 벤더" 삭제, Goals 에 G5(표면 무관/고유 축 구분) 추가. `SCOPE.md` 의 A안 조건이 발동한 결과이고, 이로써 **main 병합의 전제 조건이 해소**됐다.
- 설계상 확인: 개념 페이지의 `last_ingested_from` 에 `browser-agents/*` 를 더하니 **재색인 강제 훅이 자동으로 두 트리를 덮는다.** 새 장치가 필요 없었다.
- **`11-dia-and-neon.md` 추가** — `llms.txt`/`.md` 수법을 Dia·Neon 에 적용. Opera 는 `www.opera.com/llms.txt` 가 실재해 성공, **Dia 는 실패**(모든 경로가 동일 SPA 셸). 수법이 만능이 아니라 렌더링 방식에 달렸음을 기록했다.
- **반증 3건 추가** — ① "입력 분리를 문서화한 제품 없음"은 틀렸다(Dia 가 구체적으로 함) ② Neon 의 재사용 단위는 Skills 가 아니라 **Cards** ③ Opera `llms.txt` 의 "모든 AI 처리 로컬"은 제품 FAQ("계획은 클라우드 LLM")와 모순 — 벤더 자신의 두 1차 출처가 어긋난 사례.

## Next Actions

- [x] ~~`aside repl`/`mcp` 표면 확인~~ — 완료. 번들에서 규격까지 확보
- [ ] **GUI 확인은 macOS/Windows 기기가 필요하다.** 이 환경(헤드리스 리눅스)에서는 불가능함이 실측으로 확정됐다 — Aside 브라우저는 리눅스 빌드가 없고, CLI 는 로컬 데몬 없이는 `guide` 외 전부 실패한다
- [ ] 대안 경로: 원격 호스트(`aside --host`). macOS/Windows 기기에서 Settings > Developers 의 원격 제어를 켜고 `aside login` 하면 이 리눅스에서 조종 가능하다 — 번들 가이드가 정확히 이 시나리오를 예시로 든다
- [x] ~~브라우저 바이너리 열기~~ → `09` 완료. Vault 암호와 데몬 구조 확보
- [x] ~~권한 강제 집행 지점~~ / ~~`Aside Computer Use`~~ / ~~Secure Enclave·포스트양자~~ → `10` 에서 전부 해소
- [ ] `Aside Computer Use` **호출 흐름** 추적 — 심볼만 봤지 실제 동작 경로는 미확인
- [ ] 동적 관찰 (서버로 가는 내용) — 정적 분석의 한계. **기기가 필요하다**
- [x] ~~Dia·Neon 1차 심화~~ → `11` 완료
- [ ] **main 병합 검토** — PURPOSE 전제와 언어 통일이 모두 해소됐다. 남은 장애물 없음
- [ ] **검증 비대칭 해소** — Aside 만 바이너리까지 뜯었고 Dia·Neon 은 문서를 믿은 상태다. 문서가 좋은 것과 구현이 그런 것은 다르다
- [ ] Aside 네트워크 트래픽 관찰 → "local-first" 주장 실증
- [x] ~~문서 언어 결정~~ → 전부 영어로 통일 완료 (2026-09-23) `docs/` 는 영어이고 PROJECT_PROFILE §6 은 "문서 본문은 영어"라 적혀 있다. 기존 Codex 조사도 한국어로 시작해 나중에 일괄 번역한 이력이 있어 같은 경로를 택했다. main 병합 전 결정 필요.

## Risks & Blockers

- **⚠️ main 병합 시 공용 PURPOSE.md 수정이 필수다.** scope 는 A안으로 확정됐고(2026-09-23), 브랜치에 머무는 동안은 충돌이 없다. 그러나 **병합하는 순간 공용 `PURPOSE.md` 의 제외 영역 문구가 거짓이 된다** — 병합 PR 에 그 수정을 반드시 포함시킨다. 근거: `browser-agents/SCOPE.md` §결정.
- 이 분야는 분기 단위로 뒤집힌다. 조사 기간 중에만 Atlas 종료(2026-08), Comet 무료화(2026-03)가 있었다. `99-sources.md` §4 의 불일치 항목과 §8 유효기간 참조.
- **GUI 는 여전히 미확인**이고 이 환경에서는 원리적으로 불가능하다. 시각 디자인·애니메이션·승인 모달은 추정으로 채우지 않았다.
- **로그인하지 않았다.** `aside login` 은 사용자 계정 자격증명이 필요해 요청 없이 하지 않았다. 따라서 `skills list` 실제 목록·메모리 내용·원격 호스트 동작은 미확인.
- `08`·`09`·`10` 의 내용은 전부 🔧 **관측된 구현** 등급이다 — 벤더 보증 명세가 아니고 예고 없이 바뀐다. CLI v1.26.916.1741 기준.
- 위키 재색인 훅(`scripts/check_wiki_freshness.py`)은 `docs/` 만 매핑한다. `browser-agents/` 는 concept 페이지가 없어 훅이 아무 말도 하지 않는다 — 이 조사도 위키에 올릴지는 별도 결정.
