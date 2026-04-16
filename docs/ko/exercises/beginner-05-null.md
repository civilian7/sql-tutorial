# NULL 처리

!!! info "사용 테이블"

    `customers` — 고객 (등급, 포인트, 가입채널)  

    `orders` — 주문 (상태, 금액, 일시)  

    `products` — 상품 (이름, 가격, 재고, 브랜드)  



!!! abstract "학습 범위"

    `IS NULL`, `IS NOT NULL`, `COALESCE`, `IFNULL`, `NULL and aggregates`, `NULL sorting`



### 1. 생년월일(`birth_date`)이 없는 고객의 이름과 이메일을 조회하세요.


생년월일(`birth_date`)이 없는 고객의 이름과 이메일을 조회하세요.


**힌트 1:** NULL 값을 찾으려면 `= NULL`이 아니라 `IS NULL`을 사용해야 합니다.


??? success "정답"
    ```sql
    SELECT name, email
    FROM customers
    WHERE birth_date IS NULL;
    ```


    **실행 결과** (총 738행 중 상위 7행)

    | name | email |
    |---|---|
    | 김명자 | user7@testmail.kr |
    | 김정식 | user13@testmail.kr |
    | 윤순옥 | user14@testmail.kr |
    | 이서연 | user21@testmail.kr |
    | 강민석 | user24@testmail.kr |
    | 김서준 | user27@testmail.kr |
    | 윤지훈 | user36@testmail.kr |


---


### 2. 성별(`gender`)이 입력되어 있는 고객의 수를 구하세요.


성별(`gender`)이 입력되어 있는 고객의 수를 구하세요.


**힌트 1:** `IS NOT NULL`로 값이 있는 행만 필터링한 뒤 `COUNT(*)`로 셉니다.


??? success "정답"
    ```sql
    SELECT COUNT(*) AS gender_filled_count
    FROM customers
    WHERE gender IS NOT NULL;
    ```


    **실행 결과** (1행)

    | gender_filled_count |
    |---|
    | 4701 |


---


### 3. 한 번도 로그인하지 않은(`last_login_at`이 NULL인) 고객의 이름, 등급, 가입일을 조회하세요


한 번도 로그인하지 않은(`last_login_at`이 NULL인) 고객의 이름, 등급, 가입일을 조회하세요.


**힌트 1:** `last_login_at IS NULL`로 로그인 기록이 없는 고객을 찾습니다.


??? success "정답"
    ```sql
    SELECT name, grade, created_at
    FROM customers
    WHERE last_login_at IS NULL;
    ```


    **실행 결과** (총 281행 중 상위 7행)

    | name | grade | created_at |
    |---|---|---|
    | 윤준영 | BRONZE | 2016-02-03 04:18:52 |
    | 이영식 | BRONZE | 2016-02-23 17:09:54 |
    | 송서준 | BRONZE | 2016-05-07 02:57:58 |
    | 김지우 | BRONZE | 2016-04-29 00:44:20 |
    | 박아름 | BRONZE | 2016-08-13 13:52:58 |
    | 김정훈 | BRONZE | 2017-04-08 22:00:58 |
    | 이경수 | BRONZE | 2017-12-01 07:23:31 |


---


### 4. 배송 요청사항(`notes`)이 있는 주문의 주문번호와 요청사항을 최근 주문 순으로 10건 조회하세요.


배송 요청사항(`notes`)이 있는 주문의 주문번호와 요청사항을 최근 주문 순으로 10건 조회하세요.


**힌트 1:** `IS NOT NULL`로 notes가 비어있지 않은 주문만 필터링합니다.


