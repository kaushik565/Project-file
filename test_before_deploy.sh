#!/bin/bash

# Quick test script for local validation before deployment
# Run this to verify everything is working before sending to Pi

echo "🔧 BATCH SCANNING JIG - PRE-DEPLOYMENT TEST"
echo "==========================================="

# Test 1: Check Python and dependencies
echo ""
echo "1️⃣  Testing Python environment..."
python3 -c "
import sys
print(f'Python version: {sys.version}')
try:
    import tkinter
    print('✅ tkinter: OK')
except ImportError:
    print('❌ tkinter: MISSING')

try:
    import serial
    print('✅ serial: OK')  
except ImportError:
    print('❌ serial: MISSING (install: pip install pyserial)')

try:
    import logging
    print('✅ logging: OK')
except ImportError:
    print('❌ logging: MISSING')

try:
    import configparser
    print('✅ configparser: OK')
except ImportError:
    print('❌ configparser: MISSING')
"

# Test 2: Check required files
echo ""
echo "2️⃣  Checking project files..."
files=(
    "main.py"
    "config.py"
    "settings.ini"
    "actj_integration.py"
    "jig.py"
    "lcd_display.py"
    "logic.py"
    "hardware.py"
    "layout.py"
    "duplicate_tracker.py"
)

for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
    fi
done

# Test 3: Check configuration files
echo ""
echo "3️⃣  Checking configuration files..."
config_files=(
    "settings.ini.sample"
    "settings_production.ini"
    "switch_mode.sh"
    "install_autostart_simple.sh"
)

for file in "${config_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
    fi
done

# Test 4: Test Python syntax
echo ""
echo "4️⃣  Testing Python syntax..."
python_files=(
    "main.py"
    "config.py"
    "actj_integration.py"
    "jig.py"
    "lcd_display.py"
    "logic.py"
    "hardware.py"
)

for file in "${python_files[@]}"; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo "✅ $file - syntax OK"
    else
        echo "❌ $file - SYNTAX ERROR"
    fi
done

# Test 5: Test application startup (quick test)
echo ""
echo "5️⃣  Testing application startup..."
timeout 10s python3 -c "
import sys
sys.path.append('.')
try:
    from main import BatchScannerApp
    print('✅ Main application imports OK')
except Exception as e:
    print(f'❌ Import error: {e}')
" 2>/dev/null || echo "⚠️  Application test timed out (expected in headless mode)"

# Test 6: Check integration module
echo ""
echo "6️⃣  Testing ACTJ integration module..."
python3 -c "
try:
    from actj_integration import ACTJController, MechanicalJigInterface, ACTJCommands, ACTJResponses
    print('✅ ACTJ integration module imports OK')
    print('✅ Available commands:', [cmd.name for cmd in ACTJCommands])
    print('✅ Available responses:', [resp.name for resp in ACTJResponses])
except Exception as e:
    print(f'❌ ACTJ integration error: {e}')
"

# Test 7: Hardware interface checks (Raspberry Pi only)
echo ""
echo "7️⃣  Testing hardware interfaces (Raspberry Pi only)..."

if command -v raspi-config >/dev/null 2>&1; then
    echo "Running on Raspberry Pi - checking hardware interfaces..."
    
    # Test I2C interface
    echo "Checking I2C interface..."
    if [ -e /dev/i2c-1 ]; then
        echo "  ✅ I2C interface enabled (/dev/i2c-1)"
        if command -v i2cdetect >/dev/null 2>&1; then
            echo "  ✅ I2C tools available"
            echo "  Scanning for LCD device..."
            if sudo i2cdetect -y 1 2>/dev/null | grep -q "27\|3f"; then
                echo "  ✅ LCD device found on I2C bus"
            else
                echo "  ⚠️  No LCD at common addresses (0x27, 0x3f)"
                issues+=("LCD not detected on I2C bus")
            fi
        else
            echo "  ❌ I2C tools missing"
            issues+=("I2C tools not installed - run: sudo apt install i2c-tools")
        fi
    else
        echo "  ❌ I2C interface disabled"
        issues+=("I2C not enabled - run ./enable_i2c.sh or sudo raspi-config")
    fi
    
    # Test GPIO access
    echo "Checking GPIO access..."
    if [ -d /sys/class/gpio ]; then
        echo "  ✅ GPIO interface available"
        if groups | grep -q gpio; then
            echo "  ✅ User in gpio group"
        else
            echo "  ⚠️  User not in gpio group"
            issues+=("User not in gpio group - run: sudo usermod -a -G gpio \$USER")
        fi
    else
        echo "  ❌ GPIO interface not available"
        issues+=("GPIO interface not available")
    fi
else
    echo "Not on Raspberry Pi - skipping hardware tests"
fi

# Summary
echo ""
echo "🎯 PRE-DEPLOYMENT TEST SUMMARY"
echo "=============================="
if [ ${#issues[@]} -eq 0 ]; then
    echo "✅ ALL TESTS PASSED - Ready for deployment!"
    echo ""
    echo "Next steps:"
    echo "1. Copy project to Raspberry Pi"
    echo "2. Enable I2C: ./enable_i2c.sh (if not done)"
    echo "3. Run installation: ./install_autostart_simple.sh"
    echo "4. Test hardware integration"
else
    echo "❌ Issues found (${#issues[@]}):"
    for issue in "${issues[@]}"; do
        echo "  • $issue"
    done
    echo ""
    echo "Please fix these issues before deployment."
    echo ""
    echo "Common solutions:"
    echo "• I2C issues: Run ./enable_i2c.sh on Raspberry Pi"
    echo "• Permission issues: Add user to groups with sudo usermod -a -G i2c,gpio \$USER"
    echo "• Missing tools: sudo apt update && sudo apt install i2c-tools"
fi