# -*- coding: utf-8 -*-
"""양도소득세 비과세 특례 판정 — 확정적 결정 트리 (LLM 판단 배제).

각 함수는 {"eligible": bool, "reasons": [...], "warnings": [...], "citations": [...]}를 반환한다.
판정 근거: wiki/tax/09·10 (law-api 원문 조회분) + rules/capital_gains.json.
"""
from .common import parse_date, full_years_between, add_years


def _verdict(eligible, reason, citations=None, warnings=None):
    return {"eligible": eligible, "reasons": [reason],
            "citations": citations or [], "warnings": warnings or []}


def check_basic_requirements(cg, rules):
    """1세대1주택 비과세 기본요건: 보유 2년 + (취득 당시 조정지역이면 거주 2년).

    특례(일시적2주택 등)도 '양도하는 주택 자체'가 이 요건을 충족해야 한다
    (§155①은 §154①을 적용하는 구조 — 법제처 10-0484, wiki/tax/10).
    """
    ex = rules["exemption"]
    acq = parse_date(cg.get("acquisition_date"))
    trf = parse_date(cg.get("transfer_date"))
    holding = cg.get("holding_years")
    if holding is None:
        holding = full_years_between(acq, trf)
    if holding is None:
        return _verdict(False, "취득일·양도일 또는 보유기간 미입력 — 판정 불가")
    if holding < ex["holding_years_required"]:
        return _verdict(False, "보유기간 {}년 < 2년 (소득세법 시행령 §154①)".format(holding),
                        [ex["basis"]])
    warnings = []
    if cg.get("acquired_in_regulated_area"):
        rule_start = parse_date(ex["residence_rule_start_date"])
        if acq is None or acq >= rule_start:
            res_years = cg.get("residence_years", 0) or 0
            if res_years < ex["residence_years_required"]:
                return _verdict(False,
                                "취득 당시 조정대상지역({} 이후 취득) — 거주 {}년 < 2년".format(
                                    ex["residence_rule_start_date"], res_years),
                                [ex["basis"]])
        else:
            warnings.append("2017-08-03 이전 취득분 — 거주요건 미적용 처리(기산일은 참고값, 부칙 미검증).")
    v = _verdict(True, "보유 2년 이상 충족" + (" + 거주 2년 이상 충족" if cg.get("acquired_in_regulated_area") else " (거주요건 비대상)"),
                 [ex["basis"]])
    v["warnings"] = warnings
    return v