??? success "정답"
    ```sql
    SELECT order_number, notes
    FROM orders
    WHERE notes IS NOT NULL
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | notes |
    |---|---|
    | ORD-20251231-37543 | 층간소음 주의, 살짝 노크해주세요 |
    | ORD-20251231-37542 | 회사 정문 경비실로 보내주세요 |
    | ORD-20251231-37546 | 경비실에 맡겨주세요 |
    | ORD-20251231-37547 | 파손 주의 부탁드립니다 |
    | ORD-20251231-37549 | 배송 전 연락 부탁합니다 |
    | ORD-20251231-37550 | 택배함에 넣어주세요 |
    | ORD-20251231-37551 | 택배함에 넣어주세요 |


---


### 5. 취소된 주문(`cancelled_at`이 NULL이 아닌)의 수를 구하세요.


취소된 주문(`cancelled_at`이 NULL이 아닌)의 수를 구하세요.


**힌트 1:** `cancelled_at IS NOT NULL`이면 취소 일시가 기록된, 즉 취소된 주문입니다.


??? success "정답"
    ```sql
    SELECT COUNT(*) AS cancelled_count
    FROM orders
    WHERE cancelled_at IS NOT NULL;
    ```


    **실행 결과** (1행)

    | cancelled_count |
    |---|
    | 1859 |


---


### 6. 상품의 사양 정보(`specs`)가 없는 상품의 이름과 브랜드를 조회하세요.


상품의 사양 정보(`specs`)가 없는 상품의 이름과 브랜드를 조회하세요.


**힌트 1:** `specs IS NULL`로 사양 정보가 누락된 상품을 찾습니다.


??? success "정답"
    ```sql
    SELECT name, brand
    FROM products
    WHERE specs IS NULL;
    ```


    **실행 결과** (총 168행 중 상위 7행)

    | name | brand |
    |---|---|
    | 로지텍 G715 화이트 | 로지텍 |
    | 소니 WH-CH720N 실버 | 소니 |
    | be quiet! Light Base 900 | be quiet! |
    | TP-Link TG-3468 실버 | TP-Link |
    | MSI MAG X870E TOMAHAWK WIFI 화이트 | MSI |
    | WD Elements 2TB 블랙 | WD |
    | 넷기어 Nighthawk RS700S 블랙 | 넷기어 |


---


### 7. 고객의 이름과 성별을 조회하되, 성별이 NULL이면 '미입력'으로 표시하세요.


고객의 이름과 성별을 조회하되, 성별이 NULL이면 '미입력'으로 표시하세요.


**힌트 1:** `COALESCE(칼럼, 대체값)`은 칼럼이 NULL일 때 대체값을 반환합니다.


??? success "정답"
    ```sql
    SELECT name, COALESCE(gender, '미입력') AS gender
    FROM customers;
    ```


    **실행 결과** (총 5,230행 중 상위 7행)

    | name | gender |
    |---|---|
    | 정준호 | M |
    | 김경수 | 미입력 |
    | 김민재 | M |
    | 진정자 | F |
    | 이정수 | M |
    | 김준혁 | M |
    | 김명자 | F |


---


### 8. 주문의 주문번호와 배송 요청사항을 조회하되, 요청사항이 없으면 '없음'으로 표시하세요. 최근 10건만 조회합


주문의 주문번호와 배송 요청사항을 조회하되, 요청사항이 없으면 '없음'으로 표시하세요. 최근 10건만 조회합니다.


**힌트 1:** `IFNULL(notes, '없음')` 또는 `COALESCE(notes, '없음')`을 사용합니다. SQLite에서 둘 다 동작합니다.


??? success "정답"
    ```sql
    SELECT order_number, IFNULL(notes, '없음') AS notes
    FROM orders
    ORDER BY ordered_at DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | order_number | notes |
    |---|---|
    | ORD-20251231-37555 | 없음 |
    | ORD-20251231-37543 | 층간소음 주의, 살짝 노크해주세요 |
    | ORD-20251231-37552 | 없음 |
    | ORD-20251231-37548 | 없음 |
    | ORD-20251231-37542 | 회사 정문 경비실로 보내주세요 |
    | ORD-20251231-37546 | 경비실에 맡겨주세요 |
    | ORD-20251231-37547 | 파손 주의 부탁드립니다 |


