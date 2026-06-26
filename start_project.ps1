# Offline Precision Agriculture AI - Windows Launcher
# This script sets up the environment and launches all components.

$ErrorActionPreference = "SilentlyContinue"
# Force UTF8 for terminal output to avoid encoding errors
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Starting Agriculture AI Framework (Professional Edition)..." -ForegroundColor Green

# 1. Check for Python
if (!(Get-Command python)) {
    Write-Host "Python not found. Please install Python 3.8+ from python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# 2. Check for Node.js
if (!(Get-Command npm)) {
    Write-Host "Node.js/NPM not found. Please install Node.js from nodejs.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# 3. Setup Python Virtual Environment
if (!(Test-Path venv)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

Write-Host "Verifying Python dependencies..." -ForegroundColor Cyan
& ".\venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet

# 4. Setup Frontend
if (!(Test-Path "frontend\node_modules")) {
    Write-Host "Installing Frontend dependencies (this might take a minute)..." -ForegroundColor Cyan
    Push-Location frontend
    npm install --quiet
    Pop-Location
}

# 5. Discover ESP32
Write-Host "Checking for hardware..." -ForegroundColor Yellow
$esp_port = & ".\venv\Scripts\python.exe" find_esp32.py --get-port

if ([string]::IsNullOrWhiteSpace($esp_port)) {
    Write-Host "ESP32 not detected." -ForegroundColor Yellow
    $esp_port = Read-Host "Enter COM port (e.g. COM3) or just press ENTER to skip hardware"
} else {
    Write-Host "Detected ESP32 on $esp_port" -ForegroundColor Green
}

# 6. Launch Components
Write-Host "Launching Enterprise Dashboard..." -ForegroundColor Green

# Launch Backend
$backendCmd = "cd '$PSScriptRoot'; .\venv\Scripts\python.exe -m uvicorn server.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$backendCmd"
Write-Host "  [OK] Backend Service Started" -ForegroundColor Gray

# Launch Frontend
$frontendCmd = "cd '$PSScriptRoot\frontend'; npm start"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$frontendCmd"
Write-Host "  [OK] Frontend Service Started" -ForegroundColor Gray

# Launch Serial Ingestor (if port available)
if (![string]::IsNullOrWhiteSpace($esp_port)) {
    $serialCmd = "cd '$PSScriptRoot'; .\venv\Scripts\python.exe scripts/ingest_arduino.py --port $esp_port"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "$serialCmd"
    Write-Host "  [OK] Hardware Link Active ($esp_port)" -ForegroundColor Gray
}

Write-Host "`nReady! Your browser will open automatically." -ForegroundColor Green
Write-Host "Keep the background windows open during your presentation."
Write-Host "Press any key to close this launcher..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
