# Intermediate Comprehensive Exercises

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `customers` — Customers (grade, points, channel)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `categories` — Categories (parent-child hierarchy)  

    `payments` — Payments (method, amount, status)  

    `reviews` — Reviews (rating, content)  

    `shipping` — Shipping (carrier, tracking, status)  

    `complaints` — Complaints (type, priority)  

    `wishlists` — Wishlists (customer-product)  

    `suppliers` — Suppliers (company, contact)  

    `returns` — Returns (reason, status)  

    `coupon_usage` — Coupon usage records  



!!! abstract "Concepts"

    `JOIN`, `subquery`, `date functions`, `string functions`, `CASE`, `UNION`, `GROUP BY`, `HAVING`, `aggregate functions`, `LAG`, `window functions`



### 1. JOIN + GROUP BY: Find active product count and average price


JOIN + GROUP BY: Find active product count and average price per category. Top 10 by product count.


**Hint 1:** JOIN products with categories, aggregate per category with GROUP BY. Filter active with WHERE is_active = 1.


??? success "Answer"
    ```sql
    SELECT
        cat.name AS category,
        COUNT(*) AS product_count,
        ROUND(AVG(p.price)) AS avg_price
    FROM products p
    INNER JOIN categories cat ON p.category_id = cat.id
    WHERE p.is_active = 1
    GROUP BY cat.id, cat.name
    ORDER BY product_count DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | category | product_count | avg_price |
    |---|---|---|
    | Power Supply (PSU) | 11 | 234,645.00 |
    | Gaming Monitor | 10 | 1,123,150.00 |
    | Intel Socket | 10 | 527,080.00 |
    | Case | 10 | 159,930.00 |
    | Custom Build | 9 | 1,836,467.00 |
    | AMD Socket | 9 | 511,056.00 |
    | Speakers/Headsets | 9 | 274,056.00 |


---


### 2. JOIN + CASE: Find order number, customer name, and payment m


JOIN + CASE: Find order number, customer name, and payment method (in Korean). Most recent 10.


**Hint 1:** Connect 3 tables. Convert to Korean with `CASE payments.method WHEN ... THEN ...`.


??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        c.name AS customer_name,
        CASE pay.method
            WHEN 'card' THEN '카드'
            WHEN 'bank_transfer' THEN '계좌이체'
            WHEN 'kakao_pay' THEN '카카오페이'
            WHEN 'naver_pay' THEN '네이버페이'
            WHEN 'virtual_account' THEN '가상계좌'
            WHEN 'point' THEN '포인트'
            ELSE '기타'
        END AS payment_method_kr,
        o.total_amount
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.id
    INNER JOIN payments pay ON o.id = pay.order_id
    ORDER BY o.ordered_at DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | order_number | customer_name | payment_method_kr | total_amount |
    |---|---|---|---|
    | ORD-20251231-37555 | Angel Jones | 카드 | 74,800.00 |
    | ORD-20251231-37543 | Carla Watson | 카카오페이 | 134,100.00 |
    | ORD-20251231-37552 | Martin Hanson | 카드 | 254,300.00 |
    | ORD-20251231-37548 | Lucas Johnson | 계좌이체 | 187,700.00 |
    | ORD-20251231-37542 | Adam Moore | 카카오페이 | 155,700.00 |
    | ORD-20251231-37546 | Justin Murphy | 네이버페이 | 198,300.00 |
    | ORD-20251231-37547 | Sara Hill | 계좌이체 | 335,000.00 |


---


### 3. Subquery + dates: Find the top 5 customers by order count in


Subquery + dates: Find the top 5 customers by order count in 2024, with name, count, and total spent.


**Hint 1:** Filter with `ordered_at LIKE '2024%'` in orders, aggregate with `GROUP BY customer_id`.


??? success "Answer"
    ```sql
    SELECT
        c.name,
        sub.order_count,
        sub.total_spent
    FROM (
        SELECT customer_id, COUNT(*) AS order_count, SUM(total_amount) AS total_spent
        FROM orders
        WHERE ordered_at LIKE '2024%'
        GROUP BY customer_id
        ORDER BY order_count DESC
        LIMIT 5
    ) sub
    INNER JOIN customers c ON sub.customer_id = c.id
    ORDER BY sub.order_count DESC;
    ```


    **Result** (5 rows)

    | name | order_count | total_spent |
    |---|---|---|
    | Dennis Brown | 25 | 25,706,293.00 |
    | Christina Jennings | 25 | 24,330,429.00 |
    | Carol Anderson | 24 | 28,684,563.00 |
    | Mrs. Jennifer Rios | 23 | 24,524,212.00 |
    | Tiffany Graham | 23 | 20,979,498.00 |


---


### 4. String functions + GROUP BY: Aggregate customer count by ema


String functions + GROUP BY: Aggregate customer count by email domain.


**Hint 1:** Extract domain with `SUBSTR(email, INSTR(email, '@') + 1)`.


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(email, INSTR(email, '@') + 1) AS domain,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY domain
    ORDER BY customer_count DESC;
    ```


    **Result** (1 rows)

    | domain | customer_count |
    |---|---|
    | testmail.kr | 5230 |


