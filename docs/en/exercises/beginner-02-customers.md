# Customer Analysis

!!! info "Tables"

    `customers` — Customers (grade, points, channel)  ·  `customer_addresses` — Addresses (address, default flag)  ·  `orders` — Orders (status, amount, date)  ·  `products` — Products (name, price, stock, brand)  ·  `tags` — Tags (name, category)  ·  `product_tags` — Product-tag mapping


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


---


### 5. Find the customer count and percentage by gender. Include NU


Find the customer count and percentage by gender. Include NULL values.


**Hint 1:** Use COALESCE(gender, 'N/A') to handle NULLs. Calculate the ratio with 100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()


??? success "Answer"
    ```sql
    SELECT
        COALESCE(gender, '미입력') AS gender,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM customers
    GROUP BY gender;
    ```


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


---


### 17. Customer Acquisition Channel Distribution


Show customer count, percentage, and average purchase amount by acquisition channel.


**Hint 1:** Use `customers.acquisition_channel` (can be NULL). Use `COALESCE` to show NULL as 'Unknown'. LEFT JOIN `orders` for purchase amounts.


??? success "Answer"
    ```sql
    WITH channel_stats AS (
        SELECT
            COALESCE(c.acquisition_channel, 'unknown') AS channel,
            COUNT(DISTINCT c.id) AS customer_count,
            COUNT(o.id) AS order_count,
            ROUND(COALESCE(SUM(o.total_amount), 0), 0) AS total_revenue
        FROM customers AS c
        LEFT JOIN orders AS o
            ON c.id = o.customer_id
           AND o.status NOT IN ('cancelled')
        GROUP BY COALESCE(c.acquisition_channel, 'unknown')
    )
    SELECT
        channel,
        customer_count,
        ROUND(100.0 * customer_count / SUM(customer_count) OVER (), 1) AS pct,
        order_count,
        CASE WHEN customer_count > 0
            THEN ROUND(1.0 * total_revenue / customer_count, 0)
            ELSE 0
        END AS avg_revenue_per_customer
    FROM channel_stats
    ORDER BY customer_count DESC;
    ```


---
