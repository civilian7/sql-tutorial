# Lesson 10: CASE Expressions

`CASE` is SQL's conditional expression — similar to `if/else` in programming languages. It lets you transform values, create labels, bucket data into ranges, and conditionally aggregate, all within a single query.

## Simple CASE

The simple form compares a single column against fixed values.

```sql
-- Translate order status codes to readable labels
SELECT
    order_number,
    total_amount,
    CASE status
        WHEN 'pending'          THEN 'Awaiting Payment'
        WHEN 'paid'             THEN 'Payment Received'
        WHEN 'preparing'        THEN 'Being Prepared'
        WHEN 'shipped'          THEN 'In Transit'
        WHEN 'delivered'        THEN 'Delivered'
        WHEN 'confirmed'        THEN 'Complete'
        WHEN 'cancelled'        THEN 'Cancelled'
        WHEN 'return_requested' THEN 'Return Pending'
        WHEN 'returned'         THEN 'Returned'
        ELSE status
    END AS status_label
FROM orders
ORDER BY ordered_at DESC
LIMIT 5;
```

**Result:**

| order_number | total_amount | status_label |
|--------------|--------------|--------------|
| ORD-20241231-09842 | 2349.00 | Complete |
| ORD-20241231-09841 | 149.99 | Delivered |
| ORD-20241231-09840 | 89.99 | In Transit |
| ORD-20241230-09839 | 749.00 | Complete |
| ORD-20241230-09838 | 329.97 | Cancelled |

## Searched CASE

The searched form evaluates independent `WHEN` conditions, giving you full flexibility with comparisons and expressions.

```sql
-- Bucket products into price tiers
SELECT
    name,
    price,
    CASE
        WHEN price < 50           THEN 'Budget'
        WHEN price BETWEEN 50 AND 199.99  THEN 'Mid-range'
        WHEN price BETWEEN 200 AND 799.99 THEN 'Premium'
        ELSE 'High-end'
    END AS price_tier
FROM products
WHERE is_active = 1
ORDER BY price ASC
LIMIT 10;
```

**Result:**

| name | price | price_tier |
|------|-------|------------|
| USB-C Cable 2m | 9.99 | Budget |
| Microfiber Cleaning Kit | 12.99 | Budget |
| Screen Protector 15" | 14.99 | Budget |
| SteelSeries Gaming Headset | 79.99 | Mid-range |
| Logitech MX Master 3 | 99.99 | Mid-range |
| Corsair 16GB DDR5 RAM | 129.99 | Mid-range |
| Samsung 27" Monitor | 449.99 | Premium |
| ... | | |

## CASE for Age Groups

```sql
-- Classify customers into age cohorts
SELECT
    name,
    birth_date,
    CASE
        WHEN birth_date IS NULL THEN 'Unknown'
        WHEN CAST(SUBSTR(birth_date, 1, 4) AS INTEGER) >= 1997 THEN 'Gen Z'
        WHEN CAST(SUBSTR(birth_date, 1, 4) AS INTEGER) >= 1981 THEN 'Millennial'
        WHEN CAST(SUBSTR(birth_date, 1, 4) AS INTEGER) >= 1965 THEN 'Gen X'
        ELSE 'Boomer+'
    END AS generation
FROM customers
LIMIT 8;
```

**Result:**

| name | birth_date | generation |
|------|------------|------------|
| Jennifer Martinez | 1989-04-12 | Millennial |
| Alex Chen | (NULL) | Unknown |
| Robert Kim | 1972-08-27 | Gen X |
| Sarah Johnson | 2000-01-15 | Gen Z |
| ... | | |

## CASE in GROUP BY and Aggregation

`CASE` can be used as a grouping expression or inside aggregate functions.

```sql
-- Count products per price tier
SELECT
    CASE
        WHEN price < 50           THEN 'Budget (<$50)'
        WHEN price BETWEEN 50 AND 199.99  THEN 'Mid-range ($50–$199)'
        WHEN price BETWEEN 200 AND 799.99 THEN 'Premium ($200–$799)'
        ELSE 'High-end ($800+)'
    END AS price_tier,
    COUNT(*)   AS product_count,
    AVG(price) AS avg_price
FROM products
WHERE is_active = 1
GROUP BY price_tier
ORDER BY avg_price;
```

**Result:**

| price_tier | product_count | avg_price |
|------------|---------------|-----------|
| Budget (<$50) | 42 | 23.87 |
| Mid-range ($50–$199) | 98 | 112.43 |
| Premium ($200–$799) | 87 | 421.29 |
| High-end ($800+) | 53 | 1342.18 |

