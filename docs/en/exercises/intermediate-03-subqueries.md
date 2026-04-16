# Subqueries and Data Transformation

!!! info "Tables"

    `categories` — Categories (parent-child hierarchy)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `payments` — Payments (method, amount, status)  

    `products` — Products (name, price, stock, brand)  

    `reviews` — Reviews (rating, content)  

    `returns` — Returns (reason, status)  

    `wishlists` — Wishlists (customer-product)  



!!! abstract "Concepts"

    `scalar subquery`, `correlated subquery`, `CTE`, `CASE WHEN`, `NOT EXISTS`, `UNION ALL`, `window functions`



### 1. Retrieve the name and price of products that are more expens


Retrieve the name and price of products that are more expensive than the overall average price.


**Hint 1:** Use a scalar subquery: `WHERE price > (SELECT AVG(price) FROM products)`.


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products)
    ORDER BY price DESC;
    ```


    **Result** (top 7 of 83 rows)

    | name | price |
    |---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 |
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 |
    | Razer Blade 18 Black | 4,353,100.00 |
    | Razer Blade 16 Silver | 3,702,900.00 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 |


---


### 2. Find the name, category, total quantity sold, and total reve


Find the name, category, total quantity sold, and total revenue of the #1 best-selling product.


**Hint 1:** JOIN `order_items` with `products` and `categories`, then aggregate per product with `GROUP BY`. Use `ORDER BY total_sold DESC LIMIT 1`.


??? success "Answer"
    ```sql
    SELECT
        p.name,
        cat.name AS category,
        SUM(oi.quantity) AS total_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN orders AS o ON oi.order_id = o.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY p.id, p.name, cat.name
    ORDER BY total_sold DESC
    LIMIT 1;
    ```


    **Result** (1 rows)

    | name | category | total_sold | total_revenue |
    |---|---|---|---|
    | Crucial T700 2TB Silver | SSD | 1439 | 369,823,000.00 |


---


### 3. Retrieve only the products that are more expensive than the 


Retrieve only the products that are more expensive than the average price of their category.


**Hint 1:** Calculate the category average price in a subquery (inline view), then `JOIN` it and filter with `WHERE p.price > cat_avg.avg_price`.


??? success "Answer"
    ```sql
    SELECT p.name, p.price, cat.name AS category, cat_avg.avg_price
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN (
        SELECT category_id, ROUND(AVG(price), 2) AS avg_price
        FROM products
        GROUP BY category_id
    ) AS cat_avg ON p.category_id = cat_avg.category_id
    WHERE p.price > cat_avg.avg_price
    ORDER BY p.price DESC
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | name | price | category | avg_price |
    |---|---|---|---|
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 | NVIDIA | 2,406,500.00 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 | NVIDIA | 2,406,500.00 |
    | Razer Blade 18 Black | 4,353,100.00 | Gaming Laptop | 2,684,477.78 |
    | Razer Blade 16 Silver | 3,702,900.00 | Gaming Laptop | 2,684,477.78 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 | Custom Build | 1,719,809.09 |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 | Gaming Laptop | 2,684,477.78 |
    | ASUS ROG Strix GT35 | 3,296,800.00 | Custom Build | 1,719,809.09 |


---


### 4. Find products with an average rating of 4.5 or higher but wh


Find products with an average rating of 4.5 or higher but whose total revenue is below the median (bottom 50%).


**Hint 1:** Calculate per-product average rating and revenue in a CTE, then filter by rating threshold and revenue below the overall average.


??? success "Answer"
    ```sql
    WITH product_stats AS (
        SELECT
            p.id,
            p.name,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM products AS p
        LEFT JOIN reviews AS r ON p.id = r.product_id
        LEFT JOIN order_items AS oi ON p.id = oi.product_id
        GROUP BY p.id, p.name
        HAVING COUNT(r.id) >= 3
    )
    SELECT name, avg_rating, ROUND(revenue, 2) AS revenue
    FROM product_stats
    WHERE avg_rating >= 4.5
      AND revenue < (SELECT AVG(revenue) FROM product_stats)
    ORDER BY avg_rating DESC;
    ```


    **Result** (top 7 of 10 rows)

    | name | avg_rating | revenue |
    |---|---|---|
    | be quiet! Dark Power 13 1000W | 5.00 | 22,268,000.00 |
    | Samsung DM500TDA Silver | 4.80 | 254,851,000.00 |
    | LG 27UQ85R White | 4.60 | 669,675,000.00 |
    | LG 32UN880 Ergo White | 4.56 | 2,101,132,800.00 |
    | WD Elements 2TB Black | 4.53 | 863,861,600.00 |
    | Windows 11 Home Black | 4.52 | 994,396,200.00 |
    | ASUS ExpertCenter PN65 Silver | 4.50 | 73,654,200.00 |


