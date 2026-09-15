# 04. `codex exec` — 비대화형 모드

스크립트와 CI/CD에서 터미널 UI 없이 Codex를 돌리는 모드.
"단일 명령으로 끝까지 실행하고, 구조화된 출력을 스트리밍하고, 성공/실패 신호로 종료"하는 용도에 맞습니다.

## 설치

```bash
# macOS / Linux
curl -fsSL https://chatgpt.com/codex/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"

# 패키지 매니저
npm install -g @openai/codex
brew install --cask codex
```

독립 설치 관리자는 기본적으로 `https://releases.openai.com/codex`에서 받고, 실패하면 GitHub Releases로 폴백합니다.
GitHub Releases를 강제하려면 `CODEX_INSTALLER_USE_RELEASES_OPENAI_COM=false`.

## 기본 사용

```bash
codex exec "your task prompt here"
```

- 진행 상황 → **stderr**
- 최종 출력 → **stdout** (파이프 가능)

```bash
codex exec "generate release notes" | tee output.md
```

## 권한 / 샌드박스

기본은 **읽기 전용**입니다. 명시적으로 올려야 합니다.

| 플래그 | 의미 |
|---|---|
| (기본) | read-only. 코드 점검에 안전 |
| `--sandbox workspace-write` | 파일 편집 허용 |
| `--sandbox danger-full-access` | 전체 접근. 주의 |

`--full-auto`는 **deprecated** — 명시적 sandbox 플래그를 쓰세요.

## 기계 판독 출력

```bash
codex exec --json "analyze repo" | jq
```

JSON Lines로 thread started / turns / items / errors 이벤트가 한 줄씩 나옵니다.

## 구조화 응답 (스키마 강제)

```bash
codex exec "extract metadata" --output-schema schema.json -o output.json
```

## 세션 이어가기

```bash
codex exec resume --last "continue with next step"
```

다단계 파이프라인에서 이전 실행을 재개합니다.

## CI 인증

잡 환경에 API 키를 노출하지 않는 쪽이 권장됩니다.

- GitHub Actions → [openai/codex-action](https://github.com/openai/codex-action)
- 단발 호출 → `CODEX_API_KEY=<key> codex exec "task"`

## 기타 CLI 모드

| 명령 | 용도 |
|---|---|
| `codex` | 대화형 TUI |
| `codex app` | 데스크톱 앱 경험 |
| `codex exec` | 비대화형 |
| `codex app-server` | App Server 프로세스 (JSON-RPC) |
| `codex app-server generate-ts` | TypeScript 프로토콜 정의 생성 |
| `codex app-server generate-json-schema` | JSON Schema 번들 생성 |
| `codex debug app-server send-message-v2 "<msg>"` | 한 턴의 전체 JSON 트래픽 덤프 |
| `codex mcp-server` | **Codex를 MCP 서버로** 노출 (MCP 클라이언트에서 도구처럼 호출) |
| `codex exec-server` | **셀프호스팅 실행기** (Agents API의 self-hosted 샌드박스용) |

## `codex mcp-server`를 쓸 때

이미 MCP 기반 워크플로가 있고 Codex를 호출 가능한 도구로 쓰고 싶을 때 적합합니다.
단점: **MCP가 노출하는 것만 얻습니다.** diff 업데이트처럼 풍부한 세션 시맨틱에 의존하는
Codex 고유 상호작용은 MCP 엔드포인트로 깔끔하게 매핑되지 않을 수 있습니다.
(OpenAI 자신도 VS Code 확장을 MCP로 만들려다 포기하고 App Server를 만들었습니다.)
