# Lesson 12: String Functions

In [Lesson 11](11-datetime.md), we learned to calculate periods and change formats with date/time functions. In data analysis, tasks like "customer count by email domain" or "extracting brand from product name" are common. String functions let you slice, replace, and concatenate text.

!!! note "Already familiar?"
    If you're comfortable with SUBSTR, REPLACE, CONCAT, LENGTH, UPPER/LOWER, and TRIM, skip ahead to [Lesson 13: Numeric, Conversion, and Conditional Functions](13-utility-functions.md).

String functions often have different names or argument orders across databases. This lesson uses SQLite as the default, with MySQL and PostgreSQL tabs shown where differences exist.

## SUBSTR -- Extracting Part of a String

`SUBSTR(string, start, length)` -- `start` is 1-based. If `length` is omitted, it returns to the end.

```sql
-- Extract date part from order timestamp
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
| ---------- | ---------- | ---------- | ---------- |
| ORD-20160101-00001 | 2016-01-17 03:39:08 | 2016-01-17 | 2016-01 |
| ORD-20160102-00002 | 2016-01-11 20:08:34 | 2016-01-11 | 2016-01 |
| ORD-20160102-00003 | 2016-01-11 04:08:34 | 2016-01-11 | 2016-01 |
| ORD-20160103-00004 | 2016-01-18 01:56:50 | 2016-01-18 | 2016-01 |
| ORD-20160103-00005 | 2016-01-12 01:08:34 | 2016-01-12 | 2016-01 |
| ... | ... | ... | ... |

```sql
-- Parse year/month/day from order number: ORD-20240315-00001
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
-- Find products with particularly short or long names
SELECT name, LENGTH(name) AS name_length
FROM products
ORDER BY name_length DESC
LIMIT 5;
```

**Result:**

| name | name_length |
| ---------- | ----------: |
| ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 113 |
| HP EliteBook 840 G10 Black [Special Limited Edition] Extended 3-year warranty + exclusive carrying case included | 112 |
| ASUS ExpertBook B5 [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | 110 |
| ASUS ExpertBook B5 [Special Limited Edition] RGB lighting equipped, software customization supported | 100 |
| TeamGroup T-Force Delta RGB DDR5 32GB 6000MHz Silver | 52 |
| ... | ... |

## UPPER and LOWER

```sql
-- Normalize email to lowercase, display grade in uppercase
SELECT
    name,
    LOWER(email) AS email_lower,
    UPPER(grade) AS grade_display
FROM customers
LIMIT 5;
```

**Result:**

| name | email_lower | grade_display |
| ---------- | ---------- | ---------- |
| Joshua Atkins | user1@testmail.kr | BRONZE |
| Danny Johnson | user2@testmail.kr | GOLD |
| Adam Moore | user3@testmail.kr | VIP |
| Virginia Steele | user4@testmail.kr | GOLD |
| Jared Vazquez | user5@testmail.kr | SILVER |
| ... | ... | ... |

## REPLACE

`REPLACE(string, find, replacement)` replaces all occurrences.

```sql
-- Phone number masking: show only last 4 digits
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
-- Convert underscore-separated status values to readable format
SELECT DISTINCT
    status,
    REPLACE(status, '_', ' ') AS status_readable
FROM orders;
```

**Result:**

| status | status_readable |
| ---------- | ---------- |
| cancelled | cancelled |
| confirmed | confirmed |
| delivered | delivered |
| paid | paid |
| pending | pending |
| preparing | preparing |
| return_requested | return requested |
| returned | returned |
| ... | ... |

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
| 김민수 | 020-1234-5678 — k.minsu@testmail.kr |
| 이지은 | 020-9876-5432 — l.jieun@testmail.kr |

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

## Pattern Matching with LIKE

We covered this in Lesson 2, but here are more advanced pattern examples.

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
-- Products with numbers in model name
SELECT name
FROM products
WHERE name LIKE '%[0-9]%'   -- Standard SQL syntax
-- In SQLite, use GLOB for character classes:
-- WHERE name GLOB '*[0-9]*'
LIMIT 5;
```

