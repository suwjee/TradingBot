[CmdletBinding()]
param([string] $Case = 'All')

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:SourceDirectory = $PSScriptRoot

function Assert-Manager {
  param([bool] $Condition, [string] $Message)
  if (-not $Condition) { throw "Assertion failed: $Message" }
}

function Assert-ManagerThrows {
  param([scriptblock] $Action, [string] $Pattern)
  try { & $Action } catch {
    Assert-Manager ($_.Exception.Message -match $Pattern) "expected diagnostic matching $Pattern; got $($_.Exception.Message)"
    return
  }
  throw "Assertion failed: expected failure matching $Pattern"
}

function Invoke-TestProcess {
  param([string] $Executable, [string] $Arguments, [string] $Directory, [string] $InputText = '', [int] $TimeoutSeconds = 30)
  $info = [Diagnostics.ProcessStartInfo]::new()
  $info.FileName = $Executable
  $info.Arguments = $Arguments
  $info.WorkingDirectory = $Directory
  $info.UseShellExecute = $false
  $info.CreateNoWindow = $true
  $info.RedirectStandardOutput = $true
  $info.RedirectStandardError = $true
  $info.RedirectStandardInput = $true
  $process = [Diagnostics.Process]::new()
  $process.StartInfo = $info
  try {
    [void]$process.Start()
    $stdout = $process.StandardOutput.ReadToEndAsync()
    $stderr = $process.StandardError.ReadToEndAsync()
    $process.StandardInput.Write($InputText)
    $process.StandardInput.Close()
    if (-not $process.WaitForExit($TimeoutSeconds * 1000)) { $process.Kill(); throw 'Test child process timed out.' }
    return [pscustomobject]@{ ExitCode=$process.ExitCode; StdOut=$stdout.Result; StdErr=$stderr.Result }
  } finally { $process.Dispose() }
}

function New-ManagerFixture {
  param([switch] $SpecialPath)
  $path = Join-Path ([IO.Path]::GetTempPath()) ('tradingbot-manager-test-' + [guid]::NewGuid().ToString('N'))
  if ($SpecialPath) { $path += ' checkout & (space)!' }
  foreach ($relative in @('scripts/git', 'apps/chart', 'engine')) {
    [void](New-Item -ItemType Directory -Path (Join-Path $path $relative) -Force)
  }
  Copy-Item -LiteralPath (Join-Path $script:SourceDirectory 'git.bat') -Destination (Join-Path $path 'scripts/git')
  Copy-Item -LiteralPath (Join-Path $script:SourceDirectory 'Git.Menu.ps1') -Destination (Join-Path $path 'scripts/git')
  Copy-Item -LiteralPath (Join-Path $script:SourceDirectory 'Release.Workflow.psm1') -Destination (Join-Path $path 'scripts/git')
  Copy-Item -LiteralPath (Join-Path $script:SourceDirectory 'production-policy.psd1') -Destination (Join-Path $path 'scripts/git')
  [IO.File]::WriteAllText((Join-Path $path 'apps/chart/package.json'), '{}')
  [IO.File]::WriteAllText((Join-Path $path '.gitignore'), "origin.git/`n")
  [IO.File]::WriteAllText((Join-Path $path 'engine/runtime.py'), '# fixture')
  & git.exe -C $path init --quiet --initial-branch=main
  & git.exe -C $path config core.autocrlf false
  & git.exe -C $path config core.hooksPath (Join-Path $path 'no-hooks')
  & git.exe -C $path add --all
  & git.exe -C $path -c user.name=Fixture -c user.email=fixture@example.invalid commit --quiet -m fixture
  Assert-Manager ($LASTEXITCODE -eq 0) 'fixture commit created'
  return $path
}

function Remove-ManagerFixture {
  param([string] $Path)
  $target = [IO.Path]::GetFullPath($Path)
  $base = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
  Assert-Manager ($target.StartsWith($base, [StringComparison]::OrdinalIgnoreCase) -and (Split-Path -Leaf $target) -match '^tradingbot-manager-test-[0-9a-f]{32}(?: checkout & \(space\)!)?$') 'cleanup restricted to this test fixture'
  if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Recurse -Force }
}

