# JOIN Master

!!! info "Tables"

    `categories` — Categories (parent-child hierarchy)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `reviews` — Reviews (rating, content)  

    `shipping` — Shipping (carrier, tracking, status)  

    `staff` — Staff (dept, role, manager)  

    `suppliers` — Suppliers (company, contact)  

    `tags` — Tags (name, category)  

    `product_tags` — Product-tag mapping  



!!! abstract "Concepts"

    `INNER JOIN`, `LEFT JOIN`, `multi-table JOIN`, `GROUP BY`, `aggregate functions`



### 1. Retrieve each product's name, price, and category name. Top 


Retrieve each product's name, price, and category name. Top 10 by price descending.


**Hint 1:** `INNER JOIN` `products` and `categories` on `category_id`, then `ORDER BY ... DESC LIMIT 10`.


??? success "Answer"
    ```sql
    SELECT p.name, p.price, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    ORDER BY p.price DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | price | category |
    |---|---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 | MacBook |
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 | NVIDIA |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 | NVIDIA |
    | Razer Blade 18 Black | 4,353,100.00 | Gaming Laptop |
    | Razer Blade 16 Silver | 3,702,900.00 | Gaming Laptop |
    | ASUS ROG Strix G16CH White | 3,671,500.00 | Custom Build |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 | Gaming Laptop |


---


### 2. Retrieve the product name, category name, and supplier compa


Retrieve the product name, category name, and supplier company name together.


**Hint 1:** `INNER JOIN` both `categories` and `suppliers` from `products`.


??? success "Answer"
    ```sql
    SELECT
        p.name AS product,
        cat.name AS category,
        s.company_name AS supplier
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    ORDER BY p.name
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | product | category | supplier |
    |---|---|---|
    | AMD Ryzen 9 9900X | AMD | AMD Corp. |
    | AMD Ryzen 9 9900X | AMD | AMD Corp. |
    | APC Back-UPS Pro Gaming BGM1500B Black | UPS/Power | APC Corp. |
    | ASRock B850M Pro RS Black | AMD Socket | ASRock Corp. |
    | ASRock B850M Pro RS Silver | AMD Socket | ASRock Corp. |
    | ASRock B850M Pro RS White | AMD Socket | ASRock Corp. |
    | ASRock B860M Pro RS Silver | Intel Socket | ASRock Corp. |


---


### 3. Retrieve the name and price of products that have never rece


Retrieve the name and price of products that have never received a review.


**Hint 1:** After `LEFT JOIN reviews`, use `WHERE r.id IS NULL` to find unmatched rows.


??? success "Answer"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id
    WHERE r.id IS NULL
    ORDER BY p.price DESC;
    ```


    **Result** (2 rows)

    | name | price |
    |---|---|
    | MSI Radeon RX 9070 XT GAMING X | 1,896,000.00 |
    | Hansung BossMonster DX5800 Black | 1,129,400.00 |


---


### 4. Retrieve the name and signup date of customers who have neve


Retrieve the name and signup date of customers who have never placed an order.


**Hint 1:** `customers LEFT JOIN orders`, then `WHERE o.id IS NULL` to filter customers with no orders.


??? success "Answer"
    ```sql
    SELECT c.name, c.created_at
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    WHERE o.id IS NULL
    ORDER BY c.created_at;
    ```


    **Result** (top 7 of 2,391 rows)

    | name | created_at |
    |---|---|
    | Alan Blair | 2016-01-03 19:49:46 |
    | Dana Miles | 2016-01-15 19:21:20 |
    | Tracy Johnson | 2016-01-26 09:42:20 |
    | Tommy Kim | 2016-02-03 03:40:29 |
    | Sara Harvey | 2016-02-03 04:18:52 |
    | Duane Evans MD | 2016-02-09 18:54:54 |
    | Ashley Jones | 2016-02-17 13:41:08 |


---


### 5. Retrieve each customer's name, grade, order count, and total


Retrieve each customer's name, grade, order count, and total amount spent. Top 10 by total spent.


**Hint 1:** `customers JOIN orders`, then aggregate with `GROUP BY`. Use `COUNT` and `SUM` together.


??? success "Answer"
    ```sql
    SELECT
        c.name, c.grade,
        COUNT(o.id) AS order_count,
        ROUND(SUM(o.total_amount), 2) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | grade | order_count | total_spent |
    |---|---|---|---|
    | Allen Snyder | VIP | 312 | 409,734,279.00 |
    | Jason Rivera | VIP | 352 | 382,314,874.00 |
    | Ronald Arellano | VIP | 225 | 266,184,349.00 |
    | Brenda Garcia | VIP | 250 | 254,525,838.00 |
    | Courtney Huff | VIP | 226 | 248,498,783.00 |
    | Gabriel Walters | VIP | 290 | 248,168,491.00 |
    | James Banks | VIP | 236 | 244,859,844.00 |


