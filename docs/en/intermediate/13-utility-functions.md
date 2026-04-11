# Lesson 13: Numeric, Conversion, and Conditional Functions

In [Lesson 12](12-string.md), we learned string functions. Beyond dates and strings, SQL also has math functions for numbers, conversion functions to change data types, and conditional functions to select values based on conditions. Learning all three at once greatly increases the expressiveness of your queries.

!!! note "Already familiar?"
    If you're comfortable with ROUND, ABS, CAST, NULLIF, and GREATEST/LEAST, skip ahead to [Lesson 14: UNION](14-union.md).

## Math Functions

### ROUND -- Rounding

`ROUND(value, digits)` rounds to the specified number of decimal places. We used it briefly in Lesson 4, but here we cover it systematically.

```sql
-- Average price at various decimal places
SELECT
    ROUND(AVG(price), 2)  AS avg_2dp,
    ROUND(AVG(price), 0)  AS avg_int,
    ROUND(AVG(price), -3) AS avg_1000
FROM products
WHERE is_active = 1;
```

**Result (example):**

| avg_2dp | avg_int | avg_1000 |
| ----------: | ----------: | ----------: |
| 678774.85 | 678775.0 | 678775.0 |

> `ROUND(value, -3)` rounds to the nearest thousand. Useful when displaying approximate values in reports.

### ABS -- Absolute Value

```sql
-- Difference between cost and selling price (prevent negatives)
SELECT
    name,
    price,
    cost_price,
    ABS(price - cost_price) AS margin
FROM products
WHERE is_active = 1
ORDER BY margin DESC
LIMIT 5;
```

### CEIL / FLOOR -- Ceiling and Floor

=== "SQLite"
    SQLite does not have `CEIL`/`FLOOR`. Use `CAST` and `CASE` as substitutes.

    ```sql
    -- Ceiling: round up shipping cost to nearest 1000
    SELECT
        CASE
            WHEN total_amount % 1000 = 0
                THEN total_amount / 1000
            ELSE total_amount / 1000 + 1
        END AS shipping_units
    FROM orders
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    SELECT
        CEIL(4.2)  AS ceil_val,   -- 5
        FLOOR(4.8) AS floor_val;  -- 4

    -- Round up shipping cost to nearest 1000
    SELECT
        total_amount,
        CEIL(total_amount / 1000.0) * 1000 AS rounded_up
    FROM orders
    LIMIT 5;
    ```

=== "PostgreSQL"
    ```sql
    SELECT
        CEIL(4.2)  AS ceil_val,   -- 5
        FLOOR(4.8) AS floor_val;  -- 4

    -- Round up shipping cost to nearest 1000
    SELECT
        total_amount,
        CEIL(total_amount / 1000.0) * 1000 AS rounded_up
    FROM orders
    LIMIT 5;
    ```

### MOD -- Remainder

```sql
-- Extract even-ID customers only (A/B test group splitting)
SELECT id, name, grade
FROM customers
WHERE MOD(id, 2) = 0
  AND is_active = 1
LIMIT 10;
```

> In SQLite, use the `a % b` operator instead of `MOD(a, b)`.

### RANDOM -- Random Sampling

=== "SQLite"
    ```sql
    -- Extract 5 random products
    SELECT name, price
    FROM products
    WHERE is_active = 1
    ORDER BY RANDOM()
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    -- Extract 5 random products
    SELECT name, price
    FROM products
    WHERE is_active = 1
    ORDER BY RAND()
    LIMIT 5;
    ```

=== "PostgreSQL"
    ```sql
    -- Extract 5 random products
    SELECT name, price
    FROM products
    WHERE is_active = 1
    ORDER BY RANDOM()
    LIMIT 5;
    ```

> **Warning:** `ORDER BY RANDOM()` sorts all rows, so it's slow on large tables. Use alternative sampling techniques in production.

## Type Conversion Functions

### CAST -- Type Conversion

`CAST(expression AS type)` explicitly converts data types. We already used `CAST(SUBSTR(...) AS INTEGER)` in Lesson 12.

