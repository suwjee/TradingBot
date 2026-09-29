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

Export-ModuleMember -Function Assert-ReleaseCondition, Resolve-TradingBotProjectRoot, Invoke-ReleaseGit
