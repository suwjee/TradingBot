[CmdletBinding()]
param(
  [ValidateSet('RootResolution', 'MainPolicy', 'ProductionClosure', 'Snapshot', 'Publication')]
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
  & git -C $path checkout --quiet -b main 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Could not initialize fixture main branch.' }
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
  Write-FixtureFile $fixture '.editorconfig' 'root = true'
  Write-FixtureFile $fixture 'candidate/private.pem' (('-----BEGIN ' + 'PRIVATE KEY-----') + "`nprivate-material")
  return $fixture
}

function Commit-Fixture {
  param([string] $Root)
  & git -C $Root add --all
  & git -C $Root -c user.name=Fixture -c user.email=fixture@example.invalid commit --quiet -m fixture
  if ($LASTEXITCODE -ne 0) { throw 'Could not commit Git fixture.' }
  return (& git -C $Root rev-parse HEAD).Trim()
}

function New-FixtureRemote {
  param([string] $Root)
  $remote = Join-Path ([IO.Path]::GetTempPath()) ("tradingbot-release-remote-" + [guid]::NewGuid().ToString('N') + '.git')
  & git init --bare --quiet $remote 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Could not initialize bare Git remote fixture.' }
  & git -C $Root remote add origin $remote 2>$null | Out-Null
  & git -C $Root push --quiet origin HEAD:refs/heads/main 2>$null | Out-Null
  & git -C $Root push --quiet origin HEAD:refs/heads/production 2>$null | Out-Null
  & git -C $Root fetch --quiet origin 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'Could not populate remote Git fixture.' }
  return $remote
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
      'apps/chart/state/data/raw/BaseLine/reference.json',
      '.editorconfig'
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

function Invoke-SnapshotTests {
  Import-Module $script:ModulePath -Force
  $fixture = New-ProductionFixture
  $remote = $null
  try {
    $remote = New-FixtureRemote -Root $fixture.Root
    Write-FixtureFile $fixture.Root 'engineering/docs/intentional-dirty.md' 'valid user-owned dirty work'
    Write-FixtureFile $fixture.Root 'scripts/start.ps1' 'changed source main'
    $sourceSha = Commit-Fixture $fixture.Root
    $tag = 'snapshot-fixture-tag'
    $preflight = Test-ReleasePreflight -Root $fixture.Root -Tag $tag
    Assert-True ($preflight.Errors.Count -eq 0) ("preflight permits dirty active main and missing local production: " + ($preflight.Errors -join '; '))
    & git -C $fixture.Root show-ref --verify --quiet refs/heads/production
    $localProductionExists = ($LASTEXITCODE -eq 0)
    Assert-True (-not $localProductionExists) 'fixture has no local production branch'

    $policy = @{
      Production = @{
        MandatoryPaths = @('scripts/launch.bat', 'scripts/start.ps1', 'apps/chart/package.json', 'apps/chart/package-lock.json', 'apps/chart/vite.config.js', 'apps/chart/index.html', 'apps/chart/review.html', 'engine/bridge/trading_pipeline.py', 'engine/pipeline/detector.py')
        RuntimeRoots = @('apps/chart/src/', 'apps/chart/server/', 'engine/bridge/', 'engine/pipeline/')
        ExcludedPathPatterns = @('apps/chart/state/**', 'apps/chart/tests/**', 'engine/tests/**', 'engineering/**', 'scripts/git/**')
      }
      Sensitive = @{ PathPatterns = @(); ContentPatterns = @(); MaximumScanBytes = 1048576 }
    }
    Write-FixtureFile $fixture.Root 'apps/chart/state/cache/local.json' '{}'
    $sourceSha = Commit-Fixture $fixture.Root
    $fileSet = Get-ProductionFileSet -Root $fixture.Root -MainSha $sourceSha -Policy $policy
    Assert-True (-not ($fileSet.Paths -contains 'apps/chart/state/cache/local.json')) 'closure excludes fixture local state'
    $activeIndexBefore = (& git -C $fixture.Root write-tree).Trim()
    $refsBefore = @(& git -C $fixture.Root show-ref)
    $remoteBefore = @(& git -C $fixture.Root ls-remote origin)
    $snapshot = New-ProductionSnapshot -Root $fixture.Root -SourceMainSha $sourceSha -ProductionBaseSha $preflight.ProductionBaseSha -FileSet $fileSet -CommitMessage 'fixture release' -DryRun
    Assert-True $snapshot.ProductionChanged 'dry run creates a candidate production commit when source differs'
    $snapshotStatePaths = @(Get-GitTreePaths -Root $fixture.Root -Commitish $snapshot.ProductionSha | Where-Object { $_ -like 'apps/chart/state/**' })
    Assert-True ($snapshotStatePaths.Count -eq 0) ("snapshot excludes local state: " + ($snapshotStatePaths -join ', '))
    $validation = Test-ProductionSnapshot -Snapshot $snapshot
    Assert-True ($validation.Errors.Count -eq 0) 'candidate snapshot passes structural validation'
    Remove-TemporaryReleaseContext -Context $snapshot.Context
    Assert-True (-not (Test-Path -LiteralPath $snapshot.Context.WorktreePath)) 'dry-run worktree is cleaned'
    Assert-True ((& git -C $fixture.Root write-tree).Trim() -eq $activeIndexBefore) 'dry-run preserves the active index'
    Assert-True ((@(& git -C $fixture.Root show-ref) -join "`n") -eq ($refsBefore -join "`n")) 'dry-run preserves permanent refs and tags'
    Assert-True ((@(& git -C $fixture.Root ls-remote origin) -join "`n") -eq ($remoteBefore -join "`n")) 'dry-run leaves the remote unchanged'

    $normalSnapshot = New-ProductionSnapshot -Root $fixture.Root -SourceMainSha $sourceSha -ProductionBaseSha $preflight.ProductionBaseSha -FileSet $fileSet -CommitMessage 'fixture release' -DryRun:$false
    & git -C $fixture.Root show-ref --verify --quiet refs/heads/production
    Assert-True ($LASTEXITCODE -ne 0) 'normal preparation keeps local production absent until validation completes'
    Assert-True ((Test-ProductionSnapshot -Snapshot $normalSnapshot).Errors.Count -eq 0) 'normal candidate passes validation before production promotion'
    $promotion = Finalize-ProductionBranch -Root $fixture.Root -Snapshot $normalSnapshot
    Assert-True ((& git -C $fixture.Root rev-parse refs/heads/production).Trim() -eq $normalSnapshot.ProductionSha) 'validated candidate advances local production with guarded ref update'
    Assert-True ($promotion.Upstream -eq 'origin/production') 'promoted production branch tracks origin/production'
    Remove-TemporaryReleaseContext -Context $normalSnapshot.Context

    $divergent = (& git -C $fixture.Root -c user.name=Fixture -c user.email=fixture@example.invalid commit-tree "${sourceSha}^{tree}" -m divergent).Trim()
    & git -C $fixture.Root update-ref refs/heads/production $divergent
    $divergentPreflight = Test-ReleasePreflight -Root $fixture.Root -Tag 'snapshot-divergent'
    Assert-True (@($divergentPreflight.Errors | Where-Object { $_ -match 'diverges' }).Count -gt 0) 'preflight rejects a divergent local production branch'
  } finally {
    if ($fixture -and (Test-Path -LiteralPath $fixture.Root)) { Remove-Item -LiteralPath $fixture.Root -Recurse -Force }
    if ($remote -and (Test-Path -LiteralPath $remote)) { Remove-Item -LiteralPath $remote -Recurse -Force }
  }
}

