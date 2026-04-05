# 강의 16: 공통 테이블 식(Common Table Expressions, WITH)

공통 테이블 식(CTE)은 메인 쿼리 앞에 `WITH` 키워드로 정의하는, 이름이 붙은 임시 결과 집합입니다. CTE를 사용하면 복잡한 쿼리를 훨씬 읽기 쉽고 디버깅하기 좋게 만들 수 있습니다. 각 CTE는 여러 번 참조할 수 있는 이름 있는 서브쿼리와 같습니다.

## 기본 CTE

```sql
WITH monthly_revenue AS (
    SELECT
        SUBSTR(ordered_at, 1, 7) AS year_month,
        SUM(total_amount)        AS revenue,
        COUNT(*)                 AS order_count
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned')
    GROUP BY SUBSTR(ordered_at, 1, 7)
)
SELECT
    year_month,
    revenue,
    order_count,
    ROUND(revenue / order_count, 2) AS avg_order_value
FROM monthly_revenue
WHERE year_month LIKE '2024%'
ORDER BY year_month;
```

**결과:**

| year_month | revenue | order_count | avg_order_value |
|------------|---------|-------------|-----------------|
| 2024-01 | 147832.40 | 270 | 547.53 |
| 2024-02 | 136290.10 | 251 | 542.99 |
| 2024-03 | 204123.70 | 347 | 588.25 |
| ... | | | |

`monthly_revenue`라는 CTE 이름 자체가 의미를 담고 있습니다. 먼저 월별 합계를 구하고, 그 결과를 조회하는 방식으로 자연스럽게 읽힙니다. 서브쿼리를 중첩할 필요가 없습니다.

## 다중 CTE

쉼표로 CTE를 연결할 수 있습니다. 뒤에 오는 CTE는 앞서 정의된 CTE를 참조할 수 있습니다.

```sql
-- 고객 생애 가치(LTV) 세그먼트 분류
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(*)          AS order_count,
        SUM(total_amount) AS lifetime_value
    FROM orders
    WHERE status NOT IN ('cancelled', 'returned')
    GROUP BY customer_id
),
customer_segments AS (
    SELECT
        co.customer_id,
        c.name,
        c.grade,
        co.order_count,
        co.lifetime_value,
        CASE
            WHEN co.lifetime_value >= 5000 THEN '챔피언'
            WHEN co.lifetime_value >= 2000 THEN '충성 고객'
            WHEN co.lifetime_value >= 500  THEN '일반 고객'
            ELSE '간헐적 구매'
        END AS segment
    FROM customer_orders AS co
    INNER JOIN customers AS c ON co.customer_id = c.id
)
SELECT
    segment,
    COUNT(*)                    AS customer_count,
    ROUND(AVG(lifetime_value), 2) AS avg_ltv,
    ROUND(AVG(order_count), 1)    AS avg_orders
FROM customer_segments
GROUP BY segment
ORDER BY avg_ltv DESC;
```

**결과:**

| segment | customer_count | avg_ltv | avg_orders |
|---------|----------------|---------|------------|
| 챔피언 | 312 | 8942.30 | 38.2 |
| 충성 고객 | 891 | 3124.60 | 18.7 |
| 일반 고객 | 2341 | 842.30 | 6.4 |
| 간헐적 구매 | 1242 | 198.70 | 2.1 |

## CTE와 윈도우 함수 조합

CTE와 윈도우 함수는 서로 잘 어울립니다. CTE에서 순위를 매기고, 메인 쿼리에서 필터링하는 패턴이 대표적입니다.

```sql
-- 회원 등급별 매출 상위 3명
WITH customer_revenue AS (
    SELECT
        c.id,
        c.name,
        c.grade,
        SUM(o.total_amount) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled', 'returned')
    GROUP BY c.id, c.name, c.grade
),
ranked AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY grade ORDER BY total_spent DESC) AS rnk
    FROM customer_revenue
)
SELECT grade, name, total_spent, rnk
FROM ranked
WHERE rnk <= 3
ORDER BY grade, rnk;
```

**결과:**

| grade | name | total_spent | rnk |
|-------|------|-------------|-----|
| BRONZE | 김민준 | 3241.50 | 1 |
| BRONZE | 이서연 | 3089.90 | 2 |
| BRONZE | 박지호 | 2944.20 | 3 |
| GOLD | 최수아 | 12891.00 | 1 |
| ... | | | |

## 재귀 CTE — 카테고리 트리 탐색

재귀 CTE(Recursive CTE)는 자기 자신을 참조합니다. 카테고리 트리, 조직도, 부품 명세서(BOM)처럼 계층 구조 데이터를 순회하는 표준 SQL 방법입니다.

