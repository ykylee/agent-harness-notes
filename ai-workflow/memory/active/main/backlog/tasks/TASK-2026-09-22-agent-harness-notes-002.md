---
id: TASK-2026-09-22-agent-harness-notes-002
status: done
created_at: 2026-09-22
source_anchor: generic-task-2026-09-22-agent-harness-notes-002
source_path: backlog/2026-09-22.md
kind: generic
---

# TASK-2026-09-22-agent-harness-notes-002 — openai/codex 드리프트 재확인

## 📝 Description

- Status: done
- Priority: high
- Request date: 2026-09-22
- Owner: ykylee
- Host: iyeong-gyun-ui-MacBookAir
- Host IP:
- Affected documents:
  - ``
  - `docs/01~06, 08~16, 99-sources.md`
  - `agent-ux/03, agent-ux/99`
  - `wiki concepts 12종, SYNTHESIS.md, REPORT(영/한), README.md`

- Description: 조사 기준일 2026-09-15 스냅샷 이후 openai/codex 변경분을 확인해 기존 문서의 사실이 여전히 유효한지 대조한다
- Completion criteria: 2026-09-15 이후 변경분 중 docs/ 사실에 영향 주는 항목을 모두 판정(유효/드리프트)하고 docs/99-sources.md 에 기록
- Completion criteria: requestOptionPicker·requestImplementation·startAeon 3종을 소스에서 확인해 docs/02 반영 여부 결정

## 🛠️ Implementation / Content

- Progress: 2026-09-26 완료. 기준 2fdcdeaf0e(09-15) → e72da2b538(09-26), 686커밋. 16편 전수 대조(유효 약 170건)
- Next session starting point:
- Remaining risks:

## ✅ Outcome

- Result: 반박(기준 시점부터 틀림) 14건: docs/02 '104 total'은 stable 부분집합(생성 스키마가 #[experimental] 클라이언트 메서드 62개·서버요청 1개를 뺌, 알림은 안 뺌), codex mcp-server·--full-auto 는 기준일 전 이미 제거, Python SDK 는 이미 app-server JSON-RPC, Windows elevated 는 서비스 필수 아님, hide_users 추론 반박, worldWritableWarning 은 아무도 안 보냄, ResponsesApiRequest 16필드, WebSocket 은 previous_response_id 를 잇는다(무상태는 HTTP 한정)
- Result: agent-ux 단서 3종은 드리프트 아님: 오픈소스 이력 전체·번들 엔진(0.158.0-alpha.2.1) 어디에도 없고 webview 에만 있다(같은 부류 총 8개). docs/99 §E.3
- Result: 드리프트: gatewayOAuth 4종, Windows mxc·private desktop opt-out 제거, model_catalog_url, 로컬 모델 +gpt-6-sol/luna −gpt-5.4, Agents API 턴 오류코드 17→18·세션 설정 변경·vault credential update
- Verification: 반박 판정은 전부 소스로 직접 재확인. 서브에이전트 판정 1건(docs/08 오류코드 '기준 시점부터 틀림')은 기각 → 드리프트로 정정. 위키 신선도 검사: 기존 오탐 4건 외 경고 없음
- Follow-up: webview 전용 메서드(thread/startAeon 등)를 받는 엔진이 무엇인지 — 동적 관찰(macOS 에서 가능해짐)
- Follow-up: docs/10 L200 Agents API 플러그인 './' 규칙과 onboardingSkill 예외의 관계 미확인