---


### 5. JOIN + HAVING: Find customers who wrote 5+ reviews, with nam


JOIN + HAVING: Find customers who wrote 5+ reviews, with name and average rating. Top 10.


**Hint 1:** JOIN reviews with customers, then GROUP BY + HAVING COUNT(*) >= 5.


??? success "Answer"
    ```sql
    SELECT
        c.name,
        COUNT(*) AS review_count,
        ROUND(AVG(r.rating), 1) AS avg_rating
    FROM reviews r
    INNER JOIN customers c ON r.customer_id = c.id
    GROUP BY r.customer_id, c.name
    HAVING COUNT(*) >= 5
    ORDER BY review_count DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | review_count | avg_rating |
    |---|---|---|
    | Jason Rivera | 72 | 3.80 |
    | Allen Snyder | 63 | 3.80 |
    | Courtney Huff | 63 | 4.10 |
    | Gabriel Walters | 62 | 4.00 |
    | Brenda Garcia | 62 | 3.80 |
    | Ronald Arellano | 60 | 3.60 |
    | James Banks | 59 | 4.20 |


---


### 6. UNION + CASE: Combine new customer count and new product cou


UNION + CASE: Combine new customer count and new product count from 2024 into a single result.


**Hint 1:** COUNT 2024 data from each table and combine with UNION ALL.


??? success "Answer"
    ```sql
    SELECT '신규 고객' AS category, COUNT(*) AS count_2024
    FROM customers
    WHERE created_at LIKE '2024%'
    UNION ALL
    SELECT '신규 상품' AS category, COUNT(*) AS count_2024
    FROM products
    WHERE created_at LIKE '2024%';
    ```


    **Result** (2 rows)

    | category | count_2024 |
    |---|---|
    | 신규 고객 | 700 |
    | 신규 상품 | 30 |


---


### 7. Date functions + JOIN: Find average delivery days per carrie


Date functions + JOIN: Find average delivery days per carrier. Delivered orders only.


**Hint 1:** Calculate days with `julianday(delivered_at) - julianday(ordered_at)`.


??? success "Answer"
    ```sql
    SELECT
        s.carrier,
        COUNT(*) AS delivered_count,
        ROUND(AVG(julianday(s.delivered_at) - julianday(o.ordered_at)), 1) AS avg_days
    FROM shipping s
    INNER JOIN orders o ON s.order_id = o.id
    WHERE s.status = 'delivered' AND s.delivered_at IS NOT NULL
    GROUP BY s.carrier
    ORDER BY avg_days;
    ```


    **Result** (5 rows)

    | carrier | delivered_count | avg_days |
    |---|---|---|
    | DHL | 5184 | 4.50 |
    | FedEx | 10,198 | 4.50 |
    | OnTrac | 3417 | 4.50 |
    | UPS | 8729 | 4.50 |
    | USPS | 6990 | 4.50 |


---


### 8. Subquery + CASE: Show each product's price level relative to


Subquery + CASE: Show each product's price level relative to its category average. Top 15.


**Hint 1:** Compute category avg via subquery, JOIN it, then use CASE for comparison.


??? success "Answer"
    ```sql
    SELECT
        p.name, p.price, cat_avg.avg_price,
        CASE
            WHEN p.price > cat_avg.avg_price * 1.2 THEN '고가'
            WHEN p.price < cat_avg.avg_price * 0.8 THEN '저가'
            ELSE '평균 수준'
        END AS price_level
    FROM products p
    INNER JOIN (
        SELECT category_id, ROUND(AVG(price)) AS avg_price
        FROM products WHERE is_active = 1
        GROUP BY category_id
    ) cat_avg ON p.category_id = cat_avg.category_id
    WHERE p.is_active = 1
    ORDER BY p.price DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | price | avg_price | price_level |
    |---|---|---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 | 5,481,100.00 | 평균 수준 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 | 2,207,600.00 | 고가 |
    | Razer Blade 18 Black | 4,353,100.00 | 2,887,583.00 | 고가 |
    | Razer Blade 16 Silver | 3,702,900.00 | 2,887,583.00 | 고가 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 | 1,836,467.00 | 고가 |
    | ASUS ROG Strix GT35 | 3,296,800.00 | 1,836,467.00 | 고가 |
    | Razer Blade 18 Black | 2,987,500.00 | 2,887,583.00 | 평균 수준 |


