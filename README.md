# auction-law — 부동산 법률·세무 AI 에이전트

부동산 **경매 · 공매 · 매매 · 재개발 · 재건축 · 청약**의 법률·세무 질문을,
**국가법령정보(law.go.kr) Open API의 조문·판례 원문 근거**로 검토해 답하는 Claude Code 하네스입니다.

> "재건축 조합설립 후 경매로 샀는데 조합원 지위가 승계되나요? 투기과열지구입니다"
> → 도정법 §39② + 시행령 §37③5호 + 헌재·대법원 판례 + 법제처 유권해석까지 찾아 근거로 답합니다.

**핵심: 지어내지 않습니다.** 모든 법적 주장에 조문·판례 근거를 붙이고, 근거를 못 찾으면 "확인된 근거 없음"으로 명시합니다.

---

## 준비물

| 항목 | 필요 | 비고 |
|------|------|------|
| [Claude Code](https://claude.com/claude-code) | 필수 | 이 하네스는 Claude Code에서 동작합니다 |
| [Python 3.8+](https://www.python.org/downloads/) | 필수 | API 조회 스크립트용 (추가 패키지 설치 불필요) |
| [Git](https://git-scm.com/downloads) | 필수 | 내려받기용 |
| law.go.kr 계정 | **불필요** | 가입 없이 바로 됩니다 (자세히는 아래 "OC 등록") |

---

## 설치 (3분)

### 1. 내려받기
```bash
git clone https://github.com/earthskyisbig/auction-law.git
cd auction-law
```

### 2. 설치 점검
```bash
python scripts/check_setup.py
```
아래처럼 나오면 **끝입니다**:
```
[  OK  ] 파이썬 3.13.5
[  OK  ] 하네스 파일: 에이전트 5개 · 스킬 5개
[  OK  ] law.go.kr 조회 성공 — 예: '주택법' 확인됨
준비 완료.
```

### 3. 사용
Claude Code에서 **이 폴더를 열고** 그냥 질문하면 됩니다. 별도 명령어를 외울 필요 없습니다.

```
claude
```
그리고 이렇게 물어보세요:
```
투기과열지구 재건축 아파트를 은행 임의경매로 낙찰받았습니다.
조합설립인가는 난 상태인데 조합원 지위를 승계받나요?
```

에이전트 팀이 알아서 법령·판례를 조회하고 근거와 함께 답합니다.

---

## 이런 걸 물어보세요

**법률**
- `재건축 조합설립 후 경매 취득 시 조합원 지위가 승계되나요? (투기과열지구)`
- `경매 낙찰받았는데 체납관리비는 제가 다 내야 하나요?`
- `대항력 있는 임차인이 있으면 명도가 어떻게 되나요?`
- `재개발 현금청산 대상이 되면 청산금은 어떻게 정해지나요?`

**세무**
- `조정지역 빌라를 경매로 사서 6개월 안에 매매사업자로 팔면 취득세·양도세가 얼마인가요?`
- `기존 1주택 있는데 한 채 더 사면 취득세 중과되나요?`
- `재건축 입주권 양도세는 어떻게 계산되나요?`

**보고서로 받기**
- `방금 분석을 웹앱 보고서로 만들어줘`

---

## 무엇이 들어있나

```
auction-law/
├─ .claude/
│  ├─ agents/            에이전트 5명 (팀으로 협업)
│  │   ├─ legal-analyst          팀 리더 — 쟁점 도출·종합·보고서 초안
│  │   ├─ statute-researcher     법령·조문 조사
│  │   ├─ precedent-researcher   판례·유권해석 조사
│  │   ├─ citation-verifier      독립 인용 검증 (2차 시야, 최종 출력 전 필수)
│  │   └─ tax-advisor            세무 자문 (세금 질문 시 합류)
│  └─ skills/            스킬 5개
│      ├─ law-api-query              law.go.kr API 조회 (+ 조회 스크립트)
│      ├─ realestate-law-analysis    법률 분석 절차·쟁점 체크리스트
│      ├─ realestate-tax-analysis    세무 분석·세율표
│      ├─ citation-verification      인용 사후검증 절차
│      └─ realestate-law-orchestrator 팀 조율 (자동 실행됨)
├─ design/               보고서 웹앱 템플릿 + 디자인 시스템
├─ docs/                 워크로그 · 에러 재발방지 · 강의자료
├─ wiki/                 미리 조사해둔 경매·세법 쟁점 40개 (재사용 지식 자산)
└─ scripts/check_setup.py 설치 점검
```

**동작 방식**: 질문 → `legal-analyst`가 도메인·쟁점 판별 → 조사관 2명이 **병렬로** 법령·판례 조회(위키에 이미 있으면 재활용) → (세금이면 `tax-advisor` 합류) → 교차 검증 종합 → `citation-verifier`가 **독립적으로** 인용을 재검증(2차 시야) → 통과한 근거로만 최종 답변.

직접 조회해보고 싶다면:
```bash
python .claude/skills/law-api-query/scripts/law_api.py search --target prec --query "유치권 경매" --display 5
python .claude/skills/law-api-query/scripts/law_api.py search --target law --query "도시 및 주거환경정비법"
```

---

## OC 등록 (선택 — 안 해도 됩니다)

law.go.kr API는 `OC`라는 인증값을 쓰는데, **기본값 `test`로도 법령·판례·헌재·법령해석례가 모두 조회됩니다.** 강의 실습에는 충분하니 **그냥 시작하세요.**

본인 계정으로 쓰고 싶다면(조회 한도가 넉넉해집니다):

1. [open.law.go.kr](https://open.law.go.kr) 가입 → **OPEN API → 활용신청**
2. ⚠️ **신청서에 "서버 IP"를 반드시 등록**하세요. 이 API는 **OC와 호출 IP를 함께 검증**합니다.
   내 IP 확인: `python scripts/check_setup.py` 실행 시 하단에 표시됩니다.
3. `.env.example`을 `.env`로 복사하고 본인 OC(이메일 아이디 앞부분) 입력:
   ```
   LAW_OC=your_id
   ```

> 💡 가정용 인터넷은 IP가 바뀔 수 있습니다. 바뀌면 재등록하거나, `.env`의 `LAW_OC`를 지워 `test`로 되돌리면 계속 동작합니다.
> `.env`는 `.gitignore`에 있어 커밋되지 않습니다.

---

## 자주 겪는 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| `사용자 정보 검증에 실패하였습니다` | OC는 맞지만 **호출 IP 미등록** (OC 문제 아님) | IP 등록, 또는 `.env`에서 `LAW_OC` 삭제 → `test` 사용 |
| `python: command not found` | 파이썬 미설치/PATH 누락 | Python 3.8+ 설치 (Windows는 "Add to PATH" 체크) |
| 에이전트가 안 뜬다 | 다른 폴더에서 실행 | `cd auction-law` 후 Claude Code 실행 (`.claude/`가 있는 폴더) |
| 검색 결과가 엉뚱함 | `--search 2`(본문검색) 사용 — API가 무관한 결과를 반환함(OC 무관) | 기본 검색(`search=1`)만 쓰고 **키워드를 바꿔** 재검색 |

더 많은 사례: [`docs/ERRORS.md`](docs/ERRORS.md)

---

## ⚖️ 고지

이 도구의 산출물은 조문·판례에 근거한 **일반 법률·세무 정보**입니다.
개별 사건의 최종 판단과 세금 신고는 반드시 **변호사·법무사·세무사** 확인을 받으세요.
세법·부동산 규제는 개정이 잦으므로 **시행일**을 항상 확인하십시오.

---

데이터 출처: [국가법령정보 공동활용](https://open.law.go.kr) (법제처)
