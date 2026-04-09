# 생성기 상세 가이드

데이터베이스 생성기(`generate.py`)의 모든 옵션과 설정을 상세히 설명합니다. 기본 사용법은 [시작하기](getting-started.md)를 참고하세요.

---

## 1. 설치

### 필수 요구사항

- **Python 3.10** 이상
- pip (Python 패키지 관리자)

### 기본 설치

```bash
# 저장소 클론 후 의존성 설치
pip install -r requirements.txt
```

`requirements.txt`에는 다음 패키지가 포함되어 있습니다:

| 패키지 | 용도 |
|--------|------|
| `Faker>=25.0.0` | 한국어/영어 가상 데이터 생성 |
| `PyYAML>=6.0` | 설정 파일 파싱 |

!!! note "SQLite3"
    SQLite3는 Python 표준 라이브러리에 포함되어 있으므로 별도 설치가 필요 없습니다.

### 선택적 드라이버

MySQL 또는 PostgreSQL에 직접 적용(`--apply`)하려면 추가 드라이버가 필요합니다:

=== "MySQL/MariaDB"

    ```bash
    pip install mysql-connector-python
    ```

=== "PostgreSQL"

    ```bash
    pip install psycopg2-binary
    ```

---

## 2. 빠른 시작

### 기본 실행

```bash
# small 규모로 빠르게 생성
python generate.py --size small
```

### 출력 확인

```bash
# SQLite 파일 확인
ls -lh output/ecommerce.db

# 테이블 목록 확인
sqlite3 output/ecommerce.db ".tables"

# 데이터 건수 확인
sqlite3 output/ecommerce.db "SELECT COUNT(*) FROM orders;"
```

!!! tip "첫 실행 시"
    `--size small`로 시작하면 약 20만 건의 데이터가 10초 내에 생성됩니다. 기능을 확인한 후 `medium`이나 `large`로 규모를 키우세요.

---

## 3. 명령행 옵션 전체 목록

| 옵션 | 기본값 | 설명 | 예시 |
|------|--------|------|------|
| `--size` | `medium` (config) | 데이터 규모 (`small`, `medium`, `large`) | `--size large` |
| `--seed` | `42` (config) | 랜덤 시드 (재현성 보장) | `--seed 123` |
| `--start-date` | `2016-01-01` (config) | 데이터 시작 날짜 (YYYY-MM-DD) | `--start-date 2023-01-01` |
| `--end-date` | `2025-06-30` (config) | 데이터 종료 날짜 (YYYY-MM-DD) | `--end-date 2024-12-31` |
| `--locale` | `ko` (config) | 데이터 언어 (`ko`, `en`) | `--locale en` |
| `--target` | `sqlite` (config) | 대상 DB 형식 | `--target postgresql` |
| `--all` | - | 모든 DB 형식으로 생성 | `--all` |
| `--dirty-data` | - | 5~10% 노이즈 추가 (데이터 정제 연습용) | `--dirty-data` |
| `--config` | `config.yaml` | 설정 파일 경로 | `--config my_config.yaml` |
| `--apply` | - | 생성된 SQL을 대상 DB에 직접 적용 | `--apply` |
| `--host` | `localhost` | DB 서버 호스트 | `--host db.example.com` |
| `--port` | 자동 (MySQL:3306, PG:5432) | DB 서버 포트 | `--port 5433` |
| `--user` | 자동 (MySQL:`root`, PG:`postgres`) | DB 사용자명 | `--user admin` |
| `--password` | - | DB 비밀번호 | `--password secret` |
| `--ask-password` | - | 비밀번호를 대화형으로 입력 | `--ask-password` |
| `--database` | `ecommerce_test` | 대상 데이터베이스 이름 | `--database mydb` |
| `--download-images` | - | Pexels API로 상품 이미지 다운로드 | `--download-images` |
| `--pexels-key` | 환경변수 `PEXELS_API_KEY` | Pexels API 키 | `--pexels-key YOUR_KEY` |

---

## 4. 데이터 규모

