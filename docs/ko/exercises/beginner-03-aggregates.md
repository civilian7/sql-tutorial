# 집계 함수

!!! info "사용 테이블"
    `products` — 상품 (이름, 가격, 재고, 브랜드)  
    `customers` — 고객 (등급, 포인트, 가입채널)  
    `orders` — 주문 (상태, 금액, 일시)  
    `reviews` — 리뷰 (평점, 내용)  
    `payments` — 결제 (방법, 금액, 상태)  

!!! abstract "학습 범위"
    `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `ROUND`, `COUNT(DISTINCT)` + 이전 강의 내용

!!! info "시작하기 전에"
    이 연습은 **입문 1~4강**에서 배운 내용만 사용합니다.
    GROUP BY, HAVING, JOIN, 서브쿼리는 사용하지 않습니다.
    집계 함수는 WHERE로 필터링된 **전체 행**에 대해 하나의 결과를 반환합니다.

---

## 기초 (1~10)

한 가지 집계 함수씩 연습합니다.

---

### 문제 1

**상품 테이블에 등록된 전체 상품 수를 조회하세요.**

??? tip "힌트"
    `COUNT(*)`는 테이블의 전체 행 수를 셉니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_products
    FROM products;
    ```

    **결과:**

    | total_products |
    | ----------: |
    | 2800 |

---

### 문제 2

**판매 중인(`is_active = 1`) 상품 수를 조회하세요.**

