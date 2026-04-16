# DDL/Constraints

!!! info "Tables"

    `customers` — Customers (grade, points, channel)  

    `orders` — Orders (status, amount, date)  



!!! abstract "Concepts"

    `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`, `PRIMARY KEY`, `NOT NULL`, `UNIQUE`, `CHECK`, `DEFAULT`, `FOREIGN KEY`, `ON DELETE CASCADE`, `ON DELETE SET NULL`



### 1. Create a basic table. Create temp_memo with id (auto-increme


Create a basic table. Create temp_memo with id (auto-increment PK), title (TEXT, NOT NULL), content (TEXT), created_at (TEXT, NOT NULL, default current timestamp).


**Hint 1:** Use `INTEGER PRIMARY KEY AUTOINCREMENT` for auto-increment PK and `DEFAULT CURRENT_TIMESTAMP` for the default.


??? success "Answer"
    ```sql
    CREATE TABLE temp_memo (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        title      TEXT NOT NULL,
        content    TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    PRAGMA table_info(temp_memo);
    ```


---


### 2. Create a temp_tag table with a UNIQUE constraint. id (auto-i


Create a temp_tag table with a UNIQUE constraint. id (auto-increment PK), name (TEXT, NOT NULL, UNIQUE).


**Hint 1:** Adding `UNIQUE` after the column definition prevents duplicate values.


??? success "Answer"
    ```sql
    CREATE TABLE temp_tag (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    
    INSERT INTO temp_tag (name) VALUES ('전자제품');
    INSERT INTO temp_tag (name) VALUES ('주변기기');
    
    SELECT * FROM temp_tag;
    ```


---


### 3. Use CHECK constraints. Create temp_product: id (PK), name (N


Use CHECK constraints. Create temp_product: id (PK), name (NOT NULL), price (NOT NULL, >= 0), stock_qty (NOT NULL, >= 0, default 0).


**Hint 1:** Use `CHECK(price >= 0)` and `CHECK(stock_qty >= 0)` to prevent negative values.


??? success "Answer"
    ```sql
    CREATE TABLE temp_product (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        name      TEXT NOT NULL,
        price     REAL NOT NULL CHECK(price >= 0),
        stock_qty INTEGER NOT NULL DEFAULT 0 CHECK(stock_qty >= 0)
    );
    
    INSERT INTO temp_product (name, price, stock_qty) VALUES ('키보드', 89000, 50);
    
    SELECT * FROM temp_product;
    ```


---


### 4. Create temp_customer combining NOT NULL and DEFAULT. Grade d


Create temp_customer combining NOT NULL and DEFAULT. Grade defaults to 'BRONZE' with CHECK for allowed values.


**Hint 1:** Using `DEFAULT 'BRONZE'` with `CHECK(grade IN (...))` means omitting the value inserts 'BRONZE', and values outside the list are rejected.


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
    
    INSERT INTO temp_customer (name, email) VALUES ('김테스트', 'kim@testmail.kr');
    INSERT INTO temp_customer (name, email, grade) VALUES ('이테스트', 'lee@testmail.kr', 'GOLD');
    
    SELECT * FROM temp_customer;
    ```


---


### 5. Create temp_order with a FOREIGN KEY referencing temp_custom


Create temp_order with a FOREIGN KEY referencing temp_customer's id.


**Hint 1:** In SQLite, FK enforcement must be enabled with `PRAGMA foreign_keys = ON;` before use.


??? success "Answer"
    ```sql
    PRAGMA foreign_keys = ON;
    
    CREATE TABLE temp_order (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id  INTEGER NOT NULL REFERENCES temp_customer(id),
        total_amount REAL NOT NULL CHECK(total_amount >= 0),
        ordered_at   TEXT NOT NULL
    );
    
    INSERT INTO temp_order (customer_id, total_amount, ordered_at)
    VALUES (1, 150000, '2025-01-15');
    
    SELECT * FROM temp_order;
    ```


---


### 6. Add columns to an existing table. Add brand (TEXT, NOT NULL,


Add columns to an existing table. Add brand (TEXT, NOT NULL, default 'TBD') and weight_grams (INTEGER) to temp_product.


**Hint 1:** SQLite's `ALTER TABLE ... ADD COLUMN` adds one column at a time. Execute twice.


??? success "Answer"
    ```sql
    ALTER TABLE temp_product ADD COLUMN brand TEXT NOT NULL DEFAULT '미정';
    ALTER TABLE temp_product ADD COLUMN weight_grams INTEGER;
    
    PRAGMA table_info(temp_product);
    ```


---


### 7. Rename a table. Rename temp_memo to temp_note.


Rename a table. Rename temp_memo to temp_note.


**Hint 1:** Use `ALTER TABLE old_name RENAME TO new_name`.


??? success "Answer"
    ```sql
    ALTER TABLE temp_memo RENAME TO temp_note;
    
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%'
    ORDER BY name;
    ```


---


### 8. Experience ON DELETE CASCADE. Create temp_order_item where i


Experience ON DELETE CASCADE. Create temp_order_item where items are auto-deleted when the parent order is deleted.


**Hint 1:** `REFERENCES temp_order(id) ON DELETE CASCADE` auto-deletes child rows. `PRAGMA foreign_keys = ON` required.


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
    
    INSERT INTO temp_order_item (order_id, product_name, quantity)
    VALUES (1, '키보드', 2);
    INSERT INTO temp_order_item (order_id, product_name, quantity)
    VALUES (1, '마우스', 1);
    
    SELECT * FROM temp_order_item;
    
    DELETE FROM temp_order WHERE id = 1;
    
    SELECT * FROM temp_order_item;
    ```


---


