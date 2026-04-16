# Grouping and Filtering

!!! info "Tables"

    `products` — Products (name, price, stock, brand)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `reviews` — Reviews (rating, content)  

    `payments` — Payments (method, amount, status)  

    `complaints` — Complaints (type, priority)  



!!! abstract "Concepts"

    `GROUP BY`, `HAVING`, `Aggregate functions`, `Multi-column grouping`



### 1. Query the number of registered products per brand. Sort by p


Query the number of registered products per brand. Sort by product count in descending order.


**Hint 1:** Use GROUP BY brand and COUNT(*)


??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    ORDER BY product_count DESC;
    ```


    **Result** (top 7 of 55 rows)

    | brand | product_count |
    |---|---|
    | ASUS | 26 |
    | Samsung | 25 |
    | Logitech | 17 |
    | MSI | 13 |
    | TP-Link | 11 |
    | LG | 11 |
    | ASRock | 11 |


---


### 2. Query the number of customers per grade (tier).


Query the number of customers per grade (tier).


**Hint 1:** Use GROUP BY grade and COUNT(*)


??? success "Answer"
    ```sql
    SELECT grade, COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade
    ORDER BY customer_count DESC;
    ```


    **Result** (4 rows)

    | grade | customer_count |
    |---|---|
    | BRONZE | 3859 |
    | GOLD | 524 |
    | SILVER | 479 |
    | VIP | 368 |


---


### 3. Query the number of orders and total revenue (sum of total_a


Query the number of orders and total revenue (sum of total_amount) per order status.


**Hint 1:** Use GROUP BY status, COUNT(*), and SUM(total_amount) together


??? success "Answer"
    ```sql
    SELECT
        status,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 0) AS total_revenue
    FROM orders
    GROUP BY status
    ORDER BY total_revenue DESC;
    ```


    **Result** (top 7 of 9 rows)

    | status | order_count | total_revenue |
    |---|---|---|
    | confirmed | 34,393 | 34,386,590,179.00 |
    | cancelled | 1859 | 1,943,134,782.00 |
    | return_requested | 507 | 811,487,700.00 |
    | returned | 493 | 659,444,574.00 |
    | delivered | 125 | 195,768,235.00 |
    | pending | 82 | 87,230,243.00 |
    | shipped | 51 | 74,070,546.00 |


---


### 4. Query how many reviews exist for each rating (1-5). Sort by 


Query how many reviews exist for each rating (1-5). Sort by rating.


**Hint 1:** Use GROUP BY rating and COUNT(*)


??? success "Answer"
    ```sql
    SELECT rating, COUNT(*) AS review_count
    FROM reviews
    GROUP BY rating
    ORDER BY rating;
    ```


    **Result** (5 rows)

    | rating | review_count |
    |---|---|
    | 1 | 434 |
    | 2 | 839 |
    | 3 | 1265 |
    | 4 | 2575 |
    | 5 | 3433 |


---


### 5. Query the number of payments and total amount (sum of amount


Query the number of payments and total amount (sum of amount) per payment method. Sort by total amount in descending order.


**Hint 1:** Use GROUP BY method and SUM(amount)


??? success "Answer"
    ```sql
    SELECT
        method,
        COUNT(*) AS payment_count,
        ROUND(SUM(amount), 0) AS total_amount
    FROM payments
    GROUP BY method
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


### 6. Query the number of complaints per submission channel. Sort 


Query the number of complaints per submission channel. Sort by count in descending order.


**Hint 1:** Group the channel column of the complaints table using GROUP BY


??? success "Answer"
    ```sql
    SELECT channel, COUNT(*) AS complaint_count
    FROM complaints
    GROUP BY channel
    ORDER BY complaint_count DESC;
    ```


    **Result** (5 rows)

    | channel | complaint_count |
    |---|---|
    | website | 1341 |
    | phone | 913 |
    | email | 796 |
    | chat | 583 |
    | kakao | 180 |


---


### 7. Query the number of customers and average point balance (poi


Query the number of customers and average point balance (point_balance) per acquisition channel (acquisition_channel).


**Hint 1:** Use GROUP BY acquisition_channel and AVG(point_balance). Cases where acquisition_channel is NULL will appear as a separate group


