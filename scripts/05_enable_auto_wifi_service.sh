#!/bin/bash

SERVICE_NAME="auto_wifi_or_ap.service"
SCRIPT_PATH="$(realpath "$(dirname "$0")")/auto_wifi_or_ap.sh"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

# Create systemd service file
echo "📝 Creating systemd service for auto Wi-Fi/AP switch..."
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Auto Wi-Fi or AP Mode Switcher
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=$SCRIPT_PATH
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Reload and enable service
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "🚀 Enabling $SERVICE_NAME to start on boot..."
sudo systemctl enable $SERVICE_NAME

echo "✅ Service $SERVICE_NAME is now enabled to run on boot!"
echo "▶️ You can start it manually with: sudo systemctl start $SERVICE_NAME"