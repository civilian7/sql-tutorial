# aggregate function

!!! info "Tables"
    `products` — Products (name, price, stock, brand)  
    `customers` — Customers (grade, points, channel)  
    `orders` — Orders (status, amount, date)  
    `reviews` — Reviews (rating, content)  
    `payments` — Payments (method, amount, status)  

!!! abstract "Concepts"
    `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `ROUND`, `COUNT(DISTINCT)` + Previous lecture contents

!!! info "Before You Begin"
    This exercise uses only what you learned in **Introduction Lessons 1-4**.
    GROUP BY, HAVING, JOIN, and subqueries are not used.
    Aggregate functions return one result for **entire rows** filtered by WHERE.

---

## Basic (1~10)

Practice one aggregate function at a time.

---

### Problem 1

**Check the total number of products registered in the product table.**

??? tip "Hint"
    `COUNT(*)` counts the total number of rows in the table.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_products
    FROM products;
    ```

    **Result:**

    | total_products |
    | ----------: |
    | 280 |

---

### Problem 2

**Check the number of products on sale (`is_active = 1`).**

??? tip "Hint"
    If you set a condition with `WHERE` and count with `COUNT(*)`, only rows that meet the condition are counted.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS active_count
    FROM products
    WHERE is_active = 1;
    ```

    **Result:**

    | active_count |
    | ----------: |
    | 218 |

---

### Problem 3

**Check how many products have the discontinuation date (`discontinued_at`) recorded.**

??? tip "Hint"
    `COUNT(column_name)` counts only rows where the corresponding column is not NULL. Remember the difference from `COUNT(*)`.

??? success "Answer"
    ```sql
    SELECT COUNT(discontinued_at) AS discontinued_count
    FROM products;
    ```

    **Result:**

    | discontinued_count |
    | ----------: |
    | 62 |

    > `COUNT(*)` returns 280, but `COUNT(discontinued_at)` returns 62 excluding NULL.

---

### Problem 4

**Get the total inventory quantity for all products.**

??? tip "Hint"
    `SUM(column_name)` adds all values in that column.

??? success "Answer"
    ```sql
    SELECT SUM(stock_qty) AS total_stock
    FROM products;
    ```

    **Result:**

    | total_stock |
    | ----------: |
    | 76887 |

---

### Problem 5

**Check the average price of all products.**

??? tip "Hint"
    `AVG(column_name)` calculates the average of that column.

??? success "Answer"
    ```sql
    SELECT AVG(price) AS avg_price
    FROM products;
    ```

    **Result:**

    | avg_price |
    | ----------: |
    | 649272.5 |

    > The decimal point appears long. Later you will learn how to organize it with `ROUND`.

---

### Problem 6

**Check the price of the most expensive product.**

??? tip "Hint"
    `MAX(column_name)` returns the maximum value of the column.

??? success "Answer"
    ```sql
    SELECT MAX(price) AS max_price
    FROM products;
    ```

    **Result:**

    | max_price |
    | ----------: |
    | 5481100.0 |

---

### Problem 7

**Check the price of the cheapest product.**

??? tip "Hint"
    `MIN(column_name)` returns the minimum value of the column.

??? success "Answer"
    ```sql
    SELECT MIN(price) AS min_price
    FROM products;
    ```

    **Result:**

    | min_price |
    | ----------: |
    | 18500.0 |

---

### Problem 8

**Find the total sales (`total_amount` sum) of all orders.**

??? tip "Hint"
    Applies `SUM` to the `total_amount` column of the `orders` table.

??? success "Answer"
    ```sql
    SELECT SUM(total_amount) AS total_revenue
    FROM orders;
    ```

    **Result:**

    | total_revenue |
    | ----------: |
    | 38183495063.0 |

    > It is approximately 35.5 billion won. Cumulative sales over 10 years.

---

### Problem 9

**Check the average rating of the reviews.**

??? tip "Hint"
    Applies `AVG` to the `rating` column of the `reviews` table.

??? success "Answer"
    ```sql
    SELECT AVG(rating) AS avg_rating
    FROM reviews;
    ```

    **Result:**

    | avg_rating |
    | ----------: |
    | 3.904984788205008 |

---

### Problem 10

**Check which customer has the most points.**

??? tip "Hint"
    Applies `MAX` to `point_balance` in table `customers`.

??? success "Answer"
    ```sql
    SELECT MAX(point_balance) AS max_points
    FROM customers;
    ```

    **Result:**

    | max_points |
    | ----------: |
    | 3955828 |

    > There is a customer who holds approximately 3.34 million points.

---

## Applied (11~20)

Use aggregates with ROUND, COUNT(DISTINCT), combinations of multiple aggregate functions, and WHERE filters.

---

### Problem 11

**View the average price of products on sale, rounded to two decimal places.**

??? tip "Hint"
    Specify the number of decimal places with `ROUND(value, digits)`. You can wrap an aggregate function like `ROUND(AVG(price), 2)`.

??? success "Answer"
    ```sql
    SELECT ROUND(AVG(price), 2) AS avg_price
    FROM products
    WHERE is_active = 1;
    ```

    **Result:**

    | avg_price |
    | ----------: |
    | 659594.5 |

---

### Problem 12

**Check how many brands are registered in the product table.**

??? tip "Hint"
    `COUNT(DISTINCT column_name)` counts the number of unique values with duplicates removed.

??? success "Answer"
    ```sql
    SELECT COUNT(DISTINCT brand) AS brand_count
    FROM products;
    ```

    **Result:**

    | brand_count |
    | ----------: |
    | 55 |

---

### Problem 13

**Check how many customers have placed an order.**

??? tip "Hint"
    Applying `COUNT(DISTINCT ...)` to `customer_id` in the `orders` table gives you the number of unique customers who placed an order.

??? success "Answer"
    ```sql
    SELECT COUNT(DISTINCT customer_id) AS ordering_customers
    FROM orders;
    ```

    **Result:**

    | ordering_customers |
    | ----------: |
    | 2839 |

    > Approximately 52% of the total 5,230 people have experience ordering.

---

### Problem 14

**View the lowest, highest, and average price of a product (without decimal points) at once.**

??? tip "Hint"
    You can list multiple aggregate functions in one `SELECT`, separated by commas.

??? success "Answer"
    ```sql
    SELECT MIN(price) AS min_price,
           MAX(price) AS max_price,
           ROUND(AVG(price), 0) AS avg_price
    FROM products;
    ```

    **Result:**

    | min_price | max_price | avg_price |
    | ----------: | ----------: | ----------: |
    | 18500.0 | 5481100.0 | 649273.0 |

---

### Problem 15

**Check how many 5-star reviews there are**

??? tip "Hint"
    Filter by `WHERE rating = 5` and then use `COUNT(*)`.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS five_star_count
    FROM reviews
    WHERE rating = 5;
    ```

    **Result:**

    | five_star_count |
    | ----------: |
    | 3433 |

    > Approximately 41% of the total 7,945 reviews are 5-star reviews.

