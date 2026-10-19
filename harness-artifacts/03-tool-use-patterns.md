# 03. Tool-use patterns — 여섯 레퍼런스가 tool 을 정의·호출·절단하는 방식

> **무엇인가.** Claude Code CLI 2.1.303(바이너리에서 분리한 모듈), Codex `d42056091`(Rust 소스),
> Gemini CLI 0.42.0(번들), opencode 1.17.12(분리 모듈), Strands SDK/harness `a9a62d4e`(소스),
> 그리고 REA 6.7.0(도구 *서버* 설계 문서)에서 **tool 호출 한 번의 비용**을 결정하는 장치만 뽑았다.
> 카탈로그 크기, 지연 노출, 병렬 호출, 결과 절단·영속화, 프롬프트 캐시, 승인 왕복. 보안·승인 의미론은
> 기존 노트(`docs/02`, `strands/03·07`, `agent-ux/08`)가 다루므로 반복하지 않는다.
>
> **왜 한국어인가.** 이 문서는 독자가 자기 하네스의 tool 효율을 고치려고 읽는 비교표다. 식별자·경로·
> 인용은 원문 그대로 영어다. 다른 노트와 달리 권고 절(§8)이 있는데, 특정 하네스의 설계가 아니라
> **검증 가능한 채택 후보**로만 적었다 (`PURPOSE.md` §0.7).
>
> **등급.** ✅ 소스/모듈에서 읽음 (`파일:행` 또는 모듈명) · 📣 설명문이 하는 주장 · ⚠️/추정 읽지 못해
> 추론한 것. 바이너리에서 나온 Claude Code·opencode 의 상수명은 난독화된 지역 변수명이다.
>
> **방법.** 보조 에이전트 4개가 하네스별로 같은 6개 질문(카탈로그·호출 루프·결과 처리·컨텍스트 경제·
> 승인 비용·기타)을 조사했고, 이 문서는 그 보고를 대조해 통합했다. 각 수치의 출처는 표 안에 있다.

## 1. 한눈에: 같은 문제, 여섯 가지 답

| 축 | Claude Code 2.1.303 | Codex `d42056091` | Gemini CLI 0.42.0 | opencode 1.17.12 | Strands `a9a62d4e` | REA 6.7.0 (서버) |
|---|---|---|---|---|---|---|
| 카탈로그 노출 | 항상 로드 세트 + **deferred**(이름 한 줄만) + `ToolSearch` | `ToolExposure {Direct, Deferred, DeferredModelOnly, Hidden}` + BM25 `tool_search`; MCP 는 항상 Deferred | 모델 패밀리별 선언 세트(`GEMINI_3_SET`/`LEGACY`), `excludeTools`/`mainAgentTools`; 검색·지연 없음 | 고정 순서 15종, 플래그 게이트; 검색·지연 없음 | `@tool` 데코레이터 → JSON Schema; 하네스 built-in 8개 | 172 tools, `compact` 스키마 프로파일로 496 KB→290 KB |
| 병렬 호출 | 시스템 프롬프트가 "make all independent tool calls in parallel" 지시 | Responses `parallel_tool_calls: true`; 핸들러별 `supports_parallel_tool_calls`, RwLock 게이트 | `Scheduler` 가 `wait_for_previous` 아닌 호출을 `Promise.all` — 검증·승인·실행 모두 병렬 | 자체 스케줄러 없음, AI SDK 즉시 실행에 의존(추정) | 기본 `ConcurrentToolExecutor` | 해당 없음(호출당 1 작업); 진행 알림 100 ms 레이트 제한 |
| 코드로 오케스트레이션 | `Workflow` 도구(스크립트가 서브에이전트 조합) | **code mode**: JS 한 덩어리가 V8 격리에서 `tools.*` 를 여러 번 호출, `text()` 로 고른 것만 반환 | — | — | `programmatic_tool_caller`: `print()` 한 텍스트만 모델로, `_MAX_OUTPUT_CHARS = 200_000` | — |
| 결과 절단 | Bash 30,000자 기본(최대 150,000); 도구별 `maxResultSizeChars` 1e5 다수 | exec 수집 1 MiB 하드캡 → 모델 전달 **10,000 tokens**(모델 카탈로그 값), head/tail 50:50 | 셸/MCP 만 4e4 자, head 20 %/tail 80 %; distillation 켜면 1e4 tok + LLM 요약 | 공통 `Truncate.output` 2,000줄/51,200 B; read 50 KB cap | 실행 시점 절단 없음; 후처리 계층(ContextOffloader 2,500 tok→1,000 미리보기; 하네스 `auto` 1,500/750) | 10 MiB 수신 버퍼 초과 시 `evidence_reference` 로 참조 반환 |
| 큰 결과의 행방 | **디스크 영속화** `tool-results/` + `<persisted-output>` 포인터 + 미리보기; `Use Read to view` | `original_token_count` 필드로 "잘렸다"만 알림 | `tool-outputs/session-<id>/` 저장 + "For full output see: <path>"; 마스킹 `<tool_output_masked>` | `tool-output/tool_<id>` 저장 + "Use the Task tool … Do NOT read the full file yourself" | 디스크 오프로드 + `retrieve_context(pattern, line_range)` 도구 | **Evidence ID** 보존 + `inspect_analysis_view` 페이징(`offset/limit/next_offset`) |
| 캐시 | `cache_control` 시스템 1블록 + 마지막 메시지 1블록; TTL 5m/1h | `prompt_cache_key` = 세션 ID, 서브에이전트는 부모와 공유; `previous_response_id` 증분 | 명시적 breakpoint 없음(암묵 캐시, 추정) | `CacheHint {tools, system, latest-user-message}`, Bedrock cap 4 | Bedrock `cachePoint`, Anthropic 메시지 캐시포인트 **1개만** 유지 | — |
| 컴팩션 | 자동 컴팩트(윈도−20,000) + **시간 기반 마이크로컴팩트**(오래된 tool_result→`[Old tool result content cleared]`/영속 포인터) | 95 % 유효 윈도, 턴 종료 컴팩션, 사용자 메시지 20,000 tok 보존 | 0.5×limit 트리거, functionResponse 5e4 예산 절단 → 0.3 보존 요약; 루프 감지 5/10 | reserved 20,000, preserve 8,000; prune 40,000/20,000 → `[Old tool result content cleared]` | SlidingWindow 40 / Summarizing 0.3·최근 10 보존 / 프리셋 70 % | 부분 결과 보존(`partial_observation`) |
| 승인 왕복 회피 | 규칙 `Bash(git *)`, "don't ask again" 이 규칙 생성, `auto` 분류기(별도 API 호출, 캐시됨), 훅 exit 2 | 세션 승인 캐시(`ApprovedForSession` 키: env·exe·cmd·cwd·tty·sandbox), execpolicy `prefix_rule`, Guardian 자동 리뷰어, 거부 메시지 900 tok 캡 | `PolicyEngine` priority 규칙, `ProceedAlways` 가 세션 규칙 생성, YOLO 도 DENY 유지 | `findLast` 규칙, `always` 가 대기 요청까지 자동 승인, doom loop 3 | `allowed_tools=["*","!delete_file"]` + `enable_trust` 세션 기억; Cedar 동기 판정 | 권한 플래그 자체를 안 둠(`readOnlyHint` 힌트만) |