---


### 9. 단종일(`discontinued_at`)이 있는 상품의 이름, 가격, 단종일을 조회하세요.


단종일(`discontinued_at`)이 있는 상품의 이름, 가격, 단종일을 조회하세요.


**힌트 1:** `discontinued_at IS NOT NULL`이면 단종된 상품입니다.


??? success "정답"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    WHERE discontinued_at IS NOT NULL;
    ```


    **실행 결과** (총 62행 중 상위 7행)

    | name | price | discontinued_at |
    |---|---|---|
    | 소니 WH-CH720N 실버 | 445,700.00 | 2023-09-21 01:03:38 |
    | WD Elements 2TB 블랙 | 247,100.00 | 2024-08-25 09:29:10 |
    | JBL Quantum ONE 화이트 | 239,900.00 | 2023-06-01 06:11:13 |
    | 주연 리오나인 i7 시스템 실버 | 810,300.00 | 2023-05-08 03:08:52 |
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 | 2017-05-15 20:10:25 |
    | 로지텍 G713 실버 | 151,000.00 | 2021-05-03 13:07:12 |
    | 삼성 DDR4 32GB PC4-25600 | 91,000.00 | 2018-08-03 21:40:45 |


---


### 10. 구매 확정(`completed_at`)이 아직 되지 않은 주문 중 취소도 되지 않은 주문의 수를 구하세요.


구매 확정(`completed_at`)이 아직 되지 않은 주문 중 취소도 되지 않은 주문의 수를 구하세요.


**힌트 1:** `completed_at IS NULL AND cancelled_at IS NULL`로 두 칼럼 모두 NULL인 행을 찾습니다.


??? success "정답"
    ```sql
    SELECT COUNT(*) AS pending_count
    FROM orders
    WHERE completed_at IS NULL
      AND cancelled_at IS NULL;
    ```


    **실행 결과** (1행)

    | pending_count |
    |---|
    | 1305 |


---


### 11. 고객의 이름, 생년월일, 성별을 조회하되 생년월일은 NULL이면 '정보없음', 성별은 NULL이면 '미선택'


고객의 이름, 생년월일, 성별을 조회하되 생년월일은 NULL이면 '정보없음', 성별은 NULL이면 '미선택'으로 표시하세요. 상위 20건만 조회합니다.


**힌트 1:** `COALESCE`를 각 칼럼에 개별 적용합니다.


??? success "정답"
    ```sql
    SELECT name,
           COALESCE(birth_date, '정보없음') AS birth_date,
           COALESCE(gender, '미선택') AS gender
    FROM customers
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | name | birth_date | gender |
    |---|---|---|
    | 정준호 | 1995-02-06 | M |
    | 김경수 | 1995-06-12 | 미선택 |
    | 김민재 | 1998-05-02 | M |
    | 진정자 | 1994-12-02 | F |
    | 이정수 | 1989-12-22 | M |
    | 김준혁 | 1991-05-12 | M |
    | 김명자 | 정보없음 | F |


---


### 12. 상품의 이름, 무게를 조회하되 무게(`weight_grams`)가 NULL이면 0으로 대체하세요. 무게가 무


상품의 이름, 무게를 조회하되 무게(`weight_grams`)가 NULL이면 0으로 대체하세요. 무게가 무거운 순으로 10건만 조회합니다.


**힌트 1:** `COALESCE(weight_grams, 0)`으로 NULL을 0으로 대체한 뒤 정렬합니다.


