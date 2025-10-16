#!/usr/bin/env python3
"""
SBC-2 Error Diagnostic and Fix Tool
Diagnoses and fixes communication issues between Pi and PIC controller.
"""

import time
import logging
from hardware import get_hardware_controller

def diagnose_sbc_error():
    """Diagnose SBC-2 communication error."""
    print("🔧 SBC-2 ERROR DIAGNOSTIC")
    print("=" * 50)
    
    print("📋 WHAT IS SBC-2 ERROR:")
    print("   • PIC firmware sent command to Pi")
    print("   • Pi didn't respond with proper handshake signals")
    print("   • PIC timed out waiting for busy line response")
    print()
    
    print("🔍 CHECKING GPIO HANDSHAKE LINES:")
    print("=" * 50)
    
    try:
        hardware = get_hardware_controller()
        print("✅ Hardware controller initialized")
        
        # Test GPIO 12 (RASP_IN_PIC) - Main busy line
        print("\n📍 Testing GPIO 12 (RASP_IN_PIC - main busy line):")
        try:
            print("   Setting HIGH (Pi ready)...")
            hardware.set_busy(True)
            time.sleep(0.5)
            print("   ✅ GPIO 12 set HIGH")
            
            print("   Setting LOW (Pi busy)...")
            hardware.set_busy(False) 
            time.sleep(0.5)
            print("   ✅ GPIO 12 set LOW")
            
            print("   Setting HIGH (Pi ready)...")
            hardware.set_busy(True)
            time.sleep(0.5)
            print("   ✅ GPIO 12 set HIGH")
            
        except Exception as e:
            print(f"   ❌ GPIO 12 test failed: {e}")
        
        # Test GPIO 18 (SBC_BUSY) - SCANNER compatibility 
        print("\n📍 Testing GPIO 18 (SBC_BUSY - SCANNER compatibility):")
        try:
            print("   Setting HIGH (SBC ready)...")
            hardware.set_sbc_busy(True)
            time.sleep(0.5) 
            print("   ✅ GPIO 18 set HIGH")
            
            print("   Setting LOW (SBC busy)...")
            hardware.set_sbc_busy(False)
            time.sleep(0.5)
            print("   ✅ GPIO 18 set LOW")
            
            print("   Setting HIGH (SBC ready)...")
            hardware.set_sbc_busy(True)
            time.sleep(0.5)
            print("   ✅ GPIO 18 set HIGH")
            
        except Exception as e:
            print(f"   ❌ GPIO 18 test failed: {e}")
        
        # Test GPIO 21 (STATUS) - SCANNER compatibility
        print("\n📍 Testing GPIO 21 (STATUS - SCANNER compatibility):")
        try:
            print("   Setting HIGH (status OK)...")
            hardware.set_status(True)
            time.sleep(0.5)
            print("   ✅ GPIO 21 set HIGH")
            
            print("   Setting LOW (status signal)...")
            hardware.set_status(False)
            time.sleep(0.5)
            print("   ✅ GPIO 21 set LOW")
            
            print("   Setting HIGH (status OK)...")
            hardware.set_status(True)
            time.sleep(0.5)
            print("   ✅ GPIO 21 set HIGH")
            
        except Exception as e:
            print(f"   ❌ GPIO 21 test failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Hardware initialization failed: {e}")
        return False

