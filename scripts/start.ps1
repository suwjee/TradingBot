[CmdletBinding()]
param(
  [switch]$Console,
  [switch]$SkipUpdateCheck,
  [switch]$Loopback,
  [switch]$AfterUpdate
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$script:OnWindows = [Environment]::OSVersion.Platform -eq 'Win32NT'
$script:screenActive = $false
$script:escape = [string][char]27
$script:checks = @('Project', 'Node', 'Python', 'Python packages', 'Chart packages', 'Local state')
$script:runner = [ordered]@{
  Version = 'Checking'; Latest = 'Checking'; Internet = 'Checking'; Update = 'Checking'; UpdateNotice = ''
  Project = 'Pending'; Node = 'Pending'; Python = 'Pending'
  'Python packages' = 'Pending'; 'Chart packages' = 'Pending'; 'Local state' = 'Pending'
  Server = 'Starting'; ServerPid = $null; ServerSince = $null
  NodePath = $null; PythonPath = $null; Branch = ''; ChartVersion = ''; LocalUrl = ''
}
$script:pendingUpdate = $null
$script:updateProgress = @{ Stage = ''; Complete = 0; Download = -1 }
$script:activity = [Collections.Generic.List[object]]::new()
$script:addresses = @('Waiting for the Chart server')
$script:controls = 'Ctrl+C  Stop'
$script:screenView = @{ Mode = 'Activity'; Offset = 0; Size = ''; Previous = @(); Message = '' }

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

# Run the app's Vite configuration in Node. Emit the actual bound port only
# after the chart page responds, including when Vite moves off its usual port.
$ServerProgram = @'
import { createServer } from 'vite';
const server = await createServer({
  configLoader: 'native',
  server: { host: process.argv.includes('--loopback') ? '127.0.0.1' : '0.0.0.0' },
});
try {
  await server.listen();
  const { port } = server.httpServer.address();
  const page = await fetch(`http://127.0.0.1:${port}/`, {
    signal: AbortSignal.timeout(15_000),
  });
  await page.text();
  if (!page.ok) throw new Error(`TradingBot returned HTTP ${page.status} during startup.`);
  process.stdin.once('end', () => {
    server.close().catch((error) => {
      console.error(error);
      process.exitCode = 1;
    });
  });
  process.stdin.resume();
  console.log(`TRADINGBOT_VITE_READY ${port}`);
} catch (error) {
  await server.close();
  throw error;
}
'@

function Get-LauncherAddresses([int]$Port) {
  '{0,-5}  {1}' -f 'Local', "http://localhost:$Port/"
  if ($Loopback) { return }
  $seen = [Collections.Generic.HashSet[string]]::new()
  foreach ($adapter in [Net.NetworkInformation.NetworkInterface]::GetAllNetworkInterfaces() | Sort-Object Name) {
    if ($adapter.OperationalStatus -ne 'Up' -or $adapter.NetworkInterfaceType -eq 'Loopback') { continue }
    foreach ($entry in $adapter.GetIPProperties().UnicastAddresses) {
      $ip = $entry.Address
      if ($ip.AddressFamily -eq 'InterNetwork' -and -not [Net.IPAddress]::IsLoopback($ip) -and $seen.Add([string]$ip)) {
        '{0,-5}  {1,-30}  {2}' -f 'LAN', "http://${ip}:$Port/", $adapter.Name
      }
    }
  }
}

function Get-LauncherShortcutRows([string]$Controls, [int]$Width) {
  if ($Controls -ne 'Server') { return '  ' + $Controls }

  $items = @(
    '[U] Updates', '[R] Restart', '[C] Copy URL', '[H] Health', '[Q/Ctrl+C] Quit',
    '[D] Details', '[E] Issues', '[PgUp/PgDn] Logs', '[End] Live'
  )
  $joined = '  ' + ($items -join '   ')
  if ($joined.Length -lt $Width) { return $joined }

  $line = ''
  for ($index = 0; $index -lt $items.Count; $index++) {
    $item = $items[$index]
    # Keep command keys together and wrap only between shortcuts.
    if ($line -and ($index -eq 5 -or $line.Length + $item.Length + 5 -ge $Width)) {
      '  ' + $line
      $line = ''
    }
    if ($line) { $line += '   ' }
    $line += $item
  }
  '  ' + $line
}

function Get-LauncherLayout([int]$Rows, [string[]]$Addresses, [object[]]$Events, [string]$Controls, [int]$Width = 80) {
  $header = [Collections.Generic.List[object]]::new()
  $header.Add(@{ Text = '  TRADINGBOT   /   WORKSTATION'; Style = '1;96' })
  $serverStyle = if ($script:runner.Server -eq 'Ready') { '1;92' } elseif ($script:runner.Server -eq 'Failed') { '1;91' } else { '1;93' }
  $serverLine = "  $($script:runner.Server.ToUpperInvariant())"
  if ($script:runner.ServerSince) {
    $uptime = [DateTime]::UtcNow - $script:runner.ServerSince
    $serverLine += '    PID {0}    Uptime {1:00}:{2:00}:{3:00}' -f $script:runner.ServerPid, [Math]::Floor($uptime.TotalHours), $uptime.Minutes, $uptime.Seconds
  }
  $header.Add(@{ Text = $serverLine; Style = $serverStyle })
  $header.Add(@{ Text = "  Installed  $($script:runner.Version)     |     GitHub production  $($script:runner.Latest)"; Style = '37' })
  $headline = if ($script:runner.UpdateNotice) { "$($script:runner.UpdateNotice)  |  $($script:runner.Update)" } else { $script:runner.Update }
  $updateStyle = if ($script:runner.UpdateNotice) { '1;93' } else { '37' }
  $header.Add(@{ Text = "  Internet   $($script:runner.Internet)     |     $headline"; Style = $updateStyle })
  if ($script:updateProgress.Stage) {
    $updateFill = [int][Math]::Floor($script:updateProgress.Complete / 5)
    $updateBar = ('=' * $updateFill) + ('.' * (20 - $updateFill))
    $header.Add(@{ Text = "  Update    [$updateBar]  $($script:updateProgress.Complete)%  $($script:updateProgress.Stage)"; Style = '1;96' })
    if ($script:updateProgress.Download -ge 0) {
      $filled = [int][Math]::Floor($script:updateProgress.Download / 5)
      $bar = ('=' * $filled) + ('.' * (20 - $filled))
      $header.Add(@{ Text = "  Download  [$bar]  $($script:updateProgress.Download)% of Git objects"; Style = '96' })
    }
  }
  $divider = '-' * ([Math]::Max(1, [Math]::Min($Width - 1, 100)))
  $header.Add(@{ Text = $divider; Style = '2;36' })
  $mode = $script:screenView.Mode
  if ($mode -ne 'Details' -and $Rows -ge (19 + $Addresses.Count)) {
    $header.Add(@{ Text = '  PREFLIGHT'; Style = '1;96' })
    foreach ($check in $script:checks) {
      $result = $script:runner[$check]
      $complete = $result -match '^(Ready|Node |Python )'
      $marker = if ($complete) { '[OK]' } elseif ($result -eq 'Failed') { '[!!]' } else { '[..]' }
      $style = if ($complete) { '92' } elseif ($result -eq 'Failed') { '91' } else { '37' }
      $header.Add(@{ Text = ('  {0}  {1,-16} {2}' -f $marker, $check, $result); Style = $style })
    }
    $header.Add(@{ Text = ''; Style = '0' })
  }
  $historyHint = if ($script:screenView.Offset) { ' / HISTORY' } else { '' }
  $heading = switch ($mode) {
    'Details' { 'DETAILS' }
    'Issues' { "ISSUES$historyHint" }
    default { "ACTIVITY$historyHint" }
  }
  $header.Add(@{ Text = '  ' + $heading; Style = '1;96' })

  $shortcuts = @(Get-LauncherShortcutRows $Controls $Width)
  if ($shortcuts.Count + 4 -gt $Rows) { $shortcuts = @('  Resize for shortcuts') }
  $addressSlots = [Math]::Max(0, $Rows - $shortcuts.Count - 4)
  $footer = [Collections.Generic.List[object]]::new()
  $footer.Add(@{ Text = $divider; Style = '2;36' })
  $footerHeading = '  ADDRESSES'
  if ($script:screenView.Message) { $footerHeading += '   |   ' + $script:screenView.Message }
  $hiddenAddresses = $Addresses.Count - $addressSlots
  if ($hiddenAddresses -gt 0) { $footerHeading += "   +$hiddenAddresses more (resize terminal)" }
  $footer.Add(@{ Text = $footerHeading; Style = '1;96' })
  foreach ($address in $Addresses | Select-Object -First $addressSlots) {
    $style = if ($address -like 'Local *') { '1;37' } elseif ($address -like 'LAN *') { '37' } else { '90' }
    $footer.Add(@{ Text = '  ' + $address; Style = $style })
  }
  foreach ($shortcutRow in $shortcuts) {
    $footer.Add(@{ Text = $shortcutRow; Style = '33' })
  }

  $headerSlots = [Math]::Max(0, $Rows - $footer.Count)
  $visibleHeader = @($header | Select-Object -First $headerSlots)
  $logSlots = $headerSlots - $visibleHeader.Count
  $visibleHeader
  if ($logSlots -gt 0) {
    $body = switch ($mode) {
      'Details' {
        "Project          $Root"
        "State            $script:LocalStateRoot"
        "Node             $($script:runner.NodePath)"
        "Python           $($script:runner.PythonPath)"
        "Checkout          $($script:runner.Branch)  |  Chart package $($script:runner.ChartVersion)"
        if ($Loopback) { 'Binding          Loopback only' } else { 'Binding          Local network' }
      }
      'Issues' { $Events | Where-Object { $_ -is [hashtable] -and $_.IsIssue } }
      default { $Events }
    }
    $body = @($body | Where-Object { $null -ne $_ })
    $end = if ($body.Count) { [Math]::Max(1, $body.Count - $script:screenView.Offset) } else { 0 }
    $visibleEvents = @($body | Select-Object -First $end | Select-Object -Last $logSlots)
    if (-not $visibleEvents.Count -and $mode -eq 'Issues') { $visibleEvents = @('No warnings or errors.') }
    foreach ($event in $visibleEvents) {
      if ($event -is [string]) { @{ Text = '  ' + $event; Style = '37' } }
      else { @{ Text = '  ' + $event.Text; Style = $event.Style } }
    }
    for ($line = $visibleEvents.Count; $line -lt $logSlots; $line++) { @{ Text = ''; Style = '0' } }
  }
  $footer
}

function Show-LauncherFrame {
  if (-not $script:screenActive) { return }
  $width = [Console]::WindowWidth
  $height = [Console]::WindowHeight
  if ($width -lt 12 -or $height -lt 5) { return }
  $rows = @(Get-LauncherLayout $height $script:addresses ($script:activity.ToArray()) $script:controls $width)
  $frame = [Text.StringBuilder]::new()
  $size = "${width}x$height"
  if ($size -ne $script:screenView.Size) {
    $script:screenView.Size = $size
    $script:screenView.Previous = @()
    [void]$frame.Append("$script:escape[2J")
  }
  $rendered = [Collections.Generic.List[string]]::new()
  for ($index = 0; $index -lt $rows.Count; $index++) {
    $text = $rows[$index].Text -replace '[\x00-\x1f\x7f-\x9f]', ' '
    if ($text.Length -ge $width) { $text = $text.Substring(0, $width - 1) }
    $line = "$script:escape[$($rows[$index].Style)m$text$script:escape[0m"
    $rendered.Add($line)
    if ($line -cne $script:screenView.Previous[$index]) {
      [void]$frame.Append("$script:escape[$($index + 1);1H$script:escape[2K$line")
    }
  }
  $script:screenView.Previous = $rendered.ToArray()
  if ($frame.Length) { [Console]::Write($frame.ToString()) }
}

function Set-LauncherViewKey([string]$Key) {
  switch ($Key) {
    'D' {
      $script:screenView.Mode = if ($script:screenView.Mode -eq 'Details') { 'Activity' } else { 'Details' }
      $script:screenView.Offset = 0
    }
    'E' {
      $script:screenView.Mode = if ($script:screenView.Mode -eq 'Issues') { 'Activity' } else { 'Issues' }
      $script:screenView.Offset = 0
    }
    'PageUp' {
      $script:screenView.Offset = [Math]::Min($script:activity.Count, $script:screenView.Offset + 4)
    }
    'PageDown' {
      $script:screenView.Offset = [Math]::Max(0, $script:screenView.Offset - 4)
    }
    'End' { $script:screenView.Offset = 0 }
  }
}

function Get-LauncherKeyName([ConsoleKeyInfo]$Key) {
  if ($Key.KeyChar -eq [char]3) { return 'Ctrl+C' }
  if ($Key.KeyChar -eq [char]27) { return 'Escape' }
  if ([char]::IsControl($Key.KeyChar)) { return [string]$Key.Key }
  # Terminal input can carry a printable character with no virtual-key code.
  return [string][char]::ToUpperInvariant($Key.KeyChar)
}

function Read-LauncherKey([switch]$Wait) {
  if ($script:screenActive -and ($Wait -or [Console]::KeyAvailable)) {
    Get-LauncherKeyName ([Console]::ReadKey($true))
  }
}

function Copy-LauncherLocalUrl {
  if (-not $script:runner.LocalUrl) {
    $script:screenView.Message = 'Local URL pending'
    return
  }
  try {
    Set-Clipboard -Value $script:runner.LocalUrl -ErrorAction Stop
    $script:screenView.Message = 'Local URL copied'
  } catch {
    $script:screenView.Message = 'Clipboard unavailable'
    Write-Step 'Copy the local address from the footer.' Yellow
  }
}

function Test-LauncherHttp {
  if (-not $script:runner.LocalUrl) {
    $script:screenView.Message = 'Local URL pending'
    return
  }
  $port = ([uri]$script:runner.LocalUrl).Port
  $script:screenView.Message = 'Checking Chart HTTP'
  Show-LauncherFrame
  $timer = [Diagnostics.Stopwatch]::StartNew()
  try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/" -UseBasicParsing -TimeoutSec 4 -MaximumRedirection 0 -ErrorAction Stop
    $script:screenView.Message = "HTTP $($response.StatusCode) in $($timer.ElapsedMilliseconds) ms"
    Write-Step "Chart health check: $($script:screenView.Message)" Green
  } catch {
    $script:screenView.Message = 'Chart HTTP check failed'
    Write-Step "Chart health check failed: $($_.Exception.Message)" Yellow
  }
}

