#!/bin/bash

WIFI_INTERFACE="wlan0"
FLASK_SERVICE="wifi_portal.service"

# Check for nearby known SSID from wpa_supplicant.conf
KNOWN_SSID=$(iw dev $WIFI_INTERFACE scan | grep SSID | awk '{print $2}' | grep -F -f <(sudo grep -oP '(?<=ssid=").+?(?=")' /etc/wpa_supplicant/wpa_supplicant.conf))

if [ -n "$KNOWN_SSID" ]; then
  echo "📡 Known Wi-Fi network '$KNOWN_SSID' found. Attempting to connect..."
  sudo systemctl stop hostapd
  sudo systemctl stop dnsmasq
  sudo ip addr flush dev $WIFI_INTERFACE
  sudo systemctl restart NetworkManager
  sudo systemctl restart wpa_supplicant
else
  echo "🚫 No known Wi-Fi found. Enabling AP mode..."
  sudo systemctl stop NetworkManager
  sudo systemctl stop wpa_supplicant
  sudo ip link set $WIFI_INTERFACE down
  sudo ip addr flush dev $WIFI_INTERFACE
  sudo ip link set $WIFI_INTERFACE up
  sudo ip addr add 192.168.4.1/24 dev $WIFI_INTERFACE
  sudo systemctl start dnsmasq
  sudo systemctl start hostapd
  sudo systemctl start $FLASK_SERVICE
fi