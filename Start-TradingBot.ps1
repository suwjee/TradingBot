[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$Host.UI.RawUI.WindowTitle = 'TradingBot | Local Workstation'

$Root = $PSScriptRoot
$ChartRoot = Join-Path $Root 'lightweight-charts'
$Esc = [char]27
$State = [hashtable]::Synchronized(@{
    Logs = [System.Collections.Generic.List[object]]::new()
    Endpoints = [System.Collections.Generic.List[object]]::new()
    Dirty = $true
    ServerState = 'Preparing'
})

function Add-Log {
    param([ValidateSet('INFO', 'OK', 'WARN', 'ERROR', 'APP')] [string]$Level, [string]$Message)
    $State.Logs.Add([pscustomobject]@{ Time = Get-Date; Level = $Level; Message = $Message.Trim() })
    while ($State.Logs.Count -gt 250) { $State.Logs.RemoveAt(0) }
    $State.Dirty = $true
}

function Write-ColorLine {
    param([string]$Prefix, [string]$Text, [ConsoleColor]$Color)
    Write-Host $Prefix -NoNewline -ForegroundColor $Color
    Write-Host $Text -ForegroundColor Gray
}

function Render-Dashboard {
    try {
        $consoleWidth = [Console]::WindowWidth
        $consoleHeight = [Console]::WindowHeight
    } catch {
        $consoleWidth = 120
        $consoleHeight = 40
    }
    $width = [Math]::Min(110, [Math]::Max(72, $consoleWidth - 4))
    $line = ('─' * $width)
    Write-Host "$Esc[2J$Esc[H" -NoNewline
    Write-Host ('  TRADINGBOT  •  LOCAL WORKSTATION') -ForegroundColor Cyan
    Write-Host $line -ForegroundColor DarkGray
    Write-ColorLine '  STATUS     ' $State.ServerState $(if ($State.ServerState -eq 'Online') { 'Green' } elseif ($State.ServerState -eq 'Preparing') { 'Yellow' } else { 'Red' })
    Write-Host '  CONNECTIONS' -ForegroundColor White
    if ($State.Endpoints.Count -eq 0) {
        Write-Host '    Waiting for Vite to publish its address…' -ForegroundColor DarkGray
    } else {
        foreach ($endpoint in $State.Endpoints) {
            $label = if ($endpoint.Kind -eq 'Local') { 'Local:   ' } else { 'Network: ' }
            $suffix = if ($endpoint.Adapter) { "     $($endpoint.Adapter)" } else { '' }
            Write-Host ("    ➜  {0}{1}{2}" -f $label, $endpoint.Url, $suffix) -ForegroundColor Green
        }
    }
    Write-Host '  PROJECT     ' -NoNewline -ForegroundColor DarkGray
    Write-Host $Root -ForegroundColor Gray
    Write-Host $line -ForegroundColor DarkGray
    Write-Host '  LIVE LOGS' -ForegroundColor White
    $available = [Math]::Max(6, $consoleHeight - 9)
    $items = @($State.Logs | Select-Object -Last $available)
    foreach ($item in $items) {
        $color = switch ($item.Level) { 'OK' { 'Green' } 'WARN' { 'Yellow' } 'ERROR' { 'Red' } 'APP' { 'Cyan' } default { 'DarkGray' } }
        $stamp = $item.Time.ToString('HH:mm:ss')
        Write-Host "  $stamp " -NoNewline -ForegroundColor DarkGray
        Write-Host ("[{0}] " -f $item.Level.PadRight(5)) -NoNewline -ForegroundColor $color
        Write-Host $item.Message -ForegroundColor Gray
    }
    $State.Dirty = $false
}

function Refresh-CommandPath {
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$machine;$user"
}

function Get-Executable {
    param([string[]]$Names)
    foreach ($name in $Names) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }
    return $null
}

function Install-WingetPackage {
    param([string]$Id, [string]$Label)
    $winget = Get-Executable @('winget')
    if (-not $winget) { throw "Windows Package Manager is required to install $Label automatically. Install App Installer, then run launcher.bat again." }
    Add-Log INFO "Installing $Label…"
    Render-Dashboard
    & $winget install --id $Id --exact --silent --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw "Installation failed for $Label (winget exit code $LASTEXITCODE)." }
    Refresh-CommandPath
    Add-Log OK "$Label installed."
}

function Ensure-Directories {
    $directories = @(
        (Join-Path $Root 'market-data\raw'),
        (Join-Path $Root 'primary-cache\drawings'),
        (Join-Path $Root 'primary-cache\indicator-calculations')
    )
    foreach ($directory in $directories) {
        if (-not (Test-Path -LiteralPath $directory)) { New-Item -ItemType Directory -Force -Path $directory | Out-Null; Add-Log OK "Created required folder: $directory" }
        else { Add-Log OK "Required folder ready: $directory" }
    }
}