## TRIM, LTRIM, RTRIM

Removes leading/trailing whitespace (or specified characters).

```sql
-- Clean up accidental whitespace in product names
SELECT
    name,
    TRIM(name)   AS cleaned_name,
    LENGTH(name) - LENGTH(TRIM(name)) AS extra_chars
FROM products
WHERE LENGTH(name) != LENGTH(TRIM(name));
```

## NULL and String Concatenation

The most common mistake in string concatenation: **if one side is NULL, the entire result is NULL**.

```sql
-- If birth_date is NULL, contact_info is also NULL!
SELECT
    name || ' (' || birth_date || ')' AS contact_info
FROM customers
LIMIT 5;
```

| contact_info         |
| -------------------- |
| 정준호 (1988-03-15)    |
| (NULL)               |
| 김민재 (1995-07-22)    |
| ...                  |

You must use `COALESCE` to replace NULL with a substitute string.

=== "SQLite / PostgreSQL"
    ```sql
    SELECT
        name || ' (' || COALESCE(birth_date, 'N/A') || ')' AS contact_info
    FROM customers
    LIMIT 5;
    ```

=== "MySQL"
    ```sql
    -- MySQL's CONCAT() also returns NULL when NULL is present
    SELECT
        CONCAT(name, ' (', COALESCE(birth_date, 'N/A'), ')') AS contact_info
    FROM customers
    LIMIT 5;

    -- CONCAT_WS() skips NULLs (with specified separator)
    SELECT
        CONCAT_WS(' | ', name, phone, email) AS contact_info
    FROM customers
    LIMIT 5;
    ```

> **Rule:** When concatenating strings, always wrap columns that can be NULL with `COALESCE(col, 'default')`. MySQL's `CONCAT_WS()` automatically skips NULLs, which is convenient.

## LPAD, RPAD -- Fixed-Width Padding

Pads a string to a specified length, filling the shortfall with a specific character. Useful for order number formatting, report alignment, etc.

=== "SQLite"
    SQLite does not have `LPAD`/`RPAD` functions. Use `printf()` as a substitute.

    ```sql
    -- Zero-pad customer ID to 5 digits
    SELECT
        id,
        printf('%05d', id) AS padded_id,
        name
    FROM customers
    LIMIT 5;
    ```

    | id | padded_id | name |
    | -: | --------- | ---- |
    |  1 | 00001     | 정준호  |
    |  2 | 00002     | 김경수  |
    | ...| ...       | ...  |

=== "MySQL"
    ```sql
    -- Zero-pad customer ID to 5 digits
    SELECT
        id,
        LPAD(id, 5, '0') AS padded_id,
        name
    FROM customers
    LIMIT 5;

    -- Fixed-width product name to 30 chars (right-pad with spaces)
    SELECT RPAD(name, 30, ' ') AS fixed_name, price
    FROM products
    LIMIT 5;
    ```

=== "PostgreSQL"
    ```sql
    -- Zero-pad customer ID to 5 digits
    SELECT
        id,
        LPAD(id::text, 5, '0') AS padded_id,
        name
    FROM customers
    LIMIT 5;

    -- Fixed-width product name to 30 chars
    SELECT RPAD(name, 30, ' ') AS fixed_name, price
    FROM products
    LIMIT 5;
    ```

> `LPAD(value, total_length, fill_char)` pads the **left**, `RPAD` pads the **right**. If the value is longer than total_length, MySQL/PG will truncate it.

## GROUP_CONCAT / STRING_AGG -- String Aggregation by Group

Combines strings from multiple rows into one. A very commonly used function for "product list by category", "order numbers per customer", etc.

=== "SQLite"
    ```sql
    -- Product name list by supplier
    SELECT
        s.company_name,
        GROUP_CONCAT(p.name, ', ') AS product_list,
        COUNT(*)                   AS product_count
    FROM products AS p
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    WHERE p.is_active = 1
    GROUP BY s.company_name
    ORDER BY product_count DESC
    LIMIT 3;
    ```

    > SQLite's `GROUP_CONCAT(col, separator)` -- default separator is `','` (comma).

