#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""law.go.kr(국가법령정보 공동활용) Open API 클라이언트.

법령·판례·법령해석례·행정규칙·자치법규·헌재결정례·행정심판례를 조회한다.
법령 조사관·판례 조사관 에이전트가 공통으로 호출한다.

인증(OC):
  OC 파라미터는 open.law.go.kr 에 등록한 이메일의 '아이디 앞부분'이다.
  (예: algo1744@gmail.com -> OC=algo1744)
  환경변수 LAW_OC 로 지정한다. 미지정 시 'test'(제한적 시험용)로 폴백한다.
  실사용 전 반드시 open.law.go.kr > OPEN API > 신청 에서 본인 OC를 등록할 것.

사용법:
  # 목록 검색 (lawSearch.do)
  python law_api.py search --target prec --query "유치권 경매" --display 10
  python law_api.py search --target law  --query "도시 및 주거환경정비법"

  # 본문 조회 (lawService.do) — 목록에서 얻은 ID 또는 MST 사용
  python law_api.py body --target law --mst 267581
  python law_api.py body --target prec --id 228541

옵션:
  --type JSON|XML|HTML (기본 JSON)
  --oc OC직접지정 (환경변수보다 우선)
  --raw  가공 없이 원본 응답 출력
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

SEARCH_URL = "https://www.law.go.kr/DRF/lawSearch.do"
BODY_URL = "https://www.law.go.kr/DRF/lawService.do"

# target 코드 -> 사람이 읽는 이름 (참조용)
TARGETS = {
    "law": "현행법령",
    "eflaw": "시행일법령",
    "lsHistory": "법령연혁",
    "prec": "판례",
    "detc": "헌재결정례",
    "expc": "법령해석례",
    "decc": "행정심판례",
    "admrul": "행정규칙",
    "ordin": "자치법규",
}


def get_oc(cli_oc=None):
    return cli_oc or os.environ.get("LAW_OC") or "test"


def _request(url, params):
    qs = urllib.parse.urlencode(params, encoding="utf-8")
    full = f"{url}?{qs}"
    req = urllib.request.Request(full, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return full, raw


def search(args):
    params = {
        "OC": get_oc(args.oc),
        "target": args.target,
        "type": args.type,
        "display": str(args.display),
        "page": str(args.page),
    }
    if args.query:
        params["query"] = args.query
    if args.search:
        params["search"] = str(args.search)
    if args.extra:
        for kv in args.extra:
            k, _, v = kv.partition("=")
            params[k] = v
    full, raw = _request(SEARCH_URL, params)
    _emit(full, raw, args)


def body(args):
    params = {
        "OC": get_oc(args.oc),
        "target": args.target,
        "type": args.type,
    }
    if args.mst:
        params["MST"] = args.mst
    if args.id:
        params["ID"] = args.id
    if args.jo:
        params["JO"] = args.jo
    if args.lm:
        params["LM"] = args.lm
    if args.extra:
        for kv in args.extra:
            k, _, v = kv.partition("=")
            params[k] = v
    full, raw = _request(BODY_URL, params)
    _emit(full, raw, args)


def _emit(full, raw, args):
    sys.stderr.write(f"[요청] {full}\n")
    if args.raw or args.type != "JSON":
        print(raw)
        return
    try:
        data = json.loads(raw)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        sys.stderr.write("[경고] JSON 파싱 실패 — 원본을 출력합니다 "
                         "(OC 미등록/파라미터 오류/HTML 응답 가능).\n")
        print(raw)


def main():
    p = argparse.ArgumentParser(description="law.go.kr Open API client")
    p.add_argument("--oc")
    p.add_argument("--type", default="JSON", choices=["JSON", "XML", "HTML"])
    p.add_argument("--raw", action="store_true")
    p.add_argument("--extra", nargs="*", help="추가 파라미터 key=value (예: curt=대법원 prncYd=20200101~20241231)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="목록 검색 (lawSearch.do)")
    s.add_argument("--target", required=True, choices=list(TARGETS))
    s.add_argument("--query")
    s.add_argument("--search", type=int, help="1=제목/사건명(기본), 2=본문 전체")
    s.add_argument("--display", type=int, default=20)
    s.add_argument("--page", type=int, default=1)
    s.set_defaults(func=search)

    b = sub.add_parser("body", help="본문 조회 (lawService.do)")
    b.add_argument("--target", required=True, choices=list(TARGETS))
    b.add_argument("--mst", help="법령 일련번호(MST)")
    b.add_argument("--id", help="법령ID / 판례일련번호 등")
    b.add_argument("--jo", help="조번호 6자리 (예: 000200=제2조)")
    b.add_argument("--lm", help="법령명")
    b.set_defaults(func=body)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
