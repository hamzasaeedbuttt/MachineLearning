# Start both API and Frontend services

Write-Host "Starting Stock Predictor Services..." -ForegroundColor Green
Write-Host ""

# Start API server in background
Write-Host "Starting API server on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"

# Wait a moment for API to start
Start-Sleep -Seconds 2

# Start Frontend (runs in current terminal)
Write-Host "Starting Frontend on port 8501..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Frontend will open at http://localhost:8501" -ForegroundColor Cyan
Write-Host "API is running at http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
.\venv\Scripts\python.exe -m streamlit run frontend/app.py


