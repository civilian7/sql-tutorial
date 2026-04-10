@echo off
setlocal

set LANG=%~1
if "%LANG%"=="" set LANG=all

:: Check if mkdocs-exporter is installed
pip show mkdocs-exporter >nul 2>&1
if errorlevel 1 (
    echo Installing mkdocs-exporter...
    pip install mkdocs-exporter
)

:: Check if Chromium is installed for Playwright
python -c "from playwright.sync_api import sync_playwright" >nul 2>&1
if errorlevel 1 (
    echo Installing Playwright and Chromium...
    pip install playwright
    playwright install chromium
)

set MKDOCS_EXPORTER_PDF=true

if "%LANG%"=="ko" goto :build_ko
if "%LANG%"=="en" goto :build_en
if "%LANG%"=="all" goto :build_all

echo Usage: pdf.bat [ko^|en^|all]
goto :eof

:build_ko
echo Building Korean PDF...
cd /d "%~dp0docs"
mkdocs build -f mkdocs-ko.yml
echo.
echo Output: output\docs\ko\pdf\sql-tutorial-ko.pdf
goto :eof

:build_en
echo Building English PDF...
cd /d "%~dp0docs"
mkdocs build -f mkdocs-en.yml
echo.
echo Output: output\docs\en\pdf\sql-tutorial-en.pdf
goto :eof

:build_all
echo Building Korean PDF...
cd /d "%~dp0docs"
mkdocs build -f mkdocs-ko.yml
echo.
echo Building English PDF...
mkdocs build -f mkdocs-en.yml
echo.
echo Output:
echo   output\docs\ko\pdf\sql-tutorial-ko.pdf
echo   output\docs\en\pdf\sql-tutorial-en.pdf
goto :eof
