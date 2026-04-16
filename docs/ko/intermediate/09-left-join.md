# 9강: LEFT JOIN과 외부 조인

8강에서 INNER JOIN으로 두 테이블을 연결했습니다. 하지만 INNER JOIN은 양쪽 모두에 데이터가 있는 행만 반환합니다. '주문이 없는 고객'이나 '리뷰가 없는 상품'을 찾으려면? LEFT JOIN을 사용합니다.

!!! note "이미 알고 계신다면"
    LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN에 익숙하다면 [10강: 서브쿼리](10-subqueries.md)로 건너뛰세요.

`LEFT JOIN`은 **왼쪽 테이블의 모든 행**을 반환하고, 오른쪽 테이블에서 일치하는 행이 있으면 함께 가져옵니다. 일치하는 행이 없으면 오른쪽 칼럼은 `NULL`로 채워집니다. 관련 레코드가 없는 행을 찾을 때 꼭 필요한 기법으로, 실무에서 매우 자주 쓰입니다.

```mermaid
flowchart TD
    subgraph customers["customers (LEFT)"]
        C1["Kim · ID:1"]
        C2["Lee · ID:2"]
        C3["Park · ID:3"]
    end
    subgraph orders["orders (RIGHT)"]
        O1["ORD-001 · customer_id:1"]
        O3["ORD-003 · customer_id:2"]
    end
    subgraph result["LEFT JOIN 결과"]
        R1["Kim + ORD-001"]:::matched
        R2["Lee + ORD-003"]:::matched
        R3["Park + NULL"]:::kept
    end
    C1 --> R1
    C2 --> R2
    C3 --> R3
    O1 -.-> R1
    O3 -.-> R2
    classDef matched fill:#c8e6c9,stroke:#43a047
    classDef kept fill:#fff9c4,stroke:#f9a825
```

> **LEFT JOIN**은 왼쪽 테이블의 모든 행을 유지합니다. 오른쪽에 매칭이 없으면 NULL로 채워집니다.

![LEFT JOIN](../img/join-left.svg){ .off-glb width="300"  }

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
| ---------- | ----------: | ----------: | ---------- |
| AMD Ryzen 5 9600X | 186400.0 | 1 | 2016-10-11 19:28:27 |
| AMD Ryzen 5 9600X | 186400.0 | 1 | 2016-11-20 11:26:07 |
| AMD Ryzen 5 9600X | 186400.0 | 1 | 2021-01-06 14:45:38 |
| AMD Ryzen 5 9600X | 186400.0 | 1 | 2024-02-17 09:15:04 |
| AMD Ryzen 5 9600X | 186400.0 | 1 | 2024-04-25 10:35:27 |
| AMD Ryzen 5 9600X | 186400.0 | 1 | 2024-05-17 22:57:55 |
| AMD Ryzen 5 9600X | 186400.0 | 1 | 2025-03-07 12:44:04 |
| AMD Ryzen 5 9600X | 186400.0 | 2 | 2016-09-23 14:03:18 |
| ... | ... | ... | ... |

`ASUS TUF Gaming Laptop`과 `Belkin USB-C Hub`는 리뷰가 없으므로 `rating`과 `reviewed_at`이 `NULL`입니다.

## 불일치 행 찾기

