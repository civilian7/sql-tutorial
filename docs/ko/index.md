# SQL 튜토리얼 <small>v2.0</small>

현실적인 **전자상거래 데이터베이스**로 SQL을 배우는 실습형 튜토리얼입니다.

컴퓨터 및 주변기기를 판매하는 가상의 온라인 쇼핑몰 **테크샵(TechShop)**의 10년간 비즈니스 데이터를 직접 쿼리하며, 기초부터 고급까지 체계적으로 학습합니다.

!!! tip "기존 교재와의 차이"
    대부분의 SQL 교재는 문제만 있고 데이터가 없어서, 쿼리를 작성해도 실행해볼 수 없습니다.
    이 튜토리얼은 **68만 건의 현실적 데이터**를 제공하여, 모든 쿼리를 직접 실행하고 결과를 확인할 수 있습니다.

## 학습 과정

| 단계 | 주제 | 레슨 | 연습 |
|------|------|:----:|:----:|
| **초급** | SELECT, WHERE, ORDER BY, 집계, GROUP BY, NULL | 6개 | 60문제 |
| **중급** | JOIN, 서브쿼리, CASE, 날짜/문자열, DML, Self/Cross JOIN | 9개 | 89문제 |
| **고급** | 윈도우 함수, CTE, EXISTS, 뷰, 인덱스, 트리거 | 6개 | 74문제 |
| | | **21개 레슨** | **223문제** |

## 주요 특징

- **30개 테이블** — 고객, 상품, 주문, 결제, 배송, 리뷰, 포인트, 프로모션, Q&A 등
- **18개 뷰** — 윈도우 함수, CTE, RFM 분석 등 고급 SQL 패턴 시연
- **10년간 현실적 데이터** — 성장 곡선, 계절성, 고객 행동 패턴 반영
- **3개 DB 지원** — SQLite(기본), MySQL, PostgreSQL
- **한국어/영어** — 데이터와 문서 모두 다국어 지원
- **223개 연습문제** — 초급~고급, DB별 SQL 탭으로 비교 학습 가능

## 시작하기

```bash
pip install -r requirements.txt
python generate.py --size small
```

생성된 `output/ecommerce.db`를 SQL 도구에서 열고, [시작하기](getting-started.md)를 따라하세요.

[시작하기 →](getting-started.md){ .md-button .md-button--primary }
[스키마 참조 →](schema.md){ .md-button }
