<!-- standard-ai-workflow-kit: v1.10.0 -->

# Session Handoff

- Purpose: Compact restore context for the next AI agent session.
- Scope: current focus, task status, key changes, next actions, risks
- Audience: AI agents, maintainers
- Status: active
- Updated: 2026-09-26 (Strands — 세 번째 사례, 루프 밖 게이트는 필요조건일 뿐)
- Related docs: [Project Profile](../../../docs/PROJECT_PROFILE.md), [PURPOSE](../PURPOSE.md), [SYNTHESIS](../../../SYNTHESIS.md), [state.json](./state.json), [backlog](./backlog/)

## Current Focus

- **이 저장소의 조사는 안정 상태다. 남은 작업은 전부 기기나 동적 관찰을 요구하거나, 기존 사실의 드리프트 점검이다.** 조사가 둘(`docs/` Codex · `browser-agents/` 브라우저형), 위키 개념 16종이 둘을 재색인, `SYNTHESIS.md` 가 교차 종합, `REPORT`(영/한)에 외부 증거 반영.
- **조사 ↔ 구현 되먹임 루프가 자리잡았다.** 구현은 `ykylee/heddle` (private), 이 저장소 범위 밖이다(`PURPOSE.md` §0.1: **측정만 편입하고 코드는 밖에 둔다**). 이번 세션에 그 경로로 들어온 것이 `SYNTHESIS.md` §6 이다 — 반박 5건, 확인 6건, 방어 공격 5건 관통, 모델 실측 2공급자.
- **주입 위협 모델 재검토 완료 (TASK-015).** Brave 원문을 다시 읽으니 유출은 "공격자 서버로 navigate"가 아니라 **Reddit 댓글에 답글 달기(쓰기 1회)** 였다. 체인 어디에도 공격자 목적지가 없다. 어긋남은 시연과 실측 사이가 아니라 **우리 한 줄 요약과 원문 사이**에 있었고, 그 요약이 heddle 프로브 설계까지 흘러갔다. 정정하면 시연과 실측은 일치한다 — **목적지 기반 방어는 둘 다 못 막는다. 쓰기를 게이트해야 한다.**
- **세 번째 사례 Strands 편입 (TASK-2026-09-26-main-001).** `strands/` 8편 — AWS Strands Agents SDK 와 2026-09-22 에 나온 **Strands harness**(`create_harness()`)를 `harness-sdk@15da9dc` 소스로 읽었다. 호출자와 루프 사이에 wire 가 없는 **임베드형** 하네스라 Codex·Aside 와 다른 축에서 추상을 시험한다. 결론: **루프 밖 승인 게이트는 필요조건일 뿐** — Strands 는 그 게이트를 가졌지만 기본 off, 오류 경로 fail-open(Cedar·steering, 🧪 대조군 포함), 등록순 합성, hard deny 없음 (`SYNTHESIS.md` §2.7). provider-as-data 는 **공유 wire 전제에서만** 성립한다는 한정도 붙었다 (§2.3)
- **두 저장소의 막힌 지점은 여전히 같다**: 디스플레이 있는 macOS/Windows 기기.

## Work Status

- TASK-2026-09-26-main-001 Strands Agents 하네스 조사 및 심층 분석: done
- TASK-2026-09-23-main-015 주입 위협 모델 강조점 재검토: done
- TASK-2026-09-23-main-014 두 번째 공급자로 주입 결론 검증 및 정정: done
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

> 상한(10) 이전의 완료 항목은 `backlog/tasks/` 에 있다 — 001·005·006 (워크플로우 도입, 위키 계층, 재색인 강제), browser-agents-001~006 (조사 착수, CLI 바이너리 추출, Aside 바이너리·집행 분석, Dia·Neon 심화, 두 조사 융합).

## 현재 `in_progress` 작업

-

## 현재 `blocked` 작업

-

## Key Changes

