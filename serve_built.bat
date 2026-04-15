@echo off
setlocal

set LANG=%~1
if "%LANG%"=="" set LANG=ko
set PORT=%~2
if "%PORT%"=="" set PORT=8001

echo [1] Building %LANG%...
cd /d "%~dp0docs"
mkdocs build -f mkdocs-%LANG%.yml -q
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo [2] Serving on http://localhost:%PORT%/
cd /d "%~dp0output\docs\%LANG%"
python -m http.server %PORT%
