# 전자상거래 테스트 데이터베이스 생성기

컴퓨터 및 주변기기를 판매하는 쇼핑몰의 **현실적인 테스트 데이터베이스**를 생성하는 Python 도구입니다. 잘 설계된, 실무에 가까운 데이터로 SQL을 연습하고 싶은 학습자를 위해 만들어졌습니다.

> **왜 이 프로젝트를?** 데이터베이스를 배우는 초급/중급 개발자에게 가장 큰 걸림돌은 잘 설계된 현실적 데이터베이스에 접근하기 어렵다는 점입니다. 이 생성기는 10년간의 비즈니스 데이터, 현실적 패턴, 올바른 스키마 설계를 갖춘 완전한 전자상거래 데이터베이스를 만들어줍니다.

## 빠른 시작

```bash
# 의존성 설치
pip install -r requirements.txt
```

### 한국어 데이터 생성

```bash
# Small (23만 행, ~29MB, ~9초)
python generate.py --size small

# Medium (200만 행, ~250MB, ~2분) — 기본값
python generate.py --size medium

# Large (1000만 행, ~1.2GB, ~10분)
python generate.py --size large
```

### 영문 데이터 생성

```bash
# Small
python generate.py --size small --locale en

# Medium
python generate.py --size medium --locale en

# Large
python generate.py --size large --locale en
```

생성된 파일: `output/tutorial.db` (SQLite)

### 튜토리얼 문서 보기

MkDocs Material 기반의 튜토리얼 문서를 로컬에서 미리볼 수 있습니다.

```bash
# 한국어 튜토리얼 (http://localhost:8001)
serve.bat

# 영문 튜토리얼
serve.bat en
```

또는 직접 실행:

```bash
cd docs
mkdocs serve -f mkdocs-ko.yml -a localhost:8001
```

파일 수정 시 브라우저에 자동 반영됩니다.

### 튜토리얼 목차

**레슨 (21개)**

| 레벨 | # | 주제 |
|------|---|------|
| 초급 | 01 | SELECT 기초 |
| | 02 | WHERE로 필터링 |
| | 03 | 정렬과 페이징 |
| | 04 | 집계 함수 |
| | 05 | GROUP BY와 HAVING |
| | 06 | NULL 처리 |
| 중급 | 07 | INNER JOIN |
| | 08 | LEFT JOIN |
| | 09 | 서브쿼리 |
| | 10 | CASE 표현식 |
| | 11 | 날짜/시간 함수 |
| | 12 | 문자열 함수 |
| | 13 | UNION |
| | 14 | INSERT, UPDATE, DELETE |
| | 21 | SELF JOIN과 CROSS JOIN |
| 고급 | 15 | 윈도우 함수 |
| | 16 | CTE와 재귀 CTE |
| | 17 | EXISTS와 상관 서브쿼리 |
| | 18 | 뷰(Views) |
| | 19 | 인덱스와 성능 |
| | 20 | 트리거 |

**연습 문제 (111문제)**

| 레벨 | 실습 | 문제 수 |
|------|------|---------|
| 초급 | 상품 탐색 | 15 |
| | 고객 분석 | 15 |
| | 주문 기초 | 15 |
| 중급 | JOIN 마스터 | 12 |
| | 날짜/시간 분석 | 12 |
| | 서브쿼리와 변환 | 12 |
| 고급 | 매출 분석 | 6 |
| | 고객 세분화 | 6 |
| | 재고 관리 | 6 |
| | CS 성과 분석 | 6 |
| | 실무 SQL 패턴 | 6 |

**참고**

- DB 방언 비교 (SQLite / MySQL / PostgreSQL / SQL Server / Oracle)

## 특징

- **21개 테이블** — 외래 키, CHECK 제약조건, 인덱스 완비
- **18개 뷰** — 실무 SQL 패턴 시연 (윈도우 함수, CTE, RFM 분석 등)
- **5개 트리거** — 자동 타임스탬프 갱신, 가격 이력 추적
- **저장 프로시저** — MySQL, PostgreSQL용 (`sql/` 디렉토리)
- **다국어 지원**: 한국어(`ko`), 영어(`en`), 다른 언어로 확장 가능
- **현실적 데이터 패턴**:
  - 10년간 사업 성장 곡선 (2016~2025)
  - 계절별 주문 패턴 (블랙프라이데이 피크, 여름 비수기)
  - 시간대별 주문 분포 (저녁 피크, 새벽 저조)
  - 파레토 고객 분포 (상위 20% = 주문의 60%)
  - 휴면/이탈 고객 모델링
  - 가격 가중 상품 선택 (저가 상품이 더 많이 팔림)

