# DDL/Constraints

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __Tables Used__

    ---

    Hands-on practice creating/modifying/dropping tables (no existing tables referenced)

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __Concepts Covered__

    ---

    `CREATE TABLE`<br>
    `ALTER TABLE`<br>
    `DROP TABLE`<br>
    Constraints (`PRIMARY KEY`<br>
    `NOT NULL`<br>
    `UNIQUE`<br>
    `CHECK`<br>
    `DEFAULT`<br>
    `FOREIGN KEY`)

</div>

---


## Basic (1~5): CREATE TABLE and Constraints


### Problem 1

**Create a basic table.** Create a `temp_memo` table with the following requirements.

- `id`: Integer, auto-increment primary key
- `title`: Text, NOT NULL
- `content`: Text, NULL allowed
- `created_at`: Text, NOT NULL, default to current timestamp


??? tip "Hint"
    Use `INTEGER PRIMARY KEY AUTOINCREMENT` for auto-increment PK and `DEFAULT CURRENT_TIMESTAMP` for the default value.


??? success "Answer"
    ```sql
    CREATE TABLE temp_memo (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        title      TEXT NOT NULL,
        content    TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    -- Verify
    PRAGMA table_info(temp_memo);
    ```

    | cid | name       | type    | notnull | dflt_value        | pk |
    |-----|------------|---------|---------|-------------------|----|
    | 0   | id         | INTEGER | 0       |                   | 1  |
    | 1   | title      | TEXT    | 1       |                   | 0  |
    | 2   | content    | TEXT    | 0       |                   | 0  |
    | 3   | created_at | TEXT    | 1       | CURRENT_TIMESTAMP | 0  |


---


### Problem 2

**Create a table with a UNIQUE constraint.** Create a `temp_tag` table.

- `id`: Integer, auto-increment primary key
- `name`: Text, NOT NULL, UNIQUE


??? tip "Hint"
    Adding `UNIQUE` after the column definition prevents duplicate values in that column.


??? success "Answer"
    ```sql
    CREATE TABLE temp_tag (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );

    -- Insert test
    INSERT INTO temp_tag (name) VALUES ('전자제품');
    INSERT INTO temp_tag (name) VALUES ('주변기기');

    -- Duplicate insert attempt -> error
    -- INSERT INTO temp_tag (name) VALUES ('전자제품');

    SELECT * FROM temp_tag;
    ```

    | id | name     |
    |----|----------|
    | 1  | 전자제품 |
    | 2  | 주변기기 |


---


### Problem 3

**Use CHECK constraints.** Create a `temp_product` table.

- `id`: Integer, auto-increment primary key
- `name`: Text, NOT NULL
- `price`: Real, NOT NULL, must be >= 0
- `stock_qty`: Integer, NOT NULL, must be >= 0, default 0


??? tip "Hint"
    Use `CHECK(price >= 0)` and `CHECK(stock_qty >= 0)` to prevent negative values.


??? success "Answer"
    ```sql
    CREATE TABLE temp_product (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        name      TEXT NOT NULL,
        price     REAL NOT NULL CHECK(price >= 0),
        stock_qty INTEGER NOT NULL DEFAULT 0 CHECK(stock_qty >= 0)
    );

    -- Normal insert
    INSERT INTO temp_product (name, price, stock_qty) VALUES ('키보드', 89000, 50);

    -- CHECK violation test (uncomment to see error)
    -- INSERT INTO temp_product (name, price, stock_qty) VALUES ('마우스', -5000, 10);

    SELECT * FROM temp_product;
    ```

    | id | name   | price | stock_qty |
    |----|--------|-------|-----------|
    | 1  | 키보드 | 89000 | 50        |


---


### Problem 4

**Combine NOT NULL and DEFAULT appropriately.** Create a `temp_customer` table.

- `id`: Integer, auto-increment primary key
- `name`: Text, NOT NULL
- `email`: Text, NOT NULL, UNIQUE
- `grade`: Text, NOT NULL, default `'BRONZE'`, `CHECK(grade IN ('BRONZE','SILVER','GOLD','VIP'))`
- `is_active`: Integer, NOT NULL, default 1


??? tip "Hint"
    Using `DEFAULT 'BRONZE'` with `CHECK(grade IN (...))` means omitting the value inserts `'BRONZE'`, and values outside the allowed list are rejected.


