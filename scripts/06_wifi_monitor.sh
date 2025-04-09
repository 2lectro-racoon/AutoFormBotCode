#!/bin/bash

CHECK_INTERVAL=30  # check interval (s)
WIFI_INTERFACE="wlan0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_SWITCH_SCRIPT="$SCRIPT_DIR/04_auto_wifi_or_ap.sh"

while true; do
    if ! iw dev $WIFI_INTERFACE link | grep -q "Connected"; then
        echo "❌ Wi-Fi disconnected. Re-running auto switch..."
        "$AUTO_SWITCH_SCRIPT"
    fi
    sleep $CHECK_INTERVAL
done