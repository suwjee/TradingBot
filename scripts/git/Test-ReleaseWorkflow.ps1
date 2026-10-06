[CmdletBinding()]
param(
  [ValidateSet('All', 'RootResolution', 'MainPolicy', 'ProductionClosure', 'Snapshot', 'Publication', 'MenuSafety', 'Documentation')]
  [string] $Case = 'All'
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

function Remove-TestFixturePath {
  param([string] $Path)
  if ([string]::IsNullOrWhiteSpace($Path)) { return }
  $target = [IO.Path]::GetFullPath($Path)
  $temporaryRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
  $leaf = Split-Path -Leaf $target
  Assert-True ($target.StartsWith($temporaryRoot, [StringComparison]::OrdinalIgnoreCase) -and $leaf -match '^tradingbot-release-(?:test-[0-9a-f]{32}|remote-[0-9a-f]{32}\.git)$') 'fixture cleanup stays inside the named temporary directory'
  if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Recurse -Force }
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
  Write-FixtureFile $fixture '.gitignore' "engineering/docs/hidden.md`n"
  Write-FixtureFile $fixture 'apps/chart/tests/unit/chart.test.mjs'
  Write-FixtureFile $fixture 'engine/tests/unit/engine_test.py'
  Write-FixtureFile $fixture 'engineering/docs/architecture.md'
  Write-FixtureFile $fixture 'engineering/docs/hidden.md'
  Write-FixtureFile $fixture 'engineering/archive/repository-graphify/graph.json' '{}'
  Write-FixtureFile $fixture 'engineering/archive/repository-graphify/graph.html' '<html>historical visualization</html>'
  Write-FixtureFile $fixture 'engineering/archive/repository-graphify/cache/ast/cache.json' '{}'
  Write-FixtureFile $fixture 'graphify-out/cache/stat-index.json' '{}'
  Write-FixtureFile $fixture 'apps/chart/.vite/deps/package.json' '{}'
  Write-FixtureFile $fixture 'engineering/archive/repository-graphify/rebuild/raw-run/.graphify_extract.json' '{}'
  Write-FixtureFile $fixture 'engineering/archive/repository-graphify/rebuild/raw-run/GRAPH_REPORT.md' 'meaningful report'
  Write-FixtureFile $fixture 'apps/chart/state/data/raw/BaseLine/reference.json' '{}'
  Write-FixtureFile $fixture 'apps/chart/state/data/raw/acquired.json' '{}'
  Write-FixtureFile $fixture 'apps/chart/state/cache/runtime.json' '{}'
  Write-FixtureFile $fixture 'apps/chart/state/secret/session.dpapi.json' '{}'
  Write-FixtureFile $fixture 'apps/chart/dist/index.html' '<html></html>'
  Write-FixtureFile $fixture 'engineering/verification/regenerated-artifacts/dist/index.html' '<html></html>'
  Write-FixtureFile $fixture 'apps/chart/state/data/raw/BaseLine/temp/partial.json' '{}'
  Write-FixtureFile $fixture 'engineering/verification/regenerated-artifacts/node_modules/package/index.js' 'rebuildable dependency'
  Write-FixtureFile $fixture 'node_modules/package/index.js' 'root dependency installation'
  Write-FixtureFile $fixture 'working.tmp' 'disposable temporary file'
  Write-FixtureFile $fixture '.editorconfig' 'root = true'
  Write-FixtureFile $fixture '.env' 'TOKEN=fixture'
  Write-FixtureFile $fixture 'candidate/private.pem' (('-----BEGIN ' + 'PRIVATE KEY-----') + "`nprivate-material")
  Write-FixtureFile $fixture 'candidate/large.txt' (('x' * 1048576) + '-----BEGIN ' + 'PRIVATE KEY-----')
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
    Assert-True ((Resolve-TradingBotProjectRoot -ScriptPath $scriptPath) -eq $resolved) 'AGENTS.md is optional in a valid checkout'
    Remove-Item -LiteralPath (Join-Path $fixture 'apps/chart') -Recurse -Force
    Assert-Throws { Resolve-TradingBotProjectRoot -ScriptPath $scriptPath } 'missing runtime project marker'

    Assert-Throws { Resolve-TradingBotProjectRoot -ScriptPath (Join-Path $fixture 'scripts\git\missing.ps1') } 'missing release script is rejected'
  } finally {
    Remove-TestFixturePath $fixture
  }
}

