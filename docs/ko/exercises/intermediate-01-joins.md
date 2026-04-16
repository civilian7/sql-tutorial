# JOIN 마스터

!!! info "사용 테이블"

    `categories` — 카테고리 (부모-자식 계층)  

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `order_items` — 주문 상세 (수량, 단가)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  

    `reviews` — 리뷰 (평점, 내용)  

    `shipping` — 배송 (택배사, 추적번호, 상태)  

    `staff` — 직원 (부서, 역할, 관리자)  

    `suppliers` — 공급업체 (업체명, 연락처)  

    `tags` — 태그 (이름, 카테고리)  

    `product_tags` — 상품-태그 연결  



!!! abstract "학습 범위"

    `INNER JOIN`, `LEFT JOIN`, `multi-table JOIN`, `GROUP BY`, `aggregate functions`



### 1. 각 상품의 이름, 가격, 카테고리명을 조회하세요. 가격 내림차순으로 10개만.


각 상품의 이름, 가격, 카테고리명을 조회하세요. 가격 내림차순으로 10개만.


**힌트 1:** `products`와 `categories`를 `category_id`로 `INNER JOIN`하고, `ORDER BY ... DESC LIMIT 10`.


??? success "정답"
    ```sql
    SELECT p.name, p.price, cat.name AS category
    FROM products AS p
    INNER JOIN categories AS cat ON p.category_id = cat.id
    ORDER BY p.price DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | price | category |
    |---|---|---|
    | MacBook Air 15 M3 실버 | 5,481,100.00 | 맥북 |
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 | NVIDIA |
    | ASUS Dual RTX 5070 Ti [특별 한정판 에디션] 저소... | 4,496,700.00 | NVIDIA |
    | Razer Blade 18 블랙 | 4,353,100.00 | 게이밍 노트북 |
    | Razer Blade 16 실버 | 3,702,900.00 | 게이밍 노트북 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 | 조립PC |
    | ASUS ROG Zephyrus G16 | 3,429,900.00 | 게이밍 노트북 |


---


### 2. 상품명, 카테고리명, 공급업체명을 함께 조회하세요.


상품명, 카테고리명, 공급업체명을 함께 조회하세요.


**힌트 1:** `products`에서 `categories`와 `suppliers` 두 테이블을 각각 `INNER JOIN`으로 연결.


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


    **실행 결과** (총 20행 중 상위 7행)

    | product | category | supplier |
    |---|---|---|
    | AMD Ryzen 9 9900X | AMD | AMD코리아 |
    | AMD Ryzen 9 9900X | AMD | AMD코리아 |
    | APC Back-UPS Pro Gaming BGM1500B 블랙 | UPS/전원 | APC코리아 |
    | ASRock B850M Pro RS 블랙 | AMD 소켓 | ASRock코리아 |
    | ASRock B850M Pro RS 실버 | AMD 소켓 | ASRock코리아 |
    | ASRock B850M Pro RS 화이트 | AMD 소켓 | ASRock코리아 |
    | ASRock B860M Pro RS 실버 | Intel 소켓 | ASRock코리아 |


---


### 3. 한 번도 리뷰를 받지 않은 상품의 이름과 가격을 조회하세요.


한 번도 리뷰를 받지 않은 상품의 이름과 가격을 조회하세요.


**힌트 1:** `LEFT JOIN reviews` 후 `WHERE r.id IS NULL`로 매칭되지 않는 행을 찾기.


??? success "정답"
    ```sql
    SELECT p.name, p.price
    FROM products AS p
    LEFT JOIN reviews AS r ON p.id = r.product_id
    WHERE r.id IS NULL
    ORDER BY p.price DESC;
    ```


    **실행 결과** (2행)

    | name | price |
    |---|---|
    | MSI Radeon RX 9070 XT GAMING X | 1,896,000.00 |
    | 한성 보스몬스터 DX5800 블랙 | 1,129,400.00 |


---


### 4. 한 번도 주문하지 않은 고객의 이름과 가입일을 조회하세요.


한 번도 주문하지 않은 고객의 이름과 가입일을 조회하세요.


**힌트 1:** `customers LEFT JOIN orders` 후 `WHERE o.id IS NULL`로 주문이 없는 고객만 필터링.


??? success "정답"
    ```sql
    SELECT c.name, c.created_at
    FROM customers AS c
    LEFT JOIN orders AS o ON c.id = o.customer_id
    WHERE o.id IS NULL
    ORDER BY c.created_at;
    ```


    **실행 결과** (총 2,391행 중 상위 7행)

    | name | created_at |
    |---|---|
    | 양영진 | 2016-01-03 19:49:46 |
    | 박준영 | 2016-01-15 19:21:20 |
    | 주경희 | 2016-01-26 09:42:20 |
    | 이경수 | 2016-02-03 03:40:29 |
    | 윤준영 | 2016-02-03 04:18:52 |
    | 박수빈 | 2016-02-09 18:54:54 |
    | 김명자 | 2016-02-17 13:41:08 |


---


### 5. 각 고객의 이름, 등급, 주문 수, 총 구매 금액을 조회하세요. 주문 수 상위 10명.


각 고객의 이름, 등급, 주문 수, 총 구매 금액을 조회하세요. 주문 수 상위 10명.


**힌트 1:** `customers JOIN orders` 후 `GROUP BY`로 집계. `COUNT`와 `SUM`을 함께 사용.


??? success "정답"
    ```sql
    SELECT
        c.name, c.grade,
        COUNT(o.id) AS order_count,
        ROUND(SUM(o.total_amount), 2) AS total_spent
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY c.id, c.name, c.grade
    ORDER BY total_spent DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | grade | order_count | total_spent |
    |---|---|---|---|
    | 박정수 | VIP | 312 | 409,734,279.00 |
    | 김병철 | VIP | 352 | 382,314,874.00 |
    | 이미정 | VIP | 225 | 266,184,349.00 |
    | 강명자 | VIP | 250 | 254,525,838.00 |
    | 정유진 | VIP | 226 | 248,498,783.00 |
    | 이영자 | VIP | 290 | 248,168,491.00 |
    | 김성민 | VIP | 236 | 244,859,844.00 |