??? tip "힌트"
    `WHERE`로 조건을 걸고 `COUNT(*)`로 세면 조건에 맞는 행만 집계됩니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS active_count
    FROM products
    WHERE is_active = 1;
    ```

    **결과:**

    | active_count |
    | ----------: |
    | 2175 |

---

### 문제 3

**단종일(`discontinued_at`)이 기록된 상품은 몇 개인지 조회하세요.**

??? tip "힌트"
    `COUNT(칼럼명)`은 해당 칼럼이 NULL이 아닌 행만 셉니다. `COUNT(*)`와의 차이를 기억하세요.

??? success "정답"
    ```sql
    SELECT COUNT(discontinued_at) AS discontinued_count
    FROM products;
    ```

    **결과:**

    | discontinued_count |
    | ----------: |
    | 625 |

    > `COUNT(*)`는 280을 반환하지만, `COUNT(discontinued_at)`는 NULL을 제외한 62를 반환합니다.

---

### 문제 4

**전체 상품의 재고 수량 합계를 구하세요.**

??? tip "힌트"
    `SUM(칼럼명)`은 해당 칼럼의 모든 값을 더합니다.

??? success "정답"
    ```sql
    SELECT SUM(stock_qty) AS total_stock
    FROM products;
    ```

    **결과:**

    | total_stock |
    | ----------: |
    | 701168 |

---

### 문제 5

**전체 상품의 평균 가격을 조회하세요.**

??? tip "힌트"
    `AVG(칼럼명)`은 해당 칼럼의 평균을 계산합니다.

??? success "정답"
    ```sql
    SELECT AVG(price) AS avg_price
    FROM products;
    ```

    **결과:**

    | avg_price |
    | ----------: |
    | 667853.25 |

    > 소수점이 길게 나옵니다. 뒤에서 `ROUND`로 정리하는 방법을 배웁니다.

---

### 문제 6

**가장 비싼 상품의 가격을 조회하세요.**

??? tip "힌트"
    `MAX(칼럼명)`은 해당 칼럼의 최댓값을 반환합니다.

??? success "정답"
    ```sql
    SELECT MAX(price) AS max_price
    FROM products;
    ```

    **결과:**

    | max_price |
    | ----------: |
    | 7495200.0 |

---

### 문제 7

**가장 저렴한 상품의 가격을 조회하세요.**

??? tip "힌트"
    `MIN(칼럼명)`은 해당 칼럼의 최솟값을 반환합니다.

??? success "정답"
    ```sql
    SELECT MIN(price) AS min_price
    FROM products;
    ```

    **결과:**

    | min_price |
    | ----------: |
    | 16500.0 |

---

### 문제 8

**전체 주문의 총 매출(`total_amount` 합계)을 구하세요.**

??? tip "힌트"
    `orders` 테이블의 `total_amount` 칼럼에 `SUM`을 적용합니다.

??? success "정답"
    ```sql
    SELECT SUM(total_amount) AS total_revenue
    FROM orders;
    ```

    **결과:**

    | total_revenue |
    | ----------: |
    | 435005072142.0 |

    > 약 355억 원입니다. 10년간의 누적 매출입니다.

---

### 문제 9

**리뷰의 평균 평점을 조회하세요.**

??? tip "힌트"
    `reviews` 테이블의 `rating` 칼럼에 `AVG`를 적용합니다.

??? success "정답"
    ```sql
    SELECT AVG(rating) AS avg_rating
    FROM reviews;
    ```

    **결과:**

    | avg_rating |
    | ----------: |
    | 3.903090491521336 |

---

### 문제 10

**고객 중 가장 많은 적립금을 보유한 금액을 조회하세요.**

??? tip "힌트"
    `customers` 테이블의 `point_balance`에 `MAX`를 적용합니다.

??? success "정답"
    ```sql
    SELECT MAX(point_balance) AS max_points
    FROM customers;
    ```

    **결과:**

    | max_points |
    | ----------: |
    | 6344986 |

    > 약 334만 포인트를 보유한 고객이 있습니다.

---

## 응용 (11~20)

ROUND, COUNT(DISTINCT), 여러 집계 함수 조합, WHERE 필터와 집계를 함께 사용합니다.

---

### 문제 11

**판매 중인 상품의 평균 가격을 소수점 둘째 자리까지 반올림하여 조회하세요.**

??? tip "힌트"
    `ROUND(값, 자릿수)`로 소수점 자릿수를 지정합니다. `ROUND(AVG(price), 2)`처럼 집계 함수를 감쌀 수 있습니다.

??? success "정답"
    ```sql
    SELECT ROUND(AVG(price), 2) AS avg_price
    FROM products
    WHERE is_active = 1;
    ```

    **결과:**

    | avg_price |
    | ----------: |
    | 678774.85 |

---

### 문제 12

**상품 테이블에 등록된 브랜드가 몇 종류인지 조회하세요.**

??? tip "힌트"
    `COUNT(DISTINCT 칼럼명)`은 중복을 제거한 고유값의 개수를 셉니다.

??? success "정답"
    ```sql
    SELECT COUNT(DISTINCT brand) AS brand_count
    FROM products;
    ```

    **결과:**

    | brand_count |
    | ----------: |
    | 57 |

---

### 문제 13

**주문을 한 적 있는 고객이 몇 명인지 조회하세요.**

??? tip "힌트"
    `orders` 테이블의 `customer_id`에 `COUNT(DISTINCT ...)`를 적용하면 주문한 고유 고객 수를 알 수 있습니다.

??? success "정답"
    ```sql
    SELECT COUNT(DISTINCT customer_id) AS ordering_customers
    FROM orders;
    ```

    **결과:**

    | ordering_customers |
    | ----------: |
    | 29230 |

    > 전체 5,230명 중 약 52%가 주문 경험이 있습니다.

---

### 문제 14

**상품의 최저가, 최고가, 평균가(소수점 없이)를 한 번에 조회하세요.**

??? tip "힌트"
    하나의 `SELECT`에 여러 집계 함수를 쉼표로 구분하여 나열할 수 있습니다.

??? success "정답"
    ```sql
    SELECT MIN(price) AS min_price,
           MAX(price) AS max_price,
           ROUND(AVG(price), 0) AS avg_price
    FROM products;
    ```

    **결과:**

    | min_price | max_price | avg_price |
    | ----------: | ----------: | ----------: |
    | 16500.0 | 7495200.0 | 667853.0 |

---

### 문제 15

**별점 5점 리뷰는 몇 건인지 조회하세요.**

??? tip "힌트"
    `WHERE rating = 5`로 필터링한 후 `COUNT(*)`를 사용합니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS five_star_count
    FROM reviews
    WHERE rating = 5;
    ```

    **결과:**

    | five_star_count |
    | ----------: |
    | 38460 |

    > 전체 7,945건 중 약 41%가 5점 리뷰입니다.

