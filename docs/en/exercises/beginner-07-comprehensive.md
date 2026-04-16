# Comprehensive Exercises

!!! info "Tables"

    `products` — Products (name, price, stock, brand)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `reviews` — Reviews (rating, content)  

    `payments` — Payments (method, amount, status)  

    `categories` — Categories (parent-child hierarchy)  

    `suppliers` — Suppliers (company, contact)  



!!! abstract "Concepts"

    `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `Aggregate functions`, `GROUP BY`, `HAVING`, `IS NULL`, `COALESCE`, `CASE`



### 1. Query the name, brand, and price of the top 5 most expensive


Query the name, brand, and price of the top 5 most expensive active products (`is_active = 1`).


**Hint 1:** This is a combination of `WHERE` filtering + `ORDER BY DESC` + `LIMIT`.


??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE is_active = 1
    ORDER BY price DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | name | brand | price |
    |---|---|---|
    | MacBook Air 15 M3 Silver | Apple | 5,481,100.00 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | ASUS | 4,496,700.00 |
    | Razer Blade 18 Black | Razer | 4,353,100.00 |
    | Razer Blade 16 Silver | Razer | 3,702,900.00 |
    | ASUS ROG Strix G16CH White | ASUS | 3,671,500.00 |


---


### 2. Query the name and last login date of VIP-tier customers who


Query the name and last login date of VIP-tier customers who have a login history, sorted by most recent, limited to 10 rows.


**Hint 1:** Combine two conditions with `WHERE grade = 'VIP' AND last_login_at IS NOT NULL`.


??? success "Answer"
    ```sql
    SELECT name, last_login_at
    FROM customers
    WHERE grade = 'VIP'
      AND last_login_at IS NOT NULL
    ORDER BY last_login_at DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | name | last_login_at |
    |---|---|
    | Leslie Mccoy | 2025-12-30 20:20:12 |
    | Christopher Morris | 2025-12-30 17:25:30 |
    | Angela Clements | 2025-12-30 17:24:28 |
    | Jordan Pearson | 2025-12-30 12:28:17 |
    | Mr. James Bean | 2025-12-30 02:06:50 |
    | Lindsay Douglas | 2025-12-30 00:15:41 |
    | Sandra Williams | 2025-12-29 21:08:21 |


---


### 3. Query the order number, order amount, and cancellation date 


Query the order number, order amount, and cancellation date of cancelled orders in 2024, sorted by most recent cancellation, limited to 10 rows.


**Hint 1:** Combine conditions with `WHERE ordered_at LIKE '2024%' AND cancelled_at IS NOT NULL`.


??? success "Answer"
    ```sql
    SELECT order_number, total_amount, cancelled_at
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND cancelled_at IS NOT NULL
    ORDER BY cancelled_at DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | order_number | total_amount | cancelled_at |
    |---|---|---|
    | ORD-20241231-31231 | 1,905,400.00 | 2025-01-01 23:25:27 |
    | ORD-20241229-31194 | 657,900.00 | 2024-12-31 11:37:44 |
    | ORD-20241228-31179 | 68,900.00 | 2024-12-30 00:01:41 |
    | ORD-20241228-31177 | 289,100.00 | 2024-12-28 21:35:05 |
    | ORD-20241226-31148 | 69,400.00 | 2024-12-27 20:44:43 |
    | ORD-20241225-31134 | 2,841,800.00 | 2024-12-26 18:43:50 |
    | ORD-20241223-31096 | 234,768.00 | 2024-12-25 19:56:46 |


---


### 4. Find the count and average rating of reviews with a rating o


Find the count and average rating of reviews with a rating of 4 or higher. Display the average to 2 decimal places.


**Hint 1:** Filter with `WHERE rating >= 4`, then use `COUNT(*)` and `ROUND(AVG(rating), 2)`.


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS high_rating_count,
           ROUND(AVG(rating), 2) AS avg_rating
    FROM reviews
    WHERE rating >= 4;
    ```


    **Result** (1 rows)

    | high_rating_count | avg_rating |
    |---|---|
    | 6008 | 4.57 |


---


### 5. Find the number of active products per brand, showing only b


Find the number of active products per brand, showing only brands with 10 or more, sorted by product count descending.


**Hint 1:** This is a combination of `WHERE is_active = 1` + `GROUP BY brand` + `HAVING COUNT(*) >= 10`.


