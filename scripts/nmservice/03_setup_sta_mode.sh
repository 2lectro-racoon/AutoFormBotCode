#!/bin/bash
# 03_setup_sta_mode.sh - Setup script for STA (client) mode

set -e

echo "📶 Setting up Station (Client) Mode..."

# Stop AP services if running
echo "🛑 Stopping AP services..."
sudo systemctl is-active --quiet hostapd && sudo systemctl stop hostapd || echo "ℹ️ hostapd already stopped."
sudo systemctl is-active --quiet dnsmasq && sudo systemctl stop dnsmasq || echo "ℹ️ dnsmasq already stopped."

# Remove static IP from wlan0
echo "🔄 Releasing static IP from wlan0..."
sudo ip addr flush dev wlan0 || echo "ℹ️ No static IP to flush on wlan0."

# Set wlan0 to managed mode
echo "🔧 Setting wlan0 to managed mode..."
current_mode=$(iw dev wlan0 info | awk '/type/ {print $2}')
if [ "$current_mode" != "managed" ]; then
  sudo ip link set wlan0 down
  sudo iw dev wlan0 set type managed
  sudo ip link set wlan0 up
else
  echo "ℹ️ wlan0 is already in managed mode."
fi

# Remove unmanaged setting if present
unmanaged_conf="/etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf"
if [ -f "$unmanaged_conf" ]; then
  echo "🧹 Removing unmanaged config for wlan0..."
  sudo rm -f "$unmanaged_conf"
  sudo systemctl restart NetworkManager
else
  echo "ℹ️ No unmanaged config found for wlan0."
fi

echo "✅ STA mode setup complete. You can now connect to Wi-Fi using nmcli or a web form."