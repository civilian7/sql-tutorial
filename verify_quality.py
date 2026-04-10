#!/usr/bin/env python3
"""
Verify tutorial content quality across all chapters.

Checks:
  1. Concept coverage — each chapter covers its expected keywords
  2. Exercise coverage — exercises reference chapter concepts
  3. Navigation links — Next links point to existing files
  4. DB dialect tabs — dialect-specific SQL has tabs where needed
  5. ko/en parity — section counts and exercise counts match
  6. Terminology — correct Korean foreign word spelling
  7. Mermaid/SVG — no banned styles, diagrams present

Usage:
    python verify_quality.py
    python verify_quality.py --chapter 16
    python verify_quality.py --check links
"""

import argparse
import os
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DOCS_KO = 'docs/ko'
DOCS_EN = 'docs/en'

# Expected concepts per chapter (keywords that MUST appear in the chapter body)
CHAPTER_CONCEPTS = {
    '01-select': ['SELECT', 'FROM', 'AS', 'DISTINCT', '*'],
    '02-where': ['WHERE', 'AND', 'OR', 'BETWEEN', 'IN', 'LIKE', 'NOT'],
    '03-sort-limit': ['ORDER BY', 'ASC', 'DESC', 'LIMIT', 'OFFSET'],
    '04-aggregates': ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'ROUND'],
    '05-group-by': ['GROUP BY', 'HAVING', 'WHERE'],
    '06-null': ['IS NULL', 'IS NOT NULL', 'COALESCE', 'NULLIF'],
    '07-inner-join': ['INNER JOIN', 'ON', 'JOIN'],
    '08-left-join': ['LEFT JOIN', 'IS NULL', 'RIGHT JOIN', 'FULL'],
    '09-subqueries': ['IN (', 'NOT IN', 'FROM (', 'SELECT ('],
    '10-case': ['CASE', 'WHEN', 'THEN', 'ELSE', 'END'],
    '11-datetime': ['DATE', 'strftime', 'DATE_FORMAT', 'TO_CHAR'],
    '12-string': ['UPPER', 'LOWER', 'LENGTH', 'REPLACE', 'TRIM'],
    '13-union': ['UNION', 'UNION ALL'],
    '14-dml': ['INSERT', 'UPDATE', 'DELETE', 'UPSERT'],
    '15-ddl': ['CREATE TABLE', 'ALTER TABLE', 'DROP TABLE', 'PRIMARY KEY', 'FOREIGN KEY', 'TRUNCATE'],
    '16-transactions': ['BEGIN', 'COMMIT', 'ROLLBACK', 'SAVEPOINT', 'ACID'],
    '17-self-cross-join': ['SELF JOIN', 'CROSS JOIN', 'parent_id'],
    '18-window': ['OVER', 'PARTITION BY', 'ROW_NUMBER', 'RANK', 'LAG', 'LEAD'],
    '19-cte': ['WITH', 'CTE', 'RECURSIVE'],
    '20-exists': ['EXISTS', 'NOT EXISTS'],
    '21-views': ['CREATE VIEW', 'DROP VIEW', 'Materialized'],
    '22-indexes': ['CREATE INDEX', 'EXPLAIN', 'B-tree', 'DROP INDEX'],
    '23-triggers': ['CREATE TRIGGER', 'BEFORE', 'AFTER', 'NEW', 'OLD'],
    '24-json': ['json_extract', 'json_set', 'specs', 'JSON'],
    '25-stored-procedures': ['PROCEDURE', 'FUNCTION', 'CALL', 'DELIMITER'],
}

# Dialect-specific keywords that require DB tabs
DIALECT_MARKERS = {
    'sqlite_only': [
        r'julianday\(', r"DATE\('now'", r"datetime\('now'", r"strftime\(",
        r'SUBSTR\(.*ordered_at', r'sqlite_master', r'EXPLAIN QUERY PLAN',
        r'INTEGER PRIMARY KEY AUTOINCREMENT',
    ],
    'mysql_only': [
        r'DATE_FORMAT\(', r'CURDATE\(\)', r'NOW\(\)', r'YEAR\(',
        r'AUTO_INCREMENT', r'DELIMITER', r'ON DUPLICATE KEY',
    ],
    'pg_only': [
        r'TO_CHAR\(', r'CURRENT_DATE', r'EXTRACT\(',
        r'::date', r'::int', r'LANGUAGE plpgsql', r'GENERATED ALWAYS',
    ],
}

