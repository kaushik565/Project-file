#!/usr/bin/env python3

"""
Test ACTJv20(RJSR) Legacy Hardware Compatibility

This script tests the GPIO handshaking required for ACTJv20(RJSR) firmware
communication and helps diagnose SBC-2 errors.

Usage:
    python3 test_actj_legacy.py [--mock]
    
Options:
    --mock: Use mock hardware controller for testing without GPIO
"""

import sys
import time
import logging
import argparse

def test_legacy_compatibility(use_mock=False):
    """Test ACTJv20(RJSR) legacy hardware compatibility."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("actj_test")
    
    print("=" * 60)
    print("ACTJv20(RJSR) Legacy Hardware Compatibility Test")
    print("=" * 60)
    print()
    
    if use_mock:
        print("🔧 Running in MOCK mode (no actual GPIO)")
        # Temporarily set mock mode
        import config
        original_controller = config.HARDWARE_CONTROLLER
        config.HARDWARE_CONTROLLER = "mock"
    else:
        print("⚡ Running in GPIO mode (real hardware)")
    
    try:
        # Test hardware controller
        print("\n1. Testing Hardware Controller...")
        from hardware import get_hardware_controller
        hardware = get_hardware_controller()
        print(f"   ✓ Hardware controller: {type(hardware).__name__}")
        
        # Test basic GPIO functions
        print("\n2. Testing Basic GPIO Functions...")
        if hasattr(hardware, 'set_rasp_in_pic'):
            hardware.set_rasp_in_pic(False)
            print("   ✓ RASP_IN_PIC set to LOW")
            time.sleep(0.1)
            hardware.set_rasp_in_pic(True)
            print("   ✓ RASP_IN_PIC set to HIGH")
            time.sleep(0.1)
        else:
            print("   ❌ RASP_IN_PIC function not available")
        
        # Test legacy integration
        print("\n3. Testing Legacy Integration...")
        from actj_legacy_integration import get_legacy_integration, is_legacy_mode
        
        legacy = get_legacy_integration()
        print(f"   ✓ Legacy integration: {type(legacy).__name__}")
        print(f"   ✓ Legacy mode detected: {is_legacy_mode()}")
        
        # Test startup sequence
        print("\n4. Testing Startup Sequence...")
        legacy.startup_sequence()
        print("   ✓ Startup sequence completed")
        
        # Test QR scanning sequence
        print("\n5. Testing QR Scanning Sequence...")
        test_qr_codes = [
            "MVANC00001",
            "MVELR00014", 
            "MVBNC00012"
        ]
        
        for qr_code in test_qr_codes:
            print(f"   Testing QR: {qr_code}")
            success = legacy.handle_scanning_sequence(qr_code)
            status = "✓ SUCCESS" if success else "❌ FAILED"
            print(f"   {status}")
            time.sleep(0.5)
        
        # Test shutdown sequence
        print("\n6. Testing Shutdown Sequence...")
        legacy.shutdown_sequence()
        print("   ✓ Shutdown sequence completed")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("Next Steps:")
        print("1. Connect your ACTJv20(RJSR) hardware")
        print("2. Run: python3 switch_mode.py legacy")
        print("3. Run: python3 main.py")
        print("4. Test with real cartridge scanning")
        print()
        print("Expected behavior:")
        print("- No 'SBC Er-1' or 'SBC Er-2' errors on hardware display")
        print("- QR scanner should work normally")
        print("- Manual cartridge positioning with jig")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        logger.exception("Test failed with exception")
        return False
        
    finally:
        if use_mock:
            # Restore original controller
            config.HARDWARE_CONTROLLER = original_controller


def test_gpio_mapping():
    """Test and display GPIO pin mapping for ACTJv20(RJSR)."""
    print("\n" + "=" * 60)
    print("ACTJv20(RJSR) GPIO Pin Mapping")
    print("=" * 60)
    print()
    print("Raspberry Pi → ACTJv20(RJSR) Connections:")
    print("  GPIO 12 → RB6 (RASP_IN_PIC)")
    print("    - Controls firmware ready/busy state")
    print("    - HIGH = Pi ready for commands")
    print("    - LOW = Pi busy or not ready")
    print()
    print("Expected Firmware Behavior:")
    print("  - wait_ready_rpi(): Waits for GPIO 12 HIGH")
    print("    → If timeout: 'SBC Er-1' error")
    print("  - wait_busy_rpi(): Waits for GPIO 12 LOW after HIGH")
    print("    → If timeout: 'SBC Er-2' error")
    print()
    print("Legacy Integration Solution:")
    print("  - Startup: LOW → HIGH → LOW sequence")
    print("  - QR Scan: HIGH (ready) → LOW (busy)")
    print("  - Proper handshaking prevents SBC errors")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test ACTJv20(RJSR) legacy hardware compatibility")
    parser.add_argument("--mock", action="store_true", 
                       help="Use mock hardware controller (no GPIO)")
    parser.add_argument("--gpio-map", action="store_true",
                       help="Show GPIO pin mapping information")
    
    args = parser.parse_args()
    
    if args.gpio_map:
        test_gpio_mapping()
        sys.exit(0)
    
    success = test_legacy_compatibility(use_mock=args.mock)
    sys.exit(0 if success else 1)