---

### Problem 16

**View the average rating of the review to one decimal place, lowest rating, and highest rating at once.**

??? tip "Hint"
    List `ROUND(AVG(...), 1)`, `MIN(...)`, and `MAX(...)` in one SELECT.

??? success "Answer"
    ```sql
    SELECT ROUND(AVG(rating), 1) AS avg_rating,
           MIN(rating) AS min_rating,
           MAX(rating) AS max_rating
    FROM reviews;
    ```

    **Result:**

    | avg_rating | min_rating | max_rating |
    | ----------: | ----------: | ----------: |
    | 3.9 | 1 | 5 |

---

### Problem 17

**Check the number of payments made with card (`card`).**

??? tip "Hint"
    Filter by `method = 'card'` in table `payments`.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS card_count
    FROM payments
    WHERE method = 'card';
    ```

    **Result:**

    | card_count |
    | ----------: |
    | 16841 |

---

### Problem 18

**Check how many payment methods there are.**

??? tip "Hint"
    Applies `COUNT(DISTINCT ...)` to the `method` column of the `payments` table.

??? success "Answer"
    ```sql
    SELECT COUNT(DISTINCT method) AS method_count
    FROM payments;
    ```

    **Result:**

    | method_count |
    | ----------: |
    | 6 |

---

### Problem 19

**View the oldest and most recent order dates.**

??? tip "Hint"
    You can also use `MIN` and `MAX` in date/time strings. This is because comparing alphabetical order is the same as comparing date order.

??? success "Answer"
    ```sql
    SELECT MIN(ordered_at) AS first_order,
           MAX(ordered_at) AS last_order
    FROM orders;
    ```

    **Result:**

    | first_order | last_order |
    | ---------- | ---------- |
    | 2016-01-09 10:20:06 | 2025-12-31 22:25:39 |

    > Order data for approximately 9 years and 6 months exists.

---

### Problem 20

**Check how many orders (`discount_amount > 0`) have discounts applied to all orders.**

??? tip "Hint"
    Filter by `WHERE discount_amount > 0` and then use `COUNT(*)`.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS discounted_orders
    FROM orders
    WHERE discount_amount > 0;
    ```

    **Result:**

    | discounted_orders |
    | ----------: |
    | 7917 |

    > Discounts were applied to approximately 21% of the total 34,908 orders.

