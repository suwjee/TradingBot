@echo off
setlocal EnableExtensions

title TradingBot Git Manager

for %%I in ("%~dp0..\..") do set "TB_ROOT=%%~fI"
if exist "%TB_ROOT%\scripts\git\Git.Menu.ps1" if exist "%TB_ROOT%\AGENTS.md" goto :root_found

echo [FAIL] TradingBot Git Manager files were not found.
echo Expected: %TB_ROOT%\scripts\git\Git.Menu.ps1
echo.
pause
exit /b 2

:root_found
pushd "%TB_ROOT%" >nul 2>&1
if errorlevel 1 (
  echo [FAIL] Could not enter TradingBot project root: %TB_ROOT%
  pause
  exit /b 3
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%TB_ROOT%\scripts\git\Git.Menu.ps1"
set "TB_GIT_RC=%ERRORLEVEL%"
popd

if not "%TB_GIT_RC%"=="0" (
  echo.
  echo [FAIL] TradingBot Git Manager exited with code %TB_GIT_RC%.
  pause
)

exit /b %TB_GIT_RC%
