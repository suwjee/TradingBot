Set-StrictMode -Version Latest

function Assert-ReleaseCondition {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)] [bool] $Condition,
    [Parameter(Mandatory)] [string] $Message
  )

  if (-not $Condition) { throw $Message }
}

function Resolve-TradingBotProjectRoot {
  [CmdletBinding()]
  param([Parameter(Mandatory)] [string] $ScriptPath)

  $fullScriptPath = [IO.Path]::GetFullPath($ScriptPath)
  Assert-ReleaseCondition (Test-Path -LiteralPath $fullScriptPath -PathType Leaf) "Release script was not found: $fullScriptPath"

  $candidate = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $fullScriptPath) '..\..'))
  $gitRoot = & git -C $candidate rev-parse --show-toplevel 2>&1
  if ($LASTEXITCODE -ne 0) { throw "Unable to resolve a Git repository from: $candidate" }
  $root = [IO.Path]::GetFullPath(($gitRoot | Select-Object -First 1).ToString().Trim())

  Assert-ReleaseCondition ($root -eq $candidate) 'Release scripts must be located under the resolved repository root.'
  foreach ($relative in @('AGENTS.md', 'apps\chart', 'engine')) {
    Assert-ReleaseCondition (Test-Path -LiteralPath (Join-Path $root $relative)) "TradingBot project marker is missing: $relative"
  }
  return $root
}

function Invoke-ReleaseGit {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)] [string] $Root,
    [Parameter(Mandatory)] [string[]] $Arguments,
    [string] $WorkingDirectory = $Root
  )

  $previousErrorActionPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = 'Continue'
    $gitArguments = @('-C', $WorkingDirectory)
    if (-not ([IO.Path]::GetFullPath($WorkingDirectory).Equals([IO.Path]::GetFullPath($Root), [StringComparison]::OrdinalIgnoreCase))) {
      $gitArguments += @('-c', "safe.directory=$([IO.Path]::GetFullPath($WorkingDirectory))")
    }
    $records = @(& git @gitArguments @Arguments 2>&1)
    $exitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $previousErrorActionPreference
  }
  $stdout = @($records | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] } | ForEach-Object { $_.ToString() })
  $stderr = @($records | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] } | ForEach-Object { $_.ToString() })
  return [pscustomobject]@{
    ExitCode = $exitCode
    StdOut = $stdout -join [Environment]::NewLine
    StdErr = $stderr -join [Environment]::NewLine
    Arguments = @($Arguments)
  }
}

function ConvertTo-ReleasePath {
  param([Parameter(Mandatory)] [string] $Path)
  return $Path.Replace('\', '/').TrimStart('./')
}

function Test-ReleasePathPattern {
  param([Parameter(Mandatory)] [string] $Path, [Parameter(Mandatory)] [string[]] $Patterns)
  foreach ($pattern in $Patterns) {
    if ($Path -like $pattern) { return $true }
  }
  return $false
}

function Test-ReleasePathWithinRoots {
  param([Parameter(Mandatory)] [string] $Path, [Parameter(Mandatory)] [string[]] $Roots)
  foreach ($root in $Roots) {
    $normalizedRoot = (ConvertTo-ReleasePath $root).TrimEnd('/')
    if ($Path.Equals($normalizedRoot, [StringComparison]::OrdinalIgnoreCase) -or
        $Path.StartsWith("$normalizedRoot/", [StringComparison]::OrdinalIgnoreCase)) {
      return $true
    }
  }
  return $false
}

function Import-ReleasePolicy {
  [CmdletBinding()]
  param([Parameter(Mandatory)] [string] $Root)

  $projectPolicy = Join-Path $Root 'scripts\git\production-policy.psd1'
  $policyPath = if (Test-Path -LiteralPath $projectPolicy) { $projectPolicy } else { Join-Path $PSScriptRoot 'production-policy.psd1' }
  Assert-ReleaseCondition (Test-Path -LiteralPath $policyPath -PathType Leaf) "Release policy was not found: $policyPath"
  return Import-PowerShellDataFile -LiteralPath $policyPath
}

function Get-MainPolicyReport {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)] [string] $Root,
    [string] $IndexPath = ''
  )

  $policy = Import-ReleasePolicy -Root $Root
  $commands = @(
    @('ls-files'),
    @('ls-files', '--others', '--exclude-standard'),
    @('ls-files', '--others', '--ignored', '--exclude-standard')
  )
  $allPaths = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
  $ignoredPaths = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
  foreach ($command in $commands) {
    $result = Invoke-ReleaseGit -Root $Root -Arguments $command
    if ($result.ExitCode -ne 0) { throw "Git inventory failed: $($result.StdErr)" }
    foreach ($line in @($result.StdOut -split "`r?`n")) {
      if ([string]::IsNullOrWhiteSpace($line)) { continue }
      $path = ConvertTo-ReleasePath $line
      [void] $allPaths.Add($path)
      if ($command -contains '--ignored') { [void] $ignoredPaths.Add($path) }
    }
  }

  $eligible = [System.Collections.Generic.List[string]]::new()
  $excluded = [System.Collections.Generic.List[string]]::new()
  $drift = [System.Collections.Generic.List[string]]::new()
  foreach ($path in $allPaths | Sort-Object) {
    $included = Test-ReleasePathPattern -Path $path -Patterns $policy.Main.IncludedPathPatterns
    $isExcluded = (-not $included) -and (Test-ReleasePathPattern -Path $path -Patterns $policy.Main.ExcludedPathPatterns)
    if ($isExcluded) {
      $excluded.Add($path)
      continue
    }
    $eligible.Add($path)
    if ($ignoredPaths.Contains($path) -and (Test-ReleasePathPattern -Path $path -Patterns $policy.Main.MeaningfulRoots)) {
      $drift.Add("Meaningful path is ignored: $path")
    }
  }

  return [pscustomobject]@{
    Eligible = @($eligible)
    Excluded = @($excluded)
    Ignored = @($ignoredPaths | Sort-Object)
    Drift = @($drift)
    Errors = @($drift)
  }
}