## 2. Claude Code CLI 2.1.303 — 바이너리가 보여주는 것

출처: `bun-apps/claude/` 모듈(`chunk-*.js`), grep 만. 모듈명은 분리 결과의 파일명.

- **카탈로그.** `searchHint:"…"` 를 가진 도구 정의 **80개**(중복 제거; 예 `"read files, images, PDFs, notebooks"`, `"check on a background shell command by task ID"`). 대부분 플래그/세션 종류로 게이트되어 한 세션 노출은 20~30개 추정. 지연 판정 `chunk-wc616c60.js`: `function T(e){if(e.isMcp===!0)return!0; …; return e.shouldDefer===!0}` — **MCP 도구는 무조건 deferred**, built-in 은 `shouldDefer` 또는 원격 설정 목록. deferred 도구는 시스템 프롬프트에 `` `${e.name}: ${whenToUse}` `` **한 줄**만 들어간다(스키마 제외). `ToolSearch`: `"select:Read,Edit,Grep"` 정확 선택 / 키워드 / `"+slack send"` 필수어; `max_results` 기본 **5**; 결과에 `total_deferred_tools, pending_mcp_servers, failed_mcp_servers`. 미로딩 호출은 `InputValidationError`. deferral 로 아낀 토큰을 `countToolDefinitionTokens` 로 세어 캐시(`Ckr`) — 텔레메트리 추정.
- **lean prompt.** Read 등은 `prompt({model, leanPrompt})` 분기로 모델별 설명 길이를 바꾼다(`Reads up to 2000 lines by default` 6줄판).
- **호출 루프.** 시스템 프롬프트 `# Using your tools`: "If you intend to call multiple tools and there are no dependencies between them, make all independent tool calls in parallel … if some tool calls depend on previous calls … call them sequentially." + "Prefer dedicated tools over Bash when one fits". Bash `run_in_background` → `task-notification` 메시지로 모델을 깨움(MCP 도 `auto_background` 경로). `Agent` `subagent_type:"fork"` 는 "inherits your full conversation context, runs in the background, and keeps its tool output out of your context"; 다른 타입은 컨텍스트 0 에서 시작. Agent 설명 본문은 원격 설정 `tengu_lucky_cerf_text` 로 교체 가능(기본 "A fresh agent costs more than it looks…").
- **결과 처리.** 아래 표. 핵심은 **영속화 흐름**(`chunk-x9y5y7kk.js`): 임계 초과 → `[CONFIG]/projects/[PROJECT]/tool-results/` 에 `writeExclusive`(심링크 거부) → 컨텍스트에는 `<persisted-output>` + `Output too large (${size}). Full output saved to: ${filepath}` + 미리보기 + `Use Read to view`. 저장 실패 시 "only the first ${n} are shown; the rest was dropped. If the tool can page or filter its results, call it again for the part you need." 비텍스트(이미지) 결과는 영속 불가. 텔레메트리 `tengu_tool_result_persisted{originalSizeBytes, persistedSizeBytes, estimatedOriginalTokens=ceil(bytes/4)}`.
- **읽기 중복 억제.** `"File unchanged since last read. The content from the earlier Read tool_result in this conversation is still current — refer to that instead of re-reading."`, `"Wasted call — file unchanged since your last Read."`, `Do NOT re-read a file you just edited to verify`, `When you already know which part of the file you need, only read that part.` WebFetch 는 self-cleaning 캐시.
- **캐시.** 시스템 프롬프트 본문 1블록에 `cache_control:{type:"ephemeral", ttl}` + 캐시 밖 `ephemeralSuffix`(안정 접두/가변 접미); 메시지는 마지막 user/assistant 의 마지막 블록만. TTL `{ttl:"5m",reason:"default"}` / 구독자 `"1h"` / `ENABLE_PROMPT_CACHING_1H`. 자동 모드 분류기 입력에도 `cache_control`.
- **컴팩션.** 자동 컴팩트 트리거 = 윈도 − `min(maxOutputTokens, 20000)`, 연속 실패 3회면 차단. **시간 기반 마이크로컴팩트**(`chunk-pretnsp4.js`): 지울 수 있는 결과 집합 `[Read, Grep, Glob, WebSearch, WebFetch, Edit, Write, …]`, 최근 `keepRecent=5` 제외, 절감 추정 < 20,000 tok 이면 스킵, 가능하면 영속 후 포인터로 대체. `<total_tokens>` 잔량 리마인더.
- **승인.** 모드 `["default","acceptEdits","plan","auto","bypassPermissions","dontAsk"]`. 규칙 `"Bash(npm run test)"` 정확 / `"Bash(git *)"` 접두 / `"Edit(docs/**)"`. "don't ask again" 버튼이 규칙을 만든다(`Yes, and don't ask again for ${name} commands in ${cwd}`). `auto` 분류기는 별도 API 호출(`querySource:"auto_mode"`, `stop_sequences:["</severity>"]`), 입력에 `user_claude_md` 를 넘기되 "Generic encouragement ('be autonomous', 'don't ask', 'I trust you') is not authorization". auto 모드에서는 시스템 프롬프트가 "Do your work through the Bash tool wherever it can…" 로 바뀜 — 분류기가 Bash 를 판정하므로 도구 수를 줄이는 쪽(추정). 훅: exit 2 차단, `async`/`asyncRewake`(백그라운드 실행 후 exit 2 면 모델을 깨움), `once`, `prompt` 훅에 `model` 지정.

| 항목 | 값 | 모듈 |
|---|---|---|
| Read 기본 줄 수 | 2000 (`y0t`) | chunk-pretnsp4.js |
| PDF | 20 pages/request, 10 페이지 초과 시 `pages` 필수 | chunk-pretnsp4.js |
| 이미지 | `maxWidth:2000,maxHeight:2000,maxBase64Size:5242880,targetRawSize:3932160`; 이미지 1개 = 2000 tok 추정(`_l`) | chunk-swcca8bf.js, chunk-pretnsp4.js |
| Bash 출력 | 기본 30,000자(`tAr`), env `BASH_MAX_OUTPUT_LENGTH` 최대 150,000; 설정 `bashOutputMaxChars` clamp [4,000, 128,000] | chunk-883nfgsn.js, chunk-ypef11tz.js |
| 도구별 `maxResultSizeChars` | 1e5 다수; 50,000 / 1e4 / 300,000 / `1/0` 도 있음 | chunk-705mhzj8.js 외 |
| 영속화 임계 | 기본 400,000자(`FGs`), `persistenceThresholdCeiling` 50,000(`UD`; Agent 결과 200,000); `min(maxResultSizeChars, ceiling)` | chunk-ypef11tz.js, chunk-x9y5y7kk.js |
| 영속 파일 상한 | 1 GiB (추정) | chunk-ypef11tz.js |
| 마이크로컴팩트 | 최소 절감 20,000 tok, `keepRecent` 5 | chunk-pretnsp4.js, chunk-h7kwn2ss.js |
| 자동 컴팩트 여유 / 회로차단 | 20,000 tok / 3회 | chunk-4jsg44k7.js |
| ToolSearch `max_results` | 5 | chunk-4jsg44k7.js |
| MCP 출력 | env `MAX_MCP_OUTPUT_TOKENS` (기본값 미발견) | chunk-3r7fz8m2.js |
| Grep | `output_mode` 기본 `files_with_matches`, `head_limit` | chunk-4jsg44k7.js |

