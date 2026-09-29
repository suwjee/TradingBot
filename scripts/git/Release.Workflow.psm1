Set-StrictMode -Version Latest

function Assert-ReleaseCondition {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)] [bool] $Condition,
    [Parameter(Mandatory)] [AllowEmptyString()] [string] $Message
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
  # Git may render this VMware checkout through its UNC identity while the
  # caller uses X:.  An empty prefix proves candidate itself is the Git root
  # without replacing the canonical caller-visible X: path.
  $gitPrefix = & git -C $candidate rev-parse --show-prefix 2>&1
  Assert-ReleaseCondition ($LASTEXITCODE -eq 0 -and [string]::IsNullOrWhiteSpace(($gitPrefix | Select-Object -First 1).ToString())) 'Release scripts must be located under the resolved repository root.'
  $root = $candidate
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
  $normalized = $Path.Replace('\', '/')
  if ($normalized.StartsWith('./', [StringComparison]::Ordinal)) { $normalized = $normalized.Substring(2) }
  return $normalized
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

function Get-ReleaseObjectOid {
  param([Parameter(Mandatory)] [string] $Root, [Parameter(Mandatory)] [string] $Ref)
  $result = Invoke-ReleaseGit -Root $Root -Arguments @('rev-parse', '--verify', '--quiet', $Ref)
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

    # Production stays detached until all candidate validation has passed.  The
    # caller advances the permanent local ref with an expected-old-value guard.
    $worktree = Invoke-ReleaseGit -Root $Root -Arguments @('worktree', 'add', '--detach', $context.WorktreePath, $fetchedProductionSha)
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

function Read-ReleaseInputs {
  [CmdletBinding()]
  param(
    [string] $CommitMessage = '',
    [string] $ReleaseTag = '',
    [switch] $NonInteractive
  )
  if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
    if ($NonInteractive) { throw 'CommitMessage is required in noninteractive mode.' }
    $CommitMessage = Read-Host 'Release commit message'
  }
  if ([string]::IsNullOrWhiteSpace($ReleaseTag)) {
    if ($NonInteractive) { throw 'ReleaseTag is required in noninteractive mode.' }
    $ReleaseTag = Read-Host 'Release tag'
  }
  Assert-ReleaseCondition (-not [string]::IsNullOrWhiteSpace($CommitMessage)) 'Release commit message must not be empty.'
  Assert-ReleaseCondition (-not [string]::IsNullOrWhiteSpace($ReleaseTag)) 'Release tag must not be empty.'
  return [pscustomobject]@{ CommitMessage = $CommitMessage.Trim(); ReleaseTag = $ReleaseTag.Trim() }
}

function Invoke-PublicationGit {
  param(
    [Parameter(Mandatory)] [string] $Root,
    [Parameter(Mandatory)] [string[]] $Arguments,
    [scriptblock] $CommandAdapter
  )
  if ($null -ne $CommandAdapter) { return & $CommandAdapter $Root ([string[]] $Arguments) }
  return Invoke-ReleaseGit -Root $Root -Arguments $Arguments
}

function Get-RemoteReleaseRefOid {
  param([Parameter(Mandatory)] [string] $Root, [Parameter(Mandatory)] [string] $Ref, [scriptblock] $CommandAdapter)
  $result = Invoke-PublicationGit -Root $Root -Arguments @('ls-remote', 'origin', $Ref) -CommandAdapter $CommandAdapter
  if ($result.ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($result.StdOut)) { return $null }
  return ($result.StdOut -split '\s+' | Select-Object -First 1).Trim()
}

function Test-ReleaseOidEqual {
  param($Left, $Right)
  if ($null -eq $Left -and $null -eq $Right) { return $true }
  if ($null -eq $Left -or $null -eq $Right) { return $false }
  return [string]::Equals([string] $Left, [string] $Right, [StringComparison]::OrdinalIgnoreCase)
}

function New-ReleaseTag {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)] [string] $Root,
    [Parameter(Mandatory)] [string] $Tag,
    [Parameter(Mandatory)] [string] $ProductionSha,
    [Parameter(Mandatory)] [string] $MainSha
  )
  $syntax = Invoke-ReleaseGit -Root $Root -Arguments @('check-ref-format', "refs/tags/$Tag")
  Assert-ReleaseCondition ($syntax.ExitCode -eq 0) "Invalid Git tag syntax: $Tag"
  $existingLocal = Invoke-ReleaseGit -Root $Root -Arguments @('show-ref', '--verify', '--quiet', "refs/tags/$Tag")
  Assert-ReleaseCondition ($existingLocal.ExitCode -ne 0) "Local tag already exists: $Tag"
  $existingRemote = Invoke-ReleaseGit -Root $Root -Arguments @('ls-remote', '--exit-code', 'origin', "refs/tags/$Tag")
  Assert-ReleaseCondition ($existingRemote.ExitCode -ne 0) "Remote tag already exists: $Tag"
  $production = Invoke-ReleaseGit -Root $Root -Arguments @('cat-file', '-e', "$ProductionSha^{commit}")
  Assert-ReleaseCondition ($production.ExitCode -eq 0) "Production commit is unavailable: $ProductionSha"
  $tagCreate = Invoke-ReleaseGit -Root $Root -Arguments @('-c', 'user.name=TradingBot Release', '-c', 'user.email=release@tradingbot.invalid', 'tag', '-a', $Tag, $ProductionSha, '-m', "TradingBot release $Tag", '-m', "TradingBot-Main-Source: $MainSha")
  Assert-ReleaseCondition ($tagCreate.ExitCode -eq 0) "Could not create annotated release tag: $Tag"
  $tagObject = Invoke-ReleaseGit -Root $Root -Arguments @('rev-parse', "refs/tags/$Tag")
  $peeled = Invoke-ReleaseGit -Root $Root -Arguments @('rev-parse', "$Tag^{commit}")
  Assert-ReleaseCondition ($tagObject.ExitCode -eq 0 -and $peeled.ExitCode -eq 0 -and $peeled.StdOut.Trim() -eq $ProductionSha) 'Annotated release tag does not point to the prepared production commit.'
  return [pscustomobject]@{ Tag = $Tag; TagObjectSha = $tagObject.StdOut.Trim(); ProductionSha = $ProductionSha; MainSha = $MainSha }
}

