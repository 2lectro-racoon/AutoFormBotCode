#!/bin/bash
# AP Mode Setup Script
# This script sets up Access Point mode using hostapd and dnsmasq

set -e


SSID="$1"
echo "[DEBUG] Received SSID in setup_ap_mode: '$1'"
echo "[DEBUG] Parsed SSID: '$SSID'"

if [[ -z "$SSID" ]]; then
  echo "❌ SSID is empty. Aborting to avoid overwriting hostapd.conf with blank SSID."
  exit 1
fi

USER_HOME=$(getent passwd "$SUDO_UID" | cut -d: -f6)
AUTOFORM_PATH="$USER_HOME/AutoFormBotCode"

echo "🔧 Setting up Access Point mode..."

echo "[DEBUG] Writing ssid: '$SSID' into hostapd.conf"

HOSTAPD_CONF_CONTENT=$(cat <<EOF
interface=wlan0
driver=nl80211
ssid=${SSID}
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=0
EOF
)
echo "$HOSTAPD_CONF_CONTENT" | sudo tee /tmp/hostapd_tmp.conf > /dev/null
if ! sudo cmp -s /tmp/hostapd_tmp.conf /etc/hostapd/hostapd.conf 2>/dev/null; then
    echo "📁 Updating hostapd config..."
    sudo cp /tmp/hostapd_tmp.conf /etc/hostapd/hostapd.conf
else
    echo "📁 hostapd config already up-to-date."
fi

echo "CONFIG_FILE=/etc/hostapd/hostapd.conf" | sudo tee /etc/default/hostapd &> /dev/null

DNSMASQ_CONF_CONTENT=$(cat <<EOF
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF
)
echo "$DNSMASQ_CONF_CONTENT" | sudo tee /tmp/dnsmasq_tmp.conf > /dev/null
if ! sudo cmp -s /tmp/dnsmasq_tmp.conf /etc/dnsmasq.conf 2>/dev/null; then
    echo "📁 Updating dnsmasq config..."
    sudo cp /tmp/dnsmasq_tmp.conf /etc/dnsmasq.conf
else
    echo "📁 dnsmasq config already up-to-date."
fi

echo "⚙️ Updating NetworkManager unmanaged settings..."
sudo mkdir -p /etc/NetworkManager/conf.d
UNMANAGED_CONF=/etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf
echo -e "[keyfile]\nunmanaged-devices=interface-name:wlan0" | sudo tee "$UNMANAGED_CONF" > /dev/null
sudo systemctl restart NetworkManager

echo "🌐 Setting static IP for wlan0..."
# Ensure NM doesn't fight us (in addition to unmanaged config file)
sudo nmcli device set wlan0 managed no || true

sudo rfkill unblock wifi
sudo ip link set wlan0 down
sudo iw dev wlan0 set type __ap
sleep 2
sudo iw dev wlan0 set channel 6
sudo ip addr flush dev wlan0
sudo ip link set wlan0 up
sudo ip addr add 192.168.4.1/24 dev wlan0

for svc in hostapd dnsmasq; do
    echo "🔍 Ensuring $svc is unmasked and enabled..."
    sudo systemctl unmask "$svc"
    sudo systemctl enable "$svc"
    sudo systemctl restart "$svc"
done

echo "🔁 Re-asserting wlan0 IP (in case it was cleared)..."
# If the address is missing, add it again
if ! ip -4 addr show dev wlan0 | grep -q "192\\.168\\.4\\.1/24"; then
  sudo ip addr flush dev wlan0
  sudo ip addr add 192.168.4.1/24 dev wlan0
fi

echo "✅ AP mode setup complete."
