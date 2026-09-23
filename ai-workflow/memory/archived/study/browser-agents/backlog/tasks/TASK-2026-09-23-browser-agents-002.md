---
id: TASK-2026-09-23-browser-agents-002
status: done
created_at: 2026-09-23
source_anchor: generic-task-2026-09-23-browser-agents-002
source_path: backlog/2026-09-23.md
kind: generic
---

# TASK-2026-09-23-browser-agents-002 — Aside 코드레벨 분석 — CLI 바이너리 추출

## 📝 Description

- Status: done
- Priority: high
- Request date: 2026-09-23
- Owner: ykylee
- Host:
- Host IP:
- Affected documents:
  - `browser-agents/99-sources.md`
  - `browser-agents/04-comet-architecture.md`

- Description: 헤드리스 리눅스에서 Aside CLI 를 설치해 Node SEA 페이로드를 추출하고 인식 모델·메모리 형식·원격 제어 구조를 확인한다
- Completion criteria: 인식 모델이 1차(코드)로 확인된다
- Completion criteria: 99-sources 의 미확인 항목이 갱신된다

## 🛠️ Implementation / Content

- Progress: ESM 번들 67,774줄 추출. 미확인 2건 해소, 문서에 없던 사실 다수 확보
- Next session starting point:
- Remaining risks:

## ✅ Outcome

- Result: 08-aside-code-level.md 신설. 메모리=plain Markdown 확정, snapshot()={tree,diff} + 가상 ref ID 확인, Linux CLI 1급 지원·내장 사이트 스킬·원격 호스트 제어 발견
- Verification: 명령 실측으로 런타임 경계 확정 (guide 만 동작, 나머지는 로컬 데몬 필요)
- Follow-up:
