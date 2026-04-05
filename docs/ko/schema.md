# 데이터베이스 스키마

## 개요

이 튜토리얼은 **테크샵(TechShop)** — 10년차 전자상거래 쇼핑몰의 데이터베이스를 사용합니다.
고객 52,300명, 주문 378,000건, 상품 2,800개 등 현실적인 규모의 데이터로 SQL을 학습합니다.

> 시드값 42로 생성된 결정적 데이터이므로, 동일한 쿼리는 항상 동일한 결과를 반환합니다.

## 엔티티 관계도(ERD)

=== "주문 핵심"

    고객 → 주문 → 결제/배송/반품의 핵심 트랜잭션 흐름입니다.

    ```mermaid
    erDiagram
        customers ||--o{ orders : "customer_id"
        customers ||--o{ customer_addresses : "customer_id"
        customer_addresses ||--o{ orders : "address_id"
        staff ||--o{ orders : "staff_id (CS)"

        orders ||--o{ order_items : "order_id"
        orders ||--|| payments : "order_id"
        orders ||--o| shipping : "order_id"
        orders ||--o{ returns : "order_id"
        products ||--o{ order_items : "product_id"
    ```

=== "상품 카탈로그"

    카테고리 계층, 공급업체, 상품 이미지와 가격 이력입니다.

    ```mermaid
    erDiagram
        categories ||--o{ categories : "parent_id (자기참조)"
        categories ||--o{ products : "category_id"
        suppliers ||--o{ products : "supplier_id"
        products ||--o{ product_images : "product_id"
        products ||--o{ product_prices : "product_id"
        products ||--o{ inventory_transactions : "product_id"
    ```

=== "고객 활동"

    리뷰, 위시리스트, 장바구니, 문의 등 고객 참여 데이터입니다.

    ```mermaid
    erDiagram
        customers ||--o{ reviews : "customer_id"
        products ||--o{ reviews : "product_id"
        orders ||--o{ reviews : "order_id"

        customers ||--o{ wishlists : "customer_id"
        products ||--o{ wishlists : "product_id"

        customers ||--o{ carts : "customer_id"
        carts ||--o{ cart_items : "cart_id"
        products ||--o{ cart_items : "product_id"

        customers ||--o{ complaints : "customer_id"
        orders ||--o{ complaints : "order_id"
        staff ||--o{ complaints : "staff_id"
    ```

=== "쿠폰/마케팅"

    쿠폰 발행과 사용 내역입니다.

    ```mermaid
    erDiagram
        coupons ||--o{ coupon_usage : "coupon_id"
        customers ||--o{ coupon_usage : "customer_id"
        orders ||--o{ coupon_usage : "order_id"
    ```

=== "전체"

    21개 테이블의 전체 관계도입니다.

    ```mermaid
    erDiagram
        categories ||--o{ products : "category_id"
        categories ||--o{ categories : "parent_id"
        suppliers ||--o{ products : "supplier_id"
        products ||--o{ product_images : "product_id"
        products ||--o{ product_prices : "product_id"
        products ||--o{ inventory_transactions : "product_id"

        customers ||--o{ customer_addresses : "customer_id"
        customers ||--o{ orders : "customer_id"
        customer_addresses ||--o{ orders : "address_id"
        staff ||--o{ orders : "staff_id"
        staff ||--o{ complaints : "staff_id"

        orders ||--|| payments : "order_id"
        orders ||--o{ order_items : "order_id"
        orders ||--o| shipping : "order_id"
        orders ||--o{ returns : "order_id"
        products ||--o{ order_items : "product_id"

        customers ||--o{ reviews : "customer_id"
        products ||--o{ reviews : "product_id"
        orders ||--o{ reviews : "order_id"

        customers ||--o{ carts : "customer_id"
        carts ||--o{ cart_items : "cart_id"
        products ||--o{ cart_items : "product_id"

        customers ||--o{ wishlists : "customer_id"
        products ||--o{ wishlists : "product_id"

        customers ||--o{ complaints : "customer_id"
        orders ||--o{ complaints : "order_id"

        coupons ||--o{ coupon_usage : "coupon_id"
        customers ||--o{ coupon_usage : "customer_id"
        orders ||--o{ coupon_usage : "order_id"
    ```

## 테이블 목록

