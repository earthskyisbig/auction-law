# auction-law

## 하네스: 부동산 법률 에이전트

**목표:** 부동산경매·공매·매매·재개발·재건축·청약 법률 질문을 law.go.kr Open API의 조문·판례 원문 근거로 종합해 답한다.

**트리거:** 위 도메인의 법률 검토/자문/권리분석/근거 조문·판례 정리 요청 시 `realestate-law-orchestrator` 스킬을 사용하라. 후속 요청(재검토·보완·업데이트)도 동일 스킬. 단순 용어 질문은 직접 응답 가능.

**전제:** `LAW_OC=myung7788` 설정 + open.law.go.kr에 **호출 서버 공인 IP 등록** 필수(OC와 IP 둘 다 검증). 미설정 시 `test`로 제한 조회.

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-07-14 | 초기 구성 (팀 3인 + 스킬 3종) | 전체 | - |
| 2026-07-14 | 등록 OC=myung7788 반영 + IP 등록 요건 문서화 | law-api-query, CLAUDE.md | 실호출 시 IP 미등록 검증 실패 발견 |
| 2026-07-14 | 세무 자문관(tax-advisor) + realestate-tax-analysis 스킬 추가, 오케스트레이터에 조건부 편성 | agents/tax-advisor.md, skills/realestate-tax-analysis, orchestrator | 세무 쟁점(취득세·양도세·종부세 등) 대응 확장 요청 |


## 워크스페이스 표준 (workspace-init)

**프로젝트:** auction-law — 부동산경매·공매·매매·재개발·재건축·청약 법률에이전트 (law.go.kr Open API 기반 조문·판례 근거 검토)

작업 중 지킬 규율:
- 시작 시 `docs/ERRORS.md`를 읽고, 에러 해결 시마다 한 줄 추가(재발방지).
- 의미 있는 진전마다 `docs/WORKLOG.md` 갱신(강의용).
- 비밀은 오직 `.env`(커밋 금지). 새 키는 `.env.example`에 자리표시자 추가.
- 데이터는 `db/db.py`의 DuckDB로 적재·질의.
- 마무리 시 `docs/LECTURE.md` 7단(목적·결과물·동작원리·프롬프트·Do·Don't·자주에러) 작성.