---


### 6. Retrieve the order number, customer name, product name, quan


Retrieve the order number, customer name, product name, quantity, and unit price for the 5 most recent orders.


**Hint 1:** Connect 4 tables with `INNER JOIN`: `orders -> customers`, `orders -> order_items -> products`.


??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        c.name AS customer,
        p.name AS product,
        oi.quantity,
        oi.unit_price
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN products AS p ON oi.product_id = p.id
    ORDER BY o.ordered_at DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | order_number | customer | product | quantity | unit_price |
    |---|---|---|---|---|
    | ORD-20251231-37555 | Angel Jones | Norton AntiVirus Plus Silver | 1 | 74,800.00 |
    | ORD-20251231-37543 | Carla Watson | Hancom Office 2024 Enterprise White | 1 | 134,100.00 |
    | ORD-20251231-37552 | Martin Hanson | Hancom Office 2024 Enterprise White | 1 | 134,100.00 |
    | ORD-20251231-37552 | Martin Hanson | NZXT Kraken 240 Silver | 1 | 120,200.00 |
    | ORD-20251231-37548 | Lucas Johnson | Samsung 990 EVO Plus 1TB White | 1 | 187,700.00 |


---


### 7. Find the total revenue and units sold per category. Exclude 


Find the total revenue and units sold per category. Exclude cancelled orders.


**Hint 1:** JOIN `order_items -> products -> categories` and exclude cancelled orders with `WHERE o.status NOT IN ('cancelled')`.


??? success "Answer"
    ```sql
    SELECT
        cat.name AS category,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
    FROM order_items AS oi
    INNER JOIN orders AS o ON oi.order_id = o.id
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY cat.name
    ORDER BY revenue DESC;
    ```


    **Result** (top 7 of 38 rows)

    | category | units_sold | revenue |
    |---|---|---|
    | Gaming Laptop | 1691 | 4,982,099,000.00 |
    | AMD | 4016 | 3,124,984,300.00 |
    | NVIDIA | 1661 | 2,814,694,400.00 |
    | Gaming Monitor | 2464 | 2,781,055,700.00 |
    | General Laptop | 1365 | 2,429,349,600.00 |
    | 2-in-1 | 1301 | 1,944,050,200.00 |
    | Intel Socket | 3406 | 1,556,580,900.00 |


---


### 8. Find the name, average rating, and review count of products 


Find the name, average rating, and review count of products with 5 or more reviews.


**Hint 1:** `products JOIN reviews`, then aggregate with `GROUP BY` and filter with `HAVING COUNT(r.id) >= 5`.


