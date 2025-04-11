#!/bin/bash

CHECK_INTERVAL=30  # check interval (s)
WIFI_INTERFACE="wlan0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_SWITCH_SCRIPT="$SCRIPT_DIR/04_auto_wifi_or_ap.sh"

while true; do
    CONNECTION_STATE=$(nmcli -t -f GENERAL.STATE device show "$WIFI_INTERFACE" | grep -o '[0-9]\+')
    
    if [[ "$CONNECTION_STATE" -ne 100 ]]; then
        echo "❌ Wi-Fi not connected. Re-running auto switch..."
        nmcli radio wifi on
        sleep 2
        "$AUTO_SWITCH_SCRIPT"
    else
        if ! systemctl is-active --quiet dnsmasq; then
            echo "⚠️ dnsmasq is not running. Restarting..."
            sudo systemctl start dnsmasq
        fi

        HOSTAPD_ACTIVE=$(systemctl is-active hostapd)
        if [[ "$HOSTAPD_ACTIVE" != "active" && "$CONNECTION_STATE" -ne 100 ]]; then
            echo "🔁 Neither connected nor AP running. Reinitializing..."
            "$AUTO_SWITCH_SCRIPT"
        fi
    fi

    sleep $CHECK_INTERVAL
done