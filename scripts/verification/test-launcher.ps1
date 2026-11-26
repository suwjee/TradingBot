$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$fixture = Join-Path ([IO.Path]::GetTempPath()) ('tradingbot-launcher-test-' + [guid]::NewGuid().ToString('N') + ' checkout & (space)!')
$Root = $fixture
$ChartRoot = Join-Path $fixture 'apps\chart'
$ViteCommand = Join-Path $ChartRoot 'node_modules\vite\bin\vite.js'
$script:installCalls = [Collections.Generic.List[string]]::new()

function Assert-Launcher([bool]$Condition, [string]$Message) {
  if (-not $Condition) { throw $Message }
}

function Write-Step([string]$Text, [ConsoleColor]$Color = 'Gray') {}
function Set-Clipboard {
  [CmdletBinding()]
  param([string]$Value)
  $script:copiedLauncherUrl = $Value
}
function Invoke-WebRequest {
  [CmdletBinding()]
  param([string]$Uri, [switch]$UseBasicParsing, [int]$TimeoutSec, [int]$MaximumRedirection)
  $script:healthProbeUrl = $Uri
  return [pscustomobject]@{ StatusCode = 200 }
}
function Show-LauncherFrame {}
function Write-LauncherEvent([string]$Kind, [string]$Value, [string]$Color = 'Gray') {
  if ($Kind -eq 'Ready') { $script:readyPort = $Value }
}

