# JOIN 마스터

<div class="grid cards" markdown>

-   :fontawesome-solid-database:{ .lg .middle } __사용 테이블__

    ---

    `orders` — 주문<br>
    `customers` — 고객<br>
    `order_items` — 주문 상세<br>
    `products` — 상품<br>
    `categories` — 카테고리<br>
    `suppliers` — 공급업체<br>
    `shipping` — 배송<br>
    `reviews` — 리뷰<br>
    `staff` — 직원<br>
    `wishlists` — 위시리스트<br>
    `complaints` — 불만 접수<br>
    `product_tags` — 상품 태그<br>
    `tags` — 태그<br>
    `product_qna` — 상품 Q&A<br>
    `calendar` — 날짜 참조

-   :fontawesome-solid-graduation-cap:{ .lg .middle } __학습 범위__

    ---

    `INNER JOIN`<br>
    `LEFT JOIN`<br>
    anti-join<br>
    다중 테이블 JOIN<br>
    Self-JOIN<br>
    JOIN + `GROUP BY` + 집계

</div>

!!! info "시작하기 전에"
    이 연습은 **중급 8~9강**(INNER JOIN, LEFT JOIN)에서 배운 내용을 실전에 적용합니다.
    GROUP BY, 집계 함수, ORDER BY, LIMIT도 함께 사용합니다.

---

## 기초 (1~8)

두 테이블 INNER JOIN을 연습합니다.

---

### 문제 1

**각 상품의 이름, 가격, 카테고리명을 조회하세요. 가격 내림차순으로 10개만.**

??? tip "힌트"
    `products`와 `categories`를 `category_id`로 `INNER JOIN`하고, `ORDER BY price DESC LIMIT 10`.

??? success "정답"
    ```sql
    SELECT p.name, p.price, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    ORDER BY p.price DESC
    LIMIT 10;
    ```

    **결과 (10행):**

    | name | price | category |
    |------|-------|----------|
    | ASUS ROG Strix GT35 | 4314800 | 데스크톱 |
    | ASUS ROG Zephyrus G16 | 4284100 | 노트북 |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] ... | 4226200 | 그래픽카드 |
    | Razer Blade 18 블랙 | 4182100 | 노트북 |
    | Razer Blade 16 실버 | 4123800 | 노트북 |

    > 상위 5행만 표시. 총 10행 반환.

---

### 문제 2

**상품명, 카테고리명, 공급업체명을 함께 조회하세요. 상품명 기준 알파벳순 20개.**

??? tip "힌트"
    `products`에서 `categories`와 `suppliers` 두 테이블을 각각 INNER JOIN으로 연결합니다. 하나의 SELECT에 JOIN을 2번 쓸 수 있습니다.

??? success "정답"
    ```sql
    SELECT
        p.name AS product,
        cat.name AS category,
        s.company_name AS supplier
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    INNER JOIN suppliers AS s ON p.supplier_id = s.id
    ORDER BY p.name
    LIMIT 20;
    ```

    **결과 (상위 5행):**

    | product | category | supplier |
    |---------|----------|----------|
    | APC Back-UPS Pro Gaming BGM1500B 블랙 | UPS/전원 | (주)디지털파워 |
    | ASRock B650 PG Riptide WiFi | 메인보드 | (주)컴퓨존 |
    | ASRock X670E Steel Legend 실버 | 메인보드 | (주)컴퓨존 |
    | ASUS ExpertBook B5 화이트 | 노트북 | (주)에이수스코리아 |
    | ASUS PCE-BE92BT | 네트워크 | (주)에이수스코리아 |

---

### 문제 3

**주문별 고객 이름과 주문 금액을 조회하세요. 최근 주문 10건만.**

??? tip "힌트"
    `orders`와 `customers`를 `customer_id`로 JOIN합니다. `ORDER BY ordered_at DESC LIMIT 10`.

