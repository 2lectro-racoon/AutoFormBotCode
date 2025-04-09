#!/bin/bash

CHECK_INTERVAL=30  # check interval (s)
WIFI_INTERFACE="wlan0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_SWITCH_SCRIPT="$SCRIPT_DIR/04_auto_wifi_or_ap.sh"

while true; do
    STATE=$(cat /sys/class/net/$WIFI_INTERFACE/operstate)
    LINK_INFO=$(iw dev $WIFI_INTERFACE link)

    if [[ "$STATE" != "up" ]] || ! echo "$LINK_INFO" | grep -q "Connected"; then
        echo "❌ Wi-Fi disconnected or interface down. Re-running auto switch..."
        sudo ip link set $WIFI_INTERFACE up
        sleep 2
        "$AUTO_SWITCH_SCRIPT"
    fi

    sleep $CHECK_INTERVAL
done