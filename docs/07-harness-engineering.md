# 07. Harness Engineering — OpenAI 내부 실험에서 나온 운영 원칙

> 출처: [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/),
> Ryan Lopopolo, 2026-02-11

## 1. 실험 개요

- **수기로 작성한 코드 0줄**로 내부 베타 제품을 5개월간 개발·출시
- 최초 커밋: 2025년 8월 말, 빈 git 저장소
- 초기 스캐폴드(리포 구조, CI, 포맷 규칙, 패키지 매니저, 앱 프레임워크)도 Codex CLI + GPT-5가 생성.
  **`AGENTS.md` 자체도 Codex가 작성**
- 5개월 후: 약 **100만 줄**, **약 1,500개 PR**, 엔지니어 3명(현재 7명)
- 엔지니어당 하루 평균 **3.5 PR**, 팀이 커져도 처리량이 오히려 증가
- 손으로 짰을 때 대비 약 **1/10 시간**

> "Humans steer. Agents execute."

## 2. 엔지니어 역할의 재정의

초기 진행이 느렸던 이유는 Codex의 능력 부족이 아니라 **환경이 과소 명세(underspecified)** 되어서였습니다.

실패했을 때 답은 절대 "더 열심히 시도"가 아니라:
> **"어떤 능력이 빠져 있고, 그것을 에이전트에게 어떻게 읽히게(legible) 그리고 강제되게(enforceable) 만들 것인가?"**

작업 방식은 **depth-first** — 큰 목표를 작은 빌딩블록(설계, 코드, 리뷰, 테스트)으로 쪼개고,
에이전트에게 그 블록을 만들게 하고, 그걸로 더 복잡한 과업을 잠금 해제.

PR 완주 방식: Codex가 자기 변경을 로컬에서 리뷰 → 로컬/클라우드 에이전트 리뷰를 추가 요청 →
피드백에 응답 → 모든 에이전트 리뷰어가 만족할 때까지 루프 (이른바 Ralph Wiggum Loop).
**리뷰 노력의 거의 전부를 에이전트↔에이전트로 이관.**

## 3. 애플리케이션 가독성(legibility) 높이기

코드 처리량이 늘자 병목이 **사람의 QA 능력**이 되었습니다. 그래서 UI·로그·메트릭 자체를 Codex가 읽을 수 있게 만듦:

- **git worktree마다 앱을 부팅 가능**하게 만들어 변경마다 인스턴스를 하나씩 띄움
- **Chrome DevTools Protocol을 에이전트 런타임에 배선**, DOM 스냅샷·스크린샷·네비게이션용 skill 제작
  → 버그 재현, 수정 검증, UI 동작 추론을 직접 수행
- 로컬 관측 스택을 worktree별 ephemeral로 제공 → 에이전트가 **LogQL로 로그, PromQL로 메트릭** 질의
  → "서비스 시작을 800ms 미만으로", "이 4개 핵심 여정에서 어떤 span도 2초를 넘지 않게" 같은 프롬프트가 성립

> 단일 Codex 실행이 하나의 과업에 **6시간 이상** 매달리는 경우가 흔함 (주로 사람이 자는 동안).

## 4. 리포지터리 지식을 system of record로

> **"give Codex a map, not a 1,000-page instruction manual."**

"하나의 거대한 `AGENTS.md`" 접근은 예측 가능한 방식으로 실패했습니다:

1. **컨텍스트는 희소 자원** — 거대 지시 파일이 과업·코드·관련 문서를 밀어냄
2. **지침이 너무 많으면 지침이 아니게 됨** — 전부가 "중요"하면 아무것도 중요하지 않음.
   에이전트가 의도적으로 항해하지 않고 국소 패턴 매칭으로 빠짐
3. **즉시 썩음** — 모놀리식 매뉴얼은 낡은 규칙의 무덤이 되고, 조용히 "매력적인 위험물"이 됨
4. **검증이 어려움** — 단일 블롭은 기계적 검사(커버리지, 신선도, 오너십, 교차링크)에 맞지 않음

그래서 **`AGENTS.md`를 백과사전이 아니라 목차로** 취급합니다. 약 100줄.

