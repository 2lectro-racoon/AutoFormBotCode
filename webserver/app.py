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
