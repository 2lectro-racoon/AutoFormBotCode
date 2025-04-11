#!/bin/bash
# AP Mode Setup Script
# This script sets up Access Point mode using hostapd and dnsmasq

set -e

USER_HOME=$(getent passwd "$SUDO_UID" | cut -d: -f6)
AUTOFORM_PATH="$USER_HOME/AutoFormBotCode"

echo "🔧 Setting up Access Point mode..."

echo "📁 Creating hostapd config..."
sudo tee /etc/hostapd/hostapd.conf &> /dev/null <<EOF
interface=wlan0
driver=nl80211
ssid=AutoFormBotpi-setup
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=form1234
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

echo "CONFIG_FILE=/etc/hostapd/hostapd.conf" | sudo tee /etc/default/hostapd &> /dev/null

echo "📁 Creating dnsmasq config..."
sudo tee /etc/dnsmasq.conf &> /dev/null <<EOF
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF

echo "🌐 Setting static IP for wlan0..."
sudo rfkill unblock wifi
sudo ip link set wlan0 down
sudo ip addr flush dev wlan0
sudo ip addr add 192.168.4.1/24 dev wlan0
sudo ip link set wlan0 up

echo "⚙️ Updating NetworkManager unmanaged settings..."
sudo mkdir -p /etc/NetworkManager/conf.d
echo -e "[keyfile]\nunmanaged-devices=interface-name:wlan0" | sudo tee /etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf
sudo systemctl restart NetworkManager

echo "🚀 Enabling AP services..."
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
sudo systemctl enable dnsmasq
sudo systemctl start dnsmasq

echo "✅ AP mode setup complete."
