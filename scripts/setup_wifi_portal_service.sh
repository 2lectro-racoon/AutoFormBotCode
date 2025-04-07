#!/bin/bash

SERVICE_PATH="/etc/systemd/system/wifi_portal.service"

echo "🛠️ Creating systemd service for Flask Wi-Fi portal..."

sudo tee $SERVICE_PATH > /dev/null <<EOF
[Unit]
Description=Wi-Fi Setup Flask Web Server
After=network.target

[Service]
ExecStart=/home/pi/wifi_portal/venv/bin/python /home/pi/wifi_portal/app.py
WorkingDirectory=/home/pi/wifi_portal
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading systemd and enabling service..."
sudo systemctl daemon-reexec
sudo systemctl enable wifi_portal.service
sudo systemctl start wifi_portal.service

echo "✅ Service created and started successfully!"
echo "💡 You can check the status with: sudo systemctl status wifi_portal.service"