function Test-SensitiveCandidate {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)] [string] $Root,
    [Parameter(Mandatory)] [string[]] $Paths,
    [string] $Commitish = ''
  )

  $policy = Import-ReleasePolicy -Root $Root
  $errors = [System.Collections.Generic.List[string]]::new()
  $skippedLargeFiles = [System.Collections.Generic.List[string]]::new()
  foreach ($relativePath in $Paths) {
    $path = ConvertTo-ReleasePath $relativePath
    if (Test-ReleasePathPattern -Path $path -Patterns $policy.Sensitive.PathPatterns) {
      $errors.Add("Sensitive path detected: $path")
      continue
    }
    $content = $null
    if ([string]::IsNullOrWhiteSpace($Commitish)) {
      $filePath = Join-Path $Root $path
      if (-not (Test-Path -LiteralPath $filePath -PathType Leaf)) { continue }
      if ((Get-Item -LiteralPath $filePath).Length -gt $policy.Sensitive.MaximumScanBytes) {
        $skippedLargeFiles.Add($path)
        continue
      }
      $content = [IO.File]::ReadAllText($filePath)
    } else {
      $result = Invoke-ReleaseGit -Root $Root -Arguments @('show', "$Commitish`:$path")
      if ($result.ExitCode -ne 0) { continue }
      $content = $result.StdOut
    }
    foreach ($pattern in $policy.Sensitive.ContentPatterns) {
      if ($content -match $pattern) {
        $errors.Add("Sensitive content marker detected: $path")
        break
      }
    }
  }
  return [pscustomobject]@{
    Errors = @($errors)
    SkippedLargeFiles = @($skippedLargeFiles)
  }
}

function Get-GitTreePaths {
  [CmdletBinding()]
  param([Parameter(Mandatory)] [string] $Root, [Parameter(Mandatory)] [string] $Commitish)

  $result = Invoke-ReleaseGit -Root $Root -Arguments @('ls-tree', '-r', '--name-only', $Commitish)
  if ($result.ExitCode -ne 0) { throw "Unable to read Git tree ${Commitish}: $($result.StdErr)" }
  return @($result.StdOut -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | ForEach-Object { ConvertTo-ReleasePath $_ })
}

function Get-GitBlobText {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)] [string] $Root,
    [Parameter(Mandatory)] [string] $Commitish,
    [Parameter(Mandatory)] [string] $RelativePath
  )

  $path = ConvertTo-ReleasePath $RelativePath
  $result = Invoke-ReleaseGit -Root $Root -Arguments @('show', "$Commitish`:$path")
  if ($result.ExitCode -ne 0) { throw "Unable to read $path from $Commitish." }
  return $result.StdOut
}