---


### 6. 최근 주문 5건의 주문번호, 고객명, 상품명, 수량, 단가를 조회하세요.


최근 주문 5건의 주문번호, 고객명, 상품명, 수량, 단가를 조회하세요.


**힌트 1:** `orders -> customers`, `orders -> order_items -> products` 4개 테이블을 `INNER JOIN`으로 연결.


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


    **실행 결과** (5행)

    | order_number | customer | product | quantity | unit_price |
    |---|---|---|---|---|
    | ORD-20251231-37555 | 송지영 | Norton AntiVirus Plus 실버 | 1 | 74,800.00 |
    | ORD-20251231-37543 | 박민서 | 한컴오피스 2024 기업용 화이트 | 1 | 134,100.00 |
    | ORD-20251231-37552 | 강미경 | 한컴오피스 2024 기업용 화이트 | 1 | 134,100.00 |
    | ORD-20251231-37552 | 강미경 | NZXT Kraken 240 실버 | 1 | 120,200.00 |
    | ORD-20251231-37548 | 윤영희 | 삼성 990 EVO Plus 1TB 화이트 | 1 | 187,700.00 |


---


### 7. 카테고리별 총 매출과 판매 수량을 구하세요. 취소 제외.


카테고리별 총 매출과 판매 수량을 구하세요. 취소 제외.


**힌트 1:** `order_items -> products -> categories`를 JOIN하고, `WHERE o.status NOT IN ('cancelled')`로 취소 제외.


??? success "정답"
    ```sql
    SELECT
        cat.name AS category,
        SUM(oi.quantity) AS units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
    FROM order_items AS oi
    INNER JOIN orders AS o ON oi.order_id = o.id
    INNER JOIN products AS p ON oi.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY cat.name
    ORDER BY revenue DESC;
    ```


    **실행 결과** (총 38행 중 상위 7행)

    | category | units_sold | revenue |
    |---|---|---|
    | 게이밍 노트북 | 1691 | 4,982,099,000.00 |
    | AMD | 4016 | 3,124,984,300.00 |
    | NVIDIA | 1661 | 2,814,694,400.00 |
    | 게이밍 모니터 | 2464 | 2,781,055,700.00 |
    | 일반 노트북 | 1365 | 2,429,349,600.00 |
    | 2in1 | 1301 | 1,944,050,200.00 |
    | Intel 소켓 | 3406 | 1,556,580,900.00 |


---


### 8. 리뷰가 5개 이상인 상품의 이름, 평균 평점, 리뷰 수를 구하세요.


리뷰가 5개 이상인 상품의 이름, 평균 평점, 리뷰 수를 구하세요.


**힌트 1:** `products JOIN reviews`로 연결 후 `GROUP BY`와 `HAVING COUNT(r.id) >= 5`로 필터링.


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


    **실행 결과** (총 15행 중 상위 7행)

    | name | avg_rating | review_count |
    |---|---|---|
    | 삼성 DM500TDA 실버 | 4.80 | 5 |
    | LG 27UQ85R 화이트 | 4.60 | 5 |
    | LG 32UN880 에르고 화이트 | 4.56 | 16 |
    | WD Elements 2TB 블랙 | 4.53 | 19 |
    | Windows 11 Home 블랙 | 4.52 | 21 |
    | Dell XPS Desktop 8960 실버 | 4.50 | 10 |
    | Arctic Liquid Freezer III Pro 420 A-R... | 4.45 | 22 |


---


### 9. 배송 완료된 주문의 평균 배송 소요일(주문일 -> 배송완료일)을 구하세요.


배송 완료된 주문의 평균 배송 소요일(주문일 -> 배송완료일)을 구하세요.


**힌트 1:** `JULIANDAY(delivered_at) - JULIANDAY(ordered_at)`로 날짜 차이를 계산. `shipping JOIN orders`.


??? success "정답"
    ```sql
    SELECT
        ROUND(AVG(JULIANDAY(sh.delivered_at) - JULIANDAY(o.ordered_at)), 1) AS avg_delivery_days
    FROM shipping AS sh
    INNER JOIN orders AS o ON sh.order_id = o.id
    WHERE sh.status = 'delivered'
      AND sh.delivered_at IS NOT NULL;
    ```


    **실행 결과** (1행)

    | avg_delivery_days |
    |---|
    | 4.50 |


---


### 10. 택배사(carrier)별 배송 건수, 완료 건수, 완료율을 구하세요.


택배사(carrier)별 배송 건수, 완료 건수, 완료율을 구하세요.


**힌트 1:** `GROUP BY carrier`와 `CASE WHEN status = 'delivered'`로 조건부 집계. 완료율은 `100.0 * 완료/전체`.


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


    **실행 결과** (4행)

    | carrier | total | delivered | delivery_rate |
    |---|---|---|---|
    | CJ대한통운 | 14,087 | 13,671 | 97.00 |
    | 한진택배 | 8977 | 8701 | 96.90 |
    | 로젠택배 | 7165 | 6939 | 96.80 |
    | 우체국택배 | 5387 | 5207 | 96.70 |


---


### 11. 공급업체별 공급 상품 수, 평균 가격, 최고가를 구하세요.


공급업체별 공급 상품 수, 평균 가격, 최고가를 구하세요.


**힌트 1:** `suppliers JOIN products`로 연결 후 `GROUP BY`로 집계. `COUNT`, `AVG`, `MAX` 함수 사용.


??? success "정답"
    ```sql
    SELECT
        s.company_name,
        COUNT(p.id) AS product_count,
        ROUND(AVG(p.price), 2) AS avg_price,
        ROUND(MAX(p.price), 2) AS max_price
    FROM suppliers AS s
    INNER JOIN products AS p ON s.id = p.supplier_id
    GROUP BY s.id, s.company_name
    ORDER BY product_count DESC;
    ```


    **실행 결과** (총 45행 중 상위 7행)

    | company_name | product_count | avg_price | max_price |
    |---|---|---|---|
    | 에이수스코리아 | 26 | 1,683,630.77 | 4,526,600.00 |
    | 삼성전자 공식 유통 | 25 | 616,008.00 | 1,833,000.00 |
    | 로지텍코리아 | 17 | 111,600.00 | 216,800.00 |
    | MSI코리아 | 13 | 778,430.77 | 1,896,000.00 |
    | 서린시스테크 | 12 | 157,908.33 | 269,200.00 |
    | LG전자 공식 유통 | 11 | 1,346,836.36 | 1,828,800.00 |
    | TP-Link코리아 | 11 | 128,763.64 | 344,000.00 |


