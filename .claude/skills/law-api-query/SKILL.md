---
name: law-api-query
description: >
  국가법령정보 공동활용(law.go.kr) Open API로 법령·조문·판례·법령해석례·행정규칙·자치법규·헌재결정례·행정심판례를
  조회한다. 부동산경매·공매·매매·재개발·재건축·청약 등 법률 근거를 실제 조문/판례 원문으로 확인해야 할 때 반드시 사용.
  "이 법 조문 찾아줘", "관련 판례 검색", "도정법 몇 조", "법령해석례 조회", "근거 조문 인용" 같은 요청이면 트리거.
  법령 조사관·판례 조사관 에이전트의 공용 조회 스킬. 시세·실거래·경매물건 스크래핑용이 아니다(그건 realprice/court-auction).
---

# law-api-query — 국가법령정보 Open API 조회

부동산 법률 판단의 **1차 근거(조문·판례 원문)**를 law.go.kr Open API에서 가져온다.
근거 없는 법률 서술을 막기 위해, 답변에 인용하는 조문·판례는 이 스킬로 실제 조회한 원문이어야 한다.

## 위키 우선 확인 (신규 조회 전 필수)
실조회에 들어가기 전에 **`wiki/INDEX.md`(경매 쟁점 위키)에 관련 항목이 있는지 먼저 확인**한다. 이미 조문·판례를 조사해둔 쟁점이면 그 항목을 재활용하되, 인용하기 전 핵심 조문 번호(MST/JO)만 `law_api.py`로 짧게 재검증한다(24h 캐시라 비용이 적다). 위키 항목의 "갱신일"이 6개월(빠르게 바뀌는 쟁점은 3개월) 이상 지났으면 재조사를 권장한다. 위키에 없는 쟁점을 새로 깊게 조사했고 재사용 가치가 있다고 판단되면, `wiki/auction/TEMPLATE.md` 형식으로 새 항목을 추가하고 `wiki/INDEX.md`에 등록한다(개별 사안의 사실관계가 아니라 일반화된 쟁점·기준만 담을 것).

## 언제 무엇을 조회하나
1. 질문의 도메인을 판별한다 → `references/domain-statute-map.md`에서 검색할 법령·키워드·조문을 특정.
2. **법령 조사관**은 `target=law`(현행법령)으로 법령→MST→조문(JO)을 확정. 세율표 등 별표 수치는 `target=licbyl`.
3. **판례 조사관**은 `target=prec`(판례), `target=expc`(법령해석례), `target=decc`(행정심판례)를 병행 조회. 세무 쟁점은 `target=ttSpecialDecc`(조세심판원 결정례)도 조회.
4. 결과가 없으면 **키워드를 변형**해 재조회한다(동의어·법률용어·조문명). ⚠️ `search=2`(본문검색)는 API가 무관한 결과를 반환하므로 **사용 금지**(2026-07-15 실측, OC 무관 — `docs/ERRORS.md` 참조).
5. ⚠️ **법령명 검색 결과 1번째를 그 법령이라고 가정하지 말 것.** `target=law` 검색은 완전일치 우선이 아니라 부분일치/관련도 순으로 정렬되어, 짧고 흔한 법령명(주택법·민법 등)일수록 "주택법"이 부분 문자열로 들어간 다른 법(예: 「민간임대주택에 관한 특별법」)이 먼저 나올 수 있다(2026-08-10 실측, `docs/ERRORS.md` 참조). `--display`를 넉넉히(10 이상) 주고 `법령명한글`이 **정확히** 일치하는 항목을 골라 MST를 확정한다.

