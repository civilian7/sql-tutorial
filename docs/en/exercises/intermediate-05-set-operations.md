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

    `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT`, `set operations with JOIN/GROUP BY`



### 1. Combine customers who wrote reviews and customers who filed 


Combine customers who wrote reviews and customers who filed complaints into a single deduplicated list. Sort by name, top 20.


**Hint 1:** `SELECT customer_id FROM reviews UNION SELECT customer_id FROM complaints` — customers present in both appear only once.


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


    **Result** (top 7 of 20 rows)

    | name | email |
    |---|---|
    | Aaron Carr | user900@testmail.kr |
    | Aaron Cooper | user3587@testmail.kr |
    | Aaron Cortez | user1804@testmail.kr |
    | Aaron Fuller | user2520@testmail.kr |
    | Aaron Gillespie | user3365@testmail.kr |
    | Aaron Green | user417@testmail.kr |
    | Aaron Grimes | user347@testmail.kr |


---


### 2. Combine review author IDs and complaint author IDs including


Combine review author IDs and complaint author IDs including duplicates, and count the total.


**Hint 1:** Combine with `UNION ALL` then use `COUNT(*)` to get the total. Comparing with UNION shows the difference.


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_with_dup
    FROM (
        SELECT customer_id FROM reviews
        UNION ALL
        SELECT customer_id FROM complaints
    );
    ```


    **Result** (1 rows)

    | total_with_dup |
    |---|
    | 12,359 |


---


### 3. Combine the order counts for 2024 and 2025 into a single res


Combine the order counts for 2024 and 2025 into a single result.


**Hint 1:** `SELECT '2024' AS year, COUNT(*) ... UNION ALL SELECT '2025' AS year, COUNT(*) ...` — distinguish with a literal column.


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


    **Result** (2 rows)

    | year | order_count | revenue |
    |---|---|---|
    | 2024 | 5474 | 5,346,776,711.00 |
    | 2025 | 5993 | 6,398,165,081.00 |


---


### 4. Combine wishlisted product IDs and ordered product IDs (dedu


Combine wishlisted product IDs and ordered product IDs (deduplicated) and count the total unique products.


**Hint 1:** The row count of the union equals the number of products with either interest or purchase history.


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_products
    FROM (
        SELECT product_id FROM wishlists
        UNION
        SELECT product_id FROM order_items
    );
    ```


    **Result** (1 rows)

    | total_products |
    |---|
    | 280 |


---


### 5. Combine order cancellation events and return request events 


Combine order cancellation events and return request events into a single timeline. Most recent 20.


**Hint 1:** Add a literal column to distinguish event types. ORDER BY applies to the entire result.


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


    **Result** (top 7 of 20 rows)

    | event_type | reference | event_date |
    |---|---|---|
    | 반품 | 37371 | 2026-01-08 07:26:14 |
    | 반품 | 37537 | 2026-01-07 02:35:31 |
    | 반품 | 37409 | 2026-01-05 04:25:32 |
    | 반품 | 37515 | 2026-01-05 01:26:34 |
    | 반품 | 37405 | 2026-01-02 10:13:52 |
    | 취소 | ORD-20251231-37545 | 2026-01-01 23:35:58 |
    | 취소 | ORD-20251230-37531 | 2025-12-31 08:00:28 |


---


### 6. Show 2025 monthly revenue with an annual total row appended.


Show 2025 monthly revenue with an annual total row appended.


**Hint 1:** Append a `UNION ALL` total row to the monthly `GROUP BY` result.


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
        '== 합계 ==' AS month,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2025%'
      AND status NOT IN ('cancelled')
    ORDER BY month;
    ```


    **Result** (top 7 of 13 rows)

    | month | order_count | revenue |
    |---|---|---|
    | 2025-01 | 461 | 491,947,609.00 |
    | 2025-02 | 428 | 422,980,126.00 |
    | 2025-03 | 619 | 656,638,842.00 |
    | 2025-04 | 467 | 517,070,656.00 |
    | 2025-05 | 466 | 514,287,052.00 |
    | 2025-06 | 436 | 457,780,698.00 |
    | 2025-07 | 402 | 404,813,220.00 |


---


### 7. Show payment method counts with a total row at the end.


Show payment method counts with a total row at the end.


**Hint 1:** Structure: GROUP BY result UNION ALL total row.


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
        '== 합계 ==' AS method,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS total_amount
    FROM payments
    WHERE status = 'completed'
    ORDER BY
        CASE WHEN method = '== 합계 ==' THEN 1 ELSE 0 END,
        tx_count DESC;
    ```


---


### 8. Find customers who have both written a review and filed a co


Find customers who have both written a review and filed a complaint (intersection). Sort by name, top 15.


**Hint 1:** Returns only customer IDs present in both.


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


    **Result** (top 7 of 15 rows)

    | name | email | grade |
    |---|---|---|
    | Aaron Carr | user900@testmail.kr | BRONZE |
    | Aaron Fuller | user2520@testmail.kr | SILVER |
    | Aaron Gillespie | user3365@testmail.kr | GOLD |
    | Aaron Harris | user1884@testmail.kr | SILVER |
    | Aaron Ryan | user2324@testmail.kr | GOLD |
    | Adam Johnson | user2066@testmail.kr | VIP |
    | Adam Moore | user3@testmail.kr | VIP |