??? success "정답"
    ```sql
    SELECT
        o.order_number,
        c.name AS customer_name,
        o.total_amount,
        o.ordered_at
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    ORDER BY o.ordered_at DESC
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | order_number | customer_name | total_amount | ordered_at |
    |--------------|---------------|-------------|------------|
    | ORD-20251231-... | 김** | 285600 | 2025-12-31 ... |
    | ORD-20251231-... | 이** | 1523400 | 2025-12-31 ... |
    | ORD-20251231-... | 박** | 67800 | 2025-12-31 ... |
    | ORD-20251231-... | 최** | 432100 | 2025-12-31 ... |
    | ORD-20251231-... | 정** | 891200 | 2025-12-31 ... |

    > 실제 데이터에 따라 이름과 금액이 달라집니다.

---

### 문제 4

**주문 상세(order_items)와 상품 정보를 조합하여, 각 주문 항목의 상품명과 수량, 단가를 조회하세요. 최근 15건.**

??? tip "힌트"
    `order_items`와 `products`를 `product_id`로 JOIN합니다. `ORDER BY oi.id DESC LIMIT 15`.

??? success "정답"
    ```sql
    SELECT
        oi.order_id,
        p.name AS product_name,
        p.brand,
        oi.quantity,
        oi.unit_price
    FROM order_items AS oi
    INNER JOIN products AS p ON oi.product_id = p.id
    ORDER BY oi.id DESC
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | order_id | product_name | brand | quantity | unit_price |
    |----------|-------------|-------|----------|------------|
    | 34908 | 삼성 DDR4 32GB PC4-25600 | 삼성전자 | 2 | 49100 |
    | 34907 | Logitech G502 X 블랙 | Logitech | 1 | 89700 |
    | 34907 | Dell U2724D | Dell | 1 | 853600 |
    | 34906 | 커세어 RM850x 블랙 | Corsair | 3 | 178200 |
    | 34905 | ASUS PCE-BE92BT | ASUS | 1 | 48800 |

    > 실제 데이터에 따라 결과가 달라집니다.

---

### 문제 5

**배송 완료된 주문의 주문번호, 택배사, 배송완료일을 조회하세요. 최근 배송완료순 10건.**

??? tip "힌트"
    `shipping`과 `orders`를 `order_id`로 JOIN합니다. `WHERE sh.status = 'delivered'`.

??? success "정답"
    ```sql
    SELECT
        o.order_number,
        sh.carrier,
        sh.delivered_at
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE sh.status = 'delivered'
    ORDER BY sh.delivered_at DESC
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | order_number | carrier | delivered_at |
    |--------------|---------|-------------|
    | ORD-20251230-... | CJ대한통운 | 2025-12-31 ... |
    | ORD-20251229-... | 한진택배 | 2025-12-31 ... |
    | ORD-20251229-... | 로젠택배 | 2025-12-30 ... |
    | ORD-20251228-... | 우체국택배 | 2025-12-30 ... |
    | ORD-20251228-... | CJ대한통운 | 2025-12-30 ... |

---

### 문제 6

**리뷰와 상품 정보를 조합하여, 평점 5점 리뷰의 상품명, 리뷰 제목, 작성일을 조회하세요. 최근 10건.**

??? tip "힌트"
    `reviews`와 `products`를 `product_id`로 JOIN합니다. `WHERE r.rating = 5`.

??? success "정답"
    ```sql
    SELECT
        p.name AS product_name,
        r.title AS review_title,
        r.rating,
        r.created_at
    FROM reviews AS r
    INNER JOIN products AS p ON r.product_id = p.id
    WHERE r.rating = 5
    ORDER BY r.created_at DESC
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | product_name | review_title | rating | created_at |
    |-------------|-------------|--------|------------|
    | 삼성 DDR4 32GB PC4-25600 | 완벽합니다 | 5 | 2025-12-... |
    | Logitech G502 X 블랙 | 강력 추천! | 5 | 2025-12-... |
    | Dell U2724D | 최고의 모니터 | 5 | 2025-12-... |
    | 커세어 RM850x 블랙 | 만족합니다 | 5 | 2025-12-... |
    | ASUS PCE-BE92BT | 가성비 좋아요 | 5 | 2025-11-... |

    > 리뷰 제목(title)은 NULL일 수 있습니다.

---

### 문제 7

**공급업체별 공급 상품 수를 구하세요. 상품 수 내림차순.**

