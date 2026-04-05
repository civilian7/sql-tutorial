# 14강: INSERT, UPDATE, DELETE

DML(Data Manipulation Language, 데이터 조작 언어) 문은 테이블의 데이터를 변경합니다. `SELECT`와 달리 이 문장들은 영구적으로 반영됩니다 — `UPDATE`나 `DELETE`를 실행하기 전에 `WHERE` 절을 반드시 다시 확인하세요.

> **안전 수칙:** `UPDATE`나 `DELETE`를 실행하기 전에, 동일한 `WHERE` 조건으로 먼저 `SELECT`를 실행하여 영향받을 행을 정확히 확인하세요.

## INSERT INTO

### 단일 행 삽입

컬럼 이름을 명시적으로 나열하세요 — 쿼리가 자기 문서화되고, 테이블 구조 변경에도 안전합니다.

```sql
-- 새 상품 추가
INSERT INTO products (sku, name, category_id, supplier_id, price, stock_qty, is_active, created_at, updated_at)
VALUES (
    'SKU-TEST-001',
    '테스트 기계식 키보드',
    9,          -- Keyboards 카테고리 ID
    1,          -- 공급업체 ID
    129.99,
    50,
    1,
    datetime('now'),
    datetime('now')
);
```

실행 후 확인:
```sql
SELECT * FROM products WHERE sku = 'SKU-TEST-001';
```

### 여러 행 한 번에 삽입

```sql
-- 여러 쿠폰 코드 한 번에 추가
INSERT INTO coupons (code, discount_type, discount_value, min_order_amount, is_active, expires_at)
VALUES
    ('SAVE10', 'percentage', 10, 50.00,  1, '2025-12-31'),
    ('FLAT20', 'fixed',      20, 100.00, 1, '2025-06-30'),
    ('VIP50',  'percentage', 50, 200.00, 1, '2025-03-31');
```

### SELECT를 활용한 INSERT

다른 테이블에서 데이터를 복사하거나 오래된 레코드를 아카이브할 때 사용합니다.

```sql
-- (가정) 기존 상품을 기반으로 리퍼비시 상품 추가
INSERT INTO products (sku, name, category_id, supplier_id, price, stock_qty, is_active, created_at, updated_at)
SELECT
    'SKU-' || CAST(id + 10000 AS TEXT),
    name || ' (리퍼비시)',
    category_id,
    supplier_id,
    ROUND(price * 0.7, 2),
    10,
    1,
    datetime('now'),
    datetime('now')
FROM products
WHERE sku = 'SKU-0001';
```

## UPDATE SET

### 특정 행 업데이트

```sql
-- 카테고리 3의 모든 활성 상품 가격 15% 인상
UPDATE products
SET
    price      = ROUND(price * 1.15, 2),
    updated_at = datetime('now')
WHERE category_id = 3
  AND is_active = 1;
```

> 실행 전 확인: `SELECT id, name, price FROM products WHERE category_id = 3 AND is_active = 1;`

### 단일 행 업데이트

```sql
-- 수동 검토 후 고객 등급 변경
UPDATE customers
SET
    grade      = 'GOLD',
    updated_at = datetime('now')
WHERE id = 1042;
```

### 서브쿼리를 활용한 UPDATE

```sql
-- 한 번도 주문되지 않은 상품 비활성화
UPDATE products
SET
    is_active  = 0,
    updated_at = datetime('now')
WHERE id NOT IN (
    SELECT DISTINCT product_id FROM order_items
)
  AND is_active = 1;
```

## DELETE FROM

### 특정 행 삭제

```sql
-- 3년 이상 된 취소 주문 삭제 (아카이빙 목적)
DELETE FROM orders
WHERE status = 'cancelled'
  AND cancelled_at < DATE('now', '-3 years');
```

> 실행 전 확인: `SELECT COUNT(*) FROM orders WHERE status = 'cancelled' AND cancelled_at < DATE('now', '-3 years');`

### 서브쿼리를 활용한 DELETE

```sql
-- 더 이상 존재하지 않는 상품의 위시리스트 항목 삭제
DELETE FROM wishlists
WHERE product_id NOT IN (
    SELECT id FROM products
);
```

## 트랜잭션 — 모두 성공하거나 모두 취소하거나

관련된 DML 문들을 트랜잭션으로 묶으면 모두 성공하거나 모두 롤백됩니다.

```sql
BEGIN TRANSACTION;

-- 1단계: 재고 차감
UPDATE products
SET stock_qty = stock_qty - 2,
    updated_at = datetime('now')
WHERE id = 5;

-- 2단계: 재고 거래 내역 기록
INSERT INTO inventory_transactions (product_id, change_qty, reason, created_at)
VALUES (5, -2, 'manual_adjustment', datetime('now'));

-- 모두 정상이면:
COMMIT;

-- 문제가 생겼다면:
-- ROLLBACK;
```

## 자주 하는 실수

| 실수 | 결과 | 예방법 |
|------|------|--------|
| `WHERE` 없이 `UPDATE table SET col = val` | 모든 행이 업데이트됨 | 항상 먼저 `SELECT`로 확인 |
| `WHERE` 없이 `DELETE FROM table` | 모든 행이 삭제됨 | 트랜잭션 사용; 먼저 COUNT 확인 |
| `updated_at` 누락 | 감사 추적 정보가 낡아짐 | 모든 UPDATE에 `updated_at = datetime('now')` 포함 |
| 중복 기본 키 삽입 | 제약 조건 오류 | `INSERT OR IGNORE` 또는 `INSERT OR REPLACE` 사용 |

## 연습 문제

### 연습 1
공급업체가 납품 가격을 변경했습니다. `supplier_id = 7`인 모든 활성 상품의 `price`를 8% 인상하고 `updated_at`도 갱신하세요. 먼저 어떤 행이 변경될지 확인하는 `SELECT`를 작성하고, 그 다음 `UPDATE`를 작성하세요.

??? success "정답"
    ```sql
    -- 먼저 확인
    SELECT id, name, price, ROUND(price * 1.08, 2) AS new_price
    FROM products
    WHERE supplier_id = 7 AND is_active = 1;

    -- 그 다음 업데이트
    UPDATE products
    SET
        price      = ROUND(price * 1.08, 2),
        updated_at = datetime('now')
    WHERE supplier_id = 7
      AND is_active = 1;
    ```

### 연습 2
현장 등록 신규 고객 레코드를 삽입하세요. 사용 데이터: name `'김민준'`, email `'k.minjun@testmail.kr'`, phone `'020-0199-7823'`, grade `'BRONZE'`, `point_balance = 0`, `is_active = 1`, `created_at`과 `updated_at` 모두 현재 시각으로 설정하세요.

??? success "정답"
    ```sql
    INSERT INTO customers (name, email, phone, grade, point_balance, is_active, created_at, updated_at)
    VALUES (
        '김민준',
        'k.minjun@testmail.kr',
        '020-0199-7823',
        'BRONZE',
        0,
        1,
        datetime('now'),
        datetime('now')
    );
    ```

---
다음: [15강: 윈도우 함수](../advanced/15-window.md)