??? success "Answer"
    ```sql
    CREATE TABLE temp_customer (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        name      TEXT NOT NULL,
        email     TEXT NOT NULL UNIQUE,
        grade     TEXT NOT NULL DEFAULT 'BRONZE'
                  CHECK(grade IN ('BRONZE','SILVER','GOLD','VIP')),
        is_active INTEGER NOT NULL DEFAULT 1
    );

    -- grade omitted -> default BRONZE applied
    INSERT INTO temp_customer (name, email) VALUES ('김테스트', 'kim@testmail.kr');

    -- grade specified
    INSERT INTO temp_customer (name, email, grade) VALUES ('이테스트', 'lee@testmail.kr', 'GOLD');

    SELECT * FROM temp_customer;
    ```

    | id | name     | email             | grade  | is_active |
    |----|----------|-------------------|--------|-----------|
    | 1  | 김테스트 | kim@testmail.kr   | BRONZE | 1         |
    | 2  | 이테스트 | lee@testmail.kr   | GOLD   | 1         |


---


### Problem 5

**Create a table with a FOREIGN KEY.** Create a `temp_order` table that references `temp_customer`'s `id`.

- `id`: Integer, auto-increment primary key
- `customer_id`: Integer, NOT NULL, references `temp_customer(id)`
- `total_amount`: Real, NOT NULL, CHECK >= 0
- `ordered_at`: Text, NOT NULL


??? tip "Hint"
    In SQLite, FK enforcement must be enabled with `PRAGMA foreign_keys = ON;` before use. Define FK with `REFERENCES table(column)`.


??? success "Answer"
    ```sql
    -- Enable FK (required per session)
    PRAGMA foreign_keys = ON;

    CREATE TABLE temp_order (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id  INTEGER NOT NULL REFERENCES temp_customer(id),
        total_amount REAL NOT NULL CHECK(total_amount >= 0),
        ordered_at   TEXT NOT NULL
    );

    -- Normal insert (customer_id=1 was created above)
    INSERT INTO temp_order (customer_id, total_amount, ordered_at)
    VALUES (1, 150000, '2025-01-15');

    -- FK violation (non-existent customer) -> error
    -- INSERT INTO temp_order (customer_id, total_amount, ordered_at)
    -- VALUES (999, 50000, '2025-01-15');

    SELECT * FROM temp_order;
    ```

    | id | customer_id | total_amount | ordered_at |
    |----|-------------|--------------|------------|
    | 1  | 1           | 150000       | 2025-01-15 |


---


## Applied (6~10): ALTER TABLE, Composite Keys, ON DELETE


### Problem 6

**Add columns to an existing table.** Add a `brand` column (TEXT, NOT NULL, default `'TBD'`) and a `weight_grams` column (INTEGER, NULL allowed) to `temp_product`.


??? tip "Hint"
    SQLite's `ALTER TABLE ... ADD COLUMN` adds one column at a time. Execute twice.


??? success "Answer"
    ```sql
    ALTER TABLE temp_product ADD COLUMN brand TEXT NOT NULL DEFAULT 'TBD';
    ALTER TABLE temp_product ADD COLUMN weight_grams INTEGER;

    -- Verify
    PRAGMA table_info(temp_product);
    ```

    | cid | name         | type    | notnull | dflt_value | pk |
    |-----|--------------|---------|---------|------------|----|
    | 0   | id           | INTEGER | 0       |            | 1  |
    | 1   | name         | TEXT    | 1       |            | 0  |
    | 2   | price        | REAL    | 1       |            | 0  |
    | 3   | stock_qty    | INTEGER | 1       | 0          | 0  |
    | 4   | brand        | TEXT    | 1       | 'TBD'      | 0  |
    | 5   | weight_grams | INTEGER | 0       |            | 0  |


---


### Problem 7

**Rename a table.** Rename `temp_memo` to `temp_note`. Then verify in the table list.


??? tip "Hint"
    Use `ALTER TABLE old_name RENAME TO new_name`.


??? success "Answer"
    ```sql
    ALTER TABLE temp_memo RENAME TO temp_note;

    -- Verify (temp_memo is gone, temp_note appears)
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%'
    ORDER BY name;
    ```

    | name          |
    |---------------|
    | temp_customer |
    | temp_note     |
    | temp_order    |
    | temp_product  |
    | temp_tag      |


---