function Finalize-ProductionBranch {
  [CmdletBinding()]
  param([Parameter(Mandatory)] [string] $Root, [Parameter(Mandatory)] $Snapshot)
  $refresh = Invoke-ReleaseGit -Root $Root -Arguments @('fetch', '--quiet', 'origin', '+refs/heads/production:refs/remotes/origin/production')
  Assert-ReleaseCondition ($refresh.ExitCode -eq 0) 'Could not refresh origin/production before local branch promotion.'
  $remoteBase = Get-ReleaseRefOid -Root $Root -Ref 'refs/remotes/origin/production'
  Assert-ReleaseCondition ($remoteBase -eq $Snapshot.ProductionBaseSha) 'origin/production changed during local validation; refusing to advance production.'
  $current = Get-ReleaseRefOid -Root $Root -Ref 'refs/heads/production'
  if ($null -ne $current) { Assert-ReleaseCondition ($current -eq $Snapshot.ProductionBaseSha) 'Local production changed during validation; refusing to advance production.' }
  $expected = if ($null -eq $current) { '0000000000000000000000000000000000000000' } else { $current }
  $advance = Invoke-ReleaseGit -Root $Root -Arguments @('update-ref', 'refs/heads/production', $Snapshot.ProductionSha, $expected)
  Assert-ReleaseCondition ($advance.ExitCode -eq 0) 'Could not advance local production with its expected-old-value guard.'
  $upstream = Invoke-ReleaseGit -Root $Root -Arguments @('branch', '--set-upstream-to=origin/production', 'production')
  Assert-ReleaseCondition ($upstream.ExitCode -eq 0) 'Could not configure local production to track origin/production.'
  return [pscustomobject]@{ ProductionSha = $Snapshot.ProductionSha; PreviousSha = $current; Upstream = 'origin/production' }
}

