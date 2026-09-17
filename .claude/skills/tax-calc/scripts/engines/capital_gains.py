# -*- coding: utf-8 -*-
"""양도소득세 엔진 — 소득세법 §89·§95·§104 기반 확정적 계산.

입력(facts["capital_gains"]):
  asset_type: "HOUSE" | "PRESALE_RIGHT"(분양권) | "ASSOCIATION_RIGHT"(조합원입주권) | "OTHER"
  transfer_date, acquisition_date: "YYYY-MM-DD" (잔금 vs 등기 중 빠른 날)
  transfer_price, acquisition_price, necessary_expenses: int(원)
  holding_years, residence_years: 미입력 시 날짜로 산출 / 거주는 입력 필수
  acquired_in_regulated_area: bool — 취득 당시 조정지역 (거주요건 판정)
  regulated_at_transfer: bool — 양도 당시 조정지역 (다주택 중과 판정)
  household_house_count: int — 양도 당시 세대 주택수(양도주택 포함, 입주권·분양권 포함)
  unregistered: bool — 미등기양도
  pre_approval_gain: int|null — 입주권: 관리처분인가 전 양도차익(장특공 대상 구분)
  special_case: {type, ...} — special_cases.py 참조
"""
from .common import Result, load_rules, parse_date, full_years_between, progressive_quick, fmt_won, track_rule
from . import special_cases


def _ltsd_rate_table1(rules, holding):
    t1 = rules["ltsd"]["table1"]
    if holding < t1["min_years"]:
        return 0.0
    return min(holding * t1["per_year"], t1["cap"])


def _ltsd_rate_table2(rules, holding, residence):
    lt = rules["ltsd"]
    hold_rate = min(holding * lt["table2_hold"]["per_year"], lt["table2_hold"]["cap"]) \
        if holding >= lt["table2_hold"]["min_years"] else 0.0
    res_rate = min(residence * lt["table2_reside"]["per_year"], lt["table2_reside"]["cap"]) \
        if residence >= lt["table2_reside"]["min_years"] else 0.0
    return hold_rate + res_rate


