#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tax_calc.py — 부동산 세액 확정 계산기 (취득세·보유세·양도소득세).

LLM은 사실관계를 JSON으로 추출만 하고, 판정·계산은 이 스크립트가 전담한다(암산 금지).

사용법:
  python tax_calc.py --input facts.json                 # 입력에 있는 세목 전부 계산
  python tax_calc.py --input facts.json --tax capital_gains
  python tax_calc.py --sample acquisition               # 입력 스키마 예시 출력
  cat facts.json | python tax_calc.py --json            # 기계용 JSON 출력

의존성: 표준 라이브러리만 (Python 3.8+).
"""
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engines import acquisition, holding, capital_gains  # noqa: E402

ENGINES = {
    "acquisition": ("취득세", acquisition.calculate),
    "holding": ("보유세", holding.calculate),
    "capital_gains": ("양도소득세", capital_gains.calculate),
}

SAMPLES = {
    "acquisition": {
        "acquisition": {
            "acquirer": "INDIVIDUAL",
            "cause": "AUCTION",
            "property": "HOUSE",
            "price": 750000000,
            "sigajun_price": None,
            "is_regulated_area": True,
            "is_metropolitan": True,
            "in_redevelopment_zone": False,
            "household_house_count_before": 1,
            "temporary_2house": True,
            "exclusive_area_m2": 84.9,
            "first_time_buyer": False,
            "acquired_via_presale_right": False
        }
    },
    "holding": {
        "holding": {
            "taxpayer": "INDIVIDUAL",
            "official_prices": [1800000000],
            "house_count": 1,
            "is_one_household_one_house": True,
            "joint_special_applied": False,
            "owner_age": 65,
            "holding_years": 8,
            "prev_year_total_tax": None,
            "exclusion_prices": []
        }
    },
    "capital_gains": {
        "capital_gains": {
            "asset_type": "HOUSE",
            "transfer_date": "2026-06-15",
            "acquisition_date": "2019-05-10",
            "transfer_price": 1500000000,
            "acquisition_price": 600000000,
            "necessary_expenses": 20000000,
            "residence_years": 3,
            "acquired_in_regulated_area": True,
            "regulated_at_transfer": False,
            "household_house_count": 2,
            "unregistered": False,
            "special_case": {
                "type": "TEMPORARY_2HOUSE",
                "selling_prior_house": True,
                "prior_house_acquisition_date": "2019-05-10",
                "new_house_acquisition_date": "2024-03-02",
                "para18_reason": None,
                "was_multi_house_before": False
            }
        }
    },
}


def print_report(res):
    print("=" * 62)
    print("[{}]  총 부담세액: {:,}원".format(res.tax_name, res.total))
    print("=" * 62)
    for s in res.steps:
        line = "  {:<28} {}".format(s["항목"], s["금액/값"])
        print(line)
        if s.get("근거"):
            print("      └ 근거: {}".format(s["근거"]))
        if s.get("비고"):
            print("      └ {}".format(s["비고"]))
    if res.warnings:
        print("-" * 62)
        print("⚠ 확인 필요 / 경고 ({}건):".format(len(res.warnings)))
        for w in res.warnings:
            print("  • " + w)
    print("-" * 62)
    print("※ 참고용 세무정보입니다. 신고 전 반드시 세무사 확인이 필요합니다.")
    print()


def main():
    ap = argparse.ArgumentParser(description="부동산 세액 확정 계산기")
    ap.add_argument("--input", help="사실관계 JSON 파일 경로 (미지정 시 stdin)")
    ap.add_argument("--tax", choices=list(ENGINES.keys()) + ["all"], default="all")
    ap.add_argument("--json", action="store_true", help="기계용 JSON 출력")
    ap.add_argument("--sample", choices=list(SAMPLES.keys()), help="입력 스키마 예시 출력")
    args = ap.parse_args()

    if args.sample:
        print(json.dumps(SAMPLES[args.sample], ensure_ascii=False, indent=2))
        return

    if args.input:
        with open(args.input, encoding="utf-8") as f:
            facts = json.load(f)
    else:
        facts = json.load(sys.stdin)

    targets = list(ENGINES.keys()) if args.tax == "all" else [args.tax]
    results = []
    for key in targets:
        if key not in facts:
            continue
        name, fn = ENGINES[key]
        try:
            results.append(fn(facts))
        except Exception as e:
            sys.stderr.write("[{}] 계산 실패: {}\n".format(name, e))
            sys.exit(2)

    if not results:
        sys.stderr.write("입력 JSON에 계산할 세목이 없습니다 (키: acquisition / holding / capital_gains).\n")
        sys.exit(1)

    if args.json:
        print(json.dumps([r.to_dict() for r in results], ensure_ascii=False, indent=2))
    else:
        for r in results:
            print_report(r)


if __name__ == "__main__":
    main()
