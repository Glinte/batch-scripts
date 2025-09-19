@echo off
setlocal

rem Get the directory where the batch file is located
set SCRIPT_DIR=%~dp0

rem Get the current directory where the batch file is called from
set CURRENT_DIR=%CD%

rem If no argument is provided, use the current directory
if "%~1"=="" (
    python "%SCRIPT_DIR%resize_images.py" "%CURRENT_DIR%"
) else (
    rem If an argument is provided, use that directory
    python "%SCRIPT_DIR%resize_images.py" "%~1"
)

if errorlevel 1 (
    echo Error occurred during execution
    pause
    exit /b 1
)

echo Done!
pause