#!/bin/bash

echo "📦 Setting up AP mode configuration for Raspberry Pi OS (Bookworm)..."

# 1. Create hostapd configuration
echo "📝 Creating /etc/hostapd/hostapd.conf..."
sudo tee /etc/hostapd/hostapd.conf > /dev/null <<EOF
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
wpa_passphrase=raspberry
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# 2. Backup and create dnsmasq configuration
echo "📝 Backing up and creating /etc/dnsmasq.conf..."
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig 2>/dev/null
sudo tee /etc/dnsmasq.conf > /dev/null <<EOF
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
address=/setup.portal/192.168.4.1
EOF

# 3. Register hostapd default config path
echo "🛠️ Registering hostapd default config path..."
sudo sed -i 's|^#DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

# 🔓 Unmask hostapd if it is masked
echo "🔓 Unmasking hostapd if masked..."
# New block added
echo "🔧 Marking wlan0 as unmanaged in NetworkManager..."
sudo mkdir -p /etc/NetworkManager/conf.d
sudo tee /etc/NetworkManager/conf.d/unmanaged-wlan0.conf > /dev/null <<EOF
[keyfile]
unmanaged-devices=interface-name:wlan0
EOF
sudo systemctl restart NetworkManager
# End of new block

# 🌐 Assigning static IP to wlan0...
sudo ip addr add 192.168.4.1/24 dev wlan0

# 5. Disable hostapd and dnsmasq from autostart (they will be triggered manually)
echo "🚫 Disabling hostapd and dnsmasq on boot..."
sudo systemctl disable hostapd
sudo systemctl disable dnsmasq

echo "✅ AP mode configuration complete for Bookworm!"
echo "📡 To test AP mode manually:"
echo "   sudo ip link set wlan0 up"
echo "   sudo ip addr add 192.168.4.1/24 dev wlan0"
echo "   sudo systemctl start dnsmasq"
echo "   sudo systemctl start hostapd"
echo "📲 Then connect to 'AutoFormBotpi-setup' and open http://192.168.4.1:8080"