??? success "Answer"
    ```sql
    SELECT
        acquisition_channel,
        COUNT(*) AS customer_count,
        ROUND(AVG(point_balance), 0) AS avg_points
    FROM customers
    GROUP BY acquisition_channel
    ORDER BY avg_points DESC;
    ```


    **Result** (5 rows)

    | acquisition_channel | customer_count | avg_points |
    |---|---|---|
    | organic | 1146 | 76,371.00 |
    | direct | 408 | 70,562.00 |
    | referral | 708 | 66,944.00 |
    | search_ad | 1543 | 62,449.00 |
    | social | 1425 | 54,311.00 |


---


### 8. Extract the year from the order date (ordered_at) and query 


Extract the year from the order date (ordered_at) and query the number of orders and total revenue per year.


**Hint 1:** Extract the year with SUBSTR(ordered_at, 1, 4) and group with GROUP BY


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 0) AS total_revenue
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```


    **Result** (top 7 of 10 rows)

    | year | order_count | total_revenue |
    |---|---|---|
    | 2016 | 416 | 331,746,909.00 |
    | 2017 | 709 | 653,085,068.00 |
    | 2018 | 1319 | 1,249,197,907.00 |
    | 2019 | 2589 | 2,620,111,601.00 |
    | 2020 | 4319 | 4,468,755,264.00 |
    | 2021 | 5841 | 6,044,718,738.00 |
    | 2022 | 5203 | 5,302,071,035.00 |


---


### 9. Query the average selling price (price) and average cost (co


Query the average selling price (price) and average cost (cost_price) per brand. Sort by average price in descending order.


**Hint 1:** Use GROUP BY brand with AVG(price) and AVG(cost_price) together


??? success "Answer"
    ```sql
    SELECT
        brand,
        ROUND(AVG(price), 0) AS avg_price,
        ROUND(AVG(cost_price), 0) AS avg_cost
    FROM products
    GROUP BY brand
    ORDER BY avg_price DESC;
    ```


    **Result** (top 7 of 55 rows)

    | brand | avg_price | avg_cost |
    |---|---|---|
    | Apple | 2,815,400.00 | 1,645,500.00 |
    | Razer | 1,764,889.00 | 1,518,700.00 |
    | ASUS | 1,683,631.00 | 1,225,488.00 |
    | Lenovo | 1,597,760.00 | 1,370,820.00 |
    | HP | 1,479,017.00 | 1,110,600.00 |
    | BenQ | 1,476,300.00 | 1,312,500.00 |
    | Jooyon Tech | 1,413,550.00 | 1,073,525.00 |


---


### 10. Query the number of complaints and average response count (r


Query the number of complaints and average response count (response_count) per complaint category.


**Hint 1:** Use GROUP BY category and AVG(response_count)


??? success "Answer"
    ```sql
    SELECT
        category,
        COUNT(*) AS complaint_count,
        ROUND(AVG(response_count), 1) AS avg_responses
    FROM complaints
    GROUP BY category
    ORDER BY complaint_count DESC;
    ```


    **Result** (7 rows)

    | category | complaint_count | avg_responses |
    |---|---|---|
    | general_inquiry | 1232 | 1.70 |
    | delivery_issue | 708 | 1.70 |
    | refund_request | 522 | 2.90 |
    | product_defect | 460 | 2.90 |
    | price_inquiry | 439 | 1.60 |
    | wrong_item | 240 | 2.80 |
    | exchange_request | 212 | 2.90 |


---


### 11. Calculate the product count per brand, then query only brand


Calculate the product count per brand, then query only brands with 10 or more registered products.


**Hint 1:** To filter groups after GROUP BY, use HAVING instead of WHERE


??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY product_count DESC;
    ```


    **Result** (7 rows)

    | brand | product_count |
    |---|---|
    | ASUS | 26 |
    | Samsung | 25 |
    | Logitech | 17 |
    | MSI | 13 |
    | TP-Link | 11 |
    | LG | 11 |
    | ASRock | 11 |


---


### 12. Calculate the average order amount per order status, then qu


Calculate the average order amount per order status, then query only statuses with an average of 300,000 or more.


**Hint 1:** Filter with HAVING AVG(total_amount) >= 300000


