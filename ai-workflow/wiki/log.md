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

## [2026-09-23] ingest | 두 조사 융합 — 기존 8종 보강 + 신규 3종

소스: `browser-agents/` 11편 (브라우저형 에이전트 조사, `study/browser-agents` 브랜치)

**보강 (8)**: `control-plane-execution-plane`(계획 위치 3분화) · `wire-protocol-boundary`
(Aside 가 `CODEX_TOOL_CALL_PROVIDERS` 구현) · `primary-source-verification`(수법 성적·함정 2종) ·
`approval-gate`(채널 렌더 승인) · `provider-as-data`(선택 주체가 반대인 두 사례) ·
`capability-distribution`(재사용 단위 3축의 직교) · `harness`(외피 3형태, **표면 고유/무관 축 구분**) ·
`os-sandbox-policy`(정책 표현력, Computer Use)

**신규 (3)**: `perception-model` · `indirect-prompt-injection` · `credential-shielding`
— 전부 브라우저 조사에서만 나온 축이다. Codex 는 코딩 하네스라 페이지 인식 문제가 애초에 없다.

메모:
- 이 ingest 로 위키가 **두 조사를 함께 다루게 됐고**, 그것이 곧 저장소 성격의 변경이었다.
  공용 `PURPOSE.md` §0 에 범위 확장을 기록했다 — `browser-agents/SCOPE.md` 의 A안 조건 발동.
- 개념 페이지의 `last_ingested_from` 에 `browser-agents/*` 를 더했으므로
  **재색인 강제 훅의 커버리지가 자동으로 두 트리를 덮는다.** 새 장치는 필요 없었다.
- `[CONTRADICTION]` 0건. 두 조사의 결론이 충돌하는 지점은 없었고, 오히려
  `wire-protocol-boundary` 에서 **코드 수준으로 만났다**.
- 교차 종합 `SYNTHESIS.md` 를 루트에 신설했다 — 위키는 개념 단위, SYNTHESIS 는 읽을거리.

