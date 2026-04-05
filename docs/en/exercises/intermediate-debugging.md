# Intermediate Exercise: SQL Debugging

You are given incorrect queries. **Find and fix the bugs.** These are the most common mistakes made in real-world development.

---

### 1. Revenue Inflated by 2x

The query below calculates revenue by product for 2024. However, the revenue comes out much larger than expected. Why?

```sql
-- 버그가 있는 쿼리
SELECT
    p.name,
    SUM(oi.quantity * oi.unit_price) AS revenue,
    AVG(r.rating) AS avg_rating
FROM products AS p
INNER JOIN order_items AS oi ON p.id = oi.product_id
INNER JOIN orders AS o ON oi.order_id = o.id
INNER JOIN reviews AS r ON p.id = r.product_id
WHERE o.ordered_at LIKE '2024%'
GROUP BY p.id, p.name;
```

??? success "Answer"
    **Cause:** Joining `reviews` and `order_items` simultaneously causes row multiplication (3 reviews x 5 orders = 15 rows).

    ```sql
    -- 수정: 리뷰를 서브쿼리로 분리
    SELECT
        p.name,
        SUM(oi.quantity * oi.unit_price) AS revenue,
        review.avg_rating
    FROM products AS p
    INNER JOIN order_items AS oi ON p.id = oi.product_id
    INNER JOIN orders AS o ON oi.order_id = o.id
    LEFT JOIN (
        SELECT product_id, ROUND(AVG(rating), 2) AS avg_rating
        FROM reviews GROUP BY product_id
    ) AS review ON p.id = review.product_id
    WHERE o.ordered_at LIKE '2024%'
    GROUP BY p.id, p.name, review.avg_rating;
    ```

---

### 2. Comparing with NULL

The query below tries to find customers without a birth date. It returns 0 rows. Why?

```sql
-- 버그가 있는 쿼리
SELECT name, email
FROM customers
WHERE birth_date = NULL;
```

??? success "Answer"
    **Cause:** NULL cannot be compared with `=`. Even `NULL = NULL` evaluates to FALSE.

    ```sql
    -- 수정: IS NULL 사용
    SELECT name, email
    FROM customers
    WHERE birth_date IS NULL;
    ```

---

### 3. LEFT JOIN Behaving Like INNER JOIN

LEFT JOIN was used to include products without reviews, but products without reviews are missing from the results.

```sql
-- 버그가 있는 쿼리
SELECT p.name, p.price, r.rating
FROM products AS p
LEFT JOIN reviews AS r ON p.id = r.product_id
WHERE r.rating >= 3;
```

??? success "Answer"
    **Cause:** `WHERE r.rating >= 3` eliminates NULL rows. The LEFT JOIN effectively becomes an INNER JOIN.

    ```sql
    -- 수정: 조건을 ON 절로 이동
    SELECT p.name, p.price, r.rating
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id AND r.rating >= 3;
    ```

---

### 4. Missing GROUP BY

The query below tries to count products per category. It throws an error.

```sql
-- 버그가 있는 쿼리
SELECT cat.name, COUNT(*) AS product_count
FROM products AS p
INNER JOIN categories AS cat ON p.category_id = cat.id;
```

??? success "Answer"
    **Cause:** An aggregate function (COUNT) is used without GROUP BY.

    ```sql
    -- 수정: GROUP BY 추가
    SELECT cat.name, COUNT(*) AS product_count
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    GROUP BY cat.name;
    ```

---

### 5. Confusing HAVING and WHERE

The goal is to show only categories that have 5 or more products priced at 100,000 or above. It throws an error.

```sql
-- 버그가 있는 쿼리
SELECT cat.name, COUNT(*) AS expensive_count
FROM products AS p
INNER JOIN categories AS cat ON p.category_id = cat.id
HAVING p.price >= 100000 AND COUNT(*) >= 5
GROUP BY cat.name;
```

??? success "Answer"
    **Cause:** 1) Row-level filters belong in WHERE, group-level filters in HAVING. 2) HAVING must come after GROUP BY.

    ```sql
    -- 수정
    SELECT cat.name, COUNT(*) AS expensive_count
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE p.price >= 100000
    GROUP BY cat.name
    HAVING COUNT(*) >= 5;
    ```

---

### 6. When DISTINCT Is Needed

Counting the number of categories each customer purchased from. The counts are abnormally large.

```sql
-- 버그가 있는 쿼리
SELECT
    c.name,
    COUNT(p.category_id) AS category_count
FROM customers AS c
INNER JOIN orders AS o ON c.id = o.customer_id
INNER JOIN order_items AS oi ON o.id = oi.order_id
INNER JOIN products AS p ON oi.product_id = p.id
GROUP BY c.id, c.name
ORDER BY category_count DESC
LIMIT 10;
```

??? success "Answer"
    **Cause:** Buying multiple products from the same category results in duplicate counts.

    ```sql
    -- 수정: COUNT(DISTINCT ...)
    SELECT
        c.name,
        COUNT(DISTINCT p.category_id) AS category_count
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN products AS p ON oi.product_id = p.id
    GROUP BY c.id, c.name
    ORDER BY category_count DESC
    LIMIT 10;
    ```

---

### 7. Subquery Returns Multiple Rows

Trying to find products more expensive than the category average. It throws an error.

```sql
-- 버그가 있는 쿼리
SELECT name, price
FROM products
WHERE price > (
    SELECT AVG(price) FROM products GROUP BY category_id
);
```

