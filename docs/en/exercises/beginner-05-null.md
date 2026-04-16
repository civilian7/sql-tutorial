# NULL Handling

!!! info "Tables"

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `products` — Products (name, price, stock, brand)  



!!! abstract "Concepts"

    `IS NULL`, `IS NOT NULL`, `COALESCE`, `IFNULL`, `NULL and aggregates`, `NULL sorting`



### 1. Query the name and email of customers who do not have a date


Query the name and email of customers who do not have a date of birth (`birth_date`).


**Hint 1:** To find NULL values, you must use `IS NULL` instead of `= NULL`.


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


### 2. Find the number of customers who have a gender (`gender`) va


Find the number of customers who have a gender (`gender`) value entered.


**Hint 1:** Filter only rows with values using `IS NOT NULL`, then count with `COUNT(*)`.


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS gender_filled_count
    FROM customers
    WHERE gender IS NOT NULL;
    ```


    **Result** (1 rows)

    | gender_filled_count |
    |---|
    | 4701 |


---


### 3. Query the name, tier, and signup date of customers who have 


Query the name, tier, and signup date of customers who have never logged in (`last_login_at` is NULL).


**Hint 1:** Use `last_login_at IS NULL` to find customers with no login history.


??? success "Answer"
    ```sql
    SELECT name, grade, created_at
    FROM customers
    WHERE last_login_at IS NULL;
    ```


    **Result** (top 7 of 281 rows)

    | name | grade | created_at |
    |---|---|---|
    | Sara Harvey | BRONZE | 2016-02-03 04:18:52 |
    | Terry Miller DVM | BRONZE | 2016-02-23 17:09:54 |
    | Russell Castillo | BRONZE | 2016-05-07 02:57:58 |
    | Tony Jones | BRONZE | 2016-04-29 00:44:20 |
    | Amy Smith | BRONZE | 2016-08-13 13:52:58 |
    | Tonya Torres | BRONZE | 2017-04-08 22:00:58 |
    | Paula Allen | BRONZE | 2017-12-01 07:23:31 |


---


### 4. Query the order number and delivery notes (`notes`) for orde


Query the order number and delivery notes (`notes`) for orders that have delivery instructions. Show the 10 most recent orders.


**Hint 1:** Use `IS NOT NULL` to filter only orders where notes is not empty.


??? success "Answer"
    ```sql
    SELECT order_number, notes
    FROM orders
    WHERE notes IS NOT NULL
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | order_number | notes |
    |---|---|
    | ORD-20251231-37543 | Please knock gently |
    | ORD-20251231-37542 | Deliver to the office front desk |
    | ORD-20251231-37546 | Leave with the doorman/concierge |
    | ORD-20251231-37547 | Handle with care — fragile |
    | ORD-20251231-37549 | Please call before delivery |
    | ORD-20251231-37550 | Put in the mailbox/parcel locker |
    | ORD-20251231-37551 | Put in the mailbox/parcel locker |


---


### 5. Find the number of cancelled orders (where `cancelled_at` is


Find the number of cancelled orders (where `cancelled_at` is not NULL).


