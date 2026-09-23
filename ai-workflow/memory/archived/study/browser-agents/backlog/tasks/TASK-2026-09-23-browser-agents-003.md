---
id: TASK-2026-09-23-browser-agents-003
status: done
created_at: 2026-09-23
source_anchor: generic-task-2026-09-23-browser-agents-003
source_path: backlog/2026-09-23.md
kind: generic
---

# TASK-2026-09-23-browser-agents-003 — Aside 브라우저 바이너리 정적 분석

## 📝 Description

- Status: done
- Priority: high
- Request date: 2026-09-23
- Owner: ykylee
- Host:
- Host IP:
- Affected documents:
  - `browser-agents/04-comet-architecture.md`
  - `browser-agents/99-sources.md`

- Description: macOS DMG 를 내려받아 실행하지 않고 내부 구조·데몬·Vault 암호를 확인한다
- Completion criteria: Vault 암호 주장이 실제 호출부로 검증된다
- Completion criteria: 계획 위치(로컬/서버)가 구조로 확정된다

## 🛠️ Implementation / Content

- Progress: Chromium 포크 확인, MV3 확장 3종, 353MB 데몬 SEA 추출, libsodium 호출부 확인
- Next session starting point:
- Remaining risks:

## ✅ Outcome

- Result: 09-aside-browser-internals.md 신설. Argon2id/XChaCha20/sealed box 확인, 로컬 데몬 21420 확정, 자기 서술 1건 반증
- Verification: libsodium 래퍼가 아닌 background.js 실제 호출부에서 확인
- Follow-up:
