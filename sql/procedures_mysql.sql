-- =============================================
-- MySQL 스토어드 프로시저 예제
-- 전자상거래 테스트 DB용 비즈니스 로직
-- =============================================

DELIMITER //

-- =============================================
-- 프로시저: 고객 등급 일괄 업데이트
-- 학습 포인트: 커서(CURSOR), 조건 분기, UPDATE, 트랜잭션
-- =============================================
CREATE PROCEDURE sp_update_customer_grades()
BEGIN
    DECLARE v_customer_id INT;
    DECLARE v_total DECIMAL(12,2);
    DECLARE v_grade VARCHAR(20);
    DECLARE done INT DEFAULT FALSE;

    DECLARE cur CURSOR FOR
        SELECT c.id,
               COALESCE(SUM(o.total_amount), 0) AS total_spent
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
            AND o.status NOT IN ('cancelled')
            AND o.ordered_at >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        GROUP BY c.id;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    START TRANSACTION;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_customer_id, v_total;
        IF done THEN
            LEAVE read_loop;
        END IF;

        IF v_total >= 5000000 THEN
            SET v_grade = 'VIP';
        ELSEIF v_total >= 2000000 THEN
            SET v_grade = 'GOLD';
        ELSEIF v_total >= 500000 THEN
            SET v_grade = 'SILVER';
        ELSE
            SET v_grade = 'BRONZE';
        END IF;

        UPDATE customers SET grade = v_grade WHERE id = v_customer_id;
    END LOOP;
    CLOSE cur;

    COMMIT;
END //

-- =============================================
-- 프로시저: 주문 생성 (트랜잭션)
-- 학습 포인트: IN/OUT 파라미터, INSERT, 트랜잭션, LAST_INSERT_ID
-- =============================================
CREATE PROCEDURE sp_place_order(
    IN p_customer_id INT,
    IN p_address_id INT,
    IN p_product_ids TEXT,       -- 쉼표 구분: '1,5,12'
    IN p_quantities TEXT,        -- 쉼표 구분: '1,2,1'
    IN p_payment_method VARCHAR(30),
    OUT p_order_id INT,
    OUT p_total_amount DECIMAL(12,2)
)
BEGIN
    DECLARE v_order_number VARCHAR(20);
    DECLARE v_shipping_fee DECIMAL(10,2) DEFAULT 3000;
    DECLARE v_item_total DECIMAL(12,2) DEFAULT 0;
    DECLARE v_product_id INT;
    DECLARE v_quantity INT;
    DECLARE v_price DECIMAL(12,2);
    DECLARE v_idx INT DEFAULT 1;
    DECLARE v_count INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_order_id = -1;
        SET p_total_amount = 0;
    END;

    START TRANSACTION;

    -- 주문번호 생성
    SET v_order_number = CONCAT('ORD-', DATE_FORMAT(NOW(), '%Y%m%d'), '-',
                                LPAD((SELECT COALESCE(MAX(id), 0) + 1 FROM orders), 5, '0'));

    -- 주문 생성 (임시 금액)
    INSERT INTO orders (order_number, customer_id, address_id, status,
                        total_amount, shipping_fee, ordered_at, created_at, updated_at)
    VALUES (v_order_number, p_customer_id, p_address_id, 'pending',
            0, 0, NOW(), NOW(), NOW());

    SET p_order_id = LAST_INSERT_ID();

    -- 아이템 수 계산
    SET v_count = LENGTH(p_product_ids) - LENGTH(REPLACE(p_product_ids, ',', '')) + 1;

    -- 각 아이템 추가
    WHILE v_idx <= v_count DO
        SET v_product_id = CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(p_product_ids, ',', v_idx), ',', -1) AS UNSIGNED);
        SET v_quantity = CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(p_quantities, ',', v_idx), ',', -1) AS UNSIGNED);

        SELECT price INTO v_price FROM products WHERE id = v_product_id;

        INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
        VALUES (p_order_id, v_product_id, v_quantity, v_price, v_price * v_quantity);

        SET v_item_total = v_item_total + (v_price * v_quantity);
        SET v_idx = v_idx + 1;
    END WHILE;

    -- 배송비 계산 (5만원 이상 무료)
    IF v_item_total >= 50000 THEN
        SET v_shipping_fee = 0;
    END IF;

    SET p_total_amount = v_item_total + v_shipping_fee;

    -- 주문 금액 업데이트
    UPDATE orders
    SET total_amount = p_total_amount, shipping_fee = v_shipping_fee
    WHERE id = p_order_id;

    -- 결제 레코드 생성
    INSERT INTO payments (order_id, method, amount, status, created_at)
    VALUES (p_order_id, p_payment_method, p_total_amount, 'pending', NOW());

    COMMIT;
