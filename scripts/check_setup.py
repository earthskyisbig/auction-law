#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""설치 점검 — 이 스크립트 하나로 준비가 됐는지 확인한다.

사용: python scripts/check_setup.py

확인 항목:
  1) 파이썬 버전
  2) 하네스 파일(.claude/agents, .claude/skills) 존재
  3) LAW_OC 설정 상태 (.env 또는 환경변수, 없으면 test 폴백)
  4) law.go.kr Open API 실제 조회 성공 여부
  5) (OC 등록자용) 현재 공인 IP 안내
"""
import os
import re
import sys
import json
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OK, WARN, FAIL = "[  OK  ]", "[ 주의 ]", "[ 실패 ]"
problems = []


def load_env():
    """.env 를 읽어 환경변수로 올린다(외부 패키지 없이)."""
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())
    return True


def check_python():
    v = sys.version_info
    if v >= (3, 8):
        print(f"{OK} 파이썬 {v.major}.{v.minor}.{v.micro}")
    else:
        print(f"{FAIL} 파이썬 {v.major}.{v.minor} — 3.8 이상이 필요합니다")
        problems.append("파이썬 3.8+ 설치")


def check_harness():
    agents = os.path.join(ROOT, ".claude", "agents")
    skills = os.path.join(ROOT, ".claude", "skills")
    na = len([f for f in os.listdir(agents)]) if os.path.isdir(agents) else 0
    ns = len([d for d in os.listdir(skills)]) if os.path.isdir(skills) else 0
    if na and ns:
        print(f"{OK} 하네스 파일: 에이전트 {na}개 · 스킬 {ns}개")
    else:
        print(f"{FAIL} .claude/agents 또는 .claude/skills 를 찾을 수 없습니다")
        problems.append("저장소 루트에서 실행했는지 확인 (git clone 후 폴더 안으로 이동)")


def check_oc():
    has_env = load_env()
    oc = os.environ.get("LAW_OC", "").strip()
    print(f"{OK} .env 파일 발견" if has_env else f"{WARN} .env 없음 — .env.example 을 복사하면 됩니다(선택)")
    if oc and oc != "test":
        print(f"{OK} LAW_OC = {oc} (등록 계정 사용)")
    else:
        print(f"{WARN} LAW_OC 미설정 → 'test' 로 조회합니다. 강의 실습에는 충분합니다(선택적으로 나중에 등록)")
    return oc or "test"


def check_api(oc):
    url = ("https://www.law.go.kr/DRF/lawSearch.do?"
           f"OC={oc}&target=law&type=JSON&display=1&query=%EC%A3%BC%ED%83%9D%EB%B2%95")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"{FAIL} law.go.kr 접속 실패: {e}")
        problems.append("인터넷 연결 또는 방화벽 확인")
        return
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"{FAIL} 응답이 JSON이 아닙니다(HTML 오류 페이지일 수 있음)")
        problems.append("law.go.kr 응답 이상 — 잠시 후 재시도")
        return
    if "result" in data and "실패" in str(data.get("result", "")):
        print(f"{FAIL} 사용자 검증 실패 — OC='{oc}' 의 IP가 등록되지 않았습니다")
        print(f"         → 해결: LAW_OC를 지우고 test로 쓰거나, 아래 IP를 open.law.go.kr에 등록")
        problems.append("OC의 호출 IP 미등록 (또는 LAW_OC 삭제 후 test 사용)")
    else:
        law = data.get("LawSearch", {}).get("law")
        law = law[0] if isinstance(law, list) else law
        name = law.get("법령명한글", "?") if isinstance(law, dict) else "?"
        print(f"{OK} law.go.kr 조회 성공 — 예: '{name}' 확인됨")


def show_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=10) as r:
            ip = r.read().decode().strip()
        print(f"       현재 공인 IP: {ip}  (본인 OC를 등록해 쓸 경우 open.law.go.kr에 이 IP를 등록)")
    except Exception:
        pass


def main():
    print("\n=== auction-law 설치 점검 ===\n")
    check_python()
    check_harness()
    oc = check_oc()
    check_api(oc)
    show_ip()
    print()
    if problems:
        print("해결이 필요한 항목:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print("준비 완료. Claude Code에서 이 폴더를 열고 법률/세무 질문을 하면 됩니다.")
    print('예: "재건축 조합설립 후 경매로 샀는데 조합원 지위 승계되나요? 투기과열지구입니다"\n')


if __name__ == "__main__":
    main()
