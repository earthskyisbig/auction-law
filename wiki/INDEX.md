# 부동산 법률·세무 쟁점 위키 — 색인

law.go.kr 조문·판례(및 조세심판원 결정) 원문 근거로 미리 조사해둔 부동산 경매·세법·재개발 핵심 쟁점 모음. `statute-researcher`·
`precedent-researcher`·`tax-advisor`는 새로 조사하기 전에 **이 색인에서 관련 항목이 있는지 먼저 확인**하고, 있으면
재활용하되 조문 번호·시행일·세율은 `law_api.py`로 짧게 재검증(24h 캐시라 비용이 크지 않음)한 뒤 인용한다. 개정·판례가
자주 바뀌는 주제이므로 각 항목의 "갱신일"이 6개월(세법은 3개월) 이상 지났으면 재조사를 권장한다.

## 사용법
- 조사관: 쟁점 키워드로 이 색인을 먼저 훑는다 → 해당 항목 파일(`wiki/auction/NN-*.md`, `wiki/tax/NN-*.md`, `wiki/redev/NN-*.md`) 확인 → 근거 원문이 최신인지 조문/판례번호로 재검증 → 인용.
- 위키에 없는 쟁점이면 평소대로 law.go.kr 실조회 후, 재사용 가치가 있다고 판단되면 이 색인에 새 항목으로 추가한다(경매는 `wiki/auction/TEMPLATE.md`, 세법은 `wiki/tax/TEMPLATE.md`, 재개발·재건축은 `wiki/redev/TEMPLATE.md` 참조).
- 위키는 `_workspace/`와 달리 **git에 커밋되는 영구 자산**이다(세션 간 재사용 목적). 개별 질문의 사실관계는 넣지 않는다 — 일반화된 쟁점·기준만 담는다.

## 경매 목록

| # | 쟁점 | 카테고리 | 파일 | 상태 | 갱신일 |
|---|------|---------|------|------|--------|
| 1 | 말소기준권리 판단과 인수/소멸 권리 구분 | 권리분석 기본 | [01-malso-gijunkwonli.md](auction/01-malso-gijunkwonli.md) | 완료 | 2026-07-27 |
| 2 | 유치권 성립요건과 허위·가장 유치권 판별 | 유치권 | [02-yuchikwon-seongrip.md](auction/02-yuchikwon-seongrip.md) | 완료 | 2026-07-27 |
| 3 | 법정지상권 성립요건 | 법정지상권 | [03-beopjeongjisangkwon.md](auction/03-beopjeongjisangkwon.md) | 완료 | 2026-07-27 |
| 4 | 임차인 대항력 요건과 인수 여부 | 임차인 권리 | [04-imchain-daehangryeok.md](auction/04-imchain-daehangryeok.md) | 완료 | 2026-07-27 |
| 5 | 최우선변제 소액임차인 보증금 | 임차인 권리 | [05-choewooseon-byeonje.md](auction/05-choewooseon-byeonje.md) | 완료 (연혁표 보강) | 2026-08-10 |
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
| 21 | 명도소송(인도청구소송) 절차 | 명도절차 | [21-myeongdosongsong.md](auction/21-myeongdosongsong.md) | 완료 | 2026-08-10 |
| 22 | 인도명령 6월 도과의 법적 성질과 효과 | 명도절차 | [22-indomyeongryeong-6wol-dogwa.md](auction/22-indomyeongryeong-6wol-dogwa.md) | 완료 | 2026-08-10 |
| 23 | 점유이전금지가처분 | 명도절차 | [23-jeomyuijeon-geumjigacheobun.md](auction/23-jeomyuijeon-geumjigacheobun.md) | 완료 | 2026-08-10 |
| 24 | 부동산 인도 강제집행 절차 | 명도절차 | [24-budongsan-indojipaeng.md](auction/24-budongsan-indojipaeng.md) | 완료 | 2026-08-10 |
| 25 | 유체동산(이삿짐) 처리 절차 | 명도절차 | [25-yuchedongsan-cheori.md](auction/25-yuchedongsan-cheori.md) | 완료 | 2026-08-10 |
| 26 | 상가건물 임대차보호법상 경매 시 임차권 소멸/인수 | 명도절차 | [26-sangga-imdaeeup-somyeol.md](auction/26-sangga-imdaeeup-somyeol.md) | 완료 | 2026-08-10 |