function Resolve-ReleasePathSegments {
  param([Parameter(Mandatory)] [string] $Path)
  $segments = [System.Collections.Generic.List[string]]::new()
  foreach ($segment in $Path.Replace('\', '/').Split('/')) {
    if ([string]::IsNullOrWhiteSpace($segment) -or $segment -eq '.') { continue }
    if ($segment -eq '..') {
      if ($segments.Count -eq 0) { return $null }
      $segments.RemoveAt($segments.Count - 1)
      continue
    }
    $segments.Add($segment)
  }
  return $segments -join '/'
}

function Resolve-LocalReleaseImport {
  param(
    [Parameter(Mandatory)] [string] $SourcePath,
    [Parameter(Mandatory)] [string] $Specifier,
    [Parameter(Mandatory)] [System.Collections.Generic.HashSet[string]] $AllPaths,
    [string] $ProjectBase = ''
  )

  if (-not ($Specifier.StartsWith('.') -or $Specifier.StartsWith('/'))) { return $null }
  $base = if ($Specifier.StartsWith('/')) { $ProjectBase } else { Split-Path -Parent $SourcePath }
  $candidate = Resolve-ReleasePathSegments ("$base/$Specifier")
  if ($null -eq $candidate) { return $null }
  $candidates = [System.Collections.Generic.List[string]]::new()
  $candidates.Add($candidate)
  if (-not [IO.Path]::HasExtension($candidate)) {
    foreach ($extension in @('.js', '.mjs', '.css', '.py')) { $candidates.Add("$candidate$extension") }
    foreach ($entry in @('index.js', 'index.mjs')) { $candidates.Add("$candidate/$entry") }
  }
  foreach ($path in $candidates) {
    if ($AllPaths.Contains($path)) { return $path }
  }
  return $null
}

function Get-JavaScriptReleaseSpecifiers {
  param([Parameter(Mandatory)] [AllowEmptyString()] [string] $Text)
  $patterns = @(
    '(?ms)^\s*import\s*(?:\{[^}]*\}|\*\s+as\s+[A-Za-z_$][\w$]*|[A-Za-z_$][\w$]*(?:\s*,\s*(?:\{[^}]*\}|\*\s+as\s+[A-Za-z_$][\w$]*))?)\s+from\s+["''](?<specifier>[^"'']+)["'']',
    '(?m)^\s*import\s*["''](?<specifier>[^"'']+)["'']',
    '(?ms)^\s*export\s+(?:\{[^}]*\}|\*)\s+from\s+["''](?<specifier>[^"'']+)["'']',
    '(?m)\bimport\(\s*["''](?<specifier>[^"'']+)["'']\s*\)'
  )
  $specifiers = [System.Collections.Generic.List[string]]::new()
  foreach ($pattern in $patterns) {
    foreach ($match in [regex]::Matches($Text, $pattern)) { $specifiers.Add($match.Groups['specifier'].Value) }
  }
  return @($specifiers | Select-Object -Unique)
}

function Get-CssReleaseSpecifiers {
  param([Parameter(Mandatory)] [AllowEmptyString()] [string] $Text)
  $specifiers = [System.Collections.Generic.List[string]]::new()
  foreach ($pattern in @('(?im)@import\s+(?:url\()?\s*["''](?<specifier>[^"'']+)["'']', '(?im)url\(\s*["''](?<specifier>[^"'']+)["'']\s*\)')) {
    foreach ($match in [regex]::Matches($Text, $pattern)) { $specifiers.Add($match.Groups['specifier'].Value) }
  }
  return @($specifiers | Select-Object -Unique)
}

function Get-PythonReleaseModules {
  param([Parameter(Mandatory)] [AllowEmptyString()] [string] $Text)
  $modules = [System.Collections.Generic.List[string]]::new()
  foreach ($match in [regex]::Matches($Text, '(?m)^\s*(?:from|import)\s+(?<module>[A-Za-z_][A-Za-z0-9_]*)')) {
    $modules.Add($match.Groups['module'].Value)
  }
  return @($modules | Select-Object -Unique)
}

function Get-ProductionFileSet {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)] [string] $Root,
    [Parameter(Mandatory)] [string] $MainSha,
    [Parameter(Mandatory)] [hashtable] $Policy
  )

  $allPaths = Get-GitTreePaths -Root $Root -Commitish $MainSha
  $allPathSet = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
  foreach ($path in $allPaths) { [void] $allPathSet.Add($path) }
  $selected = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
  $queue = [System.Collections.Generic.Queue[string]]::new()
  $errors = [System.Collections.Generic.List[string]]::new()

  function Add-ClosurePath([string] $Path) {
    if ($selected.Add($Path)) { $queue.Enqueue($Path) }
  }

  foreach ($seed in $Policy.Production.MandatoryPaths) {
    if ($allPathSet.Contains($seed)) { Add-ClosurePath $seed } else { $errors.Add("Required production seed is missing: $seed") }
  }

  while ($queue.Count -gt 0) {
    $current = $queue.Dequeue()
    $extension = [IO.Path]::GetExtension($current).ToLowerInvariant()
    if ($extension -notin @('.html', '.js', '.mjs', '.css', '.py')) { continue }
    $text = Get-GitBlobText -Root $Root -Commitish $MainSha -RelativePath $current
    $specifiers = @()
    $projectBase = ''
    if ($extension -eq '.html') {
      $specifiers = @(
        [regex]::Matches($text, '(?im)<script[^>]+src\s*=\s*["''](?<specifier>[^"'']+)["'']') |
          ForEach-Object { $_.Groups['specifier'].Value }
      )
      $specifiers += @(
        [regex]::Matches($text, '(?im)<link\b[^>]*\brel\s*=\s*["''][^"'']*stylesheet[^"'']*["''][^>]*\bhref\s*=\s*["''](?<specifier>[^"'']+)["'']') |
          ForEach-Object { $_.Groups['specifier'].Value }
      )
      $projectBase = 'apps/chart'
    } elseif ($extension -in @('.js', '.mjs')) {
      $specifiers = Get-JavaScriptReleaseSpecifiers $text
    } elseif ($extension -eq '.css') {
      $specifiers = Get-CssReleaseSpecifiers $text
    } elseif ($extension -eq '.py') {
      foreach ($module in Get-PythonReleaseModules $text) {
        $candidate = "engine/pipeline/$module.py"
        if ($allPathSet.Contains($candidate)) { Add-ClosurePath $candidate }
      }
      continue
    }
    foreach ($specifier in $specifiers) {
      if (-not ($specifier.StartsWith('.') -or $specifier.StartsWith('/'))) { continue }
      $resolved = Resolve-LocalReleaseImport -SourcePath $current -Specifier $specifier -AllPaths $allPathSet -ProjectBase $projectBase
      if ($null -eq $resolved) { $errors.Add("Unresolved local import from ${current}: $specifier") } else { Add-ClosurePath $resolved }
    }
  }

  $drift = [System.Collections.Generic.List[string]]::new()
  foreach ($path in $allPaths) {
    $isRuntimeAdjacent = Test-ReleasePathWithinRoots -Path $path -Roots $Policy.Production.RuntimeRoots
    $isCode = [IO.Path]::GetExtension($path).ToLowerInvariant() -in @('.js', '.mjs', '.css', '.py', '.html')
    $isExplicitlyExcluded = Test-ReleasePathPattern -Path $path -Patterns $Policy.Production.ExcludedPathPatterns
    if ($isRuntimeAdjacent -and $isCode -and -not $selected.Contains($path) -and -not $isExplicitlyExcluded) { $drift.Add($path) }
  }

  return [pscustomobject]@{
    Root = $Root
    MainSha = $MainSha
    Policy = $Policy
    Paths = @($selected | Sort-Object)
    Drift = @($drift | Sort-Object)
    Errors = @($errors)
  }
}