??? success "정답"
    ```sql
    SELECT name, COALESCE(weight_grams, 0) AS weight_grams
    FROM products
    ORDER BY weight_grams DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | weight_grams |
    |---|---|
    | ASUS ROG Strix GT35 | 19,449 |
    | 한성 보스몬스터 DX7700 화이트 | 19,250 |
    | ASUS ROG Strix G16CH 화이트 | 16,624 |
    | 한성 보스몬스터 DX9900 실버 | 14,892 |
    | ASUS ROG Strix G16CH 실버 | 14,308 |
    | CyberPower OR1500LCDRT2U 블랙 | 14,045 |
    | 주연 리오나인 미니PC | 13,062 |


---


### 13. 전체 고객 수와 생년월일이 입력된 고객 수를 함께 조회하세요.


전체 고객 수와 생년월일이 입력된 고객 수를 함께 조회하세요.


**힌트 1:** `COUNT(*)`는 모든 행을 세고, `COUNT(칼럼)`은 해당 칼럼이 NULL이 아닌 행만 셉니다.


??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_customers,
           COUNT(birth_date) AS has_birth_date
    FROM customers;
    ```


    **실행 결과** (1행)

    | total_customers | has_birth_date |
    |---|---|
    | 5230 | 4492 |


---


### 14. 전체 주문 수, 배송 요청사항이 있는 주문 수, 구매 확정된 주문 수를 한 번에 조회하세요.


전체 주문 수, 배송 요청사항이 있는 주문 수, 구매 확정된 주문 수를 한 번에 조회하세요.


**힌트 1:** `COUNT(notes)`, `COUNT(completed_at)`처럼 각 칼럼에 `COUNT`를 적용하면 NULL이 아닌 행만 셉니다.


??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_orders,
           COUNT(notes) AS has_notes,
           COUNT(completed_at) AS completed
    FROM orders;
    ```


    **실행 결과** (1행)

    | total_orders | has_notes | completed |
    |---|---|---|
    | 37,557 | 13,219 | 34,393 |


---


### 15. 고객을 마지막 로그인일 기준 최근 순으로 정렬하되, 로그인 기록이 없는(NULL) 고객은 맨 뒤에 표시하세요


고객을 마지막 로그인일 기준 최근 순으로 정렬하되, 로그인 기록이 없는(NULL) 고객은 맨 뒤에 표시하세요. 상위 20건만 조회합니다.


**힌트 1:** SQLite에서 `ORDER BY 칼럼 DESC`를 사용하면 NULL이 맨 뒤로 갑니다. 또는 `ORDER BY 칼럼 IS NULL, 칼럼 DESC`로 명시적으로 제어합니다.


??? success "정답"
    ```sql
    SELECT name, last_login_at
    FROM customers
    ORDER BY last_login_at IS NULL, last_login_at DESC
    LIMIT 20;
    ```


    **실행 결과** (총 20행 중 상위 7행)

    | name | last_login_at |
    |---|---|
    | 김서연 | 2025-12-30 23:53:45 |
    | 이은영 | 2025-12-30 23:19:27 |
    | 이은지 | 2025-12-30 23:16:24 |
    | 김경희 | 2025-12-30 22:54:11 |
    | 김영순 | 2025-12-30 22:08:46 |
    | 박성호 | 2025-12-30 21:42:46 |
    | 김성호 | 2025-12-30 21:04:31 |


---


### 16. 상품을 단종일 기준 오래된 순으로 정렬하되, 단종되지 않은 상품(NULL)은 맨 뒤에 표시하세요. 상위 10


상품을 단종일 기준 오래된 순으로 정렬하되, 단종되지 않은 상품(NULL)은 맨 뒤에 표시하세요. 상위 10건만 조회합니다.


**힌트 1:** `ORDER BY discontinued_at IS NULL, discontinued_at ASC`로 NULL을 뒤로 보냅니다.


??? success "정답"
    ```sql
    SELECT name, price, discontinued_at
    FROM products
    ORDER BY discontinued_at IS NULL, discontinued_at ASC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | price | discontinued_at |
    |---|---|---|
    | ASUS TUF Gaming RTX 5080 화이트 | 4,526,600.00 | 2017-05-15 20:10:25 |
    | 삼성 DDR4 32GB PC4-25600 | 91,000.00 | 2018-08-03 21:40:45 |
    | ASUS PRIME Z890-A WIFI 실버 | 727,700.00 | 2019-08-25 16:52:30 |
    | SAPPHIRE NITRO+ RX 7900 XTX 블랙 | 867,300.00 | 2020-02-06 04:58:03 |
    | 레노버 IdeaPad Flex 5 화이트 | 1,657,300.00 | 2020-05-08 01:59:34 |
    | 삼성 갤럭시북5 프로 블랙 | 1,739,900.00 | 2020-06-23 23:10:47 |
    | Microsoft Ergonomic Keyboard 실버 | 45,900.00 | 2020-09-06 05:07:08 |


