@echo off
REM ============================================================
REM SBI-ADS launcher (Windows)
REM Creates the virtual environment on first run, installs
REM dependencies, and starts the server on http://127.0.0.1:8000
REM ============================================================

cd /d "%~dp0"

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo.
echo  ==============================================
echo   SBI-ADS  -  http://127.0.0.1:8000/dashboard
echo  ==============================================
echo.

uvicorn main:app --host 127.0.0.1 --port 8000
