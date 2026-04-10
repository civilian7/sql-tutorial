한국어 | **[English](README.md)**

# SQL 튜토리얼 — 전자상거래 데이터베이스 <small>v2.0</small>

[![Verify Tutorial](https://github.com/civilian7/sql-tutorial/actions/workflows/verify.yml/badge.svg)](https://github.com/civilian7/sql-tutorial/actions/workflows/verify.yml)

[**온라인 튜토리얼**](https://civilian7.github.io/sql-tutorial/) | [변경 이력](#변경-이력) | [GitHub](https://github.com/civilian7/sql-tutorial)

컴퓨터 및 주변기기 쇼핑몰의 **현실적인 테스트 데이터베이스**를 생성하고, **SQL 튜토리얼** (22개 레슨, 208개 연습문제)을 제공하는 프로젝트입니다.

> **왜 이 프로젝트를?** 대부분의 SQL 교재는 문제만 있고 데이터가 없어서 쿼리를 실행해볼 수 없습니다. 이 프로젝트는 **69만 건의 현실적 데이터**와 완전한 튜토리얼 + 실행 가능한 연습문제를 제공합니다.

## 빠른 시작

```bash
pip install -r requirements.txt
python generate.py --size small
# 출력: output/ecommerce.db (~80MB, 69만 건)
```

`output/ecommerce.db`를 SQL 도구에서 열고 학습을 시작하세요.

## 포함 내용

| 구성 | 상세 |
|------|------|
| **데이터베이스 생성기** | 30 테이블, 18 뷰, 5 트리거, 61 인덱스 |
| **튜토리얼** | 22개 레슨 (초급→중급→고급), 한국어/영어 |
| **연습문제** | 208개 레슨 내 복습 문제 + 별도 연습 세트, 정답 포함 |
| **저장 프로시저** | 25개 프로시저 + 5개 함수 (MySQL & PostgreSQL) |
| **3개 DB** | SQLite (기본), MySQL, PostgreSQL |
| **더티 데이터** | `--dirty-data` 데이터 정제 연습 |
| **시각화 도표** | 모든 레슨에 Mermaid 다이어그램 |
| **DB별 SQL** | SQLite / MySQL / PostgreSQL 탭 |

## 명령행 옵션

```
python generate.py [OPTIONS]

--size {small,medium,large}    데이터 규모 (기본: medium)
--locale {ko,en}               언어 (기본: ko)
--seed NUMBER                  랜덤 시드 (기본: 42)
--start-date YYYY-MM-DD        시작일 (기본: 2016-01-01)
--end-date YYYY-MM-DD          종료일 (기본: 2025-06-30)
--target {sqlite,mysql,postgresql}  대상 DB (기본: sqlite)
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
| small | ~69만 | ~80 MB | ~20초 | 학습, CI |
| medium | ~700만 | ~800 MB | ~3분 | 개발 |
| large | ~3500만 | ~4 GB | ~15분 | 성능 테스트 |

## 튜토리얼

22개 레슨에 시각적 도표, DB별 SQL 탭, 복습 문제가 포함됩니다.

| 레벨 | 레슨 | 주제 |
|------|------|------|
| 초급 | 01–06 | SELECT, WHERE, ORDER BY, 집계, GROUP BY, NULL |
| 중급 | 07–16 | JOIN, 서브쿼리, CASE, 날짜/문자열, DML, DDL, Self/Cross JOIN |
| 고급 | 17–22 | 윈도우 함수, CTE, EXISTS, 뷰, 인덱스, 트리거 |

## 연습문제 (208문제)

| 난이도 | 문제 수 | 예시 |
|:------:|:-------:|------|
| ⭐ | 38 | 단일 테이블 SELECT, WHERE |
| ⭐⭐ | 92 | JOIN, GROUP BY, 날짜, 문자열 |
| ⭐⭐⭐ | 78 | 서브쿼리, CTE, CASE, 복합 JOIN |
| ⭐⭐⭐⭐ | 47 | 윈도우 함수, 리텐션, 이동 평균 |
| ⭐⭐⭐⭐⭐ | 15 | 연속 구간, 세션 분석, 중앙값, 파레토 |

문제 유형: `SELECT`, `JOIN/UNION`, `Aggregate`, `String/Date`, `Subquery/CTE`, `Window`, `CASE/IF`, `Analytics`

연습문제는 YAML로 작성하고 mkdocs + exercise.db로 컴파일합니다:

```bash
python compile_exercises.py    # YAML → exercise.db + mkdocs 마크다운
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

## MySQL / PostgreSQL

```bash
# SQL 파일만 생성
python generate.py --target mysql --size small

# DB에 직접 적용
pip install mysql-connector-python   # PG: psycopg2-binary
python generate.py --target mysql --size small --apply --ask-password
```

각 DB에 포함: 적절한 타입 (DECIMAL, TIMESTAMP, BOOLEAN, ENUM), 25 SP + 5 함수, 테이블 파티셔닝, GRANT 예시. PostgreSQL은 추가로 JSONB, 커스텀 ENUM, Materialized View 포함.

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
├── generate.py              # 데이터베이스 생성기
├── compile_exercises.py     # YAML 연습문제 → exercise.db + mkdocs
├── check_integrity.py       # 데이터 무결성 검증
├── config.yaml              # 핵심 설정
├── config_detailed.yaml     # 상세 설정 (120+ 파라미터)
├── data/                    # 카테고리, 상품, 공급업체, 로케일
├── exercises/               # 연습문제 YAML (beginner/intermediate/advanced)
├── docs/                    # MkDocs 튜토리얼 (ko + en)
├── src/
│   ├── generators/          # 18개 데이터 생성기
│   └── exporters/           # SQLite, MySQL, PostgreSQL 내보내기
├── serve.bat                # 로컬 튜토리얼 서버
├── pdf.bat                  # PDF 내보내기 (mkdocs-exporter + Chromium)
└── output/                  # 생성된 파일
```

## 라이선스

**듀얼 라이선스:**

- **코드** (생성기, 스크립트): [MIT 라이선스](LICENSE)
- **콘텐츠** (튜토리얼, 연습문제, 문서): [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

개인 학습 및 비상업적 교육 목적으로 자유롭게 사용할 수 있습니다. 상업적 사용: civilian7@gmail.com

## 변경 이력

### v2.0.0 (2026-04-09)

**데이터베이스**: 21→30 테이블, RDBMS별 25 SP + 5 함수, JSON 스펙, 날짜 기반 범위

**데이터 현실감**: 상품 번들, 성별/연령 선호도, 포인트 리워드, 프로모션, 카테고리별 반품률, 인기도 감쇠, 공급업체 비활성화

**튜토리얼**: 22개 레슨 (Mermaid 도표, DB별 SQL 탭), 208개 레슨 내 복습 문제, 연습문제 컴파일러 (YAML → DB + mkdocs)

**기능**: `--start-date`/`--end-date`, `--dirty-data`, `--apply` (DB 직접 적용), `config_detailed.yaml` (120+ 파라미터), MySQL/PostgreSQL 내보내기, 한국어/영어 콘텐츠

### v1.0.0

최초 릴리스: 21 테이블, 18 뷰, 5 트리거, SQLite 전용, 201 연습문제
