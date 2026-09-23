# 11. Dia · Opera Neon — 1차 출처 심화

> [05](05-comparables.md) 은 2차 요약 수준에서 멈춰 있었다. `llms.txt`/`.md` 수법을 다시 걸어
> 1차 자료를 찾은 결과다. 조사일 2026-09-23.
>
> 등급: 이 문서는 **제품 자신의 문서**(✅ 1차)에 근거한다. 바이너리 분석은 하지 않았다.

## 1. 수법의 결과 — 3전 1승 1무 1패

| 대상 | `llms.txt` | `.md` 접미사 | 결과 |
|---|---|---|---|
| **Aside** | ✅ `docs.aside.com/llms.txt` | ✅ 동작 | 문서 16종 전부 1차 확보 ([02](02-aside.md)) |
| **Opera** | ✅ **`www.opera.com/llms.txt`** (11,613b, text/plain) | — | Neon 항목 확보 (§3) |
| **Dia** | ❌ soft 404 | ❌ **통하지 않음** | 모든 경로가 동일한 31,692b SPA 셸을 반환 |

> 📌 **Dia 의 실패 방식이 정보다.** `help.diabrowser.com` 은 `/start`, `/security`,
> `/release-notes/latest` 를 포함해 **어떤 경로든 같은 바이트 수의 Next.js 셸**을 돌려준다.
> `.md` 를 붙여도 같다. 내용이 전부 클라이언트 렌더라 정적 수법이 닿지 않는다.
> 대신 `www.diabrowser.com/security` 에 실제 문서가 있었다 (§2).
>
> ⚠️ 즉 이 수법은 **문서 사이트의 렌더링 방식에 달려 있다.** 되면 크게 얻고, 안 되면
> 렌더된 페이지로 돌아가야 한다. 만능이 아니다.

## 2. Dia — 프롬프트 주입 방어를 문서화한 유일한 제품

`www.diabrowser.com/security` 에서 확보했다. **이 조사 범위에서 간접 프롬프트 주입 방어를
구체적으로 문서화한 제품은 Dia 뿐이다.**

### 2.1 명시된 방어

| 방어 | 원문 |
|---|---|
| **LLM 생성 URL 추종 금지** | "Dia won't automatically open or follow LLM-generated URLs" |
| **URL 원문 전달 금지** | "Dia won't pass URLs to the LLM verbatim" |
| **민감 요소를 인식에서 제거** | 비밀번호 필드와 되돌릴 수 없는 동작 버튼은 "**invisible to the agentic system**" |
| 초기 권한 최소 | 채팅 세션은 "starts with **no access to other tabs** or ability to take write actions" |
| 자율 이동 금지 | 에이전트 모드는 스스로 "navigate on its own to another website" 할 수 없다 |
| 제3자 사이트 쓰기 승인 | "Dia won't insert data into third-party sites without your approval" |

**승인이 필요한 동작**: 양식 작성, 이메일 초안, 캘린더 생성 — "the assistant can use anything
with real-world effects" 전에.

### 2.2 한계를 스스로 인정한다

> 여전히 "Cause unexpected style or tone shifts" 하거나 "Nudge content toward misinformation"
> 할 수 있다.

> 📌 **이것이 이 문서에서 가장 신뢰가 가는 부분이다.** 방어를 나열하면서 무엇이 남는지도
> 적었다. [07 §6](07-security.md) 의 "프롬프트 주입은 완전히 해결되지 않는다"와 정합한다.

### 2.3 `07 §8` 의 판정을 수정한다

[07 §8](07-security.md) 에 이렇게 적었다:

> "Brave 의 완화책 4범주에 비추면, **입력 분리(#1)를 명시적으로 구현했다고 문서화한 제품이
> 조사 범위에서 확인되지 않았다.**"

**부분적으로 틀렸다.** Dia 의 "URL 을 LLM 에 원문으로 넘기지 않는다"와 "비밀번호·비가역 버튼을
에이전트 시스템에서 보이지 않게 한다"는 **입력 계층의 정제**다. Brave 의 #1(입력 분리)과 완전히
같지는 않지만 — 사용자 지시와 페이지 내용을 구조적으로 가르는 것은 아니다 — **인식에 들어가는
것을 통제한다**는 점에서 같은 층위의 방어다.