function Get-ReleaseRefOid {
  param([Parameter(Mandatory)] [string] $Root, [Parameter(Mandatory)] [string] $Ref)
  $result = Invoke-ReleaseGit -Root $Root -Arguments @('rev-parse', '--verify', '--quiet', "$Ref^{commit}")
  if ($result.ExitCode -ne 0) { return $null }
  return ($result.StdOut -split '\s+' | Select-Object -First 1).Trim()
}

function Test-ReleasePreflight {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)] [string] $Root,
    [Parameter(Mandatory)] [string] $Tag,
    [switch] $RequireGitHubCli
  )

  $errors = [System.Collections.Generic.List[string]]::new()
  $warnings = [System.Collections.Generic.List[string]]::new()
  $branch = (Invoke-ReleaseGit -Root $Root -Arguments @('symbolic-ref', '--quiet', '--short', 'HEAD'))
  if ($branch.ExitCode -ne 0 -or $branch.StdOut.Trim() -ne 'main') { $errors.Add('The active branch must be main.') }
  foreach ($marker in @('.git/MERGE_HEAD', '.git/rebase-apply', '.git/rebase-merge')) {
    if (Test-Path -LiteralPath (Join-Path $Root $marker)) { $errors.Add("Git operation in progress: $marker") }
  }
  $remoteUrl = Invoke-ReleaseGit -Root $Root -Arguments @('remote', 'get-url', 'origin')
  if ($remoteUrl.ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($remoteUrl.StdOut)) { $errors.Add('Configured origin remote is required.') }
  $tagSyntax = Invoke-ReleaseGit -Root $Root -Arguments @('check-ref-format', "refs/tags/$Tag")
  if ($tagSyntax.ExitCode -ne 0) { $errors.Add("Invalid Git tag syntax: $Tag") }
  $localTag = Invoke-ReleaseGit -Root $Root -Arguments @('show-ref', '--verify', '--quiet', "refs/tags/$Tag")
  if ($localTag.ExitCode -eq 0) { $errors.Add("Local release tag already exists: $Tag") }

  $remoteProduction = Invoke-ReleaseGit -Root $Root -Arguments @('ls-remote', '--exit-code', 'origin', 'refs/heads/production')
  $productionBaseSha = $null
  if ($remoteProduction.ExitCode -ne 0) {
    $errors.Add('origin/production is required for a release snapshot.')
  } else {
    $productionBaseSha = ($remoteProduction.StdOut -split '\s+' | Select-Object -First 1).Trim()
  }
  $remoteMain = Invoke-ReleaseGit -Root $Root -Arguments @('ls-remote', '--exit-code', 'origin', 'refs/heads/main')
  $remoteMainSha = if ($remoteMain.ExitCode -eq 0) { ($remoteMain.StdOut -split '\s+' | Select-Object -First 1).Trim() } else { $null }
  $remoteTag = Invoke-ReleaseGit -Root $Root -Arguments @('ls-remote', '--exit-code', 'origin', "refs/tags/$Tag")
  if ($remoteTag.ExitCode -eq 0) { $errors.Add("Remote release tag already exists: $Tag") }

  $localProductionSha = Get-ReleaseRefOid -Root $Root -Ref 'refs/heads/production'
  if ($null -ne $localProductionSha) {
    if ($null -eq $productionBaseSha -or $localProductionSha -ne $productionBaseSha) {
      $errors.Add('Local production branch diverges from origin/production; resolve it before release.')
    }
    $upstream = Invoke-ReleaseGit -Root $Root -Arguments @('rev-parse', '--abbrev-ref', 'production@{upstream}')
    if ($upstream.ExitCode -ne 0 -or $upstream.StdOut.Trim() -ne 'origin/production') { $errors.Add('Local production branch must track origin/production.') }
  }

  if ($remoteUrl.ExitCode -eq 0 -and $branch.ExitCode -eq 0) {
    $pushProbe = Invoke-ReleaseGit -Root $Root -Arguments @('push', '--dry-run', 'origin', 'HEAD:refs/heads/main')
    if ($pushProbe.ExitCode -ne 0) { $errors.Add('Git push authentication or main-ref authorization failed during dry-run verification.') }
  }

  $github = 'NOT_REQUESTED'
  if ($RequireGitHubCli) {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if ($null -eq $gh) {
      $errors.Add('GitHub CLI is required but unavailable.')
      $github = 'UNAVAILABLE'
    } else {
      $auth = & gh auth status 2>&1
      if ($LASTEXITCODE -ne 0) { $errors.Add('GitHub CLI authentication verification failed.'); $github = 'AUTH_FAILED' }
      else {
        $repo = & gh repo view --json nameWithOwner 2>&1
        if ($LASTEXITCODE -ne 0) { $errors.Add('GitHub repository access verification failed.'); $github = 'REPOSITORY_FAILED' }
        else { $github = 'PASS' }
      }
    }
  }

  return [pscustomobject]@{
    Root = $Root
    Tag = $Tag
    RemoteUrl = $remoteUrl.StdOut.Trim()
    RemoteMainSha = $remoteMainSha
    ProductionBaseSha = $productionBaseSha
    LocalProductionSha = $localProductionSha
    GitHub = $github
    Errors = @($errors)
    Warnings = @($warnings)
  }
}

