# 용어사전

이 교재에서 사용하는 SQL 관련 용어를 가나다순으로 정리했습니다. 각 용어에는 관련 레슨 링크를 포함하고 있어 해당 개념을 더 깊이 학습할 수 있습니다.

---

## ㄱ

### 갱신 (UPDATE)
테이블에 이미 존재하는 행의 데이터를 수정하는 DML 문. 관련 레슨: [15강](../intermediate/15-dml.md)

### 격리 수준 (Isolation Level)
동시에 실행되는 트랜잭션들이 서로의 작업에 얼마나 영향을 받는지를 결정하는 단계. READ UNCOMMITTED부터 SERIALIZABLE까지 4단계가 있다. 관련 레슨: [17강](../intermediate/17-transactions.md)

### 결합 (JOIN)
두 개 이상의 테이블을 공통 컬럼을 기준으로 연결하여 하나의 결과 집합으로 만드는 연산. 관련 레슨: [8강](../intermediate/08-inner-join.md)

### 그룹화 (GROUP BY)
동일한 값을 가진 행들을 하나의 그룹으로 묶어 집계 함수를 적용할 수 있게 하는 절. 관련 레슨: [5강](../beginner/05-group-by.md)

### 기본 키 (Primary Key)
테이블에서 각 행을 고유하게 식별하는 컬럼 또는 컬럼 조합. NULL을 허용하지 않으며 중복될 수 없다. 관련 레슨: [16강](../intermediate/16-ddl.md)

---

## ㄴ

### 내부 조인 (INNER JOIN)
두 테이블에서 조인 조건을 만족하는 행만 결과에 포함하는 조인 방식. 일치하지 않는 행은 제외된다. 관련 레슨: [8강](../intermediate/08-inner-join.md)

### 널 (NULL)
값이 존재하지 않거나 알 수 없음을 나타내는 특수한 표시. 0이나 빈 문자열과는 다르며, IS NULL / IS NOT NULL로 비교한다. 관련 레슨: [6강](../beginner/06-null.md)

---

## ㄷ

### 데이터 정의어 (DDL, Data Definition Language)
테이블, 인덱스, 뷰 등 데이터베이스 구조를 생성(CREATE), 변경(ALTER), 삭제(DROP)하는 SQL 문의 분류. 관련 레슨: [16강](../intermediate/16-ddl.md)

### 데이터 조작어 (DML, Data Manipulation Language)
테이블의 데이터를 삽입(INSERT), 조회(SELECT), 수정(UPDATE), 삭제(DELETE)하는 SQL 문의 분류. 관련 레슨: [15강](../intermediate/15-dml.md)

### 데이터 제어어 (DCL, Data Control Language)
사용자 권한을 부여(GRANT)하거나 회수(REVOKE)하는 SQL 문의 분류. 관련 레슨: [부록 - 보안](dba-security.md)

### 동시성 (Concurrency)
여러 사용자 또는 프로세스가 동시에 데이터베이스에 접근하여 작업을 수행하는 상황. 트랜잭션과 잠금으로 데이터 무결성을 보장한다. 관련 레슨: [부록 - 동시성](dba-concurrency.md)

---

## ㄹ

### 롤백 (ROLLBACK)
트랜잭션 내에서 수행한 모든 변경을 취소하고 트랜잭션 시작 전 상태로 되돌리는 명령. 관련 레슨: [17강](../intermediate/17-transactions.md)

---

## ㅁ

### 매개변수 (Parameter)
저장 프로시저나 함수에 전달하는 입력값 또는 출력값. IN, OUT, INOUT 유형이 있다. 관련 레슨: [26강](../advanced/26-stored-procedures.md)

### 뷰 (View)
SELECT 문을 저장하여 가상의 테이블처럼 사용할 수 있게 만든 데이터베이스 객체. 데이터를 직접 저장하지 않는다. 관련 레슨: [22강](../advanced/22-views.md)

---

## ㅂ

### 별칭 (Alias)
테이블이나 컬럼에 임시로 부여하는 이름. AS 키워드를 사용하며 쿼리의 가독성을 높인다. 관련 레슨: [1강](../beginner/01-select.md)

### 복합 인덱스 (Composite Index)
두 개 이상의 컬럼을 조합하여 생성하는 인덱스. 컬럼 순서가 성능에 큰 영향을 미친다. 관련 레슨: [23강](../advanced/23-indexes.md)

### 부분 인덱스 (Partial Index)
WHERE 조건을 만족하는 행에 대해서만 생성되는 인덱스. 인덱스 크기를 줄이고 특정 쿼리의 성능을 높인다. 관련 레슨: [23강](../advanced/23-indexes.md)

