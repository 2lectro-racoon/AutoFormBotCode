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
    libcanberra-gtk* \
    libqtgui4 \
    libqt4-test

# 1. Create and activate virtual environment
if [ -d "AutoFormBot_venv" ]; then
    echo "🔁 Virtual environment 'AutoFormBot_venv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment 'AutoFormBot_venv'..."
    python3.11 -m venv AutoFormBot_venv
fi
source AutoFormBot_venv/bin/activate
pip install --upgrade pip
pip install opencv-python-contrib==4.8.1.78

echo "✅ opencv install complete!"
echo "🔄 Virtual environment 'AutoFormBot_venv' is ready."

deactivate
echo "👋 Virtual environment deactivated."