function New-InstalledDependencies {
  foreach ($relative in @('vite\package.json', 'vite\bin\vite.js', 'lightweight-charts\package.json', 'playwright-core\package.json')) {
    $file = Join-Path $ChartRoot ('node_modules\' + $relative)
    [void][IO.Directory]::CreateDirectory((Split-Path -Parent $file))
    [IO.File]::WriteAllText($file, '{}')
  }
}

function Invoke-FakeNpm {
  $script:installCalls.Add(($args -join ' '))
  New-InstalledDependencies
  $global:LASTEXITCODE = 0
}

$script:OnWindows = [Environment]::OSVersion.Platform -eq 'Win32NT'
$script:checks = @('Project', 'Node', 'Python', 'Python packages', 'Chart packages', 'Local state')
$script:screenView = @{ Mode = 'Activity'; Offset = 0 }
$script:activity = @('first', 'second', 'third', 'fourth', 'fifth')
$script:updateProgress = @{ Stage = ''; Complete = 0; Download = -1 }
$script:runner = @{
  Version = 'v1.0.0'; Latest = 'v1.1.0'; Internet = 'Online'; Update = 'Press U to install'
  UpdateNotice = 'UPDATE AVAILABLE'; Server = 'Ready'
  Project = 'Ready'; Node = 'Node v22.12.0'; Python = 'Python 3.12'
  'Python packages' = 'Ready'; 'Chart packages' = 'Ready'; 'Local state' = 'Ready'
}

function Invoke-FixtureGit([string]$Directory, [string[]]$Arguments) {
  $result = Invoke-LauncherGit $Directory $Arguments
  Assert-Launcher ($result.ExitCode -eq 0) "Fixture Git failed: $($Arguments -join ' ') $($result.Error)"
  return $result.Output.Trim()
}

function Test-ProductionUpdate {
  $upstream = Join-Path $fixture 'upstream'
  $installed = Join-Path $fixture 'installed'
  [void][IO.Directory]::CreateDirectory((Join-Path $upstream 'apps\chart\src'))
  $source = Join-Path $upstream 'apps\chart\src'
  $original = Join-Path $source 'old.js'
  [IO.File]::WriteAllText($original, 'before')
  [IO.File]::WriteAllText((Join-Path $source 'obsolete.js'), 'obsolete')
  [void](Invoke-FixtureGit $upstream @('init', '-b', 'production'))
  [void](Invoke-FixtureGit $upstream @('add', '.'))
  [void](Invoke-FixtureGit $upstream @('-c', 'user.name=Launcher Test', '-c', 'user.email=test@invalid', 'commit', '-m', 'Release v1.0.0'))
  [void](Invoke-FixtureGit $fixture @('clone', '--branch', 'production', $upstream, $installed))
  $before = Invoke-FixtureGit $installed @('rev-parse', 'HEAD')
  [IO.File]::WriteAllText($original, 'after')
  [IO.File]::WriteAllText((Join-Path $source 'new.js'), 'new')
  Remove-Item -LiteralPath (Join-Path $source 'obsolete.js')
  [void](Invoke-FixtureGit $upstream @('add', '-A'))
  [void](Invoke-FixtureGit $upstream @('-c', 'user.name=Launcher Test', '-c', 'user.email=test@invalid', 'commit', '-m', 'Release v1.1.0'))
  [void](Invoke-FixtureGit $upstream @('-c', 'user.name=Launcher Test', '-c', 'user.email=test@invalid', 'tag', '-a', 'v1.1.0', '-m', 'Release'))

  $state = Join-Path $installed 'apps\chart\state'
  foreach ($relative in @('data\raw\fixture.csv', 'secret\session.json', 'cache\saved.json', 'logs\launcher.log')) {
    $file = Join-Path $state $relative
    [void][IO.Directory]::CreateDirectory((Split-Path -Parent $file))
    [IO.File]::WriteAllText($file, $relative)
  }
  $candidate = Get-ProductionCandidate $installed
  Assert-Launcher ($candidate.Version -eq 'v1.1.0' -and $candidate.Commit -ne $before) 'The candidate must come from the production tip and its exact tag.'
  Assert-Launcher ((Get-LauncherCheckout $installed).Version -eq 'v1.0.0') 'The installed release may be identified from its release commit before tags are downloaded.'
  Assert-Launcher ((Invoke-FixtureGit $installed @('rev-parse', 'HEAD')) -eq $before) 'Checking or declining an update must leave the installed version intact.'

  $localSource = Join-Path $installed 'apps\chart\src'
  $localOld = Join-Path $localSource 'old.js'
  [IO.File]::WriteAllText($localOld, 'local edit')
  $failure = try { $null = Get-ProductionUpdatePlan $installed $before $candidate.Commit } catch { $_ }
  Assert-Launcher ($failure.Exception.Message -match 'local changes' -and [IO.File]::ReadAllText($localOld) -eq 'local edit') 'The updater must keep local source edits intact.'
  [IO.File]::WriteAllText($localOld, 'before')

  $collision = Join-Path $localSource 'new.js'
  [IO.File]::WriteAllText($collision, 'local file')
  [IO.File]::WriteAllText((Join-Path $installed '.git\info\exclude'), "apps/chart/src/new.js`n")
  $failure = try { $null = Get-ProductionUpdatePlan $installed $before $candidate.Commit } catch { $_ }
  Assert-Launcher ($failure.Exception.Message -match 'local path' -and [IO.File]::ReadAllText($collision) -eq 'local file') 'The updater must keep ignored files at incoming source paths.'
  Remove-Item -LiteralPath $collision

  $plan = Get-ProductionUpdatePlan $installed $before $candidate.Commit
  Assert-Launcher ($plan.Count -eq 3) 'The plan must cover additions, modifications, and deletions.'
  Install-ProductionUpdate $installed $before $candidate.Commit
  Assert-Launcher ((Invoke-FixtureGit $installed @('rev-parse', 'HEAD')) -eq $candidate.Commit) 'An accepted update must advance production to the reviewed commit.'
  Assert-Launcher ([IO.File]::ReadAllText($localOld) -eq 'after' -and [IO.File]::ReadAllText($collision) -eq 'new' -and
    -not (Test-Path -LiteralPath (Join-Path $localSource 'obsolete.js'))) 'The installed source files must match the updated release.'
  foreach ($relative in @('data\raw\fixture.csv', 'secret\session.json', 'cache\saved.json', 'logs\launcher.log')) {
    Assert-Launcher ([IO.File]::ReadAllText((Join-Path $state $relative)) -eq $relative) "The update changed workstation data at $relative."
  }

  $unexpectedState = Join-Path $upstream 'apps\chart\state\cache'
  [void][IO.Directory]::CreateDirectory($unexpectedState)
  [IO.File]::WriteAllText((Join-Path $unexpectedState 'incoming.json'), 'must not install')
  [void](Invoke-FixtureGit $upstream @('add', '.'))
  [void](Invoke-FixtureGit $upstream @('-c', 'user.name=Launcher Test', '-c', 'user.email=test@invalid', 'commit', '-m', 'Invalid release'))
  $unsafe = Get-ProductionCandidate $installed
  $failure = try { $null = Get-ProductionUpdatePlan $installed $candidate.Commit $unsafe.Commit } catch { $_ }
  Assert-Launcher ($failure.Exception.Message -match 'protected' -and
    -not (Test-Path -LiteralPath (Join-Path $state 'cache\incoming.json'))) 'The updater must reject incoming files anywhere under workstation state.'
}

$tokens = $null
$errors = $null
$ast = [Management.Automation.Language.Parser]::ParseFile((Join-Path $repoRoot 'scripts\start.ps1'), [ref]$tokens, [ref]$errors)
Assert-Launcher ($errors.Count -eq 0) 'The launcher must parse in Windows PowerShell.'
foreach ($name in @('Get-LauncherLayout', 'Get-LauncherShortcutRows', 'Get-LauncherAddresses', 'Copy-LauncherLocalUrl', 'Test-LauncherHttp', 'Get-LauncherKeyName', 'Read-LauncherKey', 'Set-LauncherViewKey', 'Write-NativeLog',
    'New-LauncherProcessInfo', 'Stop-LauncherProcess', 'Ensure-NpmDependencies', 'Start-DevServer',
    'Find-SupportedPython', 'ConvertTo-LauncherProcessArguments', 'Invoke-LauncherGit', 'Get-ProductionCandidate', 'Get-LauncherCheckout',
    'Assert-ProductionCheckout', 'Get-ProductionUpdatePlan', 'Install-ProductionUpdate')) {
  $functionDefinition = $ast.Find({
    param($node)
    $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name
  }, $true)
  Assert-Launcher ($null -ne $functionDefinition) "The launcher must define $name."
  . ([scriptblock]::Create($functionDefinition.Extent.Text))
}

try {
  $addresses = @('Local  http://localhost:5188/', 'LAN    http://10.0.0.1:5188/')
  $rows = @(Get-LauncherLayout 23 $addresses @('test activity') 'Server')
  Assert-Launcher ($rows.Count -eq 23 -and $rows[-6].Text -match '^\s*-+\s*$' -and
    $rows[-4].Text -match 'localhost:5188' -and $rows[-3].Text -match '10.0.0.1:5188' -and
    $rows[-2].Text -match 'Restart' -and $rows[-1].Text -match 'End') 'A divider must separate the fixed addresses and controls from the activity pane.'
  $narrowRows = @(Get-LauncherLayout 18 $addresses @('test activity') 'Server' 48)
  $shortcuts = @(Get-LauncherShortcutRows 'Server' 48)
  Assert-Launcher ($narrowRows.Count -eq 18 -and ($shortcuts | Measure-Object Length -Maximum).Maximum -lt 48) 'The narrow footer must fit without scrolling.'
  foreach ($key in @('U', 'R', 'C', 'H', 'D', 'E', 'PgUp/PgDn', 'End', 'Q/Ctrl+C')) {
    Assert-Launcher (($shortcuts -join ' ') -match ('\[' + [regex]::Escape($key) + '\]')) "The key legend must show $key even when it wraps."
  }
  $script:runner.LocalUrl = 'http://localhost:5188/'
  Copy-LauncherLocalUrl
  Assert-Launcher ($script:copiedLauncherUrl -eq $script:runner.LocalUrl -and $script:screenView.Message -eq 'Local URL copied') 'Copy URL must use the actual bound URL and confirm the result in the footer.'
  Test-LauncherHttp
  Assert-Launcher ($script:healthProbeUrl -eq 'http://127.0.0.1:5188/' -and $script:screenView.Message -match '^HTTP 200 in \d+ ms$') 'Health check must probe the actual chart port and report its result in the footer.'
  $script:screenView.Message = ''
  Assert-Launcher (($rows.Text -match 'Installed\s+v1\.0\.0.+GitHub production\s+v1\.1\.0') -and
    ($rows | Where-Object { $_.Text -match 'UPDATE AVAILABLE' -and $_.Style -eq '1;93' })) 'The version strip must show both versions and highlight an available update.'
  $script:updateProgress = @{ Stage = 'Downloading production'; Complete = 0; Download = 45 }
  $transferRows = @(Get-LauncherLayout 23 @('Local http://localhost:5188/') @() 'U  Update')
  Assert-Launcher (($transferRows.Text -match 'Download\s+\[={9}\.{11}\]\s+45%') -and
    ($transferRows.Text -match 'Update\s+\[\.{20}\]\s+0%')) 'The progress bars must distinguish the reported download and completed update steps.'
  $script:updateProgress = @{ Stage = ''; Complete = 0; Download = -1 }
  $events = @(
    @{ Text = 'regular message'; Style = '37'; IsIssue = $false }
    @{ Text = 'fixture warning'; Style = '93'; IsIssue = $true }
  )
  Set-LauncherViewKey 'E'
  $issueRows = @(Get-LauncherLayout 23 @('Local http://localhost:5188/') $events 'R  Restart')
  Assert-Launcher (($issueRows.Text -match 'fixture warning') -and -not ($issueRows.Text -match 'regular message')) 'Issue view must include warnings and omit regular activity.'
  Set-LauncherViewKey 'D'
  $detailRows = @(Get-LauncherLayout 18 @('Local http://localhost:5188/') $events 'R  Restart')
  Assert-Launcher (($detailRows.Text -match 'DETAILS') -and ($detailRows.Text -match [regex]::Escape($Root))) 'Details must show the checkout even in a compact terminal.'
  Set-LauncherViewKey 'D'
  Set-LauncherViewKey 'PageUp'
  Assert-Launcher ($script:screenView.Offset -eq 4) 'PageUp must scroll the log pane upward.'
  Set-LauncherViewKey 'PageDown'
  Assert-Launcher ($script:screenView.Offset -eq 0) 'PageDown must scroll the log pane downward.'
  Set-LauncherViewKey 'PageUp'
  Set-LauncherViewKey 'End'
  Assert-Launcher ($script:screenView.Offset -eq 0) 'End must return the log pane to live activity.'
  foreach ($letter in @('u', 'r', 'c', 'h', 'q', 'd', 'e')) {
    $inputKey = [ConsoleKeyInfo]::new([char]$letter, [Enum]::ToObject([ConsoleKey], 0), $false, $false, $false)
    Assert-Launcher ((Get-LauncherKeyName $inputKey) -ceq $letter.ToUpperInvariant()) 'Printable terminal input must work without a virtual-key code.'
  }
  Test-ProductionUpdate
  $fixtureBin = Join-Path $fixture 'runtime-bin'
  [void][IO.Directory]::CreateDirectory($fixtureBin)
  [IO.File]::WriteAllLines((Join-Path $fixtureBin 'python.cmd'), @('@echo off', 'echo Python was not found 1>&2', 'exit /b 9'))
  [IO.File]::WriteAllLines((Join-Path $fixtureBin 'py.cmd'), @('@echo off', 'echo Python 3.12.4', 'exit /b 0'))
  $previousPath = $env:Path
  try {
    $env:Path = $fixtureBin
    $runtime = Find-SupportedPython
    Assert-Launcher ($runtime.Path -eq (Join-Path $fixtureBin 'py.cmd')) 'Python discovery must continue after a broken executable.'
  } finally { $env:Path = $previousPath }

  New-InstalledDependencies
  $lockfile = Join-Path $ChartRoot 'package-lock.json'
  $stamp = Join-Path $ChartRoot 'node_modules\.tradingbot-lock-sha256'
  [IO.File]::WriteAllText($lockfile, '{"lockfileVersion":3}')
  [IO.File]::WriteAllText($stamp, (Get-FileHash -LiteralPath $lockfile).Hash)

  Remove-Item -LiteralPath $ViteCommand
  Ensure-NpmDependencies 'Invoke-FakeNpm'
  Assert-Launcher ($script:installCalls.Count -eq 1 -and $script:installCalls[0] -eq 'ci --include=dev') 'A missing Vite CLI must trigger a locked install that includes the development dependencies.'
  Assert-Launcher (Test-Path -LiteralPath $ViteCommand -PathType Leaf) 'The Vite CLI was not repaired.'
  Ensure-NpmDependencies 'Invoke-FakeNpm'
  Assert-Launcher ($script:installCalls.Count -eq 1) 'A complete warm install must not rerun npm.'

  $originalLocation = (Get-Location).Path
  $originalPython = $env:TRADINGBOT_PYTHON
  $originalProjectRoot = $env:TRADINGBOT_PROJECT_ROOT
  $nodePath = (Get-Command node -CommandType Application | Select-Object -First 1).Source
  $script:screenActive = $false
  $ServerProgram = @'
import { basename } from 'node:path';
if (basename(process.cwd()) !== 'chart' || process.env.TRADINGBOT_PYTHON !== 'fixture python.exe') process.exit(15);
console.log('TRADINGBOT_VITE_READY 5188');
'@
  try {
    Assert-Launcher ((Start-DevServer $nodePath 'fixture python.exe') -eq 'Exited' -and (Get-Location).Path -eq $originalLocation) 'Vite must run from the chart directory and preserve the caller location.'
    Assert-Launcher ($script:readyPort -eq '5188') 'The launcher must forward the actual bound port to the dashboard.'
    Assert-Launcher ($env:TRADINGBOT_PYTHON -eq 'fixture python.exe' -and $env:TRADINGBOT_PROJECT_ROOT -eq $root) 'The launcher must pass its runtime and checkout context to Vite.'
  } finally {
    $env:TRADINGBOT_PYTHON = $originalPython
    $env:TRADINGBOT_PROJECT_ROOT = $originalProjectRoot
  }

  Remove-Item -LiteralPath $lockfile
  $failure = $null
  try { Ensure-NpmDependencies 'Invoke-FakeNpm' } catch { $failure = $_ }
  Assert-Launcher ($null -ne $failure -and $failure.Exception.Message -match 'package-lock\.json') 'A missing lockfile must fail explicitly.'
  Assert-Launcher ($script:installCalls.Count -eq 1) 'The launcher must not fall back to npm install.'

  if ($script:OnWindows) {
    $fixtureScripts = Join-Path $fixture 'scripts'
    [void][IO.Directory]::CreateDirectory($fixtureScripts)
    Copy-Item -LiteralPath (Join-Path $repoRoot 'scripts/launch.bat') -Destination $fixtureScripts
    [IO.File]::WriteAllText((Join-Path $fixtureScripts 'start.ps1'), @'
param([switch]$Console, [switch]$Loopback)
if (-not ($Console -and $Loopback)) { exit 15 }
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'launch.bat'), "@echo off`r`nexit /b 99`r`n")
exit 13
'@)
    $launchScript = Join-Path $fixtureScripts 'launch.bat'
    $processInfo = New-LauncherProcessInfo $env:ComSpec ([IO.Path]::GetTempPath()) @()
    $processInfo.Arguments = '/d /s /c ""' + $launchScript + '" -Console -Loopback"'
    $process = [Diagnostics.Process]::Start($processInfo)
    try {
      $stdout = $process.StandardOutput.ReadToEndAsync()
      $stderr = $process.StandardError.ReadToEndAsync()
      if (-not $process.WaitForExit(10000)) { throw 'The batch launcher fixture did not exit.' }
      Assert-Launcher ($process.ExitCode -eq 13) "The batch launcher must resolve its script from another directory and forward its arguments and exit code even when an update replaces it. $($stdout.Result) $($stderr.Result)"
      Assert-Launcher ([IO.File]::ReadAllText($launchScript).Contains('exit /b 99')) 'The batch launcher fixture must replace the running batch file.'
    } finally {
      Stop-LauncherProcess $process
      $process.Dispose()
    }
  }
  Write-Host 'PASS: terminal layout, production update and state protection, dependencies, actual Vite port, and Windows batch entry.'
} finally {
  $tempPrefix = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
  $absoluteFixture = [IO.Path]::GetFullPath($fixture)
  Assert-Launcher ($absoluteFixture.StartsWith($tempPrefix, [StringComparison]::OrdinalIgnoreCase) -and
    (Split-Path -Leaf $absoluteFixture) -cmatch '^tradingbot-launcher-test-[0-9a-f]{32} checkout & \(space\)!$') 'Fixture cleanup is restricted to the test temporary directory.'
  if (Test-Path -LiteralPath $absoluteFixture) { Remove-Item -LiteralPath $absoluteFixture -Recurse -Force }
}
