# Lesson 4: Aggregate Functions

Aggregate functions collapse many rows into a single summary value. They are the building blocks for reports, dashboards, and business metrics.

## COUNT

`COUNT(*)` counts every row in the result. `COUNT(column)` counts non-NULL values in that column.

```sql
-- Total number of customers
SELECT COUNT(*) AS total_customers
FROM customers;
```

**Result:**

| total_customers |
|-----------------|
| 5230 |

```sql
-- Customers who provided their birth date
SELECT
    COUNT(*)           AS total_customers,
    COUNT(birth_date)  AS with_birth_date,
    COUNT(*) - COUNT(birth_date) AS missing_birth_date
FROM customers;
```

**Result:**

| total_customers | with_birth_date | missing_birth_date |
|-----------------|----------------|--------------------|
| 5230 | 4445 | 785 |

## SUM

`SUM` totals a numeric column. NULL values are ignored.

```sql
-- Total revenue across all completed orders
SELECT SUM(total_amount) AS total_revenue
FROM orders
WHERE status IN ('delivered', 'confirmed');
```

**Result:**

| total_revenue |
|---------------|
| 18473920.55 |

```sql
-- Total points currently held by all customers
SELECT SUM(point_balance) AS total_points_outstanding
FROM customers
WHERE is_active = 1;
```

**Result:**

| total_points_outstanding |
|--------------------------|
| 2847340 |

## AVG

`AVG` returns the arithmetic mean, ignoring NULLs.

```sql
-- Average product price
SELECT
    AVG(price)     AS avg_price,
    AVG(stock_qty) AS avg_stock
FROM products
WHERE is_active = 1;
```

**Result:**

| avg_price | avg_stock |
|-----------|-----------|
| 387.42 | 68.3 |

```sql
-- Average order value
SELECT AVG(total_amount) AS avg_order_value
FROM orders
WHERE status NOT IN ('cancelled', 'returned');
```

**Result:**

| avg_order_value |
|-----------------|
| 532.17 |

## MIN and MAX

`MIN` and `MAX` find the smallest and largest values in a column.

```sql
-- Price range for active products
SELECT
    MIN(price) AS cheapest,
    MAX(price) AS most_expensive
FROM products
WHERE is_active = 1;
```

**Result:**

| cheapest | most_expensive |
|----------|----------------|
| 9.99 | 2199.00 |

```sql
-- Earliest and latest order dates
SELECT
    MIN(ordered_at) AS first_order,
    MAX(ordered_at) AS latest_order
FROM orders;
```

**Result:**

| first_order | latest_order |
|-------------|--------------|
| 2015-03-14 08:23:11 | 2024-12-31 23:58:01 |

## Combining Multiple Aggregates

You can use several aggregates in the same `SELECT`:

```sql
-- Review statistics for TechShop
SELECT
    COUNT(*)                    AS total_reviews,
    AVG(rating)                 AS avg_rating,
    MIN(rating)                 AS lowest_rating,
    MAX(rating)                 AS highest_rating,
    SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) AS five_star_count
FROM reviews;
```

**Result:**

| total_reviews | avg_rating | lowest_rating | highest_rating | five_star_count |
|---------------|------------|---------------|----------------|-----------------|
| 7947 | 3.87 | 1 | 5 | 2341 |

## Practice Exercises

### Exercise 1
Count how many **active** products TechShop currently carries, and find the total inventory value (sum of `price * stock_qty`) for those products.

??? success "Answer"
    ```sql
    SELECT
        COUNT(*)                AS active_product_count,
        SUM(price * stock_qty)  AS total_inventory_value
    FROM products
    WHERE is_active = 1;
    ```

### Exercise 2
Calculate the average, minimum, and maximum `total_amount` for orders that were not cancelled or returned. Use aliases `avg_order`, `min_order`, and `max_order`.

??? success "Answer"
    ```sql
    SELECT
        AVG(total_amount) AS avg_order,
        MIN(total_amount) AS min_order,
        MAX(total_amount) AS max_order
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested');
    ```

### Exercise 3
How many orders have delivery instructions (`notes IS NOT NULL`)? What percentage of all orders is that? Return `orders_with_notes`, `total_orders`, and `pct_with_notes` (rounded to 1 decimal place).

??? success "Answer"
    ```sql
    SELECT
        COUNT(CASE WHEN notes IS NOT NULL THEN 1 END)  AS orders_with_notes,
        COUNT(*)                                        AS total_orders,
        ROUND(
            100.0 * COUNT(CASE WHEN notes IS NOT NULL THEN 1 END) / COUNT(*),
            1
        ) AS pct_with_notes
    FROM orders;
    ```

---
Next: [Lesson 5: GROUP BY and HAVING](05-group-by.md)
