# Mastering Subqueries

!!! info "Tables"
    `products` — Products (name, price, stock, brand)  
    `customers` — Customers (grade, points, channel)  
    `orders` — Orders (status, amount, date)  
    `order_items` — Order items (qty, unit price)  
    `reviews` — Reviews (rating, content)  
    `wishlists` — Wishlists (customer-product)  
    `categories` — Categories (parent-child hierarchy)  
    `payments` — Payments (method, amount, status)  

!!! abstract "Concepts"
    Scalar subqueries, `IN`/`NOT IN`, `EXISTS`/`NOT EXISTS`, FROM clause subqueries (inline views), Correlated subqueries

---


## Basic (1-7): WHERE Subqueries, IN/NOT IN

### Problem 1. Find products whose name and price are higher than the overall average price.

Use a scalar subquery to select only products more expensive than the average price of all products. Sort by price descending, top 10.

??? tip "Hint"
    Use a scalar subquery in the form `WHERE price > (SELECT AVG(price) FROM products)`.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products)
    ORDER BY price DESC
    LIMIT 10;
    ```

    | name | price |
    |------|-------|
    | (product above average 1) | 2500000 |
    | ... | ... |


---


### Problem 2. Find the name, price, and category ID of the most expensive product.

Use a subquery to find the maximum price, then find the product matching that price.

??? tip "Hint"
    Use the form `WHERE price = (SELECT MAX(price) FROM products)` to get the maximum value via subquery.

??? success "Answer"
    ```sql
    SELECT name, price, category_id
    FROM products
    WHERE price = (SELECT MAX(price) FROM products);
    ```


---


### Problem 3. Find the name and email of customers who have placed at least one order.

Use an IN subquery to find only customers whose customer_id exists in the orders table. Sort by name, top 15.

??? tip "Hint"
    `WHERE id IN (SELECT customer_id FROM orders)` — the subquery returns the list of customer IDs that have orders.

??? success "Answer"
    ```sql
    SELECT name, email
    FROM customers
    WHERE id IN (SELECT customer_id FROM orders)
    ORDER BY name
    LIMIT 15;
    ```


---


### Problem 4. Find the name and grade of customers who have never written a review.

Use a NOT IN subquery. Sort by grade descending (VIP, GOLD, SILVER, BRONZE), then by name, top 15.

??? tip "Hint"
    `WHERE id NOT IN (SELECT customer_id FROM reviews)` — finds customers not in the reviews table.

??? success "Answer"
    ```sql
    SELECT name, grade
    FROM customers
    WHERE id NOT IN (SELECT customer_id FROM reviews)
    ORDER BY
        CASE grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            ELSE 4
        END,
        name
    LIMIT 15;
    ```


---


### Problem 5. Find products that have been added to a wishlist at least once, showing name and price.

Use an IN subquery to find products whose product_id exists in the wishlists table. Sort by price descending, top 10.

??? tip "Hint"
    `WHERE id IN (SELECT product_id FROM wishlists)` — gets product IDs that have been wishlisted at least once.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE id IN (SELECT product_id FROM wishlists)
    ORDER BY price DESC
    LIMIT 10;
    ```


---


### Problem 6. Find products that have never been ordered, showing name and stock quantity.

Use a NOT IN subquery to find products that never appear in order_items.

??? tip "Hint"
    `WHERE id NOT IN (SELECT product_id FROM order_items)` — filters for products not in order details.

??? success "Answer"
    ```sql
    SELECT name, stock_qty
    FROM products
    WHERE id NOT IN (SELECT product_id FROM order_items)
    ORDER BY stock_qty DESC;
    ```


---


### Problem 7. Find orders with amounts greater than the average order amount. Exclude cancelled orders. Show order number, amount, and order date.

Use a scalar subquery to compute the average order amount, then filter for orders exceeding it. Sort by amount descending, top 10.

??? tip "Hint"
    Both the main query and the subquery should exclude cancelled orders for a fair comparison. Apply `status NOT IN ('cancelled')` to both.

