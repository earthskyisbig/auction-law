# 텔레그램에서 이 워크스페이스 쓰기 — 설치 안내

> **상태: 조사만 완료, 아직 설치 안 함** (조사일 2026-08-13)
> 이 하네스(에이전트 5 · 스킬 5 · 위키 46개)를 **한 줄도 고치지 않고** 텔레그램에서 쓸 수 있다는 것까지 확인했다.
> 나중에 실제로 설치할 때 이 문서만 보고 진행하면 된다.

## 결론 요약

**Claude Code Channels**(Anthropic 공식 기능, 2026-03 출시)를 쓴다. 텔레그램 메시지가 **이 PC에서 이미 떠 있는 Claude Code 세션으로 주입**되고, 코드와 하네스는 PC를 벗어나지 않는다. 메신저는 리모컨 역할만 한다.

처음에 우려했던 두 가지가 **모두 해결돼 있음을 확인**했다:

| 우려했던 것 | 실제 |
|---|---|
| 원격에서 Bash 승인을 못 하니 결국 `--dangerously-skip-permissions`로 전면 허용해야 하는 것 아닌가 | **권한 프롬프트가 텔레그램으로 전달된다.** 텔레그램 플러그인 소스에 `'claude/channel/permission': {}` 선언 확인함. 로컬 터미널 다이얼로그와 병렬로 뜨고 **먼저 답한 쪽이 적용**된다 |
| 내 봇 주소를 아는 제3자가 말을 걸면 내 PC 셸이 뚫리는 것 아닌가 | **발신자 화이트리스트가 내장.** 공식 문서 원문: *"only IDs you've added can push messages, and everyone else is silently dropped"* |

## 선결 요건

1. **Bun 설치 필수** — 채널 플러그인은 Bun 스크립트다. **2026-08-13 기준 이 PC에 미설치**(`bun: command not found`, Node는 v24.8.0). https://bun.sh
2. **인증** — claude.ai 계정 또는 Console API 키. Bedrock·Google Cloud Agent Platform·Microsoft Foundry에서는 사용 불가.
   - Pro/Max 개인 사용자는 조직 정책 검사를 건너뛰므로 바로 쓸 수 있다.
3. 마켓플레이스 `claude-plugins-official`는 **이미 등록돼 있음**(확인 완료).

## 설치 절차

```
# 1. 플러그인 설치 (설치 scope는 user 선택 — 모든 프로젝트에서 쓰려면)
/plugin install telegram@claude-plugins-official
#    설치 요약에 "Run /reload-plugins to activate." 나오면 그것도 실행

# 2. BotFather(@BotFather)에서 /newbot → 토큰 받기 → 주입
/telegram:configure <토큰>
#    저장 위치: ~/.claude/channels/telegram/.env
#    (환경변수 TELEGRAM_BOT_TOKEN으로 대체 가능, 셸 환경변수가 우선)

# 3. 세션 종료 후 채널 플래그로 재시작 ← 이걸 해야 채널이 실제로 켜진다
claude --channels plugin:telegram@claude-plugins-official

# 4. 텔레그램에서 봇에 아무 메시지 → 봇이 페어링 코드 회신 → 세션에서:
/telegram:access pair <code>

# 5. ★ 반드시 실행 — 기본이 pairing 모드라 잠그지 않으면 열려 있다
/telegram:access policy allowlist
```

**리허설 권장**: 텔레그램 붙이기 전에 `fakechat@claude-plugins-official`(localhost:8787 웹 UI)로 흐름을 먼저 테스트할 수 있다. 토큰도 외부 서비스도 필요 없다.

## 놓치기 쉬운 것

