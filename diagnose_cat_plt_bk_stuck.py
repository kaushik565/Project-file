#!/usr/bin/env python3
"""
CAT PLT BK STUCK - Hardware Diagnostic Tool
Helps diagnose cartridge plate backward movement issues.
"""

import time
import logging
from hardware import get_hardware_controller

def test_sensors():
    """Test sensor readings that affect CAT PLT BK STUCK error."""
    print("🔍 SENSOR DIAGNOSTIC TEST")
    print("=" * 50)
    
    try:
        hardware = get_hardware_controller()
        print("✅ Hardware controller initialized")
    except Exception as e:
        print(f"❌ Hardware controller failed: {e}")
        print("🔧 This test requires actual hardware (Raspberry Pi with GPIO)")
        return False
    
    # Test pin reading (simulated for development systems)
    sensor_pins = {
        'BW_SNS (RC0)': 'Backward sensor - should be HIGH when plate at back',
        'FW_SNS (RC1)': 'Forward sensor - should be HIGH when plate at front', 
        'MECH_UP_SNS (RC2)': 'Mech plate up sensor',
        'STACK_SNS (RC4)': 'Stack sensor - cartridge present',
        'RJT_SNS (RE2)': 'Rejection sensor - diverter position'
    }
    
    print("\n📡 SENSOR STATUS:")
    for pin_name, description in sensor_pins.items():
        print(f"  {pin_name}: {description}")
        # Note: Actual GPIO reading would happen here on real hardware
    
    print("\n⚡ ACTUATOR TEST:")
    actuator_pins = {
        'PLATE_UD (RA2)': 'Plate up/down (0=up/back, 1=down/forward)',
        'CAT_FB (RE0)': 'Cartridge forward/back position',
        'REJECT_SV (RA4)': 'Rejection solenoid valve'
    }
    
    for pin_name, description in actuator_pins.items():
        print(f"  {pin_name}: {description}")
    
    return True

def diagnose_cat_plt_bk_stuck():
    """Provide specific guidance for CAT PLT BK STUCK error."""
    print("\n🚨 CAT PLT BK STUCK ERROR DIAGNOSIS")
    print("=" * 50)
    
    print("""
📋 WHAT THIS ERROR MEANS:
   • Cartridge plate cannot move to backward position
   • BW_SNS sensor (RC0) not detecting plate at back position  
   • 10-second timeout exceeded waiting for sensor signal
   
🔧 IMMEDIATE ACTIONS:
   1. Press START button on jig to reset error
   2. Remove any cartridges from stack
   3. Check for physical obstructions
   
⚠️ COMMON CAUSES:
   • Mechanical jam or binding in plate mechanism
   • BW_SNS sensor misaligned or failed
   • PLATE_UD actuator not working (RA2)
   • Low air pressure (pneumatic systems)
   • Debris blocking plate movement
   
🔍 DIAGNOSTIC STEPS:
   1. POWER OFF and manually check plate movement
   2. Verify BW_SNS sensor alignment and wiring
   3. Test PLATE_UD actuator operation
   4. Check for loose connections on RC0 (BW_SNS)
   5. Verify 5V power supply to sensors
   
💡 SENSOR TRIGGER TEST:
   • BW_SNS should be LOW (0V) when nothing detected
   • BW_SNS should be HIGH (5V) when plate at back position
   • Use multimeter to test voltage on RC0 pin
   
🔌 WIRING CHECK:
   • RC0 (BW_SNS) - Backward sensor input
   • RA2 (PLATE_UD) - Plate actuator output  
   • RE0 (CAT_FB) - Cartridge position output
   
⏱️ TIMING INFO:
   • Normal plate movement: 2-5 seconds
   • Timeout setting: 10 seconds (10000ms)
   • If movement is very slow, check for mechanical friction
""")

def show_error_recovery():
    """Show how to recover from the error state."""
    print("\n🔄 ERROR RECOVERY PROCEDURE")
    print("=" * 50)
    
    print("""
STEP 1: IMMEDIATE RESET
   → Press START button on jig control panel
   → This runs error_loop() recovery function
   → System will attempt automatic recovery
   
STEP 2: IF ERROR PERSISTS
   → POWER OFF the jig completely
   → Wait 10 seconds
   → Check for physical obstructions
   → Remove cartridges from stack
   → POWER ON and try again
   
STEP 3: MANUAL TESTING
   → With power OFF, manually move plate mechanism
   → Should move smoothly without binding
   → Check sensor triggers manually
   → Look for damaged cables or loose connections
   
STEP 4: FIRMWARE RESET
   → If USB/UART connection available:
   → Send 'R' command to reset PIC controller
   → Check Pi ↔ PIC communication status
   
STEP 5: HARDWARE MAINTENANCE
   → If error continues, likely hardware issue
   → Contact maintenance for sensor/actuator check
   → May need mechanical adjustment or part replacement
""")

def main():
    """Run complete diagnostic for CAT PLT BK STUCK error."""
    print("🛠️ CAT PLT BK STUCK - DIAGNOSTIC TOOL")
    print("=" * 60)
    print("This tool helps diagnose cartridge plate movement issues.")
    print("=" * 60)
    
    # Run hardware tests
    test_sensors()
    
    # Show specific diagnosis
    diagnose_cat_plt_bk_stuck()
    
    # Show recovery steps
    show_error_recovery()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("1. Press START button first (quickest fix)")
    print("2. Check physical obstructions (power OFF)")
    print("3. Test BW_SNS sensor (RC0) and PLATE_UD actuator (RA2)")
    print("4. If error persists, likely hardware maintenance needed")
    print("=" * 60)

if __name__ == "__main__":
    main()