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
| ORD-20160101-00001 | 2016-01-31 22:16:37 | 2016-01-31 | 2016-01 |
| ORD-20160101-00002 | 2016-01-06 01:15:21 | 2016-01-06 | 2016-01 |
| ORD-20160101-00003 | 2016-01-11 08:08:34 | 2016-01-11 | 2016-01 |
| ORD-20160101-00004 | 2016-01-23 08:32:43 | 2016-01-23 | 2016-01 |
| ORD-20160101-00005 | 2016-01-11 07:08:34 | 2016-01-11 | 2016-01 |
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
| TeamGroup T-Force Delta RGB DDR5 32GB 6000MHz 화이트 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | 89 |
| MSI MAG B850 TOMAHAWK MAX WIFI 화이트 [특별 한정판 에디션] 고급 알루미늄 합금 바디 적용, 프리미엄 패키지 구성 | 77 |
| Microsoft Bluetooth Ergonomic Mouse 실버 [특별 한정판 에디션] 전문가 추천 모델, 업계 최고 성능 인증 획득 | 77 |
| ASUS TUF Gaming RTX 4070 Ti Super 실버 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | 76 |
| be quiet! Shadow Base 800 FX 블랙 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | 71 |
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
| 정준호 | user1@testmail.kr | BRONZE |
| 김경수 | user2@testmail.kr | BRONZE |
| 김민재 | user3@testmail.kr | VIP |
| 진정자 | user4@testmail.kr | GOLD |
| 이정수 | user5@testmail.kr | BRONZE |
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
| 2 | 김경수 | 020-4423-5167 | user2@testmail.kr | BRONZE |
| 3 | 김민재 | 020-0806-0711 | user3@testmail.kr | VIP |
| 4 | 진정자 | 020-9666-8856 | user4@testmail.kr | GOLD |
| 5 | 이정수 | 020-0239-9503 | user5@testmail.kr | BRONZE |
| 8 | 성민석 | 020-8951-7989 | user8@testmail.kr | VIP |
| 10 | 박지훈 | 020-1196-8263 | user10@testmail.kr | GOLD |
| 12 | 장준서 | 020-0083-5468 | user12@testmail.kr | SILVER |
| 14 | 윤순옥 | 020-4730-0267 | user14@testmail.kr | BRONZE |
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
| ORD-20200920-99999 | 99999 | 176300.0 |
| ORD-20220603-199999 | 99999 | 6555400.0 |
| ORD-20240329-299999 | 99999 | 2933700.0 |
| ORD-20251008-399999 | 99999 | 1354900.0 |
| ORD-20200920-99998 | 99998 | 1930300.0 |
| ORD-20220603-199998 | 99998 | 129100.0 |
| ORD-20240329-299998 | 99998 | 107200.0 |
| ORD-20251008-399998 | 99998 | 64800.0 |
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
| 정준호 | 3 |
| 김경수 | 3 |
| 김민재 | 3 |
| 진정자 | 3 |
| 이정수 | 3 |
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
| MSI GeForce RTX 4070 Ti Super GAMING X | 4624100.0 |
| ASUS TUF Gaming A15 화이트 | 4280800.0 |
| 기가바이트 RTX 5080 GAMING OC 화이트 | 4229900.0 |
| ASUS TUF Gaming RTX 5080 화이트 | 3994200.0 |
| ASUS TUF Gaming A15 | 3972700.0 |
| 레노버 IdeaPad Gaming 3 블랙 | 3370800.0 |
| 레노버 IdeaPad Gaming 3 블랙 | 3319400.0 |
| ASUS TUF Gaming RTX 4070 Ti Super 화이트 | 3225400.0 |
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
| 정준호 | user1@testmail.kr | user1 |
| 김경수 | user2@testmail.kr | user2 |
| 김민재 | user3@testmail.kr | user3 |
| 진정자 | user4@testmail.kr | user4 |
| 이정수 | user5@testmail.kr | user5 |
| 김준혁 | user6@testmail.kr | user6 |
| 김명자 | user7@testmail.kr | user7 |
| 성민석 | user8@testmail.kr | user8 |
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
| TeamGroup T-Force Delta RGB DDR5 32GB 6000MHz 화이트 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | TeamGroup T-Force De... |
| MSI MAG B850 TOMAHAWK MAX WIFI 화이트 [특별 한정판 에디션] 고급 알루미늄 합금 바디 적용, 프리미엄 패키지 구성 | MSI MAG B850 TOMAHAW... |
| Microsoft Bluetooth Ergonomic Mouse 실버 [특별 한정판 에디션] 전문가 추천 모델, 업계 최고 성능 인증 획득 | Microsoft Bluetooth ... |
| ASUS TUF Gaming RTX 4070 Ti Super 실버 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | ASUS TUF Gaming RTX ... |
| be quiet! Shadow Base 800 FX 블랙 [특별 한정판 에디션] 저소음 설계, 에너지 효율 1등급, 친환경 포장 | be quiet! Shadow Bas... |
| MSI MPG X870E CARBON WIFI 화이트 [특별 한정판 에디션] 무상 보증 3년 연장 + 전용 파우치 증정 이벤트 | MSI MPG X870E CARBON... |
| Intel Core Ultra 5 245K 화이트 [특별 한정판 에디션] 무상 보증 3년 연장 + 전용 파우치 증정 이벤트 | Intel Core Ultra 5 2... |
| Super Flower Leadex VII 1000W [특별 한정판 에디션] 전문가 추천 모델, 업계 최고 성능 인증 획득 | Super Flower Leadex ... |
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
| 2 | BRONZE: bronze - 김경수 |
| 3 | VIP: vip - 김민재 |
| 4 | GOLD: gold - 진정자 |
| 5 | BRONZE: bronze - 이정수 |
| 8 | VIP: vip - 성민석 |
| 10 | GOLD: gold - 박지훈 |
| 12 | SILVER: silver - 장준서 |
| 14 | BRONZE: bronze - 윤순옥 |
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
| ORD-20240101-286269 | 20240101 | 93000.0 |
| ORD-20240101-286270 | 20240101 | 402200.0 |
| ORD-20240101-286271 | 20240101 | 137800.0 |
| ORD-20240101-286272 | 20240101 | 82500.0 |
| ORD-20240101-286273 | 20240101 | 80700.0 |
| ORD-20240101-286274 | 20240101 | 174400.0 |
| ORD-20240101-286275 | 20240101 | 1462300.0 |
| ORD-20240101-286276 | 20240101 | 694900.0 |
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
| AMD Ryzen 5 9600X | 4 |
| AMD Ryzen 7 7700X | 4 |
| AMD Ryzen 7 7700X 블랙 | 4 |
| AMD Ryzen 7 7700X 블랙 | 4 |
| AMD Ryzen 7 7800X3D | 4 |
| AMD Ryzen 7 7800X3D 실버 | 4 |
| AMD Ryzen 7 9700X 블랙 | 4 |
| AMD Ryzen 7 9800X3D 실버 | 4 |
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
