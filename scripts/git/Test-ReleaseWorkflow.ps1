[CmdletBinding()]
param(
  [ValidateSet('RootResolution', 'MainPolicy', 'ProductionClosure')]
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

function Write-FixtureFile {
  param([string] $Root, [string] $RelativePath, [string] $Content = 'fixture')
  $path = Join-Path $Root $RelativePath
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $path) | Out-Null
  [IO.File]::WriteAllText($path, $Content)
}

function New-MainPolicyFixture {
  $fixture = New-RootFixture
  Write-FixtureFile $fixture 'apps/chart/tests/unit/chart.test.mjs'
  Write-FixtureFile $fixture 'engine/tests/unit/engine_test.py'
  Write-FixtureFile $fixture 'engineering/docs/architecture.md'
  Write-FixtureFile $fixture 'engineering/archive/repository-graphify/graph.json' '{}'
  Write-FixtureFile $fixture 'engineering/archive/repository-graphify/cache/ast/cache.json' '{}'
  Write-FixtureFile $fixture 'apps/chart/state/data/raw/BaseLine/reference.json' '{}'
  Write-FixtureFile $fixture 'apps/chart/state/data/raw/acquired.json' '{}'
  Write-FixtureFile $fixture 'apps/chart/state/cache/runtime.json' '{}'
  Write-FixtureFile $fixture 'apps/chart/state/secret/session.dpapi.json' '{}'
  Write-FixtureFile $fixture 'apps/chart/dist/index.html' '<html></html>'
  Write-FixtureFile $fixture 'candidate/private.pem' '-----BEGIN PRIVATE KEY-----\nprivate-material'
  return $fixture
}

function Commit-Fixture {
  param([string] $Root)
  & git -C $Root add --all
  & git -C $Root -c user.name=Fixture -c user.email=fixture@example.invalid commit --quiet -m fixture
  if ($LASTEXITCODE -ne 0) { throw 'Could not commit Git fixture.' }
  return (& git -C $Root rev-parse HEAD).Trim()
}