**Hint 1:** If `cancelled_at IS NOT NULL`, it means the cancellation date was recorded, i.e., the order was cancelled.


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS cancelled_count
    FROM orders
    WHERE cancelled_at IS NOT NULL;
    ```


    **Result** (1 rows)

    | cancelled_count |
    |---|
    | 1859 |


---


### 6. Query the name and brand of products that have no specificat


Query the name and brand of products that have no specification information (`specs`).


**Hint 1:** Use `specs IS NULL` to find products with missing specification information.


??? success "Answer"
    ```sql
    SELECT name, brand
    FROM products
    WHERE specs IS NULL;
    ```


    **Result** (top 7 of 168 rows)

    | name | brand |
    |---|---|
    | Logitech G715 White | Logitech |
    | Sony WH-CH720N Silver | Sony |
    | be quiet! Light Base 900 | be quiet! |
    | TP-Link TG-3468 Silver | TP-Link |
    | MSI MAG X870E TOMAHAWK WIFI White | MSI |
    | WD Elements 2TB Black | WD |
    | Netgear Nighthawk RS700S Black | Netgear |


---


### 7. Query the name and gender of customers, displaying 'N/A' whe


Query the name and gender of customers, displaying 'N/A' when gender is NULL.


**Hint 1:** `COALESCE(column, replacement)` returns the replacement value when the column is NULL.


??? success "Answer"
    ```sql
    SELECT name, COALESCE(gender, '미입력') AS gender
    FROM customers;
    ```


    **Result** (top 7 of 5,230 rows)

    | name | gender |
    |---|---|
    | Joshua Atkins | M |
    | Danny Johnson | 미입력 |
    | Adam Moore | M |
    | Virginia Steele | F |
    | Jared Vazquez | M |
    | Benjamin Skinner | M |
    | Ashley Jones | F |


---


### 8. Query the order number and delivery notes, displaying 'None'


Query the order number and delivery notes, displaying 'None' when notes are missing. Show only the 10 most recent orders.


**Hint 1:** Use `IFNULL(notes, 'None')` or `COALESCE(notes, 'None')`. Both work in SQLite.


??? success "Answer"
    ```sql
    SELECT order_number, IFNULL(notes, '없음') AS notes
    FROM orders
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | order_number | notes |
    |---|---|
    | ORD-20251231-37555 | 없음 |
    | ORD-20251231-37543 | Please knock gently |
    | ORD-20251231-37552 | 없음 |
    | ORD-20251231-37548 | 없음 |
    | ORD-20251231-37542 | Deliver to the office front desk |
    | ORD-20251231-37546 | Leave with the doorman/concierge |
    | ORD-20251231-37547 | Handle with care — fragile |


---


### 9. Query the name, price, and discontinuation date of products 


Query the name, price, and discontinuation date of products that have a discontinuation date (`discontinued_at`).


**Hint 1:** If `discontinued_at IS NOT NULL`, the product has been discontinued.


??? success "Answer"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE discontinued_at IS NOT NULL;
    ```


    **Result** (top 7 of 62 rows)

    | name | price | discontinued_at |
    |---|---|---|
    | Sony WH-CH720N Silver | 445,700.00 | 2023-09-21 01:03:38 |
    | WD Elements 2TB Black | 247,100.00 | 2024-08-25 09:29:10 |
    | JBL Quantum ONE White | 239,900.00 | 2023-06-01 06:11:13 |
    | Jooyon Rionine i7 System Silver | 810,300.00 | 2023-05-08 03:08:52 |
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 | 2017-05-15 20:10:25 |
    | Logitech G713 Silver | 151,000.00 | 2021-05-03 13:07:12 |
    | Samsung DDR4 32GB PC4-25600 | 91,000.00 | 2018-08-03 21:40:45 |


---


### 10. Find the number of orders that have not been confirmed (`com


Find the number of orders that have not been confirmed (`completed_at`) and have not been cancelled either.


**Hint 1:** Use `completed_at IS NULL AND cancelled_at IS NULL` to find rows where both columns are NULL.


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS pending_count
    FROM orders
    WHERE completed_at IS NULL
      AND cancelled_at IS NULL;
    ```


    **Result** (1 rows)

    | pending_count |
    |---|
    | 1305 |


---


### 11. Query the name, birth date, and gender of customers, display


Query the name, birth date, and gender of customers, displaying 'Unknown' for NULL birth dates and 'Not specified' for NULL genders. Show only the top 20 rows.


**Hint 1:** Apply `COALESCE` individually to each column.


??? success "Answer"
    ```sql
    SELECT name,
           COALESCE(birth_date, '정보없음') AS birth_date,
           COALESCE(gender, '미선택') AS gender
    FROM customers
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | name | birth_date | gender |
    |---|---|---|
    | Joshua Atkins | 1995-02-06 | M |
    | Danny Johnson | 1995-06-12 | 미선택 |
    | Adam Moore | 1998-05-02 | M |
    | Virginia Steele | 1994-12-02 | F |
    | Jared Vazquez | 1989-12-22 | M |
    | Benjamin Skinner | 1991-05-12 | M |
    | Ashley Jones | 정보없음 | F |


