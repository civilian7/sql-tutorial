# DB 객체 설계

!!! info "사용 테이블"

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `categories` — 카테고리 (부모-자식 계층)  

    `reviews` — 리뷰 (평점, 내용)  

    `inventory_transactions` — 재고 입출고 (유형, 수량)  

    `staff` — 직원 (부서, 역할, 관리자)  

    `payments` — 결제 (방법, 금액, 상태)  



!!! abstract "학습 범위"

    `CREATE VIEW`, `DROP VIEW`, `CREATE TRIGGER`, `AFTER/BEFORE`, `INSERT/UPDATE/DELETE`, `OLD/NEW`, `Audit Logging`



### 1. 월별 매출 요약 뷰를 생성하세요.


뷰 이름: `v_monthly_revenue`. 칼럼: 년월, 주문 수, 총 매출, 평균 주문 금액.
취소/반품 주문은 제외합니다.


**힌트 1:** `CREATE VIEW v_monthly_revenue AS SELECT ...`로 뷰를 정의합니다.
뷰 내부에서 `GROUP BY`를 사용할 수 있습니다.



??? success "정답"
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


### 2. 고객 대시보드 뷰를 생성하세요.


뷰 이름: `v_customer_dashboard`. 고객별 기본 정보, 총 주문 수, 총 구매 금액, 마지막 주문일, 리뷰 수를 포함합니다.


**힌트 1:** `LEFT JOIN`으로 주문과 리뷰를 연결하면 중복 카운트 문제가 생길 수 있습니다.
서브쿼리나 CTE로 각각 집계한 뒤 JOIN하는 것이 안전합니다.



??? success "정답"
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


### 3. 상품 성과 뷰를 생성하고, 이 뷰를 이용해 재고 대비 판매 효율을 분석하세요.


뷰 이름: `v_product_performance`. 상품별 총 판매량, 매출, 현재 재고, 평균 평점을 포함합니다.


**힌트 1:** 뷰 생성 시 `LEFT JOIN`으로 리뷰가 없는 상품도 포함합니다.
뷰를 조회할 때 "재고 회전율"(`units_sold / stock_qty`) 같은 파생 칼럼을 추가할 수 있습니다.



??? success "정답"
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


### 4. 뷰를 활용한 중첩 쿼리 — 월별 매출 뷰에서 전년 동월 대비 성장률을 구하세요.


앞서 생성한 `v_monthly_revenue`를 셀프 조인합니다.


**힌트 1:** `v_monthly_revenue`를 두 번 참조합니다.
JOIN 조건: 현재 월의 "월 부분"이 전년의 "월 부분"과 같고, 연도가 1 차이.
`SUBSTR(year_month, 6, 2)`로 월 부분, `SUBSTR(year_month, 1, 4)`로 연도를 추출합니다.



??? success "정답"
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


### 5. 현재 DB에 존재하는 모든 뷰 목록을 조회하세요.


SQLite의 시스템 카탈로그를 사용합니다.


**힌트 1:** SQLite에서는 `sqlite_master` 테이블에 모든 DB 객체 정보가 저장됩니다.
`type = 'view'`로 필터링합니다.



??? success "정답"
    ```sql
    SELECT
        name,
        type,
        sql
    FROM sqlite_master
    WHERE type = 'view'
    ORDER BY name;
    ```


    **실행 결과** (총 18행 중 상위 7행)

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


### 6. 뷰를 삭제하고 재생성하세요 (DROP + CREATE).


`v_monthly_revenue` 뷰에 전월 대비 증감률 칼럼을 추가하여 재생성합니다.


**힌트 1:** SQLite는 `ALTER VIEW`를 지원하지 않으므로, `DROP VIEW IF EXISTS`로 삭제 후 다시 생성합니다.
윈도우 함수 `LAG`를 뷰 정의 내부에서 사용할 수 있습니다.



??? success "정답"
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


### 7. Materialized View 개념을 SQLite에서 시뮬레이션하세요.


일반 뷰는 매번 쿼리를 실행하지만, "구체화된 뷰"는 결과를 테이블로 저장합니다.
상품별 통계를 테이블로 저장하고, 갱신하는 패턴을 구현하세요.