---

## ㅅ

### 삭제 (DELETE)
테이블에서 조건에 맞는 행을 제거하는 DML 문. WHERE 절 없이 사용하면 모든 행이 삭제된다. 관련 레슨: [15강](../intermediate/15-dml.md)

### 삽입 (INSERT)
테이블에 새로운 행을 추가하는 DML 문. 관련 레슨: [15강](../intermediate/15-dml.md)

### 상관 서브쿼리 (Correlated Subquery)
외부 쿼리의 컬럼을 참조하여 외부 쿼리의 각 행마다 반복 실행되는 서브쿼리. 관련 레슨: [10강](../intermediate/10-subqueries.md)

### 색인 (Index)
→ 인덱스(Index) 참조. 관련 레슨: [23강](../advanced/23-indexes.md)

### 서브쿼리 (Subquery)
다른 SQL 문 안에 포함된 SELECT 문. WHERE, FROM, SELECT 절 등에서 사용할 수 있다. 관련 레슨: [10강](../intermediate/10-subqueries.md)

### 스키마 (Schema)
데이터베이스의 구조를 정의하는 설계도. 테이블, 컬럼, 자료형, 제약 조건, 관계 등의 전체 구조를 의미한다. 관련 레슨: [0강](../beginner/00-introduction.md)

### 시퀀스 (Sequence)
자동으로 증가하는 고유 번호를 생성하는 데이터베이스 객체. 주로 기본 키 값 생성에 사용된다. 관련 레슨: [16강](../intermediate/16-ddl.md)

---

## ㅇ

### 와일드카드 (Wildcard)
LIKE 연산자에서 패턴 매칭에 사용하는 특수 문자. `%`는 임의의 문자열, `_`는 임의의 한 글자를 의미한다. 관련 레슨: [2강](../beginner/02-where.md)

### 외래 키 (Foreign Key)
다른 테이블의 기본 키를 참조하는 컬럼. 테이블 간의 관계를 정의하고 참조 무결성을 보장한다. 관련 레슨: [16강](../intermediate/16-ddl.md)

### 외부 조인 (Outer JOIN)
조인 조건을 만족하지 않는 행도 결과에 포함하는 조인 방식. LEFT, RIGHT, FULL 세 가지가 있다. 관련 레슨: [9강](../intermediate/09-left-join.md)

### 윈도우 함수 (Window Function)
행 그룹에 대해 계산을 수행하되, 결과 행을 축소하지 않고 각 행에 계산 결과를 덧붙이는 함수. OVER 절과 함께 사용한다. 관련 레슨: [18강](../advanced/18-window.md)

### 인덱스 (Index)
테이블의 데이터를 빠르게 검색하기 위한 자료 구조. 책의 색인처럼 원하는 데이터의 위치를 빠르게 찾을 수 있게 한다. 관련 레슨: [23강](../advanced/23-indexes.md)

---

## ㅈ

### 저장 프로시저 (Stored Procedure)
데이터베이스에 저장되어 이름으로 호출할 수 있는 SQL 문의 묶음. 변수, 조건 분기, 반복 등의 로직을 포함할 수 있다. 관련 레슨: [26강](../advanced/26-stored-procedures.md)

### 정규화 (Normalization)
데이터 중복을 줄이고 무결성을 높이기 위해 테이블을 분리하는 설계 기법. 1NF부터 5NF까지 단계가 있다. 관련 레슨: [0강](../beginner/00-introduction.md)

### 정렬 (ORDER BY)
쿼리 결과를 지정한 컬럼 기준으로 오름차순(ASC) 또는 내림차순(DESC)으로 정렬하는 절. 관련 레슨: [3강](../beginner/03-sort-limit.md)

### 제약 조건 (Constraint)
테이블에 저장되는 데이터의 무결성을 보장하기 위한 규칙. PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, CHECK 등이 있다. 관련 레슨: [16강](../intermediate/16-ddl.md)

### 조인 (JOIN)
→ 결합(JOIN) 참조. 관련 레슨: [8강](../intermediate/08-inner-join.md)

### 조건 분기 (CASE)
SQL에서 조건에 따라 다른 값을 반환하는 표현식. 프로그래밍의 if-else와 유사하다. 관련 레슨: [7강](../beginner/07-case.md)

### 중복 제거 (DISTINCT)
SELECT 결과에서 중복된 행을 제거하여 고유한 값만 반환하는 키워드. 관련 레슨: [1강](../beginner/01-select.md)

