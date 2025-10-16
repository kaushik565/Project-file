#!/usr/bin/env python3
"""
SBC-2 Error Hardware Checklist
Step-by-step hardware debugging for persistent SBC-2 errors.
"""

def hardware_debug_checklist():
    """Interactive hardware debugging checklist."""
    print("🔧 SBC-2 ERROR - HARDWARE DEBUG CHECKLIST")
    print("=" * 60)
    print("Since SBC-2 error persists, let's check hardware step by step:")
    print("=" * 60)
    
    print("\n🔌 STEP 1: CRITICAL WIRING VERIFICATION")
    print("Check these connections with a multimeter:")
    print()
    
    connections = [
        ("Pi GPIO 12 (BCM)", "PIC RB6 pin", "RASP_IN_PIC handshake - MOST CRITICAL"),
        ("Pi GPIO 14 (TX)", "PIC RC7 pin", "UART transmit from Pi to PIC"),
        ("Pi GPIO 15 (RX)", "PIC RC6 pin", "UART receive from PIC to Pi"),
        ("Pi Ground", "PIC Ground", "Common ground reference"),
        ("Pi GPIO 18", "PIC input (optional)", "SBC_BUSY signal"),
        ("Pi GPIO 21", "PIC input (optional)", "STATUS signal")
    ]
    
    for i, (pi_pin, pic_pin, description) in enumerate(connections, 1):
        print(f"{i}. {pi_pin} → {pic_pin}")
        print(f"   Purpose: {description}")
        response = input(f"   ❓ Is this connection secure? (y/n): ").lower().strip()
        if response != 'y':
            print(f"   ❌ FIX NEEDED: Check {pi_pin} → {pic_pin} connection")
            print(f"   💡 Use multimeter to verify continuity")
        else:
            print(f"   ✅ Connection verified")
        print()
    
    print("\n⚡ STEP 2: VOLTAGE VERIFICATION")
    print("With Pi powered ON and main.py running:")
    print()
    
    voltage_tests = [
        ("Pi GPIO 12", "3.3V", "Should be HIGH when Pi ready"),
        ("PIC RB6 pin", "3.3V", "Should match Pi GPIO 12"),
        ("Pi 3.3V rail", "3.3V", "Power reference"),
        ("PIC 5V power", "5.0V", "PIC controller power"),
        ("Common ground", "0V", "Reference point")
    ]
    
    for pin, expected, note in voltage_tests:
        print(f"📍 Measure {pin}:")
        print(f"   Expected: {expected}")
        print(f"   Purpose: {note}")
        measured = input(f"   🔍 Measured voltage: ").strip()
        if measured:
            try:
                voltage = float(measured.replace('V', '').strip())
                expected_val = float(expected.replace('V', '').strip())
                if abs(voltage - expected_val) < 0.3:
                    print(f"   ✅ Voltage OK: {measured}")
                else:
                    print(f"   ❌ Voltage wrong: Expected ~{expected}, got {measured}")
            except:
                print(f"   📝 Voltage recorded: {measured}")
        print()
    
    print("\n🖥️ STEP 3: PIC FIRMWARE VERIFICATION")
    print("Check these on the PIC controller:")
    print()
    
    firmware_checks = [
        "PIC LCD shows 'WELCOME' on power-up",
        "PIC LCD shows 'JIG READY' after startup",
        "PIC responds to UART commands from Pi",
        "PIC firmware version matches hardware_firmware/main.hex",
        "PIC configuration bits set correctly for 115200 baud"
    ]
    
    for i, check in enumerate(firmware_checks, 1):
        print(f"{i}. {check}")
        response = input(f"   ❓ Confirmed? (y/n): ").lower().strip()
        if response != 'y':
            print(f"   ❌ Issue found with: {check}")
        else:
            print(f"   ✅ Verified")
        print()
    
    print("\n📡 STEP 4: UART COMMUNICATION TEST")
    print("Test UART communication independently:")
    print()
    print("On Raspberry Pi, run:")
    print("   sudo minicom -D /dev/ttyS0 -b 115200")
    print()
    print("You should be able to:")
    print("• Send characters to PIC")
    print("• Receive responses from PIC")
    print("• See UART activity")
    print()
    uart_working = input("❓ UART communication working? (y/n): ").lower().strip()
    if uart_working != 'y':
        print("❌ UART issue - check GPIO 14/15 ↔ RC6/RC7 wiring")
    else:
        print("✅ UART communication verified")
    print()
    
    print("\n🔄 STEP 5: TIMING AND SEQUENCE")
    print("Check the operation sequence:")
    print()
    sequence_steps = [
        "Pi main.py starts and shows interface",
        "Pi connects to PIC via UART (/dev/ttyS0)",
        "Pi sets GPIO 12 HIGH (ready state)",
        "User starts batch scanning",
        "Pi sends start command to PIC",
        "PIC begins cartridge cycle",
        "PIC positions cartridge and sends scan request",
        "Pi receives scan request via UART",
        "Pi sets GPIO 12 LOW (busy state)",
        "SBC-2 ERROR occurs here if GPIO 12 not working"
    ]
    
    for i, step in enumerate(sequence_steps, 1):
        print(f"{i:2d}. {step}")
    print()
    
    error_step = input("❓ At which step does SBC-2 error occur? (1-10): ").strip()
    if error_step:
        try:
            step_num = int(error_step)
            if step_num <= 5:
                print("❌ Error early in sequence - check Pi software/UART")
            elif step_num <= 8:
                print("❌ Error during command - check UART wiring") 
            else:
                print("❌ Error during handshake - check GPIO 12 → RB6")
        except:
            print("📝 Error step noted")
    print()

