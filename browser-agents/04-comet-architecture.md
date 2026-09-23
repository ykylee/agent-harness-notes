# 04. Perplexity Comet — 아키텍처

> 출처: Zenity Labs 의 리버싱 기록(확장 번들 해체·서비스워커 분석), Wikipedia(날짜·플랫폼),
> Brave 보안 연구(§5). **제품 문서가 아니라 리버싱 결과**이므로, 이 저장소 기준으로는
> "관측된 구현"이지 "벤더가 보증한 명세"가 아니다 — [99](99-sources.md) §5.

## 1. 왜 Comet 을 깊이 보나

Aside 와 **정반대 구조**이기 때문이다. 둘 다 "네이티브 AI 브라우저"로 분류되지만
([01 §1](01-landscape.md)), 속을 열면 Comet 은 **확장 3개로 구현된 브라우저**다.
겉 분류와 속 구조가 어긋나는 사례로서 가치가 있다.

## 2. 4개 구성요소

| 구성요소 | 역할 |
|---|---|
| **Perplexity API Backend** | "Where the AI model lives, plans tasks, and issues commands" — **모델과 계획이 서버에 있다** |
| **UI** | 사용자 인터페이스 |
| **커스텀 Chrome 확장 3종** | 실제 브라우저 제어 |
| **Chromium** | 브라우저 본체 |

> 📌 **결정적 차이: 계획이 서버에 산다.** 백엔드가 작업을 계획하고 **명령을 발행**하면
> 로컬 확장이 집행한다. Aside 는 로컬 우선을 내세우고 사용자 API 키·구독까지 받는 반면,
> Comet 은 제어 루프 자체가 Perplexity 인프라에 있다.

## 3. 확장 3종

| 확장 | 내용 |
|---|---|
| **comet-agent** (`agents.crx`) | **700KB 서비스워커**가 완전한 RPC 시스템을 구현. 백엔드에서 명령을 받는다. 핵심 라우터는 `dispatchRpcRequest` — 들어온 요청을 보안 검증을 거쳐 핸들러로 보낸다 |
| **Comet** (`perplexity.crx`) | 탭 생명주기, 사이드카 AI 패널, 분할 뷰 세션. PDF 파싱과 예외 모니터링 |
| **Comet Web Resources** (`comet_web_resources.crx`) | UI 자산용 로컬 CDN. **권한 없음, 백그라운드 스크립트 없음** |

확장은 `https://www.perplexity.ai/rest/browser/update-crx` 로 자동 갱신된다 — **중앙 통제가 유지된다.**

> 📌 관심사 분리가 뚜렷하다. 권한이 필요한 것(agent), 브라우저 통합(Comet), 권한이 전혀 없는
> 정적 자산(Web Resources). 세 번째가 권한도 백그라운드도 없다는 것은 **의도적 최소 권한**이다.

## 4. 이중 채널 통신

두 개의 병렬 스트림이 자동화를 조율한다.

| 채널 | 엔드포인트 | 용도 |
|---|---|---|
| **SSE** | `/rest/sse/perplexity_ask` | 모델 추론과 대화 응답을 실시간 스트리밍 |
| **WebSocket** | `wss://www.perplexity.ai/agent` | 브라우저 자동화용 고빈도 양방향 RPC |

사이드카가 들어온 `entropy_request` 메시지를 풀어 Chrome 확장 메시징 API 로 확장에 전달한다.

> 📌 **대화 흐름과 자동화 흐름을 다른 전송으로 분리**한 것이 설계 판단이다. 사람이 읽을
> 스트림(SSE, 단방향, 고지연 허용)과 기계 제어(WebSocket, 양방향, 저지연 필요)는 요구가 다르다.
> 이 저장소 기존 조사의 App Server 가 하나의 양방향 JSON-RPC 로 둘 다 처리한 것과 대조된다
> ([`docs/02-app-server-protocol.md`](../docs/02-app-server-protocol.md)).

## 5. 에이전트의 인식 — 접근성 트리

모델은 페이지를 **"특수 주석이 달린 단순화된 HTML 표현"** 으로 본다.

`ReadPage` RPC 는 `chrome.debugger` 를 호출해 Chrome 의
**`Accessibility.getFullAXTree`** 를 쓰고, **접근성 트리의 YAML 표현**을 돌려준다.

> 📌 이것이 중요한 선택이다. 스크린샷(픽셀)도 아니고 원본 DOM 도 아닌 **접근성 트리**를 인식
> 기반으로 삼았다. 접근성 트리는 이미 "의미 있는 상호작용 요소"로 정제돼 있어 토큰 효율이 좋고,
> 스크린 리더가 쓰는 것과 같은 표현이라 **의미론이 이미 정리돼 있다**.
> 세 가지 인식 방식의 비교는 [06 §2](06-architecture-axes.md).

## 6. 동작 어휘

