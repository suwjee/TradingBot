$ErrorActionPreference = 'Stop'
$verificationProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..'))
$Root = $verificationProjectRoot
$ChartRoot = Join-Path $Root 'apps\chart'
$launcherPath = Join-Path $Root 'scripts\start.ps1'
$tokens = $null
$errors = $null
$launcherAst = [Management.Automation.Language.Parser]::ParseFile($launcherPath, [ref]$tokens, [ref]$errors)
if ($errors.Count -gt 0) { throw ($errors | Out-String) }
foreach ($functionName in @('Resolve-LocalState', 'Ensure-Directories')) {
    $definition = $launcherAst.Find({ param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $functionName }, $true)
    if (-not $definition) { throw "Missing launcher function: $functionName" }
    . ([scriptblock]::Create($definition.Extent.Text))
}
$nodeCommand = (Get-Command node.exe).Source
$env:TRADINGBOT_LOCAL_STATE_ROOT = $null
Resolve-LocalState $nodeCommand
if ($LocalStateRoot -ne (Join-Path $Root 'apps\chart\state')) { throw 'Launcher default state differs.' }
Ensure-Directories
$env:TRADINGBOT_LOCAL_STATE_ROOT = 'apps/chart/state'
Resolve-LocalState $nodeCommand
if ($LocalStateRoot -ne (Join-Path $Root 'apps\chart\state')) { throw 'Launcher relative state differs.' }
$env:TRADINGBOT_LOCAL_STATE_ROOT = Join-Path $Root 'engine'
$rejected = $false
try { Resolve-LocalState $nodeCommand } catch { $rejected = $true }
if (-not $rejected) { throw 'Launcher accepted a source directory.' }
$env:TRADINGBOT_LOCAL_STATE_ROOT = $null
Write-Output 'PASS: Windows launcher AST, shared resolver default/relative/reject-source, and internal directory creation.'
