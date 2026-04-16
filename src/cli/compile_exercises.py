#!/usr/bin/env python3
"""Compile exercise YAML files into mkdocs markdown and exercise.db.

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


EXERCISES_DIR = Path("exercises")
LECTURES_DIR = Path("exercises/lectures")
DOCS_KO_DIR = Path("docs/ko/exercises")
DOCS_EN_DIR = Path("docs/en/exercises")
DOCS_KO_LESSONS = Path("docs/ko")
OUTPUT_DB = Path("output/exercise.db")

# 강의 MD 플레이스홀더
LESSON_BEGIN = "<!-- BEGIN_LESSON_EXERCISES -->"
LESSON_END = "<!-- END_LESSON_EXERCISES -->"


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def create_exercise_db(db_path: Path):
    """Create exercise.db schema."""
    os.makedirs(db_path.parent, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    conn.executescript("""
        CREATE TABLE exercise_sets (
            id              TEXT PRIMARY KEY,
            title           TEXT NOT NULL,
            title_en        TEXT,
            difficulty      TEXT NOT NULL,
            concepts        TEXT NOT NULL,
            prerequisites   TEXT,
            estimated_minutes INTEGER,
            sort_order      INTEGER NOT NULL,
            created_at      TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE problems (
            id              TEXT PRIMARY KEY,
            exercise_id     TEXT NOT NULL REFERENCES exercise_sets(id),
            question        TEXT NOT NULL,
            question_en     TEXT,
            level           INTEGER DEFAULT 3,
            type            TEXT DEFAULT 'SELECT',
            reference_sql_common TEXT,
            reference_sql_sqlite TEXT,
            reference_sql_mysql TEXT,
            reference_sql_postgresql TEXT,
            reference_sql_oracle TEXT,
            reference_sql_sqlserver TEXT,
            supported_db    TEXT NOT NULL DEFAULT '["sqlite","mysql","postgresql","oracle","sqlserver"]',
            validation_json TEXT NOT NULL,
            hints_json      TEXT,
            rubric          TEXT,
            rubric_en       TEXT,
            max_score       INTEGER DEFAULT 10,
            tags_json       TEXT,
            sort_order      INTEGER NOT NULL,
            expected_columns TEXT,
            expected_row_count INTEGER,
            expected_hash   TEXT
        );

        CREATE TABLE exercise_tags (
            tag             TEXT PRIMARY KEY,
            category        TEXT NOT NULL
        );

        CREATE TABLE problem_tags (
            problem_id      TEXT NOT NULL REFERENCES problems(id),
            tag             TEXT NOT NULL,
            PRIMARY KEY (problem_id, tag)
        );

        CREATE TABLE attempts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id      TEXT NOT NULL REFERENCES problems(id),
            user_sql        TEXT NOT NULL,
            syntax_valid    INTEGER NOT NULL,
            columns_match   INTEGER NOT NULL,
            row_count_match INTEGER NOT NULL,
            data_match      INTEGER NOT NULL,
            result_hash     TEXT,
            det_score       INTEGER NOT NULL,
            ai_score        INTEGER,
            ai_feedback     TEXT,
            total_score     INTEGER NOT NULL,
            execution_ms    INTEGER,
            row_count       INTEGER,
            attempted_at    TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE progress (
            problem_id      TEXT PRIMARY KEY REFERENCES problems(id),
            best_score      INTEGER NOT NULL DEFAULT 0,
            attempt_count   INTEGER NOT NULL DEFAULT 0,
            completed       INTEGER NOT NULL DEFAULT 0,
            first_solved_at TEXT,
            last_attempt_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE badges (
            id              TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            name_en         TEXT,
            description     TEXT NOT NULL,
            description_en  TEXT,
            icon            TEXT,
            condition_sql   TEXT NOT NULL,
            earned_at       TEXT
        );

        CREATE INDEX idx_problems_exercise_id ON problems(exercise_id);
        CREATE INDEX idx_attempts_problem_id ON attempts(problem_id);
    """)
    return conn


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


def compile_yaml_file(yaml_path: Path, conn_db, conn_tutorial, sort_base: int) -> dict:
    """Compile a single YAML file into exercise.db + mkdocs markdown."""
    data = load_yaml(yaml_path)
    meta = data.get("metadata", {})

    exercise_id = meta["id"]
    print(f"  [{exercise_id}] {meta.get('title', '')} ({len(data.get('problems', []))} problems)")

    # Insert exercise set
    conn_db.execute(
        "INSERT INTO exercise_sets (id, title, title_en, difficulty, concepts, prerequisites, estimated_minutes, sort_order) VALUES (?,?,?,?,?,?,?,?)",
        (
            exercise_id,
            meta.get("title", ""),
            meta.get("title_en", ""),
            meta.get("difficulty", "beginner"),
            json.dumps(meta.get("concepts", []), ensure_ascii=False),
            json.dumps(meta.get("prerequisites", []), ensure_ascii=False),
            meta.get("estimated_minutes"),
            sort_base,
        ),
    )

    # Build mkdocs markdown (ko + en)
    md_ko_lines = [f"# {meta.get('title', exercise_id)}\n"]
    md_en_lines = [f"# {meta.get('title_en', exercise_id)}\n"]

    # Standard info block: tables + concepts
    tables = meta.get("tables", [])
    concepts = meta.get("concepts", [])
    desc_ko = meta.get("description", "")
    desc_en = meta.get("description_en", "")

    if tables or concepts:
        if tables:
            tables_str = ", ".join(f"`{t}`" for t in tables)
            md_ko_lines.append(f"**사용 테이블:** {tables_str}\n")
            md_en_lines.append(f"**Tables:** {tables_str}\n")
        if concepts:
            concepts_str = ", ".join(concepts)
            md_ko_lines.append(f"**학습 범위:** {concepts_str}\n")
            md_en_lines.append(f"**Concepts:** {concepts_str}\n")
        md_ko_lines.append("\n---\n")
        md_en_lines.append("\n---\n")
    elif desc_ko or desc_en:
        if desc_ko:
            md_ko_lines.append(f"{desc_ko}\n\n---\n")
        if desc_en:
            md_en_lines.append(f"{desc_en}\n\n---\n")

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

        # Insert problem
        conn_db.execute(
            """INSERT INTO problems (id, exercise_id, question, question_en,
               level, type,
               reference_sql_common, reference_sql_sqlite, reference_sql_mysql, reference_sql_postgresql,
               reference_sql_oracle, reference_sql_sqlserver,
               supported_db, validation_json, hints_json, rubric, rubric_en,
               max_score, tags_json, sort_order, expected_columns, expected_row_count, expected_hash)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                pid, exercise_id,
                prob.get("question", "") or prob.get("body", ""),
                prob.get("question_en", "") or prob.get("body_en", ""),
                prob_level, prob_type,
                ref_common, ref_sqlite, ref_mysql, ref_pg, ref_oracle, ref_sqlserver,
                json.dumps(supported),
                json.dumps(validation, ensure_ascii=False),
                hints_json,
                _to_str(prob.get("rubric", "")),
                _to_str(prob.get("rubric_en", "")),
                prob.get("max_score", 10),
                json.dumps(prob_tags, ensure_ascii=False),
                sort_order,
                exp_cols, exp_rows, exp_hash,
            ),
        )

        # Insert problem-tag mappings
        for tag in prob_tags:
            conn_db.execute(
                "INSERT OR IGNORE INTO problem_tags (problem_id, tag) VALUES (?,?)",
                (pid, tag),
            )

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


