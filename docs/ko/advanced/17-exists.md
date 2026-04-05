# 강의 17: EXISTS와 상관 서브쿼리(Correlated Subqueries)

`EXISTS`는 서브쿼리가 한 건이라도 행을 반환하는지 검사합니다. `IN`과 달리 첫 번째 일치 행을 찾는 즉시 중단하므로, 대용량 데이터에서 효율적이며 NULL이 포함될 수 있는 상황에서도 안전합니다.

## EXISTS vs. IN

| 특성 | `IN` | `EXISTS` |
|---------|------|---------|
| 반환값 | 일치하는 값 | True/False |
| NULL 안전성 | 안전하지 않음 — `NOT IN`은 NULL이 있으면 실패 | 안전 |
| 단락 평가 | 없음 | 있음 — 첫 번째 일치 시 중단 |
| 자기 참조 | 불가 | 가능 — 상관 서브쿼리 |

## 기본 EXISTS

```sql
-- 주문을 한 번이라도 한 고객
SELECT id, name, grade
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.id
)
ORDER BY name
LIMIT 8;
```

내부 쿼리가 외부 쿼리의 `c.id`를 참조하는 것을 **상관 서브쿼리(Correlated Subquery)**라고 합니다. 외부 행마다 한 번씩 실행되면서 일치하는 주문이 존재하는지 확인합니다.

## NOT EXISTS — 누락 데이터 찾기

`NOT EXISTS`는 서브쿼리 컬럼에 NULL이 있을 수 있는 경우 `NOT IN`의 안전한 대안입니다.

```sql
-- 한 번도 주문하지 않은 고객 (NOT IN보다 안전)
SELECT id, name, email, created_at
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.id
)
ORDER BY created_at DESC
LIMIT 10;
```

**결과:**

| id | name | email | created_at |
|----|------|-------|------------|
| 5228 | 김태양 | t.kim@testmail.kr | 2024-12-28 |
| 5221 | 이하은 | h.lee@testmail.kr | 2024-12-19 |
| ... | | | |

```sql
-- 누군가의 찜 목록에는 있지만 한 번도 구매된 적 없는 상품
SELECT p.id, p.name, p.price
FROM products AS p
WHERE EXISTS (
    SELECT 1 FROM wishlists AS w WHERE w.product_id = p.id
)
AND NOT EXISTS (
    SELECT 1 FROM order_items AS oi WHERE oi.product_id = p.id
)
ORDER BY p.price DESC;
```

**결과:**

| id | name | price |
|----|------|-------|
| 214 | 한정판 게이밍 체어 | 899.00 |
| 187 | 8K HDMI 케이블 3m | 79.99 |
| ... | | |

## 조건부 로직을 위한 상관 서브쿼리

`SELECT` 절의 상관 서브쿼리를 사용하면 행마다 "관련 레코드가 있는가?"를 확인할 수 있습니다.

```sql
-- 각 고객의 주문, 리뷰, 불만 접수 여부 표시
SELECT
    c.id,
    c.name,
    c.grade,
    CASE WHEN EXISTS (SELECT 1 FROM orders     WHERE customer_id = c.id) THEN '있음' ELSE '없음' END AS has_orders,
    CASE WHEN EXISTS (SELECT 1 FROM reviews    WHERE customer_id = c.id) THEN '있음' ELSE '없음' END AS has_reviews,
    CASE WHEN EXISTS (SELECT 1 FROM complaints WHERE customer_id = c.id) THEN '있음' ELSE '없음' END AS has_complaints
FROM customers AS c
WHERE c.grade IN ('VIP', 'GOLD')
ORDER BY c.name
LIMIT 8;
```

**결과:**

| id | name | grade | has_orders | has_reviews | has_complaints |
|----|------|-------|------------|-------------|----------------|
| 41 | 강도현 | GOLD | 있음 | 있음 | 없음 |
| 88 | 박소율 | VIP | 있음 | 있음 | 있음 |
| 102 | 이지안 | GOLD | 있음 | 없음 | 없음 |
| ... | | | | | |

## 다중 조건 EXISTS

```sql
-- 2024년에 주문도 하고 불만도 접수한 고객
SELECT c.id, c.name, c.grade
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.id
      AND o.ordered_at LIKE '2024%'
)
AND EXISTS (
    SELECT 1
    FROM complaints AS comp
    WHERE comp.customer_id = c.id
)
ORDER BY c.name;
```

## HAVING에서 EXISTS 사용 (집계와 함께)

```sql
-- 리뷰가 50개 이상인 상품이 하나라도 있는 카테고리
SELECT
    cat.name    AS category,
    COUNT(p.id) AS product_count
FROM categories AS cat
INNER JOIN products AS p ON p.category_id = cat.id
GROUP BY cat.id, cat.name
HAVING EXISTS (
    SELECT 1
    FROM products  AS p2
    INNER JOIN reviews AS r ON r.product_id = p2.id
    WHERE p2.category_id = cat.id
    GROUP BY p2.id
    HAVING COUNT(r.id) >= 50
)
ORDER BY category;
```

## 연습 문제

### 연습 1
해당 고객이 아직 **구매하지 않은** 찜 목록 상품을 모두 찾으세요. `customer_name`, `product_name`, `added_at`(찜 등록 일시)을 반환하세요. `order_items`와 `orders`에서 `customer_id`와 `product_id`가 일치하는지 확인하는 상관 서브쿼리와 함께 `NOT EXISTS`를 사용하세요.

??? success "정답"
    ```sql
    SELECT
        c.name  AS customer_name,
        p.name  AS product_name,
        w.added_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products  AS p ON w.product_id  = p.id
    WHERE NOT EXISTS (
        SELECT 1
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.customer_id  = w.customer_id
          AND oi.product_id  = w.product_id
          AND o.status NOT IN ('cancelled', 'returned')
    )
    ORDER BY w.added_at DESC
    LIMIT 20;
    ```

### 연습 2
불만을 접수한 적 있고 반품 이력도 있는 고객을 찾으세요. `customer_id`, `name`, `grade`, `complaint_count`, `return_count`를 반환하세요. 필터링에는 `EXISTS`를 사용하고, 건수 집계에는 서브쿼리 집계 또는 JOIN을 사용하세요.

??? success "정답"
    ```sql
    SELECT
        c.id    AS customer_id,
        c.name,
        c.grade,
        (SELECT COUNT(*) FROM complaints WHERE customer_id = c.id) AS complaint_count,
        (SELECT COUNT(*) FROM orders AS o
                        INNER JOIN returns AS r ON r.order_id = o.id
                        WHERE o.customer_id = c.id)               AS return_count
    FROM customers AS c
    WHERE EXISTS (
        SELECT 1 FROM complaints WHERE customer_id = c.id
    )
    AND EXISTS (
        SELECT 1
        FROM orders AS o
        INNER JOIN returns AS r ON r.order_id = o.id
        WHERE o.customer_id = c.id
    )
    ORDER BY complaint_count DESC;
    ```

---
다음: [강의 18: 뷰(Views)](18-views.md)
