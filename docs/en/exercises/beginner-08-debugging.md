# SQL Error Detection -- Beginner

!!! info "Tables"

    `products` — Products (name, price, stock, brand)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `reviews` — Reviews (rating, content)  

    `payments` — Payments (method, amount, status)  



!!! abstract "Concepts"

    `Syntax errors`, `Logic errors`, `NULL comparison`, `WHERE vs HAVING`, `GROUP BY rules`, `CASE order`



### 1. Find and fix the error in the following query.


Find and fix the error in the following query.


**Hint 1:** Check the required separator when listing columns in the SELECT clause.


??? success "Answer"
    ```sql
    SELECT name, price, brand
    FROM products
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | price | brand |
    |---|---|---|
    | Razer Blade 18 Black | 2,987,500.00 | Razer |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | MSI |
    | Samsung DDR4 32GB PC4-25600 | 43,500.00 | Samsung |
    | Dell U2724D | 894,100.00 | Dell |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | 167,000.00 | G.SKILL |


---


### 2. Find and fix the error in the following query.


Find and fix the error in the following query.


**Hint 1:** Check the type of quotes used for string literals in the SQL standard. It may work in SQLite, but it's problematic from a standard SQL perspective.


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE brand = 'ASUS';
    ```


    **Result** (top 7 of 26 rows)

    | name | price |
    |---|---|
    | ASUS ROG Strix G16CH White | 3,671,500.00 |
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 |
    | ASUS ROG Strix Scar 16 Silver | 1,598,100.00 |
    | ASUS ExpertBook B5 [Special Limited E... | 2,041,000.00 |
    | ASUS PCE-BE92BT | 47,200.00 |
    | ASUS Dual RTX 4060 Ti Black | 2,674,800.00 |
    | ASUS Dual RX 9070 Silver | 1,344,800.00 |


---


### 3. Find and fix the error in the following query.


Find and fix the error in the following query.


**Hint 1:** Check the spelling of the SQL keyword.


??? success "Answer"
    ```sql
    SELECT name, email
    FROM customers
    WHERE grade = 'VIP';
    ```


    **Result** (top 7 of 368 rows)

    | name | email |
    |---|---|
    | Adam Moore | user3@testmail.kr |
    | Cynthia Bryant | user16@testmail.kr |
    | Terri Jones | user33@testmail.kr |
    | Corey Carroll | user96@testmail.kr |
    | Jason Rivera | user97@testmail.kr |
    | Gabriel Walters | user98@testmail.kr |
    | Dominique Vaughn | user130@testmail.kr |


---


### 4. Find and fix the error in the following query.


Find and fix the error in the following query.


**Hint 1:** This query is actually syntactically correct. Think about the default sort direction of `ORDER BY price`. What if the intent is "most expensive first"?


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE price BETWEEN 100000 AND 500000
    ORDER BY price DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | price |
    |---|---|
    | Canon imageCLASS MF655Cdw White | 490,800.00 |
    | MSI MAG Z890 TOMAHAWK WIFI Black | 481,700.00 |
    | Sony WH-CH720N Silver | 445,700.00 |
    | Philips 275E2FAE Silver | 427,600.00 |
    | MSI MAG X870E TOMAHAWK WIFI White | 425,400.00 |
    | Samsung ViewFinity S8 | 423,300.00 |
    | Windows 11 Pro Silver | 423,000.00 |


---


### 5. Find and fix the error in the following query.


Find and fix the error in the following query.


**Hint 1:** Check the exact keyword used for sorting.


??? success "Answer"
    ```sql
    SELECT name, email, grade
    FROM customers
    WHERE grade = 'VIP'
    ORDER BY name;
    ```


    **Result** (top 7 of 368 rows)

    | name | email | grade |
    |---|---|---|
    | Abigail Richardson | user4233@testmail.kr | VIP |
    | Adam Johnson | user2066@testmail.kr | VIP |
    | Adam Moore | user3@testmail.kr | VIP |
    | Adrienne Phillips | user2650@testmail.kr | VIP |
    | Aimee Norman | user3585@testmail.kr | VIP |
    | Alan Cruz | user1746@testmail.kr | VIP |
    | Alan Newman | user1516@testmail.kr | VIP |


---


### 6. Find and fix the error in the following query.


Find and fix the error in the following query.


**Hint 1:** Check the position of the quotes in the LIKE pattern. The `%` must be inside the string.


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%게이밍%';
    ```


---


### 7. Find and fix the error in the following query.


Find and fix the error in the following query.


**Hint 1:** Check the order of SQL clauses. Where should WHERE be positioned?


??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE price > 100000
      AND stock_qty > 0
      AND is_active = 1
    ORDER BY price DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | price | stock_qty |
    |---|---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 | 346 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 | 434 |
    | Razer Blade 18 Black | 4,353,100.00 | 287 |
    | Razer Blade 16 Silver | 3,702,900.00 | 323 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 | 201 |
    | ASUS ROG Strix GT35 | 3,296,800.00 | 455 |
    | Razer Blade 18 Black | 2,987,500.00 | 107 |


---


### 8. Find and fix the error in the following query.


Find and fix the error in the following query.


**Hint 1:** Even when assigning column aliases in the SELECT clause, something is needed between columns.


??? success "Answer"
    ```sql
    SELECT name AS 상품명, price AS 가격
    FROM products
    LIMIT 5;
    ```


    **Result** (5 rows)

    | 상품명 | 가격 |
    |---|---|
    | Razer Blade 18 Black | 2,987,500.00 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 |
    | Samsung DDR4 32GB PC4-25600 | 43,500.00 |
    | Dell U2724D | 894,100.00 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | 167,000.00 |


---


### 9. Find and fix the error in the following query.


Find and fix the error in the following query.


**Hint 1:** Check the separator between values in the `IN` list.


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE brand IN ('ASUS', 'MSI', 'Dell');
    ```


    **Result** (top 7 of 42 rows)

    | name | price |
    |---|---|
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 |
    | Dell U2724D | 894,100.00 |
    | MSI Radeon RX 9070 VENTUS 3X White | 383,100.00 |
    | MSI MAG X870E TOMAHAWK WIFI White | 425,400.00 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 |
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 |
    | MSI Radeon RX 7900 XTX GAMING X White | 1,517,600.00 |


---


### 10. Find and fix the error in the following query.


Find and fix the error in the following query.


**Hint 1:** Check the separator between columns in the SELECT list.


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total,
           AVG(price) AS avg_price,
           SUM(price) AS total_price
    FROM products;
    ```


    **Result** (1 rows)

    | total | avg_price | total_price |
    |---|---|---|
    | 280 | 649,272.50 | 181,796,300.00 |


---


### 11. The following query tries to find customers without a birth 


The following query tries to find customers without a birth date. The result returns 0 rows. Why?


**Hint 1:** In SQL, NULL means "unknown value." What happens when you compare with `=`? The result is always something specific.


??? success "Answer"
    ```sql
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


### 12. The following query tries to find the product count per bran


The following query tries to find the product count per brand. It throws an error.


**Hint 1:** There is a required clause when using an aggregate function alongside a non-aggregate column in SELECT.


??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand;
    ```


    **Result** (top 7 of 55 rows)

    | brand | product_count |
    |---|---|
    | AMD | 2 |
    | APC | 1 |
    | ASRock | 11 |
    | ASUS | 26 |
    | Adobe | 1 |
    | AhnLab | 2 |
    | Apple | 2 |


---


### 13. The following query tries to show only brands with 10 or mor


The following query tries to show only brands with 10 or more products. It throws an error.


**Hint 1:** Can aggregate functions be used in the `WHERE` clause?


??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10;
    ```


    **Result** (7 rows)

    | brand | product_count |
    |---|---|
    | ASRock | 11 |
    | ASUS | 26 |
    | LG | 11 |
    | Logitech | 17 |
    | MSI | 13 |
    | Samsung | 25 |
    | TP-Link | 11 |


---


### 14. The following query tries to find products that are not 'ASU


The following query tries to find products that are not 'ASUS'. However, products with a NULL brand are missing from the results.


**Hint 1:** What is the result of `NULL != 'ASUS'`? Comparisons with NULL always return NULL (UNKNOWN).


??? success "Answer"
    ```sql
    SELECT name, brand
    FROM products
    WHERE brand != 'ASUS' OR brand IS NULL;
    ```


    **Result** (top 7 of 254 rows)

    | name | brand |
    |---|---|
    | Razer Blade 18 Black | Razer |
    | MSI GeForce RTX 4070 Ti Super GAMING X | MSI |
    | Samsung DDR4 32GB PC4-25600 | Samsung |
    | Dell U2724D | Dell |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | G.SKILL |
    | MSI Radeon RX 9070 VENTUS 3X White | MSI |
    | Samsung DDR5 32GB PC5-38400 | Samsung |


---


### 15. The following query tries to find the top 10 orders by amoun


The following query tries to find the top 10 orders by amount. The ORDER BY placement is wrong.


**Hint 1:** Think about the execution order of SQL clauses. Which should come first, LIMIT or ORDER BY?


??? success "Answer"
    ```sql
    SELECT order_number, total_amount
    FROM orders
    ORDER BY total_amount DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | order_number | total_amount |
    |---|---|
    | ORD-20201121-08810 | 50,867,500.00 |
    | ORD-20250305-32265 | 46,820,024.00 |
    | ORD-20230523-22331 | 46,094,971.00 |
    | ORD-20200209-05404 | 43,677,500.00 |
    | ORD-20221231-20394 | 43,585,700.00 |
    | ORD-20251218-37240 | 38,626,400.00 |
    | ORD-20220106-15263 | 37,987,600.00 |


---


### 16. The following query sorts the average points per tier in des


The following query sorts the average points per tier in descending order. It uses an alias in ORDER BY, which may not work in some cases.


**Hint 1:** This query works correctly in SQLite. However, some databases have restrictions on using aliases in `ORDER BY`. What alternative exists?


??? success "Answer"
    ```sql
    SELECT grade,
           AVG(point_balance) AS avg_points
    FROM customers
    GROUP BY grade
    ORDER BY AVG(point_balance) DESC;
    ```


    **Result** (4 rows)

    | grade | avg_points |
    |---|---|
    | VIP | 407,014.69 |
    | GOLD | 147,710.69 |
    | SILVER | 95,042.33 |
    | BRONZE | 16,779.46 |


---


### 17. The following query tries to find only customers where gende


The following query tries to find only customers where gender is not NULL. The logic is wrong.


**Hint 1:** Same principle as Problem 11. The `!=` comparison with NULL also returns NULL.


??? success "Answer"
    ```sql
    SELECT name, gender
    FROM customers
    WHERE gender IS NOT NULL;
    ```


    **Result** (top 7 of 4,701 rows)

    | name | gender |
    |---|---|
    | Joshua Atkins | M |
    | Adam Moore | M |
    | Virginia Steele | F |
    | Jared Vazquez | M |
    | Benjamin Skinner | M |
    | Ashley Jones | F |
    | Tyler Rodriguez | F |


---


### 18. The following query finds the count per order status and fil


The following query finds the count per order status and filters with HAVING. But the intent is wrong.


**Hint 1:** `HAVING` is meant for filtering aggregate results. What clause should be used for simple column value filtering?


??? success "Answer"
    ```sql
    SELECT status, COUNT(*) AS order_count
    FROM orders
    WHERE status = 'confirmed'
    GROUP BY status;
    ```


    **Result** (1 rows)

    | status | order_count |
    |---|---|
    | confirmed | 34,393 |


---


### 19. The following query finds the count per brand for products p


The following query finds the count per brand for products priced 1M+. There is an issue with GROUP BY.


**Hint 1:** All non-aggregate columns in SELECT must be included in GROUP BY. What about `name`?


??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS cnt
    FROM products
    WHERE price >= 1000000
    GROUP BY brand;
    ```


    **Result** (top 7 of 15 rows)

    | brand | cnt |
    |---|---|
    | ASUS | 16 |
    | Apple | 1 |
    | BenQ | 1 |
    | Dell | 1 |
    | Epson | 1 |
    | Gigabyte | 2 |
    | HP | 5 |


---


### 20. The following query finds the order count per year. The resu


The following query finds the order count per year. The results look wrong.


**Hint 1:** `ordered_at` contains both date and time. How should you group by year?


??? success "Answer"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 4) AS year, COUNT(*) AS order_count
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```


    **Result** (top 7 of 10 rows)

    | year | order_count |
    |---|---|
    | 2016 | 416 |
    | 2017 | 709 |
    | 2018 | 1319 |
    | 2019 | 2589 |
    | 2020 | 4319 |
    | 2021 | 5841 |
    | 2022 | 5203 |


---


### 21. The following query calculates the margin rate (%) for produ


The following query calculates the margin rate (%) for products. Some products show a margin of 0%.


**Hint 1:** What happens when you divide two integers in SQLite?


??? success "Answer"
    ```sql
    SELECT name, price, cost_price,
           ROUND((price - cost_price) * 100.0 / price, 1) AS margin_pct
    FROM products
    WHERE is_active = 1
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | price | cost_price | margin_pct |
    |---|---|---|---|
    | Razer Blade 18 Black | 2,987,500.00 | 3,086,700.00 | -3.30 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | 1,360,300.00 | 22.00 |
    | Samsung DDR4 32GB PC4-25600 | 43,500.00 | 37,900.00 | 12.90 |
    | Dell U2724D | 894,100.00 | 565,700.00 | 36.70 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | 167,000.00 | 121,400.00 | 27.30 |
    | MSI Radeon RX 9070 VENTUS 3X White | 383,100.00 | 431,800.00 | -12.70 |
    | Samsung DDR5 32GB PC5-38400 | 211,800.00 | 151,900.00 | 28.30 |


