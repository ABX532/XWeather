#!/bin/bash
set -e

APP_NAME="XWeather"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
DESKTOP_LAUNCHER="$HOME/Desktop/$APP_NAME.command"

echo "Removing XWeather..."
rm -rf "$INSTALL_DIR"
rm -f "$DESKTOP_LAUNCHER"
echo "Uninstallation complete."