---


### 9. JOIN + GROUP BY + HAVING + Subquery: Find brands with above-


JOIN + GROUP BY + HAVING + Subquery: Find brands with above-average revenue. Top 10.


**Hint 1:** Overall average is the mean of per-brand revenues.


??? success "Answer"
    ```sql
    SELECT
        p.brand,
        SUM(oi.subtotal) AS total_revenue,
        COUNT(DISTINCT oi.order_id) AS order_count
    FROM order_items oi
    INNER JOIN products p ON oi.product_id = p.id
    GROUP BY p.brand
    HAVING SUM(oi.subtotal) > (
        SELECT AVG(brand_revenue)
        FROM (
            SELECT SUM(oi2.subtotal) AS brand_revenue
            FROM order_items oi2
            INNER JOIN products p2 ON oi2.product_id = p2.id
            GROUP BY p2.brand
        )
    )
    ORDER BY total_revenue DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | brand | total_revenue | order_count |
    |---|---|---|
    | ASUS | 6,181,415,600.00 | 4945 |
    | Razer | 4,167,252,100.00 | 2754 |
    | Samsung | 3,000,828,600.00 | 7169 |
    | MSI | 2,787,039,100.00 | 3531 |
    | LG | 2,221,778,900.00 | 1647 |
    | ASRock | 1,741,420,800.00 | 3435 |
    | Intel | 1,267,419,000.00 | 2579 |


---


### 10. Show 2024 monthly order status distribution: confirmed, canc


Show 2024 monthly order status distribution: confirmed, cancelled, in-progress counts and cancel rate.


**Hint 1:** Conditional aggregation with `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`.


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) AS confirmed,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
        SUM(CASE WHEN status NOT IN ('confirmed', 'cancelled') THEN 1 ELSE 0 END) AS in_progress,
        ROUND(100.0 * SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1) AS cancel_rate
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```


    **Result** (top 7 of 12 rows)

    | month | total_orders | confirmed | cancelled | in_progress | cancel_rate |
    |---|---|---|---|---|---|
    | 2024-01 | 346 | 314 | 21 | 11 | 6.10 |
    | 2024-02 | 465 | 416 | 32 | 17 | 6.90 |
    | 2024-03 | 601 | 555 | 29 | 17 | 4.80 |
    | 2024-04 | 506 | 466 | 28 | 12 | 5.50 |
    | 2024-05 | 415 | 385 | 19 | 11 | 4.60 |
    | 2024-06 | 415 | 389 | 18 | 8 | 4.30 |
    | 2024-07 | 414 | 381 | 23 | 10 | 5.60 |


---


### 11. Find products purchased by VIP customers with avg review rat


Find products purchased by VIP customers with avg review rating >= 4.0. Show name, brand, rating, and VIP purchase count. Top 10.


**Hint 1:** Multi-table JOIN for VIP purchases. Subquery for review avg >= 4.0.


??? success "Answer"
    ```sql
    SELECT
        p.name, p.brand, review_avg.avg_rating,
        COUNT(*) AS vip_purchase_count
    FROM order_items oi
    INNER JOIN orders o ON oi.order_id = o.id
    INNER JOIN customers c ON o.customer_id = c.id
    INNER JOIN products p ON oi.product_id = p.id
    INNER JOIN (
        SELECT product_id, ROUND(AVG(rating), 1) AS avg_rating
        FROM reviews GROUP BY product_id HAVING AVG(rating) >= 4.0
    ) review_avg ON p.id = review_avg.product_id
    WHERE c.grade = 'VIP'
    GROUP BY p.id, p.name, p.brand, review_avg.avg_rating
    ORDER BY vip_purchase_count DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | brand | avg_rating | vip_purchase_count |
    |---|---|---|---|
    | Crucial T700 2TB Silver | Crucial | 4.20 | 617 |
    | Logitech G502 X PLUS | Logitech | 4.20 | 429 |
    | be quiet! Light Base 900 | be quiet! | 4.10 | 338 |
    | Arctic Freezer 36 A-RGB White | Arctic | 4.00 | 317 |
    | Logitech MX Anywhere 3S Black | Logitech | 4.00 | 315 |
    | Logitech G715 White | Logitech | 4.10 | 314 |
    | be quiet! Pure Power 12 M 850W White | be quiet! | 4.10 | 304 |


---


### 12. LEFT JOIN + COALESCE: Find all products' name, price, total 


LEFT JOIN + COALESCE: Find all products' name, price, total sold, and review count. Show 0 for none. Top 15.


**Hint 1:** Aggregate sales and reviews separately as subqueries, then LEFT JOIN to prevent cardinality explosion.


??? success "Answer"
    ```sql
    SELECT
        p.name, p.price,
        COALESCE(sales.total_qty, 0) AS total_sold,
        COALESCE(rev.review_count, 0) AS review_count
    FROM products p
    LEFT JOIN (
        SELECT product_id, SUM(quantity) AS total_qty
        FROM order_items GROUP BY product_id
    ) sales ON p.id = sales.product_id
    LEFT JOIN (
        SELECT product_id, COUNT(*) AS review_count
        FROM reviews GROUP BY product_id
    ) rev ON p.id = rev.product_id
    WHERE p.is_active = 1
    ORDER BY total_sold DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | price | total_sold | review_count |
    |---|---|---|---|
    | Crucial T700 2TB Silver | 257,000.00 | 1503 | 77 |
    | AMD Ryzen 9 9900X | 335,700.00 | 1447 | 65 |
    | SK hynix Platinum P41 2TB Silver | 255,500.00 | 1359 | 49 |
    | Logitech G502 X PLUS | 97,500.00 | 1087 | 101 |
    | Kingston FURY Beast DDR4 16GB Silver | 48,000.00 | 1061 | 102 |
    | SteelSeries Prime Wireless Black | 89,800.00 | 1034 | 80 |
    | SteelSeries Aerox 5 Wireless Silver | 100,000.00 | 1030 | 100 |


