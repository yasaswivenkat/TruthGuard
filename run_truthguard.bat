@echo off
TITLE TruthGuard Multi-Agent Server (Virtusa Jatayu S6 - CodeBots)
COLOR 0B

echo TruthGuard: Adversarial Multi-Agent Document Q&A Verification
echo Virtusa Jatayu Season 6 | Track: TIME BU | Team: CodeBots
echo.

echo [1/3] Checking Python Virtual Environment (venv)...
if not exist "venv\" (
    echo [INFO] Virtual environment not found. Creating venv...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment. Ensure Python is installed.
        pause
        exit /b
    )
    echo [INFO] Virtual environment created successfully.
)

set VENV_PYTHON=
if exist "venv\Scripts\python.exe" (
    set VENV_PYTHON=venv\Scripts\python.exe
) else if exist "venv\bin\python.exe" (
    set VENV_PYTHON=venv\bin\python.exe
) else (
    echo [WARNING] Could not locate venv python executable. Falling back to system python.
    set VENV_PYTHON=python
)

echo [2/3] Active Virtual Environment Runtime:
%VENV_PYTHON% --version

echo [3/3] Starting TruthGuard Engine inside virtual environment at http://localhost:8000 ...
start "" "http://localhost:8000/index.html"
%VENV_PYTHON% server.py

pause