---

## Practical (21~30)

We cover complex conditions + aggregates, arithmetic operations + aggregates, and frequently used questions in practice.

---

### Problem 21

**Check the number of confirmed (`confirmed`) status orders, total sales, and average order amount. Amounts are rounded without decimal places.**

??? tip "Hint"
    Filter by `WHERE status = 'confirmed'`, then use `COUNT`, `SUM`, and `AVG` at once.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS order_count,
           ROUND(SUM(total_amount), 0) AS total_revenue,
           ROUND(AVG(total_amount), 0) AS avg_amount
    FROM orders
    WHERE status = 'confirmed';
    ```

    **Result:**

    | order_count | total_revenue | avg_amount |
    | ----------: | ----------: | ----------: |
    | 34393 | 34386590179.0 | 999814.0 |

---

### Problem 22

**Check at once how many customers have written reviews and how many types of products have reviews.**

??? tip "Hint"
    Use `COUNT(DISTINCT customer_id)` and `COUNT(DISTINCT product_id)` together in one SELECT.

??? success "Answer"
    ```sql
    SELECT COUNT(DISTINCT customer_id) AS reviewer_count,
           COUNT(DISTINCT product_id) AS reviewed_product_count
    FROM reviews;
    ```

    **Result:**

    | reviewer_count | reviewed_product_count |
    | ----------: | ----------: |
    | 1899 | 278 |

    > Out of 280 products, 256 (91%) had reviews.

---

### Problem 23

**View the customer's accumulated points and average (without decimal points).**

??? tip "Hint"
    Apply `SUM` and `ROUND(AVG(...), 0)` to `point_balance` in table `customers`.

??? success "Answer"
    ```sql
    SELECT SUM(point_balance) AS total_points,
           ROUND(AVG(point_balance), 0) AS avg_points
    FROM customers;
    ```

    **Result:**

    | total_points | avg_points |
    | ----------: | ----------: |
    | 337459019 | 64524.0 |

    > The total accumulated points of all customers is approximately 320 million points, with an average of approximately 60,000 points per person.

---

### Problem 24

**View the number of orders placed and total sales (without decimal points) in 2024.**

??? tip "Hint"
    Use the condition that `ordered_at` is greater than or equal to `'2024-01-01'` and less than `'2025-01-01'`. You can use `BETWEEN`, or you can combine `>=` and `<`.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS order_count,
           ROUND(SUM(total_amount), 0) AS revenue
    FROM orders
    WHERE ordered_at >= '2024-01-01'
      AND ordered_at < '2025-01-01';
    ```

    **Result:**

    | order_count | revenue |
    | ----------: | ----------: |
    | 5785 | 5622439762.0 |

    > Sales in 2024 are approximately 5.6 billion won.

---

### Problem 25

