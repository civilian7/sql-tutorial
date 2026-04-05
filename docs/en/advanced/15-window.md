# Lesson 15: Window Functions

Window functions perform calculations across a set of rows that are related to the current row — without collapsing the result set like `GROUP BY` does. Each row keeps its identity while gaining access to aggregate or ranking information.

The syntax is: `function() OVER (PARTITION BY ... ORDER BY ...)`

## ROW_NUMBER, RANK, DENSE_RANK

These ranking functions assign a position to each row within a partition.

| Function | Ties | Gaps after ties |
|----------|------|-----------------|
| `ROW_NUMBER()` | Arbitrary tie-breaking | — |
| `RANK()` | Same rank | Yes (1,1,3) |
| `DENSE_RANK()` | Same rank | No (1,1,2) |

```sql
-- Rank products by price within each category
SELECT
    cat.name            AS category,
    p.name              AS product_name,
    p.price,
    RANK() OVER (
        PARTITION BY p.category_id
        ORDER BY p.price DESC
    ) AS price_rank
FROM products AS p
INNER JOIN categories AS cat ON p.category_id = cat.id
WHERE p.is_active = 1
ORDER BY cat.name, price_rank
LIMIT 12;
```

**Result:**

| category | product_name | price | price_rank |
|----------|--------------|-------|------------|
| Desktops | ASUS ROG Gaming Desktop | 1899.00 | 1 |
| Desktops | CyberPowerPC Gamer Xtreme | 1299.00 | 2 |
| Desktops | Acer Aspire TC | 549.00 | 3 |
| Laptops | Dell XPS 17 Laptop | 1999.00 | 1 |
| Laptops | MacBook Pro 16" M3 | 1799.00 | 2 |
| Laptops | Dell XPS 15 Laptop | 1299.99 | 3 |
| ... | | | |

## Top-N per Group

Wrap a ranked query in a CTE or subquery to pick the top N per partition.

```sql
-- Top 3 best-selling products per category (by units sold)
WITH ranked_sales AS (
    SELECT
        cat.name                        AS category,
        p.name                          AS product_name,
        SUM(oi.quantity)                AS units_sold,
        RANK() OVER (
            PARTITION BY p.category_id
            ORDER BY SUM(oi.quantity) DESC
        ) AS sales_rank
    FROM order_items AS oi
    INNER JOIN products   AS p   ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN orders     AS o   ON oi.order_id   = o.id
    WHERE o.status IN ('delivered', 'confirmed')
    GROUP BY p.category_id, p.id, p.name, cat.name
)
SELECT category, product_name, units_sold, sales_rank
FROM ranked_sales
WHERE sales_rank <= 3
ORDER BY category, sales_rank;
```

## SUM OVER — Running Totals

`SUM() OVER (ORDER BY ...)` computes a cumulative total.

```sql
-- Cumulative revenue by month for 2024
SELECT
    SUBSTR(ordered_at, 1, 7) AS year_month,
    SUM(total_amount)        AS monthly_revenue,
    SUM(SUM(total_amount)) OVER (
        ORDER BY SUBSTR(ordered_at, 1, 7)
    ) AS cumulative_revenue
FROM orders
WHERE ordered_at LIKE '2024%'
  AND status NOT IN ('cancelled', 'returned')
GROUP BY SUBSTR(ordered_at, 1, 7)
ORDER BY year_month;
```

**Result:**

| year_month | monthly_revenue | cumulative_revenue |
|------------|-----------------|-------------------|
| 2024-01 | 147832.40 | 147832.40 |
| 2024-02 | 136290.10 | 284122.50 |
| 2024-03 | 204123.70 | 488246.20 |
| 2024-04 | 178912.30 | 667158.50 |
| ... | | |

## LAG and LEAD — Accessing Adjacent Rows

`LAG(col, n)` looks back `n` rows; `LEAD(col, n)` looks forward. Both accept a default value when the reference row doesn't exist.

