# Lesson 14: INSERT, UPDATE, DELETE

DML (Data Manipulation Language) statements change the data in your tables. Unlike `SELECT`, these statements are permanent — always double-check your `WHERE` clause before running `UPDATE` or `DELETE`.

> **Safety rule:** Before running any `UPDATE` or `DELETE`, first run the equivalent `SELECT` with the same `WHERE` clause to confirm exactly which rows will be affected.

## INSERT INTO

### Insert a Single Row

List the column names explicitly — this makes your query self-documenting and safe against table structure changes.

```sql
-- Add a new product
INSERT INTO products (sku, name, category_id, supplier_id, price, stock_qty, is_active, created_at, updated_at)
VALUES (
    'SKU-TEST-001',
    'Test Mechanical Keyboard',
    9,          -- category_id for Keyboards
    1,          -- supplier_id
    129.99,
    50,
    1,
    datetime('now'),
    datetime('now')
);
```

After running, verify:
```sql
SELECT * FROM products WHERE sku = 'SKU-TEST-001';
```

### Insert Multiple Rows

```sql
-- Add several coupon codes at once
INSERT INTO coupons (code, discount_type, discount_value, min_order_amount, is_active, expires_at)
VALUES
    ('SAVE10', 'percentage', 10, 50.00,  1, '2025-12-31'),
    ('FLAT20', 'fixed',      20, 100.00, 1, '2025-06-30'),
    ('VIP50',  'percentage', 50, 200.00, 1, '2025-03-31');
```

### INSERT with SELECT

Copy data from one table to another, or archive old records.

```sql
-- (Hypothetical) Insert a new product based on an existing one
INSERT INTO products (sku, name, category_id, supplier_id, price, stock_qty, is_active, created_at, updated_at)
SELECT
    'SKU-' || CAST(id + 10000 AS TEXT),
    name || ' (Refurbished)',
    category_id,
    supplier_id,
    ROUND(price * 0.7, 2),
    10,
    1,
    datetime('now'),
    datetime('now')
FROM products
WHERE sku = 'SKU-0001';
```

## UPDATE SET

### Update Specific Rows

```sql
-- Apply a 15% price increase to all items in category 3
UPDATE products
SET
    price      = ROUND(price * 1.15, 2),
    updated_at = datetime('now')
WHERE category_id = 3
  AND is_active = 1;
```

> Before running: `SELECT id, name, price FROM products WHERE category_id = 3 AND is_active = 1;`

### Update a Single Row

```sql
-- Update a customer's grade after a manual review
UPDATE customers
SET
    grade      = 'GOLD',
    updated_at = datetime('now')
WHERE id = 1042;
```

### Update with a Subquery

```sql
-- Deactivate products that have never been ordered
UPDATE products
SET
    is_active  = 0,
    updated_at = datetime('now')
WHERE id NOT IN (
    SELECT DISTINCT product_id FROM order_items
)
  AND is_active = 1;
```

## DELETE FROM

### Delete Specific Rows

```sql
-- Remove cancelled orders older than 3 years (for archival)
DELETE FROM orders
WHERE status = 'cancelled'
  AND cancelled_at < DATE('now', '-3 years');
```

> Before running: `SELECT COUNT(*) FROM orders WHERE status = 'cancelled' AND cancelled_at < DATE('now', '-3 years');`

### Delete with a Subquery

```sql
-- Remove wishlist entries for products that no longer exist
DELETE FROM wishlists
WHERE product_id NOT IN (
    SELECT id FROM products
);
```

## Transactions — All or Nothing

Wrap related DML statements in a transaction so they either all succeed or all roll back.

```sql
BEGIN TRANSACTION;

-- Step 1: deduct stock
UPDATE products
SET stock_qty = stock_qty - 2,
    updated_at = datetime('now')
WHERE id = 5;

-- Step 2: record the transaction
INSERT INTO inventory_transactions (product_id, change_qty, reason, created_at)
VALUES (5, -2, 'manual_adjustment', datetime('now'));

-- If both look good:
COMMIT;

-- If something went wrong:
-- ROLLBACK;
```

## Common Pitfalls

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| `UPDATE table SET col = val` with no `WHERE` | Updates every row | Always verify with `SELECT` first |
| `DELETE FROM table` with no `WHERE` | Deletes every row | Use transactions; check count first |
| Forgetting `updated_at` | Stale audit trail | Include `updated_at = datetime('now')` in every UPDATE |
| Inserting duplicate primary key | Constraint error | Use `INSERT OR IGNORE` or `INSERT OR REPLACE` |

## Practice Exercises

### Exercise 1
A supplier has changed the price of all products they supply. Update the `price` column for all active products from `supplier_id = 7` to increase by 8%. Also update `updated_at`. First write the `SELECT` to verify which rows will change, then write the `UPDATE`.

??? success "Answer"
    ```sql
    -- Verify first
    SELECT id, name, price, ROUND(price * 1.08, 2) AS new_price
    FROM products
    WHERE supplier_id = 7 AND is_active = 1;

    -- Then update
    UPDATE products
    SET
        price      = ROUND(price * 1.08, 2),
        updated_at = datetime('now')
    WHERE supplier_id = 7
      AND is_active = 1;
    ```

### Exercise 2
Insert a new customer record for a walk-in registration. Use: name `'Sam Rivera'`, email `'s.rivera@testmail.com'`, phone `'555-0199-7823'`, grade `'BRONZE'`, `point_balance = 0`, `is_active = 1`, and set both `created_at` and `updated_at` to the current time.

??? success "Answer"
    ```sql
    INSERT INTO customers (name, email, phone, grade, point_balance, is_active, created_at, updated_at)
    VALUES (
        'Sam Rivera',
        's.rivera@testmail.com',
        '555-0199-7823',
        'BRONZE',
        0,
        1,
        datetime('now'),
        datetime('now')
    );
    ```

---
Next: [Lesson 15: Window Functions](../advanced/15-window.md)