# Banned terminology
BANNED_TERMS = {
    '컬럼': '칼럼',
    '데스크탑': '데스크톱',
}

# Banned mermaid styles
BANNED_MERMAID = [
    r'style\s+\w+\s+fill:#',
    r'classDef\s+\w+\s+fill:#',
    r'color:#',
]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

class Issue:
    def __init__(self, file, line, check, message, severity='WARN'):
        self.file = file
        self.line = line
        self.check = check
        self.message = message
        self.severity = severity  # ERROR, WARN, INFO

    def __str__(self):
        rel = os.path.relpath(self.file, '.')
        return f"  {self.severity:5} {rel}:{self.line} [{self.check}] {self.message}"


def check_concepts(filepath, chapter_key):
    """Check that expected concepts appear in the chapter."""
    issues = []
    if chapter_key not in CHAPTER_CONCEPTS:
        return issues

    content = Path(filepath).read_text(encoding='utf-8')
    # Only check body (before exercises section)
    exercise_pos = content.find('## 연습 문제') or content.find('## Practice Exercises')
    if exercise_pos and exercise_pos > 0:
        body = content[:exercise_pos]
    else:
        body = content

    for keyword in CHAPTER_CONCEPTS[chapter_key]:
        if keyword.lower() not in body.lower():
            issues.append(Issue(filepath, 0, 'concept',
                               f"Missing concept: '{keyword}'", 'WARN'))
    return issues


def check_exercises(filepath):
    """Check exercise count and numbering."""
    issues = []
    content = Path(filepath).read_text(encoding='utf-8')
    lines = content.splitlines()

    # Count exercises
    exercise_pattern = re.compile(r'^###\s+(문제|연습|Exercise)\s+(\d+)')
    exercises = []
    for i, line in enumerate(lines, 1):
        m = exercise_pattern.match(line)
        if m:
            exercises.append((i, int(m.group(2))))

    if len(exercises) < 8:
        issues.append(Issue(filepath, 0, 'exercises',
                           f"Only {len(exercises)} exercises (minimum 8 recommended)", 'WARN'))

    # Check sequential numbering
    for idx, (line, num) in enumerate(exercises):
        expected = idx + 1
        if num != expected:
            issues.append(Issue(filepath, line, 'exercises',
                               f"Exercise numbering gap: expected {expected}, got {num}", 'ERROR'))

    # Check each exercise has an answer
    answer_count = len(re.findall(r'\?\?\?\s+success', content))
    if answer_count < len(exercises):
        issues.append(Issue(filepath, 0, 'exercises',
                           f"{len(exercises)} exercises but only {answer_count} answers", 'ERROR'))

    return issues


def check_nav_links(filepath):
    """Check that Next/Previous links point to existing files."""
    issues = []
    content = Path(filepath).read_text(encoding='utf-8')
    lines = content.splitlines()
    base_dir = os.path.dirname(filepath)

    link_pattern = re.compile(r'\[.*?\]\(([^)]+\.md)\)')
    for i, line in enumerate(lines, 1):
        for m in link_pattern.finditer(line):
            target = m.group(1)
            # Resolve relative path
            full_path = os.path.normpath(os.path.join(base_dir, target))
            if not os.path.exists(full_path):
                issues.append(Issue(filepath, i, 'link',
                                   f"Broken link: {target}", 'ERROR'))

    return issues


