---
doc_id: wiki-schema
type: schema
status: active
scope: ai-workflow/wiki/
applies_to: all wiki pages
parent: docs/PROJECT_PROFILE.md
related:
  - ai-workflow/memory/active/PURPOSE.md
  - docs/99-sources.md
references:
  rules: [R1, R2, R3, R4, R5, R6, R7]
  anti_patterns: [A1, A2, A3, A4]
  validations: [V-1, V-2, V-3, V-4, V-5, V-6, V-7, V-8]
  phases: [P1, P2, P3, P4]
created: 2026-09-22
updated: 2026-09-22
---

<!-- standard-ai-workflow-kit: v1.10.0 -->

# Wiki 운영 헌법 (Operating Constitution)

## §0 TL;DR  {#s0-tldr}

| # | 항목 | 값 |
|---|---|---|
| 1 | 위치 | `ai-workflow/wiki/` (Runtime layer, R1) |
| 2 | 추적 | git 추적 (memory/ 와 분리, D2) |
| 3 | 페이지 타입 | 5종 (entities, concepts, decisions, patterns, queries) |
| 4 | primary record | 페이지 atomic (R2, 1 commit = 1 ingest) |
| 5 | 인덱스 | anchor 기반 (R4) |
| 6 | 머지 | additive (R5) + wiki 확장 (R7) |
| 7 | lint | 모순·스테일·고아·누락·깨진 backlink (5항목) |

## §1 5종 페이지 타입  {#s1-page-types}

| 타입 | 위치 | 주 용도 | primary key |
|---|---|---|---|
| `entities` | `entities/<group>/<slug>.md` | Component, Service, API, Person, System 같은 식별 가능 단위 | 이름 (canonical) |
| `concepts` | `concepts/<slug>.md` | MCP, Skill, Orchestrator, Pydantic 같은 추상 개념 | 슬러그 |
| `decisions` | `decisions/ADR-NNN-<slug>.md` | ADR 형식의 결정 기록 | ADR 번호 |
| `patterns` | `patterns/<slug>.md` | 재사용 가능 패턴 (harness overlay, memory write merge 등) | 슬러그 |
| `queries` | `queries/<YYYY-MM-DD>-<slug>.md` | file-back 답변 (구문·분석·합성 결과) | 날짜+슬러그 |

### §1.1 페이지 타입별 frontmatter  {#s1-1-frontmatter}

모든 페이지는 머신 파싱 가능한 YAML frontmatter 를 가진다. 필수 필드는 타입별로 다르다.

#### entities