function New-TemporaryReleaseContext {
  [CmdletBinding()]
  param([Parameter(Mandatory)] [string] $Root)
  $id = [guid]::NewGuid().ToString('N')
  $temporaryRoot = Join-Path ([IO.Path]::GetTempPath()) "tradingbot-release-$id"
  New-Item -ItemType Directory -Force -Path $temporaryRoot | Out-Null
  return [pscustomobject]@{
    Root = $Root
    TemporaryRoot = $temporaryRoot
    WorktreePath = Join-Path $temporaryRoot 'production'
    IndexPath = Join-Path $temporaryRoot 'candidate-main.index'
    TemporaryProductionRef = "refs/release-tmp/$id/production"
    Cleaned = $false
  }
}

function New-ProductionSnapshot {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)] [string] $Root,
    [Parameter(Mandatory)] [string] $SourceMainSha,
    [Parameter(Mandatory)] [string] $ProductionBaseSha,
    [Parameter(Mandatory)] $FileSet,
    [Parameter(Mandatory)] [string] $CommitMessage,
    [switch] $DryRun
  )

  Assert-ReleaseCondition (-not [string]::IsNullOrWhiteSpace($CommitMessage)) 'A nonempty production commit message is required.'
  Assert-ReleaseCondition (@($FileSet.Errors).Count -eq 0) 'Production closure contains unresolved dependencies.'
  $context = New-TemporaryReleaseContext -Root $Root
  try {
    $sourceCheck = Invoke-ReleaseGit -Root $Root -Arguments @('cat-file', '-e', "$SourceMainSha^{commit}")
    Assert-ReleaseCondition ($sourceCheck.ExitCode -eq 0) "Source main commit is unavailable: $SourceMainSha"
    $fetch = Invoke-ReleaseGit -Root $Root -Arguments @('fetch', '--quiet', 'origin', "+refs/heads/production:$($context.TemporaryProductionRef)")
    Assert-ReleaseCondition ($fetch.ExitCode -eq 0) 'Could not fetch origin/production into the temporary release ref.'
    $fetchedProductionSha = Get-ReleaseRefOid -Root $Root -Ref $context.TemporaryProductionRef
    Assert-ReleaseCondition ($null -ne $fetchedProductionSha) 'Temporary fetched production ref is unavailable.'
    Assert-ReleaseCondition ($fetchedProductionSha -eq $ProductionBaseSha) 'origin/production changed after preflight; restart release preparation.'

    $previousIndex = $env:GIT_INDEX_FILE
    try {
      $env:GIT_INDEX_FILE = $context.IndexPath
      $readTree = Invoke-ReleaseGit -Root $Root -Arguments @('read-tree', $SourceMainSha)
      Assert-ReleaseCondition ($readTree.ExitCode -eq 0) 'Could not build a temporary source-main index.'
      $candidateMainTree = Invoke-ReleaseGit -Root $Root -Arguments @('write-tree')
      Assert-ReleaseCondition ($candidateMainTree.ExitCode -eq 0) 'Could not write the temporary source-main tree.'
      $candidateMainTreeSha = $candidateMainTree.StdOut.Trim()
    } finally {
      if ($null -eq $previousIndex) { Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue } else { $env:GIT_INDEX_FILE = $previousIndex }
    }

    if ($DryRun) {
      $worktree = Invoke-ReleaseGit -Root $Root -Arguments @('worktree', 'add', '--detach', $context.WorktreePath, $fetchedProductionSha)
    } else {
      $localProductionSha = Get-ReleaseRefOid -Root $Root -Ref 'refs/heads/production'
      if ($null -eq $localProductionSha) {
        $createBranch = Invoke-ReleaseGit -Root $Root -Arguments @('branch', '--track', 'production', $context.TemporaryProductionRef)
        Assert-ReleaseCondition ($createBranch.ExitCode -eq 0) 'Could not establish local production from fetched origin/production.'
      } else {
        Assert-ReleaseCondition ($localProductionSha -eq $fetchedProductionSha) 'Local production diverges from fetched origin/production.'
      }
      $upstream = Invoke-ReleaseGit -Root $Root -Arguments @('branch', '--set-upstream-to=origin/production', 'production')
      Assert-ReleaseCondition ($upstream.ExitCode -eq 0) 'Could not configure production upstream tracking.'
      $worktree = Invoke-ReleaseGit -Root $Root -Arguments @('worktree', 'add', $context.WorktreePath, 'production')
    }
    Assert-ReleaseCondition ($worktree.ExitCode -eq 0) 'Could not create isolated temporary production worktree.'

    $removeTracked = Invoke-ReleaseGit -Root $Root -WorkingDirectory $context.WorktreePath -Arguments @('rm', '-r', '--ignore-unmatch', '--', '.')
    Assert-ReleaseCondition ($removeTracked.ExitCode -eq 0) 'Could not clear tracked production worktree content.'
    $checkoutArgs = @('checkout', $SourceMainSha, '--') + @($FileSet.Paths)
    $restore = Invoke-ReleaseGit -Root $Root -WorkingDirectory $context.WorktreePath -Arguments $checkoutArgs
    Assert-ReleaseCondition ($restore.ExitCode -eq 0) 'Could not synchronize the production file set from source main.'

    $candidateTree = Invoke-ReleaseGit -Root $Root -WorkingDirectory $context.WorktreePath -Arguments @('write-tree')
    Assert-ReleaseCondition ($candidateTree.ExitCode -eq 0) 'Could not write the candidate production tree.'
    $candidatePaths = @(Get-GitTreePaths -Root $Root -Commitish $candidateTree.StdOut.Trim())
    $expectedPaths = @($FileSet.Paths | Sort-Object)
    Assert-ReleaseCondition (@(Compare-Object -ReferenceObject $expectedPaths -DifferenceObject $candidatePaths).Count -eq 0) 'Candidate production tree differs from the resolved source-main file set.'

    $diff = Invoke-ReleaseGit -Root $Root -WorkingDirectory $context.WorktreePath -Arguments @('diff', '--cached', '--quiet')
    Assert-ReleaseCondition ($diff.ExitCode -in @(0, 1)) 'Could not compare candidate production tree to its base.'
    $productionChanged = ($diff.ExitCode -eq 1)
    if ($productionChanged) {
      $commit = Invoke-ReleaseGit -Root $Root -WorkingDirectory $context.WorktreePath -Arguments @('-c', 'user.name=TradingBot Release', '-c', 'user.email=release@tradingbot.invalid', 'commit', '-m', $CommitMessage, '-m', "TradingBot-Main-Source: $SourceMainSha")
      Assert-ReleaseCondition ($commit.ExitCode -eq 0) 'Could not create the production snapshot commit.'
    }
    $productionHead = Invoke-ReleaseGit -Root $Root -WorkingDirectory $context.WorktreePath -Arguments @('rev-parse', '--verify', 'HEAD^{commit}')
    Assert-ReleaseCondition ($productionHead.ExitCode -eq 0) 'Could not resolve the prepared production commit.'
    $productionSha = ($productionHead.StdOut -split '\s+' | Select-Object -First 1).Trim()
    return [pscustomobject]@{
      Root = $Root
      Context = $context
      WorktreePath = $context.WorktreePath
      SourceMainSha = $SourceMainSha
      CandidateMainTreeSha = $candidateMainTreeSha
      ProductionBaseSha = $fetchedProductionSha
      ProductionSha = $productionSha
      ProductionChanged = $productionChanged
      FileSet = $FileSet
      DryRun = [bool] $DryRun
    }
  } catch {
    Remove-TemporaryReleaseContext -Context $context
    throw
  }
}

