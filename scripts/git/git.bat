@echo off
setlocal EnableExtensions DisableDelayedExpansion

set "TB_POWERSHELL=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

if /I "%~1"=="-Help" goto :help
if "%~1"=="/?" goto :help
if not exist "%TB_POWERSHELL%" (
  echo [FAIL] Windows PowerShell was not found. 1>&2
  exit /b 2
)
if "%~1"=="" goto :menu
if /I "%~1"=="-LoadFunctionsOnly" goto :menu

:release
set "TB_SCRIPT=%~dp0Invoke-TradingBotRelease.ps1"
if not exist "%TB_SCRIPT%" (
  echo [FAIL] TradingBot release command was not found: "%TB_SCRIPT%" 1>&2
  exit /b 2
)
"%TB_POWERSHELL%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%TB_SCRIPT%" -NonInteractive %*
exit /b %ERRORLEVEL%

:menu
title TradingBot Git Manager
set "TB_SCRIPT=%~dp0Git.Menu.ps1"
if not exist "%TB_SCRIPT%" (
  echo [FAIL] TradingBot Git Manager was not found: "%TB_SCRIPT%" 1>&2
  if "%~1"=="" pause
  exit /b 2
)
"%TB_POWERSHELL%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%TB_SCRIPT%" %*
set "TB_GIT_RC=%ERRORLEVEL%"
if not "%TB_GIT_RC%"=="0" (
  echo [FAIL] TradingBot Git Manager exited with code %TB_GIT_RC%. 1>&2
  if "%~1"=="" pause
)
exit /b %TB_GIT_RC%

:help
echo git.bat
echo   Open the interactive Git Manager.
echo git.bat -ReleaseTag TAG -CommitMessage MESSAGE [-ReleaseTitle TITLE] [-ReleaseNotesFile PATH] [-DryRun] [-VerboseReport]
echo   Validate and publish main, production, the annotated tag and a GitHub Release.
echo   Release options can appear in any order. Quote values containing spaces.
echo   -ReleaseTitle sets the GitHub Release title. The tag is used by default.
echo   -ReleaseNotesFile reads UTF-8 Markdown from a path relative to the caller.
echo   Use -DryRun to validate both candidate trees without publication.
echo   Main includes project and engineering files. Production includes runtime files.
exit /b 0
