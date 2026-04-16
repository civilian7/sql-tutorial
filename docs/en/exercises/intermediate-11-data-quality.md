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

    `NULL check`, `duplicate check`, `range check`, `referential integrity`, `date inversion`, `outlier detection`, `quality dashboard`



### 1. Calculate the NULL ratio for birth_date, gender, and last_lo


Calculate the NULL ratio for birth_date, gender, and last_login_at in the customers table.


**Hint 1:** Use `SUM(CASE WHEN column IS NULL THEN 1 ELSE 0 END)` for NULL count.


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


    **Result** (1 rows)

    | total | null_birth | pct_birth | null_gender | pct_gender | null_login | pct_login |
    |---|---|---|---|---|---|---|
    | 5230 | 738 | 14.10 | 529 | 10.10 | 281 | 5.40 |


---


### 2. Check if there are customers with duplicate emails. Output d


Check if there are customers with duplicate emails. Output duplicate emails and counts.


**Hint 1:** Group by email then HAVING COUNT(*) > 1 to detect duplicates.


??? success "Answer"
    ```sql
    SELECT email, COUNT(*) AS cnt
    FROM customers
    GROUP BY email
    HAVING COUNT(*) > 1
    ORDER BY cnt DESC;
    ```


---


### 3. Find products with abnormal prices. Price at or below 0, or 


Find products with abnormal prices. Price at or below 0, or priced below cost (negative margin).


**Hint 1:** Use `WHERE price <= 0 OR price < cost_price` to detect abnormal pricing.


??? success "Answer"
    ```sql
    SELECT name, sku, price, cost_price, ROUND(price - cost_price, 0) AS margin
    FROM products
    WHERE price <= 0 OR price < cost_price
    ORDER BY margin ASC;
    ```


    **Result** (top 7 of 15 rows)

    | name | sku | price | cost_price | margin |
    |---|---|---|---|---|
    | SAPPHIRE NITRO+ RX 7900 XTX Black | GP-AMD-SAP-00088 | 867,300.00 | 1,049,800.00 | -182,500.00 |
    | Razer Blade 18 Black | LA-GAM-RAZ-00001 | 2,987,500.00 | 3,086,700.00 | -99,200.00 |
    | Razer Blade 18 | LA-GAM-RAZ-00180 | 1,806,800.00 | 1,901,300.00 | -94,500.00 |
    | Lenovo IdeaPad Flex 5 | LA-2IN-ETC-00062 | 1,550,800.00 | 1,641,300.00 | -90,500.00 |
    | LG Gram 14 | LA-GEN-LGE-00226 | 1,734,000.00 | 1,820,500.00 | -86,500.00 |
    | MSI Radeon RX 9070 VENTUS 3X White | GP-AMD-MSI-00006 | 383,100.00 | 431,800.00 | -48,700.00 |
    | be quiet! Pure Power 12 M 850W White | PS-BEQ-00023 | 185,100.00 | 231,500.00 | -46,400.00 |


---


### 4. Find orders with amount at or below 0 that are not cancelled


Find orders with amount at or below 0 that are not cancelled.


**Hint 1:** Orders with non-positive amounts that aren't cancelled may be data errors.


??? success "Answer"
    ```sql
    SELECT order_number, status, total_amount, ordered_at
    FROM orders
    WHERE total_amount <= 0
      AND status NOT IN ('cancelled', 'returned', 'return_requested')
    ORDER BY ordered_at DESC;
    ```


---


### 5. Check if any review ratings fall outside the allowed range (


Check if any review ratings fall outside the allowed range (1~5).


**Hint 1:** Check with `WHERE rating < 1 OR rating > 5`.


??? success "Answer"
    ```sql
    SELECT id, product_id, customer_id, rating
    FROM reviews
    WHERE rating < 1 OR rating > 5;
    ```


---


### 6. Find products with negative stock quantities.


Find products with negative stock quantities.


**Hint 1:** Check with `WHERE stock_qty < 0`.


