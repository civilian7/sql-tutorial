# 8강: LEFT JOIN

`LEFT JOIN`은 **왼쪽 테이블의 모든 행**을 반환하고, 오른쪽 테이블에서 일치하는 행이 있으면 함께 가져옵니다. 일치하는 행이 없으면 오른쪽 컬럼은 `NULL`로 채워집니다. 관련 레코드가 없는 행을 찾을 때 꼭 필요한 기법으로, 실무에서 매우 자주 쓰입니다.

```mermaid
flowchart LR
    subgraph "customers (LEFT)"
        C1["ID:1 Kim"]
        C2["ID:2 Lee"]
        C3["ID:3 Park"]
    end
    subgraph "orders (RIGHT)"
        O1["Cust:1 ORD-001"]
        O3["Cust:2 ORD-003"]
    end
    subgraph "LEFT JOIN Result"
        R1["Kim + ORD-001"]
        R2["Lee + ORD-003"]
        R3["Park + NULL"]
    end
    C1 --> R1
    C2 --> R2
    C3 --> R3
    O1 --> R1
    O3 --> R2
    style R3 fill:#fff9c4,stroke:#f9a825
```

> LEFT JOIN은 왼쪽 테이블의 모든 행을 유지합니다. 오른쪽에 매칭이 없으면 NULL로 채워집니다.

## 기본 LEFT JOIN

```sql
-- 리뷰 여부와 관계없이 모든 상품 조회
SELECT
    p.name          AS product_name,
    p.price,
    r.rating,
    r.created_at    AS reviewed_at
FROM products AS p
LEFT JOIN reviews AS r ON p.id = r.product_id
ORDER BY p.name
LIMIT 8;
```

**결과:**

| product_name | price | rating | reviewed_at |
|--------------|-------|--------|-------------|
| ASUS ProArt 32" 4K Monitor | 2199.00 | 5 | 2023-08-14 |
| ASUS ProArt 32" 4K Monitor | 2199.00 | 4 | 2024-01-22 |
| ASUS ROG Gaming Desktop | 1899.00 | 5 | 2022-11-03 |
| ASUS TUF Gaming Laptop | 1099.00 | (NULL) | (NULL) |
| Belkin USB-C Hub | 49.99 | (NULL) | (NULL) |
| ... | | | |

`ASUS TUF Gaming Laptop`과 `Belkin USB-C Hub`는 리뷰가 없으므로 `rating`과 `reviewed_at`이 `NULL`입니다.

## 불일치 행 찾기

안티 조인(Anti-join) 패턴: `LEFT JOIN` 후 `WHERE right_table.id IS NULL` 조건을 추가합니다. 오른쪽 테이블에 **대응 행이 없는** 왼쪽 테이블의 행을 찾는 방법입니다.

```sql
-- 한 번도 리뷰를 받지 않은 상품
SELECT
    p.id,
    p.name,
    p.price
FROM products AS p
LEFT JOIN reviews AS r ON p.id = r.product_id
WHERE r.id IS NULL
ORDER BY p.name;
```

**결과:**

| id | name | price |
|----|------|-------|
| 47 | ASUS TUF Gaming Laptop | 1099.00 |
| 83 | Belkin USB-C Hub | 49.99 |
| 116 | Corsair K60 RGB Keyboard | 89.99 |
| ... | | |

```sql
-- 주문을 한 번도 하지 않은 고객
SELECT
    c.id,
    c.name,
    c.email,
    c.created_at
FROM customers AS c
LEFT JOIN orders AS o ON c.id = o.customer_id
WHERE o.id IS NULL
ORDER BY c.created_at DESC
LIMIT 10;
```

**결과:**

| id | name | email | created_at |
|----|------|-------|------------|
| 5228 | 한소희 | h.sohi@testmail.kr | 2024-12-28 |
| 5221 | 오준혁 | o.junhyuk@testmail.kr | 2024-12-19 |
| ... | | | |

> 이 고객들은 최근에 가입해서 아직 구매하지 않았을 가능성이 높습니다.

## LEFT JOIN과 집계

일치한 행만 카운트하려면 `COUNT(*)` 대신 `COUNT(right_table.id)`를 사용하세요 — NULL은 카운트에 포함되지 않습니다.