function Invoke-MainPolicyTests {
  Import-Module $script:ModulePath -Force
  $fixture = New-MainPolicyFixture
  $deletionFixture = $null
  $trackedFixture = $null
  try {
    $report = Get-MainPolicyReport -Root $fixture -IndexPath ''
    Assert-True (@($report.Drift | Where-Object { $_ -match 'engineering/docs/hidden.md' }).Count -eq 1) 'ignored meaningful engineering file is reported as policy drift'
    foreach ($path in @(
      'apps/chart/tests/unit/chart.test.mjs',
      'engine/tests/unit/engine_test.py',
      'engineering/docs/architecture.md',
      'engineering/archive/repository-graphify/graph.json',
      'engineering/archive/repository-graphify/graph.html',
      'engineering/archive/repository-graphify/rebuild/raw-run/GRAPH_REPORT.md',
      'apps/chart/state/data/raw/BaseLine/reference.json',
      '.editorconfig'
    )) {
      Assert-True ($report.Eligible -contains $path) "main policy keeps $path eligible"
    }
    foreach ($path in @(
      'engineering/archive/repository-graphify/cache/ast/cache.json',
      'graphify-out/cache/stat-index.json',
      'apps/chart/.vite/deps/package.json',
      'engineering/archive/repository-graphify/rebuild/raw-run/.graphify_extract.json',
      'apps/chart/state/data/raw/acquired.json',
      'apps/chart/state/cache/runtime.json',
      'apps/chart/state/secret/session.dpapi.json',
      'apps/chart/dist/index.html'
      'engineering/verification/regenerated-artifacts/dist/index.html'
      'apps/chart/state/data/raw/BaseLine/temp/partial.json'
      'engineering/verification/regenerated-artifacts/node_modules/package/index.js'
      'node_modules/package/index.js'
      'working.tmp'
      '.env'
    )) {
      Assert-True ($report.Excluded -contains $path) "main policy excludes $path"
    }
    $secret = Test-SensitiveCandidate -Root $fixture -Paths @('candidate/private.pem') -Commitish ''
    Assert-True ($secret.Errors.Count -eq 1) 'private-key marker is rejected'
    Assert-True ($secret.Errors[0] -notmatch 'private-material') 'secret value is redacted'
    $largeSecret = Test-SensitiveCandidate -Root $fixture -Paths @('candidate/large.txt') -Commitish ''
    Assert-True ($largeSecret.Errors.Count -eq 1) 'large eligible file is scanned for secret markers'
    $rootSecret = Test-SensitiveCandidate -Root $fixture -Paths @('root.pem', '.env') -Commitish ''
    Assert-True ($rootSecret.Errors.Count -eq 2) 'sensitive root-level filenames are rejected'

    $deletionFixture = New-RootFixture
    Write-FixtureFile $deletionFixture 'engineering/docs/retired.md' 'retired document'
    $null = Commit-Fixture $deletionFixture
    & git -C $deletionFixture rm --quiet -- engineering/docs/retired.md
    $deletionReport = Get-MainPolicyReport -Root $deletionFixture
    Assert-True ($deletionReport.Eligible -contains 'engineering/docs/retired.md') 'staged deletion remains policy eligible'
    $indexBefore = (& git -C $deletionFixture write-tree).Trim()
    $candidate = New-MainReleaseSource -Root $deletionFixture -CommitMessage 'fixture deletion' -DryRun
    Assert-True ($candidate.Changed) 'staged deletion enters dry-run main candidate'
    Assert-True (-not ((Get-GitTreePaths -Root $deletionFixture -Commitish $candidate.MainSha) -contains 'engineering/docs/retired.md')) 'candidate main tree removes staged deletion'
    Assert-True ((& git -C $deletionFixture write-tree).Trim() -eq $indexBefore) 'staged deletion remains untouched in active index'

    $trackedFixture = New-RootFixture
    Write-FixtureFile $trackedFixture 'engineering/verification/generated/dist/index.html' 'rebuildable output'
    $null = Commit-Fixture $trackedFixture
    $trackedReport = Get-MainPolicyReport -Root $trackedFixture
    Assert-True (@($trackedReport.Errors | Where-Object { $_ -match 'Excluded artifact is tracked: engineering/verification/generated/dist/index.html' }).Count -eq 1) 'already tracked build output blocks publication'
    & git -C $trackedFixture rm --cached --quiet -- engineering/verification/generated/dist/index.html
    Assert-True ($LASTEXITCODE -eq 0) 'tracked build output can be removed from Git without deleting the local file'
    $cleanedReport = Get-MainPolicyReport -Root $trackedFixture
    Assert-True ($cleanedReport.Errors.Count -eq 0) 'staged artifact removal clears main policy drift'
    $cleanedCandidate = New-MainReleaseSource -Root $trackedFixture -CommitMessage 'remove generated output' -DryRun
    Assert-True (-not ((Get-GitTreePaths -Root $trackedFixture -Commitish $cleanedCandidate.MainSha) -contains 'engineering/verification/generated/dist/index.html')) 'release candidate removes formerly tracked build output'

    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $badArchivePath = Join-Path $fixture 'engineering/archive/embedded-cache.zip'
    $badArchive = [IO.Compression.ZipFile]::Open($badArchivePath, [IO.Compression.ZipArchiveMode]::Create)
    try { $null = $badArchive.CreateEntry('snapshot/cache/rebuildable.json') }
    finally { $badArchive.Dispose() }
    $archiveReport = Get-MainPolicyReport -Root $fixture
    Assert-True (@($archiveReport.Errors | Where-Object { $_ -match 'Archive contains excluded artifact: engineering/archive/embedded-cache.zip' }).Count -eq 1) 'cache inside an eligible ZIP blocks publication'
  } finally {
    Remove-TestFixturePath $fixture
    Remove-TestFixturePath $deletionFixture
    Remove-TestFixturePath $trackedFixture
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
      Assert-True ($fileSet.Paths -contains $path) "runtime inventory includes unreferenced $path"
      Assert-True (-not ($fileSet.Drift -contains $path)) "runtime inventory has no omitted runtime path: $path"
    }
    Assert-True ($fileSet.Errors.Count -eq 0) 'fixture closure has no unresolved imports'
    Assert-True ((Test-ProductionFileSet -FileSet $fileSet -Policy $policy).Errors.Count -eq 0) 'fixture file set passes integrity checks'
  } finally {
    Remove-TestFixturePath $fixture.Root
  }
}

