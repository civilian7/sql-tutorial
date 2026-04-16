# SQL Debugging

!!! info "Tables"

    `categories` — Categories (parent-child hierarchy)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `reviews` — Reviews (rating, content)  

    `returns` — Returns (reason, status)  

    `suppliers` — Suppliers (company, contact)  



!!! abstract "Concepts"

    `cardinality explosion`, `NULL comparison`, `LEFT JOIN pitfall`, `GROUP BY`, `HAVING vs WHERE`, `DISTINCT`, `correlated subquery`, `date range`, `NULLIF`, `UNION`



### 1. The query below calculates revenue by product for 2024. Howe


The query below calculates revenue by product for 2024. However, the revenue comes out much larger than expected. Why?

```sql
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


**Hint 1:** When two 1:N relationships are JOINed simultaneously, suspect a cardinality explosion where rows multiply.


??? success "Answer"
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


    **Result** (top 7 of 217 rows)

    | name | revenue | avg_rating |
    |---|---|---|
    | Razer Blade 18 Black | 104,562,500.00 | 3.92 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 94,176,000.00 | 4.12 |
    | Samsung DDR4 32GB PC4-25600 | 3,088,500.00 | 3.94 |
    | Dell U2724D | 10,729,200.00 | 4.19 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | 9,018,000.00 | 3.61 |
    | MSI Radeon RX 9070 VENTUS 3X White | 21,836,700.00 | 4.08 |
    | Samsung DDR5 32GB PC5-38400 | 13,767,000.00 | 3.97 |


---


### 2. The query below tries to find customers without a birth date


The query below tries to find customers without a birth date. It returns 0 rows. Why?

```sql
SELECT name, email
FROM customers
WHERE birth_date = NULL;
```


**Hint 1:** In SQL, comparing with NULL using `=` always returns FALSE. Use the NULL-specific comparison operator.


??? success "Answer"
    ```sql
    -- 수정: IS NULL 사용
    SELECT name, email
    FROM customers
    WHERE birth_date IS NULL;
    ```


    **Result** (top 7 of 738 rows)

    | name | email |
    |---|---|
    | Ashley Jones | user7@testmail.kr |
    | Andrew Reeves | user13@testmail.kr |
    | Martha Murphy | user14@testmail.kr |
    | Heather Gonzalez MD | user21@testmail.kr |
    | Barbara White | user24@testmail.kr |
    | Donald Watts | user27@testmail.kr |
    | Angela Barrera | user36@testmail.kr |


---


### 3. LEFT JOIN was used to include products without reviews, but 


LEFT JOIN was used to include products without reviews, but products without reviews are missing from the results.

```sql
SELECT p.name, p.price, r.rating
FROM products AS p
LEFT JOIN reviews AS r ON p.id = r.product_id
WHERE r.rating >= 3;
```


**Hint 1:** Filtering on the RIGHT table's column in `WHERE` removes NULL rows, making a LEFT JOIN behave like an INNER JOIN. Try moving the condition to the `ON` clause.


??? success "Answer"
    ```sql
    -- 수정: 조건을 ON 절로 이동
    SELECT p.name, p.price, r.rating
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id AND r.rating >= 3;
    ```


    **Result** (top 7 of 7,277 rows)

    | name | price | rating |
    |---|---|---|
    | Razer Blade 18 Black | 2,987,500.00 | 3 |
    | Razer Blade 18 Black | 2,987,500.00 | 3 |
    | Razer Blade 18 Black | 2,987,500.00 | 3 |
    | Razer Blade 18 Black | 2,987,500.00 | 4 |
    | Razer Blade 18 Black | 2,987,500.00 | 4 |
    | Razer Blade 18 Black | 2,987,500.00 | 4 |
    | Razer Blade 18 Black | 2,987,500.00 | 4 |


---


### 4. The query below tries to count products per category. It thr


The query below tries to count products per category. It throws an error.

```sql
SELECT cat.name, COUNT(*) AS product_count
FROM products AS p
INNER JOIN categories AS cat ON p.category_id = cat.id;
```


**Hint 1:** When using an aggregate function (`COUNT`) alongside a non-aggregate column (`cat.name`), a certain clause is required.


??? success "Answer"
    ```sql
    -- 수정: GROUP BY 추가
    SELECT cat.name, COUNT(*) AS product_count
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    GROUP BY cat.name;
    ```


    **Result** (top 7 of 38 rows)

    | name | product_count |
    |---|---|
    | 2-in-1 | 9 |
    | AMD | 10 |
    | AMD Socket | 10 |
    | Air Cooling | 5 |
    | Barebone | 2 |
    | Case | 11 |
    | Custom Build | 11 |


---


### 5. The goal is to show only categories that have 5 or more prod


The goal is to show only categories that have 5 or more products priced at 100,000 or above. It throws an error.

```sql
SELECT cat.name, COUNT(*) AS expensive_count
FROM products AS p
INNER JOIN categories AS cat ON p.category_id = cat.id
HAVING p.price >= 100000 AND COUNT(*) >= 5
GROUP BY cat.name;
```


**Hint 1:** Row-level filters (`p.price >= 100000`) go in `WHERE`, group-level filters (`COUNT(*) >= 5`) go in `HAVING`. Also check the clause order.


??? success "Answer"
    ```sql
    -- 수정
    SELECT cat.name, COUNT(*) AS expensive_count
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE p.price >= 100000
    GROUP BY cat.name
    HAVING COUNT(*) >= 5;
    ```


    **Result** (top 7 of 27 rows)

    | name | expensive_count |
    |---|---|
    | 2-in-1 | 9 |
    | AMD | 10 |
    | AMD Socket | 10 |
    | Case | 10 |
    | Custom Build | 11 |
    | DDR5 | 8 |
    | External Storage | 6 |


---


### 6. Counting the number of categories each customer purchased fr


Counting the number of categories each customer purchased from. The counts are abnormally large.

```sql
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


