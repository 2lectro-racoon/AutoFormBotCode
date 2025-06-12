#!/bin/bash

echo "🔄 Auto Wi-Fi/AP mode switching script starting..."

AP_SSID="$1"
echo "[DEBUG] 04_auto_wifi_or_ap.sh received: '$1'"
echo "[DEBUG] Assigned SSID: '$SSID'"

# Get AutoFormBot root path dynamically
AUTOFORM_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Wi-Fi interface
INTERFACE="wlan0"
# AP_SSID="$SSID"
AP_IP="192.168.4.1"
CHANNEL="6"

# Wait until wlan0 interface appears
echo "⏳ Waiting for $INTERFACE to become available..."
for i in {1..10}; do
    if ip link show "$INTERFACE" &>/dev/null; then
        echo "✅ $INTERFACE is available."
        break
    fi
    sleep 1
done

if ! ip link show "$INTERFACE" &>/dev/null; then
    echo "❌ $INTERFACE not found. Exiting."
    exit 1
fi


# Known SSIDs to check for (you can make this dynamic or load from a file)
KNOWN_SSIDS=$(nmcli -t -f NAME connection show)

enable_ap_mode() {
  echo "📶 Switching to AP mode..."
  bash "$AUTOFORM_PATH/scripts/nmservice/02_setup_ap_mode.sh" "$AP_SSID"
}

enable_sta_mode() {
  echo "📡 Switching to STA mode..."
  bash "$AUTOFORM_PATH/scripts/nmservice/03_setup_sta_mode.sh"
}

# Call enable_ap_mode or enable_sta_mode based on your decision logic
# enable_ap_mode
# enable_sta_mode

# Function to enable STA mode
# enable_sta_mode() {
#   echo "📡 Switching to STA mode..."

#   # Stop AP services
#   sudo systemctl stop hostapd
#   sudo systemctl stop dnsmasq

#   # Restore managed mode
#   sudo ip link set $INTERFACE down
#   sudo iw dev $INTERFACE set type managed
#   sudo ip link set $INTERFACE up

#   # Remove unmanaged config
#   sudo rm -f /etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf
#   sudo systemctl restart NetworkManager
# }

# # Function to enable AP mode
# enable_ap_mode() {
#   echo "📶 Switching to AP mode..."

#   # Set unmanaged for NetworkManager
#   sudo mkdir -p /etc/NetworkManager/conf.d
#   echo -e "[keyfile]\nunmanaged-devices=interface-name:$INTERFACE" | sudo tee /etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf

#   # Restart NetworkManager to apply
#   sudo systemctl restart NetworkManager

#   # Set interface mode to AP
#   sudo ip link set $INTERFACE down
#   sudo iw dev $INTERFACE set type __ap
#   sudo ip addr flush dev $INTERFACE
#   sudo ip addr add ${AP_IP}/24 dev $INTERFACE
#   sudo ip link set $INTERFACE up

#   # Start AP services
#   sudo systemctl start dnsmasq
#   sudo systemctl start hostapd
# }

# Ensure wlan0 is in managed mode before checking status
CURRENT_MODE=$(iw dev $INTERFACE info | grep type | awk '{print $2}')
if [[ "$CURRENT_MODE" != "managed" ]]; then
  sudo rm -f /etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf
  sudo systemctl restart NetworkManager
  echo "🔁 Converting $INTERFACE to managed mode for scanning..."
  sudo ip link set $INTERFACE down
  sleep 1
  sudo iw dev $INTERFACE set type managed
  sleep 1
  sudo ip link set $INTERFACE up
  sudo nmcli dev set $INTERFACE managed yes
fi

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
sudo nmcli radio wifi on
sleep 2
sudo nmcli dev wifi rescan
sleep 3

SSID_FOUND=""
for SSID in $KNOWN_SSIDS; do
  if sudo nmcli -t -f SSID dev wifi | grep -q "^$SSID$"; then
    SSID_FOUND=$SSID
    break
  fi
done

if [[ -n "$SSID_FOUND" ]]; then
  SSID_ACTIVE=$(nmcli -t -f active,ssid dev wifi | grep "^yes" | cut -d: -f2)
  if [[ "$SSID_ACTIVE" == "$SSID_FOUND" ]]; then
    echo "✅ Already connected to '$SSID_FOUND'. Skipping reconnection."
    exit 0
  fi

  echo "✅ Known SSID '$SSID_FOUND' found. Connecting to it..."
  enable_sta_mode
  echo "🔗 Bringing up connection on $INTERFACE for SSID '$SSID_FOUND'..."
  sleep 2
  sudo nmcli con up "$SSID_FOUND" ifname $INTERFACE
  # Wait up to 20 seconds for connection to stabilize
  for i in {1..10}; do
    CONNECTED=$(nmcli -t -f GENERAL.STATE device show $INTERFACE | grep -oP '\d+')
    if [[ "$CONNECTED" -ge 70 ]]; then
      echo "✅ Connection established to '$SSID_FOUND'."
      break
    fi
    echo "⏳ Waiting for connection to '$SSID_FOUND'... ($i)"
    sleep 2
  done

  if [[ "$CONNECTED" -lt 70 ]]; then
    echo "❌ Connection to '$SSID_FOUND' failed. Falling back to AP mode..."
    enable_ap_mode
  fi
else
  echo "🚫 No known SSID found. Starting AP mode..."
  enable_ap_mode
fi
