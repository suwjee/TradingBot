[CmdletBinding()]
param(
  [switch] $DryRun,
  [string] $CommitMessage = '',
  [string] $ReleaseTag = '',
  [switch] $VerboseReport
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Import-Module (Join-Path $PSScriptRoot 'Release.Workflow.psm1') -Force

$releaseParameters = @{
  ScriptPath = $PSCommandPath
  DryRun = [bool] $DryRun
  CommitMessage = $CommitMessage
  ReleaseTag = $ReleaseTag
}

try {
  $result = Invoke-TradingBotRelease -Parameters $releaseParameters
  $result | Select-Object Mode, LocalMain, LocalProduction, RemoteMain, RemoteProduction, Tag, GitHubRelease, TemporaryWorktree, Checks, Publication | Format-List
} catch {
  Write-Error $_.Exception.Message
  exit 1
}