function Write-LauncherEvent([string]$Kind, [string]$Value, [string]$Color = 'Gray') {
  # External command output may contain terminal control characters.
  $Value = $Value -replace '\x1b\[[0-?]*[ -/]*[@-~]', '' -replace '[\x00-\x1f\x7f-\x9f]', ' '
  if ($Kind -eq 'Log') {
    $style = @{ Gray = '37'; Cyan = '96'; Green = '92'; Yellow = '93'; Red = '91' }[$Color]
    if ($script:activity.Count -ge 350) { $script:activity.RemoveAt(0) }
    $issue = $Color -in @('Yellow', 'Red')
    $script:activity.Add(@{ Text = $Value; Style = $style; IsIssue = $issue })
    if ($script:screenView.Offset -and ($script:screenView.Mode -eq 'Activity' -or ($script:screenView.Mode -eq 'Issues' -and $issue))) {
      $script:screenView.Offset = [Math]::Min($script:activity.Count, $script:screenView.Offset + 1)
    }
  } elseif ($Kind -eq 'Ready') {
    $script:runner.Server = 'Ready'
    $script:runner.LocalUrl = "http://localhost:$Value/"
    $script:addresses = @(Get-LauncherAddresses ([int]$Value))
  } elseif ($Kind -eq 'Prompt') {
    $script:controls = "$Value [Y/N]"
  } else {
    $script:runner[$Kind] = $Value
  }

  if ($script:screenActive) { Show-LauncherFrame; return }
  if ($Kind -eq 'Log') {
    Write-Host $Value -ForegroundColor $Color
  } elseif ($Kind -eq 'Prompt') {
    Write-Host "$Value [Y/N] " -NoNewline -ForegroundColor Yellow
  } elseif ($Kind -eq 'Ready') {
    foreach ($address in $script:addresses) { Write-Host $address -ForegroundColor Cyan }
  } else {
    Write-Host ("{0,-8} {1}" -f $Kind, $Value) -ForegroundColor $Color
  }
}