---


### 12. Query the name and weight of products, replacing NULL weight


Query the name and weight of products, replacing NULL weight (`weight_grams`) with 0. Show the 10 heaviest products.


**Hint 1:** Replace NULL with 0 using `COALESCE(weight_grams, 0)`, then sort.


??? success "Answer"
    ```sql
    SELECT name, COALESCE(weight_grams, 0) AS weight_grams
    FROM products
    ORDER BY weight_grams DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | weight_grams |
    |---|---|
    | ASUS ROG Strix GT35 | 19,449 |
    | Hansung BossMonster DX7700 White | 19,250 |
    | ASUS ROG Strix G16CH White | 16,624 |
    | Hansung BossMonster DX9900 Silver | 14,892 |
    | ASUS ROG Strix G16CH Silver | 14,308 |
    | CyberPower OR1500LCDRT2U Black | 14,045 |
    | Jooyon Rionine Mini PC | 13,062 |


---


### 13. Query the total number of customers and the number of custom


Query the total number of customers and the number of customers with a birth date entered, in a single query.


**Hint 1:** `COUNT(*)` counts all rows, while `COUNT(column)` counts only rows where the column is not NULL.


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_customers,
           COUNT(birth_date) AS has_birth_date
    FROM customers;
    ```


    **Result** (1 rows)

    | total_customers | has_birth_date |
    |---|---|
    | 5230 | 4492 |


---


### 14. Query the total number of orders, the number of orders with 


Query the total number of orders, the number of orders with delivery notes, and the number of confirmed orders in a single query.


**Hint 1:** Applying `COUNT` to each column like `COUNT(notes)` and `COUNT(completed_at)` counts only non-NULL rows.


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_orders,
           COUNT(notes) AS has_notes,
           COUNT(completed_at) AS completed
    FROM orders;
    ```


    **Result** (1 rows)

    | total_orders | has_notes | completed |
    |---|---|---|
    | 37,557 | 13,219 | 34,393 |


---


### 15. Sort customers by last login date in descending order, but p


Sort customers by last login date in descending order, but place customers with no login history (NULL) at the end. Show only the top 20 rows.


**Hint 1:** In SQLite, using `ORDER BY column DESC` places NULLs at the end. Alternatively, use `ORDER BY column IS NULL, column DESC` for explicit control.


??? success "Answer"
    ```sql
    SELECT name, last_login_at
    FROM customers
    ORDER BY last_login_at IS NULL, last_login_at DESC
    LIMIT 20;
    ```


    **Result** (top 7 of 20 rows)

    | name | last_login_at |
    |---|---|
    | Jennifer Mcgrath | 2025-12-30 23:53:45 |
    | David Barnes | 2025-12-30 23:19:27 |
    | Robert Simmons | 2025-12-30 23:16:24 |
    | Paul Hanson | 2025-12-30 22:54:11 |
    | Nicholas Richardson | 2025-12-30 22:08:46 |
    | Olivia Watson | 2025-12-30 21:42:46 |
    | Erin Pena | 2025-12-30 21:04:31 |


---


### 16. Sort products by discontinuation date in ascending order, bu


Sort products by discontinuation date in ascending order, but place non-discontinued products (NULL) at the end. Show only the top 10 rows.


**Hint 1:** Use `ORDER BY discontinued_at IS NULL, discontinued_at ASC` to push NULLs to the end.


??? success "Answer"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    ORDER BY discontinued_at IS NULL, discontinued_at ASC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | price | discontinued_at |
    |---|---|---|
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 | 2017-05-15 20:10:25 |
    | Samsung DDR4 32GB PC4-25600 | 91,000.00 | 2018-08-03 21:40:45 |
    | ASUS PRIME Z890-A WIFI Silver | 727,700.00 | 2019-08-25 16:52:30 |
    | SAPPHIRE NITRO+ RX 7900 XTX Black | 867,300.00 | 2020-02-06 04:58:03 |
    | Lenovo IdeaPad Flex 5 White | 1,657,300.00 | 2020-05-08 01:59:34 |
    | Samsung Galaxy Book5 Pro Black | 1,739,900.00 | 2020-06-23 23:10:47 |
    | Microsoft Ergonomic Keyboard Silver | 45,900.00 | 2020-09-06 05:07:08 |


---


### 17. Find the customer count and birth date completion rate (%) p


Find the customer count and birth date completion rate (%) per tier. Round the rate to 1 decimal place.


**Hint 1:** Calculate the non-NULL ratio with `COUNT(birth_date) * 100.0 / COUNT(*)`. Aggregate by tier with `GROUP BY grade`.


??? success "Answer"
    ```sql
    SELECT grade,
           COUNT(*) AS total,
           COUNT(birth_date) AS has_birth,
           ROUND(COUNT(birth_date) * 100.0 / COUNT(*), 1) AS birth_rate_pct
    FROM customers
    GROUP BY grade
    ORDER BY birth_rate_pct DESC;
    ```


    **Result** (4 rows)

    | grade | total | has_birth | birth_rate_pct |
    |---|---|---|---|
    | VIP | 368 | 326 | 88.60 |
    | GOLD | 524 | 460 | 87.80 |
    | SILVER | 479 | 416 | 86.80 |
    | BRONZE | 3859 | 3290 | 85.30 |


---


### 18. Find the customer count per signup channel (`acquisition_cha


