#!/bin/bash
set -e

USER_HOME=$(eval echo ~${SUDO_USER:-$USER})
VENV_PATH="$USER_HOME/.afbvenv"
OLED_SCRIPT_PATH="$USER_HOME/AutoFormBotCode/scripts/i2c/oled_display.py"

# ✅ Check if virtual environment already exists
if [ ! -d "$VENV_PATH" ]; then
    echo "🔧 Creating Python virtual environment at $VENV_PATH"
    python3 -m venv "$VENV_PATH"
    if [ ! -f "$VENV_PATH/bin/python3" ]; then
        echo "❌ Failed to create virtual environment. Exiting."
        exit 1
    fi
else
    echo "📂 Virtual environment already exists. Skipping creation."
fi

# ⭐ Activate the virtual environment
source "$VENV_PATH/bin/activate"

# 📦 Install OLED dependencies
pip install --upgrade pip
pip install \
  adafruit-blinka \
  adafruit-circuitpython-ssd1306 \
  adafruit-circuitpython-ina219 \
  adafruit-circuitpython-vl53l1x \
  adafruit-circuitpython-mpu6050 \
  pillow \
  netifaces


# 🎉 Done
echo "✅ Virtual environment setup complete."
echo "⚡ To run OLED script manually:"
echo "    source \"$VENV_PATH/bin/activate\" && python \"$OLED_SCRIPT_PATH\""
