#!/bin/bash
set -e

APP_NAME="XWeather"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
DESKTOP_LAUNCHER="$HOME/Desktop/$APP_NAME.command"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "     XWeather Source Installer (macOS)    "
echo "=========================================="

# 1. Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required. Please install it via Homebrew ('brew install python python-tk') or from python.org."
    exit 1
fi

# 2. Setup destination directory
echo "[1/3] Setting up installation directory at $INSTALL_DIR..."
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

cd "$SCRIPT_DIR"
cp xweather.py "$INSTALL_DIR/"
if [ -f "xweather_icon.png" ]; then
    cp xweather_icon.png "$INSTALL_DIR/"
fi
if [ -f "requirements.txt" ]; then
    cp requirements.txt "$INSTALL_DIR/"
fi

# 3. Create virtual environment and install dependencies
echo "[2/3] Creating virtual environment & installing dependencies..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip -q
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt" -q
fi

# 4. Create Desktop Shortcut (.command)
echo "[3/3] Creating launcher shortcut on your Desktop..."
cat << EOF > "$DESKTOP_LAUNCHER"
#!/bin/bash
cd "$INSTALL_DIR"
exec "$INSTALL_DIR/venv/bin/python3" "$INSTALL_DIR/xweather.py"
EOF

chmod +x "$DESKTOP_LAUNCHER"
chmod +x "$INSTALL_DIR/xweather.py"

echo "=========================================="
echo " Success! XWeather is installed."
echo " Double-click '$APP_NAME.command' on your Desktop to launch."
echo "=========================================="