- **Strands 조사 (TASK-2026-09-26-main-001)** — `strands/` 01~07·99. 반박 20건(`strands/99` §4): 승인 계층 R1–R5 가 가장 무겁다 — 문서는 "Cedar 평가 오류는 항상 fail-closed", "deny > confirm > … 우선순위", `auditLog` 를 약속하지만 코드는 아니다. 벤치마크 "동등 이상 정확도"는 차트 자체 데이터로 19쌍 중 7쌍에서 낮다 — **문구 반박이지 순위 반박이 아니다**(분산 없음). 설계 문서 "Proposed" 13건 중 11건이 이미 구현 → 새 등급 📐 designed-only. `llms.txt` 기법 기록에 변형 추가(`<page>/index.md` 만 200). 위키 개념 7종 재ingest, `PURPOSE.md` 포함 영역에 임베드형 SDK 하네스 명시
- **Brave 시연 요약 정정 (TASK-015)** — "공격자 서버로 전송"은 원문에 없다. 원문 4단계는 perplexity.ai(trailing-dot 변형 포함)·gmail.com 을 읽고 **원래 댓글에 답글로 유출**한다. `browser-agents/99-sources.md` §4.5 반박, 위키 `indirect-prompt-injection`·`primary-source-verification` 재ingest, `SYNTHESIS.md` §7 에 방법론 항목 "요약 위에 테스트를 짓기 전에 원문을 다시 읽어라" 추가. §6.5·§6.7 에 남아 있던 단일 실행 수치(9/20→3/20, 45%)와 "one model" 표현도 함께 정정

- **저장소 범위 확장** — `PURPOSE.md` §0 에 기록. 제외 영역에서 "OpenAI 외 벤더" 삭제, Goals G5 추가. `study/browser-agents` 의 A안 조건 이행.
- **조사가 둘이 됐다** — `browser-agents/` 14편 신설. Aside 는 제품 문서 1차 확보 후 **CLI·브라우저 바이너리까지 정적 분석**했다.
- **위키 개념 13 → 16종** — 기존 8종에 브라우저 근거 추가, 신규 3종(`perception-model`·`indirect-prompt-injection`·`credential-shielding`).
- **`SYNTHESIS.md` 신설** — 핵심 주장은 **표면 무관 축과 표면 고유 축의 구분**이다.
- **모델을 넣어 나머지 절반을 쟀고, 두 번째 공급자로 앞선 결론 2건을 정정했다 (§6.5)** — navigate 유출형은 **두 모델 모두 0/120**, 즉 연구가 중심에 둔 공격 모양은 재현되는 음성 결과다. 그러나 "버튼에는 넘어간다"는 **재현되지 않았다** — MiniMax 약 40%, DeepSeek 0/40. 그건 모델의 성질이 아니라 그 모델의 성질이다. 봉투는 3회 풀링 24/60 → 10/60 이지만 회차별 1~6 로 흔들려 **방향은 실측, 비율은 아니다**(처음 보고한 9/20→3/20 은 단일 실행이었다). 그리고 **두 번째 공급자는 봉투를 확인해주지 못했다** — 아무것도 안 따르는 모델에는 줄일 신호가 없다(바닥 효과)
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

**Strands 조사 (`strands/`)**
- [ ] 위조 `<system-reminder>` 태그를 모델이 하네스 권위로 받아들이는지 — 프롬프트 계약이 그렇게 말하고 아무도 이스케이프하지 않는다(`strands/07` §2.1). **실측은 heddle 측 작업**, 결과만 편입
- [ ] 장기 메모리가 주입 지시를 세션 너머로 나르는지 (⚠️ 소스상 경로만 확인)
- [ ] TS SDK 세부의 직접 확인 (일부는 위임 요약 + 스폿체크) · stateful Responses 모드의 툴 루프 중복 전송 의심
- [ ] `REPORT`(영/한)에 세 번째 사례 반영 여부 결정
- [ ] harness 는 0.x, 출시 3일차 스냅샷이다 — 재조사의 첫 수는 드리프트 확인

