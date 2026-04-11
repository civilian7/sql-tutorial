#!/usr/bin/env python3
"""
Verify DML/DDL exercise answers using a writable copy of the database.

Creates a temp copy of ecommerce-{locale}.db for each test, executes DML/DDL
statements, and checks they don't error out.

Usage:
    python verify_dml.py
    python verify_dml.py --chapter 14
"""

import argparse
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path


def extract_dml_answers(filepath):
    """Extract DML/DDL exercise answer SQL blocks."""
    content = Path(filepath).read_text(encoding='utf-8')
    lines = content.splitlines()
    answers = []

    i = 0
    n = len(lines)
    current_ex = None
    in_answer = False
    current_dialect = 'common'

    while i < n:
        line = lines[i]

        m = re.match(r'^###\s+(?:문제|연습|Exercise)\s+(\d+)', line)
        if m:
            current_ex = int(m.group(1))
            in_answer = False
            current_dialect = 'common'

        if re.match(r'\?\?\?\s+success', line):
            in_answer = True
            current_dialect = 'common'

        if in_answer and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            if re.match(r'^###\s+', line) or re.match(r'^---', line):
                in_answer = False

        tab_match = re.match(r'\s*===\s*"([^"]+)"', line)
        if tab_match and in_answer:
            name = tab_match.group(1)
            if 'SQLite' in name:
                current_dialect = 'SQLite'
            elif 'MySQL' in name:
                current_dialect = 'MySQL'
            elif 'PostgreSQL' in name:
                current_dialect = 'PostgreSQL'

        fence_match = re.match(r'(\s*)```sql', line)
        if fence_match and in_answer and current_ex:
            indent = fence_match.group(1)
            sql_lines = []
            i += 1
            while i < n and not re.match(rf'{indent}```\s*$', lines[i]):
                sl = lines[i]
                if sl.startswith(indent):
                    sl = sl[len(indent):]
                sql_lines.append(sl)
                i += 1

            sql = '\n'.join(sql_lines).strip()
            if sql and current_dialect in ('common', 'SQLite'):
                # Check if it's DML/DDL
                first_word = sql.lstrip('-').lstrip().split()[0].upper() if sql.strip() else ''
                if first_word in ('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER',
                                  'DROP', 'BEGIN', 'COMMIT', 'ROLLBACK', 'SAVEPOINT',
                                  'RELEASE', 'TRUNCATE'):
                    answers.append({
                        'exercise': current_ex,
                        'sql': sql,
                        'line': i,
                        'dialect': current_dialect,
                        'file': filepath,
                    })
                # Also handle multi-statement with DML
                elif ';' in sql:
                    stmts = [s.strip() for s in sql.split(';') if s.strip()]
                    has_dml = any(s.lstrip('-').lstrip().split()[0].upper() in
                                 ('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER',
                                  'DROP', 'BEGIN', 'COMMIT', 'ROLLBACK', 'SAVEPOINT')
                                 for s in stmts if s.strip())
                    if has_dml:
                        answers.append({
                            'exercise': current_ex,
                            'sql': sql,
                            'line': i,
                            'dialect': current_dialect,
                            'file': filepath,
                        })

        i += 1

    return answers


NON_SQLITE = re.compile(
    r'DATE_FORMAT|TO_CHAR|CURDATE|NOW\(\)|YEAR\(|EXTRACT\s*\(|TIMESTAMPDIFF|'
    r'CONCAT\(|AUTO_INCREMENT|SERIAL|GENERATED\s+ALWAYS|DELIMITER|'
    r'LANGUAGE\s+plpgsql|\$\$|::date|::int|INFORMATION_SCHEMA|pg_|'
    r'SHOW\s+CREATE|DESCRIBE\s+',
    re.IGNORECASE
)


