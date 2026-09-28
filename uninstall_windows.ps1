# Requires Administrator Privileges
$ErrorActionPreference = "Stop"

$AppName = "XWeather"
$InstallDir = "$env:ProgramFiles\$AppName"
$StartMenuShortcut = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\$AppName.lnk"

$IsAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $IsAdmin) {
    Write-Error "Error: Please run this script as Administrator."
    exit 1
}

Write-Host "Removing XWeather..." -ForegroundColor Yellow

if (Test-Path $InstallDir) {
    Remove-Item -Path $InstallDir -Recurse -Force
}

if (Test-Path $StartMenuShortcut) {
    Remove-Item -Path $StartMenuShortcut -Force
}

Write-Host "Uninstallation complete." -ForegroundColor Green
