# Intermediate Exercise: JOIN Master

12 problems combining multiple tables. Practice INNER JOIN, LEFT JOIN, and multi-table JOINs.

---

### 1. Products and Categories

Retrieve each product's name, price, and category name. Top 10 by price descending.

**Hint:** `INNER JOIN` `products` and `categories` on `category_id`, then `ORDER BY ... DESC LIMIT 10`.

??? success "Answer"
    ```sql
    SELECT p.name, p.price, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    ORDER BY p.price DESC
    LIMIT 10;
    ```

---

### 2. Product + Category + Supplier

Retrieve the product name, category name, and supplier company name together.

**Hint:** `INNER JOIN` both `categories` and `suppliers` from `products`.

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

### 3. Products with No Reviews

Retrieve the name and price of products that have never received a review.

**Hint:** After `LEFT JOIN reviews`, use `WHERE r.id IS NULL` to find unmatched rows.

??? success "Answer"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id
    WHERE r.id IS NULL
    ORDER BY p.price DESC;
    ```

---

### 4. Customers Who Never Ordered

Retrieve the name and signup date of customers who have never placed an order.

**Hint:** `customers LEFT JOIN orders`, then `WHERE o.id IS NULL` to filter customers with no orders.

??? success "Answer"
    ```sql
    SELECT c.name, c.created_at
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    WHERE o.id IS NULL
    ORDER BY c.created_at;
    ```

---

### 5. Order Summary by Customer

Retrieve each customer's name, grade, order count, and total amount spent. Top 10 by total spent.

**Hint:** `customers JOIN orders`, then aggregate with `GROUP BY`. Use `COUNT` and `SUM` together.

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

### 6. Order Details (4-Table JOIN)

Retrieve the order number, customer name, product name, quantity, and unit price for the 5 most recent orders.

**Hint:** Connect 4 tables with `INNER JOIN`: `orders -> customers`, `orders -> order_items -> products`.

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

### 7. Revenue by Category

Find the total revenue and units sold per category. Exclude cancelled orders.

**Hint:** JOIN `order_items -> products -> categories` and exclude cancelled orders with `WHERE o.status NOT IN ('cancelled')`.

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

### 8. Average Rating by Product

Find the name, average rating, and review count of products with 5 or more reviews.

**Hint:** `products JOIN reviews`, then aggregate with `GROUP BY` and filter with `HAVING COUNT(r.id) >= 5`.

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

### 9. Average Delivery Days

Find the average number of days from order to delivery for completed shipments.

**Hint:** Calculate the date difference with `JULIANDAY(delivered_at) - JULIANDAY(ordered_at)`. JOIN `shipping` with `orders`.

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

### 10. Shipping Status by Carrier

Find the total shipments, delivered count, and delivery rate per carrier.

**Hint:** `GROUP BY carrier` with conditional aggregation using `CASE WHEN status = 'delivered'`. Delivery rate is `100.0 * delivered / total`.

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

### 11. Products and Average Price by Supplier

Find the product count, average price, and highest price per supplier.

**Hint:** `suppliers JOIN products`, then aggregate with `GROUP BY`. Use `COUNT`, `AVG`, and `MAX` functions.

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

### 12. Customer's Most Recent Order

Retrieve each customer's most recent order date and order amount. Sort by most recent order.

**Hint:** Use `MAX(o.ordered_at)` to get the most recent order date and aggregate per customer with `GROUP BY`.

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
