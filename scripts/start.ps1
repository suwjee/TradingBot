[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$Root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$ChartRoot = Join-Path $Root 'apps\chart'
$ViteCommand = Join-Path $ChartRoot 'node_modules\vite\bin\vite.js'
$LocalStateRoot = $null
$env:PYTHONDONTWRITEBYTECODE = '1'

# Runtime dependencies used by the maintained Python engine.
$PythonPackages = @('orjson', 'tzdata')

# Required runtime entry points. Python module validation also discovers the
# current bridge and pipeline contents beneath their owning directories.
$EngineEntryPoints = @(
  'engine\bridge\trading_pipeline.py',
  'engine\bridge\live_pipeline.py'
)

$PythonPackageFiles = @(
  'engine\__init__.py',
  'engine\pipeline\__init__.py'
)

$ChartFiles = @(
  'apps\chart\package.json',
  'apps\chart\package-lock.json',
  'apps\chart\vite.config.js',
  'apps\chart\server\local-state-paths.js',
  'apps\chart\scripts\dev-server.mjs'
)

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

function Find-SupportedPython {
  $candidates = Get-Command -Name @('python.exe', 'python', 'py.exe', 'py') -CommandType Application -All -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty Source -Unique
  foreach ($candidate in $candidates) {
    try { $versionText = (& $candidate --version 2>$null | Out-String).Trim() }
    catch { continue }
    if ($LASTEXITCODE -eq 0 -and $versionText -match '^Python\s+(\d+\.\d+)' -and [version]$Matches[1] -ge [version]'3.12') {
      return [pscustomobject]@{ Path = $candidate; VersionText = $versionText }
    }
  }
  return $null
}

function Refresh-Path {
  $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
    [Environment]::GetEnvironmentVariable('Path', 'User')
}

function Install-Winget([string]$Id, [string]$Label) {
  $winget = Find-Command @('winget.exe', 'winget')
  if (-not $winget) {
    throw "winget is required to install $Label automatically. Install App Installer and retry."
  }

  Write-Step "Installing/updating $Label..." Yellow
  & $winget install --id $Id --exact --silent --accept-package-agreements --accept-source-agreements
  if ($LASTEXITCODE -ne 0) {
    throw "Unable to install/update $Label (winget exit code $LASTEXITCODE)."
  }
  Refresh-Path
}

function Ensure-Path([string]$Path, [string]$Label) {
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Required $Label was not found: $Path"
  }
}

function Ensure-ProjectFiles {
  $required = @($ChartFiles + $PythonPackageFiles + $EngineEntryPoints)
  foreach ($relative in $required) {
    Ensure-Path (Join-Path $Root $relative) $relative
  }

  $manifestPath = Join-Path $ChartRoot 'package.json'
  try {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
  } catch {
    throw "Invalid apps\\chart\\package.json: $($_.Exception.Message)"
  }

  if (-not $manifest.scripts -or -not $manifest.scripts.dev) {
    throw 'apps\\chart\\package.json must define scripts.dev.'
  }

  Write-Step 'Project structure matches the refactored TradingBot layout.' Green
}

function Ensure-Directories {
  $directories = @(
    'data\raw',
    'cache\drawings',
    'cache\indicator-calculations',
    'cache\indicator-templates',
    'secret',
    'tmp\faraz-candle-exports'
  )

  foreach ($relative in $directories) {
    New-Item -ItemType Directory -Force -Path (Join-Path $LocalStateRoot $relative) | Out-Null
  }
}

function Resolve-LocalState([string]$Node) {
  # Use the application's resolver so launcher and server enforce one path policy.
  $resolver = Join-Path $ChartRoot 'server\local-state-paths.js'
  $program = 'import { pathToFileURL } from ''node:url''; const { resolveLocalStatePaths } = await import(pathToFileURL(process.argv[1])); process.stdout.write(resolveLocalStatePaths(process.argv[2]).root);'
  $resolved = & $Node --input-type=module -e $program $resolver $Root
  if ($LASTEXITCODE -ne 0) { throw 'Unable to resolve the dedicated chart state directory.' }
  $script:LocalStateRoot = $resolved
  $env:TRADINGBOT_LOCAL_STATE_ROOT = $script:LocalStateRoot
}

function Test-NodeVersion([version]$Version) {
  # The app's locked Vite package requires ^20.19.0 || >=22.12.0.
  return ($Version.Major -eq 20 -and $Version -ge [version]'20.19.0') -or $Version -ge [version]'22.12.0'
}

