# 시작하기

5분이면 데이터베이스를 만들고 첫 쿼리를 실행할 수 있습니다.

## 1. Python 설치

Python 3.10 이상이 필요합니다.

=== "Windows"
    [python.org](https://www.python.org/downloads/)에서 다운로드하여 설치합니다.
    설치 화면에서 **"Add Python to PATH"** 체크박스를 반드시 선택하세요.

    ```
    python --version
    ```

=== "macOS"
    ```bash
    brew install python@3.12
    ```

=== "Linux (Ubuntu/Debian)"
    ```bash
    sudo apt update && sudo apt install python3 python3-pip python3-venv
    ```

## 2. 데이터베이스 생성

```bash
pip install -r requirements.txt
python generate.py --size small
```

`output/ecommerce.db` 파일이 생성됩니다 (약 80MB, 68만 건).

??? info "가상환경 사용 (권장)"
    ```bash
    python -m venv .venv
    source .venv/bin/activate   # macOS/Linux
    .venv\Scripts\activate      # Windows
    pip install -r requirements.txt
    python generate.py --size small
    ```

??? info "생성 옵션"
    ```bash
    python generate.py --size small --locale en           # 영어 데이터
    python generate.py --size small --all                  # MySQL/PG용 SQL도 생성
    python generate.py --size small --dirty-data           # 노이즈 포함 데이터
    python generate.py --size medium                       # 대용량 (700만건)
    ```
    전체 옵션은 [생성기 상세 가이드](generator-guide.md)를 참고하세요.

## 3. SQL 도구에서 열기

생성된 `output/ecommerce.db`를 아무 SQL 도구에서 열면 됩니다.

| 도구 | 방법 |
|------|------|
| ezQuery (개발중) | 파일 > DB 열기 > ecommerce.db |
| DB Browser for SQLite | 데이터베이스 열기 |
| DBeaver | 새 연결 > SQLite > 파일 선택 |
| 명령줄 | `sqlite3 output/ecommerce.db` |

## 4. 첫 쿼리 실행

데이터베이스가 잘 만들어졌는지 확인합니다.

```sql
-- 테이블 목록 (30개면 정상)
SELECT name FROM sqlite_master
WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
ORDER BY name;
```

```sql
-- 고객 5명 조회
SELECT name, email, grade, point_balance
FROM customers
LIMIT 5;
```

```sql
-- 전체 데이터 규모
SELECT
    (SELECT COUNT(*) FROM customers) AS 고객수,
    (SELECT COUNT(*) FROM products) AS 상품수,
    (SELECT COUNT(*) FROM orders) AS 주문수,
    (SELECT COUNT(*) FROM reviews) AS 리뷰수;
```

결과가 정상적으로 나온다면 준비 완료입니다.

[1강: SELECT 기초 시작하기 →](beginner/01-select.md){ .md-button .md-button--primary }

## 학습 가이드

### 추천 순서

| 단계 | 레슨 | 설명 |
|------|------|------|
| 1단계 | 초급 01~06 | SELECT, WHERE, 정렬, 집계, GROUP BY, NULL |
| 2단계 | 중급 07~16 | JOIN, 서브쿼리, CASE, 날짜/문자열, DML, DDL, SELF/CROSS JOIN |
| 3단계 | 고급 17~22 | 윈도우 함수, CTE, EXISTS, 뷰, 인덱스, 트리거 |

레슨은 **순서대로** 따라하세요. 앞 레슨이 뒤 레슨의 기초가 됩니다.

### 효과적인 학습법

- 예제 쿼리를 **직접 타이핑**하세요. 복사-붙여넣기보다 손으로 익히는 게 효과적입니다.
- 각 레슨 끝의 **복습 문제**를 반드시 풀어보세요.
- 쿼리를 **수정**해보세요 — 조건을 바꾸거나, 칼럼을 추가하거나, 일부러 오류를 내보세요.
- 같은 결과를 **다른 방식**(서브쿼리, JOIN, CTE)으로 작성해보세요.

### 데이터 규모 선택

| 목적 | 규모 | 데이터 건수 |
|------|------|------------:|
| SQL 문법 학습 | `--size small` | 68만 건 |
| 성능 최적화 / EXPLAIN | `--size medium` | 700만 건 |

대부분의 학습에는 `small`로 충분합니다. 인덱스 효과나 실행 계획을 체감하려면 `medium`을 사용하세요.

### MySQL / PostgreSQL 사용

SQLite로 기본 문법을 익힌 후, 같은 쿼리를 다른 DB에서도 실행해보세요.

```bash
python generate.py --size small --target mysql --apply --ask-password
python generate.py --size small --target postgresql --apply --ask-password
```

레슨과 연습 문제에서 DB별 문법이 다른 경우, **SQLite / MySQL / PostgreSQL 탭**으로 각각의 SQL을 확인할 수 있습니다.

---

## 데이터베이스 구성

| 구분 | 수 | 설명 |
|------|---:|------|
| 테이블 | 30 | 고객, 상품, 주문, 결제, 배송, 리뷰, 포인트, 프로모션, Q&A |
| 뷰 | 18 | 윈도우 함수, CTE, RFM 분석 등 고급 SQL 패턴 |
| 트리거 | 5 | 자동 타임스탬프, 가격 이력, 포인트 검증 |
| 인덱스 | 61 | 주요 쿼리 패턴 최적화 |
| 저장 프로시저 | 25+5 | MySQL/PostgreSQL 전용 |

## 더 알아보기

- [데이터베이스 스키마](schema.md) — 30개 테이블 전체 칼럼 상세
- [생성기 상세 가이드](generator-guide.md) — 모든 CLI 옵션, 설정 파일
- [DB 방언 비교](dialect-comparison.md) — SQLite, MySQL, PostgreSQL 문법 차이
