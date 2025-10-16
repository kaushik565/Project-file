#!/usr/bin/env python3
"""
USB Scanner Test for Raspberry Pi
Comprehensive testing for USB QR scanners on Linux/Raspberry Pi.
"""

import os
import sys
import time
import subprocess
import threading
from datetime import datetime

class PiUSBScannerTest:
    def __init__(self):
        self.scanned_codes = []
        self.testing = False
        
    def check_usb_devices(self):
        """Check USB devices connected to Pi."""
        print("🔌 USB DEVICE DETECTION")
        print("=" * 50)
        
        try:
            # List USB devices
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            if result.returncode == 0:
                print("📱 Connected USB devices:")
                devices = result.stdout.strip().split('\n')
                scanner_found = False
                
                for device in devices:
                    print(f"   {device}")
                    # Look for common scanner keywords
                    device_lower = device.lower()
                    if any(keyword in device_lower for keyword in ['scanner', 'barcode', 'symbol', 'honeywell', 'zebra', 'datalogic']):
                        print("   ⭐ ^ This might be your scanner!")
                        scanner_found = True
                
                if not scanner_found:
                    print("   💡 Scanner might be detected as generic HID device")
                
                return True
            else:
                print("❌ Could not run lsusb command")
                return False
                
        except Exception as e:
            print(f"❌ USB detection failed: {e}")
            return False
    
    def check_input_devices(self):
        """Check input devices that could be the scanner."""
        print("\n⌨️ INPUT DEVICE DETECTION")
        print("=" * 50)
        
        try:
            # Check /dev/input/event* devices
            event_devices = []
            if os.path.exists('/dev/input'):
                for device in os.listdir('/dev/input'):
                    if device.startswith('event'):
                        event_devices.append(f'/dev/input/{device}')
            
            if event_devices:
                print(f"📍 Found {len(event_devices)} input event devices:")
                for device in event_devices:
                    print(f"   {device}")
                print("   💡 Scanner should appear as one of these event devices")
                return True
            else:
                print("❌ No input event devices found")
                return False
                
        except Exception as e:
            print(f"❌ Input device check failed: {e}")
            return False
    
    def test_scanner_interactive(self):
        """Interactive test using simple input()."""
        print("\n🧪 INTERACTIVE SCANNER TEST")
        print("=" * 50)
        print("📋 Instructions:")
        print("1. Make sure this terminal window is active")
        print("2. Position scanner near a QR code")
        print("3. Press the scanner trigger or scan the code")
        print("4. Text should appear automatically when you scan")
        print("5. Type 'quit' to exit test")
        print()
        
        test_count = 0
        while True:
            try:
                print(f"🎯 Test #{test_count + 1}")
                print("📍 Ready for scan... (Scanner should type here automatically)")
                
                # Use input() to capture scanner data
                data = input(">>> ").strip()
                
                if data.lower() == 'quit':
                    break
                
                if data:
                    test_count += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"✅ [{timestamp}] Scanned: '{data}'")
                    print(f"   📏 Length: {len(data)} characters")
                    
                    # Analyze the data
                    if len(data) >= 8:
                        print("   ✅ Good length for QR code")
                    else:
                        print("   ⚠️ Short - might not be complete")
                    
                    if data.isalnum():
                        print("   ✅ Clean alphanumeric data")
                    elif any(c.isalnum() for c in data):
                        print("   ✅ Contains valid characters")
                    else:
                        print("   ⚠️ Unusual characters detected")
                    
                    print()
                else:
                    print("❌ Empty input - scanner might not be working")
                    print("💡 Try scanning again or check scanner power")
                    print()
                    
            except KeyboardInterrupt:
                print("\n⏹️ Test interrupted")
                break
            except Exception as e:
                print(f"❌ Error during test: {e}")
        
        return test_count > 0
    
    def test_with_cat_command(self):
        """Test using cat command to read from input devices."""
        print("\n🐱 CAT COMMAND TEST")
        print("=" * 50)
        print("This will try to read directly from input devices.")
        print("⚠️ You may need to run as sudo for this test.")
        print()
        
        # Find keyboard/scanner input devices
        try:
            result = subprocess.run(['ls', '/dev/input/by-id/'], capture_output=True, text=True)
            if result.returncode == 0:
                devices = result.stdout.strip().split('\n')
                kbd_devices = [d for d in devices if 'kbd' in d.lower() or 'keyboard' in d.lower()]
                
                if kbd_devices:
                    print("🎹 Found keyboard-like devices:")
                    for device in kbd_devices:
                        print(f"   /dev/input/by-id/{device}")
                    
                    print("\n💡 To test manually, try:")
                    print(f"   sudo cat /dev/input/by-id/{kbd_devices[0]}")
                    print("   Then scan a QR code - you should see binary output")
                    return True
                else:
                    print("❌ No keyboard devices found in /dev/input/by-id/")
                    return False
            else:
                print("❌ Could not list input devices")
                return False
                
        except Exception as e:
            print(f"❌ Device listing failed: {e}")
            return False
    
    def check_permissions(self):
        """Check if user has permissions to access input devices."""
        print("\n🔐 PERMISSION CHECK")
        print("=" * 50)
        
        try:
            # Check if user is in input group
            result = subprocess.run(['groups'], capture_output=True, text=True)
            if result.returncode == 0:
                groups = result.stdout.strip()
                print(f"👤 User groups: {groups}")
                
                if 'input' in groups:
                    print("✅ User is in 'input' group - can access input devices")
                    return True
                else:
                    print("⚠️ User not in 'input' group")
                    print("💡 Add user to input group: sudo usermod -a -G input $USER")
                    print("💡 Then logout and login again")
                    return False
            else:
                print("❌ Could not check user groups")
                return False
                
        except Exception as e:
            print(f"❌ Permission check failed: {e}")
            return False
    
    def show_troubleshooting(self):
        """Show Pi-specific troubleshooting."""
        print("\n🔧 RASPBERRY PI SCANNER TROUBLESHOOTING")
        print("=" * 60)
        print("""
🚨 SCANNER NOT WORKING ON PI:

1. **Check USB Connection**
   ❌ Scanner not detected by lsusb
   ❌ USB port not providing enough power
   ❌ Bad USB cable
   
   ✅ Solutions:
   • Try different USB port
   • Use powered USB hub if needed
   • Check cable and scanner power

2. **Scanner Configuration**
   ❌ Not in keyboard wedge mode
   ❌ Wrong output format
   ❌ No ENTER suffix configured
   
   ✅ Solutions:
   • Scan configuration barcodes from manual
   • Set to USB HID Keyboard mode
   • Enable CR/LF suffix (ENTER key)

3. **Linux Permissions**
   ❌ User not in 'input' group
   ❌ No access to /dev/input devices
   
   ✅ Solutions:
   sudo usermod -a -G input $USER
   sudo usermod -a -G dialout $USER
   # Then logout and login

4. **Pi-Specific Issues**
   ❌ Insufficient power (scanner + Pi)
   ❌ USB driver issues
   ❌ Terminal not focused
   
   ✅ Solutions:
   • Use good power supply (3A+ for Pi 4)
   • sudo apt update && sudo apt upgrade
   • Click in terminal before scanning

🧪 **MANUAL TESTING STEPS:**

1. **Basic Detection:**
   lsusb | grep -i scanner
   ls /dev/input/event*

2. **Permission Test:**
   sudo cat /dev/input/event0
   # Scan QR - should see binary output

3. **Simple Input Test:**
   # Open nano editor
   nano test.txt
   # Scan QR code - text should appear

4. **Application Test:**
   python3 -c "print(input('Scan: '))"
   # Scan QR code

💡 **WORKING SETUP:**
   • Scanner detected by lsusb
   • User in input group  
   • Scanner configured for HID keyboard mode
   • ENTER suffix enabled
   • Test works in nano/terminal

🔄 **IF STILL NOT WORKING:**
   • Try different scanner model
   • Check scanner manual for Pi compatibility
   • Use manual keyboard entry as backup
   • Contact scanner manufacturer support
""")

