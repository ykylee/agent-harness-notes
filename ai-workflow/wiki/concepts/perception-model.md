---
type: concept
status: active
last_ingested_from: browser-agents/06-architecture-axes.md + browser-agents/08-aside-code-level.md + browser-agents/04-comet-architecture.md + browser-agents/05-comparables.md
related_pages: [concepts/harness, concepts/indirect-prompt-injection, concepts/control-plane-execution-plane]
created: 2026-09-23
updated: 2026-09-23
---

# Perception Model — 에이전트가 화면을 보는 방식

- 문서 목적: 에이전트가 웹 페이지(또는 화면)를 어떤 표현으로 읽는지, 그 선택이 어떤 실패 모드를 낳는지 정리한다.
- 범위: 네 가지 방식, 인식·동작 이름 공간의 대칭, 비용 사다리
- 성격: **실행 표면 고유의 축.** 셸 기반 하네스(Codex)에는 이 문제가 없다
- 최종 수정일: 2026-09-23

## §1 TL;DR  {#s1-tldr}

| # | 항목 | 값 |
|---|---|---|
| 1 | 왜 어려운가 | 원본 DOM 은 2MB+ — **토큰 예산이 먼저 무너진다** |
| 2 | 실제로 쓰이는 방식 | 원본 DOM · 접근성 트리 · 스크린샷 · DOM 증류+SoM |
| 3 | **가장 중요한 갈림** | 인식과 동작이 **같은 이름 공간**인가 |
| 4 | 대칭이면 | "본 것과 다른 곳을 눌렀다"가 **구조적으로 불가능** |
| 5 | 조사 범위에서 비대칭 | **Comet 하나뿐** |

## §2 네 가지 방식과 각자의 실패 모드  {#s2-four-ways}

| 방식 | 채택 | 장점 | 실패 모드 |
|---|---|---|---|
| **원본 DOM** | (거의 안 씀) | 정보 손실 없음 | **2MB+** — 토큰 예산 붕괴 |
| **접근성 트리** | Comet (`Accessibility.getFullAXTree` → YAML), Aside (주입 스크립트 기반) | 의미론이 이미 정리됨, 토큰 효율 | 접근성 구현이 나쁜 사이트에서 무너짐 |
| **스크린샷** | Atlas (computer-use 모델) | 렌더된 실제 모습 | **팝업·드롭다운이 별도 서피스**로 렌더돼 합성 필요, 좌표 정밀도 |
| **DOM 증류 + SoM** | Browser Use | 2MB → **1,500~3,000 토큰** | 증류가 버린 것은 영영 안 보임 |

### §2.1 스크린샷 방식의 함정 — Atlas 가 남긴 기록  {#s2-1-screenshot-trap}

> computer-use 모델은 **스크린샷 한 장**을 입력으로 받는데, 드롭다운 같은 UI 는 메인 탭 경계
> **바깥의 별도 윈도우**로 렌더된다. Atlas 는 이 팝업들을 **올바른 좌표로 메인 이미지에 합성**해
> 넣어야 했다.

> 📌 "화면을 찍어 모델에 준다"는 개념적으로 단순하지만 **브라우저의 실제 렌더링은 한 장의
> 이미지가 아니다.** 이 방식을 고르면 합성 문제를 직접 풀어야 한다. 트리 기반에는 이 문제가 없다.

## §3 핵심 축 — 인식과 동작의 이름 공간  {#s3-naming}

| 제품 | 인식 | 동작 | 대칭? |
|---|---|---|---|
| **Aside** | 접근성 트리 + **가상 ref ID** (`e31`, `f1e1`) | `page.locator('e31')` | ✅ |
| **Browser Use** | SoM 번호 배지 (`[14]`) | `click_element(index=14)` | ✅ |
| **Comet** | 접근성 트리 (의미) | **`ComputerBatch` 픽셀 좌표** (기하) | ❌ |

