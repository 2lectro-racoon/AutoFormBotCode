#!/bin/bash

echo "📦 Setting up picamera2 and Python virtual environment..."

# 1. Create and activate virtual environment
if [ -d "AFB_venv" ]; then
    echo "🔁 Virtual environment 'AFB_venv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment 'AFB_venv'..."
    python3.11 -m venv AFB_venv
fi
source AFB_venv/bin/activate

# 2. Upgrade pip and install picamera2
pip install --upgrade pip

# Ensure system dependencies are available for picamera2
sudo apt update
sudo apt install -y python3-picamera2 libcamera-apps libatlas-base-dev

echo "✅ picamera2 setup complete!"
echo "🔄 Virtual environment 'AFB_venv' is ready with picamera2 and OpenCV installed."

deactivate
echo "👋 Virtual environment deactivated."
