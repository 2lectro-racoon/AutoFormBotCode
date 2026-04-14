#!/bin/bash
# AP Mode Setup Script
# This script sets up Access Point mode using hostapd and dnsmasq

set -e


# Notes:
# - This script may be executed by systemd (as root) where SUDO_UID is not set.
# - Always force wlan0 out of STA/NM control before enabling AP.

sudo apt install -y python3-pip python3-flask dnsmasq hostapd

INTERFACE="wlan0"
AP_IP_CIDR="192.168.4.1/24"
UNMANAGED_CONF="/etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf"
CHANNEL="6"   # 2.4GHz

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

wait_iface_type() {
  local want="$1"; local tries=${2:-20}; local i type
  for i in $(seq 1 "$tries"); do
    type=$(iw dev "$INTERFACE" info 2>/dev/null | awk '/\btype\b/{print $2; exit}')
    if [[ "$type" == "$want" ]]; then return 0; fi
    sleep 0.2
  done
  return 1
}

SSID="$1"
echo "[DEBUG] Received SSID in setup_ap_mode: '$1'"
echo "[DEBUG] Parsed SSID: '$SSID'"

if [[ -z "$SSID" ]]; then
  echo "❌ SSID is empty. Aborting to avoid overwriting hostapd.conf with blank SSID."
  exit 1
fi


log "🔧 Setting up Access Point mode..."

# Ensure required config directories exist
sudo mkdir -p /etc/hostapd

# Ensure required packages are installed
if ! command -v hostapd >/dev/null 2>&1; then
  echo "❌ hostapd is not installed. Please install hostapd first."
  exit 1
fi

if ! command -v dnsmasq >/dev/null 2>&1; then
  echo "❌ dnsmasq is not installed. Please install dnsmasq first."
  exit 1
fi

echo "[DEBUG] Writing ssid: '$SSID' into hostapd.conf"

HOSTAPD_CONF_CONTENT=$(cat <<EOF
interface=wlan0
driver=nl80211
ssid=${SSID}
hw_mode=g
channel=${CHANNEL}
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

# Stop services that may conflict with AP
log "🛑 Stopping conflicting services (if any)..."
sudo systemctl stop wpa_supplicant 2>/dev/null || true
sudo systemctl stop hostapd 2>/dev/null || true
sudo systemctl stop dnsmasq 2>/dev/null || true

# Disconnect wlan0 from any STA connection and prevent NM from fighting AP
sudo nmcli dev disconnect "$INTERFACE" 2>/dev/null || true
sudo nmcli device set "$INTERFACE" managed no 2>/dev/null || true

# Drop any STA IPs and routes before assigning AP IP
sudo ip addr flush dev "$INTERFACE" 2>/dev/null || true

echo "⚙️ Updating NetworkManager unmanaged settings..."
sudo mkdir -p /etc/NetworkManager/conf.d
echo -e "[keyfile]\nunmanaged-devices=interface-name:wlan0" | sudo tee "$UNMANAGED_CONF" > /dev/null
log "🔁 Restarting NetworkManager (apply unmanaged config)..."
sudo systemctl restart NetworkManager
sleep 1

echo "🌐 Setting static IP for wlan0..."
# Ensure NM doesn't fight us (in addition to unmanaged config file)
sudo nmcli device set "$INTERFACE" managed no || true

sudo rfkill unblock wifi
sudo ip link set "$INTERFACE" down
sudo iw dev "$INTERFACE" set type __ap
# Wait until the kernel reports AP type
if ! wait_iface_type "AP" 15; then
  # Some drivers report __ap instead of AP
  wait_iface_type "__ap" 5 || true
fi
sudo iw dev "$INTERFACE" set channel "$CHANNEL"
sudo ip addr flush dev "$INTERFACE"
sudo ip link set "$INTERFACE" up
sudo ip addr add "$AP_IP_CIDR" dev "$INTERFACE"

for svc in hostapd dnsmasq; do
    echo "🔍 Ensuring $svc is unmasked and enabled..."
    sudo systemctl unmask "$svc"
    sudo systemctl enable "$svc"
    sudo systemctl start "$svc"
done

echo "🔁 Re-asserting wlan0 IP (in case it was cleared)..."
sudo ip link set "$INTERFACE" up || true
if ! ip -4 addr show dev "$INTERFACE" | grep -q "192\\.168\\.4\\.1/24"; then
  sudo ip addr flush dev "$INTERFACE"
  sudo ip addr add "$AP_IP_CIDR" dev "$INTERFACE"
fi

log "✅ AP setup summary:"
log "- iface type: $(iw dev "$INTERFACE" info 2>/dev/null | awk '/\btype\b/{print $2; exit}')"
log "- ip: $(ip -4 addr show dev "$INTERFACE" | awk '/inet /{print $2; exit}')"
log "- hostapd: $(systemctl is-active hostapd 2>/dev/null || true)"

echo "✅ AP mode setup complete."
