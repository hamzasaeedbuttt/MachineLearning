@echo off
REM Set UTF-8 encoding to avoid character issues
chcp 65001 >nul 2>&1
title Stock Investment Recommendations
color 0B
mode con: cols=80 lines=25

REM Get the directory where the batch file is located
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo.
    echo ERROR: Virtual environment not found!
    echo Please run setup first.
    echo.
    pause
    exit /b 1
)

REM Clear screen and show startup message
cls
echo.
echo ============================================================
echo          STOCK INVESTMENT RECOMMENDATIONS
echo          Launching Application...
echo ============================================================
echo.

REM Start API server in background (hidden window)
echo [1/2] Starting FastAPI Server...
start "" /MIN "%~dp0venv\Scripts\python.exe" -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 >nul 2>&1

REM Wait a bit for API to start
timeout /t 3 /nobreak >nul 2>&1

REM Start Frontend server in background (hidden window)
echo [2/2] Starting Frontend Server...
cd frontend
start "" /MIN "%~dp0venv\Scripts\python.exe" server.py >nul 2>&1
cd ..

REM Wait for servers to be ready
timeout /t 5 /nobreak >nul 2>&1

REM Open browser
echo.
echo Opening browser...
start http://localhost:8080 >nul 2>&1

REM Close the launcher window after a brief moment
timeout /t 2 /nobreak >nul 2>&1
cls
echo.
echo ============================================================
echo          Application Launched Successfully!
echo.
echo          Your browser should now be open.
echo          Frontend: http://localhost:8080
echo.
echo          Servers are running in the background.
echo          To stop: Close the minimized server windows
echo          or check Task Manager for Python processes.
echo ============================================================
echo.
timeout /t 5 >nul
exit