- **`--channels`는 `claude --help`에 안 나온다.** 프리뷰라 숨겨져 있을 뿐 정상 동작한다. 공식 문서 원문: *"The flags work even though they aren't listed."* → `--help`에 없다고 "기능이 없다"고 판단하지 말 것(2026-08-13에 실제로 이렇게 오판했다).
- **`/telegram:access policy allowlist`를 빼먹으면 안 된다.** 기본 정책이 `pairing`이라 그 상태로 방치하면 위험하다.
- **세션이 떠 있는 동안만 메시지가 도착한다.** 닫혀 있으면 **큐잉 없이 조용히 버려진다**(에러도 안 남). 상시 사용하려면 백그라운드 프로세스나 상주 터미널로 세션을 띄워둬야 한다.
- **터미널에는 Claude의 답장 본문이 안 보인다.** 수신 메시지는 `← telegram · ...` 한 줄로, 답장은 도구 호출과 "sent" 확인만 표시된다. 실제 답변은 텔레그램에만 나온다.
- 권한 승인 형식: Claude Code가 5글자 소문자 ID를 발급 → 텔레그램에서 `yes <id>` / `no <id>`로 회신. 형식이 어긋나면 일반 대화로 처리되고 다이얼로그는 계속 열려 있다.
- **relay되지 않는 것**: 프로젝트 신뢰 다이얼로그, MCP 서버 동의 다이얼로그는 로컬 터미널 전용이다.

## 리스크 · 주의

- **화이트리스트에 넣은 사람은 내 세션의 도구 실행을 승인·거부할 수 있다.** 공식 문서 경고 원문: *"Anyone who can reply through the channel can approve or deny tool use in your session, so only allowlist senders you trust with that authority."* → 본인 계정만 넣을 것.
- **프롬프트 인젝션 통로**가 된다. 문서 원문: *"An ungated channel is a prompt injection vector."* 채널로 들어온 내용은 전부 신뢰할 수 없는 입력으로 취급해야 한다.
- **Windows 지원이 공식 문서에 언급 없음 — 확인 안 됨.** macOS 전용은 iMessage뿐이고 텔레그램은 Bun 스크립트가 텔레그램 API를 폴링하는 구조라 원리상 Windows에서 못 돌 이유는 없지만, **문서상 보증이 없다.** 이 PC는 Windows 11이므로 실제로 되는지는 해봐야 안다.
- **리서치 프리뷰**다. 문서 원문: *"the `--channels` flag syntax and protocol contract may change based on feedback."* → 나중에 설치할 때 이 문서 절차가 바뀌었을 수 있으니 공식 문서를 먼저 재확인할 것.
- 무인 운용 시 `--dangerously-skip-permissions`를 쓰라고 문서가 안내하지만, **permission relay가 되므로 이 하네스에는 필요 없다.** 굳이 쓰지 말 것.

## 대안 — Remote Control (더 간단할 수 있음)

Bun도 봇 토큰도 없이 **claude.ai나 Claude 모바일 앱에서 로컬 세션을 직접 조종**하는 별도 공식 기능이 있다. "폰에서 이 워크스페이스를 쓰고 싶다"가 목적이라면 이쪽이 설치 부담이 훨씬 적다. **이번 조사 범위 밖이라 상세는 확인 안 함** — 나중에 텔레그램 설치 전에 이것부터 검토해볼 것.
→ https://code.claude.com/docs/en/remote-control

## 검토했으나 채택하지 않은 서드파티

| | 판단 |
|---|---|
| **Hermes Agent** (`NousResearch/hermes-agent`) | `hermes import-agent claude-code`로 `.claude/` 자산 이관 가능, Windows 네이티브 지원, 승인 버튼·하드라인 블록리스트 등 안전장치가 촘촘함. 다만 **하네스를 이식해야 하고**, Anthropic OAuth 경로는 **Claude Max + 별도 구매 extra usage 크레딧 필수**(Pro는 OAuth 불가, API 키 종량제만) |
| **OpenClaw** (`openclaw/openclaw`) | 텔레그램 내장, `openclaw-code-agent` 플러그인으로 Claude Code를 그대로 굴리는 구성 가능. 다만 **샌드박싱 기본 off**(도구가 호스트에서 그대로 실행)이고 **Windows 샌드박싱은 문서에 언급조차 없음**. Claude Code 연동이 코어가 아니라 서드파티 플러그인(45★/25★) 의존 |

→ Channels가 **하네스 이식이 불필요하고 추가 비용도 없어** 우위. 서드파티는 다른 요구(예: 여러 CI 연동, 멀티유저 서비스)가 생겼을 때 재검토.

## 출처

- https://code.claude.com/docs/en/channels (공식, 원문 확인)
- https://code.claude.com/docs/en/channels-reference
- https://code.claude.com/docs/en/remote-control
- https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram (플러그인 소스 — permission 선언 직접 확인)
