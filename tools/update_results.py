"""
레슨 파일의 SQL 쿼리를 실행하고 결과 테이블을 갱신하는 스크립트.

사용법: python tools/update_results.py [파일경로...]
  파일경로 생략 시 전체 레슨 파일 처리
"""

import re
import sqlite3
import sys
import os
import io

# Windows 콘솔 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output', 'ecommerce-ko.db')
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'ko')

# MySQL/PG 전용 키워드 — 이런 쿼리는 SQLite로 실행 불가
PG_MYSQL_KEYWORDS = [
    'CURDATE', 'NOW()', 'DATE_FORMAT', 'TIMESTAMPDIFF',
    'DATE_ADD', 'DATE_SUB', 'YEAR(', 'MONTH(', 'DAYOFWEEK(',
    'EXTRACT(', 'TO_CHAR(', 'AGE(', 'DATE_TRUNC',
    '::', 'INTERVAL', 'STRING_AGG', 'GENERATE_SERIES',
    'DELIMITER', 'LANGUAGE plpgsql', 'RETURNS TABLE',
    'SHOW CREATE', 'INFORMATION_SCHEMA', 'pg_',
]


def run_query(db_path, sql, limit=8):
    """Run a SQL query with timeout, using a separate connection per thread."""
    import threading

    result = [None]

    def execute():
        try:
            c = sqlite3.connect(db_path)
            c.execute('PRAGMA journal_mode=WAL')
            cur = c.execute(sql)
            if cur.description is None:
                c.close()
                return
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchmany(limit)
            c.close()
            if rows:
                result[0] = (cols, rows)
        except Exception:
            pass

    t = threading.Thread(target=execute)
    t.start()
    t.join(timeout=15)
    if t.is_alive():
        return None
    return result[0]


def format_table(cols, rows, has_ellipsis=True):
    """Format as markdown table."""
    # Determine alignment
    alignments = []
    if rows:
        for val in rows[0]:
            alignments.append('right' if isinstance(val, (int, float)) else 'left')
    while len(alignments) < len(cols):
        alignments.append('left')

    header = '| ' + ' | '.join(str(c) for c in cols) + ' |'
    sep_parts = []
    for a in alignments:
        sep_parts.append(' ----------:' if a == 'right' else ' ----------')
    separator = '|' + ' |'.join(sep_parts) + ' |'

    data_lines = []
    for row in rows:
        cells = []
        for val in row:
            if val is None:
                cells.append('(NULL)')
            else:
                cells.append(str(val))
        data_lines.append('| ' + ' | '.join(cells) + ' |')

    if has_ellipsis and len(rows) >= 5:
        data_lines.append('| ' + ' | '.join(['...' for _ in cols]) + ' |')

    return '\n'.join([header, separator] + data_lines)


def is_pg_mysql(sql):
    """Check if SQL contains PostgreSQL/MySQL-only syntax."""
    for kw in PG_MYSQL_KEYWORDS:
        if kw in sql:
            return True
    return False


def find_sql_before_result(lines, result_idx):
    """Find the SQLite SQL code block preceding a result line."""
    # Search backwards for ```sql ... ``` block
    code_end = None
    code_start = None

    for j in range(result_idx - 1, max(result_idx - 40, -1), -1):
        stripped = lines[j].strip()

        if stripped == '```' and code_end is None:
            code_end = j
        elif stripped == '```sql' and code_end is not None:
            code_start = j
            break
        elif stripped.startswith('```') and stripped != '```' and code_end is not None:
            # e.g., ```sql or ``` something
            if 'sql' in stripped.lower():
                code_start = j
            break
        elif code_end is None and stripped.startswith('|'):
            # Hit another table before finding code — skip
            break
        elif code_end is None and stripped.startswith('## '):
            # Hit a section header — skip
            break

    if code_start is None or code_end is None:
        return None

    sql_lines = []
    for j in range(code_start + 1, code_end):
        sql_lines.append(lines[j])

    sql = '\n'.join(sql_lines).strip()

    # Remove comments
    clean_lines = [l for l in sql.split('\n') if not l.strip().startswith('--')]
    sql_clean = '\n'.join(clean_lines).strip()

    if not sql_clean:
        return None

    # Only SELECT/WITH queries
    upper = sql_clean.lstrip().upper()
    if not any(upper.startswith(kw) for kw in ('SELECT', 'WITH', 'EXPLAIN', 'PRAGMA')):
        return None

    # Skip PG/MySQL specific
    if is_pg_mysql(sql_clean):
        return None

    return sql_clean


def find_table_after_result(lines, result_idx):
    """Find the markdown table lines after a **결과** line."""
    table_start = None
    table_end = None

    for j in range(result_idx + 1, min(result_idx + 20, len(lines))):
        stripped = lines[j].strip()
        if stripped.startswith('|') and '|' in stripped[1:]:
            if table_start is None:
                table_start = j
            table_end = j
        elif table_start is not None and not stripped.startswith('|'):
            break

    if table_start is not None and table_end is not None:
        return table_start, table_end
    return None, None


def process_file(filepath, db_path, dry_run=False):
    """Process a single file, updating result tables."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    updates = []

    # Find all **결과** lines
    for i, line in enumerate(lines):
        if '**결과' not in line and '**Result' not in line:
            continue

        # Check if inside a tab block (=== "MySQL" or === "PostgreSQL")
        # by looking backwards for === markers
        in_non_sqlite_tab = False
        for j in range(i - 1, max(i - 15, -1), -1):
            stripped = lines[j].strip()
            if stripped.startswith('=== "MySQL"') or stripped.startswith('=== "PostgreSQL"'):
                in_non_sqlite_tab = True
                break
            elif stripped.startswith('=== "SQLite"') or stripped.startswith('=== '):
                break
            elif stripped.startswith('## ') or stripped.startswith('### '):
                break

        if in_non_sqlite_tab:
            continue

        sql = find_sql_before_result(lines, i)
        if sql is None:
            continue

        table_start, table_end = find_table_after_result(lines, i)
        if table_start is None:
            continue

        # Determine LIMIT
        limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
        fetch_limit = int(limit_match.group(1)) if limit_match else 10
        fetch_limit = min(fetch_limit, 8)

        result = run_query(db_path, sql, limit=fetch_limit)
        if result is None:
            continue

        cols, rows = result
        has_ellipsis = len(rows) >= 5
        new_table = format_table(cols, rows, has_ellipsis)

        updates.append({
            'table_start': table_start,
            'table_end': table_end,
            'new_lines': new_table.split('\n'),
        })

    if not updates:
        return 0

    # Apply updates in reverse order to maintain line indices
    for u in reversed(updates):
        lines[u['table_start']:u['table_end'] + 1] = u['new_lines']

    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    return len(updates)


def main():
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = []
        for subdir in ['beginner', 'intermediate', 'advanced']:
            dirpath = os.path.join(DOCS_DIR, subdir)
            if os.path.isdir(dirpath):
                for f in sorted(os.listdir(dirpath)):
                    if f.endswith('.md'):
                        files.append(os.path.join(dirpath, f))

    total = 0
    for filepath in files:
        count = process_file(filepath, DB_PATH)
        if count > 0:
            name = os.path.basename(filepath)
            print(f'  {name}: {count}개 갱신')
            total += count

    print(f'\n총 {total}개 결과 테이블 갱신')


if __name__ == '__main__':
    main()
