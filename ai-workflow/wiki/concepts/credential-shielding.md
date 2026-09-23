---
type: concept
status: active
last_ingested_from: browser-agents/06-architecture-axes.md + browser-agents/09-aside-browser-internals.md + browser-agents/11-dia-and-neon.md
related_pages: [concepts/indirect-prompt-injection, concepts/perception-model, concepts/approval-gate, concepts/control-plane-execution-plane]
created: 2026-09-23
updated: 2026-09-23
---

# Credential Shielding — 에이전트에게 비밀을 주지 않고 로그인시키기

- 문서 목적: 에이전트가 로그인 뒤편에서 일하되 자격증명을 보지 못하게 하는 설계 패턴들을 비교한다.
- 범위: 세 가지 접근, 축의 분리, 구현 실측, 남는 한계
- 성격: **실행 표면 고유의 축.** 다만 "권한 등급과 비밀 노출의 분리"는 일반 원칙이다
- 최종 수정일: 2026-09-23

## §1 문제  {#s1-problem}

에이전트가 로그인된 사이트에서 일하려면 자격증명이 필요하다. 그런데 에이전트는
**프롬프트 주입에 취약**하다 ([[concepts/indirect-prompt-injection]]).
즉 **비밀을 쥐여주면 속았을 때 그대로 빠져나간다.**

## §2 세 가지 접근  {#s2-approaches}

| 접근 | 채택 | 원리 | 평가 |
|---|---|---|---|
| **URL 차단** | Comet | `chrome://password-manager` 등 자격증명 페이지 접근을 **차단**. `file://` 도 | **열거형 방어** — 새 경로가 생기면 뚫린다 |
| **값 은닉** | **Aside** | 에이전트에게 **원문 비밀번호를 주지 않고** 브라우저가 채운다 | **근본적** — 관측 범위에서 비밀을 제거 |
| **요소 은닉** | **Dia** | 비밀번호 필드와 **비가역 동작 버튼**을 "invisible to the agentic system" | **근본적, 그리고 더 넓다** — 자격증명을 넘어선다 |
| (비교) 전송 제한 | Opera Neon | 자격증명·결제 정보가 **Opera 서버로 전송되지 않음** | **다른 층위** — 에이전트 가시성은 별개 문제 |

> 📌 **값 은닉과 요소 은닉이 같은 문제의 다른 해법이다.** Aside 는 **값**을, Dia 는 **요소**를
> 숨긴다. Dia 쪽이 범위가 넓다 — "되돌릴 수 없는 동작 버튼"까지 지우므로 자격증명을 넘어
> 파괴적 동작 일반으로 확장된다.
>
> ⚠️ Neon 의 보장은 층이 다르다. "Opera 서버로 안 간다"는 **에이전트가 볼 수 없다**는 뜻이
> 아니다. 계획이 클라우드 모델에 있으므로([[concepts/control-plane-execution-plane]])
> 페이지 맥락이 모델로 갈 때 무엇이 포함되는지는 **미확인**이다.

## §3 핵심 원칙 — 권한 등급과 비밀 노출은 다른 축이다  {#s3-axis-split}

Aside 에서 가장 베낄 만한 설계다.

> 저장된 비밀번호 값은 **`full-access` 모드에서도 AI 에게 숨겨진다.**
> 자동완성 전에 **접근 정책과 대상 URL 을 함께 검증**한다.

> 📌 **"가장 센 권한 = 전부 볼 수 있음"이 아니다.** 같은 패턴이 샌드박스에도 있다 —
> `full-access` 에서도 `sandbox.enabled: true` ([[concepts/os-sandbox-policy]] §8.5).
> 권한 등급을 올리는 것과 방어를 해제하는 것을 **분리**한 것이다.

### §3.1 격리 모드의 일관성  {#s3-1-consistency}

> **시크릿 세션에서는 에이전트가 비밀번호 관리자를 쓸 수 없다.**