function Add-ReleasePathsToIndex {
  param([Parameter(Mandatory)] [string] $Root, [Parameter(Mandatory)] [string[]] $Paths)
  foreach ($batch in @($Paths | ForEach-Object -Begin { $items = @() } -Process { $items += $_; if ($items.Count -ge 100) { ,$items; $items = @() } } -End { if ($items.Count) { ,$items } })) {
    $add = Invoke-ReleaseGit -Root $Root -Arguments (@('add', '--') + @($batch))
    Assert-ReleaseCondition ($add.ExitCode -eq 0) ("Could not stage a policy-eligible path for main: " + $add.StdErr)
  }
}

function New-MainReleaseSource {
  [CmdletBinding()]
  param([Parameter(Mandatory)] [string] $Root, [Parameter(Mandatory)] [string] $CommitMessage, [switch] $DryRun)
  $report = Get-MainPolicyReport -Root $Root
  Assert-ReleaseCondition ($report.Errors.Count -eq 0) ($report.Errors -join '; ')
  $staged = Invoke-ReleaseGit -Root $Root -Arguments @('diff', '--cached', '--name-only', '--diff-filter=ACMRD')
  Assert-ReleaseCondition ($staged.ExitCode -eq 0) 'Could not inspect the active Git index.'
  $invalidStaged = @($staged.StdOut -split "`r?`n" | Where-Object { $_ -and $report.Eligible -notcontains (ConvertTo-ReleasePath $_) })
  Assert-ReleaseCondition ($invalidStaged.Count -eq 0) ('Existing staged content violates main policy: ' + ($invalidStaged -join ', '))
  $sensitive = Test-SensitiveCandidate -Root $Root -Paths $report.Eligible
  Assert-ReleaseCondition ($sensitive.Errors.Count -eq 0) ($sensitive.Errors -join '; ')
  $head = Get-ReleaseRefOid -Root $Root -Ref 'HEAD'
  if (-not $DryRun) {
    Add-ReleasePathsToIndex -Root $Root -Paths $report.Eligible
    $diff = Invoke-ReleaseGit -Root $Root -Arguments @('diff', '--cached', '--quiet')
    Assert-ReleaseCondition ($diff.ExitCode -in @(0, 1)) 'Could not compare the staged main release candidate.'
    $changed = ($diff.ExitCode -eq 1)
    if ($changed) {
      $commit = Invoke-ReleaseGit -Root $Root -Arguments @('-c', 'user.name=TradingBot Release', '-c', 'user.email=release@tradingbot.invalid', 'commit', '-m', $CommitMessage)
      Assert-ReleaseCondition ($commit.ExitCode -eq 0) 'Could not create the main release commit.'
    }
    return [pscustomobject]@{ MainSha = (Get-ReleaseRefOid -Root $Root -Ref 'HEAD'); Changed = $changed; DryRun = $false }
  }

  $context = New-TemporaryReleaseContext -Root $Root
  try {
    $gitIndex = Invoke-ReleaseGit -Root $Root -Arguments @('rev-parse', '--git-path', 'index')
    Assert-ReleaseCondition ($gitIndex.ExitCode -eq 0) 'Could not locate the active Git index.'
    $activeIndex = Join-Path $Root $gitIndex.StdOut.Trim()
    if (Test-Path -LiteralPath $activeIndex) { [IO.File]::Copy($activeIndex, $context.IndexPath, $true) }
    $previousIndex = $env:GIT_INDEX_FILE
    try {
      $env:GIT_INDEX_FILE = $context.IndexPath
      Add-ReleasePathsToIndex -Root $Root -Paths $report.Eligible
      $diff = Invoke-ReleaseGit -Root $Root -Arguments @('diff', '--cached', '--quiet')
      Assert-ReleaseCondition ($diff.ExitCode -in @(0, 1)) 'Could not compare the temporary main release candidate.'
      $changed = ($diff.ExitCode -eq 1)
      if ($changed) {
        $tree = Invoke-ReleaseGit -Root $Root -Arguments @('write-tree')
        Assert-ReleaseCondition ($tree.ExitCode -eq 0) 'Could not write the temporary main tree.'
        $candidate = Invoke-ReleaseGit -Root $Root -Arguments @('-c', 'user.name=TradingBot Release', '-c', 'user.email=release@tradingbot.invalid', 'commit-tree', $tree.StdOut.Trim(), '-p', $head, '-m', $CommitMessage)
        Assert-ReleaseCondition ($candidate.ExitCode -eq 0) 'Could not create the temporary main candidate commit.'
        $mainSha = $candidate.StdOut.Trim()
      } else { $mainSha = $head }
    } finally {
      if ($null -eq $previousIndex) { Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue } else { $env:GIT_INDEX_FILE = $previousIndex }
    }
    return [pscustomobject]@{ MainSha = $mainSha; Changed = $changed; DryRun = $true }
  } finally { Remove-TemporaryReleaseContext -Context $context }
}

