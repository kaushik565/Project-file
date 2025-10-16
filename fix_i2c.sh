#!/bin/bash
# Quick I2C Fix Script for Raspberry Pi
# Resolves: "could not open file /dev/i2c-1 no such file or directory"

echo "🔧 Quick I2C Fix for Raspberry Pi"
echo "================================="

# Check if running on Pi
if ! command -v raspi-config >/dev/null 2>&1; then
    echo "❌ This script must run on a Raspberry Pi"
    exit 1
fi

echo "Fixing I2C interface issue..."

# 1. Enable I2C interface
echo "📋 Step 1: Enabling I2C interface"
sudo raspi-config nonint do_i2c 0
echo "   ✅ I2C enabled via raspi-config"

# 2. Ensure boot config has I2C enabled
echo "📋 Step 2: Updating boot configuration"
if ! grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
    echo "   ✅ Added I2C to boot config"
else
    echo "   ✅ I2C already in boot config"
fi

# 3. Add I2C modules
echo "📋 Step 3: Adding I2C modules"
if ! grep -q "i2c-dev" /etc/modules; then
    echo "i2c-dev" | sudo tee -a /etc/modules
    echo "   ✅ Added i2c-dev module"
else
    echo "   ✅ i2c-dev module already present"
fi

# 4. Install I2C tools
echo "📋 Step 4: Installing I2C tools"
sudo apt-get update -qq
sudo apt-get install -y i2c-tools
echo "   ✅ I2C tools installed"

# 5. Fix user permissions
echo "📋 Step 5: Setting user permissions"
sudo usermod -a -G i2c qateam
sudo usermod -a -G gpio qateam
echo "   ✅ User added to i2c and gpio groups"

# 6. Check if reboot needed
echo ""
echo "🔍 Checking I2C status..."
if [ -e /dev/i2c-1 ]; then
    echo "✅ I2C interface is ready at /dev/i2c-1"
    
    # Scan for devices
    echo ""
    echo "🔍 Scanning for I2C devices..."
    sudo i2cdetect -y 1
    
    echo ""
    echo "📋 Look for your LCD address above (commonly 0x27 or 0x3f)"
    echo "If you see a number, your LCD is connected and working!"
    
else
    echo "⚠️  I2C interface not yet active"
    echo ""
    echo "🔄 REBOOT REQUIRED"
    echo "Run: sudo reboot now"
    echo ""
    echo "After reboot:"
    echo "1. Check I2C: ls /dev/i2c-*"
    echo "2. Scan devices: sudo i2cdetect -y 1"
    echo "3. Run your program: python main.py"
fi

echo ""
echo "✅ I2C fix complete!"