---


### 5. Classify orders by amount into tiers -- small (under 50K), m


Classify orders by amount into tiers -- small (under 50K), medium (50K-200K), large (200K-500K), premium (500K+) -- and find the count and ratio for each tier.


**Hint 1:** Classify tiers with `CASE WHEN total_amount < 50000 THEN 'Small' ...`, then `GROUP BY`. Calculate the ratio using the window function `SUM(COUNT(*)) OVER ()`.


??? success "Answer"
    ```sql
    SELECT
        CASE
            WHEN total_amount < 50000 THEN '소액 (5만 미만)'
            WHEN total_amount < 200000 THEN '중액 (5~20만)'
            WHEN total_amount < 500000 THEN '대액 (20~50만)'
            ELSE '고액 (50만 이상)'
        END AS tier,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct,
        ROUND(AVG(total_amount), 2) AS avg_amount
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY tier
    ORDER BY MIN(total_amount);
    ```


    **Result** (4 rows)

    | tier | cnt | pct | avg_amount |
    |---|---|---|---|
    | 소액 (5만 미만) | 2201 | 6.20 | 35,888.07 |
    | 중액 (5~20만) | 9333 | 26.10 | 117,617.99 |
    | 대액 (20~50만) | 7372 | 20.70 | 324,592.77 |
    | 고액 (50만 이상) | 16,792 | 47.00 | 1,945,613.63 |


---


### 6. Find customer-product combinations that are in a wishlist bu


Find customer-product combinations that are in a wishlist but have never been ordered.


**Hint 1:** Use `NOT EXISTS` with a correlated subquery to check if the customer has ever ordered that product.


??? success "Answer"
    ```sql
    SELECT
        c.name AS customer,
        p.name AS product,
        w.created_at AS wishlisted_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products AS p ON w.product_id = p.id
    WHERE NOT EXISTS (
        SELECT 1
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.customer_id = w.customer_id
          AND oi.product_id = w.product_id
          AND o.status NOT IN ('cancelled')
    )
    ORDER BY w.created_at DESC
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | customer | product | wishlisted_at |
    |---|---|---|
    | Olivia Watson | Jooyon Rionine Mini PC | 2025-12-30 19:11:10 |
    | Kyle Ferguson | Samsung Galaxy Book4 360 Black | 2025-12-30 17:42:08 |
    | James Mcgrath | TP-Link TL-SG108 | 2025-12-30 11:47:20 |
    | Nathaniel Martinez | Seagate IronWolf 4TB Black | 2025-12-30 10:41:18 |
    | Bryan Powers | SK hynix Platinum P41 2TB Black | 2025-12-30 10:16:54 |
    | Warren Olsen | TeamGroup T-Force Vulcan DDR5 32GB 52... | 2025-12-30 09:25:54 |
    | Alexander Logan | APC Back-UPS Pro Gaming BGM1500B Black | 2025-12-30 06:38:37 |


---


### 7. Find the count, average payment amount, and installment rati


Find the count, average payment amount, and installment ratio per card issuer.


**Hint 1:** Filter card payments with `WHERE method = 'card'`, then `GROUP BY card_issuer`. Calculate installment ratio with conditional aggregation using `CASE WHEN installment_months > 0`.


??? success "Answer"
    ```sql
    SELECT
        card_issuer,
        COUNT(*) AS tx_count,
        ROUND(AVG(amount), 2) AS avg_amount,
        ROUND(100.0 * SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS installment_pct
    FROM payments
    WHERE method = 'card'
      AND card_issuer IS NOT NULL
    GROUP BY card_issuer
    ORDER BY tx_count DESC;
    ```


    **Result** (7 rows)

    | card_issuer | tx_count | avg_amount | installment_pct |
    |---|---|---|---|
    | Visa | 5098 | 993,810.92 | 48.50 |
    | Mastercard | 4039 | 1,063,479.07 | 47.90 |
    | American Express | 2513 | 1,040,512.18 | 48.50 |
    | Discover | 1710 | 990,776.67 | 48.60 |
    | Capital One | 1377 | 961,365.07 | 48.50 |
    | Chase | 1252 | 991,999.22 | 47.60 |
    | Citi | 852 | 901,753.10 | 48.00 |


---


### 8. Find the count, resolution rate, and average processing time


Find the count, resolution rate, and average processing time per customer inquiry channel.


**Hint 1:** Aggregate with `GROUP BY channel`. Calculate resolution rate with `CASE WHEN status IN ('resolved','closed')` conditional counting. Processing time uses `JULIANDAY` difference.


??? success "Answer"
    ```sql
    SELECT
        channel,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN status IN ('resolved', 'closed') THEN 1 ELSE 0 END) / COUNT(*), 1) AS resolution_pct,
        ROUND(AVG(CASE
            WHEN resolved_at IS NOT NULL
            THEN JULIANDAY(resolved_at) - JULIANDAY(created_at)
        END), 1) AS avg_days
    FROM complaints
    GROUP BY channel
    ORDER BY total DESC;
    ```


    **Result** (5 rows)

    | channel | total | resolution_pct | avg_days |
    |---|---|---|---|
    | website | 1341 | 94.70 | 1.20 |
    | phone | 913 | 94.10 | 1.20 |
    | email | 796 | 95.40 | 1.20 |
    | chat | 583 | 95.50 | 1.20 |
    | kakao | 180 | 95.00 | 1.20 |


---


### 9. Find the name, review count, and wishlist count of customers


Find the name, review count, and wishlist count of customers who have both written reviews and added items to their wishlist.


**Hint 1:** Aggregate reviews and wishlists in separate subqueries, then `INNER JOIN` them together (only customers present in both).


??? success "Answer"
    ```sql
    SELECT
        c.name,
        r_cnt.review_count,
        w_cnt.wishlist_count
    FROM customers AS c
    INNER JOIN (
        SELECT customer_id, COUNT(*) AS review_count
        FROM reviews GROUP BY customer_id
    ) AS r_cnt ON c.id = r_cnt.customer_id
    INNER JOIN (
        SELECT customer_id, COUNT(*) AS wishlist_count
        FROM wishlists GROUP BY customer_id
    ) AS w_cnt ON c.id = w_cnt.customer_id
    ORDER BY r_cnt.review_count DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | review_count | wishlist_count |
    |---|---|---|
    | Jason Rivera | 72 | 2 |
    | Courtney Huff | 63 | 1 |
    | James Banks | 59 | 1 |
    | Lisa Chambers | 45 | 2 |
    | Austin Townsend | 43 | 1 |
    | April Rasmussen | 40 | 1 |
    | David York | 37 | 1 |


