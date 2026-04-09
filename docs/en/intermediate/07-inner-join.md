# Lesson 7: INNER JOIN

A `JOIN` combines rows from two or more tables based on a related column. `INNER JOIN` returns only the rows where a match exists in **both** tables — unmatched rows are excluded entirely.

```mermaid
flowchart LR
    subgraph "customers"
        C1["ID:1 Kim"]
        C2["ID:2 Lee"]
        C3["ID:3 Park"]
    end
    subgraph "orders"
        O1["Cust:1 ORD-001"]
        O2["Cust:1 ORD-002"]
        O3["Cust:2 ORD-003"]
    end
    subgraph "INNER JOIN Result"
        R1["Kim + ORD-001"]
        R2["Kim + ORD-002"]
        R3["Lee + ORD-003"]
    end
    C1 --> R1
    C1 --> R2
    C2 --> R3
    O1 --> R1
    O2 --> R2
    O3 --> R3
```

> INNER JOIN returns only rows that match in both tables. Park (ID:3) has no orders and is excluded.

## Joining Two Tables

The syntax is `FROM table_a INNER JOIN table_b ON table_a.key = table_b.key`. The `ON` clause specifies the matching condition.

```sql
-- Show orders with customer names
SELECT
    o.order_number,
    c.name        AS customer_name,
    o.status,
    o.total_amount
FROM orders AS o
INNER JOIN customers AS c ON o.customer_id = c.id
ORDER BY o.ordered_at DESC
LIMIT 5;
```

**Result:**

| order_number | customer_name | status | total_amount |
|--------------|---------------|--------|-------------:|
| ORD-20241231-09842 | Jennifer Martinez | confirmed | 2349.00 |
| ORD-20241231-09841 | David Park | delivered | 149.99 |
| ORD-20241231-09840 | Sarah Johnson | shipped | 89.99 |
| ORD-20241230-09839 | Robert Kim | confirmed | 749.00 |
| ORD-20241230-09838 | Alex Chen | cancelled | 329.97 |

> **Table aliases** (`o`, `c`) shorten the query and make `ON` conditions easier to read. They are optional but strongly recommended when joining multiple tables.

## Why INNER JOIN Excludes Non-Matches

If a customer has never placed an order, they do not appear in this result — there is no matching row in `orders`. Similarly, an order cannot exist without a customer (due to the foreign key constraint), so all orders will match.

```sql
-- Confirm: all orders have a matching customer
SELECT COUNT(*) AS orders_without_customer
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id
WHERE c.id IS NULL;
```

## Joining Three or More Tables

Chain additional `JOIN` clauses. Each one links to a table already in scope.

```sql
-- Order items with product name and category name
SELECT
    oi.id           AS item_id,
    o.order_number,
    p.name          AS product_name,
    cat.name        AS category,
    oi.quantity,
    oi.unit_price
FROM order_items AS oi
INNER JOIN orders     AS o   ON oi.order_id   = o.id
INNER JOIN products   AS p   ON oi.product_id = p.id
INNER JOIN categories AS cat ON p.category_id = cat.id
ORDER BY o.ordered_at DESC
LIMIT 6;
```

**Result:**

| item_id | order_number | product_name | category | quantity | unit_price |
|--------:|--------------|--------------|----------|---------:|-----------:|
| 74513 | ORD-20241231-09842 | Dell XPS 15 Laptop | Laptops | 1 | 1299.99 |
| 74512 | ORD-20241231-09842 | Logitech MX Master 3 | Mice | 2 | 99.99 |
| 74511 | ORD-20241231-09841 | Samsung 27" Monitor | Monitors | 1 | 149.99 |
| 74510 | ORD-20241230-09840 | USB-C Hub 7-in-1 | Accessories | 1 | 89.99 |
| ... | | | | | |

## Aggregating After Joining

Join first, then aggregate. The joined table gives you the columns you need for grouping.

```sql
-- Total revenue per product category
SELECT
    cat.name        AS category,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(oi.quantity)     AS units_sold,
    SUM(oi.quantity * oi.unit_price) AS gross_revenue
FROM order_items AS oi
INNER JOIN orders     AS o   ON oi.order_id   = o.id
INNER JOIN products   AS p   ON oi.product_id = p.id
INNER JOIN categories AS cat ON p.category_id = cat.id
WHERE o.status IN ('delivered', 'confirmed')
GROUP BY cat.name
ORDER BY gross_revenue DESC
LIMIT 8;
```

**Result:**

| category | order_count | units_sold | gross_revenue |
|----------|------------:|-----------:|--------------:|
| Laptops | 6241 | 6312 | 7849201.88 |
| Desktops | 2841 | 2958 | 4293847.00 |
| Monitors | 5103 | 5587 | 2341920.45 |
| ... | | | |

## Filtering Across Joined Tables

You can apply `WHERE` conditions to any table in the join.

