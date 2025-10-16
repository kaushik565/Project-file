#!/usr/bin/env python3

"""
ACTJv20 Pi Verification Script

Quick test to verify the Raspberry Pi setup is working correctly
before running the full main.py application with ACTJv20 integration.
"""

import sys
import os

def test_actj_pi_setup():
    """Test Raspberry Pi setup for ACTJv20."""
    
    print("🔧 ACTJv20 Pi Setup Verification")
    print("================================")
    print()
    
    errors = []
    warnings = []
    
    # Test 1: Check if we're in legacy mode
    print("1️⃣ Checking legacy mode configuration...")
    try:
        from actj_legacy_integration import is_legacy_mode
        if is_legacy_mode():
            print("   ✅ Legacy mode active")
        else:
            print("   ⚠️ Legacy mode not detected")
            warnings.append("Run: python3 switch_mode.py legacy")
    except ImportError as e:
        print(f"   ❌ Legacy integration import failed: {e}")
        errors.append("Legacy integration not available")
    
    # Test 2: Check GPIO availability
    print("\n2️⃣ Checking GPIO support...")
    try:
        import RPi.GPIO as GPIO
        print("   ✅ RPi.GPIO available")
        
        # Test GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(21, GPIO.OUT, initial=GPIO.LOW)
        print("   ✅ GPIO pins configured (12, 18, 21)")
        GPIO.cleanup()
        
    except ImportError:
        print("   ❌ RPi.GPIO not available")
        errors.append("Install RPi.GPIO: pip3 install RPi.GPIO")
    except Exception as e:
        print(f"   ⚠️ GPIO setup warning: {e}")
        warnings.append("GPIO permissions may need setup")
    
    # Test 3: Check serial port
    print("\n3️⃣ Checking serial port...")
    try:
        import serial
        
        # Check if serial port exists
        serial_ports = ['/dev/ttyS0', '/dev/ttyAMA0', '/dev/serial0']
        available_ports = [port for port in serial_ports if os.path.exists(port)]
        
        if available_ports:
            print(f"   ✅ Serial ports available: {', '.join(available_ports)}")
            
            # Test opening the port
            try:
                ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
                print("   ✅ Can open /dev/ttyS0")
                ser.close()
            except Exception as e:
                print(f"   ⚠️ Cannot open /dev/ttyS0: {e}")
                warnings.append("Serial port permissions or configuration issue")
        else:
            print("   ❌ No serial ports found")
            errors.append("Enable serial port: sudo raspi-config")
            
    except ImportError:
        print("   ❌ pyserial not available")
        errors.append("Install pyserial: pip3 install pyserial")
    
    # Test 4: Check hardware controller
    print("\n4️⃣ Checking hardware controller...")
    try:
        from hardware import get_hardware_controller
        hardware = get_hardware_controller()
        print(f"   ✅ Hardware controller: {type(hardware).__name__}")
        
        # Test GPIO functions
        if hasattr(hardware, 'signal_ready_to_firmware'):
            hardware.signal_ready_to_firmware()
            print("   ✅ GPIO ready signal works")
        
        if hasattr(hardware, 'signal_busy_to_firmware'):
            hardware.signal_busy_to_firmware()
            print("   ✅ GPIO busy signal works")
            
    except Exception as e:
        print(f"   ❌ Hardware controller error: {e}")
        errors.append("Hardware controller setup failed")
    
    # Test 5: Check legacy integration
    print("\n5️⃣ Checking ACTJv20 legacy integration...")
    try:
        from actj_legacy_integration import get_legacy_integration
        legacy = get_legacy_integration()
        print("   ✅ Legacy integration loaded")
        
        # Test UART protocol
        from actj_uart_protocol import get_uart_protocol
        uart = get_uart_protocol()
        print("   ✅ UART protocol loaded")
        
    except Exception as e:
        print(f"   ❌ Legacy integration error: {e}")
        errors.append("Legacy integration failed")
    
    # Test 6: Check main application imports
    print("\n6️⃣ Checking main application...")
    try:
        from main import BatchScannerApp
        print("   ✅ Main application imports OK")
        
        # Check if we can create the app (basic test)
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        print("   ✅ Tkinter GUI available")
        root.destroy()
        
    except Exception as e:
        print(f"   ❌ Main application error: {e}")
        errors.append("Main application setup failed")
    
    # Test 7: Check settings configuration
    print("\n7️⃣ Checking settings configuration...")
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read('settings.ini')
        
        # Check legacy mode settings
        if config.getboolean('hardware', 'gpio_enabled', fallback=False):
            print("   ✅ GPIO enabled in settings")
        else:
            warnings.append("GPIO not enabled in settings.ini")
        
        if config.getboolean('hardware', 'jig_control', fallback=False):
            print("   ✅ Jig control enabled")
        else:
            warnings.append("Jig control not enabled in settings.ini")
            
    except Exception as e:
        print(f"   ⚠️ Settings check warning: {e}")
        warnings.append("Could not verify settings.ini")
    
    # Results
    print("\n" + "=" * 50)
    if not errors:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your Pi is ready for ACTJv20 operation")
        print()
        print("🚀 Next steps:")
        print("   1. Connect hardware:")
        print("      • GPIO 12 (Pi) → RB6/RASP_IN_PIC (ACTJv20)")
        print("      • UART: Pi TX/RX ↔ ACTJv20 RX/TX")
        print("   2. Run: python3 main.py")
        print("   3. Start your batch and press ACTJv20 START")
        print()
        return True
    else:
        print("❌ SETUP ISSUES FOUND")
        print()
        print("Errors to fix:")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
        
        if warnings:
            print("\nWarnings:")
            for i, warning in enumerate(warnings, 1):
                print(f"   {i}. {warning}")
        
        print()
        print("Fix these issues and run the test again.")
        return False

if __name__ == "__main__":
    success = test_actj_pi_setup()
    sys.exit(0 if success else 1)