Find the customer count per signup channel (`acquisition_channel`), displaying 'Unclassified' for NULL values.


**Hint 1:** Use `COALESCE(acquisition_channel, 'Unclassified')` in both `SELECT` and `GROUP BY`.


??? success "Answer"
    ```sql
    SELECT COALESCE(acquisition_channel, '미분류') AS channel,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY COALESCE(acquisition_channel, '미분류')
    ORDER BY customer_count DESC;
    ```


    **Result** (5 rows)

    | channel | customer_count |
    |---|---|
    | search_ad | 1543 |
    | social | 1425 |
    | organic | 1146 |
    | referral | 708 |
    | direct | 408 |


---


### 19. Find the order count and delivery notes completion rate (%) 


Find the order count and delivery notes completion rate (%) per order status.


**Hint 1:** Calculate the non-NULL ratio of notes with `COUNT(notes) * 100.0 / COUNT(*)`.


??? success "Answer"
    ```sql
    SELECT status,
           COUNT(*) AS order_count,
           ROUND(COUNT(notes) * 100.0 / COUNT(*), 1) AS notes_rate_pct
    FROM orders
    GROUP BY status
    ORDER BY order_count DESC;
    ```


    **Result** (top 7 of 9 rows)

    | status | order_count | notes_rate_pct |
    |---|---|---|
    | confirmed | 34,393 | 35.30 |
    | cancelled | 1859 | 34.30 |
    | return_requested | 507 | 33.10 |
    | returned | 493 | 34.90 |
    | delivered | 125 | 28.80 |
    | pending | 82 | 37.80 |
    | shipped | 51 | 31.40 |


---


### 20. Query product name, price, and weight, but when weight is NU


Query product name, price, and weight, but when weight is NULL, display an estimated weight calculated as price / 10 (assuming 1,000 won per 100g). Name the column `estimated_weight`.


**Hint 1:** Use `COALESCE(weight_grams, alternative_calculation)` to apply the alternative calculation only when NULL.