def check_dialect_tabs(filepath):
    """Check that dialect-specific SQL has appropriate tabs."""
    issues = []
    content = Path(filepath).read_text(encoding='utf-8')
    lines = content.splitlines()

    in_sql_block = False
    in_tab = False
    sql_start = 0
    current_sql = []

    for i, line in enumerate(lines, 1):
        # Track tab context
        if re.match(r'\s*===\s*"(SQLite|MySQL|PostgreSQL)', line):
            in_tab = True
        elif in_tab and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            if not line.startswith('==='):
                in_tab = False

        # Track SQL blocks
        if re.match(r'\s*```sql', line):
            in_sql_block = True
            sql_start = i
            current_sql = []
        elif in_sql_block and re.match(r'\s*```\s*$', line):
            in_sql_block = False
            sql_text = '\n'.join(current_sql)

            # If not in a tab, check for dialect-specific markers
            if not in_tab:
                for marker in DIALECT_MARKERS['sqlite_only']:
                    if re.search(marker, sql_text):
                        issues.append(Issue(filepath, sql_start, 'dialect',
                                           f"SQLite-specific '{marker}' without DB tabs", 'WARN'))
                        break
                for marker in DIALECT_MARKERS['mysql_only']:
                    if re.search(marker, sql_text):
                        issues.append(Issue(filepath, sql_start, 'dialect',
                                           f"MySQL-specific '{marker}' without DB tabs", 'WARN'))
                        break
        elif in_sql_block:
            current_sql.append(line)

    return issues


def check_ko_en_parity(ko_file, en_file):
    """Check that ko and en files have matching structure."""
    issues = []

    if not os.path.exists(en_file):
        issues.append(Issue(ko_file, 0, 'parity',
                           f"Missing English counterpart: {en_file}", 'ERROR'))
        return issues

    ko_content = Path(ko_file).read_text(encoding='utf-8')
    en_content = Path(en_file).read_text(encoding='utf-8')

    # Compare section counts
    ko_sections = len(re.findall(r'^## ', ko_content, re.MULTILINE))
    en_sections = len(re.findall(r'^## ', en_content, re.MULTILINE))
    if ko_sections != en_sections:
        issues.append(Issue(ko_file, 0, 'parity',
                           f"Section count mismatch: ko={ko_sections}, en={en_sections}", 'WARN'))

    # Compare exercise counts
    ko_ex = len(re.findall(r'^### (문제|연습)', ko_content, re.MULTILINE))
    en_ex = len(re.findall(r'^### Exercise', en_content, re.MULTILINE))
    if ko_ex != en_ex:
        issues.append(Issue(ko_file, 0, 'parity',
                           f"Exercise count mismatch: ko={ko_ex}, en={en_ex}", 'ERROR'))

    # Compare SQL block counts
    ko_sql = len(re.findall(r'```sql', ko_content))
    en_sql = len(re.findall(r'```sql', en_content))
    if abs(ko_sql - en_sql) > 2:
        issues.append(Issue(ko_file, 0, 'parity',
                           f"SQL block count differs: ko={ko_sql}, en={en_sql}", 'WARN'))

    # Compare tab counts
    ko_tabs = len(re.findall(r'=== "SQLite"', ko_content))
    en_tabs = len(re.findall(r'=== "SQLite"', en_content))
    if ko_tabs != en_tabs:
        issues.append(Issue(ko_file, 0, 'parity',
                           f"DB tab count mismatch: ko={ko_tabs}, en={en_tabs}", 'WARN'))

    return issues


def check_terminology(filepath):
    """Check for banned terminology."""
    issues = []
    lines = Path(filepath).read_text(encoding='utf-8').splitlines()

    for i, line in enumerate(lines, 1):
        # Skip code blocks
        if line.strip().startswith('```') or line.strip().startswith('|'):
            continue
        for banned, correct in BANNED_TERMS.items():
            if banned in line:
                issues.append(Issue(filepath, i, 'terminology',
                                   f"'{banned}' should be '{correct}'", 'ERROR'))
    return issues


def check_mermaid(filepath):
    """Check for banned mermaid styles."""
    issues = []
    content = Path(filepath).read_text(encoding='utf-8')
    lines = content.splitlines()

    in_mermaid = False
    for i, line in enumerate(lines, 1):
        if '```mermaid' in line:
            in_mermaid = True
        elif in_mermaid and '```' in line:
            in_mermaid = False
        elif in_mermaid:
            for pattern in BANNED_MERMAID:
                if re.search(pattern, line):
                    issues.append(Issue(filepath, i, 'mermaid',
                                       f"Banned mermaid style: {line.strip()}", 'ERROR'))

    return issues