| # | 테이블 | 행 수 | 설명 |
|---|--------|------:|------|
| 1 | categories | 53 | 상품 카테고리 (3단계 계층) |
| 2 | suppliers | 50 | 공급업체 |
| 3 | products | 2,800 | 상품 |
| 4 | product_images | 7,284 | 상품 이미지 |
| 5 | product_prices | 8,347 | 가격 변경 이력 |
| 6 | customers | 52,300 | 고객 |
| 7 | customer_addresses | 86,141 | 고객 배송지 |
| 8 | staff | 50 | 직원 |
| 9 | orders | 378,368 | 주문 |
| 10 | order_items | 809,564 | 주문 상세 (상품별) |
| 11 | payments | 378,368 | 결제 |
| 12 | shipping | 359,313 | 배송 |
| 13 | reviews | 86,806 | 상품 리뷰 |
| 14 | inventory_transactions | 130,322 | 재고 입출고 이력 |
| 15 | carts | 30,000 | 장바구니 |
| 16 | cart_items | 90,061 | 장바구니 상품 |
| 17 | coupons | 200 | 쿠폰 |
| 18 | coupon_usage | 1,747 | 쿠폰 사용 내역 |
| 19 | returns | 11,413 | 반품/교환 |
| 20 | wishlists | 19,995 | 위시리스트 |
| 21 | complaints | 37,953 | 고객 문의/불만 |

## 관계 유형

| 유형 | 예시 | 설명 |
|------|---------|-------------|
| **1:1** | orders → payments | 각 주문에는 정확히 하나의 결제가 존재 |
| **1:N** | customers → orders | 한 고객이 여러 주문을 가질 수 있음 |
| **M:N** | customers ↔ products (wishlists) | 여러 고객이 여러 상품을 찜할 수 있음 |
| **자기 참조** | categories.parent_id → categories.id | 부모-자식 계층 구조 |
| **Nullable FK** | orders.staff_id → staff.id | CS 처리가 필요한 주문에만 지정 |

---

## 테이블 상세

### categories — 상품 카테고리

3단계 계층 구조 (대분류 → 중분류 → 소분류). `parent_id`가 NULL이면 최상위.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 parent_id | INTEGER | → categories(id), NULL=최상위 |
| name | TEXT | 카테고리명 |
| slug | TEXT | UNIQUE — URL용 식별자 |
| depth | INTEGER | 0=대분류, 1=중분류, 2=소분류 |
| sort_order | INTEGER | 정렬 순서 |
| is_active | INTEGER | 활성 여부 (0/1) |
| created_at, updated_at | TEXT | 생성/수정 일시 |

```sql
-- 카테고리 트리 조회
SELECT id, name, depth, parent_id
FROM categories
WHERE depth = 0
ORDER BY sort_order;
```

### suppliers — 공급업체

상품을 공급하는 업체 정보. 각 상품은 하나의 공급업체에 속합니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| company_name | TEXT | 회사명 |
| business_number | TEXT | 사업자등록번호 (가상) |
| contact_name | TEXT | 담당자명 |
| phone | TEXT | 020-XXXX-XXXX (가상번호) |
| email | TEXT | contact@xxx.test.kr |
| address | TEXT | 사업장 주소 |
| is_active | INTEGER | 활성 여부 |
| created_at, updated_at | TEXT | 생성/수정 일시 |

### products — 상품

판매 중인 전자제품 2,800개. SKU 코드로 유일 식별. 가격, 원가, 재고, 단종 상태를 포함합니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 category_id | INTEGER | → categories(id) |
| 🔗 supplier_id | INTEGER | → suppliers(id) |
| name | TEXT | 상품명 |
| sku | TEXT | UNIQUE — 재고관리코드 (예: LA-GEN-삼성-00001) |
| brand | TEXT | 브랜드명 |
| model_number | TEXT | 모델번호 |
| description | TEXT | 상품 설명 |
| price | REAL | 현재 판매가 (원), CHECK >= 0 |
| cost_price | REAL | 원가 (원), CHECK >= 0 |
| stock_qty | INTEGER | 현재 재고 수량 |
| weight_grams | INTEGER | 배송 무게 (g) |
| is_active | INTEGER | 판매 중 여부 |
| discontinued_at | TEXT | 단종일 (NULL=판매중) |
| created_at, updated_at | TEXT | 생성/수정 일시 |