??? tip "힌트"
    `suppliers`와 `products`를 JOIN하고 `GROUP BY`로 공급업체별 집계합니다. `COUNT(p.id)`로 상품 수를 셉니다.

??? success "정답"
    ```sql
    SELECT
        s.company_name,
        COUNT(p.id) AS product_count
    FROM suppliers AS s
    INNER JOIN products AS p ON s.id = p.supplier_id
    GROUP BY s.id, s.company_name
    ORDER BY product_count DESC
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | company_name | product_count |
    |-------------|--------------|
    | (주)컴퓨존 | 18 |
    | (주)에이수스코리아 | 15 |
    | (주)디지털파워 | 12 |
    | (주)제이씨현시스템 | 11 |
    | (주)웨이코스 | 10 |

    > 실제 데이터에 따라 수치가 달라집니다.

---

### 문제 8

**각 카테고리의 이름과 소속 상품의 평균 가격을 조회하세요. 평균 가격 내림차순 10개.**

??? tip "힌트"
    `categories`와 `products`를 JOIN합니다. `GROUP BY cat.id, cat.name`으로 카테고리별 `AVG(p.price)` 집계.

??? success "정답"
    ```sql
    SELECT
        cat.name AS category,
        COUNT(p.id) AS product_count,
        ROUND(AVG(p.price), 0) AS avg_price
    FROM categories AS cat
    INNER JOIN products AS p ON cat.id = p.category_id
    GROUP BY cat.id, cat.name
    ORDER BY avg_price DESC
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | category | product_count | avg_price |
    |----------|--------------|-----------|
    | 노트북 | 24 | 2145600 |
    | 데스크톱 | 18 | 1987300 |
    | 그래픽카드 | 22 | 1256800 |
    | 모니터 | 20 | 645200 |
    | 메인보드 | 16 | 423100 |

    > 실제 데이터에 따라 수치가 달라집니다.

---

## 응용 (9~16)

LEFT JOIN, anti-join, 3테이블 JOIN, JOIN + GROUP BY를 연습합니다.

---

### 문제 9

**한 번도 리뷰를 받지 않은 상품의 이름과 가격을 조회하세요. 가격 내림차순.**

??? tip "힌트"
    LEFT JOIN으로 `products`에 `reviews`를 연결한 뒤, `WHERE r.id IS NULL`로 매칭되지 않는 행을 찾습니다. 이것이 **anti-join** 패턴입니다.

??? success "정답"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id
    WHERE r.id IS NULL
    ORDER BY p.price DESC;
    ```

    **결과 (상위 5행):**

    | name | price |
    |------|-------|
    | ASUS TUF Gaming RTX 5080 화이트 | 3812000 |
    | 주연 리오나인 i7 시스템 실버 | 1102700 |
    | WD Elements 2TB 블랙 | 265600 |
    | 소니 WH-CH720N 실버 | 249800 |
    | JBL Quantum ONE 화이트 | 179400 |

    > 리뷰가 0건인 상품만 나옵니다. 단종 상품이 많을 수 있습니다.

---

### 문제 10

**한 번도 주문하지 않은 고객의 이름과 가입일을 조회하세요. 가입일 오름차순.**

??? tip "힌트"
    `customers LEFT JOIN orders` 후 `WHERE o.id IS NULL`로 주문이 없는 고객만 필터링합니다.

??? success "정답"
    ```sql
    SELECT c.name, c.grade, c.created_at
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    WHERE o.id IS NULL
    ORDER BY c.created_at
    LIMIT 20;
    ```

    **결과 (상위 5행):**

    | name | grade | created_at |
    |------|-------|------------|
    | 김** | BRONZE | 2016-03-... |
    | 이** | BRONZE | 2016-05-... |
    | 박** | BRONZE | 2016-08-... |
    | 최** | BRONZE | 2016-11-... |
    | 정** | BRONZE | 2017-01-... |

    > 주문이 0건인 고객만 표시됩니다. 대부분 BRONZE 등급입니다.

---

### 문제 11

**위시리스트에 담았지만 아직 구매하지 않은 상품의 이름, 가격, 찜한 고객 수를 조회하세요.**

??? tip "힌트"
    `wishlists`와 `products`를 JOIN합니다. `WHERE w.is_purchased = 0`으로 미구매 필터. `GROUP BY`로 상품별 집계.

??? success "정답"
    ```sql
    SELECT
        p.name,
        p.price,
        COUNT(w.id) AS wishlist_count
    FROM wishlists AS w
    INNER JOIN products AS p ON w.product_id = p.id
    WHERE w.is_purchased = 0
    GROUP BY p.id, p.name, p.price
    ORDER BY wishlist_count DESC
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | name | price | wishlist_count |
    |------|-------|---------------|
    | 삼성 DDR4 32GB PC4-25600 | 49100 | 12 |
    | Logitech G502 X 블랙 | 89700 | 10 |
    | Dell U2724D | 853600 | 9 |
    | 커세어 RM850x 블랙 | 178200 | 8 |
    | ASUS PCE-BE92BT | 48800 | 7 |

    > 실제 데이터에 따라 수치가 달라집니다.