격리를 선언했으면 **자격증명까지 일관되게** 적용해야 한다. 부분 격리는 격리가 아니다.

## §4 구현 실측 — Aside Vault  {#s4-implementation}

마케팅 주장("하드웨어 기반 E2E 암호화, Secure Enclave, 포스트양자")을 바이너리에서 검증한 결과.
**libsodium 라이브러리 상수가 아니라 실제 호출부**(`background.js`) 기준:

| 원시함수 | 호출 수 | 역할 |
|---|---|---|
| `crypto_pwhash_str` | 13 | 비밀번호 해시 |
| **`crypto_box_seal`** | 12 | **익명 공개키 봉인** |
| `crypto_aead_xchacha20poly1305_ietf_encrypt`/`_decrypt` | 7/7 | AEAD |
| `crypto_secretbox_easy`/`_open_easy` | 4/4 | 대칭 |
| `crypto_kdf_derive` | 3 | 키 유도 |

키 유도는 **`ARGON2ID13`** + `memlimit_interactive`.
포스트양자는 **ML-KEM-768** (`crypto_kem_mlkem768_*`, 앱 래퍼 `mlKemEncapsulate`/`Decapsulate`).
Secure Enclave 는 `kSecAttrTokenIDSecureEnclave`, `CanCreateSecureEnclaveKeyPairBlocking`.
감사 로깅은 `appendAuditEvent` + `getPasswordAuditLogsDir`.

> 📌 **`crypto_box_seal` 이 12회로 많은 것이 설계와 부합한다.** 봉인 상자는 보내는 쪽이 받는 쪽
> 공개키로 암호화하고 **자신도 복호할 수 없는** 형태다. "에이전트에게 원문을 주지 않는다"를
> 구현하는 데 맞는 원시함수다.

> ⚠️ **검증 함정 기록**: 포스트양자 심볼은 **Chromium 이 원래 X25519MLKEM768 TLS 를 기본
> 탑재**하므로 포크에서 당연히 나온다. **파일 위치를 갈라** 제품 자신의 코드(Vault·데몬)에
> 있음을 확인한 뒤에야 고유 기능으로 확정했다. [[concepts/primary-source-verification]] §3.6.

## §5 그러나 — 기본값의 방향  {#s5-defaults}

설계는 좋은데 기본값이 반대인 경우가 있다.

| 제품 | 항목 | 기본값 |
|---|---|---|
| Aside | AI 자격증명 접근 정책 | **`Always allow`** (가장 느슨) |
| Aside | 권한 규칙 `default` | **`allow`** |
| Dia | 내용 데이터 수집 | **기본 on** (30일 보존) |

> ⚠️ **암호를 잘 짜는 것과 기본값을 좁게 잡는 것은 다른 일이다.** 도입 시 기본값을 먼저 확인하라.

## §6 커스텀 하네스에 옮길 것  {#s6-porting}

- [ ] **값 은닉으로** 가라. URL 차단은 열거형 방어다
- [ ] 위험 **요소 자체를 인식에서 제거**하는 쪽도 함께 고려하라 (Dia 방식) — 자격증명을 넘어 확장된다
- [ ] **권한 등급과 비밀 노출을 다른 축**으로 두라
- [ ] 격리 모드를 **자격증명까지 일관** 적용하라
- [ ] 자동완성 전에 **접근 정책 + 대상 URL** 을 함께 검증하라
- [ ] **기본값을 좁게** 잡아라
- [ ] 자격증명 접근에 **감사 로그**를 남겨라

## §7 다음에 읽을 문서  {#s7-next}

- [[concepts/indirect-prompt-injection]] — 왜 비밀을 주면 안 되는가
- [[concepts/perception-model]] — 요소 은닉은 인식 계층의 조작이다
- [[concepts/control-plane-execution-plane]] — 계획 위치가 실행 면의 비밀 취급을 결정한다
- 원문: [`browser-agents/06-architecture-axes.md`](../../../browser-agents/06-architecture-axes.md) §4
