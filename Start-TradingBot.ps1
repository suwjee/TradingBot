[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$Root = [IO.Path]::GetFullPath($PSScriptRoot)
$ChartRoot = Join-Path $Root 'lightweight-charts'
# These are the only third-party imports used by the maintained Python runtime.
# Keep the list explicit so a clean machine is repaired deterministically.
$PythonPackages = @('orjson', 'tzdata')

function Write-Step([string]$Text, [ConsoleColor]$Color = 'Gray') {
  Write-Host ("[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $Text) -ForegroundColor $Color
}
function Find-Command([string[]]$Names) {
  foreach ($name in $Names) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
  }
  return $null
}
function Refresh-Path {
  $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' +
    [Environment]::GetEnvironmentVariable('Path','User')
}
function Install-Winget([string]$Id, [string]$Label) {
  $winget = Find-Command @('winget.exe','winget')
  if (-not $winget) { throw "winget is required to install $Label automatically. Install App Installer and retry." }
  Write-Step "Installing $Label..." Yellow
  & $winget install --id $Id --exact --silent --accept-package-agreements --accept-source-agreements
  if ($LASTEXITCODE -ne 0) { throw "Unable to install $Label (winget exit code $LASTEXITCODE)." }
  Refresh-Path
}
function Ensure-Path([string]$Path, [string]$Label) {
  if (-not (Test-Path -LiteralPath $Path)) { throw "Required $Label was not found: $Path" }
}
function Ensure-Directories {
  foreach ($relative in @('market-data\raw','primary-cache\drawings','primary-cache\indicator-calculations','primary-cache\indicator-templates','tmp\faraz-candle-exports')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $Root $relative) | Out-Null
  }
}
function Ensure-Runtimes {
  $node = Find-Command @('node.exe','node')
  if (-not $node) { Install-Winget 'OpenJS.NodeJS.LTS' 'Node.js LTS'; $node = Find-Command @('node.exe','node') }
  if (-not $node) { throw 'Node.js is unavailable after installation.' }
  $nodeVersion = [version]((& $node --version).Trim().TrimStart('v'))
  if ($nodeVersion -lt [version]'20.19.0') { Install-Winget 'OpenJS.NodeJS.LTS' 'Node.js LTS'; $node = Find-Command @('node.exe','node') }
  $npm = Find-Command @('npm.cmd','npm')
  if (-not $npm) { throw 'npm was not found alongside Node.js.' }
  $python = Find-Command @('python.exe','python','py.exe','py')
  if (-not $python) { Install-Winget 'Python.Python.3.12' 'Python 3.12'; $python = Find-Command @('python.exe','python','py.exe','py') }
  if (-not $python) { throw 'Python is unavailable after installation.' }
  foreach ($package in $PythonPackages) {
    & $python -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('$package') else 1)" 2>$null
    if ($LASTEXITCODE -ne 0) {
      Write-Step "Installing Python package $package..." Yellow
      & $python -m pip install --disable-pip-version-check --quiet $package
      if ($LASTEXITCODE -ne 0) { throw "Failed to install Python package $package." }
    }
  }
  $engineFiles = @(
    'indicator\indicator-settings\backend\reaction_bridge.py',
    'indicator\Modules\1_reaction-detector\app\Reaction-detection-new.py',
    'indicator\Modules\2_blue-line\app\blue_line.py',
    'indicator\Modules\3_A-zone\app\a_detector.py',
    'indicator\Modules\4_S-zones\app\s_detector.py',
    'indicator\Modules\5_E-zones\app\e_detector.py',
    'indicator\Modules\6_StopAll\app\stopall_detector.py'
  )
  foreach ($relative in $engineFiles) {
    $path = Join-Path $Root $relative
    & $python -m py_compile $path
    if ($LASTEXITCODE -ne 0) { throw "Python syntax validation failed: $relative" }
  }
  Write-Step ("Node {0}; npm {1}; {2}" -f (& $node --version).Trim(), (& $npm --version).Trim(), (& $python --version 2>&1).ToString().Trim()) Green
  return [pscustomobject]@{ Node=$node; Npm=$npm; Python=$python }
}
function Ensure-NpmDependencies([string]$Npm) {
  Ensure-Path (Join-Path $ChartRoot 'package.json') 'package manifest'
  Push-Location $ChartRoot
  try {
    $requiredNodeModules = @('vite', 'lightweight-charts', 'playwright-core')
    $missing = @($requiredNodeModules | Where-Object { -not (Test-Path -LiteralPath (Join-Path $ChartRoot ("node_modules\{0}" -f $_))) })
    if ($missing.Count -gt 0) {
      Write-Step 'Installing npm dependencies...' Yellow
      if (Test-Path -LiteralPath (Join-Path $ChartRoot 'package-lock.json')) { & $Npm ci } else { & $Npm install }
      if ($LASTEXITCODE -ne 0) { throw "npm dependency installation failed (exit code $LASTEXITCODE)." }
    }
    foreach ($module in $requiredNodeModules) {
      if (-not (Test-Path -LiteralPath (Join-Path $ChartRoot ("node_modules\{0}" -f $module)))) {
        throw "npm dependency is still missing after installation: $module"
      }
    }
  } finally { Pop-Location }
  Write-Step 'npm dependencies are ready.' Green
}
function Ensure-ProjectFiles {
  $required = @(
    'lightweight-charts\vite.config.js',
    'lightweight-charts\scripts\vite-dev.mjs',
    'indicator\indicator-settings\backend\reaction_bridge.py',
    'indicator\Modules\1_reaction-detector\app\Reaction-detection-new.py',
    'indicator\Modules\2_blue-line\app\blue_line.py',
    'indicator\Modules\3_A-zone\app\a_detector.py',
    'indicator\Modules\4_S-zones\app\s_detector.py',
    'indicator\Modules\5_E-zones\app\e_detector.py',
    'indicator\Modules\6_StopAll\app\stopall_detector.py'
  )
  foreach ($relative in $required) { Ensure-Path (Join-Path $Root $relative) $relative }
}
function Start-DevServer([string]$Npm, [string]$Python) {
  $env:TRADINGBOT_PYTHON = $Python
  Push-Location $ChartRoot
  try {
    Write-Step 'Starting npm run dev...' Cyan
    & $Npm run dev -- --host 0.0.0.0
    if ($LASTEXITCODE -ne 0) { throw "npm run dev exited with code $LASTEXITCODE." }
  } finally { Pop-Location }
}

try {
  Write-Step "Checking project at $Root" Cyan
  Ensure-ProjectFiles
  Ensure-Directories
  $tools = Ensure-Runtimes
  Ensure-NpmDependencies $tools.Npm
  Start-DevServer $tools.Npm $tools.Python
} catch {
  Write-Step $_.Exception.Message Red
  Write-Host "`nStartup failed. Press any key to close." -ForegroundColor Red
  $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
  exit 1
}
