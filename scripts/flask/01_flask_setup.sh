#!/bin/bash

echo "📦 Installing Flask and Python virtual environment..."

# 1. Create and activate virtual environment
if [ -d "AFB_venv" ]; then
    echo "🔁 Virtual environment 'AFB_venv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment 'AFB_venv'..."
    python3.11 -m venv AFB_venv
fi
source AFB_venv/bin/activate

# 2. Install Flask
pip install --upgrade pip
pip install flask

echo "✅ Flask installation complete!"
echo "🔄 Virtual environment 'AFB_venv' is ready."

deactivate
echo "👋 Virtual environment deactivated."