| 항목 | small | medium | large |
|------|-------|--------|-------|
| **배율** | 0.1x | 1.0x (기준) | 5.0x |
| **총 행 수** | ~20만 건 | ~200만 건 | ~1,000만 건 |
| **SQLite 파일 크기** | ~15 MB | ~150 MB | ~800 MB |
| **생성 시간** | ~10초 | ~2분 | ~15분 |
| **용도** | CI/CD, 빠른 테스트 | 일반 개발/학습 | 성능 테스트, DB 벤치마크 |

!!! info "배율 계산"
    `config.yaml`의 `profiles` 섹션에서 각 규모의 `scale` 값을 정의합니다. 고객 수, 주문 수, 상품 수 등 모든 수량이 이 배율에 비례하여 조절됩니다.

---

## 5. 날짜 범위 설정

### 기본 사용법

```bash
# 특정 1년만 생성
python generate.py --start-date 2024-01-01 --end-date 2024-12-31

# 특정 분기만
python generate.py --start-date 2024-07-01 --end-date 2024-09-30

# 10년 전체 (기본값)
python generate.py --start-date 2016-01-01 --end-date 2025-06-30
```

### 성장 곡선 자동 보간

`config.yaml`의 `yearly_growth`에 정의되지 않은 연도를 지정하면, 가장 가까운 정의된 연도의 값을 기반으로 자동 보간합니다:

- 연도 차이 1년당 **5%** 성장/감소 적용
- 최소 0.3배, 최대 3.0배로 제한

```bash
# 2026~2028년을 지정하면 2025년 데이터를 기반으로 자동 보간
python generate.py --start-date 2026-01-01 --end-date 2028-12-31
```

!!! warning "주의"
    날짜 범위가 길수록 데이터 생성량이 비례하여 증가합니다. `--size small`과 함께 사용하면 긴 기간도 빠르게 생성할 수 있습니다.

---

## 6. 다국어 설정

### 사용법

```bash
# 한국어 데이터 (기본)
python generate.py --locale ko

# 영어 데이터
python generate.py --locale en
```

### 언어별 차이

`--locale` 설정에 따라 다음 데이터가 언어별로 달라집니다:

| 항목 | 한국어 (`ko`) | 영어 (`en`) |
|------|---------------|-------------|
| 카테고리명 | 데스크톱 PC, 노트북, ... | Desktop PC, Laptop, ... |
| 브랜드/상품명 | 한글 접미사 포함 | 영문 접미사 |
| 공급업체명 | 한글 법인명 | 영문 법인명 |
| 고객 이름 | Faker(ko_KR) | Faker(en_US) |
| 주소 | 한국 행정구역 기반 | 미국 주소 형식 |
| 이메일 도메인 | `testmail.kr` 등 | `testmail.com` 등 |
| 전화번호 | `020-XXXX-XXXX` | `555-XXXX-XXXX` |
| 택배사 | CJ대한통운, 한진택배, ... | FedEx, UPS, ... |
| 리뷰 내용 | 한국어 템플릿 | 영어 템플릿 |
| 고객 문의 | 한국어 템플릿 | 영어 템플릿 |
| 태그 | 한국어 태그 | 영어 태그 |
| 쿠폰명 | 신규 가입 환영 쿠폰, ... | Welcome Coupon, ... |
| 배송 메모 | 문 앞에 놓아주세요, ... | Leave at front door, ... |
| 달력 공휴일 | 한국 공휴일명 | 미국 공휴일명 |

### 새 언어 추가 방법

1. `data/locale/` 디렉토리에 새 로케일 파일 생성 (예: `ja.json`)
2. `ko.json` 또는 `en.json`을 복사하여 번역
3. `faker_locale` 값을 해당 로케일로 변경 (예: `ja_JP`)
4. 실행: `python generate.py --locale ja`

!!! note "로케일 파일 구조"
    로케일 파일에는 카테고리, 리뷰 템플릿, 배송 메모, 쿠폰명, 문의 템플릿 등 모든 언어 의존 데이터가 포함되어 있습니다. `data/locale/ko.json` 파일을 참고하세요.