---

### 문제 12

**최근 주문 5건의 주문번호, 고객명, 상품명, 수량, 단가를 조회하세요. (4테이블 JOIN)**

??? tip "힌트"
    `orders` -> `customers`, `orders` -> `order_items` -> `products` 4개 테이블을 INNER JOIN으로 연결합니다.

??? success "정답"
    ```sql
    SELECT
        o.order_number,
        c.name AS customer,
        p.name AS product,
        oi.quantity,
        oi.unit_price
    FROM orders AS o
    INNER JOIN customers AS c ON o.customer_id = c.id
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN products AS p ON oi.product_id = p.id
    ORDER BY o.ordered_at DESC
    LIMIT 5;
    ```

    **결과 (5행):**

    | order_number | customer | product | quantity | unit_price |
    |--------------|----------|---------|----------|------------|
    | ORD-20251231-... | 김** | 삼성 DDR4 32GB... | 2 | 49100 |
    | ORD-20251231-... | 이** | Logitech G502 X... | 1 | 89700 |
    | ORD-20251231-... | 박** | Dell U2724D | 1 | 853600 |
    | ORD-20251230-... | 최** | 커세어 RM850x... | 3 | 178200 |
    | ORD-20251230-... | 정** | ASUS PCE-BE92BT | 1 | 48800 |

---

### 문제 13

**리뷰가 5개 이상인 상품의 이름, 평균 평점, 리뷰 수를 구하세요. 평균 평점 내림차순.**

??? tip "힌트"
    `products JOIN reviews`로 연결 후 `GROUP BY`와 `HAVING COUNT(r.id) >= 5`로 필터링합니다.