---


### 13. UNION + JOIN + GROUP BY: Calculate per-customer "activity sc


UNION + JOIN + GROUP BY: Calculate per-customer "activity score". Order=10pts, review=5pts, inquiry=3pts. Top 10.


**Hint 1:** Combine scores per activity with UNION ALL, then SUM externally for total.


??? success "Answer"
    ```sql
    SELECT
        c.name, c.grade,
        SUM(activity.score) AS total_score,
        SUM(CASE WHEN activity.type = '주문' THEN 1 ELSE 0 END) AS orders,
        SUM(CASE WHEN activity.type = '리뷰' THEN 1 ELSE 0 END) AS reviews,
        SUM(CASE WHEN activity.type = '문의' THEN 1 ELSE 0 END) AS complaints
    FROM (
        SELECT customer_id, '주문' AS type, 10 AS score FROM orders
        UNION ALL
        SELECT customer_id, '리뷰' AS type, 5 AS score FROM reviews
        UNION ALL
        SELECT customer_id, '문의' AS type, 3 AS score FROM complaints
    ) activity
    INNER JOIN customers c ON activity.customer_id = c.id
    GROUP BY activity.customer_id, c.name, c.grade
    ORDER BY total_score DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | grade | total_score | orders | reviews | complaints |
    |---|---|---|---|---|---|
    | Jason Rivera | VIP | 4095 | 366 | 72 | 25 |
    | Allen Snyder | VIP | 3652 | 328 | 63 | 19 |
    | Gabriel Walters | VIP | 3467 | 307 | 62 | 29 |
    | Brenda Garcia | VIP | 3042 | 266 | 62 | 24 |
    | James Banks | VIP | 2794 | 246 | 59 | 13 |
    | Courtney Huff | VIP | 2742 | 237 | 63 | 19 |
    | Ronald Arellano | VIP | 2697 | 234 | 60 | 19 |


---


### 14. Subquery + JOIN + dates: Compare customer counts by time-to-


Subquery + JOIN + dates: Compare customer counts by time-to-first-order segments (30d/31-90d/90d+).


**Hint 1:** Get first order date with `MIN(ordered_at)`, compute days with `julianday` difference.


??? success "Answer"
    ```sql
    SELECT
        CASE
            WHEN days_to_first_order <= 30 THEN '30일 이내'
            WHEN days_to_first_order <= 90 THEN '31~90일'
            ELSE '90일 초과'
        END AS segment,
        COUNT(*) AS customer_count,
        ROUND(AVG(days_to_first_order), 1) AS avg_days
    FROM (
        SELECT c.id,
            ROUND(julianday(MIN(o.ordered_at)) - julianday(c.created_at)) AS days_to_first_order
        FROM customers c
        INNER JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.created_at
    )
    GROUP BY segment
    ORDER BY MIN(days_to_first_order);
    ```


    **Result** (3 rows)

    | segment | customer_count | avg_days |
    |---|---|---|
    | 30일 이내 | 955 | 8.30 |
    | 31~90일 | 596 | 56.10 |
    | 90일 초과 | 1288 | 329.50 |


---


### 15. Show revenue by payment method and card issuer. Non-card sho


Show revenue by payment method and card issuer. Non-card shows 'N/A'. Top 15.


**Hint 1:** Handle NULL with `COALESCE(card_issuer, 'N/A')`. `GROUP BY method, card_issuer`.


??? success "Answer"
    ```sql
    SELECT
        CASE pay.method
            WHEN 'card' THEN '카드'
            WHEN 'bank_transfer' THEN '계좌이체'
            WHEN 'kakao_pay' THEN '카카오페이'
            WHEN 'naver_pay' THEN '네이버페이'
            ELSE pay.method
        END AS method_kr,
        COALESCE(pay.card_issuer, '해당없음') AS issuer,
        COUNT(*) AS payment_count,
        SUM(pay.amount) AS total_amount,
        ROUND(AVG(pay.amount)) AS avg_amount
    FROM payments pay
    WHERE pay.status = 'completed'
    GROUP BY pay.method, pay.card_issuer
    ORDER BY total_amount DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 12 rows)

    | method_kr | issuer | payment_count | total_amount | avg_amount |
    |---|---|---|---|---|
    | 카카오페이 | 해당없음 | 6886 | 6,781,114,303.00 | 984,768.00 |
    | 네이버페이 | 해당없음 | 5270 | 5,420,480,093.00 | 1,028,554.00 |
    | 카드 | Visa | 4701 | 4,629,735,049.00 | 984,840.00 |
    | 카드 | Mastercard | 3741 | 3,950,729,395.00 | 1,056,062.00 |
    | 계좌이체 | 해당없음 | 3429 | 3,456,454,657.00 | 1,008,007.00 |
    | 카드 | American Express | 2320 | 2,371,883,900.00 | 1,022,364.00 |
    | point | 해당없음 | 1770 | 1,780,334,619.00 | 1,005,839.00 |