??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY product_count DESC;
    ```


    **Result** (6 rows)

    | brand | product_count |
    |---|---|
    | Samsung | 21 |
    | ASUS | 21 |
    | MSI | 12 |
    | TP-Link | 11 |
    | Logitech | 11 |
    | LG | 11 |


---


### 6. Find the average points per customer tier, displaying the ti


Find the average points per customer tier, displaying the tier in Korean. Sort by average points descending.


**Hint 1:** This is a combination of `CASE` for tier conversion + `GROUP BY` + `AVG` + `ORDER BY`.


??? success "Answer"
    ```sql
    SELECT CASE grade
               WHEN 'VIP' THEN 'VIP'
               WHEN 'GOLD' THEN '골드'
               WHEN 'SILVER' THEN '실버'
               WHEN 'BRONZE' THEN '브론즈'
           END AS grade_kr,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY grade
    ORDER BY avg_points DESC;
    ```


    **Result** (4 rows)

    | grade_kr | avg_points |
    |---|---|
    | VIP | 407,015.00 |
    | 골드 | 147,711.00 |
    | 실버 | 95,042.00 |
    | 브론즈 | 16,779.00 |


---


### 7. Find the total payment amount and count per payment method, 


Find the total payment amount and count per payment method, showing only methods with a total of 1 billion or more.


**Hint 1:** This is a combination of `GROUP BY method` + `HAVING SUM(amount) >= 1000000000`.


??? success "Answer"
    ```sql
    SELECT method,
           COUNT(*) AS payment_count,
           ROUND(SUM(amount)) AS total_amount
    FROM payments
    GROUP BY method
    HAVING SUM(amount) >= 1000000000
    ORDER BY total_amount DESC;
    ```


    **Result** (6 rows)

    | method | payment_count | total_amount |
    |---|---|---|
    | card | 16,841 | 17,004,951,634.00 |
    | kakao_pay | 7486 | 7,563,829,668.00 |
    | naver_pay | 5715 | 5,998,835,720.00 |
    | bank_transfer | 3718 | 3,753,149,013.00 |
    | point | 1921 | 1,951,369,604.00 |
    | virtual_account | 1876 | 1,911,359,424.00 |


---


### 8. Find the count per tier for customers with a NULL signup cha


Find the count per tier for customers with a NULL signup channel. Use CASE to sort tiers in order starting from VIP.


**Hint 1:** This is a combination of `WHERE acquisition_channel IS NULL` + `GROUP BY grade` + `ORDER BY CASE`.


??? success "Answer"
    ```sql
    SELECT grade, COUNT(*) AS customer_count
    FROM customers
    WHERE acquisition_channel IS NULL
    GROUP BY grade
    ORDER BY CASE grade
                 WHEN 'VIP' THEN 1
                 WHEN 'GOLD' THEN 2
                 WHEN 'SILVER' THEN 3
                 WHEN 'BRONZE' THEN 4
             END;
    ```


---


### 9. Find the count, average order amount, and delivery notes com


Find the count, average order amount, and delivery notes completion rate (%) per order status. Sort by count descending.


**Hint 1:** Calculate the completion rate with `COUNT(notes) * 100.0 / COUNT(*)`. This leverages the relationship between NULL and aggregate functions.


??? success "Answer"
    ```sql
    SELECT status,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount,
           ROUND(COUNT(notes) * 100.0 / COUNT(*), 1) AS notes_rate_pct
    FROM orders
    GROUP BY status
    ORDER BY order_count DESC;
    ```


    **Result** (top 7 of 9 rows)

    | status | order_count | avg_amount | notes_rate_pct |
    |---|---|---|---|
    | confirmed | 34,393 | 999,814.00 | 35.30 |
    | cancelled | 1859 | 1,045,258.00 | 34.30 |
    | return_requested | 507 | 1,600,567.00 | 33.10 |
    | returned | 493 | 1,337,616.00 | 34.90 |
    | delivered | 125 | 1,566,146.00 | 28.80 |
    | pending | 82 | 1,063,783.00 | 37.80 |
    | shipped | 51 | 1,452,364.00 | 31.40 |


---


### 10. Classify products by stock status (Out of stock/Low/Normal/S


Classify products by stock status (Out of stock/Low/Normal/Sufficient) and find the product count and average price per group. Active products only.


**Hint 1:** This is a combination of `WHERE is_active = 1` + `CASE` for stock classification + `GROUP BY` + aggregate functions.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN stock_qty = 0 THEN '품절'
               WHEN stock_qty <= 10 THEN '부족'
               WHEN stock_qty <= 100 THEN '보통'
               ELSE '충분'
           END AS stock_status,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price
    FROM products
    WHERE is_active = 1
    GROUP BY stock_status
    ORDER BY product_count DESC;
    ```


    **Result** (4 rows)

    | stock_status | product_count | avg_price |
    |---|---|---|
    | 충분 | 181 | 669,318.00 |
    | 보통 | 34 | 662,359.00 |
    | 부족 | 2 | 50,900.00 |
    | 품절 | 1 | 23,000.00 |


---


### 11. Find the active product count, average price, and average ma


Find the active product count, average price, and average margin rate (%) per brand. Show only brands with 5+ products, sorted by average margin rate descending.


