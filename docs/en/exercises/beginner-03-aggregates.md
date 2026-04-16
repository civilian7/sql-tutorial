# Aggregate Functions

!!! info "Tables"

    `products` — Products (name, price, stock, brand)  

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  

    `reviews` — Reviews (rating, content)  

    `payments` — Payments (method, amount, status)  



!!! abstract "Concepts"

    `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `ROUND`, `COUNT DISTINCT`



### 1. Check the total number of products registered in the product


Check the total number of products registered in the product table.


**Hint 1:** COUNT(*) counts the total number of rows in the table


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_products
    FROM products;
    ```


    **Result** (1 rows)

    | total_products |
    |---|
    | 280 |


---


### 2. Check the number of products on sale (`is_active = 1`).


Check the number of products on sale (`is_active = 1`).


**Hint 1:** If you set a condition with WHERE and count with COUNT(*), only rows that meet the condition are counted


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS active_count
    FROM products
    WHERE is_active = 1;
    ```


    **Result** (1 rows)

    | active_count |
    |---|
    | 218 |


---


### 3. Check how many products have the discontinuation date (`disc


Check how many products have the discontinuation date (`discontinued_at`) recorded.


**Hint 1:** COUNT(column_name) counts only rows where the corresponding column is not NULL. Remember the difference from COUNT(*)


??? success "Answer"
    ```sql
    SELECT COUNT(discontinued_at) AS discontinued_count
    FROM products;
    ```


    **Result** (1 rows)

    | discontinued_count |
    |---|
    | 62 |


---


### 4. Get the total inventory quantity for all products.


Get the total inventory quantity for all products.


**Hint 1:** SUM(column_name) adds all values in that column


??? success "Answer"
    ```sql
    SELECT SUM(stock_qty) AS total_stock
    FROM products;
    ```


    **Result** (1 rows)

    | total_stock |
    |---|
    | 76,887 |


---


### 5. Check the average price of all products.


Check the average price of all products.


**Hint 1:** AVG(column_name) calculates the average of that column


??? success "Answer"
    ```sql
    SELECT AVG(price) AS avg_price
    FROM products;
    ```


    **Result** (1 rows)

    | avg_price |
    |---|
    | 649,272.50 |


---


### 6. Check the price of the most expensive product.


Check the price of the most expensive product.


**Hint 1:** MAX(column_name) returns the maximum value of the column


??? success "Answer"
    ```sql
    SELECT MAX(price) AS max_price
    FROM products;
    ```


    **Result** (1 rows)

    | max_price |
    |---|
    | 5,481,100.00 |


---


### 7. Check the price of the cheapest product.


Check the price of the cheapest product.


**Hint 1:** MIN(column_name) returns the minimum value of the column


??? success "Answer"
    ```sql
    SELECT MIN(price) AS min_price
    FROM products;
    ```


    **Result** (1 rows)

    | min_price |
    |---|
    | 18,500.00 |


---


### 8. Find the total sales (`total_amount` sum) of all orders.


Find the total sales (`total_amount` sum) of all orders.


**Hint 1:** Applies SUM to the total_amount column of the orders table


??? success "Answer"
    ```sql
    SELECT SUM(total_amount) AS total_revenue
    FROM orders;
    ```


    **Result** (1 rows)

    | total_revenue |
    |---|
    | 38,183,495,063.00 |


---


### 9. Check the average rating of the reviews.


Check the average rating of the reviews.


**Hint 1:** Applies AVG to the rating column of the reviews table


??? success "Answer"
    ```sql
    SELECT AVG(rating) AS avg_rating
    FROM reviews;
    ```


    **Result** (1 rows)

    | avg_rating |
    |---|
    | 3.90 |


---


### 10. Check which customer has the most points.


Check which customer has the most points.


**Hint 1:** Applies MAX to point_balance in table customers


??? success "Answer"
    ```sql
    SELECT MAX(point_balance) AS max_points
    FROM customers;
    ```


    **Result** (1 rows)

    | max_points |
    |---|
    | 3,955,828 |


---


### 11. View the average price of products on sale, rounded to two d


View the average price of products on sale, rounded to two decimal places.


**Hint 1:** Specify the number of decimal places with ROUND(value, digits). You can wrap an aggregate function like ROUND(AVG(price), 2)


??? success "Answer"
    ```sql
    SELECT ROUND(AVG(price), 2) AS avg_price
    FROM products
    WHERE is_active = 1;
    ```


    **Result** (1 rows)

    | avg_price |
    |---|
    | 659,594.50 |


---


### 12. Check how many brands are registered in the product table.


Check how many brands are registered in the product table.


**Hint 1:** COUNT(DISTINCT column_name) counts the number of unique values with duplicates removed


