#!/usr/bin/env python3
"""E-commerce test database generator"""

from __future__ import annotations

import argparse
import os
import sys
import time

import yaml

from src.generators.products import ProductGenerator
from src.generators.customers import CustomerGenerator
from src.generators.staff import StaffGenerator
from src.generators.orders import OrderGenerator
from src.generators.payments import PaymentGenerator
from src.generators.shipping import ShippingGenerator
from src.generators.reviews import ReviewGenerator
from src.generators.inventory import InventoryGenerator
from src.generators.images import ImageGenerator, download_images
from src.generators.wishlists import WishlistGenerator
from src.generators.returns import ReturnGenerator
from src.generators.complaints import ComplaintGenerator
from src.generators.carts import CartGenerator
from src.generators.coupons import CouponGenerator
from src.generators.calendar import generate_calendar
from src.generators.grade_history import GradeHistoryGenerator
from src.generators.tags import TagGenerator
from src.generators.views import ProductViewGenerator
from src.generators.points import PointTransactionGenerator
from src.generators.promotions import PromotionGenerator
from src.generators.qna import QnAGenerator
from src.exporters.sqlite_exporter import SQLiteExporter
from src.exporters.mysql_exporter import MySQLExporter
from src.exporters.postgresql_exporter import PostgreSQLExporter
from src.exporters.oracle_exporter import OracleExporter
from src.exporters.sqlserver_exporter import SQLServerExporter