```sql
-- Month-over-month revenue growth for 2024
SELECT
    year_month,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY year_month) AS prev_month_revenue,
    ROUND(
        100.0 * (monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY year_month))
              / LAG(monthly_revenue) OVER (ORDER BY year_month),
        1
    ) AS mom_growth_pct
FROM (
    SELECT
        SUBSTR(ordered_at, 1, 7) AS year_month,
        SUM(total_amount)        AS monthly_revenue
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND status NOT IN ('cancelled', 'returned')
    GROUP BY SUBSTR(ordered_at, 1, 7)
) AS monthly
ORDER BY year_month;
```

**Result:**

| year_month | monthly_revenue | prev_month_revenue | mom_growth_pct |
|------------|-----------------|-------------------|----------------|
| 2024-01 | 147832.40 | (NULL) | (NULL) |
| 2024-02 | 136290.10 | 147832.40 | -7.8 |
| 2024-03 | 204123.70 | 136290.10 | 49.8 |
| 2024-04 | 178912.30 | 204123.70 | -12.4 |
| ... | | | |

## PARTITION BY with LEAD

```sql
-- For each customer, show their orders with the days until their next order
SELECT
    c.name          AS customer_name,
    o.order_number,
    o.ordered_at,
    LEAD(o.ordered_at) OVER (
        PARTITION BY o.customer_id
        ORDER BY o.ordered_at
    ) AS next_order_date,
    ROUND(
        julianday(
            LEAD(o.ordered_at) OVER (PARTITION BY o.customer_id ORDER BY o.ordered_at)
        ) - julianday(o.ordered_at),
        0
    ) AS days_to_next_order
FROM orders AS o
INNER JOIN customers AS c ON o.customer_id = c.id
WHERE c.grade = 'VIP'
ORDER BY c.name, o.ordered_at
LIMIT 10;
```

## Practice Exercises

### Exercise 1
Rank all active products by `price` descending using `DENSE_RANK()`. Return `product_name`, `price`, and `overall_rank`. Show the top 10.

??? success "Answer"
    ```sql
    SELECT
        name    AS product_name,
        price,
        DENSE_RANK() OVER (ORDER BY price DESC) AS overall_rank
    FROM products
    WHERE is_active = 1
    ORDER BY overall_rank
    LIMIT 10;
    ```

### Exercise 2
Calculate the running total of new customer signups by year (cumulative customer count from the beginning of TechShop through each year). Return `year`, `new_signups`, and `cumulative_customers`.

??? success "Answer"
    ```sql
    SELECT
        year,
        new_signups,
        SUM(new_signups) OVER (ORDER BY year) AS cumulative_customers
    FROM (
        SELECT
            SUBSTR(created_at, 1, 4) AS year,
            COUNT(*)                 AS new_signups
        FROM customers
        GROUP BY SUBSTR(created_at, 1, 4)
    ) AS yearly
    ORDER BY year;
    ```

### Exercise 3
For each month in 2023 and 2024, compute the year-over-year (YoY) revenue growth. Use `LAG(revenue, 12)` to compare the same month in the prior year. Return `year_month`, `revenue`, `same_month_last_year`, and `yoy_growth_pct`.

??? success "Answer"
    ```sql
    SELECT
        year_month,
        revenue,
        LAG(revenue, 12) OVER (ORDER BY year_month) AS same_month_last_year,
        ROUND(
            100.0 * (revenue - LAG(revenue, 12) OVER (ORDER BY year_month))
                  / LAG(revenue, 12) OVER (ORDER BY year_month),
            1
        ) AS yoy_growth_pct
    FROM (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            SUM(total_amount)        AS revenue
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned')
          AND ordered_at BETWEEN '2022-01-01' AND '2024-12-31 23:59:59'
        GROUP BY SUBSTR(ordered_at, 1, 7)
    ) AS monthly
    WHERE year_month >= '2023-01'
    ORDER BY year_month;
    ```

---
Next: [Lesson 16: Common Table Expressions (WITH)](16-cte.md)
