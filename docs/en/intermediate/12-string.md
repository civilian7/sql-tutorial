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

| order_number       | ordered_at          | order_date | year_month |
| ------------------ | ------------------- | ---------- | ---------- |
| ORD-20160101-00001 | 2016-01-17 03:39:08 | 2016-01-17 | 2016-01    |
| ORD-20160102-00002 | 2016-01-11 05:08:34 | 2016-01-11 | 2016-01    |
| ORD-20160102-00003 | 2016-01-09 15:08:34 | 2016-01-09 | 2016-01    |
| ...                | ...                 | ...        | ...        |

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

| name                                                             | name_length |
| ---------------------------------------------------------------- | ----------: |
| HP EliteBook 840 G10 블랙 [특별 한정판 에디션] 무상 보증 3년 연장 + 전용 파우치 증정 이벤트 |          64 |
| ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장    |          61 |
| ...                                                              | ...         |

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

| name | email_lower       | grade_display |
| ---- | ----------------- | ------------- |
| 정준호  | user1@testmail.kr | BRONZE        |
| 김경수  | user2@testmail.kr | VIP           |
| ...  | ...               | ...           |

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

| status    | status_readable |
| --------- | --------------- |
| cancelled | cancelled       |
| confirmed | confirmed       |
| ...       | ...             |

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

        **Expected result:**

        | customer_id | contact_card                            | grade  |
        | ----------: | --------------------------------------- | ------ |
        |           2 | 김경수 | 020-4423-5167 | user2@testmail.kr | VIP    |
        |           3 | 김민재 | 020-0806-0711 | user3@testmail.kr | VIP    |
        |           4 | 진정자 | 020-9666-8856 | user4@testmail.kr | VIP    |
        |           5 | 이정수 | 020-0239-9503 | user5@testmail.kr | SILVER |
        |           8 | 성민석 | 020-8951-7989 | user8@testmail.kr | BRONZE |
        | ...         | ...                                     | ...    |


        **Expected result:**

        | customer_id | contact_card                            | grade  |
        | ----------: | --------------------------------------- | ------ |
        |           2 | 김경수 | 020-4423-5167 | user2@testmail.kr | VIP    |
        |           3 | 김민재 | 020-0806-0711 | user3@testmail.kr | VIP    |
        |           4 | 진정자 | 020-9666-8856 | user4@testmail.kr | VIP    |
        |           5 | 이정수 | 020-0239-9503 | user5@testmail.kr | SILVER |
        |           8 | 성민석 | 020-8951-7989 | user8@testmail.kr | BRONZE |
        | ...         | ...                                     | ...    |


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

    **Expected result:**

    | order_number       | sequence_no | total_amount |
    | ------------------ | ----------: | -----------: |
    | ORD-20250630-34908 |       34908 |       387900 |
    | ORD-20250630-34907 |       34907 |      4222961 |
    | ORD-20250630-34906 |       34906 |        52400 |
    | ORD-20250630-34905 |       34905 |       152600 |
    | ORD-20250630-34904 |       34904 |      1411900 |
    | ...                | ...         | ...          |


    **Expected result:**

    | order_number       | sequence_no | total_amount |
    | ------------------ | ----------: | -----------: |
    | ORD-20250630-34908 |       34908 |       387900 |
    | ORD-20250630-34907 |       34907 |      4222961 |
    | ORD-20250630-34906 |       34906 |        52400 |
    | ORD-20250630-34905 |       34905 |       152600 |
    | ORD-20250630-34904 |       34904 |      1411900 |
    | ...                | ...         | ...          |


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

    **Expected result:**

    | name | name_length |
    | ---- | ----------: |
    | 정준호  |           3 |
    | 김경수  |           3 |
    | 김민재  |           3 |
    | 진정자  |           3 |
    | 이정수  |           3 |


    **Expected result:**

    | name | name_length |
    | ---- | ----------: |
    | 정준호  |           3 |
    | 김경수  |           3 |
    | 김민재  |           3 |
    | 진정자  |           3 |
    | 이정수  |           3 |


### Exercise 4
Replace underscores with spaces in order `status` values and convert them to uppercase. Show only distinct values. Return the original `status` and `display_status`.

??? success "Answer"
    ```sql
    SELECT DISTINCT
        status,
        UPPER(REPLACE(status, '_', ' ')) AS display_status
    FROM orders;
    ```

    **Expected result:**

    | status    | display_status |
    | --------- | -------------- |
    | cancelled | CANCELLED      |
    | confirmed | CONFIRMED      |
    | delivered | DELIVERED      |
    | paid      | PAID           |
    | pending   | PENDING        |
    | ...       | ...            |


    **Expected result:**

    | status    | display_status |
    | --------- | -------------- |
    | cancelled | CANCELLED      |
    | confirmed | CONFIRMED      |
    | delivered | DELIVERED      |
    | paid      | PAID           |
    | pending   | PENDING        |
    | ...       | ...            |


### Exercise 5
Find products whose name contains the word `'Gaming'`. Return `name` and `price`, sorted by price descending. Use a LIKE pattern.

