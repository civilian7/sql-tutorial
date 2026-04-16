# Customer Analysis

!!! info "Tables"

    `customers` — Customers (grade, points, channel)  

    `customer_addresses` — Addresses (address, default flag)  

    `orders` — Orders (status, amount, date)  

    `products` — Products (name, price, stock, brand)  

    `tags` — Tags (name, category)  

    `product_tags` — Product-tag mapping  



!!! abstract "Concepts"

    `SELECT`, `WHERE`, `GROUP BY`, `COUNT`, `AVG`, `MAX`, `COALESCE`, `SUBSTR`, `INSTR`, `JOIN`, `HAVING`, `LIKE`, `IN`, `CASE WHEN`



### 1. Find the number of active and inactive customers separately.


Find the number of active and inactive customers separately.


**Hint 1:** Group with GROUP BY is_active and count each group with COUNT(*)


??? success "Answer"
    ```sql
    SELECT
        is_active,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY is_active;
    ```


    **Result** (2 rows)

    | is_active | customer_count |
    |---|---|
    | 0 | 1570 |
    | 1 | 3660 |


---


### 2. Find the number of customers per grade.


Find the number of customers per grade.


**Hint 1:** Use GROUP BY grade and COUNT(*)


??? success "Answer"
    ```sql
    SELECT grade, COUNT(*) AS cnt
    FROM customers
    GROUP BY grade
    ORDER BY cnt DESC;
    ```


    **Result** (4 rows)

    | grade | cnt |
    |---|---|
    | BRONZE | 3859 |
    | GOLD | 524 |
    | SILVER | 479 |
    | VIP | 368 |


---


### 3. Retrieve the name, email, and point balance of VIP-grade cus


Retrieve the name, email, and point balance of VIP-grade customers, sorted by point balance in descending order.


**Hint 1:** Filter with WHERE grade = 'VIP' and sort with ORDER BY point_balance DESC


??? success "Answer"
    ```sql
    SELECT name, email, point_balance
    FROM customers
    WHERE grade = 'VIP'
    ORDER BY point_balance DESC;
    ```


    **Result** (top 7 of 368 rows)

    | name | email | point_balance |
    |---|---|---|
    | Allen Snyder | user226@testmail.kr | 3,955,828 |
    | Jason Rivera | user97@testmail.kr | 3,518,880 |
    | Brenda Garcia | user162@testmail.kr | 2,450,166 |
    | Courtney Huff | user356@testmail.kr | 2,383,491 |
    | James Banks | user227@testmail.kr | 2,297,542 |
    | Ronald Arellano | user549@testmail.kr | 2,276,622 |
    | Gabriel Walters | user98@testmail.kr | 2,218,590 |


---


### 4. Retrieve the name, signup date, and grade of the 10 most rec


Retrieve the name, signup date, and grade of the 10 most recently registered customers.


**Hint 1:** Sort with ORDER BY created_at DESC for newest first, then LIMIT 10


??? success "Answer"
    ```sql
    SELECT name, created_at, grade
    FROM customers
    ORDER BY created_at DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | created_at | grade |
    |---|---|---|
    | Robert Simmons | 2025-12-30 20:49:59 | BRONZE |
    | Olivia Watson | 2025-12-30 18:50:02 | BRONZE |
    | Jennifer Mcgrath | 2025-12-30 10:18:14 | BRONZE |
    | Nicholas Richardson | 2025-12-30 06:02:53 | BRONZE |
    | Warren Olsen | 2025-12-30 05:59:32 | BRONZE |
    | Bradley Daugherty | 2025-12-30 05:43:21 | BRONZE |
    | Michael Moore | 2025-12-29 17:18:36 | BRONZE |


---


### 5. Find the customer count and percentage by gender. Include NU


Find the customer count and percentage by gender. Include NULL values.


**Hint 1:** Use COALESCE(gender, 'N/A') to handle NULLs. Calculate the ratio with 100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers)


??? success "Answer"
    ```sql
    SELECT
        COALESCE(gender, '미입력') AS gender,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct
    FROM customers
    GROUP BY gender;
    ```


    **Result** (3 rows)

    | gender | cnt | pct |
    |---|---|---|
    | 미입력 | 529 | 10.10 |
    | F | 1669 | 31.90 |
    | M | 3032 | 58.00 |


---


### 6. Retrieve the name, grade, and point balance of the top 20 cu


Retrieve the name, grade, and point balance of the top 20 customers with the highest point balance.


**Hint 1:** Use ORDER BY point_balance DESC and LIMIT 20. Target only active customers


??? success "Answer"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    WHERE is_active = 1
    ORDER BY point_balance DESC
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | name | grade | point_balance |
    |---|---|---|
    | Allen Snyder | VIP | 3,955,828 |
    | Jason Rivera | VIP | 3,518,880 |
    | Brenda Garcia | VIP | 2,450,166 |
    | Courtney Huff | VIP | 2,383,491 |
    | James Banks | VIP | 2,297,542 |
    | Ronald Arellano | VIP | 2,276,622 |
    | Gabriel Walters | VIP | 2,218,590 |


---


### 7. Find the number of customers whose birth_date is NULL.


Find the number of customers whose birth_date is NULL.


**Hint 1:** Use WHERE birth_date IS NULL to check for NULLs. = NULL does not work


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS no_birthdate
    FROM customers
    WHERE birth_date IS NULL;
    ```


    **Result** (1 rows)

    | no_birthdate |
    |---|
    | 738 |