---


### 22. The following query has a CASE expression missing the ELSE c


The following query has a CASE expression missing the ELSE clause. What problem can occur?


**Hint 1:** What value will products priced 1M+ receive?


??? success "Answer"
    ```sql
    SELECT name, price,
           CASE
               WHEN price < 100000 THEN '저가'
               WHEN price < 500000 THEN '중저가'
               WHEN price < 1000000 THEN '중가'
               ELSE '고가'
           END AS price_tier
    FROM products;
    ```


    **Result** (top 7 of 280 rows)

    | name | price | price_tier |
    |---|---|---|
    | Razer Blade 18 Black | 2,987,500.00 | 고가 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1,744,000.00 | 고가 |
    | Samsung DDR4 32GB PC4-25600 | 43,500.00 | 저가 |
    | Dell U2724D | 894,100.00 | 중가 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | 167,000.00 | 중저가 |
    | MSI Radeon RX 9070 VENTUS 3X White | 383,100.00 | 중저가 |
    | Samsung DDR5 32GB PC5-38400 | 211,800.00 | 중저가 |


---


### 23. The following query uses an alias in HAVING. It may throw an


The following query uses an alias in HAVING. It may throw an error.


**Hint 1:** SQLite allows using aliases in HAVING, but what about MySQL, PostgreSQL, etc.?