**힌트 1:** `CREATE TABLE mv_product_stats AS SELECT ...`로 결과를 테이블에 저장합니다.
갱신 시 `DROP TABLE IF EXISTS` + `CREATE TABLE AS`를 다시 실행합니다.
SQLite는 네이티브 MATERIALIZED VIEW를 지원하지 않으므로 이 패턴이 대안입니다.



??? success "정답"
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


### 8. 현재 DB에 존재하는 트리거 목록을 조회하세요.


트리거 이름과 연결된 테이블, 그리고 정의(SQL)를 표시합니다.


**힌트 1:** `sqlite_master`에서 `type = 'trigger'`로 필터링합니다.
`tbl_name` 칼럼이 트리거가 연결된 테이블입니다.



??? success "정답"
    ```sql
    SELECT
        name       AS trigger_name,
        tbl_name   AS table_name,
        sql        AS definition
    FROM sqlite_master
    WHERE type = 'trigger'
    ORDER BY tbl_name, name;
    ```


    **실행 결과** (5행)

    | trigger_name | table_name | definition |
    |---|---|---|
    | trg_customers_updated_at | customers | CREATE TRIGGER trg_customers_updated_... |
    | trg_orders_updated_at | orders | CREATE TRIGGER trg_orders_updated_at
... |
    | trg_product_price_history | products | CREATE TRIGGER trg_product_price_hist... |
    | trg_products_updated_at | products | CREATE TRIGGER trg_products_updated_a... |
    | trg_reviews_updated_at | reviews | CREATE TRIGGER trg_reviews_updated_at... |


---


### 9. 주문 상태 변경 감사 로그 테이블과 트리거를 생성하세요.


`orders` 테이블의 `status`가 변경될 때 자동으로 로그를 기록합니다.


**힌트 1:** 먼저 감사 로그 테이블을 `CREATE TABLE`로 만들고,
`CREATE TRIGGER ... AFTER UPDATE OF status ON orders WHEN OLD.status != NEW.status`로
변경 전/후 상태를 기록합니다. `OLD`는 변경 전, `NEW`는 변경 후 값입니다.



??? success "정답"
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


### 10. 재고 자동 차감 트리거를 생성하세요.


`order_items`에 새 행이 삽입되면, 해당 상품의 `stock_qty`를 자동으로 차감합니다.


**힌트 1:** `CREATE TRIGGER ... AFTER INSERT ON order_items`를 사용합니다.
`UPDATE products SET stock_qty = stock_qty - NEW.quantity WHERE id = NEW.product_id;`



??? success "정답"
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


### 11. 리뷰 작성 시 자동 포인트 적립 트리거를 생성하세요.


`reviews`에 새 리뷰가 삽입되면, 해당 고객에게 500 포인트를 적립합니다.
`WHEN NEW.is_verified = 1` 조건으로 검증된 구매 리뷰에만 적용합니다.


**힌트 1:** 두 가지 동작을 수행해야 합니다:
1. `customers` 테이블의 `point_balance` 증가
2. `point_transactions` 테이블에 적립 기록 삽입
트리거 본문에서 여러 SQL 문을 실행할 수 있습니다.



??? success "정답"
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


### 12. 상품 가격 변경 이력 자동 기록 트리거를 생성하세요.


`products`의 `price`가 변경되면 `product_prices` 테이블에 자동으로 이력을 기록합니다.
이전 가격 레코드의 `ended_at`을 현재 시각으로 업데이트하고, 새 가격 레코드를 삽입합니다.


**힌트 1:** `AFTER UPDATE OF price ON products WHEN OLD.price != NEW.price`를 사용합니다.
1단계: 기존 레코드의 `ended_at`을 업데이트 (`WHERE product_id = NEW.id AND ended_at IS NULL`).
2단계: 새 레코드 삽입.



??? success "정답"
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


### 13. 삭제 방지 트리거를 생성하세요.


확정된 주문(status = 'confirmed' 또는 'delivered')은 삭제할 수 없도록 합니다.
삭제 시도 시 `RAISE(ABORT, ...)`로 에러를 발생시킵니다.


