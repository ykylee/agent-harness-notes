# 09. Aside Browser — 바이너리 내부 구조

> 방법: macOS DMG(334MB)를 내려받아 Linux 에서 **정적 분석**했다. 실행하지 않았다 —
> 분석은 실행을 요구하지 않는다. 앱 번들 해체 → 내부 확장 3종 확인 → 데몬의 Node SEA
> 페이로드 추출(70MB / 258,965줄) → Vault 암호 호출부 확인.
> 대상 `Aside-1.0.922.1.dmg`, 분석일 2026-09-23.
>
> ⚠️ 등급: 🔧 **관측된 구현**. [08](08-aside-code-level.md)·[04](04-comet-architecture.md) 과 같다.

## 1. 재현

```bash
# 실제 배포 URL 은 /api/download/<os> 가 302 로 알려준다
curl -sSI https://aside.com/api/download/macos   | grep -i location
# → https://releases.aside.com/dev-updater/Aside-1.0.922.1.dmg
curl -sSI https://aside.com/api/download/windows | grep -i location
# → .../dev-updater/windows/1.0.922.1/AsideInstaller-1.0.922.1-win-x64.exe  (10.7MB 스텁)

curl -sSL -o Aside.dmg https://releases.aside.com/dev-updater/Aside-1.0.922.1.dmg
7z x -y -oDMG Aside.dmg        # Aside.app 이 바로 나온다
```

## 2. 큰 그림 — Electron 이 아니다

`Aside Framework.framework` 구조는 Chromium 의 `Chromium Framework` 와 같은 모양이다.
**진짜 Chromium 포크**이지 Electron 래퍼가 아니다.

| 항목 | 값 |
|---|---|
| 번들 ID | **`at.studio.AsideBrowser`** |
| 프레임워크 | `Aside Framework.framework/Versions/1.0.922.1/` (498MB) |
| 내부 확장 | `Libraries/AsideAgentManager`(52M), `AsidePasswordManager`(5.4M), `AsideDaemon`(353M) |
| 기타 | `libaperitif.dylib`, SwiftShader/Vulkan (Chromium 표준) |

### 버전이 세 갈래다

| 구성요소 | 버전 |
|---|---|
| 브라우저 셸 | **1.0.922.1** |
| 내부 확장 (Agent / Vault) | **1.26.923.310** |
| CLI | **1.26.916.1741** |

> 📌 확장과 CLI 가 `1.26.x` 로 같은 계열이고 브라우저 셸만 `1.0.x` 다. **에이전트 로직과
> 브라우저 껍데기의 릴리스 주기가 분리돼 있다**는 뜻이다. Chromium 추격([01 §3](01-landscape.md))과
> 에이전트 기능 개발을 따로 굴릴 수 있는 구조다 — Comet 이 확장을 서버에서 자동 갱신하는 것과
> 같은 동기다.

## 3. ⚠️ 앞선 서술의 정정 — Aside 도 확장으로 구현한다

[04 §1](04-comet-architecture.md) 에서 Comet 을 두고 *"네이티브 브라우저인데 내부 구현은 확장
3개"* 라며 Aside 와 대비시켰다. **그 대비는 틀렸다.**

`AsideAgentManager/manifest.json`:

```json
{ "name": "Aside Browsing Agent", "version": "1.26.923.310", "manifest_version": 3,
  "background": { "service_worker": "background.js", "type": "module" } }
```

**Aside 의 에이전트도 MV3 크롬 확장이다.** 두 제품이 같은 구조적 선택을 했다.
[01 §1](01-landscape.md) 에 적은 "겉 분류와 속 구조가 다를 수 있다"는 경고가 Comet 만의 특성이
아니라 **이 부류의 일반 패턴**이었던 셈이다.

> 이것이 이 조사에서 **자기 서술을 뒤집은 첫 항목**이다. 04 의 해당 단락에 정정 표시를 달았다.

## 4. 에이전트 확장의 권한 — 여기가 실제 신뢰 경계다

```
sidePanel, contextMenus, storage, activeTab, tabCapture, offscreen,
debugger, downloads, favicon, history, bookmarks, topSites, browsingData,
privacy, management, nativeMessaging, cookies, tabs, scripting, userScripts,
webNavigation, sessions, tabGroups, alarms, notifications
```

`host_permissions`: **`<all_urls>`** 그리고 **`https://api.anthropic.com/*`**

### 커스텀 Chromium 확장 API 8종

표준 Chrome 에 없는 것을 직접 추가했다. **이것이 포크를 뜬 이유다.**

| 권한 | 추정 용도 |
|---|---|
| `at.studio.Aside.ext.private.account` | 계정 |
| `...adblock` | 광고 차단 |
| `...browser-import` | 타 브라우저 데이터 가져오기 |
| `...notification` | 알림 |
| `...omnibox` | 주소창 (Ask AI 모드 — [03 §2](03-aside-design-ux.md)) |
| `...pref-get-set` | 브라우저 설정 읽기/쓰기 |
| **`...capture-tab-without-userinteraction`** | **사용자 상호작용 없이 탭 캡처** |
| `...launch-extension` | 확장 실행 |

