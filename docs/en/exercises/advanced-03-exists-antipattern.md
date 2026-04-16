# EXISTS and Anti-Patterns

!!! info "Tables"

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `reviews` — Reviews (rating, content)  

    `wishlists` — Wishlists (customer-product)  

    `complaints` — Complaints (type, priority)  

    `categories` — Categories (parent-child hierarchy)  

    `payments` — Payments (method, amount, status)  



!!! abstract "Concepts"

    `EXISTS`, `NOT EXISTS`, `Correlated Subquery`, `Anti-join Pattern`, `Universal Quantification`, `Double Negation`



### 1. Check only customers who have placed an order in 2024.


Displays customer ID, name, level, and subscription date. Use `EXISTS`.


**Hint 1:** `WHERE EXISTS (SELECT 1 FROM orders WHERE customer_id = c.id AND ...)`
A subquery that references `c.id` of the outer query is a correlated subquery.



??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        c.created_at AS signup_date
    FROM customers AS c
    WHERE EXISTS (
        SELECT 1
        FROM orders AS o
        WHERE o.customer_id = c.id
          AND o.ordered_at LIKE '2024%'
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    ORDER BY c.id
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | id | name | grade | signup_date |
    |---|---|---|---|
    | 2 | Danny Johnson | GOLD | 2016-08-17 12:29:34 |
    | 3 | Adam Moore | VIP | 2016-02-11 19:59:38 |
    | 4 | Virginia Steele | GOLD | 2016-09-18 15:29:45 |
    | 5 | Jared Vazquez | SILVER | 2016-02-28 11:34:16 |
    | 8 | Tyler Rodriguez | SILVER | 2016-09-24 06:49:22 |
    | 10 | John Stark | GOLD | 2016-12-20 04:06:43 |
    | 12 | Michael Velasquez | GOLD | 2016-12-30 06:48:08 |


---


### 2. Find customers who have never placed an order.


This is a customer who has only registered but has no order history. Use `NOT EXISTS`.


**Hint 1:** `WHERE NOT EXISTS (SELECT 1 FROM orders WHERE customer_id = c.id)`
At this time, canceled/returned orders are also considered “placed” (no status filter).



??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        c.created_at AS signup_date,
        ROUND(JULIANDAY('2025-12-31') - JULIANDAY(c.created_at), 0) AS days_since_signup
    FROM customers AS c
    WHERE NOT EXISTS (
        SELECT 1
        FROM orders AS o
        WHERE o.customer_id = c.id
    )
    ORDER BY c.created_at
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | id | name | grade | signup_date | days_since_signup |
    |---|---|---|---|---|
    | 84 | Alan Blair | BRONZE | 2016-01-03 19:49:46 | 3,649.00 |
    | 38 | Dana Miles | BRONZE | 2016-01-15 19:21:20 | 3,637.00 |
    | 9 | Tracy Johnson | BRONZE | 2016-01-26 09:42:20 | 3,627.00 |
    | 69 | Tommy Kim | BRONZE | 2016-02-03 03:40:29 | 3,619.00 |
    | 25 | Sara Harvey | BRONZE | 2016-02-03 04:18:52 | 3,619.00 |
    | 32 | Duane Evans MD | BRONZE | 2016-02-09 18:54:54 | 3,612.00 |
    | 7 | Ashley Jones | BRONZE | 2016-02-17 13:41:08 | 3,604.00 |


---


### 3. Find verified customers who have not left a review.


Customers who have orders with an order status of 'confirmed' but who have not written a single review.


**Hint 1:** Combine 2 conditions:
`EXISTS (... orders WHERE status = 'confirmed')` AND
`NOT EXISTS (... reviews WHERE customer_id = c.id)`.



??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(o.id) AS confirmed_orders
    FROM customers AS c
    INNER JOIN orders AS o
        ON c.id = o.customer_id
       AND o.status = 'confirmed'
    WHERE NOT EXISTS (
        SELECT 1
        FROM reviews AS r
        WHERE r.customer_id = c.id
    )
    GROUP BY c.id, c.name, c.grade
    ORDER BY confirmed_orders DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | id | name | grade | confirmed_orders |
    |---|---|---|---|
    | 494 | Amanda Smith | GOLD | 20 |
    | 124 | Paul Wilson | BRONZE | 13 |
    | 1207 | Kevin Garcia | SILVER | 12 |
    | 1620 | Alexander Aguirre | BRONZE | 12 |
    | 2164 | Kristy Nguyen | SILVER | 12 |
    | 2236 | Kayla Davis | BRONZE | 12 |
    | 2487 | Larry Kim | BRONZE | 12 |


---


### 4. Find product-customer combinations that have been added to their wishlist but have not yet been purchased.


Among the `is_purchased = 0` items in the wishlist, the customer has never actually ordered the product.


**Hint 1:** Based on `wishlists`, create a subquery combining `order_items` and `orders` with `NOT EXISTS`.
Subquery condition: equal to `customer_id` and equal to `product_id`.



??? success "Answer"
    ```sql
    SELECT
        w.customer_id,
        c.name     AS customer_name,
        w.product_id,
        p.name     AS product_name,
        p.price,
        w.created_at AS wishlisted_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products  AS p ON w.product_id  = p.id
    WHERE w.is_purchased = 0
      AND NOT EXISTS (
          SELECT 1
          FROM order_items AS oi
          INNER JOIN orders AS o ON oi.order_id = o.id
          WHERE o.customer_id = w.customer_id
            AND oi.product_id = w.product_id
            AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
      )
    ORDER BY w.created_at DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | customer_id | customer_name | product_id | product_name | price | wishlisted_at |
    |---|---|---|---|---|---|
    | 4853 | Olivia Watson | 92 | Jooyon Rionine Mini PC | 1,194,000.00 | 2025-12-30 19:11:10 |
    | 5229 | Kyle Ferguson | 223 | Samsung Galaxy Book4 360 Black | 1,388,600.00 | 2025-12-30 17:42:08 |
    | 4675 | James Mcgrath | 271 | TP-Link TL-SG108 | 108,500.00 | 2025-12-30 11:47:20 |
    | 4940 | Nathaniel Martinez | 191 | Seagate IronWolf 4TB Black | 545,400.00 | 2025-12-30 10:41:18 |
    | 3584 | Bryan Powers | 194 | SK hynix Platinum P41 2TB Black | 237,500.00 | 2025-12-30 10:16:54 |
    | 4546 | Warren Olsen | 239 | TeamGroup T-Force Vulcan DDR5 32GB 52... | 139,800.00 | 2025-12-30 09:25:54 |
    | 4796 | Alexander Logan | 171 | APC Back-UPS Pro Gaming BGM1500B Black | 516,300.00 | 2025-12-30 06:38:37 |


---


### 5. Find the top 10 customers by order amount who have never received a CS inquiry.


Identify “blue-chip customers” who consistently purchase without making a claim.


**Hint 1:** Filter customers with no inquiry history with `NOT EXISTS (SELECT 1 FROM complaints WHERE customer_id = c.id)`,
Extract the top 10 users by total purchase amount with `SUM(total_amount)`.



??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      AND NOT EXISTS (
          SELECT 1
          FROM complaints AS cp
          WHERE cp.customer_id = c.id
      )
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | id | name | grade | order_count | total_spent |
    |---|---|---|---|---|
    | 514 | Steven Johnson | BRONZE | 5 | 52,141,700.00 |
    | 3000 | Michelle King | GOLD | 47 | 51,674,714.00 |
    | 4065 | Nicole Perry | VIP | 12 | 43,306,619.00 |
    | 41 | David Harper | BRONZE | 34 | 42,490,481.00 |
    | 44 | Melinda Lang | BRONZE | 45 | 40,153,649.00 |
    | 4136 | Zachary Ford | VIP | 4 | 39,557,863.00 |
    | 1131 | Victoria Lee | SILVER | 36 | 39,097,438.00 |


---


### 6. Find customers who purchased products from 3 or more different categories


EXISTS uses aggregates internally.


**Hint 1:** Use `GROUP BY customer_id HAVING COUNT(DISTINCT category_id) >= 3` within `EXISTS`.
Alternatively, you can count the number of categories with a correlated subquery.



??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade
    FROM customers AS c
    WHERE EXISTS (
        SELECT 1
        FROM order_items AS oi
        INNER JOIN orders   AS o ON oi.order_id   = o.id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.customer_id = c.id
          AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY o.customer_id
        HAVING COUNT(DISTINCT p.category_id) >= 3
    )
    ORDER BY c.grade DESC, c.name
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | id | name | grade |
    |---|---|---|
    | 4233 | Abigail Richardson | VIP |
    | 2066 | Adam Johnson | VIP |
    | 3 | Adam Moore | VIP |
    | 2650 | Adrienne Phillips | VIP |
    | 3585 | Aimee Norman | VIP |
    | 1746 | Alan Cruz | VIP |
    | 1516 | Alan Newman | VIP |


---


### 7. Only view orders for which all payments have been completed successfully.


There may be multiple payments in one order. Find orders that do not have any failed (`failed`) or refunded (`refunded`) payments.


**Hint 1:** "Failure/No refund" = `NOT EXISTS (... payments WHERE status IN ('failed', 'refunded') AND order_id = o.id)`.
Additionally, at least one payment must exist (`EXISTS`).



??? success "Answer"
    ```sql
    SELECT
        o.id,
        o.order_number,
        o.total_amount,
        o.ordered_at,
        o.status
    FROM orders AS o
    WHERE EXISTS (
        SELECT 1
        FROM payments AS p
        WHERE p.order_id = o.id
          AND p.status = 'completed'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM payments AS p
        WHERE p.order_id = o.id
          AND p.status IN ('failed', 'refunded')
    )
    AND o.ordered_at LIKE '2024%'
    ORDER BY o.ordered_at DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | id | order_number | total_amount | ordered_at | status |
    |---|---|---|---|---|
    | 31,230 | ORD-20241231-31230 | 506,700.00 | 2024-12-31 21:25:24 | confirmed |
    | 31,229 | ORD-20241231-31229 | 425,600.00 | 2024-12-31 20:47:26 | confirmed |
    | 31,228 | ORD-20241231-31228 | 548,900.00 | 2024-12-31 20:17:42 | confirmed |
    | 31,223 | ORD-20241231-31223 | 531,300.00 | 2024-12-31 19:30:18 | confirmed |
    | 31,226 | ORD-20241231-31226 | 500,100.00 | 2024-12-31 19:28:26 | confirmed |
    | 31,238 | ORD-20241231-31238 | 658,500.00 | 2024-12-31 16:08:40 | confirmed |
    | 31,236 | ORD-20241231-31236 | 144,100.00 | 2024-12-31 15:52:45 | confirmed |


---


### 8. Find products that are frequently purchased together with a specific product (ID=1) (simultaneous purchase analysis).


In orders containing product 1, items other than product 1 are sorted in order of frequency of simultaneous purchase.


**Hint 1:** The outer query aggregates items from `order_items` to `product_id != 1`.
`EXISTS` checks whether “the order contains product 1”.



??? success "Answer"
    ```sql
    SELECT
        p.id    AS product_id,
        p.name  AS product_name,
        p.price,
        COUNT(DISTINCT oi.order_id) AS co_purchase_count
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    WHERE oi.product_id != 1
      AND EXISTS (
          SELECT 1
          FROM order_items AS oi2
          WHERE oi2.order_id   = oi.order_id
            AND oi2.product_id = 1
      )
    GROUP BY p.id, p.name, p.price
    ORDER BY co_purchase_count DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | product_id | product_name | price | co_purchase_count |
    |---|---|---|---|
    | 45 | SteelSeries Aerox 5 Wireless Silver | 100,000.00 | 33 |
    | 70 | JBL Pebbles 2 Black | 101,500.00 | 31 |
    | 9 | Sony WH-CH720N Silver | 445,700.00 | 30 |
    | 28 | Keychron Q1 Pro Silver | 238,000.00 | 26 |
    | 8 | Logitech G715 White | 131,500.00 | 25 |
    | 34 | SteelSeries Prime Wireless Black | 89,800.00 | 25 |
    | 111 | Logitech G502 X PLUS | 97,500.00 | 24 |


---


### 9. Find “customers who ordered every month” (12 months to 2024).


Customers with at least 1 order in any 12 months in 2024.


**Hint 1:** Combines `NOT EXISTS` with a recursive CTE (or a hardcoded list of months).
“Every month has orders” = “There is no month without orders” (NOT EXISTS).



??? success "Answer"
    ```sql
    WITH RECURSIVE months AS (
        SELECT '2024-01' AS ym
        UNION ALL
        SELECT SUBSTR(DATE(ym || '-01', '+1 month'), 1, 7)
        FROM months
        WHERE ym < '2024-12'
    )
    SELECT
        c.id,
        c.name,
        c.grade
    FROM customers AS c
    WHERE NOT EXISTS (
        -- 주문이 없는 월이 하나라도 있으면 제외
        SELECT 1
        FROM months AS m
        WHERE NOT EXISTS (
            SELECT 1
            FROM orders AS o
            WHERE o.customer_id = c.id
              AND SUBSTR(o.ordered_at, 1, 7) = m.ym
              AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
        )
    )
    ORDER BY c.grade DESC, c.name;
    ```


    **Result** (3 rows)

    | id | name | grade |
    |---|---|---|
    | 3097 | Christina Jennings | VIP |
    | 2516 | Joseph Kirby | VIP |
    | 3775 | Katherine Garner | VIP |


---


### 10. Look for “churn customers” who ordered in 2024 but not in 2025.


Combines two EXISTS/NOT EXISTS conditions.


**Hint 1:** `EXISTS (... 2024년 주문)` AND `NOT EXISTS (... 2025년 주문)`.
It would be useful to also display the churn customer's last order date in 2024 and their total purchase amount.



??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order_date,
        COUNT(o.id) AS orders_in_2024,
        ROUND(SUM(o.total_amount), 0) AS spent_in_2024
    FROM customers AS c
    INNER JOIN orders AS o
        ON c.id = o.customer_id
       AND o.ordered_at LIKE '2024%'
       AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    WHERE NOT EXISTS (
        SELECT 1
        FROM orders AS o2
        WHERE o2.customer_id = c.id
          AND o2.ordered_at LIKE '2025%'
          AND o2.status NOT IN ('cancelled', 'returned', 'return_requested')
    )
    GROUP BY c.id, c.name, c.grade
    ORDER BY spent_in_2024 DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | id | name | grade | last_order_date | orders_in_2024 | spent_in_2024 |
    |---|---|---|---|---|---|
    | 2623 | Carolyn Smith | BRONZE | 2024-09-18 20:22:57 | 4 | 17,088,500.00 |
    | 2894 | Krista Martinez | BRONZE | 2024-05-24 09:44:28 | 1 | 14,204,200.00 |
    | 1724 | Amy Stephenson | BRONZE | 2024-08-03 08:13:36 | 3 | 12,494,600.00 |
    | 3667 | Steven Gonzalez | BRONZE | 2024-12-10 12:12:19 | 2 | 12,260,100.00 |
    | 1186 | Mary Harris | BRONZE | 2024-10-24 20:05:01 | 3 | 9,588,499.00 |
    | 2814 | Beth Newman | BRONZE | 2024-08-26 20:19:31 | 2 | 8,290,525.00 |
    | 2236 | Kayla Davis | BRONZE | 2024-11-21 11:34:35 | 4 | 7,629,400.00 |


---


### 11. Find customers who only paid by card on all orders


This is a customer who has never used a payment method other than a card (kakao_pay, naver_pay, bank_transfer, etc.).


**Hint 1:** Nickname only: "All payments are by card" = "No non-card payments **exist**".
Use `NOT EXISTS (... payments WHERE method != 'card' ...)`.
Only customers with an order history are eligible.



??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      -- 카드가 아닌 결제가 한 건도 없어야 함
      AND NOT EXISTS (
          SELECT 1
          FROM payments AS p
          INNER JOIN orders AS o2 ON p.order_id = o2.id
          WHERE o2.customer_id = c.id
            AND p.method != 'card'
      )
      -- 결제 이력이 있어야 함
      AND EXISTS (
          SELECT 1
          FROM payments AS p
          INNER JOIN orders AS o3 ON p.order_id = o3.id
          WHERE o3.customer_id = c.id
            AND p.method = 'card'
      )
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | id | name | grade | order_count | total_spent |
    |---|---|---|---|---|
    | 4213 | Christine Johnson | VIP | 1 | 13,895,400.00 |
    | 4179 | Troy Carr | VIP | 1 | 8,319,100.00 |
    | 3138 | Alison Gilmore | GOLD | 4 | 6,843,700.00 |
    | 2027 | Calvin Hernandez | BRONZE | 2 | 6,285,000.00 |
    | 3785 | William Morris | GOLD | 4 | 5,791,400.00 |
    | 1120 | Elizabeth Leon | BRONZE | 5 | 5,519,100.00 |
    | 2119 | Jose Hart | BRONZE | 3 | 5,265,400.00 |


---


### 12. Find customers who have experienced “all types of inquiry categories”


Customers who have submitted at least one inquiry for every `category` value in the `complaints` table.


**Hint 1:** Double negation pattern for prequalification:
"There are inquiries in all categories" = "There is **no category** in which there are no inquiries."
`NOT EXISTS (SELECT category FROM (SELECT DISTINCT category FROM complaints) WHERE NOT EXISTS (... 해당 고객의 해당 카테고리 문의))`.



??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        (SELECT COUNT(DISTINCT cp.category) FROM complaints AS cp WHERE cp.customer_id = c.id) AS category_count
    FROM customers AS c
    WHERE NOT EXISTS (
        -- 문의가 없는 카테고리가 하나라도 있으면 제외
        SELECT DISTINCT cp_all.category
        FROM complaints AS cp_all
        WHERE NOT EXISTS (
            SELECT 1
            FROM complaints AS cp
            WHERE cp.customer_id = c.id
              AND cp.category = cp_all.category
        )
    )
    ORDER BY c.name;
    ```


    **Result** (top 7 of 8 rows)

    | id | name | grade | category_count |
    |---|---|---|---|
    | 744 | Debra Mosley | VIP | 7 |
    | 98 | Gabriel Walters | VIP | 7 |
    | 97 | Jason Rivera | VIP | 7 |
    | 549 | Ronald Arellano | VIP | 7 |
    | 489 | Roy Fernandez | VIP | 7 |
    | 258 | Sandra Callahan | GOLD | 7 |
    | 1388 | Sandra Deleon | VIP | 7 |


---


### 13. Find customers who “only purchased products priced over 1 million won”


These are premium customers who have never purchased a low-priced product.


**Hint 1:** “There is no purchase of products under 1 million won”:
`NOT EXISTS (... order_items JOIN products WHERE price < 1000000 AND customer_id = c.id)`.
At the same time, there must be an order history (`EXISTS`).



??? success "Answer"
    ```sql
    SELECT
        c.id,
        c.name,
        c.grade,
        COUNT(DISTINCT o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent,
        ROUND(AVG(o.total_amount), 0) AS avg_order_value
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      -- 100만원 미만 상품 구매가 없어야 함
      AND NOT EXISTS (
          SELECT 1
          FROM order_items AS oi
          INNER JOIN orders AS o2 ON oi.order_id = o2.id
          INNER JOIN products AS p ON oi.product_id = p.id
          WHERE o2.customer_id = c.id
            AND p.price < 1000000
            AND o2.status NOT IN ('cancelled', 'returned', 'return_requested')
      )
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```


    **Result** (2 rows)

    | id | name | grade | order_count | total_spent | avg_order_value |
    |---|---|---|---|---|---|
    | 4137 | Robert Mckee | BRONZE | 1 | 4,352,405.00 | 4,352,405.00 |
    | 4973 | Terry Young | SILVER | 1 | 1,204,536.00 | 1,204,536.00 |


---


### 14. Find repeat product pairs — where the same customer has purchased the same product more than once in different orders.


EXISTS checks for “same customer, same product, different orders”.


**Hint 1:** Based on `order_items`, `EXISTS` is the same as `product_id`, and `customer_id` is the same.
Check if there is another record with `order_id`.
Counts the number of repeat purchases by customer-product combination.



??? success "Answer"
    ```sql
    SELECT
        c.name     AS customer_name,
        p.name     AS product_name,
        COUNT(DISTINCT oi.order_id) AS purchase_count,
        SUM(oi.quantity) AS total_qty
    FROM order_items AS oi
    INNER JOIN orders    AS o ON oi.order_id   = o.id
    INNER JOIN customers AS c ON o.customer_id = c.id
    INNER JOIN products  AS p ON oi.product_id = p.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
      AND EXISTS (
          -- 같은 고객이 같은 상품을 다른 주문에서 구매
          SELECT 1
          FROM order_items AS oi2
          INNER JOIN orders AS o2 ON oi2.order_id = o2.id
          WHERE o2.customer_id = o.customer_id
            AND oi2.product_id = oi.product_id
            AND oi2.order_id   != oi.order_id
            AND o2.status NOT IN ('cancelled', 'returned', 'return_requested')
      )
    GROUP BY c.id, c.name, p.id, p.name
    ORDER BY purchase_count DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | customer_name | product_name | purchase_count | total_qty |
    |---|---|---|---|
    | Gabriel Walters | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | 37 | 37 |
    | Gabriel Walters | Samsung Odyssey G7 32 White | 25 | 25 |
    | Gabriel Walters | Samsung DDR5 32GB PC5-38400 | 24 | 24 |
    | Jason Rivera | Samsung DDR4 32GB PC4-25600 | 23 | 30 |
    | Jason Rivera | be quiet! Light Base 900 | 22 | 28 |
    | Jason Rivera | AMD Ryzen 9 9900X | 22 | 22 |
    | Jason Rivera | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | 21 | 21 |


---


### 15. Compare "NOT EXISTS vs LEFT JOIN IS NULL" anti-join patterns.


Look for products that haven't left reviews in 2024 in two ways and see if the results are the same.


**Hint 1:** Method 1: `NOT EXISTS (SELECT 1 FROM reviews WHERE product_id = p.id AND created_at LIKE '2024%')`.
Method 2: `LEFT JOIN reviews ON ... WHERE r.id IS NULL`.
If you compare two queries with `EXCEPT`, the difference must be empty.



??? success "Answer"
    ```sql
    -- 방법 1: NOT EXISTS
    SELECT p.id, p.name
    FROM products AS p
    WHERE p.is_active = 1
      AND NOT EXISTS (
          SELECT 1
          FROM reviews AS r
          WHERE r.product_id = p.id
            AND r.created_at LIKE '2024%'
      )
    ORDER BY p.id;
    
    -- 방법 2: LEFT JOIN ... IS NULL
    SELECT p.id, p.name
    FROM products AS p
    LEFT JOIN reviews AS r
        ON r.product_id = p.id
       AND r.created_at LIKE '2024%'
    WHERE p.is_active = 1
      AND r.id IS NULL
    ORDER BY p.id;
    
    -- 동일성 검증: 차집합이 비어야 함
    SELECT p.id, p.name
    FROM products AS p
    WHERE p.is_active = 1
      AND NOT EXISTS (
          SELECT 1 FROM reviews AS r
          WHERE r.product_id = p.id AND r.created_at LIKE '2024%'
      )
    
    EXCEPT
    
    SELECT p.id, p.name
    FROM products AS p
    LEFT JOIN reviews AS r
        ON r.product_id = p.id AND r.created_at LIKE '2024%'
    WHERE p.is_active = 1
      AND r.id IS NULL;
    ```


---