---

## 7. 대상 데이터베이스

### SQLite (기본)

```bash
python generate.py --target sqlite
```

- 출력: `output/ecommerce.db`
- 별도 서버 불필요, 파일 하나로 즉시 사용 가능
- 뷰, 트리거, 인덱스 포함

### MySQL / MariaDB

=== "SQL 파일만 생성"

    ```bash
    python generate.py --target mysql
    ```
    출력: `output/mysql/schema.sql`, `data.sql`, `procedures.sql`

=== "DB에 직접 적용"

    ```bash
    python generate.py --target mysql --apply \
        --host localhost --port 3306 \
        --user root --ask-password \
        --database ecommerce_test
    ```

MySQL 특화 기능:

- `AUTO_INCREMENT` 기본 키
- `ENUM` 타입 (상태, 등급 등)
- `JSON` 칼럼 타입
- 저장 프로시저 (매출 집계, 고객 등급 갱신 등)
- `utf8mb4` 인코딩

### PostgreSQL

=== "SQL 파일만 생성"

    ```bash
    python generate.py --target postgresql
    ```
    출력: `output/postgresql/schema.sql`, `data.sql`, `procedures.sql`

=== "DB에 직접 적용"

    ```bash
    python generate.py --target postgresql --apply \
        --host localhost --port 5432 \
        --user postgres --ask-password \
        --database ecommerce_test
    ```

PostgreSQL 특화 기능:

- `GENERATED ALWAYS AS IDENTITY` 기본 키
- `JSONB` 칼럼 타입
- 함수 / 프로시저 (`PL/pgSQL`)
- 파티셔닝, 매터리얼라이즈드 뷰 등

### 모든 형식 동시 생성

```bash
python generate.py --all
```

!!! tip "SQL Server / Oracle"
    `--target sqlserver`와 `--target oracle`도 지원됩니다. 현재는 DDL + INSERT SQL 파일 생성까지 구현되어 있습니다.

---

## 8. config.yaml 상세 설명

`config.yaml`은 생성기의 핵심 설정 파일입니다. 각 섹션을 설명합니다.

### 기본 설정

```yaml
seed: 42                        # 랜덤 시드 (재현성)
locale: ko_KR                   # 데이터 로케일
shop_name: "테크샵(TechShop)"   # 쇼핑몰 이름
```

### 날짜 범위

```yaml
start_date: "2016-01-01"        # 데이터 시작일
end_date: "2025-06-30"          # 데이터 종료일
```

10년차 쇼핑몰의 데이터를 시뮬레이션합니다. CLI의 `--start-date` / `--end-date`로 오버라이드할 수 있습니다.

### 규모 프로필

```yaml
size: medium                    # 기본 규모

profiles:
  small:
    scale: 0.1                  # medium 대비 10%
  medium:
    scale: 1.0                  # 기준
  large:
    scale: 5.0                  # medium 대비 500%
```

### 출력 대상

```yaml
targets:
  - sqlite                      # 기본: SQLite만 생성
output_dir: ./output
```

### 성장 곡선 (yearly_growth)

연도별 쇼핑몰의 성장을 시뮬레이션합니다:

```yaml
yearly_growth:
  2016: { new_customers: 1000,  orders_per_day: [15, 25],   active_products: 300 }
  2017: { new_customers: 1800,  orders_per_day: [25, 40],   active_products: 500 }
  # ... (2018~2025)
  2025: { new_customers: 7500,  orders_per_day: [150, 200], active_products: 2800 }
```

| 필드 | 설명 |
|------|------|
| `new_customers` | 해당 연도의 신규 가입 고객 수 |
| `orders_per_day` | 일 평균 주문 수 범위 [최소, 최대] |
| `active_products` | 활성(판매 중) 상품 수 |

### 계절성 (monthly_seasonality)

월별 주문 배수를 정의합니다 (1.0 = 평균):

```yaml
monthly_seasonality:
  1: 0.85     # 1월 비수기
  3: 1.15     # 신학기
  7: 0.85     # 여름 비수기
  11: 1.25    # 블랙프라이데이
  12: 1.20    # 연말 세일
```

