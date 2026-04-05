-- =============================================
-- PostgreSQL 스토어드 프로시저/함수 예제
-- 전자상거래 테스트 DB용 비즈니스 로직
-- =============================================

-- =============================================
-- 프로시저: 고객 등급 일괄 업데이트
-- 학습 포인트: PL/pgSQL, FOR 루프, UPDATE, CTE 활용
-- =============================================
CREATE OR REPLACE PROCEDURE sp_update_customer_grades()
LANGUAGE plpgsql
AS $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN
        SELECT c.id,
               COALESCE(SUM(o.total_amount), 0) AS total_spent
        FROM customers c
        LEFT JOIN orders o ON c.id = o.customer_id
            AND o.status NOT IN ('cancelled')
            AND o.ordered_at >= CURRENT_DATE - INTERVAL '1 year'
        GROUP BY c.id
    LOOP
        UPDATE customers
        SET grade = CASE
            WHEN rec.total_spent >= 5000000 THEN 'VIP'
            WHEN rec.total_spent >= 2000000 THEN 'GOLD'
            WHEN rec.total_spent >= 500000 THEN 'SILVER'
            ELSE 'BRONZE'
        END,
        updated_at = NOW()
        WHERE id = rec.id;
    END LOOP;
END;
$$;

-- =============================================
-- 함수: 주문 생성 (트랜잭션, RETURNS 주문ID)
-- 학습 포인트: RETURNS, ARRAY 파라미터, UNNEST, FOR 루프
-- =============================================
CREATE OR REPLACE FUNCTION fn_place_order(
    p_customer_id INT,
    p_address_id INT,
    p_product_ids INT[],          -- ARRAY: '{1,5,12}'
    p_quantities INT[],           -- ARRAY: '{1,2,1}'
    p_payment_method VARCHAR(30)
)
RETURNS TABLE(order_id INT, total_amount NUMERIC)
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_id INT;
    v_order_number VARCHAR(20);
    v_item_total NUMERIC(12,2) := 0;
    v_shipping_fee NUMERIC(10,2) := 3000;
    v_price NUMERIC(12,2);
    v_total NUMERIC(12,2);
    i INT;
BEGIN
    -- 주문번호 생성
    v_order_number := 'ORD-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' ||
                      LPAD((SELECT COALESCE(MAX(id), 0) + 1 FROM orders)::TEXT, 5, '0');

    -- 주문 생성
    INSERT INTO orders (order_number, customer_id, address_id, status,
                        total_amount, shipping_fee, ordered_at, created_at, updated_at)
    VALUES (v_order_number, p_customer_id, p_address_id, 'pending',
            0, 0, NOW(), NOW(), NOW())
    RETURNING id INTO v_order_id;

    -- 아이템 추가
    FOR i IN 1..array_length(p_product_ids, 1) LOOP
        SELECT price INTO v_price FROM products WHERE id = p_product_ids[i];

        INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
        VALUES (v_order_id, p_product_ids[i], p_quantities[i], v_price, v_price * p_quantities[i]);

        v_item_total := v_item_total + (v_price * p_quantities[i]);
    END LOOP;

    -- 배송비 (5만원 이상 무료)
    IF v_item_total >= 50000 THEN
        v_shipping_fee := 0;
    END IF;

    v_total := v_item_total + v_shipping_fee;

    -- 주문 금액 업데이트
    UPDATE orders SET total_amount = v_total, shipping_fee = v_shipping_fee
    WHERE id = v_order_id;

    -- 결제 레코드
    INSERT INTO payments (order_id, method, amount, status, created_at)
    VALUES (v_order_id, p_payment_method, v_total, 'pending', NOW());

    RETURN QUERY SELECT v_order_id, v_total;
END;
$$;