```
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   ├── core-beliefs.md
│   └── ...
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   ├── new-user-onboarding.md
│   └── ...
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   ├── uv-llms.txt
│   └── ...
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

- 설계 문서는 **검증 상태(verification status)**와 함께 카탈로그·인덱싱
- 품질 문서가 도메인/아키텍처 레이어별로 **등급을 매기고 격차를 추적**
- **계획을 1급 아티팩트로** 취급 — 작은 변경은 경량 임시 계획, 복잡한 작업은 진행/결정 로그를 포함한
  실행 계획(exec plan)을 리포에 커밋. active / completed / tech-debt를 모두 버전 관리하며 같은 곳에 배치
- **점진적 공개(progressive disclosure)** — 작고 안정적인 진입점에서 시작해 "다음에 어디를 볼지"를 가르침
- **기계적으로 강제** — 전용 린터와 CI 잡이 지식 베이스의 최신성·교차링크·구조를 검증.
  주기적 "doc-gardening" 에이전트가 실제 코드와 안 맞는 문서를 찾아 수정 PR을 염

> **"From the agent's point of view, anything it can't access in-context while running effectively doesn't exist."**
> Google Docs, 채팅 스레드, 사람 머릿속의 지식은 시스템에 존재하지 않는 것과 같습니다.
> 아키텍처 패턴을 합의한 그 Slack 논의도, 에이전트가 발견할 수 없으면
> 3개월 뒤 합류한 신입에게 알려지지 않은 것과 똑같이 illegible합니다.

## 5. 기술 선택 기준이 바뀐다

- 리포 안에서 **완전히 내재화하고 추론할 수 있는** 의존성과 추상을 선호
- "지루하다"고 불리는 기술이 오히려 에이전트가 모델링하기 쉬움 — 조합성, API 안정성, 학습 데이터 내 존재감
- 때로는 **불투명한 상위 라이브러리 동작을 우회하는 것보다 에이전트가 하위 집합을 재구현하는 게 더 쌈**.
  예: 일반적인 p-limit류 패키지 대신 자체 map-with-concurrency 헬퍼 구현 —
  OpenTelemetry 계측과 긴밀히 통합, 테스트 커버리지 100%, 런타임 기대 동작과 정확히 일치

## 6. 아키텍처와 취향을 기계적으로 강제

> **불변식을 강제하되 구현을 마이크로매니징하지 않는다.**

예: "경계에서 데이터 형태를 파싱하라"는 요구하지만 *어떻게*는 규정하지 않음
(모델이 Zod를 좋아하는 듯하지만 그 라이브러리를 지정하지는 않았음).

레이어 규칙 — 각 비즈니스 도메인 안에서 **앞으로만** 의존 가능:

```
Types → Config → Repo → Service → Runtime → UI
```

횡단 관심사(auth, connectors, telemetry, feature flags)는 **Providers라는 단일 명시적 인터페이스**로만 진입.
그 외는 전부 금지이며 기계적으로 강제(커스텀 린터 + 구조 테스트, 물론 Codex가 작성).

추가로 "취향 불변식(taste invariants)"을 정적 강제 — 구조화 로깅, 스키마/타입 명명 규칙,
파일 크기 제한, 플랫폼별 신뢰성 요구사항.

> **커스텀 린트이기 때문에, 에러 메시지 자체에 교정 지시를 담아 에이전트 컨텍스트에 주입합니다.**

> "This is the kind of architecture you usually postpone until you have hundreds of engineers.
> With coding agents, it's an early prerequisite: the constraints are what allows speed without decay."

인간 우선 워크플로에서는 현학적으로 느껴질 규칙이, 에이전트에서는 **한 번 인코딩하면 전역에 동시에 적용되는 배수기**가 됩니다.

## 7. 처리량이 머지 철학을 바꾼다

- 블로킹 머지 게이트 최소화
- PR은 짧게 산다
- 테스트 flake는 무기한 블로킹 대신 **재실행으로 처리**

> "In a system where agent throughput far exceeds human attention, corrections are cheap, and waiting is expensive."
> 저처리량 환경이었다면 무책임했을 선택이, 여기서는 종종 옳은 트레이드오프입니다.

## 8. 엔트로피와 가비지 컬렉션

전면 자율성은 새로운 문제를 낳습니다. **Codex는 리포에 이미 존재하는 패턴을 복제**하며,
고르지 않거나 차선인 패턴도 그대로 복제합니다 → 필연적 드리프트.

초기에는 사람이 매주 금요일(주의 20%)을 "AI slop" 정리에 썼고, 당연히 확장되지 않았습니다.

대신 **"golden principles"**를 리포에 직접 인코딩하고 반복 정리 프로세스를 구축:
- 공유 유틸리티 패키지를 손수 만든 헬퍼보다 선호 (불변식을 중앙화)
- 데이터를 "YOLO 방식"으로 탐침하지 않음 — 경계를 검증하거나 타입드 SDK에 의존
  (추측한 형태 위에 쌓지 못하게)

정기적으로 백그라운드 Codex 태스크가 이탈을 스캔하고, 품질 등급을 갱신하고, 표적 리팩터링 PR을 엽니다.
대부분 1분 내 리뷰 가능하고 자동 머지됩니다.

> 기술 부채는 고금리 대출과 같습니다 — 복리로 불어나게 두었다가 고통스럽게 몰아서 갚는 것보다
> 작은 증분으로 지속적으로 상환하는 쪽이 거의 항상 낫습니다.

## 9. 도달한 자율성 수준

단일 프롬프트로 에이전트가 end-to-end 수행 가능해진 항목:

1. 코드베이스 현재 상태 검증
2. 보고된 버그 재현
3. **실패를 보여주는 비디오 녹화**
4. 수정 구현
5. 애플리케이션을 직접 구동해 수정 검증
6. **해결을 보여주는 두 번째 비디오 녹화**
7. PR 오픈
8. 에이전트/사람 피드백에 응답
9. 빌드 실패 탐지 및 교정
10. 판단이 필요할 때만 사람에게 에스컬레이션
11. 머지

> 단, 이 동작은 **해당 리포의 구조와 도구에 크게 의존**하며, 유사한 투자 없이 일반화된다고 가정해서는 안 된다고
> 저자가 명시합니다.

## 10. "agent-generated"의 범위

에이전트가 생산하는 것 전부:
제품 코드와 테스트 / CI 설정과 릴리스 도구 / 내부 개발자 도구 / 문서와 설계 이력 /
평가 하네스 / 리뷰 코멘트와 응답 / 리포지터리를 관리하는 스크립트 / 프로덕션 대시보드 정의 파일.

사람은 항상 루프 안에 있지만 **다른 추상 레이어에서** 일합니다 —
작업 우선순위 결정, 사용자 피드백을 수용 기준으로 번역, 결과 검증.
에이전트가 막히면 그것을 **신호**로 보고 무엇이 빠졌는지(도구·가드레일·문서) 식별해 리포에 피드백하되,
**그 수정조차 항상 Codex가 작성**합니다.

## 11. 아직 모르는 것

- 완전 에이전트 생성 시스템에서 **아키텍처 일관성이 수년에 걸쳐 어떻게 진화**하는지
- 사람의 판단이 어디에서 가장 큰 레버리지를 주는지, 그 판단을 어떻게 인코딩해야 복리로 쌓이는지
- 모델이 계속 강해질 때 이 시스템이 어떻게 변할지

> "building software still demands discipline, but the discipline shows up more in the **scaffolding** rather than the code."

## 12. 이 문서를 우리 프로젝트에 적용한다면

| 원칙 | 실행 항목 |
|---|---|
| 지도이지 매뉴얼이 아니다 | `AGENTS.md`/`CLAUDE.md`를 100줄 내외 목차로. 깊은 내용은 `docs/`로 |
| 기계적 강제 | 문서 신선도·교차링크를 CI 린트로. 린트 에러 메시지에 **교정 지시**를 담기 |
| 계획을 1급 아티팩트로 | active/completed/tech-debt를 리포에 커밋 |
| 앱을 에이전트에게 읽히게 | worktree별 부팅, 로그/메트릭 질의 경로, 브라우저 제어 skill |
| 불변식 > 구현 규정 | 레이어 의존 방향만 강제, 라이브러리 선택은 자유 |
| 지속적 GC | 주기 백그라운드 태스크가 드리프트를 스캔하고 표적 PR을 염 |
| 컨텍스트를 리포로 | 채팅/문서 도구에 있는 합의를 리포 안 버전 관리 아티팩트로 이관 |