function Write-Step([string]$Text, [ConsoleColor]$Color = 'Gray') {
  $prefix = switch ($Color) {
    'Red' { 'ERROR  ' }
    'Yellow' { 'WARN   ' }
    default { '' }
  }
  Write-LauncherEvent 'Log' ("[{0}] {1}{2}" -f (Get-Date -Format 'HH:mm:ss'), $prefix, $Text) $Color
}

function Write-UpdateProgress([string]$Stage, [int]$Completed, [int]$Download = -1) {
  if ($Completed -lt 0) { $Completed = $script:updateProgress.Complete }
  if ($Stage -eq $script:updateProgress.Stage -and $Completed -eq $script:updateProgress.Complete -and $Download -eq $script:updateProgress.Download) { return }
  $script:updateProgress = @{ Stage = $Stage; Complete = $Completed; Download = $Download }
  if ($script:screenActive) { Show-LauncherFrame }
  elseif ($Download -ge 0) { Write-Host "  $Stage - Download $Download%" -ForegroundColor Cyan }
  else { Write-Host "  $Stage - Update $Completed%" -ForegroundColor Cyan }
}

function Write-NativeLog {
  process {
    $line = [string]$_
    if ($line.Trim()) {
      $color = if ($_ -is [Management.Automation.ErrorRecord]) { 'Yellow' } else { 'Gray' }
      Write-Step $line $color
    }
  }
}

function Find-Command([string[]]$Names) {
  foreach ($name in $Names) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
  }
  return $null
}