function Invoke-SnapshotTests {
  Import-Module $script:ModulePath -Force
  $fixture = New-ProductionFixture
  $remote = $null
  $linkedWorktree = $null
  $snapshot = $null
  $normalSnapshot = $null
  $divergentSnapshot = $null
  try {
    $remote = New-FixtureRemote -Root $fixture.Root
    & git -C $fixture.Root -c user.name=Fixture -c user.email=fixture@example.invalid tag -a fixture-remote-only $fixture.Sha -m remote-only
    & git -C $fixture.Root push --quiet origin refs/tags/fixture-remote-only
    & git -C $fixture.Root tag -d fixture-remote-only | Out-Null
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
    Assert-True ($null -ne (Get-Command Assert-ReleaseValidationComplete -ErrorAction SilentlyContinue)) 'publication validation gate is exported'
    Assert-Throws { Assert-ReleaseValidationComplete -Validation $validation } 'structural-only validation cannot authorize publication'
    $incompleteValidation = [pscustomobject]@{ Errors=@(); Checks=@([pscustomobject]@{ Name='node-check'; Status='NOT_TESTED_DEPENDENCY_UNAVAILABLE' }) }
    Assert-Throws { Assert-ReleaseValidationComplete -Validation $incompleteValidation } 'missing required runtime validator cannot authorize publication'
    Remove-TemporaryReleaseContext -Context $snapshot.Context
    Assert-True (-not (Test-Path -LiteralPath $snapshot.Context.WorktreePath)) 'dry-run worktree is cleaned'
    & git -C $fixture.Root show-ref --verify --quiet refs/tags/fixture-remote-only
    Assert-True ($LASTEXITCODE -ne 0) 'dry-run does not import remote-only tags'
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

    $linkedWorktree = Join-Path ([IO.Path]::GetTempPath()) ("tradingbot-release-checkedout-" + [guid]::NewGuid().ToString('N'))
    & git -C $fixture.Root worktree add --quiet $linkedWorktree production
    Assert-True ($LASTEXITCODE -eq 0) 'fixture can check out production in a linked worktree'
    $checkedOutPreflight = Test-ReleasePreflight -Root $fixture.Root -Tag 'snapshot-checkedout'
    Assert-True (@($checkedOutPreflight.Errors | Where-Object { $_ -match 'checked out in another worktree' }).Count -gt 0) 'preflight rejects a checked-out production branch'
    & git -C $fixture.Root worktree remove --force $linkedWorktree
    Assert-True ($LASTEXITCODE -eq 0) 'linked production fixture worktree is removed'
    $linkedWorktree = $null

    $divergent = (& git -C $fixture.Root -c user.name=Fixture -c user.email=fixture@example.invalid commit-tree "${sourceSha}^{tree}" -m divergent).Trim()
    & git -C $fixture.Root update-ref refs/heads/production $divergent
    $divergentPreflight = Test-ReleasePreflight -Root $fixture.Root -Tag 'snapshot-divergent'
    Assert-True ($divergentPreflight.Errors.Count -eq 0) 'preflight accepts preservation of divergent local production history'
    Assert-True (@($divergentPreflight.Warnings | Where-Object { $_ -match 'history will be preserved' }).Count -eq 1) 'preflight reports local production history integration'
    $divergentSnapshot = New-ProductionSnapshot -Root $fixture.Root -SourceMainSha $sourceSha -ProductionBaseSha $preflight.ProductionBaseSha -FileSet $fileSet -CommitMessage 'fixture integrated production' -DryRun
    & git -C $fixture.Root merge-base --is-ancestor $divergent $divergentSnapshot.ProductionSha
    Assert-True ($LASTEXITCODE -eq 0) 'integrated snapshot retains the local production commit'
    & git -C $fixture.Root merge-base --is-ancestor $preflight.ProductionBaseSha $divergentSnapshot.ProductionSha
    Assert-True ($LASTEXITCODE -eq 0) 'integrated snapshot retains the remote production commit'
    Assert-True ((Test-ProductionSnapshot -Snapshot $divergentSnapshot).Errors.Count -eq 0) 'integrated snapshot keeps the exact runtime tree'
    $integratedPromotion = Finalize-ProductionBranch -Root $fixture.Root -Snapshot $divergentSnapshot
    Assert-True ($integratedPromotion.PreviousSha -eq $divergent) 'integrated promotion advances the expected local production ref'
    Remove-TemporaryReleaseContext -Context $divergentSnapshot.Context
  } finally {
    if ($snapshot -and -not $snapshot.Context.Cleaned) { Remove-TemporaryReleaseContext -Context $snapshot.Context }
    if ($normalSnapshot -and -not $normalSnapshot.Context.Cleaned) { Remove-TemporaryReleaseContext -Context $normalSnapshot.Context }
    if ($divergentSnapshot -and -not $divergentSnapshot.Context.Cleaned) { Remove-TemporaryReleaseContext -Context $divergentSnapshot.Context }
    if ($linkedWorktree -and (Test-Path -LiteralPath $linkedWorktree)) { & git -C $fixture.Root worktree remove --force $linkedWorktree 2>$null | Out-Null }
    if ($fixture) { Remove-TestFixturePath $fixture.Root }
    Remove-TestFixturePath $remote
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

    $indeterminateFixture = New-PublicationFixture
    $fixtures += $indeterminateFixture
    $indeterminateTag = New-ReleaseTag -Root $indeterminateFixture.Root -Tag 'fixture-indeterminate' -ProductionSha $indeterminateFixture.ProductionSha -MainSha $indeterminateFixture.MainSha
    $indeterminatePrepared = [pscustomobject]@{ MainSha=$indeterminateFixture.MainSha; ProductionSha=$indeterminateFixture.ProductionSha; Tag='fixture-indeterminate'; TagObjectSha=$indeterminateTag.TagObjectSha; RemoteMainSha=$indeterminateFixture.ProductionSha; RemoteProductionSha=$indeterminateFixture.ProductionSha; RemoteTagSha=$null }
    $indeterminateAdapter = { param($root, $gitArgs) if ($gitArgs -contains '--atomic') { return [pscustomobject]@{ ExitCode=1; StdOut=''; StdErr='fatal: the receiving end does not support --atomic push'; Arguments=$gitArgs } }; if ($gitArgs -contains 'refs/tags/fixture-indeterminate') { return [pscustomobject]@{ ExitCode=128; StdOut=''; StdErr='simulated remote read failure'; Arguments=$gitArgs } }; Invoke-ReleaseGit -Root $root -Arguments $gitArgs }
    $indeterminate = Publish-ReleaseRefs -Root $indeterminateFixture.Root -PreparedRelease $indeterminatePrepared -CommandAdapter $indeterminateAdapter
    Assert-True ($indeterminate.Status -eq 'INDETERMINATE_REMOTE') 'indeterminate remote ref verification stops publication'
    Assert-True ((& git -C $indeterminateFixture.Root ls-remote origin refs/heads/main | ForEach-Object { ($_ -split '\s+')[0] }) -eq $indeterminateFixture.ProductionSha) 'indeterminate probe leaves remote main unchanged'

    $changedFixture = New-PublicationFixture
    $fixtures += $changedFixture
    $changedTag = New-ReleaseTag -Root $changedFixture.Root -Tag 'fixture-ref-changed' -ProductionSha $changedFixture.ProductionSha -MainSha $changedFixture.MainSha
    $changedPrepared = [pscustomobject]@{ MainSha=$changedFixture.MainSha; ProductionSha=$changedFixture.ProductionSha; Tag='fixture-ref-changed'; TagObjectSha=$changedTag.TagObjectSha; RemoteMainSha=$changedFixture.ProductionSha; RemoteProductionSha=$changedFixture.ProductionSha; RemoteTagSha=$null }
    $readState = [pscustomobject]@{ MainReads=0; OriginalMain=$changedFixture.ProductionSha }
    $changedAdapter = { param($root, $gitArgs) if ($gitArgs -contains '--atomic') { return [pscustomobject]@{ ExitCode=1; StdOut=''; StdErr='fatal: the receiving end does not support --atomic push'; Arguments=$gitArgs } }; if ($gitArgs[0] -eq 'ls-remote' -and $gitArgs[-1] -eq 'refs/heads/main') { $readState.MainReads++; if ($readState.MainReads -ge 3) { return [pscustomobject]@{ ExitCode=0; StdOut="$($readState.OriginalMain)`trefs/heads/main"; StdErr=''; Arguments=$gitArgs } } }; Invoke-ReleaseGit -Root $root -Arguments $gitArgs }
    $changed = Publish-ReleaseRefs -Root $changedFixture.Root -PreparedRelease $changedPrepared -CommandAdapter $changedAdapter
    Assert-True ($changed.Status -eq 'PARTIAL_FAILURE') 'fallback stops if a previously verified ref changes'
  } finally {
    foreach ($fixture in $fixtures) {
      if ($fixture) { Remove-TestFixturePath $fixture.Root; Remove-TestFixturePath $fixture.Remote }
    }
  }
}

