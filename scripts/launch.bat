@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "START_SCRIPT=%~dp0start.ps1"
if not exist "%START_SCRIPT%" (
  echo [ERROR] Missing scripts\start.ps1
  pause
  exit /b 2
)

rem Parse the exit before launch so an accepted update can replace this file.
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%START_SCRIPT%" %* & call exit /b %%errorlevel%%