function Find-SupportedPython {
  $candidates = Get-Command -Name @('python.exe', 'python3', 'python', 'py.exe', 'py') -CommandType Application -All -ErrorAction SilentlyContinue |
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
  if (-not $script:OnWindows) { throw "Install a supported $Label on this host and run the launcher again." }
  $winget = Find-Command @('winget.exe', 'winget')
  if (-not $winget) {
    throw "winget is required to install $Label automatically. Install App Installer and retry."
  }

  Write-Step "Installing/updating $Label..." Cyan
  & { $ErrorActionPreference = 'Continue'; & $winget install --id $Id --exact --silent --accept-package-agreements --accept-source-agreements 2>&1 | Write-NativeLog }
  if ($LASTEXITCODE -ne 0) { throw "Unable to install/update $Label (winget exit code $LASTEXITCODE)." }
  Refresh-Path
}

function Ensure-Path([string]$Path, [string]$Label) {
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Required $Label was not found: $Path"
  }
}

function Ensure-ProjectFiles {
  Write-LauncherEvent 'Project' 'Checking'
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

  Write-LauncherEvent 'Project' 'Ready' Green
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
  Write-LauncherEvent 'Node' 'Checking'
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
  $npmVersion = (& $npm --version 2>$null | Out-String).Trim()
  if ($LASTEXITCODE -ne 0 -or $npmVersion -notmatch '^\d+\.\d+\.\d+') { throw 'npm did not report a usable version.' }
  $script:runner.NodePath = $node
  Write-LauncherEvent 'Node' "Node v$nodeVersion / npm $npmVersion" Green

  Write-LauncherEvent 'Python' 'Checking'
  $pythonRuntime = Find-SupportedPython
  if (-not $pythonRuntime) {
    Install-Winget 'Python.Python.3.12' 'Python 3.12'
    $pythonRuntime = Find-SupportedPython
  }
  if (-not $pythonRuntime) { throw 'A working Python 3.12 or newer was not found after installation.' }
  $python = $pythonRuntime.Path
  $script:runner.PythonPath = $python
  Write-LauncherEvent 'Python' $pythonRuntime.VersionText Green

  Write-LauncherEvent 'Python packages' 'Checking'
  $findMissing = 'import importlib.util, sys; print(chr(10).join(p for p in sys.argv[1:] if importlib.util.find_spec(p) is None))'
  $missingPackages = @(& $python -B -c $findMissing @PythonPackages)
  if ($LASTEXITCODE -ne 0) { throw 'Unable to check the Python packages.' }
  if (@($missingPackages | Where-Object { $_ }).Count -gt 0 -and -not $script:OnWindows) {
    $venv = Join-Path $Root '.venv/tradingbot-launcher'
    $venvPython = Join-Path $venv 'bin/python'
    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
      Write-Step 'Creating the project Python environment...' Cyan
      & { $ErrorActionPreference = 'Continue'; & $python -m venv $venv 2>&1 | Write-NativeLog }
      if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment. Check that Python venv support is installed.' }
    }
    $python = $venvPython
    $script:runner.PythonPath = $python
    $missingPackages = @(& $python -B -c $findMissing @PythonPackages)
    if ($LASTEXITCODE -ne 0) { throw 'Unable to check the project Python environment.' }
  }
  foreach ($package in $missingPackages) {
    if (-not $package) { continue }
    Write-Step "Installing Python package $package..." Cyan
    & { $ErrorActionPreference = 'Continue'; & $python -m pip install --disable-pip-version-check --quiet $package 2>&1 | Write-NativeLog }
    if ($LASTEXITCODE -ne 0) { throw "Failed to install Python package $package." }
  }
  $checkImports = 'import importlib,sys; [importlib.import_module(name) for name in sys.argv[1:]]'
  & { $ErrorActionPreference = 'Continue'; & $python -B -c $checkImports @PythonPackages 2>&1 | Write-NativeLog }
  if ($LASTEXITCODE -ne 0) { throw 'Python Engine packages could not be imported.' }

  $checkSyntax = "import ast,pathlib,sys; engine=pathlib.Path(sys.argv[1])/'engine'; paths=[engine/'__init__.py', *(engine/'bridge').rglob('*.py'), *(engine/'pipeline').rglob('*.py')]; [ast.parse(path.read_bytes(), filename=str(path)) for path in paths if '__pycache__' not in path.parts]"
  & { $ErrorActionPreference = 'Continue'; & $python -B -c $checkSyntax $Root 2>&1 | Write-NativeLog }
  if ($LASTEXITCODE -ne 0) { throw 'Python Engine syntax validation failed.' }

  Write-LauncherEvent 'Python packages' ('Ready - ' + ($PythonPackages -join ', ')) Green

  return [pscustomobject]@{
    Node = $node
    Npm = $npm
    Python = $python
  }
}

function Ensure-NpmDependencies([string]$Npm) {
  Write-LauncherEvent 'Chart packages' 'Checking'
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
      Write-Step 'Installing npm dependencies for this checkout...' Cyan
      & { $ErrorActionPreference = 'Continue'; & $Npm ci --include=dev 2>&1 | Write-NativeLog }
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

  Write-LauncherEvent 'Chart packages' 'Ready - lockfile verified' Green
}

