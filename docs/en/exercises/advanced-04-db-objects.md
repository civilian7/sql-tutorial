# DB Object Design

!!! info "Tables"

    `orders` — Orders (status, amount, date)  

    `order_items` — Order items (qty, unit price)  

    `products` — Products (name, price, stock, brand)  

    `customers` — Customers (grade, points, channel)  

    `categories` — Categories (parent-child hierarchy)  

    `reviews` — Reviews (rating, content)  

    `inventory_transactions` — Inventory (type, quantity)  

    `staff` — Staff (dept, role, manager)  

    `payments` — Payments (method, amount, status)  



!!! abstract "Concepts"

    `CREATE VIEW`, `DROP VIEW`, `CREATE TRIGGER`, `AFTER/BEFORE`, `INSERT/UPDATE/DELETE`, `OLD/NEW`, `Audit Logging`



### 1. Create monthly sales summary views.


View name: `v_monthly_revenue`. Columns: Year Month, Number of Orders, Total Sales, Average Order Amount.
Excludes canceled/returned orders.


**Hint 1:** Define the view as `CREATE VIEW v_monthly_revenue AS SELECT ...`.
You can use `GROUP BY` inside a view.



??? success "Answer"
    ```sql
    CREATE VIEW v_monthly_revenue AS
    SELECT
        SUBSTR(ordered_at, 1, 7)   AS year_month,
        COUNT(*)                    AS order_count,
        ROUND(SUM(total_amount), 0) AS total_revenue,
        ROUND(AVG(total_amount), 0) AS avg_order_value
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY SUBSTR(ordered_at, 1, 7);
    
    -- 뷰 사용
    SELECT *
    FROM v_monthly_revenue
    WHERE year_month LIKE '2024%'
    ORDER BY year_month;
    ```


---


### 2. Create a customer dashboard view


View name: `v_customer_dashboard`. Includes basic information for each customer, total number of orders, total purchase amount, last order date, and number of reviews.


**Hint 1:** Linking orders and reviews with `LEFT JOIN` may cause double counting issues.
It is safer to aggregate each by subquery or CTE and then join.



??? success "Answer"
    ```sql
    CREATE VIEW v_customer_dashboard AS
    WITH order_stats AS (
        SELECT
            customer_id,
            COUNT(*)              AS order_count,
            ROUND(SUM(total_amount), 0) AS total_spent,
            MAX(ordered_at)       AS last_order_date
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY customer_id
    ),
    review_stats AS (
        SELECT
            customer_id,
            COUNT(*) AS review_count
        FROM reviews
        GROUP BY customer_id
    )
    SELECT
        c.id              AS customer_id,
        c.name,
        c.email,
        c.grade,
        c.created_at      AS signup_date,
        COALESCE(os.order_count, 0)   AS order_count,
        COALESCE(os.total_spent, 0)   AS total_spent,
        os.last_order_date,
        COALESCE(rs.review_count, 0)  AS review_count
    FROM customers AS c
    LEFT JOIN order_stats  AS os ON c.id = os.customer_id
    LEFT JOIN review_stats AS rs ON c.id = rs.customer_id;
    
    -- VIP 고객 조회
    SELECT *
    FROM v_customer_dashboard
    WHERE grade = 'VIP'
    ORDER BY total_spent DESC
    LIMIT 10;
    ```


---


### 3. Create product performance views and use them to analyze sales efficiency relative to inventory.


View name: `v_product_performance`. Includes total sales, revenue, current inventory, and average rating for each product.


**Hint 1:** When creating a view, also include products without reviews as `LEFT JOIN`.
When querying a view, you can add derived columns such as "Inventory Turnover" (`units_sold / stock_qty`).



??? success "Answer"
    ```sql
    CREATE VIEW v_product_performance AS
    SELECT
        p.id              AS product_id,
        p.name            AS product_name,
        cat.name          AS category,
        p.price,
        p.stock_qty,
        COALESCE(SUM(oi.quantity), 0) AS total_sold,
        COALESCE(ROUND(SUM(oi.quantity * oi.unit_price), 0), 0) AS total_revenue,
        COALESCE(r.review_count, 0)   AS review_count,
        r.avg_rating
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LEFT JOIN order_items AS oi ON p.id = oi.product_id
    LEFT JOIN orders AS o ON oi.order_id = o.id
        AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    LEFT JOIN (
        SELECT
            product_id,
            COUNT(*) AS review_count,
            ROUND(AVG(rating), 2) AS avg_rating
        FROM reviews
        GROUP BY product_id
    ) AS r ON p.id = r.product_id
    WHERE p.is_active = 1
    GROUP BY p.id, p.name, cat.name, p.price, p.stock_qty,
             r.review_count, r.avg_rating;
    
    -- 재고 대비 판매 효율 분석
    SELECT
        product_name,
        category,
        total_sold,
        stock_qty,
        CASE
            WHEN stock_qty > 0
            THEN ROUND(1.0 * total_sold / stock_qty, 2)
            ELSE NULL
        END AS turnover_ratio,
        total_revenue,
        avg_rating
    FROM v_product_performance
    WHERE total_sold > 0
    ORDER BY turnover_ratio DESC
    LIMIT 10;
    ```