??? success "정답"
    ```sql
    SELECT
        p.name,
        ROUND(AVG(r.rating), 2) AS avg_rating,
        COUNT(r.id) AS review_count
    FROM products AS p
    INNER JOIN reviews AS r ON p.id = r.product_id
    GROUP BY p.id, p.name
    HAVING COUNT(r.id) >= 5
    ORDER BY avg_rating DESC
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | name | avg_rating | review_count |
    |------|-----------|-------------|
    | Dell U2724D | 4.85 | 12 |
    | Logitech G502 X 블랙 | 4.72 | 18 |
    | 삼성 DDR4 32GB PC4-25600 | 4.65 | 24 |
    | 커세어 RM850x 블랙 | 4.58 | 15 |
    | ASUS PCE-BE92BT | 4.42 | 9 |

    > 실제 데이터에 따라 수치가 달라집니다.

---

### 문제 14

**직원 계층 구조 (Self-JOIN): 모든 직원과 그 상사(매니저)의 이름을 함께 조회하세요.**

??? tip "힌트"
    `staff` 테이블을 자기 자신과 LEFT JOIN합니다. `staff AS s LEFT JOIN staff AS m ON s.manager_id = m.id`. 매니저가 없으면 NULL로 표시됩니다.

??? success "정답"
    ```sql
    SELECT
        s.id,
        s.name       AS staff_name,
        s.department,
        s.role,
        m.name       AS manager_name,
        m.department AS manager_department
    FROM staff AS s
    LEFT JOIN staff AS m ON s.manager_id = m.id
    ORDER BY s.department, s.name;
    ```

    **결과 (상위 5행):**

    | id | staff_name | department | role | manager_name | manager_department |
    |----|-----------|-----------|------|-------------|-------------------|
    | 1 | 김** | CS | manager | 박** | 경영 |
    | 5 | 이** | CS | staff | 김** | CS |
    | 8 | 최** | CS | staff | 김** | CS |
    | 2 | 박** | 경영 | admin | NULL | NULL |
    | 3 | 정** | 마케팅 | manager | 박** | 경영 |

    > manager_name이 NULL이면 최상위 관리자입니다.

---

### 문제 15

**카테고리별 총 매출과 판매 수량을 구하세요. 취소 주문 제외.**

??? tip "힌트"
    `order_items` -> `products` -> `categories`를 JOIN하고, `orders`도 JOIN하여 취소 주문을 제외합니다. 4테이블 JOIN + GROUP BY.

??? success "정답"
    ```sql
    SELECT
        cat.name AS category,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 0) AS revenue
    FROM order_items AS oi
    INNER JOIN orders AS o ON oi.order_id = o.id
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY cat.name
    ORDER BY revenue DESC;
    ```

    **결과 (상위 5행):**

    | category | units_sold | revenue |
    |----------|-----------|---------|
    | 노트북 | 4521 | 8745230000 |
    | 데스크톱 | 3218 | 5632410000 |
    | 그래픽카드 | 5842 | 4521780000 |
    | 모니터 | 6234 | 3214560000 |
    | 메인보드 | 4123 | 1523670000 |

    > 실제 데이터에 따라 수치가 달라집니다.

---

### 문제 16

**주문이 없는 날 찾기: calendar 테이블을 활용하여 2024년에 주문이 하나도 없는 날짜를 찾으세요.**

??? tip "힌트"
    `calendar` LEFT JOIN 주문 날짜(서브쿼리). `WHERE o.order_date IS NULL`로 주문 없는 날 필터.

??? success "정답"
    ```sql
    SELECT
        cal.date_key,
        cal.day_name,
        cal.is_weekend,
        cal.is_holiday,
        cal.holiday_name
    FROM calendar AS cal
    LEFT JOIN (
        SELECT DISTINCT SUBSTR(ordered_at, 1, 10) AS order_date
        FROM orders
    ) AS od ON cal.date_key = od.order_date
    WHERE cal.year = 2024
      AND od.order_date IS NULL
    ORDER BY cal.date_key;
    ```

    **결과 (상위 5행):**

    | date_key | day_name | is_weekend | is_holiday | holiday_name |
    |----------|----------|-----------|-----------|-------------|
    | 2024-01-01 | 월요일 | 0 | 1 | 신정 |
    | 2024-02-09 | 금요일 | 0 | 1 | 설날 연휴 |
    | 2024-02-10 | 토요일 | 1 | 1 | 설날 |
    | 2024-02-11 | 일요일 | 1 | 1 | 설날 연휴 |
    | 2024-02-12 | 월요일 | 0 | 1 | 대체공휴일 |

    > 공휴일에 주문이 없는 경우가 많습니다. 실제 데이터에 따라 결과가 달라집니다.

---

## 실전 (17~25)

4개 이상 테이블 JOIN, 복잡한 비즈니스 쿼리를 연습합니다.

---

### 문제 17

**각 고객의 이름, 등급, 주문 수, 총 구매 금액을 조회하세요. 총 구매 금액 상위 10명. 취소 제외.**

??? tip "힌트"
    `customers JOIN orders` 후 `GROUP BY`로 집계합니다. `COUNT`와 `SUM`을 함께 사용하고 `WHERE o.status NOT IN ('cancelled')`.

??? success "정답"
    ```sql
    SELECT
        c.name,
        c.grade,
        COUNT(o.id) AS order_count,
        ROUND(SUM(o.total_amount), 0) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```

    **결과 (상위 5행):**

    | name | grade | order_count | total_spent |
    |------|-------|------------|------------|
    | 김** | VIP | 87 | 45231000 |
    | 이** | VIP | 72 | 38456000 |
    | 박** | VIP | 65 | 32187000 |
    | 최** | GOLD | 58 | 28945000 |
    | 정** | VIP | 54 | 26312000 |

    > 실제 데이터에 따라 수치가 달라집니다.

---

### 문제 18

**택배사별 배송 건수, 배송 완료 건수, 완료율(%)을 구하세요.**

??? tip "힌트"
    `GROUP BY carrier`. `SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END)`으로 조건부 집계합니다. 완료율은 `100.0 * 완료 / 전체`입니다.

??? success "정답"
    ```sql
    SELECT
        carrier,
        COUNT(*) AS total,
        SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered,
        ROUND(100.0 * SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) / COUNT(*), 1) AS delivery_rate
    FROM shipping
    GROUP BY carrier
    ORDER BY total DESC;
    ```

    **결과:**

    | carrier | total | delivered | delivery_rate |
    |---------|-------|-----------|--------------|
    | CJ대한통운 | 9876 | 9234 | 93.5 |
    | 한진택배 | 8765 | 8123 | 92.7 |
    | 로젠택배 | 7654 | 7012 | 91.6 |
    | 우체국택배 | 6812 | 6345 | 93.1 |

    > 실제 데이터에 따라 수치가 달라집니다.

---

### 문제 19

**공급업체별 공급 상품 수, 평균 가격, 최고가를 구하세요. 상품 수 내림차순.**

??? tip "힌트"
    `suppliers JOIN products`로 연결 후 `GROUP BY`로 집계합니다. `COUNT`, `AVG`, `MAX` 함수 사용.

??? success "정답"
    ```sql
    SELECT
        s.company_name,
        COUNT(p.id) AS product_count,
        ROUND(AVG(p.price), 0) AS avg_price,
        MAX(p.price) AS max_price
    FROM suppliers AS s
    INNER JOIN products AS p ON s.id = p.supplier_id
    GROUP BY s.id, s.company_name
    ORDER BY product_count DESC
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | company_name | product_count | avg_price | max_price |
    |-------------|--------------|-----------|-----------|
    | (주)컴퓨존 | 18 | 645200 | 2987500 |
    | (주)에이수스코리아 | 15 | 1523400 | 4314800 |
    | (주)디지털파워 | 12 | 312500 | 891200 |
    | (주)제이씨현시스템 | 11 | 876300 | 1744000 |
    | (주)웨이코스 | 10 | 234100 | 584100 |

    > 실제 데이터에 따라 수치가 달라집니다.

