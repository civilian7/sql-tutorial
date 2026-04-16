# SQL Error Detection -- Beginner

!!! info "Tables"
    `products` — Products (name, price, stock, brand)  
    `customers` — Customers (grade, points, channel)  
    `orders` — Orders (status, amount, date)  
    `reviews` — Reviews (rating, content)  
    `payments` — Payments (method, amount, status)  

!!! abstract "Concepts"
    Finding and fixing syntax/logic errors from Beginner Lessons 1-7

Find syntax errors.

---

### Problem 1

Find and fix the error in the following query.

```sql
SELECT name price brand
FROM products
LIMIT 5;
```

??? tip "Hint"
    Check the required separator when listing columns in the SELECT clause.

??? success "Answer"
    **Error:** Commas (`,`) are missing between columns.

    **Fix:**
    ```sql
    SELECT name, price, brand
    FROM products
    LIMIT 5;
    ```

---

### Problem 2

Find and fix the error in the following query.

```sql
SELECT name, price
FROM products
WHERE brand = "ASUS";
```

??? tip "Hint"
    Check the type of quotes used for string literals in the SQL standard. It may work in SQLite, but it's problematic from a standard SQL perspective.

??? success "Answer"
    **Error:** In the SQL standard, string literals use single quotes (`'`). Double quotes (`"`) are for identifiers (column names, table names). SQLite allows double quotes for strings, but other databases will throw an error.

    **Fix:**
    ```sql
    SELECT name, price
    FROM products
    WHERE brand = 'ASUS';
    ```

---

### Problem 3

Find and fix the error in the following query.

```sql
SELCET name, email
FROM customers
WHERE grade = 'VIP';
```

??? tip "Hint"
    Check the spelling of the SQL keyword.

??? success "Answer"
    **Error:** `SELCET` is a typo. The correct keyword is `SELECT`.

    **Fix:**
    ```sql
    SELECT name, email
    FROM customers
    WHERE grade = 'VIP';
    ```

---

### Problem 4

Find and fix the error in the following query.

```sql
SELECT name, price
FROM products
WHERE price BETWEEN 100000 AND 500000
ORDER BY price
LIMIT 10;
```

??? tip "Hint"
    This query is actually syntactically correct. Think about the default sort direction of `ORDER BY price`. What if the intent is "most expensive first"?

??? success "Answer"
    **Error:** There is no syntax error, but `ORDER BY price` defaults to ascending (ASC). If the intent is to sort most expensive first, `DESC` is needed. This may or may not be correct depending on intent.

    **Fix (if descending order is intended):**
    ```sql
    SELECT name, price
    FROM products
    WHERE price BETWEEN 100000 AND 500000
    ORDER BY price DESC
    LIMIT 10;
    ```

---

### Problem 5

Find and fix the error in the following query.

```sql
SELECT name, email, grade
FROM customers
WHERE grade = 'VIP'
ORDER name;
```

??? tip "Hint"
    Check the exact keyword used for sorting.

??? success "Answer"
    **Error:** `ORDER name` is incorrect syntax. The correct form is `ORDER BY name`.

    **Fix:**
    ```sql
    SELECT name, email, grade
    FROM customers
    WHERE grade = 'VIP'
    ORDER BY name;
    ```

---

### Problem 6

Find and fix the error in the following query.

```sql
SELECT name, price
FROM products
WHERE name LIKE '%게이밍'%;
```

??? tip "Hint"
    Check the position of the quotes in the LIKE pattern. The `%` must be inside the string.

??? success "Answer"
    **Error:** The closing quote in `'%게이밍'%` is in the wrong position. The `%` is outside the string.

    **Fix:**
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%게이밍%';
    ```

---

### Problem 7

Find and fix the error in the following query.

```sql
SELECT name, price, stock_qty
FROM products
WHERE price > 100000
  AND stock_qty > 0
ORDER BY price DESC
LIMIT 10
WHERE is_active = 1;
```

??? tip "Hint"
    Check the order of SQL clauses. Where should WHERE be positioned?

??? success "Answer"
    **Error:** The `WHERE` clause is used twice, and it cannot appear after `LIMIT`. All conditions must be combined with `AND` in a single `WHERE` clause.

    **Fix:**
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE price > 100000
      AND stock_qty > 0
      AND is_active = 1
    ORDER BY price DESC
    LIMIT 10;
    ```

---

### Problem 8

Find and fix the error in the following query.

