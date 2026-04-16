# Mastering Subqueries

!!! info "Tables"

    `products` — Products (name, price, stock, brand)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `reviews` — Reviews (rating, content)  

    `wishlists` — Wishlists (customer-product)  

    `categories` — Categories (parent-child hierarchy)  

    `payments` — Payments (method, amount, status)  



!!! abstract "Concepts"

    `scalar subquery`, `IN`, `NOT IN`, `EXISTS`, `NOT EXISTS`, `FROM clause subquery`, `correlated subquery`



### 1. Find products whose price is higher than the overall average


Find products whose price is higher than the overall average price. Sort by price descending, top 10.


**Hint 1:** Use a scalar subquery in the form `WHERE price > (SELECT AVG(price) FROM products)`.


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products)
    ORDER BY price DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

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


### 2. Find the name, price, and category ID of the most expensive 


Find the name, price, and category ID of the most expensive product.


**Hint 1:** Use the form `WHERE price = (SELECT MAX(price) FROM products)` to get the maximum value via subquery.


??? success "Answer"
    ```sql
    SELECT name, price, category_id
    FROM products
    WHERE price = (SELECT MAX(price) FROM products);
    ```


    **Result** (1 rows)

    | name | price | category_id |
    |---|---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 | 9 |


---


### 3. Find the name and email of customers who have placed at leas


Find the name and email of customers who have placed at least one order. Sort by name, top 15.


**Hint 1:** `WHERE id IN (SELECT customer_id FROM orders)` — the subquery returns the list of customer IDs that have orders.


??? success "Answer"
    ```sql
    SELECT name, email
    FROM customers
    WHERE id IN (SELECT customer_id FROM orders)
    ORDER BY name
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | email |
    |---|---|
    | Aaron Carr | user900@testmail.kr |
    | Aaron Cooper | user3587@testmail.kr |
    | Aaron Fuller | user2520@testmail.kr |
    | Aaron Gillespie | user3365@testmail.kr |
    | Aaron Green | user417@testmail.kr |
    | Aaron Grimes | user347@testmail.kr |
    | Aaron Harris | user1884@testmail.kr |


---


### 4. Find the name and grade of customers who have never written 


Find the name and grade of customers who have never written a review. Sort by grade descending, then by name, top 15.


**Hint 1:** `WHERE id NOT IN (SELECT customer_id FROM reviews)` — finds customers not in the reviews table.


??? success "Answer"
    ```sql
    SELECT name, grade
    FROM customers
    WHERE id NOT IN (SELECT customer_id FROM reviews)
    ORDER BY
        CASE grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            ELSE 4
        END,
        name
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | grade |
    |---|---|
    | Alex Gomez | VIP |
    | Andrew Thompson | VIP |
    | Brenda Nichols | VIP |
    | Chad Wyatt | VIP |
    | Christine Floyd | VIP |
    | David Caldwell | VIP |
    | David Levy | VIP |


---


### 5. Find products that have been added to a wishlist at least on


Find products that have been added to a wishlist at least once, showing name and price. Sort by price descending, top 10.


**Hint 1:** `WHERE id IN (SELECT product_id FROM wishlists)` — gets product IDs that have been wishlisted at least once.


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE id IN (SELECT product_id FROM wishlists)
    ORDER BY price DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | price |
    |---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 |
    | Razer Blade 18 Black | 4,353,100.00 |
    | Razer Blade 16 Silver | 3,702,900.00 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 |
    | ASUS ROG Strix GT35 | 3,296,800.00 |
    | Razer Blade 18 Black | 2,987,500.00 |


---


### 6. Find products that have never been ordered, showing name and


Find products that have never been ordered, showing name and stock quantity.


**Hint 1:** `WHERE id NOT IN (SELECT product_id FROM order_items)` — filters for products not in order details.


??? success "Answer"
    ```sql
    SELECT name, stock_qty
    FROM products
    WHERE id NOT IN (SELECT product_id FROM order_items)
    ORDER BY stock_qty DESC;
    ```


    **Result** (1 rows)

    | name | stock_qty |
    |---|---|
    | FK 테스트 | 10 |