function Test-ProductionSnapshot {
  [CmdletBinding()]
  param([Parameter(Mandatory)] $Snapshot, [switch] $RunRuntimeValidation)
  $errors = [System.Collections.Generic.List[string]]::new()
  $checks = [System.Collections.Generic.List[object]]::new()
  $treePaths = @(Get-GitTreePaths -Root $Snapshot.Root -Commitish $Snapshot.ProductionSha)
  $treeDifference = Compare-Object -ReferenceObject @($Snapshot.FileSet.Paths | Sort-Object) -DifferenceObject $treePaths
  if (@($treeDifference).Count -eq 0) { $checks.Add([pscustomobject]@{ Name = 'snapshot-tree'; Status = 'PASS'; Detail = 'exact resolved file set' }) }
  else { $errors.Add('Production snapshot tree does not equal the resolved file set.'); $checks.Add([pscustomobject]@{ Name = 'snapshot-tree'; Status = 'FAIL'; Detail = 'tree mismatch' }) }
  if (@($treePaths | Where-Object { $_ -like 'apps/chart/state/**' }).Count -eq 0) { $checks.Add([pscustomobject]@{ Name = 'state-exclusion'; Status = 'PASS'; Detail = 'no local state content' }) }
  else { $errors.Add('Production snapshot contains apps/chart/state content.'); $checks.Add([pscustomobject]@{ Name = 'state-exclusion'; Status = 'FAIL'; Detail = 'state content present' }) }
  $sensitive = Test-SensitiveCandidate -Root $Snapshot.Root -Paths $treePaths -Commitish $Snapshot.ProductionSha
  foreach ($error in $sensitive.Errors) { $errors.Add($error) }
  if ($sensitive.Errors.Count -eq 0) { $checks.Add([pscustomobject]@{ Name = 'sensitive-content'; Status = 'PASS'; Detail = 'no policy match' }) }
  else { $checks.Add([pscustomobject]@{ Name = 'sensitive-content'; Status = 'FAIL'; Detail = 'policy match' }) }
  if (-not $RunRuntimeValidation) {
    $checks.Add([pscustomobject]@{ Name = 'runtime-validation'; Status = 'NOT_TESTED'; Detail = 'not requested for structural snapshot test' })
    return [pscustomobject]@{ Errors = @($errors); Checks = @($checks) }
  }

  $psErrors = $null
  foreach ($path in @($treePaths | Where-Object { $_ -like '*.ps1' })) {
    $psErrors = @()
    $null = [System.Management.Automation.Language.Parser]::ParseFile((Join-Path $Snapshot.WorktreePath $path), [ref] $null, [ref] $psErrors)
    if ($psErrors.Count -gt 0) { $errors.Add("PowerShell parse failed: $path") }
  }
  $checks.Add([pscustomobject]@{ Name = 'powershell-parse'; Status = if ($errors | Where-Object { $_ -like 'PowerShell parse failed:*' }) { 'FAIL' } else { 'PASS' }; Detail = 'selected scripts' })

  $node = Get-Command node -ErrorAction SilentlyContinue
  if ($null -eq $node) { $checks.Add([pscustomobject]@{ Name = 'node-check'; Status = 'NOT_TESTED_DEPENDENCY_UNAVAILABLE'; Detail = 'node unavailable' }) }
  else {
    $nodeFailures = 0
    foreach ($path in @($treePaths | Where-Object { $_ -match '\.(js|mjs)$' })) { & $node.Source --check (Join-Path $Snapshot.WorktreePath $path); if ($LASTEXITCODE -ne 0) { $nodeFailures++ } }
    if ($nodeFailures) { $errors.Add('Node syntax validation failed.'); $checks.Add([pscustomobject]@{ Name = 'node-check'; Status = 'FAIL'; Detail = "$nodeFailures selected files" }) }
    else { $checks.Add([pscustomobject]@{ Name = 'node-check'; Status = 'PASS'; Detail = 'selected JavaScript files' }) }
  }

  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($null -eq $python) { $checks.Add([pscustomobject]@{ Name = 'python-ast'; Status = 'NOT_TESTED_DEPENDENCY_UNAVAILABLE'; Detail = 'python unavailable' }) }
  else {
    $pythonFailures = 0
    $astCode = 'import ast,pathlib,sys; ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))'
    foreach ($path in @($treePaths | Where-Object { $_ -like '*.py' })) { & $python.Source -B -c $astCode (Join-Path $Snapshot.WorktreePath $path); if ($LASTEXITCODE -ne 0) { $pythonFailures++ } }
    if ($pythonFailures) { $errors.Add('Python AST validation failed.'); $checks.Add([pscustomobject]@{ Name = 'python-ast'; Status = 'FAIL'; Detail = "$pythonFailures selected files" }) }
    else { $checks.Add([pscustomobject]@{ Name = 'python-ast'; Status = 'PASS'; Detail = 'selected Python files' }) }
    & $python.Source -B (Join-Path $Snapshot.WorktreePath 'engine/bridge/trading_pipeline.py') --help
    if ($LASTEXITCODE -ne 0) { $errors.Add('Bridge --help validation failed.'); $checks.Add([pscustomobject]@{ Name = 'bridge-help'; Status = 'FAIL'; Detail = 'bridge command failed' }) }
    else { $checks.Add([pscustomobject]@{ Name = 'bridge-help'; Status = 'PASS'; Detail = 'bridge command' }) }
  }

  $npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
  if ($null -eq $npm) { $checks.Add([pscustomobject]@{ Name = 'npm-ci-build'; Status = 'NOT_TESTED_DEPENDENCY_UNAVAILABLE'; Detail = 'npm.cmd unavailable' }) }
  else {
    Push-Location $Snapshot.WorktreePath
    try {
      & $npm.Source ci
      $ciExit = $LASTEXITCODE
      if ($ciExit -eq 0) { & $npm.Source run build; $buildExit = $LASTEXITCODE } else { $buildExit = -1 }
    } finally { Pop-Location }
    if ($ciExit -ne 0 -or $buildExit -ne 0) { $errors.Add('npm ci or npm run build validation failed.'); $checks.Add([pscustomobject]@{ Name = 'npm-ci-build'; Status = 'FAIL'; Detail = "ci=$ciExit build=$buildExit" }) }
    else { $checks.Add([pscustomobject]@{ Name = 'npm-ci-build'; Status = 'PASS'; Detail = 'lockfile install and build' }) }
  }
  return [pscustomobject]@{ Errors = @($errors); Checks = @($checks) }
}