??? success "Answer"
    ```sql
    SELECT
        status,
        COUNT(*) AS order_count,
        ROUND(AVG(total_amount), 0) AS avg_amount
    FROM orders
    GROUP BY status
    HAVING AVG(total_amount) >= 300000
    ORDER BY avg_amount DESC;
    ```


    **Result** (top 7 of 9 rows)

    | status | order_count | avg_amount |
    |---|---|---|
    | return_requested | 507 | 1,600,567.00 |
    | delivered | 125 | 1,566,146.00 |
    | shipped | 51 | 1,452,364.00 |
    | returned | 493 | 1,337,616.00 |
    | pending | 82 | 1,063,783.00 |
    | cancelled | 1859 | 1,045,258.00 |
    | confirmed | 34,393 | 999,814.00 |


---


### 13. Aggregate the monthly order count for 2024, and query only m


Aggregate the monthly order count for 2024, and query only months with 3,000 or more orders.


**Hint 1:** Filter 2024 first with WHERE, then aggregate by month with GROUP BY, and filter the count with HAVING


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS order_count
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    HAVING COUNT(*) >= 3000
    ORDER BY month;
    ```


---


### 14. Query the count for each combination of complaint priority a


Query the count for each combination of complaint priority and status.


**Hint 1:** You can list multiple columns separated by commas in GROUP BY: GROUP BY priority, status


??? success "Answer"
    ```sql
    SELECT
        priority,
        status,
        COUNT(*) AS cnt
    FROM complaints
    GROUP BY priority, status
    ORDER BY priority, status;
    ```


    **Result** (top 7 of 12 rows)

    | priority | status | cnt |
    |---|---|---|
    | high | closed | 773 |
    | high | open | 51 |
    | high | resolved | 134 |
    | low | closed | 1021 |
    | low | open | 66 |
    | low | resolved | 183 |
    | medium | closed | 1002 |


---


### 15. Query the customer count for each combination of gender and 


Query the customer count for each combination of gender and grade (tier). Sort by customer count in descending order.


**Hint 1:** Group both columns together with GROUP BY gender, grade. Cases where gender is NULL will also appear as a separate group


??? success "Answer"
    ```sql
    SELECT
        gender,
        grade,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY gender, grade
    ORDER BY customer_count DESC;
    ```


    **Result** (top 7 of 12 rows)

    | gender | grade | customer_count |
    |---|---|---|
    | M | BRONZE | 2128 |
    | F | BRONZE | 1302 |
    | NULL | BRONZE | 429 |
    | M | GOLD | 343 |
    | M | SILVER | 293 |
    | M | VIP | 268 |
    | F | SILVER | 141 |


---


### 16. Filter only payments with status 'completed', then query pay


Filter only payments with status 'completed', then query payment methods with an average amount of 200,000 or more.


**Hint 1:** Filter with WHERE status = 'completed' first, then filter the average amount with GROUP BY + HAVING


??? success "Answer"
    ```sql
    SELECT
        method,
        COUNT(*) AS payment_count,
        ROUND(AVG(amount), 0) AS avg_amount
    FROM payments
    WHERE status = 'completed'
    GROUP BY method
    HAVING AVG(amount) >= 200000
    ORDER BY avg_amount DESC;
    ```


    **Result** (6 rows)

    | method | payment_count | avg_amount |
    |---|---|---|
    | naver_pay | 5270 | 1,028,554.00 |
    | bank_transfer | 3429 | 1,008,007.00 |
    | point | 1770 | 1,005,839.00 |
    | virtual_account | 1705 | 1,001,042.00 |
    | card | 15,556 | 998,781.00 |
    | kakao_pay | 6886 | 984,768.00 |


---


### 17. For products currently on sale (is_active = 1), query brands


For products currently on sale (is_active = 1), query brands with a total stock (sum of stock_qty) of 100 or more.


**Hint 1:** Filter active products with WHERE is_active = 1, then apply GROUP BY brand + HAVING SUM(stock_qty) >= 100


??? success "Answer"
    ```sql
    SELECT
        brand,
        COUNT(*) AS product_count,
        SUM(stock_qty) AS total_stock
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING SUM(stock_qty) >= 100
    ORDER BY total_stock DESC;
    ```


    **Result** (top 7 of 48 rows)

    | brand | product_count | total_stock |
    |---|---|---|
    | Samsung | 21 | 6174 |
    | ASUS | 21 | 5828 |
    | MSI | 12 | 4070 |
    | ASRock | 9 | 3084 |
    | TP-Link | 11 | 3081 |
    | LG | 11 | 2667 |
    | Logitech | 11 | 2461 |


---


### 18. Extract the year from the order date and query the order cou


Extract the year from the order date and query the order count for each year and status combination.


**Hint 1:** Group by both criteria together with GROUP BY SUBSTR(ordered_at, 1, 4), status


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        status,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4), status
    ORDER BY year, order_count DESC;
    ```


    **Result** (top 7 of 45 rows)

    | year | status | order_count |
    |---|---|---|
    | 2016 | confirmed | 379 |
    | 2016 | cancelled | 15 |
    | 2016 | returned | 13 |
    | 2016 | return_requested | 9 |
    | 2017 | confirmed | 652 |
    | 2017 | cancelled | 41 |
    | 2017 | returned | 11 |


