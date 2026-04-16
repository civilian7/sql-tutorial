# NULL Handling

!!! info "Tables"
    `customers` — Customers (grade, points, channel)  
    `orders` — Orders (status, amount, date)  
    `products` — Products (name, price, stock, brand)  

!!! abstract "Concepts"
    `IS NULL`, `IS NOT NULL`, `COALESCE`, `IFNULL`, NULL and aggregate functions, NULL sorting

## Basic (1~10)

Practice the basic usage of IS NULL, IS NOT NULL, and COALESCE.

---

### Problem 1

**Query the name and email of customers who do not have a date of birth (`birth_date`).**

??? tip "Hint"
    To find NULL values, you must use `IS NULL` instead of `= NULL`.

??? success "Answer"
    ```sql
    SELECT name, email
    FROM customers
    WHERE birth_date IS NULL;
    ```

---

### Problem 2

**Find the number of customers who have a gender (`gender`) value entered.**

??? tip "Hint"
    Filter only rows with values using `IS NOT NULL`, then count with `COUNT(*)`.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS gender_filled_count
    FROM customers
    WHERE gender IS NOT NULL;
    ```

---

### Problem 3

**Query the name, tier, and signup date of customers who have never logged in (`last_login_at` is NULL).**

??? tip "Hint"
    Use `last_login_at IS NULL` to find customers with no login history.

??? success "Answer"
    ```sql
    SELECT name, grade, created_at
    FROM customers
    WHERE last_login_at IS NULL;
    ```

---

### Problem 4

**Query the order number and delivery notes (`notes`) for orders that have delivery instructions. Show the 10 most recent orders.**

??? tip "Hint"
    Use `IS NOT NULL` to filter only orders where notes is not empty.

??? success "Answer"
    ```sql
    SELECT order_number, notes
    FROM orders
    WHERE notes IS NOT NULL
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```

---

### Problem 5

**Find the number of cancelled orders (where `cancelled_at` is not NULL).**

??? tip "Hint"
    If `cancelled_at IS NOT NULL`, it means the cancellation date was recorded, i.e., the order was cancelled.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS cancelled_count
    FROM orders
    WHERE cancelled_at IS NOT NULL;
    ```

---

### Problem 6

**Query the name and brand of products that have no specification information (`specs`).**

??? tip "Hint"
    Use `specs IS NULL` to find products with missing specification information.

??? success "Answer"
    ```sql
    SELECT name, brand
    FROM products
    WHERE specs IS NULL;
    ```

---

### Problem 7

**Query the name and gender of customers, displaying 'N/A' when gender is NULL.**

??? tip "Hint"
    `COALESCE(column, replacement)` returns the replacement value when the column is NULL.

??? success "Answer"
    ```sql
    SELECT name, COALESCE(gender, 'N/A') AS gender
    FROM customers;
    ```

---

### Problem 8

**Query the order number and delivery notes, displaying 'None' when notes are missing. Show only the 10 most recent orders.**

??? tip "Hint"
    Use `IFNULL(notes, 'None')` or `COALESCE(notes, 'None')`. Both work in SQLite.

??? success "Answer"
    ```sql
    SELECT order_number, IFNULL(notes, 'None') AS notes
    FROM orders
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```

---

### Problem 9

**Query the name, price, and discontinuation date of products that have a discontinuation date (`discontinued_at`).**

??? tip "Hint"
    If `discontinued_at IS NOT NULL`, the product has been discontinued.

??? success "Answer"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE discontinued_at IS NOT NULL;
    ```

---

### Problem 10

**Find the number of orders that have not been confirmed (`completed_at`) and have not been cancelled either.**

??? tip "Hint"
    Use `completed_at IS NULL AND cancelled_at IS NULL` to find rows where both columns are NULL.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS pending_count
    FROM orders
    WHERE completed_at IS NULL
      AND cancelled_at IS NULL;
    ```

---

## Applied (11~20)

Practice COALESCE usage, the relationship between NULL and aggregate functions, and NULL sorting.

---

### Problem 11

**Query the name, birth date, and gender of customers, displaying 'Unknown' for NULL birth dates and 'Not specified' for NULL genders. Show only the top 20 rows.**

