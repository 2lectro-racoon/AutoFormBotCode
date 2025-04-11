#!/bin/bash
# Set regulatory domain to US for consistent AP behavior
sudo iw reg set US

# Unblock Wi-Fi in case it was disabled by previous state
sudo rfkill unblock wifi
# Unmask hostapd to ensure it can be started
# Ensure NetworkManager manages wlan0 and disables MAC address randomization
sudo mkdir -p /etc/NetworkManager/conf.d
cat <<EOF | sudo tee /etc/NetworkManager/conf.d/99-wifi-managed.conf > /dev/null
[device]
wifi.scan-rand-mac-address=no

[ifupdown]
managed=true
EOF

sudo systemctl reload NetworkManager
sleep 2

# Ensure wlan0 is managed by NetworkManager before attempting Wi-Fi connection
if [ -f /etc/NetworkManager/conf.d/unmanaged-wlan0.conf ]; then
  echo "🔄 Removing unmanaged configuration for $WIFI_INTERFACE"
  sudo rm /etc/NetworkManager/conf.d/unmanaged-wlan0.conf
  sudo systemctl reload NetworkManager
  sleep 2
fi

# Give NetworkManager a moment to initialize
sleep 3

WIFI_INTERFACE="wlan0"
FLASK_SERVICE="wifi_portal.service"

# Wait for wlan0 to be recognized
RETRY=0
while ! iw dev "$WIFI_INTERFACE" info &> /dev/null; do
  echo "⏳ Waiting for $WIFI_INTERFACE to be recognized..."
  sleep 1
  RETRY=$((RETRY+1))
  if [ "$RETRY" -ge 20 ]; then
    echo "❌ $WIFI_INTERFACE not recognized after 20 seconds. Aborting."
    exit 1
  fi
done
echo "✅ $WIFI_INTERFACE recognized by system."

RETRY=0
while ! ip link show "$WIFI_INTERFACE" | grep -q "state UP"; do
  echo "⏳ Waiting for $WIFI_INTERFACE to be UP..."
  sudo ip link set "$WIFI_INTERFACE" up
  sleep 1
  RETRY=$((RETRY+1))
  if [ "$RETRY" -ge 20 ]; then
    echo "❌ $WIFI_INTERFACE failed to come UP. Aborting."
    exit 1
  fi
done
echo "✅ $WIFI_INTERFACE is UP."

# Check for nearby known SSID from NetworkManager
KNOWN_SSIDS=$(nmcli connection show | grep wifi | awk '{print $1}')
CURRENT_SCAN_SSIDS=$(nmcli dev wifi list | awk 'NR>1 {print $2}')
KNOWN_SSID=$(echo "$CURRENT_SCAN_SSIDS" | grep -Fx -f <(echo "$KNOWN_SSIDS") | head -n 1)

if [ -n "$KNOWN_SSID" ]; then
  echo "📡 Known Wi-Fi network '$KNOWN_SSID' found. Attempting to connect..."

  CURRENT_SCAN_SSID=$(nmcli dev wifi list | awk 'NR>1 {print $2}')
  if ! echo "$CURRENT_SCAN_SSID" | grep -Fxq "$KNOWN_SSID"; then
    echo "⚠️  SSID '$KNOWN_SSID' not currently available. Switching to AP mode..."
    KNOWN_SSID=""
  fi
fi

if [ -n "$KNOWN_SSID" ]; then
  sudo systemctl stop hostapd
  sudo systemctl stop dnsmasq
  sudo systemctl restart NetworkManager
  sudo ip link set $WIFI_INTERFACE down
  sudo ip link set $WIFI_INTERFACE up
  sleep 2
  nmcli dev wifi connect "$KNOWN_SSID"
  sleep 10

  WLAN_IP=$(ip addr show $WIFI_INTERFACE | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
  
  # IP가 없으면 dhclient로 수동 요청
  if [ -z "$WLAN_IP" ]; then
    echo "🔁 No IP obtained. Trying dhclient with retries..."
    for i in {1..5}; do
      sudo dhclient -v $WIFI_INTERFACE
      sleep 3
      WLAN_IP=$(ip addr show $WIFI_INTERFACE | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
      if [ -n "$WLAN_IP" ]; then
        break
      fi
      echo "⏳ Retry $i: Waiting for IP..."
    done
  fi

  if [ -n "$WLAN_IP" ]; then
    echo "✅ Connected to $KNOWN_SSID with IP $WLAN_IP"
    exit 0
  else
    echo "⚠️  Wi-Fi connection failed or no IP obtained. Switching to AP mode..."
    
    # Make wlan0 unmanaged by NetworkManager (for AP mode)
    cat <<EOF | sudo tee /etc/NetworkManager/conf.d/unmanaged-wlan0.conf > /dev/null
[keyfile]
unmanaged-devices=interface-name:wlan0
EOF

    sudo systemctl reload NetworkManager
    sleep 2
    
    sudo systemctl stop wpa_supplicant
    sleep 1
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
    sudo systemctl reload NetworkManager
    sleep 2
    sudo systemctl start dnsmasq
    sudo systemctl unmask hostapd
    sudo systemctl start hostapd
    sudo systemctl start $FLASK_SERVICE
  fi
else
  echo "🚫 No known Wi-Fi found. Enabling AP mode..."
  
  # Make wlan0 unmanaged by NetworkManager (for AP mode)
  cat <<EOF | sudo tee /etc/NetworkManager/conf.d/unmanaged-wlan0.conf > /dev/null
[keyfile]
unmanaged-devices=interface-name:wlan0
EOF

  sudo systemctl reload NetworkManager
  sleep 2
  
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
  sudo systemctl reload NetworkManager
  sleep 2
  sudo systemctl start dnsmasq
  sudo systemctl unmask hostapd
  sudo systemctl start hostapd
  sudo systemctl start $FLASK_SERVICE
fi