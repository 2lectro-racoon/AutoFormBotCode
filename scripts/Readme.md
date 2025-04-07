# Raspberry Pi Wi-Fi / AP Mode Setup Guide

## ✨ Overview
This project allows your Raspberry Pi to automatically:
- ✅ Connect to a known Wi-Fi network (STA mode)
- ⚠️ If no known network is found, create an AP hotspot and show a Flask-based Wi-Fi setup portal

---

## 🚀 Initial Setup (One-time)

1. **Run these scripts in order:**

```bash
./setup_wifi_portal.sh           # Sets up Flask portal app
./setup_ap_mode.sh              # Configures hostapd, dnsmasq, wlan0 settings
./enable_auto_wifi_service.sh   # Registers auto-switch service with systemd
```

2. **Reboot to test:**
```bash
sudo reboot
```

---

## ⚡ Scripts Explained

| Script | Purpose |
|--------|---------|
| `setup_wifi_portal.sh` | Installs Flask, sets up portal app in `/home/pi/wifi_portal/` |
| `setup_ap_mode.sh` | Configures `hostapd`, `dnsmasq`, and sets wlan0 as unmanaged |
| `enable_auto_wifi_service.sh` | Registers systemd service for `auto_wifi_or_ap.sh` |
| `auto_wifi_or_ap.sh` | Logic to switch between Wi-Fi mode and AP mode |
| `setup_wifi_portal_service.sh` | Registers `wifi_portal.service` to run Flask automatically (called by the others) |

---

## 🔧 Manual Testing

### Force AP Mode:
```bash
sudo systemctl stop wpa_supplicant
sudo ip link set wlan0 down
sudo ip addr flush dev wlan0
sudo ip link set wlan0 up
sudo ip addr add 192.168.4.1/24 dev wlan0
sudo systemctl start dnsmasq
sudo systemctl start hostapd
sudo systemctl start wifi_portal.service
```

### Force Wi-Fi Mode:
```bash
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq
sudo ip addr flush dev wlan0
sudo systemctl restart wpa_supplicant
```

---

## 🔍 Useful Checks

```bash
ip addr show wlan0              # Check if 192.168.4.1 or DHCP IP assigned
nmcli dev                      # Should show wlan0 as unmanaged
sudo systemctl status wifi_portal.service
sudo systemctl status auto_wifi_or_ap.service
```

---

## 🚫 Troubleshooting

- **No internet on eth0?**
  - Run `sudo dhclient eth0` or check `ip route`

- **SSID 'mypi-setup' visible but can't connect?**
  - Double check password is `raspberry`
  - Confirm `hostapd` is running with `sudo systemctl status hostapd`

- **Web portal not opening?**
  - Try `http://192.168.4.1:8080` from your phone browser
  - Restart Flask manually: `sudo systemctl restart wifi_portal.service`

---

## 🚀 Next Steps

- Implement frontend style for Flask portal
- Add OTA update capability for settings
- Store Wi-Fi history with timestamps for diagnostics

---

Last updated: April 2025