**저장소**
- [ ] 위키 신선도 검사기 오탐 4건 — `last_ingested_from` 의 `SYNTHESIS.md §6.4` 같은 주석이 경로로 파싱돼 "원 문서가 사라졌다"로 뜬다(지난 세션부터). 주석을 빼거나 파서가 공백 뒤를 버리게 할 것
- [x] ~~`SYNTHESIS.md` 구현 피드백 절 편입~~ — TASK-011 완료. `PURPOSE.md` §0.1 에 "측정만 편입, 코드는 아님" 경계를 명시했다
- [x] ~~간접 프롬프트 주입 방어 검증~~ — TASK-012. Dia 의 공개 방어를 구현해 공격했다. **16건 중 5건 관통.** 결과는 `SYNTHESIS.md` §6.4
- [x] ~~나머지 절반: 모델이 루프에 있을 때~~ — TASK-013. `SYNTHESIS.md` §6.5
- [x] ~~두 번째 모델~~ — DeepSeek 추가. 취약성 질문은 갈렸고 **방어 질문은 갈리지 않았다**
- [ ] **봉투 검증에는 실제로 취약한 모델이 필요하다.** DeepSeek 은 아무것도 안 따라서 방어 효과를 보여줄 수 없다(바닥 효과). 취약한 세 번째 공급자, 또는 MiniMax 회차를 더 쌓는 것 중 하나 — 아무도 명시하지 않는 요건이고 모델을 붙여본 뒤에야 알게 된다
- [ ] Google 키는 402(크레딧 소진)라 측정 불가. 복구되면 세 번째 점이 생긴다
- [x] ~~§2/§3.2 위협 모델 재검토~~ — TASK-015. 원문 재독으로 요약 오류 발견·정정. `browser-agents/07` §2·§10, `SYNTHESIS.md` §3.2·§7
- [ ] **원문 체인 그대로의 측정은 아직 없다** — 세션 횡단 읽기 여러 번 → 쓰기 1회, 다단계. 지금 실측은 단발·합성 페이지·공격자 origin navigate 였다. 프로브는 heddle 쪽 작업이다(범위 밖) — 측정이 나오면 §6.5 로 편입
- [ ] Dia 의 "되돌릴 수 없는 버튼"에 공개 정의가 없다 — 우리 측정은 *서술의 구현* 을 공격한 것이라 Dia 코드에 대한 평가가 아니다. 1차 출처가 생기면 이 경계를 갱신할 것
- [ ] `SYNTHESIS.md` §6 은 heddle 의 2026-09-23 시점 실측이다. heddle 이 진행되면 여기도 드리프트한다

## Risks & Blockers

- **"0 은 입력이 도달했음을 증명할 수 있을 때만 증거다."** 이번 작업에서 전달 실패가 *좋은 숫자*로 찍힌 사례가 네 번 나왔다 — 프레임 미순회, charset 모지바케, interactive 모드가 페이로드를 버림, 그리고 공급자가 404 를 200번 내는데 **완벽한 방어로 렌더**. 네 번 다 assertion 은 리뷰에서 멀쩡해 보였고, 실제로 도달한 것을 출력해서야 잡혔다. `SYNTHESIS.md` §7 에 방법론 항목으로 올렸다
- **근거 등급이 칸마다 다르다.** Aside 는 바이너리까지, Dia·Neon 은 문서만, Comet 은 3자 리버싱이다. 비교표를 읽을 때 이 비대칭을 잊으면 안 된다 — `SYNTHESIS.md` §8 에 경고로 달아뒀다.
- 두 분야 모두 빠르게 낡는다. Codex 는 2026-09-15, 브라우저는 2026-09-22/23 기준이다. 재조사의 첫 수는 **기존 사실의 드리프트 확인**이다.
- `docs/` 또는 `browser-agents/` 를 고치면 **위키 재색인이 따라와야 한다.** pre-commit 훅이 막지만 `core.hooksPath` 를 설정한 clone 에서만 돈다 — 새 clone 에서는 `git config core.hooksPath .githooks` 가 필요하다.
- `wiki/SCHEMA.md` 는 kit 생성물이라 한국어로 남아 있다. 번역하면 kit 재생성과 갈린다.