```sql
SELECT name AS product_name price AS unit_price
FROM products
LIMIT 5;
```

??? tip "Hint"
    Even when assigning column aliases in the SELECT clause, something is needed between columns.

??? success "Answer"
    **Error:** A comma (`,`) is missing between `product_name` and `price`.

    **Fix:**
    ```sql
    SELECT name AS product_name, price AS unit_price
    FROM products
    LIMIT 5;
    ```

---

### Problem 9

Find and fix the error in the following query.

```sql
SELECT name, price
FROM products
WHERE brand IN ('ASUS' 'MSI' 'Dell');
```

??? tip "Hint"
    Check the separator between values in the `IN` list.

??? success "Answer"
    **Error:** Commas are missing between values in the `IN` list. `('ASUS' 'MSI' 'Dell')` may be interpreted as string concatenation.

    **Fix:**
    ```sql
    SELECT name, price
    FROM products
    WHERE brand IN ('ASUS', 'MSI', 'Dell');
    ```

---

### Problem 10

Find and fix the error in the following query.

```sql
SELECT COUNT(*) AS total,
       AVG(price) AS avg_price
       SUM(price) AS total_price
FROM products;
```

??? tip "Hint"
    Check the separator between columns in the SELECT list.

??? success "Answer"
    **Error:** A comma is missing between `AVG(price) AS avg_price` and `SUM(price) AS total_price`.

    **Fix:**
    ```sql
    SELECT COUNT(*) AS total,
           AVG(price) AS avg_price,
           SUM(price) AS total_price
    FROM products;
    ```

---

Find logic errors.

---

### Problem 11

The following query tries to find customers without a birth date. The result returns 0 rows. Why?

```sql
SELECT name, email
FROM customers
WHERE birth_date = NULL;
```

??? tip "Hint"
    In SQL, NULL means "unknown value." What happens when you compare with `=`? The result is always something specific.

??? success "Answer"
    **Error:** `NULL = NULL` returns NULL (UNKNOWN), not TRUE. You must use `IS NULL` instead of `= NULL` when comparing with NULL.

    **Fix:**
    ```sql
    SELECT name, email
    FROM customers
    WHERE birth_date IS NULL;
    ```

---

### Problem 12

The following query tries to find the product count per brand. It throws an error.

```sql
SELECT brand, COUNT(*) AS product_count
FROM products;
```

??? tip "Hint"
    There is a required clause when using an aggregate function alongside a non-aggregate column in SELECT.

??? success "Answer"
    **Error:** `COUNT(*)` is an aggregate function, but `brand` is a non-aggregate column. Without a `GROUP BY` clause, the database cannot determine which brand value to display.

    **Fix:**
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand;
    ```

---

### Problem 13

The following query tries to show only brands with 10 or more products. It throws an error.

```sql
SELECT brand, COUNT(*) AS product_count
FROM products
WHERE COUNT(*) >= 10
GROUP BY brand;
```

??? tip "Hint"
    Can aggregate functions be used in the `WHERE` clause?

??? success "Answer"
    **Error:** Aggregate functions cannot be used in the `WHERE` clause. Filtering after grouping requires `HAVING`.

    **Fix:**
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10;
    ```

---

### Problem 14

The following query tries to find products that are not 'ASUS'. However, products with a NULL brand are missing from the results.

```sql
SELECT name, brand
FROM products
WHERE brand != 'ASUS';
```

??? tip "Hint"
    What is the result of `NULL != 'ASUS'`? Comparisons with NULL always return NULL (UNKNOWN).

??? success "Answer"
    **Error:** For rows where `brand` is NULL, `NULL != 'ASUS'` returns NULL (UNKNOWN), so those rows are excluded from the results. To include NULL rows, you must handle them explicitly.

    **Fix:**
    ```sql
    SELECT name, brand
    FROM products
    WHERE brand != 'ASUS' OR brand IS NULL;
    ```

    > In the products table, brand is NOT NULL, so this issue wouldn't actually occur. However, for nullable columns, this is an important consideration.

---

### Problem 15

The following query tries to find the top 10 orders by amount. The ORDER BY placement is wrong.

```sql
SELECT order_number, total_amount
FROM orders
LIMIT 10
ORDER BY total_amount DESC;
```

??? tip "Hint"
    Think about the execution order of SQL clauses. Which should come first, LIMIT or ORDER BY?

