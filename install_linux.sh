#!/bin/bash
set -e

APP_NAME="xweather"
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

# 1. Install system prerequisites
echo "[1/4] Installing system dependencies (python3-tk, python3-venv)..."
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-tk python3-pip

# 2. Setup destination directory and copy source files
echo "[2/4] Setting up /opt/$APP_NAME..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

cp xweather.py "$INSTALL_DIR/"
if [ -f "xweather_icon.png" ]; then
    cp xweather_icon.png "$INSTALL_DIR/"
fi

# 3. Create isolated venv in /opt and install packages
echo "[3/4] Creating local virtual environment & installing Python packages..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip -q
"$INSTALL_DIR/venv/bin/pip" install -r requirements.txt -q

# 4. Create desktop menu entry
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

echo "=========================================="
echo " Success! XWeather is installed."
echo " Launch it anytime from your app menu."
echo "=========================================="