??? success "Answer"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE status NOT IN ('cancelled')
      AND total_amount > (
          SELECT AVG(total_amount)
          FROM orders
          WHERE status NOT IN ('cancelled')
      )
    ORDER BY total_amount DESC
    LIMIT 10;
    ```


---


## Applied (8-14): FROM Subqueries, Correlated Subqueries, SELECT Scalars

### Problem 8. Find the average price per category, then find products more expensive than their category average.

Use a FROM clause subquery (inline view) to compute the average price per category first, then JOIN it with products. Top 15.

??? tip "Hint"
    `FROM products AS p INNER JOIN (SELECT category_id, AVG(price) AS avg_price FROM products GROUP BY category_id) AS ca ON ...` — JOIN the inline view like a table.

??? success "Answer"
    ```sql
    SELECT p.name, p.price, ca.avg_price
    FROM products AS p
    INNER JOIN (
        SELECT category_id, ROUND(AVG(price), 2) AS avg_price
        FROM products
        GROUP BY category_id
    ) AS ca ON p.category_id = ca.category_id
    WHERE p.price > ca.avg_price
    ORDER BY p.price DESC
    LIMIT 15;
    ```


---


### Problem 9. Use a SELECT clause scalar subquery to compute each customer's order count. Show only customers with 3 or more orders, sorted by order count descending, top 15.

Practice scalar subqueries that compute a value for each row in the SELECT clause.

??? tip "Hint"
    `SELECT name, (SELECT COUNT(*) FROM orders WHERE customer_id = c.id) AS order_count FROM customers AS c` — references the outer query's `c.id` in the subquery.

??? success "Answer"
    ```sql
    SELECT
        c.name,
        c.grade,
        (SELECT COUNT(*)
         FROM orders
         WHERE customer_id = c.id
           AND status NOT IN ('cancelled')) AS order_count
    FROM customers AS c
    WHERE (SELECT COUNT(*)
           FROM orders
           WHERE customer_id = c.id
             AND status NOT IN ('cancelled')) >= 3
    ORDER BY order_count DESC
    LIMIT 15;
    ```


---


### Problem 10. Use a correlated subquery to retrieve each product's most recent review date. Top 15.

A correlated subquery executes the subquery for each row of the outer query.

??? tip "Hint"
    `(SELECT MAX(created_at) FROM reviews WHERE product_id = p.id)` — a correlated subquery referencing the outer query's `p.id`.

??? success "Answer"
    ```sql
    SELECT
        p.name,
        p.price,
        (SELECT MAX(created_at)
         FROM reviews
         WHERE product_id = p.id) AS last_review_at
    FROM products AS p
    ORDER BY last_review_at DESC NULLS LAST
    LIMIT 15;
    ```


---


### Problem 11. Use a FROM subquery to compute total order amount per customer, then show the top 10.

Create a derived table in the FROM clause that aggregates orders, then JOIN with customers.

??? tip "Hint"
    `FROM (SELECT customer_id, SUM(total_amount) AS total_spent FROM orders WHERE ... GROUP BY customer_id) AS os` — use the derived table with an alias.

??? success "Answer"
    ```sql
    SELECT c.name, c.grade, os.total_spent
    FROM customers AS c
    INNER JOIN (
        SELECT customer_id, ROUND(SUM(total_amount), 2) AS total_spent
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ) AS os ON c.id = os.customer_id
    ORDER BY os.total_spent DESC
    LIMIT 10;
    ```


---


### Problem 12. Use EXISTS to find only products that have at least one review.

EXISTS checks whether the subquery returns any results. Compare with IN.

??? tip "Hint"
    `WHERE EXISTS (SELECT 1 FROM reviews WHERE product_id = p.id)` — returns TRUE if the subquery returns at least one row.

??? success "Answer"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    WHERE EXISTS (
        SELECT 1
        FROM reviews
        WHERE product_id = p.id
    )
    ORDER BY p.name
    LIMIT 15;
    ```


---


### Problem 13. Find customer-product combinations that were wishlisted but never ordered. Most recent 20.

Use a NOT EXISTS correlated subquery to check whether a customer has ordered that specific product.

??? tip "Hint"
    `WHERE NOT EXISTS (SELECT 1 FROM order_items AS oi INNER JOIN orders AS o ON ... WHERE o.customer_id = w.customer_id AND oi.product_id = w.product_id)` — a correlated subquery checking two conditions simultaneously.

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


### Problem 14. Find the most expensive product in each category, showing name and price.

Use a correlated subquery to compare each product's price with the maximum price in its category.

??? tip "Hint"
    `WHERE p.price = (SELECT MAX(price) FROM products WHERE category_id = p.category_id)` — computes the max price within the same category via correlated subquery.

??? success "Answer"
    ```sql
    SELECT p.name, p.price, p.category_id
    FROM products AS p
    WHERE p.price = (
        SELECT MAX(price)
        FROM products
        WHERE category_id = p.category_id
    )
    ORDER BY p.price DESC;
    ```


---


## Advanced (15-20): Nested Subqueries, Multi-level, Subquery vs JOIN Comparison

### Problem 15. Find products ordered by VIP customers that have an average rating of 4 or above.

Multi-level subquery: first get VIP customer IDs, then get product IDs from their orders, then filter by rating.

??? tip "Hint"
    `WHERE id IN (SELECT product_id FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE grade = 'VIP')))` — 3 levels of nesting. Note that such deep nesting hurts readability; in practice, JOINs or CTEs are recommended.

??? success "Answer"
    ```sql
    SELECT DISTINCT p.name, p.price
    FROM products AS p
    WHERE p.id IN (
        SELECT oi.product_id
        FROM order_items AS oi
        WHERE oi.order_id IN (
            SELECT o.id
            FROM orders AS o
            WHERE o.status NOT IN ('cancelled')
              AND o.customer_id IN (
                  SELECT id FROM customers WHERE grade = 'VIP'
              )
        )
    )
    AND p.id IN (
        SELECT product_id
        FROM reviews
        GROUP BY product_id
        HAVING AVG(rating) >= 4.0
    )
    ORDER BY p.price DESC
    LIMIT 15;
    ```


