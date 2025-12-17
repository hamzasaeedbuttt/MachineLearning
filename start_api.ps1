# Start FastAPI Server
Write-Host "Starting FastAPI Server..." -ForegroundColor Green
cd $PSScriptRoot
.\venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000