---


### 4. Nested query using views — Find year-on-year growth rate in monthly sales view.


Self-join the `v_monthly_revenue` created earlier.


**Hint 1:** It references `v_monthly_revenue` twice.
JOIN condition: The "month part" of the current month is the same as the "month part" of the previous year, and the year is 1 different.
Extract the month part with `SUBSTR(year_month, 6, 2)` and the year with `SUBSTR(year_month, 1, 4)`.



??? success "Answer"
    ```sql
    SELECT
        curr.year_month,
        curr.total_revenue      AS current_revenue,
        prev.total_revenue      AS prev_year_revenue,
        curr.total_revenue - prev.total_revenue AS diff,
        ROUND(100.0 * (curr.total_revenue - prev.total_revenue)
            / prev.total_revenue, 1) AS yoy_growth_pct
    FROM v_monthly_revenue AS curr
    INNER JOIN v_monthly_revenue AS prev
        ON SUBSTR(curr.year_month, 6, 2) = SUBSTR(prev.year_month, 6, 2)
       AND CAST(SUBSTR(curr.year_month, 1, 4) AS INTEGER)
         = CAST(SUBSTR(prev.year_month, 1, 4) AS INTEGER) + 1
    WHERE curr.year_month LIKE '2024%'
    ORDER BY curr.year_month;
    ```


---


### 5. Check the list of all views that currently exist in the DB.


It uses SQLite's system catalog.


**Hint 1:** In SQLite, all DB object information is stored in the `sqlite_master` table.
Filter by `type = 'view'`.



??? success "Answer"
    ```sql
    SELECT
        name,
        type,
        sql
    FROM sqlite_master
    WHERE type = 'view'
    ORDER BY name;
    ```


    **Result** (top 7 of 18 rows)

    | name | type | sql |
    |---|---|---|
    | v_cart_abandonment | view | CREATE VIEW v_cart_abandonment AS
SEL... |
    | v_category_tree | view | CREATE VIEW v_category_tree AS
WITH R... |
    | v_coupon_effectiveness | view | CREATE VIEW v_coupon_effectiveness AS... |
    | v_customer_rfm | view | CREATE VIEW v_customer_rfm AS
WITH rf... |
    | v_customer_summary | view | CREATE VIEW v_customer_summary AS
SEL... |
    | v_daily_orders | view | CREATE VIEW v_daily_orders AS
SELECT
... |
    | v_hourly_pattern | view | CREATE VIEW v_hourly_pattern AS
SELEC... |


---


### 6. Drop the view and recreate it (DROP + CREATE).


Regenerate the `v_monthly_revenue` view by adding a column for increase/decrease compared to the previous month.


**Hint 1:** SQLite does not support `ALTER VIEW`, so delete and recreate it as `DROP VIEW IF EXISTS`.
You can use the window function `LAG` inside a view definition.



??? success "Answer"
    ```sql
    DROP VIEW IF EXISTS v_monthly_revenue;
    
    CREATE VIEW v_monthly_revenue AS
    WITH base AS (
        SELECT
            SUBSTR(ordered_at, 1, 7)   AS year_month,
            COUNT(*)                    AS order_count,
            ROUND(SUM(total_amount), 0) AS total_revenue,
            ROUND(AVG(total_amount), 0) AS avg_order_value
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    )
    SELECT
        year_month,
        order_count,
        total_revenue,
        avg_order_value,
        LAG(total_revenue, 1) OVER (ORDER BY year_month) AS prev_month_revenue,
        ROUND(100.0 * (total_revenue - LAG(total_revenue, 1) OVER (ORDER BY year_month))
            / LAG(total_revenue, 1) OVER (ORDER BY year_month), 1) AS mom_growth_pct
    FROM base;
    
    -- 개선된 뷰 확인
    SELECT *
    FROM v_monthly_revenue
    WHERE year_month LIKE '2024%'
    ORDER BY year_month;
    ```


---


### 7. Simulate the Materialized View concept in SQLite.


A regular view executes the query every time, but a “materialized view” stores the results in a table.
Save statistics for each product as a table and implement an update pattern.


**Hint 1:** Save the results to a table with `CREATE TABLE mv_product_stats AS SELECT ...`.
On update, run `DROP TABLE IF EXISTS` + `CREATE TABLE AS` again.
Since SQLite does not support native MATERIALIZED VIEW, this pattern is an alternative.



