# CASE Expressions

!!! info "Tables"
    `products` — Products (name, price, stock, brand)  
    `customers` — Customers (grade, points, channel)  
    `orders` — Orders (status, amount, date)  
    `reviews` — Reviews (rating, content)  
    `payments` — Payments (method, amount, status)  

!!! abstract "Concepts"
    `CASE WHEN THEN ELSE END`, Simple CASE, Searched CASE, CASE + aggregation/sorting

Practice the basic usage of simple CASE and searched CASE.

---

### Problem 1

**Query customer names and tiers, displaying the tier in Korean. BRONZE='브론즈', SILVER='실버', GOLD='골드', VIP='VIP'**

??? tip "Hint"
    Simple CASE syntax: `CASE column WHEN value1 THEN result1 WHEN value2 THEN result2 ... END`

??? success "Answer"
    ```sql
    SELECT name,
           CASE grade
               WHEN 'BRONZE' THEN '브론즈'
               WHEN 'SILVER' THEN '실버'
               WHEN 'GOLD' THEN '골드'
               WHEN 'VIP' THEN 'VIP'
           END AS grade_kr
    FROM customers
    LIMIT 10;
    ```

---

### Problem 2

**Display the product name, price, and price tier. Under 100K='Budget', 100K-500K='Mid-low', 500K-1M='Mid', 1M+='Premium'**

??? tip "Hint"
    Searched CASE syntax: `CASE WHEN condition1 THEN result1 WHEN condition2 THEN result2 ... ELSE default END`. Conditions are evaluated top-to-bottom, so order matters.

??? success "Answer"
    ```sql
    SELECT name, price,
           CASE
               WHEN price < 100000 THEN 'Budget'
               WHEN price < 500000 THEN 'Mid-low'
               WHEN price < 1000000 THEN 'Mid'
               ELSE 'Premium'
           END AS price_tier
    FROM products
    LIMIT 10;
    ```

---

### Problem 3

**Query order numbers and statuses, displaying the status in Korean. pending='주문접수', paid='결제완료', preparing='준비중', shipped='배송중', delivered='배송완료', confirmed='구매확정', cancelled='취소', return_requested='반품요청', returned='반품완료'**

??? tip "Hint"
    Use simple CASE to convert status values to Korean.

??? success "Answer"
    ```sql
    SELECT order_number,
           CASE status
               WHEN 'pending' THEN '주문접수'
               WHEN 'paid' THEN '결제완료'
               WHEN 'preparing' THEN '준비중'
               WHEN 'shipped' THEN '배송중'
               WHEN 'delivered' THEN '배송완료'
               WHEN 'confirmed' THEN '구매확정'
               WHEN 'cancelled' THEN '취소'
               WHEN 'return_requested' THEN '반품요청'
               WHEN 'returned' THEN '반품완료'
           END AS status_kr
    FROM orders
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```

---

### Problem 4

**Display review ratings as text. 5='Excellent', 4='Good', 3='Average', 2='Poor', 1='Terrible'**

??? tip "Hint"
    Use simple CASE: `CASE rating WHEN 5 THEN 'Excellent' ...`

??? success "Answer"
    ```sql
    SELECT rating,
           CASE rating
               WHEN 5 THEN 'Excellent'
               WHEN 4 THEN 'Good'
               WHEN 3 THEN 'Average'
               WHEN 2 THEN 'Poor'
               WHEN 1 THEN 'Terrible'
           END AS rating_text,
           title
    FROM reviews
    LIMIT 10;
    ```

---

### Problem 5

**Display the stock status of products. Stock 0='Out of stock', 1-10='Low', 11-100='Normal', 101+='Sufficient'**

??? tip "Hint"
    Use the `stock_qty` range as conditions in a searched CASE.

??? success "Answer"
    ```sql
    SELECT name, stock_qty,
           CASE
               WHEN stock_qty = 0 THEN 'Out of stock'
               WHEN stock_qty <= 10 THEN 'Low'
               WHEN stock_qty <= 100 THEN 'Normal'
               ELSE 'Sufficient'
           END AS stock_status
    FROM products
    LIMIT 10;
    ```

---

### Problem 6

**Display the payment method (`method`) in Korean. card='신용카드', bank_transfer='계좌이체', virtual_account='가상계좌', kakao_pay='카카오페이', naver_pay='네이버페이', point='포인트'. Show only the top 10 rows.**

