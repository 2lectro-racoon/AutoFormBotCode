#!/bin/bash

CONFIG_FILE="/boot/firmware/config.txt"
GPIO_LINE="gpio=19=op,dl"
GPIO_EXTRA="gpio=7=op,dl gpio=8=op,dl"

# Check if main GPIO line exists
if ! grep -Fxq "$GPIO_LINE" "$CONFIG_FILE"; then
    echo "$GPIO_LINE" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo "✅ Added '$GPIO_LINE' to $CONFIG_FILE"
else
    echo "ℹ️  '$GPIO_LINE' is already present in $CONFIG_FILE"
fi

# Check if extra GPIO line exists
if ! grep -Fq "$GPIO_EXTRA" "$CONFIG_FILE"; then
    echo "$GPIO_EXTRA" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo "✅ Added '$GPIO_EXTRA' to $CONFIG_FILE"
else
    echo "ℹ️  '$GPIO_EXTRA' is already present in $CONFIG_FILE"
fi