# Uprising ColdOutreach — Unified Deployment Script (Windows)
# Usage: .\deploy.ps1
# Launches backend (uvicorn) + scheduler as separate PowerShell windows.

$ErrorActionPreference = "Stop"

function Show-Header {
    Write-Host "`n================================================" -ForegroundColor Cyan
    Write-Host "   Uprising Prospection - Deployment Script   " -ForegroundColor Cyan
    Write-Host "================================================`n" -ForegroundColor Cyan
}

Show-Header

# 1. Check Prerequisites
Write-Host "[1/4] Verification des prerequis..." -ForegroundColor Yellow

$dockerAvailable = $false
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $dockerAvailable = $true
    Write-Host "OK Docker detecte." -ForegroundColor Green
}
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python n'est pas installe ou n'est pas dans le PATH."
}
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js n'est pas installe ou n'est pas dans le PATH."
}
Write-Host "OK Prerequis valides.`n" -ForegroundColor Green

if ($dockerAvailable) {
    $choice = Read-Host "Souhaitez-vous lancer l'application via Docker ? (O/N)"
    if ($choice -eq 'O' -or $choice -eq 'o') {
        Write-Host "Demarrage via Docker Compose..." -ForegroundColor Cyan
        docker-compose up --build
        exit
    }
}

# 2. Setup Backend
Write-Host "[2/4] Configuration du Backend (FastAPI)..." -ForegroundColor Yellow
if (!(Test-Path ".venv")) {
    Write-Host "Creation de l'environnement virtuel..."
    python -m venv .venv
}
Write-Host "Installation des dependances Python..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
Write-Host "OK Backend configure.`n" -ForegroundColor Green

# 3. Setup & Build Frontend
Write-Host "[3/4] Configuration du Frontend (React/Vite)..." -ForegroundColor Yellow
Set-Location .\prospectai
Write-Host "Installation des dependances npm..."
npm install --silent
Write-Host "Construction du projet (Build)..."
npm run build
Set-Location ..
Write-Host "OK Frontend construit.`n" -ForegroundColor Green

# 3.5 Run Backend Tests
Write-Host "[3.5/4] Execution des tests backend..." -ForegroundColor Yellow
& .\.venv\Scripts\pytest.exe tests/test_api_endpoints.py tests/test_mcp_skills.py tests/test_apify_integration.py -v --tb=short
if ($LASTEXITCODE -ne 0) {
    Write-Error "Les tests backend ont echoue. Le deploiement est interrompu."
}
Write-Host "OK Tests backend reussis.`n" -ForegroundColor Green

# 4. Launch Application
Write-Host "[4/4] Lancement des services..." -ForegroundColor Yellow
Write-Host "Lancement du backend   -> http://localhost:8000" -ForegroundColor Gray
Write-Host "Lancement du scheduler -> process arrière-plan" -ForegroundColor Gray
Write-Host "(Le frontend est servi par le backend en production)" -ForegroundColor Gray

$root = $PSScriptRoot

# Start backend (uvicorn)
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$root'; Write-Host 'Backend starting...' -ForegroundColor Cyan; .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
) -WindowStyle Normal

Start-Sleep -Seconds 2

# Start scheduler (APScheduler)
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$root'; Write-Host 'Scheduler starting...' -ForegroundColor Yellow; .\.venv\Scripts\python.exe -m app.scheduler"
) -WindowStyle Normal

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "   Deploiement termine avec succes !         " -ForegroundColor Green
Write-Host "   Interface : http://localhost:8000         " -ForegroundColor White
Write-Host "   API Doc   : http://localhost:8000/docs    " -ForegroundColor White
Write-Host "   MCP Api   : http://localhost:8000/mcp     " -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan
