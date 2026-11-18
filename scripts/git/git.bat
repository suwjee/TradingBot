@echo off
setlocal EnableExtensions DisableDelayedExpansion

title TradingBot Git Manager

set "TB_MENU=%~dp0Git.Menu.ps1"
set "TB_RELEASE=%~dp0Invoke-TradingBotRelease.ps1"
set "TB_POWERSHELL=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
for %%I in ("%~dp0..\..") do set "TB_ROOT=%%~fI"

if /I "%~1"=="-Help" goto :help
if "%~1"=="/?" goto :help
if /I "%~1"=="-ReleaseTag" goto :release
if not exist "%TB_MENU%" (
  echo [FAIL] TradingBot Git Manager files were not found.
  echo Expected: "%TB_MENU%"
  pause
  exit /b 2
)

pushd "%TB_ROOT%" >nul 2>&1
if errorlevel 1 (
  echo [FAIL] Could not enter TradingBot project root: "%TB_ROOT%"
  pause
  exit /b 3
)

"%TB_POWERSHELL%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%TB_MENU%" %*
set "TB_GIT_RC=%ERRORLEVEL%"
popd

if not "%TB_GIT_RC%"=="0" (
  echo.
  echo [FAIL] TradingBot Git Manager exited with code %TB_GIT_RC%.
  pause
)

exit /b %TB_GIT_RC%

:help
echo git.bat
echo   Open the interactive Git Manager.
echo git.bat -ReleaseTag TAG -CommitMessage MESSAGE [-ReleaseTitle TITLE] [-ReleaseNotesFile PATH] [-DryRun] [-VerboseReport]
echo   Validate and publish main, production, the annotated tag and a GitHub Release.
echo   Pass -ReleaseTag first. Quote values containing spaces.
echo   -ReleaseTitle sets the GitHub Release title. The tag is used by default.
echo   -ReleaseNotesFile reads UTF-8 Markdown from a path relative to the caller.
echo   Use -DryRun to validate both candidate trees without publication.
exit /b 0

:release
if not exist "%TB_RELEASE%" (
  echo [FAIL] The TradingBot release command was not found.
  exit /b 2
)
"%TB_POWERSHELL%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%TB_RELEASE%" -NonInteractive %*
exit /b %ERRORLEVEL%