---


### Problem 16. Compare each customer's average order amount with the overall average, and find customers whose average is higher.

Use a FROM subquery to compute per-customer averages, then compare with the overall average scalar subquery in WHERE.

??? tip "Hint"
    Compute per-customer average order amount in a derived table, then filter with `WHERE avg_amount > (SELECT AVG(total_amount) FROM orders ...)`.

??? success "Answer"
    ```sql
    SELECT
        c.name,
        c.grade,
        ca.avg_amount,
        ca.order_count
    FROM customers AS c
    INNER JOIN (
        SELECT
            customer_id,
            ROUND(AVG(total_amount), 2) AS avg_amount,
            COUNT(*) AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ) AS ca ON c.id = ca.customer_id
    WHERE ca.avg_amount > (
        SELECT AVG(total_amount)
        FROM orders
        WHERE status NOT IN ('cancelled')
    )
    ORDER BY ca.avg_amount DESC
    LIMIT 15;
    ```


---


### Problem 17. Find products whose total sales quantity exceeds the average sales quantity across all products.

This uses a dual structure: aggregation inside a FROM subquery, and another subquery in WHERE.

??? tip "Hint"
    First compute total sales per product in a derived table. Then compare with `WHERE total_qty > (SELECT AVG(total_qty) FROM (...))`. SQLite allows nesting subqueries inside subqueries.

??? success "Answer"
    ```sql
    SELECT
        p.name,
        ps.total_qty
    FROM products AS p
    INNER JOIN (
        SELECT product_id, SUM(quantity) AS total_qty
        FROM order_items
        GROUP BY product_id
    ) AS ps ON p.id = ps.product_id
    WHERE ps.total_qty > (
        SELECT AVG(total_qty)
        FROM (
            SELECT SUM(quantity) AS total_qty
            FROM order_items
            GROUP BY product_id
        )
    )
    ORDER BY ps.total_qty DESC
    LIMIT 15;
    ```


---


### Problem 18. Find reviews whose rating is below the product's average rating. Most recent 15.

Use a correlated subquery in the WHERE clause to compare each review's rating with the product's average rating.

??? tip "Hint"
    `WHERE r.rating < (SELECT AVG(rating) FROM reviews WHERE product_id = r.product_id)` — computes the average rating for the same product via correlated subquery for each review.

??? success "Answer"
    ```sql
    SELECT
        r.id,
        p.name AS product,
        r.rating,
        ROUND((SELECT AVG(rating) FROM reviews WHERE product_id = r.product_id), 2) AS avg_rating,
        r.title,
        r.created_at
    FROM reviews AS r
    INNER JOIN products AS p ON r.product_id = p.id
    WHERE r.rating < (
        SELECT AVG(rating)
        FROM reviews
        WHERE product_id = r.product_id
    )
    ORDER BY r.created_at DESC
    LIMIT 15;
    ```


---


### Problem 19. Subquery vs JOIN comparison: Write the query "customers who have written a review" using two different approaches.

Write the same result using (A) IN subquery and (B) JOIN, and understand the differences.

??? tip "Hint"
    (A) `WHERE id IN (SELECT customer_id FROM reviews)`, (B) `INNER JOIN reviews ON ...` with DISTINCT. Both queries produce the same result but execute differently.

??? success "Answer"
    ```sql
    -- (A) IN subquery approach
    SELECT name, email
    FROM customers
    WHERE id IN (SELECT customer_id FROM reviews)
    ORDER BY name
    LIMIT 10;

    -- (B) JOIN approach (DISTINCT required)
    SELECT DISTINCT c.name, c.email
    FROM customers AS c
    INNER JOIN reviews AS r ON c.id = r.customer_id
    ORDER BY c.name
    LIMIT 10;
    ```

    Both queries return the same result. In general:

    - **IN subquery**: Deduplication is automatic, no DISTINCT needed. Efficient when the subquery result is small.
    - **JOIN**: Advantageous when you need additional columns (review content, etc.). May be better optimized for large datasets.


---


### Problem 20. Find customers who have purchased products from 3 or more categories, showing name and category count.

Use a FROM subquery to aggregate the number of purchase categories per customer, then filter for 3 or more.

??? tip "Hint"
    JOIN orders -> order_items -> products to compute the DISTINCT category_id count per customer. Create this aggregation as a derived table, then JOIN with customers.

??? success "Answer"
    ```sql
    SELECT c.name, c.grade, cc.cat_count
    FROM customers AS c
    INNER JOIN (
        SELECT
            o.customer_id,
            COUNT(DISTINCT p.category_id) AS cat_count
        FROM orders AS o
        INNER JOIN order_items AS oi ON o.id = oi.order_id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY o.customer_id
        HAVING COUNT(DISTINCT p.category_id) >= 3
    ) AS cc ON c.id = cc.customer_id
    ORDER BY cc.cat_count DESC, c.name
    LIMIT 15;
    ```


---