??? success "Answer"
    ```sql
    -- 1. 구체화된 뷰 생성 (테이블로 저장)
    DROP TABLE IF EXISTS mv_product_stats;
    
    CREATE TABLE mv_product_stats AS
    SELECT
        p.id              AS product_id,
        p.name            AS product_name,
        cat.name          AS category,
        COALESCE(SUM(oi.quantity), 0) AS total_sold,
        COALESCE(ROUND(SUM(oi.quantity * oi.unit_price), 0), 0) AS total_revenue,
        (SELECT COUNT(*) FROM reviews AS r WHERE r.product_id = p.id) AS review_count,
        (SELECT ROUND(AVG(rating), 2) FROM reviews AS r WHERE r.product_id = p.id) AS avg_rating,
        DATETIME('now') AS refreshed_at
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    LEFT JOIN order_items AS oi ON p.id = oi.product_id
    LEFT JOIN orders AS o ON oi.order_id = o.id
        AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    WHERE p.is_active = 1
    GROUP BY p.id, p.name, cat.name;
    
    -- 2. 구체화된 뷰 사용 (인덱스 생성 가능 — 일반 뷰와의 차이점)
    CREATE INDEX idx_mv_product_stats_revenue ON mv_product_stats(total_revenue);
    
    SELECT *
    FROM mv_product_stats
    ORDER BY total_revenue DESC
    LIMIT 5;
    ```


---


### 8. Check the list of triggers that currently exist in the DB.


Displays the trigger name, associated table, and definition (SQL).


**Hint 1:** Filter from `sqlite_master` to `type = 'trigger'`.
The `tbl_name` column is the table to which the trigger is attached.



??? success "Answer"
    ```sql
    SELECT
        name       AS trigger_name,
        tbl_name   AS table_name,
        sql        AS definition
    FROM sqlite_master
    WHERE type = 'trigger'
    ORDER BY tbl_name, name;
    ```


    **Result** (5 rows)

    | trigger_name | table_name | definition |
    |---|---|---|
    | trg_customers_updated_at | customers | CREATE TRIGGER trg_customers_updated_... |
    | trg_orders_updated_at | orders | CREATE TRIGGER trg_orders_updated_at
... |
    | trg_product_price_history | products | CREATE TRIGGER trg_product_price_hist... |
    | trg_products_updated_at | products | CREATE TRIGGER trg_products_updated_a... |
    | trg_reviews_updated_at | reviews | CREATE TRIGGER trg_reviews_updated_at... |


---


### 9. Create order status change audit log tables and triggers.


Automatically logs changes to `status` in the `orders` table.


**Hint 1:** First, create the audit log table as `CREATE TABLE`,
to `CREATE TRIGGER ... AFTER UPDATE OF status ON orders WHEN OLD.status != NEW.status`
Record the status before and after the change. `OLD` is the value before the change, and `NEW` is the value after the change.



??? success "Answer"
    ```sql
    -- 1. 감사 로그 테이블 생성
    CREATE TABLE IF NOT EXISTS order_status_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id    INTEGER NOT NULL,
        old_status  TEXT NOT NULL,
        new_status  TEXT NOT NULL,
        changed_at  TEXT NOT NULL DEFAULT (DATETIME('now'))
    );
    
    -- 2. 트리거 생성
    CREATE TRIGGER trg_order_status_change
    AFTER UPDATE OF status ON orders
    WHEN OLD.status != NEW.status
    BEGIN
        INSERT INTO order_status_log (order_id, old_status, new_status)
        VALUES (NEW.id, OLD.status, NEW.status);
    END;
    
    -- 3. 테스트: 주문 상태 변경
    UPDATE orders SET status = 'shipped' WHERE id = 1 AND status = 'preparing';
    
    -- 4. 로그 확인
    SELECT * FROM order_status_log ORDER BY id DESC LIMIT 5;
    ```


---


### 10. Create automatic inventory deduction triggers.


When a new row is inserted in `order_items`, `stock_qty` for that product is automatically deducted.


**Hint 1:** Use `CREATE TRIGGER ... AFTER INSERT ON order_items`.
`UPDATE products SET stock_qty = stock_qty - NEW.quantity WHERE id = NEW.product_id;`



??? success "Answer"
    ```sql
    CREATE TRIGGER trg_stock_deduct
    AFTER INSERT ON order_items
    BEGIN
        UPDATE products
        SET stock_qty = stock_qty - NEW.quantity,
            updated_at = DATETIME('now')
        WHERE id = NEW.product_id;
    END;
    
    -- 테스트: 현재 재고 확인
    SELECT id, name, stock_qty FROM products WHERE id = 1;
    
    -- order_items에 삽입 (실제 운영에서는 주문 프로세스에서 발생)
    -- INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_amount, subtotal)
    -- VALUES (1, 1, 2, 2987500, 0, 5975000);
    
    -- 재고가 2 감소했는지 확인
    -- SELECT id, name, stock_qty FROM products WHERE id = 1;
    ```


---


### 11. Create automatic point accumulation triggers when you write a review.


When a new review is inserted into `reviews`, you will earn 500 points for that customer.
Applies only to purchase reviews verified by the `WHEN NEW.is_verified = 1` condition.


