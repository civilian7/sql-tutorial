# Set Operations

!!! info "Tables"
    `customers` — Customers (grade, points, channel)  
    `orders` — Orders (status, amount, date)  
    `reviews` — Reviews (rating, content)  
    `complaints` — Complaints (type, priority)  
    `wishlists` — Wishlists (customer-product)  
    `order_items` — Order items (qty, unit price)  
    `products` — Products (name, price, stock, brand)  
    `payments` — Payments (method, amount, status)  
    `returns` — Returns (reason, status)  

!!! abstract "Concepts"
    `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT`, Set operations + `JOIN`/`GROUP BY`

---

### Problem 1. Combine customers who wrote reviews and customers who filed complaints into a single deduplicated list.

UNION merges two SELECT results while automatically removing duplicates.

??? tip "Hint"
    `SELECT customer_id FROM reviews UNION SELECT customer_id FROM complaints` — customers present in both appear only once.

??? success "Answer"
    ```sql
    SELECT c.name, c.email
    FROM customers AS c
    WHERE c.id IN (
        SELECT customer_id FROM reviews
        UNION
        SELECT customer_id FROM complaints
    )
    ORDER BY c.name
    LIMIT 20;
    ```

---

### Problem 2. Combine review author IDs and complaint author IDs including duplicates, and count the total.

UNION ALL does not remove duplicates, so a customer present in both sets appears twice.

??? tip "Hint"
    Combine with `UNION ALL` then use `COUNT(*)` to get the total. Comparing with UNION shows the difference in count.

??? success "Answer"
    ```sql
    -- UNION ALL: includes duplicates
    SELECT COUNT(*) AS total_with_dup
    FROM (
        SELECT customer_id FROM reviews
        UNION ALL
        SELECT customer_id FROM complaints
    );
    ```

    For comparison with `UNION` (deduplication):

    ```sql
    -- UNION: removes duplicates
    SELECT COUNT(*) AS total_without_dup
    FROM (
        SELECT customer_id FROM reviews
        UNION
        SELECT customer_id FROM complaints
    );
    ```

    The difference between the two results is "the number of customers active in both."

---

### Problem 3. Combine the order counts for 2024 and 2025 into a single result.

Write separate SELECT statements for each year's aggregation and combine with UNION ALL.

??? tip "Hint"
    `SELECT '2024' AS year, COUNT(*) ... UNION ALL SELECT '2025' AS year, COUNT(*) ...` — distinguish with a literal column.

??? success "Answer"
    ```sql
    SELECT '2024' AS year,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND status NOT IN ('cancelled')
    UNION ALL
    SELECT '2025' AS year,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2025%'
      AND status NOT IN ('cancelled');
    ```

    | year | order_count | revenue |
    |------|-------------|---------|
    | 2024 | ... | ... |
    | 2025 | ... | ... |

---

### Problem 4. Combine wishlisted product IDs and ordered product IDs (deduplicated) and count the total unique products.

UNION automatically removes duplicates when combining two sets.

??? tip "Hint"
    `SELECT product_id FROM wishlists UNION SELECT product_id FROM order_items` — the row count of the union equals the number of products with either interest or purchase history.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_products
    FROM (
        SELECT product_id FROM wishlists
        UNION
        SELECT product_id FROM order_items
    );
    ```

---

### Problem 5. Combine order cancellation events and return request events into a single timeline. Most recent 20.

Combine events from different tables using UNION ALL to create a unified timeline. Column count and types must match.

??? tip "Hint"
    Add a literal column to distinguish event types. `SELECT 'Cancellation' AS event_type, ... UNION ALL SELECT 'Return' AS event_type, ...` — ORDER BY applies to the entire result.

??? success "Answer"
    ```sql
    SELECT '취소' AS event_type,
           order_number AS reference,
           cancelled_at AS event_date
    FROM orders
    WHERE status = 'cancelled' AND cancelled_at IS NOT NULL
    UNION ALL
    SELECT '반품' AS event_type,
           CAST(order_id AS TEXT) AS reference,
           requested_at AS event_date
    FROM returns
    WHERE requested_at IS NOT NULL
    ORDER BY event_date DESC
    LIMIT 20;
    ```

    | event_type | reference | event_date |
    |------------|-----------|------------|
    | 취소 | ORD-... | 2025-... |
    | 반품 | 1234 | 2025-... |
    | ... | ... | ... |

---

### Problem 6. Show 2025 monthly revenue with an annual total row appended.

Use UNION ALL to combine monthly aggregation with an overall total into a single result.

??? tip "Hint"
    Append a `UNION ALL` total row with `'== Total =='` as the month to the monthly `GROUP BY` result.

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2025%'
      AND status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 7)
    UNION ALL
    SELECT
        '== Total ==' AS month,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2025%'
      AND status NOT IN ('cancelled')
    ORDER BY month;
    ```