```yaml
---
type: entity
status: active | draft | deprecated
last_ingested_from: <relative path to source>
related_pages: [<relative path>, ...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

#### concepts

```yaml
---
type: concept
status: active | draft | deprecated
last_ingested_from: <relative path to source>
related_pages: [<relative path>, ...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

#### decisions (ADR)

```yaml
---
type: decision
status: proposed | accepted | superseded
adr_id: ADR-NNN
decided_at: YYYY-MM-DD
alternatives_considered: [<option>, ...]
related_pages: [<relative path>, ...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

#### patterns

```yaml
---
type: pattern
status: active | draft | deprecated
used_in: [<component or project>, ...]
related_components: [<relative path>, ...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

#### queries (file-back 답변)

```yaml
---
type: query
asked_at: YYYY-MM-DD
sources: [<relative path>, ...]
answer_synthesis: <path to synthesis page or inline>
related_pages: [<relative path>, ...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

### §1.2 cross-page 식별자 규칙  {#s1-2-identifiers}

| ID 종류 | 형식 | 보존 정책 | 예시 |
|---|---|---|---|
| Rule (R) | `R1`, `R2`, ... | 영구. 개정 시 ID 유지, version 만 bump | `R4` (Index Structure) |
| Anti-pattern (A) | `A1`, `A2`, ... | 영구. 동일 | `A3` (index.md 자유 산문) |
| Validation (V) | `V-1`, `V-2`, ... | 영구. 동일 | `V-4` (anchor 구조 검사) |
| Phase (P) | `P1`, `P2`, ... | 영구. 동일 | `P1` (스켈레톤 단계) |
| ADR | `ADR-NNN-<slug>` | 영구. supersede 시 status 변경 | `ADR-004-wiki-layer` |

## §2 Ingest Workflow  {#s2-ingest}

소스 → 다중 페이지 갱신 + `log.md` append + 모순 플래그. 트리거는 per-session (D3).

| 단계 | 동작 | 산출물 |
|---|---|---|
| **1. read sources** | handoff.md + work_backlog.md + 오늘 backlog 읽기. 추가 소스: `last_ingested_from` 메타로 추적 | 입력 컨텍스트 |
| **2. identify pages** | 언급된 entity / concept / decision / pattern 식별 (5~15 페이지) | 후보 페이지 목록 |
| **3. multi-page update** | 후보 페이지를 atomic 단위로 갱신 (R2). `[CONTRADICTION]` 발견 시 양쪽 페이지에 명시 (R5) | 갱신된 페이지 5~15개 |
| **4. log append** | `log.md` 에 `## [YYYY-MM-DD] ingest | <summary>` 한 줄 + 1 commit (R2, 1 commit = 1 ingest) | log 항목 + commit |

### §2.1 ingest commit 메시지 규칙  {#s2-1-commit}

| 필드 | 형식 | 예시 |
|---|---|---|
| prefix | `wiki-ingest:` | `wiki-ingest: bootstrap + 2 concept pages` |
| body | 갱신 페이지 목록 (5~15개) | `concepts/harness, concepts/retained-reasoning` |

자동 push 금지 (A2). push 직전 `git fetch && git rebase origin/main` (R3). `.ingest_lock` 으로 동시 ingest 직렬화 (R3).

## §3 Query Workflow  {#s3-query}

"X 에 대해 뭐 아는가?" 형태의 질문 → 인덱스 기반 retrieval → file-back 판단.

| 단계 | 동작 | 산출물 |
|---|---|---|
| **1. index load** | `wiki/index.md` 먼저 로드. anchor 구조로 페이지 카탈로그 확인 (R4) | 후보 페이지 anchor 목록 |
| **2. identify relevant** | anchor 별 1줄 요약 + `related_pages` + `last_ingested_from` 보고 3~7개 페이지 선정 | 관련 페이지 집합 |
| **3. synthesize** | 선정 페이지 본문 + 표 + 코드 로 인용 합성. 페이지 citation 필수 | 답변 (사용자 보고) |
| **4. file-back decision** | 답변 길이 30줄 초과 또는 합성 결과가 durable knowledge 면 `queries/<date>-<slug>.md` 로 file-back. 일반 Q&A 는 메모리에만 | queries/ 페이지 또는 휘발 답변 |

### §3.1 file-back 트리거  {#s3-1-file-back}

| 조건 | 동작 |
|---|---|
| 답변 30줄 초과 | `queries/<date>-<slug>.md` 생성 |
| 합성 결과가 재사용 가능 | `queries/<date>-<slug>.md` 생성 |
| 1회성 단순 lookup | 메모리만 (file-back 안 함) |
| 모순 발견 | [CONTRADICTION] 태그 + 양쪽 페이지 명시 (R5) |

## §4 Lint Checklist  {#s4-lint}

주기적 (릴리스 전, 주 1회, 수동) 검사. 5항목.

| # | 항목 | 검사 방법 | 심각도 |
|---|---|---|---|
| 1 | **contradiction** | `[CONTRADICTION]` 태그 검색. 미해결 항목 = 0건 유지 | error |
| 2 | **stale** | `updated` 가 90일 이전인 페이지 목록. 5% 이상 = warning | warning |
| 3 | **orphan** | 인바운드 링크 0인 페이지. R1~R7 외의 신규 페이지는 반드시 1개 이상 inbound | error |
| 4 | **missing** | `related_pages` 에서 참조되지만 파일이 없는 경우. index.md anchor 와 실재 파일 1:1 매핑 | error |
| 5 | **broken backlinks** | `[[path]]` 또는 `[text](path)` 의 target 이 존재하지 않음 | error |

### §4.1 자동화 매핑  {#s4-1-automation}

| 검사 | 자동화 (planned) | 비고 |
|---|---|---|
| 1 contradiction | `check_wiki_antipatterns.py` | R5·A4 와 결합 |
| 2 stale | `check_wiki_antipatterns.py` | 90일 임계치 |
| 3 orphan | `check_wiki_index_structure.py` | inbound 그래프 분석 |
| 4 missing | `check_wiki_index_structure.py` | index anchor vs filesystem |
| 5 broken | `check_wiki_antipatterns.py` | link graph walker |

## §5 Cross-Reference Index  {#s5-cross-references}

### §5.1 Rules (R1~R7)  {#s5-1-rules}

상위 spec: standard_ai_workflow kit v1.10.0 의 wiki 규칙. 이 저장소에 사본은 없고, 아래 표가 정본 요약이다.

| ID | 이름 | 한 줄 | 검증 |
|---|---|---|---|
| **R1** | Wiki Location | `ai-workflow/wiki/` 단일. 다른 위치 사용 금지 | V-1 |
| **R2** | Page Atomicity | 1 commit = 1 ingest (5~15 페이지 동시 갱신) | V-2 |
| **R3** | Pull-Before-Push | push 직전 `fetch && rebase origin/main` 필수. `.ingest_lock` 으로 동시 ingest 직렬화 | V-3 |
| **R4** | Index Structure | `index.md` anchor 기반. `### [[path]] {#anchor}` 스키마 강제 | V-4 |
| **R5** | Additive Merge | 충돌 시 양쪽 결합, 폐기 금지. LLM reviewer 가 canonical 선택 | V-5 |
| **R6** | Topic-Branch Mode | 6+ 페이지 분량 큰 탐색 phase 는 `wiki/topic/<name>` 브랜치 | V-6 |
| **R7** | Merge-Resolution Extension | `merge-doc-reconcile` 위키 확장. 4 conflict type 분류 | V-7 |

### §5.2 Anti-Patterns (A1~A4)  {#s5-2-antipatterns}

상위 spec: standard_ai_workflow kit v1.10.0 의 wiki 안티패턴. 이 저장소에 사본은 없다.

| ID | 안티패턴 | 위험 | 대안 |
|---|---|---|---|
| **A1** | 페이지 분할 동시 작업 | merge 시 backlink graph 깨짐, R2 위반 | 단일 페이지 = 단일 owner. 동시 작업 필요 시 topic branch (R6) |
| **A2** | 자동 push | ref lock cascade 실패, 동시 ingest data loss | R3 sync protocol 강제 |
| **A3** | `index.md` 자유 산문 / anchor 미부착 | 영구 충돌 지점, R4 위반 | anchor 기반 구조화 강제 |
| **A4** | 위키 merge 결과 자동 accept | 의미적 모순 가려짐, R5·R7 위반 | R5 additive + R7 semantic-conflict LLM review 의무 |

### §5.3 Validation (V-1~V-8)  {#s5-3-validation}

| ID | 검증 | 자동화 (planned) | 심각도 |
|---|---|---|---|
| **V-1** | wiki 위치 단일성 (R1) | `check_wiki_location.py` | error |
| **V-2** | commit = 1 ingest (R2) | `check_wiki_commit_unit.py` | error |
| **V-3** | rebase 없이 push = 0 (R3) | `check_wiki_sync_protocol.py` | error |
| **V-4** | index.md anchor 구조 (R4) | `check_wiki_index_structure.py` | error |
| **V-5** | 충돌 commit 의 양쪽 보존 (R5) | `check_wiki_additive_merge.py` | error |
| **V-6** | topic branch → main PR review (R6) | `check_wiki_topic_branch_promotion.py` | warning |
| **V-7** | `--apply` 호출 시 `confirm-llm-review` (R7) | `merge-doc-reconcile` flag check | error |
| **V-8** | 안티패턴 A1~A4 검출 | `check_wiki_antipatterns.py` | error |

### §5.4 Phases (P1~P4)  {#s5-4-phases}

| ID | 기간 | 목표 | DoD |
|---|---|---|---|
| **P1** | 1~2주 | 디렉토리 + SCHEMA + index + 1~2 concept page 수동 작성. lint 스킬 1차 | V-1·V-4 통과, 수동 1 page ingest |
| **P2** | 2~4주 | `wiki-ingest` / `wiki-lint` 스킬, 5+ 페이지 누적, R2·R3·R5 적용 | V-2·V-3·V-5 통과, 자동 ingest 5+ 회 |
| **P3** | 1~2월 | `wiki-query` 스킬, `merge-doc-reconcile` 위키 확장, topic branch (R6) | V-6·V-7 통과, semantic-conflict 1+ LLM review |
| **P4** | 3월+ | 하네스 overlay 6종 동기화, federated sync 평가, ADR-004 정식 채택 | harness 6종 동기화, 1+ project pilot, ADR-004 status = accepted |

## §6 Writing Convention Reminder  {#s6-writing-convention}

본 wiki 의 모든 페이지는 kit 의 writing convention 을 따른다. 핵심 요약:

| 원칙 | 적용 |
|---|---|
| YAML frontmatter | 메타·결정·validator·scope·lineage 모두 머신 파싱 가능 |
| Stable section anchors | `## §N Title {#sN-slug}` 형식. 외부 cross-reference 안정 |
| Tables over prose | 구조화 데이터는 항상 table (decision matrix, rule schema) |
| No narrative fluff | 배경 서술 최소화. 결정·규칙·근거 중심 |
| ID 영구 보존 | R / A / V / P 번호는 개정 시에도 유지, version 만 bump |
| Cross-reference 형식 | 상대경로 + `#anchor` (예: `[§4 Rules](path#s4-rules)`) |
| Language policy | 한국어 (user-facing prose) + 영어 (technical terms, code, paths) |

### §6.1 섹션 anchor 작성 규칙  {#s6-1-anchor}

| 패턴 | 예시 |
|---|---|
| `## §N Title  {#sN-slug}` (한글 제목 OK) | `## §4 Lint Checklist  {#s4-lint}` |
| `### §N.M Sub  {#sN-m-slug}` (하위 섹션) | `### §4.1 자동화 매핑  {#s4-1-automation}` |
| anchor 는 ASCII 소문자 + hyphen | `#s5-1-rules` ✅, `#s5-1-Rules` ❌ |

### §6.2 페이지간 cross-link  {#s6-2-cross-link}

| 형식 | 용도 |
|---|---|
| `[[concepts/harness]]` | wiki 내부 페이지 (R4 의 `[[path]]` anchor 기반) |
| `[§4 Rules](path#s4-rules)` | 외부 섹션 cross-reference (R7 의 상대경로 + anchor) |
| `[harness concept](./concepts/harness.md)` | 일반 마크다운 링크 (UI fallback) |

## §7 Bootstrap State (P1)  {#s7-bootstrap}

본 wiki 는 기존 조사 저장소를 표준 워크플로우에 편입하며 P1 단계로 세워졌다.

| 항목 | 상태 |
|---|---|
| 디렉토리 | `ai-workflow/wiki/` + `concepts/` 생성 완료 |
| skeleton 파일 | `SCHEMA.md`, `index.md`, `log.md`, `.gitignore` 생성 완료 |
| concept 페이지 | **13종** — [`./index.md`](./index.md) 참조 |
| pages 총수 | 13 (P1 목표 1~2 초과 달성) |
| 다른 페이지 타입 | `entities` / `decisions` / `patterns` / `queries` 는 아직 없다 — 필요가 생길 때 만든다 |
| ADR | 이 저장소에는 아직 없다 |

이 저장소 고유의 제약 두 가지:

| # | 제약 |
|---|---|
| 1 | **위키는 `docs/` 의 대체가 아니라 재색인이다.** 사실의 SSOT 는 `docs/` 에 남고, 위키는 같은 사실을 개념 축으로 다시 건다. 두 곳이 갈리면 `docs/` 가 이긴다. 이 제약은 선언이 아니라 **집행된다** — `scripts/check_wiki_freshness.py` 와 `.githooks/pre-commit` 이 원 문서만 바뀐 커밋을 막는다 ([PROJECT_PROFILE §5](../../docs/PROJECT_PROFILE.md)) |
| 2 | **등급을 잃지 않고 옮긴다.** 원문이 추론(inferred)·반증(refuted)으로 표시한 것은 위키 페이지에서도 그 등급을 유지한다. 등급을 떼면 그 순간 거짓이 된다 — [[concepts/primary-source-verification]] |

## §8 다음에 읽을 문서  {#s8-next}

- 인덱스: [`./index.md`](./index.md)
- 인제스트 로그: [`./log.md`](./log.md)
- 프로젝트 프로파일: [`../../docs/PROJECT_PROFILE.md`](../../docs/PROJECT_PROFILE.md)
- 방향 의도: [`../memory/active/PURPOSE.md`](../memory/active/PURPOSE.md)
- 첫 concept: [`./concepts/harness.md`](./concepts/harness.md)

## §9 Revision Log  {#s9-revision-log}

| Date | Version | Change | Author |
|---|---|---|---|
| 2026-06-12 | 0.1.0 | kit 원본 초안. 5 page types, ingest/query/lint workflow, R1~R7·A1~A4·V-1~V-8·P1~P4 cross-reference | standard_ai_workflow kit |
| 2026-09-22 | 0.1.2 | 재색인 제약을 집행 장치에 연결 (pre-commit + PostToolUse 훅) | agent-harness-notes |
| 2026-09-22 | 0.1.1 | agent-harness-notes 도입. 이 저장소에 없는 `.omo/plans` 참조 제거, §7 을 실제 상태로 교체, 재색인·등급 보존 제약 2건 추가 | agent-harness-notes |