-- =============================================
-- 함수: 월별 매출 리포트 (TABLE 반환)
-- 학습 포인트: RETURNS TABLE, 날짜 처리, 집계
-- =============================================
CREATE OR REPLACE FUNCTION fn_monthly_report(p_year INT, p_month INT)
RETURNS TABLE(
    order_date DATE,
    order_count BIGINT,
    unique_customers BIGINT,
    daily_revenue NUMERIC,
    avg_order_value NUMERIC,
    cancellations BIGINT,
    return_count BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.ordered_at::DATE,
        COUNT(*)::BIGINT,
        COUNT(DISTINCT o.customer_id)::BIGINT,
        SUM(o.total_amount)::NUMERIC,
        AVG(o.total_amount)::NUMERIC,
        SUM(CASE WHEN o.status = 'cancelled' THEN 1 ELSE 0 END)::BIGINT,
        SUM(CASE WHEN o.status IN ('return_requested','returned') THEN 1 ELSE 0 END)::BIGINT
    FROM orders o
    WHERE EXTRACT(YEAR FROM o.ordered_at::DATE) = p_year
      AND EXTRACT(MONTH FROM o.ordered_at::DATE) = p_month
    GROUP BY o.ordered_at::DATE
    ORDER BY o.ordered_at::DATE;
END;
$$;

-- =============================================
-- 함수: 재고 부족 알림
-- 학습 포인트: RETURNS TABLE, lateral join, 판매 속도
-- =============================================
CREATE OR REPLACE FUNCTION fn_low_stock_alert(p_threshold INT DEFAULT 10)
RETURNS TABLE(
    product_id INT,
    product_name TEXT,
    sku TEXT,
    current_stock INT,
    avg_daily_sales NUMERIC,
    days_until_stockout INT,
    supplier_name TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.name::TEXT,
        p.sku::TEXT,
        p.stock_qty,
        COALESCE(s.avg_daily, 0)::NUMERIC,
        CASE
            WHEN COALESCE(s.avg_daily, 0) > 0
            THEN (p.stock_qty / s.avg_daily)::INT
            ELSE 999
        END,
        sup.company_name::TEXT
    FROM products p
    JOIN suppliers sup ON p.supplier_id = sup.id
    LEFT JOIN LATERAL (
        SELECT ROUND(COUNT(*)::NUMERIC / 30, 2) AS avg_daily
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE oi.product_id = p.id
          AND o.ordered_at::DATE >= CURRENT_DATE - 30
          AND o.status NOT IN ('cancelled')
    ) s ON TRUE
    WHERE p.is_active = 1
      AND p.stock_qty <= p_threshold
    ORDER BY p.stock_qty;
END;
$$;

-- =============================================
-- 함수: 고객 LTV (생애 가치)
-- 학습 포인트: 단순 FUNCTION, RETURNS NUMERIC
-- =============================================
CREATE OR REPLACE FUNCTION fn_customer_ltv(p_customer_id INT)
RETURNS NUMERIC
LANGUAGE SQL
STABLE
AS $$
    SELECT COALESCE(SUM(total_amount), 0)
    FROM orders
    WHERE customer_id = p_customer_id
      AND status NOT IN ('cancelled');
$$;

-- =============================================
-- 함수: 상품 평균 평점
-- =============================================
CREATE OR REPLACE FUNCTION fn_product_rating(p_product_id INT)
RETURNS NUMERIC(3,1)
LANGUAGE SQL
STABLE
AS $$
    SELECT COALESCE(ROUND(AVG(rating)::NUMERIC, 1), 0)
    FROM reviews
    WHERE product_id = p_product_id;
$$;

-- =============================================
-- 트리거 함수: updated_at 자동 갱신
-- 학습 포인트: 트리거 함수, NEW/OLD, RETURNS TRIGGER
-- =============================================
CREATE OR REPLACE FUNCTION fn_update_timestamp()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- 여러 테이블에 트리거 적용
CREATE TRIGGER trg_orders_updated BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

CREATE TRIGGER trg_products_updated BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

CREATE TRIGGER trg_customers_updated BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

CREATE TRIGGER trg_shipping_updated BEFORE UPDATE ON shipping
    FOR EACH ROW EXECUTE FUNCTION fn_update_timestamp();

-- =============================================
-- 사용 예시
-- =============================================
-- CALL sp_update_customer_grades();
-- SELECT * FROM fn_place_order(1, 1, '{10,20}', '{1,2}', 'card');
-- SELECT * FROM fn_monthly_report(2024, 11);
-- SELECT * FROM fn_low_stock_alert(10);
-- SELECT fn_customer_ltv(42);
-- SELECT id, name, fn_product_rating(id) FROM products LIMIT 10;
