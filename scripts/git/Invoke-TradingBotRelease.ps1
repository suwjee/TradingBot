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
  $result | Select-Object Mode, LocalMain, LocalProduction, RemoteMain, RemoteProduction, RemoteTag, Tag, TagStatus, TagObjectSha, GitHubRelease, TemporaryWorktree, ProductionDrift, Publication, Error | Format-List
  if ($VerboseReport) { $result.Checks | Format-Table Name, Status, Detail -AutoSize }
  if ($result.Mode -notin @('DRY_RUN', 'PUBLISHED')) { exit 1 }
} catch {
  Write-Error $_.Exception.Message
  exit 1
}