??? tip "Hint"
    Apply `COALESCE` individually to each column.

??? success "Answer"
    ```sql
    SELECT name,
           COALESCE(birth_date, 'Unknown') AS birth_date,
           COALESCE(gender, 'Not specified') AS gender
    FROM customers
    LIMIT 20;
    ```

---

### Problem 12

**Query the name and weight of products, replacing NULL weight (`weight_grams`) with 0. Show the 10 heaviest products.**

??? tip "Hint"
    Replace NULL with 0 using `COALESCE(weight_grams, 0)`, then sort.

??? success "Answer"
    ```sql
    SELECT name, COALESCE(weight_grams, 0) AS weight_grams
    FROM products
    ORDER BY weight_grams DESC
    LIMIT 10;
    ```

---

### Problem 13

**Query the total number of customers and the number of customers with a birth date entered, in a single query.**

??? tip "Hint"
    `COUNT(*)` counts all rows, while `COUNT(column)` counts only rows where the column is not NULL.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_customers,
           COUNT(birth_date) AS has_birth_date
    FROM customers;
    ```

    > `COUNT(birth_date)` automatically excludes rows where birth_date is NULL.

---

### Problem 14

**Query the total number of orders, the number of orders with delivery notes, and the number of confirmed orders in a single query.**

??? tip "Hint"
    Applying `COUNT` to each column like `COUNT(notes)` and `COUNT(completed_at)` counts only non-NULL rows.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_orders,
           COUNT(notes) AS has_notes,
           COUNT(completed_at) AS completed
    FROM orders;
    ```

---

### Problem 15

**Sort customers by last login date in descending order, but place customers with no login history (NULL) at the end. Show only the top 20 rows.**

??? tip "Hint"
    In SQLite, using `ORDER BY column DESC` places NULLs at the end. Alternatively, use `ORDER BY column IS NULL, column DESC` for explicit control.

??? success "Answer"
    ```sql
    SELECT name, last_login_at
    FROM customers
    ORDER BY last_login_at IS NULL, last_login_at DESC
    LIMIT 20;
    ```

    > `last_login_at IS NULL` returns 1 for NULL and 0 otherwise. Since 0 sorts first, non-NULL rows appear at the top.

---

### Problem 16

**Sort products by discontinuation date in ascending order, but place non-discontinued products (NULL) at the end. Show only the top 10 rows.**

??? tip "Hint"
    Use `ORDER BY discontinued_at IS NULL, discontinued_at ASC` to push NULLs to the end.