### 집계 함수 (Aggregate Function)
여러 행의 값을 하나의 결과로 계산하는 함수. COUNT, SUM, AVG, MIN, MAX 등이 있다. 관련 레슨: [4강](../beginner/04-aggregates.md)

---

## ㅊ

### 차집합 (EXCEPT)
첫 번째 쿼리 결과에서 두 번째 쿼리 결과에 포함된 행을 제외하는 집합 연산자. 관련 레슨: [14강](../intermediate/14-union.md)

---

## ㅋ

### 커밋 (COMMIT)
트랜잭션 내에서 수행한 모든 변경을 확정하여 영구적으로 저장하는 명령. 관련 레슨: [17강](../intermediate/17-transactions.md)

### 커버링 인덱스 (Covering Index)
쿼리에 필요한 모든 컬럼을 포함하여 테이블 접근 없이 인덱스만으로 결과를 반환할 수 있는 인덱스. 관련 레슨: [23강](../advanced/23-indexes.md)

### 커서 (Cursor)
쿼리 결과 집합을 한 행씩 순차적으로 처리할 수 있게 하는 데이터베이스 객체. 관련 레슨: [26강](../advanced/26-stored-procedures.md)

### 쿼리 (Query)
데이터베이스에 정보를 요청하는 SQL 문. 좁은 의미로는 SELECT 문을 가리킨다. 관련 레슨: [1강](../beginner/01-select.md)

### 쿼리 실행 계획 (Query Execution Plan)
데이터베이스 엔진이 SQL 문을 실행하기 위해 선택한 전략을 보여주는 정보. EXPLAIN 명령으로 확인한다. 관련 레슨: [23강](../advanced/23-indexes.md)

---

## ㅌ

### 테이블 (Table)
행(row)과 열(column)로 구성된 데이터 저장 단위. 관계형 데이터베이스의 핵심 구조이다. 관련 레슨: [0강](../beginner/00-introduction.md)

### 트랜잭션 (Transaction)
하나의 논리적 작업 단위로 묶인 SQL 문의 집합. 전부 성공하거나 전부 실패하는 원자성을 보장한다. 관련 레슨: [17강](../intermediate/17-transactions.md)

### 트리거 (Trigger)
특정 테이블에 INSERT, UPDATE, DELETE가 발생할 때 자동으로 실행되는 저장 프로시저. 관련 레슨: [24강](../advanced/24-triggers.md)

---

## ㅍ

### 페이징 (Paging/Pagination)
대량의 결과를 일정 개수씩 나누어 조회하는 기법. LIMIT과 OFFSET을 조합하여 구현한다. 관련 레슨: [3강](../beginner/03-sort-limit.md)

### 필터링 (WHERE)
조건을 지정하여 원하는 행만 결과에 포함시키는 절. 비교 연산자, 논리 연산자, LIKE, IN, BETWEEN 등을 사용한다. 관련 레슨: [2강](../beginner/02-where.md)

---

## ㅎ

### 함수 (Function)
입력값을 받아 계산을 수행하고 결과를 반환하는 데이터베이스 객체. 내장 함수와 사용자 정의 함수로 나뉜다. 관련 레슨: [13강](../intermediate/13-utility-functions.md)

### 합집합 (UNION)
두 개 이상의 SELECT 결과를 하나로 합치는 집합 연산자. UNION은 중복을 제거하고 UNION ALL은 중복을 허용한다. 관련 레슨: [14강](../intermediate/14-union.md)

### HAVING
GROUP BY로 그룹화한 결과에 조건을 적용하는 절. WHERE가 개별 행을 필터링한다면 HAVING은 그룹을 필터링한다. 관련 레슨: [5강](../beginner/05-group-by.md)

### CTE (Common Table Expression)
WITH 절을 사용하여 이름을 붙인 임시 결과 집합. 쿼리의 가독성과 재사용성을 높인다. 재귀 CTE로 계층 구조도 표현할 수 있다. 관련 레슨: [19강](../advanced/19-cte.md)

### EXISTS
서브쿼리가 하나 이상의 행을 반환하면 TRUE를 반환하는 조건 연산자. 상관 서브쿼리와 함께 사용하여 존재 여부를 확인한다. 관련 레슨: [20강](../advanced/20-exists.md)

### JSON
JavaScript Object Notation. 최신 RDBMS에서 JSON 데이터를 저장하고 쿼리할 수 있는 기능을 제공한다. 관련 레슨: [25강](../advanced/25-json.md)

### SELF JOIN
같은 테이블을 자기 자신과 조인하는 기법. 동일 테이블 내의 행 간 관계를 표현할 때 사용한다. 관련 레슨: [21강](../advanced/21-self-cross-join.md)