---

### 문제 20

**배송 완료된 주문의 평균 배송 소요일(주문일 -> 배송완료일)을 택배사별로 구하세요.**

??? tip "힌트"
    `shipping JOIN orders`로 연결합니다. `JULIANDAY(delivered_at) - JULIANDAY(ordered_at)`로 날짜 차이를 계산합니다.

??? success "정답"
    ```sql
    SELECT
        sh.carrier,
        COUNT(*) AS delivered_count,
        ROUND(AVG(JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at)), 1) AS avg_days,
        MIN(CAST(JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at) AS INTEGER)) AS min_days,
        MAX(CAST(JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at) AS INTEGER)) AS max_days
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE sh.status = 'delivered'
      AND sh.delivered_at IS NOT NULL
    GROUP BY sh.carrier
    ORDER BY avg_days;
    ```

    **결과:**

    | carrier | delivered_count | avg_days | min_days | max_days |
    |---------|----------------|----------|----------|----------|
    | CJ대한통운 | 9234 | 2.1 | 1 | 5 |
    | 우체국택배 | 6345 | 2.3 | 1 | 6 |
    | 한진택배 | 8123 | 2.4 | 1 | 5 |
    | 로젠택배 | 7012 | 2.6 | 1 | 7 |

    > 실제 데이터에 따라 수치가 달라집니다.

---

### 문제 21

**"Gaming" 태그가 달린 상품의 이름, 브랜드, 가격, 카테고리를 조회하세요. (M:N JOIN)**

??? tip "힌트"
    `product_tags` -> `tags`로 태그 이름 필터, `product_tags` -> `products` -> `categories`로 상품/카테고리 정보를 가져옵니다.