## 기계판독 마커 (실패를 자연어로만 쓰다가 놓치는 것 방지)
`law_api.py`는 조회가 실패하거나 결과가 0건이면 JSON 출력 **앞에** 아래 마커를 한 줄 찍는다. 조사관은 이 마커를 보고 판단하고, 사람이 읽는 자연어 요약("결과 없음" 등)만으로 스스로 재해석하지 않는다.
- `[NOT_FOUND]` — 검색 결과 0건, 또는 본문 조회 시 "일치하는 판례가 없습니다" 류의 안내문만 온 경우(정상 JSON, 내용 없음 — 2026-08-10 실측: 국세법령정보시스템 출처 판례는 `target=prec` body 조회가 이렇게 옴). API 자체는 정상 응답했다는 뜻(추측 아님). → 검색이면 키워드 변형, 본문이면 그 판례는 원문 확보 불가로 처리.
- `[ERROR:HTTP_xxx]` / `[ERROR:NETWORK]` — 요청 자체가 실패(HTTP 에러·타임아웃·연결 실패). → "확인 안 됨"이 아니라 **"조회 실패"**로 구분 보고(원인이 다르면 사용자 조치가 다르다 — OC/IP 등록 확인 필요).
- `[ERROR:PARSE_FAILED]` — JSON이 아닌 응답(HTML 등). 보통 OC/IP 미등록·파라미터 오류. → "조회 실패"로 보고.
이 마커는 `_workspace/` 산출물에 근거 없음을 적을 때도 그대로 인용해 legal-analyst가 "결과 없음(NOT_FOUND)"과 "조회 실패(ERROR)"를 혼동하지 않게 한다.

## 캐싱
`law_api.py`는 파일 기반 캐시를 자동 적용한다 — **검색(search) TTL 1시간, 본문(body) TTL 24시간** (스크립트 옆 `.cache/`에 저장, `.gitignore` 처리됨). 조사관 2명이 병렬로 비슷한 질의를 던질 때 중복 호출을 줄인다. 인용 사후검증처럼 **최신 원문을 다시 확인해야 하는 경우**에는 `--no-cache`를 붙인다 (전역 옵션이라 서브커맨드 앞에 온다: `python law_api.py --no-cache body --target law --mst ...`).

## 도구
공용 스크립트: `scripts/law_api.py` (표준 라이브러리만 사용, 설치 불필요).

```bash
# 목록 검색
python scripts/law_api.py search --target prec --query "유치권 경매" --display 10
python scripts/law_api.py search --target law  --query "도시 및 주거환경정비법"
python scripts/law_api.py search --target expc --query "재건축 현금청산"   # search=1(기본)만 사용

# 본문 조회 (목록에서 얻은 MST/ID 사용)
python scripts/law_api.py body --target law  --mst 284065            # 법령 전체 조문
python scripts/law_api.py body --target law  --mst 284065 --jo 003900 # 제39조만
python scripts/law_api.py body --target prec --id 240671 --type HTML  # 판례 전문

# 판례 부가 필터
python scripts/law_api.py search --target prec --query "관리처분계획" \
  --extra curt=대법원 prncYd=20180101~20251231
```

## 인증 (OC + IP) — 중요
- `OC`는 open.law.go.kr에 등록한 **이메일 아이디(앞부분)**. 환경변수 `LAW_OC`로 지정.
  - **이 프로젝트 등록 OC: `myung7788`** (myung7788@naver.com). PowerShell: `$env:LAW_OC="myung7788"`
- **IP/도메인 등록 필수**: 이 API는 OC뿐 아니라 **요청을 보내는 서버의 공인 IP**도 검증한다.
  open.law.go.kr > 마이페이지 > OPEN API 신청/관리에서 **호출 IP를 등록**해야 통과한다.
  - 현재 IP 확인: `curl -s https://api.ipify.org`
  - 유동 IP면 재부팅 후 바뀔 수 있어 재등록이 필요하다.
- 검증 실패 시 응답: `{"result":"사용자 정보 검증에 실패하였습니다.","msg":"...IP주소 및 도메인주소를 등록..."}`
  → 이 메시지가 나오면 **OC가 아니라 IP 미등록** 문제다.
- 미지정 시 `test`로 폴백(조회 제한). OC 오류 시 JSON 대신 HTML/오류 JSON이 올 수 있다.

## 왜 이렇게 하나 (원칙)
- **원문 인용 우선**: 법률 답변의 신뢰도는 조문·판례 원문 인용에서 나온다. API 응답에 없는 내용을 지어내지 않는다.
- **식별자 흐름 유지**: 목록의 `법령일련번호(MST)`·`판례일련번호`를 본문 조회에 그대로 넘겨 정확한 원문을 확보한다.
- **시행일 확인**: 부동산 규제 법령은 개정이 잦다. `시행일자` 필드를 확인하고, 필요 시 `eflaw`(시행일법령)로 특정 시점 법령을 조회한다.

## 참조 파일
- `references/api-spec.md` — 엔드포인트·target·파라미터·응답 필드 전체 스펙
- `references/domain-statute-map.md` — 도메인별 법령·쟁점·조문·검색 키워드 매핑
