# BolKhata - Start React Frontend
Write-Host "Starting BolKhata Frontend on http://localhost:5173..." -ForegroundColor Green
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$PSScriptRoot\..\frontend"
npm.cmd run dev
