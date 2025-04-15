#!/bin/bash

echo "📦 Setting up pigpio and Python virtual environment..."

# 1. Create and activate virtual environment
if [ -d "AutoFormBot_venv" ]; then
    echo "🔁 Virtual environment 'AutoFormBot_venv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment 'AutoFormBot_venv'..."
    python3.11 -m venv AutoFormBot_venv
fi
source AutoFormBot_venv/bin/activate

# 2. Install pigpio for Python
pip install --upgrade pip
pip install pigpio

# 3. Install and enable pigpio system daemon
sudo apt update
sudo apt install -y pigpio python3-pigpio

sudo systemctl enable pigpiod
sudo systemctl start pigpiod

echo "✅ pigpio setup complete!"
echo "🔄 Virtual environment 'AutoFormBot_venv' is ready and pigpiod is running."

deactivate
echo "👋 Virtual environment deactivated."