> 📌 `capture-tab-without-userinteraction` 이 눈에 띈다. 표준 `tabCapture` 는 사용자 제스처를
> 요구하는데, 그 제약을 **우회하는 전용 API 를 포크에 심었다.** 에이전트가 배경에서 화면을
> 봐야 하니 필요한 것이지만, 동시에 **표준 브라우저가 왜 그 제약을 두는지**를 생각하면
> 이것이 포크의 대가다.
>
> `host_permissions` 에 **Anthropic API 가 명시**된 것도 기록해 둘 만하다. 다른 프로바이더는
> `<all_urls>` 로 덮이는데 Anthropic 만 따로 적혀 있다.

## 5. AsideDaemon — 353MB, 진짜 본체

```
AsideDaemon/
├── mac-arm64/
│   ├── Aside Daemon.app/Contents/MacOS/aside-daemon      ← 151MB Mach-O, Node SEA
│   └── Aside Computer Use.app/Contents/MacOS/aside-computer-use
└── mac-x64/ (동일 구성)
```

CLI 가 붙는 곳이 이것이다 ([08 §5](08-aside-code-level.md)):

| 채널 | 주소 |
|---|---|
| stable | **`http://127.0.0.1:21420`** |
| canary | **`http://127.0.0.1:21421`** |

> 📌 **`Aside Computer Use.app` 이 별도 실행파일**이라는 점이 중요하다. 브라우저 자동화와
> **컴퓨터 사용(OS 수준 제어)이 다른 프로세스**로 분리돼 있다. 문서에는 없는 기능 축이다.

### 데몬 페이로드

`aside-daemon` 도 Node SEA 다. 추출하면 **70,121,815 bytes / 258,965줄**의 JS 가 나온다.
CLI 번들(2.5MB)의 28배 — 에이전트 루프·프로바이더·저장소가 전부 여기 있다.

`drizzle` ORM 이 들어 있어 **데몬이 SQL 데이터베이스를 갖는다.**

## 6. 모델 프로바이더 — 문서보다 훨씬 넓다

문서([02 §9](02-aside.md))는 API 키 프로바이더 7종을 안내한다. 데몬 코드에서 확인되는 id 는
그보다 넓다.

```
anthropic, openai, google, xai, openrouter, cloudflare, mistral, fireworks,
github-copilot, together, groq, deepseek, ollama,
azure-openai-responses, openai-codex, opencode
```

엔드포인트 문자열에는 Bedrock(`bedrock-runtime.us-east-1.amazonaws.com`), NVIDIA,
Aliyun MaaS, `radius.pi.dev` 까지 등장한다.

> 📌 **`openai-codex` 와 `opencode` 가 프로바이더 id 로 있다.** 이 저장소의 본 조사
> ([`docs/`](../docs/))가 다루는 Codex 가 Aside 에서 **모델 제공자로 취급된다**는 뜻이다.
> 두 조사가 여기서 만난다.
>
> 그리고 `CODEX_TOOL_CALL_PROVIDERS = {openai, openai-codex, opencode}` 라는 집합이 있고,
> 인접 코드에 `supportsAdditionalTools` · `supportsToolSearch` 플래그가 보인다.
> `AdditionalTools` 는 Codex 의 `responses_lite` 요청 형태에서 도구 목록을 싣는 항목이다
> ([`docs/16-responses-chat-adapter.md`](../docs/16-responses-chat-adapter.md) §10.2).
> **Aside 가 Codex 의 요청 형태 분기를 그대로 구현하고 있다.**

> ⚠️ 정정: 초기 탐색에서 `opencode` 가 100회 출현한다고 셌으나, 대부분 ANSI 색상 변수
> `openCodes` 오탐이었다. 실제 의미 있는 출현은 프로바이더 id 와 `x-opencode-client` /
> `x-opencode-session` 헤더다.

## 7. Vault 암호 — 마케팅 주장의 실체

[02 §4](02-aside.md)·[99 §4](99-sources.md) 에서 "랜딩 페이지 주장, 검증 불가"로 뒀던 항목이다.
`AsidePasswordManager` 가 **libsodium** 을 싣고 있고, **라이브러리 상수가 아니라 실제 호출부**를
확인했다 (`background.js`).

| 원시함수 | 호출 수 | 역할 |
|---|---|---|
| `crypto_pwhash_str` | 13 | 비밀번호 해시 |
| `crypto_box_seal` | 12 | **익명 공개키 봉인** |
| `crypto_aead_xchacha20poly1305_ietf_encrypt` / `_decrypt` | 7 / 7 | AEAD 암호화 |
| `crypto_secretbox_easy` / `_open_easy` | 4 / 4 | 대칭 암호화 |
| `crypto_kdf_derive` | 3 | 키 유도 |
| `crypto_pwhash(` | 2 | 키 유도용 |