### 전화번호 / 이메일

```yaml
phone:
  prefix: "020"
  format: "020-{4d}-{4d}"       # 존재하지 않는 국번 사용

email:
  customer_domain: "testmail.kr"       # 고객 이메일 도메인
  staff_domain: "techshop-staff.kr"    # 직원 이메일 도메인
  supplier_domain: "test.kr"           # 공급업체 이메일 도메인
```

!!! info "가상 전화번호"
    `020` 국번은 한국에서 할당되지 않은 지역번호로, 영화/드라마의 미국 555번호와 같은 원리입니다. 영어 모드에서는 `555-XXXX-XXXX`를 사용합니다.

### 주문 설정

```yaml
order:
  free_shipping_threshold: 50000   # 무료배송 기준 (5만원)
  default_shipping_fee: 3000       # 기본 배송비
  items_per_order:
    min: 1
    max: 5
    avg: 2.3
  cancellation_rate: 0.05          # 취소율 5%
  return_rate: 0.03                # 반품율 3%
  points_earn_rate: 0.01           # 결제금액 1% 적립
```

### 결제 수단 비율

```yaml
payment_methods:
  card: 0.45            # 신용카드 45%
  kakao_pay: 0.20       # 카카오페이 20%
  naver_pay: 0.15       # 네이버페이 15%
  bank_transfer: 0.10   # 계좌이체 10%
  virtual_account: 0.05 # 가상계좌 5%
  point: 0.05           # 포인트 5%
```

### 택배사 비율

```yaml
carriers:
  CJ대한통운: 0.40
  한진택배: 0.25
  로젠택배: 0.20
  우체국택배: 0.15
```

### 리뷰 설정

```yaml
review:
  write_rate: 0.25               # 구매 확정의 25%가 리뷰 작성
  rating_distribution:           # 별점 분포 (현실적 J자 커브)
    5: 0.40
    4: 0.30
    3: 0.15
    2: 0.10
    1: 0.05
```

### 고객 등급 기준

```yaml
customer_grades:
  BRONZE: 0          # 기본
  SILVER: 500000     # 최근 1년 50만원 이상
  GOLD: 2000000      # 최근 1년 200만원 이상
  VIP: 5000000       # 최근 1년 500만원 이상
```

### 엣지 케이스 비율

```yaml
edge_cases:
  null_birth_date: 0.15          # 생년월일 NULL 15%
  null_gender: 0.10              # 성별 NULL 10%
  long_product_name: 0.01        # 200자 이상 상품명 1%
  zero_payment: 0.01             # 포인트 전액 결제 1%
  bulk_order: 0.005              # 기업 대량 구매 0.5%
  no_review_products: 0.20       # 리뷰 없는 상품 20%
```

---

## 9. config_detailed.yaml 상세 설명

`config_detailed.yaml`은 120개 이상의 세부 파라미터를 제공합니다. `config.yaml`에 정의되지 않은 값은 이 파일에서 불러옵니다.

### customer (고객)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `gender_ratio` | `[0.65, 0.35]` | 남성/여성 비율 |
| `dormancy_rates.under_1year` | `0.05` | 가입 1년 미만 휴면율 |
| `dormancy_rates.1_to_3_years` | `0.15` | 1~3년차 휴면율 |
| `dormancy_rates.3_to_5_years` | `0.30` | 3~5년차 휴면율 |
| `dormancy_rates.over_5_years` | `0.45` | 5년 초과 휴면율 |
| `withdrawal_rate` | `0.03` | 탈퇴(비활성화)율 |
| `never_logged_in_rate` | `0.05` | 가입 후 미접속 비율 |
| `address_count_weights` | `[0.50, 0.35, 0.15]` | 주소 1/2/3개 보유 확률 |
| `apartment_probability` | `0.70` | 아파트 상세주소 비율 |

**변경 예시:** 여성 고객 비율을 높이려면:

```yaml
customer:
  gender_ratio: [0.50, 0.50]
```

