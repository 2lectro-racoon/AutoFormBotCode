#!/bin/bash
echo "📡 Monitoring Wi-Fi status..."
INTERFACE="wlan0"

while true; do
  STATE=$(nmcli -t -f GENERAL.STATE device show $INTERFACE | cut -d: -f2 | cut -d' ' -f1)

  MODE=$(iw dev $INTERFACE info | grep type | awk '{print $2}')
  if [[ "$STATE" -lt 70 && "$MODE" != "AP" ]]; then
    echo "⚠️ Wi-Fi disconnected. Switching mode..."
    /home/$USER/AutoFormBotCode/scripts/nmservice/04_auto_wifi_or_ap.sh
  fi

  sleep 10
done