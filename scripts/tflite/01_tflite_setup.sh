#!/bin/bash

echo "📦 Installing tflite and Python virtual environment..."

# 1. Create and activate virtual environment
if [ -d ".afbvenv" ]; then
    echo "🔁 Virtual environment '.afbvenv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment '.afbvenv'..."
    python3.11 -m venv .afbvenv
fi
source .afbvenv/bin/activate
# 2. Install TensorFlow 2.20.0
pip install --upgrade pip
pip install tensorflow==2.20.0

echo "✅ TensorFlow install complete!"
echo "🔄 Virtual environment '.afbvenv' is ready."

deactivate
echo "👋 Virtual environment deactivated."