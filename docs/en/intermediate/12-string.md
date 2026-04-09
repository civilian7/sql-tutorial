# Lesson 12: String Functions

String functions often differ in name or argument order across databases. This lesson uses SQLite as the default but shows MySQL and PostgreSQL alternatives in tabs where the syntax diverges.

SQLite provides a useful set of functions for manipulating text. These are essential for cleaning data, formatting output, parsing stored strings, and building search conditions.

## SUBSTR — Extract Part of a String

`SUBSTR(string, start, length)` — `start` is 1-based; omit `length` to get everything to the end.

```sql
-- Extract the date portion from order timestamps
SELECT
    order_number,
    ordered_at,
    SUBSTR(ordered_at, 1, 10) AS order_date,
    SUBSTR(ordered_at, 1, 7)  AS year_month
FROM orders
LIMIT 5;
```

**Result:**

| order_number | ordered_at | order_date | year_month |
|--------------|------------|------------|------------|
| ORD-20150314-00001 | 2015-03-14 08:23:11 | 2015-03-14 | 2015-03 |
| ORD-20150314-00002 | 2015-03-14 11:47:33 | 2015-03-14 | 2015-03 |
| ORD-20150315-00003 | 2015-03-15 09:12:05 | 2015-03-15 | 2015-03 |

```sql
-- Parse the year from an order number: ORD-20240315-00001
SELECT
    order_number,
    SUBSTR(order_number, 5, 4)  AS order_year,
    SUBSTR(order_number, 9, 2)  AS order_month,
    SUBSTR(order_number, 11, 2) AS order_day
FROM orders
LIMIT 3;
```

## LENGTH

`LENGTH(string)` returns the number of characters.

```sql
-- Find unusually short or long product names
SELECT name, LENGTH(name) AS name_length
FROM products
ORDER BY name_length DESC
LIMIT 5;
```

**Result:**

| name | name_length |
|------|------------:|
| Razer BlackWidow V3 Pro Wireless TKL Gaming Keyboard | 52 |
| ASUS ProArt PA329CRV 32" 4K HDR Professional Monitor | 51 |
| ... | |

## UPPER and LOWER

```sql
-- Normalize email addresses for display
SELECT
    name,
    LOWER(email) AS email_lower,
    UPPER(grade) AS grade_display
FROM customers
LIMIT 5;
```

**Result:**

| name | email_lower | grade_display |
|------|-------------|---------------|
| Jennifer Martinez | jennifer.m@testmail.com | VIP |
| Alex Chen | alex.chen@testmail.com | SILVER |

## REPLACE

`REPLACE(string, find, replacement)` substitutes all occurrences.

```sql
-- Mask phone numbers: show only last 4 digits
SELECT
    name,
    REPLACE(
        REPLACE(phone, SUBSTR(phone, 1, 9), '***-****-'),
        SUBSTR(phone, 1, 9), '***-****-'
    ) AS masked_phone
FROM customers
LIMIT 3;
```

```sql
-- Normalize status values that might have underscores
SELECT DISTINCT
    status,
    REPLACE(status, '_', ' ') AS status_readable
FROM orders;
```

**Result:**

| status | status_readable |
|--------|-----------------|
| pending | pending |
| return_requested | return requested |
| ... | |

## String Concatenation

=== "SQLite / PostgreSQL"
    ```sql
    -- Build a contact info string with ||
    SELECT
        name,
        phone || ' — ' || email AS contact_info
    FROM customers
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    -- Build a contact info string with CONCAT()
    SELECT
        name,
        CONCAT(phone, ' — ', email) AS contact_info
    FROM customers
    LIMIT 5;
    ```

**Result:**

| name | contact_info |
|------|--------------|
| Jennifer Martinez | 555-0142-8821 — jennifer.m@testmail.com |
| Alex Chen | 555-0287-4412 — alex.chen@testmail.com |

