# 부동산경매 쟁점 위키 — 색인

law.go.kr 조문·판례 원문 근거로 미리 조사해둔 부동산경매 핵심 쟁점 모음. `statute-researcher`·`precedent-researcher`는
새로 조사하기 전에 **이 색인에서 관련 항목이 있는지 먼저 확인**하고, 있으면 재활용하되 조문 번호·시행일은
`law_api.py`로 짧게 재검증(24h 캐시라 비용이 크지 않음)한 뒤 인용한다. 개정·판례가 자주 바뀌는 주제이므로
각 항목의 "갱신일"이 6개월 이상 지났으면 재조사를 권장한다.

## 사용법
- 조사관: 쟁점 키워드로 이 색인을 먼저 훑는다 → 해당 항목 파일(`wiki/auction/NN-*.md`) 확인 → 근거 원문이 최신인지 조문/판례번호로 재검증 → 인용.
- 위키에 없는 쟁점이면 평소대로 law.go.kr 실조회 후, 재사용 가치가 있다고 판단되면 이 색인에 새 항목으로 추가한다(형식은 `wiki/auction/TEMPLATE.md` 참조).
- 위키는 `_workspace/`와 달리 **git에 커밋되는 영구 자산**이다(세션 간 재사용 목적). 개별 질문의 사실관계는 넣지 않는다 — 일반화된 쟁점·기준만 담는다.

## 목록

| # | 쟁점 | 카테고리 | 파일 | 상태 | 갱신일 |
|---|------|---------|------|------|--------|
| 1 | 말소기준권리 판단과 인수/소멸 권리 구분 | 권리분석 기본 | [01-malso-gijunkwonli.md](auction/01-malso-gijunkwonli.md) | 완료 | 2026-07-27 |
| 2 | 유치권 성립요건과 허위·가장 유치권 판별 | 유치권 | [02-yuchikwon-seongrip.md](auction/02-yuchikwon-seongrip.md) | 완료 | 2026-07-27 |
| 3 | 법정지상권 성립요건 | 법정지상권 | [03-beopjeongjisangkwon.md](auction/03-beopjeongjisangkwon.md) | 완료 | 2026-07-27 |
| 4 | 임차인 대항력 요건과 인수 여부 | 임차인 권리 | [04-imchain-daehangryeok.md](auction/04-imchain-daehangryeok.md) | 완료 | 2026-07-27 |
| 5 | 최우선변제 소액임차인 보증금 | 임차인 권리 | [05-choewooseon-byeonje.md](auction/05-choewooseon-byeonje.md) | 완료 | 2026-07-27 |
| 6 | 배당순위(확정일자부 임차권·전세권·근저당) | 배당 | [06-baedang-sunwi.md](auction/06-baedang-sunwi.md) | 완료 | 2026-07-27 |
| 7 | 당해세 우선원칙과 조세채권 배당순위 | 조세·공과금 | [07-danghaese-usun.md](auction/07-danghaese-usun.md) | 완료 | 2026-07-27 |
| 8 | 매각불허가 사유(민사집행법 §121·§123) | 절차·매각 | [08-maegak-bulheoga.md](auction/08-maegak-bulheoga.md) | 완료 | 2026-07-27 |
| 9 | 인도명령 대상·요건 vs 명도소송 | 절차·매각 | [09-indomyeongryeong.md](auction/09-indomyeongryeong.md) | 완료 | 2026-07-27 |
| 10 | 체납관리비(공용부분) 낙찰자 인수 여부 | 조세·공과금 | [10-chenap-gwanribi.md](auction/10-chenap-gwanribi.md) | 완료 | 2026-07-27 |
| 11 | 선순위 가압류·가처분·가등기의 인수 여부 | 권리분석 기본 | [11-seonsunwi-gaapryu-gacheobun.md](auction/11-seonsunwi-gaapryu-gacheobun.md) | 완료 | 2026-07-27 |
| 12 | 배당요구종기와 배당요구의 효력(실권 여부) | 배당 | [12-baedangyogu-jonggi.md](auction/12-baedangyogu-jonggi.md) | 완료 | 2026-07-27 |
| 13 | 상가임차인 대항력·권리금 회수기회 보호 | 임차인 권리 | [13-sangga-daehangryeok-gwonrigeum.md](auction/13-sangga-daehangryeok-gwonrigeum.md) | 완료 | 2026-07-27 |
| 14 | 재매각 절차(대금미납·보증금 처리) | 절차·매각 | [14-jaemaegak.md](auction/14-jaemaegak.md) | 완료 | 2026-07-27 |
| 15 | 무잉여 취소(잉여 가망 없는 경매의 취소) | 절차·매각 | [15-mujingyeo.md](auction/15-mujingyeo.md) | 완료 | 2026-07-27 |
| 16 | 지분경매(공유지분) 낙찰 후 공유물분할청구 | 특수물건 | [16-jibun-gyeongmae.md](auction/16-jibun-gyeongmae.md) | 완료 | 2026-07-27 |
| 17 | 농지 낙찰과 농지취득자격증명 | 특수물건 | [17-nongji-chwideukjagyeok.md](auction/17-nongji-chwideukjagyeok.md) | 완료 | 2026-07-27 |
| 18 | 선순위 전세권의 배당요구 여부에 따른 인수/소멸 | 특수물건 | [18-jeonsegwon-inswu-somyeol.md](auction/18-jeonsegwon-inswu-somyeol.md) | 완료 | 2026-07-27 |
| 19 | 조합설립인가 후 경매 취득 시 조합원 지위 승계 여부 | 재개발·재건축 연계 | [19-johapwon-jiwi-seunggye.md](auction/19-johapwon-jiwi-seunggye.md) | 완료 | 2026-07-27 |
| 20 | 투기과열지구 조합원 지위 양도 제한과 경매 예외 | 재개발·재건축 연계 | [20-tugigwayeoljigu-johapwon-yangdo.md](auction/20-tugigwayeoljigu-johapwon-yangdo.md) | 완료 | 2026-07-27 |

## 3차 확장 후보 (아직 조사 안 함)
대위변제로 인한 권리관계 변동, 예고등기(폐지 전 물건 잔존 이슈), 구분소유적 공유(집합건물 대지권 미등기),
법정지상권 있는 건물의 지료 산정, 유치권과 점유이전금지가처분의 경합. — 필요 시 요청하면 같은 형식으로 추가 조사.
