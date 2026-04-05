# 데이터베이스 스키마 및 데이터 생성 명세

## 1. 스키마 설계

### 1.1 테이블 목록

| # | 테이블명 | 설명 | 예상 건수(medium) |
|---|---------|------|-------------------|
| 1 | categories | 상품 카테고리 (계층형) | ~50 |
| 2 | suppliers | 공급업체 | ~100 |
| 3 | products | 상품 | ~3,000 |
| 4 | product_prices | 상품 가격 이력 | ~10,000 |
| 5 | customers | 고객 | ~50,000 |
| 6 | customer_addresses | 고객 배송지 | ~70,000 |
| 7 | staff | 직원/관리자 | ~50 |
| 8 | orders | 주문 | ~300,000 |
| 9 | order_items | 주문 상세 | ~700,000 |
| 10 | payments | 결제 | ~300,000 |
| 11 | shipping | 배송 | ~300,000 |
| 12 | reviews | 상품 리뷰 | ~80,000 |
| 13 | inventory_transactions | 입출고 이력 | ~150,000 |
| 14 | carts | 장바구니 | ~30,000 |
| 15 | cart_items | 장바구니 상세 | ~60,000 |
| 16 | coupons | 쿠폰 | ~200 |
| 17 | coupon_usage | 쿠폰 사용 이력 | ~50,000 |

**전체: 약 200만 건**

### 1.2 데이터 규모 프로필

| 프로필 | 배율 | 전체 건수 | 용도 |
|--------|------|----------|------|
| small | 0.1x | ~20만 건 | 빠른 기능 테스트, CI |
| medium | 1.0x | ~200만 건 | 일반 개발/테스트 (기본값) |
| large | 5.0x | ~1,000만 건 | 성능 테스트, DB 엔진 비교 |

---

## 2. 상세 스키마

### 2.1 categories (상품 카테고리)
```
id              INTEGER PRIMARY KEY
parent_id       INTEGER NULL REFERENCES categories(id)  -- 계층 구조
name            VARCHAR(100) NOT NULL
slug            VARCHAR(100) NOT NULL UNIQUE
depth           INTEGER NOT NULL DEFAULT 0  -- 0=대분류, 1=중분류, 2=소분류
sort_order      INTEGER NOT NULL DEFAULT 0
is_active       BOOLEAN NOT NULL DEFAULT TRUE
created_at      TIMESTAMP NOT NULL
updated_at      TIMESTAMP NOT NULL
```

**카테고리 예시 (대분류 > 중분류 > 소분류):**
- 데스크톱 PC > 완제품, 조립PC, 베어본
- 노트북 > 일반 노트북, 게이밍 노트북, 2in1, 맥북
- 모니터 > 일반 모니터, 게이밍 모니터, 전문가용 모니터
- CPU > Intel, AMD
- 메인보드 > Intel 소켓, AMD 소켓
- 메모리(RAM) > DDR4, DDR5
- 저장장치 > SSD, HDD, 외장 스토리지
- 그래픽카드 > NVIDIA, AMD
- 파워서플라이(PSU)
- 케이스
- 쿨링 > 공랭, 수랭
- 키보드 > 기계식, 멤브레인, 무선
- 마우스 > 유선, 무선, 게이밍
- 스피커/헤드셋
- 프린터/스캐너
- 네트워크 장비 > 공유기, 허브/스위치, 랜카드
- UPS/전원
- 소프트웨어 > OS, 오피스, 보안

### 2.2 suppliers (공급업체)
```
id              INTEGER PRIMARY KEY
company_name    VARCHAR(200) NOT NULL
business_number VARCHAR(20) NOT NULL  -- 가상 사업자번호
contact_name    VARCHAR(50) NOT NULL
phone           VARCHAR(20) NOT NULL   -- 020-XXXX-XXXX
email           VARCHAR(100) NOT NULL
address         TEXT
is_active       BOOLEAN NOT NULL DEFAULT TRUE
created_at      TIMESTAMP NOT NULL
updated_at      TIMESTAMP NOT NULL
```

