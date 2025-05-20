#!/bin/bash

echo "📦 Installing Ultralytics YOLOv11 and Python virtual environment..."

# 1. Create and activate virtual environment
if [ -d "AFB_venv" ]; then
    echo "🔁 Virtual environment 'AFB_venv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment 'AFB_venv'..."
    python3.11 -m venv AFB_venv
fi
source AFB_venv/bin/activate
# 2. Install ultralytics Yolov11
pip install --upgrade pip
pip install ultralytics==8.3.104  --no-deps
pip install matplotlib pandas pillow psutil py-cpuinfo pyyaml scipy seaborn torch torchvision tqdm ultralytics-thop


echo "✅ Ultralytics YOLOv11 install complete!"
echo "🔄 Virtual environment 'AFB_venv' is ready."

deactivate
echo "👋 Virtual environment deactivated."