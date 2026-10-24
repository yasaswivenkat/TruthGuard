@echo off
TITLE TruthGuard Virtual Environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [TruthGuard venv activated via venv\Scripts\activate.bat]
) else if exist "venv\bin\activate.bat" (
    call venv\bin\activate.bat
    echo [TruthGuard venv activated via venv\bin\activate.bat]
) else (
    echo [ERROR] Virtual environment not found in venv\
)
cmd /k