### 2.3 products (상품)
```
id              INTEGER PRIMARY KEY
category_id     INTEGER NOT NULL REFERENCES categories(id)
supplier_id     INTEGER NOT NULL REFERENCES suppliers(id)
name            VARCHAR(300) NOT NULL
sku             VARCHAR(50) NOT NULL UNIQUE  -- 예: NB-SAM-GAL-001
brand           VARCHAR(100) NOT NULL
model_number    VARCHAR(100)
description     TEXT
price           DECIMAL(12,2) NOT NULL       -- 현재 판매가
cost_price      DECIMAL(12,2) NOT NULL       -- 원가
stock_qty  INTEGER NOT NULL DEFAULT 0
weight_grams    INTEGER                       -- 배송 무게
is_active       BOOLEAN NOT NULL DEFAULT TRUE
discontinued_at TIMESTAMP NULL               -- 단종일
created_at      TIMESTAMP NOT NULL
updated_at      TIMESTAMP NOT NULL
```

**상품 예시 (현실적 브랜드/모델):**
- 삼성 갤럭시북4 프로, LG 그램, 레노버 ThinkPad
- 삼성 오디세이 G5, LG 울트라기어, 델 S2722DGM
- Intel Core i7-14700K, AMD Ryzen 7 7800X3D
- 삼성 990 PRO 2TB, WD Black SN850X
- NVIDIA RTX 4070, AMD RX 7800 XT
- 로지텍 G PRO X, 레오폴드 FC660M
- (단종 상품도 20~30% 포함)

### 2.4 product_prices (가격 이력)
```
id              INTEGER PRIMARY KEY
product_id      INTEGER NOT NULL REFERENCES products(id)
price           DECIMAL(12,2) NOT NULL
started_at      TIMESTAMP NOT NULL
ended_at        TIMESTAMP NULL
change_reason   VARCHAR(50)  -- 'regular', 'promotion', 'price_drop', 'cost_increase'
```

### 2.5 customers (고객)
```
id              INTEGER PRIMARY KEY
email           VARCHAR(200) NOT NULL UNIQUE  -- {userid}@testmail.kr
password_hash   VARCHAR(256) NOT NULL         -- 가상 해시값
name            VARCHAR(50) NOT NULL
phone           VARCHAR(20) NOT NULL          -- 020-XXXX-XXXX
birth_date      DATE NULL
gender          CHAR(1) NULL                  -- 'M', 'F', NULL
grade           VARCHAR(20) NOT NULL DEFAULT 'BRONZE'  -- BRONZE/SILVER/GOLD/VIP
point_balance   INTEGER NOT NULL DEFAULT 0
is_active       BOOLEAN NOT NULL DEFAULT TRUE
last_login_at   TIMESTAMP NULL
created_at      TIMESTAMP NOT NULL            -- 가입일
updated_at      TIMESTAMP NOT NULL
```

**고객 등급 기준:**
- BRONZE: 기본
- SILVER: 최근 1년 구매 50만원 이상
- GOLD: 최근 1년 구매 200만원 이상
- VIP: 최근 1년 구매 500만원 이상

### 2.6 customer_addresses (배송지)
```
id              INTEGER PRIMARY KEY
customer_id     INTEGER NOT NULL REFERENCES customers(id)
label           VARCHAR(50) NOT NULL          -- '자택', '회사', '기타'
recipient_name  VARCHAR(50) NOT NULL
phone           VARCHAR(20) NOT NULL          -- 020-XXXX-XXXX
zip_code        VARCHAR(10) NOT NULL
address1        VARCHAR(200) NOT NULL         -- 기본 주소
address2        VARCHAR(200)                  -- 상세 주소
is_default      BOOLEAN NOT NULL DEFAULT FALSE
created_at      TIMESTAMP NOT NULL
```

### 2.7 staff (직원)
```
id              INTEGER PRIMARY KEY
email           VARCHAR(200) NOT NULL UNIQUE
name            VARCHAR(50) NOT NULL
phone           VARCHAR(20) NOT NULL          -- 020-XXXX-XXXX
department      VARCHAR(50) NOT NULL          -- 영업, 물류, CS, 마케팅, 개발, 경영
role            VARCHAR(30) NOT NULL          -- admin, manager, staff
is_active       BOOLEAN NOT NULL DEFAULT TRUE
hired_at        DATE NOT NULL
created_at      TIMESTAMP NOT NULL
```

