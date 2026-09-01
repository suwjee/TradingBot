@echo off
setlocal
chcp 65001 >nul
pushd "%~dp0"
if not exist "%~dp0Start-TradingBot.ps1" (
    echo [ERROR] Start-TradingBot.ps1 was not found next to launcher.bat.
    echo Expected: "%~dp0Start-TradingBot.ps1"
    pause
    popd
    exit /b 2
)
%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-TradingBot.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo [ERROR] TradingBot stopped with exit code %EXIT_CODE%.
    pause
)
popd
endlocal
exit /b %EXIT_CODE%