## 명령행 옵션

```
python generate.py [OPTIONS]

--size {small,medium,large}    데이터 규모 (기본: medium)
--locale {ko,en}               데이터 언어 (기본: ko)
--seed NUMBER                  재현성을 위한 랜덤 시드 (기본: 42)
--target {sqlite,...}          대상 데이터베이스 (기본: sqlite)
--all                          모든 데이터베이스 대상으로 생성
--download-images              Pexels API로 실제 상품 사진 다운로드
--pexels-key KEY               Pexels API 키 (또는 PEXELS_API_KEY 환경변수)
--config PATH                  설정 파일 경로 (기본: config.yaml)
```

## 데이터 규모 프로필

| 프로필 | 배율 | 총 행 수 | 파일 크기 | 생성 시간 | 용도 |
|--------|------|----------|-----------|-----------|------|
| small | 0.1x | ~23만 | ~29 MB | ~9초 | 빠른 테스트, CI |
| medium | 1.0x | ~200만 | ~250 MB | ~2분 | 일반 개발 (기본값) |
| large | 5.0x | ~1000만 | ~1.2 GB | ~10분 | 성능 테스트 |

## 스키마 개요

### 엔티티 관계도

```
categories ──┐
             ├── products ──┬── product_images
suppliers ───┘              ├── product_prices
                            ├── order_items ──── orders ──┬── payments
                            ├── reviews                   ├── shipping
                            ├── wishlists                 ├── returns
                            ├── cart_items ── carts        ├── complaints
                            └── inventory_transactions     └── coupon_usage ── coupons

customers ──┬── customer_addresses
            ├── orders
            ├── reviews
            ├── wishlists (M:N — 상품과 다대다)
            ├── carts
            ├── complaints
            └── coupon_usage

staff ──┬── orders (CS 담당 배정)
        └── complaints
```

### 테이블 (21개)

| # | 테이블 | 설명 | 행 수 (small) | 학습 포인트 |
|---|--------|------|---------------|-------------|
| 1 | `categories` | 상품 카테고리 (계층 구조) | 53 | 자기 참조 FK, 재귀 CTE |
| 2 | `suppliers` | 공급업체 | 50 | 1:N 관계 |
| 3 | `products` | 컴퓨터 및 주변기기 | 280 | 복수 FK, CHECK 제약조건 |
| 4 | `product_images` | 상품 이미지 (상품당 1~5장) | 748 | 1:N, 이미지 타입 |
| 5 | `product_prices` | 가격 변경 이력 | 814 | 시계열 데이터, SCD Type 2 |
| 6 | `customers` | 등록 고객 | 5,230 | NULL 처리, 등급, 휴면 |
| 7 | `customer_addresses` | 배송지 (고객당 1~3개) | 8,553 | 1:N, 기본 플래그 |
| 8 | `staff` | 직원/관리자 | 5 | 부서, 역할 |
| 9 | `orders` | 주문 | 34,689 | 상태 머신, 타임스탬프 |
| 10 | `order_items` | 주문 상세 | 74,513 | 연결 테이블, 수량 × 단가 |
| 11 | `payments` | 결제 | 34,689 | 카드/계좌/간편결제 상세 |
| 12 | `shipping` | 배송 추적 | 32,942 | 택배사, 상태 전이 |
| 13 | `reviews` | 상품 리뷰 (1~5점) | 7,947 | 평점 분포, 텍스트 |
| 14 | `inventory_transactions` | 재고 입출고 이력 | 12,935 | 추가 전용 원장 |
| 15 | `carts` | 장바구니 | 3,000 | 활성/전환/이탈 |
| 16 | `cart_items` | 장바구니 상세 | 9,172 | 장바구니 → 상품 |
| 17 | `coupons` | 할인 쿠폰 | 20 | 정율/정액, 유효기간 |
| 18 | `coupon_usage` | 쿠폰 사용 내역 | 172 | 3자 연결 테이블 |
| 19 | `wishlists` | 위시리스트 | 1,998 | **M:N** (고객 ↔ 상품), UNIQUE 복합키 |
| 20 | `returns` | 반품/교환 | 1,022 | 역물류, 검수 프로세스 |
| 21 | `complaints` | 고객 문의/불만 | 3,481 | 우선순위, 해결 추적 |