---

### 문제 16

**리뷰의 평균 평점을 소수점 첫째 자리까지, 최저 평점, 최고 평점을 한 번에 조회하세요.**

??? tip "힌트"
    `ROUND(AVG(...), 1)`, `MIN(...)`, `MAX(...)`를 하나의 SELECT에 나열합니다.

??? success "정답"
    ```sql
    SELECT ROUND(AVG(rating), 1) AS avg_rating,
           MIN(rating) AS min_rating,
           MAX(rating) AS max_rating
    FROM reviews;
    ```

    **결과:**

    | avg_rating | min_rating | max_rating |
    | ----------: | ----------: | ----------: |
    | 3.9 | 1 | 5 |

---

### 문제 17

**카드(`card`)로 결제한 건수를 조회하세요.**

??? tip "힌트"
    `payments` 테이블에서 `method = 'card'`로 필터링합니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS card_count
    FROM payments
    WHERE method = 'card';
    ```

    **결과:**

    | card_count |
    | ----------: |
    | 187835 |

---

### 문제 18

**결제 수단이 몇 종류인지 조회하세요.**

??? tip "힌트"
    `payments` 테이블의 `method` 칼럼에 `COUNT(DISTINCT ...)`를 적용합니다.

??? success "정답"
    ```sql
    SELECT COUNT(DISTINCT method) AS method_count
    FROM payments;
    ```

    **결과:**

    | method_count |
    | ----------: |
    | 6 |

---

### 문제 19

**가장 오래된 주문일과 가장 최근 주문일을 조회하세요.**

??? tip "힌트"
    날짜/시간 문자열에도 `MIN`과 `MAX`를 사용할 수 있습니다. 사전순 비교가 날짜순 비교와 동일하기 때문입니다.

??? success "정답"
    ```sql
    SELECT MIN(ordered_at) AS first_order,
           MAX(ordered_at) AS last_order
    FROM orders;
    ```

    **결과:**

    | first_order | last_order |
    | ---------- | ---------- |
    | 2016-01-02 13:54:14 | 2026-01-01 08:40:57 |

    > 약 9년 6개월간의 주문 데이터가 존재합니다.

---

### 문제 20

**전체 주문에서 할인이 적용된 주문(`discount_amount > 0`)은 몇 건인지 조회하세요.**

??? tip "힌트"
    `WHERE discount_amount > 0`으로 필터링한 후 `COUNT(*)`를 사용합니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS discounted_orders
    FROM orders
    WHERE discount_amount > 0;
    ```

    **결과:**

    | discounted_orders |
    | ----------: |
    | 88688 |

    > 전체 34,908건 중 약 21%의 주문에 할인이 적용되었습니다.

---

## 실전 (21~30)

복합 조건 + 집계, 산술 연산 + 집계, 실무에서 자주 쓰는 질문을 다룹니다.

---

### 문제 21

**확정(`confirmed`) 상태 주문의 건수, 총 매출, 평균 주문 금액을 조회하세요. 금액은 소수점 없이 반올림합니다.**

