# -*- coding: utf-8 -*-
"""취득세 엔진 — 지방세법 §11·§13의2·§13의3 기반 확정적 판정·계산.

입력(facts["acquisition"]):
  acquirer: "INDIVIDUAL" | "CORPORATION"
  cause: "PURCHASE"(매매) | "AUCTION"(경매낙찰=유상승계취득) | "GIFT"(증여) |
         "INHERITANCE"(상속) | "ORIGINAL"(신축·원시취득)
  property: "HOUSE" | "OFFICETEL_RESIDENTIAL" | "OFFICETEL_COMMERCIAL" |
            "COMMERCIAL" | "LAND" | "FARMLAND"
  price: int — 취득당시가액(원). 경매는 낙찰가.
  sigajun_price: int|null — 시가표준액(저가주택 중과제외·증여 중과 판정용)
  is_regulated_area: bool — 취득 당시 조정대상지역 여부 (국토부 고시 — 입력 필수)
  is_metropolitan: bool — 수도권 여부 (저가주택 1억/2억 기준)
  in_redevelopment_zone: bool — 정비구역·소규모주택정비 사업시행구역 소재 여부
  household_house_count_before: int — 취득 직전 세대 주택수
      (조합원입주권·주택분양권·주택과세 오피스텔 포함 — §13의3)
  temporary_2house: bool — 일시적 2주택 주장 여부(이사·학업·취업·직장이전 등 사유 전제)
  exclusive_area_m2: float|null — 전용면적(농특세 85㎡ 판정)
  first_time_buyer: bool — 생애최초 감면 신청
  acquired_via_presale_right: bool — 분양권에 의한 주택 취득 여부(기산일 함정 경고용)
  gift_from_one_house_household: bool — 1세대1주택자로부터 배우자·직계존비속 증여 여부
"""
from .common import Result, load_rules, track_rule, fmt_won


def _standard_house_rate(price, rule):
    """주택 유상취득 표준세율(1~3%, 6~9억 슬라이딩). §11①8호."""
    if price <= rule["low_threshold"]:
        return rule["low_rate"]
    if price <= rule["high_threshold"]:
        # (취득당시가액 × 2/3억 − 3)%, 소수점 다섯째자리 반올림(넷째자리까지)
        pct = price * 2 / 300000000 - 3
        return round(pct, 4) / 100
    return rule["high_rate"]