function Initialize-ManagerFunctions {
  param([string] $Fixture)
  . (Join-Path $Fixture 'scripts/git/Git.Menu.ps1') -LoadFunctionsOnly
  $script:Root = $Fixture
}

function New-ManagerRemote {
  param([string] $Root, [switch] $Production)
  $remote = Join-Path ([IO.Path]::GetTempPath()) ('tradingbot-manager-test-' + [guid]::NewGuid().ToString('N'))
  & git.exe init --bare --quiet $remote
  & git.exe -C $Root remote add origin $remote
  & git.exe -C $Root push --quiet origin HEAD:refs/heads/main
  if ($Production) { & git.exe -C $Root push --quiet origin HEAD:refs/heads/production }
  Assert-Manager ($LASTEXITCODE -eq 0) 'local fixture remote initialized'
  return $remote
}

function Test-ManagerRoot {
  $fixture = New-ManagerFixture
  try {
    Import-Module (Join-Path $fixture 'scripts/git/Release.Workflow.psm1') -Force -DisableNameChecking
    $resolved = Resolve-TradingBotProjectRoot -ScriptPath (Join-Path $fixture 'scripts/git/Git.Menu.ps1')
    Assert-Manager ($resolved -eq $fixture) 'AGENTS.md is optional for a valid checkout'
  } finally { Remove-ManagerFixture $fixture }
}

function Test-ManagerLauncher {
  $fixture = New-ManagerFixture -SpecialPath
  try {
    $bat = Join-Path $fixture 'scripts/git/git.bat'
    $result = Invoke-TestProcess -Executable $env:ComSpec -Arguments ('/d /c ""' + $bat + '""') -Directory ([IO.Path]::GetTempPath()) -InputText "0`r`n"
    Assert-Manager ($result.ExitCode -eq 0) "launcher opens and exits from a different CWD without AGENTS.md or origin: $($result.StdOut) $($result.StdErr)"
    Assert-Manager ($result.StdOut -match 'TradingBot Git Manager' -and $result.StdOut -match 'Preview Only') 'real menu was displayed'
    $result = Invoke-TestProcess -Executable $env:ComSpec -Arguments ('/d /c ""' + $bat + '" -LoadFunctionsOnly"') -Directory ([IO.Path]::GetTempPath())
    Assert-Manager ($result.ExitCode -eq 0) 'batch forwards arguments to PowerShell'
  } finally { Remove-ManagerFixture $fixture }
}

function Test-ManagerBranch {
  $fixture = New-ManagerFixture
  try {
    # Functions should load even when the source checkout has no project markers.
    . Initialize-ManagerFunctions $fixture
    $blob = (& git.exe -C $fixture rev-parse 'HEAD:engine/runtime.py').Trim()
    "0 0000000000000000000000000000000000000000`tengine/runtime.py`n100644 $blob 1`tengine/runtime.py`n100644 $blob 3`tengine/runtime.py" | & git.exe -C $fixture update-index --add --index-info
    Assert-ManagerThrows { Assert-ActiveMain } 'unresolved|unmerged|conflict'
    $preflight = Test-ReleasePreflight -Root $fixture -Tag candidate
    Assert-Manager (@($preflight.Errors | Where-Object { $_ -match 'unresolved|unmerged|conflict' }).Count -gt 0) 'module preflight rejects an unmerged index without MERGE_HEAD'
    Assert-ManagerThrows { New-MainReleaseSource -Root $fixture -CommitMessage candidate -DryRun } 'unresolved|unmerged|conflict'
  } finally { Remove-ManagerFixture $fixture }
}

function Test-ManagerMainOnly {
  $fixture = New-ManagerFixture
  $remote = $null
  try {
    . Initialize-ManagerFunctions $fixture
    $remote = New-ManagerRemote -Root $fixture
    $head = (& git.exe -C $fixture rev-parse HEAD).Trim()
    Update-RemoteState -Target main
    $state = Get-BranchState -Target main
    Assert-Manager ($state.LocalMain -eq $head -and $state.RemoteMain -eq $head) 'main-only operation works when origin/production is absent'
    $script:HadOperationFailure = $false
    function Read-Host { param($Prompt); return '' }
    try { Invoke-InteractiveOperation -Target main -DryRun } finally { Remove-Item Function:\Read-Host }
    Assert-Manager (-not $script:HadOperationFailure) 'empty message/tag main dry run passes'
  } finally { Remove-ManagerFixture $fixture; if ($remote) { Remove-ManagerFixture $remote } }
}

