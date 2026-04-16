# Data Quality Checks

**Tables:** `customers`, `orders`, `order_items`, `payments`, `products`, `shipping`

**Concepts:** data validation, orphan records, NULL analysis, status consistency, date validation, duplicates, outliers, cross-table consistency


---


### 1. Check if there are any orders placed before the customer's s


Check if there are any orders placed before the customer's signup date.


**Hint 1:** JOIN `orders` with `customers`, then detect time reversal with `WHERE ordered_at < created_at`.


??? success "Answer"
    ```sql
    SELECT
        o.order_number, o.ordered_at,
        c.name, c.created_at AS signup_date
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.id
    WHERE o.ordered_at < c.created_at;
    ```


---


### 2. Check if there are payment records with no corresponding ord


Check if there are payment records with no corresponding order.


**Hint 1:** `payments LEFT JOIN orders`, then `WHERE o.id IS NULL` to find orphan records without a parent.


??? success "Answer"
    ```sql
    SELECT p.id, p.order_id, p.amount
    FROM payments p
    LEFT JOIN orders o ON p.order_id = o.id
    WHERE o.id IS NULL;
    ```


---


### 3. Find columns with high NULL rates in each table.


Find columns with high NULL rates in each table.


**Hint 1:** Calculate the NULL ratio for each column with `SUM(CASE WHEN column IS NULL THEN 1 ELSE 0 END) / COUNT(*)`.


??? success "Answer"
    ```sql
    -- customers 테이블의 NULL 비율
    SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN birth_date IS NULL THEN 1 ELSE 0 END) AS null_birthdate,
        ROUND(100.0 * SUM(CASE WHEN birth_date IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_birthdate,
        SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) AS null_gender,
        ROUND(100.0 * SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_gender,
        SUM(CASE WHEN last_login_at IS NULL THEN 1 ELSE 0 END) AS null_login,
        ROUND(100.0 * SUM(CASE WHEN last_login_at IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_login
    FROM customers;
    ```


---


### 4. Find inconsistencies where shipping is delivered but the ord


Find inconsistencies where shipping is delivered but the order status is still shipped.


**Hint 1:** JOIN `orders` with `shipping`, then find rows where `shipping.status = 'delivered'` but `orders.status` is not a delivery-completed state.


??? success "Answer"
    ```sql
    SELECT
        o.order_number, o.status AS order_status,
        sh.status AS shipping_status, sh.delivered_at
    FROM orders o
    INNER JOIN shipping sh ON o.id = sh.order_id
    WHERE sh.status = 'delivered'
      AND o.status NOT IN ('delivered', 'confirmed', 'return_requested', 'returned');
    ```


---


### 5. Find abnormal records where the delivery date is earlier tha


Find abnormal records where the delivery date is earlier than the shipment date.


**Hint 1:** Detect date reversal with `WHERE delivered_at < shipped_at`. Only target rows where both columns are NOT NULL.


??? success "Answer"
    ```sql
    SELECT
        sh.id, o.order_number,
        sh.shipped_at, sh.delivered_at,
        ROUND(JULIANDAY(sh.delivered_at) - JULIANDAY(sh.shipped_at), 1) AS days
    FROM shipping sh
    INNER JOIN orders o ON sh.order_id = o.id
    WHERE sh.shipped_at IS NOT NULL
      AND sh.delivered_at IS NOT NULL
      AND sh.delivered_at < sh.shipped_at;
    ```


---


### 6. Check if the same product is registered multiple times in th


Check if the same product is registered multiple times in the same order.


**Hint 1:** After `GROUP BY order_id, product_id`, use `HAVING COUNT(*) > 1` to detect combinations that appear more than once.


??? success "Answer"
    ```sql
    SELECT order_id, product_id, COUNT(*) AS cnt
    FROM order_items
    GROUP BY order_id, product_id
    HAVING COUNT(*) > 1;
    ```


---


### 7. Find abnormally large values in prices, quantities, ratings,


Find abnormally large values in prices, quantities, ratings, etc.


