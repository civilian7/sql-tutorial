#!/usr/bin/env python3
"""
Add expected result tables (up to 5 rows) to exercise answers.

Inserts a result preview after each exercise answer SQL block that:
- Is a SELECT/WITH statement (not DML/DDL)
- Is SQLite-compatible (common or SQLite tab)
- Doesn't already have a result table

Usage:
    python add_answer_results.py                # Process all chapters (ko + en)
    python add_answer_results.py --chapter 07   # Specific chapter
    python add_answer_results.py --dry-run      # Preview without writing
"""

import argparse
import os
import re
import sqlite3
import sys
from pathlib import Path


MAX_ROWS = 5


def is_numeric(val):
    if val is None:
        return False
    if isinstance(val, (int, float)):
        return True
    try:
        float(str(val))
        return True
    except (ValueError, TypeError):
        return False


def format_val(val):
    if val is None:
        return '(NULL)'
    if isinstance(val, float):
        if val == int(val) and abs(val) > 100:
            return str(int(val))
        return f'{val:.2f}'.rstrip('0').rstrip('.')
    return str(val)


def make_table(columns, rows):
    """Generate markdown table lines."""
    if not columns:
        return []

    display = rows[:MAX_ROWS]
    has_more = len(rows) > MAX_ROWS

    # Detect numeric columns
    numeric = []
    for i in range(len(columns)):
        numeric.append(any(is_numeric(r[i]) for r in display))

    # Format values
    formatted = [[format_val(r[i]) for i in range(len(columns))] for r in display]

    # Column widths
    widths = [max(len(columns[i]), max((len(formatted[r][i]) for r in range(len(formatted))), default=0))
              for i in range(len(columns))]

    lines = []
    # Header
    lines.append('| ' + ' | '.join(columns[i].ljust(widths[i]) for i in range(len(columns))) + ' |')
    # Separator
    seps = []
    for i in range(len(columns)):
        seps.append('-' * (widths[i] - 1) + ':' if numeric[i] else '-' * widths[i])
    lines.append('| ' + ' | '.join(seps) + ' |')
    # Rows
    for row in formatted:
        cells = []
        for i, val in enumerate(row):
            cells.append(val.rjust(widths[i]) if numeric[i] else val.ljust(widths[i]))
        lines.append('| ' + ' | '.join(cells) + ' |')
    # Ellipsis
    if has_more:
        lines.append('| ' + ' | '.join('...' + ' ' * max(0, widths[i] - 3) for i in range(len(columns))) + ' |')

    return lines


# Patterns to detect dialect-specific SQL
NON_SQLITE = re.compile(
    r'DATE_FORMAT|TO_CHAR|CURDATE|NOW\(\)|YEAR\(|EXTRACT\s*\(|TIMESTAMPDIFF|'
    r'DATEDIFF\(|::date|::int|::text|::numeric|CONCAT\(|LOCATE\(|POSITION\(|'
    r'SUBSTRING\(|DAYOFWEEK\(|LPAD\(|INFORMATION_SCHEMA|pg_|SHOW\s+|DESCRIBE\s+|'
    r'AUTO_INCREMENT|SERIAL|GENERATED\s+ALWAYS|DELIMITER|LANGUAGE\s+plpgsql|'
    r'\$\$|RETURNS\s+TRIGGER|CREATE\s+PROCEDURE|TRUNCATE\s+TABLE|START\s+TRANSACTION',
    re.IGNORECASE
)

DML_DDL = re.compile(
    r'^\s*(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|BEGIN|COMMIT|ROLLBACK|'
    r'SAVEPOINT|RELEASE|GRANT|REVOKE|CALL|DELIMITER|EXPLAIN|PRAGMA)',
    re.IGNORECASE
)


def can_execute(sql, dialect):
    """Check if SQL can be executed on read-only SQLite."""
    if dialect in ('MySQL', 'PostgreSQL'):
        return False
    if DML_DDL.match(sql):
        return False
    if NON_SQLITE.search(sql):
        return False
    # Multiple statements
    stmts = [s.strip() for s in sql.split(';') if s.strip()]
    select_count = sum(1 for s in stmts if s.upper().startswith(('SELECT', 'WITH')))
    if select_count == 0:
        return False
    if len(stmts) > 1:
        return False
    return True


def execute(conn, sql):
    """Execute SQL, return (columns, rows) or None."""
    try:
        cursor = conn.execute(sql.rstrip(';'))
        if cursor.description:
            cols = [d[0] for d in cursor.description]
            rows = [list(r) for r in cursor.fetchall()]
            return cols, rows
    except Exception:
        pass
    return None, None