**Hint 1:** You need to perform two actions:
1. Increment `point_balance` in table `customers`
2. Insert accrual record into `point_transactions` table
Multiple SQL statements can be executed in the trigger body.



??? success "Answer"
    ```sql
    CREATE TRIGGER trg_review_point
    AFTER INSERT ON reviews
    WHEN NEW.is_verified = 1
    BEGIN
        -- 1. 포인트 잔액 증가
        UPDATE customers
        SET point_balance = point_balance + 500,
            updated_at = DATETIME('now')
        WHERE id = NEW.customer_id;
    
        -- 2. 포인트 이력 기록
        INSERT INTO point_transactions (
            customer_id, order_id, type, reason, amount,
            balance_after, expires_at, created_at
        )
        VALUES (
            NEW.customer_id,
            NEW.order_id,
            'earn',
            'review',
            500,
            (SELECT point_balance FROM customers WHERE id = NEW.customer_id),
            DATE('now', '+1 year'),
            DATETIME('now')
        );
    END;
    
    -- 트리거 확인
    SELECT name, sql
    FROM sqlite_master
    WHERE type = 'trigger' AND name = 'trg_review_point';
    ```


---


### 12. Create a trigger to automatically record product price change history.


When `price` of `products` is changed, the history is automatically recorded in the `product_prices` table.
Updates `ended_at` in the old price record to the current time and inserts a new price record.


**Hint 1:** Use `AFTER UPDATE OF price ON products WHEN OLD.price != NEW.price`.
Step 1: Update `ended_at` of an existing record (`WHERE product_id = NEW.id AND ended_at IS NULL`).
Step 2: Insert a new record.



??? success "Answer"
    ```sql
    CREATE TRIGGER trg_price_history
    AFTER UPDATE OF price ON products
    WHEN OLD.price != NEW.price
    BEGIN
        -- 1. 이전 가격 레코드 종료
        UPDATE product_prices
        SET ended_at = DATETIME('now')
        WHERE product_id = NEW.id
          AND ended_at IS NULL;
    
        -- 2. 새 가격 레코드 생성
        INSERT INTO product_prices (product_id, price, started_at, change_reason)
        VALUES (NEW.id, NEW.price, DATETIME('now'), 'price_drop');
    END;
    
    -- 테스트: 가격 변경
    -- UPDATE products SET price = 2800000, updated_at = DATETIME('now') WHERE id = 1;
    
    -- 이력 확인
    SELECT *
    FROM product_prices
    WHERE product_id = 1
    ORDER BY started_at DESC
    LIMIT 3;
    ```


---


### 13. Create a delete protection trigger.


Confirmed orders (status = 'confirmed' or 'delivered') cannot be deleted.
When attempting to delete, an error occurs with `RAISE(ABORT, ...)`.


**Hint 1:** Use `BEFORE DELETE ON orders`.
In condition `WHEN OLD.status IN ('confirmed', 'delivered')`
Run `RAISE(ABORT, 'Confirmed orders cannot be deleted.')`.



??? success "Answer"
    ```sql
    CREATE TRIGGER trg_prevent_order_delete
    BEFORE DELETE ON orders
    WHEN OLD.status IN ('confirmed', 'delivered')
    BEGIN
        SELECT RAISE(ABORT, '확정/배송 완료된 주문은 삭제할 수 없습니다.');
    END;
    
    -- 테스트: 확정된 주문 삭제 시도
    -- DELETE FROM orders WHERE id = 100 AND status = 'confirmed';
    -- 결과: Error: 확정/배송 완료된 주문은 삭제할 수 없습니다.
    
    -- 트리거 확인
    SELECT name, sql
    FROM sqlite_master
    WHERE type = 'trigger' AND name = 'trg_prevent_order_delete';
    ```


---


### 14. Practice trigger deletion and conditional regeneration.


Delete the existing `trg_stock_deduct` trigger and recreate it with an improved version that raises an error when out of stock.


**Hint 1:** Delete with `DROP TRIGGER IF EXISTS trg_stock_deduct;`.
The improved trigger uses `BEFORE INSERT`,
If inventory is low, insertion itself is prevented with `RAISE(ABORT, ...)`.



??? success "Answer"
    ```sql
    -- 1. 기존 트리거 삭제
    DROP TRIGGER IF EXISTS trg_stock_deduct;
    
    -- 2. 재고 검증 트리거 (BEFORE)
    CREATE TRIGGER trg_stock_check
    BEFORE INSERT ON order_items
    WHEN (SELECT stock_qty FROM products WHERE id = NEW.product_id) < NEW.quantity
    BEGIN
        SELECT RAISE(ABORT, '재고가 부족합니다.');
    END;
    
    -- 3. 재고 차감 트리거 (AFTER)
    CREATE TRIGGER trg_stock_deduct
    AFTER INSERT ON order_items
    BEGIN
        UPDATE products
        SET stock_qty = stock_qty - NEW.quantity,
            updated_at = DATETIME('now')
        WHERE id = NEW.product_id;
    
        -- 재고 변동 이력 기록
        INSERT INTO inventory_transactions (
            product_id, type, quantity, reference_id, notes, created_at
        )
        VALUES (
            NEW.product_id, 'outbound', -NEW.quantity,
            NEW.order_id, 'order_deduction', DATETIME('now')
        );
    END;
    
    -- 트리거 확인
    SELECT name, tbl_name, sql
    FROM sqlite_master
    WHERE type = 'trigger'
      AND name IN ('trg_stock_check', 'trg_stock_deduct')
    ORDER BY name;
    ```