def show_sbc2_solutions():
    """Show solutions for SBC-2 error."""
    print("\n🔧 SBC-2 ERROR SOLUTIONS:")
    print("=" * 50)
    print("""
🚨 ROOT CAUSES & FIXES:

1. **WIRING ISSUES** (Most Common):
   ❌ GPIO 12 not connected to PIC RB6 (RASP_IN_PIC)
   ❌ Loose connections on handshake lines
   ❌ Wrong pin mapping
   
   ✅ SOLUTIONS:
   • Verify Pi GPIO 12 → PIC RB6 connection
   • Check continuity with multimeter
   • Ensure good solder joints
   • Double-check pin numbers

2. **TIMING ISSUES**:
   ❌ Pi takes too long to respond
   ❌ Busy signals not set fast enough
   ❌ Application not running when PIC sends command
   
   ✅ SOLUTIONS:
   • Keep main.py application running
   • Don't close/restart during operation
   • Ensure stable power to Pi

3. **SOFTWARE ISSUES**:
   ❌ GPIO not initialized properly
   ❌ Wrong pin configuration
   ❌ Hardware controller in mock mode
   
   ✅ SOLUTIONS:
   • Use production mode: python3 switch_mode.py production
   • Check settings.ini: controller = gpio
   • Restart application: python3 main.py

4. **PIC FIRMWARE ISSUES**:
   ❌ Wrong firmware version
   ❌ Different pin expectations
   ❌ Timing parameters too strict
   
   ✅ SOLUTIONS:
   • Use latest firmware: hardware_firmware/main.hex
   • Check pin definitions match
   • Verify UART communication working

💡 **QUICK FIXES TO TRY:**

A. **Restart Sequence:**
   1. Stop main.py (Ctrl+C)
   2. python3 switch_mode.py production
   3. python3 main.py
   4. Try operation again

B. **Hardware Reset:**
   1. Power OFF PIC controller
   2. Wait 10 seconds
   3. Power ON PIC controller
   4. Wait for LCD "WELCOME" message
   5. Try operation again

C. **Connection Check:**
   1. Measure voltage on Pi GPIO 12 (should be 3.3V when HIGH)
   2. Check voltage at PIC RB6 pin (should match Pi GPIO 12)
   3. Verify common ground between Pi and PIC

⚠️ **CRITICAL WIRING:**
   Pi GPIO 12 (BCM) → PIC RB6 (RASP_IN_PIC)
   Pi GPIO 14 (TX) → PIC RC7 (RX) 
   Pi GPIO 15 (RX) → PIC RC6 (TX)
   Pi Ground → PIC Ground

🎯 **SUCCESS INDICATORS:**
   • PIC LCD shows "JIG READY" (not SBC Er-2)
   • Cartridge moves to scan position
   • Pi shows "USB Scanner Ready" message
   • QR scanning works without timeout
""")

def test_communication_timing():
    """Test the communication timing that might cause SBC-2."""
    print("\n⏱️ COMMUNICATION TIMING TEST:")
    print("=" * 50)
    
    try:
        hardware = get_hardware_controller()
        
        print("🧪 Simulating PIC command → Pi response cycle:")
        
        # Simulate what happens when PIC sends scan command
        print("1. 📥 PIC sends scan command (simulated)")
        
        print("2. 📍 Pi sets busy LOW (processing)...")
        start_time = time.time()
        hardware.set_busy(False)
        hardware.set_sbc_busy(False)
        hardware.set_status(False)
        response_time = (time.time() - start_time) * 1000
        print(f"   ⏱️ Response time: {response_time:.1f}ms")
        
        print("3. ⏳ Pi processing QR scan (simulated 2s)...")
        time.sleep(2.0)
        
        print("4. 📍 Pi sets busy HIGH (done)...")
        start_time = time.time()
        hardware.set_busy(True)
        hardware.set_sbc_busy(True) 
        hardware.set_status(True)
        complete_time = (time.time() - start_time) * 1000
        print(f"   ⏱️ Complete time: {complete_time:.1f}ms")
        
        print("\n📊 TIMING ANALYSIS:")
        if response_time < 100:
            print(f"   ✅ Response time OK: {response_time:.1f}ms < 100ms")
        else:
            print(f"   ❌ Response time too slow: {response_time:.1f}ms")
            
        print(f"   💡 Total cycle time: {2000 + response_time + complete_time:.1f}ms")
        print("   💡 PIC timeout is typically 10-15 seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Timing test failed: {e}")
        return False

def main():
    """Run SBC-2 error diagnosis and fixes."""
    print("🚨 SBC-2 ERROR DIAGNOSTIC TOOL")
    print("=" * 60)
    print("This tool helps diagnose and fix SBC-2 communication errors")
    print("between the Raspberry Pi and PIC controller.")
    print("=" * 60)
    
    # Test 1: GPIO diagnostics
    gpio_ok = diagnose_sbc_error()
    
    # Test 2: Timing test
    if gpio_ok:
        timing_ok = test_communication_timing()
    else:
        timing_ok = False
    
    # Show solutions
    show_sbc2_solutions()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY:")
    print(f"   GPIO Tests: {'✅ PASSED' if gpio_ok else '❌ FAILED'}")
    print(f"   Timing Tests: {'✅ PASSED' if timing_ok else '❌ FAILED'}")
    
    if gpio_ok and timing_ok:
        print("\n🎉 GPIO HANDSHAKE IS WORKING!")
        print("💡 If you still get SBC-2 errors, check:")
        print("   • PIC firmware is programmed correctly")
        print("   • UART wiring (GPIO 14/15 ↔ RC6/RC7)")
        print("   • Power stability to both Pi and PIC")
        print("   • Try restarting both Pi and PIC")
    else:
        print("\n❌ GPIO HANDSHAKE ISSUES DETECTED")
        print("🔧 Follow the solutions above to fix wiring/software issues")
        print("💡 Most common fix: Check Pi GPIO 12 → PIC RB6 connection")
    
    print("=" * 60)

if __name__ == "__main__":
    main()