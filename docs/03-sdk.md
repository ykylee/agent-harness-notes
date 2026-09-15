# 03. Codex SDK (TypeScript / Python)

SDK는 **`codex` CLI를 자식 프로세스로 띄우고 stdin/stdout으로 JSONL 이벤트를 교환**하는 래퍼입니다.
JSON-RPC 클라이언트를 직접 만들 필요 없이 네이티브 라이브러리 인터페이스를 제공합니다.

## 1. TypeScript SDK

### 설치

```bash
npm install @openai/codex-sdk    # Node.js 18+
```

### 기본

```typescript
import { Codex } from "@openai/codex-sdk";

const codex = new Codex();
const thread = codex.startThread();
const turn = await thread.run("Diagnose the test failure and propose a fix");

console.log(turn.finalResponse);
console.log(turn.items);
```

같은 `Thread` 인스턴스에 `run()`을 반복 호출하면 대화가 이어집니다.

```typescript
const nextTurn = await thread.run("Implement the fix");
```

### 스트리밍

`run()`은 턴이 끝날 때까지 이벤트를 버퍼링합니다. 중간 진행(도구 호출, 스트리밍 응답, 파일 변경)을
받으려면 `runStreamed()`:

```typescript
const { events } = await thread.runStreamed("Diagnose the test failure and propose a fix");

for await (const event of events) {
  switch (event.type) {
    case "item.completed":
      console.log("item", event.item);
      break;
    case "turn.completed":
      console.log("usage", event.usage);
      break;
  }
}
```

> 이벤트 이름이 App Server의 `item/completed`가 아니라 **`item.completed`(점 표기)**임에 주의.
> SDK는 별도 이벤트 표면을 씁니다.

### 구조화된 출력

```typescript
const schema = {
  type: "object",
  properties: {
    summary: { type: "string" },
    status: { type: "string", enum: ["ok", "action_required"] },
  },
  required: ["summary", "status"],
  additionalProperties: false,
} as const;

const turn = await thread.run("Summarize repository status", { outputSchema: schema });
console.log(turn.finalResponse);
```

Zod에서 변환할 때는 `zod-to-json-schema`의 `target: "openAi"`:

```typescript
const schema = z.object({
  summary: z.string(),
  status: z.enum(["ok", "action_required"]),
});

const turn = await thread.run("Summarize repository status", {
  outputSchema: zodToJsonSchema(schema, { target: "openAi" }),
});
```

### 이미지 첨부

텍스트 항목은 최종 프롬프트로 합쳐지고, 이미지 항목은 CLI의 `--image`로 전달됩니다.

```typescript
const turn = await thread.run([
  { type: "text", text: "Describe these screenshots" },
  { type: "local_image", path: "./ui.png" },
  { type: "local_image", path: "./diagram.jpg" },
]);
```

### 스레드 재개

스레드는 `~/.codex/sessions`에 영속화됩니다.

```typescript
const savedThreadId = process.env.CODEX_THREAD_ID!;
const thread = codex.resumeThread(savedThreadId);
await thread.run("Implement the fix");
```

### 작업 디렉터리

기본은 현재 디렉터리이며, **복구 불가능한 오류를 막기 위해 Git 리포지터리일 것을 요구**합니다.

```typescript
const thread = codex.startThread({
  workingDirectory: "/path/to/project",
  skipGitRepoCheck: true,
});
```

### CLI 환경 통제 (Electron 등 샌드박스 호스트용)

```typescript
const codex = new Codex({
  env: { PATH: "/usr/local/bin" },
});
```

SDK는 그 위에 필요한 변수(`CODEX_API_KEY` 등)를 주입합니다.
`baseUrl`을 설정하면 `--config openai_base_url=...` 오버라이드로 전달됩니다.

### `--config` 오버라이드

JSON 객체를 받아 점 표기 경로로 평탄화하고 TOML 리터럴로 직렬화해 반복 `--config key=value` 플래그로 전달:

```typescript
const codex = new Codex({
  config: {
    show_raw_agent_reasoning: true,
    sandbox_workspace_write: { network_access: true },
  },
});
```

점 표기로 표현 불가능한 키는 `configOverrides`로 raw TOML 전달:

```typescript
const codex = new Codex({
  config: { default_permissions: "audit" },
  configOverrides: ['permissions.audit.filesystem={":root"="read","/path/to/project/.env"="deny"}'],
});
```

