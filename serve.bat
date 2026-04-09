@echo off
setlocal

set LANG=%~1
if "%LANG%"=="" set LANG=all

if "%LANG%"=="all" (
    echo Building both languages...
    cd /d "%~dp0docs"
    mkdocs build -f mkdocs-ko.yml -q
    mkdocs build -f mkdocs-en.yml -q

    echo.
    echo Serving at http://localhost:8001
    echo   Korean:  http://localhost:8001/ko/
    echo   English: http://localhost:8001/en/
    echo.

    cd /d "%~dp0output\docs"
    python -m http.server 8001
) else (
    cd /d "%~dp0docs"
    mkdocs serve -f mkdocs-%LANG%.yml -a localhost:8001
)