---


### 7. Find orders with amounts greater than the average. Exclude c


Find orders with amounts greater than the average. Exclude cancelled. Sort by amount descending, top 10.


**Hint 1:** Both the main query and the subquery should exclude cancelled orders for a fair comparison.


??? success "Answer"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE status NOT IN ('cancelled')
      AND total_amount > (
          SELECT AVG(total_amount)
          FROM orders
          WHERE status NOT IN ('cancelled')
      )
    ORDER BY total_amount DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | order_number | total_amount | ordered_at |
    |---|---|---|
    | ORD-20201121-08810 | 50,867,500.00 | 2020-11-21 12:04:42 |
    | ORD-20250305-32265 | 46,820,024.00 | 2025-03-05 09:01:08 |
    | ORD-20200209-05404 | 43,677,500.00 | 2020-02-09 23:36:36 |
    | ORD-20251218-37240 | 38,626,400.00 | 2025-12-18 17:09:12 |
    | ORD-20220106-15263 | 37,987,600.00 | 2022-01-06 17:24:14 |
    | ORD-20200820-07684 | 37,518,200.00 | 2020-08-20 19:00:29 |
    | ORD-20220224-15869 | 35,397,700.00 | 2022-02-24 23:01:50 |


---


### 8. Find the average price per category, then find products more


Find the average price per category, then find products more expensive than their category average. Top 15.


**Hint 1:** JOIN the inline view like a table using `FROM products AS p INNER JOIN (SELECT ...) AS ca ON ...`.


??? success "Answer"
    ```sql
    SELECT p.name, p.price, ca.avg_price
    FROM products AS p
    INNER JOIN (
        SELECT category_id, ROUND(AVG(price), 2) AS avg_price
        FROM products
        GROUP BY category_id
    ) AS ca ON p.category_id = ca.category_id
    WHERE p.price > ca.avg_price
    ORDER BY p.price DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | price | avg_price |
    |---|---|---|
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 | 2,406,500.00 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 | 2,406,500.00 |
    | Razer Blade 18 Black | 4,353,100.00 | 2,684,477.78 |
    | Razer Blade 16 Silver | 3,702,900.00 | 2,684,477.78 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 | 1,719,809.09 |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 | 2,684,477.78 |
    | ASUS ROG Strix GT35 | 3,296,800.00 | 1,719,809.09 |


---


### 9. Use a SELECT clause scalar subquery to compute each customer


Use a SELECT clause scalar subquery to compute each customer's order count. Show only customers with 3+ orders, top 15.


**Hint 1:** References the outer query's `c.id` in the subquery.


??? success "Answer"
    ```sql
    SELECT
        c.name,
        c.grade,
        (SELECT COUNT(*)
         FROM orders
         WHERE customer_id = c.id
           AND status NOT IN ('cancelled')) AS order_count
    FROM customers AS c
    WHERE (SELECT COUNT(*)
           FROM orders
           WHERE customer_id = c.id
             AND status NOT IN ('cancelled')) >= 3
    ORDER BY order_count DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | grade | order_count |
    |---|---|---|
    | Jason Rivera | VIP | 352 |
    | Allen Snyder | VIP | 312 |
    | Gabriel Walters | VIP | 290 |
    | Brenda Garcia | VIP | 250 |
    | James Banks | VIP | 236 |
    | Courtney Huff | VIP | 226 |
    | Ronald Arellano | VIP | 225 |


---


### 10. Use a correlated subquery to retrieve each product's most re


Use a correlated subquery to retrieve each product's most recent review date. Top 15.


**Hint 1:** `(SELECT MAX(created_at) FROM reviews WHERE product_id = p.id)` — a correlated subquery referencing the outer query's `p.id`.


