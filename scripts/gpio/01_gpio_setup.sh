#!/bin/bash

echo "📦 Setting up lgpio, SPI (spidev), and Python virtual environment..."

# 1. Create and activate virtual environment
if [ -d ".afbvenv" ]; then
    echo "🔁 Virtual environment '.afbvenv' already exists. Activating..."
else
    echo "🆕 Creating virtual environment '.afbvenv'..."
    python3.11 -m venv .afbvenv
fi
source .afbvenv/bin/activate

# 2. Install Python packages for low-level hardware access
pip install --upgrade pip

# lgpio: legacy GPIO access (used only for STM32 NRST reset)
pip install lgpio

# spidev: SPI communication with STM32
pip install spidev

# mmap is part of Python standard library (no installation required)

# 3. Install required system packages
sudo apt update

# lgpio: GPIO access from userspace
sudo apt install -y lgpio

# python3-spidev: system-level SPI bindings (backup for non-venv execution)
sudo apt install -y python3-spidev

echo "✅ lgpio and SPI (spidev) setup complete!"
echo "🔄 Virtual environment '.afbvenv' is ready and lgpio system package is installed."

deactivate
echo "👋 Virtual environment deactivated."
