# BolKhata - Start FastAPI Backend Server
Write-Host "Starting BolKhata Backend on http://127.0.0.1:8000..." -ForegroundColor Green
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$PSScriptRoot\..\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
