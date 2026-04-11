# 04. 생성기 고급 옵션

[03. 데이터 생성](03-generate.md)에서 기본 실행 방법을 익혔다면, 이 페이지에서는 데이터 규모, 언어, 날짜 범위, 노이즈, 설정 파일 등 상세 옵션을 다룹니다.

## 명령행 옵션 전체 목록

| 옵션 | 기본값 | 설명 | 예시 |
|------|--------|------|------|
| `--size` | `medium` (config) | 데이터 규모 (`small`, `medium`, `large`) | `--size large` |
| `--seed` | `42` (config) | 랜덤 시드 (재현성 보장) | `--seed 123` |
| `--start-date` | `2016-01-01` | 데이터 시작 날짜 | `--start-date 2023-01-01` |
| `--end-date` | `2025-12-31` | 데이터 종료 날짜 | `--end-date 2024-12-31` |
| `--locale` | `ko` | 데이터 언어 (`ko`, `en`) | `--locale en` |
| `--target` | `sqlite` | 대상 DB 형식 | `--target postgresql` |
| `--all` | - | 모든 DB 형식으로 생성 | `--all` |
| `--dirty-data` | - | 5~10% 노이즈 추가 | `--dirty-data` |
| `--config` | `config.yaml` | 설정 파일 경로 | `--config my_config.yaml` |
| `--apply` | - | 생성된 SQL을 DB에 직접 적용 | `--apply` |
| `--host` | `localhost` | DB 서버 호스트 | `--host db.example.com` |
| `--port` | 자동 | DB 서버 포트 | `--port 5433` |
| `--user` | 자동 | DB 사용자명 | `--user admin` |
| `--password` | - | DB 비밀번호 | `--password secret` |
| `--ask-password` | - | 비밀번호를 대화형으로 입력 | `--ask-password` |
| `--database` | `ecommerce_test` | 대상 데이터베이스 이름 | `--database mydb` |
| `--download-images` | - | Pexels API로 상품 이미지 다운로드 | `--download-images` |
| `--pexels-key` | 환경변수 | Pexels API 키 | `--pexels-key YOUR_KEY` |

---

## 데이터 규모

| 항목 | small | medium | large |
|------|-------|--------|-------|
| **배율** | 0.1x | 1.0x (기준) | 5.0x |
| **총 행 수** | ~69만 건 | ~697만 건 | ~3,480만 건 |
| **SQLite 파일 크기** | ~80 MB | ~800 MB | ~4 GB |
| **생성 시간** | ~20초 | ~3분 | ~15분 |
| **용도** | SQL 학습, 빠른 테스트 | 성능 테스트, EXPLAIN 연습 | DB 벤치마크, 대용량 처리 |

```bash
python generate.py --size small     # 학습용 (추천)
python generate.py --size medium    # 성능 테스트
python generate.py --size large     # 대용량 벤치마크
```

---

## 날짜 범위 설정

기본값은 2016-01-01 ~ 2025-12-31 (10년)입니다.

```bash
# 특정 1년만 생성
python generate.py --start-date 2024-01-01 --end-date 2024-12-31

# 특정 분기만
python generate.py --start-date 2024-07-01 --end-date 2024-09-30
```

`config.yaml`의 `yearly_growth`에 정의되지 않은 연도를 지정하면, 가장 가까운 연도를 기반으로 연 5% 성장률로 자동 보간합니다.

!!! warning "주의"
    날짜 범위가 길수록 데이터 생성량이 비례하여 증가합니다. `--size small`과 함께 사용하면 긴 기간도 빠르게 생성할 수 있습니다.

---

## 다국어 설정

```bash
python generate.py --locale ko    # 한국어 (기본)
python generate.py --locale en    # 영어
```

### 언어별 차이

