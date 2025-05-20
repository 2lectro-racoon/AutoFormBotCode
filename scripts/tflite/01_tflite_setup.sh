#!/bin/bash

echo "📦 Installing tflite and Python virtual environment..."

# 1. Create and activate virtual environment
if [ -d "AFB_venv" ]; then
    echo "🔁 Virtual environment 'AFB_venv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment 'AFB_venv'..."
    python3.11 -m venv AFB_venv
fi
source AFB_venv/bin/activate
# 2. Install TensorFlow 2.19
pip install --upgrade pip
pip install tensorflow==2.19.0

echo "✅ TensorFlow install complete!"
echo "🔄 Virtual environment 'AFB_venv' is ready."

deactivate
echo "👋 Virtual environment deactivated."