function New-PublicationFixture {
  $fixture = New-ProductionFixture
  $remote = New-FixtureRemote -Root $fixture.Root
  $base = (& git -C $fixture.Root rev-parse refs/remotes/origin/production).Trim()
  Write-FixtureFile $fixture.Root 'scripts/start.ps1' ('release source ' + [guid]::NewGuid().ToString('N'))
  $main = Commit-Fixture $fixture.Root
  & git -C $fixture.Root branch production $base
  if ($LASTEXITCODE -ne 0) { throw 'Could not create local production fixture branch.' }
  return [pscustomobject]@{ Root = $fixture.Root; Remote = $remote; MainSha = $main; ProductionSha = $base }
}

function Invoke-PublicationTests {
  Import-Module $script:ModulePath -Force
  $fixtures = @()
  try {
    $fixture = New-PublicationFixture
    $fixtures += $fixture
    $inputs = Read-ReleaseInputs -CommitMessage 'fixture release' -ReleaseTag 'fixture-release'
    Assert-True ($inputs.CommitMessage -eq 'fixture release' -and $inputs.ReleaseTag -eq 'fixture-release') 'provided release inputs are accepted unchanged'
    Assert-Throws { Read-ReleaseInputs -CommitMessage '' -ReleaseTag 'fixture-release' -NonInteractive } 'empty noninteractive commit message'
    Assert-Throws { New-ReleaseTag -Root $fixture.Root -Tag 'bad tag' -ProductionSha $fixture.ProductionSha -MainSha $fixture.MainSha } 'invalid tag syntax'
    $tag = New-ReleaseTag -Root $fixture.Root -Tag 'fixture-release' -ProductionSha $fixture.ProductionSha -MainSha $fixture.MainSha
    $tagText = & git -C $fixture.Root cat-file -p refs/tags/fixture-release
    Assert-True ((($tagText -join "`n") -match [regex]::Escape("TradingBot-Main-Source: $($fixture.MainSha)"))) 'annotated tag records source main SHA'
    Assert-True ((& git -C $fixture.Root rev-parse 'fixture-release^{}').Trim() -eq $fixture.ProductionSha) 'annotated tag points to exact production commit'
    Assert-Throws { New-ReleaseTag -Root $fixture.Root -Tag 'fixture-release' -ProductionSha $fixture.ProductionSha -MainSha $fixture.MainSha } 'existing tag is never overwritten'
    $prepared = [pscustomobject]@{ MainSha=$fixture.MainSha; ProductionSha=$fixture.ProductionSha; Tag='fixture-release'; TagObjectSha=$tag.TagObjectSha; RemoteMainSha=$fixture.ProductionSha; RemoteProductionSha=$fixture.ProductionSha; RemoteTagSha=$null }
    $published = Publish-ReleaseRefs -Root $fixture.Root -PreparedRelease $prepared
    Assert-True ($published.Status -eq 'ATOMIC_PASS') 'atomic publication succeeds to fixture remote'
    Assert-True ($published.RemoteMain -eq $fixture.MainSha -and $published.RemoteProduction -eq $fixture.ProductionSha -and $published.RemoteTag -eq $tag.TagObjectSha) 'atomic publication verifies all refs'

    $fallbackFixture = New-PublicationFixture
    $fixtures += $fallbackFixture
    $fallbackTag = New-ReleaseTag -Root $fallbackFixture.Root -Tag 'fixture-fallback' -ProductionSha $fallbackFixture.ProductionSha -MainSha $fallbackFixture.MainSha
    $fallbackPrepared = [pscustomobject]@{ MainSha=$fallbackFixture.MainSha; ProductionSha=$fallbackFixture.ProductionSha; Tag='fixture-fallback'; TagObjectSha=$fallbackTag.TagObjectSha; RemoteMainSha=$fallbackFixture.ProductionSha; RemoteProductionSha=$fallbackFixture.ProductionSha; RemoteTagSha=$null }
    $unsupportedAtomic = { param($root, $gitArgs) if ($gitArgs -contains '--atomic') { return [pscustomobject]@{ ExitCode=1; StdOut=''; StdErr='fatal: the receiving end does not support --atomic push'; Arguments=$gitArgs } }; Invoke-ReleaseGit -Root $root -Arguments $gitArgs }
    $fallback = Publish-ReleaseRefs -Root $fallbackFixture.Root -PreparedRelease $fallbackPrepared -CommandAdapter $unsupportedAtomic
    Assert-True ($fallback.Status -eq 'FALLBACK_PASS') 'unsupported atomic remote uses verified fallback'

    $partialFixture = New-PublicationFixture
    $fixtures += $partialFixture
    $partialTag = New-ReleaseTag -Root $partialFixture.Root -Tag 'fixture-partial' -ProductionSha $partialFixture.ProductionSha -MainSha $partialFixture.MainSha
    $partialPrepared = [pscustomobject]@{ MainSha=$partialFixture.MainSha; ProductionSha=$partialFixture.ProductionSha; Tag='fixture-partial'; TagObjectSha=$partialTag.TagObjectSha; RemoteMainSha=$partialFixture.ProductionSha; RemoteProductionSha=$partialFixture.ProductionSha; RemoteTagSha=$null }
    $partialAdapter = { param($root, $gitArgs) if ($gitArgs -contains '--atomic') { return [pscustomobject]@{ ExitCode=1; StdOut=''; StdErr='fatal: the receiving end does not support --atomic push'; Arguments=$gitArgs } }; if ($gitArgs -contains 'refs/heads/production:refs/heads/production') { return [pscustomobject]@{ ExitCode=1; StdOut=''; StdErr='simulated production rejection'; Arguments=$gitArgs } }; Invoke-ReleaseGit -Root $root -Arguments $gitArgs }
    $partial = Publish-ReleaseRefs -Root $partialFixture.Root -PreparedRelease $partialPrepared -CommandAdapter $partialAdapter
    Assert-True ($partial.Status -eq 'PARTIAL_FAILURE') 'fallback stops and reports a partial publication'
    $remotePartialTag = & git -C $partialFixture.Root ls-remote --exit-code origin refs/tags/fixture-partial
    Assert-True ($LASTEXITCODE -ne 0) 'fallback does not publish tag after a partial branch failure'
  } finally {
    foreach ($fixture in $fixtures) {
      if ($fixture -and (Test-Path -LiteralPath $fixture.Root)) { Remove-Item -LiteralPath $fixture.Root -Recurse -Force }
      if ($fixture -and (Test-Path -LiteralPath $fixture.Remote)) { Remove-Item -LiteralPath $fixture.Remote -Recurse -Force }
    }
  }
}

try {
  switch ($Case) {
    'RootResolution' { Invoke-RootResolutionTests }
    'MainPolicy' { Invoke-MainPolicyTests }
    'ProductionClosure' { Invoke-ProductionClosureTests }
    'Snapshot' { Invoke-SnapshotTests }
    'Publication' { Invoke-PublicationTests }
  }
  $script:Passed++
  Write-Output "PASS: $Case ($script:Passed passed, $script:Failed failed)"
} catch {
  $script:Failed++
  Write-Error "FAIL: $Case - $($_.Exception.Message) at $($_.InvocationInfo.PositionMessage)"
  exit 1
}