def compile_lesson_yaml(yaml_path: Path, conn_db, conn_tutorial, sort_base: int) -> dict:
    """Compile a lesson YAML and inject exercises into the lesson MD file."""
    data = load_yaml(yaml_path)
    meta = data.get("metadata", {})
    exercise_id = meta["id"]
    lesson_path = meta.get("lesson", "")  # e.g. "beginner/01-select"

    title_safe = meta.get('title', '').encode('ascii', 'replace').decode('ascii')
    print(f"  [{exercise_id}] {title_safe} -> {lesson_path}")

    # Insert into exercise.db (same as regular exercises)
    conn_db.execute(
        "INSERT INTO exercise_sets (id, title, title_en, difficulty, concepts, prerequisites, estimated_minutes, sort_order) VALUES (?,?,?,?,?,?,?,?)",
        (
            exercise_id,
            meta.get("title", ""),
            meta.get("title_en", ""),
            meta.get("difficulty", "beginner"),
            json.dumps(meta.get("concepts", []), ensure_ascii=False),
            json.dumps(meta.get("prerequisites", []), ensure_ascii=False),
            meta.get("estimated_minutes"),
            sort_base,
        ),
    )

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

        conn_db.execute(
            """INSERT INTO problems (id, exercise_id, question, question_en,
               level, type,
               reference_sql_common, reference_sql_sqlite, reference_sql_mysql, reference_sql_postgresql,
               reference_sql_oracle, reference_sql_sqlserver,
               supported_db, validation_json, hints_json, rubric, rubric_en,
               max_score, tags_json, sort_order, expected_columns, expected_row_count, expected_hash)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                pid, exercise_id,
                prob.get("question", ""),
                prob.get("question_en", ""),
                prob_level, prob_type,
                ref_common, ref_sqlite, ref_mysql, ref_pg, ref_oracle, ref_sqlserver,
                json.dumps(supported),
                json.dumps(validation, ensure_ascii=False),
                hints_json,
                _to_str(prob.get("rubric", "")),
                _to_str(prob.get("rubric_en", "")),
                prob.get("max_score", 10),
                json.dumps(prob_tags, ensure_ascii=False),
                sort_order,
                exp_cols, exp_rows, exp_hash,
            ),
        )

        for tag in prob_tags:
            conn_db.execute(
                "INSERT OR IGNORE INTO problem_tags (problem_id, tag) VALUES (?,?)",
                (pid, tag),
            )

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
    parser = argparse.ArgumentParser(description="Compile exercise YAML to mkdocs + exercise.db")
    parser.add_argument("--tutorial-db", type=str, default="output/ecommerce-ko.db",
                        help="Tutorial DB for computing expected results")
    parser.add_argument("--output-db", type=str, default=str(OUTPUT_DB),
                        help="Output exercise.db path")
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

    # Connect to tutorial DB for expected result computation
    conn_tutorial = None
    if os.path.exists(args.tutorial_db):
        conn_tutorial = sqlite3.connect(args.tutorial_db)
        print(f"Using tutorial DB: {args.tutorial_db}")

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

    # Create exercise.db
    conn_db = create_exercise_db(Path(args.output_db))
    os.makedirs(DOCS_KO_DIR, exist_ok=True)
    os.makedirs(DOCS_EN_DIR, exist_ok=True)

    total_problems = 0
    for i, yf in enumerate(yaml_files):
        try:
            result = compile_yaml_file(yf, conn_db, conn_tutorial, sort_base=i + 1)
            total_problems += result["problem_count"]

            # Write mkdocs markdown
            md_filename = f"{result['exercise_id']}.md"
            ko_path = DOCS_KO_DIR / md_filename
            en_path = DOCS_EN_DIR / md_filename

            # Only write if file doesn't exist OR is auto-generated
            # (preserve hand-written files)
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
                result = compile_lesson_yaml(lf, conn_db, conn_tutorial,
                                              sort_base=len(yaml_files) + j + 1)
                lesson_problems += result["problem_count"]
            except Exception as e:
                print(f"  ERR {lf}: {e}")
                import traceback
                traceback.print_exc()

    conn_db.commit()
    conn_db.close()
    if conn_tutorial:
        conn_tutorial.close()

    print(f"\nCompiled {len(yaml_files)} exercise files, {total_problems} problems")
    if lecture_files:
        print(f"  + {len(lecture_files)} lesson files, {lesson_problems} problems")
    print(f"  exercise.db: {args.output_db}")
    print(f"  mkdocs (ko): {DOCS_KO_DIR}/")
    print(f"  mkdocs (en): {DOCS_EN_DIR}/")


if __name__ == "__main__":
    main()