??? success "Answer"
    ```sql
    SELECT name, sku, stock_qty, is_active
    FROM products
    WHERE stock_qty < 0
    ORDER BY stock_qty ASC;
    ```


---


### 7. Check if the same product is duplicated within the same orde


Check if the same product is duplicated within the same order.


**Hint 1:** GROUP BY order_id, product_id then HAVING COUNT(*) > 1 for duplicate combinations.


??? success "Answer"
    ```sql
    SELECT order_id, product_id, COUNT(*) AS cnt
    FROM order_items
    GROUP BY order_id, product_id
    HAVING COUNT(*) > 1
    ORDER BY cnt DESC;
    ```


---


### 8. Check for payment records with no corresponding order (orpha


Check for payment records with no corresponding order (orphan records).


**Hint 1:** Use payments LEFT JOIN orders, then find where orders.id IS NULL.


??? success "Answer"
    ```sql
    SELECT p.id AS payment_id, p.order_id, p.method, p.amount
    FROM payments AS p
    LEFT JOIN orders AS o ON p.order_id = o.id
    WHERE o.id IS NULL;
    ```


---


### 9. Check if any orders have an order date earlier than the cust


Check if any orders have an order date earlier than the customer's signup date. (Time inversion)


**Hint 1:** Join orders with customers, then find rows where ordered_at < created_at.


??? success "Answer"
    ```sql
    SELECT
        o.order_number, o.ordered_at, c.name,
        c.created_at AS signup_date,
        ROUND(JULIANDAY(c.created_at) - JULIANDAY(o.ordered_at), 1) AS days_diff
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.ordered_at < c.created_at
    ORDER BY days_diff DESC;
    ```


---


### 10. Find records where delivery date is earlier than shipment da


Find records where delivery date is earlier than shipment date.


**Hint 1:** Among rows where both dates are NOT NULL, find where delivered_at < shipped_at.


??? success "Answer"
    ```sql
    SELECT
        sh.id, o.order_number, sh.shipped_at, sh.delivered_at,
        ROUND(JULIANDAY(sh.delivered_at) - JULIANDAY(sh.shipped_at), 1) AS days_diff
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE sh.shipped_at IS NOT NULL AND sh.delivered_at IS NOT NULL
      AND sh.delivered_at < sh.shipped_at;
    ```


---


### 11. Find mismatches where shipping is delivered but order status


Find mismatches where shipping is delivered but order status hasn't progressed.


**Hint 1:** If shipping is delivered, order status should be one of delivered, confirmed, return_requested, or returned.


??? success "Answer"
    ```sql
    SELECT
        o.order_number, o.status AS order_status,
        sh.status AS ship_status, sh.delivered_at
    FROM orders AS o
    INNER JOIN shipping AS sh ON o.id = sh.order_id
    WHERE sh.status = 'delivered'
      AND o.status NOT IN ('delivered', 'confirmed', 'return_requested', 'returned');
    ```


---


### 12. Find contradictory data: cancelled orders with delivery comp


Find contradictory data: cancelled orders with delivery completion records.


**Hint 1:** Orders with cancelled status and delivered shipping are logically contradictory.


??? success "Answer"
    ```sql
    SELECT
        o.order_number, o.status AS order_status, o.cancelled_at,
        sh.status AS ship_status, sh.delivered_at
    FROM orders AS o
    INNER JOIN shipping AS sh ON o.id = sh.order_id
    WHERE o.status = 'cancelled' AND sh.status = 'delivered';
    ```


---


### 13. Check if discontinued products have been ordered after disco


Check if discontinued products have been ordered after discontinuation. Most recent 20.


**Hint 1:** Compare product's discontinued_at with order's ordered_at.


??? success "Answer"
    ```sql
    SELECT
        p.name, p.discontinued_at, o.order_number, o.ordered_at
    FROM products AS p
    INNER JOIN order_items AS oi ON p.id = oi.product_id
    INNER JOIN orders AS o ON oi.order_id = o.id
    WHERE p.discontinued_at IS NOT NULL AND o.ordered_at > p.discontinued_at
    ORDER BY o.ordered_at DESC
    LIMIT 20;
    ```