??? success "Answer"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    ORDER BY discontinued_at IS NULL, discontinued_at ASC
    LIMIT 10;
    ```

---

### Problem 17

**Find the customer count and birth date completion rate (%) per tier. Round the rate to 1 decimal place.**

??? tip "Hint"
    Calculate the non-NULL ratio with `COUNT(birth_date) * 100.0 / COUNT(*)`. Aggregate by tier with `GROUP BY grade`.

??? success "Answer"
    ```sql
    SELECT grade,
           COUNT(*) AS total,
           COUNT(birth_date) AS has_birth,
           ROUND(COUNT(birth_date) * 100.0 / COUNT(*), 1) AS birth_rate_pct
    FROM customers
    GROUP BY grade
    ORDER BY birth_rate_pct DESC;
    ```

---

### Problem 18

**Find the customer count per signup channel (`acquisition_channel`), displaying 'Unclassified' for NULL values.**

??? tip "Hint"
    Use `COALESCE(acquisition_channel, 'Unclassified')` in both `SELECT` and `GROUP BY`.

??? success "Answer"
    ```sql
    SELECT COALESCE(acquisition_channel, 'Unclassified') AS channel,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY COALESCE(acquisition_channel, 'Unclassified')
    ORDER BY customer_count DESC;
    ```

---

### Problem 19

**Find the order count and delivery notes completion rate (%) per order status.**

??? tip "Hint"
    Calculate the non-NULL ratio of notes with `COUNT(notes) * 100.0 / COUNT(*)`.

??? success "Answer"
    ```sql
    SELECT status,
           COUNT(*) AS order_count,
           ROUND(COUNT(notes) * 100.0 / COUNT(*), 1) AS notes_rate_pct
    FROM orders
    GROUP BY status
    ORDER BY order_count DESC;
    ```

---

### Problem 20

**Query product name, price, and weight, but when weight is NULL, display an estimated weight calculated as price / 10 (assuming 1,000 won per 100g). Name the column `estimated_weight`.**

??? tip "Hint"
    Use `COALESCE(weight_grams, alternative_calculation)` to apply the alternative calculation only when NULL.

??? success "Answer"
    ```sql
    SELECT name,
           price,
           COALESCE(weight_grams, CAST(price / 10 AS INTEGER)) AS estimated_weight
    FROM products
    ORDER BY estimated_weight DESC
    LIMIT 10;
    ```

    > In real operations, when using such estimates, a separate flag column is used to distinguish estimated values from actual ones.

---

## Practical (21~30)

Practice NULL analysis, data quality checks, and NULL-safe comparisons.

---

### Problem 21

**Query the NULL count for multiple columns in the customers table at once. Find the NULL count for birth_date, gender, last_login_at, and acquisition_channel.**

??? tip "Hint"
    Calculate the NULL count for each column with `COUNT(*) - COUNT(column)`.

??? success "Answer"
    ```sql
    SELECT COUNT(*) - COUNT(birth_date) AS birth_null,
           COUNT(*) - COUNT(gender) AS gender_null,
           COUNT(*) - COUNT(last_login_at) AS login_null,
           COUNT(*) - COUNT(acquisition_channel) AS channel_null
    FROM customers;
    ```

---

### Problem 22

**Find the missing rate (%) for each nullable column in the customers table. Display to 1 decimal place.**

??? tip "Hint"
    Calculate the missing rate with `(COUNT(*) - COUNT(column)) * 100.0 / COUNT(*)`.

??? success "Answer"
    ```sql
    SELECT ROUND((COUNT(*) - COUNT(birth_date)) * 100.0 / COUNT(*), 1) AS birth_missing_pct,
           ROUND((COUNT(*) - COUNT(gender)) * 100.0 / COUNT(*), 1) AS gender_missing_pct,
           ROUND((COUNT(*) - COUNT(last_login_at)) * 100.0 / COUNT(*), 1) AS login_missing_pct,
           ROUND((COUNT(*) - COUNT(acquisition_channel)) * 100.0 / COUNT(*), 1) AS channel_missing_pct
    FROM customers;
    ```

---

### Problem 23

**Find the NULL rate (%) for notes, completed_at, and cancelled_at in the orders table.**

??? tip "Hint"
    Apply the same pattern from Problem 22 to the orders table.

??? success "Answer"
    ```sql
    SELECT ROUND((COUNT(*) - COUNT(notes)) * 100.0 / COUNT(*), 1) AS notes_missing_pct,
           ROUND((COUNT(*) - COUNT(completed_at)) * 100.0 / COUNT(*), 1) AS completed_missing_pct,
           ROUND((COUNT(*) - COUNT(cancelled_at)) * 100.0 / COUNT(*), 1) AS cancelled_missing_pct
    FROM orders;
    ```

---

### Problem 24

**Find the tier distribution of customers whose gender is NULL. Show the count and percentage (%) per tier.**

??? tip "Hint"
    Filter with `WHERE gender IS NULL`, then aggregate with `GROUP BY grade`. The percentage is relative to the total number of NULL-gender customers.

??? success "Answer"
    ```sql
    SELECT grade,
           COUNT(*) AS cnt,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM customers
    WHERE gender IS NULL
    GROUP BY grade
    ORDER BY cnt DESC;
    ```

    > If you haven't learned window functions yet, you can simply calculate the count without the percentage:

    ```sql
    SELECT grade,
           COUNT(*) AS cnt
    FROM customers
    WHERE gender IS NULL
    GROUP BY grade
    ORDER BY cnt DESC;
    ```

---

### Problem 25

**Find the number of customers where both birth_date and gender are NULL. Also find the number of customers where at least one of them is NULL.**

??? tip "Hint"
    Use `AND` for the "both NULL" condition and `OR` for the "at least one NULL" condition.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total,
           SUM(CASE WHEN birth_date IS NULL AND gender IS NULL THEN 1 ELSE 0 END) AS both_null,
           SUM(CASE WHEN birth_date IS NULL OR gender IS NULL THEN 1 ELSE 0 END) AS any_null
    FROM customers;
    ```

    > If you haven't learned CASE yet, you can split this into two queries:

    ```sql
    -- Both NULL
    SELECT COUNT(*) AS both_null
    FROM customers
    WHERE birth_date IS NULL AND gender IS NULL;

    -- At least one NULL
    SELECT COUNT(*) AS any_null
    FROM customers
    WHERE birth_date IS NULL OR gender IS NULL;
    ```

