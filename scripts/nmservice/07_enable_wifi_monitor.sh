#!/bin/bash
sudo cp /home/$USER/AutoFormBotCode/scripts/nmservice/06_wifi_monitor.sh /usr/local/bin/autoformbot_wifi_monitor.sh
sudo chmod +x /usr/local/bin/autoformbot_wifi_monitor.sh

cat <<EOF | sudo tee /etc/systemd/system/autoformbot_wifi_monitor.service
[Unit]
Description=AutoFormBot Wi-Fi Monitor
After=network.target

[Service]
ExecStart=/usr/local/bin/autoformbot_wifi_monitor.sh
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable autoformbot_wifi_monitor.service
sudo systemctl start autoformbot_wifi_monitor.service