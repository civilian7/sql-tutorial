# 연습 문제

각 레슨의 복습 문제를 넘어, 여러 개념을 종합하는 실전 연습 문제입니다. 총 **640문제**를 난이도별로 제공합니다.

> 모든 문제는 TechShop 샘플 데이터베이스(`ecommerce-ko.db`)로 검증할 수 있습니다. 각 문제에 접힌 **힌트**와 **정답**이 포함되어 있으니, 먼저 직접 풀어본 뒤 확인하세요.

## 초급 (240문제)

레슨 00~07에서 배운 개념으로 풀 수 있습니다. JOIN, 서브쿼리 없이 단일 테이블만 사용합니다.

| # | 주제 | 문제 수 | 핵심 개념 |
|--:|------|:-------:|-----------|
| 1 | [상품 탐색](beginner-01-products.md) | 30 | SELECT, WHERE, LIKE, BETWEEN, IN |
| 2 | [정렬과 페이징](beginner-02-sort-paging.md) | 30 | ORDER BY, LIMIT, OFFSET, DISTINCT |
| 3 | [집계 함수](beginner-03-aggregates.md) | 30 | COUNT, SUM, AVG, MIN, MAX, ROUND |
| 4 | [그룹화와 필터](beginner-04-group-by.md) | 30 | GROUP BY, HAVING |
| 5 | [NULL 처리](beginner-05-null.md) | 30 | IS NULL, COALESCE, NULL과 집계 |
| 6 | [CASE 표현식](beginner-06-case.md) | 30 | CASE WHEN, 분류, 조건부 집계 |
| 7 | [종합 문제](beginner-07-comprehensive.md) | 30 | 초급 전 개념 조합 |
| 8 | [SQL 오류 찾기](beginner-08-debugging.md) | 30 | 구문/논리/결과 오류 진단 |

## 중급 (220문제)

레슨 08~17에서 배운 개념을 사용합니다. JOIN, 서브쿼리, 함수, DML/DDL을 포함합니다.

| # | 주제 | 문제 수 | 핵심 개념 |
|--:|------|:-------:|-----------|
| 1 | [JOIN 마스터](intermediate-01-joins.md) | 25 | INNER/LEFT JOIN, 안티 조인, 다중 테이블 |
| 2 | [날짜/시간 분석](intermediate-02-dates.md) | 20 | SUBSTR, julianday, strftime, calendar |
| 3 | [문자열/숫자 함수](intermediate-03-string-math.md) | 20 | LENGTH, REPLACE, GROUP_CONCAT, ROUND, CAST |
| 4 | [서브쿼리](intermediate-04-subqueries.md) | 20 | WHERE/FROM/SELECT/상관 서브쿼리 |
| 5 | [집합 연산](intermediate-05-set-operations.md) | 15 | UNION, INTERSECT, EXCEPT |
| 6 | [DML 실습](intermediate-06-dml.md) | 20 | INSERT, UPDATE, DELETE, UPSERT |
| 7 | [DDL/제약조건](intermediate-07-ddl.md) | 15 | CREATE/ALTER/DROP TABLE, PK, FK, CHECK |
| 8 | [트랜잭션](intermediate-08-transactions.md) | 15 | BEGIN, COMMIT, ROLLBACK, SAVEPOINT |
| 9 | [종합 문제](intermediate-09-comprehensive.md) | 25 | 중급 전 개념 조합 |
| 10 | [SQL 디버깅](intermediate-10-debugging.md) | 25 | JOIN/서브쿼리/날짜 오류 진단 |
| 11 | [데이터 품질](intermediate-11-data-quality.md) | 20 | NULL, 중복, FK 정합성, 이상치 |

## 고급 (180문제)

레슨 18~26에서 배운 개념을 사용합니다. 윈도우 함수, CTE, DB 객체, 비즈니스 분석을 포함합니다.

| # | 주제 | 문제 수 | 핵심 개념 |
|--:|------|:-------:|-----------|
| 1 | [윈도우 함수 실전](advanced-01-window-functions.md) | 15 | ROW_NUMBER, RANK, LAG, NTILE, SUM OVER |
| 2 | [CTE 활용](advanced-02-cte.md) | 15 | WITH, 재귀 CTE, 다중 CTE 체이닝 |
| 3 | [EXISTS와 안티 패턴](advanced-03-exists-antipattern.md) | 15 | EXISTS, NOT EXISTS, 전칭 부정 |
| 4 | [DB 객체 설계](advanced-04-db-objects.md) | 20 | 뷰, 트리거, 저장 프로시저 |
| 5 | [JSON 활용](advanced-05-json.md) | 10 | json_extract, json_set, JSON 집계 |
| 6 | [인덱스와 최적화](advanced-06-optimization.md) | 15 | EXPLAIN, 커버링/부분 인덱스, 쿼리 리라이트 |
| 7 | [매출 분석](advanced-07-sales-analysis.md) | 20 | YoY, ABC, 프로모션, 바스켓 분석 |
| 8 | [고객/운영 분석](advanced-08-customer-ops.md) | 20 | RFM, 코호트, 재고, CS 성과 |
| 9 | [실무 SQL 패턴](advanced-09-patterns.md) | 15 | Top-N, 세션, 퍼널, 피벗, 파레토 |
| 10 | [면접 대비](advanced-10-interview.md) | 20 | FAANG/한국 IT 빈출 패턴 |
| 11 | [도전 문제](advanced-11-challenge.md) | 15 | 미니 프로젝트, 종합 설계 |
