# 03. 데이터 생성

데이터 생성기는 Python으로 작성되어 있습니다. Python을 설치하고, 생성기를 실행하면 학습용 데이터베이스가 만들어집니다.

## Python 설치

Python **3.10 이상**이 필요하며, 추천 버전은 **Python 3.14**입니다 (이 튜토리얼의 개발 및 테스트에 사용된 버전).

**이미 설치되어 있는지 확인:**

=== "Windows"

    명령 프롬프트에서:
    ```
    python --version
    ```

=== "macOS / Linux"

    터미널에서:
    ```bash
    python3 --version
    ```

`Python 3.10.x` 이상이 출력되면 [의존성 설치](#의존성-설치)로 건너뛰세요.

---

### Python 설치 방법

=== "Windows"

    #### 1. 다운로드

    [python.org/downloads](https://www.python.org/downloads/)에서 **Download Python 3.x.x** 버튼을 클릭합니다. 64비트 Windows용이 자동으로 선택됩니다.

    #### 2. 설치

    !!! warning "가장 중요한 단계"
        설치 첫 화면 하단의 **"Add python.exe to PATH"** 체크박스를 **반드시** 선택하세요. 이걸 놓치면 터미널에서 `python` 명령이 작동하지 않습니다.

    **Install Now**를 클릭하면 설치가 진행됩니다. 완료 화면에서 **"Disable path length limit"**이 나타나면 클릭하세요 (긴 경로 문제 방지).

    #### 3. 설치 확인

    **명령 프롬프트**를 엽니다:

    !!! info "명령 프롬프트 여는 법"
        - 시작 메뉴에서 `cmd` 검색, 또는
        - ++win+r++ → `cmd` 입력 → ++enter++

    ```
    python --version
    ```

    `Python 3.12.x` 등이 출력되면 정상입니다.

    !!! warning "`python`을 찾을 수 없다면"
        - 설치 시 "Add to PATH"를 놓쳤을 수 있습니다. Python을 **제거 후 다시 설치**하면서 체크박스를 선택하세요.
        - 또는 `py --version`을 시도하세요. Windows Python Launcher가 설치되어 있으면 `py` 명령으로도 실행 가능합니다. 이 경우 이후 명령에서 `python` 대신 `py`를 사용하세요.

=== "macOS"

    #### 1. Homebrew 확인

    ```bash
    brew --version
    ```

    없으면 먼저 설치합니다:
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

    #### 2. Python 설치

    ```bash
    brew install python@3.12
    ```

    #### 3. 설치 확인

    ```bash
    python3 --version
    ```

    !!! info "`python3`를 사용하세요"
        macOS에서는 `python`이 아니라 `python3`입니다. 이후 명령에서도 `python` 대신 `python3`, `pip` 대신 `pip3`을 사용하세요.

=== "Linux (Ubuntu/Debian)"

    #### 1. 설치

    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv
    ```

    #### 2. 설치 확인

    ```bash
    python3 --version
    ```

    !!! info "`python3`를 사용하세요"
        Linux에서도 `python`이 아니라 `python3`입니다.

---

## 커맨드라인 기초 { #cli-basics }

이 단계부터는 **터미널**(또는 명령 프롬프트)에서 명령어를 입력합니다. 익숙하지 않아도 아래 명령어를 **그대로 복사해서 붙여넣으면** 됩니다.

| 명령어 | 의미 | 예시 |
|--------|------|------|
| `cd 폴더명` | 해당 폴더로 이동 | `cd sql-tutorial` |
| `ls` (macOS/Linux) / `dir` (Windows) | 현재 폴더의 파일 목록 | |
| ++enter++ | 명령어 실행 | |

**붙여넣기 방법:**

- Windows 명령 프롬프트: 마우스 **우클릭**
- macOS 터미널: ++cmd+v++
- Linux 터미널: ++ctrl+shift+v++

---

## 의존성 설치 { #의존성-설치 }

프로젝트 폴더로 이동한 뒤, 필요한 라이브러리를 설치합니다:

```bash
cd sql-tutorial
pip install -r requirements.txt
```

!!! tip "macOS/Linux에서는 `pip3`"
    `pip: command not found`가 나오면 `pip3`으로 대체하세요:
    ```bash
    pip3 install -r requirements.txt
    ```

!!! info "가상환경(venv)이란?"
    가상환경은 프로젝트별로 독립된 Python 패키지 공간을 만드는 기능입니다. 시스템 Python에 영향을 주지 않으므로 안전합니다. `Permission denied` 오류가 나거나, 시스템 패키지와 충돌을 피하고 싶을 때 사용합니다.

    ```bash
    python -m venv .venv

    # Windows
    .venv\Scripts\activate

    # macOS / Linux
    source .venv/bin/activate

    # 활성화된 상태에서 설치
    pip install -r requirements.txt
    ```

    가상환경이 활성화되면 프롬프트 앞에 `(.venv)`가 표시됩니다.

---

## 데이터 생성

=== "SQLite (기본)"

    ```bash
    python generate.py --size small
    ```

    `output/ecommerce-ko.db` 파일이 생성됩니다 (약 80MB, 68만 건). 약 20초 소요됩니다.

=== "MySQL"

    ```bash
    python generate.py --size small --target mysql
    ```

    `output/mysql/` 디렉토리에 `schema.sql`, `data.sql`, `procedures.sql`이 생성됩니다.

    서버에 바로 적용하려면:

    ```bash
    python generate.py --size small --target mysql --apply --ask-password
    ```

    02단계에서 설정한 root 비밀번호를 입력합니다.

=== "PostgreSQL"

    ```bash
    python generate.py --size small --target postgresql
    ```

    `output/postgresql/` 디렉토리에 `schema.sql`, `data.sql`, `procedures.sql`이 생성됩니다.

    서버에 바로 적용하려면:

    ```bash
    python generate.py --size small --target postgresql --apply --ask-password
    ```

    02단계에서 설정한 postgres 비밀번호를 입력합니다.

=== "전체 (한번에)"

    ```bash
    python generate.py --size small --all
    ```

    SQLite DB + MySQL SQL + PostgreSQL SQL을 한번에 생성합니다.

!!! info "macOS/Linux에서는 `python3`"
    `python: command not found`가 나오면 `python3 generate.py --size small`로 실행하세요.

### 생성 확인

정상적으로 완료되면 다음과 같은 출력이 나타납니다:

```
Data generation complete: 696,771 total records (12.8s)
Exporting to SQLite...
  -> ./output/ecommerce-ko.db (80.7 MB)
Export complete (11.2s)
Total elapsed time: 24.0s
```

`output/` 폴더에 파일이 생성되었는지 확인합니다:

=== "Windows"

    ```
    dir output
    ```

=== "macOS / Linux"

    ```bash
    ls -la output/
    ```

!!! tip "더 다양한 옵션이 필요하다면"
    데이터 규모 변경, 영어 데이터 생성, 노이즈 추가, 설정 파일 커스텀 등 고급 옵션은 [생성기 고급 옵션](04-generate-advanced.md)에서 안내합니다.

---

## MySQL / PostgreSQL 수동 적용

`--apply` 없이 SQL 파일만 생성한 경우, 직접 서버에 적용합니다:

=== "MySQL"

    ```bash
    mysql -u root -p < output/mysql/schema.sql
    mysql -u root -p ecommerce < output/mysql/data.sql
    mysql -u root -p ecommerce < output/mysql/procedures.sql
    ```

    각 명령마다 root 비밀번호를 입력합니다.

=== "PostgreSQL"

    ```bash
    psql -U postgres -f output/postgresql/schema.sql
    psql -U postgres ecommerce -f output/postgresql/data.sql
    psql -U postgres ecommerce -f output/postgresql/procedures.sql
    ```

---

## 문제 해결

!!! warning "자주 발생하는 문제들"

    **`python`/`pip` 명령을 찾을 수 없음**

    - Windows: `py` 또는 `py -3`을 시도하세요
    - macOS/Linux: `python3`, `pip3`을 사용하세요
    - PATH 설정이 안 된 경우: Python을 재설치하면서 "Add to PATH" 체크

    **`ModuleNotFoundError`**

    `pip install -r requirements.txt`를 실행하지 않았거나, 가상환경이 비활성 상태입니다.

    **생성 중 메모리 부족**

    `--size medium`은 약 4GB 메모리가 필요합니다. `--size small`로 시작하세요.

    **MySQL/PG `--apply` 시 접속 오류**

    DB 서버가 실행 중인지 확인하세요:
    ```bash
    # MySQL
    mysql -u root -p -e "SELECT 1"

    # PostgreSQL
    psql -U postgres -c "SELECT 1"
    ```

[← 02. 데이터베이스 설치](02-database.md){ .md-button }
[05. 확인 및 첫 쿼리 →](05-verify.md){ .md-button .md-button--primary }
