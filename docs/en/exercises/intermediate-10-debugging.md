# SQL Debugging -- Intermediate

!!! info "Tables"
    `customers` — Customers (grade, points, channel)  
    `orders` — Orders (status, amount, date)  
    `order_items` — Order items (qty, unit price)  
    `products` — Products (name, price, stock, brand)  
    `categories` — Categories (parent-child hierarchy)  
    `suppliers` — Suppliers (company, contact)  
    `reviews` — Reviews (rating, content)  
    `shipping` — Shipping (carrier, tracking, status)  
    `payments` — Payments (method, amount, status)  

!!! abstract "Concepts"
    JOIN, Subqueries, Date functions, Aggregation, UNION, Diagnosing and fixing errors from intermediate syntax (Lessons 08~17) including DML

!!! info "Before You Begin"
    In practice, **logical errors** are more common than syntax errors when writing SQL.
    This covers cases where queries run but produce wrong results, or unexpected errors occur.

---

## Basic (1~8): JOIN and Table Alias Errors

### Problem 1

Find and fix the error in the following query.

```sql
SELECT name, order_number, total_amount
FROM customers
INNER JOIN orders ON customer_id = id;
```

??? tip "Hint"
    Both tables have an `id` column. `customer_id = id` is ambiguous as to which table's `id` is referenced.

??? success "Answer"
    **Error:** Column ownership is ambiguous in the JOIN condition. It's not specified which table `customer_id` and `id` belong to.

    **Fix:**

    ```sql
    SELECT c.name, o.order_number, o.total_amount
    FROM customers AS c
    INNER JOIN orders AS o ON o.customer_id = c.id;
    ```

---

### Problem 2

Find and fix the error in the following query.

```sql
SELECT c.name, o.order_number, oi.quantity
FROM customers AS c
INNER JOIN order_items AS oi ON o.id = oi.order_id
INNER JOIN orders AS o ON c.id = o.customer_id
LIMIT 10;
```

??? tip "Hint"
    In SQL, table aliases are defined in the order they appear in `FROM`/`JOIN` clauses. `o` must be defined before use.

??? success "Answer"
    **Error:** `orders AS o` is defined in the second JOIN, but `o.id` is already referenced in the first JOIN. The alias doesn't exist yet.

    **Fix:**

    ```sql
    SELECT c.name, o.order_number, oi.quantity
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    LIMIT 10;
    ```

---

### Problem 3

Find and fix the error in the following query. The intent was to include customers without orders.

```sql
SELECT c.name, COUNT(o.id) AS order_count
FROM customers AS c
INNER JOIN orders AS o ON c.id = o.customer_id
GROUP BY c.id, c.name
ORDER BY order_count DESC;
```

??? tip "Hint"
    INNER JOIN returns only rows with matches on both sides. Which JOIN should you use to include customers without orders?

??? success "Answer"
    **Error:** `INNER JOIN` returns only customers with orders. Customers without orders are excluded from the result.

    **Fix:**

    ```sql
    SELECT c.name, COUNT(o.id) AS order_count
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name
    ORDER BY order_count ASC
    LIMIT 20;
    ```

---

### Problem 4

Find and fix the error in the following query.

```sql
SELECT p.name, cat.name, s.company_name
FROM products AS p
INNER JOIN categories AS cat ON p.id = cat.id
INNER JOIN suppliers AS s ON p.supplier_id = s.id
LIMIT 10;
```

??? tip "Hint"
    Check if `p.id = cat.id` is the correct FK column connecting `products` and `categories`. What column represents the relationship?

??? success "Answer"
    **Error:** The JOIN condition is wrong. `p.id = cat.id` compares product ID with category ID, which is not a FK relationship. `products.category_id` references `categories.id`.

    **Fix:**

    ```sql
    SELECT p.name, cat.name, s.company_name
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    LIMIT 10;
    ```

---

### Problem 5

Find and fix the error in the following query. Find product count per supplier.

```sql
SELECT company_name, COUNT(*) AS product_count
FROM products AS p
INNER JOIN suppliers AS s ON p.supplier_id = s.id
GROUP BY s.id;
```