function Ensure-Dependencies {
    $node = Get-Executable @('node')
    if (-not $node) { Install-WingetPackage 'OpenJS.NodeJS.LTS' 'Node.js LTS'; $node = Get-Executable @('node') }
    if (-not $node) { throw 'Node.js is still unavailable after installation. Open a new terminal and run launcher.bat again.' }
    $nodeVersion = [version]((& $node --version).Trim().TrimStart('v'))
    if ($nodeVersion -lt [version]'20.19.0') { Install-WingetPackage 'OpenJS.NodeJS.LTS' 'Node.js LTS'; $node = Get-Executable @('node') }
    Add-Log OK "Node.js $((& $node --version).Trim())"

    $npm = Get-Executable @('npm.cmd', 'npm')
    if (-not $npm) { throw 'npm is missing even though Node.js is installed.' }
    Add-Log OK "npm $((& $npm --version).Trim())"

    $python = Get-Executable @('python', 'py')
    if (-not $python) { Install-WingetPackage 'Python.Python.3.12' 'Python 3.12'; $python = Get-Executable @('python', 'py') }
    if (-not $python) { throw 'Python is still unavailable after installation. Open a new terminal and run launcher.bat again.' }
    & $python -c "from zoneinfo import ZoneInfo; ZoneInfo('Asia/Tehran')"
    if ($LASTEXITCODE -ne 0) {
        & $python -m pip install --disable-pip-version-check --quiet tzdata
        if ($LASTEXITCODE -ne 0) { throw 'Unable to install the Python timezone dependency (tzdata).' }
    }
    Add-Log OK "Python $((& $python --version 2>&1).ToString().Trim())"
    return [pscustomobject]@{ Node = $node; Npm = $npm; Python = $python }
}

function Ensure-NpmPackages {
    param([string]$Npm)
    $requiredPackages = @(
        (Join-Path $ChartRoot 'node_modules\vite'),
        (Join-Path $ChartRoot 'node_modules\playwright-core')
    )
    $missingPackages = @($requiredPackages | Where-Object { -not (Test-Path -LiteralPath $_) })
    if ($missingPackages.Count -gt 0) {
        Add-Log WARN 'Node packages are incomplete; restoring the locked dependencies.'
    } elseif (Test-Path -LiteralPath (Join-Path $ChartRoot 'node_modules')) {
        Add-Log OK 'Node packages are ready.'
        return
    }
    Add-Log INFO 'Installing Node packages…'
    Render-Dashboard
    Push-Location $ChartRoot
    try {
        if (Test-Path -LiteralPath (Join-Path $ChartRoot 'package-lock.json')) { & $Npm ci } else { & $Npm install }
        if ($LASTEXITCODE -ne 0) { throw "npm dependency installation failed (exit code $LASTEXITCODE)." }
    } finally { Pop-Location }
    Add-Log OK 'Node packages installed.'
}

function Add-Endpoint {
    param([ValidateSet('Local', 'Network')][string]$Kind, [string]$Address, [string]$Adapter)
    if (-not $Address) { return }
    $url = $Address.TrimEnd('/') + '/'
    if (-not ($State.Endpoints | Where-Object { $_.Url -eq $url })) {
        $State.Endpoints.Add([pscustomobject]@{ Kind = $Kind; Url = $url; Adapter = $Adapter })
        $State.Dirty = $true
    }
}

function Stop-ProcessTree {
    param([System.Diagnostics.Process]$Process)
    if (-not $Process) { return }
    if (-not $Process.HasExited) {
        & taskkill.exe /PID $Process.Id /T /F 2>$null | Out-Null
    }
}

function Start-Server {
    param([string]$Npm, [string]$Python)
    $env:TRADINGBOT_PYTHON = $Python
    $portsBeforeStart = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalPort -ge 5173 -and $_.LocalPort -le 5273 } |
        Select-Object -ExpandProperty LocalPort -Unique)
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $Npm
    $psi.Arguments = 'run dev -- --host 0.0.0.0'
    $psi.WorkingDirectory = $ChartRoot
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.Environment['TRADINGBOT_PYTHON'] = $Python
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi
    if (-not $process.Start()) { throw 'Unable to start the Vite server.' }
    Add-Log APP 'npm run dev started; waiting for Vite to bind its actual port…'
    $boundPort = $null
    for ($attempt = 0; $attempt -lt 40 -and -not $process.HasExited; $attempt++) {
        $newPort = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
            Where-Object { $_.LocalPort -ge 5173 -and $_.LocalPort -le 5273 -and $portsBeforeStart -notcontains $_.LocalPort } |
            Select-Object -ExpandProperty LocalPort -Unique |
            Sort-Object | Select-Object -First 1
        if ($newPort) { $boundPort = [int]$newPort; break }
        Start-Sleep -Milliseconds 250
    }
    if (-not $boundPort) {
        if ($process.HasExited) { throw "Vite stopped unexpectedly (exit code $($process.ExitCode))." }
        throw 'Vite did not publish a listening port between 5173 and 5273.'
    }
    Add-Endpoint -Kind Local -Address ("http://localhost:{0}" -f $boundPort)
    Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.IPAddress -notmatch '^(127\.|169\.254\.)' -and $_.AddressState -eq 'Preferred' } |
        ForEach-Object { Add-Endpoint -Kind Network -Address ("http://{0}:{1}" -f $_.IPAddress, $boundPort) -Adapter $_.InterfaceAlias }
    $State.ServerState = 'Online'; Add-Log OK ("Vite is listening on port {0}; addresses below use the live bound port." -f $boundPort)
    Render-Dashboard
    try {
        while (-not $process.HasExited) { if ($State.Dirty) { Render-Dashboard }; Start-Sleep -Milliseconds 150 }
        throw "Vite server stopped unexpectedly (exit code $($process.ExitCode))."
    } finally {
        Stop-ProcessTree -Process $process
        if ($boundPort) {
            Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
                Where-Object { $_.LocalPort -eq $boundPort } |
                Select-Object -ExpandProperty OwningProcess -Unique |
                ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
        }
    }
}

try {
    Add-Log INFO 'Checking the local TradingBot environment…'
    $tools = Ensure-Dependencies
    Ensure-Directories
    Ensure-NpmPackages -Npm $tools.Npm
    Start-Server -Npm $tools.Npm -Python $tools.Python
} catch {
    $State.ServerState = 'Error'; Add-Log ERROR $_.Exception.Message; Render-Dashboard
    Write-Host "`n  Startup stopped. Press any key to close." -ForegroundColor Red
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}
