# 서브쿼리 완전 정복


## 기초 (1-7): WHERE 서브쿼리, IN/NOT IN

### 문제 1. 전체 평균 가격보다 비싼 상품의 이름과 가격을 조회하세요.

스칼라 서브쿼리를 사용하여 전체 상품의 평균 가격보다 비싼 상품만 골라내세요. 가격 내림차순, 상위 10개.

??? tip "힌트"
    `WHERE price > (SELECT AVG(price) FROM products)` 형태의 스칼라 서브쿼리를 사용합니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE price > (SELECT AVG(price) FROM products)
    ORDER BY price DESC
    LIMIT 10;
    ```

    | name | price |
    |------|-------|
    | (평균 초과 상품 1) | 2500000 |
    | ... | ... |


---


### 문제 2. 가장 비싼 상품의 이름, 가격, 카테고리 ID를 조회하세요.

서브쿼리로 최대 가격을 구한 뒤, 해당 가격과 일치하는 상품을 찾으세요.

??? tip "힌트"
    `WHERE price = (SELECT MAX(price) FROM products)` 형태로 최대값을 서브쿼리로 구합니다.

??? success "정답"
    ```sql
    SELECT name, price, category_id
    FROM products
    WHERE price = (SELECT MAX(price) FROM products);
    ```


---


### 문제 3. 주문을 한 번이라도 한 고객의 이름과 이메일을 조회하세요.

IN 서브쿼리를 사용하여 orders 테이블에 존재하는 customer_id를 가진 고객만 조회하세요. 이름순 정렬, 상위 15개.

??? tip "힌트"
    `WHERE id IN (SELECT customer_id FROM orders)` — 서브쿼리가 주문이 존재하는 고객 ID 목록을 반환합니다.

??? success "정답"
    ```sql
    SELECT name, email
    FROM customers
    WHERE id IN (SELECT customer_id FROM orders)
    ORDER BY name
    LIMIT 15;
    ```


---


### 문제 4. 리뷰를 한 번도 작성하지 않은 고객의 이름과 등급을 조회하세요.

NOT IN 서브쿼리를 사용하세요. 등급 내림차순(VIP, GOLD, SILVER, BRONZE), 이름순 정렬, 상위 15개.

??? tip "힌트"
    `WHERE id NOT IN (SELECT customer_id FROM reviews)` — reviews 테이블에 없는 고객을 찾습니다.

??? success "정답"
    ```sql
    SELECT name, grade
    FROM customers
    WHERE id NOT IN (SELECT customer_id FROM reviews)
    ORDER BY
        CASE grade
            WHEN 'VIP' THEN 1
            WHEN 'GOLD' THEN 2
            WHEN 'SILVER' THEN 3
            ELSE 4
        END,
        name
    LIMIT 15;
    ```


---


### 문제 5. 위시리스트에 담긴 적이 있는 상품의 이름과 가격을 조회하세요.

IN 서브쿼리로 wishlists 테이블에 존재하는 product_id를 가진 상품만 조회하세요. 가격 내림차순, 상위 10개.

??? tip "힌트"
    `WHERE id IN (SELECT product_id FROM wishlists)` — 위시리스트에 한 번이라도 등록된 상품 ID를 구합니다.

??? success "정답"
    ```sql
    SELECT name, price
    FROM products
    WHERE id IN (SELECT product_id FROM wishlists)
    ORDER BY price DESC
    LIMIT 10;
    ```


---


### 문제 6. 한 번도 주문되지 않은 상품의 이름과 재고를 조회하세요.

NOT IN 서브쿼리로 order_items에 한 번도 등장하지 않은 상품을 찾으세요.

??? tip "힌트"
    `WHERE id NOT IN (SELECT product_id FROM order_items)` — 주문 상세에 없는 상품을 필터링합니다.

??? success "정답"
    ```sql
    SELECT name, stock_qty
    FROM products
    WHERE id NOT IN (SELECT product_id FROM order_items)
    ORDER BY stock_qty DESC;
    ```


---


### 문제 7. 평균 주문 금액보다 큰 주문의 주문번호, 금액, 주문일을 조회하세요. 취소 제외.

스칼라 서브쿼리로 평균 주문 금액을 구하고, 이를 초과하는 주문만 필터링하세요. 금액 내림차순, 상위 10개.

??? tip "힌트"
    서브쿼리에서도 취소 주문을 제외해야 공정한 비교가 됩니다. 메인 쿼리와 서브쿼리 모두 `status NOT IN ('cancelled')` 조건을 적용하세요.

??? success "정답"
    ```sql
    SELECT order_number, total_amount, ordered_at
    FROM orders
    WHERE status NOT IN ('cancelled')
      AND total_amount > (
          SELECT AVG(total_amount)
          FROM orders
          WHERE status NOT IN ('cancelled')
      )
    ORDER BY total_amount DESC
    LIMIT 10;
    ```


---


## 응용 (8-14): FROM 서브쿼리, 상관 서브쿼리, SELECT 스칼라

### 문제 8. 카테고리별 평균 가격을 구한 뒤, 자기 카테고리 평균보다 비싼 상품을 조회하세요.

FROM 절 서브쿼리(인라인 뷰)로 카테고리별 평균 가격을 먼저 구하고, 이를 products와 JOIN하세요. 상위 15개.

??? tip "힌트"
    `FROM products AS p INNER JOIN (SELECT category_id, AVG(price) AS avg_price FROM products GROUP BY category_id) AS ca ON ...` — 인라인 뷰를 테이블처럼 JOIN합니다.

??? success "정답"
    ```sql
    SELECT p.name, p.price, ca.avg_price
    FROM products AS p
    INNER JOIN (
        SELECT category_id, ROUND(AVG(price), 2) AS avg_price
        FROM products
        GROUP BY category_id
    ) AS ca ON p.category_id = ca.category_id
    WHERE p.price > ca.avg_price
    ORDER BY p.price DESC
    LIMIT 15;
    ```


---


### 문제 9. 각 고객의 주문 횟수를 SELECT 절 스칼라 서브쿼리로 구하세요. 주문 3회 이상인 고객만, 주문 횟수 내림차순 15개.

SELECT 절에 서브쿼리를 넣어 각 행마다 값을 계산하는 스칼라 서브쿼리를 연습합니다.

??? tip "힌트"
    `SELECT name, (SELECT COUNT(*) FROM orders WHERE customer_id = c.id) AS order_count FROM customers AS c` — 외부 쿼리의 `c.id`를 서브쿼리에서 참조합니다.

??? success "정답"
    ```sql
    SELECT
        c.name,
        c.grade,
        (SELECT COUNT(*)
         FROM orders
         WHERE customer_id = c.id
           AND status NOT IN ('cancelled')) AS order_count
    FROM customers AS c
    WHERE (SELECT COUNT(*)
           FROM orders
           WHERE customer_id = c.id
             AND status NOT IN ('cancelled')) >= 3
    ORDER BY order_count DESC
    LIMIT 15;
    ```


---


### 문제 10. 상관 서브쿼리로 각 상품의 최근 리뷰 날짜를 함께 조회하세요. 상위 15개.

상관 서브쿼리(correlated subquery)는 외부 쿼리의 각 행에 대해 서브쿼리가 실행됩니다.

??? tip "힌트"
    `(SELECT MAX(created_at) FROM reviews WHERE product_id = p.id)` — 외부 쿼리의 `p.id`를 참조하는 상관 서브쿼리입니다.

??? success "정답"
    ```sql
    SELECT
        p.name,
        p.price,
        (SELECT MAX(created_at)
         FROM reviews
         WHERE product_id = p.id) AS last_review_at
    FROM products AS p
    ORDER BY last_review_at DESC NULLS LAST
    LIMIT 15;
    ```


---


### 문제 11. 고객별 총 주문 금액을 FROM 서브쿼리로 구한 뒤, 상위 10명을 조회하세요.

FROM 절에서 주문을 집계한 파생 테이블을 만들고, customers와 JOIN하세요.

??? tip "힌트"
    `FROM (SELECT customer_id, SUM(total_amount) AS total_spent FROM orders WHERE ... GROUP BY customer_id) AS os` — 파생 테이블을 별칭으로 사용합니다.

??? success "정답"
    ```sql
    SELECT c.name, c.grade, os.total_spent
    FROM customers AS c
    INNER JOIN (
        SELECT customer_id, ROUND(SUM(total_amount), 2) AS total_spent
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ) AS os ON c.id = os.customer_id
    ORDER BY os.total_spent DESC
    LIMIT 10;
    ```


---


### 문제 12. EXISTS를 사용하여 리뷰가 1건 이상 있는 상품만 조회하세요.

EXISTS는 서브쿼리의 결과가 존재하는지만 확인합니다. IN과 비교해 보세요.

??? tip "힌트"
    `WHERE EXISTS (SELECT 1 FROM reviews WHERE product_id = p.id)` — 서브쿼리가 한 행이라도 반환하면 TRUE입니다.

??? success "정답"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    WHERE EXISTS (
        SELECT 1
        FROM reviews
        WHERE product_id = p.id
    )
    ORDER BY p.name
    LIMIT 15;
    ```