??? tip "Hint"
    `SELECT` contains columns not in `GROUP BY`. This may work in SQLite but errors in other DBs.

??? success "Answer"
    **Error:** `SELECT` has `company_name` but `GROUP BY` only has `s.id`. The table for `company_name` is also not specified.

    **Fix:**

    ```sql
    SELECT s.company_name, COUNT(*) AS product_count
    FROM products AS p
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    GROUP BY s.id, s.company_name;
    ```

---

### Problem 6

Find and fix the error in the following query. Find the most recent order date per customer.

```sql
SELECT c.name, c.email, o.ordered_at AS last_order
FROM customers AS c
INNER JOIN orders AS o ON c.id = o.customer_id
WHERE o.ordered_at = MAX(o.ordered_at)
GROUP BY c.id;
```

??? tip "Hint"
    `WHERE` 절에서는 Aggregation 함수(`MAX`, `SUM` 등)를 사용할 수 없습니다. Aggregation 결과로 필터링하려면 다른 방법을 써야 합니다.

??? success "Answer"
    **Error:** `WHERE`에서 `MAX()`를 직접 사용할 수 없습니다. 또한 고객별 최근 주문을 구하려면 Subqueries나 GROUP BY 후 MAX를 사용해야 합니다.

    **Fix:**

    ```sql
    SELECT c.name, c.email, MAX(o.ordered_at) AS last_order
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.email;
    ```

---

### Problem 7

Find and fix the error in the following query. Intent is to show only products with reviews.

```sql
SELECT p.name, p.price, r.rating
FROM products AS p, reviews AS r
WHERE p.id = r.product_id
  AND p.price > 100000
ORDER BY p.price DESC
LIMIT 10;
```

??? tip "Hint"
    The query works, but products with multiple reviews appear multiple times. What if you want one result per product?

??? success "Answer"
    **Error:** Uses implicit JOIN (comma-separated), and products with multiple reviews repeat.

    **Fix:**

    ```sql
    -- 방법 1: 명시적 JOIN + Aggregation
    SELECT p.name, p.price, ROUND(AVG(r.rating), 1) AS avg_rating
    FROM products AS p
    INNER JOIN reviews AS r ON p.id = r.product_id
    WHERE p.price > 100000
    GROUP BY p.id, p.name, p.price
    ORDER BY p.price DESC
    LIMIT 10;

    -- Approach 2: EXISTS to check existence only
    SELECT p.name, p.price
    FROM products AS p
    WHERE p.price > 100000
      AND EXISTS (SELECT 1 FROM reviews WHERE product_id = p.id)
    ORDER BY p.price DESC
    LIMIT 10;
    ```

---

### Problem 8

Find and fix the error in the following query. Find customer names for orders in transit.

```sql
SELECT c.name, o.order_number, sh.tracking_number
FROM customers AS c
LEFT JOIN orders AS o ON c.id = o.customer_id
LEFT JOIN shipping AS sh ON o.id = sh.order_id
WHERE sh.status = 'shipped';
```

??? tip "Hint"
    Filtering on right-table columns in `WHERE` after `LEFT JOIN` removes NULL rows, effectively making it an INNER JOIN.

??? success "Answer"
    **Error:** If only orders in transit are needed, LEFT JOIN is unnecessary. If the intent was to include customers without orders, the WHERE condition negates that intent.

    **Fix:**

    ```sql
    -- Only need customers with in-transit orders, so INNER JOIN is appropriate
    SELECT c.name, o.order_number, sh.tracking_number
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    INNER JOIN shipping AS sh ON o.id = sh.order_id
    WHERE sh.status = 'shipped';
    ```

---

## Applied (9~16): 카디널리티, Aggregation, Subqueries, 날짜

### Problem 9

Find and fix the error in the following query. Find revenue and average rating per product. However, revenue is much larger than expected.

