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

Export-ModuleMember -Function Assert-ReleaseCondition, Resolve-TradingBotProjectRoot, Invoke-ReleaseGit, Import-ReleasePolicy, Get-MainPolicyReport, Test-SensitiveCandidate
