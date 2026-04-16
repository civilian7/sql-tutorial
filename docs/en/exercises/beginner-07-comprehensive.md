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
    All Beginner topics: `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, Aggregate functions, `GROUP BY`, `HAVING`, `IS NULL`, `COALESCE`, `CASE`

## Basic (1~10)

Practice combining 2-3 concepts.

---

### Problem 1

**Query the name, brand, and price of the top 5 most expensive active products (`is_active = 1`).**

??? tip "Hint"
    This is a combination of `WHERE` filtering + `ORDER BY DESC` + `LIMIT`.

??? success "Answer"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE is_active = 1
    ORDER BY price DESC
    LIMIT 5;
    ```

---

### Problem 2

**Query the name and last login date of VIP-tier customers who have a login history, sorted by most recent, limited to 10 rows.**

??? tip "Hint"
    Combine two conditions with `WHERE grade = 'VIP' AND last_login_at IS NOT NULL`.

??? success "Answer"
    ```sql
    SELECT name, last_login_at
    FROM customers
    WHERE grade = 'VIP'
      AND last_login_at IS NOT NULL
    ORDER BY last_login_at DESC
    LIMIT 10;
    ```

---

### Problem 3

**Query the order number, order amount, and cancellation date of cancelled orders in 2024, sorted by most recent cancellation, limited to 10 rows.**

??? tip "Hint"
    Combine conditions with `WHERE ordered_at LIKE '2024%' AND cancelled_at IS NOT NULL`.

??? success "Answer"
    ```sql
    SELECT order_number, total_amount, cancelled_at
    FROM orders
    WHERE ordered_at LIKE '2024%'
      AND cancelled_at IS NOT NULL
    ORDER BY cancelled_at DESC
    LIMIT 10;
    ```

---

### Problem 4

**Find the count and average rating of reviews with a rating of 4 or higher. Display the average to 2 decimal places.**

??? tip "Hint"
    Filter with `WHERE rating >= 4`, then use `COUNT(*)` and `ROUND(AVG(rating), 2)`.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS high_rating_count,
           ROUND(AVG(rating), 2) AS avg_rating
    FROM reviews
    WHERE rating >= 4;
    ```

---

### Problem 5

**Find the number of active products per brand, showing only brands with 10 or more, sorted by product count descending.**

??? tip "Hint"
    This is a combination of `WHERE is_active = 1` + `GROUP BY brand` + `HAVING COUNT(*) >= 10`.

??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY product_count DESC;
    ```

---

### Problem 6

**Find the average points per customer tier, displaying the tier in Korean. Sort by average points descending.**

??? tip "Hint"
    This is a combination of `CASE` for tier conversion + `GROUP BY` + `AVG` + `ORDER BY`.

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

---

### Problem 7

**Find the total payment amount and count per payment method, showing only methods with a total of 1 billion or more.**

??? tip "Hint"
    This is a combination of `GROUP BY method` + `HAVING SUM(amount) >= 1000000000`.

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

---

### Problem 8

**Find the count per tier for customers with a NULL signup channel. Use CASE to sort tiers in order starting from VIP.**

??? tip "Hint"
    This is a combination of `WHERE acquisition_channel IS NULL` + `GROUP BY grade` + `ORDER BY CASE`.

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

### Problem 9

**Find the count, average order amount, and delivery notes completion rate (%) per order status. Sort by count descending.**

??? tip "Hint"
    Calculate the completion rate with `COUNT(notes) * 100.0 / COUNT(*)`. This leverages the relationship between NULL and aggregate functions.

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

---

### Problem 10

**Classify products by stock status (Out of stock/Low/Normal/Sufficient) and find the product count and average price per group. Active products only.**

