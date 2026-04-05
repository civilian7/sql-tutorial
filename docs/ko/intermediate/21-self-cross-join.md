# 21강: SELF JOIN과 CROSS JOIN

지금까지 서로 다른 테이블 간의 JOIN을 배웠습니다. 이 강에서는 **같은 테이블을 자기 자신과 결합**하는 SELF JOIN과, **모든 행의 조합**을 만드는 CROSS JOIN을 다룹니다. 두 기법 모두 실무에서 자주 등장하며, 특히 계층 구조와 비교 분석에 필수적입니다.

## SELF JOIN — 같은 테이블끼리 결합

SELF JOIN은 특별한 문법이 아닙니다. 같은 테이블에 서로 다른 별칭을 붙여 JOIN하면 됩니다.

### 카테고리 계층 구조 조회

`categories` 테이블은 `parent_id`로 자기 자신을 참조합니다. SELF JOIN으로 부모-자식 관계를 펼칠 수 있습니다.

```sql
-- 카테고리의 부모-자식 관계 조회
SELECT
    child.id,
    child.name       AS category,
    child.depth,
    parent.name      AS parent_category
FROM categories AS child
LEFT JOIN categories AS parent ON child.parent_id = parent.id
ORDER BY child.depth, child.sort_order;
```

**결과:**

| id | category | depth | parent_category |
|----|----------|-------|-----------------|
| 1 | 데스크톱 PC | 0 | (NULL) |
| 5 | 노트북 | 0 | (NULL) |
| 10 | 모니터 | 0 | (NULL) |
| 2 | 완제품 | 1 | 데스크톱 PC |
| 6 | 일반 노트북 | 1 | 노트북 |
| 7 | 게이밍 노트북 | 1 | 노트북 |
| ... | | | |

최상위 카테고리(`depth=0`)는 `parent_id`가 NULL이므로 `parent_category`도 NULL입니다. `LEFT JOIN`을 사용하여 이런 행도 결과에 포함합니다.

### 대분류-소분류 경로 만들기

SELF JOIN으로 부모(대분류) → 자식(소분류) 전체 경로를 만들 수 있습니다.

```sql
SELECT
    parent.name AS top_category,
    child.name  AS sub_category,
    parent.name || ' > ' || child.name AS full_path
FROM categories AS child
INNER JOIN categories AS parent ON child.parent_id = parent.id
WHERE child.depth = 1
ORDER BY parent.sort_order, child.sort_order;
```

**결과:**

| top_category | sub_category | full_path |
|--------------|--------------|-----------|
| 데스크톱 PC | 완제품 | 데스크톱 PC > 완제품 |
| 데스크톱 PC | 조립PC | 데스크톱 PC > 조립PC |
| 노트북 | 일반 노트북 | 노트북 > 일반 노트북 |
| 노트북 | 게이밍 노트북 | 노트북 > 게이밍 노트북 |
| ... | | |

> **팁:** 계층 깊이가 고정되어 있을 때는 SELF JOIN이 간결합니다. 깊이가 가변적이면 16강의 재귀 CTE를 사용하세요.

### 같은 카테고리 내 상품 비교

같은 카테고리의 상품끼리 가격을 비교하려면 `products` 테이블을 자기 자신과 JOIN합니다.

```sql
-- 같은 카테고리에서 가격 차이가 가장 큰 상품 쌍 찾기
SELECT
    p1.name AS product_a,
    p2.name AS product_b,
    p1.price AS price_a,
    p2.price AS price_b,
    ABS(p1.price - p2.price) AS price_diff
FROM products AS p1
INNER JOIN products AS p2
    ON p1.category_id = p2.category_id
   AND p1.id < p2.id  -- 중복 쌍 방지 (A-B만, B-A는 제외)
ORDER BY price_diff DESC
LIMIT 10;
```

`p1.id < p2.id` 조건이 핵심입니다. 이 조건이 없으면 (A, B)와 (B, A)가 모두 나오고, (A, A) 자기 자신과의 쌍도 포함됩니다.

---

## CROSS JOIN — 모든 조합 생성

`CROSS JOIN`은 왼쪽 테이블의 모든 행과 오른쪽 테이블의 모든 행을 결합합니다. 결과 행 수 = 왼쪽 행 수 × 오른쪽 행 수. ON 조건이 없습니다.

### 월-카테고리 매트릭스

매출 보고서에서 "데이터가 없는 월"도 표시해야 할 때, CROSS JOIN으로 빈 프레임을 먼저 만들고 실제 데이터를 LEFT JOIN합니다.

