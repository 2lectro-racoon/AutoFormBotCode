#!/bin/bash

echo "🌐 Setting up AutoFormBot Web Server..." | tee /dev/tty1
echo "🌍 Setting Wi-Fi regulatory domain to KR..." | tee /dev/tty1
echo "🔓 Unblocking Wi-Fi via rfkill..." | tee /dev/tty1
sudo rfkill unblock wifi
sudo rfkill unblock all
sudo iw reg set KR
WPA_CONF="/etc/wpa_supplicant/wpa_supplicant.conf"
if [ ! -f "$WPA_CONF" ]; then
    echo "⚠️  $WPA_CONF not found, creating with country=KR..." | tee /dev/tty1
    echo "country=KR" | sudo tee "$WPA_CONF" > /dev/null
elif ! grep -q "^country=KR" "$WPA_CONF"; then
    echo "✏️  Updating country code in $WPA_CONF..." | tee /dev/tty1
    sudo sed -i 's/^#\?country=.*/country=KR/' "$WPA_CONF"
fi
echo "🗺 Setting country in NetworkManager config..." | tee /dev/tty1
sudo mkdir -p /etc/NetworkManager/conf.d
sudo tee /etc/NetworkManager/conf.d/99-country.conf > /dev/null <<NMCONF
  [device]
  wifi.scan-rand-mac-address=no

  [regulatory]
  country=KR
NMCONF

sudo systemctl restart NetworkManager

# 1. Install required system packages
echo "📦 Installing system dependencies..." | tee /dev/tty1
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pip python3-flask dnsmasq hostapd

# 2. Ensure Flask is installed in case it's missing
if ! python3 -c "import flask" &>/dev/null; then
    echo "📦 Installing Flask via pip..." | tee /dev/tty1
    pip3 install flask
fi

# 3. Ensure web script exists
WEB_SCRIPT="$(eval echo ~$USER)/AutoFormBotCode/webserver/app.py"
if [ ! -f "$WEB_SCRIPT" ]; then
    echo "⚠️  Web server script not found: $WEB_SCRIPT" | tee /dev/tty1
    echo "📄 Creating a default app.py for Flask..." | tee /dev/tty1
    mkdir -p "$(dirname "$WEB_SCRIPT")"
    cat > "$WEB_SCRIPT" <<PYEOF
from flask import Flask, request, render_template_string
import subprocess
from pathlib import Path

app = Flask(__name__)

html = """
<!DOCTYPE html>
<html>
<head><title>AutoFormBotpi Wi-Fi Setup</title></head>
<body>
  <h2>Wi-Fi Setup</h2>
  <form action="/" method="POST">
    SSID: <input type="text" name="ssid"><br>
    Password: <input type="password" name="psk"><br>
    <input type="submit" value="Save">
  </form>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ssid = request.form["ssid"]
        psk = request.form["psk"]

        # Delete any existing connection
        subprocess.run(["sudo", "nmcli", "connection", "delete", ssid])

        # Create and configure the connection
        subprocess.run([
            "sudo", "nmcli", "connection", "add", "type", "wifi", "con-name", ssid,
            "ifname", "wlan0", "ssid", ssid
        ])
        subprocess.run([
            "sudo", "nmcli", "connection", "modify", ssid,
            "wifi-sec.key-mgmt", "wpa-psk",
            "wifi-sec.psk", psk
        ])
        subprocess.run([
            "sudo", "nmcli", "connection", "up", ssid
        ])

        script_path = str(Path.home() / "AutoFormBotCode/scripts/nmservice/04_auto_wifi_or_ap.sh")
        subprocess.run(["sudo", script_path])
        return f"<p>Saved and attempted connection to {ssid}. Please check status.</p><a href='/'>Back</a>"
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
PYEOF
fi

# 4. Create systemd service file
echo "🛠 Creating systemd service for web server..." | tee /dev/tty1
sudo tee /etc/systemd/system/autoformbot_web.service > /dev/null <<EOF
[Unit]
Description=AutoFormBot Web Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 $(eval echo ~$USER)/AutoFormBotCode/webserver/app.py
WorkingDirectory=$(eval echo ~$USER)/AutoFormBotCode/webserver
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$(logname)

[Install]
WantedBy=multi-user.target
EOF

# 5. Enable and start the service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable autoformbot_web.service
sudo systemctl start autoformbot_web.service

echo "✅ Web server setup complete and started!" | tee /dev/tty1