키 유도 파라미터로 **`ARGON2ID13`** 과 `memlimit_interactive` 가 확인된다.

> 📌 **표준적이고 잘 고른 조합이다.** Argon2id + XChaCha20-Poly1305 + Curve25519 sealed box 는
> 현대 비밀 관리의 정석이다. 마케팅의 "하드웨어 기반 E2E 암호화" 주장에 **구체적 실체가 있다.**
>
> `crypto_box_seal` 이 12회로 많은 것이 흥미롭다. 봉인 상자는 **보내는 쪽이 받는 쪽 공개키로
> 암호화하고 자신도 복호할 수 없는** 형태다. "에이전트에게 원문 비밀번호를 주지 않는다"
> ([02 §4](02-aside.md))는 설계와 부합하는 원시함수다.

> ⚠️ 여전히 미확인: **Secure Enclave 연동**과 **포스트양자 암호**는 이 확장 코드에서 확인되지
> 않았다. 네이티브 계층(`libaperitif.dylib` 또는 프레임워크 본체)에 있을 수 있다. 판정 보류.

## 8. 인식 모델 — ref 의 출처

[08 §3](08-aside-code-level.md) 에서 `snapshot()` 이 `e31` 같은 **가상 ref ID** 를 준다는 것을
확인했다. 데몬에서 `Accessibility.getFullAXTree` 같은 원시 CDP 호출은 거의 보이지 않고
(`Page.captureScreenshot` 5회), `injectedScript` 가 등장한다.

> 이는 Playwright 계열의 **aria snapshot** 방식과 일치한다 — 페이지에 스크립트를 주입해
> 접근성 트리를 만들고 `e1`, `e2`… 형태의 ref 를 매긴다. Comet 이 `chrome.debugger` 로
> CDP 의 `getFullAXTree` 를 직접 부르는 것([04 §5](04-comet-architecture.md))과 **구현 경로가 다르다.**
>
> ⚠️ 다만 주입 스크립트 본문을 끝까지 따라가지는 않았다. **추론 등급**으로 둔다.

## 9. 비교표 최종 갱신

| 축 | Comet | Aside |
|---|---|---|
| 외피 | Chromium + 확장 3종 | **Chromium 포크 + 확장 3종** (같다) |
| 에이전트 구현 | MV3 확장 (`comet-agent`) | **MV3 확장** (`Aside Browsing Agent`) |
| 커스텀 브라우저 API | 공개 정보 없음 | **8종 (`at.studio.Aside.ext.private.*`)** |
| 계획 위치 | **서버** (Perplexity 백엔드) | **로컬 데몬** (`127.0.0.1:21420`, 353MB) |
| 인식 | CDP `getFullAXTree` → YAML | **주입 스크립트 기반 aria snapshot → ref** |
| 동작 | 픽셀 좌표 `ComputerBatch` | ref 기반 locator |
| 모델 | Perplexity (Max 는 선택) | **16+ 프로바이더 id, BYO 구독/키** |
| 자격증명 | URL 차단 | **libsodium (Argon2id/XChaCha20/sealed box)** |
| OS 수준 제어 | — | **`Aside Computer Use.app` 별도 프로세스** |
| 저장소 | — | **drizzle ORM (SQL)** |

> 📌 **가장 큰 차이는 계획의 위치다.** 구조는 놀랍도록 닮았지만, Comet 은 서버가 계획하고
> Aside 는 353MB짜리 로컬 데몬이 계획한다. [02 §9](02-aside.md) 의 "BYO 구독/API 키"가
> 가능한 이유가 이것이다 — 계획이 로컬이니 사용자의 모델 자격증명을 그대로 쓸 수 있다.
> "local-first" 주장에 **구조적 근거가 있다.**

## 10. 남은 미확인

| 항목 | 상태 |
|---|---|
| Secure Enclave · 포스트양자 암호 | ⚠️ 확장 코드에서 미확인. 네이티브 계층 추정 |
| 주입 스크립트의 ref 생성 로직 | ⚠️ §8 은 추론. 끝까지 따라가지 않음 |
| 권한 강제(Allow/Ask/Deny)의 실제 집행 지점 | ⚠️ 데몬 258,965줄 중 미탐색 |
| `Aside Computer Use` 의 능력 범위 | ⚠️ 별도 바이너리, 미분석 |
| 서버 통신 내용 | ⚠️ 정적 분석으로는 한계. 실행 관찰 필요 |
| **GUI · 시각 디자인** | ⚠️ **여전히 미확인** — 실행이 필요하고 리눅스 빌드가 없다 |