**Hint 1:** Buying from the same category multiple times causes duplicate counts. Add a deduplication keyword to `COUNT`.


??? success "Answer"
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


    **Result** (top 7 of 10 rows)

    | name | category_count |
    |---|---|
    | Brenda Garcia | 38 |
    | James Banks | 38 |
    | Courtney Huff | 38 |
    | Thomas Moran | 38 |
    | Eduardo Taylor | 38 |
    | Dennis Herrera | 38 |
    | Christina Suarez | 38 |


---


### 7. Trying to find products more expensive than the category ave


Trying to find products more expensive than the category average. It throws an error.

```sql
SELECT name, price
FROM products
WHERE price > (
    SELECT AVG(price) FROM products GROUP BY category_id
);
```


**Hint 1:** The `>` operator can only compare against a single value, but the subquery returns multiple rows. Remove the `GROUP BY` or convert to a correlated subquery.


??? success "Answer"
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


### 8. Trying to get December 2024 orders. Orders from December 31s


Trying to get December 2024 orders. Orders from December 31st are missing.

```sql
SELECT COUNT(*) AS december_orders
FROM orders
WHERE ordered_at BETWEEN '2024-12-01' AND '2024-12-31';
```


**Hint 1:** If `ordered_at` contains time information, `'2024-12-31'` is compared as `'2024-12-31 00:00:00'`. Make sure to include up to the end of the day.


??? success "Answer"
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


### 9. A monthly revenue report includes cancelled orders in the re


A monthly revenue report includes cancelled orders in the revenue.

```sql
SELECT
    SUBSTR(ordered_at, 1, 7) AS month,
    SUM(total_amount) AS revenue
FROM orders
GROUP BY SUBSTR(ordered_at, 1, 7)
ORDER BY month;
```


**Hint 1:** The `WHERE` clause is missing a condition to exclude cancelled/returned order statuses.


??? success "Answer"
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


    **Result** (top 7 of 120 rows)

    | month | revenue |
    |---|---|
    | 2016-01 | 14,194,769.00 |
    | 2016-02 | 12,984,335.00 |
    | 2016-03 | 14,154,562.00 |
    | 2016-04 | 16,878,372.00 |
    | 2016-05 | 28,570,768.00 |
    | 2016-06 | 23,793,991.00 |
    | 2016-07 | 29,696,984.00 |


---


### 10. Calculating the return rate. An error occurs for suppliers w


Calculating the return rate. An error occurs for suppliers with zero sales.

```sql
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


**Hint 1:** The denominator can be zero. Use `NULLIF(value, 0)` to convert 0 to NULL, which returns NULL instead of an error.


??? success "Answer"
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


    **Result** (top 7 of 60 rows)

    | company_name | return_count | sale_count | return_rate |
    |---|---|---|---|
    | Samsung Official Distribution | 210 | 7542 | 2.78 |
    | LG Official Distribution | 60 | 1661 | 3.61 |
    | Intel Corp. | 83 | 2582 | 3.21 |
    | AMD Corp. | 48 | 1653 | 2.90 |
    | NVIDIA Corp. | 0 | 0 | NULL |
    | Hansung Computer | 19 | 266 | 7.14 |
    | Jooyon Tech | 10 | 208 | 4.81 |


---


### 11. Trying to count products by price tier and then filter. It t


Trying to count products by price tier and then filter. It throws an error.

```sql
SELECT
    CASE WHEN price < 100000 THEN '저가' ELSE '고가' END AS tier,
    COUNT(*) AS cnt
FROM products
WHERE tier = '저가'
GROUP BY tier;
```


**Hint 1:** SQL execution order is FROM -> WHERE -> GROUP BY -> SELECT. `WHERE` cannot reference aliases from `SELECT`.


??? success "Answer"
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


### 12. Trying to combine order events and complaint events. It thro


Trying to combine order events and complaint events. It throws an error.

```sql
SELECT order_number, total_amount, ordered_at FROM orders
UNION ALL
SELECT title, category, created_at FROM complaints;
```


**Hint 1:** Each SELECT in a `UNION` must have the same number of columns with compatible types. Align the columns to a unified structure with matching semantics.


??? success "Answer"
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


    **Result** (top 7 of 20 rows)

    | type | reference | event_date |
    |---|---|---|
    | 문의 | Not powering on | 2026-01-13 20:27:26 |
    | 문의 | Product usage question | 2026-01-11 05:32:28 |
    | 문의 | Partial refund request | 2026-01-10 08:43:56 |
    | 문의 | Screen has dead pixels | 2026-01-08 10:26:57 |
    | 문의 | Product usage question | 2026-01-08 08:28:26 |
    | 문의 | Product usage question | 2026-01-05 13:56:10 |
    | 문의 | Can I exchange for a different size? | 2026-01-04 21:17:27 |


---