---


### 16. Classify customers by RFM Recency: Active (30d), Warm (90d),


Classify customers by RFM Recency: Active (30d), Warm (90d), Cold (180d), Dormant.


**Hint 1:** Include customers without orders via LEFT JOIN. Use MAX and julianday for elapsed days.


??? success "Answer"
    ```sql
    SELECT
        recency_group,
        COUNT(*) AS customer_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM (
        SELECT c.id,
            CASE
                WHEN MAX(o.ordered_at) IS NULL THEN 'Dormant'
                WHEN julianday('now') - julianday(MAX(o.ordered_at)) <= 30 THEN 'Active'
                WHEN julianday('now') - julianday(MAX(o.ordered_at)) <= 90 THEN 'Warm'
                WHEN julianday('now') - julianday(MAX(o.ordered_at)) <= 180 THEN 'Cold'
                ELSE 'Dormant'
            END AS recency_group
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id
    )
    GROUP BY recency_group
    ORDER BY CASE recency_group WHEN 'Active' THEN 1 WHEN 'Warm' THEN 2 WHEN 'Cold' THEN 3 ELSE 4 END;
    ```


    **Result** (2 rows)

    | recency_group | customer_count | pct |
    |---|---|---|
    | Cold | 960 | 18.40 |
    | Dormant | 4270 | 81.60 |


---


### 17. Monthly revenue report: 2024 monthly revenue, order count, u


Monthly revenue report: 2024 monthly revenue, order count, unique customers, avg order value, and MoM growth rate.


**Hint 1:** Use `LAG()` window function to get previous month revenue and calculate growth rate.


??? success "Answer"
    ```sql
    SELECT
        month, total_revenue, order_count, unique_customers,
        ROUND(total_revenue * 1.0 / order_count) AS avg_order_value,
        CASE
            WHEN prev_revenue IS NULL THEN '-'
            ELSE ROUND((total_revenue - prev_revenue) * 100.0 / prev_revenue, 1) || '%'
        END AS growth_rate
    FROM (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS month,
            SUM(total_amount) AS total_revenue,
            COUNT(*) AS order_count,
            COUNT(DISTINCT customer_id) AS unique_customers,
            LAG(SUM(total_amount)) OVER (ORDER BY SUBSTR(ordered_at, 1, 7)) AS prev_revenue
        FROM orders
        WHERE ordered_at LIKE '2024%' AND status NOT IN ('cancelled')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    ORDER BY month;
    ```


    **Result** (top 7 of 12 rows)

    | month | total_revenue | order_count | unique_customers | avg_order_value | growth_rate |
    |---|---|---|---|---|---|
    | 2024-01 | 301,075,320.00 | 325 | 275 | 926,386.00 | - |
    | 2024-02 | 426,177,449.00 | 433 | 345 | 984,244.00 | 41.6% |
    | 2024-03 | 536,322,767.00 | 572 | 428 | 937,627.00 | 25.8% |
    | 2024-04 | 470,154,081.00 | 478 | 362 | 983,586.00 | -12.3% |
    | 2024-05 | 459,724,596.00 | 396 | 323 | 1,160,921.00 | -2.2% |
    | 2024-06 | 377,040,302.00 | 397 | 327 | 949,724.00 | -18.0% |
    | 2024-07 | 363,944,597.00 | 391 | 320 | 930,805.00 | -3.5% |


