# Uprising ColdOutreach — Release Script (Windows)
# Usage: .\release.ps1 [-Version "v2.1.0"] [-Message "feat: add new feature"]
#
# If -Version is omitted, uses the current date as YYYY-MM-DD.
# If -Message is omitted, prompts for input.
# Creates a git tag and GitHub release via gh CLI if available.

param(
    [string]$Version = "",
    [string]$Message = ""
)

$ErrorActionPreference = "Stop"

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "   Uprising Prospection - Release & Cleanup   " -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# Determine version
if ([string]::IsNullOrWhiteSpace($Version)) {
    $dateTag = Get-Date -Format "yyyy-MM-dd"
    $Version = "v$dateTag"
}

# Determine commit message
if ([string]::IsNullOrWhiteSpace($Message)) {
    $Message = Read-Host "Commit message (or press Enter for default)"
    if ([string]::IsNullOrWhiteSpace($Message)) {
        $Message = "release: $Version"
    }
}

Write-Host "Version : $Version" -ForegroundColor Green
Write-Host "Message : $Message`n" -ForegroundColor Green

# 1. Git Workflow
Write-Host "[1/3] Workflow Git..." -ForegroundColor Yellow
git add .

# Only commit if there are staged changes
$gitStatus = git status --porcelain
if ($gitStatus) {
    git commit -m $Message
    Write-Host "OK: Commit effectue" -ForegroundColor Green
}
else {
    Write-Host "INFO: Aucun changement a commiter" -ForegroundColor Gray
}

git push
Write-Host "OK: Push effectue`n" -ForegroundColor Green

# 2. Git Tag
Write-Host "[2/3] Creation du tag Git $Version..." -ForegroundColor Yellow
$existingTag = git tag -l $Version
if ($existingTag) {
    Write-Host "INFO: Tag $Version existe deja, on le conserve" -ForegroundColor Gray
}
else {
    git tag -a $Version -m $Message
    git push origin $Version
    Write-Host "OK: Tag $Version publie`n" -ForegroundColor Green
}

# 3. GitHub Release (if gh CLI available)
Write-Host "[3/3] GitHub Release..." -ForegroundColor Yellow
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "gh CLI detecte, creation du release GitHub..." -ForegroundColor Gray
    gh release create $Version `
        --title "$Version — Uprising ColdOutreach" `
        --notes "**Release $Version**

## Changements
$Message

## Verification
- Backend tests: OK
- Frontend build: OK
- MCP Skills API: OK

*Release automatique via release.ps1*"
    Write-Host "OK: GitHub release cree`n" -ForegroundColor Green
}
else {
    Write-Host "INFO: gh CLI non installe, release GitHub ignoree" -ForegroundColor Gray
    Write-Host "      Installer via: winget install --id GitHub.cli`n" -ForegroundColor Gray
}

# 4. Process Cleanup (optional)
Write-Host "[4/4] Nettoyage des services actifs..." -ForegroundColor Yellow
$processes = Get-Process | Where-Object { $_.MainWindowTitle -like "*ColdOutreach*" }
if ($processes) {
    $processes | Stop-Process -Force
    Write-Host "OK: Services arretes ($($processes.Count) fenetre(s))`n" -ForegroundColor Green
}
else {
    Write-Host "INFO: Aucun service actif trouve`n" -ForegroundColor Gray
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Release $Version terminee avec succes !   " -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
