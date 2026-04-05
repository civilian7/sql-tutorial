#!/usr/bin/env python3
"""
sync_sql.py — ko/ SQL 블록을 en/으로 동기화

ko/ 마크다운 파일의 SQL 코드 블록을 추출하여 en/ 대응 파일에 패치한다.
영문 텍스트(설명, 힌트, 인사이트)는 건드리지 않고 SQL만 교체한다.

사용법:
    python sync_sql.py              # 전체 동기화 (dry-run)
    python sync_sql.py --apply      # 실제 적용
    python sync_sql.py --file exercises/sales-analysis.md  # 특정 파일만
"""

import argparse
import re
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "docs"
KO_DIR = DOCS_DIR / "ko"
EN_DIR = DOCS_DIR / "en"

# 구조가 다른 파일은 동기화 대상에서 제외
EXCLUDE = {"schema.md", "index.md", "dialect-comparison.md"}

# ```sql ... ``` 블록 매칭 (들여쓰기 포함)
SQL_BLOCK_RE = re.compile(
    r"^(?P<indent>[ \t]*)```sql\s*\n"
    r"(?P<body>.*?)"
    r"^(?P=indent)```",
    re.MULTILINE | re.DOTALL,
)


def extract_sql_blocks(content: str) -> list[dict]:
    """마크다운에서 모든 SQL 코드 블록을 추출한다."""
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
    """SQL 블록을 주어진 들여쓰기로 재구성한다."""
    # body의 들여쓰기를 대상 indent에 맞춘다
    lines = body.splitlines(keepends=True)
    return f"{indent}```sql\n{''.join(lines)}{indent}```"


def strip_strings(sql: str) -> str:
    """SQL 문자열 리터럴('...')을 빈 문자열로 치환하여 비교에서 제외한다."""
    return re.sub(r"'[^']*'", "''", sql)


def strip_inline_comments(sql: str) -> str:
    """인라인 SQL 주석(-- ...)을 제거한다. 문자열 내부의 --는 보존."""
    # 문자열 리터럴 밖의 -- 주석만 제거
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
            break  # 이후는 주석
        else:
            result.append(sql[i])
        i += 1
    return "".join(result).rstrip()


def normalize_body(body: str) -> str:
    """비교용: 주석, 빈 줄, 문자열 리터럴을 제거하고 SQL 구조만 비교한다."""
    lines = body.strip().splitlines()
    stripped = []
    for line in lines:
        s = line.lstrip()
        if s.startswith("--") or not s:
            continue
        s = strip_inline_comments(s)
        if not s:
            continue
        # 연속 공백을 하나로 축소
        s = re.sub(r"\s+", " ", strip_strings(s))
        stripped.append(s)
    return "\n".join(stripped)


def sync_file(rel_path: str, apply: bool) -> dict:
    """단일 파일의 SQL 블록을 동기화한다."""
    ko_path = KO_DIR / rel_path
    en_path = EN_DIR / rel_path

    if not ko_path.exists():
        return {"status": "skip", "reason": f"ko 파일 없음: {rel_path}"}
    if not en_path.exists():
        return {"status": "skip", "reason": f"en 파일 없음: {rel_path}"}

    ko_content = ko_path.read_text(encoding="utf-8")
    en_content = en_path.read_text(encoding="utf-8")

    ko_blocks = extract_sql_blocks(ko_content)
    en_blocks = extract_sql_blocks(en_content)

    if len(ko_blocks) != len(en_blocks):
        return {
            "status": "error",
            "reason": f"블록 수 불일치: ko={len(ko_blocks)}, en={len(en_blocks)}",
        }

    if not ko_blocks:
        return {"status": "skip", "reason": "SQL 블록 없음"}

    changes = []
    new_content = en_content

    # 뒤에서부터 교체하여 오프셋 유지
    for i in range(len(ko_blocks) - 1, -1, -1):
        ko_body = normalize_body(ko_blocks[i]["body"])
        en_body = normalize_body(en_blocks[i]["body"])

        if ko_body != en_body:
            # en의 들여쓰기를 유지하면서 ko의 SQL 본문을 적용
            en_indent = en_blocks[i]["indent"]

            # ko body의 줄들을 en indent에 맞게 재조정
            ko_lines = ko_blocks[i]["body"].rstrip("\n").splitlines()
            # ko의 기본 들여쓰기 감지
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
        return {"status": "ok", "reason": "이미 동기화됨"}

    if apply:
        en_path.write_text(new_content, encoding="utf-8")

    return {
        "status": "updated" if apply else "diff",
        "reason": f"블록 {len(changes)}개 {'적용' if apply else '변경 예정'}: #{', #'.join(str(c) for c in sorted(changes))}",
    }


def find_all_files() -> list[str]:
    """ko/ 디렉토리에서 모든 .md 파일의 상대 경로를 반환한다."""
    files = []
    for p in sorted(KO_DIR.rglob("*.md")):
        rel = p.relative_to(KO_DIR).as_posix()
        en_path = EN_DIR / rel
        if en_path.exists() and rel not in EXCLUDE:
            files.append(rel)
    return files


def main():
    parser = argparse.ArgumentParser(
        description="ko/ SQL 블록을 en/으로 동기화"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="실제 파일에 적용 (기본: dry-run)"
    )
    parser.add_argument(
        "--file", type=str, default=None,
        help="특정 파일만 동기화 (예: exercises/sales-analysis.md)"
    )
    args = parser.parse_args()

    if args.file:
        files = [args.file]
    else:
        files = find_all_files()

    if not args.apply:
        print("=== DRY RUN (--apply 로 실제 적용) ===\n")

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

    print(f"\n총 {len(files)}개 파일 검사, {updated}개 변경, {errors}개 오류")

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
