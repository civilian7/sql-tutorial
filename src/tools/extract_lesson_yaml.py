#!/usr/bin/env python3
"""강의 MD에서 복습 문제를 추출하여 YAML 파일을 생성합니다.

Usage:
    python tools/extract_lesson_yaml.py
"""

import re
import sys
from pathlib import Path

DOCS_KO = Path("docs/ko")
OUTPUT_DIR = Path("exercises/lectures")

LEVELS = {
    "beginner": ("beginner", [
        "00-introduction", "01-select", "02-where", "03-sort-limit",
        "04-aggregates", "05-group-by", "06-null", "07-case",
    ]),
    "intermediate": ("intermediate", [
        "08-inner-join", "09-left-join", "10-subqueries", "11-datetime",
        "12-string", "13-utility-functions", "14-union", "15-dml",
        "16-ddl", "17-transactions",
    ]),
    "advanced": ("advanced", [
        "18-window", "19-cte", "20-exists", "21-self-cross-join",
        "22-views", "23-indexes", "24-triggers", "25-json",
        "26-stored-procedures",
    ]),
}

# 강의번호 → 개념 매핑
CONCEPTS = {
    "00-introduction": ["SELECT", "기본 조회"],
    "01-select": ["SELECT", "AS", "DISTINCT", "산술 연산"],
    "02-where": ["WHERE", "비교 연산자", "AND", "OR", "BETWEEN", "IN", "LIKE"],
    "03-sort-limit": ["ORDER BY", "LIMIT", "OFFSET"],
    "04-aggregates": ["COUNT", "SUM", "AVG", "MIN", "MAX"],
    "05-group-by": ["GROUP BY", "HAVING"],
    "06-null": ["IS NULL", "IS NOT NULL", "COALESCE", "IFNULL"],
    "07-case": ["CASE WHEN", "조건 분기"],
    "08-inner-join": ["INNER JOIN", "ON", "다중 조인"],
    "09-left-join": ["LEFT JOIN", "RIGHT JOIN", "FULL JOIN"],
    "10-subqueries": ["서브쿼리", "IN", "EXISTS", "스칼라 서브쿼리"],
    "11-datetime": ["DATE", "TIME", "DATETIME", "날짜 함수"],
    "12-string": ["문자열 함수", "SUBSTR", "LENGTH", "REPLACE", "UPPER", "LOWER"],
    "13-utility-functions": ["CAST", "TYPEOF", "ROUND", "ABS", "RANDOM"],
    "14-union": ["UNION", "UNION ALL", "INTERSECT", "EXCEPT"],
    "15-dml": ["INSERT", "UPDATE", "DELETE"],
    "16-ddl": ["CREATE TABLE", "ALTER TABLE", "DROP TABLE"],
    "17-transactions": ["BEGIN", "COMMIT", "ROLLBACK", "SAVEPOINT"],
    "18-window": ["ROW_NUMBER", "RANK", "DENSE_RANK", "LAG", "LEAD", "SUM OVER"],
    "19-cte": ["WITH", "CTE", "재귀 CTE"],
    "20-exists": ["EXISTS", "NOT EXISTS", "안티 조인"],
    "21-self-cross-join": ["SELF JOIN", "CROSS JOIN"],
    "22-views": ["CREATE VIEW", "DROP VIEW"],
    "23-indexes": ["CREATE INDEX", "실행 계획", "EXPLAIN"],
    "24-triggers": ["CREATE TRIGGER", "BEFORE", "AFTER"],
    "25-json": ["JSON_EXTRACT", "JSON_EACH", "JSON_GROUP_ARRAY"],
    "26-stored-procedures": ["저장 프로시저", "함수"],
}

TITLE_MAP = {
    "00-introduction": ("시작하기", "Getting Started"),
    "01-select": ("SELECT 기초", "SELECT Basics"),
    "02-where": ("WHERE 필터링", "WHERE Filtering"),
    "03-sort-limit": ("정렬과 페이징", "Sorting and Paging"),
    "04-aggregates": ("집계 함수", "Aggregate Functions"),
    "05-group-by": ("GROUP BY", "GROUP BY"),
    "06-null": ("NULL 처리", "Handling NULL"),
    "07-case": ("CASE 조건문", "CASE Expressions"),
    "08-inner-join": ("INNER JOIN", "INNER JOIN"),
    "09-left-join": ("LEFT JOIN", "LEFT JOIN"),
    "10-subqueries": ("서브쿼리", "Subqueries"),
    "11-datetime": ("날짜/시간 함수", "Date/Time Functions"),
    "12-string": ("문자열 함수", "String Functions"),
    "13-utility-functions": ("유틸리티 함수", "Utility Functions"),
    "14-union": ("집합 연산", "Set Operations"),
    "15-dml": ("데이터 변경 (DML)", "Data Manipulation"),
    "16-ddl": ("테이블 관리 (DDL)", "Table Management"),
    "17-transactions": ("트랜잭션", "Transactions"),
    "18-window": ("윈도우 함수", "Window Functions"),
    "19-cte": ("CTE", "Common Table Expressions"),
    "20-exists": ("EXISTS와 안티 패턴", "EXISTS and Anti-patterns"),
    "21-self-cross-join": ("셀프/크로스 조인", "Self/Cross Join"),
    "22-views": ("뷰", "Views"),
    "23-indexes": ("인덱스", "Indexes"),
    "24-triggers": ("트리거", "Triggers"),
    "25-json": ("JSON 함수", "JSON Functions"),
    "26-stored-procedures": ("저장 프로시저", "Stored Procedures"),
}


