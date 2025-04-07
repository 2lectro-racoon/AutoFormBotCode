#!/bin/bash

echo "🔧 Updating packages..."
sudo apt update

echo "📦 Installing required packages..."
sudo apt install -y hostapd dnsmasq iw net-tools python3-pip python3-venv

echo "📂 Creating Flask web server directory..."
mkdir -p ~/wifi_portal
cd ~/wifi_portal

echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

echo "📦 Installing Flask inside virtual environment..."
./venv/bin/pip install flask

echo "📝 Creating Flask app (app.py)..."
cat <<EOF > app.py
from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

html = """
<!DOCTYPE html>
<html>
<head><title>Wi-Fi Setup</title></head>
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
        config = f"""ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=GB

network={{
    ssid="{ssid}"
    psk="{psk}"
    scan_ssid=1
}}"""
        subprocess.run(["sudo", "tee", "/etc/wpa_supplicant/wpa_supplicant.conf"], input=config.encode())
        subprocess.run(["sudo", "systemctl", "stop", "hostapd"])
        subprocess.run(["sudo", "systemctl", "stop", "dnsmasq"])
        subprocess.run(["sudo", "ip", "addr", "flush", "dev", "wlan0"])
        subprocess.run(["sudo", "ip", "link", "set", "wlan0", "down"])
        subprocess.run(["sudo", "ip", "link", "set", "wlan0", "up"])
        subprocess.run(["sudo", "wpa_supplicant", "-B", "-i", "wlan0", "-c", "/etc/wpa_supplicant/wpa_supplicant.conf"])
        subprocess.run(["sudo", "dhclient", "wlan0"])
        return f"<p>Network {ssid} saved!</p><a href='/'>Back</a>"
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
EOF

echo "✅ Setup completed!"
echo "▶️ To manually run the Flask server, use:"
echo "sudo ~/wifi_portal/venv/bin/python ~/wifi_portal/app.py"