```sql
-- 브랜드별 평균 가격과 상품 수
SELECT brand, COUNT(*) AS cnt, CAST(AVG(price) AS INTEGER) AS avg_price
FROM products
WHERE is_active = 1
GROUP BY brand
ORDER BY cnt DESC
LIMIT 10;
```

### product_images — 상품 이미지

상품별 다각도 이미지. `is_primary`로 대표 이미지를 구분합니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 product_id | INTEGER | → products(id) |
| image_url | TEXT | 이미지 경로/URL |
| file_name | TEXT | 파일명 (예: 42_1.jpg) |
| image_type | TEXT | main/angle/side/back/detail/package/lifestyle 등 |
| alt_text | TEXT | 대체 텍스트 |
| width, height | INTEGER | 이미지 크기 (px) |
| file_size | INTEGER | 파일 크기 (bytes) |
| sort_order | INTEGER | 표시 순서 |
| is_primary | INTEGER | 대표 이미지 여부 |
| created_at | TEXT | 생성 일시 |

### product_prices — 가격 변경 이력

상품 가격 변동을 기록합니다. `ended_at`이 NULL이면 현재 적용 중인 가격입니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 product_id | INTEGER | → products(id) |
| price | REAL | 해당 기간 판매가 |
| started_at | TEXT | 적용 시작일 |
| ended_at | TEXT | 적용 종료일 (NULL=현재가) |
| change_reason | TEXT | regular/promotion/price_drop/cost_increase |

### customers — 고객

쇼핑몰 회원 52,300명. 등급제(BRONZE~VIP), 적립금, 활성/탈퇴 상태를 관리합니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| email | TEXT | UNIQUE — `user123@testmail.kr` |
| password_hash | TEXT | SHA-256 (가상) |
| name | TEXT | 고객명 |
| phone | TEXT | `020-XXXX-XXXX` (가상번호) |
| birth_date | TEXT | 생년월일 (~15% NULL) |
| gender | TEXT | M/F (NULL ~10%, M:65%) |
| grade | TEXT | CHECK: BRONZE/SILVER/GOLD/VIP |
| point_balance | INTEGER | 적립금 잔액, CHECK >= 0 |
| is_active | INTEGER | 0=탈퇴, 1=활성 |
| last_login_at | TEXT | NULL = 한 번도 로그인 안 함 |
| created_at, updated_at | TEXT | 가입일/수정일 |

```sql
-- 등급별 고객 수와 평균 적립금
SELECT grade, COUNT(*) AS cnt, CAST(AVG(point_balance) AS INTEGER) AS avg_points
FROM customers
WHERE is_active = 1
GROUP BY grade;
```

### customer_addresses — 고객 배송지

고객별 다수 배송지. `is_default`로 기본 배송지를 구분합니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 customer_id | INTEGER | → customers(id) |
| label | TEXT | 자택/회사/기타 |
| recipient_name | TEXT | 수령인 |
| phone | TEXT | 수령인 연락처 |
| zip_code | TEXT | 우편번호 |
| address1 | TEXT | 기본 주소 |
| address2 | TEXT | 상세 주소 |
| is_default | INTEGER | 기본 배송지 여부 |
| created_at | TEXT | 생성 일시 |

### staff — 직원

쇼핑몰 운영 직원 50명. CS 담당자 배정, 문의 처리에 사용됩니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| email | TEXT | UNIQUE — staffN@techshop-staff.kr |
| name | TEXT | 직원명 |
| phone | TEXT | 연락처 |
| department | TEXT | 영업/물류/CS/마케팅/개발/경영 |
| role | TEXT | admin/manager/staff |
| is_active | INTEGER | 활성 여부 |
| hired_at | TEXT | 입사일 |
| created_at | TEXT | 생성 일시 |

### orders — 주문

핵심 트랜잭션 테이블 (378,368건). 주문번호 `ORD-YYYYMMDD-NNNNN` 기반, 9단계 상태 관리.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| order_number | TEXT | UNIQUE — `ORD-20240315-00001` |
| 🔗 customer_id | INTEGER | → customers(id) |
| 🔗 address_id | INTEGER | → customer_addresses(id) |
| 🔗 staff_id | INTEGER | → staff(id), CS 없으면 NULL |
| status | TEXT | 아래 상태 흐름 참조 |
| total_amount | REAL | 최종 결제 금액 |
| discount_amount | REAL | 총 할인 금액 |
| shipping_fee | REAL | 배송비 (5만원 이상 무료) |
| point_used | INTEGER | 사용 적립금 |
| point_earned | INTEGER | 적립 예정 포인트 |
| notes | TEXT | 배송 요청사항 (~35%) |
| ordered_at | TEXT | 주문 일시 |
| completed_at | TEXT | 구매 확정일 |
| cancelled_at | TEXT | 취소일 |
| created_at, updated_at | TEXT | 생성/수정 일시 |

