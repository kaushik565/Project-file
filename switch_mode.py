#!/usr/bin/env python3
"""
Mode Switcher for Batch Validation Jig
Python version that works on both Windows and Linux without permission issues.
"""

import os
import sys
import shutil
from pathlib import Path

class JigModeManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.settings_file = self.script_dir / "settings.ini"
        self.production_file = self.script_dir / "settings_production.ini"
        self.backup_file = self.script_dir / "settings_backup.ini"
    
    def check_current_mode(self):
        """Check and display current jig mode."""
        print("🔍 CHECKING CURRENT MODE")
        print("=" * 40)
        
        if not self.settings_file.exists():
            print("❌ settings.ini not found")
            return None
        
        try:
            with open(self.settings_file, 'r') as f:
                content = f.read()
            
            # Check key indicators
            is_gpio = "controller = gpio" in content
            is_mock = "controller = mock" in content
            jig_enabled = "enabled = true" in content and "[jig]" in content
            is_legacy = "LEGACY MODE" in content or "LEGACY HARDWARE" in content
            
            if is_legacy or (is_mock and not jig_enabled):
                if is_legacy:
                    print("🏛️ LEGACY MODE ACTIVE")
                    print("   ✅ Hardware: Compatible with old ACTJ")
                    print("   ✅ Jig: Manual operation")
                    print("   ✅ LCD: Disabled")
                    print("   ✅ Scanner: USB only")
                    print("   ✅ GPIO: No handshaking")
                    return "legacy"
                else:
                    print("🧪 DEVELOPMENT MODE ACTIVE")
                    print("   ✅ Hardware: Mock/safe")
                    print("   ✅ Jig: Manual control")
                    print("   ✅ LCD: Mock display")
                    print("   ✅ Scanner: USB + Camera")
                    print("   ✅ PIC: Mock communication")
                    return "development"
            elif is_gpio and jig_enabled:
                print("🏭 PRODUCTION MODE ACTIVE")
                print("   ✅ Hardware: Real GPIO")
                print("   ✅ Jig: Enabled & automated")
                print("   ✅ LCD: I2C display")
                print("   ✅ Scanner: USB only")
                print("   ✅ PIC: UART communication")
                return "production"
            else:
                print("🧪 DEVELOPMENT MODE ACTIVE")
                print("   ✅ Hardware: Mock/safe")
                print("   ✅ Jig: Manual control")
                print("   ✅ LCD: Mock display")
                print("   ✅ Scanner: USB + Camera")
                print("   ✅ PIC: Mock communication")
                return "development"
                
        except Exception as e:
            print(f"❌ Error reading settings: {e}")
            return None
    
    def switch_to_production(self):
        """Switch to production mode with real hardware."""
        print("🏭 SWITCHING TO PRODUCTION MODE")
        print("=" * 50)
        
        # Backup current settings
        if self.settings_file.exists():
            shutil.copy2(self.settings_file, self.backup_file)
            print("📄 Current settings backed up")
        
        # Check if production settings exist
        if not self.production_file.exists():
            print("❌ Production settings file not found!")
            print(f"   Expected: {self.production_file}")
            print("💡 Create settings_production.ini first")
            return False
        
        # Copy production settings
        shutil.copy2(self.production_file, self.settings_file)
        print("✅ Production settings activated")
        
        self.show_production_checklist()
        return True
    
    def switch_to_legacy(self):
        """Switch to legacy mode for old hardware/firmware."""
        print("🏛️ SWITCHING TO LEGACY MODE")
        print("=" * 50)
        print("For use with old ACTJ hardware and firmware")
        print()
        
        # Backup current settings
        if self.settings_file.exists():
            shutil.copy2(self.settings_file, self.backup_file)
            print("📄 Current settings backed up")
        
        # Check if legacy settings exist
        legacy_file = self.script_dir / "settings_legacy.ini"
        if not legacy_file.exists():
            print("❌ Legacy settings file not found!")
            print(f"   Expected: {legacy_file}")
            return False
        
        # Copy legacy settings
        shutil.copy2(legacy_file, self.settings_file)
        print("✅ Legacy settings activated")
        
        self.show_legacy_features()
        return True
    
    def show_legacy_features(self):
        """Show legacy mode features."""
        print("\n🏛️ LEGACY MODE FEATURES:")
        print("=" * 50)
        print("• Compatible with old ACTJ firmware")
        print("• No GPIO handshaking (no SBC errors)")
        print("• Manual jig operation")
        print("• USB scanner for QR input")
        print("• All QR validation logic active")
        print("• Batch logging functional")
        print("• No hardware dependencies")
        print()
        print("⚠️ LEGACY MODE LIMITATIONS:")
        print("• No automatic jig control")
        print("• No LCD display integration")
        print("• Manual cartridge handling")
        print("• Operator must trigger scans manually")
        print()
        print("✅ Ready to run: python3 main.py")

    def switch_to_development(self):
        """Switch to development mode with mock hardware."""
        print("🧪 SWITCHING TO DEVELOPMENT MODE")
        print("=" * 50)
        
        # Backup current settings
        if self.settings_file.exists():
            shutil.copy2(self.settings_file, self.backup_file)
            print("📄 Current settings backed up")
        
        # Create development settings
        dev_settings = """# Development settings for testing without hardware
[folders]
log_folder = batch_logs
setup_log_folder = Batch_Setup_Logs
recovery_file = recovery.json

[window]
app_title = AUTOMATIC CARTRIDGE SCANNING JIG [DEV MODE]
window_width = 800
window_height = 480
fullscreen = false
background_color = black

[ui]
header_text = MOLBIO DIAGNOSTICS LIMITED [DEVELOPMENT]
footer_text = DEVELOPED BY QA TEAM SITE-III
subheader_text = Automatic Cartridge Scanning JIG
clock_format = %d/%m/%Y %H:%M:%S
auto_advance = true

[layout]
entry_width = 18
qr_width = 30
padding_x = 8
padding_y = 6
section_gap = 10

[typography]
title_font = Segoe UI,14,bold
subtitle_font = Segoe UI,10,bold
body_font = Segoe UI,9,normal
small_font = Segoe UI,8,normal
scan_status_font = Segoe UI,12,bold
scan_counter_font = Segoe UI,14,bold
button_font = Segoe UI,10,bold

[palette]
text_primary = #e5e7ff
text_muted = #94a3b8
info_text = #60a5fa
success_text = #4caf50
card_border = #1f3251

[hardware]
# DEVELOPMENT MODE: Use mock hardware
controller = mock
pin_mode = BCM
red_pin = 20
green_pin = 21
yellow_pin = 22
buzzer_pin = 23

[jig]
# DEVELOPMENT MODE: Disable automatic jig control
enabled = false
auto_start = false
advance_on_fail = true
busy_signal_pin = 12

[camera]
# DEVELOPMENT MODE: Enable camera for testing
enabled = true
port = /dev/qrscanner
baudrate = 115200
timeout = 5

[lcd]
# DEVELOPMENT MODE: Use mock LCD
enabled = true
type = mock
address = 0x27
width = 16
height = 2
welcome_message = WELCOME TO MOLBIO
ready_message = JIG READY
scanning_message = SCANNING...

[controller]
# DEVELOPMENT MODE: Mock serial communication
serial_port = /dev/serial0
baudrate = 115200
"""
        
        with open(self.settings_file, 'w') as f:
            f.write(dev_settings)
        
        print("✅ Development settings activated")
        self.show_development_features()
        return True
    
    def show_production_checklist(self):
        """Show production mode requirements."""
        print("\n🔧 PRODUCTION MODE CHECKLIST:")
        print("=" * 50)
        print("Before running python3 main.py, ensure:")
        print()
        print("1. 🔌 HARDWARE CONNECTIONS:")
        print("   • Pi GPIO 14 (TX) → PIC RC7 (RX)")
        print("   • Pi GPIO 15 (RX) → PIC RC6 (TX)")
        print("   • Pi GPIO 12 → PIC RB6 (RASP_IN_PIC)")
        print("   • Common ground between Pi and PIC")
        print()
        print("2. 🖥️ PIC CONTROLLER:")
        print("   • PIC18F4550 programmed with firmware")
        print("   • Power supply to PIC (5V)")
        print("   • UART communication at 115200 baud")
        print()
        print("3. 🔧 JIG HARDWARE:")
        print("   • All sensors connected to PIC")
        print("   • All actuators connected to PIC")
        print("   • Pneumatic/hydraulic systems operational")
        print()
        print("4. 📱 USB SCANNER:")
        print("   • Connected to Pi USB port")
        print("   • Configured for keyboard wedge mode")
        print("   • ENTER suffix enabled")
        print()
        print("5. 🖼️ LCD DISPLAY:")
        print("   • I2C LCD connected to Pi (address 0x27)")
        print("   • I2C enabled: sudo raspi-config → Interface → I2C")
        print()
        print("✅ Ready to run: python3 main.py")
    
    def show_development_features(self):
        """Show development mode features."""
        print("\n🧪 DEVELOPMENT MODE FEATURES:")
        print("=" * 50)
        print("• Safe for testing without hardware")
        print("• Mock GPIO (no hardware required)")
        print("• Manual jig control")
        print("• USB scanner still works")
        print("• All QR validation logic active")
        print("• Batch logging functional")
        print()
        print("✅ Ready to run: python3 main.py")
    
    def show_usage(self):
        """Show usage instructions."""
        print("🔧 BATCH JIG MODE SWITCHER")
        print("=" * 40)
        print("Usage: python3 switch_mode.py [command]")
        print()
        print("Commands:")
        print("  production   - Switch to production mode (real hardware)")
        print("  legacy       - Switch to legacy mode (old ACTJ hardware)")
        print("  development  - Switch to development mode (mock hardware)")
        print("  status       - Show current mode")
        print("  help         - Show this help")
        print()
        print("Legacy Mode Features:")
        print("  ✅ Compatible with old ACTJ hardware")
        print("  ✅ No GPIO handshaking (no SBC errors)")
        print("  ✅ Manual jig operation")
        print("  ✅ USB scanner support")
        print()
        print("Production Mode Features:")
        print("  ✅ Real GPIO hardware control")
        print("  ✅ PIC controller communication")
        print("  ✅ I2C LCD display")
        print("  ✅ USB scanner (camera disabled)")
        print("  ✅ Jig automation enabled")
        print()
        print("Development Mode Features:")
        print("  ✅ Mock hardware (safe for testing)")
        print("  ✅ No GPIO dependencies")
        print("  ✅ Camera scanner enabled")
        print("  ✅ Manual jig control")

def main():
    manager = JigModeManager()
    
    # Get command from argument or prompt user
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        manager.show_usage()
        print("\nCurrent mode:")
        manager.check_current_mode()
        return
    
    # Execute command
    if command in ['production', 'prod']:
        success = manager.switch_to_production()
        if success:
            print("\n🎉 Switched to production mode successfully!")
    
    elif command in ['legacy', 'old']:
        success = manager.switch_to_legacy()
        if success:
            print("\n🎉 Switched to legacy mode successfully!")
    
    elif command in ['development', 'dev']:
        success = manager.switch_to_development()
        if success:
            print("\n🎉 Switched to development mode successfully!")
    
    elif command in ['status', 'check']:
        manager.check_current_mode()
    
    elif command in ['help', '-h', '--help']:
        manager.show_usage()
    
    else:
        print(f"❌ Unknown command: {command}")
        manager.show_usage()

if __name__ == "__main__":
    main()