| 항목 | 한국어 (`ko`) | 영어 (`en`) |
|------|---------------|-------------|
| 카테고리명 | 데스크톱 PC, 노트북, ... | Desktop PC, Laptop, ... |
| 고객 이름 | Faker(ko_KR) | Faker(en_US) |
| 주소 | 한국 행정구역 기반 | 미국 주소 형식 |
| 전화번호 | `020-XXXX-XXXX` | `555-XXXX-XXXX` |
| 택배사 | CJ대한통운, 한진택배, ... | FedEx, UPS, ... |
| 리뷰/문의 | 한국어 템플릿 | 영어 템플릿 |
| 공휴일 | 한국 공휴일 (가상) | 영어권 공휴일 (가상) |

### 새 언어 추가

1. `data/locale/ko.json`을 복사하여 `ja.json` 생성
2. 각 섹션을 해당 언어로 번역
3. `python generate.py --locale ja`로 실행

아래는 일본어(`ja.json`)를 추가하는 실제 예시입니다. 모든 키를 번역하면 되며, 구조는 동일합니다:

```json
{
  "faker_locale": "ja_JP",
  "phone": {
    "format": "090-{0:04d}-{1:04d}",
    "description": "日本の仮想携帯番号"
  },
  "email": {
    "customer_domains": [
      ["testmail.jp", 0.30],
      ["fakemail.jp", 0.20],
      ["example.co.jp", 0.15]
    ],
    "staff_domain": "techshop-staff.jp",
    "supplier_domain": "test.jp"
  },
  "categories": {
    "desktop-prebuilt": "デスクトップPC",
    "laptop-general": "ノートパソコン",
    "monitor-general": "モニター",
    "keyboard-mechanical": "メカニカルキーボード"
  },
  "shipping": {
    "carriers": {
      "ヤマト運輸": 0.40,
      "佐川急便": 0.30,
      "日本郵便": 0.20,
      "西濃運輸": 0.10
    }
  },
  "holidays": {
    "01-01": "元日",
    "01-13": "成人の日",
    "02-11": "建国記念の日",
    "03-21": "春分の日",
    "05-03": "憲法記念日"
  },
  "coupon": {
    "names": [
      "新規登録クーポン",
      "お誕生日クーポン",
      "リピーター限定割引"
    ]
  }
}
```

!!! tip "AI를 활용한 번역"
    `ko.json` 전체를 AI에게 넘기고 "이 JSON을 일본어로 번역해주세요. 키는 유지하고 값만 번역"이라고 요청하면 빠르게 작업할 수 있습니다.

---

## 더티 데이터 모드

실무에서 자주 만나는 "지저분한" 데이터를 의도적으로 생성합니다. 데이터 정제(Data Cleaning) 연습에 유용합니다.

```bash
python generate.py --dirty-data
```

전체 데이터의 **5~10%**에 다음과 같은 노이즈가 추가됩니다:

| 대상 | 노이즈 유형 | 예시 |
|------|------------|------|
| 고객 이름 | 앞/뒤 공백, 이중 공백 | `"  홍길동"`, `"홍  길동"` |
| 이메일 | 대소문자 혼용, @ 앞 공백 | `"USER@testmail.kr"` |
| 전화번호 | 하이픈 제거, 국제번호 | `"02012345678"`, `"+82-20-1234-5678"` |
| 생년월일 | 빈 문자열, "N/A" | NULL 대신 `""` 또는 `"N/A"` |
| 성별 | 소문자, 영문 표기 | `"m"`, `"Male"`, `""` |
| 상품명 | 앞 공백, 특수 공백 | `" 삼성 SSD"` |

!!! tip "정제 연습 아이디어"
    - `TRIM()`으로 공백 제거
    - `LOWER()`/`UPPER()`로 대소문자 통일
    - `CASE WHEN`으로 비일관적 값 정규화
    - `NULL` vs 빈 문자열 구분 처리
    - `REPLACE()`로 전화번호 형식 통일

---

## 시드와 재현성 { #시드와-재현성 }

**시드(seed)란?** 난수 생성기의 시작점입니다. 컴퓨터의 "랜덤"은 실제로는 시드값에서 출발하는 수열이므로, 같은 시드를 사용하면 생성되는 고객 이름, 주문 날짜, 금액 등이 **항상 동일**합니다.