??? tip "Hint"
    Use simple CASE to convert method values to Korean.

??? success "Answer"
    ```sql
    SELECT order_id,
           CASE method
               WHEN 'card' THEN '신용카드'
               WHEN 'bank_transfer' THEN '계좌이체'
               WHEN 'virtual_account' THEN '가상계좌'
               WHEN 'kakao_pay' THEN '카카오페이'
               WHEN 'naver_pay' THEN '네이버페이'
               WHEN 'point' THEN '포인트'
           END AS method_kr,
           amount
    FROM payments
    LIMIT 10;
    ```

---

### Problem 7

**Display the customer active status as text. is_active 1='Active', 0='Withdrawn'**

??? tip "Hint"
    Use `CASE is_active WHEN 1 THEN 'Active' WHEN 0 THEN 'Withdrawn' END` or a searched CASE.

??? success "Answer"
    ```sql
    SELECT name, email,
           CASE is_active
               WHEN 1 THEN 'Active'
               WHEN 0 THEN 'Withdrawn'
           END AS status
    FROM customers
    LIMIT 10;
    ```

---

### Problem 8

**Display the order amount tier. Under 50K='Small', 50K-200K='Regular', 200K-1M='Large', 1M+='VIP-level'. Show the 10 most recent orders.**

??? tip "Hint"
    Use searched CASE to categorize `total_amount` ranges.

??? success "Answer"
    ```sql
    SELECT order_number, total_amount,
           CASE
               WHEN total_amount < 50000 THEN 'Small'
               WHEN total_amount < 200000 THEN 'Regular'
               WHEN total_amount < 1000000 THEN 'Large'
               ELSE 'VIP-level'
           END AS amount_tier
    FROM orders
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```

---

### Problem 9

**Display the comprehensive sale status of products. If is_active is 0, show 'Discontinued'; if stock_qty is 0, show 'Out of stock'; otherwise show 'On sale'**

??? tip "Hint"
    CASE evaluates conditions top-to-bottom. Check discontinuation first, then out-of-stock.

??? success "Answer"
    ```sql
    SELECT name, price, is_active, stock_qty,
           CASE
               WHEN is_active = 0 THEN 'Discontinued'
               WHEN stock_qty = 0 THEN 'Out of stock'
               ELSE 'On sale'
           END AS sale_status
    FROM products
    LIMIT 15;
    ```

---

### Problem 10

**Display the customer points level. 0='None', 1-5000='Low', 5001-20000='Medium', 20001+='High'. Show only the top 10 rows.**

??? tip "Hint"
    Classify `point_balance` ranges using searched CASE.

??? success "Answer"
    ```sql
    SELECT name, point_balance,
           CASE
               WHEN point_balance = 0 THEN 'None'
               WHEN point_balance <= 5000 THEN 'Low'
               WHEN point_balance <= 20000 THEN 'Medium'
               ELSE 'High'
           END AS point_level
    FROM customers
    LIMIT 10;
    ```

---

Combine CASE + GROUP BY, CASE + ORDER BY, and CASE + aggregate functions.

---

### Problem 11

**Classify products by price tier and find the product count per tier. Under 100K='Budget', 100K-500K='Mid-low', 500K-1M='Mid', 1M+='Premium'**

??? tip "Hint"
    Use the CASE expression in both `SELECT` and `GROUP BY`.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN price < 100000 THEN 'Budget'
               WHEN price < 500000 THEN 'Mid-low'
               WHEN price < 1000000 THEN 'Mid'
               ELSE 'Premium'
           END AS price_tier,
           COUNT(*) AS product_count
    FROM products
    GROUP BY CASE
                 WHEN price < 100000 THEN 'Budget'
                 WHEN price < 500000 THEN 'Mid-low'
                 WHEN price < 1000000 THEN 'Mid'
                 ELSE 'Premium'
             END
    ORDER BY product_count DESC;
    ```

---

### Problem 12

**Classify orders into 3 major status groups and find the count for each. pending/paid/preparing='Processing', shipped/delivered/confirmed='Completed', cancelled/return_requested/returned='Cancelled/Returned'**

??? tip "Hint"
    Use `CASE WHEN status IN (...) THEN ...` to group multiple values into a single category.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN status IN ('pending', 'paid', 'preparing') THEN 'Processing'
               WHEN status IN ('shipped', 'delivered', 'confirmed') THEN 'Completed'
               WHEN status IN ('cancelled', 'return_requested', 'returned') THEN 'Cancelled/Returned'
           END AS status_group,
           COUNT(*) AS order_count
    FROM orders
    GROUP BY status_group
    ORDER BY order_count DESC;
    ```

