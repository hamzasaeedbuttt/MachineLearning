@echo off
echo ========================================
echo   Stock Investment Recommendations
echo   Starting Application...
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Starting FastAPI Server...
start "Stock API Server" cmd /k "venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend Server...
echo.
echo ========================================
echo   Application is starting!
echo   Frontend will open automatically
echo   API Server: http://localhost:8000
echo   Frontend: http://localhost:8080
echo ========================================
echo.

cd frontend
start "Stock Frontend Server" cmd /k "..\venv\Scripts\python.exe server.py"

timeout /t 5 /nobreak >nul

start http://localhost:8080

echo.
echo ========================================
echo   Application launched successfully!
echo   Close this window if desired.
echo   To stop servers, close their windows.
echo ========================================
echo.

pause

