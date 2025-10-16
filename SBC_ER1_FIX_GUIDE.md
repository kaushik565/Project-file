# SBC Er-1 FIX GUIDE

## 🚨 URGENT: SBC Er-1 Error Resolution

### What is SBC Er-1?
**SBC Er-1** means the ACTJv20 firmware **cannot detect the Raspberry Pi GPIO signal**. This prevents communication between the Pi and the jig.

### 🔧 IMMEDIATE FIXES DEPLOYED

#### 1. Enhanced GPIO Initialization
- **Added proper GPIO setup** with error checking
- **Added ACTJv20-specific initialization** method
- **Fixed silent GPIO failures** that were causing SBC Er-1

#### 2. Startup Sequence Fix
- **Added GPIO initialization** to legacy startup sequence
- **Proper error handling** for GPIO setup failures
- **Ensured READY signal** is properly established

### 📋 STEP-BY-STEP DIAGNOSIS

#### On Your Raspberry Pi:

1. **Run the Quick Fix Script:**
   ```bash
   python3 quick_sbc_fix.py
   ```
   This will test GPIO 12 and show you exactly what's wrong.

2. **Check Physical Connections:**
   - **GPIO 12** (Pi Pin 32) → **RB6/RASP_IN_PIC** (ACTJv20)
   - Use multimeter to check continuity
   - Verify tight connections

3. **Test with Enhanced Main App:**
   ```bash
   python3 main.py
   ```
   The new GPIO initialization should fix SBC Er-1.

### 🔍 COMMON SBC Er-1 CAUSES & FIXES

| Cause | Symptom | Fix |
|-------|---------|-----|
| **Loose GPIO 12 wire** | Intermittent SBC Er-1 | Re-solder/tighten connection |
| **Wrong GPIO pin** | Consistent SBC Er-1 | Verify GPIO 12 → RB6 |
| **GPIO not initialized** | SBC Er-1 on startup | Use updated code with initialization |
| **Pi not in legacy mode** | SBC Er-1 always | Run: `python3 switch_mode.py legacy` |
| **ACTJv20 not ready** | SBC Er-1 timing | Power cycle ACTJv20 first |

### 🚀 ENHANCED FILES DEPLOYED

#### `hardware.py` 
- **New:** `initialize_actj_gpio()` method
- **Fixed:** Proper GPIO setup with error handling
- **Enhanced:** Better logging for GPIO operations

#### `actj_legacy_integration.py`
- **New:** GPIO initialization in startup sequence
- **Fixed:** Proper error handling for GPIO failures
- **Enhanced:** Better startup reliability

#### `quick_sbc_fix.py`
- **New:** Step-by-step GPIO diagnosis
- **Test:** GPIO 12 functionality
- **Verify:** Hardware controller operation

### 📊 DIAGNOSTIC STEPS

1. **Run:** `python3 quick_sbc_fix.py`
   - Tests GPIO 12 initialization
   - Verifies hardware controller
   - Checks legacy mode

2. **Check connections:**
   - GPIO 12 → RB6 continuity
   - Power supply stability
   - Ground connections

3. **Test application:**
   - Run: `python3 main.py`
   - Check for GPIO initialization messages
   - Verify SBC Er-1 is resolved

### 🎯 EXPECTED RESULTS

#### BEFORE (SBC Er-1):
❌ ACTJv20 LCD shows "SBC Er-1"  
❌ No communication with Pi  
❌ Jig won't start automatic operation

#### AFTER (Fixed):
✅ ACTJv20 detects Pi GPIO signal  
✅ No SBC errors  
✅ Full automatic operation restored

### 🆘 IF SBC Er-1 PERSISTS

1. **Hardware Check:**
   ```bash
   # Check if GPIO 12 is physically working
   echo "12" > /sys/class/gpio/export
   echo "out" > /sys/class/gpio/gpio12/direction
   echo "1" > /sys/class/gpio/gpio12/value
   # Measure voltage at ACTJv20 RB6 - should be ~3.3V
   ```

2. **Permission Check:**
   ```bash
   sudo python3 main.py  # Try with sudo
   ```

3. **ACTJv20 Power:**
   - Power cycle the ACTJv20 completely
   - Check all power supply voltages
   - Verify ACTJv20 LCD startup sequence

### 🔧 NEXT ACTIONS

1. **Deploy updated files** to Pi
2. **Run quick_sbc_fix.py** for diagnosis
3. **Check physical connections**
4. **Test with main.py**
5. **Report results**

The enhanced GPIO initialization should resolve SBC Er-1! 🎉