### 2.8 orders (주문)
```
id              INTEGER PRIMARY KEY
order_number    VARCHAR(20) NOT NULL UNIQUE   -- 예: ORD-20160315-00001
customer_id     INTEGER NOT NULL REFERENCES customers(id)
address_id      INTEGER NOT NULL REFERENCES customer_addresses(id)
staff_id        INTEGER NULL REFERENCES staff(id)  -- 담당자 (CS 처리 시)
status          VARCHAR(20) NOT NULL          -- 아래 참조
total_amount    DECIMAL(12,2) NOT NULL
discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0
shipping_fee    DECIMAL(10,2) NOT NULL DEFAULT 0  -- 5만원 이상 무료배송
point_used      INTEGER NOT NULL DEFAULT 0
point_earned    INTEGER NOT NULL DEFAULT 0
notes           TEXT NULL
ordered_at      TIMESTAMP NOT NULL
completed_at    TIMESTAMP NULL
cancelled_at    TIMESTAMP NULL
created_at      TIMESTAMP NOT NULL
updated_at      TIMESTAMP NOT NULL
```

**주문 상태:**
- `pending` → `paid` → `preparing` → `shipped` → `delivered` → `confirmed`
- `pending` → `cancelled` (결제 전 취소)
- `paid` → `cancelled` (결제 후 취소 → 환불)
- `delivered` → `return_requested` → `returned`

### 2.9 order_items (주문 상세)
```
id              INTEGER PRIMARY KEY
order_id        INTEGER NOT NULL REFERENCES orders(id)
product_id      INTEGER NOT NULL REFERENCES products(id)
quantity        INTEGER NOT NULL
unit_price      DECIMAL(12,2) NOT NULL        -- 주문 시점 가격
discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0
subtotal        DECIMAL(12,2) NOT NULL        -- (unit_price * quantity) - discount
```

### 2.10 payments (결제)
```
id              INTEGER PRIMARY KEY
order_id        INTEGER NOT NULL REFERENCES orders(id)
method          VARCHAR(30) NOT NULL          -- card, bank_transfer, virtual_account, kakao_pay, naver_pay, point
amount          DECIMAL(12,2) NOT NULL
status          VARCHAR(20) NOT NULL          -- pending, completed, failed, refunded, partial_refund
pg_transaction_id VARCHAR(100) NULL           -- PG사 거래번호 (가상)
paid_at         TIMESTAMP NULL
refunded_at     TIMESTAMP NULL
created_at      TIMESTAMP NOT NULL
```

**결제 수단 비율 (현실적):**
- 신용카드: 45%
- 카카오페이: 20%
- 네이버페이: 15%
- 계좌이체: 10%
- 가상계좌: 5%
- 포인트 전액: 5%

### 2.11 shipping (배송)
```
id              INTEGER PRIMARY KEY
order_id        INTEGER NOT NULL REFERENCES orders(id)
carrier         VARCHAR(50) NOT NULL          -- CJ대한통운, 한진택배, 로젠택배, 우체국택배
tracking_number VARCHAR(50) NULL
status          VARCHAR(20) NOT NULL          -- preparing, shipped, in_transit, delivered, returned
shipped_at      TIMESTAMP NULL
delivered_at    TIMESTAMP NULL
created_at      TIMESTAMP NOT NULL
updated_at      TIMESTAMP NOT NULL
```

**택배사 비율:**
- CJ대한통운: 40%
- 한진택배: 25%
- 로젠택배: 20%
- 우체국택배: 15%

### 2.12 reviews (리뷰)
```
id              INTEGER PRIMARY KEY
product_id      INTEGER NOT NULL REFERENCES products(id)
customer_id     INTEGER NOT NULL REFERENCES customers(id)
order_id        INTEGER NOT NULL REFERENCES orders(id)
rating          INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5)
title           VARCHAR(200) NULL
content         TEXT NULL
is_verified     BOOLEAN NOT NULL DEFAULT TRUE   -- 구매 인증 리뷰
created_at      TIMESTAMP NOT NULL
updated_at      TIMESTAMP NOT NULL
```

**평점 분포 (현실적):**
- 5점: 40%, 4점: 30%, 3점: 15%, 2점: 10%, 1점: 5%

