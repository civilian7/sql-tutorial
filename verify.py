#!/usr/bin/env python3
"""튜토리얼 환경 검증 스크립트.

데이터베이스 연결, 테이블 존재 여부, 데이터 건수를 확인합니다.

사용법:
    python verify.py                    # SQLite만 검증
    python verify.py --target mysql     # MySQL 검증
    python verify.py --target postgresql  # PostgreSQL 검증
    python verify.py --all              # 전체 검증
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys

# ── 검증 기준 ──
EXPECTED_TABLES = [
    "calendar", "cart_items", "carts", "categories", "complaints",
    "coupon_usage", "coupons", "customer_addresses", "customer_grade_history",
    "customers", "inventory_transactions", "order_items", "orders",
    "payments", "point_transactions", "product_images", "product_prices",
    "product_qna", "product_tags", "product_views", "products",
    "promotion_products", "promotions", "returns", "reviews",
    "shipping", "staff", "suppliers", "tags", "wishlists",
]

# 최소 행 수 (small 기준, 여유 있게 80%로 설정)
MIN_ROWS = {
    "customers": 4000,
    "orders": 28000,
    "order_items": 67000,
    "products": 200,
    "reviews": 6000,
    "payments": 28000,
}


class Result:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def ok(self, msg: str):
        self.passed += 1
        print(f"  [OK]{msg}")

    def fail(self, msg: str):
        self.failed += 1
        print(f"  [FAIL]{msg}")

    def warn(self, msg: str):
        self.warnings += 1
        print(f"  [WARN]{msg}")

    def summary(self) -> bool:
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        if self.failed == 0:
            print(f"[OK] 검증 완료: {self.passed}/{total} 통과")
        else:
            print(f"[FAIL] 검증 실패: {self.passed}/{total} 통과, {self.failed}개 실패")
        if self.warnings > 0:
            print(f"[WARN] 경고: {self.warnings}개")
        print(f"{'='*50}")
        return self.failed == 0


def verify_sqlite(result: Result, db_path: str = "output/ecommerce.db"):
    """SQLite 데이터베이스를 검증합니다."""
    print("\n[CHECK]SQLite 검증")
    print(f"   파일: {db_path}")

    # 파일 존재
    if not os.path.exists(db_path):
        result.fail(f"파일을 찾을 수 없습니다: {db_path}")
        result.fail("먼저 'python generate.py --size small'을 실행하세요")
        return

    file_size = os.path.getsize(db_path) / (1024 * 1024)
    result.ok(f"파일 존재 ({file_size:.1f} MB)")

    # 연결
    try:
        conn = sqlite3.connect(db_path)
        result.ok("연결 성공")
    except Exception as e:
        result.fail(f"연결 실패: {e}")
        return

    # 테이블 확인
    try:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        if len(tables) >= len(EXPECTED_TABLES):
            result.ok(f"테이블 {len(tables)}개 확인")
        else:
            result.fail(f"테이블 {len(tables)}개 (예상: {len(EXPECTED_TABLES)}개)")

        missing = set(EXPECTED_TABLES) - set(tables)
        if missing:
            result.fail(f"누락된 테이블: {', '.join(sorted(missing))}")
    except Exception as e:
        result.fail(f"테이블 조회 실패: {e}")
        conn.close()
        return

    # 뷰 확인
    views = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name"
        )
    ]
    if views:
        result.ok(f"뷰 {len(views)}개 확인")
    else:
        result.warn("뷰가 없습니다")

    # 트리거 확인
    triggers = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name"
        )
    ]
    if triggers:
        result.ok(f"트리거 {len(triggers)}개 확인")
    else:
        result.warn("트리거가 없습니다")

    # 행 수 확인
    for table, min_count in MIN_ROWS.items():
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if count >= min_count:
                result.ok(f"{table}: {count:,}행")
            else:
                result.warn(f"{table}: {count:,}행 (예상 최소 {min_count:,})")
        except Exception as e:
            result.fail(f"{table} 조회 실패: {e}")

    # 데이터 무결성 샘플 체크
    try:
        # FK 무결성: 주문의 고객이 실제 존재하는지
        orphans = conn.execute(
            "SELECT COUNT(*) FROM orders o WHERE NOT EXISTS (SELECT 1 FROM customers c WHERE c.id = o.customer_id)"
        ).fetchone()[0]
        if orphans == 0:
            result.ok("FK 무결성 확인 (orders → customers)")
        else:
            result.warn(f"고아 주문 {orphans}건 발견")
    except Exception as e:
        result.warn(f"무결성 체크 실패: {e}")

    conn.close()


def verify_mysql(result: Result, host="localhost", port=3306, user="root", password=None):
    """MySQL 데이터베이스를 검증합니다."""
    print("\n[CHECK]MySQL 검증")
    print(f"   호스트: {host}:{port}")

    try:
        import pymysql
    except ImportError:
        try:
            import mysql.connector as pymysql
        except ImportError:
            result.fail("MySQL 드라이버가 없습니다. 'pip install pymysql' 또는 'pip install mysql-connector-python'을 실행하세요")
            return

    if password is None:
        import getpass
        password = getpass.getpass("MySQL root 비밀번호: ")

    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database="ecommerce")
        result.ok("연결 성공 (ecommerce 데이터베이스)")
    except Exception as e:
        result.fail(f"연결 실패: {e}")
        return

    cursor = conn.cursor()

    # 테이블 확인
    try:
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        if len(tables) >= len(EXPECTED_TABLES):
            result.ok(f"테이블 {len(tables)}개 확인")
        else:
            result.fail(f"테이블 {len(tables)}개 (예상: {len(EXPECTED_TABLES)}개)")
    except Exception as e:
        result.fail(f"테이블 조회 실패: {e}")
        conn.close()
        return

    # 뷰 확인
    try:
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = 'ecommerce'")
        view_count = len(cursor.fetchall())
        if view_count > 0:
            result.ok(f"뷰 {view_count}개 확인")
        else:
            result.warn("뷰가 없습니다")
    except Exception:
        result.warn("뷰 조회 실패")

    # 프로시저 확인
    try:
        cursor.execute("SELECT ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_SCHEMA = 'ecommerce'")
        proc_count = len(cursor.fetchall())
        if proc_count > 0:
            result.ok(f"저장 프로시저 {proc_count}개 확인")
        else:
            result.warn("저장 프로시저가 없습니다")
    except Exception:
        result.warn("프로시저 조회 실패")

    # 행 수 확인
    for table, min_count in MIN_ROWS.items():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            if count >= min_count:
                result.ok(f"{table}: {count:,}행")
            else:
                result.warn(f"{table}: {count:,}행 (예상 최소 {min_count:,})")
        except Exception as e:
            result.fail(f"{table} 조회 실패: {e}")

    conn.close()


def verify_postgresql(result: Result, host="localhost", port=5432, user="postgres", password=None):
    """PostgreSQL 데이터베이스를 검증합니다."""
    print("\n[CHECK]PostgreSQL 검증")
    print(f"   호스트: {host}:{port}")

    try:
        import psycopg2
    except ImportError:
        result.fail("PostgreSQL 드라이버가 없습니다. 'pip install psycopg2-binary'를 실행하세요")
        return

    if password is None:
        import getpass
        password = getpass.getpass("PostgreSQL postgres 비밀번호: ")

    try:
        conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname="ecommerce")
        result.ok("연결 성공 (ecommerce 데이터베이스)")
    except Exception as e:
        result.fail(f"연결 실패: {e}")
        return

    cursor = conn.cursor()

    # 테이블 확인
    try:
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
        tables = [row[0] for row in cursor.fetchall()]
        # PG는 파티션 테이블이 추가로 있으므로 기본 테이블만 카운트
        base_tables = [t for t in tables if not any(t.endswith(f"_{y}") for y in range(2015, 2030)) and not t.endswith("_default")]
        if len(base_tables) >= len(EXPECTED_TABLES):
            result.ok(f"테이블 {len(base_tables)}개 확인 (파티션 제외)")
        else:
            result.fail(f"테이블 {len(base_tables)}개 (예상: {len(EXPECTED_TABLES)}개)")
    except Exception as e:
        result.fail(f"테이블 조회 실패: {e}")
        conn.close()
        return

    # 뷰 확인
    try:
        cursor.execute("SELECT viewname FROM pg_views WHERE schemaname = 'public'")
        view_count = len(cursor.fetchall())
        cursor.execute("SELECT matviewname FROM pg_matviews WHERE schemaname = 'public'")
        mv_count = len(cursor.fetchall())
        total_views = view_count + mv_count
        if total_views > 0:
            result.ok(f"뷰 {view_count}개 + Materialized View {mv_count}개 확인")
        else:
            result.warn("뷰가 없습니다")
    except Exception:
        result.warn("뷰 조회 실패")

    # 함수 확인
    try:
        cursor.execute(
            "SELECT routine_name FROM information_schema.routines "
            "WHERE routine_schema = 'public' AND routine_type = 'FUNCTION'"
        )
        func_count = len(cursor.fetchall())
        if func_count > 0:
            result.ok(f"함수 {func_count}개 확인")
        else:
            result.warn("함수가 없습니다")
    except Exception:
        result.warn("함수 조회 실패")

    # 행 수 확인
    for table, min_count in MIN_ROWS.items():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            if count >= min_count:
                result.ok(f"{table}: {count:,}행")
            else:
                result.warn(f"{table}: {count:,}행 (예상 최소 {min_count:,})")
        except Exception as e:
            result.fail(f"{table} 조회 실패: {e}")

    conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="튜토리얼 환경 검증",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="예시:\n  python verify.py\n  python verify.py --target mysql\n  python verify.py --all",
    )
    parser.add_argument("--target", choices=["sqlite", "mysql", "postgresql"], default="sqlite",
                        help="검증할 데이터베이스 (기본: sqlite)")
    parser.add_argument("--all", action="store_true", help="모든 데이터베이스 검증")
    parser.add_argument("--db-path", default="output/ecommerce.db", help="SQLite DB 파일 경로")
    parser.add_argument("--host", default="localhost", help="MySQL/PG 호스트")
    parser.add_argument("--port", type=int, help="MySQL/PG 포트")
    parser.add_argument("--user", help="MySQL/PG 사용자")
    parser.add_argument("--password", help="MySQL/PG 비밀번호 (생략 시 프롬프트)")

    args = parser.parse_args()
    result = Result()

    print("=" * 50)
    print("[VERIFY]SQL 튜토리얼 환경 검증")
    print("=" * 50)

    # Python 버전 확인
    ver = sys.version_info
    if ver >= (3, 10):
        result.ok(f"Python {ver.major}.{ver.minor}.{ver.micro}")
    else:
        result.fail(f"Python {ver.major}.{ver.minor}.{ver.micro} (3.10 이상 필요)")

    targets = ["sqlite", "mysql", "postgresql"] if args.all else [args.target]

    for target in targets:
        if target == "sqlite":
            verify_sqlite(result, args.db_path)
        elif target == "mysql":
            verify_mysql(
                result,
                host=args.host,
                port=args.port or 3306,
                user=args.user or "root",
                password=args.password,
            )
        elif target == "postgresql":
            verify_postgresql(
                result,
                host=args.host,
                port=args.port or 5432,
                user=args.user or "postgres",
                password=args.password,
            )

    success = result.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
