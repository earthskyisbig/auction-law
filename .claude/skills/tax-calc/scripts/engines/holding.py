# -*- coding: utf-8 -*-
"""보유세 엔진 — 재산세(지방세법, 참고값) + 종합부동산세(종부세법, wiki/tax/05 검증).

입력(facts["holding"]):
  taxpayer: "INDIVIDUAL" | "CORPORATION"
  official_prices: [int, ...] — 납세의무자(인별) 보유 주택의 공시가격 목록
  house_count: int — 인별 주택수(종부세 세율표 선택 — 2주택 이하 vs 3주택 이상, 조정지역 무관)
  is_one_household_one_house: bool — 1세대1주택자 여부(단독명의 12억 공제·세액공제·재산세 특례)
  joint_special_applied: bool — 부부공동명의 1주택 특례 신청(§10의2, 9.16~9.30) → 1세대1주택자로 계산
  owner_age: int|null — 고령자 세액공제
  holding_years: int|null — 장기보유 세액공제
  prev_year_total_tax: int|null — 직전년도 총세액상당액(세부담상한 150%)
  exclusion_prices: [int, ...] — 합산배제 주택 공시가격(등록임대 등 — 합산에서 제외)

과세기준일: 매년 6월 1일 소유자(잔금일 vs 등기접수일 중 빠른 날).
"""
from .common import Result, load_rules, progressive_cumulative, fmt_won, track_rule


def _pick(value, table):
    """[[임계값, 결과], ...] 오름차순 테이블에서 value 이상인 마지막 결과."""
    out = 0.0
    for threshold, v in table:
        if value >= threshold:
            out = v
    return out


def _ratio_for_price(price, table):
    for limit, ratio in table:
        if limit is None or price <= limit:
            return ratio
    return table[-1][1]