---


### 19. Aggregate the review count per product (product_id), and que


Aggregate the review count per product (product_id), and query only products with 50 or more reviews.


**Hint 1:** Use GROUP BY product_id + HAVING COUNT(*) >= 50


??? success "Answer"
    ```sql
    SELECT
        product_id,
        COUNT(*) AS review_count
    FROM reviews
    GROUP BY product_id
    HAVING COUNT(*) >= 50
    ORDER BY review_count DESC;
    ```


    **Result** (top 7 of 52 rows)

    | product_id | review_count |
    |---|---|
    | 100 | 105 |
    | 176 | 102 |
    | 111 | 101 |
    | 45 | 100 |
    | 139 | 89 |
    | 102 | 87 |
    | 124 | 82 |


---


### 20. Calculate the customer count per grade and acquisition_chann


Calculate the customer count per grade and acquisition_channel combination, and query only combinations with 100 or more customers.


**Hint 1:** After GROUP BY grade, acquisition_channel, filter with HAVING COUNT(*) >= 100


??? success "Answer"
    ```sql
    SELECT
        grade,
        acquisition_channel,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade, acquisition_channel
    HAVING COUNT(*) >= 100
    ORDER BY grade, customer_count DESC;
    ```


    **Result** (top 7 of 11 rows)

    | grade | acquisition_channel | customer_count |
    |---|---|---|
    | BRONZE | search_ad | 1118 |
    | BRONZE | social | 1074 |
    | BRONZE | organic | 838 |
    | BRONZE | referral | 528 |
    | BRONZE | direct | 301 |
    | GOLD | search_ad | 151 |
    | GOLD | organic | 137 |


---


### 21. Divide the 2024 orders by quarter and query the order count,


Divide the 2024 orders by quarter and query the order count, total revenue, and average order amount. Quarters are determined by month.


**Hint 1:** Extract the month with SUBSTR(ordered_at, 6, 2), then calculate the quarter with (month - 1) / 3 + 1


??? success "Answer"
    ```sql
    SELECT
        (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) - 1) / 3 + 1 AS quarter,
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 0) AS total_revenue,
        ROUND(AVG(total_amount), 0) AS avg_amount
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY (CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) - 1) / 3 + 1
    ORDER BY quarter;
    ```


    **Result** (4 rows)

    | quarter | order_count | total_revenue | avg_amount |
    |---|---|---|---|
    | 1 | 1412 | 1,339,538,725.00 | 948,682.00 |
    | 2 | 1336 | 1,368,754,119.00 | 1,024,517.00 |
    | 3 | 1423 | 1,394,047,576.00 | 979,654.00 |
    | 4 | 1614 | 1,520,099,342.00 | 941,821.00 |


---


### 22. For each complaint category, calculate the total count, esca


For each complaint category, calculate the total count, escalation count (escalated = 1), and escalation rate (%). Show only categories with a rate of 10% or more.


**Hint 1:** Calculate the escalation count with SUM(escalated), and the rate with 100.0 * SUM(escalated) / COUNT(*)