### 뷰 (18개)

| 뷰 | 설명 | 시연하는 SQL 개념 |
|----|------|-------------------|
| `v_monthly_sales` | 월별 매출 요약 | GROUP BY, 날짜 함수, 집계 |
| `v_customer_summary` | 고객 생애 가치 | LEFT JOIN, COALESCE, CASE, 서브쿼리 |
| `v_product_performance` | 상품 판매 지표 | 다중 LEFT JOIN, 마진율 계산 |
| `v_category_tree` | 전체 카테고리 경로 | **재귀 CTE**, 문자열 연결 |
| `v_daily_orders` | 일별 주문 현황 | 날짜 추출, CASE 피벗 |
| `v_payment_summary` | 결제 수단별 현황 | 비율 계산, 집계 |
| `v_order_detail` | 비정규화 주문 상세 | 5테이블 JOIN, NULL 처리 |
| `v_revenue_growth` | 전월 대비 매출 성장률 | **LAG 윈도우 함수** |
| `v_top_products_by_category` | 카테고리별 매출 상위 상품 | **ROW_NUMBER + PARTITION BY** |
| `v_customer_rfm` | RFM 마케팅 세분화 | **NTILE**, CTE, CASE 분류 |
| `v_cart_abandonment` | 장바구니 이탈 분석 | LEFT JOIN, 잠재 매출 |
| `v_supplier_performance` | 공급업체 성과 + 반품률 | 다중 서브쿼리 JOIN |
| `v_hourly_pattern` | 시간대별 주문 패턴 | 시간 추출, CASE 그룹핑 |
| `v_product_abc` | ABC / 파레토 (80/20) 분석 | **누적 SUM 윈도우 함수** |
| `v_staff_workload` | CS 직원 업무량 | 평균 처리 시간 |
| `v_coupon_effectiveness` | 쿠폰 ROI 분석 | ROI 계산 |
| `v_return_analysis` | 반품 사유별 분석 | CASE 피벗, 비율 |
| `v_yearly_kpi` | 연간 KPI 대시보드 | 다중 소스 서브쿼리 JOIN |

### 트리거 (5개, SQLite)

| 트리거 | 이벤트 | 동작 |
|--------|--------|------|
| `trg_orders_updated_at` | orders 상태 UPDATE | `updated_at` 자동 갱신 |
| `trg_reviews_updated_at` | reviews UPDATE | `updated_at` 자동 갱신 |
| `trg_product_price_history` | products 가격 UPDATE | 가격 이력 자동 삽입 |
| `trg_products_updated_at` | products UPDATE | `updated_at` 자동 갱신 |
| `trg_customers_updated_at` | customers UPDATE | `updated_at` 자동 갱신 |

### 저장 프로시저 (MySQL / PostgreSQL)

`sql/` 디렉토리에 위치:

| 프로시저/함수 | 설명 | 핵심 개념 |
|---------------|------|-----------|
| `sp_update_customer_grades` | 고객 등급 일괄 갱신 | CURSOR, 트랜잭션 |
| `sp_place_order` / `fn_place_order` | 주문 생성 (아이템 포함) | IN/OUT 파라미터, LAST_INSERT_ID |
| `sp_monthly_report` / `fn_monthly_report` | 월별 매출 보고서 | RETURNS TABLE, 날짜 함수 |
| `sp_low_stock_alert` / `fn_low_stock_alert` | 재고 부족 알림 | 판매 속도 계산 |
| `fn_customer_ltv` | 고객 생애 가치 | 스칼라 함수 |
| `fn_product_rating` | 상품 평균 평점 | 스칼라 함수 |
| `fn_update_timestamp` (PG) | 트리거 함수 | RETURNS TRIGGER |

## 관계 유형

이 데이터베이스는 모든 주요 관계 패턴을 포함합니다:

| 유형 | 예시 | 학습 포인트 |
|------|------|-------------|
| **1:1** | orders → payments | 주문당 하나의 결제 |
| **1:N** | customers → orders | 한 고객, 여러 주문 |
| **M:N** | customers ↔ products (wishlists 경유) | UNIQUE 복합 키 |
| **자기 참조** | categories.parent_id | 계층 구조 데이터 |
| **Nullable FK** | orders.staff_id | 선택적 관계 |