---


### 17. 등급별 고객 수와 생년월일 입력률(%)을 구하세요. 입력률은 소수점 1자리까지 반올림합니다.


등급별 고객 수와 생년월일 입력률(%)을 구하세요. 입력률은 소수점 1자리까지 반올림합니다.


**힌트 1:** `COUNT(birth_date) * 100.0 / COUNT(*)`로 NULL이 아닌 비율을 계산합니다. `GROUP BY grade`로 등급별 집계합니다.


??? success "정답"
    ```sql
    SELECT grade,
           COUNT(*) AS total,
           COUNT(birth_date) AS has_birth,
           ROUND(COUNT(birth_date) * 100.0 / COUNT(*), 1) AS birth_rate_pct
    FROM customers
    GROUP BY grade
    ORDER BY birth_rate_pct DESC;
    ```


    **실행 결과** (4행)

    | grade | total | has_birth | birth_rate_pct |
    |---|---|---|---|
    | VIP | 368 | 326 | 88.60 |
    | GOLD | 524 | 460 | 87.80 |
    | SILVER | 479 | 416 | 86.80 |
    | BRONZE | 3859 | 3290 | 85.30 |


---


### 18. 가입 경로(`acquisition_channel`)별 고객 수를 구하되, NULL인 경우 '미분류'로 표시하


가입 경로(`acquisition_channel`)별 고객 수를 구하되, NULL인 경우 '미분류'로 표시하세요.


**힌트 1:** `COALESCE(acquisition_channel, '미분류')`를 SELECT와 GROUP BY 모두에 사용합니다.


??? success "정답"
    ```sql
    SELECT COALESCE(acquisition_channel, '미분류') AS channel,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY COALESCE(acquisition_channel, '미분류')
    ORDER BY customer_count DESC;
    ```


    **실행 결과** (5행)

    | channel | customer_count |
    |---|---|
    | search_ad | 1543 |
    | social | 1425 |
    | organic | 1146 |
    | referral | 708 |
    | direct | 408 |


---


### 19. 주문 상태별로 주문 수와 배송 요청사항 입력 비율(%)을 구하세요.


주문 상태별로 주문 수와 배송 요청사항 입력 비율(%)을 구하세요.


**힌트 1:** `COUNT(notes) * 100.0 / COUNT(*)`로 notes가 NULL이 아닌 비율을 계산합니다.


??? success "정답"
    ```sql
    SELECT status,
           COUNT(*) AS order_count,
           ROUND(COUNT(notes) * 100.0 / COUNT(*), 1) AS notes_rate_pct
    FROM orders
    GROUP BY status
    ORDER BY order_count DESC;
    ```


    **실행 결과** (총 9행 중 상위 7행)

    | status | order_count | notes_rate_pct |
    |---|---|---|
    | confirmed | 34,393 | 35.30 |
    | cancelled | 1859 | 34.30 |
    | return_requested | 507 | 33.10 |
    | returned | 493 | 34.90 |
    | delivered | 125 | 28.80 |
    | pending | 82 | 37.80 |
    | shipped | 51 | 31.40 |


---


### 20. 상품의 이름, 가격, 무게를 조회하되, 무게가 NULL이면 가격 기준 100g당 1,000원으로 추정한 무게