```sql
SELECT
    p.name,
    SUM(oi.quantity * oi.unit_price) AS revenue,
    ROUND(AVG(r.rating), 1) AS avg_rating
FROM products AS p
INNER JOIN order_items AS oi ON p.id = oi.product_id
INNER JOIN reviews AS r ON p.id = r.product_id
GROUP BY p.id, p.name
ORDER BY revenue DESC
LIMIT 10;
```

??? tip "Hint"
    JOINing `order_items` and `reviews` simultaneously multiplies rows (cardinality explosion). 3 orders x 2 reviews = 6 rows.

??? success "Answer"
    **Error:** JOINing two 1:N relationships simultaneously produces M x N rows, inflating revenue.

    **Fix:**

    ```sql
    SELECT
        p.name,
        SUM(oi.quantity * oi.unit_price) AS revenue,
        sub_r.avg_rating
    FROM products AS p
    INNER JOIN order_items AS oi ON p.id = oi.product_id
    LEFT JOIN (
        SELECT product_id, ROUND(AVG(rating), 1) AS avg_rating
        FROM reviews
        GROUP BY product_id
    ) AS sub_r ON p.id = sub_r.product_id
    GROUP BY p.id, p.name, sub_r.avg_rating
    ORDER BY revenue DESC
    LIMIT 10;
    ```

---

### Problem 10

Find and fix the error in the following query. Intent is to show only customers with total orders >= 1,000,000 won.

```sql
SELECT c.name, SUM(o.total_amount) AS total_spent
FROM customers AS c
INNER JOIN orders AS o ON c.id = o.customer_id
WHERE SUM(o.total_amount) >= 1000000
GROUP BY c.id, c.name;
```

??? tip "Hint"
    `WHERE` 절에서는 Aggregation 함수를 사용할 수 없습니다. 그룹화 후 필터링에 쓰는 절은 무엇인가요?

??? success "Answer"
    **Error:** `WHERE`에서 `SUM()`을 사용했습니다. Aggregation 결과 필터링은 `HAVING`에서 해야 합니다.

    **Fix:**

    ```sql
    SELECT c.name, SUM(o.total_amount) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name
    HAVING SUM(o.total_amount) >= 1000000
    ORDER BY total_spent DESC;
    ```

---

### Problem 11

Find and fix the error in the following query. Find products more expensive than their category average.

```sql
SELECT p.name, p.price
FROM products AS p
WHERE p.price > (
    SELECT AVG(price)
    FROM products
    GROUP BY category_id
);
```

??? tip "Hint"
    `>` 연산자는 단일 값과만 비교할 수 있습니다. Subqueries가 `GROUP BY`로 여러 행을 반환하면 에러가 납니다.

??? success "Answer"
    **Error:** Subqueries가 카테고리별 평균 여러 행을 반환하므로 `>` 비교가 불가능합니다. 상관 Subqueries로 자기 카테고리의 평균만 구해야 합니다.

    **Fix:**

    ```sql
    SELECT p.name, p.price
    FROM products AS p
    WHERE p.price > (
        SELECT AVG(p2.price)
        FROM products AS p2
        WHERE p2.category_id = p.category_id
    )
    ORDER BY p.price DESC;
    ```

---

### Problem 12

Find and fix the error in the following query. Find Q3 2024 (Jul~Sep) order count. Returns fewer than expected.

```sql
SELECT COUNT(*) AS q3_orders
FROM orders
WHERE ordered_at BETWEEN '2024-07-01' AND '2024-09-30';
```

??? tip "Hint"
    If `ordered_at` includes time info, `'2024-09-30'` equals `'2024-09-30 00:00:00'`. Afternoon orders on Sep 30 are missed.

??? success "Answer"
    **Error:** `BETWEEN` end value `'2024-09-30'` (= 00:00:00) misses orders after 00:00:00 on Sep 30.

    **Fix:**

    ```sql
    -- Approach 1: Include time end in the end value
    SELECT COUNT(*) AS q3_orders
    FROM orders
    WHERE ordered_at BETWEEN '2024-07-01' AND '2024-09-30 23:59:59';

    -- Approach 2: Month pattern matching with LIKE (safer)
    SELECT COUNT(*) AS q3_orders
    FROM orders
    WHERE ordered_at >= '2024-07-01'
      AND ordered_at < '2024-10-01';
    ```