> 📌 Aside 가 **자격증명의 값을 금고에 숨기는** 방식([02 §4](02-aside.md))과, Dia 가 **비밀번호
> 필드 자체를 에이전트의 인식에서 지우는** 방식은 같은 문제의 다른 해법이다. Aside 는 값을,
> Dia 는 **요소를** 숨긴다. Dia 쪽은 "비가역 동작 버튼"까지 확장돼 있어 자격증명을 넘어선다.

### 2.4 그러나 — 로컬 우선이 아니다

[05 §2](05-comparables.md) 에서 2차 출처를 따라 "로컬 암호화 강조"라고 적었다. 저장은 맞지만
**AI 처리는 서버 경유**다.

| 축 | 내용 |
|---|---|
| 로컬 저장 | "conversations, history, bookmarks, and files are **encrypted and stored locally**" (알고리즘 미공개) |
| 동기화 | "**end-to-end encrypted**, and our servers cannot read the data" (방식 미공개) |
| **AI 요청** | "The data needed to fulfill your request... is **sent through our servers** to trusted AI partners" |
| 메모리 | 요약은 "created on **our servers** and stored locally" |
| **기본 데이터 수집** | "**By default**, we use some content data to improve Dia" — 계정 비연결, **30일 보존 후 삭제** |
| 모델 | GPT (OpenAI Azure), Claude (Anthropic·Vertex·AWS), Gemini (Vertex) |
| 학습 금지 | 제공자는 데이터를 "retain or using your data to train their own models" 할 수 없다 |

> ⚠️ **"기본값이 수집"** 이라는 점은 짚어야 한다. Aside 의 분석 공유 기본 on
> ([02 §5 인접](02-aside.md))과 같은 패턴이다.

## 3. Opera Neon — 두 1차 출처가 모순된다

### 3.1 모순

| 출처 | 주장 |
|---|---|
| **`www.opera.com/llms.txt`** | "**All AI processes run locally on the device**, keeping interactions private and fast." |
| **`operaneon.com/faq`** | "Neon Do runs locally within your browser and directly interacts with webpages. **However, it uses cloud-based large language models (LLMs) to generate the plans and instructions it follows.**" |

**FAQ 가 이긴다.** 더 구체적이고, 제품 자신의 FAQ 이며, 모델 목록(§3.2)이 뒷받침한다.

> ❌ **판정: `llms.txt` 의 "모든 AI 처리가 로컬"은 틀렸다** — 또는 최소한 위험하게 부정확하다.
> 로컬인 것은 **실행**이고, **계획은 클라우드**다.
>
> 📌 그리고 이 구분이 정확히 [06 §3](06-architecture-axes.md) 의 **계획 위치** 축이다.
> Neon 은 Comet 과 같은 편이다 — 실행은 로컬 브라우저, 계획은 서버 모델.
> 벤더의 "로컬" 마케팅이 **어느 면을 말하는지 확인해야 하는 이유**다.

### 3.2 모델 — Opera 자체 라우팅 계층

> "Neon runs on **Opera's AI engine, which is model-agnostic**, using different Google and OpenAI
> models depending on the task. Opera AI **intelligently routes your task to the most appropriate
> model** each time."

Neon Chat 에서는 사용자가 직접 고를 수도 있다:

```
Gemini, Grok, GPT / GPT Pro, Claude Opus / Claude Sonnet,
Deepseek, GLM-5, Qwen3
+ 생성 모델: Veo 3.1, Nano Banana 2, Nano Banana Pro
```

Neon Do(에이전트)에서는 **에이전트가 작업에 맞는 모델을 고른다** — 이미지 생성이면 이미지 모델,
조사면 브라우징·종합에 좋은 모델.

> 📌 **모델 라우팅을 제품이 소유한다.** Aside 는 사용자가 프로바이더를 고르게 하고
> ([02 §9](02-aside.md)), Neon 은 Opera 가 대신 고른다. 같은 "model-agnostic"이지만 방향이 반대다.

### 3.3 Neon 은 MCP 서버다

> "MCP, or Model Context Protocol, is an open standard that lets different AI tools communicate
> directly with each other. **Opera Neon acts as an MCP server**, which means external AI tools that
> support MCP can **connect to your live Neon browser session**."

> 📌 **`aside mcp` 와 같은 패턴이다** ([02 §6](02-aside.md)). 두 제품이 독립적으로 같은 결론에
> 도달했다 — **브라우저를 다른 에이전트의 실행 표면으로 노출한다.** [06](06-architecture-axes.md) §6
> 의 권고 9번("자기 도구를 MCP 로 노출하라")이 이 분야의 수렴 지점임을 보여준다.

