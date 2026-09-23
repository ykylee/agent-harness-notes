<!-- standard-ai-workflow-kit: v1.10.0 -->

# Session Handoff

- Purpose: Compact restore context for the next AI agent session.
- Scope: current focus, task status, key changes, next actions, risks
- Audience: AI agents, maintainers
- Status: active
- Updated: 2026-09-23 (주입 — 모델 넣은 절반까지 측정)
- Related docs: [Project Profile](../../../docs/PROJECT_PROFILE.md), [PURPOSE](../PURPOSE.md), [SYNTHESIS](../../../SYNTHESIS.md), [state.json](./state.json), [backlog](./backlog/)

## Current Focus

- **이 저장소의 조사는 안정 상태다. 남은 작업은 전부 기기나 동적 관찰을 요구하거나, 기존 사실의 드리프트 점검이다.** 조사가 둘(`docs/` Codex · `browser-agents/` 브라우저형), 위키 개념 16종이 둘을 재색인, `SYNTHESIS.md` 가 교차 종합, `REPORT`(영/한)에 외부 증거 반영.
- **조사 결론이 별도 저장소에서 구현되기 시작했다 — `ykylee/heddle` (private).** 이 저장소의 범위 밖이므로(`PURPOSE.md` 제외 영역: "하네스의 실제 구현·포크·재배포") 여기서 추적하지 않는다. 링크만 남긴다. 다만 **두 저장소의 막힌 지점이 같다**: 둘 다 디스플레이 있는 macOS/Windows 기기를 기다린다.

## Work Status

- TASK-2026-09-23-main-013 주입 — 모델을 넣은 나머지 절반 측정: done
- TASK-2026-09-23-main-012 주입 방어 실측을 노트 저장소로 편입: done
- TASK-2026-09-23-main-011 SYNTHESIS 구현 피드백 절 편입: done
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
- **모델을 넣어 나머지 절반을 쟀다 (§6.5)** — 공격 4종×조건 2종×N=20. **연구가 중심에 둔 공격 모양(navigate 유출)이 모델이 가장 잘 거부하는 모양이었다 — 0/80.** 뚫린 건 페이지가 "먼저 눌러야 한다"고 설명한 **눈앞의 버튼**, 9/20. 봉투 감싸기는 9/20 → 3/20 으로 줄였다 — 조사에서 누구도 검증하지 않았던 가설의 첫 숫자이고, **돕지만 해결하지 않는다**. 그리고 모델이 넘어간 행동 부류(click)가 게이트에 정보를 가장 적게 싣는 쪽이다
- **주입 방어를 처음으로 공격했다 (§6.4)** — 조사가 "이 분야의 중심 위험인데 누구도 자기 방어를 검증하지 않았다"고 기록한 바로 그 지점. Dia 의 공개 방어를 구현해 공격했더니 **16건 중 5건 관통**. 차폐가 입력 *타입* 만 봤고, 필드를 다 막아도 비밀이 **URL** 로 샜고, 보이지 않는 문자가 단어 경계를 이겼다. **인지 계층 방어는 전부 공격자가 연구할 수 있는 휴리스틱이고, 게이트만 모델의 통제 루프 바깥에 있다.**
- **`SYNTHESIS.md` §6 구현 피드백 편입** — 이 저장소에서 가장 강한 근거 등급이 생겼다: 다른 모든 주장은 남의 산출물을 **읽은** 것이고 §6 은 **실행한** 것이다. 반박 5건·확인 6건. 개념 페이지 3종(`perception-model`·`approval-gate`·`primary-source-verification`)과 `PURPOSE.md` §0.1 경계를 함께 갱신했다. **구현 코드는 여전히 이 저장소 밖이다 — 들어온 것은 측정뿐이다.**
- **내용 문서 전체 영어**. 규칙과 예외는 `docs/PROJECT_PROFILE.md` §6.
- **`REPORT`(영/한)에 외부 증거 절 추가** — 권고 여럿이 서드파티 시스템에서 독립 구현된 것으로 확인됐다.
- 브랜치 병합(`--no-ff`)·삭제, 고아 메모리를 `memory/archived/` 로 아카이브.
- **하류 구현 착수 (이 저장소 외부, 기록만)** — `SYNTHESIS.md` 의 표면 무관 축(대칭 네임스페이스·정책 우선순위·승인·비밀 핸들)을 `ykylee/heddle` 에서 코드로 옮겼다. 설계 주장 5건이 실측에 반박당했다. 드러난 버그 중 **세 건은 같은 결함의 반복**이었다 — 요소 식별자가 구별 축(스냅샷 세대 · 프레임 · 프로세스 생애)을 담지 못해 옛 참조가 조용히 다른 요소로 해석됐다. **이 결과는 `SYNTHESIS.md` §6 으로 편입됐다.**

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
- [x] ~~`SYNTHESIS.md` 구현 피드백 절 편입~~ — TASK-011 완료. `PURPOSE.md` §0.1 에 "측정만 편입, 코드는 아님" 경계를 명시했다
- [x] ~~간접 프롬프트 주입 방어 검증~~ — TASK-012. Dia 의 공개 방어를 구현해 공격했다. **16건 중 5건 관통.** 결과는 `SYNTHESIS.md` §6.4
- [x] ~~나머지 절반: 모델이 루프에 있을 때~~ — TASK-013. `SYNTHESIS.md` §6.5
- [ ] **두 번째 모델이 필요하다.** §6.5 의 거부가 봉투 덕인지 그 공급자의 안전 훈련 덕인지 한 모델로는 못 가른다. 다른 공급자 하나면 갈린다 — 지금 열려 있는 것 중 가장 싸고 가장 결정적인 후속
- [ ] **§2/§3.2 의 위협 모델 자체를 다시 볼 것.** 이 저장소의 주입 서술은 Brave/Comet 시연, 즉 **navigate 유출**을 중심으로 쓰여 있는데 그 모양은 모델이 80/80 거부했다. 뚫린 건 눈앞의 버튼이다. 조사 문서의 강조점이 실제 위험과 어긋나 있을 수 있다
- [ ] Dia 의 "되돌릴 수 없는 버튼"에 공개 정의가 없다 — 우리 측정은 *서술의 구현* 을 공격한 것이라 Dia 코드에 대한 평가가 아니다. 1차 출처가 생기면 이 경계를 갱신할 것
- [ ] `SYNTHESIS.md` §6 은 heddle 의 2026-09-23 시점 실측이다. heddle 이 진행되면 여기도 드리프트한다

## Risks & Blockers

- **근거 등급이 칸마다 다르다.** Aside 는 바이너리까지, Dia·Neon 은 문서만, Comet 은 3자 리버싱이다. 비교표를 읽을 때 이 비대칭을 잊으면 안 된다 — `SYNTHESIS.md` §8 에 경고로 달아뒀다.
- 두 분야 모두 빠르게 낡는다. Codex 는 2026-09-15, 브라우저는 2026-09-22/23 기준이다. 재조사의 첫 수는 **기존 사실의 드리프트 확인**이다.
- `docs/` 또는 `browser-agents/` 를 고치면 **위키 재색인이 따라와야 한다.** pre-commit 훅이 막지만 `core.hooksPath` 를 설정한 clone 에서만 돈다 — 새 clone 에서는 `git config core.hooksPath .githooks` 가 필요하다.
- `wiki/SCHEMA.md` 는 kit 생성물이라 한국어로 남아 있다. 번역하면 kit 재생성과 갈린다.
