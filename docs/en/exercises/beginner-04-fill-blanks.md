# Fill in the Blanks

!!! info "Tables"

    `categories` — Categories (parent-child hierarchy)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `payments` — Payments (method, amount, status)  

    `products` — Products (name, price, stock, brand)  

    `shipping` — Shipping (carrier, tracking, status)  



!!! abstract "Concepts"

    `WHERE`, `ORDER BY`, `COUNT`, `HAVING`, `JOIN`, `LEFT JOIN`, `IS NULL`, `BETWEEN`, `CASE WHEN`, `COALESCE`, `subquery`, `GROUP BY`, `LIKE`, `SUBSTR`, `IN`



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


    **Result** (top 7 of 368 rows)

    | name | email | grade |
    |---|---|---|
    | Abigail Richardson | user4233@testmail.kr | VIP |
    | Adam Johnson | user2066@testmail.kr | VIP |
    | Adam Moore | user3@testmail.kr | VIP |
    | Adrienne Phillips | user2650@testmail.kr | VIP |
    | Aimee Norman | user3585@testmail.kr | VIP |
    | Alan Cruz | user1746@testmail.kr | VIP |
    | Alan Newman | user1516@testmail.kr | VIP |


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


    **Result** (top 7 of 10 rows)

    | name | price |
    |---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 |
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 |
    | Razer Blade 18 Black | 4,353,100.00 |
    | Razer Blade 16 Silver | 3,702,900.00 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 |


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


    **Result** (top 7 of 40 rows)

    | category_id | product_count |
    |---|---|
    | 2 | 5 |
    | 3 | 11 |
    | 4 | 2 |
    | 6 | 10 |
    | 7 | 9 |
    | 8 | 9 |
    | 9 | 1 |


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


    **Result** (top 7 of 953 rows)

    | customer_id | order_count |
    |---|---|
    | 2 | 77 |
    | 3 | 161 |
    | 4 | 95 |
    | 5 | 114 |
    | 8 | 38 |
    | 10 | 29 |
    | 12 | 41 |


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


    **Result** (top 7 of 10 rows)

    | name | category |
    |---|---|
    | Razer Blade 18 Black | Gaming Laptop |
    | MSI GeForce RTX 4070 Ti Super GAMING X | NVIDIA |
    | Samsung DDR4 32GB PC4-25600 | DDR4 |
    | Dell U2724D | General Monitor |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | DDR5 |
    | MSI Radeon RX 9070 VENTUS 3X White | AMD |
    | Samsung DDR5 32GB PC5-38400 | DDR5 |


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


    **Result** (top 7 of 2,391 rows)

    | name | email |
    |---|---|
    | Joshua Atkins | user1@testmail.kr |
    | Benjamin Skinner | user6@testmail.kr |
    | Ashley Jones | user7@testmail.kr |
    | Tracy Johnson | user9@testmail.kr |
    | David Wright | user11@testmail.kr |
    | Andrew Reeves | user13@testmail.kr |
    | Melinda Reed | user17@testmail.kr |


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


    **Result** (top 7 of 1,412 rows)

    | order_number | total_amount | ordered_at |
    |---|---|---|
    | ORD-20240101-25455 | 42,600.00 | 2024-01-01 02:48:53 |
    | ORD-20240101-25453 | 160,400.00 | 2024-01-01 03:38:36 |
    | ORD-20240101-25457 | 616,200.00 | 2024-01-01 06:57:33 |
    | ORD-20240101-25466 | 243,600.00 | 2024-01-01 07:55:46 |
    | ORD-20240101-25465 | 189,100.00 | 2024-01-01 09:35:17 |
    | ORD-20240101-25454 | 117,700.00 | 2024-01-01 10:48:07 |
    | ORD-20240101-25463 | 325,800.00 | 2024-01-01 12:01:21 |


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


    **Result** (top 7 of 280 rows)

    | name | stock_qty | stock_status |
    |---|---|---|
    | Razer Blade 18 Black | 107 | 충분 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 499 | 충분 |
    | Samsung DDR4 32GB PC4-25600 | 359 | 충분 |
    | Dell U2724D | 337 | 충분 |
    | G.SKILL Trident Z5 DDR5 64GB 6000MHz ... | 59 | 보통 |
    | MSI Radeon RX 9070 VENTUS 3X White | 460 | 충분 |
    | Samsung DDR5 32GB PC5-38400 | 340 | 충분 |


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


    **Result** (top 7 of 10 rows)

    | name | birth_date |
    |---|---|
    | Joshua Atkins | 1995-02-06 |
    | Danny Johnson | 1995-06-12 |
    | Adam Moore | 1998-05-02 |
    | Virginia Steele | 1994-12-02 |
    | Jared Vazquez | 1989-12-22 |
    | Benjamin Skinner | 1991-05-12 |
    | Ashley Jones | 미입력 |


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


    **Result** (top 7 of 83 rows)

    | name | price |
    |---|---|
    | MacBook Air 15 M3 Silver | 5,481,100.00 |
    | ASUS TUF Gaming RTX 5080 White | 4,526,600.00 |
    | ASUS Dual RTX 5070 Ti [Special Limite... | 4,496,700.00 |
    | Razer Blade 18 Black | 4,353,100.00 |
    | Razer Blade 16 Silver | 3,702,900.00 |
    | ASUS ROG Strix G16CH White | 3,671,500.00 |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 |


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


    **Result** (4 rows)

    | grade | customer_count | avg_points | max_points |
    |---|---|---|---|
    | BRONZE | 3859 | 16,779.00 | 956,983 |
    | GOLD | 524 | 147,711.00 | 2,007,717 |
    | SILVER | 479 | 95,042.00 | 1,266,757 |
    | VIP | 368 | 407,015.00 | 3,955,828 |


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


    **Result** (top 7 of 10 rows)

    | name | email |
    |---|---|
    | Joshua Atkins | user1@testmail.kr |
    | Danny Johnson | user2@testmail.kr |
    | Adam Moore | user3@testmail.kr |
    | Virginia Steele | user4@testmail.kr |
    | Jared Vazquez | user5@testmail.kr |
    | Benjamin Skinner | user6@testmail.kr |
    | Ashley Jones | user7@testmail.kr |


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


    **Result** (top 7 of 120 rows)

    | year | month | order_count |
    |---|---|---|
    | 2016 | 01 | 38 |
    | 2016 | 02 | 27 |
    | 2016 | 03 | 34 |
    | 2016 | 04 | 30 |
    | 2016 | 05 | 39 |
    | 2016 | 06 | 34 |
    | 2016 | 07 | 30 |


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


    **Result** (top 7 of 36,546 rows)

    | id | order_id | method | amount | status |
    |---|---|---|---|---|
    | 1 | 1 | card | 167,000.00 | completed |
    | 2 | 2 | card | 211,800.00 | completed |
    | 3 | 3 | card | 704,800.00 | completed |
    | 4 | 4 | card | 167,000.00 | completed |
    | 5 | 5 | kakao_pay | 534,490.00 | completed |
    | 6 | 6 | card | 167,000.00 | completed |
    | 7 | 7 | card | 687,400.00 | completed |


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


    **Result** (5 rows)

    | order_number | customer | paid | shipping_status |
    |---|---|---|---|
    | ORD-20251231-37555 | Angel Jones | 74,800.00 | NULL |
    | ORD-20251231-37543 | Carla Watson | 134,100.00 | NULL |
    | ORD-20251231-37552 | Martin Hanson | 254,300.00 | NULL |
    | ORD-20251231-37548 | Lucas Johnson | 187,700.00 | NULL |
    | ORD-20251231-37542 | Adam Moore | 155,700.00 | NULL |


---
