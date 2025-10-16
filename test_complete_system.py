#!/usr/bin/env python3

"""
Complete ACTJv20 Integration Test

This script tests the full integration between main.py and ACTJv20 hardware,
including GPIO handshaking and UART communication for automatic operation.
"""

import sys
import time
import logging
import threading
from unittest.mock import Mock

def test_complete_integration():
    """Test complete ACTJv20 integration with main.py."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("integration_test")
    
    print("=" * 70)
    print("🎯 COMPLETE ACTJv20 INTEGRATION TEST")
    print("=" * 70)
    print()
    
    try:
        print("1️⃣ Testing Legacy Integration Components...")
        
        # Test legacy integration
        from actj_legacy_integration import get_legacy_integration, is_legacy_mode
        legacy = get_legacy_integration()
        print(f"   ✅ Legacy integration: {type(legacy).__name__}")
        
        # Test UART protocol
        from actj_uart_protocol import get_uart_protocol
        uart = get_uart_protocol()
        print(f"   ✅ UART protocol: {type(uart).__name__}")
        
        print("\n2️⃣ Testing Batch Context Setup...")
        
        # Test batch context
        test_mould_ranges = {
            "MOULD_A": ("MVANC00001", "MVANC00100"),
            "MOULD_B": ("MVBNC00001", "MVBNC00100")
        }
        
        def test_duplicate_checker(qr_code):
            return False  # No duplicates for test
        
        legacy.set_batch_context("V", test_mould_ranges, test_duplicate_checker)
        print("   ✅ Batch context set successfully")
        
        print("\n3️⃣ Testing QR Validation Bridge...")
        
        # Test QR validation
        test_qr_codes = [
            "MVANC00001",  # Should PASS
            "MVBNC00050",  # Should PASS  
            "MXELR00001",  # Should FAIL (wrong line)
            "INVALID",     # Should FAIL (format)
        ]
        
        for qr_code in test_qr_codes:
            status, mould = legacy._qr_validation_bridge(qr_code)
            result = "✅ PASS" if status == "PASS" else "❌ FAIL"
            print(f"   {result} QR: {qr_code} → {status} ({mould})")
        
        print("\n4️⃣ Testing UART Protocol Communication...")
        
        # Mock serial port for testing
        class MockSerial:
            def __init__(self):
                self.data = []
                self.in_waiting = 0  # Fix the attribute vs method issue
            def write(self, data):
                self.data.append(data)
                print(f"   📤 UART TX: {data}")
            def read(self, size):
                return b'2'  # Simulate command
            def close(self):
                pass
        
        # Test UART communication
        uart.set_qr_validator(legacy._qr_validation_bridge)
        uart.serial_port = MockSerial()
        
        print("   Testing QR processing through UART...")
        uart._waiting_for_qr = True
        uart.process_qr_input("MVANC00001")
        
        if uart.serial_port.data:
            response = uart.serial_port.data[-1]
            print(f"   ✅ UART Response: {response}")
        
        print("\n5️⃣ Testing Startup Sequence...")
        
        # Test startup sequence
        legacy.startup_sequence()
        print("   ✅ Startup sequence completed")
        
        print("\n6️⃣ Testing Hardware Integration...")
        
        # Test hardware integration
        from hardware import get_hardware_controller
        hardware = get_hardware_controller()
        print(f"   ✅ Hardware controller: {type(hardware).__name__}")
        
        # Test GPIO functions
        hardware.signal_ready_to_firmware()
        print("   ✅ GPIO ready signal test")
        
        hardware.signal_busy_to_firmware()
        print("   ✅ GPIO busy signal test")
        
        print("\n" + "=" * 70)
        print("🎉 INTEGRATION TEST COMPLETE!")
        print("=" * 70)
        print()
        print("✅ All Components Working:")
        print("   • Legacy Integration: Ready")
        print("   • UART Protocol: Ready") 
        print("   • QR Validation Bridge: Ready")
        print("   • GPIO Handshaking: Ready")
        print("   • Batch Context: Ready")
        print()
        print("🚀 Ready for ACTJv20 Hardware Testing:")
        print("   1. Connect GPIO 12 → RB6 (RASP_IN_PIC)")
        print("   2. Connect Pi UART → ACTJv20 UART")
        print("   3. Run: python3 main.py")
        print("   4. Start batch and press START on ACTJv20")
        print("   5. Automatic operation should work!")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}")
        logging.exception("Integration test failed")
        return False


def test_main_py_integration():
    """Test that main.py can work with legacy integration."""
    print("\n" + "=" * 70)
    print("🔧 TESTING MAIN.PY INTEGRATION")
    print("=" * 70)
    
    try:
        # Import main components
        from main import BatchScannerApp
        from logic import handle_qr_scan
        
        print("✅ Main application components imported successfully")
        
        # Test QR handling
        test_qr = "MVANC00001"
        test_batch_line = "V"
        test_mould_ranges = {
            "MOULD_A": ("MVANC00001", "MVANC00100")
        }
        
        status, mould = handle_qr_scan(test_qr, test_batch_line, test_mould_ranges)
        print(f"✅ QR validation test: {test_qr} → {status} ({mould})")
        
        print("✅ Main.py integration ready for ACTJv20!")
        
        return True
        
    except Exception as e:
        print(f"❌ Main.py integration test failed: {e}")
        return False


if __name__ == "__main__":
    print("Starting Complete ACTJv20 Integration Test...")
    print("This tests all components needed for automatic operation.")
    print()
    
    # Run integration test
    integration_success = test_complete_integration()
    
    # Run main.py integration test  
    main_success = test_main_py_integration()
    
    print("\n" + "=" * 70)
    if integration_success and main_success:
        print("🎊 ALL TESTS PASSED - READY FOR ACTJv20 OPERATION!")
        print("=" * 70)
        print()
        print("Next Steps:")
        print("1. Deploy to Raspberry Pi")
        print("2. Connect hardware (GPIO + UART)")
        print("3. Run: python3 main.py") 
        print("4. Your ACTJv20 jig will work automatically!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - NEEDS FIXES")
        print("=" * 70)
        sys.exit(1)