??? success "Answer"
    ```sql
    SELECT
        category,
        COUNT(*) AS total_count,
        SUM(escalated) AS escalated_count,
        ROUND(100.0 * SUM(escalated) / COUNT(*), 1) AS escalation_rate
    FROM complaints
    GROUP BY category
    HAVING 100.0 * SUM(escalated) / COUNT(*) >= 10
    ORDER BY escalation_rate DESC;
    ```


    **Result** (3 rows)

    | category | total_count | escalated_count | escalation_rate |
    |---|---|---|---|
    | exchange_request | 212 | 31 | 14.60 |
    | product_defect | 460 | 56 | 12.20 |
    | refund_request | 522 | 58 | 11.10 |


---


### 23. For card payments only (method = 'card'), query the payment 


For card payments only (method = 'card'), query the payment count and total amount per card issuer (card_issuer). Sort by total amount in descending order.


**Hint 1:** Filter card payments with WHERE method = 'card', then aggregate with GROUP BY card_issuer


??? success "Answer"
    ```sql
    SELECT
        card_issuer,
        COUNT(*) AS payment_count,
        ROUND(SUM(amount), 0) AS total_amount
    FROM payments
    WHERE method = 'card'
    GROUP BY card_issuer
    ORDER BY total_amount DESC;
    ```


    **Result** (7 rows)

    | card_issuer | payment_count | total_amount |
    |---|---|---|
    | Visa | 5098 | 5,066,448,079.00 |
    | Mastercard | 4039 | 4,295,391,977.00 |
    | American Express | 2513 | 2,614,807,100.00 |
    | Discover | 1710 | 1,694,228,100.00 |
    | Capital One | 1377 | 1,323,799,708.00 |
    | Chase | 1252 | 1,241,983,028.00 |
    | Citi | 852 | 768,293,642.00 |


---


### 24. Calculate the average rating per product, then query product


Calculate the average rating per product, then query products with 5 or more reviews and an average rating below 3.0.


**Hint 1:** You can use multiple conditions in HAVING: HAVING COUNT(*) >= 5 AND AVG(rating) < 3.0


??? success "Answer"
    ```sql
    SELECT
        product_id,
        COUNT(*) AS review_count,
        ROUND(AVG(rating), 2) AS avg_rating
    FROM reviews
    GROUP BY product_id
    HAVING COUNT(*) >= 5 AND AVG(rating) < 3.0
    ORDER BY avg_rating;
    ```


---


### 25. Query the order count per year-month combination, but only f


Query the order count per year-month combination, but only for 2023 and 2024 data. Sort by year, then month.


