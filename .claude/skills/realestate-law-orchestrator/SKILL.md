---
name: realestate-law-orchestrator
description: >
  부동산경매·공매·매매·재개발·재건축·청약의 법률 및 세무 질문에 대해 법령·판례·세법 근거를 조회·종합해 답하는
  부동산법률팀을 조율한다. "경매 권리분석 법적으로", "재개발 조합원 자격/현금청산", "청약 자격/전매제한", "공매 대항력",
  "매매 계약금/하자/토지거래허가", "취득세/양도세/종부세/다주택 중과 계산", "1세대1주택 비과세", "재건축 입주권 양도세",
  "매도 시 세금/절세", "이 상황 법적으로/세금으로 어떻게 되나", "근거 조문·판례 정리해줘", "법률/세무 검토 보고서"
  같은 요청이면 사용. 후속 요청("다시 검토", "이 쟁점만 보완", "업데이트", "이전 결과 기반으로")도 이 스킬로 처리.
  단순 용어 질문은 직접 답변 가능. 시세·실거래·경매물건 스크래핑은 대상 아님.
---

# realestate-law-orchestrator — 부동산법률팀 오케스트레이터

부동산 5개 도메인(경매·공매·매매·재개발/재건축·청약)의 **법률·세무 질문**을 **조문·판례·세법 근거로 종합**하는
에이전트 팀을 구성·조율한다.

## 실행 모드
**에이전트 팀** (팬아웃/팬인 → 종합). 기본 3명 + 세무 쟁점 시 1명:
| 에이전트 | 역할 | 스킬 | 포함 조건 |
|----------|------|------|-----------|
| `legal-analyst` (리더) | 도메인 판별·쟁점 도출·종합·보고서 | realestate-law-analysis | 항상 |
| `statute-researcher` | 법령·조문(세법 포함) 조회 | law-api-query | 항상 |
| `precedent-researcher` | 판례·법령해석례·예규 조회 | law-api-query | 항상 |
| `tax-advisor` | 세금 이벤트 판별·세액 산출·절세 | realestate-tax-analysis | **세무 쟁점 있을 때** |

**세무 쟁점 감지**: 질문에 취득세·양도세·종부세·재산세·부가세·상속증여세·중과·비과세·절세·입주권 세금·매매사업자/법인 과세 등이 있으면 `tax-advisor`를 팀에 포함한다. 세금 조사는 새 조사관을 만들지 않고 기존 `statute-researcher`(세법 조문)·`precedent-researcher`(국세 판례·예규)를 재사용한다.

모든 Agent 호출은 `model: "opus"`.

⚠️ **`isolation: "worktree"`를 절대 쓰지 말 것.** `_workspace/`는 `.gitignore` 대상이라, 격리 워크트리에서 조사관이 그 안에 파일을 써도 git은 "변경 없음"으로 판정해 에이전트 종료 시 워크트리를 자동 정리(삭제)한다 — 조사 결과 파일이 통째로 유실된다(2026-07-27 실측: statute-researcher·precedent-researcher 산출물 유실, 완료 보고서 텍스트로 수동 복원). 조사관·분석관 에이전트는 항상 **격리 없이(기본값)** 실행해 `_workspace/`에 직접 쓰게 한다.

## Phase 0: 컨텍스트 확인
- `_workspace/` 존재 + 부분 수정 요청 → **부분 재실행** (해당 쟁점만 조사관 재호출).
- `_workspace/` 존재 + 새 질문 → 기존을 `_workspace_prev/`로 이동 후 **새 실행**.
- `_workspace/` 미존재 → **초기 실행**.
- 실사용이면 `LAW_OC` 환경변수(등록 이메일 아이디) 설정을 먼저 확인. 미설정이면 `test`로 진행하되
  조회 제한 가능성을 사용자에게 고지.

## Phase 1: 팀 구성 & 도메인 판별
1. 세무 쟁점 감지 → 팀원 구성 결정(기본 3명, 세무 시 tax-advisor 추가).
2. `TeamCreate`로 `부동산법률팀` 구성.
3. `legal-analyst`가 법률 도메인·쟁점을 판별(`law-api-query/references/domain-statute-map.md` + `realestate-law-analysis/references/issue-checklists.md`). 세무 포함 시 `tax-advisor`가 세금 이벤트·납세자 구조를 판별(`realestate-tax-analysis/references/tax-map.md`).

