@echo off
title PENOSINT
setlocal enabledelayedexpansion

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

if not exist "modules\misc.py" (
    echo [ERROR] Run this from the PENOSINT root directory.
    pause
    exit /b 1
)

if not exist "Misc\requirements.txt" (
    echo [WARNING] Misc\requirements.txt not found, skipping dependency check.
    goto run
)

echo.
echo  Checking dependencies...
echo.

for /f "usebackq tokens=*" %%P in ("Misc\requirements.txt") do (
    set "pkg=%%P"
    if not "!pkg!"=="" (
        python -c "import importlib; pkg='!pkg!'.split('[')[0].replace('-','_'); importlib.import_module(pkg)" >nul 2>&1
        if errorlevel 1 (
            echo  [ .. ] Installing !pkg!...
            pip install "%%P" --quiet >nul 2>&1
            if errorlevel 1 (
                echo  [ !! ] Failed    ^> !pkg!
            ) else (
                echo  [ OK ] Installed ^> !pkg!
            )
        ) else (
            echo  [ OK ] !pkg!
        )
    )
)

echo.

:run
cls
python main.py
