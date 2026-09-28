#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run with sudo."
  exit 1
fi

echo "Removing XWeather..."
rm -rf /opt/xweather
rm -f /usr/share/applications/xweather.desktop
echo "Uninstallation complete."
