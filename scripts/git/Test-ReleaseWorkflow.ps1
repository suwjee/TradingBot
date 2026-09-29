[CmdletBinding()]
param(
  [ValidateSet('RootResolution')]
  [string] $Case = 'RootResolution'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:Passed = 0
$script:Failed = 0
$script:ModulePath = Join-Path $PSScriptRoot 'Release.Workflow.psm1'

function Assert-True {
  param([bool] $Condition, [string] $Message)
  if (-not $Condition) { throw "Assertion failed: $Message" }
}

function Assert-Throws {
  param([scriptblock] $Action, [string] $Message)
  try {
    & $Action
  } catch {
    return
  }
  throw "Assertion failed: expected failure for $Message"
}

function New-RootFixture {
  $path = Join-Path ([IO.Path]::GetTempPath()) ("tradingbot-release-test-" + [guid]::NewGuid().ToString('N'))
  New-Item -ItemType Directory -Force -Path (Join-Path $path 'apps\chart') | Out-Null
  New-Item -ItemType Directory -Force -Path (Join-Path $path 'engine\bridge') | Out-Null
  New-Item -ItemType Directory -Force -Path (Join-Path $path 'scripts\git') | Out-Null
  [IO.File]::WriteAllText((Join-Path $path 'AGENTS.md'), '# fixture')
  [IO.File]::WriteAllText((Join-Path $path 'apps\chart\package.json'), '{}')
  [IO.File]::WriteAllText((Join-Path $path 'engine\bridge\trading_pipeline.py'), '# fixture')
  [IO.File]::WriteAllText((Join-Path $path 'scripts\git\Invoke-TradingBotRelease.ps1'), '# fixture')
  & git -C $path init --quiet
  if ($LASTEXITCODE -ne 0) { throw 'Could not initialize Git fixture.' }
  return $path
}

function Invoke-RootResolutionTests {
  Import-Module $script:ModulePath -Force
  $fixture = New-RootFixture
  try {
    $scriptPath = Join-Path $fixture 'scripts\git\Invoke-TradingBotRelease.ps1'
    $resolved = Resolve-TradingBotProjectRoot -ScriptPath $scriptPath
    Assert-True ($resolved -eq [IO.Path]::GetFullPath($fixture)) 'valid fixture root resolves from script location'

    Remove-Item -LiteralPath (Join-Path $fixture 'AGENTS.md') -Force
    Assert-Throws { Resolve-TradingBotProjectRoot -ScriptPath $scriptPath } 'missing AGENTS marker'

    Assert-Throws { Resolve-TradingBotProjectRoot -ScriptPath 'D:\My-Projects\TradingBot\scripts\git\Invoke-TradingBotRelease.ps1' } 'legacy path is never accepted'
  } finally {
    if (Test-Path -LiteralPath $fixture) { Remove-Item -LiteralPath $fixture -Recurse -Force }
  }
}

try {
  switch ($Case) {
    'RootResolution' { Invoke-RootResolutionTests }
  }
  $script:Passed++
  Write-Output "PASS: $Case ($script:Passed passed, $script:Failed failed)"
} catch {
  $script:Failed++
  Write-Error "FAIL: $Case - $($_.Exception.Message)"
  exit 1
}
