import time
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas

# Initialize I2C interface and OLED device
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)

# Clear the screen by drawing a black rectangle over the whole display
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline=0, fill=0)

time.sleep(0.5)  # Give it a short moment to take effect
