# 초급 연습: 상품 탐색

`products`, `categories`, `suppliers` 테이블을 사용합니다. 한 테이블 또는 간단한 JOIN만 사용하는 15문제입니다.

---

### 1. 전체 상품 수

현재 등록된 전체 상품 수를 구하세요.

**힌트:** `COUNT(*)` 집계 함수를 사용하세요.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_products FROM products;
    ```

---

### 2. 가장 비싼 상품 5개

가격이 높은 순으로 상위 5개 상품의 이름과 가격을 조회하세요.

**힌트:** `ORDER BY price DESC`로 정렬하고 `LIMIT 5`로 상위 5개만 가져오세요.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    ORDER BY price DESC
    LIMIT 5;
    ```

---

### 3. 10만원 이하 상품

가격이 100,000원 이하인 상품의 이름, 브랜드, 가격을 가격 오름차순으로 조회하세요.

**힌트:** `WHERE price <= 100000` 조건과 `ORDER BY price ASC`를 사용하세요.

??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE price <= 100000
    ORDER BY price ASC;
    ```

---

### 4. 품절 상품

재고가 0인 상품의 이름과 SKU를 조회하세요.

**힌트:** `WHERE stock_qty = 0` 조건으로 필터링하세요.

??? success "정답"
    ```sql
    SELECT name, sku
    FROM products
    WHERE stock_qty = 0;
    ```

---

### 5. 브랜드별 상품 수

브랜드별로 몇 개의 상품이 있는지 세고, 상품 수가 많은 순으로 정렬하세요.

**힌트:** `GROUP BY brand`로 그룹화하고 `COUNT(*)`로 세기. `ORDER BY ... DESC`로 정렬.

??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS product_count
    FROM products
    GROUP BY brand
    ORDER BY product_count DESC;
    ```

---

### 6. 단종된 상품

단종일(`discontinued_at`)이 NULL이 아닌 상품의 이름, 가격, 단종일을 조회하세요.

**힌트:** `IS NOT NULL`로 NULL이 아닌 행만 필터링하세요.

??? success "정답"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE discontinued_at IS NOT NULL
    ORDER BY discontinued_at DESC;
    ```

---

### 7. 평균 가격

전체 상품의 평균 가격과 중간 가격대를 구하세요.

**힌트:** `AVG()`, `MIN()`, `MAX()` 집계 함수를 함께 사용하세요. `ROUND()`로 소수점 정리.

??? success "정답"
    ```sql
    SELECT
        ROUND(AVG(price), 2) AS avg_price,
        ROUND(MIN(price), 2) AS min_price,
        ROUND(MAX(price), 2) AS max_price
    FROM products;
    ```

---

### 8. 삼성(Samsung) 상품

브랜드가 'Samsung'인 상품의 이름, 가격, 재고를 조회하세요.

**힌트:** `WHERE brand = 'Samsung'` 조건을 사용하세요. 문자열은 작은따옴표로 감싸기.

??? success "정답"
    ```sql
    SELECT name, price, stock_qty
    FROM products
    WHERE brand = 'Samsung'
    ORDER BY price DESC;
    ```

---

### 9. 이름에 "Gaming" 포함

상품명에 "Gaming"이 포함된 상품을 조회하세요.

**힌트:** `LIKE '%Gaming%'`으로 부분 문자열을 검색하세요. `%`는 임의의 문자열을 의미.

??? success "정답"
    ```sql
    SELECT name, brand, price
    FROM products
    WHERE name LIKE '%Gaming%'
    ORDER BY price DESC;
    ```

---

### 10. 재고 부족 상품 (10개 이하)

재고가 10개 이하이고 판매 중(`is_active = 1`)인 상품의 이름, 재고, 가격을 조회하세요.

**힌트:** `WHERE` 절에서 `AND`로 두 조건을 결합하세요: `stock_qty <= 10 AND is_active = 1`.

??? success "정답"
    ```sql
    SELECT name, stock_qty, price
    FROM products
    WHERE stock_qty <= 10
      AND is_active = 1
    ORDER BY stock_qty ASC;
    ```

---

### 11. 카테고리 목록

최상위 카테고리(depth = 0)만 이름순으로 조회하세요.

**힌트:** `categories` 테이블에서 `WHERE depth = 0`으로 필터링하세요.

??? success "정답"
    ```sql
    SELECT id, name, slug
    FROM categories
    WHERE depth = 0
    ORDER BY sort_order;
    ```

---

### 12. 가격대별 상품 수

10만원 미만, 10~50만원, 50~100만원, 100만원 이상으로 나누어 각 구간의 상품 수를 구하세요.

**힌트:** `CASE WHEN`으로 가격 구간을 분류한 뒤 `GROUP BY`와 `COUNT(*)`로 집계하세요.

??? success "정답"
    ```sql
    SELECT
        CASE
            WHEN price < 100000 THEN '10만원 미만'
            WHEN price < 500000 THEN '10~50만원'
            WHEN price < 1000000 THEN '50~100만원'
            ELSE '100만원 이상'
        END AS price_range,
        COUNT(*) AS product_count
    FROM products
    GROUP BY price_range
    ORDER BY MIN(price);
    ```

---

### 13. 공급업체 목록

활성(`is_active = 1`) 공급업체의 회사명과 담당자명을 조회하세요.

**힌트:** `suppliers` 테이블에서 `WHERE is_active = 1`로 필터링하세요.

??? success "정답"
    ```sql
    SELECT company_name, contact_name, email
    FROM suppliers
    WHERE is_active = 1
    ORDER BY company_name;
    ```

---

### 14. 마진율 계산

각 상품의 마진율(`(price - cost_price) / price * 100`)을 계산하고, 마진율이 높은 순으로 10개를 조회하세요.

**힌트:** SELECT 절에서 산술 연산으로 마진율을 계산하세요. `ROUND()`로 소수점 정리, `price > 0` 조건으로 0 나눗셈 방지.

??? success "정답"
    ```sql
    SELECT
        name,
        price,
        cost_price,
        ROUND((price - cost_price) / price * 100, 1) AS margin_pct
    FROM products
    WHERE price > 0
    ORDER BY margin_pct DESC
    LIMIT 10;
    ```

---

### 15. 브랜드별 평균 가격과 상품 수

상품이 3개 이상인 브랜드만 대상으로, 평균 가격과 상품 수를 구하세요.

**힌트:** `GROUP BY brand` 후 `HAVING COUNT(*) >= 3`으로 그룹을 필터링하세요. `HAVING`은 집계 후 조건.

??? success "정답"
    ```sql
    SELECT
        brand,
        COUNT(*) AS product_count,
        ROUND(AVG(price), 2) AS avg_price,
        ROUND(MIN(price), 2) AS min_price,
        ROUND(MAX(price), 2) AS max_price
    FROM products
    GROUP BY brand
    HAVING COUNT(*) >= 3
    ORDER BY avg_price DESC;
    ```
