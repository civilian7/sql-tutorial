# 전자상거래 테스트 데이터베이스 생성기

## 프로젝트 개요
데이터베이스 쿼리 앱 개발용 **현실감 있는 테스트 데이터베이스**를 생성하는 Python 프로젝트.
컴퓨터 및 주변기기를 판매하는 쇼핑몰(개업 10년차)의 데이터를 시뮬레이션한다.

## 핵심 원칙

### 현실감
- 10년간 자연스러운 성장 곡선 (고객, 매출, 상품 수 모두 연차별 증가)
- 계절성 반영 (연말/신학기 매출 증가, 여름 비수기 등)
- 비즈니스 로직 일관성 (주문일 > 가입일, 배송완료 > 주문일 등)
- NULL, 결측치, 이상치를 현실적 비율로 포함

### 개인정보 가상화
- 전화번호: `020-XXXX-XXXX` 형식 사용 (존재하지 않는 국번으로 오인 방지)
  - 영화/드라마의 미국 555번호와 같은 원리
- 이름: Faker(ko_KR) 사용
- 주소: Faker(ko_KR) 사용, 실제 행정구역 기반이되 상세주소는 가상
- 이메일: `{userid}@testmail.kr` 형식 (실존 도메인 회피)
- 사업자등록번호: 000-00-00000 형태의 가상 번호

### 지원 데이터베이스
1. **SQLite3** — 기본 출력, 파일 하나로 즉시 사용 가능
2. **MySQL/MariaDB** — DDL + INSERT SQL 파일
3. **PostgreSQL** — DDL + INSERT SQL 파일 (시퀀스, 타입 등 PG 네이티브)
4. **SQL Server** — DDL + INSERT SQL 파일 (T-SQL 문법)
5. **Oracle** — DDL + INSERT SQL 파일 (Oracle 문법)

각 DB용 DDL은 해당 DB 엔진의 네이티브 문법과 베스트 프랙티스를 따른다.
(예: MySQL의 AUTO_INCREMENT, PG의 SERIAL/GENERATED, Oracle의 SEQUENCE 등)

## 기술 스택
- Python 3.10+
- Faker (ko_KR 로케일)
- sqlite3 (표준 라이브러리)
- 설정: YAML 또는 JSON

## 프로젝트 구조
```
ecommerce-test-db/
├── CLAUDE.md                # 이 파일 (프로젝트 컨텍스트)
├── README.md                # 사용법 문서
├── config.yaml              # 데이터 생성 설정 (규모, 성장률 등)
├── requirements.txt         # Python 의존성
├── generate.py              # 메인 실행 스크립트
├── src/
│   ├── __init__.py
│   ├── schema.py            # 스키마 정의 (테이블, 컬럼, 관계)
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── base.py          # 공통 생성 로직
│   │   ├── customers.py     # 고객 데이터 생성
│   │   ├── products.py      # 상품/카테고리 데이터 생성
│   │   ├── orders.py        # 주문/주문상세 생성
│   │   ├── payments.py      # 결제 데이터 생성
│   │   ├── shipping.py      # 배송 데이터 생성
│   │   ├── reviews.py       # 리뷰 데이터 생성
│   │   ├── inventory.py     # 재고/입고 데이터 생성
│   │   └── staff.py         # 직원/관리자 데이터 생성
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── sqlite_exporter.py
│   │   ├── mysql_exporter.py
│   │   ├── postgresql_exporter.py
│   │   ├── sqlserver_exporter.py
│   │   └── oracle_exporter.py
│   └── utils/
│       ├── __init__.py
│       ├── fake_phone.py    # 020-XXXX-XXXX 전화번호 생성
│       ├── growth.py        # 성장 곡선 계산
│       └── seasonality.py   # 계절성 패턴
├── data/
│   ├── categories.json      # 상품 카테고리 마스터 (수동 큐레이션)
│   ├── products.json        # 상품 마스터 (브랜드, 모델명, 가격대)
│   └── suppliers.json       # 공급업체 마스터
└── output/                  # 생성된 DB/SQL 파일 출력 디렉토리
    ├── ecommerce.db         # SQLite DB
    ├── mysql/
    ├── postgresql/
    ├── sqlserver/
    └── oracle/
```

## 실행 방법
```bash
# 기본 실행 (SQLite만 생성)
python generate.py

# 전체 DB 포맷 생성
python generate.py --all

# 특정 DB만
python generate.py --target postgresql

# 데이터 규모 조절 (small/medium/large)
python generate.py --size medium

# 시드 고정 (재현 가능)
python generate.py --seed 42
```