```sql
-- VIP customer orders over $1,000 in 2024
SELECT
    c.name          AS customer_name,
    o.order_number,
    o.total_amount,
    o.ordered_at
FROM orders AS o
INNER JOIN customers AS c ON o.customer_id = c.id
WHERE c.grade = 'VIP'
  AND o.total_amount > 1000
  AND o.ordered_at LIKE '2024%'
ORDER BY o.total_amount DESC;
```

!!! note "Lesson Review"
    Quick exercises to check your understanding of this lesson. For comprehensive practice combining multiple concepts, see the [Exercises](../exercises/index.md) section.

## Practice Exercises

### Exercise 1
List each review with the customer's `name` and the product's `name`. Return `review_id`, `customer_name`, `product_name`, `rating`, and `created_at`. Sort by `rating` descending, then `created_at` descending. Limit to 10 rows.

??? success "Answer"
    ```sql
    SELECT
        r.id          AS review_id,
        c.name        AS customer_name,
        p.name        AS product_name,
        r.rating,
        r.created_at
    FROM reviews AS r
    INNER JOIN customers AS c ON r.customer_id = c.id
    INNER JOIN products  AS p ON r.product_id  = p.id
    ORDER BY r.rating DESC, r.created_at DESC
    LIMIT 10;
    ```

### Exercise 2
For each payment method, count how many distinct customers have used it. Return `method` and `unique_customers`, sorted by `unique_customers` descending.

??? success "Answer"
    ```sql
    SELECT
        p.method,
        COUNT(DISTINCT o.customer_id) AS unique_customers
    FROM payments AS p
    INNER JOIN orders AS o ON p.order_id = o.id
    WHERE p.status = 'completed'
    GROUP BY p.method
    ORDER BY unique_customers DESC;
    ```

### Exercise 3
Find the top 5 customers by total amount spent (sum of `total_amount` for non-cancelled, non-returned orders). Return `customer_name`, `grade`, `order_count`, and `total_spent`.

??? success "Answer"
    ```sql
    SELECT
        c.name   AS customer_name,
        c.grade,
        COUNT(o.id)         AS order_count,
        SUM(o.total_amount) AS total_spent
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 5;
    ```

### Exercise 4
Show the `order_number`, `customer_name`, and `status` for orders whose status is `'shipped'`. Sort by `ordered_at` descending and limit to 10 rows.

??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        c.name   AS customer_name,
        o.status
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    WHERE o.status = 'shipped'
    ORDER BY o.ordered_at DESC
    LIMIT 10;
    ```

### Exercise 5
Join the `shipping` and `orders` tables to list delivered shipments. Return `order_number`, `carrier`, `tracking_number`, and `delivered_at`. Sort by `delivered_at` descending and limit to 10 rows.

??? success "Answer"
    ```sql
    SELECT
        o.order_number,
        s.carrier,
        s.tracking_number,
        s.delivered_at
    FROM shipping AS s
    INNER JOIN orders AS o ON s.order_id = o.id
    WHERE s.status = 'delivered'
    ORDER BY s.delivered_at DESC
    LIMIT 10;
    ```

### Exercise 6
From `order_items`, show the product name (`products.name`), supplier name (`suppliers.company_name`), quantity, and unit price. Join three tables and sort by unit price descending. Limit to 10 rows.

??? success "Answer"
    ```sql
    SELECT
        p.name          AS product_name,
        sup.company_name AS supplier_name,
        oi.quantity,
        oi.unit_price
    FROM order_items AS oi
    INNER JOIN products  AS p   ON oi.product_id  = p.id
    INNER JOIN suppliers AS sup ON p.supplier_id   = sup.id
    ORDER BY oi.unit_price DESC
    LIMIT 10;
    ```

### Exercise 7
For each supplier, find the total number of orders containing their products (`order_count`) and the total quantity sold (`total_qty`). Return `company_name`, `order_count`, and `total_qty`, sorted by `total_qty` descending.

??? success "Answer"
    ```sql
    SELECT
        sup.company_name,
        COUNT(DISTINCT oi.order_id) AS order_count,
        SUM(oi.quantity)            AS total_qty
    FROM order_items AS oi
    INNER JOIN products  AS p   ON oi.product_id = p.id
    INNER JOIN suppliers AS sup ON p.supplier_id  = sup.id
    GROUP BY sup.id, sup.company_name
    ORDER BY total_qty DESC;
    ```

### Exercise 8
For each staff member, count the orders they handled (`order_count`) and total revenue (`total_revenue`). Exclude cancelled and returned orders. Return `staff_name`, `department`, `order_count`, and `total_revenue`. Sort by `total_revenue` descending and limit to 10.

??? success "Answer"
    ```sql
    SELECT
        st.name        AS staff_name,
        st.department,
        COUNT(o.id)         AS order_count,
        SUM(o.total_amount) AS total_revenue
    FROM orders AS o
    INNER JOIN staff AS st ON o.staff_id = st.id
    WHERE o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY st.id, st.name, st.department
    ORDER BY total_revenue DESC
    LIMIT 10;
    ```

---
Next: [Lesson 8: LEFT JOIN](08-left-join.md)