```sql
-- String -> Number
SELECT CAST('12345' AS INTEGER) AS num_val;

-- Number -> String (for concatenation)
SELECT 'Order #' || CAST(id AS TEXT) AS label
FROM orders
LIMIT 3;
```

=== "SQLite"
    ```sql
    -- SQLite types: INTEGER, REAL, TEXT, BLOB, NUMERIC
    SELECT
        CAST(price AS INTEGER) AS int_price,
        CAST(id AS TEXT)       AS text_id,
        TYPEOF(price)          AS price_type
    FROM products
    LIMIT 3;
    ```

    > `TYPEOF(expr)` is a SQLite-specific function that returns the actual storage type of a value.

=== "MySQL"
    ```sql
    -- MySQL conversion types: SIGNED, UNSIGNED, CHAR, DATE, DECIMAL, etc.
    SELECT
        CAST(price AS SIGNED)       AS int_price,
        CAST(id AS CHAR)            AS text_id,
        CAST('2024-03-15' AS DATE)  AS date_val
    FROM products
    LIMIT 3;
    ```

=== "PostgreSQL"
    ```sql
    -- PostgreSQL also supports :: shorthand syntax
    SELECT
        price::integer    AS int_price,
        id::text          AS text_id,
        '2024-03-15'::date AS date_val
    FROM products
    LIMIT 3;
    ```

### Integer Division Pitfall

We covered this in Lesson 4, but it's the most common conversion mistake, so it's worth emphasizing again.

```sql
-- Integer / Integer = Integer (decimals truncated!)
SELECT 7 / 2 AS wrong;    -- 3 (not 3.5!)

-- Solution: Convert one side to float
SELECT 7 / 2.0 AS correct;           -- 3.5
SELECT CAST(7 AS REAL) / 2 AS also;  -- 3.5
SELECT 7 * 1.0 / 2 AS trick;         -- 3.5
```

```sql
-- Practical: Cancellation rate vs total orders
SELECT
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
    ROUND(
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        1
    ) AS cancel_rate_pct
FROM orders;
```

## Conditional Functions

### NULLIF -- Preventing Division by Zero

`NULLIF(a, b)` -- returns NULL if a equals b, otherwise returns a. Most commonly used to prevent division-by-zero errors.

```sql
-- Prevent division by zero
SELECT
    category_id,
    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_count,
    SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive_count,
    ROUND(
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) * 100.0
        / NULLIF(SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END), 0),
        1
    ) AS active_to_inactive_ratio
FROM products
GROUP BY category_id
LIMIT 5;
```

> `NULLIF(denominator, 0)` -- if the denominator is 0, returns NULL so you get NULL instead of an error.

### IIF / IF -- Simple Conditional Branching

A shorthand for CASE expressions. Can be written concisely when there is only one condition.

=== "SQLite"
    ```sql
    -- IIF(condition, true_value, false_value) — SQLite 3.32.0+
    SELECT
        name,
        price,
        IIF(price >= 1000000, '고가', '일반') AS price_tier
    FROM products
    WHERE is_active = 1
    LIMIT 10;
    ```

=== "MySQL"
    ```sql
    -- IF(condition, true_value, false_value)
    SELECT
        name,
        price,
        IF(price >= 1000000, '고가', '일반') AS price_tier
    FROM products
    WHERE is_active = 1
    LIMIT 10;
    ```

=== "PostgreSQL"
    ```sql
    -- PostgreSQL has no IIF/IF -> use CASE
    SELECT
        name,
        price,
        CASE WHEN price >= 1000000 THEN '고가' ELSE '일반' END AS price_tier
    FROM products
    WHERE is_active = 1
    LIMIT 10;
    ```

### GREATEST / LEAST -- Max/Min Among Multiple Values

Used to compare values across multiple columns within a row. `MAX`/`MIN` aggregate across rows, while `GREATEST`/`LEAST` compare across columns.

=== "SQLite"
    SQLite does not have `GREATEST`/`LEAST`. `MAX()`/`MIN()` serve the same purpose.

    ```sql
    -- Greater of order amount and 1,000,000 (guaranteed minimum)
    SELECT
        order_number,
        total_amount,
        MAX(total_amount, 1000000) AS guaranteed_min
    FROM orders
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    SELECT
        order_number,
        total_amount,
        GREATEST(total_amount, 1000000) AS guaranteed_min,
        LEAST(total_amount, 5000000)    AS capped_max
    FROM orders
    LIMIT 5;
    ```