=== "SQLite / PostgreSQL"
    ```sql
    -- Display SKU with category prefix
    SELECT
        p.name,
        cat.name || '-' || p.sku AS display_sku
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    -- Display SKU with category prefix
    SELECT
        p.name,
        CONCAT(cat.name, '-', p.sku) AS display_sku
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LIMIT 5;
    ```

## LIKE for Pattern Matching

Covered in Lesson 2, but here are more advanced patterns.

=== "SQLite"
    ```sql
    -- Users per email domain (after @)
    SELECT DISTINCT
        SUBSTR(email, INSTR(email, '@') + 1) AS domain,
        COUNT(*) AS users
    FROM customers
    GROUP BY domain
    ORDER BY users DESC
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    -- Users per email domain (after @)
    SELECT
        SUBSTRING(email, LOCATE('@', email) + 1) AS domain,
        COUNT(*) AS users
    FROM customers
    GROUP BY domain
    ORDER BY users DESC
    LIMIT 5;
    ```

=== "PostgreSQL"
    ```sql
    -- Users per email domain (after @)
    SELECT
        SUBSTRING(email FROM POSITION('@' IN email) + 1) AS domain,
        COUNT(*) AS users
    FROM customers
    GROUP BY domain
    ORDER BY users DESC
    LIMIT 5;
    ```

```sql
-- Products with model numbers that contain digits
SELECT name
FROM products
WHERE name LIKE '%[0-9]%'   -- note: this is standard SQL syntax
-- In SQLite use GLOB for character classes:
-- WHERE name GLOB '*[0-9]*'
LIMIT 5;
```

## TRIM, LTRIM, RTRIM

Remove leading and/or trailing characters (spaces by default).

```sql
-- Clean up any accidental whitespace in product names
SELECT
    name,
    TRIM(name)   AS cleaned_name,
    LENGTH(name) - LENGTH(TRIM(name)) AS extra_chars
FROM products
WHERE LENGTH(name) != LENGTH(TRIM(name));
```

!!! note "Lesson Review"
    Quick exercises to check your understanding of this lesson. For comprehensive practice combining multiple concepts, see the [Exercises](../exercises/index.md) section.

## Practice Exercises

### Exercise 1
Build a customer contact card: concatenate each customer's `name`, `phone`, and `email` into a single string formatted as `"Name | Phone | Email"`. Return `customer_id`, `contact_card`, and `grade` for all active customers. Limit to 10 rows.

??? success "Answer"
    === "SQLite / PostgreSQL"
        ```sql
        SELECT
            id AS customer_id,
            name || ' | ' || phone || ' | ' || email AS contact_card,
            grade
        FROM customers
        WHERE is_active = 1
        LIMIT 10;
        ```

    === "MySQL"
        ```sql
        SELECT
            id AS customer_id,
            CONCAT(name, ' | ', phone, ' | ', email) AS contact_card,
            grade
        FROM customers
        WHERE is_active = 1
        LIMIT 10;
        ```

### Exercise 2
For each order, extract the sequence number (the last 5 digits of `order_number`, e.g. `00042` from `ORD-20240315-00042`) and display it as an integer. Return `order_number`, `sequence_no` (as integer), and `total_amount`. Sort by `sequence_no` descending, limit 10.

??? success "Answer"
    ```sql
    SELECT
        order_number,
        CAST(SUBSTR(order_number, -5) AS INTEGER) AS sequence_no,
        total_amount
    FROM orders
    ORDER BY sequence_no DESC
    LIMIT 10;
    ```

### Exercise 3
Find the 5 customers with the longest names. Return `name` and `name_length`, sorted by `name_length` descending.

??? success "Answer"
    ```sql
    SELECT
        name,
        LENGTH(name) AS name_length
    FROM customers
    ORDER BY name_length DESC
    LIMIT 5;
    ```

### Exercise 4
Replace underscores with spaces in order `status` values and convert them to uppercase. Show only distinct values. Return the original `status` and `display_status`.

??? success "Answer"
    ```sql
    SELECT DISTINCT
        status,
        UPPER(REPLACE(status, '_', ' ')) AS display_status
    FROM orders;
    ```