def check_temporary_2house(cg, rules):
    """일시적 2주택 (시행령 §155①): 1-3 요건 + §18항 기한 도과 용서 사유."""
    t2 = rules["temporary_2house"]
    sc = cg.get("special_case", {})
    warnings = []

    if not sc.get("selling_prior_house", True):
        return _verdict(False, "신규주택을 먼저 양도 — 특례는 '종전주택' 양도에만 적용", [t2["basis"]])

    prior_acq = parse_date(sc.get("prior_house_acquisition_date") or cg.get("acquisition_date"))
    new_acq = parse_date(sc.get("new_house_acquisition_date"))
    trf = parse_date(cg.get("transfer_date"))
    if not (prior_acq and new_acq and trf):
        return _verdict(False, "종전주택 취득일·신규주택 취득일·양도일 미입력 — 판정 불가")

    # 대법원 2024두55426: 직전 상태가 '1주택'이어야 한다 (3주택→2주택 경로 배제)
    if cg.get("household_house_count", 2) > 2:
        return _verdict(False, "양도 당시 세대 주택수 3 이상 — 일시적 2주택 아님", [t2["basis"]])
    if sc.get("was_multi_house_before"):
        return _verdict(False,
                        "2주택 보유 중 신규 취득 후 처분으로 2주택이 된 경우 특례 배제 (대법원 2025.2.13. 2024두55426)",
                        [t2["basis"], "대법원 2024두55426"])

    # 요건 1: 종전주택 취득 후 1년 이상 경과하여 신규주택 취득
    if new_acq < add_years(prior_acq, t2["min_gap_years"]):
        return _verdict(False,
                        "종전주택 취득({}) 후 1년 미경과 시점에 신규주택 취득({}) — §154①1호·2호가목·3호 예외 비해당 전제".format(prior_acq, new_acq),
                        [t2["basis"]])

    # 요건 2: 신규주택 취득일부터 3년 이내 종전주택 양도 (§18항 사유 시 용서)
    deadline = add_years(new_acq, t2["disposal_years"])
    if trf > deadline:
        reason18 = sc.get("para18_reason")
        if reason18 in t2["para18_reasons"]:
            warnings.append("3년 기한({}) 도과했으나 §155⑱ 사유({})로 특례 유지 — '3년이 되는 날 현재' 사유 존재 증빙 필요(경매신청 접수증 등).".format(deadline, reason18))
        else:
            return _verdict(False,
                            "신규주택 취득일부터 3년({}) 내 미양도. §155⑱ 사유는 한정열거(경매신청·공매진행·캠코 매각의뢰·현금청산/수용 소송) — '안 팔려서'는 사유 아님".format(deadline),
                            [t2["basis"]])

    # 요건 3: 종전주택 자체의 기본요건 (보유2년 + 조정지역 취득 시 거주2년)
    basic = check_basic_requirements(cg, rules)
    if not basic["eligible"]:
        return _verdict(False, "종전주택 자체의 §154① 요건 미충족: " + basic["reasons"][0],
                        [t2["basis"]] + basic["citations"])
    warnings += basic["warnings"]

    if trf < parse_date(t2["old_law_watch_before"]):
        warnings.append("양도일이 2023-02-28(3년 완화 개정) 이전 — 구법(조정지역 1~2년+전입요건) 적용 가능성. 적용례 부칙 미검증이므로 수동 확인 필수(wiki/tax/10).")

    v = _verdict(True, "일시적 2주택 요건 충족(1년 경과 취득 + 3년 내 종전주택 양도 + 기본요건)", [t2["basis"]])
    v["warnings"] = warnings
    return v


def check_inheritance(cg, rules):
    """상속주택 특례 (§155②·③ — 2026-08-16 law-api 원문 검증).

    추가 입력(special_case):
      same_household_at_inheritance: bool — 상속개시 당시 상속인·피상속인 동일세대 여부
      merged_for_parent_care: bool — 동일세대가 동거봉양 합가로 형성된 경우(합가 전 보유 주택 예외)
      gifted_from_deceased_within_2y: bool — 일반주택이 상속개시일 소급 2년 내 피상속인에게서 증여받은 것
      minor_share_only: bool — 공동상속 소수지분만 보유(주택수 제외 → 특례 판정 불요)
    """
    r = rules["inheritance_special"]
    sc = cg.get("special_case", {})
    warnings = []
    if not sc.get("selling_general_house", False):
        return _verdict(False, "상속주택을 먼저 양도 — 특례는 '일반주택' 양도에 적용(상속주택 먼저 양도 시 과세)", [r["basis"]], warnings)
    if not sc.get("held_general_house_at_inheritance", False):
        return _verdict(False, "상속개시 당시 일반주택 미보유(상속 후 취득) — 특례 배제", [r["basis"]], warnings)
    if sc.get("gifted_from_deceased_within_2y"):
        return _verdict(False, "일반주택이 상속개시일부터 소급 2년 이내 피상속인으로부터 증여받은 주택 — 특례 배제(§155② 괄호)", [r["basis"]], warnings)
    if sc.get("same_household_at_inheritance") and not sc.get("merged_for_parent_care"):
        return _verdict(False, "상속개시 당시 상속인·피상속인 동일세대 — 특례 배제(동거봉양 합가 예외만 인정, §155② 단서)", [r["basis"]], warnings)
    if sc.get("minor_share_only"):
        warnings.append("공동상속 소수지분: 해당 상속주택은 주택수에서 제외되므로(§155③) 일반주택은 특례가 아니라 1세대1주택 기본 판정 대상일 수 있다.")
    if sc.get("deceased_had_multiple_houses"):
        warnings.append("피상속인이 2주택 이상 보유 — 특례는 선순위 1주택(①소유기간 최장 ②거주기간 최장 ③상속개시 당시 거주 ④기준시가 최고)에만 적용(§155② 각 호). 대상 주택이 선순위인지 확인 필요.")
    basic = check_basic_requirements(cg, rules)
    if not basic["eligible"]:
        return _verdict(False, "일반주택 자체의 §154① 요건 미충족: " + basic["reasons"][0], [r["basis"]], warnings)
    v = _verdict(True, "상속주택 특례 충족(상속 당시 보유 일반주택 먼저 양도 — 기간 제한 없음)", [r["basis"]])
    v["warnings"] = warnings + basic["warnings"]
    return v