### Problem 8

**Experience ON DELETE CASCADE.** Create a `temp_order_item` table where items are automatically deleted when the parent `temp_order` is deleted.

- `id`: Integer, auto-increment primary key
- `order_id`: Integer, NOT NULL, references `temp_order(id)`, ON DELETE CASCADE
- `product_name`: Text, NOT NULL
- `quantity`: Integer, NOT NULL, CHECK > 0


??? tip "Hint"
    `REFERENCES temp_order(id) ON DELETE CASCADE` auto-deletes child rows when the parent is deleted. `PRAGMA foreign_keys = ON` is required.


??? success "Answer"
    ```sql
    PRAGMA foreign_keys = ON;

    CREATE TABLE temp_order_item (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id     INTEGER NOT NULL
                     REFERENCES temp_order(id) ON DELETE CASCADE,
        product_name TEXT NOT NULL,
        quantity     INTEGER NOT NULL CHECK(quantity > 0)
    );

    -- Insert data
    INSERT INTO temp_order_item (order_id, product_name, quantity)
    VALUES (1, '키보드', 2);
    INSERT INTO temp_order_item (order_id, product_name, quantity)
    VALUES (1, '마우스', 1);

    -- Verify insertion
    SELECT * FROM temp_order_item;

    -- Delete parent order -> items auto-deleted
    DELETE FROM temp_order WHERE id = 1;

    -- Verify deletion (should be 0 rows)
    SELECT * FROM temp_order_item;
    ```

    Before deletion:

    | id | order_id | product_name | quantity |
    |----|----------|--------------|----------|
    | 1  | 1        | 키보드       | 2        |
    | 2  | 1        | 마우스       | 1        |

    After deletion: (0 rows)


---


### Problem 9

**Experience ON DELETE SET NULL.** Create a `temp_task` table where the assignee becomes NULL (but the task record is preserved) when the assignee is deleted.

- `id`: Integer, auto-increment primary key
- `title`: Text, NOT NULL
- `assignee_id`: Integer, NULL allowed, references `temp_customer(id)`, ON DELETE SET NULL


??? tip "Hint"
    `ON DELETE SET NULL` changes the child's FK column to NULL when the parent is deleted. The FK column cannot be `NOT NULL`.


??? success "Answer"
    ```sql
    PRAGMA foreign_keys = ON;

    CREATE TABLE temp_task (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        title       TEXT NOT NULL,
        assignee_id INTEGER
                    REFERENCES temp_customer(id) ON DELETE SET NULL
    );

    -- Insert data
    INSERT INTO temp_task (title, assignee_id) VALUES ('재고 확인', 1);
    INSERT INTO temp_task (title, assignee_id) VALUES ('배송 처리', 2);

    SELECT t.id, t.title, t.assignee_id, c.name
    FROM temp_task t
    LEFT JOIN temp_customer c ON t.assignee_id = c.id;

    -- Delete customer 1 (delete related temp_order records first)
    DELETE FROM temp_order_item WHERE order_id IN (SELECT id FROM temp_order WHERE customer_id = 1);
    DELETE FROM temp_order WHERE customer_id = 1;
    DELETE FROM temp_customer WHERE id = 1;

    -- assignee_id is now NULL
    SELECT t.id, t.title, t.assignee_id
    FROM temp_task t;
    ```

    After deletion:

    | id | title     | assignee_id |
    |----|-----------|-------------|
    | 1  | 재고 확인 |             |
    | 2  | 배송 처리 | 2           |


---


### Problem 10

**Use a composite PRIMARY KEY.** Create a product-tag relationship table `temp_product_tag` with (product_id, tag_id) as the composite PK.

- `product_id`: Integer, NOT NULL
- `tag_id`: Integer, NOT NULL
- PRIMARY KEY is (product_id, tag_id)


??? tip "Hint"
    A composite PK (not AUTOINCREMENT) is declared as a table constraint: `PRIMARY KEY (col1, col2)`.


??? success "Answer"
    ```sql
    CREATE TABLE temp_product_tag (
        product_id INTEGER NOT NULL,
        tag_id     INTEGER NOT NULL,
        PRIMARY KEY (product_id, tag_id)
    );

    -- Insert
    INSERT INTO temp_product_tag VALUES (1, 10);
    INSERT INTO temp_product_tag VALUES (1, 20);
    INSERT INTO temp_product_tag VALUES (2, 10);

    -- Duplicate combination insert -> error
    -- INSERT INTO temp_product_tag VALUES (1, 10);

    SELECT * FROM temp_product_tag;
    ```

    | product_id | tag_id |
    |------------|--------|
    | 1          | 10     |
    | 1          | 20     |
    | 2          | 10     |


