# 10. Aside — 권한 집행 · Computer Use · 네이티브 암호층

> [09 §10](09-aside-browser-internals.md) 에서 미확인으로 남긴 3건을 판 결과다.
> 방법은 동일 — DMG 정적 분석, 데몬 SEA 페이로드(258,965줄) 탐색, 네이티브 바이너리 심볼 조사.
> 실행하지 않았다. 분석일 2026-09-23, `Aside-1.0.922.1.dmg`.
>
> ⚠️ 등급: 🔧 **관측된 구현**.

## 1. 권한 집행 — 문서보다 훨씬 정교하다

문서([02 §3](02-aside.md))는 "3구역 · Allow/Ask/Deny · 세션 모드 3종"까지만 말한다.
데몬의 zod 스키마를 읽으면 실제 정책 엔진이 나온다.

### 1.1 규칙 매칭 — 3종 (discriminated union on `type`)

| 유형 | 필드 | 설명(원문) |
|---|---|---|
| **`tool`** | `tool` | "Tool name or glob, e.g. \`bash\` or \`mcp__*\`." |
| | `args` | "Optional argument matchers **keyed by input field name**." |
| **`browser`** | `action` | `read` \| `modify` \| `download` |
| | `url` | "Optional URL glob." |
| **`network`** | `url` | "URL or domain glob." |

**인자 매처**(`argMatchSchema`)는 두 형태다:

```
{ $: "eq",    value: string | number | boolean | null }
{ $: "regex", value: string }
```

> 📌 **도구 이름 glob + 인자별 정규식 매칭**까지 있다. "bash 를 허용"이 아니라
> "bash 중 첫 인자가 이 정규식에 맞는 것만 허용"을 표현할 수 있다. 이 저장소 본 조사의
> Codex `ExecPolicyAmendment`([`docs/02-app-server-protocol.md`](../docs/02-app-server-protocol.md) §7)와
> 같은 문제의식이고, 표현력은 이쪽이 더 구체적이다.

### 1.2 버킷은 넷이다 — 문서에 없는 `approved`

```js
permissionRulesSchema = {
  allow:    [rule], approved: [rule],
  deny:     [rule], ask:      [rule],
  default:  "allow" | "deny" | "ask"   // 기본값: allow
}
```

> ⚠️ **`approved` 는 어느 문서에도 없는 네 번째 버킷**이다. 이름과 위치로 보아 "사용자가 이번
> 세션에서 승인함"을 담는 자리로 보인다 — 승인 프롬프트의 "Allow once"(§1.5)가 여기 쌓일 것이다.
> **추론 등급**으로 둔다.
>
> ⚠️ **`default` 의 기본값이 `allow`** 다. 규칙에 걸리지 않은 것은 통과가 기본이다.
> 제한은 `guard` 모드의 파일 root 설정이 담당하는 구조다.

### 1.3 파일 권한

```js
filePermissionConfigSchema = {
  readableRoots: [], writableRoots: [],
  outsideRead:  "deny" | "ask",   // 기본 ask
  outsideWrite: "deny" | "ask",   // 기본 ask
}
sandbox: { enabled: boolean }     // 기본 true
```

`full-access` 프리셋으로 보이는 값이 코드에 있다:

```js
{ rules: { allow:[], deny:[], ask:[], default:"allow" },
  files: { readableRoots:["/"], writableRoots:["/"],
           outsideRead:"deny", outsideWrite:"deny" },
  sandbox: { enabled: true } }
```

> 📌 흥미로운 점: **full-access 에서도 `outsideRead/Write` 는 `deny`** 다. 모순처럼 보이지만
> root 가 이미 `/` 라서 "바깥"이 존재하지 않는다. **root 확대와 바깥 정책을 분리**한 설계라
> 표현이 일관된다.
>
> 그리고 **full-access 에서도 `sandbox.enabled: true`** 다. 권한 등급과 샌드박스가 다른 축이다 —
> [02 §3.2](02-aside.md) 에서 본 "권한 등급과 자격증명 노출의 분리"와 같은 패턴이 여기서도 나온다.

### 1.4 해석 순서 — 계정 → 세션

```js
resolvePermission({ accountRoot, permissionMode, accountPermission, sessionPermission })
  → mergePermissionConfig({}, accountPermission)     // 계정 기본값
  → mergePermissionConfig(ei, sessionPermission)     // 세션 override
  → mergePermissionConfig(ei, { sandbox, files:{ readableRoots:[accountRoot, RUNTIME_DIR] }})
  → permissionMode === "read-only" 이면 별도 처리

checkPermission(ctx, callId, request)
  → hasPermission(resolvePermission({...}), request)
```

`hasPermission` 은 `request.type === "file"` 일 때 **`process.platform === "win32"` 분기**를 갖는다 —
경로 비교를 OS 별로 다르게 처리한다.

문서의 "두 층(에이전트 기본값 / 세션 override)"([02 §3.1](02-aside.md))이 코드로 확인된다.
다만 실제로는 **세 겹**이다 — 계정 → 세션 → 런타임 강제 root.