### product (상품)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `discontinuation_rate` | `0.25` | 단종율 (전체 상품의 25%) |
| `price_history.max_changes` | `4` | 상품당 최대 가격 변경 횟수 |
| `price_history.change_ratio_range` | `[0.80, 1.15]` | 가격 변동 범위 (-20%~+15%) |
| `images_per_product_weights` | `[15, 35, 30, 15, 5]` | 이미지 1/2/3/4/5개 확률 |

### order (주문)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `hourly_weights` | 24개 가중치 | 시간대별 주문 빈도 (0시~23시) |
| `weekday_weights` | `[1.10, 0.95, ..., 1.10]` | 요일별 주문 빈도 (월~일) |
| `daily_variance` | `[0.8, 1.2]` | 일별 주문 수 변동 범위 |
| `item_count_weights` | `[40, 30, 15, 10, 5]` | 상품 1/2/3/4/5개 주문 확률 |
| `bulk_item_range` | `[5, 15]` | 대량 주문 시 상품 수 범위 |
| `bulk_quantity_range` | `[2, 10]` | 대량 주문 시 수량 범위 |
| `discount_probability` | `0.10` | 할인 적용 확률 |
| `discount_ratio_range` | `[0.03, 0.15]` | 할인율 범위 (3%~15%) |
| `points_usage_probability` | `0.10` | 포인트 사용 확률 |
| `points_usage_range` | `[100, 5000]` | 포인트 사용량 범위 |
| `points_max_ratio` | `0.30` | 최대 포인트 결제 비율 (30%) |
| `status_timeline_days` | `[3, 5, 10, 21]` | 상태 전이 기준일 (대기/결제/배송/완료) |
| `completion_days_range` | `[8, 21]` | 구매 확정까지 소요일 |
| `cancellation_hours_range` | `[1, 48]` | 취소까지 소요 시간 |
| `delivery_notes_probability` | `0.35` | 배송 메모 작성 확률 |

**파레토 분포** (상위 고객 주문 집중):

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `pareto.tiers` | `[0.05, 0.20, 0.50]` | 상위 5% / 20% / 50% 구간 |
| `pareto.weights` | `[10.0, 4.0, 1.5, 0.5]` | 각 구간별 주문 가중치 |

**가격대별 조회 가중치**:

| 가격대 | 가중치 | 의미 |
|--------|-------:|------|
| ~5만원 | 5.0 | 저가 상품이 가장 많이 조회 |
| ~20만원 | 3.0 | |
| ~50만원 | 2.0 | |
| ~100만원 | 1.0 | |
| ~200만원 | 0.5 | |
| 200만원 초과 | 0.2 | 고가 상품은 드물게 조회 |

### payment (결제)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `cancelled_refund_probability` | `0.50` | 취소 주문 환불 확률 |
| `receipt_probability.bank_transfer` | `0.70` | 계좌이체 현금영수증 비율 |
| `receipt_probability.easy_pay` | `0.20` | 간편결제 현금영수증 비율 |
| `processing_delays.card_minutes` | `[1, 30]` | 카드 결제 처리 지연 (분) |
| `processing_delays.virtual_account_days` | `[7, 21]` | 가상계좌 입금 기한 (일) |
| `processing_delays.bank_transfer_minutes` | `[1, 30]` | 계좌이체 처리 지연 (분) |

### shipping (배송)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `ship_days_range` | `[1, 3]` | 주문에서 발송까지 (일) |
| `deliver_days_range` | `[1, 4]` | 발송에서 배달까지 (일) |

### review (리뷰)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `creation_delay_days` | `[3, 30]` | 주문 후 리뷰 작성까지 (일) |
| `title_probability` | `0.80` | 리뷰 제목 작성 확률 |
| `empty_content_probability` | `0.10` | 리뷰 본문 미작성 확률 |

### inventory (재고)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `initial_stock_range` | `[50, 500]` | 초기 재고량 범위 |
| `restock_frequency_range` | `[1, 5]` | 재입고 빈도 (횟수) |
| `restock_quantity_range` | `[20, 300]` | 재입고 수량 범위 |