---

### Problem 13

Find and fix the error in the following query. Calculate elapsed days from order date. Result is NULL.

```sql
SELECT
    order_number,
    ordered_at,
    DATEDIFF('2025-01-01', ordered_at) AS days_elapsed
FROM orders
LIMIT 10;
```

??? tip "Hint"
    SQLite has no `DATEDIFF` function. What function calculates date differences in SQLite?

??? success "Answer"
    **Error:** `DATEDIFF` is a MySQL function. SQLite uses `JULIANDAY()` to calculate date differences.

    **Fix:**

    ```sql
    SELECT
        order_number,
        ordered_at,
        CAST(JULIANDAY('2025-01-01') - JULIANDAY(ordered_at) AS INTEGER) AS days_elapsed
    FROM orders
    LIMIT 10;
    ```

---

### Problem 14

Find and fix the error in the following query. Find monthly new customer count. Errors occur.

```sql
SELECT
    STRFTIME('%Y-%m', created_at) AS month,
    COUNT(*) AS new_customers
FROM customers
GROUP BY month
HAVING new_customers > 100
ORDER BY month;
```

??? tip "Hint"
    `HAVING`에서 SELECT aliases을 사용할 수 있는 DB와 없는 DB가 있습니다. SQLite에서는 동작하지만, 표준 SQL에서는 Aggregation 표현식을 직접 써야 합니다. 이 쿼리의 진짜 문제를 찾아보세요.

??? success "Answer"
    **Error:** This query actually works in SQLite. However, `HAVING COUNT(*) > 100` is standard SQL instead of `HAVING new_customers > 100`. If errors occur, it may be due to `STRFTIME` case sensitivity (`strftime`) or date format issues.

    **Fix:**

    ```sql
    SELECT
        STRFTIME('%Y-%m', created_at) AS month,
        COUNT(*) AS new_customers
    FROM customers
    GROUP BY STRFTIME('%Y-%m', created_at)
    HAVING COUNT(*) > 100
    ORDER BY month;
    ```

---

### Problem 15

Find and fix the error in the following query. Find the top 10% most expensive products.

```sql
SELECT name, price
FROM products
WHERE price > (SELECT AVG(price) * 1.1 FROM products)
ORDER BY price DESC;
```

??? tip "Hint"
    "Top 10%" is not "110% of average". Top 10% means products in the top 10th percentile by price rank.

??? success "Answer"
    **Error:** `AVG(price) * 1.1` is "110% of average price", not "top 10% price". Top 10% means at or above the 90th percentile.

    **Fix:**

    ```sql
    -- 전체 상품 중 상위 10%
    SELECT name, price
    FROM products
    WHERE price >= (
        SELECT price FROM products
        ORDER BY price DESC
        LIMIT 1 OFFSET (SELECT COUNT(*) / 10 FROM products)
    )
    ORDER BY price DESC;
    ```

---

### Problem 16

Find and fix the error in the following query. Find categories with average review rating >= 4.0.

```sql
SELECT cat.name, AVG(r.rating) AS avg_rating
FROM categories AS cat
INNER JOIN products AS p ON cat.id = p.category_id
LEFT JOIN reviews AS r ON p.id = r.product_id
GROUP BY cat.id, cat.name
HAVING avg_rating >= 4.0
ORDER BY avg_rating DESC;
```

??? tip "Hint"
    Products without reviews have NULL `r.rating`. `AVG` ignores NULLs so results may be correct, but categories with 0 reviews get NULL `avg_rating` and are excluded from `>= 4.0` comparison. Verify this is intended.