??? success "Answer"
    **Error:** `LIMIT` appears before `ORDER BY`. In SQL, `ORDER BY` must come before `LIMIT`. This query retrieves any 10 rows without sorting first, then sorts them, so the result is not the top 10.

    **Fix:**
    ```sql
    SELECT order_number, total_amount
    FROM orders
    ORDER BY total_amount DESC
    LIMIT 10;
    ```

---

### Problem 16

The following query sorts the average points per tier in descending order. It uses an alias in ORDER BY, which may not work in some cases.

```sql
SELECT grade,
       AVG(point_balance) AS avg_points
FROM customers
GROUP BY grade
ORDER BY avg_points DESC;
```

??? tip "Hint"
    This query works correctly in SQLite. However, some databases have restrictions on using aliases in `ORDER BY`. What alternative exists?

??? success "Answer"
    **Error:** This works in SQLite, but some databases (especially older versions) do not recognize SELECT aliases in `ORDER BY`.

    **Fix (more portable version):**
    ```sql
    SELECT grade,
           AVG(point_balance) AS avg_points
    FROM customers
    GROUP BY grade
    ORDER BY AVG(point_balance) DESC;
    ```

---

### Problem 17

The following query tries to find only customers where gender is not NULL. The logic is wrong.

```sql
SELECT name, gender
FROM customers
WHERE gender != NULL;
```

??? tip "Hint"
    Same principle as Problem 11. The `!=` comparison with NULL also returns NULL.

??? success "Answer"
    **Error:** `gender != NULL` always returns NULL (UNKNOWN), resulting in 0 rows. You must use `IS NOT NULL`.

    **Fix:**
    ```sql
    SELECT name, gender
    FROM customers
    WHERE gender IS NOT NULL;
    ```

---

### Problem 18

The following query finds the count per order status and filters with HAVING. But the intent is wrong.

```sql
SELECT status, COUNT(*) AS order_count
FROM orders
GROUP BY status
HAVING status = 'confirmed';
```

??? tip "Hint"
    `HAVING` is meant for filtering aggregate results. What clause should be used for simple column value filtering?

??? success "Answer"
    **Error:** `HAVING status = 'confirmed'` works, but `HAVING` is intended for aggregate function conditions. Simple value filtering should use `WHERE`. Using `WHERE` filters before grouping, which is more efficient.

    **Fix:**
    ```sql
    SELECT status, COUNT(*) AS order_count
    FROM orders
    WHERE status = 'confirmed'
    GROUP BY status;
    ```

---

### Problem 19

The following query finds the count per brand for products priced 1M+. There is an issue with GROUP BY.

```sql
SELECT brand, name, COUNT(*) AS cnt
FROM products
WHERE price >= 1000000
GROUP BY brand;
```

??? tip "Hint"
    All non-aggregate columns in SELECT must be included in GROUP BY. What about `name`?

??? success "Answer"
    **Error:** `name` is in SELECT but not included in `GROUP BY`. When grouping by brand, each group may contain multiple names, so it's unclear which name to display. In SQLite, an arbitrary value is selected without error, but the result is meaningless.

    **Fix (if only the count per brand is needed):**
    ```sql
    SELECT brand, COUNT(*) AS cnt
    FROM products
    WHERE price >= 1000000
    GROUP BY brand;
    ```

---

### Problem 20

The following query finds the order count per year. The results look wrong.

```sql
SELECT ordered_at AS year, COUNT(*) AS order_count
FROM orders
GROUP BY ordered_at;
```

??? tip "Hint"
    `ordered_at` contains both date and time. How should you group by year?

??? success "Answer"
    **Error:** `ordered_at` is a full timestamp like `2024-03-15 14:30:00`. Grouping by this means almost every row becomes its own group. You need to extract only the year.

    **Fix:**
    ```sql
    SELECT SUBSTR(ordered_at, 1, 4) AS year, COUNT(*) AS order_count
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```

---

Find subtle errors.

---

### Problem 21

The following query calculates the margin rate (%) for products. Some products show a margin of 0%.

```sql
SELECT name, price, cost_price,
       (price - cost_price) / price * 100 AS margin_pct
FROM products
WHERE is_active = 1
LIMIT 10;
```

??? tip "Hint"
    What happens when you divide two integers in SQLite?

