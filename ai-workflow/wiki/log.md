---
type: meta
status: active
r9_skip: true
title: Wiki Ingest/Query Log
related_pages: [index]
last_touched: 2026-09-22
created: 2026-09-22
---

<!-- standard-ai-workflow-kit: v1.10.0 -->

# Wiki Ingest/Query Log

> 형식은 [`./SCHEMA.md`](./SCHEMA.md) §2. ingest / query 마다 entry 를 append 한다.

## [2026-09-22] ingest | bootstrap + concept 13종 (기존 조사 문서 16편에서 추출)

소스: `docs/01`~`docs/16`, `docs/99-sources.md`, `REPORT.md` (전부 기존 커밋된 문서. 신규 조사 없음)

갱신 페이지 (13):
`concepts/harness`, `concepts/harness-engineering`, `concepts/thread-turn-item`,
`concepts/approval-gate`, `concepts/wire-protocol-boundary`,
`concepts/stateless-conversation-wire`, `concepts/retained-reasoning`,
`concepts/control-plane-execution-plane`, `concepts/execution-environment-topology`,
`concepts/os-sandbox-policy`, `concepts/capability-distribution`,
`concepts/provider-as-data`, `concepts/primary-source-verification`

메모:
- 위키는 `docs/` 의 **대체가 아니라 재색인**이다. 문서는 출처 축(App Server / Agents API / 어댑터)으로
  정렬돼 있고, 위키는 **개념 축**으로 정렬한다. 사실의 SSOT 는 `docs/` 에 남는다.
- 각 페이지의 `last_ingested_from` 이 원 문서를 가리킨다. 원 문서가 바뀌면 해당 페이지를 재ingest 한다.
- `[CONTRADICTION]` 0건. 반증된 2차 출처는 모순이 아니라 **판정 완료 기록**이므로
  `concepts/primary-source-verification` §4 에 등급과 함께 보존했다.
- Windows 샌드박스 내부는 원문과 같이 **추론 등급**을 페이지 본문에 명시했다 — 등급을 잃지 않고 옮기는 것이 이 ingest 의 제약이었다.