---

### Problem 13

**Classify reviews as Positive (4-5 stars), Neutral (3 stars), or Negative (1-2 stars) and find the count for each group.**

??? tip "Hint"
    Use searched CASE to divide the rating range into 3 groups.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN rating >= 4 THEN 'Positive'
               WHEN rating = 3 THEN 'Neutral'
               ELSE 'Negative'
           END AS sentiment,
           COUNT(*) AS review_count
    FROM reviews
    GROUP BY sentiment
    ORDER BY review_count DESC;
    ```

---

### Problem 14

**Classify products by price tier and find the average stock quantity per tier. Round to no decimal places.**

??? tip "Hint"
    Classify the price tier with CASE and calculate the average stock with `AVG(stock_qty)`.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN price < 100000 THEN 'Budget'
               WHEN price < 500000 THEN 'Mid-low'
               WHEN price < 1000000 THEN 'Mid'
               ELSE 'Premium'
           END AS price_tier,
           COUNT(*) AS product_count,
           ROUND(AVG(stock_qty)) AS avg_stock
    FROM products
    GROUP BY price_tier
    ORDER BY avg_stock DESC;
    ```

---

### Problem 15

**Classify customers by gender, displaying NULL as 'Not entered', and find the count per group.**

??? tip "Hint"
    Handle NULL first: `CASE WHEN gender IS NULL THEN 'Not entered' WHEN gender = 'M' THEN 'Male' ...`

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN gender IS NULL THEN 'Not entered'
               WHEN gender = 'M' THEN 'Male'
               WHEN gender = 'F' THEN 'Female'
           END AS gender_label,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY gender_label
    ORDER BY customer_count DESC;
    ```

---

### Problem 16

**Find the count and average payment amount per payment method, displaying the method in Korean. Round the average amount to the nearest won.**

??? tip "Hint"
    Convert method to Korean with CASE, then use GROUP BY and aggregate functions together.

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
           ROUND(AVG(amount)) AS avg_amount
    FROM payments
    GROUP BY method
    ORDER BY payment_count DESC;
    ```

---

### Problem 17

**Sort products with out-of-stock items (stock_qty=0) at the bottom, and the rest by price ascending. Show only the top 15 rows.**

??? tip "Hint"
    Using CASE in `ORDER BY` enables custom sorting. Return 1 for out-of-stock and 0 otherwise to push out-of-stock items to the bottom.

??? success "Answer"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE is_active = 1
    ORDER BY CASE WHEN stock_qty = 0 THEN 1 ELSE 0 END,
             price ASC
    LIMIT 15;
    ```

---

### Problem 18

**Sort customer tiers in custom order (VIP > GOLD > SILVER > BRONZE) and show the customer count per tier.**

??? tip "Hint"
    Use `ORDER BY CASE grade WHEN 'VIP' THEN 1 WHEN 'GOLD' THEN 2 ...` to specify the desired order.

??? success "Answer"
    ```sql
    SELECT grade, COUNT(*) AS customer_count
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

### Problem 19

**Find the order count and total revenue per order amount tier. Tiers: under 50K, 50K-200K, 200K-1M, 1M+**

??? tip "Hint"
    Classify the amount tier with CASE, then aggregate with `COUNT(*)` and `SUM(total_amount)` together.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN total_amount < 50000 THEN 'Under 50K'
               WHEN total_amount < 200000 THEN '50K-200K'
               WHEN total_amount < 1000000 THEN '200K-1M'
               ELSE '1M+'
           END AS amount_tier,
           COUNT(*) AS order_count,
           ROUND(SUM(total_amount)) AS total_revenue
    FROM orders
    GROUP BY amount_tier
    ORDER BY total_revenue DESC;
    ```

---

### Problem 20

**Classify reviews by rating group (Positive/Neutral/Negative) and find the percentage (%) of reviews with a title.**

??? tip "Hint"
    Calculate the non-NULL title ratio with `COUNT(title) * 100.0 / COUNT(*)`. Group by rating with CASE, then GROUP BY.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN rating >= 4 THEN 'Positive'
               WHEN rating = 3 THEN 'Neutral'
               ELSE 'Negative'
           END AS sentiment,
           COUNT(*) AS review_count,
           ROUND(COUNT(title) * 100.0 / COUNT(*), 1) AS title_rate_pct
    FROM reviews
    GROUP BY sentiment
    ORDER BY review_count DESC;
    ```