**Hint 1:** Check for values exceeding N times the average like `WHERE total_amount > (SELECT AVG(total_amount) * 10 FROM orders)`, and also check for negative or zero values.


??? success "Answer"
    ```sql
    -- 주문 금액이 평균의 10배 이상인 이상치
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE total_amount > (SELECT AVG(total_amount) * 10 FROM orders)
    ORDER BY total_amount DESC;
    ```


---


### 8. Find inconsistencies where a cancelled order has a delivery 


Find inconsistencies where a cancelled order has a delivery completion record.


**Hint 1:** JOIN `orders` with `shipping`, then detect contradictory data where `o.status = 'cancelled' AND sh.status = 'delivered'`.


??? success "Answer"
    ```sql
    SELECT
        o.order_number, o.status, o.cancelled_at,
        sh.status AS ship_status, sh.delivered_at
    FROM orders o
    INNER JOIN shipping sh ON o.id = sh.order_id
    WHERE o.status = 'cancelled'
      AND sh.status = 'delivered';
    ```


---


### 9. Check if discontinued or inactive (is_active=0) products hav


Check if discontinued or inactive (is_active=0) products have been ordered recently.


**Hint 1:** Check with `HAVING` whether the most recent order date (`MAX(ordered_at)`) for inactive products is after the discontinuation date.


??? success "Answer"
    ```sql
    SELECT
        p.name, p.is_active, p.discontinued_at,
        MAX(o.ordered_at) AS last_ordered
    FROM products p
    INNER JOIN order_items oi ON p.id = oi.product_id
    INNER JOIN orders o ON oi.order_id = o.id
    WHERE p.is_active = 0 OR p.discontinued_at IS NOT NULL
    GROUP BY p.id, p.name, p.is_active, p.discontinued_at
    HAVING MAX(o.ordered_at) > COALESCE(p.discontinued_at, '9999-12-31');
    ```


---


### 10. Verify whether orders and payments match 1:1.


Verify whether orders and payments match 1:1.


**Hint 1:** Check both directions with `LEFT JOIN` -- orders without payments, and payments without orders.


??? success "Answer"
    ```sql
    -- 주문은 있는데 결제가 없는 경우
    SELECT o.id, o.order_number
    FROM orders o
    LEFT JOIN payments p ON o.id = p.order_id
    WHERE p.id IS NULL;
    ```


---


### 11. Check whether the product's current price matches the latest


Check whether the product's current price matches the latest record in the price history.


**Hint 1:** Compare the price from `product_prices` where `ended_at IS NULL` (currently active price) with `products.price` to detect mismatches.


??? success "Answer"
    ```sql
    SELECT
        p.name, p.price AS current_price,
        pp.price AS latest_history_price
    FROM products p
    INNER JOIN product_prices pp ON p.id = pp.product_id
    WHERE pp.ended_at IS NULL
      AND p.price <> pp.price;
    ```


---


### 12. Summarize key quality metrics in a single query.


Summarize key quality metrics in a single query.


**Hint 1:** Create each quality check as a scalar subquery `(SELECT COUNT(*) FROM ... WHERE condition)` and list them all in a single SELECT.


??? success "Answer"
    ```sql
    SELECT
        (SELECT COUNT(*) FROM orders o INNER JOIN customers c ON o.customer_id = c.id WHERE o.ordered_at < c.created_at) AS orders_before_signup,
        (SELECT COUNT(*) FROM payments p LEFT JOIN orders o ON p.order_id = o.id WHERE o.id IS NULL) AS orphan_payments,
        (SELECT COUNT(*) FROM shipping WHERE delivered_at < shipped_at) AS invalid_delivery_dates,
        (SELECT COUNT(*) FROM order_items GROUP BY order_id, product_id HAVING COUNT(*) > 1) AS duplicate_items,
        (SELECT COUNT(*) FROM products WHERE stock_qty < 0) AS negative_stock,
        (SELECT COUNT(*) FROM orders WHERE total_amount <= 0 AND status NOT IN ('cancelled')) AS zero_amount_orders;
    ```


---