??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS cnt
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10;
    ```


    **Result** (7 rows)

    | brand | cnt |
    |---|---|
    | ASRock | 11 |
    | ASUS | 26 |
    | LG | 11 |
    | Logitech | 17 |
    | MSI | 13 |
    | Samsung | 25 |
    | TP-Link | 11 |


---


### 24. The following query calculates the discount rate for orders.


The following query calculates the discount rate for orders. A division-by-zero error may occur.


**Hint 1:** What happens if `total_amount` is 0?


??? success "Answer"
    ```sql
    SELECT order_number,
           total_amount,
           discount_amount,
           CASE
               WHEN total_amount = 0 THEN 0
               ELSE ROUND(discount_amount * 100.0 / total_amount, 1)
           END AS discount_rate
    FROM orders
    ORDER BY discount_rate DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | order_number | total_amount | discount_amount | discount_rate |
    |---|---|---|---|
    | ORD-20240509-27481 | 155,218.00 | 28,100.00 | 18.10 |
    | ORD-20190915-04201 | 84,269.00 | 15,000.00 | 17.80 |
    | ORD-20221108-19511 | 375,878.00 | 66,400.00 | 17.70 |
    | ORD-20230429-21988 | 56,000.00 | 9,900.00 | 17.70 |
    | ORD-20240405-26944 | 737,599.00 | 130,300.00 | 17.70 |
    | ORD-20171114-00993 | 90,300.00 | 15,900.00 | 17.60 |
    | ORD-20200211-05431 | 205,300.00 | 36,100.00 | 17.60 |