??? tip "힌트"
    `WHERE status = 'confirmed'`로 필터링한 후 `COUNT`, `SUM`, `AVG`를 한 번에 사용합니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS order_count,
           ROUND(SUM(total_amount), 0) AS total_revenue,
           ROUND(AVG(total_amount), 0) AS avg_amount
    FROM orders
    WHERE status = 'confirmed';
    ```

    **결과:**

    | order_count | total_revenue | avg_amount |
    | ----------: | ----------: | ----------: |
    | 382081 | 392629443801.0 | 1027608.0 |

---

### 문제 22

**리뷰를 작성한 고객이 몇 명인지, 리뷰가 달린 상품이 몇 종류인지 한 번에 조회하세요.**

??? tip "힌트"
    하나의 SELECT에서 `COUNT(DISTINCT customer_id)`와 `COUNT(DISTINCT product_id)`를 함께 사용합니다.

??? success "정답"
    ```sql
    SELECT COUNT(DISTINCT customer_id) AS reviewer_count,
           COUNT(DISTINCT product_id) AS reviewed_product_count
    FROM reviews;
    ```

    **결과:**

    | reviewer_count | reviewed_product_count |
    | ----------: | ----------: |
    | 20329 | 2758 |

    > 전체 280개 상품 중 256개(91%)에 리뷰가 달렸습니다.

---

### 문제 23

**고객의 적립금 합계와 평균(소수점 없이)을 조회하세요.**

??? tip "힌트"
    `customers` 테이블의 `point_balance`에 `SUM`과 `ROUND(AVG(...), 0)`를 적용합니다.

??? success "정답"
    ```sql
    SELECT SUM(point_balance) AS total_points,
           ROUND(AVG(point_balance), 0) AS avg_points
    FROM customers;
    ```

    **결과:**

    | total_points | avg_points |
    | ----------: | ----------: |
    | 3840575170 | 73434.0 |

    > 전체 고객의 적립금 합계는 약 3.2억 포인트이며, 1인당 평균 약 6만 포인트입니다.

---

### 문제 24

**2024년에 접수된 주문의 건수와 총 매출(소수점 없이)을 조회하세요.**

??? tip "힌트"
    `ordered_at`이 `'2024-01-01'` 이상이고 `'2025-01-01'` 미만인 조건을 사용합니다. `BETWEEN`을 쓸 수도 있고, `>=`와 `<`를 조합할 수도 있습니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS order_count,
           ROUND(SUM(total_amount), 0) AS revenue
    FROM orders
    WHERE ordered_at >= '2024-01-01'
      AND ordered_at < '2025-01-01';
    ```

    **결과:**

    | order_count | revenue |
    | ----------: | ----------: |
    | 63967 | 65739060082.0 |

    > 2024년 한 해 매출은 약 56억 원입니다.

---

### 문제 25

**환불(`refunded`) 상태 결제의 건수와 총 환불 금액을 조회하세요.**