function Ensure-Runtimes {
  $node = Find-Command @('node.exe', 'node')
  if (-not $node) {
    Install-Winget 'OpenJS.NodeJS.LTS' 'Node.js LTS'
    $node = Find-Command @('node.exe', 'node')
  }
  if (-not $node) { throw 'Node.js is unavailable after installation.' }

  $nodeVersion = [version]((& $node --version).Trim().TrimStart('v'))
  if (-not (Test-NodeVersion $nodeVersion)) {
    Install-Winget 'OpenJS.NodeJS.LTS' 'Node.js LTS'
    $node = Find-Command @('node.exe', 'node')
    if (-not $node) { throw 'Node.js is unavailable after update.' }
    $nodeVersion = [version]((& $node --version).Trim().TrimStart('v'))
    if (-not (Test-NodeVersion $nodeVersion)) {
      throw "Node.js 20.19+ in the 20.x line or 22.12+ is required; found $nodeVersion."
    }
  }

  $npm = Find-Command @('npm.cmd', 'npm')
  if (-not $npm) { throw 'npm was not found alongside Node.js.' }

  $pythonRuntime = Find-SupportedPython
  if (-not $pythonRuntime) {
    Install-Winget 'Python.Python.3.12' 'Python 3.12'
    $pythonRuntime = Find-SupportedPython
  }
  if (-not $pythonRuntime) { throw 'A working Python 3.12 or newer was not found after installation.' }
  $python = $pythonRuntime.Path

  $findMissing = 'import importlib.util, sys; print(chr(10).join(p for p in sys.argv[1:] if importlib.util.find_spec(p) is None))'
  $missingPackages = @(& $python -B -c $findMissing @PythonPackages)
  if ($LASTEXITCODE -ne 0) { throw 'Unable to check the Python packages.' }
  foreach ($package in $missingPackages) {
    if (-not $package) { continue }
    Write-Step "Installing Python package $package..." Yellow
    & $python -m pip install --disable-pip-version-check --quiet $package
    if ($LASTEXITCODE -ne 0) { throw "Failed to install Python package $package." }
  }

  $checkSyntax = "import ast,pathlib,sys; engine=pathlib.Path(sys.argv[1])/'engine'; paths=[engine/'__init__.py', *(engine/'bridge').rglob('*.py'), *(engine/'pipeline').rglob('*.py')]; [ast.parse(path.read_bytes(), filename=str(path)) for path in paths if '__pycache__' not in path.parts]"
  & $python -B -c $checkSyntax $Root
  if ($LASTEXITCODE -ne 0) { throw 'Python Engine syntax validation failed.' }

  Write-Step "Node v$nodeVersion and $($pythonRuntime.VersionText)" Green

  return [pscustomobject]@{
    Node = $node
    Npm = $npm
    Python = $python
  }
}

function Ensure-NpmDependencies([string]$Npm) {
  Push-Location $ChartRoot
  try {
    $requiredFiles = @(
      $ViteCommand
      (Join-Path $ChartRoot 'node_modules\vite\package.json')
      (Join-Path $ChartRoot 'node_modules\lightweight-charts\package.json')
      (Join-Path $ChartRoot 'node_modules\playwright-core\package.json')
    )
    $lockPath = Join-Path $ChartRoot 'package-lock.json'
    $lockStampPath = Join-Path $ChartRoot 'node_modules\.tradingbot-lock-sha256'
    if (-not (Test-Path -LiteralPath $lockPath -PathType Leaf)) {
      throw 'apps/chart/package-lock.json is required for a reproducible npm installation.'
    }
    $sha256 = [Security.Cryptography.SHA256]::Create()
    try {
      $stream = [IO.File]::OpenRead($lockPath)
      try {
        $lockHash = [BitConverter]::ToString($sha256.ComputeHash($stream)).Replace('-', '')
      } finally { $stream.Dispose() }
    } finally { $sha256.Dispose() }
    $installedLockHash = if (Test-Path -LiteralPath $lockStampPath -PathType Leaf) {
      [IO.File]::ReadAllText($lockStampPath).Trim()
    }

    $missing = @($requiredFiles | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
    if ($missing.Count -gt 0 -or $lockHash -ne $installedLockHash) {
      Write-Step 'Installing npm dependencies for this checkout...' Yellow
      & $Npm ci --include=dev
      if ($LASTEXITCODE -ne 0) {
        throw "npm dependency installation failed (exit code $LASTEXITCODE)."
      }
      foreach ($file in $requiredFiles) {
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
          throw "npm dependency file is still missing after installation: $file"
        }
      }
      Set-Content -LiteralPath $lockStampPath -Value $lockHash -Encoding ASCII
    }
  } finally {
    Pop-Location
  }

  Write-Step 'npm dependencies are ready.' Green
}

function Start-DevServer([string]$Node, [string]$Python) {
  $env:TRADINGBOT_PYTHON = $Python
  $env:TRADINGBOT_PROJECT_ROOT = $Root

  if (-not (Test-Path -LiteralPath $ViteCommand -PathType Leaf)) { throw 'The Vite command is missing. Check the npm installation.' }
  Push-Location $ChartRoot
  try {
    Write-Step 'Starting TradingBot development server...' Cyan
    # Vite's bundled config loader corrupts paths on the VMware shared drive.
    # Native loading keeps the launcher's reported LAN addresses routable.
    & $Node $ViteCommand --host 0.0.0.0 --configLoader native
    if ($LASTEXITCODE -ne 0) {
      throw "Vite exited with code $LASTEXITCODE."
    }
  } finally {
    Pop-Location
  }
}

try {
  Write-Step "Checking project at $Root" Cyan
  Ensure-ProjectFiles
  $tools = Ensure-Runtimes
  Resolve-LocalState $tools.Node
  Ensure-Directories
  Ensure-NpmDependencies $tools.Npm
  Start-DevServer $tools.Node $tools.Python
} catch {
  Write-Step $_.Exception.Message Red
  exit 1
}
