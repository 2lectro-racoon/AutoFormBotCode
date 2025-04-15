#!/bin/bash

echo "📦 Installing tflite and Python virtual environment..."

# 1. Create and activate virtual environment
if [ -d "AutoFormBot_venv" ]; then
    echo "🔁 Virtual environment 'AutoFormBot_venv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment 'AutoFormBot_venv'..."
    python3.11 -m venv AutoFormBot_venv
fi
source AutoFormBot_venv/bin/activate
# 2. Install TensorFlow 2.19
pip install --upgrade pip
pip install tensorflow==2.19.0

echo "✅ TensorFlow install complete!"
echo "🔄 Virtual environment 'AutoFormBot_venv' is ready."

deactivate
echo "👋 Virtual environment deactivated."