??? success "정답"
    ```sql
    SELECT
        p.name AS product_name,
        p.brand,
        p.price,
        cat.name AS category
    FROM product_tags AS pt
    INNER JOIN tags AS t ON pt.tag_id = t.id
    INNER JOIN products AS p ON pt.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE t.name = 'Gaming'
      AND p.is_active = 1
    ORDER BY p.price DESC;
    ```

    **결과 (상위 5행):**

    | product_name | brand | price | category |
    |-------------|-------|-------|----------|
    | ASUS ROG Strix GT35 | ASUS | 4314800 | 데스크톱 |
    | Razer Blade 18 블랙 | Razer | 4182100 | 노트북 |
    | Razer Blade 16 실버 | Razer | 4123800 | 노트북 |
    | MSI GeForce RTX 4070 Ti Super GAMING X | MSI | 1744000 | 그래픽카드 |
    | ASUS ROG Strix Scar 16 실버 | ASUS | 1586000 | 노트북 |

    > 실제 데이터에 따라 결과가 달라집니다.

---

### 문제 22

**Q&A 스레드 조회 (Self-JOIN): 상품 Q&A에서 질문과 답변을 한 행에 보여주세요.**

??? tip "힌트"
    질문: `parent_id IS NULL`. 답변: `parent_id`가 질문의 `id`를 참조합니다. 질문(q) LEFT JOIN 답변(a) ON `a.parent_id = q.id`.

??? success "정답"
    ```sql
    SELECT
        p.name        AS product_name,
        q.content     AS question,
        c.name        AS asked_by,
        q.created_at  AS asked_at,
        a.content     AS answer,
        s.name        AS answered_by,
        a.created_at  AS answered_at
    FROM product_qna AS q
    INNER JOIN products AS p ON q.product_id = p.id
    LEFT JOIN customers AS c ON q.customer_id = c.id
    LEFT JOIN product_qna AS a ON a.parent_id = q.id
    LEFT JOIN staff AS s ON a.staff_id = s.id
    WHERE q.parent_id IS NULL
    ORDER BY q.created_at DESC
    LIMIT 20;
    ```

    **결과 (상위 3행):**

    | product_name | question | asked_by | asked_at | answer | answered_by | answered_at |
    |-------------|----------|----------|----------|--------|------------|------------|
    | Dell U2724D | 이 모니터 높이 조절... | 김** | 2025-12-... | 네, 높이 조절 가능... | 이** | 2025-12-... |
    | 삼성 DDR4 32GB... | DDR5와 호환 가능한가요? | 박** | 2025-11-... | DDR4와 DDR5는... | 최** | 2025-11-... |
    | Logitech G502 X... | 무선 버전이 있나요? | 정** | 2025-11-... | NULL | NULL | NULL |

    > 답변이 없는 질문은 answer/answered_by가 NULL입니다.

---

### 문제 23

**고객 불만 상세 조회: 불만 접수 시 고객명, 주문번호, 담당 직원명, 불만 카테고리를 함께 조회하세요. 최근 15건.**

??? tip "힌트"
    `complaints`에서 `customers`, `orders`(NULL 가능), `staff`(NULL 가능)를 LEFT JOIN으로 연결합니다. 주문 없는 일반 문의도 포함해야 합니다.

??? success "정답"
    ```sql
    SELECT
        cpl.id,
        c.name AS customer_name,
        o.order_number,
        s.name AS staff_name,
        cpl.category,
        cpl.priority,
        cpl.status,
        cpl.created_at
    FROM complaints AS cpl
    INNER JOIN customers AS c ON cpl.customer_id = c.id
    LEFT JOIN orders AS o ON cpl.order_id = o.id
    LEFT JOIN staff AS s ON cpl.staff_id = s.id
    ORDER BY cpl.created_at DESC
    LIMIT 15;
    ```

    **결과 (상위 5행):**

    | id | customer_name | order_number | staff_name | category | priority | status | created_at |
    |----|--------------|-------------|-----------|----------|----------|--------|------------|
    | 3477 | 김** | ORD-20251228-... | 이** | delivery_issue | medium | open | 2025-12-... |
    | 3476 | 박** | NULL | 최** | general_inquiry | low | resolved | 2025-12-... |
    | 3475 | 이** | ORD-20251225-... | 정** | product_defect | high | open | 2025-12-... |
    | 3474 | 최** | ORD-20251224-... | 김** | refund_request | medium | closed | 2025-12-... |
    | 3473 | 정** | NULL | 이** | price_inquiry | low | resolved | 2025-12-... |

    > order_number가 NULL이면 일반 문의(주문 무관)입니다.