??? success "Answer"
    **Error:** Two logical issues: (1) Categories without reviews have NULL AVG and are auto-excluded — this may be intended. (2) `HAVING avg_rating` works in SQLite but standard SQL requires `HAVING AVG(r.rating)`. Also, categories with very few reviews could reach 4.0+, so adding a minimum review count condition is advisable.

    **Fix:**

    ```sql
    SELECT cat.name,
           ROUND(AVG(r.rating), 2) AS avg_rating,
           COUNT(r.id) AS review_count
    FROM categories AS cat
    INNER JOIN products AS p ON cat.id = p.category_id
    INNER JOIN reviews AS r ON p.id = r.product_id
    GROUP BY cat.id, cat.name
    HAVING AVG(r.rating) >= 4.0
       AND COUNT(r.id) >= 10
    ORDER BY avg_rating DESC;
    ```

---

## Advanced (17~25): UNION, NULL, DML, Complex Diagnostics

### Problem 17

Find and fix the error in the following query. Combine order events and payment events into one.

```sql
SELECT order_number, total_amount, status, ordered_at
FROM orders
UNION ALL
SELECT order_id, amount, status, paid_at
FROM payments;
```

??? tip "Hint"
    `UNION ALL` requires compatible column count and types. Does combining `order_number` (TEXT) and `order_id` (INTEGER) make semantic sense?

??? success "Answer"
    **Error:** Column semantics mismatch. `order_number` is text and `order_id` is integer. Also, the two `status` columns have different value domains (order status vs payment status).

    **Fix:**

    ```sql
    SELECT '주문' AS event_type,
           order_number AS reference,
           total_amount AS amount,
           status,
           ordered_at AS event_at
    FROM orders
    UNION ALL
    SELECT '결제' AS event_type,
           CAST(order_id AS TEXT) AS reference,
           amount,
           status,
           paid_at AS event_at
    FROM payments
    WHERE paid_at IS NOT NULL
    ORDER BY event_at DESC
    LIMIT 20;
    ```

---

### Problem 18

Find and fix the error in the following query. LEFT JOIN was used to include products without reviews, but adding a review count condition caused reviewless products to disappear.

```sql
SELECT p.name, p.price, COUNT(r.id) AS review_count
FROM products AS p
LEFT JOIN reviews AS r ON p.id = r.product_id
WHERE r.rating >= 3 OR r.rating IS NULL
GROUP BY p.id, p.name, p.price
HAVING review_count <= 5
ORDER BY p.price DESC;
```

??? tip "Hint"
    `WHERE r.rating >= 3` removes LEFT JOIN NULL rows. `OR r.rating IS NULL` tries to recover but excludes reviews with rating < 3. Reconsider condition placement.

??? success "Answer"
    **Error:** Filtering right-table columns in WHERE damages the LEFT JOIN effect. To count only 3+ rated reviews while including all products, move the condition to the ON clause.

    **Fix:**

    ```sql
    SELECT p.name, p.price, COUNT(r.id) AS review_count
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id AND r.rating >= 3
    GROUP BY p.id, p.name, p.price
    HAVING COUNT(r.id) <= 5
    ORDER BY p.price DESC
    LIMIT 20;
    ```

---

### Problem 19

Find and fix the error in the following query. GROUP BY와 비Aggregation 칼럼이 섞여 있습니다.

```sql
SELECT
    c.name,
    c.email,
    c.grade,
    COUNT(o.id) AS order_count,
    SUM(o.total_amount) AS total_spent
FROM customers AS c
INNER JOIN orders AS o ON c.id = o.customer_id
GROUP BY c.name;
```

??? tip "Hint"
    `GROUP BY c.name` only, but `SELECT` has `c.email`, `c.grade`. With same-name customers, which email/grade is displayed?

??? success "Answer"
    **Error:** With only `c.name` in `GROUP BY`, `email` and `grade` for same-name customers are non-deterministic. Group by `c.id` which uniquely identifies customers.

    **Fix:**

    ```sql
    SELECT
        c.name,
        c.email,
        c.grade,
        COUNT(o.id) AS order_count,
        SUM(o.total_amount) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.id, c.name, c.email, c.grade
    ORDER BY total_spent DESC
    LIMIT 20;
    ```

---

### Problem 20

Find and fix the error in the following query. Attempting to insert a new product.

```sql
INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, created_at, updated_at)
VALUES (1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000);
```

