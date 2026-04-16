# Data Quality Checks

!!! info "Tables"
    `customers` — Customers (grade, points, channel)  
    `products` — Products (name, price, stock, brand)  
    `orders` — Orders (status, amount, date)  
    `order_items` — Order items (qty, unit price)  
    `payments` — Payments (method, amount, status)  
    `shipping` — Shipping (carrier, tracking, status)  
    `reviews` — Reviews (rating, content)  
    `returns` — Returns (reason, status)  
    `customer_addresses` — Addresses (address, default flag)  
    `coupons` — Coupons (discount, validity)  
    `coupon_usage` — Coupon usage records  
    `product_prices` — Price history (change reason)  

!!! abstract "Concepts"
    NULL/duplicate/range checks, Referential integrity verification, Date inversion detection, Outlier discovery, Comprehensive quality dashboard

## Basic (1~7): NULL, Duplicates, Value Ranges

### Problem 1

Calculate the NULL ratio for each column in the customers table. Compute NULL count and percentage (%) for `birth_date`, `gender`, and `last_login_at`.

??? tip "Hint"
    Use `SUM(CASE WHEN column IS NULL THEN 1 ELSE 0 END)` for NULL count and `COUNT(*)` for total count to calculate the ratio.

??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN birth_date IS NULL THEN 1 ELSE 0 END) AS null_birth,
        ROUND(100.0 * SUM(CASE WHEN birth_date IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_birth,
        SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) AS null_gender,
        ROUND(100.0 * SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_gender,
        SUM(CASE WHEN last_login_at IS NULL THEN 1 ELSE 0 END) AS null_login,
        ROUND(100.0 * SUM(CASE WHEN last_login_at IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_login
    FROM customers;
    ```

---

### Problem 2

Check if there are customers with duplicate emails. Output duplicate emails and their counts.

??? tip "Hint"
    Group by `GROUP BY email` then detect duplicates with `HAVING COUNT(*) > 1`. Since the `email` column has a UNIQUE constraint, theoretically there should be 0 rows.

??? success "Answer"
    ```sql
    SELECT email, COUNT(*) AS cnt
    FROM customers
    GROUP BY email
    HAVING COUNT(*) > 1
    ORDER BY cnt DESC;
    ```

---

### Problem 3

Find products with abnormal prices. Output products with prices at or below 0, or priced below cost (negative margin).

??? tip "Hint"
    Use `WHERE price <= 0 OR price < cost_price` to detect abnormal pricing.

??? success "Answer"
    ```sql
    SELECT name, sku, price, cost_price,
           ROUND(price - cost_price, 0) AS margin
    FROM products
    WHERE price <= 0 OR price < cost_price
    ORDER BY margin ASC;
    ```

---

### Problem 4

Find orders with amount at or below 0 that are not in cancelled status.

??? tip "Hint"
    Orders with `total_amount <= 0` and `status NOT IN ('cancelled', 'returned', 'return_requested')` may be data errors.

??? success "Answer"
    ```sql
    SELECT order_number, status, total_amount, ordered_at
    FROM orders
    WHERE total_amount <= 0
      AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY ordered_at DESC;
    ```

---

### Problem 5

Check if any review ratings fall outside the allowed range (1~5).

??? tip "Hint"
    With a `CHECK(rating BETWEEN 1 AND 5)` constraint, there should theoretically be 0 rows. Verify with `WHERE rating NOT BETWEEN 1 AND 5`.

??? success "Answer"
    ```sql
    SELECT id, product_id, customer_id, rating
    FROM reviews
    WHERE rating < 1 OR rating > 5;
    ```

---

### Problem 6

Find products with negative stock quantities. Output product name, SKU, stock, and active status.

??? tip "Hint"
    Even with a `CHECK(stock_qty >= 0)` constraint, negative values may exist in real data. Check with `WHERE stock_qty < 0`.

??? success "Answer"
    ```sql
    SELECT name, sku, stock_qty, is_active
    FROM products
    WHERE stock_qty < 0
    ORDER BY stock_qty ASC;
    ```

---

### Problem 7

Check if the same product is duplicated within the same order. Output duplicate combinations and their counts.

??? tip "Hint"
    Use `GROUP BY order_id, product_id` then `HAVING COUNT(*) > 1` to detect combinations with 2 or more entries.

??? success "Answer"
    ```sql
    SELECT order_id, product_id, COUNT(*) AS cnt
    FROM order_items
    GROUP BY order_id, product_id
    HAVING COUNT(*) > 1
    ORDER BY cnt DESC;
    ```

---

## Applied (8~14): FK Integrity, Date Inversions, Status Mismatches

### Problem 8

Check for payment records with no corresponding order (orphan records).

??? tip "Hint"
    Use `payments LEFT JOIN orders`, then find payments where `orders.id IS NULL` -- these are orphan records with no parent.

??? success "Answer"
    ```sql
    SELECT p.id AS payment_id, p.order_id, p.method, p.amount
    FROM payments AS p
    LEFT JOIN orders AS o ON p.order_id = o.id
    WHERE o.id IS NULL;
    ```

---

### Problem 9

Check if any orders have an order date earlier than the customer's signup date. Time inversion is a classic data error.

??? tip "Hint"
    Join `orders` with `customers`, then find rows where `ordered_at < created_at`.

??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        o.ordered_at,
        c.name,
        c.created_at AS signup_date,
        ROUND(JULIANDAY(c.created_at) - JULIANDAY(o.ordered_at), 1) AS days_diff
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.ordered_at < c.created_at
    ORDER BY days_diff DESC;
    ```

---

### Problem 10

Find abnormal records where the delivery date (`delivered_at`) is earlier than the shipment date (`shipped_at`).

??? tip "Hint"
    Among rows where both dates are NOT NULL, find cases where `delivered_at < shipped_at`.

??? success "Answer"
    ```sql
    SELECT
        sh.id,
        o.order_number,
        sh.shipped_at,
        sh.delivered_at,
        ROUND(JULIANDAY(sh.delivered_at) - JULIANDAY(sh.shipped_at), 1) AS days_diff
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE sh.shipped_at IS NOT NULL
      AND sh.delivered_at IS NOT NULL
      AND sh.delivered_at < sh.shipped_at;
    ```

---

### Problem 11

Find mismatches where shipping is `delivered` but the order status has not progressed to a post-delivery stage.

??? tip "Hint"
    If shipping is `delivered`, the order status should be one of `delivered`, `confirmed`, `return_requested`, or `returned`. Any other status is a mismatch.

??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        o.status AS order_status,
        sh.status AS ship_status,
        sh.delivered_at
    FROM orders AS o
    INNER JOIN shipping AS sh ON o.id = sh.order_id
    WHERE sh.status = 'delivered'
      AND o.status NOT IN ('delivered', 'confirmed', 'return_requested', 'returned');
    ```

---

### Problem 12

Find contradictory data where an order is cancelled but has a delivery completion record.

??? tip "Hint"
    Orders with `orders.status = 'cancelled'` and `shipping.status = 'delivered'` are logically contradictory.

??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        o.status AS order_status,
        o.cancelled_at,
        sh.status AS ship_status,
        sh.delivered_at
    FROM orders AS o
    INNER JOIN shipping AS sh ON o.id = sh.order_id
    WHERE o.status = 'cancelled'
      AND sh.status = 'delivered';
    ```

---

### Problem 13

Check if discontinued products (`discontinued_at IS NOT NULL`) have been ordered after their discontinuation date.

??? tip "Hint"
    Compare the product's `discontinued_at` with the order's `ordered_at`. Orders after the discontinuation date are abnormal.

??? success "Answer"
    ```sql
    SELECT
        p.name,
        p.discontinued_at,
        o.order_number,
        o.ordered_at
    FROM products AS p
    INNER JOIN order_items AS oi ON p.id = oi.product_id
    INNER JOIN orders AS o ON oi.order_id = o.id
    WHERE p.discontinued_at IS NOT NULL
      AND o.ordered_at > p.discontinued_at
    ORDER BY o.ordered_at DESC
    LIMIT 20;
    ```

---

### Problem 14

Find products where the current price (`products.price`) does not match the currently effective price in the price history table (`product_prices` where `ended_at IS NULL`).

??? tip "Hint"
    Rows in `product_prices` where `ended_at IS NULL` represent the currently active price. If this differs from `products.price`, it's a sync error.

??? success "Answer"
    ```sql
    SELECT
        p.name,
        p.price AS current_price,
        pp.price AS history_price,
        ROUND(p.price - pp.price, 0) AS diff
    FROM products AS p
    INNER JOIN product_prices AS pp ON p.id = pp.product_id
    WHERE pp.ended_at IS NULL
      AND p.price <> pp.price
    ORDER BY ABS(p.price - pp.price) DESC;
    ```

---

## Advanced (15~20): Comprehensive Quality Reports

### Problem 15

Find orders where the payment amount does not match the order amount. Compare the sum of completed payments (`status = 'completed'`) with `orders.total_amount`.

??? tip "Hint"
    Compute per-order payment totals via subquery, then compare with `orders.total_amount`. There may be decimal differences, so filter with `ABS(difference) > 1`.

??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        o.total_amount AS order_amount,
        pay_sum.paid_total,
        ROUND(o.total_amount - pay_sum.paid_total, 2) AS diff
    FROM orders AS o
    INNER JOIN (
        SELECT order_id, SUM(amount) AS paid_total
        FROM payments
        WHERE status = 'completed'
        GROUP BY order_id
    ) AS pay_sum ON o.id = pay_sum.order_id
    WHERE ABS(o.total_amount - pay_sum.paid_total) > 1
    ORDER BY ABS(diff) DESC
    LIMIT 20;
    ```

---

### Problem 16

Verify that each customer has exactly 1 default shipping address (`is_default = 1`). Find customers with 0 or 2+ default addresses.

??? tip "Hint"
    Count `is_default = 1` rows per customer in `customer_addresses`, then find customers where the count is not 1. Use LEFT JOIN to find customers with no addresses at all.

??? success "Answer"
    ```sql
    -- Customers with 2+ default addresses
    SELECT
        c.name,
        c.email,
        COUNT(*) AS default_count
    FROM customers AS c
    INNER JOIN customer_addresses AS ca ON c.id = ca.customer_id
    WHERE ca.is_default = 1
    GROUP BY c.id, c.name, c.email
    HAVING COUNT(*) > 1;
    ```

---

### Problem 17

Check if any coupon usage in `coupon_usage` exceeds the `per_user_limit`. Find cases where per-customer/per-coupon usage count exceeds the coupon's `per_user_limit`.

??? tip "Hint"
    Group `coupon_usage` by `coupon_id, customer_id` to count usage, then compare with `coupons.per_user_limit`.

??? success "Answer"
    ```sql
    SELECT
        cp.code AS coupon_code,
        cp.name AS coupon_name,
        c.name AS customer_name,
        COUNT(*) AS usage_count,
        cp.per_user_limit
    FROM coupon_usage AS cu
    INNER JOIN coupons AS cp ON cu.coupon_id = cp.id
    INNER JOIN customers AS c ON cu.customer_id = c.id
    GROUP BY cu.coupon_id, cu.customer_id, cp.code, cp.name, c.name, cp.per_user_limit
    HAVING COUNT(*) > cp.per_user_limit
    ORDER BY usage_count DESC;
    ```

---

### Problem 18

Find orders in the `returns` table where the total refund amount exceeds the original order amount.

??? tip "Hint"
    Compute per-order refund totals and compare with `orders.total_amount`.

??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        o.total_amount AS order_amount,
        SUM(ret.refund_amount) AS total_refund,
        ROUND(SUM(ret.refund_amount) - o.total_amount, 2) AS over_refund
    FROM returns AS ret
    INNER JOIN orders AS o ON ret.order_id = o.id
    GROUP BY ret.order_id, o.order_number, o.total_amount
    HAVING SUM(ret.refund_amount) > o.total_amount
    ORDER BY over_refund DESC;
    ```

---

### Problem 19

Calculate a data completeness score per table. Compute (1) total row count and (2) average non-NULL ratio for nullable columns. Combine `customers`, `products`, and `orders` using UNION ALL.

??? tip "Hint"
    Calculate the non-NULL ratio for each nullable column as `1 - (NULL count / total)`, then average across columns.

??? success "Answer"
    ```sql
    SELECT 'customers' AS table_name,
           COUNT(*) AS total_rows,
           ROUND(100.0 * (
               (1.0 - 1.0 * SUM(CASE WHEN birth_date IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN last_login_at IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN acquisition_channel IS NULL THEN 1 ELSE 0 END) / COUNT(*))
           ) / 4.0, 1) AS completeness_pct
    FROM customers

    UNION ALL

    SELECT 'products' AS table_name,
           COUNT(*) AS total_rows,
           ROUND(100.0 * (
               (1.0 - 1.0 * SUM(CASE WHEN description IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN specs IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN weight_grams IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN model_number IS NULL THEN 1 ELSE 0 END) / COUNT(*))
           ) / 4.0, 1) AS completeness_pct
    FROM products

    UNION ALL

    SELECT 'orders' AS table_name,
           COUNT(*) AS total_rows,
           ROUND(100.0 * (
               (1.0 - 1.0 * SUM(CASE WHEN notes IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN completed_at IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN cancelled_at IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN staff_id IS NULL THEN 1 ELSE 0 END) / COUNT(*))
           ) / 4.0, 1) AS completeness_pct
    FROM orders;
    ```

---

### Problem 20

Summarize key data quality indicators in a single query. Output the following items as scalar subqueries in one row.

- Number of orders before signup date
- Number of orphan payment records
- Number of delivery date inversions
- Number of duplicate order details
- Number of products with negative stock
- Number of cancelled orders with delivery completion

??? tip "Hint"
    Create each quality check as a `(SELECT COUNT(*) FROM ... WHERE condition)` scalar subquery and list them all in a single SELECT.

??? success "Answer"
    ```sql
    SELECT
        (SELECT COUNT(*)
         FROM orders AS o
         INNER JOIN customers AS c ON o.customer_id = c.id
         WHERE o.ordered_at < c.created_at
        ) AS orders_before_signup,

        (SELECT COUNT(*)
         FROM payments AS p
         LEFT JOIN orders AS o ON p.order_id = o.id
         WHERE o.id IS NULL
        ) AS orphan_payments,

        (SELECT COUNT(*)
         FROM shipping
         WHERE shipped_at IS NOT NULL
           AND delivered_at IS NOT NULL
           AND delivered_at < shipped_at
        ) AS date_inversions,

        (SELECT COUNT(*)
         FROM (
             SELECT order_id, product_id
             FROM order_items
             GROUP BY order_id, product_id
             HAVING COUNT(*) > 1
         )
        ) AS duplicate_items,

        (SELECT COUNT(*)
         FROM products
         WHERE stock_qty < 0
        ) AS negative_stock,

        (SELECT COUNT(*)
         FROM orders AS o
         INNER JOIN shipping AS sh ON o.id = sh.order_id
         WHERE o.status = 'cancelled'
           AND sh.status = 'delivered'
        ) AS cancelled_but_delivered;
    ```