**힌트 1:** `BEFORE DELETE ON orders`를 사용합니다.
`WHEN OLD.status IN ('confirmed', 'delivered')` 조건에서
`RAISE(ABORT, '확정된 주문은 삭제할 수 없습니다.')`를 실행합니다.



??? success "정답"
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


### 14. 트리거 삭제와 조건부 재생성을 연습하세요.


기존 `trg_stock_deduct` 트리거를 삭제하고, 재고 부족 시 에러를 발생시키는 개선된 버전으로 재생성합니다.


**힌트 1:** `DROP TRIGGER IF EXISTS trg_stock_deduct;`로 삭제합니다.
개선된 트리거에서는 `BEFORE INSERT`를 사용하여,
재고가 부족하면 `RAISE(ABORT, ...)`로 삽입 자체를 방지합니다.



??? success "정답"
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


### 15. SQLite에서 저장 프로시저와 유사한 기능을 확인하세요.


시스템 카탈로그에서 현재 DB의 모든 테이블, 뷰, 트리거, 인덱스 수를 집계하세요.


**힌트 1:** `sqlite_master`에서 `type`별로 `COUNT(*)`를 구합니다.
`GROUP BY type`으로 유형별 개수를 알 수 있습니다.



??? success "정답"
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


    **실행 결과** (4행)

    | type | object_count |
    |---|---|
    | table | 33 |
    | view | 18 |
    | index | 73 |
    | trigger | 5 |


---


### 16. 고객 등급 갱신 프로시저를 설계하세요.


연간 구매 금액에 따라 고객 등급을 재산정합니다:
VIP (500만원 이상), GOLD (300~500만원), SILVER (100~300만원), BRONZE (100만원 미만).


**힌트 1:** MySQL에서는 `CREATE PROCEDURE`, PostgreSQL에서는 `CREATE OR REPLACE PROCEDURE`를 사용합니다.
커서나 UPDATE ... FROM 패턴으로 각 고객의 등급을 갱신합니다.



??? success "정답"
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


### 17. 월말 정산 프로시저를 설계하세요.


특정 월의 매출 요약을 계산하여 정산 테이블에 저장합니다.


**힌트 1:** 매개변수로 연월(`p_year_month`)을 받습니다.
주문/결제 데이터를 집계하여 정산 레코드를 INSERT합니다.
이미 정산이 완료된 월은 에러를 발생시킵니다.



??? success "정답"
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


### 18. 재고 보충 프로시저를 설계하세요.


안전 재고(threshold) 이하인 상품을 찾아 자동 발주 요청을 생성합니다.


**힌트 1:** 안전 재고 기준(예: 20개)을 매개변수로 받습니다.
재고 부족 상품을 조회하여 발주 테이블에 INSERT합니다.
보충 수량은 "평균 월 판매량 x 2"로 계산합니다.



??? success "정답"
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


### 19. 고객 활동 요약 함수를 설계하세요.


특정 고객 ID를 받아 해당 고객의 종합 활동 요약(주문/리뷰/포인트/CS)을 JSON으로 반환합니다.


**힌트 1:** MySQL에서는 `CREATE FUNCTION ... RETURNS JSON`, PostgreSQL에서는 `RETURNS JSONB`를 사용합니다.
각 지표를 서브쿼리로 구하고 `JSON_OBJECT`/`jsonb_build_object`로 합칩니다.



??? success "정답"
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


### 20. 트랜잭션 기반 주문 처리 프로시저를 설계하세요.


주문 생성의 전체 프로세스(주문 레코드 생성 -> 주문 항목 생성 -> 재고 차감 -> 결제 생성 -> 포인트 적립)를
하나의 프로시저로 캡슐화합니다. 중간에 실패하면 전체 롤백합니다.


**힌트 1:** MySQL에서는 `START TRANSACTION ... COMMIT`, PostgreSQL에서는 `BEGIN ... COMMIT`을 사용합니다.
에러 발생 시 `ROLLBACK`으로 전체 취소합니다.
MySQL의 `DECLARE ... HANDLER FOR SQLEXCEPTION`, PostgreSQL의 `EXCEPTION WHEN` 블록을 활용합니다.



??? success "정답"
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