#### 주문 상태 흐름

```mermaid
stateDiagram-v2
    pending --> paid
    pending --> cancelled
    paid --> preparing
    paid --> cancelled : 환불
    preparing --> shipped
    shipped --> delivered
    delivered --> confirmed
    confirmed --> return_requested
    return_requested --> returned
```

### order_items — 주문 상세

주문별 상품 목록. 주문 시점의 단가와 할인을 기록하여 가격 변동에 독립적입니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 order_id | INTEGER | → orders(id) |
| 🔗 product_id | INTEGER | → products(id) |
| quantity | INTEGER | 수량, CHECK > 0 |
| unit_price | REAL | 주문 시점 단가 |
| discount_amount | REAL | 아이템 할인 |
| subtotal | REAL | (단가 × 수량) − 할인 |

```sql
-- 가장 많이 팔린 상품 Top 10
SELECT p.name, p.brand, SUM(oi.quantity) AS total_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN orders o ON oi.order_id = o.id
WHERE o.status NOT IN ('cancelled')
GROUP BY p.id
ORDER BY total_sold DESC
LIMIT 10;
```

### payments — 결제

주문당 1건의 결제. 카드, 계좌이체, 간편결제 등 다양한 수단을 지원합니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 order_id | INTEGER | → orders(id) |
| method | TEXT | card/bank_transfer/virtual_account/kakao_pay/naver_pay/point |
| amount | REAL | 결제 금액, CHECK >= 0 |
| status | TEXT | CHECK: pending/completed/failed/refunded |
| pg_transaction_id | TEXT | PG사 거래번호 (가상) |
| card_issuer | TEXT | 신한/삼성/KB국민/현대/롯데/하나/우리/NH농협/BC |
| card_approval_no | TEXT | 카드 승인번호 (8자리) |
| installment_months | INTEGER | 할부 개월 (0=일시불) |
| bank_name | TEXT | 은행명 (계좌이체/가상계좌) |
| account_no | TEXT | 가상계좌 번호 |
| depositor_name | TEXT | 입금자명 |
| easy_pay_method | TEXT | 간편결제 내부 수단 |
| receipt_type | TEXT | 소득공제/지출증빙 |
| receipt_no | TEXT | 현금영수증 번호 |
| paid_at | TEXT | 결제 완료 시각 |
| refunded_at | TEXT | 환불 시각 |
| created_at | TEXT | 생성 일시 |

### shipping — 배송

주문별 배송 추적. 택배사별 운송장 번호와 상태를 관리합니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 order_id | INTEGER | → orders(id) |
| carrier | TEXT | CJ대한통운/한진택배/로젠택배/우체국택배 |
| tracking_number | TEXT | 운송장 번호 |
| status | TEXT | preparing/shipped/in_transit/delivered/returned |
| shipped_at | TEXT | 출고일 |
| delivered_at | TEXT | 배송완료일 |
| created_at, updated_at | TEXT | 생성/수정 일시 |

### reviews — 상품 리뷰

구매 인증 리뷰 86,806건. 1~5점 평점 (5점 40%, 4점 30%, 3점 15%, 2점 10%, 1점 5%).

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 product_id | INTEGER | → products(id) |
| 🔗 customer_id | INTEGER | → customers(id) |
| 🔗 order_id | INTEGER | → orders(id) |
| rating | INTEGER | 1~5점, CHECK BETWEEN 1 AND 5 |
| title | TEXT | 리뷰 제목 (~80%) |
| content | TEXT | 리뷰 본문 |
| is_verified | INTEGER | 구매 인증 여부 |
| created_at, updated_at | TEXT | 작성/수정 일시 |

