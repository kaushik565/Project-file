#!/usr/bin/env python3
"""
Simple USB Scanner Test for Windows
Tests if USB QR scanner is working by capturing keyboard input.
"""

import sys
import time
import threading
from datetime import datetime

class USBScannerTest:
    def __init__(self):
        self.scanned_codes = []
        self.testing = False
        
    def test_scanner_simple(self):
        """Simple test - just use input() to capture scanner data."""
        print("🔧 USB SCANNER SIMPLE TEST")
        print("=" * 50)
        print("📱 How USB scanners work:")
        print("   • Acts like a keyboard")
        print("   • Types scanned data automatically")
        print("   • Usually adds ENTER at the end")
        print()
        print("🧪 TEST PROCEDURE:")
        print("1. Make sure cursor is in this window")
        print("2. Scan a QR code with your USB scanner")
        print("3. The text should appear automatically")
        print("4. Press ENTER if scanner doesn't add it")
        print("5. Type 'quit' to exit")
        print()
        
        test_count = 0
        while True:
            try:
                print(f"📍 Test #{test_count + 1} - Ready to scan...")
                scanned_data = input("🔍 Scan QR code (or type 'quit'): ").strip()
                
                if scanned_data.lower() == 'quit':
                    break
                
                if scanned_data:
                    test_count += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"✅ [{timestamp}] Received: '{scanned_data}'")
                    print(f"   Length: {len(scanned_data)} characters")
                    
                    # Check if it looks like a valid QR code
                    if len(scanned_data) >= 10:
                        print("   ✅ Length looks good for QR code")
                    else:
                        print("   ⚠️ Seems short for a typical QR code")
                    
                    # Check format
                    if any(char.isalnum() for char in scanned_data):
                        print("   ✅ Contains alphanumeric characters")
                    
                    print()
                else:
                    print("❌ No data received - try scanning again")
                    print()
                    
            except KeyboardInterrupt:
                print("\n⏹️ Test interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Total scans: {test_count}")
        if test_count > 0:
            print("   ✅ USB scanner is working!")
            print("   💡 Scanner can type data into applications")
        else:
            print("   ❌ No successful scans detected")
            
        return test_count > 0

    def test_with_notepad(self):
        """Guide user to test with Windows Notepad."""
        print("\n📝 NOTEPAD TEST")
        print("=" * 50)
        print("Let's test your scanner with Windows Notepad:")
        print()
        print("🔹 STEP 1: Open Notepad")
        print("   • Press Windows key")
        print("   • Type 'notepad'")
        print("   • Press ENTER")
        print()
        print("🔹 STEP 2: Test Scanner")
        print("   • Click in the notepad window")
        print("   • Scan a QR code with your USB scanner")
        print("   • You should see text appear automatically")
        print("   • Scanner should add a new line (ENTER)")
        print()
        print("🔹 STEP 3: Verify Results")
        print("   • Text appears instantly when scanned")
        print("   • Cursor moves to next line after scan")
        print("   • Multiple scans create multiple lines")
        print()
        
        response = input("❓ Did the Notepad test work? (y/n): ").lower().strip()
        if response == 'y':
            print("✅ Great! Your USB scanner is working correctly")
            print("💡 It will work the same way in the batch application")
            return True
        else:
            print("❌ Scanner not working - see troubleshooting below")
            return False

    def show_troubleshooting(self):
        """Show common scanner issues and solutions."""
        print("\n🔧 USB SCANNER TROUBLESHOOTING")
        print("=" * 50)
        print("""
❌ SCANNER NOT RESPONDING:
   🔧 Check USB connection (try different port)
   🔧 Scanner power (some need batteries)
   🔧 Scanner mode (should be in 'keyboard wedge' mode)
   🔧 Windows drivers (should install automatically)

❌ SCANNER BEEPS BUT NO TEXT:
   🔧 Scanner not in keyboard wedge mode
   🔧 Wrong application focus (click in text area first)
   🔧 Scanner configured incorrectly

❌ TEXT APPEARS BUT WRONG FORMAT:
   🔧 Check scanner suffix settings (should send ENTER)
   🔧 Check prefix settings (should be empty)
   🔧 Character encoding issues

🔧 SCANNER CONFIGURATION:
   Most USB scanners work out of the box, but some need setup:
   • Scan configuration barcodes from scanner manual
   • Set to 'Keyboard Wedge' or 'HID' mode
   • Enable 'Suffix' → 'Carriage Return' (ENTER)
   • Disable any prefix characters

🔧 WINDOWS SPECIFIC:
   • Scanner should appear in Device Manager as 'HID-compliant device'
   • No special drivers needed for most scanners
   • Test in any text application (Notepad, Word, etc.)

💡 QUICK TEST:
   1. Open Notepad
   2. Scan any barcode/QR code
   3. Text should appear + cursor moves to new line
   4. If this works, scanner is ready!
""")

def main():
    """Run USB scanner test for Windows."""
    print("🔍 USB QR SCANNER TEST - WINDOWS")
    print("=" * 60)
    print("Testing USB QR scanner connected to this Windows system")
    print("=" * 60)
    
    tester = USBScannerTest()
    
    # Test 1: Simple input test
    scanner_working = tester.test_scanner_simple()
    
    if not scanner_working:
        # Test 2: Notepad test as backup
        print("\n💡 Let's try a different approach...")
        notepad_working = tester.test_with_notepad()
        scanner_working = notepad_working
    
    # Show troubleshooting if needed
    if not scanner_working:
        tester.show_troubleshooting()
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL RESULT:")
    if scanner_working:
        print("✅ USB Scanner is WORKING!")
        print("🎉 Ready to use with batch application")
        print()
        print("💡 Next steps:")
        print("   • Transfer this project to your Raspberry Pi")
        print("   • Connect scanner to Pi USB port")
        print("   • Run main.py on the Pi")
        print("   • Scanner will work the same way")
    else:
        print("❌ USB Scanner is NOT WORKING")
        print("🔧 Check troubleshooting guide above")
        print()
        print("🔄 Alternative options:")
        print("   • Manual keyboard entry (always available)")
        print("   • Fix scanner configuration")
        print("   • Try different scanner model")
    print("=" * 60)

if __name__ == "__main__":
    main()