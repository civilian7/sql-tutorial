# Lesson 17: EXISTS and Correlated Subqueries

`EXISTS` tests whether a subquery returns any rows at all. Unlike `IN`, it stops as soon as it finds one matching row — making it efficient for large datasets and safe when NULLs might be present.

## EXISTS vs. IN

| Feature | `IN` | `EXISTS` |
|---------|------|---------|
| Returns | Matching values | True/False |
| NULL safety | Unsafe — `NOT IN` fails with NULLs | Safe |
| Short-circuit | No | Yes — stops at first match |
| Self-referencing | No | Yes — correlated |

## Basic EXISTS

```sql
-- Customers who have placed at least one order
SELECT id, name, grade
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.id
)
ORDER BY name
LIMIT 8;
```

The inner query references `c.id` from the outer query — this is a **correlated subquery**. It runs once per outer row, checking whether any matching order exists.

## NOT EXISTS — Finding Gaps

`NOT EXISTS` is the safe alternative to `NOT IN` when the subquery column might contain NULLs.

```sql
-- Customers who have NEVER placed an order (safer than NOT IN)
SELECT id, name, email, created_at
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.id
)
ORDER BY created_at DESC
LIMIT 10;
```

**Result:**

| id | name | email | created_at |
|----|------|-------|------------|
| 5228 | Tyler Brooks | t.brooks@testmail.com | 2024-12-28 |
| 5221 | Grace Liu | g.liu@testmail.com | 2024-12-19 |
| ... | | | |

```sql
-- Products in someone's wishlist that have NEVER been purchased
SELECT p.id, p.name, p.price
FROM products AS p
WHERE EXISTS (
    SELECT 1 FROM wishlists AS w WHERE w.product_id = p.id
)
AND NOT EXISTS (
    SELECT 1 FROM order_items AS oi WHERE oi.product_id = p.id
)
ORDER BY p.price DESC;
```

**Result:**

| id | name | price |
|----|------|-------|
| 214 | Limited Edition Gaming Chair | 899.00 |
| 187 | 8K HDMI Cable 3m | 79.99 |
| ... | | |

## Correlated Subqueries for Conditional Logic

Correlated subqueries in `SELECT` can answer "does this row have a related record?" per row.

```sql
-- Show each customer with flags for order, review, and complaint history
SELECT
    c.id,
    c.name,
    c.grade,
    CASE WHEN EXISTS (SELECT 1 FROM orders     WHERE customer_id = c.id) THEN 'Yes' ELSE 'No' END AS has_orders,
    CASE WHEN EXISTS (SELECT 1 FROM reviews    WHERE customer_id = c.id) THEN 'Yes' ELSE 'No' END AS has_reviews,
    CASE WHEN EXISTS (SELECT 1 FROM complaints WHERE customer_id = c.id) THEN 'Yes' ELSE 'No' END AS has_complaints
FROM customers AS c
WHERE c.grade IN ('VIP', 'GOLD')
ORDER BY c.name
LIMIT 8;
```

**Result:**

| id | name | grade | has_orders | has_reviews | has_complaints |
|----|------|-------|------------|-------------|----------------|
| 41 | Aaron Cross | GOLD | Yes | Yes | No |
| 88 | Alice Morgan | VIP | Yes | Yes | Yes |
| 102 | Amanda Foster | GOLD | Yes | No | No |
| ... | | | | | |

## EXISTS with Multiple Conditions

```sql
-- Customers who have BOTH an order in 2024 AND a complaint
SELECT c.id, c.name, c.grade
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.id
      AND o.ordered_at LIKE '2024%'
)
AND EXISTS (
    SELECT 1
    FROM complaints AS comp
    WHERE comp.customer_id = c.id
)
ORDER BY c.name;
```

## Using EXISTS in HAVING (via Aggregation)

```sql
-- Categories where at least one product has been reviewed 50+ times
SELECT
    cat.name    AS category,
    COUNT(p.id) AS product_count
FROM categories AS cat
INNER JOIN products AS p ON p.category_id = cat.id
GROUP BY cat.id, cat.name
HAVING EXISTS (
    SELECT 1
    FROM products  AS p2
    INNER JOIN reviews AS r ON r.product_id = p2.id
    WHERE p2.category_id = cat.id
    GROUP BY p2.id
    HAVING COUNT(r.id) >= 50
)
ORDER BY category;
```

## Practice Exercises

### Exercise 1
Find all wishlist items where the product has **not yet been purchased** by that same customer. Return `customer_name`, `product_name`, and `added_at` (when the item was wishlisted). Use `NOT EXISTS` with a correlated subquery that checks `order_items` + `orders` for a matching `customer_id` and `product_id`.

??? success "Answer"
    ```sql
    SELECT
        c.name  AS customer_name,
        p.name  AS product_name,
        w.added_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products  AS p ON w.product_id  = p.id
    WHERE NOT EXISTS (
        SELECT 1
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.customer_id  = w.customer_id
          AND oi.product_id  = w.product_id
          AND o.status NOT IN ('cancelled', 'returned')
    )
    ORDER BY w.added_at DESC
    LIMIT 20;
    ```

### Exercise 2
Identify customers who have submitted a complaint AND have a return on record. Return `customer_id`, `name`, `grade`, `complaint_count`, and `return_count`. Use `EXISTS` for filtering, and subquery aggregation or joins for the counts.

??? success "Answer"
    ```sql
    SELECT
        c.id    AS customer_id,
        c.name,
        c.grade,
        (SELECT COUNT(*) FROM complaints WHERE customer_id = c.id) AS complaint_count,
        (SELECT COUNT(*) FROM orders AS o
                        INNER JOIN returns AS r ON r.order_id = o.id
                        WHERE o.customer_id = c.id)               AS return_count
    FROM customers AS c
    WHERE EXISTS (
        SELECT 1 FROM complaints WHERE customer_id = c.id
    )
    AND EXISTS (
        SELECT 1
        FROM orders AS o
        INNER JOIN returns AS r ON r.order_id = o.id
        WHERE o.customer_id = c.id
    )
    ORDER BY complaint_count DESC;
    ```

---
Next: [Lesson 18: Views](18-views.md)