---


### 15. Check out stored procedure-like functionality in SQLite.


Count the number of all tables, views, triggers, and indexes in the current DB from the system catalog.


**Hint 1:** Returns `COUNT(*)` from `sqlite_master` by `type`.
You can know the number of each type with `GROUP BY type`.



??? success "Answer"
    ```sql
    SELECT
        type,
        COUNT(*) AS object_count
    FROM sqlite_master
    WHERE type IN ('table', 'view', 'trigger', 'index')
    GROUP BY type
    ORDER BY
        CASE type
            WHEN 'table' THEN 1
            WHEN 'view' THEN 2
            WHEN 'index' THEN 3
            WHEN 'trigger' THEN 4
        END;
    ```


    **Result** (4 rows)

    | type | object_count |
    |---|---|
    | table | 31 |
    | view | 18 |
    | index | 72 |
    | trigger | 5 |


---


### 16. Design a customer rating renewal process.


Customer levels are recalculated based on annual purchase amount:
VIP (5 million won or more), GOLD (3 to 5 million won), SILVER (1 to 3 million won), BRONZE (less than 1 million won).


**Hint 1:** Use `CREATE PROCEDURE` in MySQL and `CREATE OR REPLACE PROCEDURE` in PostgreSQL.
Update each customer's rating using a cursor or the UPDATE ... FROM pattern.



??? success "Answer"
    ```sql
    DELIMITER //
    
        CREATE PROCEDURE sp_update_customer_grades(IN p_year INT)
        BEGIN
            -- 1. 연간 구매 금액 기반 등급 갱신
            UPDATE customers AS c
            INNER JOIN (
                SELECT
                    customer_id,
                    SUM(total_amount) AS annual_spent
                FROM orders
                WHERE YEAR(ordered_at) = p_year
                  AND status NOT IN ('cancelled', 'returned', 'return_requested')
                GROUP BY customer_id
            ) AS s ON c.id = s.customer_id
            SET c.grade = CASE
                WHEN s.annual_spent >= 5000000 THEN 'VIP'
                WHEN s.annual_spent >= 3000000 THEN 'GOLD'
                WHEN s.annual_spent >= 1000000 THEN 'SILVER'
                ELSE 'BRONZE'
            END,
            c.updated_at = NOW();
    
            -- 2. 등급 변경 이력 기록
            INSERT INTO customer_grade_history (customer_id, old_grade, new_grade, changed_at, reason)
            SELECT
                c.id, cgh.prev_grade, c.grade, NOW(), 'yearly_review'
            FROM customers AS c
            INNER JOIN (
                SELECT customer_id, grade AS prev_grade
                FROM customer_grade_history
                WHERE (customer_id, changed_at) IN (
                    SELECT customer_id, MAX(changed_at)
                    FROM customer_grade_history
                    GROUP BY customer_id
                )
            ) AS cgh ON c.id = cgh.customer_id
            WHERE c.grade != cgh.prev_grade;
    
            SELECT ROW_COUNT() AS updated_count;
        END //
    
        DELIMITER ;
    
        -- 실행
        CALL sp_update_customer_grades(2024);
    
    CREATE OR REPLACE PROCEDURE sp_update_customer_grades(p_year INT)
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_updated INT;
        BEGIN
            -- 1. 연간 구매 금액 기반 등급 갱신
            UPDATE customers AS c
            SET grade = CASE
                WHEN s.annual_spent >= 5000000 THEN 'VIP'
                WHEN s.annual_spent >= 3000000 THEN 'GOLD'
                WHEN s.annual_spent >= 1000000 THEN 'SILVER'
                ELSE 'BRONZE'
            END,
            updated_at = NOW()
            FROM (
                SELECT
                    customer_id,
                    SUM(total_amount) AS annual_spent
                FROM orders
                WHERE EXTRACT(YEAR FROM ordered_at) = p_year
                  AND status NOT IN ('cancelled', 'returned', 'return_requested')
                GROUP BY customer_id
            ) AS s
            WHERE c.id = s.customer_id;
    
            GET DIAGNOSTICS v_updated = ROW_COUNT;
            RAISE NOTICE '갱신된 고객 수: %', v_updated;
        END;
        $$;
    
        -- 실행
        CALL sp_update_customer_grades(2024);
    ```


---


### 17. Design a month-end settlement procedure.


Calculates a sales summary for a specific month and stores it in a settlement table.


