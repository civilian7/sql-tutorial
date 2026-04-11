# Getting Started

To use this tutorial, you need to prepare the following:

- **Project source** — Download from GitHub (Git or ZIP)
- **Python 3.10+** — Required to run the data generator
- **Database** — SQLite (no installation needed), MySQL, or PostgreSQL
- **SQL tool** — A program to open the generated database and run queries

!!! info "Just want to read the docs?"
    You can read the entire tutorial on the web at [GitHub Pages](https://civilian7.github.io/sql-tutorial/ko/) without any installation. However, you really need to **practice querying** to learn SQL.

Follow the 5 steps below. Even for beginners, 30 minutes is enough.

<ul class="timeline" markdown>
<li markdown>
<div class="tl-title" markdown>[00. Download the Project](00-install.md)</div>
<p class="tl-desc">Get the source from GitHub. Choose between Git or ZIP</p>
<p class="tl-time">~2 min</p>
</li>
<li markdown>
<div class="tl-title" markdown>[01. Choose a Database](01-choose-db.md)</div>
<p class="tl-desc">Pick the right DB for you from SQLite, MySQL, or PostgreSQL</p>
<p class="tl-time">~1 min</p>
</li>
<li markdown>
<div class="tl-title" markdown>[02. Install the Database](02-database.md)</div>
<p class="tl-desc">Install your chosen DB. SQLite requires no installation — you can skip this step</p>
<p class="tl-time">~5-10 min</p>
</li>
<li markdown>
<div class="tl-title" markdown>[03. Generate Data](03-generate.md)</div>
<p class="tl-desc">Install Python and run the generator to create the database</p>
<p class="tl-time">~10 min</p>
</li>
<li markdown>
<div class="tl-title" markdown>[04. Advanced Generator Options](04-generate-advanced.md)</div>
<p class="tl-desc">Detailed options for data size, language, noise, config files, etc. (optional)</p>
<p class="tl-time">As needed</p>
</li>
<li markdown>
<div class="tl-title" markdown>[05. Verify and First Query](05-verify.md)</div>
<p class="tl-desc">Open the database in a SQL tool and run your first query</p>
<p class="tl-time">~5 min</p>
</li>
</ul>

## Installation Summary by OS and DB

=== "Windows"

    | Software | For SQLite | + MySQL | + PostgreSQL |
    |----------|:---------:|:------:|:-----------:|
    | [Git](https://git-scm.com/download/win) | **Required** | **Required** | **Required** |
    | [Python](https://www.python.org/downloads/) | **Required** | **Required** | **Required** |
    | [MySQL Server](https://dev.mysql.com/downloads/installer/) | — | **Required** | — |
    | [PostgreSQL](https://www.postgresql.org/download/windows/) | — | — | **Required** |
    | [DBeaver](https://dbeaver.io/download/) (recommended) | Recommended | Recommended | Recommended |

=== "macOS"

    | Software | For SQLite | + MySQL | + PostgreSQL |
    |----------|:---------:|:------:|:-----------:|
    | Git | Included | Included | Included |
    | `brew install python@3.12` | **Required** | **Required** | **Required** |
    | `brew install mysql` | — | **Required** | — |
    | `brew install postgresql@16` | — | — | **Required** |
    | [DBeaver](https://dbeaver.io/download/) (recommended) | Recommended | Recommended | Recommended |

=== "Linux (Ubuntu/Debian)"

    | Software | For SQLite | + MySQL | + PostgreSQL |
    |----------|:---------:|:------:|:-----------:|
    | `sudo apt install git` | **Required** | **Required** | **Required** |
    | `sudo apt install python3 python3-pip` | **Required** | **Required** | **Required** |
    | `sudo apt install mysql-server` | — | **Required** | — |
    | `sudo apt install postgresql` | — | — | **Required** |
    | [DBeaver](https://dbeaver.io/download/) (recommended) | Recommended | Recommended | Recommended |

!!! tip "If Using SQLite Only"
    You only need to install Git + Python. No DB server installation needed, making it the fastest way to get started.

Detailed installation instructions for each step are provided on the respective pages.

[00. Download the Project →](00-install.md){ .md-button .md-button--primary }
