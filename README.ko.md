한국어 | **[English](README.md)**

# SQL 튜토리얼 — 전자상거래 데이터베이스 <small>v3.6</small>

[![Verify Tutorial](https://github.com/civilian7/sql-tutorial/actions/workflows/verify.yml/badge.svg)](https://github.com/civilian7/sql-tutorial/actions/workflows/verify.yml)

[**온라인 튜토리얼**](https://civilian7.github.io/sql-tutorial/) | [변경 이력](#변경-이력) | [GitHub](https://github.com/civilian7/sql-tutorial)

> 이 콘텐츠가 마음에 드셨다면 :star: 스타 하나 부탁드립니다!

컴퓨터 및 주변기기 쇼핑몰의 **현실적인 테스트 데이터베이스**를 생성하고, **SQL 튜토리얼** (27개 레슨, 910개 연습문제)을 제공하는 프로젝트입니다.

> **왜 이 프로젝트를?** 대부분의 SQL 교재는 문제만 있고 데이터가 없어서 쿼리를 실행해볼 수 없습니다. 이 프로젝트는 **75만 건의 현실적 데이터**와 완전한 튜토리얼 + 실행 가능한 연습문제를 제공합니다.

## 빠른 시작

```bash
pip install -r requirements.txt
python -m src.cli.generate --size small
# 출력: output/ecommerce-ko.db (~80MB, 75만 건)
```

`output/ecommerce-ko.db`를 SQL 도구에서 열고 학습을 시작하세요.

## 포함 내용

| 구성 | 상세 |
|------|------|
| **데이터베이스 생성기** | 30 테이블, 18 뷰, 5 트리거, 61 인덱스 |
| **튜토리얼** | 27개 레슨 (초급→중급→고급), 한국어/영어 |
| **연습문제** | 640개 (30세트) + 270개 레슨 복습 = 총 910문제 |
| **저장 프로시저** | 25개 프로시저 + 5개 함수 (MySQL & PostgreSQL) |
| **5개 DB** | SQLite (기본), MySQL, PostgreSQL, Oracle, SQL Server |
| **더티 데이터** | `--dirty-data` 데이터 정제 연습 |
| **시각화 도표** | 모든 레슨에 Mermaid 다이어그램 |
| **DB별 SQL** | SQLite / MySQL / PostgreSQL / Oracle / SQL Server 탭 |

## 명령행 옵션

```
python -m src.cli.generate [OPTIONS]

--size {small,medium,large}    데이터 규모 (기본: medium)
--locale {ko,en}               언어 (기본: ko)
--seed NUMBER                  랜덤 시드 (기본: 42)
--start-date YYYY-MM-DD        시작일 (기본: 2016-01-01)
--end-date YYYY-MM-DD          종료일 (기본: 2025-06-30)
--target {sqlite,mysql,postgresql,oracle,sqlserver}  대상 DB (기본: sqlite)
--all                          모든 DB 생성
--dirty-data                   5~10% 노이즈 추가
--apply                        대상 DB에 직접 적용
--host / --port / --user       DB 접속 정보
--password / --ask-password    DB 비밀번호
--database NAME                DB명 (기본: ecommerce_test)
--config PATH                  설정 파일 (기본: config.yaml)
```

## 데이터 규모

| 규모 | 행 수 | SQLite | 시간 | 용도 |
|------|------:|-------:|-----:|------|
| small | ~75만 | ~80 MB | ~20초 | 학습, CI |
| medium | ~700만 | ~800 MB | ~3분 | 개발 |
| large | ~3500만 | ~4 GB | ~15분 | 성능 테스트 |

## 튜토리얼

27개 레슨에 시각적 도표, DB별 SQL 탭 (최대 5개 DB), 복습 문제가 포함됩니다.

| 레벨 | 레슨 | 주제 |
|------|------|------|
| 초급 | 00–07 | DB 개요, SELECT, WHERE, ORDER BY, 집계, GROUP BY, NULL, CASE |
| 중급 | 08–17 | INNER/LEFT JOIN, 서브쿼리, 날짜/문자열, 숫자·변환, UNION, DML, DDL, 트랜잭션 |
| 고급 | 18–26 | 윈도우 함수, CTE, EXISTS, Self/Cross JOIN, 뷰, 인덱스, 트리거, JSON, 저장 프로시저 |

## 연습문제 (910문제 · 30세트 + 26레슨)

| 레벨 | 세트 수 | 문제 수 | 주요 주제 |
|:----:|:-------:|:-------:|----------|
| 초급 | 8 | 240 | SELECT, WHERE, 집계, GROUP BY, NULL, CASE, 종합, 디버깅 |
| 중급 | 11 | 220 | JOIN, 날짜, 문자열·숫자, 서브쿼리, 집합, DML, DDL, 트랜잭션, 종합, 디버깅, 데이터 품질 |
| 고급 | 11 | 180 | 윈도우 함수, CTE, EXISTS, DB 객체, JSON, 최적화, 매출 분석, 고객·운영, 실전 패턴, 면접, 챌린지 |

문제 유형: `SELECT`, `JOIN/UNION`, `Aggregate`, `String/Date`, `Subquery/CTE`, `Window`, `CASE/IF`, `Analytics`

연습문제는 YAML로 작성하고 mkdocs + exercise.db로 컴파일합니다:

```bash
python -m src.cli.compile_exercises    # YAML → exercise.db + mkdocs 마크다운
```

## 데이터베이스 (30 테이블)

### 핵심 커머스 (12)

| 테이블 | 행 수 | 설명 |
|--------|------:|------|
| `categories` | 53 | 계층형 카테고리 (자기참조) |
| `suppliers` | 60 | 공급업체 |
| `products` | 280 | 하드웨어/주변기기 (JSON 스펙, 후속모델) |
| `product_images` | 748 | 상품 이미지 |
| `product_prices` | 829 | 가격 이력 |
| `customers` | 5,230 | 고객 (등급, 유입경로) |
| `customer_addresses` | 8,554 | 배송지 |
| `staff` | 5 | 직원 (조직 계층) |
| `orders` | 34,908 | 주문 (9단계 상태) |
| `order_items` | 84,270 | 주문 상세 |
| `payments` | 34,908 | 결제 |
| `shipping` | 33,107 | 배송 |

### 고객 참여 (7)

| 테이블 | 행 수 | 설명 |
|--------|------:|------|
| `reviews` | 7,945 | 리뷰 |
| `wishlists` | 1,999 | 위시리스트 (M:N) |
| `carts` / `cart_items` | 3,000 / 9,037 | 장바구니 |
| `complaints` | 3,477 | CS 클레임 (에스컬레이션, 보상) |
| `returns` | 936 | 반품 (클레임 연결, 교환, 수수료) |
| `product_qna` | 946 | Q&A (자기참조 스레드) |

### 분석/리워드 (11)

| 테이블 | 행 수 | 설명 |
|--------|------:|------|
| `point_transactions` | 130,149 | 포인트 적립/사용/소멸 |
| `product_views` | 299,792 | 조회 로그 |
| `promotions` / `promotion_products` | 129 / 6,871 | 세일 이벤트 |
| `customer_grade_history` | 10,273 | 등급 이력 (SCD Type 2) |
| `calendar` | 3,469 | 날짜 차원 |
| `tags` / `product_tags` | 46 / 1,288 | 상품 태그 (M:N) |
| `inventory_transactions` | 14,331 | 재고 원장 |
| `coupons` / `coupon_usage` | 20 / 111 | 쿠폰 |

## 멀티 DB 지원

### 데이터 생성 (5개 DB)

```bash
# SQL 파일만 생성
python -m src.cli.generate --target mysql --size small
python -m src.cli.generate --target oracle --size small
python -m src.cli.generate --target sqlserver --size small

# 전체 DB 생성
python -m src.cli.generate --all --size small

# MySQL/PostgreSQL은 직접 적용 가능
pip install mysql-connector-python   # PG: psycopg2-binary
python -m src.cli.generate --target mysql --size small --apply --ask-password
```

각 DB에 포함: 네이티브 타입, 저장 프로시저/함수, 뷰, 인덱스, 트리거. DB별 특성:

| DB | DDL 특성 | SP/함수 |
|----|---------|---------|
| MySQL | ENUM, AUTO_INCREMENT, 파티셔닝 | 25 SP + 5 함수 |
| PostgreSQL | 커스텀 ENUM, JSONB, Materialized View | 25 SP + 5 함수 |
| Oracle | IDENTITY, NUMBER, VARCHAR2, CLOB, 파티셔닝 | 16 SP + 5 함수 (PL/SQL) |
| SQL Server | IDENTITY, NVARCHAR, BIT, 파티셔닝 | 14 SP (T-SQL) |

### 연습문제 SQL 탭 (5개 DB)

연습문제와 레슨 복습에서 DB별 문법이 다른 경우, 최대 5개 탭으로 정답을 제공합니다:

| DB | 데이터 생성 | 연습문제 탭 | 비고 |
|----|:----------:|:----------:|------|
| **SQLite** | :white_check_mark: | :white_check_mark: | 기본 DB, 파일 하나로 즉시 사용 |
| **MySQL** | :white_check_mark: | :white_check_mark: | DDL + INSERT SQL 파일, `--apply` 직접 적용 |
| **PostgreSQL** | :white_check_mark: | :white_check_mark: | DDL + INSERT SQL 파일, `--apply` 직접 적용 |
| **Oracle** | :white_check_mark: | :white_check_mark: | PL/SQL, IDENTITY, 파티셔닝, 18개 뷰 |
| **SQL Server** | :white_check_mark: | :white_check_mark: | T-SQL, NVARCHAR, 파티셔닝, 18개 뷰 |

Oracle과 SQL Server는 연습문제 YAML에 `oracle` / `sqlserver` 키로 SQL을 작성하면 자동으로 탭에 추가됩니다:

```yaml
reference_sql:
  sqlite: |
    SELECT * FROM orders LIMIT 10;
  oracle: |
    SELECT * FROM orders FETCH FIRST 10 ROWS ONLY;
  sqlserver: |
    SELECT TOP 10 * FROM orders;
```

## 설정

| 파일 | 용도 |
|------|------|
| `config.yaml` | 핵심 설정 (날짜, 규모, 성장, 비율) |
| `config_detailed.yaml` | 120+ 세부 파라미터 (기본값 내장) |

## 튜토리얼 보기 (MkDocs)

튜토리얼은 [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)로 빌드됩니다. 먼저 패키지를 설치하세요:

```bash
pip install -r requirements.txt    # mkdocs + mkdocs-material 포함
```

### 양 언어 (정적)

```bash
serve.bat
# http://localhost:8001/ko/  (한국어)
# http://localhost:8001/en/  (영어)
```

툴바의 **언어 전환** 버튼으로 한국어/영어를 전환할 수 있습니다. 파일 수정 후에는 `serve.bat`을 다시 실행하세요.

### 단일 언어 + 라이브 리로드

```bash
serve.bat ko     # 한국어 http://localhost:8001 (파일 수정 시 자동 반영)
serve.bat en     # 영어 http://localhost:8001
```

### 정적 빌드만

```bash
cd docs
mkdocs build -f mkdocs-ko.yml     # → output/docs/ko/
mkdocs build -f mkdocs-en.yml     # → output/docs/en/
```

### PDF 내보내기

```bash
pdf.bat          # 한국어 + 영어
pdf.bat ko       # 한국어만
pdf.bat en       # 영어만
```

출력: `output/docs/{ko,en}/pdf/sql-tutorial-{ko,en}.pdf`

첫 실행 시 Playwright + Chromium (~200MB)이 자동 설치됩니다. 헤드리스 브라우저로 렌더링하므로 탭, 머메이드 다이어그램, admonition이 모두 정상 출력됩니다.

## 프로젝트 구조

```
├── config.yaml              # 핵심 설정
├── config_detailed.yaml     # 상세 설정 (120+ 파라미터)
├── data/                    # 카테고리, 상품, 공급업체, 로케일
├── exercises/               # 연습문제 YAML (beginner/intermediate/advanced)
│   └── lectures/            # 26개 레슨 복습 문제 YAML
├── docs/                    # MkDocs 튜토리얼 (ko + en)
├── src/
│   ├── cli/                 # 메인 실행 스크립트 (generate, compile, sync 등)
│   ├── verify/              # 검증 스크립트 (SQL, 품질, 난이도, DML)
│   ├── tools/               # 유틸리티 (YAML 추출, 결과 업데이트)
│   ├── generators/          # 23개 데이터 생성기
│   ├── exporters/           # SQLite, MySQL, PostgreSQL, Oracle, SQL Server
│   └── utils/               # 전화번호, 성장곡선, 계절성
├── .github/workflows/       # CI (verify.yml)
├── serve.bat                # 로컬 튜토리얼 서버
├── pdf.bat                  # PDF 내보내기 (mkdocs-exporter + Chromium)
└── output/                  # 생성된 파일
```

## 라이선스

**듀얼 라이선스:**

- **코드** (생성기, 스크립트): [MIT 라이선스](LICENSE)
- **콘텐츠** (튜토리얼, 연습문제, 문서): [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

개인 학습 및 비상업적 교육 목적으로 자유롭게 사용할 수 있습니다. 상업적 사용: civilian7@gmail.com

## 기여자

| 기여자 | 기여 내용 |
|--------|----------|
| [@shinnyeonki](https://github.com/shinnyeonki) | PostgreSQL/MySQL 파티션 테이블 UNIQUE 제약조건 수정, products FK 위반 이슈 리포트 ([#1](https://github.com/civilian7/sql-tutorial/pull/1), [#2](https://github.com/civilian7/sql-tutorial/issues/2)) |

## 변경 이력

### v3.6.0 (2026-04-16)

**Docker 기반 DB 설치 가이드**: 02-database.md를 Docker Desktop 중심으로 재작성. Docker 개념 설명, Docker Desktop 설치, 기본 명령어, MySQL/PostgreSQL/SQL Server/Oracle 컨테이너 실행 가이드 포함. 기존 네이티브 설치 가이드는 "직접 설치" 탭으로 유지

**Oracle --apply 지원**: oracledb(thin mode) 기반 `--apply` 직접 적용. PL/SQL 블록 `/` 구분자 파서 추가. 대화형 모드에서도 Oracle 서버 적용 선택 가능

**대화형 모드 (Interactive Wizard)**: 옵션 없이 `python -m src.cli.generate` 실행 시 단계별 안내. 규모/언어/DB 선택/서버 적용/접속 정보를 대화형으로 입력

### v3.5.0 (2026-04-16)

**프로젝트 구조 개편**: 루트의 Python 파일을 `src/` 하위로 기능별 정리 (`src/cli/`, `src/verify/`, `src/tools/`). `python -m src.cli.generate` 방식으로 실행. 루트 래퍼 스크립트 삭제. CI 워크플로우 및 교재 전체 실행 명령 업데이트

**Oracle / SQL Server SQL 정답**: 30개 연습문제에 Oracle/SQL Server 정답 SQL 추가 (날짜 함수, EXPLAIN, 세션 분석, 코호트 등). 컴파일 후 60개 DB별 탭 생성

**SQL Server --apply 지원**: pyodbc 기반 `--apply` 직접 적용. GO 배치 구분자 파서 추가

**SQLite SQL 스크립트**: .db 파일과 함께 `output/sqlite/schema.sql` + `data.sql` 동시 생성

**버그 수정**: PostgreSQL `v_supplier_performance` 뷰 GROUP BY 누락, MySQL `_execute_sql_file` 주석+USE 처리 개선

### v3.4.0 (2026-04-15)

**Oracle / SQL Server 데이터 생성**: Oracle exporter (PL/SQL, IDENTITY, VARCHAR2, NUMBER, 파티셔닝, 18개 뷰, 16 SP + 5 함수)와 SQL Server exporter (T-SQL, NVARCHAR, BIT, 파티셔닝, 18개 뷰, 14 SP) 추가. `--target oracle`, `--target sqlserver`, `--all`로 5개 DB 동시 생성 가능

### v3.3.0 (2026-04-15)

**Oracle / SQL Server 연습문제 탭**: 연습문제에 Oracle, SQL Server용 SQL 탭 추가. exercise.db 스키마 확장 (`reference_sql_oracle`, `reference_sql_sqlserver`). DB별 SQL이 있으면 최대 5개 탭 (SQLite / MySQL / PostgreSQL / Oracle / SQL Server) 표시

### v3.2.0 (2026-04-14)

**레슨 복습 문제 YAML 통합**: 26개 강의에서 270개 복습 문제를 독립 YAML 파일로 추출. `compile_exercises.py`로 강의 MD 자동 삽입. 총 910문제 (연습 640 + 레슨 270)

### v3.0.0 (2026-04-12)

**튜토리얼 확장**: 22→27개 레슨 (0강 DB개요, CASE, 숫자·변환, UNION, Self/Cross JOIN, JSON, 저장프로시저 추가)

**연습문제 대폭 확대**: 208→640개 (30세트). 초급 8·중급 11·고급 11세트. 디버깅, 데이터 품질, 면접 대비, 챌린지 세트 신설

**문서 구조 개편**: 스키마·준비하기 분리, 페르소나 9명 학습 경로, 학습 일정 (2주/4주/8주), DB 선택 가이드

**영문 완전 번역**: 27개 레슨 + 30개 연습 세트 + 부록 전체 영문 버전 추가

**뷰·SP 강화**: MySQL/PG 뷰 18개, 저장 프로시저 25개 + 함수 5개, 트리거·뷰·SP 플로우차트

**빌드 자동화**: MkDocs 빌드 훅 (Mermaid CDN, 버전 자동 치환), CI 검증 (verify.py), PDF 내보내기

### v2.0.0 (2026-04-09)

**데이터베이스**: 21→30 테이블, RDBMS별 25 SP + 5 함수, JSON 스펙, 날짜 기반 범위

**데이터 현실감**: 상품 번들, 성별/연령 선호도, 포인트 리워드, 프로모션, 카테고리별 반품률, 인기도 감쇠, 공급업체 비활성화

**튜토리얼**: 22개 레슨 (Mermaid 도표, DB별 SQL 탭), 208개 레슨 내 복습 문제, 연습문제 컴파일러 (YAML → DB + mkdocs)

**기능**: `--start-date`/`--end-date`, `--dirty-data`, `--apply` (DB 직접 적용), `config_detailed.yaml` (120+ 파라미터), MySQL/PostgreSQL 내보내기, 한국어/영어 콘텐츠

### v1.0.0

최초 릴리스: 21 테이블, 18 뷰, 5 트리거, SQLite 전용, 201 연습문제
