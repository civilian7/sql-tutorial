# JOIN Master

**Tables:** `categories`, `customers`, `orders`, `order_items`, `products`, `reviews`, `shipping`, `staff`, `suppliers`, `tags`, `product_tags`

**Concepts:** INNER JOIN, LEFT JOIN, multi-table JOIN, GROUP BY, aggregate functions


---


### 1. Retrieve each product's name, price, and category name. Top 


Retrieve each product's name, price, and category name. Top 10 by price descending.


**Hint 1:** `INNER JOIN` `products` and `categories` on `category_id`, then `ORDER BY ... DESC LIMIT 10`.


??? success "Answer"
    ```sql
    SELECT p.name, p.price, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    ORDER BY p.price DESC
    LIMIT 10;
    ```


---


### 2. Retrieve the product name, category name, and supplier compa


Retrieve the product name, category name, and supplier company name together.


**Hint 1:** `INNER JOIN` both `categories` and `suppliers` from `products`.


??? success "Answer"
    ```sql
    SELECT
        p.name AS product,
        cat.name AS category,
        s.company_name AS supplier
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    ORDER BY p.name
    LIMIT 20;
    ```


---


### 3. Retrieve the name and price of products that have never rece


Retrieve the name and price of products that have never received a review.


**Hint 1:** After `LEFT JOIN reviews`, use `WHERE r.id IS NULL` to find unmatched rows.


??? success "Answer"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id
    WHERE r.id IS NULL
    ORDER BY p.price DESC;
    ```


---


### 4. Retrieve the name and signup date of customers who have neve


Retrieve the name and signup date of customers who have never placed an order.


**Hint 1:** `customers LEFT JOIN orders`, then `WHERE o.id IS NULL` to filter customers with no orders.


??? success "Answer"
    ```sql
    SELECT c.name, c.created_at
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    WHERE o.id IS NULL
    ORDER BY c.created_at;
    ```


---


### 5. Retrieve each customer's name, grade, order count, and total


Retrieve each customer's name, grade, order count, and total amount spent. Top 10 by total spent.


**Hint 1:** `customers JOIN orders`, then aggregate with `GROUP BY`. Use `COUNT` and `SUM` together.


??? success "Answer"
    ```sql
    SELECT
        c.name, c.grade,
        COUNT(o.id) AS order_count,
        ROUND(SUM(o.total_amount), 2) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```


---


### 6. Retrieve the order number, customer name, product name, quan


Retrieve the order number, customer name, product name, quantity, and unit price for the 5 most recent orders.


**Hint 1:** Connect 4 tables with `INNER JOIN`: `orders -> customers`, `orders -> order_items -> products`.


??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        c.name AS customer,
        p.name AS product,
        oi.quantity,
        oi.unit_price
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN products AS p ON oi.product_id = p.id
    ORDER BY o.ordered_at DESC
    LIMIT 5;
    ```


---


### 7. Find the total revenue and units sold per category. Exclude 


Find the total revenue and units sold per category. Exclude cancelled orders.


**Hint 1:** JOIN `order_items -> products -> categories` and exclude cancelled orders with `WHERE o.status NOT IN ('cancelled')`.


??? success "Answer"
    ```sql
    SELECT
        cat.name AS category,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
    FROM order_items AS oi
    INNER JOIN orders AS o ON oi.order_id = o.id
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY cat.name
    ORDER BY revenue DESC;
    ```


---


### 8. Find the name, average rating, and review count of products 


Find the name, average rating, and review count of products with 5 or more reviews.


**Hint 1:** `products JOIN reviews`, then aggregate with `GROUP BY` and filter with `HAVING COUNT(r.id) >= 5`.


??? success "Answer"
    ```sql
    SELECT
        p.name,
        ROUND(AVG(r.rating), 2) AS avg_rating,
        COUNT(r.id) AS review_count
    FROM products AS p
    INNER JOIN reviews AS r ON p.id = r.product_id
    GROUP BY p.id, p.name
    HAVING COUNT(r.id) >= 5
    ORDER BY avg_rating DESC
    LIMIT 15;
    ```


---


### 9. Find the average number of days from order to delivery for c


Find the average number of days from order to delivery for completed shipments.


**Hint 1:** Calculate the date difference with `JULIANDAY(delivered_at) - JULIANDAY(ordered_at)`. JOIN `shipping` with `orders`.


??? success "Answer"
    ```sql
    SELECT
        ROUND(AVG(JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at)), 1) AS avg_delivery_days
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE sh.status = 'delivered'
      AND sh.delivered_at IS NOT NULL;
    ```


---


### 10. Find the total shipments, delivered count, and delivery rate


Find the total shipments, delivered count, and delivery rate per carrier.


**Hint 1:** `GROUP BY carrier` with conditional aggregation using `CASE WHEN status = 'delivered'`. Delivery rate is `100.0 * delivered / total`.


??? success "Answer"
    ```sql
    SELECT
        carrier,
        COUNT(*) AS total,
        SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered,
        ROUND(100.0 * SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) / COUNT(*), 1) AS delivery_rate
    FROM shipping
    GROUP BY carrier
    ORDER BY total DESC;
    ```


---


### 11. Find the product count, average price, and highest price per