못 찾은 것: `MAX_MCP_OUTPUT_TOKENS` 기본, Grep `head_limit` 기본, 서브에이전트 결과 요약 전용 코드, `task-notification` 본문 템플릿.

## 3. Codex `d42056091` — 소스가 말하는 것

경로는 `codex-rs/` 기준 ✅. **드리프트 재점검 2026-10-19 (`b1fd48c48`, 719 커밋, rust-v0.161–0.163):** 아래 표의 수치는
전부 같거나 행만 이동했고(`docs/99` §E.6 에 새 위치), 바뀐 것은 세 가지 — `executed_tool_call` 인자 캡(8 KiB/32 KiB) **제거**(#52268),
memories 에 바이트 상한 추가(`MAX_ROLLOUT_BYTES` 8 MiB, `MAX_RECORD_BYTES` 1 MiB, #53940), 메모리 확장 리소스 보존 7→14 일(#54033).
플래그 기본값 중 질문된 것(`code_mode` off, `code_mode_only` off, `code_mode_host` on, `tool_search` 항상 on, `unified_exec` on,
`model_catalog_in_context` off)은 그대로다. 새 레버 네 가지가 생겼다: `code_mode_tool_search`(off, `await tools.tool_search({query, limit: 8})`),
`async_compaction`(off, 턴 체크포인트에서 백그라운드 원격 컴팩션), `retain_client_tool_outputs`(off, `retain: true` 출력을 64,000 tok
예산 안에서 통째로 보존), `credential_masking`(off, 셸에는 플레이스홀더만 주고 프록시가 실제 자격증명 주입). 병렬 read-lock 경로가
스킬·메모리·이력 조회·dynamic 도구로 확대됐다(#52245, #54654).

- **카탈로그.** `core/src/tools/spec_plan.rs` 가 `ToolRegistry` 를 채우고 `build_model_visible_specs`(:554) 가 `exposure.is_direct()` 만 노출. 내장: `exec_command`/`write_stdin`(unified_exec), `apply_patch`, `view_image`, `update_plan`, `request_user_input`, `request_permissions`, `get_context_remaining`, `sleep`, `tool_search`, `spawn_agent`/`wait_agent`/`send_message`/`interrupt_agent`/`list_agents`, `list_mcp_resources` 계열. 거의 전부 `Feature::*` 게이트(예 `Feature::UnifiedExec` 없으면 `ExecCommandHandler::one_shot`, :1108-1116). 노출 6변형 `ToolExposure { Direct, DirectModelOnly, Deferred, DeferredModelOnly, CodeModeOnly, Hidden }`(`tools/src/tool_executor.rs:51-80`; `is_direct()` = `Direct | DirectModelOnly`, `is_deferred()` = `Deferred | DeferredModelOnly` — 2026-10-19 재점검에서 "4단계"를 정정). **`mcp_tool_exposure.rs:85-89`**: 검색 도구가 켜지면 MCP 도구는 전부 `Deferred`; agent-plugin MCP 스펙은 `MAX_AGENT_PLUGIN_MCP_SPEC_BYTES = 8_000`, 총 `64_000` 초과 시 `Hidden`; 서버별 `tool_input_schema_max_bytes`. `tool_search` 는 BM25("Searches over deferred tool metadata with BM25 and exposes matching tools for the next model call", `tool_search_spec.rs:94`), 기본 반환 `TOOL_SEARCH_DEFAULT_LIMIT = 8`, 플래그는 제거되어 **항상 on**(`features/src/lib.rs:241-244`), 실제 조건은 기준 커밋에서 `model_info.supports_search_tool && namespace_tools_enabled` — **드리프트(10-19)**: #50447 로 `namespace_tools` 능력 게이트가 삭제되어 `supports_search_tool && tool_policy.allows && (deferred 도구 ≥ 1)` (`spec_plan.rs:392-397`).
- **Code mode** (`code-mode-protocol/src/description.rs:20-25`): "Run JavaScript code to orchestrate/compose tool calls — Evaluates the provided JavaScript code in a fresh V8 isolate as an async module. All nested tools are available on the global `tools` object, for example `await tools.exec_command(...)` … Runs raw JavaScript -- no Node, no file system, no network access, no console." `ToolSpec::Freeform` + lark 문법, 첫 줄 `// @exec: {"yield_time_ms": 10000, "max_output_tokens": 1000}`, 헬퍼 `text()/image()/store()/load()/notify()/yield_control()/exit()`, `ALL_TOOLS`. 비동기 셀: `yield_time_ms` 뒤 "Script running with cell ID …" 를 돌려주고 `wait` 로 이어받음; 기본 `DEFAULT_EXEC_YIELD_TIME_MS = 10_000`, `DEFAULT_MAX_OUTPUT_TOKENS_PER_EXEC_CALL = 10_000`(`runtime.rs:15-17`), 중첩 스키마 TS 렌더 `16_000` B. `ToolMode::CodeModeOnly` 면 중첩 가능 도구가 최상위에서 숨음(`spec_plan.rs:794-806`). 호스트는 별도 바이너리(`codex-code-mode-host`, `stdio`/`grpc://`), 없으면 "Falling back to direct tools / Code mode will fail closed". 플래그: `code_mode` 기본 off, `code_mode_host` on, `code_mode_only` off. 절약 대상은 추정: 왕복(여러 호출+가공을 한 턴), 토큰(중간 결과 비노출, `store/load` 로 모델 우회), 스키마 토큰.
- **호출 루프.** `parallel_tool_calls: prompt.parallel_tool_calls && !model_info.use_responses_lite`(`client.rs:1001`); 실행은 `supports_parallel ? lock.read() : lock.write()`(`tools/parallel.rs:205-209`); 병렬 허용: `exec_command`, `write_stdin`, `view_image`, `tool_search`, MCP read-only 어노테이션. **unified_exec** 가 기본(PTY 세션 재사용): yield 250–30,000 ms, 빈 stdin 폴링 ≥5,000 ms, 백그라운드 300,000 ms, 동시 64 프로세스(`unified_exec/mod.rs:73-82`); 설계 메모 "on sandbox denial, retries without sandbox when policy allows (no re-prompt thanks to caching)". 서브에이전트 `wait_agent` 30,000 ms. `Feature::ShellSnapshot` 기본 on — 로그인 셸 환경 3일 캐시.
- **결과 처리.** 수집 하드캡 `EXEC_OUTPUT_MAX_BYTES = 1 MiB`("so a single runaway command cannot OOM the process"), 모델 전달은 `format_exec_output_for_model`(`Exit code / Wall time / Total output lines / Output:`) + `truncate_text`; 정책은 모델 카탈로그 `"mode":"tokens","limit":10000`(폴백 bytes 10,000), 설정 `tool_output_token_limit`; `APPROX_BYTES_PER_TOKEN = 4`. unified_exec 는 `HeadTailBuffer` 50:50, `"... {omitted_bytes} bytes omitted ..."`, 응답에 `original_token_count`. `thread_rollout_truncation.rs` 는 토큰 절약이 아니라 **포크/롤백 경계 절단**. 이미지 1장 ≈ 7,373 B ≈ 1,844 tok 추정(`history.rs:1048`). apply_patch 성공 결과 `"Success. Updated the following files:"` + `A/M/D path`. file-search 기본 20. 거부 메시지 900 tok 캡.
- **컨텍스트 경제.** `prompt_cache_key` = 세션 ID, 내부 서브에이전트 `"{source}:{parent_thread_id}"`(`client.rs:581-593`); 요청 속성이 같을 때만 WebSocket `previous_response_id` 증분 재사용; 프리웜 `response.create` + `generate=false`. 컴팩션: `context_window × 95 %`, 턴 종료 `model_post_turn_compact_threshold_percent`, 범위 `Total | BodyAfterPrefix`; 사용자 메시지 보존 20,000 tok, 원격 v2 64,000. `get_context_remaining` 도구(`Feature::TokenBudget`). AGENTS.md 류 프로젝트 문서는 **바이트** 상한 `DEFAULT_PROJECT_DOC_MAX_BYTES = 32 * 1024`(`config/src/config_toml.rs:75`; 처음 적었던 "10,000 tok" 은 스킬 메타데이터 예산 `MAX_CONFIGURED_SKILL_METADATA_TOKEN_BUDGET`, `ext/skills/src/render.rs:20` 으로 보임 — 추정, 10-19 정정). `memories`: 롤아웃 150,000 tok·툴 출력 2,000 tok 로 잘라 요약.
- **승인.** `AskForApproval { UnlessTrusted, OnRequest(기본), Granular{…}, Never }`; Granular 의 false 항목은 "automatically rejected instead of shown to the user". 순서 "1. Hooks 2. Guardian(StrictAutoReview 시) else user"(`approvals.rs:505-507`), 그 앞에 세션 캐시 `with_cached_approval`(키: `environment_id, executable, canonical command, cwd, tty, sandbox_permissions`), execpolicy Starlark `prefix_rule(decision=allow|prompt|forbidden)` + 승인 시 `ApprovedExecpolicyAmendment` 영구 추가. 샌드박스 거부는 출력 포함 그대로 모델로, 사용자 거부는 `"exec command rejected by user"` 정규화.
- **기타.** 전송 메시지 15 MiB 초과 시 `executed_tool_calls` 메타만 셰딩("Only the wire copy changes"); MCP 핸들러·검색 인덱스 캐시; `immutable_spec`. 같은 호출 반복 시 결과 재사용(dedupe) 은 **없음**.

| 항목 | 값 | 위치 |
|---|---|---|
| exec 수집 캡 | 1 MiB | `utils/pty/src/lib.rs:25` |
| 모델 전달 툴 출력 | 10,000 tok (신형) / 10,000 B 폴백 | `models-manager/models.json`, `model_info.rs:127` |
| unified_exec yield / 백그라운드 / 동시 | 250–30,000 ms / 300,000 ms / 64 | `unified_exec/mod.rs:73-82` |
| one-shot 타임아웃 | 10,000 ms | `exec.rs:63` |
| tool_search 기본 | 8 | `tools/src/tool_discovery.rs:7` |
| agent-plugin MCP 스펙 | 8,000 / 64,000 B | `mcp_tool_exposure.rs:18-19` |
| code-mode yield / wait / 출력 | 10,000 ms / 10,000 ms / 10,000 tok | `code-mode-protocol/src/runtime.rs:15-17` |
| 거부 메시지 | 900 tok | `tools/events.rs:39` |
| 유효 윈도 / 컴팩션 보존 | 95 % / 20,000 tok (원격 64,000) | `models-manager/src/model_info.rs:133` (처음 적은 `openai_models.rs:1093` 은 존재하지 않는 파일 — 정정), `compact.rs:55` |
| 이미지 추정 | 7,373 B ≈ 1,844 tok | `context_manager/history.rs:1048` |
| 전송 소프트캡 | 15 MiB | `client_tool_metadata.rs:10` |

## 4. Strands `a9a62d4e` — SDK 가 기본값으로 정한 것

> 드리프트 재점검 2026-10-19 (`bd0b6a94`, 176 커밋, python 1.61.1 / ts 1.21.0 / harness 0.3.1): 아래 수치는 전부 같다. 바뀐 것은 경로 — 하네스의 ContextOffloader 배선 제거(#4701), 실행기 재작성(#4976 미들웨어 공개, `Input → Wrap → Output`, `MiddlewareInterruptResult` 라는 네 번째 승인 채널 ⚠️), 분류기·steering 의 모델이 `aux_model` 우선. SDK 에 vended `subagent`·`python_repl`·`swarm` 이 생겼으나 하네스 built-in 8개는 그대로. `strands/99` §6.2.

- **스펙.** `ToolSpec = {name, description, inputSchema{json}, outputSchema?, annotations}`(`types/tools.py:30-42`); `@tool` 이 docstring+타입힌트로 생성(`tools/decorator.py`). 레지스트리가 설명 없는 프로퍼티에 `"Property {name}"`, 타입 없으면 `"string"` 을 **강제 삽입**해 크기를 키움(`registry.py:605-624`). 하네스 built-in 8개(`shell, read, write, edit, web_fetch, web_search, programmatic_tool_caller, subagent`), `read` 는 "Text defaults to the first 2000 lines; use offset/limit".
- **실행기.** 기본 `ConcurrentToolExecutor()`(py `agent.py:534`, ts `agent.ts:360-362`): 도구마다 task, 이벤트 큐 직렬화, 결과는 **원래 순서**. Sequential 은 `ToolInterruptEvent` 시 나머지 미실행. 취소 시 `"Tool execution cancelled"` 합성.
- **결과.** `ToolResult{toolUseId, status, content[text|json|image|document]}`; **실행 시점 절단 없음**(grep 0). 절단은 후처리: ContextOffloader 플러그인 2,500 tok 초과 → 디스크 + 미리보기 1,000 tok + `retrieve_context(pattern, line_range)`(최대 10,000); 하네스 `"auto"` 는 1,500/750 — **드리프트(10-19, #4701)**: 하네스는 더 이상 ContextOffloader 를 쓰지 않고 SDK `ContextManager()` 기본(`_AUTO_TRUNCATE_THRESHOLD = 1_500`, `_TRUNCATE_PREVIEW_TOKENS = 750`, `_AUTO_SUMMARIZE_UTILIZATION = 0.85`, `strands-py/_context_manager/context_manager.py:30-33`)으로만 동작, 세션 없으면 stash 가 메모리에 남음; 프리셋 `stale_tool_cleanup`(최근 5개 밖 drop), `proactive_summarization`(70 %); SlidingWindow 40, 오버플로 시 앞뒤 200자만 남기고 `[truncated: N chars removed]`; Summarizing 0.3·최근 10 보존. `programmatic_tool_caller`: `print()` 한 것만 모델로, 200,000자, 내부 동시 10, 60 s CPU/256 MB. `shell` 은 `timeout=120` 만 있고 바이트 상한 **없음**.
- **훅.** `BeforeToolCallEvent(cancel_tool, selected_tool, tool_use)` → 미들웨어 → `AfterToolCallEvent(result, retry=True)`; 취소는 terminal.
- **승인.** `HumanInTheLoop(allowed_tools=["*","!delete_file"], enable_trust=True)` — "trust responses approve the tool AND remember it in `agent.state`"; `classifier=True` 는 내부 LLM 위험 분류기; Cedar 는 동기 `Proceed/Deny`.
- **캐시.** `DEFAULT_CACHING="auto"`; Bedrock `toolConfig.tools` 끝 `cachePoint`; Anthropic 은 메시지 캐시포인트 **1개만** 유지하고 마지막 user 로 이동("so they cannot accumulate one per turn", `anthropic.py:408-460`).
- **서브에이전트 입력.** `context="none"`(기본) 과제 문자열만 / `"all"` 부모 메시지 복사(미응답 toolUse·reasoning 제거, 트림 경계는 tool pair 보존) / `"no_tools"`; 반환은 **최종 메시지 텍스트만**("Your final message is the only thing that returns to the parent"). Swarm `max_handoffs=20`, Graph 는 의존 노드 결과를 요약 없이 연결. 깊이 `DEFAULT_SUBAGENT_MAX_DEPTH = 2`.

## 5. Gemini CLI 0.42.0 과 opencode 1.17.12 — 번들에서 읽은 것

`7VV` = `bundle/chunk-7VVHSNDQ.js`, `JEW` = `bundle/chunk-JEW7ZIWE.js`; opencode 는 분리 모듈의 청크명. 상수명은 난독화된 지역명.

### 5.1 Gemini CLI

- **카탈로그.** 내장 도구는 **모델 패밀리별 선언 세트**: `coreTools.js` `getToolSet(modelId)` → `"gemini-3"` 면 `GEMINI_3_SET`, 아니면 `DEFAULT_LEGACY_SET`(JEW:50409~). 키 `read_file, write_file, grep_search, grep_search_ripgrep, glob, list_directory, run_shell_command, replace, google_web_search, web_fetch, read_many_files, save_memory, write_todos, get_internal_docs, ask_user, enter_plan_mode, exit_plan_mode, activate_skill, read_mcp_resource, list_mcp_resources`. 같은 도구라도 모델별 description 이 다르다(gemini-3 의 `read_file`: "To maintain context efficiency, you MUST use 'start_line' and 'end_line' for targeted, surgical reads"). 모든 선언에 `wait_for_previous: boolean` 자동 주입(`addWaitForPreviousParameter`, JEW:41426). `ToolRegistry.getFunctionDeclarations(modelId)`(7VV:274644) 가 `mainAgentTools` 화이트리스트 필터, MCP 는 `mcp_` 접두, Plan 모드면 `write_file/replace` 설명을 `ONLY FOR PLANS: …` 로 덮어씀. 동적 발견 `toolDiscoveryCommand` stdout JSON + MCP 서버 `Promise.all` 병렬 연결, `MCP_DEFAULT_TIMEOUT_MSEC = 10*60*1e3`. **툴 검색/지연 노출 없음**(문자열 미발견); 노출 제어는 `excludeTools` 와 `mainAgentTools` 뿐.
- **호출 루프.** `Scheduler`(7VV:307462) 가 한 턴의 호출을 큐잉, `_isParallelizable` = `args.wait_for_previous !== true` 인 호출을 연속 dequeue 해 `Promise.all(…_processValidatingCall)` → `Promise.all(…_execute)` 로 **검증·승인·실행 모두 병렬**. 시스템 프롬프트 "Tools execute in parallel by default… Do NOT make multiple calls to the replace tool for the SAME file in a single turn"(7VV:294428). 셸 `is_background` → "Command moved to background (PID: …). Output hidden." 서브에이전트 `AgentTool`(7VV:312061) → `LocalAgentExecutor`: 자식은 **새 `ToolRegistry`**(`toolConfig.tools` 로 선별), 부모 히스토리 없이 `query` 문자열만("The COMPLETE query… Include all context"); `codebase_investigator`(LS/READ_FILE/GLOB/GREP, `maxTurns 50`, JSON 보고서), `generalist`(전체, 20), 기본 `DEFAULT_MAX_TURNS = 30`; `complete_task` 미호출 시 `ERROR_NO_COMPLETE_TASK_CALL`.
- **결과 처리 — 두 경로.** (a) 기본(`contextManagement.enabled ?? false`): `ToolExecutor.truncateOutputIfNeeded` 는 **셸 또는 MCP 단일 텍스트 파트만** 대상, `DEFAULT_TRUNCATE_TOOL_OUTPUT_THRESHOLD = 4e4` 자 초과 시 `<projectTemp>/tool-outputs/session-<id>/<tool>_<callId>.txt` 저장 + **head 20 % / tail 80 %** + "Output too large. Showing first … and last … characters. For full output see: <path>". (b) context management 켜면 `ToolOutputDistillationService.distill`: `read_file`/`read_many_files` 면제, `maxOutputTokens(1e4)*4` 자 초과 시 저장+구조 보존 절단, `summarizationThresholdTokens(2e4)*4` ~ `MAX_DISTILLATION_SIZE = 1e6` 구간은 **보조 LLM 호출로 "Strategic Significance of Truncated Content" 요약**을 덧붙임. `read_file` 2,000줄·줄당 2,000자, 잘리면 "use start_line: <end+1>" 안내; 이미지/오디오/PDF 는 `inlineData`. `grep_search` 총 100 매치. `replace` 결과는 "Successfully modified file: … (N replacements)" + 앞뒤 5줄 스니펫(`getDiffContextSnippet`). 셸 LLM 요약은 설정 `summarizeToolOutput[run_shell_command]` 있을 때만(`maxOutputTokens ?? 2e3`).
- **컨텍스트 경제.** 명시적 캐시 breakpoint 없음 — `cachedContent` 패스와 `cachedContentTokenCount` 텔레메트리만(**암묵 캐시 의존, 추정**). 압축 `ChatCompressionService.compress`(7VV:296570): `DEFAULT_COMPRESSION_TOKEN_THRESHOLD = 0.5`×tokenLimit 미만이면 스킵; ① `truncateHistoryToBudget` — 최근부터 functionResponse 토큰 합산, `COMPRESSION_FUNCTION_RESPONSE_TOKEN_BUDGET = 5e4` 초과분 저장+4e4 자 절단(그것만으로 줄면 `CONTENT_TRUNCATED` 종료) ② `findCompressSplitPoint(…, 1-0.3)` user 턴 경계 분할 후 앞부분을 보조 모델(`chat-compression-*`)로 요약, 요약이 더 크면 `COMPRESSION_FAILED_INFLATED_TOKEN_COUNT`. 마스킹 `ToolOutputMaskingService.mask`(7VV:303826): 최신 턴 제외 뒤에서부터 누적, `protectionThresholdTokens 5e4` 초과분이 prunable, 합이 `minPrunableThresholdTokens 3e4` 이상일 때만 파일 저장+`<tool_output_masked>`; 면제 `activate_skill, save_memory, ask_user, enter/exit_plan_mode`. 루프 감지 `TOOL_CALL_LOOP_THRESHOLD 5`, `CONTENT_LOOP_THRESHOLD 10`, LLM 검사 20/10, 감지 시 "System: Potential loop detected…" 주입; `MAX_TURNS 100`. 토큰 추정 `JSON.stringify(value).length/4`.
- **승인.** `ApprovalMode = default | autoEdit | yolo | plan`. `PolicyEngine`(7VV:320113): 규칙 `priority` 내림차순 매칭(`toolName`, `commandPrefix`, `argsPattern`, MCP `serverName`); 비대화형 기본 `DENY`, 대화형 `ASK_USER`. YOLO 도 DENY 규칙 유지, 위험 셸은 `applyShellHeuristics` 가 ASK 강제, `isKnownSafeCommand` 면 ASK→ALLOW, 리다이렉트 포함은 ALLOW→ASK. `ProceedAlways` 가 **세션 규칙**(exec 는 `rootCommands`→`commandPrefix`, edit 는 경로 `argsPattern`)을 추가, `ProceedAlwaysAndSave` 는 workspace/user 영구화, MCP 는 `ProceedAlwaysServer/Tool`. 거부: 정책 DENY → `"Tool execution denied by policy.<denyMessage>"`(`POLICY_VIOLATION`) functionResponse; 사용자 취소 → `"User denied execution."` + **큐 전체 취소**(`cancelAllQueued`); 비대화형에서 ASK 는 예외. 시스템 프롬프트 "Confirmation Protocol: If a tool call is declined or cancelled, respect the decision immediately. Do not re-attempt"; 훅이 `"ask"` 를 돌려주면 정책 결과를 ASK 로 덮어씀.
- **기타.** `wait_for_previous` 로 모델이 의존성을 직접 표기(스케줄러 힌트). LSP 없음(`textDocument/` 0). 파일 중복 읽기 억제 미발견.

| 항목 | 값 | 파일 |
|---|---|---|
| 셸/MCP 절단 임계 | 4e4 chars (head 20 %) | 7VV:335436, 237271 |
| distillation 출력 / 요약 임계 / 상한 | 1e4 / 2e4 tok / 1e6 chars | 7VV:335865, 306993 |
| 마스킹 보호 / 최소 prune | 5e4 / 3e4 tok | 7VV:303812 |
| read_file 줄 / 줄길이 | 2e3 / 2e3 | JEW:49818 |
| grep 총 매치 | 100 | 7VV:282542 |
| 압축 트리거 / 보존 / functionResponse 예산 | 0.5×limit / 0.3 / 5e4 | 7VV:296463-5 |
| 루프 임계 | tool 5, content 10, LLM 검사 20/10 | 7VV:303026 |
| 서브에이전트 maxTurns | 30 / investigator 50 / generalist 20 | 7VV:296749, 295660, 300196 |
| MCP 타임아웃 | 600,000 ms | 7VV:326048 |
| historyWindow max / retained (contextManagement) | 15e4 / 4e4 tok | 7VV |

### 5.2 opencode

- **카탈로그.** `ToolRegistry.state`(chunk-pggd0f5s.js) 가 순서를 고정: `[invalid, (question), bash, read, glob, grep, edit, write, task, webfetch, todowrite, websearch, skill, apply_patch, (lsp), (plan)]` — `question` 은 `client ∈ {app,cli,desktop}`, `lsp` 는 `OPENCODE_EXPERIMENTAL_LSP_TOOL`, `plan` 은 `experimentalPlanMode && client==="cli"`. `invalid` 는 잘못된 호출을 받아내는 싱크 도구. 스키마는 Effect `Schema.Struct` + `annotate({description})` → `jsonSchema`; 커스텀 도구 `{tool,tools}/*.{js,ts}` 스캔 + 플러그인; `Tool.execute` 래퍼가 공통으로 `Truncate.output` 적용. `task` 설명에 `describeTask` 가 "Available agent types and the tools they have access to:" 를 동적으로 붙임. 툴 검색/지연 노출 없음; `batch` 도구 0건.
- **호출 루프.** 도구는 AI SDK 형식 `{description, inputSchema, execute}`(chunk-f6y47634.js: `"tool.execute.before" → execute → "tool.execute.after"`), `SessionProcessor` 는 스트림 이벤트로 파트 상태만 갱신. **자체 스케줄러 없음 — 병렬성은 AI SDK 의 즉시 실행에 의존(추정)**; 턴 종료 시 `forEach(toolcalls, await done, {concurrency:"unbounded"})`. 의존성 힌트 없음. 서브에이전트 `task`: `{description, prompt, subagent_type, task_id?, background?}` → **새 세션**, `prompt` 만 전달, 결과는 마지막 텍스트를 `<task id state><task_result>…</task_result></task>` 로 래핑, `task_id` 로 재개; 자식 권한은 부모 ruleset 병합 + `todowrite` deny; 백그라운드는 `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true`, 완료 시 `injectBackgroundResult`("DO NOT sleep, poll for progress…"). 셸 백그라운드 플래그 없음, `bashDefaultTimeoutMs ?? 120000`.
- **결과 처리.** 공통 `Truncate.output`(chunk-3w4319fg.js): `maxLines 2000`, `maxBytes 51200`(설정 `tool_output.max_lines/max_bytes`), head/tail 방향; 초과 시 `<data>/tool-output/tool_<id>` 저장(7일 보관) 후 — task 허용 시 "Full output saved to: … Use the Task tool to have explore agent process this file with Grep and Read (with offset/limit). **Do NOT read the full file yourself - delegate to save context.**", 불허 시 "Use Grep to search the full content or Read with offset/limit". bash 수집 상한 `maxBytes*2`, 메타 30,000자 head/tail, 타임아웃 시 "retry with a larger timeout value". read: `limit` 2,000줄, 줄당 2,000자(`… (line truncated to 2000 chars)`), 누적 51,200 B 에서 `ReadStop` — "(Output capped at 50 KB. Showing lines a-b. Use offset=N to continue.)"; 이미지·PDF 는 `attachments:[{type:"file", mime, url:"data:…"}]`, 바이너리는 "Cannot read binary file". glob/grep 각 100. **edit 결과는 "Edit applied successfully." 뿐**, diff 는 `metadata.diff/filediff` 로 UI 전용 분리, 저장 후 **LSP 진단을 조회해 "LSP errors detected in this file, please fix:" 를 덧붙임**. webfetch 5,242,880 B 상한, 타임아웃 30,000(최대 120,000) ms, HTML→markdown.
- **컨텍스트 경제.** `LLM.CacheHint`(chunk-77wnt84w.js) 기본 `{tools: true, system: true, messages: "latest-user-message"}`, 대상 `{"anthropic-messages","bedrock-converse"}`; 마지막 도구·마지막 시스템 파트·최신 user 의 마지막 content 에 `{type:"ephemeral", ttlSeconds?}`; Bedrock `BEDROCK_BREAKPOINT_CAP = 4`. 오버플로 `tokens.total ≥ limit.input ?? (limit.context − reserved)`, `reserved = compaction.reserved ?? min(20000, maxOutputTokens)`; 압축 시 `preserve_recent_tokens ?? min(8000, max(2000, floor(limit*0.25)))` 를 tail 로 보존하고 앞을 요약(요약 입력의 도구 출력 2,000자 cap, `stripMedia`). 프루닝 `SessionCompaction.prune`: 완료 tool 파트를 최신부터 누적, 40,000 tok 보호, 초과 합 20,000 넘으면 `"[Old tool result content cleared]"` 치환+첨부 제거, 면제 `["skill"]`. **지시문 중복 억제**: read 결과 `metadata.loaded` 에 경로까지의 `AGENTS.md`(+`CLAUDE.md`) 목록을 기록하고 `Instruction.resolve` 가 이미 주입한 파일은 재삽입하지 않음.
- **승인.** `ask | allow | deny`, 규칙 `{permission, pattern, action}` 을 **`findLast` 로 마지막 매칭 우선**, 기본 `{action:"ask", pattern:"*"}`; `edit/write/apply_patch` 는 `"edit"`, MCP 리소스는 `"read"` 로 묶음. `Permission.ask`(chunk-nvnbhxab.js): deny 즉시 `DeniedError`, allow 통과, 나머지만 질의; `always` 응답은 세션 `approved` 에 push 하고 **대기 중인 다른 요청도 재평가해 자동 승인**. bash 는 `ShellTool.collect` 가 트리시터로 명령 루트별 `"<prefix> *"` 패턴과 `external_directory` 생성. 거부 텍스트: `PermissionRejectedError` "The user rejected permission to use this specific tool call.", `PermissionCorrectedError` "…with the following feedback: ${feedback}", `PermissionDeniedError` "The user has specified a rule … Here are some of the relevant rules ${JSON.stringify(ruleset)}". doom loop: 동일 도구·동일 입력 연속 3회면 `permission:"doom_loop"` 확인 요구.
- **기타.** 결과의 `attachments`/`metadata`(diff, diagnostics) 를 모델용 `output` 과 분리해 UI 데이터가 토큰을 쓰지 않게 함; 요약 생성 중 도구 호출 금지.

| 항목 | 값 | 파일 |
|---|---|---|
| 공통 절단 maxLines / maxBytes / 보관 | 2000 / 51200 / 7 days | chunk-3w4319fg.js |
| read limit / 줄길이 / 바이트 cap | 2000 / 2000 / 51200 | chunk-pggd0f5s.js |
| glob / grep | 100 / 100 | chunk-pggd0f5s.js |
| bash timeout / 메타 절단 | 120,000 ms / 30,000 chars | chunk-pggd0f5s.js |
| webfetch 크기 / timeout | 5,242,880 B / 30,000·120,000 ms | chunk-pggd0f5s.js |
| compaction reserved / preserve_recent | 20,000 / min(8000, max(2000, 25 %)) | chunk-f6y47634.js |
| prune 보호 / 최소 prune | 40,000 / 20,000 tok | chunk-f6y47634.js |
| 압축 요약 입력 도구출력 cap | 2,000 chars | chunk-f6y47634.js |
| doom loop | 3 | chunk-f6y47634.js |
| 캐시 breakpoint / Bedrock cap | tools+system+latest-user / 4 | chunk-77wnt84w.js |

못 찾은 것: Gemini 의 툴 검색·LSP·중복 읽기 억제·명시적 캐시 breakpoint; opencode 의 `batch` 도구·자체 병렬 스케줄러.

## 6. REA 6.7.0 — 도구 *서버* 쪽에서 본 토큰 설계

규칙 → 출처 → 절약 대상 ✅.

- "Return the smallest sufficient answer with necessary provenance, coverage and limitations … Count the whole task, including schemas, extra calls and retries." → `AGENTS.md` §Performance → 응답 토큰과 후속 호출. 최적화 순서 1 토큰 → 2 분석 시간 → 3 CPU/메모리.
- **Evidence ID 참조** `{"kind":"retained-evidence","evidence_id":"ev_<64 hex>"}` — "No additional lookup call, provider selection, or approval step is required for a same-session follow-up." → `docs/mcp-contracts.md` §Retained application Evidence inputs → 큰 결과 재전송.
- **요약 우선** `detail: "summary"` + `inspect_analysis_view` 투영; 문서의 예 "Electron Framework: 2.5 MB of imports and exports, 3.3 KB as a summary" → 첫 응답 ~1000×.
- **페이징** `offset`/`limit` 기본 0/64, `next_offset`(null 까지), `total` 별도, UTF-16 단위로 서로게이트 보존 → 프레임 상한.
- **예산 초과 시 참조+continuation**: 10 MiB 수신 버퍼 초과 → `resource_constraint` + `details.reported_limits.evidence_reference`, 네이티브는 `details.reported_limits.continuation` 에 "ready-to-call `inspect_analysis_view` request" → 재시도 왕복 1회.
- **타임아웃/취소 시 부분 결과** `details.partial_observation`(이 노트의 gemini 첫 실행이 실제로 그 경로를 탔다) → 전체 재실행.
- **진행 알림** 토큰 요청 시만, 100 ms 레이트 제한, "REA does not fabricate percentages".
- **CLI 토큰 창** `--token-limit/--token-offset/--token-count`(`src/cli/cliResultOutput.ts:357-375`, `[truncated: showing tokens a–b of total]`, `meta.nextOffset`), `--filter-output evidence_id,normalized_result.statistics`; 구조화 출력엔 토큰 창 대신 필터/페이징.
- **스키마 예시에 완전 증거 금지**; **compact 입력 스키마 프로파일** `REA_MCP_INPUT_SCHEMA_PROFILE=compact`: 도구당 13,312 B 예산(Moonshot 관측 "13.7 KB accepted, ~15 KB rejected"), 중첩 설명·예시·기본값·title 제거, `$ref` 인라인; 출력 스키마 `off` 가능 → 카탈로그: 172 tools, `full` ≈496 KB(≈120k o200k tok) → `compact` ≈290 KB(≈68k) (`docs/client-configuration.md:109-117`).
- **오류도 구조화·경계**: `isError:true` + JSON, "Oversized errors are retained as Evidence before delivery of a bounded diagnostic".
- **권한 플래그 없음**: "REA does not require permission grants or per-call approval flags"; `readOnlyHint`/`destructiveHint` 는 힌트.
- **한도는 실제 제약에서만**: `docs/tool-design.md` "An assumed agent budget is insufficient justification for a limit." / "Keep the catalog complete; report capability/session availability instead of truncating schemas."

## 7. 교차 독해 — 여섯이 합의한 것과 갈린 것

**합의(독립적으로 같은 답에 도달한 것):**
1. **큰 결과는 컨텍스트 밖에 두고 포인터를 남긴다.** Claude Code `<persisted-output>`+`Use Read to view`, Strands 오프로드+`retrieve_context`, REA Evidence ID+`inspect_analysis_view`. Codex 만 "잘렸다"는 신호(`original_token_count`)로 끝낸다 — 대신 code mode 로 중간 결과를 모델 밖에서 가공.
2. **바이트/토큰 ≈ 4** 를 세 곳이 쓴다(Claude Code `UWe=4`, Codex `APPROX_BYTES_PER_TOKEN = 4`, REA 는 tokenx 추정).
3. **MCP 도구는 기본 지연 노출**(Claude Code `isMcp → deferred`, Codex "MCP tools are always deferred when tool_search is available") + 검색 도구(키워드 5 / BM25 8).
4. **캐시포인트는 적게, 고정 위치에**: Claude Code 시스템 1 + 마지막 메시지 1, Strands Anthropic 1개 이동, Codex 세션 키 + `previous_response_id`.
5. **승인은 기억한다**: 세션 승인 캐시(Codex 키 6개), 규칙 생성 버튼(Claude Code), `enable_trust`(Strands). 분류기(Claude `auto`, Codex Guardian, Strands `classifier`) 는 사람 왕복을 **모델 호출 1회**로 바꾸고, 두 데스크탑 UI 는 그 비용을 문장으로 알린다(`harness-artifacts/02` §3.3).

**갈린 것:**
- 절단 단위: Claude Code 는 **문자**(30,000), Codex 는 **토큰**(10,000, 모델별 카탈로그 값), Strands 는 **토큰**(1,500~2,500) 후처리, REA 는 **바이트**(10 MiB) + 토큰 창은 CLI 표시용.
- 절단 위치: Codex head/tail 50:50, Strands 앞뒤 200자, Claude Code 앞부분 미리보기.
- 병렬의 주체: Claude Code 는 프롬프트 지시, Codex 는 API 플래그 + 핸들러별 선언 + RwLock, Strands 는 실행기 기본값. 코드 오케스트레이션은 Codex(code mode) 와 Strands(`programmatic_tool_caller`) 만 1급 도구.
- 서브에이전트 컨텍스트: Claude Code fork 는 전체 상속, Strands 기본 `none`, Codex 는 부모 캐시 키 공유. 반환은 셋 다 **최종 텍스트만**.
- 한도의 근거: REA 만 "가정된 예산은 한도의 근거가 못 된다"를 규칙으로 적었다. 나머지는 상수다.

## 8. 검증 가능한 채택 후보

각 항목은 "무엇을 → 누가 그렇게 하나 → 어떻게 확인하나"다. 측정되기 전까지 효과는 ⚠️.

1. **결과 ID + 미리보기 + 재조회 도구.** 임계(Strands 하네스 1,500 tok / Claude Code 도구별 1e5자) 초과 결과는 디스크에, 컨텍스트에는 `result_id` + 미리보기(750 tok). 확인: 10 KB Read 뒤 컨텍스트 증가 ≤ 미리보기+참조.
2. **모든 built-in 에 `offset/limit/next_offset/total`** (REA 0/64, Strands/Claude Read 2,000줄). Grep·Bash 출력에도 같은 계약. 확인: 5,000 매치 grep 이 1페이지 + `next_offset` 로 끝남.
3. **절단 응답에 바로 호출 가능한 continuation** (REA `details.reported_limits.continuation`). 확인: 절단 응답만 보고 다음 페이지를 추가 추론 없이 호출.
4. **summary-first 플래그** (`detail:"summary"`): 테스트 러너·빌드 결과는 실패 수·마지막 N줄·전체 참조. 확인: 10 MB 로그 → ≤2 KB.
5. **스키마 예산을 CI 에 고정** (REA 13,312 B/도구; Codex agent-plugin 8,000/64,000 B). Strands 식 `Property x` 자동 삽입 금지. 확인: `tools/list` 직렬화 크기 회귀 테스트.
6. **지연 노출 + 검색** (Claude Code `select:`/키워드 5, Codex BM25 8): MCP 는 기본 deferred, 프롬프트에는 이름+한 줄. 확인: deferred 로 아낀 토큰을 Claude Code 처럼 세어 로그.
7. **타임아웃/취소 시 부분 출력 보존** (REA `partial_observation`, Codex unified_exec 의 yield 후 이어받기). 확인: `sleep 999; echo` 타임아웃 → 선행 stdout 유지 + `partial:true`.
8. **턴 내 병렬 + 코드 오케스트레이션** (Strands Concurrent 기본, Codex code mode / Strands `programmatic_tool_caller`): 독립 호출은 병렬, 루프·필터는 "print 한 것만 모델로". 확인: 50 파일 grep→filter→read 가 모델 왕복 1회.
9. **캐시포인트 1~2개, 고정 위치** + 도구 정의 캐시. 확인: 연속 턴 `cache_read_input_tokens` ≥ 시스템+도구 정의.
10. **읽기 중복 억제 문구** (Claude Code "File unchanged since last read… refer to that instead"). 확인: 같은 파일 2회 Read 시 두 번째는 포인터만.
11. **승인 기억 + 규칙 생성 버튼** (Codex 세션 캐시 키, Claude Code "don't ask again", Strands `enable_trust`). 확인: 같은 명령 2회 중 승인 왕복 1회.
12. **한도는 측정으로만 바꾼다** (REA): cold/warm 분리, 토큰·시간을 함께 보고. "Fewer bytes alone do not establish fewer tokens."

못 찾은 것(전체): Claude Code `MAX_MCP_OUTPUT_TOKENS` 기본값, Strands `shell` 출력 상한, REA 소스의 도구 수 상수(172 는 문서 측정치), Codex 의 결과 dedupe(없음).