![LEFT JOIN — A only](../img/join-left-only.svg){ .off-glb width="300"  }

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
| ----------: | ---------- | ----------: |
| 2712 | ASRock X870E Taichi 화이트 | 218900.0 |
| 2224 | ASUS ExpertCenter D900 | 2655100.0 |
| 21 | ASUS ROG Strix G16CH 화이트 | 3307900.0 |
| 2570 | ASUS ROG Zephyrus G14 실버 | 3362500.0 |
| 2719 | BenQ PD2725U 화이트 | 814400.0 |
| 2577 | CORSAIR Vengeance DDR5 32GB 실버 | 338300.0 |
| 2523 | Dell P2723D | 817700.0 |
| 2514 | Dell U2723QE 실버 | 555800.0 |
| ... | ... | ... |

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
| ----------: | ---------- | ---------- | ---------- |
| 49801 | 김선영 | user49801@testmail.kr | 2025-12-30 22:45:23 |
| 48802 | 류은경 | user48802@testmail.kr | 2025-12-30 22:33:01 |
| 51023 | 이은경 | user51023@testmail.kr | 2025-12-30 19:52:14 |
| 47952 | 류지원 | user47952@testmail.kr | 2025-12-30 19:44:42 |
| 45855 | 강성민 | user45855@testmail.kr | 2025-12-30 17:47:49 |
| 50734 | 최하은 | user50734@testmail.kr | 2025-12-30 15:43:58 |
| 49114 | 이재호 | user49114@testmail.kr | 2025-12-30 15:37:59 |
| 48650 | 김민지 | user48650@testmail.kr | 2025-12-30 13:11:58 |
| ... | ... | ... | ... |

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
| ---------- | ----------: | ----------: | ----------: |
| 로지텍 G PRO X SUPERLIGHT 2 실버 | 49400.0 | 137 | 3.93 |
| Arctic Freezer i35 화이트 | 31800.0 | 121 | 3.79 |
| Keychron Q1 Pro 실버 | 178600.0 | 116 | 3.79 |
| SteelSeries Aerox 5 Wireless 실버 | 61500.0 | 114 | 3.7 |
| 로지텍 G502 X PLUS 화이트 | 91400.0 | 112 | 4.02 |
| Crucial T700 2TB 실버 | 37100.0 | 111 | 3.85 |
| SteelSeries Aerox 5 Wireless 실버 | 101400.0 | 106 | 3.86 |
| Arctic Freezer i35 블랙 | 44600.0 | 106 | 3.73 |
| ... | ... | ... | ... |

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
| ---------- | ---------- | ----------: | ----------: |
| 박정수 | VIP | 661 | 671056103.0 |
| 정유진 | VIP | 544 | 646834022.0 |
| 이미정 | VIP | 530 | 633645694.0 |
| 김상철 | VIP | 513 | 565735423.0 |
| 문영숙 | VIP | 546 | 523138846.0 |
| 이영자 | VIP | 509 | 520594776.0 |
| 이미정 | VIP | 440 | 497376276.0 |
| 장영숙 | VIP | 356 | 487964896.0 |
| ... | ... | ... | ... |

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

## RIGHT JOIN

![RIGHT JOIN](../img/join-right.svg){ .off-glb width="300"  }

`RIGHT JOIN`은 LEFT JOIN의 반대입니다. **오른쪽 테이블의 모든 행**을 유지하고, 왼쪽 테이블에서 일치하는 행이 없으면 `NULL`로 채웁니다.

```mermaid
flowchart TD
    subgraph orders["orders (LEFT)"]
        O1["ORD-001 · customer_id:1"]
        O3["ORD-003 · customer_id:2"]
    end
    subgraph customers["customers (RIGHT)"]
        C1["Kim · ID:1"]
        C2["Lee · ID:2"]
        C3["Park · ID:3"]
    end
    subgraph result["RIGHT JOIN 결과"]
        R1["ORD-001 + Kim"]:::matched
        R2["ORD-003 + Lee"]:::matched
        R3["NULL + Park"]:::kept
    end
    O1 --> R1
    O3 --> R2
    C1 -.-> R1
    C2 -.-> R2
    C3 --> R3
    classDef matched fill:#c8e6c9,stroke:#43a047
    classDef kept fill:#fff9c4,stroke:#f9a825
```

```sql
-- RIGHT JOIN: 주문이 없는 고객도 포함
SELECT
    c.name,
    c.email,
    o.order_number,
    o.total_amount
FROM orders AS o
RIGHT JOIN customers AS c ON c.id = o.customer_id
ORDER BY c.name
LIMIT 10;
```

실무에서는 RIGHT JOIN을 거의 쓰지 않습니다. 테이블 순서를 바꿔서 LEFT JOIN으로 작성하면 동일한 결과를 얻을 수 있기 때문입니다:

```sql
-- LEFT JOIN으로 동일한 결과
SELECT
    c.name,
    c.email,
    o.order_number,
    o.total_amount
FROM customers AS c
LEFT JOIN orders AS o ON c.id = o.customer_id
ORDER BY c.name
LIMIT 10;
```

> 두 쿼리는 같은 결과를 반환합니다. LEFT JOIN이 더 직관적이므로 대부분의 팀에서는 LEFT JOIN을 선호합니다.

## FULL OUTER JOIN

![FULL OUTER JOIN](../img/join-full.svg){ .off-glb width="300"  }