**우선순위**: 구조화 `config` → raw `configOverrides` → SDK 관리 설정(`baseUrl`) 및 thread 옵션 (뒤가 이김).

## 2. Python SDK

### 설치

```bash
pip install openai-codex    # Python 3.10+
```

`openai-codex-cli-bin` 런타임 의존성이 자동 설치되며, 안정 SDK 릴리스는 대응하는 안정 CLI 릴리스를 추적합니다.

### 기본

```python
from openai_codex import Codex

with Codex() as codex:
    thread = codex.thread_start()
    result = thread.run("Explain this repository in three bullets.")
    print(result.final_response)
```

`thread.run(...)`은 `TurnResult`(최종 응답 + 수집된 items + 토큰 사용량)를 반환합니다.
평문 문자열은 `TextInput(...)`의 축약형입니다.

### 샌드박스 프리셋

```python
from openai_codex import Codex, Sandbox

with Codex() as codex:
    thread = codex.thread_start(model="gpt-5.6-terra", sandbox=Sandbox.workspace_write)
    thread.run("Make the requested changes.")
    review = thread.run("Review the diff only.", sandbox=Sandbox.read_only)
```

| 프리셋 | 의미 |
|---|---|
| `Sandbox.read_only` | 읽기만 |
| `Sandbox.workspace_write` | 워크스페이스 + 설정된 쓰기 가능 루트에 쓰기 (일반적 기본값) |
| `Sandbox.full_access` | 파일시스템 제약 없음 |

**턴 단위 오버라이드는 이후 턴에도 적용**됩니다 (App Server의 sticky 시맨틱과 동일).

### 스트리밍 / steering / interrupt

`Thread.run(...)`은 완료까지 대기합니다.
스트리밍·steer·interrupt가 필요하면 `Thread.turn(...)`으로 **`TurnHandle`**을 받으세요.

### 신뢰할 수 없는 입력 — `ExternalMessage`

다른 에이전트/도구/애플리케이션에서 온 **신뢰할 수 없는 콘텐츠**는
`ExternalMessage`로 전달해야 합니다.

> 이것은 도구 수준 권한은 유지하되 **사용자 승인/권한을 부여하지 않습니다.**
> 평문 문자열과 `TextInput`은 *사용자 입력*을 의미합니다.

프롬프트 인젝션 대응이 타입 레벨로 들어와 있는 부분이라 실무에서 반드시 지켜야 합니다.

### 인증

```python
# ChatGPT 브라우저 로그인
with Codex() as codex:
    login = codex.login_chatgpt()
    print(login.auth_url)
    print(login.wait().success)

# 디바이스 코드
with Codex() as codex:
    login = codex.login_chatgpt_device_code()
    print(login.verification_url, login.user_code)
    login.wait()

# API 키
with Codex() as codex:
    codex.login_api_key("sk-...")
    print(codex.account().account)
```

기존 Codex 인증이 있으면 자동 재사용됩니다.

### 비동기

```python
import asyncio
from openai_codex import AsyncCodex, Sandbox

async def main() -> None:
    async with AsyncCodex() as codex:
        thread = await codex.thread_start(sandbox=Sandbox.workspace_write)
        result = await thread.run("Continue where we left off.")
        print(result.final_response)

asyncio.run(main())
```

### 스레드 재개

```python
with Codex() as codex:
    thread = codex.thread_resume("thr_123")
    print(thread.run("Continue where we left off.").final_response)
```

### 내장 도움말

```python
import openai_codex
from openai_codex import Codex, CodexConfig
help(openai_codex); help(Codex); help(CodexConfig)
# 또는 python -m pydoc openai_codex
```

## 3. SDK vs App Server

블로그의 솔직한 평가:

> Codex SDK는 App Server보다 **먼저 출시**되었기 때문에 현재 지원 언어가 적고 표면적이 좁다.
> 개발자 수요가 있다면 App Server 프로토콜을 감싸는 추가 SDK를 만들어,
> JSON-RPC 바인딩을 직접 쓰지 않고도 harness 표면을 더 넓게 커버하게 할 수 있다.

즉 **SDK ⊂ App Server** 관계이며, 앞으로 SDK가 App Server 위로 재구축될 가능성이 언급되어 있습니다.