??? success "Answer"
    **Cause:** The subquery returns multiple rows (one per category), but `>` can only compare against a single value.

    ```sql
    -- 수정 방법 1: 전체 평균과 비교
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products);

    -- 수정 방법 2: 자기 카테고리 평균과 비교 (상관 서브쿼리)
    SELECT p.name, p.price
    FROM products AS p
    WHERE p.price > (
        SELECT AVG(p2.price)
        FROM products AS p2
        WHERE p2.category_id = p.category_id
    );
    ```

---

### 8. Missing Date Range

Trying to get December 2024 orders. Orders from December 31st are missing.

```sql
-- 버그가 있는 쿼리
SELECT COUNT(*) AS december_orders
FROM orders
WHERE ordered_at BETWEEN '2024-12-01' AND '2024-12-31';
```

??? success "Answer"
    **Cause:** If `ordered_at` includes a time component, `'2024-12-31'` equals `'2024-12-31 00:00:00'`, so any time after midnight is excluded.

    ```sql
    -- 수정: 시간 끝까지 포함
    SELECT COUNT(*) AS december_orders
    FROM orders
    WHERE ordered_at BETWEEN '2024-12-01' AND '2024-12-31 23:59:59';

    -- 또는 LIKE 사용
    SELECT COUNT(*) AS december_orders
    FROM orders
    WHERE ordered_at LIKE '2024-12%';
    ```

---

### 9. Cancelled Orders Included

A monthly revenue report includes cancelled orders in the revenue.

```sql
-- 버그가 있는 쿼리
SELECT
    SUBSTR(ordered_at, 1, 7) AS month,
    SUM(total_amount) AS revenue
FROM orders
GROUP BY SUBSTR(ordered_at, 1, 7)
ORDER BY month;
```

??? success "Answer"
    **Cause:** Cancelled and returned orders are not excluded.

    ```sql
    -- 수정: 상태 필터 추가
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        SUM(total_amount) AS revenue
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```

---

### 10. Division by Zero

Calculating the return rate. An error occurs for suppliers with zero sales.

```sql
-- 버그가 있는 쿼리
SELECT
    s.company_name,
    COUNT(DISTINCT ret.id) AS return_count,
    COUNT(DISTINCT oi.id) AS sale_count,
    100.0 * COUNT(DISTINCT ret.id) / COUNT(DISTINCT oi.id) AS return_rate
FROM suppliers AS s
LEFT JOIN products AS p ON s.id = p.supplier_id
LEFT JOIN order_items AS oi ON p.id = oi.product_id
LEFT JOIN returns AS ret ON ret.order_id = oi.order_id
GROUP BY s.id, s.company_name;
```

??? success "Answer"
    **Cause:** Division by zero error when `sale_count` is 0.

    ```sql
    -- 수정: NULLIF로 0 나누기 방지
    SELECT
        s.company_name,
        COUNT(DISTINCT ret.id) AS return_count,
        COUNT(DISTINCT oi.id) AS sale_count,
        ROUND(100.0 * COUNT(DISTINCT ret.id)
            / NULLIF(COUNT(DISTINCT oi.id), 0), 2) AS return_rate
    FROM suppliers AS s
    LEFT JOIN products AS p ON s.id = p.supplier_id
    LEFT JOIN order_items AS oi ON p.id = oi.product_id
    LEFT JOIN returns AS ret ON ret.order_id = oi.order_id
    GROUP BY s.id, s.company_name;
    ```

---

### 11. Using Alias in WHERE

Trying to count products by price tier and then filter. It throws an error.

```sql
-- 버그가 있는 쿼리
SELECT
    CASE WHEN price < 100000 THEN '저가' ELSE '고가' END AS tier,
    COUNT(*) AS cnt
FROM products
WHERE tier = '저가'
GROUP BY tier;
```

??? success "Answer"
    **Cause:** WHERE cannot reference SELECT aliases (execution order: FROM -> WHERE -> GROUP BY -> SELECT).

    ```sql
    -- 수정: 원래 표현식을 WHERE에 사용
    SELECT
        CASE WHEN price < 100000 THEN '저가' ELSE '고가' END AS tier,
        COUNT(*) AS cnt
    FROM products
    WHERE price < 100000
    GROUP BY tier;

    -- 또는 HAVING 사용 (그룹 필터)
    SELECT
        CASE WHEN price < 100000 THEN '저가' ELSE '고가' END AS tier,
        COUNT(*) AS cnt
    FROM products
    GROUP BY tier
    HAVING tier = '저가';
    ```

---

### 12. UNION Column Mismatch

Trying to combine order events and complaint events. It throws an error.

```sql
-- 버그가 있는 쿼리
SELECT order_number, total_amount, ordered_at FROM orders
UNION ALL
SELECT title, category, created_at FROM complaints;
```

??? success "Answer"
    **Cause:** Each SELECT in a UNION must have the same number of columns with compatible types. `total_amount` (REAL) and `category` (TEXT) have different semantics.

    ```sql
    -- 수정: 동일 구조로 맞추기
    SELECT '주문' AS type, order_number AS reference, ordered_at AS event_date
    FROM orders
    UNION ALL
    SELECT '문의' AS type, title AS reference, created_at AS event_date
    FROM complaints
    ORDER BY event_date DESC
    LIMIT 20;
    ```