### 1.5 승인 프롬프트 — `03 §10` 의 빈칸이 채워졌다

[03 §10](03-aside-design-ux.md) 에서 "승인 UI 의 실제 형태는 문서에 없음, 판정 보류"로 뒀다.
데몬의 **suspension**(일시정지) 시스템이 그것이다.

| 종류 | 버튼 | 문구 |
|---|---|---|
| 권한 승인 | `Allow once` / (거부) | "_… deny it. **No lasting permission will be granted.**_" |
| `action-confirmation` | `Confirm` / `Cancel` | "_Confirm to proceed, or reply with what to do instead._" |
| `ask-user-question` | 선택지 **최대 5개** | "_Pick an option or just reply with your answer._" |

승인 범위는 네 가지로 렌더된다 (`formatApprovalScope`):

```
file    → "{mode}: {path}"
tool    → "Tool: {tool}\n{toolCallTitle(tool, args)}"
browser → "Browser: {action}\n{url}"
network → "Network: {url}"
```

> 📌 **가장 중요한 발견**: 프롬프트가 `{id, label, value, style}` 버튼 배열을 갖되,
> **번호 목록 텍스트 폴백**(`${i+1}. ${label}`)도 함께 만든다. 그리고 힌트가 전부
> *"or just reply with your answer"* 다.
>
> **이 승인 UI 는 네이티브 창이 아니라 채팅 채널에서 렌더되도록 설계돼 있다.**
> Pro 플랜의 "Channels (Remote control)"([02 §8](02-aside.md))이 이것이고, 번들에 discord.js 가
> 들어 있는 이유이기도 하다. 사용자가 Slack/Discord 에서 에이전트의 승인 요청을 받아
> 버튼을 누르거나 그냥 답장할 수 있다.
>
> "Allow once" 뿐이고 "항상 허용"이 없다는 점, 그리고 **"영구 권한은 부여되지 않는다"를
> 명시**하는 점은 보수적으로 잘 잡은 기본값이다.

## 2. Aside Computer Use — 문서에 없는 OS 제어 축

[09 §5](09-aside-browser-internals.md) 에서 존재만 확인했던 별도 바이너리다.

| 항목 | 값 |
|---|---|
| 형태 | **네이티브 Mach-O** (Node 아님), 2.0MB |
| 위치 | `AsideDaemon/mac-{arm64,x64}/Aside Computer Use.app` |

### 2.1 링크된 시스템 프레임워크

```
AppKit, ApplicationServices, Carbon, Contacts, CoreFoundation,
CoreGraphics, CoreServices, Foundation, IOKit, QuartzCore,
ScreenCaptureKit, Security, Vision
```

### 2.2 심볼이 말하는 능력

| 능력 | 심볼 |
|---|---|
| **시스템 전역 접근성 트리** | `AXUIElementRef`, **`AXTreeSerializer`**, `AXValueGetValue`, `AXValueGetTypeID` |
| **입력 탭 (관찰 + 주입)** | `CGEventTapCreate`, `CGEventTapEnable`, `CGEventTapIsEnabled` |
| 키보드·마우스 | `CGEventKeyboardGetUnicodeString`, `CGEventGetLocation`, `CGEventGetFlags`, `CGEventGetIntegerValueField` |
| 화면 캡처 | `ScreenCaptureKit`, `ScreenCaptureAccess` |
| 이미지 분석 | **`Vision.framework`** |
| 연락처 | **`Contacts.framework`** |

> 📌 **인식 철학이 일관된다.** 브라우저에서 접근성 트리 + ref 를 쓰는 것처럼
> ([08 §3](08-aside-code-level.md)), OS 제어에서도 **`AXTreeSerializer` 로 데스크톱 전체의
> 접근성 트리를 직렬화**한다. 스크린샷 좌표가 아니라 구조를 먼저 읽는다.
>
> ⚠️ 그러나 능력 범위는 **브라우저를 한참 넘어선다.** 이벤트 탭은 시스템 전역 키 입력을
> 관찰할 수도 주입할 수도 있고, 화면 캡처와 Vision OCR 이 붙고, **연락처 접근**까지 있다.
> [07](07-security.md) 의 프롬프트 주입과 겹쳐 읽으면, 속은 에이전트가 닿을 수 있는 면적이
> 브라우저 탭이 아니라 **데스크톱 전체**라는 뜻이다.
>
> 이 구성요소는 **어느 제품 문서에도 없다.** iMessage 스킬이 존재하는 것
> ([08 §7](08-aside-code-level.md))과 `Contacts.framework` 링크가 같은 방향을 가리킨다.

## 3. 네이티브 암호층 — 세 주장 판정

[99 §4](99-sources.md) 에서 미확인으로 남긴 마케팅 주장들이다.

### 3.1 Secure Enclave — ✅ 확인

`Aside Framework` 본체에서:

```
kSecAttrTokenIDSecureEnclave
SecureEnclaveOperation
CanCreateSecureEnclaveKeyPairBlocking
```