def calculate(facts):
    rules = load_rules("capital_gains.json")
    cg = facts["capital_gains"]
    res = Result("양도소득세")

    tp = int(cg["transfer_price"])
    ap = int(cg["acquisition_price"])
    exp = int(cg.get("necessary_expenses", 0))
    asset = cg.get("asset_type", "HOUSE")
    acq_d = parse_date(cg.get("acquisition_date"))
    trf_d = parse_date(cg.get("transfer_date"))
    holding = cg.get("holding_years")
    if holding is None:
        holding = full_years_between(acq_d, trf_d)
    if holding is None:
        raise ValueError("보유기간 산출 불가 — 취득일·양도일 또는 holding_years 입력 필요")
    residence = cg.get("residence_years", 0) or 0

    gain = tp - ap - exp
    res.step("① 양도차익", fmt_won(gain), "소득세법 §95①",
             "양도가액 {} − 취득가액 {} − 필요경비 {}".format(fmt_won(tp), fmt_won(ap), fmt_won(exp)))
    res.warn("필요경비는 자본적 지출(샷시·확장·보일러 등)과 취득·양도 중개보수, 신고비용만 인정 — 도배·장판 등 수익적 지출은 배제(수동 검증 필요).")
    if gain <= 0:
        res.total = 0
        res.step("⑥ 총 부담세액", "0원", None, "양도차손 — 납부세액 없음(동일 자산그룹 내 통산 가능)")
        return res

    # ── ② 비과세 판정 (특례 결정 트리 — special_cases.py) ─────────
    verdict = special_cases.determine_exemption(cg, rules)
    for w in verdict["warnings"]:
        res.warn(w)
    for c in verdict["citations"]:
        res.cite(c)
    exempt = verdict["eligible"]
    ex_rule = rules["exemption"]
    res.step("② 비과세 판정", "충족" if exempt else "미충족", ex_rule["basis"], verdict["reasons"][0])

    threshold = ex_rule["high_price_threshold"]
    if exempt and tp <= threshold:
        res.total = 0
        res.step("⑥ 총 부담세액", "0원", ex_rule["basis"], "양도가액 12억 이하 전액 비과세")
        res.extra = {"비과세": True}
        return res

    # ── ③ 과세대상 양도차익 (고가주택 안분) + 장특공 ─────────────
    surcharge = 0.0
    heavy_applied = False
    hv = rules["heavy"]
    if exempt:
        taxable_gain = int(gain * (tp - threshold) / tp)
        res.step("③-1 고가주택 안분 과세차익", fmt_won(taxable_gain), ex_rule["basis"],
                 "전체 차익 × (양도가액−12억)/양도가액")
    else:
        taxable_gain = gain
        # 다주택 조정지역 중과 판정 (유예 종료: 2026-05-09 양도분까지 배제)
        if (asset == "HOUSE" and cg.get("regulated_at_transfer")
                and cg.get("household_house_count", 1) >= 2 and not cg.get("unregistered")):
            suspended = (trf_d is not None
                         and trf_d <= parse_date(hv["suspension_last_transfer_date"])
                         and holding >= hv["suspension_requires_holding_years"])
            if suspended:
                res.step("③-0 다주택 중과", "한시 배제(유예) 적용", hv["basis"],
                         "2026-05-09까지 양도분 + 보유 2년 이상 (시행령 §167의3①12호의2)")
            else:
                heavy_applied = True
                surcharge = hv["surcharge_2house"] if cg["household_house_count"] == 2 else hv["surcharge_3plus"]
                res.step("③-0 다주택 중과", "+{}%p 가산·장특공 배제".format(int(surcharge * 100)), hv["basis"],
                         "유예 종료(2026-05-10 이후 양도분) — 조정지역 {}주택".format(cg["household_house_count"]))
                if trf_d and trf_d <= parse_date(hv["grace_watch_until"]):
                    res.warn("토지거래허가·매매계약 관련 경과조치(최장 2026-11-09)에 해당하면 중과 배제 가능 — 시행령 §167의3①12호의2 나·다목 확인 필요(wiki/tax/11).")
        track_rule(res, hv)

    # 장기보유특별공제
    lt = rules["ltsd"]
    ltsd_rate = 0.0
    ltsd_base = taxable_gain
    if cg.get("unregistered"):
        res.step("③-2 장기보유특별공제", "배제", rules["unregistered"]["basis"], "미등기양도자산")
        track_rule(res, rules["unregistered"])
    elif heavy_applied:
        res.step("③-2 장기보유특별공제", "배제", hv["basis"], "중과 대상은 장특공 배제(§95② 본문)")
    elif asset == "PRESALE_RIGHT":
        res.step("③-2 장기보유특별공제", "비대상", lt["basis"], "분양권은 토지·건물이 아님")
    elif asset == "ASSOCIATION_RIGHT":
        pre_gain = cg.get("pre_approval_gain")
        if pre_gain is None:
            res.step("③-2 장기보유특별공제", "미적용(자료 부족)", lt["basis"],
                     "입주권은 관리처분인가 '전' 양도차익에만 적용(조심 2022서8211) — pre_approval_gain 입력 시 반영")
            res.warn("입주권 장특공: 관리처분인가 전/후 양도차익 구분 자료가 없어 공제를 0으로 처리 — 세액이 과대계상될 수 있다. 인가 전 차익을 확인해 재계산 권장.")
        else:
            ltsd_base = min(int(pre_gain), taxable_gain)
            ltsd_rate = _ltsd_rate_table1(rules, holding)
            res.step("③-2 장특공(입주권·인가 전 차익분)", "{:.0f}%".format(ltsd_rate * 100), lt["basis"],
                     "표1 — 인가 전 차익 {}에만 적용".format(fmt_won(ltsd_base)))
    elif holding >= lt["table1"]["min_years"]:
        if exempt or (cg.get("household_house_count", 1) == 1):
            if residence >= lt["table2_requires_residence_years"]:
                ltsd_rate = _ltsd_rate_table2(rules, holding, residence)
                res.step("③-2 장기보유특별공제(표2)", "{:.0f}%".format(ltsd_rate * 100), lt["basis"],
                         "보유 {}년 + 거주 {}년 (각 연 4%, 합산 최대 80%)".format(holding, residence))
            else:
                ltsd_rate = _ltsd_rate_table1(rules, holding)
                res.step("③-2 장기보유특별공제(표1)", "{:.0f}%".format(ltsd_rate * 100), lt["basis"],
                         "거주 2년 미만 → 표2 배제, 표1 적용(최대 30%) — wiki/tax/12 함정")
        else:
            ltsd_rate = _ltsd_rate_table1(rules, holding)
            res.step("③-2 장기보유특별공제(표1)", "{:.0f}%".format(ltsd_rate * 100), lt["basis"],
                     "보유 {}년 × 연 2%".format(holding))
    else:
        res.step("③-2 장기보유특별공제", "0% (보유 3년 미만)", lt["basis"])
    track_rule(res, lt)

    ltsd_amount = int(ltsd_base * ltsd_rate)
    income = taxable_gain - ltsd_amount
    bd = rules["basic_deduction"]
    deduction = 0 if cg.get("unregistered") else bd["amount"]
    track_rule(res, bd)
    base = max(income - deduction, 0)
    res.step("④ 과세표준", fmt_won(base), bd["basis"],
             "양도소득금액 {} − 기본공제 {} (연 1회)".format(fmt_won(income), fmt_won(deduction)))

    # ── ⑤ 세율 적용 (비교과세: 해당 세율 중 큰 세액 — §104① 후단) ──
    br = rules["brackets"]
    st = rules["short_term"]
    track_rule(res, br)
    candidates = []
    if cg.get("unregistered"):
        candidates.append((int(base * rules["unregistered"]["rate"]), "미등기 70%", rules["unregistered"]["basis"]))
    elif asset == "PRESALE_RIGHT":
        track_rule(res, st)
        rate = st["presale_under_1y"] if holding < 1 else st["presale_over_1y"]
        candidates.append((int(base * rate), "분양권 {}%".format(int(rate * 100)), st["basis"]))
    else:
        tax_prog, applied_rate = progressive_quick(base, br["table"], surcharge)
        label = "기본누진 {:.0f}%".format(applied_rate * 100) + ("(중과 +{}%p 포함)".format(int(surcharge * 100)) if surcharge else "")
        candidates.append((tax_prog, label, br["basis"] + (" · " + hv["basis"] if surcharge else "")))
        if asset in ("HOUSE", "ASSOCIATION_RIGHT") and holding < 2:
            track_rule(res, st)
            rate = st["house_under_1y"] if holding < 1 else st["house_1_to_2y"]
            candidates.append((int(base * rate), "단기 {}%".format(int(rate * 100)), st["basis"]))

    tax, rate_label, rate_basis = max(candidates, key=lambda c: c[0])
    if len(candidates) > 1:
        res.step("⑤-0 비교과세", " vs ".join("{}({})".format(c[1], fmt_won(c[0])) for c in candidates),
                 "소득세법 §104① 후단·§104⑦ 후단", "큰 세액 적용")
    res.step("⑤ 산출세액", fmt_won(tax), rate_basis, rate_label)

    local = int(tax * rules["local_income_tax_ratio"])
    res.step("⑤-1 지방소득세", fmt_won(local), "지방세법 §103의3", "양도소득세의 10%")

    total = tax + local
    res.total = total
    res.step("⑥ 총 부담세액", fmt_won(total), None, "양도소득세 + 지방소득세")
    res.extra = {"양도차익": gain, "과세대상차익": taxable_gain, "장특공률": ltsd_rate,
                 "장특공액": ltsd_amount, "과세표준": base, "산출세액": tax,
                 "지방소득세": local, "비과세": False, "중과적용": heavy_applied}
    res.warn(rules["filing_deadline"] + " — 1천만원 초과 시 분납 가능(참고값).")
    res.warn("10원 미만 절사 등 단수처리 미적용 — 신고서 작성 시 별도 반영 필요.")
    return res
