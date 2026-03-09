#!/bin/bash

echo "📦 Installing Ultralytics YOLOv11 and Python virtual environment..."

# 1. Create and activate virtual environment
if [ -d ".afbvenv" ]; then
    echo "🔁 Virtual environment '.afbvenv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment '.afbvenv'..."
    python3 -m venv ~/.afbvenv
fi
source ~/.afbvenv/bin/activate
# 2. Install ultralytics Yolov11
pip install --upgrade pip
pip install ultralytics  --no-deps
pip install matplotlib pandas pillow psutil py-cpuinfo pyyaml scipy seaborn torch torchvision tqdm ultralytics-thop


echo "✅ Ultralytics YOLOv11 install complete!"
echo "🔄 Virtual environment '.afbvenv' is ready."

deactivate
echo "👋 Virtual environment deactivated."