```sql
-- Pivot: count orders by status as columns
SELECT
    SUBSTR(ordered_at, 1, 7) AS year_month,
    COUNT(CASE WHEN status = 'confirmed' THEN 1 END) AS confirmed,
    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) AS cancelled,
    COUNT(CASE WHEN status = 'returned'  THEN 1 END) AS returned,
    COUNT(*) AS total
FROM orders
WHERE ordered_at LIKE '2024%'
GROUP BY SUBSTR(ordered_at, 1, 7)
ORDER BY year_month;
```

**Result:**

| year_month | confirmed | cancelled | returned | total |
|------------|-----------|-----------|----------|-------|
| 2024-01 | 198 | 42 | 12 | 312 |
| 2024-02 | 183 | 38 | 9 | 289 |
| 2024-03 | 261 | 57 | 14 | 405 |
| ... | | | | |

## CASE in ORDER BY

You can sort by a computed expression.

```sql
-- Sort orders: active statuses first, terminal statuses last
SELECT order_number, status, total_amount
FROM orders
ORDER BY
    CASE status
        WHEN 'pending'   THEN 1
        WHEN 'paid'      THEN 2
        WHEN 'preparing' THEN 3
        WHEN 'shipped'   THEN 4
        ELSE 5
    END,
    total_amount DESC
LIMIT 10;
```

## Practice Exercises

### Exercise 1
Add a `stock_status` column to a product listing: `'Out of Stock'` when `stock_qty = 0`, `'Low Stock'` when `1–10`, `'In Stock'` when `11–100`, and `'Well Stocked'` when over 100. Return `name`, `stock_qty`, and `stock_status` for all active products.

??? success "Answer"
    ```sql
    SELECT
        name,
        stock_qty,
        CASE
            WHEN stock_qty = 0         THEN 'Out of Stock'
            WHEN stock_qty <= 10       THEN 'Low Stock'
            WHEN stock_qty <= 100      THEN 'In Stock'
            ELSE 'Well Stocked'
        END AS stock_status
    FROM products
    WHERE is_active = 1
    ORDER BY stock_qty ASC;
    ```

### Exercise 2
Create a generation breakdown report: count how many active customers fall into each generation (Gen Z: born 1997+, Millennial: 1981–1996, Gen X: 1965–1980, Boomer+: before 1965, Unknown: NULL birth_date). Return `generation` and `customer_count`.

??? success "Answer"
    ```sql
    SELECT
        CASE
            WHEN birth_date IS NULL THEN 'Unknown'
            WHEN CAST(SUBSTR(birth_date, 1, 4) AS INTEGER) >= 1997 THEN 'Gen Z'
            WHEN CAST(SUBSTR(birth_date, 1, 4) AS INTEGER) >= 1981 THEN 'Millennial'
            WHEN CAST(SUBSTR(birth_date, 1, 4) AS INTEGER) >= 1965 THEN 'Gen X'
            ELSE 'Boomer+'
        END AS generation,
        COUNT(*) AS customer_count
    FROM customers
    WHERE is_active = 1
    GROUP BY generation
    ORDER BY customer_count DESC;
    ```

### Exercise 3
For each product, calculate the revenue earned in each quarter of 2024 as separate columns (`q1_revenue`, `q2_revenue`, `q3_revenue`, `q4_revenue`) using conditional aggregation (`SUM(CASE WHEN ... THEN ... END)`). Only show products with any 2024 sales. Limit to 10 rows by total 2024 revenue descending.

??? success "Answer"
    ```sql
    SELECT
        p.name AS product_name,
        SUM(CASE WHEN o.ordered_at BETWEEN '2024-01-01' AND '2024-03-31 23:59:59'
                 THEN oi.quantity * oi.unit_price ELSE 0 END) AS q1_revenue,
        SUM(CASE WHEN o.ordered_at BETWEEN '2024-04-01' AND '2024-06-30 23:59:59'
                 THEN oi.quantity * oi.unit_price ELSE 0 END) AS q2_revenue,
        SUM(CASE WHEN o.ordered_at BETWEEN '2024-07-01' AND '2024-09-30 23:59:59'
                 THEN oi.quantity * oi.unit_price ELSE 0 END) AS q3_revenue,
        SUM(CASE WHEN o.ordered_at BETWEEN '2024-10-01' AND '2024-12-31 23:59:59'
                 THEN oi.quantity * oi.unit_price ELSE 0 END) AS q4_revenue
    FROM order_items AS oi
    INNER JOIN orders    AS o ON oi.order_id   = o.id
    INNER JOIN products  AS p ON oi.product_id = p.id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled', 'returned')
    GROUP BY p.id, p.name
    ORDER BY (q1_revenue + q2_revenue + q3_revenue + q4_revenue) DESC
    LIMIT 10;
    ```

---
Next: [Lesson 11: Date and Time Functions](11-datetime.md)
