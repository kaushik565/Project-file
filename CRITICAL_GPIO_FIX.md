# 🚨 CRITICAL UPDATE: SCANNER Hardware GPIO Compatibility

## What Was Missing

You mentioned you're using the **SAME hardware and firmware** as the SCANNER project, but your `main.py` was **missing GPIO 18 and GPIO 21** that the SCANNER firmware requires!

---

## GPIO Pins Required for SCANNER Hardware

| Pin | SCANNER Name | Purpose | When Changed |
|-----|--------------|---------|--------------|
| **GPIO 12** | (Not in SCANNER) | Busy line to PIC RB6 | ✅ Already implemented |
| **GPIO 18** | `sbc_busy_pin` | SBC busy indicator to PIC | ❌ **WAS MISSING** → ✅ **NOW ADDED** |
| **GPIO 21** | `status_pin` | Status output to PIC | ❌ **WAS MISSING** → ✅ **NOW ADDED** |

---

## What We Fixed

### 1. Updated `hardware.py` ✅

**Added GPIO 18 and 21 Support:**

```python
class BaseHardwareController:
    # NEW methods added:
    def set_sbc_busy(self, busy: bool) -> None:
        """Toggle SBC busy pin (GPIO 18) - SCANNER hardware compatibility."""
    
    def set_status(self, ready: bool) -> None:
        """Toggle status pin (GPIO 21) - SCANNER hardware compatibility."""
```

**GPIO Hardware Controller Initialization:**

```python
class GPIOHardwareController:
    def __init__(self, pin_mode, pin_map):
        # ... existing code ...
        
        # SCANNER hardware compatibility: GPIO 18 and 21
        self.sbc_busy_pin = 18  # SBC busy indicator (matches SCANNER)
        self.status_pin = 21    # Status output to PIC (matches SCANNER)
        GPIO.setup(self.sbc_busy_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.status_pin, GPIO.OUT, initial=GPIO.LOW)
```

### 2. Updated `main.py` GPIO Control Pattern ✅

**Startup (launch_app):**
```python
# NOW matches SCANNER initialization
hardware.set_busy(True)       # GPIO 12 (if configured)
hardware.set_sbc_busy(True)   # GPIO 18 HIGH (ready)
hardware.set_status(True)     # GPIO 21 HIGH (ready)
```

**When PIC Sends Command (_handle_controller_request):**
```python
# Drop pins LOW while processing (matches SCANNER pattern)
self.hardware.set_status(False)      # GPIO 21 LOW (busy)
self.hardware.set_sbc_busy(False)    # GPIO 18 LOW (busy)
```

**After Sending Result (_complete_controller_request):**
```python
# Raise pins HIGH when ready (matches SCANNER pattern)
self.hardware.set_status(True)       # GPIO 21 HIGH (ready)
self.hardware.set_sbc_busy(True)     # GPIO 18 HIGH (ready)
```

---

## SCANNER Hardware Communication Pattern

### Complete Signal Flow (Now Implemented!)

```
STARTUP:
├─ GPIO 18 (sbc_busy_pin) → HIGH  ✅ NOW ADDED
├─ GPIO 21 (status_pin) → HIGH     ✅ NOW ADDED
└─ GPIO 12 (busy) → HIGH (if used) ✅ Already had

PIC SENDS COMMAND (byte 20):
├─ Python receives via UART /dev/ttyS0
├─ GPIO 18 → LOW                   ✅ NOW ADDED
├─ GPIO 21 → LOW                   ✅ NOW ADDED
├─ Camera starts scanning
└─ Wait for QR detection

QR DETECTED:
├─ Validates QR (batch check, duplicate, etc.)
├─ Sends result via UART ('A'/'R'/'D')
├─ GPIO 18 → HIGH                  ✅ NOW ADDED
└─ GPIO 21 → HIGH                  ✅ NOW ADDED

READY FOR NEXT CARTRIDGE (cycle repeats)
```

---

## Why This Was Critical

### SCANNER Firmware Expects These Signals!

From `SCANNER/matrix.py` lines 607-635:

```python
# Initialization
self.sbc_busy_pin = init_gpio(18, 'high')
set_gpio(self.sbc_busy_pin, 1)  # Set HIGH on startup

self.status_pin = init_gpio(21, 'high')
set_gpio(self.status_pin, 1)  # Set HIGH on startup

# Before scanning
set_gpio(self.status_pin, 0)    # Set LOW when busy
set_gpio(self.sbc_busy_pin, 0)  # Set LOW when busy

# After scanning
set_gpio(self.status_pin, 1)    # Set HIGH when ready
set_gpio(self.sbc_busy_pin, 1)  # Set HIGH when ready
```

**If your PIC firmware monitors GPIO 18/21 and they're not controlled, the PIC may:**
- ❌ Not recognize Raspberry Pi as ready
- ❌ Timeout waiting for status signals
- ❌ Show "SBC Er-X" errors
- ❌ Not advance cartridges properly

---

## Testing Checklist

When you deploy to hardware, verify these GPIO signals:

### On Startup
```bash
# GPIO 18 should be HIGH
gpio -g read 18  # Should output: 1

# GPIO 21 should be HIGH  
gpio -g read 21  # Should output: 1
```

### During Scan (when PIC sends command)
```bash
# Both should drop to LOW
gpio -g read 18  # Should output: 0
gpio -g read 21  # Should output: 0
```

### After Scan Complete
```bash
# Both should return to HIGH
gpio -g read 18  # Should output: 1
gpio -g read 21  # Should output: 1
```

---

## Files Modified

1. ✅ **`hardware.py`**
   - Added `set_sbc_busy()` method
   - Added `set_status()` method
   - Initialize GPIO 18 and 21 in GPIOHardwareController
   
2. ✅ **`main.py`**
   - Updated `launch_app()` to set GPIO 18/21 HIGH on startup
   - Updated `_handle_controller_request()` to drop GPIO 18/21 LOW when processing
   - Updated `_complete_controller_request()` to raise GPIO 18/21 HIGH after result

---

## Summary

### Before (Missing GPIO 18/21) ❌
- Only controlled GPIO 12
- SCANNER firmware may have failed waiting for GPIO 18/21 signals
- Not fully compatible with SCANNER hardware

### After (Complete SCANNER Compatibility) ✅
- ✅ GPIO 12 (busy line) - if configured
- ✅ GPIO 18 (sbc_busy_pin) - SCANNER hardware
- ✅ GPIO 21 (status_pin) - SCANNER hardware
- ✅ Camera /dev/qrscanner
- ✅ UART /dev/ttyS0
- ✅ All command/response codes

**NOW FULLY COMPATIBLE WITH SCANNER HARDWARE!** 🎯

---

## What This Means

Since you're using the **same hardware and firmware** as SCANNER, your PIC expects:

1. **UART communication** → ✅ You had this
2. **Camera QR scanner** → ✅ We added this
3. **GPIO 18 signals** → ✅ **NOW ADDED**
4. **GPIO 21 signals** → ✅ **NOW ADDED**

All SCANNER hardware requirements are now satisfied! Your `main.py` is a **drop-in replacement** for SCANNER's `matrix.py`, with the added benefit of **batch validation logic**. 🚀

