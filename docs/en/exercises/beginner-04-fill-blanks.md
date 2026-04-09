# Fill in the Blanks

The key parts of the query are replaced with ___. Fill in the correct SQL.

---


### 1. Retrieve only VIP grade customers.


Retrieve only VIP grade customers.

```sql
SELECT name, email, grade
FROM customers
WHERE ___
ORDER BY name;
```


**Hint 1:** The blank needs an equality condition comparing the grade column with the value 'VIP'


??? success "Answer"
    ```sql
    SELECT name, email, grade
    FROM customers
    WHERE grade = 'VIP'
    ORDER BY name;
    ```


---


### 2. Sort products by price in descending order.


Sort products by price in descending order.

```sql
SELECT name, price
FROM products
ORDER BY ___
LIMIT 10;
```


**Hint 1:** The blank needs the sort column and the descending keyword (DESC)


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 10;
    ```


---


### 3. Count the number of products per category.


Count the number of products per category.

```sql
SELECT category_id, ___ AS product_count
FROM products
GROUP BY category_id;
```


**Hint 1:** The blank needs an aggregate function that counts rows


??? success "Answer"
    ```sql
    SELECT category_id, COUNT(*) AS product_count
    FROM products
    GROUP BY category_id;
    ```


---


### 4. Filter only customers with 10 or more orders.


Filter only customers with 10 or more orders.

```sql
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
___ ;
```


**Hint 1:** The blank needs a HAVING clause that filters grouped results. WHERE filters before grouping, HAVING filters after grouping


??? success "Answer"
    ```sql
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
    HAVING COUNT(*) >= 10;
    ```


---


### 5. Connect products with their categories.


Connect products with their categories.

```sql
SELECT p.name, cat.name AS category
FROM products AS p
INNER JOIN categories AS cat ON ___
LIMIT 10;
```


**Hint 1:** The blank needs the join condition linking the two tables. Match the foreign key in products with the primary key in categories


??? success "Answer"
    ```sql
    SELECT p.name, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LIMIT 10;
    ```


---


### 6. Find customers who have never placed an order.


Find customers who have never placed an order.

```sql
SELECT c.name, c.email
FROM customers AS c
LEFT JOIN orders AS o ON c.id = o.customer_id
WHERE ___ ;
```


**Hint 1:** After a LEFT JOIN, unmatched rows have NULL in the right table's columns. Use IS NULL to check


??? success "Answer"
    ```sql
    SELECT c.name, c.email
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    WHERE o.id IS NULL;
    ```


---


### 7. Retrieve orders from Q1 2024 (January through March).


Retrieve orders from Q1 2024 (January through March).

```sql
SELECT order_number, total_amount, ordered_at
FROM orders
WHERE ordered_at ___ ;
```


**Hint 1:** The blank needs BETWEEN 'start_date' AND 'end_date' to specify a date range


??? success "Answer"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE ordered_at BETWEEN '2024-01-01' AND '2024-03-31 23:59:59';
    ```


---


### 8. Classify inventory status.


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


**Hint 1:** List conditions for each range like WHEN stock_qty = 0 THEN 'Out of Stock'. End with ELSE for the default


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


### 9. Display 'N/A' when the birth date is missing.


Display 'N/A' when the birth date is missing.

```sql
SELECT
    name,
    ___ AS birth_date
FROM customers
LIMIT 10;
```


**Hint 1:** The COALESCE(column, default_value) function returns a substitute value when the column is NULL


??? success "Answer"
    ```sql
    SELECT
        name,
        COALESCE(birth_date, '미입력') AS birth_date
    FROM customers
    LIMIT 10;
    ```


---


### 10. Retrieve products more expensive than the average price.


Retrieve products more expensive than the average price.

```sql
SELECT name, price
FROM products
WHERE price > ___
ORDER BY price DESC;
```


**Hint 1:** The blank needs a subquery that calculates the average price: (SELECT AVG(price) FROM products)


??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products)
    ORDER BY price DESC;
    ```


---


### 11. Get the customer count, average points, and maximum points b


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


**Hint 1:** The three blanks need COUNT(*), ROUND(AVG(...), 0), and MAX(...) aggregate functions respectively


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


### 12. Find customers whose email is from the testmail.kr domain.


Find customers whose email is from the testmail.kr domain.

```sql
SELECT name, email
FROM customers
WHERE email LIKE ___
LIMIT 10;
```


**Hint 1:** In LIKE patterns, % represents any string. Create a pattern that ends with @testmail.kr


??? success "Answer"
    ```sql
    SELECT name, email
    FROM customers
    WHERE email LIKE '%@testmail.kr'
    LIMIT 10;
    ```


---


### 13. Extract the year and month from orders.


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


**Hint 1:** Use SUBSTR(ordered_at, start_position, length) to extract substrings. Year is positions 1-4, month is positions 6-2


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


### 14. Retrieve only payments with status completed or refunded.


Retrieve only payments with status completed or refunded.

```sql
SELECT id, order_id, method, amount, status
FROM payments
WHERE status ___ ;
```


**Hint 1:** Use the IN ('value1', 'value2') operator to check if a value matches one of several values


??? success "Answer"
    ```sql
    SELECT id, order_id, method, amount, status
    FROM payments
    WHERE status IN ('completed', 'refunded');
    ```


---


### 15. Retrieve the order number, customer name, payment amount, an


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


**Hint 1:** Each blank needs a foreign key relationship: o.customer_id = c.id, o.id = p.order_id, o.id = sh.order_id pattern


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


---