### cart (장바구니)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `target_count_base` | `30000` | 기본 장바구니 수 (scale 곱) |
| `status_weights` | `[0.2, 0.5, 0.3]` | 활성/포기/전환 비율 |
| `items_range` | `[1, 5]` | 장바구니 상품 수 범위 |
| `item_quantity_weights` | `[0.7, 0.2, 0.1]` | 수량 1/2/3개 확률 |
| `item_add_time_minutes` | `[0, 120]` | 상품 추가 시간 간격 (분) |

### coupon (쿠폰)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `target_count_base` | `200` | 기본 쿠폰 종류 수 |
| `max_count` | `500` | 최대 쿠폰 종류 수 |
| `percent_values` | `[5, 10, 15, 20, 30]` | 퍼센트 할인 값 목록 |
| `fixed_values` | `[3000, ..., 50000]` | 정액 할인 값 목록 |
| `min_order_amounts` | `[null, 30000, ..., 500000]` | 최소 주문 금액 목록 |
| `duration_days` | `[30, 60, 90, 180, 365]` | 유효 기간 (일) |
| `usage_limits` | `[null, 100, ..., 5000]` | 총 사용 횟수 제한 |
| `per_user_limits` | `[1, 1, 1, 2, 3]` | 1인당 사용 제한 |
| `target_usage_base` | `50000` | 기본 쿠폰 사용 건수 |

### wishlist (위시리스트)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `target_count_base` | `20000` | 기본 위시리스트 건수 |
| `purchase_conversion_rate` | `0.40` | 찜 후 구매 전환율 |
| `pre_purchase_days_range` | `[1, 30]` | 찜 후 구매까지 (일) |
| `notify_on_sale_rate` | `0.30` | 세일 알림 신청률 |

### return (반품/교환)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `request_delay_days` | `[0, 14]` | 주문 후 반품 요청까지 (일) |
| `pickup_days_range` | `[1, 3]` | 수거까지 소요일 |
| `full_return_probability` | `0.70` | 전체 반품 확률 (vs 부분) |
| `reception_days_range` | `[1, 4]` | 반품 수령까지 소요일 |
| `inspection_hours_range` | `[2, 48]` | 검수 소요 시간 |
| `completion_hours_range` | `[1, 24]` | 환불 완료까지 소요 시간 |

### complaint (고객 문의/불만)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `order_complaint_rate` | `0.08` | 주문 대비 문의 발생률 |
| `general_ratio` | `0.25` | 일반 문의 비율 |
| `unresolved_rate` | `0.05` | 미해결 문의 비율 |
| `auto_closure_probability` | `0.85` | 자동 종결 확률 |
| `response_hours_by_priority` | 긴급:1~4h, 높음:2~12h, ... | 우선순위별 응답 시간 |
| `category_weights` | 제품불량:15%, 배송:25%, ... | 문의 유형별 비율 |
| `channel_weights` | 웹:35%, 전화:25%, ... | 문의 채널별 비율 |

### staff (직원)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `target_count_base` | `50` | 기본 직원 수 |
| `max_count` | `200` | 최대 직원 수 |
| `admin_count` | `3` | 관리자(admin) 수 |
| `manager_threshold` | `10` | 매니저 역할 기준 ID |
| `termination_rate` | `0.10` | 퇴직률 |

### tags (태그)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `per_product_range` | `[2, 6]` | 상품당 태그 수 범위 |
| `price_thresholds.high_end` | `2000000` | 고급 태그 기준 가격 |
| `price_thresholds.premium` | `1000000` | 프리미엄 태그 기준 |
| `price_thresholds.budget` | `100000` | 가성비 태그 기준 |