### 9. Experience ON DELETE SET NULL. Create temp_task where the as


Experience ON DELETE SET NULL. Create temp_task where the assignee becomes NULL when deleted.


**Hint 1:** `ON DELETE SET NULL` changes the child's FK column to NULL when parent is deleted. Cannot be used with NOT NULL FK columns.


??? success "Answer"
    ```sql
    PRAGMA foreign_keys = ON;
    
    CREATE TABLE temp_task (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        title       TEXT NOT NULL,
        assignee_id INTEGER
                    REFERENCES temp_customer(id) ON DELETE SET NULL
    );
    
    INSERT INTO temp_task (title, assignee_id) VALUES ('재고 확인', 1);
    INSERT INTO temp_task (title, assignee_id) VALUES ('배송 처리', 2);
    
    SELECT t.id, t.title, t.assignee_id, c.name
    FROM temp_task t
    LEFT JOIN temp_customer c ON t.assignee_id = c.id;
    
    DELETE FROM temp_order_item WHERE order_id IN (SELECT id FROM temp_order WHERE customer_id = 1);
    DELETE FROM temp_order WHERE customer_id = 1;
    DELETE FROM temp_customer WHERE id = 1;
    
    SELECT t.id, t.title, t.assignee_id
    FROM temp_task t;
    ```


---


### 10. Use a composite PRIMARY KEY. Create temp_product_tag with (p


Use a composite PRIMARY KEY. Create temp_product_tag with (product_id, tag_id) as composite PK.


**Hint 1:** A composite PK is declared as a table constraint: `PRIMARY KEY (col1, col2)`.


??? success "Answer"
    ```sql
    CREATE TABLE temp_product_tag (
        product_id INTEGER NOT NULL,
        tag_id     INTEGER NOT NULL,
        PRIMARY KEY (product_id, tag_id)
    );
    
    INSERT INTO temp_product_tag VALUES (1, 10);
    INSERT INTO temp_product_tag VALUES (1, 20);
    INSERT INTO temp_product_tag VALUES (2, 10);
    
    SELECT * FROM temp_product_tag;
    ```


---


### 11. The following CREATE TABLE has 3 errors. Find and fix them a


The following CREATE TABLE has 3 errors. Find and fix them all. (AUTOINCREMENT position, missing NOT NULL on name, missing DEFAULT value)


**Hint 1:** 1. AUTOINCREMENT must come after PRIMARY KEY. 2. name is missing NOT NULL. 3. DEFAULT has no value.


??? success "Answer"
    ```sql
    CREATE TABLE temp_employee (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        email      TEXT UNIQUE,
        salary     REAL CHECK(salary > 0),
        department TEXT DEFAULT '미배정',
        hired_at   TEXT NOT NULL
    );
    
    INSERT INTO temp_employee (name, hired_at)
    VALUES ('테스트 직원', '2025-01-01');
    
    SELECT * FROM temp_employee;
    ```


---


### 12. Use CTAS to create a 2024 order summary table.


Use CTAS to create a 2024 order summary table.


**Hint 1:** `CREATE TABLE name AS SELECT ...` saves the SELECT result as a new table.


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
    
    SELECT * FROM temp_order_summary_2024
    ORDER BY total_spent DESC
    LIMIT 5;
    ```


---


### 13. Compare DELETE vs DROP TABLE vs table recreation. Delete dat


Compare DELETE vs DROP TABLE vs table recreation. Delete data only vs delete the table itself.


**Hint 1:** Data only: `DELETE FROM table;`, Table: `DROP TABLE table;`, Safe: `DROP TABLE IF EXISTS table;`


??? success "Answer"
    ```sql
    DELETE FROM temp_tag;
    
    SELECT COUNT(*) AS cnt FROM temp_tag;
    
    DROP TABLE temp_tag;
    
    DROP TABLE IF EXISTS temp_tag;
    ```


---


### 14. Design a temp_coupon table from requirements. Unique code, t


Design a temp_coupon table from requirements. Unique code, type percent/fixed only, positive discount, optional min order amount, required validity period, default active=1.


**Hint 1:** Map each requirement to a constraint: unique->UNIQUE, allowed list->CHECK IN, positive->CHECK > 0, optional->nullable, required->NOT NULL, default->DEFAULT.


??? success "Answer"
    ```sql
    CREATE TABLE temp_coupon (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        code             TEXT NOT NULL UNIQUE,
        type             TEXT NOT NULL CHECK(type IN ('percent','fixed')),
        discount_value   REAL NOT NULL CHECK(discount_value > 0),
        min_order_amount REAL CHECK(min_order_amount >= 0),
        is_active        INTEGER NOT NULL DEFAULT 1,
        started_at       TEXT NOT NULL,
        expired_at       TEXT NOT NULL
    );
    
    INSERT INTO temp_coupon (code, type, discount_value, min_order_amount, started_at, expired_at)
    VALUES ('WELCOME10', 'percent', 10, 50000, '2025-01-01', '2025-12-31');
    
    INSERT INTO temp_coupon (code, type, discount_value, started_at, expired_at)
    VALUES ('FLAT5000', 'fixed', 5000, '2025-06-01', '2025-06-30');
    
    SELECT * FROM temp_coupon;
    ```


---


### 15. Cleanup: Drop all temporary tables. Mind FK reference order 


Cleanup: Drop all temporary tables. Mind FK reference order — delete children first.


**Hint 1:** Check the list first, then delete each with `DROP TABLE IF EXISTS`. Mind FK reference order (children first).


??? success "Answer"
    ```sql
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%'
    ORDER BY name;
    
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
    
    SELECT name FROM sqlite_master
    WHERE type = 'table' AND name LIKE 'temp_%';
    ```


---
