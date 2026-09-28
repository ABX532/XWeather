# XWeather

A lightweight, cross-platform weather application and Conky desktop widget powered by Python and Open-Meteo. **XWeather** features automatic location detection, current weather conditions, Air Quality Index (AQI), and a 7-day extended forecast with dynamic display scaling support.

---

## Features

* **Cross-Platform Compatibility:** Native installers and desktop integration for Linux, Windows, and macOS.
* **Dual Display Options:** 
  * Standalone Python GUI Application (`xweather.py`).
  * Dynamic Conky Desktop Widget (`conky_2.py` / `weather_2.conf`).
* **Zero Config Location:** Automatic IP-based geolocation lookup with offline fallback caching.
* **Comprehensive Metrics:** Real-time temperature, humidity, wind speed & direction, precipitation probability, sunrise/sunset, AQI status, and 7-day daily forecasts.
* **Proportional Widget Scaling:** Configurable scaling engine (`conky_settings.json`) that resizes window canvas, graphics, text offsets, and enforces minimum font bounds to prevent rendering distortion.

---

## File Structure

```text
XWeather/  
└── conky >
    ├── conky.py                 # Conky Widget Generation Script
    ├── weather.conf             # Conky Configuration File
    ├── conky_settings.json      # Configuration file for scaling percentage
    ├── xweather_icon.png        # Application Icon
    ├── xweather_glass_panel.png # Background panel asset
    └── requirements.txt         # Python dependency list
├── xweather.py              # Main Script
├── install.sh               # Linux Installer Script (System-wide)
├── uninstall.sh             # Linux Uninstaller Script
├── install.ps1              # Windows Installer Script (PowerShell)
├── uninstall.ps1            # Windows Uninstaller Script
├── install_mac.sh           # macOS Installer Script
├── uninstall_mac.sh         # macOS Uninstaller Script
├── xweather_logo.png        # Logo asset
└── xweather_logo.svg        # Logo asset
```

## Installation
clone the repository
```bash
git clone https://github.com/ABX532/XWeather/
```

# 🐧 Linux
Run the installer script with sudo to set up /opt/xweather, create a dedicated Python virtual environment, and register an application menu launcher (.desktop).

```Bash
sudo chmod +x install.sh
sudo ./install.sh
```
# 🪟 Windows
Open PowerShell as Administrator, navigate to the project directory, and execute the installation script:

```PowerShell
powershell -ExecutionPolicy Bypass -File .\install.ps1
Note: The Windows installer configures pythonw.exe to run the application silently in the background without opening a command prompt window.
```

# 🍎 macOS
Open Terminal, navigate to the repository directory, and run the macOS setup script (no sudo required):

```Bash
chmod +x install_mac.sh
./install_mac.sh
```
This creates an executable XWeather.command shortcut on your Desktop.

## Prerequisites
If installing manually without the provided installer scripts, ensure you have Python 3.8+ installed along with python3-tk (on Linux) and the following packages:

```Bash
pip install -r requirements.txt
```
Dependencies:

* openmeteo-requests

*  requests-cache

* retry-requests

## Uninstallation
To completely remove XWeather and its associated desktop launchers from your system:

Linux: 
```Bash
sudo ./uninstall.sh
```

Windows: 
```PowerShell
powershell -ExecutionPolicy Bypass -File .\uninstall.ps1
```

macOS:
```Bash
./uninstall_mac.sh
```