---


### 18. Find avg order amount, avg review rating, and return rate pe


Find avg order amount, avg review rating, and return rate per customer grade.


**Hint 1:** Aggregate each metric separately as subqueries, then GROUP BY grade.


??? success "Answer"
    ```sql
    SELECT
        c.grade,
        COUNT(DISTINCT c.id) AS customer_count,
        ROUND(AVG(order_stats.avg_amount)) AS avg_order_amount,
        ROUND(AVG(review_stats.avg_rating), 2) AS avg_rating,
        ROUND(100.0 * SUM(COALESCE(return_stats.return_count, 0))
            / NULLIF(SUM(COALESCE(order_stats.order_count, 0)), 0), 2) AS return_rate_pct
    FROM customers c
    LEFT JOIN (
        SELECT customer_id, COUNT(*) AS order_count, AVG(total_amount) AS avg_amount
        FROM orders GROUP BY customer_id
    ) order_stats ON c.id = order_stats.customer_id
    LEFT JOIN (
        SELECT customer_id, AVG(rating) AS avg_rating
        FROM reviews GROUP BY customer_id
    ) review_stats ON c.id = review_stats.customer_id
    LEFT JOIN (
        SELECT customer_id, COUNT(*) AS return_count
        FROM returns GROUP BY customer_id
    ) return_stats ON c.id = return_stats.customer_id
    GROUP BY c.grade
    ORDER BY CASE c.grade WHEN 'VIP' THEN 1 WHEN 'GOLD' THEN 2 WHEN 'SILVER' THEN 3 WHEN 'BRONZE' THEN 4 END;
    ```


    **Result** (4 rows)

    | grade | customer_count | avg_order_amount | avg_rating | return_rate_pct |
    |---|---|---|---|---|
    | VIP | 368 | 1,419,393.00 | 3.88 | 2.56 |
    | GOLD | 524 | 1,119,695.00 | 3.92 | 2.48 |
    | SILVER | 479 | 887,476.00 | 3.90 | 2.68 |
    | BRONZE | 3859 | 699,518.00 | 3.92 | 3.02 |


---


### 19. Low stock risk check: Find products where current stock is l


Low stock risk check: Find products where current stock is less than 30-day sales volume. Include estimated days left. Top 15.


**Hint 1:** Calculate 30-day sales from order_items JOIN orders with date filter.


??? success "Answer"
    ```sql
    SELECT
        p.name, p.stock_qty AS current_stock,
        COALESCE(sales.qty_30d, 0) AS sold_30d,
        CASE
            WHEN COALESCE(sales.qty_30d, 0) = 0 THEN '판매 없음'
            ELSE CAST(ROUND(p.stock_qty * 30.0 / sales.qty_30d) AS INTEGER) || '일'
        END AS est_days_left
    FROM products p
    LEFT JOIN (
        SELECT oi.product_id, SUM(oi.quantity) AS qty_30d
        FROM order_items oi
        INNER JOIN orders o ON oi.order_id = o.id
        WHERE o.ordered_at >= date('now', '-30 days') AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    ) sales ON p.id = sales.product_id
    WHERE p.is_active = 1 AND p.stock_qty < COALESCE(sales.qty_30d, 0)
    ORDER BY p.stock_qty ASC
    LIMIT 15;
    ```


---


### 20. Category hierarchy analysis: Find product count, total reven


Category hierarchy analysis: Find product count, total revenue, and avg review rating per top-level category (depth=0).


**Hint 1:** Follow the category parent_id upward. Self-JOIN categories to find the top-level.


??? success "Answer"
    ```sql
    SELECT
        top_cat.name AS top_category,
        COUNT(DISTINCT p.id) AS product_count,
        COALESCE(SUM(sales.revenue), 0) AS total_revenue,
        ROUND(AVG(rev.avg_rating), 1) AS avg_rating
    FROM categories top_cat
    LEFT JOIN categories mid_cat ON mid_cat.parent_id = top_cat.id
    LEFT JOIN categories sub_cat ON sub_cat.parent_id = mid_cat.id
    LEFT JOIN products p ON p.category_id IN (top_cat.id, mid_cat.id, sub_cat.id)
    LEFT JOIN (
        SELECT product_id, SUM(subtotal) AS revenue FROM order_items GROUP BY product_id
    ) sales ON p.id = sales.product_id
    LEFT JOIN (
        SELECT product_id, AVG(rating) AS avg_rating FROM reviews GROUP BY product_id
    ) rev ON p.id = rev.product_id
    WHERE top_cat.depth = 0
    GROUP BY top_cat.id, top_cat.name
    ORDER BY total_revenue DESC;
    ```


    **Result** (top 7 of 18 rows)

    | top_category | product_count | total_revenue | avg_rating |
    |---|---|---|---|
    | Laptop | 29 | 10,050,178,200.00 | 3.70 |
    | Graphics Card | 15 | 5,559,698,400.00 | 3.90 |
    | Monitor | 22 | 4,712,362,900.00 | 3.90 |
    | Motherboard | 23 | 3,225,292,000.00 | 3.70 |
    | CPU | 7 | 1,858,019,600.00 | 3.80 |
    | Speakers/Headsets | 12 | 1,546,414,500.00 | 3.90 |
    | Storage | 15 | 1,511,680,300.00 | 3.90 |