> Secure Enclave **키 쌍 생성** 경로가 실재한다. 생성 가능 여부를 먼저 확인하는
> (`CanCreate...Blocking`) 구조이므로, 미지원 기기에서는 폴백이 있을 것이다.

### 3.2 포스트양자 암호 — ✅ 확인 (단, 함정을 피해야 한다)

> ⚠️ **먼저 갈라야 할 것**: Chromium 은 2024년부터 **X25519MLKEM768 TLS 키 합의를 기본
> 탑재**한다. Chromium 포크에서 ML-KEM 문자열이 나온다고 해서 제품 고유 기능이 아니다.
> 그래서 **어느 파일에 있는지**를 확인했다.

결과 — **Aside 자신의 코드에 있다:**

| 위치 | 확인된 것 |
|---|---|
| `AsidePasswordManager/background.js` (Vault 앱 코드) | `crypto_kem_mlkem768_keypair`, `_enc`, `_dec`, `_enc_deterministic`, `_seed_keypair`, 및 각 바이트 길이 상수 |
| `aside-daemon` 페이로드 | `MLKEM768`, **`mlKemEncapsulate`**, **`mlKemDecapsulate`**, `mlKemImportKey`, `mlKemExportKey` |

**ML-KEM-768** (NIST FIPS 203) 이고, 애플리케이션 계층 래퍼까지 있다. 같은 파일에 `x25519` 가
함께 나오는 것으로 보아 **하이브리드 구성**(고전 + 포스트양자)일 가능성이 높다 — 표준적인 접근이다.

> ⚠️ 하이브리드 결합 방식 자체는 확인하지 않았다. **추론 등급.**

### 3.3 감사 로깅 — ✅ 확인

```
appendAuditEvent        (11)
AuditLogEvent           (11)
AuditLogOptionsType     (11)
getPasswordAuditLogsDir  (4)
```

**비밀번호 감사 로그 전용 디렉터리**가 있다. [02 §4](02-aside.md) 의 "감사 로깅" 주장에 실체가 있다.

## 4. 종합 — 마케팅 주장 대 실측

| 주장 | 판정 |
|---|---|
| 하드웨어 기반 E2E 암호화 | ✅ libsodium + **Secure Enclave 키 쌍** |
| 포스트양자 암호 | ✅ **ML-KEM-768**, Aside 자신의 코드. Chromium TLS 상속 아님 |
| 감사 로깅 | ✅ 전용 디렉터리 + `appendAuditEvent` |
| 민감 동작에 사람 승인 | ✅ suspension 시스템, "Allow once" 뿐이고 영구 권한 없음 |
| 에이전트에게 비밀번호 비노출 | ✅ `crypto_box_seal` 12회 ([09 §7](09-aside-browser-internals.md)) |

> 📌 **이 제품의 보안 주장은 대체로 사실이었다.** 조사 초기에 "랜딩 페이지 주장, 검증 불가"로
> 깎아 두었던 항목들이 코드에서 대부분 확인됐다. 다만 그것을 **확인하는 데 바이너리 분석이
> 필요했다는 사실 자체**가 기록될 만하다 — 제품 문서는 이 중 어느 것도 뒷받침하지 않는다.

## 5. 그러나 — 표면의 크기

같은 분석이 반대편도 보여준다.

| 항목 | 함의 |
|---|---|
| `capture-tab-without-userinteraction` ([09 §4](09-aside-browser-internals.md)) | 표준 브라우저의 제스처 요구를 우회하는 전용 API |
| `CGEventTapCreate` (§2.2) | 시스템 전역 입력 관찰·주입 |
| `Contacts.framework` (§2.2) | 연락처 접근 |
| `ScreenCaptureKit` + `Vision` (§2.2) | 화면 캡처 + OCR |
| `default: "allow"` (§1.2) | 규칙 미매칭 시 통과가 기본 |
| AI 자격증명 접근 기본값 `Always allow` ([02 §4](02-aside.md)) | 가장 느슨한 쪽이 기본 |

> **암호는 잘 짰다. 표면은 넓다.** 이 둘은 모순이 아니라 서로 다른 축이다.
> 비밀을 잘 보관하는 것과, 속은 에이전트가 닿을 수 있는 범위를 좁히는 것은 다른 문제다.
> [07 §9](07-security.md) 의 결론 — "완화의 실질은 권한 축소" — 이 그대로 적용된다.

## 6. 남은 미확인

| 항목 | 상태 |
|---|---|
| `approved` 버킷의 정확한 의미 | ⚠️ 추론 |
| 하이브리드 KEM 결합 방식 | ⚠️ 추론 |
| `Aside Computer Use` 의 실제 동작 흐름 | ⚠️ 심볼만 봤다. 호출 그래프 미추적 |
| Secure Enclave 미지원 기기의 폴백 | ⚠️ 미확인 |
| 서버로 가는 내용 | ⚠️ 정적 분석의 한계. 동적 관찰 필요 |
| **GUI · 시각 디자인** | ⚠️ 실행 필요. 리눅스 빌드 없음 |