??? success "Answer"
    ```sql
    SELECT
        p.name,
        p.price,
        (SELECT MAX(created_at)
         FROM reviews
         WHERE product_id = p.id) AS last_review_at
    FROM products AS p
    ORDER BY last_review_at DESC NULLS LAST
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | price | last_review_at |
    |---|---|---|
    | Kingston FURY Beast DDR4 32GB Black | 83,300.00 | 2026-01-19 09:22:49 |
    | Super Flower Leadex VII XG 850W White | 71,200.00 | 2026-01-14 10:58:04 |
    | Samsung DDR4 16GB PC4-25600 | 83,400.00 | 2026-01-13 12:39:53 |
    | Norton AntiVirus Plus Silver | 74,800.00 | 2026-01-13 12:09:18 |
    | Razer DeathAdder V4 Pro White | 52,500.00 | 2026-01-12 10:35:41 |
    | Netgear GS308 Silver | 194,800.00 | 2026-01-11 21:02:15 |
    | CORSAIR HX1200 Silver | 122,200.00 | 2026-01-11 15:23:03 |


---


### 11. Use a FROM subquery to compute total order amount per custom


Use a FROM subquery to compute total order amount per customer, then show the top 10.


**Hint 1:** Use the derived table with an alias.


??? success "Answer"
    ```sql
    SELECT c.name, c.grade, os.total_spent
    FROM customers AS c
    INNER JOIN (
        SELECT customer_id, ROUND(SUM(total_amount), 2) AS total_spent
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ) AS os ON c.id = os.customer_id
    ORDER BY os.total_spent DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | grade | total_spent |
    |---|---|---|
    | Allen Snyder | VIP | 409,734,279.00 |
    | Jason Rivera | VIP | 382,314,874.00 |
    | Ronald Arellano | VIP | 266,184,349.00 |
    | Brenda Garcia | VIP | 254,525,838.00 |
    | Courtney Huff | VIP | 248,498,783.00 |
    | Gabriel Walters | VIP | 248,168,491.00 |
    | James Banks | VIP | 244,859,844.00 |


---


### 12. Use EXISTS to find only products that have at least one revi


Use EXISTS to find only products that have at least one review. Sort by name, top 15.


**Hint 1:** `WHERE EXISTS (SELECT 1 FROM reviews WHERE product_id = p.id)` — returns TRUE if the subquery returns at least one row.


??? success "Answer"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    WHERE EXISTS (
        SELECT 1
        FROM reviews
        WHERE product_id = p.id
    )
    ORDER BY p.name
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | price |
    |---|---|
    | AMD Ryzen 9 9900X | 335,700.00 |
    | AMD Ryzen 9 9900X | 591,800.00 |
    | APC Back-UPS Pro Gaming BGM1500B Black | 516,300.00 |
    | ASRock B850M Pro RS Black | 201,000.00 |
    | ASRock B850M Pro RS Silver | 665,600.00 |
    | ASRock B850M Pro RS White | 419,600.00 |
    | ASRock B860M Pro RS Silver | 351,700.00 |


---


### 13. Find customer-product combinations that were wishlisted but 


Find customer-product combinations that were wishlisted but never ordered. Most recent 20.


**Hint 1:** A correlated subquery checking two conditions simultaneously.


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


### 14. Find the most expensive product in each category, showing na


Find the most expensive product in each category, showing name and price.


**Hint 1:** Computes the max price within the same category via correlated subquery.


