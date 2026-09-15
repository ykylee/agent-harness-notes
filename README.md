# Codex Harness 학습 노트

OpenAI가 공개한 **Codex harness**(Codex 에이전트의 실행 엔진)와 그 위에 올라간 API 표면을
1차 자료(공식 블로그 / 공식 문서 / `openai/codex` 리포지터리 생성 스키마) 기준으로 정리한 문서입니다.

조사 기준일: 2026-09-14
저장소: <https://github.com/ykylee/agent-harness-notes>

## 한 줄 요약

> "harness"는 모델과 과업 사이에 있는 **실행 시스템**이다. OpenAI는 이 실행 시스템을
> (1) 오픈소스 바이너리/프로토콜(App Server), (2) 언어별 SDK, (3) 관리형 API(Agents API)
> 세 층으로 나눠서 외부에 개방했다.

## 공개 타임라인

| 날짜 | 무엇 | 성격 |
|---|---|---|
| 2026-02-04 | [Unlocking the Codex harness: how we built the App Server](https://openai.com/index/unlocking-the-codex-harness/) (Celia Chen) | App Server 아키텍처/프로토콜 설계 공개 |
| 2026-02-11 | [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) (Ryan Lopopolo) | "harness engineering"이라는 직무 개념 제시 |
| 2026-08 (2차 출처상 8/19~20) | [Codex as a platform: build on the open agent harness](https://developers.openai.com/blog/codex-as-a-platform) | CLI · app-server · SDK를 **오픈 에이전트 하네스**로 공식 포지셔닝 (Apache-2.0) |
| 2026-09-10 | [Agents API 퍼블릭 베타](https://developers.openai.com/api/docs/guides/agents-api/overview) | 같은 harness를 **OpenAI가 호스팅**하는 관리형 API로 제공 |

## 문서 구성

| 문서 | 내용 |
|---|---|
| [01-overview.md](docs/01-overview.md) | harness란 무엇인가, 내부 구성요소, 3-Layer 개방 구조 |
| [02-app-server-protocol.md](docs/02-app-server-protocol.md) | **핵심.** App Server JSON-RPC 프로토콜 전체 (전송, 핸드셰이크, 104개 메서드, 84개 알림, 승인 흐름) |
| [03-sdk.md](docs/03-sdk.md) | TypeScript / Python SDK |
| [04-cli-exec.md](docs/04-cli-exec.md) | `codex exec` 비대화형 모드 |
| [05-agents-api.md](docs/05-agents-api.md) | 관리형 Agents API 개념 (세션 / 샌드박스 / 서브에이전트) |
| [08-agents-api-reference.md](docs/08-agents-api-reference.md) | **Agents API 레퍼런스** — OpenAPI 스펙에서 추출한 엔드포인트 33개 · 스키마 · 이벤트 30종 |
| [06-choosing.md](docs/06-choosing.md) | 4가지 통합 경로 비교 및 선택 기준 |
| [07-harness-engineering.md](docs/07-harness-engineering.md) | OpenAI 내부 "0줄 수기 코드" 실험에서 나온 운영 원칙 |
| [99-sources.md](docs/99-sources.md) | 출처 목록 및 검증 상태 |

## 빠르게 손에 잡히는 것부터

```bash
# 1. Codex CLI 설치
curl -fsSL https://chatgpt.com/codex/install.sh | sh

# 2. app-server 프로토콜 타입을 직접 생성해보기
codex app-server generate-ts            # TypeScript 정의
codex app-server generate-json-schema   # JSON Schema 번들

# 3. 한 턴의 실제 JSON 트래픽 전부 구경하기
codex debug app-server send-message-v2 "run tests and summarize failures"
```

## 라이선스

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

이 저장소의 **노트와 정리 글**은 [Creative Commons Attribution 4.0 International](LICENSE)
(CC BY 4.0)을 따릅니다. 출처를 밝히면 자유롭게 공유·수정·상업적 이용이 가능합니다.

> © 2026 ykylee · <https://github.com/ykylee/agent-harness-notes> · CC BY 4.0

다만 문서 안에는 출처를 밝힌 **인용문과 코드 예제**가 포함되어 있으며, 이들에는 각자의 조건이 적용됩니다.

| 대상 | 조건 |
|---|---|
| 이 저장소의 노트·요약·표·주석 | **CC BY 4.0** (이 저장소) |
| [`openai/codex`](https://github.com/openai/codex) 에서 인용한 코드·스키마 | Apache-2.0 (OpenAI) |
| [`openai/openai-openapi`](https://github.com/openai/openai-openapi) 에서 추출한 스펙 내용 | 해당 저장소의 라이선스 (OpenAI) |
| OpenAI 블로그·공식 문서에서 인용한 문장 | © OpenAI. 출처 표기와 함께 인용 목적으로만 포함 |

이 저장소는 OpenAI와 무관한 개인 학습 노트이며, 공식 문서를 대체하지 않습니다.
정확한 내용은 항상 [원문](docs/99-sources.md)을 확인하세요.