**Hint 1:** It takes the year and month (`p_year_month`) as a parameter.
Aggregate order/payment data and INSERT settlement records.
An error occurs for months in which settlement has already been completed.



??? success "Answer"
    ```sql
    DELIMITER //
    
        CREATE PROCEDURE sp_monthly_settlement(IN p_year_month VARCHAR(7))
        BEGIN
            DECLARE v_exists INT;
    
            -- 중복 정산 검사
            SELECT COUNT(*) INTO v_exists
            FROM monthly_settlements
            WHERE year_month = p_year_month;
    
            IF v_exists > 0 THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = '이미 정산이 완료된 월입니다.';
            END IF;
    
            -- 정산 데이터 삽입
            INSERT INTO monthly_settlements (
                year_month, order_count, total_revenue,
                total_discount, net_revenue, settled_at
            )
            SELECT
                p_year_month,
                COUNT(*),
                SUM(total_amount),
                SUM(discount_amount),
                SUM(total_amount) - SUM(discount_amount),
                NOW()
            FROM orders
            WHERE DATE_FORMAT(ordered_at, '%Y-%m') = p_year_month
              AND status NOT IN ('cancelled', 'returned', 'return_requested');
    
            SELECT * FROM monthly_settlements WHERE year_month = p_year_month;
        END //
    
        DELIMITER ;
    
        CALL sp_monthly_settlement('2024-12');
    
    CREATE OR REPLACE PROCEDURE sp_monthly_settlement(p_year_month TEXT)
        LANGUAGE plpgsql
        AS $$
        BEGIN
            -- 중복 정산 검사
            IF EXISTS (SELECT 1 FROM monthly_settlements WHERE year_month = p_year_month) THEN
                RAISE EXCEPTION '이미 정산이 완료된 월입니다: %', p_year_month;
            END IF;
    
            -- 정산 데이터 삽입
            INSERT INTO monthly_settlements (
                year_month, order_count, total_revenue,
                total_discount, net_revenue, settled_at
            )
            SELECT
                p_year_month,
                COUNT(*),
                SUM(total_amount),
                SUM(discount_amount),
                SUM(total_amount) - SUM(discount_amount),
                NOW()
            FROM orders
            WHERE TO_CHAR(ordered_at, 'YYYY-MM') = p_year_month
              AND status NOT IN ('cancelled', 'returned', 'return_requested');
    
            RAISE NOTICE '정산 완료: %', p_year_month;
        END;
        $$;
    
        CALL sp_monthly_settlement('2024-12');
    ```


---


### 18. Design inventory replenishment procedures.


Find products that are below the safety stock (threshold) and create an automatic order request.


**Hint 1:** It takes the safety stock standard (e.g. 20 units) as a parameter.
Search for out-of-stock products and INSERT them into the ordering table.
Replenishment quantity is calculated as “average monthly sales x 2”.



??? success "Answer"
    ```sql
    DELIMITER //
    
        CREATE PROCEDURE sp_restock_check(IN p_threshold INT)
        BEGIN
            -- 재고 부족 상품 + 권장 발주 수량
            SELECT
                p.id            AS product_id,
                p.name          AS product_name,
                p.stock_qty     AS current_stock,
                p_threshold     AS safety_stock,
                COALESCE(ROUND(AVG(monthly_sold) * 2), 50) AS recommended_qty,
                s.company_name  AS supplier
            FROM products AS p
            INNER JOIN suppliers AS s ON p.supplier_id = s.id
            LEFT JOIN (
                SELECT
                    oi.product_id,
                    DATE_FORMAT(o.ordered_at, '%Y-%m') AS ym,
                    SUM(oi.quantity) AS monthly_sold
                FROM order_items AS oi
                INNER JOIN orders AS o ON oi.order_id = o.id
                WHERE o.ordered_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
                  AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
                GROUP BY oi.product_id, DATE_FORMAT(o.ordered_at, '%Y-%m')
            ) AS ms ON p.id = ms.product_id
            WHERE p.is_active = 1
              AND p.stock_qty <= p_threshold
            GROUP BY p.id, p.name, p.stock_qty, s.company_name
            ORDER BY p.stock_qty ASC;
        END //
    
        DELIMITER ;
    
        CALL sp_restock_check(20);
    
    CREATE OR REPLACE PROCEDURE sp_restock_check(p_threshold INT)
        LANGUAGE plpgsql
        AS $$
        DECLARE
            rec RECORD;
        BEGIN
            FOR rec IN
                SELECT
                    p.id AS product_id,
                    p.name AS product_name,
                    p.stock_qty AS current_stock,
                    COALESCE(ROUND(AVG(ms.monthly_sold) * 2), 50) AS recommended_qty,
                    s.company_name AS supplier
                FROM products AS p
                INNER JOIN suppliers AS s ON p.supplier_id = s.id
                LEFT JOIN (
                    SELECT
                        oi.product_id,
                        TO_CHAR(o.ordered_at, 'YYYY-MM') AS ym,
                        SUM(oi.quantity) AS monthly_sold
                    FROM order_items AS oi
                    INNER JOIN orders AS o ON oi.order_id = o.id
                    WHERE o.ordered_at >= NOW() - INTERVAL '6 months'
                      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
                    GROUP BY oi.product_id, TO_CHAR(o.ordered_at, 'YYYY-MM')
                ) AS ms ON p.id = ms.product_id
                WHERE p.is_active = 1
                  AND p.stock_qty <= p_threshold
                GROUP BY p.id, p.name, p.stock_qty, s.company_name
                ORDER BY p.stock_qty ASC
            LOOP
                RAISE NOTICE '발주 필요: % (재고: %, 권장: %)',
                    rec.product_name, rec.current_stock, rec.recommended_qty;
            END LOOP;
        END;
        $$;
    
        CALL sp_restock_check(20);
    ```


