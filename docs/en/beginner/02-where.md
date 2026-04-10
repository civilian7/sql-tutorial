# Lesson 2: Filtering with WHERE

The `WHERE` clause narrows your results to only the rows that satisfy a condition. Without it, every row in the table is returned. Mastering `WHERE` is essential for answering real business questions.

```mermaid
flowchart LR
    T["🗄️ All Rows\n(5,230)"] --> W["WHERE\ncondition"] --> R["📋 Filtered\n(127 rows)"]
```

> **Concept:** WHERE filters rows by condition. Like extracting 127 VIP customers from 5,230 total.

## Comparison Operators

| Operator | Meaning |
|----------|---------|
| `=` | Equal |
| `<>` or `!=` | Not equal |
| `<`, `<=` | Less than, less than or equal |
| `>`, `>=` | Greater than, greater than or equal |

```sql
-- Products priced over $500
SELECT name, price
FROM products
WHERE price > 500;
```

**Result:**

| name                                   | price   |
| -------------------------------------- | ------: |
| Razer Blade 18 블랙                      | 2987500 |
| MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
| 삼성 DDR4 32GB PC4-25600                 |   49100 |
| ...                                    | ...     |

```sql
-- Only active products
SELECT name, price, stock_qty
FROM products
WHERE is_active = 1;
```

## AND / OR

Combine conditions with `AND` (both must be true) and `OR` (either must be true).

```sql
-- Active products priced between $100 and $500
SELECT name, price
FROM products
WHERE is_active = 1
  AND price >= 100
  AND price <= 500;
```

**Result:**

| name | price |
| ---- | ----- |

```sql
-- VIP or GOLD customers
SELECT name, email, grade
FROM customers
WHERE grade = 'VIP'
   OR grade = 'GOLD';
```

> **Tip:** Use parentheses when mixing `AND` and `OR` to make precedence explicit.
> `WHERE (grade = 'VIP' OR grade = 'GOLD') AND is_active = 1`

## IN

`IN` is a shortcut for multiple `OR` conditions on the same column.

```sql
-- Customers who are GOLD or VIP (cleaner with IN)
SELECT name, grade
FROM customers
WHERE grade IN ('GOLD', 'VIP');
```

**Result:**

| name | grade |
| ---- | ----- |
| 김경수  | VIP   |
| 김민재  | VIP   |
| 진정자  | VIP   |
| ...  | ...   |

```sql
-- Orders in terminal states
SELECT order_number, status, total_amount
FROM orders
WHERE status IN ('delivered', 'confirmed', 'returned');
```

## BETWEEN

`BETWEEN` tests for an inclusive range — equivalent to `>= low AND <= high`.

```sql
-- Products priced from $50 to $200
SELECT name, price
FROM products
WHERE price BETWEEN 50 AND 200;
```

**Result:**

| name | price |
| ---- | ----- |

```sql
-- Orders placed in Q1 2024
SELECT order_number, ordered_at, total_amount
FROM orders
WHERE ordered_at BETWEEN '2024-01-01' AND '2024-03-31 23:59:59';
```

## LIKE

`LIKE` matches text patterns. `%` matches any sequence of characters; `_` matches exactly one character.

```sql
-- Products whose name contains "Gaming"
SELECT name, price
FROM products
WHERE name LIKE '%Gaming%';
```

**Result:**

| name                                   | price   |
| -------------------------------------- | ------: |
| MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
| ASUS TUF Gaming RTX 5080 화이트           | 3812000 |
| MSI Radeon RX 7900 XTX GAMING X 화이트    | 1478100 |
| ...                                    | ...     |

```sql
-- Customers whose email is on testmail.com
SELECT name, email
FROM customers
WHERE email LIKE '%@testmail.com';
```

## IS NULL / IS NOT NULL

NULL means "unknown" or "missing." You cannot use `= NULL` — you must use `IS NULL`.

```sql
-- Customers with no birth date on file
SELECT name, email
FROM customers
WHERE birth_date IS NULL;
```

**Result:**

| name | email              |
| ---- | ------------------ |
| 김명자  | user7@testmail.kr  |
| 김정식  | user13@testmail.kr |
| ...  | ...                |

```sql
-- Orders that have delivery instructions
SELECT order_number, notes
FROM orders
WHERE notes IS NOT NULL;
```

!!! note "Lesson Review"
    Quick exercises to check your understanding of this lesson. For comprehensive practice combining multiple concepts, see the [Exercises](../exercises/index.md) section.

## Practice Exercises

### Exercise 1
Find all female customers (`gender = 'F'`) who hold a SILVER or GOLD membership grade. Return their `name`, `grade`, and `point_balance`.

??? success "Answer"
    ```sql
    SELECT name, grade, point_balance
    FROM customers
    WHERE gender = 'F'
      AND grade IN ('SILVER', 'GOLD');
    ```

### Exercise 2
List products that are active (`is_active = 1`) and priced between $200 and $800. Return `name` and `price`, ordered by price descending.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE is_active = 1
      AND price BETWEEN 200 AND 800
    ORDER BY price DESC;
    ```

### Exercise 3
Find all customers whose gender is unknown (NULL) and who have never logged in (`last_login_at IS NULL`). Return their `name` and `created_at`.

??? success "Answer"
    ```sql
    SELECT name, created_at
    FROM customers
    WHERE gender IS NULL
      AND last_login_at IS NULL;
    ```

### Exercise 4
Find all products with a price of $1,000 or more. Return `name` and `price`.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE price >= 1000;
    ```

### Exercise 5
List products whose stock quantity is not zero (`stock_qty <> 0`). Return `name` and `stock_qty`.

??? success "Answer"
    ```sql
    SELECT name, stock_qty
    FROM products
    WHERE stock_qty <> 0;
    ```

### Exercise 6
Find GOLD-grade customers whose point balance is between 500 and 2000. Return `name` and `point_balance`.

??? success "Answer"
    ```sql
    SELECT name, point_balance
    FROM customers
    WHERE grade = 'GOLD'
      AND point_balance BETWEEN 500 AND 2000;
    ```

### Exercise 7
List orders whose status is either `'pending'` or `'processing'`. Return `order_number` and `status`. Use the `IN` operator.

??? success "Answer"
    ```sql
    SELECT order_number, status
    FROM orders
    WHERE status IN ('pending', 'processing');
    ```

### Exercise 8
Find products whose name ends with "Keyboard". Return `name` and `price`.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%Keyboard';
    ```

### Exercise 9
From the `staff` table, find active employees (`is_active = 1`) who are not in the `'Sales'` department. Return `name` and `department`.

??? success "Answer"
    ```sql
    SELECT name, department
    FROM staff
    WHERE is_active = 1
      AND department <> 'Sales';
    ```

### Exercise 10
Find customers who are either VIP-grade and inactive (`is_active = 0`), or have a point balance of 5,000 or more. Return `name`, `grade`, `point_balance`, and `is_active`. Use parentheses to make the condition precedence clear.

??? success "Answer"
    ```sql
    SELECT name, grade, point_balance, is_active
    FROM customers
    WHERE (grade = 'VIP' AND is_active = 0)
       OR point_balance >= 5000;
    ```

---
Next: [Lesson 3: Sorting and Pagination](03-sort-limit.md)