### Exercise 5
Find products whose name contains the word `'Gaming'`. Return `name` and `price`, sorted by price descending. Use a LIKE pattern.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%Gaming%'
    ORDER BY price DESC;
    ```

### Exercise 6
Extract the user ID part of each customer's email (everything before the `@`). Return `name`, `email`, and `user_id`. Limit to 10 rows.

??? success "Answer"
    === "SQLite"
        ```sql
        SELECT
            name,
            email,
            SUBSTR(email, 1, INSTR(email, '@') - 1) AS user_id
        FROM customers
        LIMIT 10;
        ```

    === "MySQL"
        ```sql
        SELECT
            name,
            email,
            SUBSTRING(email, 1, LOCATE('@', email) - 1) AS user_id
        FROM customers
        LIMIT 10;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            name,
            email,
            SUBSTRING(email FROM 1 FOR POSITION('@' IN email) - 1) AS user_id
        FROM customers
        LIMIT 10;
        ```

### Exercise 7
Truncate product names to 20 characters and append `'...'` if the name is longer than 20 characters. If the name is 20 characters or fewer, show it as-is. Return `name` and `short_name`, sorted by name length descending, limit 10.

??? success "Answer"
    === "SQLite / PostgreSQL"
        ```sql
        SELECT
            name,
            CASE
                WHEN LENGTH(name) > 20
                    THEN SUBSTR(name, 1, 20) || '...'
                ELSE name
            END AS short_name
        FROM products
        ORDER BY LENGTH(name) DESC
        LIMIT 10;
        ```

    === "MySQL"
        ```sql
        SELECT
            name,
            CASE
                WHEN LENGTH(name) > 20
                    THEN CONCAT(SUBSTRING(name, 1, 20), '...')
                ELSE name
            END AS short_name
        FROM products
        ORDER BY LENGTH(name) DESC
        LIMIT 10;
        ```

### Exercise 8
Build a display string in the format `"GRADE: grade - Name"` for each customer, where grade appears in both uppercase and lowercase. Return `id` and `display_text` for active customers. Limit to 10 rows.

??? success "Answer"
    === "SQLite / PostgreSQL"
        ```sql
        SELECT
            id,
            UPPER(grade) || ': ' || LOWER(grade) || ' - ' || name AS display_text
        FROM customers
        WHERE is_active = 1
        LIMIT 10;
        ```

    === "MySQL"
        ```sql
        SELECT
            id,
            CONCAT(UPPER(grade), ': ', LOWER(grade), ' - ', name) AS display_text
        FROM customers
        WHERE is_active = 1
        LIMIT 10;
        ```

### Exercise 9
From orders starting with `'ORD-2024'`, extract the date portion embedded in the order number (characters 5 through 12, e.g. `20240315`). Return `order_number`, `date_part`, and `total_amount`. Limit to 10 rows.

??? success "Answer"
    ```sql
    SELECT
        order_number,
        SUBSTR(order_number, 5, 8) AS date_part,
        total_amount
    FROM orders
    WHERE order_number LIKE 'ORD-2024%'
    LIMIT 10;
    ```

### Exercise 10
Find the position of the first space in product names. Only include products whose name contains a space. Return `name` and `space_pos`. Limit to 10 rows.

??? success "Answer"
    === "SQLite"
        ```sql
        SELECT
            name,
            INSTR(name, ' ') AS space_pos
        FROM products
        WHERE INSTR(name, ' ') > 0
        LIMIT 10;
        ```

    === "MySQL"
        ```sql
        SELECT
            name,
            LOCATE(' ', name) AS space_pos
        FROM products
        WHERE LOCATE(' ', name) > 0
        LIMIT 10;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            name,
            POSITION(' ' IN name) AS space_pos
        FROM products
        WHERE POSITION(' ' IN name) > 0
        LIMIT 10;
        ```

---
Next: [Lesson 13: UNION](13-union.md)
