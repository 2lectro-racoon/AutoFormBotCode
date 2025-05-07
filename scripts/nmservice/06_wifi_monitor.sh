#!/bin/bash
echo "📡 Monitoring Wi-Fi status..."
INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}')

while true; do
  STATE=$(nmcli -t -f GENERAL.STATE device show $INTERFACE | cut -d: -f2 | cut -d' ' -f1)

  MODE=$(iw dev $INTERFACE info | grep type | awk '{print $2}')
  IP=$(ip -4 addr show $INTERFACE | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n1)

  if [[ "$STATE" -lt 70 && -z "$IP" && "$MODE" != "AP" ]]; then
    echo "⚠️ Wi-Fi disconnected (no IP). Switching mode..."
    /home/$USER/AutoFormBotCode/scripts/nmservice/04_auto_wifi_or_ap.sh
  fi

  sleep 10
done