??? success "Answer"
    ```sql
    SELECT name, price
    FROM products
    WHERE name LIKE '%Gaming%'
    ORDER BY price DESC;
    ```

    **Expected result:**

    | name                                   | price   |
    | -------------------------------------- | ------: |
    | ASUS TUF Gaming RTX 5080 화이트           | 3812000 |
    | MSI Radeon RX 9070 XT GAMING X         | 1788500 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
    | MSI Radeon RX 7900 XTX GAMING X 화이트    | 1478100 |
    | APC Back-UPS Pro Gaming BGM1500B 블랙    |  408800 |


    **Expected result:**

    | name                                   | price   |
    | -------------------------------------- | ------: |
    | ASUS TUF Gaming RTX 5080 화이트           | 3812000 |
    | MSI Radeon RX 9070 XT GAMING X         | 1788500 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | 1744000 |
    | MSI Radeon RX 7900 XTX GAMING X 화이트    | 1478100 |
    | APC Back-UPS Pro Gaming BGM1500B 블랙    |  408800 |


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

        **Expected result:**

        | name | email             | user_id |
        | ---- | ----------------- | ------- |
        | 정준호  | user1@testmail.kr | user1   |
        | 김경수  | user2@testmail.kr | user2   |
        | 김민재  | user3@testmail.kr | user3   |
        | 진정자  | user4@testmail.kr | user4   |
        | 이정수  | user5@testmail.kr | user5   |
        | ...  | ...               | ...     |


        **Expected result:**

        | name | email             | user_id |
        | ---- | ----------------- | ------- |
        | 정준호  | user1@testmail.kr | user1   |
        | 김경수  | user2@testmail.kr | user2   |
        | 김민재  | user3@testmail.kr | user3   |
        | 진정자  | user4@testmail.kr | user4   |
        | 이정수  | user5@testmail.kr | user5   |
        | ...  | ...               | ...     |


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

        **Expected result:**

        | name                                                             | short_name              |
        | ---------------------------------------------------------------- | ----------------------- |
        | HP EliteBook 840 G10 블랙 [특별 한정판 에디션] 무상 보증 3년 연장 + 전용 파우치 증정 이벤트 | HP EliteBook 840 G10... |
        | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장    | ASUS Dual RTX 5070 T... |
        | ASUS ExpertBook B5 [특별 한정판 에디션] RGB 라이팅 탑재, 소프트웨어 커스터마이징 지원      | ASUS ExpertBook B5 [... |
        | ASUS ExpertBook B5 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장       | ASUS ExpertBook B5 [... |
        | TeamGroup T-Force Delta RGB DDR5 32GB 6000MHz 실버                 | TeamGroup T-Force De... |
        | ...                                                              | ...                     |


        **Expected result:**

        | name                                                             | short_name              |
        | ---------------------------------------------------------------- | ----------------------- |
        | HP EliteBook 840 G10 블랙 [특별 한정판 에디션] 무상 보증 3년 연장 + 전용 파우치 증정 이벤트 | HP EliteBook 840 G10... |
        | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장    | ASUS Dual RTX 5070 T... |
        | ASUS ExpertBook B5 [특별 한정판 에디션] RGB 라이팅 탑재, 소프트웨어 커스터마이징 지원      | ASUS ExpertBook B5 [... |
        | ASUS ExpertBook B5 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장       | ASUS ExpertBook B5 [... |
        | TeamGroup T-Force Delta RGB DDR5 32GB 6000MHz 실버                 | TeamGroup T-Force De... |
        | ...                                                              | ...                     |


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

        **Expected result:**

        | id | display_text         |
        | -: | -------------------- |
        |  2 | VIP: vip - 김경수       |
        |  3 | VIP: vip - 김민재       |
        |  4 | VIP: vip - 진정자       |
        |  5 | SILVER: silver - 이정수 |
        |  8 | BRONZE: bronze - 성민석 |
        | ... | ...                  |


        **Expected result:**

        | id | display_text         |
        | -: | -------------------- |
        |  2 | VIP: vip - 김경수       |
        |  3 | VIP: vip - 김민재       |
        |  4 | VIP: vip - 진정자       |
        |  5 | SILVER: silver - 이정수 |
        |  8 | BRONZE: bronze - 성민석 |
        | ... | ...                  |


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

    **Expected result:**

    | order_number       | date_part | total_amount |
    | ------------------ | --------: | -----------: |
    | ORD-20240101-26304 |  20240101 |      3250600 |
    | ORD-20240101-26305 |  20240101 |      1465600 |
    | ORD-20240101-26306 |  20240101 |        82700 |
    | ORD-20240101-26307 |  20240101 |       419600 |
    | ORD-20240101-26308 |  20240101 |      2860850 |
    | ...                | ...       | ...          |


    **Expected result:**

    | order_number       | date_part | total_amount |
    | ------------------ | --------: | -----------: |
    | ORD-20240101-26304 |  20240101 |      3250600 |
    | ORD-20240101-26305 |  20240101 |      1465600 |
    | ORD-20240101-26306 |  20240101 |        82700 |
    | ORD-20240101-26307 |  20240101 |       419600 |
    | ORD-20240101-26308 |  20240101 |      2860850 |
    | ...                | ...       | ...          |


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

        **Expected result:**

        | name                                | space_pos |
        | ----------------------------------- | --------: |
        | AMD Ryzen 9 9900X                   |         4 |
        | AMD Ryzen 9 9900X                   |         4 |
        | APC Back-UPS Pro Gaming BGM1500B 블랙 |         4 |
        | ASRock B850M Pro RS 블랙              |         7 |
        | ASRock B850M Pro RS 실버              |         7 |
        | ...                                 | ...       |


        **Expected result:**

        | name                                | space_pos |
        | ----------------------------------- | --------: |
        | AMD Ryzen 9 9900X                   |         4 |
        | AMD Ryzen 9 9900X                   |         4 |
        | APC Back-UPS Pro Gaming BGM1500B 블랙 |         4 |
        | ASRock B850M Pro RS 블랙              |         7 |
        | ASRock B850M Pro RS 실버              |         7 |
        | ...                                 | ...       |


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