## 경매 3차 확장 후보 (아직 조사 안 함)
대위변제로 인한 권리관계 변동, 예고등기(폐지 전 물건 잔존 이슈), 구분소유적 공유(집합건물 대지권 미등기),
법정지상권 있는 건물의 지료 산정. — 필요 시 요청하면 같은 형식으로 추가 조사.

## 세법 목록

| # | 쟁점 | 카테고리 | 파일 | 상태 | 갱신일 |
|---|------|---------|------|------|--------|
| 1 | 다주택자 취득세 중과(조정대상지역·법인) | 취득세 | [01-chwideukse-jungwa.md](tax/01-chwideukse-jungwa.md) | 완료 | 2026-08-10 |
| 2 | 주택 수 산정 기준(분양권·입주권·오피스텔) | 취득세 | [02-jutaeksu-sanjeong.md](tax/02-jutaeksu-sanjeong.md) | 완료 | 2026-08-10 |
| 3 | 생애최초 취득세 감면 요건 | 취득세 | [03-saengaechoicho-gammyeon.md](tax/03-saengaechoicho-gammyeon.md) | 완료 | 2026-08-10 |
| 4 | 경매·공매 낙찰의 취득세 과세표준·유상취득 판단 | 취득세 | [04-gyeongmae-chwideukse.md](tax/04-gyeongmae-chwideukse.md) | 완료 | 2026-08-10 |
| 5 | 종부세 1세대1주택 특례(12억 공제·세액공제) | 재산세·종부세 | [05-jongbuse-1sedae1jutaek.md](tax/05-jongbuse-1sedae1jutaek.md) | 완료 | 2026-08-10 |
| 6 | 종부세 합산배제 임대주택 요건 | 재산세·종부세 | [06-jongbuse-imdaejutaek.md](tax/06-jongbuse-imdaejutaek.md) | 완료 | 2026-08-10 |
| 7 | 부부공동명의 1주택 종부세 특례 | 재산세·종부세 | [07-bubugongdong-jongbuse.md](tax/07-bubugongdong-jongbuse.md) | 완료 | 2026-08-10 |
| 8 | 주택임대소득 과세(분리과세·등록임대 감면) | 임대소득세 | [08-jutaek-imdaesodeuk.md](tax/08-jutaek-imdaesodeuk.md) | 완료 | 2026-08-10 |
| 9 | 1세대1주택 양도세 비과세 요건(보유·거주기간, 12억) | 양도소득세 | [09-1sedae1jutaek-biguase.md](tax/09-1sedae1jutaek-biguase.md) | 완료 | 2026-08-10 |
| 10 | 일시적 2주택 비과세 특례 | 양도소득세 | [10-ilsijeok-2jutaek.md](tax/10-ilsijeok-2jutaek.md) | 완료 | 2026-08-10 |
| 11 | 다주택자 양도세 중과(조정대상지역·한시배제) | 양도소득세 | [11-yangdose-jungwa.md](tax/11-yangdose-jungwa.md) | 완료·인용검증 PASS ([검증서](tax/11-yangdose-jungwa_verification.md)) | 2026-08-10 |
| 12 | 장기보유특별공제(1세대1주택 vs 일반) | 양도소득세 | [12-janggiboyu-teukbyeolgongje.md](tax/12-janggiboyu-teukbyeolgongje.md) | 완료 | 2026-08-10 |
| 13 | 조합원 입주권 양도세 비과세·주택수 산정 | 양도소득세 | [13-ipjugwon-yangdose.md](tax/13-ipjugwon-yangdose.md) | 완료 · **상가 전환 입주권 절 추가(2026-08-13)** | 2026-08-10 (F항 2026-08-13) |
| 14 | 분양권 양도세(단기중과·주택수 산입) | 양도소득세 | [14-bunyanggwon-yangdose.md](tax/14-bunyanggwon-yangdose.md) | 완료 | 2026-08-10 |
| 15 | 상생임대인 특례 | 양도소득세 | [15-sangsaeng-imdaein.md](tax/15-sangsaeng-imdaein.md) | 완료 | 2026-08-10 |
| 16 | 부동산 상속세 평가(시가·기준시가)와 공제 | 상속증여세 | [16-sangsokse-pyeongga.md](tax/16-sangsokse-pyeongga.md) | 완료 | 2026-08-10 |
| 17 | 부담부증여 시 양도세·증여세 병행 과세 | 상속증여세 | [17-budambu-jeungyeo.md](tax/17-budambu-jeungyeo.md) | 완료 | 2026-08-10 |
| 18 | 대체주택 양도세 비과세 특례(재건축·재개발) | 재개발재건축 특유 | [18-daechejutaek-biguase.md](tax/18-daechejutaek-biguase.md) | 완료 | 2026-08-10 |
| 19 | 청산금 과세(수령 시 양도세, 납부 시 취득가 가산) | 재개발재건축 특유 | [19-cheongsangeum-guase.md](tax/19-cheongsangeum-guase.md) | 완료 | 2026-08-10 |
| 20 | 매매사업자·법인의 부동산 양도 과세구조(비교과세·부가세) | 사업자·법인 | [20-maemaesaeopja-beobin.md](tax/20-maemaesaeopja-beobin.md) | 완료 | 2026-08-10 |