**Hint 1:** Filter 2023 and 2024 with WHERE, then group by year and month with GROUP BY SUBSTR(ordered_at, 1, 4), SUBSTR(ordered_at, 6, 2)


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        SUBSTR(ordered_at, 6, 2) AS month,
        COUNT(*) AS order_count
    FROM orders
    WHERE SUBSTR(ordered_at, 1, 4) IN ('2023', '2024')
    GROUP BY SUBSTR(ordered_at, 1, 4), SUBSTR(ordered_at, 6, 2)
    ORDER BY year, month;
    ```


    **Result** (top 7 of 24 rows)

    | year | month | order_count |
    |---|---|---|
    | 2023 | 01 | 305 |
    | 2023 | 02 | 383 |
    | 2023 | 03 | 504 |
    | 2023 | 04 | 423 |
    | 2023 | 05 | 430 |
    | 2023 | 06 | 332 |
    | 2023 | 07 | 329 |


---


### 26. Query the customer count and average point balance per grade


Query the customer count and average point balance per grade and is_active flag combination. Sort by grade, then is_active flag.


**Hint 1:** Combine both criteria with GROUP BY grade, is_active


??? success "Answer"
    ```sql
    SELECT
        grade,
        is_active,
        COUNT(*) AS customer_count,
        ROUND(AVG(point_balance), 0) AS avg_points
    FROM customers
    GROUP BY grade, is_active
    ORDER BY grade, is_active DESC;
    ```


    **Result** (5 rows)

    | grade | is_active | customer_count | avg_points |
    |---|---|---|---|
    | BRONZE | 1 | 2289 | 28,288.00 |
    | BRONZE | 0 | 1570 | 0.0 |
    | GOLD | 1 | 524 | 147,711.00 |
    | SILVER | 1 | 479 | 95,042.00 |
    | VIP | 1 | 368 | 407,015.00 |


---


### 27. Query the count and average response count per channel and p


Query the count and average response count per channel and priority combination, showing only combinations with 50+ complaints and an average response count of 2 or more.


**Hint 1:** Combine two conditions with AND in HAVING: HAVING COUNT(*) >= 50 AND AVG(response_count) >= 2


??? success "Answer"
    ```sql
    SELECT
        channel,
        priority,
        COUNT(*) AS complaint_count,
        ROUND(AVG(response_count), 1) AS avg_responses
    FROM complaints
    GROUP BY channel, priority
    HAVING COUNT(*) >= 50 AND AVG(response_count) >= 2
    ORDER BY avg_responses DESC;
    ```


    **Result** (top 7 of 15 rows)

    | channel | priority | complaint_count | avg_responses |
    |---|---|---|---|
    | chat | urgent | 59 | 2.60 |
    | email | urgent | 74 | 2.60 |
    | chat | high | 136 | 2.50 |
    | email | high | 212 | 2.40 |
    | phone | urgent | 87 | 2.40 |
    | website | high | 341 | 2.40 |
    | website | urgent | 129 | 2.40 |


---


### 28. Find the average margin rate (%) per brand and show the top 


Find the average margin rate (%) per brand and show the top 5 brands. The margin rate is calculated as (price - cost_price) / price * 100. Only include active products (is_active = 1).


**Hint 1:** Calculate the average margin rate per brand with AVG((price - cost_price) / price * 100). Extract the top 5 with ORDER BY + LIMIT


??? success "Answer"
    ```sql
    SELECT
        brand,
        COUNT(*) AS product_count,
        ROUND(AVG((price - cost_price) / price * 100), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    ORDER BY avg_margin_pct DESC
    LIMIT 5;
    ```


    **Result** (5 rows)

    | brand | product_count | avg_margin_pct |
    |---|---|---|
    | Norton | 1 | 56.70 |
    | AhnLab | 1 | 48.00 |
    | WD | 1 | 46.00 |
    | Hancom | 3 | 43.40 |
    | Apple | 2 | 42.20 |


---


### 29. For card payments (method = 'card'), calculate the payment c


For card payments (method = 'card'), calculate the payment count and average amount per installment period (installment_months). Show only installment periods with 100 or more payments.


**Hint 1:** Filter with WHERE method = 'card', then apply GROUP BY installment_months + HAVING COUNT(*) >= 100


??? success "Answer"
    ```sql
    SELECT
        installment_months,
        COUNT(*) AS payment_count,
        ROUND(AVG(amount), 0) AS avg_amount
    FROM payments
    WHERE method = 'card'
    GROUP BY installment_months
    HAVING COUNT(*) >= 100
    ORDER BY installment_months;
    ```


    **Result** (7 rows)

    | installment_months | payment_count | avg_amount |
    |---|---|---|
    | 0 | 8713 | 430,180.00 |
    | 2 | 965 | 395,901.00 |
    | 3 | 2084 | 1,276,668.00 |
    | 6 | 2092 | 1,810,057.00 |
    | 10 | 1419 | 2,061,261.00 |
    | 12 | 968 | 2,200,027.00 |
    | 24 | 600 | 2,288,301.00 |


---


### 30. Extract the year from the customer signup date (created_at) 


Extract the year from the customer signup date (created_at) and query the number of new signups per year. Show only years with 100 or more signups.


**Hint 1:** Extract the year with SUBSTR(created_at, 1, 4), then filter with GROUP BY + HAVING COUNT(*) >= 100


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 4) AS year,
        COUNT(*) AS new_customers
    FROM customers
    GROUP BY SUBSTR(created_at, 1, 4)
    HAVING COUNT(*) >= 100
    ORDER BY year;
    ```


    **Result** (top 7 of 10 rows)

    | year | new_customers |
    |---|---|
    | 2016 | 100 |
    | 2017 | 180 |
    | 2018 | 300 |
    | 2019 | 450 |
    | 2020 | 700 |
    | 2021 | 800 |
    | 2022 | 650 |


---