??? tip "Hint"
    This is a combination of `WHERE is_active = 1` + `CASE` for stock classification + `GROUP BY` + aggregate functions.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN stock_qty = 0 THEN 'Out of stock'
               WHEN stock_qty <= 10 THEN 'Low'
               WHEN stock_qty <= 100 THEN 'Normal'
               ELSE 'Sufficient'
           END AS stock_status,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price
    FROM products
    WHERE is_active = 1
    GROUP BY stock_status
    ORDER BY product_count DESC;
    ```

---

## Applied (11~20)

Business scenarios combining 3-4 concepts.

---

### Problem 11

**Find the active product count, average price, and average margin rate (%) per brand. Show only brands with 5+ products, sorted by average margin rate descending.**

??? tip "Hint"
    Margin rate = `(price - cost_price) * 100.0 / price`. This is a combination of `WHERE` + `GROUP BY` + `HAVING` + `ORDER BY`.

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

---

### Problem 12

**Find the order count, total revenue, average order amount, and cancellation count per year. The cancellation count is the number of rows where cancelled_at is not NULL.**

??? tip "Hint"
    Extract the year with `SUBSTR(ordered_at, 1, 4)`. `COUNT(cancelled_at)` counts only non-NULL rows.

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

---

### Problem 13

**Find the customer count, VIP rate (%), and average points per signup channel. Display 'Unclassified' for NULL channels, sorted by customer count descending.**

??? tip "Hint"
    This is a combination of `COALESCE` for NULL replacement + `SUM(CASE WHEN grade = 'VIP' THEN 1 ELSE 0 END)` for VIP count aggregation + `GROUP BY`.

??? success "Answer"
    ```sql
    SELECT COALESCE(acquisition_channel, 'Unclassified') AS channel,
           COUNT(*) AS customer_count,
           ROUND(SUM(CASE WHEN grade = 'VIP' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS vip_rate_pct,
           ROUND(AVG(point_balance)) AS avg_points
    FROM customers
    GROUP BY COALESCE(acquisition_channel, 'Unclassified')
    ORDER BY customer_count DESC;
    ```

---

### Problem 14

**Find the monthly order count and average order amount for 2024, also displaying the season (Spring/Summer/Fall/Winter).**

??? tip "Hint"
    This is a combination of `SUBSTR` for month extraction + `CASE` for season classification + `GROUP BY` + aggregation.

??? success "Answer"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 7) AS month,
           CASE
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (3, 4, 5) THEN 'Spring'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (6, 7, 8) THEN 'Summer'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (9, 10, 11) THEN 'Fall'
               ELSE 'Winter'
           END AS season,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```

---

### Problem 15

**Aggregate reviews by rating, displaying the Korean label, count, overall percentage (%), and title completion rate (%) for each rating. Sort by rating descending.**

??? tip "Hint"
    This is a combination of `CASE` for rating labels + `COUNT(*)` + percentage calculation + `COUNT(title)`.

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

    > If you haven't learned window functions (`OVER()`) yet, you can omit the percentage column.

---

### Problem 16

**Find the product count, average stock, and discontinuation rate (%) per price tier (Budget/Mid-low/Mid/Premium). The discontinuation rate is the percentage of is_active=0.**

??? tip "Hint"
    This is a combination of `CASE` for price tier classification + `SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END)` for discontinuation count + `GROUP BY`.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN price < 100000 THEN 'Budget'
               WHEN price < 500000 THEN 'Mid-low'
               WHEN price < 1000000 THEN 'Mid'
               ELSE 'Premium'
           END AS price_tier,
           COUNT(*) AS product_count,
           ROUND(AVG(stock_qty)) AS avg_stock,
           ROUND(SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS discontinued_pct
    FROM products
    GROUP BY price_tier
    ORDER BY product_count DESC;
    ```

---

### Problem 17

**Query the customer count, average points, gender completion rate (%), and login experience rate (%) per tier in a single query. Tier order: VIP > GOLD > SILVER > BRONZE.**

??? tip "Hint"
    Use `COUNT(gender)` for gender completion count and `COUNT(last_login_at)` for login experience count. Use `ORDER BY CASE` for tier ordering.

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

---

### Problem 18

**Classify orders into 3 status groups (Processing/Completed/Cancelled-Returned) and find the count, total revenue, average shipping fee, and points-used count per group.**

??? tip "Hint"
    Classify groups with `CASE WHEN status IN (...)`. Count points-used orders with `SUM(CASE WHEN point_used > 0 THEN 1 ELSE 0 END)`.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN status IN ('pending', 'paid', 'preparing') THEN 'Processing'
               WHEN status IN ('shipped', 'delivered', 'confirmed') THEN 'Completed'
               ELSE 'Cancelled/Returned'
           END AS status_group,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue,
           ROUND(AVG(shipping_fee)) AS avg_shipping,
           SUM(CASE WHEN point_used > 0 THEN 1 ELSE 0 END) AS point_used_count
    FROM orders
    GROUP BY status_group
    ORDER BY order_count DESC;
    ```

---

### Problem 19

**For card payments, find the payment count, average amount, and installment usage rate (%) per card issuer. Exclude records where card issuer is NULL, and show only card issuers with 100+ payments.**

??? tip "Hint"
    Filter with `WHERE method = 'card' AND card_issuer IS NOT NULL`. Count installment payments with `SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END)`.

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

---

### Problem 20

**Find the product count and active product rate (%) per supplier. Only include suppliers with 3+ products, sorted by active rate descending. Group by supplier_id.**

??? tip "Hint"
    This is a combination of `GROUP BY supplier_id` + `HAVING COUNT(*) >= 3` + `SUM(CASE WHEN is_active = 1 ...)` for active rate calculation + `ORDER BY`.

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

---

## Practical (21~30)

Real-world analysis tasks combining 4+ concepts.

---

### Problem 21

**Find the active product count and average price per brand, showing only brands with an average price of 1M+. Also display the price tier classification (Premium/Mainstream/Budget).**

??? tip "Hint"
    This is a combination of `WHERE is_active = 1` + `GROUP BY brand` + `HAVING AVG(price) >= 1000000` + `CASE` for price tier classification.

??? success "Answer"
    ```sql
    SELECT brand,
           COUNT(*) AS active_product_count,
           ROUND(AVG(price)) AS avg_price,
           CASE
               WHEN AVG(price) >= 2000000 THEN 'Premium'
               WHEN AVG(price) >= 1000000 THEN 'Mainstream'
               ELSE 'Budget'
           END AS brand_tier
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING AVG(price) >= 1000000
    ORDER BY avg_price DESC;
    ```

---

### Problem 22

**2024 monthly revenue analysis: Find the monthly order count, total revenue, average order amount, cancellation rate (%), and free shipping rate (%).**

??? tip "Hint"
    Combine various aggregations. Cancellation rate = `COUNT(cancelled_at) / COUNT(*)`. Free shipping = percentage of orders with `shipping_fee = 0`.

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

---

### Problem 23

**Customer segment analysis: Combine tier and activity status (Active/Dormant/Withdrawn) to find the customer count and average points per segment. Show only segments with 100+ customers.**

??? tip "Hint"
    Classify activity status with `CASE` (is_active=0 is Withdrawn, last_login_at IS NULL is Dormant, the rest is Active). Combine with `GROUP BY grade, activity_status`.

??? success "Answer"
    ```sql
    SELECT grade,
           CASE
               WHEN is_active = 0 THEN 'Withdrawn'
               WHEN last_login_at IS NULL THEN 'Dormant'
               ELSE 'Active'
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

---

### Problem 24

**Product data quality report: Find the product count, description missing rate (%), specs missing rate (%), and weight missing rate (%) per brand. Only include brands with 10+ products, sorted by the overall missing rate (average of all three) descending.**

??? tip "Hint"
    Calculate each column's missing rate with `(COUNT(*) - COUNT(column)) * 100.0 / COUNT(*)`. Sort by the average of the three missing rates.

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

---

### Problem 25

**Yearly customer signup analysis: Find the customer count, gender ratio (Male/Female/Unknown), and average points per signup year.**

??? tip "Hint"
    Calculate the male ratio with `SUM(CASE WHEN gender = 'M' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)`. Also calculate the NULL gender ratio separately.

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

---

### Problem 26

**Discount analysis: For 2024 orders, combine discount status (Has discount/No discount) and amount tier (Small/Regular/Large/VIP-level) to find the count and average order amount.**

??? tip "Hint"
    Classify discount status with `CASE WHEN discount_amount > 0` and amount tier with `CASE WHEN total_amount < 50000`. Use both CASE expressions in `GROUP BY`.

??? success "Answer"
    ```sql
    SELECT CASE WHEN discount_amount > 0 THEN 'Has discount' ELSE 'No discount' END AS has_discount,
           CASE
               WHEN total_amount < 50000 THEN 'Small'
               WHEN total_amount < 200000 THEN 'Regular'
               WHEN total_amount < 1000000 THEN 'Large'
               ELSE 'VIP-level'
           END AS amount_tier,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY has_discount, amount_tier
    ORDER BY has_discount, avg_amount DESC;
    ```

---

### Problem 27

**Product status by category: Find the total product count, active count, discontinued count, out-of-stock count, and average price per category_id. Only include categories with 5+ total products.**

??? tip "Hint"
    Use `SUM(CASE WHEN condition THEN 1 ELSE 0 END)` to aggregate each status count into separate columns.

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

---

### Problem 28

**Comprehensive payment method analysis: Find the count, total amount, average amount, refund count, and refund rate (%) per method (displayed in Korean). Only include methods with 1,000+ payments.**

??? tip "Hint"
    This is a combination of `CASE` for Korean method labels + `COUNT(refunded_at)` for refund count + `HAVING` + `ORDER BY`.

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

---

### Problem 29

**Customer profile completeness analysis: Find the customer count, percentage (%), average points, and VIP rate (%) per completeness score (0-4). Completeness = number of non-NULL columns among birth_date, gender, last_login_at, and acquisition_channel.**

??? tip "Hint"
    `(column IS NOT NULL)` returns 1 or 0 in SQLite. Adding all four gives the completeness score.

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

    > If higher profile completeness correlates with higher VIP rate and average points, this provides justification for profile completion campaigns.

---

### Problem 30

**Comprehensive dashboard: Find the active product count, average price, average margin rate (%), price tier classification, and low-stock product count (stock_qty <= 10) per brand from the products table. Only include brands with 5+ active products, sorted by active product count descending, limited to the top 10.**

??? tip "Hint"
    Use multiple aggregations and CASE simultaneously. This is a combination of `WHERE is_active = 1` + `GROUP BY brand` + `HAVING` + `ORDER BY` + `LIMIT`.

??? success "Answer"
    ```sql
    SELECT brand,
           COUNT(*) AS active_count,
           ROUND(AVG(price)) AS avg_price,
           ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct,
           CASE
               WHEN AVG(price) >= 1000000 THEN 'Premium'
               WHEN AVG(price) >= 300000 THEN 'Mainstream'
               ELSE 'Budget'
           END AS brand_tier,
           SUM(CASE WHEN stock_qty <= 10 THEN 1 ELSE 0 END) AS low_stock_count
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 5
    ORDER BY active_count DESC
    LIMIT 10;
    ```

    > This type of query is used in real e-commerce operations to evaluate brand portfolios. Brands with low margin rates and many low-stock products need profitability improvements.
