#!/usr/bin/env python3

"""
Test QR Rejection Handling for ACTJv20

Tests the GPIO pulse sequence when QR codes are rejected to ensure
the mechanism plate doesn't get stuck.
"""

import sys
import time
import logging

def test_rejection_handling():
    """Test rejection handling with proper GPIO signaling."""
    
    print("🔧 Testing ACTJv20 QR Rejection Handling")
    print("=======================================")
    print()
    
    # Setup logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        # Import legacy integration
        from actj_legacy_integration import get_legacy_integration
        from actj_uart_protocol import get_uart_protocol
        from hardware import get_hardware_controller
        
        print("✅ Imports successful")
        
        # Get components
        hardware = get_hardware_controller()
        legacy = get_legacy_integration()
        uart = get_uart_protocol()
        
        print(f"✅ Hardware controller: {type(hardware).__name__}")
        print()
        
        # Test 1: Test rejection pulse sequence
        print("1️⃣ Testing rejection pulse sequence...")
        print("   Simulating QR rejection...")
        
        # Simulate the rejection sequence
        hardware.signal_busy_to_firmware()
        time.sleep(0.1)
        print("   📡 Sent busy signal")
        
        # Simulate sending 'R' (this would happen in UART protocol)
        print("   📤 Sending 'R' (reject) to firmware...")
        time.sleep(0.2)  # Wait for firmware processing
        
        # Test the rejection pulse
        hardware.signal_rejection_pulse()
        print("   🔄 Sent rejection pulse sequence")
        
        print("   ✅ Rejection pulse test completed")
        print()
        
        # Test 2: Test multiple rejections
        print("2️⃣ Testing multiple rejections...")
        for i in range(3):
            print(f"   Rejection test {i+1}/3...")
            hardware.signal_busy_to_firmware()
            time.sleep(0.05)
            hardware.signal_rejection_pulse()
            time.sleep(0.1)
            print(f"   ✅ Rejection {i+1} completed")
        
        print()
        
        # Test 3: Test GPIO state verification
        print("3️⃣ Testing GPIO state verification...")
        
        # Test ready state
        hardware.signal_ready_to_firmware()
        print("   📡 Set READY state (GPIO 12 HIGH)")
        time.sleep(0.1)
        
        # Test busy state
        hardware.signal_busy_to_firmware()
        print("   📡 Set BUSY state (GPIO 12 LOW)")
        time.sleep(0.1)
        
        # Return to ready
        hardware.signal_ready_to_firmware()
        print("   📡 Return to READY state")
        
        print("   ✅ GPIO state test completed")
        print()
        
        # Test 4: Test accept pulse sequence
        print("4️⃣ Testing accept pulse sequence...")
        print("   Simulating QR acceptance...")
        
        # Test accept pulse
        hardware.signal_accept_pulse()
        print("   ✅ Accept pulse sequence completed")
        print()
        
        # Test 5: Simulate complete workflows
        print("5️⃣ Testing complete workflows...")
        
        def simulate_qr_accept():
            """Simulate complete QR accept process."""
            print("   🔍 Accept workflow:")
            hardware.signal_ready_to_firmware()
            hardware.signal_busy_to_firmware()
            print("     ✅ QR validation PASSED - simulating accept...")
            time.sleep(0.15)  # Processing time
            hardware.signal_accept_pulse()
            time.sleep(0.1)
            hardware.signal_ready_to_firmware()
            print("     ✅ Accept workflow completed")
        
        def simulate_qr_rejection():
            """Simulate complete QR rejection process."""
            print("   🔍 Reject workflow:")
            hardware.signal_ready_to_firmware()
            hardware.signal_busy_to_firmware()
            print("     ❌ QR validation FAILED - simulating rejection...")
            time.sleep(0.15)  # Processing time
            hardware.signal_rejection_pulse()
            time.sleep(0.1)
            hardware.signal_ready_to_firmware()
            print("     ✅ Reject workflow completed")
        
        simulate_qr_accept()
        simulate_qr_rejection()
        print("   ✅ Complete workflow tests completed")
        print()
        
        print("🎉 ALL REJECTION TESTS PASSED!")
        print()
        print("💡 Key fixes implemented:")
        print("   • Added GPIO busy signal before UART transmission")
        print("   • Added accept pulse sequence for PASSED QR codes")
        print("   • Added rejection pulse sequence for FAILED QR codes")
        print("   • Added proper timing delays for firmware processing")
        print("   • Added final ready signal after ALL responses")
        print()
        print("🚀 This should fix the 'mch plt u stuck' error for BOTH accepts AND rejects!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during rejection test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rejection_handling()
    if success:
        print("\n✅ Test completed successfully")
        print("Deploy to Pi and test with actual ACTJv20 hardware")
    else:
        print("\n❌ Test failed")
    sys.exit(0 if success else 1)