function Start-DevServer([string]$Node, [string]$Python) {
  $env:TRADINGBOT_PYTHON = $Python
  $env:TRADINGBOT_PROJECT_ROOT = $Root

  $serverArgs = @('--input-type=module', '--eval', $ServerProgram, '--')
  if ($Loopback) { $serverArgs += '--loopback' }
  $processInfo = New-LauncherProcessInfo $Node $ChartRoot $serverArgs
  $processInfo.RedirectStandardInput = $true
  $process = [Diagnostics.Process]::Start($processInfo)
  $oldControlMode = $false
  try {
    $script:addresses = @('Waiting for the Chart server')
    $script:runner.LocalUrl = ''
    $script:screenView.Message = ''
    $script:controls = 'Server'
    $script:runner.ServerPid = $process.Id
    $script:runner.ServerSince = [DateTime]::UtcNow
    Write-LauncherEvent 'Server' 'Starting' Cyan
    if ($script:screenActive) {
      $oldControlMode = [Console]::TreatControlCAsInput
      [Console]::TreatControlCAsInput = $true
    }
    $readers = @{ Log = $process.StandardOutput; Error = $process.StandardError }
    $reads = @{ Log = $readers.Log.ReadLineAsync(); Error = $readers.Error.ReadLineAsync() }
    $deadline = [DateTime]::UtcNow.AddSeconds(75)
    $ready = $false
    $previousTick = ''
    while (-not $process.HasExited -or $reads.Log -or $reads.Error) {
      foreach ($stream in @('Log', 'Error')) {
        for ($n = 0; $n -lt 40 -and $reads[$stream] -and $reads[$stream].IsCompleted; $n++) {
          $line = $reads[$stream].GetAwaiter().GetResult()
          if ($null -eq $line) { $reads[$stream] = $null; break }
          $reads[$stream] = $readers[$stream].ReadLineAsync()
          if ($stream -eq 'Log' -and $line -match '^TRADINGBOT_VITE_READY ([0-9]{1,5})$') {
            $ready = $true
            Write-LauncherEvent 'Ready' $Matches[1] Green
            Write-Step 'TradingBot responded over HTTP.' Green
            if ($AfterUpdate -and $script:updateProgress.Complete -lt 100) { Write-UpdateProgress 'Update complete' 100 }
          } elseif ($line.Trim()) {
            $level = if ($stream -eq 'Error') { 'Red' } else { 'Gray' }
            Write-Step $line $level
          }
        }
      }
      if (-not $ready -and [DateTime]::UtcNow -ge $deadline) { throw 'The server did not become ready within 75 seconds.' }
      $key = Read-LauncherKey
      if ($key -eq 'R') { return 'Restart' }
      if ($key -eq 'U' -and $script:pendingUpdate) {
        Write-LauncherEvent 'Server' 'Stopping for update' Yellow
        return 'Update'
      }
      if ($key -eq 'U') {
        $script:screenView.Message = 'Checking GitHub production'
        Invoke-LauncherUpdate -Manual
        $script:screenView.Message = if ($script:runner.Internet -eq 'Online') { 'GitHub check complete' } else { 'GitHub check unavailable' }
      }
      if ($key -eq 'C') { Copy-LauncherLocalUrl }
      if ($key -eq 'H') { Test-LauncherHttp }
      if ($key -in @('Q', 'Ctrl+C')) { return 'Stopped' }
      if ($script:screenActive) {
        $tick = [DateTime]::UtcNow.ToString('HH:mm:ss')
        $size = "$([Console]::WindowWidth)x$([Console]::WindowHeight)"
        if ($key) { Set-LauncherViewKey $key }
        if ($key -or $size -ne $script:screenView.Size -or $tick -ne $previousTick) {
          $previousTick = $tick
          Show-LauncherFrame
        }
      }
      Start-Sleep -Milliseconds 65
    }
    if ($process.ExitCode -ne 0) { throw "Vite exited with code $($process.ExitCode)." }
    if (-not $ready) { throw 'The server stopped before reporting readiness.' }
    return 'Exited'
  } finally {
    $script:runner.ServerPid = $null
    $script:runner.ServerSince = $null
    try {
      if ($script:screenActive) { [Console]::TreatControlCAsInput = $oldControlMode }
      if ($ready -and -not $process.HasExited) {
        # Closing stdin lets Vite run its shutdown handlers before an owned
        # process-tree stop is needed.
        $process.StandardInput.Close()
        [void]$process.WaitForExit(3000)
      }
    } finally {
      try { Stop-LauncherProcess $process }
      finally { $process.Dispose() }
    }
  }
}

function ConvertTo-LauncherProcessArguments([string[]]$Arguments) {
  # ProcessStartInfo on .NET Framework takes a Windows command line.
  return ($Arguments | ForEach-Object {
    '"' + (($_ -replace '(\\*)"', '$1$1\"') -replace '(\\+)$', '$1$1') + '"'
  }) -join ' '
}

function New-LauncherProcessInfo([string]$Executable, [string]$Directory, [string[]]$Arguments) {
  $info = [Diagnostics.ProcessStartInfo]::new()
  $info.FileName = $Executable
  if ($info.PSObject.Properties['ArgumentList']) {
    foreach ($argument in $Arguments) { $info.ArgumentList.Add($argument) }
  } else {
    $info.Arguments = ConvertTo-LauncherProcessArguments $Arguments
  }
  $info.WorkingDirectory = $Directory
  $info.UseShellExecute = $false
  $info.CreateNoWindow = $true
  $info.RedirectStandardOutput = $true
  $info.RedirectStandardError = $true
  $info.StandardOutputEncoding = [Text.Encoding]::UTF8
  $info.StandardErrorEncoding = [Text.Encoding]::UTF8
  return $info
}

function Stop-LauncherProcess([Diagnostics.Process]$Process) {
  if ($Process.HasExited) { return }
  if ($PSVersionTable.PSEdition -eq 'Core') {
    try { $Process.Kill($true) }
    catch [InvalidOperationException] { if (-not $Process.HasExited) { throw } }
  } else {
    & { $ErrorActionPreference = 'Continue'; & "$env:SystemRoot\System32\taskkill.exe" /PID $Process.Id /T /F 2>&1 | Out-Null }
    if (-not $Process.HasExited) { $Process.Kill() }
  }
  [void]$Process.WaitForExit(5000)
}

function Read-LauncherFetchProgress([Diagnostics.Process]$Process, [int]$TimeoutSeconds) {
  $diagnostics = [Text.StringBuilder]::new()
  $read = $Process.StandardError.ReadLineAsync()
  $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
  while ($read) {
    if ($read.IsCompleted) {
      $line = $read.GetAwaiter().GetResult()
      if ($null -eq $line) { break }
      [void]$diagnostics.AppendLine($line)
      if ($line -match '^\s*(Receiving|Unpacking) objects:\s*(\d{1,3})%') {
        Write-UpdateProgress 'Downloading production' 0 ([Math]::Min(100, [int]$Matches[2]))
      }
      $read = $Process.StandardError.ReadLineAsync()
    } else { Start-Sleep -Milliseconds 35 }
    if ([DateTime]::UtcNow -ge $deadline) { throw 'The Git download timed out.' }
  }
  $remaining = [Math]::Max(0, ($deadline - [DateTime]::UtcNow).TotalMilliseconds)
  if (-not $Process.WaitForExit([int]$remaining)) { throw 'The Git download timed out.' }
  return $diagnostics.ToString()
}

