#!/bin/bash
# Quick USB Scanner Setup for Raspberry Pi
# Run this script to fix common scanner issues

echo "🔧 USB SCANNER SETUP - RASPBERRY PI"
echo "===================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️ Don't run this as root (sudo). Run as normal user."
    exit 1
fi

echo "1. 📡 Checking USB devices..."
if command -v lsusb &> /dev/null; then
    echo "USB devices connected:"
    lsusb | grep -E "(scanner|Scanner|barcode|Barcode|Symbol|Honeywell|Zebra|Datalogic)" || echo "   No obvious scanners detected"
    echo
else
    echo "❌ lsusb command not found"
fi

echo "2. 👤 Checking user permissions..."
if groups | grep -q "input"; then
    echo "✅ User is in 'input' group"
else
    echo "❌ User not in 'input' group"
    echo "💡 Adding user to input group..."
    sudo usermod -a -G input $USER
    echo "✅ Added to input group (logout/login required)"
fi

if groups | grep -q "dialout"; then
    echo "✅ User is in 'dialout' group"
else
    echo "❌ User not in 'dialout' group"
    echo "💡 Adding user to dialout group..."
    sudo usermod -a -G dialout $USER
    echo "✅ Added to dialout group"
fi

echo
echo "3. 📁 Checking input devices..."
if [ -d "/dev/input" ]; then
    event_count=$(ls /dev/input/event* 2>/dev/null | wc -l)
    echo "✅ Found $event_count input event devices"
    ls -la /dev/input/event* 2>/dev/null | head -5
else
    echo "❌ /dev/input directory not found"
fi

echo
echo "4. 🔋 Checking USB power..."
if [ -f "/sys/kernel/debug/usb/devices" ]; then
    echo "USB power info available"
else
    echo "💡 USB power debugging not available"
fi

echo
echo "5. 📦 Checking Python dependencies..."
python3 -c "import serial; print('✅ pyserial installed')" 2>/dev/null || echo "❌ pyserial not installed - run: pip3 install pyserial"
python3 -c "import tkinter; print('✅ tkinter available')" 2>/dev/null || echo "❌ tkinter not available - run: sudo apt install python3-tk"

echo
echo "6. 🧪 Quick scanner test..."
echo "   Try scanning a QR code in the next 10 seconds..."
echo "   (Text should appear automatically if scanner is working)"
echo -n "   Scan result: "
read -t 10 scan_result
if [ -n "$scan_result" ]; then
    echo "✅ Scanner appears to be working: '$scan_result'"
else
    echo "❌ No scanner input detected"
fi

echo
echo "======================================"
echo "📋 SETUP SUMMARY:"
echo "======================================"

# Check if everything is ready
all_good=true

# Check groups
if ! groups | grep -q "input"; then
    echo "❌ User permissions need fix (logout/login required)"
    all_good=false
else
    echo "✅ User permissions OK"
fi

# Check USB
if lsusb &> /dev/null; then
    echo "✅ USB detection working"
else
    echo "❌ USB detection issues"
    all_good=false
fi

# Check Python
if python3 -c "import serial" 2>/dev/null; then
    echo "✅ Python dependencies OK"
else
    echo "❌ Python dependencies missing"
    all_good=false
fi

echo
if [ "$all_good" = true ]; then
    echo "🎉 SYSTEM READY!"
    echo "💡 Next steps:"
    echo "   1. If you added user to groups, logout and login"
    echo "   2. Run: python3 test_pi_usb_scanner.py"
    echo "   3. Test scanner with application: python3 main.py"
else
    echo "🔧 ISSUES FOUND - follow the fixes above"
    echo "💡 Common solutions:"
    echo "   • Logout and login (for group changes)"
    echo "   • pip3 install pyserial"
    echo "   • sudo apt update && sudo apt upgrade"
    echo "   • Try different USB port"
    echo "   • Check scanner configuration"
fi

echo "======================================"