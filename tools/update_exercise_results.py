"""
연습문제 파일의 정답 SQL을 실행하고 결과 테이블을 갱신하는 스크립트.

사용법: python tools/update_exercise_results.py [파일경로...]
  파일경로 생략 시 exercises/*.md 전체 처리
"""

import re
import sqlite3
import sys
import os
import io
import threading

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output', 'ecommerce-ko.db')
EXERCISES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'ko', 'exercises')

PG_MYSQL_KEYWORDS = [
    'CURDATE', 'NOW()', 'DATE_FORMAT', 'TIMESTAMPDIFF',
    'DATE_ADD', 'DATE_SUB', 'YEAR(', 'MONTH(', 'DAYOFWEEK(',
    'EXTRACT(', 'TO_CHAR(', 'AGE(', 'DATE_TRUNC',
    '::', 'INTERVAL', 'STRING_AGG', 'GENERATE_SERIES',
    'DELIMITER', 'LANGUAGE plpgsql', 'RETURNS TABLE',
    'SHOW CREATE', 'INFORMATION_SCHEMA', 'pg_',
    'HOUR(', 'WEEK(', 'QUARTER(',
]


def run_query_with_timeout(db_path, sql, limit=8, timeout=15):
    """Run query in a separate thread with its own connection."""
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
    t.join(timeout=timeout)
    if t.is_alive():
        return None  # Query took too long
    return result[0]


def format_table(cols, rows, has_ellipsis=True):
    """Format as markdown table."""
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
            cells.append('(NULL)' if val is None else str(val))
        data_lines.append('| ' + ' | '.join(cells) + ' |')

    if has_ellipsis and len(rows) >= 5:
        data_lines.append('| ' + ' | '.join(['...' for _ in cols]) + ' |')

    return '\n'.join([header, separator] + data_lines)


def is_pg_mysql(sql):
    for kw in PG_MYSQL_KEYWORDS:
        if kw in sql:
            return True
    return False


def process_exercise_file(filepath, db_path):
    """Process an exercise file, updating result tables in ??? success blocks."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    content = ''.join(lines)
    updated = 0

    # Find all ??? success blocks with their positions
    # We'll work with line indices
    i = 0
    edits = []  # (table_start_line, table_end_line, new_table_text, indent)

    while i < len(lines):
        line = lines[i]

        # Find result table markers inside success blocks
        stripped = line.strip()
        if ('**결과' in stripped or '**Result' in stripped) and '**' in stripped:
            # Determine indentation level
            indent = len(line) - len(line.lstrip())

            # Search backwards for SQL in this success block
            sql = find_sql_in_success_block(lines, i)
            if sql and not is_pg_mysql(sql):
                # Find the table after this result marker
                table_start = None
                table_end = None
                for j in range(i + 1, min(i + 25, len(lines))):
                    sl = lines[j].strip()
                    if sl.startswith('|') and '|' in sl[1:]:
                        if table_start is None:
                            table_start = j
                        table_end = j
                    elif table_start is not None and not sl.startswith('|'):
                        break

                if table_start is not None and table_end is not None:
                    # Determine LIMIT
                    limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
                    fetch_limit = int(limit_match.group(1)) if limit_match else 10
                    fetch_limit = min(fetch_limit, 8)

                    result = run_query_with_timeout(db_path, sql, limit=fetch_limit)
                    if result is not None:
                        cols, rows = result
                        has_ellipsis = len(rows) >= 5
                        new_table = format_table(cols, rows, has_ellipsis)

                        # Add indentation to match context
                        indented_lines = []
                        for tl in new_table.split('\n'):
                            indented_lines.append(' ' * indent + tl + '\n')

                        edits.append((table_start, table_end, indented_lines))
                        updated += 1
        i += 1

    # Apply edits in reverse order
    for table_start, table_end, new_lines in reversed(edits):
        lines[table_start:table_end + 1] = new_lines

    if updated > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    return updated


def find_sql_in_success_block(lines, result_line_idx):
    """Find SQLite SQL in the success block before a result table."""
    # Search backwards from result line for the FIRST ```sql...``` block
    code_end = None
    code_start = None

    for j in range(result_line_idx - 1, max(result_line_idx - 40, -1), -1):
        stripped = lines[j].strip()

        # Stop at problem heading or another success block
        if stripped.startswith('### 문제') or stripped.startswith('## '):
            break

        if stripped == '```' and code_end is None:
            code_end = j
        elif stripped.startswith('```sql') and code_end is not None:
            code_start = j
            break
        elif stripped == '```' and code_end is not None:
            # Hit another ``` before finding ```sql — this was a different block
            # Reset and use this as new code_end
            code_end = j

    if code_start is None or code_end is None:
        return None

    sql_lines = []
    for j in range(code_start + 1, code_end):
        line = lines[j].rstrip('\n').rstrip('\r')
        # Remove leading indentation (4-12 spaces)
        line = re.sub(r'^\s{4,12}', '', line)
        sql_lines.append(line)

    sql = '\n'.join(sql_lines).strip()

    # Remove comments
    clean_lines = [l for l in sql.split('\n') if not l.strip().startswith('--')]
    sql_clean = '\n'.join(clean_lines).strip()

    if not sql_clean:
        return None

    upper = sql_clean.lstrip().upper()
    if not any(upper.startswith(kw) for kw in ('SELECT', 'WITH', 'EXPLAIN', 'PRAGMA')):
        return None

    return sql_clean


def main():
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = []
        for f in sorted(os.listdir(EXERCISES_DIR)):
            if f.endswith('.md') and f != 'index.md' and f != 'EXERCISE-CATALOG.md':
                files.append(os.path.join(EXERCISES_DIR, f))

    total = 0
    for filepath in files:
        name = os.path.basename(filepath)
        count = process_exercise_file(filepath, DB_PATH)
        if count > 0:
            print(f'  {name}: {count}개 갱신')
        else:
            print(f'  {name}: 변경 없음')
        total += count

    print(f'\n총 {total}개 결과 테이블 갱신')


if __name__ == '__main__':
    main()