## 재개발·재건축 목록

정비사업(도정법) 도메인. **이 도메인의 핵심 특성은 법률·시행령이 정하지 않고 시·도조례와 조합 정관·관리처분계획에
위임한 사항이 많다는 것**이다 — 각 항목의 "⚠ 조례·정관 확인 필요" 절을 반드시 함께 읽을 것. 아래 5개 항목은
2026-08-13 재개발 상가 투자 종합검토 보고서를 위키화한 것으로 **citation-verifier 독립 검증 PASS**를 통과한 인용이다.
**조례 분석은 서울특별시 기준**이므로 다른 시·도 물건은 해당 조례를 개별 확인해야 한다.

| # | 쟁점 | 카테고리 | 파일 | 상태 | 갱신일 |
|---|------|---------|------|------|--------|
| 1 | 재개발 상가 소유자의 조합원 자격(도정법 §2 9호 가목·§39①, 지위 승계 시점) | 조합원 자격 | [01-sangga-johapwon-jagyeok.md](redev/01-sangga-johapwon-jagyeok.md) | 완료 (citation-verifier PASS) | 2026-08-13 |
| 2 | **상가→아파트 분양자격** — 법률 부존재 → 시행령 §63①3 위임 → 서울조례 §36①3 권리가액 기준 | 분양자격 | [02-sangga-apt-bunyang-jagyeok.md](redev/02-sangga-apt-bunyang-jagyeok.md) | 완료 (citation-verifier PASS) | 2026-08-13 |
| 3 | 현금청산(§73) — 청산금 산정·지연이자·인도 동시이행 | 현금청산 | [03-hyeongeum-cheongsan-sangga.md](redev/03-hyeongeum-cheongsan-sangga.md) | 완료 (citation-verifier PASS) | 2026-08-13 |
| 4 | 투기과열지구 양도제한의 상가 적용(§39②, 예외 규정 사각지대, 재개발/재건축 기산점 차이) | 양도제한 | [04-tugigwayeol-sangga-yangdo.md](redev/04-tugigwayeol-sangga-yangdo.md) | 완료 (citation-verifier PASS) | 2026-08-13 |
| 5 | 임차인 리스크 — 보증금 구상·압류(§70②~④), 영업보상(공람공고일 기준), 권리금 배제 | 임차인·보상 | [05-sangga-imchain-bosang.md](redev/05-sangga-imchain-bosang.md) | 완료 (citation-verifier PASS) | 2026-08-13 |

세무는 별도 항목을 만들지 않고 세법 위키에 연결했다 — 상가는 취득세 주택 수에 미산입이나 **관리처분계획인가로 입주권이
되는 순간 소득세법상 주택 수에 산입**된다(조심 2020구1136). → [tax/13 "F. 상가에서 전환된 입주권"](tax/13-ipjugwon-yangdose.md)

## 재개발·재건축 확장 후보 (아직 조사 안 함)
서울 외 시·도조례(경기·인천)의 재개발 분양대상 기준, 재건축 상가→아파트 전환(시행령 §63②2호) 상세,
1+1 분양(§76①7호라목) 요건, 재건축초과이익환수제, 조합 정관 표준안의 상가 관련 조항. — 필요 시 요청하면 같은 형식으로 추가 조사.

## 세법 2차 확장 후보 (아직 조사 안 함)
농지·비사업용토지 양도세 중과, 상가·오피스텔 부가가치세(포괄양수도 면제), 재건축초과이익환수제(재건축부담금),
1세대의 범위(세대분리 요건), 해외주택 보유 시 종부세·양도세 취급. — 필요 시 요청하면 같은 형식으로 추가 조사.
