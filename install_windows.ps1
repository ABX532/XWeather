# Requires Administrator Privileges
$ErrorActionPreference = "Stop"

$AppName = "XWeather"
$InstallDir = "$env:ProgramFiles\$AppName"
$ScriptDir =$PSScriptRoot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "    XWeather Source Installer (Windows)   " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Check Administrator Privileges
$IsAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $IsAdmin) {
    Write-Error "Error: Please run this script as Administrator."
    exit 1
}

# 2. Check for Python installation
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Error: Python is not installed or not added to system PATH. Please install Python from https://www.python.org/ and check 'Add Python to PATH'."
    exit 1
}

# 3. Setup Install Directory
Write-Host "[1/4] Setting up $InstallDir..." -ForegroundColor Yellow
if (Test-Path $InstallDir) {
    Remove-Item -Path $InstallDir -Recurse -Force
}
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

Copy-Item -Path "$ScriptDir\xweather.py" -Destination "$InstallDir\"
if (Test-Path "$ScriptDir\xweather_icon.png") {
    Copy-Item -Path "$ScriptDir\xweather_icon.png" -Destination "$InstallDir\"
}
if (Test-Path "$ScriptDir\requirements.txt") {
    Copy-Item -Path "$ScriptDir\requirements.txt" -Destination "$InstallDir\"
}

# 4. Create Virtual Environment & Install Dependencies
Write-Host "[2/4] Creating local virtual environment..." -ForegroundColor Yellow
python -m venv "$InstallDir\venv"

Write-Host "[3/4] Installing Python packages from requirements.txt..." -ForegroundColor Yellow
& "$InstallDir\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
if (Test-Path "$InstallDir\requirements.txt") {
    & "$InstallDir\venv\Scripts\python.exe" -m pip install -r "$InstallDir\requirements.txt" --quiet
}

# 5. Create Start Menu Shortcut
Write-Host "[4/4] Creating Start Menu shortcut..." -ForegroundColor Yellow
$WshShell = New-Object -ComObject WScript.Shell
$StartMenuDir = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs"
$ShortcutPath = "$StartMenuDir\$AppName.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
# pythonw.exe launches the app without opening a background Command Prompt console
$Shortcut.TargetPath = "$InstallDir\venv\Scripts\pythonw.exe"
$Shortcut.Arguments = "`"$InstallDir\xweather.py`""
$Shortcut.WorkingDirectory = $InstallDir$Shortcut.Description = "XWeather Application"
if (Test-Path "$InstallDir\xweather_icon.png") {
    $Shortcut.IconLocation = "$InstallDir\xweather_icon.png"
}
$Shortcut.Save()

Write-Host "==========================================" -ForegroundColor Green
Write-Host " Success! XWeather is installed." -ForegroundColor Green
Write-Host " Launch it anytime from your Windows Start Menu." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
