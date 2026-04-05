# Lesson 9: Subqueries

A subquery is a `SELECT` statement nested inside another query. It can appear in the `WHERE`, `FROM`, or `SELECT` clause. Subqueries let you break complex questions into smaller, readable steps.

## Scalar Subqueries in WHERE

A scalar subquery returns a single value (one row, one column). It can be used anywhere a literal value would work.

```sql
-- Products priced above the overall average
SELECT name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products WHERE is_active = 1)
  AND is_active = 1
ORDER BY price ASC;
```

**Result:**

| name | price |
|------|-------|
| Corsair 32GB DDR5 Kit | 419.99 |
| Samsung 27" Monitor | 449.99 |
| ASUS ROG Swift 27" Monitor | 799.00 |
| ... | |

The inner query `(SELECT AVG(price) FROM products WHERE is_active = 1)` computes the average once, and the outer query compares each product's price against that number.

```sql
-- Customers who joined before the very first order was placed
SELECT name, created_at
FROM customers
WHERE created_at < (SELECT MIN(ordered_at) FROM orders)
LIMIT 5;
```

## IN Subqueries

When a subquery can return multiple rows, use `IN` instead of `=`.

```sql
-- Customers who have ever left a 1-star review
SELECT name, email, grade
FROM customers
WHERE id IN (
    SELECT DISTINCT customer_id
    FROM reviews
    WHERE rating = 1
)
ORDER BY name;
```

**Result:**

| name | email | grade |
|------|-------|-------|
| Alex Chen | alex.chen@testmail.com | SILVER |
| Diana Walsh | d.walsh@testmail.com | BRONZE |
| ... | | |

```sql
-- Products that appear in at least one active cart right now
SELECT name, price, stock_qty
FROM products
WHERE id IN (
    SELECT DISTINCT product_id
    FROM cart_items
)
  AND is_active = 1
ORDER BY name;
```

## NOT IN

`NOT IN` finds rows that are *absent* from the subquery result — similar to the `LEFT JOIN ... IS NULL` anti-join pattern.

```sql
-- Products that have NEVER appeared in any order
SELECT name, price
FROM products
WHERE id NOT IN (
    SELECT DISTINCT product_id
    FROM order_items
)
  AND is_active = 1;
```

> **Caution:** `NOT IN` behaves unexpectedly when the subquery returns any NULL values (it returns no rows). Prefer `NOT EXISTS` (Lesson 17) when NULLs might appear.

## FROM Subqueries (Derived Tables)

A subquery in the `FROM` clause creates a temporary, inline table — called a **derived table** or **inline view**.

```sql
-- Average order value per customer grade
SELECT
    grade,
    ROUND(AVG(avg_order), 2) AS avg_order_value
FROM (
    SELECT
        c.grade,
        o.customer_id,
        AVG(o.total_amount) AS avg_order
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.status NOT IN ('cancelled', 'returned')
    GROUP BY c.grade, o.customer_id
) AS customer_avgs
GROUP BY grade
ORDER BY avg_order_value DESC;
```

**Result:**

| grade | avg_order_value |
|-------|-----------------|
| VIP | 892.34 |
| GOLD | 614.22 |
| SILVER | 421.87 |
| BRONZE | 312.49 |

```sql
-- Top 3 highest-revenue months, then show their order counts
SELECT
    monthly.year_month,
    monthly.revenue,
    monthly.order_count
FROM (
    SELECT
        SUBSTR(ordered_at, 1, 7) AS year_month,
        SUM(total_amount)        AS revenue,
        COUNT(*)                 AS order_count
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned')
    GROUP BY SUBSTR(ordered_at, 1, 7)
) AS monthly
ORDER BY revenue DESC
LIMIT 3;
```

**Result:**

| year_month | revenue | order_count |
|------------|---------|-------------|
| 2024-12 | 1841293.70 | 892 |
| 2023-12 | 1624817.40 | 801 |
| 2024-11 | 1312944.90 | 703 |

## Scalar Subqueries in SELECT

A subquery in the `SELECT` list runs once per output row.

```sql
-- Each customer with their most recent order date
SELECT
    c.name,
    c.grade,
    (
        SELECT MAX(ordered_at)
        FROM orders
        WHERE customer_id = c.id
    ) AS last_order_date
FROM customers AS c
WHERE c.is_active = 1
ORDER BY last_order_date DESC
LIMIT 8;
```

**Result:**

| name | grade | last_order_date |
|------|-------|-----------------|
| Jennifer Martinez | VIP | 2024-12-31 |
| David Park | GOLD | 2024-12-30 |
| ... | | |

> Scalar subqueries in `SELECT` can be slow on large tables because they run per row. Consider a `LEFT JOIN` with aggregation for better performance.

## Practice Exercises

### Exercise 1
Find all products whose price is higher than the average price of products in their own category. Return `product_name`, `price`, and `category_id`. Use a scalar subquery in the `WHERE` clause that references the outer query's `category_id`.

??? success "Answer"
    ```sql
    SELECT
        p.name        AS product_name,
        p.price,
        p.category_id
    FROM products AS p
    WHERE p.price > (
        SELECT AVG(p2.price)
        FROM products AS p2
        WHERE p2.category_id = p.category_id
          AND p2.is_active = 1
    )
      AND p.is_active = 1
    ORDER BY p.category_id, p.price DESC;
    ```

### Exercise 2
Use a `FROM` subquery to find the top 10 customers by number of completed orders. The inner query should count orders per customer; the outer query adds the customer's `name` and `grade` by joining to `customers`.

??? success "Answer"
    ```sql
    SELECT
        c.name,
        c.grade,
        order_stats.order_count,
        order_stats.total_spent
    FROM (
        SELECT
            customer_id,
            COUNT(*)            AS order_count,
            SUM(total_amount)   AS total_spent
        FROM orders
        WHERE status IN ('delivered', 'confirmed')
        GROUP BY customer_id
    ) AS order_stats
    INNER JOIN customers AS c ON order_stats.customer_id = c.id
    ORDER BY order_stats.order_count DESC
    LIMIT 10;
    ```

### Exercise 3
Find products that are in the wishlist of at least one customer but have **never appeared in any order**. Use `IN` and `NOT IN` subqueries. Return `product_name` and `price`.

??? success "Answer"
    ```sql
    SELECT name AS product_name, price
    FROM products
    WHERE id IN (
        SELECT DISTINCT product_id FROM wishlists
    )
      AND id NOT IN (
        SELECT DISTINCT product_id FROM order_items
    )
    ORDER BY price DESC;
    ```

---
Next: [Lesson 10: CASE Expressions](10-case.md)