이 튜토리얼은 **시드값 42**를 기본으로 사용합니다. 따라서 여러분이 동일한 설정으로 생성하면, 레슨의 쿼리 예제와 결과표가 정확히 일치합니다.

```bash
python generate.py --seed 42     # 항상 동일한 데이터
python generate.py --seed 42     # 위와 바이트 단위까지 동일
python generate.py --seed 100    # 완전히 다른 데이터
```

**시드를 바꾸면?** 테이블 구조는 동일하지만 고객 이름, 주문 건수, 금액 등이 모두 달라집니다. 레슨의 쿼리 결과와 일치하지 않게 되지만, 자신만의 데이터로 연습하고 싶을 때 유용합니다.

- 시드를 지정하지 않으면 `config.yaml`의 `seed: 42`가 사용됩니다
- CI/CD에서 시드를 고정하면 테스트 결과를 재현할 수 있습니다
- 다른 시드로 여러 데이터셋을 만들어 비교 연습에 활용할 수 있습니다

---

## config.yaml 설정

`config.yaml`은 생성기의 핵심 설정 파일입니다. CLI 옵션보다 우선도가 낮으며, CLI로 오버라이드할 수 있습니다.

### 주요 설정

```yaml
seed: 42                          # 랜덤 시드
locale: ko_KR                     # 데이터 로케일
shop_name: "테크샵(TechShop)"     # 쇼핑몰 이름
start_date: "2016-01-01"          # 데이터 시작일
end_date: "2025-12-31"            # 데이터 종료일
size: medium                      # 기본 규모
```

### 성장 곡선

연도별 쇼핑몰의 성장을 시뮬레이션합니다:

```yaml
yearly_growth:
  2016: { new_customers: 1000,  orders_per_day: [15, 25],   active_products: 300 }
  2020: { new_customers: 4500,  orders_per_day: [80, 120],  active_products: 1500 }
  2025: { new_customers: 7500,  orders_per_day: [150, 200], active_products: 2800 }
```

### 계절성

월별 주문 배수 (1.0 = 평균):

```yaml
monthly_seasonality:
  1: 0.85     # 1월 비수기
  3: 1.15     # 신학기
  7: 0.85     # 여름 비수기
  11: 1.25    # 블랙프라이데이
  12: 1.20    # 연말 세일
```

### 주문 설정

```yaml
order:
  free_shipping_threshold: 50000   # 무료배송 기준 (5만원)
  default_shipping_fee: 3000       # 기본 배송비
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
  no_review_products: 0.20       # 리뷰 없는 상품 20%
```

### config_detailed.yaml 세부 파라미터

`config.yaml`에 없는 값은 `config_detailed.yaml`에서 자동으로 불러옵니다. 120개 이상의 파라미터로 데이터의 세부 특성을 조절할 수 있습니다.

**고객 (customer)**

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| gender_ratio | [0.65, 0.35] | 남/여 비율 |
| dormancy_rates.under_1year | 0.05 | 1년 미만 고객 휴면율 |
| dormancy_rates.over_5_years | 0.45 | 5년 이상 고객 휴면율 |
| withdrawal_rate | 0.03 | 탈퇴율 |
| never_logged_in_rate | 0.05 | 미로그인 비율 |
| address_count_weights | [0.50, 0.35, 0.15] | 주소 1/2/3개 확률 |
| apartment_probability | 0.70 | 아파트(상세주소) 비율 |

**상품 (product)**

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| discontinuation_rate | 0.25 | 단종률 |
| price_history.max_changes | 4 | 상품당 최대 가격 변경 횟수 |
| price_history.change_ratio_range | [0.80, 1.15] | 가격 변동 범위 (-20%~+15%) |
| images_per_product_weights | [15, 35, 30, 15, 5] | 이미지 1~5장 확률 |