function Invoke-DocumentationTests {
  Assert-True (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'Invoke-TradingBotRelease.ps1') -PathType Leaf) 'documented scripted release entry point exists'
  $readmePath = Join-Path $PSScriptRoot 'README.md'
  Assert-True (Test-Path -LiteralPath $readmePath -PathType Leaf) 'release operations README exists'
  $text = Get-Content -LiteralPath $readmePath -Raw
  Assert-True ($text -match '(?m)^powershell\.exe .*Invoke-TradingBotRelease\.ps1\s*$') 'README shows the one-command normal release invocation'
  foreach ($phrase in @(
    'derive the project root from their own locations', 'inclusion-first', 'dependency-derived', 'BaseLine', 'Graphify', 'apps/chart/state',
    'origin/production', 'GitHub CLI', '-DryRun', 'temporary worktree', '--atomic', 'fallback',
    'TradingBot-Main-Source', 'GitHub Release', 'Recovery', 'No publication occurs during implementation validation'
  )) {
    Assert-True ($text.Contains($phrase)) "README covers $phrase"
  }
}

function Invoke-MenuSafetyTests {
  . (Join-Path $PSScriptRoot 'Git.Menu.ps1') -LoadFunctionsOnly
  $fixture = New-RootFixture
  $remote = $null
  try {
    $null = Commit-Fixture $fixture
    $remote = New-FixtureRemote $fixture
    $script:Root = $fixture
    $beforeHead = (& git -C $fixture rev-parse HEAD).Trim()
    $beforeStash = @(& git -C $fixture stash list)
    Assert-Throws { Sync-MainFastForwardIfNeeded -State ([pscustomobject]@{ MainBehind=1 }) } 'behind main is rejected without stashing or merging'
    Assert-True ((& git -C $fixture rev-parse HEAD).Trim() -eq $beforeHead) 'rejected sync preserves main HEAD'
    Assert-True ((@(& git -C $fixture stash list) -join "`n") -eq ($beforeStash -join "`n")) 'rejected sync preserves stash list'
    Assert-Throws { Get-AheadBehind -RemoteSha 'missing-remote-oid' -LocalSha $beforeHead } 'invalid branch comparison is not reported as equal'
    & git -C $fixture remote set-url origin (Join-Path $fixture 'missing-origin.git')
    Assert-Throws { Test-OptionalTag -Tag 'candidate-tag' } 'unreadable remote tag state blocks a menu release'
    $preflight = Test-ReleasePreflight -Root $fixture -Tag 'candidate-tag'
    Assert-True (@($preflight.Errors | Where-Object { $_ -match 'Remote release tag state is indeterminate' }).Count -eq 1) 'unreadable remote tag state blocks module release'
    Assert-Throws { New-ReleaseTag -Root $fixture -Tag 'candidate-tag' -ProductionSha $beforeHead -MainSha $beforeHead } 'unreadable remote tag state blocks tag creation'
    Assert-True (-not ((& git -C $fixture tag --list 'candidate-tag') -join '')) 'no tag created after remote read failure'
  } finally {
    Remove-TestFixturePath $fixture
    Remove-TestFixturePath $remote
  }
}

try {
  switch ($Case) {
    'All' {
      Invoke-RootResolutionTests
      Invoke-MainPolicyTests
      Invoke-ProductionClosureTests
      Invoke-SnapshotTests
      Invoke-PublicationTests
      Invoke-MenuSafetyTests
      Invoke-DocumentationTests
      $script:Passed += 7
    }
    'RootResolution' { Invoke-RootResolutionTests; $script:Passed++ }
    'MainPolicy' { Invoke-MainPolicyTests; $script:Passed++ }
    'ProductionClosure' { Invoke-ProductionClosureTests; $script:Passed++ }
    'Snapshot' { Invoke-SnapshotTests; $script:Passed++ }
    'Publication' { Invoke-PublicationTests; $script:Passed++ }
    'MenuSafety' { Invoke-MenuSafetyTests; $script:Passed++ }
    'Documentation' { Invoke-DocumentationTests; $script:Passed++ }
  }
  Write-Output "PASS: $Case ($script:Passed passed, $script:Failed failed)"
} catch {
  $script:Failed++
  Write-Error "FAIL: $Case - $($_.Exception.Message) at $($_.InvocationInfo.PositionMessage)"
  exit 1
}