### product_views (상품 조회)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `views_per_order` | `8` | 주문당 평균 조회 수 |
| `session_gap_minutes` | `30` | 세션 구분 기준 (분) |
| `session_probability` | `0.30` | 세션 내 추가 조회 확률 |
| `session_extra_views` | `[1, 4]` | 세션 내 추가 조회 수 |
| `pre_purchase_views` | `[1, 5]` | 구매 전 조회 수 |
| `pre_purchase_days` | `[0, 14]` | 구매 전 조회 기간 (일) |
| `referrer_weights` | 직접:20%, 검색:35%, 광고:15%, ... | 유입 경로별 비율 |
| `device_weights` | 데스크톱:45%, 모바일:45%, 태블릿:10% | 기기별 비율 |

---

## 10. 더티 데이터 모드

### 사용법

```bash
python generate.py --dirty-data
```

### 추가되는 노이즈

`--dirty-data` 플래그를 사용하면 전체 데이터의 **5~10%**에 의도적인 노이즈가 추가됩니다:

| 대상 | 노이즈 유형 | 예시 |
|------|------------|------|
| 고객 이름 | 앞/뒤 공백, 이중 공백 | `"  홍길동"`, `"홍  길동"` |
| 이메일 | 대소문자 혼용, @ 앞 공백 | `"USER@testmail.kr"`, `"user @testmail.kr"` |
| 전화번호 | 하이픈 제거, 공백 구분, 국제번호 | `"02012345678"`, `"+82-20-1234-5678"` |
| 생년월일 | 빈 문자열, "N/A", "unknown" | NULL 대신 `""` 또는 `"N/A"` |
| 성별 | 소문자, 영문 표기, 빈 문자열 | `"m"`, `"Male"`, `""` |
| 상품명 | 앞 공백, 논브레이킹 스페이스 | `" 삼성 SSD"`, `"삼성\u00a0SSD"` |
| 주문 메모 | 공백만, "N/A", "-" | `" "`, `"N/A"` |
| 리뷰 내용 | 불필요한 개행 | `"좋습니다.\n"` |

### 데이터 정제 연습 활용법

!!! example "실습 아이디어"
    1. `TRIM()`으로 공백 제거 연습
    2. `LOWER()`/`UPPER()`로 대소문자 통일
    3. `CASE WHEN`으로 비일관적 값 정규화
    4. `NULL` vs 빈 문자열 구분 처리
    5. `REPLACE()`로 전화번호 형식 통일

---

## 11. 시드와 재현성

### 기본 동작

```bash
# 같은 시드 → 같은 데이터
python generate.py --seed 42
python generate.py --seed 42   # 동일한 결과
```

### 원리

- 시드 값은 모든 생성기(Generator)에 전달됩니다
- 각 생성기는 `seed + offset` 형태로 독립적인 난수 생성기를 초기화합니다
- 동일한 시드, 동일한 설정 → 바이트 단위까지 동일한 데이터베이스

### 다른 데이터 생성

```bash
# 시드를 바꾸면 완전히 다른 데이터 세트
python generate.py --seed 100
python generate.py --seed 200
```

!!! tip "활용 팁"
    - **CI/CD**: 시드를 고정하여 테스트 결과를 재현할 수 있습니다
    - **다양한 데이터셋**: 시드를 바꿔 여러 버전의 테스트 데이터를 생성할 수 있습니다
    - **기본 시드**: 지정하지 않으면 `config.yaml`의 `seed: 42`가 사용됩니다

---

## 12. 출력 파일 구조

```
output/
├── ecommerce.db                 # SQLite 데이터베이스 (기본)
├── mysql/
│   ├── schema.sql               # 테이블/인덱스/뷰 DDL
│   ├── data.sql                 # INSERT 문 (모든 데이터)
│   └── procedures.sql           # 저장 프로시저
└── postgresql/
    ├── schema.sql               # 테이블/인덱스/뷰 DDL
    ├── data.sql                 # INSERT 문 (모든 데이터)
    └── procedures.sql           # 함수/프로시저
```

!!! note "SQLite DB 내용"
    `ecommerce.db`에는 30개 테이블, 뷰, 트리거, 인덱스가 포함되어 있습니다. 상세 스키마는 [데이터베이스 스키마](schema.md) 페이지를 참고하세요.

---

## 13. 데이터 검증

### 무결성 검사 실행