상품의 이름, 가격, 무게를 조회하되, 무게가 NULL이면 가격 기준 100g당 1,000원으로 추정한 무게(`price / 10`)를 표시하세요. 칼럼명은 `estimated_weight`로 지정합니다.


**힌트 1:** `COALESCE(weight_grams, 다른_계산식)`으로 NULL일 때만 대체 계산을 적용합니다.


??? success "정답"
    ```sql
    SELECT name,
           price,
           COALESCE(weight_grams, CAST(price / 10 AS INTEGER)) AS estimated_weight
    FROM products
    ORDER BY estimated_weight DESC
    LIMIT 10;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | name | price | estimated_weight |
    |---|---|---|
    | Windows 11 Pro 실버 | 423,000.00 | 42,300 |
    | Adobe Creative Cloud 1년 실버 | 327,300.00 | 32,730 |
    | 한컴오피스 2024 기업용 실버 | 241,400.00 | 24,140 |
    | Windows 11 Home 블랙 | 208,600.00 | 20,860 |
    | ASUS ROG Strix GT35 | 3,296,800.00 | 19,449 |
    | 한성 보스몬스터 DX7700 화이트 | 1,579,400.00 | 19,250 |
    | ASUS ROG Strix G16CH 화이트 | 3,671,500.00 | 16,624 |


---


### 21. 고객 테이블에서 각 칼럼의 NULL 수를 한 번에 조회하세요. birth_date, gender, last_


고객 테이블에서 각 칼럼의 NULL 수를 한 번에 조회하세요. birth_date, gender, last_login_at, acquisition_channel의 NULL 수를 구합니다.


**힌트 1:** `COUNT(*) - COUNT(칼럼)`으로 해당 칼럼의 NULL 수를 계산합니다.


??? success "정답"
    ```sql
    SELECT COUNT(*) - COUNT(birth_date) AS birth_null,
           COUNT(*) - COUNT(gender) AS gender_null,
           COUNT(*) - COUNT(last_login_at) AS login_null,
           COUNT(*) - COUNT(acquisition_channel) AS channel_null
    FROM customers;
    ```


    **실행 결과** (1행)

    | birth_null | gender_null | login_null | channel_null |
    |---|---|---|---|
    | 738 | 529 | 281 | 0 |


---


### 22. 고객 테이블에서 각 NULL 허용 칼럼의 결측률(%)을 구하세요. 소수점 1자리까지 표시합니다.


고객 테이블에서 각 NULL 허용 칼럼의 결측률(%)을 구하세요. 소수점 1자리까지 표시합니다.


**힌트 1:** `(COUNT(*) - COUNT(칼럼)) * 100.0 / COUNT(*)`로 결측률을 계산합니다.


??? success "정답"
    ```sql
    SELECT ROUND((COUNT(*) - COUNT(birth_date)) * 100.0 / COUNT(*), 1) AS birth_missing_pct,
           ROUND((COUNT(*) - COUNT(gender)) * 100.0 / COUNT(*), 1) AS gender_missing_pct,
           ROUND((COUNT(*) - COUNT(last_login_at)) * 100.0 / COUNT(*), 1) AS login_missing_pct,
           ROUND((COUNT(*) - COUNT(acquisition_channel)) * 100.0 / COUNT(*), 1) AS channel_missing_pct
    FROM customers;
    ```


    **실행 결과** (1행)

    | birth_missing_pct | gender_missing_pct | login_missing_pct | channel_missing_pct |
    |---|---|---|---|
    | 14.10 | 10.10 | 5.40 | 0.0 |


---


### 23. 주문 테이블에서 notes, completed_at, cancelled_at 각각의 NULL 비율(%)을 구


주문 테이블에서 notes, completed_at, cancelled_at 각각의 NULL 비율(%)을 구하세요.


**힌트 1:** 문제 22와 동일한 패턴을 orders 테이블에 적용합니다.


??? success "정답"
    ```sql
    SELECT ROUND((COUNT(*) - COUNT(notes)) * 100.0 / COUNT(*), 1) AS notes_missing_pct,
           ROUND((COUNT(*) - COUNT(completed_at)) * 100.0 / COUNT(*), 1) AS completed_missing_pct,
           ROUND((COUNT(*) - COUNT(cancelled_at)) * 100.0 / COUNT(*), 1) AS cancelled_missing_pct
    FROM orders;
    ```


    **실행 결과** (1행)

    | notes_missing_pct | completed_missing_pct | cancelled_missing_pct |
    |---|---|---|
    | 64.80 | 8.40 | 95.10 |


---


### 24. 성별이 NULL인 고객의 등급별 분포를 구하세요. 등급별 수와 비율(%)을 표시합니다.


성별이 NULL인 고객의 등급별 분포를 구하세요. 등급별 수와 비율(%)을 표시합니다.


**힌트 1:** `WHERE gender IS NULL`로 필터링 후 `GROUP BY grade`로 집계합니다. 비율은 전체 NULL 고객 대비입니다.


??? success "정답"
    ```sql
    SELECT grade,
           COUNT(*) AS cnt,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM customers
    WHERE gender IS NULL
    GROUP BY grade
    ORDER BY cnt DESC;
    ```


    **실행 결과** (4행)

    | grade | cnt | pct |
    |---|---|---|
    | BRONZE | 429 | 81.10 |
    | SILVER | 45 | 8.50 |
    | GOLD | 41 | 7.80 |
    | VIP | 14 | 2.60 |


---


### 25. 생년월일과 성별이 모두 NULL인 고객의 수를 구하세요. 그리고 생년월일 또는 성별 중 하나라도 NULL인 


생년월일과 성별이 모두 NULL인 고객의 수를 구하세요. 그리고 생년월일 또는 성별 중 하나라도 NULL인 고객의 수도 함께 구하세요.


**힌트 1:** `AND`로 모두 NULL인 조건, `OR`로 하나라도 NULL인 조건을 만듭니다.


??? success "정답"
    ```sql
    SELECT COUNT(*) AS total,
           SUM(CASE WHEN birth_date IS NULL AND gender IS NULL THEN 1 ELSE 0 END) AS both_null,
           SUM(CASE WHEN birth_date IS NULL OR gender IS NULL THEN 1 ELSE 0 END) AS any_null
    FROM customers;
    ```


    **실행 결과** (1행)

    | total | both_null | any_null |
    |---|---|---|
    | 5230 | 87 | 1180 |


---


### 26. 가입 경로가 NULL인 고객 중 VIP 등급의 수와, 가입 경로가 있는 고객 중 VIP 등급의 수를 비교하세


가입 경로가 NULL인 고객 중 VIP 등급의 수와, 가입 경로가 있는 고객 중 VIP 등급의 수를 비교하세요.


**힌트 1:** 두 개의 `COUNT`에 각각 다른 `WHERE` 조건을 적용하거나, 하나의 쿼리에서 필터링된 COUNT를 사용합니다.


??? success "정답"
    ```sql
    SELECT '경로없음' AS channel_status,
           COUNT(*) AS vip_count
    FROM customers
    WHERE acquisition_channel IS NULL AND grade = 'VIP'
    UNION ALL
    SELECT '경로있음',
           COUNT(*)
    FROM customers
    WHERE acquisition_channel IS NOT NULL AND grade = 'VIP';
    ```


    **실행 결과** (2행)

    | channel_status | vip_count |
    |---|---|
    | 경로없음 | 0 |
    | 경로있음 | 368 |


---


### 27. 상품의 설명(`description`)과 사양(`specs`) 중 하나라도 NULL인 상품의 수를 구하고, 


상품의 설명(`description`)과 사양(`specs`) 중 하나라도 NULL인 상품의 수를 구하고, 둘 다 NULL인 상품의 수도 함께 조회하세요.


**힌트 1:** `OR`와 `AND`를 조합하여 두 가지 조건을 만듭니다.


??? success "정답"
    ```sql
    SELECT COUNT(*) AS total_products,
           SUM(CASE WHEN description IS NULL OR specs IS NULL THEN 1 ELSE 0 END) AS any_null,
           SUM(CASE WHEN description IS NULL AND specs IS NULL THEN 1 ELSE 0 END) AS both_null
    FROM products;
    ```


    **실행 결과** (1행)

    | total_products | any_null | both_null |
    |---|---|---|
    | 280 | 168 | 0 |


---


### 28. 연도별 주문 수와 배송 요청사항 작성률(%)을 구하세요. `SUBSTR(ordered_at, 1, 4)`로 


연도별 주문 수와 배송 요청사항 작성률(%)을 구하세요. `SUBSTR(ordered_at, 1, 4)`로 연도를 추출합니다.


**힌트 1:** `GROUP BY SUBSTR(ordered_at, 1, 4)`로 연도별 그룹화 후 `COUNT(notes) * 100.0 / COUNT(*)`로 작성률을 계산합니다.


??? success "정답"
    ```sql
    SELECT SUBSTR(ordered_at, 1, 4) AS year,
           COUNT(*) AS order_count,
           ROUND(COUNT(notes) * 100.0 / COUNT(*), 1) AS notes_rate_pct
    FROM orders
    GROUP BY SUBSTR(ordered_at, 1, 4)
    ORDER BY year;
    ```


    **실행 결과** (총 10행 중 상위 7행)

    | year | order_count | notes_rate_pct |
    |---|---|---|
    | 2016 | 416 | 37.00 |
    | 2017 | 709 | 33.90 |
    | 2018 | 1319 | 34.60 |
    | 2019 | 2589 | 34.50 |
    | 2020 | 4319 | 34.60 |
    | 2021 | 5841 | 34.70 |
    | 2022 | 5203 | 36.30 |


---


### 29. 상품 무게(`weight_grams`)가 NULL인 상품의 브랜드별 수를 구하고, 5개 이상인 브랜드만 조회


상품 무게(`weight_grams`)가 NULL인 상품의 브랜드별 수를 구하고, 5개 이상인 브랜드만 조회하세요.


**힌트 1:** `WHERE weight_grams IS NULL`로 필터링 후 `GROUP BY brand`, `HAVING COUNT(*) >= 5`로 조건을 겁니다.


??? success "정답"
    ```sql
    SELECT brand, COUNT(*) AS null_weight_count
    FROM products
    WHERE weight_grams IS NULL
    GROUP BY brand
    HAVING COUNT(*) >= 5
    ORDER BY null_weight_count DESC;
    ```


---


### 30. 고객의 데이터 완성도를 점수로 계산하세요. birth_date, gender, last_login_at, a


고객의 데이터 완성도를 점수로 계산하세요. birth_date, gender, last_login_at, acquisition_channel 4개 칼럼 중 NULL이 아닌 칼럼 수를 세어 0~4점으로 표시합니다. 점수별 고객 수를 구하세요.


**힌트 1:** `(칼럼 IS NOT NULL)`은 SQLite에서 TRUE=1, FALSE=0을 반환합니다. 4개를 더하면 완성도 점수가 됩니다.


??? success "정답"
    ```sql
    SELECT (birth_date IS NOT NULL)
         + (gender IS NOT NULL)
         + (last_login_at IS NOT NULL)
         + (acquisition_channel IS NOT NULL) AS completeness_score,
           COUNT(*) AS customer_count
    FROM customers
    GROUP BY completeness_score
    ORDER BY completeness_score;
    ```


    **실행 결과** (4행)

    | completeness_score | customer_count |
    |---|---|
    | 1 | 5 |
    | 2 | 143 |
    | 3 | 1247 |
    | 4 | 3835 |


---