??? tip "Hint"
    Count the VALUES and column list entries one by one.

??? success "Answer"
    **Error:** 9 columns (`category_id` ~ `updated_at`) but only 7 VALUES. `created_at` and `updated_at` values are missing.

    **Fix:**

    ```sql
    INSERT INTO products (category_id, supplier_id, name, sku, brand, price, cost_price, stock_qty, is_active, created_at, updated_at)
    VALUES (1, 1, '테스트 키보드', 'TEST-KB-001', 'TestBrand', 89000, 45000, 100, 1, '2025-01-01', '2025-01-01');
    ```

---

### Problem 21

Find and fix the error in the following query. Find monthly revenue excluding cancelled orders.

```sql
SELECT
    SUBSTR(ordered_at, 1, 7) AS month,
    SUM(total_amount) AS revenue,
    COUNT(*) AS order_count
FROM orders
WHERE status != 'cancelled'
GROUP BY SUBSTR(ordered_at, 1, 7)
ORDER BY month;
```

??? tip "Hint"
    `!= 'cancelled'` only excludes cancellations, but should returns (`returned`, `return_requested`) also be excluded from revenue?

??? success "Answer"
    **Error:** Excluding only `cancelled` includes `returned` and `return_requested` orders in revenue. All statuses not counted as actual revenue should be excluded.

    **Fix:**

    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        SUM(total_amount) AS revenue,
        COUNT(*) AS order_count
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```

---

### Problem 22

Find and fix the error in the following query. Finding revenue by payment method, but totals differ from order totals.

```sql
SELECT
    p.method,
    COUNT(*) AS payment_count,
    SUM(p.amount) AS total_amount
FROM payments AS p
GROUP BY p.method
ORDER BY total_amount DESC;
```

??? tip "Hint"
    Check payment `status`. Are failed or refunded payments included?

??? success "Answer"
    **Error:** Records with `failed` or `refunded` status are included, causing discrepancy with actual revenue.

    **Fix:**

    ```sql
    SELECT
        p.method,
        COUNT(*) AS payment_count,
        SUM(p.amount) AS total_amount
    FROM payments AS p
    WHERE p.status = 'completed'
    GROUP BY p.method
    ORDER BY total_amount DESC;
    ```

---

### Problem 23

Find and fix the error in the following query. Find dormant VIP customers with no orders in the last 6 months.

```sql
SELECT c.name, c.email, c.grade
FROM customers AS c
WHERE c.grade = 'VIP'
  AND c.id NOT IN (
      SELECT customer_id
      FROM orders
      WHERE ordered_at >= DATE('now', '-6 months')
  );
```

??? tip "Hint"
    `NOT IN` Subqueries의 결과에 NULL이 포함되면 전체 결과가 빈 집합이 됩니다. `customer_id`가 NULL인 행이 있는지 확인하세요.

??? success "Answer"
    **Error:** `NOT IN` Subqueries에서 `customer_id`가 NULL인 주문이 하나라도 있으면 결과가 0행이 됩니다. `NOT IN (1, 2, NULL)`은 항상 UNKNOWN이 되기 때문입니다.

    **Fix:**

    ```sql
    -- Approach 1: Use NOT EXISTS (NULL-safe)
    SELECT c.name, c.email, c.grade
    FROM customers AS c
    WHERE c.grade = 'VIP'
      AND NOT EXISTS (
          SELECT 1 FROM orders AS o
          WHERE o.customer_id = c.id
            AND o.ordered_at >= DATE('now', '-6 months')
      );

    -- Approach 2: Exclude NULL from NOT IN
    SELECT c.name, c.email, c.grade
    FROM customers AS c
    WHERE c.grade = 'VIP'
      AND c.id NOT IN (
          SELECT customer_id
          FROM orders
          WHERE ordered_at >= DATE('now', '-6 months')
            AND customer_id IS NOT NULL
      );
    ```

---

### Problem 24

Find and fix the error in the following query. Calculate return rate per supplier. Some suppliers cause errors.

```sql
SELECT
    s.company_name,
    COUNT(DISTINCT oi.id) AS total_sales,
    COUNT(DISTINCT ret.id) AS return_count,
    ROUND(100.0 * COUNT(DISTINCT ret.id) / COUNT(DISTINCT oi.id), 2) AS return_rate