??? success "Answer"
    ```sql
    SELECT name,
           price,
           COALESCE(weight_grams, CAST(price / 10 AS INTEGER)) AS estimated_weight
    FROM products
    ORDER BY estimated_weight DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | price | estimated_weight |
    |---|---|---|
    | Windows 11 Pro Silver | 423,000.00 | 42,300 |
    | Adobe Creative Cloud 1-Year Silver | 327,300.00 | 32,730 |
    | Hancom Office 2024 Enterprise Silver | 241,400.00 | 24,140 |
    | Windows 11 Home Black | 208,600.00 | 20,860 |
    | ASUS ROG Strix GT35 | 3,296,800.00 | 19,449 |
    | Hansung BossMonster DX7700 White | 1,579,400.00 | 19,250 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 | 16,624 |


---


### 21. Query the NULL count for multiple columns in the customers t


Query the NULL count for multiple columns in the customers table at once. Find the NULL count for birth_date, gender, last_login_at, and acquisition_channel.


**Hint 1:** Calculate the NULL count for each column with `COUNT(*) - COUNT(column)`.


??? success "Answer"
    ```sql
    SELECT COUNT(*) - COUNT(birth_date) AS birth_null,
           COUNT(*) - COUNT(gender) AS gender_null,
           COUNT(*) - COUNT(last_login_at) AS login_null,
           COUNT(*) - COUNT(acquisition_channel) AS channel_null
    FROM customers;
    ```


    **Result** (1 rows)

    | birth_null | gender_null | login_null | channel_null |
    |---|---|---|---|
    | 738 | 529 | 281 | 0 |


---


### 22. Find the missing rate (%) for each nullable column in the cu


Find the missing rate (%) for each nullable column in the customers table. Display to 1 decimal place.


**Hint 1:** Calculate the missing rate with `(COUNT(*) - COUNT(column)) * 100.0 / COUNT(*)`.


??? success "Answer"
    ```sql
    SELECT ROUND((COUNT(*) - COUNT(birth_date)) * 100.0 / COUNT(*), 1) AS birth_missing_pct,
           ROUND((COUNT(*) - COUNT(gender)) * 100.0 / COUNT(*), 1) AS gender_missing_pct,
           ROUND((COUNT(*) - COUNT(last_login_at)) * 100.0 / COUNT(*), 1) AS login_missing_pct,
           ROUND((COUNT(*) - COUNT(acquisition_channel)) * 100.0 / COUNT(*), 1) AS channel_missing_pct
    FROM customers;
    ```


    **Result** (1 rows)

    | birth_missing_pct | gender_missing_pct | login_missing_pct | channel_missing_pct |
    |---|---|---|---|
    | 14.10 | 10.10 | 5.40 | 0.0 |


---


### 23. Find the NULL rate (%) for notes, completed_at, and cancelle


Find the NULL rate (%) for notes, completed_at, and cancelled_at in the orders table.


**Hint 1:** Apply the same pattern from Problem 22 to the orders table.


??? success "Answer"
    ```sql
    SELECT ROUND((COUNT(*) - COUNT(notes)) * 100.0 / COUNT(*), 1) AS notes_missing_pct,
           ROUND((COUNT(*) - COUNT(completed_at)) * 100.0 / COUNT(*), 1) AS completed_missing_pct,
           ROUND((COUNT(*) - COUNT(cancelled_at)) * 100.0 / COUNT(*), 1) AS cancelled_missing_pct
    FROM orders;
    ```


    **Result** (1 rows)

    | notes_missing_pct | completed_missing_pct | cancelled_missing_pct |
    |---|---|---|
    | 64.80 | 8.40 | 95.10 |


---


### 24. Find the tier distribution of customers whose gender is NULL


Find the tier distribution of customers whose gender is NULL. Show the count and percentage (%) per tier.


**Hint 1:** Filter with `WHERE gender IS NULL`, then aggregate with `GROUP BY grade`. The percentage is relative to the total number of NULL-gender customers.


??? success "Answer"
    ```sql
    SELECT grade,
           COUNT(*) AS cnt,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM customers
    WHERE gender IS NULL
    GROUP BY grade
    ORDER BY cnt DESC;
    ```


    **Result** (4 rows)

    | grade | cnt | pct |
    |---|---|---|
    | BRONZE | 429 | 81.10 |
    | SILVER | 45 | 8.50 |
    | GOLD | 41 | 7.80 |
    | VIP | 14 | 2.60 |


---


### 25. Find the number of customers where both birth_date and gende


Find the number of customers where both birth_date and gender are NULL. Also find the number of customers where at least one of them is NULL.


**Hint 1:** Use `AND` for the "both NULL" condition and `OR` for the "at least one NULL" condition.


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total,
           SUM(CASE WHEN birth_date IS NULL AND gender IS NULL THEN 1 ELSE 0 END) AS both_null,
           SUM(CASE WHEN birth_date IS NULL OR gender IS NULL THEN 1 ELSE 0 END) AS any_null
    FROM customers;
    ```


    **Result** (1 rows)

    | total | both_null | any_null |
    |---|---|---|
    | 5230 | 87 | 1180 |