function Remove-TemporaryReleaseContext {
  [CmdletBinding()]
  param([Parameter(Mandatory)] $Context)
  if ($Context.Cleaned) { return }
  $worktreeList = Invoke-ReleaseGit -Root $Context.Root -Arguments @('worktree', 'list', '--porcelain')
  $registeredWorktree = $worktreeList.StdOut -split "`r?`n" | Where-Object { $_ -eq "worktree $($Context.WorktreePath.Replace('\', '/'))" }
  if ($registeredWorktree) {
    $removeWorktree = Invoke-ReleaseGit -Root $Context.Root -Arguments @('worktree', 'remove', '--force', $Context.WorktreePath)
    if ($removeWorktree.ExitCode -ne 0) { throw 'Could not remove the temporary release worktree.' }
  }
  if ($Context.TemporaryProductionRef) { $null = Invoke-ReleaseGit -Root $Context.Root -Arguments @('update-ref', '-d', $Context.TemporaryProductionRef) }
  $tempBase = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
  $tempRoot = [IO.Path]::GetFullPath($Context.TemporaryRoot)
  Assert-ReleaseCondition ($tempRoot.StartsWith($tempBase, [StringComparison]::OrdinalIgnoreCase) -and (Split-Path -Leaf $tempRoot).StartsWith('tradingbot-release-', [StringComparison]::OrdinalIgnoreCase)) 'Refusing to remove a non-release temporary path.'
  if (Test-Path -LiteralPath $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force }
  $Context.Cleaned = $true
}