`FULL OUTER JOIN`은 **양쪽 테이블의 모든 행**을 유지합니다. 어느 쪽에서든 매칭이 안 되면 `NULL`로 채워집니다. 주문이 없는 고객과 고객 정보가 없는 주문을 동시에 확인할 때 유용합니다.

```mermaid
flowchart TD
    subgraph customers["customers"]
        C1["Kim · ID:1"]
        C2["Lee · ID:2"]
        C3["Park · ID:3"]
    end
    subgraph orders["orders"]
        O1["ORD-001 · customer_id:1"]
        O2["ORD-003 · customer_id:2"]
        O4["ORD-007 · customer_id:99"]
    end
    subgraph result["FULL OUTER JOIN 결과"]
        R1["Kim + ORD-001"]:::matched
        R2["Lee + ORD-003"]:::matched
        R3["Park + NULL"]:::kept
        R4["NULL + ORD-007"]:::kept
    end
    C1 --> R1
    C2 --> R2
    C3 --> R3
    O1 -.-> R1
    O2 -.-> R2
    O4 --> R4
    classDef matched fill:#c8e6c9,stroke:#43a047
    classDef kept fill:#fff9c4,stroke:#f9a825
```

FULL OUTER JOIN의 지원 여부는 데이터베이스마다 다릅니다:

=== "SQLite"

    SQLite 3.39.0(2022-07-21) 이상에서는 `FULL OUTER JOIN`을 직접 지원합니다:

    ```sql
    -- SQLite 3.39+ : FULL OUTER JOIN 직접 사용
    SELECT
        c.name,
        c.email,
        o.order_number,
        o.total_amount
    FROM customers AS c
    FULL OUTER JOIN orders AS o ON c.id = o.customer_id
    ORDER BY c.name
    LIMIT 15;
    ```

    이전 버전과의 호환이 필요하다면 `LEFT JOIN` + `UNION ALL` 패턴으로 대체할 수 있습니다:

    ```sql
    -- SQLite 3.38 이하 호환: LEFT JOIN UNION ALL
    SELECT
        c.name,
        c.email,
        o.order_number,
        o.total_amount
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id

    UNION ALL

    SELECT
        NULL    AS name,
        NULL    AS email,
        o.order_number,
        o.total_amount
    FROM orders AS o
    LEFT JOIN customers AS c ON c.id = o.customer_id
    WHERE c.id IS NULL
    ORDER BY name
    LIMIT 15;
    ```

=== "MySQL"

    MySQL은 `FULL OUTER JOIN`을 지원하지 않습니다. `LEFT JOIN`과 `RIGHT JOIN`을 `UNION`으로 결합하여 대체합니다:

    ```sql
    -- MySQL: LEFT JOIN UNION RIGHT JOIN
    SELECT
        c.name,
        c.email,
        o.order_number,
        o.total_amount
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id

    UNION

    SELECT
        c.name,
        c.email,
        o.order_number,
        o.total_amount
    FROM customers AS c
    RIGHT JOIN orders AS o ON c.id = o.customer_id
    ORDER BY name
    LIMIT 15;
    ```

=== "PostgreSQL"

    PostgreSQL은 `FULL OUTER JOIN`을 직접 지원합니다:

    ```sql
    -- PostgreSQL: FULL OUTER JOIN 직접 지원
    SELECT
        c.name,
        c.email,
        o.order_number,
        o.total_amount
    FROM customers AS c
    FULL OUTER JOIN orders AS o ON c.id = o.customer_id
    ORDER BY c.name
    LIMIT 15;
    ```

## 정리

| 개념 | 설명 | 예시 |
|------|------|------

<!-- BEGIN_LESSON_EXERCISES -->

!!! note "레슨 복습 문제"
    이 레슨에서 배운 개념을 바로 확인하는 간단한 문제입니다. 여러 개념을 종합하는 실전 연습은 [연습 문제](../exercises/index.md) 섹션을 참고하세요.

### 문제 1
주문이 없는 고객과 고객 정보가 누락된 주문을 **모두** 포함하여 `customer_name`, `order_number`, `total_amount`를 조회하세요. 고객이 없으면 `'(알 수 없음)'`, 주문이 없으면 `'(주문 없음)'`으로 표시하세요. `customer_name` 오름차순으로 정렬하여 15행까지 반환하세요.

