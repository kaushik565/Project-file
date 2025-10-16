#!/bin/bash
# Complete System Test - Batch Validation System
# Run this after scanner is working to test the full system

echo "🚀 COMPLETE SYSTEM TEST"
echo "======================="

echo "1. 📋 Checking project files..."
required_files=("main.py" "config.py" "hardware.py" "logic.py" "test_pi_usb_scanner.py")
missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file - MISSING"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ Missing files. Make sure all project files are copied to Pi."
    exit 1
fi

echo
echo "2. 🔌 Testing hardware communication..."
if python3 verify_system.py | grep -q "PASSED"; then
    echo "   ✅ Hardware verification passed"
else
    echo "   ⚠️ Hardware verification issues - check output above"
fi

echo
echo "3. 📱 Testing USB scanner..."
echo "   Scanning test QR in 5 seconds..."
echo "   Scan any QR code when ready:"
echo -n "   "
read -t 10 test_scan
if [ -n "$test_scan" ]; then
    echo "   ✅ Scanner working: '$test_scan'"
else
    echo "   ❌ Scanner timeout - check scanner setup"
fi

echo
echo "4. 📁 Checking log directories..."
for dir in "batch_logs" "Batch_Setup_Logs"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir exists"
    else
        echo "   📁 Creating $dir..."
        mkdir -p "$dir"
        echo "   ✅ $dir created"
    fi
done

echo
echo "5. ⚙️ Checking configuration..."
if [ -f "settings.ini" ]; then
    echo "   ✅ settings.ini found"
    
    # Check key settings
    if grep -q "controller = gpio" settings.ini; then
        echo "   ✅ Hardware controller set to GPIO"
    else
        echo "   ⚠️ Hardware controller not set to GPIO"
        echo "      Edit settings.ini: [hardware] controller = gpio"
    fi
    
    if grep -q "enabled = false" settings.ini | head -1; then
        echo "   ✅ Camera disabled (using USB scanner)"
    fi
else
    echo "   ⚠️ settings.ini not found - using defaults"
fi

echo
echo "6. 🧪 Testing Python imports..."
python3 -c "
import main
import config
import hardware
import logic
print('   ✅ All modules import successfully')
" 2>/dev/null || echo "   ❌ Module import errors - check Python dependencies"

echo
echo "======================="
echo "📊 SYSTEM STATUS:"
echo "======================="

# Determine system readiness
all_good=true

# Check critical components
if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ Missing project files"
    all_good=false
fi

if ! python3 -c "import main" 2>/dev/null; then
    echo "❌ Python import issues"
    all_good=false
fi

if [ ! -d "batch_logs" ]; then
    echo "❌ Log directories missing"
    all_good=false
fi

if [ -z "$test_scan" ]; then
    echo "❌ Scanner not responding"
    all_good=false
fi

if [ "$all_good" = true ]; then
    echo "🎉 SYSTEM READY FOR PRODUCTION!"
    echo ""
    echo "🚀 NEXT STEPS:"
    echo "   1. Connect jig hardware (PIC controller, sensors, actuators)"
    echo "   2. Program PIC with firmware: hardware_firmware/main.hex"
    echo "   3. Run application: python3 main.py"
    echo "   4. Follow batch setup wizard"
    echo "   5. Start scanning cartridges!"
    echo ""
    echo "📖 OPERATION GUIDE:"
    echo "   • Fill batch info (number, line, moulds)"
    echo "   • Click 'Start Scanning'"
    echo "   • Load cartridges in jig stack"
    echo "   • Press START on physical jig"
    echo "   • Scan QR codes when prompted"
    echo "   • System automatically sorts cartridges"
else
    echo "🔧 ISSUES FOUND - Fix the problems above"
    echo ""
    echo "💡 COMMON SOLUTIONS:"
    echo "   • Copy all files: scp -r project/ pi@pi-ip:/home/pi/"
    echo "   • Install dependencies: pip3 install pyserial"
    echo "   • Fix scanner: ./setup_scanner_pi.sh"
    echo "   • Check wiring: python3 verify_system.py"
fi

echo "======================="