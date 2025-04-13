#!/bin/bash

echo "AutoFormBot Auto Wi-Fi/AP mode switching script install..."

AUTOFORM_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bash "$AUTOFORM_PATH/AutoFormBotCode/scripts/nmservice/01_setup_web_server.sh"
bash "$AUTOFORM_PATH/scripts/nmservice/05_enable_auto_wifi_service.sh"
bash "$AUTOFORM_PATH/scripts/nmservice/07_enable_wifi_monitor.sh"

echo "AutoFormBot Auto Wi-Fi/AP mode switching script installed..."