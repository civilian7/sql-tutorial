# Beginner Exercise: Customer Analysis

Uses the `customers` and `customer_addresses` tables. 15 problems practicing filtering, aggregation, and GROUP BY.

---

### 1. Total Customer Count

Find the number of active and inactive customers separately.

??? success "Answer"
    ```sql
    SELECT
        is_active,
        COUNT(*) AS customer_count
    FROM customers
    GROUP BY is_active;
    ```

---

### 2. Customers by Grade

Find the number of customers per grade.

??? success "Answer"
    ```sql
    SELECT grade, COUNT(*) AS cnt
    FROM customers
    GROUP BY grade
    ORDER BY cnt DESC;
    ```

---

### 3. VIP Customers

Retrieve the name, email, and point balance of VIP-grade customers, sorted by point balance in descending order.

??? success "Answer"
    ```sql
    SELECT name, email, point_balance
    FROM customers
    WHERE grade = 'VIP'
    ORDER BY point_balance DESC;
    ```

---

### 4. 10 Most Recent Signups

Retrieve the name, signup date, and grade of the 10 most recently registered customers.

??? success "Answer"
    ```sql
    SELECT name, created_at, grade
    FROM customers
    ORDER BY created_at DESC
    LIMIT 10;
    ```

---

### 5. Gender Ratio

Find the customer count and percentage by gender. Include NULL values.

??? success "Answer"
    ```sql
    SELECT
        COALESCE(gender, '미입력') AS gender,
        COUNT(*) AS cnt,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM customers
    GROUP BY gender;
    ```

---

### 6. Top 20 by Point Balance

Retrieve the name, grade, and point balance of the top 20 customers with the highest point balance.

??? success "Answer"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    WHERE is_active = 1
    ORDER BY point_balance DESC
    LIMIT 20;
    ```

---

### 7. Customers Without Birth Date

Find the number of customers whose birth_date is NULL.

??? success "Answer"
    ```sql
    SELECT COUNT(*) AS no_birthdate
    FROM customers
    WHERE birth_date IS NULL;
    ```

---

### 8. Signups by Year

Find the number of new customers per signup year.

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 4) AS join_year,
        COUNT(*) AS new_customers
    FROM customers
    GROUP BY SUBSTR(created_at, 1, 4)
    ORDER BY join_year;
    ```

---

### 9. Customers Who Never Logged In

Find the count and percentage of customers whose `last_login_at` is NULL.

??? success "Answer"
    ```sql
    SELECT
        COUNT(*) AS never_logged_in,
        ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct
    FROM customers
    WHERE last_login_at IS NULL;
    ```

---

### 10. Average Points by Grade

Find the average and maximum point balance per grade.

??? success "Answer"
    ```sql
    SELECT
        grade,
        COUNT(*) AS cnt,
        ROUND(AVG(point_balance), 0) AS avg_points,
        MAX(point_balance) AS max_points
    FROM customers
    GROUP BY grade
    ORDER BY avg_points DESC;
    ```

---

### 11. Email Domain Analysis

Find the customer count by email domain (after the @).

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(email, INSTR(email, '@') + 1) AS domain,
        COUNT(*) AS cnt
    FROM customers
    GROUP BY domain
    ORDER BY cnt DESC
    LIMIT 10;
    ```

---

### 12. Customers with Multiple Addresses

Retrieve the name and address count of customers who have registered 2 or more shipping addresses.

??? success "Answer"
    ```sql
    SELECT
        c.name,
        COUNT(a.id) AS address_count
    FROM customers AS c
    INNER JOIN customer_addresses AS a ON c.id = a.customer_id
    GROUP BY c.id, c.name
    HAVING COUNT(a.id) >= 2
    ORDER BY address_count DESC
    LIMIT 20;
    ```

---

### 13. VIP/GOLD Customers Who Joined in 2024

Retrieve the name, signup date, and grade of customers who joined in 2024 with a grade of VIP or GOLD.

??? success "Answer"
    ```sql
    SELECT name, created_at, grade
    FROM customers
    WHERE created_at LIKE '2024%'
      AND grade IN ('VIP', 'GOLD')
    ORDER BY created_at;
    ```

---

### 14. Monthly Signup Trend (2024)

Find the number of signups per month in 2024.

??? success "Answer"
    ```sql
    SELECT
        SUBSTR(created_at, 1, 7) AS month,
        COUNT(*) AS signups
    FROM customers
    WHERE created_at LIKE '2024%'
    GROUP BY SUBSTR(created_at, 1, 7)
    ORDER BY month;
    ```

---

### 15. Point Balance Distribution

Divide point balances into ranges — 0, 1–1,000, 1,001–5,000, 5,001–10,000, and 10,001+ — and count the customers in each range.

??? success "Answer"
    ```sql
    SELECT
        CASE
            WHEN point_balance = 0 THEN '없음'
            WHEN point_balance <= 1000 THEN '1~1,000'
            WHEN point_balance <= 5000 THEN '1,001~5,000'
            WHEN point_balance <= 10000 THEN '5,001~10,000'
            ELSE '10,001 이상'
        END AS point_range,
        COUNT(*) AS cnt
    FROM customers
    GROUP BY point_range
    ORDER BY MIN(point_balance);
    ```