```sql
-- 상품별 평균 평점과 리뷰 수
SELECT p.name, COUNT(r.id) AS review_count, ROUND(AVG(r.rating), 1) AS avg_rating
FROM products p
JOIN reviews r ON p.id = r.product_id
GROUP BY p.id
HAVING review_count >= 10
ORDER BY avg_rating DESC
LIMIT 10;
```

### inventory_transactions — 재고 입출고

상품 재고 변동 이력. 입고(양수), 출고(음수), 반품, 조정을 기록합니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 product_id | INTEGER | → products(id) |
| type | TEXT | inbound/outbound/return/adjustment |
| quantity | INTEGER | 양수=입고, 음수=출고 |
| reference_id | INTEGER | 관련 주문 ID |
| notes | TEXT | 초기입고/정기입고/반품입고 등 |
| created_at | TEXT | 발생 일시 |

### carts — 장바구니

고객별 장바구니. 주문 전환(converted), 포기(abandoned) 상태를 추적합니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 customer_id | INTEGER | → customers(id) |
| status | TEXT | active/converted/abandoned |
| created_at, updated_at | TEXT | 생성/수정 일시 |

### cart_items — 장바구니 상품

장바구니에 담긴 개별 상품과 수량.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 cart_id | INTEGER | → carts(id) |
| 🔗 product_id | INTEGER | → products(id) |
| quantity | INTEGER | 수량 |
| added_at | TEXT | 추가 일시 |

### coupons — 쿠폰

할인 쿠폰 200종. 정율(percent) 또는 정액(fixed) 할인, 사용 한도, 유효기간을 관리합니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| code | TEXT | UNIQUE — 쿠폰 코드 (CP2401001) |
| name | TEXT | 쿠폰명 |
| type | TEXT | percent/fixed |
| discount_value | REAL | 할인율(%) 또는 할인금액(원), CHECK > 0 |
| min_order_amount | REAL | 최소 주문금액 |
| max_discount | REAL | 최대 할인금액 (percent 타입) |
| usage_limit | INTEGER | 전체 사용 한도 |
| per_user_limit | INTEGER | 1인당 사용 한도 |
| is_active | INTEGER | 활성 여부 |
| started_at | TEXT | 유효기간 시작 |
| expired_at | TEXT | 유효기간 종료 |
| created_at | TEXT | 생성 일시 |

### coupon_usage — 쿠폰 사용 내역

쿠폰이 실제로 사용된 기록. 어떤 고객이 어떤 주문에서 얼마 할인받았는지 추적합니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 coupon_id | INTEGER | → coupons(id) |
| 🔗 customer_id | INTEGER | → customers(id) |
| 🔗 order_id | INTEGER | → orders(id) |
| discount_amount | REAL | 실제 할인 금액 |
| used_at | TEXT | 사용 일시 |

### returns — 반품/교환

반품 또는 교환 요청 11,413건. 사유, 수거, 검수, 환불의 전 과정을 추적합니다.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 order_id | INTEGER | → orders(id) |
| 🔗 customer_id | INTEGER | → customers(id) |
| return_type | TEXT | refund/exchange |
| reason | TEXT | defective/wrong_item/change_of_mind/damaged_in_transit/not_as_described/late_delivery |
| reason_detail | TEXT | 상세 사유 설명 |
| status | TEXT | requested/pickup_scheduled/in_transit/completed |
| is_partial | INTEGER | 부분반품 여부 (~17%) |
| refund_amount | REAL | 환불 금액 |
| refund_status | TEXT | pending/refunded/exchanged/partial_refund |
| carrier | TEXT | 수거 택배사 |
| tracking_number | TEXT | 수거 운송장 번호 |
| requested_at | TEXT | 반품 요청일 |
| pickup_at | TEXT | 수거 예정/완료일 |
| received_at | TEXT | 물류센터 입고일 |
| inspected_at | TEXT | 검수 완료일 |
| inspection_result | TEXT | good/opened_good/defective/unsellable |
| completed_at | TEXT | 처리 완료일 |
| created_at | TEXT | 생성 일시 |

### wishlists — 위시리스트

고객이 관심 상품으로 등록. 동일 고객-상품 조합은 UNIQUE.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 customer_id | INTEGER | → customers(id) |
| 🔗 product_id | INTEGER | → products(id) |
| notify_on_sale | INTEGER | 가격 하락 알림 (0/1) |
| created_at | TEXT | 등록 일시 |

### complaints — 고객 문의/불만

