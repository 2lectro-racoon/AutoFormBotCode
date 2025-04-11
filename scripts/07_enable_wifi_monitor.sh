#!/bin/bash

SERVICE_NAME="wifi_monitor.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/06_wifi_monitor.sh"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

echo "📝 Creating systemd service for Wi-Fi monitoring..."

# generate
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Wi-Fi Connection Monitor and Recovery
After=NetworkManager.service

[Service]
ExecStart=$SCRIPT_PATH
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# sudo and register
echo "🔒 Making script executable..."
chmod +x $SCRIPT_PATH

echo "🔄 Reloading systemd and enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "✅ $SERVICE_NAME is now active and monitoring Wi-Fi!"