---


### 문제 13. 위시리스트에 담았지만 한 번도 주문하지 않은 고객-상품 조합을 찾으세요. 최근 20개.

NOT EXISTS 상관 서브쿼리로 해당 고객이 해당 상품을 주문한 이력이 있는지 확인합니다.

??? tip "힌트"
    `WHERE NOT EXISTS (SELECT 1 FROM order_items AS oi INNER JOIN orders AS o ON ... WHERE o.customer_id = w.customer_id AND oi.product_id = w.product_id)` — 두 조건을 동시에 확인하는 상관 서브쿼리입니다.

??? success "정답"
    ```sql
    SELECT
        c.name AS customer,
        p.name AS product,
        w.created_at AS wishlisted_at
    FROM wishlists AS w
    INNER JOIN customers AS c ON w.customer_id = c.id
    INNER JOIN products AS p ON w.product_id = p.id
    WHERE NOT EXISTS (
        SELECT 1
        FROM order_items AS oi
        INNER JOIN orders AS o ON oi.order_id = o.id
        WHERE o.customer_id = w.customer_id
          AND oi.product_id = w.product_id
          AND o.status NOT IN ('cancelled')
    )
    ORDER BY w.created_at DESC
    LIMIT 20;
    ```


---


### 문제 14. 각 카테고리에서 가장 비싼 상품의 이름과 가격을 구하세요.

