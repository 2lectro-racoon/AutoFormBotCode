#!/bin/bash
set -e

if [[ "$1" =~ ^[0-9]+$ ]]; then
  printf -v SSID "AFB-setup%03d" "$1"
else
  SSID="AFB-setup"
fi
export SSID

LOG_FILE="install_log_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "AutoFormBot Auto Wi-Fi/AP mode switching script install..."

AUTOFORM_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bash "$AUTOFORM_PATH/scripts/nmservice/01_setup_web_server.sh"
SSID="$SSID" bash "$AUTOFORM_PATH/scripts/nmservice/05_enable_auto_wifi_service.sh"
SSID="$SSID" bash "$AUTOFORM_PATH/scripts/nmservice/07_enable_wifi_monitor.sh"
bash "$AUTOFORM_PATH/scripts/i2c/01_install.sh"
bash "$AUTOFORM_PATH/scripts/i2c/02_oled_service.sh"
bash "$AUTOFORM_PATH/scripts/i2c/03_oled_clear_service.sh"
bash "$AUTOFORM_PATH/scripts/opencv/01_opencv_setup.sh"
bash "$AUTOFORM_PATH/scripts/YOLOv11/01_yolo_setup.sh"
bash "$AUTOFORM_PATH/scripts/tflite/01_tflite_setup.sh"
bash "$AUTOFORM_PATH/scripts/gpio/02_gpio_setup.sh"
bash "$AUTOFORM_PATH/scripts/afb/01_picamera2_setup.sh"

echo '# === Auto PYTHONPATH for AutoFormBotCode ===' >> "$HOME/AFB_venv/bin/activate"
echo 'export AUTOBOT_ROOT="$HOME/AutoFormBotCode"' >> "$HOME/AFB_venv/bin/activate"
echo 'export PYTHONPATH="$AUTOBOT_ROOT/scripts/gpio:$AUTOBOT_ROOT/scripts/opencv:$AUTOBOT_ROOT/scripts/tflite:$AUTOBOT_ROOT/scripts/YOLOv11:$AUTOBOT_ROOT/scripts/package:$PYTHONPATH"' >> "$HOME/AFB_venv/bin/activate"

bash "$AUTOFORM_PATH/scripts/gpio/01_servo_stop.sh"

echo 'avoid_warnings=1' | sudo tee -a /boot/firmware/config.txt
echo "AutoFormBot Setting Done..."

sudo reboot