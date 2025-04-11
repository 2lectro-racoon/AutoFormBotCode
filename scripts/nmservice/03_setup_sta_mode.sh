

#!/bin/bash
# 03_setup_sta_mode.sh - Setup script for STA (client) mode

set -e

echo "📶 Setting up Station (Client) Mode..."

# Stop AP services if running
echo "🛑 Stopping AP services..."
sudo systemctl stop hostapd || true
sudo systemctl stop dnsmasq || true

# Remove static IP from wlan0
echo "🔄 Releasing static IP from wlan0..."
sudo ip addr flush dev wlan0

# Set wlan0 to managed mode
echo "🔧 Setting wlan0 to managed mode..."
sudo ip link set wlan0 down
sudo iw dev wlan0 set type managed
sudo ip link set wlan0 up

# Remove unmanaged setting if present
if [ -f /etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf ]; then
  echo "🧹 Removing unmanaged config for wlan0..."
  sudo rm -f /etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf
  sudo systemctl restart NetworkManager
fi

echo "✅ STA mode setup complete. You can now connect to Wi-Fi using nmcli or a web form."