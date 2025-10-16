#!/bin/bash
# Enable I2C Interface on Raspberry Pi
# Run this script on the Raspberry Pi to enable I2C for LCD support

echo "=== Enabling I2C Interface on Raspberry Pi ==="

# Check if already enabled
if [ -e /dev/i2c-1 ]; then
    echo "✓ I2C already enabled at /dev/i2c-1"
else
    echo "Enabling I2C interface..."
    
    # Enable I2C using raspi-config non-interactively
    sudo raspi-config nonint do_i2c 0
    
    # Verify the setting in boot config
    if ! grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
        echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
    fi
    
    # Add i2c modules if not present
    if ! grep -q "i2c-dev" /etc/modules; then
        echo "i2c-dev" | sudo tee -a /etc/modules
    fi
    
    echo "I2C enabled in configuration"
fi

# Install I2C tools if not present
if ! command -v i2cdetect &> /dev/null; then
    echo "Installing I2C tools..."
    sudo apt-get update -qq
    sudo apt-get install -y i2c-tools
fi

# Add user to i2c group
sudo usermod -a -G i2c qateam
sudo usermod -a -G gpio qateam

echo ""
echo "=== I2C Setup Complete ==="

# Check if reboot is needed
if [ ! -e /dev/i2c-1 ]; then
    echo "⚠️  REBOOT REQUIRED"
    echo "Run: sudo reboot"
    echo "After reboot, verify with: ls /dev/i2c-*"
else
    echo "✓ I2C interface ready"
    
    # Scan for devices
    echo ""
    echo "Scanning I2C bus for devices..."
    sudo i2cdetect -y 1
    
    echo ""
    echo "Look for your LCD address (typically 0x27 or 0x3f)"
    echo "Update settings_production.ini if different address found"
fi