## Phase 2: 병렬 조사 (팬아웃)
1. `TaskCreate`로 조사 작업 등록.
2. `statute-researcher`·`precedent-researcher`(및 세무 시 `tax-advisor`) 스폰 시 **`isolation` 파라미터를 지정하지 않는다**(worktree 금지 — 위 경고 참조).
2-1. 경매 쟁점이면 조사관에게 `wiki/INDEX.md`(경매 쟁점 위키, `_workspace/`와 달리 git 커밋되는 영구 자산)를 먼저 확인하도록 지시 — 이미 조사된 항목은 재조사 대신 재검증만 한다.
3. `SendMessage`로 검색 지시 배분:
   - `statute-researcher` → 법령·조문(세무 시 세법 조문 포함) → `_workspace/01_statute_findings.md`
   - `precedent-researcher` → 판례·법령해석례·예규 → `_workspace/02_precedent_findings.md`
4. 조사관들은 병렬 조회 후 결과 파일 경로를 리더/tax-advisor에게 통지.

## Phase 3: 종합 (팬인)
1. `legal-analyst`가 조문↔판례 교차 검증. `tax-advisor`는 세법 근거로 세액 산출(중과·특례 반영) → `_workspace/tax_analysis.md`.
2. **법률·세무 정합**: 재건축 입주권 성립 시점 등 공통 전제를 legal-analyst ↔ tax-advisor가 맞춘다.
3. 근거 부족 쟁점은 조사관에게 1회 추가 검색 재요청.
4. `legal-analyst`가 법률+세무를 `_workspace/03_analyst_report.md`에 종합.
5. **인용 사후검증**: 사용자 출력 전, `legal-analyst`가 보고서에 인용한 조문·판례를 `law_api.py`로 재조회해 ✓/✗/⚠ 표시(`realestate-law-analysis` 스킬 참조). ✗가 나오면 보고서를 수정한 뒤에만 다음 단계로 진행.
6. 검증 완료된 보고서를 사용자에게 요약.
7. 팀 정리(`TeamDelete`).

## 데이터 전달 프로토콜
- 태스크 기반(조율) + 파일 기반(산출물, `_workspace/{phase}_{agent}_{artifact}.md`) + 메시지 기반(실시간 지시).
- 최종 보고서만 사용자 지정 경로/화면에 출력, 중간 파일은 `_workspace/`에 보존(감사 추적).

## 에러 핸들링
- 조회 실패(OC 오류/HTML 응답): 1회 재시도 → 재실패 시 해당 근거 없이 진행하고 보고서에 누락 명시.
- 판례 미발견: **키워드 변형**으로 재검색(`search=2`는 무관 결과를 반환하므로 금지) 후에도 없으면 "관련 판례 확인 안 됨"으로 명시.
- 상충 근거: 삭제 금지, 출처 병기 + 다수·최신 견해 표시.

## 테스트 시나리오
- **정상 흐름**: "재건축 조합설립 후 조합원 지위를 양수했는데 조합원 자격이 인정되나요?(투기과열지구)"
  → 도정법 §39 조문 + 조합원 지위 양도 제한/예외 판례·해석례 → 적용 분석 + 리스크 보고서.
- **법률+세무 복합**: "재건축 입주권을 3년 보유 후 팔면 양도세가 얼마인가요? 1세대1주택인데요"
  → tax-advisor 포함 팀. legal-analyst가 입주권 성립·주택 수 판단 → tax-advisor가 소득세법·조특법 근거로 비과세 특례 검토 + 양도세 산출 → 통합 보고서.
- **에러 흐름**: `LAW_OC` 미설정으로 판례 조회가 HTML 오류 → 1회 재시도 → 실패 시 조문 근거만으로 진행하고
  "판례 근거 조회 실패, OC 등록 필요"를 보고서에 명시.

## 고지
산출물은 일반 법률정보이며 개별 사건의 최종 판단은 변호사·법무사 상담이 필요하다는 문구를 항상 포함한다.