상관 서브쿼리로 각 상품의 가격이 해당 카테고리 최대 가격과 같은지 비교합니다.

??? tip "힌트"
    `WHERE p.price = (SELECT MAX(price) FROM products WHERE category_id = p.category_id)` — 같은 카테고리 내 최대 가격을 상관 서브쿼리로 구합니다.

??? success "정답"
    ```sql
    SELECT p.name, p.price, p.category_id
    FROM products AS p
    WHERE p.price = (
        SELECT MAX(price)
        FROM products
        WHERE category_id = p.category_id
    )
    ORDER BY p.price DESC;
    ```


---


## 실전 (15-20): 중첩 서브쿼리, 다단계, 서브쿼리 vs JOIN 비교

### 문제 15. VIP 고객이 주문한 상품 중 평점 4 이상인 상품의 이름을 구하세요.

다단계 서브쿼리: 먼저 VIP 고객 ID를 구하고, 그 고객의 주문에서 상품 ID를 구하고, 평점 조건으로 필터링합니다.

??? tip "힌트"
    `WHERE id IN (SELECT product_id FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE grade = 'VIP')))` — 3단계 중첩입니다. 단, 이렇게 깊은 중첩은 가독성이 떨어지므로 실무에서는 JOIN이나 CTE를 권장합니다.

??? success "정답"
    ```sql
    SELECT DISTINCT p.name, p.price
    FROM products AS p
    WHERE p.id IN (
        SELECT oi.product_id
        FROM order_items AS oi
        WHERE oi.order_id IN (
            SELECT o.id
            FROM orders AS o
            WHERE o.status NOT IN ('cancelled')
              AND o.customer_id IN (
                  SELECT id FROM customers WHERE grade = 'VIP'
              )
        )
    )
    AND p.id IN (
        SELECT product_id
        FROM reviews
        GROUP BY product_id
        HAVING AVG(rating) >= 4.0
    )
    ORDER BY p.price DESC
    LIMIT 15;
    ```


---


### 문제 16. 전체 평균 주문 금액과 자신의 평균 주문 금액을 비교하여, 전체 평균보다 높은 고객을 찾으세요.

FROM 서브쿼리로 고객별 평균을 구하고, WHERE에서 전체 평균 스칼라 서브쿼리와 비교합니다.

??? tip "힌트"
    파생 테이블에서 고객별 평균 주문 금액을 구한 뒤, `WHERE avg_amount > (SELECT AVG(total_amount) FROM orders ...)` 조건으로 필터링합니다.

??? success "정답"
    ```sql
    SELECT
        c.name,
        c.grade,
        ca.avg_amount,
        ca.order_count
    FROM customers AS c
    INNER JOIN (
        SELECT
            customer_id,
            ROUND(AVG(total_amount), 2) AS avg_amount,
            COUNT(*) AS order_count
        FROM orders
        WHERE status NOT IN ('cancelled')
        GROUP BY customer_id
    ) AS ca ON c.id = ca.customer_id
    WHERE ca.avg_amount > (
        SELECT AVG(total_amount)
        FROM orders
        WHERE status NOT IN ('cancelled')
    )
    ORDER BY ca.avg_amount DESC
    LIMIT 15;
    ```


---


### 문제 17. 상품별 판매 수량이 전체 상품 평균 판매 수량보다 많은 상품을 찾으세요.

FROM 서브쿼리 안에 집계를, WHERE에서 다시 서브쿼리를 사용하는 이중 구조입니다.

