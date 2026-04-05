# Lesson 5: GROUP BY and HAVING

`GROUP BY` divides rows into groups and applies aggregate functions to each group separately. `HAVING` then filters those groups — it is the `WHERE` for aggregated results.

## GROUP BY — Single Column

```sql
-- How many customers in each membership grade?
SELECT
    grade,
    COUNT(*) AS customer_count
FROM customers
GROUP BY grade;
```

**Result:**

| grade | customer_count |
|-------|----------------|
| BRONZE | 2614 |
| SILVER | 1569 |
| GOLD | 785 |
| VIP | 262 |

The database collects all rows that share the same `grade` value into a bucket, then counts the rows in each bucket.

```sql
-- Total revenue by order status
SELECT
    status,
    COUNT(*)           AS order_count,
    SUM(total_amount)  AS total_revenue
FROM orders
GROUP BY status
ORDER BY total_revenue DESC;
```

**Result:**

| status | order_count | total_revenue |
|--------|-------------|---------------|
| confirmed | 8423 | 7291847.20 |
| delivered | 6812 | 5904329.10 |
| shipped | 4103 | 3287650.88 |
| cancelled | 3891 | 0.00 |
| ... | | |

## GROUP BY — Multiple Columns

Group by two or more columns to create finer-grained segments.

```sql
-- Count customers by grade AND gender
SELECT
    grade,
    gender,
    COUNT(*) AS cnt
FROM customers
WHERE gender IS NOT NULL
GROUP BY grade, gender
ORDER BY grade, gender;
```

**Result:**

| grade | gender | cnt |
|-------|--------|-----|
| BRONZE | F | 922 |
| BRONZE | M | 1580 |
| GOLD | F | 271 |
| GOLD | M | 494 |
| SILVER | F | 543 |
| SILVER | M | 990 |
| VIP | F | 91 |
| VIP | M | 163 |

## Monthly Order Counts

Date strings in SQLite (format `YYYY-MM-DD HH:MM:SS`) let you group by extracting a prefix.

```sql
-- Monthly order count for 2024
SELECT
    SUBSTR(ordered_at, 1, 7) AS year_month,
    COUNT(*)                 AS order_count,
    SUM(total_amount)        AS monthly_revenue
FROM orders
WHERE ordered_at LIKE '2024%'
GROUP BY SUBSTR(ordered_at, 1, 7)
ORDER BY year_month;
```

**Result:**

| year_month | order_count | monthly_revenue |
|------------|-------------|-----------------|
| 2024-01 | 312 | 178432.50 |
| 2024-02 | 289 | 162890.20 |
| 2024-03 | 405 | 238741.90 |
| ... | | |

## HAVING

`HAVING` filters after grouping, operating on aggregate values. Think of it as `WHERE` for groups.

```sql
-- Grades with more than 500 customers
SELECT
    grade,
    COUNT(*) AS customer_count
FROM customers
GROUP BY grade
HAVING COUNT(*) > 500;
```

**Result:**

| grade | customer_count |
|-------|----------------|
| BRONZE | 2614 |
| SILVER | 1569 |

```sql
-- Categories with at least 10 active products and avg price over $100
SELECT
    category_id,
    COUNT(*)   AS product_count,
    AVG(price) AS avg_price
FROM products
WHERE is_active = 1
GROUP BY category_id
HAVING COUNT(*) >= 10
   AND AVG(price) > 100
ORDER BY avg_price DESC;
```

**Result:**

| category_id | product_count | avg_price |
|-------------|---------------|-----------|
| 3 | 22 | 987.45 |
| 5 | 18 | 412.30 |
| 2 | 15 | 248.90 |
| ... | | |

## WHERE vs. HAVING

| Clause | Filters | Timing |
|--------|---------|--------|
| `WHERE` | Individual rows | Before grouping |
| `HAVING` | Groups | After grouping |

```sql
-- WHERE filters rows first, HAVING filters groups after
SELECT
    grade,
    AVG(point_balance) AS avg_points
FROM customers
WHERE is_active = 1          -- exclude inactive customers (row-level)
GROUP BY grade
HAVING AVG(point_balance) > 500;  -- only grades where avg points > 500
```

## Practice Exercises

### Exercise 1
Count the number of orders for each `status` value. Show only statuses that have more than 1,000 orders, ordered by count descending.

??? success "Answer"
    ```sql
    SELECT
        status,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY status
    HAVING COUNT(*) > 1000
    ORDER BY order_count DESC;
    ```

### Exercise 2
For each `method` in the `payments` table, calculate the total `amount` collected and the number of transactions. Order by total amount descending.

??? success "Answer"
    ```sql
    SELECT
        method,
        COUNT(*)       AS transaction_count,
        SUM(amount)    AS total_collected
    FROM payments
    WHERE status = 'completed'
    GROUP BY method
    ORDER BY total_collected DESC;
    ```

### Exercise 3
Find all months (from the `orders` table) in 2023 and 2024 where monthly revenue exceeded $500,000. Return `year_month` and `monthly_revenue`, sorted chronologically.

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS year_month,
        SUM(total_amount)        AS monthly_revenue
    FROM orders
    WHERE ordered_at BETWEEN '2023-01-01' AND '2024-12-31 23:59:59'
      AND status NOT IN ('cancelled', 'returned')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    HAVING SUM(total_amount) > 500000
    ORDER BY year_month;
    ```

---
Next: [Lesson 6: Working with NULL](06-null.md)
