#!/bin/bash

echo "📦 Installing Ultralytics YOLOv11 and Python virtual environment..."

# 1. Create and activate virtual environment
if [ -d "AutoFormBot_venv" ]; then
    echo "🔁 Virtual environment 'AutoFormBot_venv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment 'AutoFormBot_venv'..."
    python3.11 -m venv AutoFormBot_venv
fi
source AutoFormBot_venv/bin/activate
# 2. Install ultralytics Yolov11
pip install --upgrade pip
pip install matplotlib pandas pillow psutil py-cpuinfo pyyaml scipy seaborn torch torchvision tqdm ultralytics-thop
pip install ultralytics==8.3.104  --no-deps

echo "✅ Ultralytics YOLOv11 install complete!"
echo "🔄 Virtual environment 'AutoFormBot_venv' is ready."

deactivate
echo "👋 Virtual environment deactivated."