**주문 (order)**

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| hourly_weights | [0.3, 0.2, ..., 0.8] | 시간대별 주문 가중치 (24개) |
| weekday_weights | [1.10, 0.95, ..., 1.10] | 요일별 주문 가중치 (월~일) |
| daily_variance | [0.8, 1.2] | 일별 주문 수 변동 범위 |
| item_count_weights | [40, 30, 15, 10, 5] | 주문당 상품 1~5개 확률 |
| discount_probability | 0.10 | 할인 적용 확률 |
| points_usage_probability | 0.10 | 포인트 사용 확률 |
| points_max_ratio | 0.30 | 주문액 대비 최대 포인트 사용 비율 |
| status_timeline_days | [3, 5, 10, 21] | 상태 전이 기간 (일) |
| delivery_notes_probability | 0.35 | 배송 메모 작성 확률 |

**결제 (payment)**

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| cancelled_refund_probability | 0.50 | 취소 시 환불 확률 |
| processing_delays.card_minutes | [1, 30] | 카드 결제 처리 시간 (분) |

**배송 (shipping)**

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| ship_days_range | [1, 3] | 주문→발송 소요일 |
| deliver_days_range | [1, 4] | 발송→배송 완료 소요일 |

**리뷰 (review)**

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| creation_delay_days | [3, 30] | 주문 후 리뷰 작성까지 일수 |
| title_probability | 0.80 | 제목 작성 확률 |
| empty_content_probability | 0.10 | 내용 미작성 확률 |

**재고 (inventory)**

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| initial_stock_range | [50, 500] | 초기 재고 범위 |
| restock_frequency_range | [1, 5] | 입고 빈도 (연간) |
| restock_quantity_range | [20, 300] | 입고 수량 범위 |

**장바구니 (cart)**

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| status_weights | [0.2, 0.5, 0.3] | active/abandoned/converted 비율 |
| items_range | [1, 5] | 장바구니 상품 수 범위 |

**쿠폰 (coupon)**

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| percent_values | [5, 10, 15, 20, 30] | 할인율 (%) |
| fixed_values | [3000, 5000, ..., 50000] | 정액 할인 (원) |
| duration_days | [30, 60, 90, 180, 365] | 쿠폰 유효 기간 |

**반품 (return)**

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| request_delay_days | [0, 14] | 주문 후 반품 요청까지 일수 |
| full_return_probability | 0.70 | 전체 반품 확률 (vs 부분) |
| inspection_hours_range | [2, 48] | 검수 소요 시간 |

**문의/불만 (complaint)**

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| order_complaint_rate | 0.08 | 주문당 문의 발생률 |
| unresolved_rate | 0.05 | 미해결 비율 |
| response_hours_by_priority | urgent: [1,4], low: [12,96] | 우선순위별 응답 시간 |

**상품 조회 (product_views)**

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| views_per_order | 8 | 주문당 평균 조회 수 |
| referrer_weights | direct: 0.20, search: 0.35, ... | 유입 경로 비율 |
| device_weights | desktop: 0.45, mobile: 0.45, tablet: 0.10 | 디바이스 비율 |

---

## 소스코드 구조

```
generate.py                 ← 메인 실행 스크립트
verify.py                   ← 환경 검증 스크립트
config.yaml                 ← 기본 설정 파일
config_detailed.yaml        ← 세부 파라미터 (120+)
data/
├── categories.json         ← 상품 카테고리 마스터 (수동 큐레이션)
├── products.json           ← 상품 마스터 (브랜드, 모델명, 가격대)
├── suppliers.json          ← 공급업체 마스터
└── locale/
    ├── ko.json             ← 한국어 로케일 데이터
    └── en.json             ← 영어 로케일 데이터
src/
├── generators/             ← 데이터 생성 모듈
│   ├── base.py             ← 공통 생성 로직 (BaseGenerator)
│   ├── customers.py        ← 고객 + 주소
│   ├── products.py         ← 상품 + 카테고리 + 공급업체
│   ├── orders.py           ← 주문 + 주문상세
│   ├── payments.py         ← 결제
│   ├── shipping.py         ← 배송
│   ├── reviews.py          ← 리뷰
│   ├── inventory.py        ← 재고 입출고
│   ├── staff.py            ← 직원
│   ├── images.py           ← 상품 이미지 + Pexels 다운로드
│   ├── carts.py            ← 장바구니
│   ├── coupons.py          ← 쿠폰 + 사용 내역
│   ├── complaints.py       ← 문의/불만
│   ├── returns.py          ← 반품/교환
│   ├── calendar.py         ← 날짜 차원 테이블
│   ├── grade_history.py    ← 고객 등급 이력
│   ├── tags.py             ← 상품 태그
│   ├── views.py            ← 상품 조회 로그
│   ├── points.py           ← 포인트 거래
│   ├── promotions.py       ← 프로모션
│   ├── qna.py              ← 상품 Q&A
│   ├── wishlists.py        ← 위시리스트
│   └── dirty.py            ← 더티 데이터 노이즈 주입
├── exporters/              ← DB별 출력 모듈
│   ├── sqlite_exporter.py  ← SQLite DDL + 뷰 + 트리거
│   ├── mysql_exporter.py   ← MySQL DDL + 뷰 + SP
│   └── postgresql_exporter.py ← PostgreSQL DDL + MV + SP
└── utils/                  ← 유틸리티
    ├── fake_phone.py       ← 가상 전화번호 생성
    ├── growth.py           ← 성장 곡선 계산
    └── seasonality.py      ← 계절성 패턴
```