=== "MySQL"
    ```sql
    -- Product name list by supplier
    SELECT
        s.company_name,
        GROUP_CONCAT(p.name ORDER BY p.name SEPARATOR ', ') AS product_list,
        COUNT(*) AS product_count
    FROM products AS p
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    WHERE p.is_active = 1
    GROUP BY s.company_name
    ORDER BY product_count DESC
    LIMIT 3;
    ```

    > MySQL's `GROUP_CONCAT` supports `ORDER BY` and `SEPARATOR`. Default max length is 1024 bytes (`group_concat_max_len`).

=== "PostgreSQL"
    ```sql
    -- Product name list by supplier
    SELECT
        s.company_name,
        STRING_AGG(p.name, ', ' ORDER BY p.name) AS product_list,
        COUNT(*) AS product_count
    FROM products AS p
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    WHERE p.is_active = 1
    GROUP BY s.company_name
    ORDER BY product_count DESC
    LIMIT 3;
    ```

    > PostgreSQL uses `STRING_AGG(col, separator ORDER BY ...)` format. No length limit.

**Result (example):**

| company_name | product_list                              | product_count |
| ------------ | ----------------------------------------- | ------------: |
| 에이수스코리아      | ASUS Dual RTX 5070 Ti ..., ASUS PCE-BE92BT ... | 21 |
| 삼성전자 공식 유통   | 삼성 DDR4 32GB ..., 삼성 DDR5 16GB ...         | 21 |
| ...          | ...                                       | ...           |

```sql
-- Customer names by grade (top 5 each)
SELECT
    grade,
    GROUP_CONCAT(name, ', ') AS sample_names
FROM (
    SELECT grade, name, ROW_NUMBER() OVER (PARTITION BY grade ORDER BY id) AS rn
    FROM customers
    WHERE is_active = 1
) AS ranked
WHERE rn <= 5
GROUP BY grade;
```

## REGEXP -- Regular Expressions

LIKE's `%` and `_` alone make it difficult to express complex patterns like "alphanumeric combinations" or "email format validation". Regular expressions enable much more precise pattern matching.

### Database Support

=== "SQLite"
    SQLite has the `REGEXP` operator in its syntax, but **the default installation has no implementation**, so using it causes an error. An extension must be loaded for it to work.

    As an alternative, use `GLOB`. GLOB is case-sensitive and supports `*` (multiple characters), `?` (single character), and `[...]` (character classes).

    ```sql
    -- Products with numbers in name (using GLOB)
    SELECT name, price
    FROM products
    WHERE name GLOB '*[0-9]*'
    LIMIT 5;
    ```

    ```sql
    -- Products starting with uppercase letters
    SELECT name
    FROM products
    WHERE name GLOB '[A-Z]*'
    LIMIT 5;
    ```

=== "MySQL"
    MySQL natively supports the `REGEXP` (or synonym `RLIKE`) operator. MySQL 8.0+ uses the ICU regular expression library.

    ```sql
    -- Model number pattern: letters followed by numbers (e.g., RTX 5070, DDR5 16GB)
    SELECT name, price
    FROM products
    WHERE name REGEXP '[A-Za-z]+[0-9]+'
    LIMIT 5;
    ```

    ```sql
    -- Basic email format validation (characters before and after @)
    SELECT name, email
    FROM customers
    WHERE email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
    LIMIT 5;
    ```

=== "PostgreSQL"
    PostgreSQL uses the `~` operator (case-sensitive) and `~*` operator (case-insensitive). It supports POSIX regular expressions.

    ```sql
    -- Model number pattern: letters followed by numbers
    SELECT name, price
    FROM products
    WHERE name ~ '[A-Za-z]+[0-9]+'
    LIMIT 5;
    ```

    ```sql
    -- Case-insensitive: products containing 'gaming' (using ~*)
    SELECT name, price
    FROM products
    WHERE name ~* 'gaming'
    LIMIT 5;

    -- Basic email format validation
    SELECT name, email
    FROM customers
    WHERE email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    LIMIT 5;
    ```

### Syntax Comparison