def calculate(facts):
    rules = load_rules("acquisition.json")
    f = facts["acquisition"]
    res = Result("취득세")
    price = int(f["price"])
    prop = f.get("property", "HOUSE")
    cause = f.get("cause", "PURCHASE")
    is_house = prop == "HOUSE"

    res.step("① 과세표준(취득당시가액)", fmt_won(price), "지방세법 §10의2 이하",
             "경매는 낙찰가(유상승계취득)" if cause == "AUCTION" else None)

    rate = None
    heavy_level = None  # None | 8 | 12
    rate_basis = None

    # ── 무상·원시취득 분기 ──────────────────────────────
    if cause == "INHERITANCE":
        r = rules["inheritance"]
        track_rule(res, r)
        rate = r["farmland"] if prop == "FARMLAND" else r["non_farmland"]
        rate_basis = r["basis"]
        res.warn("상속 취득 주택은 상속개시일부터 5년간 다른 주택 취득세 중과 판정 시 주택수에서 제외된다(영 §28의4⑥3호 — wiki/tax/01).")
    elif cause == "ORIGINAL":
        r = rules["original"]
        track_rule(res, r)
        rate = r["rate"]
        rate_basis = r["basis"]
    elif cause == "GIFT":
        r = rules["gift"]
        track_rule(res, r)
        sigajun = f.get("sigajun_price") or price
        if (is_house and f.get("is_regulated_area")
                and sigajun >= r["regulated_price_threshold"]
                and not f.get("gift_from_one_house_household")):
            rate = r["regulated_heavy_rate"]
            heavy_level = 12
            rate_basis = "지방세법 §13의2②"
            res.warn("증여 중과 기준금액 3억원(시가표준액)은 시행령(§28의6) 미조회 참고값 — law-api-query로 확인 필요.")
        else:
            rate = r["standard_rate"]
            rate_basis = "지방세법 §11①2호"
            if f.get("gift_from_one_house_household"):
                res.warn("1세대1주택자 소유 주택의 배우자·직계존비속 무상취득 중과 제외 — 시행령 요건 원문 확인 필요(§13의2② 단서).")

    # ── 유상취득(매매·경매) ─────────────────────────────
    elif prop in ("COMMERCIAL", "LAND", "OFFICETEL_COMMERCIAL", "OFFICETEL_RESIDENTIAL", "FARMLAND"):
        r = rules["non_house"]
        track_rule(res, r)
        rate = r["farmland_purchase"] if prop == "FARMLAND" else r["general"]
        rate_basis = r["basis"]
        if prop.startswith("OFFICETEL"):
            res.warn("오피스텔은 취득 시점엔 4%(건축물 기준)이나, 주택분 재산세로 과세되는 오피스텔은 이후 다른 주택 취득 시 주택수에 가산된다(§13의3 — wiki/tax/01).")
    else:
        # 주택 유상취득 — 주택수·지역 조합 판정
        acquirer = f.get("acquirer", "INDIVIDUAL")
        heavy = rules["heavy"]
        std = rules["standard_house"]
        count_after = int(f.get("household_house_count_before", 0)) + 1
        regulated = bool(f.get("is_regulated_area"))

        if f.get("acquired_via_presale_right"):
            res.warn("분양권에 의한 주택 취득: 주택수 판정 기산일은 주택 취득일이 아니라 '분양권 취득일(분양계약일)'이다(영 §28의4① 후단). 아래 판정은 입력된 주택수를 그대로 신뢰한 결과.")

        if acquirer == "CORPORATION":
            track_rule(res, heavy)
            rate, heavy_level, rate_basis = heavy["corporation"], 12, heavy["basis"] + " 1호(법인)"
            res.step("② 판정: 법인의 주택 유상취득", "주택수·지역 무관 12% 중과", rate_basis)
        else:
            # 저가주택 중과 제외 (시가표준액 기준, 정비구역 소재는 제외)
            low = rules["low_price_exclusion"]
            sigajun = f.get("sigajun_price")
            low_price_ok = False
            if sigajun is not None:
                cap = low["metropolitan_cap"] if f.get("is_metropolitan", True) else low["non_metropolitan_cap"]
                if sigajun <= cap and not f.get("in_redevelopment_zone"):
                    low_price_ok = True
                elif sigajun <= cap and f.get("in_redevelopment_zone"):
                    res.warn("시가표준액이 저가주택 기준 이하지만 정비구역·사업시행구역 소재라 중과 제외에서 배제된다(영 §28의2 1호 단서) — 재개발 구역 저가빌라 함정.")

            temp2 = bool(f.get("temporary_2house")) and count_after == 2

            if low_price_ok:
                track_rule(res, low)
                rate = _standard_house_rate(price, std)
                rate_basis = std["basis"] + " (저가주택 중과 제외: " + low["basis"] + ")"
                res.step("② 판정: 저가주택 중과 제외", "시가표준액 {} ≤ 기준".format(fmt_won(sigajun)), low["basis"])
            elif temp2 and regulated:
                track_rule(res, rules["temporary_2house"])
                rate = _standard_house_rate(price, std)
                rate_basis = std["basis"] + " (일시적 2주택: " + rules["temporary_2house"]["basis"] + ")"
                res.warn("일시적 2주택 사후요건: 신규주택 취득일부터 3년 내 종전 주택등 처분 + 이사·학업·취업·직장이전 등 사유 필요(영 §28의5). 미이행 시 8%와의 차액 + 가산세 추징.")
            elif count_after <= 1 or (count_after == 2 and not regulated):
                rate = _standard_house_rate(price, std)
                rate_basis = std["basis"]
            elif count_after == 2 and regulated:
                track_rule(res, heavy)
                rate, heavy_level, rate_basis = heavy["regulated_2house"], 8, heavy["basis"] + " 2호"
            elif count_after == 3:
                track_rule(res, heavy)
                if regulated:
                    rate, heavy_level, rate_basis = heavy["regulated_3plus"], 12, heavy["basis"] + " 3호"
                else:
                    rate, heavy_level, rate_basis = heavy["non_regulated_3house"], 8, heavy["basis"] + " 2호 후단"
            else:  # 4주택 이상
                track_rule(res, heavy)
                rate, heavy_level, rate_basis = heavy["regulated_3plus"], 12, heavy["basis"] + " 3호"
            track_rule(res, std)
            res.step("② 판정: 취득 후 세대 주택수 {}·{}".format(
                count_after, "조정대상지역" if regulated else "비조정지역"),
                "적용세율 {:.4f}%".format(rate * 100), rate_basis)
            res.warn("세대 주택수는 조합원입주권·주택분양권·주택과세 오피스텔·신탁주택(위탁자)을 포함해 산정해야 한다(§13의3). 입력값이 이를 반영했는지 확인.")

    if rate is None:
        raise ValueError("세율 판정 실패 — 입력값 확인: property={}, cause={}".format(prop, cause))

    main_tax = int(price * rate)
    res.step("③ 산출세액(본세)", fmt_won(main_tax), rate_basis, "세율 {:.4f}%".format(rate * 100))

    # ── 감면(생애최초, 지특법 §36의3) ──────────────────
    reduction = 0
    if f.get("first_time_buyer") and is_house and cause in ("PURCHASE", "AUCTION"):
        ftb = rules["first_time_buyer"]
        track_rule(res, ftb)
        if price <= ftb["price_cap"]:
            # 소형·저가(60㎡ 이하 & 3억/수도권 6억 이하 아파트 제외 공동주택 등)·인구감소지역 → 300만 한도
            small_cheap = bool(f.get("first_time_small_cheap"))
            cap = ftb["reduction_cap_small_cheap"] if small_cheap else ftb["reduction_cap_default"]
            reduction = min(main_tax, cap)
            res.step("④ 생애최초 감면", "-" + fmt_won(reduction), ftb["basis"],
                     "한도 {} ({}) — {}까지".format(fmt_won(cap),
                                                  "소형·저가/인구감소지역" if small_cheap else "일반",
                                                  ftb["sunset"]))
            res.warn("생애최초 감면 사후요건: 취득일부터 3년 내 매각·증여(배우자 제외)·임대 등 타용도 사용 시 추징(지특법 §36의3④). 본인·배우자 모두 주택 소유 이력 없어야 하며 미성년자·부담부증여는 제외.")
        else:
            res.warn("생애최초 감면: 취득당시가액이 기준({}) 초과로 미적용 처리.".format(fmt_won(ftb["price_cap"])))

    # ── 부가세목: 지방교육세 ────────────────────────────
    edu_rule = rules["local_education_tax"]
    track_rule(res, edu_rule)
    if heavy_level:
        edu = int(price * edu_rule["heavy_flat"])
        edu_note = "중과 시 과세표준의 0.4% 고정"
    elif is_house and cause in ("PURCHASE", "AUCTION"):
        edu = int(price * rate * 0.5 * 0.2)
        edu_note = "취득세율×50%×20%"
    else:
        edu = int(price * max(rate - 0.02, 0) * 0.2)
        edu_note = "(세율−2%)×20%"
    res.step("⑤-1 지방교육세", fmt_won(edu), edu_rule["basis"], edu_note)

    # ── 부가세목: 농어촌특별세 ──────────────────────────
    rst_rule = rules["rural_special_tax"]
    rst = 0
    area = f.get("exclusive_area_m2")
    if is_house:
        if area is None:
            res.warn("전용면적 미입력 — 농어촌특별세(85㎡ 초과 시 부과)를 0으로 처리했다. 면적 확인 필요.")
        elif area > rst_rule["exempt_area_m2"]:
            track_rule(res, rst_rule)
            key = {None: "standard", 8: "heavy_8", 12: "heavy_12"}[heavy_level]
            rst = int(price * rst_rule[key])
            res.step("⑤-2 농어촌특별세", fmt_won(rst), rst_rule["basis"], "전용 {}㎡ > 85㎡".format(area))
    elif prop in ("COMMERCIAL", "LAND", "OFFICETEL_COMMERCIAL", "OFFICETEL_RESIDENTIAL"):
        track_rule(res, rst_rule)
        rst = int(price * rst_rule["standard"])
        res.step("⑤-2 농어촌특별세", fmt_won(rst), rst_rule["basis"])

    total = main_tax - reduction + edu + rst
    res.total = total
    res.step("⑥ 총 부담세액", fmt_won(total), None, "본세 − 감면 + 지방교육세 + 농특세")
    res.extra = {"본세": main_tax, "적용세율": rate, "중과단계": heavy_level,
                 "감면": reduction, "지방교육세": edu, "농어촌특별세": rst}
    filing = rules["filing"]
    deadline = {"INHERITANCE": filing["inheritance"], "GIFT": filing["gift"]}.get(cause, filing["onerous"])
    res.warn("신고·납부 기한: {} ({}). 조정대상지역 지정 현황은 국토부 고시로 반드시 별도 확인(wiki/tax/01 조사한계).".format(deadline, filing["basis"]))
    res.warn("10원 미만 절사 등 단수처리 미적용 — 신고서 작성 시 별도 반영 필요.")
    return res