function Invoke-LauncherGit([string]$Directory, [string[]]$Arguments, [int]$TimeoutSeconds = 12, [switch]$ReportProgress) {
  $git = Get-Command git -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $git) { throw 'Git is unavailable.' }
  $info = New-LauncherProcessInfo $git.Source $Directory (@('-c', 'credential.interactive=never') + $Arguments)
  $info.EnvironmentVariables['GIT_TERMINAL_PROMPT'] = '0'
  $info.EnvironmentVariables['GCM_INTERACTIVE'] = 'Never'
  $info.EnvironmentVariables['GIT_SSH_COMMAND'] = 'ssh -o BatchMode=yes -o ConnectTimeout=8'
  $info.EnvironmentVariables['GIT_OPTIONAL_LOCKS'] = '0'
  $process = [Diagnostics.Process]::Start($info)
  try {
    $output = $process.StandardOutput.ReadToEndAsync()
    if ($ReportProgress) {
      $errors = Read-LauncherFetchProgress $process $TimeoutSeconds
    } else {
      $pendingErrors = $process.StandardError.ReadToEndAsync()
      if (-not $process.WaitForExit($TimeoutSeconds * 1000)) { throw 'The Git operation timed out.' }
      $errors = $pendingErrors.Result
    }
    return [pscustomobject]@{ ExitCode = $process.ExitCode; Output = $output.Result; Error = $errors }
  } finally {
    try { Stop-LauncherProcess $process }
    finally { $process.Dispose() }
  }
}

function Get-ProductionCandidate([string]$Directory) {
  $remote = Invoke-LauncherGit $Directory @('ls-remote', '--exit-code', '--sort=-version:refname', 'origin', 'refs/heads/production', 'refs/tags/*')
  if ($remote.ExitCode -ne 0) { throw "GitHub production is unavailable (Git exit $($remote.ExitCode))." }
  $tip = [regex]::Match($remote.Output, '(?m)^([0-9a-f]{40,64})\trefs/heads/production\r?$')
  if (-not $tip.Success) { throw 'GitHub did not advertise a production branch.' }
  $commit = $tip.Groups[1].Value
  $tag = [regex]::Match($remote.Output, "(?m)^${commit}\trefs/tags/(v?[0-9][A-Za-z0-9.+-]*)(?:\^\{\})?\r?$")
  $version = if ($tag.Success) { $tag.Groups[1].Value } else { 'Revision ' + $commit.Substring(0, 8) }
  return [pscustomobject]@{ Commit = $commit; Version = $version }
}

function Get-LauncherCheckout([string]$Directory) {
  try {
    $top = Invoke-LauncherGit $Directory @('rev-parse', '--show-toplevel')
    if ($top.ExitCode -ne 0 -or [IO.Path]::GetFullPath($top.Output.Trim()) -ne $Directory) { return }

    $head = (Invoke-LauncherGit $Directory @('rev-parse', '--verify', 'HEAD')).Output.Trim()
    if ($head -notmatch '^[0-9a-f]{40,64}$') { return }
    $branch = (Invoke-LauncherGit $Directory @('symbolic-ref', '--quiet', '--short', 'HEAD')).Output.Trim()
    $remote = (Invoke-LauncherGit $Directory @('remote', 'get-url', 'origin')).Output.Trim()
    $isGitHub = $remote -match '^(?:https://(?:[^/@]+@)?github\.com/|ssh://git@github\.com(?::22)?/|git@github\.com:)[\w.-]+/[\w.-]+/?$'
    $version = 'Revision ' + $head.Substring(0, 8)
    $tag = (Invoke-LauncherGit $Directory @('describe', '--tags', '--exact-match', '--match', 'v[0-9]*', '--match', '[0-9]*', 'HEAD')).Output.Trim()
    $subject = (Invoke-LauncherGit $Directory @('log', '-1', '--first-parent', '--extended-regexp', '--grep=^Release v?[0-9]', '--format=%s', 'HEAD')).Output.Trim()
    if ($tag -match '^v?[0-9][A-Za-z0-9.+-]*$') { $version = $tag }
    elseif ($subject -match '^Release (v?[0-9][A-Za-z0-9.+-]*)(?:\s|:|$)') { $version = $Matches[1] }
    return [pscustomobject]@{ Head = $head; Branch = $branch; GitHub = $isGitHub; Version = $version }
  } catch { return }
}

