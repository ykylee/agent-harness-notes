---
purpose_version: 1
last_purpose_review: 2026-09-22
---

# Purpose — 이 저장소의 Why

- 문서 목적: 이 저장소가 *왜* 존재하고 어디로 가는지(directional intent)를 정의한다. AI agent 가 session-start / backlog-update 시 읽어 작업 분류와 scope 판정에 사용한다.
- 범위: 4-element (Goals / Key Questions / Research Scope / Evolving Thesis)
- 대상 독자: AI agent, 저장소 관리자
- 상태: draft — 기존 조사 저장소를 표준 워크플로우에 편입하며 최초 작성
- 최종 수정일: 2026-09-22
- 관련 문서: [PROJECT_PROFILE.md](../../../docs/PROJECT_PROFILE.md), [99-sources.md](../../../docs/99-sources.md)

## 1. Goals

- **G1**: OpenAI Codex 하네스의 **실제 계약**(App Server JSON-RPC 프로토콜, SDK, Agents API)을
  블로그 요약이 아니라 **생성 스키마와 Rust 소스**에서 읽어 기록한다.
- **G2**: 자체 하네스를 만든다면 무엇을 구현해야 하는지 — 메서드·이벤트·승인 흐름·샌드박스·플러그인 —
  **구축 체크리스트로 환산 가능한 형태**로 남긴다.
- **G3**: 모든 주장에 검증 상태(1차 확인 / 추론 / 반증)를 붙이고, 틀린 2차 출처는 **지우지 않고 반증으로 보존**한다.
  반증의 기록이 이 저장소의 신뢰를 만든다.
- **G4**: 영문 본문과 한국어 보고서를 같은 사실 위에서 동기 유지한다.

## 2. Key Questions

- **Q1**: Codex 하네스에서 모델과 실행부의 경계(wire protocol)는 정확히 어디인가? 코어를 재사용할 수 있는가?
- **Q2**: 관리형 Agents API 와 오픈소스 App Server 는 같은 하네스인가, 다른 표면인가? 어디까지 일치하는가?
- **Q3**: Responses 페이로드를 Chat Completions 로 되돌리는 어댑터는 fork 없이 가능한가?
- **Q4**: 어떤 주장이 1차 출처로 확정되고, 어떤 것이 아직 추론인가? 그 경계를 문서가 스스로 말하는가?

## 3. Research Scope

### 포함 영역

- `openai/codex` 저장소의 생성 스키마·Rust 소스 독해
- App Server JSON-RPC 프로토콜 (메서드 / 알림 / 승인 / 전송 계층 / 오류 코드)
- Agents API (엔드포인트, 환경 유형, 샌드박스, 도구, 웹훅·관측·비용)
- CLI `codex exec`, TypeScript / Python SDK
- 모델 프로바이더 설정, Responses↔Chat Completions 어댑터 타당성
- Windows 네이티브 샌드박스, 마켓플레이스·플러그인 배포 형식
- 하네스 엔지니어링 운영 원칙 (OpenAI 내부 실험 기록)
- 출처 검증 기록과 반증 이력 (`99-sources.md`)

### 제외 영역

- **Codex 하네스의 실제 구현·포크·재배포** — 이 저장소는 조사 노트이지 코드베이스가 아니다
- OpenAI 외 벤더의 하네스 비교 조사 (Anthropic / Google 등) — 별도 저장소의 일
- 모델 자체의 성능 벤치마크 재현
- 사내 제품 설계 문서 — 여기의 결론을 가져다 쓰되, 여기에 쓰지 않는다
- 2차 출처만으로 확정한 서술 — 1차 대조 전에는 "미확인"으로만 남긴다

## 4. Evolving Thesis

*현재까지의 working hypothesis (바뀔 수 있다):*

- 하네스는 모델과 과업 사이의 **실행 시스템**이며, OpenAI 는 이를 바이너리·SDK·관리형 API 의 3계층으로 열었다.
- 문서화된 산문보다 **커밋된 아티팩트**(생성 스키마, 소스, 기본값)가 진실에 가깝다. 산문은 드리프트한다.
- 어댑터는 fork 가 아니라 **프로바이더 형태의 프록시**로 붙일 때만 공짜다. 상태를 갖는 순간 그 이점이 사라진다.
- 조사 기준일(2026-09-15)은 빠르게 낡는다. 재조사의 첫 수는 새 사실 수집이 아니라 **기존 사실의 드리프트 확인**이다.
