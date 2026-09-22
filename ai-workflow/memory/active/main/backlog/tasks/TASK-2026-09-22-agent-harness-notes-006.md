---
id: TASK-2026-09-22-agent-harness-notes-006
status: done
created_at: 2026-09-22
source_anchor: generic-task-2026-09-22-agent-harness-notes-006
source_path: backlog/2026-09-22.md
kind: generic
---

# TASK-2026-09-22-agent-harness-notes-006 — docs 수정 시 위키 재색인 강제

## 📝 Description

- Status: done
- Priority: high
- Request date: 2026-09-22
- Owner: ykylee
- Host:
- Host IP:
- Affected documents:
  - `docs/PROJECT_PROFILE.md`
  - `ai-workflow/wiki/SCHEMA.md`

- Description: docs/ 를 고쳤는데 대응 concept 페이지가 따라가지 않는 상태를 커밋 경계에서 차단한다
- Completion criteria: docs 만 고친 커밋이 실제로 차단된다
- Completion criteria: PostToolUse 훅이 실제로 발화해 재색인 대상을 알린다
- Completion criteria: 대응 관계 정의가 last_ingested_from 한 곳에만 있다

## 🛠️ Implementation / Content

- Progress: 역인덱스 체커 + pre-commit 차단 + Claude Code PostToolUse 알림 3지점 구성
- Next session starting point:
- Remaining risks:

## ✅ Outcome

- Result: scripts/check_wiki_freshness.py (history/staged/paths/hook 4모드), .githooks/pre-commit, .claude/settings.json
- Verification: pre-commit 차단 실측(exit 1), PostToolUse 발화 실측(sentinel + additionalContext 수신)
- Follow-up:
