#!/bin/bash

# Ensure wpa_supplicant is running before continuing
sudo systemctl unmask wpa_supplicant
sudo systemctl restart wpa_supplicant

# Ensure wlan0 is managed by NetworkManager before attempting Wi-Fi connection
if [ -f /etc/NetworkManager/conf.d/unmanaged-wlan0.conf ]; then
  echo "🔄 Removing unmanaged configuration for $WIFI_INTERFACE"
  sudo rm /etc/NetworkManager/conf.d/unmanaged-wlan0.conf
  sudo systemctl reload NetworkManager
  sleep 2
fi

# Give wpa_supplicant a moment to initialize
sleep 3

WIFI_INTERFACE="wlan0"
FLASK_SERVICE="wifi_portal.service"

# Wait for wlan0 to be up
RETRY=0
while ! ip link show $WIFI_INTERFACE | grep -q "state UP"; do
  echo "⏳ Waiting for $WIFI_INTERFACE to be up..."
  sleep 1
  RETRY=$((RETRY+1))
  if [ "$RETRY" -ge 10 ]; then
    echo "❌ $WIFI_INTERFACE did not come up. Aborting."
    exit 1
  fi
done

# Check for nearby known SSID from wpa_supplicant.conf
WPA_CONF="/etc/wpa_supplicant/wpa_supplicant.conf"
if [ -f "$WPA_CONF" ]; then
  KNOWN_SSID=$(iw dev $WIFI_INTERFACE scan | grep SSID | awk '{print $2}' | grep -F -f <(grep -oP '(?<=ssid=").+?(?=")' "$WPA_CONF"))
else
  KNOWN_SSID=""
fi

if [ -n "$KNOWN_SSID" ]; then
  echo "📡 Known Wi-Fi network '$KNOWN_SSID' found. Attempting to connect..."
  sudo systemctl stop hostapd
  sudo systemctl stop dnsmasq
  sudo ip link set $WIFI_INTERFACE down
  sudo ip link set $WIFI_INTERFACE up
  sudo systemctl restart wpa_supplicant

  sleep 5  # allow time for association
  echo "🔄 Attempting DHCP..."
  sudo dhclient -v $WIFI_INTERFACE

  WLAN_IP=$(ip addr show $WIFI_INTERFACE | grep "inet " | awk '{print $2}' | cut -d'/' -f1)

  if [ -n "$WLAN_IP" ]; then
    echo "✅ Connected to $KNOWN_SSID with IP $WLAN_IP"
    exit 0
  else
    echo "⚠️  DHCP failed. Falling back to AP mode..."
    sudo systemctl stop wpa_supplicant
    sudo wpa_cli -i $WIFI_INTERFACE terminate
    sleep 1
    sudo wpa_supplicant -B -i $WIFI_INTERFACE -c "$WPA_CONF"
    sleep 5
    sudo ip link set $WIFI_INTERFACE down
    sudo ip link set $WIFI_INTERFACE up
    if ! ip addr show $WIFI_INTERFACE | grep -q "192.168.4.1"; then
      sudo ip addr add 192.168.4.1/24 dev $WIFI_INTERFACE
    else
      echo "ℹ️  IP 192.168.4.1 is already assigned to $WIFI_INTERFACE"
    fi
    cat <<EOF | sudo tee /etc/dnsmasq.conf > /dev/null
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF
    echo -e "[keyfile]\nunmanaged-devices=interface-name:$WIFI_INTERFACE" | sudo tee /etc/NetworkManager/conf.d/unmanaged-wlan0.conf > /dev/null
    sudo systemctl reload NetworkManager
    sleep 2
    sudo systemctl start dnsmasq
    sudo systemctl unmask hostapd
    sudo systemctl start hostapd
    sudo systemctl start $FLASK_SERVICE
  fi
else
  echo "🚫 No known Wi-Fi found. Enabling AP mode..."
  sudo systemctl stop wpa_supplicant
  sudo ip link set $WIFI_INTERFACE down
  sudo ip link set $WIFI_INTERFACE up
  if ! ip addr show $WIFI_INTERFACE | grep -q "192.168.4.1"; then
    sudo ip addr add 192.168.4.1/24 dev $WIFI_INTERFACE
  else
    echo "ℹ️  IP 192.168.4.1 is already assigned to $WIFI_INTERFACE"
  fi
  cat <<EOF | sudo tee /etc/dnsmasq.conf > /dev/null
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF
  # Ensure wlan0 is unmanaged in AP mode
  echo -e "[keyfile]\nunmanaged-devices=interface-name:$WIFI_INTERFACE" | sudo tee /etc/NetworkManager/conf.d/unmanaged-wlan0.conf > /dev/null
  sudo systemctl reload NetworkManager
  sleep 2
  sudo systemctl start dnsmasq
  sudo systemctl unmask hostapd
  sudo systemctl start hostapd
  sudo systemctl start $FLASK_SERVICE
fi