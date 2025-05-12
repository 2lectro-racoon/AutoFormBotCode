#!/bin/bash

echo "📦 Setting up lgpio and Python virtual environment..."

# 1. Create and activate virtual environment
if [ -d "AutoFormBot_venv" ]; then
    echo "🔁 Virtual environment 'AutoFormBot_venv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment 'AutoFormBot_venv'..."
    python3.11 -m venv AutoFormBot_venv
fi
source AutoFormBot_venv/bin/activate

# 2. Install lgpio for Python
pip install --upgrade pip
pip install lgpio

# 3. (Optional) Install lgpio system package
sudo apt update
sudo apt install -y lgpio

echo "✅ lgpio setup complete!"
echo "🔄 Virtual environment 'AutoFormBot_venv' is ready and lgpio system package is installed."

deactivate
echo "👋 Virtual environment deactivated."
