# TruthGuard Virtual Environment PowerShell Activator
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptPath

if (Test-Path ".\venv\Scripts\Activate.ps1") {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "[TruthGuard venv activated via venv\Scripts\Activate.ps1]" -ForegroundColor Green
} elseif (Test-Path ".\venv\bin\Activate.ps1") {
    & ".\venv\bin\Activate.ps1"
    Write-Host "[TruthGuard venv activated via venv\bin\Activate.ps1]" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Virtual environment not found in .\venv\" -ForegroundColor Red
}