def process_file(filepath, conn, dry_run=False):
    """Add result tables to exercise answers in a file."""
    content = Path(filepath).read_text(encoding='utf-8')
    lines = content.splitlines()
    insertions = []  # (line_index, indent, table_lines, label)

    i = 0
    n = len(lines)
    in_answer = False
    answer_indent = ''
    current_dialect = 'common'

    while i < n:
        line = lines[i]

        # Track answer blocks
        if re.match(r'\?\?\?\s+success', line):
            in_answer = True
            answer_indent = '    '  # default indent inside ???

        # Track dialect tabs inside answers
        tab_match = re.match(r'(\s*)===\s*"([^"]+)"', line)
        if tab_match:
            tab_indent = tab_match.group(1)
            tab_name = tab_match.group(2)
            if 'SQLite' in tab_name:
                current_dialect = 'SQLite'
                answer_indent = tab_indent + '    '
            elif 'MySQL' in tab_name:
                current_dialect = 'MySQL'
            elif 'PostgreSQL' in tab_name:
                current_dialect = 'PostgreSQL'
            else:
                current_dialect = tab_name

        # Find SQL code blocks inside answers
        fence_match = re.match(r'(\s*)```sql', line)
        if fence_match and in_answer:
            indent = fence_match.group(1)
            sql_lines = []
            block_start = i
            i += 1
            while i < n and not re.match(rf'{indent}```\s*$', lines[i]):
                sql_line = lines[i]
                if sql_line.startswith(indent):
                    sql_line = sql_line[len(indent):]
                sql_lines.append(sql_line)
                i += 1
            block_end = i  # closing ```

            sql = '\n'.join(sql_lines).strip()

            # Check if there's already a result table after this block
            j = block_end + 1
            while j < n and not lines[j].strip():
                j += 1
            has_result = j < n and ('**' in lines[j] and ('결과' in lines[j] or 'Result' in lines[j] or '예시' in lines[j]))

            if not has_result and can_execute(sql, current_dialect):
                cols, rows = execute(conn, sql)
                if cols and rows:
                    table = make_table(cols, rows)
                    if table:
                        insertions.append((block_end + 1, indent, table))

            # Reset dialect after non-tabbed block
            if not any(re.match(r'\s*===', lines[j]) for j in range(max(0, block_start - 3), block_start)):
                current_dialect = 'common'

        # Exit answer block
        if in_answer and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            if re.match(r'^###\s+', line) or re.match(r'^---', line):
                in_answer = False
                current_dialect = 'common'

        i += 1

    if not insertions:
        return 0

    if dry_run:
        rel = os.path.relpath(filepath, '.')
        print(f"  {rel}: {len(insertions)} results to add")
        return len(insertions)

    # Insert in reverse order
    for line_idx, indent, table in sorted(insertions, key=lambda x: x[0], reverse=True):
        # Detect language from filepath
        norm_path = filepath.replace('\\', '/')
        is_ko = '/ko/' in norm_path
        label = f'{indent}**결과 (예시):**' if is_ko else f'{indent}**Expected result:**'
        new_lines = ['', label, '']
        for tl in table:
            new_lines.append(f'{indent}{tl}')
        new_lines.append('')
        lines[line_idx:line_idx] = new_lines

    Path(filepath).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return len(insertions)


def find_files(docs_dir, chapter=None):
    files = []
    for sub in ['beginner', 'intermediate', 'advanced']:
        d = os.path.join(docs_dir, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith('.md') and f[0].isdigit():
                if chapter and chapter not in f:
                    continue
                files.append(os.path.join(d, f))
    return files


def main():
    parser = argparse.ArgumentParser(description='Add result tables to exercise answers')
    parser.add_argument('--db', default='output/ecommerce.db')
    parser.add_argument('--chapter', help='Filter by chapter number')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"ERROR: {args.db} not found")
        sys.exit(1)

    conn = sqlite3.connect(f'file:{args.db}?mode=ro', uri=True)

    total = 0
    for docs_dir in ['docs/ko', 'docs/en']:
        files = find_files(docs_dir, args.chapter)
        for f in files:
            count = process_file(f, conn, args.dry_run)
            if count > 0:
                rel = os.path.relpath(f, '.')
                if not args.dry_run:
                    print(f"  {rel}: +{count} result tables")
                total += count

    print(f"\nTotal: {total} result tables {'would be ' if args.dry_run else ''}added")
    conn.close()


if __name__ == '__main__':
    main()