| DB | Operator | Case Insensitive | Example |
|----|--------|:----------:|------|
| SQLite | GLOB (alternative) | No | `WHERE name GLOB '*[0-9]*'` |
| MySQL | REGEXP / RLIKE | Yes by default | `WHERE name REGEXP '[0-9]+'` |
| PostgreSQL | `~` | Use `~*` | `WHERE name ~ '[0-9]+'` |

> **Practical tip:** REGEXP cannot use indexes, so for large datasets, narrow down with LIKE first, then use REGEXP for precise filtering.

## Summary

| Concept | Description | Example |
|------|------|------|
| SUBSTR | Extract part of a string (1-based) | `SUBSTR(name, 1, 10)` |
| LENGTH | Returns character count | `LENGTH(name)` |
| UPPER / LOWER | Case conversion | `UPPER(grade)`, `LOWER(email)` |
| REPLACE | String replacement | `REPLACE(status, '_', ' ')` |
| String concatenation | SQLite/PG: `\|\|`, MySQL: `CONCAT()` | `name \|\| ' - ' \|\| email` |
| NULL + concatenation | If NULL, entire result is NULL -> COALESCE required | `COALESCE(col, 'default')` |
| INSTR / LOCATE / POSITION | Find character position (varies by DB) | `INSTR(email, '@')` |
| TRIM / LTRIM / RTRIM | Remove leading/trailing whitespace/characters | `TRIM(name)` |
| LPAD / RPAD | Fixed-width padding (SQLite: `printf`) | `LPAD(id, 5, '0')` |
| GROUP_CONCAT / STRING_AGG | Aggregate strings by group | `GROUP_CONCAT(name, ', ')` |
| LIKE | Pattern matching (`%`, `_` wildcards) | `WHERE name LIKE '%Gaming%'` |
| REGEXP | Regular expression pattern matching (varies by DB) | MySQL: `REGEXP`, PG: `~`, SQLite: `GLOB` |

!!! note "Lesson Review Problems"
    These are simple problems to immediately test the concepts from this lesson. For comprehensive practice combining multiple concepts, see the [Practice Problems](../exercises/index.md) section.

## Practice Problems

### Problem 1
Create a customer contact card: concatenate each customer's `name`, `phone`, `email` into a single string in `"name | phone | email"` format. Return `customer_id`, `contact_card`, `grade` for all active customers, limited to 10 rows.

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

        **Result (example):**

| customer_id | contact_card | grade |
| ----------: | ---------- | ---------- |
| 2 | Danny Johnson | 555-4423-5167 | user2@testmail.kr | GOLD |
| 3 | Adam Moore | 555-0806-0711 | user3@testmail.kr | VIP |
| 4 | Virginia Steele | 555-9666-8856 | user4@testmail.kr | GOLD |
| 5 | Jared Vazquez | 555-0239-9503 | user5@testmail.kr | SILVER |
| 8 | Tyler Rodriguez | 555-8951-7989 | user8@testmail.kr | SILVER |
| 10 | John Stark | 555-1196-8263 | user10@testmail.kr | GOLD |
| 12 | Michael Velasquez | 555-0083-5468 | user12@testmail.kr | GOLD |
| 14 | Martha Murphy | 555-4730-0267 | user14@testmail.kr | BRONZE |
| ... | ... | ... |


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

### Problem 2
Extract the sequence number from each order (e.g., last 5 digits `00042` from `ORD-20240315-00042`) and display as integer. Return `order_number`, `sequence_no` (integer), `total_amount`, sorted by `sequence_no` descending, limited to 10 rows.

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

    **Result (example):**

| order_number | sequence_no | total_amount |
| ---------- | ----------: | ----------: |
| ORD-20251231-37557 | 37557 | 388500.0 |
| ORD-20251231-37556 | 37556 | 153900.0 |
| ORD-20251231-37555 | 37555 | 74800.0 |
| ORD-20251231-37554 | 37554 | 74900.0 |
| ORD-20251231-37553 | 37553 | 350500.0 |
| ORD-20251231-37552 | 37552 | 254300.0 |
| ORD-20251231-37551 | 37551 | 417000.0 |
| ORD-20251231-37550 | 37550 | 71200.0 |
| ... | ... | ... |


