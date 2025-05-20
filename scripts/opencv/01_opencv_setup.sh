#!/bin/bash

echo "📦 Installing opencv 4.8.1 and Python virtual environment..."

# 0. Install OpenCV system dependencies
echo "🛠 Installing OpenCV system dependencies..."
sudo apt update
sudo apt install -y \
    libatlas-base-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libcanberra-gtk*

# 1. Create and activate virtual environment
if [ -d "AFB_venv" ]; then
    echo "🔁 Virtual environment 'AFB_venv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment 'AFB_venv'..."
    python3.11 -m venv AFB_venv
fi
source AFB_venv/bin/activate

# 2. Install opencv-contrib-python 4.8.1.78
pip install --upgrade pip
pip install opencv-contrib-python==4.8.1.78 numpy==1.26.4

echo "✅ opencv install complete!"
echo "🔄 Virtual environment 'AFB_venv' is ready."

deactivate
echo "👋 Virtual environment deactivated."