**Hint 1:** Margin rate = `(price - cost_price) * 100.0 / price`. This is a combination of `WHERE` + `GROUP BY` + `HAVING` + `ORDER BY`.


??? success "Answer"
    ```sql
    SELECT brand,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price,
           ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 5
    ORDER BY avg_margin_pct DESC;
    ```


    **Result** (top 7 of 17 rows)

    | brand | product_count | avg_price | avg_margin_pct |
    |---|---|---|---|
    | Microsoft | 5 | 129,260.00 | 38.20 |
    | SteelSeries | 7 | 212,643.00 | 31.60 |
    | TP-Link | 11 | 128,764.00 | 30.30 |
    | NZXT | 5 | 213,100.00 | 29.70 |
    | Logitech | 11 | 115,127.00 | 28.00 |
    | ASUS | 21 | 1,589,552.00 | 28.00 |
    | ASRock | 9 | 493,244.00 | 25.60 |


---


### 12. Find the order count, total revenue, average order amount, a


Find the order count, total revenue, average order amount, and cancellation count per year. The cancellation count is the number of rows where cancelled_at is not NULL.


**Hint 1:** Extract the year with `SUBSTR(ordered_at, 1, 4)`. `COUNT(cancelled_at)` counts only non-NULL rows.


??? success "Answer"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 4) AS year,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue,
           ROUND(AVG(total_amount)) AS avg_amount,
           COUNT(cancelled_at) AS cancelled_count
    FROM orders
    GROUP BY year
    ORDER BY year;
    ```


    **Result** (top 7 of 10 rows)

    | year | order_count | total_revenue | avg_amount | cancelled_count |
    |---|---|---|---|---|
    | 2016 | 416 | 331,746,909.00 | 797,469.00 | 15 |
    | 2017 | 709 | 653,085,068.00 | 921,135.00 | 41 |
    | 2018 | 1319 | 1,249,197,907.00 | 947,080.00 | 64 |
    | 2019 | 2589 | 2,620,111,601.00 | 1,012,017.00 | 116 |
    | 2020 | 4319 | 4,468,755,264.00 | 1,034,674.00 | 191 |
    | 2021 | 5841 | 6,044,718,738.00 | 1,034,877.00 | 270 |
    | 2022 | 5203 | 5,302,071,035.00 | 1,019,041.00 | 256 |


---


### 13. Find the customer count, VIP rate (%), and average points pe


Find the customer count, VIP rate (%), and average points per signup channel. Display 'Unclassified' for NULL channels, sorted by customer count descending.


**Hint 1:** This is a combination of `COALESCE` for NULL replacement + `SUM(CASE WHEN grade = 'VIP' THEN 1 ELSE 0 END)` for VIP count aggregation + `GROUP BY`.


??? success "Answer"
    ```sql
    SELECT COALESCE(acquisition_channel, '미분류') AS channel,
           COUNT(*) AS customer_count,
           ROUND(SUM(CASE WHEN grade = 'VIP' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS vip_rate_pct,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY COALESCE(acquisition_channel, '미분류')
    ORDER BY customer_count DESC;
    ```


    **Result** (5 rows)

    | channel | customer_count | vip_rate_pct | avg_points |
    |---|---|---|---|
    | search_ad | 1543 | 7.50 | 62,449.00 |
    | social | 1425 | 6.20 | 54,311.00 |
    | organic | 1146 | 7.10 | 76,371.00 |
    | referral | 708 | 7.20 | 66,944.00 |
    | direct | 408 | 7.80 | 70,562.00 |


---


### 14. Find the monthly order count and average order amount for 20


Find the monthly order count and average order amount for 2024, also displaying the season (Spring/Summer/Fall/Winter).


**Hint 1:** This is a combination of `SUBSTR` for month extraction + `CASE` for season classification + `GROUP BY` + aggregation.


??? success "Answer"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 7) AS month,
           CASE
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (3, 4, 5) THEN '봄'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (6, 7, 8) THEN '여름'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (9, 10, 11) THEN '가을'
               ELSE '겨울'
           END AS season,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```


    **Result** (top 7 of 12 rows)

    | month | season | order_count | avg_amount |
    |---|---|---|---|
    | 2024-01 | 겨울 | 346 | 925,700.00 |
    | 2024-02 | 겨울 | 465 | 966,554.00 |
    | 2024-03 | 봄 | 601 | 948,084.00 |
    | 2024-04 | 봄 | 506 | 980,283.00 |
    | 2024-05 | 봄 | 415 | 1,140,347.00 |
    | 2024-06 | 여름 | 415 | 962,619.00 |
    | 2024-07 | 여름 | 414 | 926,084.00 |


---


### 15. Aggregate reviews by rating, displaying the Korean label, co


Aggregate reviews by rating, displaying the Korean label, count, overall percentage (%), and title completion rate (%) for each rating. Sort by rating descending.


**Hint 1:** This is a combination of `CASE` for rating labels + `COUNT(*)` + percentage calculation + `COUNT(title)`.


??? success "Answer"
    ```sql
    SELECT rating,
           CASE rating
               WHEN 5 THEN '최고'
               WHEN 4 THEN '좋음'
               WHEN 3 THEN '보통'
               WHEN 2 THEN '별로'
               WHEN 1 THEN '최악'
           END AS rating_label,
           COUNT(*) AS review_count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct,
           ROUND(COUNT(title) * 100.0 / COUNT(*), 1) AS title_rate_pct
    FROM reviews
    GROUP BY rating
    ORDER BY rating DESC;
    ```


    **Result** (5 rows)

    | rating | rating_label | review_count | pct | title_rate_pct |
    |---|---|---|---|---|
    | 5 | 최고 | 3433 | 40.20 | 80.80 |
    | 4 | 좋음 | 2575 | 30.10 | 80.50 |
    | 3 | 보통 | 1265 | 14.80 | 80.10 |
    | 2 | 별로 | 839 | 9.80 | 80.30 |
    | 1 | 최악 | 434 | 5.10 | 80.60 |


---


### 16. Find the product count, average stock, and discontinuation r


Find the product count, average stock, and discontinuation rate (%) per price tier (Budget/Mid-low/Mid/Premium). The discontinuation rate is the percentage of is_active=0.


**Hint 1:** This is a combination of `CASE` for price tier classification + `SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END)` for discontinuation count + `GROUP BY`.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN price < 100000 THEN '저가'
               WHEN price < 500000 THEN '중저가'
               WHEN price < 1000000 THEN '중가'
               ELSE '고가'
           END AS price_tier,
           COUNT(*) AS product_count,
           ROUND(AVG(stock_qty)) AS avg_stock,
           ROUND(SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS discontinued_pct
    FROM products
    GROUP BY price_tier
    ORDER BY product_count DESC;
    ```


    **Result** (4 rows)

    | price_tier | product_count | avg_stock | discontinued_pct |
    |---|---|---|---|
    | 중저가 | 130 | 277.00 | 23.80 |
    | 고가 | 65 | 271.00 | 20.00 |
    | 저가 | 47 | 267.00 | 19.10 |
    | 중가 | 38 | 282.00 | 23.70 |


---


### 17. Query the customer count, average points, gender completion 


Query the customer count, average points, gender completion rate (%), and login experience rate (%) per tier in a single query. Tier order: VIP > GOLD > SILVER > BRONZE.


**Hint 1:** Use `COUNT(gender)` for gender completion count and `COUNT(last_login_at)` for login experience count. Use `ORDER BY CASE` for tier ordering.


??? success "Answer"
    ```sql
    SELECT grade,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points,
           ROUND(COUNT(gender) * 100.0 / COUNT(*), 1) AS gender_rate_pct,
           ROUND(COUNT(last_login_at) * 100.0 / COUNT(*), 1) AS login_rate_pct
    FROM customers
    GROUP BY grade
    ORDER BY CASE grade
                 WHEN 'VIP' THEN 1
                 WHEN 'GOLD' THEN 2
                 WHEN 'SILVER' THEN 3
                 WHEN 'BRONZE' THEN 4
             END;
    ```


    **Result** (4 rows)

    | grade | customer_count | avg_points | gender_rate_pct | login_rate_pct |
    |---|---|---|---|---|
    | VIP | 368 | 407,015.00 | 96.20 | 100.00 |
    | GOLD | 524 | 147,711.00 | 92.20 | 100.00 |
    | SILVER | 479 | 95,042.00 | 90.60 | 100.00 |
    | BRONZE | 3859 | 16,779.00 | 88.90 | 92.70 |


---


### 18. Classify orders into 3 status groups (Processing/Completed/C


Classify orders into 3 status groups (Processing/Completed/Cancelled-Returned) and find the count, total revenue, average shipping fee, and points-used count per group.


**Hint 1:** Classify groups with `CASE WHEN status IN (...)`. Count points-used orders with `SUM(CASE WHEN point_used > 0 THEN 1 ELSE 0 END)`.


??? success "Answer"
    ```sql
    SELECT CASE
               WHEN status IN ('pending', 'paid', 'preparing') THEN '처리중'
               WHEN status IN ('shipped', 'delivered', 'confirmed') THEN '완료'
               ELSE '취소/반품'
           END AS status_group,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue,
           ROUND(AVG(shipping_fee)) AS avg_shipping,
           SUM(CASE WHEN point_used > 0 THEN 1 ELSE 0 END) AS point_used_count
    FROM orders
    GROUP BY status_group
    ORDER BY order_count DESC;
    ```


    **Result** (3 rows)

    | status_group | order_count | total_revenue | avg_shipping | point_used_count |
    |---|---|---|---|---|
    | 완료 | 34,569 | 34,656,428,960.00 | 248.00 | 3439 |
    | 취소/반품 | 2859 | 3,414,067,056.00 | 208.00 | 291 |
    | 처리중 | 129 | 112,999,047.00 | 163.00 | 10 |


---


### 19. For card payments, find the payment count, average amount, a


For card payments, find the payment count, average amount, and installment usage rate (%) per card issuer. Exclude records where card issuer is NULL, and show only card issuers with 100+ payments.


**Hint 1:** Filter with `WHERE method = 'card' AND card_issuer IS NOT NULL`. Count installment payments with `SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END)`.


??? success "Answer"
    ```sql
    SELECT card_issuer,
           COUNT(*) AS payment_count,
           ROUND(AVG(amount)) AS avg_amount,
           ROUND(SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS installment_rate_pct
    FROM payments
    WHERE method = 'card'
      AND card_issuer IS NOT NULL
    GROUP BY card_issuer
    HAVING COUNT(*) >= 100
    ORDER BY payment_count DESC;
    ```


    **Result** (7 rows)

    | card_issuer | payment_count | avg_amount | installment_rate_pct |
    |---|---|---|---|
    | Visa | 5098 | 993,811.00 | 48.50 |
    | Mastercard | 4039 | 1,063,479.00 | 47.90 |
    | American Express | 2513 | 1,040,512.00 | 48.50 |
    | Discover | 1710 | 990,777.00 | 48.60 |
    | Capital One | 1377 | 961,365.00 | 48.50 |
    | Chase | 1252 | 991,999.00 | 47.60 |
    | Citi | 852 | 901,753.00 | 48.00 |


---


### 20. Find the product count and active product rate (%) per suppl


Find the product count and active product rate (%) per supplier. Only include suppliers with 3+ products, sorted by active rate descending. Group by supplier_id.


**Hint 1:** This is a combination of `GROUP BY supplier_id` + `HAVING COUNT(*) >= 3` + `SUM(CASE WHEN is_active = 1 ...)` for active rate calculation + `ORDER BY`.


??? success "Answer"
    ```sql
    SELECT supplier_id,
           COUNT(*) AS product_count,
           SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_count,
           ROUND(SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS active_rate_pct
    FROM products
    GROUP BY supplier_id
    HAVING COUNT(*) >= 3
    ORDER BY active_rate_pct DESC;
    ```


    **Result** (top 7 of 32 rows)

    | supplier_id | product_count | active_count | active_rate_pct |
    |---|---|---|---|
    | 2 | 11 | 11 | 100.00 |
    | 17 | 6 | 6 | 100.00 |
    | 22 | 3 | 3 | 100.00 |
    | 24 | 5 | 5 | 100.00 |
    | 36 | 11 | 11 | 100.00 |
    | 37 | 5 | 5 | 100.00 |
    | 27 | 13 | 12 | 92.30 |


---


### 21. Find the active product count and average price per brand, s


Find the active product count and average price per brand, showing only brands with an average price of 1M+. Also display the price tier classification (Premium/Mainstream/Budget).


**Hint 1:** This is a combination of `WHERE is_active = 1` + `GROUP BY brand` + `HAVING AVG(price) >= 1000000` + `CASE` for price tier classification.


??? success "Answer"
    ```sql
    SELECT brand,
           COUNT(*) AS active_product_count,
           ROUND(AVG(price)) AS avg_price,
           CASE
               WHEN AVG(price) >= 2000000 THEN '프리미엄'
               WHEN AVG(price) >= 1000000 THEN '대중'
               ELSE '보급형'
           END AS brand_tier
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING AVG(price) >= 1000000
    ORDER BY avg_price DESC;
    ```


    **Result** (top 7 of 8 rows)

    | brand | active_product_count | avg_price | brand_tier |
    |---|---|---|---|
    | Apple | 2 | 2,815,400.00 | 프리미엄 |
    | Razer | 7 | 1,996,443.00 | 대중 |
    | Lenovo | 2 | 1,695,450.00 | 대중 |
    | Jooyon Tech | 3 | 1,614,633.00 | 대중 |
    | ASUS | 21 | 1,589,552.00 | 대중 |
    | BenQ | 1 | 1,476,300.00 | 대중 |
    | HP | 5 | 1,433,140.00 | 대중 |


---


### 22. 2024 monthly revenue analysis: Find the monthly order count,


2024 monthly revenue analysis: Find the monthly order count, total revenue, average order amount, cancellation rate (%), and free shipping rate (%).


**Hint 1:** Combine various aggregations. Cancellation rate = `COUNT(cancelled_at) / COUNT(*)`. Free shipping = percentage of orders with `shipping_fee = 0`.


??? success "Answer"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 7) AS month,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue,
           ROUND(AVG(total_amount)) AS avg_amount,
           ROUND(COUNT(cancelled_at) * 100.0 / COUNT(*), 1) AS cancel_rate_pct,
           ROUND(SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS free_ship_pct
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```


    **Result** (top 7 of 12 rows)

    | month | order_count | total_revenue | avg_amount | cancel_rate_pct | free_ship_pct |
    |---|---|---|---|---|---|
    | 2024-01 | 346 | 320,292,182.00 | 925,700.00 | 6.10 | 91.30 |
    | 2024-02 | 465 | 449,447,834.00 | 966,554.00 | 6.90 | 92.30 |
    | 2024-03 | 601 | 569,798,709.00 | 948,084.00 | 4.80 | 93.30 |
    | 2024-04 | 506 | 496,023,258.00 | 980,283.00 | 5.50 | 94.50 |
    | 2024-05 | 415 | 473,243,857.00 | 1,140,347.00 | 4.60 | 94.00 |
    | 2024-06 | 415 | 399,487,004.00 | 962,619.00 | 4.30 | 93.70 |
    | 2024-07 | 414 | 383,398,728.00 | 926,084.00 | 5.60 | 93.50 |


---


### 23. Customer segment analysis: Combine tier and activity status 


Customer segment analysis: Combine tier and activity status (Active/Dormant/Withdrawn) to find the customer count and average points per segment. Show only segments with 100+ customers.


**Hint 1:** Classify activity status with `CASE` (is_active=0 is Withdrawn, last_login_at IS NULL is Dormant, the rest is Active). Combine with `GROUP BY grade, activity_status`.


??? success "Answer"
    ```sql
    SELECT grade,
           CASE
               WHEN is_active = 0 THEN '탈퇴'
               WHEN last_login_at IS NULL THEN '휴면'
               ELSE '활동'
           END AS activity_status,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY grade, activity_status
    HAVING COUNT(*) >= 100
    ORDER BY CASE grade
                 WHEN 'VIP' THEN 1
                 WHEN 'GOLD' THEN 2
                 WHEN 'SILVER' THEN 3
                 WHEN 'BRONZE' THEN 4
             END,
             customer_count DESC;
    ```


    **Result** (6 rows)

    | grade | activity_status | customer_count | avg_points |
    |---|---|---|---|
    | VIP | 활동 | 368 | 407,015.00 |
    | GOLD | 활동 | 524 | 147,711.00 |
    | SILVER | 활동 | 479 | 95,042.00 |
    | BRONZE | 활동 | 2100 | 30,834.00 |
    | BRONZE | 탈퇴 | 1570 | 0.0 |
    | BRONZE | 휴면 | 189 | 0.0 |


---


### 24. Product data quality report: Find the product count, descrip


Product data quality report: Find the product count, description missing rate (%), specs missing rate (%), and weight missing rate (%) per brand. Only include brands with 10+ products, sorted by the overall missing rate (average of all three) descending.


**Hint 1:** Calculate each column's missing rate with `(COUNT(*) - COUNT(column)) * 100.0 / COUNT(*)`. Sort by the average of the three missing rates.


??? success "Answer"
    ```sql
    SELECT brand,
           COUNT(*) AS product_count,
           ROUND((COUNT(*) - COUNT(description)) * 100.0 / COUNT(*), 1) AS desc_missing_pct,
           ROUND((COUNT(*) - COUNT(specs)) * 100.0 / COUNT(*), 1) AS specs_missing_pct,
           ROUND((COUNT(*) - COUNT(weight_grams)) * 100.0 / COUNT(*), 1) AS weight_missing_pct
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY (
        (COUNT(*) - COUNT(description)) +
        (COUNT(*) - COUNT(specs)) +
        (COUNT(*) - COUNT(weight_grams))
    ) * 1.0 / COUNT(*) DESC;
    ```


    **Result** (7 rows)

    | brand | product_count | desc_missing_pct | specs_missing_pct | weight_missing_pct |
    |---|---|---|---|---|
    | TP-Link | 11 | 0.0 | 100.00 | 0.0 |
    | Logitech | 17 | 0.0 | 100.00 | 0.0 |
    | ASRock | 11 | 0.0 | 100.00 | 0.0 |
    | MSI | 13 | 0.0 | 61.50 | 0.0 |
    | ASUS | 26 | 0.0 | 30.80 | 0.0 |
    | Samsung | 25 | 0.0 | 24.00 | 0.0 |
    | LG | 11 | 0.0 | 0.0 | 0.0 |


---


### 25. Yearly customer signup analysis: Find the customer count, ge


Yearly customer signup analysis: Find the customer count, gender ratio (Male/Female/Unknown), and average points per signup year.


**Hint 1:** Calculate the male ratio with `SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)`. Also calculate the NULL gender ratio separately.


??? success "Answer"
    ```sql
    SELECT SUBSTR(created_at, 1, 4) AS join_year,
           COUNT(*) AS customer_count,
           ROUND(SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS male_pct,
           ROUND(SUM(CASE WHEN gender = 'F' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS female_pct,
           ROUND(SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS unknown_pct,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY join_year
    ORDER BY join_year;
    ```


    **Result** (top 7 of 10 rows)

    | join_year | customer_count | male_pct | female_pct | unknown_pct | avg_points |
    |---|---|---|---|---|---|
    | 2016 | 100 | 53.00 | 29.00 | 18.00 | 212,578.00 |
    | 2017 | 180 | 57.20 | 32.20 | 10.60 | 170,364.00 |
    | 2018 | 300 | 56.30 | 32.00 | 11.70 | 144,012.00 |
    | 2019 | 450 | 56.90 | 32.70 | 10.40 | 99,968.00 |
    | 2020 | 700 | 61.60 | 28.70 | 9.70 | 94,152.00 |
    | 2021 | 800 | 56.30 | 33.00 | 10.80 | 69,793.00 |
    | 2022 | 650 | 60.60 | 30.30 | 9.10 | 53,009.00 |


---


### 26. Discount analysis: For 2024 orders, combine discount status 


Discount analysis: For 2024 orders, combine discount status (Has discount/No discount) and amount tier (Small/Regular/Large/VIP-level) to find the count and average order amount.


**Hint 1:** Classify discount status with `CASE WHEN discount_amount > 0` and amount tier with `CASE WHEN total_amount < 50000`. Use both CASE expressions in `GROUP BY`.


??? success "Answer"
    ```sql
    SELECT CASE WHEN discount_amount > 0 THEN '할인있음' ELSE '할인없음' END AS has_discount,
           CASE
               WHEN total_amount < 50000 THEN '소액'
               WHEN total_amount < 200000 THEN '일반'
               WHEN total_amount < 1000000 THEN '고액'
               ELSE 'VIP급'
           END AS amount_tier,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY has_discount, amount_tier
    ORDER BY has_discount, avg_amount DESC;
    ```


    **Result** (top 7 of 8 rows)

    | has_discount | amount_tier | order_count | avg_amount |
    |---|---|---|---|
    | 할인없음 | VIP급 | 1314 | 2,190,896.00 |
    | 할인없음 | 고액 | 1498 | 447,381.00 |
    | 할인없음 | 일반 | 1435 | 121,632.00 |
    | 할인없음 | 소액 | 276 | 36,244.00 |
    | 할인있음 | VIP급 | 652 | 2,567,481.00 |
    | 할인있음 | 고액 | 398 | 481,555.00 |
    | 할인있음 | 일반 | 173 | 125,703.00 |


---


### 27. Product status by category: Find the total product count, ac


Product status by category: Find the total product count, active count, discontinued count, out-of-stock count, and average price per category_id. Only include categories with 5+ total products.


**Hint 1:** Use `SUM(CASE WHEN condition THEN 1 ELSE 0 END)` to aggregate each status count into separate columns.


??? success "Answer"
    ```sql
    SELECT category_id,
           COUNT(*) AS total,
           SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_count,
           SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS discontinued_count,
           SUM(CASE WHEN stock_qty = 0 THEN 1 ELSE 0 END) AS out_of_stock,
           ROUND(AVG(price)) AS avg_price
    FROM products
    GROUP BY category_id
    HAVING COUNT(*) >= 5
    ORDER BY total DESC;
    ```


    **Result** (top 7 of 31 rows)

    | category_id | total | active_count | discontinued_count | out_of_stock | avg_price |
    |---|---|---|---|---|---|
    | 18 | 13 | 10 | 3 | 0 | 529,754.00 |
    | 30 | 13 | 11 | 2 | 0 | 219,008.00 |
    | 43 | 12 | 9 | 3 | 0 | 277,150.00 |
    | 3 | 11 | 9 | 2 | 0 | 1,719,809.00 |
    | 31 | 11 | 10 | 1 | 0 | 158,482.00 |
    | 36 | 11 | 8 | 3 | 0 | 158,000.00 |
    | 37 | 11 | 7 | 4 | 0 | 41,064.00 |


---


### 28. Comprehensive payment method analysis: Find the count, total


Comprehensive payment method analysis: Find the count, total amount, average amount, refund count, and refund rate (%) per method (displayed in Korean). Only include methods with 1,000+ payments.


**Hint 1:** This is a combination of `CASE` for Korean method labels + `COUNT(refunded_at)` for refund count + `HAVING` + `ORDER BY`.


??? success "Answer"
    ```sql
    SELECT CASE method
               WHEN 'card' THEN '신용카드'
               WHEN 'bank_transfer' THEN '계좌이체'
               WHEN 'virtual_account' THEN '가상계좌'
               WHEN 'kakao_pay' THEN '카카오페이'
               WHEN 'naver_pay' THEN '네이버페이'
               WHEN 'point' THEN '포인트'
           END AS method_kr,
           COUNT(*) AS payment_count,
           ROUND(SUM(amount)) AS total_amount,
           ROUND(AVG(amount)) AS avg_amount,
           COUNT(refunded_at) AS refund_count,
           ROUND(COUNT(refunded_at) * 100.0 / COUNT(*), 1) AS refund_rate_pct
    FROM payments
    GROUP BY method
    HAVING COUNT(*) >= 1000
    ORDER BY total_amount DESC;
    ```


    **Result** (6 rows)

    | method_kr | payment_count | total_amount | avg_amount | refund_count | refund_rate_pct |
    |---|---|---|---|---|---|
    | 신용카드 | 16,841 | 17,004,951,634.00 | 1,009,735.00 | 872 | 5.20 |
    | 카카오페이 | 7486 | 7,563,829,668.00 | 1,010,397.00 | 380 | 5.10 |
    | 네이버페이 | 5715 | 5,998,835,720.00 | 1,049,665.00 | 285 | 5.00 |
    | 계좌이체 | 3718 | 3,753,149,013.00 | 1,009,454.00 | 178 | 4.80 |
    | 포인트 | 1921 | 1,951,369,604.00 | 1,015,809.00 | 98 | 5.10 |
    | 가상계좌 | 1876 | 1,911,359,424.00 | 1,018,848.00 | 117 | 6.20 |


---


### 29. Customer profile completeness analysis: Find the customer co


Customer profile completeness analysis: Find the customer count, percentage (%), average points, and VIP rate (%) per completeness score (0-4). Completeness = number of non-NULL columns among birth_date, gender, last_login_at, and acquisition_channel.


**Hint 1:** `(column IS NOT NULL)` returns 1 or 0 in SQLite. Adding all four gives the completeness score.


??? success "Answer"
    ```sql
    SELECT (birth_date IS NOT NULL)
         + (gender IS NOT NULL)
         + (last_login_at IS NOT NULL)
         + (acquisition_channel IS NOT NULL) AS completeness,
           COUNT(*) AS customer_count,
           ROUND(AVG(point_balance)) AS avg_points,
           ROUND(SUM(CASE WHEN grade = 'VIP' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS vip_rate_pct
    FROM customers
    GROUP BY completeness
    ORDER BY completeness;
    ```


    **Result** (4 rows)

    | completeness | customer_count | avg_points | vip_rate_pct |
    |---|---|---|---|
    | 1 | 5 | 0.0 | 0.0 |
    | 2 | 143 | 20,877.00 | 0.7 |
    | 3 | 1247 | 45,918.00 | 4.30 |
    | 4 | 3835 | 72,285.00 | 8.20 |


---


### 30. Comprehensive dashboard: Find the active product count, aver


Comprehensive dashboard: Find the active product count, average price, average margin rate (%), price tier classification, and low-stock product count (stock_qty <= 10) per brand from the products table. Only include brands with 5+ active products, sorted by active product count descending, limited to the top 10.


**Hint 1:** Use multiple aggregations and CASE simultaneously. This is a combination of `WHERE is_active = 1` + `GROUP BY brand` + `HAVING` + `ORDER BY` + `LIMIT`.


??? success "Answer"
    ```sql
    SELECT brand,
           COUNT(*) AS active_count,
           ROUND(AVG(price)) AS avg_price,
           ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct,
           CASE
               WHEN AVG(price) >= 1000000 THEN '프리미엄'
               WHEN AVG(price) >= 300000 THEN '대중'
               ELSE '보급형'
           END AS brand_tier,
           SUM(CASE WHEN stock_qty <= 10 THEN 1 ELSE 0 END) AS low_stock_count
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 5
    ORDER BY active_count DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | brand | active_count | avg_price | avg_margin_pct | brand_tier | low_stock_count |
    |---|---|---|---|---|---|
    | Samsung | 21 | 641,800.00 | 18.50 | 대중 | 1 |
    | ASUS | 21 | 1,589,552.00 | 28.00 | 프리미엄 | 0 |
    | MSI | 12 | 820,292.00 | 16.80 | 대중 | 0 |
    | TP-Link | 11 | 128,764.00 | 30.30 | 보급형 | 0 |
    | Logitech | 11 | 115,127.00 | 28.00 | 보급형 | 1 |
    | LG | 11 | 1,346,836.00 | 21.20 | 프리미엄 | 0 |
    | ASRock | 9 | 493,244.00 | 25.60 | 대중 | 0 |


---