??? success "Answer"
    ```sql
    SELECT COUNT(DISTINCT brand) AS brand_count
    FROM products;
    ```


    **Result** (1 rows)

    | brand_count |
    |---|
    | 55 |


---


### 13. Check how many customers have placed an order.


Check how many customers have placed an order.


**Hint 1:** Applying COUNT(DISTINCT ...) to customer_id in the orders table gives you the number of unique customers who placed an order


??? success "Answer"
    ```sql
    SELECT COUNT(DISTINCT customer_id) AS ordering_customers
    FROM orders;
    ```


    **Result** (1 rows)

    | ordering_customers |
    |---|
    | 2839 |


---


### 14. View the lowest, highest, and average price of a product (wi


View the lowest, highest, and average price of a product (without decimal points) at once.


**Hint 1:** You can list multiple aggregate functions in one SELECT, separated by commas


??? success "Answer"
    ```sql
    SELECT MIN(price) AS min_price,
           MAX(price) AS max_price,
           ROUND(AVG(price), 0) AS avg_price
    FROM products;
    ```


    **Result** (1 rows)

    | min_price | max_price | avg_price |
    |---|---|---|
    | 18,500.00 | 5,481,100.00 | 649,273.00 |


---


### 15. Check how many 5-star reviews there are.


Check how many 5-star reviews there are.


**Hint 1:** Filter by WHERE rating = 5 and then use COUNT(*)


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS five_star_count
    FROM reviews
    WHERE rating = 5;
    ```


    **Result** (1 rows)

    | five_star_count |
    |---|
    | 3433 |


---


### 16. View the average rating of the review to one decimal place, 


View the average rating of the review to one decimal place, lowest rating, and highest rating at once.


**Hint 1:** List ROUND(AVG(...), 1), MIN(...), and MAX(...) in one SELECT


??? success "Answer"
    ```sql
    SELECT ROUND(AVG(rating), 1) AS avg_rating,
           MIN(rating) AS min_rating,
           MAX(rating) AS max_rating
    FROM reviews;
    ```


    **Result** (1 rows)

    | avg_rating | min_rating | max_rating |
    |---|---|---|
    | 3.90 | 1 | 5 |


---


### 17. Check the number of payments made with card (`card`).


Check the number of payments made with card (`card`).


**Hint 1:** Filter by method = 'card' in table payments


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS card_count
    FROM payments
    WHERE method = 'card';
    ```


    **Result** (1 rows)

    | card_count |
    |---|
    | 16,841 |


---


### 18. Check how many payment methods there are.


Check how many payment methods there are.


**Hint 1:** Applies COUNT(DISTINCT ...) to the method column of the payments table


??? success "Answer"
    ```sql
    SELECT COUNT(DISTINCT method) AS method_count
    FROM payments;
    ```


    **Result** (1 rows)

    | method_count |
    |---|
    | 6 |


---


### 19. View the oldest and most recent order dates.


View the oldest and most recent order dates.


**Hint 1:** You can also use MIN and MAX in date/time strings


??? success "Answer"
    ```sql
    SELECT MIN(ordered_at) AS first_order,
           MAX(ordered_at) AS last_order
    FROM orders;
    ```


    **Result** (1 rows)

    | first_order | last_order |
    |---|---|
    | 2016-01-09 10:20:06 | 2025-12-31 22:25:39 |


---


### 20. Check how many orders (`discount_amount > 0`) have discounts


Check how many orders (`discount_amount > 0`) have discounts applied to all orders.


**Hint 1:** Filter by WHERE discount_amount > 0 and then use COUNT(*)


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS discounted_orders
    FROM orders
    WHERE discount_amount > 0;
    ```


    **Result** (1 rows)

    | discounted_orders |
    |---|
    | 7917 |


---


### 21. Check the number of confirmed (`confirmed`) status orders, t


Check the number of confirmed (`confirmed`) status orders, total sales, and average order amount. Amounts are rounded without decimal places.


**Hint 1:** Filter by WHERE status = 'confirmed', then use COUNT, SUM, and AVG at once


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS order_count,
           ROUND(SUM(total_amount), 0) AS total_revenue,
           ROUND(AVG(total_amount), 0) AS avg_amount
    FROM orders
    WHERE status = 'confirmed';
    ```


    **Result** (1 rows)

    | order_count | total_revenue | avg_amount |
    |---|---|---|
    | 34,393 | 34,386,590,179.00 | 999,814.00 |


---


### 22. Check at once how many customers have written reviews and ho


Check at once how many customers have written reviews and how many types of products have reviews.


**Hint 1:** Use COUNT(DISTINCT customer_id) and COUNT(DISTINCT product_id) together in one SELECT