??? success "정답"
    ```sql
    -- SQLite 3.39+
    SELECT
    COALESCE(c.name, '(알 수 없음)')       AS customer_name,
    COALESCE(o.order_number, '(주문 없음)') AS order_number,
    o.total_amount
    FROM customers AS c
    FULL OUTER JOIN orders AS o ON c.id = o.customer_id
    ORDER BY customer_name
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | customer_name | order_number | total_amount |
    |---|---|---|
    | 강건우 | (주문 없음) | NULL |
    | 강경수 | ORD-20250128-31663 | 1,387,400.00 |
    | 강경숙 | ORD-20211210-14732 | 615,800.00 |
    | 강경숙 | ORD-20220509-16871 | 175,500.00 |
    | 강경숙 | ORD-20230111-20503 | 101,500.00 |
    | 강경숙 | ORD-20240924-29511 | 287,100.00 |
    | 강경숙 | ORD-20241025-30040 | 781,300.00 |

### 문제 2
**리뷰를 남기지 않은** 고객 수를 구하세요. `no_review_customers`라는 단일 값을 반환하세요.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS no_review_customers
    FROM customers AS c
    LEFT JOIN reviews AS r ON c.id = r.customer_id
    WHERE r.id IS NULL;
    ```


    **실행 결과** (1행)

    | no_review_customers |
    |---|
    | 3331 |

### 문제 3
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


    **실행 결과** (1행)

    | product_id | name | stock_qty |
    |---|---|---|
    | 281 | FK 테스트 | 10 |

### 문제 4
모든 카테고리에 대해 카테고리명과 해당 카테고리에 속한 상품 수(`product_count`)를 구하세요. **상품이 하나도 없는 카테고리도 포함**하여 0으로 표시하세요. `product_count` 내림차순, 같으면 카테고리명 오름차순으로 정렬하세요.

??? success "정답"
    ```sql
    SELECT
    cat.name        AS category_name,
    COUNT(p.id)     AS product_count
    FROM categories AS cat
    LEFT JOIN products AS p ON cat.id = p.category_id
    GROUP BY cat.id, cat.name
    ORDER BY product_count DESC, category_name ASC;
    ```


    **실행 결과** (총 53행 중 상위 7행)

    | category_name | product_count |
    |---|---|
    | Intel 소켓 | 13 |
    | 파워서플라이(PSU) | 13 |
    | 스피커/헤드셋 | 12 |
    | 기계식 | 11 |
    | 멤브레인 | 11 |
    | 조립PC | 11 |
    | 케이스 | 11 |

### 문제 5
`orders` 테이블을 기준으로 RIGHT JOIN을 사용하여, 모든 고객의 이름(`name`)과 주문 횟수(`order_count`)를 구하세요. **주문이 없는 고객도 포함**하고, 주문 횟수 내림차순으로 정렬하여 10행까지 반환하세요.

