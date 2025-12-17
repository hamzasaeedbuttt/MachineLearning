# Start Streamlit Frontend
Write-Host "Starting Streamlit Frontend..." -ForegroundColor Green
cd $PSScriptRoot
.\venv\Scripts\python.exe -m streamlit run frontend/app.py


