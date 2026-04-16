# Grouping and Filtering

!!! info "Tables"
    `products` — Products (name, price, stock, brand)  
    `customers` — Customers (grade, points, channel)  
    `orders` — Orders (status, amount, date)  
    `reviews` — Reviews (rating, content)  
    `payments` — Payments (method, amount, status)  
    `complaints` — Complaints (type, priority)  

!!! abstract "Concepts"
    `GROUP BY`, `HAVING`, Aggregate functions + `GROUP BY`, Multi-column grouping

## Basic

### Problem 1. Find the number of products per brand.

Query the number of registered products per brand. Sort by product count in descending order.

??? tip "Hint"
    Use `GROUP BY brand` and `COUNT(*)`.

??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    ORDER BY product_count DESC;
    ```

---

### Problem 2. Find the number of customers per tier.

Query the number of customers per grade (tier). 

??? tip "Hint"
    Use `GROUP BY grade` and `COUNT(*)`.

??? success "Answer"
    ```sql
    SELECT grade, COUNT(*) AS customer_count
    FROM customers
    GROUP BY grade
    ORDER BY customer_count DESC;
    ```

---

### Problem 3. Find the total revenue per order status.

Query the number of orders and total revenue (sum of total_amount) per order status.

??? tip "Hint"
    Use `GROUP BY status`, `COUNT(*)`, and `SUM(total_amount)` together.

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

---

### Problem 4. Find the number of reviews per rating.

Query how many reviews exist for each rating (1-5). Sort by rating.

??? tip "Hint"
    Use `GROUP BY rating` and `COUNT(*)`.

??? success "Answer"
    ```sql
    SELECT rating, COUNT(*) AS review_count
    FROM reviews
    GROUP BY rating
    ORDER BY rating;
    ```

---

### Problem 5. Find the total payment amount per payment method.

Query the number of payments and total amount (sum of amount) per payment method. Sort by total amount in descending order.

??? tip "Hint"
    Use `GROUP BY method` and `SUM(amount)`.

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

---

### Problem 6. Find the number of complaints per channel.

Query the number of complaints per submission channel. Sort by count in descending order.

??? tip "Hint"
    Group the `channel` column of the complaints table using `GROUP BY`.

??? success "Answer"
    ```sql
    SELECT channel, COUNT(*) AS complaint_count
    FROM complaints
    GROUP BY channel
    ORDER BY complaint_count DESC;
    ```

---

### Problem 7. Find the average point balance per customer signup channel.

Query the number of customers and average point balance (point_balance) per acquisition channel (acquisition_channel).

??? tip "Hint"
    Use `GROUP BY acquisition_channel` and `AVG(point_balance)`. Cases where acquisition_channel is NULL will appear as a separate group.

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

---

### Problem 8. Find the number of orders and revenue per year.

Extract the year from the order date (ordered_at) and query the number of orders and total revenue per year.

??? tip "Hint"
    Extract the year with `SUBSTR(ordered_at, 1, 4)` and group with `GROUP BY`.

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

---

### Problem 9. Find the average price and average cost per brand.

Query the average selling price (price) and average cost (cost_price) per brand. Sort by average price in descending order.

??? tip "Hint"
    Use `GROUP BY brand` with `AVG(price)` and `AVG(cost_price)` together.

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

---

### Problem 10. Find the number of complaints and average response count per complaint type.

Query the number of complaints and average response count (response_count) per complaint category.

??? tip "Hint"
    Use `GROUP BY category` and `AVG(response_count)`.

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

---

## Applied

### Problem 11. Find brands with 10 or more products.

Calculate the product count per brand, then query only brands with 10 or more registered products.

??? tip "Hint"
    To filter groups after `GROUP BY`, use `HAVING` instead of `WHERE`.

??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY product_count DESC;
    ```

---

### Problem 12. Find order statuses with an average order amount of 300,000 or more.

Calculate the average order amount per order status, then query only statuses with an average of 300,000 or more.

??? tip "Hint"
    Filter with `HAVING AVG(total_amount) >= 300000`.

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

---

### Problem 13. Find the monthly order count for 2024, but only for months with 3,000 or more orders.

Aggregate the monthly order count for 2024, and query only months with 3,000 or more orders.

??? tip "Hint"
    Filter 2024 first with `WHERE`, then aggregate by month with `GROUP BY`, and filter the count with `HAVING`.

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

### Problem 14. Find the count per complaint priority and status combination.

Query the count for each combination of complaint priority and status.

??? tip "Hint"
    You can list multiple columns separated by commas in `GROUP BY`: `GROUP BY priority, status`

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

---

### Problem 15. Find the number of customers per gender and tier combination.

Query the customer count for each combination of gender and grade (tier). Sort by customer count in descending order.

??? tip "Hint"
    Group both columns together with `GROUP BY gender, grade`. Cases where gender is NULL will also appear as a separate group.

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

---

### Problem 16. For completed payments only, find payment methods with an average amount of 200,000 or more.

Filter only payments with status 'completed', then query payment methods with an average amount of 200,000 or more.