---


### 10. Find the image count per product, including products with no


Find the image count per product, including products with no images.


**Hint 1:** `products LEFT JOIN product_images` to include products without images. `COUNT(pi.id)` doesn't count NULLs, so it returns 0.


??? success "Answer"
    ```sql
    SELECT
        p.name,
        COUNT(pi.id) AS image_count,
        SUM(CASE WHEN pi.is_primary = 1 THEN 1 ELSE 0 END) AS has_primary
    FROM products AS p
    LEFT JOIN product_images AS pi ON p.id = pi.product_id
    GROUP BY p.id, p.name
    ORDER BY image_count ASC
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | name | image_count | has_primary |
    |---|---|---|
    | ASRock B850M Pro RS Silver | 1 | 1 |
    | ASRock Z890 Taichi Black | 1 | 1 |
    | ASUS Dual RTX 4060 Ti Black | 1 | 1 |
    | ASUS ROG Strix G16CH White | 1 | 1 |
    | ASUS ROG Swift OLED PG27AQDM Silver | 1 | 1 |
    | Arctic Liquid Freezer III 240 | 1 | 1 |
    | Arctic Liquid Freezer III Pro 420 A-R... | 1 | 1 |


---


### 11. Find the count and percentage per cart status (active/conver


Find the count and percentage per cart status (active/converted/abandoned).


**Hint 1:** Aggregate with `GROUP BY status`. Calculate the ratio with `100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()`.


??? success "Answer"
    ```sql
    SELECT
        status,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM carts
    GROUP BY status
    ORDER BY cnt DESC;
    ```


    **Result** (3 rows)

    | status | cnt | pct |
    |---|---|---|
    | converted | 1486 | 49.50 |
    | abandoned | 899 | 30.00 |
    | active | 615 | 20.50 |


---


### 12. Combine order cancellation events and return request events 


Combine order cancellation events and return request events into a single timeline. Show the 20 most recent.


**Hint 1:** Combine two SELECTs with `UNION ALL`, matching the number and meaning of columns. Add an event type column to distinguish them.


??? success "Answer"
    ```sql
    SELECT '취소' AS event_type, order_number AS reference, cancelled_at AS event_date
    FROM orders
    WHERE status = 'cancelled' AND cancelled_at IS NOT NULL
    UNION ALL
    SELECT '반품' AS event_type, CAST(order_id AS TEXT), requested_at
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