function Assert-ProductionCheckout([string]$Directory, [string]$Installed) {
  $branch = Invoke-LauncherGit $Directory @('symbolic-ref', '--quiet', 'HEAD')
  $head = Invoke-LauncherGit $Directory @('rev-parse', '--verify', 'HEAD')
  if ($branch.Output.Trim() -cne 'refs/heads/production' -or $head.Output.Trim() -ne $Installed) {
    throw 'The production checkout changed. Reopen the launcher to check again.'
  }
  $status = Invoke-LauncherGit $Directory @('status', '--porcelain=v1', '--untracked-files=no')
  if ($status.ExitCode -ne 0 -or $status.Output) { throw 'Production has local changes. Review them before installing the update.' }
  $index = Invoke-LauncherGit $Directory @('ls-files', '-v', '-z')
  if ($index.ExitCode -ne 0 -or $index.Output -cmatch '(?:^|\x00)[a-zS] ') {
    throw 'Production has hidden index entries. Use a regular checkout to install the update.'
  }
  foreach ($operation in @('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'sequencer', 'BISECT_START')) {
    $path = (Invoke-LauncherGit $Directory @('rev-parse', '--path-format=absolute', '--git-path', $operation)).Output.Trim()
    if (-not $path -or (Test-Path -LiteralPath $path)) { throw 'A Git operation is in progress. Finish it before installing the update.' }
  }
}

function Get-ProductionUpdatePlan([string]$Directory, [string]$Installed, [string]$Candidate, [switch]$ReportProgress) {
  Assert-ProductionCheckout $Directory $Installed
  # Fetch only the commit the user reviewed. Leave remote-tracking refs and tags alone.
  $fetch = Invoke-LauncherGit $Directory @('fetch', '--progress', '--no-tags', '--no-write-fetch-head', '--no-auto-gc', 'origin', $Candidate) 90 -ReportProgress:$ReportProgress
  if ($fetch.ExitCode -ne 0) { throw "Could not download the selected production revision (Git exit $($fetch.ExitCode))." }
  if ($ReportProgress) { Write-UpdateProgress 'Checking the downloaded files' 33 100 }
  $ancestor = Invoke-LauncherGit $Directory @('merge-base', '--is-ancestor', $Installed, $Candidate)
  if ($ancestor.ExitCode -ne 0) { throw 'Production has diverged from the published branch. An automatic update is unavailable.' }

  $diff = Invoke-LauncherGit $Directory @('diff', '--raw', '-z', '--no-renames', $Installed, $Candidate, '--')
  if ($diff.ExitCode -ne 0) { throw 'Could not inspect the production file changes.' }
  $entries = $diff.Output.Split([char]0)
  for ($i = 0; $i -lt $entries.Count - 1; $i += 2) {
    $change = $entries[$i]
    $relative = $entries[$i + 1]
    $parts = $relative.Split('/')
    if ($change -notmatch '^:(?:000000|100644|100755) (?:000000|100644|100755) [0-9a-f]+ [0-9a-f]+ ([AMD])$') {
      throw 'Production contains an unsupported file type change.'
    }
    $isAddition = $Matches[1] -eq 'A'
    # The release publishes a runtime-only tree. Apply an independent, conservative
    # protection check before Git can touch anything under the workstation root.
    if (($relative -ne '.gitattributes' -and $relative -notmatch '^(apps/chart|engine|scripts)/') -or
      $relative -match '^(apps/chart/state|scripts/git|scripts/verification)/' -or
      $relative -match '(?:^|/)(?:\.git|\.env(?:\..*)?|node_modules|\.venv|venv|__pycache__|dist|build|\.vite|\.?cache|caches|tmp|temp|temporary|logs?|secrets?|sessions?)(?:/|$)|\.(?:log|pem|key|har|pid|bak|tmp)$' -or
      $parts -match '[\x00-\x1f<>:"\\|?*]|[ .]$|^$') {
      throw 'Production contains a protected path. The update was cancelled.'
    }

    $path = $Directory
    for ($part = 0; $part -lt $parts.Count; $part++) {
      $path = Join-Path $path $parts[$part]
      $item = Get-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
      if (-not $item) { break }
      $isLeaf = $part -eq $parts.Count - 1
      if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
        ($isLeaf -and ($isAddition -or $item.PSIsContainer)) -or (-not $isLeaf -and -not $item.PSIsContainer)) {
        throw "A local path blocks the update: $relative"
      }
    }
    $relative
  }
}

function Install-ProductionUpdate([string]$Directory, [string]$Installed, [string]$Candidate) {
  Assert-ProductionCheckout $Directory $Installed
  # Retain Git's index locking and untracked-file protection, including ignored paths.
  $merge = Invoke-LauncherGit $Directory @('-c', 'submodule.recurse=false', 'merge', '--ff-only', '--no-autostash', '--no-overwrite-ignore', $Candidate) 90
  $head = Invoke-LauncherGit $Directory @('rev-parse', '--verify', 'HEAD')
  if ($merge.ExitCode -ne 0 -or $head.Output.Trim() -ne $Candidate) {
    throw 'Git could not finish the source update. Review git status before starting TradingBot again.'
  }
}

function Invoke-LauncherUpdate([switch]$Manual) {
  $checkout = Get-LauncherCheckout $Root
  try { $chartVersion = (Get-Content -LiteralPath (Join-Path $ChartRoot 'package.json') -Raw -Encoding UTF8 | ConvertFrom-Json).version }
  catch { $chartVersion = 'Unknown' }
  $script:runner.ChartVersion = $chartVersion
  $script:runner.Branch = if ($checkout.Branch) { $checkout.Branch } elseif ($checkout) { 'detached' } else { 'source bundle' }
  $installedVersion = if ($checkout) { $checkout.Version } else { "Chart $chartVersion" }
  Write-LauncherEvent 'Version' $installedVersion

  $connected = [Net.NetworkInformation.NetworkInterface]::GetIsNetworkAvailable()
  $internet = if ($connected) { 'Checking GitHub' } else { 'Offline' }
  Write-LauncherEvent 'Internet' $internet
  if ($SkipUpdateCheck -and -not $Manual) {
    if ($connected) { Write-LauncherEvent 'Internet' 'Unchecked' }
    Write-LauncherEvent 'Latest' 'Not checked'
    Write-LauncherEvent 'Update' 'Check skipped'
    return
  }
  if (-not $connected) {
    Write-LauncherEvent 'Latest' 'Unavailable'
    Write-LauncherEvent 'Update' 'Check deferred'
    return
  }
  if (-not $checkout -or -not $checkout.GitHub) {
    Write-LauncherEvent 'Internet' 'Unverified'
    Write-LauncherEvent 'Latest' 'Unavailable'
    Write-LauncherEvent 'Update' 'GitHub checkout required'
    return
  }

  try { $candidate = Get-ProductionCandidate $Root }
  catch {
    Write-LauncherEvent 'Internet' 'GitHub unreachable'
    Write-LauncherEvent 'Latest' 'Unavailable'
    Write-LauncherEvent 'Update' 'Check deferred'
    Write-Step $_.Exception.Message Yellow
    return
  }
  Write-LauncherEvent 'Internet' 'Online'
  Write-LauncherEvent 'Latest' $candidate.Version
  if ($checkout.Branch -ne 'production') {
    if ($checkout.Version -notlike 'Revision *' -and $checkout.Version.TrimStart('v') -ne $candidate.Version.TrimStart('v')) {
      Write-LauncherEvent 'UpdateNotice' 'PRODUCTION VERSION DIFFERS' Yellow
    }
    Write-LauncherEvent 'Update' 'Development checkout'
    return
  }
  if ($checkout.Head -eq $candidate.Commit) { Write-LauncherEvent 'Update' 'Up to date'; return }

  if ((Invoke-LauncherGit $Root @('merge-base', '--is-ancestor', $candidate.Commit, $checkout.Head)).ExitCode -eq 0) {
    Write-LauncherEvent 'Update' 'Local production is ahead'
    return
  }
  $script:pendingUpdate = @{ Installed = $checkout.Head; Candidate = $candidate.Commit; Version = $candidate.Version }
  Write-LauncherEvent 'UpdateNotice' 'UPDATE AVAILABLE' Yellow
  Write-LauncherEvent 'Update' 'Press U to install'
}

