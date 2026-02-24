@echo off
REM ════════════════════════════════════════════════════════
REM  Java Fact Agent — Run
REM ════════════════════════════════════════════════════════

REM ── Check venv exists ─────────────────────────────────
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found.
    echo         Run setup.bat first!
    pause
    exit /b 1
)

REM ── Check .env exists ─────────────────────────────────
if not exist ".env" (
    echo [ERROR] .env file not found.
    echo         Run setup.bat first, then fill in your credentials.
    pause
    exit /b 1
)

REM ── Activate venv ─────────────────────────────────────
call venv\Scripts\activate.bat

echo.
echo ╔══════════════════════════════════════════╗
echo ║   Java Fact Agent — Starting...         ║
echo ╚══════════════════════════════════════════╝
echo.
echo  App running at: http://localhost:8080
echo.
echo  To send a test email RIGHT NOW, open a new
echo  Command Prompt and run:
echo.
echo    curl -X POST http://localhost:8080/trigger
echo.
echo  Press Ctrl+C to stop.
echo.

python main.py
pause