??? success "정답"
    ```sql
    SELECT
    c.name,
    COUNT(o.id) AS order_count
    FROM orders AS o
    RIGHT JOIN customers AS c ON c.id = o.customer_id
    GROUP BY c.id, c.name
    ORDER BY order_count DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | order_count |
    |---|---|
    | 김병철 | 366 |
    | 박정수 | 328 |
    | 이영자 | 307 |
    | 강명자 | 266 |
    | 김성민 | 246 |
    | 정유진 | 237 |
    | 이미정 | 234 |

### 문제 6
공급업체(`suppliers`)별로 공급하는 활성 상품 수(`product_count`)와 총 재고(`total_stock`)를 구하세요. **상품이 없는 공급업체도 포함**하고, 해당 값은 0으로 표시하세요. `total_stock` 내림차순으로 정렬하세요.

??? success "정답"
    ```sql
    SELECT
    sup.company_name,
    COUNT(p.id)                     AS product_count,
    COALESCE(SUM(p.stock_qty), 0)   AS total_stock
    FROM suppliers AS sup
    LEFT JOIN products AS p ON sup.id = p.supplier_id
    AND p.is_active = 1
    GROUP BY sup.id, sup.company_name
    ORDER BY total_stock DESC;
    ```


    **실행 결과** (총 60행 중 상위 7행)

    | company_name | product_count | total_stock |
    |---|---|---|
    | 삼성전자 공식 유통 | 22 | 6184 |
    | 에이수스코리아 | 21 | 5828 |
    | MSI코리아 | 12 | 4070 |
    | ASRock코리아 | 9 | 3084 |
    | TP-Link코리아 | 11 | 3081 |
    | LG전자 공식 유통 | 11 | 2667 |
    | 로지텍코리아 | 11 | 2461 |

### 문제 7
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


    **실행 결과** (총 20행 중 상위 7행)

    | product_name | price | units_sold | order_appearances |
    |---|---|---|---|
    | Crucial T700 2TB 실버 | 257,000.00 | 1503 | 1472 |
    | AMD Ryzen 9 9900X | 335,700.00 | 1447 | 1396 |
    | SK하이닉스 Platinum P41 2TB 실버 | 255,500.00 | 1359 | 1317 |
    | 로지텍 G502 X PLUS | 97,500.00 | 1087 | 979 |
    | Kingston FURY Beast DDR4 16GB 실버 | 48,000.00 | 1061 | 919 |
    | SteelSeries Prime Wireless 블랙 | 89,800.00 | 1034 | 981 |
    | SteelSeries Aerox 5 Wireless 실버 | 100,000.00 | 1030 | 974 |

### 문제 8
모든 주문에 대해 주문번호, 총액, 결제 수단(`payments.method`), 배송 운송사(`shipping.carrier`)를 보여주세요. 결제나 배송 정보가 없는 주문도 포함하고, 그 경우 `COALESCE`로 `'미결제'`, `'미배송'`으로 표시하세요. 주문 총액 내림차순으로 10행까지 반환하세요.

??? success "정답"
    ```sql
    SELECT
    o.order_number,
    o.total_amount,
    COALESCE(p.method, '미결제')   AS payment_method,
    COALESCE(s.carrier, '미배송')  AS carrier
    FROM orders AS o
    LEFT JOIN payments AS p ON o.id = p.order_id
    LEFT JOIN shipping AS s ON o.id = s.order_id
    ORDER BY o.total_amount DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | total_amount | payment_method | carrier |
    |---|---|---|---|
    | ORD-20201121-08810 | 50,867,500.00 | card | CJ대한통운 |
    | ORD-20250305-32265 | 46,820,024.00 | naver_pay | CJ대한통운 |
    | ORD-20230523-22331 | 46,094,971.00 | naver_pay | 미배송 |
    | ORD-20200209-05404 | 43,677,500.00 | card | 로젠택배 |
    | ORD-20221231-20394 | 43,585,700.00 | naver_pay | 미배송 |
    | ORD-20251218-37240 | 38,626,400.00 | bank_transfer | 로젠택배 |
    | ORD-20220106-15263 | 37,987,600.00 | card | CJ대한통운 |

### 문제 9
모든 고객의 이름, 이메일, 가장 최근 주문 상태(`status`)를 조회하세요. 주문이 없는 고객의 상태는 `'주문 없음'`으로 표시하세요. `COALESCE`를 사용하고, 고객명 오름차순으로 정렬하여 15행까지 반환하세요.

??? success "정답"
    ```sql
    SELECT
    c.name,
    c.email,
    COALESCE(o.status, '주문 없음') AS last_order_status
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    AND o.ordered_at = (
    SELECT MAX(o2.ordered_at)
    FROM orders AS o2
    WHERE o2.customer_id = c.id
    )
    ORDER BY c.name
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | name | email | last_order_status |
    |---|---|---|
    | 강건우 | user4737@testmail.kr | 주문 없음 |
    | 강경수 | user3281@testmail.kr | confirmed |
    | 강경숙 | user2384@testmail.kr | confirmed |
    | 강경숙 | user3645@testmail.kr | confirmed |
    | 강경자 | user1109@testmail.kr | confirmed |
    | 강경희 | user2103@testmail.kr | confirmed |
    | 강광수 | user3374@testmail.kr | confirmed |

### 문제 10
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


    **실행 결과** (총 346행 중 상위 7행)

    | customer_name | email | wishlist_items |
    |---|---|---|
    | 최미영 | user4491@testmail.kr | 4 |
    | 강지민 | user1573@testmail.kr | 3 |
    | 김서준 | user1804@testmail.kr | 3 |
    | 성수빈 | user3206@testmail.kr | 3 |
    | 장승민 | user3245@testmail.kr | 3 |
    | 최영진 | user4373@testmail.kr | 3 |
    | 박미경 | user4436@testmail.kr | 3 |

<!-- END_LESSON_EXERCISES -->