---


### 21. Supplier performance comparison: product count, revenue, avg


Supplier performance comparison: product count, revenue, avg rating, return rate per supplier. Top 10 by revenue.


**Hint 1:** Separating each metric into subqueries keeps it clean.


??? success "Answer"
    ```sql
    SELECT
        s.company_name,
        COUNT(DISTINCT p.id) AS product_count,
        COALESCE(SUM(sales.revenue), 0) AS total_revenue,
        ROUND(AVG(rev.avg_rating), 1) AS avg_rating,
        ROUND(100.0 * COALESCE(SUM(ret.return_count), 0)
            / NULLIF(COALESCE(SUM(sales.sold_count), 0), 0), 2) AS return_rate_pct
    FROM suppliers s
    INNER JOIN products p ON p.supplier_id = s.id
    LEFT JOIN (SELECT product_id, SUM(subtotal) AS revenue, COUNT(*) AS sold_count FROM order_items GROUP BY product_id) sales ON p.id = sales.product_id
    LEFT JOIN (SELECT product_id, AVG(rating) AS avg_rating FROM reviews GROUP BY product_id) rev ON p.id = rev.product_id
    LEFT JOIN (SELECT oi.product_id, COUNT(DISTINCT r.id) AS return_count FROM returns r INNER JOIN orders o ON r.order_id = o.id INNER JOIN order_items oi ON o.id = oi.order_id GROUP BY oi.product_id) ret ON p.id = ret.product_id
    GROUP BY s.id, s.company_name
    ORDER BY total_revenue DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | company_name | product_count | total_revenue | avg_rating | return_rate_pct |
    |---|---|---|---|---|
    | ASUS Corp. | 26 | 6,181,415,600.00 | 3.90 | 3.42 |
    | Razer Corp. | 9 | 4,167,252,100.00 | 3.90 | 4.17 |
    | Samsung Official Distribution | 26 | 3,000,828,600.00 | 3.80 | 2.96 |
    | MSI Corp. | 13 | 2,787,039,100.00 | 3.90 | 3.50 |
    | LG Official Distribution | 11 | 2,221,778,900.00 | 3.90 | 3.61 |
    | ASRock Corp. | 11 | 1,741,420,800.00 | 3.60 | 3.38 |
    | Intel Corp. | 6 | 1,267,419,000.00 | 3.80 | 3.21 |


---


### 22. Coupon impact analysis: Compare avg amount, avg items, and c


Coupon impact analysis: Compare avg amount, avg items, and completion rate between coupon-used and non-coupon orders.


**Hint 1:** JOIN orders LEFT JOIN coupon_usage. Distinguish with CASE on cu.id IS NOT NULL.


??? success "Answer"
    ```sql
    SELECT
        CASE WHEN cu.id IS NOT NULL THEN '쿠폰 사용' ELSE '쿠폰 미사용' END AS coupon_group,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(AVG(o.total_amount)) AS avg_amount,
        ROUND(AVG(item_stats.item_count), 1) AS avg_items,
        ROUND(100.0 * SUM(CASE WHEN o.status = 'confirmed' THEN 1 ELSE 0 END)
            / COUNT(DISTINCT o.id), 1) AS confirm_rate_pct
    FROM orders o
    LEFT JOIN coupon_usage cu ON o.id = cu.order_id
    LEFT JOIN (SELECT order_id, COUNT(*) AS item_count FROM order_items GROUP BY order_id) item_stats ON o.id = item_stats.order_id
    GROUP BY CASE WHEN cu.id IS NOT NULL THEN '쿠폰 사용' ELSE '쿠폰 미사용' END;
    ```


    **Result** (2 rows)

    | coupon_group | order_count | avg_amount | avg_items | confirm_rate_pct |
    |---|---|---|---|---|
    | 쿠폰 미사용 | 35,893 | 998,277.00 | 2.40 | 91.20 |
    | 쿠폰 사용 | 1664 | 1,413,663.00 | 2.90 | 100.00 |


---


### 23. Wishlist conversion analysis: Find conversion rate per categ


Wishlist conversion analysis: Find conversion rate per category for wishlisted products. 5+ entries only. Top 10.


**Hint 1:** Determine conversion via `wishlists.is_purchased`.


??? success "Answer"
    ```sql
    SELECT
        cat.name AS category,
        COUNT(*) AS wishlist_count,
        SUM(w.is_purchased) AS purchased_count,
        ROUND(100.0 * SUM(w.is_purchased) / COUNT(*), 1) AS conversion_rate_pct
    FROM wishlists w
    INNER JOIN products p ON w.product_id = p.id
    INNER JOIN categories cat ON p.category_id = cat.id
    GROUP BY cat.id, cat.name
    HAVING COUNT(*) >= 5
    ORDER BY conversion_rate_pct DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | category | wishlist_count | purchased_count | conversion_rate_pct |
    |---|---|---|---|
    | Barebone | 8 | 1 | 12.50 |
    | Membrane | 81 | 6 | 7.40 |
    | Case | 96 | 7 | 7.30 |
    | Intel Socket | 92 | 5 | 5.40 |
    | DDR5 | 64 | 3 | 4.70 |
    | Wired | 22 | 1 | 4.50 |
    | AMD | 47 | 2 | 4.30 |