function Publish-ReleaseRefs {
  [CmdletBinding()]
  param([Parameter(Mandatory)] [string] $Root, [Parameter(Mandatory)] $PreparedRelease, [scriptblock] $CommandAdapter)
  foreach ($local in @(@('refs/heads/main', $PreparedRelease.MainSha), @('refs/heads/production', $PreparedRelease.ProductionSha))) {
    Assert-ReleaseCondition ((Get-ReleaseRefOid -Root $Root -Ref $local[0]) -eq $local[1]) "Local release ref is not prepared as expected: $($local[0])"
  }
  Assert-ReleaseCondition ((Get-ReleaseObjectOid -Root $Root -Ref "refs/tags/$($PreparedRelease.Tag)") -eq $PreparedRelease.TagObjectSha) "Local release ref is not prepared as expected: refs/tags/$($PreparedRelease.Tag)"
  $specs = @('refs/heads/main:refs/heads/main', 'refs/heads/production:refs/heads/production', "refs/tags/$($PreparedRelease.Tag):refs/tags/$($PreparedRelease.Tag)")
  $before = [pscustomobject]@{ Main = $PreparedRelease.RemoteMainSha; Production = $PreparedRelease.RemoteProductionSha; Tag = $PreparedRelease.RemoteTagSha }
  $atomic = Invoke-PublicationGit -Root $Root -Arguments (@('push', '--atomic', 'origin') + $specs) -CommandAdapter $CommandAdapter
  $readRemote = {
    [pscustomobject]@{
      Main = Get-RemoteReleaseRefOid -Root $Root -Ref 'refs/heads/main' -CommandAdapter $CommandAdapter
      Production = Get-RemoteReleaseRefOid -Root $Root -Ref 'refs/heads/production' -CommandAdapter $CommandAdapter
      Tag = Get-RemoteReleaseRefOid -Root $Root -Ref "refs/tags/$($PreparedRelease.Tag)" -CommandAdapter $CommandAdapter
    }
  }
  $afterAtomic = & $readRemote
  $desired = [pscustomobject]@{ Main = $PreparedRelease.MainSha; Production = $PreparedRelease.ProductionSha; Tag = $PreparedRelease.TagObjectSha }
  $isDesired = (Test-ReleaseOidEqual $afterAtomic.Main $desired.Main) -and (Test-ReleaseOidEqual $afterAtomic.Production $desired.Production) -and (Test-ReleaseOidEqual $afterAtomic.Tag $desired.Tag)
  if ($atomic.ExitCode -eq 0 -and $isDesired) { return [pscustomobject]@{ Status='ATOMIC_PASS'; Method='atomic'; RemoteMain=$afterAtomic.Main; RemoteProduction=$afterAtomic.Production; RemoteTag=$afterAtomic.Tag; AtomicError='' } }
  $unchanged = (Test-ReleaseOidEqual $afterAtomic.Main $before.Main) -and (Test-ReleaseOidEqual $afterAtomic.Production $before.Production) -and (Test-ReleaseOidEqual $afterAtomic.Tag $before.Tag)
  $unsupported = $atomic.StdErr -match '(?i)(does not support.*atomic|atomic.*not supported|unsupported.*atomic)'
  if (-not $unchanged) { return [pscustomobject]@{ Status='PARTIAL_FAILURE'; Method='atomic'; RemoteMain=$afterAtomic.Main; RemoteProduction=$afterAtomic.Production; RemoteTag=$afterAtomic.Tag; AtomicError=$atomic.StdErr } }
  if (-not $unsupported) { return [pscustomobject]@{ Status='ATOMIC_FAILED'; Method='atomic'; RemoteMain=$afterAtomic.Main; RemoteProduction=$afterAtomic.Production; RemoteTag=$afterAtomic.Tag; AtomicError=$atomic.StdErr } }
  foreach ($item in @([pscustomobject]@{ Name='Main'; Spec=$specs[0]; Desired=$desired.Main }, [pscustomobject]@{ Name='Production'; Spec=$specs[1]; Desired=$desired.Production }, [pscustomobject]@{ Name='Tag'; Spec=$specs[2]; Desired=$desired.Tag })) {
    $push = Invoke-PublicationGit -Root $Root -Arguments @('push', 'origin', $item.Spec) -CommandAdapter $CommandAdapter
    $state = & $readRemote
    $actual = $state.($item.Name)
    if ($push.ExitCode -ne 0 -or -not (Test-ReleaseOidEqual $actual $item.Desired)) { return [pscustomobject]@{ Status='PARTIAL_FAILURE'; Method='fallback'; RemoteMain=$state.Main; RemoteProduction=$state.Production; RemoteTag=$state.Tag; AtomicError=$atomic.StdErr } }
  }
  $final = & $readRemote
  return [pscustomobject]@{ Status='FALLBACK_PASS'; Method='fallback'; RemoteMain=$final.Main; RemoteProduction=$final.Production; RemoteTag=$final.Tag; AtomicError=$atomic.StdErr }
}

