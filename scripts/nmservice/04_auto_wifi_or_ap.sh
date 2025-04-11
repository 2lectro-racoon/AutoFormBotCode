#!/bin/bash

echo "🔄 Auto Wi-Fi/AP mode switching script starting..."

# Get current user dynamically
CURRENT_USER=$(logname)
HOME_DIR=$(eval echo "~$CURRENT_USER")

# Wi-Fi interface
INTERFACE="wlan0"
AP_SSID="AutoFormBotpi-setup"
AP_IP="192.168.4.1"
CHANNEL="6"

# Known SSIDs to check for (you can make this dynamic or load from a file)
KNOWN_SSIDS=$(nmcli -t -f NAME connection show)

# Function to enable STA mode
enable_sta_mode() {
  echo "📡 Switching to STA mode..."

  # Stop AP services
  sudo systemctl stop hostapd
  sudo systemctl stop dnsmasq

  # Restore managed mode
  sudo ip link set $INTERFACE down
  sudo iw dev $INTERFACE set type managed
  sudo ip link set $INTERFACE up

  # Remove unmanaged config
  sudo rm -f /etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf
  sudo systemctl restart NetworkManager
}

# Function to enable AP mode
enable_ap_mode() {
  echo "📶 Switching to AP mode..."

  # Set unmanaged for NetworkManager
  sudo mkdir -p /etc/NetworkManager/conf.d
  echo -e "[keyfile]\nunmanaged-devices=interface-name:$INTERFACE" | sudo tee /etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf

  # Restart NetworkManager to apply
  sudo systemctl restart NetworkManager

  # Set interface mode to AP
  sudo ip link set $INTERFACE down
  sudo iw dev $INTERFACE set type __ap
  sudo ip addr flush dev $INTERFACE
  sudo ip addr add ${AP_IP}/24 dev $INTERFACE
  sudo ip link set $INTERFACE up

  # Start AP services
  sudo systemctl start dnsmasq
  sudo systemctl start hostapd
}

# Check if wlan0 is up
echo "⏳ Waiting for wlan0 to be UP..."
for i in {1..5}; do
  sudo ip link set $INTERFACE up
  sleep 1
  STATE=$(cat /sys/class/net/$INTERFACE/operstate)
  if [[ "$STATE" == "up" ]]; then
    echo "✅ $INTERFACE is UP."
    break
  fi
done

# Scan for known SSIDs
echo "🔍 Scanning for Wi-Fi networks..."
nmcli radio wifi on
sleep 2
nmcli dev wifi rescan
sleep 3

SSID_FOUND=""
for SSID in $KNOWN_SSIDS; do
  if nmcli -t -f SSID dev wifi | grep -q "^$SSID$"; then
    SSID_FOUND=$SSID
    break
  fi
done

if [[ -n "$SSID_FOUND" ]]; then
  echo "✅ Known SSID '$SSID_FOUND' found. Connecting to it..."
  enable_sta_mode
  nmcli con up "$SSID_FOUND"
else
  echo "🚫 No known SSID found. Starting AP mode..."
  enable_ap_mode
fi