---

Practice business classification, compound conditions, and CASE applications.

---

### Problem 21

**Classify products by margin rate tier. Margin rate = (price - cost_price) / price * 100. Under 10%='Low margin', 10-20%='Standard', 20-30%='High margin', 30%+='Premium'. For active products only (is_active = 1), find the product count and average margin rate per tier.**

??? tip "Hint"
    Use the margin rate formula directly in the CASE conditions. Calculate with `(price - cost_price) * 100.0 / price`.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN (price - cost_price) * 100.0 / price < 10 THEN 'Low margin'
               WHEN (price - cost_price) * 100.0 / price < 20 THEN 'Standard'
               WHEN (price - cost_price) * 100.0 / price < 30 THEN 'High margin'
               ELSE 'Premium'
           END AS margin_tier,
           COUNT(*) AS product_count,
           ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1
    GROUP BY margin_tier
    ORDER BY avg_margin_pct DESC;
    ```

---

### Problem 22

**Classify customers by signup year and tier, and find the count. Extract the signup year with SUBSTR(created_at, 1, 4). Only include the last 3 years (2023, 2024, 2025).**

??? tip "Hint"
    Use both `SUBSTR(created_at, 1, 4)` and `grade` in `GROUP BY`. Filter years with `WHERE`, not `HAVING`.

??? success "Answer"
    ```sql
    SELECT SUBSTR(created_at, 1, 4) AS join_year,
           grade,
           COUNT(*) AS customer_count
    FROM customers
    WHERE SUBSTR(created_at, 1, 4) IN ('2023', '2024', '2025')
    GROUP BY join_year, grade
    ORDER BY join_year, CASE grade
                            WHEN 'VIP' THEN 1
                            WHEN 'GOLD' THEN 2
                            WHEN 'SILVER' THEN 3
                            WHEN 'BRONZE' THEN 4
                        END;
    ```

---

### Problem 23

**Analyze the shipping fee policy. Orders under 50K are charged shipping, orders 50K+ get free shipping. For 2024 orders, find the count, average order amount, and total shipping fee for paid/free shipping.**

??? tip "Hint"
    Classify with `CASE WHEN total_amount < 50000 THEN 'Paid shipping' ELSE 'Free shipping' END`.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN total_amount < 50000 THEN 'Paid shipping'
               ELSE 'Free shipping'
           END AS shipping_type,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount,
           ROUND(SUM(shipping_fee)) AS total_shipping_fee
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY shipping_type;
    ```

---

### Problem 24

**Find the count per payment status, displaying the status in Korean, and also show the percentage (%) of 'completed' payments.**

??? tip "Hint"
    Calculate the ratio of a specific condition to the total with `SUM(CASE WHEN ... THEN 1 ELSE 0 END) * 100.0 / COUNT(*)`.

??? success "Answer"
    ```sql
    SELECT CASE status
               WHEN 'completed' THEN '완료'
               WHEN 'pending' THEN '대기'
               WHEN 'failed' THEN '실패'
               WHEN 'refunded' THEN '환불'
           END AS status_kr,
           COUNT(*) AS payment_count,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM payments
    GROUP BY status
    ORDER BY payment_count DESC;
    ```

    > If you haven't learned window functions yet, you can omit the percentage and just calculate the count.

---

### Problem 25

**Classify customers into 3 activity levels. Withdrawn (is_active=0), Dormant (is_active=1 but last_login_at is NULL), Active (the rest). Find the customer count per group.**

