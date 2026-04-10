#!/usr/bin/env python3
"""
Analyze exercise difficulty curve across all chapters.

Measures SQL complexity per exercise and checks that difficulty
increases monotonically within each chapter.

Usage:
    python verify_difficulty.py
    python verify_difficulty.py --chapter 07
"""

import argparse
import os
import re
import sys
from pathlib import Path


def complexity_score(sql: str) -> dict:
    """Calculate complexity metrics for a SQL statement."""
    sql_upper = sql.upper()
    sql_clean = re.sub(r'--[^\n]*', '', sql)  # remove comments
    sql_clean_upper = sql_clean.upper()

    metrics = {
        'tables': 0,
        'joins': 0,
        'subqueries': 0,
        'window_functions': 0,
        'cte': 0,
        'case': 0,
        'aggregates': 0,
        'group_by': 0,
        'having': 0,
        'union': 0,
        'exists': 0,
        'order_by': 0,
        'distinct': 0,
        'lines': len([l for l in sql.splitlines() if l.strip()]),
    }

    # Tables (FROM/JOIN references)
    metrics['tables'] = len(re.findall(r'\bFROM\b', sql_clean_upper)) + \
                        len(re.findall(r'\bJOIN\b', sql_clean_upper))

    # JOINs
    metrics['joins'] = len(re.findall(r'\b(?:INNER|LEFT|RIGHT|FULL|CROSS)\s+JOIN\b', sql_clean_upper)) + \
                       len(re.findall(r'\bJOIN\b', sql_clean_upper))

    # Subqueries (SELECT inside parentheses)
    metrics['subqueries'] = max(0, len(re.findall(r'\(\s*SELECT\b', sql_clean_upper)) )

    # Window functions
    metrics['window_functions'] = len(re.findall(r'\bOVER\s*\(', sql_clean_upper))

    # CTEs
    metrics['cte'] = len(re.findall(r'\bWITH\b', sql_clean_upper))

    # CASE expressions
    metrics['case'] = len(re.findall(r'\bCASE\b', sql_clean_upper))

    # Aggregate functions
    metrics['aggregates'] = len(re.findall(r'\b(?:COUNT|SUM|AVG|MIN|MAX)\s*\(', sql_clean_upper))

    # GROUP BY
    metrics['group_by'] = 1 if re.search(r'\bGROUP\s+BY\b', sql_clean_upper) else 0

    # HAVING
    metrics['having'] = 1 if re.search(r'\bHAVING\b', sql_clean_upper) else 0

    # UNION
    metrics['union'] = len(re.findall(r'\bUNION\b', sql_clean_upper))

    # EXISTS
    metrics['exists'] = len(re.findall(r'\bEXISTS\b', sql_clean_upper))

    # ORDER BY
    metrics['order_by'] = 1 if re.search(r'\bORDER\s+BY\b', sql_clean_upper) else 0

    # DISTINCT
    metrics['distinct'] = 1 if re.search(r'\bDISTINCT\b', sql_clean_upper) else 0

    # Weighted total score
    score = (
        metrics['lines'] * 1 +
        metrics['tables'] * 3 +
        metrics['joins'] * 5 +
        metrics['subqueries'] * 8 +
        metrics['window_functions'] * 10 +
        metrics['cte'] * 8 +
        metrics['case'] * 4 +
        metrics['aggregates'] * 3 +
        metrics['group_by'] * 3 +
        metrics['having'] * 4 +
        metrics['union'] * 5 +
        metrics['exists'] * 7 +
        metrics['distinct'] * 1
    )
    metrics['score'] = score
    return metrics


def extract_exercise_sql(filepath):
    """Extract exercise answer SQL blocks from a file."""
    content = Path(filepath).read_text(encoding='utf-8')
    lines = content.splitlines()
    exercises = []

    i = 0
    n = len(lines)
    current_ex = None

    while i < n:
        # Find exercise header
        m = re.match(r'^###\s+(?:문제|연습|Exercise)\s+(\d+)', lines[i])
        if m:
            current_ex = int(m.group(1))

        # Find answer SQL (first SQL block after ??? success)
        if current_ex and re.match(r'\?\?\?\s+success', lines[i]):
            # Find next SQL block
            j = i + 1
            while j < n:
                fence = re.match(r'(\s*)```sql', lines[j])
                if fence:
                    indent = fence.group(1)
                    sql_lines = []
                    j += 1
                    while j < n and not re.match(rf'{indent}```\s*$', lines[j]):
                        sl = lines[j]
                        if sl.startswith(indent):
                            sl = sl[len(indent):]
                        sql_lines.append(sl)
                        j += 1
                    sql = '\n'.join(sql_lines).strip()
                    if sql:
                        exercises.append({
                            'num': current_ex,
                            'sql': sql,
                            'line': j,
                        })
                    current_ex = None
                    break
                j += 1

        i += 1

    return exercises


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
    parser = argparse.ArgumentParser(description='Analyze exercise difficulty curve')
    parser.add_argument('--docs', default='docs/ko')
    parser.add_argument('--chapter', help='Filter by chapter')
    args = parser.parse_args()

    files = find_files(args.docs, args.chapter)
    total_issues = 0

    for filepath in files:
        basename = os.path.basename(filepath)
        exercises = extract_exercise_sql(filepath)

        if not exercises:
            continue

        scores = []
        for ex in exercises:
            m = complexity_score(ex['sql'])
            scores.append((ex['num'], m['score'], m))

        # Check monotonic increase (allow small dips)
        issues = []
        for i in range(1, len(scores)):
            prev_score = scores[i-1][1]
            curr_score = scores[i][1]
            # Flag if current is significantly easier than previous (>30% drop)
            if curr_score < prev_score * 0.6 and prev_score > 20:
                issues.append(
                    f"  #{scores[i][0]} (score={curr_score}) is much easier than "
                    f"#{scores[i-1][0]} (score={prev_score})"
                )

        # Print chapter summary
        min_s = min(s[1] for s in scores)
        max_s = max(s[1] for s in scores)
        avg_s = sum(s[1] for s in scores) / len(scores)

        status = 'OK' if not issues else 'WARN'
        print(f"{status:4s} {basename}: {len(scores)} exercises, "
              f"score {min_s}-{max_s} (avg {avg_s:.0f})")

        if issues:
            total_issues += len(issues)
            for issue in issues:
                print(issue)

        # Detailed view for --chapter
        if args.chapter:
            print(f"  {'#':>3} {'Score':>5}  {'Lines':>3} {'Joins':>3} {'Sub':>3} "
                  f"{'Win':>3} {'CTE':>3} {'Agg':>3} {'Case':>3}")
            print(f"  {'---':>3} {'-----':>5}  {'---':>3} {'---':>3} {'---':>3} "
                  f"{'---':>3} {'---':>3} {'---':>3} {'---':>3}")
            for num, score, m in scores:
                print(f"  {num:>3} {score:>5}  {m['lines']:>3} {m['joins']:>3} "
                      f"{m['subqueries']:>3} {m['window_functions']:>3} "
                      f"{m['cte']:>3} {m['aggregates']:>3} {m['case']:>3}")

    print(f"\nDifficulty curve issues: {total_issues}")
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == '__main__':
    main()
