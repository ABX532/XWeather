#!/bin/bash
set -e

APP_NAME="XWeather"
INSTALL_DIR="/opt/$APP_NAME"
DESKTOP_FILE="/usr/share/applications/$APP_NAME.desktop"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "    XWeather Source Installer (Linux)     "
echo "=========================================="

if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run this script with sudo."
  echo "Usage: sudo ./install.sh"
  exit 1
fi

cd "$SCRIPT_DIR"

# 1. Detect package manager and install dependencies
install_dependencies() {
    echo "[1/4] Detecting package manager and installing system dependencies..."

	if [ -f /etc/NIXOS ]; then
    	echo "NixOS detected."
    	echo "Imperative installation via /opt is not supported on NixOS."
    	echo "Please Run xweather.py Directly"
    	exit 1
	fi
    if command -v apt-get &>/dev/null; then
        apt-get update -qq
        apt-get install -y -qq python3 python3-venv python3-tk python3-pip
    elif command -v dnf &>/dev/null; then
        dnf install -y -q python3 python3-pip python3-tkinter
    elif command -v yum &>/dev/null; then
        yum install -y -q python3 python3-pip python3-tkinter
    elif command -v pacman &>/dev/null; then
        pacman -Sy --noconfirm --needed python python-pip tk
    elif command -v zypper &>/dev/null; then
        zypper --non-interactive install -y python3 python3-pip python3-tk
    elif command -v apk &>/dev/null; then
        apk add --no-cache python3 py3-pip python3-tkinter
    else
        echo "Warning: Package manager not recognized."
        echo "Please ensure Python 3, pip, venv, and Tkinter are installed manually."
    fi
}

install_dependencies

echo "[2/4] Setting up $INSTALL_DIR..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

cp xweather.py "$INSTALL_DIR/"
if [ -f "xweather_icon.png" ]; then
    cp xweather_icon.png "$INSTALL_DIR/"
fi

echo "[3/4] Creating local virtual environment & installing Python packages..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip -q

if [ -f "requirements.txt" ]; then
    "$INSTALL_DIR/venv/bin/pip" install -r requirements.txt -q
fi

echo "[4/4] Creating system application entry..."
cat << EOF > "$DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Type=Application
Name=XWeather
Comment=Weather Application
Exec=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/xweather.py
Icon=$INSTALL_DIR/xweather_icon.png
Terminal=false
Categories=Utility;
EOF

chmod +x "$DESKTOP_FILE"
chmod +x "$INSTALL_DIR/xweather.py"

if command -v update-desktop-database &>/dev/null; then
    update-desktop-database /usr/share/applications/ &>/dev/null || true
fi

echo "=========================================="
echo " Success! XWeather is installed."
echo " Launch it anytime from your app menu."
echo "=========================================="
