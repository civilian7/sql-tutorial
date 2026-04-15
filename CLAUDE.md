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
sql-tutorial/
├── config.yaml              # 핵심 설정 (날짜, 규모, 성장, 비율)
├── config_detailed.yaml     # 상세 설정 (120+ 파라미터)
├── requirements.txt         # Python 의존성
├── src/
│   ├── cli/                 # 메인 실행 스크립트
│   │   ├── generate.py      # 데이터베이스 생성기
│   │   ├── compile_exercises.py  # YAML 연습문제 → exercise.db + mkdocs
│   │   ├── check_integrity.py    # 데이터 무결성 검증
│   │   └── sync_sql.py      # 한국어↔영어 SQL 동기화
│   ├── verify/              # 튜토리얼 검증 스크립트
│   │   ├── verify.py        # 통합 검증 (SQL, 난이도, 품질)
│   │   ├── verify_sql.py    # SQL 구문 검증
│   │   ├── verify_quality.py     # 콘텐츠 품질 검증
│   │   ├── verify_difficulty.py  # 난이도 곡선 검증
│   │   └── verify_dml.py    # DML/DDL 정답 검증
│   ├── tools/               # 유틸리티 스크립트
│   │   ├── add_answer_results.py      # 정답 결과 추가
│   │   ├── extract_lesson_yaml.py     # 레슨 MD → YAML 추출
│   │   ├── update_exercise_results.py # 연습문제 결과 업데이트
│   │   └── update_results.py          # 결과 업데이트
│   ├── generators/          # 23개 데이터 생성기
│   ├── exporters/           # SQLite, MySQL, PostgreSQL, Oracle, SQL Server
│   └── utils/               # 전화번호, 성장곡선, 계절성
├── data/                    # 카테고리, 상품, 공급업체, 로케일
├── exercises/               # 연습문제 YAML (beginner/intermediate/advanced)
│   └── lectures/            # 26개 레슨 복습 문제 YAML
├── docs/                    # MkDocs 튜토리얼
│   ├── ko/                  # 한국어
│   ├── en/                  # 영어
│   ├── hooks/               # 빌드 훅 (mermaid, 버전 치환)
│   └── version.json         # 버전 정보
├── .github/workflows/       # CI (verify.yml)
├── serve.bat                # 로컬 튜토리얼 서버
├── pdf.bat                  # PDF 내보내기
└── output/                  # 생성된 DB/SQL 파일 출력 디렉토리
    ├── ecommerce-ko.db      # SQLite DB (한국어)
    ├── sqlite/              # SQLite SQL 스크립트
    ├── mysql/               # MySQL SQL 스크립트
    ├── postgresql/          # PostgreSQL SQL 스크립트
    ├── oracle/              # Oracle SQL 스크립트
    └── sqlserver/           # SQL Server SQL 스크립트
```

## 실행 방법
```bash
# 기본 실행 (SQLite만 생성)
python -m src.cli.generate

# 전체 DB 포맷 생성
python -m src.cli.generate --all

# 특정 DB만
python -m src.cli.generate --target postgresql

# 데이터 규모 조절 (small/medium/large)
python -m src.cli.generate --size medium

# 시드 고정 (재현 가능)
python -m src.cli.generate --seed 42
```
