@echo off
setlocal EnableDelayedExpansion

rem Get the directory where the batch file is located
set SCRIPT_DIR=%~dp0

rem If no argument is provided
if "%~1"=="" (
    echo Usage: compress_video.bat ^<input_file^>
) else (
    python "%SCRIPT_DIR%compress_video.py" "%~1"
)