def split_statements(sql):
    """Split SQL into statements, respecting BEGIN...END and transaction blocks."""
    statements = []
    current = []
    depth = 0  # track BEGIN...END nesting (triggers)
    in_transaction = False

    for line in sql.splitlines():
        stripped = line.strip()
        # Skip pure comment lines
        if stripped.startswith('--'):
            continue
        if not stripped:
            continue

        upper = stripped.upper()

        # Track trigger BEGIN...END depth
        # Only count BEGIN that's part of a trigger (not BEGIN TRANSACTION)
        if upper == 'BEGIN' and depth > 0:
            depth += 1
        elif 'CREATE TRIGGER' in upper:
            depth = 1  # trigger body will have BEGIN...END
        if (upper == 'END;' or upper == 'END') and depth > 0:
            depth = max(0, depth - 1)

        # Track transaction blocks: BEGIN TRANSACTION → COMMIT/ROLLBACK
        if upper.startswith('BEGIN') and ('TRANSACTION' in upper or (upper == 'BEGIN;' and depth == 0)):
            in_transaction = True

        current.append(line)

        if stripped.endswith(';') and depth == 0:
            stmt = '\n'.join(current).strip()

            # Check if this ends a transaction
            if in_transaction and (upper.startswith('COMMIT') or upper.startswith('ROLLBACK')):
                in_transaction = False
                # Keep the full transaction as one statement
                if stmt:
                    statements.append(stmt)
                current = []
                continue

            # If inside transaction, keep accumulating
            if in_transaction:
                continue

            # Normal statement boundary
            if stmt.endswith(';') and not stmt.upper().endswith('END;'):
                stmt = stmt[:-1].strip()
            if stmt:
                statements.append(stmt)
            current = []

    # Handle last statement without semicolon
    if current:
        stmt = '\n'.join(current).strip().rstrip(';').strip()
        if stmt:
            statements.append(stmt)

    return statements


def execute_dml(db_path, sql):
    """Execute DML/DDL SQL on a writable database."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    errors = []
    statements = split_statements(sql)

    for stmt in statements:
        # Skip non-SQLite syntax
        if NON_SQLITE.search(stmt):
            continue
        # Skip VACUUM (needs exclusive access)
        if stmt.upper().startswith('VACUUM'):
            continue
        try:
            # Use executescript for multi-statement blocks (transactions, triggers)
            if stmt.count(';') > 1 or 'BEGIN' in stmt.upper():
                conn.executescript(stmt)
            else:
                conn.execute(stmt)
        except Exception as e:
            errors.append((stmt[:80], str(e)))

    conn.commit()
    conn.close()
    return errors


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
    parser = argparse.ArgumentParser(description='Verify DML/DDL exercise answers')
    parser.add_argument('--db', default='output/ecommerce-ko.db')
    parser.add_argument('--docs', default='docs/ko')
    parser.add_argument('--chapter', help='Filter by chapter')
    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"ERROR: {args.db} not found")
        sys.exit(1)

    files = find_files(args.docs, args.chapter)
    total = 0
    passed = 0
    failed = 0
    skipped = 0
    failures = []

    print(f"Database: {args.db}")
    print(f"Files: {len(files)}")
    print("=" * 70)

    for filepath in files:
        answers = extract_dml_answers(filepath)
        if not answers:
            continue

        basename = os.path.basename(filepath)
        file_errors = 0

        # Use ONE temp DB per file — exercises may depend on each other
        # (e.g., Ex#2 CREATE TABLE, Ex#1 ALTER TABLE)
        # Sort by exercise number to execute in order
        answers.sort(key=lambda a: a['exercise'])

        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            tmp_path = tmp.name
        shutil.copy2(args.db, tmp_path)

        try:
            for ans in answers:
                total += 1
                errors = execute_dml(tmp_path, ans['sql'])
                if errors:
                    failed += 1
                    file_errors += 1
                    for stmt, err in errors:
                        failures.append((basename, ans['exercise'], ans['line'], stmt, err))
                        print(f"  FAIL {basename} Ex#{ans['exercise']}:{ans['line']} - {err}")
                else:
                    passed += 1
        finally:
            os.unlink(tmp_path)

        if file_errors == 0 and answers:
            print(f"  OK   {basename} ({len(answers)} DML/DDL answers)")

    print("=" * 70)
    print(f"DML/DDL answers: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    if failures:
        print(f"\nFailures:")
        for fname, ex, line, stmt, err in failures:
            print(f"  {fname} Ex#{ex}:{line}")
            print(f"    SQL: {stmt}...")
            print(f"    Error: {err}")

    sys.exit(1 if failed > 0 else 0)


if __name__ == '__main__':
    main()