=== "PostgreSQL"
    ```sql
    SELECT
        order_number,
        total_amount,
        GREATEST(total_amount, 1000000) AS guaranteed_min,
        LEAST(total_amount, 5000000)    AS capped_max
    FROM orders
    LIMIT 5;
    ```

> **MAX vs GREATEST:** `MAX(col)` finds the maximum across multiple **rows**, while `GREATEST(a, b, c)` finds the maximum among multiple **values** within a single **row**.

## Summary

| Concept | Description | Example |
|------|------|------|
| ROUND | Rounding (negative digits supported) | `ROUND(price, -3)` |
| ABS | Absolute value | `ABS(price - cost_price)` |
| CEIL / FLOOR | Ceiling / Floor | `CEIL(4.2)` → 5 |
| MOD (%) | Remainder | `MOD(id, 2)` = 짝수 필터 |
| RANDOM | Random ordering | `ORDER BY RANDOM()` |
| CAST | Type conversion | `CAST('123' AS INTEGER)` |
| TYPEOF | Type check (SQLite) | `TYPEOF(price)` |
| Integer division | integer/integer=integer pitfall | `* 1.0`으로 실수 변환 |
| NULLIF | NULL if equal | `NULLIF(분모, 0)` |
| IIF / IF | Simple conditional branching | `IIF(cond, true, false)` |
| GREATEST / LEAST | Max/min across columns | `GREATEST(a, b, c)` |

!!! note "Lesson Review Problems"
    These are simple problems to immediately test the concepts from this lesson. For comprehensive practice combining multiple concepts, see the [Practice Problems](../exercises/index.md) section.

## Practice Problems

### Problem 1
Display the average, maximum, and minimum prices of active products, each rounded to the nearest thousand. Return `avg_price`, `max_price`, `min_price`.

??? success "Answer"
    ```sql
    SELECT
        ROUND(AVG(price), -3) AS avg_price,
        ROUND(MAX(price), -3) AS max_price,
        ROUND(MIN(price), -3) AS min_price
    FROM products
    WHERE is_active = 1;
    ```


### Problem 2
Calculate the margin (difference between selling price and cost price) as an absolute value. Return `name`, `price`, `cost_price`, `margin`, sorted by margin descending, limited to 10 rows.

??? success "Answer"
    ```sql
    SELECT
        name,
        price,
        cost_price,
        ABS(price - cost_price) AS margin
    FROM products
    WHERE is_active = 1
    ORDER BY margin DESC
    LIMIT 10;
    ```


### Problem 3
Extract only odd-ID customers and return `id`, `name`, `grade`. Target only active customers, limited to 10 rows.

??? success "Answer"
    ```sql
    SELECT id, name, grade
    FROM customers
    WHERE id % 2 = 1
      AND is_active = 1
    LIMIT 10;
    ```


### Problem 4
Randomly extract 3 active products and return `name` and `price`.

??? success "Answer"
    === "SQLite / PostgreSQL"
        ```sql
        SELECT name, price
        FROM products
        WHERE is_active = 1
        ORDER BY RANDOM()
        LIMIT 3;
        ```

    === "MySQL"
        ```sql
        SELECT name, price
        FROM products
        WHERE is_active = 1
        ORDER BY RAND()
        LIMIT 3;
        ```


### Problem 5
Convert the last 5-digit sequence number from `order_number` to an integer, and convert the order amount to a string with `'₩'` prefix. Return `order_number`, `seq_no` (integer), `amount_display` (string), limited to 5 rows.

??? success "Answer"
    === "SQLite / PostgreSQL"
        ```sql
        SELECT
            order_number,
            CAST(SUBSTR(order_number, -5) AS INTEGER) AS seq_no,
            '₩' || CAST(total_amount AS TEXT)         AS amount_display
        FROM orders
        LIMIT 5;
        ```

    === "MySQL"
        ```sql
        SELECT
            order_number,
            CAST(SUBSTRING(order_number, -5) AS SIGNED) AS seq_no,
            CONCAT('₩', CAST(total_amount AS CHAR))     AS amount_display
        FROM orders
        LIMIT 5;
        ```