function Install-LauncherPendingUpdate {
  $pending = $script:pendingUpdate
  $script:controls = 'Installing update'
  $script:addresses = @('The Chart server will restart after installation')
  Write-LauncherEvent 'UpdateNotice' ''
  Write-LauncherEvent 'Update' 'Installing'
  Write-UpdateProgress 'Downloading production' 0
  Write-Step "Downloading production $($pending.Version)..." Cyan
  try { $paths = @(Get-ProductionUpdatePlan $Root $pending.Installed $pending.Candidate -ReportProgress) }
  catch {
    Write-LauncherEvent 'Update' 'Installation deferred'
    Write-UpdateProgress 'Update deferred' 0
    Write-LauncherEvent 'UpdateNotice' 'UPDATE AVAILABLE' Yellow
    Write-Step $_.Exception.Message Yellow
    return $false
  }
  Write-UpdateProgress "Installing $($paths.Count) source changes" 33 100
  Write-Step "Applying $($paths.Count) tracked source changes..." Cyan
  try { Install-ProductionUpdate $Root $pending.Installed $pending.Candidate }
  catch { Write-LauncherEvent 'Update' 'Installation failed'; throw }
  Write-LauncherEvent 'Update' 'Restarting'
  Write-UpdateProgress 'Restarting TradingBot' 66 100
  Write-Step "Production $($pending.Version) installed. Restarting TradingBot..." Green
  return $true
}

function Invoke-LauncherStartup {
  try {
    if ($AfterUpdate) { Write-UpdateProgress 'Checking the updated server' 66 100 }
    Invoke-LauncherUpdate
    if ($script:pendingUpdate -and -not $script:screenActive -and -not [Console]::IsInputRedirected) {
      Write-Host 'Press U then Enter to install, or Enter to continue. ' -NoNewline -ForegroundColor Yellow
      if ([Console]::ReadLine() -match '^\s*u\s*$' -and (Install-LauncherPendingUpdate)) { return 75 }
    }
    Write-Step "Checking project at $Root" Cyan
    Ensure-ProjectFiles
    $tools = Ensure-Runtimes
    Write-LauncherEvent 'Local state' 'Checking'
    Resolve-LocalState $tools.Node
    Ensure-Directories
    Write-LauncherEvent 'Local state' 'Ready - directory verified' Green
    Ensure-NpmDependencies $tools.Npm
    do {
      $action = Start-DevServer $tools.Node $tools.Python
      if ($action -eq 'Update') {
        if (Install-LauncherPendingUpdate) { return 75 }
        $action = 'Restart'
      }
      if ($action -eq 'Restart') { Write-Step 'Restarting the Chart server...' Cyan }
    } while ($action -eq 'Restart')
    return 0
  } catch {
    Write-Step $_.Exception.Message Red
    foreach ($check in $script:checks) {
      if ($script:runner[$check] -eq 'Checking') { Write-LauncherEvent $check 'Failed' Red }
    }
    Write-LauncherEvent 'Server' 'Failed' Red
    return 1
  }
}

$sha = [Security.Cryptography.SHA256]::Create()
$lockPath = if ($script:OnWindows) { $Root.ToUpperInvariant() } else { $Root }
try { $checkoutId = [BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($lockPath))).Replace('-', '') }
finally { $sha.Dispose() }
$mutex = [Threading.Mutex]::new($false, "TradingBotLauncher_$checkoutId")
$ownsMutex = $false
$exitCode = 1
try {
  try { $ownsMutex = $mutex.WaitOne(0) } catch [Threading.AbandonedMutexException] { $ownsMutex = $true }
  if (-not $ownsMutex) { throw 'TradingBot is already running from this checkout.' }
  $script:screenActive = -not $Console -and $Host.UI.SupportsVirtualTerminal -and
    -not [Console]::IsOutputRedirected -and -not [Console]::IsInputRedirected -and
    -not (Test-Path Env:NO_COLOR) -and $env:TERM -notin @('dumb', 'xterm-mono')
  if ($script:screenActive) {
    [Console]::Write("$script:escape[?1049h$script:escape[?25l$script:escape[2J")
    Show-LauncherFrame
  }
  $exitCode = Invoke-LauncherStartup
  if ($exitCode -eq 1 -and $script:screenActive) {
    $script:controls = 'Any key  Exit'
    Show-LauncherFrame
    [void][Console]::ReadKey($true)
  }
} catch {
  Write-Step $_.Exception.Message Red
} finally {
  if ($script:screenActive) {
    [Console]::Write("$script:escape[0m$script:escape[?25h$script:escape[?1049l")
    $script:screenActive = $false
  }
  if ($ownsMutex) { $mutex.ReleaseMutex() }
  $mutex.Dispose()
}
if ($exitCode -eq 75) {
  # Re-read the installed launcher script before starting the updated server.
  $restart = @{}
  $restart['AfterUpdate'] = $true
  if ($Console) { $restart['Console'] = $true }
  if ($Loopback) { $restart['Loopback'] = $true }
  & $PSCommandPath @restart
  exit $LASTEXITCODE
}
exit $exitCode