??? success "Answer"
    **Error:** In SQLite, integer division truncates the decimal part. When `price` and `cost_price` are integers, `(price - cost_price) / price` can result in 0. Example: `(100 - 80) / 100 = 0` (integer division).

    **Fix:**
    ```sql
    SELECT name, price, cost_price,
           ROUND((price - cost_price) * 100.0 / price, 1) AS margin_pct
    FROM products
    WHERE is_active = 1
    LIMIT 10;
    ```

    > Multiplying by `100.0` or appending `* 1.0` forces floating-point arithmetic.

---

### Problem 22

The following query has a CASE expression missing the ELSE clause. What problem can occur?

```sql
SELECT name, price,
       CASE
           WHEN price < 100000 THEN 'Budget'
           WHEN price < 500000 THEN 'Mid-low'
           WHEN price < 1000000 THEN 'Mid'
       END AS price_tier
FROM products;
```

??? tip "Hint"
    What value will products priced 1M+ receive?

??? success "Answer"
    **Error:** Without `ELSE`, rows that don't match any `WHEN` condition return `NULL`. Products priced 1M+ will have `NULL` as their `price_tier`.

    **Fix:**
    ```sql
    SELECT name, price,
           CASE
               WHEN price < 100000 THEN 'Budget'
               WHEN price < 500000 THEN 'Mid-low'
               WHEN price < 1000000 THEN 'Mid'
               ELSE 'Premium'
           END AS price_tier
    FROM products;
    ```

---

### Problem 23

The following query uses an alias in HAVING. It may throw an error.

```sql
SELECT brand, COUNT(*) AS cnt
FROM products
GROUP BY brand
HAVING cnt >= 10;
```

??? tip "Hint"
    SQLite allows using aliases in HAVING, but what about MySQL, PostgreSQL, etc.?

??? success "Answer"
    **Error:** This works in SQLite, but most databases (MySQL, PostgreSQL, SQL Server) do not recognize SELECT aliases in the `HAVING` clause. You should use the aggregate function directly in `HAVING`.

    **Fix:**
    ```sql
    SELECT brand, COUNT(*) AS cnt
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10;
    ```

---

### Problem 24

The following query calculates the discount rate for orders. A division-by-zero error may occur.

```sql
SELECT order_number,
       total_amount,
       discount_amount,
       ROUND(discount_amount * 100.0 / total_amount, 1) AS discount_rate
FROM orders
ORDER BY discount_rate DESC
LIMIT 10;
```

??? tip "Hint"
    What happens if `total_amount` is 0?

??? success "Answer"
    **Error:** If `total_amount` is 0, a division-by-zero error occurs. In SQLite, it returns NULL instead of an error, but this is an unintended result.

    **Fix:**
    ```sql
    SELECT order_number,
           total_amount,
           discount_amount,
           CASE
               WHEN total_amount = 0 THEN 0
               ELSE ROUND(discount_amount * 100.0 / total_amount, 1)
           END AS discount_rate
    FROM orders
    ORDER BY discount_rate DESC
    LIMIT 10;
    ```

---

### Problem 25

The following query finds monthly statistics for 2024 orders. The month sorting is wrong.

```sql
SELECT SUBSTR(ordered_at, 6, 2) AS month,
       COUNT(*) AS order_count
FROM orders
WHERE ordered_at LIKE '2024%'
GROUP BY month
ORDER BY order_count DESC;
```

??? tip "Hint"
    For "monthly statistics," it's natural to view from January to December in chronological order. What is the current sort criterion?

??? success "Answer"
    **Error:** The query sorts by `ORDER BY order_count DESC` (count descending). To see the monthly trend, the data should be sorted by month in chronological order.

    **Fix:**
    ```sql
    SELECT SUBSTR(ordered_at, 6, 2) AS month,
           COUNT(*) AS order_count
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```

---

### Problem 26

The following query finds the average and total points per tier. ROUND is applied to only one place.

```sql
SELECT grade,
       ROUND(AVG(point_balance)) AS avg_points,
       SUM(point_balance) AS total_points,
       COUNT(*) AS customer_count,
       AVG(point_balance) AS avg_points_raw
FROM customers
GROUP BY grade;
```

??? tip "Hint"
    The same value (`AVG(point_balance)`) is queried twice -- one with ROUND, one without. This isn't an error per se, but `avg_points_raw` will show a long decimal number.

??? success "Answer"
    **Error:** `avg_points_raw` is an unnecessary duplicate and is displayed without rounding. Computing the same column twice is inefficient and confusing.

    **Fix:**
    ```sql
    SELECT grade,
           ROUND(AVG(point_balance)) AS avg_points,
           SUM(point_balance) AS total_points,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade;
    ```

