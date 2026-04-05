# Beginner Exercise: Order Basics

Uses the `orders` and `payments` tables. 15 problems practicing date filters, status conditions, and basic aggregation.

---

### 1. Total Order Count

Find the total number of orders and total revenue.

**Hint:** Use `COUNT(*)` and `SUM(total_amount)` together.

??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS total_orders,
        ROUND(SUM(total_amount), 2) AS total_revenue
    FROM orders;
    ```

---

### 2. Order Count by Status

Find the count of orders per status.

**Hint:** Use `GROUP BY status` and `COUNT(*)`.

??? success "Answer"
    ```sql
    SELECT status, COUNT(*) AS cnt
    FROM orders
    GROUP BY status
    ORDER BY cnt DESC;
    ```

---

### 3. Orders in 2024

Find the number of orders and total revenue for 2024.

**Hint:** Filter for 2024 data only with `WHERE ordered_at LIKE '2024%'`.

??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS order_count,
        ROUND(SUM(total_amount), 2) AS revenue
    FROM orders
    WHERE ordered_at LIKE '2024%';
    ```

---

### 4. Cancelled Orders

Find the number of cancelled orders and the cancellation rate (%).

**Hint:** Calculate the cancellation rate with `100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders)`. Use a subquery to get the total count.

??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS cancelled_count,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 2) AS cancel_rate
    FROM orders
    WHERE status = 'cancelled';
    ```

---

### 5. Largest Orders

Retrieve the order number, amount, and order date of the top 10 orders by amount.

**Hint:** Sort with `ORDER BY total_amount DESC` then `LIMIT 10`.

??? success "Answer"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    ORDER BY total_amount DESC
    LIMIT 10;
    ```

---

### 6. Monthly Order Count (2024)

Find the number of orders and revenue per month in 2024.

**Hint:** Extract 'YYYY-MM' with `SUBSTR(ordered_at, 1, 7)` and aggregate monthly with `GROUP BY`. Filter for 2024 with `WHERE`.

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

---

### 7. Average Order Amount

Compare the overall average order amount with the average excluding cancelled orders.

**Hint:** Compare `AVG(total_amount)` with `AVG(CASE WHEN status NOT IN ('cancelled') THEN total_amount END)` in a single query.

??? success "Answer"
    ```sql
    SELECT
        ROUND(AVG(total_amount), 2) AS avg_all,
        ROUND(AVG(CASE
            WHEN status NOT IN ('cancelled') THEN total_amount
        END), 2) AS avg_excl_cancelled
    FROM orders;
    ```

---

### 8. Free Shipping Order Rate

Find the percentage of orders with zero shipping fee.

**Hint:** Use `SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END)` for conditional counting. Divide by `COUNT(*)` to calculate the ratio.

??? success "Answer"
    ```sql
    SELECT
        SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END) AS free_shipping,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN shipping_fee = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct
    FROM orders;
    ```

---

### 9. Orders Using Points

Find the number of orders that used points and the average amount of points used.

**Hint:** Filter with `WHERE point_used > 0` for orders that used points. Calculate the average with `AVG(point_used)`.

??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS orders_with_points,
        ROUND(AVG(point_used), 0) AS avg_points_used,
        MAX(point_used) AS max_points_used
    FROM orders
    WHERE point_used > 0;
    ```

---

### 10. Payment Method Summary

Find the count and total payment amount per payment method.

**Hint:** Group with `GROUP BY method` from the `payments` table. Use `COUNT(*)` and `SUM(amount)`.

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

---

### 11. Card Installment Analysis

Find the installment ratio and average installment months among card payments.

**Hint:** Filter card payments with `WHERE method = 'card'`. Use `CASE WHEN` to count installment transactions and conditional `AVG` for average months.

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

---

### 12. Orders by Day of Week

Find the number of orders per day of the week (Mon–Sun).

**Hint:** Extract the day-of-week number with `STRFTIME('%w', ordered_at)` (0=Sun, 1=Mon, ...). Map to day names with `CASE`.

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

---

### 13. Orders with Delivery Notes

Find the percentage of orders that have a delivery note (notes).

**Hint:** Determine note presence with `CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END` and aggregate with `SUM`.

??? success "Answer"
    ```sql
    SELECT
        SUM(CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END) AS with_notes,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN notes IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct
    FROM orders;
    ```

---

### 14. Yearly Revenue Trend

Find the order count, total revenue, and average order amount per year. Exclude cancelled orders.

**Hint:** Exclude cancelled orders with `WHERE status NOT IN ('cancelled')`. Extract the year with `SUBSTR(ordered_at, 1, 4)` then `GROUP BY`.

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

---

### 15. Refunded Payments

Find the count and total amount of refunded payments.

**Hint:** Filter with `WHERE status = 'refunded'` from the `payments` table. Use `COUNT(*)` and `SUM(amount)`.

??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS refund_count,
        ROUND(SUM(amount), 2) AS total_refunded
    FROM payments
    WHERE status = 'refunded';
    ```