### Problem 3
Find the length of customer names and return the top 5 with the longest names. Sort by `name_length` descending.

??? success "Answer"
    ```sql
    SELECT
        name,
        LENGTH(name) AS name_length
    FROM customers
    ORDER BY name_length DESC
    LIMIT 5;
    ```

    **Result (example):**

| name | name_length |
| ---------- | ----------: |
| Mr. William Hernandez Jr. | 25 |
| Mr. Michael Contreras IV | 24 |
| Mrs. Christina Scott DVM | 24 |
| Dr. Brandon Martinez DDS | 24 |
| Mr. James Hernandez DDS | 23 |
| ... | ... |


### Problem 4
Replace underscores (`_`) in order status with spaces and convert to uppercase. Show only unique status values. Return `status` (original) and `display_status`.

??? success "Answer"
    ```sql
    SELECT DISTINCT
        status,
        UPPER(REPLACE(status, '_', ' ')) AS display_status
    FROM orders;
    ```

    **Result (example):**

| status | display_status |
| ---------- | ---------- |
| cancelled | CANCELLED |
| confirmed | CONFIRMED |
| delivered | DELIVERED |
| paid | PAID |
| pending | PENDING |
| preparing | PREPARING |
| return_requested | RETURN REQUESTED |
| returned | RETURNED |
| ... | ... |


