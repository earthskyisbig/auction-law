#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""auction-law — DuckDB 데이터 관리 헬퍼.

이 프로젝트의 데이터는 흩어진 CSV가 아니라 DuckDB 하나로 적재·질의·누적한다.
설치: pip install duckdb
사용:
  python db/db.py            # DB 초기화(스키마 생성)
  # 코드에서:
  import db.db as D
  con = D.connect(); D.init(con)
  con.execute("INSERT INTO ...")

DuckDB 장점: 분석 질의 빠름, CSV/Parquet 직접 read_csv_auto/read_parquet 질의 가능,
컬럼형 저장으로 대용량 집계 강함. 로컬 파일 하나(data/app.duckdb)로 관리.
"""
import os

try:
    import duckdb
except ImportError:
    raise SystemExit("duckdb 미설치: pip install duckdb")


def project_root():
    here = os.path.abspath(os.path.dirname(__file__))
    for _ in range(6):
        if os.path.isdir(os.path.join(here, ".git")) or os.path.isdir(os.path.join(here, "docs")):
            return here
        here = os.path.dirname(here)
    return os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


def load_env():
    """프로젝트 루트 .env 를 환경변수로 로드(이미 설정된 값은 유지)."""
    env = os.path.join(project_root(), ".env")
    if os.path.isfile(env):
        for line in open(env, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def db_path():
    load_env()
    return os.environ.get("DB_PATH") or os.path.join(project_root(), "data", "app.duckdb")


def connect():
    p = db_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return duckdb.connect(p)


# 프로젝트에 맞게 스키마를 선언한다. (예시)
SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id        BIGINT,
    name      VARCHAR,
    value     DOUBLE,
    created_at TIMESTAMP DEFAULT now()
);
"""


def init(con):
    con.execute(SCHEMA)


if __name__ == "__main__":
    con = connect()
    init(con)
    print("DuckDB ready:", db_path())