def load_config(path: str = "config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # Merge detailed config if present (detailed values are lower priority)
    detailed_path = os.path.join(os.path.dirname(path), "config_detailed.yaml")
    if os.path.exists(detailed_path):
        with open(detailed_path, encoding="utf-8") as f:
            detailed = yaml.safe_load(f) or {}
        _merge_defaults(config, detailed)
    return config


def _merge_defaults(target: dict, defaults: dict):
    """Merge defaults into target (target values take priority)."""
    for key, value in defaults.items():
        if key not in target:
            target[key] = value
        elif isinstance(value, dict) and isinstance(target[key], dict):
            _merge_defaults(target[key], value)
        # else: target already has this key, keep it


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="E-commerce test DB generator")
    parser.add_argument("--size", choices=["small", "medium", "large"], help="Data scale")
    parser.add_argument("--seed", type=int, help="Random seed (default: 42)")
    parser.add_argument("--target", choices=["sqlite", "mysql", "postgresql", "sqlserver", "oracle", "all"],
                        help="Target DB")
    parser.add_argument("--all", action="store_true", help="Generate all DB formats")
    parser.add_argument("--start-date", type=str, help="Start date YYYY-MM-DD (default: from config)")
    parser.add_argument("--end-date", type=str, help="End date YYYY-MM-DD (default: from config)")
    parser.add_argument("--locale", choices=["ko", "en"], help="Data locale (ko/en, default: ko)")
    parser.add_argument("--dirty-data", action="store_true", help="Add 5-10%% noise for data cleaning exercises")
    parser.add_argument("--download-images", action="store_true", help="Download images via Pexels API")
    parser.add_argument("--pexels-key", help="Pexels API key (or PEXELS_API_KEY env var)")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    # RDBMS direct apply options
    parser.add_argument("--apply", action="store_true", help="Apply generated SQL directly to the target database")
    parser.add_argument("--host", default="localhost", help="DB host (default: localhost)")
    parser.add_argument("--port", type=int, help="DB port (default: 3306 for MySQL, 5432 for PostgreSQL)")
    parser.add_argument("--user", help="DB username (default: root for MySQL, postgres for PostgreSQL)")
    parser.add_argument("--password", help="DB password")
    parser.add_argument("--ask-password", action="store_true", help="Prompt for DB password interactively")
    parser.add_argument("--database", default="ecommerce_test", help="Database name (default: ecommerce_test)")
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)

    if args.size:
        config["size"] = args.size
    if args.seed is not None:
        config["seed"] = args.seed
    if args.locale:
        config["locale"] = f"{args.locale}_{'KR' if args.locale == 'ko' else 'US'}"
    # Resolve date range: --start-date/--end-date > --start-year/--end-year > config
    _resolve_date_range(config, args)
    _ensure_yearly_growth(config)
    if args.all:
        config["targets"] = ["sqlite", "mysql", "postgresql", "sqlserver", "oracle"]
    elif args.target:
        config["targets"] = [args.target]

    seed = config["seed"]
    size = config["size"]
    scale = config["profiles"][size]["scale"]
    output_dir = config.get("output_dir", "./output")

    print(f"=== E-commerce Test DB Generator ===")
    print(f"Scale: {size} ({scale}x)")
    print(f"Period: {config['start_date']} ~ {config['end_date']}")
    print(f"Seed: {seed}")
    print(f"Targets: {', '.join(config['targets'])}")
    print()

    t0 = time.time()

    # 1. Categories / Suppliers / Products
    print("[1/13] Generating categories, suppliers, products...")
    prod_gen = ProductGenerator(config, seed)
    categories = prod_gen.generate_categories()
    suppliers = prod_gen.generate_suppliers()
    products = prod_gen.generate_products(suppliers)
    print(f"  Categories: {len(categories)}, Suppliers: {len(suppliers)}, Products: {len(products)}")

    # 2. Price history
    print("[2/13] Generating price history...")
    product_prices = prod_gen.generate_product_prices(products)
    print(f"  Price history: {len(product_prices)} records")

    # 3. Product images
    print("[3/13] Generating product images...")
    img_gen = ImageGenerator(config, seed + 12)
    product_images = img_gen.generate_product_images(products, categories)
    print(f"  Images: {len(product_images)} records")

    # 4. Staff
    print("[4/13] Generating staff...")
    staff_gen = StaffGenerator(config, seed + 1)
    staff = staff_gen.generate_staff()
    print(f"  Staff: {len(staff)}")

    # 5. Customers / Addresses
    print("[5/13] Generating customers, addresses...")
    cust_gen = CustomerGenerator(config, seed + 2)
    customers = cust_gen.generate_customers()
    addresses = cust_gen.generate_addresses(customers)
    print(f"  Customers: {len(customers)}, Addresses: {len(addresses)}")

    # 6. Coupons
    print("[6/13] Generating coupons...")
    coupon_gen = CouponGenerator(config, seed + 3)
    coupons = coupon_gen.generate_coupons()
    print(f"  Coupons: {len(coupons)}")

    # 7. Orders / Order items
    print("[7/13] Generating orders, order items...")
    config["_categories_cache"] = categories  # shared with OrderGenerator for slug lookup
    order_gen = OrderGenerator(config, seed + 4)
    orders, order_items = order_gen.generate_orders(customers, addresses, products, staff)
    print(f"  Orders: {len(orders)}, Order items: {len(order_items)}")

    # 8. Payments
    print("[8/13] Generating payments...")
    pay_gen = PaymentGenerator(config, seed + 5)
    payments = pay_gen.generate_payments(orders)
    # Post-process depositor names (bank transfer: map to customer name)
    cust_name_map = {c["id"]: c["name"] for c in customers}
    order_cust_map = {o["id"]: o["customer_id"] for o in orders}
    for p in payments:
        if p["method"] == "bank_transfer" and p["depositor_name"] is None and p["status"] == "completed":
            cid = order_cust_map.get(p["order_id"])
            if cid:
                p["depositor_name"] = cust_name_map.get(cid)
    print(f"  Payments: {len(payments)}")

    # 9. Shipping
    print("[9/13] Generating shipping...")
    ship_gen = ShippingGenerator(config, seed + 6)
    shipping = ship_gen.generate_shipping(orders)
    print(f"  Shipping: {len(shipping)}")

    # 10. Reviews
    print("[10/13] Generating reviews...")
    review_gen = ReviewGenerator(config, seed + 7)
    reviews = review_gen.generate_reviews(orders, order_items, products)
    print(f"  Reviews: {len(reviews)}")

    # 11. Inventory / Carts / Coupon usage
    print("[11/13] Generating inventory, carts, coupon usage...")
    inv_gen = InventoryGenerator(config, seed + 8)
    inventory = inv_gen.generate_inventory(products, orders, order_items)

    cart_gen = CartGenerator(config, seed + 9)
    carts, cart_items = cart_gen.generate_carts(customers, products)

    coupon_usage = coupon_gen.generate_coupon_usage(coupons, orders)

    wish_gen = WishlistGenerator(config, seed + 13)
    wishlists = wish_gen.generate_wishlists(customers, products, orders, order_items)
    print(f"  Inventory: {len(inventory)}, Carts: {len(carts)}/{len(cart_items)} items, Coupons: {len(coupon_usage)}, Wishlists: {len(wishlists)}")

    # 12. Customer inquiries/complaints (generated before returns for claim linking)
    print("[12/13] Generating customer inquiries/complaints...")
    complaint_gen = ComplaintGenerator(config, seed + 11)
    complaints = complaint_gen.generate_complaints(orders, customers, staff)
    print(f"  Complaints: {len(complaints)}")

    # 13. Returns/Exchanges (can link to complaints)
    print("[13/13] Generating returns/exchanges...")
    return_gen = ReturnGenerator(config, seed + 10)
    returns = return_gen.generate_returns(orders, order_items, shipping, complaints, products)
    print(f"  Returns: {len(returns)}")

    # Update customer grades
    _update_customer_grades(customers, orders, order_items, config)

    # Additional tables: date dimension, grade history, tags
    print("\n[Extra] Generating date dimension, grade history, tags...")
    # Load locale for calendar holiday names
    from src.generators.base import load_locale
    _locale = load_locale(config.get("locale", "ko_KR"))
    calendar = generate_calendar(config["start_date"], config["end_date"], _locale)

    grade_gen = GradeHistoryGenerator(config, seed + 14)
    grade_history = grade_gen.generate_grade_history(customers, orders)

    tag_gen = TagGenerator(config, seed + 15)
    tags = tag_gen.generate_tags()
    product_tags = tag_gen.generate_product_tags(products, categories)

    view_gen = ProductViewGenerator(config, seed + 16)
    product_views = view_gen.generate_product_views(customers, products, orders, order_items)

    point_gen = PointTransactionGenerator(config, seed + 17)
    point_transactions = point_gen.generate_point_transactions(customers, orders, reviews)

    promo_gen = PromotionGenerator(config, seed + 18)
    promotions, promotion_products = promo_gen.generate_promotions(products, categories)

    qna_gen = QnAGenerator(config, seed + 19)
    product_qna = qna_gen.generate_qna(customers, products, staff)

    print(f"  Dates: {len(calendar)}, Grade history: {len(grade_history)}, Tags: {len(tags)}/{len(product_tags)}")
    print(f"  Views: {len(product_views)}, Points: {len(point_transactions)}, Promos: {len(promotions)}/{len(promotion_products)}, Q&A: {len(product_qna)}")

    # All data
    all_data = {
        "categories": categories,
        "suppliers": suppliers,
        "products": products,
        "product_images": product_images,
        "product_prices": product_prices,
        "customers": customers,
        "customer_addresses": addresses,
        "staff": staff,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
        "shipping": shipping,
        "reviews": reviews,
        "inventory_transactions": inventory,
        "carts": carts,
        "cart_items": cart_items,
        "coupons": coupons,
        "coupon_usage": coupon_usage,
        "wishlists": wishlists,
        "returns": returns,
        "complaints": complaints,
        "calendar": calendar,
        "customer_grade_history": grade_history,
        "tags": tags,
        "product_tags": product_tags,
        "product_views": product_views,
        "point_transactions": point_transactions,
        "promotions": promotions,
        "promotion_products": promotion_products,
        "product_qna": product_qna,
    }

    total_rows = sum(len(v) for v in all_data.values())
    gen_time = time.time() - t0
    print(f"\nData generation complete: {total_rows:,} total records ({gen_time:.1f}s)")

    # Apply dirty data noise (optional)
    if args.dirty_data:
        from src.generators.dirty import apply_dirty_data
        print("\nApplying dirty data noise (5-10%)...")
        apply_dirty_data(all_data, seed)

    # Image download (optional)
    if args.download_images:
        pexels_key = args.pexels_key or os.environ.get("PEXELS_API_KEY", "")
        if not pexels_key:
            print("\n[Warning] --pexels-key or PEXELS_API_KEY environment variable is required.")
            print("  Free API key: https://www.pexels.com/api/")
        else:
            print(f"\nDownloading images via Pexels API...")
            product_images = download_images(
                products, categories, product_images,
                output_dir, pexels_key,
            )
            all_data["product_images"] = product_images

    # Export
    t1 = time.time()
    for target in config["targets"]:
        if target == "sqlite":
            print(f"\nExporting to SQLite...")
            exporter = SQLiteExporter(output_dir, locale=config.get("locale", "ko_KR"))
            db_path = exporter.export(all_data)
            file_size = os.path.getsize(db_path) / (1024 * 1024)
            print(f"  -> {db_path} ({file_size:.1f} MB)")
        elif target == "mysql":
            print(f"\nExporting to MySQL...")
            exporter = MySQLExporter(output_dir)
            out_path = exporter.export(all_data)
            print(f"  -> {out_path}/")
            if args.apply:
                _apply_mysql(out_path, args)
        elif target == "postgresql":
            print(f"\nExporting to PostgreSQL...")
            exporter = PostgreSQLExporter(output_dir)
            out_path = exporter.export(all_data)
            print(f"  -> {out_path}/")
            if args.apply:
                _apply_postgresql(out_path, args)
        elif target == "oracle":
            print(f"\nExporting to Oracle...")
            exporter = OracleExporter(output_dir)
            out_path = exporter.export(all_data)
            print(f"  -> {out_path}/")
        elif target == "sqlserver":
            print(f"\nExporting to SQL Server...")
            exporter = SQLServerExporter(output_dir)
            out_path = exporter.export(all_data)
            print(f"  -> {out_path}/")
            if args.apply:
                _apply_sqlserver(out_path, args)
        else:
            print(f"\n{target} export is not yet implemented.")

    export_time = time.time() - t1
    total_time = time.time() - t0
    print(f"\nExport complete ({export_time:.1f}s)")
    print(f"Total elapsed time: {total_time:.1f}s")


