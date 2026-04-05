# Beginner Exercise: Fill in the Blanks

The key parts of the query are replaced with `___`. Fill in the correct SQL.

---

### 1. WHERE Condition

Retrieve only VIP grade customers.

```sql
SELECT name, email, grade
FROM customers
WHERE ___
ORDER BY name;
```

??? success "Answer"
    ```sql
    SELECT name, email, grade
    FROM customers
    WHERE grade = 'VIP'
    ORDER BY name;
    ```

---

### 2. ORDER BY

Sort products by price in descending order.

```sql
SELECT name, price
FROM products
ORDER BY ___
LIMIT 10;
```

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 10;
    ```

---

### 3. Aggregate Function

Count the number of products per category.

```sql
SELECT category_id, ___ AS product_count
FROM products
GROUP BY category_id;
```

??? success "Answer"
    ```sql
    SELECT category_id, COUNT(*) AS product_count
    FROM products
    GROUP BY category_id;
    ```

---

### 4. HAVING

Filter only customers with 10 or more orders.

```sql
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
___ ;
```

??? success "Answer"
    ```sql
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    HAVING COUNT(*) >= 10;
    ```

---

### 5. JOIN Condition

Connect products with their categories.

```sql
SELECT p.name, cat.name AS category
FROM products AS p
INNER JOIN categories AS cat ON ___
LIMIT 10;
```

??? success "Answer"
    ```sql
    SELECT p.name, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LIMIT 10;
    ```

---

### 6. LEFT JOIN + IS NULL

Find customers who have never placed an order.

```sql
SELECT c.name, c.email
FROM customers AS c
LEFT JOIN orders AS o ON c.id = o.customer_id
WHERE ___ ;
```

??? success "Answer"
    ```sql
    SELECT c.name, c.email
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    WHERE o.id IS NULL;
    ```

---

### 7. BETWEEN

Retrieve orders from Q1 2024 (January through March).

```sql
SELECT order_number, total_amount, ordered_at
FROM orders
WHERE ordered_at ___ ;
```

??? success "Answer"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE ordered_at BETWEEN '2024-01-01' AND '2024-03-31 23:59:59';
    ```

---

### 8. CASE Expression

Classify inventory status.

```sql
SELECT
    name,
    stock_qty,
    CASE
        ___
    END AS stock_status
FROM products;
```

??? success "Answer"
    ```sql
    SELECT
        name,
        stock_qty,
        CASE
            WHEN stock_qty = 0 THEN '품절'
            WHEN stock_qty <= 10 THEN '부족'
            WHEN stock_qty <= 100 THEN '보통'
            ELSE '충분'
        END AS stock_status
    FROM products;
    ```

---

### 9. COALESCE

Display 'N/A' when the birth date is missing.

```sql
SELECT
    name,
    ___ AS birth_date
FROM customers
LIMIT 10;
```

??? success "Answer"
    ```sql
    SELECT
        name,
        COALESCE(birth_date, '미입력') AS birth_date
    FROM customers
    LIMIT 10;
    ```

---

### 10. Subquery

Retrieve products more expensive than the average price.

```sql
SELECT name, price
FROM products
WHERE price > ___
ORDER BY price DESC;
```

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products)
    ORDER BY price DESC;
    ```

---

### 11. GROUP BY + Multiple Aggregates

Get the customer count, average points, and maximum points by grade.

```sql
SELECT
    grade,
    ___ AS customer_count,
    ___ AS avg_points,
    ___ AS max_points
FROM customers
GROUP BY grade;
```

??? success "Answer"
    ```sql
    SELECT
        grade,
        COUNT(*) AS customer_count,
        ROUND(AVG(point_balance), 0) AS avg_points,
        MAX(point_balance) AS max_points
    FROM customers
    GROUP BY grade;
    ```

---

### 12. LIKE Pattern

Find customers whose email is from the testmail.kr domain.

```sql
SELECT name, email
FROM customers
WHERE email LIKE ___
LIMIT 10;
```

??? success "Answer"
    ```sql
    SELECT name, email
    FROM customers
    WHERE email LIKE '%@testmail.kr'
    LIMIT 10;
    ```

---

### 13. Date Extraction

Extract the year and month from orders.

```sql
SELECT
    ___ AS year,
    ___ AS month,
    COUNT(*) AS order_count
FROM orders
GROUP BY year, month
ORDER BY year, month;
```

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(ordered_at, 1, 4) AS year,
        SUBSTR(ordered_at, 6, 2) AS month,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY year, month
    ORDER BY year, month;
    ```

---

### 14. IN Operator

Retrieve only payments with status completed or refunded.

```sql
SELECT id, order_id, method, amount, status
FROM payments
WHERE status ___ ;
```

??? success "Answer"
    ```sql
    SELECT id, order_id, method, amount, status
    FROM payments
    WHERE status IN ('completed', 'refunded');
    ```

---

### 15. Multi-Table JOIN

Retrieve the order number, customer name, payment amount, and shipping status in one query.

```sql
SELECT
    o.order_number,
    c.name AS customer,
    p.amount AS paid,
    sh.status AS shipping_status
FROM orders AS o
INNER JOIN customers AS c ON ___
INNER JOIN payments AS p ON ___
LEFT JOIN shipping AS sh ON ___
ORDER BY o.ordered_at DESC
LIMIT 5;
```

??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        c.name AS customer,
        p.amount AS paid,
        sh.status AS shipping_status
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    INNER JOIN payments AS p ON o.id = p.order_id
    LEFT JOIN shipping AS sh ON o.id = sh.order_id
    ORDER BY o.ordered_at DESC
    LIMIT 5;
    ```