??? tip "Hint"
    Filter with `WHERE status = 'completed'` first, then filter the average amount with `GROUP BY` + `HAVING`.

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

---

### Problem 17. For active products only, find brands with a total stock quantity of 100 or more.

For products currently on sale (is_active = 1), query brands with a total stock (sum of stock_qty) of 100 or more.

??? tip "Hint"
    Filter active products with `WHERE is_active = 1`, then apply `GROUP BY brand` + `HAVING SUM(stock_qty) >= 100`.

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

---

### Problem 18. Find the count per year and order status combination.

Extract the year from the order date and query the order count for each year and status combination.

??? tip "Hint"
    Group by both criteria together with `GROUP BY SUBSTR(ordered_at, 1, 4), status`.

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

---

### Problem 19. Find product IDs with 50 or more reviews.

Aggregate the review count per product (product_id), and query only products with 50 or more reviews.

??? tip "Hint"
    Use `GROUP BY product_id` + `HAVING COUNT(*) >= 50`.

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

---

### Problem 20. Find the signup channel distribution per customer tier, but only for combinations with 100 or more customers.

Calculate the customer count per grade and acquisition_channel combination, and query only combinations with 100 or more customers.

??? tip "Hint"
    After `GROUP BY grade, acquisition_channel`, filter with `HAVING COUNT(*) >= 100`.

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

---

## Advanced

### Problem 21. Find the quarterly revenue and average order amount for 2024.

Divide the 2024 orders by quarter and query the order count, total revenue, and average order amount. Quarters are determined by month.

??? tip "Hint"
    Extract the month with `SUBSTR(ordered_at, 6, 2)`, then calculate the quarter with `(month - 1) / 3 + 1`. In SQLite, use `CAST` to convert the string to an integer.

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

---

### Problem 22. Find the escalation rate per complaint category, and show only categories with a rate of 10% or more.

For each complaint category, calculate the total count, escalation count (escalated = 1), and escalation rate (%). Show only categories with a rate of 10% or more.

??? tip "Hint"
    Calculate the escalation count with `SUM(escalated)`, and the rate with `100.0 * SUM(escalated) / COUNT(*)`. Filter the rate with `HAVING`.

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

---

### Problem 23. Find the total payment amount per card issuer for card payments.

For card payments only (method = 'card'), query the payment count and total amount per card issuer (card_issuer). Sort by total amount in descending order.

??? tip "Hint"
    Filter card payments with `WHERE method = 'card'`, then aggregate with `GROUP BY card_issuer`.

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

---

### Problem 24. Find product IDs with an average rating below 3.0, but only for products with 5 or more reviews.

Calculate the average rating per product, then query products with 5 or more reviews and an average rating below 3.0.

??? tip "Hint"
    You can use multiple conditions in `HAVING`: `HAVING COUNT(*) >= 5 AND AVG(rating) < 3.0`

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

### Problem 25. Compare the monthly order counts for 2023 and 2024.

Query the order count per year-month combination, but only for 2023 and 2024 data. Sort by year, then month.

??? tip "Hint"
    Filter 2023 and 2024 with `WHERE`, then group by year and month with `GROUP BY SUBSTR(ordered_at, 1, 4), SUBSTR(ordered_at, 6, 2)`.

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

---

### Problem 26. Find the active/inactive customer count and average points per tier.

Query the customer count and average point balance per grade and is_active flag combination. Sort by grade, then is_active flag.

??? tip "Hint"
    Combine both criteria with `GROUP BY grade, is_active`.

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

---

### Problem 27. Find complaint channel and priority combinations with 50+ complaints and an average response count of 2 or more.

Query the count and average response count per channel and priority combination, showing only combinations with 50+ complaints and an average response count of 2 or more.

??? tip "Hint"
    Combine two conditions with `AND` in `HAVING`: `HAVING COUNT(*) >= 50 AND AVG(response_count) >= 2`

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

---

### Problem 28. Find the average margin rate (%) per brand and show the top 5 brands.

The margin rate is calculated as (price - cost_price) / price * 100. Only include active products (is_active = 1).

??? tip "Hint"
    Calculate the average margin rate per brand with `AVG((price - cost_price) / price * 100)`. Extract the top 5 with `ORDER BY` + `LIMIT`.

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

---

### Problem 29. Find the card payment count and average amount per installment period, showing only periods with 100+ payments.

For card payments (method = 'card'), calculate the payment count and average amount per installment period (installment_months). Show only installment periods with 100 or more payments.

??? tip "Hint"
    Filter with `WHERE method = 'card'`, then apply `GROUP BY installment_months` + `HAVING COUNT(*) >= 100`.

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

---

### Problem 30. Find the yearly customer signup count and verify the year-over-year growth trend.

Extract the year from the customer signup date (created_at) and query the number of new signups per year. Show only years with 100 or more signups.

??? tip "Hint"
    Extract the year with `SUBSTR(created_at, 1, 4)`, then filter with `GROUP BY` + `HAVING COUNT(*) >= 100`.

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
