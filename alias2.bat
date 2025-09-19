@echo off
setlocal EnableDelayedExpansion

REM Define alias directory (assumed to be C:\Aliases)
set "aliasDir=C:\Aliases"

REM ----- List all aliases if no arguments provided -----
if "%~1"=="" (
    echo Current aliases:
    for %%F in ("%aliasDir%\*.bat") do (
        set "aliasName=%%~nF"
        if /I not "!aliasName!"=="alias" (
            REM Get the command by finding the line starting with "call"
            for /f "tokens=1,* delims= " %%a in ('findstr /b /c:"call" "%%F"') do (
                set "aliasCmd=%%b"
                REM Remove trailing " %%*" (used for argument passing)
                set "aliasCmd=!aliasCmd: %%*=!"
            )
            echo alias !aliasName!='!aliasCmd!'
        )
    )
    endlocal
    exit /b
)

REM ----- Show alias definition if no '=' present in the argument -----
echo %* | find "=" >nul
if errorlevel 1 (
    if exist "%aliasDir%\%~1.bat" (
        echo %~1 is aliased to:
        for /f "tokens=1,* delims= " %%a in ('findstr /b /c:"call" "%aliasDir%\%~1.bat"') do (
            set "aliasCmd=%%b"
            set "aliasCmd=!aliasCmd: %%*=!"
        )
        echo alias %~1='!aliasCmd!'
    ) else (
        echo No alias named '%~1' found.
    )
    endlocal
    exit /b
)

REM ----- Create or update an alias (syntax: alias name=command) -----
set "line=%*"
for /f "tokens=1* delims==" %%a in ("%line%") do (
    set "name=%%a"
    set "cmd=%%b"
)

REM Remove surrounding quotes from the command if any
set "cmd=%cmd:"=%"

REM Write the alias file (overwrite if it exists)
(
    echo @echo off
    REM Using call so that %%* is expanded to %* at runtime (passing any extra arguments)
    echo call %cmd% %%*
) > "%aliasDir%\%name%.bat"

echo Alias "%name%" created for command: %cmd%
endlocal