END //

-- =============================================
-- 프로시저: 월별 매출 리포트
-- 학습 포인트: 임시 테이블, 집계, 결과 셋 반환
-- =============================================
CREATE PROCEDURE sp_monthly_report(
    IN p_year INT,
    IN p_month INT
)
BEGIN
    SELECT
        DATE_FORMAT(o.ordered_at, '%Y-%m-%d') AS order_date,
        COUNT(*) AS order_count,
        COUNT(DISTINCT o.customer_id) AS unique_customers,
        CAST(SUM(o.total_amount) AS SIGNED) AS daily_revenue,
        CAST(AVG(o.total_amount) AS SIGNED) AS avg_order_value,
        SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END) AS cancellations,
        SUM(CASE WHEN o.status IN ('return_requested','returned') THEN 1 ELSE 0 END) AS returns
    FROM orders o
    WHERE YEAR(o.ordered_at) = p_year
      AND MONTH(o.ordered_at) = p_month
      AND o.status != 'cancelled'
    GROUP BY DATE_FORMAT(o.ordered_at, '%Y-%m-%d')
    ORDER BY order_date;

    -- 월 요약
    SELECT
        COUNT(*) AS total_orders,
        COUNT(DISTINCT customer_id) AS total_customers,
        CAST(SUM(total_amount) AS SIGNED) AS total_revenue,
        CAST(AVG(total_amount) AS SIGNED) AS avg_order_value,
        MAX(total_amount) AS max_order,
        MIN(total_amount) AS min_order
    FROM orders
    WHERE YEAR(ordered_at) = p_year
      AND MONTH(ordered_at) = p_month
      AND status NOT IN ('cancelled');
END //

-- =============================================
-- 프로시저: 재고 부족 알림
-- 학습 포인트: 조건부 SELECT, 판매 속도 계산
-- =============================================
CREATE PROCEDURE sp_low_stock_alert(
    IN p_threshold INT  -- 재고 기준선 (예: 10)
)
BEGIN
    SELECT
        p.id,
        p.name,
        p.sku,
        p.stock_qty AS current_stock,
        COALESCE(s.avg_daily_sales, 0) AS avg_daily_sales,
        CASE
            WHEN COALESCE(s.avg_daily_sales, 0) > 0
            THEN CAST(p.stock_qty / s.avg_daily_sales AS SIGNED)
            ELSE 999
        END AS days_until_stockout,
        sup.company_name AS supplier
    FROM products p
    JOIN suppliers sup ON p.supplier_id = sup.id
    LEFT JOIN (
        SELECT
            oi.product_id,
            ROUND(COUNT(*) / 30.0, 2) AS avg_daily_sales
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.ordered_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
          AND o.status NOT IN ('cancelled')
        GROUP BY oi.product_id
    ) s ON p.id = s.product_id
    WHERE p.is_active = 1
      AND p.stock_qty <= p_threshold
    ORDER BY p.stock_qty ASC;
END //

-- =============================================
-- 함수: 고객 생애 가치(LTV) 계산
-- 학습 포인트: FUNCTION, RETURNS, 단일 값 반환
-- =============================================
CREATE FUNCTION fn_customer_ltv(p_customer_id INT)
RETURNS DECIMAL(12,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_ltv DECIMAL(12,2);

    SELECT COALESCE(SUM(total_amount), 0) INTO v_ltv
    FROM orders
    WHERE customer_id = p_customer_id
      AND status NOT IN ('cancelled');

    RETURN v_ltv;
END //

-- =============================================
-- 함수: 상품 평균 평점 계산
-- 학습 포인트: FUNCTION, IFNULL, 반올림
-- =============================================
CREATE FUNCTION fn_product_rating(p_product_id INT)
RETURNS DECIMAL(3,1)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_rating DECIMAL(3,1);

    SELECT IFNULL(ROUND(AVG(rating), 1), 0) INTO v_rating
    FROM reviews
    WHERE product_id = p_product_id;

    RETURN v_rating;
END //

DELIMITER ;

-- =============================================
-- 사용 예시
-- =============================================
-- CALL sp_update_customer_grades();
-- CALL sp_place_order(1, 1, '10,20,30', '1,2,1', 'card', @oid, @total);
-- SELECT @oid, @total;
-- CALL sp_monthly_report(2024, 11);
-- CALL sp_low_stock_alert(10);
-- SELECT fn_customer_ltv(42);
-- SELECT id, name, fn_product_rating(id) AS rating FROM products LIMIT 10;
