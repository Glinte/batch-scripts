@echo off
setlocal enabledelayedexpansion

REM Check if no arguments: list aliases
if "%~1"=="" (
  echo Current aliases:
  for %%F in (C:\Aliases\*.bat) do (
    set fname=%%~nF
    if /I not "!fname!"=="alias" (
      echo !fname!
    )
  )
  endlocal
  exit /b
)

REM Check if argument given but no '=' means show that alias
echo %* | findstr "=" >nul
if %errorlevel% neq 0 (
  if exist C:\Aliases\%~1.bat (
    echo %~1 is aliased to:
    type C:\Aliases\%~1.bat | findstr /v /i "@echo off"
  ) else (
    echo No alias named '%~1' found.
  )
  endlocal
  exit /b
)

REM Otherwise, setting an alias: name="command"
set line=%*
for /f "tokens=1* delims==" %%a in ("%line%") do (
  set name=%%a
  set cmd=%%b
)

REM Remove surrounding quotes from the cmd if any
set cmd=%cmd:"=%

REM Write the alias into C:\Aliases
(
  echo @echo off
  REM Use 'call' so that %%* becomes %* at runtime, enabling argument passing
  echo call %cmd% %%*
) > C:\Aliases\%name%.bat

echo Alias "%name%" created for command: %cmd%
endlocal