function Test-ManagerUnicode {
  $fixture = New-ManagerFixture
  try {
    . Initialize-ManagerFunctions $fixture
    $base = (& git.exe -C $fixture rev-parse HEAD).Trim()
    $relative = 'engine/' + [char]0x062A + [char]0x0633 + [char]0x062A + ' file.py'
    [IO.File]::WriteAllText((Join-Path $fixture $relative), '# unicode path')
    $candidate = New-MainReleaseSource -Root $fixture -CommitMessage preview -DryRun
    $entries = @(Get-DiffEntries -Base $base -Target $candidate.MainSha)
    Assert-Manager ($entries.Count -eq 1 -and $entries[0].Path -eq $relative) 'preview stages and displays the exact Unicode filename'
    & git.exe -C $fixture diff --cached --quiet
    Assert-Manager ($LASTEXITCODE -eq 0) 'preview preserves active index'
  } finally { Remove-ManagerFixture $fixture }
}

function Test-ManagerPublication {
  $fixture = New-ManagerFixture
  try {
    . Initialize-ManagerFunctions $fixture
    $head = (& git.exe -C $fixture rev-parse HEAD).Trim()
    $script:PublicationPushes = 0
    function Invoke-GitSafe { param($Arguments); if ($Arguments[0] -eq 'push') { $script:PublicationPushes++ }; return [pscustomobject]@{ ExitCode=0; StdOut=$head; StdErr='' } }
    function Get-LocalCommitOid { param($Ref); return $head }
    function Get-RemoteOid { param($Ref); return 'changed-after-preview' }
    $refs = @([pscustomobject]@{ Name='main'; LocalRef='refs/heads/main'; RemoteRef='refs/heads/main'; BaselineOid='preview-baseline'; DesiredOid=$head })
    Assert-ManagerThrows { Publish-MenuRefs -Refs $refs } 'Remote changed'
    Assert-Manager ($script:PublicationPushes -eq 0) 'remote race blocks push inside publication helper'
  } finally { Remove-ManagerFixture $fixture }
}

function Test-ManagerTag {
  $fixture = New-ManagerFixture
  try {
    . Initialize-ManagerFunctions $fixture
    $head = (& git.exe -C $fixture rev-parse HEAD).Trim()
    $null = New-MenuTag -Tag both-tag -TargetSha $head -TargetKind both -MainSourceSha $head
    $text = (& git.exe -C $fixture cat-file -p refs/tags/both-tag) -join "`n"
    Assert-Manager ($text.Contains("TradingBot-Main-Source: $head")) 'Both tag on production records the main source SHA'
  } finally { Remove-ManagerFixture $fixture }
}