---


### 25. The following query finds monthly statistics for 2024 orders


The following query finds monthly statistics for 2024 orders. The month sorting is wrong.


**Hint 1:** For "monthly statistics," it's natural to view from January to December in chronological order. What is the current sort criterion?


??? success "Answer"
    ```sql
    SELECT SUBSTR(ordered_at, 6, 2) AS month,
           COUNT(*) AS order_count
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```


    **Result** (top 7 of 12 rows)

    | month | order_count |
    |---|---|
    | 01 | 346 |
    | 02 | 465 |
    | 03 | 601 |
    | 04 | 506 |
    | 05 | 415 |
    | 06 | 415 |
    | 07 | 414 |


---


### 26. The following query finds the average and total points per t


The following query finds the average and total points per tier. ROUND is applied to only one place.


**Hint 1:** The same value (`AVG(point_balance)`) is queried twice -- one with ROUND, one without. This isn't an error per se, but `avg_points_raw` will show a long decimal number.


??? success "Answer"
    ```sql
    SELECT grade,
           ROUND(AVG(point_balance)) AS avg_points,
           SUM(point_balance) AS total_points,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade;
    ```


    **Result** (4 rows)

    | grade | avg_points | total_points | customer_count |
    |---|---|---|---|
    | BRONZE | 16,779.00 | 64,751,937 | 3859 |
    | GOLD | 147,711.00 | 77,400,400 | 524 |
    | SILVER | 95,042.00 | 45,525,276 | 479 |
    | VIP | 407,015.00 | 149,781,406 | 368 |