def extract_problems(md_path: Path) -> list:
    """MD에서 ### 문제/연습 N 블록을 추출."""
    text = md_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    problems = []
    i = 0

    while i < len(lines):
        m = re.match(r'^###\s+(?:문제|연습)\s+(\d+)', lines[i])
        if m:
            num = int(m.group(1))
            # 문제 텍스트 수집
            question_lines = []
            j = i + 1
            while j < len(lines):
                line = lines[j].strip()
                if line.startswith("### ") or line.startswith("## ") or line.startswith("???"):
                    break
                if line and not line.startswith("---"):
                    question_lines.append(line)
                j += 1

            # SQL 추출
            sql_lines = []
            in_success = False
            in_sql = False
            k = i + 1
            while k < len(lines):
                sline = lines[k]
                stripped = sline.strip()
                if stripped.startswith("### ") or stripped.startswith("## "):
                    break
                if stripped.startswith('??? success'):
                    in_success = True
                elif in_success and stripped.startswith("```sql"):
                    in_sql = True
                elif in_success and in_sql and stripped.startswith("```"):
                    in_sql = False
                    in_success = False
                elif in_sql:
                    sql_lines.append(sline.strip())
                k += 1

            question = "\n".join(question_lines).strip()
            sql = "\n".join(sql_lines).strip()

            if question and sql:
                problems.append({
                    "num": num,
                    "question": question,
                    "sql": sql,
                })
            i = k
        else:
            i += 1

    return problems


def yaml_escape(s: str) -> str:
    """YAML 문자열 이스케이프."""
    return s.replace("\\", "\\\\")


def generate_yaml(lesson_name: str, difficulty: str, problems: list) -> str:
    """YAML 문자열을 생성합니다."""
    title_ko, title_en = TITLE_MAP.get(lesson_name, (lesson_name, lesson_name))
    concepts = CONCEPTS.get(lesson_name, [])
    num_str = lesson_name.split("-")[0]

    lines = []
    lines.append("metadata:")
    lines.append(f'  id: lesson-{lesson_name}')
    lines.append(f'  title: "{title_ko} — 레슨 복습"')
    lines.append(f'  title_en: "{title_en} — Lesson Review"')
    lines.append(f"  difficulty: {difficulty}")
    lines.append(f'  lesson: "{difficulty}/{lesson_name}"')
    lines.append(f"  concepts: {concepts}")
    lines.append(f"  estimated_minutes: {max(5, len(problems) * 2)}")
    lines.append("")
    lines.append("  video:")
    lines.append(f'    output_dir: "lectures/{difficulty}"')
    lines.append(f'    filename: "lesson_{lesson_name.replace("-", "_")}_review.mp4"')
    lines.append(f"    fps: 15")
    lines.append(f'    intro_text: "{num_str}강 {title_ko} — 복습 문제"')
    lines.append(f'    intro_effect: "fadeIn"')
    lines.append(f"    intro_duration_ms: 3000")
    lines.append(f'    question_effect: "slideUp"')
    lines.append(f"    question_duration_ms: 3000")
    lines.append(f"    answer_delay_ms: 2000")
    lines.append(f"    result_delay_ms: 3000")
    lines.append(f'    outro_text: "수고하셨습니다!"')
    lines.append(f'    outro_effect: "fadeOut"')
    lines.append("")
    lines.append("  tts:")
    lines.append(f"    enabled: false")
    lines.append(f'    provider: "clova"')
    lines.append(f'    voice: "nara"')
    lines.append(f"    speed: 1.0")
    lines.append(f'    intro_script: "{num_str}강 {title_ko} 복습 문제입니다."')
    lines.append(f'    outro_script: "수고하셨습니다. 다음 강의에서 만나요."')
    lines.append("")
    lines.append("problems:")

    for prob in problems:
        pid = f"L{num_str}-{prob['num']:02d}"
        lines.append(f"  - id: {pid}")
        lines.append(f"    level: 2")
        lines.append(f'    type: "SELECT"')
        lines.append(f"    question: |")
        for qline in prob["question"].split("\n"):
            lines.append(f"      {qline}")
        lines.append(f"    reference_sql:")
        lines.append(f"      common: |")
        for sline in prob["sql"].split("\n"):
            lines.append(f"        {sline}")
        lines.append(f"    tags: []")
        lines.append("")

    return "\n".join(lines)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0

    for difficulty, (subdir, lessons) in LEVELS.items():
        for lesson_name in lessons:
            md_path = DOCS_KO / subdir / f"{lesson_name}.md"
            if not md_path.exists():
                continue

            problems = extract_problems(md_path)
            if not problems:
                print(f"  {lesson_name}: 문제 없음")
                continue

            yaml_content = generate_yaml(lesson_name, difficulty, problems)
            yaml_path = OUTPUT_DIR / f"{lesson_name}.yaml"

            # 이미 존재하면 건너뜀 (수동 편집 보존)
            if yaml_path.exists():
                print(f"  {lesson_name}: 이미 존재 ({len(problems)}문제)")
                continue

            yaml_path.write_text(yaml_content, encoding="utf-8")
            print(f"  {lesson_name}: {len(problems)}문제 → {yaml_path.name}")
            total += len(problems)

    print(f"\n완료: {total}개 문제 추출")


if __name__ == "__main__":
    main()
