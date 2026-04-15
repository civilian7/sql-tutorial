# 준비하기

이 튜토리얼을 사용하기 위해서는 다음을 준비해야 합니다:

- **프로젝트 소스** — GitHub에서 다운로드 (Git 또는 ZIP)
- **Python 3.10+** — 데이터 생성기 실행에 필요
- **데이터베이스** — SQLite(설치 불필요), MySQL, 또는 PostgreSQL
- **SQL 도구** — 생성된 데이터베이스를 열고 쿼리를 실행할 프로그램

!!! info "문서만 보고 싶다면"
    설치 없이 [GitHub Pages](https://civilian7.github.io/sql-tutorial/ko/)에서 튜토리얼 전체를 웹으로 읽을 수 있습니다. 단, SQL은 **직접 쿼리해봐야** 익힙니다.

아래 5단계를 따라가면 됩니다. 처음이라도 30분이면 충분합니다.

<ul class="timeline" markdown>
<li markdown>
<div class="tl-title" markdown>[00. 프로젝트 다운로드](00-install.md)</div>
<p class="tl-desc">GitHub에서 소스를 받습니다. Git 또는 ZIP 중 선택</p>
<p class="tl-time">약 2분</p>
</li>
<li markdown>
<div class="tl-title" markdown>[01. 데이터베이스 선택](01-choose-db.md)</div>
<p class="tl-desc">SQLite, MySQL, PostgreSQL, Oracle, SQL Server 중 자신에게 맞는 DB를 고릅니다</p>
<p class="tl-time">약 1분</p>
</li>
<li markdown>
<div class="tl-title" markdown>[02. 데이터베이스 설치](02-database.md)</div>
<p class="tl-desc">선택한 DB를 설치합니다. SQLite는 설치 불필요 — 이 단계를 건너뛸 수 있습니다</p>
<p class="tl-time">약 5~10분</p>
</li>
<li markdown>
<div class="tl-title" markdown>[03. 데이터 생성](03-generate.md)</div>
<p class="tl-desc">Python을 설치하고 생성기를 실행하여 데이터베이스를 만듭니다</p>
<p class="tl-time">약 10분</p>
</li>
<li markdown>
<div class="tl-title" markdown>[04. 생성기 고급 옵션](04-generate-advanced.md)</div>
<p class="tl-desc">데이터 규모, 언어, 노이즈, 설정 파일 등 상세 옵션 (선택)</p>
<p class="tl-time">필요 시</p>
</li>
<li markdown>
<div class="tl-title" markdown>[05. 확인 및 첫 쿼리](05-verify.md)</div>
<p class="tl-desc">SQL 도구에서 데이터베이스를 열고 첫 쿼리를 실행합니다</p>
<p class="tl-time">약 5분</p>
</li>
</ul>

## OS별 · DB별 설치 요약

=== "Windows"

    | 소프트웨어 | SQLite 사용 시 | MySQL 추가 | PostgreSQL 추가 |
    |-----------|:-------------:|:---------:|:--------------:|
    | [Git](https://git-scm.com/download/win) | **필수** | **필수** | **필수** |
    | [Python](https://www.python.org/downloads/) | **필수** | **필수** | **필수** |
    | [MySQL Server](https://dev.mysql.com/downloads/installer/) | — | **필수** | — |
    | [PostgreSQL](https://www.postgresql.org/download/windows/) | — | — | **필수** |
    | [DBeaver](https://dbeaver.io/download/) (추천) | 추천 | 추천 | 추천 |

=== "macOS"

    | 소프트웨어 | SQLite 사용 시 | MySQL 추가 | PostgreSQL 추가 |
    |-----------|:-------------:|:---------:|:--------------:|
    | Git | 기본 포함 | 기본 포함 | 기본 포함 |
    | `brew install python@3.12` | **필수** | **필수** | **필수** |
    | `brew install mysql` | — | **필수** | — |
    | `brew install postgresql@16` | — | — | **필수** |
    | [DBeaver](https://dbeaver.io/download/) (추천) | 추천 | 추천 | 추천 |

=== "Linux (Ubuntu/Debian)"

    | 소프트웨어 | SQLite 사용 시 | MySQL 추가 | PostgreSQL 추가 |
    |-----------|:-------------:|:---------:|:--------------:|
    | `sudo apt install git` | **필수** | **필수** | **필수** |
    | `sudo apt install python3 python3-pip` | **필수** | **필수** | **필수** |
    | `sudo apt install mysql-server` | — | **필수** | — |
    | `sudo apt install postgresql` | — | — | **필수** |
    | [DBeaver](https://dbeaver.io/download/) (추천) | 추천 | 추천 | 추천 |

!!! tip "SQLite로 시작한다면"
    Git + Python만 설치하면 됩니다. DB 서버 설치가 필요 없어 가장 빠르게 시작할 수 있습니다.

각 단계의 상세 설치 방법은 해당 페이지에서 안내합니다.

[00. 프로젝트 다운로드 →](00-install.md){ .md-button .md-button--primary }
