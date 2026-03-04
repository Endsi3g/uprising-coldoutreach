# Unified Release & Cleanup Script for Uprising ColdOutreach

$ErrorActionPreference = "Stop"

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "   Uprising Prospection - Release & Cleanup   " -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# 1. Git Workflow
Write-Host "[1/2] Execution du workflow Git..." -ForegroundColor Yellow
Write-Host "Ajout des fichiers..." -ForegroundColor Gray
git add .

Write-Host "Commit des changements..." -ForegroundColor Gray
git commit -m "feat: jasmin integration and performance optimizations"

Write-Host "Push vers le depot distant..." -ForegroundColor Gray
git push
Write-Host "Succes: Changements pousses.`n" -ForegroundColor Green

# 2. Process Cleanup
Write-Host "[2/2] Fermeture des services actifs..." -ForegroundColor Yellow
$processes = Get-Process | Where-Object { $_.MainWindowTitle -like "*ColdOutreach-Backend*" }

if ($processes) {
    Write-Host "Fermeture de $($processes.Count) fenetre(s) identifiee(s)..." -ForegroundColor Gray
    $processes | Stop-Process -Force
    Write-Host "Succes: Services arretes.`n" -ForegroundColor Green
} else {
    Write-Host "Info: Aucun service backend actif trouve via le titre de la fenetre.`n" -ForegroundColor Gray
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Release terminee et environnement propre ! " -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
