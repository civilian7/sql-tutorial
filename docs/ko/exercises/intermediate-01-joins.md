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
    | ---------- | ----------: | ---------- |
    | Razer Blade 14 블랙 | 7495200.0 | 게이밍 노트북 |
    | Razer Blade 16 블랙 | 5634900.0 | 게이밍 노트북 |
    | Razer Blade 16 | 5518300.0 | 게이밍 노트북 |
    | Razer Blade 16 화이트 | 5503500.0 | 게이밍 노트북 |
    | Razer Blade 18 | 5450500.0 | 게이밍 노트북 |
    | Razer Blade 14 | 5339100.0 | 게이밍 노트북 |
    | Razer Blade 16 실버 | 5127500.0 | 게이밍 노트북 |
    | Razer Blade 16 블랙 | 4938200.0 | 게이밍 노트북 |
    | ... | ... | ... |

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
    | ---------- | ---------- | ---------- |
    | AMD Ryzen 5 9600X | AMD | AMD코리아 |
    | AMD Ryzen 7 7700X | AMD | AMD코리아 |
    | AMD Ryzen 7 7700X 블랙 | AMD | AMD코리아 |
    | AMD Ryzen 7 7700X 블랙 | AMD | AMD코리아 |
    | AMD Ryzen 7 7800X3D | AMD | AMD코리아 |
    | AMD Ryzen 7 7800X3D 실버 | AMD | AMD코리아 |
    | AMD Ryzen 7 9700X 블랙 | AMD | AMD코리아 |
    | AMD Ryzen 7 9800X3D 실버 | AMD | AMD코리아 |
    | ... | ... | ... |

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
    | ---------- | ---------- | ----------: | ---------- |
    | ORD-20251211-413965 | 송광수 | 409600.0 | 2026-01-01 08:40:57 |
    | ORD-20251226-416837 | 송광수 | 1169700.0 | 2026-01-01 06:40:57 |
    | ORD-20251231-417734 | 류미숙 | 2076300.0 | 2025-12-31 23:28:51 |
    | ORD-20251231-417696 | 김영미 | 814400.0 | 2025-12-31 23:26:03 |
    | ORD-20251231-417737 | 이영미 | 550600.0 | 2025-12-31 23:17:28 |
    | ORD-20251231-417735 | 조성수 | 35000.0 | 2025-12-31 23:12:47 |
    | ORD-20251231-417677 | 김지우 | 2002473.0 | 2025-12-31 23:09:05 |
    | ORD-20251231-417764 | 이중수 | 42700.0 | 2025-12-31 23:00:56 |
    | ... | ... | ... | ... |

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
    | ----------: | ---------- | ---------- | ----------: | ----------: |
    | 417803 | 엡손 L6290 블랙 | 엡손 | 1 | 399000.0 |
    | 417803 | Dell UP2720Q 화이트 | Dell | 1 | 1289400.0 |
    | 417802 | 넷기어 Nighthawk RS700S 화이트 | 넷기어 | 1 | 184200.0 |
    | 417801 | be quiet! Straight Power 12 1000W 블랙 | be quiet! | 1 | 295500.0 |
    | 417801 | Seagate IronWolf 8TB 화이트 | Seagate | 1 | 194300.0 |
    | 417800 | Norton 360 Standard 블랙 | Norton | 1 | 81000.0 |
    | 417800 | Fractal Design Pop Air | Fractal Design | 1 | 150300.0 |
    | 417800 | CORSAIR iCUE 4000X 실버 | CORSAIR | 1 | 228900.0 |
    | ... | ... | ... | ... | ... |

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
    | ---------- | ---------- | ---------- |
    | ORD-20251225-416704 | 한진택배 | 2026-01-01 22:43:08 |
    | ORD-20251225-416550 | CJ대한통운 | 2026-01-01 22:14:41 |
    | ORD-20251225-416613 | 한진택배 | 2026-01-01 16:37:19 |
    | ORD-20251225-416538 | CJ대한통운 | 2026-01-01 16:08:52 |
    | ORD-20251225-416700 | 로젠택배 | 2026-01-01 15:48:04 |
    | ORD-20251225-416555 | CJ대한통운 | 2026-01-01 15:04:18 |
    | ORD-20251225-416610 | 우체국택배 | 2026-01-01 14:50:31 |
    | ORD-20251225-416570 | 로젠택배 | 2026-01-01 14:26:55 |
    | ... | ... | ... |

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
    | ---------- | ---------- | ----------: | ---------- |
    | Keychron K6 Pro 실버 | 대만족 | 5 | 2026-01-19 14:32:43 |
    | Windows 11 Pro for Workstations 화이트 | 최고입니다! | 5 | 2026-01-18 22:59:14 |
    | 엡손 L3260 블랙 | (NULL) | 5 | 2026-01-17 12:41:28 |
    | MSI MAG X870E TOMAHAWK WIFI | (NULL) | 5 | 2026-01-16 19:31:49 |
    | 로지텍 M750 화이트 | (NULL) | 5 | 2026-01-16 09:52:54 |
    | Arctic Freezer 36 | 완벽해요 | 5 | 2026-01-15 19:31:49 |
    | Ducky One 3 Mini 화이트 | (NULL) | 5 | 2026-01-14 22:26:41 |
    | 로지텍 K580 화이트 | 최고입니다! | 5 | 2026-01-14 14:19:57 |
    | ... | ... | ... | ... |

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
    | ---------- | ----------: |
    | 에이수스코리아 | 230 |
    | 삼성전자 공식 유통 | 211 |
    | 로지텍코리아 | 153 |
    | MSI코리아 | 137 |
    | 앱솔루트 테크놀로지 | 129 |
    | 레이저코리아 | 124 |
    | 서린시스테크 | 120 |
    | LG전자 공식 유통 | 118 |
    | ... | ... |

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
    | ---------- | ----------: | ----------: |
    | 맥북 | 24 | 3347704.0 |
    | 게이밍 노트북 | 113 | 2930866.0 |
    | NVIDIA | 60 | 2324320.0 |
    | 조립PC | 60 | 2220050.0 |
    | 일반 노트북 | 115 | 1730655.0 |
    | 2in1 | 59 | 1606744.0 |
    | 완제품 | 98 | 1505784.0 |
    | 전문가용 모니터 | 57 | 1361037.0 |
    | ... | ... | ... |

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
    | ---------- | ----------: |
    | Razer Blade 14 블랙 | 7495200.0 |
    | Razer Blade 16 | 5518300.0 |
    | 한성 프리워크 P5700 블랙 | 3917100.0 |
    | Razer Blade 16 실버 | 3899800.0 |
    | 기가바이트 AORUS 16X | 3551600.0 |
    | ASUS ROG Zephyrus G14 실버 | 3362500.0 |
    | ASUS ROG Strix G16CH 화이트 | 3307900.0 |
    | Razer Blade 14 실버 | 2902800.0 |
    | ... | ... |

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
    | ---------- | ---------- | ---------- |
    | 성미숙 | BRONZE | 2016-01-01 00:53:24 |
    | 오진호 | BRONZE | 2016-01-01 03:10:41 |
    | 노지민 | BRONZE | 2016-01-01 10:17:05 |
    | 양영진 | BRONZE | 2016-01-03 19:49:46 |
    | 김지아 | BRONZE | 2016-01-05 08:33:42 |
    | 김민준 | BRONZE | 2016-01-05 21:52:07 |
    | 최유진 | BRONZE | 2016-01-06 00:09:48 |
    | 이미정 | BRONZE | 2016-01-06 05:24:42 |
    | ... | ... | ... |

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
    | ---------- | ----------: | ----------: |
    | 로지텍 MK470 화이트 | 41300.0 | 22 |
    | Razer BlackShark V2 Pro | 172300.0 | 21 |
    | Dell U2724D 실버 | 643000.0 | 19 |
    | HP LaserJet Pro M404dn 블랙 | 608200.0 | 19 |
    | 삼성 990 EVO Plus 1TB 블랙 | 88500.0 | 19 |
    | BenQ SW272U 실버 | 2023100.0 | 18 |
    | WD Black SN8100 2TB 블랙 | 90800.0 | 18 |
    | 레오폴드 FC750R PD | 190400.0 | 18 |
    | ... | ... | ... |

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
    | ---------- | ---------- | ---------- | ----------: | ----------: |
    | ORD-20251211-413965 | 송광수 | Windows 11 Pro | 1 | 409600.0 |
    | ORD-20251226-416837 | 송광수 | MSI Radeon RX 7800 XT GAMING X 실버 | 1 | 994000.0 |
    | ORD-20251226-416837 | 송광수 | Razer Huntsman V3 Pro Mini 화이트 | 1 | 175700.0 |
    | ORD-20251231-417734 | 류미숙 | NZXT Kraken 240 실버 | 1 | 169800.0 |
    | ORD-20251231-417734 | 류미숙 | BenQ PD2725U | 1 | 1596100.0 |
    | ... | ... | ... | ... | ... |

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
    | ---------- | ----------: | ----------: |
    | MSI Radeon RX 7900 XTX GAMING X | 4.83 | 6 |
    | 넷기어 Orbi 970 실버 | 4.83 | 6 |
    | ASUS TUF GAMING B860M-PLUS 화이트 | 4.8 | 5 |
    | 넷기어 RAX70 실버 | 4.8 | 5 |
    | 레노버 ThinkPad X1 2in1 실버 | 4.8 | 5 |
    | 삼성 갤럭시북4 프로 화이트 | 4.8 | 5 |
    | 한성 보스몬스터 DX5800 블랙 | 4.8 | 5 |
    | SteelSeries Arctis Nova 7 Wireless 실버 | 4.78 | 9 |
    | ... | ... | ... |

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
    | ----------: | ---------- | ---------- | ---------- | ---------- | ---------- |
    | 24 | 김옥자 | CS | staff | 박경수 | 경영 |
    | 34 | 이순자 | CS | staff | 장주원 | 경영 |
    | 38 | 이현준 | CS | staff | 한민재 | 경영 |
    | 7 | 김영일 | 개발 | manager | 박경수 | 경영 |
    | 21 | 김현주 | 개발 | staff | 김영일 | 개발 |
    | 48 | 김경희 | 경영 | staff | 김진우 | 경영 |
    | 10 | 김진우 | 경영 | manager | 박경수 | 경영 |
    | 13 | 남정순 | 경영 | staff | 김진우 | 경영 |
    | ... | ... | ... | ... | ... | ... |

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
    | ---------- | ----------: | ----------: |
    | 게이밍 노트북 | 18930 | 53851781900.0 |
    | NVIDIA | 18253 | 40205792400.0 |
    | AMD | 43977 | 35401431700.0 |
    | 일반 노트북 | 19642 | 32862183400.0 |
    | 게이밍 모니터 | 20873 | 24964654700.0 |
    | 스피커/헤드셋 | 67551 | 16433071700.0 |
    | 2in1 | 9744 | 15525975700.0 |
    | Intel 소켓 | 38524 | 15401899600.0 |
    | ... | ... | ... |

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
    | ---------- | ---------- | ----------: | ----------: |
    | 박정수 | VIP | 671 | 683999108.0 |
    | 정유진 | VIP | 551 | 661364522.0 |
    | 이미정 | VIP | 533 | 637982227.0 |
    | 김상철 | VIP | 520 | 570706423.0 |
    | 문영숙 | VIP | 552 | 533764115.0 |
    | 이영자 | VIP | 522 | 531101676.0 |
    | 이미정 | VIP | 443 | 504714776.0 |
    | 장영숙 | VIP | 362 | 492889661.0 |
    | ... | ... | ... | ... |

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
    | ---------- | ----------: | ----------: | ----------: |
    | CJ대한통운 | 158460 | 153326 | 96.8 |
    | 한진택배 | 99055 | 95746 | 96.7 |
    | 로젠택배 | 79147 | 76537 | 96.7 |
    | 우체국택배 | 59417 | 57501 | 96.8 |

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
    | ---------- | ----------: | ----------: | ----------: |
    | 에이수스코리아 | 230 | 1290918.0 | 4621600.0 |
    | 삼성전자 공식 유통 | 211 | 712006.0 | 2743700.0 |
    | 로지텍코리아 | 153 | 122777.0 | 327600.0 |
    | MSI코리아 | 137 | 1201664.0 | 4881500.0 |
    | 앱솔루트 테크놀로지 | 129 | 171332.0 | 820400.0 |
    | 레이저코리아 | 124 | 1105065.0 | 7495200.0 |
    | 서린시스테크 | 120 | 153247.0 | 441700.0 |
    | LG전자 공식 유통 | 118 | 1317411.0 | 3053700.0 |
    | ... | ... | ... | ... |

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
    | ---------- | ----------: | ----------: | ----------: | ----------: |
    | CJ대한통운 | 153326 | 4.5 | 2 | 7 |
    | 로젠택배 | 76537 | 4.5 | 2 | 7 |
    | 우체국택배 | 57501 | 4.5 | 2 | 7 |
    | 한진택배 | 95746 | 4.5 | 2 | 7 |

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
    | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
    | MSI Katana 15 | 후속 모델 출시 예정이 있나요? | 서지연 | 2025-12-30 23:57:48 | (NULL) | (NULL) | (NULL) |
    | Dell UP3218K 실버 | 풀로드 시 팬 소음이 어느 정도인가요? | 박영식 | 2025-12-30 23:52:07 | (NULL) | (NULL) | (NULL) |
    | HP ProDesk 400 G9 블랙 | 실제 소비 전력이 어느 정도인가요? | 이순옥 | 2025-12-30 22:56:41 | (NULL) | (NULL) | (NULL) |
    | Razer Barracuda X 화이트 | 한국어 매뉴얼이 있나요? | 김명자 | 2025-12-30 22:55:40 | (NULL) | (NULL) | (NULL) |
    | 삼성 SPA-KFG0BUB 화이트 | 풀로드 시 팬 소음이 어느 정도인가요? | 박준영 | 2025-12-30 20:00:41 | (NULL) | (NULL) | (NULL) |
    | SK하이닉스 Platinum P41 2TB 블랙 | SSD 추가 장착이 가능한가요? | 양우진 | 2025-12-30 19:12:12 | (NULL) | (NULL) | (NULL) |
    | TP-Link TL-SG108 실버 | 맥에서도 사용할 수 있나요? | 김지민 | 2025-12-30 18:51:07 | (NULL) | (NULL) | (NULL) |
    | SteelSeries Aerox 5 Wireless 블랙 | 풀로드 시 팬 소음이 어느 정도인가요? | 박현지 | 2025-12-30 16:06:22 | (NULL) | (NULL) | (NULL) |
    | ... | ... | ... | ... | ... | ... | ... |

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
    | ----------: | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
    | 33270 | 송광수 | ORD-20251211-413965 | 이현준 | delivery_issue | medium | closed | 2026-01-14 17:40:57 |
    | 33595 | 김은정 | ORD-20251231-417744 | 이순자 | delivery_issue | medium | closed | 2026-01-14 14:14:25 |
    | 33570 | 김예은 | ORD-20251230-417476 | 이현준 | refund_request | urgent | closed | 2026-01-13 14:47:24 |
    | 33597 | 박성호 | ORD-20251231-417761 | 이현준 | exchange_request | medium | closed | 2026-01-13 12:22:20 |
    | 33599 | 김영수 | ORD-20251231-417780 | 이순자 | price_inquiry | high | resolved | 2026-01-13 11:32:17 |
    | 33577 | 홍도현 | ORD-20251230-417527 | 이순자 | refund_request | high | closed | 2026-01-13 10:54:24 |
    | 33590 | 이주원 | ORD-20251231-417649 | 이현준 | refund_request | high | closed | 2026-01-12 22:43:43 |
    | 33543 | 문은영 | ORD-20251228-417236 | 이현준 | refund_request | medium | closed | 2026-01-12 18:56:18 |
    | ... | ... | ... | ... | ... | ... | ... | ... |

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
    | ---------- | ----------: | ---------- | ---------- | ----------: | ----------: |
    | 로지텍 G715 실버 | 100600.0 | 2025-12-27 19:50:12 | 로지텍 G715 화이트 | 196000.0 | 95400.0 |
    | 주연 리오나인 i9 하이엔드 실버 | 1663400.0 | 2025-12-15 15:04:20 | 한성 보스몬스터 DX5800 블랙 | 609200.0 | -1054200.0 |
    | Apple Magic Keyboard 숫자 키패드 포함 블랙 | 140700.0 | 2025-12-14 10:44:03 | 로지텍 ERGO K860 화이트 | 116300.0 | -24400.0 |
    | APC Smart-UPS SMT1500 화이트 | 548700.0 | 2025-11-24 01:47:28 | APC Back-UPS Pro BR1500G 블랙 | 217000.0 | -331700.0 |
    | Intel NUC 13 Pro 블랙 | 512900.0 | 2025-11-20 14:16:24 | ASUS NUC 14 Pro+ 블랙 | 1233300.0 | 720400.0 |
    | Apple Magic Mouse | 98500.0 | 2025-11-14 10:48:19 | Microsoft Arc Mouse 실버 | 66000.0 | -32500.0 |
    | 레노버 ThinkPad T14s | 2576700.0 | 2025-11-12 20:25:30 | 삼성 갤럭시북4 프로 360 실버 | 1858500.0 | -718200.0 |
    | ASUS ROG Strix G16CH 실버 | 3224500.0 | 2025-10-30 23:43:51 | 주연 리오나인 R7 시스템 실버 | 1754300.0 | -1470200.0 |
    | ... | ... | ... | ... | ... | ... |

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
    | ---------- | ---------- | ----------: | ----------: | ----------: |
    | BRONZE | card | 37883 | 34898879078.0 | 45.2 |
    | BRONZE | kakao_pay | 16783 | 15394346630.0 | 20.0 |
    | BRONZE | naver_pay | 12505 | 11438714795.0 | 14.8 |
    | BRONZE | bank_transfer | 8562 | 7798095897.0 | 10.1 |
    | BRONZE | virtual_account | 4255 | 3929589888.0 | 5.1 |
    | BRONZE | point | 4124 | 3671393885.0 | 4.8 |
    | GOLD | card | 37930 | 39631329241.0 | 45.0 |
    | GOLD | kakao_pay | 16585 | 17303693765.0 | 19.7 |
    | ... | ... | ... | ... | ... |

    > 실제 데이터에 따라 수치가 달라집니다. 윈도우 함수 `SUM() OVER()`로 등급 내 비중을 계산합니다.