```bash
python check_integrity.py
# 또는 특정 DB 파일 지정
python check_integrity.py output/ecommerce.db
```

### 검증 항목

| 검사 | 설명 |
|------|------|
| **테이블 인벤토리** | 모든 테이블의 행 수 확인 |
| **뷰/트리거/인덱스** | 메타데이터 개체 수 확인 |
| **외래 키 무결성** | 23개 FK 관계의 고아 레코드 검사 |
| **시간 무결성** | 주문일 > 가입일, 배송일 > 발송일 등 |
| **현실감 지표** | 성별 주문 빈도, 첫 구매/재구매 평균 금액 |
| **신규 테이블** | 포인트, 프로모션, Q&A, 달력 데이터 확인 |
| **CS 데이터** | 문의 유형, 에스컬레이션, 반품-클레임 연결 |
| **출력 파일** | SQLite/MySQL/PostgreSQL 파일 존재 및 크기 확인 |

검사 결과 예시:

```
==========================================================
COMPREHENSIVE DATA INTEGRITY CHECK
==========================================================
[1] Tables: 30
  categories                         53
  customers                       52,500
  orders                         195,000
  ...
  TOTAL                        2,134,567

[5] FOREIGN KEY INTEGRITY
  OK  orders.customer_id → customers
  OK  order_items.order_id → orders
  ...
  Result: 23/23 passed

ALL CHECKS PASSED
==========================================================
```

---

## 14. 자주 묻는 질문 (FAQ)

??? question "Q: medium 규모는 얼마나 걸리나요?"
    `--size medium`은 약 **2분** 소요됩니다 (SQLite 기준). MySQL/PostgreSQL SQL 파일 생성까지 포함하면 약 3~4분입니다. 하드웨어에 따라 차이가 있습니다.

??? question "Q: 특정 테이블만 생성할 수 있나요?"
    현재는 모든 테이블을 한 번에 생성합니다. 테이블 간 외래 키 관계가 있어 부분 생성 시 무결성 문제가 발생할 수 있습니다. 생성 후 불필요한 테이블을 `DROP TABLE`로 제거하세요.

??? question "Q: 기존 DB에 추가 데이터를 넣을 수 있나요?"
    직접적인 증분 생성은 지원하지 않습니다. 대신:
    
    1. 다른 시드(`--seed`)로 새 DB를 생성합니다
    2. 날짜 범위를 다르게 설정하여 다른 기간의 데이터를 생성합니다
    3. `INSERT INTO ... SELECT FROM`으로 필요한 데이터를 병합합니다

??? question "Q: 다른 업종(의류, 식품 등)으로 변경할 수 있나요?"
    현재는 컴퓨터/주변기기 쇼핑몰에 특화되어 있습니다. 업종을 변경하려면:
    
    1. `data/locale/ko.json`의 카테고리, 상품, 태그를 수정합니다
    2. `data/products.json`의 상품 마스터를 교체합니다
    3. `data/suppliers.json`의 공급업체를 수정합니다
    4. `config.yaml`의 가격대, 결제 수단 비율 등을 업종에 맞게 조정합니다

??? question "Q: Windows에서도 동작하나요?"
    네, Python 3.10 이상이 설치되어 있으면 Windows, macOS, Linux 모두에서 동작합니다.

??? question "Q: --all 옵션은 SQLite, MySQL, PostgreSQL을 모두 생성하나요?"
    `--all`은 sqlite, mysql, postgresql, sqlserver, oracle 총 5가지 형식을 모두 생성합니다. 단, sqlserver와 oracle은 아직 완전히 구현되지 않을 수 있습니다.

??? question "Q: 이미지 다운로드는 어떻게 하나요?"
    Pexels API를 사용합니다. [pexels.com/api](https://www.pexels.com/api/)에서 무료 API 키를 발급받은 후:
    
    ```bash
    python generate.py --download-images --pexels-key YOUR_API_KEY
    ```
    
    또는 환경변수로 설정:
    
    ```bash
    export PEXELS_API_KEY=YOUR_API_KEY
    python generate.py --download-images
    ```