function New-GitHubRelease {
  [CmdletBinding()]
  param([Parameter(Mandatory)] [string] $Root, [Parameter(Mandatory)] $PreparedRelease)
  $existing = & gh release view $PreparedRelease.Tag 2>&1
  Assert-ReleaseCondition ($LASTEXITCODE -ne 0) "GitHub Release already exists for tag: $($PreparedRelease.Tag)"
  $provenance = "TradingBot-Main-Source: $($PreparedRelease.MainSha)"
  $sourceNote = if ($PreparedRelease.ProductionChanged) { 'Production commit carries the provenance trailer.' } else { 'Production tree was unchanged; provenance is tag-sourced.' }
  $created = & gh release create $PreparedRelease.Tag --target $PreparedRelease.ProductionSha --title $PreparedRelease.Tag --notes "$provenance`n$sourceNote" 2>&1
  Assert-ReleaseCondition ($LASTEXITCODE -eq 0) 'Could not create GitHub Release after ref publication.'
  return [pscustomobject]@{ Status='PASS'; Url=($created | Select-Object -Last 1).ToString().Trim() }
}

function Invoke-TradingBotRelease {
  [CmdletBinding()]
  param([Parameter(Mandatory)] [hashtable] $Parameters)
  $root = if ($Parameters.ContainsKey('Root')) { $Parameters.Root } else { Resolve-TradingBotProjectRoot -ScriptPath $Parameters.ScriptPath }
  $nonInteractive = $Parameters.ContainsKey('NonInteractive') -and [bool] $Parameters.NonInteractive
  $inputs = Read-ReleaseInputs -CommitMessage $Parameters.CommitMessage -ReleaseTag $Parameters.ReleaseTag -NonInteractive:$nonInteractive
  $preflight = Test-ReleasePreflight -Root $root -Tag $inputs.ReleaseTag -RequireGitHubCli
  Assert-ReleaseCondition ($preflight.Errors.Count -eq 0) ($preflight.Errors -join '; ')
  $containsRemoteMain = Invoke-ReleaseGit -Root $root -Arguments @('merge-base', '--is-ancestor', $preflight.RemoteMainSha, 'HEAD')
  Assert-ReleaseCondition ($containsRemoteMain.ExitCode -eq 0) 'Local main must contain fetched origin/main before release preparation.'
  $main = New-MainReleaseSource -Root $root -CommitMessage $inputs.CommitMessage -DryRun:([bool] $Parameters.DryRun)
  $policy = Import-ReleasePolicy -Root $root
  $fileSet = Get-ProductionFileSet -Root $root -MainSha $main.MainSha -Policy $policy
  $fileSetValidation = Test-ProductionFileSet -FileSet $fileSet -Policy $policy
  Assert-ReleaseCondition ($fileSet.Errors.Count -eq 0 -and $fileSetValidation.Errors.Count -eq 0) (($fileSet.Errors + $fileSetValidation.Errors) -join '; ')
  $snapshot = $null
  $outcome = $null
  try {
    $snapshot = New-ProductionSnapshot -Root $root -SourceMainSha $main.MainSha -ProductionBaseSha $preflight.ProductionBaseSha -FileSet $fileSet -CommitMessage $inputs.CommitMessage -DryRun:([bool] $Parameters.DryRun)
    $validation = Test-ProductionSnapshot -Snapshot $snapshot -RunRuntimeValidation
    Assert-ReleaseCondition ($validation.Errors.Count -eq 0) ($validation.Errors -join '; ')
    if ($Parameters.DryRun) {
      $outcome = [pscustomobject]@{ Mode='DRY_RUN'; LocalMain=$main.MainSha; LocalProduction=$snapshot.ProductionSha; RemoteMain=$preflight.RemoteMainSha; RemoteProduction=$preflight.ProductionBaseSha; Tag=$inputs.ReleaseTag; GitHubRelease='NOT_CREATED'; TemporaryWorktree='CLEANUP_PENDING'; Checks=@($validation.Checks) }
      return $outcome
    }
    $branch = Finalize-ProductionBranch -Root $root -Snapshot $snapshot
    $tag = New-ReleaseTag -Root $root -Tag $inputs.ReleaseTag -ProductionSha $branch.ProductionSha -MainSha $main.MainSha
    $prepared = [pscustomobject]@{ MainSha=$main.MainSha; ProductionSha=$branch.ProductionSha; ProductionChanged=$snapshot.ProductionChanged; Tag=$tag.Tag; TagObjectSha=$tag.TagObjectSha; RemoteMainSha=$preflight.RemoteMainSha; RemoteProductionSha=$preflight.ProductionBaseSha; RemoteTagSha=$null }
    $publication = Publish-ReleaseRefs -Root $root -PreparedRelease $prepared
    Assert-ReleaseCondition ($publication.Status -in @('ATOMIC_PASS','FALLBACK_PASS')) "Ref publication stopped with status: $($publication.Status)"
    $github = New-GitHubRelease -Root $root -PreparedRelease $prepared
    $outcome = [pscustomobject]@{ Mode='PUBLISHED'; LocalMain=$main.MainSha; LocalProduction=$branch.ProductionSha; RemoteMain=$publication.RemoteMain; RemoteProduction=$publication.RemoteProduction; Tag=$tag.Tag; GitHubRelease=$github.Url; TemporaryWorktree='CLEANUP_PENDING'; Publication=$publication; Checks=@($validation.Checks) }
    return $outcome
  } finally {
    if ($null -ne $snapshot) {
      Remove-TemporaryReleaseContext -Context $snapshot.Context
      if ($null -ne $outcome) { $outcome.TemporaryWorktree = 'CLEANUP_COMPLETE' }
    }
  }
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

Export-ModuleMember -Function Assert-ReleaseCondition, Resolve-TradingBotProjectRoot, Invoke-ReleaseGit, Import-ReleasePolicy, Get-MainPolicyReport, Test-SensitiveCandidate, Get-GitTreePaths, Get-GitBlobText, Get-ProductionFileSet, Test-ProductionFileSet, Test-ReleasePreflight, New-TemporaryReleaseContext, New-ProductionSnapshot, Test-ProductionSnapshot, Remove-TemporaryReleaseContext, Read-ReleaseInputs, New-ReleaseTag, Finalize-ProductionBranch, Publish-ReleaseRefs, New-GitHubRelease, Invoke-TradingBotRelease