---


### 12. 각 고객의 가장 최근 주문일과 주문 금액을 조회하세요. 최근 주문순으로 정렬.


각 고객의 가장 최근 주문일과 주문 금액을 조회하세요. 최근 주문순으로 정렬.


**힌트 1:** `MAX(o.ordered_at)`로 최근 주문일을 구하고, `GROUP BY` 고객별로 집계.


??? success "정답"
    ```sql
    SELECT
        c.name,
        c.grade,
        MAX(o.ordered_at) AS last_order_date,
        o.total_amount AS last_order_amount
    FROM customers AS c
    INNER JOIN orders AS o ON c.id = o.customer_id
    WHERE o.status NOT IN ('cancelled')
    GROUP BY c.id, c.name, c.grade
    ORDER BY last_order_date DESC
    LIMIT 15;
    ```


    **실행 결과** (총 15행 중 상위 7행)

    | name | grade | last_order_date | last_order_amount |
    |---|---|---|---|
    | 송지영 | BRONZE | 2025-12-31 22:25:39 | 74,800.00 |
    | 박민서 | GOLD | 2025-12-31 21:40:27 | 134,100.00 |
    | 강미경 | SILVER | 2025-12-31 20:00:48 | 254,300.00 |
    | 윤영희 | BRONZE | 2025-12-31 18:43:56 | 187,700.00 |
    | 문도현 | BRONZE | 2025-12-31 18:00:24 | 155,700.00 |
    | 박상호 | VIP | 2025-12-31 15:43:23 | 198,300.00 |
    | 강서준 | GOLD | 2025-12-31 15:33:05 | 335,000.00 |


---


### 13. 직원 계층 구조 (Self-JOIN)


모든 직원과 그 상사(매니저)의 이름을 함께 조회하세요.
매니저가 없는 최상위 직원은 상사명을 NULL로 표시합니다.


**힌트 1:** `staff` 테이블을 자기 자신과 LEFT JOIN. `staff AS s LEFT JOIN staff AS m ON s.manager_id = m.id`. 매니저가 없으면 `m.name`이 NULL.


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


    **실행 결과** (5행)

    | id | staff_name | department | role | manager_name | manager_department |
    |---|---|---|---|---|---|
    | 3 | 박경수 | 경영 | admin | 한민재 | 경영 |
    | 2 | 장주원 | 경영 | admin | 한민재 | 경영 |
    | 1 | 한민재 | 경영 | admin | NULL | NULL |
    | 5 | 권영희 | 마케팅 | manager | 박경수 | 경영 |
    | 4 | 이준혁 | 영업 | manager | 한민재 | 경영 |


---


### 14. 상품 후속 모델 체인 (Self-JOIN)


단종된 상품과 그 후속 모델을 함께 조회하세요.
단종 상품명, 단종일, 후속 모델명, 후속 모델 가격을 표시합니다.


**힌트 1:** `products.successor_id`가 같은 테이블의 `id`를 참조. `products AS p JOIN products AS succ ON p.successor_id = succ.id`. `p.discontinued_at IS NOT NULL` 필터.


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


    **실행 결과** (총 18행 중 상위 7행)

    | discontinued_product | old_price | discontinued_at | successor_product | new_price | price_diff |
    |---|---|---|---|---|---|
    | Dell XPS Desktop 8960 실버 | 1,249,400.00 | 2025-11-20 15:30:12 | HP Z2 Mini G1a 블랙 | 895,000.00 | -354,400.00 |
    | 한성 보스몬스터 DX7700 화이트 | 1,579,400.00 | 2025-10-25 03:47:01 | 주연 리오나인 i9 하이엔드 | 1,849,900.00 | 270,500.00 |
    | SAPPHIRE PULSE RX 7800 XT 실버 | 1,146,300.00 | 2025-08-01 06:10:51 | MSI Radeon RX 9070 XT GAMING X | 1,896,000.00 | 749,700.00 |
    | 로지텍 G715 | 187,900.00 | 2025-04-16 06:47:20 | Ducky One 3 Full 블랙 | 153,900.00 | -34,000.00 |
    | Razer Basilisk V3 Pro 35K 화이트 | 102,100.00 | 2025-02-14 06:48:19 | 로지텍 G PRO X SUPERLIGHT 2 화이트 | 120,400.00 | 18,300.00 |
    | 캐논 imageCLASS MF655Cdw 블랙 | 278,900.00 | 2024-09-20 15:47:07 | 엡손 L15160 | 1,019,500.00 | 740,600.00 |
    | be quiet! Straight Power 12 1000W | 131,800.00 | 2024-08-15 23:34:23 | be quiet! Dark Power 13 1000W | 293,000.00 | 161,200.00 |