---


## Advanced (11~15): Design, CTAS, Error Fixing


### Problem 11

**The following CREATE TABLE statement has 3 errors. Find and fix them all.**

```sql
CREATE TABLE temp_employee (
    id INTEGER AUTOINCREMENT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    salary REAL CHECK(salary > 0),
    department TEXT DEFAULT,
    hired_at TEXT NOT NULL
);
```


??? tip "Hint"
    1. Check whether `AUTOINCREMENT` is in the correct position.
    2. If `name` is missing NOT NULL, employees without names are possible.
    3. `DEFAULT` has no default value after it.


??? success "Answer"
    ```sql
    -- 3 errors:
    -- 1) AUTOINCREMENT must come after PRIMARY KEY
    --    -> INTEGER PRIMARY KEY AUTOINCREMENT
    -- 2) name is missing NOT NULL (name should be required)
    -- 3) DEFAULT has no value after it (syntax error)
    --    -> DEFAULT 'Unassigned' or similar

    CREATE TABLE temp_employee (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        email      TEXT UNIQUE,
        salary     REAL CHECK(salary > 0),
        department TEXT DEFAULT '미배정',
        hired_at   TEXT NOT NULL
    );

    -- Test
    INSERT INTO temp_employee (name, hired_at)
    VALUES ('테스트 직원', '2025-01-01');

    SELECT * FROM temp_employee;
    ```

    | id | name        | email | salary | department | hired_at   |
    |----|-------------|-------|--------|------------|------------|
    | 1  | 테스트 직원 |       |        | 미배정     | 2025-01-01 |


---


### Problem 12

**Use CTAS (CREATE TABLE AS SELECT) to create a 2024 order summary table.** Create a `temp_order_summary_2024` table from `orders` with per-customer order count, total amount, and average amount.


??? tip "Hint"
    `CREATE TABLE name AS SELECT ...` saves the SELECT result as a new table. Use `WHERE ordered_at LIKE '2024%'` to filter for 2024.


??? success "Answer"
    ```sql
    CREATE TABLE temp_order_summary_2024 AS
    SELECT
        c.id AS customer_id,
        c.name AS customer_name,
        COUNT(o.id) AS order_count,
        SUM(o.total_amount) AS total_spent,
        ROUND(AVG(o.total_amount)) AS avg_order_amount
    FROM customers c
    INNER JOIN orders o ON c.id = o.customer_id
    WHERE o.ordered_at LIKE '2024%'
    GROUP BY c.id, c.name;

    -- Verify (top 5)
    SELECT * FROM temp_order_summary_2024
    ORDER BY total_spent DESC
    LIMIT 5;
    ```

    | customer_id | customer_name | order_count | total_spent | avg_order_amount |
    |-------------|---------------|-------------|-------------|------------------|
    | ...         | ...           | ...         | ...         | ...              |

    !!! note
        Tables created with CTAS do not copy constraints like PK, FK, or CHECK. Add them separately if needed.


---


### Problem 13

**Compare DELETE vs DROP TABLE vs table recreation.** Delete all data from `temp_tag` while keeping the table structure, and also delete the table itself. Execute each approach.

!!! info "Note"
    SQLite does not have a `TRUNCATE TABLE` command. Use `DELETE FROM` instead. MySQL/PostgreSQL support `TRUNCATE TABLE`, which is faster than DELETE (table reset instead of row-by-row deletion).


??? tip "Hint"
    - Delete data only: `DELETE FROM table;`
    - Delete table: `DROP TABLE table;`
    - Safe delete: `DROP TABLE IF EXISTS table;`


