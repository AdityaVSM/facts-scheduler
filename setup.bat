@echo off
REM ════════════════════════════════════════════════════════
REM  Java Fact Agent — Windows Setup Script
REM  Run this ONCE to set everything up
REM ════════════════════════════════════════════════════════

echo.
echo ╔══════════════════════════════════════════╗
echo ║   Java Fact Agent — Windows Setup       ║
echo ╚══════════════════════════════════════════╝
echo.

REM ── Check Python ──────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Download from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)
echo [OK] Python found:
python --version

REM ── Create virtual environment ────────────────────────
echo.
echo [SETUP] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created

REM ── Install dependencies ──────────────────────────────
echo.
echo [SETUP] Installing dependencies...
call venv\Scripts\activate.bat
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo [ERROR] pip install failed. See above for details.
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM ── Create .env if not exists ─────────────────────────
echo.
if not exist ".env" (
    copy .env.local .env >nul
    echo [OK] Created .env from template
    echo.
    echo ════════════════════════════════════════════════════
    echo  ACTION REQUIRED: Open .env and fill in your values
    echo  - DB_PASSWORD       (your PostgreSQL password)
    echo  - MAIL_SENDER       (your Gmail address)
    echo  - MAIL_APP_PASSWORD (Gmail App Password)
    echo  - LLM_API_KEY       (Anthropic API key)
    echo ════════════════════════════════════════════════════
) else (
    echo [OK] .env already exists
)

REM ── Create PostgreSQL database ────────────────────────
echo.
echo [SETUP] Creating PostgreSQL database 'factdb'...
psql -U postgres -c "SELECT 1 FROM pg_database WHERE datname='factdb'" 2>nul | findstr /c:"1 row" >nul
if errorlevel 1 (
    psql -U postgres -c "CREATE DATABASE factdb;" 2>nul
    if errorlevel 1 (
        echo [WARN] Could not auto-create database.
        echo        Run manually in psql: CREATE DATABASE factdb;
    ) else (
        echo [OK] Database 'factdb' created
    )
) else (
    echo [OK] Database 'factdb' already exists
)

echo.
echo ════════════════════════════════════════════════════
echo  Setup complete!
echo.
echo  Next steps:
echo  1. Edit .env with your credentials (if not done yet)
echo  2. Run: run.bat
echo  3. Test: curl -X POST http://localhost:8080/trigger
echo ════════════════════════════════════════════════════
echo.
pause
