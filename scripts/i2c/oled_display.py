import subprocess
import time
import netifaces
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont

def get_mode_and_info():
    try:
        # Get interface type (AP or managed)
        iw_output = subprocess.check_output("iw dev wlan0 info", shell=True).decode()
        mode = "Unknown"
        if "type AP" in iw_output:
            mode = "AP"
        elif "type managed" in iw_output:
            mode = "STA"

        # Get SSID
        ssid = "N/A"
        try:
            if mode == "STA":
                ssid = subprocess.check_output(
                    "iw dev wlan0 link | grep SSID | awk '{print $2}'",
                    shell=True).decode().strip()
            elif mode == "AP":
                with open("/etc/hostapd/hostapd.conf") as f:
                    for line in f:
                        if line.startswith("ssid="):
                            ssid = line.strip().split("=")[1]
                            break
        except:
            pass

        # Get IP
        ip = "No IP"
        interface = 'wlan0' if mode == "STA" else 'eth0'
        if interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                ip = addrs[netifaces.AF_INET][0]['addr']

        return mode, ssid, ip
    except Exception as e:
        return "Error", "Check", str(e)

def display_info():
    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial, height=32)

    # Use a larger TrueType font
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)

    while True:
        mode, ssid, ip = get_mode_and_info()
        with canvas(device) as draw:
            if mode == "STA":
                draw.text((0, 0), f"{ssid}", font=font, fill=255)
                draw.text((0, 16), f"{ip}", font=font, fill=255)
            else:
                draw.text((0, 0), f"{ssid}", font=font, fill=255)
                draw.text((0, 16), f"{ip}", font=font, fill=255)
        time.sleep(5)

if __name__ == "__main__":
    display_info()