**Check the number of refund (`refunded`) status payments and the total refund amount.**

??? tip "Hint"
    Filter by `status = 'refunded'` in table `payments`.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS refund_count,
           ROUND(SUM(amount), 0) AS refund_total
    FROM payments
    WHERE status = 'refunded';
    ```

    **Result:**

    | refund_count | refund_total |
    | ----------: | ----------: |
    | 1930 | 2357145631.0 |

    > Approximately 2.25 billion won was refunded.

---

### Problem 26

**Find the total inventory value (cost x inventory quantity) of the products you are selling.**

??? tip "Hint"
    Arithmetic operations can be used inside `SUM`. Like `SUM(cost_price * stock_qty)`, the values ​​multiplied by columns are added together.

??? success "Answer"
    ```sql
    SELECT ROUND(SUM(cost_price * stock_qty), 0) AS inventory_value
    FROM products
    WHERE is_active = 1;
    ```

    **Result:**

    | inventory_value |
    | ----------: |
    | 30030260700.0 |

    > The total inventory cost of products being sold is approximately 30 billion won.

---

### Problem 27

**Find the net sales (order amount minus discount amount) for all orders.**

??? tip "Hint"
    Like `SUM(total_amount - discount_amount)`, you can subtract between columns within SUM.

??? success "Answer"
    ```sql
    SELECT ROUND(SUM(total_amount - discount_amount), 0) AS net_revenue
    FROM orders;
    ```

    **Result:**

    | net_revenue |
    | ----------: |
    | 37831403663.0 |

    > Total sales before discount of KRW 35.5 billion, excluding discount of approximately KRW 310 million, net sales are approximately KRW 35.2 billion.

---

### Problem 28

**Find the number of 1-star reviews and 5-star reviews, respectively.**

??? tip "Hint"
    It is not possible to split two groups in one query without an aggregate function, but it is possible using `COUNT` and `WHERE`. Since we haven't learned `SUM(CASE ...)` or `GROUP BY` yet, let's use the two `COUNT` + arithmetic expressions. `COUNT` only counts non-NULL values, so couldn't we use a trick to return NULL when the condition is false? In fact, for this problem you can run two queries side by side.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS one_star_count
    FROM reviews
    WHERE rating = 1;
    ```

    **Result:**

    | one_star_count |
    | ----------: |
    | 434 |

    ```sql
    SELECT COUNT(*) AS five_star_count
    FROM reviews
    WHERE rating = 5;
    ```

    **Result:**

    | five_star_count |
    | ----------: |
    | 3433 |

    > A score of 5 (3,221 cases) is approximately 8 times more than a score of 1 (395 cases). If you learn GROUP BY, you can get the number of cases by all ratings with one query.

---

### Problem 29

**Find the average margin rate (%) for products being sold. The margin rate is `(price - cost_price) * 100.0 / price`, rounded to one decimal place.**

??? tip "Hint"
    You can put an arithmetic expression in `AVG`. Calculate the average margin rate for each row with `AVG((price - cost_price) * 100.0 / price)`.

??? success "Answer"
    ```sql
    SELECT ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1;
    ```

    **Result:**

    | avg_margin_pct |
    | ----------: |
    | 23.9 |

    > The average margin for products being sold is approximately 23%.

---

### Problem 30

**View the total number of orders, total sales, average order amount, total discount amount, total shipping cost, and total points used in the order table at once. All amounts are rounded without decimal places.**

??? tip "Hint"
    Lists six aggregate functions in one `SELECT`. This is the true power of aggregate functions --- condensing tens of thousands of pieces of data into a single line summary.

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

    **Result:**

    | total_orders | total_revenue | avg_amount | total_discount | total_shipping | total_point_used |
    | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: |
    | 37557 | 38183495063.0 | 1016681.0 | 352091400.0 | 9198000.0 | 9303137 |

    > Approximately 35,000 cases over 10 years, sales of KRW 35.5 billion, average of approximately KRW 1.02 million per case, total discounts of KRW 310 million, delivery fee income of 8.87 million, and point usage of 8.82 million.