`categories` 테이블에는 자기 자신을 가리키는 `parent_id` 컬럼이 있습니다.

```sql
-- 전체 카테고리 트리를 탐색하며 깊이와 경로 표시
WITH RECURSIVE category_tree AS (
    -- 기본 케이스: 최상위 카테고리 (부모 없음)
    SELECT
        id,
        name,
        parent_id,
        0             AS depth,
        name          AS path
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    -- 재귀 케이스: 이미 찾은 노드의 자식
    SELECT
        c.id,
        c.name,
        c.parent_id,
        ct.depth + 1,
        ct.path || ' > ' || c.name
    FROM categories AS c
    INNER JOIN category_tree AS ct ON c.parent_id = ct.id
)
SELECT
    SUBSTR('          ', 1, depth * 2) || name AS indented_name,
    depth,
    path
FROM category_tree
ORDER BY path;
```

**결과:**

| indented_name | depth | path |
|---------------|-------|------|
| 전자기기 | 0 | 전자기기 |
|   컴퓨터 | 1 | 전자기기 > 컴퓨터 |
|     노트북 | 2 | 전자기기 > 컴퓨터 > 노트북 |
|     데스크탑 | 2 | 전자기기 > 컴퓨터 > 데스크탑 |
|   주변기기 | 1 | 전자기기 > 주변기기 |
|     마우스 | 2 | 전자기기 > 주변기기 > 마우스 |
|     키보드 | 2 | 전자기기 > 주변기기 > 키보드 |
| ... | | |

## 연습 문제

### 연습 1
두 개의 CTE를 사용하여 2024년 월별 매출을 구하고, 전월 대비 변화량을 계산하세요. CTE 1: 월별 합계. CTE 2: `LAG`로 전월 값 추가. 메인 쿼리: 모든 컬럼과 `mom_change`, `mom_pct` 반환.

??? success "정답"
    ```sql
    WITH monthly AS (
        SELECT
            SUBSTR(ordered_at, 1, 7) AS year_month,
            SUM(total_amount)        AS revenue
        FROM orders
        WHERE ordered_at LIKE '2024%'
          AND status NOT IN ('cancelled', 'returned')
        GROUP BY SUBSTR(ordered_at, 1, 7)
    ),
    with_lag AS (
        SELECT
            year_month,
            revenue,
            LAG(revenue) OVER (ORDER BY year_month) AS prev_revenue
        FROM monthly
    )
    SELECT
        year_month,
        revenue,
        prev_revenue,
        ROUND(revenue - prev_revenue, 2) AS mom_change,
        ROUND(100.0 * (revenue - prev_revenue) / prev_revenue, 1) AS mom_pct
    FROM with_lag
    ORDER BY year_month;
    ```

### 연습 2
CTE를 사용하여 "이탈 위험 고객"을 찾으세요. 최소 3번 주문했지만 마지막 주문이 180일 이상 지난 고객입니다. `customer_id`, `name`, `grade`, `order_count`, `last_order_date`를 반환하세요.

??? success "정답"
    ```sql
    WITH customer_recency AS (
        SELECT
            customer_id,
            COUNT(*)        AS order_count,
            MAX(ordered_at) AS last_order_date
        FROM orders
        WHERE status NOT IN ('cancelled', 'returned')
        GROUP BY customer_id
    )
    SELECT
        c.id    AS customer_id,
        c.name,
        c.grade,
        cr.order_count,
        cr.last_order_date
    FROM customer_recency AS cr
    INNER JOIN customers AS c ON cr.customer_id = c.id
    WHERE cr.order_count >= 3
      AND julianday('now') - julianday(cr.last_order_date) > 180
    ORDER BY cr.last_order_date ASC;
    ```

### 연습 3
재귀 CTE를 사용하여 모든 말단 카테고리(자식이 없는 카테고리)의 전체 경로(브레드크럼)를 구하세요. `category_id`, `category_name`, `full_path`를 반환하세요.

??? success "정답"
    ```sql
    WITH RECURSIVE category_tree AS (
        SELECT
            id,
            name,
            parent_id,
            name AS full_path
        FROM categories
        WHERE parent_id IS NULL

        UNION ALL

        SELECT
            c.id,
            c.name,
            c.parent_id,
            ct.full_path || ' > ' || c.name
        FROM categories AS c
        INNER JOIN category_tree AS ct ON c.parent_id = ct.id
    )
    SELECT
        ct.id   AS category_id,
        ct.name AS category_name,
        ct.full_path
    FROM category_tree AS ct
    WHERE ct.id NOT IN (SELECT parent_id FROM categories WHERE parent_id IS NOT NULL)
    ORDER BY ct.full_path;
    ```

---
다음: [강의 17: EXISTS와 상관 서브쿼리](17-exists.md)
