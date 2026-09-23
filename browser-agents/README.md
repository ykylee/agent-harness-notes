# 브라우저형 에이전트 도구 — 조사 노트

**Aside** 를 중심으로, 브라우저를 제어 표면으로 삼는 에이전트 도구들을 조사한다.
기능·구성·구조·디자인·UI/UX 를 축으로 보고, 마케팅 문구가 아니라 **문서·소스·리버싱 기록**에서 읽는다.

조사일: 2026-09-22 · 브랜치: `study/browser-agents`

> ⚠️ **이 저장소의 기존 조사(`docs/`)와 별개 주제다.** 기존 조사는 OpenAI Codex 하네스이고,
> 이쪽은 브라우저형 에이전트다. scope 관계는 [SCOPE.md](SCOPE.md) 참조.

## 문서

| 문서 | 내용 |
|---|---|
| [01-landscape.md](01-landscape.md) | 판세 — 3분류 체계, 2026 연표, **Atlas 종료**가 바꾼 것 |
| [02-aside.md](02-aside.md) | **Aside 심층** — 기능·구성·구조, 권한 모델, Vault, 메모리, CLI/MCP |
| [03-aside-design-ux.md](03-aside-design-ux.md) | **Aside 디자인·UI/UX** — 진입점 4종, 단축키, 분할 탭, 라쏘, 승인 흐름 |
| [04-comet-architecture.md](04-comet-architecture.md) | Perplexity Comet 아키텍처 — 리버싱으로 드러난 확장 3종·RPC·인식 모델 |
| [05-comparables.md](05-comparables.md) | Dia · Opera Neon · Claude for Chrome · Gemini in Chrome · Browser Use |
| [06-architecture-axes.md](06-architecture-axes.md) | **교차 분석** — 인식 / 제어 표면 / 신뢰 경계 / 자격증명 4축 |
| [08-aside-code-level.md](08-aside-code-level.md) | **Aside 코드레벨** — 바이너리에서 추출한 인식 모델·메모리 형식·원격 제어·내장 스킬 |
| [07-security.md](07-security.md) | 간접 프롬프트 주입 — 공격 사슬, 구조적 원인, 완화책, 미해결 상태 |
| [99-sources.md](99-sources.md) | 출처와 **검증 등급** — 확인 / 자체보고 / 추론 / 반증 |

## 한 줄 요약

> 브라우저형 에이전트의 경쟁축은 모델이 아니라 **제어 표면을 어디에 두는가**다 —
> 확장(Comet), 네이티브 브라우저(Aside), 라이브러리(Browser Use). 그 선택이
> 권한·자격증명·보안 경계를 전부 결정한다.

## 읽는 순서

1. 판세를 모르면 [01](01-landscape.md) 부터. Atlas 가 2026-08-09 에 사라졌다는 사실이 기존 비교글 대부분을 낡게 만들었다.
2. Aside 만 궁금하면 [02](02-aside.md) → [03](03-aside-design-ux.md).
3. "직접 만든다면" 관점이면 [06](06-architecture-axes.md) 이 핵심이다.
4. 어떤 주장을 믿어도 되는지는 [99](99-sources.md) 가 등급으로 말한다.