```sql
-- 모든 상품의 리뷰 수와 평균 평점
SELECT
    p.name          AS product_name,
    p.price,
    COUNT(r.id)     AS review_count,
    ROUND(AVG(r.rating), 2) AS avg_rating
FROM products AS p
LEFT JOIN reviews AS r ON p.id = r.product_id
WHERE p.is_active = 1
GROUP BY p.id, p.name, p.price
ORDER BY review_count DESC
LIMIT 10;
```

**결과:**

| product_name | price | review_count | avg_rating |
|--------------|-------|--------------|------------|
| Dell XPS 15 Laptop | 1299.99 | 87 | 4.21 |
| Logitech MX Master 3 | 99.99 | 74 | 4.56 |
| Samsung 27" Monitor | 449.99 | 68 | 4.03 |
| ... | | | |

```sql
-- 주문이 0건인 고객을 포함한 고객별 주문 통계
SELECT
    c.name,
    c.grade,
    COUNT(o.id)         AS order_count,
    COALESCE(SUM(o.total_amount), 0) AS lifetime_value
FROM customers AS c
LEFT JOIN orders AS o ON c.id = o.customer_id
    AND o.status NOT IN ('cancelled', 'returned')
GROUP BY c.id, c.name, c.grade
ORDER BY lifetime_value DESC
LIMIT 8;
```

> 추가 `AND` 조건을 `WHERE` 대신 `ON` 절에 넣은 것에 주목하세요. `WHERE`에 넣으면 주문이 없는 고객이 결과에서 제외됩니다.

**결과:**

| name | grade | order_count | lifetime_value |
|------|-------|-------------|----------------|
| 김민수 | VIP | 48 | 64291.50 |
| 이지은 | VIP | 41 | 52884.20 |
| ... | | | |

## 여러 LEFT JOIN 연결

```sql
-- 배송 및 결제 정보를 선택적으로 포함한 주문 조회
SELECT
    o.order_number,
    o.status,
    o.total_amount,
    s.carrier,
    s.tracking_number,
    p.method         AS payment_method
FROM orders AS o
LEFT JOIN shipping AS s ON s.order_id = o.id
LEFT JOIN payments AS p ON p.order_id = o.id
WHERE o.ordered_at LIKE '2024-12%'
LIMIT 5;
```

!!! note "레슨 복습 문제"
    이 레슨에서 배운 개념을 바로 확인하는 간단한 문제입니다. 여러 개념을 종합하는 실전 연습은 [연습 문제](../exercises/) 섹션을 참고하세요.

## 연습 문제

### 연습 1
위시리스트에 상품을 담았지만 **주문을 한 번도 하지 않은** 고객을 모두 구하세요. `customer_name`, `email`, `wishlist_items`(위시리스트 항목 수)를 반환하고, `wishlist_items` 내림차순으로 정렬하세요.

??? success "정답"
    ```sql
    SELECT
        c.name  AS customer_name,
        c.email,
        COUNT(w.id) AS wishlist_items
    FROM customers AS c
    LEFT JOIN orders    AS o ON c.id = o.customer_id
    INNER JOIN wishlists AS w ON c.id = w.customer_id
    WHERE o.id IS NULL
    GROUP BY c.id, c.name, c.email
    ORDER BY wishlist_items DESC;
    ```

### 연습 2
모든 상품에 대해 상품명, 가격, 총 판매 수량(`SUM(order_items.quantity)`), 해당 상품이 등장한 주문 수를 보여주세요. **한 번도 주문되지 않은 상품도 포함**하고 그 경우 0으로 표시하세요. 판매 수량 내림차순으로 20행까지 반환하세요.

??? success "정답"
    ```sql
    SELECT
        p.name              AS product_name,
        p.price,
        COALESCE(SUM(oi.quantity), 0)    AS units_sold,
        COUNT(DISTINCT oi.order_id)       AS order_appearances
    FROM products AS p
    LEFT JOIN order_items AS oi ON p.id = oi.product_id
    GROUP BY p.id, p.name, p.price
    ORDER BY units_sold DESC
    LIMIT 20;
    ```

### 연습 3
`inventory_transactions` 테이블에 **재고 거래 내역이 전혀 없는** 활성 상품을 모두 구하세요. `product_id`, `name`, `stock_qty`를 반환하세요.

??? success "정답"
    ```sql
    SELECT
        p.id        AS product_id,
        p.name,
        p.stock_qty
    FROM products AS p
    LEFT JOIN inventory_transactions AS it ON p.id = it.product_id
    WHERE p.is_active = 1
      AND it.id IS NULL
    ORDER BY p.name;
    ```

---
다음: [9강: 서브쿼리](09-subqueries.md)