---

### Problem 26

**Compare the number of VIP-tier customers with NULL signup channel versus those with a signup channel.**

??? tip "Hint"
    Apply different `WHERE` conditions to two `COUNT` expressions, or use filtered COUNTs in a single query.

??? success "Answer"
    ```sql
    SELECT 'No channel' AS channel_status,
           COUNT(*) AS vip_count
    FROM customers
    WHERE acquisition_channel IS NULL AND grade = 'VIP'
    UNION ALL
    SELECT 'Has channel',
           COUNT(*)
    FROM customers
    WHERE acquisition_channel IS NOT NULL AND grade = 'VIP';
    ```

---

### Problem 27

**Find the number of products where either description or specs is NULL, and also the number where both are NULL.**

??? tip "Hint"
    Combine `OR` and `AND` to create two different conditions.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS total_products,
           SUM(CASE WHEN description IS NULL OR specs IS NULL THEN 1 ELSE 0 END) AS any_null,
           SUM(CASE WHEN description IS NULL AND specs IS NULL THEN 1 ELSE 0 END) AS both_null
    FROM products;
    ```

    > If you haven't learned CASE yet, run separate queries:

    ```sql
    SELECT COUNT(*) FROM products WHERE description IS NULL OR specs IS NULL;
    SELECT COUNT(*) FROM products WHERE description IS NULL AND specs IS NULL;
    ```

---

### Problem 28

**Find the order count and delivery notes completion rate (%) per year. Extract the year with `SUBSTR(ordered_at, 1, 4)`.**

??? tip "Hint"
    Group by year with `GROUP BY SUBSTR(ordered_at, 1, 4)`, then calculate the completion rate with `COUNT(notes) * 100.0 / COUNT(*)`.

??? success "Answer"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 4) AS year,
           COUNT(*) AS order_count,
           ROUND(COUNT(notes) * 100.0 / COUNT(*), 1) AS notes_rate_pct
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```

    > The year-over-year trend in delivery notes completion rate can help identify changes in customer behavior.

---

### Problem 29

**Find the brand-wise count of products where weight (`weight_grams`) is NULL, showing only brands with 5 or more such products.**

??? tip "Hint"
    Filter with `WHERE weight_grams IS NULL`, then apply `GROUP BY brand` and `HAVING COUNT(*) >= 5`.

??? success "Answer"
    ```sql
    SELECT brand, COUNT(*) AS null_weight_count
    FROM products
    WHERE weight_grams IS NULL
    GROUP BY brand
    HAVING COUNT(*) >= 5
    ORDER BY null_weight_count DESC;
    ```

---

### Problem 30

**Calculate a data completeness score for each customer. Count the number of non-NULL columns among birth_date, gender, last_login_at, and acquisition_channel (score 0-4). Find the customer count per score.**

??? tip "Hint"
    `(column IS NOT NULL)` returns TRUE=1 and FALSE=0 in SQLite. Adding all four gives the completeness score.

??? success "Answer"
    ```sql
    SELECT (birth_date IS NOT NULL)
         + (gender IS NOT NULL)
         + (last_login_at IS NOT NULL)
         + (acquisition_channel IS NOT NULL) AS completeness_score,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY completeness_score
    ORDER BY completeness_score;
    ```

    > A score of 0 means the customer entered none of the optional information, while 4 means all information was provided. This analysis serves as foundational data for customer profile completion campaigns.
