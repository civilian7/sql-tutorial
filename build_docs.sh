#!/bin/bash
# =============================================
# SQL 튜토리얼 MkDocs 빌드 스크립트
# 사용법: ./build_docs.sh [ko|en|all]
# =============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_DIR="$SCRIPT_DIR/docs"
OUTPUT_DIR="$SCRIPT_DIR/output/docs"
DEPLOY_DIR="$SCRIPT_DIR/../bin/www/docs/tutorial"

LANG="${1:-all}"

build_lang() {
    local lang="$1"
    local config="$DOCS_DIR/mkdocs-${lang}.yml"

    if [ ! -f "$config" ]; then
        echo "[ERROR] $config not found"
        return 1
    fi

    echo "[BUILD] $lang ..."
    mkdocs build -f "$config" -q
    echo "  -> $OUTPUT_DIR/$lang/ ($(find "$OUTPUT_DIR/$lang" -name '*.html' | wc -l) pages)"
}

deploy_lang() {
    local lang="$1"
    local src="$OUTPUT_DIR/$lang"
    local dst="$DEPLOY_DIR/$lang"

    if [ ! -d "$src" ]; then
        echo "[SKIP] $src not found"
        return
    fi

    mkdir -p "$dst"
    cp -r "$src/"* "$dst/"
    echo "  -> deployed to $dst/"
}

echo "=== SQL Tutorial Build ==="
echo ""

# SQL 블록 동기화 (ko → en)
echo "[SYNC] ko/ SQL → en/ ..."
python "$SCRIPT_DIR/sync_sql.py" --apply
echo ""

case "$LANG" in
    ko)
        build_lang ko
        deploy_lang ko
        ;;
    en)
        build_lang en
        deploy_lang en
        ;;
    all)
        build_lang ko
        build_lang en
        deploy_lang ko
        deploy_lang en
        ;;
    *)
        echo "Usage: $0 [ko|en|all]"
        exit 1
        ;;
esac

echo ""
echo "Done."