---


### 15. Q&A 스레드 조회 (Self-JOIN)


상품 Q&A에서 질문과 답변을 한 행에 보여주세요.
질문 내용, 질문 작성자(고객), 답변 내용, 답변 작성자(직원)를 표시합니다.


**힌트 1:** 질문: `parent_id IS NULL`. 답변: `parent_id`가 질문의 `id`를 참조. 질문(`q`) LEFT JOIN 답변(`a`) ON `a.parent_id = q.id`.


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


    **실행 결과** (총 20행 중 상위 7행)

    | product_name | question | asked_by | asked_at | answer | answered_by | answered_at |
    |---|---|---|---|---|---|---|
    | SK하이닉스 Platinum P41 2TB 실버 | 정확한 크기가 어떻게 되나요? | 이은지 | 2025-12-30 23:10:22 | NULL | NULL | NULL |
    | ASRock B850M Pro RS 화이트 | 이 구성에 파워 몇W를 추천하시나요? | 권상훈 | 2025-12-30 23:01:05 | NULL | NULL | NULL |
    | Dell U2724D | 이 구성에 파워 몇W를 추천하시나요? | 김경희 | 2025-12-30 17:53:24 | 네, Windows와 Mac 모두 사용 가능합니다. | 이준혁 | 2025-12-30 20:53:24 |
    | ASRock X870E Taichi 실버 | 새 제품인가요, 리퍼인가요? | 이지연 | 2025-12-30 14:27:52 | NULL | NULL | NULL |
    | Fractal Design North | 정확한 크기가 어떻게 되나요? | 임성훈 | 2025-12-30 13:30:22 | NULL | NULL | NULL |
    | MSI MEG Ai1300P PCIE5 화이트 | 케이블이 포함되어 있나요? | 이성민 | 2025-12-29 19:22:36 | 네, 필요한 케이블이 모두 포함되어 있습니다. | 권영희 | 2025-12-30 21:22:36 |
    | TP-Link TG-3468 블랙 | 맥에서도 사용할 수 있나요? | 신준호 | 2025-12-29 10:01:52 | 2주 내 재입고 예정입니다. 알림 설정이 가능합니다. | 권영희 | 2025-12-29 11:01:52 |


---


### 16. 주문이 없는 날 찾기 (CROSS JOIN)


calendar 테이블을 활용하여 2024년에 주문이 하나도 없는 날짜를 찾으세요.


**힌트 1:** `calendar` LEFT JOIN `orders` (날짜 기준). `orders`의 주문일을 `SUBSTR(ordered_at, 1, 10)`으로 날짜만 추출. `WHERE o.id IS NULL`로 주문 없는 날 필터.


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


---


### 17. 상품 태그 검색 (M:N JOIN)


"Gaming" 태그가 달린 상품 목록을 조회하세요.
상품명, 브랜드, 가격, 카테고리를 표시합니다.


**힌트 1:** `product_tags` -> `tags` JOIN으로 태그 이름 필터. `product_tags` -> `products` JOIN으로 상품 정보. `tags.name = 'Gaming'`.


??? success "정답"
    ```sql
    SELECT
        p.name   AS product_name,
        p.brand,
        p.price,
        cat.name AS category
    FROM product_tags AS pt
    INNER JOIN tags       AS t   ON pt.tag_id     = t.id
    INNER JOIN products   AS p   ON pt.product_id = p.id
    INNER JOIN categories AS cat ON p.category_id = cat.id
    WHERE t.name = 'Gaming'
      AND p.is_active = 1
    ORDER BY p.price DESC;
    ```


---
