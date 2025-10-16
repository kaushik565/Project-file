#!/bin/bash

# Raspberry Pi Setup Commands for ACTJv20 Hardware
# Run these commands on your Raspberry Pi

echo "Setting up ACTJv20 Legacy Mode on Raspberry Pi..."

# 1. Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# 2. Switch to legacy mode
echo "Switching to ACTJv20 legacy mode..."
python3 switch_mode.py legacy

# 3. Update settings for GPIO hardware
echo "Configuring GPIO hardware controller..."
sed -i 's/controller = mock/controller = gpio/' settings.ini

# 4. Set up GPIO permissions
echo "Setting up GPIO permissions..."
sudo usermod -a -G gpio $USER

# 5. Test the legacy integration
echo "Testing ACTJv20 legacy integration..."
python3 test_actj_legacy.py

# 6. Show GPIO pin mapping
echo "GPIO Pin Mapping for ACTJv20 connection:"
python3 test_actj_legacy.py --gpio-map

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Connect GPIO 12 (Pi) to RB6 (ACTJv20 RASP_IN_PIC)"
echo "2. Connect USB QR scanner"
echo "3. Power on ACTJv20 hardware"
echo "4. Run: python3 main.py"
echo ""
echo "Expected result: No SBC Er-1 or SBC Er-2 errors!"