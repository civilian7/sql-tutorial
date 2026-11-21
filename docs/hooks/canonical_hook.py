"""MkDocs hook (한국어판 전용): 각 문서의 원본(canonical) 주소를 풀빛컴퓨팅 블로그 강좌로 알린다.

같은 강좌가 https://fullbit.co.kr/blog/<주소> 에도 실려 있으므로, 검색엔진이 블로그 쪽을 원본으로
보게 한다. 블로그로 가져오지 않는 쪽(첫 화면, 플레이그라운드, 검토용 카탈로그)은 그대로 둔다.

주소 규칙은 fullbit.co.kr 저장소의 site/scripts/import-sql-tutorial.mjs(slugOf)와 같아야 한다.
"""

import re

BLOG = "https://fullbit.co.kr/blog/"
SKIP = {"index.md", "playground.md", "exercises/EXERCISE-CATALOG.md"}
LESSON_DIRS = {"beginner", "intermediate", "advanced", "appendix"}


def blog_slug(src_path: str) -> str:
    parts = src_path.replace("\\", "/")[: -len(".md")].split("/")
    if parts[0] == "exercises":
        name = "exercises" if parts[1] == "index" else f"ex-{parts[1]}"
    elif parts[0] in LESSON_DIRS:
        name = parts[1]
    elif len(parts) > 1 and parts[1] == "index":
        name = parts[0]
    else:
        name = "-".join(parts)
    slug = re.sub(r"[^a-z0-9-]+", "-", f"sql-{name}".lower())
    return re.sub(r"-+", "-", slug).rstrip("-")


def on_page_context(context, page, config, nav):
    src = page.file.src_path.replace("\\", "/")
    if src.endswith(".md") and src not in SKIP:
        page.canonical_url = BLOG + blog_slug(src)
    return context
