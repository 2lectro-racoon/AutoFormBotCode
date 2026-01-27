
#!/bin/bash
set -e

echo "🧩 Setting up I2C Manager service..."

USER_NAME=$(whoami)
SERVICE_FILE="/etc/systemd/system/i2c_manager.service"
PYTHON_PATH="/home/$USER_NAME/.afbvenv/bin/python3"
SCRIPT_PATH="/home/$USER_NAME/AutoFormBotCode/scripts/i2c/i2c_manager.py"
OLED_CLEAR_PATH="/home/$USER_NAME/AutoFormBotCode/scripts/i2c/oled_clear.py"
UDS_PATH="/run/autoformbot/afb_i2c.sock"

# Create the systemd service file
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=AutoFormBot I2C Manager (OLED + sensors + UDS)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=/home/$USER_NAME
Environment=PYTHONUNBUFFERED=1

# Create /run/autoformbot at runtime (owned by root but writable as needed)
RuntimeDirectory=autoformbot
RuntimeDirectoryMode=0755

# Remove stale socket before start
ExecStartPre=/bin/rm -f $UDS_PATH

ExecStart=$PYTHON_PATH $SCRIPT_PATH

# Explicitly clear OLED on stop/shutdown
ExecStopPost=$PYTHON_PATH $OLED_CLEAR_PATH

Restart=always
RestartSec=1
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable/start the service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable i2c_manager.service
sudo systemctl restart i2c_manager.service

echo "✅ i2c_manager service registered and started!"

echo "\nUseful commands:"
echo "  sudo systemctl status i2c_manager.service"
echo "  sudo journalctl -u i2c_manager.service -f"
