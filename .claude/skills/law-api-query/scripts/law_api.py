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
  --no-cache  캐시 무시(검색 1h/본문 24h TTL 자동 캐시) — 서브커맨드 앞에 붙일 것

마커(자동 판정, 조사관은 이 마커를 근거로 판단할 것):
  [NOT_FOUND]           검색 결과 0건 (API 정상 응답)
  [ERROR:HTTP_xxx]       HTTP 요청 실패
  [ERROR:NETWORK]        네트워크/타임아웃 실패
  [ERROR:PARSE_FAILED]   JSON 아닌 응답(OC/IP 미등록 가능성)
"""
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SEARCH_URL = "https://www.law.go.kr/DRF/lawSearch.do"
BODY_URL = "https://www.law.go.kr/DRF/lawService.do"

# 파일 기반 캐시 — 조사관 2명이 병렬로 유사 질의를 던져 중복 호출이 실제로 발생하므로 도입.
# (korean-law-mcp 참고: 검색 1h / 본문 24h TTL. `_workspace/reference_comparison.md` §4.5)
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
SEARCH_TTL = 3600      # 1시간
BODY_TTL = 86400       # 24시간

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
    "ttSpecialDecc": "조세심판원 결정례(특별행정심판)",  # 2026-07-27 추가, 실호출 검증 완료
    "licbyl": "법령 별표·서식",  # 2026-07-27 추가. search는 정상 동작(별표명 검색), body는 HTML 위젯만 반환하므로 호출 금지 — search 결과의 별표서식파일링크/PDF파일링크를 그대로 쓸 것
}


def get_oc(cli_oc=None):
    return cli_oc or os.environ.get("LAW_OC") or "test"


def _cache_path(full_url):
    h = hashlib.sha1(full_url.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.json")


def _cache_get(full_url, ttl):
    path = _cache_path(full_url)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            entry = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if time.time() - entry.get("cached_at", 0) > ttl:
        return None
    return entry.get("raw")


def _cache_set(full_url, raw):
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(_cache_path(full_url), "w", encoding="utf-8") as f:
            json.dump({"cached_at": time.time(), "full_url": full_url, "raw": raw}, f, ensure_ascii=False)
    except OSError:
        pass  # 캐시 쓰기 실패는 치명적이지 않으므로 무시


def _request(url, params, ttl=0, no_cache=False):
    qs = urllib.parse.urlencode(params, encoding="utf-8")
    full = f"{url}?{qs}"

    if ttl and not no_cache:
        cached = _cache_get(full, ttl)
        if cached is not None:
            sys.stderr.write(f"[캐시 HIT, TTL {ttl}s] {full}\n")
            return full, cached

    req = urllib.request.Request(full, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        print(f"[ERROR:HTTP_{e.code}] 요청 실패 — {e.reason}")
        sys.stderr.write(f"[요청] {full}\n[에러] HTTP {e.code} {e.reason}\n")
        sys.exit(1)
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"[ERROR:NETWORK] 요청 실패 — {e}")
        sys.stderr.write(f"[요청] {full}\n[에러] {e}\n")
        sys.exit(1)

    if ttl and not no_cache:
        _cache_set(full, raw)
    return full, raw


def _find_no_match_placeholder(obj):
    """정상 JSON이지만 '일치하는 판례가 없습니다' 류의 안내문 하나만 담긴 응답을 감지한다.
    (2026-08-10 실측: target=prec body 조회에서 국세법령정보시스템 출처 판례가 이 형태로 옴 —
    totalCnt 필드 자체가 없어 _find_total_cnt로는 못 잡는다.)"""
    if isinstance(obj, dict) and len(obj) == 1:
        v = next(iter(obj.values()))
        if isinstance(v, str) and ("없습니다" in v or "존재하지" in v):
            return v
    return None


def _find_total_cnt(obj):
    """응답 JSON 어디에 있든 totalCnt(검색결과 건수)를 재귀적으로 찾는다.
    target마다 최상위 키(LawSearch/PrecSearch/...)가 달라 위치를 하드코딩하지 않는다."""
    if isinstance(obj, dict):
        if "totalCnt" in obj:
            return obj["totalCnt"]
        for v in obj.values():
            found = _find_total_cnt(v)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _find_total_cnt(v)
            if found is not None:
                return found
    return None


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
    full, raw = _request(SEARCH_URL, params, ttl=SEARCH_TTL, no_cache=args.no_cache)
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
    full, raw = _request(BODY_URL, params, ttl=BODY_TTL, no_cache=args.no_cache)
    _emit(full, raw, args)


def _emit(full, raw, args):
    sys.stderr.write(f"[요청] {full}\n")
    if args.raw or args.type != "JSON":
        print(raw)
        return
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        sys.stderr.write("[경고] JSON 파싱 실패 — 원본을 출력합니다 "
                         "(OC 미등록/파라미터 오류/HTML 응답 가능).\n")
        print("[ERROR:PARSE_FAILED] JSON이 아닌 응답 — OC 미등록/IP 미등록/파라미터 오류 가능성. "
              "아래는 원본 응답이다.")
        print(raw)
        return

    total = _find_total_cnt(data)
    if total is not None and str(total) == "0":
        print("[NOT_FOUND] 검색 결과 0건 — 키워드를 바꿔 재검색할 것 (search=2 본문검색은 사용 금지).")

    placeholder = _find_no_match_placeholder(data)
    if placeholder:
        print(f'[NOT_FOUND] 본문 없음 — API가 "{placeholder}"라고 응답함(정상 JSON, 내용 없음). '
              "목록(search)에는 있어도 본문(body) 출처가 다른 시스템(예: 국세법령정보시스템)이면 이렇게 나올 수 있다.")

    print(json.dumps(data, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description="law.go.kr Open API client")
    p.add_argument("--oc")
    p.add_argument("--type", default="JSON", choices=["JSON", "XML", "HTML"])
    p.add_argument("--raw", action="store_true")
    p.add_argument("--no-cache", action="store_true", help="캐시 무시하고 항상 새로 조회(인용 사후검증 등 최신성이 중요할 때)")
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
