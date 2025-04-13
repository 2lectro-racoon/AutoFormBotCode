#!/bin/bash

CONFIG_FILE="/boot/firmware/config.txt"
GPIO_LINE="gpio=19=op,dl"

# Check if line already exists
if ! grep -Fxq "$GPIO_LINE" "$CONFIG_FILE"; then
    echo "$GPIO_LINE" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo "✅ Added '$GPIO_LINE' to $CONFIG_FILE"
else
    echo "ℹ️  '$GPIO_LINE' is already present in $CONFIG_FILE"
fi