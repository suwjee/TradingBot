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

function Invoke-FakeNode {
  $script:nodeArguments = @($args)
  $script:nodeWorkingDirectory = (Get-Location).Path
  $global:LASTEXITCODE = 0
}

$tokens = $null
$errors = $null
$ast = [Management.Automation.Language.Parser]::ParseFile((Join-Path $repoRoot 'scripts\start.ps1'), [ref]$tokens, [ref]$errors)
Assert-Launcher ($errors.Count -eq 0) 'The launcher must parse in Windows PowerShell.'
foreach ($name in @('Ensure-NpmDependencies', 'Start-DevServer')) {
  $functionDefinition = $ast.Find({
    param($node)
    $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name
  }, $true)
  Assert-Launcher ($null -ne $functionDefinition) "The launcher must define $name."
  . ([scriptblock]::Create($functionDefinition.Extent.Text))
}

try {
  New-InstalledDependencies
  $lockfile = Join-Path $ChartRoot 'package-lock.json'
  $stamp = Join-Path $ChartRoot 'node_modules\.tradingbot-lock-sha256'
  [IO.File]::WriteAllText($lockfile, '{"lockfileVersion":3}')
  [IO.File]::WriteAllText($stamp, (Get-FileHash -LiteralPath $lockfile).Hash)

  Remove-Item -LiteralPath $ViteCommand
  Ensure-NpmDependencies 'Invoke-FakeNpm'
  Assert-Launcher ($script:installCalls.Count -eq 1 -and $script:installCalls[0] -eq 'ci') 'A current lock stamp must not hide a missing Vite CLI.'
  Assert-Launcher (Test-Path -LiteralPath $ViteCommand -PathType Leaf) 'The Vite CLI was not repaired.'
  Ensure-NpmDependencies 'Invoke-FakeNpm'
  Assert-Launcher ($script:installCalls.Count -eq 1) 'A complete warm install must not rerun npm.'

  $originalLocation = (Get-Location).Path
  $originalPython = $env:TRADINGBOT_PYTHON
  $originalProjectRoot = $env:TRADINGBOT_PROJECT_ROOT
  try {
    Start-DevServer 'Invoke-FakeNode' 'fixture python.exe'
    Assert-Launcher ($script:nodeWorkingDirectory -eq $ChartRoot -and (Get-Location).Path -eq $originalLocation) 'Vite must run from the chart directory and restore the caller location.'
    Assert-Launcher ($script:nodeArguments.Count -eq 5 -and $script:nodeArguments[0] -eq $ViteCommand -and
      ($script:nodeArguments[1..4] -join ' ') -eq '--host 0.0.0.0 --configLoader native') 'The launcher must invoke the installed Vite CLI with native config loading.'
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

  $fixtureScripts = Join-Path $fixture 'scripts'
  [void][IO.Directory]::CreateDirectory($fixtureScripts)
  Copy-Item -LiteralPath (Join-Path $repoRoot 'scripts\launch.bat') -Destination $fixtureScripts
  $launchScript = Join-Path $fixtureScripts 'launch.bat'
  [IO.File]::WriteAllText((Join-Path $fixtureScripts 'start.ps1'), @'
if ((Get-Location).Path -ne (Split-Path -Parent $PSScriptRoot)) { exit 15 }
exit 13
'@)
  $processInfo = [Diagnostics.ProcessStartInfo]::new()
  $processInfo.FileName = $env:ComSpec
  $processInfo.Arguments = '/d /s /c ""' + $launchScript + '""'
  $processInfo.WorkingDirectory = [IO.Path]::GetTempPath()
  $processInfo.UseShellExecute = $false
  $processInfo.CreateNoWindow = $true
  $processInfo.RedirectStandardInput = $true
  $processInfo.RedirectStandardOutput = $true
  $processInfo.RedirectStandardError = $true
  $process = [Diagnostics.Process]::Start($processInfo)
  try {
    $process.StandardInput.Close()
    $stdout = $process.StandardOutput.ReadToEndAsync()
    $stderr = $process.StandardError.ReadToEndAsync()
    if (-not $process.WaitForExit(10000)) { $process.Kill(); throw 'The launcher fixture did not exit.' }
    Assert-Launcher ($process.ExitCode -eq 13) "The batch launcher must resolve the checkout and propagate the exit code. $($stdout.Result) $($stderr.Result)"
  } finally { $process.Dispose() }

  Write-Host 'PASS: launcher locked dependency repair, complete warm startup, missing lockfile, native Vite invocation, and batch checkout/exit propagation.'
} finally {
  $tempPrefix = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
  $absoluteFixture = [IO.Path]::GetFullPath($fixture)
  Assert-Launcher ($absoluteFixture.StartsWith($tempPrefix, [StringComparison]::OrdinalIgnoreCase) -and
    (Split-Path -Leaf $absoluteFixture) -cmatch '^tradingbot-launcher-test-[0-9a-f]{32} checkout & \(space\)!$') 'Fixture cleanup is restricted to the test temporary directory.'
  if (Test-Path -LiteralPath $absoluteFixture) { Remove-Item -LiteralPath $absoluteFixture -Recurse -Force }
}