---


### 8. Find the number of new customers per signup year.


Find the number of new customers per signup year.


**Hint 1:** Extract the year with SUBSTR(created_at, 1, 4) and group with GROUP BY


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 4) AS join_year,
        COUNT(*) AS new_customers
    FROM customers
    GROUP BY SUBSTR(created_at, 1, 4)
    ORDER BY join_year;
    ```


    **Result** (top 7 of 10 rows)

    | join_year | new_customers |
    |---|---|
    | 2016 | 100 |
    | 2017 | 180 |
    | 2018 | 300 |
    | 2019 | 450 |
    | 2020 | 700 |
    | 2021 | 800 |
    | 2022 | 650 |


---


### 9. Find the count and percentage of customers whose last_login_


Find the count and percentage of customers whose last_login_at is NULL.


**Hint 1:** Calculate the ratio by dividing by the total count from a subquery (SELECT COUNT(*) FROM customers)


??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS never_logged_in,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct
    FROM customers
    WHERE last_login_at IS NULL;
    ```


    **Result** (1 rows)

    | never_logged_in | pct |
    |---|---|
    | 281 | 5.40 |


---


### 10. Find the average and maximum point balance per grade.


Find the average and maximum point balance per grade.


**Hint 1:** Use GROUP BY grade with AVG(point_balance) and MAX(point_balance) together


??? success "Answer"
    ```sql
    SELECT
        grade,
        COUNT(*) AS cnt,
        ROUND(AVG(point_balance), 0) AS avg_points,
        MAX(point_balance) AS max_points
    FROM customers
    GROUP BY grade
    ORDER BY avg_points DESC;
    ```


    **Result** (4 rows)

    | grade | cnt | avg_points | max_points |
    |---|---|---|---|
    | VIP | 368 | 407,015.00 | 3,955,828 |
    | GOLD | 524 | 147,711.00 | 2,007,717 |
    | SILVER | 479 | 95,042.00 | 1,266,757 |
    | BRONZE | 3859 | 16,779.00 | 956,983 |


---


### 11. Find the customer count by email domain (after the @).


Find the customer count by email domain (after the @).


**Hint 1:** Extract the domain after @ with SUBSTR(email, INSTR(email, '@') + 1)


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(email, INSTR(email, '@') + 1) AS domain,
        COUNT(*) AS cnt
    FROM customers
    GROUP BY domain
    ORDER BY cnt DESC
    LIMIT 10;
    ```


    **Result** (1 rows)

    | domain | cnt |
    |---|---|
    | testmail.kr | 5230 |


---


### 12. Retrieve the name and address count of customers who have re


Retrieve the name and address count of customers who have registered 2 or more shipping addresses.


**Hint 1:** JOIN customers and customer_addresses, then filter with HAVING COUNT(...) >= 2


??? success "Answer"
    ```sql
    SELECT
        c.name,
        COUNT(a.id) AS address_count
    FROM customers AS c
    INNER JOIN customer_addresses AS a ON c.id = a.customer_id
    GROUP BY c.id, c.name
    HAVING COUNT(a.id) >= 2
    ORDER BY address_count DESC
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | name | address_count |
    |---|---|
    | Joshua Atkins | 3 |
    | Danny Johnson | 3 |
    | Adam Moore | 3 |
    | Michael Velasquez | 3 |
    | Maria Daniels | 3 |
    | Duane Evans MD | 3 |
    | Jeremy Curtis | 3 |