---


### 14. Find products where current price doesn't match the active p


Find products where current price doesn't match the active price in the history table.


**Hint 1:** Rows in product_prices where ended_at IS NULL represent the currently active price.


??? success "Answer"
    ```sql
    SELECT
        p.name, p.price AS current_price, pp.price AS history_price,
        ROUND(p.price - pp.price, 0) AS diff
    FROM products AS p
    INNER JOIN product_prices AS pp ON p.id = pp.product_id
    WHERE pp.ended_at IS NULL AND p.price <> pp.price
    ORDER BY ABS(p.price - pp.price) DESC;
    ```


---


### 15. Find orders where payment amount doesn't match order amount.


Find orders where payment amount doesn't match order amount. Top 20.


**Hint 1:** Compute per-order payment totals via subquery, then compare with orders.total_amount.


??? success "Answer"
    ```sql
    SELECT
        o.order_number, o.total_amount AS order_amount,
        pay_sum.paid_total,
        ROUND(o.total_amount - pay_sum.paid_total, 2) AS diff
    FROM orders AS o
    INNER JOIN (
        SELECT order_id, SUM(amount) AS paid_total
        FROM payments WHERE status = 'completed'
        GROUP BY order_id
    ) AS pay_sum ON o.id = pay_sum.order_id
    WHERE ABS(o.total_amount - pay_sum.paid_total) > 1
    ORDER BY ABS(diff) DESC
    LIMIT 20;
    ```


---


### 16. Find customers with 2 or more default shipping addresses.


Find customers with 2 or more default shipping addresses.


**Hint 1:** Count is_default = 1 rows per customer, find those with more than 1.


??? success "Answer"
    ```sql
    SELECT c.name, c.email, COUNT(*) AS default_count
    FROM customers AS c
    INNER JOIN customer_addresses AS ca ON c.id = ca.customer_id
    WHERE ca.is_default = 1
    GROUP BY c.id, c.name, c.email
    HAVING COUNT(*) > 1;
    ```


---


### 17. Check if any coupon usage exceeds the per_user_limit.


Check if any coupon usage exceeds the per_user_limit.


**Hint 1:** Group coupon_usage by coupon_id, customer_id, count usage, then compare with per_user_limit.


??? success "Answer"
    ```sql
    SELECT
        cp.code AS coupon_code, cp.name AS coupon_name,
        c.name AS customer_name,
        COUNT(*) AS usage_count, cp.per_user_limit
    FROM coupon_usage AS cu
    INNER JOIN coupons AS cp ON cu.coupon_id = cp.id
    INNER JOIN customers AS c ON cu.customer_id = c.id
    GROUP BY cu.coupon_id, cu.customer_id, cp.code, cp.name, c.name, cp.per_user_limit
    HAVING COUNT(*) > cp.per_user_limit
    ORDER BY usage_count DESC;
    ```


---


### 18. Find orders where total refund exceeds the original order am


Find orders where total refund exceeds the original order amount.


**Hint 1:** Compute per-order refund totals and compare with orders.total_amount.


??? success "Answer"
    ```sql
    SELECT
        o.order_number, o.total_amount AS order_amount,
        SUM(ret.refund_amount) AS total_refund,
        ROUND(SUM(ret.refund_amount) - o.total_amount, 2) AS over_refund
    FROM returns AS ret
    INNER JOIN orders AS o ON ret.order_id = o.id
    GROUP BY ret.order_id, o.order_number, o.total_amount
    HAVING SUM(ret.refund_amount) > o.total_amount
    ORDER BY over_refund DESC;
    ```


    **Result** (top 7 of 69 rows)

    | order_number | order_amount | total_refund | over_refund |
    |---|---|---|---|
    | ORD-20211201-14549 | 1,339,931.00 | 1,344,800.00 | 4,869.00 |
    | ORD-20250612-33985 | 1,145,546.00 | 1,150,400.00 | 4,854.00 |
    | ORD-20191218-04896 | 1,485,673.00 | 1,490,500.00 | 4,827.00 |
    | ORD-20160925-00299 | 1,124,799.00 | 1,129,400.00 | 4,601.00 |
    | ORD-20251102-36300 | 253,362.00 | 257,900.00 | 4,538.00 |
    | ORD-20241019-29928 | 2,368,896.00 | 2,373,400.00 | 4,504.00 |
    | ORD-20200101-05044 | 126,002.00 | 130,500.00 | 4,498.00 |