def main():
    """Run comprehensive USB scanner test for Raspberry Pi."""
    print("🔍 USB SCANNER TEST - RASPBERRY PI")
    print("=" * 60)
    print("Testing USB QR scanner on Raspberry Pi Linux system")
    print("=" * 60)
    
    tester = PiUSBScannerTest()
    
    # Test 1: USB device detection
    usb_ok = tester.check_usb_devices()
    
    # Test 2: Input device detection  
    input_ok = tester.check_input_devices()
    
    # Test 3: Permission check
    perm_ok = tester.check_permissions()
    
    # Test 4: Interactive scanner test
    if usb_ok:
        print("\n🎯 Now let's test the actual scanning...")
        scanner_ok = tester.test_scanner_interactive()
    else:
        scanner_ok = False
    
    # Test 5: Advanced testing info
    if not scanner_ok:
        tester.test_with_cat_command()
    
    # Show troubleshooting if needed
    if not scanner_ok:
        tester.show_troubleshooting()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"   USB Detection: {'✅' if usb_ok else '❌'}")
    print(f"   Input Devices: {'✅' if input_ok else '❌'}")
    print(f"   Permissions: {'✅' if perm_ok else '❌'}")
    print(f"   Scanner Test: {'✅' if scanner_ok else '❌'}")
    
    if scanner_ok:
        print("\n🎉 USB SCANNER IS WORKING!")
        print("✅ Ready to use with main.py application")
    else:
        print("\n❌ USB SCANNER NOT WORKING")
        print("🔧 Follow troubleshooting guide above")
        print("💡 Manual keyboard entry is always available as backup")
    
    print("=" * 60)

if __name__ == "__main__":
    main()