```sql
-- 2024년 12개월 × 대분류 카테고리 매트릭스
WITH months AS (
    SELECT '2024-01' AS m UNION ALL SELECT '2024-02'
    UNION ALL SELECT '2024-03' UNION ALL SELECT '2024-04'
    UNION ALL SELECT '2024-05' UNION ALL SELECT '2024-06'
    UNION ALL SELECT '2024-07' UNION ALL SELECT '2024-08'
    UNION ALL SELECT '2024-09' UNION ALL SELECT '2024-10'
    UNION ALL SELECT '2024-11' UNION ALL SELECT '2024-12'
),
top_categories AS (
    SELECT id, name FROM categories WHERE depth = 0
),
monthly_sales AS (
    SELECT
        SUBSTR(o.ordered_at, 1, 7) AS year_month,
        COALESCE(parent.id, cat.id) AS category_id,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
    FROM order_items AS oi
    INNER JOIN orders     AS o      ON oi.order_id   = o.id
    INNER JOIN products   AS p      ON oi.product_id = p.id
    INNER JOIN categories AS cat    ON p.category_id = cat.id
    LEFT  JOIN categories AS parent ON cat.parent_id = parent.id
    WHERE o.ordered_at LIKE '2024%'
      AND o.status NOT IN ('cancelled', 'returned', 'return_requested')
    GROUP BY SUBSTR(o.ordered_at, 1, 7), COALESCE(parent.id, cat.id)
)
SELECT
    m.m AS year_month,
    tc.name AS category,
    COALESCE(ms.revenue, 0) AS revenue
FROM months AS m
CROSS JOIN top_categories AS tc
LEFT JOIN monthly_sales AS ms
    ON m.m = ms.year_month AND tc.id = ms.category_id
ORDER BY m.m, tc.name;
```

CROSS JOIN으로 12 × N 행의 완전한 매트릭스를 만든 후, LEFT JOIN으로 실제 매출을 연결합니다. 매출이 없는 셀은 `COALESCE`로 0이 됩니다.

### 전체 매출 대비 비율 계산

CROSS JOIN의 또 다른 활용: 전체 합계를 모든 행에 붙여서 비율을 계산합니다.

```sql
-- 각 결제 수단이 전체 매출에서 차지하는 비율
SELECT
    p.method,
    COUNT(*)              AS tx_count,
    ROUND(SUM(p.amount), 2) AS total_amount,
    ROUND(100.0 * SUM(p.amount) / gt.grand_total, 1) AS pct
FROM payments AS p
CROSS JOIN (
    SELECT SUM(amount) AS grand_total
    FROM payments
    WHERE status = 'completed'
) AS gt
WHERE p.status = 'completed'
GROUP BY p.method, gt.grand_total
ORDER BY total_amount DESC;
```

> **주의:** CROSS JOIN은 강력하지만, 큰 테이블끼리 CROSS JOIN하면 행 수가 폭발합니다. 반드시 한쪽 또는 양쪽이 소규모 결과 집합일 때만 사용하세요.

---

## 연습 문제

### 연습 1: 같은 공급업체의 상품 쌍

같은 공급업체가 공급하는 상품 쌍을 찾아, 가격 차이와 함께 표시하세요. 중복 쌍은 제거합니다.

??? success "정답"
    ```sql
    SELECT
        s.company_name AS supplier,
        p1.name AS product_a,
        p2.name AS product_b,
        p1.price AS price_a,
        p2.price AS price_b,
        ABS(p1.price - p2.price) AS price_diff
    FROM products AS p1
    INNER JOIN products AS p2
        ON p1.supplier_id = p2.supplier_id
       AND p1.id < p2.id
    INNER JOIN suppliers AS s ON p1.supplier_id = s.id
    ORDER BY price_diff DESC
    LIMIT 10;
    ```

### 연습 2: 배송지 여러 개인 고객

같은 고객이 서로 다른 주소로 주문한 경우를 찾으세요. (`customer_addresses` 테이블 SELF JOIN)

??? success "정답"
    ```sql
    SELECT
        c.name,
        a1.address1 AS address_1,
        a2.address1 AS address_2
    FROM customer_addresses AS a1
    INNER JOIN customer_addresses AS a2
        ON a1.customer_id = a2.customer_id
       AND a1.id < a2.id
       AND a1.address1 <> a2.address1
    INNER JOIN customers AS c ON a1.customer_id = c.id
    GROUP BY c.id, c.name, a1.address1, a2.address1
    ORDER BY c.name
    LIMIT 15;
    ```

### 연습 3: 월-공급업체 CROSS JOIN 보고서

2024년 각 월과 각 공급업체의 조합에 대해, 해당 월의 입고 수량을 보여주세요. 입고가 없는 셀은 0으로 표시합니다.

??? success "정답"
    ```sql
    WITH months AS (
        SELECT '2024-01' AS m UNION ALL SELECT '2024-02'
        UNION ALL SELECT '2024-03' UNION ALL SELECT '2024-04'
        UNION ALL SELECT '2024-05' UNION ALL SELECT '2024-06'
        UNION ALL SELECT '2024-07' UNION ALL SELECT '2024-08'
        UNION ALL SELECT '2024-09' UNION ALL SELECT '2024-10'
        UNION ALL SELECT '2024-11' UNION ALL SELECT '2024-12'
    ),
    supplier_inbound AS (
        SELECT
            SUBSTR(it.created_at, 1, 7) AS year_month,
            p.supplier_id,
            SUM(it.quantity) AS inbound_qty
        FROM inventory_transactions AS it
        INNER JOIN products AS p ON it.product_id = p.id
        WHERE it.type = 'inbound' AND it.created_at LIKE '2024%'
        GROUP BY SUBSTR(it.created_at, 1, 7), p.supplier_id
    )
    SELECT
        m.m AS year_month,
        s.company_name AS supplier,
        COALESCE(si.inbound_qty, 0) AS inbound_qty
    FROM months AS m
    CROSS JOIN suppliers AS s
    LEFT JOIN supplier_inbound AS si
        ON m.m = si.year_month AND s.id = si.supplier_id
    ORDER BY m.m, s.company_name
    LIMIT 30;
    ```
