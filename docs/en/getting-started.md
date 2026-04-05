# Getting Started

## Opening the Database

The sample database `tutorial.db` is a SQLite file. Open it in your SQL query tool.

If you need to generate the database yourself:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate (English data, small size)
python generate.py --size small --locale en
```

The database file will be created at `output/tutorial.db`.

## Exploring the Schema

Before writing queries, let's understand what's in the database.

### List All Tables

```sql
SELECT name
FROM sqlite_master
WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
ORDER BY name;
```

### See Table Structure

```sql
-- Show columns of the customers table
PRAGMA table_info(customers);
```

### Count Rows in Each Table

```sql
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'payments', COUNT(*) FROM payments
ORDER BY row_count DESC;
```

## Pre-Built Views

The database includes 18 views that demonstrate advanced SQL patterns. You can query them like regular tables:

```sql
-- Monthly sales summary
SELECT * FROM v_monthly_sales ORDER BY month DESC LIMIT 12;

-- Customer lifetime value summary
SELECT * FROM v_customer_summary WHERE total_orders > 10 ORDER BY total_spent DESC LIMIT 10;

-- Product ABC analysis (Pareto/80-20)
SELECT * FROM v_product_abc WHERE abc_class = 'A';
```

!!! info "Views as Learning Resources"
    Each view in the database demonstrates specific SQL techniques. After you learn a concept in the lessons, find the corresponding view and study how it's built:

    ```sql
    -- See how a view is defined
    SELECT sql FROM sqlite_master WHERE type = 'view' AND name = 'v_monthly_sales';
    ```

## Conventions Used in This Tutorial

- `-- This is a comment` — explanatory notes within SQL
- **Bold column names** in result tables indicate important values
- 🔑 marks primary keys, 🔗 marks foreign keys
- Each lesson ends with practice exercises
- Answers are hidden in expandable sections — try before peeking!

Ready? Start with [Lesson 1: SELECT Basics](beginner/01-select.md).
