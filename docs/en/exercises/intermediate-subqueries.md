# Intermediate Exercise: Subqueries and Data Transformation

12 problems practicing subqueries, CASE expressions, string functions, and set operations.

---

### 1. Products More Expensive Than Average

Retrieve the name and price of products that are more expensive than the overall average price.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products)
    ORDER BY price DESC;
    ```

---

### 2. Best-Selling Product Details

Find the name, category, total quantity sold, and total revenue of the #1 best-selling product.

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

### 3. Products Pricier Than Their Category Average

Retrieve only the products that are more expensive than the average price of their category.

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

### 4. High-Rated but Low-Revenue Products

Find products with an average rating of 4.5 or higher but whose total revenue is below the median (bottom 50%).

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

### 5. Order Amount Tier Classification

Classify orders by amount into tiers — small (under 50K), medium (50K–200K), large (200K–500K), premium (500K+) — and find the count and ratio for each tier.

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

### 6. Wishlisted but Never Purchased Products

Find customer-product combinations that are in a wishlist but have never been ordered.

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

### 7. Card Issuer Analysis

Find the count, average payment amount, and installment ratio per card issuer.

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

### 8. Resolution Rate by Inquiry Channel

Find the count, resolution rate, and average processing time per customer inquiry channel.

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

### 9. Customers Who Both Reviewed and Wishlisted

Find the name, review count, and wishlist count of customers who have both written reviews and added items to their wishlist.

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

### 10. Product Image Analysis

Find the image count per product, including products with no images.

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

### 11. Cart Conversion Rate

Find the count and percentage per cart status (active/converted/abandoned).

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

### 12. Combining Two Tables (UNION)

Combine order cancellation events and return request events into a single timeline. Show the 20 most recent.

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