---

### Problem 7. Show payment method counts with a total row at the end.

Use UNION ALL to combine GROUP BY results and a total row.

??? tip "Hint"
    `SELECT method, COUNT(*), SUM(amount) FROM payments GROUP BY method UNION ALL SELECT 'Total', COUNT(*), SUM(amount) FROM payments` structure.

??? success "Answer"
    ```sql
    SELECT
        method,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS total_amount
    FROM payments
    WHERE status = 'completed'
    GROUP BY method
    UNION ALL
    SELECT
        '== Total ==' AS method,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS total_amount
    FROM payments
    WHERE status = 'completed'
    ORDER BY
        CASE WHEN method = '== Total ==' THEN 1 ELSE 0 END,
        tx_count DESC;
    ```

---

### Problem 8. Find customers who have both written a review and filed a complaint (intersection).

INTERSECT returns the intersection of two SELECT results.

??? tip "Hint"
    `SELECT customer_id FROM reviews INTERSECT SELECT customer_id FROM complaints` — returns only customer IDs present in both.

??? success "Answer"
    ```sql
    SELECT c.name, c.email, c.grade
    FROM customers AS c
    WHERE c.id IN (
        SELECT customer_id FROM reviews
        INTERSECT
        SELECT customer_id FROM complaints
    )
    ORDER BY c.name
    LIMIT 15;
    ```

---

### Problem 9. Find products that were wishlisted but never ordered (set difference).

EXCEPT returns the difference: the first SELECT minus the second SELECT.

??? tip "Hint"
    `SELECT product_id FROM wishlists EXCEPT SELECT product_id FROM order_items` — product IDs only in wishlists, not in orders.