def _check_union(cg, rules, rule_key, label, extra_check=None):
    """혼인합가·동거봉양 공통 로직: 합가일부터 N년 내 먼저 양도하는 주택.

    혼인 특례는 2024-11-12 개정으로 5년→10년 — 양도일이 개정일 전이면 구법 5년 적용.
    """
    r = rules[rule_key]
    sc = cg.get("special_case", {})
    warnings = []
    union = parse_date(sc.get("union_date"))
    trf = parse_date(cg.get("transfer_date"))
    if not (union and trf):
        return _verdict(False, "합가일(혼인일)·양도일 미입력 — 판정 불가", [r["basis"]], warnings)
    if extra_check:
        err = extra_check(sc)
        if err:
            return _verdict(False, err, [r["basis"]], warnings)
    years = r["years"]
    amend = parse_date(r.get("amendment_date")) if r.get("amendment_date") else None
    if amend and trf < amend:
        years = r["old_years"]
        warnings.append("양도일({})이 {} 개정 전 — 구법 기한 {}년 적용. 적용례 부칙 미조회이므로 경계 사안은 부칙 확인 필요.".format(trf, amend, years))
    if trf > add_years(union, years):
        return _verdict(False, "{}일({})부터 {}년 경과 후 양도 — 특례 배제".format(label, union, years),
                        [r["basis"]], warnings)
    basic = check_basic_requirements(cg, rules)
    if not basic["eligible"]:
        return _verdict(False, "양도주택 자체의 §154① 요건 미충족: " + basic["reasons"][0], [r["basis"]], warnings)
    v = _verdict(True, "{} 특례 충족({}년 내 양도 + 기본요건)".format(label, years), [r["basis"]])
    v["warnings"] = warnings + basic["warnings"]
    return v


def check_marriage(cg, rules):
    return _check_union(cg, rules, "marriage_special", "혼인합가")


def check_parent_care(cg, rules):
    def age_check(sc):
        age = sc.get("parent_min_age")
        if age is None:
            return "직계존속 연령 미입력 — 판정 불가"
        if age < rules["parent_care_special"]["parent_min_age"]:
            return ("직계존속 연령 {}세 < 60세 — 배제. 단 ①직계존속 중 다른 한 사람이 60세 이상이거나 "
                    "②요양급여 수급자(§155④ 각 호)면 예외 인정 — 해당 시 parent_min_age에 60세 이상인 분 기준으로 재입력".format(age))
        return None
    return _check_union(cg, rules, "parent_care_special", "동거봉양합가", age_check)


def determine_exemption(cg, rules):
    """비과세 여부 총괄 판정. cg = facts["capital_gains"]."""
    if cg.get("asset_type", "HOUSE") != "HOUSE":
        return _verdict(False, "주택이 아닌 자산({}) — 1세대1주택 비과세 비대상".format(cg.get("asset_type")))
    if cg.get("unregistered"):
        return _verdict(False, "미등기양도자산 — 비과세·장특공·기본공제 모두 배제(소득세법 §91①)")
    sc_type = (cg.get("special_case") or {}).get("type", "NONE")
    count = cg.get("household_house_count", 1)
    if sc_type == "NONE":
        if count == 1:
            return check_basic_requirements(cg, rules)
        return _verdict(False, "세대 주택수 {} — 특례 주장 없음, 비과세 배제".format(count))
    dispatch = {
        "TEMPORARY_2HOUSE": check_temporary_2house,
        "INHERITANCE": check_inheritance,
        "MARRIAGE": check_marriage,
        "PARENT_CARE": check_parent_care,
    }
    if sc_type not in dispatch:
        return _verdict(False, "알 수 없는 특례 유형: " + sc_type)
    return dispatch[sc_type](cg, rules)
