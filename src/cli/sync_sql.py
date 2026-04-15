#!/usr/bin/env python3
"""
sync_sql.py -- Sync SQL blocks from ko/ to en/

Extracts SQL code blocks from ko/ markdown files and patches them into
the corresponding en/ files. English text (descriptions, hints, insights)
is left untouched; only SQL is replaced.

Usage:
    python sync_sql.py              # Full sync (dry-run)
    python sync_sql.py --apply      # Apply changes
    python sync_sql.py --file exercises/sales-analysis.md  # Single file
"""

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
KO_DIR = DOCS_DIR / "ko"
EN_DIR = DOCS_DIR / "en"

# Files with different structure are excluded from sync
EXCLUDE = {"schema.md", "index.md", "dialect-comparison.md"}

# Match ```sql ... ``` blocks (including indentation)
SQL_BLOCK_RE = re.compile(
    r"^(?P<indent>[ \t]*)```sql\s*\n"
    r"(?P<body>.*?)"
    r"^(?P=indent)```",
    re.MULTILINE | re.DOTALL,
)


def extract_sql_blocks(content: str) -> list[dict]:
    """Extract all SQL code blocks from markdown."""
    blocks = []
    for m in SQL_BLOCK_RE.finditer(content):
        blocks.append({
            "start": m.start(),
            "end": m.end(),
            "indent": m.group("indent"),
            "body": m.group("body"),
            "full": m.group(0),
        })
    return blocks


def rebuild_block(indent: str, body: str) -> str:
    """Rebuild SQL block with given indentation."""
    # Adjust body indentation to target indent
    lines = body.splitlines(keepends=True)
    return f"{indent}```sql\n{''.join(lines)}{indent}```"


def strip_strings(sql: str) -> str:
    """Replace SQL string literals ('...') with empty strings for comparison."""
    return re.sub(r"'[^']*'", "''", sql)


def strip_inline_comments(sql: str) -> str:
    """Remove inline SQL comments (-- ...). Preserves -- inside string literals."""
    # Only remove -- comments outside string literals
    result = []
    in_string = False
    i = 0
    while i < len(sql):
        if sql[i] == "'" and not in_string:
            in_string = True
            result.append(sql[i])
        elif sql[i] == "'" and in_string:
            in_string = False
            result.append(sql[i])
        elif not in_string and sql[i:i+2] == "--":
            break  # rest is comment
        else:
            result.append(sql[i])
        i += 1
    return "".join(result).rstrip()


def normalize_body(body: str) -> str:
    """Normalize for comparison: strip comments, blank lines, and string literals."""
    lines = body.strip().splitlines()
    stripped = []
    for line in lines:
        s = line.lstrip()
        if s.startswith("--") or not s:
            continue
        s = strip_inline_comments(s)
        if not s:
            continue
        # Collapse consecutive whitespace
        s = re.sub(r"\s+", " ", strip_strings(s))
        stripped.append(s)
    return "\n".join(stripped)


def sync_file(rel_path: str, apply: bool) -> dict:
    """Sync SQL blocks for a single file."""
    ko_path = KO_DIR / rel_path
    en_path = EN_DIR / rel_path

    if not ko_path.exists():
        return {"status": "skip", "reason": f"ko file not found: {rel_path}"}
    if not en_path.exists():
        return {"status": "skip", "reason": f"en file not found: {rel_path}"}

    ko_content = ko_path.read_text(encoding="utf-8")
    en_content = en_path.read_text(encoding="utf-8")

    ko_blocks = extract_sql_blocks(ko_content)
    en_blocks = extract_sql_blocks(en_content)

    if len(ko_blocks) != len(en_blocks):
        return {
            "status": "error",
            "reason": f"Block count mismatch: ko={len(ko_blocks)}, en={len(en_blocks)}",
        }

    if not ko_blocks:
        return {"status": "skip", "reason": "No SQL blocks"}

    changes = []
    new_content = en_content

    # Replace from end to preserve offsets
    for i in range(len(ko_blocks) - 1, -1, -1):
        ko_body = normalize_body(ko_blocks[i]["body"])
        en_body = normalize_body(en_blocks[i]["body"])

        if ko_body != en_body:
            # Apply ko SQL body while preserving en indentation
            en_indent = en_blocks[i]["indent"]

            # Re-indent ko body lines to match en indent
            ko_lines = ko_blocks[i]["body"].rstrip("\n").splitlines()
            # Detect ko base indentation
            ko_indent = ko_blocks[i]["indent"]

            adjusted_lines = []
            for line in ko_lines:
                if not line.strip():
                    adjusted_lines.append("")
                elif line.startswith(ko_indent):
                    adjusted_lines.append(en_indent + line[len(ko_indent):])
                else:
                    adjusted_lines.append(en_indent + line.lstrip())
            adjusted_body = "\n".join(adjusted_lines) + "\n"

            new_block = f"{en_indent}```sql\n{adjusted_body}{en_indent}```"
            new_content = (
                new_content[: en_blocks[i]["start"]]
                + new_block
                + new_content[en_blocks[i]["end"]:]
            )
            changes.append(i + 1)

    if not changes:
        return {"status": "ok", "reason": "Already in sync"}

    if apply:
        en_path.write_text(new_content, encoding="utf-8")

    return {
        "status": "updated" if apply else "diff",
        "reason": f"{len(changes)} block(s) {'applied' if apply else 'to update'}: #{', #'.join(str(c) for c in sorted(changes))}",
    }


def find_all_files() -> list[str]:
    """Return relative paths of all .md files in ko/ directory."""
    files = []
    for p in sorted(KO_DIR.rglob("*.md")):
        rel = p.relative_to(KO_DIR).as_posix()
        en_path = EN_DIR / rel
        if en_path.exists() and rel not in EXCLUDE:
            files.append(rel)
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Sync SQL blocks from ko/ to en/"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Apply to files (default: dry-run)"
    )
    parser.add_argument(
        "--file", type=str, default=None,
        help="Sync a specific file only (e.g. exercises/sales-analysis.md)"
    )
    args = parser.parse_args()

    if args.file:
        files = [args.file]
    else:
        files = find_all_files()

    if not args.apply:
        print("=== DRY RUN (use --apply to write changes) ===\n")

    updated = 0
    errors = 0

    for rel in files:
        result = sync_file(rel, args.apply)
        status = result["status"]
        icon = {
            "ok": "  ",
            "skip": "  ",
            "diff": ">>",
            "updated": "OK",
            "error": "!!",
        }.get(status, "??")

        if status in ("diff", "updated", "error"):
            print(f"[{icon}] {rel}: {result['reason']}")

        if status in ("diff", "updated"):
            updated += 1
        elif status == "error":
            errors += 1

    print(f"\n{len(files)} files scanned, {updated} changed, {errors} errors")

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