FROM suppliers AS s
LEFT JOIN products AS p ON s.id = p.supplier_id
LEFT JOIN order_items AS oi ON p.id = oi.product_id
LEFT JOIN returns AS ret ON ret.order_id = oi.order_id
GROUP BY s.id, s.company_name
ORDER BY return_rate DESC;
```

??? tip "Hint"
    Suppliers with 0 sales have `COUNT(DISTINCT oi.id)` = 0. Dividing by 0 causes an error.

??? success "Answer"
    **Error:** Division by zero error for suppliers with `total_sales` = 0. Use `NULLIF` to convert 0 denominator to NULL.

    **Fix:**

    ```sql
    SELECT
        s.company_name,
        COUNT(DISTINCT oi.id) AS total_sales,
        COUNT(DISTINCT ret.id) AS return_count,
        ROUND(100.0 * COUNT(DISTINCT ret.id)
            / NULLIF(COUNT(DISTINCT oi.id), 0), 2) AS return_rate
    FROM suppliers AS s
    LEFT JOIN products AS p ON s.id = p.supplier_id
    LEFT JOIN order_items AS oi ON p.id = oi.product_id
    LEFT JOIN returns AS ret ON ret.order_id = oi.order_id
    GROUP BY s.id, s.company_name
    ORDER BY return_rate DESC;
    ```

---

### Problem 25

Find and fix the error in the following query. Create a report of avg order amount, order count, and review rating per customer grade. Order amounts are abnormally large.

```sql
SELECT
    c.grade,
    COUNT(o.id) AS order_count,
    ROUND(AVG(o.total_amount), 0) AS avg_order_amount,
    ROUND(AVG(r.rating), 2) AS avg_rating,
    COUNT(r.id) AS review_count
FROM customers AS c
INNER JOIN orders AS o ON c.id = o.customer_id
INNER JOIN order_items AS oi ON o.id = oi.order_id
LEFT JOIN reviews AS r ON c.id = r.customer_id
GROUP BY c.grade
ORDER BY avg_order_amount DESC;
```

??? tip "Hint"
    JOINing `orders` → `order_items` duplicates each order by item count. Adding `reviews` causes row explosion. `COUNT(o.id)` becomes much larger than actual order count.

??? success "Answer"
    **Error:** 세 가지 문제가 있습니다. (1) `order_items` JOIN으로 주문 행이 아이템 수만큼 복제 (2) `reviews` JOIN으로 추가 카디널리티 폭발 (3) `COUNT(o.id)`가 주문 수가 아닌 복제된 행 수를 셉니다. 각 Aggregation를 Subqueries로 분리해야 합니다.

    **Fix:**

    ```sql
    SELECT
        c.grade,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(SUM(o.total_amount) * 1.0 / NULLIF(COUNT(DISTINCT o.id), 0), 0) AS avg_order_amount,
        sub_r.avg_rating,
        sub_r.review_count
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    LEFT JOIN (
        SELECT customer_id,
               ROUND(AVG(rating), 2) AS avg_rating,
               COUNT(*) AS review_count
        FROM reviews
        GROUP BY customer_id
    ) AS sub_r ON c.id = sub_r.customer_id
    GROUP BY c.grade, sub_r.avg_rating, sub_r.review_count
    ORDER BY avg_order_amount DESC;
    ```

    Or fully separated by grade:

    ```sql
    SELECT
        c.grade,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(AVG(DISTINCT o.total_amount), 0) AS avg_order_amount,
        (SELECT ROUND(AVG(r.rating), 2)
         FROM reviews AS r
         INNER JOIN customers AS c2 ON r.customer_id = c2.id
         WHERE c2.grade = c.grade) AS avg_rating
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    GROUP BY c.grade
    ORDER BY avg_order_amount DESC;
    ```
