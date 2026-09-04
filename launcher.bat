@echo off
setlocal EnableExtensions
chcp 65001 >nul
set "PROJECT_ROOT=%~dp0"
if not exist "%PROJECT_ROOT%Start-TradingBot.ps1" (
  echo [ERROR] Missing Start-TradingBot.ps1
  pause
  exit /b 2
)
if not exist "%PROJECT_ROOT%lightweight-charts\package.json" (
  echo [ERROR] Missing lightweight-charts\package.json
  pause
  exit /b 2
)
pushd "%PROJECT_ROOT%"
%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_ROOT%Start-TradingBot.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
popd
if not "%EXIT_CODE%"=="0" (
  echo.
  echo [ERROR] TradingBot stopped with exit code %EXIT_CODE%.
  pause
)
endlocal & exit /b %EXIT_CODE%
