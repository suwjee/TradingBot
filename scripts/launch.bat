@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul

for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI\"
set "START_SCRIPT=%PROJECT_ROOT%scripts\start.ps1"

if not exist "%START_SCRIPT%" (
  echo [ERROR] Missing scripts\start.ps1
  pause
  exit /b 2
)

pushd "%PROJECT_ROOT%" >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Could not enter the TradingBot project directory.
  pause
  exit /b 3
)
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%START_SCRIPT%"
set "EXIT_CODE=%ERRORLEVEL%"
popd

if not "%EXIT_CODE%"=="0" (
  echo.
  echo [ERROR] TradingBot stopped with exit code %EXIT_CODE%.
  pause
)

endlocal & exit /b %EXIT_CODE%