??? tip "Hint"
    The order of CASE conditions matters. Check `is_active = 0` first, then `last_login_at IS NULL`.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN is_active = 0 THEN 'Withdrawn'
               WHEN last_login_at IS NULL THEN 'Dormant'
               ELSE 'Active'
           END AS activity_status,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY activity_status
    ORDER BY customer_count DESC;
    ```

---

### Problem 26

**Find the monthly order count for 2024, displaying the season as well. Mar-May='Spring', Jun-Aug='Summer', Sep-Nov='Fall', Dec-Feb='Winter'**

??? tip "Hint"
    Extract the month with `CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER)`. Classify the season with CASE.

??? success "Answer"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 7) AS month,
           CASE
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (3, 4, 5) THEN 'Spring'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (6, 7, 8) THEN 'Summer'
               WHEN CAST(SUBSTR(ordered_at, 6, 2) AS INTEGER) IN (9, 10, 11) THEN 'Fall'
               ELSE 'Winter'
           END AS season,
           COUNT(*) AS order_count
    FROM orders
    WHERE ordered_at LIKE '2024%'
    GROUP BY month
    ORDER BY month;
    ```

---

### Problem 27

**Find the product count and average price per brand, showing only brands with 10+ products. Classify brands by average price as 'Premium brand' (1M+), 'Mainstream brand' (300K-1M), or 'Budget brand' (under 300K).**

??? tip "Hint"
    Filter with `GROUP BY brand` + `HAVING COUNT(*) >= 10`, then classify the average price with `CASE`.

??? success "Answer"
    ```sql
    SELECT brand,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price,
           CASE
               WHEN AVG(price) >= 1000000 THEN 'Premium brand'
               WHEN AVG(price) >= 300000 THEN 'Mainstream brand'
               ELSE 'Budget brand'
           END AS brand_tier
    FROM products
    WHERE is_active = 1
    GROUP BY brand
    HAVING COUNT(*) >= 10
    ORDER BY avg_price DESC;
    ```

---

### Problem 28

**Points usage analysis: Classify orders by whether points were used or not, and find the count, average order amount, and average discount amount for each.**

??? tip "Hint"
    Classify with `CASE WHEN point_used > 0 THEN 'Used' ELSE 'Not used' END`.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN point_used > 0 THEN 'Points used'
               ELSE 'Points not used'
           END AS point_usage,
           COUNT(*) AS order_count,
           ROUND(AVG(total_amount)) AS avg_amount,
           ROUND(AVG(discount_amount)) AS avg_discount
    FROM orders
    GROUP BY point_usage;
    ```

---

### Problem 29

**Classify products into 4 groups by discontinuation status and stock status. (Discontinued+In stock, Discontinued+No stock, On sale+In stock, On sale+No stock) Find the product count and average price for each group.**

??? tip "Hint"
    Combine two conditions (is_active, stock_qty) in a CASE to classify into 4 categories.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN is_active = 0 AND stock_qty > 0 THEN 'Discontinued+In stock'
               WHEN is_active = 0 AND stock_qty = 0 THEN 'Discontinued+No stock'
               WHEN is_active = 1 AND stock_qty > 0 THEN 'On sale+In stock'
               WHEN is_active = 1 AND stock_qty = 0 THEN 'On sale+Out of stock'
           END AS status_group,
           COUNT(*) AS product_count,
           ROUND(AVG(price)) AS avg_price
    FROM products
    GROUP BY status_group
    ORDER BY product_count DESC;
    ```

---

### Problem 30

**Card payment installment analysis: For card payments (method = 'card'), find the count and average amount per installment tier (Lump sum, 2-3 months, 4-6 months, 7+ months, No info). Lump sum means installment_months is 0.**

??? tip "Hint"
    Filter card payments with `WHERE method = 'card'`. Also consider cases where `installment_months` is NULL.

??? success "Answer"
    ```sql
    SELECT CASE
               WHEN installment_months IS NULL THEN 'No info'
               WHEN installment_months = 0 THEN 'Lump sum'
               WHEN installment_months <= 3 THEN '2-3 months'
               WHEN installment_months <= 6 THEN '4-6 months'
               ELSE '7+ months'
           END AS installment_tier,
           COUNT(*) AS payment_count,
           ROUND(AVG(amount)) AS avg_amount
    FROM payments
    WHERE method = 'card'
    GROUP BY installment_tier
    ORDER BY payment_count DESC;
    ```

    > There tends to be a pattern where longer installment periods have higher average payment amounts. This reflects consumer behavior of preferring installments for high-value purchases.