---


### 24. Customer inquiry response analysis: Find avg resolution time


Customer inquiry response analysis: Find avg resolution time, resolution rate, and escalation rate per inquiry type.


**Hint 1:** Resolution time: julianday difference. Escalation: SUM(escalated).


??? success "Answer"
    ```sql
    SELECT
        category,
        COUNT(*) AS total_count,
        ROUND(AVG(CASE WHEN resolved_at IS NOT NULL THEN julianday(resolved_at) - julianday(created_at) END), 1) AS avg_resolve_days,
        ROUND(100.0 * SUM(CASE WHEN resolved_at IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS resolve_rate_pct,
        ROUND(100.0 * SUM(escalated) / COUNT(*), 1) AS escalation_rate_pct
    FROM complaints
    GROUP BY category
    ORDER BY total_count DESC;
    ```


    **Result** (7 rows)

    | category | total_count | avg_resolve_days | resolve_rate_pct | escalation_rate_pct |
    |---|---|---|---|---|
    | general_inquiry | 1232 | 1.70 | 94.20 | 4.20 |
    | delivery_issue | 708 | 0.7 | 95.60 | 4.90 |
    | refund_request | 522 | 0.8 | 94.40 | 11.10 |
    | product_defect | 460 | 0.6 | 95.00 | 12.20 |
    | price_inquiry | 439 | 1.60 | 95.70 | 3.20 |
    | wrong_item | 240 | 0.6 | 94.20 | 6.70 |
    | exchange_request | 212 | 1.30 | 95.30 | 14.60 |


---


### 25. Comprehensive dashboard query: Total customers, active custo


Comprehensive dashboard query: Total customers, active customers, this/last month revenue, avg order amount, avg review rating, and unresolved inquiries in one query.


**Hint 1:** Create each KPI as SELECT with metric name and value, combine with UNION ALL.


??? success "Answer"
    ```sql
    SELECT '총 고객 수' AS metric, CAST(COUNT(*) AS TEXT) AS value FROM customers
    UNION ALL
    SELECT '활성 고객 수', CAST(COUNT(*) AS TEXT) FROM customers WHERE is_active = 1
    UNION ALL
    SELECT '이번 달 매출', CAST(COALESCE(SUM(total_amount), 0) AS TEXT) FROM orders WHERE SUBSTR(ordered_at, 1, 7) = strftime('%Y-%m', 'now') AND status NOT IN ('cancelled')
    UNION ALL
    SELECT '지난 달 매출', CAST(COALESCE(SUM(total_amount), 0) AS TEXT) FROM orders WHERE SUBSTR(ordered_at, 1, 7) = strftime('%Y-%m', 'now', '-1 month') AND status NOT IN ('cancelled')
    UNION ALL
    SELECT '평균 주문 금액', CAST(ROUND(AVG(total_amount)) AS TEXT) FROM orders WHERE status NOT IN ('cancelled')
    UNION ALL
    SELECT '평균 리뷰 평점', CAST(ROUND(AVG(rating), 2) AS TEXT) FROM reviews
    UNION ALL
    SELECT '미해결 문의', CAST(COUNT(*) AS TEXT) FROM complaints WHERE status NOT IN ('resolved', 'closed');
    ```


    **Result** (7 rows)

    | metric | value |
    |---|---|
    | 총 고객 수 | 5230 |
    | 활성 고객 수 | 3660 |
    | 이번 달 매출 | 0 |
    | 지난 달 매출 | 0 |
    | 평균 주문 금액 | 1015193.0 |
    | 평균 리뷰 평점 | 3.9 |
    | 미해결 문의 | 197 |


---