??? success "Answer"
    ```sql
    -- 1) Delete data only (structure preserved)
    DELETE FROM temp_tag;

    -- Table still exists
    SELECT COUNT(*) AS cnt FROM temp_tag;
    -- cnt = 0

    -- 2) Delete the table itself
    DROP TABLE temp_tag;

    -- No longer queryable (error)
    -- SELECT * FROM temp_tag;

    -- 3) Safe delete (no error even if already gone)
    DROP TABLE IF EXISTS temp_tag;
    ```

    !!! tip "TRUNCATE vs DELETE (Other DBs)"
        | Feature | DELETE FROM | TRUNCATE TABLE |
        |---------|------------|----------------|
        | Speed | Slow (row-by-row) | Fast (table reset) |
        | WHERE condition | Supported | Not supported |
        | Transaction rollback | Supported | Varies by DB |
        | Auto-increment reset | No | Yes (MySQL) |
        | SQLite support | Yes | No |


---


### Problem 14

**Design a table from requirements.** Create a `temp_coupon` table satisfying these business requirements.

Requirements:

1. Coupon code must be unique
2. Coupon type must be only `'percent'` or `'fixed'`
3. Discount value must be positive
4. Minimum order amount is optional, but must be >= 0 if set
5. Validity period (start date, end date) is required
6. Active flag defaults to 1 (active)


??? tip "Hint"
    Map each requirement to a constraint: unique -> `UNIQUE`, allowed list -> `CHECK IN`, positive -> `CHECK > 0`, optional -> NULL allowed, required -> `NOT NULL`, default -> `DEFAULT`.


??? success "Answer"
    ```sql
    CREATE TABLE temp_coupon (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        code             TEXT NOT NULL UNIQUE,                          -- Req 1: unique
        type             TEXT NOT NULL CHECK(type IN ('percent','fixed')), -- Req 2: allowed types
        discount_value   REAL NOT NULL CHECK(discount_value > 0),      -- Req 3: positive
        min_order_amount REAL CHECK(min_order_amount >= 0),            -- Req 4: optional, >= 0
        is_active        INTEGER NOT NULL DEFAULT 1,                   -- Req 6: default active
        started_at       TEXT NOT NULL,                                -- Req 5: required
        expired_at       TEXT NOT NULL                                 -- Req 5: required
    );

    -- Test
    INSERT INTO temp_coupon (code, type, discount_value, min_order_amount, started_at, expired_at)
    VALUES ('WELCOME10', 'percent', 10, 50000, '2025-01-01', '2025-12-31');

    INSERT INTO temp_coupon (code, type, discount_value, started_at, expired_at)
    VALUES ('FLAT5000', 'fixed', 5000, '2025-06-01', '2025-06-30');

    SELECT * FROM temp_coupon;
    ```

    | id | code      | type    | discount_value | min_order_amount | is_active | started_at | expired_at |
    |----|-----------|---------|----------------|------------------|-----------|------------|------------|
    | 1  | WELCOME10 | percent | 10             | 50000            | 1         | 2025-01-01 | 2025-12-31 |
    | 2  | FLAT5000  | fixed   | 5000           |                  | 1         | 2025-06-01 | 2025-06-30 |


---


### Problem 15

**Cleanup: Drop all temporary tables created in this exercise.** Query `sqlite_master` for tables starting with `temp_`, then DROP them all.


??? tip "Hint"
    First check the list with `SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'temp_%'`, then delete each with `DROP TABLE IF EXISTS`. Mind FK reference order (delete children first).


??? success "Answer"
    ```sql
    -- 1) Check current temp_ table list
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%'
    ORDER BY name;

    -- 2) Drop in child -> parent order considering FK relationships
    DROP TABLE IF EXISTS temp_order_item;
    DROP TABLE IF EXISTS temp_product_tag;
    DROP TABLE IF EXISTS temp_task;
    DROP TABLE IF EXISTS temp_order;
    DROP TABLE IF EXISTS temp_order_summary_2024;
    DROP TABLE IF EXISTS temp_customer;
    DROP TABLE IF EXISTS temp_product;
    DROP TABLE IF EXISTS temp_employee;
    DROP TABLE IF EXISTS temp_coupon;
    DROP TABLE IF EXISTS temp_note;
    DROP TABLE IF EXISTS temp_tag;

    -- 3) Verify deletion (should be 0 rows)
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%';
    ```

    !!! tip "PostgreSQL SEQUENCE"
        PostgreSQL uses `SERIAL` or `GENERATED ALWAYS AS IDENTITY` for auto-increment. Internally, a sequence object is created and can be controlled directly via `nextval()`, `currval()`, and `setval()`. Unlike SQLite's `AUTOINCREMENT`, sequences are independent objects that can be shared across multiple tables.