def _get_password(args) -> str:
    """Resolve DB password from CLI args or interactive prompt."""
    if args.password:
        return args.password
    if args.ask_password:
        import getpass
        return getpass.getpass("Enter database password: ")
    return ""


def _apply_mysql(out_path: str, args):
    """Apply generated MySQL SQL files directly to a MySQL/MariaDB server."""
    try:
        import mysql.connector
    except ImportError:
        print("  [ERROR] mysql-connector-python is required for --apply.")
        print("  Install: pip install mysql-connector-python")
        return

    password = _get_password(args)
    port = args.port or 3306
    user = args.user or "root"
    db = args.database

    print(f"  Applying to MySQL {user}@{args.host}:{port}/{db}...")

    try:
        # Connect without database first to create it
        conn = mysql.connector.connect(
            host=args.host, port=port, user=user, password=password,
            charset="utf8mb4", allow_local_infile=True,
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE `{db}`")
        conn.database = db

        # Execute schema
        schema_path = os.path.join(out_path, "schema.sql")
        print(f"  Applying schema...")
        _execute_sql_file(cursor, schema_path)
        conn.commit()

        # Execute data
        data_path = os.path.join(out_path, "data.sql")
        print(f"  Inserting data (this may take a while)...")
        _execute_sql_file(cursor, data_path)
        conn.commit()

        # Execute procedures
        proc_path = os.path.join(out_path, "procedures.sql")
        if os.path.exists(proc_path):
            print(f"  Creating stored procedures...")
            _execute_sql_file(cursor, proc_path, delimiter="$$")
            conn.commit()

        cursor.close()
        conn.close()
        print(f"  Successfully applied to MySQL: {db}")

    except mysql.connector.Error as e:
        print(f"  [ERROR] MySQL: {e}")


def _apply_postgresql(out_path: str, args):
    """Apply generated PostgreSQL SQL files directly to a PostgreSQL server."""
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    except ImportError:
        print("  [ERROR] psycopg2 is required for --apply.")
        print("  Install: pip install psycopg2-binary")
        return

    password = _get_password(args)
    port = args.port or 5432
    user = args.user or "postgres"
    db = args.database

    print(f"  Applying to PostgreSQL {user}@{args.host}:{port}/{db}...")

    try:
        # Connect to default database first to create target database
        conn = psycopg2.connect(
            host=args.host, port=port, user=user, password=password,
            dbname="postgres",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Create database if not exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (db,))
        if not cursor.fetchone():
            cursor.execute(f'CREATE DATABASE "{db}" ENCODING \'UTF8\'')
        cursor.close()
        conn.close()

        # Reconnect to target database
        conn = psycopg2.connect(
            host=args.host, port=port, user=user, password=password,
            dbname=db,
        )
        cursor = conn.cursor()

        # Execute schema
        schema_path = os.path.join(out_path, "schema.sql")
        print(f"  Applying schema...")
        with open(schema_path, encoding="utf-8") as f:
            cursor.execute(f.read())
        conn.commit()

        # Execute data
        data_path = os.path.join(out_path, "data.sql")
        print(f"  Inserting data (this may take a while)...")
        with open(data_path, encoding="utf-8") as f:
            cursor.execute(f.read())
        conn.commit()

        # Execute procedures
        proc_path = os.path.join(out_path, "procedures.sql")
        if os.path.exists(proc_path):
            print(f"  Creating functions/procedures...")
            with open(proc_path, encoding="utf-8") as f:
                cursor.execute(f.read())
            conn.commit()

        cursor.close()
        conn.close()
        print(f"  Successfully applied to PostgreSQL: {db}")

    except psycopg2.Error as e:
        print(f"  [ERROR] PostgreSQL: {e}")


def _apply_sqlserver(out_path: str, args):
    """Apply generated SQL Server SQL files directly to a SQL Server instance."""
    try:
        import pyodbc
    except ImportError:
        print("  [ERROR] pyodbc is required for --apply with SQL Server.")
        print("  Install: pip install pyodbc")
        return

    password = _get_password(args)
    port = args.port or 1433
    user = args.user or "sa"
    db = args.database

    print(f"  Applying to SQL Server {user}@{args.host}:{port}/{db}...")

    try:
        # Find the best ODBC driver
        drivers = [d for d in pyodbc.drivers() if "SQL Server" in d]
        driver = next((d for d in drivers if "ODBC Driver 18" in d),
                      next((d for d in drivers if "ODBC Driver 17" in d),
                           drivers[0] if drivers else "ODBC Driver 18 for SQL Server"))

        # Connect to master first to create database
        conn_str = (f"DRIVER={{{driver}}};SERVER={args.host},{port};"
                    f"UID={user};PWD={password};TrustServerCertificate=yes;")
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()

        cursor.execute(f"""
            IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = '{db}')
            CREATE DATABASE [{db}]
        """)
        cursor.close()
        conn.close()

        # Reconnect to target database
        conn_str += f"DATABASE={db};"
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()

        # Execute schema (split by GO batch separator)
        schema_path = os.path.join(out_path, "schema.sql")
        print(f"  Applying schema...")
        _execute_sql_file_go(cursor, schema_path)

        # Execute data
        data_path = os.path.join(out_path, "data.sql")
        print(f"  Inserting data (this may take a while)...")
        _execute_sql_file_go(cursor, data_path)

        # Execute procedures
        proc_path = os.path.join(out_path, "procedures.sql")
        if os.path.exists(proc_path):
            print(f"  Creating stored procedures...")
            _execute_sql_file_go(cursor, proc_path)

        cursor.close()
        conn.close()
        print(f"  Successfully applied to SQL Server: {db}")

    except pyodbc.Error as e:
        print(f"  [ERROR] SQL Server: {e}")


def _execute_sql_file_go(cursor, path: str):
    """Execute a SQL Server SQL file split by GO batch separator."""
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Split by GO on its own line
    import re
    batches = re.split(r'^\s*GO\s*$', content, flags=re.MULTILINE | re.IGNORECASE)

    for batch in batches:
        # Strip comment-only lines
        lines = [ln for ln in batch.split("\n") if ln.strip() and not ln.strip().startswith("--")]
        batch = "\n".join(lines).strip()
        if not batch:
            continue
        # Skip database selection statements
        batch_upper = batch.upper().lstrip()
        if batch_upper.startswith("USE ") or batch_upper.startswith("CREATE DATABASE"):
            continue
        try:
            cursor.execute(batch)
        except Exception:
            pass  # Skip individual batch errors


def _execute_sql_file(cursor, path: str, delimiter: str = ";"):
    """Execute a SQL file statement by statement."""
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if delimiter != ";":
        # For MySQL stored procedures with custom delimiter
        statements = content.split(delimiter)
    else:
        statements = content.split(";\n")

    for stmt in statements:
        # Strip comment-only lines, keep actual SQL
        lines = [ln for ln in stmt.split("\n") if ln.strip() and not ln.strip().startswith("--")]
        stmt = "\n".join(lines).strip()
        if not stmt:
            continue
        # Skip database selection statements (handled by --database option)
        stmt_upper = stmt.upper().lstrip()
        if stmt_upper.startswith("USE ") or stmt_upper.startswith("CREATE DATABASE") or stmt_upper.startswith("\\C "):
            continue
        try:
            cursor.execute(stmt)
        except Exception:
            pass  # Skip individual statement errors (e.g., DROP IF EXISTS)


def _resolve_date_range(config: dict, args):
    """Resolve start/end dates from CLI args and config."""
    from datetime import datetime

    if getattr(args, 'start_date', None):
        config["start_date"] = args.start_date
    if getattr(args, 'end_date', None):
        config["end_date"] = args.end_date

    # Parse to datetime
    config["_start_dt"] = datetime.strptime(config["start_date"], "%Y-%m-%d")
    config["_end_dt"] = datetime.strptime(config["end_date"], "%Y-%m-%d")

    # Derive year integers (used by generators for yearly loops)
    config["start_year"] = config["_start_dt"].year
    config["end_year"] = config["_end_dt"].year


def _ensure_yearly_growth(config: dict):
    """Ensure yearly_growth covers start_year..end_year.

    If the user specifies a custom year range, interpolate/extrapolate
    growth values from the nearest defined years.
    """
    growth = config.get("yearly_growth", {})
    start = config["start_year"]
    end = config["end_year"]
    defined_years = sorted(int(y) for y in growth.keys())

    if not defined_years:
        # No growth data at all — generate flat defaults
        for y in range(start, end + 1):
            growth[y] = {
                "new_customers": 5000,
                "orders_per_day": [80, 120],
                "active_products": 1500,
            }
        config["yearly_growth"] = growth
        return

    # Re-key as int (YAML may load as int or str)
    growth_int = {int(k): v for k, v in growth.items()}

    for y in range(start, end + 1):
        if y in growth_int:
            continue
        # Find nearest defined year and copy its values
        nearest = min(defined_years, key=lambda d: abs(d - y))
        base = growth_int[nearest]
        # Scale slightly by distance
        distance = y - nearest
        scale_factor = 1.0 + distance * 0.05  # 5% growth per year from nearest
        scale_factor = max(0.3, min(scale_factor, 3.0))
        growth_int[y] = {
            "new_customers": int(base["new_customers"] * scale_factor),
            "orders_per_day": [
                int(base["orders_per_day"][0] * scale_factor),
                int(base["orders_per_day"][1] * scale_factor),
            ],
            "active_products": int(base["active_products"] * scale_factor),
        }

    config["yearly_growth"] = growth_int


def _update_customer_grades(
    customers: list[dict],
    orders: list[dict],
    order_items: list[dict],
    config: dict,
):
    """Update customer grades based on purchases in the last year."""
    from datetime import datetime, timedelta

    grade_thresholds = config["customer_grades"]
    cutoff = config["_end_dt"] - timedelta(days=365)

    # Per-customer spending total for the last year
    spending: dict[int, float] = {}
    for o in orders:
        if o["status"] not in ("confirmed", "delivered"):
            continue
        ordered = datetime.strptime(o["ordered_at"], "%Y-%m-%d %H:%M:%S")
        if ordered >= cutoff:
            spending[o["customer_id"]] = spending.get(o["customer_id"], 0) + o["total_amount"]

    # Per-customer point balance: sum of point_earned - point_used for confirmed/delivered orders
    point_balance: dict[int, int] = {}
    for o in orders:
        if o["status"] not in ("confirmed", "delivered"):
            continue
        cid = o["customer_id"]
        point_balance[cid] = point_balance.get(cid, 0) + o["point_earned"] - o["point_used"]

    for c in customers:
        total = spending.get(c["id"], 0)
        if total >= grade_thresholds["VIP"]:
            c["grade"] = "VIP"
        elif total >= grade_thresholds["GOLD"]:
            c["grade"] = "GOLD"
        elif total >= grade_thresholds["SILVER"]:
            c["grade"] = "SILVER"
        else:
            c["grade"] = "BRONZE"

        c["point_balance"] = max(0, point_balance.get(c["id"], 0))


if __name__ == "__main__":
    main()
