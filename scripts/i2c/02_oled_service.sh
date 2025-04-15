#!/bin/bash

echo "🖥️ Setting up OLED display service..."

USER_NAME=$(whoami)
SERVICE_FILE="/etc/systemd/system/oled_display.service"
PYTHON_PATH="/home/$USER_NAME/.oledenv/bin/python3"
SCRIPT_PATH="/home/$USER_NAME/AutoFormBotCode/scripts/i2c/oled_display.py"

# Create the systemd service file
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=OLED Display Info Service
After=network-online.target
DefaultDependencies=no
Before=shutdown.target

[Service]
Type=simple
ExecStart=$PYTHON_PATH $SCRIPT_PATH
ExecStopPost=$PYTHON_PATH /home/$USER_NAME/AutoFormBotCode/scripts/i2c/oled_clear.py
Restart=always
User=$USER_NAME
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable/start the service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable oled_display.service
sudo systemctl start oled_display.service

echo "✅ OLED display service registered and started!"
