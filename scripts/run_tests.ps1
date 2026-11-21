# BolKhata - Run Automated Test Suite
Write-Host "Running BolKhata Backend Pytest Tests..." -ForegroundColor Cyan
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$PSScriptRoot\..\backend"
python -m pytest -v