---

### Problem 27

The following query finds products containing 'Black' or 'White' in the name. The results are more than expected.

```sql
SELECT name, price
FROM products
WHERE name LIKE '%블랙%'
   OR name LIKE '%화이트%'
   AND price > 500000;
```

??? tip "Hint"
    Check the operator precedence of `AND` and `OR`. Which is evaluated first?

??? success "Answer"
    **Error:** `AND` has higher precedence than `OR`. So this query is interpreted as `name LIKE '%블랙%'` OR (`name LIKE '%화이트%'` AND `price > 500000`). All products with 'Black' are included regardless of price.

    **Fix (both conditions require price > 500,000):**
    ```sql
    SELECT name, price
    FROM products
    WHERE (name LIKE '%블랙%' OR name LIKE '%화이트%')
      AND price > 500000;
    ```

---

### Problem 28

The following query calculates the sum of columns that may contain NULL. The results differ from expectations.

```sql
SELECT COUNT(*) AS total_orders,
       SUM(discount_amount) + SUM(shipping_fee) AS extra_charges,
       AVG(discount_amount + shipping_fee) AS avg_extra
FROM orders;
```

??? tip "Hint"
    If `discount_amount` or `shipping_fee` is NULL, `SUM` ignores NULLs, but what about `discount_amount + shipping_fee`?

??? success "Answer"
    **Error:** `SUM` ignores NULLs, but in `discount_amount + shipping_fee`, if either side is NULL, the result is NULL. `AVG(discount_amount + shipping_fee)` will skip those rows. Also, `SUM(A) + SUM(B)` and `SUM(A + B)` handle NULLs differently.

    **Fix:**
    ```sql
    SELECT COUNT(*) AS total_orders,
           SUM(COALESCE(discount_amount, 0)) + SUM(COALESCE(shipping_fee, 0)) AS extra_charges,
           AVG(COALESCE(discount_amount, 0) + COALESCE(shipping_fee, 0)) AS avg_extra
    FROM orders;
    ```

---

### Problem 29

The following query finds product count by price tier. The CASE condition order is wrong.

```sql
SELECT CASE
           WHEN price >= 0 THEN 'Budget'
           WHEN price >= 100000 THEN 'Mid-low'
           WHEN price >= 500000 THEN 'Mid'
           WHEN price >= 1000000 THEN 'Premium'
       END AS price_tier,
       COUNT(*) AS cnt
FROM products
GROUP BY price_tier;
```

??? tip "Hint"
    CASE evaluates conditions top-to-bottom and stops at the first TRUE condition. All product prices are >= 0.

??? success "Answer"
    **Error:** `price >= 0` is TRUE for all products, so every product is classified as 'Budget'. CASE conditions should start with the largest value, or use explicit ranges.

    **Fix:**
    ```sql
    SELECT CASE
               WHEN price >= 1000000 THEN 'Premium'
               WHEN price >= 500000 THEN 'Mid'
               WHEN price >= 100000 THEN 'Mid-low'
               ELSE 'Budget'
           END AS price_tier,
           COUNT(*) AS cnt
    FROM products
    GROUP BY price_tier;
    ```

---

### Problem 30

The following query analyzes customer data by signup year. WHERE and HAVING are confused.

```sql
SELECT SUBSTR(created_at, 1, 4) AS join_year,
       grade,
       COUNT(*) AS customer_count,
       ROUND(AVG(point_balance)) AS avg_points
FROM customers
HAVING grade IN ('GOLD', 'VIP')
GROUP BY join_year, grade
HAVING COUNT(*) >= 50
ORDER BY join_year, grade;
```

??? tip "Hint"
    HAVING is used twice, and the SQL clause order is also wrong. Distinguish between row-level filtering and group-level filtering.

??? success "Answer"
    **Error:** There are three problems:
    1. `HAVING` appears before `GROUP BY` (clause order error).
    2. `HAVING` is used twice.
    3. `grade IN ('GOLD', 'VIP')` is row-level filtering, so `WHERE` should be used.

    **Fix:**
    ```sql
    SELECT SUBSTR(created_at, 1, 4) AS join_year,
           grade,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    WHERE grade IN ('GOLD', 'VIP')
    GROUP BY join_year, grade
    HAVING COUNT(*) >= 50
    ORDER BY join_year, grade;
    ```
