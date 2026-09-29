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

  $records = @(& git -C $WorkingDirectory @Arguments 2>&1)
  $stdout = @($records | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] } | ForEach-Object { $_.ToString() })
  $stderr = @($records | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] } | ForEach-Object { $_.ToString() })
  return [pscustomobject]@{
    ExitCode = $LASTEXITCODE
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
    Paths = @($selected | Sort-Object)
    Drift = @($drift | Sort-Object)
    Errors = @($errors)
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

Export-ModuleMember -Function Assert-ReleaseCondition, Resolve-TradingBotProjectRoot, Invoke-ReleaseGit, Import-ReleasePolicy, Get-MainPolicyReport, Test-SensitiveCandidate, Get-GitTreePaths, Get-GitBlobText, Get-ProductionFileSet, Test-ProductionFileSet