Find the product count, average price, and highest price per supplier.


**Hint 1:** `suppliers JOIN products`, then aggregate with `GROUP BY`. Use `COUNT`, `AVG`, and `MAX` functions.


??? success "Answer"
    ```sql
    SELECT
        s.company_name,
        COUNT(p.id) AS product_count,
        ROUND(AVG(p.price), 2) AS avg_price,
        ROUND(MAX(p.price), 2) AS max_price
    FROM suppliers AS s
    INNER JOIN products AS p ON s.id = p.supplier_id
    GROUP BY s.id, s.company_name
    ORDER BY product_count DESC;
    ```


---


### 12. Retrieve each customer's most recent order date and order am


Retrieve each customer's most recent order date and order amount. Sort by most recent order.


**Hint 1:** Use `MAX(o.ordered_at)` to get the most recent order date and aggregate per customer with `GROUP BY`.


??? success "Answer"
    ```sql
    SELECT
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order_date,
        o.total_amount AS last_order_amount
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY c.id, c.name, c.grade
    ORDER BY last_order_date DESC
    LIMIT 15;
    ```


---


### 13. Staff Hierarchy (Self-JOIN)


List all staff members with their manager names.
Top-level staff with no manager should show NULL for manager name.


**Hint 1:** Self LEFT JOIN on `staff` table. `staff AS s LEFT JOIN staff AS m ON s.manager_id = m.id`. If no manager, `m.name` is NULL.


??? success "Answer"
    ```sql
    SELECT
        s.id,
        s.name       AS staff_name,
        s.department,
        s.role,
        m.name       AS manager_name,
        m.department AS manager_department
    FROM staff AS s
    LEFT JOIN staff AS m ON s.manager_id = m.id
    ORDER BY s.department, s.name;
    ```


---


### 14. Product Successor Chain (Self-JOIN)


Find discontinued products and their successors.
Show discontinued product name, date, successor name, and successor price.


**Hint 1:** `products.successor_id` references `id` in the same table. `products AS p JOIN products AS succ ON p.successor_id = succ.id`. Filter `p.discontinued_at IS NOT NULL`.


??? success "Answer"
    ```sql
    SELECT
        p.name        AS discontinued_product,
        p.price       AS old_price,
        p.discontinued_at,
        succ.name     AS successor_product,
        succ.price    AS new_price,
        ROUND(succ.price - p.price, 0) AS price_diff
    FROM products AS p
    INNER JOIN products AS succ ON p.successor_id = succ.id
    WHERE p.discontinued_at IS NOT NULL
    ORDER BY p.discontinued_at DESC
    LIMIT 20;
    ```


---


### 15. Q&A Thread View (Self-JOIN)


Show Q&A pairs in one row: question content, customer name, answer content, staff name.


**Hint 1:** Questions: `parent_id IS NULL`. Answers: `parent_id` references question's `id`. Question (`q`) LEFT JOIN Answer (`a`) ON `a.parent_id = q.id`.


??? success "Answer"
    ```sql
    SELECT
        p.name        AS product_name,
        q.content     AS question,
        c.name        AS asked_by,
        q.created_at  AS asked_at,
        a.content     AS answer,
        s.name        AS answered_by,
        a.created_at  AS answered_at
    FROM product_qna AS q
    INNER JOIN products AS p ON q.product_id = p.id
    LEFT JOIN customers AS c ON q.customer_id = c.id
    LEFT JOIN product_qna AS a ON a.parent_id = q.id
    LEFT JOIN staff AS s ON a.staff_id = s.id
    WHERE q.parent_id IS NULL
    ORDER BY q.created_at DESC
    LIMIT 20;
    ```


---


### 16. Days with No Orders (CROSS JOIN)


Using the calendar table, find dates in 2024 with zero orders.


**Hint 1:** LEFT JOIN `calendar` with `orders` on date. Extract date from `ordered_at` with `SUBSTR(ordered_at, 1, 10)`. Filter `WHERE o.id IS NULL` for no-order days.


??? success "Answer"
    ```sql
    SELECT
        cal.date_key,
        cal.day_name,
        cal.is_weekend,
        cal.is_holiday,
        cal.holiday_name
    FROM calendar AS cal
    LEFT JOIN (
        SELECT DISTINCT SUBSTR(ordered_at, 1, 10) AS order_date
        FROM orders
    ) AS od ON cal.date_key = od.order_date
    WHERE cal.year = 2024
      AND od.order_date IS NULL
    ORDER BY cal.date_key;
    ```


---


### 17. Product Tag Search (M:N JOIN)


Find products with the "Gaming" tag.
Show product name, brand, price, and category.


**Hint 1:** JOIN `product_tags` -> `tags` to filter by tag name. JOIN `product_tags` -> `products` for product info. `tags.name = 'Gaming'`.


??? success "Answer"
    ```sql
    SELECT
        p.name   AS product_name,
        p.brand,
        p.price,
        cat.name AS category
    FROM product_tags AS pt
    INNER JOIN tags       AS t   ON pt.tag_id     = t.id
    INNER JOIN products   AS p   ON pt.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE t.name = 'Gaming'
      AND p.is_active = 1
    ORDER BY p.price DESC;
    ```


---