??? success "Answer"
    ```sql
    SELECT
        p.name,
        ROUND(AVG(r.rating), 2) AS avg_rating,
        COUNT(r.id) AS review_count
    FROM products AS p
    INNER JOIN reviews AS r ON p.id = r.product_id
    GROUP BY p.id, p.name
    HAVING COUNT(r.id) >= 5
    ORDER BY avg_rating DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | avg_rating | review_count |
    |---|---|---|
    | Samsung DM500TDA Silver | 4.80 | 5 |
    | LG 27UQ85R White | 4.60 | 5 |
    | LG 32UN880 Ergo White | 4.56 | 16 |
    | WD Elements 2TB Black | 4.53 | 19 |
    | Windows 11 Home Black | 4.52 | 21 |
    | Dell XPS Desktop 8960 Silver | 4.50 | 10 |
    | Arctic Liquid Freezer III Pro 420 A-R... | 4.45 | 22 |


---


### 9. Find the average number of days from order to delivery for c


Find the average number of days from order to delivery for completed shipments.


**Hint 1:** Calculate the date difference with `JULIANDAY(delivered_at) - JULIANDAY(ordered_at)`. JOIN `shipping` with `orders`.


??? success "Answer"
    ```sql
    SELECT
        ROUND(AVG(JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at)), 1) AS avg_delivery_days
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE sh.status = 'delivered'
      AND sh.delivered_at IS NOT NULL;
    ```


    **Result** (1 rows)

    | avg_delivery_days |
    |---|
    | 4.50 |


---


### 10. Find the total shipments, delivered count, and delivery rate


Find the total shipments, delivered count, and delivery rate per carrier.


**Hint 1:** `GROUP BY carrier` with conditional aggregation using `CASE WHEN status = 'delivered'`. Delivery rate is `100.0 * delivered / total`.


??? success "Answer"
    ```sql
    SELECT
        carrier,
        COUNT(*) AS total,
        SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered,
        ROUND(100.0 * SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) / COUNT(*), 1) AS delivery_rate
    FROM shipping
    GROUP BY carrier
    ORDER BY total DESC;
    ```


    **Result** (5 rows)

    | carrier | total | delivered | delivery_rate |
    |---|---|---|---|
    | FedEx | 10,507 | 10,198 | 97.10 |
    | UPS | 8993 | 8729 | 97.10 |
    | USPS | 7227 | 6990 | 96.70 |
    | DHL | 5356 | 5184 | 96.80 |
    | OnTrac | 3533 | 3417 | 96.70 |


---


### 11. Find the product count, average price, and highest price per


Find the product count, average price, and highest price per supplier.


**Hint 1:** `suppliers JOIN products`, then aggregate with `GROUP BY`. Use `COUNT`, `AVG`, and `MAX` functions.


??? success "Answer"
    ```sql
    SELECT
        s.company_name,
        COUNT(p.id) AS product_count,
        ROUND(AVG(p.price), 2) AS avg_price,
        ROUND(MAX(p.price), 2) AS max_price
    FROM suppliers AS s
    INNER JOIN products AS p ON s.id = p.supplier_id
    GROUP BY s.id, s.company_name
    ORDER BY product_count DESC;
    ```


    **Result** (top 7 of 45 rows)

    | company_name | product_count | avg_price | max_price |
    |---|---|---|---|
    | ASUS Corp. | 26 | 1,683,630.77 | 4,526,600.00 |
    | Samsung Official Distribution | 25 | 616,008.00 | 1,833,000.00 |
    | Logitech Corp. | 17 | 111,600.00 | 216,800.00 |
    | MSI Corp. | 13 | 778,430.77 | 1,896,000.00 |
    | Seorin Systech | 12 | 157,908.33 | 269,200.00 |
    | LG Official Distribution | 11 | 1,346,836.36 | 1,828,800.00 |
    | TP-Link Corp. | 11 | 128,763.64 | 344,000.00 |


---


### 12. Retrieve each customer's most recent order date and order am


Retrieve each customer's most recent order date and order amount. Sort by most recent order.


**Hint 1:** Use `MAX(o.ordered_at)` to get the most recent order date and aggregate per customer with `GROUP BY`.


??? success "Answer"
    ```sql
    SELECT
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order_date,
        o.total_amount AS last_order_amount
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY c.id, c.name, c.grade
    ORDER BY last_order_date DESC
    LIMIT 15;
    ```


    **Result** (top 7 of 15 rows)

    | name | grade | last_order_date | last_order_amount |
    |---|---|---|---|
    | Angel Jones | BRONZE | 2025-12-31 22:25:39 | 74,800.00 |
    | Carla Watson | GOLD | 2025-12-31 21:40:27 | 134,100.00 |
    | Martin Hanson | SILVER | 2025-12-31 20:00:48 | 254,300.00 |
    | Lucas Johnson | BRONZE | 2025-12-31 18:43:56 | 187,700.00 |
    | Adam Moore | BRONZE | 2025-12-31 18:00:24 | 155,700.00 |
    | Justin Murphy | VIP | 2025-12-31 15:43:23 | 198,300.00 |
    | Sara Hill | GOLD | 2025-12-31 15:33:05 | 335,000.00 |


---


### 13. Staff Hierarchy (Self-JOIN)


List all staff members with their manager names.
Top-level staff with no manager should show NULL for manager name.


**Hint 1:** Self LEFT JOIN on `staff` table. `staff AS s LEFT JOIN staff AS m ON s.manager_id = m.id`. If no manager, `m.name` is NULL.


??? success "Answer"
    ```sql
    SELECT
        s.id,
        s.name       AS staff_name,
        s.department,
        s.role,
        m.name       AS manager_name,
        m.department AS manager_department
    FROM staff AS s
    LEFT JOIN staff AS m ON s.manager_id = m.id
    ORDER BY s.department, s.name;
    ```


    **Result** (5 rows)

    | id | staff_name | department | role | manager_name | manager_department |
    |---|---|---|---|---|---|
    | 3 | Jonathan Smith | Management | admin | Michael Thomas | Management |
    | 2 | Michael Mcguire | Management | admin | Michael Thomas | Management |
    | 1 | Michael Thomas | Management | admin | NULL | NULL |
    | 5 | Nicole Hamilton | Marketing | manager | Jonathan Smith | Management |
    | 4 | Jaime Phelps | Sales | manager | Michael Thomas | Management |


---


### 14. Product Successor Chain (Self-JOIN)


Find discontinued products and their successors.
Show discontinued product name, date, successor name, and successor price.


**Hint 1:** `products.successor_id` references `id` in the same table. `products AS p JOIN products AS succ ON p.successor_id = succ.id`. Filter `p.discontinued_at IS NOT NULL`.


??? success "Answer"
    ```sql
    SELECT
        p.name        AS discontinued_product,
        p.price       AS old_price,
        p.discontinued_at,
        succ.name     AS successor_product,
        succ.price    AS new_price,
        ROUND(succ.price - p.price, 0) AS price_diff
    FROM products AS p
    INNER JOIN products AS succ ON p.successor_id = succ.id
    WHERE p.discontinued_at IS NOT NULL
    ORDER BY p.discontinued_at DESC
    LIMIT 20;
    ```


    **Result** (top 7 of 18 rows)

    | discontinued_product | old_price | discontinued_at | successor_product | new_price | price_diff |
    |---|---|---|---|---|---|
    | Dell XPS Desktop 8960 Silver | 1,249,400.00 | 2025-11-20 15:30:12 | HP Z2 Mini G1a Black | 895,000.00 | -354,400.00 |
    | Hansung BossMonster DX7700 White | 1,579,400.00 | 2025-10-25 03:47:01 | Jooyon Rionine i9 High-End | 1,849,900.00 | 270,500.00 |
    | SAPPHIRE PULSE RX 7800 XT Silver | 1,146,300.00 | 2025-08-01 06:10:51 | MSI Radeon RX 9070 XT GAMING X | 1,896,000.00 | 749,700.00 |
    | Logitech G715 | 187,900.00 | 2025-04-16 06:47:20 | Ducky One 3 Full Black | 153,900.00 | -34,000.00 |
    | Razer Basilisk V3 Pro 35K White | 102,100.00 | 2025-02-14 06:48:19 | Logitech G PRO X SUPERLIGHT 2 White | 120,400.00 | 18,300.00 |
    | Canon imageCLASS MF655Cdw Black | 278,900.00 | 2024-09-20 15:47:07 | Epson L15160 | 1,019,500.00 | 740,600.00 |
    | be quiet! Straight Power 12 1000W | 131,800.00 | 2024-08-15 23:34:23 | be quiet! Dark Power 13 1000W | 293,000.00 | 161,200.00 |


---


### 15. Q&A Thread View (Self-JOIN)


Show Q&A pairs in one row: question content, customer name, answer content, staff name.


**Hint 1:** Questions: `parent_id IS NULL`. Answers: `parent_id` references question's `id`. Question (`q`) LEFT JOIN Answer (`a`) ON `a.parent_id = q.id`.


??? success "Answer"
    ```sql
    SELECT
        p.name        AS product_name,
        q.content     AS question,
        c.name        AS asked_by,
        q.created_at  AS asked_at,
        a.content     AS answer,
        s.name        AS answered_by,
        a.created_at  AS answered_at
    FROM product_qna AS q
    INNER JOIN products AS p ON q.product_id = p.id
    LEFT JOIN customers AS c ON q.customer_id = c.id
    LEFT JOIN product_qna AS a ON a.parent_id = q.id
    LEFT JOIN staff AS s ON a.staff_id = s.id
    WHERE q.parent_id IS NULL
    ORDER BY q.created_at DESC
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | product_name | question | asked_by | asked_at | answer | answered_by | answered_at |
    |---|---|---|---|---|---|---|
    | SK hynix Platinum P41 2TB Silver | What are the exact dimensions? | Robert Simmons | 2025-12-30 23:10:22 | NULL | NULL | NULL |
    | ASRock B850M Pro RS White | What PSU wattage do you recommend for... | Kathleen Stewart | 2025-12-30 23:01:05 | NULL | NULL | NULL |
    | Dell U2724D | What PSU wattage do you recommend for... | Jill Reed | 2025-12-30 17:53:24 | Yes, it works with both Windows and Mac. | Jaime Phelps | 2025-12-30 20:53:24 |
    | ASRock X870E Taichi Silver | Is this product new or refurbished? | Cory Salazar | 2025-12-30 14:27:52 | NULL | NULL | NULL |
    | Fractal Design North | What are the exact dimensions? | Daniel Murphy | 2025-12-30 13:30:22 | NULL | NULL | NULL |
    | MSI MEG Ai1300P PCIE5 White | Does this come with cables included? | Tracey Johnston | 2025-12-29 19:22:36 | Yes, all necessary cables are include... | Nicole Hamilton | 2025-12-30 21:22:36 |
    | TP-Link TG-3468 Black | Can I use this with a Mac? | John Moss | 2025-12-29 10:01:52 | We expect restock within 2 weeks. You... | Nicole Hamilton | 2025-12-29 11:01:52 |


