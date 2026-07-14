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

## 언제 무엇을 조회하나
1. 질문의 도메인을 판별한다 → `references/domain-statute-map.md`에서 검색할 법령·키워드·조문을 특정.
2. **법령 조사관**은 `target=law`(현행법령)으로 법령→MST→조문(JO)을 확정.
3. **판례 조사관**은 `target=prec`(판례), `target=expc`(법령해석례), `target=decc`(행정심판례)를 병행 조회.
4. 검색범위가 애매하면 `search=2`(본문 검색)로 재조회.

## 도구
공용 스크립트: `scripts/law_api.py` (표준 라이브러리만 사용, 설치 불필요).

```bash
# 목록 검색
python scripts/law_api.py search --target prec --query "유치권 경매" --display 10
python scripts/law_api.py search --target law  --query "도시 및 주거환경정비법"
python scripts/law_api.py search --target expc --query "재건축 현금청산" --search 2

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
