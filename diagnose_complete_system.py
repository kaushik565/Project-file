#!/usr/bin/env python3

"""
Complete ACTJv20 System Diagnosis

This script will systematically test every aspect of the ACTJv20 integration
to identify exactly what's causing the SBC errors and mechanism plate issues.
"""

import sys
import time
import logging
import os

def comprehensive_diagnosis():
    """Complete system diagnosis with step-by-step verification."""
    
    print("🔬 COMPLETE ACTJv20 SYSTEM DIAGNOSIS")
    print("=" * 50)
    print()
    print("Let's find out exactly what's wrong...")
    print()
    
    # Setup logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(message)s')
    
    errors = []
    warnings = []
    
    # STEP 1: Platform Check
    print("🖥️  STEP 1: Platform Verification")
    print("-" * 30)
    
    try:
        import RPi.GPIO as GPIO
        print("✅ Running on Raspberry Pi")
        
        # Check if we can access GPIO
        try:
            GPIO.setmode(GPIO.BCM)
            print("✅ GPIO access available")
        except Exception as e:
            print(f"❌ GPIO access failed: {e}")
            errors.append("Try: sudo python3 script.py")
            
    except ImportError:
        print("❌ NOT on Raspberry Pi - simulation mode")
        warnings.append("Testing on non-Pi hardware")
    
    # STEP 2: Basic GPIO Test
    print("\n🔌 STEP 2: GPIO 12 Basic Test")
    print("-" * 30)
    
    try:
        import RPi.GPIO as GPIO
        
        # Test basic GPIO operations
        GPIO.cleanup()  # Clean start
        GPIO.setmode(GPIO.BCM)
        
        print("Testing GPIO 12 (RASP_IN_PIC)...")
        
        # Setup as output
        GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)
        print("   📌 GPIO 12 setup as OUTPUT")
        
        # Test HIGH
        GPIO.output(12, GPIO.HIGH)
        print("   ⬆️  GPIO 12 = HIGH (3.3V) - ACTJv20 should see READY")
        time.sleep(2)
        
        # Test LOW  
        GPIO.output(12, GPIO.LOW)
        print("   ⬇️  GPIO 12 = LOW (0V) - ACTJv20 should see BUSY")
        time.sleep(2)
        
        # Back to HIGH
        GPIO.output(12, GPIO.HIGH)
        print("   ⬆️  GPIO 12 = HIGH - Ready for ACTJv20")
        
        print("✅ GPIO 12 basic test completed")
        
    except Exception as e:
        print(f"❌ GPIO test failed: {e}")
        errors.append(f"GPIO error: {e}")
    
    # STEP 3: Serial Port Check
    print("\n📡 STEP 3: Serial Port Test")
    print("-" * 30)
    
    try:
        import serial
        
        # Check available ports
        serial_ports = ['/dev/ttyS0', '/dev/ttyAMA0', '/dev/serial0']
        found_ports = []
        
        for port in serial_ports:
            if os.path.exists(port):
                found_ports.append(port)
                print(f"✅ Found serial port: {port}")
        
        if not found_ports:
            print("❌ No serial ports found!")
            errors.append("Enable serial: sudo raspi-config > Interface > Serial")
        else:
            # Test opening primary port
            try:
                ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
                print("✅ Can open /dev/ttyS0 at 115200 baud")
                ser.close()
            except Exception as e:
                print(f"❌ Cannot open /dev/ttyS0: {e}")
                errors.append("Serial port access issue")
                
    except ImportError:
        print("❌ pyserial not installed")
        errors.append("Install: pip3 install pyserial")
    
    # STEP 4: Hardware Controller Test
    print("\n🔧 STEP 4: Hardware Controller Test")
    print("-" * 30)
    
    try:
        from hardware import get_hardware_controller
        
        hardware = get_hardware_controller()
        print(f"✅ Hardware controller: {type(hardware).__name__}")
        
        # Test each method
        print("Testing hardware methods...")
        
        hardware.signal_ready_to_firmware()
        print("   📤 signal_ready_to_firmware() - OK")
        time.sleep(1)
        
        hardware.signal_busy_to_firmware()
        print("   📤 signal_busy_to_firmware() - OK")
        time.sleep(1)
        
        hardware.signal_ready_to_firmware()
        print("   📤 Back to ready - OK")
        
        print("✅ Hardware controller working")
        
    except Exception as e:
        print(f"❌ Hardware controller failed: {e}")
        errors.append(f"Hardware error: {e}")
    
    # STEP 5: Legacy Integration Test
    print("\n🔄 STEP 5: Legacy Integration Test")
    print("-" * 30)
    
    try:
        from actj_legacy_integration import get_legacy_integration, is_legacy_mode
        
        # Check mode
        if is_legacy_mode():
            print("✅ Legacy mode is ACTIVE")
        else:
            print("❌ Legacy mode NOT active")
            errors.append("Run: python3 switch_mode.py legacy")
        
        # Test integration
        legacy = get_legacy_integration()
        print("✅ Legacy integration loaded")
        
        # Test startup
        print("Testing startup sequence...")
        legacy.startup_sequence()
        print("✅ Startup sequence completed")
        
    except Exception as e:
        print(f"❌ Legacy integration failed: {e}")
        errors.append(f"Legacy error: {e}")
    
    # STEP 6: UART Protocol Test
    print("\n📻 STEP 6: UART Protocol Test")
    print("-" * 30)
    
    try:
        from actj_uart_protocol import get_uart_protocol
        
        uart = get_uart_protocol()
        print("✅ UART protocol loaded")
        
        # Don't start actual communication, just verify it loads
        print("✅ UART protocol ready")
        
    except Exception as e:
        print(f"❌ UART protocol failed: {e}")
        errors.append(f"UART error: {e}")
    
    # STEP 7: Configuration Check
    print("\n⚙️  STEP 7: Configuration Check")
    print("-" * 30)
    
    try:
        import configparser
        
        config = configparser.ConfigParser()
        config.read('settings.ini')
        
        # Check critical settings
        gpio_enabled = config.getboolean('hardware', 'gpio_enabled', fallback=False)
        jig_control = config.getboolean('hardware', 'jig_control', fallback=False)
        
        if gpio_enabled:
            print("✅ GPIO enabled in settings")
        else:
            print("❌ GPIO not enabled in settings")
            warnings.append("Enable GPIO in settings.ini")
        
        if jig_control:
            print("✅ Jig control enabled")
        else:
            print("❌ Jig control not enabled")
            warnings.append("Enable jig_control in settings.ini")
        
    except Exception as e:
        print(f"⚠️ Configuration check failed: {e}")
        warnings.append("Check settings.ini file")
    
    # RESULTS AND RECOMMENDATIONS
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS RESULTS")
    print("=" * 60)
    
    if not errors:
        print("🎉 ALL MAJOR TESTS PASSED!")
        print()
        print("✅ GPIO working")
        print("✅ Serial port accessible") 
        print("✅ Hardware controller functional")
        print("✅ Legacy integration loaded")
        print("✅ UART protocol ready")
        print()
        print("💡 LIKELY ISSUES:")
        print("   • Physical connection problems")
        print("   • ACTJv20 firmware timing expectations")
        print("   • Communication protocol mismatch")
        print()
        print("🔧 NEXT STEPS:")
        print("   1. Check PHYSICAL wires: GPIO 12 → RB6")
        print("   2. Check UART wires: TX ↔ RX properly crossed")
        print("   3. Power cycle ACTJv20 completely")
        print("   4. Try MINIMAL test with just GPIO signals")
        
    else:
        print("❌ CRITICAL ISSUES FOUND:")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
        
        if warnings:
            print("\n⚠️ WARNINGS:")
            for i, warning in enumerate(warnings, 1):
                print(f"   {i}. {warning}")
        
        print("\n🔧 FIX THESE ISSUES FIRST:")
        print("   • Resolve all critical errors above")
        print("   • Re-run this diagnosis")
        print("   • Then test with ACTJv20 hardware")
    
    print("\n" + "=" * 60)
    print("💭 REMEMBER:")
    print("   • SBC errors = ACTJv20 can't see/understand Pi signals")
    print("   • mvt plt stuck = Mechanism needs proper GPIO pulses")
    print("   • Both issues are usually timing/communication problems")
    print()
    print("Let's fix these step by step! 💪")
    
    return len(errors) == 0

if __name__ == "__main__":
    print("🚀 Starting comprehensive ACTJv20 diagnosis...")
    print("This will test EVERYTHING to find the real problem.")
    print()
    
    success = comprehensive_diagnosis()
    
    if success:
        print("\n✅ Diagnosis complete - ready for hardware testing")
    else:
        print("\n❌ Issues found - fix these first")
    
    sys.exit(0 if success else 1)