---


### 9. Find products that were wishlisted but never ordered (set di


Find products that were wishlisted but never ordered (set difference). Sort by price descending, top 15.


**Hint 1:** Product IDs only in wishlists, not in orders.


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


### 10. Find customers who ordered in 2024 but not in 2025. Sort by 


Find customers who ordered in 2024 but not in 2025. Sort by name, top 20.


**Hint 1:** Subtract 2025 customers from 2024 customers.


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


    **Result** (top 7 of 20 rows)

    | name | grade | email |
    |---|---|---|
    | Aaron Grimes | BRONZE | user347@testmail.kr |
    | Adam Martin | BRONZE | user2247@testmail.kr |
    | Adam Mcdaniel | BRONZE | user3712@testmail.kr |
    | Adam Ponce | BRONZE | user1506@testmail.kr |
    | Alan Hill | BRONZE | user3087@testmail.kr |
    | Alan Thompson | BRONZE | user1955@testmail.kr |
    | Alec Miranda Jr. | BRONZE | user3251@testmail.kr |


---


### 11. Combine customer activity counts into a single report (order


Combine customer activity counts into a single report (orders, reviews, complaints, wishlists).


**Hint 1:** Column names and types must match across each SELECT.


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


    **Result** (4 rows)

    | activity_type | total_count |
    |---|---|
    | 주문 | 35,698 |
    | 리뷰 | 8546 |
    | 불만 접수 | 3813 |
    | 위시리스트 | 1998 |


---


### 12. Find loyal customers who ordered in both 2024 and 2025, show


Find loyal customers who ordered in both 2024 and 2025, showing name, grade, and order counts for each year. Top 15.


**Hint 1:** First use INTERSECT to get customer IDs who ordered in both years, then add yearly order counts as SELECT clause scalar subqueries.


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


    **Result** (top 7 of 15 rows)

    | name | grade | orders_2024 | orders_2025 |
    |---|---|---|---|
    | Allen Snyder | VIP | 16 | 24 |
    | Dylan Green | VIP | 15 | 22 |
    | Charles Patterson | VIP | 21 | 21 |
    | Stephanie Berry | VIP | 19 | 21 |
    | Sandra Deleon | VIP | 14 | 21 |
    | Richard Woods | VIP | 5 | 20 |
    | Mrs. Tara Miller DDS | VIP | 17 | 18 |


---


### 13. Find orders that received complaints but were not returned. 


Find orders that received complaints but were not returned. Show order number and amount. Most recent 15.


**Hint 1:** Orders with complaints but no returns.


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


    **Result** (top 7 of 15 rows)

    | order_number | total_amount | ordered_at |
    |---|---|---|
    | ORD-20251231-37548 | 187,700.00 | 2025-12-31 18:43:56 |
    | ORD-20251231-37541 | 900,900.00 | 2025-12-31 09:27:26 |
    | ORD-20251230-37523 | 419,600.00 | 2025-12-30 18:22:10 |
    | ORD-20251229-37498 | 1,785,500.00 | 2025-12-29 15:06:38 |
    | ORD-20251228-37479 | 1,758,716.00 | 2025-12-28 22:03:50 |
    | ORD-20251228-37483 | 116,700.00 | 2025-12-28 21:32:28 |
    | ORD-20251228-37467 | 52,600.00 | 2025-12-28 15:56:10 |


---


### 14. Compute per-product "review count + wishlist count" using a 


Compute per-product "review count + wishlist count" using a UNION ALL subquery. Top 10.


**Hint 1:** After combining, `GROUP BY product_id` count gives the combined interest score.


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


    **Result** (top 7 of 10 rows)

    | name | interest_score |
    |---|---|
    | SteelSeries Prime Wireless Silver | 112 |
    | Kingston FURY Beast DDR4 16GB Silver | 110 |
    | SteelSeries Aerox 5 Wireless Silver | 110 |
    | Logitech G502 X PLUS | 102 |
    | Samsung SPA-KFG0BUB Silver | 95 |
    | Ducky One 3 TKL White | 94 |
    | Crucial T700 2TB Silver | 90 |


---


### 15. Compute quarterly new signups and ordering customers for 202


Compute quarterly new signups and ordering customers for 2024, combined into one report.


**Hint 1:** Use a metric column to distinguish indicators.


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


    **Result** (top 7 of 8 rows)

    | quarter | metric | value |
    |---|---|---|
    | Q1 | 신규가입 | 171 |
    | Q1 | 주문고객 | 767 |
    | Q2 | 신규가입 | 164 |
    | Q2 | 주문고객 | 766 |
    | Q3 | 신규가입 | 176 |
    | Q3 | 주문고객 | 813 |
    | Q4 | 신규가입 | 189 |


---