## 제약조건

- **CHECK 10개**: price >= 0, quantity > 0, rating BETWEEN 1 AND 5, grade IN (...) 등
- **UNIQUE 7개**: email, SKU, order_number, coupon code, slug, (customer_id, product_id)
- **인덱스 38개**: 모든 외래 키 및 자주 쓰이는 쿼리 패턴 커버

## 데이터 현실성

### 비즈니스 패턴
- **10년 성장 곡선**: 스타트업 → 성장기 → 코로나 특수 → 안정기
- **계절 패턴**: 블랙프라이데이 +25%, 여름 -15%, 신학기 +15%
- **시간대별**: 저녁 피크 (오후 8~10시), 새벽 최저 (오전 2~5시)
- **요일별**: 월/토/일이 수/목보다 약간 높음

### 고객 행동
- **파레토 분포**: 상위 5% 고객 = 대량 구매자; 하위 50% = 간헐적 구매
- **휴면 모델**: 가입 후 오래된 고객일수록 휴면 확률 상승 (5년+ = 45%)
- **인구통계**: 남성 65% (컴퓨터 매장), 연령 30대 피크 (33%)
- **미구매자**: 가입 후 한 번도 주문하지 않은 비율 ~25% (현실적 퍼널)

### 데이터 무결성 (검증 완료)
- 고객 가입일 이전 주문 없음
- 단종 상품 주문 없음
- 동일 주문 내 상품 중복 없음
- 배송완료일은 항상 출고일 이후
- 취소/반품 주문에 리뷰 없음
- 상품 가격이 최신 가격 이력과 일치

## 로케일 시스템

`data/locale/{code}.json`을 통해 다국어를 지원합니다:

| 데이터 | 한국어 (`ko`) | 영어 (`en`) |
|--------|---------------|-------------|
| 고객 이름 | 김민수, 이영희 | Justin Maxwell, Lisa Jones |
| 전화 형식 | 020-XXXX-XXXX | 555-XXXX-XXXX |
| 카테고리 | 데스크톱 PC, 노트북 | Desktop PC, Laptop |
| 택배사 | CJ대한통운, 한진택배 | FedEx, UPS, DHL |
| 카드사 | 신한카드, 삼성카드 | Visa, Mastercard |
| 은행 | KB국민은행, 신한은행 | Chase, Bank of America |
| 간편결제 | 카카오페이, 네이버페이 | PayPal, Apple Pay |
| 리뷰/문의 | 한국어 텍스트 | 영문 텍스트 |

**새 언어 추가**: `data/locale/{code}.json`을 기존 구조에 맞게 생성하면 됩니다.

## 프로젝트 구조

```
ecommerce-test-db/
├── generate.py              # 메인 실행 스크립트
├── config.yaml              # 성장 곡선, 비율, 설정
├── requirements.txt         # Python 의존성 (Faker, PyYAML)
├── data/
│   ├── categories.json      # 53개 상품 카테고리 (계층형)
│   ├── products.json        # 75개 상품 템플릿 (실제 브랜드)
│   ├── suppliers.json       # 50개 공급업체
│   └── locale/
│       ├── en.json          # 영문 텍스트 데이터
│       └── ko.json          # 한국어 텍스트 데이터
├── src/
│   ├── generators/          # 데이터 생성기 (도메인별 1개)
│   │   ├── base.py          # BaseGenerator (로케일, RNG, 헬퍼)
│   │   ├── products.py      # 카테고리, 공급업체, 상품, 가격
│   │   ├── customers.py     # 고객, 배송지
│   │   ├── staff.py         # 직원
│   │   ├── orders.py        # 주문, 주문 상세
│   │   ├── payments.py      # 결제 상세 (카드/계좌/간편결제)
│   │   ├── shipping.py      # 배송 추적
│   │   ├── reviews.py       # 상품 리뷰
│   │   ├── inventory.py     # 재고 입출고
│   │   ├── carts.py         # 장바구니
│   │   ├── coupons.py       # 쿠폰, 사용 내역
│   │   ├── wishlists.py     # 위시리스트 (M:N)
│   │   ├── returns.py       # 반품/교환
│   │   ├── complaints.py    # 고객 문의
│   │   └── images.py        # 상품 이미지 + Pexels 다운로더
│   ├── exporters/
│   │   └── sqlite_exporter.py  # SQLite DDL + 뷰 + 트리거 + 벌크 삽입
│   └── utils/
│       ├── fake_phone.py
│       ├── growth.py        # 연도별 성장 계산
│       └── seasonality.py   # 월별 계절성
├── sql/
│   ├── procedures_mysql.sql      # MySQL 저장 프로시저 & 함수
│   └── procedures_postgresql.sql # PostgreSQL 프로시저 & 함수
└── output/                  # 생성된 파일
    └── tutorial.db          # SQLite 데이터베이스
```

