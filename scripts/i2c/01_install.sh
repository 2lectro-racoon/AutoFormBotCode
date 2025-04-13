#!/bin/bash

VENV_PATH="$HOME/autoformbot_oled_venv"
OLED_SCRIPT_PATH="$HOME/AutoFormBotCode/scripts/oled_display_status.py"

# ✅ Check if virtual environment already exists
if [ ! -d "$VENV_PATH" ]; then
    echo "🔧 Creating Python virtual environment at $VENV_PATH"
    python3 -m venv "$VENV_PATH"
else
    echo "📂 Virtual environment already exists. Skipping creation."
fi

# ⭐ Activate the virtual environment
source "$VENV_PATH/bin/activate"

# 📦 Install OLED dependencies
pip install --upgrade pip
pip install adafruit-circuitpython-ssd1306 adafruit-blinka

# 🎉 Done
echo "✅ Virtual environment setup complete."
echo "⚡ To run OLED script manually:"
echo "    source ~/autoformbot_oled_venv/bin/activate && python $OLED_SCRIPT_PATH"
