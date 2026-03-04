# Uprising ColdOutreach - Unified Deployment Script (Windows)

$ErrorActionPreference = "Stop"

function Show-Header {
    Write-Host "`n================================================" -ForegroundColor Cyan
    Write-Host "   Uprising Prospection - Deployment Script   " -ForegroundColor Cyan
    Write-Host "================================================`n" -ForegroundColor Cyan
}

Show-Header

# 1. Check Prerequisites
Write-Host "[1/4] Vérification des prérequis..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python n'est pas installé ou n'est pas dans le PATH."
}
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js n'est pas installé ou n'est pas dans le PATH."
}
Write-Host "✅ Prérequis validés.`n" -ForegroundColor Green

# 2. Setup Backend
Write-Host "[2/4] Configuration du Backend (FastAPI)..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    Write-Host "Création de l'environnement virtuel..."
    python -m venv venv
}
Write-Host "Installation des dépendances Python..."
& .\venv\Scripts\python.exe -m pip install --upgrade pip
& .\venv\Scripts\python.exe -m pip install -r requirements.txt
Write-Host "✅ Backend configuré.`n" -ForegroundColor Green

# 3. Setup & Build Frontend
Write-Host "[3/4] Configuration du Frontend (React/Vite)..." -ForegroundColor Yellow
Set-Location .\prospectai
Write-Host "Installation des dépendances npm..."
npm install
Write-Host "Construction du projet (Build)..."
npm run build
Set-Location ..
Write-Host "✅ Frontend construit.`n" -ForegroundColor Green

# 4. Launch Application
Write-Host "[4/4] Lancement des services..." -ForegroundColor Yellow
Write-Host "Lancement du backend sur http://localhost:8000" -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

Write-Host "Lancement du frontend sur http://localhost:3000" -ForegroundColor Gray
Set-Location .\prospectai
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev -- --port 3000"
Set-Location ..

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "   Déploiement terminé avec succès !         " -ForegroundColor Green
Write-Host "   Interface : http://localhost:3000         " -ForegroundColor White
Write-Host "   API Doc   : http://localhost:8000/docs    " -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan
