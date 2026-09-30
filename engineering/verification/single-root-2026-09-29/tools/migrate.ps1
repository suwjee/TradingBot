$ErrorActionPreference = 'Stop'
$migrationRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..\..'))
$externalRoot = [IO.Path]::GetFullPath($migrationRoot + '-Local')
$reportRoot = Split-Path -Parent $PSScriptRoot
$records = Get-Content -LiteralPath (Join-Path $reportRoot 'inventory.json') -Raw | ConvertFrom-Json

function Assert-Contained([string]$value, [string]$boundary) {
    $absolute = [IO.Path]::GetFullPath($value)
    $prefix = $boundary.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    if (-not $absolute.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside the verified migration boundary: $absolute"
    }
    return $absolute
}

# Validate the entire migration before its first move. Every destination is unique.
foreach ($record in $records) {
    $sourceRoot = if ($record.origin -eq 'external') { $externalRoot } else { $migrationRoot }
    $source = Assert-Contained (Join-Path $sourceRoot $record.source) $sourceRoot
    $target = Assert-Contained (Join-Path $migrationRoot $record.destination) $migrationRoot
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        if ($record.action -eq 'move' -and (Test-Path -LiteralPath $target -PathType Leaf)) {
            if ($record.sha256 -and (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $record.sha256) {
                throw "Previously moved input differs: $target"
            }
            continue
        }
        throw "Missing migration input: $source"
    }
    if ($record.sha256 -and (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $record.sha256) {
        throw "Migration input changed since inventory: $source"
    }
    if ($record.action -eq 'move' -and (Test-Path -LiteralPath $target)) { throw "Destination already exists: $target" }
}

$completed = [Collections.Generic.List[object]]::new()
foreach ($record in $records | Where-Object action -eq 'move') {
    $sourceRoot = if ($record.origin -eq 'external') { $externalRoot } else { $migrationRoot }
    $source = Assert-Contained (Join-Path $sourceRoot $record.source) $sourceRoot
    $target = Assert-Contained (Join-Path $migrationRoot $record.destination) $migrationRoot
    if (-not (Test-Path -LiteralPath $source) -and (Test-Path -LiteralPath $target)) {
        $completed.Add([pscustomobject]@{ origin=$record.origin; source=$record.source; destination=$record.destination })
        continue
    }
    New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
    Move-Item -LiteralPath $source -Destination $target -ErrorAction Stop
    $completed.Add([pscustomobject]@{ origin=$record.origin; source=$record.source; destination=$record.destination })
}
$completed | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $reportRoot 'completed-moves.json') -Encoding utf8
Write-Output ("Moved {0} files without overwriting any destination." -f $completed.Count)

# Remove empty superseded directory shells only, deepest first, without recursion.
foreach ($oldRoot in @($externalRoot, (Join-Path $migrationRoot 'docs'), (Join-Path $migrationRoot 'scripts'), (Join-Path $migrationRoot 'tests'))) {
    $absoluteRoot = [IO.Path]::GetFullPath($oldRoot)
    if ($absoluteRoot -ne $externalRoot) { $null = Assert-Contained $absoluteRoot $migrationRoot }
    if (Test-Path -LiteralPath $absoluteRoot -PathType Container) {
        $directories = @(Get-ChildItem -LiteralPath $absoluteRoot -Directory -Recurse -Force | Sort-Object { $_.FullName.Length } -Descending)
        foreach ($directory in $directories) {
            $null = Assert-Contained $directory.FullName $absoluteRoot
            if (@(Get-ChildItem -LiteralPath $directory.FullName -Force).Count -eq 0) {
                Remove-Item -LiteralPath $directory.FullName -Force -ErrorAction Stop
            }
        }
        if (@(Get-ChildItem -LiteralPath $absoluteRoot -Force).Count -eq 0) {
            Remove-Item -LiteralPath $absoluteRoot -Force -ErrorAction Stop
        }
    }
}
Write-Output ("External project directory still exists: {0}" -f (Test-Path -LiteralPath $externalRoot))
