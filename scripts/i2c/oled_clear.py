import time
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas

# Log to temp file for debug
with open("/tmp/oled_clear_log.txt", "a") as f:
    f.write("oled_clear.py started\n")

try:
    serial = i2c(port=1, address=0x3C)
    device = sh1106(serial)

    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline=0, fill=0)

    with open("/tmp/oled_clear_log.txt", "a") as f:
        f.write("OLED cleared successfully\n")

    time.sleep(0.3)

except Exception as e:
    with open("/tmp/oled_clear_log.txt", "a") as f:
        f.write(f"ERROR: {e}\n")