---


### 19. Design a customer activity summary function.


Takes a specific customer ID and returns a comprehensive activity summary (orders/reviews/points/CS) for that customer as JSON.


**Hint 1:** Use `CREATE FUNCTION ... RETURNS JSON` in MySQL and `RETURNS JSONB` in PostgreSQL.
Each indicator is obtained as a subquery and combined into `JSON_OBJECT`/`jsonb_build_object`.



??? success "Answer"
    ```sql
    DELIMITER //
    
        CREATE FUNCTION fn_customer_summary(p_customer_id INT)
        RETURNS JSON
        DETERMINISTIC
        READS SQL DATA
        BEGIN
            DECLARE v_result JSON;
    
            SELECT JSON_OBJECT(
                'customer_id', c.id,
                'name', c.name,
                'grade', c.grade,
                'order_count', COALESCE(os.cnt, 0),
                'total_spent', COALESCE(os.total, 0),
                'review_count', COALESCE(rs.cnt, 0),
                'avg_rating_given', COALESCE(rs.avg_r, 0),
                'point_balance', c.point_balance,
                'complaint_count', COALESCE(cs.cnt, 0)
            ) INTO v_result
            FROM customers AS c
            LEFT JOIN (
                SELECT customer_id, COUNT(*) AS cnt, SUM(total_amount) AS total
                FROM orders
                WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
                GROUP BY customer_id
            ) AS os ON c.id = os.customer_id
            LEFT JOIN (
                SELECT customer_id, COUNT(*) AS cnt, AVG(rating) AS avg_r
                FROM reviews GROUP BY customer_id
            ) AS rs ON c.id = rs.customer_id
            LEFT JOIN (
                SELECT customer_id, COUNT(*) AS cnt
                FROM complaints GROUP BY customer_id
            ) AS cs ON c.id = cs.customer_id
            WHERE c.id = p_customer_id;
    
            RETURN v_result;
        END //
    
        DELIMITER ;
    
        SELECT fn_customer_summary(1);
    
    CREATE OR REPLACE FUNCTION fn_customer_summary(p_customer_id INT)
        RETURNS JSONB
        LANGUAGE plpgsql
        STABLE
        AS $$
        DECLARE
            v_result JSONB;
        BEGIN
            SELECT jsonb_build_object(
                'customer_id', c.id,
                'name', c.name,
                'grade', c.grade,
                'order_count', COALESCE(os.cnt, 0),
                'total_spent', COALESCE(os.total, 0),
                'review_count', COALESCE(rs.cnt, 0),
                'avg_rating_given', COALESCE(ROUND(rs.avg_r, 2), 0),
                'point_balance', c.point_balance,
                'complaint_count', COALESCE(cs.cnt, 0)
            ) INTO v_result
            FROM customers AS c
            LEFT JOIN (
                SELECT customer_id, COUNT(*) AS cnt, SUM(total_amount) AS total
                FROM orders
                WHERE status NOT IN ('cancelled', 'returned', 'return_requested')
                GROUP BY customer_id
            ) AS os ON c.id = os.customer_id
            LEFT JOIN (
                SELECT customer_id, COUNT(*) AS cnt, AVG(rating) AS avg_r
                FROM reviews GROUP BY customer_id
            ) AS rs ON c.id = rs.customer_id
            LEFT JOIN (
                SELECT customer_id, COUNT(*) AS cnt
                FROM complaints GROUP BY customer_id
            ) AS cs ON c.id = cs.customer_id
            WHERE c.id = p_customer_id;
    
            RETURN v_result;
        END;
        $$;
    
        SELECT fn_customer_summary(1);
    ```


---


### 20. Design transaction-based order processing procedures.


The entire process of order creation (Create order record -> Create order item -> Deduct inventory -> Create payment -> Earn points)
Encapsulate it in one procedure. If there is an intermediate failure, there is a full rollback.


**Hint 1:** Use `START TRANSACTION ... COMMIT` in MySQL and `BEGIN ... COMMIT` in PostgreSQL.
If an error occurs, cancel entirely with `ROLLBACK`.
Utilizes MySQL's `DECLARE ... HANDLER FOR SQLEXCEPTION` and PostgreSQL's `EXCEPTION WHEN` blocks.