> 📌 **대칭이 구조적으로 견고하다.** 본 것과 가리키는 것이 같은 이름 공간이면 "본 것과 다른
> 곳을 눌렀다"라는 실패 모드가 **존재할 수 없다.** Browser Use 는 이 방식으로 동작 정밀도
> 95%+ 를 보고한다.
>
> 커스텀 하네스를 만든다면 여기서 시작하는 것이 안전하다.

### §3.1 Aside 의 ref 규약 (코드 확인)  {#s3-1-aside-refs}

```ts
snapshot(page, { interactive?, showHidden?, ref?, selector? })
  : Promise<{ tree: string; diff: string }>
```

| 규칙 | 내용 |
|---|---|
| 표현 | "compact accessibility tree with unique ref IDs such as `e12` or `f1e1`" |
| 범위 | 제목·URL·**자식 iframe·스크롤 뷰포트 밖 요소**까지 |
| ref 의 성질 | "**virtual locator IDs, not actual DOM properties**" — CSS 선택자에 섞지 말 것 |
| 무효화 | 새 snapshot 은 **이전 ref 를 전부 무효화**한다 |
| **diff** | 최초엔 `tree`, **동작 후에는 `diff` 만** 출력 |

> 📌 **`diff` 가 토큰 효율의 핵심이다.** 매 동작 후 전체 트리를 다시 읽으면 스텝마다 수천 토큰을
> 태운다. 변화분만 주면 대화가 길어져도 비용이 선형으로 늘지 않는다.
> 조사 범위에서 diff 를 1급으로 제공하는 것은 Aside 뿐이다.

## §4 비용 사다리 — 싼 것부터  {#s4-escalation}

Aside 가 코드로 명시하는 **읽기 에스컬레이션**:

| 순서 | 수단 |
|---|---|
| 1 | `snapshot(page, { interactive: true })` — 상호작용 요소만 |
| 2 | `snapshot(page)` — 전체 |
| 3 | 잠깐 대기 후 재촬영 (페이지가 아직 변하는 중일 때만) |
| 4 | **`annotatedScreenshot(page)`** — **ref ID 가 박힌 바운딩 박스** |
| 5 | `page.screenshot()` — 원시 시각 상태 |

> 📌 4단계가 좋은 설계다. 시각 확인으로 내려가도 **이름 공간이 유지된다.** Browser Use 의 SoM 과
> 같은 아이디어인데, Aside 는 그것을 **기본 경로가 아니라 폴백**으로 뒀다.

## §5 복구 전략  {#s5-recovery}

인식이 틀렸을 때 빠져나오는 법. Browser Use 가 공개한 것:

> 같은 요소를 **3회 연속 클릭**해도 DOM 토폴로지가 바뀌지 않으면 워치독이 페이지를 강제
> 새로고침하고, **모달 감지나 스크롤 필요 같은 대안 전략으로 유도하는 맥락 피드백**을 주입한다.

> 📌 **정체 감지는 인식 설계의 일부다.** 에이전트는 자기가 아무것도 바꾸지 못하고 있다는 것을
> 스스로 알 수 없다 — 외부 워치독이 알려줘야 한다.

## §6 OS 로 확장될 때  {#s6-os}

Aside 의 `Computer Use` 는 같은 철학을 데스크톱으로 옮긴다 — **`AXTreeSerializer`** 로 화면
전체의 접근성 트리를 직렬화한다. 스크린샷 좌표가 아니라 구조를 먼저 읽는 것이 일관된다.
자세한 것은 [[concepts/os-sandbox-policy]] §8.6.

## §7 다음에 읽을 문서  {#s7-next}

- [[concepts/indirect-prompt-injection]] — 인식에 무엇을 넣느냐가 곧 공격면이다
- [[concepts/credential-shielding]] — 인식에서 **빼는** 쪽의 설계
- [[concepts/harness]] §7.6 — 표면 고유 축과 무관 축의 구분
- 원문: [`browser-agents/06-architecture-axes.md`](../../../browser-agents/06-architecture-axes.md) §2