각 생성 모듈은 `BaseGenerator`를 상속하며, `config.yaml`의 설정과 시드를 받아 독립적으로 데이터를 생성합니다. 익스포터는 플러그인 구조로, 새 DB를 추가하려면 `exporters/` 디렉토리에 모듈 하나만 작성하면 됩니다.

---

## 출력 파일 구조

```
output/
├── ecommerce-ko.db                 # SQLite 데이터베이스 (기본)
├── mysql/
│   ├── schema.sql               # 테이블/인덱스/뷰 DDL
│   ├── data.sql                 # INSERT 문 (모든 데이터)
│   └── procedures.sql           # 저장 프로시저
└── postgresql/
    ├── schema.sql               # 테이블/인덱스/뷰 DDL
    ├── data.sql                 # INSERT 문 (모든 데이터)
    └── procedures.sql           # 함수/프로시저
```

---

## 데이터 검증

```bash
python verify.py                    # SQLite 검증
python verify.py --target mysql     # MySQL 검증
python verify.py --target postgresql  # PostgreSQL 검증
python verify.py --all              # 전체 검증
```

테이블 수, 뷰, 트리거, 행 수, FK 무결성을 자동으로 확인합니다. 상세 내용은 [05. 확인 및 첫 쿼리](05-verify.md#자동-검증-스크립트)를 참고하세요.

---

## 자주 묻는 질문

!!! question "medium 규모는 얼마나 걸리나요?"
    약 **3분** 소요됩니다 (SQLite 기준). MySQL/PostgreSQL SQL 파일 생성까지 포함하면 약 4~5분입니다.

!!! question "특정 테이블만 생성할 수 있나요?"
    테이블 간 FK 관계가 있어 부분 생성 시 무결성 문제가 발생합니다. 전체 생성 후 불필요한 테이블을 `DROP TABLE`로 제거하세요.

!!! question "기존 DB에 추가 데이터를 넣을 수 있나요?"
    증분 생성은 지원하지 않습니다. 다른 시드(`--seed`)나 날짜 범위로 새 DB를 생성한 뒤 `INSERT INTO ... SELECT FROM`으로 병합하세요.

!!! question "다른 업종(의류, 식품 등)으로 변경할 수 있나요?"
    `data/locale/ko.json`의 카테고리·상품·태그, `data/products.json`의 상품 마스터, `config.yaml`의 가격대·결제 비율을 수정하면 가능합니다.

!!! question "상품 이미지를 실제로 다운로드하려면?"
    [Pexels API](https://www.pexels.com/api/)에서 무료 키를 발급받은 후:
    ```bash
    python generate.py --download-images --pexels-key YOUR_API_KEY
    ```

[← 03. 데이터 생성](03-generate.md){ .md-button }
[05. 확인 및 첫 쿼리 →](05-verify.md){ .md-button .md-button--primary }