??? tip "힌트"
    먼저 상품별 총 판매량을 파생 테이블로 구합니다. 그 다음 `WHERE total_qty > (SELECT AVG(total_qty) FROM (...))` 형태로 평균과 비교하세요. SQLite에서는 서브쿼리 안에 서브쿼리를 넣을 수 있습니다.

??? success "정답"
    ```sql
    SELECT
        p.name,
        ps.total_qty
    FROM products AS p
    INNER JOIN (
        SELECT product_id, SUM(quantity) AS total_qty
        FROM order_items
        GROUP BY product_id
    ) AS ps ON p.id = ps.product_id
    WHERE ps.total_qty > (
        SELECT AVG(total_qty)
        FROM (
            SELECT SUM(quantity) AS total_qty
            FROM order_items
            GROUP BY product_id
        )
    )
    ORDER BY ps.total_qty DESC
    LIMIT 15;
    ```


---


### 문제 18. 리뷰 평점이 해당 상품의 평균 평점보다 낮은 리뷰를 찾으세요. 최근 15개.

상관 서브쿼리를 WHERE 절에서 사용하여 각 리뷰의 평점과 해당 상품의 평균 평점을 비교합니다.

??? tip "힌트"
    `WHERE r.rating < (SELECT AVG(rating) FROM reviews WHERE product_id = r.product_id)` — 각 리뷰에 대해 같은 상품의 평균 평점을 상관 서브쿼리로 구합니다.

??? success "정답"
    ```sql
    SELECT
        r.id,
        p.name AS product,
        r.rating,
        ROUND((SELECT AVG(rating) FROM reviews WHERE product_id = r.product_id), 2) AS avg_rating,
        r.title,
        r.created_at
    FROM reviews AS r
    INNER JOIN products AS p ON r.product_id = p.id
    WHERE r.rating < (
        SELECT AVG(rating)
        FROM reviews
        WHERE product_id = r.product_id
    )
    ORDER BY r.created_at DESC
    LIMIT 15;
    ```


---


### 문제 19. 서브쿼리 vs JOIN 비교: "리뷰를 작성한 고객" 목록을 두 가지 방법으로 작성하세요.

같은 결과를 (A) IN 서브쿼리, (B) JOIN으로 각각 작성하고 차이를 이해하세요.

??? tip "힌트"
    (A) `WHERE id IN (SELECT customer_id FROM reviews)`, (B) `INNER JOIN reviews ON ...`에서 DISTINCT를 사용합니다. 두 쿼리의 결과는 동일하지만 실행 방식이 다릅니다.

??? success "정답"
    ```sql
    -- (A) IN 서브쿼리 방식
    SELECT name, email
    FROM customers
    WHERE id IN (SELECT customer_id FROM reviews)
    ORDER BY name
    LIMIT 10;

    -- (B) JOIN 방식 (DISTINCT 필요)
    SELECT DISTINCT c.name, c.email
    FROM customers AS c
    INNER JOIN reviews AS r ON c.id = r.customer_id
    ORDER BY c.name
    LIMIT 10;
    ```

    두 쿼리는 같은 결과를 반환합니다. 일반적으로:

    - **IN 서브쿼리**: 중복 제거가 자동이라 DISTINCT 불필요. 서브쿼리 결과가 작을 때 효율적.
    - **JOIN**: 추가 컬럼(리뷰 내용 등)을 함께 가져올 때 유리. 대규모 데이터에서 더 최적화되기도 함.


---


### 문제 20. 3개 이상의 카테고리에서 상품을 구매한 고객의 이름과 구매 카테고리 수를 구하세요.

FROM 서브쿼리로 고객별 구매 카테고리 수를 집계한 뒤, 3개 이상인 고객만 필터링하세요.

??? tip "힌트"
    orders → order_items → products를 JOIN하여 고객별 DISTINCT category_id 수를 구합니다. 이 집계를 파생 테이블로 만든 뒤 customers와 JOIN하세요.

??? success "정답"
    ```sql
    SELECT c.name, c.grade, cc.cat_count
    FROM customers AS c
    INNER JOIN (
        SELECT
            o.customer_id,
            COUNT(DISTINCT p.category_id) AS cat_count
        FROM orders AS o
        INNER JOIN order_items AS oi ON o.id = oi.order_id
        INNER JOIN products AS p ON oi.product_id = p.id
        WHERE o.status NOT IN ('cancelled')
        GROUP BY o.customer_id
        HAVING COUNT(DISTINCT p.category_id) >= 3
    ) AS cc ON c.id = cc.customer_id
    ORDER BY cc.cat_count DESC, c.name
    LIMIT 15;
    ```


---