??? success "Answer"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    WHERE p.id IN (
        SELECT product_id FROM wishlists
        EXCEPT
        SELECT product_id FROM order_items
    )
    ORDER BY p.price DESC
    LIMIT 15;
    ```

---

### Problem 10. Find customers who ordered in 2024 but not in 2025.

Use EXCEPT to compute the set difference of customers by year. Useful for churn analysis.

??? tip "Hint"
    `SELECT customer_id FROM orders WHERE ordered_at LIKE '2024%' EXCEPT SELECT customer_id FROM orders WHERE ordered_at LIKE '2025%'` — subtract 2025 customers from 2024 customers.

??? success "Answer"
    ```sql
    SELECT c.name, c.grade, c.email
    FROM customers AS c
    WHERE c.id IN (
        SELECT customer_id
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled')
        EXCEPT
        SELECT customer_id
        FROM orders
        WHERE ordered_at LIKE '2025%'
          AND status NOT IN ('cancelled')
    )
    ORDER BY c.name
    LIMIT 20;
    ```

---

### Problem 11. Combine customer activity counts into a single report (orders, reviews, complaints, wishlists).

Use UNION ALL to merge counts from multiple activity types into one summary table.

??? tip "Hint"
    `SELECT 'Orders' AS activity, COUNT(*) FROM orders UNION ALL SELECT 'Reviews', COUNT(*) FROM reviews UNION ALL ...` — column names and types must match across each SELECT.

??? success "Answer"
    ```sql
    SELECT '주문' AS activity_type, COUNT(*) AS total_count
    FROM orders
    WHERE status NOT IN ('cancelled')
    UNION ALL
    SELECT '리뷰', COUNT(*)
    FROM reviews
    UNION ALL
    SELECT '불만 접수', COUNT(*)
    FROM complaints
    UNION ALL
    SELECT '위시리스트', COUNT(*)
    FROM wishlists
    ORDER BY total_count DESC;
    ```

    | activity_type | total_count |
    |--------------|-------------|
    | 주문 | ... |
    | 위시리스트 | ... |
    | 리뷰 | ... |
    | 불만 접수 | ... |

---

### Problem 12. Find loyal customers who ordered in both 2024 and 2025, showing name, grade, and order counts for each year.

Use INTERSECT to find loyal customers, then add per-year order counts via scalar subqueries.

??? tip "Hint"
    First use INTERSECT to get customer IDs who ordered in both years, then add yearly order counts as SELECT clause scalar subqueries.

??? success "Answer"
    ```sql
    SELECT
        c.name,
        c.grade,
        (SELECT COUNT(*) FROM orders
         WHERE customer_id = c.id
           AND ordered_at LIKE '2024%'
           AND status NOT IN ('cancelled')) AS orders_2024,
        (SELECT COUNT(*) FROM orders
         WHERE customer_id = c.id
           AND ordered_at LIKE '2025%'
           AND status NOT IN ('cancelled')) AS orders_2025
    FROM customers AS c
    WHERE c.id IN (
        SELECT customer_id FROM orders
        WHERE ordered_at LIKE '2024%' AND status NOT IN ('cancelled')
        INTERSECT
        SELECT customer_id FROM orders
        WHERE ordered_at LIKE '2025%' AND status NOT IN ('cancelled')
    )
    ORDER BY orders_2025 DESC, orders_2024 DESC
    LIMIT 15;
    ```

---

### Problem 13. Find orders that received complaints but were not returned. Show order number and amount.

Use EXCEPT to subtract return orders from complaint orders.

??? tip "Hint"
    `SELECT order_id FROM complaints WHERE order_id IS NOT NULL EXCEPT SELECT order_id FROM returns` — orders with complaints but no returns.

??? success "Answer"
    ```sql
    SELECT o.order_number, o.total_amount, o.ordered_at
    FROM orders AS o
    WHERE o.id IN (
        SELECT order_id FROM complaints WHERE order_id IS NOT NULL
        EXCEPT
        SELECT order_id FROM returns
    )
    ORDER BY o.ordered_at DESC
    LIMIT 15;
    ```

---

### Problem 14. Compute per-product "review count + wishlist count" using a UNION ALL subquery. Top 10.

Combine interest from two tables using UNION ALL, then aggregate externally.

??? tip "Hint"
    `FROM (SELECT product_id FROM reviews UNION ALL SELECT product_id FROM wishlists) AS combined` — after combining, `GROUP BY product_id` count gives the combined interest score.

??? success "Answer"
    ```sql
    SELECT
        p.name,
        COUNT(*) AS interest_score
    FROM (
        SELECT product_id FROM reviews
        UNION ALL
        SELECT product_id FROM wishlists
    ) AS combined
    INNER JOIN products AS p ON combined.product_id = p.id
    GROUP BY p.id, p.name
    ORDER BY interest_score DESC
    LIMIT 10;
    ```

    | name | interest_score |
    |------|----------------|
    | (popular product 1) | 42 |
    | ... | ... |

---

### Problem 15. Compute quarterly new signups and ordering customers for 2024, combined into one report.

Combine quarterly aggregations of different metrics using UNION ALL to create a comparison report.

??? tip "Hint"
    `SELECT quarter, 'New Signups' AS metric, COUNT(*) ... UNION ALL SELECT quarter, 'Ordering Customers' AS metric, COUNT(DISTINCT customer_id) ...` — use a metric column to distinguish indicators.

??? success "Answer"
    ```sql
    SELECT
        'Q' || ((CAST(SUBSTR(created_at, 6, 2) AS INTEGER) - 1) / 3 + 1) AS quarter,
        '신규가입' AS metric,
        COUNT(*) AS value
    FROM customers
    WHERE created_at LIKE '2024%'
    GROUP BY quarter
    UNION ALL
    SELECT
        'Q' || ((CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) - 1) / 3 + 1) AS quarter,
        '주문고객' AS metric,
        COUNT(DISTINCT customer_id) AS value
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND status NOT IN ('cancelled')
    GROUP BY quarter
    ORDER BY quarter, metric;
    ```

    | quarter | metric | value |
    |---------|--------|-------|
    | Q1 | 신규가입 | ... |
    | Q1 | 주문고객 | ... |
    | Q2 | 신규가입 | ... |
    | Q2 | 주문고객 | ... |
    | ... | ... | ... |

---