def calculate(facts):
    rules = load_rules("holding.json")
    h = facts["holding"]
    res = Result("보유세(재산세+종부세)")
    pt = rules["property_tax"]
    ct = rules["cret"]
    track_rule(res, pt)
    track_rule(res, ct)

    prices = [int(p) for p in h.get("official_prices", [])]
    if not prices:
        raise ValueError("official_prices(공시가격 목록) 입력 필요")
    one_house = bool(h.get("is_one_household_one_house")) and len(prices) == 1
    corp = h.get("taxpayer") == "CORPORATION"

    # ── 재산세 (물건별 과세) — 참고값 ──────────────────────────
    prop_tax_sum = 0
    city_sum = 0
    edu_sum = 0
    for i, price in enumerate(prices):
        if one_house and not corp:
            ratio = _ratio_for_price(price, pt["fair_market_ratio_one_house"])
        else:
            ratio = pt["fair_market_ratio_default"]
        base = int(price * ratio)
        special = one_house and not corp and price <= pt["special_price_cap"]
        brackets = pt["brackets_special_one_house"] if special else pt["brackets_standard"]
        tax = progressive_cumulative(base, brackets)
        city = int(base * pt["city_area_rate"])
        edu = int(tax * pt["local_education_ratio"])
        prop_tax_sum += tax
        city_sum += city
        edu_sum += edu
        res.step("재산세 [주택{}] 과표 {} (공정비율 {:.0%}{})".format(
            i + 1, fmt_won(base), ratio, "·특례세율" if special else ""),
            fmt_won(tax + city + edu), pt["basis"],
            "본세 {} + 도시지역분 {} + 지방교육세 {}".format(fmt_won(tax), fmt_won(city), fmt_won(edu)))
    prop_total = prop_tax_sum + city_sum + edu_sum
    res.step("재산세 합계", fmt_won(prop_total), pt["basis"], "7월·9월 1/2씩 분납")

    # ── 종합부동산세 (인별 전국 합산) — wiki/tax/05 검증값 ───────
    excl = [int(p) for p in h.get("exclusion_prices", [])]
    if excl:
        res.warn("합산배제 주택 {}건은 종부세 합산에서 제외 처리 — 9.16~9.30 합산배제 신고 요건(시행령 §3⑨) 확인 필요.".format(len(excl)))
    total_price = sum(prices)

    if corp:
        deduction = ct["deduction_corporation"]
        ded_label = "법인 0원"
    elif one_house or h.get("joint_special_applied"):
        deduction = ct["deduction_one_house_single"]
        ded_label = "1세대1주택자 12억" + ("(부부공동명의 특례 신청)" if h.get("joint_special_applied") else "")
        if h.get("joint_special_applied"):
            res.warn("부부공동명의 1주택자 특례는 9.16~9.30 관할세무서장 신청 요건(§10의2②) — 미신청 시 각자 9억 공제로 계산해야 한다.")
    else:
        deduction = ct["deduction_default"]
        ded_label = "일반 9억(인별)"

    cret_base = max(total_price - deduction, 0)
    cret_base = int(cret_base * ct["fair_market_ratio"])
    res.step("종부세 과세표준", fmt_won(cret_base), ct["basis"],
             "(공시합산 {} − 공제 {} [{}]) × 공정시장가액비율 60%".format(
                 fmt_won(total_price), fmt_won(deduction), ded_label))

    if cret_base <= 0:
        res.total = prop_total
        res.step("종부세", "0원", ct["basis"], "과세표준 0 이하")
        res.step("총 보유세", fmt_won(prop_total), None, "재산세만 부담")
        res.extra = {"재산세": prop_total, "종부세": 0}
        return res

    count = int(h.get("house_count", len(prices)))
    if corp:
        rate = ct["corporation_ge3"] if count >= 3 else ct["corporation_le2"]
        raw = int(cret_base * rate)
        res.step("종부세 산출세액(법인 단일세율 {:.1%})".format(rate), fmt_won(raw), ct["basis"])
    else:
        brackets = ct["brackets_ge3"] if count >= 3 else ct["brackets_le2"]
        raw = progressive_cumulative(cret_base, brackets)
        res.step("종부세 산출세액({}주택 세율표)".format("3+" if count >= 3 else "2이하"),
                 fmt_won(raw), ct["basis"], "조정대상지역 여부 무관(주택수 기준)")

    # 재산세액 공제 (§9③) — 근사 산식
    overlap_base = int(cret_base * pt["fair_market_ratio_default"])
    overlap = min(progressive_cumulative(overlap_base, pt["brackets_standard"]), raw, prop_tax_sum)
    res.step("재산세액 공제(중복분)", "-" + fmt_won(overlap), "종부세법 §9③",
             "근사 산식 — 시행령 §4의2 정확 산식과 차이 가능")
    res.warn("재산세액 공제는 근사 산식으로 계산 — 실제 고지세액은 시행령 §4의2 산식에 따라 다를 수 있다.")
    after = raw - overlap

    # 1세대1주택자 세액공제 (고령자 + 장기보유, 합산 80% 한도)
    credit_rate = 0.0
    if (one_house or h.get("joint_special_applied")) and not corp:
        age_credit = _pick(h.get("owner_age") or 0, ct["age_credit"])
        hold_credit = _pick(h.get("holding_years") or 0, ct["holding_credit"])
        credit_rate = min(age_credit + hold_credit, ct["credit_cap"])
        if credit_rate > 0:
            res.step("1세대1주택 세액공제", "-{:.0f}%".format(credit_rate * 100), ct["basis"],
                     "고령자 {:.0f}% + 장기보유 {:.0f}% (합산 한도 80%)".format(age_credit * 100, hold_credit * 100))
        res.warn("세액공제는 거주자 한정(비거주자 배제 — 조심2009서2720). §8④ 의제 1주택(상속·지방저가 등)은 해당분 산출세액이 공제 기초에서 제외된다.")
    cret_tax = int(after * (1 - credit_rate))

    # 세부담상한 150%
    prev = h.get("prev_year_total_tax")
    if prev:
        cap = int(prev * ct["burden_cap_ratio"])
        combined = prop_tax_sum + cret_tax
        if combined > cap:
            cret_tax = max(cap - prop_tax_sum, 0)
            res.step("세부담상한 적용", fmt_won(cret_tax), "종부세법 §10",
                     "직전년도 총세액상당액 {} × 150% 한도(단순 적용 — 정확 산식 별도)".format(fmt_won(prev)))
    else:
        res.warn("직전년도 총세액상당액 미입력 — 세부담상한(150%, §10) 미적용. 상한 해당 시 세액이 줄 수 있다.")

    rural = int(cret_tax * ct["rural_special_ratio"])
    res.warn("농어촌특별세(종부세의 20%)는 " + ct["rural_special_verified"])
    res.step("종부세 + 농어촌특별세", fmt_won(cret_tax + rural), ct["basis"],
             "본세 {} + 농특세 {} (12월 1~15일 납부)".format(fmt_won(cret_tax), fmt_won(rural)))

    total = prop_total + cret_tax + rural
    res.total = total
    res.step("총 보유세", fmt_won(total), None, "재산세 합계 + 종부세 + 농특세")
    res.extra = {"재산세": prop_total, "종부세": cret_tax, "농특세": rural,
                 "종부세과세표준": cret_base, "세액공제율": credit_rate}
    res.warn("재산세 주의: ①1세대1주택 공정시장가액비율 43~45%는 '2026년도 납세의무 성립분' 문언(영 §109①2호) — 매년 시행령 개정 확인 ②표준세율은 조례로 ±50% 가감 가능(§111③) ③과세표준상한제(§110③)·재산세 세부담상한(§122) 미구현 — 급등 지역은 실제 고지액이 더 낮을 수 있음.")
    return res
