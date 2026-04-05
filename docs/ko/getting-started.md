# 시작하기

## 데이터베이스 열기

샘플 데이터베이스 `tutorial.db`는 SQLite 파일입니다. SQL 쿼리 도구에서 이 파일을 열면 바로 사용할 수 있습니다.

직접 데이터베이스를 생성하려면:

```bash
# Python 의존성 설치
pip install -r requirements.txt

# 생성 (한국어 데이터, 소규모)
python generate.py --size small --locale ko
```

데이터베이스 파일은 `output/tutorial.db` 경로에 생성됩니다.

## 스키마 살펴보기

쿼리를 작성하기 전에 데이터베이스에 어떤 내용이 있는지 파악해 봅시다.

### 전체 테이블 목록

```sql
SELECT name
FROM sqlite_master
WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
ORDER BY name;
```

### 테이블 구조 확인

```sql
-- customers 테이블의 컬럼 확인
PRAGMA table_info(customers);
```

### 각 테이블의 행 수 확인

```sql
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'payments', COUNT(*) FROM payments
ORDER BY row_count DESC;
```

## 기본 제공 뷰

데이터베이스에는 고급 SQL 패턴을 보여주는 뷰(View) 18개가 포함되어 있습니다. 일반 테이블처럼 조회할 수 있습니다:

```sql
-- 월별 매출 요약
SELECT * FROM v_monthly_sales ORDER BY month DESC LIMIT 12;

-- 고객 생애 가치(LTV) 요약
SELECT * FROM v_customer_summary WHERE total_orders > 10 ORDER BY total_spent DESC LIMIT 10;

-- 상품 ABC 분석 (파레토/80-20 법칙)
SELECT * FROM v_product_abc WHERE abc_class = 'A';
```

!!! info "뷰를 학습 자료로 활용하기"
    데이터베이스에 포함된 각 뷰는 특정 SQL 기법을 실제로 보여줍니다. 강의에서 개념을 배운 뒤 해당 뷰의 정의를 살펴보면 어떻게 구현됐는지 확인할 수 있습니다:

    ```sql
    -- 뷰의 정의 확인
    SELECT sql FROM sqlite_master WHERE type = 'view' AND name = 'v_monthly_sales';
    ```

## 이 튜토리얼의 표기 규칙

- `-- 이것은 주석입니다` — SQL 내 설명 표기
- 결과 테이블에서 **굵게** 표시된 컬럼명은 중요한 값을 나타냄
- 🔑 는 기본 키(Primary Key), 🔗 는 외래 키(Foreign Key)를 나타냄
- 각 강의 마지막에 연습 문제가 있음
- 정답은 접을 수 있는 섹션에 숨겨져 있으니 먼저 직접 풀어볼 것

준비됐나요? [강의 1: SELECT 기초](beginner/01-select.md)부터 시작하세요.
