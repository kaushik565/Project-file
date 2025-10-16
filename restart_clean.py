#!/usr/bin/env python3
"""
Clean restart script for batch validation system.
Fixes GPIO warnings and restarts the application cleanly.
"""

import subprocess
import sys
import time

def restart_application():
    """Restart the batch validation application cleanly."""
    print("🔄 RESTARTING BATCH VALIDATION SYSTEM")
    print("=" * 50)
    
    # Step 1: Switch to production mode (updates settings)
    print("1. 📋 Applying production settings...")
    try:
        result = subprocess.run([sys.executable, "switch_mode.py", "production"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Production settings applied")
        else:
            print("   ⚠️ Settings update had issues, continuing...")
    except Exception as e:
        print(f"   ⚠️ Could not update settings: {e}")
    
    # Step 2: Clean any existing GPIO usage
    print("2. 🧹 Cleaning GPIO state...")
    try:
        import RPi.GPIO as GPIO
        GPIO.cleanup()
        print("   ✅ GPIO cleaned")
    except Exception as e:
        print(f"   💡 GPIO cleanup: {e}")
    
    # Step 3: Wait a moment
    print("3. ⏱️ Waiting for system to settle...")
    time.sleep(2)
    
    # Step 4: Start main application
    print("4. 🚀 Starting main application...")
    print("=" * 50)
    
    try:
        # Run main.py
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n⏹️ Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    restart_application()