function Test-ManagerProcess {
  $fixture = New-ManagerFixture
  try {
    $module = Import-Module (Join-Path $fixture 'scripts/git/Release.Workflow.psm1') -Force -DisableNameChecking -PassThru
    $node = (Get-Command node -CommandType Application | Select-Object -First 1).Source
    $values = @('', 'space value', 'quote"value', 'C:\space path\', "first line`nsecond line")
    $result = & $module { param($exe, $values, $root) Invoke-ReleaseExecutable -FilePath $exe -Arguments (@('-e','console.log(JSON.stringify(process.argv.slice(1)))','--') + $values) -WorkingDirectory $root } $node $values $fixture
    Assert-Manager ($result.ExitCode -eq 0) 'native executable succeeded'
    $actual = ConvertFrom-Json -InputObject $result.StdOut
    Assert-Manager ($actual.Count -eq $values.Count) 'empty native argument is preserved'
    for ($i=0; $i -lt $values.Count; $i++) { Assert-Manager ($actual[$i] -eq $values[$i]) "native argument $i survives quotes and trailing backslashes" }
    $worker = @'
param($ModulePath, $NodePath, $Root)
$ErrorActionPreference = 'Stop'
$module = Import-Module $ModulePath -Force -PassThru -DisableNameChecking
$result = & $module { param($node, $root) Invoke-ReleaseExecutable -FilePath $node -Arguments @('-e', 'process.stderr.write("e".repeat(262144)); process.stdout.write("ok");') -WorkingDirectory $root } $NodePath $Root
if ($result.ExitCode -ne 0 -or $result.StdOut -ne 'ok' -or $result.StdErr.Length -ne 262144) { throw 'Separate output streams were not captured completely.' }
'@
    $workerPath = Join-Path $fixture 'process-worker.ps1'
    [IO.File]::WriteAllText($workerPath, $worker)
    $ps = Join-Path $PSHOME 'powershell.exe'
    if (-not (Test-Path -LiteralPath $ps)) { $ps = Join-Path $PSHOME 'pwsh.exe' }
    $arguments = '-NoLogo -NoProfile -File "' + $workerPath + '" -ModulePath "' + (Join-Path $fixture 'scripts/git/Release.Workflow.psm1') + '" -NodePath "' + $node + '" -Root "' + $fixture + '"'
    $result = Invoke-TestProcess -Executable $ps -Arguments $arguments -Directory $fixture -TimeoutSeconds 15
    Assert-Manager ($result.ExitCode -eq 0) 'large stderr and stdout cannot deadlock validation'
  } finally { Remove-ManagerFixture $fixture }
}

function Test-ManagerValidationGate {
  $fixture = New-ManagerFixture
  try {
    . Initialize-ManagerFunctions $fixture
    $script:Confirmations = 0
    $script:HadOperationFailure = $false
    function Assert-ActiveMain { }
    function Update-RemoteState { param($Target) }
    function Get-BranchState { param($Target); return [pscustomobject]@{ LocalMain='main-sha'; RemoteMain='main-sha'; LocalProduction='prod-sha'; RemoteProduction='prod-sha'; MainAhead=0; MainBehind=0; ProductionAhead=0; ProductionBehind=0 } }
    function Show-RepositoryStatus { param($State) }
    function Test-GitAuthentication { param($Target,$State) }
    function Read-Host { param($Prompt); if ($Prompt -like 'Commit message*') { return 'message' }; return '' }
    function Read-YesNo { param($Prompt); if ($Prompt -eq 'Continue?') { $script:Confirmations++; return $false }; return $false }
    function New-ProductionPreview { param($SourceMainSha,$ProductionBaseSha,$CommitMessage,[switch]$RuntimeValidation); return [pscustomobject]@{ Snapshot=[pscustomobject]@{ Context=$null }; FileSet=[pscustomobject]@{ Drift=@() }; TreeSha='preview-tree'; Entries=@() } }
    function New-MainPreview { param($CommitMessage,$RemoteMain,[switch]$IncludeWorkingTree); return [pscustomobject]@{ TargetSha='main-sha'; TreeSha='main-tree'; Entries=@() } }
    function Test-ProductionSnapshot { param($Snapshot,[switch]$RunRuntimeValidation,$ProgressCallback); return [pscustomobject]@{ Errors=@('runtime validation failed'); Checks=@() } }
    function Remove-PreviewProduction { param($Preview) }
    Invoke-InteractiveOperation -Target production
    Assert-Manager ($script:HadOperationFailure -and $script:Confirmations -eq 0) 'runtime validation must fail before final confirmation and any permanent commit'
  } finally { Remove-ManagerFixture $fixture }
}

function Test-ManagerRuntime {
  $fixture = New-ManagerFixture
  $remote = $null
  $snapshot = $null
  try {
    . Initialize-ManagerFunctions $fixture
    $policy = Import-ReleasePolicy -Root $fixture
    foreach ($relative in $policy.Production.MandatoryPaths) {
      $path = Join-Path $fixture $relative
      [void](New-Item -ItemType Directory -Path (Split-Path -Parent $path) -Force)
      [IO.File]::WriteAllText($path, '')
    }
    [IO.File]::WriteAllText((Join-Path $fixture 'apps/chart/package.json'), '{"name":"manager-fixture","version":"1.0.0","scripts":{"build":"node --check vite.config.js"}}')
    [IO.File]::WriteAllText((Join-Path $fixture 'apps/chart/package-lock.json'), '{"name":"manager-fixture","version":"1.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"manager-fixture","version":"1.0.0"}}}')
    [IO.File]::WriteAllText((Join-Path $fixture 'engine/bridge/trading_pipeline.py'), "import argparse`nargparse.ArgumentParser().parse_args()`n")
    & git.exe -C $fixture add --all
    & git.exe -C $fixture -c user.name=Fixture -c user.email=fixture@example.invalid commit --quiet -m runtime
    $remote = New-ManagerRemote -Root $fixture -Production
    $source = (& git.exe -C $fixture rev-parse HEAD).Trim()
    $fileSet = Get-ProductionFileSet -Root $fixture -MainSha $source -Policy $policy
    $snapshot = New-ProductionSnapshot -Root $fixture -SourceMainSha $source -ProductionBaseSha $source -FileSet $fileSet -CommitMessage fixture -DryRun
    $validation = Test-ProductionSnapshot -Snapshot $snapshot -RunRuntimeValidation
    Assert-ReleaseValidationComplete -Validation $validation
    Assert-Manager ($validation.Checks.Count -eq 8) 'all eight production gates run with real Node, Python, and npm processes'
    $null = Finalize-ProductionBranch -Root $fixture -Snapshot $snapshot
    & git.exe -C $fixture push --quiet origin refs/heads/production:refs/heads/production
    Remove-TemporaryReleaseContext -Context $snapshot.Context
    $beforeIndex = (Get-FileHash -LiteralPath (Join-Path $fixture '.git/index')).Hash
    $beforeRefs = (& git.exe -C $fixture show-ref) -join "`n"
    $beforeRemote = (& git.exe -C $fixture ls-remote origin) -join "`n"
    [IO.File]::WriteAllText((Join-Path $fixture 'scripts/start.ps1'), '$WarningPreference = ''Continue''')
    [void](New-Item -ItemType Directory -Path (Join-Path $fixture 'engine/pipeline') -Force)
    [IO.File]::WriteAllText((Join-Path $fixture 'engine/pipeline/xyz.py'), '# new module without imports')
    $script:ObservedMainEntries = @()
    $script:ObservedProductionEntries = @()
    $script:OriginalMainPreview = ${function:New-MainPreview}
    $script:OriginalProductionPreview = ${function:New-ProductionPreview}
    function New-MainPreview { param($CommitMessage,$RemoteMain,[switch]$IncludeWorkingTree); $preview = & $script:OriginalMainPreview -CommitMessage $CommitMessage -RemoteMain $RemoteMain -IncludeWorkingTree:$IncludeWorkingTree; $script:ObservedMainEntries=$preview.Entries; return $preview }
    function New-ProductionPreview { param($SourceMainSha,$ProductionBaseSha,$CommitMessage,[switch]$RuntimeValidation); $preview = & $script:OriginalProductionPreview -SourceMainSha $SourceMainSha -ProductionBaseSha $ProductionBaseSha -CommitMessage $CommitMessage -RuntimeValidation:$RuntimeValidation; $script:ObservedProductionEntries=$preview.Entries; return $preview }
    function Read-Host { param($Prompt); return '' }
    $script:HadOperationFailure = $false
    Invoke-InteractiveOperation -Target both -DryRun
    Assert-Manager (-not $script:HadOperationFailure) 'Both dry run passes full runtime validation'
    Assert-Manager (@($script:ObservedMainEntries | Where-Object { $_.Path -eq 'engine/pipeline/xyz.py' -and $_.Kind -eq 'Added' }).Count -eq 1) 'blank message still includes a new module in main'
    Assert-Manager (@($script:ObservedProductionEntries | Where-Object { $_.Path -eq 'engine/pipeline/xyz.py' -and $_.Kind -eq 'Added' }).Count -eq 1) 'new unreferenced module is included in production'
    Assert-Manager ((Get-FileHash -LiteralPath (Join-Path $fixture '.git/index')).Hash -eq $beforeIndex) 'Both dry run preserves exact active index bytes'
    Assert-Manager (((& git.exe -C $fixture show-ref) -join "`n") -eq $beforeRefs) 'Both dry run preserves permanent refs and tags'
    Assert-Manager (((& git.exe -C $fixture ls-remote origin) -join "`n") -eq $beforeRemote) 'Both dry run preserves the remote'
    Assert-Manager (@(& git.exe -C $fixture worktree list).Count -eq 1) 'Both dry run cleans temporary worktrees'
  } finally {
    if ($snapshot -and -not $snapshot.Context.Cleaned) { Remove-TemporaryReleaseContext -Context $snapshot.Context }
    Remove-ManagerFixture $fixture
    if ($remote) { Remove-ManagerFixture $remote }
  }
}

function Test-ManagerFallback {
  $fixture = New-ManagerFixture
  $remote = $null
  try {
    . Initialize-ManagerFunctions $fixture
    $remote = New-ManagerRemote -Root $fixture -Production
    $base = (& git.exe -C $fixture rev-parse HEAD).Trim()
    [IO.File]::WriteAllText((Join-Path $fixture 'engine/runtime.py'), '# changed')
    & git.exe -C $fixture add --all
    & git.exe -C $fixture -c user.name=Fixture -c user.email=fixture@example.invalid commit --quiet -m changed
    $head = (& git.exe -C $fixture rev-parse HEAD).Trim()
    & git.exe -C $fixture branch production $head
    $tag = New-MenuTag -Tag fallback-tag -TargetSha $head -TargetKind both -MainSourceSha $head
    function Invoke-GitSafe {
      param($Arguments)
      if ($Arguments -contains '--atomic') { return [pscustomobject]@{ ExitCode=1; StdOut=''; StdErr='the receiving end does not support --atomic push' } }
      return Invoke-ReleaseGit -Root $script:Root -Arguments $Arguments
    }
    $refs = @(
      [pscustomobject]@{ Name='main'; LocalRef='refs/heads/main'; RemoteRef='refs/heads/main'; BaselineOid=$base; DesiredOid=$head },
      [pscustomobject]@{ Name='production'; LocalRef='refs/heads/production'; RemoteRef='refs/heads/production'; BaselineOid=$base; DesiredOid=$head },
      [pscustomobject]@{ Name='tag'; LocalRef='refs/tags/fallback-tag'; RemoteRef='refs/tags/fallback-tag'; BaselineOid=$null; DesiredOid=$tag }
    )
    $result = Publish-MenuRefs -Refs $refs
    Assert-Manager ($result.Status -eq 'PASS' -and $result.Method -eq 'fallback') 'guarded fallback publishes to a real local bare remote'
    foreach ($ref in $refs) { Assert-Manager ((Get-RemoteOid $ref.RemoteRef) -eq $ref.DesiredOid) "fallback verifies $($ref.Name)" }
  } finally { Remove-ManagerFixture $fixture; if ($remote) { Remove-ManagerFixture $remote } }
}

function Test-ManagerAuthentication {
  $fixture = New-ManagerFixture
  try {
    . Initialize-ManagerFunctions $fixture
    $script:AuthenticationSpecs = @()
    function Invoke-GitSafe { param($Arguments); $script:AuthenticationSpecs += $Arguments[-1]; return [pscustomobject]@{ ExitCode=0; StdOut=''; StdErr='' } }
    Test-GitAuthentication -Target production -State ([pscustomobject]@{ LocalMain='main-sha'; RemoteProduction='prod-sha' })
    Assert-Manager ($script:AuthenticationSpecs.Count -eq 1 -and $script:AuthenticationSpecs[0] -eq 'prod-sha:refs/heads/production') 'production-only authorization checks production instead of main'
  } finally { Remove-ManagerFixture $fixture }
}

function Test-ManagerFileChanges {
  $fixture = New-ManagerFixture
  try {
    . Initialize-ManagerFunctions $fixture
    [IO.File]::WriteAllText((Join-Path $fixture 'engine/deleted.py'), '# removed module')
    & git.exe -C $fixture add --all
    & git.exe -C $fixture -c user.name=Fixture -c user.email=fixture@example.invalid commit --quiet -m baseline
    $base = (& git.exe -C $fixture rev-parse HEAD).Trim()
    $beforeIndex = (Get-FileHash -LiteralPath (Join-Path $fixture '.git/index')).Hash
    [void](New-Item -ItemType Directory -Path (Join-Path $fixture 'engine/new-package/config') -Force)
    $source = [IO.Path]::GetFullPath((Join-Path $fixture 'engine/runtime.py'))
    $destination = [IO.Path]::GetFullPath((Join-Path $fixture 'engine/new-package/runtime.py'))
    Assert-Manager ($source.StartsWith($fixture + '\') -and $destination.StartsWith($fixture + '\')) 'rename stays in the fixture'
    Move-Item -LiteralPath $source -Destination $destination
    Remove-Item -LiteralPath (Join-Path $fixture 'engine/deleted.py')
    [IO.File]::WriteAllText((Join-Path $fixture 'engine/new-package/config/new.json'), '{}')
    [IO.File]::WriteAllText((Join-Path $fixture '.gitignore'), "engine/new-package/config/new.json`n")
    $candidate = New-MainReleaseSource -Root $fixture -CommitMessage changes -DryRun
    $policy = @{ Production=@{ MandatoryPaths=@('apps/chart/package.json'); RuntimeRoots=@('engine/'); ExcludedPathPatterns=@('engine/tests/**') } }
    $fileSet = Get-ProductionFileSet -Root $fixture -MainSha $candidate.MainSha -Policy $policy
    Assert-Manager ($fileSet.Paths -contains 'engine/new-package/runtime.py') 'renamed runtime file remains in production'
    Assert-Manager ($fileSet.Paths -contains 'engine/new-package/config/new.json') 'new configuration is included even when ignored by Git'
    Assert-Manager ($fileSet.Paths -notcontains 'engine/runtime.py' -and $fileSet.Paths -notcontains 'engine/deleted.py') 'renames and deletions remove the old production paths'
    Assert-Manager ($fileSet.Errors.Count -eq 0 -and $fileSet.Drift.Count -eq 0) 'dynamic inventory accepts the new package structure'
    Assert-Manager ((Get-FileHash -LiteralPath (Join-Path $fixture '.git/index')).Hash -eq $beforeIndex) 'file-change preview preserves active index'
    $entries = @(Get-DiffEntries -Base $base -Target $candidate.MainSha)
    Assert-Manager (@($entries | Where-Object { $_.Kind -eq 'Renamed' }).Count -eq 1) 'main preview shows the rename'
    Assert-Manager (@($entries | Where-Object { $_.Kind -eq 'Deleted' -and $_.Path -eq 'engine/deleted.py' }).Count -eq 1) 'main preview shows the deletion'
  } finally { Remove-ManagerFixture $fixture }
}

$cases = [ordered]@{ Root={Test-ManagerRoot}; Launcher={Test-ManagerLauncher}; Branch={Test-ManagerBranch}; MainOnly={Test-ManagerMainOnly}; Unicode={Test-ManagerUnicode}; Publication={Test-ManagerPublication}; Tag={Test-ManagerTag}; Process={Test-ManagerProcess}; ValidationGate={Test-ManagerValidationGate}; Runtime={Test-ManagerRuntime}; Fallback={Test-ManagerFallback}; Authentication={Test-ManagerAuthentication}; FileChanges={Test-ManagerFileChanges} }
if ($Case -ne 'All' -and -not $cases.Contains($Case)) { throw "Unknown test case: $Case" }
$passed = 0
$failed = 0
foreach ($name in $cases.Keys) {
  if ($Case -ne 'All' -and $Case -ne $name) { continue }
  try { & $cases[$name]; $passed++; Write-Output "PASS: $name" }
  catch { $failed++; Write-Output "FAIL: $name - $($_.Exception.Message)" }
}
Write-Output "Git Manager: $passed passed, $failed failed"
if ($failed) { exit 1 }