## SQL 개념 커버리지

이 데이터베이스로 거의 모든 SQL 개념을 연습할 수 있습니다:

| 개념 | 지원 | 연습 위치 |
|------|------|-----------|
| SELECT / WHERE / ORDER BY | ✅ | 모든 테이블 |
| JOIN (INNER, LEFT, RIGHT) | ✅ | 20+ FK 관계 |
| GROUP BY / HAVING | ✅ | `v_monthly_sales`, `v_payment_summary` |
| 서브쿼리 (스칼라, 상관) | ✅ | 카테고리별 1위 상품, 평균 이상 고객 |
| 윈도우 함수 | ✅ | `v_revenue_growth` (LAG), `v_customer_rfm` (NTILE), `v_top_products_by_category` (ROW_NUMBER), `v_product_abc` (누적 SUM) |
| CTE / 재귀 CTE | ✅ | `v_category_tree`, `v_customer_rfm` |
| CASE / COALESCE | ✅ | `v_customer_summary`, `v_daily_orders` |
| EXISTS / NOT EXISTS | ✅ | 위시리스트 → 구매 전환, 미주문 고객 |
| UNION / UNION ALL | ✅ | 문의 + 리뷰 통합 |
| INSERT / UPDATE / DELETE | ✅ | 모든 테이블 |
| VIEW | ✅ | 18개 뷰 |
| INDEX | ✅ | 38개 인덱스 |
| CHECK 제약조건 | ✅ | 10개 |
| UNIQUE 제약조건 | ✅ | 7개 (복합 키 포함) |
| FOREIGN KEY | ✅ | 20+ 외래 키 |
| NULL 처리 | ✅ | birth_date, gender, notes, staff_id |
| 날짜/시간 함수 | ✅ | julianday, strftime, DATE |
| 문자열 함수 | ✅ | SUBSTR, LIKE, \|\| 연결 |
| M:N 관계 | ✅ | wishlists (UNIQUE 복합 키) |
| SELF JOIN | ✅ | categories 계층 구조 |
| 집계 함수 | ✅ | COUNT, SUM, AVG, MIN, MAX |
| LIMIT / OFFSET | ✅ | 페이징 연습 |
| 트리거 | ✅ | 5개 (자동 타임스탬프, 가격 이력) |
| 저장 프로시저 | ✅ | MySQL + PostgreSQL (`sql/`) |

## 라이선스

이 도구는 **가상 데이터**를 생성합니다:
- 가짜 이름 (Faker 라이브러리 사용)
- 가짜 전화번호 (020-XXXX / 555-XXXX — 존재하지 않는 국번)
- 가짜 이메일 도메인 (testmail.kr / testmail.com — 존재하지 않는 도메인)
- 실제 브랜드/상품명은 현실감을 위해 사용 (Samsung, Intel, ASUS 등)

모든 생성 데이터는 **테스트 및 교육 목적으로만** 사용해야 합니다.

## 도움을 구합니다

이 프로젝트는 SQL 전문가가 아닌 개발자가 만들었습니다. 스키마 설계, 쿼리 작성, 튜토리얼 구성에 잘못되거나 누락된 부분이 있을 수 있습니다. SQL에 능숙하신 분들의 피드백과 기여를 환영합니다.

- 스키마나 데이터에 비현실적인 부분이 있다면 알려주세요
- 더 나은 쿼리 작성법이 있다면 제안해 주세요
- 추가하면 좋을 연습 문제나 주제가 있다면 공유해 주세요

Issues나 Pull Request로 기여해 주시면 감사하겠습니다.

## 작성자

**안영제** — civilian7@gmail.com