---


### 27. The following query finds products containing 'Black' or 'Wh


The following query finds products containing 'Black' or 'White' in the name. The results are more than expected.


**Hint 1:** Check the operator precedence of `AND` and `OR`. Which is evaluated first?


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE (name LIKE '%블랙%' OR name LIKE '%화이트%')
      AND price > 500000;
    ```


---


### 28. The following query calculates the sum of columns that may c


The following query calculates the sum of columns that may contain NULL. The results differ from expectations.


**Hint 1:** If `discount_amount` or `shipping_fee` is NULL, `SUM` ignores NULLs, but what about `discount_amount + shipping_fee`?


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_orders,
           SUM(COALESCE(discount_amount, 0)) + SUM(COALESCE(shipping_fee, 0)) AS extra_charges,
           AVG(COALESCE(discount_amount, 0) + COALESCE(shipping_fee, 0)) AS avg_extra
    FROM orders;
    ```


    **Result** (1 rows)

    | total_orders | extra_charges | avg_extra |
    |---|---|---|
    | 37,557 | 361,289,400.00 | 9,619.76 |


---


### 29. The following query finds product count by price tier. The C


The following query finds product count by price tier. The CASE condition order is wrong.


**Hint 1:** CASE evaluates conditions top-to-bottom and stops at the first TRUE condition. All product prices are >= 0.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN price >= 1000000 THEN '고가'
               WHEN price >= 500000 THEN '중가'
               WHEN price >= 100000 THEN '중저가'
               ELSE '저가'
           END AS price_tier,
           COUNT(*) AS cnt
    FROM products
    GROUP BY price_tier;
    ```


    **Result** (4 rows)

    | price_tier | cnt |
    |---|---|
    | 고가 | 65 |
    | 저가 | 47 |
    | 중가 | 38 |
    | 중저가 | 130 |


---


### 30. The following query analyzes customer data by signup year. W


The following query analyzes customer data by signup year. WHERE and HAVING are confused.


**Hint 1:** HAVING is used twice, and the SQL clause order is also wrong. Distinguish between row-level filtering and group-level filtering.


??? success "Answer"
    ```sql
    SELECT SUBSTR(created_at, 1, 4) AS join_year,
           grade,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    WHERE grade IN ('GOLD', 'VIP')
    GROUP BY join_year, grade
    HAVING COUNT(*) >= 50
    ORDER BY join_year, grade;
    ```


    **Result** (top 7 of 10 rows)

    | join_year | grade | customer_count | avg_points |
    |---|---|---|---|
    | 2020 | GOLD | 63 | 243,137.00 |
    | 2021 | GOLD | 101 | 142,592.00 |
    | 2021 | VIP | 60 | 409,715.00 |
    | 2022 | GOLD | 72 | 119,752.00 |
    | 2022 | VIP | 60 | 296,670.00 |
    | 2023 | GOLD | 67 | 73,467.00 |
    | 2023 | VIP | 58 | 203,509.00 |


---
