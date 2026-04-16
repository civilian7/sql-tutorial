#!/usr/bin/env python3
"""Compile exercise YAML files into mkdocs markdown.

Usage:
    # Compile all exercises
    python compile_exercises.py

    # Compile and generate expected results from tutorial DB
    python compile_exercises.py --tutorial-db output/ecommerce-ko.db

    # Validate only (no output)
    python compile_exercises.py --validate-only

    # Compile single file
    python compile_exercises.py --file exercises/beginner/01-select.yaml
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path

import yaml


# Table descriptions for exercise header blocks
_TABLE_DESC = {
    "categories":              ("카테고리 (부모-자식 계층)", "Categories (parent-child hierarchy)"),
    "suppliers":               ("공급업체 (업체명, 연락처)", "Suppliers (company, contact)"),
    "products":                ("상품 (이름, 가격, 재고, 브랜드)", "Products (name, price, stock, brand)"),
    "product_images":          ("상품 이미지 (유형, 크기)", "Product images (type, size)"),
    "product_prices":          ("가격 이력 (변경 사유)", "Price history (change reason)"),
    "customers":               ("고객 (등급, 포인트, 가입채널)", "Customers (grade, points, channel)"),
    "customer_addresses":      ("배송지 (주소, 기본 여부)", "Addresses (address, default flag)"),
    "staff":                   ("직원 (부서, 역할, 관리자)", "Staff (dept, role, manager)"),
    "orders":                  ("주문 (상태, 금액, 일시)", "Orders (status, amount, date)"),
    "order_items":             ("주문 상세 (수량, 단가)", "Order items (qty, unit price)"),
    "payments":                ("결제 (방법, 금액, 상태)", "Payments (method, amount, status)"),
    "shipping":                ("배송 (택배사, 추적번호, 상태)", "Shipping (carrier, tracking, status)"),
    "reviews":                 ("리뷰 (평점, 내용)", "Reviews (rating, content)"),
    "wishlists":               ("위시리스트 (고객-상품)", "Wishlists (customer-product)"),
    "complaints":              ("고객 불만 (유형, 우선순위)", "Complaints (type, priority)"),
    "returns":                 ("반품/교환 (사유, 상태)", "Returns (reason, status)"),
    "coupons":                 ("쿠폰 (할인율, 유효기간)", "Coupons (discount, validity)"),
    "coupon_usage":            ("쿠폰 사용 내역", "Coupon usage records"),
    "inventory_transactions":  ("재고 입출고 (유형, 수량)", "Inventory (type, quantity)"),
    "carts":                   ("장바구니 (상태)", "Carts (status)"),
    "cart_items":              ("장바구니 상품 (수량)", "Cart items (quantity)"),
    "calendar":                ("날짜 차원 (요일, 공휴일)", "Calendar (weekday, holiday)"),
    "customer_grade_history":  ("등급 이력 (변경 전후)", "Grade history (before/after)"),
    "tags":                    ("태그 (이름, 카테고리)", "Tags (name, category)"),
    "product_tags":            ("상품-태그 연결", "Product-tag mapping"),
    "product_views":           ("조회 로그 (고객, 상품, 일시)", "View log (customer, product, date)"),
    "point_transactions":      ("포인트 (적립, 사용, 소멸)", "Points (earn, use, expire)"),
    "promotions":              ("프로모션 (기간, 할인)", "Promotions (period, discount)"),
    "promotion_products":      ("프로모션 대상 상품", "Promotion products"),
    "product_qna":             ("상품 Q&A (질문-답변)", "Product Q&A (question-answer)"),
}

EXERCISES_DIR = Path("exercises")
LECTURES_DIR = Path("exercises/lectures")
DOCS_KO_DIR = Path("docs/ko/exercises")
DOCS_EN_DIR = Path("docs/en/exercises")
DOCS_KO_LESSONS = Path("docs/ko")

# 강의 MD 플레이스홀더
LESSON_BEGIN = "<!-- BEGIN_LESSON_EXERCISES -->"
LESSON_END = "<!-- END_LESSON_EXERCISES -->"


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)




def compute_expected(conn_tutorial, sql: str) -> tuple:
    """Execute reference SQL and compute expected results."""
    try:
        cursor = conn_tutorial.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        row_count = len(rows)

        # Hash for result comparison (sorted, stringified)
        sorted_rows = sorted(str(r) for r in rows)
        result_hash = hashlib.sha256("\n".join(sorted_rows).encode()).hexdigest()

        return json.dumps(columns), row_count, result_hash
    except Exception as e:
        print(f"    WARNING: SQL execution failed: {e}")
        return None, None, None


MAX_RESULT_ROWS = 7  # Show top N rows in result preview


def _execute_and_format(conn, sql: str, lang: str = "ko") -> str:
    """Execute SQL and return a markdown result table (top rows only)."""
    if not conn or not sql:
        return ""
    try:
        # Handle multi-statement SQL (DML etc.) - skip
        stripped = sql.strip().rstrip(";").strip()
        upper = stripped.upper()
        if any(upper.startswith(k) for k in ("INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "BEGIN", "COMMIT")):
            return ""

        cursor = conn.execute(sql.strip())
        if not cursor.description:
            return ""
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        total = len(rows)
        if total == 0:
            return ""

        # Build markdown table
        display_rows = rows[:MAX_RESULT_ROWS]
        lines = []
        header_label = "실행 결과" if lang == "ko" else "Result"
        if total > MAX_RESULT_ROWS:
            if lang == "ko":
                lines.append(f"\n    **{header_label}** (총 {total:,}행 중 상위 {MAX_RESULT_ROWS}행)\n")
            else:
                lines.append(f"\n    **{header_label}** (top {MAX_RESULT_ROWS} of {total:,} rows)\n")
        else:
            lines.append(f"\n    **{header_label}** ({total:,}{('행' if lang == 'ko' else ' rows')})\n")

        # Header
        lines.append("    | " + " | ".join(str(c) for c in columns) + " |")
        lines.append("    |" + "|".join("---" for _ in columns) + "|")

        # Rows
        for row in display_rows:
            cells = []
            for v in row:
                if v is None:
                    cells.append("NULL")
                elif isinstance(v, float):
                    cells.append(f"{v:,.2f}" if abs(v) >= 1 else f"{v}")
                elif isinstance(v, int):
                    cells.append(f"{v:,}" if abs(v) >= 10000 else str(v))
                else:
                    s = str(v)
                    if len(s) > 40:
                        s = s[:37] + "..."
                    cells.append(s)
            lines.append("    | " + " | ".join(cells) + " |")

        return "\n".join(lines) + "\n"
    except Exception:
        return ""


def compile_yaml_file(yaml_path: Path, conn_tutorial, sort_base: int, conn_tutorial_en=None) -> dict:
    """Compile a single YAML file into mkdocs markdown."""
    data = load_yaml(yaml_path)
    meta = data.get("metadata", {})

    exercise_id = meta["id"]
    print(f"  [{exercise_id}] {meta.get('title', '')} ({len(data.get('problems', []))} problems)")


    # Build mkdocs markdown (ko + en)
    md_ko_lines = [f"# {meta.get('title', exercise_id)}\n"]
    md_en_lines = [f"# {meta.get('title_en', exercise_id)}\n"]

    # Standard info block: admonition style (tables + concepts)
    tables = meta.get("tables", [])
    concepts = meta.get("concepts", [])

    if tables or concepts:
        for lines, lang in [(md_ko_lines, "ko"), (md_en_lines, "en")]:
            # Tables admonition
            if tables:
                title = "사용 테이블" if lang == "ko" else "Tables"
                lines.append(f'!!! info "{title}"\n')
                for t in tables:
                    desc_ko_t, desc_en_t = _TABLE_DESC.get(t, (t, t))
                    desc = desc_ko_t if lang == "ko" else desc_en_t
                    lines.append(f'    `{t}` — {desc}  \n')
                lines.append('\n')

            # Concepts admonition
            if concepts:
                title = "학습 범위" if lang == "ko" else "Concepts"
                concepts_str = ", ".join(f"`{c}`" for c in concepts)
                lines.append(f'!!! abstract "{title}"\n')
                lines.append(f'    {concepts_str}\n\n')

    problems = data.get("problems", [])
    for i, prob in enumerate(problems):
        pid = prob["id"]
        sort_order = sort_base * 100 + i + 1

        # Resolve reference SQL
        ref_sql = prob.get("reference_sql", {})
        if isinstance(ref_sql, str):
            ref_common = ref_sql
            ref_sqlite = ref_mysql = ref_pg = ref_oracle = ref_sqlserver = None
        else:
            ref_common = ref_sql.get("common") or ref_sql.get("all")
            ref_sqlite = ref_sql.get("sqlite")
            ref_mysql = ref_sql.get("mysql")
            ref_pg = ref_sql.get("postgresql")
            ref_oracle = ref_sql.get("oracle")
            ref_sqlserver = ref_sql.get("sqlserver")

        supported = prob.get("supported_db", ["sqlite", "mysql", "postgresql", "oracle", "sqlserver"])

        # Compute expected results
        exec_sql = ref_sqlite or ref_common
        exp_cols, exp_rows, exp_hash = None, None, None
        if conn_tutorial and exec_sql:
            exp_cols, exp_rows, exp_hash = compute_expected(conn_tutorial, exec_sql.strip())

        # Hints (support both "hints" array and single "hint"/"hint_en" strings)
        hints = prob.get("hints", [])
        if not hints:
            hint_ko = prob.get("hint", "")
            hint_en = prob.get("hint_en", "")
            if hint_ko:
                hints = [{"ko": hint_ko, "en": hint_en or hint_ko}]
        hints_json = json.dumps(hints, ensure_ascii=False) if hints else None

        # Validation
        validation = prob.get("validation", {"type": "result_match"})

        # Resolve level and type
        prob_level = prob.get("level", meta.get("level", 3))
        prob_type = prob.get("type", meta.get("type", "SELECT"))
        prob_tags = prob.get("tags", [])



        # Generate markdown
        num = i + 1
        # Support both "question" and "body" (with optional "title" prefix)
        body_ko = prob.get("question", "") or prob.get("body", "")
        body_en = prob.get("question_en", "") or prob.get("body_en", "") or body_ko
        title_ko = prob.get("title", "")
        title_en = prob.get("title_en", title_ko)

        # Heading: use title if available, otherwise first line of body
        heading_ko = title_ko or body_ko.strip().split("\n")[0][:60]
        heading_en = title_en or body_en.strip().split("\n")[0][:60]

        md_ko_lines.append(f"\n### {num}. {heading_ko}\n")
        md_ko_lines.append(f"\n{body_ko.strip()}\n")
        md_en_lines.append(f"\n### {num}. {heading_en}\n")
        md_en_lines.append(f"\n{body_en.strip()}\n")

        # Hints
        for hi, hint in enumerate(hints):
            if isinstance(hint, dict):
                hint_ko = hint.get("ko", "")
                hint_en = hint.get("en", hint_ko)
            else:
                hint_ko = hint_en = str(hint)
            md_ko_lines.append(f"\n**힌트 {hi+1}:** {hint_ko}\n")
            md_en_lines.append(f"\n**Hint {hi+1}:** {hint_en}\n")

        # Answer (collapsible)
        answer_sql = ref_common or ref_sqlite or ""
        db_tabs = [
            ("SQLite", ref_sqlite),
            ("MySQL", ref_mysql),
            ("PostgreSQL", ref_pg),
            ("Oracle", ref_oracle),
            ("SQL Server", ref_sqlserver),
        ]
        has_db_specific = any(sql for _, sql in db_tabs)
        if has_db_specific:
            # Multi-DB tabs
            md_ko_lines.append('\n??? success "정답"\n')
            md_en_lines.append('\n??? success "Answer"\n')
            for db_name, db_sql in db_tabs:
                if db_sql:
                    md_ko_lines.append(f'    === "{db_name}"\n        ```sql\n        {_indent(db_sql)}\n        ```\n')
                    md_en_lines.append(f'    === "{db_name}"\n        ```sql\n        {_indent(db_sql)}\n        ```\n')
        else:
            md_ko_lines.append(f'\n??? success "정답"\n    ```sql\n    {_indent(answer_sql)}\n    ```\n')
            md_en_lines.append(f'\n??? success "Answer"\n    ```sql\n    {_indent(answer_sql)}\n    ```\n')

        # Insert execution result table
        exec_sql_for_result = ref_sqlite or ref_common or answer_sql
        if exec_sql_for_result:
            result_ko = _execute_and_format(conn_tutorial, exec_sql_for_result.strip(), "ko")
            if result_ko:
                md_ko_lines.append(result_ko)
            result_en = _execute_and_format(conn_tutorial_en or conn_tutorial, exec_sql_for_result.strip(), "en")
            if result_en:
                md_en_lines.append(result_en)

        md_ko_lines.append("\n---\n")
        md_en_lines.append("\n---\n")

    return {
        "exercise_id": exercise_id,
        "md_ko": "\n".join(md_ko_lines),
        "md_en": "\n".join(md_en_lines),
        "problem_count": len(problems),
    }


def _to_str(val) -> str:
    """Convert value to string; dict/list become JSON."""
    if val is None:
        return ""
    if isinstance(val, (dict, list)):
        return json.dumps(val, ensure_ascii=False)
    return str(val)


def _indent(sql: str, prefix: str = "    ") -> str:
    """Indent multi-line SQL for markdown code blocks."""
    lines = sql.strip().split("\n")
    return f"\n{prefix}".join(lines)


def compile_lesson_yaml(yaml_path: Path, conn_tutorial, sort_base: int) -> dict:
    """Compile a lesson YAML and inject exercises into the lesson MD file."""
    data = load_yaml(yaml_path)
    meta = data.get("metadata", {})
    exercise_id = meta["id"]
    lesson_path = meta.get("lesson", "")  # e.g. "beginner/01-select"

    title_safe = meta.get('title', '').encode('ascii', 'replace').decode('ascii')
    print(f"  [{exercise_id}] {title_safe} -> {lesson_path}")


    problems = data.get("problems", [])

    # Generate exercise markdown block
    md_lines = []
    md_lines.append(LESSON_BEGIN)
    md_lines.append("")
    md_lines.append('!!! note "레슨 복습 문제"')
    md_lines.append('    이 레슨에서 배운 개념을 바로 확인하는 간단한 문제입니다. '
                     '여러 개념을 종합하는 실전 연습은 [연습 문제](../exercises/index.md) 섹션을 참고하세요.')
    md_lines.append("")

    for i, prob in enumerate(problems):
        pid = prob["id"]
        sort_order = sort_base * 100 + i + 1

        ref_sql = prob.get("reference_sql", {})
        if isinstance(ref_sql, str):
            ref_common = ref_sql
            ref_sqlite = ref_mysql = ref_pg = ref_oracle = ref_sqlserver = None
        else:
            ref_common = ref_sql.get("common") or ref_sql.get("all")
            ref_sqlite = ref_sql.get("sqlite")
            ref_mysql = ref_sql.get("mysql")
            ref_pg = ref_sql.get("postgresql")
            ref_oracle = ref_sql.get("oracle")
            ref_sqlserver = ref_sql.get("sqlserver")

        supported = prob.get("supported_db", ["sqlite", "mysql", "postgresql", "oracle", "sqlserver"])
        exec_sql = ref_sqlite or ref_common
        exp_cols, exp_rows, exp_hash = None, None, None
        if conn_tutorial and exec_sql:
            exp_cols, exp_rows, exp_hash = compute_expected(conn_tutorial, exec_sql.strip())

        hints = prob.get("hints", [])
        hints_json = json.dumps(hints, ensure_ascii=False) if hints else None

        validation = prob.get("validation", {"type": "result_match"})
        prob_level = prob.get("level", meta.get("default_level", 3))
        prob_type = prob.get("type", meta.get("default_type", "SELECT"))
        prob_tags = prob.get("tags", [])


        # Markdown block
        num = i + 1
        body = prob.get("question", "").strip()
        answer_sql = ref_common or ref_sqlite or ""

        md_lines.append(f"### 문제 {num}")
        md_lines.append(body)
        md_lines.append("")

        db_tabs = [
            ("SQLite", ref_sqlite),
            ("MySQL", ref_mysql),
            ("PostgreSQL", ref_pg),
            ("Oracle", ref_oracle),
            ("SQL Server", ref_sqlserver),
        ]
        has_db_specific = any(sql for _, sql in db_tabs)
        if has_db_specific:
            md_lines.append(f'??? success "정답"')
            for db_name, db_sql in db_tabs:
                if db_sql:
                    md_lines.append(f'    === "{db_name}"')
                    md_lines.append(f"        ```sql")
                    for sql_line in db_sql.strip().split("\n"):
                        md_lines.append(f"        {sql_line}")
                    md_lines.append(f"        ```")
                    md_lines.append("")
        else:
            md_lines.append(f'??? success "정답"')
            md_lines.append(f"    ```sql")
            for sql_line in answer_sql.strip().split("\n"):
                md_lines.append(f"    {sql_line}")
            md_lines.append(f"    ```")
            md_lines.append("")

        # Insert execution result for lesson exercises
        exec_sql_for_result = ref_sqlite or ref_common or answer_sql
        if exec_sql_for_result:
            result_table = _execute_and_format(conn_tutorial, exec_sql_for_result.strip(), "ko")
            if result_table:
                md_lines.append(result_table)

    md_lines.append(LESSON_END)

    # Inject into lesson MD if it has placeholder, or replace existing exercises
    md_block = "\n".join(md_lines)

    if lesson_path:
        lesson_md_path = DOCS_KO_LESSONS / f"{lesson_path}.md"
        if lesson_md_path.exists():
            content = lesson_md_path.read_text(encoding="utf-8")

            if LESSON_BEGIN in content:
                # Replace between placeholders
                before = content[:content.index(LESSON_BEGIN)]
                after_marker = content.find(LESSON_END)
                if after_marker >= 0:
                    after = content[after_marker + len(LESSON_END):]
                else:
                    after = ""
                new_content = before + md_block + after
            else:
                # Find existing "!!! note "레슨 복습 문제" and replace from there to end
                marker = '!!! note "레슨 복습 문제"'
                idx = content.find(marker)
                if idx >= 0:
                    # Go back to find the --- before the note
                    before_idx = content.rfind("---", 0, idx)
                    if before_idx >= 0:
                        before = content[:before_idx + 3] + "\n\n"
                    else:
                        before = content[:idx]
                    new_content = before + md_block + "\n"
                else:
                    # Append at end
                    new_content = content.rstrip() + "\n\n---\n\n" + md_block + "\n"

            lesson_md_path.write_text(new_content, encoding="utf-8")
            print(f"    → {lesson_md_path} 갱신 ({len(problems)}문제)")

    return {
        "exercise_id": exercise_id,
        "problem_count": len(problems),
        "lesson_path": lesson_path,
    }


def main():
    parser = argparse.ArgumentParser(description="Compile exercise YAML to mkdocs markdown")
    parser.add_argument("--tutorial-db", type=str, default="output/ecommerce-ko.db",
                        help="Tutorial DB for computing expected results and result tables")
    parser.add_argument("--validate-only", action="store_true", help="Validate only, no output")
    parser.add_argument("--file", type=str, help="Compile a single YAML file")
    args = parser.parse_args()

    # Find YAML files (exclude lectures — processed separately)
    if args.file:
        yaml_files = [Path(args.file)]
    else:
        yaml_files = sorted(
            f for f in EXERCISES_DIR.rglob("*.yaml")
            if "lectures" not in f.parts
        )
    lecture_files = sorted(LECTURES_DIR.glob("*.yaml")) if LECTURES_DIR.exists() else []

    if not yaml_files:
        print("No YAML exercise files found in exercises/")
        return

    print(f"Found {len(yaml_files)} exercise files")

    # Connect to tutorial DBs for expected result computation
    conn_tutorial = None
    if os.path.exists(args.tutorial_db):
        conn_tutorial = sqlite3.connect(args.tutorial_db)
        print(f"Using tutorial DB (ko): {args.tutorial_db}")

    # English DB for result tables in en docs
    en_db_path = args.tutorial_db.replace("-ko.db", "-en.db")
    conn_tutorial_en = None
    if os.path.exists(en_db_path):
        conn_tutorial_en = sqlite3.connect(en_db_path)
        print(f"Using tutorial DB (en): {en_db_path}")

    if args.validate_only:
        # Just parse and validate
        for yf in yaml_files:
            try:
                data = load_yaml(yf)
                meta = data.get("metadata", {})
                problems = data.get("problems", [])
                print(f"  OK  {yf} -{meta.get('id', '?')}: {len(problems)} problems")
            except Exception as e:
                print(f"  ERR {yf} -{e}")
        return

    os.makedirs(DOCS_KO_DIR, exist_ok=True)
    os.makedirs(DOCS_EN_DIR, exist_ok=True)

    total_problems = 0
    for i, yf in enumerate(yaml_files):
        try:
            result = compile_yaml_file(yf, conn_tutorial, sort_base=i + 1, conn_tutorial_en=conn_tutorial_en)
            total_problems += result["problem_count"]

            # Write mkdocs markdown
            md_filename = f"{result['exercise_id']}.md"
            ko_path = DOCS_KO_DIR / md_filename
            en_path = DOCS_EN_DIR / md_filename

            ko_path.write_text(result["md_ko"], encoding="utf-8")
            en_path.write_text(result["md_en"], encoding="utf-8")

        except Exception as e:
            print(f"  ERR {yf}: {e}")
            import traceback
            traceback.print_exc()

    # Compile lesson YAML files
    lesson_problems = 0
    if lecture_files and not args.file:
        print(f"\n=== Lesson exercises ({len(lecture_files)} files) ===")
        for j, lf in enumerate(lecture_files):
            try:
                result = compile_lesson_yaml(lf, conn_tutorial,
                                              sort_base=len(yaml_files) + j + 1)
                lesson_problems += result["problem_count"]
            except Exception as e:
                print(f"  ERR {lf}: {e}")
                import traceback
                traceback.print_exc()

    if conn_tutorial:
        conn_tutorial.close()
    if conn_tutorial_en:
        conn_tutorial_en.close()

    print(f"\nCompiled {len(yaml_files)} exercise files, {total_problems} problems")
    if lecture_files:
        print(f"  + {len(lecture_files)} lesson files, {lesson_problems} problems")
    print(f"  mkdocs (ko): {DOCS_KO_DIR}/")
    print(f"  mkdocs (en): {DOCS_EN_DIR}/")


if __name__ == "__main__":
    main()
