---
id: TASK-2026-09-22-agent-harness-notes-003
status: done
created_at: 2026-09-22
source_anchor: generic-task-2026-09-22-agent-harness-notes-003
source_path: backlog/2026-09-22.md
kind: generic
wbs: exempt
wbs_exempt_reason: 조사 로드맵 밖 기존 사실의 1차 출처 검증
---

# TASK-2026-09-22-agent-harness-notes-003 — Agents API 서버측 모델 목록 검증

## 📝 Description

- Status: done
- Priority: medium
- Request date: 2026-09-22
- Owner: ykylee
- Host:
- Host IP:
- Affected documents:
  - `docs/99-sources.md`
  - `docs/08-agents-api-reference.md`
  - `docs/05-agents-api.md`
  - `docs/15-model-providers.md`
  - `docs/16-responses-chat-adapter.md`

- Description: 99-sources.md 에 유일하게 미확인으로 남은 항목 — 클라이언트 카탈로그 9종과 Agents API 서버측 목록의 일치 여부를 1차 출처로 확인한다
- Completion criteria:

## 🛠️ Implementation / Content

- Progress: 2026-09-27 공개 산출물로는 결정 불가로 종료. 2026-09-30 세 표면으로 정착: Agents API unconstrained string, 번들 카탈로그 11종, ModelIdsShared 89값(Chat/Responses).
- Next session starting point:
- Remaining risks:

## ✅ Outcome

- Result: 2026-09-27: OpenAPI model 은 enum 없는 자유 string, agents-api/models.md 404. 클라이언트 카탈로그는 별개 표면.
- Result: 2026-09-30: 세 표면이 서로 다른 목록이라 "Agents 목록 = 카탈로그" 등식은 성립하지 않음. 가이드 예시는 gpt-6-astra 만. 카탈로그 9→11 (gpt-6.1-sol·gpt-6-sol·gpt-6-luna, gpt-5.4 제거). ModelIdsShared 89값은 Chat/Responses.
- Verification: openai-openapi 09-27 두 리비전 + 09-30 openapi.yaml 3,880,172 bytes; SessionAgentConfigParam.model type string no enum. models.json 11 slugs. 라이브 POST 는 OPENAI_API_KEY 부재로 미실시.
- Follow-up: 라이브 Agents session 의 slug 수락은 API 키가 있을 때.
