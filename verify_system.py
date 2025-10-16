#!/usr/bin/env python3
"""
System verification script for Batch Mix-Up jig
Checks all dependencies and configurations before deployment
"""

import sys
import os
import importlib
import serial
import configparser
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 6):
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} is too old. Need Python 3.6+")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - OK")
    return True

def check_dependencies():
    """Check required Python packages."""
    print("\n📦 Checking dependencies...")
    required = ['serial', 'tkinter', 'configparser', 'csv', 'logging']
    
    for package in required:
        try:
            if package == 'serial':
                import serial
                print(f"✅ pyserial {serial.VERSION} - OK")
            elif package == 'tkinter':
                import tkinter as tk
                print("✅ tkinter - OK")
            else:
                importlib.import_module(package)
                print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - MISSING")
            if package == 'serial':
                print("   Install with: pip3 install pyserial")
            return False
    return True

def check_config_file():
    """Check settings.ini configuration."""
    print("\n⚙️ Checking configuration...")
    config_file = "settings.ini"
    
    if not os.path.exists(config_file):
        print(f"❌ {config_file} not found")
        return False
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    # Check critical sections
    required_sections = ['hardware', 'window', 'folders']
    for section in required_sections:
        if section not in config:
            print(f"❌ Missing [{section}] section in {config_file}")
            return False
        print(f"✅ [{section}] section found")
    
    # Check hardware controller setting
    controller = config.get('hardware', 'controller', fallback='mock')
    if controller == 'mock':
        print("⚠️ Hardware controller set to 'mock' - change to 'gpio' for real hardware")
    else:
        print(f"✅ Hardware controller: {controller}")
    
    return True

def check_directories():
    """Check required directories exist."""
    print("\n📁 Checking directories...")
    required_dirs = ['batch_logs', 'Batch_Setup_Logs']
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"⚠️ Creating missing directory: {dir_name}")
            os.makedirs(dir_name, exist_ok=True)
        else:
            print(f"✅ {dir_name}/ exists")
    return True

def check_serial_ports():
    """Check available serial ports."""
    print("\n🔌 Checking serial ports...")
    
    try:
        from serial.tools import list_ports
        ports = list_ports.comports()
        
        if not ports:
            print("⚠️ No serial ports detected")
            return True
        
        print("Available serial ports:")
        for port in ports:
            print(f"   📡 {port.device} - {port.description}")
        
        return True
    except Exception as e:
        print(f"❌ Error checking serial ports: {e}")
        return False

def check_file_permissions():
    """Check file permissions."""
    print("\n🔐 Checking file permissions...")
    
    python_files = ['main.py', 'config.py', 'hardware.py', 'logic.py']
    
    for file_name in python_files:
        if os.path.exists(file_name):
            if os.access(file_name, os.R_OK):
                print(f"✅ {file_name} - readable")
            else:
                print(f"❌ {file_name} - not readable")
                return False
        else:
            print(f"❌ {file_name} - not found")
            return False
    
    return True

def check_firmware_files():
    """Check firmware files are present."""
    print("\n🔧 Checking firmware files...")
    
    firmware_dir = "hardware_firmware"
    required_files = [
        "src/main.c",
        "include/pins.h", 
        "include/protocol.h",
        "include/config_bits.h",
        "Makefile"
    ]
    
    for file_path in required_files:
        full_path = os.path.join(firmware_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - missing")
            return False
    
    return True

def test_basic_imports():
    """Test importing main application modules."""
    print("\n🧪 Testing module imports...")
    
    try:
        import main
        print("✅ main.py imports successfully")
    except Exception as e:
        print(f"❌ main.py import failed: {e}")
        return False
    
    try:
        import config
        print("✅ config.py imports successfully")
    except Exception as e:
        print(f"❌ config.py import failed: {e}")
        return False
    
    return True

def main():
    """Run all verification checks."""
    print("🔍 BATCH MIX-UP SYSTEM VERIFICATION")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies), 
        ("Configuration", check_config_file),
        ("Directories", check_directories),
        ("Serial Ports", check_serial_ports),
        ("File Permissions", check_file_permissions),
        ("Firmware Files", check_firmware_files),
        ("Module Imports", test_basic_imports),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 VERIFICATION RESULTS: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 System verification PASSED - ready for deployment!")
        return 0
    else:
        print("⚠️ Some checks failed - please fix issues before deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())