---


### 16. Days with No Orders (CROSS JOIN)


Using the calendar table, find dates in 2024 with zero orders.


**Hint 1:** LEFT JOIN `calendar` with `orders` on date. Extract date from `ordered_at` with `SUBSTR(ordered_at, 1, 10)`. Filter `WHERE o.id IS NULL` for no-order days.


??? success "Answer"
    ```sql
    SELECT
        cal.date_key,
        cal.day_name,
        cal.is_weekend,
        cal.is_holiday,
        cal.holiday_name
    FROM calendar AS cal
    LEFT JOIN (
        SELECT DISTINCT SUBSTR(ordered_at, 1, 10) AS order_date
        FROM orders
    ) AS od ON cal.date_key = od.order_date
    WHERE cal.year = 2024
      AND od.order_date IS NULL
    ORDER BY cal.date_key;
    ```


---


### 17. Product Tag Search (M:N JOIN)


Find products with the "Gaming" tag.
Show product name, brand, price, and category.


**Hint 1:** JOIN `product_tags` -> `tags` to filter by tag name. JOIN `product_tags` -> `products` for product info. `tags.name = 'Gaming'`.


??? success "Answer"
    ```sql
    SELECT
        p.name   AS product_name,
        p.brand,
        p.price,
        cat.name AS category
    FROM product_tags AS pt
    INNER JOIN tags       AS t   ON pt.tag_id     = t.id
    INNER JOIN products   AS p   ON pt.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE t.name = 'Gaming'
      AND p.is_active = 1
    ORDER BY p.price DESC;
    ```


    **Result** (top 7 of 39 rows)

    | product_name | brand | price | category |
    |---|---|---|---|
    | Razer Blade 18 Black | Razer | 4,353,100.00 | Gaming Laptop |
    | Razer Blade 16 Silver | Razer | 3,702,900.00 | Gaming Laptop |
    | Razer Blade 18 Black | Razer | 2,987,500.00 | Gaming Laptop |
    | Razer Blade 18 White | Razer | 2,483,600.00 | Gaming Laptop |
    | ASUS ROG Strix Scar 16 | ASUS | 2,452,500.00 | Gaming Laptop |
    | ASUS ROG Swift PG32UCDM Silver | ASUS | 1,890,300.00 | Gaming Monitor |
    | ASUS ROG Strix G16CH Silver | ASUS | 1,879,100.00 | Custom Build |


---
