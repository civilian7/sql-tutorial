"""Comprehensive data integrity check for the generated database."""
import sqlite3
import sys

def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else "./output/ecommerce-ko.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    errors = []

    print("=" * 60)
    print("COMPREHENSIVE DATA INTEGRITY CHECK")
    print("=" * 60)

    # 1. Table inventory
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite%' ORDER BY name")
    tables = [r[0] for r in c.fetchall()]
    print(f"\n[1] Tables: {len(tables)}")
    total_rows = 0
    for t in tables:
        c.execute(f"SELECT COUNT(*) FROM [{t}]")
        cnt = c.fetchone()[0]
        total_rows += cnt
        print(f"  {t:35s} {cnt:>10,}")
    print(f"  {'TOTAL':35s} {total_rows:>10,}")

    # 2. Views, Triggers, Indexes
    c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='view'")
    print(f"\n[2] Views: {c.fetchone()[0]}")
    c.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
    triggers = [r[0] for r in c.fetchall()]
    print(f"[3] Triggers: {len(triggers)}")
    c.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite%'")
    print(f"[4] Indexes: {c.fetchone()[0]}")

    # 5. FK Integrity
    print(f"\n[5] FOREIGN KEY INTEGRITY")
    fk_checks = [
        ("orders.customer_id → customers", "SELECT COUNT(*) FROM orders WHERE customer_id NOT IN (SELECT id FROM customers)"),
        ("orders.address_id → addresses", "SELECT COUNT(*) FROM orders WHERE address_id NOT IN (SELECT id FROM customer_addresses)"),
        ("order_items.order_id → orders", "SELECT COUNT(*) FROM order_items WHERE order_id NOT IN (SELECT id FROM orders)"),
        ("order_items.product_id → products", "SELECT COUNT(*) FROM order_items WHERE product_id NOT IN (SELECT id FROM products)"),
        ("products.category_id → categories", "SELECT COUNT(*) FROM products WHERE category_id NOT IN (SELECT id FROM categories)"),
        ("products.supplier_id → suppliers", "SELECT COUNT(*) FROM products WHERE supplier_id NOT IN (SELECT id FROM suppliers)"),
        ("products.successor_id → products", "SELECT COUNT(*) FROM products WHERE successor_id IS NOT NULL AND successor_id NOT IN (SELECT id FROM products)"),
        ("staff.manager_id → staff", "SELECT COUNT(*) FROM staff WHERE manager_id IS NOT NULL AND manager_id NOT IN (SELECT id FROM staff)"),
        ("reviews.product_id → products", "SELECT COUNT(*) FROM reviews WHERE product_id NOT IN (SELECT id FROM products)"),
        ("reviews.customer_id → customers", "SELECT COUNT(*) FROM reviews WHERE customer_id NOT IN (SELECT id FROM customers)"),
        ("payments.order_id → orders", "SELECT COUNT(*) FROM payments WHERE order_id NOT IN (SELECT id FROM orders)"),
        ("shipping.order_id → orders", "SELECT COUNT(*) FROM shipping WHERE order_id NOT IN (SELECT id FROM orders)"),
        ("returns.order_id → orders", "SELECT COUNT(*) FROM returns WHERE order_id NOT IN (SELECT id FROM orders)"),
        ("complaints.customer_id → customers", "SELECT COUNT(*) FROM complaints WHERE customer_id NOT IN (SELECT id FROM customers)"),
        ("wishlists.customer_id → customers", "SELECT COUNT(*) FROM wishlists WHERE customer_id NOT IN (SELECT id FROM customers)"),
        ("wishlists.product_id → products", "SELECT COUNT(*) FROM wishlists WHERE product_id NOT IN (SELECT id FROM products)"),
        ("product_tags.tag_id → tags", "SELECT COUNT(*) FROM product_tags WHERE tag_id NOT IN (SELECT id FROM tags)"),
        ("product_views.customer_id → customers", "SELECT COUNT(*) FROM product_views WHERE customer_id NOT IN (SELECT id FROM customers)"),
        ("point_tx.customer_id → customers", "SELECT COUNT(*) FROM point_transactions WHERE customer_id NOT IN (SELECT id FROM customers)"),
        ("grade_history.customer_id → customers", "SELECT COUNT(*) FROM customer_grade_history WHERE customer_id NOT IN (SELECT id FROM customers)"),
        ("qna.product_id → products", "SELECT COUNT(*) FROM product_qna WHERE product_id NOT IN (SELECT id FROM products)"),
        ("promo_products.promotion_id → promos", "SELECT COUNT(*) FROM promotion_products WHERE promotion_id NOT IN (SELECT id FROM promotions)"),
        ("categories.parent_id → categories", "SELECT COUNT(*) FROM categories WHERE parent_id IS NOT NULL AND parent_id NOT IN (SELECT id FROM categories)"),
    ]
    fk_pass = 0
    for name, sql in fk_checks:
        c.execute(sql)
        cnt = c.fetchone()[0]
        if cnt == 0:
            fk_pass += 1
            print(f"  OK  {name}")
        else:
            errors.append(f"FK: {name} has {cnt} orphans")
            print(f"  ERR {name} — {cnt} orphans!")
    print(f"  Result: {fk_pass}/{len(fk_checks)} passed")

    # 6. Temporal integrity
    print(f"\n[6] TEMPORAL INTEGRITY")
    temporal_checks = [
        ("Order before signup", "SELECT COUNT(*) FROM orders o JOIN customers c ON o.customer_id=c.id WHERE o.ordered_at < c.created_at"),
        ("Delivery before shipment", "SELECT COUNT(*) FROM shipping WHERE delivered_at IS NOT NULL AND shipped_at IS NOT NULL AND delivered_at < shipped_at"),
        ("Completion before delivery", "SELECT COUNT(*) FROM orders o JOIN shipping s ON s.order_id=o.id WHERE o.completed_at IS NOT NULL AND s.delivered_at IS NOT NULL AND o.completed_at < s.delivered_at"),
        ("Review before order", "SELECT COUNT(*) FROM reviews r JOIN orders o ON r.order_id=o.id WHERE r.created_at < o.ordered_at"),
        ("Order for discontinued product", "SELECT COUNT(*) FROM orders o JOIN order_items oi ON o.id=oi.order_id JOIN products p ON oi.product_id=p.id WHERE p.discontinued_at IS NOT NULL AND o.ordered_at > p.discontinued_at"),
    ]
    for name, sql in temporal_checks:
        c.execute(sql)
        cnt = c.fetchone()[0]
        if cnt == 0:
            print(f"  OK  {name}")
        else:
            errors.append(f"Temporal: {name} has {cnt} violations")
            print(f"  ERR {name} — {cnt} violations!")

    # 7. Data realism metrics
    print(f"\n[7] DATA REALISM")
    c.execute("SELECT c.gender, ROUND(1.0*COUNT(o.id)/COUNT(DISTINCT c.id),1) FROM customers c LEFT JOIN orders o ON c.id=o.customer_id AND o.status IN ('confirmed','delivered') WHERE c.gender IS NOT NULL GROUP BY c.gender")
    for r in c.fetchall():
        label = "Male" if r[0] == "M" else "Female"
        print(f"  {label} order freq: {r[1]} per customer")

    c.execute("""
        WITH ranked AS (
            SELECT customer_id, total_amount,
                   ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered_at) as rn
            FROM orders WHERE status IN ('confirmed','delivered')
        )
        SELECT CASE WHEN rn=1 THEN 'First' ELSE 'Repeat' END, ROUND(AVG(total_amount))
        FROM ranked GROUP BY 1
    """)
    for r in c.fetchall():
        print(f"  {r[0]:8s} order avg amount: {r[1]:,.0f}")

    c.execute("SELECT is_active, COUNT(*) FROM suppliers GROUP BY is_active")
    for r in c.fetchall():
        print(f"  Suppliers is_active={r[0]}: {r[1]}")

    c.execute("SELECT COUNT(*) FROM products WHERE successor_id IS NOT NULL")
    print(f"  Products with successor: {c.fetchone()[0]}")

    c.execute("SELECT COUNT(*) FROM customers WHERE point_balance < 0")
    neg = c.fetchone()[0]
    if neg > 0:
        errors.append(f"Negative point balance: {neg}")
    print(f"  Negative point balance: {neg}")

    # 8. New tables
    print(f"\n[8] NEW TABLES")
    c.execute("SELECT type, COUNT(*) FROM point_transactions GROUP BY type ORDER BY type")
    print(f"  Point tx: {dict(c.fetchall())}")
    c.execute("SELECT type, COUNT(*) FROM promotions GROUP BY type ORDER BY type")
    print(f"  Promotions: {dict(c.fetchall())}")
    c.execute("SELECT SUM(CASE WHEN parent_id IS NULL THEN 1 ELSE 0 END) as q, SUM(CASE WHEN parent_id IS NOT NULL THEN 1 ELSE 0 END) as a FROM product_qna")
    r = c.fetchone()
    print(f"  Q&A: {r[0]} questions, {r[1]} answers")
    c.execute("SELECT SUM(is_holiday), SUM(is_weekend) FROM calendar")
    r = c.fetchone()
    print(f"  Calendar: {r[0]} holidays, {r[1]} weekends")
    c.execute("SELECT COUNT(*) FROM products WHERE specs IS NOT NULL")
    print(f"  Products with specs: {c.fetchone()[0]}")

    # 9. CS enhancements
    print(f"\n[9] CS ENHANCEMENTS")
    c.execute("SELECT type, COUNT(*) FROM complaints GROUP BY type ORDER BY type")
    print(f"  Complaint types: {dict(c.fetchall())}")
    c.execute("SELECT SUM(escalated), COUNT(*) FROM complaints")
    r = c.fetchone()
    print(f"  Escalated: {r[0]}/{r[1]}")
    c.execute("SELECT COUNT(*) FROM returns WHERE claim_id IS NOT NULL")
    print(f"  Returns with claim: {c.fetchone()[0]}")
    c.execute("SELECT COUNT(*) FROM returns WHERE exchange_product_id IS NOT NULL")
    print(f"  Returns with exchange: {c.fetchone()[0]}")

    # 10. Output files
    print(f"\n[10] OUTPUT FILES")
    import os
    for path in ["output/ecommerce-ko.db", "output/mysql/schema.sql", "output/mysql/data.sql",
                  "output/mysql/procedures.sql", "output/postgresql/schema.sql",
                  "output/postgresql/data.sql", "output/postgresql/procedures.sql"]:
        if os.path.exists(path):
            size = os.path.getsize(path)
            if size > 1024*1024:
                print(f"  OK  {path} ({size/1024/1024:.1f} MB)")
            else:
                print(f"  OK  {path} ({size/1024:.1f} KB)")
        else:
            errors.append(f"Missing: {path}")
            print(f"  ERR Missing: {path}")

    # Summary
    print(f"\n{'='*60}")
    if errors:
        print(f"ERRORS FOUND: {len(errors)}")
        for e in errors:
            print(f"  ! {e}")
    else:
        print("ALL CHECKS PASSED")
    print("=" * 60)

    conn.close()
    return len(errors)

if __name__ == "__main__":
    sys.exit(main())
