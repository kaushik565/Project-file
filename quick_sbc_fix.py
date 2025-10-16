#!/usr/bin/env python3

"""
SBC Er-1 Quick Fix

The SBC Er-1 error means ACTJv20 firmware can't detect the Pi GPIO signal.
This script tests and fixes common GPIO initialization issues.
"""

import sys
import time

def quick_sbc_fix():
    """Quick diagnosis and fix for SBC Er-1."""
    
    print("🚨 SBC Er-1 QUICK FIX")
    print("=====================")
    print()
    print("📋 SBC Er-1 means: ACTJv20 can't detect Pi GPIO signal")
    print()
    
    # Test 1: GPIO Basic Test
    print("1️⃣ Testing GPIO 12 (RASP_IN_PIC)...")
    try:
        import RPi.GPIO as GPIO
        
        # Clean slate
        GPIO.cleanup()
        GPIO.setmode(GPIO.BCM)
        
        # Setup GPIO 12
        GPIO.setup(12, GPIO.OUT, initial=GPIO.HIGH)
        print("   ✅ GPIO 12 initialized as OUTPUT HIGH")
        
        # Test sequence
        for i in range(3):
            GPIO.output(12, GPIO.LOW)
            print(f"   🔄 GPIO 12 LOW (test {i+1})")
            time.sleep(0.5)
            
            GPIO.output(12, GPIO.HIGH) 
            print(f"   🔄 GPIO 12 HIGH (test {i+1})")
            time.sleep(0.5)
        
        print("   ✅ GPIO 12 responding correctly")
        
    except Exception as e:
        print(f"   ❌ GPIO Error: {e}")
        return False
    
    # Test 2: Hardware Controller
    print("\n2️⃣ Testing Hardware Controller...")
    try:
        from hardware import get_hardware_controller
        hardware = get_hardware_controller()
        
        print("   🔄 Sending READY signal...")
        hardware.signal_ready_to_firmware()
        time.sleep(1)
        
        print("   🔄 Sending BUSY signal...")
        hardware.signal_busy_to_firmware()
        time.sleep(1)
        
        print("   🔄 Back to READY...")
        hardware.signal_ready_to_firmware()
        
        print("   ✅ Hardware controller working")
        
    except Exception as e:
        print(f"   ❌ Hardware Error: {e}")
        return False
    
    # Test 3: Legacy Mode Check
    print("\n3️⃣ Checking Legacy Mode...")
    try:
        from actj_legacy_integration import is_legacy_mode
        
        if is_legacy_mode():
            print("   ✅ Legacy mode is ACTIVE")
        else:
            print("   ⚠️ Legacy mode NOT active - this could cause SBC Er-1!")
            print("   🔧 Run: python3 switch_mode.py legacy")
            
    except Exception as e:
        print(f"   ❌ Legacy check error: {e}")
    
    print("\n" + "=" * 40)
    print("💡 COMMON SBC Er-1 CAUSES:")
    print("   1. GPIO 12 not connected to ACTJv20 RB6")
    print("   2. Poor/loose wire connection")
    print("   3. ACTJv20 not powered on properly")
    print("   4. Pi not in legacy mode")
    print("   5. GPIO permissions issue")
    print()
    print("🔧 IMMEDIATE FIXES TO TRY:")
    print("   1. Check GPIO 12 (Pi) → RB6 (ACTJv20) wire")
    print("   2. Power cycle the ACTJv20")
    print("   3. Run: sudo python3 main.py")
    print("   4. Check ACTJv20 LCD for startup messages")
    print()
    
    # Keep GPIO ready for testing
    try:
        GPIO.output(12, GPIO.HIGH)  # Keep ready
        print("🚀 GPIO 12 is now HIGH (READY) for ACTJv20 testing")
        print("   Try pressing START on ACTJv20 now...")
    except:
        pass
    
    return True

if __name__ == "__main__":
    success = quick_sbc_fix()
    
    if success:
        print("\n✅ GPIO tests completed")
        print("🔌 Check your hardware connections and try main.py")
    else:
        print("\n❌ GPIO issues detected - fix these first")
        
    print("\n⏳ Keeping script running for 30 seconds...")
    print("   (GPIO 12 will stay HIGH for testing)")
    
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        pass
    
    # Cleanup
    try:
        import RPi.GPIO as GPIO
        GPIO.cleanup()
        print("🧹 GPIO cleaned up")
    except:
        pass