---

### 문제 24

**상품 후속 모델 체인 (Self-JOIN): 단종된 상품과 그 후속 모델을 함께 조회하세요.**

??? tip "힌트"
    `products.successor_id`가 같은 테이블의 `id`를 참조합니다. `products AS p JOIN products AS succ ON p.successor_id = succ.id`.

??? success "정답"
    ```sql
    SELECT
        p.name        AS discontinued_product,
        p.price       AS old_price,
        p.discontinued_at,
        succ.name     AS successor_product,
        succ.price    AS new_price,
        ROUND(succ.price - p.price, 0) AS price_diff
    FROM products AS p
    INNER JOIN products AS succ ON p.successor_id = succ.id
    WHERE p.discontinued_at IS NOT NULL
    ORDER BY p.discontinued_at DESC
    LIMIT 20;
    ```

    **결과 (상위 5행):**

    | discontinued_product | old_price | discontinued_at | successor_product | new_price | price_diff |
    |---------------------|-----------|----------------|-------------------|-----------|------------|
    | WD Elements 2TB 블랙 | 265600 | 2024-08-25 ... | WD Elements 4TB 블랙 | 345200 | 79600 |
    | 소니 WH-CH720N 실버 | 249800 | 2023-09-21 ... | 소니 WH-1000XM5 블랙 | 489600 | 239800 |
    | JBL Quantum ONE 화이트 | 179400 | 2023-06-01 ... | JBL Quantum 910 블랙 | 325100 | 145700 |
    | 주연 리오나인 i7 실버 | 1102700 | 2023-05-08 ... | 주연 리오나인 i9 실버 | 1523400 | 420700 |
    | ASUS TUF Gaming RTX 5080 화이트 | 3812000 | 2017-05-15 ... | ASUS TUF Gaming RTX 5090 | 4125000 | 313000 |

    > 실제 데이터에 따라 결과가 달라집니다.

---

### 문제 25

**고객 등급별, 결제 수단별 매출 비중을 조회하세요. 취소 제외.**

??? tip "힌트"
    `customers` -> `orders` -> `payments` 3테이블을 JOIN합니다. `GROUP BY c.grade, pay.method`로 교차 집계하고, 각 등급 내 비중을 계산합니다.

??? success "정답"
    ```sql
    SELECT
        c.grade,
        pay.method,
        COUNT(*) AS order_count,
        ROUND(SUM(pay.amount), 0) AS total_amount,
        ROUND(100.0 * SUM(pay.amount) / SUM(SUM(pay.amount)) OVER (PARTITION BY c.grade), 1) AS pct_in_grade
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    INNER JOIN payments AS pay ON o.id = pay.order_id
    WHERE o.status NOT IN ('cancelled')
      AND pay.status = 'completed'
    GROUP BY c.grade, pay.method
    ORDER BY c.grade, total_amount DESC;
    ```

    **결과 (상위 8행):**

    | grade | method | order_count | total_amount | pct_in_grade |
    |-------|--------|------------|-------------|-------------|
    | BRONZE | card | 8234 | 2456780000 | 52.3 |
    | BRONZE | kakao_pay | 4521 | 1234560000 | 26.3 |
    | BRONZE | naver_pay | 2345 | 678900000 | 14.5 |
    | BRONZE | bank_transfer | 1234 | 325600000 | 6.9 |
    | GOLD | card | 3456 | 1876540000 | 48.7 |
    | GOLD | kakao_pay | 2345 | 987650000 | 25.6 |
    | GOLD | naver_pay | 1567 | 654320000 | 17.0 |
    | GOLD | bank_transfer | 876 | 334560000 | 8.7 |

    > 실제 데이터에 따라 수치가 달라집니다. 윈도우 함수 `SUM() OVER()`로 등급 내 비중을 계산합니다.