??? success "Answer"
    ```sql
    DELIMITER //
    
        CREATE PROCEDURE sp_create_order(
            IN p_customer_id INT,
            IN p_product_id INT,
            IN p_quantity INT,
            IN p_payment_method VARCHAR(20)
        )
        BEGIN
            DECLARE v_price REAL;
            DECLARE v_stock INT;
            DECLARE v_order_id INT;
            DECLARE v_total REAL;
            DECLARE v_order_number VARCHAR(20);
    
            DECLARE EXIT HANDLER FOR SQLEXCEPTION
            BEGIN
                ROLLBACK;
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = '주문 처리 중 오류가 발생했습니다.';
            END;
    
            START TRANSACTION;
    
            -- 1. 상품 정보 & 재고 확인
            SELECT price, stock_qty INTO v_price, v_stock
            FROM products WHERE id = p_product_id FOR UPDATE;
    
            IF v_stock < p_quantity THEN
                SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = '재고가 부족합니다.';
            END IF;
    
            -- 2. 주문 생성
            SET v_total = v_price * p_quantity;
            SET v_order_number = CONCAT('ORD-',
                DATE_FORMAT(NOW(), '%Y%m%d'), '-',
                LPAD(FLOOR(RAND() * 99999), 5, '0'));
    
            INSERT INTO orders (
                order_number, customer_id, address_id, status,
                total_amount, discount_amount, shipping_fee,
                ordered_at, created_at, updated_at
            ) VALUES (
                v_order_number, p_customer_id,
                (SELECT id FROM customer_addresses
                 WHERE customer_id = p_customer_id AND is_default = 1 LIMIT 1),
                'paid', v_total, 0,
                CASE WHEN v_total >= 50000 THEN 0 ELSE 3000 END,
                NOW(), NOW(), NOW()
            );
    
            SET v_order_id = LAST_INSERT_ID();
    
            -- 3. 주문 항목 생성
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
            VALUES (v_order_id, p_product_id, p_quantity, v_price, v_total);
    
            -- 4. 재고 차감
            UPDATE products
            SET stock_qty = stock_qty - p_quantity, updated_at = NOW()
            WHERE id = p_product_id;
    
            -- 5. 결제 생성
            INSERT INTO payments (order_id, method, amount, status, paid_at, created_at)
            VALUES (v_order_id, p_payment_method, v_total, 'completed', NOW(), NOW());
    
            COMMIT;
    
            SELECT v_order_id AS order_id, v_order_number AS order_number,
                   v_total AS total_amount, '주문 완료' AS message;
        END //
    
        DELIMITER ;
    
        CALL sp_create_order(1, 10, 2, 'card');
    
    CREATE OR REPLACE PROCEDURE sp_create_order(
            p_customer_id INT,
            p_product_id INT,
            p_quantity INT,
            p_payment_method TEXT
        )
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_price NUMERIC;
            v_stock INT;
            v_order_id INT;
            v_total NUMERIC;
            v_order_number TEXT;
        BEGIN
            -- 1. 상품 정보 & 재고 확인 (행 잠금)
            SELECT price, stock_qty INTO v_price, v_stock
            FROM products WHERE id = p_product_id FOR UPDATE;
    
            IF v_stock < p_quantity THEN
                RAISE EXCEPTION '재고가 부족합니다. (현재: %, 요청: %)', v_stock, p_quantity;
            END IF;
    
            -- 2. 주문 생성
            v_total := v_price * p_quantity;
            v_order_number := 'ORD-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-'
                || LPAD(FLOOR(RANDOM() * 99999)::TEXT, 5, '0');
    
            INSERT INTO orders (
                order_number, customer_id, address_id, status,
                total_amount, discount_amount, shipping_fee,
                ordered_at, created_at, updated_at
            ) VALUES (
                v_order_number, p_customer_id,
                (SELECT id FROM customer_addresses
                 WHERE customer_id = p_customer_id AND is_default = TRUE LIMIT 1),
                'paid', v_total, 0,
                CASE WHEN v_total >= 50000 THEN 0 ELSE 3000 END,
                NOW(), NOW(), NOW()
            )
            RETURNING id INTO v_order_id;
    
            -- 3. 주문 항목 생성
            INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
            VALUES (v_order_id, p_product_id, p_quantity, v_price, v_total);
    
            -- 4. 재고 차감
            UPDATE products
            SET stock_qty = stock_qty - p_quantity, updated_at = NOW()
            WHERE id = p_product_id;
    
            -- 5. 결제 생성
            INSERT INTO payments (order_id, method, amount, status, paid_at, created_at)
            VALUES (v_order_id, p_payment_method, v_total, 'completed', NOW(), NOW());
    
            RAISE NOTICE '주문 완료: % (금액: %)', v_order_number, v_total;
        END;
        $$;
    
        CALL sp_create_order(1, 10, 2, 'card');
    ```


---
