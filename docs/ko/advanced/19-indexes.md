# 강의 19: 인덱스(Indexes)와 쿼리 실행 계획

인덱스(Index)는 SQLite가 테이블 전체를 스캔하지 않고도 행을 빠르게 찾을 수 있게 해주는 데이터 구조입니다. 언제 인덱스가 도움이 되고 언제 그렇지 않은지를 이해하는 것이 쿼리 성능 튜닝의 기초입니다.

## 인덱스의 역할

인덱스가 없으면 SQLite는 일치하는 행을 찾기 위해 테이블의 모든 행을 읽어야 합니다(**전체 테이블 스캔, Full Table Scan**). 검색 컬럼에 인덱스가 있으면 관련 행으로 바로 이동합니다. 책의 색인으로 찾는 것과 처음부터 끝까지 읽는 것의 차이와 같습니다.

```
테이블 스캔:  O(n)      — 모든 행 확인
인덱스 조회:  O(log n)  — 인덱스 트리 이진 탐색
```

34,689개 주문이 있는 테이블을 스캔하면 34,689개 행을 모두 확인합니다. `customer_id`에 인덱스가 있으면 5~10번의 인덱스 조회로 줄어듭니다.

## EXPLAIN QUERY PLAN

`EXPLAIN QUERY PLAN`은 SQLite가 쿼리를 어떻게 실행할 계획인지, 즉 스캔을 할지 인덱스를 쓸지를 보여줍니다.

```sql
-- 자주 사용하는 쿼리의 실행 계획 확인
EXPLAIN QUERY PLAN
SELECT order_number, total_amount
FROM orders
WHERE customer_id = 42;
```

**인덱스 없음 — 전체 테이블 스캔:**
```
QUERY PLAN
└── SCAN orders
```

**customer_id 인덱스 있음 — 인덱스 조회:**
```
QUERY PLAN
└── SEARCH orders USING INDEX idx_orders_customer_id (customer_id=?)
```

## 기존 인덱스 확인

이 데이터베이스에는 모든 외래 키와 자주 조회되는 컬럼에 인덱스가 미리 생성되어 있습니다.

```sql
-- 데이터베이스의 모든 인덱스 목록
SELECT name, tbl_name, sql
FROM sqlite_master
WHERE type = 'index'
  AND sql IS NOT NULL   -- PRIMARY KEY 자동 생성 인덱스 제외
ORDER BY tbl_name, name;
```

**결과 예시:**

| name | tbl_name | sql |
|------|----------|-----|
| idx_orders_customer_id | orders | CREATE INDEX idx_orders_customer_id ON orders(customer_id) |
| idx_orders_ordered_at | orders | CREATE INDEX idx_orders_ordered_at ON orders(ordered_at) |
| idx_order_items_order_id | order_items | CREATE INDEX ... |
| idx_order_items_product_id | order_items | CREATE INDEX ... |
| idx_reviews_product_id | reviews | CREATE INDEX ... |
| ... | | |

## SCAN vs. SEARCH 비교

```sql
-- 인덱스 있음: 빠른 검색
EXPLAIN QUERY PLAN
SELECT * FROM orders
WHERE ordered_at BETWEEN '2024-01-01' AND '2024-12-31';
-- 결과: SEARCH orders USING INDEX idx_orders_ordered_at
```

```sql
-- 인덱스 없음: 전체 스캔
EXPLAIN QUERY PLAN
SELECT * FROM orders
WHERE notes LIKE '%긴급%';
-- 결과: SCAN orders
-- (앞에 와일드카드가 붙은 LIKE '%...'는 B-트리 인덱스를 사용할 수 없음)
```

## 인덱스가 도움이 되는 경우

| 상황 | 인덱스 효과 |
|-----------|--------------|
| 고카디널리티 컬럼에 `WHERE col = ?` | 있음 |
| `WHERE col BETWEEN ? AND ?` | 있음 |
| `ORDER BY col` (LIMIT 함께 사용 시) | 있음 |
| `JOIN ON a.id = b.fk_id` | 있음 |
| `WHERE col LIKE '접두어%'` | 있음 |
| `WHERE col LIKE '%접미어'` | 없음 — 앞에 와일드카드 |
| `WHERE UPPER(col) = ?` | 없음 — 컬럼에 함수 적용 |
| 소규모 테이블 (1,000행 미만) | 거의 효과 없음 |
| 대량 INSERT/UPDATE/DELETE | 인덱스가 쓰기 속도를 늦춤 |

## 인덱스 생성

```sql
-- 자주 사용하는 필터 패턴을 위한 복합 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_orders_status_date
ON orders (status, ordered_at);
```

이제 상태와 날짜를 함께 필터링하는 쿼리에서 이 인덱스를 활용할 수 있습니다:

```sql
EXPLAIN QUERY PLAN
SELECT order_number, total_amount
FROM orders
WHERE status = 'confirmed'
  AND ordered_at >= '2024-01-01';
-- SEARCH orders USING INDEX idx_orders_status_date (status=? AND ordered_at>?)
```

## 복합 인덱스의 컬럼 순서

복합 인덱스 `(a, b)`는 다음 경우를 지원합니다:
- `a` 단독 필터
- `a`와 `b` 함께 필터
- `a` 기준 정렬 (또는 `a, b` 기준)

하지만 `b`만 필터링하는 경우에는 **도움이 되지 않습니다**.

```sql
-- 복합 인덱스 (status, ordered_at) 사용 가능
WHERE status = 'confirmed' AND ordered_at > '2024-01-01'

-- 왼쪽 접두어만 사용해도 가능
WHERE status = 'confirmed'

-- 이 경우는 사용 불가 (왼쪽 컬럼 누락)
WHERE ordered_at > '2024-01-01'
```

## 인덱스 삭제

```sql
DROP INDEX IF EXISTS idx_orders_status_date;
```

## 연습 문제

### 연습 1
특정 고객의 주문을 날짜 순으로 찾는 쿼리에 `EXPLAIN QUERY PLAN`을 실행하세요. 인덱스가 사용되는지 확인하세요. 그런 다음 `notes IS NOT NULL` 조건으로 필터링하는 쿼리에도 같은 확인을 해보세요.

??? success "정답"
    ```sql
    -- idx_orders_customer_id 인덱스를 사용해야 함
    EXPLAIN QUERY PLAN
    SELECT order_number, ordered_at, total_amount
    FROM orders
    WHERE customer_id = 100
    ORDER BY ordered_at DESC;

    -- notes에 인덱스가 없으므로 전체 스캔 가능성 높음
    EXPLAIN QUERY PLAN
    SELECT order_number, notes
    FROM orders
    WHERE notes IS NOT NULL;
    ```

### 연습 2
`sqlite_master`를 사용하여 데이터베이스의 모든 인덱스를 나열하세요. 각 인덱스에 대해 `sql` 컬럼을 검토하여 단일 컬럼 인덱스인지 복합(다중 컬럼) 인덱스인지 판별하세요. 복합 인덱스가 몇 개나 있나요?

??? success "정답"
    ```sql
    SELECT
        name,
        tbl_name,
        sql,
        CASE WHEN sql LIKE '%,%' THEN '복합' ELSE '단일' END AS index_type
    FROM sqlite_master
    WHERE type = 'index'
      AND sql IS NOT NULL
    ORDER BY tbl_name, name;
    ```

---
다음: [강의 20: 트리거(Triggers)](20-triggers.md)