??? success "Answer"
    ```sql
    SELECT p.name, p.price, p.category_id
    FROM products AS p
    WHERE p.price = (
        SELECT MAX(price)
        FROM products
        WHERE category_id = p.category_id
    )
    ORDER BY p.price DESC;
    ```


    **Result** (top 7 of 41 rows)

    | name | price | category_id |
    |---|---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 | 9 |
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 | 28 |
    | Razer Blade 18 Black | 4,353,100.00 | 7 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 | 3 |
    | ASUS ExpertBook B5 [Special Limited E... | 2,121,600.00 | 6 |
    | MSI Radeon RX 9070 XT GAMING X | 1,896,000.00 | 29 |
    | ASUS ROG Swift PG32UCDM Silver | 1,890,300.00 | 12 |


---


### 15. Find products ordered by VIP customers that have an average 


Find products ordered by VIP customers that have an average rating of 4 or above. Top 15.


**Hint 1:** 3-level nested IN subqueries: VIP customers -> orders -> products. Rating condition is filtered via a separate subquery.


??? success "Answer"
    ```sql
    SELECT DISTINCT p.name, p.price
    FROM products AS p
    WHERE p.id IN (
        SELECT oi.product_id
        FROM order_items AS oi
        WHERE oi.order_id IN (
            SELECT o.id
            FROM orders AS o
            WHERE o.status NOT IN ('cancelled')
              AND o.customer_id IN (
                  SELECT id FROM customers WHERE grade = 'VIP'
              )
        )
    )
    AND p.id IN (
        SELECT product_id
        FROM reviews
        GROUP BY product_id
        HAVING AVG(rating) >= 4.0
    )
    ORDER BY p.price DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | price |
    |---|---|
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 |
    | Razer Blade 18 Black | 4,353,100.00 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 |
    | Razer Blade 18 White | 2,483,600.00 |
    | ASUS ROG Strix Scar 16 | 2,452,500.00 |
    | ASUS ROG Strix G16CH Silver | 1,879,100.00 |
    | Jooyon Rionine i9 High-End | 1,849,900.00 |


---


### 16. Compare each customer's average order amount with the overal


Compare each customer's average order amount with the overall average, and find customers whose average is higher. Top 15.


**Hint 1:** Compute per-customer average order amount in a derived table, then filter with a scalar subquery comparison.


??? success "Answer"
    ```sql
    SELECT
        c.name,
        c.grade,
        ca.avg_amount,
        ca.order_count
    FROM customers AS c
    INNER JOIN (
        SELECT
            customer_id,
            ROUND(AVG(total_amount), 2) AS avg_amount,
            COUNT(*) AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ) AS ca ON c.id = ca.customer_id
    WHERE ca.avg_amount > (
        SELECT AVG(total_amount)
        FROM orders
        WHERE status NOT IN ('cancelled')
    )
    ORDER BY ca.avg_amount DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | grade | avg_amount | order_count |
    |---|---|---|---|
    | Sandra Williams | VIP | 16,177,700.00 | 2 |
    | Christine Johnson | VIP | 13,895,400.00 | 1 |
    | Steven Johnson | BRONZE | 10,428,340.00 | 5 |
    | Zachary Ford | VIP | 9,889,465.75 | 4 |
    | Krista Martinez | BRONZE | 8,659,350.00 | 2 |
    | Troy Carr | VIP | 8,319,100.00 | 1 |
    | Donald Landry | BRONZE | 8,301,220.00 | 5 |


---


### 17. Find products whose total sales quantity exceeds the average


Find products whose total sales quantity exceeds the average sales quantity across all products. Top 15.


**Hint 1:** First compute total sales per product in a derived table. Then compare with the average via a nested subquery.


??? success "Answer"
    ```sql
    SELECT
        p.name,
        ps.total_qty
    FROM products AS p
    INNER JOIN (
        SELECT product_id, SUM(quantity) AS total_qty
        FROM order_items
        GROUP BY product_id
    ) AS ps ON p.id = ps.product_id
    WHERE ps.total_qty > (
        SELECT AVG(total_qty)
        FROM (
            SELECT SUM(quantity) AS total_qty
            FROM order_items
            GROUP BY product_id
        )
    )
    ORDER BY ps.total_qty DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | total_qty |
    |---|---|
    | Crucial T700 2TB Silver | 1503 |
    | AMD Ryzen 9 9900X | 1447 |
    | SK hynix Platinum P41 2TB Silver | 1359 |
    | Logitech G502 X PLUS | 1087 |
    | Kingston FURY Beast DDR4 16GB Silver | 1061 |
    | SteelSeries Prime Wireless Black | 1034 |
    | SteelSeries Aerox 5 Wireless Silver | 1030 |


---


### 18. Find reviews whose rating is below the product's average rat


Find reviews whose rating is below the product's average rating. Most recent 15.


**Hint 1:** Computes the average rating for the same product via correlated subquery for each review.


??? success "Answer"
    ```sql
    SELECT
        r.id,
        p.name AS product,
        r.rating,
        ROUND((SELECT AVG(rating) FROM reviews WHERE product_id = r.product_id), 2) AS avg_rating,
        r.title,
        r.created_at
    FROM reviews AS r
    INNER JOIN products AS p ON r.product_id = p.id
    WHERE r.rating < (
        SELECT AVG(rating)
        FROM reviews
        WHERE product_id = r.product_id
    )
    ORDER BY r.created_at DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | id | product | rating | avg_rating | title | created_at |
    |---|---|---|---|---|---|
    | 8546 | Kingston FURY Beast DDR4 32GB Black | 2 | 3.96 | Needs Improvement | 2026-01-19 09:22:49 |
    | 8538 | CORSAIR HX1200 Silver | 2 | 3.68 | Not Great | 2026-01-11 15:23:03 |
    | 8525 | SK hynix Platinum P41 1TB | 2 | 4.13 | Needs Improvement | 2026-01-10 09:56:48 |
    | 8544 | Logitech G715 White | 4 | 4.09 | Good | 2026-01-09 20:41:38 |
    | 8501 | Microsoft Ergonomic Keyboard White | 1 | 3.75 | NULL | 2026-01-05 20:37:52 |
    | 8476 | TP-Link TL-SG108 | 3 | 3.88 | Mediocre | 2025-12-31 10:11:39 |
    | 8480 | V3 Endpoint Security Black | 3 | 3.92 | NULL | 2025-12-30 09:05:01 |


---


### 19. Subquery vs JOIN comparison: Write the query "customers who 


Subquery vs JOIN comparison: Write the query "customers who have written a review" using two different approaches.


**Hint 1:** (A) `WHERE id IN (SELECT customer_id FROM reviews)`, (B) `INNER JOIN reviews ON ...` with DISTINCT. Both produce the same result but execute differently.


??? success "Answer"
    ```sql
    -- (A) IN 서브쿼리 방식
    SELECT name, email
    FROM customers
    WHERE id IN (SELECT customer_id FROM reviews)
    ORDER BY name
    LIMIT 10;
    
    -- (B) JOIN 방식 (DISTINCT 필요)
    SELECT DISTINCT c.name, c.email
    FROM customers AS c
    INNER JOIN reviews AS r ON c.id = r.customer_id
    ORDER BY c.name
    LIMIT 10;
    ```


---


### 20. Find customers who have purchased products from 3 or more ca


Find customers who have purchased products from 3 or more categories, showing name and category count. Top 15.


**Hint 1:** JOIN orders -> order_items -> products to compute the DISTINCT category_id count per customer. Create this aggregation as a derived table, then JOIN with customers.


??? success "Answer"
    ```sql
    SELECT c.name, c.grade, cc.cat_count
    FROM customers AS c
    INNER JOIN (
        SELECT
            o.customer_id,
            COUNT(DISTINCT p.category_id) AS cat_count
        FROM orders AS o
        INNER JOIN order_items AS oi ON o.id = oi.order_id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY o.customer_id
        HAVING COUNT(DISTINCT p.category_id) >= 3
    ) AS cc ON c.id = cc.customer_id
    ORDER BY cc.cat_count DESC, c.name
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | grade | cat_count |
    |---|---|---|
    | Brenda Garcia | VIP | 38 |
    | Christina Suarez | VIP | 38 |
    | Courtney Huff | VIP | 38 |
    | Dennis Herrera | VIP | 38 |
    | James Banks | VIP | 38 |
    | Allen Snyder | VIP | 37 |
    | Dominique Vaughn | VIP | 37 |


---
