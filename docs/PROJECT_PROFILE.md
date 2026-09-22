<!-- standard-ai-workflow-kit: v1.10.0 -->

# Project Workflow Profile

- 문서 목적: 프로젝트 특화 규칙과 실행/검증 기준을 정의한다.
- 범위: 프로젝트 개요, 문서 구조, 기본 명령, 검증 포인트, 예외 규칙
- 대상 독자: 개발자, 운영자, AI agent, 프로젝트 온보딩 담당자
- 상태: draft
- 최종 수정일: 2026-09-22
- 관련 문서: [공통 표준](../ai-workflow/core/global_workflow_standard.md)

## 1. 프로젝트 개요
- 프로젝트명: Codex Harness — Study Notes
- 프로젝트 목적: OpenAI Codex 하네스(App Server / SDK / Agents API)를 1차 출처 기반으로 조사·검증하고 문서로 남긴다
- 주요 이해관계자: ykylee (단독 조사자 겸 관리자)
- 성격: **코드가 없는 조사 문서 저장소.** 산출물은 `docs/` 의 마크다운 문서와 `REPORT.md` / `REPORT.ko.md` 이며,
  빌드·배포·런타임이 존재하지 않는다. 따라서 "테스트"는 실행이 아니라 **출처 재검증**을 뜻한다.

## 2. 문서 구조 (Path)
- 문서 위키 홈: `README.md` (문서 목차), `docs/` (본문 16편)
- 최종 보고서: `REPORT.md` (영문), `REPORT.ko.md` (한국어)
- 출처·검증 기록: `docs/99-sources.md`
- 운영 문서 홈: `ai-workflow/memory/active/`
- 백로그 위치: `ai-workflow/memory/active/main/backlog/`
- 세션 인계 문서: `ai-workflow/memory/active/main/session_handoff.md`
- 환경 기록 위치: `ai-workflow/memory/active/repository_assessment.md`

## 3. 기본 명령 (Commands)
- 설치: 해당 없음 — 의존성 없는 마크다운 저장소
- 로컬 실행: 해당 없음 — 실행 대상이 없다
- 빠른 테스트: `grep -rn "](" docs/ README.md REPORT.md REPORT.ko.md` 로 상대 링크 깨짐 육안 확인
- 격리 테스트: 해당 없음
- 실행 확인: 1차 출처 URL 재확인 — OpenAI 문서 페이지는 URL 끝에 `.md` 를 붙이면 원본 마크다운을 돌려준다

## 4. 검증 포인트 (Validation)
- 코드 변경: 해당 없음
- 문서 변경:
  - **주장 하나에 출처 하나.** 근거 없는 문장을 새로 넣지 않는다.
  - 2차 출처(블로그·요약 기사)의 주장은 `openai/codex` 저장소의 생성 스키마·Rust 소스로 대조하기 전에는 확정으로 적지 않는다.
  - 추론으로 채운 부분은 문서 안에서 **추론이라고 명시**한다 (예: `14-windows-sandbox.md` 의 Windows 내부 구조).
  - 사실이 바뀌면 `docs/99-sources.md` 의 검증 표를 같은 커밋에서 갱신한다.
  - 영문 문서를 고치면 `REPORT.ko.md` 의 대응 부분도 같은 커밋에서 맞춘다.
- UI 변경: 해당 없음
- 배포/운영: 해당 없음 — 변경은 main 에 직접 커밋한다

## 5. 예외 규칙 (Policy)
- 병합: 단독 저장소이므로 상태 문서 충돌은 발생하지 않는다. 충돌 시 `backlog/tasks/` 를 SSOT 로 본다.
- 승인: 기존 문서의 **결론을 뒤집는** 수정(확정→반증 등)은 사용자 확인을 거친다.
- 제약:
  - 조사 기준일은 `openai/codex` 2026-09-15 스냅샷이다. 빠르게 움직이는 저장소이므로 재조사 시 드리프트를 먼저 확인한다.
  - 날짜는 타임존 때문에 1차 출처끼리도 갈린다. 게시일은 UTC 기준으로 적고 필요하면 환산표를 남긴다.
- 기타: 문서 본문은 영어, 커밋 메시지와 운영 문서는 한국어로 쓴다 (기존 이력의 컨벤션).

## 다음에 읽을 문서
- [세션 인계 문서](../ai-workflow/memory/active/main/session_handoff.md)
- [작업 백로그](../ai-workflow/memory/active/main/backlog/)
- [출처·검증 기록](99-sources.md)