### Problem 6
Calculate the cancellation rate relative to total orders. Avoid the integer division pitfall and display to 1 decimal place. Return `total_orders`, `cancelled_orders`, `cancel_rate_pct`.

??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
        ROUND(
            SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
            1
        ) AS cancel_rate_pct
    FROM orders;
    ```


### Problem 7
Calculate the active product ratio per category, using `NULLIF` to prevent division-by-zero errors in categories with 0 inactive products. Return `category_id`, `active_count`, `inactive_count`, `ratio`.

??? success "Answer"
    ```sql
    SELECT
        category_id,
        SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_count,
        SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS inactive_count,
        ROUND(
            SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) * 1.0
            / NULLIF(SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END), 0),
            2
        ) AS ratio
    FROM products
    GROUP BY category_id;
    ```


### Problem 8
Classify product prices as `'premium'` if 1,000,000 or more, otherwise `'standard'`. Use `IIF` (SQLite) or `IF` (MySQL). Return `name`, `price`, `tier`, sorted by price descending, limited to 10 rows.

??? success "Answer"
    === "SQLite"
        ```sql
        SELECT
            name,
            price,
            IIF(price >= 1000000, '고가', '일반') AS tier
        FROM products
        WHERE is_active = 1
        ORDER BY price DESC
        LIMIT 10;
        ```

    === "MySQL"
        ```sql
        SELECT
            name,
            price,
            IF(price >= 1000000, '고가', '일반') AS tier
        FROM products
        WHERE is_active = 1
        ORDER BY price DESC
        LIMIT 10;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            name,
            price,
            CASE WHEN price >= 1000000 THEN '고가' ELSE '일반' END AS tier
        FROM products
        WHERE is_active = 1
        ORDER BY price DESC
        LIMIT 10;
        ```


### Problem 9
Cap order amounts: if below 500,000, set to 500,000; if above 5,000,000, set to 5,000,000. Return `order_number`, `total_amount`, `capped_amount`, limited to 10 rows.

??? success "Answer"
    === "SQLite"
        ```sql
        SELECT
            order_number,
            total_amount,
            MIN(MAX(total_amount, 500000), 5000000) AS capped_amount
        FROM orders
        LIMIT 10;
        ```

    === "MySQL / PostgreSQL"
        ```sql
        SELECT
            order_number,
            total_amount,
            LEAST(GREATEST(total_amount, 500000), 5000000) AS capped_amount
        FROM orders
        LIMIT 10;
        ```


### Problem 10
Calculate margin rate per product (`(price - cost_price) / price * 100`), handling products with a price of 0 to prevent errors. Return `name`, `price`, `cost_price`, `margin_pct` (1 decimal place), sorted by margin rate descending, limited to 10 rows.

??? success "Answer"
    ```sql
    SELECT
        name,
        price,
        cost_price,
        ROUND(
            (price - cost_price) * 100.0 / NULLIF(price, 0),
            1
        ) AS margin_pct
    FROM products
    WHERE is_active = 1
    ORDER BY margin_pct DESC
    LIMIT 10;
    ```


### Scoring Guide

| Score | Next Step |
|:----:|----------|
| **9-10** | Move on to [Lesson 14: UNION](14-union.md) |
| **7-8** | Review the explanations for incorrect answers, then proceed |
| **Half or fewer** | Re-read this lesson |
| **3 or fewer** | Start again from [Lesson 12: String Functions](12-string.md) |

**Problem Areas:**

| Area | Problems |
|------|:--------:|
| ROUND (rounding) | 1 |
| ABS (absolute value) | 2 |
| MOD (remainder) | 3 |
| RANDOM (random) | 4 |
| CAST (type conversion) | 5 |
| Integer division pitfall | 6 |
| NULLIF (prevent divide by zero) | 7, 10 |
| IIF / IF (simple conditional) | 8 |
| GREATEST / LEAST (cross-column comparison) | 9 |

---
Next: [Lesson 14: UNION](14-union.md)
