#!/bin/bash

# ACTJv20 Deployment Script for Raspberry Pi
# This script sets up everything needed to run main.py with your old ACTJv20 jig

echo "🚀 ACTJv20 Automatic Operation Setup"
echo "====================================="
echo ""

# 1. Update system
echo "1️⃣ Updating system packages..."
sudo apt update
sudo apt upgrade -y

# 2. Install Python dependencies
echo ""
echo "2️⃣ Installing Python dependencies..."
pip3 install -r requirements.txt
pip3 install pyserial RPi.GPIO

# 3. Enable serial port
echo ""
echo "3️⃣ Configuring Raspberry Pi serial port..."
sudo raspi-config nonint do_serial_hw 0   # Enable serial port hardware
sudo raspi-config nonint do_serial_cons 1 # Disable serial console
echo "enable_uart=1" | sudo tee -a /boot/config.txt
echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt

# 4. Set up GPIO permissions
echo ""
echo "4️⃣ Setting up GPIO permissions..."
sudo usermod -a -G gpio $USER
sudo usermod -a -G dialout $USER

# 5. Switch to legacy mode
echo ""
echo "5️⃣ Switching to ACTJv20 legacy mode..."
python3 switch_mode.py legacy

# 6. Update settings for GPIO (not mock)
echo ""
echo "6️⃣ Configuring for GPIO hardware..."
sed -i 's/controller = mock/controller = gpio/' settings.ini

# 7. Test the integration
echo ""
echo "7️⃣ Testing ACTJv20 integration..."
python3 test_complete_system.py

echo ""
echo "✅ SETUP COMPLETE!"
echo "=================="
echo ""
echo "🔌 Hardware Connections Required:"
echo "   • GPIO 12 (Pi) → RB6 (ACTJv20 RASP_IN_PIC)"
echo "   • UART TX (Pi) → UART RX (ACTJv20)"
echo "   • UART RX (Pi) → UART TX (ACTJv20)"
echo "   • Ground (Pi) → Ground (ACTJv20)"
echo "   • USB QR Scanner → Pi USB port"
echo ""
echo "🎯 How to Use:"
echo "   1. Power on ACTJv20 hardware"
echo "   2. Run: python3 main.py"
echo "   3. Fill batch details in application"
echo "   4. Click 'Start Batch'"
echo "   5. Press START button on ACTJv20 jig"
echo "   6. Jig runs automatically with QR validation!"
echo ""
echo "🔧 Expected Results:"
echo "   • No 'SBC Er-1' or 'SBC Er-2' errors"
echo "   • Automatic cartridge advancement"
echo "   • QR scanning and validation"
echo "   • Pass/reject decisions"
echo "   • Complete batch logging"
echo ""
echo "⚠️  IMPORTANT: Reboot Pi after first setup to activate serial port"
echo "   sudo reboot"
echo ""