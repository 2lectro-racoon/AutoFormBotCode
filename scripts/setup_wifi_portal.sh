#!/bin/bash

echo "🔧 Updating packages..."
sudo apt update

echo "📦 Installing required packages..."
sudo apt install -y hostapd dnsmasq iw net-tools python3-pip

echo "🐍 Installing Flask..."
pip3 install flask

echo "📂 Creating Flask web server directory..."
mkdir -p ~/wifi_portal
cat <<EOF > ~/wifi_portal/app.py
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
        subprocess.run(["sudo", "wpa_cli", "add_network"])
        subprocess.run(["sudo", "wpa_cli", "set_network", "0", "ssid", f'"{ssid}"'])
        subprocess.run(["sudo", "wpa_cli", "set_network", "0", "psk", f'"{psk}"'])
        subprocess.run(["sudo", "wpa_cli", "enable_network", "0"])
        subprocess.run(["sudo", "wpa_cli", "save_config"])
        return f"<p>Network {ssid} saved!</p><a href='/'>Back</a>"
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
EOF

echo "📜 To run the web server, use:"
echo "sudo python3 ~/wifi_portal/app.py"

echo "✅ Setup completed!"