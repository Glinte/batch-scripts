@echo off
setlocal EnableDelayedExpansion

REM This script takes in two arguments: the first is the path to the file to be converted, and the second is the path to the output file.
REM Usage: boc2ynab.bat <input_file> <output_file>
REM where <input_file> is the path to the BOC xls file and <output_file> is the path to the YNAB CSV file.
REM This script simply calls the Python script boc2ynab.py with the provided arguments.

REM Check if the correct number of arguments is provided
if "%~1"=="" (
    echo Usage: boc2ynab.bat ^<input_file^> ^<output_file^>
    exit /b 1
)
set "input_file=%~1"

if "%~2"=="" (
    echo No output file specified, using default output file: "%~dpn1.csv"
    set "output_file=%~dpn1.csv"
) else (
    set "output_file=%~2"
)

REM Check if the input file exists
if not exist "%input_file%" (
    echo Input file "%input_file%" does not exist.
    exit /b 1
)

REM Check if the output file already exists
if exist "%output_file%" (
    set /p overwrite_choice="Output file %output_file% exists. Overwrite? [y/N] "
    if /i "!overwrite_choice!" neq "y" (
        echo Exiting without overwriting.
        exit /b 1
    )
)

REM Call the Python script with the provided arguments
uv run "%~dp0boc2ynab.py" "%input_file%" "%output_file%"