### Problem 5
Query `name` and `price` for products containing the word `'Gaming'` in their name, sorted by price descending. Use a LIKE pattern.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%Gaming%'
    ORDER BY price DESC;
    ```

    **Result (example):**

| name | price |
| ---------- | ----------: |
| ASUS TUF Gaming RTX 5080 White | 4526600.0 |
| MSI Radeon RX 9070 XT GAMING X | 1896000.0 |
| MSI GeForce RTX 4070 Ti Super GAMING X | 1744000.0 |
| MSI Radeon RX 7900 XTX GAMING X White | 1517600.0 |
| APC Back-UPS Pro Gaming BGM1500B Black | 516300.0 |
| ... | ... |


### Problem 6
Extract only the user ID portion before `@` from customer emails. Return `name`, `email`, `user_id`, limited to 10 rows.

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

        **Result (example):**

| name | email | user_id |
| ---------- | ---------- | ---------- |
| Joshua Atkins | user1@testmail.kr | user1 |
| Danny Johnson | user2@testmail.kr | user2 |
| Adam Moore | user3@testmail.kr | user3 |
| Virginia Steele | user4@testmail.kr | user4 |
| Jared Vazquez | user5@testmail.kr | user5 |
| Benjamin Skinner | user6@testmail.kr | user6 |
| Ashley Jones | user7@testmail.kr | user7 |
| Tyler Rodriguez | user8@testmail.kr | user8 |
| ... | ... | ... |


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

### Problem 7
Create a `short_name` by truncating product names to the first 20 characters and appending ellipsis (`...`). If the name is 20 characters or less, show the original name. Return `name`, `short_name`, sorted by name length descending, limited to 10 rows.

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

        **Result (example):**

| name | short_name |
| ---------- | ---------- |
| ASUS Dual RTX 5070 Ti [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | ASUS Dual RTX 5070 T... |
| HP EliteBook 840 G10 Black [Special Limited Edition] Extended 3-year warranty + exclusive carrying case included | HP EliteBook 840 G10... |
| ASUS ExpertBook B5 [Special Limited Edition] Low-noise design, energy efficiency rated, eco-friendly packaging | ASUS ExpertBook B5 [... |
| ASUS ExpertBook B5 [Special Limited Edition] RGB lighting equipped, software customization supported | ASUS ExpertBook B5 [... |
| TeamGroup T-Force Delta RGB DDR5 32GB 6000MHz Silver | TeamGroup T-Force De... |
| CORSAIR Dominator Titanium DDR5 32GB 7200MHz Silver | CORSAIR Dominator Ti... |
| Arctic Liquid Freezer III Pro 420 A-RGB Silver | Arctic Liquid Freeze... |
| Kingston FURY Renegade DDR5 32GB 7200MHz Black | Kingston FURY Renega... |
| ... | ... |


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

### Problem 8
Convert customer grade to lowercase and name to uppercase to create a string in `"GRADE: grade - NAME"` format. Example: `"VIP: vip - Kim"`. Return `id`, `display_text`, limited to 10 active customers.

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

        **Result (example):**

| id | display_text |
| ----------: | ---------- |
| 2 | GOLD: gold - Danny Johnson |
| 3 | VIP: vip - Adam Moore |
| 4 | GOLD: gold - Virginia Steele |
| 5 | SILVER: silver - Jared Vazquez |
| 8 | SILVER: silver - Tyler Rodriguez |
| 10 | GOLD: gold - John Stark |
| 12 | GOLD: gold - Michael Velasquez |
| 14 | BRONZE: bronze - Martha Murphy |
| ... | ... |


    === "MySQL"
        ```sql
        SELECT
            id,
            CONCAT(UPPER(grade), ': ', LOWER(grade), ' - ', name) AS display_text
        FROM customers
        WHERE is_active = 1
        LIMIT 10;
        ```

### Problem 9
From orders where `order_number` starts with `'ORD-2024'`, extract the date portion from the middle (characters 5-12, e.g., `20240315`). Return `order_number`, `date_part`, `total_amount`, limited to 10 rows.

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

    **Result (example):**

| order_number | date_part | total_amount |
| ---------- | ---------- | ----------: |
| ORD-20240101-25452 | 20240101 | 337900.0 |
| ORD-20240101-25453 | 20240101 | 160400.0 |
| ORD-20240101-25454 | 20240101 | 117700.0 |
| ORD-20240101-25455 | 20240101 | 42600.0 |
| ORD-20240101-25456 | 20240101 | 1171392.0 |
| ORD-20240101-25457 | 20240101 | 616200.0 |
| ORD-20240101-25458 | 20240101 | 206300.0 |
| ORD-20240101-25459 | 20240101 | 612280.0 |
| ... | ... | ... |


### Problem 10
Find the position of the `@` symbol in product names (0 if not found). Target only products with spaces in their names, return `name`, `space_pos` (first space position), limited to 10 rows.

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

        **Result (example):**

| name | space_pos |
| ---------- | ----------: |
| AMD Ryzen 9 9900X | 4 |
| AMD Ryzen 9 9900X | 4 |
| APC Back-UPS Pro Gaming BGM1500B Black | 4 |
| ASRock B850M Pro RS Black | 7 |
| ASRock B850M Pro RS Silver | 7 |
| ASRock B850M Pro RS White | 7 |
| ASRock B860M Pro RS Silver | 7 |
| ASRock B860M Pro RS White | 7 |
| ... | ... |


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

### Problem 11
Concatenate customer's `name` and `phone`, displaying `'no number'` when phone is NULL. Return `customer_id`, `contact`, limited to 10 rows.

??? success "Answer"
    === "SQLite / PostgreSQL"
        ```sql
        SELECT
            id AS customer_id,
            name || ' — ' || COALESCE(phone, 'no number') AS contact
        FROM customers
        LIMIT 10;
        ```

    === "MySQL"
        ```sql
        SELECT
            id AS customer_id,
            CONCAT(name, ' — ', COALESCE(phone, 'no number')) AS contact
        FROM customers
        LIMIT 10;
        ```


### Problem 12
Format customer ID with 6-digit zero-padding and a `'C-'` prefix to create `customer_code`. Example: ID 42 -> `'C-000042'`. Return `customer_code`, `name`, `grade`, limited to 10 rows.

??? success "Answer"
    === "SQLite"
        ```sql
        SELECT
            'C-' || printf('%06d', id) AS customer_code,
            name,
            grade
        FROM customers
        LIMIT 10;
        ```

    === "MySQL"
        ```sql
        SELECT
            CONCAT('C-', LPAD(id, 6, '0')) AS customer_code,
            name,
            grade
        FROM customers
        LIMIT 10;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            'C-' || LPAD(id::text, 6, '0') AS customer_code,
            name,
            grade
        FROM customers
        LIMIT 10;
        ```


### Problem 13
For each category, concatenate the names of active products in that category with commas into a single row. Return `category_name`, `product_list`, `product_count`, sorted by product count descending, limited to 5 rows.

??? success "Answer"
    === "SQLite"
        ```sql
        SELECT
            cat.name AS category_name,
            GROUP_CONCAT(p.name, ', ') AS product_list,
            COUNT(*) AS product_count
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.is_active = 1
        GROUP BY cat.name
        ORDER BY product_count DESC
        LIMIT 5;
        ```

    === "MySQL"
        ```sql
        SELECT
            cat.name AS category_name,
            GROUP_CONCAT(p.name ORDER BY p.name SEPARATOR ', ') AS product_list,
            COUNT(*) AS product_count
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.is_active = 1
        GROUP BY cat.name
        ORDER BY product_count DESC
        LIMIT 5;
        ```

    === "PostgreSQL"
        ```sql
        SELECT
            cat.name AS category_name,
            STRING_AGG(p.name, ', ' ORDER BY p.name) AS product_list,
            COUNT(*) AS product_count
        FROM products AS p
        INNER JOIN categories AS cat ON p.category_id = cat.id
        WHERE p.is_active = 1
        GROUP BY cat.name
        ORDER BY product_count DESC
        LIMIT 5;
        ```


### Problem 14
Find products whose names contain a model number pattern (letters immediately followed by digits, e.g., `RTX5070`, `DDR5`). Return `name`, `price`, sorted by price descending, limited to 10 rows.

??? success "Answer"
    === "SQLite"
        SQLite does not natively support REGEXP, so GLOB is used instead. Since GLOB character classes match only single characters, it is difficult to express "letter immediately followed by digit" precisely. This approximation finds products containing both letters and digits.

        ```sql
        SELECT name, price
        FROM products
        WHERE name GLOB '*[A-Za-z][0-9]*'
        ORDER BY price DESC
        LIMIT 10;
        ```

    === "MySQL"
        ```sql
        SELECT name, price
        FROM products
        WHERE name REGEXP '[A-Za-z][0-9]'
        ORDER BY price DESC
        LIMIT 10;
        ```

        **Result (example):**

        | name                                   |   price |
        | -------------------------------------- | ------: |
        | ASUS TUF Gaming RTX 5080 화이트           | 3812000 |
        | ASUS Dual RTX 5070 Ti ...              | 2890000 |
        | MSI Radeon RX 9070 XT GAMING X         | 1788500 |
        | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
        | ...                                    |     ... |

    === "PostgreSQL"
        ```sql
        SELECT name, price
        FROM products
        WHERE name ~ '[A-Za-z][0-9]'
        ORDER BY price DESC
        LIMIT 10;
        ```


### Scoring Guide

| Score | Next Step |
|:----:|----------|
| **13-14** | Move on to [Lesson 13: Numeric, Conversion, and Conditional Functions](13-utility-functions.md) |
| **10-12** | Review the explanations for incorrect answers, then proceed |
| **Half or fewer** | Re-read this lesson |
| **3 or fewer** | Start again from [Lesson 11: Date/Time Functions](11-datetime.md) |

**Problem Areas:**

| Area | Problems |
|------|:--------:|
| String concatenation (&#124;&#124; / CONCAT) | 1, 8 |
| SUBSTR + CAST extraction | 2, 9 |
| LENGTH | 3 |
| REPLACE + UPPER/LOWER | 4 |
| LIKE pattern matching | 5 |
| SUBSTR + INSTR parsing | 6, 10 |
| CASE + LENGTH + SUBSTR combination | 7 |
| NULL + string concatenation (COALESCE) | 11 |
| LPAD / printf padding | 12 |
| GROUP_CONCAT / STRING_AGG | 13 |
| REGEXP / GLOB pattern matching | 14 |

---
Next: [Lesson 13: Numeric, Conversion, and Conditional Functions](13-utility-functions.md)
