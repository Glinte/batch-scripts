@echo off
setlocal enabledelayedexpansion

REM Determine the directory where the script is located
set "SCRIPT_DIR=%~dp0"

REM Run the Python script
uv run --script "%SCRIPT_DIR%rename_md_frontmatter.py" %*
exit /b %errorlevel%