---


### 26. Compare the number of VIP-tier customers with NULL signup ch


Compare the number of VIP-tier customers with NULL signup channel versus those with a signup channel.


**Hint 1:** Apply different `WHERE` conditions to two `COUNT` expressions, or use filtered COUNTs in a single query.


??? success "Answer"
    ```sql
    SELECT '경로없음' AS channel_status,
           COUNT(*) AS vip_count
    FROM customers
    WHERE acquisition_channel IS NULL AND grade = 'VIP'
    UNION ALL
    SELECT '경로있음',
           COUNT(*)
    FROM customers
    WHERE acquisition_channel IS NOT NULL AND grade = 'VIP';
    ```


    **Result** (2 rows)

    | channel_status | vip_count |
    |---|---|
    | 경로없음 | 0 |
    | 경로있음 | 368 |


---


### 27. Find the number of products where either description or spec


Find the number of products where either description or specs is NULL, and also the number where both are NULL.


**Hint 1:** Combine `OR` and `AND` to create two different conditions.


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_products,
           SUM(CASE WHEN description IS NULL OR specs IS NULL THEN 1 ELSE 0 END) AS any_null,
           SUM(CASE WHEN description IS NULL AND specs IS NULL THEN 1 ELSE 0 END) AS both_null
    FROM products;
    ```


    **Result** (1 rows)

    | total_products | any_null | both_null |
    |---|---|---|
    | 280 | 168 | 0 |


---


### 28. Find the order count and delivery notes completion rate (%) 


Find the order count and delivery notes completion rate (%) per year. Extract the year with `SUBSTR(ordered_at, 1, 4)`.


**Hint 1:** Group by year with `GROUP BY SUBSTR(ordered_at, 1, 4)`, then calculate the completion rate with `COUNT(notes) * 100.0 / COUNT(*)`.


??? success "Answer"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 4) AS year,
           COUNT(*) AS order_count,
           ROUND(COUNT(notes) * 100.0 / COUNT(*), 1) AS notes_rate_pct
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```


    **Result** (top 7 of 10 rows)

    | year | order_count | notes_rate_pct |
    |---|---|---|
    | 2016 | 416 | 37.00 |
    | 2017 | 709 | 33.90 |
    | 2018 | 1319 | 34.60 |
    | 2019 | 2589 | 34.50 |
    | 2020 | 4319 | 34.60 |
    | 2021 | 5841 | 34.70 |
    | 2022 | 5203 | 36.30 |


---


### 29. Find the brand-wise count of products where weight (`weight_


Find the brand-wise count of products where weight (`weight_grams`) is NULL, showing only brands with 5 or more such products.


**Hint 1:** Filter with `WHERE weight_grams IS NULL`, then apply `GROUP BY brand` and `HAVING COUNT(*) >= 5`.


??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS null_weight_count
    FROM products
    WHERE weight_grams IS NULL
    GROUP BY brand
    HAVING COUNT(*) >= 5
    ORDER BY null_weight_count DESC;
    ```


---


### 30. Calculate a data completeness score for each customer. Count


Calculate a data completeness score for each customer. Count the number of non-NULL columns among birth_date, gender, last_login_at, and acquisition_channel (score 0-4). Find the customer count per score.


**Hint 1:** `(column IS NOT NULL)` returns TRUE=1 and FALSE=0 in SQLite. Adding all four gives the completeness score.


??? success "Answer"
    ```sql
    SELECT (birth_date IS NOT NULL)
         + (gender IS NOT NULL)
         + (last_login_at IS NOT NULL)
         + (acquisition_channel IS NOT NULL) AS completeness_score,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY completeness_score
    ORDER BY completeness_score;
    ```


    **Result** (4 rows)

    | completeness_score | customer_count |
    |---|---|
    | 1 | 5 |
    | 2 | 143 |
    | 3 | 1247 |
    | 4 | 3835 |


---