### 3.4 Cards — 재사용 단위

> "They instruct Neon **how to handle a specific type of task** without you having to explain it each
> time. They're organized into **decks** grouped by area of work... When you build a workflow that
> works well for you, you can **turn it into a card and reuse it anytime with one click**.
> Cards work across Neon Chat, Neon Do and all Research Agents."

> 📌 [06 §5](06-architecture-axes.md) 에서 "반복되는 위임을 재사용 단위로"가 공통 과제라고 적었다.
> 세 제품의 축이 이제 분명해졌다:
>
> | 제품 | 이름 | 축 |
> |---|---|---|
> | **Neon** | **Cards** | **작업 유형** — "이런 종류의 일은 이렇게 다뤄라". 덱으로 묶임 |
> | Dia | Skills | 이름으로 호출하는 루틴 |
> | Aside | Routines | **시간** — cron(새 작업) / heartbeat(대화 이어가기) |
>
> Neon 의 Cards 는 **스케줄이 아니라 방법론**을 담는다. Aside 의 Routines 와 직교한다 —
> 한 제품이 둘 다 가질 수 있고, 아직 아무도 그러지 않았다.

### 3.5 자격증명

> "when you sign into a site and enter your credentials, those credentials are **not sent to any
> third-party servers (such as Opera's)**. The same is true for payment details, which **stay within
> your browser session** and are never sent to Opera or any third-party servers."

> ⚠️ 이 문장은 **자격증명이 Opera 서버로 가지 않는다**고 말하지, **에이전트가 볼 수 없다**고
> 말하지 않는다. Aside 의 값 은닉이나 Dia 의 요소 은닉과는 **다른 층위의 보장**이다.
> 계획이 클라우드에 있으므로(§3.1) 페이지 맥락이 모델로 갈 때 무엇이 포함되는지는 별개 문제다.
> 미확인.

### 3.6 학습 금지

> "No. Opera doesn't train models on user data. Opera's AI engine **orchestrates third-party models**,
> and Opera's agreements with providers such as OpenAI and Google prohibit them from using Opera
> users' data to train their models."

Dia 와 같은 구조의 약속이다 — 자사 학습 없음 + 제공자 계약으로 금지.

## 4. 비교표 갱신

| 축 | Aside | Dia | Opera Neon |
|---|---|---|---|
| 계획 위치 | **로컬 데몬** | **서버 경유** | **클라우드 모델** |
| 실행 위치 | 로컬 | 로컬 | 로컬 (Neon Do) |
| 모델 선택권 | **사용자** (BYO 구독/키) | 제품 (GPT/Claude/Gemini) | **제품이 라우팅** (Chat 은 선택 가능) |
| 재사용 단위 | Routines (시간) | Skills (호출) | **Cards (작업 유형)** |
| MCP | ✅ `aside mcp` | — | ✅ **MCP 서버** |
| CLI | ✅ | — | ✅ (제품 페이지 언급) |
| 프롬프트 주입 방어 문서화 | 부분 (승인·권한) | **✅ 구체적** | 미확인 |
| 자격증명 보호 방식 | **값 은닉** (금고) | **요소 은닉** (인식에서 제거) | 서버 미전송 (에이전트 가시성은 미확인) |
| 기본 데이터 수집 | 분석 공유 기본 on | **내용 데이터 기본 on** (30일) | 학습 금지 명시 |

## 5. 남은 미확인

| 항목 | 상태 |
|---|---|
| Dia 의 암호 알고리즘 | ⚠️ "encrypted" 라고만 하고 방식 미공개 |
| Dia 의 E2E 동기화 구현 | ⚠️ 동일 |
| Neon 의 에이전트 가시 범위 | ⚠️ 자격증명이 모델 맥락에 들어가는지 미확인 (§3.5) |
| Neon 의 Tasks 상세 | ⚠️ FAQ 답변을 끝까지 추출하지 못했다 |
| 양 제품의 바이너리 | ⚠️ 분석하지 않았다. Aside 수준의 확인은 안 됐다 |

> 📌 **비대칭을 기억할 것**: Aside 는 바이너리까지 뜯어서 주장을 검증했고
> ([08](08-aside-code-level.md)·[09](09-aside-browser-internals.md)·[10](10-aside-enforcement-and-native.md)),
> Dia·Neon 은 **제품 문서를 믿은 상태**다. 문서가 좋다는 것과 구현이 그렇다는 것은 다르다.
