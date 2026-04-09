# 시작하기

5분이면 데이터베이스를 만들고 첫 쿼리를 실행할 수 있습니다.

## 1. 사전 준비

### Python 설치

Python 3.10 이상이 필요합니다. 설치되어 있지 않다면:

=== "Windows"
    [python.org](https://www.python.org/downloads/)에서 다운로드하여 설치합니다.

    !!! warning "설치 시 주의"
        설치 화면에서 **"Add Python to PATH"** 체크박스를 반드시 선택하세요.

    설치 확인:
    ```
    python --version
    ```

=== "macOS"
    ```bash
    # Homebrew 사용
    brew install python@3.12

    # 또는 python.org에서 다운로드
    ```

=== "Linux (Ubuntu/Debian)"
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv
    ```

### 패키지 설치

```bash
pip install -r requirements.txt
```

설치되는 패키지:

| 패키지 | 용도 |
|--------|------|
| `Faker` | 가상 이름, 주소, 전화번호 등 생성 |
| `PyYAML` | 설정 파일(config.yaml) 파싱 |
| `mkdocs` | 튜토리얼 문서 빌드 (선택) |
| `mkdocs-material` | 문서 테마 (선택) |

!!! tip "가상환경 사용 권장"
    ```bash
    python -m venv .venv
    source .venv/bin/activate   # macOS/Linux
    .venv\Scripts\activate      # Windows
    pip install -r requirements.txt
    ```

## 2. 데이터베이스 생성

```bash
python generate.py --size small
```

`output/ecommerce.db` 파일이 생성됩니다 (약 80MB, 68만 건).

!!! info "다른 옵션"
    ```bash
    # 영어 데이터
    python generate.py --size small --locale en

    # 기간 지정
    python generate.py --size small --start-date 2020-01-01 --end-date 2025-06-30

    # MySQL/PostgreSQL용 SQL 파일도 생성
    python generate.py --size small --all
    ```
    전체 옵션은 [생성기 상세 가이드](generator-guide.md)를 참고하세요.

## 3. 데이터베이스 열기

생성된 `output/ecommerce.db`를 SQL 도구에서 엽니다.

- **ezQuery** — 파일 > DB 열기 > ecommerce.db 선택
- **DB Browser for SQLite** — 데이터베이스 열기
- **DBeaver** — 새 연결 > SQLite > 파일 선택
- **명령줄** — `sqlite3 output/ecommerce.db`

## 4. 첫 쿼리 실행

데이터베이스가 잘 만들어졌는지 확인합니다.

### 테이블 목록 확인

```sql
SELECT name FROM sqlite_master
WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
ORDER BY name;
```

30개 테이블이 표시되면 정상입니다.

### 데이터 맛보기

```sql
-- 고객 5명 조회
SELECT name, email, grade, point_balance
FROM customers
LIMIT 5;
```

```sql
-- 최근 주문 5건
SELECT order_number, customer_id, status, total_amount, ordered_at
FROM orders
ORDER BY ordered_at DESC
LIMIT 5;
```

```sql
-- 상품 카테고리
SELECT parent.name AS 대분류, child.name AS 소분류
FROM categories child
JOIN categories parent ON child.parent_id = parent.id
WHERE child.depth = 1
ORDER BY parent.sort_order, child.sort_order;
```

### 전체 데이터 규모 확인

```sql
SELECT
    (SELECT COUNT(*) FROM customers) AS 고객수,
    (SELECT COUNT(*) FROM products) AS 상품수,
    (SELECT COUNT(*) FROM orders) AS 주문수,
    (SELECT COUNT(*) FROM reviews) AS 리뷰수;
```

## 5. 튜토리얼 활용 가이드

### 추천 학습 순서

```
1단계: 초급 레슨 (01~06) → 초급 연습문제
2단계: 중급 레슨 (07~14, 21) → 중급 연습문제
3단계: 고급 레슨 (15~20) → 고급 연습문제
4단계: 도전 문제 → 실행 계획 분석
```

!!! tip "효과적인 학습법"
    - 레슨을 **순서대로** 따라하세요. 앞 레슨이 뒤 레슨의 기초가 됩니다.
    - 예제 쿼리를 **직접 타이핑**하세요. 복사-붙여넣기보다 손으로 익히는 게 효과적입니다.
    - 각 레슨 끝의 **복습 문제**를 반드시 풀어보세요.
    - 레슨을 마친 후 해당 레벨의 **연습 문제**에 도전하세요.
    - 쿼리를 **수정**해보세요. 조건을 바꾸거나, 컬럼을 추가하거나, 일부러 오류를 내보세요.

### 규모 선택 가이드

| 목적 | 추천 규모 | 이유 |
|------|-----------|------|
| SQL 문법 학습 | `--size small` | 빠른 생성(20초), 결과 확인 즉시 |
| 복잡한 쿼리 연습 | `--size small` | 충분한 데이터(68만건)로 현실적 결과 |
| 윈도우 함수/분석 | `--size small` 이상 | 시계열 데이터 필요 |
| 성능 최적화/EXPLAIN | `--size medium` | 대량 데이터(700만건)에서 차이 체감 |
| 인덱스 효과 비교 | `--size medium` 이상 | 데이터가 적으면 인덱스 효과가 안 보임 |

### 데이터 활용 팁

!!! info "이 데이터로 할 수 있는 것들"
    - **비즈니스 질문 만들기**: "VIP 고객 중 최근 3개월 미접속 고객은?" 같은 질문을 스스로 만들어보세요
    - **결과 예측하기**: 쿼리 실행 전에 결과를 예측하고, 실제 결과와 비교하세요
    - **다른 방법 시도**: 같은 결과를 서브쿼리, JOIN, CTE 등 다른 방식으로 작성해보세요
    - **EXPLAIN 활용**: 고급 단계에서는 모든 쿼리에 EXPLAIN을 붙여 실행 계획을 확인하세요

### 연습문제 난이도 안내

| 난이도 | 대상 | 문제 유형 |
|:------:|------|-----------|
| ⭐ | SQL 입문자 | 단일 테이블 SELECT, WHERE, ORDER BY |
| ⭐⭐ | 기초 학습 완료 | JOIN, GROUP BY, 기본 집계, 날짜/문자열 |
| ⭐⭐⭐ | 중급 학습 완료 | 서브쿼리, CTE, CASE, 복합 JOIN |
| ⭐⭐⭐⭐ | 실무 준비 | 윈도우 함수, 누적 합계, 리텐션, 이동 평균 |
| ⭐⭐⭐⭐⭐ | 면접/실전 | 연속 구간, 세션 분석, 중앙값, 파레토 |

### MySQL / PostgreSQL 사용자

SQLite로 기본 문법을 익힌 후, 같은 쿼리를 MySQL이나 PostgreSQL에서 실행해보세요.

```bash
# MySQL용 DB 생성
python generate.py --size small --target mysql --apply --ask-password

# PostgreSQL용 DB 생성
python generate.py --size small --target postgresql --apply --ask-password
```

레슨과 연습문제에서 DB별 문법이 다른 경우, **SQLite / MySQL / PostgreSQL 탭**으로 각각의 SQL을 확인할 수 있습니다.

### 더티 데이터로 실전 연습

실무에서는 데이터가 항상 깨끗하지 않습니다. `--dirty-data` 옵션으로 노이즈가 포함된 데이터를 생성하여 데이터 정제를 연습할 수 있습니다.

```bash
python generate.py --size small --dirty-data
```

포함되는 노이즈: 이름 앞뒤 공백, 이메일 대소문자 혼용, 전화번호 형식 불일치, 성별 표기 혼재 (`M`/`Male`/`m`) 등

[레슨 1: SELECT 기초 →](beginner/01-select.md){ .md-button .md-button--primary }

---

## 데이터베이스 구성 요약

| 구분 | 수 | 설명 |
|------|---:|------|
| 테이블 | 30 | 고객, 상품, 주문 등 전체 커머스 도메인 |
| 뷰 | 18 | 윈도우 함수, CTE, RFM 등 고급 SQL 패턴 |
| 트리거 | 5 | 자동 타임스탬프, 가격 이력, 포인트 검증 |
| 인덱스 | 61 | 주요 쿼리 패턴 최적화 |
| 저장 프로시저 | 25+5 | MySQL/PostgreSQL 전용 |

!!! tip "학습 팁"
    쿼리를 읽기만 하지 말고 **직접 타이핑**하세요. 쿼리를 수정해보고, 일부러 오류를 만들어보고, 고쳐보세요. 그게 진짜 학습입니다.

## 더 알아보기

- [데이터베이스 스키마](schema.md) — 30개 테이블 전체 컬럼 상세
- [생성기 상세 가이드](generator-guide.md) — 모든 CLI 옵션, 설정 파일, MySQL/PostgreSQL 사용법
- [DB 방언 비교](dialect-comparison.md) — SQLite, MySQL, PostgreSQL 문법 차이
