$ErrorActionPreference = 'Stop'
$ProjectRoot = [IO.Path]::GetFullPath('D:\My-Projects\TradingBot').TrimEnd('\')
$StateRoot = [IO.Path]::GetFullPath('D:\My-Projects\TradingBot-Local').TrimEnd('\')
$AuditRoot = Join-Path $StateRoot 'cleanup-2026-09-29'
$ArchiveRoot = Join-Path $StateRoot 'archive'
$Actions = [Collections.Generic.List[object]]::new()

function Confirm-Source([string]$Target) {
    $absolute = [IO.Path]::GetFullPath($Target)
    if (-not $absolute.StartsWith($ProjectRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Source escapes the authorized project: $absolute"
    }
    return $absolute
}

function Move-Verified([string]$Relative, [string]$Destination, [string]$Reason) {
    $source = Confirm-Source (Join-Path $ProjectRoot $Relative)
    $target = [IO.Path]::GetFullPath($Destination)
    if (-not ($target.StartsWith($ProjectRoot + '\', [StringComparison]::OrdinalIgnoreCase) -or $target.StartsWith($StateRoot + '\', [StringComparison]::OrdinalIgnoreCase))) {
        throw "Destination escapes authorized roots: $target"
    }
    if (-not (Test-Path -LiteralPath $source)) { return }
    if (Test-Path -LiteralPath $target) { throw "Destination already exists: $target" }
    $items = if (Test-Path -LiteralPath $source -PathType Container) { @(Get-ChildItem -LiteralPath $source -File -Force -Recurse) } else { @(Get-Item -LiteralPath $source) }
    $hashes = @{}
    foreach ($item in $items) {
        if ($item.FullName -notmatch '[\\/]secret[\\/]') {
            $suffix = $item.FullName.Substring($source.Length)
            $hashes[$suffix] = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash
        }
    }
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    Move-Item -LiteralPath $source -Destination $target
    foreach ($suffix in $hashes.Keys) {
        $moved = $target + $suffix
        if ((Get-FileHash -LiteralPath $moved -Algorithm SHA256).Hash -ne $hashes[$suffix]) { throw "Moved bytes differ: $Relative" }
    }
    $Actions.Add([pscustomobject]@{source=$Relative.Replace('\','/');destination=$target;action='MOVE';reason=$Reason;files=$items.Count;verifiedHashes=$hashes.Count})
    $Actions | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $AuditRoot 'migration-actions.json') -Encoding utf8
}

function Remove-Generated([string]$Relative) {
    $target = Confirm-Source (Join-Path $ProjectRoot $Relative)
    if (-not (Test-Path -LiteralPath $target)) { return }
    $count = @(Get-ChildItem -LiteralPath $target -File -Recurse -Force).Count
    Remove-Item -LiteralPath $target -Recurse -Force
    $Actions.Add([pscustomobject]@{source=$Relative.Replace('\','/');destination='';action='DELETE';reason='Regenerable dependency/build/cache output';files=$count})
    $Actions | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $AuditRoot 'migration-actions.json') -Encoding utf8
}

Move-Verified 'data' (Join-Path $StateRoot 'data') 'Immutable RAW and metadata move to external storage'
Move-Verified 'runtime\cache\secret' (Join-Path $StateRoot 'secret') 'Persistent authentication state moves outside Git'
Move-Verified 'runtime\cache' (Join-Path $StateRoot 'cache') 'Preserve drawing, calculation and template state'
Move-Verified 'runtime' (Join-Path $StateRoot 'runtime') 'Preserve remaining local runtime state'
Move-Verified 'tmp' (Join-Path $StateRoot 'tmp') 'Preserve local temporary storage externally'
Move-Verified 'graphify-out' (Join-Path $ArchiveRoot 'graphify-out') 'Preserve pre-existing staged generated Graphify work externally'
Move-Verified 'docs\graphify' (Join-Path $ArchiveRoot 'docs\graphify') 'Preserve historical Graphify evidence outside repository'
Move-Verified 'docs\hpzr2-regression-2026-09-23\synthetic-benchmark\bench.py' (Join-Path $ProjectRoot 'tests\engine\benchmarks\bench.py') 'Reusable local benchmark helper'
Move-Verified 'docs\hpzr2-regression-2026-09-23\synthetic-benchmark\generate_fixture.py' (Join-Path $ProjectRoot 'tests\engine\benchmarks\generate_fixture.py') 'Reusable local synthetic input generator'
Copy-Item -LiteralPath (Join-Path $ProjectRoot 'docs\hpzr2-regression-2026-09-23\README.md') -Destination (Join-Path $AuditRoot 'HPZR2_Projection_Report.md')
Move-Verified 'docs\hpzr2-regression-2026-09-23' (Join-Path $ArchiveRoot 'docs\hpzr2-regression-2026-09-23') 'Preserve irreplaceable historical regression evidence externally'
Move-Verified 'docs\order-architecture-2026-09-27' (Join-Path $ArchiveRoot 'docs\order-architecture-2026-09-27') 'Preserve baseline/source recovery/regression archives externally'
Move-Verified 'docs\validation-temp' (Join-Path $ArchiveRoot 'docs\validation-temp') 'Historical temporary build evidence'

$DocMoves = @{
    'TradingBot_Technical_Architecture.md' = 'architecture\TradingBot_Technical_Architecture.md'
    'TradingBot_UI_UX_Technical_Reference.md' = 'architecture\TradingBot_UI_UX_Technical_Reference.md'
    'TradingBot_AI_Operating_Protocol.md' = 'development\TradingBot_AI_Operating_Protocol.md'
    'TradingBot_Repository_Baseline.md' = 'history\TradingBot_Repository_Baseline.md'
    'TradingBot_Project_Audit.md' = 'history\TradingBot_Project_Audit.md'
    'TradingBot_Cleanup_Report.md' = 'history\TradingBot_Cleanup_Report.md'
    'TradingBot_Validation_Report.md' = 'history\TradingBot_Validation_Report.md'
    'TradingBot — High-Performance Zero-Difference Refactor Specification.md' = 'development\Zero_Difference_Refactor_Specification.md'
    'TradingBot — Master Prompt for Complete Standalone Bullish & Bearish Algorithm References.md' = 'development\Standalone_Reference_Specification.md'
}
foreach ($name in $DocMoves.Keys) { Move-Verified ('docs\' + $name) (Join-Path $ProjectRoot ('docs\' + $DocMoves[$name])) 'Organize durable documentation by purpose' }
foreach ($name in @('TradingBot_Bullish_Algorithm_Reference.md','TradingBot_Bearish_Algorithm_Reference.md','AGEN.md','Complete Project Engineering Audit.md')) {
    Move-Verified ('docs\' + $name) (Join-Path $ArchiveRoot ('docs\' + $name)) 'Superseded reference/operating-guide/request; preserve historical bytes externally'
}
Move-Verified 'docs\superpowers\specs\2026-09-23-bridge-output-projection-design.md' (Join-Path $ProjectRoot 'docs\development\specs\Bridge_Output_Projection.md') 'Retain durable interface design in normal documentation'
Move-Verified 'docs\superpowers\plans\2026-09-23-bridge-output-projection.md' (Join-Path $ProjectRoot 'docs\development\plans\2026-09-23-bridge-output-projection.md') 'Retain implementation plan with explicit historical status'
Move-Verified 'docs\superpowers' (Join-Path $ArchiveRoot 'docs\superpowers') 'Retire completed historical tool-specific audit plans'

Move-Verified 'apps\chart\tests' (Join-Path $ProjectRoot 'tests\chart\unit') 'Centralize local chart contract tests'
Move-Verified 'tests\local-state-paths.test.mjs' (Join-Path $ProjectRoot 'tests\chart\unit\local-state-paths.test.mjs') 'Local storage path regression'
foreach ($name in @('test_order_audit_lifecycle_contracts.py','test_order_b_reset_leg.py')) {
    Move-Verified ('tests\' + $name) (Join-Path $ProjectRoot ('tests\engine\unit\' + $name)) 'Centralize local engine unit tests'
}
foreach ($name in @('verify_order_references.py','verify_order_b_raw.py')) {
    Move-Verified ('tests\' + $name) (Join-Path $ProjectRoot ('tests\engine\helpers\' + $name)) 'Centralize local verification helpers'
}
foreach ($name in @('order_regression.py','compare_order_regressions.py','hpzr2_regression.py','hpzr2_verify_saved.py')) {
    Move-Verified ('scripts\' + $name) (Join-Path $ProjectRoot ('tests\engine\regression\' + $name)) 'Move test-only tools out of operational scripts'
}
foreach ($name in @('extract_order_module.py','extract_s_order_methods.py','build_order_references.py')) {
    Move-Verified ('scripts\' + $name) (Join-Path $ArchiveRoot ('scripts\' + $name)) 'Completed one-off extraction/reference generator uses superseded baseline/version defaults'
}

Remove-Generated 'apps\chart\node_modules'
Remove-Generated 'apps\chart\dist'
Remove-Generated 'apps\chart\ Folders'
Remove-Generated 'apps\chart\Folders'
Remove-Generated '.pytest_cache'
Remove-Generated '.benchmarks'
$CacheDirectories = @(Get-ChildItem -LiteralPath $ProjectRoot -Directory -Recurse -Force | Where-Object { $_.FullName -notlike "$ProjectRoot\.git\*" -and $_.Name -in @('__pycache__','.vite','.vite-temp','.cache') } | Sort-Object { $_.FullName.Length } -Descending)
foreach ($directory in $CacheDirectories) { Remove-Generated $directory.FullName.Substring($ProjectRoot.Length + 1) }
foreach ($file in @(Get-ChildItem -LiteralPath $ProjectRoot -File -Recurse -Force | Where-Object { $_.FullName -notlike "$ProjectRoot\.git\*" -and $_.Extension -in @('.pyc','.pyo') })) {
    $target = Confirm-Source $file.FullName
    Remove-Item -LiteralPath $target -Force
}
$Actions | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $AuditRoot 'migration-actions.json') -Encoding utf8
Write-Output ('Migration operations: ' + $Actions.Count)