---


### 13. Retrieve the name, signup date, and grade of customers who j


Retrieve the name, signup date, and grade of customers who joined in 2024 with a grade of VIP or GOLD.


**Hint 1:** Filter year with LIKE '2024%' and grade with IN ('VIP', 'GOLD'). Combine both conditions with AND


??? success "Answer"
    ```sql
    SELECT name, created_at, grade
    FROM customers
    WHERE created_at LIKE '2024%'
      AND grade IN ('VIP', 'GOLD')
    ORDER BY created_at;
    ```


    **Result** (top 7 of 140 rows)

    | name | created_at | grade |
    |---|---|---|
    | Andrea Berry | 2024-01-05 14:23:16 | GOLD |
    | Theresa Lynch | 2024-01-07 05:39:40 | GOLD |
    | Dr. Donna Barber | 2024-01-07 12:17:28 | VIP |
    | Lauren Bradley | 2024-01-07 19:33:43 | VIP |
    | David Dorsey | 2024-01-11 06:40:22 | GOLD |
    | Clayton Howell | 2024-01-16 06:45:22 | GOLD |
    | David Levy | 2024-01-23 05:29:21 | VIP |


---


### 14. Find the number of signups per month in 2024.


Find the number of signups per month in 2024.


**Hint 1:** Extract 'YYYY-MM' format with SUBSTR(created_at, 1, 7) and aggregate monthly with GROUP BY


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 7) AS month,
        COUNT(*) AS signups
    FROM customers
    WHERE created_at LIKE '2024%'
    GROUP BY SUBSTR(created_at, 1, 7)
    ORDER BY month;
    ```


    **Result** (top 7 of 12 rows)

    | month | signups |
    |---|---|
    | 2024-01 | 52 |
    | 2024-02 | 48 |
    | 2024-03 | 71 |
    | 2024-04 | 53 |
    | 2024-05 | 43 |
    | 2024-06 | 68 |
    | 2024-07 | 62 |


---


### 15. Divide point balances into ranges -- 0, 1-1,000, 1,001-5,000


Divide point balances into ranges -- 0, 1-1,000, 1,001-5,000, 5,001-10,000, and 10,001+ -- and count the customers in each range.


**Hint 1:** Classify point ranges with CASE WHEN, then aggregate with GROUP BY and COUNT(*). Sort by range order with ORDER BY MIN(point_balance)


??? success "Answer"
    ```sql
    SELECT
        CASE
            WHEN point_balance = 0 THEN '없음'
            WHEN point_balance <= 1000 THEN '1~1,000'
            WHEN point_balance <= 5000 THEN '1,001~5,000'
            WHEN point_balance <= 10000 THEN '5,001~10,000'
            ELSE '10,001 이상'
        END AS point_range,
        COUNT(*) AS cnt
    FROM customers
    GROUP BY point_range
    ORDER BY MIN(point_balance);
    ```


    **Result** (5 rows)

    | point_range | cnt |
    |---|---|
    | 없음 | 2506 |
    | 1~1,000 | 137 |
    | 1,001~5,000 | 344 |
    | 5,001~10,000 | 148 |
    | 10,001 이상 | 2095 |


---


### 16. Multi-Tag Products (GROUP BY HAVING)


Find products with 3 or more tags.
Show product name and tag list (comma-separated).


**Hint 1:** GROUP BY `product_id` on `product_tags`. `HAVING COUNT(*) >= 3`. Use `GROUP_CONCAT(t.name, ', ')` for tag list.


??? success "Answer"

    === "SQLite"
        ```sql
        SELECT
        p.name AS product_name,
        p.brand,
        COUNT(pt.tag_id) AS tag_count,
        GROUP_CONCAT(t.name, ', ') AS tags
    FROM product_tags AS pt
    INNER JOIN products AS p ON pt.product_id = p.id
    INNER JOIN tags     AS t ON pt.tag_id     = t.id
    GROUP BY p.id, p.name, p.brand
    HAVING COUNT(pt.tag_id) >= 3
    ORDER BY tag_count DESC
    LIMIT 20;
        ```

    === "MySQL"
        ```sql
        SELECT
        p.name AS product_name,
        p.brand,
        COUNT(pt.tag_id) AS tag_count,
        GROUP_CONCAT(t.name SEPARATOR ', ') AS tags
    FROM product_tags AS pt
    INNER JOIN products AS p ON pt.product_id = p.id
    INNER JOIN tags     AS t ON pt.tag_id     = t.id
    GROUP BY p.id, p.name, p.brand
    HAVING COUNT(pt.tag_id) >= 3
    ORDER BY tag_count DESC
    LIMIT 20;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
        p.name AS product_name,
        p.brand,
        COUNT(pt.tag_id) AS tag_count,
        STRING_AGG(t.name, ', ') AS tags
    FROM product_tags AS pt
    INNER JOIN products AS p ON pt.product_id = p.id
    INNER JOIN tags     AS t ON pt.tag_id     = t.id
    GROUP BY p.id, p.name, p.brand
    HAVING COUNT(pt.tag_id) >= 3
    ORDER BY tag_count DESC
    LIMIT 20;
        ```

    === "Oracle"
        ```sql
        SELECT
        p.name AS product_name,
        p.brand,
        COUNT(pt.tag_id) AS tag_count,
        LISTAGG(t.name, ', ') WITHIN GROUP (ORDER BY t.name) AS tags
    FROM product_tags pt
    INNER JOIN products p ON pt.product_id = p.id
    INNER JOIN tags     t ON pt.tag_id     = t.id
    GROUP BY p.id, p.name, p.brand
    HAVING COUNT(pt.tag_id) >= 3
    ORDER BY tag_count DESC
    FETCH FIRST 20 ROWS ONLY;
        ```

    === "SQL Server"
        ```sql
        SELECT TOP 20
        p.name AS product_name,
        p.brand,
        COUNT(pt.tag_id) AS tag_count,
        STRING_AGG(t.name, ', ') AS tags
    FROM product_tags AS pt
    INNER JOIN products AS p ON pt.product_id = p.id
    INNER JOIN tags     AS t ON pt.tag_id     = t.id
    GROUP BY p.id, p.name, p.brand
    HAVING COUNT(pt.tag_id) >= 3
    ORDER BY tag_count DESC;
        ```


    **Result** (top 7 of 20 rows)

    | product_name | brand | tag_count | tags |
    |---|---|---|---|
    | Razer Blade 16 Silver | Razer | 8 | Water/Dust Resistant, Ergonomic, Gami... |
    | Razer Blade 18 Black | Razer | 8 | USB-C, Touchscreen, Gaming, Student, ... |
    | MSI GeForce RTX 4070 Ti Super GAMING X | MSI | 7 | Low Noise, Wi-Fi 7, Touchscreen, Work... |
    | Razer Blade 18 White | Razer | 7 | QHD, Wi-Fi 6E, Gaming, Portable, High... |
    | Logitech K580 | Logitech | 7 | FHD, Video Editing, Graphic Design, E... |
    | SteelSeries Prime Wireless Black | SteelSeries | 7 | RGB Lighting, USB-C, PCIe 4.0, Gaming... |
    | SteelSeries Aerox 5 Wireless Silver | SteelSeries | 7 | OLED, High Refresh Rate, DDR5, Gaming... |


---


### 17. Customer Count and Percentage by Acquisition Channel


Find the customer count and percentage by acquisition channel. Show NULL as 'Unknown'.


**Hint 1:** Use `COALESCE(acquisition_channel, 'Unknown')` to handle NULLs. Calculate the ratio with `(SELECT COUNT(*) FROM customers)`.


??? success "Answer"
    ```sql
    SELECT
        COALESCE(acquisition_channel, '미분류') AS channel,
        COUNT(*) AS customer_count,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct
    FROM customers
    GROUP BY COALESCE(acquisition_channel, '미분류')
    ORDER BY customer_count DESC;
    ```


    **Result** (5 rows)

    | channel | customer_count | pct |
    |---|---|---|
    | search_ad | 1543 | 29.50 |
    | social | 1425 | 27.20 |
    | organic | 1146 | 21.90 |
    | referral | 708 | 13.50 |
    | direct | 408 | 7.80 |


---
