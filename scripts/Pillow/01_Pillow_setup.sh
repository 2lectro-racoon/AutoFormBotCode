#!/bin/bash

echo "📦 Installing Pillow and Python virtual environment..."

# 1. Create and activate virtual environment
if [ -d "AutoFormBot_venv" ]; then
    echo "🔁 Virtual environment 'AutoFormBot_venv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment 'AutoFormBot_venv'..."
    python3.11 -m venv AutoFormBot_venv
fi
source AutoFormBot_venv/bin/activate
# 2. Install Pillow
pip install --upgrade pip
pip install Pillow==9.4.0

echo "✅ Pillow install complete!"
echo "🔄 Virtual environment 'AutoFormBot_venv' is ready."

deactivate
echo "👋 Virtual environment deactivated."