### 2.13 inventory_transactions (입출고 이력)
```
id              INTEGER PRIMARY KEY
product_id      INTEGER NOT NULL REFERENCES products(id)
type            VARCHAR(20) NOT NULL          -- inbound, outbound, return, adjustment
quantity         INTEGER NOT NULL              -- 양수=입고, 음수=출고
reference_id    INTEGER NULL                  -- 주문ID 또는 입고ID
notes           TEXT NULL
created_at      TIMESTAMP NOT NULL
```

### 2.14 carts (장바구니)
```
id              INTEGER PRIMARY KEY
customer_id     INTEGER NOT NULL REFERENCES customers(id)
status          VARCHAR(20) NOT NULL DEFAULT 'active'  -- active, converted, abandoned
created_at      TIMESTAMP NOT NULL
updated_at      TIMESTAMP NOT NULL
```

### 2.15 cart_items (장바구니 상세)
```
id              INTEGER PRIMARY KEY
cart_id         INTEGER NOT NULL REFERENCES carts(id)
product_id      INTEGER NOT NULL REFERENCES products(id)
quantity        INTEGER NOT NULL DEFAULT 1
added_at        TIMESTAMP NOT NULL
```

### 2.16 coupons (쿠폰)
```
id              INTEGER PRIMARY KEY
code            VARCHAR(30) NOT NULL UNIQUE
name            VARCHAR(100) NOT NULL
type            VARCHAR(20) NOT NULL          -- percent, fixed
discount_value  DECIMAL(10,2) NOT NULL        -- 퍼센트 or 금액
min_order_amount DECIMAL(12,2) NULL           -- 최소 주문금액
max_discount    DECIMAL(12,2) NULL            -- 최대 할인금액 (percent 타입)
usage_limit     INTEGER NULL                  -- 전체 사용 제한
per_user_limit  INTEGER NOT NULL DEFAULT 1
is_active       BOOLEAN NOT NULL DEFAULT TRUE
started_at      TIMESTAMP NOT NULL
expired_at      TIMESTAMP NOT NULL
created_at      TIMESTAMP NOT NULL
```

### 2.17 coupon_usage (쿠폰 사용 이력)
```
id              INTEGER PRIMARY KEY
coupon_id       INTEGER NOT NULL REFERENCES coupons(id)
customer_id     INTEGER NOT NULL REFERENCES customers(id)
order_id        INTEGER NOT NULL REFERENCES orders(id)
discount_amount DECIMAL(12,2) NOT NULL
used_at         TIMESTAMP NOT NULL
```

---

## 3. 데이터 생성 규칙

### 3.1 성장 곡선 (10년)

| 연차 | 연도 | 신규 고객 | 일 평균 주문 | 활성 상품 | 비고 |
|------|------|----------|-------------|----------|------|
| 1 | 2016 | 1,000 | 15~25 | 300 | 창업기 |
| 2 | 2017 | 1,800 | 25~40 | 500 | 초기 성장 |
| 3 | 2018 | 3,000 | 40~70 | 800 | |
| 4 | 2019 | 4,500 | 70~100 | 1,100 | |
| 5 | 2020 | 7,000 | 100~160 | 1,500 | 코로나 특수 |
| 6 | 2021 | 8,000 | 140~200 | 1,800 | 코로나 특수 |
| 7 | 2022 | 6,500 | 130~180 | 2,000 | 반도체 수급 이슈 |
| 8 | 2023 | 6,000 | 120~170 | 2,200 | |
| 9 | 2024 | 7,000 | 140~190 | 2,500 | AI PC 붐 |
| 10 | 2025 | 7,500 | 150~200 | 2,800 | |

### 3.2 계절성 패턴

- **1월**: 0.85 (비수기)
- **2월**: 0.90 (설 연휴)
- **3월**: 1.15 (신학기)
- **4월**: 1.00
- **5월**: 0.95
- **6월**: 0.90 (비수기)
- **7월**: 0.85 (여름 비수기)
- **8월**: 1.05 (방학, 신학기 준비)
- **9월**: 1.10 (신학기)
- **10월**: 1.05
- **11월**: 1.25 (블랙프라이데이/빼빼로데이)
- **12월**: 1.20 (연말 세일/크리스마스)