function Test-ProductionFileSet {
  [CmdletBinding()]
  param([Parameter(Mandatory)] $FileSet, [Parameter(Mandatory)] [hashtable] $Policy)

  $errors = [System.Collections.Generic.List[string]]::new()
  foreach ($seed in $Policy.Production.MandatoryPaths) {
    if ($FileSet.Paths -notcontains $seed) { $errors.Add("Missing production seed: $seed") }
  }
  foreach ($path in $FileSet.Paths) {
    if (Test-ReleasePathPattern -Path $path -Patterns $Policy.Production.ExcludedPathPatterns) {
      $errors.Add("Excluded path entered production set: $path")
    }
  }
  $sensitive = Test-SensitiveCandidate -Root $FileSet.Root -Paths $FileSet.Paths -Commitish $FileSet.MainSha
  foreach ($error in $sensitive.Errors) { $errors.Add($error) }
  return [pscustomobject]@{ Errors = @($errors) }
}

Export-ModuleMember -Function Assert-ReleaseCondition, Resolve-TradingBotProjectRoot, Invoke-ReleaseGit, Import-ReleasePolicy, Get-MainPolicyReport, Test-SensitiveCandidate, Get-GitTreePaths, Get-GitBlobText, Get-ProductionFileSet, Test-ProductionFileSet, Test-ReleasePreflight, New-TemporaryReleaseContext, New-ProductionSnapshot, Test-ProductionSnapshot, Remove-TemporaryReleaseContext
