# -*- coding: utf-8 -*-
"""공통 유틸 — 날짜·누진세율·결과 수집. 표준 라이브러리만 사용(설치 불필요)."""
import json
import os
from datetime import date, datetime

RULES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "rules")


def load_rules(name):
    """rules/*.json 로드. 모든 수치는 근거 조문(basis)·검증상태(verified)를 함께 갖는다."""
    path = os.path.join(RULES_DIR, name)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_date(s):
    if s is None:
        return None
    if isinstance(s, date):
        return s
    return datetime.strptime(s, "%Y-%m-%d").date()


def full_years_between(start, end):
    """만 나이 방식 경과 연수(보유·거주기간 판정용). start/end는 date."""
    if start is None or end is None:
        return None
    years = end.year - start.year
    if (end.month, end.day) < (start.month, start.day):
        years -= 1
    return max(years, 0)


def add_years(d, n):
    """n년 후 같은 날짜(2/29는 2/28로)."""
    try:
        return d.replace(year=d.year + n)
    except ValueError:
        return d.replace(year=d.year + n, day=28)


def progressive_cumulative(base, brackets):
    """구간누적 누진 계산. brackets = [[상한(None=무한), 구간세율], ...] (하한은 직전 상한)."""
    if base <= 0:
        return 0
    tax = 0.0
    prev = 0
    for limit, rate in brackets:
        upper = base if limit is None else min(base, limit)
        if upper > prev:
            tax += (upper - prev) * rate
        if limit is None or base <= limit:
            break
        prev = limit
    return int(tax)


def progressive_quick(base, brackets, surcharge=0.0):
    """속산표 누진 계산(과표×세율−누진공제). brackets = [[상한(None), 세율, 누진공제], ...].
    surcharge: 다주택 중과 가산(세율에 +20%p/+30%p, 누진공제 동일 — 소득세법 §104⑦)."""
    if base <= 0:
        return 0, 0.0
    for limit, rate, deduction in brackets:
        if limit is None or base <= limit:
            return int(base * (rate + surcharge) - deduction), rate + surcharge
    raise ValueError("누진표 구간 누락")


class Result:
    """세목별 계산 결과 — 단계(steps)·경고(warnings)·근거(citations)를 함께 수집한다."""

    def __init__(self, tax_name):
        self.tax_name = tax_name
        self.steps = []
        self.warnings = []
        self.citations = []
        self.total = 0
        self.extra = {}

    def step(self, label, value, basis=None, note=None):
        self.steps.append({"항목": label, "금액/값": value, "근거": basis, "비고": note})

    def warn(self, msg):
        if msg not in self.warnings:
            self.warnings.append(msg)

    def cite(self, c):
        if c and c not in self.citations:
            self.citations.append(c)

    def to_dict(self):
        return {
            "세목": self.tax_name,
            "계산단계": self.steps,
            "총부담세액": self.total,
            "부가정보": self.extra,
            "경고": self.warnings,
            "근거": self.citations,
        }


def fmt_won(x):
    if x is None:
        return "-"
    return "{:,}원".format(int(x))


def track_rule(res, rule):
    """규칙 항목의 근거·검증상태를 결과에 반영. 미검증 값은 경고로 승격."""
    basis = rule.get("basis")
    verified = rule.get("verified", "")
    if basis:
        res.cite(basis)
    if verified.startswith("참고값"):
        res.warn("미검증 수치 사용: {} — {} ({})".format(rule.get("name", basis), verified, basis or "근거 미상"))
    return basis