??? tip "힌트"
    `payments` 테이블에서 `status = 'refunded'`로 필터링합니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS refund_count,
           ROUND(SUM(amount), 0) AS refund_total
    FROM payments
    WHERE status = 'refunded';
    ```

    **결과:**

    | refund_count | refund_total |
    | ----------: | ----------: |
    | 22633 | 28380821307.0 |

    > 약 22.5억 원이 환불되었습니다.

---

### 문제 26

**판매 중인 상품의 총 재고 자산 가치(원가 x 재고수량의 합)를 구하세요.**

??? tip "힌트"
    `SUM` 안에서 산술 연산을 사용할 수 있습니다. `SUM(cost_price * stock_qty)`처럼 칼럼끼리 곱한 값을 합산합니다.

??? success "정답"
    ```sql
    SELECT ROUND(SUM(cost_price * stock_qty), 0) AS inventory_value
    FROM products
    WHERE is_active = 1;
    ```

    **결과:**

    | inventory_value |
    | ----------: |
    | 288433758600.0 |

    > 판매 중인 상품의 재고 원가 합계는 약 300억 원입니다.

---

### 문제 27

**전체 주문의 순매출(주문 금액 - 할인 금액의 합)을 구하세요.**

??? tip "힌트"
    `SUM(total_amount - discount_amount)`처럼 SUM 안에서 칼럼 간 뺄셈을 할 수 있습니다.

??? success "정답"
    ```sql
    SELECT ROUND(SUM(total_amount - discount_amount), 0) AS net_revenue
    FROM orders;
    ```

    **결과:**

    | net_revenue |
    | ----------: |
    | 431099282542.0 |

    > 할인 전 총 매출 355억에서 할인 약 3.1억을 제외한 순매출은 약 352억 원입니다.

---

### 문제 28

**별점 1점 리뷰와 별점 5점 리뷰의 건수를 각각 구하세요.**

??? tip "힌트"
    집계 함수 없이는 한 쿼리로 두 그룹을 나눌 수 없지만, `COUNT`와 `WHERE`를 활용하면 가능합니다. `SUM(CASE ...)`나 `GROUP BY`를 아직 배우지 않았으므로, 두 개의 `COUNT` + 산술식을 사용해봅시다. `COUNT`는 NULL이 아닌 값만 세므로, 조건이 거짓일 때 NULL을 반환하는 트릭을 쓸 수 없을까요? 사실 이 문제에서는 두 개의 쿼리를 나란히 실행해도 됩니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS one_star_count
    FROM reviews
    WHERE rating = 1;
    ```

    **결과:**

    | one_star_count |
    | ----------: |
    | 4762 |

    ```sql
    SELECT COUNT(*) AS five_star_count
    FROM reviews
    WHERE rating = 5;
    ```

    **결과:**

    | five_star_count |
    | ----------: |
    | 38460 |

    > 5점(3,221건)이 1점(395건)보다 약 8배 많습니다. GROUP BY를 배우면 한 쿼리로 모든 평점별 건수를 구할 수 있습니다.

---

### 문제 29

**판매 중인 상품의 평균 마진율(%)을 구하세요. 마진율은 `(price - cost_price) * 100.0 / price`이며, 소수점 첫째 자리까지 반올림합니다.**

??? tip "힌트"
    `AVG` 안에 산술식을 넣을 수 있습니다. `AVG((price - cost_price) * 100.0 / price)`로 각 행의 마진율 평균을 구합니다.

??? success "정답"
    ```sql
    SELECT ROUND(AVG((price - cost_price) * 100.0 / price), 1) AS avg_margin_pct
    FROM products
    WHERE is_active = 1;
    ```

    **결과:**

    | avg_margin_pct |
    | ----------: |
    | 23.3 |

    > 판매 중인 상품의 평균 마진율은 약 23%입니다.

---

### 문제 30

**주문 테이블에서 전체 건수, 총 매출, 평균 주문 금액, 총 할인 금액, 총 배송비, 총 사용 포인트를 한 번에 조회하세요. 금액은 모두 소수점 없이 반올림합니다.**

??? tip "힌트"
    하나의 `SELECT`에 6개의 집계 함수를 나열합니다. 이것이 집계 함수의 진정한 힘입니다 --- 수만 건의 데이터를 한 줄의 요약으로 압축합니다.

??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_orders,
           ROUND(SUM(total_amount), 0) AS total_revenue,
           ROUND(AVG(total_amount), 0) AS avg_amount,
           ROUND(SUM(discount_amount), 0) AS total_discount,
           ROUND(SUM(shipping_fee), 0) AS total_shipping,
           SUM(point_used) AS total_point_used
    FROM orders;
    ```

    **결과:**

    | total_orders | total_revenue | avg_amount | total_discount | total_shipping | total_point_used |
    | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: |
    | 417803 | 435005072142.0 | 1041173.0 | 3905789600.0 | 65301000.0 | 107572558 |

    > 10년간 약 3.5만 건, 355억 매출, 건당 평균 약 102만 원, 총 할인 3.1억, 배송비 수입 887만, 포인트 사용 882만입니다.
