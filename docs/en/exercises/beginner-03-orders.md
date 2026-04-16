# Order Basics

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `payments` — Payments (method, amount, status)  



!!! abstract "Concepts"

    `SELECT`, `WHERE`, `GROUP BY`, `COUNT`, `SUM`, `AVG`, `MAX`, `ROUND`, `SUBSTR`, `STRFTIME`, `CASE WHEN`, `LIKE`, `subquery`



### 1. Find the total number of orders and total revenue.


Find the total number of orders and total revenue.


**Hint 1:** Use COUNT(*) and SUM(total_amount) together


??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS total_orders,
        ROUND(SUM(total_amount), 2) AS total_revenue
    FROM orders;
    ```


    **Result** (1 rows)

    | total_orders | total_revenue |
    |---|---|
    | 37,557 | 38,183,495,063.00 |


---


### 2. Find the count of orders per status.


Find the count of orders per status.


**Hint 1:** Use GROUP BY status and COUNT(*)


??? success "Answer"
    ```sql
    SELECT status, COUNT(*) AS cnt
    FROM orders
    GROUP BY status
    ORDER BY cnt DESC;
    ```


    **Result** (top 7 of 9 rows)

    | status | cnt |
    |---|---|
    | confirmed | 34,393 |
    | cancelled | 1859 |
    | return_requested | 507 |
    | returned | 493 |
    | delivered | 125 |
    | pending | 82 |
    | shipped | 51 |


---


### 3. Find the number of orders and total revenue for 2024.


Find the number of orders and total revenue for 2024.


**Hint 1:** Filter for 2024 data only with WHERE ordered_at LIKE '2024%'


??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%';
    ```


    **Result** (1 rows)

    | order_count | revenue |
    |---|---|
    | 5785 | 5,622,439,762.00 |


---


### 4. Find the number of cancelled orders and the cancellation rat


Find the number of cancelled orders and the cancellation rate (%).


**Hint 1:** Calculate the cancellation rate with 100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders). Use a subquery to get the total count


??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS cancelled_count,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 2) AS cancel_rate
    FROM orders
    WHERE status = 'cancelled';
    ```


    **Result** (1 rows)

    | cancelled_count | cancel_rate |
    |---|---|
    | 1859 | 4.95 |


---


### 5. Retrieve the order number, amount, and order date of the top


Retrieve the order number, amount, and order date of the top 10 orders by amount.


**Hint 1:** Sort with ORDER BY total_amount DESC then LIMIT 10


??? success "Answer"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    ORDER BY total_amount DESC
    LIMIT 10;
    ```


    **Result** (top 7 of 10 rows)

    | order_number | total_amount | ordered_at |
    |---|---|---|
    | ORD-20201121-08810 | 50,867,500.00 | 2020-11-21 12:04:42 |
    | ORD-20250305-32265 | 46,820,024.00 | 2025-03-05 09:01:08 |
    | ORD-20230523-22331 | 46,094,971.00 | 2023-05-23 08:50:55 |
    | ORD-20200209-05404 | 43,677,500.00 | 2020-02-09 23:36:36 |
    | ORD-20221231-20394 | 43,585,700.00 | 2022-12-31 21:35:59 |
    | ORD-20251218-37240 | 38,626,400.00 | 2025-12-18 17:09:12 |
    | ORD-20220106-15263 | 37,987,600.00 | 2022-01-06 17:24:14 |


---


### 6. Find the number of orders and revenue per month in 2024.


Find the number of orders and revenue per month in 2024.


**Hint 1:** Extract 'YYYY-MM' with SUBSTR(ordered_at, 1, 7) and aggregate monthly with GROUP BY. Filter for 2024 with WHERE


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 7) AS month,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY SUBSTR(ordered_at, 1, 7)
    ORDER BY month;
    ```


    **Result** (top 7 of 12 rows)

    | month | orders | revenue |
    |---|---|---|
    | 2024-01 | 346 | 320,292,182.00 |
    | 2024-02 | 465 | 449,447,834.00 |
    | 2024-03 | 601 | 569,798,709.00 |
    | 2024-04 | 506 | 496,023,258.00 |
    | 2024-05 | 415 | 473,243,857.00 |
    | 2024-06 | 415 | 399,487,004.00 |
    | 2024-07 | 414 | 383,398,728.00 |


---


### 7. Compare the overall average order amount with the average ex


Compare the overall average order amount with the average excluding cancelled orders.


**Hint 1:** Compare AVG(total_amount) with AVG(CASE WHEN status NOT IN ('cancelled') THEN total_amount END) in a single query


??? success "Answer"
    ```sql
    SELECT
        ROUND(AVG(total_amount), 2) AS avg_all,
        ROUND(AVG(CASE
            WHEN status NOT IN ('cancelled') THEN total_amount
        END), 2) AS avg_excl_cancelled
    FROM orders;
    ```


    **Result** (1 rows)

    | avg_all | avg_excl_cancelled |
    |---|---|
    | 1,016,681.18 | 1,015,193.02 |


---


### 8. Find the percentage of orders with zero shipping fee.


Find the percentage of orders with zero shipping fee.


**Hint 1:** Use SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END) for conditional counting. Divide by COUNT(*) to calculate the ratio


??? success "Answer"
    ```sql
    SELECT
        SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END) AS free_shipping,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct
    FROM orders;
    ```


    **Result** (1 rows)

    | free_shipping | total | pct |
    |---|---|---|
    | 34,491 | 37,557 | 91.80 |


---


### 9. Find the number of orders that used points and the average a


Find the number of orders that used points and the average amount of points used.


**Hint 1:** Filter with WHERE point_used > 0 for orders that used points. Calculate the average with AVG(point_used)


??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS orders_with_points,
        ROUND(AVG(point_used), 0) AS avg_points_used,
        MAX(point_used) AS max_points_used
    FROM orders
    WHERE point_used > 0;
    ```


    **Result** (1 rows)

    | orders_with_points | avg_points_used | max_points_used |
    |---|---|---|
    | 3740 | 2,487.00 | 5000 |