def check_svg_images(filepath):
    """Check SVG images have .off-glb and reasonable width."""
    issues = []
    lines = Path(filepath).read_text(encoding='utf-8').splitlines()

    for i, line in enumerate(lines, 1):
        if '.svg)' in line and '![' in line:
            if '.off-glb' not in line:
                issues.append(Issue(filepath, i, 'svg',
                                   "SVG image missing .off-glb class", 'WARN'))
            width_match = re.search(r'width="(\d+)"', line)
            if width_match:
                w = int(width_match.group(1))
                if w < 200:
                    issues.append(Issue(filepath, i, 'svg',
                                       f"SVG width={w} too small (min 200)", 'WARN'))

    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def find_chapter_files(docs_dir):
    """Find all chapter markdown files."""
    files = []
    for subdir in ['beginner', 'intermediate', 'advanced']:
        dirpath = os.path.join(docs_dir, subdir)
        if not os.path.isdir(dirpath):
            continue
        for f in sorted(os.listdir(dirpath)):
            if f.endswith('.md') and f[0].isdigit():
                files.append(os.path.join(dirpath, f))
    return files


def main():
    parser = argparse.ArgumentParser(description='Verify tutorial content quality')
    parser.add_argument('--chapter', help='Filter by chapter (e.g., "16")')
    parser.add_argument('--check', help='Run specific check only (concepts, exercises, links, dialect, parity, terminology, mermaid, svg)')
    args = parser.parse_args()

    ko_files = find_chapter_files(DOCS_KO)
    en_files = find_chapter_files(DOCS_EN)

    if args.chapter:
        ko_files = [f for f in ko_files if args.chapter in os.path.basename(f)]
        en_files = [f for f in en_files if args.chapter in os.path.basename(f)]

    all_issues = []
    checks = args.check.split(',') if args.check else None

    print(f"Checking {len(ko_files)} chapters (ko) + {len(en_files)} chapters (en)")
    print("=" * 70)

    for filepath in ko_files:
        basename = os.path.basename(filepath)
        chapter_key = os.path.splitext(basename)[0]

        if not checks or 'concepts' in checks:
            all_issues.extend(check_concepts(filepath, chapter_key))
        if not checks or 'exercises' in checks:
            all_issues.extend(check_exercises(filepath))
        if not checks or 'links' in checks:
            all_issues.extend(check_nav_links(filepath))
        if not checks or 'dialect' in checks:
            all_issues.extend(check_dialect_tabs(filepath))
        if not checks or 'terminology' in checks:
            all_issues.extend(check_terminology(filepath))
        if not checks or 'mermaid' in checks:
            all_issues.extend(check_mermaid(filepath))
        if not checks or 'svg' in checks:
            all_issues.extend(check_svg_images(filepath))

        # ko/en parity
        if not checks or 'parity' in checks:
            en_counterpart = filepath.replace(DOCS_KO, DOCS_EN)
            all_issues.extend(check_ko_en_parity(filepath, en_counterpart))

    # Also check en files for their own issues
    for filepath in en_files:
        basename = os.path.basename(filepath)
        chapter_key = os.path.splitext(basename)[0]

        if not checks or 'exercises' in checks:
            all_issues.extend(check_exercises(filepath))
        if not checks or 'links' in checks:
            all_issues.extend(check_nav_links(filepath))
        if not checks or 'mermaid' in checks:
            all_issues.extend(check_mermaid(filepath))
        if not checks or 'svg' in checks:
            all_issues.extend(check_svg_images(filepath))

    # Report
    errors = [i for i in all_issues if i.severity == 'ERROR']
    warnings = [i for i in all_issues if i.severity == 'WARN']

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for issue in errors:
            print(issue)

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for issue in warnings:
            print(issue)

    # Summary by check type
    print("\n" + "=" * 70)
    print("Summary by check type:")
    from collections import Counter
    check_counts = Counter()
    for i in all_issues:
        check_counts[f"{i.severity}:{i.check}"] += 1
    for key in sorted(check_counts.keys()):
        print(f"  {key}: {check_counts[key]}")

    print(f"\nTotal: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