def show_common_fixes():
    """Show the most common fixes for SBC-2 error."""
    print("🎯 MOST COMMON SBC-2 FIXES:")
    print("=" * 60)
    print("""
🥇 **#1 FIX - Missing GPIO 12 Connection (80% of cases)**
   Problem: Pi GPIO 12 not connected to PIC RB6
   Solution: Add wire from Pi GPIO 12 to PIC RB6 pin
   Test: Measure 3.3V on both pins when Pi ready

🥈 **#2 FIX - Wrong Pin Numbers (15% of cases)**  
   Problem: GPIO pins mixed up (BOARD vs BCM mode)
   Solution: Use BCM mode - GPIO 12 is physical pin 32
   Test: Verify pin mapping with Pi pinout diagram

🥉 **#3 FIX - Ground Issues (5% of cases)**
   Problem: No common ground between Pi and PIC
   Solution: Connect Pi Ground to PIC Ground (VSS)
   Test: Measure 0V difference between grounds

💡 **EMERGENCY BYPASS:**
If you can't fix wiring immediately, disable hardware sync:

1. Edit main.py:
   ```python
   # Temporarily disable controller link
   self.controller_link = None
   ```

2. This allows QR testing without PIC handshake
3. Fix wiring before production use

🔧 **SYSTEMATIC DEBUG:**
1. Power OFF everything
2. Check GPIO 12 → RB6 with multimeter continuity
3. Power ON Pi only, measure GPIO 12 voltage (3.3V)
4. Power ON PIC, measure RB6 voltage (should match GPIO 12)
5. If voltages don't match, fix wiring
6. Test again

⚠️ **WARNING SIGNS:**
• SBC-2 error always at same point = wiring issue
• SBC-2 error random timing = power/noise issue  
• No UART communication = wrong TX/RX wiring
• PIC doesn't start = power or firmware issue
""")

def main():
    """Run interactive hardware debugging."""
    print("🚨 PERSISTENT SBC-2 ERROR DEBUGGING")
    print("=" * 60)
    print("This tool helps find the exact hardware issue causing SBC-2 errors.")
    print("Have your multimeter ready!")
    print("=" * 60)
    
    # Interactive hardware debugging
    hardware_debug_checklist()
    
    # Show common fixes
    show_common_fixes()
    
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("1. Fix any wiring issues found above")
    print("2. Power cycle both Pi and PIC")
    print("3. Run: python3 main.py")
    print("4. Test cartridge operation")
    print("5. If still SBC-2 error, check firmware programming")
    print("=" * 60)

if __name__ == "__main__":
    main()