CS 문의 접수 및 처리 37,953건. 7개 카테고리, 5개 채널, 4단계 우선순위.

| 컬럼 | 타입 | 비고 |
|------|------|------|
| 🔑 id | INTEGER | 자동 증가 |
| 🔗 order_id | INTEGER | → orders(id), NULL=일반문의 |
| 🔗 customer_id | INTEGER | → customers(id) |
| 🔗 staff_id | INTEGER | → staff(id), 담당 CS 직원 |
| category | TEXT | product_defect/delivery_issue/wrong_item/refund_request/exchange_request/general_inquiry/price_inquiry |
| channel | TEXT | website/phone/email/chat/kakao |
| priority | TEXT | low/medium/high/urgent |
| status | TEXT | open/resolved/closed |
| title | TEXT | 문의 제목 |
| content | TEXT | 문의 내용 |
| resolution | TEXT | 처리 결과 (해결 시) |
| created_at | TEXT | 접수일 |
| resolved_at | TEXT | 해결일 |
| closed_at | TEXT | 종료일 |

---

## 뷰 목록

미리 정의된 뷰로 복잡한 분석 쿼리를 바로 사용할 수 있습니다.

| 뷰 | 설명 |
|----|------|
| v_monthly_sales | 월별 매출 요약 (주문수, 고객수, 매출, 평균주문액, 할인) |
| v_customer_summary | 고객 종합 프로필 (주문수, 총 지출, 리뷰, 위시리스트, 활동상태) |
| v_product_performance | 상품 성과 (판매량, 매출, 마진율, 리뷰, 반품) |
| v_category_tree | CTE 재귀 카테고리 트리 (전체경로, 상품수) |
| v_daily_orders | 일별 주문 현황 (요일, 확인/취소/반품, 매출) |
| v_payment_summary | 결제수단별 요약 (건수, 금액, 비율, 환불) |
| v_order_detail | 주문 상세 (고객/결제/배송 JOIN) |
| v_revenue_growth | 월별 매출 성장률 (LAG 윈도우 함수) |
| v_top_products_by_category | 카테고리별 매출 상위 5 상품 (ROW_NUMBER) |
| v_customer_rfm | RFM 분석 (Recency/Frequency/Monetary, NTILE 세그먼트) |
| v_cart_abandonment | 장바구니 이탈 분석 (미전환 장바구니의 잠재매출) |
| v_supplier_performance | 공급업체 성과 (매출, 판매량, 반품률) |
| v_hourly_pattern | 시간대별 주문 패턴 (새벽/오전/오후/저녁) |
| v_product_abc | ABC 분석 (매출 기여도 누적 → A/B/C 등급) |
| v_staff_workload | CS 직원 업무량 (문의수, 해결수, 평균처리시간) |
| v_coupon_effectiveness | 쿠폰 효과 분석 (사용수, 할인액, ROI) |
| v_return_analysis | 반품 사유별 분석 (환불/교환, 검수결과, 처리일수) |
| v_yearly_kpi | 연도별 핵심 KPI (매출, 주문수, 취소율, 반품률) |

```sql
-- 뷰 사용 예시: 월별 매출 추이
SELECT * FROM v_monthly_sales ORDER BY month DESC LIMIT 12;

-- 뷰 사용 예시: VIP 고객의 RFM 분석
SELECT * FROM v_customer_rfm WHERE segment = 'Champions' LIMIT 10;
```

## 트리거

| 트리거 | 설명 |
|--------|------|
| trg_orders_updated_at | 주문 상태 변경 시 updated_at 자동 갱신 |
| trg_reviews_updated_at | 리뷰 수정 시 updated_at 자동 갱신 |
| trg_product_price_history | 상품 가격 변경 시 product_prices에 이력 자동 기록 |
| trg_products_updated_at | 상품 수정 시 updated_at 자동 갱신 |
| trg_customers_updated_at | 고객 정보 수정 시 updated_at 자동 갱신 |

## 전체 스키마 확인

```sql
-- 전체 테이블 목록과 DDL
SELECT name, sql FROM sqlite_master
WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
ORDER BY name;

-- 전체 뷰 목록
SELECT name FROM sqlite_master WHERE type = 'view' ORDER BY name;

-- 특정 테이블의 컬럼 정보
PRAGMA table_info('orders');

-- 인덱스 목록
SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' ORDER BY tbl_name;
```