??? success "Answer"
    ```sql
    SELECT COUNT(DISTINCT customer_id) AS reviewer_count,
           COUNT(DISTINCT product_id) AS reviewed_product_count
    FROM reviews;
    ```


    **Result** (1 rows)

    | reviewer_count | reviewed_product_count |
    |---|---|
    | 1899 | 278 |


---


### 23. View the customer's accumulated points and average (without 


View the customer's accumulated points and average (without decimal points).


**Hint 1:** Apply SUM and ROUND(AVG(...), 0) to point_balance in table customers


??? success "Answer"
    ```sql
    SELECT SUM(point_balance) AS total_points,
           ROUND(AVG(point_balance), 0) AS avg_points
    FROM customers;
    ```


    **Result** (1 rows)

    | total_points | avg_points |
    |---|---|
    | 337,459,019 | 64,524.00 |


---


### 24. View the number of orders placed and total sales (without de


View the number of orders placed and total sales (without decimal points) in 2024.


**Hint 1:** Use the condition that ordered_at is greater than or equal to '2024-01-01' and less than '2025-01-01'


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS order_count,
           ROUND(SUM(total_amount), 0) AS revenue
    FROM orders
    WHERE ordered_at >= '2024-01-01'
      AND ordered_at < '2025-01-01';
    ```


    **Result** (1 rows)

    | order_count | revenue |
    |---|---|
    | 5785 | 5,622,439,762.00 |


---


### 25. Check the number of refund (`refunded`) status payments and 


Check the number of refund (`refunded`) status payments and the total refund amount.


**Hint 1:** Filter by status = 'refunded' in table payments


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS refund_count,
           ROUND(SUM(amount), 0) AS refund_total
    FROM payments
    WHERE status = 'refunded';
    ```


    **Result** (1 rows)

    | refund_count | refund_total |
    |---|---|
    | 1930 | 2,357,145,631.00 |


---


### 26. Find the total inventory value (cost x inventory quantity) o


Find the total inventory value (cost x inventory quantity) of the products you are selling.


**Hint 1:** Arithmetic operations can be used inside SUM. Like SUM(cost_price * stock_qty), the values multiplied by columns are added together


??? success "Answer"
    ```sql
    SELECT ROUND(SUM(cost_price * stock_qty), 0) AS inventory_value
    FROM products
    WHERE is_active = 1;
    ```


    **Result** (1 rows)

    | inventory_value |
    |---|
    | 30,030,260,700.00 |


---


### 27. Find the net sales (order amount minus discount amount) for 


Find the net sales (order amount minus discount amount) for all orders.


**Hint 1:** Like SUM(total_amount - discount_amount), you can subtract between columns within SUM


??? success "Answer"
    ```sql
    SELECT ROUND(SUM(total_amount - discount_amount), 0) AS net_revenue
    FROM orders;
    ```


    **Result** (1 rows)

    | net_revenue |
    |---|
    | 37,831,403,663.00 |


---


### 28. Find the number of 1-star reviews and 5-star reviews, respec


Find the number of 1-star reviews and 5-star reviews, respectively.


**Hint 1:** Since we haven't learned GROUP BY yet, you can run two queries side by side


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS one_star_count
    FROM reviews
    WHERE rating = 1;
    ```


    **Result** (1 rows)

    | one_star_count |
    |---|
    | 434 |


---


### 29. Find the average margin rate (%) for products being sold. Th


Find the average margin rate (%) for products being sold. The margin rate is `(price - cost_price) * 100.0 / price`, rounded to one decimal place.


**Hint 1:** You can put an arithmetic expression in AVG. Calculate the average margin rate for each row with AVG((price - cost_price) * 100.0 / price)


??? success "Answer"
    ```sql
    SELECT ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1;
    ```


    **Result** (1 rows)

    | avg_margin_pct |
    |---|
    | 23.90 |


---


### 30. View the total number of orders, total sales, average order 


View the total number of orders, total sales, average order amount, total discount amount, total shipping cost, and total points used in the order table at once. All amounts are rounded without decimal places.


**Hint 1:** Lists six aggregate functions in one SELECT


??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_orders,
           ROUND(SUM(total_amount), 0) AS total_revenue,
           ROUND(AVG(total_amount), 0) AS avg_amount,
           ROUND(SUM(discount_amount), 0) AS total_discount,
           ROUND(SUM(shipping_fee), 0) AS total_shipping,
           SUM(point_used) AS total_point_used
    FROM orders;
    ```


    **Result** (1 rows)

    | total_orders | total_revenue | avg_amount | total_discount | total_shipping | total_point_used |
    |---|---|---|---|---|---|
    | 37,557 | 38,183,495,063.00 | 1,016,681.00 | 352,091,400.00 | 9,198,000.00 | 9,303,137 |


---
