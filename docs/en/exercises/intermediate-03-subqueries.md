# Subqueries and Data Transformation

<div class="grid" markdown>

<div markdown>
#### :material-database: Tables

`categories` — Categories (parent-child hierarchy)<br>

`customers` — Customers (grade, points, channel)<br>

`orders` — Orders (status, amount, date)<br>

`order_items` — Order items (qty, unit price)<br>

`payments` — Payments (method, amount, status)<br>

`products` — Products (name, price, stock, brand)<br>

`reviews` — Reviews (rating, content)<br>

`returns` — Returns (reason, status)<br>

`wishlists` — Wishlists (customer-product)<br>

</div>

<div markdown>
#### :material-book-open-variant: Concepts

`scalar subquery`

`correlated subquery`

`CTE`

`CASE WHEN`

`NOT EXISTS`

`UNION ALL`

`window functions`

</div>

</div>

---


### 1. Retrieve the name and price of products that are more expens


Retrieve the name and price of products that are more expensive than the overall average price.


**Hint 1:** Use a scalar subquery: `WHERE price > (SELECT AVG(price) FROM products)`.


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products)
    ORDER BY price DESC;
    ```


---


### 2. Find the name, category, total quantity sold, and total reve


Find the name, category, total quantity sold, and total revenue of the #1 best-selling product.


**Hint 1:** JOIN `order_items` with `products` and `categories`, then aggregate per product with `GROUP BY`. Use `ORDER BY total_sold DESC LIMIT 1`.


??? success "Answer"
    ```sql
    SELECT
        p.name,
        cat.name AS category,
        SUM(oi.quantity) AS total_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN orders AS o ON oi.order_id = o.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY p.id, p.name, cat.name
    ORDER BY total_sold DESC
    LIMIT 1;
    ```


---


### 3. Retrieve only the products that are more expensive than the 


Retrieve only the products that are more expensive than the average price of their category.


**Hint 1:** Calculate the category average price in a subquery (inline view), then `JOIN` it and filter with `WHERE p.price > cat_avg.avg_price`.


??? success "Answer"
    ```sql
    SELECT p.name, p.price, cat.name AS category, cat_avg.avg_price
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN (
        SELECT category_id, ROUND(AVG(price), 2) AS avg_price
        FROM products
        GROUP BY category_id
    ) AS cat_avg ON p.category_id = cat_avg.category_id
    WHERE p.price > cat_avg.avg_price
    ORDER BY p.price DESC
    LIMIT 20;
    ```


---


### 4. Find products with an average rating of 4.5 or higher but wh


Find products with an average rating of 4.5 or higher but whose total revenue is below the median (bottom 50%).


**Hint 1:** Calculate per-product average rating and revenue in a CTE, then filter by rating threshold and revenue below the overall average.


??? success "Answer"
    ```sql
    WITH product_stats AS (
        SELECT
            p.id,
            p.name,
            ROUND(AVG(r.rating), 2) AS avg_rating,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue
        FROM products AS p
        LEFT JOIN reviews AS r ON p.id = r.product_id
        LEFT JOIN order_items AS oi ON p.id = oi.product_id
        GROUP BY p.id, p.name
        HAVING COUNT(r.id) >= 3
    )
    SELECT name, avg_rating, ROUND(revenue, 2) AS revenue
    FROM product_stats
    WHERE avg_rating >= 4.5
      AND revenue < (SELECT AVG(revenue) FROM product_stats)
    ORDER BY avg_rating DESC;
    ```


---


### 5. Classify orders by amount into tiers -- small (under 50K), m


Classify orders by amount into tiers -- small (under 50K), medium (50K-200K), large (200K-500K), premium (500K+) -- and find the count and ratio for each tier.


**Hint 1:** Classify tiers with `CASE WHEN total_amount < 50000 THEN 'Small' ...`, then `GROUP BY`. Calculate the ratio using the window function `SUM(COUNT(*)) OVER ()`.


??? success "Answer"
    ```sql
    SELECT
        CASE
            WHEN total_amount < 50000 THEN '소액 (5만 미만)'
            WHEN total_amount < 200000 THEN '중액 (5~20만)'
            WHEN total_amount < 500000 THEN '대액 (20~50만)'
            ELSE '고액 (50만 이상)'
        END AS tier,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct,
        ROUND(AVG(total_amount), 2) AS avg_amount
    FROM orders
    WHERE status NOT IN ('cancelled')
    GROUP BY tier
    ORDER BY MIN(total_amount);
    ```


---


### 6. Find customer-product combinations that are in a wishlist bu


Find customer-product combinations that are in a wishlist but have never been ordered.


**Hint 1:** Use `NOT EXISTS` with a correlated subquery to check if the customer has ever ordered that product.


??? success "Answer"
    ```sql
    SELECT
        c.name AS customer,
        p.name AS product,
        w.created_at AS wishlisted_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products AS p ON w.product_id = p.id
    WHERE NOT EXISTS (
        SELECT 1
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.customer_id = w.customer_id
          AND oi.product_id = w.product_id
          AND o.status NOT IN ('cancelled')
    )
    ORDER BY w.created_at DESC
    LIMIT 20;
    ```


---


### 7. Find the count, average payment amount, and installment rati


Find the count, average payment amount, and installment ratio per card issuer.


**Hint 1:** Filter card payments with `WHERE method = 'card'`, then `GROUP BY card_issuer`. Calculate installment ratio with conditional aggregation using `CASE WHEN installment_months > 0`.


??? success "Answer"
    ```sql
    SELECT
        card_issuer,
        COUNT(*) AS tx_count,
        ROUND(AVG(amount), 2) AS avg_amount,
        ROUND(100.0 * SUM(CASE WHEN installment_months > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS installment_pct
    FROM payments
    WHERE method = 'card'
      AND card_issuer IS NOT NULL
    GROUP BY card_issuer
    ORDER BY tx_count DESC;
    ```


---


### 8. Find the count, resolution rate, and average processing time


Find the count, resolution rate, and average processing time per customer inquiry channel.


**Hint 1:** Aggregate with `GROUP BY channel`. Calculate resolution rate with `CASE WHEN status IN ('resolved','closed')` conditional counting. Processing time uses `JULIANDAY` difference.


??? success "Answer"
    ```sql
    SELECT
        channel,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN status IN ('resolved', 'closed') THEN 1 ELSE 0 END) / COUNT(*), 1) AS resolution_pct,
        ROUND(AVG(CASE
            WHEN resolved_at IS NOT NULL
            THEN JULIANDAY(resolved_at) - JULIANDAY(created_at)
        END), 1) AS avg_days
    FROM complaints
    GROUP BY channel
    ORDER BY total DESC;
    ```


---


### 9. Find the name, review count, and wishlist count of customers


Find the name, review count, and wishlist count of customers who have both written reviews and added items to their wishlist.


**Hint 1:** Aggregate reviews and wishlists in separate subqueries, then `INNER JOIN` them together (only customers present in both).


??? success "Answer"
    ```sql
    SELECT
        c.name,
        r_cnt.review_count,
        w_cnt.wishlist_count
    FROM customers AS c
    INNER JOIN (
        SELECT customer_id, COUNT(*) AS review_count
        FROM reviews GROUP BY customer_id
    ) AS r_cnt ON c.id = r_cnt.customer_id
    INNER JOIN (
        SELECT customer_id, COUNT(*) AS wishlist_count
        FROM wishlists GROUP BY customer_id
    ) AS w_cnt ON c.id = w_cnt.customer_id
    ORDER BY r_cnt.review_count DESC
    LIMIT 15;
    ```


---


### 10. Find the image count per product, including products with no


Find the image count per product, including products with no images.


**Hint 1:** `products LEFT JOIN product_images` to include products without images. `COUNT(pi.id)` doesn't count NULLs, so it returns 0.


??? success "Answer"
    ```sql
    SELECT
        p.name,
        COUNT(pi.id) AS image_count,
        SUM(CASE WHEN pi.is_primary = 1 THEN 1 ELSE 0 END) AS has_primary
    FROM products AS p
    LEFT JOIN product_images AS pi ON p.id = pi.product_id
    GROUP BY p.id, p.name
    ORDER BY image_count ASC
    LIMIT 20;
    ```


---


### 11. Find the count and percentage per cart status (active/conver


Find the count and percentage per cart status (active/converted/abandoned).


**Hint 1:** Aggregate with `GROUP BY status`. Calculate the ratio with `100.0 * COUNT(*) / SUM(COUNT(*)) OVER ()`.


??? success "Answer"
    ```sql
    SELECT
        status,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM carts
    GROUP BY status
    ORDER BY cnt DESC;
    ```


---


### 12. Combine order cancellation events and return request events 


Combine order cancellation events and return request events into a single timeline. Show the 20 most recent.


**Hint 1:** Combine two SELECTs with `UNION ALL`, matching the number and meaning of columns. Add an event type column to distinguish them.


??? success "Answer"
    ```sql
    SELECT '취소' AS event_type, order_number AS reference, cancelled_at AS event_date
    FROM orders
    WHERE status = 'cancelled' AND cancelled_at IS NOT NULL
    UNION ALL
    SELECT '반품' AS event_type, CAST(order_id AS TEXT), requested_at
    FROM returns
    WHERE requested_at IS NOT NULL
    ORDER BY event_date DESC
    LIMIT 20;
    ```


---