| RPC | 내용 |
|---|---|
| **`ComputerBatch`** | 저수준 동작 시퀀스(클릭·드래그·스크롤·키입력)를 **원시 픽셀 좌표로** 실행 |
| `FormInput` | 양식 입력 |
| `Navigate` | 이동 |
| `GetPageText` | 텍스트 추출 |
| `TabsCreate` | 탭 생성 |
| **`CreateSubagent`** | **하위 에이전트 생성** |

> 📌 **인식은 접근성 트리(의미), 동작은 픽셀 좌표(기하)** 라는 비대칭이 흥미롭다. 읽을 때는
> 정제된 의미 구조를 쓰고, 조작할 때는 좌표로 내려간다. Browser Use 가 **인식과 동작을 같은
> 인덱스 체계로 묶은 것**([05 §5](05-comparables.md))과 대조적이다 — Comet 쪽이 더 유연하지만
> 좌표 오차에 취약하다.

`CreateSubagent` 의 존재는 **다중 에이전트 위임**이 프로토콜 수준에 있다는 뜻이다.

## 7. 보안 경계

두 검증 함수가 능력을 제한한다.

| 함수 | 차단 대상 |
|---|---|
| **`isInternalPage`** | `chrome://settings`, `chrome://password-manager`, `comet://` URL |
| **`isUrlBlocked`** | `file://` 파일시스템 접근, 비허용 문서 유형, **관리형 스토리지를 통한 관리자 정의 블랙리스트**, 사용자 설정 도메인 블랙리스트 |

> 📌 `chrome://password-manager` 를 명시 차단한 것은 **자격증명 격리를 URL 수준에서** 한 것이다.
> Aside 가 **자격증명 자체를 에이전트에게 주지 않는 방식**([02 §4](02-aside.md))으로 푼 것과
> 접근이 다르다 — Comet 은 "그 페이지에 못 가게", Aside 는 "값을 안 보여주게".
>
> 관리자 정의 블랙리스트를 **관리형 스토리지**로 받는 것은 기업 배포를 고려한 설계다.

## 8. 사실 정보

| 축 | 내용 |
|---|---|
| 엔진 | Blink (Chromium) |
| 출시 | Windows·macOS 2025-07-09 / Android 2025-11-20 / iOS 2026-03-18 |
| 요구사항 | Windows 10+, macOS Big Sur+, Android 12+, iOS 18+, visionOS 2.0+ |
| 가격 | 초기 프리미엄 한정 → 2025-10 무료 개방 → 2026-03 에이전트 모드까지 무료 |
| 모델 | Max 구독자는 에이전트 모델 선택 가능 (기본 Opus 4.6, 대안 Sonnet 4.5) |

## 9. 보안 이력

| 사건 | 내용 |
|---|---|
| **간접 프롬프트 주입** (Brave, 2025) | 페이지 내용과 사용자 지시를 분리하지 않아 이메일·OTP 탈취 실증. 상세는 [07](07-security.md) |
| **CometJacking** | 민감 개인정보 탈취 가능. Perplexity 가 초기에 보안 영향을 부인했다가 이후 독자 발견·패치 |

> 두 건 모두 **아키텍처에서 따라 나온 것**이지 구현 버그가 아니다. 모델과 계획이 서버에 있고
> 페이지 내용이 그대로 맥락에 들어가는 구조에서는 이런 종류가 구조적으로 가능하다.

## 10. Aside 와의 구조 대조

| 축 | Comet | Aside |
|---|---|---|
| 제어 표면 | 네이티브 브라우저 + **확장 3종** | 네이티브 브라우저 |
| 계획 위치 | **서버 (Perplexity 백엔드)** | 로컬 우선 주장 |
| 모델 | Perplexity 제공 (Max 는 선택) | **BYO 구독 / BYO API 키 / 자체** |
| 인식 | 접근성 트리 (YAML) | **접근성 트리 + 가상 ref ID** ([08](08-aside-code-level.md)) |
| 동작 | 픽셀 좌표 배치 + 고수준 RPC | **ref 기반 Playwright locator** — 대칭 |
| 자격증명 | **URL 차단**으로 격리 | **값을 안 보여주는** 금고 |
| 전송 | SSE + WebSocket 이중 | 로컬 데몬 + tRPC (외부 엔드포인트 미확인) |
| 개발자 표면 | 공개 없음 | **CLI · MCP · REPL** |

> 📌 **갱신 (2026-09-23)**: 이 표의 Aside 열은 원래 "미공개"가 많았다. Comet 은 리버싱 당했기
> 때문에 내부가 알려졌고 Aside 는 그런 분석이 없었기 때문이다. 이후 **Aside CLI 를 직접
> 열어** 상당수가 채워졌다 — [08](08-aside-code-level.md). 정보량의 차이를 제품 성숙도의
> 차이로 읽으면 안 된다는 원래 경고가 그대로 입증됐다.
