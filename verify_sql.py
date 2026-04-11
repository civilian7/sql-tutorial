#!/usr/bin/env python3
"""
Verify all SQL examples and exercise answers in tutorial markdown files.

Usage:
    python verify_sql.py                    # Run all checks
    python verify_sql.py --fix-results      # Also update result tables in markdown
    python verify_sql.py --chapter 07       # Check specific chapter(s)
    python verify_sql.py --verbose          # Show all SQL, not just errors
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SQLBlock:
    """A SQL code block extracted from a markdown file."""
    file: str
    line: int
    sql: str
    dialect: str  # "common", "SQLite", "MySQL", "PostgreSQL"
    context: str  # "example", "answer"
    result_table: list = field(default_factory=list)  # expected result rows
    result_line: int = 0


@dataclass
class VerifyResult:
    block: SQLBlock
    success: bool
    error: str = ""
    actual_columns: list = field(default_factory=list)
    actual_rows: list = field(default_factory=list)
    row_count: int = 0
    result_mismatch: bool = False
    mismatch_detail: str = ""


# ---------------------------------------------------------------------------
# SQL Extraction
# ---------------------------------------------------------------------------

# Statements that can't run on a read-only SQLite DB
DML_DDL_KEYWORDS = re.compile(
    r'^\s*(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|BEGIN|COMMIT|ROLLBACK|SAVEPOINT|RELEASE|GRANT|REVOKE|CALL|DELIMITER|EXPLAIN)',
    re.IGNORECASE
)

# SQLite-incompatible hints
NON_SQLITE = re.compile(
    r'DATE_FORMAT|TO_CHAR|CURDATE|CURRENT_DATE\s*-|NOW\(\)|YEAR\(|MONTH\(|EXTRACT\s*\(|TIMESTAMPDIFF|'
    r'DATEDIFF\(|::date|::int|::text|::numeric|::char|CONCAT\(|LOCATE\(|POSITION\(|'
    r'SUBSTRING\(|DAYOFWEEK\(|LPAD\(|INFORMATION_SCHEMA|pg_|SHOW\s+|DESCRIBE\s+|'
    r'AUTO_INCREMENT|SERIAL|GENERATED\s+ALWAYS|DELIMITER|LANGUAGE\s+plpgsql|'
    r'\$\$|RETURNS\s+TRIGGER|CREATE\s+OR\s+REPLACE\s+FUNCTION|CREATE\s+PROCEDURE|'
    r'TRUNCATE\s+TABLE|START\s+TRANSACTION|JSON_EXTRACT\(|jsonb_|JSON_KEYS|'
    r'FULL\s+OUTER\s+JOIN.*UNION|RIGHT\s+JOIN',
    re.IGNORECASE
)


def extract_sql_blocks(filepath: str) -> list[SQLBlock]:
    """Extract SQL code blocks from a markdown file."""
    blocks = []
    lines = Path(filepath).read_text(encoding='utf-8').splitlines()
    i = 0
    n = len(lines)
    current_dialect = "common"
    in_answer = False

    while i < n:
        line = lines[i]

        # Track if we're inside a ??? success block
        if re.match(r'\?\?\?\s+success', line):
            in_answer = True
        elif in_answer and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            if not line.startswith('    ') and not line.startswith('\t'):
                in_answer = False

        # Track dialect tabs
        tab_match = re.match(r'\s*===\s*"([^"]+)"', line)
        if tab_match:
            tab_name = tab_match.group(1)
            if 'SQLite' in tab_name:
                current_dialect = "SQLite"
            elif 'MySQL' in tab_name:
                current_dialect = "MySQL"
            elif 'PostgreSQL' in tab_name:
                current_dialect = "PostgreSQL"
            else:
                current_dialect = tab_name

        # Find SQL code blocks
        fence_match = re.match(r'(\s*)```sql', line)
        if fence_match:
            indent = fence_match.group(1)
            sql_lines = []
            start_line = i + 1
            i += 1
            while i < n:
                if re.match(rf'{indent}```\s*$', lines[i]):
                    break
                # Remove leading indentation
                sql_line = lines[i]
                if sql_line.startswith(indent):
                    sql_line = sql_line[len(indent):]
                sql_lines.append(sql_line)
                i += 1

            sql = '\n'.join(sql_lines).strip()
            if sql:
                context = "answer" if in_answer else "example"
                block = SQLBlock(
                    file=filepath,
                    line=start_line,
                    sql=sql,
                    dialect=current_dialect,
                    context=context
                )
                # Look for result table after the code block
                result_table, result_line = find_result_table(lines, i + 1)
                if result_table:
                    block.result_table = result_table
                    block.result_line = result_line
                blocks.append(block)

            # Reset dialect after closing fence if not in a tab context
            if current_dialect != "common" and not any(
                re.match(r'\s*===', lines[j]) for j in range(max(0, start_line - 5), start_line)
            ):
                current_dialect = "common"

        i += 1

    return blocks


def find_result_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    """Find a markdown result table after a SQL block."""
    i = start
    n = len(lines)

    # Skip blank lines and look for **결과:** or **Result:**
    while i < n and not lines[i].strip():
        i += 1

    if i >= n:
        return [], 0

    # Check for result header
    if not re.match(r'\*\*(결과|Result)', lines[i]):
        return [], 0

    i += 1
    # Skip blank lines
    while i < n and not lines[i].strip():
        i += 1

    if i >= n or '|' not in lines[i]:
        return [], 0

    # Parse table header
    table_start = i
    rows = []
    header = [c.strip() for c in lines[i].split('|')[1:-1]]
    rows.append(header)
    i += 1

    # Skip separator line
    if i < n and re.match(r'\s*\|[-:\s|]+\|', lines[i]):
        i += 1

    # Parse data rows
    while i < n and '|' in lines[i] and lines[i].strip().startswith('|'):
        cells = [c.strip() for c in lines[i].split('|')[1:-1]]
        if cells and not all(c in ('', '...') for c in cells):
            rows.append(cells)
        if '...' in lines[i]:
            break
        i += 1

    return rows, table_start


# ---------------------------------------------------------------------------
# SQL Execution
# ---------------------------------------------------------------------------

def should_skip(block: SQLBlock) -> tuple[bool, str]:
    """Determine if a SQL block should be skipped."""
    sql = block.sql

    # Skip non-SQLite dialects
    if block.dialect in ("MySQL", "PostgreSQL"):
        return True, f"non-SQLite dialect ({block.dialect})"

    # Skip DML/DDL (can't run on read-only DB)
    if DML_DDL_KEYWORDS.match(sql):
        return True, "DML/DDL statement"

    # Skip if contains MySQL/PG-specific syntax
    if NON_SQLITE.search(sql):
        return True, "non-SQLite syntax detected"

    # Skip comments-only blocks
    clean = re.sub(r'--[^\n]*', '', sql).strip()
    if not clean:
        return True, "comments only"

    # Skip if it's a PRAGMA
    if re.match(r'\s*PRAGMA', sql, re.IGNORECASE):
        return True, "PRAGMA statement"

    # Skip WRONG examples (intentional errors)
    if '잘못된' in sql or 'WRONG' in sql or '-- ❌' in sql:
        return True, "intentional error example"

    return False, ""


def execute_sql(conn: sqlite3.Connection, sql: str) -> tuple[bool, str, list, list]:
    """Execute SQL and return (success, error, columns, rows)."""
    try:
        # Handle multiple statements (split by semicolons, take first SELECT)
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for stmt in statements:
            if stmt.upper().startswith('SELECT') or stmt.upper().startswith('WITH'):
                cursor = conn.execute(stmt)
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                return True, "", columns, [list(r) for r in rows]

        # If no SELECT found, try executing the whole thing
        cursor = conn.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return True, "", columns, [list(r) for r in rows]

    except Exception as e:
        return False, str(e), [], []


def compare_results(expected: list[list[str]], actual_cols: list, actual_rows: list) -> tuple[bool, str]:
    """Compare expected markdown table with actual query results."""
    if not expected or len(expected) < 2:
        return True, ""  # No expected results to compare

    exp_header = expected[0]
    exp_data = expected[1:]

    # Check column count
    if len(exp_header) != len(actual_cols):
        return False, f"Column count: expected {len(exp_header)}, got {len(actual_cols)}"

    # Check column names (case-insensitive)
    for i, (exp, act) in enumerate(zip(exp_header, actual_cols)):
        if exp.lower() != act.lower():
            return False, f"Column {i}: expected '{exp}', got '{act}'"

    # Check data rows (only first few, since markdown may be truncated)
    check_rows = min(len(exp_data), len(actual_rows))
    for r in range(check_rows):
        for c in range(len(exp_header)):
            exp_val = exp_data[r][c].strip() if c < len(exp_data[r]) else ""
            if exp_val in ('...', '', '(NULL)'):
                continue
            act_val = str(actual_rows[r][c]) if actual_rows[r][c] is not None else '(NULL)'

            # Normalize for comparison
            exp_norm = exp_val.replace(',', '').strip()
            act_norm = act_val.replace(',', '').strip()

            # Numeric comparison (handle floating point)
            try:
                if abs(float(exp_norm) - float(act_norm)) < 0.01:
                    continue
            except (ValueError, TypeError):
                pass

            if exp_norm.lower() != act_norm.lower():
                return False, f"Row {r+1}, Col '{exp_header[c]}': expected '{exp_val}', got '{act_val}'"

    return True, ""


# ---------------------------------------------------------------------------
# Result Table Generation
# ---------------------------------------------------------------------------

def format_value(val) -> str:
    """Format a value for markdown table display."""
    if val is None:
        return '(NULL)'
    if isinstance(val, float):
        # Remove trailing zeros but keep at least 1 decimal for money
        if val == int(val) and abs(val) > 100:
            return str(int(val))
        return f'{val:.2f}'.rstrip('0').rstrip('.')
    return str(val)


def is_numeric_column(rows, col_idx) -> bool:
    """Determine if a column contains numeric values."""
    for row in rows:
        val = row[col_idx]
        if val is None:
            continue
        if isinstance(val, (int, float)):
            return True
        try:
            float(str(val))
            return True
        except (ValueError, TypeError):
            return False
    return False


def generate_md_table(columns, rows, max_rows=None, has_ellipsis=False) -> list[str]:
    """Generate markdown table lines from query results."""
    if not columns:
        return []

    # Determine numeric columns for right-alignment
    numeric = [is_numeric_column(rows[:20], i) for i in range(len(columns))]

    # Format all values
    display_rows = rows[:max_rows] if max_rows else rows
    formatted = []
    for row in display_rows:
        formatted.append([format_value(row[i]) for i in range(len(columns))])

    # Calculate column widths
    widths = [len(c) for c in columns]
    for row in formatted:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(val))

    # Build table lines
    lines = []
    # Header
    header = '| ' + ' | '.join(c.ljust(widths[i]) for i, c in enumerate(columns)) + ' |'
    lines.append(header)

    # Separator with alignment
    sep_parts = []
    for i in range(len(columns)):
        if numeric[i]:
            sep_parts.append('-' * (widths[i] - 1) + ':')
        else:
            sep_parts.append('-' * widths[i])
    sep = '| ' + ' | '.join(sep_parts) + ' |'
    lines.append(sep)

    # Data rows
    for row in formatted:
        cells = []
        for i, val in enumerate(row):
            if numeric[i]:
                cells.append(val.rjust(widths[i]))
            else:
                cells.append(val.ljust(widths[i]))
        lines.append('| ' + ' | '.join(cells) + ' |')

    # Ellipsis row if truncated
    if has_ellipsis or (max_rows and len(rows) > max_rows):
        cells = ['...' + ' ' * (widths[i] - 3) if widths[i] >= 3 else '...' for i in range(len(columns))]
        lines.append('| ' + ' | '.join(cells) + ' |')

    return lines


def fix_result_tables(filepath, conn, dry_run=False):
    """Fix result tables in a markdown file with actual query results."""
    blocks = extract_sql_blocks(filepath)
    lines = Path(filepath).read_text(encoding='utf-8').splitlines()
    fixes = []

    for block in blocks:
        skip, _ = should_skip(block)
        if skip or not block.result_table or block.result_line == 0:
            continue

        success, error, cols, rows = execute_sql(conn, block.sql)
        if not success or not cols:
            continue

        # Determine how many rows the original table showed
        orig_data_rows = len(block.result_table) - 1  # minus header
        has_ellipsis = any('...' in str(cell) for row in block.result_table for cell in row)
        max_rows = orig_data_rows if orig_data_rows > 0 else min(len(rows), 5)
        if has_ellipsis and max_rows > 0:
            max_rows = max(max_rows - 1, 1)  # ellipsis took one row

        new_table = generate_md_table(cols, rows, max_rows, has_ellipsis)

        # Find the old table extent in lines
        table_start = block.result_line  # 0-indexed in result_table, 1-indexed in file
        # The result_line points to the header line (after **결과:**)
        # Find actual table start and end
        i = table_start - 1  # convert to 0-indexed
        while i < len(lines) and '|' not in lines[i]:
            i += 1
        if i >= len(lines):
            continue
        table_begin = i

        # Find table end
        j = table_begin
        while j < len(lines) and ('|' in lines[j] or lines[j].strip() == ''):
            if lines[j].strip() == '' and j > table_begin + 1:
                break
            j += 1
        table_end = j

        # Check if table actually differs
        old_table = lines[table_begin:table_end]
        if old_table == new_table:
            continue

        fixes.append({
            'start': table_begin,
            'end': table_end,
            'old': old_table,
            'new': new_table,
            'file': filepath,
            'line': table_begin + 1,
        })

    if not fixes:
        return 0

    if dry_run:
        for fix in fixes:
            rel = os.path.relpath(fix['file'], '.')
            print(f"  WOULD FIX {rel}:{fix['line']}")
        return len(fixes)

    # Apply fixes in reverse order to preserve line numbers
    for fix in sorted(fixes, key=lambda f: f['start'], reverse=True):
        lines[fix['start']:fix['end']] = fix['new']

    Path(filepath).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return len(fixes)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def find_md_files(docs_dir: str, chapter_filter: str = None) -> list[str]:
    """Find tutorial markdown files."""
    files = []
    for subdir in ['beginner', 'intermediate', 'advanced']:
        dirpath = os.path.join(docs_dir, subdir)
        if not os.path.isdir(dirpath):
            continue
        for f in sorted(os.listdir(dirpath)):
            if not f.endswith('.md') or not f[0].isdigit():
                continue
            if chapter_filter and chapter_filter not in f:
                continue
            files.append(os.path.join(dirpath, f))
    return files


def main():
    parser = argparse.ArgumentParser(description='Verify SQL in tutorial markdown')
    parser.add_argument('--db', default='output/ecommerce-ko.db', help='SQLite database path')
    parser.add_argument('--docs', default='docs/ko', help='Docs directory')
    parser.add_argument('--chapter', help='Filter by chapter number (e.g., "07")')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all results')
    parser.add_argument('--fix-results', action='store_true', help='Update result tables')
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"ERROR: Database not found: {args.db}")
        print("Run: python generate.py --size small")
        sys.exit(1)

    conn = sqlite3.connect(f'file:{args.db}?mode=ro', uri=True)
    conn.execute("PRAGMA query_only = ON")

    md_files = find_md_files(args.docs, args.chapter)
    if not md_files:
        print(f"No markdown files found in {args.docs}")
        sys.exit(1)

    total = 0
    executed = 0
    passed = 0
    failed = 0
    skipped = 0
    result_checked = 0
    result_mismatch = 0
    errors = []

    print(f"Database: {args.db}")
    print(f"Docs: {args.docs}")
    print(f"Files: {len(md_files)}")
    print("=" * 70)

    for filepath in md_files:
        blocks = extract_sql_blocks(filepath)
        file_errors = 0
        rel_path = os.path.relpath(filepath, args.docs)

        for block in blocks:
            total += 1
            skip, reason = should_skip(block)

            if skip:
                skipped += 1
                if args.verbose:
                    print(f"  SKIP {rel_path}:{block.line} ({reason})")
                continue

            executed += 1
            success, error, cols, rows = execute_sql(conn, block.sql)

            if success:
                passed += 1
                result = VerifyResult(block=block, success=True,
                                     actual_columns=cols, actual_rows=rows,
                                     row_count=len(rows))

                # Check result table if present
                if block.result_table:
                    result_checked += 1
                    match, detail = compare_results(block.result_table, cols, rows)
                    if not match:
                        result_mismatch += 1
                        result.result_mismatch = True
                        result.mismatch_detail = detail
                        print(f"  MISMATCH {rel_path}:{block.result_line} -{detail}")

                if args.verbose:
                    print(f"  OK   {rel_path}:{block.line} ({len(rows)} rows)")
            else:
                failed += 1
                file_errors += 1
                errors.append(VerifyResult(block=block, success=False, error=error))
                print(f"  FAIL {rel_path}:{block.line} -{error}")
                if args.verbose:
                    # Show first 3 lines of SQL
                    for sql_line in block.sql.split('\n')[:3]:
                        print(f"       {sql_line}")

        if file_errors == 0 and not args.verbose:
            block_count = len([b for b in blocks if not should_skip(b)[0]])
            if block_count > 0:
                print(f"  OK   {rel_path} ({block_count} queries)")

    print("=" * 70)
    print(f"Total SQL blocks: {total}")
    print(f"  Executed: {executed} (skipped {skipped} non-SQLite/DML/DDL)")
    print(f"  Passed:   {passed}")
    print(f"  Failed:   {failed}")
    print()
    print(f"Result tables checked: {result_checked}")
    print(f"  Matched:    {result_checked - result_mismatch}")
    print(f"  Mismatched: {result_mismatch}")
    print()

    if failed > 0:
        print("ERRORS:")
        for r in errors:
            print(f"  {os.path.relpath(r.block.file, args.docs)}:{r.block.line}")
            print(f"    {r.error}")
            print(f"    SQL: {r.block.sql[:100]}...")
            print()

    # Fix result tables if requested
    if args.fix_results and result_mismatch > 0:
        print("=" * 70)
        print("Fixing result tables...")
        total_fixed = 0
        for filepath in md_files:
            fixed = fix_result_tables(filepath, conn)
            if fixed > 0:
                rel = os.path.relpath(filepath, args.docs)
                print(f"  Fixed {fixed} tables in {rel}")
                total_fixed += fixed

        # Also fix English counterparts
        en_docs = args.docs.replace('/ko', '/en').replace('\\ko', '\\en')
        en_files = find_md_files(en_docs, args.chapter)
        for filepath in en_files:
            fixed = fix_result_tables(filepath, conn)
            if fixed > 0:
                rel = os.path.relpath(filepath, en_docs)
                print(f"  Fixed {fixed} tables in en/{rel}")
                total_fixed += fixed

        print(f"\nTotal tables fixed: {total_fixed}")

    conn.close()
    # Exit 1 only for result table mismatches (real data errors)
    # DML/DDL/multi-statement failures are expected and ignored
    sys.exit(1 if result_mismatch > 0 else 0)


if __name__ == '__main__':
    main()
