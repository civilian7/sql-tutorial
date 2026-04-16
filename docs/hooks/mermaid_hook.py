"""MkDocs hooks: mermaid.js CDN + version/date + table name linking."""

import json
import os
import re
import subprocess

MERMAID_SCRIPT = """<script src="https://unpkg.com/mermaid@10/dist/mermaid.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {
  if (typeof mermaid === "undefined") return;
  document.querySelectorAll(".mermaid").forEach(function(el) {
    el.textContent = el.textContent;
  });
  var isDark = document.body.getAttribute("data-md-color-scheme") === "slate";
  mermaid.initialize({ startOnLoad: true, theme: isDark ? "dark" : "default" });
});
</script>
"""

_version_cache = {}

# =============================================
# Table name → schema link + tooltip
# =============================================
# {table_name: (tooltip_ko, tooltip_en)}
# Anchor = table name itself (MkDocs generates #categories, #products, etc.)
_TABLE_META = {
    "categories":              ("상품 카테고리. 대/중/소 3단계 계층 구조", "Product categories. 3-level hierarchy"),
    "suppliers":               ("공급업체(입점 판매자)", "Suppliers (product vendors)"),
    "products":                ("상품 마스터. SKU, 가격, 재고, 브랜드", "Product master. SKU, price, stock, brand"),
    "product_images":          ("상품 이미지. 상품당 복수 이미지", "Product images. Multiple per product"),
    "product_prices":          ("가격 변경 이력", "Price change history"),
    "customers":               ("고객 정보. 등급(BRONZE~VIP), 적립금", "Customer info. Grade (BRONZE~VIP), points"),
    "customer_addresses":      ("고객 배송지. 복수 주소 등록 가능", "Customer addresses. Multiple per customer"),
    "staff":                   ("직원. 관리자 계층 구조", "Staff. Manager hierarchy"),
    "orders":                  ("주문. 9단계 상태 흐름", "Orders. 9-stage status flow"),
    "order_items":             ("주문 상세. 주문당 1~5개 상품", "Order items. 1-5 products per order"),
    "payments":                ("결제 정보. 카드/계좌이체/간편결제", "Payments. Card/transfer/easy pay"),
    "shipping":                ("배송 추적", "Shipping tracking"),
    "reviews":                 ("상품 리뷰. 1~5점 평점", "Product reviews. 1-5 star rating"),
    "wishlists":               ("위시리스트 (고객-상품 M:N)", "Wishlists (customer-product M:N)"),
    "complaints":              ("고객 문의/불만. 에스컬레이션, 보상", "Customer complaints. Escalation, compensation"),
    "returns":                 ("반품/교환", "Returns/exchanges"),
    "coupons":                 ("쿠폰. 정률/정액 할인", "Coupons. Percent/fixed discount"),
    "coupon_usage":            ("쿠폰 사용 내역", "Coupon usage records"),
    "inventory_transactions":  ("재고 입출고 원장", "Inventory transaction ledger"),
    "carts":                   ("장바구니", "Shopping carts"),
    "cart_items":              ("장바구니 상품", "Cart items"),
    "calendar":                ("날짜 차원 테이블 (CROSS JOIN 연습용)", "Date dimension table (for CROSS JOIN)"),
    "customer_grade_history":  ("등급 변경 이력 (SCD Type 2)", "Grade change history (SCD Type 2)"),
    "tags":                    ("상품 태그 (M:N)", "Product tags (M:N)"),
    "product_tags":            ("상품-태그 연결 (M:N)", "Product-tag mapping (M:N)"),
    "product_views":           ("상품 조회 로그", "Product view log"),
    "point_transactions":      ("포인트 적립/사용/소멸", "Point earn/use/expire"),
    "promotions":              ("프로모션/세일 이벤트", "Promotions/sale events"),
    "promotion_products":      ("프로모션 대상 상품", "Promotion target products"),
    "product_qna":             ("상품 Q&A (자기참조 스레드)", "Product Q&A (self-ref threads)"),
}

# Pages where table linking should NOT be applied (schema page itself, etc.)
_SKIP_PAGES = {"schema/tables", "schema/views", "schema/stored-procedures", "schema/index"}


def _is_lang_ko(page) -> bool:
    """Check if the page is Korean based on its path."""
    return "/ko/" in page.file.src_path or page.file.src_path.startswith("ko/")


def _link_table_names(markdown: str, page, config=None) -> str:
    """Replace `table_name` with linked version in lesson/exercise pages."""
    # Skip schema pages themselves to avoid self-links
    for skip in _SKIP_PAGES:
        if skip in page.file.src_path:
            return markdown

    # Detect language from config (docs_dir) or page path
    is_ko = True
    if config:
        docs_dir = config.get("docs_dir", "")
        if docs_dir.endswith("/en") or docs_dir.endswith("\\en") or "/en" in str(docs_dir):
            is_ko = False
    else:
        is_ko = _is_lang_ko(page)

    # Compute relative URL from this page to schema/tables/
    # page.file.url: "beginner/01-select/" -> need "../../schema/tables/"
    page_url = page.file.url  # e.g. "beginner/01-select/" or "index.html"
    page_depth = page_url.rstrip("/").count("/") + (1 if page_url.endswith("/") else 0)
    prefix = "../" * page_depth if page_depth > 0 else ""
    schema_path = f"{prefix}schema/tables/"

    def _replace_table(match):
        full = match.group(0)
        pre_char = match.group(1)   # char before backtick (or empty)
        table = match.group(2)      # table name inside backticks

        # Skip if already inside a markdown link [...] or HTML tag
        if pre_char in ("(", "[", '"', "'", "/", "#"):
            return full

        if table not in _TABLE_META:
            return full

        tip_ko, tip_en = _TABLE_META[table]
        tip = tip_ko if is_ko else tip_en

        return f'{pre_char}[`{table}`]({schema_path}#{table} "{tip}")'

    # Protect exercise header blocks (table list + concepts) — already has descriptions
    _protected = []
    def _save_block(m):
        _protected.append(m.group(0))
        return f"__PROTECTED_{len(_protected) - 1}__"
    # Match: #### :material-database: ... through next ---
    markdown = re.sub(
        r'#{4}\s+:material-database:.*?(?=\n---)',
        _save_block, markdown, flags=re.DOTALL,
    )

    # Match `table_name` — backtick-wrapped words
    result = re.sub(
        r'(.|^)`(\w+)`',
        _replace_table,
        markdown,
        flags=re.MULTILINE,
    )

    # Restore protected blocks
    for i, block in enumerate(_protected):
        result = result.replace(f"__PROTECTED_{i}__", block)

    return result


def _load_version(config):
    if _version_cache:
        return _version_cache

    hook_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.dirname(hook_dir)
    version_file = os.path.join(docs_dir, "version.json")

    version = "3.6"
    date = ""

    if os.path.exists(version_file):
        with open(version_file, encoding="utf-8") as f:
            data = json.load(f)
        version = data.get("version", version)
        date = data.get("date", "")

    _version_cache["version"] = version
    _version_cache["date"] = date
    return _version_cache


def on_page_markdown(markdown, page, config, **kwargs):
    if "{{version}}" in markdown or "{{date}}" in markdown:
        v = _load_version(config)
        markdown = markdown.replace("{{version}}", v["version"])
        markdown = markdown.replace("{{date}}", v["date"])

    # Link table names in lesson/exercise pages
    markdown = _link_table_names(markdown, page, config)

    return markdown


def on_post_page(output, page, config):
    if "mermaid" in output:
        return output.replace("</body>", MERMAID_SCRIPT + "</body>")
    return output
