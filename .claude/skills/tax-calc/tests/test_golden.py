# -*- coding: utf-8 -*-
"""골든 테스트 — 손으로 검산한 기대값과 엔진 출력을 대조한다.

실행: python -m unittest discover -s .claude/skills/tax-calc/tests -v
새 케이스 추가 시 반드시 기대값을 수기 검산(조문 근거 포함)해 주석으로 남길 것.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from engines import acquisition, holding, capital_gains  # noqa: E402


class TestAcquisition(unittest.TestCase):
    def base(self, **kw):
        f = {"acquirer": "INDIVIDUAL", "cause": "PURCHASE", "property": "HOUSE",
             "price": 500000000, "is_regulated_area": False, "is_metropolitan": True,
             "household_house_count_before": 0, "exclusive_area_m2": 84.0}
        f.update(kw)
        return {"acquisition": f}

    def test_first_house_500m(self):
        # 무주택→1주택, 5억, 85㎡ 이하: 취득세 1% = 500만, 교육세 1%×0.5×0.2=0.1% = 50만, 농특세 0
        r = acquisition.calculate(self.base())
        self.assertEqual(r.extra["본세"], 5000000)
        self.assertEqual(r.extra["지방교육세"], 500000)
        self.assertEqual(r.extra["농어촌특별세"], 0)
        self.assertEqual(r.total, 5500000)

    def test_sliding_750m(self):
        # 7.5억: 세율 = 7.5×2/3 − 3 = 2.0% → 1,500만. §11①8호 나목
        r = acquisition.calculate(self.base(price=750000000))
        self.assertAlmostEqual(r.extra["적용세율"], 0.02)
        self.assertEqual(r.extra["본세"], 15000000)

    def test_sliding_rounding(self):
        # 7억: 7×2/3−3 = 1.66666...% → 넷째자리 반올림 1.6667% → 11,666,900원
        r = acquisition.calculate(self.base(price=700000000))
        self.assertAlmostEqual(r.extra["적용세율"], 0.016667)
        self.assertEqual(r.extra["본세"], int(700000000 * 0.016667))

    def test_regulated_2nd_house_heavy(self):
        # 조정지역 2주택째(일시적 아님), 6억: 8% = 4,800만, 교육세 0.4% = 240만
        r = acquisition.calculate(self.base(price=600000000, is_regulated_area=True,
                                            household_house_count_before=1))
        self.assertEqual(r.extra["중과단계"], 8)
        self.assertEqual(r.extra["본세"], 48000000)
        self.assertEqual(r.extra["지방교육세"], 2400000)

    def test_temporary_2house_standard_rate(self):
        # 조정지역 2주택째지만 일시적 2주택 → 표준세율 1% (6억 이하)
        r = acquisition.calculate(self.base(price=600000000, is_regulated_area=True,
                                            household_house_count_before=1, temporary_2house=True))
        self.assertIsNone(r.extra["중과단계"])
        self.assertEqual(r.extra["본세"], 6000000)
        self.assertTrue(any("3년" in w for w in r.warnings))

    def test_corporation_flat_12(self):
        r = acquisition.calculate(self.base(acquirer="CORPORATION", price=300000000))
        self.assertEqual(r.extra["중과단계"], 12)
        self.assertEqual(r.extra["본세"], 36000000)

    def test_non_regulated_3rd_8pct(self):
        # 비조정 3주택째: 8% (§13의2①2호 후단 — "비조정은 중과 없음"은 오해)
        r = acquisition.calculate(self.base(price=400000000, household_house_count_before=2))
        self.assertEqual(r.extra["중과단계"], 8)

    def test_low_price_exclusion(self):
        # 비수도권 시가표준 1.5억(≤2억), 조정 3주택째 → 중과 배제, 표준 1%
        r = acquisition.calculate(self.base(price=150000000, sigajun_price=150000000,
                                            is_regulated_area=True, is_metropolitan=False,
                                            household_house_count_before=2))
        self.assertIsNone(r.extra["중과단계"])
        self.assertEqual(r.extra["본세"], 1500000)

    def test_low_price_in_redev_zone_heavy(self):
        # 같은 조건이지만 정비구역 소재 → 저가주택 제외 배제 → 조정 3주택 12% (재개발 빌라 함정)
        r = acquisition.calculate(self.base(price=150000000, sigajun_price=150000000,
                                            is_regulated_area=True, is_metropolitan=False,
                                            household_house_count_before=2, in_redevelopment_zone=True))
        self.assertEqual(r.extra["중과단계"], 12)

    def test_commercial_4pct(self):
        # 상가 4%: 본세 2,000만, 교육세 (4−2)%×20%=0.4% 200만, 농특세 0.2% 100만
        r = acquisition.calculate(self.base(property="COMMERCIAL", price=500000000))
        self.assertEqual(r.extra["본세"], 20000000)
        self.assertEqual(r.extra["지방교육세"], 2000000)
        self.assertEqual(r.extra["농어촌특별세"], 1000000)

    def test_inheritance_rates(self):
        # 상속 농지 외 2.8% (§11①1호나목, 2026-08-16 원문 검증)
        r = acquisition.calculate(self.base(cause="INHERITANCE", price=300000000))
        self.assertEqual(r.extra["본세"], 8400000)
        # 상속 농지 2.3%
        r2 = acquisition.calculate(self.base(cause="INHERITANCE", property="FARMLAND", price=300000000))
        self.assertEqual(r2.extra["본세"], 6900000)

    def test_first_time_buyer_caps(self):
        # 생애최초 일반: 5억 × 1% = 500만 → 200만 공제 (지특법 §36의3①2호)
        r = acquisition.calculate(self.base(first_time_buyer=True))
        self.assertEqual(r.extra["감면"], 2000000)
        # 소형·저가: 2.8억 × 1% = 280만 → 300만 한도 내 전액 → 산출세액만큼 감면
        r2 = acquisition.calculate(self.base(price=280000000, first_time_buyer=True,
                                             first_time_small_cheap=True))
        self.assertEqual(r2.extra["감면"], 2800000)
        # 12억 초과 → 감면 배제
        r3 = acquisition.calculate(self.base(price=1300000000, first_time_buyer=True))
        self.assertEqual(r3.extra["감면"], 0)


class TestCapitalGains(unittest.TestCase):
    def base(self, **kw):
        f = {"asset_type": "HOUSE", "transfer_date": "2026-06-15",
             "acquisition_date": "2019-05-10", "transfer_price": 1000000000,
             "acquisition_price": 600000000, "necessary_expenses": 0,
             "residence_years": 3, "acquired_in_regulated_area": True,
             "regulated_at_transfer": False, "household_house_count": 1,
             "special_case": {"type": "NONE"}}
        f.update(kw)
        return {"capital_gains": f}

    def test_full_exemption_under_12(self):
        # 1주택·보유7년·거주3년·양도가 10억 ≤ 12억 → 전액 비과세
        r = capital_gains.calculate(self.base())
        self.assertEqual(r.total, 0)
        self.assertTrue(r.extra.get("비과세"))

    def test_residence_fail_no_exemption(self):
        # 취득 당시 조정지역 + 거주 1년 → 비과세 탈락 → 과세
        r = capital_gains.calculate(self.base(residence_years=1))
        self.assertGreater(r.total, 0)

    def test_high_price_proration(self):
        # 고가 1주택: 양도 15억, 취득 6억, 경비 2천만, 보유 7년(2019-05-10~2026-06-15), 거주 3년
        # 차익 8.8억 → 과세차익 = 8.8억×3/15 = 1.76억
        # 표2: 보유 7년 28% + 거주 3년 12% = 40% → 공제 70,400,000
        # 소득 105,600,000 − 250만 = 103,100,000 → 35% − 15,440,000 = 20,645,000
        # 지방소득세 2,064,500 → 합계 22,709,500
        r = capital_gains.calculate(self.base(transfer_price=1500000000,
                                              necessary_expenses=20000000))
        self.assertEqual(r.extra["과세대상차익"], 176000000)
        self.assertAlmostEqual(r.extra["장특공률"], 0.40)
        self.assertEqual(r.extra["과세표준"], 103100000)
        self.assertEqual(r.extra["산출세액"], 20645000)
        self.assertEqual(r.total, 22709500)

    def test_table1_when_residence_under_2y(self):
        # 거주 2년 미만 → 표2 배제 → 표1 (보유 7년 = 14%) — 단 비과세도 탈락하므로 전체 과세
        r = capital_gains.calculate(self.base(residence_years=0,
                                              acquired_in_regulated_area=False,
                                              household_house_count=2))
        self.assertAlmostEqual(r.extra["장특공률"], 0.14)

    def test_short_term_70pct(self):
        # 보유 6개월 주택: 차익 1억 − 기본공제 250만 = 9,750만 × 70% = 68,250,000
        r = capital_gains.calculate(self.base(acquisition_date="2026-01-02",
                                              transfer_price=700000000,
                                              acquisition_price=600000000,
                                              residence_years=0,
                                              acquired_in_regulated_area=False))
        self.assertEqual(r.extra["산출세액"], 68250000)

    def test_heavy_after_suspension_end(self):
        # 2026-06-15 양도(유예 종료 후), 조정지역 2주택, 보유 7년 → +20%p, 장특공 배제
        # 차익 4억 − 0(장특공 배제) − 250만 = 3.975억 → (40%+20%) − 2,594만 = 212,560,000
        r = capital_gains.calculate(self.base(regulated_at_transfer=True,
                                              household_house_count=2,
                                              residence_years=0,
                                              acquired_in_regulated_area=False))
        self.assertTrue(r.extra["중과적용"])
        self.assertAlmostEqual(r.extra["장특공률"], 0.0)
        self.assertEqual(r.extra["산출세액"], int(397500000 * 0.60 - 25940000))

    def test_heavy_suspended_before_deadline(self):
        # 2026-05-01 양도(유예 기간 내) + 보유 2년 이상 → 중과 배제, 표1 장특공 적용
        r = capital_gains.calculate(self.base(transfer_date="2026-05-01",
                                              regulated_at_transfer=True,
                                              household_house_count=2,
                                              residence_years=0,
                                              acquired_in_regulated_area=False))
        self.assertFalse(r.extra["중과적용"])
        self.assertGreater(r.extra["장특공률"], 0)

    def test_temporary_2house_ok(self):
        # 일시적 2주택 충족: 종전 2019-05-10 취득 → 신규 2024-03-02(1년 경과) → 2026-06-15 양도(3년 내)
        r = capital_gains.calculate(self.base(
            household_house_count=2,
            special_case={"type": "TEMPORARY_2HOUSE", "selling_prior_house": True,
                          "prior_house_acquisition_date": "2019-05-10",
                          "new_house_acquisition_date": "2024-03-02"}))
        self.assertEqual(r.total, 0)

    def test_temporary_2house_deadline_fail(self):
        # 신규 2022-03-02 취득 → 3년 기한 2025-03-02 < 양도 2026-06-15 → 탈락
        r = capital_gains.calculate(self.base(
            household_house_count=2,
            special_case={"type": "TEMPORARY_2HOUSE", "selling_prior_house": True,
                          "prior_house_acquisition_date": "2019-05-10",
                          "new_house_acquisition_date": "2022-03-02"}))
        self.assertGreater(r.total, 0)

    def test_temporary_2house_auction_para18(self):
        # 3년 도과했지만 경매신청(§155⑱ 2호) → 특례 유지
        r = capital_gains.calculate(self.base(
            household_house_count=2,
            special_case={"type": "TEMPORARY_2HOUSE", "selling_prior_house": True,
                          "prior_house_acquisition_date": "2019-05-10",
                          "new_house_acquisition_date": "2022-03-02",
                          "para18_reason": "AUCTION_FILED"}))
        self.assertEqual(r.total, 0)

    def test_marriage_10y_current_law(self):
        # 혼인 2018-01-10, 양도 2026-06-15 (개정 2024.11.12 이후) → 10년 내 → 비과세
        r = capital_gains.calculate(self.base(
            household_house_count=2,
            special_case={"type": "MARRIAGE", "union_date": "2018-01-10"}))
        self.assertEqual(r.total, 0)

    def test_marriage_5y_old_law(self):
        # 같은 혼인일이지만 양도 2024-06-15 (개정 전) → 구법 5년 초과 → 과세
        r = capital_gains.calculate(self.base(
            transfer_date="2024-06-15", household_house_count=2,
            special_case={"type": "MARRIAGE", "union_date": "2018-01-10"}))
        self.assertGreater(r.total, 0)

    def test_inheritance_same_household_excluded(self):
        # 상속개시 당시 동일세대(동거봉양 합가 아님) → 특례 배제 (§155② 단서)
        r = capital_gains.calculate(self.base(
            household_house_count=2,
            special_case={"type": "INHERITANCE", "selling_general_house": True,
                          "held_general_house_at_inheritance": True,
                          "same_household_at_inheritance": True}))
        self.assertGreater(r.total, 0)

    def test_presale_right_60pct(self):
        # 분양권 보유 1년 이상 → 60% (기본세율 없음)
        r = capital_gains.calculate(self.base(asset_type="PRESALE_RIGHT",
                                              acquisition_date="2024-01-05",
                                              transfer_price=700000000,
                                              acquisition_price=600000000,
                                              residence_years=0))
        self.assertEqual(r.extra["산출세액"], int((100000000 - 2500000) * 0.60))


class TestHolding(unittest.TestCase):
    def test_one_house_12eok_no_cret(self):
        # 1세대1주택 공시 12억 → 종부세 과표 0
        r = holding.calculate({"holding": {"taxpayer": "INDIVIDUAL",
                                           "official_prices": [1200000000], "house_count": 1,
                                           "is_one_household_one_house": True}})
        self.assertEqual(r.extra["종부세"], 0)
        self.assertGreater(r.extra["재산세"], 0)

    def test_one_house_18eok_credit(self):
        # 공시 18억 1주택: 과표 (18−12)×0.6 = 3.6억 → 150만 + 0.6억×0.7% = 192만(공제 전)
        r = holding.calculate({"holding": {"taxpayer": "INDIVIDUAL",
                                           "official_prices": [1800000000], "house_count": 1,
                                           "is_one_household_one_house": True,
                                           "owner_age": 65, "holding_years": 8}})
        self.assertEqual(r.extra["종부세과세표준"], 360000000)
        # 세액공제: 고령 65세 30% + 장기 8년 20% = 50%
        self.assertAlmostEqual(r.extra["세액공제율"], 0.50)

    def test_three_houses_30eok(self):
        # 3주택 합산 30억: 과표 (30−9)×0.6 = 12.6억 → 3주택 세율표
        # 960만(12억까지) + 0.6억×2.0% = 1,080만 (재산세액 공제 전)
        r = holding.calculate({"holding": {"taxpayer": "INDIVIDUAL",
                                           "official_prices": [1000000000, 1000000000, 1000000000],
                                           "house_count": 3,
                                           "is_one_household_one_house": False}})
        self.assertEqual(r.extra["종부세과세표준"], 1260000000)

    def test_credit_cap_80(self):
        # 고령 70세(40%) + 장기 15년(50%) = 90% → 한도 80%
        r = holding.calculate({"holding": {"taxpayer": "INDIVIDUAL",
                                           "official_prices": [2000000000], "house_count": 1,
                                           "is_one_household_one_house": True,
                                           "owner_age": 72, "holding_years": 16}})
        self.assertAlmostEqual(r.extra["세액공제율"], 0.80)


if __name__ == "__main__":
    unittest.main()
