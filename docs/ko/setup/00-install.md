# 00. 프로젝트 다운로드

이 프로젝트는 [GitHub](https://github.com/civilian7/sql-tutorial)에서 소스 코드, 데이터 생성기, 문서를 모두 관리합니다.

문서는 수시로 업데이트되므로 **항상 최신 상태를 유지할 수 있는 Git 사용을 권장**합니다. Git이 처음이라면 아래 설명을 참고하세요.

## Git이란?

**Git**은 파일의 변경 이력을 추적하는 버전 관리 시스템입니다. 이 튜토리얼에서는 두 가지만 알면 됩니다:

- `git clone` — 프로젝트를 내 컴퓨터에 복사
- `git pull` — 이후 업데이트를 한 줄로 받기

!!! info "Git 설치 방법 (클릭해서 펼치기)"

    === "Windows"

        [git-scm.com](https://git-scm.com/download/win)에서 다운로드하여 설치합니다. 설치 중 기본 옵션을 그대로 두면 됩니다.

        설치 후 **명령 프롬프트** 또는 **Git Bash**에서 확인:

        ```
        git --version
        ```

    === "macOS"

        **터미널**에서:

        ```bash
        # Xcode 명령줄 도구에 포함 (대부분 이미 설치됨)
        git --version

        # 없으면 Homebrew로 설치
        brew install git
        ```

    === "Linux (Ubuntu/Debian)"

        ```bash
        sudo apt update && sudo apt install git
        git --version
        ```

## 다운로드 방법

=== "Git (추천)"

    ```bash
    git clone https://github.com/civilian7/sql-tutorial.git
    cd sql-tutorial
    ```

    이후 업데이트가 있을 때:

    ```bash
    git pull
    ```

=== "Git GUI (GitHub Desktop)"

    커맨드라인이 어렵다면 [GitHub Desktop](https://desktop.github.com/)을 사용할 수 있습니다.

    1. GitHub Desktop 설치 후 실행
    2. **File > Clone repository** 선택
    3. URL 탭에서 `https://github.com/civilian7/sql-tutorial.git` 입력
    4. 로컬 경로 지정 후 **Clone** 클릭
    5. 이후 업데이트: 상단의 **Fetch origin** → **Pull origin** 클릭

=== "ZIP 다운로드"

    Git 없이 바로 시작할 수 있지만, 업데이트를 받으려면 매번 다시 다운로드해야 합니다.

    1. [GitHub에서 ZIP 다운로드](https://github.com/civilian7/sql-tutorial/archive/refs/heads/main.zip)
    2. 다운로드한 파일의 압축을 풀기
    3. 압축을 푼 폴더(`sql-tutorial-main`)로 이동

    !!! warning "ZIP의 한계"
        ZIP은 다운로드 시점의 스냅샷입니다. 레슨 추가, 오류 수정 등의 업데이트를 받을 수 없습니다.

## 다운로드 확인

프로젝트 폴더에 다음 파일이 있으면 정상입니다:

```
sql-tutorial/
├── generate.py          ← 데이터 생성기
├── requirements.txt     ← Python 의존성
├── config.yaml          ← 생성 설정
├── src/                 ← 생성기 소스 코드
├── data/                ← 상품·카테고리 마스터 데이터
├── docs/                ← 튜토리얼 문서
└── output/              ← (생성 후) DB/SQL 출력
```

[← 준비하기](index.md){ .md-button }
[01. 데이터베이스 선택 →](01-choose-db.md){ .md-button .md-button--primary }