### 3.3 가격대 (컴퓨터/주변기기)

| 카테고리 | 최저가 | 최고가 | 평균 |
|---------|--------|--------|------|
| 데스크톱 PC | 500,000 | 5,000,000 | 1,200,000 |
| 노트북 | 600,000 | 4,000,000 | 1,500,000 |
| 모니터 | 150,000 | 2,500,000 | 400,000 |
| CPU | 100,000 | 900,000 | 350,000 |
| GPU | 200,000 | 3,500,000 | 700,000 |
| RAM | 30,000 | 300,000 | 80,000 |
| SSD | 50,000 | 500,000 | 120,000 |
| 키보드 | 15,000 | 300,000 | 80,000 |
| 마우스 | 10,000 | 200,000 | 50,000 |
| 기타 주변기기 | 5,000 | 500,000 | 50,000 |

### 3.4 전화번호 생성 규칙
```
형식: 020-XXXX-XXXX
범위: 020-0000-0000 ~ 020-9999-9999
```
- 020은 한국에서 할당되지 않은 지역번호
- 실제 존재하는 번호와 혼동될 가능성 제로
- 고객, 직원, 공급업체 모두 동일 규칙 적용

### 3.5 이메일 생성 규칙
```
고객: {name_romanized}{random_digits}@testmail.kr
직원: {name_romanized}@techshop-staff.kr
공급업체: contact@{company_slug}.test.kr
```
- testmail.kr, test.kr은 실존하지 않는 도메인

### 3.6 엣지 케이스 (의도적 포함)
- NULL birth_date: 고객의 ~15%
- NULL gender: 고객의 ~10%
- 매우 긴 상품명 (200자+): ~1%
- 주문 후 즉시 취소: 전체 주문의 ~5%
- 환불 처리: 전체 주문의 ~3%
- 0원 결제 (포인트 전액): ~1%
- 동일 고객 대량 주문 (기업 구매): ~0.5%
- 리뷰 없는 상품: ~20%
- 재고 마이너스 (일시적 overselling): 극소수

---

## 4. DB별 DDL 특이사항

### SQLite3
- AUTOINCREMENT 사용
- BOOLEAN은 INTEGER(0/1)로 처리
- DECIMAL은 REAL로 처리

### MySQL/MariaDB
- ENGINE=InnoDB, CHARSET=utf8mb4
- AUTO_INCREMENT
- DECIMAL(12,2) 네이티브
- INDEX 별도 생성

### PostgreSQL
- SERIAL 또는 GENERATED ALWAYS AS IDENTITY
- BOOLEAN 네이티브
- DECIMAL/NUMERIC 네이티브
- 적절한 INDEX + 부분 인덱스

### SQL Server
- IDENTITY(1,1)
- NVARCHAR 사용 (유니코드)
- BIT 타입 (BOOLEAN)
- DATETIME2

### Oracle
- SEQUENCE + TRIGGER 또는 GENERATED AS IDENTITY (12c+)
- NUMBER 타입
- VARCHAR2
- CLOB (TEXT 대체)

---

## 5. 인덱스 전략

공통적으로 생성할 인덱스:
```
-- 자주 조회되는 FK
idx_products_category_id
idx_products_supplier_id
idx_orders_customer_id
idx_orders_ordered_at
idx_order_items_order_id
idx_order_items_product_id
idx_payments_order_id
idx_shipping_order_id
idx_reviews_product_id
idx_reviews_customer_id
idx_inventory_product_id

-- 검색용
idx_products_name          -- 상품명 검색
idx_products_sku           -- SKU 검색
idx_customers_email        -- 이메일 로그인
idx_orders_order_number    -- 주문번호 조회
idx_orders_status          -- 상태별 조회

-- 복합 인덱스
idx_orders_customer_status     -- 고객별 주문 상태 조회
idx_order_items_order_product  -- 주문-상품 조합
idx_reviews_product_rating     -- 상품별 평점 조회
```

---

## 6. 시드(Seed) 및 재현성
- 모든 랜덤 생성은 시드 기반 (기본 시드: 42)
- 동일 시드 → 동일 데이터 보장
- Faker, random 모듈 모두 시드 고정