---


### 19. Calculate data completeness score for customers, products, a


Calculate data completeness score for customers, products, and orders. Combine with UNION ALL.


**Hint 1:** Calculate non-NULL ratio for nullable columns, then average across columns.


??? success "Answer"
    ```sql
    SELECT '고객' AS table_name, COUNT(*) AS total_rows,
           ROUND(100.0 * (
               (1.0 - 1.0 * SUM(CASE WHEN birth_date IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN last_login_at IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN acquisition_channel IS NULL THEN 1 ELSE 0 END) / COUNT(*))
           ) / 4.0, 1) AS completeness_pct
    FROM customers
    UNION ALL
    SELECT '상품', COUNT(*),
           ROUND(100.0 * (
               (1.0 - 1.0 * SUM(CASE WHEN description IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN specs IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN weight_grams IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN model_number IS NULL THEN 1 ELSE 0 END) / COUNT(*))
           ) / 4.0, 1)
    FROM products
    UNION ALL
    SELECT '주문', COUNT(*),
           ROUND(100.0 * (
               (1.0 - 1.0 * SUM(CASE WHEN notes IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN completed_at IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN cancelled_at IS NULL THEN 1 ELSE 0 END) / COUNT(*))
             + (1.0 - 1.0 * SUM(CASE WHEN staff_id IS NULL THEN 1 ELSE 0 END) / COUNT(*))
           ) / 4.0, 1)
    FROM orders;
    ```


    **Result** (3 rows)

    | table_name | total_rows | completeness_pct |
    |---|---|---|
    | 고객 | 5230 | 92.60 |
    | 상품 | 281 | 83.60 |
    | 주문 | 37,557 | 32.90 |


---


### 20. Summarize key data quality indicators in a single query. Out


Summarize key data quality indicators in a single query. Output signup inversion, orphan payments, date inversions, duplicate items, negative stock, and cancelled-but-delivered counts in one row.


**Hint 1:** Create each quality check as a scalar subquery and list them all in a single SELECT.


??? success "Answer"
    ```sql
    SELECT
        (SELECT COUNT(*) FROM orders AS o INNER JOIN customers AS c ON o.customer_id = c.id WHERE o.ordered_at < c.created_at) AS orders_before_signup,
        (SELECT COUNT(*) FROM payments AS p LEFT JOIN orders AS o ON p.order_id = o.id WHERE o.id IS NULL) AS orphan_payments,
        (SELECT COUNT(*) FROM shipping WHERE shipped_at IS NOT NULL AND delivered_at IS NOT NULL AND delivered_at < shipped_at) AS date_inversions,
        (SELECT COUNT(*) FROM (SELECT order_id, product_id FROM order_items GROUP BY order_id, product_id HAVING COUNT(*) > 1)) AS duplicate_items,
        (SELECT COUNT(*) FROM products WHERE stock_qty < 0) AS negative_stock,
        (SELECT COUNT(*) FROM orders AS o INNER JOIN shipping AS sh ON o.id = sh.order_id WHERE o.status = 'cancelled' AND sh.status = 'delivered') AS cancelled_but_delivered;
    ```


    **Result** (1 rows)

    | orders_before_signup | orphan_payments | date_inversions | duplicate_items | negative_stock | cancelled_but_delivered |
    |---|---|---|---|---|---|
    | 0 | 0 | 0 | 0 | 0 | 0 |


---