function New-ProductionFixture {
  $fixture = New-RootFixture
  Write-FixtureFile $fixture 'scripts/launch.bat'
  Write-FixtureFile $fixture 'scripts/start.ps1'
  Write-FixtureFile $fixture 'apps/chart/package-lock.json' '{}'
  Write-FixtureFile $fixture 'apps/chart/vite.config.js' "import './server/api.js';"
  Write-FixtureFile $fixture 'apps/chart/index.html' '<script type="module" src="/src/main.js"></script>'
  Write-FixtureFile $fixture 'apps/chart/review.html' '<link rel="stylesheet" href="/src/review.css"><script type="module" src="/src/review.js"></script>'
  Write-FixtureFile $fixture 'apps/chart/src/main.js' "import {`n  component`n} from './component.js';`nimport './styles.css';`nimport 'lightweight-charts';"
  Write-FixtureFile $fixture 'apps/chart/src/component.js' "import './shared.js'; export const component = true;"
  Write-FixtureFile $fixture 'apps/chart/src/shared.js'
  Write-FixtureFile $fixture 'apps/chart/src/styles.css' "@import './theme.css';"
  Write-FixtureFile $fixture 'apps/chart/src/theme.css'
  Write-FixtureFile $fixture 'apps/chart/src/review.css'
  Write-FixtureFile $fixture 'apps/chart/src/review.js'
  Write-FixtureFile $fixture 'apps/chart/src/unused.js'
  Write-FixtureFile $fixture 'apps/chart/server/api.js' "import '../src/shared.js';"
  Write-FixtureFile $fixture 'apps/chart/server/unused.js'
  Write-FixtureFile $fixture 'engine/bridge/trading_pipeline.py' "from core_utils import helper\n"
  Write-FixtureFile $fixture 'engine/pipeline/detector.py' "from helper_module import helper\n"
  Write-FixtureFile $fixture 'engine/pipeline/core_utils.py' "def helper(): pass\n"
  Write-FixtureFile $fixture 'engine/pipeline/helper_module.py' "def helper(): pass\n"
  Write-FixtureFile $fixture 'engine/pipeline/unused.py'
  $sha = Commit-Fixture $fixture
  return [pscustomobject]@{ Root = $fixture; Sha = $sha }
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

function Invoke-MainPolicyTests {
  Import-Module $script:ModulePath -Force
  $fixture = New-MainPolicyFixture
  try {
    $report = Get-MainPolicyReport -Root $fixture -IndexPath ''
    foreach ($path in @(
      'apps/chart/tests/unit/chart.test.mjs',
      'engine/tests/unit/engine_test.py',
      'engineering/docs/architecture.md',
      'engineering/archive/repository-graphify/graph.json',
      'apps/chart/state/data/raw/BaseLine/reference.json'
    )) {
      Assert-True ($report.Eligible -contains $path) "main policy keeps $path eligible"
    }
    foreach ($path in @(
      'engineering/archive/repository-graphify/cache/ast/cache.json',
      'apps/chart/state/data/raw/acquired.json',
      'apps/chart/state/cache/runtime.json',
      'apps/chart/state/secret/session.dpapi.json',
      'apps/chart/dist/index.html'
    )) {
      Assert-True ($report.Excluded -contains $path) "main policy excludes $path"
    }
    $secret = Test-SensitiveCandidate -Root $fixture -Paths @('candidate/private.pem') -Commitish ''
    Assert-True ($secret.Errors.Count -eq 1) 'private-key marker is rejected'
    Assert-True ($secret.Errors[0] -notmatch 'private-material') 'secret value is redacted'
  } finally {
    if (Test-Path -LiteralPath $fixture) { Remove-Item -LiteralPath $fixture -Recurse -Force }
  }
}

function Invoke-ProductionClosureTests {
  Import-Module $script:ModulePath -Force
  $fixture = New-ProductionFixture
  try {
    $policy = @{
      Production = @{
        MandatoryPaths = @(
          'scripts/launch.bat', 'scripts/start.ps1', 'apps/chart/package.json', 'apps/chart/package-lock.json',
          'apps/chart/vite.config.js', 'apps/chart/index.html', 'apps/chart/review.html', 'engine/bridge/trading_pipeline.py', 'engine/pipeline/detector.py'
        )
        RuntimeRoots = @('apps/chart/src/', 'apps/chart/server/', 'engine/bridge/', 'engine/pipeline/')
        ExcludedPathPatterns = @('apps/chart/state/**', 'apps/chart/tests/**', 'engine/tests/**', 'scripts/git/**')
      }
      Sensitive = @{ PathPatterns = @(); ContentPatterns = @(); MaximumScanBytes = 1048576 }
    }
    $fileSet = Get-ProductionFileSet -Root $fixture.Root -MainSha $fixture.Sha -Policy $policy
    foreach ($path in @('apps/chart/src/main.js', 'apps/chart/src/component.js', 'apps/chart/src/shared.js', 'apps/chart/src/styles.css', 'apps/chart/src/theme.css', 'apps/chart/src/review.css', 'apps/chart/src/review.js', 'apps/chart/server/api.js', 'engine/pipeline/core_utils.py', 'engine/pipeline/helper_module.py')) {
      Assert-True ($fileSet.Paths -contains $path) "closure includes $path"
    }
    foreach ($path in @('apps/chart/src/unused.js', 'apps/chart/server/unused.js', 'engine/pipeline/unused.py')) {
      Assert-True (-not ($fileSet.Paths -contains $path)) "closure excludes unreferenced $path"
      Assert-True ($fileSet.Drift -contains $path) "closure reports drift for $path"
    }
    Assert-True ($fileSet.Errors.Count -eq 0) 'fixture closure has no unresolved imports'
    Assert-True ((Test-ProductionFileSet -FileSet $fileSet -Policy $policy).Errors.Count -eq 0) 'fixture file set passes integrity checks'
  } finally {
    if (Test-Path -LiteralPath $fixture.Root) { Remove-Item -LiteralPath $fixture.Root -Recurse -Force }
  }
}

try {
  switch ($Case) {
    'RootResolution' { Invoke-RootResolutionTests }
    'MainPolicy' { Invoke-MainPolicyTests }
    'ProductionClosure' { Invoke-ProductionClosureTests }
  }
  $script:Passed++
  Write-Output "PASS: $Case ($script:Passed passed, $script:Failed failed)"
} catch {
  $script:Failed++
  Write-Error "FAIL: $Case - $($_.Exception.Message)"
  exit 1
}
