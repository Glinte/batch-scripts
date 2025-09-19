@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Usage: %~nx0 file1 [file2 ... fileN]
    exit /b 1
)

rem --- Compute hash of the first file
set "first=%~1"
for /f "usebackq tokens=*" %%H in (`
    powershell -NoProfile -Command "Get-FileHash -Algorithm SHA256 '%first%' ^| Select-Object -ExpandProperty Hash"
`) do set "baseHash=%%H"

shift

:compare_next
if "%~1"=="" goto all_equal

rem --- Compute hash of the next file
set "current=%~1"
for /f "usebackq tokens=*" %%H in (`
    powershell -NoProfile -Command "Get-FileHash -Algorithm SHA256 '%current%' ^| Select-Object -ExpandProperty Hash"
`) do set "nextHash=%%H"

if /I "!baseHash!" neq "!nextHash!" (
    echo NOT identical: "%first%" vs "%current%"
    exit /b 2
)

shift
goto compare_next

:all_equal
echo All files (%*) are identical.
exit /b 0