---


### 10. Find the count and total payment amount per payment method.


Find the count and total payment amount per payment method.


**Hint 1:** Group with GROUP BY method from the payments table. Use COUNT(*) and SUM(amount)


??? success "Answer"
    ```sql
    SELECT
        method,
        COUNT(*) AS tx_count,
        ROUND(SUM(amount), 2) AS total_amount
    FROM payments
    GROUP BY method
    ORDER BY total_amount DESC;
    ```


    **Result** (6 rows)

    | method | tx_count | total_amount |
    |---|---|---|
    | card | 16,841 | 17,004,951,634.00 |
    | kakao_pay | 7486 | 7,563,829,668.00 |
    | naver_pay | 5715 | 5,998,835,720.00 |
    | bank_transfer | 3718 | 3,753,149,013.00 |
    | point | 1921 | 1,951,369,604.00 |
    | virtual_account | 1876 | 1,911,359,424.00 |


---


### 11. Find the installment ratio and average installment months am


Find the installment ratio and average installment months among card payments.


**Hint 1:** Filter card payments with WHERE method = 'card'. Use CASE WHEN to count installment transactions and conditional AVG for average months


??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS card_payments,
        SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) AS installment_count,
        ROUND(100.0 * SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS installment_pct,
        ROUND(AVG(CASE WHEN installment_months > 0 THEN installment_months END), 1) AS avg_months
    FROM payments
    WHERE method = 'card';
    ```


    **Result** (1 rows)

    | card_payments | installment_count | installment_pct | avg_months |
    |---|---|---|---|
    | 16,841 | 8128 | 48.30 | 7.50 |


---


### 12. Find the number of orders per day of the week (Mon-Sun).


Find the number of orders per day of the week (Mon-Sun).


**Hint 1:** Extract the day-of-week number with STRFTIME('%w', ordered_at) (0=Sun, 1=Mon, ...). Map to day names with CASE


??? success "Answer"
    ```sql
    SELECT
        CASE CAST(STRFTIME('%w', ordered_at) AS INTEGER)
            WHEN 0 THEN '일'
            WHEN 1 THEN '월'
            WHEN 2 THEN '화'
            WHEN 3 THEN '수'
            WHEN 4 THEN '목'
            WHEN 5 THEN '금'
            WHEN 6 THEN '토'
        END AS day_name,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY STRFTIME('%w', ordered_at)
    ORDER BY STRFTIME('%w', ordered_at);
    ```


    **Result** (7 rows)

    | day_name | order_count |
    |---|---|
    | 일 | 5929 |
    | 월 | 5890 |
    | 화 | 5136 |
    | 수 | 4798 |
    | 목 | 4757 |
    | 금 | 5112 |
    | 토 | 5935 |


---


### 13. Find the percentage of orders that have a delivery note (not


Find the percentage of orders that have a delivery note (notes).


**Hint 1:** Determine note presence with CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END and aggregate with SUM


??? success "Answer"
    ```sql
    SELECT
        SUM(CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END) AS with_notes,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct
    FROM orders;
    ```


    **Result** (1 rows)

    | with_notes | total | pct |
    |---|---|---|
    | 13,219 | 37,557 | 35.20 |


---


### 14. Find the order count, total revenue, and average order amoun


Find the order count, total revenue, and average order amount per year. Exclude cancelled orders.


**Hint 1:** Exclude cancelled orders with WHERE status NOT IN ('cancelled'). Extract the year with SUBSTR(ordered_at, 1, 4) then GROUP BY


??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        COUNT(*) AS orders,
        ROUND(SUM(total_amount), 2) AS revenue,
        ROUND(AVG(total_amount), 2) AS avg_order
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```


    **Result** (top 7 of 10 rows)

    | year | orders | revenue | avg_order |
    |---|---|---|---|
    | 2016 | 401 | 301,871,490.00 | 752,796.73 |
    | 2017 | 668 | 630,467,381.00 | 943,813.44 |
    | 2018 | 1255 | 1,203,414,419.00 | 958,895.95 |
    | 2019 | 2473 | 2,523,296,474.00 | 1,020,338.24 |
    | 2020 | 4128 | 4,251,046,262.00 | 1,029,807.72 |
    | 2021 | 5571 | 5,771,175,319.00 | 1,035,931.67 |
    | 2022 | 4947 | 4,999,116,420.00 | 1,010,534.95 |


---


### 15. Find the count and total amount of refunded payments.


Find the count and total amount of refunded payments.


**Hint 1:** Filter with WHERE status = 'refunded' from the payments table. Use COUNT(*) and SUM(amount)


??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS refund_count,
        ROUND(SUM(amount), 2) AS total_refunded
    FROM payments
    WHERE status = 'refunded';
    ```


    **Result** (1 rows)

    | refund_count | total_refunded |
    |---|---|
    | 1930 | 2,357,145,631.00 |


---
